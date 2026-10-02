#!/usr/bin/env python3
"""Discover esimdb country + provider slugs (from sitemap.xml + homepage links).
Writes scrape_tmp/probe/esimdb_slugs.json
"""
import json
import re
from pathlib import Path

from playwright.sync_api import sync_playwright

OUT = Path(__file__).resolve().parent / "probe"
OUT.mkdir(parents=True, exist_ok=True)

UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/148.0.0.0 Safari/537.36")

links: set[str] = set()

with sync_playwright() as p:
    b = p.chromium.launch(headless=True, args=["--disable-blink-features=AutomationControlled"])
    ctx = b.new_context(user_agent=UA, viewport={"width": 1366, "height": 900}, locale="en-US")
    pg = ctx.new_page()

    # 1. sitemap
    for sm in ("https://esimdb.com/sitemap.xml",):
        try:
            pg.goto(sm, wait_until="domcontentloaded", timeout=40000)
            pg.wait_for_timeout(1500)
            body = pg.evaluate("() => document.body.innerText")
            urls = re.findall(r"https://esimdb\.com(/[^\s<'\"<>]+)", body)
            links.update(urls)
            print(f"{sm}: {len(urls)} urls")
        except Exception as e:
            print(f"{sm} FAIL: {str(e)[:120]}")

    # 2. homepage + a country page (provider links live on country pages)
    for page_url in ("https://esimdb.com/", "https://esimdb.com/usa", "https://esimdb.com/japan"):
        try:
            pg.goto(page_url, wait_until="domcontentloaded", timeout=40000)
            pg.wait_for_timeout(3500)
            hrefs = pg.eval_on_selector_all("a", "els => els.map(e => e.getAttribute('href'))")
            links.update(h for h in hrefs if h)
            print(f"{page_url}: {len(hrefs)} links")
        except Exception as e:
            print(f"{page_url} FAIL: {str(e)[:120]}")
    b.close()

links = {l if l.startswith("/") else "/" + l for l in links}
links = {l.split("#")[0].split("?")[0] for l in links}

# classify: /{slug}/ = country or provider hub; /{c}/{p}/ = provider-in-country
countries: dict[str, int] = {}
providers: dict[str, int] = {}
pairs: set[tuple[str, str]] = set()
for l in links:
    m = re.fullmatch(r"/([a-z0-9-]+)/?", l)
    m2 = re.fullmatch(r"/([a-z0-9-]+)/([a-z0-9-]+)/?", l)
    if m2:
        countries[m2.group(1)] = countries.get(m2.group(1), 0) + 1
        providers[m2.group(2)] = providers.get(m2.group(2), 0) + 1
        pairs.add(m2.groups())
    elif m:
        countries[m.group(1)] = countries.get(m.group(1), 0)  # 0 = hub link only

print(f"\ntop-level slugs: {len(countries)}, provider slugs: {len(providers)}, pairs: {len(pairs)}")

result = {
    "countries": sorted(countries),
    "providers": sorted(providers),
    "pairs": sorted([list(x) for x in pairs]),
}
(OUT / "esimdb_slugs.json").write_text(json.dumps(result, indent=1), encoding="utf-8")

print("\nproviders seen:")
print(", ".join(sorted(providers)))
