# -*- coding: utf-8 -*-
"""Probe maya Angular transfer-state JSON for a structured plans array."""
import json
import re
from pathlib import Path

P = Path(__file__).resolve().parent
OUT = Path(r"C:\Users\27197\WorkBuddy\2026-10-04-19-19-25\_probe_out.txt")


def log(*a):
    OUT.open("a", encoding="utf-8").write(" ".join(str(x) for x in a) + "\n")


maya = (P / "maya_home.html").read_text(encoding="utf-8", errors="replace")
m = re.search(r'<script[^>]*type="application/json"[^>]*>(.*?)</script>', maya, re.S)
body = m.group(1).strip()
try:
    data = json.loads(body)
except Exception as e:
    log("outer parse err:", e)
    data = None

hits = []


def walk(node, path, depth=0):
    if depth > 9 or len(hits) > 60:
        return
    if isinstance(node, dict):
        for k, v in node.items():
            kl = str(k).lower()
            if any(t in kl for t in ("plan", "price", "package", "offer", "topup")):
                s = json.dumps(v, ensure_ascii=False)
                if 20 < len(s) < 4000:
                    hits.append((path + "/" + str(k), s[:1500]))
            walk(v, path + "/" + str(k), depth + 1)
    elif isinstance(node, list):
        for i, v in enumerate(node[:30]):
            walk(v, f"{path}[{i}]", depth + 1)


if data is not None:
    log("outer keys:", list(data.keys())[:20])
    walk(data, "$")
    seen = set()
    for p, s in hits:
        key = p.split("/")[-2:] if "/" in p else p
        sig = s[:80]
        if sig in seen:
            continue
        seen.add(sig)
        log("\nPATH:", p)
        log("VAL :", s)
