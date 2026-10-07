#!/usr/bin/env python3
"""Parse maya.net homepage (Angular transfer state) -> _competitors/plans/maya/maya_official_home.json

Source of truth: the page's `application/json` transfer-state cache (CMS catalog),
NOT the marketing FAQ copy. Cross-checks are recorded explicitly.
Read-only input: _competitors/_probe/maya_home.html
"""
import json
import re
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "_competitors" / "_probe" / "maya_home.html"
OUT = ROOT / "_competitors" / "plans" / "maya" / "maya_official_home.json"

html = SRC.read_text(encoding="utf-8", errors="replace")
captured_at = datetime.fromtimestamp(SRC.stat().st_mtime, tz=timezone.utc).isoformat(timespec="seconds")

# --- ld+json ---
ld_blocks = []
for m in re.finditer(r'<script[^>]*type="application/ld\+json"[^>]*>(.*?)</script>', html, re.S):
    try:
        ld_blocks.append(json.loads(m.group(1).strip()))
    except json.JSONDecodeError:
        pass
ld_product = None
for blk in ld_blocks:
    for node in blk.get("@graph", [blk] if "@type" in blk else []):
        if isinstance(node, dict) and node.get("@type") == "Product":
            ld_product = node

# --- transfer state ---
m = re.search(r'<script[^>]*type="application/json"[^>]*>(.*?)</script>', html, re.S)
state = json.loads(m.group(1).strip())
cache = state["CACHE_CONTENT_STATE_KEY"]["cache"]


def norm_plan(pl, region_name):
    pb = pl.get("priceBundle") or {}
    validity_days = pl.get("validity") or pl.get("cycle")
    usd = pb.get("USD")
    out = {
        "name": pl.get("name"),
        "product_category": pl.get("productCategory"),
        "region": region_name,
        "data": "Unlimited" if pl.get("dataUsageAllowanceType") == "UNLIMITED" else pl.get("dataUsageAllowanceType"),
        "validity_days": validity_days,
        "price_usd": usd,
        "price_eur": pb.get("EUR"),
        "price_per_day_usd": round(usd / validity_days, 3) if usd and validity_days else None,
        "price_bundle_currencies": sorted(pb.keys()),
        "activation_type": pl.get("activationType"),
        "product_id": pl.get("productId"),
        "is_trending": pl.get("isTrending"),
        "best_for_value": pl.get("bestForValue"),
        "is_active": pl.get("isActive"),
        "auto_topup_enabled": pl.get("autoTopupEnabled"),
    }
    return out


def region_summary(reg):
    keys = ("planType", "technology", "tetheringSupport", "vpnSupport",
            "activationInfo", "installation", "deliveryTime", "allowedUsage")
    return {k: reg.get(k) for k in keys if reg.get(k)}


def collect(group_key, region_name):
    regs = cache.get(group_key) or []
    if not regs:
        return []
    reg = regs[0]
    plans = [norm_plan(p, region_name) for p in (reg.get("plans") or [])]
    return plans, reg


global_plans, global_reg = collect("globalRegions", "Global")
cruise_plans, cruise_reg = collect("cruiseRegions", "Global Cruise")

singles = cache.get("singleCountries") or []
regions_list = cache.get("regions") or []

out = {
    "brand": "maya",
    "brand_company": "Mobile Maya Inc",
    "source": "maya.net homepage - Angular transfer state (CMS catalog)",
    "source_url": "https://maya.net/",
    "captured_at": captured_at,
    "raw_file": "_competitors/_probe/maya_home.html",
    "ld_json_product": ld_product,
    "coverage": {
        "global": global_reg.get("supportedCountries"),
        "single_countries_in_catalog": len(singles),
        "multi_country_regions_in_catalog": len(regions_list),
        "cruises_in_catalog": len(cache.get("cruises") or []),
        "note": ("Per-country plans are NOT in the homepage transfer state "
                 "(plans arrays empty, lazy-loaded on destination pages). "
                 "Country slugs available in state -> future per-country scraping."),
    },
    "region_meta": {
        "global": region_summary(global_reg),
        "global_cruise": region_summary(cruise_reg),
    },
    "plans": {
        "global_unlimited": global_plans,
        "global_unlimited_plus_cruise": cruise_plans,
    },
    "cross_checks": {
        "ld_json_price_usd": (ld_product or {}).get("offers", {}).get("price"),
        "faq_copy_vs_catalog": [
            "FAQ copy: '14 Days Global + Cruise - $164.99 ($11.78/day)' "
            "vs catalog: USD 160.98 (API variant) / 160.99 (PDP variant) -> use catalog, verify on PDP later",
            "FAQ copy: '3 Days Global + Cruise - $49.99' vs catalog: USD 49.98 (API) / 49.99 (PDP)",
        ],
    },
    "marketing_claims_unverified": {
        "source": "on-page FAQ copy",
        "claims": [
            "165+ countries, 20+ cruises",
            "unlimited data, hotspot, 5G where available, zero throttling",
            "per-day: 3d $3.33, 7d $2.86, 14d $2.00, 30d $1.67",
        ],
    },
}

OUT.parent.mkdir(parents=True, exist_ok=True)
OUT.write_text(json.dumps(out, indent=1, ensure_ascii=False), encoding="utf-8")
print(f"wrote {OUT} plans: global={len(global_plans)} cruise={len(cruise_plans)}")
