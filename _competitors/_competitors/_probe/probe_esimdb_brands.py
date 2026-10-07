# -*- coding: utf-8 -*-
"""Probe: do these 5 brands exist on esimdb? One page each, print plan count."""
from playwright.sync_api import sync_playwright

UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/148.0.0.0 Safari/537.36")

BRANDS = ["nomad", "jetpac", "gigsky", "maya", "quibity"]

with sync_playwright() as p:
    b = p.chromium.launch(headless=True, args=["--disable-blink-features=AutomationControlled"])
    ctx = b.new_context(user_agent=UA, viewport={"width": 1280, "height": 900}, locale="en-US")
    pg = ctx.new_page()
    pg.goto("https://esimdb.com/usa", wait_until="domcontentloaded", timeout=45000)
    pg.wait_for_timeout(5000)
    for brand in BRANDS:
        try:
            r = pg.goto(f"https://esimdb.com/usa/{brand}", wait_until="domcontentloaded", timeout=35000)
            pg.wait_for_timeout(3000)
            status = r.status if r else 0
            h1 = pg.evaluate("() => document.querySelector('h1')?.innerText.trim() || null")
            cards = len(pg.query_selector_all("div.w-full.bg-white.rounded-xl"))
            tabs = pg.evaluate("()=>[...document.querySelectorAll('button')].map(b=>b.innerText.trim()).filter(t=>/^(All|Single|Multiple)/.test(t))")
            print(f"{brand:10s} HTTP {status}  cards={cards:3d}  h1={h1!r}  tabs={tabs}")
        except Exception as e:
            print(f"{brand:10s} ERROR {str(e)[:120]}")
    b.close()
