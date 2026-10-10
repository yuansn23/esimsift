#!/usr/bin/env python3
"""批 C：`content/de/networks/{spain,thailand,united-kingdom}.md` 德语正文。

结构与断言逻辑完全复用 `_patch_networks_de_batch.py`（fm_keys/body_h/check/main
一字未改），只把 DOCS 换成这 3 篇。断言：
  1 front matter 字段集/顺序一致，德语侧允许唯一多出 `noindex`（分层发布）
  2 正文 h2/h3 条数与层级一一对应
  3 德语 h2/h3 禁 `,` `;` `:`（`—`/`–` 允许）
  4 站内链必须 `/de/` 前缀（外链裸写）
  5 单位禁 `Mbps`/`Kbps`/`Gbps`（全站口径 `Mbit/s`）
  6 短代码 `{{< count-providers >}}` 保留
用法：python -X utf8 scripts/_patch_networks_de_c.py [--dry] [--only SLUG]
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
# spain
# ═════════════════════════════════════════════════════════════════════════════
DOCS["spain"] = '''---
title: "Spanien Reise-eSIM Netze: Movistar, Orange, Vodafone und Yoigo erklärt"
description: "Spanien betreibt vier nationale Netze, aber zwei davon gehören jetzt derselben Gruppe. Wie Movistar, Orange, Vodafone und Yoigo für eine Spanien-eSIM abschneiden."
date: 2026-10-03
lastmod: 2026-10-03
iso: "ES"
noindex: true
# TODO(de)：分层发布 —— 全站德语译文解禁（D9 那一轮）时删掉上面这行。
seo:
  title: "Spanien Reise-eSIM Netze 2026: Bestes 5G für Touristen"
kicker: "Spanien ist das einzige Reiseziel in unserer Netzlandkarte, in dem vier Betreiber Reise-eSIM-Verkehr tragen, und zwei der vier sind heute dasselbe Unternehmen. Movistar gewinnt fast alles, was sich messen lässt, und jede Marke, die wir erfassen, fährt auf allen vier Netzen — die Marke entscheidet also über die Rechnung statt über das Signal."
h2_carriers: "Die vier spanischen Netze hinter einer Reise-eSIM"
h2_scoreboard: "Movistar Orange Vodafone und Yoigo im unabhängigen Test"
h2_brands: "Das Heimatnetz je eSIM-Marke in Spanien"
h2_cities: "Spanische Städte und Küsten mit Netz bei allen Anbietern"
h2_next: "Bevor du eine Spanien-eSIM kaufst"
h2_answer: "Wo eine Spanien-Reise-eSIM das Bild ändert"
h2_facts: "Fakten zum eSIM-Netz in Spanien"
prompt_answer: "Spanien betreibt vier nationale Netze — Movistar, Orange, Vodafone und Yoigo — und zwei davon, Orange und Yoigo, gehören derselben Gruppe, der Markt verhält sich also wie drei Wettbewerber statt vier. Movistar führt bei Geschwindigkeit und Abdeckung, und jede Reise-eSIM-Marke, die wir erfassen, fährt auf allen vier Netzen. Lokale Prepaid-SIMs brauchen eine Passregistrierung, eine Reise-eSIM für Touristen braucht gar kein Dokument."
fact_registration: "Lokale Prepaid-SIMs brauchen eine Passregistrierung. Eine Reise-eSIM braucht keine."
intro_carriers: "Spanische Reise-eSIM-Daten werden im Großhandel bei Movistar, Orange, Vodafone oder Yoigo gekauft. Der Anbieter auf deinem Tarif betreibt das Funknetz nicht, die Abdeckung bestimmen also das Heimatnetz und die Region Spaniens, in die du reist. Jede Marke hier ist ein MVNO eines oder mehrerer spanischer Netze, weshalb die vier Betreiber zählen und die Marke nicht."
intro_brands: "Alle vier spanischen Betreiber treten als Heimatnetz für jede Marke unten auf. Das macht diese Tabelle zu einer Preisliste statt zu einem Abdeckungsvergleich, und es heißt, dass es um die Datenmenge geht und nicht darum, auf wessen Masten du fährst."
cities_note: "Madrid, Barcelona, Valencia und Sevilla laufen auf den vier Netzen alle mit schnellem 5G, und auch die Küstenregionen sind gut abgedeckt. Movistars Vorsprung auf dieser Seite ist eine nationale Messung, und erst im Landesinneren, wo die Bevölkerung dünner wird, entscheidet der größere Fußabdruck über eine Reise."
cities_detail:
  - name: "Madrid"
    reality: "Madrid ist auf allen vier Netzen geklärt, und die offene Frage sind das Hochplateau um die Stadt und die Straßen nach Süden in La Mancha."
  - name: "Barcelona"
    reality: "Barcelona ist auf allen vier Netzen geklärt, und die Abdeckung dünnt nach Norden in die Pyrenäen aus, wo Bergtäler die Wahl auf den nächsten Masten reduzieren."
  - name: "Valencia"
    reality: "Valencia ist auf allen vier Netzen geklärt, und die Abdeckung läuft die Costa Blanca Richtung Alicante ohne Unterbrechung weiter."
  - name: "Sevilla"
    reality: "Sevilla ist auf allen vier Netzen geklärt, und der erste dünnere Boden liegt südlich und östlich in den andalusischen Hügeln und der Sierra."
faq_heading: "Fragen zu Spanien-eSIM und Netz"
faqs:
  - q: "Brauche ich in Spanien einen Ausweis für eine SIM-Karte?"
    a: "Für eine spanische SIM ja. Das spanische Recht verlangt, dass Prepaid-SIMs auf eine identifizierte Person registriert werden, und der Betreiber erfasst am Verkaufspunkt deinen Namen, deine Passnummer und eine Adresse. Bring einen Original-Pass mit. Eine online gekaufte Reise-eSIM kennt bei keinem Schritt eine Registrierung, was am wichtigsten ist, wenn du spät ankommst oder nur wenige Tage bleibst."
  - q: "Sind Orange und Yoigo in Spanien dasselbe Netz?"
    a: "Sie gehören derselben Gruppe an. Orange und Yoigo sitzen beide im Joint Venture MasOrange, weshalb sich ihre Abdeckungsfußabdrücke stark überschneiden und Yoigo sich wie eine Billigmarke auf einem größeren Netz verhält statt wie ein unabhängiger Betreiber mit eigenen Masten. Für Besucher heißt das praktisch, dass ein von Yoigo getragener Tarif kein Abdeckungsverlust ist, wie es ein Kleinstbetreiber-Tarif oft wäre."
  - q: "Welches spanische Netz ist am besten?"
    a: "Movistar. Der Bericht von Opensignal vom April 2026 kürte es mit 10 alleinigen und 3 geteilten Auszeichnungen zum besten Netz, inklusive Download-Geschwindigkeit mit 96,7 Mbit/s gegen Oranges 66,8. Ookla machte es separat zu Spaniens bestem Mobilfunknetz und besten 5G-Netz. Vodafone und Orange sind in Städten stark. Für das ländliche Spanien, die Pyrenäen oder das Landesinnere ist Movistars Reichweite der Grund, darauf zu achten, was unter deinem Tarif liegt."
  - q: "Kann ich eine Spanien-eSIM in Portugal oder Frankreich nutzen?"
    a: "Eine reine Spanien-eSIM endet an der Grenze. Lokal gekaufte spanische SIM-Karten enthalten Freiroaming in der Europäischen Union, aber dieses Recht gehört zur lokalen SIM und nicht zu einem spanien-spezifischen Reise-Tarif. Wenn deine Reise nach Portugal, Frankreich oder Marokko führt, kaufe einen regionalen Tarif und bestätige die Länderliste vor der Zahlung."
  - q: "Ist 5G mit einer Spanien-eSIM verfügbar?"
    a: "Ja. Alle vier Betreiber, die wir erfassen, listen 5G, und jedes spanische Betreiberprofil enthält es, es gibt also kein reines 4G-Netz zu meiden. Der Bericht von Opensignal vom April 2026 setzte Movistars 5G bei den Erlebniswerten deutlich vor das Feld, während eine Herausforderermarke die rohen 5G-Geschwindigkeitspreise holte. Für Besucher ist die nützliche Prüfung, ob der Tarif 5G listet und ob dein Gerät die spanischen Bänder unterstützt."
  - q: "Gibt es unbegrenzte Daten mit einer Spanien-eSIM?"
    a: "Ja. Einige der Marken, die wir erfassen, verkaufen Spanien-Tarife mit unbegrenzten Daten neben Tarifen mit festem Kontingent. Unbegrenzte Reise-Tarife setzen nach einem Tageskontingent normalerweise eine Fair-Use-Schwelle und senken die Geschwindigkeit, statt dich abzuklemmen, prüfe diese Grenze also, bevor du für unbegrenzt mehr zahlst."
  - q: "Ist eine Spanien-eSIM das bessere Preis-Leistungs-Verhältnis als eine lokale Prepaid-SIM?"
    a: "Für eine kurze Reise meist ja. Eine spanische Prepaid-SIM ist pro Gigabyte günstig, braucht aber eine Passregistrierung am Verkaufspunkt, und der Betreiber erfasst deinen Namen und eine Adresse. Eine Reise-eSIM kennt bei keinem Schritt eine Registrierung, was den kleinen Preisunterschied mehr als aufwiegt, wenn du spät ankommst oder nur wenige Tage bleibst."
  - q: "Wie viele Daten braucht eine Spanien-Reise?"
    a: "Eine Woche mit Karten, Nachrichten und Foto-Uploads bleibt für die meisten Besucher innerhalb von 5 GB, und zwei Wochen derselben Nutzung passen meist in 10 GB. Video-Streaming und Hotspot-Tethering sind die Posten, die ein kleines Kontingent sprengen. Unser Reisedaten-Rechner dimensioniert einen Datentarif für die Reise nach Apps und Reisedauer vor dem Kauf, was der schnellste Weg ist, den Wert eines Tarifs gegen einen anderen zu sehen."
---

## Warum Spanien vier Netze und drei Eigentümer hat

Vier Betreiber betreiben in Spanien nationale Netze, aber nur drei Unternehmen besitzen sie. Es ist das einzige Reiseziel, das wir erfassen, in dem vier Betreiber Reise-eSIM-Verkehr tragen, und die vier sind keine vier unabhängigen Unternehmen.

Orange und Yoigo sitzen beide im Joint Venture MasOrange. Ihre Abdeckungsfußabdrücke überschneiden sich dadurch stark, und Yoigo verhält sich wie eine Billigmarke auf einem großen Netz statt wie ein kleiner Betreiber mit eigenen Masten. Das ist für Besucher wirklich nützlich, denn es heißt, dass der billigste Tarif nicht automatisch ein Abdeckungsverlust ist, wie es anderswo oft der Fall ist.

Movistar und Vodafone bleiben unabhängige nationale Netze. Die echte Wahl in Spanien liegt also zwischen drei Abdeckungsfußabdrücken zu vier Preispunkten — und die Aufsichtsbehörde über alle ist die [CNMC](https://www.cnmc.es/).

Hinzu kommt, dass alle {{< count-providers >}} Reise-eSIM-Marken, die wir erfassen, sich mit allen vier Betreibern verbinden, wie die Markentabelle unten Zeile für Zeile zeigt. Kein Anbieter kann dir bessere spanische Abdeckung verkaufen als ein anderer, was die ganze Entscheidung auf Preis und Tarifform verlagert. Unsere [Spanien-Tarifrangliste](/de/compare/spain/) sortiert sie genau danach.

## Die spanische SIM-Registrierung und das eine nötige Dokument

Das spanische Recht verlangt, dass Prepaid-SIMs am Verkaufspunkt auf eine identifizierte Person registriert werden, und der Betreiber erfasst deinen Namen, deine Passnummer und eine Adresse. Bring einen Original-Pass mit und keine Kopie.

| | Reise-eSIM | Spanische Prepaid-SIM |
|---|---|---|
| Registrierung | Keine | Name, Passnummer und Adresse werden erfasst |
| Nötiges Dokument | Keines | Original-Pass |
| Funktioniert EU-weit | Nur mit einem Europa-Tarif | Ja, im Rahmen der Fair-Use-Grenzen |
| Wann sie läuft | Bei der Landung, zu jeder Stunde | Nach einem Schalterbesuch |
| Am besten für | Kurze Reisen und späte Ankünfte | Aufenthalte, die lange genug für eine spanische Nummer sind |

Besucher aus der Europäischen Union sollten ihren eigenen Tarif prüfen, bevor sie etwas kaufen. Roam-like-at-home deckt Spanien womöglich schon zu Inlandspreisen ab, was einen spanischen Tarif überflüssig macht, es sei denn, du brauchst eine lokale Nummer oder ein längeres Gültigkeitsfenster. Für alle anderen liegt die Wahl zwischen einer Reise-eSIM und einem Kauf am Schalter, und die eSIM gewinnt bei der Zeit, selbst wenn die lokale SIM beim Preis gewinnt.

## Welches spanische Netz bei der Geschwindigkeit führt und wo die anderen antworten

Spaniens Messwerte sind an der Spitze ungewöhnlich einseitig.

### Movistar ist der spanische Maßstab

Der Bericht von Opensignal vom April 2026 kürte Movistar mit 10 alleinigen und 3 geteilten Auszeichnungen zum besten Netz und bei der Download-Geschwindigkeit mit 96,7 Mbit/s — rund 30 Mbit/s vor Orange auf Platz zwei. Ookla machte es separat zu Spaniens bestem Mobilfunknetz und besten 5G-Netz für das erste Halbjahr 2025, mit einem Median-Download von 102,94 Mbit/s und einem Median-5G-Download von 191,62 Mbit/s. Seine ländliche Abdeckung ist die weiteste der vier und der Grund, warum es die sichere Wahl für das Landesinnere und den Norden ist.

### Orange ist der spanische Preis-Leistungs-Zweite

Orange holte im selben Zyklus die Download-Geschwindigkeit mit 66,8 Mbit/s und ist oft das bessere Preis-Leistungs-Verhältnis, weil es zu einer Gruppe mit der Größe gehört, aggressiv zu bepreisen. Im Zyklus von Opensignal vom April 2026 holte eine Herausforderermarke, DIGI, beide 5G-Geschwindigkeitspreise mit 260,4 Mbit/s beim 5G-Download — eine nützliche Erinnerung daran, dass eine einzelne Schlagzeilenzahl selten ein ganzes Netz beschreibt.

### Vodafone hält einen kleineren spanischen 5G-Fußabdruck

Vodafone deckt Städte und die Küste gut ab, liegt bei der 5G-Reichweite aber hinter den Führenden.

### Yoigo ist der günstige spanische Einstieg

Yoigo ist der Billig-Einstieg in dieselbe Gruppe wie Orange, weshalb es nicht der Abdeckungskompromiss ist, der eine Billigmarke sonst ist.

Behandle die beiden Spalten als unabhängige Meinungen statt als eine einzige Note. Sie werden unterschiedlich zusammengestellt und können dieselben vier Netze in eine andere Reihenfolge bringen, ohne dass eine falsch ist. Keine von beiden sagt deine eigenen Geschwindigkeiten voraus, die auch von der Auslastung und deinem Gerät abhängen.

## Insel- und Festlandabdeckung in ganz Spanien

Spaniens Geografie zerfällt in mehrere sehr unterschiedliche Abdeckungsprobleme, und die Netz-Frage ändert sich mit jedem.

| | Was dich erwartet | Welches Netz zählt |
|---|---|---|
| Madrid, Barcelona, Valencia, Sevilla | Schnelles 5G auf allen vier Netzen | Egal |
| Die mediterranen und atlantischen Resortküsten | Durchgehend solides 5G und 4G | Egal |
| Ländliches Inneres, Kastilien, Extremadura | Abdeckung dünnt außerhalb der Städte schnell aus | Movistar |
| Die Pyrenäen und der nördliche Grüngürtel | Berge und niedrige Bevölkerung machen es lückenhaft | Movistar |
| Die Balearen und die Kanaren | Auf den Hauptinseln gut abgedeckt | Egal, mit Movistar vorne auf den kleineren |

Das Muster ist beständig. Städte und Küsten sind geklärt, und je weiter deine Reise ins Landesinnere oder in die Berge führt, desto mehr zählt Movistars Reichweite. Da jede Marke, die wir erfassen, Movistar anbietet, ist das eine Prüfung des Tarifs und nicht des Anbieters.

Vodafone Spanien schaltete sein 3G-Netz 2024 ab, und Movistar beginnt seinen eigenen 3G-Rückzug im Oktober 2026 mit Abschlussziel Ende 2027. Ein 4G- oder 5G-Gerät mit VoLTE ist nicht betroffen. Eine eSIM ist ein Profil, das dein Telefon herunterlädt, statt einer Karte, die es annimmt — ein Standard, den die [GSMA](https://www.gsma.com/esim/) pflegt —, und sie erbt die Netztechnik, die dein Gerät unterstützt. Der Ratgeber [Telefon prüfen](/de/guides/esim-compatibility-check/) deckt die Details auf Modellebene ab.

## 5G in Spanien und was du vor dem Kauf prüfen solltest

Alle vier spanischen Betreiber, die wir erfassen, listen 5G, es gibt im Markt also kein reines 4G-Netz und 5G ist kein Unterscheidungsmerkmal zwischen Marken. Movistar führt bei den 5G-Erlebniswerten insgesamt, während DIGI im Zyklus von Opensignal vom April 2026 die rohen 5G-Geschwindigkeitspreise holte. Diese Lücke zwischen „bestem Erlebnis“ und „schnellster Schlagzeile“ lohnt sich zu verstehen, bevor du einen Aufpreis für eine Geschwindigkeitskennzahl zahlst, die du womöglich nie erreichst.

Das lässt drei praktische Prüfungen übrig. Listet der Tarif 5G. Unterstützt dein Gerät die spanischen Bänder. Und deckt der Tarif die Länder auf deiner Route ab, denn ein großer Teil europäischer Reisepläne quert eine Grenze und eine reine Spanien-eSIM folgt dir nicht nach Portugal oder Frankreich.

Unsere Netz-Seiten zu [Portugal](/de/compare/portugal/) und [Frankreich](/de/networks/france/) behandeln die Betreiber auf der anderen Seite. Der [Datenrechner](/de/tools/) dimensioniert ein Kontingent auf deine Reisedaten, und aktuelle Rabatte stehen in den [eSIM-Rabattcodes](/de/esim-deals/).

Zwei Schlussprüfungen. Das spanische Spektrum wird national lizenziert und die genutzten Bänder unterscheiden sich von denen Nordamerikas, weshalb sich ein importiertes Gerät zu prüfen lohnt. Der Upload-Durchsatz zählt für Videoanrufe und Foto-Uploads, und Spaniens Netze meistern beides in den Städten bequem, auch wenn Download-Zahlen die Schlagzeilen belegen.
'''


# ═════════════════════════════════════════════════════════════════════════════
# thailand
# ═════════════════════════════════════════════════════════════════════════════
DOCS["thailand"] = '''---
title: "Thailand Reise-eSIM Netze: AIS, True Move und DTAC erklärt"
description: "Thailändische SIMs brauchen eine Passregistrierung mit Gesichtsscan, und Touristen-SIMs enden nach 60 Tagen. Wie AIS, True Move und DTAC für eine Thailand-eSIM abschneiden."
date: 2026-10-03
lastmod: 2026-10-03
iso: "TH"
noindex: true
# TODO(de)：分层发布 —— 全站德语译文解禁（D9 那一轮）时删掉上面这行。
seo:
  title: "Thailand Reise-eSIM Netze 2026: Bestes 5G für Inseln"
kicker: "Thailand ist eines der schwierigsten Reiseziele Asiens für den Kauf einer lokalen SIM und eines der einfachsten für den Kauf einer eSIM. Die Registrierung verlangt jetzt einen Pass und einen biometrischen Gesichtsscan, Touristen-SIMs enden nach 60 Tagen, und alle Reise-eSIM-Marken, die wir erfassen, fahren auf denselben drei Betreibern — AIS, True Move und DTAC."
h2_carriers: "Die drei thailändischen Netze einer Reise-eSIM"
h2_scoreboard: "AIS True Move und DTAC im unabhängigen Test"
h2_brands: "Das Heimatnetz je eSIM-Marke in Thailand"
h2_cities: "Thailändische Städte und Inseln mit zuverlässiger Abdeckung"
h2_next: "So bekommst du deine Thailand-eSIM richtig hin"
h2_answer: "Was eine Thailand-Reise-eSIM vermeidet"
h2_facts: "Fakten zum eSIM-Netz in Thailand"
prompt_answer: "Thailand betreibt drei nationale 5G-Netze — AIS, True Move und DTAC — und jede Reise-eSIM-Marke, die wir erfassen, fährt auf allen dreien. AIS hat die weiteste Abdeckung, und genau die trägt auf die Inseln, während DTAC beim Download am schnellsten ist und True Move sich den Netz-Preis teilt. Thailändische SIMs brauchen eine Passregistrierung mit biometrischem Gesichtsscan und Touristen-SIMs enden nach 60 Tagen, während eine Reise-eSIM für Touristen beide Regeln überspringt."
fact_registration: "Pass plus biometrischer Gesichtsscan, und Touristen-SIMs enden nach 60 Tagen. Reise-eSIMs sind ausgenommen."
intro_carriers: "Die Kapazität thailändischer Reise-eSIMs stammt von AIS, True Move oder DTAC. Keine der Marken unten betreibt in Thailand ein eigenes Netz, deine Abdeckung bestimmt also, welchen der drei Betreiber der Tarif nutzen darf. Das macht jede Marke zu einem MVNO thailändischer Netze, die Abdeckung, die du bekommst, ist also eine Eigenschaft des Heimatnetzes des Tarifs und nicht der Marke."
intro_brands: "Jede Marke unten verbindet sich mit allen drei thailändischen Betreibern, was hier mehr zählt als in den meisten Märkten, weil ein großer Teil des Landes per Boot bereist wird. Die Tabelle ist deshalb eine Preisliste und kein Abdeckungsvergleich."
cities_note: "Bangkok, Chiang Mai, Phuket und Pattaya haben auf den drei thailändischen Netzen alle schnelle Abdeckung, das Stadt-Signal ist also geklärt. Die thailändische Abdeckungsfrage dreht sich wirklich um die Inseln und die Routen dazwischen, wo sich AIS, True Move und DTAC deutlich trennen."
cities_detail:
  - name: "Bangkok"
    reality: "Bangkok ist auf allen drei Netzen geklärt, und die Abdeckung hält über die ganze Metropolregion und hinaus entlang der Golfküste."
  - name: "Chiang Mai"
    reality: "Chiang Mai ist auf allen drei Netzen geklärt, und die nördlichen Berge sind der Punkt, an dem es sich ändert, besonders auf dem Mae-Hong-Son-Loop und den Grenzstraßen."
  - name: "Phuket"
    reality: "Phuket ist auf allen drei Netzen über die ganze Insel geklärt, und die Überfahrten nach Phi Phi und zu den anderen Andamanen-Inseln sind der Punkt, an dem die Abdeckung tatsächlich schwankt."
  - name: "Pattaya"
    reality: "Pattaya ist auf allen drei Netzen geklärt, und die Abdeckung läuft die Ostküste Richtung Rayong ohne Unterbrechung weiter."
faq_heading: "Fragen zu Thailand-eSIM und Netz"
faqs:
  - q: "Muss ich eine thailändische SIM oder eSIM registrieren?"
    a: "Jede thailändische SIM und eSIM muss auf den echten Namen registriert werden, und seit August 2025 müssen Betreiber bei der Registrierung zusätzlich eine biometrische Gesichtsprüfung durchführen. Für eine lokale SIM heißt das, persönlich einen Original-Pass vorzulegen und keine Fotokopie. Ausländische Besucher dürfen höchstens drei SIMs oder eSIMs je Betreiber registrieren. Eine vor dem Flug bei einem internationalen Anbieter gekaufte Reise-eSIM kennt nichts davon, weshalb sie für kurze Reisen zum Standard geworden ist."
  - q: "Gibt es eine Zeitgrenze für thailändische Touristen-SIMs?"
    a: "Ja. Nach einer Regel, die am 30. August 2025 in Kraft trat, sind Touristen-SIMs auf 60 Tage Nutzung begrenzt, und ein Aufladen verlängert die Grenze nicht. Eine weitere Nutzung über 60 Tage hinaus verlangt eine erneute Identifizierung beim Betreiber. Eine Reise-eSIM kennt keine solche Grenze, für einen langen Aufenthalt lohnt es sich also, eine lokal neu identifizierte SIM gegen eine Abfolge von eSIM-Tarifen abzuwägen."
  - q: "Welches thailändische Netz ist am besten?"
    a: "Das hängt davon ab, was du misst, und die beiden unabhängigen Firmen widersprechen sich auf aufschlussreiche Weise. Der Bericht von Opensignal vom August 2026 machte AIS mit sieben alleinigen und drei geteilten Siegen zum am meisten ausgezeichneten Betreiber, mit gleichbleibender Qualität bei 75,1 % und Upload-Geschwindigkeit bei 15 Mbit/s. DTAC und True holten gemeinsam den Preis für das beste Netz, wobei DTAC Zuverlässigkeit mit 907 Punkten und die schnellsten Downloads gewann. Ooklas Preis für das schnellste Netz im ersten Halbjahr 2026 ging an AIS."
  - q: "Welches Netz deckt die thailändischen Inseln am besten ab?"
    a: "AIS, und das ist die Frage, die die meisten Besucher wirklich haben. Sein Sieg bei der Abdeckungserfahrung im selben Opensignal-Zyklus spiegelt den weitesten landesweiten Fußabdruck wider, und genau der trägt auf Phuket, Koh Samui, Koh Phi Phi und die Andamanenküste. DTAC ist die Billigoption und schlägt sich in Bangkok und Chiang Mai gut; die Inseln sind die Stelle, an der es zurückfällt. Jede Marke, die wir erfassen, bietet AIS, die Prüfung gilt also dem Tarif und nicht dem Anbieter."
  - q: "Ist 5G mit einer Thailand-eSIM verfügbar?"
    a: "Ja. Alle drei Betreiber betreiben kommerzielles 5G und jedes thailändische Betreiberprofil, das wir erfassen, listet es. Opensignal maß DTACs 5G-Download im August 2026 mit 102,7 Mbit/s und überholte AIS in dieser Kategorie, während AIS beide Abdeckungskategorien gewann. Thailand hielt im Juni 2025 eine Spektrumauktion ab, die erhebliche Kapazität hinzufügte, die 5G-Leistung verbessert sich also, statt stehen zu bleiben."
  - q: "Gibt es unbegrenzte Daten mit einer Thailand-eSIM?"
    a: "Ja. Mehrere der Marken, die wir erfassen, verkaufen Thailand-Tarife mit unbegrenzten Daten neben Tarifen mit festem Kontingent, und sie stehen im selben Vergleich. Thailändische Netze sind schnell und lokale Daten sind nach internationalen Maßstäben günstig, ein unbegrenzter Tarif kann also gutes Preis-Leistungs-Verhältnis bieten, sofern du die übliche Fair-Use-Schwelle nach einem Tageskontingent akzeptierst."
  - q: "Wie viel sollte ein Thailand-eSIM-Datentarif für Touristen kosten?"
    a: "Weniger als fast überall sonst in unserer Netzlandkarte. Thailand ist ein wettbewerbsstarker Markt mit drei nationalen Betreibern und starkem Touristenverkehr, der Preis pro Gigabyte liegt also nahe am unteren Ende der Reiseziele, die wir erfassen. Dimensioniere den Datentarif nach deiner Reisedauer, statt den größten zu kaufen, denn in den unteren Stufen liegt der Wert. Für Reisen von einer Woche oder weniger gewinnen meist die mittleren Stufen, und das eSIM-Profil kommt innerhalb von Minuten nach der Zahlung."
  - q: "Funktioniert eine Thailand-eSIM in Kambodscha oder Vietnam ohne Roaming-Gebühren?"
    a: "Nicht mit einem reinen Thailand-Tarif. Regionales Roaming innerhalb Südostasiens ist nicht automatisch, eine thailand-spezifische Reise-eSIM endet also an der Grenze. Wenn deine Route nach Kambodscha, Laos, Vietnam oder Malaysia führt, kaufe einen Asien-Regionaltarif und bestätige die Länderliste vor der Zahlung."
---

## Warum die thailändische SIM-Registrierung strenger ist als in fast ganz Asien

Die meisten Reiseziele machen die lokale SIM etwas unbequem und etwas günstig. Thailand macht sie wirklich umständlich, und die Regeln summieren sich inzwischen.

Jede thailändische SIM und eSIM muss auf den echten Namen registriert werden, was für Besucher heißt, einen Original-Pass statt einer Fotokopie vorzulegen. Seit dem 18. August 2025 müssen Betreiber am Registrierungspunkt außerdem eine biometrische Gesichtsprüfung durchführen, der Vorgang umfasst also einen Gesichtsscan. Ausländische Besucher dürfen höchstens drei SIMs oder eSIMs je Betreiber registrieren. Die Regeln setzt und vollstreckt die [NBTC](https://www.nbtc.go.th/), Thailands Telekomregulierer. Kommt nach einem langen Flug ein Schalter mit Warteschlange hinzu, ändert sich die Rechnung.

Dann ist da die Zeitgrenze, die längere Aufenthalte erwischt. Seit dem 30. August 2025 sind Touristen-SIMs auf 60 Tage Nutzung begrenzt, und ein Aufladen verlängert die Grenze nicht — eine weitere Nutzung verlangt eine erneute Identifizierung beim Betreiber.

Eine vor der Abreise gekaufte Reise-eSIM hat nichts davon: keine Registrierung, keinen Gesichtsscan, keine 60-Tage-Grenze und keinen Schalter. Das ist das ganze Argument für eine Thailand-eSIM, und es ist hier ungewöhnlich stark. Unsere [Thailand-Tarifrangliste](/de/compare/thailand/) sortiert die Produkte nach Preis und Kontingent statt nach Papierkram.

## Wie AIS True Move und DTAC den thailändischen Markt aufteilen

Thailand hat eine strukturelle Besonderheit, die man zuerst verstehen sollte: True und DTAC fusionierten 2023, treten aber weiter als getrennte Marken mit unterschiedlicher Netzstrategie auf, sie teilen also Infrastruktur und messen doch unterschiedlich. Deshalb berichten die beiden unabhängigen Firmen sie uneinheitlich, und deshalb will die Rangliste oben sorgfältig gelesen werden.

### AIS führt bei thailändischer Abdeckung und Qualität

Der Bericht von Opensignal vom August 2026 machte AIS mit sieben alleinigen und drei geteilten Siegen zum am meisten ausgezeichneten Betreiber, inklusive gleichbleibender Qualität bei 75,1 %, Upload-Geschwindigkeit bei 15 Mbit/s und beiden Abdeckungskategorien. Ookla nannte es mit einem Speed Score von 70,6 gegen True dtacs 66,4 das schnellste Mobilfunknetz Thailands im ersten Halbjahr 2026. Wenn deine Reise Inseln einschließt, ist das das Netz, das du darunter willst.

### DTAC ist der thailändische Preis-Leistungs-Sprinter

DTAC teilt sich den Preis für das beste Netz mit True, gewann Zuverlässigkeit allein mit 907 von 1000 Punkten und holte die schnellsten Gesamt-Downloads mit 41,1 Mbit/s und den 5G-Download mit 102,7 Mbit/s — und überholte AIS in beidem. DTAC ist die preisorientierte Wahl und hält sich in Bangkok und im Norden gut.

### True Move besitzt die thailändische 5G-Verfügbarkeit

True Move erreichte 90,2 %, den höchsten Zeitanteil, in dem ein Nutzer mit einem 5G-Gerät tatsächlich ein 5G-Signal erkennt. In der Praxis teilt es sowohl den Preis für das beste Netz als auch das physische Netz mit DTAC.

Alle {{< count-providers >}} Reise-eSIM-Marken, die wir erfassen, verbinden sich mit allen dreien, kein Anbieter kann dir also bessere thailändische Abdeckung verkaufen. Die Markentabelle unten zeigt es Zeile für Zeile.

Die beiden Spalten ordnen dieselben Betreiber nach unterschiedlichen Belegen, die eine mittelt die nationale Nutzererfahrung und die andere nimmt den Median freiwilliger Speedtests. Keine von beiden sagt deinen eigenen Durchsatz voraus, der auch von der Auslastung, deinem Gerät und den unterstützten Bändern abhängt.

## Die 60-Tage-Grenze für thailändische Touristen-SIMs

Eine thailändische lokale SIM lohnt den Aufwand nur für einen langen Aufenthalt statt für einen Urlaub. Das erwartet dich.

| | Reise-eSIM | Thailändische Touristen-SIM |
|---|---|---|
| Registrierung | Keine | Echter Name mit einem Original-Pass |
| Biometrische Prüfung | Keine | Gesichtsprüfung seit August 2025 |
| Grenze pro Person | Keine | Drei SIMs oder eSIMs je Betreiber |
| Maximale Dauer | Vom Tarif festgelegt | 60 Tage, und Aufladen verlängert sie nicht |
| Wo du sie kaufst | Online, vor dem Flug | Flughafenschalter, Betreibershops, Convenience-Stores |
| Am besten für | Reisen bis zu einigen Wochen | Aufenthalte, die lang genug für eine erneute Identifizierung sind |

Die 60-Tage-Grenze ist das Detail, das die meisten Besucher übersehen. Wenn du länger bleibst, plane entweder eine erneute Identifizierung beim Betreiber ein oder kaufe deine Daten in Etappen, und prüfe, was die Gültigkeit des Tarifs selbst erlaubt, statt anzunehmen, er lasse sich unbegrenzt aufladen.

## Inselabdeckung und welches thailändische Netz für Inseln am besten ist

Thailands Geografie macht die Abdeckung zu einer praktischen statt zu einer technischen Frage, weil ein großer Teil der Besuche Wasser einschließt.

| | Was dich erwartet | Welches Netz |
|---|---|---|
| Bangkok und die Metropole | Schnelles 5G auf allen drei | Egal |
| Chiang Mai, Chiang Rai und der Norden | Solides 4G mit wachsendem 5G | Egal, mit AIS vorne in den Hügeln |
| Phuket, Krabi, Koh Samui, Koh Phi Phi | Gute Abdeckung nahe den Resorts, dünner auf kleineren Inseln | AIS |
| Kleinere und entferntere Inseln | Stellenweise nutzbar, anderswo lückenhaft | AIS |
| Grenzregionen zu Myanmar, Laos oder Kambodscha | Die Abdeckung kann auf ein Nachbarnetz abdriften | Prüfe die Länderliste deines Tarifs |

Die letzte Zeile verdient einen Moment. Entlang der thailändischen Landgrenzen empfangen Telefone manchmal das Netz eines Nachbarlandes, was bei einem länderspezifischen Tarif entweder keinen Dienst oder eine unerwartete Rechnung bedeutet. AIS hat in diesen Gebieten den beständigsten Inlandsfußabdruck.

Die NBTC hat AIS und True verpflichtet, bis zum dritten Quartal 2026 Fahrpläne für die Abschaltung von 2G und 3G vorzulegen, und genehmigte ab August 2025 keine Importe reiner 2G- und 3G-Geräte mehr. Bring ein 4G- oder 5G-Gerät mit VoLTE mit, dann betrifft dich nichts davon. Eine eSIM ist ein Download statt einer physischen Karte — ein Standard, den die [GSMA](https://www.gsma.com/esim/) pflegt —, und sie läuft auf den Bändern, die dein Telefon unterstützt. Der [eSIM-Kompatibilitätscheck](/de/guides/esim-compatibility-check/) deckt die Details auf Modellebene ab.

## Einen Thailand-eSIM-Datentarif fürs Inselhüpfen dimensionieren

Alle drei Betreiber, die wir erfassen, listen 5G, die Technik ist also kein Unterscheidungsmerkmal zwischen Marken. Wo es zählt, ist die Geschwindigkeit der Verbesserung: DTAC hob seinen 5G-Download in einem einzigen Berichtszyklus um 13 Mbit/s an und überholte AIS mit 102,7 Mbit/s, und Thailands Spektrumauktion vom Juni 2025 fügte erhebliche neue Kapazität hinzu. Thailändisches 5G wird schneller, statt sich einzupendeln.

Für Besucher sind die nützlichen Prüfungen enger. Listet der Tarif alle drei Betreiber, was dich auf den kleineren Inseln schützt. Erlaubt er Hotspot-Sharing, wenn du zu zweit reist. Und passt das Kontingent zur Reisedauer, denn Karten-Apps und Foto-Uploads summieren sich im Strandurlaub schneller, als die meisten erwarten.

Unsere [Rangliste der Thailand-eSIM-Tarife](/de/compare/thailand/) sortiert jeden Tarif, den wir erfassen, nach Preis pro Gigabyte und pro Tag, und der [Reisekosten-Rechner](/de/tools/) schätzt ein Kontingent aus deinen Apps und Reisedaten. Aktuelle Rabatte stehen in den [eSIM-Rabattcodes diesen Monats](/de/esim-deals/).

Drei praktische Hinweise. Das thailändische Spektrum wird national lizenziert und die genutzten Bänder unterscheiden sich von denen Europas, bestätige also, dass dein Gerät sie unterstützt. Thailand steht außerhalb jeder regionalen Roaming-Regelung, was heißt, dass eine hier genutzte Heimat-SIM zu internationalen Sätzen abgerechnet wird und ein lokal gekaufter Prepaid-Tarif eigene Fair-Use-Bedingungen trägt. Wenn du am Ende doch diese lokale Prepaid-SIM als Backup kaufst, gelten Gesichtsscan und 60-Tage-Grenze auch für sie.
'''


# ═════════════════════════════════════════════════════════════════════════════
# united-kingdom
# ═════════════════════════════════════════════════════════════════════════════
DOCS["united-kingdom"] = '''---
title: "Vereinigtes Königreich Reise-eSIM Netze: EE, Vodafone, O2 und Three erklärt"
description: "Das Vereinigte Königreich verlangt für eine Prepaid-SIM keinen Ausweis, aber der Brexit beendete das freie EU-Roaming. Wie EE, Vodafone, O2 und Three für eine Reise-eSIM abschneiden."
date: 2026-10-03
lastmod: 2026-10-03
iso: "GB"
noindex: true
# TODO(de)：分层发布 —— 全站德语译文解禁（D9 那一轮）时删掉上面这行。
seo:
  title: "Vereinigtes Königreich Reise-eSIM Netze 2026: Bestes 5G für Touristen"
kicker: "Das Vereinigte Königreich ist eines der einfachsten Länder der Welt, um mobile Daten zu kaufen, und eines der kniffligsten, um sie wieder mitzunehmen. Es gibt überhaupt keine Registrierungspflicht, vier Netze tragen Reise-eSIM-Verkehr, und jede Marke, die wir erfassen, fährt auf allen vier."
h2_carriers: "Die vier britischen Netze einer Reise-eSIM"
h2_scoreboard: "EE Vodafone O2 und Three im unabhängigen Test"
h2_brands: "Das Heimatnetz je eSIM-Marke im Vereinigten Königreich"
h2_cities: "Britische Städte mit schnellem Netz bei allen Anbietern"
h2_next: "So planst du deine Reise-eSIM für das Vereinigte Königreich"
h2_answer: "Was eine Reise-eSIM für das Vereinigte Königreich nicht löst"
h2_facts: "Fakten zum eSIM-Netz im Vereinigten Königreich"
prompt_answer: "Das Vereinigte Königreich betreibt vier nationale 5G-Netze — EE, Vodafone, O2 und Three — und jede Reise-eSIM-Marke, die wir erfassen, fährt auf allen vier. EE ist der stärkste Akteur und hat die weiteste Abdeckung inklusive des ländlichen Schottland, Wales und Nordirland, während O2 den Preis für die Abdeckungserfahrung und Three das rohe 5G-Geschwindigkeit holt. Für eine Prepaid-SIM gibt es keine Ausweispflicht, aber der Brexit beendete das freie EU-Roaming, eine Reise-eSIM für Touristen endet also am Ärmelkanal."
fact_registration: "Kein Ausweis für Prepaid-SIMs oder Reise-eSIMs nötig."
intro_carriers: "Reise-eSIM-Daten für das Vereinigte Königreich werden im Großhandel bei EE, Vodafone, O2 oder Three gekauft. Die Marke hinter dem Tarif betreibt die Masten nicht, das Netz, auf dem du fährst, ist also eine Eigenschaft des Reiseziels und nicht des Unternehmens, das du bezahlst. Jede Marke hier ist damit ein MVNO britischer Netze, und keine von ihnen besitzt die Funkausrüstung, von der ihre Tarife abhängen."
intro_brands: "Vier britische Betreiber treten als Heimatnetz für jede Marke unten auf, die Tabelle ist also eine Preisliste statt ein Abdeckungsvergleich. Eines ist erwähnenswert: Vodafone und Three haben fusioniert, die Form des Marktes pendelt sich also noch ein."
cities_note: "London, Manchester, Birmingham und Edinburgh laufen auf den vier Netzen alle mit schnellem 5G, die Stadt-Abdeckung ist also geklärt. Interessanter wird das britische Bild in Schottland, im ländlichen Wales und in Nordirland, wo sich EE, Vodafone, O2 und Three klar trennen."
cities_detail:
  - name: "London"
    reality: "London ist auf allen vier Netzen geklärt, auch in weiten Teilen der Underground, und die Abdeckung läuft durch die Home Counties entlang der Hauptbahnkorridore weiter."
  - name: "Manchester"
    reality: "Manchester ist auf allen vier Netzen geklärt, und der erste dünnere Boden liegt östlich im Peak District und nördlich Richtung Lake District."
  - name: "Birmingham"
    reality: "Birmingham ist auf allen vier Netzen geklärt, und die Abdeckung läuft westlich ins ländliche Wales, wo die Lücke zwischen den vier Fußabdrücken am weitesten ist."
  - name: "Edinburgh"
    reality: "Edinburgh ist auf allen vier Netzen geklärt, und nördlich der Stadt sind die Highlands und die Inseln die Stelle, an der die vier am stärksten auseinandergehen."
faq_heading: "Fragen zu eSIM und Netz im Vereinigten Königreich"
faqs:
  - q: "Brauche ich im Vereinigten Königreich einen Ausweis für eine SIM?"
    a: "Nein. Prepaid-SIM-Karten im Vereinigten Königreich brauchen keine Identitätsregistrierung, keine Passprüfung und keine Adresse, und sie lassen sich am selben Tag kaufen und aktivieren. Nur Monatsverträge verlangen eine Bonitätsprüfung und eine britische Adresse. Das stellt das Vereinigte Königreich neben Kanada und die USA in die Gruppe ohne Papierkram, und es heißt, dass eine lokale Prepaid-SIM für alle, die länger als ein paar Wochen bleiben, eine wirklich konkurrenzfähige Option ist."
  - q: "Kann ich eine eSIM für das Vereinigte Königreich in Europa nutzen?"
    a: "Ein Tarif, der nur das Vereinigte Königreich abdeckt, endet an der Grenze. Wichtiger noch: Das freie Roaming auf britischen SIM-Karten endet dort ebenfalls. Das Vereinigte Königreich verließ zum Ende der Übergangsphase die Freiroaming-Regelungen der Europäischen Union, und es gibt keine gesetzliche Pflicht für britische Betreiber, aufschlagsfreies Roaming in der EU oder im EWR anzubieten. Die meisten britischen Netze verlangen heute eine Tagesgebühr für die europäische Nutzung, ein solcher Tarif ist also der falsche Kauf, wenn deine Reise nach Europa weitergeht."
  - q: "Welches britische Netz ist am besten?"
    a: "EE ist mit Abstand der stärkste Akteur. Der Bericht von Opensignal vom Januar 2026 gab ihm 11 alleinige Auszeichnungen, inklusive Download-Geschwindigkeit mit 53,2 Mbit/s, und Ooklas Fahrtests ergaben, dass es zum 26. Mal in Folge jeden landesweiten RootScore gewann oder teilte, mit einem Median-Download von 130,3 Mbit/s. O2 gewann den Preis für die Abdeckungserfahrung allein mit 9,0 von 10, und Three holte das 5G-Download-Geschwindigkeit mit 187 Mbit/s. EE hat die weiteste Abdeckung inklusive des ländlichen Schottland, Wales und Nordirland."
  - q: "Ist 5G mit einer eSIM für das Vereinigte Königreich verfügbar?"
    a: "Ja. Alle vier Netze betreiben kommerzielles 5G und jedes britische Betreiberprofil, das wir erfassen, listet es. Three führt die rohe 5G-Download-Zahl mit 187 Mbit/s im Zyklus von Opensignal vom Januar 2026 an, während EE bei den Erlebnis- und Zuverlässigkeitswerten insgesamt führt. Weil alle vier 5G haben, lohnt sich hier kein Aufpreis dafür — die Prüfung, die zählt, ist, ob dein Gerät die britischen Bänder unterstützt."
  - q: "Funktioniert eine eSIM für das Vereinigte Königreich in Irland?"
    a: "Nicht mit einem reinen britischen Tarif, und das erwischt Leute, weil Irland wie eine innerbritische Verlängerung einer Reise aussieht. Die beiden sind getrennte Mobilfunkmärkte ohne Freiroaming-Abkommen zwischen sich, die Überfahrt nach Dublin heißt also, einen Tarif zu kaufen, der Irland abdeckt, oder einen Europa-Regionaltarif. Prüfe die Länderliste des Tarifs vor der Zahlung, statt anzunehmen, die Inseln reisten gemeinsam."
  - q: "Gibt es unbegrenzte Daten mit einer eSIM für das Vereinigte Königreich?"
    a: "Ja. Mehrere Marken, die wir erfassen, verkaufen Tarife mit unbegrenzten Daten neben Tarifen mit festem Kontingent. Nach einem Tageskontingent greift die übliche Fair-Use-Schwelle, die die Geschwindigkeit senkt, statt die Verbindung zu beenden. Ein großzügiger fester Tarif ist hier oft das bessere Preis-Leistungs-Verhältnis, weil die vier Netze schnell sind und gewöhnliche touristische Nutzung selten den Punkt erreicht, an dem sich unbegrenzt auszahlt."
  - q: "Ist eine eSIM für das Vereinigte Königreich günstiger als Roaming mit einer Heimat-SIM?"
    a: "Für Besucher von außerhalb Europas fast immer. Eine Reise-eSIM wird im Voraus zu einem festen Preis gekauft, während die meisten Heimat-Betreiber für Roaming einen Tagessatz verlangen oder dich auf ein kleines Tageskontingent begrenzen. Dieser Vergleich ist der Grund, warum das Vereinigte Königreich einer der Märkte ist, in denen ein vor der Abreise gekaufter Datentarif das Roaming klar schlägt, weshalb wir es als die günstigere Route für Reisen dorthin zählen."
  - q: "Ist Nordirland mit einer eSIM für das Vereinigte Königreich abgedeckt?"
    a: "Ja, und derselbe Tarif, der England und Schottland abdeckt, deckt es ab. Nordirland ist Teil des Vereinigten Königreichs, eine solche eSIM registriert sich dort also genauso wie in London. Die Komplikation ist die Landgrenze, wo ein Gerät in einem Grenzcounty auf ein Netz der Republik Irland abdriften und bei einem reinen britischen Tarif den Dienst verlieren oder eine unerwartete Rechnung einfangen kann. Wenn die Route in die Republik führt, kaufe einen Europa-Regionaltarif und bestätige, dass die Länderliste beide Seiten abdeckt."
---

## Was der Brexit beim Roaming in Europa geändert hat

Beginne mit der Regel, die die meisten Besucher überrascht, denn sie ist ein echter Bruch mit dem übrigen Europa.

Das Vereinigte Königreich verließ die Freiroaming-Regelungen der Europäischen Union mit dem Ende der Übergangsphase, und keine gesetzliche Pflicht verlangt heute von britischen Betreibern, aufschlagsfreies Roaming in der EU oder im EWR anzubieten. In der Praxis verlangen die meisten britischen Netze eine Tagesgebühr für die europäische Nutzung, statt sie einzuschließen, was heißt, dass eine lokal gekaufte britische SIM der falsche Kauf für eine Reise ist, die nach Frankreich, Spanien oder Irland weitergeht. Wer zuletzt vor 2021 mit einer britischen SIM gereist ist, arbeitet mit veralteten Erwartungen.

Umgekehrt gilt dasselbe. Eine Reise-eSIM, die nur das Vereinigte Königreich abdeckt, ist für britische Netze bereitgestellt und endet an der Grenze, und die Überfahrt nach Dublin oder Paris ist in Mobilfunkbegriffen ein separates Land, auch wenn sie in Reisebegriffen ein kurzer Sprung ist.

Diese eine Regel formt den Kauf neu. Ist deine Reise nur das Vereinigte Königreich, kaufe einen Tarif dafür. Ist sie eine Europareise, die in London beginnt oder endet, kaufe einen Europa-Regionaltarif und bestätige die Länderliste vor der Zahlung. Unsere Seiten zu [Irland](/de/compare/ireland/) und zu den [Frankreich-eSIM-Netzen](/de/networks/france/) behandeln die Betreiber auf der anderen Seite.

## Warum das Vereinigte Königreich einer der einfachsten Orte für den Datenkauf ist

Nun die gute Nachricht, die das Gegenteil von Deutschland, Spanien und Thailand ist.

Das Vereinigte Königreich kennt keine Identitätsregistrierungspflicht für Prepaid-SIM-Karten. Kein Pass, kein Video-Ident-Anruf, keine Warteschlange am Schalter für Papierkram, kein Registrierungsportal. Du kaufst eine Pay-as-you-go-SIM in einem Laden oder am Flughafen, oder du installierst vor dem Flug eine Reise-eSIM, und beides funktioniert sofort. Ofcom, das die Kommunikation im Vereinigten Königreich reguliert, betreibt sogar einen öffentlichen [Mobilfunkabdeckungs-Checker](https://www.ofcom.org.uk/phones-and-broadband/coverage-and-speeds/ofcom-checker), der das Signal je Anbieter für jede Postleitzahl zeigt — nützlich, wenn du an einem bestimmten Ort bleibst, statt umherzureisen.

| | Reise-eSIM | Britische Prepaid-SIM |
|---|---|---|
| Ausweis nötig | Keiner | Keiner |
| Registrierung | Keine | Keine |
| Funktioniert EU-weit | Nur mit einem Europa-Tarif | Nur mit einem Roaming-Zusatz, der extra kostet |
| Wann sie läuft | Bei der Landung, zu jeder Stunde | Sofort nach dem Kauf |
| Am besten für | Reisen bis zu einigen Wochen | Längere Aufenthalte oder alle, die eine britische Nummer wollen |

Weil in beide Richtungen keine Reibung besteht, läuft die Wahl auf Preis und Bequemlichkeit hinaus statt auf Papierkram. Britische Prepaid-SIMs sind für längere Aufenthalte konkurrenzfähig, und eine Reise-eSIM gewinnt in der ersten Stunde nach der Landung und dadurch, dass sie vor der Abreise gekauft wird.

Alle {{< count-providers >}} Reise-eSIM-Marken, die wir erfassen, verbinden sich mit allen vier Netzen — EE, Vodafone, O2 und Three — wie die Markentabelle unten Zeile für Zeile zeigt. Kein Anbieter kann dir bessere britische Abdeckung verkaufen als ein anderer.

## Wo EE führt und wo O2 und Three antworten

Der britische Markt hat einen klaren Führenden und dahinter eine klare Aufteilung.

### EE gewinnt fast alles im Vereinigten Königreich

Der Bericht von Opensignal vom Januar 2026 gab EE 11 alleinige Auszeichnungen, inklusive Download-Geschwindigkeit mit 53,2 Mbit/s, Zuverlässigkeit mit 915 von 1000 Punkten und gleichbleibender Qualität bei 78,6 %. Ooklas Fahrtests ergaben, dass es zum 26. Mal in Folge jeden landesweiten RootScore gewann oder teilte, mit einem Median-Download von 130,3 Mbit/s — mehr als das Doppelte des nächstbesten Ergebnisses. Wenn deine Reise die schottischen Highlands, das ländliche Wales oder Nordirland einschließt, ist EEs Reichweite der Grund, warum du es unter deinem Tarif haben willst.

### O2 besitzt die Abdeckung als Kategorie

O2 gewann die Abdeckungserfahrung allein mit 9,0 von 10 und ist das einzige Netz außer EE, das in diesem Zyklus etwas gewann.

### Three besitzt das rohe britische 5G-Geschwindigkeit

Three holte das 5G-Download-Geschwindigkeit mit 187 Mbit/s und das 5G-Upload-Geschwindigkeit mit 20,2 Mbit/s.

### Vodafone gewann nichts allein

Vodafone holte im selben Bericht keine alleinige Auszeichnung, was man wissen sollte, bevor man einen Aufpreis dafür zahlt. Es hat sich inzwischen mit Three fusioniert, die Form des Marktes ändert sich also unter den Marken.

Die beiden Spalten sind kein einziges Urteil. Die eine stammt aus Crowdsourcing-Nutzermessungen, die andere aus kontrollierten Fahrtests mit kalibrierter Ausrüstung. Die zweite kommt dem näher, wie sich ein Roadtrip tatsächlich anfühlt, weshalb die beiden darüber uneinig sein können, wie groß EEs Vorsprung wirklich ist. Keine von beiden sagt deine eigenen Geschwindigkeiten voraus, denn Auslastung und dein Gerät zählen beide.

## Abdeckung in Schottland Wales und Nordirland

Das Vereinigte Königreich ist kompakt, aber seine Abdeckung ist nicht gleichmäßig, und das Muster zählt für alle, die über Englands Städte hinaus reisen.

| | Was dich erwartet | Welches Netz |
|---|---|---|
| London und die großen englischen Städte | Schnelles 5G auf allen vier Netzen | Egal |
| Das englische Land und die Küste | Gutes 4G, wachsendes 5G | EE oder O2 |
| Die schottischen Highlands und Inseln | Abdeckung in Städten und entlang der Hauptrouten, Lücken dazwischen | EE |
| Ländliches Wales und die walisischen Täler | In Städten solide, dazwischen dünner | EE |
| Nordirland | Gute Abdeckung, mit Grenzeffekten nahe der Republik | EE oder O2 |

Die beständige Antwort abseits der Städte ist EE, weshalb die Netz-Frage im Vereinigten Königreich eine einfachere Antwort hat als in den meisten Reisezielen. Das eine, worauf du achten solltest, ist die irische Grenze, wo Telefone in Grenzcountys auf ein Netz der Republik Irland abdriften können — bei einem reinen britischen Tarif bedeutet das entweder keinen Dienst oder eine unerwartete Rechnung.

Die 3G-Netze des Vereinigten Königreichs sind weitgehend abgeschaltet, wobei Vodafone, EE und Three ihre Abschaltungen abgeschlossen haben und O2 Anfang 2026 fertig wurde. Alle vier planen, 2G bis 2033 außer Betrieb zu nehmen, die Richtung ist also einseitig. Ein 4G- oder 5G-Gerät mit VoLTE ist nicht betroffen. Eine eSIM ist ein Profil, das dein Telefon herunterlädt, statt einer Karte, die es annimmt — ein Standard, den die [GSMA](https://www.gsma.com/esim/) pflegt —, und sie nutzt die Netztechnik, die dein Gerät unterstützt. Der Ratgeber [Ist dein Telefon kompatibel](/de/guides/esim-compatibility-check/) bestätigt das Modell.

## 5G im Vereinigten Königreich und was du vor dem Kauf prüfen solltest

Alle vier Netze betreiben kommerzielles 5G und jedes britische Betreiberprofil, das wir erfassen, listet es, das Vereinigte Königreich hat also keine reine 4G-Option und 5G ist keinen Aufpreis wert. Was sich unterscheidet, ist das, was die Schlagzeilenzahl beschreibt. Threes 187 Mbit/s sind eine rohe 5G-Download-Zahl, während EEs Auszeichnungszahl eine beständige Erfahrung über jede Kategorie und jede Technik widerspiegelt.

Diese Unterscheidung solltest du in den Kauf mitnehmen. Ein Tarif, der auf Three fährt, mag die schnellste 5G-Zahl liefern und außerhalb der Städte doch ein schwächeres Erlebnis bieten, und ein Tarif, der auf EE fährt, wird eine niedrigere Schlagzeilengeschwindigkeit melden und in mehr Orten zuverlässiger eine nutzbare Verbindung halten.

Praktisch ist die Abdeckung im Vereinigten Königreich gut genug, dass für die meisten Reisen der Tarif mehr zählt als das Netz. Unsere [Rangliste der eSIM-Tarife für das Vereinigte Königreich](/de/compare/united-kingdom/) sortiert jeden Tarif, den wir erfassen, nach Preis pro Gigabyte und pro Tag, der [Datenkontingent-Rechner](/de/tools/) dimensioniert ein Kontingent auf deine Reisedaten, und aktuelle Rabatte stehen in den [eSIM-Rabattcodes](/de/esim-deals/), die wir aktuell halten.

Zwei Schlussprüfungen. Das Spektrum wird im Vereinigten Königreich von Ofcom lizenziert, und die genutzten Bänder unterscheiden sich von denen Nordamerikas, ein importiertes Gerät lohnt also der Prüfung vor der Reise. Britische SIMs kommen außerdem ohne Fair-Use-Garantie für europäische Reisen, was die praktische Folge des Verlassens des EU-Roaming-Rahmens ist.
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
