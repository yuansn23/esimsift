# -*- coding: utf-8 -*-
"""Jetpac (jetpacglobal.com) OFFICIAL plan scraper — 50 tracked countries.

Why official: esimdb has jetpac for 49/50 (fiji = 404) and exposes no carrier info.
Jetpac's country pages embed a JSON-LD Product/AggregateOffer with a full offers
array, e.g. for Japan:

  {"priceCurrency":"USD","lowPrice":5,"highPrice":65.99,"offerCount":24,
   "offers":[{"sku":"JAPAN-UNLIMITEDGB-3D","name":"Japan eSIM - Unlimited GB - 3 Days",
              "description":"... data valid for 3 Days.","price":10.99,
              "priceCurrency":"USD","priceValidUntil":"2027-12-31"}, ...]}

Real country pages are ~760KB-1MB; unknown slugs soft-404 to a ~360KB generic
page (HTTP 200), so we detect by page weight + presence of offerCount.

Output: _competitors/raw/jetpac_official/<our-slug>.json  (resumable)
"""
import json
import re
import sys
import time
from pathlib import Path

import requests

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "_competitors" / "raw" / "jetpac_official"
UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/148.0.0.0 Safari/537.36")

# candidate slugs to try, in priority order (first real hit wins)
CANDIDATES = {
    "united-states": ["united-states", "usa", "us"],
    "united-kingdom": ["uk", "united-kingdom", "great-britain"],
    "united-arab-emirates": ["uae", "united-arab-emirates"],
    "czechia": ["czechia", "czech-republic"],
    "turkiye": ["turkey", "turkiye"],
    "macao": ["macao", "macau"],
    "south-korea": ["south-korea", "korea"],
}
ALL = ["united-states", "united-kingdom", "canada", "mexico", "brazil", "argentina",
       "colombia", "peru", "costa-rica", "japan", "south-korea", "china",
       "hong-kong", "macao", "taiwan", "singapore", "thailand", "vietnam",
       "indonesia", "malaysia", "philippines", "india", "australia",
       "new-zealand", "fiji", "france", "germany", "italy", "spain",
       "portugal", "netherlands", "belgium", "switzerland", "austria",
       "ireland", "turkiye", "greece", "czechia", "croatia", "iceland",
       "poland", "georgia", "united-arab-emirates", "qatar", "israel",
       "saudi-arabia", "egypt", "morocco", "south-africa", "kenya"]

FORCE = "--force" in sys.argv


def jsonld_blocks(html: str):
    for b in re.findall(r'<script[^>]*application/ld\+json[^>]*>(.*?)</script>', html, re.S):
        try:
            yield json.loads(b)
        except Exception:
            continue


def extract(html: str) -> dict:
    offers, aggregate, org, ratings = [], None, None, []
    for j in jsonld_blocks(html):
        items = j if isinstance(j, list) else [j]
        for it in items:
            if not isinstance(it, dict):
                continue
            t = it.get("@type")
            if t == "Organization" and org is None:
                org = {k: it.get(k) for k in
                       ("name", "url", "description", "foundingDate", "logo",
                        "address", "contactPoint", "sameAs", "alternateName")}
            if "offers" in it:
                o = it["offers"]
                if isinstance(o, dict) and isinstance(o.get("offers"), list):
                    aggregate = {k: o.get(k) for k in
                                 ("priceCurrency", "lowPrice", "highPrice", "offerCount")}
                    offers = [x for x in o["offers"] if isinstance(x, dict)]
                elif isinstance(o, list):
                    offers = [x for x in o if isinstance(x, dict) and "price" in x]
            if it.get("aggregateRating"):
                ratings.append({"name": it.get("name"), **it["aggregateRating"]})

    # carrier / network mentions in page text
    networks = sorted(set(re.findall(r'"network"\s*:\s*"([^"]{2,40})"', html)))
    h1 = re.search(r"<h1[^>]*>(.*?)</h1>", html, re.S)
    title = re.search(r"<title[^>]*>(.*?)</title>", html, re.S)
    return {
        "offers": offers,
        "aggregate": aggregate,
        "organization": org,
        "ratings": ratings,
        "networks": networks,
        "meta": {
            "title": title.group(1).strip() if title else None,
            "h1": re.sub(r"<[^>]+>", "", h1.group(1)).strip() if h1 else None,
            "bytes": len(html),
        },
    }


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    s = requests.Session()
    s.headers.update({"User-Agent": UA, "Accept-Language": "en-US,en;q=0.9"})
    todo = [c for c in ALL if FORCE or not (OUT / f"{c}.json").exists()]
    print(f"### jetpac official: {len(todo)} countries", flush=True)
    stats = {"ok": 0, "empty": [], "fail": []}
    for i, c in enumerate(todo, 1):
        cands = CANDIDATES.get(c, [c])
        hit = None
        for slug in cands:
            url = f"https://www.jetpacglobal.com/{slug}-esim/"
            try:
                r = s.get(url, timeout=45)
            except Exception as e:
                print(f"    {slug}: ERR {str(e)[:60]}", flush=True)
                continue
            body = r.text
            # real page: heavy AND exposes an offers block
            if len(body) > 500_000 and '"offerCount"' in body:
                hit = (slug, url, body)
                break
            if len(body) > 500_000 and '"offers"' in body:
                hit = (slug, url, body)
                break
        if not hit:
            stats["fail"].append(c)
            print(f"[{i}/{len(todo)}] {c:22s} NO REAL PAGE (tried {cands})", flush=True)
            time.sleep(0.4)
            continue
        slug, url, body = hit
        res = extract(body)
        res.update({"slug": c, "jetpac_slug": slug, "url": url, "status": 200})
        n = len(res["offers"])
        (OUT / f"{c}.json").write_text(json.dumps(res, indent=1, ensure_ascii=False),
                                       encoding="utf-8")
        print(f"[{i}/{len(todo)}] {c:22s} /{slug:18s} offers={n:3d} "
              f"networks={len(res['networks']):3d} h1={res['meta']['h1']!r}", flush=True)
        if n: stats["ok"] += 1
        else: stats["empty"].append(c)
        time.sleep(0.5)
    print(f"=== jetpac official: ok={stats['ok']} empty={stats['empty']} fail={stats['fail']}",
          flush=True)


if __name__ == "__main__":
    main()
