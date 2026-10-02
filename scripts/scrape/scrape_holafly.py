#!/usr/bin/env python3
"""Scrape holafly.com PDP price tables (unlimited-by-days plans).

esimdb does not list Holafly -> source is the official product page.
Pattern: https://esim.holafly.com/esim-{country}/ with a `pdp-table`
(Number of days | Price USD). All plans unlimited; FUP wording comes from
the Product JSON-LD description (Always On backup etc).

Output: scripts/scrape/raw/holafly/<our-slug>.json (same shape as esimdb raw)
"""
import json
import random
import re
import sys
import time
import tomllib
from pathlib import Path

from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[2]
RAW = Path(__file__).resolve().parent / "raw"

UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/148.0.0.0 Safari/537.36")

# our slug -> holafly slug candidates (priority order)
VARIANTS = {
    "united-states": ["esim-united-states", "esim-usa"],
    "united-kingdom": ["esim-united-kingdom", "esim-uk"],
    "turkiye": ["esim-turkey", "esim-turkiye"],
    "czechia": ["esim-czech-republic", "esim-czechia"],
    "united-arab-emirates": ["esim-dubai", "esim-united-arab-emirates", "esim-uae"],
    "macao": ["esim-macau", "esim-macao"],
    "south-korea": ["esim-south-korea", "esim-korea"],
}


def load_countries() -> dict[str, dict]:
    data = tomllib.loads((ROOT / "data" / "countries.toml").read_text(encoding="utf-8"))
    return {c["slug"]: c for c in data.values()}


def parse_pdp(pg) -> dict:
    rows = pg.eval_on_selector_all(
        "table.pdp-table tr",
        """els => els.map(tr => ({
               head: (tr.querySelector('th')||{}).innerText || '',
               cell: (tr.querySelector('td')||{}).innerText || ''
           }))""")
    plans = []
    for r in rows:
        m = re.match(r"\s*([1-9]\d*)\s*days?\s*$", r.get("head") or "", re.I)
        if not m:
            continue
        days = int(m.group(1))
        pm = re.search(r"\$\s*(\d+(?:\.\d+)?)", r.get("cell") or "")
        cur = "USD" in (r.get("cell") or "")
        if pm and cur:
            plans.append({"name": f"Unlimited / {days} Days",
                          "data": "Unlimited",
                          "validity": f"{days} Days",
                          "price": f"${pm.group(1)}",
                          "badges": []})
    # FUP wording from Product JSON-LD description
    fup = ""
    try:
        ld = pg.evaluate(
            """() => {
                for (const s of document.querySelectorAll('script[type="application/ld+json"]')) {
                    try {
                        const g = JSON.parse(s.textContent);
                        const arr = (g["@graph"] || [g]).flat();
                        const prod = arr.find(n => n && n["@type"] === "Product");
                        if (prod && prod.description) return prod.description;
                    } catch (e) {}
                }
                return "";
            }""")
        if ld:
            m = re.search(r"(Always On[^.]*\.|fair[- ]use[^.]*\.)", ld, re.I)
            fup = (m.group(1) if m else ld)[:220]
    except Exception:
        pass
    title = pg.title()
    return {"plans": plans, "fup": fup, "title": title}


def main() -> None:
    force = "--force" in sys.argv
    countries = load_countries()
    outdir = RAW / "holafly"
    outdir.mkdir(parents=True, exist_ok=True)

    todo = [s for s in sorted(countries)
            if force or not (outdir / f"{s}.json").exists()]
    print(f"holafly: {len(todo)} countries to fetch")

    with sync_playwright() as p:
        b = p.chromium.launch(headless=True, args=["--disable-blink-features=AutomationControlled"])
        ctx = b.new_context(user_agent=UA, viewport={"width": 1280, "height": 900},
                            locale="en-US", timezone_id="America/New_York")
        pg = ctx.new_page()
        for i, slug in enumerate(todo, 1):
            cands = VARIANTS.get(slug, [f"esim-{slug}"])
            done = False
            for cand in cands:
                url = f"https://esim.holafly.com/{cand}/"
                try:
                    resp = pg.goto(url, wait_until="domcontentloaded", timeout=30000)
                    pg.wait_for_timeout(2500)
                    if resp and resp.status == 200:
                        parsed = parse_pdp(pg)
                        if parsed["plans"]:
                            parsed.update({"slug": slug, "url": url, "status": 200,
                                           "tab": {"clicked": False, "label": "pdp-table"}})
                            (outdir / f"{slug}.json").write_text(
                                json.dumps(parsed, indent=1, ensure_ascii=False), encoding="utf-8")
                            print(f"[{i}/{len(todo)}] {slug} -> {cand}: {len(parsed['plans'])} plans", flush=True)
                            done = True
                            break
                except Exception as e:
                    print(f"    {cand} error: {str(e)[:80]}")
            if not done:
                print(f"[{i}/{len(todo)}] {slug}: NOT FOUND ({cands})", flush=True)
                (outdir / f"{slug}.json").write_text(
                    json.dumps({"slug": slug, "url": None, "status": 404,
                                "plans": [], "fup": "", "title": ""}), encoding="utf-8")
            time.sleep(random.uniform(1.0, 2.0))
        b.close()

    n_ok = len([f for f in outdir.glob("*.json")
                if json.loads(f.read_text(encoding="utf-8")).get("status") == 200])
    print(f"holafly done: {n_ok}/50 with plans")


if __name__ == "__main__":
    main()
