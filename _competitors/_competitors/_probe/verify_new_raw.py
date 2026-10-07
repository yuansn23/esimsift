# -*- coding: utf-8 -*-
import json
from pathlib import Path

OUT = Path(r"C:\Users\27197\WorkBuddy\2026-10-04-19-19-25\_parse2.txt")
RAW = Path(r"D:\HUGO test\29.1_windows-amd64\hugo_0.159.1_windows-amd64\esimsift-main\esimsift-main\_competitors\raw")
lines = []
for brand in ("roamless", "gomoworld"):
    tot = ok = f404 = 0
    plansum = 0
    for f in sorted((RAW / brand).glob("*.json")):
        j = json.loads(f.read_text(encoding="utf-8"))
        tot += 1
        if j.get("status") == 404:
            f404 += 1
        elif j.get("status") == 200:
            ok += 1
            plansum += len(j.get("plans") or [])
    lines.append(f"{brand}: files={tot} 200={ok} 404={f404} plans={plansum}")
    sample = json.loads((RAW / brand / "japan.json").read_text(encoding="utf-8"))
    lines.append(f"  japan.json tab={sample.get('tab')} url={sample.get('url')}")
    for p in (sample.get("plans") or [])[:4]:
        lines.append("    " + json.dumps(p, ensure_ascii=False))
OUT.write_text("\n".join(lines), encoding="utf-8")
