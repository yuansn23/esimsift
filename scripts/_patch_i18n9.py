#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""第二十四轮（品牌 Hub 页）i18n 补丁：新增本页全部文案键，en/de 两侧同值同序。

为什么要脚本而不是手改两个 945 行的文件：
  check_i18n.py 会逐个 key 比对 en.toml 与 de.toml，手改必然漏。
  脚本跑完自带断言（每个 key 两侧都命中），漏了当场失败。

约定（沿用仓库既有状态）：
  · 德语值暂为英文占位 —— 与 compare_provider__* / compare_single__* 同一状态，
    德语站正式启动时统一翻。
  · 值一律 json.dumps(ensure_ascii=False)，因为 check_i18n 用 json.loads 读它。
  · 文件按 key 排序输出，保持 i18n_extract.py 的形态。
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
EN = ROOT / "i18n" / "en.toml"
DE = ROOT / "i18n" / "de.toml"

# ── HTML 侧（用 {{ .x }} 占位，模板调用时传 dict）──────────────────────────
NEW_HTML = [
    ("esim_providers_single__last_updated", "Last updated {{ .date }}"),

    ("esim_providers_single__reality_eyebrow", "Beyond the price tag"),
    ("esim_providers_single__reality_h2", "{{ .brand }} hotspot 5G and fair-use rules"),
    ("esim_providers_single__reality_lead",
     "Price is only half the decision. These four terms decide whether a {{ .brand }} plan actually works on the trip you are taking."),
    ("esim_providers_single__reality_voice",
     "Every plan is data-only — you keep your own number for calls and texts."),
    ("esim_providers_single__reality_5g_count", "5G in {{ .n5g }} of {{ .total }} markets"),
    ("esim_providers_single__reality_5g_text",
     "5G comes from the local networks rather than the brand. We profile {{ .n }} carrier networks across the markets where {{ .brand }} sells, and 5G is live on them wherever the country has rolled it out."),
    ("esim_providers_single__reality_4g_note",
     "LTE only in {{ .list }} — no brand can sell you 5G there."),
    ("esim_providers_single__reality_5g_link",
     "Per-country speeds and coverage are on the"),
    ("esim_providers_single__fair_use_audit", "fair-use audit"),

    ("esim_providers_single__who_beats_eyebrow", "Alternatives by market"),
    ("esim_providers_single__who_beats_h2",
     "Who beats {{ .brand }} on price and where to go instead"),
    ("esim_providers_single__who_beats_lead",
     "Another brand sells a comparable plan for less in {{ .n }} of the {{ .total }} markets where we track {{ .brand }}. We match like for like — the same data allowance and the same validity — so every gap below is a real price difference rather than a bigger bucket measured against a smaller one."),
    ("esim_providers_single__who_beats_col_mine", "{{ .brand }} cheapest"),
    ("esim_providers_single__who_beats_col_rival", "Cheaper rival"),
    ("esim_providers_single__who_beats_col_rival_price", "Rival price"),
    ("esim_providers_single__who_beats_col_gap", "Gap"),
    ("esim_providers_single__who_beats_caveat",
     "How we matched: first the same data allowance and validity as {{ .brand }}'s cheapest plan in that market; if no rival sells that exact combination, the cheapest rival plan with at least as much data; only when neither exists do we fall back to entry price against entry price. Both prices are dated list prices before promo codes and taxes."),
    ("esim_providers_single__who_beats_route",
     "The brand that beats {{ .brand }} most often is {{ .rival }}, ahead in {{ .n }} of those markets. Read its review or open a full matchup"),
    ("esim_providers_single__who_beats_none",
     "In all {{ .total }} markets where we track {{ .brand }}, no other brand we compare sells a comparable plan for less. That is uncommon and worth knowing before you shop around — but it is a price result, not a recommendation for your trip."),

    ("esim_providers_single__network_eyebrow", "Network reality"),
    ("esim_providers_single__network_h2", "Which local networks {{ .brand }} rides on"),
    ("esim_providers_single__network_lead",
     "An eSIM does not build towers. In every market {{ .brand }} buys capacity from that country's national operators, so the networks below are the same ones every reseller in that country uses. We profile {{ .n }} of them."),
    ("esim_providers_single__network_5g_title", "5G is live in {{ .n5g }} of {{ .total }} markets"),
    ("esim_providers_single__network_5g_cheap_lead",
     "Markets where 5G is live and {{ .brand }} is also the cheapest provider we track:"),
    ("esim_providers_single__network_5g_cheap_none",
     "5G is live in these markets, but {{ .brand }} is not the cheapest provider in any of them — check the price table above before assuming the fastest network comes at the best price."),
    ("esim_providers_single__network_lte_title", "Where 5G is not available at all"),
    ("esim_providers_single__network_lte_lead",
     "Host networks in these markets run LTE only, so no eSIM on any brand can be faster than that:"),
    ("esim_providers_single__network_lte_none",
     "Every market we track has live 5G on at least one host network, so coverage rather than generation is the thing to check locally."),
    ("esim_providers_single__network_footnote",
     "Speeds and generations come from our per-country network profiles, built from operator material and third-party measurement."),

    ("esim_providers_single__h2h_eyebrow", "Head to head"),
    ("esim_providers_single__h2h_h2", "The two brands closest to {{ .brand }}"),
    ("esim_providers_single__h2h_lead",
     "These two are not picked by hand. We rank every rival by how close its record is to {{ .brand }}'s number of cheapest-market wins and show the two nearest. The three lines below are the numbers that actually separate them."),
    ("esim_providers_single__h2h_count",
     "{{ .rival }} is the cheapest provider in {{ .n }} of the {{ .total }} markets where it sells, against {{ .mine }} for {{ .brand }}."),
    ("esim_providers_single__h2h_entry",
     "Its entry price is ${{ .price }} against ${{ .mine }} for {{ .brand }}."),
    ("esim_providers_single__h2h_value",
     "Its best value on our $/GB measure is ${{ .price }}/GB against ${{ .mine }}/GB."),
    ("esim_providers_single__h2h_no_value",
     "It sells unlimited plans only, so it has no $/GB figure to compare."),
    ("esim_providers_single__h2h_full", "Full {{ .brand }} vs {{ .rival }} comparison"),

    ("esim_providers_single__calc_eyebrow", "Trip calculator"),
    ("esim_providers_single__calc_h2", "What {{ .brand }} would cost for your trip"),
    ("esim_providers_single__calc_lead",
     "Pick a destination, a trip length and your expected daily use. We price {{ .brand }}'s own catalogue against the cheapest plans in the same market. A plan qualifies when its validity covers the trip and its data covers your need, and unlimited plans always qualify."),
    ("esim_providers_single__calc_dest_label", "Where are you going"),
    ("esim_providers_single__calc_days_label", "Trip length"),
    ("esim_providers_single__calc_gb_label", "Data per day"),
    ("esim_providers_single__calc_gb_option", "{{ .n }} GB"),
    ("esim_providers_single__calc_noscript",
     "This calculator needs JavaScript. The same market benchmarks are in the price tables and the alternatives table further up this page."),
    ("esim_providers_single__calc_more",
     "The full cross-brand version, with a usage estimator that turns app hours into gigabytes, is on the <a href=\"/tools/\">trip cost calculator</a>."),

    ("esim_providers_single__reading_eyebrow", "Keep reading"),
    ("esim_providers_single__reading_h2", "What else to check before you buy {{ .brand }}"),
    ("esim_providers_single__reading_reviews_h3", "What {{ .brand }} customers say elsewhere"),
    ("esim_providers_single__reading_reviews_note",
     "We do not republish a star rating for {{ .brand }}. The same brand scores differently depending on which Trustpilot domain you land on, the figures move weekly, and an average hides the only part that predicts your trip — the one-star reviews, which cluster on the eSIM failing to connect after landing. Read those, filter for your own destination and weight the last two months. Every number on this page is dated and reproducible; a borrowed score would not be."),
    ("esim_providers_single__reading_reviews_link", "Read {{ .brand }} reviews on Trustpilot"),
    ("esim_providers_single__reading_guides_h3", "Guides for your trip"),
    ("esim_providers_single__reading_guide_region", "Best eSIM for {{ .region }}"),
    ("esim_providers_single__reading_guide_install", "How to install an eSIM"),
    ("esim_providers_single__reading_guide_compat", "Is your phone eSIM-ready"),
    ("esim_providers_single__reading_guide_dualsim", "Using an eSIM alongside your own SIM"),
    ("esim_providers_single__reading_data_h3", "Where these numbers come from"),
    ("esim_providers_single__reading_data_note",
     "Every figure here is computed from our price database — {{ .plans }} {{ .brand }} plans across {{ .countries }} destinations, list prices in USD before promo codes and taxes, rebuilt {{ .date }}. Rankings are sort positions, not editorial scores."),
    ("esim_providers_single__reading_fup", "Fair-use audit across every unlimited plan"),
    ("esim_providers_single__reading_unlimited", "The unlimited eSIM league"),
    ("esim_providers_single__reading_index", "The eSIM price index"),
]

# ── JS 侧（用单花括号占位；模板用无参 i18n 取原串，塞进 data-msg-* 属性）────
NEW_JS = [
    ("esim_providers_single__calc_card_mine", "Cheapest {brand} plan that fits"),
    ("esim_providers_single__calc_card_field", "Cheapest metered plan in this market"),
    ("esim_providers_single__calc_card_unl", "Cheapest unlimited plan in this market"),
    ("esim_providers_single__calc_plan_line", "{price} for {data} over {days} days"),
    ("esim_providers_single__calc_nocover",
     "No single plan covers {need} GB in {days} days — the largest tier is as far as one purchase goes."),
    ("esim_providers_single__calc_na", "Not sold in this market"),
    ("esim_providers_single__calc_need", "A {days}-day trip at {gb} GB a day needs about {need} GB."),
    ("esim_providers_single__calc_v_floor",
     "{brand} lands at ${pergb}/GB against a market floor of ${floor}/GB from {floorBrand} ({floorData})."),
    ("esim_providers_single__calc_v_above", "About {pct}% above the floor."),
    ("esim_providers_single__calc_v_level", "At or below the floor."),
    ("esim_providers_single__calc_v_unl",
     "Unlimited for {days} days at {price}. The cheapest unlimited plan in this market is {alt} from {altBrand}."),
    ("esim_providers_single__calc_unit_unl", "unlimited"),
    ("esim_providers_single__calc_unit_days", "{n} days"),
]

NEW = NEW_HTML + NEW_JS


def load(path: Path):
    head, body = [], {}
    for line in path.read_text(encoding="utf-8").splitlines():
        s = line.strip()
        if not s or s.startswith("#") or " = " not in line:
            head.append(line)
            continue
        k, v = line.split(" = ", 1)
        try:
            body[k.strip()] = json.loads(v.strip())
        except json.JSONDecodeError:
            print(f"!! 无法解析 {path.name} 的既有值：{line[:70]}")
            sys.exit(1)
    return head, body


def write(path: Path, head, body):
    out = list(head)
    if out and out[-1].strip():
        out.append("")
    for k in sorted(body):
        out.append(f"{k} = {json.dumps(body[k], ensure_ascii=False)}")
    path.write_text("\n".join(out) + "\n", encoding="utf-8", newline="\n")


def main() -> int:
    hits = []
    for path in (EN, DE):
        head, body = load(path)
        before = len(body)
        for k, v in NEW:
            if k in body and body[k] != v:
                print(f"   ~ 覆盖 {path.name}: {k}")
            body[k] = v
        write(path, head, body)
        hits.append((path.name, before, len(body)))
        print(f"{path.name}: {before} -> {len(body)} key (+{len(body) - before})")

    # 断言：每组改动都真的落盘（上一轮踩过「替换成功但没插入」的坑）
    for path in (EN, DE):
        txt = path.read_text(encoding="utf-8")
        missing = [k for k, _ in NEW if not re.search(r"^%s = " % re.escape(k), txt, re.M)]
        if missing:
            print(f"!! {path.name} 缺少 {len(missing)} 个 key：{missing[:5]}")
            return 1
    print(f"OK：{len(NEW)} 个 key 在 en/de 两侧全部命中")
    return 0


if __name__ == "__main__":
    sys.exit(main())
