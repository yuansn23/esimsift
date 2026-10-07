# -*- coding: utf-8 -*-
"""Normalise every raw competitor capture into the esimsift plan schema.

Reads   : _competitors/raw/<source>/<slug>.json
Writes  : _competitors/plans/<brand>.toml      (same shape as data/plans/*.toml)
          _competitors/plans_all.csv           (flat summary, one row per plan)
          _competitors/COVERAGE.md             (per-brand x country coverage matrix)

Plan schema (mirrors the project's data model documented in scripts/scrape/scrape_esimdb.py):
  data "10GB"                 -> type=data,      gb=10
  data "1GB/Day"              -> type=data,      gb=1*days, fup_note="1 GB per day for N days"
  data "3GB/day + ∞ at 1Mbps" -> type=unlimited, gb=0, fup_note=<text>
  data "Unlimited"            -> type=unlimited, gb=0, fup_note=""

Nothing outside _competitors/ is touched.
"""
import csv
import json
import re
import tomllib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "_competitors"
RAW = BASE / "raw"
PLANS = BASE / "plans"
PLANS.mkdir(parents=True, exist_ok=True)
CAPTURED = "2026-10-04"

# brand -> (raw source dir, primary source label, kind)
# kind: esimdb | maya | bnesim | firsty
SOURCES = {
    "nomad":     ("nomad",     "esimdb.com", "esimdb"),
    "jetpac":    ("jetpac",    "esimdb.com", "esimdb"),
    "gigsky":    ("gigsky",    "esimdb.com", "esimdb"),
    "quibity":   ("quibity",   "esimdb.com", "esimdb"),
    "roamless":  ("roamless",  "esimdb.com", "esimdb"),
    "gomoworld": ("gomoworld", "esimdb.com", "esimdb"),
    "maya":      ("maya",      "maya.net (official)", "maya"),
    "bnesim":    ("bnesim",    "bnesim.com (official API)", "bnesim"),
    "firsty":    ("firsty",    "firsty.app (official)", "firsty"),
}


def countries():
    d = tomllib.loads((ROOT / "data" / "countries.toml").read_text(encoding="utf-8"))
    by_slug, by_iso = {}, {}
    for iso, c in d.items():
        if isinstance(c, dict) and c.get("slug"):
            by_slug[c["slug"]] = {"iso": iso, **c}
            by_iso[iso] = {"iso": iso, **c}
    return by_slug, by_iso


def parse_days(text):
    if not text:
        return 0
    m = re.search(r"(\d+(?:\.\d+)?)", text)
    return int(float(m.group(1))) if m else 0


def parse_size(text):
    """-> (gb_float, unit) ; unit in {gb, mb, unlimited, None}"""
    t = (text or "").strip()
    if not t:
        return None, None
    if re.search(r"unlimited|∞", t, re.I):
        return 0.0, "unlimited"
    m = re.search(r"(\d+(?:\.\d+)?)\s*(GB|MB)\b", t, re.I)
    if not m:
        return None, None
    v = float(m.group(1))
    return (v if m.group(2).upper() == "GB" else v / 1024), m.group(2).lower()


def norm_esimdb(plan):
    """esimdb card -> schema dict, or None if it isn't a priced plan.

    esimdb renders a few unpriced navigation/region cards (e.g. name 'United
    States', data '100MB', no price) alongside real plans. A plan with no
    parseable price is not a purchasable plan, so it is dropped.
    """
    data, validity, price = plan.get("data", ""), plan.get("validity", ""), plan.get("price", "")
    pm = re.search(r"([\d.]+)", price or "")
    if not pm:
        return None
    price_f = float(pm.group(1))
    if price_f <= 0:
        return None
    days = parse_days(validity)
    gb, unit = parse_size(data)

    daily = bool(re.search(r"/\s*(day|Day)", data or ""))
    has_unl = unit == "unlimited"
    note = ""

    if daily:
        per = gb or 0.0
        if has_unl:
            typ, gb_out = "unlimited", 0.0
            note = f"{per:g} GB per day at full speed, then unlimited" if per else (data or "")
        else:
            typ, gb_out = "data", round(per * days, 2) if days else per
            note = f"{per:g} GB per day for {days} days" if days else f"{per:g} GB per day"
    elif has_unl:
        typ, gb_out = "unlimited", 0.0
    else:
        typ, gb_out = "data", (gb or 0.0)

    return {"name": plan.get("name", ""), "gb": gb_out, "days": days, "type": typ,
            "price": price_f, "fup_note": note, "raw_data": data,
            "raw_validity": validity, "badges": plan.get("badges") or []}


def norm_maya(plan):
    name = (plan.get("name") or "").strip()
    # drop section headers ("Global", "Global Cruise") and unexposed products
    if plan.get("price_usd") in (None, 0) or not plan.get("cycle"):
        return None
    days = int(plan.get("cycle") or 0)
    dt = (plan.get("data_type") or "").upper()
    typ = "unlimited" if "UNLIMITED" in dt else "data"
    cruise = "cruise" in name.lower()
    return {"name": name, "gb": 0.0 if typ == "unlimited" else 0.0, "days": days,
            "type": typ, "price": float(plan["price_usd"]), "fup_note": "",
            "cruise_addon": cruise, "raw_data": dt, "raw_validity": f"{days} days",
            "badges": []}


def norm_bnesim(plan):
    """bnesim API product -> schema dict.

    Prices are EUR in the API (currency == 'EUR'); the project schema labels the
    price column "price_usd", so we keep the numeric value and flag the currency
    source in the TOML header + CSV (see main()). duration == -1 means the API
    states no fixed day count.
    """
    price = plan.get("price")
    try:
        price_f = float(price)
    except (TypeError, ValueError):
        return None
    if price_f <= 0:
        return None
    amount = plan.get("amount")
    unit = (plan.get("unit") or "GB").upper()
    infinity = bool(plan.get("infinity"))
    if infinity:
        typ, gb_out = "unlimited", 0.0
    elif amount is None:
        return None
    else:
        gb_out = float(amount) if unit == "GB" else float(amount) / 1024
        typ = "unlimited" if str(unit).lower() == "unlimited" else "data"
    d = plan.get("duration")
    days = int(d) if isinstance(d, (int, float)) and d > 0 else 0
    speeds = plan.get("networkSpeed") or []
    return {"name": plan.get("name") or "", "gb": gb_out, "days": days, "type": typ,
            "price": price_f, "fup_note": "",
            "raw_data": f"{amount} {unit}" if amount is not None else "unlimited",
            "raw_validity": f"{days} days" if days else "no fixed days",
            "speeds": speeds, "is_unlimited": infinity, "badges": []}


def norm_firsty_model(rec):
    """Firsty global price model -> schema dicts (one row per stated price point).

    Firsty has no per-country pricing, so rows are global. Only *stated* price
    points and floors are emitted; nothing is inferred.
    """
    rows = []
    model = rec.get("pricing_model") or {}
    tiers = {t.get("name"): t for t in (model.get("tiers") or [])}
    classic = tiers.get("Classic") or {}
    unl = tiers.get("Unlimited") or {}
    if classic.get("from_price_eur_per_gb") is not None:
        rows.append({"name": "Firsty Classic (from)", "gb": 1.0, "days": 0, "type": "data",
                     "price": float(classic["from_price_eur_per_gb"]), "fup_note": "per GB",
                     "raw_data": "per-GB pricing", "raw_validity": "n/a", "badges": ["floor price"]})
    if unl.get("from_price_eur_per_day") is not None:
        rows.append({"name": "Firsty Unlimited (from)", "gb": 0.0, "days": 1, "type": "unlimited",
                     "price": float(unl["from_price_eur_per_day"]),
                     "fup_note": "per day; 5 GB high speed then 512 Kbps",
                     "raw_data": "unlimited per day", "raw_validity": "1 day",
                     "badges": ["floor price"]})
    for pt in (rec.get("price_points") or []):
        gb, eur = pt.get("data_gb"), pt.get("price_eur")
        if gb and eur:
            rows.append({"name": f"Firsty Classic {gb:g} GB", "gb": float(gb), "days": 0,
                         "type": "data", "price": float(eur), "fup_note": "",
                         "raw_data": f"{gb:g} GB", "raw_validity": "n/a", "badges": ["stated price point"]})
    return rows


def dedupe(plans):
    """Collapse duplicates: key = (normalised name, days, price).

    Normalising the name folds cosmetic variants such as
    '3 Days - Unlimited Global Data' vs '3 Days Unlimited Global Data' (same
    product, different storefront SKU). Same-name plans at *different* prices are
    kept as separate rows on purpose.
    """
    def nkey(p):
        n = re.sub(r"[^a-z0-9]+", " ", (p["name"] or "").lower()).strip()
        return (n, p["days"], round(p["price"], 2) if p["price"] is not None else None)

    best = {}
    for p in plans:
        k = nkey(p)
        if k not in best:
            best[k] = p
    return list(best.values())


def main():
    by_slug, by_iso = countries()
    csv_rows, coverage = [], {}

    for brand, (src, label, kind) in SOURCES.items():
        d = RAW / src
        if not d.is_dir():
            print(f"SKIP {brand}: no raw dir {d}")
            continue
        files = sorted(d.glob("*.json"))
        out_lines = [
            f"# {brand} - competitor plan data",
            f"# primary source: {label}",
            f"# captured: {CAPTURED}   countries: {len(files)}",
            "# normalised to the esimsift plan schema (gb/days/type/price/fup_note).",
            "# NOTE: this file is a SEPARATE capture set - it is not wired into data/plans/.",
            "",
        ]
        if kind == "bnesim":
            out_lines.insert(4, "# CURRENCY: bnesim API prices are EUR (esimsift schema labels this column price).")
        if kind == "firsty":
            out_lines.insert(4, "# SCOPE: Firsty sells ONE global price list (no per-country pricing) -> global rows only.")
        per_country, total, ok_countries = {}, 0, 0

        for f in files:
            slug = f.stem
            rec = json.loads(f.read_text(encoding="utf-8"))
            meta = by_slug.get(slug)
            if not meta:
                if kind == "firsty":
                    # Firsty is a single global price list -> emit under a synthetic "GLOBAL" bucket
                    iso = "GLOBAL"
                else:
                    continue
            else:
                iso = meta["iso"]

            if kind == "maya":
                nets = []
                car = rec.get("carriers") or {}
                # maya's carrier map is ISO3-keyed; our project stores ISO2 -> use country name match
                iso3 = {"JP": "JPN", "US": "USA", "GB": "GBR", "FR": "FRA", "IT": "ITA",
                        "TH": "THA", "KR": "KOR", "SG": "SGP", "ES": "ESP", "DE": "DEU",
                        "AU": "AUS", "TW": "TWN", "HK": "HKG", "MO": "MAC", "MY": "MYS",
                        "VN": "VNM", "ID": "IDN", "PH": "PHL", "IN": "IND", "CN": "CHN",
                        "PT": "PRT", "NL": "NLD", "BE": "BEL", "CH": "CHE", "AT": "AUT",
                        "GR": "GRC", "TR": "TUR", "IE": "IRL", "PL": "POL", "CZ": "CZE",
                        "HR": "HRV", "IS": "ISL", "GE": "GEO", "CA": "CAN", "MX": "MXN",
                        "BR": "BRA", "AR": "ARG", "CO": "COL", "PE": "PER", "CR": "CRI",
                        "AE": "ARE", "SA": "SAU", "QA": "QAT", "IL": "ISR", "EG": "EGY",
                        "MA": "MAR", "ZA": "ZAF", "KE": "KEN", "NZ": "NZL", "FJ": "FJI"}.get(iso)
                for n in (car.get(iso3) or []):
                    if n.get("network"):
                        nets.append(n["network"] + (f" ({n['tech']})" if n.get("tech") else ""))
                raw_plans = rec.get("plans") or []
                parsed = [x for x in (norm_maya(p) for p in raw_plans) if x]
            elif kind == "bnesim":
                # carriers live on each product in the API -> aggregate per country
                nets = []
                for p in (rec.get("plans") or []):
                    for n in (p.get("carriers") or []):
                        if n and n not in nets:
                            nets.append(n)
                parsed = [x for x in (norm_bnesim(p) for p in (rec.get("plans") or [])) if x]
            elif kind == "firsty":
                nets = []
                parsed = norm_firsty_model(rec)
            else:
                nets = []
                parsed = [x for x in (norm_esimdb(p) for p in (rec.get("plans") or [])) if x]

            parsed = dedupe(parsed)
            per_country[iso] = {"slug": slug, "plans": parsed, "networks": nets,
                                "status": rec.get("status"), "url": rec.get("url")}
            total += len(parsed)
            if parsed:
                ok_countries += 1

        for iso in sorted(per_country):
            c = per_country[iso]
            out_lines.append(f"[{iso}]")
            out_lines.append(f'checked = "{CAPTURED}"')
            out_lines.append(f'source = "{label}"')
            out_lines.append(f'url = "{c["url"]}"')
            out_lines.append("networks = [" + ", ".join(json.dumps(n) for n in c["networks"]) + "]")
            out_lines.append("")
            for p in c["plans"]:
                out_lines.append(f"[[{iso}.plans]]")
                out_lines.append(f"name = {json.dumps(p['name'], ensure_ascii=False)}")
                out_lines.append(f"gb = {p['gb']:g}")
                out_lines.append(f"days = {p['days']}")
                out_lines.append(f'type = "{p["type"]}"')
                out_lines.append(f"price = {p['price']:.2f}" if p["price"] is not None else "price = 0.00")
                if p.get("fup_note"):
                    out_lines.append(f"fup_note = {json.dumps(p['fup_note'], ensure_ascii=False)}")
                if p.get("cruise_addon"):
                    out_lines.append("cruise_addon = true")
                out_lines.append("")
                csv_rows.append({
                    "brand": brand, "iso": iso, "slug": c["slug"],
                    "country": by_iso[iso]["name"] if iso in by_iso else ("Global" if iso == "GLOBAL" else ""),
                    "plan_name": p["name"], "gb": p["gb"], "days": p["days"],
                    "type": p["type"], "price": p["price"],
                    "currency": "EUR" if kind in ("bnesim", "firsty") else "USD",
                    "fup_note": p.get("fup_note", ""), "source": label,
                    "url": c["url"], "captured": CAPTURED,
                })
            out_lines.append("")

        (PLANS / f"{brand}.toml").write_text("\n".join(out_lines), encoding="utf-8")
        coverage[brand] = {"kind": kind, "source": label,
                           "countries_captured": len(files), "countries_with_plans": ok_countries,
                           "plans": total}
        print(f"{brand:10s} kind={kind:8s} countries={len(files):2d} with_plans={ok_countries:2d} plans={total:4d}")

    with (BASE / "plans_all.csv").open("w", newline="", encoding="utf-8-sig") as fh:
        w = csv.DictWriter(fh, fieldnames=list(csv_rows[0].keys()))
        w.writeheader()
        w.writerows(csv_rows)
    print(f"\nplans_all.csv rows = {len(csv_rows)}")

    with (BASE / "coverage.json").open("w", encoding="utf-8") as fh:
        json.dump(coverage, fh, indent=1, ensure_ascii=False)


if __name__ == "__main__":
    main()
