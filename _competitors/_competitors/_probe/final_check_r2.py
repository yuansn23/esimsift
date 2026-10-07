# -*- coding: utf-8 -*-
import csv
import json
from collections import Counter
from pathlib import Path

BASE = Path(r"D:\HUGO test\29.1_windows-amd64\hugo_0.159.1_windows-amd64\esimsift-main\esimsift-main\_competitors")
OUT = Path(r"C:\Users\27197\WorkBuddy\2026-10-04-19-19-25\_parse2.txt")
lines = []

with (BASE / "plans_all.csv").open(encoding="utf-8-sig") as fh:
    rows = list(csv.DictReader(fh))
lines.append(f"CSV rows: {len(rows)}")
lines.append(f"CSV columns: {list(rows[0].keys())}")
by_brand = Counter(r["brand"] for r in rows)
lines.append("per brand: " + json.dumps(dict(by_brand), ensure_ascii=False))
by_cur = Counter(f'{r["brand"]}:{r["currency"]}' for r in rows)
lines.append("currency mix: " + json.dumps(dict(by_cur), ensure_ascii=False))
firsty = [r for r in rows if r["brand"] == "firsty"]
lines.append("firsty rows: " + json.dumps(firsty, ensure_ascii=False))

plans = sorted(p.name for p in (BASE / "plans").glob("*.toml"))
lines.append("plans/*.toml: " + ", ".join(plans))
brands = sorted(p.name for p in (BASE / "brand").glob("*.json"))
lines.append("brand/*.json: " + ", ".join(brands))

# bnesim networks sanity: does JP carry KDDI?
bt = (BASE / "plans" / "bnesim.toml").read_text(encoding="utf-8")
seg = bt.split("[JP]")[1].split("[")[0]
lines.append("bnesim JP networks line: " + next((l for l in seg.splitlines() if l.startswith("networks")), "?"))

OUT.write_text("\n".join(str(l) for l in lines), encoding="utf-8")
