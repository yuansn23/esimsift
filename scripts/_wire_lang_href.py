#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""把 layouts/ 里**未过 lang-href** 的裸 `href="{{ printf "/…" }}"` 改成语言感知链接。

为什么必须修：
  `lang-href.html` 的三层兜底只有在**经过它**时才生效。裸 `printf` 拼路径会写出
  「德语页里的英文路径」—— `/de/compare/austria/` 上出现 `/compare/austria/roamic/`。
  它**不 404**（英文页存在），所以：

    · `check_links.py` 看不见（目标存在）；
    · `audit_de_links.py` 的「死链」一栏看不见（目标存在）；
    · 只有按「语言降级」口径扫才现形 —— 德语用户被静默送到英文页，
      GSC 还会看到语言不一致的内链。

  修法：`href="{{ printf "…" … }}"` → `href="{{ partial "lang-href.html" (printf "…" …) }}"`
  ⚠ 静态资源（favicon / css / img）**不动** —— 它们全站共享，加语言前缀才是错的。

  英文侧恒等：lang-href 第 1 层命中「当前语言有该页」⇒ 英文站输出 == 入参 ⇒ 英文产物逐字节不变。

用法：
  python -X utf8 scripts/_wire_lang_href.py [--dry]
  python -X utf8 scripts/_wire_lang_href.py --selftest
"""
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
LAYOUTS = ROOT / "layouts"

# href="{{ printf "<带引号路径>" <参数…> }}"  —— 参数可含括号（如 (index $x 0)），
# 所以用非贪婪 + 行尾锚定的 ` }}"` 收口，而不是禁止括号。
PAT = re.compile(r'(href="\{\{) printf (".*?") (.+?) (\}\}")')
FIXED = "lang-href.html"


def fix(text: str) -> tuple[str, int]:
    """返回 (改后文本, 命中数)。已含 lang-href 的行天然不匹配。"""
    n = 0

    def _sub(m: re.Match) -> str:
        nonlocal n
        n += 1
        return f'{m.group(1)} partial "{FIXED}" (printf {m.group(2)} {m.group(3)}) {m.group(4)}'

    return PAT.sub(_sub, text), n


def selftest() -> None:
    ok = 0
    bad = 0

    def chk(cond: bool, name: str) -> None:
        nonlocal ok, bad
        if cond:
            ok += 1
            print(f"  [OK] {name}")
        else:
            bad += 1
            print(f"  [!!] {name}")

    a, n = fix('href="{{ printf "/esim-providers/%s/" $key }}"')
    chk(n == 1 and a == 'href="{{ partial "lang-href.html" (printf "/esim-providers/%s/" $key) }}"',
        "正例 A：简单路径被正确包裹")

    b, n = fix('href="{{ printf "/compare/%s-vs-%s/" (index $vsPair 0) (index $vsPair 1) }}"')
    chk(n == 1 and b.count("(") == b.count(")"), "正例 B：含括号参数且括号平衡")
    chk(b.index("lang-href") < b.index("printf"), "正例 B：lang-href 在 printf 外层")

    c, n = fix('href="{{ partial "lang-href.html" "/compare/matchups/" }}"')
    chk(n == 0, "反例 A：已本地化的链接不重复包裹（幂等）")

    d, n = fix('<link rel="icon" href="/favicon.svg" type="image/svg+xml">')
    chk(n == 0, "反例 B：静态资源不被改写")

    e, n = fix('<a href="/about/">x</a>')
    chk(n == 0, "反例 C：纯字面路径不在本脚本职责内（不静默改）")

    f, n = fix('href="{{ printf "/a/%s/" $x }}" href="{{ printf "/b/%s/" $y }}"')
    chk(n == 2, "正例 C：一行两处都改")

    g, n = fix('href="{{- printf "/a/%s/" $x }}"')
    chk(n == 0, "边界：带 `{{-` 的写法不在本次清单内（需人工确认）")

    print(f"\nselftest: {ok} 项通过 / {bad} 项失败")
    sys.exit(1 if bad else 0)


if "--selftest" in sys.argv:
    selftest()

DRY = "--dry" in sys.argv
total, files = 0, []
for f in sorted(LAYOUTS.rglob("*.html")):
    raw = f.read_bytes()
    crlf = raw.count(b"\r\n")
    text = raw.decode("utf-8")
    new, n = fix(text)
    if not n:
        continue
    total += n
    files.append((f.relative_to(ROOT).as_posix(), n))
    print(f"  {n:2d}×  {f.relative_to(ROOT).as_posix()}")
    if not DRY:
        f.write_bytes(new.encode("utf-8"))
        assert f.read_bytes().count(b"\r\n") == crlf, f"CRLF 被改变：{f}"

print(f"\n{'[dry] 待改' if DRY else '已改'}: {total} 处 / {len(files)} 个文件")
if not DRY:
    left = []
    for f in sorted(LAYOUTS.rglob("*.html")):
        m = PAT.findall(f.read_text(encoding="utf-8"))
        if m:
            left.append((f.relative_to(ROOT).as_posix(), len(m)))
    if left:
        sys.exit(f"ERROR: 还有未包裹的写法：{left}")
    print("复核：layouts/ 下已无裸 `href=\"{{ printf \"…\"` 写法")
