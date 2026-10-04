#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""重写 8 个品牌 Hub 页的 title / description（2026-10-04 第二轮 SEO 改造）。

用户口径（本轮已确认）：
  · title **不放套餐数量、不放价格** —— 沿用 2026-10-04 既定规则（数字会随数据过时）。
    只保留意图词：Review / Plans / Prices / Unlimited / 5G / Value / Compared / Worth It。
  · 套餐数量改由 description 与 H1 承担（这两处本来就承载数字与价格锚点）。
  · description 必须 120-140 字符且含 "eSIM Sift"（scripts/audit_meta.py 规则）。
  · 改写动机：原 title 复述品牌营销话术（「Unlimited 5G From $9.50」），却与本页
    自己算出的「0 国最便宜」自相矛盾。新口径一律是**独立比价**口吻。

description 里的套餐数（985/915/298/1181/1791/471/483/1652）取自 data/plans/*.toml，
与页面上模板渲染的 $totalPlans 同源。脚本会重新数一遍并断言一致 —— 数字对不上就中止。
"""
import io
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CONTENT = ROOT / "content" / "en" / "esim-providers"

# brand -> (title, description)
NEW = {
    "airalo": (
        "Airalo eSIM Review 2026: Plans, Prices and Real Value",
        "eSIM Sift compared all 985 Airalo plans: hotspot rules, 5G support, "
        "fair-use caps and the brands undercutting it in 50 markets.",
    ),
    "alosim": (
        "aloSIM eSIM Review 2026: Plans and Value Compared",
        "eSIM Sift ranked all 915 aloSIM plans by price per GB, hotspot rules and "
        "5G support, plus the brand that wins in each of 50 markets.",
    ),
    "holafly": (
        "Holafly eSIM Review 2026: Is Unlimited Data Worth It?",
        "eSIM Sift tested all 298 Holafly plans: daily unlimited rates, the hotspot "
        "cap, fair-use throttling and the metered rivals that beat it.",
    ),
    "roami": (
        "Roami eSIM Review 2026: Cheap Plans, Honest Verdict",
        "eSIM Sift reviewed all 1181 Roami plans: hotspot rules, 5G support, the "
        "web20 code and where Roami really is cheapest in 50 markets.",
    ),
    "roamic": (
        "Roamic eSIM Review 2026: Unlimited Value in Europe?",
        "eSIM Sift reviewed all 1791 Roamic plans: unlimited tiers, hotspot rules, "
        "5G support and the rivals that undercut it market by market.",
    ),
    "saily": (
        "Saily eSIM Review 2026: Plans, Prices and Who Wins",
        "eSIM Sift compared all 471 Saily plans: hotspot rules, 5G support, the "
        "VEEPEE25 code and which brands beat it on price per GB.",
    ),
    "ubigi": (
        "Ubigi eSIM Review 2026: 5G Data and the Real Cost",
        "eSIM Sift reviewed all 483 Ubigi plans from Transatel: 5G support, "
        "hotspot rules, the WELCOME10 code and where rivals sell cheaper.",
    ),
    "yesim": (
        "Yesim eSIM Review 2026: Pay-As-You-Go Value Check",
        "eSIM Sift reviewed all 1652 Yesim plans: pay-as-you-go rates, hotspot "
        "rules, 5G support and the destinations where Yesim wins.",
    ),
}


def plan_count(brand: str) -> int:
    import tomllib
    with open(ROOT / "data" / "plans" / ("%s.toml" % brand), "rb") as f:
        d = tomllib.load(f)
    return sum(len(b.get("plans") or []) for b in d.values())


def main() -> int:
    errors = []
    seen_titles = {}

    for brand, (title, desc) in NEW.items():
        # ---- 规则断言 ----
        if not (48 <= len(title) <= 54):
            errors.append("%s: title 长度 %d 不在 48-54" % (brand, len(title)))
        if not (120 <= len(desc) <= 140):
            errors.append("%s: desc 长度 %d 不在 120-140" % (brand, len(desc)))
        if "eSIM Sift" in title:
            errors.append("%s: title 含站名（仅首页可含）" % brand)
        if "eSIM Sift" not in desc:
            errors.append("%s: desc 缺 'eSIM Sift'" % brand)
        if "$" in title:
            errors.append("%s: title 含价格（用户口径禁止）" % brand)
        # 允许 2026 与 5G；其余裸数字视为「套餐数/价格」残留
        for num in re.findall(r"\d+", title):
            if num in ("2026", "5"):
                continue
            errors.append("%s: title 含数字 %s（用户口径禁止）" % (brand, num))
        if title in seen_titles:
            errors.append("%s: title 与 %s 重复" % (brand, seen_titles[title]))
        seen_titles[title] = brand

        # ---- description 里的套餐数必须与数据层一致 ----
        n = plan_count(brand)
        m = re.search(r"all (\d+)", desc)
        if not m:
            errors.append("%s: desc 未含套餐数" % brand)
        elif int(m.group(1)) != n:
            errors.append("%s: desc 写 %s 个套餐，数据层实际 %d 个"
                          % (brand, m.group(1), n))

    if errors:
        print("ABORT —— 规则未通过：")
        for e in errors:
            print("  ✗", e)
        return 1

    for brand, (title, desc) in NEW.items():
        body = '---\ntitle: %s\ndescription: %s\n---\n' % (
            _toml_str(title), _toml_str(desc))
        p = CONTENT / ("%s.md" % brand)
        with io.open(p, "w", encoding="utf-8", newline="\n") as f:
            f.write(body)
        print("  写入 %-7s T=%2d D=%3d (%d plans)" % (brand, len(title), len(desc),
                                                     plan_count(brand)))

    print("OK: 8 个品牌页 front matter 重写完成")
    return 0


def _toml_str(s: str) -> str:
    """输出 TOML 双引号字符串（值与源模板一致时用 ASCII 直引号）。"""
    return '"%s"' % s.replace("\\", "\\\\").replace('"', '\\"')


if __name__ == "__main__":
    sys.exit(main())
