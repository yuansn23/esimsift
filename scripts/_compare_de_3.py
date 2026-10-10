# -*- coding: utf-8 -*-
"""批 E 分册 3/5：indonesia · ireland · israel · italy · japan ·
kenya · macao · malaysia · mexico · morocco 的德语正文。

数字口径全部现算（`.buildlog/compare_de_facts.json`）：
  · ID 185 / 97 · Yesim 500 MB $0.51 · Roamic $0.66/GB · Roamic $1.55/Tag · be 2,4
  · IE 196 / 98 · Yesim 500 MB $0.51 · Roamic $0.36/GB · Roamic $1.00/Tag · be 2,8
  · IL 179 / 94 · Yesim 500 MB $0.57 · Roamic $0.50/GB · Roamic $1.37/Tag · be 2,7
  · IT 204 / 101 · Yesim 500 MB $0.51 · Ubigi $0.32/GB · Roamic $1.00/Tag · be 3,1
  · JP 211 / 102 · Roami 1 GB 3 Tage $1.99 · aloSIM $0.55/GB · Ubigi $1.50/Tag
       ⚠ japan 是唯一无 `{{< count-providers >}}` 的国家页；英语正文数字经现算**全部正确**
         （Roami 20 GB/30 Tage = $20.99 → $1.05/GB；7-Tage-unbegrenzt $18.99 vs Holafly $27.50）
  · KE 139 / 73 · Roamic 1 GB $5.00 · Ubigi $1.65/GB · Holafly $3.95/Tag · be 2,4
  · MO 127 / 53 · Yesim $0.51 · Roamic $0.54/GB · Roamic $1.47/Tag · be 2,7
  · MY 172 / 95 · Yesim 500 MB $0.51 · Roamic $0.42/GB · Roamic $1.57/Tag · be 3,7
  · MX 189 / 96 · Ubigi 500 MB 2 Tage $3.00 · Airalo $0.90/GB · Jetpac $1.88/Tag · be 2,1
  · MA 160 / 86 · Yesim 104 MB $0.51 · Nomad $0.90/GB · Roamic $2.08/Tag · be 2,3

用法：python -X utf8 scripts/_compare_de_3.py [--dry]
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _compare_de_lib import apply_country  # noqa: E402

DOCS: dict[str, list[str]] = {}

DOCS["indonesia"] = [
    "Die Preise der in Indonesien erfassten Anbieter trennen sich entlang einer Linie — und es ist "
    "nicht die Marke. Sparsame Käufer landen in Indonesien bei Yesim 500 MB / 1 Tag für $0.51. "
    "Dieselbe Summe erreicht innerhalb des Kontingents von 50 GB etwa 791 MB bei $0.66/GB. Beim "
    "Tarif gewinnt Roamic, mit $0.66/GB für einen Block von 50 GB über 30 Tage. "
    "{{< count-providers >}} Anbieter listen hier 185 Tarife für Indonesien, 97 davon unbegrenzt.",

    "Tagespreis-unbegrenzt beginnt in Indonesien bei $1.55, dank Roamic. Der Umschlagpunkt in "
    "Indonesien liegt bei rund 2,4 GB pro Tag, wo unbegrenzt die Kontingente zu $0.66/GB einholt. "
    "Eine Woche zwischen Jakarta und Surabaya ist der Punkt, an dem der Rat zum kleinen Kontingent "
    "kippt. In Indonesien brauchen lokale Prepaid-SIMs eine Passregistrierung — eine eSIM entfernt "
    "also einen Schritt, nicht nur eine Schlange.",

    "Indonesien wird von Telkomsel, Indosat und XL Axiata versorgt, alle mit 5G. Rechne in "
    "Indonesien mit 10 bis 150 Mbit/s, wobei die Spitze nur auf Telkomsel zu erreichen ist. "
    "Telkomsel deckt die größte Fläche ab und ist damit die Voreinstellung für alles außerhalb von "
    "Jakarta. Der Kompromiss ist Indosat, das in der Stadt trägt und dazwischen weniger. Reisen, "
    "die nach Singapur weitergehen, brauchen einen eigenen Tarif, weil die Abdeckung an der Grenze "
    "endet.",
]

DOCS["ireland"] = [
    "Eine kurze Sortierung des Angebots für Irland trennt die guten Käufe von der Füllware. Der "
    "billigste Tarif auf der Liste ist Yesim 500 MB / 1 Tag für $0.51. Dieselben $0.51 ergäben zum "
    "Tarif von $0.36/GB etwa 1,4 GB. Der beste Gegenwert pro Gigabyte gehört Roamic, wo 50 GB über "
    "30 Tage $0.36 pro Gigabyte ergeben. Wir erfassen hier {{< count-providers >}} Anbieter, die "
    "zusammen 196 Tarife für Irland listen, 98 davon unbegrenzt.",

    "Für Irland liegt die Tagesuntergrenze für unbegrenzt bei $1.00 mit Roamic. Gegen $0.36/GB "
    "gemessen liegt die Gewinnschwelle bei etwa 2,8 GB pro Tag. Wer aus Dublin Fotos und Videos "
    "hochlädt, verbraucht Gigabytes schneller als die meisten Reisenden erwarten. Eine lokale SIM "
    "in Irland zu besorgen ist einfach — Preis und sofortige Aktivierung bleiben als Gründe für "
    "eine eSIM.",

    "Den Dienst in Irland erbringen Vodafone, Three und Eir, alle mit 5G. Typische Tempi in Irland "
    "liegen zwischen 15 und 250 Mbit/s auf Vodafone, weniger auf den übrigen Netzen. Vodafone hat "
    "die größte Reichweite, deshalb sind Tarife darauf die sichere Wahl, sobald deine Route Dublin "
    "verlässt. Three liegt bei der Reichweite hinten, was in Irland nur abseits der üblichen Routen "
    "ein Problem ist. Reisen, die ins Vereinigte Königreich weitergehen, brauchen einen eigenen "
    "Tarif, weil die Abdeckung an der Grenze endet.",
]

DOCS["israel"] = [
    "In Israel konkurrieren zwei Preismodelle, und sie passen zu unterschiedlichen Reisen. Am "
    "günstigsten ist Yesim 500 MB / 1 Tag für $0.57. In Israel reichen dieselben $0.57 zum Tarif "
    "von $0.50/GB für etwa 1,1 GB. Das Rennen um den Preis pro Gigabyte gewinnt Roamic mit einem "
    "Tarif von 50 GB über 30 Tage für $0.50/GB. Der erfasste Katalog hält 179 Tarife für Israel "
    "von {{< count-providers >}} Anbietern, 94 davon unbegrenzt.",

    "Unbegrenzt ist billiger, als es aussieht: Roamic unterbietet das Feld mit $1.37 pro Tag. In "
    "Israel setzt der gemessene Tarif von $0.50/GB den Umschlagpunkt für unbegrenzt auf fast "
    "2,7 GB pro Tag. Auf Roadtrips außerhalb von Tel Aviv beginnt die Netzwahl mehr zu zählen als "
    "der Preis. In Israel ist für Prepaid-SIMs eine Registrierung nötig — mit bereits installierter "
    "eSIM sparst du dir einen Halt.",

    "Die nationalen Netze sind Cellcom, Partner und Pelephone, alle mit 5G. Der Durchsatz in Israel "
    "liegt je nach Netz in einem Band von 20 bis 300 Mbit/s. Außerhalb von Tel Aviv ist Cellcom das "
    "Netz der Wahl. Pelephone steht am anderen Ende: in den Städten Israels in Ordnung, dünnt aber "
    "als erstes außerhalb aus.",
]

DOCS["italy"] = [
    "In Italien sind der billigste Aufkleber und der beste Gegenwert verschiedene Tarife. Am "
    "billigsten hinein kommst du mit Yesim 500 MB / 1 Tag für $0.51. Dieselben $0.51 ergäben zum "
    "Tarif von $0.32/GB in Italien etwa 1,6 GB. Pro Gigabyte am billigsten ist Ubigi, mit 240 GB "
    "über 365 Tage für $0.32/GB. Das gesamte Angebot sind 204 Tarife für Italien von "
    "{{< count-providers >}} Anbietern, 101 davon unbegrenzt.",

    "Pro Tag gerechnet erreicht unbegrenzt mit $1.00 bei Roamic seinen Tiefpunkt. Bei $0.32/GB für "
    "gemessenes Volumen braucht unbegrenzt in Italien etwa 3,1 GB pro Tag, um Sinn zu ergeben. "
    "Streaming und Hotspot-Sharing schieben eine Rom-Reise in die unbegrenzte Stufe. Lokal in "
    "Italien zu kaufen ist einfach — Preis und sofortige Einrichtung bleiben als entscheidende "
    "Faktoren.",

    "Die lokale Abdeckung kommt in Italien von TIM, Vodafone und WindTre, alle mit 5G. Die "
    "gemessene Leistung in Italien reicht von etwa 15 Mbit/s nach oben bis nahe 300. Alles, was Rom "
    "verlässt, ist auf TIM besser aufgehoben, das die größte gemessene Reichweite hält. WindTre "
    "ist die weichere Option, was erst außerhalb der großen Städte zählt. Die Abdeckung in Italien "
    "folgt dir nicht nach Frankreich, plane also einen zweiten Tarif ein oder eine regionale eSIM.",
]

DOCS["japan"] = [
    "Die rohe Tabelle verbirgt eine Spaltung darin, wie japanische eSIMs bepreist werden — und wer "
    "sie versteht, spart echtes Geld. Ein Lager verkauft feste Datenkontingente: $4-8 für ein paar "
    "Gigabyte, die mit dem Gültigkeitsfenster verfallen. Das andere Lager, angeführt von Holafly, "
    "verkauft unbegrenzte Daten, tageweise abgerechnet zu rund $3.90 pro Tag. Unter etwa 5 GB "
    "erwartetem Verbrauch gewinnen feste Kontingente klar. Ab 15 GB beginnen die Tagestarife "
    "vernünftig auszusehen — aber nur, wenn du vorher das Kleingedruckte zur Fair-Use-Regel prüfst, "
    "denn „unbegrenzt“ bedeutet fast nie unbegrenzte Geschwindigkeit.",

    "Der Umschlagpunkt für Japan liegt niedriger, als die meisten Reisenden erwarten. Roamis Tarif "
    "von 20 GB über 30 Tage ergibt $1.05 pro Gigabyte, und seine unbegrenzte Stufe über 7 Tage für "
    "$18.99 unterbietet Holaflys vergleichbares Fenster um etwa $8, ohne eine dokumentierte "
    "Fair-Use-Grenze zu nennen. Wenn du nicht ausdrücklich die Einfachheit eines Tagespreises "
    "willst, sind die günstigsten japanischen Daten derzeit ein festes Kontingent von Roami oder "
    "Saily — kein unbegrenzter Tarif von irgendwem.",

    "Zwei Japan-spezifische Regeln prägen den Markt hier und lohnen sich vor dem Kauf. Erstens "
    "verlangen lokale Prepaid-SIMs gesetzlich eine Passprüfung, und SoftBanks eigener "
    "Aktivierungsschalter hält Öffnungszeiten von 9:00 bis 21:00 JST — Reise-eSIMs umgehen beides, "
    "weshalb späte Ankünfte in Narita und Haneda niemals auf eine lokale SIM setzen sollten. "
    "Zweitens zählt im ländlichen Japan das Netz mehr als der Preis: Tarife, die nur auf Docomo "
    "fahren, sind fast überall in Ordnung, aber Multi-Netz-Tarife, die automatisch zwischen Docomo, "
    "SoftBank und KDDI wechseln, geben dir ein Ausweichsignal in Onsen-Orten und entlang der "
    "Shinkansen-Korridore, wo ein einzelnes Netz abreißen kann.",
]

DOCS["kenya"] = [
    "In Kenia trennen pro Gigabyte nur wenige Dollar die guten von den schlechten Käufen. Roamic "
    "führt beim Einstiegspreis in Kenia mit 1 GB / 7 Tage für $5.00. Zum Tarif von $1.65/GB "
    "ausgegeben, kaufte dieselbe Summe eher 3,0 GB. Die Wertungskrone gehört Ubigi, mit $1.65/GB "
    "für 60 GB über 30 Tage. Bei {{< count-providers >}} Anbietern liegen 139 Tarife für Kenia "
    "vor, 73 mit dem Label unbegrenzt.",

    "Auf Tagesbasis ist unbegrenzt am günstigsten bei Holafly mit $3.95. Täglicher Bedarf über "
    "2,4 GB macht unbegrenzt in Kenia lohnend, gegen $1.65/GB bei gemessenem Volumen. Bleibt die "
    "Reise in Nairobi und Mombasa, deckt ein bescheidenes Kontingent Karten, Nachrichten und die "
    "eine oder andere Buchung ab. Ausweisregeln gelten in Kenia für Prepaid-SIMs, aber nicht für "
    "Reise-eSIMs, die ohne Papierkram aktiviert werden.",

    "Hinter jeder eSIM für Kenia stehen Safaricom, Airtel Kenya und Telkom Kenya, eine Mischung aus "
    "4G und 5G. Rechne in Kenia mit 8 bis 200 Mbit/s, wobei die Spitze nur auf Safaricom zu "
    "erreichen ist. Safaricom hat die größte Reichweite, deshalb sind Tarife darauf die sichere "
    "Wahl, sobald deine Route Nairobi verlässt. Telkom Kenya liegt bei der Reichweite hinten, was "
    "in Kenia nur abseits der üblichen Routen ein Problem ist.",
]

DOCS["macao"] = [
    "Anbieter in Macau berechnen dasselbe Gigabyte sehr unterschiedlich. In Macau kommt nichts "
    "unter Yesim für $0.51. Diese $0.51 kaufen einen Bruchteil dessen, was zum Tarif von $0.54/GB "
    "möglich wäre, nämlich eher 967 MB. Der beste Tarif hier ist Roamics Block von 50 GB über "
    "30 Tage für $0.54/GB. Das sind 53 unbegrenzte Tarife unter 127 Optionen für Macau von "
    "{{< count-providers >}} Anbietern.",

    "Der Preis für unbegrenzt in Macau erreicht seine Untergrenze bei $1.47 pro Tag mit Roamic. "
    "Verglichen mit $0.54/GB auf der Kontingentseite musst du etwa 2,7 GB pro Tag überschreiten, "
    "bevor unbegrenzt billiger wird. Wer von der Macau-Halbinsel aus remote arbeitet, sollte die "
    "unbegrenzte Tagesstufe vor der Buchung durchrechnen. Lokale Prepaid-SIMs sind in Macau leicht "
    "zu kaufen, das Argument für die eSIM ist also der Preis und die Verbindung direkt bei der "
    "Landung.",

    "Macau wird von CTM, 3 Macau und China Telecom versorgt, alle mit 5G. Der real erreichbare "
    "Durchsatz liegt je nach Netz zwischen 20 und 300 Mbit/s. Außerhalb der Macau-Halbinsel ist CTM "
    "das Netz der Wahl. 3 Macau steht am anderen Ende: in den Städten Macaus in Ordnung, dünnt aber "
    "als erstes außerhalb aus. Die Abdeckung in Macau folgt dir nicht nach Hongkong, plane also "
    "einen zweiten Tarif ein oder eine regionale eSIM.",
]

DOCS["malaysia"] = [
    "Sortiere die Tabelle für Malaysia nach Preis pro Gigabyte, und die Reihenfolge ändert sich. "
    "Yesim 500 MB / 1 Tag ist mit $0.51 der billigste Kauf in Malaysia. Kleine Kontingente kosten "
    "hier rund das 2,5-Fache des Tarifs der großen. Die Wertführerschaft liegt bei Roamic, dessen "
    "Tarif von 50 GB über 30 Tage bei $0.42/GB landet. Alles zusammengerechnet listen "
    "{{< count-providers >}} Anbieter 172 Tarife für Malaysia, davon 95 unbegrenzt.",

    "Roamic bepreist unbegrenzt in Malaysia ab $1.57 pro Tag. Reisen in Malaysia, die unter 3,7 GB "
    "pro Tag bleiben, sind mit einem Kontingent zu $0.42/GB billiger. Zwei Wochen mit Standort "
    "Kuala Lumpur und regelmäßigen Videoanrufen sind der Punkt, an dem ein größeres Kontingent "
    "einen Tagestarif schlägt. Eine lokale SIM in Malaysia zu besorgen ist einfach — Preis und "
    "sofortige Aktivierung bleiben als Gründe für eine eSIM.",

    "Den Dienst in Malaysia erbringen Maxis, Celcom und DiGi, alle mit 5G. Typische Tempi in "
    "Malaysia liegen zwischen 15 und 300 Mbit/s auf Maxis, weniger auf den übrigen Netzen. Alles, "
    "was Kuala Lumpur verlässt, ist auf Maxis besser aufgehoben, das die größte gemessene "
    "Reichweite hält. DiGi ist die weichere Option, was erst außerhalb der großen Städte zählt. Die "
    "Abdeckung in Malaysia folgt dir nicht nach Thailand, plane also einen zweiten Tarif ein oder "
    "eine regionale eSIM.",
]

DOCS["mexico"] = [
    "Billige Einstiegspreise in Mexiko verbergen eine weite Spanne, sobald man auf Daten normiert. "
    "In Mexiko ist Ubigi 500 MB / 2 Tage mit $3.00 so billig wie nur möglich. Einstiegstarife in "
    "Mexiko liegen beim etwa 6,8-Fachen des besten Preises pro Gigabyte. Beim Preis pro Gigabyte "
    "führt Airalo mit einem Tarif von 50 GB über 30 Tage für $0.90/GB. {{< count-providers >}} "
    "Anbieter listen hier 189 Tarife für Mexiko, 96 davon unbegrenzt.",

    "Jetpac hält den günstigsten unbegrenzten Tarif in Mexiko bei $1.88 pro Tag. Gegen $0.90/GB "
    "für gemessenes Volumen gewinnt unbegrenzt erst ab etwa 2,1 GB pro Tag. Eine Städtereise rund "
    "um Mexiko-Stadt überschreitet selten ein paar Gigabyte, ein kleines Kontingent reicht also "
    "meist. In Mexiko ist für Prepaid-SIMs eine Registrierung nötig — mit bereits installierter "
    "eSIM sparst du dir einen Halt.",

    "Die nationalen Netze sind Telcel, AT&T Mexico und Movistar, alle mit 5G. Der Durchsatz in "
    "Mexiko liegt je nach Netz in einem Band von 10 bis 250 Mbit/s. Telcel deckt die größte Fläche "
    "ab und ist damit die Voreinstellung für alles außerhalb von Mexiko-Stadt. Der Kompromiss ist "
    "Movistar, das in der Stadt trägt und dazwischen weniger. Reisen, die in die USA weitergehen, "
    "brauchen einen eigenen Tarif, weil die Abdeckung an der Grenze endet.",
]

DOCS["morocco"] = [
    "Die Preisliste für Marokko ist nicht gleichförmig, und ihre Form entscheidet, was du zahlst. "
    "Der niedrigste Aufkleberpreis gehört Yesim, dessen 104 MB / 1 Tag $0.51 kosten. Kleine Tarife "
    "in Marokko kosten pro Gigabyte das 5,5-Fache des besten Tarifs. Den Preis pro Gigabyte setzt "
    "Nomad mit $0.90 für 50 GB über 30 Tage. Wir erfassen hier {{< count-providers >}} Anbieter, "
    "die zusammen 160 Tarife für Marokko listen, 86 davon unbegrenzt.",

    "Tagespreis-unbegrenzt in Marokko beginnt bei $2.08 über Roamic. Da Kontingente $0.90/GB "
    "kosten, lohnt der Tagestarif erst ab etwa 2,3 GB pro Tag. Hotel-WLAN in Casablanca erledigt "
    "den Großteil der Arbeit, was gemessene Tarife billig hält. Passkontrollen gehören in Marokko "
    "zum Ablauf für lokale SIMs — eine Schlange, in der eine eSIM nie steht.",

    "Die lokale Abdeckung kommt in Marokko von Maroc Telecom, Orange Maroc und Inwi, alle mit 5G. "
    "Die gemessene Leistung in Marokko reicht von etwa 10 Mbit/s nach oben bis nahe 200. Maroc "
    "Telecom hat die größte Reichweite, deshalb sind Tarife darauf die sichere Wahl, sobald deine "
    "Route Casablanca verlässt. Orange Maroc liegt bei der Reichweite hinten, was in Marokko nur "
    "abseits der üblichen Routen ein Problem ist.",
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
