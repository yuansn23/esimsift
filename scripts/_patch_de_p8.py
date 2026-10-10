#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""D8 页型的德语 i18n（第 8 批）：`esim_deals_list`（112）+ `tools_list`（48）= 160 条。

为什么这批必须做：`/de/esim-deals/` 与 `/de/tools/` 是**新建的德语栏目页**，
它们的正文全部由模板 + i18n 渲染 —— 只写德语 `title`/`description` 不够。
d32 构建实测：守卫 F 在这两页报 10 处英文词（`days` / `and` / `plans` /
`countries` / `every`），G 段报 1 条数据串残留。

剩余 189 条（`research_*` / `guides_*` / `networks_*` / `compare_single` 等）
留给第 9 批 `_patch_de_p9.py`。

    判据（四条）：
      ① key 必须存在于 `i18n/en.toml`（拼错即报）
      ② **当前德语值必须逐字节等于英文值** —— 防止覆盖已人工审校过的译文
      ③ 占位符集合必须相等（`{{ .n }}` 之类；本批全部是 `{{ .x }}` 形态）
      ④ 德语不得凭空多出数字（`1.1 GB` → `1,1 GB` 是允许的写法差异，
         `20%` → `20 %` 同理；但 `30` 变成 `30–50` 就是错译）

用法：
  python -X utf8 scripts/_patch_de_p8.py [--dry]
  python -X utf8 scripts/_patch_de_p8.py --selftest
"""
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
I18N = ROOT / "i18n"
RE_GO = re.compile(r"\{\{\s*\.\w+\s*\}\}")
RE_NUM = re.compile(r"\d+")

T: dict[str, str] = {
    # ── esim_deals_list（112）──
    "esim_deals_list__a_30_day_bundle_on_a_5_day_trip_is_money_in_the_bin_our":
        "Ein 30-Tage-Paket auf einer 5-Tage-Reise ist rausgeworfenes Geld. Unser",
    "esim_deals_list__across_our_tracked_countries_the_gap_between_the_cheapes":
        "Über alle erfassten Länder hinweg ist die Lücke zwischen dem günstigsten und dem teuersten Anbieter im selben Reiseziel regelmäßig größer als der Rabatt jedes Codes. Der",
    "esim_deals_list__all_providers": "Alle Anbieter",
    "esim_deals_list__already": "bereits",
    "esim_deals_list__and_each_country_page_s_how_to_choose_section_size_the_p":
        "und der Abschnitt „So wählst du“ jeder Landesseite den Tarif auf deine Tage und Gewohnheiten zuschneidet.",
    "esim_deals_list__and_find_the_plan_you_actually_want_a_code_on_the_wrong_":
        "und finde den Tarif, den du wirklich willst — ein Code auf dem falschen Tarif ist immer noch zu viel bezahlt.",
    "esim_deals_list__aud_all": "Alle Nutzer",
    "esim_deals_list__aud_conditional": "Bedingungen gelten",
    "esim_deals_list__aud_existing": "Bestandskunden",
    "esim_deals_list__aud_new": "Neukunden",
    "esim_deals_list__backup_codes": "Ersatzcodes, falls der Hauptcode abgelehnt wird",
    "esim_deals_list__before_paying_for_data_you_won_t_use":
        "bevor du für Daten zahlst, die du nicht nutzt.",
    "esim_deals_list__best_overall_no_conditions": "Insgesamt am besten — ohne Bedingungen",
    "esim_deals_list__bestfor": "Am besten für:",
    "esim_deals_list__beyond_codes": "Jenseits von Codes",
    "esim_deals_list__black_friday_and_summer_sales_can_hit_30_50_at_some_prov":
        "Black Friday und Sommersales erreichen bei manchen Anbietern 30–50 %. Unsere Tabellen zeigen immer den Listenpreis, damit du einen echten Rabatt von einem aufgeblähten „statt“-Preis unterscheiden kannst. Gemerkt",
    "esim_deals_list__buy_through_the_provider": "Beim Anbieter kaufen",
    "esim_deals_list__buy_with_the_get_button_beside_the_code_so_the_code_s_co":
        "Kaufe über die Schaltfläche „Holen“ neben dem Code, damit Land und Berechtigung des Codes zu deiner Bestellung passen.",
    "esim_deals_list__cheapest_at_list_price_if_a_code_appears_it_lands_on_thi":
        "beim Listenpreis am günstigsten. Erscheint ein Code, steht er an dem Tag auf dieser Seite, an dem wir ihn prüfen können.",
    "esim_deals_list__check_the_new_total": "Prüfe die neue Summe",
    "esim_deals_list__codes_never_change_how_activation_works":
        "— Codes ändern nie, wie die Aktivierung funktioniert.",
    "esim_deals_list__compare_every_provider_we_track": "Vergleiche jeden erfassten Anbieter",
    "esim_deals_list__compare_first": "Erst vergleichen",
    "esim_deals_list__copy": "Kopieren",
    "esim_deals_list__data_calculator": "Datenschätzer",
    "esim_deals_list__data_calculator_2": "Datenschätzer",
    "esim_deals_list__disclosure_codes_above_are_affiliate_partner_codes_where":
        "Offenlegung: Die Codes oben sind Affiliate-Partnercodes, wenn der Anbieter gesponserter Partner ist — ihre Nutzung kann eSIM Sift eine Provision einbringen, ohne Mehrkosten für dich. Das ändert nie die Tarifreihenfolge in unseren Vergleichen (siehe",
    "esim_deals_list__do_seasonal_sales_beat_the_everyday_price":
        "Schlagen Saisonaktionen den Alltagspreis",
    "esim_deals_list__esim_promo_code_questions": "Fragen zu eSIM-Rabattcodes",
    "esim_deals_list__every_head_to_head_computed_country_by_country":
        "Jeder Direktvergleich, Land für Land berechnet.",
    "esim_deals_list__flip_cell": "{{ .n }} von {{ .total }} Ländern",
    "esim_deals_list__flip_legend_body":
        "Wir erfassen {{ .total }} Länder. „Kein Code nötig“ zählt die Länder, in denen diese Marke schon beim Listenpreis den günstigsten Tarif hat. „Mit angewandtem Code“ wiederholt denselben Test nach dem Rabatt — 1 → 2 heißt also, der Gutschein gewinnt genau ein Land dazu, und „keine Änderung“ heißt, der Code ändert nicht, wer am günstigsten ist.",
    "esim_deals_list__flip_legend_head": "So liest du diese Tabelle:",
    "esim_deals_list__flip_more": "+{{ .n }} weitere",
    "esim_deals_list__flip_no_change": "keine Änderung",
    "esim_deals_list__flip_th_group":
        "In wie vielen der {{ .total }} erfassten Länder ist diese Marke die günstigste Option?",
    "esim_deals_list__flip_th_price": "Günstigster Tarif",
    "esim_deals_list__flip_th_price_sub": "Listenpreis → mit angewandtem Code",
    "esim_deals_list__flip_th_with": "Mit angewandtem Code",
    "esim_deals_list__flip_th_without": "Kein Code nötig",
    "esim_deals_list__four_ways_to_save_that_beat_most_coupon_boxes":
        "Vier Spartipps, die die meisten Gutscheinboxen schlagen",
    "esim_deals_list__how_to_redeem": "So löst du ein",
    "esim_deals_list__how_to_use_an_esim_promo_code": "So nutzt du einen eSIM-Rabattcode",
    "esim_deals_list__install_and_go": "Installieren und los",
    "esim_deals_list__install_the_esim_per_our": "Installiere die eSIM nach unserem",
    "esim_deals_list__is_the_fastest_way_back": "ist der schnellste Weg zurück.",
    "esim_deals_list__live_codes_verified_against_real_prices":
        "Live-Codes gegen echte Preise geprüft",
    "esim_deals_list__look_for_the_promo_code_or_discount_code_field_at_checko":
        "Suche beim Checkout (Web) oder im Zahlungsfenster (App) das Feld „Promo-Code“ bzw. „Rabattcode“ — kopiere ihn aus der Karte oben.",
    "esim_deals_list__match_the_plan_to_the_trip_instead_of_the_headline":
        "Pass den Tarif an die Reise an statt an die Schlagzeile",
    "esim_deals_list__matrix_col_pick": "Beste Wahl",
    "esim_deals_list__matrix_col_situation": "Deine Situation",
    "esim_deals_list__matrix_eyebrow": "Entscheidungshilfe",
    "esim_deals_list__matrix_intro":
        "Hinter jeder Rabattzahl in der Schlagzeile steckt eine Bedingung — wer sie nutzen darf, wofür und wie oft. Diese Tabelle dreht die Frage um: Wähle zuerst deine Situation, und sie nennt den Code, der wirklich passt — berechnet zur Build-Zeit aus den Bedingungen auf dieser Seite.",
    "esim_deals_list__matrix_title": "Welcher Code zu deiner Situation passt",
    "esim_deals_list__method_for_every_country_the_provider_s_cheapest_plan_pr":
        "Methode: Für jedes Land wird der günstigste Tarifpreis des Anbieters × (1 − Rabatt) gegen den günstigsten Tarif irgendeines Anbieters in diesem Land gestellt. Gleichstand zählt nur dann als weiterhin #1, wenn der Anbieter schon beim Listenpreis #1 war. Die vollen Formeln stehen im",
    "esim_deals_list__min_spend": "Mindestbestellwert:",
    "esim_deals_list__no_code_needed": "Kein Code nötig",
    "esim_deals_list__no_expiry": "kein Ablaufdatum veröffentlicht",
    "esim_deals_list__no_strings": "Keine — ohne jede Bedingung",
    "esim_deals_list__no_strings_detail":
        "Kein Mindestbestellwert, keine Kundengrenzen, keine Tarifgrenzen — der Code gilt beim Checkout für jede Bestellung.",
    "esim_deals_list__open_the": "Öffne die",
    "esim_deals_list__page": "Seite.",
    "esim_deals_list__params_cta": "Code verwenden bei {{ .brand }}",
    "esim_deals_list__params_eyebrow": "Das Gesamtbild",
    "esim_deals_list__params_intro":
        "Die Karten oben erzählen jeweils die Geschichte einer Marke. Dieses Raster stellt dieselben Parameter für alle Marken nebeneinander, damit du sie in einem Durchgang vergleichen kannst — den Rabatt, wer berechtigt ist, was er abdeckt, wie oft du ihn nutzen kannst, wann er abläuft und die Einschränkungen, die nie in die Schlagzeile kommen. Die Preise nach jedem Code stehen weiter unten auf dieser Seite.",
    "esim_deals_list__params_legend_body":
        "Zuerst die wenigsten Einschränkungen, dann der größte Rabatt — nie danach, wer uns bezahlt. Jeder Wert stammt aus den eigenen veröffentlichten Bedingungen des Anbieters oder von dem Dritten, der den Code veröffentlicht; das Badge sagt, welche Quelle, und jede Zeile trägt das Datum unserer letzten Prüfung. „Nicht angegeben“ heißt, der Anbieter hat keine Grenze veröffentlicht — wir erfinden keine.",
    "esim_deals_list__params_legend_head": "Wie diese Tabelle sortiert ist:",
    "esim_deals_list__params_th_code": "Bester Code",
    "esim_deals_list__params_th_covers": "Was er abdeckt",
    "esim_deals_list__params_th_discount": "Rabatt",
    "esim_deals_list__params_th_expiry": "Ablauf",
    "esim_deals_list__params_th_limits": "Einschränkungen",
    "esim_deals_list__params_th_often": "Wie oft",
    "esim_deals_list__params_th_who": "Wer berechtigt ist",
    "esim_deals_list__params_title": "Alle eSIM-Rabattcodes nebeneinander vergleichen",
    "esim_deals_list__params_verdict_body":
        "Schon auf eine Marke festgelegt? Nimm die Zeile dieser Marke — ein Code schlägt keinen Code, auch wenn er klein ist, und prüfe dann die Preistabelle unten, ob er diese Marke tatsächlich zur günstigsten macht. Noch unentschieden? Nimm eine Zeile, die in der Spalte Einschränkungen nichts stehen hat: Diese Codes können an der Kasse nicht aus Berechtigungsgründen abgelehnt werden. Davon gibt Roamis web20 als einziger auch 20 %; jeder andere Code hier ab 20 % — Sailys 25 %, Yesims 20 % und Nomads BEYOND20 mit 20 % — hat mindestens einen Haken.",
    "esim_deals_list__params_verdict_head": "Welche Zeile ist deine?",
    "esim_deals_list__paste_before_paying": "Vor dem Bezahlen einfügen",
    "esim_deals_list__price_index": "Preisindex",
    "esim_deals_list__right_provider_beats_20_off_the_wrong_one":
        "Der richtige Anbieter schlägt 20 % beim falschen",
    "esim_deals_list__saves_on_a_real_plan_and_because_we_run_a_full_price_dat":
        "auf einen echten Tarif spart. Und weil wir eine vollständige Preisdatenbank führen, zeigen wir auch, wann ein Rabattcode trotzdem gegen einen günstigeren Anbieter ganz ohne Code verliert.",
    "esim_deals_list__savings_examples_are_computed_from_the_plan_prices_in_ou":
        "). Die Sparbeispiele werden zur Prüfzeit aus den Tarifpreisen unserer Datenbank berechnet.",
    "esim_deals_list__shows_the_spread_country_by_country_start_there_not_at_a":
        "zeigt die Spanne Land für Land — starte dort, nicht auf einer Gutscheinseite.",
    "esim_deals_list__sit_biggest":
        "Du jagst den größten Rabatt aus der Schlagzeile und prüfst, ob er angekommen ist",
    "esim_deals_list__sit_first": "Dies ist dein erster Kauf bei einem Anbieter",
    "esim_deals_list__sit_no_strings":
        "Du willst einen Code, der einfach bei jedem Tarif funktioniert",
    "esim_deals_list__sit_returning": "Du hast schon einmal bei diesem Anbieter gekauft",
    "esim_deals_list__sit_unlimited": "Du willst einen Unlimited-Tarif",
    "esim_deals_list__size_the_plan_before_you_pay_for_it":
        "Bemiss den Tarif, bevor du ihn bezahlst.",
    "esim_deals_list__src_official": "Offizieller Code",
    "esim_deals_list__src_partner": "Drittanbieter-Code",
    "esim_deals_list__step_1": "Schritt 1",
    "esim_deals_list__step_2": "Schritt 2",
    "esim_deals_list__step_3": "Schritt 3",
    "esim_deals_list__step_4": "Schritt 4",
    "esim_deals_list__step_5": "Schritt 5",
    "esim_deals_list__step_by_step_guide": "Schritt-für-Schritt-Anleitung",
    "esim_deals_list__the_50_country_gb_league_table": "Die $/GB-Rangliste über 50 Länder.",
    "esim_deals_list__the_line_total_must_drop_before_you_pay_if_it_doesn_t_th":
        "Die Zeilensumme muss vor dem Bezahlen sinken. Tut sie es nicht, ist der Code tot oder dein Tarif nicht berechtigt — probiere nicht mit zufälligen Codes weiter.",
    "esim_deals_list__these_providers_had_no_verifiable_public_promo_code_when":
        "Diese Anbieter hatten bei unserer letzten Prüfung keinen überprüfbaren öffentlichen Rabattcode. Statt einen zufälligen Gutschein aus einem Forum einzufügen, starte mit den Zahlen: Hier ist jeder",
    "esim_deals_list__this_page": "diese Seite",
    "esim_deals_list__unlimited_isn_t_automatically_expensive":
        "Unlimited ist nicht automatisch teuer",
    "esim_deals_list__unlimited_plans_win_on_price_once_your_usage_passes_a_br":
        "Unlimited-Tarife gewinnen beim Preis, sobald dein Verbrauch einen Break-even-Punkt überschreitet (rund 1,1 GB/Tag im mittleren erfassten Land). Prüfe",
    "esim_deals_list__unlimited_vs_metered": "Unlimited vs. Volumen",
    "esim_deals_list__uses_not_stated": "Nicht angegeben",
    "esim_deals_list__uses_once": "Einmal pro Kunde",
    "esim_deals_list__uses_repeatable": "Jede Bestellung",
    "esim_deals_list__when_a_discount_code_still_loses": "Wann ein Rabattcode trotzdem verliert",
    "esim_deals_list__when_unlimited_is_cheaper": "wann Unlimited günstiger ist",
    "esim_deals_list__when_unlimited_plans_are_actually_cheaper":
        "Wann Unlimited-Tarife tatsächlich günstiger sind.",
    "esim_deals_list__which_providers_have_no_discount_code":
        "Welche Anbieter keinen Rabattcode haben",
    "esim_deals_list__zero_conditions_head":
        "Null Bedingungen — dieser Code gilt für alle, jedes Mal",
    # ── tools_list（48）──
    "tools_list__1_200_mb_hour": "1.200 MB/Stunde",
    "tools_list__3_mb_per_photo": "3 MB pro Foto",
    "tools_list__5_mb_hour": "5 MB/Stunde",
    "tools_list__7_days": "7 Tage",
    "tools_list__a_plan_matches_when_its_validity_covers_your_trip":
        "Ein Tarif passt, wenn seine Gültigkeit deine Reise abdeckt",
    "tools_list__activity": "Aktivität",
    "tools_list__add_a_20_safety_margin": "20 % Sicherheitsmarge hinzurechnen",
    "tools_list__and_ranked_by_gb_in_the": "und nach $/GB gereiht im",
    "tools_list__compare_esim_providers_side_by_side":
        "eSIM-Anbieter nebeneinander vergleichen",
    "tools_list__country_index": "Länderindex",
    "tools_list__data_need": "Datenbedarf",
    "tools_list__day_trip_rounded_up": "-Tage-Reise, aufgerundet",
    "tools_list__destination": "Reiseziel",
    "tools_list__documents_how_every_price_these_rates_feed_into_is_colle":
        "dokumentiert, wie jeder Preis erhoben wird, in den diese Raten einfließen.",
    "tools_list__don_t_know_how_many_gigabytes_you_need_start_from_what_y":
        "Du weißt nicht, wie viele Gigabyte du brauchst? Starte bei dem, was du online tatsächlich machst — der Schätzer unten rechnet deine Apps in GB um und dann in den einen günstigsten echten Tarif, der deine Reise abdeckt.",
    "tools_list__email_without_attachments": "E-Mail ohne Anhänge",
    "tools_list__esim_prices_for_the_most_compared_destinations":
        "eSIM-Preise für die meistvergleichten Reiseziele",
    "tools_list__every_brand_whose_plans_we_track_with_the_cheapest_listi":
        "Jede Marke, deren Tarife wir erfassen, mit dem günstigsten Angebot, das wir je von ihr erfasst haben. Das vollständige Preisverhalten — wo jede am günstigsten ist und wo es weh tut — steht auf ihrer Testseite, und Paar-für-Paar-Fazits im Duell-Index.",
    "tools_list__find_the_cheapest_plan_for_this": "Günstigsten Tarif dafür finden →",
    "tools_list__for_your": "Für deine",
    "tools_list__free_tool": "Kostenloses Tool",
    "tools_list__heavy_10gb": "Viel · 10 GB",
    "tools_list__how_do_you_pick_the_right_esim_plan_for_your_trip":
        "Wie wählst du den richtigen eSIM-Tarif für deine Reise",
    "tools_list__how_it_works": "So funktioniert es",
    "tools_list__how_much_data_do_you_need_for_your_trip":
        "Wie viele Daten brauchst du für deine Reise?",
    "tools_list__how_much_data_each_app_uses_per_hour":
        "Wie viele Daten jede App pro Stunde verbraucht",
    "tools_list__its_data_covers_your_need_unlimited_plans_always_satisfy":
        "sein Datenvolumen deinen Bedarf deckt. Unlimited-Tarife bestehen den Datentest immer; die Fair-Use-Grenzen stehen auf jeder Vergleichsseite.",
    "tools_list__light_1gb": "Wenig · 1 GB",
    "tools_list__photo_upload_to_cloud": "Foto-Upload in die Cloud",
    "tools_list__plans_from": "Tarife ab",
    "tools_list__prices_in_usd_excluding_promo_codes_and_taxes_data_re_ch":
        "Preise in USD, ohne Rabattcodes und Steuern. Daten neu geprüft an den Daten, die auf jeder Landesseite stehen.",
    "tools_list__rates_are_industry_typical_figures_at_default_app_qualit":
        "Die Raten sind branchenübliche Werte bei Standard-App-Qualität; Streaming in 4K oder Auto-Qualität auf großem Bildschirm kann sie verdoppeln. Unsere",
    "tools_list__set_roughly_how_many_hours_a_day_you_spend_on_each_activ":
        "Stell grob ein, wie viele Stunden am Tag du mit jeder Aktivität verbringst. Wir rechnen die Stunden mit den Raten aus unserer Referenztabelle unten in Gigabyte um — und übergeben die Summe direkt an den Rechner.",
    "tools_list__sets_your_data_need_in_the_calculator_below_and_re_picks":
        "Setzt deinen Datenbedarf im Rechner unten und wählt den Sieger aus echten Tarifen neu.",
    "tools_list__standard_5gb": "Standard · 5 GB",
    "tools_list__the_destinations_where_the_most_providers_compete_usuall":
        "Die Reiseziele, in denen die meisten Anbieter konkurrieren — meist dort, wo die Preise am schärfsten sind. Jede Karte öffnet die vollständige Landestabelle mit allen Tarifen nebeneinander.",
    "tools_list__the_rates": "Die Raten",
    "tools_list__this_calculator_is_powered_by_our_full_price_database_em":
        "Dieser Rechner läuft auf unserer vollständigen Preisdatenbank — binde ihn auf deiner eigenen Reiseseite ein (verlinke zurück auf eSIM Sift, und wir halten die Daten frisch). Siehe",
    "tools_list__traveler_estimating_esim_data_needs_before_a_trip":
        "Reisender schätzt den eSIM-Datenbedarf vor einer Reise",
    "tools_list__trip_length": "Reisedauer",
    "tools_list__two_brands_on_your_shortlist_every_pairing_airalo_vs_hol":
        "Zwei Marken auf deiner Liste? Jede Paarung — Airalo vs Holafly inklusive — wird Land für Land bewertet im",
    "tools_list__typical_data_use": "Typischer Datenverbrauch",
    "tools_list__typical_rates_at_default_quality_settings_the_same_numbe":
        "Typische Raten bei Standard-Qualität — dieselben Zahlen, die der Schätzer oben nutzt. Apps unterscheiden sich, und die Qualitätseinstellung einer Video-App zählt weit mehr als die App selbst; behandle sie als Planungszahlen und lass die 20-%-Marge die Differenz auffangen.",
    "tools_list__usage_estimator": "Verbrauchsschätzer",
    "tools_list__video_upload_1080p": "Video-Upload (1080p)",
    "tools_list__what_1gb_buys_you": "Was 1 GB dir bringt",
    "tools_list__your_daily_usage": "Dein Tagesverbrauch",
    "tools_list__your_estimate": "Deine Schätzung",
}


def load(p: Path) -> dict[str, str]:
    out: dict[str, str] = {}
    for line in p.read_text(encoding="utf-8").splitlines():
        s = line.strip()
        if s and not s.startswith("#") and " = " in line:
            k, v = line.split(" = ", 1)
            out[k.strip()] = json.loads(v.strip())
    return out


def audit(pairs: dict[str, str], en: dict[str, str], de: dict[str, str]) -> list[str]:
    errs: list[str] = []
    for k, v in pairs.items():
        if k not in en:
            errs.append(f"{k} 不在 en.toml 里（拼错？）")
            continue
        if k not in de:
            errs.append(f"{k} 不在 de.toml 里")
            continue
        if de[k] != en[k]:
            errs.append(f"{k} 的德语值已不是英文占位（已人工审校？）—— 拒绝覆盖：{de[k]!r}")
        a, b = set(RE_GO.findall(en[k])), set(RE_GO.findall(v))
        if a != b:
            errs.append(f"{k} 占位符不一致：en={sorted(a)} de={sorted(b)}")
        extra = set(RE_NUM.findall(v)) - set(RE_NUM.findall(en[k]))
        if extra:
            errs.append(f"{k} 德语凭空多出数字 {sorted(extra)}：en={en[k]!r} de={v!r}")
    return errs


def selftest() -> None:
    ok = bad = 0

    def chk(c: bool, n: str) -> None:
        nonlocal ok, bad
        if c:
            ok += 1
            print(f"  [OK] {n}")
        else:
            bad += 1
            print(f"  [!!] {n}")

    base_en = {
        "k1": "All providers",
        "k2": "{{ .n }} of {{ .total }} countries",
        "k3": "20% off plans",
    }
    base_de = {k: v for k, v in base_en.items()}

    chk(not audit({"k1": "Alle Anbieter"}, base_en, base_de), "正例 A：普通值通过")
    chk(not audit({"k2": "{{ .n }} von {{ .total }} Ländern"}, base_en, base_de),
        "正例 B：占位符保留 + 语序调整通过")
    chk(not audit({"k3": "20 % Rabatt auf Tarife"}, base_en, base_de),
        "正例 C：`20%` → `20 %` 的写法差异不算多数字")
    chk(bool(audit({"kX": "x"}, base_en, base_de)), "反例 A：key 拼错被抓住")
    chk(bool(audit({"k2": "{{ .n }} Länder"}, base_en, base_de)), "反例 B：漏占位符被抓住")
    chk(bool(audit({"k3": "30–50 % Rabatt"}, base_en, base_de)), "反例 C：凭空多数字被抓住")
    e2, d2 = dict(base_en), dict(base_de)
    d2["k1"] = "Alle Anbieter"
    chk(bool(audit({"k1": "Irgendwas"}, e2, d2)), "反例 D：覆盖已译值被拒绝")

    print(f"\nselftest: {ok} 项通过 / {bad} 项失败")
    sys.exit(1 if bad else 0)


if "--selftest" in sys.argv:
    selftest()

DRY = "--dry" in sys.argv
en, de = load(I18N / "en.toml"), load(I18N / "de.toml")
errs = audit(T, en, de)
if errs:
    print(f"!! {len(errs)} 项断言失败：")
    for e in errs[:40]:
        print("   " + e)
    sys.exit(1)

print(f"断言通过：{len(T)} 条待写（de.toml 现有 {len(de)} key）")
if DRY:
    sys.exit(0)

p = I18N / "de.toml"
raw = p.read_bytes()
crlf = raw.count(b"\r\n")
text = raw.decode("utf-8")
missing = [k for k in T if f"\n{k} = " not in "\n" + text]
if missing:
    sys.exit(f"ERROR: 这些 key 在 de.toml 里找不到行（无法原地替换）：{missing[:5]}")

lines = text.split("\n")
out: list[str] = []
done: set[str] = set()
for line in lines:
    m = re.match(r"^([A-Za-z0-9_]+) = ", line)
    if m and m.group(1) in T:
        k = m.group(1)
        out.append(f'{k} = {json.dumps(T[k], ensure_ascii=False)}')
        done.add(k)
    else:
        out.append(line)
if set(done) != set(T):
    sys.exit(f"ERROR: 只替换了 {len(done)}/{len(T)} 行")
new = "\n".join(out)
p.write_bytes(new.encode("utf-8"))
assert p.read_bytes().count(b"\r\n") == crlf, "CRLF 被改变"
# 本批全部是**原地替换**（key 早已存在、值还是英文占位），因此总 key 数必须不变。
# 旧写法 `len(de) + len(T)` 只对「新增 key」的批次成立 —— 会把正确的写入判成失败。
assert len(de) == len(load(p)), f"key 总数变了：{len(de)} -> {len(load(p))}"
print(f"OK 写入 {len(T)} 条（de.toml {len(raw)} -> {len(new.encode('utf-8'))} B）")
