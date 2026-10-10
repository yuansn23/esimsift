#!/usr/bin/env python3
"""批 D-1：`content/de/networks/japan.md` —— 德语正文。

结构 = 与 en 侧**逐字段对齐**（22 个 front matter 字段 + 正文 h2/h3 序列）。
德语纪律（`.buildlog/de_l10n_contract.md`）：
  · 人称 `du`（guides/networks/compare 一致）
  · 站内链显式 `/de/` 前缀；**外链一律裸写**（禁过 lang-href）
  · 单位 `Mbit/s`（禁 `Mbps`）
  · h2/h3 禁 `,` `;` `:`（`check_headings.py` 的 RELAXED；`—`/`–` 允许）
  · 短代码 `{{< count-providers >}}` 原样保留
用法：python -X utf8 scripts/_patch_networks_de_1.py [--dry]
"""
from __future__ import annotations

import argparse
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
REL = "japan.md"
EN = ROOT / "content" / "en" / "networks" / REL
DE = ROOT / "content" / "de" / "networks" / REL

DOC = '''---
title: "Japan Reise-eSIM Netze: Docomo, SoftBank und KDDI erklärt"
description: "Jede Reise-eSIM, die wir erfassen, fährt in Japan über Docomo, SoftBank oder KDDI. Wie sich die drei Netze bei 5G-Geschwindigkeit und Reichweite unterscheiden und was du zuerst prüfen solltest."
date: 2026-10-03
lastmod: 2026-10-03
iso: "JP"
noindex: true
# TODO(de)：分层发布 —— 全站德语译文解禁（D9 那一轮）时删掉上面这行。
seo:
  title: "Japan Reise-eSIM Netze 2026: Bestes 5G für Touristen"
kicker: "Japan läuft über drei Netze — Docomo, SoftBank und KDDI — und jede Reise-eSIM-Marke, die wir erfassen, fährt auf allen dreien. Die Abdeckung ist hier also keine Markenentscheidung. Was sich wirklich unterscheidet: welcher Betreiber bei der Geschwindigkeit gewinnt, welcher bis in die Berge reicht und was du vor dem Kauf prüfen solltest."
h2_carriers: "Die drei japanischen Netze hinter einer Reise-eSIM"
h2_scoreboard: "Docomo SoftBank und KDDI im unabhängigen Test"
h2_brands: "Das Heimatnetz je eSIM-Marke in Japan"
h2_cities: "Japanische Städte mit schnellem Netz bei allen Anbietern"
h2_next: "So bekommst du deine Japan-eSIM richtig hin"
h2_answer: "Was eine Japan-Reise-eSIM kann und was nicht"
h2_facts: "Fakten zum eSIM-Netz in Japan"
prompt_answer: "Japan hat drei nationale Mobilfunknetze — NTT Docomo, SoftBank und KDDI — und jede Reise-eSIM-Marke, die wir erfassen, fährt auf allen dreien. Eine Japan-eSIM ist also nicht an einen Betreiber gebunden. Docomo hat die größte Reichweite, SoftBank den schnellsten Download, und alle drei betreiben kommerzielles 5G. Die Regel, die Besucher erwischt, ist die Registrierung: Lokale Prepaid-SIMs brauchen eine Passprüfung, eine Reise-eSIM für Touristen braucht gar kein Dokument."
fact_registration: "Lokale Prepaid-SIMs brauchen eine Passprüfung. Eine Reise-eSIM braucht keine."
intro_carriers: "Japanische Reise-eSIM-Daten werden im Großhandel bei NTT Docomo, SoftBank oder KDDI eingekauft. Keine der Marken unten besitzt einen Masten in Japan, das Netz deines Tarifs entscheidet also das Reiseziel und nicht der Name auf dem Tarif. Jede Marke ist damit ein MVNO japanischer Netze, weshalb keine von ihnen eine Abdeckung versprechen kann, die die anderen nicht auch haben."
intro_brands: "Jede Marke unten listet alle drei japanischen Betreiber als Heimatnetze. Deshalb ist die Tabelle eine Preisliste und kein Abdeckungsvergleich, und deshalb ist eine billigere Japan-eSIM nicht automatisch die schwächere."
cities_note: "Tokio, Osaka, Kyoto und Fukuoka laufen auf allen drei Netzen mit schneller Abdeckung, die Signalqualität in den Städten ist also geklärt. Die japanische Frage ist die Reichweite außerhalb der großen Städte, in den Bergen und auf den Inseln — dort trennen sich Docomo, SoftBank und KDDI."
cities_detail:
  - name: "Tokio"
    reality: "Tokio ist auf allen drei Netzen geklärt, inklusive U-Bahn und Bahnnetz, und die Abdeckung hält entlang des Shinkansen-Korridors Richtung Nagoya und Osaka durchgehend."
  - name: "Osaka"
    reality: "Osaka ist auf allen drei Netzen geklärt, und der erste dünnere Boden liegt südlich auf der Kii-Halbinsel, wo Bergrouten zwischen den drei Fußabdrücken verlaufen."
  - name: "Kyoto"
    reality: "Kyoto ist auf allen drei Netzen dicht abgedeckt, auch im umgebenden Tal, und die Abdeckung dünnt auf den Landstraßen nach Norden zur Küste des Japanischen Meeres aus."
  - name: "Fukuoka"
    reality: "Fukuoka ist auf allen drei Netzen geklärt und Kyushu gut abgedeckt, womit die Inselfähren und die kleineren vorgelagerten Inseln der unsichere Teil bleiben."
faq_heading: "Fragen zu Japan-eSIM und Netz"
faqs:
  - q: "Wie viele Mobilfunknetze hat Japan?"
    a: "Drei nationale Betreibernetze tragen den Reise-eSIM-Verkehr in Japan — NTT Docomo, SoftBank und KDDI. Jeder Anbieter, den wir erfassen, verbindet sich bei dieser Prüfung mit allen dreien, eine Japan-eSIM ist also nicht an einen Betreiber gebunden wie ein günstiger Einzelnetz-Tarif in manchen Märkten. Rakuten Mobile betreibt in Japan ein viertes Netz, aber keine Reise-eSIM-Marke, die wir beobachten, listet es bei dieser Prüfung als Heimatnetz."
  - q: "Ist Docomo oder SoftBank das schnellere Netz in Japan?"
    a: "SoftBank gewinnt bei der Spitzen-Download-Geschwindigkeit in beiden Firmen, die den Markt messen — Opensignal verzeichnete im April 2026 65,1 Mbit/s beim Download, und Ookla kürte SoftBank für das erste Halbjahr 2026 zum schnellsten Mobilfunknetz Japans. Docomo antwortet mit Reichweite statt Geschwindigkeit und holt den Abdeckungspreis mit 9,0 von 10 sowie den 5G-Downloadpreis mit 159,1 Mbit/s. Lies die beiden Ranglisten getrennt: Opensignal berichtet die durchschnittliche Nutzererfahrung und Ookla den Median der Speedtest-Proben, die Rohzahlen sind also nicht miteinander vergleichbar."
  - q: "Enthalten alle Japan-eSIM-Tarife 5G?"
    a: "Ja. Alle drei nationalen Netze betreiben kommerzielles 5G und jedes Netzbetreiber-Profil, das wir erfassen, listet 5G — eine Japan-Reise-eSIM ist also kein 4G-Downgrade. Unabhängige Tests verorten Japans 5G deutlich im dreistelligen Mbit-Bereich: Opensignal maß Docomos 5G-Download mit 159,1 Mbit/s. Weil alle drei Netze es haben, lohnt sich in Japan kein Aufpreis für 5G; prüfe stattdessen, dass der Tarif selbst 5G listet und dass dein Telefon die japanischen Bänder unterstützt."
  - q: "Ändert das Netz hinter meiner Japan-eSIM tatsächlich etwas?"
    a: "Auf Markenebene nicht, denn jeder Anbieter, den wir erfassen, verbindet sich mit denselben drei nationalen Netzen — zwei Tarife zweier Marken auf derselben Reise fahren auf identischen Masten. Auf Tarifebene zählt es aber. Ein Multi-Netz-Tarif fällt automatisch über Docomo, SoftBank und KDDI zurück, und genau das hält dich außerhalb der Städte verbunden; ein auf einen Betreiber festgelegter Tarif erbt dessen Fußabdruck, in Japan also Docomo für Reichweite oder SoftBank für Geschwindigkeit. Keine der Marken, die wir erfassen, verkauft einen Einzelnetz-Tarif für Japan."
  - q: "Welches japanische Netz sollte ich für ländliche Gebiete und die Berge wählen?"
    a: "NTT Docomo, wegen der Reichweite. Es gewann den Abdeckungspreis von Opensignal für Japan im April 2026 mit 9,0 von 10 und deckt die Bergregionen, ländlichen Inseln und Kleinstädte ab, die die anderen zwei weniger vollständig erreichen — das Netz der Wahl, wenn deine Route über Tokio, Osaka und Kyoto hinausgeht. In der Praxis wählst du es selten direkt, weil die Japan-Tarife, die wir erfassen, alle über alle drei Betreiber zurückfallen und das Gerät das stärkste verfügbare Signal nimmt. Was du wählen kannst: einen Tarif meiden, der auf ein einziges Netz festgelegt ist."
  - q: "Können Touristen eine Prepaid-SIM oder eSIM direkt bei einem japanischen Betreiber kaufen?"
    a: "Eine Prepaid-SIM ja, aber mit Reibung. Japanisches Recht verlangt eine Passprüfung für lokale Prepaid-Karten von SoftBank, Docomo und KDDI, und SoftBanks eigene Touristen-SIM lässt sich nur zwischen 09:00 und 21:00 JST aktivieren — ein unbequemes Fenster, wenn du nach Einbruch der Dunkelheit in Narita oder Haneda landest. Reise-eSIMs umgehen beide Beschränkungen vollständig: kein Dokumenten-Upload bei irgendeinem Schritt, und die Aktivierung funktioniert zu jeder Stunde, was der Hauptgrund ist, warum eine Japan-eSIM für eine kurze Reise eine Betreiber-Prepaid-Karte schlägt."
  - q: "Gibt es unbegrenzte Daten mit einer Japan-eSIM für Touristen?"
    a: "Ja. Mehrere der Marken, die wir erfassen, verkaufen Japan-Tarife mit unbegrenzten Daten neben Tarifen mit festem Kontingent, beide Formen stehen also zur Wahl. Lies die Fair-Use-Bedingungen vor der Wahl, denn unbegrenzte Reise-Tarife senken die Geschwindigkeit nach einem Tagesgrenzwert, statt die Verbindung zu kappen. Für eine ein- oder zweiwöchige Reise bleiben die meisten Reisenden innerhalb eines festen Kontingents, das für Reisen unter zwei Wochen meist das bessere Preis-Leistungs-Verhältnis ist."
  - q: "Ist eine Japan-eSIM günstiger als Pocket WiFi?"
    a: "Bei ein oder zwei Personen meist ja, sobald Tagesmiete und Rückfahrt mitgezählt werden, weil ein vorab gekaufter Datentarif keine Hardware trägt und nichts zurückzugeben ist. Pocket WiFi gewinnt weiterhin, wenn drei oder mehr Personen eine Verbindung teilen. Unsere Japan-Tarifrangliste sortiert jeden Tarif nach Preis pro Gigabyte und Preis pro Tag, was die Frage für deine Daten klärt."
  - q: "Ist die Aktivierung einer Japan-eSIM sofort?"
    a: "Das Profil wird direkt nach der Zahlung digital geliefert, meist innerhalb von Minuten, und die Leitung geht live, sobald du sie einschaltest — das meinen die Leute mit sofortiger Aktivierung. Nichts läuft, bevor du sie installierst, ein Kauf Wochen im Voraus ist also sicher. Ein Betreiberschalter arbeitet umgekehrt, denn dort startet die Uhr am Schalter und nur während der Öffnungszeiten."
---

## Ändert der Netzbetreiber hinter deiner Japan-eSIM deine Abdeckung

In Japan nicht, und das ist der nützlichste Fakt auf dieser Seite. Der Markt läuft über drei nationale Betreibernetze — NTT Docomo, SoftBank und KDDI — und alle {{< count-providers >}} Marken, die wir erfassen (Airalo, aloSIM, Holafly, Roami, Roamic, Saily, Ubigi und Yesim), listen alle drei als Heimatnetze. Die Markentabelle unten zeigt es Zeile für Zeile.

Die Folge: Keine Reise-eSIM-Marke kann dir in Japan bessere Abdeckung verkaufen. Eine günstigere Japan-eSIM ist hier kein Netzdowngrade, und das gilt nicht überall — in vielen Reisezielen fährt ein Billigtarif auf einem einzigen Netz und zahlt dafür mit ländlichem Signal. In Japan existiert dieser Kompromiss nicht, also zählen Preis pro Gigabyte, die Form des Datentarifs, Hotspot-Regeln, Gültigkeit und Support.

Das verschiebt die Kaufentscheidung. Statt die Japan-eSIM mit dem besten Netz zu suchen, frag dich, welche Marke den Tarif, den deine Reise braucht, am günstigsten verkauft — und die Antwort hängt von der Reisedauer ab, weshalb unsere [Japan-Tarifrangliste](/de/compare/japan/) alle 177 Tarife nach $/GB und $/Tag sortiert statt nach Netz.

## Wo jedes japanische 5G-Netz bei Geschwindigkeit und Reichweite am besten ist

Japans drei nationale 5G-Netze sind bei der Verfügbarkeit nahezu identisch und bei der Leistung klar verschieden. Unabhängige Tests trennen sie danach, was man misst.

### NTT Docomo besitzt die japanische Reichweite

Im Japan-Bericht von Opensignal vom April 2026 holte Docomo die Abdeckung mit 9,0 von 10 und gewann die 5G-Download-Geschwindigkeit mit 159,1 Mbit/s. Wenn deine Route die Städte Richtung Berge oder die Inseln Okinawas verlässt, ist Docomos Fußabdruck der Grund, darauf zu achten, was unter deinem Tarif liegt.

### SoftBank besitzt die japanische 5G-Spitzengeschwindigkeit

Opensignal maß SoftBank beim Download mit 65,1 Mbit/s am schnellsten, und Ookla kürte es für das erste Halbjahr 2026 zum schnellsten Mobilfunknetz Japans, mit einem Median-Download von 73,8 Mbit/s vor au mit 67,9 und einem Median-5G-Download von 153,6 Mbit/s. Diese Stärke zeigt sich in Städten und entlang der Korridore um die großen Bahnhöfe.

### KDDI au ist der japanische Balancepunkt

KDDI, lokal als au verkauft, sammelte im April-Zyklus 2026 die meisten Auszeichnungen aller Betreiber — zehn alleinige Siege plus einen geteilten. Die landesweite Reichweite liegt nahe an Docomo, lehnt sich aber nach Westen und hält Küstenrouten besonders fest.

Eine Warnung, falls du diese Zahlen anderswo vergleichst. Die Panels sind aus ungleichen Belegen zusammengesetzt, und sie direkt nebeneinanderzustellen ergibt eine Zahl ohne Bedeutung. Behandle jedes Panel als eigene Rangliste derselben drei japanischen Netze.

## Ist 5G mit einer Japan-eSIM verfügbar

Ja, und in Japan ist die 5G-Frage nahezu geklärt. Alle drei nationalen Netze betreiben kommerzielles 5G und jedes Netzbetreiber-Profil, das wir erfassen, listet es — eine Japan-Reise-eSIM ist also nicht still auf 4G begrenzt. Unabhängige Tests verorten die Technik dort, wo man sie in einem so dichten Markt erwartet: Opensignal maß Docomos 5G-Download mit 159,1 Mbit/s, und Ookla verzeichnete im selben Zyklus einen Median-5G-Download von 153,6 Mbit/s für SoftBank.

Für Käufer heißt das: 5G ist kein Aufpreis wert, weil es kein Netz ohne 5G gibt. Die nützlichen Prüfungen sind enger — listet der Tarif vor dir 5G, unterstützt dein Gerät die japanischen Bänder (der [Geräte-Kompatibilitätsratgeber](/de/guides/esim-compatibility-check/) klärt das in 30 Sekunden), und senkt die Fair-Use-Regel des Tarifs nach einem Tageskontingent die Geschwindigkeit statt das Netz selbst. Eine eSIM ist ein Profil, das dein Telefon herunterlädt, statt einer Karte zum Einlegen — ein Standard, den die [GSMA](https://www.gsma.com/esim/) pflegt — also reist der Tarif mit dem Gerät statt mit dem SIM-Schacht.

## Japan-Reise-eSIM vs Pocket WiFi vs lokale Prepaid-SIM

Drei Wege zu Daten in Japan, und die Wahl hängt mehr an Regeln und Logistik als am Preis. Die allgemeinen Abwägungen stehen in unserem [Ratgeber eSIM vs physische SIM](/de/guides/esim-vs-physical-sim/); was folgt, ist Japan-spezifisch.

| | Reise-eSIM | Pocket WiFi | Lokale Prepaid-SIM |
|---|---|---|---|
| Ausweis oder Pass | Nicht erforderlich | Nicht erforderlich | Passprüfung gesetzlich vorgeschrieben |
| Aktivierung | Jede Stunde, bei der Landung | Bei Abholung, Läden haben Öffnungszeiten | SoftBank-Touristen-SIM nur 09:00 bis 21:00 JST |
| Wofür geeignet | Alleinreisende und Paare | Gruppen ab drei Personen mit einer Verbindung | Lange Aufenthalte und alle, die eine lokale Nummer brauchen |
| Hauptnachteil | Nur Daten, keine lokale Nummer | Tagesmiete plus Rückgabelogistik und ein Akku zum Laden | Schlangestehen und Papierkram am ersten Tag |

Für eine allein reisende Person oder ein Paar kostet die eSIM fast immer weniger, sobald Tagesmiete und Rückfahrt des Pocket WiFi mitgezählt werden. Pocket WiFi gewinnt weiterhin bei einer Gruppe ab drei Personen mit einer Verbindung. Eine Prepaid-SIM eines japanischen Betreibers ist der einzige Weg zu einer anrufbaren lokalen Nummer, und sie ist die Option, bei der die Passregel und das Aktivierungsfenster am härtesten zuschlagen — siehe den Abschnitt mit den Länderhinweisen auf der [Japan-Tarifrangliste](/de/compare/japan/) dazu, wie das in Narita und Haneda abläuft.

## Japan-eSIM-Regeln und Roaming-Grundlagen für Touristen

Zwei Japan-spezifische Regeln entscheiden mehr Käufe als jeder Geschwindigkeitstest, dazu eine Abrechnungsfalle, die man vor dem Flug kennen sollte. Die Passpflicht für lokale Prepaid-Karten setzt das [Ministerium für innere Angelegenheiten und Kommunikation](https://www.soumu.go.jp/english/), das die japanische Telekommunikation reguliert.

### Warum eine japanische Prepaid-SIM einen Pass braucht

Japanisches Recht verlangt von SoftBank, Docomo und KDDI, eine lokale Prepaid-SIM auf deinen Pass zu registrieren. Reise-eSIMs stehen außerhalb dieses Regimes — online kaufen, Code scannen, verbinden, ohne Dokumenten-Upload bei irgendeinem Schritt.

### Sofortige Aktivierung gegen eine SoftBank-Counter-SIM

SoftBanks eigene Touristenkarte aktiviert nur zwischen 09:00 und 21:00 JST. Eine Reise-eSIM kennt kein solches Fenster, was bei einer späten Ankunft in Narita oder Haneda am wichtigsten ist — wenn die Schalter zu sind und du Daten vor dem Zug willst.

### Keine Roaming-Union deckt Japan für Touristen ab

Japan hat nichts wie die Freiroaming-Regelung der EU für einreisende Besucher, eine hier genutzte Heimat-SIM rechnet also zu internationalen Sätzen ab. Genau das ist das Argument für einen Prepaid-Datentarif in Japan: Eine Reise-eSIM wird vorab zu einem festen Preis gekauft, ohne Roaming-Aufschlag und ohne Rechnung, die du zu Hause öffnest.

Bevor du zahlst, laufen vier Prüfungen. Der Tarif listet alle drei Netze. Er listet 5G, wenn dir das wichtig ist. Hotspot-Sharing ist erlaubt, wenn du es brauchst. Und die Fair-Use-Bedingungen stehen auf der Seite statt in einem Support-Ticket. Aktuelle Rabatte findest du in den [eSIM-Rabattcodes](/de/esim-deals/), und der [Datenrechner](/de/tools/) dimensioniert ein Kontingent für deine Reisedaten.

Zwei Schlussnotizen. Das japanische Spektrum ist landesweit über Bänder lizenziert, die manche importierten Geräte nicht abstimmen, prüfe dein Gerät also, bevor du auf 5G zählst. Japans Betreiber haben zudem ihre älteren Netze abgeschaltet, ein Gerät braucht also VoLTE-Unterstützung statt 2G- oder 3G-Fallback, um sich überhaupt zu registrieren.
'''


def fm_keys(text: str) -> list[str]:
    fm = text.split("---", 2)[1]
    return [l.split(":")[0] for l in fm.split("\n") if l and not l.startswith((" ", "-", "#"))]


def h2h3(text: str) -> list[str]:
    body = text.split("---", 2)[2]
    return [l for l in body.split("\n") if l.startswith(("## ", "### "))]


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry", action="store_true")
    args = ap.parse_args()

    en = EN.read_bytes().decode("utf-8")
    fails: list[str] = []

    # 断言 1：front matter 字段集一致（顺序一致）；德语侧允许唯一多出 `noindex`
    #        —— 分层发布：只有 /de/ 首页可索引，其余德语页 noindex。
    ke, kd = fm_keys(en), fm_keys(DOC)
    extra = [k for k in kd if k not in ke]
    missing = [k for k in ke if k not in kd]
    if extra != ["noindex"]:
        fails.append(f"德语侧多出的字段应为 ['noindex']，实为 {extra}")
    if missing:
        fails.append(f"德语侧缺字段 {missing}")
    order_ok = [k for k in kd if k != "noindex"] == ke
    if not order_ok:
        fails.append(f"字段顺序不一致\n  en={ke}\n  de={[k for k in kd if k != 'noindex']}")

    # 断言 2：正文 h2/h3 条数与层级一致
    he, hd = h2h3(en), h2h3(DOC)
    if len(he) != len(hd):
        fails.append(f"h2/h3 条数 en={len(he)} de={len(hd)}")
    else:
        for a, b in zip(he, hd):
            if a[:3] != b[:3]:
                fails.append(f"层级错位: {a[:20]!r} vs {b[:20]!r}")

    # 断言 3：德语 h2/h3 禁 `,` `;` `:`
    import re as _re

    for h in hd:
        body = h.lstrip("#").strip()
        if _re.search(r"[,;:]", body):
            fails.append(f"德语标题含禁用标点: {body[:60]!r}")

    # 断言 4：站内链必须带 /de/ 前缀（外链不得带）
    for m in _re.finditer(r"\]\((/[^)]*)\)", DOC):
        if not m.group(1).startswith("/de/"):
            fails.append(f"站内链缺 /de/ 前缀: {m.group(1)}")

    # 断言 5：单位禁用 Mbps
    for w in ("Mbps", "Kbps", "Gbps"):
        if w in DOC:
            fails.append(f"德语正文含非法单位 {w}")

    # 断言 6：短代码保留
    if "{{< count-providers >}}" not in DOC:
        fails.append("缺 {{< count-providers >}} 短代码")

    if fails:
        print("\n".join("FAIL " + f for f in fails))
        return 1
    print(f"断言全过：{len(kd)} 字段 / {len(hd)} 个 h2-h3 / {len(DOC.encode('utf-8'))} bytes")

    if args.dry:
        print("（--dry：未写盘）")
        return 0

    DE.parent.mkdir(parents=True, exist_ok=True)
    if DE.exists() and DE.read_bytes().decode("utf-8") == DOC:
        print("已是目标内容，无需写盘")
        return 0
    DE.write_bytes(DOC.encode("utf-8"))
    b = DE.read_bytes()
    crlf = b.count(b"\r\n")
    print(f"写入 content/de/networks/{REL}: {len(b)} bytes / CRLF={crlf}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
