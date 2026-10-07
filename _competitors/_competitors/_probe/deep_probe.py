# -*- coding: utf-8 -*-
"""Deep probe: dump maya ld+json + application/json state, jetpac Product ld+json."""
import json
import re
from pathlib import Path

P = Path(__file__).resolve().parent
OUT = Path(r"C:\Users\27197\WorkBuddy\2026-10-04-19-19-25\_probe_out.txt")


def log(*a):
    OUT.open("a", encoding="utf-8").write(" ".join(str(x) for x in a) + "\n")


OUT.write_text("", encoding="utf-8")  # reset

maya = (P / "maya_home.html").read_text(encoding="utf-8", errors="replace")

# 1. maya ld+json full
m = re.search(r'<script[^>]*type="application/ld\+json"[^>]*>(.*?)</script>', maya, re.S)
if m:
    try:
        log("== MAYA LD+JSON ==")
        log(json.dumps(json.loads(m.group(1)), indent=1, ensure_ascii=False)[:3000])
    except Exception as e:
        log("maya ld+json parse err:", e)

# 2. maya application/json script (Angular transfer state?)
log("\n== MAYA application/json scripts ==")
for i, m in enumerate(re.finditer(r'<script[^>]*type="application/json"[^>]*>(.*?)</script>', maya, re.S)):
    body = m.group(1).strip()
    log(f"--- json block #{i}: {len(body)} chars")
    log(body[:1200])
    log("...")

# 3. maya: all $price with wider context to catch plan names/data sizes
log("\n== MAYA price lines (dedup) ==")
seen = set()
for m in re.finditer(r"\$\d+\.\d{2}", maya):
    s = max(0, m.start() - 200)
    ctx = maya[s:m.end() + 100].replace("\\u003C", "<").replace("\n", " ")
    key = re.sub(r"\s+", " ", ctx)[-160:]
    if key in seen:
        continue
    seen.add(key)
    log("CTX:", key)

jet = (P / "jetpac_japan.html").read_text(encoding="utf-8", errors="replace")

# 4. jetpac Product ld+json (#6) full parse
log("\n== JETPAC LD+JSON blocks ==")
for i, m in enumerate(re.finditer(
        r'<script[^>]*type="application/ld\+json"[^>]*>(.*?)</script>', jet, re.S)):
    body = m.group(1).strip()
    try:
        data = json.loads(body)
    except Exception as e:
        log(f"#{i} parse err {e}; len={len(body)}")
        continue
    t = data.get("@type")
    log(f"--- #{i} type={t} len={len(body)}")
    if t == "Product":
        log(json.dumps(data, indent=1, ensure_ascii=False))
