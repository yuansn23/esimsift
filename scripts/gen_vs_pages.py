#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Generate the missing A-vs-B matchup pages (content/en/compare/{a}-vs-{b}.md).

Why this exists: adding a brand grows the matchup set from C(8,2)=28 to C(9,2)=36.
The 28 originals were hand-written; regenerating them would churn pages that are
already indexed, so this script ONLY creates pairs that do not exist yet and never
rewrites an existing file.

Naming/format rules are the ones the live site already enforces:
  · filename == "{a}-vs-{b}.md" with a < b alphabetically (scripts/validate.py §7)
  · providers = ["a", "b"] in the same alphabetical order
  · layout: vs-single
  · title 48-54 chars (scripts/audit_meta.py) — candidates come from the same
    two families scripts/regen_meta_brand.py uses, so new pages read identically
    to the old ones; first candidate that fits is taken
  · description 120-140 chars and must contain "eSIM Sift"; the family rotates by
    index so the new pages do not all open with the same sentence
    (anti-homogenization — same idea as the anchor rotation in regen_meta_brand)

Usage:
  python -X utf8 scripts/gen_vs_pages.py [--dry-run]
"""
import sys
import tomllib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
COMPARE = ROOT / "content" / "en" / "compare"
DRY = "--dry-run" in sys.argv

TITLE_MIN, TITLE_MAX = 48, 54
DESC_MIN, DESC_MAX = 120, 140

providers = tomllib.loads((DATA / "providers.toml").read_text(encoding="utf-8"))
brands = {k: v for k, v in providers.items() if isinstance(v, dict) and v.get("name")}


def title_candidates(a: str, b: str) -> list[str]:
    """Same two families as the live pages, longest first."""
    return [
        f"{a} vs {b} eSIM Compared: Prices and Verdict 2026",
        f"{a} vs {b} eSIM: Prices, Data and Verdict 2026",
        f"{a} vs {b} eSIM: Prices and Verdict 2026",
        f"{a} or {b} eSIM? 2026 Price and Data Comparison",
        f"{a} or {b} eSIM? Full 2026 Price Comparison",
        f"{a} or {b} eSIM? 2026 Price Comparison",
        f"{a} vs {b} eSIM: Which Is Cheaper in 2026?",
        f"{a} vs {b} eSIM: 2026 Price and Data Comparison",
    ]


def desc_candidates(a: str, b: str, i: int) -> list[str]:
    """Three rotated families (anti-homogenization), long form first."""
    fams = [
        [
            f"eSIM Sift compares {a} and {b} eSIMs: entry prices, $/GB and unlimited data in every shared country — a computed verdict.",
            f"eSIM Sift compares {a} and {b} eSIMs: entry prices, $/GB and unlimited data in every shared country.",
        ],
        [
            f"{a} or {b} for your trip? eSIM Sift computes the verdict: cheapest plan per country, best $/GB, unlimited coverage — live prices.",
            f"{a} or {b} for your trip? eSIM Sift computes the verdict: cheapest plan per country, best $/GB, unlimited coverage.",
        ],
        [
            f"Which eSIM is cheaper, {a} or {b}? eSIM Sift compares entry prices, $/GB and fair-use caps in every shared country — prices change.",
            f"Which eSIM is cheaper, {a} or {b}? eSIM Sift compares entry prices, $/GB and fair-use caps in every shared country.",
        ],
    ]
    return fams[i % 3]


def fit(cands: list[str], lo: int, hi: int) -> str | None:
    return next((c for c in cands if lo <= len(c) <= hi), None)


keys = sorted(brands)
created, skipped, problems = [], [], []

for i, a in enumerate(keys):
    for b in keys[i + 1:]:
        f = COMPARE / f"{a}-vs-{b}.md"
        if f.exists():
            skipped.append(f.name)
            continue
        na, nb = brands[a]["name"], brands[b]["name"]
        title = fit(title_candidates(na, nb), TITLE_MIN, TITLE_MAX)
        desc = fit(desc_candidates(na, nb, i + len(created)), DESC_MIN, DESC_MAX)
        if not title or not desc:
            problems.append(
                f"{a}-vs-{b}: no candidate fits "
                f"(title cands={[len(c) for c in title_candidates(na, nb)]}, "
                f"desc cands={[len(c) for c in desc_candidates(na, nb, i)]})"
            )
            continue
        body = "\n".join([
            "---",
            f'title: "{title}"',
            f'description: "{desc}"',
            f'providers: ["{a}", "{b}"]',
            "layout: vs-single",
            "---",
            "",
        ])
        if not DRY:
            f.write_text(body, encoding="utf-8", newline="\n")
        created.append((f.name, len(title), len(desc)))

print(f"existing matchups untouched: {len(skipped)}")
print(f"{'[dry] would create' if DRY else 'created'}: {len(created)}")
for name, tl, dl in created:
    print(f"  {name:28s} title={tl} desc={dl}")
if problems:
    print(f"\n{len(problems)} problem(s):")
    for p in problems:
        print("  " + p)
    sys.exit(1)
