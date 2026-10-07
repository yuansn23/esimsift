#!/usr/bin/env python3
"""Parse jetpacglobal.com product page JSON-LD -> _competitors/plans/jetpac/jetpac_japan_offers.json

Source of truth: <script type="application/ld+json"> Product block
(AggregateOffer -> offers[], each with additionalProperty Data allowance / Validity).
Read-only input: _competitors/_probe/jetpac_japan.html
"""
import json
import re
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "_competitors" / "_probe" / "jetpac_japan.html"
OUT = ROOT / "_competitors" / "plans" / "jetpac" / "jetpac_japan_offers.json"

html = SRC.read_text(encoding="utf-8", errors="replace")
captured_at = datetime.fromtimestamp(SRC.stat().st_mtime, tz=timezone.utc).isoformat(timespec="seconds")

blocks = []
for m in re.finditer(r'<script[^>]*type="application/ld\+json"[^>]*>(.*?)</script>', html, re.S):
    try:
        blocks.append(json.loads(m.group(1).strip()))
    except json.JSONDecodeError:
        pass

product = next((b for b in blocks if b.get("@type") == "Product"), None)
if product is None:
    raise SystemExit("no Product ld+json found")

props = product.get("additionalProperty") or []
agg = product.get("offers") or {}
offers_norm = []
for o in agg.get("offers", []):
    ap = {p.get("name"): p.get("value") for p in o.get("additionalProperty", []) if isinstance(p, dict)}
    offers_norm.append({
        "sku": o.get("sku"),
        "name": o.get("name"),
        "data": ap.get("Data allowance"),
        "validity": ap.get("Validity"),
        "price": o.get("price"),
        "currency": o.get("priceCurrency"),
        "price_valid_until": o.get("priceValidUntil"),
        "availability": (o.get("availability") or "").rsplit("/", 1)[-1],
    })
offers_norm.sort(key=lambda x: (0 if (x["data"] or "").startswith("Unlimited") else 1,
                                x["validity"] or "", x["price"] or 0))

out = {
    "brand": "jetpac",
    "source": "jetpacglobal.com product page JSON-LD (schema.org Product / AggregateOffer)",
    "source_url": product.get("url"),
    "captured_at": captured_at,
    "raw_file": "_competitors/_probe/jetpac_japan.html",
    "country": "japan",
    "area_served": (product.get("areaServed") or {}).get("name"),
    "brand_official": (product.get("brand") or {}).get("name"),
    "aggregate_rating": {
        "rating_value": (product.get("aggregateRating") or {}).get("ratingValue"),
        "review_count": (product.get("aggregateRating") or {}).get("reviewCount"),
        "note": "on-site rating shown in Product ld+json; trustpilot NOT scraped (placeholder only)",
    },
    "aggregate_offer": {
        "low_price": agg.get("lowPrice"),
        "high_price": agg.get("highPrice"),
        "offer_count_declared": agg.get("offerCount"),
        "offer_count_extracted": len(offers_norm),
        "currency": agg.get("priceCurrency"),
    },
    "offers": offers_norm,
    "notes": [
        "Voice packs / messaging features appear only in RSC flight data as copy, not structured - not extracted.",
        "priceValidUntil 2027-12-31 on all offers (likely placeholder expiry set by Jetpac).",
    ],
}

OUT.parent.mkdir(parents=True, exist_ok=True)
OUT.write_text(json.dumps(out, indent=1, ensure_ascii=False), encoding="utf-8")
print(f"wrote {OUT} offers={len(offers_norm)}")
