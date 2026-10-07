#!/usr/bin/env python3
"""Scrape esimdb.com plan data for the 5 competitor brands x 50 tracked countries.

Output (does NOT touch any existing project file):
  _competitors/raw/<brand>/<our-slug>.json   raw per-country capture
Resumable: existing output files are skipped unless --force.

Brands: nomad / jetpac / gigsky / quibity  (maya is NOT on esimdb -> official site)
"""
import json
import random
import re
import sys
import time
import tomllib
from pathlib import Path

from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[1]        # esimsift-main/esimsift-main
OUT = ROOT / "_competitors" / "raw"
UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/148.0.0.0 Safari/537.36")

ESIMDB_SLUGS = {
    "united-states": "usa", "united-kingdom": "uk", "canada": "canada",
    "mexico": "mexico", "brazil": "brazil", "argentina": "argentina",
    "colombia": "colombia", "peru": "peru", "costa-rica": "costa-rica",
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

BRANDS = [a for a in sys.argv[1:] if not a.startswith("--")]
FORCE = "--force" in sys.argv
LIMIT = next((int(a.split("=")[1]) for a in sys.argv if a.startswith("--limit=")), 0)


def load_countries():
    data = tomllib.loads((ROOT / "data" / "countries.toml").read_text(encoding="utf-8"))
    return {c["slug"]: c for c in data.values()}


def extract(pg) -> dict:
    tab = pg.evaluate(
        """() => {
            const btns=[...document.querySelectorAll('button')];
            const txt=b=>(b.innerText||'').replace(/\\s+/g,' ').trim();
            // gigsky labels its tab just "Single" / "Single-country 11"; accept both
            const t=btns.find(b=>/^Single-?country/i.test(txt(b)))
                 || btns.find(b=>/^Single\\b/i.test(txt(b)));
            if(t){t.click();return {clicked:true,label:txt(t)};}
            return {clicked:false,label:null};
        }""")
    if tab.get("clicked"):
        pg.wait_for_timeout(900)

    plans = []
    for card in pg.query_selector_all("div.w-full.bg-white.rounded-xl"):
        try:
            name_el = card.query_selector(".text-body-15")
            bolds = card.query_selector_all(".text-body-20-extrabold")
            price_el = card.query_selector(".text-body-22-black")
            badges = [x.strip() for x in
                      (card.eval_on_selector_all(".badge", "els=>els.map(e=>e.innerText.replace(/\\s+/g,' ').trim())") or []) if x]
            if not name_el or not price_el:
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

    # meta is best-effort: a failure here must never discard the plans we already parsed
    try:
        meta = pg.evaluate(
            """() => {
                const h1=document.querySelector('h1');
                const netEl=[...document.querySelectorAll('*')].find(e=>/^Networks?:/i.test(((e.innerText||'')+'').trim().slice(0,40))&&e.children.length===0);
                return {
                    title:document.title,
                    h1:h1?(h1.innerText||'').trim():null,
                    networks:netEl?(netEl.innerText||'').trim():null,
                };
            }""")
    except Exception as e:
        meta = {"title": None, "h1": None, "networks": None, "meta_error": str(e)[:120]}
    return {"tab": tab, "plans": plans, "meta": meta}


def fetch(pg, brand, slug, esimdb_slug):
    url = f"https://esimdb.com/{esimdb_slug}/{brand}"
    for attempt in (1, 2, 3, 4):
        try:
            r = pg.goto(url, wait_until="domcontentloaded", timeout=35000)
            pg.wait_for_timeout(2500 + attempt * 800)
            status = r.status if r else 0
            if status == 404:
                return {"slug": slug, "url": url, "status": 404, "plans": [], "meta": None, "tab": None}
            if "Human Verification" in pg.content():
                cool = 8000 + 4000 * attempt   # challenge may auto-resolve; grow backoff
                print(f"    WAF retry {attempt}, wait {cool / 1000:.0f}s", flush=True)
                pg.wait_for_timeout(cool)
                continue
            if status != 200:
                pg.wait_for_timeout(3000)
                continue
            res = extract(pg)
            res.update({"slug": slug, "url": url, "status": 200})
            return res
        except Exception as e:
            print(f"    attempt {attempt} err: {str(e)[:90]}", flush=True)
            pg.wait_for_timeout(3000)
    return None


def main():
    countries = load_countries()
    for brand in BRANDS:
        outdir = OUT / brand
        outdir.mkdir(parents=True, exist_ok=True)
        todo = [s for s in sorted(countries)
                if s in ESIMDB_SLUGS and (FORCE or not (outdir / f"{s}.json").exists())]
        if LIMIT:
            todo = todo[:LIMIT]
        print(f"\n### {brand}: {len(todo)} countries", flush=True)
        stats = {"ok": 0, "empty": [], "fail": [], "404": []}
        with sync_playwright() as p:
            b = p.chromium.launch(headless=True, args=["--disable-blink-features=AutomationControlled"])
            ctx = b.new_context(user_agent=UA, viewport={"width": 1280, "height": 900}, locale="en-US")
            pg = ctx.new_page()
            pg.goto("https://esimdb.com/usa", wait_until="domcontentloaded", timeout=45000)
            pg.wait_for_timeout(4500)
            consec_fail = 0
            for i, slug in enumerate(todo, 1):
                print(f"[{i}/{len(todo)}] {brand}/{slug}", flush=True)
                res = fetch(pg, brand, slug, ESIMDB_SLUGS[slug])
                if res is None:
                    stats["fail"].append(slug); print("    FAIL", flush=True)
                    consec_fail += 1
                    if consec_fail >= 2:
                        cool = random.uniform(45, 75)
                        print(f"    cooldown {cool:.0f}s after {consec_fail} consecutive fails", flush=True)
                        time.sleep(cool)
                else:
                    consec_fail = 0
                    n = len(res["plans"])
                    print(f"    {res['status']}  {n} plans", flush=True)
                    (outdir / f"{slug}.json").write_text(
                        json.dumps(res, indent=1, ensure_ascii=False), encoding="utf-8")
                    if res["status"] == 404: stats["404"].append(slug)
                    elif n == 0: stats["empty"].append(slug)
                    else: stats["ok"] += 1
                time.sleep(random.uniform(2.0, 3.5))
            b.close()
        print(f"=== {brand}: ok={stats['ok']} empty={stats['empty']} 404={stats['404']} fail={stats['fail']}", flush=True)


if __name__ == "__main__":
    main()
