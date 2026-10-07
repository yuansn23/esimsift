# -*- coding: utf-8 -*-
"""Fetch + quick-inspect: bnesim /plans/jp/ and firsty /japan-esim (default lang)."""
import re
from pathlib import Path

from playwright.sync_api import sync_playwright

P = Path(__file__).resolve().parent
OUT = Path(r"C:\Users\27197\WorkBuddy\2026-10-04-19-19-25\_probe_result.txt")


def log(*a):
    OUT.open("a", encoding="utf-8").write(" ".join(str(x) for x in a) + "\n")


UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/148.0.0.0 Safari/537.36")

TARGETS = [
    ("bnesim_japan_plans.html", "https://www.bnesim.com/plans/jp/"),
    ("firsty_japan_esim.html", "https://www.firsty.app/japan-esim"),
]

with sync_playwright() as p:
    b = p.chromium.launch(headless=True, args=["--disable-blink-features=AutomationControlled"])
    ctx = b.new_context(user_agent=UA, viewport={"width": 1280, "height": 900}, locale="en-US")
    pg = ctx.new_page()
    for fname, url in TARGETS:
        try:
            r = pg.goto(url, wait_until="domcontentloaded", timeout=45000)
            pg.wait_for_timeout(7000)
            status = r.status if r else 0
            html = pg.content()
            (P / fname).write_text(html, encoding="utf-8")
            log(f"--- {fname}: HTTP {status}, {len(html)} chars")
            # prices
            seen = []
            for m in re.finditer(r"[€$]\s?\d+([.,]\d{1,2})?", html):
                s = max(0, m.start() - 90)
                ctx_s = re.sub(r"\s+", " ", html[s:m.end() + 50])
                if not seen or seen[-1][1] != ctx_s:
                    seen.append((m.group(0), ctx_s))
            log(f"    price hits: {len(seen)}")
            for pr, c in seen[:8]:
                log(f"    {pr} <- {c[-130:]}")
            # ld+json types
            for i, m in enumerate(re.finditer(r'<script[^>]*type="application/ld\+json"[^>]*>(.*?)</script>', html, re.S)):
                body = m.group(1).strip()
                log(f"    ld+json #{i}: {body[:110]}")
        except Exception as e:
            log(f"--- {fname} ERROR {str(e)[:140]}")
    b.close()
