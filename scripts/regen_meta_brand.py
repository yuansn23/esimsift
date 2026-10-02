# -*- coding: utf-8 -*-
"""Meta brand pass (2026-10-02, user spec v3).

Rules enforced everywhere after this run:
  - title: 48-54 chars, NO brand word (except homepage), eSIM core keyword present
  - description: 120-140 chars, MUST contain brand "eSIM Sift"

Sections:
  A. Country pages (50): seo.description rebuilt from live plan data, brand-led.
  B. VS pages (28): titles rebuilt to 48-54 from providers data (family preserved);
     descriptions rebuilt brand-led, 3 rotated families (anti-homogenization).
  C. Handwritten pages: explicit title/description map (varied lead-ins on purpose).

Usage: python -X utf8 scripts/regen_meta_brand.py [--dry-run]
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
    """Apply regex subs to front matter only; a (pat, None) entry means 'insert if missing'."""
    global changed
    text = path.read_text(encoding="utf-8")
    fm_end = text.index("\n---", 4)
    head, body = text[:fm_end], text[fm_end:]
    new_head = head
    for pat, rep in subs:
        if rep is None:  # already applied by a paired sub; skip
            continue
        new2 = re.sub(pat, rep, new_head, count=1, flags=re.M)
        if new2 == new_head and not re.search(pat, new_head):
            problems.append(f"NO MATCH: {label} / pattern {pat[:40]}...")
            continue
        new_head = new2
    if new_head != head:
        if not DRY:
            path.write_text(new_head + body, encoding="utf-8")
        changed += 1
        print(f"  [x] {label}")


def set_kv(path: Path, kv: dict[str, str], label: str) -> None:
    """Set top-level front-matter string keys, inserting missing ones before '---'."""
    global changed
    text = path.read_text(encoding="utf-8")
    fm_end = text.index("\n---", 4)
    head, body = text[:fm_end], text[fm_end:]
    new_head = head
    for k, v in kv.items():
        pat = re.compile(rf'^({re.escape(k)}: ")[^"]*(")$', re.M)
        if pat.search(new_head):
            new_head = pat.sub(lambda m: m.group(1) + v + m.group(2), new_head, count=1)
        else:
            new_head = new_head + f'\n{k}: "{v}"'
    if new_head != head:
        if not DRY:
            path.write_text(new_head + body, encoding="utf-8")
        changed += 1
        print(f"  [x] {label}")


def fit(cands: list[str], lo: int, hi: int, label: str) -> str:
    for c in cands:
        if lo <= len(c) <= hi:
            return c
    problems.append(f"NO FIT {lo}-{hi} {label}: " + ", ".join(f"{len(c)}:{c}" for c in cands))
    return cands[-1]


# ── A. Country descriptions: brand-led, 120-140 ──
print("A. country page descriptions (brand-led, computed):")
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
    cname = providers[cheapest]["name"]
    core = (f"eSIM Sift compares every {c['name']} eSIM: {total} real plans from "
            f"{len(prov_min)} providers, cheapest {cname} from ${prov_min[cheapest]:.2f}")
    cands = [
        core + ", ranked by $/GB with fair-use caps decoded.",
        core + ", ranked by $/GB and $/day.",
        core + ", ranked by $/GB.",
        core + ".",
    ]
    desc = fit(cands, 120, 140, f"country desc {iso}")
    if desc not in cands:
        continue
    f = CONTENT / "compare" / f"{c['slug']}.md"
    rewrite(f, [(r'(seo:\n  description: ")[^"]*(")', lambda m, _d=desc: m.group(1) + _d + m.group(2))],
            f"{iso} desc ({len(desc)} ch)")

# ── B. VS pages: titles 48-54 (family kept) + brand-led descs, 3 rotated families ──
print("B. vs pages (titles + descriptions):")
VS_TITLES = {
    "F1": lambda a, b: [
        f"{a} vs {b} eSIM Compared: Prices and Verdict 2026",
        f"{a} vs {b} eSIM: Prices, Data and Verdict 2026",
        f"{a} vs {b} eSIM: Prices and Verdict 2026",
    ],
    "F2": lambda a, b: [
        f"{a} or {b} eSIM? 2026 Price and Data Comparison",
        f"{a} or {b} eSIM? Full 2026 Price Comparison",
        f"{a} or {b} eSIM? 2026 Price Comparison",
    ],
}
VS_SPECIAL = {
    "roami-vs-roamic": "Roami vs Roamic: Two Different eSIM Brands Compared",
}
VS_DESCS = lambda a, b, i: [
    # family rotation = anti-homogenization (same idea as anchor rotation)
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
][i % 3]

for i, f in enumerate(sorted((CONTENT / "compare").glob("*-vs-*.md"))):
    text = f.read_text(encoding="utf-8")
    old_title = re.search(r'^title: "(.*)"$', text, re.M).group(1)
    keys = re.search(r'^providers: \[(.*?)\]$', text, re.M)
    if not keys:
        problems.append(f"no providers list: {f.name}")
        continue
    pk_a, pk_b = [k.strip().strip('"') for k in keys.group(1).split(",")]
    a, b = providers[pk_a]["name"], providers[pk_b]["name"]
    stem = f.stem
    if stem in VS_SPECIAL:
        new_title = VS_SPECIAL[stem]
    elif "Verdict 2026" in old_title:
        new_title = fit(VS_TITLES["F1"](a, b), 48, 54, f"{stem} title")
    elif "2026 Price Comparison" in old_title or "Price and Data Comparison" in old_title:
        new_title = fit(VS_TITLES["F2"](a, b), 48, 54, f"{stem} title")
    elif "Is Cheaper" in old_title:
        new_title = fit([
            f"{a} vs {b} eSIM: Which One Is Cheaper in 2026?",
            f"{a} vs {b} eSIM: Which Is Cheaper in 2026?",
        ], 48, 54, f"{stem} title")
    else:
        problems.append(f"VS title unmatched family: {f.name}: {old_title}")
        continue
    desc = fit(VS_DESCS(a, b, i), 120, 140, f"{stem} desc")
    set_kv(f, {"title": new_title, "description": desc},
           f"{stem} ({len(new_title)}t/{len(desc)}d)")

# ── C. Handwritten pages: varied lead-ins on purpose (anti-homogenization) ──
MAP: dict[str, dict[str, str]] = {
    # providers
    "esim-providers/_index.md": {
        "title": "Every eSIM Provider Compared: 2026 Prices and Reviews",
        "description": "eSIM Sift profiles every major travel eSIM provider: coverage, pricing philosophy, strengths, weaknesses, and where each one actually wins.",
    },
    "esim-providers/airalo.md": {
        "title": "Airalo eSIM Review 2026: Prices, Coverage and Verdict",
        "description": "eSIM Sift review of Airalo: countries covered, cheapest plans per destination, the app install flow, and where Airalo still wins.",
    },
    "esim-providers/alosim.md": {
        "title": "aloSIM eSIM Review 2026: Prices, Coverage and Verdict",
        "description": "How good is aloSIM? eSIM Sift checks AffinityClick's country packs, plan prices per destination, and where aloSIM is cheapest.",
    },
    "esim-providers/holafly.md": {
        "title": "Holafly eSIM Review: Is Unlimited Data Worth It?",
        "description": "Is Holafly's unlimited data worth it? eSIM Sift checks daily-rate pricing against fair-use caps, country by country, before you buy.",
    },
    "esim-providers/roami.md": {
        "title": "Roami eSIM Review 2026: Prices, Coverage and Verdict",
        "description": "Roami review by eSIM Sift: coverage, entry prices per country, the web20 new-user code, and where Roami is actually the cheapest.",
    },
    "esim-providers/roamic.md": {
        "title": "Roamic eSIM Review 2026: Prices, Coverage and Verdict",
        "description": "Roamic is Byte Travel's brand — eSIM Sift reviews its unlimited options, plan prices per country, and where Roamic is cheapest.",
    },
    "esim-providers/saily.md": {
        "title": "Saily eSIM Review 2026: Prices, Coverage and Verdict",
        "description": "Saily is the NordVPN team's eSIM — eSIM Sift checks coverage, entry prices, the VEEPEE25 code, and where Saily is actually cheapest.",
    },
    "esim-providers/ubigi.md": {
        "title": "Ubigi eSIM Review 2026: Prices, Coverage and Verdict",
        "description": "Ubigi from Transatel (an NTT company): eSIM Sift reviews plan prices per country, car and laptop data, and the WELCOME10 code.",
    },
    "esim-providers/yesim.md": {
        "title": "Yesim eSIM Review 2026: Prices, Coverage and Verdict",
        "description": "Yesim, the Swiss pay-as-you-go eSIM: eSIM Sift reviews plan prices per country and where Yesim is actually the cheapest pick.",
    },
    # guides
    "guides/_index.md": {
        "title": "eSIM Guides: How to Pick, Install and Use Travel eSIMs",
        "description": "Practical travel eSIM guides from eSIM Sift — choosing plans, installing profiles, and troubleshooting, written for travelers first.",
    },
    "guides/what-is-an-esim.md": {
        "title": "What Is an eSIM? How It Works, in Plain English (2026)",
        "description": "What is an eSIM? eSIM Sift explains how a built-in SIM works, what actually gets installed, and what it means for calls and SMS abroad.",
    },
    "guides/esim-vs-physical-sim.md": {
        "title": "eSIM vs Physical SIM: Which Wins for Travel in 2026?",
        "description": "eSIM or physical SIM for travel? eSIM Sift compares price, setup time, number keeping and security — including where a local SIM still wins.",
    },
    "guides/how-to-install-esim.md": {
        "title": "How to Install a Travel eSIM on iPhone and Android",
        "description": "How to install an eSIM in five minutes: eSIM Sift covers activation timing, QR and app installs, and the errors to avoid before you fly.",
    },
    "guides/esim-compatibility-check.md": {
        "title": "Is Your Phone eSIM Compatible? The 30-Second Check",
        "description": "Check eSIM compatibility in 30 seconds: the *#06# EID test, supported iPhones and Androids, and eSIM Sift's searchable phone list.",
    },
    "guides/dual-sim-and-esim.md": {
        "title": "Dual SIM With eSIM: Keep Your Home Number Abroad",
        "description": "How dual SIM works with one eSIM plus one physical SIM: eSIM Sift explains keeping your home number while the eSIM carries data.",
    },
    # research
    "research/_index.md": {
        "title": "eSIM Research: Price Index, Fair Use and Data Trends",
        "description": "Original research from the eSIM Sift price database — price-per-GB league tables, fair-use audits, and unlimited-data analysis.",
    },
    "research/esim-price-index.md": {
        "title": "eSIM Price Index 2026: 50 Countries by Data Cost",
        "description": "eSIM prices by country, ranked by best $/GB across all 50 destinations in the eSIM Sift database — regional averages and league table.",
    },
    "research/fair-use-audit.md": {
        "title": "eSIM Fair Use Audit 2026: What Unlimited Really Means",
        "description": "What unlimited eSIM plans really throttle: eSIM Sift audits the fair-use policies of all 8 providers, plan by plan, quoted verbatim.",
    },
    "research/unlimited-esim.md": {
        "title": "Best Unlimited eSIM Plans 2026: Daily Rates Compared",
        "description": "Best unlimited eSIM plans compared: eSIM Sift ranks daily rates for every country with unlimited data, plus the fair-use catches.",
    },
    # hubs / tools / deals / static
    "compare/_index.md": {
        "title": "Compare eSIM Plans by Country: Best Prices and $/GB",
        "description": "Every prepaid travel eSIM plan in one eSIM Sift index — filter by country, sort by price per GB, and compare all 8 providers.",
    },
    "methodology.md": {
        "title": "Our Methodology: How We Collect and Verify eSIM Prices",
    },
    "compare/matchups.md": {
        "title": "All 28 eSIM Provider Matchups Compared on Real Prices",
        "description": "Every eSIM provider matchup in one eSIM Sift index — Airalo vs Holafly, Roami vs Roamic and every other pair, computed country by country.",
    },
    "tools/_index.md": {
        "title": "eSIM Tools: Trip Cost Calculator and Data Estimator",
        "description": "Estimate how much travel data you need app by app, then get the cheapest matching eSIM — eSIM Sift computes it live from 8 providers.",
    },
    "esim-deals/_index.md": {
        "title": "eSIM Deals 2026: Verified Promo Codes and Real Savings",
        "description": "Verified eSIM promo codes with expiry and terms — eSIM Sift computes what each code saves on a real plan, and when no-code still wins.",
    },
    "about.md": {
        "title": "About Us: Why We Built an Independent eSIM Database",
        "description": "Who we are, why eSIM Sift tracks an independent price database of 8 providers and 50 countries, and how the site makes money.",
    },
    "contact.md": {
        "title": "Contact Us: Price Corrections and Provider Requests",
        "description": "Report a price change, suggest a provider to track, or reach the eSIM Sift team — verified fixes ship with the next site build.",
    },
    "disclosure.md": {
        "title": "Affiliate Disclosure: Commissions and Editorial Rules",
        "description": "How eSIM Sift earns referral commissions from eSIM providers, and the disclosure rules we hold ourselves to across every page we publish.",
    },
    "privacy.md": {
        "title": "Privacy Policy: Data, Cookies and Analytics Explained",
        "description": "How eSIM Sift handles personal data, cookies and analytics — what we collect, what we never collect, and the choices you have.",
    },
    "terms.md": {
        "title": "Terms of Service: Price Data Accuracy and Liability",
        "description": "The terms of service for using eSIM Sift, including our price-data disclaimer and the limits of our editorial liability.",
    },
}

print("C. handwritten pages:")
# 法务/联系页不参与关键词竞争，只受长度+无品牌约束（eSIM 关键词免检）
EKEY_EXEMPT = {"contact.md", "disclosure.md", "privacy.md", "terms.md"}
for rel, fields in MAP.items():
    f = CONTENT / rel
    t, d = fields["title"], fields.get("description", "")
    if not 48 <= len(t) <= 54:
        problems.append(f"title {len(t)} out of 48-54: {rel}: {t}")
    if d:
        if not 120 <= len(d) <= 140:
            problems.append(f"desc {len(d)} out of 120-140: {rel}")
        if "eSIM Sift" not in d:
            problems.append(f"desc missing brand: {rel}")
    if "eSIM Sift" in t:
        problems.append(f"title has brand (only home may): {rel}")
    if "eSIM" not in t and rel not in EKEY_EXEMPT:
        problems.append(f"title missing eSIM keyword: {rel}")
    set_kv(f, fields, f"{rel} ({len(t)}t/{len(d)}d)")

print(f"\n{'(dry-run) ' if DRY else ''}changed files: {changed}")
if problems:
    print("PROBLEMS:")
    for p in problems:
        print("  !", p)
    sys.exit(1)
print("OK: no problems")
