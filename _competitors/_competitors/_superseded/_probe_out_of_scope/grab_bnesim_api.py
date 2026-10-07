# -*- coding: utf-8 -*-
"""Load bnesim /plans/jp/ and save the actual api.bnesim.com response bodies."""
from pathlib import Path

from playwright.sync_api import sync_playwright

P = Path(__file__).resolve().parent
OUT = Path(r"C:\Users\27197\WorkBuddy\2026-10-04-19-19-25\_probe_result.txt")


def log(*a):
    OUT.open("a", encoding="utf-8").write(" ".join(str(x) for x in a) + "\n")


UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/148.0.0.0 Safari/537.36")

WANT = {
    "sim_card_landing_pricing": P / "bnesim_pricing_api.json",
    "country_rates_ext": P / "bnesim_country_rates.json",
    "promo": P / "bnesim_promo.json",
}

saved = []
with sync_playwright() as p:
    b = p.chromium.launch(headless=True, args=["--disable-blink-features=AutomationControlled"])
    ctx = b.new_context(user_agent=UA, viewport={"width": 1280, "height": 900}, locale="en-US")
    pg = ctx.new_page()

    def on_response(resp):
        for key, dest in WANT.items():
            if key in resp.url and dest not in saved:
                try:
                    body = resp.body()
                    dest.write_bytes(body)
                    saved.append(dest)
                    log(f"SAVED {key}: {len(body)} bytes <- {resp.url[:160]}")
                except Exception as e:
                    log(f"SAVE FAIL {key}: {str(e)[:120]}")

    pg.on("response", on_response)
    pg.goto("https://www.bnesim.com/plans/jp/", wait_until="domcontentloaded", timeout=45000)
    pg.wait_for_timeout(15000)
    b.close()

log("done, saved:", [s.name for s in saved])
