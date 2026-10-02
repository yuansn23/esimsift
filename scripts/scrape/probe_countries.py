#!/usr/bin/env python3
"""Probe candidate esimdb slugs for our 20 unmapped countries + holafly check.
Writes scrape_tmp/probe/country_map_verified.json
"""
import json
from pathlib import Path

from playwright.sync_api import sync_playwright

OUT = Path(__file__).resolve().parent / "probe"

UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/148.0.0.0 Safari/537.36")

# our slug -> candidate esimdb slugs (in priority order)
CANDIDATES = {
    "united-states": ["usa"],
    "united-kingdom": ["uk", "united-kingdom", "great-britain"],
    "singapore": ["singapore"],
    "macao": ["macau", "macao"],
    "indonesia": ["indonesia"],
    "philippines": ["philippines"],
    "india": ["india"],
    "netherlands": ["netherlands", "holland"],
    "belgium": ["belgium"],
    "switzerland": ["switzerland"],
    "turkiye": ["turkey", "turkiye"],
    "ireland": ["ireland"],
    "czechia": ["czechia", "czech-republic"],
    "croatia": ["croatia"],
    "iceland": ["iceland"],
    "georgia": ["georgia"],
    "united-arab-emirates": ["uae", "united-arab-emirates"],
    "qatar": ["qatar"],
    "israel": ["israel"],
    "kenya": ["kenya"],
}

results: dict[str, str] = {}
holafly_status = None

with sync_playwright() as p:
    b = p.chromium.launch(headless=True, args=["--disable-blink-features=AutomationControlled"])
    ctx = b.new_context(user_agent=UA, viewport={"width": 1280, "height": 800}, locale="en-US")
    pg = ctx.new_page()

    # warm up: pass WAF challenge once
    pg.goto("https://esimdb.com/usa", wait_until="domcontentloaded", timeout=45000)
    pg.wait_for_timeout(4000)

    for our, cands in CANDIDATES.items():
        for cand in cands:
            url = f"https://esimdb.com/{cand}/airalo"
            try:
                resp = pg.goto(url, wait_until="domcontentloaded", timeout=30000)
                pg.wait_for_timeout(1200)
                status = resp.status if resp else 0
                title = pg.title()
                if status == 200 and "airalo" in title.lower() and "not" not in title.lower()[:12]:
                    results[our] = cand
                    print(f"OK   {our:24} -> {cand}   ({title[:60]})")
                    break
                print(f"MISS {our:24} -> {cand}   HTTP {status} ({title[:50]})")
            except Exception as e:
                print(f"ERR  {our:24} -> {cand}   {str(e)[:80]}")

    # holafly check on a known-good country
    try:
        resp = pg.goto("https://esimdb.com/usa/holafly", wait_until="domcontentloaded", timeout=30000)
        pg.wait_for_timeout(2500)
        title = pg.title()
        holafly_status = {"status": resp.status if resp else 0, "title": title,
                          "h1": pg.evaluate("() => (document.querySelector('h1')||{}).innerText || ''")}
        print(f"\nholafly on /usa: HTTP {resp.status}, title={title!r}")
    except Exception as e:
        holafly_status = {"error": str(e)[:200]}
        print(f"\nholafly FAIL: {str(e)[:120]}")

    b.close()

(OUT / "country_map_verified.json").write_text(
    json.dumps({"map": results, "holafly_usa": holafly_status}, indent=1), encoding="utf-8")
print(f"\nmapped {len(results)}/20")
print(json.dumps(results, indent=0))
