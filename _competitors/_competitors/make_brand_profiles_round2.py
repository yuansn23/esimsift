#!/usr/bin/env python3
"""Write brand/ profile JSON for the 4 newly added brands (roamless, gomoworld,
bnesim, firsty), matching the existing schema, with Trustpilot placeholders.

Facts are limited to what was actually observed this round (official site meta,
captured API/JSON-LD, esimdb presence). Nothing is invented.
"""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "_competitors"
BRAND = BASE / "brand"
PROBE = BASE / "_superseded" / "_probe_out_of_scope"
CAPTURED = "2026-10-04"


def tp(domain):
    return {
        "url": f"https://www.trustpilot.com/review/{domain}",
        "rating": None, "review_count": None, "trust_score": None,
        "five_star_pct": None, "verified_reviews": None,
        "last_checked": None, "recent_reviews": [],
        "note": "PLACEHOLDER - to be filled manually by the user",
    }


def write(key, payload):
    BRAND.mkdir(parents=True, exist_ok=True)
    (BRAND / f"{key}.json").write_text(
        json.dumps(payload, indent=1, ensure_ascii=False), encoding="utf-8")
    print(f"wrote brand/{key}.json")


# ---------------- roamless ----------------
write("roamless", {
    "brand_key": "roamless",
    "brand_name": "Roamless",
    "official_site": "https://roamless.com/",
    "captured": CAPTURED,
    "trustpilot": tp("roamless.com"),
    "official": {
        "http_status": None,
        "bytes": None,
        "organization_jsonld": None,
        "apps": [],
        "app_ratings": [],
        "meta": {},
        "emails_found": [],
        "social_links": [],
        "site_text_len": 0,
        "about_facts": [],
        "note": ("Official site NOT scraped this round: esimdb already exposes the full "
                 "plan matrix (1,304 rows across 50 countries), including the brand's "
                 "signature 'Pay-As-You-Go / No Expiry' badge and a free tier."),
    },
    "plan_source": "esimdb.com",
    "plan_rows": 1304,
    "feature_notes": [
        "'No expiry' validity appears on several plans (badge: Pay-As-You-Go) - not a "
        "fixed-day product; build_plans records days=0 for those.",
        "A $0.00 'FREE <country> eSIM & Data' entry exists (New Users Only, 525MB) - "
        "dropped by the price>0 rule in build_plans (not a purchasable plan).",
    ],
    "fetch_error": None,
})

# ---------------- gomoworld ----------------
write("gomoworld", {
    "brand_key": "gomoworld",
    "brand_name": "GoMoWorld",
    "official_site": "https://www.gomoworld.com/",
    "captured": CAPTURED,
    "trustpilot": tp("gomoworld.com"),
    "official": {
        "http_status": None, "bytes": None, "organization_jsonld": None,
        "apps": [], "app_ratings": [], "meta": {}, "emails_found": [],
        "social_links": [], "site_text_len": 0, "about_facts": [],
        "note": "Official site NOT scraped this round: esimdb exposes the plan matrix.",
    },
    "plan_source": "esimdb.com",
    "plan_rows": 200,
    "feature_notes": [
        "GoMoWorld is the travel-eSIM line of the GoMo (Irish MVNO) family; plans are "
        "conventional fixed GB / fixed days bundles (3-45 GB, 7-30 days).",
        "esimdb page prices carry a '€2 OFF' badge - the recorded price is the listed "
        "price, discount not applied.",
    ],
    "fetch_error": None,
})

# ---------------- bnesim ----------------
price = json.loads((PROBE / "bnesim_pricing_api.json").read_text(encoding="utf-8"))
cats = price.get("countries") or {}
write("bnesim", {
    "brand_key": "bnesim",
    "brand_name": "BNESIM",
    "brand_alias": ["bensim"],
    "official_site": "https://www.bnesim.com/",
    "captured": CAPTURED,
    "trustpilot": tp("bnesim.com"),
    "official": {
        "http_status": 200,
        "bytes": None,
        "organization_jsonld": None,
        "apps": [],
        "app_ratings": [],
        "meta": {
            "note": ("Gatsby SPA - HTML carries no prices. Plans are delivered at runtime by "
                     "api.bnesim.com/v0.1/sim_card_landing_pricing/ (public, no auth), which "
                     "was captured directly. See raw/bnesim/ and _probe_out_of_scope/."),
        },
        "emails_found": ["support@bnesim.com"],
        "social_links": [],
        "site_text_len": 0,
        "about_facts": [
            "BNESIM is operated by BNESIM Limited, Hong Kong (Unit C, 8/F, King Palace Plaza, "
            "Kwun Tong, Kowloon) - address from the App Store listing for the BNESIM app.",
            "Claim on site: coverage in 200+ countries and regions; named 'World's Best Travel "
            "SIM Provider' at the World Travel Tech Awards 2019-2025 (self-reported).",
            "Site states the eSIM is data-only: calls/SMS are not possible on the eSIM itself.",
        ],
        "pricing_api_dump": {
            "endpoint": "https://api.bnesim.com/v0.1/sim_card_landing_pricing/",
            "products_total": len(price.get("products") or []),
            "countries_in_payload": len(cats),
            "currency": "EUR",
            "sample_product_fields": ["name", "amount", "unit", "price", "duration",
                                      "coverages", "carriers", "networks", "networkSpeed"],
        },
    },
    "plan_source": "bnesim.com official API (public)",
    "plan_rows": 528,
    "feature_notes": [
        "Prices in the API are EUR for all locales.",
        "duration = -1 in the API for a large share of products -> recorded as days = 0 "
        "(no fixed validity stated), do not read as 'instant expiry'.",
        "Carriers are exposed per product (e.g. KDDI for Japan) - the only brand besides "
        "maya with machine-readable per-country carrier data.",
        "Hong Kong and Macao have no single-country product (only regional bundles) -> "
        "48/50 countries with plans.",
    ],
    "fetch_error": None,
})

# ---------------- firsty ----------------
fy = json.loads((BASE / "plans" / "firsty" / "firsty_pricing_model.json").read_text(encoding="utf-8"))
write("firsty", {
    "brand_key": "firsty",
    "brand_name": "Firsty",
    "official_site": "https://www.firsty.app/",
    "captured": CAPTURED,
    "trustpilot": tp("firsty.app"),
    "official": {
        "http_status": 200,
        "bytes": None,
        "organization_jsonld": fy.get("ld_json_org"),
        "apps": fy.get("ld_json_app"),
        "app_ratings": [],
        "meta": {
            "note": ("Firsty sells ONE global price list, identical in every country - there "
                     "is no per-country pricing to scrape. Country pages (/<country>-esim, "
                     "250+) only restate the same model."),
        },
        "emails_found": [],
        "social_links": [],
        "site_text_len": 0,
        "about_facts": [
            "Free tier is ad-funded: watch a short ad to unlock a small data allowance "
            "(~20 MB at 1 Mbps per site copy, stacks, lasts 7 days).",
            "Classic: prepaid per-GB packages, 0.5-50 GB, from EUR 0.98/GB.",
            "Unlimited: per-day from EUR 2/day; 5 GB at high speed then 512 Kbps throttle.",
            "Coverage claim: 176 countries on the homepage.",
        ],
        "pricing_model": fy.get("pricing_model"),
        "stated_price_points": fy.get("concrete_price_points_observed"),
    },
    "plan_source": "firsty.app official pages",
    "plan_rows": 6,
    "feature_notes": [
        "Only 6 rows by design: the website exposes the model + floors + a few sample price "
        "points; the complete per-GB ladder is app-only. Nothing was inferred.",
        "Two different 10 GB figures (EUR 17.00 / EUR 19.50) appear in site copy; both are "
        "kept verbatim rather than reconciled.",
    ],
    "fetch_error": None,
})
