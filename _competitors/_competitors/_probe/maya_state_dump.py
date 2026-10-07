# -*- coding: utf-8 -*-
"""Dump maya transfer-state plan structures (globalRegions / cruiseRegions / singleCountries)."""
import json
import re
from pathlib import Path

P = Path(__file__).resolve().parent
OUT = Path(r"C:\Users\27197\WorkBuddy\2026-10-04-19-19-25\_probe_out.txt")


def log(*a):
    OUT.open("a", encoding="utf-8").write(" ".join(str(x) for x in a) + "\n")


maya = (P / "maya_home.html").read_text(encoding="utf-8", errors="replace")
m = re.search(r'<script[^>]*type="application/json"[^>]*>(.*?)</script>', maya, re.S)
data = json.loads(m.group(1).strip())
cache = data["CACHE_CONTENT_STATE_KEY"]["cache"]

log("cache keys:", list(cache.keys()))

for grp in ("globalRegions", "cruiseRegions"):
    regs = cache.get(grp) or []
    log(f"\n== {grp}: {len(regs)} regions ==")
    for r in regs[:3]:
        log(f"-- region keys: {list(r.keys())}")
        plans = r.get("plans") or []
        log(f"-- {r.get('name','?')} ({r.get('code','?')}): {len(plans)} plans")
        for i, pl in enumerate(plans):
            slim = {k: v for k, v in pl.items()
                    if not isinstance(v, dict) or k in ("priceBundle", "priceOriginal")}
            if isinstance(slim.get("priceBundle"), dict):
                slim["priceBundle"] = {"USD": slim["priceBundle"].get("USD"),
                                       "EUR": slim["priceBundle"].get("EUR")}
            log(f"   [{i}] " + json.dumps(slim, ensure_ascii=False)[:600])

singles = cache.get("singleCountries") or []
log(f"\n== singleCountries: {len(singles)} ==")
if singles:
    s0 = singles[0]
    log("sample keys:", list(s0.keys()))
    log("sample:", json.dumps(s0, ensure_ascii=False)[:1500])

# any other plan-bearing structures
for k, v in cache.items():
    if k in ("globalRegions", "cruiseRegions", "singleCountries", "config"):
        continue
    s = json.dumps(v, ensure_ascii=False)
    log(f"\ncache[{k}]: type={type(v).__name__} len={len(s)} head={s[:300]}")
