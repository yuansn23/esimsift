#!/usr/bin/env python3
"""Parse Firsty official pages -> _competitors/plans/firsty/firsty_pricing_model.json

Firsty sells ONE pricing model, identical in every country ("Same price, every
country"): Free (ad-based) / Classic (per-GB packages) / Unlimited (per-day).
The full per-GB price ladder lives in the app, NOT on the website - the website
exposes the model, floor prices, and a few concrete package price points, which
is what this parser records (no invention).

Inputs (all playwright-captured):
  _probe/firsty_home.html          homepage
  _probe/firsty_classic_plans.html /plans/classic
  _probe/firsty_japan_esim.html    /japan-esim (country page sample)
"""
import json
import re
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
P = ROOT / "_competitors" / "_superseded" / "_probe_out_of_scope"
OUT = ROOT / "_competitors" / "plans" / "firsty" / "firsty_pricing_model.json"


def mt(p):
    return datetime.fromtimestamp((P / p).stat().st_mtime, tz=timezone.utc).isoformat(timespec="seconds")


def ld_json(html):
    blocks = []
    for m in re.finditer(r'<script[^>]*type="application/ld\+json"[^>]*>(.*?)</script>', html, re.S):
        try:
            blocks.append(json.loads(m.group(1).strip()))
        except json.JSONDecodeError:
            pass
    return blocks


home = (P / "firsty_home.html").read_text(encoding="utf-8", errors="replace")
classic = (P / "firsty_classic_plans.html").read_text(encoding="utf-8", errors="replace")
japan = (P / "firsty_japan_esim.html").read_text(encoding="utf-8", errors="replace")

# --- concrete package price points stated on official pages ---
# Strict pattern only: "<N> GB for €<X>" / "<N> GB" within a short span of "€<X>".
# Loose GB...€ proximity matching pulls in unrelated figures from FAQ copy, so it
# is deliberately avoided (see README note on Firsty data granularity).
price_points = set()
for html in (home, classic, japan):
    for m in re.finditer(r"(\d+(?:\.\d+)?)\s*GB\s+for\s+€\s?(\d+(?:\.\d+)?)", html, re.I):
        price_points.add((float(m.group(1)), float(m.group(2))))
price_points = sorted(price_points, key=lambda x: x[0])

# --- floor prices ---
floors = {}
m = re.search(r"Starts at\s*€\s?(\d+[.,]\d+)\s*per\s*GB", home) or \
    re.search(r"€\s?(\d+[.,]\d+)\s*per\s*GB", home)
if m:
    floors["classic_per_gb_from_eur"] = float(m.group(1).replace(",", "."))
m = re.search(r"Starts at\s*€\s?(\d+)\s*per\s*day", home) or re.search(r"€\s?(\d+)\s*per\s*day", home)
if m:
    floors["unlimited_per_day_from_eur"] = float(m.group(1))

# --- country page sample: carrier names in meta description ---
m = re.search(r"mobile data in ([A-Za-z ]+?) on ([^.]+?)\.", japan)
country_sample = None
if m:
    country_sample = {
        "page": "https://www.firsty.app/japan-esim",
        "country": m.group(1).strip(),
        "carriers_named": [n.strip() for n in re.split(r",| and ", m.group(2)) if n.strip()],
    }

faq = next((b for b in ld_json(home) if b.get("@type") == "FAQPage"), None)
org = next((b for b in ld_json(home) if b.get("@type") == "Organization"), None)
app = next((b for b in ld_json(home) if b.get("@type") == "SoftwareApplication"), None)

out = {
    "brand": "firsty",
    "brand_company": (org or {}).get("name") or "Firsty Inc",
    "source": "firsty.app official pages (homepage / /plans/classic / /japan-esim)",
    "source_urls": [
        "https://www.firsty.app/",
        "https://www.firsty.app/plans/classic",
        "https://www.firsty.app/japan-esim",
    ],
    "captured_at": max(mt("firsty_home.html"), mt("firsty_classic_plans.html"), mt("firsty_japan_esim.html")),
    "raw_files": [
        "_competitors/_superseded/_probe_out_of_scope/firsty_home.html",
        "_competitors/_superseded/_probe_out_of_scope/firsty_classic_plans.html",
        "_competitors/_superseded/_probe_out_of_scope/firsty_japan_esim.html",
    ],
    "pricing_model": {
        "schema": "one global price list - identical in every country (no per-country pricing)",
        "tiers": [
            {"name": "Free", "price": 0, "currency": "EUR",
             "mechanics": "watch a short ad to unlock ~20 MB at basic speed (1 Mbps); data stacks and lasts 7 days",
             "availability_note": "available to users in North America, Europe & APAC per site copy"},
            {"name": "Classic", "billing": "prepaid per-GB packages",
             "packages_gb_range": [0.5, 50], "from_price_eur_per_gb": floors.get("classic_per_gb_from_eur"),
             "notes": "high speed, no ads; pay only for the GB you need"},
            {"name": "Unlimited", "billing": "per-day",
             "from_price_eur_per_day": floors.get("unlimited_per_day_from_eur"),
             "notes": "5 GB at high speed per day, then 512 Kbps until next day/top-up; pausable"},
        ],
    },
    "concrete_price_points_observed": [
        {"data_gb": gb, "price_eur": eur, "implied_eur_per_gb": round(eur / gb, 3)} for gb, eur in price_points
    ],
    "concrete_price_points_note": (
        "Points are quoted from site copy and can disagree with each other across pages "
        "(e.g. two different 10 GB figures appear: EUR 17.00 and EUR 19.50). Both are kept "
        "verbatim rather than reconciled; the app is the only authoritative price source."),
    "coverage": {"countries_claimed": 176, "note": "site copy: 'Stay online in 176 countries'"},
    "country_page_sample": country_sample,
    "notes": [
        "Full per-GB price ladder is app-only; website exposes floors + a few sample points only.",
        "Country pages exist for 250+ destinations at /{country}-esim, but they only restate the same global model.",
        "FAQPage ld+json captured in raw file (7.4KB) for any further Q&A mining.",
    ],
    "ld_json_org": org,
    "ld_json_app": app,
    "faq_questions": [q.get("name") for q in (faq or {}).get("mainEntity", [])] if faq else [],
}

OUT.parent.mkdir(parents=True, exist_ok=True)
OUT.write_text(json.dumps(out, indent=1, ensure_ascii=False), encoding="utf-8")
print(f"wrote {OUT}")
print("price points:", price_points, "floors:", floors)
