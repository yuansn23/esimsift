# -*- coding: utf-8 -*-
"""1) Fetch firsty /plans/classic (definitive price ladder).
2) Sniff BNESIM /plans/jp/ network traffic for the plans API."""
import json
import re
from pathlib import Path

from playwright.sync_api import sync_playwright

P = Path(__file__).resolve().parent
OUT = Path(r"C:\Users\27197\WorkBuddy\2026-10-04-19-19-25\_probe_result.txt")


def log(*a):
    OUT.open("a", encoding="utf-8").write(" ".join(str(x) for x in a) + "\n")


UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/148.0.0.0 Safari/537.36")

with sync_playwright() as p:
    b = p.chromium.launch(headless=True, args=["--disable-blink-features=AutomationControlled"])
    ctx = b.new_context(user_agent=UA, viewport={"width": 1280, "height": 900}, locale="en-US")
    pg = ctx.new_page()

    # --- 1. firsty classic price ladder ---
    try:
        r = pg.goto("https://www.firsty.app/plans/classic", wait_until="domcontentloaded", timeout=45000)
        pg.wait_for_timeout(6000)
        html = pg.content()
        (P / "firsty_classic_plans.html").write_text(html, encoding="utf-8")
        log(f"--- firsty /plans/classic HTTP {r.status if r else 0}, {len(html)} chars")
        seen = set()
        for m in re.finditer(r"(\d+(?:\.\d+)?)\s*(?:GB|gb)[^<>{}]{0,120}?[€$]\s?(\d+(?:\.\d+)?)", html):
            pair = f"{m.group(1)}GB = EUR {m.group(2)}"
            if pair in seen:
                continue
            seen.add(pair)
            log("   ", pair, "| ctx:", re.sub(r"\s+", " ", m.group(0))[:160])
    except Exception as e:
        log("firsty classic ERROR", str(e)[:120])

    # --- 2. bnesim network sniff ---
    hits = []

    def on_response(resp):
        url = resp.url
        if any(t in url for t in ("api", "plan", "product", "offer", "package", "bundle", "graphql")) \
                and "fonts.googleapis" not in url and "gtag" not in url:
            try:
                body = resp.text() if "json" in (resp.headers.get("content-type") or "") else ""
            except Exception:
                body = ""
            hits.append((url, resp.status, len(body), body[:200]))

    pg.on("response", on_response)
    try:
        r = pg.goto("https://www.bnesim.com/plans/jp/", wait_until="domcontentloaded", timeout=45000)
        pg.wait_for_timeout(12000)
        # scroll to trigger lazy loads
        for y in (0, 800, 1600, 2400):
            pg.evaluate(f"window.scrollTo(0,{y})")
            pg.wait_for_timeout(1200)
        pg.wait_for_timeout(3000)
        log(f"--- bnesim /plans/jp/ HTTP {r.status if r else 0}, sniffed {len(hits)} candidate responses")
        for url, st, ln, head in hits[:30]:
            log(f"    {st} {ln:6d}B  {url[:130]}")
            if head and ("plan" in head.lower() or "price" in head.lower() or "gb" in head.lower()):
                log(f"        HEAD: {head[:180]}")
    except Exception as e:
        log("bnesim sniff ERROR", str(e)[:120])
    b.close()
