# -*- coding: utf-8 -*-
"""Rendered h2/h3 punctuation guard: scan public/*.html for , ; : em-dash en-dash in headings.
H1 exempt; /research/ hub card titles keep their "Title: Subtitle" strip via replaceRE in template.
Usage: python -X utf8 scripts/check_headings.py"""
import re, sys
from pathlib import Path
bad = 0; n = 0
for f in Path("public").rglob("*.html"):
    t = f.read_text(encoding="utf-8")
    n += 1
    for m in re.finditer(r"<h([23])[^>]*>(.*?)</h>", t, re.S):
        h = re.sub(r"<[^>]+>", "", m.group(2)).strip()
        if re.search(r"[,;:—–]", h):
            bad += 1
            print(f"{f.relative_to('public')}: {h[:70]}")
print(f"checked {n} html files, bad h2/h3: {bad}")
sys.exit(1 if bad else 0)
