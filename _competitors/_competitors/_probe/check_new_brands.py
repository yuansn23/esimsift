# -*- coding: utf-8 -*-
import json
from pathlib import Path

BASE = Path(r"D:\HUGO test\29.1_windows-amd64\hugo_0.159.1_windows-amd64\esimsift-main\esimsift-main\_competitors")
OUT = Path(r"C:\Users\27197\WorkBuddy\2026-10-04-19-19-25\_parse2.txt")
lines = []

cov = json.loads((BASE / "coverage.json").read_text(encoding="utf-8"))
for b in ("bnesim", "firsty", "roamless", "gomoworld"):
    lines.append(f"{b}: {json.dumps(cov.get(b), ensure_ascii=False)}")

lines.append("\n--- bnesim.toml head ---")
lines.append((BASE / "plans" / "bnesim.toml").read_text(encoding="utf-8")[:900])
lines.append("\n--- firsty.toml ---")
lines.append((BASE / "plans" / "firsty.toml").read_text(encoding="utf-8"))

# which bnesim countries have no plans
raw = BASE / "raw" / "bnesim"
missing = []
for f in sorted(raw.glob("*.json")):
    j = json.loads(f.read_text(encoding="utf-8"))
    if not j.get("plans"):
        missing.append(f"{f.stem} (ISO {j.get('iso2')}, regionals={len(j.get('regional_options') or [])})")
lines.append("\nbnesim countries with 0 single-country plans: " + ", ".join(missing))

OUT.write_text("\n".join(lines), encoding="utf-8")
