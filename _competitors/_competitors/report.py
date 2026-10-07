# -*- coding: utf-8 -*-
"""Emit _competitors/COVERAGE.md : per-brand x per-country coverage matrix."""
import json
import tomllib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "_competitors"
CAPTURED = "2026-10-04"

ct = tomllib.loads((ROOT / "data" / "countries.toml").read_text(encoding="utf-8"))
order = [iso for iso, c in ct.items() if isinstance(c, dict) and c.get("slug")]
name = {iso: ct[iso]["name"] for iso in order}

BRANDS = ["nomad", "jetpac", "gigsky", "quibity", "roamless", "gomoworld",
          "maya", "bnesim", "firsty"]
tables = {}
for b in BRANDS:
    f = BASE / "plans" / f"{b}.toml"
    tables[b] = tomllib.loads(f.read_text(encoding="utf-8")) if f.exists() else {}

# brand metadata for the sources table (kind/source read from coverage.json)
cov = json.loads((BASE / "coverage.json").read_text(encoding="utf-8")) \
    if (BASE / "coverage.json").exists() else {}
OFFICIAL = {
    "nomad": ("nomadesim.com", "No — proxied network blocks it (timeout)"),
    "jetpac": ("jetpacglobal.com", "Only `japan-esim` is a real product page (24 offers)"),
    "gigsky": ("gigsky.com", "Rendered docs only, no per-country plan table in HTML"),
    "quibity": ("quibity.com", "SPA, no embedded plan payload"),
    "roamless": ("roamless.com", "Not attempted — esimdb already has the full matrix"),
    "gomoworld": ("gomoworld.com", "Not attempted — esimdb already has the full matrix"),
    "maya": ("maya.net", "**Yes — Angular SSR embeds structured `plans[]` JSON**"),
    "bnesim": ("bnesim.com", "**Yes — public pricing API `sim_card_landing_pricing`**"),
    "firsty": ("firsty.app", "Yes, but only the global model (no per-country pricing)"),
}

lines = [
    "# Competitor capture coverage",
    "",
    f"- Captured: **{CAPTURED}**",
    "- Countries tracked: **{}**".format(len(order)),
    "- Brands: " + ", ".join(BRANDS),
    "",
    "Plan counts below are post-normalisation (priced plans only, cosmetic duplicates merged).",
    "",
    "## Per-country plan count",
    "",
    "| ISO | Country | " + " | ".join(b.capitalize() for b in BRANDS) + " |",
    "|---|---|" + "---|" * len(BRANDS),
]

totals = {b: 0 for b in BRANDS}
gaps = {b: [] for b in BRANDS}
for iso in order:
    cells = []
    for b in BRANDS:
        d = tables[b].get(iso)
        n = len(d.get("plans", [])) if d else 0
        totals[b] += n
        if n == 0:
            gaps[b].append(iso)
            cells.append("**—**")
        else:
            cells.append(str(n))
    lines.append(f"| {iso} | {name[iso]} | " + " | ".join(cells) + " |")

# fold globally-priced brands into their totals (their rows live under [GLOBAL])
global_counts = {}
for b in BRANDS:
    g = tables[b].get("GLOBAL")
    if g:
        gn = len(g.get("plans", []))
        global_counts[b] = gn
        totals[b] += gn

lines += [
    "| — | **Total (tracked countries)** | " + " | ".join(f"**{totals[b]}**" for b in BRANDS) + " |",
]

# brands that price globally rather than per country
for b in BRANDS:
    g = tables[b].get("GLOBAL")
    if g:
        gn = len(g.get("plans", []))
        cells = [str(gn) if bb == b else "—" for bb in BRANDS]
        lines.append(f"| GLOBAL | Global price list (not per-country) | " + " | ".join(cells) + " |")

lines += [
    "",
    "## Gaps",
]
for b in BRANDS:
    lines.append(f"- **{b}**: " + (", ".join(f"{i} ({name[i]})" for i in gaps[b]) if gaps[b] else "none — 50/50 covered"))

lines += [
    "",
    "## Sources & method",
    "",
    "| Brand | Official site | Official usable? | Primary source used | Plans |",
    "|---|---|---|---|---|",
]
for b in BRANDS:
    site, usable = OFFICIAL.get(b, ("?", "?"))
    src = cov.get(b, {}).get("source", "?")
    lines.append(f"| {b.capitalize()} | {site} | {usable} | {src} | {totals[b]} |")

lines += [
    "",
    "### Per-brand caveats",
    "",
    "- **Jetpac / Fiji** — 404 on esimdb and no official Fiji product page: 49/50 is the true ceiling.",
    "- **BNESIM** — prices are **EUR** (API currency, all locales); `duration = -1` in the API is",
    "  recorded as `days = 0` (no fixed validity stated). Hong Kong / Macao carry only regional",
    "  bundles, hence 48/50 single-country coverage. Carriers are exposed per product (like Maya).",
    "- **Firsty** — one **global** price list, identical in every country (no per-country pricing);",
    "  only the model, floor prices and a few stated price points are public (6 rows). Full per-GB",
    "  ladder is app-only. Two conflicting 10 GB figures appear in site copy and are both kept.",
    "- **Roamless** — includes 'Pay-As-You-Go / No Expiry' products (`days = 0`) and a free tier",
    "  (dropped by the price>0 rule). Discount badges (e.g. 20% OFF) are not applied to prices.",
    "- **GoMoWorld** — fixed GB/day bundles; `€2 OFF` badges are not applied to prices.",
    "",
    "### Notes on the Maya capture",
    "",
    "Maya sells a single **global unlimited** product, so the same plan ladder appears on every",
    "country page (`3/7/14/30 days`, USD 9.99 / 19.99 / 27.99 / 49.99) plus a Global + Cruise tier.",
    "The `networks` array in `plans/maya.toml` is Maya's *real per-country carrier* (e.g. JP ->",
    "`Rakuten Mobile Inc. (5G)`), taken from the ISO3 carrier map embedded in the same payload.",
    "",
    "### Trustpilot",
    "",
    "Not scraped on purpose (the user supplies it). Each `brand/<brand>.json` carries a",
    "`trustpilot` object with the review URL and null fields ready to fill:",
    "`rating`, `review_count`, `trust_score`, `five_star_pct`, `verified_reviews`,",
    "`last_checked`, `recent_reviews[]`.",
    "",
]
(BASE / "COVERAGE.md").write_text("\n".join(lines), encoding="utf-8")
print("wrote COVERAGE.md")
print(json.dumps(totals, indent=1))
