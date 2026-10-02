#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Fill every brand's plans[ISO].networks with the country's full carrier list
(countries.toml `carriers`), implementing the rule "operators are a country
property — every brand rides the same local networks".

Idempotent: replaces whatever `networks = [...]` is already there ([] or a subset).
Names come from countries.toml.carriers, which is already verified identical to
carriers.toml profiles[].name, so no name validation is needed here.

Run: python -X utf8 scripts/backfill_networks_uniform.py
"""
import glob, os, re, tomllib

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(ROOT)

countries = tomllib.load(open("data/countries.toml", "rb"))

report = []
for tf in sorted(glob.glob("data/plans/*.toml")):
    brand = os.path.basename(tf)[:-5]
    text = open(tf, encoding="utf-8").read()
    filled = 0
    for iso in sorted(countries):
        names = countries[iso]["carriers"]
        arr = "[" + ", ".join('"%s"' % n for n in names) + "]"
        pat = re.compile(
            r"(\[" + re.escape(iso) + r"\]\n[^\[]*?)networks\s*=\s*\[[^\]]*\]",
            re.M,
        )
        new_text, n = pat.subn(
            lambda m: m.group(1) + "networks = " + arr, text, count=1
        )
        if n:
            text = new_text
            filled += 1
    open(tf, "w", encoding="utf-8").write(text)
    report.append((brand, filled))

print("=== uniform networks backfill ===")
for brand, filled in report:
    print(f"  {brand:10s} filled {filled:2d}/50")
print("done.")
