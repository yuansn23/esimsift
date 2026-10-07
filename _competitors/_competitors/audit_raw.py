# -*- coding: utf-8 -*-
"""Audit the raw esimdb capture: files, plan counts, empties, 404s, timestamps."""
import json
from collections import Counter
from pathlib import Path

RAW = Path(__file__).resolve().parent / "raw"
# esimdb-sourced brands: raw/<brand>/<slug>.json with a "plans" array + "status"
BRANDS = ["nomad", "jetpac", "gigsky", "quibity", "roamless", "gomoworld",
          "maya", "bnesim"]
TOTAL_CC = 50

for brand in BRANDS:
    d = RAW / brand
    files = sorted(d.glob("*.json"))
    counts, empty, notfound, bad = [], [], [], []
    for f in files:
        try:
            j = json.loads(f.read_text(encoding="utf-8"))
        except Exception as e:
            bad.append((f.stem, str(e)[:60])); continue
        n = len(j.get("plans") or [])
        counts.append(n)
        if j.get("status") == 404 or n == 0:
            (notfound if j.get("status") == 404 else empty).append(f.stem)
    ts = sorted(f.stat().st_mtime for f in files)
    print(f"\n### {brand}: {len(files)} files (of {TOTAL_CC} target)")
    if counts:
        print(f"    plans/file: min={min(counts)} max={max(counts)} avg={sum(counts)/len(counts):.1f} total={sum(counts)}")
    print(f"    empty={empty}")
    print(f"    404={notfound}")
    if brand == "bnesim" and empty:
        print(f"    NOTE: bnesim 'empty' countries have regional bundles only "
              f"(see raw/bnesim/<slug>.json -> regional_options): {empty}")
    if bad:
        print(f"    CORRUPT={bad}")
    if files:
        import datetime
        print(f"    modified: {datetime.datetime.fromtimestamp(ts[0]):%Y-%m-%d %H:%M} -> {datetime.datetime.fromtimestamp(ts[-1]):%Y-%m-%d %H:%M}")

# firsty: single global record, no per-country files
d = RAW / "firsty"
if d.is_dir():
    files = sorted(d.glob("*.json"))
    print(f"\n### firsty: {len(files)} global file(s) (brand prices globally, not per country)")
    for f in files:
        j = json.loads(f.read_text(encoding="utf-8"))
        tiers = (j.get("pricing_model") or {}).get("tiers") or []
        print(f"    {f.name}: scope={j.get('scope')} tiers={[t.get('name') for t in tiers]} "
              f"price_points={len(j.get('price_points') or [])}")
