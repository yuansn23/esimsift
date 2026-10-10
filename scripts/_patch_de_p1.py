#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""D7 前置①-a：把 esim_providers_single__* 的 124 条英文占位翻成德语。

只改 i18n/de.toml（en 侧一字不动 → 英文产物恒等的前提）。
逐行替换，不用「整表重排」，避免动到无关行。

自带四条断言：
  1. 每个键都必须在 en.toml 里存在；
  2. 每个键在 de.toml 里必须恰好命中一行；
  3. **占位符集合必须与英文值完全一致**（`{{ .x }}` 与 JS 的 `{x}` 分别比）——
     这是本脚本唯一的机械正确性保证：句子改了，占位符不能丢、不能多；
  4. 写盘后断言无 CRLF。
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
EN = ROOT / "i18n" / "en.toml"
DE = ROOT / "i18n" / "de.toml"

# 术语与风格（对齐 de.toml 既有已译条目）：
#   · 直接称呼用 du/dein；站点自称 wir。
#   · unlimited：形容词/谓语用 `unbegrenzt`；复合词与标签用借词 `unlimited-Tarif`。
#   · Rivale / Anbieter / Tarif / Reiseziel / Länder / Abdeckung / Günstigster / Rangliste。
#   · `Anbieter` = provider；`Rivale` = 具体对决里的对手（对齐既有 compare_vs_single）。
T: list[tuple[str, str]] = [
    # ── 促销条 ──────────────────────────────────────────────────────────
    ("esim_providers_single__promo_no_expiry",
     "Kein Ablaufdatum angegeben. Alle"),
    # ── 覆盖说明 ────────────────────────────────────────────────────────
    ("esim_providers_single__a_note_on_coverage",
     "Ein Hinweis zur Abdeckung:"),
    ("esim_providers_single__alternatives",
     "Alternativen"),
    ("esim_providers_single__any_country_page",
     "jede beliebige Länder-Seite"),
    ("esim_providers_single__app_store",
     "App Store ↗"),
    ("esim_providers_single__badge_in_the_coverage_list_below",
     "Label in der Abdeckungsliste unten."),
    ("esim_providers_single__before_buying",
     "bevor du kaufst."),
    ("esim_providers_single__best_gb_in",
     "Bester $/GB in"),
    ("esim_providers_single__best_value_anywhere",
     "Bester Wert überhaupt:"),
    ("esim_providers_single__buy_on_the_website",
     "Auf der Website kaufen"),
    # ── 计算器（HTML 侧） ───────────────────────────────────────────────
    ("esim_providers_single__calc_card_field",
     "Günstigster Volumentarif in diesem Markt"),
    ("esim_providers_single__calc_card_mine",
     "Günstigster {brand}-Tarif, der passt"),
    ("esim_providers_single__calc_card_unl",
     "Günstigster unlimited-Tarif in diesem Markt"),
    ("esim_providers_single__calc_days_label",
     "Reisedauer"),
    ("esim_providers_single__calc_dest_label",
     "Wohin reist du"),
    ("esim_providers_single__calc_eyebrow",
     "Reisekostenrechner"),
    ("esim_providers_single__calc_gb_label",
     "Daten pro Tag"),
    ("esim_providers_single__calc_gb_option",
     "{{ .n }} GB"),
    ("esim_providers_single__calc_h2",
     "Was {{ .brand }} für deine Reise kosten würde"),
    ("esim_providers_single__calc_lead",
     "Wähle ein Reiseziel, eine Reisedauer und deinen voraussichtlichen Tagesbedarf. Wir stellen den eigenen Katalog von {{ .brand }} den günstigsten Tarifen im selben Markt gegenüber. Ein Tarif qualifiziert sich, wenn seine Gültigkeit die Reise und sein Datenvolumen deinen Bedarf abdeckt; unlimited-Tarife qualifizieren sich immer."),
    ("esim_providers_single__calc_more",
     'Die vollständige markenübergreifende Variante mit einem Nutzungsschätzer, der App-Stunden in Gigabyte umrechnet, findest du im <a href="/tools/">Reisekostenrechner</a>.'),
    ("esim_providers_single__calc_na",
     "In diesem Markt nicht erhältlich"),
    ("esim_providers_single__calc_need",
     "Eine Reise über {days} Tage mit {gb} GB pro Tag braucht etwa {need} GB."),
    ("esim_providers_single__calc_nocover",
     "Kein einzelner Tarif deckt {need} GB in {days} Tagen ab — die größte Stufe ist mit einem Kauf erreichbar."),
    ("esim_providers_single__calc_noscript",
     "Dieser Rechner benötigt JavaScript. Dieselben Marktvergleiche stehen in den Preistabellen und der Alternativentabelle weiter oben auf dieser Seite."),
    ("esim_providers_single__calc_plan_line",
     "{price} für {data} über {days} Tage"),
    ("esim_providers_single__calc_unit_days",
     "{n} Tage"),
    ("esim_providers_single__calc_unit_unl",
     "unlimited"),
    ("esim_providers_single__calc_v_above",
     "Etwa {pct}% über der Untergrenze."),
    ("esim_providers_single__calc_v_floor",
     "{brand} liegt bei ${pergb}/GB gegenüber einer Marktuntergrenze von ${floor}/GB von {floorBrand} ({floorData})."),
    ("esim_providers_single__calc_v_level",
     "Auf oder unter der Untergrenze."),
    ("esim_providers_single__calc_v_unl",
     "Unlimited für {days} Tage für {price}. Der günstigste unlimited-Tarif in diesem Markt ist {alt} von {altBrand}."),
    ("esim_providers_single__channels",
     "Kanäle"),
    ("esim_providers_single__choose_the_country_package_and_pay_online_the_esim_arriv",
     "Wähle das Länderpaket und zahle online — die eSIM kommt innerhalb von Minuten per E-Mail, noch vor der Reise."),
    ("esim_providers_single__countries_entry_price_from",
     "Länder; Einstiegspreis ab"),
    ("esim_providers_single__customer_support",
     "Kundensupport"),
    ("esim_providers_single__data_starts_when_you_land",
     "Die Daten starten bei der Landung"),
    ("esim_providers_single__destinations_coverage",
     "Reiseziele & Abdeckung"),
    ("esim_providers_single__destinations_tracked",
     "Erfasste Reiseziele"),
    ("esim_providers_single__email",
     "E-Mail"),
    ("esim_providers_single__entry_plan_price_vs_the_next_cheapest_provider_in_the_sa",
     "Einstiegspreis gegenüber dem nächstgünstigeren Anbieter im selben Land. Jeder Gewinner oben trägt außerdem ein"),
    ("esim_providers_single__every_price_badge_and_ranking_on_this_page_is_a_literal_",
     "Jeder Preis, jedes Label und jede Rangfolge auf dieser Seite ist eine wörtliche Sortierposition aus unserer Preisdatenbank — kein redaktionelles Bezahlen für Rankings. Wie wir Daten erheben und prüfen, steht in unserer"),
    ("esim_providers_single__fair_use_audit",
     "Fair-Use-Prüfung"),
    ("esim_providers_single__google_play",
     "Google Play ↗"),
    # ── 直接对决 ────────────────────────────────────────────────────────
    ("esim_providers_single__h2h_count",
     "{{ .rival }} ist in {{ .n }} der {{ .total }} Märkte, in denen er verkauft, der günstigste Anbieter — gegenüber {{ .mine }} bei {{ .brand }}."),
    ("esim_providers_single__h2h_entry",
     "Sein Einstiegspreis liegt bei ${{ .price }} gegenüber ${{ .mine }} bei {{ .brand }}."),
    ("esim_providers_single__h2h_eyebrow",
     "Direktduell"),
    ("esim_providers_single__h2h_full",
     "Vollständiger Vergleich {{ .brand }} vs. {{ .rival }}"),
    ("esim_providers_single__h2h_h2",
     "Die zwei Marken, die {{ .brand }} am nächsten kommen"),
    ("esim_providers_single__h2h_lead",
     "Diese beiden sind nicht von Hand ausgewählt. Wir ordnen jeden Rivalen danach, wie nah seine Bilanz an der Zahl der Günstigster-Markt-Siege von {{ .brand }} liegt, und zeigen die zwei nächsten. Die drei Zeilen unten sind die Zahlen, die sie tatsächlich trennen."),
    ("esim_providers_single__h2h_no_value",
     "Er verkauft nur unlimited-Tarife, hat also keinen $/GB-Wert zum Vergleichen."),
    ("esim_providers_single__h2h_value",
     "Sein bester Wert nach unserem $/GB-Maß ist ${{ .price }}/GB gegenüber ${{ .mine }}/GB."),
    # ── 价格分布 / 覆盖 ────────────────────────────────────────────────
    ("esim_providers_single__highest_entry_prices",
     "Höchste Einstiegspreise"),
    ("esim_providers_single__install_the_app_and_buy_in_app",
     "App installieren und direkt in der App kaufen"),
    ("esim_providers_single__it_activates_on_arrival",
     "Sie aktiviert sich bei der Ankunft"),
    ("esim_providers_single__last_updated",
     "Zuletzt aktualisiert am {{ .date }}"),
    ("esim_providers_single__lowest_entry_prices",
     "Niedrigste Einstiegspreise"),
    # ── 网络 ────────────────────────────────────────────────────────────
    ("esim_providers_single__network_5g_cheap_lead",
     "Märkte, in denen 5G aktiv ist und {{ .brand }} zugleich der günstigste Anbieter ist, den wir erfassen:"),
    ("esim_providers_single__network_5g_cheap_none",
     "In diesen Märkten ist 5G aktiv, doch {{ .brand }} ist in keinem davon der günstigste Anbieter — prüfe die Preistabelle oben, bevor du annimmst, das schnellste Netz komme zum besten Preis."),
    ("esim_providers_single__network_5g_title",
     "5G ist in {{ .n5g }} von {{ .total }} Märkten aktiv"),
    ("esim_providers_single__network_eyebrow",
     "Netzrealität"),
    ("esim_providers_single__network_footnote",
     "Geschwindigkeiten und Generationen stammen aus unseren Länder-Netzprofilen, erstellt aus Betreibermaterial und Messungen Dritter."),
    ("esim_providers_single__network_h2",
     "Auf welchen lokalen Netzen {{ .brand }} fährt"),
    ("esim_providers_single__network_lead",
     "Eine eSIM baut keine Masten. In jedem Markt kauft {{ .brand }} Kapazität bei den nationalen Betreibern des Landes — die unten genannten Netze sind also dieselben, die jeder Wiederverkäufer dort nutzt. Wir profilieren {{ .n }} davon."),
    ("esim_providers_single__network_lte_lead",
     "Die Gastgebernetze in diesen Märkten laufen nur mit LTE, keine eSIM einer Marke kann also schneller sein:"),
    ("esim_providers_single__network_lte_none",
     "Jeder Markt, den wir erfassen, hat aktives 5G auf mindestens einem Gastgebernetz — lokal ist also die Abdeckung und nicht die Generation zu prüfen."),
    ("esim_providers_single__network_lte_title",
     "Wo 5G gar nicht verfügbar ist"),
    ("esim_providers_single__no_editorial_star_rating_just_the_numbers_computed_the_s",
     ". Keine redaktionelle Sternebewertung — nur die Zahlen, für jede Marke gleich berechnet."),
    ("esim_providers_single__official_site",
     "Offizielle Website ↗"),
    ("esim_providers_single__one_tap_installs_the_esim",
     "Ein Tippen installiert die eSIM"),
    ("esim_providers_single__or_browse",
     "oder durchsuche"),
    ("esim_providers_single__pick_your_destination_and_plan_inside_the_app_checkout_e",
     "Wähle Reiseziel und Tarif direkt in der App — Checkout, eSIM und Nachbuchen liegen an einem Ort, keine E-Mail-Gutscheine."),
    ("esim_providers_single__plan_shape",
     "Tarifform"),
    ("esim_providers_single__price_check_in_progress",
     "Preisprüfung läuft"),
    ("esim_providers_single__price_competitiveness_index_editorial",
     "Preiswettbewerbsindex (redaktionell)"),
    ("esim_providers_single__price_range",
     "Preisspanne"),
    ("esim_providers_single__price_record",
     "Preisbilanz"),
    ("esim_providers_single__provider_overview",
     "Anbieterübersicht"),
    # ── 阅读区 ──────────────────────────────────────────────────────────
    ("esim_providers_single__reading_data_h3",
     "Woher diese Zahlen kommen"),
    ("esim_providers_single__reading_data_note",
     "Jede Zahl hier ist aus unserer Preisdatenbank berechnet — {{ .plans }} Tarife von {{ .brand }} über {{ .countries }} Reiseziele, Listenpreise in USD vor Rabattcodes und Steuern, neu erstellt am {{ .date }}. Rangfolgen sind Sortierpositionen, keine redaktionellen Bewertungen."),
    ("esim_providers_single__reading_eyebrow",
     "Weiterlesen"),
    ("esim_providers_single__reading_fup",
     "Fair-Use-Prüfung über jeden unlimited-Tarif"),
    ("esim_providers_single__reading_guide_compat",
     "Ist dein Handy eSIM-fähig"),
    ("esim_providers_single__reading_guide_dualsim",
     "Eine eSIM neben deiner eigenen SIM nutzen"),
    ("esim_providers_single__reading_guide_install",
     "So installierst du eine eSIM"),
    ("esim_providers_single__reading_guide_region",
     "Beste eSIM für {{ .region }}"),
    ("esim_providers_single__reading_guides_h3",
     "Ratgeber für deine Reise"),
    ("esim_providers_single__reading_h2",
     "Was du sonst noch prüfen solltest, bevor du {{ .brand }} kaufst"),
    ("esim_providers_single__reading_index",
     "Der eSIM-Preisindex"),
    ("esim_providers_single__reading_reviews_h3",
     "Was Kundinnen und Kunden von {{ .brand }} anderswo berichten"),
    ("esim_providers_single__reading_reviews_link",
     "{{ .brand }}-Bewertungen auf Trustpilot lesen"),
    ("esim_providers_single__reading_reviews_none",
     "{{ .brand }} hat kein Trustpilot-Unternehmensprofil, das wir verifizieren könnten — es gibt also keine öffentliche Sternebewertung, auf die wir dich redlich verweisen können. Seiten, die eine nennen, wiederholen meist das Marketing von {{ .brand }} selbst oder das Profil eines ähnlich benannten Wettbewerbers. Beurteile es stattdessen an dem, was du selbst prüfen kannst: die datierten Preise auf dieser Seite, die Fair-Use-Bedingungen in der Tariftabelle und das Rückgabefenster in der Profilkarte oben."),
    ("esim_providers_single__reading_reviews_note",
     "Wir veröffentlichen keine Sternebewertung für {{ .brand }}. Dieselbe Marke schneidet je nach Trustpilot-Domain unterschiedlich ab, die Werte bewegen sich wöchentlich, und ein Durchschnitt verdeckt genau den Teil, der deine Reise vorhersagt — die Ein-Stern-Bewertungen, die sich auf die eSIM häufen, die nach der Landung keine Verbindung bekommt. Lies diese, filtere nach deinem eigenen Reiseziel und gewichte die letzten zwei Monate. Jede Zahl auf dieser Seite ist datiert und reproduzierbar; eine geliehene Punktzahl wäre es nicht."),
    ("esim_providers_single__reading_unlimited",
     "Die Liga der unlimited-eSIMs"),
    # ── 现实区（4G / 声音） ──────────────────────────────────────────────
    ("esim_providers_single__reality_4g_note",
     "Nur LTE in {{ .list }} — dort kann dir keine Marke 5G verkaufen."),
    ("esim_providers_single__reality_5g_count",
     "5G in {{ .n5g }} von {{ .total }} Märkten"),
    ("esim_providers_single__reality_5g_link",
     "Geschwindigkeiten und Abdeckung je Land stehen in der"),
    ("esim_providers_single__reality_5g_text",
     "5G kommt von den lokalen Netzen, nicht von der Marke. Wir profilieren {{ .n }} Betreibernetze in den Märkten, in denen {{ .brand }} verkauft; 5G ist dort aktiv, wo das Land es ausgebaut hat."),
    ("esim_providers_single__reality_eyebrow",
     "Jenseits des Preisschilds"),
    ("esim_providers_single__reality_h2",
     "Hotspot, 5G und Fair-Use-Regeln bei {{ .brand }}"),
    ("esim_providers_single__reality_voice",
     "Jeder Tarif ist ein reiner Datentarif — deine eigene Nummer bleibt für Anrufe und SMS."),
    ("esim_providers_single__response_time",
     "Antwortzeit"),
    ("esim_providers_single__same_provider_very_different_entry_prices_by_country_if_",
     "Derselbe Anbieter, sehr unterschiedliche Einstiegspreise je Land. Liegt dein Reiseziel in der rechten Spalte, vergleiche vor dem Kauf mit der vollständigen Tabelle."),
    ("esim_providers_single__scan_the_qr_code",
     "QR-Code scannen"),
    ("esim_providers_single__settings_cellular_add_esim_ios_or_the_equivalent_on_andr",
     "Einstellungen → Mobilfunk → eSIM hinzufügen (iOS) oder das Gegenstück auf Android — das Profil lädt herunter und bleibt ruhend, bis der Gültigkeitszeitraum beginnt."),
    ("esim_providers_single__support_refunds",
     "Support & Erstattungen"),
    ("esim_providers_single__the_computed_verdict",
     "Das berechnete Urteil"),
    ("esim_providers_single__the_line_registers_on_the_local_partner_network_when_you",
     "Die Leitung registriert sich bei der Landung im lokalen Partnernetz. Brauchst du später mehr Daten? Kaufe ein neues Paket und installiere es genauso."),
    ("esim_providers_single__the_mechanics",
     "Die Mechanik"),
    ("esim_providers_single__the_plan_activates_per_its_validity_window_if_you_run_lo",
     "Der Tarif aktiviert sich nach seinem Gültigkeitsfenster; wird es knapp, kaufe ein Nachbuchungspaket in der App und behalte dieselbe eSIM."),
    ("esim_providers_single__the_refund_policy_in_short",
     "Die Rückgabepolitik in Kürze"),
    ("esim_providers_single__typical_entry_price_across_its_markets",
     "Typischer Einstiegspreis über seine Märkte:"),
    # ── 谁更便宜 ────────────────────────────────────────────────────────
    ("esim_providers_single__who_beats_caveat",
     "Wie wir abgeglichen haben: zuerst dieselbe Datenmenge und Gültigkeit wie der günstigste Tarif von {{ .brand }} in diesem Markt; verkauft kein Rivale genau diese Kombination, der günstigste Rivalentarif, der mindestens genauso viel Datenvolumen und mindestens genauso viele Tage abdeckt; gibt es auch den nicht, bleibt der Markt weg, statt ungleiche Tarife zu vergleichen. Beide Preise sind datierte Listenpreise vor Rabattcodes und Steuern."),
    ("esim_providers_single__who_beats_col_gap",
     "Differenz"),
    ("esim_providers_single__who_beats_col_mine",
     "{{ .brand }} günstigster"),
    ("esim_providers_single__who_beats_col_rival",
     "Günstigerer Rivale"),
    ("esim_providers_single__who_beats_col_rival_price",
     "Preis des Rivalen"),
    ("esim_providers_single__who_beats_eyebrow",
     "Alternativen nach Markt"),
    ("esim_providers_single__who_beats_h2",
     "Wer {{ .brand }} beim Preis schlägt und wohin du stattdessen gehst"),
    ("esim_providers_single__who_beats_lead",
     "Eine andere Marke verkauft in {{ .n }} der {{ .total }} Märkte, in denen wir {{ .brand }} erfassen, einen vergleichbaren Tarif günstiger. Wir vergleichen Gleiches mit Gleichem: identisches Datenvolumen und identische Gültigkeit, wo ein Rivale so etwas verkauft, sonst der nächstliegende Rivalentarif, der mindestens genauso viel Datenvolumen und mindestens genauso viele Tage abdeckt. Jede Differenz unten ist ein echter Listenpreisunterschied aus demselben datierten Schnappschuss; wo nichts wirklich vergleichbar ist, listen wir nichts."),
    ("esim_providers_single__who_beats_none",
     "In allen {{ .total }} Märkten, in denen wir {{ .brand }} erfassen, verkauft keine andere verglichene Marke einen vergleichbaren Tarif günstiger. Das ist ungewöhnlich und wissenswert, bevor du weiter suchst — aber es ist ein Preisbefund, keine Empfehlung für deine Reise."),
    ("esim_providers_single__who_beats_route",
     "Die Marke, die {{ .brand }} am häufigsten schlägt, ist {{ .rival }} — vorne in {{ .n }} dieser Märkte. Lies den Test oder öffne ein vollständiges Duell"),
    ("esim_providers_single__wondering_which_local_towers_it_connects_to_every_provid",
     "Du fragst dich, mit welchen lokalen Masten er sich verbindet? Jeder Anbieter fährt je Reiseziel auf denselben Gastgebernetzen — siehe die"),
    ("esim_providers_single__mult_suffix",
     "{{ .mult }}&times;"),
]

# 同形词白名单：德语与英语**完全同形**是正确译法（专有名词 / SI 单位 / 纯标记），
# 保留英文占位会被 i18n_coverage.py 继续计入「未译」——这是**已知假阳性**，显式记账。
SAME_FORM = {
    "esim_providers_single__app_store",            # App Store（德语同形）
    "esim_providers_single__google_play",          # Google Play（专有名词）
    "esim_providers_single__calc_gb_option",       # "{{ .n }} GB"（GB 是 SI 单位）
    "esim_providers_single__calc_unit_unl",        # "unlimited" 借词（全站策略未定，见 MEMORY §11）
    "esim_providers_single__mult_suffix",          # "{{ .mult }}&times;"（纯标记）
}

RE_GO = re.compile(r"\{\{.*?\}\}", re.S)
RE_JS = re.compile(r"\{[A-Za-z_][A-Za-z0-9_]*\}")


def load(path: Path) -> dict[str, str]:
    out: dict[str, str] = {}
    for line in path.read_text(encoding="utf-8").splitlines():
        s = line.strip()
        if s and not s.startswith("#") and " = " in line:
            k, v = line.split(" = ", 1)
            out[k.strip()] = json.loads(v.strip())
    return out


def ph(value: str) -> tuple[tuple[str, ...], tuple[str, ...]]:
    go = tuple(sorted(RE_GO.findall(value)))
    rest = RE_GO.sub("", value)
    js = tuple(sorted(RE_JS.findall(rest)))
    return go, js


def main() -> int:
    en, de = load(EN), load(DE)
    bad = 0

    for k, v in T:
        if k not in en:
            print(f"!! {k} 不在 en.toml 里"); bad += 1; continue
        eg, ej = ph(en[k])
        dg, dj = ph(v)
        if (eg, ej) != (dg, dj):
            print(f"!! 占位符不一致 {k}\n     en={eg}{ej}\n     de={dg}{dj}"); bad += 1
        if k in SAME_FORM and v != en[k]:
            print(f"!! {k} 在白名单里但值变了"); bad += 1
    if bad:
        print(f"\n{bad} 处问题，未写盘。")
        return 1

    raw = DE.read_bytes()
    text = raw.decode("utf-8")
    for k, v in T:
        pat = re.compile(r"(?m)^%s = .*$" % re.escape(k))
        hits = pat.findall(text)
        if len(hits) != 1:
            print(f"!! {k} 在 de.toml 命中 {len(hits)} 行"); return 1
        text = pat.sub(lambda _m, kk=k, vv=v: f"{kk} = {json.dumps(vv, ensure_ascii=False)}",
                       text, count=1)

    data = text.encode("utf-8")
    if data.count(b"\r\n"):
        print("!! 产物出现 CRLF"); return 1
    DE.write_bytes(data)

    after = load(DE)
    still = [k for k, _ in T if after.get(k) == en.get(k)]
    print(f"OK 写入 {len(T)} 条德语译文（de.toml {len(raw)} -> {len(data)} B）")
    print(f"   仍与英文同形的：{len(still)} 条 -> {sorted(still)}")
    unexpected = sorted(set(still) - SAME_FORM)
    if unexpected:
        print(f"!! 未预期的同形：{unexpected}"); return 1
    print("   同形全部落在白名单内（德语本就该同形）")
    return 0


if __name__ == "__main__":
    sys.exit(main())
