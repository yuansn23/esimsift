# -*- coding: utf-8 -*-
"""One-shot meta title/description normalization (2026-10-01 SEO compliance pass).

A. Country pages (50): regenerate seo.description from LIVE plan data
   (old ones were stale — wrong plan counts, some mentioned retired Nomad).
B. VS pages (28): shorten title to fit <=60 chars incl " | eSIM Sift" suffix.
C. Handwritten pages: explicit title/description map (promo-code facts fixed
   to the real verified codes: roami web20 / saily VEEPEE25 / ubigi WELCOME10).

Usage: python -X utf8 scripts/regen_meta_fixes.py [--dry-run]
"""
import re
import sys
import tomllib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
CONTENT = ROOT / "content" / "en"
DRY = "--dry-run" in sys.argv

countries = tomllib.loads((DATA / "countries.toml").read_text(encoding="utf-8"))
providers = tomllib.loads((DATA / "providers.toml").read_text(encoding="utf-8"))
plans = {f.stem: tomllib.loads(f.read_text(encoding="utf-8"))
         for f in sorted((DATA / "plans").glob("*.toml"))}

problems = []
changed = 0


def rewrite(path: Path, subs: list[tuple[str, str]], label: str) -> None:
    """Apply regex subs to the file's front matter only (first --- block)."""
    global changed
    text = path.read_text(encoding="utf-8")
    fm_end = text.index("\n---", 4)
    head, body = text[:fm_end], text[fm_end:]
    new_head = head
    for pat, rep in subs:
        new_head = re.sub(pat, rep, new_head, count=1, flags=re.M)
    if new_head != head:
        if not DRY:
            path.write_text(new_head + body, encoding="utf-8")
        changed += 1
        print(f"  [x] {label}")
    else:
        problems.append(f"NO MATCH: {label} ({path.name})")


# ── A. Country descriptions: live numbers, 120-158 chars ──
print("A. country page descriptions (computed):")
for iso, c in countries.items():
    prov_min: dict[str, float] = {}
    total = 0
    for pk, pdata in plans.items():
        block = pdata.get(iso)
        if not block or not block.get("plans"):
            continue
        total += len(block["plans"])
        prov_min[pk] = min(p["price"] for p in block["plans"])
    cheapest = min(prov_min, key=prov_min.get)
    core = (f"Every {c['name']} eSIM compared: {total} real plans from {len(prov_min)} "
            f"providers, cheapest {providers[cheapest]['name']} from ${prov_min[cheapest]:.2f}")
    tail_a = ". Ranked by $/GB with fair-use caps decoded."
    tail_b = ". Ranked by $/GB and $/day."
    desc = core + (tail_a if len(core) + len(tail_a) <= 158 else tail_b)
    if not 120 <= len(desc) <= 158:
        problems.append(f"desc len {len(desc)} out of range: {iso}: {desc}")
        continue
    f = CONTENT / "compare" / f"{c['slug']}.md"
    rewrite(f, [(r'(seo:\n  description: ")[^"]*(")', lambda m: m.group(1) + desc + m.group(2))],
            f"{iso} ({len(desc)} ch)")

# ── B. VS titles: shorten families, <=48 content chars (60 incl suffix) ──
print("B. vs page titles:")
for f in sorted((CONTENT / "compare").glob("*-vs-*.md")):
    text = f.read_text(encoding="utf-8")
    m = re.search(r'^title: "(.*)"$', text, re.M)
    old = m.group(1)
    new = old
    if " eSIM Compared: Prices & Verdict 2026" in old:
        new = old.replace(" eSIM Compared: Prices & Verdict 2026", " eSIM: Prices and Verdict 2026")
    elif " eSIM? Price Comparison & Verdict (2026)" in old:
        new = old.replace(" eSIM? Price Comparison & Verdict (2026)", " eSIM? 2026 Price Comparison")
    elif " eSIM: Which Is Cheaper in 2026?" in old:
        new = old.replace(" eSIM: Which Is Cheaper in 2026?", " eSIM: Which Is Cheaper?")
    elif " eSIM: Two Different Brands, Compared (2026)" in old:
        new = old.replace(" eSIM: Two Different Brands, Compared (2026)", ": Two Different eSIM Brands")
    elif len(old) <= 48:
        new = old  # already compliant, leave
    else:
        problems.append(f"VS title unmatched family: {f.name}: {old}")
        continue
    if len(new) > 48:
        problems.append(f"VS title still {len(new)} >48: {f.name}: {new}")
        continue
    if new != old:
        rewrite(f, [(re.escape(f'title: "{old}"'), f'title: "{new}"')], f"{f.stem} -> {new}")

# ── C. Handwritten pages map ──
FIXES: dict[str, dict[str, str]] = {
    "esim-providers/airalo.md": {
        "title": "Airalo eSIM Review 2026: Prices, App and Verdict",
        "description": "Airalo eSIM review: countries covered, cheapest plans per destination, the app install flow, and where Airalo still wins on value.",
    },
    "esim-providers/alosim.md": {
        "title": "aloSIM eSIM Review 2026: Prices and Verdict",
    },
    "esim-providers/holafly.md": {
        "title": "Holafly eSIM Review: Is Unlimited Data Worth It?",
        "description": "Holafly eSIM review: unlimited-data pricing versus fair-use caps, which countries cost most, and when Holafly is worth the daily rate.",
    },
    "esim-providers/roami.md": {
        "title": "Roami eSIM Review 2026: Prices and Verdict",
        "description": "Independent Roami eSIM review: coverage, entry prices per country, the web20 new-user code, and where Roami is actually the cheapest.",
    },
    "esim-providers/roamic.md": {
        "title": "Roamic eSIM Review 2026: Prices and Verdict",
    },
    "esim-providers/saily.md": {
        "title": "Saily eSIM Review 2026: Prices and Verdict",
        "description": "Saily eSIM review: the NordVPN team's app, coverage and entry prices, the VEEPEE25 code, and the countries where Saily is cheapest.",
    },
    "esim-providers/ubigi.md": {
        "title": "Ubigi eSIM Review 2026: Prices and Verdict",
        "description": "Ubigi eSIM review: Transatel (an NTT company) since 2017, plan prices per country, car and laptop data, the WELCOME10 code and where it wins.",
    },
    "esim-providers/yesim.md": {
        "title": "Yesim eSIM Review 2026: Prices and Verdict",
    },
    "guides/dual-sim-and-esim.md": {
        "title": "Dual SIM With eSIM: Keep Your Home Number",
        "description": "How dual SIM works with one eSIM and one physical SIM: keep your home number for calls and SMS while the eSIM carries data abroad.",
    },
    "guides/esim-compatibility-check.md": {
        "title": "Is Your Phone eSIM Compatible? 30-Second Check",
        "description": "Check eSIM compatibility in 30 seconds: the *#06# EID test, every supported iPhone and Android, carrier lock, and a searchable phone list.",
    },
    "guides/esim-vs-physical-sim.md": {
        "title": "eSIM vs Physical SIM: Which Wins Abroad?",
    },
    "guides/how-to-install-esim.md": {
        "title": "How to Install an eSIM on iPhone and Android",
        "description": "How to install an eSIM in five minutes: activation timing, QR and app installs, which providers need their app, and the errors to avoid.",
    },
    "guides/what-is-an-esim.md": {
        "description": "What is an eSIM? A plain-English explainer: how a built-in SIM works, what gets installed, and what it means for calls and SMS abroad.",
    },
    "compare/matchups.md": {
        "title": "All 28 eSIM Provider Matchups Compared",
        "description": "Every eSIM provider matchup in one index — Airalo vs Holafly, Roami vs Roamic and every other pair, each verdict computed country by country.",
    },
    "research/esim-price-index.md": {
        "title": "eSIM Price Index 2026: 50 Countries Ranked",
    },
    "research/fair-use-audit.md": {
        "title": "eSIM Fair Use Audit 2026: What Unlimited Means",
    },
    "research/unlimited-esim.md": {
        "title": "Best Unlimited eSIM 2026: Daily Rates Compared",
    },
    "research/_index.md": {
        "description": "Original research from our price database — price-per-GB league tables, fair-use audits, and unlimited-data market analysis.",
    },
    "about.md": {
        "description": "Who we are, why we built an independent eSIM price database covering 8 providers and 50 countries, and how the site makes money.",
    },
    "contact.md": {
        "description": "Report a price change, suggest a provider to track, or reach the eSIM Sift team — verified fixes ship with the next site build.",
    },
    "disclosure.md": {
        "description": "How eSIM Sift earns money from referral commissions, and the disclosure rules we hold ourselves to across every page we publish.",
    },
    "privacy.md": {
        "description": "How eSIM Sift handles personal data, cookies and analytics — what we collect, what we never collect, and the choices you have.",
    },
    "terms.md": {
        "description": "The terms of service for using eSIM Sift, including our price-data disclaimer and the limits of our editorial liability.",
    },
    "tools/_index.md": {
        "description": "Estimate how much travel data you need app by app, then get the cheapest matching eSIM plan — computed live from 8 providers across 50 countries.",
    },
}

print("C. handwritten pages:")
for rel, fields in FIXES.items():
    f = CONTENT / rel
    if "title" in fields and '"' in fields["title"]:
        problems.append(f"bad title quotes: {rel}")
        continue
    for k, v in fields.items():
        if k == "title" and len(v) > 48:
            problems.append(f"title {len(v)} >48: {rel}")
        if k == "description" and not 120 <= len(v) <= 158:
            problems.append(f"desc {len(v)} out of range: {rel}")
    rewrite(f, [(rf'^(title: ")[^"]*(")$', lambda m, _v=fields.get("title"): m.group(1) + _v + m.group(2) if _v else m.group(0)),
                (rf'^(description: ")[^"]*(")$', lambda m, _v=fields.get("description"): m.group(1) + _v + m.group(2) if _v else m.group(0))],
            rel)

print(f"\n{'(dry-run) ' if DRY else ''}changed files: {changed}")
if problems:
    print("PROBLEMS:")
    for p in problems:
        print("  !", p)
    sys.exit(1)
print("OK: no problems")
