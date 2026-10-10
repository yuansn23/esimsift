# -*- coding: utf-8 -*-
"""批 E 分册 2/5：czechia · egypt · fiji · france · georgia ·
germany · greece · hong-kong · iceland · india 的德语正文。

数字口径全部现算（`.buildlog/compare_de_facts.json`）：
  · CZ 175 / 98 · Yesim 500 MB $0.51 · Roami $0.55/GB · Roamic $1.00/Tag · be 1,8
  · EG 165 / 94 · Yesim 399 MB $0.51 · Yesim $0.88/GB · Roamic $2.23/Tag · be 2,5
  · FJ 103 / 52 · Roamic 1 GB $3.00 · Yesim $1.17/GB · Yesim $2.08/Tag · be 1,8
  · FR 203 / 99 · Yesim 500 MB $0.51 · Ubigi $0.30/GB · Ubigi $0.87/Tag · be 2,9
  · GE 152 / 81 · Yesim 300 MB $0.51 · Jetpac $0.93/GB · Roamic $1.60/Tag · be 1,7
  · DE 202 / 99 · Yesim 500 MB $0.51 · aloSIM $0.50/GB · Roamic $1.00/Tag · be 2,0
  · GR 197 / 99 · Yesim 500 MB $0.51 · Roamic $0.36/GB · Roamic $1.00/Tag · be 2,8
  · HK 185 / 97 · Yesim 500 MB $0.57 · Roamic $0.52/GB · Roamic $1.41/Tag · be 2,7
  · IS 148 / 73 · Yesim 500 MB $0.51 · Roamic $0.36/GB · Roamic $1.09/Tag · be 3,0
  · IN 186 / 98 · Yesim 300 MB $0.51 · Ubigi $0.57/GB · Ubigi $1.60/Tag · be 2,8

用法：python -X utf8 scripts/_compare_de_2.py [--dry]
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _compare_de_lib import apply_country  # noqa: E402

DOCS: dict[str, list[str]] = {}

DOCS["czechia"] = [
    "Anbieter in Tschechien berechnen dasselbe Gigabyte sehr unterschiedlich. Für Tschechien ist das "
    "Günstigste auf der Liste Yesim für $0.51. Dieselben $0.51 ergäben zum Tarif von $0.55/GB etwa "
    "950 MB. Beim Tarif gewinnt Roami, mit $0.55/GB für einen Block von 100 GB über 30 Tage. Das "
    "sind 98 unbegrenzte Tarife unter 175 Optionen für Tschechien von {{< count-providers >}} Anbietern.",

    "Tagespreis-unbegrenzt ist am günstigsten bei Roamic, mit $1.00. In Tschechien setzt der "
    "gemessene Tarif von $0.55/GB den Umschlagpunkt für unbegrenzt auf fast 1,8 GB pro Tag. Eine "
    "Woche zwischen Prag und Brno ist der Punkt, an dem der Rat zum kleinen Kontingent kippt. In "
    "Tschechien gibt es keine Registrierungshürde, deshalb trennen Preis und Einrichtungsgeschwindigkeit "
    "eine eSIM von einer lokalen SIM.",

    "Die nationalen Netze sind O2, T-Mobile und Vodafone, alle mit 5G. Der Durchsatz in Tschechien "
    "liegt je nach Netz in einem Band von 15 bis 250 Mbit/s. Außerhalb von Prag ist O2 das Netz der "
    "Wahl. Vodafone steht am anderen Ende: in den Städten Tschechiens in Ordnung, dünnt aber als "
    "erstes außerhalb aus. Die Abdeckung in Tschechien folgt dir nicht nach Deutschland, plane also "
    "einen zweiten Tarif ein oder eine regionale eSIM.",
]

DOCS["egypt"] = [
    "Sortiere die Tabelle für Ägypten nach Preis pro Gigabyte, und die Reihenfolge ändert sich. Der "
    "Einstieg in Ägypten beginnt bei $0.51 mit Yesim 399 MB / 1 Tag. In Ägypten reichen dieselben "
    "$0.51 zum Tarif von $0.88/GB für etwa 590 MB. Der beste Gegenwert pro Gigabyte gehört Yesim, wo "
    "50 GB über 30 Tage $0.88 pro Gigabyte ergeben. Alles zusammengerechnet listen "
    "{{< count-providers >}} Anbieter 165 Tarife für Ägypten, davon 94 unbegrenzt.",

    "Der Preis für unbegrenzt in Ägypten erreicht seine Untergrenze bei $2.23 pro Tag mit Roamic. "
    "Bei $0.88/GB für gemessenes Volumen braucht unbegrenzt in Ägypten etwa 2,5 GB pro Tag, um Sinn "
    "zu ergeben. Wer aus Kairo Fotos und Videos hochlädt, verbraucht Gigabytes schneller als die "
    "meisten Reisenden erwarten. Passkontrollen gehören in Ägypten zum Ablauf für lokale SIMs — eine "
    "Schlange, in der eine eSIM nie steht.",

    "Die lokale Abdeckung kommt in Ägypten von Vodafone Egypt, Orange Egypt und Etisalat Misr, alle "
    "mit 5G. Die gemessene Leistung in Ägypten reicht von etwa 10 Mbit/s nach oben bis nahe 200. "
    "Alles, was Kairo verlässt, ist auf Vodafone Egypt besser aufgehoben, das die größte gemessene "
    "Reichweite hält. Orange Egypt ist die weichere Option, was erst außerhalb der großen Städte "
    "zählt. Saudi-Arabien liegt oft auf derselben Route — kalkuliere einen zweiten Tarif ein oder "
    "eine regionale eSIM für beide.",
]

DOCS["fiji"] = [
    "Billige Einstiegspreise in Fidschi verbergen eine weite Spanne, sobald man auf Daten normiert. "
    "Der niedrigste Preis in Fidschi ist Roamic 1 GB / 7 Tage für $3.00. Dieselben $3.00 ergäben zum "
    "Tarif von $1.17/GB in Fidschi etwa 2,6 GB. Das Rennen um den Preis pro Gigabyte gewinnt Yesim "
    "mit einem Tarif von 30 GB über 30 Tage für $1.17/GB. {{< count-providers >}} Anbieter listen "
    "hier 103 Tarife für Fidschi, 52 davon unbegrenzt.",

    "Yesim bepreist unbegrenzt in Fidschi ab $2.08 pro Tag. Bei gemessenem Volumen zu $1.17/GB zahlt "
    "sich unbegrenzt erst oberhalb von rund 1,8 GB pro Tag aus. Auf Roadtrips außerhalb von Suva "
    "beginnt die Netzwahl mehr zu zählen als der Preis. Lokale SIMs in Fidschi sind unkompliziert zu "
    "kaufen, das Argument für die eSIM ist also eines von Preis und sofortiger Aktivierung.",

    "Fidschi läuft über Vodafone Fiji und Digicel Fiji, beide mit 4G. Praktisch liegen die Tempi je "
    "nach Netz zwischen 8 und 80 Mbit/s. Vodafone Fiji deckt die größte Fläche ab und ist damit die "
    "Voreinstellung für alles außerhalb von Suva. Der Kompromiss ist Digicel Fiji, das in der Stadt "
    "trägt und dazwischen weniger. Reisen, die nach Australien weitergehen, brauchen einen eigenen "
    "Tarif, weil die Abdeckung an der Grenze endet.",
]

DOCS["france"] = [
    "Die Preisliste für Frankreich ist nicht gleichförmig, und ihre Form entscheidet, was du zahlst. "
    "Der Einstiegspunkt für Frankreich ist Yesim 500 MB / 1 Tag für $0.51. Dieselbe Summe ergäbe in "
    "Frankreich zum Tarif von $0.30/GB etwa 1,7 GB. Pro Gigabyte am billigsten ist Ubigi, mit 240 GB "
    "über 365 Tage für $0.30/GB. Wir erfassen hier {{< count-providers >}} Anbieter, die zusammen "
    "203 Tarife für Frankreich listen, 99 davon unbegrenzt.",

    "Ubigi hält den günstigsten unbegrenzten Tarif in Frankreich bei $0.87 pro Tag. Täglicher Bedarf "
    "über 2,9 GB macht unbegrenzt in Frankreich lohnend, gegen $0.30/GB bei gemessenem Volumen. "
    "Streaming und Hotspot-Sharing schieben eine Paris-Reise in die unbegrenzte Stufe. Nichts "
    "spricht dagegen, in Frankreich am Flughafen eine lokale SIM zu kaufen — Preis und "
    "Aktivierungszeitpunkt sind also die eigentlichen Unterschiede.",

    "Hinter jeder eSIM für Frankreich stehen Orange, SFR und Bouygues, alle mit 5G. Rechne in "
    "Frankreich mit 20 bis 300 Mbit/s, wobei die Spitze nur auf Orange zu erreichen ist. Orange hat "
    "die größte Reichweite, deshalb sind Tarife darauf die sichere Wahl, sobald deine Route Paris "
    "verlässt. SFR liegt bei der Reichweite hinten, was in Frankreich nur abseits der üblichen "
    "Routen ein Problem ist. Der Sprung ins Vereinigte Königreich ist üblich, und kein einzelner "
    "Tarif deckt beides ab — plane also einen zweiten Tarif ein oder einen regionalen.",
]

DOCS["georgia"] = [
    "Der Markt in Georgien belohnt ein wenig Arithmetik. Die Einstiegspreise beginnen bei $0.51, mit "
    "Yesim 300 MB / 1 Tag. Zum Tarif von $0.93/GB ausgegeben, kaufte dieselbe Summe eher 565 MB. "
    "Beim Tarif setzt Jetpac die Untergrenze mit $0.93/GB für 40 GB über 30 Tage. Der erfasste "
    "Katalog hält 152 Tarife für Georgien von {{< count-providers >}} Anbietern, 81 davon unbegrenzt.",

    "Tagespreis-unbegrenzt in Georgien beginnt bei $1.60 über Roamic. Verglichen mit $0.93/GB auf "
    "der Kontingentseite musst du etwa 1,7 GB pro Tag überschreiten, bevor unbegrenzt billiger "
    "wird. Wer zwischen Tiflis und Batumi unterwegs ist, bleibt beim Tagesverbrauch moderat — "
    "gemessenes Volumen bleibt damit die billigere Form. Lokale Prepaid-SIMs sind in Georgien leicht "
    "zu kaufen, das Argument für die eSIM ist also der Preis und die Verbindung direkt bei der Landung.",

    "Georgien wird von Magti, Silknet und Beeline versorgt, einer Mischung aus 4G und 5G. Der real "
    "erreichbare Durchsatz liegt je nach Netz zwischen 8 und 150 Mbit/s. Außerhalb von Tiflis ist "
    "Magti das Netz der Wahl. Beeline steht am anderen Ende: in den Städten Georgiens in Ordnung, "
    "dünnt aber als erstes außerhalb aus. Die Abdeckung in Georgien folgt dir nicht in die Türkei, "
    "plane also einen zweiten Tarif ein oder eine regionale eSIM.",
]

DOCS["germany"] = [
    "Der billigste Tarif in Deutschland ist selten die billigste Reise. Für den kleinsten Einsatz "
    "bekommst du Yesim 500 MB / 1 Tag für $0.51. Diese $0.51 kaufen einen Bruchteil dessen, was zum "
    "Tarif von $0.50/GB möglich wäre, nämlich eher 1,0 GB. Die Wertungskrone gehört aloSIM, mit "
    "$0.50/GB für 50 GB über 10 Tage. Das gesamte Angebot sind 202 Tarife für Deutschland von "
    "{{< count-providers >}} Anbietern, 99 davon unbegrenzt.",

    "Die unbegrenzte Stufe beginnt bei $1.00 pro Tag mit Roamic. Reisen in Deutschland, die unter "
    "2,0 GB pro Tag bleiben, sind mit einem Kontingent zu $0.50/GB billiger. Bleibt die Reise in "
    "Berlin und München, deckt ein bescheidenes Kontingent Karten, Nachrichten und die eine oder "
    "andere Buchung ab. Eine lokale SIM in Deutschland zu besorgen ist einfach — Preis und sofortige "
    "Aktivierung bleiben als Gründe für eine eSIM.",

    "Den Dienst in Deutschland erbringen Telekom, Vodafone und O2, alle mit 5G. Typische Tempi in "
    "Deutschland liegen zwischen 15 und 300 Mbit/s auf Telekom, weniger auf den übrigen Netzen. "
    "Alles, was Berlin verlässt, ist auf Telekom besser aufgehoben, das die größte gemessene "
    "Reichweite hält. O2 ist die weichere Option, was erst außerhalb der großen Städte zählt. "
    "Frankreich liegt oft auf derselben Route — kalkuliere einen zweiten Tarif ein oder eine "
    "regionale eSIM für beide.",
]

DOCS["greece"] = [
    "Die eSIM-Preise in Griechenland sind weniger gleichförmig, als der Lockpreis vermuten lässt. "
    "Nichts unterbietet Yesim 500 MB / 1 Tag für $0.51. Kleine Kontingente kosten hier rund das "
    "2,9-Fache des Tarifs der großen. Der beste Tarif ist Roamics Block von 50 GB über 30 Tage für "
    "$0.36/GB. Über {{< count-providers >}} Anbieter hinweg läuft das Angebot auf 197 Tarife für "
    "Griechenland, 99 davon unbegrenzt verkauft.",

    "Tagespreis-unbegrenzt ist am günstigsten bei Roamic, mit $1.00 pro Tag. Gegen $0.36/GB für "
    "gemessenes Volumen gewinnt unbegrenzt erst ab etwa 2,8 GB pro Tag. Wer aus Athen remote "
    "arbeitet, sollte die unbegrenzte Tagesstufe vor der Buchung durchrechnen. In Griechenland gibt "
    "es keine Registrierungshürde, deshalb trennen Preis und Einrichtungsgeschwindigkeit eine eSIM "
    "von einer lokalen SIM.",

    "Die nationalen Netze sind Cosmote, Vodafone und Wind, alle mit 5G. Der Durchsatz in "
    "Griechenland liegt je nach Netz in einem Band von 15 bis 300 Mbit/s. Cosmote deckt die größte "
    "Fläche ab und ist damit die Voreinstellung für alles außerhalb von Athen. Der Kompromiss ist "
    "Vodafone, das in der Stadt trägt und dazwischen weniger. Reisen, die in die Türkei "
    "weitergehen, brauchen einen eigenen Tarif, weil die Abdeckung an der Grenze endet.",
]

DOCS["hong-kong"] = [
    "Der Markt in Hongkong wirkt beim Einstiegspreis mittelmäßig und beim Gegenwert deutlich besser. "
    "Der Einstiegspreis in Hongkong erreicht mit Yesim seinen Tiefpunkt bei $0.57 für 500 MB / 1 Tag. "
    "Einstiegstarife in Hongkong liegen beim etwa 2,2-Fachen des besten Preises pro Gigabyte. Die "
    "Wertführerschaft liegt bei Roamic, dessen Tarif von 50 GB über 30 Tage bei $0.52/GB landet. Bei "
    "{{< count-providers >}} Anbietern liegen 185 Tarife für Hongkong vor, 97 mit dem Label unbegrenzt.",

    "Unbegrenzt beginnt bei $1.41 pro Tag mit Roamic. Da Kontingente $0.52/GB kosten, lohnt der "
    "Tagestarif erst ab etwa 2,7 GB pro Tag. Zwei Wochen mit Standort Central und regelmäßigen "
    "Videoanrufen sind der Punkt, an dem ein größeres Kontingent einen Tagestarif schlägt. Lokal in "
    "Hongkong zu kaufen ist einfach — Preis und sofortige Einrichtung bleiben als entscheidende "
    "Faktoren.",

    "Die lokale Abdeckung kommt in Hongkong von CSL, 3HK und SmarTone, alle mit 5G. Die gemessene "
    "Leistung in Hongkong reicht von etwa 20 Mbit/s nach oben bis nahe 400. CSL hat die größte "
    "Reichweite, deshalb sind Tarife darauf die sichere Wahl, sobald deine Route Central verlässt. "
    "3HK liegt bei der Reichweite hinten, was in Hongkong nur abseits der üblichen Routen ein "
    "Problem ist. Der Sprung nach Taiwan ist üblich, und kein einzelner Tarif deckt beides ab — "
    "plane also einen zweiten Tarif ein oder einen regionalen.",
]

DOCS["iceland"] = [
    "Daten in Island lassen sich billig oder teuer kaufen. Die Untergrenze in Island ist Yesim "
    "500 MB / 1 Tag für $0.51. Kleine Tarife in Island kosten pro Gigabyte das 2,9-Fache des besten "
    "Tarifs. Beim Preis pro Gigabyte führt Roamic mit einem Tarif von 50 GB über 30 Tage für "
    "$0.36/GB. Das sind 73 unbegrenzte Tarife unter 148 Optionen für Island von "
    "{{< count-providers >}} Anbietern.",

    "In Island beginnt unbegrenzt bei $1.09 pro Tag mit Roamic. Unter etwa 3,0 GB pro Tag bleiben "
    "Kontingente in Island zu $0.36/GB vor jedem Tagestarif. Eine Städtereise rund um Reykjavík "
    "überschreitet selten ein paar Gigabyte, ein kleines Kontingent reicht also meist. Lokale SIMs "
    "in Island sind unkompliziert zu kaufen, das Argument für die eSIM ist also eines von Preis und "
    "sofortiger Aktivierung.",

    "Island läuft über Siminn, Vodafone und Noa, einer Mischung aus 4G und 5G. Praktisch liegen die "
    "Tempi je nach Netz zwischen 8 und 200 Mbit/s. Außerhalb von Reykjavík ist Siminn das Netz der "
    "Wahl. Noa steht am anderen Ende: in den Städten Islands in Ordnung, dünnt aber als erstes "
    "außerhalb aus.",
]

DOCS["india"] = [
    "Wer eSIMs für Indien nach Einstiegspreis sortiert, bekommt die Reihenfolge falsch. Der "
    "billigste Tarif in Indien ist Yesim 300 MB / 1 Tag für $0.51. Diese Lücke ist die Geschichte "
    "Indiens in einer Zeile: das 3,1-Fache des Tarifs für das kleinste Kontingent. Den Preis pro "
    "Gigabyte setzt Ubigi mit $0.57 für 60 GB über 365 Tage. Alles zusammengerechnet listen "
    "{{< count-providers >}} Anbieter 186 Tarife für Indien, davon 98 unbegrenzt.",

    "Der günstigste unbegrenzte Tarif in Indien kommt von Ubigi für $1.60 pro Tag. Gegen $0.57/GB "
    "gemessen liegt die Gewinnschwelle bei etwa 2,8 GB pro Tag. Hotel-WLAN in Mumbai erledigt den "
    "Großteil der Arbeit, was gemessene Tarife billig hält. Ausweisregeln gelten in Indien für "
    "Prepaid-SIMs, aber nicht für Reise-eSIMs, die ohne Papierkram aktiviert werden.",

    "Hinter jeder eSIM für Indien stehen Jio und Airtel, beide mit 5G. Rechne in Indien mit 25 bis "
    "300 Mbit/s, wobei die Spitze nur auf Jio zu erreichen ist. Alles, was Mumbai verlässt, ist auf "
    "Jio besser aufgehoben, das die größte gemessene Reichweite hält. Airtel ist die weichere "
    "Option, was erst außerhalb der großen Städte zählt. Thailand liegt oft auf derselben Route — "
    "kalkuliere einen zweiten Tarif ein oder eine regionale eSIM für beide.",
]


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry", action="store_true")
    args = ap.parse_args()
    n_applied = n_skip = 0
    for slug, paras in DOCS.items():
        r = apply_country(slug, paras, dry=args.dry)
        print(f"  [{r:7}] {slug}")
        n_applied += r == "applied"
        n_skip += r == "skipped"
    print(f"\n{'（dry-run）' if args.dry else ''}应用 {n_applied} 处 / 已存在跳过 {n_skip} 处 / 共 {len(DOCS)} 篇")


if __name__ == "__main__":
    main()
