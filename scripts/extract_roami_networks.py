#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Extract Roami's network partners from the Roami project's country front matter
(country_meta.operators) -> _net_results/roami.json for the backfill step.

Authoritative: these are Roami's own published operator lists (roamiapp.com pages).
Every name is validated against data/carriers.toml before it is kept; unmatched
names are recorded in `notes` and never fabricated.
"""
import json, re, tomllib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ROAMI_CONTENT = Path(r"D:\HUGO test\29.1_windows-amd64\hugo_0.159.1_windows-amd64\esim\content\en")

NAME_VARIANTS = {
    "united-states": ["United-States-eSIM.md", "USA-eSIM.md", "Us-eSIM.md"],
    "united-kingdom": ["United-Kingdom-eSIM.md", "UK-eSIM.md"],
    "turkiye": ["Turkey-eSIM.md", "Turkiye-eSIM.md"],
    "czechia": ["Czech-Republic-eSIM.md", "Czechia-eSIM.md"],
    "united-arab-emirates": ["United-Arab-Emirates-eSIM.md", "UAE-eSIM.md"],
    "macao": ["Macau-eSIM.md", "Macao-eSIM.md"],
    "south-korea": ["South-Korea-eSIM.md", "Korea-eSIM.md"],
    "hong-kong": ["Hong-Kong-eSIM.md", "Hongkong-eSIM.md"],
}

countries = tomllib.load(open(ROOT / "data" / "countries.toml", "rb"))
carriers = tomllib.load(open(ROOT / "data" / "carriers.toml", "rb"))

def canon(iso):
    return [p["name"] for p in carriers.get(iso, {}).get("profiles", [])]

def norm(s):
    return re.sub(r"[^a-z0-9]", "", (s or "").lower())

# Roami operator name -> canonical carriers.toml name, per country. Only sound
# brand-name equivalences (rebrands / legal names), nothing guessed.
ALIASES = {
    "AT": {"A1 Telekom": "A1", "T-Mobile": "Magenta"},
    "BE": {"Orange Belgium": "Orange", "Telenet": "Base"},
    "CR": {"ICE": "Kolbi", "Liberty": "Movistar"},
    "DE": {"Deutsche Telekom": "Telekom"},
    "EG": {"Orange": "Orange Egypt", "Vodafone": "Vodafone Egypt", "Etisalat": "Etisalat Misr"},
    "FR": {"Bouygues Telecom": "Bouygues"},
    "GE": {"MagtiCom": "Magti", "Cellfie": "Beeline"},
    "ID": {"Indosat Ooredoo": "Indosat"},
    "IS": {"Síminn": "Siminn"},
    "IT": {"Vodafone Italia": "Vodafone"},
    "MA": {"Orange": "Orange Maroc"},
    "MX": {"AT&T": "AT&T Mexico"},
}

result = {"brand": "roami", "source_url": "https://roamiapp.com country pages (country_meta.operators)", "networks": {}, "notes": {}}
filled = 0
for iso, c in sorted(countries.items(), key=lambda kv: kv[1]["slug"]):
    slug, name = c["slug"], c["name"]
    cands = NAME_VARIANTS.get(slug, [f"{name}-eSIM.md"])
    path = next((ROAMI_CONTENT / x for x in cands if (ROAMI_CONTENT / x).exists()), None)
    if path is None:
        pat = re.compile(re.escape(name).replace(r"\ ", r"[-\ ]") + r"-eSIM\.md", re.I)
        hits = [p for p in ROAMI_CONTENT.glob("*-eSIM.md") if pat.match(p.name)]
        path = hits[0] if hits else None
    if path is None:
        result["notes"][iso] = "no Roami page found"
        continue
    text = path.read_text(encoding="utf-8")
    fm = text.split("---")[1] if text.startswith("---") else ""
    m = re.search(r"^[ \t]*operators:[ \t]*(.+?)[ \t]*$", fm, re.M)
    if not m:
        result["notes"][iso] = "no operators field"
        continue
    ops = [o.strip() for o in m.group(1).split(",") if o.strip()]
    ok = []
    for o in ops:
        match = next((cn for cn in canon(iso) if norm(cn) == norm(o)), None)
        if match is None:
            match = ALIASES.get(iso, {}).get(o)
        if match:
            ok.append(match)
        else:
            result["notes"].setdefault(iso, "unmatched: ")
            result["notes"][iso] += f"{o!r} "
    if ok:
        result["networks"][iso] = ok
        filled += 1

outdir = ROOT / "_net_results"
outdir.mkdir(exist_ok=True)
(outdir / "roami.json").write_text(json.dumps(result, ensure_ascii=False, indent=1), encoding="utf-8")
print(f"roami: filled {filled}/50 countries with network partners")
for iso in sorted(result["networks"]):
    print(f"  {iso:3} -> {result['networks'][iso]}")
if result["notes"]:
    print("notes:")
    for iso, n in sorted(result["notes"].items()):
        print(f"  {iso}: {n}")
