#!/usr/bin/env python3
"""esimsift data-layer validation.

Runs BEFORE `hugo` so bad TOML data never reaches a build.
Checks:
  1. countries.toml    required fields, neighbors refer to existing ISOs
  2. providers.toml    required fields, plan files <-> provider keys aligned
  3. data/plans/*.toml per-ISO blocks: checked/networks/plans, plan field
                       completeness, value sanity (price>0, days>0, gb>=0),
                       flag unverified SAMPLE data
  4. compare pages     iso <-> countries.toml bidirectional alignment
                       (matchup files {a}-vs-{b}.md are skipped here; see 7)
  5. data/faqs/*.toml  every compare page has FAQs (FAQPage schema), no orphans
  6. slug map          every covered ISO has a roami deep-link slug
  7. vs pages          exactly 2 valid providers, alphabetical, filename=={a}-vs-{b}
                       (lives at content/en/compare/{a}-vs-{b}.md, layout vs-single)
  8. carriers.toml     (optional) profile fields sane, name joins countries.carriers
Exit code 1 on any ERROR; warnings do not fail.
"""
import re
import sys
import tomllib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
COMPARE = ROOT / "content" / "en" / "compare"

errors: list[str] = []
warnings: list[str] = []


def err(msg: str) -> None:
    errors.append(msg)


def warn(msg: str) -> None:
    warnings.append(msg)


def load(rel: str) -> dict:
    return tomllib.loads((DATA / rel).read_text(encoding="utf-8"))


# --- 1. countries.toml -------------------------------------------------------
countries = load("countries.toml")
for iso, c in countries.items():
    for f in ("name", "slug", "flag", "region"):
        if f not in c:
            err(f"countries.{iso}: missing field '{f}'")
    for n in c.get("neighbors", []):
        if n not in countries:
            err(f"countries.{iso}.neighbors: unknown ISO '{n}'")

# --- 2. providers.toml -------------------------------------------------------
providers = load("providers.toml")
for k, p in providers.items():
    for f in ("name", "tagline", "strengths", "weaknesses"):
        if f not in p:
            err(f"providers.{k}: missing field '{f}'")

# --- 3. data/plans/*.toml ----------------------------------------------------
plan_dir = DATA / "plans"
plan_files = sorted(plan_dir.glob("*.toml")) if plan_dir.exists() else []
coverage: dict[str, set[str]] = {iso: set() for iso in countries}

# 注：2026-10-03 移除了「plan name 禁止非拉丁字符」的检查（站点要上多语言，
# 该禁令会拦住合法的本地化 plan 名）。爬虫侧的清洗仍是必须的，责任移到
# scraper（toml_write.clean_plan_name），这里只保留结构性校验。

for pf in plan_files:
    if pf.stem not in providers:
        err(f"plans/{pf.name}: provider '{pf.stem}' not in providers.toml")
    raw = pf.read_text(encoding="utf-8")
    has_sample_marker = bool(re.search(r"SAMPLE", raw, re.I))
    data = tomllib.loads(raw)
    for iso, block in data.items():
        if iso not in countries:
            err(f"{pf.name}: plan block for unknown ISO '{iso}'")
            continue
        coverage[iso].add(pf.stem)
        if "checked" not in block:
            err(f"{pf.name}[{iso}]: missing 'checked' (date)")
        if "networks" not in block:
            err(f"{pf.name}[{iso}]: missing 'networks'")
        if not block.get("plans"):
            err(f"{pf.name}[{iso}]: empty plans array")
        for i, plan in enumerate(block.get("plans", [])):
            where = f"{pf.name}[{iso}].plans[{i}]"
            for f in ("name", "gb", "days", "type", "price"):
                if f not in plan:
                    err(f"{where}: missing '{f}'")
            if plan.get("price", 0) <= 0:
                err(f"{where}: price must be > 0")
            if plan.get("days", 0) <= 0:
                err(f"{where}: days must be > 0")
            if plan.get("gb", -1) < 0:
                err(f"{where}: gb must be >= 0 (0 = unlimited)")
            name = plan.get("name", "")
            if name != name.strip():
                err(f"{where}: plan name has leading/trailing whitespace {name!r}")
            elif re.match(r"^[^0-9A-Za-z\u00C0-\u024F]", name):
                err(f"{where}: plan name starts with junk {name!r} "
                    f"(stray quote/punctuation from the source DOM)")
    if has_sample_marker:
        warn(f"{pf.name}: contains SAMPLE data - prices not yet verified")

# --- 4. compare pages <-> countries -----------------------------------------
pages: dict[str, str] = {}
if COMPARE.exists():
    for md in sorted(COMPARE.glob("*.md")):
        if md.name == "_index.md":
            continue
        if "-vs-" in md.stem:
            continue  # matchup page, checked in section 7
        if md.stem == "matchups":
            continue  # matchup hub page (layout matchups, nolist) — not a country page
        text = md.read_text(encoding="utf-8")
        m = re.search(r'^iso\s*[:=]\s*["\']?([A-Z]{2})["\']?\s*$', text, re.M)
        if not m:
            err(f"compare/{md.name}: no iso = \"XX\" in front matter")
            continue
        iso = m.group(1)
        pages[iso] = md.name
        if iso not in countries:
            err(f"compare/{md.name}: iso {iso} not defined in countries.toml")

for iso in countries:
    if iso not in pages:
        warn(f"countries.{iso} ({countries[iso].get('name', iso)}): no compare page yet")
    elif coverage[iso] and len(coverage[iso]) < 3:
        warn(f"{iso}: only {len(coverage[iso])} provider(s) priced - comparison page will look thin")

# --- 5. faqs <-> pages -------------------------------------------------------
faq_dir = DATA / "faqs"
faqs = {p.stem.upper(): p.name for p in faq_dir.glob("*.toml")} if faq_dir.exists() else {}
for iso in pages:
    if iso not in faqs:
        warn(f"compare/{pages[iso]}: no data/faqs/{iso.lower()}.toml (page renders without FAQ section)")
for iso, fname in faqs.items():
    if iso not in pages:
        warn(f"faqs/{fname}: no compare page for {iso}")
    else:
        fdata = tomllib.loads((faq_dir / fname).read_text(encoding="utf-8"))
        for i, qa in enumerate(fdata.get("faq", [])):
            if "q" not in qa or "a" not in qa:
                err(f"faqs/{fname}.faq[{i}]: needs both 'q' and 'a'")

# --- 6. slug map (deep links) ------------------------------------------------
# Targets with a country_path in hugo.toml need per-country slugs. Today: roami.
DEEPLINK_TARGETS = {"roami": "/{slug}/"}
for iso in countries:
    slugs = countries[iso].get("slugs", {})
    for target in DEEPLINK_TARGETS:
        if target in coverage[iso] and target not in slugs:
            warn(f"countries.{iso}.slugs: '{target}' deep link missing -> CTA falls back to provider homepage")

# --- 7. vs pages (content/en/compare/{a}-vs-{b}.md) ---------------------------
# Layout guards exist (errorf), but validate.py runs BEFORE hugo - catch it here.
for md in sorted(COMPARE.glob("*-vs-*.md")):
    text = md.read_text(encoding="utf-8")
    m = re.search(r'^providers\s*[:=]\s*\[(.*)\]\s*$', text, re.M)
    if not m:
        err(f'compare/{md.name}: no providers = ["a", "b"] in front matter')
        continue
    pair = re.findall(r'["\']([\w-]+)["\']', m.group(1))
    if len(pair) != 2:
        err(f"compare/{md.name}: expected exactly 2 providers, got {len(pair)}: {pair}")
        continue
    for p in pair:
        if p not in providers:
            err(f"compare/{md.name}: unknown provider '{p}'")
    if not re.search(r"^layout\s*[:=]\s*['\"]?vs-single", text, re.M):
        err(f"compare/{md.name}: missing 'layout: vs-single' (would render via country template)")
    a, b = pair[0], pair[1]
    if a >= b:
        err(f"compare/{md.name}: providers must be alphabetical, got [{a}, {b}]")
    elif md.name != f"{a}-vs-{b}.md":
        err(f"compare/{md.name}: filename should be '{a}-vs-{b}.md'")

# --- 8. carriers.toml (optional host-network profiles) -----------------------
carriers_file = DATA / "carriers.toml"
if carriers_file.exists():
    cdata = tomllib.loads(carriers_file.read_text(encoding="utf-8"))
    for iso, block in cdata.items():
        if iso not in countries:
            err(f"carriers.{iso}: unknown ISO")
            continue
        local = countries[iso].get("carriers", [])
        for i, prof in enumerate(block.get("profiles", [])):
            where = f"carriers.{iso}.profiles[{i}]"
            for f in ("name", "tech", "speed_min", "speed_top", "note"):
                if f not in prof:
                    err(f"{where}: missing '{f}'")
            if prof.get("name") and prof["name"] not in local:
                err(f"carriers.{iso}: profile '{prof['name']}' not in countries.{iso}.carriers {local} (join key)")
            if prof.get("tech") not in ("4G", "5G"):
                err(f"{where}: tech must be '4G' or '5G'")
            if prof.get("speed_min", 0) <= 0 or prof.get("speed_top", 0) < prof.get("speed_min", 0):
                err(f"{where}: need 0 < speed_min <= speed_top")

# --- report ------------------------------------------------------------------
for w in warnings:
    print(f"WARN  {w}")
for e in errors:
    print(f"ERROR {e}")
print(f"\n{len(errors)} error(s), {len(warnings)} warning(s)")
sys.exit(1 if errors else 0)
