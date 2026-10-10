#!/usr/bin/env python3
"""批 D：`content/de/networks/*.md` 德语正文（批量，通用断言）。

结构 = 与 en 侧**逐字段对齐**。断言（每篇都跑）：
  1 front matter 字段集/顺序一致，德语侧允许唯一多出 `noindex`（分层发布）
  2 正文 h2/h3 条数与层级一一对应
  3 德语 h2/h3 禁 `,` `;` `:`（check_headings 的 RELAXED；`—`/`–` 允许）
  4 站内链必须 `/de/` 前缀（外链裸写，禁过 lang-href）
  5 单位禁 `Mbps`/`Kbps`/`Gbps`（全站口径 `Mbit/s`）
  6 短代码 `{{< count-providers >}}` 保留
德语纪律：人称 `du`；术语 Tarif / Anbieter / Heimatnetz / Kontingent / Fair-Use。
用法：python -X utf8 scripts/_patch_networks_de_batch.py [--dry] [--only SLUG]
"""
from __future__ import annotations

import argparse
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
EN_DIR = ROOT / "content" / "en" / "networks"
DE_DIR = ROOT / "content" / "de" / "networks"

DOCS: dict[str, str] = {}

# ═════════════════════════════════════════════════════════════════════════════
# canada
# ═════════════════════════════════════════════════════════════════════════════
DOCS["canada"] = '''---
title: "Kanada Reise-eSIM Netze: Bell, Rogers und Telus erklärt"
description: "Mobile Daten in Kanada gehören zu den teuersten der Industrieländer. Wie Bell, Rogers und Telus abschneiden und warum der Preis hier mehr zählt als das Netz."
date: 2026-10-03
lastmod: 2026-10-03
iso: "CA"
noindex: true
# TODO(de)：分层发布 —— 全站德语译文解禁（D9 那一轮）时删掉上面这行。
seo:
  title: "Kanada Reise-eSIM Netze 2026: Beste 5G-Abdeckung"
kicker: "Kanada ist einer der teuersten Orte der Industrieländer für mobile Daten, weshalb der Preis einer Reise-eSIM hier mehr zählt als das Netz dahinter. Alle Marken, die wir erfassen, fahren auf denselben drei Betreibern — Bell, Rogers und Telus — und zwei davon teilen ihr Funknetz sogar vollständig."
h2_carriers: "Die drei kanadischen Netze einer Reise-eSIM"
h2_scoreboard: "Bell Rogers und Telus im unabhängigen Test"
h2_brands: "Das Heimatnetz je eSIM-Marke in Kanada"
h2_cities: "Kanadische Städte mit schnellem Netz bei allen Anbietern"
h2_next: "So holst du das Meiste aus einer Kanada-eSIM"
h2_answer: "Wo eine Kanada-Reise-eSIM die Rechnung ändert"
h2_facts: "Fakten zum eSIM-Netz in Kanada"
prompt_answer: "Kanada betreibt drei nationale 5G-Netze — Bell, Rogers und Telus — und Bell und Telus teilen sich in weiten Teilen des Landes ein Funknetz, der Markt verhält sich also wie zwei Fußabdrücke statt drei. Jede Reise-eSIM-Marke, die wir erfassen, fährt auf allen dreien. Mobile Daten in Kanada gehören zu den teuersten der Industrieländer, hier zählt also der Preis mehr als die Abdeckung, und eine Reise-eSIM für Touristen braucht keinen Ausweis."
fact_registration: "Kein Ausweis und keine Registrierung für Prepaid-SIMs oder Reise-eSIMs nötig."
intro_carriers: "Keine der Marken unten besitzt einen kanadischen Masten. Jede kauft Großhandelszugang bei Bell, Rogers oder Telus, das Netz deines Tarifs ist also eine Eigenschaft des Reiseziels und der Vereinbarung hinter dem Tarif. Dieses Großhandelsmodell macht jede Marke zu einer Art MVNO, weshalb keine von ihnen bessere kanadische Abdeckung versprechen kann als eine andere."
intro_brands: "Weil Bell und Telus sich in weiten Teilen des Landes ein Funknetz teilen, fallen die drei Namen unten auf zwei echte Fußabdrücke zusammen. Genau das macht diese Tabelle zu einer Preisliste statt zu einem Abdeckungsvergleich."
cities_note: "Bell, Rogers und Telus decken Toronto, Vancouver, Montreal und Calgary alle gut ab, ein Geschwindigkeitstest in einer davon trennt die drei also selten. Der strukturelle Unterschied ist, dass Bell und Telus sich im Westen und Norden ein Funknetz teilen, was den kanadischen Markt zu zwei Fußabdrücken statt drei macht. Was eine Reise entscheidet, ist deshalb nicht die Stadt, sondern die Route aus ihr heraus."
cities_detail:
  - name: "Toronto"
    reality: "Toronto ist auf allen drei Netzen geklärt, und die Frage beginnt nördlich im Cottage Country und östlich entlang des 401-Korridors Richtung Montreal wieder, wo das Signal der Autobahn folgt statt der Karte."
  - name: "Vancouver"
    reality: "Vancouver ist auf allen dreien geklärt, und der Westen läuft auf dem gemeinsamen Funknetz von Bell und Telus, die erste echte Lücke zeigt sich also auf dem Sea-to-Sky Highway Richtung Whistler und auf den BC-Ferries-Überfahrten."
  - name: "Montreal"
    reality: "Montreal ist geklärt, und Quebec ist Bells Heimatprovinz mit Telus auf demselben Funknetz, die Abdeckung wird also in den Laurentiden und auf der langen Fahrt nach Quebec City unsicher."
  - name: "Calgary"
    reality: "Calgary ist geklärt, Telus und Bell führen im Westen gemeinsam, und die erste echte Lücke liegt westlich auf dem Highway 1 nach Banff und in die Rockies."
faq_heading: "Fragen zu Kanada-eSIM und Netz"
faqs:
  - q: "Warum sind mobile Daten in Kanada so teuer?"
    a: "Kanada verbindet eine kleine Bevölkerung mit einer enormen Landmasse, die Kosten für die Abdeckung des Landes verteilen sich also auf sehr wenige Teilnehmer. Berichtete Durchschnitte setzen den Preis lokaler Daten unter die höchsten der Industrieländer, ein Vielfaches des europäischen Niveaus. Das ist der praktische Grund, warum eine bei einem internationalen Anbieter gekaufte Reise-eSIM eine kanadische Prepaid-SIM beim Preis meist schlägt, und der Grund, warum die Spalte pro Gigabyte in unserem [Kanada-eSIM-Vergleich](/de/compare/canada/) vor der Abdeckungsspalte lesenswert ist."
  - q: "Brauche ich in Kanada einen Ausweis für SIM oder eSIM?"
    a: "Nein. Kanada kennt keine Ausweispflicht für Prepaid-SIM-Karten oder Reise-eSIMs, es gibt also keine Passprüfung, kein Registrierungsportal und keine Wartezeit. Du kannst eine kanadische Prepaid-SIM am Flughafen, in einem Betreibershop oder im Großmarkt bar kaufen, und eine Reise-eSIM kommt ganz ohne Papierkram."
  - q: "Sind Bell und Telus dasselbe Netz?"
    a: "Nicht dasselbe Unternehmen, aber sie teilen ihr Funkzugangsnetz in weiten Teilen des Landes, weshalb ihre Abdeckungskarten nahezu identisch aussehen und Opensignal sie bei der Download-Geschwindigkeit als statistisch gleichauf meldet. In der Praxis heißt das: Die Wahl zwischen ihnen ist eine Frage von Preis und Tarifform, nicht der Abdeckung. Rogers betreibt ein eigenes Netz und ist die echte Alternative."
  - q: "Welches kanadische Netz ist am schnellsten?"
    a: "Bell führt bei 5G. Es hielt im Opensignal-Bericht vom August 2026 die 5G-Download-Führung mit 173,6 Mbit/s, und Ookla kürte es für das zweite Halbjahr 2025 zum besten und schnellsten 5G-Anbieter Kanadas mit einem Median-5G-Download von 171,17 Mbit/s. Rogers holte im selben Opensignal-Zyklus mit neun die meisten Auszeichnungen insgesamt, während Telus den Titel bestes Netz gewann und den Download-Geschwindigkeitspreis mit 91,8 Mbit/s allein holte."
  - q: "Funktioniert meine eSIM auf einem kanadischen Roadtrip?"
    a: "Sie funktioniert, aber plane Lücken ein. Die kanadische Abdeckung folgt dem besiedelten Korridor entlang der Südgrenze, und lange Autobahnabschnitte zwischen Städten haben gar kein Signal. Lade Offline-Karten herunter, bevor du fährst, und behandle eine Fahrt zwischen Städten als Zeit ohne Daten, statt auf sporadisches Signal zu bauen."
  - q: "Gibt es unbegrenzte Daten mit einer Kanada-eSIM?"
    a: "Ja. Einige der Marken, die wir erfassen, listen Kanada-Tarife mit unbegrenzten Daten neben Tarifen mit festem Kontingent. Weil mobile Daten in Kanada zu den teuersten der Industrieländer gehören, ist ein unbegrenzter Tarif hier oft das bessere Preis-Leistungs-Verhältnis als in Europa, wobei nach einem Tageskontingent weiterhin die übliche Fair-Use-Schwelle greift."
  - q: "Wie viel günstiger ist eine Kanada-eSIM als ein lokaler Prepaid-Tarif?"
    a: "Meist deutlich. Lokale kanadische Daten gehören zu den teuersten der Industrieländer, während eine Reise-eSIM zu internationalen Sätzen verkauft wird, die außerhalb dieses Marktes festgelegt werden. Bei einer ein- oder zweiwöchigen Reise ist die Lücke groß genug, dass der Preis und nicht die Abdeckung der Grund ist, warum die meisten Besucher eine eSIM vor dem Flug kaufen."
  - q: "Welches kanadische Netz ist auf einem Roadtrip am besten?"
    a: "Rogers, wegen der Reichweite, weil es landesweit ein eigenes Netz betreibt, während Bell und Telus sich in weiten Teilen des Landes ein Funknetz teilen. Die Abdeckung folgt bei jedem kanadischen Netz dem besiedelten Korridor entlang der Südgrenze, lade also vor einer langen Fahrt zwischen Städten Offline-Karten herunter und behandle diese Abschnitte als Zeit ohne Daten. Für Reisen zwischen Städten zählt der Datentarif mehr als das Netz-Etikett, und das eSIM-Profil kommt innerhalb von Minuten nach der Zahlung."
---

## Warum mobile Daten in Kanada so viel kosten

Die meisten Reisezielseiten beginnen mit dem Netz. Kanada sollte mit der Rechnung beginnen, denn dort fällt die Entscheidung tatsächlich. Das Land paart eine Bevölkerung kleiner als die Kaliforniens mit einer Landmasse größer als die gesamte Europäische Union, und die Kosten für deren Abdeckung landen bei sehr wenigen Teilnehmern. Das Ergebnis ist ein Inlandspreis für Daten unter den höchsten der Industrieländer — ein Vielfaches dessen, was ein europäischer Besucher zu Hause zahlt.

Für einen Besucher ist das keine Fußnote, es ist der ganze Vergleich. Eine kanadische Prepaid-SIM ist nach internationalen Maßstäben teuer, selbst wenn sie lokal günstig aussieht, und eine vor der Abreise gekaufte Reise-eSIM unterbietet sie meist und spart den Ladenbesuch. Die Zahlen pro Gigabyte in unserer [Rangliste der Kanada-eSIM-Tarife](/de/compare/canada/) machen die Lücke konkret.

Die Netz-Frage ist hier derweil einfacher als fast überall. Alle {{< count-providers >}} Marken, die wir erfassen, fahren auf denselben drei Betreibern — Bell, Rogers und Telus — kein Anbieter kann dir also bessere Abdeckung verkaufen. Und zwei der drei gehen noch weiter: Sie teilen die Infrastruktur vollständig.

## Wie die Netzteilung von Bell und Telus funktioniert

Bell und Telus sind getrennte Unternehmen mit einem gemeinsamen Funkzugangsnetz in weiten Teilen Kanadas. Die praktische Folge: Ihre Abdeckungsfußabdrücke sind nahezu identisch, und Opensignal meldet sie bei der Gesamt-Download-Geschwindigkeit als statistisch gleichauf bei 91,5 bis 91,9 Mbit/s — eine Lücke innerhalb des Konfidenzintervalls. Die Wahl zwischen ihnen ist eine Frage von Preis und Tarifform, nicht davon, wo du Signal bekommst.

Rogers ist die echte Alternative. Es betreibt ein eigenes Netz, ist im Osten und in den Innenstädten am stärksten und hält die schnellsten Upload-Geschwindigkeiten des Landes — 13,1 Mbit/s insgesamt und 25,3 Mbit/s bei 5G im Opensignal-Zyklus vom August 2026. Upload übersieht man leicht, bis man Fotos von einer Reise verschickt, und Rogers ist das Netz, das ihn liefert.

Kanada ist also wirklich ein Markt mit zwei Fußabdrücken statt einem mit drei Betreibern, beide national. Es heißt außerdem, dass die Markentabelle unten überhaupt kein Abdeckungsvergleich ist. Sie ist eine Preisliste.

## Wie sich Bell Rogers und Telus bei 5G-Geschwindigkeit und Zuverlässigkeit unterscheiden

Bell, Rogers und Telus trennen sich bei der Leistung, auch wo sie sich bei der Verfügbarkeit einig sind.

### Bell führt bei der kanadischen 5G-Geschwindigkeit

Bell hielt im Opensignal-Bericht vom August 2026 die 5G-Download-Führung mit 173,6 Mbit/s, und Ookla kürte es für das zweite Halbjahr 2025 zum besten und schnellsten 5G-Anbieter Kanadas mit einem Median-5G-Download von 171,17 Mbit/s. Bemerkenswert: Ookla verzichtete darauf, einen Gesamtsieger beim besten Mobilfunknetz zu küren — ein Hinweis darauf, wie knapp der Markt außerhalb der 5G-Kategorie ist.

### Rogers führt bei Konsistenz und App-Erfahrung

Rogers holte im selben Zyklus mit neun die meisten Auszeichnungen, führte die App-Erfahrung an und teilte sich sowohl Zuverlässigkeit als auch gleichbleibende Qualität mit Telus. Sein Upload-Vorteil ist real und ungewöhnlich in einem Markt, in dem jeder Betreiber Download-Zahlen jagt.

### Telus ist das ausgewogene kanadische Netz

Telus gewann das beste Netz und holte den Download-Geschwindigkeitspreis mit 91,8 Mbit/s allein, und es teilt sich beide Konsistenz-Siege mit Rogers. Auf einer Fahrt durch Westkanada sind Telus und Bell wegen des gemeinsamen Netzes austauschbar.

Eine Lesgewohnheit zählt hier. Die beiden Firmen widersprechen sich in manchen Kategorien, weil sie nicht dasselbe messen — die eine beprobt, wie der durchschnittliche Nutzer das Netz erlebt, die andere nimmt den Median der selbst durchgeführten Speedtests. Wo sie auseinandergehen, behandle jede als eigenes Urteil. Keine ist ein Versprechen für deine eigene Verbindung, denn Auslastung, dein Gerät und lokale Bedingungen bewegen die Zahl.

## Ist eine Kanada-eSIM günstiger als ein kanadischer Prepaid-Datentarif

| | Reise-eSIM | Kanadische Prepaid-SIM |
|---|---|---|
| Ausweis nötig | Keiner | Keiner |
| Preis pro GB | Vom Anbieter festgelegt, meist unter lokalen Sätzen | Unter den höchsten der Industrieländer |
| Wann sie läuft | Bei der Landung, zu jeder Stunde | Sofort nach dem Kauf |
| Wo kaufen | Online, vor dem Flug | Flughafen, Betreibershops, Großmärkte |
| Am besten für | Reisen bis zu einigen Wochen | Lange Aufenthalte oder alle, die eine kanadische Nummer wollen |

Die CRTC, die den kanadischen Telekommunikationsmarkt reguliert, veröffentlicht Verbraucherhinweise zu [Roaming-Gebühren und ihrer Funktionsweise](https://crtc.gc.ca/eng/phone/mobile/trav.htm), und der von ihr durchgesetzte Wireless Code setzt die Regeln, die ein kanadischer Anbieter bei der Abrechnung befolgen muss. Das zählt für eine Prepaid-SIM weniger als für einen Vertrag, aber es lohnt zu wissen, dass der kanadische Verbraucherschutz vergleichsweise stark ist. Beim Preis ist eine Reise-eSIM der einfachere Kauf. Ein eSIM-Profil ist ein herunterladbarer Standard statt ein Chip, weshalb es überhaupt aus dem Ausland gekauft werden kann — ein Punkt, den die [GSMA](https://www.gsma.com/esim/) für alle dokumentiert, die die Mechanik wollen.

## Funktioniert eine Kanada-eSIM in den USA

Meist brauchst du einen Nordamerika-Tarif, keinen reinen Kanada-Tarif. Eine Kanada-eSIM ist für kanadische Netze bereitgestellt und endet an der Grenze, und es gibt keine kontinentale Freiroaming-Regelung. Wenn deine Reise in die USA führt — und sehr viele kanadische Routen tun das — kaufe einen regionalen Tarif und prüfe die Länderliste vor der Zahlung. Die Betreiberdetails auf der anderen Seite stehen auf unserer Seite zu den [USA-eSIM-Netzen](/de/networks/united-states/).

Das ändert auch die Rechnung. Ein Nordamerika-Tarif kostet pro Gigabyte mehr als ein reiner Kanada-Tarif, weil er einen größeren Markt abdeckt, kaufe ihn also nur, wenn die Route tatsächlich die Grenze quert. Bleibt deine Reise in Kanada, ist ein Ein-Land-Tarif günstiger und einfacher, und der [Kontingentrechner](/de/tools/) dimensioniert ihn. Aktuelle Rabatte stehen in den [eSIM-Rabattcodes](/de/esim-deals/).

Zwei Schlussprüfungen. Spektrumlizenzen werden in Kanada national vergeben, und die genutzten Bänder passen nicht zum europäischen Plan, ein weiterer Grund, dein Gerät zu prüfen. Es lohnt auch zu wissen, dass Rogers 2025 begann, 3G abzuschalten, Bell und Telus folgten in Manitoba — bring also ein Gerät mit, das 4G und VoLTE unterstützt, statt ein älteres. Unser Ratgeber [Telefon prüfen](/de/guides/esim-compatibility-check/) listet die sicheren Modelle. Kanada bietet Besuchern keinen Fair-Use-Roaming-Puffer wie die Europäische Union, ein Tarif, der das Land tatsächlich abdeckt, ist also der einzige sichere Kauf.
'''


# ═════════════════════════════════════════════════════════════════════════════
# united-states
# ═════════════════════════════════════════════════════════════════════════════
DOCS["united-states"] = '''---
title: "USA Reise-eSIM Netze: T-Mobile, AT&T und Verizon erklärt"
description: "Jede US-eSIM, die wir erfassen, fährt über T-Mobile, AT&T und Verizon. Die Marke bestimmt also den Preis und nicht die Abdeckung. Was sich auf einer USA-Reise tatsächlich unterscheidet."
date: 2026-10-03
lastmod: 2026-10-03
iso: "US"
noindex: true
# TODO(de)：分层发布 —— 全站德语译文解禁（D9 那一轮）时删掉上面这行。
seo:
  title: "USA Reise-eSIM Netze 2026: Bestes 5G für Touristen"
kicker: "Drei nationale Netze tragen jede Reise-eSIM, die wir in den USA erfassen, und alle Marken verbinden sich mit allen dreien. Kein Anbieter kann dir hier bessere Abdeckung verkaufen, die echten Fragen sind also welches Netz bei der Geschwindigkeit führt wie schnell das Signal dünner wird sobald du den Interstate verlässt und ob dein Telefon die Bänder unterstützt auf denen amerikanisches 5G läuft."
h2_carriers: "Die drei Netze hinter einer USA-eSIM"
h2_scoreboard: "Wie T-Mobile AT&T und Verizon in unabhängigen Tests abschneiden"
h2_brands: "Das US-Heimatnetz je eSIM-Marke"
h2_cities: "US-Städte in denen alle drei Netze stark sind"
h2_next: "Bevor du eine USA-eSIM kaufst"
h2_answer: "Was eine USA-Reise-eSIM wirklich ändert"
h2_facts: "Fakten zum eSIM-Netz in den USA"
prompt_answer: "Die USA betreiben drei nationale 5G-Netze — T-Mobile, AT&T und Verizon — und jede Reise-eSIM-Marke, die wir erfassen, verbindet sich mit allen dreien, kein Anbieter kann also bessere Abdeckung verkaufen als ein anderer. T-Mobile führt bei der Download-Geschwindigkeit, Verizon hält die weiteste Abdeckung, und AT&T hält etwas öfter ein nutzbares Signal. Der Kauf dreht sich um den Datentarif und den Preis, denn eine Reise-eSIM für Touristen braucht keinen Ausweis und keine Registrierung."
fact_registration: "Kein Ausweis und keine Registrierung für Prepaid-SIMs oder Reise-eSIMs nötig."
intro_carriers: "Reise-eSIM-Marken besitzen keine Masten in den USA. Sie kaufen Großhandelskapazität bei T-Mobile, AT&T und Verizon, das Netz unter deinem Tarif wählt also das Reiseziel und nicht die Marke, die du bezahlst. Jeder Anbieter hier ist faktisch ein MVNO, der Kapazität weiterverkauft, die er nicht besitzt, der Name an der Kasse kann deine Abdeckung also nicht ändern."
intro_brands: "Das Heimatnetz ist der Betreiber, auf dem ein Tarif tatsächlich fährt. In den USA listen alle Marken unten alle drei, weshalb diese Tabelle als Preisliste zu lesen ist und nicht als Abdeckungsvergleich."
cities_note: "In New York, Los Angeles, Chicago und Miami sind alle drei Netze stark, das Stadtsignal entscheidet einen US-Kauf also fast nie. Wo T-Mobile, AT&T und Verizon auseinandergehen, sind die langen Fahrten zwischen Städten, die Nationalparks und die ländlichen Countys außerhalb der Metropolregionen."
cities_detail:
  - name: "New York"
    reality: "New York ist auf allen drei Netzen geklärt, und die Abdeckung läuft das Hudson Valley hinauf und den I-95-Korridor hinunter ohne nennenswerte Unterbrechung weiter."
  - name: "Los Angeles"
    reality: "Los Angeles ist auf allen drei Netzen im ganzen Becken geklärt, und der erste echte Test ist die Wüstenfahrt nach Las Vegas und die Küstenstraße nach Norden."
  - name: "Chicago"
    reality: "Chicago ist auf allen drei Netzen geklärt, und hinter der Metropolregion beginnt in den Ebenen des Mittleren Westens der Bereich, in dem sich die drei Fußabdrücke unterscheiden."
  - name: "Miami"
    reality: "Miami ist auf allen drei Netzen geklärt, und in den Keys und den Everglades dünnt die Abdeckung aus, wobei der Overseas Highway der erste Abschnitt ist, der es zeigt."
faq_heading: "Fragen zu USA-eSIM und Netz"
faqs:
  - q: "Ändert das Netz hinter meiner US-eSIM meine Abdeckung?"
    a: "Auf Markenebene nicht. Alle Reise-eSIM-Marken, die wir erfassen, verbinden sich mit T-Mobile, AT&T und Verizon, zwei Tarife zweier verschiedener Firmen fahren also auf denselben Masten. Das gilt nicht in jedem Reiseziel — in vielen Ländern ist ein Billigtarif an einen Betreiber gebunden und zahlt dafür mit ländlichem Signal. In den USA verschwindet dieser Kompromiss, was die Entscheidung auf das Datenkontingent und den Preis pro Gigabyte verschiebt."
  - q: "Welches US-Netz ist am schnellsten und welches deckt am meisten ab?"
    a: "T-Mobile führt bei der Geschwindigkeit. Der Opensignal-Bericht vom Juli 2026 gab ihm 12 von 16 Auszeichnungen direkt, darunter Download-Geschwindigkeit mit 192,5 Mbit/s und Zuverlässigkeit mit 942 Punkten, und Ookla maß einen Median-Download von 275,6 Mbit/s für das erste Halbjahr 2026. Verizon antwortet bei der Reichweite, mit dem weitesten Abdeckungsfußabdruck der drei. AT&T liegt dazwischen und gewann die Zeit im Netz mit 99,6 % — es hält also etwas öfter eine nutzbare Verbindung als beide Rivalen."
  - q: "Funktioniert eine US-eSIM wenn ich nach Kanada oder Mexiko fahre?"
    a: "Meist nicht mit demselben Tarif. Eine länderspezifische USA-eSIM ist für US-Netze gebaut und hört an der Grenze auf zu funktionieren. In Nordamerika gibt es keine kontinentweite Freiroaming-Regelung — nichts Vergleichbares zu den Regeln der Europäischen Union — wenn deine Route also nach Kanada oder Mexiko führt, kaufe stattdessen einen Nordamerika- oder Regionaltarif und prüfe die Länderliste vor der Zahlung."
  - q: "Kann ich bei der Landung eine US-SIM am Flughafen kaufen?"
    a: "Du kannst, und in den USA ist keine Pass- oder Ausweisregistrierung nötig, der Papierkram ist also minimal. Das praktische Problem ist das Timing. Flughafenschalter und Betreibershops haben Öffnungszeiten, eine späte Ankunft bedeutet also Warten bis zum Morgen ohne Daten. Eine Reise-eSIM wird vor dem Flug installiert und verbindet sich bei der Landung zu jeder Stunde, was der Hauptgrund ist, warum sie für eine kurze Reise den Kauf am Schalter schlägt."
  - q: "Brauche ich ein bestimmtes Telefon für 5G in den USA?"
    a: "Dein Telefon muss die amerikanischen Bänder unterstützen, und eines zählt mehr als die übrigen: T-Mobiles 600-MHz-Band 71 trägt einen großen Teil seines ländlichen 5G, und außerhalb Nordamerikas verkaufte Geräte lassen es teils weg. Eine zweite Anforderung erwischt ältere Geräte — alle drei Betreiber haben ihre 3G-Netze 2022 abgeschaltet, ein Telefon ohne VoLTE-Unterstützung funktioniert also überhaupt nicht, auch nicht für Daten. Prüfe dein Modell vor dem Kauf mit unserem [eSIM-Kompatibilitätsprüfer](/de/guides/esim-compatibility-check/)."
  - q: "Gibt es unbegrenzte Daten mit einer US-eSIM?"
    a: "Ja. Mehrere Reise-eSIM-Marken, die wir erfassen, verkaufen USA-Tarife mit unbegrenzten Daten, und sie stehen im selben Vergleich wie die Tarife mit festem Kontingent. Unbegrenzte Reise-Tarife tragen fast immer eine Fair-Use-Schwelle, die die Geschwindigkeit nach einem Tageskontingent senkt, statt die Daten zu stoppen, lies diese Bedingungen also bevor du einen einem günstigeren festen Tarif vorziehst."
  - q: "Ist eine US-eSIM günstiger als Roaming mit der Heimat-SIM?"
    a: "Fast immer, und mit großem Abstand. Eine Reise-eSIM wird vorab zu einem festen Preis gekauft, ohne Tagesgebühr und ohne Rechnung, die du zu Hause öffnest, während die meisten Betreiber außerhalb Nordamerikas für US-Roaming einen Tagessatz verlangen oder dich bei wenigen hundert Megabyte pro Tag deckeln. Prüfe zuerst deinen eigenen Tarif, denn einige Tarife enthalten die USA bereits, während der Rest Roaming pro Tag abrechnet. Das Profil selbst kommt innerhalb von Minuten nach der Zahlung, was Anbieter sofortige Aktivierung nennen."
  - q: "Wie viele Daten braucht eine USA-Reise?"
    a: "Zwei Wochen gewöhnlicher touristischer Nutzung — Karten, Messaging, Foto-Uploads und gelegentliche Videoanrufe — bleiben bei den meisten Reisenden bequem unter 10 GB, und leichtere Nutzung endet deutlich unter 5 GB. Videostreaming und Hotspot-Tethering an einen Laptop sind die schweren Posten. Unser Reisedaten-Rechner dimensioniert ein Kontingent nach App, bevor du dich festlegst."
---

## Warum eine USA-eSIM zuerst eine Preisentscheidung ist und erst dann eine Abdeckungsfrage

Die amerikanische Abdeckung ist national, und das ist ungewöhnlich genug, um deinen Einkauf zu verändern. Drei Betreiber betreiben die Masten — T-Mobile, AT&T und Verizon — und jede der {{< count-providers >}} Reise-eSIM-Marken, die wir erfassen, kauft Kapazität bei allen dreien. Die Markentabelle weiter unten zeigt es ausnahmslos.

Die Folge ist unmissverständlich. Keine Marke kann dir in den USA bessere Abdeckung verkaufen, weil jede Marke dieselbe Infrastruktur einkauft. Europäische Besucher kommen oft mit der gegenteiligen Erwartung an, denn zu Hause kann ein Billigtarif wirklich ein schwächeres Netz bedeuten. Hier nicht, und damit verschwindet eine ganze Vergleichsachse.

Was bleibt, ist der Tarif selbst — wie viele Daten, über wie viele Tage, zu welchem Preis pro Gigabyte, mit welchen Hotspot-Regeln und welchen Fair-Use-Bedingungen. Unsere [USA-Tarifrangliste](/de/compare/united-states/) sortiert jeden Tarif, den wir erfassen, nach diesen Zahlen statt nach Betreiberlogos, und der Markenabschnitt unten erklärt, warum das der einzige verfügbare Vergleich ist.

## Welches US-Netz bei der Geschwindigkeit führt und welches ein Signal am längsten hält

Die Verfügbarkeit ist bei den dreien nahezu identisch. Die Leistung nicht, und beide Messfirmen sind sich bei der Richtung einig.

### T-Mobile besitzt US-Geschwindigkeit und Konsistenz

Der Opensignal-Zyklus vom Juli 2026 gab T-Mobile 12 von 16 Auszeichnungen direkt, darunter Download-Geschwindigkeit mit 192,5 Mbit/s — rund 97 Mbit/s Vorsprung auf Platz zwei — und Zuverlässigkeit mit 942 Punkten gegen AT&Ts 939 und Verizons 932. Ookla verzeichnete separat einen Median-Download von 275,6 Mbit/s für das erste Halbjahr 2026.

### Verizon besitzt die US-5G-Reichweite

Verizon hält den weitesten Abdeckungsfußabdruck der drei, weshalb es das Netz ist, auf das es ankommt, wenn deine Route durch Nationalparks oder lange ländliche Strecken führt.

### AT&T ist der US-Mittelweg

AT&T gewinnt eine Kategorie direkt, die Zeit im Netz mit 99,6 % gegen Verizons 99,5 % und T-Mobiles 99,2 %. Diese Zahl misst, wie viel der Zeit du tatsächlich eine nutzbare Verbindung hältst, und auf einer Reise, die Städte mit langen Fahrten mischt, kann sie mehr zählen als eine Spitzengeschwindigkeit.

Behandle die beiden Spalten als getrennte Ranglisten statt als eine gemischte Note. Die eine mittelt, was echte Nutzer tatsächlich erlebt haben, die andere nimmt den Mittelpunkt der selbst durchgeführten Speedtests. Die Scoreboard-Tabelle oben hält sie deshalb in getrennten Spalten. Beide sind branchenübliche Maßstäbe, und keine sagt etwas darüber, wie schnell eine Reise-eSIM auf deiner Reise läuft — die Obergrenze eines Tarifs setzt das Heimatnetz, was du tatsächlich bekommst, hängt aber auch von Auslastung, deinem Gerät und deinem Standort ab.

## Funktioniert eine USA-eSIM weiter in Kanada und Mexiko

Ob eine USA-eSIM über die kanadische und mexikanische Grenze weiter funktioniert, entscheidet viele Käufe, und die Antwort ist eine Warnung. Eine USA-eSIM ist für amerikanische Netze bereitgestellt und hört an der Grenze auf zu funktionieren. Nordamerika hat kein Gegenstück zu den Roam-like-at-home-Regeln der Europäischen Union, ein reiner US-Tarif folgt dir also nicht still nach Norden oder Süden.

| | USA-eSIM | Nordamerika-eSIM |
|---|---|---|
| Genutzte Netze | T-Mobile, AT&T, Verizon | Die drei US-Netze plus kanadische und mexikanische Betreiber |
| Funktioniert an der Grenze | Nein | Ja, in allen drei Ländern |
| Preis pro GB | Niedriger | Höher, weil drei Märkte abgedeckt werden |
| Wann kaufen | Deine Reise bleibt in den USA | Deine Route quert nach Kanada oder Mexiko |

Wenn deine Reise Niagara Falls, Vancouver, Tijuana oder Cancún berührt, ist der regionale Tarif der richtige Kauf — der Aufpreis ist kleiner als der Kauf einer zweiten eSIM mitten auf der Reise, und er beseitigt einen Ausfall, der sich gern im ungünstigsten Moment zeigt. Die Abdeckung auf der anderen Seite jeder Grenze ist eine eigene Frage, beantwortet auf unseren Seiten zu den [Kanada-eSIM-Netzen](/de/networks/canada/) und zum [Mexiko-eSIM-Netz](/de/networks/mexico/).

## USA-eSIM gegen Prepaid-Datentarif und Heimatroaming

Die USA bieten drei Wege zu mobilen Daten, und die Abwägungen sind ungewöhnlich klar, weil das Land überhaupt keine Registrierungspflicht kennt.

| | Reise-eSIM | Lokale Prepaid-SIM | Roaming mit der Heimat-SIM |
|---|---|---|---|
| Ausweis oder Pass | Nicht erforderlich | Nicht erforderlich | Nicht erforderlich |
| Wann sie läuft | Bei der Landung, zu jeder Stunde | Öffnungszeiten von Laden oder Flughafenschalter | Bei der Landung |
| Datenkontingent | Fest, vorab gekauft | Fest oder monatlich, lokal verlängert | Meist ein kleines Tageslimit |
| Kosten für zwei Wochen | Fester Preis, keine Überraschungen | Günstig pro GB, plus Weg in einen Laden | In den meisten Fällen der höchste der drei |
| Hauptnachteil | Nur Daten, keine lokale Nummer | Schlangestehen und eine neue Nummer zum Teilen | Rechnungsschock bei Überschreiten des Tageslimits |

Weil es keine Ausweispflicht gibt, ist eine Prepaid-SIM für einen langen Aufenthalt eine echt konkurrenzfähige Option — Wochen statt Tage. Für eine ein- oder zweiwöchige Reise spricht die Rechnung meist für eine Reise-eSIM, weil sie vor der Abreise gekauft wird und keinen Ladenbesuch braucht. Prüfe zuerst deinen eigenen Heimattarif, denn einige Betreiber enthalten die USA in ihren Tarifen und andere berechnen sie teuer. Der [Ratgeber eSIM gegen physische SIM](/de/guides/esim-vs-physical-sim/) deckt den allgemeinen Fall ab, und der [Reisedaten-Rechner](/de/tools/) dimensioniert ein Kontingent für deine Daten.

## Bänder und VoLTE was dein Telefon für US-5G braucht

Alle drei Betreiber betreiben kommerzielles 5G und jedes US-Betreiberprofil auf dieser Seite listet es, 5G ist also auch hier kein Unterscheidungsmerkmal zwischen Marken. T-Mobiles Download-Wert von 192,5 Mbit/s ist eine 5G-Ära-Zahl, die Technik leistet also echte Arbeit statt nur auf einem Datenblatt zu stehen.

Zwei Geräteprüfungen entscheiden, ob du sie tatsächlich bekommst. Die erste ist die Bandunterstützung: T-Mobile stützt sich beim ländlichen 5G auf das 600-MHz-Band 71, und außerhalb Nordamerikas verkaufte Telefone haben es teils nicht. Die amerikanischen Betreiber nutzen zudem Bänder, die europäische und asiatische Modelle nicht immer abstimmen, und die Spektrumszuweisungen der FCC setzen diese Landkarte. Die zweite Prüfung ist ernster. Alle drei Betreiber haben ihre [3G-Abschaltung 2022 abgeschlossen](https://www.fcc.gov/consumers/guides/3g-phase-out), ein Gerät ohne VoLTE-Unterstützung registriert sich also bei keinem von ihnen, Daten eingeschlossen. Eine eSIM ist ein herunterladbares Profil statt ein physischer Chip, und sie erbt, was dein Gerät unterstützt — der Standard wird von der [GSMA](https://www.gsma.com/esim/) gepflegt, das Profil ist also portabel, das Funkmodul nicht.

Dazu kommt die praktische Seite eines Landes dieser Größe. 5G in der Stadt ist leicht zu finden; die Lücken zeigen sich auf den langen Fahrten dazwischen, wo Verizons Abdeckungsvorteil und AT&Ts Zeit-im-Netz-Wert jede Spitzenzahl aufwiegen. Aktuelle Rabatte stehen in den [aktuellen eSIM-Angeboten](/de/esim-deals/), und die vollständige Reisezielliste steht auf der [eSIM-Netzkarte](/de/networks/).

Zwei Details lohnt es, vor der Zahlung zu bestätigen. Wo 5G fehlt, fällt das Telefon auf 4G zurück, das in amerikanischen Netzen noch schnell genug für Karten und Messaging ist. Und der Upload-Durchsatz zählt mehr, als die meisten Reisenden erwarten, weil das Posten von Fotos und das Beitreten zu Videoanrufen unterwegs der häufigste Weg ist, auf dem ein kleines Kontingent verschwindet.
'''


# ─────────────────────────────────────────────────────────────────────────────
def fm_keys(text: str) -> list[str]:
    fm = text.split("---", 2)[1]
    return [l.split(":")[0] for l in fm.split("\n") if l and not l.startswith((" ", "-", "#"))]


def body_h(text: str) -> list[str]:
    return [l for l in text.split("---", 2)[2].split("\n") if l.startswith(("## ", "### "))]


def check(slug: str, doc: str) -> list[str]:
    fails: list[str] = []
    en = (EN_DIR / f"{slug}.md").read_bytes().decode("utf-8")
    ke, kd = fm_keys(en), fm_keys(doc)
    extra = [k for k in kd if k not in ke]
    missing = [k for k in ke if k not in kd]
    if extra != ["noindex"]:
        fails.append(f"{slug}: 德语侧多出字段应为 ['noindex']，实为 {extra}")
    if missing:
        fails.append(f"{slug}: 德语侧缺字段 {missing}")
    if [k for k in kd if k != "noindex"] != ke:
        fails.append(f"{slug}: 字段顺序不一致")

    he, hd = body_h(en), body_h(doc)
    if len(he) != len(hd):
        fails.append(f"{slug}: h2/h3 条数 en={len(he)} de={len(hd)}")
    else:
        for a, b in zip(he, hd):
            if a[:3] != b[:3]:
                fails.append(f"{slug}: 层级错位 {a[:20]!r} vs {b[:20]!r}")
    for h in hd:
        t = h.lstrip("#").strip()
        if re.search(r"[,;:]", t):
            fails.append(f"{slug}: 德语标题含禁用标点 {t[:50]!r}")
    for m in re.finditer(r"\]\((/[^)]*)\)", doc):
        if not m.group(1).startswith("/de/"):
            fails.append(f"{slug}: 站内链缺 /de/ 前缀 {m.group(1)}")
    for w in ("Mbps", "Kbps", "Gbps"):
        if w in doc:
            fails.append(f"{slug}: 含非法单位 {w}")
    if "{{< count-providers >}}" not in doc:
        fails.append(f"{slug}: 缺 {{< count-providers >}}")
    return fails


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry", action="store_true")
    ap.add_argument("--only", default="")
    args = ap.parse_args()

    slugs = [args.only] if args.only else sorted(DOCS)
    allfails: list[str] = []
    written: list[str] = []
    for slug in slugs:
        doc = DOCS[slug]
        f = check(slug, doc)
        allfails += f
        if f:
            continue
        if args.dry:
            continue
        DE_DIR.mkdir(parents=True, exist_ok=True)
        p = DE_DIR / f"{slug}.md"
        if p.exists() and p.read_bytes().decode("utf-8") == doc:
            continue
        p.write_bytes(doc.encode("utf-8"))
        written.append(slug)
    if allfails:
        print("\n".join("FAIL " + x for x in allfails))
        return 1
    print(f"断言全过：{len(slugs)} 篇")
    if args.dry:
        print("（--dry：未写盘）")
        return 0
    for slug in written:
        b = (DE_DIR / f"{slug}.md").read_bytes()
        crlf = b.count(b"\r\n")
        print(f"  写入 {slug}.md  {len(b):6d} bytes  CRLF={crlf}")
    if not written:
        print("  全部已是目标内容，无需写盘")
    return 0


if __name__ == "__main__":
    sys.exit(main())
