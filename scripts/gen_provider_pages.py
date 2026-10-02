#!/usr/bin/env python3
"""Regenerate brand×country sub-pages (content/en/compare/<slug>/<provider>.md)
from CURRENT data (single source of truth). Also removes sub-pages of providers
that no longer exist in providers.toml.

Unlike gen_sample_data.py this NEVER touches data/plans/*.toml - safe to run
after real scraped data lands. Run after every plans/provider set change.

Usage: python -X utf8 scripts/gen_provider_pages.py
"""
import shutil
import sys
import tomllib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
CONTENT = ROOT / "content" / "en" / "compare"

countries = tomllib.loads((DATA / "countries.toml").read_text(encoding="utf-8"))
providers = tomllib.loads((DATA / "providers.toml").read_text(encoding="utf-8"))
plans = {f.stem: tomllib.loads(f.read_text(encoding="utf-8"))
         for f in sorted((DATA / "plans").glob("*.toml"))}

unknown = [p for p in plans if p not in providers]
if unknown:
    sys.exit(f"ERROR: plans file without provider entry: {unknown} "
             f"(fix providers.toml or delete the plans file first)")

# 1. drop stale sub-pages (provider left the set, or country left countries.toml)
removed = 0
for d in CONTENT.iterdir():
    if not d.is_dir():
        continue
    for f in d.glob("*.md"):
        if f.stem not in providers:
            f.unlink()
            removed += 1
    if not any(d.glob("*.md")):
        shutil.rmtree(d)

# 2. rebuild every sub-page from current plan data
written = 0
rank_cache: dict[str, tuple[list[str], int]] = {}
for iso, c in countries.items():
    slug, name = c["slug"], c["name"]
    # rank per country: best $/GB across providers (unlimited-only sorts last)
    best = {}
    for pk, pdata in plans.items():
        block = pdata.get(iso)
        if not block or not block.get("plans"):
            continue
        pgb = [pl["price"] / pl["gb"] for pl in block["plans"] if pl["gb"] > 0]
        best[pk] = min(pgb) if pgb else float("inf")
    ranked = sorted(best, key=lambda k: best[k])
    n_all = sum(len(pdata[iso]["plans"]) for pk, pdata in plans.items()
                if iso in pdata and pdata[iso].get("plans"))

    for pk in sorted(plans):
        block = plans[pk].get(iso)
        if not block or not block.get("plans"):
            continue
        my = block["plans"]
        pname = providers[pk]["name"]
        from_price = min(pl["price"] for pl in my)
        metered = [pl for pl in my if pl["gb"] > 0]
        unl = [pl for pl in my if pl["gb"] == 0]
        rank = ranked.index(pk) + 1
        if metered:
            bpgb = min(pl["price"] / pl["gb"] for pl in metered)
            core = (f"eSIM Sift compares {pname} eSIM plans for {name}: {len(my)} plans from "
                    f"${from_price:.2f}, best ${bpgb:.2f}/GB (#{rank} of {len(best)})")
            tails = [
                f" — benchmarked against all {n_all} {name} eSIMs we track.",
                f" — ranked against {n_all} {name} plans.",
                " — from our live price index.",
                " — live prices.",
            ]
        else:
            bday = min(pl["price"] / pl["days"] for pl in unl)
            core = (f"eSIM Sift compares {pname} unlimited eSIMs for {name}: {len(my)} daily "
                    f"plans from ${bday:.2f}/day, fair-use caps decoded")
            tails = [
                f" — benchmarked against all {n_all} {name} eSIMs we track.",
                f" — {n_all} {name} eSIMs tracked.",
                " — from our live price index.",
                " — live prices.",
            ]
        desc = next((c for t in tails if 120 <= len(c := core + t) <= 140), None)
        if desc is None:
            sys.exit(f"ERROR: desc out of 120-140 range for {pk}/{iso}: "
                     f"core={len(core)}, tails={[len(core + t) for t in tails]}")
        d = CONTENT / slug
        d.mkdir(parents=True, exist_ok=True)
        md = ["---",
              f'title: "{pname} {name} eSIM Plans & Prices"',
              f"iso: {iso}",
              f"provider: {pk}",
              "layout: provider",
              "seo:",
              f'  description: "{desc}"',
              "---", ""]
        (d / f"{pk}.md").write_text("\n".join(md), encoding="utf-8")
        written += 1

print(f"OK: {written} provider×country sub-pages written, {removed} stale removed.")
