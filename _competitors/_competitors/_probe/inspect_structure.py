# -*- coding: utf-8 -*-
"""Inspect structure of maya_home.html and jetpac_japan.html (read-only probe)."""
import json
import re
from pathlib import Path

P = Path(__file__).resolve().parent


def probe(name):
    html = (P / name).read_text(encoding="utf-8", errors="replace")
    print("=" * 30, name, len(html), "chars")
    # script types
    for m in re.finditer(r'<script[^>]*type="([^"]+)"[^>]*>', html):
        print("  script type:", m.group(1))
    # next data / nuxt
    for key in ("__NEXT_DATA__", "__NUXT__", "application/ld+json"):
        print(f"  has {key}:", key in html)
    # price occurrences with context (first 5)
    for i, m in enumerate(re.finditer(r"\$\d+\.\d{2}", html)):
        if i >= 5:
            break
        s = max(0, m.start() - 120)
        print("  price ctx:", html[s:m.end() + 60].replace("\n", " ")[:200])
    # json-ld blocks
    for i, m in enumerate(re.finditer(
            r'<script[^>]*type="application/ld\+json"[^>]*>(.*?)</script>',
            html, re.S)):
        block = m.group(1).strip()
        print(f"  ld+json #{i}: {len(block)} chars, head: {block[:150]}")


for f in ("maya_home.html", "jetpac_japan.html"):
    try:
        probe(f)
    except Exception as e:
        print(f, "ERR", e)
