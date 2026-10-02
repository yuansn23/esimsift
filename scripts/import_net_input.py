#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Import the user's filled _network_data_needed.md -> _net_results/{brand}.json,
validating every network name against data/carriers.toml canonical names.

Parses Part 1 lines:   `- {ISO} {Country}: {Name1;Name2}`  (networks after the colon).
Then run scripts/backfill_networks.py to write plans/*.toml.
"""
import json, os, re, tomllib

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(ROOT)

carriers = tomllib.load(open("data/carriers.toml", "rb"))
def canon(iso):
    return [p["name"] for p in carriers.get(iso, {}).get("profiles", [])]
def norm(s):
    return re.sub(r"[^a-z0-9]", "", (s or "").lower())

BRANDS = {"airalo", "saily", "ubigi", "holafly", "yesim", "alosim", "roamic"}

text = open("_network_data_needed.md", encoding="utf-8").read()
results = {}
dropped = {}
cur_brand = None
for line in text.splitlines():
    m = re.match(r"^###\s+([a-z]+)\s*$", line, re.I)
    if m and m.group(1).lower() in BRANDS:
        cur_brand = m.group(1).lower()
        continue
    if line.startswith("## "):
        cur_brand = None
        continue
    m = re.match(r"^-\s*([A-Z]{2})\s+[^:]+:\s*(.*)$", line)
    if not m or not cur_brand:
        continue
    iso = m.group(1).upper()
    net = m.group(2).strip()
    if not net:
        continue
    names = [n.strip() for n in re.split(r"[;；,，]", net) if n.strip()]
    ok = []
    for n in names:
        mm = next((c for c in canon(iso) if norm(c) == norm(n)), None)
        if mm:
            ok.append(mm)
        else:
            dropped.setdefault(f"{cur_brand}/{iso}", []).append(n)
    if ok:
        results.setdefault(cur_brand, {})[iso] = ok

os.makedirs("_net_results", exist_ok=True)
for brand, networks in results.items():
    data = {"brand": brand, "source_url": "manual (user-provided)",
            "networks": networks, "notes": {}}
    with open(f"_net_results/{brand}.json", "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=1)

print("=== import report ===")
for brand in sorted(results):
    print(f"  {brand:10s} filled {len(results[brand]):2d} countries")
if dropped:
    print("DROPPED (name not in carriers.toml for that country — fix the spelling):")
    for k, v in sorted(dropped.items()):
        print(f"  {k}: {v}")
else:
    print("  no dropped names")
print("now run: python -X utf8 scripts/backfill_networks.py")
