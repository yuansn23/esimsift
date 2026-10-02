#!/usr/bin/env python3
"""Pilot verification: diff our scraped esimdb data against airalo.com official site.
Samples N countries. Checks: every official fixed+unlimited plan price appears in our
TOML with matching (gb, days), and reports official plans we lack / extras we have.
"""
import re
import sys
import tomllib
from pathlib import Path

from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[2]
UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/148.0.0.0 Safari/537.36")

# our slug -> (iso, airalo.com country path)
SAMPLES = {
    "united-states": ("US", "united-states-esim"),
    "japan": ("JP", "japan-esim"),
    "italy": ("IT", "italy-esim"),
}


def parse_airalo_page(pg) -> list[tuple[float, int, float]]:
    """Extract (gb, days, price) triples from the currently visible package list."""
    txt = pg.evaluate("() => document.body.innerText")
    i = txt.find("Choose your package")
    if i < 0:
        return []
    seg = txt[i:i + 6000]
    seg = seg.split("Need broader coverage")[0]
    # blocks: "<validity> days\n(<data> GB | Unlimited)\nGB\n$<price>\nUSD"
    plans = []
    for m in re.finditer(
            r"(\d+)\s*days?\s*\n\s*(Unlimited\s+GB|\d+(?:\.\d+)?\s*GB)\s*\n\$(\d+(?:\.\d+)?)", seg, re.I):
        days = int(m.group(1))
        data_txt = m.group(2).strip()
        price = float(m.group(3))
        gb = 0.0 if "unlimited" in data_txt.lower() else float(re.search(r"[\d.]+", data_txt).group())
        plans.append((gb, days, price))
    return plans


def main() -> None:
    ours = tomllib.loads((ROOT / "data" / "plans" / "airalo.toml").read_text(encoding="utf-8"))
    ok = True
    with sync_playwright() as p:
        b = p.chromium.launch(headless=True, args=["--disable-blink-features=AutomationControlled"])
        ctx = b.new_context(user_agent=UA, viewport={"width": 1280, "height": 900}, locale="en-US")
        pg = ctx.new_page()
        for slug, (iso, path) in SAMPLES.items():
            try:
                pg.goto(f"https://www.airalo.com/{path}", wait_until="domcontentloaded", timeout=40000)
                pg.wait_for_timeout(6000)
            except Exception as e:
                print(f"{iso}: NAV FAIL {str(e)[:100]}")
                ok = False
                continue

            official: list[tuple[float, int, float]] = []
            for tab in ("Data / Calls / Texts", "Fixed data", "Unlimited"):
                try:
                    btn = pg.query_selector(f"text={tab}")
                    if btn:
                        btn.click()
                        pg.wait_for_timeout(1500)
                except Exception:
                    pass
                official.extend(parse_airalo_page(pg))

            my_plans = ours.get(iso, {}).get("plans", [])
            # multiset of (gb, days, price) — Change/Change+ tiers share (gb, days)
            from collections import Counter
            my_ms = Counter((float(pl["gb"]), int(pl["days"]), round(float(pl["price"]), 2))
                            for pl in my_plans)
            off_ms = Counter((gb, days, round(price, 2)) for gb, days, price in official)

            print(f"\n=== {iso}: official(data-only tabs) {len(official)} plans, ours {len(my_plans)} ===")
            only_official = off_ms - my_ms
            only_ours = my_ms - off_ms
            matched = sum((my_ms & off_ms).values())
            if only_official:
                ok = False
                for (gb, days, price), n in sorted(only_official.items()):
                    print(f"  OFFICIAL-ONLY: {gb:g}GB/{days}d ${price:.2f} ×{n}")
            # same (gb,days) with different price = real mismatch; otherwise ours
            # simply tracks extra tiers (e.g. Change+ calls/SMS) the tab didn't show
            real_mismatch = 0
            off_by_key = {}
            for gb, days, price in official:
                off_by_key.setdefault((gb, days), set()).add(price)
            for (gb, days, price), n in sorted(only_ours.items()):
                if (gb, days) in off_by_key:
                    print(f"  PRICE DIFF {gb:g}GB/{days}d: ours ${price:.2f} vs official {sorted(off_by_key[(gb, days)])}")
                    ok = False
                    real_mismatch += n
                else:
                    print(f"  ours-extra tier: {gb:g}GB/{days}d ${price:.2f} ×{n} (calls/SMS or promo tier)")
            print(f"  matched {matched}, official-only {sum(only_official.values())}, "
                  f"price-diffs {real_mismatch}, ours-extra {sum(only_ours.values()) - real_mismatch}")
        b.close()

    print("\nPILOT " + ("VERIFIED OK" if ok else "HAS DIFFS — review above"))


if __name__ == "__main__":
    main()
