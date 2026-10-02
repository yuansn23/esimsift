#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Backfill plans[ISO].networks from agent research results (_net_results/*.json).

Safety: every network name is validated against the canonical MNO list for that
country (data/carriers.toml profiles) BEFORE it is written. A name that does not
match a real carrier for that country is dropped (never fabricated). Empty
results are left as-is.

Run: python -X utf8 scripts/backfill_networks.py
"""
import json, glob, os, re, tomllib, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(ROOT)

# 1) canonical carriers per country
carriers = tomllib.load(open("data/carriers.toml", "rb"))
def canonical_names(iso):
    profs = carriers.get(iso, {}).get("profiles", [])
    return [p["name"] for p in profs]

def normalize(s):
    return re.sub(r"[^a-z0-9]", "", (s or "").lower())

def match_name(name, iso):
    want = normalize(name)
    for c in canonical_names(iso):
        if normalize(c) == want:
            return c  # return the canonical spelling
    return None

def to_toml_array(names):
    return "[" + ", ".join('"%s"' % n for n in names) + "]"

report = []
result_files = sorted(glob.glob("_net_results/*.json"))
if not result_files:
    print("No _net_results/*.json found — nothing to do.")
    sys.exit(0)

for rf in result_files:
    brand = os.path.basename(rf)[:-5]
    data = json.load(open(rf, encoding="utf-8"))
    networks = data.get("networks", {})
    if not networks:
        report.append((brand, 0, 0, "no networks mapping"))
        continue

    toml_path = f"data/plans/{brand}.toml"
    if not os.path.exists(toml_path):
        report.append((brand, 0, 0, "TOML missing"))
        continue

    text = open(toml_path, encoding="utf-8").read()
    filled = 0
    dropped = 0
    for iso, names in networks.items():
        # validate + canonicalize
        ok = []
        for n in names:
            m = match_name(n, iso)
            if m:
                ok.append(m)
            else:
                dropped += 1
        if not ok:
            continue  # nothing valid for this country; leave empty

        # replace networks = [] inside this country's [ISO] block only
        # match the [ISO] header, then the following 'networks = [...]' line
        pat = re.compile(
            r"(\[" + re.escape(iso) + r"\]\n[^\[]*?)networks\s*=\s*\[[^\]]*\]",
            re.M
        )
        new_text, nsub = pat.subn(
            lambda m: m.group(1) + "networks = " + to_toml_array(ok),
            text, count=1,
        )
        if nsub:
            text = new_text
            filled += 1

    open(toml_path, "w", encoding="utf-8").write(text)
    report.append((brand, filled, dropped, ""))

print("=== networks backfill report ===")
for brand, filled, dropped, note in report:
    print(f"  {brand:10s} filled={filled:3d} dropped(non-matching)={dropped:3d} {note}")
print("done.")
