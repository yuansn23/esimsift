#!/usr/bin/env python3
"""Stage official-site captures into raw/<brand>/ so build_plans.py can ingest them.

- bnesim : api.bnesim.com pricing dump -> raw/bnesim/<our-slug>.json  (per tracked country)
- firsty : one global price model -> raw/firsty/_global.json           (no per-country pricing)

Keeps the raw/ -> plans/*.toml pipeline uniform across esimdb brands and
official-site brands, following the maya precedent.
"""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "_competitors"
RAW = BASE / "raw"
PROBE = BASE / "_superseded" / "_probe_out_of_scope"

# our slug -> ISO2 (bnesim coverages are ISO2)
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

# ---------------- bnesim ----------------
price = json.loads((PROBE / "bnesim_pricing_api.json").read_text(encoding="utf-8"))
prods = price.get("products") or []
cc_names = {}
for iso2, langs in (price.get("countries") or {}).items():
    en = langs.get("en") if isinstance(langs, dict) else None
    cc_names[iso2] = (en or {}).get("country_name") or iso2

out_b = RAW / "bnesim"
out_b.mkdir(parents=True, exist_ok=True)
staged = 0
for slug, iso2 in sorted(SLUG_ISO2.items()):
    singles = []
    regionals = []
    for pr in prods:
        cov = pr.get("coverages") or []
        if iso2 not in cov:
            continue
        rec = {
            "id": pr.get("id"),
            "name": pr.get("name"),
            "amount": pr.get("amount"),
            "unit": pr.get("unit"),
            "price": pr.get("price"),
            "full_price": pr.get("full_price"),
            "currency": pr.get("currency"),
            "duration": pr.get("duration"),
            "infinity": pr.get("infinity"),
            "carriers": pr.get("carriers"),
            "networks": pr.get("networks"),
            "networkSpeed": pr.get("networkSpeed"),
            "best_networks_speed": pr.get("best_networks_speed"),
            "region": pr.get("region"),
            "flag_class": pr.get("flag_class"),
            "esim": pr.get("esim"),
            "sms": pr.get("sms"),
            "phoneNumber": pr.get("phoneNumber"),
        }
        (regionals if pr.get("regional") else singles).append(rec)
    payload = {
        "brand": "bnesim",
        "slug": slug,
        "iso2": iso2,
        "country_name": cc_names.get(iso2),
        "url": f"https://www.bnesim.com/plans/{iso2.lower()}/",
        "source": "api.bnesim.com/v0.1/sim_card_landing_pricing/ (public)",
        "status": 200 if singles else 0,
        "plans": singles,
        "regional_options": regionals,
    }
    (out_b / f"{slug}.json").write_text(json.dumps(payload, indent=1, ensure_ascii=False), encoding="utf-8")
    staged += 1
print(f"bnesim: staged {staged} country files -> {out_b}")

# ---------------- firsty ----------------
# Firsty has ONE global price list (no per-country pricing) -> single global record.
fy = json.loads((BASE / "plans" / "firsty" / "firsty_pricing_model.json").read_text(encoding="utf-8"))
out_f = RAW / "firsty"
out_f.mkdir(parents=True, exist_ok=True)
glob = {
    "brand": "firsty",
    "scope": "global (single price list, identical in every country)",
    "url": "https://www.firsty.app/",
    "source": "firsty.app official pages",
    "pricing_model": fy["pricing_model"],
    "price_points": fy.get("concrete_price_points_observed"),
    "coverage_countries": (fy.get("coverage") or {}).get("countries_claimed"),
}
(out_f / "_global.json").write_text(json.dumps(glob, indent=1, ensure_ascii=False), encoding="utf-8")
print(f"firsty: staged _global.json -> {out_f}")
