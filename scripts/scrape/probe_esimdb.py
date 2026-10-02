#!/usr/bin/env python3
"""Probe: can Playwright chromium pass esimdb's AWS WAF challenge?
Captars page state + all JSON API responses to scrape_tmp/probe/.
Usage: python -X utf8 scripts/scrape/probe_esimdb.py [url]
"""
import json
import sys
from pathlib import Path

from playwright.sync_api import sync_playwright

OUT = Path(__file__).resolve().parent / "probe"
OUT.mkdir(parents=True, exist_ok=True)

URL = sys.argv[1] if len(sys.argv) > 1 else "https://esimdb.com/usa/airalo"

with sync_playwright() as p:
    browser = p.chromium.launch(
        headless=True,
        args=["--disable-blink-features=AutomationControlled"],
    )
    ctx = browser.new_context(
        user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/148.0.0.0 Safari/537.36",
        viewport={"width": 1366, "height": 900},
        locale="en-US",
    )
    page = ctx.new_page()

    json_blobs = []

    def on_response(resp):
        url = resp.url
        ct = resp.headers.get("content-type", "")
        if any(k in ct for k in ("json", "javascript")) and "esimdb" in url:
            try:
                body = resp.text()
            except Exception:
                return
            if body and len(body) > 200:
                json_blobs.append({"url": url, "ct": ct, "size": len(body), "body": body})

    page.on("response", on_response)

    try:
        page.goto(URL, wait_until="domcontentloaded", timeout=45000)
        page.wait_for_timeout(6000)  # let WAF challenge JS run + reload
        title = page.title()
        content = page.content()
        (OUT / "page.html").write_text(content, encoding="utf-8")
        print(f"TITLE: {title!r}")
        print(f"HTML size: {len(content)}")
        print(f"WAF challenge visible: {'Human Verification' in content or 'awswaf' in content.lower()}")
        # visible text snippet
        txt = page.evaluate("() => document.body.innerText.slice(0, 600)")
        print("VISIBLE TEXT HEAD:\n" + txt)
    except Exception as e:
        print(f"NAV FAIL: {str(e)[:300]}")
        browser.close()
        sys.exit(1)

    print(f"\n{len(json_blobs)} JSON/JS responses captured:")
    seen = set()
    for b in json_blobs:
        key = b["url"].split("?")[0]
        if key in seen:
            continue
        seen.add(key)
        print(f"  {b['size']:>8} {b['ct'][:24]:24} {b['url'][:120]}")
        # save unique-looking api payloads
        if "/api/" in b["url"] or "graphql" in b["url"]:
            fn = b["url"].split("?")[0].rstrip("/").replace("/", "_")[-80:] + ".json"
            (OUT / fn).write_text(b["body"], encoding="utf-8")
            print(f"           -> saved {fn}")

    browser.close()
print("DONE")
