#!/usr/bin/env python3
"""Scrape esimdb.com provider plan data for all 50 tracked countries.

Usage:
  python -X utf8 scripts/scrape/scrape_esimdb.py <provider> [--force]

- Passes AWS WAF via real chromium; one browser session for all countries.
- Clicks the "Single-country" tab (regional/multi-country plans are out of scope).
- Raw JSON per country -> scripts/scrape/raw/<provider>/<our-slug>.json
- Resumable: existing output files are skipped unless --force.

Data model written downstream (toml_write.py):
  data text "10GB"                -> type=data, gb=10
  data text "1GB/Day + ..."       -> daily allowance: type=data, gb=1*days,
                                     fup_note="1 GB per day for N days"
  data text "3GB/day + ∞ at 1Mbps"-> type=unlimited, gb=0, fup_note=<text>
  data text "Unlimited"           -> type=unlimited, gb=0, fup_note=""
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

# our slug -> esimdb slug (30 direct + 20 verified by probe_countries.py 2026-09-30)
ESIMDB_SLUGS = {
    "united-states": "usa", "united-kingdom": "uk", "canada": "canada",
    "mexico": "mexico", "brazil": "brazil", "argentina": "argentina",
    "chile": "chile", "colombia": "colombia", "peru": "peru",
    "costa-rica": "costa-rica",
    "japan": "japan", "south-korea": "south-korea", "china": "china",
    "hong-kong": "hong-kong", "macao": "macau", "taiwan": "taiwan",
    "singapore": "singapore", "thailand": "thailand", "vietnam": "vietnam",
    "indonesia": "indonesia", "malaysia": "malaysia", "philippines": "philippines",
    "india": "india", "australia": "australia", "new-zealand": "new-zealand",
    "fiji": "fiji",
    "france": "france", "germany": "germany", "italy": "italy", "spain": "spain",
    "portugal": "portugal", "netherlands": "netherlands", "belgium": "belgium",
    "switzerland": "switzerland", "austria": "austria", "ireland": "ireland",
    "turkiye": "turkey", "greece": "greece", "czechia": "czechia",
    "croatia": "croatia", "iceland": "iceland", "poland": "poland",
    "georgia": "georgia", "united-arab-emirates": "uae", "qatar": "qatar",
    "israel": "israel", "saudi-arabia": "saudi-arabia", "egypt": "egypt",
    "morocco": "morocco", "south-africa": "south-africa", "kenya": "kenya",
}


def load_countries() -> dict[str, dict]:
    data = tomllib.loads((ROOT / "data" / "countries.toml").read_text(encoding="utf-8"))
    return {c["slug"]: c for c in data.values()}


def extract_plans(pg) -> dict:
    """Extract plan cards + page meta from a rendered provider page."""
    # try to switch to the Single-country tab
    tab_info = pg.evaluate(
        """() => {
            const btns = [...document.querySelectorAll('button')];
            const tab = btns.find(b => /^Single-country/.test(b.innerText.trim()));
            if (tab) { tab.click(); return {clicked: true, label: tab.innerText.trim()}; }
            return {clicked: false, label: null};
        }"""
    )
    if tab_info.get("clicked"):
        pg.wait_for_timeout(900)

    cards = pg.query_selector_all("div.w-full.bg-white.rounded-xl")
    plans = []
    for card in cards:
        try:
            name_el = card.query_selector(".text-body-15")
            bolds = card.query_selector_all(".text-body-20-extrabold")
            price_el = card.query_selector(".text-body-22-black")
            badges = [b.strip() for b in
                      (card.eval_on_selector_all(".badge", "els => els.map(e => e.innerText.replace(/\\s+/g,' ').trim())")
                       or []) if b]
            if not name_el or not bolds or not price_el:
                continue
            plans.append({
                "name": name_el.inner_text().strip(),
                "data": bolds[0].inner_text().strip() if bolds else "",
                "validity": bolds[1].inner_text().strip() if len(bolds) > 1 else "",
                "price": price_el.inner_text().strip(),
                "badges": badges,
            })
        except Exception:
            continue

    meta = pg.evaluate(
        """() => {
            const h1 = document.querySelector('h1');
            const desc = document.querySelector('.text-body-16, [class*=description]');
            const chips = [...document.querySelectorAll('button')].map(b => b.innerText.trim())
                .filter(t => /^(All plans|Single-country|Multiple-country)/.test(t));
            const site = [...document.querySelectorAll('a')].find(a => /Official Website/i.test(a.innerText));
            return {
                title: document.title,
                h1: h1 ? h1.innerText.trim() : null,
                chips,
                official_site: site ? site.href : null,
                body_head: document.body.innerText.slice(0, 900),
            };
        }"""
    )
    return {"tab": tab_info, "plans": plans, "meta": meta}


def fetch_country(pg, provider: str, slug: str, esimdb_slug: str) -> dict | None:
    url = f"https://esimdb.com/{esimdb_slug}/{provider}"
    for attempt in (1, 2, 3):
        try:
            resp = pg.goto(url, wait_until="domcontentloaded", timeout=35000)
            pg.wait_for_timeout(2500 + attempt * 800)
            status = resp.status if resp else 0
            if status == 404:
                return {"slug": slug, "url": url, "status": 404, "plans": [], "meta": None, "tab": None}
            content = pg.content()
            if "Human Verification" in content:
                print(f"    WAF challenge, retry {attempt}")
                pg.wait_for_timeout(5000)
                continue
            if status != 200:
                pg.wait_for_timeout(3000)
                continue
            result = extract_plans(pg)
            result.update({"slug": slug, "url": url, "status": 200})
            return result
        except Exception as e:
            print(f"    attempt {attempt} error: {str(e)[:100]}")
            pg.wait_for_timeout(3000)
    return None


def main() -> None:
    providers = [a for a in sys.argv[1:] if not a.startswith("--")]
    force = "--force" in sys.argv
    countries = load_countries()

    for provider in providers:
        outdir = RAW / provider
        outdir.mkdir(parents=True, exist_ok=True)
        todo = []
        for slug in sorted(countries):
            if slug not in ESIMDB_SLUGS:
                print(f"SKIP {slug}: no esimdb slug mapping")
                continue
            f = outdir / f"{slug}.json"
            if f.exists() and not force:
                continue
            todo.append(slug)
        if not todo:
            print(f"\n### {provider}: nothing to do")
            continue
        print(f"\n### {provider}: {len(todo)} countries to fetch", flush=True)

        stats = {"ok": 0, "empty": [], "fail": [], "http404": []}
        with sync_playwright() as p:
            b = p.chromium.launch(headless=True, args=["--disable-blink-features=AutomationControlled"])
            ctx = b.new_context(user_agent=UA, viewport={"width": 1280, "height": 900}, locale="en-US")
            pg = ctx.new_page()

            # warm-up navigation to clear the WAF challenge once
            pg.goto("https://esimdb.com/usa", wait_until="domcontentloaded", timeout=45000)
            pg.wait_for_timeout(4000)

            for i, slug in enumerate(todo, 1):
                esimdb_slug = ESIMDB_SLUGS[slug]
                print(f"[{i}/{len(todo)}] {slug} (/esimdb: {esimdb_slug}) ...", flush=True)
                result = fetch_country(pg, provider, slug, esimdb_slug)
                if result is None:
                    stats["fail"].append(slug)
                    print("    FAIL")
                else:
                    n = len(result["plans"])
                    chip = (result.get("tab") or {}).get("label") or ""
                    print(f"    {result['status']}, {n} plans (tab: {chip})")
                    (outdir / f"{slug}.json").write_text(
                        json.dumps(result, indent=1, ensure_ascii=False), encoding="utf-8")
                    if result["status"] == 404:
                        stats["http404"].append(slug)
                    elif n == 0:
                        stats["empty"].append(slug)
                    else:
                        stats["ok"] += 1
                time.sleep(random.uniform(1.0, 2.2))
            b.close()

        print(f"=== {provider}: ok={stats['ok']} empty={stats.get('empty', [])} "
              f"404={stats.get('http404', [])} fail={stats['fail']}")


if __name__ == "__main__":
    main()
