# -*- coding: utf-8 -*-
"""Render JS-heavy promo pages and dump visible text + embedded JSON code tokens."""
import os, sys, re, json, time, random
from playwright.sync_api import sync_playwright

OUT = os.path.dirname(os.path.abspath(__file__))
UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36")

PAGES = {
    "pw_bnesim_offers": "https://www.bnesim.com/offers",
    "pw_bnesim_promotions": "https://www.bnesim.com/promotions",
    "pw_gigsky_promotions": "https://www.gigsky.com/promotions",
    "pw_gigsky_refer": "https://www.gigsky.com/refer",
    "pw_gigsky_visa": "https://www.gigsky.com/visa-benefits",
    "pw_maya_promotions": "https://maya.net/",
    "pw_quibity_coupons": "https://quibity.com/coupons",
    "pw_gomoworld_promo": "https://www.gomoworld.com/en",
    "pw_firsty_refer": "https://www.firsty.app/refer-a-friend",
    "pw_roamless_offers": "https://roamless.com/",
}


def main(names):
    targets = {k: v for k, v in PAGES.items() if not names or k in names}
    with sync_playwright() as p:
        br = p.chromium.launch(headless=True, args=["--disable-blink-features=AutomationControlled"])
        ctx = br.new_context(user_agent=UA, locale="en-US",
                             viewport={"width": 1440, "height": 1200},
                             extra_http_headers={"Accept-Language": "en-US,en;q=0.9"})
        pg = ctx.new_page()
        for k, u in targets.items():
            try:
                pg.goto(u, wait_until="networkidle", timeout=60000)
                pg.wait_for_timeout(4000)
                # scroll to trigger lazy content
                for _ in range(4):
                    pg.mouse.wheel(0, 1600)
                    pg.wait_for_timeout(700)
                body = pg.inner_text("body")
                html = pg.content()
                open(os.path.join(OUT, k + ".txt"), "w", encoding="utf-8").write(body)
                open(os.path.join(OUT, k + ".html"), "w", encoding="utf-8").write(html)
                print("%-24s OK text=%d html=%d" % (k, len(body), len(html)))
                time.sleep(random.uniform(1.2, 2.4))
            except Exception as e:
                print("%-24s ERR %s %s" % (k, type(e).__name__, str(e)[:60]))
        br.close()


if __name__ == "__main__":
    main(sys.argv[1:])
