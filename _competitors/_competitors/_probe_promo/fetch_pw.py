# -*- coding: utf-8 -*-
"""Fetch pages via Playwright Chromium (bypasses simple WAF / Cloudflare 403 that blocks requests)."""
import os, sys, json, time, random
from playwright.sync_api import sync_playwright

OUT = os.path.dirname(os.path.abspath(__file__))
UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36")

PAGES = {
    "ubigi_home": "https://www.ubigi.com/",
    "ubigi_promotions": "https://www.ubigi.com/en/promotions/",
    "ubigi_offers": "https://www.ubigi.com/en/offers/",
    "ubigi_store": "https://www.ubigi.com/en/store/",
    "airalo_home": "https://www.airalo.com/",
    "airalo_promo": "https://www.airalo.com/promo-codes",
    "airalo_deals": "https://www.airalo.com/deals",
    "alosim_home": "https://alosim.com/",
    "alosim_deals": "https://alosim.com/deals",
    "nomad_home": "https://www.nomadesim.com/",
    "nomad_deals": "https://www.nomadesim.com/deals",
    "nomad_promo": "https://www.nomadesim.com/promotions",
}


def main(names):
    targets = {k: v for k, v in PAGES.items() if not names or k in names}
    with sync_playwright() as p:
        br = p.chromium.launch(headless=True, args=["--disable-blink-features=AutomationControlled"])
        ctx = br.new_context(user_agent=UA, locale="en-US",
                             viewport={"width": 1440, "height": 900},
                             extra_http_headers={"Accept-Language": "en-US,en;q=0.9"})
        pg = ctx.new_page()
        for k, u in targets.items():
            try:
                pg.goto(u, wait_until="domcontentloaded", timeout=45000)
                pg.wait_for_timeout(3500)
                title = pg.title()
                content = pg.content()
                fp = os.path.join(OUT, k + ".html")
                open(fp, "w", encoding="utf-8").write(content)
                print("%-18s OK  %7d  %s" % (k, len(content), title[:60]))
                time.sleep(random.uniform(1.5, 3.0))
            except Exception as e:
                print("%-18s ERR %s %s" % (k, type(e).__name__, str(e)[:70]))
        br.close()


if __name__ == "__main__":
    main(sys.argv[1:])
