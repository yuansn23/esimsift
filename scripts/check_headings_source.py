#!/usr/bin/env python -X utf8
"""check_headings_source.py —— `check_headings.py` 的**构建前**版本（源码/数据层同一判据）。

## 为什么要前移
`check_headings.py` 是**产物级**守卫：只有已经渲染出来的 1291 个页面才被检查，
而一次全量构建 ≈ 11 分钟。第七十八轮就因为新加的一条德语 H2 里带逗号，
跑满 11 分钟后才在末尾报 `bad: 45` —— 45 个页面全部返工一次构建。

本脚本把**同一条判据**前移到「i18n 值 + content 正文」层：
  · 找出所有会成为 `<h2>/<h3>` 的 i18n key（含 `$xH2 = i18n "…"` 的间接赋值形态）；
  · 对 en 值用 STRICT（禁 `, ; : — –`），对 de 值用 RELAXED（禁 `, ; :`）；
  · content/de、content/en 的 Markdown 标题同样按所在语言的口径查。
规则从 `scripts/lang_rules.py` 读，**与产物级守卫同源**，不抄第二份正则。

## 与产物级的边界（本脚本不能替代 check_headings.py）
  · 值里可能含 `{{ .x }}` 占位符，**代入后**才出现标点（如 `{{ .a }} – {{ .b }}`）；
  · 数据层的国名/品牌名进标题后才带标点；
  两者本脚本都看不见 ⇒ 产物级守卫必须保留。本脚本只求「构建前把已知的一网打尽」。

用法：
  python -X utf8 scripts/check_headings_source.py
  python -X utf8 scripts/check_headings_source.py --selftest
"""
from __future__ import annotations

import html
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from lang_rules import dash_ok_prefixes, under_any  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
STRICT = re.compile(r"[,;:—–]")
RELAXED = re.compile(r"[,;:]")
DASH_OK = dash_ok_prefixes()

_H = re.compile(r"<h([23])\b[^>]*>(.*?)</h\1>", re.S)
_ACT = re.compile(r"\{\{-?\s*(.*?)\s*-?\}\}", re.S)
_KEY_IN_ACT = re.compile(r'i18n\s+"([^"]+)"')
# 间接形态：{{ $faqH2 = printf (i18n "…") … }}  …  <h2>{{ $faqH2 }}</h2>
# （第六十五轮实漏一处，靠命名习惯兜住；比产物级弱，故只作为补充来源）
_VAR_H = re.compile(r"\$(\w*(?:[Hh][23]|Head|heading)\w*)\s*=[^\n]*?i18n\s+\"([^\"]+)\"")


def load_i18n() -> dict[str, dict[str, str]]:
    out: dict[str, dict[str, str]] = {}
    for p in sorted((ROOT / "i18n").glob("*.toml")):
        kv: dict[str, str] = {}
        for line in p.read_text(encoding="utf-8").splitlines():
            m = re.match(r'^([A-Za-z0-9_.]+)\s*=\s*"(.*)"\s*$', line)
            if m:
                kv[m.group(1)] = m.group(2).replace('\\"', '"')
        out[p.stem] = kv
    return out


def strip_ph(v: str) -> str:
    return re.sub(r"\{\{.*?\}\}", "", v)


def check_value(lang: str, value: str) -> str | None:
    """返回违规标点，合法则 None。en 用 STRICT，其余语言用 RELAXED（与产物级同源）。"""
    pat = RELAXED if under_any("%s/x.html" % lang, DASH_OK) else STRICT
    m = pat.search(html.unescape(strip_ph(value)))
    return m.group(0) if m else None


def scan_layouts(i18n: dict[str, dict[str, str]]) -> list[str]:
    errs: list[str] = []
    for f in sorted((ROOT / "layouts").rglob("*")):
        if f.suffix != ".html" and f.name != "llms.txt":
            continue
        src = f.read_text(encoding="utf-8", errors="replace")
        rel = f.relative_to(ROOT).as_posix()

        def report(key: str, where: str) -> None:
            for lang, kv in i18n.items():
                if key not in kv:
                    continue
                hit = check_value(lang, kv[key])
                if hit:
                    errs.append("%s: %s 的 %s 值含 %r ⇒ 会成为 <h2>/<h3> 的违规标题：%r"
                                % (rel, where, lang, hit, kv[key][:80]))

        for m in _H.finditer(src):
            block = m.group(2)
            keys = set()
            for a in _ACT.finditer(block):
                keys |= set(_KEY_IN_ACT.findall(a.group(1)))
            keys |= set(_KEY_IN_ACT.findall(block))
            for k in sorted(keys):
                report(k, "h%s" % m.group(1))
        for m in _VAR_H.finditer(src):
            report(m.group(2), "$%s" % m.group(1))
    return errs


def scan_content() -> list[str]:
    errs: list[str] = []
    for lang in sorted(p.name for p in (ROOT / "content").iterdir() if p.is_dir()):
        for f in sorted((ROOT / "content" / lang).rglob("*.md")):
            raw = f.read_text(encoding="utf-8", errors="replace")
            parts = raw.split("---", 2)
            body = parts[2] if len(parts) == 3 else raw
            for ln, line in enumerate(body.splitlines(), 1):
                m = re.match(r"^(#{2,3})\s+(.*)$", line)
                if m and check_value(lang, m.group(2)):
                    errs.append("%s:%d (content/%s) 标题含 %r：%s"
                                % (f.relative_to(ROOT).as_posix(), ln, lang,
                                   check_value(lang, m.group(2)), m.group(2)[:80]))
    return errs


# ── selftest ─────────────────────────────────────────────────────
def selftest() -> int:
    fake = {
        "en": {
            "h_ok": "Which providers win most head-to-heads",
            "h_comma": "Which providers win, and why",
            "h_dash": "Airalo vs Roami — the full picture",
            "h_colon": "Head to head: the index",
        },
        "de": {
            "h_ok": "Welcher Anbieter gewinnt die meisten Duelle",
            "h_comma": "Welcher Anbieter gewinnt, und warum",
            "h_dash": "Airalo gegen Roami – das ganze Bild",   # de 允许破折号
            "h_colon": "Kopf an Kopf: der Index",
        },
    }
    case = {
        "h_ok": [0, 0],
        "h_comma": ["ERR", "ERR"],
        "h_dash": ["ERR", 0],      # en 禁破折号、de 放行
        "h_colon": ["ERR", "ERR"],
    }
    bad = 0
    print("=== selftest：逐 key 期望（en/de 各自的判据）===")
    for k, exp in case.items():
        got = ["ERR" if check_value(lg, fake[lg][k]) else 0 for lg in ("en", "de")]
        ok = got == exp
        print("  %s %-10s en=%-4s de=%-4s（期望 %s）" % ("OK " if ok else "MISS", k, got[0], got[1], exp))
        if not ok:
            bad += 1
    # 模板侧：h2 块里的 key 必须被找到（含间接赋值形态）
    tmpl = '<h2>{{ i18n "h_comma" | safeHTML }}</h2>\n{{ $faqH2 = printf (i18n "h_colon") $x }}\n<h2>{{ $faqH2 }}</h2>\n<h1>{{ i18n "h_dash" }}</h1>'
    found = set(_KEY_IN_ACT.findall(tmpl)) | {m.group(2) for m in _VAR_H.finditer(tmpl)}
    for m in _H.finditer(tmpl):
        found |= set(_KEY_IN_ACT.findall(m.group(2)))
    ok = {"h_comma", "h_colon"} <= found and "h_dash" not in {k for k in found if k != "h_dash"}
    print("  %s 模板侧识别：h2 内联 + $faqH2 间接赋值都被找到（H1 不参与）" % ("OK " if ok else "MISS"))
    if not ok:
        bad += 1
    print("\n未被正确处理的情形: %d（必须为 0）" % bad)
    return 1 if bad else 0


def main() -> int:
    if "--selftest" in sys.argv:
        return selftest()
    i18n = load_i18n()
    print("check_headings_source.py —— h2/h3 标点守卫（构建前；与 check_headings.py 同源规则）")
    errs = scan_layouts(i18n) + scan_content()
    for e in errs:
        print("  ERR " + e)
    print("  扫描 %d 个语言的 i18n + layouts + content 标题：%d 处违规" % (len(i18n), len(errs)))
    if errs:
        print("\n把标点去掉或改写句式（德语从句的逗号要用句式解决，不能删词）")
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
