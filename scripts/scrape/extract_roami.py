#!/usr/bin/env python3
"""Extract Roami (own brand) plan data from the local Roami Hugo project's
money pages (content/en/{Country}-eSIM.md -> front matter plans_data).

Emits scripts/scrape/raw/roami/<our-slug>.json in the same shape as esimdb
scrapes so toml_write.py works unchanged.

Usage: python -X utf8 scripts/scrape/extract_roami.py
"""
import json
import re
import sys
import tomllib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
RAW = Path(__file__).resolve().parent / "raw"
ROAMI_CONTENT = Path(r"D:\HUGO test\29.1_windows-amd64\hugo_0.159.1_windows-amd64\esim\content\en")

# our slug -> Roami content filename candidates (Country-eSIM.md, case variants)
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


def parse_plans_data(fm_text: str) -> list[dict] | None:
    """Minimal YAML-subset parser for the plans_data block."""
    m = re.search(r"^plans_data:\s*$", fm_text, re.M)
    if not m:
        return None
    lines = fm_text[m.end():].splitlines()
    plans: list[dict] = []
    duration = None
    item: dict | None = None
    for line in lines:
        if not line.strip() or line.strip().startswith("#"):
            break_like = not line.startswith(" ")
        # end of block: a non-indented key that is not plans_data
        if line and not line[0].isspace():
            break
        s = line.strip()
        if re.fullmatch(r"\d+ Days:", s):
            duration = int(s.split()[0])
            item = None
            continue
        mm = re.fullmatch(r"- spec:\s*(.+)", s)
        if mm:
            item = {"spec": mm.group(1).strip()}
            plans.append(item)
            continue
        mm = re.match(r"(price|daily):\s*'?([\d.]+)'?", s)
        if mm and item is not None:
            item[mm.group(1)] = mm.group(2)
            continue
    # keep only complete items with duration
    out = []
    for pl in plans:
        pass
    return plans


def main() -> None:
    sys.path.insert(0, "")
    try:
        import yaml
        HAVE_YAML = True
    except ImportError:
        HAVE_YAML = False
    print(f"pyyaml: {HAVE_YAML}")

    countries = tomllib.loads((ROOT / "data" / "countries.toml").read_text(encoding="utf-8"))
    by_slug = {c["slug"]: (iso, c["name"]) for iso, c in countries.items()}
    outdir = RAW / "roami"
    outdir.mkdir(parents=True, exist_ok=True)

    ok, miss = 0, []
    for slug, (iso, name) in sorted(by_slug.items()):
        cands = NAME_VARIANTS.get(slug, [f"{name}-eSIM.md"])
        path = next((ROAMI_CONTENT / c for c in cands if (ROAMI_CONTENT / c).exists()), None)
        if path is None:
            # try title-case fallback search
            pat = re.compile(re.escape(name).replace(r"\ ", r"[-\ ]") + r"-eSIM\.md", re.I)
            hits = [p for p in ROAMI_CONTENT.glob("*-eSIM.md") if pat.match(p.name)]
            path = hits[0] if hits else None
        if path is None:
            miss.append(name)
            (outdir / f"{slug}.json").write_text(
                json.dumps({"slug": slug, "url": None, "status": 404, "plans": []}),
                encoding="utf-8")
            continue

        text = path.read_text(encoding="utf-8")
        fm = text.split("---")[1] if text.startswith("---") else ""
        plans = []
        if HAVE_YAML:
            import yaml
            data = yaml.safe_load(fm) or {}
            pd = data.get("plans_data") or {}
            for dur_label, items in pd.items():
                mm = re.match(r"(\d+)\s*Days?", str(dur_label))
                if not mm or not isinstance(items, list):
                    continue
                days = int(mm.group(1))
                for it in items:
                    spec = str(it.get("spec", "")).strip()
                    price = str(it.get("price", "")).strip()
                    if not spec or not price:
                        continue
                    plans.append({
                        "name": f"{spec} / {days} Days",
                        "data": "Unlimited" if "unlimited" in spec.lower() else spec.replace(" ", ""),
                        "validity": f"{days} Days",
                        "price": f"${price}",
                        "badges": [],
                    })
        if not plans:  # fallback minimal parser
            plans = parse_plans_data(fm) or []

        (outdir / f"{slug}.json").write_text(
            json.dumps({"slug": slug, "url": str(path), "status": 200,
                        "tab": {"clicked": False, "label": "local:plans_data"},
                        "plans": plans, "meta": {"title": path.name}}, indent=1),
            encoding="utf-8")
        ok += 1
        print(f"{slug:22} {path.name:34} {len(plans):>3} plans")

    print(f"\nroami: {ok}/50 extracted; missing: {miss}")


if __name__ == "__main__":
    main()
