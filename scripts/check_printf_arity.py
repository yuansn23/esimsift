#!/usr/bin/env python -X utf8
"""check_printf_arity.py —— i18n 调用的**跨文件契约**静态守卫（构建前，秒级）。

## 判据一：`printf (i18n "KEY") args…` 的格式串元数
## 为什么需要它（真实事故）
第七十八轮在 `/compare/matchups/` 的 FAQ 里写了
`printf (i18n "compare_matchups__faq_a_decided") $total`，而那条 i18n 值里
**一个 `%` 占位符都没有**，Go 于是把多余的实参打印成 `%!(EXTRA int=45)` 并
**印到读者页面上**（4 个页面）。它只被构建末端 `check_output.py` 判据① 抓到 ——
代价是一次 11 分钟的全量构建。

根因是**跨文件契约**：
  · 格式串（`%s` / `%.2f` / `%d` …）住在 `i18n/*.toml` 的**值**里；
  · 实参个数住在 `layouts/**` 的**模板**里；
  · `check_i18n.py` 只扫「printf 字面量里有没有英文文案」，管不到这条。

## 判据二：`i18n "KEY" (dict "a" … "b" …)` 的占位符对齐
i18n 值里的 `{{ .x }}` 是另一套契约：模板少传一个 ⇒ Hugo **不报错**，
直接把该处渲染成 `<no value>` 印给读者；多传一个 ⇒ 静默丢弃（模板与文案已漂移）。
某一语言少写一个占位符（德英不对齐）也在这里被抓 —— 这是本判据的主要价值。

用法：
  python -X utf8 scripts/check_printf_arity.py            # 扫正式仓库
  python -X utf8 scripts/check_printf_arity.py --selftest # 注入反例验证守卫本身
"""
from __future__ import annotations

import io
import os
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
I18N_DIR = ROOT / "i18n"
LAYOUTS = ROOT / "layouts"

# Go fmt 格式动词：%[flags][width][.prec]verb
# ★ 动词白名单只收本项目在 i18n 里真正用过的几类（s/d/v/f/q）。
#   一旦收全字母表，`20% off` 里的 `% o` 会被当成「合法的八进制动词」而漏判 ——
#   实测 `printf "Save 20% off" $x` 在 Go 里正是印成 `%!o(string=…)` 的泄漏。
_VERB = re.compile(r"%[-+# 0]*[\d*]*(?:\.[\d*]+)?[sdvqf]")
# i18n 值里的 Go 模板占位符（{{ .x }}）不是格式动词，先挖掉
_PLACEHOLDER = re.compile(r"\{\{.*?\}\}", re.S)
# 只认 `{{ .name }}` 形态 —— 其它形态（`{{ len $d.x }}`）会被 Hugo 静默渲染成空串
_PLACEHOLDER_NAME = re.compile(r"\{\{\s*\.([A-Za-z0-9_]+)\s*\}\}")


def load_i18n() -> dict[str, dict[str, str]]:
    """{lang: {key: value}}，只认单行 `key = "value"`。"""
    out: dict[str, dict[str, str]] = {}
    for p in sorted(I18N_DIR.glob("*.toml")):
        kv: dict[str, str] = {}
        for line in p.read_text(encoding="utf-8").splitlines():
            m = re.match(r'^([A-Za-z0-9_.]+)\s*=\s*"(.*)"\s*$', line)
            if m:
                kv[m.group(1)] = m.group(2).replace('\\"', '"')
        out[p.stem] = kv
    return out


def fmt_verbs(value: str) -> list[str]:
    return _VERB.findall(_PLACEHOLDER.sub(" ", value))


def bare_percent(value: str) -> list[str]:
    """值里不是合法格式动词的裸 %（含结尾 %）—— 当格式串用会印出 %! 噪声。"""
    v = _PLACEHOLDER.sub(" ", value)
    spans = [(m.start(), m.end()) for m in _VERB.finditer(v)]
    bad = []
    for i, ch in enumerate(v):
        if ch != "%":
            continue
        if i + 1 < len(v) and v[i + 1] == "%":
            continue
        if any(a <= i < b for a, b in spans):
            continue
        bad.append(v[max(0, i - 20):i + 12])
    return bad


# ── 模板 action 的解析 ───────────────────────────────────────────
# 注意：Go 模板里实参**不加括号**，`printf (i18n "k") $total` 的圆括号只包住 i18n 调用。
# 因此不能靠括号平衡去找 printf 的实参边界，必须按 **action 边界**（`{{ … }}`）切。
def split_actions(src: str):
    """产出 (行号, action 内文本)。注释 `{{/* … */}}` 整块跳过（里面可能有任意 `}}`）。"""
    i, n = 0, len(src)
    while True:
        s = src.find("{{", i)
        if s < 0:
            return
        if src.startswith("{{/*", s):
            e = src.find("*/}}", s)
            i = (e + 4) if e >= 0 else n
            continue
        j = s + 2
        while j < n:
            c = src[j]
            if c == '"':
                j += 1
                while j < n and src[j] != '"':
                    j += 2 if src[j] == "\\" else 1
            elif src[j:j + 2] == "}}":
                break
            j += 1
        yield src.count("\n", 0, s) + 1, src[s + 2:j]
        i = j + 2


def _strip_pipes(txt: str) -> str:
    """砍掉顶层 `|` 之后的管道段（safeHTML / markdownify …）。"""
    depth, i, n = 0, 0, len(txt)
    while i < n:
        c = txt[i]
        if c == '"':
            i += 1
            while i < n and txt[i] != '"':
                i += 2 if txt[i] == "\\" else 1
        elif c == "(":
            depth += 1
        elif c == ")":
            depth -= 1
        elif c == "|" and depth == 0:
            return txt[:i]
        i += 1
    return txt


def _scan_call(src: str, open_idx: int) -> tuple[str, int]:
    """从 `(` 开始，按引号/括号平衡截出整个调用体，返回 (体内文本, 闭合位置+1)。"""
    depth, i, n = 0, open_idx, len(src)
    while i < n:
        c = src[i]
        if c == '"':                                  # 跳过字符串字面量
            i += 1
            while i < n and src[i] != '"':
                i += 2 if src[i] == "\\" else 1
        elif c in "(`":
            depth += 1
        elif c in ")`":
            depth -= 1
            if depth == 0:
                return src[open_idx + 1:i], i + 1
        i += 1
    return src[open_idx + 1:], n


def _split_args(body: str) -> list[str]:
    """把调用体按**顶层空白**切实参（Go 模板是空格分隔，不是逗号）。"""
    args, buf, depth, i, n = [], [], 0, 0, len(body)
    while i < n:
        c = body[i]
        if c == '"':
            j = i + 1
            while j < n and body[j] != '"':
                j += 2 if body[j] == "\\" else 1
            buf.append(body[i:min(j + 1, n)])
            i = min(j + 1, n)
            continue
        if c in "(`":
            depth += 1
        elif c in ")`":
            depth -= 1
        if c.isspace() and depth == 0:
            if buf:
                args.append("".join(buf).strip())
                buf = []
            i += 1
            continue
        buf.append(c)
        i += 1
    if buf:
        args.append("".join(buf).strip())
    return [a for a in args if a]


def scan_source(src: str, i18n: dict[str, dict[str, str]]) -> list[tuple[str, str]]:
    """返回 [(级别, 说明)]，级别为 "ERR"（会印给读者）或 "WARN"（静默、无可见缺陷）。

    ★ 分级依据（用真实仓库校准过的边界，别凭直觉收紧）：
      · 模板**少传**必需占位符 ⇒ 产物印 `<no value>` ⇒ ERR
        「必需」= **该 key 各语言占位符的并集**，不是某一语言的集合。
      · dict **多传**一个键 ⇒ 分两种，不能用一条规则一刀切：
          (a) 该键被**某种语言**用到（德语要 `country_acc`/`country_dat` 的格变化，
              英语只要 `country`）⇒ **刻意设计，不报**；
          (b) 该键**任何语言都没用到** ⇒ 真冗余，Go 静默忽略 ⇒ WARN。
        实测：一条「多传即漂移」的原始判据会在 provider.html 上误报 160 处 ——
        那 160 处全部是 (a) 形态（德语格变化供给），差点用新守卫卡死正确代码。
      · 各语言占位符集合**互不相同是允许的**（同上，语法需要）⇒ 不判。
    """
    errs: list[tuple[str, str]] = []
    for line_no, action in split_actions(src):
        body = _strip_pipes(action).strip().lstrip("-").strip()

        # ── 判据一：printf (i18n "KEY") args… ──
        m = re.match(r"^printf\b", body)
        if m:
            args = _split_args(body[m.end():])
            if args:
                mm = re.match(r'^\(\s*i18n\s+"([^"]+)"\s*\)$', args[0])
                if mm:
                    key = mm.group(1)
                    n_args = len(args) - 1
                    for lang, kv in i18n.items():
                        if key not in kv:
                            errs.append(("ERR", "[%s] L%d: i18n 键在 %s.toml 里不存在（产物会直接印出 key）"
                                         % (key, line_no, lang)))
                            continue
                        verbs = fmt_verbs(kv[key])
                        if len(verbs) != n_args:
                            errs.append(("ERR", "[%s] L%d: %s.toml 的格式串有 %d 个动词 %s，但模板传了 %d 个实参 ⇒ 产物会印出 %%!(EXTRA/INVALID …)"
                                         % (key, line_no, lang, len(verbs), verbs, n_args)))
                        bad = bare_percent(kv[key])
                        if bad:
                            errs.append(("ERR", "[%s] L%d: %s.toml 的值里有非格式动词的裸 %% ⇒ 当格式串用会印出 %%! 噪声：%r"
                                         % (key, line_no, lang, bad[:2])))
                    continue

        # ── 判据二 / 三：i18n "KEY" (dict …) 与 i18n "KEY"（无实参）──
        m = re.match(r'^i18n\s+"([^"]+)"\s*(.*)$', body, re.S)
        if not m:
            continue
        key = m.group(1)
        rest = m.group(2).strip()
        pset: set[str] | None = None
        if rest.startswith("(dict"):
            dm = re.match(r"^\(\s*dict\b(.*)\)$", rest, re.S)
            if not dm:
                continue
            dargs = _split_args(_strip_pipes(dm.group(1)))
            pset = {a[1:-1] for a in dargs[0::2]
                    if len(a) >= 2 and a[0] == '"' and a[-1] == '"'}
        elif rest not in ("", "|"):
            continue          # 其它形态（管道已剥、未知实参）不归本守卫
        for lang, kv in i18n.items():
            if key not in kv:
                errs.append(("ERR", "[%s] L%d: i18n 键在 %s.toml 里不存在（产物会直接印出 key）"
                             % (key, line_no, lang)))
                continue
            placeholders = set(_PLACEHOLDER_NAME.findall(kv[key]))
            if pset is None:
                if placeholders:
                    errs.append(("ERR", "[%s] L%d: 模板没传 dict，但 %s.toml 的值用了 %s ⇒ 产物会印出 <no value>"
                                 % (key, line_no, lang, sorted("{{ .%s }}" % x for x in placeholders))))
                continue
            for miss in sorted(placeholders - pset):
                errs.append(("ERR", "[%s] L%d: %s.toml 用了 {{ .%s }}，但模板的 dict 没传 ⇒ 产物会印出 <no value>"
                             % (key, line_no, lang, miss)))
        if pset is not None:
            # ★ 逐 key 的跨语言并集：只有「任何语言都没用到」才算真冗余
            key_ph: set[str] = set()
            for kv in i18n.values():
                if key in kv:
                    key_ph |= set(_PLACEHOLDER_NAME.findall(kv[key]))
            for extra in sorted(pset - key_ph):
                errs.append(("WARN", "[%s] L%d: 模板传了 dict 键 %r，但它没出现在任何语言的 %s 值里 ⇒ 真冗余（Go 静默忽略）"
                             % (key, line_no, extra, key)))
    return errs


# ── selftest ─────────────────────────────────────────────────────
_GOOD = [
    '{{ printf (i18n "k_ok") $a $b }}',
    '{{ printf (i18n "k_num") 3 }}',
    '{{ i18n "k_extra" | safeHTML }}',
    '{{ printf (i18n "k_extra" (dict "a" 1)) }}',
    '{{ printf "%.2f" $x }}',
    '{{ i18n "k_dict" (dict "n" $n) }}',
    '{{ i18n "k_dict2" (dict "lo" 1 "hi" 3) }}',
    '{{ i18n "k_dict" (dict "n" $n) | safeHTML }}',
    '{{- i18n "k_dict" (dict "n" $n) -}}',
    # ★ 德语格变化：模板同时供给各语言各自需要的形态 —— 不得报 ERR 也不得报 WARN
    '{{ i18n "k_lang_specific" (dict "country" $c.name "country_acc" $c.name_acc) }}',
]
_BAD = [
    ('{{ printf (i18n "k_extra") $total }}', "EXTRA"),
    ('{{ printf (i18n "k_pct") $x }}', "EXTRA"),
    ('{{ printf (i18n "k_num") }}', "INVALID"),
    ('{{ printf (i18n "k_ok") $a }}', "INVALID"),
    ('{{ printf (i18n "k_missing") $a }}', "不存在"),
    ('{{ i18n "k_dict" }}', "占位符没传"),
    ('{{ i18n "k_dict2" (dict "lo" 1) }}', "少传 hi"),
    ('{{ i18n "k_lang_specific" (dict "country" $x) }}', "少传德语要的 country_acc"),
    ('{{ i18n "k_missing" (dict "a" 1) }}', "key 不存在"),
]
_WARN = [
    ('{{ i18n "k_dict" (dict "n" $n "x" 1) }}', "多传 x（任何语言都没用到）"),
    ('{{ i18n "k_extra" (dict "a" 1) }}', "无占位符却传 dict"),
]

_FAKE = {
    "en": {
        "k_ok": "Save %s on %s",
        "k_extra": "Save on every plan",           # 0 动词
        "k_pct": "Save 20% off",                   # 裸 %
        "k_num": "Only %d left",
        "k_dict": "Showing {{ .n }} plans",
        "k_dict2": "From {{ .lo }} to {{ .hi }} GB",
        "k_de_drift": "Brands {{ .a }} and {{ .b }}",
        "k_lang_specific": "{{ .country }} eSIM",
    },
    "de": {
        "k_ok": "%s auf %s sparen",
        "k_extra": "Bei jedem Tarif sparen",
        "k_pct": "20 % Rabatt",
        "k_num": "Nur noch %d übrig",
        "k_dict": "{{ .n }} Tarife werden angezeigt",
        "k_dict2": "Von {{ .lo }} bis {{ .hi }} GB",
        "k_de_drift": "Marken {{ .a }}",           # 德语少一个占位符 —— **刻意不判**（见下）
        "k_lang_specific": "{{ .country_acc }}-eSIM",   # 德语要宾格：与 en 形态不同是设计
    },
}


def selftest() -> int:
    bad = 0
    print("=== selftest A：正例（不得出现任何 ERR）===")
    for s in _GOOD:
        errs = [e for lv, e in scan_source(s, _FAKE) if lv == "ERR"]
        print("  %s %s" % ("OK " if not errs else "ERR", s))
        if errs:
            print("      " + errs[0][:120])
            bad += 1
    print("=== selftest B：硬反例（必须报 ERR）===")
    for s, why in _BAD:
        errs = [e for lv, e in scan_source(s, _FAKE) if lv == "ERR"]
        print("  %s %-46s <- %s" % ("OK " if errs else "MISS", s, why))
        if not errs:
            bad += 1
    print("=== selftest C：软反例（必须报 WARN、且不得报 ERR）===")
    for s, why in _WARN:
        res = scan_source(s, _FAKE)
        w = [e for lv, e in res if lv == "WARN"]
        e = [e for lv, e in res if lv == "ERR"]
        print("  %s %-46s <- %s" % ("OK " if (w and not e) else "MISS", s, why))
        if not w or e:
            bad += 1
    print("\n未被正确处理的情形: %d（必须为 0）" % bad)
    return 1 if bad else 0


def main() -> int:
    if "--selftest" in sys.argv:
        return selftest()
    i18n = load_i18n()
    print("check_printf_arity.py —— i18n 调用契约守卫（printf 格式串元数 + dict 占位符对齐）")
    print("  i18n 语言文件 %d 个：%s" % (len(i18n), ", ".join("%s(%d key)" % (k, len(v)) for k, v in i18n.items())))
    n_err = n_warn = 0
    files = 0
    warn_files: dict[str, int] = {}
    for p in sorted(LAYOUTS.rglob("*")):
        if p.suffix.lower() not in (".html", ".xml", ".txt", ".js", ".json"):
            continue
        files += 1
        res = scan_source(p.read_text(encoding="utf-8", errors="replace"), i18n)
        errs = [(lv, e) for lv, e in res if lv == "ERR"]
        warns = [(lv, e) for lv, e in res if lv == "WARN"]
        n_err += len(errs)
        n_warn += len(warns)
        if warns:
            warn_files[p.relative_to(ROOT).as_posix()] = len(warns)
        if errs:
            print("  ERR %s" % p.relative_to(ROOT).as_posix())
            for _, e in errs[:4]:
                print("      " + e)
    if warn_files:
        print("  WARN 冗余 dict 键（Go 静默忽略，无可见缺陷；清理是可选优化）：")
        for f, n in sorted(warn_files.items(), key=lambda x: -x[1]):
            print("      %-34s %d 处" % (f, n))
    print("  扫描 %d 个布局文件：ERR %d / WARN %d" % (files, n_err, n_warn))
    if n_err:
        print("\n%d 处契约不一致会**印到读者页面上** ⇒ 失败" % n_err)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
