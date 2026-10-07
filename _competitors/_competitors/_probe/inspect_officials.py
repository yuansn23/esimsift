# -*- coding: utf-8 -*-
"""Inspect firsty/bnesim captured pages: script types, ld+json, embedded state, price ctx."""
import json
import re
from pathlib import Path

P = Path(__file__).resolve().parent
OUT = Path(r"C:\Users\27197\WorkBuddy\2026-10-04-19-19-25\_probe_result.txt")


def log(*a):
    OUT.open("a", encoding="utf-8").write(" ".join(str(x) for x in a) + "\n")


OUT.open("a", encoding="utf-8").write("\n===== STRUCTURE INSPECT =====\n")

for name in ("firsty_home.html", "bnesim_home.html", "bnesim_shop_home.html"):
    html = (P / name).read_text(encoding="utf-8", errors="replace")
    log("=" * 30, name, len(html), "chars")
    for key in ("__NEXT_DATA__", "__NUXT__", "application/ld+json", "application/json",
                "window.__", "data-drupal", "wp-content"):
        log(f"  {key}:", key in html)
    for i, m in enumerate(re.finditer(r'<script[^>]*type="application/ld\+json"[^>]*>(.*?)</script>', html, re.S)):
        body = m.group(1).strip()
        try:
            data = json.loads(body)
        except Exception:
            log(f"  ld+json #{i}: parse err, {len(body)} chars")
            continue
        t = data.get("@type")
        log(f"  ld+json #{i}: type={t} len={len(body)}")
        if t in ("Product", "Offer", "ProductCollection", "ItemList"):
            log("    HEAD:", json.dumps(data, ensure_ascii=False)[:500])
    # price context samples
    seen = set()
    n = 0
    for m in re.finditer(r"[€$]\s?\d+[.,]?\d*", html):
        s = max(0, m.start() - 100)
        ctx = re.sub(r"\s+", " ", html[s:m.end() + 60])
        key = ctx[-100:]
        if key in seen:
            continue
        seen.add(key)
        if n < 6:
            log("  PRICE CTX:", ctx)
        n += 1
    log(f"  distinct price ctxs: {len(seen)}")
