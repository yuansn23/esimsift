#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""给 data/providers.toml 的 8 个品牌顶层块补 profile_checked（品牌档案核实日）。

它解决什么
    品牌 Hub 页的内容 = 价格数据（data/plans/<key>.toml）**加上** 品牌档案
    （data/providers.toml 的 strengths / weaknesses / info / policy / promo）。
    在补这个字段之前，只改品牌简介或热点/FUP 政策，任何日期都不会动 ——
    页面上「Last updated」还停在价格快照日。

日期取值的依据（2026-10-04 逐个核对 providers.toml 内的注释）
    · 品牌档案事实（HQ / 法人 / 官网 / 双商店 / 客服 / 退款 / 目的地数）：2026-10-01 三路代理核验
    · policy 块（热点 / FUP / 充值 / 语音）：2026-10-04（文件内注明「核实口径（2026-10-04）一次；
      2026-10-04 二次补齐 roami / roamic」）
    · trustpilot 档案链接：2026-10-04 逐个核实
    三个日期取最新 ⇒ **八个品牌统一为 2026-10-04**（roami 无 Trustpilot 档案，
    但它的 policy 是 10-04 补齐的，同样落在 10-04）。

    后续维护：任何一次改了某个品牌块的档案事实，就把该品牌的 profile_checked 改成当天。
    直接手改 TOML 即可（比 plans 的 checked 简单，不需要脚本）。

用法
    python scripts/_patch_profile_checked.py --dry-run
    python scripts/_patch_profile_checked.py
"""
from __future__ import annotations

import argparse
import io
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
SRC = ROOT / "data" / "providers.toml"

BRANDS = ["roami", "airalo", "holafly", "saily", "yesim", "ubigi", "roamic", "alosim"]
DATE = "2026-10-04"

HEADER = re.compile(r"^\[(" + "|".join(BRANDS) + r")\]\s*$")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    with io.open(SRC, "r", encoding="utf-8", newline="") as f:
        text = f.read()
    if "\r\n" in text:
        sys.exit("错误：providers.toml 含 CRLF，先统一为 LF")

    lines = text.split("\n")
    out: list[str] = []
    seen: set[str] = set()
    inserted = 0
    for ln in lines:
        m = HEADER.match(ln)
        out.append(ln)
        if m:
            brand = m.group(1)
            if brand in seen:
                sys.exit(f"错误：{brand} 顶层块出现两次")
            seen.add(brand)
            out.append(f'profile_checked = "{DATE}"   # 品牌档案（简介/政策/官网事实）核对日')
            inserted += 1

    missing = [b for b in BRANDS if b not in seen]
    if missing:
        sys.exit(f"错误：这些品牌没有顶层块：{', '.join(missing)}")

    print(f"命中顶层块 {inserted}/8，目标日期 {DATE}")
    if args.dry_run:
        print("（预演，未写入）")
        return 0

    with io.open(SRC, "w", encoding="utf-8", newline="") as f:
        f.write("\n".join(out))
    print(f"已写入 {SRC.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
