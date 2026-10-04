# -*- coding: utf-8 -*-
"""Rendered h2/h3 punctuation guard: scan public/*.html for , ; : em-dash en-dash in headings.
H1 exempt; /research/ hub card titles keep their "Title: Subtitle" strip via replaceRE in template.

Per-language: 标点规则见 scripts/lang_rules.py。德语/法语/日语等语言里 en/em dash
是正常标题排版（如 "eSIM in Deutschland – Test"），这些语言的产物目录放宽破折号禁令；
逗号/分号/冒号仍然全语言禁止（CJK 用的是全角标点，本正则天然不命中）。
单语言（仅 en）时行为与改造前完全一致。

Usage: python -X utf8 scripts/check_headings.py"""
import html
import re, sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from lang_rules import dash_ok_prefixes, under_any  # noqa: E402

DASH_OK = dash_ok_prefixes()
STRICT = re.compile(r"[,;:—–]")
RELAXED = re.compile(r"[,;:]")

bad = 0; n = 0; seen = 0
for f in Path("public").rglob("*.html"):
    t = f.read_text(encoding="utf-8")
    n += 1
    rel = f.relative_to("public").as_posix()
    pat = RELAXED if under_any(rel, DASH_OK) else STRICT
    for m in re.finditer(r"<h([23])[^>]*>(.*?)</h\1>", t, re.S):
        seen += 1
        # 先剥标签、再解实体：否则 "Data &amp; research" 里的 ";" 会误报
        h = html.unescape(re.sub(r"<[^>]+>", "", m.group(2))).strip()
        if pat.search(h):
            bad += 1
            print(f"{f.relative_to('public')}: {h[:70]}")
print(f"checked {n} html files, {seen} h2/h3, bad: {bad}")
sys.exit(1 if bad else 0)
