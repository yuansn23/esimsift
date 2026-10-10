# -*- coding: utf-8 -*-
"""研究栏目 i18n 收口（第 68 轮）—— 把 23 处「英文 + 插值 + 内联 <a>」的拼装句碎片
改成「带占位符的整句」，让德语子页能整句重写而不是在英文语序里填空。

为什么必须做（而不是放着不管）：
  `i18n_extract.collect()` 把「含 {{ }} 插值的英文混排」归为 **frags（WARN）**，
  于是 build 全绿、`check_i18n.py` 只报「89 处拼装句碎片待人工重写」。但德语一旦
  落地，这些碎片就是「英文语序 + 德语词」的洋泾浜 —— 从句语序、介词格、标点全错。
  所以研究栏目要发布德语，这一步必须前移。

三条已实测的 Hugo 行为（` .buildlog/i18n_probe/`，第 68 轮）：
  1. `i18n` 内层按 **text/template** 执行 —— 值里的 `{{ .x }}` **原样插入，不转义**；
     外层 html/template 会转义**整条返回值** ⇒ 值含 HTML（`<a>`）或参数含实体（`&amp;`）
     时**必须 `| safeHTML`**，否则 `&amp;` → `&amp;amp;`（正是 d36 修过的坑）。
  2. 参数是**普通 string** 时内层不转义 ⇒ 需要「与现状同款转义」的参数要在模板侧
     自己处理：国名用 `| htmlEscape`（现状 html/template 文本上下文会转 `&` → `&amp;`）。
  3. `partial` 的 `{{ return }}` 返回普通 string ⇒ `region-label.html` 的输出
     （`Africa &amp; Middle East`）**不能再转义**，只能靠外层 `safeHTML` 放行。

判据（本脚本自证）：
  · 每个 `old` 在目标文件里**恰好 1 次**（0 次且 `new` 已在 ⇒ 视为已应用；否则报错）
  · 23 个新 key 在 en.toml 里**不存在**（重建时先断言，避免静默覆盖）
  · 2 个孤儿 key 各**恰好 1 行**
  · 行尾全程 LF（en.toml / de.toml / 三个模板实测 0 个 CRLF）
  · en.toml 与 de.toml 的 key **顺序严格一致**（追加后仍一致）

用法：python -X utf8 scripts/_patch_research_i18n.py [--dry]
"""
from __future__ import annotations

import json
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]

# ── 1. 模板：old → new（模板里的裸英文碎片 → 带占位符的整句） ────────────────
EDITS: list[tuple[str, str, str]] = [
    # ── fair-use-audit.html ──
    (
        "layouts/research/fair-use-audit.html",
        '{{ $totalUnlimited }} unlimited plans audited',
        '{{ i18n "research_fair_use_audit__n_unlimited_plans_audited" (dict "n" $totalUnlimited) | safeHTML }}',
    ),
    (
        "layouts/research/fair-use-audit.html",
        '+{{ sub (len .notes) 2 }} more variants',
        '{{ i18n "research_fair_use_audit__n_more_variants" (dict "n" (sub (len .notes) 2)) | safeHTML }}',
    ),
    (
        "layouts/research/fair-use-audit.html",
        'All {{ len $d.countries }} countries ranked by best $/GB, with regional averages.',
        '{{ i18n "g_price_index_card_desc" (dict "n" (len $d.countries)) | safeHTML }}',
    ),
    # ── price-index.html ──
    (
        "layouts/research/price-index.html",
        '{{ $n }} countries',
        '{{ i18n "research_price_index__n_countries" (dict "n" $n) | safeHTML }}',
    ),
    (
        "layouts/research/price-index.html",
        'prices checked {{ time.Format ":date_medium" (time .) }}',
        '{{ i18n "g_prices_checked_date" (dict "date" (time.Format ":date_medium" (time .))) | safeHTML }}',
    ),
    (
        "layouts/research/price-index.html",
        'The same ruler, {{ len $d.countries }} times. For every destination we track, this index takes'
        ' the cheapest per-gigabyte rate across all providers and ranks the countries against each other'
        ' — the cheapest places to buy eSIM data, and the most expensive.',
        '{{ i18n "research_price_index__the_same_ruler_n_times_for_every_destination_we_track"'
        ' (dict "n" (len $d.countries)) | safeHTML }}',
    ),
    (
        "layouts/research/price-index.html",
        'cheapest at ${{ printf "%.2f" $cheapest.minPerGB }}/GB',
        '{{ i18n "research_price_index__cheapest_at_price_per_gb"'
        ' (dict "price" (printf "%.2f" $cheapest.minPerGB)) | safeHTML }}',
    ),
    (
        "layouts/research/price-index.html",
        'priciest at ${{ printf "%.2f" $dearest.minPerGB }}/GB',
        '{{ i18n "research_price_index__priciest_at_price_per_gb"'
        ' (dict "price" (printf "%.2f" $dearest.minPerGB)) | safeHTML }}',
    ),
    (
        "layouts/research/price-index.html",
        'cheapest region, avg ${{ printf "%.2f" .avg }}/GB',
        '{{ i18n "research_price_index__cheapest_region_avg_price_per_gb"'
        ' (dict "price" (printf "%.2f" .avg)) | safeHTML }}',
    ),
    (
        "layouts/research/price-index.html",
        '{{ if gt .unlimited 0 }}{{ .unlimited }} plans{{ else }}—{{ end }}',
        '{{ if gt .unlimited 0 }}{{ i18n "research_price_index__n_plans" (dict "n" .unlimited) | safeHTML }}'
        '{{ else }}—{{ end }}',
    ),
    # P161：含 2 个内联 <a>。国名参数必须 htmlEscape（现状 html/template 文本上下文会转 &）。
    (
        "layouts/research/price-index.html",
        'The same gigabyte costs {{ printf "%.1f" $spread }} times more in '
        '<a href="{{ partial "lang-href.html" (printf "/compare/%s/" $dearest.slug) }}"'
        ' class="font-semibold text-brand-700 hover:underline">{{ $dearest.name }}</a> '
        '{{ i18n "research_price_index__than_in" | safeHTML }} '
        '<a href="{{ partial "lang-href.html" (printf "/compare/%s/" $cheapest.slug) }}"'
        ' class="font-semibold text-brand-700 hover:underline">{{ $cheapest.name }}</a> '
        '(${{ printf "%.2f" $cheapest.minPerGB }}/GB vs ${{ printf "%.2f" $dearest.minPerGB }}/GB).'
        ' Destination choice moves the price far more than provider choice does.',
        '{{ i18n "research_price_index__the_same_gigabyte_costs_n_times_more_in" (dict'
        ' "n" (printf "%.1f" $spread)'
        ' "h1" (partial "lang-href.html" (printf "/compare/%s/" $dearest.slug))'
        ' "c1" ($dearest.name | htmlEscape)'
        ' "h2" (partial "lang-href.html" (printf "/compare/%s/" $cheapest.slug))'
        ' "c2" ($cheapest.name | htmlEscape)'
        ' "p1" (printf "%.2f" $cheapest.minPerGB)'
        ' "p2" (printf "%.2f" $dearest.minPerGB)) | safeHTML }}',
    ),
    # P166：含 2 个内联 <a>；句尾原为独立 key（值以 ". " 开头），一并内联。
    (
        "layouts/research/price-index.html",
        '$10 buys about {{ printf "%.0f" $gb10Low }} GB of budget data in '
        '<a href="{{ partial "lang-href.html" (printf "/compare/%s/" $cheapest.slug) }}"'
        ' class="font-semibold text-brand-700 hover:underline">{{ $cheapest.name }}</a> —'
        ' but only {{ printf "%.1f" $gb10High }} GB in '
        '<a href="{{ partial "lang-href.html" (printf "/compare/%s/" $dearest.slug) }}"'
        ' class="font-semibold text-brand-700 hover:underline">{{ $dearest.name }}</a>'
        '{{ i18n "research_price_index__in_expensive_markets_a_short_validity_small_bucket_not_a" | safeHTML }}',
        '{{ i18n "research_price_index__ten_dollars_buys_about_n_gb_of_budget_data_in" (dict'
        ' "gb1" (printf "%.0f" $gb10Low)'
        ' "h1" (partial "lang-href.html" (printf "/compare/%s/" $cheapest.slug))'
        ' "c1" ($cheapest.name | htmlEscape)'
        ' "gb2" (printf "%.1f" $gb10High)'
        ' "h2" (partial "lang-href.html" (printf "/compare/%s/" $dearest.slug))'
        ' "c2" ($dearest.name | htmlEscape)) | safeHTML }}',
    ),
    # P171：两个区域名（region-label 输出含 &amp;，不能再转义）。
    (
        "layouts/research/price-index.html",
        '{{ partial "region-label.html" $rCheap.region | safeHTML }} averages'
        ' ${{ printf "%.2f" $rCheap.avg }}/GB — {{ printf "%.1f" $regionGap }}× cheaper than '
        '{{ partial "region-label.html" $rDear.region | safeHTML }} at ${{ printf "%.2f" $rDear.avg }}/GB.'
        ' Multi-country trips through a cheap region can safely buy bigger buckets;'
        ' check the region card below for its own league.',
        '{{ i18n "research_price_index__region_averages_n_times_cheaper" (dict'
        ' "r1" (partial "region-label.html" $rCheap.region)'
        ' "a1" (printf "%.2f" $rCheap.avg)'
        ' "n" (printf "%.1f" $regionGap)'
        ' "r2" (partial "region-label.html" $rDear.region)'
        ' "a2" (printf "%.2f" $rDear.avg)) | safeHTML }}',
    ),
    (
        "layouts/research/price-index.html",
        '{{ .count }} countries tracked{{ if eq $i 0 }} · cheapest region{{ end }}',
        '{{ if eq $i 0 }}'
        '{{ i18n "research_price_index__n_countries_tracked_cheapest_region" (dict "n" .count) | safeHTML }}'
        '{{ else }}'
        '{{ i18n "research_price_index__n_countries_tracked" (dict "n" .count) | safeHTML }}'
        '{{ end }}',
    ),
    (
        "layouts/research/price-index.html",
        'Where each provider is cheapest and priciest, computed across all {{ len $d.countries }} countries.',
        '{{ i18n "research_price_index__where_each_provider_is_cheapest_and_priciest"'
        ' (dict "n" (len $d.countries)) | safeHTML }}',
    ),
    # ── unlimited-esim.html ──
    (
        "layouts/research/unlimited-esim.html",
        '{{ $n }} countries with unlimited',
        '{{ i18n "research_unlimited_esim__n_countries_with_unlimited" (dict "n" $n) | safeHTML }}',
    ),
    (
        "layouts/research/unlimited-esim.html",
        'prices checked {{ time.Format ":date_medium" (time .) }}',
        '{{ i18n "g_prices_checked_date" (dict "date" (time.Format ":date_medium" (time .))) | safeHTML }}',
    ),
    (
        "layouts/research/unlimited-esim.html",
        'cheapest unlimited, ${{ printf "%.2f" .bestDaily }}/day',
        '{{ i18n "research_unlimited_esim__cheapest_unlimited_price_per_day"'
        ' (dict "price" (printf "%.2f" .bestDaily)) | safeHTML }}',
    ),
    (
        "layouts/research/unlimited-esim.html",
        'Unlimited at ${{ printf "%.2f" $beLow.bestDaily }}/day against'
        ' ${{ printf "%.2f" $beLow.minPerGB }}/GB metered: stream a couple of hours a day'
        " and unlimited already pays. A heavy user's dream market.",
        '{{ i18n "research_unlimited_esim__unlimited_at_n_per_day_against_m_per_gb" (dict'
        ' "p1" (printf "%.2f" $beLow.bestDaily) "p2" (printf "%.2f" $beLow.minPerGB)) | safeHTML }}',
    ),
    (
        "layouts/research/unlimited-esim.html",
        'Across the {{ $beN }} countries we computed, the typical break-even sits at'
        ' {{ printf "%.1f" $beMedian }} GB/day. Rough rule: if you burn through more than'
        ' {{ printf "%.1f" $beMedian }} GB on a normal travel day (maps + music + an evening of video),'
        ' unlimited is likely the cheaper side.',
        '{{ i18n "research_unlimited_esim__across_the_n_countries_we_computed" (dict'
        ' "n" $beN "be" (printf "%.1f" $beMedian)) | safeHTML }}',
    ),
    (
        "layouts/research/unlimited-esim.html",
        'Cheap metered data (${{ printf "%.2f" $beHigh.minPerGB }}/GB) meets a pricier'
        ' unlimited rate (${{ printf "%.2f" $beHigh.bestDaily }}/day): you would need'
        ' {{ printf "%.1f" $beHigh.be }} GB every single day before unlimited wins.'
        ' Buy a big bucket here instead.',
        '{{ i18n "research_unlimited_esim__cheap_metered_data_meets_a_pricier_unlimited_rate" (dict'
        ' "p1" (printf "%.2f" $beHigh.minPerGB) "p2" (printf "%.2f" $beHigh.bestDaily)'
        ' "n" (printf "%.1f" $beHigh.be)) | safeHTML }}',
    ),
    (
        "layouts/research/unlimited-esim.html",
        '{{ .cheapestDays }} days',
        '{{ i18n "research_unlimited_esim__n_days" (dict "n" .cheapestDays) | safeHTML }}',
    ),
    # U180：模板层硬编码 FAQ 问句（i18n_extract 的盲区 —— 它在 dict "q" "…" 字面量里）。
    (
        "layouts/research/unlimited-esim.html",
        'dict "q" "Does unlimited eSIM mean unlimited speed?"',
        'dict "q" (i18n "research_unlimited_esim__does_unlimited_esim_mean_unlimited_speed")',
    ),
    (
        "layouts/research/unlimited-esim.html",
        'All {{ len $d.countries }} countries ranked by best $/GB, with regional averages.',
        '{{ i18n "g_price_index_card_desc" (dict "n" (len $d.countries)) | safeHTML }}',
    ),
    # 单位本地化：`GB/day` -> `GB/Tag`、`$/day` -> `$/Tag`。
    # 英文侧字节不变，德语侧必须换 —— 这正是「德语发布前必须清掉」的单位泄漏。
    (
        "layouts/research/unlimited-esim.html",
        '{{ printf "%.1f" $beLow.be }} GB/day',
        '{{ i18n "research_unlimited_esim__n_gb_per_day" (dict "n" (printf "%.1f" $beLow.be)) | safeHTML }}',
    ),
    (
        "layouts/research/unlimited-esim.html",
        '{{ printf "%.1f" $beMedian }} GB/day',
        '{{ i18n "research_unlimited_esim__n_gb_per_day" (dict "n" (printf "%.1f" $beMedian)) | safeHTML }}',
    ),
    (
        "layouts/research/unlimited-esim.html",
        '{{ printf "%.1f" $beHigh.be }} GB/day',
        '{{ i18n "research_unlimited_esim__n_gb_per_day" (dict "n" (printf "%.1f" $beHigh.be)) | safeHTML }}',
    ),
    (
        "layouts/research/unlimited-esim.html",
        '${{ printf "%.2f" .bestDaily }}/day <span class="font-sans text-xs font-medium">· <a',
        '{{ i18n "research_unlimited_esim__price_per_day" (dict "price" (printf "%.2f" .bestDaily)) | safeHTML }}'
        ' <span class="font-sans text-xs font-medium">· <a',
    ),
]

# ── 2. i18n 新 key（en 值 = 现状英文原文；de = 德语整句） ─────────────────────
NEW_KEYS: list[tuple[str, str, str]] = [
    (
        "g_prices_checked_date",
        "prices checked {{ .date }}",
        "Preise geprüft am {{ .date }}",
    ),
    (
        "g_price_index_card_desc",
        "All {{ .n }} countries ranked by best $/GB, with regional averages.",
        "Alle {{ .n }} Länder nach dem besten $/GB sortiert, mit regionalen Durchschnitten.",
    ),
    (
        "research_fair_use_audit__n_unlimited_plans_audited",
        "{{ .n }} unlimited plans audited",
        "{{ .n }} unbegrenzte Tarife geprüft",
    ),
    (
        "research_fair_use_audit__n_more_variants",
        "+{{ .n }} more variants",
        "+{{ .n }} weitere Varianten",
    ),
    (
        "research_price_index__n_countries",
        "{{ .n }} countries",
        "{{ .n }} Länder",
    ),
    (
        "research_price_index__the_same_ruler_n_times_for_every_destination_we_track",
        "The same ruler, {{ .n }} times. For every destination we track, this index takes the"
        " cheapest per-gigabyte rate across all providers and ranks the countries against each"
        " other — the cheapest places to buy eSIM data, and the most expensive.",
        "Dasselbe Maß, {{ .n }} Mal angelegt. Für jedes Reiseziel, das wir erfassen, nimmt dieser"
        " Index den günstigsten Preis pro Gigabyte über alle Anbieter hinweg und reiht die Länder"
        " gegeneinander auf — die günstigsten Orte für eSIM-Daten und die teuersten.",
    ),
    (
        "research_price_index__cheapest_at_price_per_gb",
        "cheapest at ${{ .price }}/GB",
        "am günstigsten bei ${{ .price }}/GB",
    ),
    (
        "research_price_index__priciest_at_price_per_gb",
        "priciest at ${{ .price }}/GB",
        "am teuersten bei ${{ .price }}/GB",
    ),
    (
        "research_price_index__cheapest_region_avg_price_per_gb",
        "cheapest region, avg ${{ .price }}/GB",
        "günstigste Region, Ø ${{ .price }}/GB",
    ),
    (
        "research_price_index__n_plans",
        "{{ .n }} plans",
        "{{ .n }} Tarife",
    ),
    (
        "research_price_index__the_same_gigabyte_costs_n_times_more_in",
        'The same gigabyte costs {{ .n }} times more in <a href="{{ .h1 }}"'
        ' class="font-semibold text-brand-700 hover:underline">{{ .c1 }}</a> than in'
        ' <a href="{{ .h2 }}" class="font-semibold text-brand-700 hover:underline">{{ .c2 }}</a>'
        " (${{ .p1 }}/GB vs ${{ .p2 }}/GB). Destination choice moves the price far more than"
        " provider choice does.",
        'Dasselbe Gigabyte kostet in <a href="{{ .h1 }}"'
        ' class="font-semibold text-brand-700 hover:underline">{{ .c1 }}</a> {{ .n }} Mal mehr als in'
        ' <a href="{{ .h2 }}" class="font-semibold text-brand-700 hover:underline">{{ .c2 }}</a>'
        " (${{ .p1 }}/GB vs. ${{ .p2 }}/GB). Die Wahl des Reiseziels bewegt den Preis weit stärker"
        " als die Wahl des Anbieters.",
    ),
    (
        "research_price_index__ten_dollars_buys_about_n_gb_of_budget_data_in",
        '$10 buys about {{ .gb1 }} GB of budget data in <a href="{{ .h1 }}"'
        ' class="font-semibold text-brand-700 hover:underline">{{ .c1 }}</a> — but only'
        ' {{ .gb2 }} GB in <a href="{{ .h2 }}"'
        ' class="font-semibold text-brand-700 hover:underline">{{ .c2 }}</a>. In expensive markets'
        " a short validity small bucket, not a big one, is usually the sane buy.",
        'Für $10 gibt es in <a href="{{ .h1 }}"'
        ' class="font-semibold text-brand-700 hover:underline">{{ .c1 }}</a> rund {{ .gb1 }} GB Daten'
        ' zum Sparpreis — in <a href="{{ .h2 }}"'
        ' class="font-semibold text-brand-700 hover:underline">{{ .c2 }}</a> aber nur {{ .gb2 }} GB.'
        " In teuren Märkten ist ein kleines Kontingent mit kurzer Laufzeit meist der vernünftige"
        " Kauf, kein großes.",
    ),
    (
        "research_price_index__region_averages_n_times_cheaper",
        "{{ .r1 }} averages ${{ .a1 }}/GB — {{ .n }}× cheaper than {{ .r2 }} at ${{ .a2 }}/GB."
        " Multi-country trips through a cheap region can safely buy bigger buckets; check the"
        " region card below for its own league.",
        "{{ .r1 }} kostet im Schnitt ${{ .a1 }}/GB — {{ .n }}× günstiger als {{ .r2 }} mit"
        " ${{ .a2 }}/GB. Mehrländer-Reisen durch eine günstige Region können bedenkenlos größere"
        " Kontingente kaufen; die Regionskarte unten zeigt die eigene Rangliste.",
    ),
    (
        "research_price_index__n_countries_tracked",
        "{{ .n }} countries tracked",
        "{{ .n }} Länder erfasst",
    ),
    (
        "research_price_index__n_countries_tracked_cheapest_region",
        "{{ .n }} countries tracked · cheapest region",
        "{{ .n }} Länder erfasst · günstigste Region",
    ),
    (
        "research_price_index__where_each_provider_is_cheapest_and_priciest",
        "Where each provider is cheapest and priciest, computed across all {{ .n }} countries.",
        "Wo jeder Anbieter am günstigsten und am teuersten ist, berechnet über alle {{ .n }} Länder.",
    ),
    (
        "research_unlimited_esim__n_countries_with_unlimited",
        "{{ .n }} countries with unlimited",
        "{{ .n }} Länder mit Unlimited",
    ),
    (
        "research_unlimited_esim__cheapest_unlimited_price_per_day",
        "cheapest unlimited, ${{ .price }}/day",
        "günstigstes Unlimited, ${{ .price }}/Tag",
    ),
    (
        "research_unlimited_esim__unlimited_at_n_per_day_against_m_per_gb",
        "Unlimited at ${{ .p1 }}/day against ${{ .p2 }}/GB metered: stream a couple of hours a day"
        " and unlimited already pays. A heavy user's dream market.",
        "Unlimited für ${{ .p1 }}/Tag gegenüber ${{ .p2 }}/GB als Kontingent: Schon ein paar Stunden"
        " Streaming am Tag, und Unlimited rechnet sich. Ein Traummarkt für Vielnutzer.",
    ),
    (
        "research_unlimited_esim__across_the_n_countries_we_computed",
        "Across the {{ .n }} countries we computed, the typical break-even sits at {{ .be }} GB/day."
        " Rough rule: if you burn through more than {{ .be }} GB on a normal travel day"
        " (maps + music + an evening of video), unlimited is likely the cheaper side.",
        "Über die {{ .n }} Länder, die wir berechnet haben, liegt der typische Break-even bei"
        " {{ .be }} GB/Tag. Grobe Regel: Wer an einem normalen Reisetag mehr als {{ .be }} GB"
        " verbraucht (Karten + Musik + ein Abend Video), fährt mit Unlimited meist günstiger.",
    ),
    (
        "research_unlimited_esim__cheap_metered_data_meets_a_pricier_unlimited_rate",
        "Cheap metered data (${{ .p1 }}/GB) meets a pricier unlimited rate (${{ .p2 }}/day): you"
        " would need {{ .n }} GB every single day before unlimited wins. Buy a big bucket here"
        " instead.",
        "Günstige Kontingentdaten (${{ .p1 }}/GB) treffen auf einen teureren Unlimited-Tarif"
        " (${{ .p2 }}/Tag): Sie bräuchten jeden einzelnen Tag {{ .n }} GB, bevor Unlimited gewinnt."
        " Kaufen Sie hier stattdessen ein großes Kontingent.",
    ),
    (
        "research_unlimited_esim__n_days",
        "{{ .n }} days",
        "{{ .n }} Tage",
    ),
    (
        "research_unlimited_esim__does_unlimited_esim_mean_unlimited_speed",
        "Does unlimited eSIM mean unlimited speed?",
        "Bedeutet Unlimited-eSIM auch unbegrenzte Geschwindigkeit?",
    ),
    (
        "research_unlimited_esim__n_gb_per_day",
        "{{ .n }} GB/day",
        "{{ .n }} GB/Tag",
    ),
    (
        "research_unlimited_esim__price_per_day",
        "${{ .price }}/day",
        "${{ .price }}/Tag",
    ),
]

# ── 3. 被内联后不再引用的孤儿 key（en + de 各删一行） ────────────────────────
DEL_KEYS = [
    "research_price_index__than_in",
    "research_price_index__in_expensive_markets_a_short_validity_small_bucket_not_a",
]


def _read(p: str) -> str:
    b = (ROOT / p).read_bytes()
    crlf = b.count(b"\r\n")
    lf = b.count(b"\n") - crlf
    if crlf:
        raise SystemExit(f"{p}: 预期 LF 行尾，实测 CRLF {crlf} 行 —— 拒绝改写")
    return b.decode("utf-8")


def _write(p: str, s: str) -> None:
    (ROOT / p).write_bytes(s.encode("utf-8"))


def patch_templates(dry: bool) -> int:
    n = 0
    for rel, old, new in EDITS:
        src = _read(rel)
        c_old, c_new = src.count(old), src.count(new)
        if c_old == 1:
            if not dry:
                _write(rel, src.replace(old, new, 1))
            n += 1
            print(f"  EDIT  {rel}: ...{old[:56]!r} -> i18n")
        elif c_old == 0 and c_new >= 1:
            print(f"  skip  {rel}: 已应用（{old[:40]!r} 不在，new 在）")
        else:
            raise SystemExit(f"{rel}: 锚点命中 {c_old} 次（应为 1）: {old[:80]!r}")
    return n


def patch_toml(dry: bool) -> None:
    for lang in ("en", "de"):
        rel = f"i18n/{lang}.toml"
        src = _read(rel)
        lines = src.split("\n")

        # 3a. 删孤儿
        for k in DEL_KEYS:
            hits = [i for i, l in enumerate(lines) if l.startswith(k + " = ")]
            if len(hits) == 1:
                if not dry:
                    lines.pop(hits[0])
                print(f"  DEL   {rel}: {k}")
            elif not hits:
                print(f"  skip  {rel}: {k} 已删除")
            else:
                raise SystemExit(f"{rel}: 孤儿 key {k} 命中 {len(hits)} 行")

        body = "\n".join(lines)
        # 3b. 追加新 key（顺序 = NEW_KEYS 顺序，en/de 相同）
        idx = 1 if lang == "en" else 2
        add = []
        for tup in NEW_KEYS:
            k, v = tup[0], tup[idx]
            if f"\n{k} = " in body or body.startswith(f"{k} = "):
                print(f"  skip  {rel}: {k} 已存在")
                continue
            add.append(f"{k} = {json.dumps(v, ensure_ascii=False)}")
        if add:
            if not body.endswith("\n"):
                body += "\n"
            body += "\n".join(add) + "\n"
            if not dry:
                _write(rel, body)
            print(f"  ADD   {rel}: +{len(add)} key")


def verify() -> None:
    def keys(p: str) -> list[str]:
        out = []
        for ln in _read(p).split("\n"):
            s = ln.strip()
            if s and not s.startswith("#") and " = " in s:
                out.append(s.split(" = ", 1)[0].strip())
        return out

    a, b = keys("i18n/en.toml"), keys("i18n/de.toml")
    print(f"  shape en {len(a)} key / de {len(b)} key / 顺序一致 {a == b}")
    if a != b:
        raise SystemExit("en/de key 顺序不一致 —— 追加位置破坏了对齐")
    for k, _, _ in NEW_KEYS:
        if k not in a:
            raise SystemExit(f"新 key 未写入: {k}")


def main() -> int:
    dry = "--dry" in sys.argv
    print(f"patch_research_i18n {'(dry-run)' if dry else ''}")
    n = patch_templates(dry)
    patch_toml(dry)
    if not dry:
        verify()
    print(f"完成：模板改动 {n} 处 / 新 key {len(NEW_KEYS)} / 删 key {len(DEL_KEYS)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
