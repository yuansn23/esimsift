#!/usr/bin/env python3
"""Create Trustpilot placeholder structure for all 5 brands -> _competitors/brand/<brand>/trustpilot.json

Trustpilot is NOT scraped (WAF 403 on curl, needs browser automation - deliberate
scope cut for this round). These placeholders fix the schema so future scraping
only fills values. Domains below were verified from og:url of captured homepages.
"""
import json
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "_competitors" / "brand"

BRANDS = {
    "nomad":   "https://nomadesim.com",          # per recon (site needs browser; not captured this round)
    "jetpac":  "https://www.jetpacglobal.com",   # og:url verified
    "gigsky":  "https://www.gigsky.com",         # og:url verified
    "maya":    "https://maya.net",               # og:url verified
    "quibity": "https://quibity.com",            # og:url verified
}

for brand, site in BRANDS.items():
    data = {
        "brand": brand,
        "official_site": site,
        "source": "trustpilot",
        "status": "placeholder - not scraped (trustpilot blocks curl with 403; deferred, needs browser automation)",
        "tp_review_url": None,
        "tp_slug_hint": site.split("//", 1)[1].split("/")[0] + " (typical Trustpilot slug = brand domain, confirm before scraping)",
        "rating": None,
        "review_count": None,
        "rating_distribution": None,
        "fetched_at": None,
        "notes": "Fill tp_review_url + rating + review_count when Trustpilot scraping is scheduled.",
    }
    d = OUT / brand
    d.mkdir(parents=True, exist_ok=True)
    (d / "trustpilot.json").write_text(
        json.dumps(data, indent=1, ensure_ascii=False), encoding="utf-8")
    print(f"wrote {d / 'trustpilot.json'}")

readme = f"""# _competitors/brand/

Per-brand non-plan data (ratings, reviews, company info). One folder per brand.

## Status (generated {datetime.now(timezone.utc).date().isoformat()})

- `trustpilot.json` for all 5 brands (nomad / jetpac / gigsky / maya / quibity) is a
  **placeholder**: Trustpilot was deliberately NOT scraped this round (curl -> 403 WAF;
  scraping needs browser automation like the esimdb Playwright approach).
- Schema is fixed; a future scraper only fills `tp_review_url`, `rating`,
  `review_count`, `rating_distribution`, `fetched_at`.
- Jetpac's on-site aggregate rating (4.8 / 3276 reviews, from product JSON-LD) lives in
  `_competitors/plans/jetpac/jetpac_japan_offers.json` under `aggregate_rating` -
  do not duplicate it here until a real Trustpilot fetch happens.
"""
(OUT / "README.md").write_text(readme, encoding="utf-8")
print(f"wrote {OUT / 'README.md'}")
