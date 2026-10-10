# -*- coding: utf-8 -*-
"""研究栏目德语页面（第 68 轮 · 批 B 之二）—— 建 3 篇德语子页 + 补栏目索引。

前置依赖（必须先跑）：
  `scripts/_patch_research_de_keys.py` —— 107 条 research i18n 德语译文。
  否则这三张页会印英文（模板里的 h1/h2/表格头全部走 i18n）。

页面结构对齐英文侧（`content/en/research/*.md`）：
  · 英文子页正文只有 1 段（页面主体全在 `layouts/research/<layout>.html`），德语同样；
  · `date` 与英文页一致（同一份数据快照）；
  · `noindex: true` —— 分层发布纪律：只有 `/de/` 首页可索引，其余德语页等 D9 那一轮统一解禁；
  · 站内链接用**显式 `/de/` 前缀**（德语 md 的既有约定），下列路径均已核实存在：
    /de/compare/ · /de/research/{esim-price-index,fair-use-audit,unlimited-esim}/ ·
    /de/tools/ · /de/methodology/
  · 页内锚点（#league / #audit / #howpriced）不带前缀。

`content/de/research/_index.md` 补齐 `hero` / `hero_alt` / `faq_heading` / `faqs`（6 条）
与 3 段正文 —— 与英文 `_index.md` 同构；`faq_heading` 在 `research/list.html:179` 渲染成
**h2**、FAQ 问句渲染成 **h3**，故德语值一律避开 `,;:—–`（check_headings.py 会拦）。

用法：python -X utf8 scripts/_patch_research_de_pages.py [--dry]
"""
from __future__ import annotations

import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
TODO = "# TODO(de)：分层发布 —— 全站德语译文解禁（D9 那一轮）时删掉上面这行。"

PRICE_INDEX = """---
title: "eSIM-Preisindex 2026: Jedes Land nach Preis sortiert"
date: 2026-10-01
description: "Jedes Reiseziel in unserer Datenbank nach seinem günstigsten Preis pro Gigabyte sortiert — regionale Durchschnitte und vollständige Rangliste."
layout: price-index
noindex: true
{TODO}
---

Wo Sie reisen, verändert die Datenkosten stärker als die Wahl des Anbieters. Der folgende Index sortiert alle {{< count-countries >}} Reiseziele unserer Datenbank nach ihrem günstigsten Preis pro Gigabyte — die eine Zahl, die am besten erfasst, wie teuer ein Land beim Vernetztbleiben ist. Die günstigsten und die teuersten Länder unterscheiden sich um ein Mehrfaches pro Gigabyte, und das Muster ist regional: [lesen Sie die vollständige Rangliste unten](#league) oder beginnen Sie mit den Extremen.
""".replace("{TODO}", TODO)

FAIR_USE = """---
title: "Fair-Use-Prüfung 2026: Was „unlimited“ wirklich bedeutet"
date: 2026-10-01
description: "Was unbegrenzte eSIM-Tarife wirklich drosseln: eSIM Sift prüft die Fair-Use-Richtlinie jedes erfassten Anbieters, Tarif für Tarif, wörtlich."
layout: fair-use-audit
noindex: true
{TODO}
---

Jede „unbegrenzte“ eSIM trägt eine Fair-Use-Richtlinie (FUP) — eine Schwelle oder Heuristik, die Ihre Verbindung lange vor Ablauf des Zeitraums verlangsamen kann. Anbieter verstecken diese Richtlinien selten, aber sie vergraben sie. Diese Prüfung zieht den Fair-Use-Hinweis aus jedem Unlimited-Tarif unserer Datenbank, zitiert ihn wörtlich und bewertet jeden Anbieter danach, ob seine Einträge überhaupt einen nennen. Wenn Sie sich nur eines merken: **Unlimited ist ein Abrechnungsbegriff, kein Geschwindigkeitsversprechen** — was Ihr Anbieter sagt, steht in [der Prüfungstabelle](#audit).
""".replace("{TODO}", TODO)

UNLIMITED = """---
title: "Beste Unlimited-eSIM 2026: Tagespreise im Vergleich"
date: 2026-10-01
description: "Beste Unlimited-eSIM-Tarife im Vergleich: eSIM Sift sortiert Tagespreise für jedes Land mit unbegrenzten Daten, plus die Fair-Use-Fallen."
layout: unlimited-esim
noindex: true
{TODO}
---

Unlimited klingt nach einem Produkt, ist aber wie ein Hotelzimmer bepreist: pro Tag. Damit ist der Tagespreis — Gesamtpreis geteilt durch Laufzeit in Tagen — die einzige ehrliche Art, Unlimited-eSIMs über Länder und Anbieter hinweg zu vergleichen. Unten steht jedes Reiseziel unserer Datenbank mit mindestens einem Unlimited-Tarif, sortiert nach dem besten Tagespreis, den ein Anbieter dort erreicht. Bevor Sie sich entscheiden, lesen Sie [wie die Preisgestaltung funktioniert](#howpriced) und was „unlimited“ rechtlich bedeutet in unserer [Fair-Use-Prüfung](/de/research/fair-use-audit/).
""".replace("{TODO}", TODO)

NEW_PAGES = {
    "content/de/research/esim-price-index.md": PRICE_INDEX,
    "content/de/research/fair-use-audit.md": FAIR_USE,
    "content/de/research/unlimited-esim.md": UNLIMITED,
}

# ── 栏目索引：把「缺 hero/faq + 空正文」的壳补成与英文侧同构 ──
IDX_ANCHOR = 'description: "Eigene Auswertungen aus der eSIM-Sift-Preisdatenbank — Ranglisten nach Preis pro GB, Fair-Use-Analysen und Unlimited-Daten im Vergleich."\n'
IDX_INSERT = IDX_ANCHOR + """hero: "travel-esim-illustration-142.webp"
hero_alt: "Reisender prüft eSIM-Preistabellen und Datentrends auf dem Smartphone — unabhängige eSIM-Preisanalyse"
faq_heading: "Häufige Fragen zu unseren eSIM-Analysen"
"""

IDX_TAIL_OLD = """# 未做的还有：3 篇子页正文（研究页模板里仍有英文硬编码，须先补 i18n key）。
---
"""
IDX_TAIL_NEW = """# 2026-10-10 复核：3 篇子页已建，研究模板 23 处英文硬编码已抽成 i18n 整句（第 68 轮）。
faqs:
  - q: "Wie oft werden die eSIM-Preise geprüft?"
    a: "Jeder Tarif in der Datenbank trägt einen datierten Datenstand — das Abzeichen oben auf dieser Seite zeigt das jüngste Prüfdatum, und jede Analyse-Seite wiederholt es. Wir erheben und berechnen neu, statt veraltete Feeds erneut zu veröffentlichen."
  - q: "Woher stammen die eSIM-Preise?"
    a: "Direkt aus den Einträgen der Anbieter, aus offiziellen Websites und Apps, dann in $/GB und $/Tag normalisiert, damit unterschiedliche Tarifformen ehrlich vergleichbar sind. Die Regeln für Erhebung und Normalisierung sind in unserer Methodik dokumentiert."
  - q: "Warum unterscheiden sich eSIM-Preise zwischen Ländern so stark?"
    a: "Der lokale Wettbewerb der Netze setzt die Untergrenze. Ein Markt mit mehreren aggressiven Anbietern bepreist Daten weit unter einem Markt, der von ein oder zwei Platzhirschen dominiert wird, und Reise-eSIMs geben diesen Unterschied fast eins zu eins weiter — die regionale Tabelle auf dieser Seite macht das Muster sichtbar."
  - q: "Sind unbegrenzte eSIM-Daten wirklich unbegrenzt?"
    a: "Meist unbegrenzt im Volumen, aber nicht in der Geschwindigkeit. Die meisten Unlimited-Tarife halten die volle Geschwindigkeit bis zu einem Tages- oder Gesamtkontingent und drosseln danach. Die Fair-Use-Prüfung zitiert das Kleingedruckte jedes Anbieters, damit die tatsächliche Grenze vor dem Kauf sichtbar ist."
  - q: "Was begrenzt eine Fair-Use-Richtlinie tatsächlich?"
    a: "Fast immer die Geschwindigkeit nach einer Schwelle — manchmal ein Tageslimit, manchmal ein Gesamtlimit über die Laufzeit. Die Grenzen stehen in den Tarifbedingungen, nicht im Marketing, deshalb zitieren wir sie in der Prüfung wörtlich."
  - q: "Welches Land hat derzeit die günstigsten eSIM-Daten?"
    a: "Die aktuelle Tabelle oben auf dieser Seite zeigt immer die aktuellen Top 5 nach bestem $/GB, und die vollständige Rangliste mit den Tarifen jedes Anbieters steht im Preisindex."
---

Jede Zahl in diesem Bereich wird berechnet, nicht geschrieben. Die Ranglisten unten entstehen aus demselben datierten Datenstand echter Prepaid-Tarife, der auch unsere [Ländervergleiche](/de/compare/) speist — {{< count-countries >}} Reiseziele, {{< count-providers >}} Anbieter, Tausende Tarife, eine Sortierung.

Das ist wichtig, weil die meisten eSIM-Ranglisten, die Sie online treffen, Werbetexte in Tabellenform sind: ein Affiliate-Feed, neu veröffentlicht mit anderer Schrift. Wir erheben die Listenpreise jedes Anbieters neu, normalisieren sie in Dollar pro Gigabyte und Dollar pro Tag und zitieren das Fair-Use-Kleingedruckte wörtlich, statt es wegzuformulieren. Wenn ein Anbieter einen Unlimited-Tarif still begrenzt, landet diese Tatsache in der [Fair-Use-Prüfung](/de/research/fair-use-audit/), nicht unter den Teppich.

Nutzen Sie sie wie ein Nachschlagewerk — beginnen Sie bei der Frage, die Sie tatsächlich haben. Der [Preisindex](/de/research/esim-price-index/) beantwortet, wo Daten am günstigsten sind, die Fair-Use-Prüfung beantwortet, was unlimited wirklich bedeutet, und die [Unlimited-Datenstudie](/de/research/unlimited-esim/) beantwortet, was ein Tag Daten kosten sollte. Reisende, die eine Zahl für ihre eigenen Daten wollen, springen direkt zum [Reisekostenrechner](/de/tools/); wer das Innenleben sehen will, liest [wie wir Preise erheben](/de/methodology/).
"""


def main() -> int:
    dry = "--dry" in sys.argv
    n_new = n_skip = 0

    for rel, body in NEW_PAGES.items():
        p = ROOT / rel
        if p.exists():
            cur = p.read_text(encoding="utf-8")
            if cur == body:
                print(f"  skip  {rel}: 内容一致")
                n_skip += 1
            else:
                raise SystemExit(f"{rel}: 已存在且内容不同 —— 人工确认后再动")
            continue
        if not dry:
            p.parent.mkdir(parents=True, exist_ok=True)
            p.write_bytes(body.encode("utf-8"))
        print(f"  NEW   {rel} ({len(body.encode('utf-8'))} bytes)")
        n_new += 1

    # 栏目索引
    rel = "content/de/research/_index.md"
    b = (ROOT / rel).read_bytes()
    if b.count(b"\r\n"):
        raise SystemExit(f"{rel}: 预期 LF 行尾")
    src = b.decode("utf-8")
    if "hero_alt:" in src and "faq_heading:" in src:
        print(f"  skip  {rel}: 已补")
    else:
        if src.count(IDX_ANCHOR) != 1:
            raise SystemExit(f"{rel}: description 锚点命中 {src.count(IDX_ANCHOR)} 次")
        if src.count(IDX_TAIL_OLD) != 1:
            raise SystemExit(f"{rel}: 尾部锚点命中 {src.count(IDX_TAIL_OLD)} 次")
        src = src.replace(IDX_ANCHOR, IDX_INSERT, 1).replace(IDX_TAIL_OLD, IDX_TAIL_NEW, 1)
        if not dry:
            (ROOT / rel).write_bytes(src.encode("utf-8"))
        print(f"  EDIT  {rel}: +hero/hero_alt/faq_heading/faqs + 3 段正文")

    print(f"{'(dry-run) ' if dry else ''}新建 {n_new} / 跳过 {n_skip} / 索引已处理")
    return 0


if __name__ == "__main__":
    sys.exit(main())
