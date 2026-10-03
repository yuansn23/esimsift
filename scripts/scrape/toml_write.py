#!/usr/bin/env python3
"""Convert scraped esimdb raw JSON -> data/plans/<provider>.toml

Usage: python -X utf8 scripts/scrape/toml_write.py <provider> [--dry-run]

Parsing rules (raw 'data' text -> model):
  "10GB"                     -> type=data, gb=10
  "1GB/Day"                  -> daily allowance: type=data, gb=1*days,
                                fup_note="1 GB per day for N days (daily refresh)"
  "3GB/day + ∞ at 1Mbps"     -> type=unlimited, gb=0, fup_note=<text>
  "Unlimited"                -> type=unlimited, gb=0, fup_note="" (or page-level
                                raw "fup" wording, e.g. holafly PDP Always On)
  "5GB/month" + Monthly      -> subscription: days=30, gb=5, fup_note notes renewal
  "5GB/month" + Yearly       -> days=365, gb=5*12 (annual total keeps $/GB honest)
Unparsed data/validity/price -> logged, plan skipped (manual review list).
"""
import json
import re
import sys
import tomllib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
RAW = Path(__file__).resolve().parent / "raw"

CHECKED = "2026-09-30"

RX_FIXED = re.compile(r"^(\d+(?:\.\d+)?)\s*GB$", re.I)
RX_FIXED_MB = re.compile(r"^(\d+(?:\.\d+)?)\s*MB$", re.I)
RX_DAILY = re.compile(r"^(\d+(?:\.\d+)?)\s*GB\s*/\s*day$", re.I)
RX_GB_MONTH = re.compile(r"^(\d+(?:\.\d+)?)\s*GB\s*/\s*month$", re.I)
RX_UNLIM_CAP = re.compile(r"^(\d+(?:\.\d+)?)\s*GB\s*/\s*day\s*\+\s*(.+)$", re.I)
RX_DAYS = re.compile(r"^(\d+)\s*Days?$", re.I)
RX_PRICE = re.compile(r"^\$\s*([\d,]+(?:\.\d+)?)\s*(?:/\s*(?:mo|month|yr|year))?$", re.I)


def toml_str(s: str) -> str:
    return json.dumps(s, ensure_ascii=False)


# --- plan-name normalisation -------------------------------------------------
# Site copy is English-only. Upstream listings occasionally name a plan with a
# local-language word: most are Latin script ("Élan", "Fáilte", "Prosím") and are
# the provider's real product name -> kept verbatim. Non-Latin scripts (Airalo's
# Korean "짱 Jjang") must never reach a page; keep the Latin remainder.
NON_LATIN = re.compile(
    "["
    "\u0370-\u03FF"  # Greek
    "\u0400-\u04FF"  # Cyrillic
    "\u0530-\u058F"  # Armenian
    "\u0590-\u05FF"  # Hebrew
    "\u0600-\u06FF\u0750-\u077F"  # Arabic
    "\u0900-\u097F"  # Devanagari
    "\u0980-\u09FF"  # Bengali
    "\u0B80-\u0BFF"  # Tamil
    "\u0D80-\u0DFF"  # Sinhala
    "\u0E00-\u0E7F"  # Thai
    "\u0E80-\u0EFF"  # Lao
    "\u1000-\u109F"  # Myanmar
    "\u10A0-\u10FF"  # Georgian
    "\u1100-\u11FF\u3130-\u318F\uAC00-\uD7AF"  # Hangul
    "\u1780-\u17FF"  # Khmer
    "\u1800-\u18AF"  # Mongolian
    "\u3040-\u309F\u30A0-\u30FF"  # Kana
    "\u3400-\u4DBF\u4E00-\u9FFF\uF900-\uFAFF"  # Han
    "]+"
)
normalized: list[str] = []


def clean_plan_name(raw: str, where: str) -> str:
    """Strip non-Latin script and leading junk from a scraped plan name.

    Drops non-Latin characters, collapses whitespace, and trims the stray
    leading punctuation the DOM sometimes carries (e.g. `'짱 Jjang - 1 GB`
    -> `Jjang - 1 GB`). Latin accents are intentionally preserved.
    """
    out = NON_LATIN.sub("", raw)
    out = re.sub(r"\s{2,}", " ", out)
    out = re.sub(r"^[^0-9A-Za-z\u00C0-\u024F]+", "", out)  # stray leading quotes/punct
    out = re.sub(r"\s+([-–—/])", r" \1", out).strip()
    if out and out != raw.strip():
        normalized.append(f"{where}: {raw.strip()!r} -> {out!r}")
        return out
    return raw.strip()


def parse_plan(p: dict, problems: list[str], where: str) -> dict | None:
    data_txt = p["data"].replace("\n", " ").strip()
    valid = p["validity"].strip()
    price_txt = p["price"].strip()
    name_lower = p["name"].lower()
    badges = " ".join(p.get("badges") or [])

    # validity: fixed days, or subscription period (Ubigi sells Monthly/Yearly subs)
    sub = ""
    m = RX_DAYS.match(valid)
    if m:
        days = int(m.group(1))
    elif valid.strip().lower() == "monthly":
        days, sub = 30, "monthly"
    elif valid.strip().lower() == "yearly":
        days, sub = 365, "yearly"
    else:
        problems.append(f"{where}: unparseable validity {valid!r} ({p['name']!r})")
        return None

    m = RX_PRICE.match(price_txt)
    if not m:
        problems.append(f"{where}: unparseable price {price_txt!r} ({p['name']!r})")
        return None
    price = float(m.group(1).replace(",", ""))
    if price <= 0:
        problems.append(f"{where}: price <= 0 ({price_txt!r})")
        return None

    plan = {"name": clean_plan_name(p["name"], where), "days": days, "price": round(price, 2)}

    # fair-use cap text lives in a badge on esimdb DOM ("+ ∞ at 1Mbps")
    cap_badge = ""
    for b in p.get("badges") or []:
        if "∞" in b or "mbps" in b.lower() or "kbps" in b.lower():
            cap_badge = b.strip().lstrip("+ ").strip()
            break

    if RX_UNLIM_CAP.match(data_txt):
        m = RX_UNLIM_CAP.match(data_txt)
        gb_day = float(m.group(1))
        cap_txt = m.group(2).strip()
        plan.update(gb=0, type="unlimited",
                    fup_note=f"{fmt_gb(gb_day)} per day at full speed, then {cap_txt}")
    elif data_txt.strip().lower() in ("unlimited", "unlimited data"):
        plan.update(gb=0, type="unlimited",
                    fup_note=(f"auto-renewing {sub} subscription" if sub else ""))
    elif RX_GB_MONTH.match(data_txt):
        # Ubigi subscriptions: "5GB/month" Monthly or Yearly billing
        m = RX_GB_MONTH.match(data_txt)
        g_month = float(m.group(1))
        if cap_badge or "unlimited" in name_lower:
            cap = cap_badge or "unlimited at reduced speed"
            plan.update(gb=0, type="unlimited",
                        fup_note=f"{fmt_gb(g_month)} per month at full speed, then {cap} "
                                 f"({'auto-renewing monthly' if sub == 'monthly' else 'annual'} subscription)")
        elif sub == "monthly":
            plan.update(gb=round(g_month, 2), type="data",
                        fup_note=f"{fmt_gb(g_month)} per month (auto-renewing subscription)")
        elif sub == "yearly":
            # yearly price buys 12 monthly refreshes -> total keeps $/GB honest
            plan.update(gb=round(g_month * 12, 2), type="data",
                        fup_note=f"{fmt_gb(g_month)} per month for 12 months (annual subscription)")
    elif RX_DAILY.match(data_txt):
        m = RX_DAILY.match(data_txt)
        gb_day = float(m.group(1))
        if cap_badge or "unlimited" in name_lower:
            # daily full-speed cap + throttled unlimited after (Airalo "Unlimited" plans)
            cap = cap_badge or "unlimited at reduced speed"
            plan.update(gb=0, type="unlimited",
                        fup_note=f"{fmt_gb(gb_day)} per day at full speed, then {cap}")
        else:
            # hard daily allowance, total = gb_day * days (keeps $/GB honest)
            plan.update(gb=round(gb_day * days, 2), type="data",
                        fup_note=f"{fmt_gb(gb_day)} per day for {days} days (daily refresh)")
    elif RX_FIXED.match(data_txt):
        m = RX_FIXED.match(data_txt)
        if "unlimited" in name_lower and cap_badge:
            # esimdb shows a 1-day daily-cap plan's allowance as a total ("3GB"),
            # but the name + ∞ badge mark it as unlimited (verified: all brands)
            plan.update(gb=0, type="unlimited",
                        fup_note=f"{fmt_gb(float(m.group(1)))} per day at full speed, then {cap_badge}")
        else:
            plan.update(gb=float(m.group(1)), type="data")
    elif RX_FIXED_MB.match(data_txt):
        m = RX_FIXED_MB.match(data_txt)
        if "unlimited" in name_lower and cap_badge:
            mb = float(m.group(1)) / 1024
            plan.update(gb=0, type="unlimited",
                        fup_note=f"{fmt_gb(mb)} per day at full speed, then {cap_badge}")
        else:
            plan.update(gb=round(float(m.group(1)) / 1024, 4), type="data")
    else:
        problems.append(f"{where}: unparseable data {data_txt!r} ({p['name']!r})")
        return None

    if plan["gb"] < 0 or plan["days"] <= 0:
        problems.append(f"{where}: sanity fail {plan}")
        return None
    return plan


def fmt_gb(g: float) -> str:
    return f"{g:g} GB"


def main() -> None:
    provider = sys.argv[1]
    dry = "--dry-run" in sys.argv
    rawdir = RAW / provider
    files = sorted(rawdir.glob("*.json"))
    if not files:
        print(f"no raw files in {rawdir}")
        sys.exit(1)

    countries = tomllib.loads((ROOT / "data" / "countries.toml").read_text(encoding="utf-8"))
    by_slug = {c["slug"]: (iso, c["name"]) for iso, c in countries.items()}

    problems: list[str] = []
    blocks: dict[str, list[dict]] = {}
    empty_countries: list[str] = []

    for f in files:
        raw = json.loads(f.read_text(encoding="utf-8"))
        slug = raw["slug"]
        if slug not in by_slug:
            problems.append(f"{f.name}: slug {slug} not in countries.toml")
            continue
        iso, cname = by_slug[slug]
        if raw.get("status") == 404 or not raw.get("plans"):
            empty_countries.append(f"{iso} ({cname})")
            continue
        plans = []
        fup_default = (raw.get("fup") or "").strip()  # holafly PDP: page-level FUP wording
        for p in raw["plans"]:
            parsed = parse_plan(p, problems, f"{iso}/{p['name']}")
            if parsed:
                if parsed["type"] == "unlimited" and not parsed.get("fup_note") and fup_default:
                    parsed["fup_note"] = fup_default
                plans.append(parsed)
        # generic plan names (e.g. esimdb lists yesim rows as the country name)
        # -> rebuild "{data} / {validity}" so tables stay readable
        for pl in plans:
            if pl["name"].strip().lower() in (cname.lower(), provider.lower(), "", "plan", "data plan"):
                dur = f"{pl['days']} Day" if pl["days"] == 1 else f"{pl['days']} Days"
                if pl["type"] == "unlimited":
                    pl["name"] = f"Unlimited / {dur}"
                else:
                    gb = pl["gb"]
                    gb_s = f"{gb:g}GB" if gb >= 1 else f"{int(gb * 1024)}MB"
                    pl["name"] = f"{gb_s} / {dur}"
        if plans:
            blocks[iso] = plans

    print(f"{provider}: {len(blocks)} countries with plans, "
          f"{len(empty_countries)} without ({', '.join(empty_countries) or '-'})")
    if normalized:
        print(f"{len(normalized)} plan name(s) normalised (non-Latin script / leading junk):")
        for n in normalized[:40]:
            print("  " + n)
    if problems:
        print(f"{len(problems)} problems:")
        for pr in problems[:40]:
            print("  " + pr)

    if dry:
        return

    if provider == "holafly":
        src = "holafly.com official PDP (esim.holafly.com/esim-{country}/, USD price table)"
    else:
        src = f"esimdb.com/{provider} (Single-country plans, USD list prices)"
    lines = [
        f"# Scraped from {src} on {CHECKED}.",
        "# Raw capture: scripts/scrape/raw/ (per-country JSON incl. badges & page meta).",
        "# networks: not exposed on plan cards - left empty until verified per brand page.",
        "",
    ]
    iso_name = {iso: name for _, (iso, name) in by_slug.items()}
    for iso in sorted(blocks, key=lambda k: iso_name.get(k, k)):
        lines.append(f"[{iso}]")
        lines.append(f'checked = "{CHECKED}"')
        lines.append("networks = []")
        lines.append("")
        for plan in blocks[iso]:
            lines.append("[[%s.plans]]" % iso)
            lines.append(f"name = {toml_str(plan['name'])}")
            gb = plan["gb"]
            lines.append("gb = %s" % (int(gb) if gb == int(gb) else gb))
            lines.append(f"days = {plan['days']}")
            lines.append(f'type = "{plan["type"]}"')
            # always float form: TOML `price = 4` parses as int64 and breaks
            # Hugo printf "%.2f" (%!f(int64=4)) in every consumer template
            lines.append("price = %.2f" % plan["price"])
            if plan.get("fup_note"):
                lines.append(f"fup_note = {toml_str(plan['fup_note'])}")
            lines.append("")

    out = ROOT / "data" / "plans" / f"{provider}.toml"
    out.write_text("\n".join(lines), encoding="utf-8", newline="\n")
    print(f"wrote {out} ({len(blocks)} countries, "
          f"{sum(len(v) for v in blocks.values())} plans)")


if __name__ == "__main__":
    main()
