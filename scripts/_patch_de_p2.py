#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""D7 前置①-b：把 compare_provider__* 的 112 条英文占位翻成德语。

配套 `scripts/_wire_de_country_case.py`：该模板现已把 `country`（裸名，用于复合词
`{{ .country }}-eSIM`）、`country_acc`（für/über 后）、`country_dat`（in/von/bei 后）
三份都传进每个 i18n dict，故德语值按介词选格。

只改 i18n/de.toml。四条断言同 `_patch_de_p1.py`：key 存在 / 唯一命中 /
**占位符集合与英文值完全一致** / 无 CRLF。
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
EN = ROOT / "i18n" / "en.toml"
DE = ROOT / "i18n" / "de.toml"

T: list[tuple[str, str]] = [
    ("compare_provider__all_n_plans",
     "Alle {{ .n }} {{ .brand }}-Tarife für {{ .country_acc }}"),
    ("compare_provider__calc_days_label", "Deine Reisedauer"),
    ("compare_provider__calc_days_unit", "Tage"),
    ("compare_provider__calc_h3", "Preis für deine eigenen Daten"),
    ("compare_provider__calc_mine", "Günstigster {{ .brand }}-Tarif, der die Reise abdeckt"),
    ("compare_provider__calc_none",
     "Kein einzelner Tarif deckt so viele Tage ab — kombiniere zwei kürzere Tarife oder verkürze die Reise. Der vollständige Rechner deckt beides ab."),
    ("compare_provider__calc_note",
     "Hier zählen nur Tarife, deren Gültigkeit die ganze Reise abdeckt: Eine 30-Tage-Reise wird also mit einem 30-Tage-Tarif bepreist und nicht mit einem fünffach gestapelten 5-Tage-Tarif. Jede Auswahl zeigt ihr Datenvolumen neben dem Preis — dass ein 500-MB-Paket einen 5-GB-Tarif unterbietet, hat seinen Grund."),
    ("compare_provider__calc_rival", "Günstigster Rivale"),
    ("compare_provider__calc_tie", "Beide kosten dasselbe"),
    ("compare_provider__calc_win_mine", "{{ .brand }} ist günstiger um"),
    ("compare_provider__calc_win_rival", "Der Rivale ist günstiger um"),
    ("compare_provider__country_comparison", "{{ .country }}-eSIM-Vergleich"),
    ("compare_provider__country_crumb", "{{ .country }}-eSIM"),
    ("compare_provider__cta_view_plans", "{{ .brand }}-Tarife für {{ .country_acc }} ansehen"),
    ("compare_provider__diff_cheaper", "Einstieg um ${{ .diff }} günstiger"),
    ("compare_provider__diff_pricier", "Einstieg um ${{ .diff }} teurer"),
    ("compare_provider__diff_same", "Gleicher Einstiegspreis"),
    ("compare_provider__diff_unknown", "Einstiegspreis nicht erfasst"),
    ("compare_provider__fair_use_threshold", "Fair-Use-Schwelle"),
    ("compare_provider__faq_a_network",
     "{{ .brand }} besitzt keine Masten in {{ .country_dat }} — deine Daten laufen also über die lokalen Gastgebernetze {{ .carriers }}. Das schnellste davon erreicht rund {{ .max }} Mbps, und alle {{ .plans }} Tarife für {{ .country_acc }}, die wir erfassen, verbinden sich mit denselben lokalen Netzen."),
    ("compare_provider__faq_a_price_met",
     "{{ .brand }} verkauft {{ .n }} Tarife für {{ .country_acc }}, ab ${{ .from }}. Der beste Satz liegt bei ${{ .pergb }}/GB — Platz #{{ .rank }} von {{ .total }} Anbietern, die wir für dieses Reiseziel erfassen. Alle Preise in USD wie von {{ .brand }} gelistet, ohne Rabattcodes."),
    ("compare_provider__faq_a_price_unl",
     "{{ .brand }} verkauft {{ .n }} Tarife für {{ .country_acc }}, alle mit unbegrenzten Daten, ab ${{ .from }} für eine Reise über {{ .days }} Tage — etwa ${{ .perday }}/Tag. Es gibt keine volumenbasierte Stufe zum Vergleich, der ehrliche Test ist also, ob du mehr als das pro Tag verbrauchst."),
    ("compare_provider__faq_a_rival",
     "Der günstigste Tarif von {{ .brand }} kostet hier ${{ .mine }}; der von {{ .rival }} liegt bei ${{ .rivalprice }}, wobei dieser Einstiegspreis {{ .rivaldata }} kauft. Die vollständige Rangliste mit jedem Tarif — Datenvolumen und $/GB nebeneinander — steht im <a href=\"{{ .compare }}\">{{ .country }}-eSIM-Vergleich</a>."),
    ("compare_provider__faq_a_unverified",
     "Wir haben die veröffentlichten Bedingungen von {{ .brand }} dafür noch nicht geprüft. Prüfe vor dem Kauf die technischen Angaben des Anbieters selbst."),
    ("compare_provider__faq_caption",
     "Fragen zur {{ .brand }}-eSIM für {{ .country_acc }} — Daten, Hotspot-Regeln und Fair Use."),
    ("compare_provider__faq_eyebrow", "FAQ"),
    ("compare_provider__faq_h2", "Fragen zur {{ .brand }}-eSIM für {{ .country_acc }}"),
    ("compare_provider__faq_img_alt",
     "Illustration zu Fragen rund um die {{ .brand }}-eSIM für {{ .country_acc }}"),
    ("compare_provider__faq_q_hotspot",
     "Kann ich meine {{ .brand }}-eSIM für {{ .country_acc }} mit einem Laptop teilen?"),
    ("compare_provider__faq_q_network", "Welches Netz nutzt {{ .brand }} in {{ .country_dat }}?"),
    ("compare_provider__faq_q_price", "Wie viel verlangt {{ .brand }} für {{ .country_acc }}?"),
    ("compare_provider__faq_q_rival",
     "Ist {{ .brand }} oder {{ .rival }} die bessere {{ .country }}-eSIM?"),
    ("compare_provider__faq_q_unlimited",
     "Ist unbegrenztes Datenvolumen von {{ .brand }} in {{ .country_dat }} wirklich unbegrenzt?"),
    ("compare_provider__fit_best", "Kaufe es, wenn"),
    ("compare_provider__fit_data_only",
     "Du eine lokale Telefonnummer brauchst — das sind reine Datentarife."),
    ("compare_provider__fit_eyebrow", "Für wen es passt"),
    ("compare_provider__fit_h2", "Solltest du {{ .brand }} für {{ .country_acc }} kaufen"),
    ("compare_provider__fit_hotspot_block",
     "Du geplant hast, vom getetherten Laptop zu arbeiten — Hotspot ist auf {{ .allowance }} begrenzt."),
    ("compare_provider__fit_long_trip",
     "Du {{ .days }} Tage oder länger unterwegs bist — {{ .plan }} deckt das für ${{ .price }} ab."),
    ("compare_provider__fit_metered_lineup",
     "Du dein Datenvolumen lieber selbst dosierst — hier {{ .n }} Tarife, ab ${{ .price }}."),
    ("compare_provider__fit_no_topup",
     "Du unterwegs mehr Daten brauchen könntest — {{ .brand }} bietet kein Nachbuchen, ein zweiter Tarif ist also der einzige Weg zu mehr."),
    ("compare_provider__fit_rival",
     "Der günstigste Headline-Preis alles ist — der kleinste Tarif von {{ .rival }} in {{ .country_dat }} startet bei ${{ .price }}, und das kauft {{ .data }}."),
    ("compare_provider__fit_short_trip",
     "Du auf einem Kurztrip bist — {{ .plan }} läuft {{ .days }} Tage für ${{ .price }}."),
    ("compare_provider__fit_skip", "Sieh dich anderswo um, wenn"),
    ("compare_provider__fit_unlimited_lineup",
     "Du null Datensorgen willst — alle {{ .n }} Tarife hier sind unbegrenzt."),
    ("compare_provider__flag_alt", "Flagge von {{ .country_dat }}"),
    ("compare_provider__from", "Ab"),
    ("compare_provider__from_price", "ab ${{ .price }}"),
    ("compare_provider__full_review", "Vollständiger {{ .brand }}-Test →"),
    ("compare_provider__fup_drop_to", "Fällt auf"),
    ("compare_provider__fup_h2",
     "Ist unbegrenztes Datenvolumen von {{ .brand }} in {{ .country_dat }} wirklich unbegrenzt"),
    ("compare_provider__h1",
     "{{ .brand }} {{ .country }} eSIM-Tarife &amp; Preise ({{ .year }})"),
    ("compare_provider__hero_caption",
     "{{ .brand }} in {{ .country_dat }} — {{ .n }} Tarife, Preise geprüft am {{ .date }}."),
    ("compare_provider__hero_img_alt",
     "{{ .brand }}-eSIM-Tarife für {{ .country_acc }} — Daten, Gültigkeit und Preise"),
    ("compare_provider__hero_lead",
     "Das vollständige {{ .country }}-Angebot von {{ .brand }} — <strong class=\"text-ink-950 tnum\">{{ .n }} Tarife</strong>, gemessen an allen {{ .providers }} Anbietern und {{ .plans }} Tarifen, die wir für dieses Land erfassen."),
    ("compare_provider__host_lead",
     "{{ .brand }} besitzt keine Masten in {{ .country_dat }}. Dieser Tarif verbindet sich mit den lokalen Gastgebernetzen <strong class=\"text-ink-800\">{{ .nets }}</strong> — Abdeckung, Geschwindigkeit und Reichweite auf dem Land richten sich also nach diesen Masten, nicht nach der Marke auf dem Gutschein."),
    ("compare_provider__host_network_h2",
     "Auf welchem Netz {{ .brand }} in {{ .country_dat }} fährt"),
    ("compare_provider__hotspot_sharing", "Hotspot und Tethering"),
    ("compare_provider__last_checked", " Zuletzt geprüft am {{ .date }}."),
    ("compare_provider__network_by_network_breakdown_including_which_carriers_ev",
     "Aufschlüsselung Netz für Netz, inklusive der Netze, auf denen jeder Rivale fährt, und wie die zwei Tester sie einordnen:"),
    ("compare_provider__network_page_link", "Netzbetreiber in {{ .country }} →"),
    ("compare_provider__not_verified",
     "Wir haben die Hotspot-, Fair-Use- und Nachbuchungsbedingungen von {{ .brand }} für {{ .country_acc }} noch nicht geprüft. Prüfe vor dem Kauf die technischen Angaben des Anbieters selbst — wir lassen lieber eine Lücke als zu raten."),
    ("compare_provider__of_n_on_gb", "von {{ .n }} bei $/GB"),
    ("compare_provider__others_h2",
     "{{ .brand }} gegen die anderen Anbieter in {{ .country_dat }}"),
    ("compare_provider__plans_eyebrow", "{{ .brand }} in {{ .country_dat }}"),
    ("compare_provider__prices_footnote",
     "Preise in USD wie von {{ .brand }} gelistet, ohne Rabattcodes und Steuern. Labels vergleichen gegen alle {{ .plans }} eSIM-Tarife für {{ .country_acc }}, die wir erfassen — siehe unsere"),
    ("compare_provider__prices_verified", "Preise geprüft am {{ .date }}."),
    ("compare_provider__promo_cta", "Code bei {{ .brand }} einlösen"),
    ("compare_provider__promo_expires",
     "Gültig bis {{ .date }}. Gilt beim Checkout bei {{ .brand }} zusätzlich zu den Preisen unten."),
    ("compare_provider__promo_no_expiry",
     "Kein Ablaufdatum angegeben. Gilt beim Checkout bei {{ .brand }} zusätzlich zu den Preisen unten."),
    ("compare_provider__promo_eyebrow", "{{ .brand }}-Rabattcode"),
    ("compare_provider__promo_line", "{{ .label }} — Code"),
    ("compare_provider__reality_eyebrow", "Jenseits des Preisschilds"),
    ("compare_provider__see_plans", "Alle {{ .brand }}-Tarife ansehen"),
    ("compare_provider__speed_4g", "Nur 4G"),
    ("compare_provider__speed_5g", "5G verfügbar"),
    ("compare_provider__speed_and_coverage", "Geschwindigkeit und 5G"),
    ("compare_provider__speed_mbps", "{{ .min }}–{{ .max }} Mbps"),
    ("compare_provider__speed_typical",
     "Typischer Download in der Praxis im schnellsten Gastgebernetz, {{ .carrier }}. Die tatsächliche Geschwindigkeit hängt davon ab, welchen Mast dein Handy wählt und wie ausgelastet er ist."),
    ("compare_provider__speed_unprofiled",
     "Wir haben die Mobilfunkgeschwindigkeiten in {{ .country_dat }} noch nicht profiliert. Die unten genannten Betreiber sind die, mit denen sich dieser Tarif verbindet."),
    ("compare_provider__status_allowed", "Erlaubt"),
    ("compare_provider__status_available", "Verfügbar"),
    ("compare_provider__status_capped", "Begrenzt"),
    ("compare_provider__status_none", "Nicht verfügbar"),
    ("compare_provider__status_unverified", "Noch nicht geprüft"),
    ("compare_provider__the_country_benchmark_is", "; der Länder-Benchmark liegt bei"),
    ("compare_provider__the_destination_by_destination_breakdown_of_every_host_c",
     "Die Aufschlüsselung jedes Gastgebernetzes nach Reiseziel steht in der"),
    ("compare_provider__the_masts_behind_the_plan", "Die Masten hinter dem Tarif"),
    ("compare_provider__the_other_side_by_side", "Die andere Seite im Vergleich"),
    ("compare_provider__top_ups", "Nachbuchen"),
    ("compare_provider__trip_calc", "Brauchst du eine genaue Zahl für deine eigenen Daten?"),
    ("compare_provider__trip_calc_link", "Reisekostenrechner starten"),
    ("compare_provider__trip_cheaper", "günstiger"),
    ("compare_provider__trip_col_length", "Reisedauer"),
    ("compare_provider__trip_col_rival", "Günstigster Rivale in {{ .country_dat }}"),
    ("compare_provider__trip_days", "{{ .n }} Tage"),
    ("compare_provider__trip_eyebrow", "Preis nach Reisedauer"),
    ("compare_provider__trip_fit", "{{ .days }} Tage · {{ .data }}"),
    ("compare_provider__trip_fit_rival", "{{ .days }} Tage · {{ .data }} · {{ .provider }}"),
    ("compare_provider__trip_h2",
     "Was {{ .brand }} je Reisedauer in {{ .country_dat }} kostet"),
    ("compare_provider__trip_lead",
     "Dieselbe Reise, zweimal bepreist — der günstigste eigene Tarif von {{ .brand }}, der für den ganzen Aufenthalt gültig bleibt, gegen den günstigsten Rivalentarif, der dieselben Tage in {{ .country_dat }} abdeckt."),
    ("compare_provider__trip_this", "{{ .brand }} günstigster"),
    ("compare_provider__trust_h", "Sieh dir das gesamte Bild für {{ .country_acc }} an"),
    ("compare_provider__trust_ranked",
     "{{ .brand }} liegt beim besten $/GB in {{ .country_dat }} auf Platz #{{ .rank }} von {{ .total }} — die vollständige Tabelle mit allen {{ .plans }} Tarifen, Labels und Fair-Use-Hinweisen steht in der"),
    ("compare_provider__trust_unlimited",
     "{{ .brand }} verkauft nur unbegrenzte Daten, es gibt also keinen $/GB-Wert zum Einordnen. Die vollständige Tabelle mit allen {{ .plans }} Tarifen für {{ .country_acc }}, Labels und Fair-Use-Hinweisen steht in der"),
    ("compare_provider__verdict_entry_cheap",
     " — der günstigste Einstieg in jede {{ .country }}-eSIM auf dieser Seite."),
    ("compare_provider__verdict_entry_floor",
     " gegenüber der Länderuntergrenze von ${{ .floor }}."),
    ("compare_provider__verdict_h2",
     "Ist {{ .brand }} die richtige eSIM für {{ .country_acc }}"),
    ("compare_provider__verdict_met_rank",
     "Der beste Satz von {{ .brand }} in {{ .country_dat }} ist <strong class=\"text-ink-950 tnum\">${{ .pergb }}/GB</strong> — Platz <strong class=\"text-ink-950 tnum\">#{{ .rank }} von {{ .total }}</strong>{{ .benchmark }} <strong class=\"text-ink-950 tnum\">${{ .bench }}/GB</strong>. Der Einstiegspreis liegt bei <strong class=\"text-ink-950 tnum\">${{ .min }}</strong>{{ .entrybit }} Der vollständige Ranking-Kontext steht im <a href=\"{{ .url }}\" class=\"font-semibold text-brand-700 hover:underline\">{{ .country }}-Vergleich aller Anbieter</a>."),
    ("compare_provider__verdict_met_top",
     "Der beste Satz von {{ .brand }} in {{ .country_dat }} ist <strong class=\"text-ink-950 tnum\">${{ .pergb }}/GB</strong> — der beste aller {{ .total }} Anbieter, die wir hier erfassen. Der Einstiegspreis liegt bei <strong class=\"text-ink-950 tnum\">${{ .min }}</strong>{{ .entrybit }} Der vollständige Ranking-Kontext steht im <a href=\"{{ .url }}\" class=\"font-semibold text-brand-700 hover:underline\">{{ .country }}-Vergleich aller Anbieter</a>."),
    ("compare_provider__verdict_unl",
     "{{ .brand }} verkauft in {{ .country_dat }} nur eine Tarifform: unbegrenzte Daten, tageweise abgerechnet, ab <strong class=\"text-ink-950 tnum\">${{ .perday }}/Tag</strong>. Das begrenzt dein Risiko auf datenintensiven Reisen — doch zwei Wochen zu diesem Satz kosten mehr als die meisten Volumenpakete, und Hotspot hat eine eigene, separate Grenze. Der Länder-Benchmark zum Vergleich liegt bei <strong class=\"text-ink-950 tnum\">${{ .bench }}/GB</strong>."),
    ("compare_provider__view_plan", "Tarif ansehen"),
]

SAME_FORM = {
    "compare_provider__faq_eyebrow",   # "FAQ"（德语同形缩写）
    "compare_provider__speed_mbps",    # "{{ .min }}–{{ .max }} Mbps"（单位 + 占位符）
}

RE_GO = re.compile(r"\{\{.*?\}\}", re.S)
RE_JS = re.compile(r"\{[A-Za-z_][A-Za-z0-9_]*\}")

# ★ 德语三格是「同一个占位符的三种形态」，不是三个占位符。
#   en 只有 `{{ .country }}`（英文不分格），德语按介词选 `_acc` / `_dat`；
#   若把占位符当字面串逐字比对，会把 112 条**正确**的译文全判成错误（第六十三轮实测）。
#   归一化：三格 → `{{ .country }}`，从而「集合 + 出现次数」仍须完全相等。
VARIANTS = {
    "{{ .country_acc }}": "{{ .country }}",
    "{{ .country_dat }}": "{{ .country }}",
}
# de 侧允许出现、而 en 侧不会出现的占位符（仅当 en 有裸 country 占位符时才放行）
DE_ONLY = {"{{ .country_acc }}", "{{ .country_dat }}"}


def norm(tokens) -> tuple[str, ...]:
    return tuple(sorted(VARIANTS.get(t, t) for t in tokens))


def load(path: Path) -> dict[str, str]:
    out: dict[str, str] = {}
    for line in path.read_text(encoding="utf-8").splitlines():
        s = line.strip()
        if s and not s.startswith("#") and " = " in line:
            k, v = line.split(" = ", 1)
            out[k.strip()] = json.loads(v.strip())
    return out


def ph(value: str) -> tuple[tuple[str, ...], tuple[str, ...]]:
    """归一化后的占位符指纹：(Go 模板占位符多集, JS 单花括号占位符多集)。"""
    go = norm(RE_GO.findall(value))
    rest = RE_GO.sub("", value)
    return go, tuple(sorted(RE_JS.findall(rest)))


def extra_tokens(en_v: str, de_v: str) -> set[str]:
    """de 侧凭空多出来的 Go 占位符（归一化后仍在 en 里找不到的）。"""
    allowed = set(RE_GO.findall(en_v))
    if "{{ .country }}" in allowed:
        allowed |= DE_ONLY
    return set(RE_GO.findall(de_v)) - allowed


def audit(pairs, en: dict[str, str], de: dict[str, str]) -> list[str]:
    """四条判据，返回错误描述列表（空 = 全过）。"""
    errs: list[str] = []
    for k, v in pairs:
        if k not in en:
            errs.append(f"{k} 不在 en.toml"); continue
        if k not in de:
            errs.append(f"{k} 不在 de.toml"); continue
        if ph(en[k]) != ph(v):
            errs.append(f"占位符不一致 {k}  en={ph(en[k])}  de={ph(v)}")
        over = extra_tokens(en[k], v)
        if over:
            errs.append(f"de 侧凭空多出占位符 {k} {sorted(over)}")
        if k in SAME_FORM and v != en[k]:
            errs.append(f"{k} 在白名单里但值变了")
        if k not in SAME_FORM and v == en[k]:
            errs.append(f"{k} 与英文同形却不在白名单（= 未翻译）")
    return errs


def selftest(en: dict[str, str], de: dict[str, str]) -> int:
    """注入反例，证明归一化没把判据改瞎。"""
    # 挑一条同时含 country 与其它占位符的，A/B/D 用它做底
    base_k, base_v = next((k, v) for k, v in T if "{{ .country_acc }}" in v and "{{ .brand }}" in v)
    unl_k = "compare_provider__all_n_plans"
    unl_de = next(v for k, v in T if k == unl_k)

    cases: list[tuple[str, list[tuple[str, str]], int]] = [
        # A：漏掉一个 country 占位符 → 必须报
        ("A 漏占位符", [(base_k, base_v.replace("{{ .country_acc }}", "", 1))], 1),
        # B：凭空多一个占位符 → 必须报
        ("B 多占位符", [(base_k, base_v + " {{ .bogus }}")], 1),
        # C：三格互换（acc↔dat）→ 归一化生效，必须**不报**
        ("C 格互换应放过", [(base_k, base_v.replace("{{ .country_acc }}", "{{ .country_dat }}"))], 0),
        # C2：裸 country ↔ acc 互换 → 也必须不报
        ("C2 裸名换格应放过", [(unl_k, unl_de.replace("{{ .country }}", "{{ .country_dat }}"))], 0),
        # D：白名单 key 的值被改动 → 必须报
        ("D 白名单值变了", [("compare_provider__faq_eyebrow", "FAQx")], 1),
        # E：改了不存在的 key → 必须报
        ("E key 不存在", [("compare_provider__no_such_key", "x")], 1),
        # F：写成英文原文（= 未翻译）→ 必须报（第六十三轮：country_crumb 就是这么漏的）
        ("F 未翻译同形", [(base_k, en[base_k])], 1),
    ]
    ok = 0
    for label, pairs, want in cases:
        got = 1 if audit(pairs, en, de) else 0
        flag = "ok" if got == want else "!!"
        ok += got == want
        print(f"  [{flag}] {label}  期望报={want} 实报={got}")
    print(f"selftest: {ok}/{len(cases)} 项通过")
    return 0 if ok == len(cases) else 1


def main() -> int:
    dry = "--dry" in sys.argv
    en, de = load(EN), load(DE)

    if "--selftest" in sys.argv:
        return selftest(en, de)

    errs = audit(T, en, de)
    for e in errs:
        print(f"!! {e}")
    if errs:
        print(f"\n{len(errs)} 处问题，未写盘。")
        return 1
    print(f"断言全过（{len(T)} 条）：key 存在 / 占位符归一后多集相等 / 无凭空占位符 / 白名单同形。")
    if dry:
        print("--dry：未写盘。")
        return 0

    raw = DE.read_bytes()
    text = raw.decode("utf-8")
    for k, v in T:
        pat = re.compile(r"(?m)^%s = .*$" % re.escape(k))
        if len(pat.findall(text)) != 1:
            print(f"!! {k} 未唯一命中"); return 1
        text = pat.sub(lambda _m, kk=k, vv=v: f"{kk} = {json.dumps(vv, ensure_ascii=False)}",
                       text, count=1)
    data = text.encode("utf-8")
    if data.count(b"\r\n"):
        print("!! 产物出现 CRLF"); return 1
    DE.write_bytes(data)

    after = load(DE)
    still = sorted(k for k, _ in T if after.get(k) == en.get(k))
    print(f"OK 写入 {len(T)} 条（de.toml {len(raw)} -> {len(data)} B）")
    print(f"   仍与英文同形 {len(still)} 条：{still}")
    if set(still) - SAME_FORM:
        print(f"!! 未预期同形：{sorted(set(still) - SAME_FORM)}"); return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
