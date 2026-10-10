# -*- coding: utf-8 -*-
"""研究栏目德语译文（第 68 轮 · 批 B）—— 107 条 research key 的德语落地。

为什么单独一个脚本：本批是**纯文本替换**（de.toml 的值 EN -> DE），
不动结构与行数，因此必须用 bytes 读写 + 三条前置断言：
  1. 每个 key 在 de.toml 里**恰好 1 行**；
  2. 脚本里的 key 集合**精确等于**「en/de 值逐字相同」的 research key 集合
     —— 既防拼写漏译，也防「译了却忘写进脚本」；
  3. 幂等：值已经是目标德语则跳过（复跑全「skip」）。
行尾断言 LF（en.toml / de.toml 实测 0 个 CRLF）。

译写纪律（与同栏目已译样本对齐）：
  · 人称用 **Sie**（`research_unlimited_esim__no_every_...` 既有译文即 Sie）；
  · 术语：Tarif / Anbieter / Länder / Reiseziel / Kontingent / Fair-Use / Unlimited / Break-even；
  · 单位与小数按德语惯例：`$/Tag`、`GB/Tag`、`$3,90`；
  · **h2/h3 禁 `,;:—–`** ⇒ 两处标题刻意避开逗号
    （`four_things_to_check_...` -> "Vier Dinge zum Prüfen bei jedem Unlimited-Tarif"、
      `how_do_you_spot_...` -> "Woran erkennen Sie eine Fair-Use-Falle vor dem Kauf"）；
  · 碎片 key（以 `=` / `.` 开头）保持碎片形态，拼接点在模板侧不动。

用法：python -X utf8 scripts/_patch_research_de_keys.py [--dry]
"""
from __future__ import annotations

import json
import pathlib
import sys
import tomllib

ROOT = pathlib.Path(__file__).resolve().parents[1]

PI = "research_price_index__"
FU = "research_fair_use_audit__"
UE = "research_unlimited_esim__"

KEYS: list[tuple[str, str]] = [
    # ── research_price_index__ (30) ──
    (PI + "5_cheapest_per_gb", "5 günstigste pro GB"),
    (PI + "5_priciest_per_gb", "5 teuerste pro GB"),
    (PI + "airalo_vs_holafly_and_every_other_head_to_head_computed_",
     "Airalo vs. Holafly und jedes andere Duell, Land für Land berechnet."),
    (PI + "best_gb_is_the_cheapest_per_gigabyte_rate_any_provider_o",
     "„Bestes $/GB“ ist der günstigste Preis pro Gigabyte, den ein Anbieter dort bietet — meist ein"
     " großes Kontingent, nicht der Einstiegstarif. Jedes Land und jeder Siegertarif ist ein Link:"
     " Der Ländername öffnet die vollständige Anbietertabelle, der Tarif öffnet die Tarife dieses"
     " Anbieters für das Land."),
    (PI + "by", "von"),
    (PI + "by_region", "Nach Region"),
    (PI + "cheapest_vs_priciest_country", "Günstigstes vs. teuerstes Land"),
    (PI + "cite_it_fork_it_check_it", "Zitieren, nachrechnen, prüfen."),
    (PI + "each_region_s_average_gb_with_its_countries_ranked_cheap",
     "Der durchschnittliche $/GB jeder Region, darunter ihre Länder nach günstigstem Preis sortiert"
     " — klicken Sie auf ein Land, um seine vollständige Anbietertabelle zu sehen."),
    (PI + "esim_prices_by_country_every_gb_rate_computed_from_the_s",
     "eSIM-Preise nach Land — jeder $/GB-Wert aus demselben datierten Datenstand berechnet."),
    (PI + "every_number_here_is_a_literal_sort_of_the_same_dated_sn",
     "Jede Zahl hier ist eine wörtliche Sortierung desselben datierten Datenstands — keine"
     " redaktionellen Anpassungen. Die gesamte Datenbank erscheint auch als maschinenlesbares JSON,"
     " und der Erhebungsrhythmus ist dokumentiert in unserer"),
    (PI + "how_we_make_money", "Wie wir Geld verdienen"),
    (PI + "method_for_each_country_the_minimum_of_price_gb_over_eve",
     "Methode: Für jedes Land das Minimum aus Preis÷GB über jeden Kontingenttarif jedes Anbieters,"
     " aus demselben datierten Datenstand. Unlimited-Tarife (pro Tag) sind aus der $/GB-Spalte"
     " ausgeschlossen, werden aber in ihrer eigenen Spalte gezählt — siehe"),
    (PI + "phone_showing_esim_data_prices_for_different_countries",
     "Smartphone mit eSIM-Datenpreisen für verschiedene Länder"),
    (PI + "price_database_json", "Preisdatenbank (JSON)"),
    (PI + "read_it_like_a_traveler", "Wie ein Reisender gelesen"),
    (PI + "region", "Region"),
    (PI + "regional_averages_and_the_countries_behind_them",
     "Regionale Durchschnitte und die Länder dahinter"),
    (PI + "the_extremes", "Die Extreme"),
    (PI + "the_full_index", "Der vollständige Index"),
    (PI + "the_full_league_table_of_esim_prices_by_country",
     "Die vollständige Rangliste der eSIM-Preise nach Land"),
    (PI + "the_regional_gap", "Die regionale Lücke"),
    (PI + "what_10_buys_at_the_extremes", "Was $10 an den Extremen kauft"),
    (PI + "what_every_unlimited_plan_s_small_print_actually_throttl",
     "Was das Kleingedruckte jedes „unbegrenzten“ Tarifs tatsächlich drosselt, Anbieter für Anbieter."),
    (PI + "what_should_you_know_about_esim_prices_by_country",
     "Was Sie über eSIM-Preise nach Land wissen sollten"),
    (PI + "what_the_price_spread_means_for_your_trip",
     "Was die Preisspanne für Ihre Reise bedeutet"),
    (PI + "where_unlimited_data_is_cheapest_per_day_and_when_it_bea",
     "Wo unbegrenzte Daten pro Tag am günstigsten sind und wann sie ein Kontingent schlagen."),
    (PI + "which_countries_have_the_cheapest_and_priciest_esim_data",
     "Welche Länder die günstigsten und die teuersten eSIM-Daten haben"),
    (PI + "which_countries_have_the_cheapest_unlimited_esims",
     "welche Länder die günstigsten unbegrenzten eSIMs haben"),
    (PI + "winning_plan", "Siegertarif"),

    # ── research_fair_use_audit__ (40) ──
    (FU + "1_the_daily_rate_rather_than_the_sticker_price",
     "1 · Der Tagespreis statt des Listenpreises"),
    (FU + "2_whether_a_fair_use_note_exists_at_all",
     "2 · Ob überhaupt ein Fair-Use-Hinweis existiert"),
    (FU + "3_hotspot_sharing_rules", "3 · Regeln zur Hotspot-Nutzung"),
    (FU + "4_whether_a_big_metered_bucket_is_cheaper",
     "4 · Ob ein großes Kontingent günstiger ist"),
    (FU + "a_listing_with_no_fup_note_isn_t_a_promise_of_unthrottle",
     "Ein Eintrag ohne FUP-Hinweis ist kein Versprechen ungedrosselter Daten — er bedeutet nur, dass"
     " der Verkäufer keinen genannt hat. Behandeln Sie „nicht angegeben“ als „unbekannt“, nicht als"
     " „keiner“."),
    (FU + "before_committing", "bevor Sie sich entscheiden."),
    (FU + "carry_an_explicit_fup_note", "tragen einen ausdrücklichen FUP-Hinweis"),
    (FU + "country_price_table", "Preistabelle des Landes"),
    (FU + "destination_s_page", "Seite des Reiseziels"),
    (FU + "divide_the_price_by_the_days_the", "Teilen Sie den Preis durch die Tage. Die"),
    (FU + "does_this_for_every_country_we_track",
     "macht das für jedes Land, das wir erfassen."),
    (FU + "each_provider_s_plans_pricing_behavior_and_coverage_revi",
     "Die Tarife, das Preisverhalten und die Abdeckung jedes Anbieters im Überblick."),
    (FU + "every_country_s_cheapest_unlimited_rate_and_when_it_beat",
     "Der günstigste Unlimited-Preis jedes Landes und wann er Kontingentdaten schlägt."),
    (FU + "every_provider_head_to_head_computed_country_by_country",
     "Jedes Anbieterduell, Land für Land berechnet."),
    (FU + "every_tracked_unlimited_plan_carries_an_explicit_note",
     "= jeder erfasste Unlimited-Tarif trägt einen ausdrücklichen Hinweis;"),
    (FU + "every_unlimited_esim_carries_a_fair_use_policy_we_quote_",
     "Jede „unbegrenzte“ eSIM trägt eine Fair-Use-Richtlinie — wir zitieren jede wörtlich."),
    (FU + "every_unlimited_plan_s_note_is_also_shown_on_its_own_row",
     ". Der Hinweis jedes Unlimited-Tarifs steht auch in seiner eigenen Zeile in jeder"),
    (FU + "fair_use_notes_are_captured_verbatim_from_each_provider_",
     "Fair-Use-Hinweise werden zum Prüfzeitpunkt wörtlich aus dem Eintrag jedes Anbieters"
     " übernommen und nach unserem regulären Rhythmus erneut geprüft — siehe die"),
    (FU + "four_things_to_check_on_any_unlimited_plan",
     "Vier Dinge zum Prüfen bei jedem Unlimited-Tarif"),
    (FU + "how_do_you_spot_a_fair_use_catch_before_you_buy",
     "Woran erkennen Sie eine Fair-Use-Falle vor dem Kauf"),
    (FU + "if_your_usage_is_predictable_a_20gb_metered_plan_often_b",
     "Wenn Ihre Nutzung planbar ist, schlägt ein 20-GB-Kontingenttarif Unlimited beim Preis oft."
     " Prüfen Sie beide Tabellen auf Ihrer"),
    (FU + "no_note_on_any_tracked_listing", "kein Hinweis in keinem erfassten Eintrag"),
    (FU + "none_do_we_do_not_paraphrase_or_interpret_policies_notes",
     "= keiner. Wir paraphrasieren oder interpretieren Richtlinien nicht — Hinweise werden wörtlich"
     " zitiert."),
    (FU + "not_applicable", "nicht zutreffend"),
    (FU + "say_nothing_on_the_listing", "sagen nichts im Eintrag"),
    (FU + "sells_no_unlimited_plans", "verkauft keine Unlimited-Tarife"),
    (FU + "some_do", "= manche;"),
    (FU + "tethering_is_where_fair_use_policies_bite_hardest_some_p",
     "Beim Tethering beißen Fair-Use-Richtlinien am härtesten. Manche Tarife erlauben es, manche"
     " drosseln es, manche streichen es nach einer Schwelle — all das steht in den Tarifhinweisen"
     " auf jeder Länderseite."),
    (FU + "the_audit", "Die Prüfung"),
    (FU + "the_small_print_in_large_print", "Das Kleingedruckte, groß geschrieben."),
    (FU + "traveler_reading_the_fair_use_policy_of_an_unlimited_esi",
     "Reisende liest die Fair-Use-Richtlinie eines unbegrenzten eSIM-Tarifs"),
    (FU + "unlimited_league_table", "Unlimited-Rangliste"),
    (FU + "unlimited_on_an_esim_listing_never_means_unthrottled_we_",
     "„Unlimited“ in einem eSIM-Eintrag heißt nie ungedrosselt. Wir prüfen die Fair-Use-Richtlinie"
     " jedes Unlimited-Tarifs in unserer Datenbank — zum Prüfzeitpunkt wörtlich erfasst — und"
     " veröffentlichen, was das Kleingedruckte jedes Anbieters tatsächlich tut."),
    (FU + "unlimited_plans_tracked", "erfasste Unlimited-Tarife"),
    (FU + "unlimited_plans_tracked_2", "Erfasste Unlimited-Tarife"),
    (FU + "verdict", "Bewertung"),
    (FU + "verdict_reflects_only_what_a_provider_s_own_listing_stat",
     "„Bewertung“ gibt nur wieder, was der Eintrag eines Anbieters zum Prüfzeitpunkt angibt:"),
    (FU + "what_each_provider_s_unlimited_really_means",
     "Was „unlimited“ bei jedem Anbieter wirklich bedeutet"),
    (FU + "what_the_note_says", "Was im Hinweis steht"),
    (FU + "with_explicit_fup_note", "Mit ausdrücklichem FUP-Hinweis"),

    # ── research_unlimited_esim__ (37) ──
    (UE + "before_betting_a_heavy_streaming_trip_on_one",
     "bevor Sie eine starke Streaming-Reise darauf setzen."),
    (UE + "before_you_buy", "bevor Sie kaufen."),
    (UE + "best_daily_rate", "Bester Tagespreis"),
    (UE + "best_daily_rate_is_the_cheapest_price_per_day_any_provid",
     "„Bester Tagespreis“ ist der günstigste Preis pro Tag, den ein Unlimited-Tarif eines Anbieters"
     " in diesem Land erreicht. Jeder Eintrag ist ein Link: Der Ländername öffnet alle seine Tarife,"
     " der Anbietername öffnet die Tarife dieses Anbieters dort, der Tarifname öffnet den"
     " günstigsten Eintrag."),
    (UE + "break_even_best_unlimited_day_best_metered_gb_in_the_sam",
     "Break-even = bester Unlimited-$/Tag ÷ bester Kontingent-$/GB im selben Land, derselbe datierte"
     " Datenstand. Oberhalb des Break-even gilt weiterhin die Fair-Use-Drosselung — lesen Sie die"),
    (UE + "cheapest_unlimited_plan", "Günstigster Unlimited-Tarif"),
    (UE + "countries_with_unlimited_plans", "Länder mit Unlimited-Tarifen"),
    (UE + "divide_a_country_s_best_unlimited_daily_rate_by_its_best",
     "Teilen Sie den besten Unlimited-Tagespreis eines Landes durch seinen besten Kontingent-$/GB,"
     " erhalten Sie den Break-even: wie viele GB pro Tag Sie tatsächlich verbrauchen müssen, bevor"
     " sich Unlimited trägt. Wir haben ihn für jedes Land berechnet — die Spanne ist enorm."),
    (UE + "every_rate_on_this_page_is_a_literal_sort_of_the_same_da",
     "Jeder Preis auf dieser Seite ist eine wörtliche Sortierung desselben datierten Datenstands —"
     " kein Anbieter bezahlt für Platzierung, und Fair-Use-Fallen werden gezeigt, nicht versteckt."
     " Siehe die"),
    (UE + "every_unlimited_plan_we_track_carries_a_fair_use_policy_",
     "Jeder Unlimited-Tarif, den wir erfassen, trägt eine Fair-Use-Richtlinie, die Ihre"
     " Geschwindigkeit drosseln kann. Wir erfassen den Richtlinienhinweis jedes Tarifs wörtlich —"
     " siehe die"),
    (UE + "fair_use_note", "Fair-Use-Hinweis"),
    (UE + "fair_use_notes_are_recorded_verbatim_from_each_provider_",
     "Fair-Use-Hinweise werden zum Prüfzeitpunkt wörtlich aus dem Tarifeintrag jedes Anbieters"
     " erfasst; „nicht angegeben“ heißt, der Eintrag enthielt keinen ausdrücklichen Hinweis — pro"
     " Anbieter bewertet in der"),
    (UE + "holafly_vs_airalo_and_every_other_head_to_head_with_comp",
     "Holafly vs. Airalo und jedes andere Duell, mit berechneten Bewertungen."),
    (UE + "how_unlimited_esim_pricing_works",
     "Wie die Preisgestaltung bei Unlimited-eSIM funktioniert"),
    (UE + "longer_trips_mean_a_lower_daily_rate",
     "Längere Reisen bedeuten einen niedrigeren Tagespreis"),
    (UE + "median_break_even_per_day", "mittlerer Break-even pro Tag"),
    (UE + "most_providers_discount_longer_validity_the_cheapest_dai",
     "Die meisten Anbieter rabattieren längere Laufzeiten. Der günstigste Tagespreis eines Landes"
     " ist meist das 20–30-Tage-Paket, nicht das 5-Tage-Paket — unsere Tabelle zeigt immer den"
     " besten Preis."),
    (UE + "not_stated", "nicht angegeben"),
    (UE + "per_day_rather_than_per_gb", "Pro Tag statt pro GB"),
    (UE + "read_the_prices_right", "Preise richtig lesen"),
    (UE + "the_easiest_win_is", "Am leichtesten gewinnt"),
    (UE + "the_full_league", "Die vollständige Rangliste"),
    (UE + "the_hardest_win_is", "Am schwersten gewinnt"),
    (UE + "the_median_country", "Das mittlere Land"),
    (UE + "traveler_comparing_unlimited_esim_plans_on_a_phone",
     "Reisender vergleicht Unlimited-eSIM-Tarife auf dem Smartphone"),
    (UE + "unlimited_always_has_a_ceiling", "„Unlimited“ hat immer eine Obergrenze"),
    (UE + "unlimited_compared_honestly", "Unlimited, ehrlich verglichen."),
    (UE + "unlimited_esim_daily_rates_ranked_country_by_country",
     "Unlimited-eSIM-Tagespreise nach Land sortiert"),
    (UE + "unlimited_esim_plans_ranked_by_daily_rate_the_only_fair_",
     "Unlimited-eSIM-Tarife nach Tagespreis sortiert — der einzig faire Vergleich über Länder und"
     " Reiselängen hinweg."),
    (UE + "unlimited_esims_are_priced_per_day_so_the_only_fair_rank",
     "Unlimited-eSIMs werden pro Tag berechnet, also ist der Tagespreis die einzig faire Rangfolge."
     " Für jedes Land mit einem Unlimited-Tarif listen wir den niedrigsten Tagespreis über alle"
     " Anbieter — und die Fair-Use-Falle dahinter."),
    (UE + "unlimited_plans_sell_a_number_of_days_not_gigabytes_a_3_",
     "Unlimited-Tarife verkaufen eine Anzahl Tage, keine Gigabyte. Ein „$3,90/Tag“-Tarif für 7 Tage"
     " kostet vorab $27,30 — der Tagespreis ist die einzige Zahl, die über Reiselängen hinweg"
     " vergleichbar ist."),
    (UE + "what_every_unlimited_plan_s_small_print_actually_throttl",
     "Was das Kleingedruckte jedes „unbegrenzten“ Tarifs tatsächlich drosselt."),
    (UE + "what_should_you_know_before_buying_unlimited_esim_data",
     "Was Sie vor dem Kauf von Unlimited-eSIM-Daten wissen sollten"),
    (UE + "when_is_an_unlimited_esim_cheaper_than_metered_data",
     "Wann ist eine Unlimited-eSIM günstiger als Kontingentdaten?"),
    (UE + "when_unlimited_actually_wins", "Wann Unlimited wirklich gewinnt"),
    (UE + "which_providers_sell_unlimited_where_and_where_each_is_c",
     "Welche Anbieter wo Unlimited verkaufen — und wo jeder am günstigsten ist."),
    (UE + "who_sells_unlimited", "Wer verkauft Unlimited"),
]

BAD_HEADING_CHARS = ",;:—–"

# 德语与英语同形：`Region` 本就是德语词，「de 值 == en 值」的待译判据对它永远成立。
# 这不是漏译，必须从待译集合里显式排除，否则幂等复跑会把它误报成「缺 1 条」。
SAME_AS_EN_ON_PURPOSE = {"research_price_index__region"}


def load(path: str) -> dict:
    def flat(d, p=""):
        for k, v in d.items():
            if isinstance(v, dict):
                yield from flat(v, p + k + ".")
            else:
                yield p + k, v
    return dict(flat(tomllib.loads((ROOT / path).read_text(encoding="utf-8"))))


def main() -> int:
    dry = "--dry" in sys.argv
    en, de = load("i18n/en.toml"), load("i18n/de.toml")

    groups = ("research_price_index", "research_fair_use_audit", "research_unlimited_esim")
    group_keys = {k for k in en if k.split("__")[0] in groups}
    pending = {k for k in group_keys if de.get(k) == en.get(k)} - SAME_AS_EN_ON_PURPOSE
    mine = {k for k, _ in KEYS} - SAME_AS_EN_ON_PURPOSE
    print(f"待译集合 {len(pending)} / 脚本覆盖 {len(mine)}")
    if not mine <= set(en):
        raise SystemExit(f"脚本引用了 en.toml 不存在的 key: {sorted(mine - set(en))}")
    if pending == mine:
        pass  # 首次执行：脚本覆盖 == 待译全集，这是本脚本要证的覆盖性
    elif not pending:
        print("待译集合为空 —— 已应用，幂等复跑跳过覆盖校验")
    else:
        raise SystemExit(f"集合不匹配 —— 缺 {sorted(pending - mine)} / 多 {sorted(mine - pending)}")

    # 行数复核（替换不改行数）
    p = ROOT / "i18n/de.toml"
    raw = p.read_bytes()
    if raw.count(b"\r\n"):
        raise SystemExit("i18n/de.toml: 预期 LF 行尾")
    lines = raw.decode("utf-8").split("\n")
    n0 = len(lines)

    # 标题约束：会渲染成 h2/h3 的 key，德语值不得含禁用标点
    H2H3 = {
        "5_cheapest_per_gb", "5_priciest_per_gb", "cheapest_vs_priciest_country",
        "what_10_buys_at_the_extremes", "the_regional_gap",
        "what_should_you_know_about_esim_prices_by_country",
        "what_the_price_spread_means_for_your_trip",
        "regional_averages_and_the_countries_behind_them",
        "the_full_league_table_of_esim_prices_by_country",
        "which_countries_have_the_cheapest_and_priciest_esim_data",
        "1_the_daily_rate_rather_than_the_sticker_price",
        "2_whether_a_fair_use_note_exists_at_all", "3_hotspot_sharing_rules",
        "4_whether_a_big_metered_bucket_is_cheaper",
        "four_things_to_check_on_any_unlimited_plan",
        "how_do_you_spot_a_fair_use_catch_before_you_buy",
        "what_each_provider_s_unlimited_really_means",
        "how_unlimited_esim_pricing_works", "per_day_rather_than_per_gb",
        "longer_trips_mean_a_lower_daily_rate", "unlimited_always_has_a_ceiling",
        "when_is_an_unlimited_esim_cheaper_than_metered_data",
        "the_easiest_win_is", "the_median_country", "the_hardest_win_is",
        "unlimited_esim_daily_rates_ranked_country_by_country",
        "what_should_you_know_before_buying_unlimited_esim_data",
    }
    bad = [k for k, v in KEYS if k.split("__")[1] in H2H3
           and any(c in v for c in BAD_HEADING_CHARS)]
    if bad:
        raise SystemExit(f"h2/h3 德语值含禁用标点（check_headings.py 会拦）: {bad}")
    print(f"标题约束复核：{len(H2H3)} 个 h2/h3 key 全部通过")

    done = skip = 0
    for k, v in KEYS:
        hits = [i for i, l in enumerate(lines) if l.startswith(k + " = ")]
        if len(hits) != 1:
            raise SystemExit(f"de.toml: {k} 命中 {len(hits)} 行")
        new_line = f"{k} = {json.dumps(v, ensure_ascii=False)}"
        if lines[hits[0]] == new_line:
            skip += 1
            continue
        if not dry:
            lines[hits[0]] = new_line
        done += 1

    if not dry:
        out = "\n".join(lines)
        if len(lines) != n0:
            raise SystemExit(f"行数变了 {n0} -> {len(lines)}")
        p.write_bytes(out.encode("utf-8"))
    print(f"{'(dry-run) ' if dry else ''}写入 {done} 条 / 已是目标值 {skip} 条")

    if not dry:
        de2 = load("i18n/de.toml")
        left = sorted(({k for k in group_keys if de2.get(k) == en.get(k)}) - SAME_AS_EN_ON_PURPOSE)
        print(f"复核：research 待译剩 {len(left)} 条 -> {left}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
