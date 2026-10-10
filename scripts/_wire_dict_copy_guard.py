# -*- coding: utf-8 -*-
"""给 `scripts/check_i18n.py` 加第 6 条检查：`dict "q" "…"` 里的模板层文案。

为什么需要（第 68 轮发现的真实盲区）：
  `i18n_extract.collect()` 只扫 HTML **文本节点**与**属性值**。
  `dict "q" "Does unlimited eSIM mean unlimited speed?"` 两者都不是 ——
  于是 `layouts/research/unlimited-esim.html` 的 5 条 FAQ 里 4 条走了 i18n、
  唯独这条是字面量，`check_i18n.py` 仍报「0 处硬编码文案」、build 全绿，
  而德语子页一落地就会把英文问句印给德国读者（同时进 FAQPage 的 JSON-LD）。

幂等：每条编辑都带**独立 marker**，已施加则整条跳过（不用 `new in raw` —— 会被同一批
      的其它编辑改写产物）。
前置断言：文件必须是 LF 行尾、`ast.parse` 可解析、5 个锚点各命中 1 次。

用法：python -X utf8 scripts/_wire_dict_copy_guard.py [--dry]
"""
from __future__ import annotations

import ast
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
TARGET = "scripts/check_i18n.py"

DOC_OLD = """  5. [ERROR]  `printf "…"` 格式串里的英文文案 —— 含 JSON-LD 的 `"name" (printf "…")`
              与 head.html 的 <title> 候选串（第六十三轮新增；实测 53 个德语页曾印英文而守卫全绿）
"""
DOC_NEW = """  5. [ERROR]  `printf "…"` 格式串里的英文文案 —— 含 JSON-LD 的 `"name" (printf "…")`
              与 head.html 的 <title> 候选串（第六十三轮新增；实测 53 个德语页曾印英文而守卫全绿）
  6. [ERROR]  `dict "q" "…"` / `dict "a" "…"` 等**文案键的字面量值** ——
              FAQ 的 q/a 与 JSON-LD 的 name/text 都装在 dict 里，i18n_extract 只扫
              HTML 文本节点与属性值，这一类整个在视野外（第六十八轮实测：
              `research_unlimited_esim` 的 "Does unlimited eSIM mean unlimited speed?"
              曾硬编码进 dict，德语读者会看到英文问句而全部守卫全绿）
"""

FUNC_OLD = "def check_keys():"
FUNC_NEW = r'''# ── `dict "q" "…"` / `dict "a" "…"`：模板层文案在 dict 字面量里的盲区 ──
# 键列表只收**明确承载用户可见文案**的键；`@type` / `indent` / `id` / `path` / `site`
# 这些是 schema 关键词、缩进、锚点、路径 —— 值再像句子也不是文案。
DICT_COPY_KEYS = ("q", "a", "name", "text", "label", "title", "desc", "lead", "heading", "caption")
DICT_LIT = re.compile(r'dict\s+"(' + "|".join(DICT_COPY_KEYS) + r')"\s*"((?:[^"\\]|\\.)*)"')
_BACKSLASH = chr(92)


def hardcoded_dict_literals(src: str) -> list[str]:
    """`dict "q" "…"` / `dict "a" "…"` —— 模板层文案在 dict 字面量里的盲区。

    为什么单列一条：`i18n_extract` 只扫 HTML **文本节点**与**属性值**，
    `dict "q" "…"` 两者都不是 —— 于是 FAQ 问句/答案一旦写成字面量，
    `check_i18n.py` 会报「0 处硬编码」、产物却把英文原样印给德语读者。
    2026-10-10 实测：`layouts/research/unlimited-esim.html` 的
    `dict "q" "Does unlimited eSIM mean unlimited speed?"` 就是这么漏的
    （同一页其它 4 条 FAQ 都走了 i18n，唯独这条是字面量）。

    判据：值含空格、含 >=2 个 >=2 字母的拉丁词、不含 `{` / 反斜杠（排除插值兜底）。
    正例（不报）：`dict "@type" "Question"`（键不在列表）、`dict "indent" "  "`（无词）、
    `dict "path" "/guides/x"`（无空格）、`dict "q" (i18n "k")`（非字面量）。
    """
    out: list[str] = []
    for m in DICT_LIT.finditer(src):
        lit = m.group(2)
        if " " not in lit or "{" in lit or _BACKSLASH in lit:
            continue
        if len(re.findall(r"[A-Za-z][A-Za-z'\-]+", lit)) >= 2:
            out.append(f"{m.group(1)}: {lit}")
    return out


def check_keys():'''

VAR_OLD = """    printf_lits: list[str] = []
    raw_hrefs: list[str] = []
    ext_hrefs: list[str] = []
"""
VAR_NEW = """    printf_lits: list[str] = []
    raw_hrefs: list[str] = []
    ext_hrefs: list[str] = []
    dict_copies: list[str] = []
"""

COLLECT_OLD = """            for v in external_lang_href(src):
                ext_hrefs.append(f"{rel}: {v}")
"""
COLLECT_NEW = """            for v in external_lang_href(src):
                ext_hrefs.append(f"{rel}: {v}")
            for v in hardcoded_dict_literals(src):
                dict_copies.append(f"{rel}: {v[:60]!r}")
"""

RET_OLD = "    return hardcoded, frags, scripts, defaults, printf_lits, raw_hrefs, ext_hrefs\n"
RET_NEW = "    return hardcoded, frags, scripts, defaults, printf_lits, raw_hrefs, ext_hrefs, dict_copies\n"

UNPACK_OLD = "    hardcoded, frags, scripts, defaults, pf, raw_hrefs, ext_hrefs = scan_layouts()\n"
UNPACK_NEW = "    hardcoded, frags, scripts, defaults, pf, raw_hrefs, ext_hrefs, dc = scan_layouts()\n"

REPORT_OLD = """    for v in ext_hrefs[:10]:
        errors.append("外链被套进 lang-href（产物会变成 /https:/… 的 404 站内路径）-> " + v)
    if len(ext_hrefs) > 10:
        errors.append(f"... 另有 {len(ext_hrefs) - 10} 处外链误过 lang-href")
"""
REPORT_NEW = REPORT_OLD + """
    for v in dc[:15]:
        errors.append("`dict \\"q\\"/\\"a\\"` 字面量文案未抽 i18n -> " + v)
    if len(dc) > 15:
        errors.append(f"... 另有 {len(dc) - 15} 处 dict 字面量文案")
"""

STAT_OLD = """    print(f"  layouts: {len(hardcoded)} 处硬编码文案 / {len(frags)} 处拼装句碎片 / "
          f"{len(scripts)} 处内联脚本文案 / {len(defaults)} 处 default 兜底文案 / "
          f"{len(pf)} 处 printf 格式串文案 / {len(raw_hrefs)} 处未过 lang-href 的 href / "
          f"{len(ext_hrefs)} 处外链误过 lang-href")
"""
STAT_NEW = """    print(f"  layouts: {len(hardcoded)} 处硬编码文案 / {len(frags)} 处拼装句碎片 / "
          f"{len(scripts)} 处内联脚本文案 / {len(defaults)} 处 default 兜底文案 / "
          f"{len(pf)} 处 printf 格式串文案 / {len(raw_hrefs)} 处未过 lang-href 的 href / "
          f"{len(ext_hrefs)} 处外链误过 lang-href / {len(dc)} 处 dict 字面量文案")
"""

SELFTEST_OLD = """    print(f"\\n自测{'通过' if not failed else f'失败 {failed} 项'}")
"""
SELFTEST_NEW = r'''    # dict 字面量文案：正例必须放过 schema 关键词 / 缩进 / 路径 / 非字面量 / 单词值，
    # 反例必须抓住真文案 —— 含 2026-10-10 实测泄漏的原始形态。
    dlgood = (
        '{{ dict "@type" "Question" }}',
        '{{ dict "indent" "  " }}',
        '{{ dict "path" "/guides/what-is-an-esim" }}',
        '{{ dict "q" (i18n "k") }}',
        '{{ dict "name" "esimsift" }}',
        '{{ dict "a" (printf (i18n "k") $x) }}',
    )
    dlbad = (
        '{{ dict "q" "Does unlimited eSIM mean unlimited speed?" }}',
        "{{ dict \"a\" \"A heavy user's dream market.\" }}",
        '{{ dict "name" "Best eSIM plans ranked by cost per GB" }}',
    )
    for name, cases, want in (("dict-copy-good", dlgood, 0), ("dict-copy-bad", dlbad, 3)):
        got = [x for c in cases for x in hardcoded_dict_literals(c)]
        ok = len(got) == want
        failed += 0 if ok else 1
        print(f"  {'OK  ' if ok else 'MISS'} {name}: 期望 {want} 处，实得 {len(got)} 处 -> {got}")

    print(f"\n自测{'通过' if not failed else f'失败 {failed} 项'}")
'''

EDITS = [
    ("docstring", DOC_OLD, DOC_NEW, "  6. [ERROR]  `dict \"q\" \"…\"`"),
    ("新函数", FUNC_OLD, FUNC_NEW, "def hardcoded_dict_literals"),
    ("局部变量", VAR_OLD, VAR_NEW, "    dict_copies: list[str] = []"),
    ("收集循环", COLLECT_OLD, COLLECT_NEW, "dict_copies.append("),
    ("return", RET_OLD, RET_NEW, "ext_hrefs, dict_copies"),
    ("解包", UNPACK_OLD, UNPACK_NEW, "ext_hrefs, dc = scan_layouts()"),
    ("报错段", REPORT_OLD, REPORT_NEW, "字面量文案未抽 i18n"),
    ("统计行", STAT_OLD, STAT_NEW, "{len(dc)} 处 dict 字面量文案"),
    ("selftest", SELFTEST_OLD, SELFTEST_NEW, "dict-copy-bad"),
]


def main() -> int:
    dry = "--dry" in sys.argv
    p = ROOT / TARGET
    b = p.read_bytes()
    crlf = b.count(b"\r\n")
    if crlf:
        raise SystemExit(f"{TARGET}: 预期 LF 行尾，实测 CRLF {crlf} 行 —— 拒绝改写")
    src = b.decode("utf-8")
    ast.parse(src)  # 前置：现在必须可解析

    hits = 0
    for name, old, new, marker in EDITS:
        if marker in src:
            print(f"  skip  {name}: 已施加")
            continue
        c = src.count(old)
        if c != 1:
            raise SystemExit(f"{name}: 锚点命中 {c} 次（应为 1）")
        src = src.replace(old, new, 1)
        hits += 1
        print(f"  EDIT  {name}")

    if dry:
        print(f"dry-run：将施加 {hits} 处编辑")
        return 0

    ast.parse(src)  # 后置：改完仍可解析
    p.write_bytes(src.encode("utf-8"))
    print(f"完成：{hits} 处编辑 / {len(b)} -> {len(src.encode('utf-8'))} bytes")
    return 0


if __name__ == "__main__":
    sys.exit(main())
