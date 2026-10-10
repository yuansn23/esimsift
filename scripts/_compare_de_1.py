# -*- coding: utf-8 -*-
"""批 E 分册 1/5：argentina · australia · austria · belgium · brazil ·
canada · china · colombia · costa-rica · croatia 的德语正文。

数字口径全部现算（`.buildlog/compare_de_facts.json`），与英语正文逐项核对：
  · AR 154 Tarife / 83 unbegrenzt · Einstieg Yesim 199 MB $0.51 · Rate Ubigi $1.30/GB
  · AU 180 / 98 · Yesim 399 MB $0.51 · Nomad $0.64/GB · Roamic $1.47/Tag
  · AT 182 / 92 · Yesim 500 MB $0.51 · Roamic $0.36/GB · Roamic $1.00/Tag
  · BE 212 / 98 · Yesim 500 MB $0.51 · Roamic $0.40/GB · Roamic $1.10/Tag
  · BR 180 / 97 · Yesim 199 MB $0.51 · Nomad $0.90/GB · Ubigi $2.30/Tag
  · CA 221 / 99 · Yesim 199 MB $0.51 · aloSIM $0.64/GB · Ubigi $2.30/Tag
  · CN 203 / 98 · Yesim 100 MB $0.51 · Roamic $0.48/GB · Roamic $1.70/Tag
  · CO 161 / 85 · Nomad 1 GB $4.00 · Airalo $0.98/GB · aloSIM $3.05/Tag
  · CR 170 / 88 · Roamic 1 GB $3.00 · Roamic $1.06/GB · Airalo $2.97/Tag
  · HR 195 / 98 · Yesim 500 MB $0.51 · Roamic $0.36/GB · Roamic $1.00/Tag

用法：python -X utf8 scripts/_compare_de_1.py [--dry]
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _compare_de_lib import apply_country  # noqa: E402

DOCS: dict[str, list[str]] = {}

DOCS["argentina"] = [
    "Die eSIM-Preise in Argentinien sind weniger gleichförmig, als der Lockpreis vermuten lässt. "
    "Am günstigsten ist Yesim 199 MB / 1 Tag für $0.51. Zum Tarif von $1.30/GB gerechnet reicht "
    "dieselbe Summe in Argentinien für rund 402 MB. Beim Preis pro Gigabyte liegt Ubigi vorn, "
    "mit $1.30/GB für einen Block von 60 GB über 30 Tage. Über {{< count-providers >}} Anbieter "
    "hinweg stehen 154 Tarife für Argentinien auf der Liste, 83 davon unbegrenzt.",

    "Ab $2.98 pro Tag gibt es unbegrenzte Daten bei Holafly. Weil gemessenes Volumen $1.30/GB kostet, "
    "rechnet sich unbegrenzt erst ab etwa 2,3 GB pro Tag. Eine Woche zwischen Buenos Aires und "
    "Córdoba ist der Punkt, an dem der Rat zum kleinen Kontingent kippt. Wer in Argentinien vor Ort "
    "eine SIM kauft, braucht Ausweispapiere — eine Reise-eSIM überspringt das komplett.",

    "Argentinien läuft über Personal, Claro und Movistar, alle mit 5G. Praktisch liegen die Tempi "
    "je nach Netz zwischen 15 und 200 Mbit/s. Personal deckt die größte Fläche ab und ist damit die "
    "Voreinstellung für alles außerhalb von Buenos Aires. Der Kompromiss ist Claro, das in der Stadt "
    "trägt und dazwischen weniger. Reisen, die nach Brasilien weitergehen, brauchen einen eigenen "
    "Tarif, weil die Abdeckung an der Grenze endet.",
]

DOCS["australia"] = [
    "Der Markt in Australien wirkt beim Einstiegspreis mittelmäßig und beim Gegenwert deutlich "
    "besser. Am billigsten hinein kommst du mit Yesim 399 MB / 1 Tag für $0.51. Zum Tarif von "
    "$0.64/GB gerechnet ergibt dieselbe Summe in Australien rund 816 MB. Beim Preis pro Gigabyte "
    "liegt Nomad vorn: 50 GB über 30 Tage ergeben $0.64 pro Gigabyte. Bei {{< count-providers >}} "
    "Anbietern liegen 180 Tarife für Australien vor, 98 davon tragen das Label unbegrenzt.",

    "Tagespreis-unbegrenzt ist am günstigsten bei Roamic, mit $1.47 pro Tag. Täglicher Bedarf über "
    "2,3 GB macht unbegrenzt in Australien lohnend, gegen $0.64/GB bei gemessenem Volumen. Wer in "
    "Sydney Fotos und Videos hochlädt, verbraucht Gigabytes schneller als die meisten Reisenden "
    "erwarten. Es spricht nichts dagegen, in Australien am Flughafen eine lokale SIM zu kaufen — "
    "Preis und Aktivierungszeitpunkt sind also die eigentlichen Unterschiede.",

    "Hinter jeder eSIM für Australien stehen Telstra, Optus und Vodafone, alle mit 5G. Rechne in "
    "Australien mit 15 bis 300 Mbit/s, wobei die Spitze nur auf Telstra zu erreichen ist. Telstra "
    "hat die größte Reichweite, deshalb sind Tarife darauf die sichere Wahl, sobald deine Route "
    "Sydney verlässt. Vodafone liegt bei der Reichweite hinten, was in Australien nur abseits der "
    "üblichen Routen ein Problem ist. Der Sprung nach Neuseeland ist üblich, und kein einzelner "
    "Tarif deckt beides ab — plane also einen zweiten Tarif ein oder einen regionalen.",
]

DOCS["austria"] = [
    "Daten in Österreich lassen sich billig oder teuer kaufen. Die günstigste Option in Österreich "
    "ist Yesim 500 MB / 1 Tag für $0.51. Dieselbe Summe ergäbe in Österreich zum Tarif von $0.36/GB "
    "etwa 1,4 GB. Das Rennen um den Preis pro Gigabyte gewinnt Roamic mit einem Tarif von 50 GB "
    "über 30 Tage für $0.36/GB. Das sind 92 unbegrenzte Tarife unter 182 Optionen für Österreich "
    "von {{< count-providers >}} Anbietern.",

    "Unbegrenzt beginnt bei $1.00 pro Tag bei Roamic. Gegen $0.36/GB auf der Kontingentseite musst "
    "du etwa 2,8 GB pro Tag überschreiten, bevor unbegrenzt billiger wird. Auf Roadtrips außerhalb "
    "Wiens zählt die Netzwahl mehr als der Preis. Lokale Prepaid-SIMs sind in Österreich leicht zu "
    "kaufen, das Argument für die eSIM ist also der Preis und die Verbindung direkt bei der Landung.",

    "Österreich wird von A1, Magenta und Drei versorgt, alle mit 5G. Die real erreichbare Datenrate "
    "liegt je nach Netz zwischen 15 und 300 Mbit/s. Außerhalb Wiens ist A1 das Netz der Wahl. Drei "
    "steht am anderen Ende: in den Städten Österreichs in Ordnung, dünnt aber als erstes außerhalb "
    "aus. Die Abdeckung in Österreich folgt dir nicht nach Deutschland, plane also einen zweiten "
    "Tarif ein oder eine regionale eSIM.",
]

DOCS["belgium"] = [
    "Wer eSIMs für Belgien nach Einstiegspreis sortiert, bekommt die Reihenfolge falsch. Beim "
    "Einstiegspreis führt Yesim in Belgien mit 500 MB / 1 Tag für $0.51. Zum Tarif von $0.40/GB "
    "ausgegeben, kaufte dieselbe Summe eher 1,3 GB. Pro Gigabyte am billigsten ist Roamic, mit 50 GB "
    "über 30 Tage für $0.40/GB. Alles zusammengerechnet listen {{< count-providers >}} Anbieter "
    "212 Tarife für Belgien, davon 98 unbegrenzt.",

    "In Belgien beginnt unbegrenzt bei $1.10 pro Tag mit Roamic. Reisen in Belgien, die unter "
    "2,8 GB pro Tag bleiben, sind mit einem Kontingent zu $0.40/GB billiger. Streaming und "
    "Hotspot-Sharing schieben eine Brüssel-Reise in die unbegrenzte Stufe. Eine lokale SIM in "
    "Belgien zu besorgen ist einfach — Preis und sofortige Aktivierung bleiben als Gründe für eine eSIM.",

    "Den Dienst in Belgien erbringen Proximus, Orange und Base, alle mit 5G. Typische Tempi in "
    "Belgien liegen zwischen 15 und 300 Mbit/s auf Proximus, weniger auf den übrigen Netzen. Alles, "
    "was Brüssel verlässt, ist auf Proximus besser aufgehoben, das die größte gemessene Reichweite "
    "hält. Base ist die weichere Option, was erst außerhalb der großen Städte zählt. Die Niederlande "
    "liegen oft auf derselben Route — kalkuliere einen zweiten Tarif ein oder eine regionale eSIM "
    "für beide.",
]

DOCS["brazil"] = [
    "Die Preise der in Brasilien erfassten Anbieter trennen sich entlang einer Linie — und es ist "
    "nicht die Marke. Unter Yesim 199 MB / 1 Tag für $0.51 geht in Brasilien nichts. Diese $0.51 "
    "kaufen einen Bruchteil dessen, was zum Tarif von $0.90/GB möglich wäre, nämlich eher 580 MB. "
    "Beim Tarif setzt Nomad die Untergrenze mit $0.90/GB für 50 GB über 30 Tage. "
    "{{< count-providers >}} Anbieter listen hier 180 Tarife für Brasilien, 97 davon unbegrenzt.",

    "Der günstigste unbegrenzte Tarif in Brasilien kommt von Ubigi für $2.30 pro Tag. Gegen "
    "$0.90/GB für gemessenes Volumen gewinnt unbegrenzt erst ab etwa 2,6 GB pro Tag. Wer zwischen "
    "São Paulo und Rio de Janeiro unterwegs ist, bleibt beim Tagesverbrauch moderat — gemessenes "
    "Volumen bleibt damit die billigere Form. In Brasilien gibt es keine Registrierungshürde, "
    "deshalb trennen Preis und Einrichtungsgeschwindigkeit eine eSIM von einer lokalen SIM.",

    "Die nationalen Netze sind Vivo, Claro und TIM, alle mit 5G. Der Durchsatz in Brasilien liegt "
    "je nach Netz in einem Band von 15 bis 250 Mbit/s. Vivo deckt die größte Fläche ab und ist damit "
    "die Voreinstellung für alles außerhalb von São Paulo. Der Kompromiss ist TIM, das in der Stadt "
    "trägt und dazwischen weniger. Reisen, die nach Argentinien weitergehen, brauchen einen eigenen "
    "Tarif, weil die Abdeckung an der Grenze endet.",
]

DOCS["canada"] = [
    "Eine kurze Sortierung des Angebots für Kanada trennt die guten Käufe von der Füllware. Yesim "
    "199 MB / 1 Tag ist mit $0.51 der billigste Kauf in Kanada. Kleine Kontingente kosten hier rund "
    "das 4,1-Fache des Tarifs der großen. Die Wertungskrone gehört aloSIM, mit $0.64/GB für 50 GB "
    "über 10 Tage. Wir erfassen hier {{< count-providers >}} Anbieter, die zusammen 221 Tarife für "
    "Kanada listen, 99 davon unbegrenzt.",

    "Tagespreis-unbegrenzt beginnt in Kanada bei $2.30, dank Ubigi. Da Kontingente $0.64/GB kosten, "
    "lohnt der Tagestarif erst ab etwa 3,6 GB pro Tag. Bleibt die Reise in Toronto und Vancouver, "
    "deckt ein bescheidenes Kontingent Karten, Nachrichten und die eine oder andere Buchung ab. "
    "Lokal in Kanada zu kaufen ist einfach — Preis und sofortige Einrichtung bleiben als "
    "entscheidende Faktoren.",

    "Die lokale Abdeckung kommt in Kanada von Bell, Rogers und Telus, alle mit 5G. Die gemessene "
    "Leistung reicht von etwa 20 Mbit/s nach oben bis nahe 300. Bell hat die größte Reichweite, "
    "deshalb sind Tarife darauf die sichere Wahl, sobald deine Route Toronto verlässt. Rogers liegt "
    "bei der Reichweite hinten, was in Kanada nur abseits der üblichen Routen ein Problem ist. Der "
    "Sprung in die USA ist üblich, und kein einzelner Tarif deckt beides ab — plane also einen "
    "zweiten Tarif ein oder einen regionalen.",
]

DOCS["china"] = [
    "In China konkurrieren zwei Preismodelle, und sie passen zu unterschiedlichen Reisen. In China "
    "ist Yesim 100 MB / 1 Tag mit $0.51 so billig wie nur möglich. Einstiegstarife liegen hier beim "
    "etwa 10,9-Fachen des besten Preises pro Gigabyte. Der beste Tarif ist Roamics Block von 50 GB "
    "über 30 Tage für $0.48/GB. Der erfasste Katalog hält 203 Tarife für China von "
    "{{< count-providers >}} Anbietern, 98 davon unbegrenzt.",

    "Für China liegt die Tagesuntergrenze für unbegrenzt bei $1.70 mit Roamic. Unter etwa 3,5 GB "
    "pro Tag bleiben Kontingente in China zu $0.48/GB vor jedem Tagestarif. Wer aus Peking remote "
    "arbeitet, sollte die unbegrenzte Tagesstufe vor der Buchung durchrechnen. Wer in China vor Ort "
    "eine SIM kauft, braucht Ausweispapiere — eine Reise-eSIM überspringt das komplett.",

    "China läuft über China Mobile, China Unicom und China Telecom, alle mit 5G. Praktisch liegen "
    "die Tempi je nach Netz zwischen 20 und 300 Mbit/s. Außerhalb von Peking ist China Mobile das "
    "Netz der Wahl. China Unicom steht am anderen Ende: in den Städten Chinas in Ordnung, dünnt "
    "aber als erstes außerhalb aus. Die Abdeckung in China folgt dir nicht nach Hongkong, plane "
    "also einen zweiten Tarif ein oder eine regionale eSIM.",
]

DOCS["colombia"] = [
    "In Kolumbien sind der billigste Aufkleber und der beste Gegenwert verschiedene Tarife. Der "
    "niedrigste Aufkleberpreis gehört Nomad, dessen 1 GB / 7 Tage $4.00 kostet. Kleine Tarife in "
    "Kolumbien kosten pro Gigabyte das 4,1-Fache des besten Tarifs. Die Wertführerschaft liegt bei "
    "Airalo, dessen Tarif von 50 GB über 30 Tage bei $0.98/GB landet. Das gesamte Angebot sind "
    "161 Tarife für Kolumbien von {{< count-providers >}} Anbietern, 85 davon unbegrenzt.",

    "Unbegrenzt ist billiger, als es aussieht: aloSIM unterbietet das Feld mit $3.05 pro Tag. Gegen "
    "$0.98/GB gemessen liegt die Gewinnschwelle bei etwa 3,1 GB pro Tag. Zwei Wochen mit Standort "
    "Bogotá und regelmäßigen Videoanrufen sind der Punkt, an dem ein größeres Kontingent einen "
    "Tagestarif schlägt. Es spricht nichts dagegen, in Kolumbien am Flughafen eine lokale SIM zu "
    "kaufen — Preis und Aktivierungszeitpunkt sind also die eigentlichen Unterschiede.",

    "Hinter jeder eSIM für Kolumbien stehen Claro, Movistar und Tigo, alle mit 5G. Rechne in "
    "Kolumbien mit 10 bis 200 Mbit/s, wobei die Spitze nur auf Claro zu erreichen ist. Alles, was "
    "Bogotá verlässt, ist auf Claro besser aufgehoben, das die größte gemessene Reichweite hält. "
    "Tigo ist die weichere Option, was erst außerhalb der großen Städte zählt. Peru liegt oft auf "
    "derselben Route — kalkuliere einen zweiten Tarif ein oder eine regionale eSIM für beide.",
]

DOCS["costa-rica"] = [
    "Daten in Costa Rica sind bezahlbar. Die falsche Form davon zu kaufen ist es nicht. Roamic hält "
    "den Einstiegspreis mit 1 GB / 7 Tage für $3.00. Diese Lücke ist die Geschichte Costa Ricas in "
    "einer Zeile: das 2,8-Fache des Tarifs für das kleinste Kontingent. Beim Preis pro Gigabyte "
    "führt Roamic mit einem Tarif von 50 GB über 30 Tage für $1.06/GB. Bei "
    "{{< count-providers >}} Anbietern läuft das Angebot auf 170 Tarife für Costa Rica, 88 davon "
    "unbegrenzt verkauft.",

    "Pro Tag gerechnet erreicht unbegrenzt mit $2.97 bei Airalo seinen Tiefpunkt. Der Umschlagpunkt "
    "in Costa Rica liegt bei etwa 2,8 GB pro Tag, wo unbegrenzt die Kontingente zu $1.06/GB "
    "einholt. Eine Städtereise rund um San José überschreitet selten ein paar Gigabyte, ein kleines "
    "Kontingent reicht also meist. Lokale Prepaid-SIMs sind in Costa Rica leicht zu kaufen, das "
    "Argument für die eSIM ist also der Preis und die Verbindung direkt bei der Landung.",

    "Costa Rica wird von Kolbi, Claro und Movistar versorgt, alle mit 5G. Der real erreichbare "
    "Durchsatz liegt je nach Netz zwischen 10 und 150 Mbit/s. Kolbi deckt die größte Fläche ab und "
    "ist damit die Voreinstellung für alles außerhalb von San José. Claro ist die weichere Option, "
    "was erst außerhalb der großen Städte zählt.",
]

DOCS["croatia"] = [
    "In Kroatien trennen pro Gigabyte nur wenige Dollar die guten von den schlechten Käufen. Ganz "
    "unten steht Yesim 500 MB / 1 Tag für $0.51. Dieselbe Summe erreicht innerhalb des Kontingents "
    "von 50 GB etwa 1,4 GB bei $0.36/GB. Den Preis pro Gigabyte setzt Roamic mit $0.36 für 50 GB "
    "über 30 Tage. Bei {{< count-providers >}} Anbietern liegen 195 Tarife für Kroatien vor, "
    "98 mit dem Label unbegrenzt.",

    "Der günstigste unbegrenzte Tarif hier ist Roamics, mit $1.00 pro Tag. Gegen den besten "
    "gemessenen Tarif von $0.36/GB braucht der Tagestarif etwa 2,8 GB pro Tag, um sich zu lohnen. "
    "Hotel-WLAN in Zagreb erledigt den Großteil der Arbeit, was gemessene Tarife billig hält. Eine "
    "lokale SIM in Kroatien zu besorgen ist einfach — Preis und sofortige Aktivierung bleiben als "
    "Gründe für eine eSIM.",

    "Den Dienst in Kroatien erbringen Hrvatski Telekom und A1 Hrvatska, beide mit 5G. Typische "
    "Tempi in Kroatien liegen zwischen 15 und 250 Mbit/s auf Hrvatski Telekom, weniger auf dem "
    "übrigen Netz. Hrvatski Telekom hat die größte Reichweite, deshalb sind Tarife darauf die "
    "sichere Wahl, sobald deine Route Zagreb verlässt. A1 Hrvatska liegt bei der Reichweite hinten, "
    "was in Kroatien nur abseits der üblichen Routen ein Problem ist.",
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
