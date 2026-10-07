# -*- coding: utf-8 -*-
"""Sample BNESIM products: local JP/US, regional, unlimited, price/currency variety."""
import json
from pathlib import Path

P = Path(__file__).resolve().parent
OUT = Path(r"C:\Users\27197\WorkBuddy\2026-10-04-19-19-25\_probe_result.txt")


def log(*a):
    OUT.open("a", encoding="utf-8").write(" ".join(str(x) for x in a) + "\n")


data = json.loads((P / "bnesim_pricing_api.json").read_text(encoding="utf-8"))
prods = data["products"]

log(f"total products: {len(prods)}")

# field diversity
units = {}
currencies = set()
dur = {}
for pr in prods:
    units[pr.get("unit")] = units.get(pr.get("unit"), 0) + 1
    currencies.add(pr.get("currency"))
    dur[pr.get("duration")] = dur.get(pr.get("duration"), 0) + 1
log("units:", units)
log("currencies:", sorted(currencies))
log("durations (top):", sorted(dur.items(), key=lambda x: -x[1])[:12])

# samples: japan local, one regional, one unlimited, one with networks
shown = {"jp": 0, "regional": 0, "unl": 0, "net": 0}
for pr in prods:
    name = (pr.get("name") or "")
    cov = pr.get("coverages")
    if shown["jp"] < 2 and "Japan" in name:
        log("JP SAMPLE:", json.dumps(pr, ensure_ascii=False)[:700])
        shown["jp"] += 1
    elif shown["regional"] < 1 and pr.get("regional"):
        log("REGIONAL SAMPLE:", json.dumps(pr, ensure_ascii=False)[:500])
        shown["regional"] += 1
    elif shown["unl"] < 2 and "unlimited" in name.lower():
        log("UNLIMITED SAMPLE:", json.dumps(pr, ensure_ascii=False)[:500])
        shown["unl"] += 1
    elif shown["net"] < 1 and pr.get("networks") and pr.get("carriers"):
        log("NETWORK SAMPLE:", json.dumps(pr, ensure_ascii=False)[:600])
        shown["net"] += 1
    if all(v >= 2 for v in shown.values()) if False else False:
        pass

# coverage object shape of one japan product
for pr in prods:
    if "Japan" in (pr.get("name") or "") and pr.get("coverages"):
        log("JP coverage:", json.dumps(pr["coverages"], ensure_ascii=False)[:400])
        break
