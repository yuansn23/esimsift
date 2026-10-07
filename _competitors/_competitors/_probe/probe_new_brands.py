# -*- coding: utf-8 -*-
"""Probe: do bensim/roamless/firsty/gomoworld (+slug variants) exist on esimdb?
One page each on /usa, print status / plan-card count / h1 / tab labels.
Slug variants included so we learn the exact URL segment per brand."""
from playwright.sync_api import sync_playwright

UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/148.0.0.0 Safari/537.36")

CANDIDATES = [
    "bensim", "ben-sim",
    "roamless",
    "firsty",
    "gomoworld", "gomo", "gomo-world",
]

with sync_playwright() as p:
    b = p.chromium.launch(headless=True, args=["--disable-blink-features=AutomationControlled"])
    ctx = b.new_context(user_agent=UA, viewport={"width": 1280, "height": 900}, locale="en-US")
    pg = ctx.new_page()
    pg.goto("https://esimdb.com/usa", wait_until="domcontentloaded", timeout=45000)
    pg.wait_for_timeout(5000)
    for slug in CANDIDATES:
        try:
            r = pg.goto(f"https://esimdb.com/usa/{slug}", wait_until="domcontentloaded", timeout=35000)
            pg.wait_for_timeout(3500)
            status = r.status if r else 0
            if "Human Verification" in pg.content():
                pg.wait_for_timeout(10000)
            h1 = pg.evaluate("() => { const h=document.querySelector('h1'); return h?(h.innerText||'').trim():null }")
            cards = len(pg.query_selector_all("div.w-full.bg-white.rounded-xl"))
            print(f"{slug:12s} HTTP {status}  cards={cards:3d}  h1={h1!r}", flush=True)
        except Exception as e:
            print(f"{slug:12s} ERROR {str(e)[:120]}", flush=True)
        pg.wait_for_timeout(2000)
    b.close()
