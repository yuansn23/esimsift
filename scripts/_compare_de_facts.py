# -*- coding: utf-8 -*-
"""批 E 前置：导出 50 个 compare 国家页的德语正文所需的全部事实数字（现算）。

口径（与 content/en/compare/*.md 正文一致，逐页复现验证）：
  - total_plans       = 所有品牌在该 ISO 下的方案总数
  - unlimited_plans   = 其中 type=='unlimited' 的数量
  - provider_count    = 有该 ISO 方案的品牌数
  - cheapest_entry    = 全站最低价方案（价格升序，同价取 gb 小者 -> 英语正文的「入口价」）
  - best_rate         = 最低 $/GB（price / (gb 或 gb_unlimited_equiv)）
  - entry_at_rate_mb  = cheapest_entry.price / best_rate * 1024  （「同样的钱在最优费率下能买多少」）
  - cheapest_unlim    = 最低日费 unlimited 方案（price / days）

用法：python -X utf8 scripts/_compare_de_facts.py [--json out.json]
"""
from __future__ import annotations

import argparse
import json
import pathlib
import tomllib

ROOT = pathlib.Path(__file__).resolve().parents[1]
D = ROOT / "data"

countries = tomllib.loads((D / "countries.toml").read_text(encoding="utf-8"))
providers = tomllib.loads((D / "providers.toml").read_text(encoding="utf-8"))
carriers = tomllib.loads((D / "carriers.toml").read_text(encoding="utf-8"))
plans = {f.stem: tomllib.loads(f.read_text(encoding="utf-8"))
         for f in sorted((D / "plans").glob("*.toml"))}

MB_PER_GB = 1024.0


def collect(iso: str) -> dict:
    rows: list[dict] = []
    for pk, pdata in plans.items():
        block = pdata.get(iso)
        if not block or not block.get("plans"):
            continue
        for p in block["plans"]:
            rows.append({
                "brand": pk,
                "name": p["name"],
                "gb": float(p.get("gb", 0)),
                "days": int(p.get("days", 0)),
                "type": p.get("type", "data"),
                "price": float(p["price"]),
            })
    if not rows:
        return {}

    total = len(rows)
    unlimited = [r for r in rows if r["type"] == "unlimited"]
    metered = [r for r in rows if r["type"] != "unlimited"]

    cheapest_entry = min(rows, key=lambda r: (r["price"], r["gb"]))

    def rate(r: dict) -> float:
        return r["price"] / r["gb"] if r["gb"] > 0 else float("inf")

    best_rate_row = min(metered, key=lambda r: (rate(r), r["price"]))
    best_rate = rate(best_rate_row)

    unlim_daily = sorted(
        ({"brand": r["brand"], "name": r["name"], "days": r["days"],
          "price": r["price"], "per_day": r["price"] / r["days"]}
         for r in unlimited if r["days"] > 0),
        key=lambda r: (r["per_day"], r["price"]),
    )
    cheapest_unlim = unlim_daily[0] if unlim_daily else None

    entry_at_rate_mb = cheapest_entry["price"] / best_rate * MB_PER_GB if best_rate else 0.0
    breakeven_gb_day = (cheapest_unlim["per_day"] / best_rate) if (cheapest_unlim and best_rate) else 0.0

    c = countries[iso]
    cprof = carriers.get(iso, {}).get("profiles", [])
    return {
        "iso": iso,
        "slug": c["slug"],
        "name": c["name"],
        "region": c["region"],
        "neighbors": c.get("neighbors", []),
        "neighbor_names": [countries[n]["name"] for n in c.get("neighbors", []) if n in countries],
        "kyc_required": bool(c.get("kyc_required")),
        "country_carriers": c.get("carriers", []),
        "total_plans": total,
        "unlimited_plans": len(unlimited),
        "metered_plans": len(metered),
        "provider_count": len({r["brand"] for r in rows}),
        "cheapest_entry": cheapest_entry,
        "best_rate_row": best_rate_row,
        "best_rate": round(best_rate, 4),
        "entry_at_rate_mb": round(entry_at_rate_mb),
        "cheapest_unlim": cheapest_unlim,
        "breakeven_gb_day": round(breakeven_gb_day, 1),
        "carrier_profiles": [
            {"name": p["name"], "tech": p.get("tech"), "speed_min": p.get("speed_min"),
             "speed_top": p.get("speed_top"), "note": p.get("note")}
            for p in cprof
        ],
        "unlim_top3": unlim_daily[:3],
    }


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--json")
    args = ap.parse_args()
    out: dict[str, dict] = {}
    for iso in countries:
        s = collect(iso)
        if s:
            out[iso] = s

    for iso, s in out.items():
        ce, br, cu = s["cheapest_entry"], s["best_rate_row"], s["cheapest_unlim"]
        print(f"── {iso} {s['slug']:22} total={s['total_plans']:>3} unl={s['unlimited_plans']:>3} "
              f"prov={s['provider_count']}  kyc={s['kyc_required']}")
        print(f"   entry  : {ce['brand']:7} {ce['name'][:38]:38} ${ce['price']:.2f} "
              f"({ce['gb']}GB/{ce['days']}d) -> @rate {s['entry_at_rate_mb']:.0f}MB")
        print(f"   rate   : {br['brand']:7} {br['name'][:38]:38} ${s['best_rate']:.2f}/GB "
              f"({br['gb']}GB/{br['days']}d)")
        if cu:
            print(f"   unlim  : {cu['brand']:7} {cu['name'][:38]:38} ${cu['per_day']:.2f}/day "
                  f"; breakeven {s['breakeven_gb_day']}GB/day")
        print(f"   nets   : " + " | ".join(
            f"{p['name']}({p['tech']} {p['speed_min']}-{p['speed_top']})" for p in s["carrier_profiles"]))
        print(f"   nbr    : {', '.join(s['neighbor_names']) or '-'}")

    if args.json:
        pathlib.Path(args.json).write_text(
            json.dumps(out, ensure_ascii=False, indent=1), encoding="utf-8", newline="\n")
        print(f"\nwrote {args.json}  ({len(out)} countries)")


if __name__ == "__main__":
    main()
