#!/usr/bin/env python3
"""批 A：`content/de/networks/{china,france,germany}.md` 德语正文（通用断言）。

结构 = 与 en 侧**逐字段对齐**。断言（每篇都跑）：
  1 front matter 字段集/顺序一致，德语侧允许唯一多出 `noindex`（分层发布）
  2 正文 h2/h3 条数与层级一一对应
  3 德语 h2/h3 禁 `,` `;` `:`（check_headings 的 RELAXED；`—`/`–` 允许）
  4 站内链必须 `/de/` 前缀（外链裸写，禁过 lang-href）
  5 单位禁 `Mbps`/`Kbps`/`Gbps`（全站口径 `Mbit/s`）
  6 短代码 `{{< count-providers >}}` 保留
德语纪律：人称 `du`；术语 Tarif / Anbieter / Heimatnetz / Kontingent / Fair-Use。
用法：python -X utf8 scripts/_patch_networks_de_a.py [--dry] [--only SLUG]
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
# china
# ═════════════════════════════════════════════════════════════════════════════
DOCS["china"] = '''---
title: "China Reise-eSIM Netze: China Mobile, China Unicom und China Telecom"
description: "Eine China-eSIM leitet den Datenverkehr außerhalb der Festlandnetze, deshalb funktionieren Google und WhatsApp ohne Zusatzsoftware. Welcher Anbieter und welches Telefon nötig sind."
date: 2026-10-03
lastmod: 2026-10-03
iso: "CN"
noindex: true
# TODO(de)：分层发布 —— 全站德语译文解禁（D9 那一轮）时删掉上面这行。
seo:
  title: "China Reise-eSIM Netze 2026: Datentarife die funktionieren"
kicker: "China ist das eine Reiseziel, an dem die gekaufte eSIM nicht nur deine Geschwindigkeit ändert, sondern auch welche Teile des Internets du erreichst. Alle Reise-eSIM-Marken, die wir erfassen, fahren auf denselben drei Betreibern, die Marke ist also eine Preisfrage, während das Routing die ganze Entscheidung ist."
h2_carriers: "Die drei chinesischen Betreiber einer Reise-eSIM"
h2_scoreboard: "Was unabhängige Tests über chinesische Netze sagen"
h2_brands: "Chinesisches Heimatnetz je eSIM-Marke"
h2_cities: "Chinesische Städte mit schnellem 5G in jedem Netz"
h2_next: "Bevor du eine China-eSIM kaufst"
h2_answer: "Was eine China-Reise-eSIM zuerst verändert"
h2_facts: "Fakten zum eSIM-Netz in China"
prompt_answer: "China betreibt drei nationale Betreiber — China Mobile, China Unicom und China Telecom — und jede Reise-eSIM-Marke, die wir erfassen, fährt auf allen dreien. Der entscheidende Unterschied ist das Routing und nicht die Geschwindigkeit, denn eine Reise-eSIM wird außerhalb des chinesischen Festlands ausgegeben und erreicht das Internet von außerhalb des Festlands, deshalb funktionieren Dienste, die an einer inländischen chinesischen Leitung gesperrt sind, meist trotzdem. China Mobile hat die größte Reichweite, und die eSIM vor dem Flug zu installieren ist unerlässlich."
fact_registration: "Lokale SIMs brauchen eine Echtnamen-Registrierung. Reise-eSIMs brauchen keinen Ausweis und werden im Ausland gekauft."
intro_carriers: "Eine Reise-eSIM für China kauft Großhandelszugang bei China Mobile, China Unicom oder China Telecom. Die Marke besitzt das Funknetz nicht, auf welchen der drei du also landest, bestimmen die Vereinbarungen des Tarifs und nicht etwas, das du beim Kauf wählst. Das macht jede Marke zu einer Art MVNO chinesischer Netze, weshalb das Routing eines Tarifs mehr zählt als der Markenname darauf."
intro_brands: "Jede Marke unten verbindet sich mit allen drei chinesischen Betreibern. Weil alle drei national sind, zeigen sich die praktischen Unterschiede vor allem außerhalb der großen Städte, und die Tabelle liest sich als Preisliste statt als Abdeckungskarte."
cities_note: "Peking, Shanghai, Guangzhou und Shenzhen fahren auf allen drei Betreibern schnelles 5G, auch unterirdisch, das Stadtsignal entscheidet einen chinesischen Kauf also nicht. Die Variable auf dieser Seite ist das Routing und nicht die Abdeckung: Eine einreisende Reise-eSIM erreicht das Internet über ein internationales Gateway, und das ist vor deiner Ankunft festgelegt."
cities_detail:
  - name: "Peking"
    reality: "Peking ist auf allen drei Betreibern abgedeckt, auch in der U-Bahn, und das Netz hält auf den Strecken zur Großen Mauer und nach Hebei, wo weiterhin das Routing und nicht das Signal das Erlebnis prägt."
  - name: "Shanghai"
    reality: "Shanghai ist auf allen drei Betreibern abgedeckt, auch in der Metro, und die Abdeckung läuft ohne Unterbrechung entlang des Bahnkorridors im Jangtse-Delta nach Suzhou und Hangzhou weiter."
  - name: "Guangzhou"
    reality: "Guangzhou ist auf allen drei Betreibern abgedeckt, und das Perlflussdelta liest sich als ein durchgehendes Abdeckungsgebiet bis nach Shenzhen und an die Grenze zu Hongkong."
  - name: "Shenzhen"
    reality: "Shenzhen ist auf allen drei Betreibern abgedeckt, die U-Bahn voll ausgestattet, und nahe der Grenze zu Hongkong kann ein Telefon auf ein Hongkonger Netz abdriften, was eine Abrechnungsfrage und keine Abdeckungsfrage ist."
faq_heading: "Fragen zu China-eSIM und Netz"
faqs:
  - q: "Warum erreicht eine Reise-eSIM Seiten die eine chinesische SIM nicht erreicht?"
    a: "Es hängt davon ab, wo der Datenverkehr herauskommt. Eine Reise-eSIM wird von einem Anbieter außerhalb des chinesischen Festlands ausgegeben, deine Datensitzung wird also zurück zum Heimatnetz dieses Anbieters geführt und erreicht das Internet von außerhalb des Festlands. Eine lokal gekaufte chinesische SIM-Karte ist eine inländische Leitung, und inländischer Mobilfunkverkehr bleibt in den Festlandnetzen. Das praktische Ergebnis ist, dass Google, WhatsApp, Gmail und andere Dienste, die an einer inländischen chinesischen Leitung nicht erreichbar sind, auf einer einreisenden Reise-eSIM ohne Zusatzsoftware meist funktionieren."
  - q: "Muss ich eine China-eSIM installieren bevor ich lande?"
    a: "Ja, und das ist die mit Abstand häufigste Art, wie eine China-Reise schiefgeht. Anbieterseiten, App-Stores und Aktivierungsportale sind oft nicht erreichbar, sobald du an einer Festlandverbindung bist, eine Installation nach der Landung kann also genau in dem Moment scheitern, in dem du sie brauchst. Installiere sie zu Hause über deine normale Verbindung und schalte sie bei der Landung ein."
  - q: "Funktioniert eine China-eSIM auf einem im Festland gekauften Handy?"
    a: "Meist nicht. In Festlandchina verkaufte Telefone unterstützen nur inländische eSIM-Profile, und eine einreisende Reise-eSIM wird darauf nicht aktiviert. Dieselbe Einschränkung gilt für in China verkaufte eSIM-only-Geräte, die außerdem weniger Profilplätze haben als die internationale Version. Bring ein außerhalb des Festlands gekauftes Telefon mit oder eine physische SIM, und prüfe das Modell vor der Reise."
  - q: "Welches chinesische Netz ist am besten?"
    a: "China Mobile hat die größte Reichweite, einschließlich U-Bahn-Tunneln, kleinerer Städte und der meisten Touristenrouten, was in China mehr zählt als in den meisten Reisezielen, weil die Entfernungen so groß sind. China Unicom ist in den Städten schnell und ein häufiger Host für einreisende Reise-eSIMs. China Telecom ist stark im Süden und in jeder Großstadt. Beachte, dass Opensignal für das chinesische Festland keinen Crowdsourced-Bericht veröffentlicht, es gibt also keine unabhängige Betreiber-Rangliste wie auf den anderen Seiten dieser Netz-Karte."
  - q: "Muss ich eine chinesische SIM oder eSIM registrieren?"
    a: "Eine chinesische SIM erfordert eine Echtnamen-Registrierung mit Reisepass, und die Aktivierung einer inländischen eSIM bedeutet einen Besuch in einem Betreibershop zur persönlichen Identitätsprüfung. Eine bei einem internationalen Anbieter gekaufte Reise-eSIM ist auf diesen Anbieter registriert und nicht auf dich, du sparst dir den Ladenbesuch also ganz — dasselbe Muster wie in fast jedem Reiseziel dieser Netz-Karte, hier aber folgenreicher wegen der Sprachbarriere und der Wartezeiten."
  - q: "Gibt es unbegrenzte Daten mit einer China-eSIM?"
    a: "Ja. Einige der Marken, die wir erfassen, verkaufen China-Tarife mit unbegrenzten Daten neben den Datentarifen mit festem Kontingent, und beide erscheinen im selben Vergleich. Weil Anbieterportale an einer Festlandverbindung schwer erreichbar sein können, ist ein Datentarif mit großzügigem Puffer im Alltag einfacher als einer, den du mitten auf der Reise aufladen willst."
  - q: "Lohnt sich eine China-eSIM gegenüber einer lokalen SIM?"
    a: "Für Touristen meist ja, und das Routing zählt mehr als der Preis. Eine lokal gekaufte chinesische SIM braucht eine Echtnamen-Registrierung mit Reisepass und erreicht nur Festlandnetze, inländisch gesperrte Dienste bleiben also gesperrt. Eine einreisende Reise-eSIM ist auf ihren Anbieter registriert und nicht auf dich und erreicht das Internet von außerhalb des Festlands. Für die meisten Touristen ist das mehr wert als der niedrigere Listenpreis einer inländischen SIM, und das Profil kommt innerhalb von Minuten nach der Zahlung, lange vor deinem Flug."
  - q: "Wie viele Daten braucht eine China-Reise?"
    a: "Eine Woche Karten, Messaging und Foto-Uploads liegt für die meisten Besucher unter 5 GB, und zwei Wochen derselben Nutzung passen meist in 10 GB. Video-Streaming ist der Posten, der ein kleines Kontingent sprengt. Der beste Ansatz ist, den Datentarif vor dem Flug zu dimensionieren, denn ein Aufladen aus dem chinesischen Festland heraus kann umständlich sein."
---

## Wie internationales Roaming verändert was eine China-eSIM erreichen kann

China ist das eine Reiseziel in dieser Netz-Karte, bei dem die Frage das Routing und nicht das Signal ist. Hier geht es um das Routing, und das Routing zählt mehr.

Eine Reise-eSIM wird von einem Unternehmen außerhalb des chinesischen Festlands ausgegeben. Wenn du sie nutzt, wird deine Datensitzung zurück zum Heimatnetz dieses Anbieters geführt und erreicht das Internet von außerhalb des Festlands statt über einen inländischen chinesischen Betreiber. Eine in China gekaufte SIM-Karte ist eine inländische Leitung, und inländischer Mobilfunkverkehr bleibt in den Festlandnetzen. Die Regulierungsbehörde für den inländischen Markt ist das [Ministerium für Industrie und Informationstechnologie](https://www.miit.gov.cn/).

Der Unterschied zeigt sich sofort auf einer normalen Reise. Dienste, die an einer inländischen chinesischen Verbindung nicht erreichbar sind, funktionieren auf einer einreisenden Reise-eSIM meist ohne Zusatzsoftware, ohne Konfiguration und ohne etwas, das du nach der Landung installieren musst. Das ist kein Merkmal, das der Anbieter als Workaround bewirbt — es ist einfach die Art, wie internationales Roaming immer funktioniert hat —, für einen Besucher aber ist es die folgenreichste Tatsache beim Datenkauf in China.

Es bedeutet auch, dass der Vergleich gar nicht zwischen drei chinesischen Betreibern stattfindet. Er findet zwischen einer Reise-eSIM und einer lokalen SIM statt, und die beiden geben dir Zugang zu unterschiedlichen Diensten.

## Installiere deine China-eSIM bevor du fliegst

Die Installation vor dem Flug zu überspringen ist das Fehlermuster, das China-Reisen ruiniert, und es ist völlig vermeidbar.

Anbieterseiten, App-Stores und Aktivierungsportale sind von einer Festlandverbindung aus häufig nicht erreichbar. Wenn du landest, eine lokale SIM kaufst und dann versuchst, eine Reise-eSIM als Backup zu installieren, kann es sein, dass du den Anbieter dafür nicht erreichst. Dasselbe gilt für alle, die annehmen, sie regeln eine eSIM am Flughafen über Hotel-WLAN, das selbst an einer Festlandverbindung hängt.

Die Lösung dauert zu Hause zwei Minuten: Installiere die eSIM vor der Abreise, während du an einer Verbindung bist, die du kontrollierst, und schalte die Leitung bei der Landung einfach ein. Eine eSIM ist ein Profil, das dein Telefon herunterlädt, statt eine Karte, die du einsetzt — den Standard pflegt die [GSMA](https://www.gsma.com/esim/) —, und genau deshalb kann sie von überall installiert werden. Unser [Installationsratgeber](/de/guides/how-to-install-esim/) führt dich durch. Erledige es, bevor du packst, und nicht erst nach der Ankunft.

## Funktioniert eine China-eSIM in einem in China gekauften Telefon

Die eSIM-Regel nur für den Inlandsmarkt trifft eine bestimmte Gruppe von Reisenden, und es lohnt sich, das vor jedem Kauf zu prüfen.

| Telefon | eSIM-Unterstützung | Reise-eSIM aus dem Ausland |
|---|---|---|
| iPhone außerhalb des Festlands gekauft | Ja, mehrere Profile | Funktioniert |
| iPhone im Festland gekauft | Nur inländische Profile | Wird nicht aktiviert |
| Die meisten in China gekauften Android-Telefone | Nur inländische Profile, falls überhaupt | Wird nicht aktiviert |
| Jedes Telefon mit physischem SIM-Slot | Nicht zutreffend | Nutze stattdessen eine physische Reise-SIM |

Das chinesische Festland hat eSIM in Telefonen erst im Oktober 2025 zugelassen, und die Umsetzung ist inlandsorientiert: Dort verkaufte Geräte unterstützen chinesische Betreiberprofile, und die internationalen eSIM-only-Modelle haben mehr Profilplätze als dieselbe lokal verkaufte Hardware.

Wenn du mit einem in China gekauften Telefon reist, ist eine physische Reise-SIM die praktikable Option. Wenn dein Telefon von woanders kommt und eSIM unterstützt, ist der eSIM-Weg unkompliziert.

## China Mobile China Unicom und China Telecom im Vergleich

China ist der eine große Markt ohne Opensignal Mobile Network Experience Report, es gibt also keine unabhängige Crowdsourced-Rangliste je Betreiber, die man neben die anderen Seiten hier stellen könnte. Der Speedtest Global Index von Ookla verfolgt das Land Monat für Monat und setzte den Median-Mobilfunk-Download des chinesischen Festlands im August 2026 auf 221,77 Mbit/s, was es in die globale Spitzengruppe bringt, ohne dir zu sagen, welchen Betreiber du bevorzugen sollst.

Was gut belegt ist, ist die Form des Marktes.

### China Mobile hat die größte 5G-Reichweite

China Mobile hat die größte Teilnehmerbasis und den breitesten Fußabdruck, einschließlich U-Bahn-Tunneln, kleinerer Städte und der meisten Touristenrouten. In einem so großen Land zählt Reichweite mehr als Spitzengeschwindigkeit, und es ist das Netz, in dem du sein solltest, wenn deine Route über die großen Küstenstädte hinausgeht.

### China Unicom ist in den Städten schnell

China Unicom ist ein häufiger Host für einreisende Reise-eSIMs, und seine ländliche Reichweite liegt einen Schritt hinter China Mobile.

### China Telecom ist stark im Süden

China Telecom ist in jeder Großstadt stark und überall eine solide zweite Wahl.

Alle {{< count-providers >}} Reise-eSIM-Marken, die wir erfassen, verbinden sich mit allen drei Betreibern, was die Markentabelle unten Zeile für Zeile zeigt. In der Praxis entscheidet dein Anbieter, auf welchem der drei du landest, und da alle drei national sind, zeigen sich Abdeckungsunterschiede vor allem weit außerhalb der Städte.

## Abdeckung von den Küstenstädten bis ins Landesinnere

Chinas Größe macht eine Abdeckungsplanung wirklich notwendig, und die Entfernungen sind größer, als die meisten Besucher erwarten.

| | Was zu erwarten ist | Welches Netz |
|---|---|---|
| Peking, Shanghai, Guangzhou, Shenzhen | Durchgehend sehr schnelles 5G, auch in der U-Bahn | Beliebig |
| Große Touristenstädte und der Küstenstreifen | Zuverlässiges 5G und 4G | Beliebig |
| Hochgeschwindigkeitsbahn-Korridore | Abdeckung entlang der Strecke mit gelegentlichen Lücken | China Mobile |
| Kleinere Städte und Kreisstädte | Solides 4G, dünneres 5G | China Mobile |
| Binnenprovinzen weit von der Küste | Abdeckung folgt Siedlungen statt der Karte | China Mobile, und rechne mit Lücken |

China Mobile ist von den dreien im größten Gebiet vertreten, weshalb es die sichere Antwort bleibt, sobald eine Reise die Küstenstädte verlässt. Weil jeder Anbieter, den wir erfassen, es anbietet, ist das eine Prüfung des Tarifs und nicht der Marke.

China zieht sich außerdem aus älteren Technologien zurück. Die 2G-Zulassung von China Mobile lief Ende 2025 aus, und provinziale 3G-Abschaltungen haben 2026 begonnen, ein 4G- oder 5G-Gerät mit VoLTE ist also das richtige Gerät zum Mitbringen. Der [Kompatibilitätscheck](/de/guides/esim-compatibility-check/) deckt konkrete Modelle ab.

## Vier Prüfungen bevor du einen China-eSIM-Datentarif kaufst

Vier Prüfungen decken fast alles ab, was auf einer China-Reise schiefgehen kann.

Erstens, leitet der Tarif international weiter, statt eine inländische chinesische Leitung weiterzuverkaufen. Das ist der ganze Punkt, und jede seriöse Reise-eSIM tut das standardmäßig. Zweitens, unterstützt dein Telefon einreisende eSIM-Profile, denn ein in China gekauftes Gerät tut das nicht. Drittens, hast du sie vor der Abreise installiert. Viertens, passt das Kontingent zur Reisedauer, da Karten-Apps, Übersetzungswerkzeuge und Foto-Uploads alle anders verbrauchen, wenn du zugleich Dienste erreichst, die lokal nicht verfügbar sind.

Unser [Vergleich der China-eSIM-Tarife](/de/compare/china/) ordnet die Tarife, die wir erfassen, nach Preis pro Gigabyte und pro Tag, der [Reisedaten-Rechner](/de/tools/) dimensioniert ein Kontingent auf deine Daten, und aktuelle Rabatte findest du in den [aktuellen eSIM-Angeboten](/de/esim-deals/). Wenn deine Reise in einen anderen asiatischen Markt weitergeht, decken unsere Netzseiten zu [Japan](/de/networks/japan/) und [Südkorea](/de/networks/south-korea/) die Betreiber auf der anderen Seite ab.

Drei Schlusshinweise. Spektrum im chinesischen Festland wird national über Bänder lizenziert, auf die importierte Geräte nicht immer abgestimmt sind, eine einreisende eSIM kann also weniger liefern als die angegebene Zahl. Stadtnetze können zu Pendlerstoßzeiten außerdem unter Überlast leiden, besonders in der Metro. Und lokal gekaufte Prepaid-Tarife tragen Fair-Use-Bedingungen, die selten auf Englisch erklärt werden, ein weiterer Grund, warum der Weg über die einreisende eSIM einfacher ist.
'''


# ═════════════════════════════════════════════════════════════════════════════
# france
# ═════════════════════════════════════════════════════════════════════════════
DOCS["france"] = '''---
title: "Frankreich Reise-eSIM Netze: Orange, SFR und Bouygues erklärt"
description: "Orange, SFR und Bouygues tragen jede Reise-eSIM, die wir in Frankreich erfassen. Wie sie sich bei 5G-Geschwindigkeit und Reichweite unterscheiden und was die französische SIM-Ausweisregel bedeutet."
date: 2026-10-03
lastmod: 2026-10-03
iso: "FR"
noindex: true
# TODO(de)：分层发布 —— 全站德语译文解禁（D9 那一轮）时删掉上面这行。
seo:
  title: "Frankreich Reise-eSIM Netze 2026: Bestes 5G für Touristen"
kicker: "Frankreich teilt seine Netze sauber auf. Orange gewinnt fast alles, was messbar ist, Bouygues gewinnt die Erlebniskategorien, und SFR liegt beim Preis zwischen ihnen. Alle Reise-eSIM-Marken, die wir erfassen, fahren auf denselben drei Betreibern, die gewählte Marke ändert also die Rechnung und nicht die Masten."
h2_carriers: "Die drei französischen Netze offen für eine Reise-eSIM"
h2_scoreboard: "Orange Bouygues und SFR im unabhängigen Test"
h2_brands: "Französisches Heimatnetz je eSIM-Marke"
h2_cities: "Französische Städte von jedem Netz gut abgedeckt"
h2_next: "Eine Frankreich-eSIM passend zu deiner Route wählen"
h2_answer: "Was eine Frankreich-Reise-eSIM ändert und was nicht"
h2_facts: "Fakten zum eSIM-Netz in Frankreich"
prompt_answer: "Frankreich betreibt drei nationale 5G-Netze — Orange, SFR und Bouygues — und jede Reise-eSIM-Marke, die wir erfassen, fährt auf allen dreien, die Marke ändert also die Rechnung und nicht das Signal. Orange führt bei Geschwindigkeit und Abdeckung, Bouygues gewinnt die Video- und Qualitätskategorien, und alle drei tragen kommerzielles 5G. Lokale Prepaid-SIMs brauchen eine Passregistrierung, während eine Reise-eSIM für Touristen gar kein Dokument braucht."
fact_registration: "Lokale Prepaid-SIMs brauchen eine Passregistrierung. Eine Reise-eSIM braucht keine."
intro_carriers: "Französische Reise-eSIM-Kapazität wird im Großhandel bei Orange, SFR oder Bouygues gekauft. Die Marke auf deinem Tarif betreibt das Funknetz nicht, die Abdeckung, die du bekommst, ist also eine Funktion des Heimatnetzes und dessen, wohin du reist. Diese Marken sind der Substanz nach MVNOs, sie verkaufen französische Kapazität weiter, statt sie aufzubauen, keine kann also eine breitere Abdeckung bieten als ihre Rivalen."
intro_brands: "Die Tabelle unten zeigt, auf welchen der drei französischen Betreiber jede Marke setzt. Jeder Anbieter listet alle drei, weshalb sich die französische Abdeckung nicht ändert, wenn du die Marke wechselst."
cities_note: "Paris, Marseille, Lyon und Nizza fahren auf den drei französischen Netzen schnelles 5G, die Stadt ist also nicht der Ort, an dem eine Frankreich-eSIM-Entscheidung fällt. Orange führt die nationalen Testergebnisse auf dieser Seite an, und die Lücke zwischen den dreien ist eine Landesmessung, an den Küsten abseits der Resorts und oben in den Bergen."
cities_detail:
  - name: "Paris"
    reality: "Paris ist auf allen drei Netzen geklärt, und die erste Unsicherheit liegt außerhalb der Ile-de-France auf dem ländlichen Boden, den die TGV-Linien mit hoher Geschwindigkeit durchqueren."
  - name: "Marseille"
    reality: "Marseille ist geklärt mit einer starken 5G-Schicht über die Stadt, und die offene Frage ist die Provence-Küste und die Calanques, wo das Gelände die Sichtlinien zwischen den Masten durchschneidet."
  - name: "Lyon"
    reality: "Lyon ist auf allen drei Netzen geklärt, und der erste echte Test liegt östlich in den Alpen, wo die Täler um Grenoble und Chamonix die Wahl auf das Netz verengen, das das Dorf erreicht."
  - name: "Nizza"
    reality: "Nizza ist entlang der Côte d'Azur geklärt, und die Abdeckung dünnt landeinwärts durch die Alpes-Maritimes aus, wo Bergtäler jedes Netz auf seinen nächsten Mast reduzieren."
faq_heading: "Fragen zu Frankreich-eSIM und Netz"
faqs:
  - q: "Brauche ich einen Ausweis um eine SIM-Karte in Frankreich zu kaufen?"
    a: "Für eine französische SIM ja. Das französische Recht verlangt, dass Prepaid-SIMs auf eine identifizierte Person registriert werden, du zeigst also im Laden einen Reisepass, und der Betreiber erfasst deinen Namen und deine Ausweisnummer. Du brauchst keinen französischen Personalausweis, und eine Hotel- oder Mietadresse wird normalerweise akzeptiert. Niemand fragt nach einer französischen Steuernummer oder einem Bankkonto. Eine online gekaufte Reise-eSIM umgeht die Vorgabe vollständig, was einer der zwei Gründe ist, warum sie für eine kurze Reise der einfachere Kauf ist."
  - q: "Welches französische Netz ist am besten?"
    a: "Orange, mit großem Abstand. Im Bericht von Opensignal vom November 2025 räumte es die Kategorien Geschwindigkeit und Abdeckung ab und holte Download-Geschwindigkeit mit 83,8 Mbit/s, 5G-Download-Geschwindigkeit mit 273,4 Mbit/s und Abdeckungserlebnis mit 9,3 von 10. Bouygues sammelte insgesamt mehr Auszeichnungen, 12 von 17, weil es die Anwendungskategorien gewinnt — Video-Erlebnis und gleichbleibende Qualität — und sich Zuverlässigkeit mit Orange bei 925 Punkten teilt. Lies sie als unterschiedliche Arten von Stärke und nicht als einen klaren Sieger."
  - q: "Ist 5G mit einer Frankreich-eSIM verfügbar?"
    a: "Ja. Alle drei Betreiber, die wir erfassen, betreiben kommerzielles 5G, und jedes französische Betreiberprofil listet es. Opensignal maß den 5G-Download von Orange mit 273,4 Mbit/s, vor SFR mit 223,8 Mbit/s. Es gibt keinen reinen 4G-Betreiber zu meiden, 5G ist in Frankreich also nicht extra zu bezahlen wert — die nützliche Prüfung ist, ob dein Gerät die europäischen Bänder unterstützt."
  - q: "Kann ich eine Frankreich-eSIM in Spanien oder Italien nutzen?"
    a: "Eine reine Frankreich-eSIM endet an der Grenze. Lokal verkaufte französische SIM-Karten enthalten kostenloses Roaming in der Europäischen Union, aber dieses Recht hängt an der lokalen SIM und nicht an einem Frankreich-spezifischen Reisetarif. Wenn deine Reise mehr als ein Land quert — was in Europa häufig ist —, kaufe einen Europa-Tarif und prüfe die Länderliste vor der Zahlung."
  - q: "Funktioniert mein Telefon noch wenn Frankreich ältere Netze abschaltet?"
    a: "Es hängt davon ab, wie alt das Gerät ist. Orange zieht sich 2026 im französischen Festland aus 2G zurück und ab Ende 2028 aus 3G. Ein 4G- oder 5G-Telefon mit VoLTE ist nicht betroffen. Geräte, die allein auf 2G oder 3G angewiesen sind — einige ältere importierte Telefone, Feature-Phones und zellulare Tracker —, funktionieren nicht mehr. Unser [Kompatibilitätsratgeber](/de/guides/esim-compatibility-check/) listet die sicheren Modelle."
  - q: "Gibt es unbegrenzte Daten mit einer Frankreich-eSIM?"
    a: "Ja. Mehrere Marken, die wir erfassen, verkaufen Frankreich-Tarife mit unbegrenzten Daten neben den Datentarifen mit festem Kontingent, und die beiden stehen im selben Vergleich. Unbegrenzte Reisetarife reduzieren normalerweise die Geschwindigkeit nach einem täglichen Fair-Use-Kontingent, statt die Verbindung zu beenden, prüfe diese Zahl also, wenn du streamen oder tethern willst. Das Profil kommt innerhalb von Minuten nach der Zahlung, die Sofortaktivierung, die zu spät gebuchten Reisen passt."
  - q: "Ist eine Frankreich-eSIM ein guter Wert gegenüber einer lokalen Prepaid-SIM?"
    a: "Für eine kurze Reise ja, und der Papierkram ist der Grund. Eine französische Prepaid-SIM ist billiger pro Gigabyte, braucht aber eine Passregistrierung am Verkaufspunkt. Eine Reise-eSIM braucht in keinem Schritt ein Dokument und wird vor dem Flug gekauft, was bei allem unter zwei Wochen den Preisunterschied meist aufwiegt."
  - q: "Funktioniert eine Frankreich-eSIM in Spanien oder Italien ohne Roaming-Gebühren?"
    a: "Nicht mit einem reinen Frankreich-Tarif. Kostenloses Roaming in der Europäischen Union hängt an lokal gekauften französischen SIM-Karten und nicht an einer Frankreich-spezifischen Reise-eSIM, eine Mehrländer-Route braucht also einen Europa-Tarif. Die Grenzen hier sind nah und per Zug leicht zu queren, bestätige die Länderliste also vor der Zahlung."
---

## Die zwei französischen Regeln die einen SIM-Kauf prägen

Frankreich ist ein reifer Markt, in dem die Netze gut und weitgehend ähnlich sind, die Entscheidung dreht sich also eher um die Regulierung als um die Leistung. Zwei Regeln zählen, und die Regulierungsbehörde hinter beiden ist [ARCEP](https://www.arcep.fr/).

### Warum eine französische Prepaid-SIM einen Reisepass braucht

Eine französische Prepaid-SIM zu kaufen bedeutet, am Verkaufspunkt einen Reisepass zu zeigen, und der Betreiber erfasst ihn. Es gibt keine Anforderung einer französischen Adresse und keine Wartezeit, aber einen Schalterbesuch und ein Dokument. Eine vor dem Flug gekaufte Reise-eSIM hat diesen Schritt nicht.

### EU-Roaming-Regeln hängen an der französischen SIM

Roaming in der Europäischen Union hängt an der SIM und nicht am Tarif. Eine lokal gekaufte französische SIM funktioniert in der EU und im EWR zu Inlandssätzen weiter, vorbehaltlich der Fair-Use-Grenzen. Eine reine Frankreich-Reise-eSIM nicht — sie ist für französische Netze bereitgestellt und endet an der Grenze. Diese Unterscheidung entscheidet, ob du einen Ein-Land-Tarif oder einen Europa-Tarif brauchst.

Die Netzseite ist einfach. {{< count-providers >}} Reise-eSIM-Marken, die wir erfassen, fahren alle auf denselben drei Betreibern — Orange, SFR und Bouygues —, kein Anbieter kann also eine bessere französische Abdeckung bieten als ein anderer, und die Markentabelle unten beweist es Zeile für Zeile. Free Mobile betreibt in Frankreich ebenfalls ein nationales Netz, doch die Tarife, die wir erfassen, fahren auf den drei Betreibern oben. Unser [Frankreich-Tarifvergleich](/de/compare/france/) ordnet die tatsächlichen Produkte.

## Wo Orange Bouygues und SFR jeweils den Vorteil haben

Die drei nationalen Netze Frankreichs teilen sich ungewöhnlich sauber auf, und die Aufteilung liegt zwischen zwei verschiedenen Arten von Stärke.

### Orange gewinnt alles Messbare im französischen Netz

Der Bericht von Opensignal vom November 2025 gab Orange Download-Geschwindigkeit mit 83,8 Mbit/s, 5G-Download-Geschwindigkeit mit 273,4 Mbit/s vor SFR mit 223,8, und Abdeckungserlebnis mit 9,3 von 10. Ookla machte es separat für die zweite Hälfte 2024 mit einem Median-Download von 122,77 Mbit/s zum schnellsten Mobilfunkanbieter Frankreichs, mit einem Median-5G-Download von 281,3 Mbit/s. Wenn deine Reise das ländliche Frankreich, die Atlantikküste oder die Alpen einschließt, ist die Reichweite von Orange der Grund, darauf zu achten, was unter deinem Tarif steckt.

### Bouygues gewinnt die französischen Erlebniskategorien

Bouygues sammelte im selben Zyklus 12 von 17 Auszeichnungen, darunter Video-Erlebnis, Sprach-App-Erlebnis und gleichbleibende Qualität, und teilt sich Zuverlässigkeit mit Orange bei statistisch gleichauf liegenden 925 Punkten. Das ist ein Netz, das darauf optimiert ist, wie es sich anfühlt, statt darauf, was es in einem Speedtest anzeigt — ein bedeutsamer Unterschied, wenn du die Reise mit Videoanrufen und Streaming statt mit Downloads verbringst.

### SFR ist die günstige Mitteloption in Frankreich

SFR ist die mittlere Option mit schnellen 5G-Spitzen und einem breiten Fußabdruck, der bei der Abdeckung knapp hinter Orange liegt. Es ist oft das günstigere der drei, weshalb es auf so vielen Budget-Tarifen erscheint.

Die beiden Spalten entstehen durch unterschiedliche Methoden und sind nicht austauschbar — die eine mittelt, was echte Nutzer erlebt haben, die andere nimmt den Mittelwert der Speedtests, die Menschen freiwillig ausgeführt haben. Das reicht, um dieselben drei Netze neu zu ordnen. Keine von beiden sagt deine eigene Verbindung voraus.

## Was Frankreich mit seinen älteren Netzen macht

Frankreich ist auf halbem Weg, die Technologien vor 4G abzuschalten, und den Zeitplan solltest du kennen, wenn du mit einem älteren Gerät oder einem zellularen Tracker reist.

| | Status | Was betroffen ist |
|---|---|---|
| 2G | Orange zieht sich 2026 im französischen Festland zurück, Pilot-Departements ab März | Ältere Feature-Phones, einige Tracker und Telemetriegeräte |
| 3G | Orange schaltet ab Ende 2028 ab | Geräte, die für Anrufe oder Daten auf 3G zurückfallen |
| 4G und 5G | Bleiben und werden ausgebaut | Jedes moderne Telefon mit VoLTE-Unterstützung |

Die praktische Schlussfolgerung ist einfach. Bring ein 4G- oder 5G-Gerät mit, das VoLTE unterstützt, und nichts davon berührt dich. Bring ein älteres Gerät mit, und es registriert sich womöglich gar nicht in einem französischen Netz. Eine eSIM ist ein Profil, das dein Telefon herunterlädt, statt eine Karte, die du einsetzt, und den Standard dahinter pflegt die [GSMA](https://www.gsma.com/esim/), doch die Netztechnologie, die ein Gerät unterstützt, ist durch seine Hardware festgelegt. Der [Geräte-Kompatibilitätsratgeber](/de/guides/esim-compatibility-check/) klärt das, bevor du packst.

## Eine Frankreich-eSIM gegen eine französische SIM ohne Roaming-Gebühren

Frankreich bietet drei Wege zu mobilen Daten, und die Kompromisse werden von der Registrierungsregel geprägt.

| | Reise-eSIM | Französische Prepaid-SIM | Roaming mit Heimat-SIM |
|---|---|---|---|
| Ausweisprüfung | Keine | Reisepass beim Kauf erfasst | Keine |
| Funktioniert EU-weit | Nur mit einem Europa-Tarif | Ja, vorbehaltlich der Fair-Use-Grenzen | Ja, wenn dein Heimatnetz es erlaubt |
| Wann sie funktioniert | Bei der Landung, zu jeder Stunde | Nach einem Schalterbesuch | Bei der Landung |
| Kosten für eine Woche | Festpreis, keine Überraschungen | Günstig pro GB, plus der Umweg | Hängt ganz von deinem Heimattarif ab |
| Hauptnachteil | Nur Daten, keine französische Nummer | Schalterschlange und Papierkram bei der Ankunft | Möglicher Aufpreis außerhalb deines Kontingents |

Besucher aus der Europäischen Union sollten zuerst ihren eigenen Tarif prüfen, denn Roam-like-at-Home deckt Frankreich möglicherweise bereits ohne Aufpreis ab. Alle anderen wählen zwischen einer Reise-eSIM und einem Kauf am Schalter, und bei einer einwöchigen Reise gewinnt die eSIM meist bei der Zeit, selbst wenn die lokale SIM bei den Cents gewinnt. Der [Ratgeber eSIM gegen physische SIM](/de/guides/esim-vs-physical-sim/) deckt den breiteren Vergleich ab.

## Was du auf deinem Telefon prüfen solltest vor einer französischen 5G-Reise

Alle drei Betreiber, die wir erfassen, betreiben kommerzielles 5G, und jedes französische Profil auf dieser Seite listet es, Frankreich hat also keine reine 4G-Falle. Opensignal maß den 5G-Download von Orange im November 2025 mit 273,4 Mbit/s und SFR mit 223,8 Mbit/s, was das französische 5G unter die stärkeren Netze in Westeuropa einordnet.

Das macht 5G zu einer geklärten Frage statt zu einem Verkaufsargument. Die sinnvollen Prüfungen sind enger. Listet der Tarif vor dir 5G. Deckt dein Gerät die europäischen Bänder ab. Kann es VoLTE-Anrufe führen, was zählt, da 3G abgeschaltet wird. Und wenn deine Reise Grenzen quert, deckt der Tarif die Länder auf deiner Route ab — unsere Netzseiten zu [Spanien](/de/networks/spain/), [Deutschland](/de/networks/germany/) und [Italien](/de/compare/italy/) decken die Betreiber nebenan ab.

Für eine Reise, die in Frankreich bleibt, ist das Letzte, was zu wägen ist, die Form des Tarifs. Ein kurzer Städtekurzurlaub braucht ein kleines Kontingent über ein paar Tage; ein Autourlaub durch die Provence braucht mehr, und der [Datenkontingent-Rechner](/de/tools/) schätzt es aus deinen Apps und Daten. Aktuelle Rabatte findest du unter den [aktuellen eSIM-Rabatten](/de/esim-deals/).

Zwei praktische Hinweise vor dem Kauf. Französisches Spektrum wird national lizenziert, und die genutzten Bänder unterscheiden sich von denen in Nordamerika, ein importiertes Gerät ist also eine Prüfung wert. Überlast zu Stoßzeiten in Paris und Lyon trifft alle drei Netze gleichermaßen, und der Upload-Durchsatz ist die Zahl, die du beobachten solltest, wenn du unterwegs posten willst.
'''


# ═════════════════════════════════════════════════════════════════════════════
# germany
# ═════════════════════════════════════════════════════════════════════════════
DOCS["germany"] = '''---
title: "Deutschland Reise-eSIM Netze: Telekom, Vodafone und O2 erklärt"
description: "Das deutsche Recht erzwingt eine Ausweisprüfung bei jeder Prepaid-SIM. Wie Telekom, Vodafone und O2 abschneiden und warum eine Deutschland-eSIM den Papierkram ganz überspringt."
date: 2026-10-03
lastmod: 2026-10-03
iso: "DE"
noindex: true
# TODO(de)：分层发布 —— 全站德语译文解禁（D9 那一轮）时删掉上面这行。
seo:
  title: "Deutschland Reise-eSIM Netze 2026: Bestes 5G für Touristen"
kicker: "Deutschland ist der eine große europäische Markt, in dem der Papierkram mehr Käufe entscheidet als der Speedtest. Jede lokale Prepaid-SIM muss per Gesetz gegen deine Identität registriert werden, und alle Reise-eSIM-Marken, die wir erfassen, fahren auf denselben drei Betreibern — Telekom, Vodafone und O2 —, die Netzwerkwahl ändert also nichts, während die Registrierung alles ändert."
h2_carriers: "Die drei deutschen Netze auf denen eine Reise-eSIM fahren kann"
h2_scoreboard: "Telekom Vodafone und O2 im unabhängigen Test"
h2_brands: "Deutsches Heimatnetz je eSIM-Marke"
h2_cities: "Deutsche Städte in denen alle drei Netze überzeugen"
h2_next: "Deinen Deutschland-eSIM-Kauf planen"
h2_answer: "Was eine Deutschland-Reise-eSIM zuerst löst"
h2_facts: "Fakten zum eSIM-Netz in Deutschland"
prompt_answer: "Deutschland betreibt drei nationale 5G-Netze — Telekom, Vodafone und O2 — und jede Reise-eSIM-Marke, die wir erfassen, fährt auf allen dreien, die Markenwahl ändert die Abdeckung also nicht. Telekom ist sowohl das schnellste als auch das reichweitenstärkste, und alle drei tragen kommerzielles 5G. Die Regel, die die meisten Käufe entscheidet, ist die Registrierung: Lokale Prepaid-SIMs brauchen nach deutschem Recht eine Identitätsprüfung, während eine Reise-eSIM für Touristen gar kein Dokument braucht."
fact_registration: "Lokale Prepaid-SIMs brauchen per Gesetz eine Identitätsprüfung. Eine Reise-eSIM braucht keine."
intro_carriers: "Eine Reise-eSIM in Deutschland ist eine Großhandelsvereinbarung. Der Anbieter, bei dem du kaufst, betreibt keine Masten; er kauft Kapazität bei Telekom, Vodafone oder O2, und das Netz, auf dem du landest, ist dasjenige, das dir das Reiseziel zuweist. Jede Marke, die deutsche Daten verkauft, ist in der Praxis ein MVNO, sie least Zugang, statt Funkausrüstung zu betreiben, keine von ihnen kann also eine andere beim Signal überbieten."
intro_brands: "Jede Marke unten listet dieselben drei deutschen Netze als Heimatnetz. Das macht die Tabelle zu einer Preisliste und nicht zu einer Abdeckungskarte — der schnellste Weg zu sehen, dass kein Anbieter dir ein stärkeres Signal verkaufen kann als ein anderer."
cities_note: "Berlin, München, Hamburg und Frankfurt werden von allen drei deutschen Netzen stark abgedeckt, und die Lücken zwischen ihnen innerhalb einer Stadt sind zu klein, um sie einzuplanen. Die Rangliste auf dieser Seite ist eine nationale Messung, und sie beginnt, eine Reise außerhalb der Städte zu beschreiben, wo der Fußabdruck von Telekom der breiteste und der von O2 der dünnste ist."
cities_detail:
  - name: "Berlin"
    reality: "Berlin wird von allen drei Netzen stark abgedeckt, und der erste dünnere Boden ist Brandenburg, das ländliche Bundesland, das die Stadt umgibt, wo der Fußabdruck von O2 zuerst schmaler wird."
  - name: "München"
    reality: "München wird von allen drei Netzen stark abgedeckt, und die Abdeckung wird nach Süden in die Bayerischen Alpen schmaler, wo Talrouten die Wahl auf den nächsten Mast reduzieren."
  - name: "Hamburg"
    reality: "Hamburg wird von allen drei Netzen stark abgedeckt, und die Unsicherheit beginnt nach Norden in Schleswig-Holstein und entlang der Nordseeküste."
  - name: "Frankfurt"
    reality: "Frankfurt wird von allen drei Netzen stark abgedeckt, einschließlich des Flughafens und des Rhein-Main-Bahnknotens, und die Abdeckung läuft ohne Unterbrechung das Rheintal hinab Richtung Köln weiter."
faq_heading: "Fragen zu Deutschland-eSIM und Netz"
faqs:
  - q: "Brauche ich einen Ausweis um eine SIM oder eSIM in Deutschland zu kaufen?"
    a: "Für eine lokale deutsche SIM ja, ohne Ausnahme. Das deutsche Recht verlangt seit 2017 bei jeder Prepaid-Aktivierung eine Identitätsprüfung, das heißt einen Reisepass in einem Laden vorzeigen, einen Video-Ident-Anruf durchführen oder an einem Postschalter verifizieren. Du brauchst keine deutsche Adresse, keine Steuernummer und kein Bankkonto. Eine bei einem internationalen Anbieter gekaufte Reise-eSIM steht ganz außerhalb dieses Regimes und braucht in keinem Schritt ein Dokument."
  - q: "Ist Telekom oder Vodafone das bessere deutsche Netz?"
    a: "Telekom ist der Maßstab. Opensignal nannte es Deutschlands Bestes Netz mit 11 von 14 Auszeichnungen direkt, darunter Download-Geschwindigkeit mit 68,9 Mbit/s gegenüber Vodafone mit 56,3 und O2 mit 47,4, und Ookla gab ihm einen Speed Score von 77,9 für das erste Halbjahr 2026 gegenüber Vodafone mit 56,1. Vodafone und O2 funktionieren in Städten beide gut. Wenn deine Reise ins ländliche Brandenburg, in den Schwarzwald oder nach Bayern führt, ist die Reichweite von Telekom der Grund, darauf zu achten."
  - q: "Ist 5G mit einer Deutschland-eSIM verfügbar?"
    a: "Ja. Alle drei nationalen Betreiber betreiben kommerzielles 5G, und jedes deutsche Betreiberprofil, das wir erfassen, listet es, keine Marke kann dir also versehentlich ein reines 4G-Downgrade verkaufen. Opensignal maß den 5G-Download von Telekom im November 2025 mit 173,8 Mbit/s, vor Vodafone mit 154,3 und O2 mit 114,5. Weil alle drei 5G haben, ist es hier keinen Aufpreis wert — die Prüfung, die zählt, ist, ob dein Gerät die deutschen Bänder unterstützt."
  - q: "Kann ich eine Deutschland-eSIM in Nachbarländern nutzen?"
    a: "Nur wenn du einen regionalen Europa-Tarif kaufst und keinen reinen Deutschland-Tarif. Lokal verkaufte deutsche SIM-Karten enthalten kostenloses Roaming in der Europäischen Union, aber eine Deutschland-spezifische Reise-eSIM ist für deutsche Netze bereitgestellt und endet an der Grenze. Wenn deine Reise mehr als ein Land quert, kaufe einen Europa-Tarif und prüfe die Länderliste vor der Zahlung."
  - q: "Was passiert mit meinem Telefon wenn Deutschland ältere Netze abschaltet?"
    a: "Deutschland hat seinen 3G-Abbau bereits abgeschlossen, ein Gerät, das keine VoLTE-Anrufe führen kann, funktioniert in einem deutschen Netz also gar nicht mehr, Daten eingeschlossen. Das trifft ältere importierte Telefone und einige Budget-Geräte. Prüfe dein Modell gegen unseren [Kompatibilitätsratgeber](/de/guides/esim-compatibility-check/), bevor du dich für die Navigation darauf verlässt."
  - q: "Gibt es unbegrenzte Daten mit einer Deutschland-eSIM?"
    a: "Ja. Einige der Marken, die wir erfassen, verkaufen Deutschland-Tarife mit unbegrenzten Daten neben den Datentarifen mit festem Kontingent, und beide erscheinen im selben Vergleich. Unbegrenzte Reisetarife drosseln meist die Geschwindigkeit nach einem täglichen Fair-Use-Kontingent, statt die Verbindung zu kappen, prüfe diese Schwelle also, bevor du einen Aufpreis dafür zahlst. Das Profil kommt innerhalb von Minuten nach der Zahlung, die Sofortaktivierung, die eine eSIM für kurzfristig gebuchte Reisen praktisch macht."
  - q: "Ist eine Deutschland-eSIM mehr wert als eine registrierte Prepaid-SIM?"
    a: "Für eine kurze Reise meist ja. Eine lokale SIM ist beim Preis pro Gigabyte konkurrenzfähig, kostet dich aber einen Schritt der Identitätsprüfung, was in Deutschland einen Passcheck in einem Laden, einen Video-Ident-Anruf oder einen Besuch am Postschalter bedeutet. Eine Reise-eSIM bringt keine Registrierung und keine Schlange mit, und unter zwei Wochen wiegt diese Bequemlichkeit den kleinen Preisunterschied meist auf."
  - q: "Überquert eine Deutschland-eSIM die Europäische Union ohne Roaming-Gebühren?"
    a: "Eine reine Deutschland-eSIM endet an der Grenze. Kostenloses Roaming innerhalb der Europäischen Union gehört zu lokal gekauften deutschen SIM-Karten und nicht zu einem Deutschland-spezifischen Reisetarif, ein Grenzübertritt nach Österreich, Frankreich oder in die Niederlande braucht also einen Europa-Tarif. Kaufe das regionale Produkt, wenn deine Route mehr als ein Land berührt, und bestätige die Länderliste vor der Zahlung."
---

## Wie die deutsche Prepaid-Registrierungspflicht tatsächlich funktioniert

Beginne mit der Regel, denn sie entscheidet in Deutschland mehr Käufe als jeder Speedtest. Seit 2017 ist bei jeder Prepaid-Aktivierung eine Identitätsprüfung Pflicht, und die Behörde, die sie durchsetzt, ist die [Bundesnetzagentur](https://www.bundesnetzagentur.de/EN/Home/home_node.html). In der Praxis erfüllst du sie auf eine von drei Weisen: deinen Reisepass an einem Ladenschalter geprüft, einen Video-Ident-Anruf mit einem echten Mitarbeiter oder einen PostIdent-Termin in einer Postfiliale. Nichts davon ist schwierig, und nichts davon braucht eine deutsche Adresse, eine Steuernummer oder ein Bankkonto. Alles davon kostet Zeit, die du lieber anders verbringst, und alles davon passiert nach der Landung statt vor dem Flug.

Eine Reise-eSIM tritt in diesen Prozess nie ein. Du kaufst bei einem internationalen Anbieter, scannst einen QR-Code und verbindest dich — kein Dokument, kein Mitarbeiter, kein Schalter. Für einen fünftägigen Städtekurzurlaub ist das das ganze Argument, und deshalb verkauft sich eine Deutschland-eSIM bei Kurzzeitbesuchern besser als lokales Prepaid, obwohl lokale SIMs pro Gigabyte billiger sind.

Das zweite, was du wissen solltest, ist, dass die Netz-Frage geklärt ist, bevor du sie stellst. Alle {{< count-providers >}} Marken, die wir erfassen, fahren auf denselben drei Betreibern — Telekom, Vodafone und O2 —, wie die Markentabelle unten Zeile für Zeile zeigt. Kein Anbieter kann dir eine stärkere deutsche Abdeckung verkaufen als ein anderer, die Entscheidung verengt sich also auf Preis, Datenform und Support. Unser [Vergleich der Deutschland-eSIM-Tarife](/de/compare/germany/) ordnet sie genau nach diesen drei.

## Telekom gegen Vodafone und O2 bei Geschwindigkeit und ländlicher Reichweite

Die drei nationalen Netze Deutschlands liegen bei der Leistung ungewöhnlich weit auseinander für einen so dichten Markt.

### Telekom ist der deutsche 5G-Maßstab

Opensignal nannte Telekom Deutschlands Bestes Netz und gewann 11 von 14 Auszeichnungen direkt, darunter Download-Geschwindigkeit mit 68,9 Mbit/s vor Vodafone mit 56,3 und O2 mit 47,4. Ookla maß einen Speed Score von 77,9 für das erste Halbjahr 2026 gegenüber Vodafone mit 56,1. Seine Autobahn- und ländliche Abdeckung ist der Grund, warum es die sichere Wahl für einen Autourlaub ist.

### Vodafone ist der deutsche Stadt-Performer

Vodafone betreibt starkes 5G in städtischen Gebieten und im Westen des Landes und liegt in den Tabellen beider Firmen klar auf Platz zwei. Auf dem Land hinter den Städten fällt es hinter Telekom zurück.

### O2 ist die günstige deutsche 5G-Option

O2 ist die Preisoption und liegt im selben Zyklus bei der Geschwindigkeit mit 47,4 Mbit/s auf Platz drei. Es hat sich erheblich verbessert und liegt in ländlichen Gebieten und in Innenräumen weiterhin zurück. Berlin, Hamburg und München sind in Ordnung. Bayern und der Schwarzwald sind der Ort, wo es sich zeigt.

Ein Hinweis, wie die beiden Spalten zu lesen sind. Sie entstehen durch unterschiedliche Methoden, die eine von der anderen abzuziehen bedeutet also gar nichts. Behandle jede als eigene Rangliste derselben drei Betreiber. Keine von beiden sagt deinen eigenen Durchsatz voraus, der auch von Überlast, deinem Gerät und den unterstützten Bändern abhängt.

## Eine deutsche Grenze überqueren ohne Roaming-Gebühren

Deutschland liegt in der Mitte Europas, und viele Routen respektieren die Grenze nicht. Je nachdem, was du gekauft hast, passieren zwei verschiedene Dinge.

Eine **deutsche lokale SIM** enthält kostenloses Roaming in der Europäischen Union, sie funktioniert in der EU und im EWR weiter, vorbehaltlich der Fair-Use-Grenzen dafür, wie viel des Kontingents du im Ausland verbrauchst. Eine **reine Deutschland-Reise-eSIM** nicht. Sie ist für deutsche Netze bereitgestellt und endet an der Grenze, was zählt, wenn deine Reise Salzburg, Straßburg, Zürich oder Amsterdam berührt. Kaufe in diesem Fall einen Europa-Tarif und bestätige die Länderliste vor der Zahlung — unsere Netzseiten zu [Österreich](/de/compare/austria/), den [Niederlanden](/de/networks/netherlands/) und [Frankreich](/de/networks/france/) decken die Betreiber auf der anderen Seite ab.

## Eine Deutschland-eSIM gegen einen registrierten Prepaid-Datentarif

Eine deutsche lokale SIM ist den Aufwand nur für einen Aufenthalt von einem Monat oder länger wert, weil die Identitätsprüfung die Reibung ist. Das umfasst der Prozess.

| | Reise-eSIM | Deutsche Prepaid-SIM |
|---|---|---|
| Ausweisprüfung | Keine | Reisepass oder Personalausweis, per Gesetz |
| Wie du verifizierst | Nicht zutreffend | Ladenschalter, Video-Ident-Anruf oder PostIdent in einer Postfiliale |
| Deutsche Adresse nötig | Nein | Nein |
| Wann sie funktioniert | Bei der Landung, zu jeder Stunde | Nach Abschluss der Verifizierung, was den nächsten Tag bedeuten kann |
| Wo kaufen | Online, vor dem Flug | Supermärkte, Elektronikketten, Betreibershops, einige Flughäfen |

Die Reibung ist nicht der Papierkram selbst, sondern die Abfolge. Die Verifizierung kann Stunden dauern, Läden haben deutsche Sonntagsöffnungszeiten, und eine späte Ankunft kann dich bis zum nächsten Morgen ohne Daten lassen. Eine Reise-eSIM entfernt diese Abhängigkeit und kostet dafür mehr pro Gigabyte — den Kompromiss, den die meisten Kurzzeitbesucher gern eingehen.

## Was du auf deinem Gerät prüfen solltest vor einer deutschen 5G-Reise

Alle drei deutschen Betreiber betreiben kommerzielles 5G, und jedes deutsche Betreiberprofil, das wir erfassen, listet es, es gibt also keine reine 4G-Falle, in die du tappen könntest. Opensignal maß den 5G-Download von Telekom im November 2025 mit 173,8 Mbit/s, deutlich vor Vodafone mit 154,3 und O2 mit 114,5 — echter Durchsatz und kein Marketing-Etikett.

Das macht 5G zu einem schlechten Grund, in Deutschland mehr zu zahlen. Die Prüfungen, die wirklich zählen, sind enger. Listet der Tarif 5G. Deckt dein Gerät die deutschen Bänder ab. Und kann es überhaupt VoLTE-Anrufe führen, denn Deutschland hat seinen 3G-Abbau bereits abgeschlossen, und ein Telefon ohne VoLTE registriert sich schlicht nicht im Netz. Ein eSIM-Profil reist mit deinem Gerät statt mit dem SIM-Fach, was praktisch ist, doch die Funkunterstützung ist eine Eigenschaft des Geräts — den zugrunde liegenden Standard dokumentiert die [GSMA](https://www.gsma.com/esim/). Führe dein Modell durch den [Telefon-Kompatibilitätsprüfer](/de/guides/esim-compatibility-check/), bevor du reist.

Darüber hinaus geht es auf dem deutschen Markt darum, wohin du fährst, statt darum, was du kaufst. Städtisches 5G ist reichlich und auf allen drei Netzen schnell, und auf den ländlichen Routen setzt sich Telekom ab. Aktuelle Rabatte findest du in den [eSIM-Angeboten, die wir erfassen](/de/esim-deals/), und der [Reisekosten-Rechner](/de/tools/) dimensioniert ein Kontingent auf deine Daten.

Ein letztes Paar Prüfungen, bevor du dich festlegst. Deutsches Spektrum wird national lizenziert, weshalb sich die genutzten Bänder von denen in Nordamerika unterscheiden und weshalb ein importiertes Gerät sich hier anders verhalten kann. Auch der Upload-Durchsatz verdient einen Blick, wenn du Fotos senden oder an Videoanrufen teilnehmen willst, da deutsche Netze in erster Linie auf Download abgestimmt sind.
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
