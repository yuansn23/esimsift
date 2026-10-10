# -*- coding: utf-8 -*-
"""批 E 分册 4/5：netherlands · new-zealand · peru · philippines · poland ·
portugal · qatar · saudi-arabia · singapore · south-africa 的德语正文。

数字口径全部现算（`.buildlog/compare_de_facts.json`）：
  · NL 209 / 99 · Yesim 500 MB $0.51 · Roamic $0.36/GB · Roamic $1.00/Tag · be 2,8
  · NZ 174 / 98 · Yesim 500 MB $0.51 · Roamic $0.76/GB · Roamic $1.70/Tag · be 2,2
  · PE 135 / 63 · Roamic 1 GB $3.00 · Roamic $1.30/GB · aloSIM $2.27/Tag · be 1,7
  · PH 195 / 96 · Yesim 500 MB $0.51 · Roamic $0.56/GB · Yesim $2.06/Tag · be 3,7
  · PL 178 / 99 · Yesim 500 MB $0.51 · Roamic $0.36/GB · Roamic $1.00/Tag · be 2,8
  · PT 197 / 97 · Yesim 500 MB $0.51 · Roamic $0.36/GB · Roamic $1.00/Tag · be 2,8
  · QA 160 / 89 · Yesim 500 MB $0.57 · Nomad $0.98/GB · Roamic $2.87/Tag · be 2,9
  · SA 169 / 96 · Yesim 199 MB $0.51 · Nomad $0.82/GB · Jetpac $3.15/Tag · be 3,8
  · SG 217 / 110 · Yesim 500 MB $0.51 · Roamic $0.40/GB · Roamic $1.43/Tag · be 3,6
  · ZA 155 / 69 · Yesim 199 MB $0.51 · Airalo $0.98/GB · Yesim $2.04/Tag · be 2,1

用法：python -X utf8 scripts/_compare_de_4.py [--dry]
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _compare_de_lib import apply_country  # noqa: E402

DOCS: dict[str, list[str]] = {}

DOCS["netherlands"] = [
    "Der Markt in den Niederlanden belohnt ein wenig Arithmetik. Yesim hält den Einstiegspreis mit "
    "500 MB / 1 Tag für $0.51. Diese Lücke ist die Geschichte der Niederlande in einer Zeile: das "
    "2,9-Fache des Tarifs für das kleinste Kontingent. Beim Tarif gewinnt Roamic, mit $0.36/GB für "
    "einen Block von 50 GB über 30 Tage. Der erfasste Katalog hält 209 Tarife für die Niederlande "
    "von {{< count-providers >}} Anbietern, 99 davon unbegrenzt.",

    "In den Niederlanden beginnt unbegrenzt bei $1.00 pro Tag mit Roamic. Unter etwa 2,8 GB pro Tag "
    "bleiben Kontingente in den Niederlanden zu $0.36/GB vor jedem Tagestarif. Eine Woche zwischen "
    "Amsterdam und Rotterdam ist der Punkt, an dem der Rat zum kleinen Kontingent kippt. Lokale "
    "SIMs in den Niederlanden sind unkompliziert zu kaufen, das Argument für die eSIM ist also "
    "eines von Preis und sofortiger Aktivierung.",

    "Die Niederlande laufen über KPN, Vodafone und Odido, alle mit 5G. Die gemessene Leistung in "
    "den Niederlanden reicht von etwa 20 Mbit/s nach oben bis nahe 300. Außerhalb von Amsterdam ist "
    "KPN das Netz der Wahl. Vodafone steht am anderen Ende: in den Städten der Niederlande in "
    "Ordnung, dünnt aber als erstes außerhalb aus. Die Abdeckung in den Niederlanden folgt dir "
    "nicht nach Belgien, plane also einen zweiten Tarif ein oder eine regionale eSIM.",
]

DOCS["new-zealand"] = [
    "Der billigste Tarif in Neuseeland ist selten die billigste Reise. Die günstigste Option in "
    "Neuseeland ist Yesim 500 MB / 1 Tag für $0.51. Dieselbe Summe erreicht innerhalb des "
    "Kontingents von 50 GB etwa 687 MB bei $0.76/GB. Der beste Gegenwert pro Gigabyte gehört "
    "Roamic, wo 50 GB über 30 Tage $0.76 pro Gigabyte ergeben. Das gesamte Angebot sind 174 Tarife "
    "für Neuseeland von {{< count-providers >}} Anbietern, 98 davon unbegrenzt.",

    "Tagespreis-unbegrenzt ist am günstigsten bei Roamic, mit $1.70 pro Tag. Gegen $0.76/GB "
    "gemessen liegt die Gewinnschwelle bei etwa 2,2 GB pro Tag. Wer aus Auckland Fotos und Videos "
    "hochlädt, verbraucht Gigabytes schneller als die meisten Reisenden erwarten. Nichts spricht "
    "dagegen, in Neuseeland am Flughafen eine lokale SIM zu kaufen — Preis und Aktivierungszeitpunkt "
    "sind also die eigentlichen Unterschiede.",

    "Hinter jeder eSIM für Neuseeland stehen Spark, One NZ und 2degrees, alle mit 5G. Rechne in "
    "Neuseeland mit 15 bis 250 Mbit/s, wobei die Spitze nur auf Spark zu erreichen ist. Alles, was "
    "Auckland verlässt, ist auf Spark besser aufgehoben, das die größte gemessene Reichweite hält. "
    "2degrees ist die weichere Option, was erst außerhalb der großen Städte zählt. Australien liegt "
    "oft auf derselben Route — kalkuliere einen zweiten Tarif ein oder eine regionale eSIM für beide.",
]

DOCS["peru"] = [
    "Die eSIM-Preise in Peru sind weniger gleichförmig, als der Lockpreis vermuten lässt. Für Peru "
    "ist das Günstigste auf der Liste Roamic 1 GB / 7 Tage für $3.00. Dieselben $3.00 ergäben zum "
    "Tarif von $1.30/GB etwa 2,3 GB. Das Rennen um den Preis pro Gigabyte gewinnt Roamic mit einem "
    "Tarif von 50 GB über 30 Tage für $1.30/GB. Über {{< count-providers >}} Anbieter hinweg läuft "
    "das Angebot auf 135 Tarife für Peru, 63 davon unbegrenzt verkauft.",

    "Unbegrenzt beginnt bei $2.27 pro Tag mit aloSIM. Der Umschlagpunkt in Peru liegt bei rund "
    "1,7 GB pro Tag, wo unbegrenzt die Kontingente zu $1.30/GB einholt. Auf Roadtrips außerhalb von "
    "Lima beginnt die Netzwahl mehr zu zählen als der Preis. Lokale Prepaid-SIMs sind in Peru leicht "
    "zu kaufen, das Argument für die eSIM ist also der Preis und die Verbindung direkt bei der "
    "Landung.",

    "Peru wird von Claro, Movistar und Entel versorgt, alle mit 5G. Rechne in Peru mit 10 bis "
    "150 Mbit/s, wobei die Spitze nur auf Claro zu erreichen ist. Claro deckt die größte Fläche ab "
    "und ist damit die Voreinstellung für alles außerhalb von Lima. Movistar ist die weichere "
    "Option, was erst außerhalb der großen Städte zählt. Reisen, die nach Kolumbien weitergehen, "
    "brauchen einen eigenen Tarif, weil die Abdeckung an der Grenze endet.",
]

DOCS["philippines"] = [
    "Der Markt auf den Philippinen wirkt beim Einstiegspreis mittelmäßig und beim Gegenwert deutlich "
    "besser. Der Einstieg beginnt auf den Philippinen bei $0.51 mit Yesim 500 MB / 1 Tag. Auf den "
    "Philippinen reichen dieselben $0.51 zum Tarif von $0.56/GB für etwa 933 MB. Pro Gigabyte am "
    "billigsten ist Roamic, mit 50 GB über 30 Tage für $0.56/GB. Bei {{< count-providers >}} "
    "Anbietern liegen 195 Tarife für die Philippinen vor, 96 mit dem Label unbegrenzt.",

    "Auf den Philippinen beginnt unbegrenzt bei $2.06 pro Tag mit Yesim. Gegen den besten "
    "gemessenen Tarif von $0.56/GB braucht der Tagestarif etwa 3,7 GB pro Tag, um sich zu lohnen. "
    "Streaming und Hotspot-Sharing schieben eine Manila-Reise in die unbegrenzte Stufe. Lokale "
    "Prepaid-SIMs auf den Philippinen bringen Registrierungspflichten mit, die Reise-eSIMs nicht "
    "haben.",

    "Den Dienst auf den Philippinen erbringen Globe und Smart, beide mit 5G. Typische Tempi auf den "
    "Philippinen liegen zwischen 15 und 200 Mbit/s auf Globe, weniger auf dem übrigen Netz. Globe "
    "hat die größte Reichweite, deshalb sind Tarife darauf die sichere Wahl, sobald deine Route "
    "Manila verlässt. Smart liegt bei der Reichweite hinten, was auf den Philippinen nur abseits "
    "der üblichen Routen ein Problem ist. Der Sprung nach Indonesien ist üblich, und kein einzelner "
    "Tarif deckt beides ab — plane also einen zweiten Tarif ein oder einen regionalen.",
]

DOCS["poland"] = [
    "Daten in Polen lassen sich billig oder teuer kaufen. Der niedrigste Preis in Polen ist Yesim "
    "500 MB / 1 Tag für $0.51. Dieselben $0.51 ergäben zum Tarif von $0.36/GB in Polen etwa 1,4 GB. "
    "Beim Tarif setzt Roamic die Untergrenze mit $0.36/GB für 50 GB über 30 Tage. Das sind 99 "
    "unbegrenzte Tarife unter 178 Optionen für Polen von {{< count-providers >}} Anbietern.",

    "Der günstigste unbegrenzte Tarif in Polen kommt von Roamic für $1.00 pro Tag. In Polen setzt "
    "der gemessene Tarif von $0.36/GB den Umschlagpunkt für unbegrenzt auf fast 2,8 GB pro Tag. Wer "
    "zwischen Warschau und Krakau unterwegs ist, bleibt beim Tagesverbrauch moderat — gemessenes "
    "Volumen bleibt damit die billigere Form. In Polen gibt es keine Registrierungshürde, deshalb "
    "trennen Preis und Einrichtungsgeschwindigkeit eine eSIM von einer lokalen SIM.",

    "Die nationalen Netze sind Orange, Play, Plus und T-Mobile, alle mit 5G. Der Durchsatz in Polen "
    "liegt je nach Netz in einem Band von 20 bis 300 Mbit/s. Außerhalb von Warschau ist Orange das "
    "Netz der Wahl. Play steht am anderen Ende: in den Städten Polens in Ordnung, dünnt aber als "
    "erstes außerhalb aus. Die Abdeckung in Polen folgt dir nicht nach Deutschland, plane also "
    "einen zweiten Tarif ein oder eine regionale eSIM.",
]

DOCS["portugal"] = [
    "Wer eSIMs für Portugal nach Einstiegspreis sortiert, bekommt die Reihenfolge falsch. Der "
    "Einstiegspunkt für Portugal ist Yesim 500 MB / 1 Tag für $0.51. Dieselbe Summe ergäbe in "
    "Portugal zum Tarif von $0.36/GB etwa 1,4 GB. Die Wertungskrone gehört Roamic, mit $0.36/GB für "
    "50 GB über 30 Tage. Alles zusammengerechnet listen {{< count-providers >}} Anbieter 197 Tarife "
    "für Portugal, davon 97 unbegrenzt.",

    "Tagespreis-unbegrenzt beginnt in Portugal bei $1.00, dank Roamic. Bei $0.36/GB für gemessenes "
    "Volumen braucht unbegrenzt in Portugal etwa 2,8 GB pro Tag, um Sinn zu ergeben. Bleibt die "
    "Reise in Lissabon und Porto, deckt ein bescheidenes Kontingent Karten, Nachrichten und die "
    "eine oder andere Buchung ab. Lokal in Portugal zu kaufen ist einfach — Preis und sofortige "
    "Einrichtung bleiben als entscheidende Faktoren.",

    "Die lokale Abdeckung kommt in Portugal von MEO, NOS und Vodafone, alle mit 5G. Die gemessene "
    "Leistung in Portugal reicht von etwa 20 Mbit/s nach oben bis nahe 300. Alles, was Lissabon "
    "verlässt, ist auf MEO besser aufgehoben, das die größte gemessene Reichweite hält. NOS ist die "
    "weichere Option, was erst außerhalb der großen Städte zählt. Spanien liegt oft auf derselben "
    "Route — kalkuliere einen zweiten Tarif ein oder eine regionale eSIM für beide.",
]

DOCS["qatar"] = [
    "Die Preise der in Katar erfassten Anbieter trennen sich entlang einer Linie — und es ist nicht "
    "die Marke. Die Einstiegspreise beginnen bei $0.57, mit Yesim 500 MB / 1 Tag. Zum Tarif von "
    "$0.98/GB ausgegeben, kaufte dieselbe Summe eher 596 MB. Der beste Tarif ist Nomads Block von "
    "50 GB über 30 Tage für $0.98/GB. {{< count-providers >}} Anbieter listen hier 160 Tarife für "
    "Katar, 89 davon unbegrenzt.",

    "Für Katar liegt die Tagesuntergrenze für unbegrenzt bei $2.87 mit Roamic. Bei gemessenem "
    "Volumen zu $0.98/GB zahlt sich unbegrenzt erst oberhalb von rund 2,9 GB pro Tag aus. Wer aus "
    "Doha remote arbeitet, sollte die unbegrenzte Tagesstufe vor der Buchung durchrechnen. Lokale "
    "SIMs in Katar sind unkompliziert zu kaufen, das Argument für die eSIM ist also eines von Preis "
    "und sofortiger Aktivierung.",

    "Katar läuft über Ooredoo und Vodafone Qatar, beide mit 5G. Praktisch liegen die Tempi je nach "
    "Netz zwischen 20 und 350 Mbit/s. Ooredoo deckt die größte Fläche ab und ist damit die "
    "Voreinstellung für alles außerhalb von Doha. Der Kompromiss ist Vodafone Qatar, das in der "
    "Stadt trägt und dazwischen weniger. Reisen, die in die Vereinigten Arabischen Emirate "
    "weitergehen, brauchen einen eigenen Tarif, weil die Abdeckung an der Grenze endet.",
]

DOCS["saudi-arabia"] = [
    "Eine kurze Sortierung des Angebots für Saudi-Arabien trennt die guten Käufe von der Füllware. "
    "Für den kleinsten Einsatz bekommst du Yesim 199 MB / 1 Tag für $0.51. Diese $0.51 kaufen einen "
    "Bruchteil dessen, was zum Tarif von $0.82/GB möglich wäre, nämlich eher 637 MB. Die "
    "Wertführerschaft liegt bei Nomad, dessen Tarif von 50 GB über 30 Tage bei $0.82/GB landet. Wir "
    "erfassen hier {{< count-providers >}} Anbieter, die zusammen 169 Tarife für Saudi-Arabien "
    "listen, 96 davon unbegrenzt.",

    "Unbegrenzt ist billiger, als es aussieht: Jetpac unterbietet das Feld mit $3.15 pro Tag. "
    "Täglicher Bedarf über 3,8 GB macht unbegrenzt in Saudi-Arabien lohnend, gegen $0.82/GB bei "
    "gemessenem Volumen. Zwei Wochen mit Standort Riad und regelmäßigen Videoanrufen sind der "
    "Punkt, an dem ein größeres Kontingent einen Tagestarif schlägt. Ausweisregeln gelten in "
    "Saudi-Arabien für Prepaid-SIMs, aber nicht für Reise-eSIMs, die ohne Papierkram aktiviert "
    "werden.",

    "Hinter jeder eSIM für Saudi-Arabien stehen STC, Mobily und Zain, alle mit 5G. Rechne in "
    "Saudi-Arabien mit 20 bis 350 Mbit/s, wobei die Spitze nur auf STC zu erreichen ist. STC hat "
    "die größte Reichweite, deshalb sind Tarife darauf die sichere Wahl, sobald deine Route Riad "
    "verlässt. Mobily liegt bei der Reichweite hinten, was in Saudi-Arabien nur abseits der "
    "üblichen Routen ein Problem ist. Der Sprung in die Vereinigten Arabischen Emirate ist üblich, "
    "und kein einzelner Tarif deckt beides ab — plane also einen zweiten Tarif ein oder einen "
    "regionalen.",
]

DOCS["singapore"] = [
    "In Singapur konkurrieren zwei Preismodelle, und sie passen zu unterschiedlichen Reisen. Die "
    "günstigste Option in Singapur ist Yesim 500 MB / 1 Tag für $0.51. Kleine Kontingente kosten "
    "hier rund das 2,6-Fache des Tarifs der großen. Beim Preis pro Gigabyte führt Roamic mit einem "
    "Tarif von 50 GB über 30 Tage für $0.40/GB. Der erfasste Katalog hält 217 Tarife für Singapur "
    "von {{< count-providers >}} Anbietern, 110 davon unbegrenzt.",

    "Pro Tag gerechnet erreicht unbegrenzt mit $1.43 bei Roamic seinen Tiefpunkt. Verglichen mit "
    "$0.40/GB auf der Kontingentseite musst du etwa 3,6 GB pro Tag überschreiten, bevor unbegrenzt "
    "billiger wird. Eine Städtereise rund um die Orchard Road überschreitet selten ein paar "
    "Gigabyte, ein kleines Kontingent reicht also meist. Lokale Prepaid-SIMs sind in Singapur leicht "
    "zu kaufen, das Argument für die eSIM ist also der Preis und die Verbindung direkt bei der "
    "Landung.",

    "Singapur wird von Singtel, StarHub und M1 versorgt, alle mit 5G. Der real erreichbare Durchsatz "
    "liegt je nach Netz zwischen 20 und 400 Mbit/s. Außerhalb der Orchard Road ist Singtel das Netz "
    "der Wahl. M1 steht am anderen Ende: in den Städten Singapurs in Ordnung, dünnt aber als erstes "
    "außerhalb aus. Die Abdeckung in Singapur folgt dir nicht nach Malaysia, plane also einen "
    "zweiten Tarif ein oder eine regionale eSIM.",
]

DOCS["south-africa"] = [
    "In Südafrika sind der billigste Aufkleber und der beste Gegenwert verschiedene Tarife. Der "
    "Einstiegspreis in Südafrika erreicht mit Yesim seinen Tiefpunkt bei $0.51 für 199 MB / 1 Tag. "
    "Einstiegstarife in Südafrika liegen beim etwa 2,7-Fachen des besten Preises pro Gigabyte. Den "
    "Preis pro Gigabyte setzt Airalo mit $0.98 für 50 GB über 30 Tage. Das gesamte Angebot sind 155 "
    "Tarife für Südafrika von {{< count-providers >}} Anbietern, 69 davon unbegrenzt.",

    "Der günstigste unbegrenzte Tarif hier ist Yesims, mit $2.04 pro Tag. Reisen in Südafrika, die "
    "unter 2,1 GB pro Tag bleiben, sind mit einem Kontingent zu $0.98/GB billiger. Hotel-WLAN in "
    "Johannesburg erledigt den Großteil der Arbeit, was gemessene Tarife billig hält. Eine lokale "
    "SIM in Südafrika zu besorgen ist einfach — Preis und sofortige Aktivierung bleiben als Gründe "
    "für eine eSIM.",

    "Den Dienst in Südafrika erbringen Vodacom, MTN und Telkom, eine Mischung aus 4G und 5G. "
    "Typische Tempi in Südafrika liegen zwischen 10 und 250 Mbit/s auf Vodacom, weniger auf den "
    "übrigen Netzen. Alles, was Johannesburg verlässt, ist auf Vodacom besser aufgehoben, das die "
    "größte gemessene Reichweite hält. Telkom ist die weichere Option, was erst außerhalb der "
    "großen Städte zählt.",
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
