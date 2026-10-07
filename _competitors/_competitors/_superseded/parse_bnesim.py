#!/usr/bin/env python3
"""Parse BNESIM public pricing API dump -> _competitors/plans/bnesim/.

Input : _competitors/_probe/bnesim_pricing_api.json
        (captured from https://api.bnesim.com/v0.1/sim_card_landing_pricing/
         - public endpoint the /plans/{cc}/ pages call at runtime)
Output: _competitors/plans/bnesim/bnesim_catalog.json     normalized full catalog
        _competitors/plans/bnesim/bnesim_by_country.json  single-country products
                                                          for the 50 tracked slugs

Note: user shorthand "bensim" == BNESIM (bnesim.com). esimdb has no such brand (404).
"""
import json
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "_competitors" / "_probe" / "bnesim_pricing_api.json"
OUTDIR = ROOT / "_competitors" / "plans" / "bnesim"

# our country slug -> ISO2 (BNESIM coverages use ISO 3166-1 alpha-2)
SLUG_ISO2 = {
    "united-states": "US", "united-kingdom": "GB", "canada": "CA", "mexico": "MX",
    "brazil": "BR", "argentina": "AR", "colombia": "CO", "peru": "PE",
    "costa-rica": "CR", "japan": "JP", "south-korea": "KR", "china": "CN",
    "hong-kong": "HK", "macao": "MO", "taiwan": "TW", "singapore": "SG",
    "thailand": "TH", "vietnam": "VN", "indonesia": "ID", "malaysia": "MY",
    "philippines": "PH", "india": "IN", "australia": "AU", "new-zealand": "NZ",
    "fiji": "FJ", "france": "FR", "germany": "DE", "italy": "IT", "spain": "ES",
    "portugal": "PT", "netherlands": "NL", "belgium": "BE", "switzerland": "CH",
    "austria": "AT", "ireland": "IE", "turkiye": "TR", "greece": "GR",
    "czechia": "CZ", "croatia": "HR", "iceland": "IS", "poland": "PL",
    "georgia": "GE", "united-arab-emirates": "AE", "qatar": "QA", "israel": "IL",
    "saudi-arabia": "SA", "egypt": "EG", "morocco": "MA", "south-africa": "ZA",
    "kenya": "KE",
}

raw = json.loads(SRC.read_text(encoding="utf-8"))
prods = raw.get("products") or []
captured_at = datetime.fromtimestamp(SRC.stat().st_mtime, tz=timezone.utc).isoformat(timespec="seconds")

catalog = []
for pr in prods:
    amount = pr.get("amount")
    unit = pr.get("unit") or "GB"
    price = pr.get("price")
    duration = pr.get("duration")
    catalog.append({
        "id": pr.get("id"),
        "name": pr.get("name"),
        "data": f"{amount} {unit}" if amount is not None else None,
        "data_gb": (amount / 1024.0 if unit == "MB" else amount) if amount is not None else None,
        "is_unlimited": bool(pr.get("infinity")),
        "validity_days": duration if isinstance(duration, (int, float)) and duration > 0 else None,
        "validity_note": "duration=-1 in API (no fixed days stated)" if duration in (-1, None) else None,
        "price_eur": float(price) if price not in (None, "") else None,
        "price_original_eur": float(pr["full_price"]) if pr.get("full_price") not in (None, "", "0.00") else None,
        "currency": pr.get("currency"),
        "coverage_iso2": pr.get("coverages"),
        "is_regional": bool(pr.get("regional")),
        "region_label": pr.get("region"),
        "carriers": pr.get("carriers"),
        "networks_detail": pr.get("networks"),
        "best_network_speed": pr.get("best_networks_speed"),
        "network_speeds": pr.get("networkSpeed"),
        "esim": pr.get("esim"),
        "rechargeable": pr.get("rechargeable"),
        "phone_number": pr.get("phoneNumber"),
        "sms": pr.get("sms"),
    })

by_country = {}
missing = []
for slug, iso2 in sorted(SLUG_ISO2.items()):
    singles = [p for p in catalog
               if p["coverage_iso2"] and iso2 in p["coverage_iso2"] and not p["is_regional"]]
    regionals = [p["id"] for p in catalog
                 if p["coverage_iso2"] and iso2 in p["coverage_iso2"] and p["is_regional"]]
    if singles:
        by_country[slug] = {
            "iso2": iso2,
            "single_country_plans": singles,
            "regional_plan_ids_including": regionals,
        }
    else:
        missing.append(f"{slug}({iso2}) singles=0 regionals={len(regionals)}")

stats = {
    "products_total": len(catalog),
    "products_regional": sum(1 for p in catalog if p["is_regional"]),
    "products_unlimited_flag": sum(1 for p in catalog if p["is_unlimited"]),
    "countries_in_catalog": len(raw.get("countries") or {}),
    "tracked_slugs_with_single_country_plans": len(by_country),
    "tracked_slugs_without_single_country_plans": missing,
    "carriers_seen": sorted({c for p in catalog for c in (p["carriers"] or [])}),
}

OUTDIR.mkdir(parents=True, exist_ok=True)
cat_out = {
    "brand": "bnesim",
    "brand_alias": ["bensim"],
    "brand_company": "BNESIM Limited",
    "source": "bnesim.com runtime API /v0.1/sim_card_landing_pricing/ (public, no auth)",
    "captured_at": captured_at,
    "raw_file": "_competitors/_probe/bnesim_pricing_api.json",
    "currency_note": "API prices are EUR regardless of display currency",
    "stats": stats,
    "products": catalog,
}
(OUTDIR / "bnesim_catalog.json").write_text(
    json.dumps(cat_out, indent=1, ensure_ascii=False), encoding="utf-8")

by_out = {
    "brand": "bnesim",
    "captured_at": captured_at,
    "tracked_countries": 50,
    "countries": by_country,
}
(OUTDIR / "bnesim_by_country.json").write_text(
    json.dumps(by_out, indent=1, ensure_ascii=False), encoding="utf-8")

print(f"wrote {OUTDIR}/bnesim_catalog.json products={len(catalog)}")
print(f"wrote {OUTDIR}/bnesim_by_country.json countries={len(by_country)}")
print("stats:", json.dumps(stats, ensure_ascii=False)[:500])
