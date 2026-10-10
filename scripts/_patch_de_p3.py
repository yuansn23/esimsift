#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""D7 前置①-c：把 compare_vs_single(17) + compare_matchups(15) + esim_providers_list(7)
共 39 条英文占位翻成德语。

与 `_patch_de_p2.py` 同一套判据（归一化占位符多集 + 凭空占位符 + 未翻译同形 + 无 CRLF），
但本批 39 条**全部是纯文本、零占位符**，故占位符判据退化为「de 侧不许凭空出现 {{ }}」。

三条「半句」key（后面紧跟 <a> 链接）的德语收尾按相邻 key 的实际值定：
  compare_vs_single__entry_price_each_provider_s_cheapest_plan_in_that_countr
      + " " + <a>g_methodology → "Methodik</a>" + "."
  compare_vs_single__every_verdict_on_this_page_is_a_literal_sort_position_fr
      + " " + <a>Methodik</a> + g_how_we_make_money_in_our + " " + <a>Offenlegung</a>
  esim_providers_list__provider_order_on_this_page_follows_our_database_key_ord
      + " " + <a>Methodik</a> + "."
三者都要以阴性 "unserer" 收尾，才能与 "Methodik"/"Offenlegung" 对上。

只改 i18n/de.toml。用 --dry 只跑断言；--selftest 注入反例证明判据没被改瞎。
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
    # ── compare_vs_single（17）────────────────────────────────────────────
    ("compare_vs_single__beyond_price", "Mehr als der Preis"),
    ("compare_vs_single__build_your_own_comparison", "Stell dir deinen eigenen Vergleich zusammen"),
    ("compare_vs_single__cheaper_entry", "Günstigerer Einstieg"),
    ("compare_vs_single__country_by_country", "Land für Land"),
    ("compare_vs_single__each_cell_is_the_provider_s_cheapest_plan_in_that_countr",
     "Jede Zelle zeigt den günstigsten Tarif des Anbieters in diesem Land. "
     "Der Ländername öffnet den vollständigen Vergleich, die Preise öffnen die Tarife des Anbieters vor Ort."),
    ("compare_vs_single__entry_price_each_provider_s_cheapest_plan_in_that_countr",
     "Einstiegspreis = der günstigste Tarif jedes Anbieters in diesem Land, aus derselben datierten "
     "Momentaufnahme. Wie wir rechnen und prüfen, steht in unserer"),
    ("compare_vs_single__every_head_to_head_we_track", "Alle Duelle, die wir erfassen"),
    ("compare_vs_single__every_verdict_on_this_page_is_a_literal_sort_position_fr",
     "Jedes Urteil auf dieser Seite ist eine wörtliche Sortierposition aus derselben datierten "
     "Preis-Momentaufnahme — keine redaktionellen Sternebewertungen, kein Pay-to-Rank. "
     "Wie wir Daten erheben und prüfen, steht in unserer"),
    ("compare_vs_single__identical_prices", "identische Preise"),
    ("compare_vs_single__more_matchups", "Weitere Duelle"),
    ("compare_vs_single__no_pay_to_rank", "kein Pay-to-Rank"),
    ("compare_vs_single__other_esim_comparisons", "Weitere eSIM-Vergleiche"),
    ("compare_vs_single__pick_any_two_providers_every_head_to_head_on_this_site_i",
     "Wähle zwei beliebige Anbieter — jedes Duell auf dieser Seite wird aus derselben datierten "
     "Preis-Momentaufnahme berechnet. Eine dritte Auswahl ersetzt deine älteste."),
    ("compare_vs_single__pick_two_providers", "Wähle zwei Anbieter"),
    ("compare_vs_single__tick_exactly_two_the_button_opens_the_computed_head_to_h",
     "Wähle genau zwei aus — der Button öffnet das berechnete Duell."),
    ("compare_vs_single__tie", "Gleichstand"),
    ("compare_vs_single__unlimited_only", "nur unbegrenzt"),

    # ── compare_matchups（15）─────────────────────────────────────────────
    ("compare_matchups__all_matchups", "Alle Duelle"),
    ("compare_matchups__compare_by_country", "Nach Land vergleichen"),
    ("compare_matchups__each_brand_s_pricing_behavior_in_full",
     "das Preisverhalten jeder Marke im Detail"),
    ("compare_matchups__each_verdict_counts_the_countries_where_both_providers_s",
     "Jedes Urteil zählt die Länder, in denen beide Anbieter Tarife verkaufen, und vergleicht den "
     "jeweils günstigsten Tarif (und separat den besten $/GB) aus derselben datierten Momentaufnahme. "
     "Umgekehrte Suchanfragen landen auf derselben Seite — eine URL pro Duell, keine Fast-Duplikate."),
    ("compare_matchups__even", "ausgeglichen"),
    ("compare_matchups__every_matchup_verdict_is_computed_country_by_country_fro",
     "Jedes Duell-Urteil wird Land für Land aus derselben datierten Preis-Momentaufnahme berechnet."),
    ("compare_matchups__every_provider_pair_we_track_one_page_per_matchup_verdic",
     "Jedes Anbieterpaar, das wir erfassen, eine Seite pro Duell. Urteile sind keine Meinungen: "
     "Für jedes gemeinsame Land vergleichen wir die günstigsten Tarife direkt und zählen, wer gewinnt — "
     "dieselben datierten Preise, die jede Tabelle dieser Seite speisen."),
    ("compare_matchups__head_to_head_index", "Duell-Index"),
    ("compare_matchups__how_every_provider_compares_head_to_head",
     "Wie sich jeder Anbieter im direkten Duell schlägt"),
    ("compare_matchups__most_lopsided_one_side_wins_nearly_everywhere",
     "am einseitigsten — eine Seite gewinnt fast überall"),
    ("compare_matchups__provider_reviews", "Anbieter-Tests →"),
    ("compare_matchups__two_esim_providers_compared_country_by_country",
     "Zwei eSIM-Anbieter, Land für Land verglichen"),
    ("compare_matchups__unlimited_daily_rates", "Tagespreise für Unlimited-Tarife"),
    ("compare_matchups__what_every_unlimited_plan_s_small_print_really_throttles",
     "Was das Kleingedruckte jedes \u201eunlimited\u201c-Tarifs wirklich drosselt."),
    ("compare_matchups__where_unlimited_data_is_cheapest_per_day_and_when_it_win",
     "Wo unbegrenzte Daten pro Tag am günstigsten sind — und wann sie gewinnen."),

    # ── esim_providers_list（7）──────────────────────────────────────────
    ("esim_providers_list__all_deals", "Alle Angebote →"),
    ("esim_providers_list__best_gb_in_our_database", "Bester $/GB in unserer Datenbank:"),
    ("esim_providers_list__coverage_at_a_glance", "Abdeckung auf einen Blick"),
    ("esim_providers_list__esim_providers_we_track", "eSIM-Anbieter, die wir erfassen"),
    ("esim_providers_list__no_pay_to_win", "Kein Pay-to-Win."),
    ("esim_providers_list__provider_order_on_this_page_follows_our_database_key_ord",
     "Die Anbieter-Reihenfolge auf dieser Seite folgt unserer Datenbank-Schlüsselreihenfolge, "
     "nicht dem Werbebudget. Die Rankings in den Länderseiten sind wörtliche Sortierpositionen — "
     "siehe unsere"),
    ("esim_providers_list__the_same_ruler_for_everyone_coverage_entry_price_and_hon",
     "Derselbe Maßstab für alle: Abdeckung, Einstiegspreis und ehrliche Abwägungen für jeden Anbieter "
     "in unserer Datenbank. Tippe auf eine Marke für den vollständigen berechneten Test — die Preise "
     "werden nach festem Zeitplan erneut geprüft."),
]

# 本批无条件同形白名单（39 条全部应真译；留空集是为了让判据「未翻译同形」保持有效）
SAME_FORM: set[str] = set()

RE_GO = re.compile(r"\{\{.*?\}\}", re.S)
RE_JS = re.compile(r"\{[A-Za-z_][A-Za-z0-9_]*\}")

# 与 _patch_de_p2.py 同源：德语三格是同一占位符的三种形态，归一化后比「集合 + 次数」
VARIANTS = {
    "{{ .country_acc }}": "{{ .country }}",
    "{{ .country_dat }}": "{{ .country }}",
}
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
    go = norm(RE_GO.findall(value))
    rest = RE_GO.sub("", value)
    return go, tuple(sorted(RE_JS.findall(rest)))


def extra_tokens(en_v: str, de_v: str) -> set[str]:
    allowed = set(RE_GO.findall(en_v))
    if "{{ .country }}" in allowed:
        allowed |= DE_ONLY
    return set(RE_GO.findall(de_v)) - allowed


def audit(pairs, en: dict[str, str], de: dict[str, str]) -> list[str]:
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
    """本批 39 条零占位符 → 判据退化为「不许凭空出现 {{ }}」。注入反例证明它没瞎。"""
    k0, v0 = T[0]
    cases: list[tuple[str, list[tuple[str, str]], int]] = [
        ("A 凭空加 {{ }}", [(k0, v0 + " {{ .bogus }}")], 1),
        ("B 未翻译同形", [(k0, en[k0])], 1),
        ("C key 不存在", [("compare_vs_single__no_such_key", "x")], 1),
        ("D 正常译文", [(k0, v0)], 0),
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
    print(f"断言全过（{len(T)} 条）：key 存在 / 占位符归一后多集相等 / 无凭空占位符 / 无未翻译同形。")
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
