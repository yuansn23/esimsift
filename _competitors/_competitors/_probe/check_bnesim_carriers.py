# -*- coding: utf-8 -*-
import json
from pathlib import Path

RAW = Path(r"D:\HUGO test\29.1_windows-amd64\hugo_0.159.1_windows-amd64\esimsift-main\esimsift-main\_competitors\raw\bnesim")
OUT = Path(r"C:\Users\27197\WorkBuddy\2026-10-04-19-19-25\_parse2.txt")
j = json.loads((RAW / "japan.json").read_text(encoding="utf-8"))
lines = [f"slug={j['slug']} iso2={j['iso2']} status={j['status']} plans={len(j['plans'])}"]
for p in j["plans"][:3]:
    lines.append("  " + json.dumps({k: p.get(k) for k in ("name", "amount", "unit", "price", "carriers")}, ensure_ascii=False))
OUT.write_text("\n".join(lines), encoding="utf-8")
