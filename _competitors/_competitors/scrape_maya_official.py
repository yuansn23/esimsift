# -*- coding: utf-8 -*-
"""Maya Mobile (maya.net) plan scraper — 50 tracked countries.

Maya is NOT listed on esimdb, so it must come from the official site.

Each country page (https://maya.net/esim/<slug>) is Angular SSR and embeds a
transfer-state JSON payload containing structured plan objects:

  "plans":[{"_id":"...","productId":"...","name":"3 Days - Unlimited Global Data",
            "cycle":3,"cycleUnits":"day","dataUsageAllowanceType":"UNLIMITED",
            "priceBundle":{"USD":9.99,"EUR":8.49,...}}, ...]

and a per-country carrier map (ISO3 -> [{network, topService, apnAndroid, apnIOS, imsi}]).

Output: _competitors/raw/maya/<our-slug>.json   (resumable)
"""
import json
import re
import sys
import time
from pathlib import Path

import requests

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "_competitors" / "raw" / "maya"
UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/148.0.0.0 Safari/537.36")

# our slug -> maya.net/esim/<slug>  (maya uses full country names; UK and US are abbreviated)
MAYA_SLUGS = {
    "japan": "japan", "united-states": "usa", "united-kingdom": "uk",
    "france": "france", "italy": "italy", "thailand": "thailand",
    "south-korea": "south-korea", "singapore": "singapore", "spain": "spain",
    "germany": "germany", "australia": "australia", "taiwan": "taiwan",
    "hong-kong": "hong-kong", "macao": "macau", "malaysia": "malaysia",
    "vietnam": "vietnam", "indonesia": "indonesia", "philippines": "philippines",
    "india": "india", "china": "china", "portugal": "portugal",
    "netherlands": "netherlands", "belgium": "belgium",
    "switzerland": "switzerland", "austria": "austria", "greece": "greece",
    "turkiye": "turkey", "ireland": "ireland", "poland": "poland",
    "czechia": "czech-republic", "croatia": "croatia", "iceland": "iceland",
    "georgia": "georgia", "canada": "canada", "mexico": "mexico",
    "brazil": "brazil", "argentina": "argentina", "colombia": "colombia",
    "peru": "peru", "costa-rica": "costa-rica",
    "united-arab-emirates": "uae", "saudi-arabia": "saudi-arabia",
    "qatar": "qatar", "israel": "israel", "egypt": "egypt",
    "morocco": "morocco", "south-africa": "south-africa", "kenya": "kenya",
    "new-zealand": "new-zealand", "fiji": "fiji",
}

FORCE = "--force" in sys.argv


def balanced_objects(text: str, anchor: str):
    """Yield every balanced {...} JSON object that starts at an occurrence of `anchor`."""
    start = 0
    while True:
        i = text.find(anchor, start)
        if i < 0:
            return
        start = i + 1
        depth, in_str, esc, j = 0, False, False, i
        while j < len(text):
            c = text[j]
            if in_str:
                if esc:
                    esc = False
                elif c == "\\":
                    esc = True
                elif c == '"':
                    in_str = False
            else:
                if c == '"':
                    in_str = True
                elif c == "{":
                    depth += 1
                elif c == "}":
                    depth -= 1
                    if depth == 0:
                        yield text[i:j + 1]
                        break
            j += 1


def extract(html: str) -> dict:
    # ---- plans ----
    plans, seen = [], set()
    for blob in balanced_objects(html, '{"_id":"'):
        if '"priceBundle"' not in blob or '"name"' not in blob:
            continue
        try:
            p = json.loads(blob)
        except Exception:
            continue
        pid = p.get("productId") or p.get("_id")
        if pid in seen:
            continue
        seen.add(pid)
        pb = p.get("priceBundle") or {}
        plans.append({
            "product_id": pid,
            "name": p.get("name"),
            "cycle": p.get("cycle"),
            "cycle_units": p.get("cycleUnits"),
            "data_type": p.get("dataUsageAllowanceType"),
            "price_usd": pb.get("USD"),
            "price_bundle": pb,
            "public": p.get("public"),
            "activation_type": p.get("activationType"),
        })

    # ---- per-country carrier map: "JPN":[{"network":"...","topService":"..."}] ----
    carriers = {}
    for m in re.finditer(r'"([A-Z]{3})":\[(\{"network".*?\})\]', html):
        iso3, body = m.group(1), m.group(2)
        try:
            arr = json.loads("[" + body + "]")
        except Exception:
            continue
        nets = []
        for n in arr:
            if isinstance(n, dict) and n.get("network"):
                nets.append({"network": n["network"], "tech": n.get("topService"),
                             "apn": n.get("apnIOS") or n.get("apnAndroid")})
        if nets and iso3 not in carriers:
            carriers[iso3] = nets

    # ---- page identity ----
    h1 = re.search(r"<h1[^>]*>(.*?)</h1>", html, re.S)
    title = re.search(r"<title[^>]*>(.*?)</title>", html, re.S)
    return {
        "plans": plans,
        "carriers": carriers,
        "meta": {
            "title": title.group(1).strip() if title else None,
            "h1": re.sub(r"<[^>]+>", "", h1.group(1)).strip() if h1 else None,
            "bytes": len(html),
        },
    }


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    todo = [s for s in MAYA_SLUGS if FORCE or not (OUT / f"{s}.json").exists()]
    print(f"### maya: {len(todo)} countries to fetch", flush=True)
    s = requests.Session()
    s.headers.update({"User-Agent": UA, "Accept-Language": "en-US,en;q=0.9"})
    stats = {"ok": 0, "empty": [], "fail": []}
    for i, slug in enumerate(sorted(todo), 1):
        maya = MAYA_SLUGS[slug]
        url = f"https://maya.net/esim/{maya}"
        try:
            r = s.get(url, timeout=40)
            res = extract(r.text)
            res.update({"slug": slug, "maya_slug": maya, "url": url, "status": r.status_code})
            n = len(res["plans"])
            (OUT / f"{slug}.json").write_text(json.dumps(res, indent=1, ensure_ascii=False),
                                             encoding="utf-8")
            print(f"[{i}/{len(todo)}] {slug:22s} /{maya:18s} {r.status_code}  "
                  f"plans={n:3d} carriers={len(res['carriers']):3d}  h1={res['meta']['h1']!r}", flush=True)
            if n: stats["ok"] += 1
            else: stats["empty"].append(slug)
        except Exception as e:
            stats["fail"].append(slug)
            print(f"[{i}/{len(todo)}] {slug:22s} ERROR {str(e)[:80]}", flush=True)
        time.sleep(0.6)
    print(f"=== maya: ok={stats['ok']} empty={stats['empty']} fail={stats['fail']}", flush=True)


if __name__ == "__main__":
    main()
