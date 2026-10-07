# -*- coding: utf-8 -*-
"""Final inventory of _competitors (read-only) + counts."""
import json
from pathlib import Path

ROOT = Path(r"D:\HUGO test\29.1_windows-amd64\hugo_0.159.1_windows-amd64\esimsift-main\esimsift-main")
COMP = ROOT / "_competitors"
OUT = Path(r"C:\Users\27197\WorkBuddy\2026-10-04-19-19-25\_final.txt")

lines = []
total = {"ok": 0, "404": 0}
for brand in ("nomad", "jetpac", "gigsky", "quibity"):
    d = COMP / "raw" / brand
    files = sorted(d.glob("*.json")) if d.exists() else []
    ok = f404 = 0
    plans_sum = 0
    for f in files:
        try:
            j = json.loads(f.read_text(encoding="utf-8"))
            st = j.get("status")
            if st == 200:
                ok += 1
                plans_sum += len(j.get("plans") or [])
            elif st == 404:
                f404 += 1
        except Exception:
            pass
    total["ok"] += ok
    total["404"] += f404
    lines.append(f"raw/{brand:8s}: {len(files):2d} files | 200:{ok} 404:{f404} | total plans captured: {plans_sum}")

for p in sorted((COMP / "plans").rglob("*.json")):
    lines.append("plans: " + str(p.relative_to(COMP)))
for p in sorted((COMP / "brand").rglob("*.json")):
    lines.append("brand: " + str(p.relative_to(COMP)))
lines.append(f"TOTAL raw: ok={total['ok']} 404={total['404']} (expected 200 = 199, 404 = 1 jetpac/fiji)")
OUT.write_text("\n".join(lines), encoding="utf-8")
