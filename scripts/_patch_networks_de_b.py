#!/usr/bin/env python3
"""批 B：`content/de/networks/{mexico,netherlands,south-korea}.md` 德语正文（通用断言）。

结构 = 与 en 侧**逐字段对齐**。断言（每篇都跑）：
  1 front matter 字段集/顺序一致，德语侧允许唯一多出 `noindex`（分层发布）
  2 正文 h2/h3 条数与层级一一对应
  3 德语 h2/h3 禁 `,` `;` `:`（check_headings 的 RELAXED；`—`/`–` 允许）
  4 站内链必须 `/de/` 前缀（外链裸写，禁过 lang-href）
  5 单位禁 `Mbps`/`Kbps`/`Gbps`（全站口径 `Mbit/s`）
  6 短代码 `{{< count-providers >}}` 保留
德语纪律：人称 `du`；术语 Tarif / Anbieter / Heimatnetz / Kontingent / Fair-Use。
用法：python -X utf8 scripts/_patch_networks_de_b.py [--dry] [--only SLUG]
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
# mexico
# ═════════════════════════════════════════════════════════════════════════════
DOCS["mexico"] = '''---
title: "Mexiko Reise-eSIM Netze: Telcel, AT&T Mexico und Movistar erklärt"
description: "Mexiko registriert inzwischen jede im Land verkaufte Mobilfunkleitung, aber einreisende Reise-eSIMs sind ausgenommen. Wie Telcel, AT&T und Movistar abschneiden."
date: 2026-10-03
lastmod: 2026-10-03
iso: "MX"
noindex: true
# TODO(de)：分层发布 —— 全站德语译文解禁（D9 那一轮）时删掉上面这行。
seo:
  title: "Mexiko Reise-eSIM Netze 2026: Beste 5G-Abdeckung"
kicker: "Mexiko hat im Januar 2026 seine Regeln geändert. Jede im Land verkaufte Mobilfunkleitung muss jetzt auf einen identifizierten Nutzer registriert werden, und eine nicht registrierte Leitung wird abgeschaltet. Die Ausnahme für einreisende Reise-eSIMs ist der Grund, warum dies einer der klarsten Fälle für einen Kauf vor dem Flug ist."
h2_carriers: "Die drei mexikanischen Netze einer Reise-eSIM"
h2_scoreboard: "Telcel AT&T und Movistar im unabhängigen Test"
h2_brands: "Das mexikanische Heimatnetz je eSIM-Marke"
h2_cities: "Mexikanische Städte und Resorts mit starker Abdeckung"
h2_next: "Eine Mexiko-eSIM für deine Reise kaufen"
h2_answer: "Was eine Mexiko-Reise-eSIM Besuchern erspart"
h2_facts: "Fakten zum eSIM-Netz in Mexiko"
prompt_answer: "Mexiko betreibt drei nationale Netze — Telcel, AT&T Mexico und Movistar — und jede Reise-eSIM-Marke, die wir erfassen, fährt auf allen dreien. Telcel ist am schnellsten und reicht am weitesten, und sein 5G-Download liegt mehr als dreimal so hoch wie der der Konkurrenz. Seit dem 9. Januar 2026 muss jede in Mexiko verkaufte Mobilfunkleitung auf einen identifizierten Nutzer registriert werden, aber eine Reise-eSIM für Touristen ist ausgenommen, weil sie im Ausland ausgegeben wird."
fact_registration: "In Mexiko gekaufte Leitungen müssen registriert werden. Einreisende Reise-eSIMs sind ausgenommen."
intro_carriers: "Eine mexikanische Reise-eSIM fährt auf Kapazität, die bei Telcel, AT&T Mexico oder Movistar gekauft wurde. Die Marke besitzt die Masten nicht, die Netzbetreiber-Identität des Tarifs entscheidet also über deine Reichweite außerhalb der Städte und Resortgebiete. Jede Marke ist hier faktisch ein MVNO, der entscheidende Netzbetreiber ist also der im Tarif genannte und nicht das verkaufende Unternehmen."
intro_brands: "Jede Marke unten nennt dieselben drei mexikanischen Netzbetreiber als Heimatnetz, die Markenwahl kann deine Abdeckung also nicht ändern. Was sie ändern kann, ist ob Telcel in dem Tarif auftaucht, den du kaufst, und genau das ist die nützlichste Zeile der Tabelle."
cities_note: "Mexiko-Stadt, Cancún, Guadalajara und Monterrey haben alle schnelle Abdeckung, und in den Resortkorridoren leisten die drei Netzbetreiber ähnlich viel. Telcels Vorsprung auf dieser Seite ist eine landesweite Messung, und es ist die Reichweite, die eine Mexikoreise entscheidet, sobald du eine Stadt oder einen Resortstreifen verlässt."
cities_detail:
  - name: "Mexiko-Stadt"
    reality: "Mexiko-Stadt ist auf allen drei Netzbetreibern erschlossen, mit dichter Abdeckung im ganzen Tal, und die Frage beginnt auf den Fahrten hinaus in die umliegenden Bundesstaaten."
  - name: "Cancún"
    reality: "Cancún ist auf allen drei Netzbetreibern in der Hotelzone erschlossen, und die Abdeckung hält nach Süden die Riviera Maya hinunter bis Tulum, bevor sie auf den Inlandsstraßen dünner wird."
  - name: "Guadalajara"
    reality: "Guadalajara ist auf allen drei Netzbetreibern erschlossen, und die Abdeckung läuft westwärts weiter zur Küste von Puerto Vallarta, wo die Bergstraße der erste Abschnitt ist, der sie auf die Probe stellt."
  - name: "Monterrey"
    reality: "Monterrey ist auf allen drei Netzbetreibern erschlossen, und nördlich der Stadt sind die Wüstenautobahnen Richtung US-Grenze der Ort, an dem Telcels größerer Fußabdruck zum Grund wird, sich zu kümmern."
faq_heading: "Fragen zu Mexiko-eSIM und Netz"
faqs:
  - q: "Muss ich meine eSIM in Mexiko registrieren?"
    a: "Wenn du eine mexikanische SIM oder Leitung in Mexiko kaufst, ja. Seit dem 9. Januar 2026 muss jede Mobilfunkleitung des Landes, ob Prepaid oder Postpaid, auf einen identifizierten Nutzer registriert werden, und ausländische Besucher registrieren mit einem gültigen Reisepass statt mit einer mexikanischen Steuernummer. Eine nicht registrierte Leitung wird abgeschaltet und behält nur Notrufe. Reise-eSIMs, die bei einem internationalen Anbieter gekauft werden, stehen ganz außerhalb der Regel, weil die Leitung im Ausland ausgegeben wird und als einreisendes Roaming in Mexiko ankommt."
  - q: "Welches mexikanische Netz ist am besten?"
    a: "Telcel. Es räumte im Opensignal-Bericht vom Oktober 2025 alle vier Geschwindigkeitsauszeichnungen ab, mit Download Speed von 46,0 Mbit/s gegen 27,2 von AT&T und einem 5G-Download von 180,7 Mbit/s, mehr als dreimal so viel wie die Konkurrenz. Es hielt außerdem Zuverlässigkeit bei 863 von 1000, 96 Punkte vor AT&T, und gewann Coverage Experience. Ookla kürte es zudem zum besten Mobilfunknetz Mexikos. Für alles außerhalb der Großstädte und Resorts ist Telcel die sichere Antwort."
  - q: "Ist 5G mit einer Mexiko-eSIM verfügbar?"
    a: "Ja, und es ist konzentriert. Telcels 5G-Download lag im Opensignal-Test vom Oktober 2025 bei durchschnittlich 180,7 Mbit/s, aber der Fußabdruck folgt den Großstädten und den Resortkorridoren statt dem ganzen Land. Alle drei Netzbetreiber, die wir erfassen, listen 5G, die 5G-Verfügbarkeit ist also kein Unterscheidungsmerkmal zwischen Marken — wohin du fährst schon."
  - q: "Funktioniert eine Mexiko-eSIM in den USA oder Kanada?"
    a: "Nicht mit einem reinen Mexiko-Tarif. Er ist für mexikanische Netze bereitgestellt und endet an der Grenze. Wenn deine Reise in die USA führt, kaufe einen Nordamerika- oder Regionaltarif und prüfe die Länderliste vor der Zahlung. Es gibt keine kontinentale Freiroaming-Regelung in Nordamerika."
  - q: "Welches Netz nutzt Movistar in Mexiko?"
    a: "Movistar betreibt landesweit kein eigenes vollständiges Funknetz, sein Verkehr hängt also von der Infrastruktur eines anderen Netzbetreibers statt von eigenen Masten ab. Deshalb taucht es nicht in den Auszeichnungstabellen neben Telcel und AT&T auf, und deshalb behandelt man es am besten als günstige Stadtoption statt als Alternative für Reisen aufs Land."
  - q: "Gibt es unbegrenzte Daten mit einer Mexiko-eSIM?"
    a: "Ja. Einige der Marken, die wir erfassen, verkaufen Mexiko-Tarife mit unbegrenzten Daten neben den Datentarifen mit festem Kontingent, und beide erscheinen im selben Vergleich. Unbegrenzte Reisetarife drosseln die Geschwindigkeit nach einem Tageskontingent meist, statt deine Daten zu stoppen, und genau diese Zahl lohnt sich zu prüfen, bevor du für eine mehr zahlst."
  - q: "Ist eine Mexiko-eSIM günstiger als ein lokaler Prepaid-Tarif?"
    a: "Meist ja, und seit Januar 2026 kippen die Regeln das noch weiter. Eine mexikanische Prepaid-Leitung muss auf einen identifizierten Nutzer registriert werden und wird abgeschaltet wenn nicht, was auf einer kurzen Reise ein echtes Risiko ist. Eine Reise-eSIM kostet einen festen Preis, braucht keine Registrierung und kommt als einreisendes Roaming an, bleibt also ganz außerhalb der Regel."
  - q: "Wie viele Daten verbraucht eine Mexikoreise?"
    a: "Eine Woche Karten, Nachrichten und Foto-Uploads bleibt für die meisten Besucher unter 5 GB, und zwei Wochen derselben Nutzung passen meist in 10 GB. Video-Streaming und Hotspot-Tethering sind das, was einen Datentarif sprengt. Unser Reisedatenrechner dimensioniert ein Kontingent nach App-Nutzung, bevor du dich entscheidest, und das ist der einfachste Weg, den Wert eines Tarifs gegen einen anderen abzuwägen."
---

## Wie sich die mexikanische Registrierungspflicht für Leitungen auf Besucher auswirkt

Hier beginnt man, denn diese Regel erwischt Reisende, die nicht nachgesehen haben. Seit dem 9. Januar 2026 muss jede Mobilfunkleitung in Mexiko auf einen identifizierten Nutzer registriert werden. Sie deckt Prepaid und Postpaid gleichermaßen ab, bei jedem Netzbetreiber, und sie gilt für im Land gekaufte Leitungen. Ausländische Besucher registrieren mit einem gültigen Reisepass — keine mexikanische Steuernummer nötig — und eine nicht registrierte Leitung wird abgeschaltet und behält nur Notrufe. Die Aufsichtsbehörde, die den Markt überwacht, ist die [IFT](https://www.ift.org.mx/).

Interessant wird es beim Geltungsbereich. Die Regel zielt auf Leitungen, die mexikanische Netzbetreiber ausgeben. Eine bei einem internationalen Anbieter gekaufte Reise-eSIM wird im Ausland ausgegeben und kommt als einreisendes Roaming in Mexiko an, was sie ganz außerhalb des Registrierungsverfahrens stellt. Das ist kein Schlupfloch in irgendeinem sinnvollen Sinne — so ist die Regel geschrieben — aber es heißt, dass sich die Papierfrage von selbst beantwortet, wenn du vor dem Flug kaufst.

Der übrige mexikanische Markt ist ungewöhnlich konzentriert, und das prägt alles andere auf dieser Seite.

## Warum Telcel den mexikanischen Markt dominiert

Telcel ist nicht eines von drei vergleichbaren Netzen. Es ist das Netz, und die Messungen sagen das ohne Zurückhaltung.

Opensignals Bericht vom Oktober 2025 zeigt Telcel, das alle vier Geschwindigkeitsauszeichnungen abräumt, mit Download Speed Experience von 46,0 Mbit/s gegen 27,2 Mbit/s von AT&T und einem 5G-Download von 180,7 Mbit/s — mehr als dreimal so viel wie die Konkurrenz. Es hielt außerdem Reliability Experience bei 863 Punkten von 1000, 96 Punkte vor AT&T, und gewann Coverage Experience. Ookla kürte es zudem zum besten Mobilfunknetz Mexikos für das zweite Halbjahr 2025, mit einem Median-5G-Download von 212,68 Mbit/s.

Diese Dominanz hat eine praktische Gestalt. In Mexiko-Stadt, Guadalajara, Monterrey und Cancún leisten alle drei Netzbetreiber viel, und der Unterschied ist eine Frage des Grades. Außerhalb von ihnen — in kleineren Städten, auf den Straßen zwischen den Städten und überall im Inland abseits eines Resortkorridors — ist Telcels Fußabdruck der Unterschied zwischen einem funktionierenden Telefon und gar keinem. Deshalb zählt die Netzbetreiber-Identität deines Tarifs in Mexiko mehr als an den meisten Reisezielen.

{{< count-providers >}} Reise-eSIM-Marken, die wir erfassen, fahren alle auf denselben drei Netzbetreibern, die Marke kann das also nicht ändern. Was du prüfen kannst, ist dass der Tarif, den du kaufst, Telcel listet, was die Tabelle unten für jeden Anbieter zeigt.

## Warum die Lücke zwischen Telcel AT&T und Movistar so weit ist

Die Lücke zwischen Telcel auf Platz eins und Movistar auf Platz drei ist die weiteste jedes Marktes in unserer Netzlandkarte.

### Telcel ist überall der mexikanische Maßstab

Telcel ist am besten bei Geschwindigkeit, Zuverlässigkeit und Abdeckungsbreite. Wenn deine Route irgendetwas jenseits einer Großstadt oder eines Resorts enthält, ist das die Antwort.

### AT&T Mexico ist das Stadtnetz

AT&T gewann im selben Opensignal-Zyklus die Auszeichnung für Verfügbarkeit, hält also in den Gebieten, die es abdeckt, länger eine Verbindung als seine Rivalen. In Mexiko-Stadt und Monterrey ist es wirklich konkurrenzfähig. Auf den Strecken zwischen den Städten nicht.

### Movistar ist Mexikos Preisoption

Movistar ist eine Budgetoption, die auf der Infrastruktur eines anderen Netzbetreibers statt auf eigenen Masten läuft, weshalb es nicht in den Auszeichnungstabellen neben den beiden anderen auftaucht. Es funktioniert als günstige Stadtwahl und ist nicht die Wahl für eine längere Reise.

Die beiden Spalten stammen aus unterschiedlichen Arten der Messung und sollten nie voneinander abgezogen werden. Sie sagen dir, welchen Netzbetreiber jede Quelle als am stärksten sah und in welcher Kategorie, nicht was dein Telefon einbuchen wird. Deine eigene Geschwindigkeit hängt außerdem von Auslastung, deinem Gerät und den Bändern ab, die es unterstützt.

## Wo die mexikanische Abdeckung außerhalb der Resortkorridore dünner wird

Mexikos Tourismusgeografie ist weit gestreut, was die Abdeckungsplanung zu einem Teil der Reiseplanung macht.

| | Was zu erwarten ist | Welches Netz zählt |
|---|---|---|
| Mexiko-Stadt, Guadalajara, Monterrey | Schnelles 5G auf allen drei Netzen | Egal |
| Cancún, Playa del Carmen, Los Cabos, Puerto Vallarta | Gute Abdeckung entlang der Resortkorridore | Egal, mit Telcel vorn im Inland |
| Kolonialstädte und kleinere Orte | Solides 4G, dünneres 5G | Telcel |
| Die Straßen dazwischen | Lange Abschnitte, in denen die Abdeckung stark dünner wird | Telcel |
| Ländliche Inlandsgebiete abseits der Hauptrouten | Bestenfalls lückenhaft, manchmal gar nicht | Telcel oder Offline-Karten |

Die Faustregel ist, dass der Netzbetreiber unter deinem Tarif umso mehr zählt, je weiter sich deine Reise von einem Resortkorridor oder einer Großstadt entfernt. Da jede Marke, die wir erfassen, Telcel bietet, geht es bei dieser Prüfung um die Tarifangabe und nicht darum, bei welchem Unternehmen du kaufst. Lade für jede lange Fahrt trotzdem Offline-Karten herunter, denn selbst Telcel hat Lücken.

Nur AT&T Mexico hat bisher sein 3G-Netz abgeschaltet, Movistar folgt, während Telcel in Teilen des Landes noch 3G betreibt. Bring ein 4G- oder 5G-Gerät mit VoLTE mit, dann stellt sich die Frage nicht. Eine eSIM ist ein Profil, das dein Telefon herunterlädt, statt eine physische Karte, ein von der [GSMA](https://www.gsma.com/esim/) gepflegter Standard, und sie läuft auf welchen Bändern dein Gerät auch unterstützt. Die [Kompatibilitätsprüfung](/de/guides/esim-compatibility-check/) deckt konkrete Modelle ab.

## Wohin mexikanisches 5G reicht und was du an deinem Datentarif prüfen solltest

Alle drei mexikanischen Netzbetreiber, die wir erfassen, listen 5G, die Technologie ist auf Markenebene also kein Unterscheidungsmerkmal. Was sich unterscheidet, ist wo es existiert.

Telcels 5G lag im Opensignal-Test vom Oktober 2025 bei durchschnittlich 180,7 Mbit/s, das ist echter Durchsatz statt ein Marketing-Etikett. Der Fußabdruck folgt den Großstädten, den wichtigsten Resortkorridoren und den Geschäftsvierteln. Verlässt du diese Routen, fällt das Telefon auf 4G zurück, was in Mexiko noch schnell genug für Karten, Nachrichten und Streaming ist.

Das macht 5G hier zu einem schlechten Grund, mehr zu zahlen, und Abdeckung zu einem guten Grund, sorgfältig zu wählen. Die nützlichen Prüfungen vor dem Kauf sind, ob der Tarif Telcel listet, ob er die Regionen deiner Route abdeckt und ob das Kontingent zur Reiselänge passt. Unser [Vergleich der Mexiko-eSIM-Tarife](/de/compare/mexico/) ordnet sie nach Preis pro Gigabyte und pro Tag, der [Verbrauchsrechner](/de/tools/) dimensioniert ein Kontingent zu deiner Route, und aktuelle Rabatte stehen in den [eSIM-Angeboten dieses Monats](/de/esim-deals/).

Wenn deine Reise auch in die USA führt, stehen die Netzbetreiberdetails auf jener Seite auf unserer Seite zu den [USA-eSIM-Netzen](/de/networks/united-states/), und ein Nordamerika-Tarif ist der richtige Kauf statt zwei Einzelnetz-Tarife.

Drei Schlusshinweise. Das mexikanische Spektrum wird landesweit in Bändern lizenziert, die nicht zu jedem importierten Gerät passen, prüfe dein Gerät also, bevor du dich auf 5G verlässt. Fair-Use-Grenzen und Hotspot-Regeln variieren je Anbieter, selbst wenn das Netz darunter identisch ist. Und Upload-Durchsatz zählt, wenn du unterwegs posten willst, und genau dann geht ein kleines Kontingent am schnellsten aus.
'''


# ═════════════════════════════════════════════════════════════════════════════
# netherlands
# ═════════════════════════════════════════════════════════════════════════════
DOCS["netherlands"] = '''---
title: "Niederlande Reise-eSIM Netze: KPN, Vodafone und Odido erklärt"
description: "Die Niederlande haben nahezu vollständige Abdeckung, drei Netze und keine allgemeine SIM-Registrierungspflicht. Wie KPN, Vodafone und Odido für eine eSIM abschneiden."
date: 2026-10-03
lastmod: 2026-10-03
iso: "NL"
noindex: true
# TODO(de)：分层发布 —— 全站德语译文解禁（D9 那一轮）时删掉上面这行。
seo:
  title: "Niederlande Reise-eSIM Netze 2026: Beste 5G-Abdeckung"
kicker: "Die Niederlande sind der kleinste Markt in unserer Netzlandkarte, der von Ende zu Ende gemessen wird, und sie verhalten sich wie eine Stadt statt wie ein Land. Die Abdeckung ist praktisch total, alle Reise-eSIM-Marken, die wir erfassen, fahren auf denselben drei Netzen, und das Schwierigste am Kauf lokaler Daten ist, dass Prepaid-eSIM kaum existiert."
h2_carriers: "Die drei niederländischen Netze einer Reise-eSIM"
h2_scoreboard: "Odido KPN und Vodafone im unabhängigen Test"
h2_brands: "Das niederländische Heimatnetz je eSIM-Marke"
h2_cities: "Niederländische Städte von jedem Netz identisch abgedeckt"
h2_next: "Deine Niederlande-eSIM kaufen"
h2_answer: "Was eine Niederlande-Reise-eSIM löst"
h2_facts: "Fakten zum eSIM-Netz in den Niederlanden"
prompt_answer: "Die Niederlande betreiben drei nationale 5G-Netze — KPN, Vodafone und Odido — und jede Reise-eSIM-Marke, die wir erfassen, fährt auf allen dreien, mit einer Abdeckung, die landesweit nahezu total ist. Odido, früher T-Mobile Niederlande, führt bei der Download-Geschwindigkeit, während KPN bei Abdeckung und Sprachqualität antwortet. Es gibt keine allgemeine SIM-Registrierungspflicht, aber niederländische Netzbetreiber verkaufen eSIM überwiegend mit Verträgen, eine Reise-eSIM für Touristen ist also meist die einzige Prepaid-eSIM-Option."
fact_registration: "Keine allgemeine Registrierungspflicht. Prepaid-eSIM ist bei lokalen Netzbetreibern selten."
intro_carriers: "Niederländische Reise-eSIM-Daten werden im Großhandel bei KPN, Vodafone oder Odido gekauft. Die Marke auf deinem Tarif betreibt das Funknetz nicht, deine Abdeckung wird also vom Reiseziel statt vom Unternehmen bestimmt, bei dem du kaufst. Jede Marke unten ist faktisch ein MVNO niederländischer Netze, weshalb keine eine Abdeckung bieten kann, die die anderen nicht bieten."
intro_brands: "Alle drei niederländischen Netzbetreiber erscheinen als Heimatnetz für jede Marke unten, was diese Tabelle zu einer Preisliste statt zu einem Abdeckungsvergleich macht. In den Niederlanden ist das keine Vereinfachung — die Netze decken das Land wirklich auf demselben Niveau ab."
cities_note: "Die Niederlande sind klein und dicht bebaut, und Amsterdam, Rotterdam und Den Haag liegen bei nahezu identischer Abdeckung eine Stunde voneinander entfernt. Alle drei Netze sind nah genug beieinander, dass die niederländische Netz-Frage sehr wenig Gewicht trägt, selbst an der Küste und draußen in den Blumenfeldern."
cities_detail:
  - name: "Amsterdam"
    reality: "Amsterdam ist auf allen drei Netzen erschlossen, und die Abdeckung hält westwärts bis zur Küste bei Zandvoort und hinaus durch die Blumenfelder rund um Lisse."
  - name: "Rotterdam"
    reality: "Rotterdam ist auf allen drei Netzen erschlossen, und die Abdeckung läuft nach Süden durch das Delta Richtung Zeeland ohne nennenswerte Unterbrechung weiter."
  - name: "Den Haag"
    reality: "Den Haag ist auf allen drei Netzen erschlossen, und das Seebad Scheveningen ist genauso gut abgedeckt wie das Stadtzentrum."
faq_heading: "Fragen zu Niederlande-eSIM und Netz"
faqs:
  - q: "Welches niederländische Netz ist am schnellsten?"
    a: "Odido. Opensignals Bericht vom März 2026 setzte es bei Download Speed Experience mit 146,4 Mbit/s an die Spitze, vor KPN mit 101,2 und Vodafone mit 92,9, und es führte auch die Kategorien Video und Games an. Ookla machte es zudem zum schnellsten Mobilfunkanbieter über alle Technologien im ersten Halbjahr 2025, mit einem Median-Download von 216,3 Mbit/s. KPN antwortet bei Abdeckung und Sprachqualität statt bei roher Geschwindigkeit."
  - q: "Ist Odido dasselbe wie T-Mobile Niederlande?"
    a: "Ja, der Sache nach. Odido ist die Neumarke von T-Mobile Niederlande nach der Fusion mit Tele2, und beide Namen wurden am 5. September 2023 zu Odido. Tarife, die vor diesem Datum gebaut wurden, können in ihren Bedingungen noch T-Mobile oder Tele2 nennen. Es ist dasselbe Netz und derselbe Betreiber unter einer neuen Marke."
  - q: "Brauche ich in den Niederlanden einen Ausweis für eine SIM?"
    a: "Keine allgemeine Pflicht, und das macht die Niederlande an diesem Punkt einfacher als Deutschland, Spanien oder Belgien. Das niederländische Recht schreibt keine Prepaid-SIM-Registrierung vor, einzelne Händler fragen manchmal aus eigener Ladenpolitik nach einem Reisepass. Trage deinen Reisepass vorsichtshalber mit, aber erwarte einen unkomplizierten Kauf. Eine Reise-eSIM braucht überhaupt keine Identifikation."
  - q: "Kann ich eine Prepaid-eSIM bei einem niederländischen Netzbetreiber kaufen?"
    a: "Selten, und das ist der praktische Haken. Niederländische Netzbetreiber bieten eSIM überwiegend im Abo statt als Prepaid-Produkt an, ein Besucher, der eine eSIM ohne Vertrag will, muss sie also meist bei einem internationalen Reise-eSIM-Anbieter statt bei einem lokalen Netz kaufen. Das kehrt die übliche Empfehlung um, denn an den meisten Reisezielen ist eine lokale Prepaid-Option die günstigere Rückfalllösung."
  - q: "Kann ich eine Niederlande-eSIM in Belgien oder Deutschland nutzen?"
    a: "Eine reine Niederlande-eSIM endet an der Grenze, was hier besonders sorgfältig zu prüfen ist, weil die Grenzen nah und mit dem Zug leicht zu überqueren sind. Vor Ort gekaufte niederländische SIM-Karten enthalten europäisches Freiroaming, aber dieses Recht hängt an der lokalen SIM und nicht an einem niederlandespezifischen Reisetarif. Kaufe für eine Mehrländerroute einen Europa-Tarif und bestätige die Länderliste vor der Zahlung."
  - q: "Gibt es unbegrenzte Daten mit einer Niederlande-eSIM?"
    a: "Ja. Einige der Marken, die wir erfassen, verkaufen Niederlande-Tarife mit unbegrenzten Daten neben den Datentarifen mit festem Kontingent, und beide liegen im selben Vergleich. Das Land ist klein und die drei Netze decken es fast vollständig ab, ein bescheidenes festes Kontingent ist also oft mehr wert als unbegrenzt, außer du streamst oder teatherst jeden Tag. Das Profil kommt innerhalb von Minuten nach der Zahlung, und genau diese sofortige Aktivierung macht eine eSIM zur praktischen Wahl für spät gebuchte Reisen."
  - q: "Ist eine Niederlande-eSIM mehr wert als eine lokale Prepaid-SIM?"
    a: "Sie ist oft die einzige Prepaid-eSIM-Option. Niederländische Netzbetreiber verkaufen eSIM überwiegend mit Verträgen statt als Prepaid-Produkte, ein Besucher, der eine eSIM ohne Abo will, muss also meist bei einem internationalen Reise-eSIM-Anbieter kaufen. Ein Reisender, der eine physische Prepaid-SIM am Ladentisch nimmt, hat mehr lokale Auswahl."
  - q: "Überquert eine Niederlande-eSIM die Benelux ohne Roaminggebühren?"
    a: "Eine reine Niederlande-eSIM endet an der Grenze, und die Grenzen hier sind nah genug, um sie mit dem Zug in unter einer Stunde zu überqueren. Freies Roaming in der Benelux gehört zu vor Ort gekauften niederländischen SIM-Karten und nicht zu einem niederlandespezifischen Reisetarif, eine Mehrländerroute braucht also einen Europa-Tarif mit Belgien und Deutschland auf der Länderliste."
---

## Warum die Niederlande fast kein Abdeckungsproblem haben

Die meisten Reiseziele auf dieser Seite haben eine Abdeckungsfrage. Die Niederlande kaum. Das Land ist klein, dicht besiedelt und flach, die drei nationalen Netze decken es alle stark ab, und die praktischen Lücken, die es anderswo in Europa gibt — Bergtäler, lange leere Landstriche, abgelegene Inseln — fehlen weitgehend.

Das ändert die Gestalt der Kaufentscheidung. Für eine Reise, die im Land bleibt, gibt es keine sinnvolle Frage danach, welches Netz die Orte erreicht, an die du fährst. Die verbleibenden Variablen sind Geschwindigkeit, Preis und eine regulatorische Eigenheit mit echten Folgen. Die niederländische Aufsichtsbehörde für die digitale Infrastruktur ist die [RDI](https://www.rdi.nl/), die den Markt überwacht.

Alle {{< count-providers >}} Reise-eSIM-Marken, die wir erfassen, verbinden sich mit denselben drei Netzen — KPN, Vodafone und Odido — was die Markentabelle unten Zeile für Zeile zeigt. Kein Anbieter kann dir bessere niederländische Abdeckung verkaufen als ein anderer, die Marke entscheidet also die Rechnung und nichts sonst. Unser [Vergleich der Niederlande-eSIM-Tarife](/de/compare/netherlands/) ordnet sie auf dieser Basis.

## Odido ist die Neumarke von T-Mobile Niederlande

Der Name Odido verdient dreißig Sekunden, weil er Leute verwirrt, die ältere Tarifbedingungen lesen.

Odido ist das, was aus T-Mobile Niederlande nach der Fusion mit Tele2 wurde. Beide Marken nahmen den Namen Odido am 5. September 2023 an. Hinter dem Namen versteckt sich kein viertes Netz — es ist derselbe Betreiber mit drei Generationen von Branding, und Reisetarife, die vor der Änderung verkauft wurden, können in der Tarifbeschreibung noch T-Mobile oder Tele2 sagen.

Das zählt, weil Odido auch das schnellste der drei Netze ist, ein Tarif mit dem älteren Namen ist also kein älteres oder geringeres Produkt. Es ist derselbe Netzbetreiber, der die niederländischen Geschwindigkeitstabellen anführt.

Die anderen beiden sind unkompliziert. KPN ist der Incumbent und der Abdeckungsmaßstab. Vodafone ist das dritte nationale Netz, am stärksten in den Randstad-Städten, wo die meisten Besucher ihre Zeit verbringen.

## Welches niederländische Netz bei Geschwindigkeit und Abdeckung am besten ist

Die niederländische Aufteilung ist klarer als bei den meisten, mit Odido vorn bei der Geschwindigkeit und KPN vorn bei Abdeckung und Sprachqualität.

### Odido führt beim niederländischen 5G-Geschwindigkeit

Opensignals Bericht vom März 2026 setzte Odido bei Download Speed Experience mit 146,4 Mbit/s an die Spitze, vor KPN mit 101,2 und Vodafone mit 92,9, und es führte auch die Kategorien Video und Games an. Ookla maß zudem einen Median-Download von 216,3 Mbit/s für das erste Halbjahr 2025, was es zum schnellsten Anbieter über alle Technologien machte. Es ist das Netz, in dem du sein willst, wenn Geschwindigkeit Priorität hat.

### KPN führt bei niederländischer Abdeckung und Sprache

KPN gewann Coverage Experience mit 9,4 von 10 und 5G Coverage Experience mit 8,3 und stand bei Voice App Experience mit 83,8 Punkten oben — das Maß, das die Anrufqualität über Apps wie WhatsApp statt über das zellulare Sprachnetz abdeckt. Time on Network wurde zum statistischen Gleichstand, 99,3 % gegen 99,1 % von Odido. Für eine Reise, die über Amsterdam und Rotterdam hinausgeht, ist KPN die sicherere Grundlage.

### Vodafone ist die niederländische dritte Option

Vodafone leistet im Randstad viel und liegt in den Geschwindigkeitstabellen hinter den beiden anderen. Es bleibt ein nationales Netz mit voller Abdeckung des Landes, die Lücke ist also eine des Grades statt der Reichweite.

Lies die beiden Spalten als getrennte Urteile statt als einen kombinierten Wert. Die eine baut auf von Nutzern beigesteuerten Messwerten auf, die andere auf dem Median freiwillig durchgeführter Tests, sie können dieselben drei Netze also unterschiedlich einordnen, ohne dass eine falsch ist. Keine sagt, wie schnell eine Reise-eSIM für dich laufen wird, denn Auslastung und dein Gerät zählen beide.

## Niederländische SIM-Regeln und warum Prepaid-eSIM schwer zu finden ist

Zwei niederländische Regeln prägen, wie du Daten tatsächlich kaufst und registrierst, und die zweite ist ungewöhnlich.

| | Reise-eSIM | Niederländische Prepaid-SIM | Niederländischer Vertrag |
|---|---|---|---|
| Ausweis nötig | Keiner | Nicht per Gesetz, manchmal per Ladenpolitik | Ja, mit BSN und niederländischem Bankkonto |
| eSIM-Verfügbarkeit | Standard | Selten, meist nur im Abo | Ja |
| Funktioniert EU-weit | Nur mit einem Europa-Tarif | Ja, unter Fair-Use-Grenzen | Ja, unter Fair-Use-Grenzen |
| Am besten für | Fast jede kurze Reise | Längere Aufenthalte mit Wunsch nach niederländischer Nummer | Ansässige |

Das Registrierungsbild ist entspannter als in Deutschland, Spanien oder Belgien, wo Prepaid-SIMs gegen ein Dokument registriert werden müssen. Der niederländische Staat verlangt es nicht, einzelne Läden fragen manchmal aus eigener Politik danach, einen Reisepass mitzutragen ist also sinnvoll statt verpflichtend.

Das eSIM-Bild ist das Gegenteil. Niederländische Netzbetreiber bieten eSIM überwiegend im Abo statt als Prepaid an, und ein Abo braucht eine Bürger-Servicenummer und ein niederländisches Bankkonto. Für einen Besucher heißt das praktisch, der eSIM-Weg läuft über einen internationalen Reise-eSIM-Anbieter statt über ein lokales Netz, was das Gegenteil der Empfehlung ist, die in Deutschland oder Thailand funktioniert.

## 5G in den Niederlanden und wie du um ein kleines Land herum planst

Alle drei niederländischen Netze betreiben kommerzielles 5G und jedes niederländische Netzbetreiberprofil, das wir erfassen, listet es, es gibt also keine reine 4G-Option und 5G ist kein Aufpreis, der sich lohnt. Odidos Download von 146,4 Mbit/s und der Ookla-Median von 216,3 Mbit/s spiegeln beide ausgereiftes 5G statt einen laufenden Ausbau wider, und KPNs 5G Coverage Experience von 8,3 von 10 beschreibt, wie breit es tatsächlich verfügbar ist.

Was die Niederlande ungewöhnlich macht, ist wie wenig Geografie es zu planen gibt. Amsterdam, Rotterdam, Den Haag und Utrecht liegen eine Stunde voneinander entfernt und werden von allen drei Netzen identisch abgedeckt. Tagesausflüge an die Küste und in die Blumenfelder sind die einzigen Routen, auf denen die Netz-Frage Substanz hat, und selbst dort sind die Unterschiede klein genug, um sie für eine kurze Reise zu ignorieren.

KPN und Vodafone haben 3G bereits abgeschaltet, und KPN plant, 2G am 1. Dezember 2027 abzuschalten, ein 4G- oder 5G-Gerät mit VoLTE ist also das richtige Gerät zum Mitbringen. Eine eSIM ist ein Profil, das dein Telefon herunterlädt, statt eine Karte, die es annimmt, ein von der [GSMA](https://www.gsma.com/esim/) gepflegter Standard, und sie funktioniert mit welchen Bändern dein Gerät auch abdeckt. Der [Telefon-Kompatibilitäts-Check](/de/guides/esim-compatibility-check/) deckt konkrete Modelle ab.

Wenn deine Route nach Belgien oder Deutschland weitergeht, kaufe einen Europa-Regionaltarif statt eines reinen Niederlande-Tarifs, da beide Grenzen nur eine kurze Zugfahrt entfernt sind. Unsere Seiten zu den [Deutschland-eSIM-Netzen](/de/networks/germany/) und zu [Belgien](/de/compare/belgium/) decken die Netzbetreiber auf der anderen Seite ab. Für eine Reise, die im Land bleibt, listet unsere [Niederlande-Tarifrangliste](/de/compare/netherlands/) jeden Tarif, den wir erfassen, der [Kontingentrechner](/de/tools/) dimensioniert ein Kontingent zu deinen Daten, und aktuelle Rabatte stehen in den [eSIM-Rabattcodes](/de/esim-deals/).

Zwei Schlusshinweise. Das niederländische Spektrum wird landesweit in Bändern lizenziert, die eng mit dem weiteren europäischen Plan übereinstimmen, die meisten europäischen Geräte brauchen also keine Anpassung. Der Upload-Durchsatz folgt demselben Muster ausgereifter Kapazität, was auf einer kurzen Reise wenig zählt und sehr viel, wenn du aus einem Hotelzimmer remote arbeitest.
'''


# ═════════════════════════════════════════════════════════════════════════════
# south-korea
# ═════════════════════════════════════════════════════════════════════════════
DOCS["south-korea"] = '''---
title: "Südkorea Reise-eSIM Netze: SK Telecom, KT und LG U+ erklärt"
description: "Korea betreibt das schnellste 5G in unserer Netzlandkarte, aber Touristentarife sind reine Datentarife. Wie SK Telecom, KT und LG U+ abschneiden und was du tatsächlich kaufen kannst."
date: 2026-10-03
lastmod: 2026-10-03
iso: "KR"
noindex: true
# TODO(de)：分层发布 —— 全站德语译文解禁（D9 那一轮）时删掉上面这行。
seo:
  title: "Südkorea Reise-eSIM Netze 2026: Schnellstes 5G"
kicker: "Südkorea liefert die größten 5G-Zahlen irgendwo in unserer Netzlandkarte, und der Vorsprung vor dem Rest der Welt ist nicht klein. Alle Reise-eSIM-Marken, die wir erfassen, fahren auf denselben drei Netzbetreibern — SK Telecom, KT und LG U+ — die Marke entscheidet also den Preis, während das Netz alles andere entscheidet."
h2_carriers: "Die drei koreanischen Netze einer Reise-eSIM"
h2_scoreboard: "SK Telecom KT und LG U+ im unabhängigen Test"
h2_brands: "Das koreanische Heimatnetz je eSIM-Marke"
h2_cities: "Koreanische Städte mit nahezu vollständiger Abdeckung"
h2_next: "Eine Südkorea-eSIM wählen"
h2_answer: "Was dir eine Südkorea-Reise-eSIM gibt"
h2_facts: "Fakten zum eSIM-Netz in Südkorea"
prompt_answer: "Südkorea betreibt drei nationale 5G-Netze — SK Telecom, KT und LG U+ — und jede Reise-eSIM-Marke, die wir erfassen, fährt auf allen dreien. KT verzeichnet den höchsten 5G-Download in unserer Netzlandkarte mit 486 Mbit/s, SK Telecom hat die weiteste Abdeckung, und LG U+ führt bei der 5G-Verfügbarkeit. Koreanische Leitungen brauchen eine Echtnamenregistrierung und Touristen-eSIMs sind reine Datentarife, eine Reise-eSIM für Touristen ist also der einfachste Weg zu Daten, gibt dir aber keine nutzbare koreanische Nummer."
fact_registration: "Die Echtnamenregistrierung gilt für lokale Leitungen. Reise-eSIMs sind reine Datentarife und brauchen keinen Ausweis."
intro_carriers: "Eine koreanische Reise-eSIM fährt auf Großhandelskapazität von SK Telecom, KT oder LG U+. Die Marke, bei der du kaufst, betreibt die Masten nicht, das Netz deines Tarifs ist also eine Eigenschaft der Vereinbarungen des Tarifs statt des Markennamens. Jeder Anbieter ist der Sache nach ein MVNO koreanischer Netze, die Marke kann also nicht ändern, welche Masten deine Daten überqueren."
intro_brands: "Jede Marke unten fährt auf allen drei koreanischen Netzbetreibern, die Tabelle ist also eine Preisliste. Sie zählt auch aus einem praktischen Grund — koreanische Datentarife reichen weiter als die meisten, und das Kontingent zählt mehr als der Netzbetreiber, der es trägt."
cities_note: "Seoul, Busan und Incheon haben nahezu vollständige 5G-Abdeckung auf allen drei Netzbetreibern, einschließlich der U-Bahn-Tunnel, das Stadtsignal entscheidet einen koreanischen Kauf also nie. Abseits der Großstädte und an der Ostküste ist SK Telecoms größerer Fußabdruck die sicherere Grundlage."
cities_detail:
  - name: "Seoul"
    reality: "Seoul ist auf allen drei Netzbetreibern erschlossen, einschließlich der U-Bahn, und die Abdeckung hält durchgehend den KTX-Korridor Richtung Daejeon und Busan hinunter."
  - name: "Busan"
    reality: "Busan ist auf allen drei Netzbetreibern erschlossen, und die Ostküste nordwärts Richtung Pohang ist der Ort, an dem die drei Fußabdrücke beginnen, sich zu unterscheiden."
  - name: "Incheon"
    reality: "Incheon ist auf allen drei Netzbetreibern erschlossen, einschließlich des Flughafens und der Fährterminals, was die Inselüberfahrten zum ersten Ort macht, an dem die Netz-Frage Gewicht trägt."
faq_heading: "Fragen zu Südkorea-eSIM und Netz"
faqs:
  - q: "Welches koreanische Netz ist am besten?"
    a: "Zwei verschiedene Antworten je nachdem, was du misst, und die Spaltung ist echt. SK Telecom gewann Best Network im Opensignal-Bericht vom Dezember 2025 mit neun Auszeichnungen direkt plus drei geteilten, darunter Download Speed mit 189,3 Mbit/s und Coverage Experience mit 9,4 von 10. KT nahm den 5G Download Speed mit 486,2 Mbit/s, der höchsten 5G-Zahl auf irgendeiner Seite unserer Netzlandkarte. LG U+ gewann 5G Availability mit 90,3 %. Für landesweite Reisen ist SK Telecom die sichere Wahl, für reine Geschwindigkeit hat KT den Vorsprung."
  - q: "Muss ich eine koreanische SIM oder eSIM registrieren?"
    a: "Korea erzwingt die Echtnamenregistrierung für jede Mobilfunkleitung, das heißt die Leitung muss an deine verifizierte rechtliche Identität gebunden sein. Für Touristen ist das ein Reisepass. Prepaid-SIMs können an Schaltern am Flughafen Incheon allein mit einem Reisepass gekauft werden, eine Aufenthaltskarte ist nicht nötig. Eine vor dem Flug gekaufte Reise-eSIM umgeht den Schalter ganz und wird unter der Registrierung des Anbieters statt deiner ausgegeben."
  - q: "Bekomme ich auf einer Touristen-eSIM eine koreanische Telefonnummer?"
    a: "Meist nicht in einer nutzbaren Form. Reise-eSIMs für Korea sind überwiegend reine Datentarife, und selbst die sprachfähigen Touristenprodukte können nicht genutzt werden, um die koreanische Identitätsprüfung für Banken oder Behördendienste zu bestehen. Wenn du für solche Zwecke eine echte koreanische Nummer brauchst, erfordert das eine Aufenthaltskarte und einen lokalen Vertrag statt eines Reiseprodukts."
  - q: "Ist 5G mit einer Südkorea-eSIM verfügbar?"
    a: "Ja, und Korea ist der Markt, in dem 5G sein Versprechen am meisten einlöst. Alle drei Netzbetreiber betreiben kommerzielles 5G und jedes koreanische Netzbetreiberprofil, das wir erfassen, listet es. Opensignal maß KTs 5G-Download im Dezember 2025 bei 486,2 Mbit/s, und Ooklas kontrollierte Testfahrten über den Raum Seoul bis Incheon verzeichneten einen Median-Download von 853,37 Mbit/s beim führenden Netzbetreiber. Das sind keine Zahlen, die du in den meisten Ländern sehen wirst."
  - q: "Funktioniert eine Südkorea-eSIM in Japan oder China?"
    a: "Nicht mit einem reinen Korea-Tarif. Er ist für koreanische Netze bereitgestellt und endet an der Grenze. Wenn deine Reise nach Japan oder China weitergeht, kaufe einen Asien-Regionaltarif und bestätige die Länderliste vor der Zahlung. Alle drei Länder werden in unserer Netzlandkarte als getrennte Märkte geführt, mit eigenen Netzbetreibergruppen."
  - q: "Gibt es unbegrenzte Daten mit einer Südkorea-eSIM?"
    a: "Ja, und es ist das häufigste Produkt auf dieser Route. Die meisten Südkorea-Reisetarife, die wir erfassen, sind reine Datentarife, und unbegrenzte Varianten liegen neben den Datentarifen mit festem Kontingent. Koreanische Netze sind die schnellsten in unserer Netzlandkarte, eine schwere Route aus Video und Uploads ist hier also realistischer als fast überall sonst. Es gibt auch keinen Roaming-Schritt zu arrangieren, weil die eSIM bereitgestellt ankommt statt im Land eingeschaltet zu werden."
  - q: "Ist eine Südkorea-eSIM günstiger als eine lokale Prepaid-SIM?"
    a: "Bei einer kurzen Reise oft ja, und der Papierkram entscheidet es genauso wie der Preis. Eine koreanische Prepaid-Leitung braucht eine Echtnamenregistrierung, was für Besucher einen Reisepass und einen Schalterbesuch am Flughafen bedeutet. Eine Reise-eSIM braucht keine eigene Registrierung und wird vor dem Flug gekauft, sie ist also unter zwei Wochen die einfachere und meist günstigere Option."
  - q: "Ist die Aktivierung bei einer Südkorea-eSIM sofort?"
    a: "Das Profil kommt direkt nach der Zahlung digital an, meist innerhalb von Minuten, und die Leitung geht live, wenn du sie einschaltest, was sofortige Aktivierung in der Praxis bedeutet. Nichts läuft, bevor du sie installierst, wochenlang im Voraus zu kaufen ist also sicher. Eine am Schalter gekaufte SIM arbeitet umgekehrt, weil ihre Uhr am Tresen startet."
---

## Warum koreanische Mobilfunkgeschwindigkeiten wie ein Tippfehler wirken

Südkorea liefert die größten Netzzahlen irgendwo in unserer Netzlandkarte, und der Vorsprung ist nicht marginal. Opensignal maß KTs 5G-Download im Dezember 2025 bei 486,2 Mbit/s. Ooklas kontrollierte Testfahrten über den Raum Seoul bis Incheon verzeichneten einen Median-Download von 853,37 Mbit/s beim führenden Netzbetreiber, wobei alle drei Betreiber im selben Test zwischen 982 und 993 von 1000 Punkten erreichten.

Zum Kontext, die entsprechenden 5G-Zahlen anderswo auf dieser Seite landen im Bereich von 100 bis 280 Mbit/s. Korea operiert in einer anderen Liga, und das ändert, wofür ein Datentarif eigentlich gut ist. Ein Kontingent von 20 GB auf einem koreanischen Netz reicht weiter als dasselbe Kontingent fast überall sonst, weil die Kapazität, es zu liefern, da ist.

Das lohnt sich zu wissen, bevor du kaufst, denn es heißt, der billigste Tarif mit dem kleinsten Kontingent reicht oft. Die Frage ist nicht, ob das Netz mithält. Es ist, wie viele Daten deine Apps durchbringen, und auf koreanischer Infrastruktur ist die Antwort meist weniger, als du erwartest.

## Was Touristen auf einer koreanischen SIM kaufen können und was nicht

Korea erzwingt die Echtnamenregistrierung für jede Mobilfunkleitung, die Identitätsanforderungen sind also streng nach internationalen Maßstäben. Die Regeln liegen beim [Ministerium für Wissenschaft und ICT](https://www.msit.go.kr/eng/), und wo sie für dich landen, hängt ganz davon ab, welches Produkt du kaufst.

| | Reise-eSIM | Prepaid-SIM in Korea | Koreanischer Postpaid-Vertrag |
|---|---|---|---|
| Registrierung | Die des Anbieters, nicht deine | Echtname mit Reisepass | Echtname mit Aufenthaltskarte |
| Wo du sie bekommst | Online, vor dem Flug | Schalter am Flughafen Incheon, Betreiberläden | Nur in Betreiberläden |
| Dokumentation | Keine | Reisepass, keine ARC nötig | Alien Registration Card plus koreanische Zahlungsmethode |
| Typischer Preisbereich | Vom Anbieter festgelegt | Rund 30.000 bis 60.000 Won je nach Dauer | Monatliche Abrechnung |
| Lokale Telefonnummer | In den meisten Fällen nur Daten | Ja | Ja |
| Am besten für | Fast jede kurze Reise | Längere Aufenthalte mit Bedarf an koreanischer Nummer | Ansässige |

Die mittlere Spalte ist die praktische Option für einen Besucher, der eine koreanische Nummer will, und die Flughafenschalter machen sie einigermaßen schmerzlos. Was nicht mehr möglich ist, ist der Abschluss eines monatlichen Postpaid-Vertrags allein mit einem Reisepass — das erfordert eine Alien Registration Card und eine koreanische Zahlungsmethode, was es für einen Touristen außer Reichweite rückt.

Die meisten Reise-eSIMs für Korea sind reine Datentarife, und selbst die sprachfähigen Touristenprodukte können nicht für die koreanische Identitätsprüfung genutzt werden. Wenn deine Reise davon abhängt, unter einer koreanischen Nummer erreichbar zu sein, kaufe am Flughafen. Wenn sie von Daten abhängt, ist eine Reise-eSIM einfacher und günstiger.

## Wo SK Telecom KT und LG U+ jeweils den Vorsprung haben

Opensignal und Ookla sind sich bei Südkorea auf eine Weise uneinig, die wirklich informativ statt widersprüchlich ist.

### SK Telecom ist das beste koreanische Gesamtnetz

Opensignals Bericht vom Dezember 2025 gab SK Telecom neun Auszeichnungen direkt plus drei geteilte und den Titel Best Network, mit Download Speed bei 189,3 Mbit/s — etwa 35 Mbit/s vor KT — und Coverage Experience bei 9,4 von 10, der höchste der drei. Es ist die Wahl für alles außerhalb des Großraums Seoul.

### KT hält den koreanischen 5G-Geschwindigkeitsrekord

KTs 5G Download Speed kam mit einer Zahl von 486,2 Mbit/s, der höchsten auf irgendeiner Seite dieser Netzlandkarte. Im Testlauf Seoul bis Incheon lag es insgesamt auf Platz zwei, und KT ist auch der Netzbetreiber, der am stärksten mit ausländerfreundlichen Tarifprodukten verbunden wird.

### LG U+ ist der koreanische Führer bei 5G-Verfügbarkeit

LG U+ erreichte 90,3 % Verfügbarkeit, das heißt Nutzer mit einem 5G-Gerät erkennen öfter ein 5G-Signal als bei beiden Rivalen. Es stand außerdem bei RootMetrics' Overall RootScore für den Raum Seoul bis Incheon mit 993 von 1000 oben, mit der höchsten Median-Download-Geschwindigkeit im selben Test. Es ist das kleinste der drei landesweit und oft das günstigste.

Alle {{< count-providers >}} Reise-eSIM-Marken, die wir erfassen, fahren auf allen dreien, die Markentabelle unten ist also eine Preisliste statt ein Abdeckungsvergleich.

Lies die beiden Spalten als unabhängige Urteile über dieselben drei Netze, die eine mittelt die von Nutzern beigesteuerte Erfahrung, die andere entsteht durch kalibrierte Testfahrten. Sie können sich uneinig sein, ohne dass eine falsch ist. Sie ordnen dieselben drei Netze getrennt ein, und keine ist ein Versprechen über die Geschwindigkeit, die du persönlich sehen wirst — Auslastung und dein Gerät bewegen die Zahl beide.

## Seoul gegen den Rest von Korea

Korea ist klein, dicht und stark verstädtert, was das Abdeckungsproblem im Vergleich zu den USA oder Kanada zusammendrückt. Trotzdem trennen sich die drei Netze an den Orten, die ein Besucher am ehesten aufsucht.

| | Was zu erwarten ist | Welches Netz |
|---|---|---|
| Seoul und der Großraum, einschließlich U-Bahn-Tunnel | Nahezu vollständige 5G-Abdeckung auf allen dreien | Egal |
| Busan, Incheon, Daegu, Daejeon | Durchgehend schnelles 5G | Egal |
| Jeju-Insel | Rund um die Küste und die Hauptrouten gut abgedeckt | SK Telecom oder KT |
| Die Ostküste und die Bergregionen | Die Abdeckung dünnt abseits der Orte aus | SK Telecom |
| Die entmilitarisierte Zone und Grenzgebiete | Von Natur aus eingeschränkt und unzuverlässig | Verlass dich nicht darauf |

SK Telecoms Coverage-Experience-Wert von 9,4 von 10 ist der Grund, warum es abseits der Städte die sichere Antwort bleibt, und sein Vorsprung in der Seouler U-Bahn ist ein kleinerer aber echter Vorteil, wenn du eine Woche in der Hauptstadt verbringst.

Koreas 2G-Netze wurden vor Jahren geschlossen, 2012 und 2020 je nach Netzbetreiber. Es kommt keine besucherrelevante Abschaltung, um die du planen müsstest. Bring ein 4G- oder 5G-Gerät mit VoLTE-Unterstützung mit, dann bestätigt die [Kompatibilitätsprüfung deines Telefons](/de/guides/esim-compatibility-check/) das Modell. Eine eSIM ist ein Profil, das dein Telefon herunterlädt, statt eine Karte, die du einsetzt, ein von der [GSMA](https://www.gsma.com/esim/) gepflegter Standard, und sie läuft auf welchen Bändern dein Gerät auch abdeckt.

## Einen Südkorea-eSIM-Datentarif dimensionieren

Alle drei koreanischen Netzbetreiber, die wir erfassen, listen 5G, es gibt also keine reine 4G-Option und 5G ist kein Grund, mehr zu zahlen. Ungewöhnlich ist, wie viel die Technologie liefert — KTs 486,2 Mbit/s und der im Test Seoul bis Incheon verzeichnete Median von 853,37 Mbit/s liegen in einer anderen Klasse als die anderswo typischen 100 bis 280 Mbit/s, und deshalb ist Korea der eine Markt auf dieser Seite, in dem ein bescheidenes Kontingent meist ausreicht.

Praktisch sind koreanische Datentarife effektiv großzügig. Navigation, Übersetzung, Streaming und Foto-Uploads laufen alle schneller, und ein Tarif der Mittelklasse über einen normalen Urlaub wird unwahrscheinlich aufgebraucht. Unsere [Rangliste der Südkorea-eSIM-Tarife](/de/compare/south-korea/) sortiert sie nach Preis pro Gigabyte und pro Tag, der [Verbrauchsrechner](/de/tools/) dimensioniert einen zu deinen Daten, und aktuelle Rabatte stehen in den [eSIM-Angeboten, die wir erfassen](/de/esim-deals/).

Wenn deine Reise nach Japan weitergeht, stehen die Netzbetreiberdetails auf jener Seite auf unserer Seite zu den [Japan-eSIM-Netzen](/de/networks/japan/), und ein Asien-Regionaltarif ist meist der günstigere Kauf als zwei Einzelnetz-Tarife.

Zwei Schlusshinweise. Das koreanische Spektrum wird landesweit lizenziert und ist auf Mittelfrequenzbänder konzentriert, ein Gerät, das diese Bänder abdeckt, bekommt also den vollen Nutzen des Netzes. Es gibt auch keine regionale Roaming-Union, die Korea abdeckt, eine hier genutzte Heimat-SIM rechnet also zu internationalen Sätzen ab, und jede Fair-Use-Bedingung eines Tarifs ist lesenswert, bevor du dich darauf verlässt.
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
