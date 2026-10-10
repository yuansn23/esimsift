# -*- coding: utf-8 -*-
"""批 E 分册 5/5：south-korea · spain · switzerland · taiwan · thailand ·
turkiye · united-arab-emirates · united-kingdom · united-states · vietnam 的德语正文。

数字口径全部现算（`.buildlog/compare_de_facts.json`）：
  · KR 185 / 99 · Roamic 1 GB $1.00 · Roami $0.55/GB · Roamic $1.37/Tag · be 2,5
  · ES 202 / 100 · Yesim 500 MB $0.51 · Ubigi $0.45/GB · Roamic $1.10/Tag · be 2,5
  · CH 181 / 99 · Yesim 500 MB $0.51 · Roami $0.55/GB · Ubigi $1.30/Tag · be 2,4
  · TW 161 / 73 · Yesim 500 MB $0.57 · Roamic $0.56/GB · Yesim $1.47/Tag · be 2,6
  · TH 188 / 99 · Yesim 500 MB $0.51 · Nomad $0.24/GB · Nomad $1.10/Tag · be 4,6
  · TR 202 / 99 · Yesim 500 MB $0.57 · Roamic $0.46/GB · Roamic $1.10/Tag · be 2,4
  · AE 182 / 97 · Yesim 105 MB $0.51 · Jetpac $1.10/GB · Roami $1.67/Tag · be 1,5
  · GB 230 / 102 · Yesim 500 MB $0.51 · Roamic $0.44/GB · Ubigi $0.87/Tag · be 2,0
  · US 254 / 100 · Yesim 500 MB $0.51 · Nomad $0.60/GB · Roami $1.67/Tag · be 2,8
  · VN 185 / 97 · Yesim 300 MB $0.51 · Roamic $0.60/GB · Roamic $1.83/Tag · be 3,0

用法：python -X utf8 scripts/_compare_de_5.py [--dry]
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _compare_de_lib import apply_country  # noqa: E402

DOCS: dict[str, list[str]] = {}

DOCS["south-korea"] = [
    "Daten in Südkorea sind bezahlbar. Die falsche Form davon zu kaufen kostet dich etwas. Die "
    "Untergrenze in Südkorea ist Roamic 1 GB / 7 Tage für $1.00. Kleine Tarife in Südkorea kosten "
    "pro Gigabyte das 1,8-Fache des besten Tarifs. Beim Tarif gewinnt Roami, mit $0.55/GB für einen "
    "Block von 20 GB über 7 Tage. Über {{< count-providers >}} Anbieter hinweg läuft das Angebot "
    "auf 185 Tarife für Südkorea, 99 davon unbegrenzt verkauft.",

    "Auf Tagesbasis ist unbegrenzt am günstigsten bei Roamic mit $1.37. Gegen $0.55/GB für "
    "gemessenes Volumen gewinnt unbegrenzt erst ab etwa 2,5 GB pro Tag. Eine Woche zwischen Seoul "
    "und Busan ist der Punkt, an dem der Rat zum kleinen Kontingent kippt. In Südkorea gibt es "
    "keine Registrierungshürde, deshalb trennen Preis und Einrichtungsgeschwindigkeit eine eSIM von "
    "einer lokalen SIM.",

    "Die nationalen Netze sind SK Telecom, KT und LG U+, alle mit 5G. Der Durchsatz in Südkorea "
    "liegt je nach Netz in einem Band von 20 bis 350 Mbit/s. SK Telecom deckt die größte Fläche ab "
    "und ist damit die Voreinstellung für alles außerhalb von Seoul. Der Kompromiss ist LG U+, das "
    "in der Stadt trägt und dazwischen weniger. Reisen, die nach Japan weitergehen, brauchen einen "
    "eigenen Tarif, weil die Abdeckung an der Grenze endet.",
]

DOCS["spain"] = [
    "In Spanien trennen pro Gigabyte nur wenige Dollar die guten von den schlechten Käufen. Der "
    "billigste Tarif in Spanien ist Yesim 500 MB / 1 Tag für $0.51. Diese Lücke ist die Geschichte "
    "Spaniens in einer Zeile: das 2,3-Fache des Tarifs für das kleinste Kontingent. Der beste "
    "Gegenwert pro Gigabyte gehört Ubigi, wo 20 GB über 30 Tage $0.45 pro Gigabyte ergeben. Bei "
    "{{< count-providers >}} Anbietern liegen 202 Tarife für Spanien vor, 100 mit dem Label "
    "unbegrenzt.",

    "Der Preis für unbegrenzt in Spanien erreicht seine Untergrenze bei $1.10 pro Tag mit Roamic. "
    "Da Kontingente $0.45/GB kosten, lohnt der Tagestarif erst ab etwa 2,5 GB pro Tag. Wer aus "
    "Madrid Fotos und Videos hochlädt, verbraucht Gigabytes schneller als die meisten Reisenden "
    "erwarten. Lokal in Spanien zu kaufen ist einfach — Preis und sofortige Einrichtung bleiben als "
    "entscheidende Faktoren.",

    "Die lokale Abdeckung kommt in Spanien von Movistar, Vodafone, Orange und Yoigo, alle mit 5G. "
    "Die gemessene Leistung in Spanien reicht von etwa 15 Mbit/s nach oben bis nahe 300. Movistar "
    "hat die größte Reichweite, deshalb sind Tarife darauf die sichere Wahl, sobald deine Route "
    "Madrid verlässt. Yoigo liegt bei der Reichweite hinten, was in Spanien nur abseits der üblichen "
    "Routen ein Problem ist. Der Sprung nach Portugal ist üblich, und kein einzelner Tarif deckt "
    "beides ab — plane also einen zweiten Tarif ein oder einen regionalen.",
]

DOCS["switzerland"] = [
    "Anbieter in der Schweiz berechnen dasselbe Gigabyte sehr unterschiedlich. Sparsame Käufer "
    "landen in der Schweiz bei Yesim 500 MB / 1 Tag für $0.51. Dieselbe Summe erreicht innerhalb "
    "des Kontingents von 100 GB etwa 950 MB bei $0.55/GB. Das Rennen um den Preis pro Gigabyte "
    "gewinnt Roami mit einem Tarif von 100 GB über 30 Tage für $0.55/GB. Das sind 99 unbegrenzte "
    "Tarife unter 181 Optionen für die Schweiz von {{< count-providers >}} Anbietern.",

    "Ubigi bepreist unbegrenzt in der Schweiz ab $1.30 pro Tag. Unter etwa 2,4 GB pro Tag bleiben "
    "Kontingente in der Schweiz zu $0.55/GB vor jedem Tagestarif. Auf Roadtrips außerhalb von Zürich "
    "beginnt die Netzwahl mehr zu zählen als der Preis. Lokale SIMs in der Schweiz sind "
    "unkompliziert zu kaufen, das Argument für die eSIM ist also eines von Preis und sofortiger "
    "Aktivierung.",

    "Die Schweiz läuft über Swisscom, Sunrise und Salt, alle mit 5G. Praktisch liegen die Tempi je "
    "nach Netz zwischen 15 und 350 Mbit/s. Außerhalb von Zürich ist Swisscom das Netz der Wahl. "
    "Salt steht am anderen Ende: in den Städten der Schweiz in Ordnung, dünnt aber als erstes "
    "außerhalb aus. Die Abdeckung in der Schweiz folgt dir nicht nach Frankreich, plane also einen "
    "zweiten Tarif ein oder eine regionale eSIM.",
]

DOCS["taiwan"] = [
    "Sortiere die Tabelle für Taiwan nach Preis pro Gigabyte, und die Reihenfolge ändert sich. Der "
    "billigste Tarif auf der Liste ist Yesim 500 MB / 1 Tag für $0.57. Dieselben $0.57 ergäben zum "
    "Tarif von $0.56/GB etwa 1,0 GB. Beim Tarif gewinnt Roamic, mit $0.56/GB für einen Block von "
    "50 GB über 30 Tage. Alles zusammengerechnet listen {{< count-providers >}} Anbieter 161 Tarife "
    "für Taiwan, davon 73 unbegrenzt.",

    "Yesim hält den günstigsten unbegrenzten Tarif in Taiwan bei $1.47 pro Tag. Gegen $0.56/GB "
    "gemessen liegt die Gewinnschwelle bei etwa 2,6 GB pro Tag. Streaming und Hotspot-Sharing "
    "schieben eine Taipei-Reise in die unbegrenzte Stufe. Nichts spricht dagegen, in Taiwan am "
    "Flughafen eine lokale SIM zu kaufen — Preis und Aktivierungszeitpunkt sind also die "
    "eigentlichen Unterschiede.",

    "Hinter jeder eSIM für Taiwan stehen Chunghwa Telecom, Taiwan Mobile und FarEasTone, alle mit "
    "5G. Rechne in Taiwan mit 20 bis 300 Mbit/s, wobei die Spitze nur auf Chunghwa Telecom zu "
    "erreichen ist. Alles, was Taipei verlässt, ist auf Chunghwa Telecom besser aufgehoben, das die "
    "größte gemessene Reichweite hält. Taiwan Mobile ist die weichere Option, was erst außerhalb der "
    "großen Städte zählt. Japan liegt oft auf derselben Route — kalkuliere einen zweiten Tarif ein "
    "oder eine regionale eSIM für beide.",
]

DOCS["thailand"] = [
    "Billige Einstiegspreise in Thailand verbergen eine weite Spanne, sobald man auf Daten "
    "normiert. Am günstigsten ist Yesim 500 MB / 1 Tag für $0.51. In Thailand reichen dieselben "
    "$0.51 zum Tarif von $0.24/GB für etwa 2,2 GB. Beim Tarif setzt Nomad die Untergrenze mit "
    "$0.24/GB für 50 GB über 10 Tage. {{< count-providers >}} Anbieter listen hier 188 Tarife für "
    "Thailand, 99 davon unbegrenzt.",

    "Tagespreis-unbegrenzt in Thailand beginnt bei $1.10 über Nomad. Der Umschlagpunkt in Thailand "
    "liegt bei rund 4,6 GB pro Tag, wo unbegrenzt die Kontingente zu $0.24/GB einholt. Wer zwischen "
    "Bangkok und Chiang Mai unterwegs ist, bleibt beim Tagesverbrauch moderat — gemessenes Volumen "
    "bleibt damit die billigere Form. Lokale Prepaid-SIMs sind in Thailand leicht zu kaufen, das "
    "Argument für die eSIM ist also der Preis und die Verbindung direkt bei der Landung.",

    "Thailand wird von AIS, True Move und DTAC versorgt, alle mit 5G. Rechne in Thailand mit 15 bis "
    "300 Mbit/s, wobei die Spitze nur auf AIS zu erreichen ist. AIS deckt die größte Fläche ab und "
    "ist damit die Voreinstellung für alles außerhalb von Bangkok. Der Kompromiss ist DTAC, das in "
    "der Stadt trägt und dazwischen weniger. Reisen, die nach Malaysia weitergehen, brauchen einen "
    "eigenen Tarif, weil die Abdeckung an der Grenze endet.",
]

DOCS["turkiye"] = [
    "Die Preisliste für die Türkei ist nicht gleichförmig, und ihre Form entscheidet, was du zahlst. "
    "Am billigsten hinein kommst du mit Yesim für $0.57. Dieselben $0.57 ergäben zum Tarif von "
    "$0.46/GB in der Türkei etwa 1,2 GB. Die Wertungskrone gehört Roamic, mit $0.46/GB für 50 GB "
    "über 30 Tage. Wir erfassen hier {{< count-providers >}} Anbieter, die zusammen 202 Tarife für "
    "die Türkei listen, 99 davon unbegrenzt.",

    "Die unbegrenzte Stufe beginnt bei $1.10 pro Tag mit Roamic. Gegen den besten gemessenen Tarif "
    "von $0.46/GB braucht der Tagestarif etwa 2,4 GB pro Tag, um sich zu lohnen. Bleibt die Reise "
    "in Istanbul und Ankara, deckt ein bescheidenes Kontingent Karten, Nachrichten und die eine "
    "oder andere Buchung ab. Lokale Prepaid-SIMs in der Türkei bringen Registrierungspflichten mit, "
    "die Reise-eSIMs nicht haben.",

    "Den Dienst in der Türkei erbringen Turkcell, Vodafone und Turk Telekom, alle mit 5G. Typische "
    "Tempi in der Türkei liegen zwischen 15 und 300 Mbit/s auf Turkcell, weniger auf den übrigen "
    "Netzen. Turkcell hat die größte Reichweite, deshalb sind Tarife darauf die sichere Wahl, "
    "sobald deine Route Istanbul verlässt. Turk Telekom liegt bei der Reichweite hinten, was in der "
    "Türkei nur abseits der üblichen Routen ein Problem ist. Der Sprung nach Griechenland ist "
    "üblich, und kein einzelner Tarif deckt beides ab — plane also einen zweiten Tarif ein oder "
    "einen regionalen.",
]

DOCS["united-arab-emirates"] = [
    "Der Markt in den Vereinigten Arabischen Emiraten belohnt ein wenig Arithmetik. Die günstigste "
    "Option dort ist Yesim 105 MB / 1 Tag für $0.51. Dieselbe Summe ergäbe dort zum Tarif von "
    "$1.10/GB etwa 475 MB. Der beste Tarif hier ist Jetpacs Block von 10 GB für $1.10/GB. Der "
    "erfasste Katalog hält 182 Tarife für die Vereinigten Arabischen Emirate von "
    "{{< count-providers >}} Anbietern, 97 davon unbegrenzt.",

    "Tagespreis-unbegrenzt ist am günstigsten bei Roami, mit $1.67 pro Tag. In den Vereinigten "
    "Arabischen Emiraten setzt der gemessene Tarif von $1.10/GB den Umschlagpunkt für unbegrenzt "
    "auf fast 1,5 GB pro Tag. Wer aus Dubai remote arbeitet, sollte die unbegrenzte Tagesstufe vor "
    "der Buchung durchrechnen. In den Vereinigten Arabischen Emiraten ist für Prepaid-SIMs eine "
    "Registrierung nötig — mit bereits installierter eSIM sparst du dir einen Halt.",

    "Die nationalen Netze sind Etisalat und du, beide mit 5G. Der Durchsatz in den Vereinigten "
    "Arabischen Emiraten liegt je nach Netz in einem Band von 20 bis 300 Mbit/s. Außerhalb von "
    "Dubai ist Etisalat das Netz der Wahl. du steht am anderen Ende: in den Städten der "
    "Vereinigten Arabischen Emirate in Ordnung, dünnt aber als erstes außerhalb aus. Die Abdeckung "
    "dort folgt dir nicht nach Saudi-Arabien, plane also einen zweiten Tarif ein oder eine "
    "regionale eSIM.",
]

DOCS["united-kingdom"] = [
    "Der billigste Tarif im Vereinigten Königreich ist selten die billigste Reise. Yesim führt beim "
    "Einstiegspreis im Vereinigten Königreich mit 500 MB / 1 Tag für $0.51. Zum Tarif von $0.44/GB "
    "ausgegeben, kaufte dieselbe Summe eher 1,2 GB. Die Wertführerschaft liegt bei Roamic, dessen "
    "Tarif von 50 GB über 30 Tage bei $0.44/GB landet. Das gesamte Angebot sind 230 Tarife für das "
    "Vereinigte Königreich von {{< count-providers >}} Anbietern, 102 davon unbegrenzt.",

    "Unbegrenzt beginnt bei $0.87 pro Tag mit Ubigi. Bei $0.44/GB für gemessenes Volumen braucht "
    "unbegrenzt im Vereinigten Königreich etwa 2,0 GB pro Tag, um Sinn zu ergeben. Zwei Wochen mit "
    "Standort London und regelmäßigen Videoanrufen sind der Punkt, an dem ein größeres Kontingent "
    "einen Tagestarif schlägt. Lokal im Vereinigten Königreich zu kaufen ist einfach — Preis und "
    "sofortige Einrichtung bleiben als entscheidende Faktoren.",

    "Die lokale Abdeckung kommt im Vereinigten Königreich von EE, Vodafone, O2 und Three, alle mit "
    "5G. Die gemessene Leistung reicht von etwa 15 Mbit/s nach oben bis nahe 300. Alles, was London "
    "verlässt, ist auf EE besser aufgehoben, das die größte gemessene Reichweite hält. O2 steht am "
    "anderen Ende: in den Städten in Ordnung, dünnt aber als erstes außerhalb aus. Irland liegt oft "
    "auf derselben Route — kalkuliere einen zweiten Tarif ein oder eine regionale eSIM für beide.",
]

DOCS["united-states"] = [
    "Die eSIM-Preise in den USA sind weniger gleichförmig, als der Lockpreis vermuten lässt. In den "
    "USA kommt nichts unter Yesim 500 MB / 1 Tag für $0.51. Diese $0.51 kaufen einen Bruchteil "
    "dessen, was zum Tarif von $0.60/GB möglich wäre, nämlich eher 870 MB. Beim Preis pro Gigabyte "
    "führt Nomad mit einem Tarif von 50 GB über 30 Tage für $0.60/GB. Über "
    "{{< count-providers >}} Anbieter hinweg läuft das Angebot auf 254 Tarife für die USA, 100 "
    "davon unbegrenzt verkauft.",

    "In den USA beginnt unbegrenzt bei $1.67 pro Tag mit Roami. Bei gemessenem Volumen zu $0.60/GB "
    "zahlt sich unbegrenzt erst oberhalb von rund 2,8 GB pro Tag aus. Eine Städtereise rund um New "
    "York überschreitet selten ein paar Gigabyte, ein kleines Kontingent reicht also meist. Lokale "
    "SIMs in den USA sind unkompliziert zu kaufen, das Argument für die eSIM ist also eines von "
    "Preis und sofortiger Aktivierung.",

    "Die USA laufen über T-Mobile, AT&T und Verizon, alle mit 5G. Praktisch liegen die Tempi je "
    "nach Netz zwischen 25 und 350 Mbit/s. Verizon deckt die größte Fläche ab und ist damit die "
    "Voreinstellung für alles außerhalb von New York. Der Kompromiss ist T-Mobile, das in der Stadt "
    "trägt und dazwischen weniger. Reisen, die nach Kanada weitergehen, brauchen einen eigenen "
    "Tarif, weil die Abdeckung an der Grenze endet.",
]

DOCS["vietnam"] = [
    "Der Markt in Vietnam wirkt beim Einstiegspreis mittelmäßig und beim Gegenwert deutlich besser. "
    "Yesim 300 MB / 1 Tag ist mit $0.51 der billigste Kauf in Vietnam. In Vietnam reichen dieselben "
    "$0.51 zum Tarif von $0.60/GB für etwa 870 MB. Den Preis pro Gigabyte setzt Roamic mit $0.60 "
    "für 50 GB über 30 Tage. Bei {{< count-providers >}} Anbietern liegen 185 Tarife für Vietnam "
    "vor, 97 mit dem Label unbegrenzt.",

    "Der günstigste unbegrenzte Tarif in Vietnam kommt von Roamic für $1.83 pro Tag. Täglicher "
    "Bedarf über 3,0 GB macht unbegrenzt in Vietnam lohnend, gegen $0.60/GB bei gemessenem Volumen. "
    "Hotel-WLAN in Hanoi erledigt den Großteil der Arbeit, was gemessene Tarife billig hält. "
    "Ausweisregeln gelten in Vietnam für Prepaid-SIMs, aber nicht für Reise-eSIMs, die ohne "
    "Papierkram aktiviert werden.",

    "Hinter jeder eSIM für Vietnam stehen Viettel, Vinaphone und Mobifone, alle mit 5G. Rechne in "
    "Vietnam mit 15 bis 250 Mbit/s, wobei die Spitze nur auf Viettel zu erreichen ist. Viettel hat "
    "die größte Reichweite, deshalb sind Tarife darauf die sichere Wahl, sobald deine Route Hanoi "
    "verlässt. Vinaphone liegt bei der Reichweite hinten, was in Vietnam nur abseits der üblichen "
    "Routen ein Problem ist. Der Sprung nach Thailand ist üblich, und kein einzelner Tarif deckt "
    "beides ab — plane also einen zweiten Tarif ein oder einen regionalen.",
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
