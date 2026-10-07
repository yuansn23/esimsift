# -*- coding: utf-8 -*-
"""Find Firsty GB-price pairs and BNESIM API endpoints in captured HTML."""
import re
from pathlib import Path

P = Path(__file__).resolve().parent
OUT = Path(r"C:\Users\27197\WorkBuddy\2026-10-04-19-19-25\_probe_result.txt")


def log(*a):
    OUT.open("a", encoding="utf-8").write(" ".join(str(x) for x in a) + "\n")


log("\n===== GB-price pairs (firsty) =====")
fj = (P / "firsty_japan_esim.html").read_text(encoding="utf-8", errors="replace")
seen = set()
for m in re.finditer(r"(\d+(?:\.\d+)?)\s*(?:GB|gb|Mb|MB)[^<>{}]{0,120}?[€$]\s?(\d+(?:\.\d+)?)", fj):
    pair = f"{m.group(1)}GB = EUR {m.group(2)}"
    if pair in seen:
        continue
    seen.add(pair)
    log("  ", pair, " ctx:", re.sub(r"\s+", " ", m.group(0))[:150])
# reverse order: price then GB
for m in re.finditer(r"[€$]\s?(\d+(?:\.\d+)?)[^<>{}]{0,80}?(\d+(?:\.\d+)?)\s*(?:GB|gb)", fj):
    pair = f"EUR {m.group(1)} -> {m.group(2)}GB"
    key = "R:" + pair
    if key in seen:
        continue
    seen.add(key)
    log("  R:", pair, " ctx:", re.sub(r"\s+", " ", m.group(0))[:150])

log("\n===== BNESIM api endpoints =====")
for name in ("bnesim_shop_home.html", "bnesim_japan_plans.html", "bnesim_home.html"):
    html = (P / name).read_text(encoding="utf-8", errors="replace")
    eps = set()
    for m in re.finditer(r"https?://[a-z0-9.\-]*api[a-z0-9.\-]*\.[a-z]{2,6}[^\"'\s)<\\]*", html, re.I):
        eps.add(m.group(0)[:120])
    for m in re.finditer(r"['\"](\/(?:api|v\d|graphql|rest)[^\"'\s]{3,80})['\"]", html):
        eps.add("(rel)" + m.group(1))
    log(f"  {name}: {len(eps)} endpoints")
    for e in sorted(eps)[:20]:
        log("    ", e)
    # window.__ globals
    globs = set(re.findall(r"window\.(__[A-Za-z_]+__|[A-Za-z_$][\w$]{2,30})\s*=", html))
    log(f"    window globals: {sorted(globs)[:12]}")
