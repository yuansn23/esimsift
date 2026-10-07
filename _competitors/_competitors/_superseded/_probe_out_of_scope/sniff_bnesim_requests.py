# -*- coding: utf-8 -*-
"""Capture full BNESIM api requests (method/url/params/body) while loading /plans/jp/."""
from pathlib import Path

from playwright.sync_api import sync_playwright

OUT = Path(r"C:\Users\27197\WorkBuddy\2026-10-04-19-19-25\_probe_result.txt")
P = Path(__file__).resolve().parent


def log(*a):
    OUT.open("a", encoding="utf-8").write(" ".join(str(x) for x in a) + "\n")


UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/148.0.0.0 Safari/537.36")

with sync_playwright() as p:
    b = p.chromium.launch(headless=True, args=["--disable-blink-features=AutomationControlled"])
    ctx = b.new_context(user_agent=UA, viewport={"width": 1280, "height": 900}, locale="en-US")
    pg = ctx.new_page()

    def on_request(req):
        if "api.bnesim.com" in req.url:
            hdr = {k.lower(): v for k, v in req.headers.items()}
            interesting = {k: hdr[k] for k in ("token", "authorization", "x-api-key", "device-id", "platform", "content-type") if k in hdr}
            log("REQ", req.method, req.url)
            if req.post_data:
                log("   BODY:", req.post_data[:300])
            log("   HDRS:", interesting)

    pg.on("request", on_request)
    pg.goto("https://www.bnesim.com/plans/jp/", wait_until="domcontentloaded", timeout=45000)
    pg.wait_for_timeout(12000)
    b.close()
