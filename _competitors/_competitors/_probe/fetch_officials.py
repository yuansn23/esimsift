# -*- coding: utf-8 -*-
"""Fetch firsty.app + bnesim.com + shop.bnesim.com homepages via playwright -> _probe/."""
from pathlib import Path

from playwright.sync_api import sync_playwright

P = Path(__file__).resolve().parent
UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/148.0.0.0 Safari/537.36")

TARGETS = [
    ("firsty_home.html", "https://www.firsty.app/"),
    ("bnesim_home.html", "https://www.bnesim.com/"),
    ("bnesim_shop_home.html", "https://shop.bnesim.com/"),
]

with sync_playwright() as p:
    b = p.chromium.launch(headless=True, args=["--disable-blink-features=AutomationControlled"])
    ctx = b.new_context(user_agent=UA, viewport={"width": 1280, "height": 900}, locale="en-US")
    pg = ctx.new_page()
    for fname, url in TARGETS:
        try:
            r = pg.goto(url, wait_until="domcontentloaded", timeout=45000)
            pg.wait_for_timeout(6000)
            status = r.status if r else 0
            html = pg.content()
            (P / fname).write_text(html, encoding="utf-8")
            print(f"{fname:24s} HTTP {status}  {len(html)} chars", flush=True)
        except Exception as e:
            print(f"{fname:24s} ERROR {str(e)[:140]}", flush=True)
    b.close()
