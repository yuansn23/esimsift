# -*- coding: utf-8 -*-
"""Brand profile extractor for the 5 competitor brands.

Pulls company facts from each brand's OFFICIAL site: JSON-LD Organization /
SoftwareApplication, meta description, app-store ratings, social links, and a few
regex'd facts (founded year, HQ, support contacts).

Trustpilot is intentionally NOT scraped: the `trustpilot` key is left as a
placeholder for the user to fill in by hand.

Output: _competitors/brand/<brand>.json
"""
import json
import re
from pathlib import Path

import requests

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "_competitors" / "brand"
OUT.mkdir(parents=True, exist_ok=True)

UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/148.0.0.0 Safari/537.36")

BRANDS = {
    "nomad": {
        "name": "Nomad eSIM", "site": "https://www.nomadesim.com/en-US",
        "trustpilot_url": "https://www.trustpilot.com/review/www.nomadesim.com",
    },
    "jetpac": {
        "name": "Jetpac Travel eSIM", "site": "https://www.jetpacglobal.com/",
        "trustpilot_url": "https://www.trustpilot.com/review/jetpacglobal.com",
    },
    "gigsky": {
        "name": "GigSky", "site": "https://www.gigsky.com/",
        "trustpilot_url": "https://www.trustpilot.com/review/gigsky.com",
    },
    "maya": {
        "name": "Maya Mobile", "site": "https://maya.net/",
        "trustpilot_url": "https://www.trustpilot.com/review/maya.net",
    },
    "quibity": {
        "name": "Quibity eSIM", "site": "https://quibity.com/",
        "trustpilot_url": "https://www.trustpilot.com/review/quibity.com",
    },
}


def jsonld(html):
    for b in re.findall(r'<script[^>]*application/ld\+json[^>]*>(.*?)</script>', html, re.S):
        try:
            j = json.loads(b)
        except Exception:
            continue
        yield from (j if isinstance(j, list) else [j])


def profile(url, html):
    org, app, ratings, social = None, [], [], set()
    for it in jsonld(html):
        if not isinstance(it, dict):
            continue
        t = it.get("@type")
        if t == "Organization" and org is None:
            org = {k: it.get(k) for k in
                   ("name", "alternateName", "url", "description", "foundingDate",
                    "logo", "address", "contactPoint", "sameAs")}
        if t in ("SoftwareApplication", "MobileApplication"):
            o = it.get("offers") if isinstance(it.get("offers"), dict) else {}
            app.append({
                "name": it.get("name"),
                "operatingSystem": it.get("operatingSystem"),
                "downloadUrl": it.get("downloadUrl"),
                "app_price": o.get("price"),
                "app_store_url": o.get("url"),
            })
            if it.get("aggregateRating"):
                ratings.append({"name": it.get("name"), **it["aggregateRating"]})

    text = re.sub(r"<script.*?</script>|<style.*?</style>", " ", html, flags=re.S)
    text = re.sub(r"<[^>]+>", " ", text)
    text = re.sub(r"\s+", " ", text)

    meta = {}
    for k in ("description", "og:description", "og:site_name"):
        m = re.search(rf'<meta[^>]+(?:name|property)="{re.escape(k)}"[^>]+content="([^"]{{10,400}})"', html)
        if m:
            meta[k] = m.group(1).strip()

    support = sorted(set(re.findall(r"[\w.+-]+@[\w-]+\.[\w.]{2,10}", html)))[:8]
    for a in re.findall(r'href="(https?://(?:www\.)?(?:facebook|instagram|twitter|x|linkedin|youtube|tiktok|trustpilot)\.[^"]{4,80})"', html):
        social.add(a)

    return {
        "organization_jsonld": org,
        "apps": app,
        "app_ratings": ratings,
        "meta": meta,
        "emails_found": support,
        "social_links": sorted(social)[:12],
        "site_text_len": len(text),
    }


def main():
    s = requests.Session()
    s.headers.update({"User-Agent": UA, "Accept-Language": "en-US,en;q=0.9"})
    for key, b in BRANDS.items():
        rec = {
            "brand_key": key,
            "brand_name": b["name"],
            "official_site": b["site"],
            "captured": "2026-10-04",
            # ---- placeholder: user supplies Trustpilot data manually ----
            "trustpilot": {
                "url": b["trustpilot_url"],
                "rating": None,
                "review_count": None,
                "trust_score": None,
                "five_star_pct": None,
                "verified_reviews": None,
                "last_checked": None,
                "recent_reviews": [],
                "note": "PLACEHOLDER - to be filled manually by the user",
            },
            "official": None,
            "fetch_error": None,
        }
        try:
            r = s.get(b["site"], timeout=35)
            rec["official"] = {"http_status": r.status_code, "bytes": len(r.text),
                               **profile(b["site"], r.text)}
            print(f"{key:8s} {r.status_code} {len(r.text):8d}  "
                  f"org={'Y' if rec['official']['organization_jsonld'] else 'n'} "
                  f"apps={len(rec['official']['apps'])} "
                  f"ratings={len(rec['official']['app_ratings'])}", flush=True)
        except Exception as e:
            rec["fetch_error"] = str(e)[:200]
            print(f"{key:8s} ERROR {str(e)[:110]}", flush=True)
        (OUT / f"{key}.json").write_text(json.dumps(rec, indent=1, ensure_ascii=False),
                                         encoding="utf-8")


if __name__ == "__main__":
    main()
