# -*- coding: utf-8 -*-
"""批 C 之二：content/de/guides/{esim-vs-physical-sim,dual-sim-and-esim,esim-compatibility-check}.md

纪律同 _patch_guides_de_1.py：
* bytes 读写、LF 行尾、幂等。
* 标题标点守卫扩展到 front matter 的 h2_answer / h2_facts / h2_next / faq_heading
  （模板把 faq_heading 渲染成 h2、FAQ q 渲染成 h3）+ body 的 h2/h3。
* 站内链一律 /de/ 前缀。
"""
import pathlib
import re
import sys

ROOT = pathlib.Path(".")

TODO = "# TODO(de)：分层发布 —— 全站德语译文解禁（D9 那一轮）时删掉上面这行。"

VS = '''---
title: "eSIM oder physische SIM: Was gewinnt auf Reisen 2026"
hero: "travel-esim-illustration-058.webp"
hero_alt: "Eine Reisende wiegt vor einer Auslandsreise eine physische SIM-Karte gegen eine eSIM ab"
date: 2026-10-01
description: "eSIM oder physische SIM auf Reisen? eSIM Sift vergleicht Preis, Einrichtungszeit, Nummernerhalt und Sicherheit — einschließlich der Fälle, in denen eine lokale SIM noch gewinnt."
faq_heading: "Solltest du im Ausland eine eSIM oder eine physische SIM nutzen"
prompt_answer: "Eine eSIM und eine physische SIM liefern dasselbe Netz und dieselbe Geschwindigkeit, weil beide sich beim selben Betreiber einbuchen. Was sich unterscheidet, sind Form und Zeitpunkt. Eine physische SIM ist eine Karte, die du wechselst, während eine eSIM ein Profil ist, das du vor der Reise installierst und parallel zu deiner Heimatleitung laufen lassen kannst — und eine physische SIM gewinnt weiterhin bei netzgesperrten Smartphones und dort, wo ein lokales Prepaid-Angebot jede eSIM-Marke unterbietet."
h2_answer: "Welche Variante kurz gesagt gewinnt"
h2_facts: "Fakten zu eSIM gegen physische SIM"
facts:
  - label: "Netz und Geschwindigkeit"
    value: "Identisch, weil beide beim selben Betreiber fahren"
  - label: "Einrichtungszeit"
    value: "Eine eSIM braucht Minuten, eine physische SIM einen Laden oder eine Lieferung"
  - label: "Heimatnummer"
    value: "Eine eSIM lässt den physischen Schacht frei um sie aktiv zu halten"
  - label: "Wo eine physische SIM noch gewinnt"
    value: "Netzgesperrte Geräte, Umzug einer Leitung zwischen Smartphones, manche lokalen Prepaid-Angebote"
h2_next: "Wähle dein Format und mach weiter"
noindex: true
{TODO}
faqs:
  - q: "Ist eine eSIM im Ausland günstiger als eine physische SIM?"
    a: "Im Vergleich mit SIM-Schaltern am Flughafen und in Touristengebieten fast immer — Online-Preise für eSIMs sind ausgezeichnet und vergleichbar, während Schalterpreise kosten, was der Markt an dem Tag hergibt. Im Vergleich zum Kauf einer lokalen SIM in einem offiziellen Ladengeschäft des Betreibers in der Innenstadt können die Preise nah beieinanderliegen; der Vorteil der eSIM ist, weniger Zeit zu zahlen, nicht unbedingt weniger Dollar."
  - q: "Kann ich eine physische SIM und eine eSIM gleichzeitig nutzen?"
    a: "Eine physische SIM und eine eSIM können auf jedem Smartphone mit eSIM-Unterstützung gleichzeitig laufen. Die typische Reise-Einrichtung hält die heimische physische SIM für Nummer und SMS aktiv, während die eSIM alle Daten im Ausland trägt. Unser Dual-SIM-Ratgeber geht die genauen Einstellungen durch, einschließlich der Roaming-Schalter, die entscheiden, welche Leitung Daten nutzen darf."
  - q: "Verkaufen Flughäfen eSIMs?"
    a: "Einige Flughafenkioske drucken inzwischen eSIM-QR-Codes, aber zu denselben aufgeschlagenen Schalterpreisen wie ihre physischen Karten — du bekommst den Komfort der eSIM ohne ihren Hauptvorteil, nämlich echte Preise online zu vergleichen, bevor du kaufst. Beim Kauf auf der Website oder in der App des Anbieters vor der Abreise liegt die Ersparnis."
  - q: "Kann ich meine Rufnummer mit einer eSIM behalten?"
    a: "Mit einer Reise-eSIM bleibt deine Heimatnummer auf ihrer bestehenden physischen SIM am Leben — du verschiebst sie nirgendwohin. Deine Hauptleitung selbst auf eine eSIM umzustellen, also deine Nummer umzuwandeln, ist ein anderer Vorgang, den du mit deinem Heimanbieter machst, und nicht das, was Anbieter von Reise-eSIMs verkaufen."
  - q: "Unterstützen Reise-eSIMs 5G?"
    a: "Viele bleiben selbst in Ländern mit breiter 5G-Abdeckung bei 4G LTE, während lokale SIMs 5G-Zugang häufig ohne Aufpreis enthalten. Der Unterschied ist für Karten, Nachrichten und Streaming selten wichtig, aber wenn du Spitzengeschwindigkeiten brauchst, prüfe die Netzdetails des Tarifs vor dem Kauf — die Abdeckungsliste nennt meist die maximale Technik."
  - q: "Gibt es eine eSIM die in mehreren Ländern funktioniert?"
    a: "Mehrländer-eSIMs existieren als regionale Tarife und decken Gruppen benachbarter Länder ab — Europa oder Südostasien zum Beispiel — mit einem Profil und einem gemeinsamen Datenpool über alle. Sie tauschen etwas Preis-Leistung pro Gigabyte gegen die Bequemlichkeit des Grenzübertritts, also vergleiche für eine Zwei-Länder-Reise den regionalen Tarif gegen zwei Ein-Länder-Tarife, bevor du wählst."
  - q: "Solltest du eine eSIM nach dem Ablauf löschen?"
    a: "Ein altes eSIM-Profil zu löschen ist völlig optional. Ein abgelaufenes Profil ist inaktiv — es enthält keine persönlichen Daten und verbraucht nichts — es zu behalten kostet also nur einen Platz im Profilspeicher des Smartphones. Es zu löschen ist ebenfalls völlig sicher und gibt einen Platz frei, wenn du oft installierst, und es beeinflusst nie Erstattungen oder die Kaufaufzeichnung des Anbieters."
---

Die ehrliche Antwort ist, dass jede in anderen Situationen gewinnt — aber die Situationen sind nicht symmetrisch. Für kurze Reisen, datenorientierte Reisende und alle, die zu unchristlichen Zeiten landen, gewinnt die eSIM auf fast jeder wichtigen Achse. Für lange Aufenthalte, lokale Nummern und datenintensive Wohnsitze hält die physische SIM noch stand. Alles Folgende gilt für Reise-eSIMs, die vor der Abreise online gekauft werden — das ist die Produktkategorie, die tatsächlich mit lokalen SIMs konkurriert. Hier ist der Vergleich ohne Marketing.

## Was sich zwischen eSIM und physischer SIM tatsächlich unterscheidet

Funktional nichts: Beide halten die Kennung, die deine Leitung in einem Netz registriert, und beide verbinden sich mit denselben Türmen bei denselben Geschwindigkeiten. Eine Reise-eSIM fährt über die Partnerschaften des Anbieters in lokalen Netzen — weshalb Abdeckung und Geschwindigkeit im selben Netz mit einer lokalen SIM identisch sind. Die echten Unterschiede drehen sich alle um die Kennung selbst: wie sie gekauft wird, wie sie geliefert wird, wann sie aktiviert, wie sie ersetzt wird und was sie auf jeder Marktebene kostet. Ist das Konzept selbst neu für dich, erklärt der [eSIM-Grundlagen-Ratgeber](/de/guides/what-is-an-esim/), was eine eSIM tatsächlich ist; dieser Artikel behandelt strikt die Kompromisse gegenüber Plastik.

## Preisvergleich eSIM gegen physische SIM

Auf jeder Destination gibt es drei Preisebenen, und wer sie verwechselt, zahlt zu viel:

- **Schalter am Flughafen und in Touristengebieten** — die teuerste Ebene, bepreist für Dringlichkeit und gefangene Kunden. Mit dieser Ebene vergleicht sich das Marketing der Reise-eSIMs, und der Vergleich ist fair: Online-Preise sind ausgezeichnet, überprüfbar und für dieselben Netze regelmäßig ein Bruchteil der Schalterpreise.
- **Offizielle Ladengeschäfte der Betreiber in der Innenstadt** — echt wettbewerbsfähig, bei großen lokalen Paketen manchmal günstiger, aber mit Zeit und Papierkram bezahlt: den Laden finden, anstehen und in vielen Ländern die SIM vor dem ersten Betrieb gegen den Pass registrieren.
- **Online-Anbieter von eSIMs** — ausgezeichnete Preise, vergleichbar über die {{< count-providers >}} Anbieter, die wir erfassen, bevor du etwas kaufst. Die [Ländervergleiche](/de/compare/) stellen die Tarife jedes Anbieters nebeneinander, und der [Preisindex](/de/research/esim-price-index/) sortiert die {{< count-countries >}} Reiseziele, die wir erfassen, nach dem besten Preis pro Gigabyte.

Die praktische Lehre ist einfach. Eine online gekaufte eSIM konkurriert mit der dritten Ebene und schlägt die erste; eine im Betreiberladen gekaufte lokale SIM konkurriert beim Preis, verliert aber bei der Zeit. Was die Preisdatenbank von eSIM Sift hinzufügt, ist die Möglichkeit, diesen Satz für deine konkrete Destination zu prüfen, bevor du dich festlegst — die Live-Tabelle auf dieser Seite zeigt die günstigsten Einstiegstarife, die wir derzeit erfassen, also die Untergrenze, die jeder physische Schalter schlagen muss.

## eSIM gegen physische SIM auf einen Blick

Die ganze Entscheidung, in einer Tabelle verdichtet:

| | Reise-eSIM | Lokale physische SIM |
|---|---|---|
| Wo du kaufst | Online vor der Abreise | Schalter oder Laden nach der Landung |
| Lieferung | Sofortiger QR-Code | Plastikkarte in der Hand |
| Zeit bis zu funktionierenden Daten | Minuten nach der Landung | Erst Schlangen und Registrierung |
| Deine Heimatnummer | Bleibt aktiv in ihrem Schacht | Meist entfernt oder deaktiviert |
| Lokale Rufnummer | Selten enthalten | Mit Prepaid-Guthaben enthalten |
| Ersatz bei verlorenem Smartphone | Anbieter stellt das Profil neu aus | Neue Karte erneut kaufen |
| Mehrländer-Reisen | Ein Tarif oder gestapelte Profile | Neue Karte an jeder Grenze |

## Einrichtungszeit am Flughafen im Vergleich

Physische SIM nach der Landung: Schalter finden oder den Laden in der Innenstadt, anstehen, möglicherweise die Karte gegen den Pass registrieren, die heimische SIM herausnehmen, die neue einsetzen und hoffen, dass das Personal den APN richtig einstellt. Realistisch sind das 30 bis 90 Minuten deines ersten Tages, drinnen verbracht und oft in einer Schlange, die im Jetlag-Tempo vorankommt.

eSIM: vor der Abreise zu Hause gekauft und installiert, aktiviert sie sich von selbst, wenn das Smartphone erstmals das Netz der Destination sieht. Die [Installationsanleitung](/de/guides/how-to-install-esim/) dauert etwa fünf Minuten, größtenteils Warten auf einen QR-Scan. Deine erste Stunde am Reiseziel verbringst du draußen vor dem Flughafen, nicht darin — was bei Nachtflügen und späten Ankünften am wichtigsten ist, wenn die Läden geschlossen sind und die Flughafenschalter ihre schärfsten Aufschläge verlangen.

## Sind Abdeckung oder Geschwindigkeit bei einer eSIM anders

Ein eSIM-Profil und eine physische SIM im selben Netz liefern identische Abdeckung und identische Geschwindigkeiten, es gibt also keine „eSIM-Steuer" auf die Funkverbindung. Zwei Vorbehalte halten diese Aussage ehrlich.

### Das Partnernetz entscheidet über dein Signal

Eine Reise-eSIM bucht sich in die lokalen Netze ein, die ihr Anbieter vertraglich gebunden hat — manchmal der stärkste Betreiber des Landes, manchmal nur einer oder zwei von mehreren. Wirf vor dem Kauf einen Blick darauf, welche Netze der Tarif an deinem Reiseziel nutzt; diese Wahl, nicht die eSIM-Technik, entscheidet, ob du in den Bergen oder nur in den Städten Empfang hast. Eine im eigenen Laden eines Betreibers gekaufte lokale SIM nutzt immer dessen volle Netzabdeckung, was sie in ländlichen Gebieten gelegentlich zur besseren Wahl macht.

### Die Geschwindigkeitsgrenze von Reise-eSIMs

Viele Reise-eSIMs enden bei 4G LTE, selbst in Ländern mit breiter 5G-Abdeckung, während lokale SIMs 5G-Zugang häufig ohne Aufpreis enthalten. Für Karten, Nachrichten, Musik und HD-Streaming ist LTE mehr als genug — aber wenn deine Arbeit Spitzendurchsatz braucht oder du einfach die Obergrenze wichtig findest, prüfe die Netzdetails des Tarifs und behandle eine lokale SIM mit 5G als die sicherere Annahme.

## Nummer behalten und SMS im Ausland empfangen

eSIM und physische SIM gehen am stärksten dort auseinander, was mit deiner Heimatnummer passiert:

- **Reise-eSIM:** Deine heimische SIM bleibt in ihrem Schacht, deine Nummer empfängt weiter kostenlos SMS, während Daten über die eSIM laufen. Zwei Leitungen gleichzeitig sind genau die Einrichtung aus dem [Dual-SIM-Ratgeber](/de/guides/dual-sim-and-esim/).
- **Physische lokale SIM:** Deine heimische SIM kommt meist heraus oder wird deaktiviert, um Roaming-Gebühren zu vermeiden, und mit ihr die SMS deiner Nummer. Verifizierungscodes der Bank kommen unterwegs nicht mehr an — die klassische Krise am dritten Tag — es sei denn, du hast das Roaming auf der Heimatleitung aktiv gelassen und zahlst, was es kostet.

Ist eine lokale Nummer mit lokalem Telefonguthaben das eigentliche Ziel, liefert das nur die physische SIM. Reise-eSIMs sind datenorientierte Produkte, Punkt — wenige können SMS empfangen und noch weniger telefonieren, aber keine gibt dir eine lokale Nummer, die Einheimische anrufen können.

## Wie Mehrländer-Reisen die Rechnung ändern

Jeder Grenzübertritt ist dort, wo physische SIMs Zeit und Geld verlieren. Die Plastikroutine wiederholt sich pro Land — Laden finden, anstehen, registrieren, wechseln — und jeder Wechsel lässt das restliche Prepaid-Guthaben der vorigen Karte verfallen, da lokales Guthaben im Ausland fast nie funktioniert. Auf einer Vier-Länder-Reise sind das vier Schlangen, vier Registrierungen und vier sterbende Guthaben.

Die eSIM-Alternativen sind sauberer:

- **Regionale Tarife** decken eine Gruppe von Ländern mit einem Profil und einem gemeinsamen Datenpool ab — ein Europa-Tarif trägt dich von einer [Italien-eSIM](/de/compare/italy/)-Route direkt in [Griechenland-eSIM](/de/compare/greece/)-Gebiet, ohne an der Grenze etwas zu ändern. Die großen Anbieter verkaufen sie alle — die [Airalo-Bewertung](/de/esim-providers/airalo/) behandelt deren regionale Produkte — und sie tauschen etwas Preis-Leistung pro Gigabyte gegen das Nie-mehr-an-Grenzen-Denken.
- **Gestapelte Länder-Tarife** nehmen den anderen Weg — installiere vor der Abreise ein separates Ein-Länder-Profil pro Stopp und aktiviere jedes bei der Landung. Smartphones speichern mehrere Profile gleichzeitig, also reisen drei Länder ab Tag eins im Gerät mit.

Welcher der beiden günstiger ist, hängt von der Route ab: Regionale Tarife gewinnen bei Bequemlichkeit und oft beim Preis für verstreute kurze Stopps, während gezielte Ein-Länder-Tarife meist bei der Preis-Leistung pro Gigabyte gewinnen, wenn du an jedem Ort echte Zeit verbringst. Die Länderseiten machen diesen Vergleich direkt.

## Sicherheit und Ersatz bei Verlust oder Defekt

### Warum eine eSIM schwerer zu stehlen ist

Eine physische SIM lässt sich in Sekunden zwischen Smartphones verschieben — bequem für dich und ebenso bequem für einen Dieb. Ein eSIM-Profil lässt sich nicht still übertragen; es bindet sich nur über den Anbieter neu, was ein echter Sicherheitsvorteil für die Kennung selbst ist und der Grund, warum Netzbetreiber Vertragsleitungen zunehmend als eSIM ausgeben.

### Ersatz wenn das Smartphone weg ist

Der Ersatz einer eSIM schneidet in die andere Richtung, und es ist die eine Stelle, an der eine Plastikkarte klar gewinnt. Verlierst du das Smartphone, braucht es eine Neuausstellung durch den Anbieter — QR-Codes sind einmalig und Profile binden sich an das erste Gerät — während eine Ersatzkarte aus Plastik in deiner Geldbörse sofort in jedem entsperrten Smartphone funktioniert, ohne Support-Chat. Häufige Aufrüster sollten dieselbe Bindung beachten: ein Gerätewechsel mitten auf der Reise bedeutet eine Neuausstellung, kein erneutes Scannen, und während die meisten Anbieter Neuausstellungen schnell erledigen, tun es nicht alle sofort oder kostenlos.

## Schlägt eine physische SIM eine eSIM noch irgendwo

Eine physische SIM schlägt eine eSIM noch in drei Fällen:

1. **Lange Aufenthalte.** Ein lokales Prepaid über einen Monat oder mehr schlägt oft das Stapeln von Reise-eSIMs; die Ladenschlange amortisiert sich über Wochen statt Tage, und lokale Pakete sind für lokale Bedürfnisse bemessen, nicht für Touristenreisen.
2. **Eine lokale anrufbare Nummer.** Vermieter, Restaurants, Lieferungen, lokale Registrierungen — nur eine lokale SIM mit Guthaben gibt dir eine Nummer, die Menschen im Land tatsächlich anrufen können.
3. **Nicht unterstützte oder gesperrte Geräte.** Smartphones ohne eSIM-Hardware oder noch netzgesperrt haben keine Wahl — der [Kompatibilitäts-Check](/de/guides/esim-compatibility-check/) klärt deines in 30 Sekunden.

## Welche solltest du wählen

Zwei Reisendenprofile decken die meisten Entscheidungen ab, und fast jede Reise fällt in eines davon.

### Der Kurzreisende

Ein Wochenende bis etwa ein Monat datenorientierter Reisen, oft über mehr als ein Land, deutet auf eine online vor der Abreise gekaufte eSIM. Der [Reisekostenrechner](/de/tools/) passt ein Datenvolumen an deine Daten und Gewohnheiten an, und die aktuellen [eSIM-Angebote](/de/esim-deals/) zeigen, wo Anbieter gerade rabattieren. Du landest verbunden, behältst deine Heimatnummer für Codes und stehst nie für Konnektivität an.

### Der Langzeitreisende

Ein Monat oder mehr an einem Ort, mit Bedarf nach einer lokalen Nummer oder wirklich schweren Daten, deutet auf eine lokale SIM aus einem offiziellen Betreiberladen. Sie kostet eine Schlange und bezahlt sich an jedem Tag danach selbst, und die lokale Nummer wird Teil des Alltags statt ein Behelf.

Wenn du den eSIM-Weg gehst, behandeln die [Anbieterbewertungen](/de/esim-providers/), wie jede Marke Neuausstellungen, Fair Use und App-Qualität handhabt — die Unterschiede, die nach dem Kauf auftauchen, wenn es zu spät ist, Preise zu vergleichen.
'''

DUAL = '''---
title: "Dual-SIM mit eSIM: Heimatnummer im Ausland behalten"
hero: "travel-esim-illustration-018.webp"
hero_alt: "Eine Reisende steigt ins Flugzeug, während sie ein Smartphone nutzt, das gleichzeitig eine Heimatnummer und eine Reise-eSIM betreibt"
date: 2026-10-01
description: "So funktioniert Dual-SIM mit einer eSIM plus einer physischen SIM: eSIM Sift erklärt, wie du deine Heimatnummer behältst, während die eSIM Daten trägt."
faq_heading: "Ist Dual-SIM mit einer eSIM das Richtige für dich"
prompt_answer: "Dual-SIM lässt ein Smartphone zwei Leitungen gleichzeitig betreiben, und die übliche Reise-Einrichtung ist eine physische SIM mit deiner Heimatnummer plus eine eSIM mit lokalen Daten. Anrufe und SMS kommen weiter auf der Heimatnummer an, während mobile Daten über die eSIM laufen — vorausgesetzt du setzt die eSIM als Datenleitung und lässt das Daten-Roaming auf der Heimatleitung aus."
h2_answer: "Die Dual-SIM-Einrichtung fürs Ausland"
h2_facts: "Fakten zu Dual-SIM und eSIM"
facts:
  - label: "Übliche Reise-Einrichtung"
    value: "Heimatnummer auf der physischen SIM, Reisedaten auf der eSIM"
  - label: "Die entscheidende Einstellung"
    value: "Die eSIM als Leitung für mobile Daten setzen"
  - label: "Was du ausschaltest"
    value: "Daten-Roaming auf der Heimatleitung"
  - label: "Was weiter funktioniert"
    value: "Anrufe und SMS auf der Heimatnummer"
  - label: "Zwei eSIMs gleichzeitig"
    value: "Unterstützt auf aktuellen iPhones und vielen aktuellen Android-Geräten"
h2_next: "Schließe die Dual-SIM-Einrichtung ab"
noindex: true
{TODO}
faqs:
  - q: "Empfange ich SMS auf der heimischen SIM weiter?"
    a: "Ja, solange die Heimatleitung im physischen Schacht aktiv bleibt. SMS auf deiner Heimatnummer kommen weiter normal an, während die eSIM Daten trägt, und genau deshalb schlägt die Dual-SIM-Einrichtung das Kartenwechseln — deine Bank- und App-Verifizierungscodes kommen weiter an."
  - q: "Entlädt Dual-SIM den Akku schneller?"
    a: "Dual-SIM entlädt den Akku tatsächlich etwas schneller. Zwei aktive Funkmodule bedeuten einen etwas höheren Ruheverbrauch als eines, wobei moderne Smartphones das gut bewältigen. Der praktische Tipp: Wenn du die Anrufe deiner Heimatleitung im Ausland nicht brauchst, kannst du sie ganz ausschalten und nur ihre SMS ankommen lassen — oder beide anlassen und ein paar Prozent pro Tag akzeptieren."
  - q: "Kann ich zwei eSIMs gleichzeitig aktiv haben?"
    a: "Auf aktuellen iPhones (13 und neuer) und vielen aktuellen Android-Geräten ja — zwei eSIM-Leitungen können gleichzeitig aktiv sein, mit oder ohne physische SIM. Bei älteren Dual-SIM-Smartphones ist eine eSIM plus die physische SIM die funktionierende Kombination. Prüfe dein Modell in unserem Kompatibilitäts-Ratgeber."
  - q: "Was passiert bei Daten-Roaming auf beiden Leitungen"
    a: "Das Smartphone nutzt Daten über die Leitung, die als Datenleitung gesetzt ist, aber Roaming-Gebühren folgen den Regeln jeder Leitung. Das sichere Muster im Ausland: Datenleitung auf die eSIM gesetzt, Daten-Roaming AN nur für die eSIM, und Daten-Roaming AUS für die Heimatleitung, damit sie sich nie still in ein ausländisches Netz einbuchen kann."
  - q: "Welche Leitung empfängt meine Bank-Verifizierungscodes auf Reisen?"
    a: "Die Leitung, die deine Bank gespeichert hat, empfängt die Codes. Für die meisten Menschen ist das die Heimatnummer, die weiter SMS empfängt, solange die heimische SIM in ihrem Schacht aktiv bleibt. Wenn du einem Dienst je die Nummer der eSIM gegeben hast, empfängt stattdessen diese Leitung die Codes, wisse also vor dem Flug, welche Nummer jedes Konto nutzt."
  - q: "Kann ich meine Heimatleitung auf Reisen aus- und wieder einschalten?"
    a: "Die Heimatleitung auf Reisen aus- und wieder einzuschalten ist sicher und zerstörungsfrei. Eine Leitung auszuschalten stoppt einfach ihre Registrierung; die SIM oder das Profil bleibt installiert, und die Leitung kehrt zurück, sobald du sie wieder einschaltest. Es ist der sauberste Akkusparer an datenintensiven Tagen, und SMS kommen wieder an, wann immer du sie brauchst."
  - q: "Funktioniert 5G auf beiden Leitungen gleichzeitig?"
    a: "Auf den meisten aktuellen Smartphones verankert die für Daten gesetzte Leitung die 5G-Verbindung, und die zweite Leitung liegt auf 4G oder im Standby, was für Anrufe und SMS in Ordnung ist. Die eSIM kann im Ausland 5G fahren, wo ihre Partnernetze es senden. Die Heimatleitung braucht kein 5G, um Anrufe und SMS weiter zu empfangen."
---

Dual-SIM ist die Funktion, die Reise-eSIMs schmerzlos macht: dein Smartphone hält zwei Leitungen gleichzeitig — die heimische SIM, die du schon hast, und die Reise-eSIM mit günstigen lokalen Daten. Anrufe und SMS kommen weiter auf deiner Nummer an; Karten und Streaming laufen über die eSIM; und niemand wechselt eine physische Karte an einem Flughafenschalter.

Dieser Ratgeber geht die Einrichtung zwei Leitungen ein Smartphone von Anfang bis Ende durch: wie die Funkmodule die Arbeit tatsächlich teilen, die dreischrittige Konfiguration, die Schockrechnungen verhindert, und die Teile, die die meisten Anleitungen auslassen — welche Leitung iMessage und WhatsApp trägt, was WLAN-Anrufe im Ausland wirklich tun, und drei echte Schockrechnungs-Szenarien, zurückverfolgt bis zu dem einen Schalter, der jedes verhindert. Neu bei eSIMs allgemein? Beginne mit den [eSIM-Grundlagen](/de/guides/what-is-an-esim/).

## Wie Dual-SIM mit einer eSIM und einer physischen SIM funktioniert

Moderne Smartphones laufen im Dual-SIM-Dual-Standby: Beide Leitungen sind gleichzeitig im Netz registriert, und das Smartphone leitet jedes Ereignis nach Regeln, die du setzt — welche Leitung abgehende Anrufe macht, welche sie empfängt und welche Daten trägt. Die übliche Reiseaufteilung:

- **Heimatleitung (physische SIM):** aktiv, in ihrem Schacht, tut was sie immer tat — empfängt Anrufe und SMS auf deiner Nummer.
- **Reiseleitung (eSIM):** vor der Abreise installiert, trägt alle mobilen Daten im Ausland zu lokalen eSIM-Preisen.

Das entscheidende Denkmodell: *Daten* sind ein Schalter (eine Leitung zur Zeit), *Anrufe und SMS* sind pro Leitung (beide arbeiten weiter). An der heimischen SIM ändert sich nichts außer einer Einstellung, die du gleich ausschaltest.

Das Wort *Standby* verdient einen Moment, denn es erklärt eine Eigenheit, die Reisende bemerken. Dual-Standby bedeutet, dass jede Leitung erreichbar ist, aber auf den meisten Geräten sendet nur ein Funkmodul zur Zeit — nimmst du einen Anruf auf der Heimatleitung an, pausieren die Daten der eSIM für die Dauer. Einige wenige aktuelle Flaggschiffe schaffen gleichzeitige Daten auf zwei Leitungen, aber das ändert hier nichts, weil du ohnehin eine Leitung für Daten setzt.

## Welche iPhones und Androids Dual-SIM mit eSIM unterstützen

Praktisch jedes Smartphone mit eSIM-Unterstützung kann Dual-SIM — die Funktionspaare kommen zusammen. iPhone XR und XS und neuer (mit regionalen Ausnahmen für Modelle aus dem chinesischen Festland), Google Pixel ab dem 3, Samsung Galaxy S20 und neuer (US-Varianten eingeschlossen) und die meisten aktuellen Flaggschiffe von Motorola, Xiaomi und anderen. US-iPhones ab dem 14 kommen ganz ohne physischen Schacht, was die eSIM zur Standard-Zweitleitung macht statt zur Option.

Marketingnamen variieren — Apple sagt Dual-SIM, Samsung sagt Dual-Standby oder eSIM plus SIM — aber die Fähigkeit, nach der du suchst, ist dieselbe: eine EID aus dem Wählertest und ein zweiter Leitungsschacht in den Einstellungen. Der 30-Sekunden-`*#06#`-EID-Test in unserem [Kompatibilitäts-Check](/de/guides/esim-compatibility-check/) klärt dein konkretes Gerät. Aktuelle iPhones können zwei eSIM-Leitungen gleichzeitig ohne physische Karte fahren; auf den meisten aktuellen Android-Geräten ist eine eSIM plus die physische SIM die funktionierende Kombination, wobei zusätzliche Profile gespeichert aber inaktiv bleiben.

## So hältst du deine Heimatnummer bei eSIM-Daten aktiv

Die Einrichtung dauert eine Minute und wird am besten vor der Abreise erledigt:

1. **Setze die Datenleitung auf die eSIM.** Auf dem iPhone: *Einstellungen → Mobilfunk → Mobilfunkdaten*, dann die eSIM wählen. Auf Android: *Einstellungen → Netzwerk und Internet → SIMs → Mobile Daten*, dann die eSIM.
2. **Schalte Daten-Roaming nur für die eSIM-Leitung ein.** Das ist der Schalter, der die eSIM ausländische Partnernetze nutzen lässt. Ohne ihn zeigt die eSIM Signal und lädt nichts.
3. **Schalte Daten-Roaming für deine Heimatleitung aus.** Das ist der Schalter gegen Schockrechnungen. Ausgeschaltet kann die Heimatleitung im Ausland Anrufe und SMS empfangen, aber nie still Roaming-Daten verbrennen.

Das zu Hause zu tun ist wichtig: Jeder Schalter liegt in einem Menü, das du auf dem Sofa in Ruhe findest, und die Konfiguration übersteht den Flug unverändert. In der Ankunftshalle bleibt nichts mehr zu konfigurieren außer der Flugmodus.

Lass die Heimatleitung als Standard für abgehende Anrufe, oder setze die eSIM, wenn dein Tarif Anrufe enthält — die meisten Reise-eSIMs sind reine Datentarife, und ob eine Marke überhaupt Sprache anbietet, gehört zu ihrem Eintrag in den [Anbieterbewertungen](/de/esim-providers/). Ist die eSIM noch nicht installiert, deckt die [Installationsanleitung](/de/guides/how-to-install-esim/) diese Hälfte ab; der Rest dieser Seite setzt voraus, dass beide Leitungen auf dem Smartphone sind.

## Wie Anrufe und Nachrichten auf zwei Leitungen funktionieren

Jede Leitung hat ihre eigene Nummer, ihren eigenen Tarif und ihre eigene Mailbox. Was Menschen stolpern lässt, ist nur das Routing — welche Leitung das Smartphone wofür wählt.

### Welche Leitung deine abgehenden Anrufe macht

**Abgehende Anrufe** gehen über die Leitung, die Standard ist. Auf dem iPhone kannst du die Leitung pro Anruf im Wähler wechseln, und beide Plattformen lassen dich eine bevorzugte Leitung pro Kontakt setzen — das Hotel auf der eSIM, die Familie auf der Heimatleitung.

### Welche Leitung deine SMS nutzt

**SMS** gehen über die Leitung, die du wählst; das iPhone fragt, mit welcher Leitung neue Unterhaltungen beginnen sollen, und merkt sich das pro Kontakt. Eine weitere Routing-Regel ist wichtig: Antworten bleiben auf der Leitung, auf der die Unterhaltung begann, also wird ein Thread, der auf der Heimatleitung startete, sein ganzes Leben lang als Heimatleitung abgerechnet.

### Wie WhatsApp und iMessage eine Leitung wählen

Messaging-Apps sind der Teil, den die meisten Anleitungen auslassen. iMessage, WhatsApp, Telegram und jede andere ignorieren die Telefonleitung völlig und fahren über die Leitung, die Daten trägt. Im Ausland ist das per Design die eSIM. WhatsApp funktioniert genau wie zu Hause auf deiner registrierten Nummer weiter; die eSIM bewegt seine Bytes, und der Roaming-Status deiner Heimatleitung ist dafür irrelevant. iMessage verhält sich über Daten gleich, mit einer Nuance — Nachrichten an deine Heimatnummer kommen weiter an, weil Apples Server sie routen, aber die einfache grüne SMS einer Freundin an deine Heimatnummer kommt als internationale Textnachricht an, kostenlos zu empfangen bei den meisten Heimanbietern und der Bestätigung bei deinem wert.

Die praktische Lehre: Jeder, der dich über eine App erreicht, erreicht dich über die Daten der eSIM. Nur einfache SMS und gewöhnliche Telefonanrufe berühren die Heimatleitung — und genau dieser Verkehr soll ja ankommen.

## Wie sich WLAN-Anrufe im Ausland verhalten

### Der Trick der WLAN-Anrufe für Dual-SIM-Reisende

WLAN-Anrufe sind eine Funktion des Heimanbieters, die Anrufe und SMS über jede Internetverbindung statt über das Mobilfunknetz leitet. Der Wähler verhält sich normal; das Audio wandert als Daten. Für einen Dual-SIM-Reisenden hat es einen wirklich nützlichen Trick: Im Ausland können die Anrufe der Heimatleitung über die Datenverbindung der eSIM fahren, sodass Menschen, die deine Heimatnummer wählen, dich ohne Roaming-Sprachgebühren erreichen — der Anruf berührt nie einen ausländischen Mobilfunkmast.

### Warum die Abrechnung von WLAN-Anrufen unvorhersehbar ist

Die Abrechnungspolitik ist der Haken, und sie variiert nach Anbieter statt nach Smartphone. Manche Anbieter behandeln WLAN-Anrufe aus einem ausländischen Netz trotzdem als Roaming, manche beschränken sie auf Anrufe in dein Heimatland, und wenige deaktivieren sie im Ausland ganz. Zu Hause sieht es kostenlos aus und verhält sich im Ausland anders, also prüfe es bei deinem Anbieter, bevor du dich darauf verlässt. Aktiviere es vor der Abreise — auf dem iPhone unter *Einstellungen → Mobilfunk →* deine Heimatleitung → *WLAN-Anrufe*, auf Android in den Einstellungen dieser SIM auf den meisten Oberflächen — und führe einen Testanruf, solange du noch auf heimischem Boden bist. Ein Sicherheitshinweis: Notrufe können mit aktiven WLAN-Anrufen anders geroutet werden, also prüfe, wie dein Anbieter sie an deinem Zielort handhabt.

## Die Daten-Roaming-Einstellungen erklärt

Die zwei Roaming-Schalter haben unterschiedliche Aufgaben und werden ständig verwechselt:

- **Daten-Roaming (eSIM-Leitung): im Ausland an.** Die Partnernetze der eSIM sind ausländische Netze; ohne diesen Schalter kann sie sie überhaupt nicht nutzen.
- **Daten-Roaming (Heimatleitung): im Ausland immer aus.** Die Roaming-Tarife deines Heimanbieters gelten, sobald die Heimatleitung ausländische Daten nutzt. Aus heißt aus — Anrufe und eingehende SMS funktionieren weiter.

### Die Falle der automatischen Netzwahl

Die **automatische** Netzwahl kann eine Leitung beim falschen Partner parken. Verbindet sich die eSIM, kriecht aber, stelle ihre Auswahl auf manuell und wähle aus der Partnerliste auf der Tarifseite. Derselbe manuelle Trick kontrolliert die Sprachraten der Heimatleitung — Roaming aus stoppt Daten, aber ein angenommener Anruf wird weiter zum Sprachsatz des Partners abgerechnet, und Partner desselben Anbieters können stark abweichen.

## Drei Schockrechnungs-Szenarien und der eine Schalter dagegen

Jede Schockrechnungsgeschichte endet mit einem Schalter, der schon auf dem Smartphone war. Drei der häufigsten:

**Die stille Verbindung.** Das Flugzeug landet, die Heimatleitung registriert sich automatisch bei einem ausländischen Partner deines Heimanbieters, und ein Hintergrund-App-Refresh läuft, bevor du das Gate erreichst. Die Rechnung kommt nächsten Monat. *Verhindert durch* Daten-Roaming **aus** auf der Heimatleitung — eine Leitung mit deaktiviertem Roaming kann sich für Anrufe registrieren, aber kein Byte ausländischer Daten bewegen, es gibt also nichts abzurechnen.

**Der falsche Partner.** Alles ist korrekt konfiguriert, aber die automatische Auswahl parkt die Heimatleitung bei einem Partner, den dein Anbieter zum Spitzensatz abrechnet, und ein fünfminütiger Anruf kostet, was ein Abendessen kosten sollte. *Verhindert durch* die Netzwahl der Heimatleitung auf **manuell** und die Wahl des Partners, den dein Anbieter als bevorzugt nennt, direkt nach der Landung.

**Die zurückgelassene Datenleitung.** Mitten auf der Reise geht die eSIM zur Neige, du schaltest Mobilfunkdaten auf die Heimatleitung, um eine Sache zu prüfen, und vergisst es zwei Tage. *Verhindert durch* die **Datenleitungswahl selbst** — behandle Daten-auf-der-eSIM als geprüften Zustand, und wenn die eSIM zur Neige geht, lade sie auf oder kaufe den nächsten Tarif, statt jedes Megabyte auf Roaming-Raten zu schieben.

## Alle Schalter für vor dem Flug

Jede Dual-SIM-Einstellung, die du vor dem Flug prüfen solltest, passt in eine Tabelle:

| Schalter | Leitung | Setzen auf | Warum |
|---|---|---|---|
| Daten-Roaming | eSIM-Leitung | An | lässt die eSIM Partnernetze nutzen |
| Daten-Roaming | Heimatleitung | Aus | blockiert stille ausländische Datenkosten |
| Mobilfunkdaten | eine davon | eSIM | eine Leitung trägt alle Daten im Ausland |
| Netzwahl | Heimatleitung | Manuell | wählt den günstigeren Roaming-Partner |
| Standard-Sprachleitung | eine davon | Heimatleitung | abgehende Anrufe werden planbar abgerechnet |

Dreißig Sekunden in den Einstellungen, einmal, vor dem Flughafen — und jedes Szenario oben ist bereits tot.

## Fakten zu Dual-SIM bei Akku und Geschwindigkeit

Zwei registrierte Leitungen kosten etwas Standby-Akku — ein paar Prozent pro Tag auf moderner Hardware, selten spürbar neben der Bildschirmzeit am Reisetag. Die Geschwindigkeit ist unberührt: Die Daten der eSIM laufen in denselben lokalen Netzen mit denselben Geschwindigkeiten, die eine lokale SIM bekommen würde, und 5G verankert sich auf den meisten Geräten an der Datenleitung, die eSIM bekommt also volle lokale Geschwindigkeiten, wo Netze sie bieten. Willst du null Verbrauch auf der Heimatleitung, schalte die heimische SIM an datenintensiven Tagen ganz aus und wieder ein, wenn du ihre SMS brauchst — nichts geht verloren und nichts wird neu installiert; es ist ein Schalter.

Bereit, den eSIM-Schacht zu füllen? Die [Vergleichstabelle](/de/compare/) von eSIM Sift listet jeden Anbieter pro Destination — [Italien](/de/compare/italy/), [Japan](/de/compare/japan/) und [Spanien](/de/compare/spain/) zeigen das Layout — oder prüfe in der [Unlimited-Rangliste](/de/research/unlimited-esim/), wo unbegrenzte Daten pro Tag am günstigsten sind, ideal für diese Zwei-Leitungs-Einrichtung. Viel Streaming? Lies zuerst die [Fair-Use-Prüfung](/de/research/fair-use-audit/) — die Drosselungsregel jedes Unlimited-Tarifs wird wörtlich zitiert. Knappes Budget? Der [Preisindex](/de/research/esim-price-index/) verfolgt typische Reisekosten pro Land, und die [aktuellen Angebote](/de/esim-deals/) fassen aktive Rabatte zusammen.
'''

COMPAT = '''---
title: "Ist dein Smartphone eSIM-fähig? Der 30-Sekunden-Check"
description: "Prüfe die eSIM-Kompatibilität in 30 Sekunden: der *#06#-EID-Test, was eine eSIM braucht, warum es keine eSIM-Größe zu messen gibt und die verifizierte Geräteliste."
hero: "travel-esim-illustration-012.webp"
hero_alt: "Eine Lupe über einem Smartphone, das prüft ob das Gerät eSIM unterstützt"
date: 2026-10-01
faq_heading: "Wird dein Smartphone mit einer Reise-eSIM funktionieren"
prompt_answer: "Der 30-Sekunden-Kompatibilitätscheck ist der EID-Test über den Wähler des Smartphones. Wähle *#06# und wenn der Bildschirm eine EID-Nummer zeigt, hat das Smartphone den eSIM-Chip. Die Netzsperre ist der zweite Check, denn ein gesperrtes Gerät kann die Hardware haben und eine Reise-eSIM trotzdem verweigern. Derselbe Modellname kann sich zudem nach Markt unterscheiden, ein in China Festland gekauftes Smartphone oder ein netzgesperrtes US-Gerät verhält sich also anders als dasselbe Modell, das anderswo verkauft wurde."
h2_answer: "Ob dein Smartphone den eSIM-Check besteht"
h2_facts: "Fakten zur eSIM-Kompatibilität"
facts:
  - label: "Der 30-Sekunden-Check"
    value: "Wähle *#06# und suche eine EID-Nummer"
  - label: "Zweiter Check"
    value: "Ob das Smartphone netzgesperrt ist"
  - label: "Gleiches Modell anderer Markt"
    value: "Ja, iPhones aus China Festland kommen ohne eSIM-Hardware"
  - label: "Tablets und Laptops"
    value: "Cellular-Modelle unterstützen eSIM meist, reine WLAN-Modelle nicht"
  - label: "Gebrauchte Smartphones"
    value: "Führe den EID-Test vor dem Kauf aus"
  - label: "eSIM-Kartengröße"
    value: "Keine — der Chip ist eingebettet, es gibt also kein standard-, micro- oder nano-Format zum Abgleichen"
h2_next: "Prüfe den Rest vor dem Kauf"
noindex: true
{TODO}
faqs:
  - q: "Woran erkenne ich eine Netzsperre"
    a: "Auf iOS 14 und neuer öffne Einstellungen, gehe auf Allgemein, dann Info, und scrolle zu Netzbetreibersperre — dort muss Keine SIM-Einschränkungen stehen. Auf Android liegt der Sperrstatus je nach Marke unter Einstellungen in Verbindungen oder Telefoninfo, oder frage einfach den Betreiber. Ein gesperrtes Smartphone verweigert eSIM-Profile Dritter, selbst wenn seine eSIM-Hardware vorhanden ist."
  - q: "Unterstützen in China verkaufte iPhones eSIM?"
    a: "iPhone-Modelle aus China Festland haben keine eSIM-Hardware — sie laufen stattdessen mit zwei physischen SIMs, und das gilt auch für aktuelle Modelle (die iPhone Air ist die eine Ausnahme: sie ist weltweit eSIM-only, China Festland eingeschlossen). Wurde dein Smartphone in China Festland gekauft, gehe unabhängig vom Modelljahr von keiner eSIM-Unterstützung aus. Modelle aus Hongkong kamen historisch ebenfalls mit zwei physischen SIMs, prüfe also mit dem EID-Test, bevor du einen Tarif kaufst."
  - q: "Kann ich eine eSIM auf einem netzgesperrten Smartphone nutzen?"
    a: "Ein netzgesperrtes Smartphone kann eine Reise-eSIM überhaupt nicht nutzen. Die Netzsperre blockiert Profile jedes anderen Anbieters, und Reise-eSIMs sind genau das. Ist das Gerät abbezahlt? Die Entsperrung ist meist eine kostenlose Anfrage beim ursprünglichen Betreiber und wirkt in der Regel innerhalb weniger Tage."
  - q: "Hängt die eSIM-Unterstützung von meinem Heimanbieter ab?"
    a: "Bei Reise-eSIMs nein — das Profil kommt vom Reiseanbieter und registriert sich in ausländischen Partnernetzen, die Meinung deines Heimanbieters spielt also keine Rolle. Wichtig sind Hardware-Unterstützung und ein entsperrtes Gerät. Dein Heimanbieter kommt nur ins Spiel, wenn du deine Hauptleitung selbst auf eine eSIM umstellst, was ein anderer Vorgang ist."
  - q: "Mein Smartphone steht nicht auf der Kompatibilitätsliste. Was nun?"
    a: "Ein Smartphone, das auf einer veröffentlichten Liste fehlt, ist kein Urteil über es. Veröffentlichte Listen — unsere eingeschlossen — hinken neuen Veröffentlichungen hinterher und übersehen regionale Varianten. Wähle *#06# auf dem Smartphone selbst: erscheint neben der IMEI eine EID-Nummer, ist der eSIM-Chip vorhanden und ein Reiseprofil installiert sich. Keine EID bedeutet kein Chip, und der Weg über die physische SIM ist dein Ausweich."
  - q: "Unterstützen Hongkonger Pixel-Smartphones eSIM?"
    a: "Hongkonger Pixel-Smartphones unterstützen eSIM in keinem Modelljahr. Jeder Hongkonger Pixel kommt ohne eSIM-Chip, über alle Modelljahre — die Ausnahme liegt nicht in einer bestimmten Generation, sie ist der ganze Markt. Wurde ein Pixel in Hongkong gekauft, plane den Weg über die physische SIM ein oder ein anderes Gerät."
  - q: "Kann ein älteres Smartphone eSIM später bekommen?"
    a: "Ein älteres Smartphone kann eSIM-Unterstützung nicht nachträglich bekommen. Der eSIM-Chip ist physische Hardware, die bei der Fertigung festgelegt wird — kein Software-Update, kein Betreiberbesuch und keine Reparatur fügt ihn einem Smartphone hinzu, das ohne ihn das Werk verließ. Zeigt *#06# keine EID, wird dieses Gerät nie ein eSIM-Profil aufnehmen."
  - q: "Funktionieren Cellular-iPads mit Reise-eSIMs?"
    a: "Oft ja — Cellular-iPads folgen demselben Profilablauf wie iPhones, also kaufen, scannen und installieren, und viele Reisende nutzen sie im Ausland als reine Datengeräte. Zwei Hinweise — nur WLAN + Cellular-Modelle haben überhaupt ein Modem, und manche Reiseanbieter beschränken Tarife auf Smartphones, also prüfe die Seite zu unterstützten Geräten des Anbieters vor dem Kauf."
  - q: "Gibt es eSIMs in verschiedenen Größen?"
    a: "Nein — eine eSIM hat keine Karte und daher keine Größe. Physische SIMs werden auf standard-, micro- und nano-Maße zugeschnitten, weshalb der Umzug einer alten SIM in ein neueres Smartphone früher einen Adapter oder eine Stanze brauchte. Der eSIM-Chip ist im Gerät eingebettet, es gibt also nichts zu messen und nichts abzugleichen. Kompatibilität hängt davon ab, ob dein Modell den Chip trägt und netzentsperrt ist, und der *#06#-Wählertest klärt beides."
  - q: "Was braucht eine eSIM zum Funktionieren"
    a: "Vier Dinge, und nur das erste ist Hardware. Ein eSIM-fähiges Gerät, ein netzentsperrtes Smartphone, eine EID an die der Anbieter das Profil binden kann, und einen Installationsweg, den dein Smartphone ausführen kann — QR-Code- und Web-Installationen brauchen nichts außer einer Kamera und einer Verbindung, während Anbieter mit App-Weg eine Mindest-OS-Version und eine Kontoregistrierung hinzufügen. Fehlt eines der vier, schlägt die Installation fehl, meist mit einem vagen Aktivierungsfehler statt einem klaren Grund."
---

Dreißig Sekunden entscheiden, ob die Vergleiche dieser Seite für dich gelten: Entweder dein Smartphone hat eSIM-Hardware oder nicht, und entweder ist es netzentsperrt oder nicht. Beide Checks passieren am Gerät selbst — kein Datenblattsuchen nötig. Aber zwei weitere Fallen verstecken sich hinter diesem Wählertest, und sie versenken mehr Reisen als fehlende Hardware je tat: regionale Varianten (derselbe Modellname mit unterschiedlicher Innerei je Markt) und Installationswege der Anbieter, die still eigene Anforderungen hinzufügen. Dieser Ratgeber behandelt alle vier, und die durchsuchbare Liste verifizierter Modelle, die eSIM Sift unten pflegt, klärt den Rest.

## Hat eine eSIM eine Größe

Nein. Die Frage kommt aus der Ära der physischen SIM, als die Karte selbst auf eines von drei Maßen zugeschnitten wurde — standard, micro und nano — und ein Smartphonewechsel bedeutete, zu prüfen welches das neue Gerät aufnimmt, oder eine kleinere Karte aus einer größeren zu stanzen. Eine eSIM hat keine Karte zum Messen, keinen Schacht zum Abgleichen und keinen Adapter zu kaufen: Der Chip sitzt im Gerät und verlässt es nie, eine eSIM passt also per Definition physisch in jedes eSIM-Smartphone.

War die Größe, die du im Kopf hattest, das Datenvolumen statt die Karte, wird sie in Gigabyte gemessen und für jeden Tarif auf jeder [Länderseite](/de/compare/) gelistet. So oder so geht es bei der Kompatibilitätsfrage nicht um Größe — sondern darum, ob dein Modell den Chip überhaupt trägt, was der EID-Test unten in Sekunden klärt.

## So prüfst du ob dein Smartphone eSIM unterstützt

Wähle `*#06#` auf dem Smartphone, mit dem du reist, und der Bildschirm beantwortet die Frage direkt — neben der IMEI zeigt ein eSIM-fähiges Gerät eine **EID**-Nummer. EID vorhanden heißt, der eingebettete SIM-Chip existiert. Das ist der ganze Hardware-Test, und er schlägt jede veröffentlichte Liste aus einem Grund: Der Wähler liest *dein genaues Gerät*, nicht die Modellfamilie. Datenblätter und Shop-Einträge beschreiben eine Modellreihe; die Variante, die in deine Tasche kam, kann abweichen.

### Die Software-Bestätigung in den Einstellungen

Der Wählertest ist der schnelle, und das Einstellungsmenü bestätigt ihn. Auf dem **iPhone** zeigt *Einstellungen → Mobilfunk* **eSIM hinzufügen** (oder *Mobilfunktarif hinzufügen*), wenn die Funktion aktiv ist. Auf **Android** zeigt *Einstellungen → Netzwerk und Internet → SIMs* (Samsung: *Verbindungen → SIM-Manager*) **eSIM hinzufügen** oder **SIM herunterladen**.

Einige Android-Oberflächen lassen die EID im `*#06#`-Bildschirm weg, obwohl sie eSIM unterstützen. Zeigt der Wähler nur eine IMEI, weiche auf den SIM-Manager-Bildschirm oben aus — die Anwesenheit eines „eSIM hinzufügen"-Bedienelements dort ist ein gleichwertiger Beweis. Was nach diesem Tipp tatsächlich passiert, behandelt die Erklärung [Was eine eSIM tatsächlich ist](/de/guides/what-is-an-esim/) in einfachen Worten.

## Welche iPhones eSIM unterstützen

Jedes iPhone ab dem **XR und XS (2018)** hat eSIM-Hardware — das umfasst die iPhone 11 bis 18-Familien, beide SE-Generationen und die neue iPhone Air-Reihe. Drei Hinweise, die Geld wert sind: US-Modelle ab dem iPhone 14 sind eSIM-only (gar kein physischer SIM-Schacht), Modelle aus China Festland haben kein eSIM (stattdessen zwei physische SIMs — das eSIM-only iPhone Air ist die Ausnahme, die dort funktioniert), und jedes iPhone, das noch auf seinen ursprünglichen Betreiber gesperrt ist, verweigert Reiseprofile bis zur Entsperrung. Ein iPhone X oder älter fällt durch den Test — diese Generation hat einfach keinen Chip. Qualifiziert die Hardware, dauert die [Installationsanleitung](/de/guides/how-to-install-esim/) etwa fünf Minuten.

## Welche Android-Smartphones eSIM unterstützen

Die Unterstützung ist bei Android lückenhafter und variantenabhängig — dasselbe Modell kann sich nach Kaufland unterscheiden. Drei Markengruppen decken das meiste ab.

### eSIM-Unterstützung bei Google Pixel

Jeder Pixel ab dem **Pixel 3** (2018) unterstützt eSIM — außer allen Hongkong-Einheiten plus einigen frühen regionalen Ausnahmen beim Pixel 3 und 3a, die die Variantentabelle unten aufführt.

### eSIM-Unterstützung bei Samsung Galaxy

Jedes Flaggschiff der **S20-Reihe und später** unterstützt eSIM (S/Flip/Fold-Familien) — aber die Variante entscheidet: US-gekaufte S20 und S21, das S20 FE, Hongkonger Samsungs und in Korea gekaufte S20 bis S22, Fold und Flip-Modelle haben es nicht.

### eSIM-Unterstützung bei anderen Android-Marken

Flaggschiffe von Motorola, Xiaomi, Oppo, Honor und Nothing ab etwa 2020 enthalten eSIM häufig, Mittelklasse-Modelle oft nicht. Huawei-Unterstützung existiert (ab P40), aber Huawei kommt ohne Google-Dienste, was den App-basierten Installationsweg blockiert, auf den mehrere Anbieter setzen.

Japans heimische Sharp- und Rakuten-Geräte erscheinen ebenfalls in der Tabelle — relevant, wenn du eine [Japan-eSIM](/de/compare/japan/) kaufst und vor Ort nach einem Smartphone suchst.

Die vollständige durchsuchbare Tabelle unter diesem Artikel listet jedes Modell, das wir verifiziert haben — mehrere hundert Smartphones und Tablets über Markengruppen hinweg, mit den Variantenfallen je Marke hervorgehoben. Der `*#06#`-EID-Test klärt dein genaues Gerät trotzdem in Sekunden, weshalb er die empfohlene Prüfung ist und nicht eine Modellliste.

## Was eine EID-Nummer ist und warum sie zählt

Die EID (Embedded Identity Document) ist die Werkkennung des eSIM-Chips selbst — denk an IMEI, aber für die eingebettete SIM. Anbieter nutzen sie, um ein gekauftes Profil an dein konkretes Gerät zu binden, weshalb eine Reise-eSIM auf einem anderen Smartphone nicht neu gescannt werden kann: Das Profil passt zur EID, für die es ausgegeben wurde. Keine EID im `*#06#`-Bildschirm heißt kein Chip, keine eSIM, und der [Weg über die physische SIM](/de/guides/esim-vs-physical-sim/) ist dein Ausweich. Ein praktischer Hinweis nebenbei — wenn eine Installation scheitert und du den Anbieter kontaktierst, ist die EID das Erste, wonach der Support fragt. Mach vor der Reise einen Screenshot des `*#06#`-Bildschirms; er macht die Fehlersuche aus dem Ausland deutlich schneller.

## Warum dasselbe Smartphone-Modell je Land abweichen kann

Hersteller bauen regionale Hardware-Varianten eines einzelnen Modells. Funkbänder, SIM-Schacht-Layouts — und der eSIM-Chip selbst — folgen dem Markt, für den eine Einheit gebaut wurde, nicht dem Namen auf der Schachtel. Ein Galaxy S21 für den US-Markt und eines für Europa teilen einen Namen, einen Bildschirm und ein Kamerasystem und unterscheiden sich bei eSIM. Das ist kein Versehen; es spiegelt Betreiberdeals, lokale Vorschriften und Dual-SIM-Konventionen in jeder Region.

Für Reisende ist die folgende Regel einfach: **Wo das Smartphone gekauft wurde, zählt mehr als wie es heißt.** Die Fallencluster sind stabil und bekannt — US-Varianten bestimmter Samsung-Generationen, iPhones aus China Festland, Hongkong-Einheiten über alle Marken, in Korea gekaufte Samsung-Flaggschiffe. Die Tabelle blockierter Varianten unter diesem Artikel listet die konkreten Kombinationen, auf die Reisende tatsächlich stoßen, und jeder Markenabschnitt in der Gerätedatenbank markiert seine eigene Variantenwarnung in Amber.

Gebrauchtmärkte machen das schlimmer, nicht besser: Exportvarianten überqueren Grenzen still, und ein Angebot erwähnt selten, in welchem Markt das Smartphone ursprünglich verkauft wurde. Hast du das Smartphone nicht selbst neu gekauft, nimm nichts an und führe den EID-Test aus — er liest die Hardware, den einzigen Zeugen, der nie lügt.

## Unterstützen Tablets und Laptops eSIM

Manchmal, und es lohnt zu wissen, wo die Grenze liegt. **Cellular-iPads** (WLAN + Cellular-Modelle) tragen eine eSIM und folgen demselben Installationsablauf wie iPhones — scannen, aktivieren, fertig. Reine WLAN-iPads haben überhaupt kein Mobilfunkmodem, es gilt also kein Tarif irgendeiner Art. **Windows-Laptops** mit Mobilfunkmodem kommen seit Jahren mit eSIM-Unterstützung; der Check ist *Einstellungen → Netzwerk und Internet → Mobilfunk* — ein Eintrag dort heißt, ein Modem existiert, und eine Option „Mit einem Mobilfunknetz verbinden" oder eine eingebettete SIM heißt, es ist eSIM-fähig.

Der ehrliche Vorbehalt: Anbieter von Reise-eSIMs entwerfen und bepreisen ihre Tarife für Smartphones. Die meisten Installationen auf einem Cellular-Tablet funktionieren identisch, aber manche Anbieter beschränken Tarife auf Smartphone-Geräte oder schließen Tablets vom Support aus. Prüfe die Seite zu unterstützten Geräten des Anbieters, bevor du einen reinen Tablet-Tarif kaufst — die [Anbieterbewertungen](/de/esim-providers/) hier verlinken die offiziellen Kanäle jedes Anbieters.

## Blockiert ein netzgesperrtes Smartphone eSIMs

Ein netzgesperrtes Smartphone kann eine eSIM überhaupt nicht installieren. Es akzeptiert Profile nur von dem Betreiber, auf den es gesperrt ist; jede Installation einer Reise-eSIM schlägt fehl, meist mit einem vagen Fehler zur Aktivierung statt einer klaren Sperrmeldung. Prüfe auf iOS 14 und neuer unter *Einstellungen → Allgemein → Info → Netzbetreibersperre*: Dort muss **Keine SIM-Einschränkungen** stehen. Ist dein Gerät abbezahlt? Die Entsperrung ist normalerweise eine kostenlose Betreiberanfrage — erledige sie eine Woche vor der Abreise, nicht am Gate. Und beachte das grausame Detail: Ein gesperrtes Smartphone *besteht* den EID-Wählertest, weil der Chip existiert. Die Sperre ist ein Software-Gate über der Hardware, weshalb die zwei Checks getrennte Schritte sind.

## Was eine eSIM vor dem Betrieb braucht

Vier Voraussetzungen entscheiden, ob eine Reise-eSIM installiert und verbindet, und nur die erste betrifft Hardware:

1. **Ein eSIM-fähiges Gerät** — ein Smartphone, Tablet oder Laptop mit dem eingebetteten Chip. Der `*#06#`-Wählertest beantwortet das in Sekunden, und die Variantentabelle unten deckt die regionalen Fallen ab.
2. **Ein netzentsperrtes Smartphone** — der Chip kann vorhanden sein und trotzdem jedes Drittprofil verweigern. Auf iOS 14 und neuer muss unter *Einstellungen → Allgemein → Info → Netzbetreibersperre* **Keine SIM-Einschränkungen** stehen.
3. **Eine EID an die der Anbieter binden kann** — das Profil wird gegen die EID deines Geräts ausgegeben, weshalb derselbe QR-Code nicht zweimal installiert.
4. **Ein Installationsweg den dein Smartphone ausführen kann** — QR-Code- und Web-Installationen brauchen nichts außer einer Kamera und einer Verbindung, während Anbieter mit App-Weg eine Mindest-OS-Version und eine Kontoregistrierung hinzufügen.

Fehlt eines der vier, schlägt die Installation fehl, meist mit einem vagen Aktivierungsfehler statt einem klaren Grund. Deshalb ist die Installation zu Hause im WLAN, Tage vor der Abreise, die Gewohnheit, die es wert ist, beibehalten zu werden — ein Fehler am Abfluggate hat keine Lösung.

## Die Hälfte der Kompatibilität ist der Installationsweg des Anbieters

Hardware ist eine Hälfte der Kompatibilität; die andere Hälfte ist, wie der Anbieter seine Profile installiert. {{< count-app-providers >}} der {{< count-providers >}} Anbieter, die wir erfassen, liefern über ihre eigene App — was still eine Anforderung an die Betriebssystemversion und eine Kontoregistrierung auf den eSIM-Hardware-Check draufsetzt. Die anderen {{< count-direct-providers >}} installieren über einen einfachen QR-Code oder eine Website, ohne App. Die Anbietertabelle auf dieser Seite zeigt, wer was ist, denn „mein Smartphone unterstützt eSIM" kann trotzdem mit „dieser Anbieter braucht eine App, die mein Smartphone nicht ausführen kann" zusammenstoßen.

## Warum ein bestandener Check bei der Installation trotzdem scheitern kann

Ein sauberer EID-Bildschirm ist notwendig, aber nicht ausreichend. Drei Fehler zeigen sich erst bei der Installation, und alle drei sind billiger zu Hause zu entdecken:

- **Die Sperre die du nicht bemerkt hast.** Smartphones, gebraucht gekauft, von der Familie geerbt oder im letzten Jahr aus einem Vertrag gelöst, sind häufig noch gesperrt. Die Installation schlägt mit einem Aktivierungsfehler fehl, der nie „gesperrt" sagt.
- **Die App die deinem Smartphone entwachsen ist.** Anbieter mit App-Weg heben ihre Mindest-OS-Version mit der Zeit an; ein sonst fähiges Smartphone, zwei Hauptversionen zurück, kann vom Installations-App ausgesperrt werden.
- **Die App-Store-Region.** Manche Anbieter-Apps sind nicht in jedem Länderstore veröffentlicht. Reisende mit einem Heimstore-Konto im Ausland können den Installer manchmal überhaupt nicht herunterladen.

Die Lösung für alle drei ist dieselbe Gewohnheit: **installiere vor dem Flug**, im heimischen WLAN, mit Tagen Reserve. Scheitert etwas, hast du noch Zeit, das Smartphone zu entsperren, das OS zu aktualisieren oder stattdessen einen QR-Code-Anbieter zu wählen — und der [Dual-SIM-Ratgeber](/de/guides/dual-sim-and-esim/) zeigt, wie du deine Heimatleitung unberührt lässt, während die eSIM die Daten übernimmt.

## Was du vor dem Kauf eines gebrauchten Smartphones für Reisen prüfst

Gebrauchte Smartphones sind die größte einzige Quelle für Variantenüberraschungen, führe also dieselben Checks aus, die ein Käufer schriftlich verlangen sollte:

1. **EID per `*#06#`** — am physischen Smartphone, bevor Geld den Besitzer wechselt. Keine EID, kein Geschäft, egal was das Angebot behauptet.
2. **Netzsperren-Status** — auf iOS muss Keine SIM-Einschränkungen stehen; auf Android bestätige es mit dem Betreiber des Verkäufers, wenn das Menü es nicht zeigt.
3. **Der Markt in dem es verkauft wurde** — frag, wo das Smartphone neu gekauft wurde. Der Modellcode unter *Einstellungen → Telefoninfo* identifiziert die genaue Variante, und diesen Code zu suchen klärt, ob ihre Region den eSIM-Chip behielt.
4. **Die OS-Version** — wenn du einen Anbieter mit App-Weg nutzt, prüfe, ob das Smartphone auf eine aktuelle OS-Version aktualisieren kann.

Zehn Minuten Prüfen schlagen die Entdeckung eines toten Profils am Abfluggate — und hat das Smartphone bestanden, zählt mehr, was Daten kosten, als das Gerät selbst.

Für kompatibel befunden? Du bist einen Vergleich von einem Tarif entfernt: [alle Länderseiten](/de/compare/), der [Reisekostenrechner](/de/tools/), der einen Tarif an deine Daten anpasst, oder der [Preisindex](/de/research/esim-price-index/), der jedes Reiseziel, das wir erfassen, nach echten Datenkosten sortiert.
'''

PAGES = {
    "content/de/guides/esim-vs-physical-sim.md": VS.replace("{TODO}", TODO),
    "content/de/guides/dual-sim-and-esim.md": DUAL.replace("{TODO}", TODO),
    "content/de/guides/esim-compatibility-check.md": COMPAT.replace("{TODO}", TODO),
}

BAD = [",", ";", ":", "\u2014", "\u2013"]


def headings_of(text: str):
    """body 的 h2/h3 + front matter 里会被模板渲染成 h1/h2/h3 的字段。"""
    fm, body = text.split("\n---\n", 1)
    out = []
    for line in body.split("\n"):
        if line.startswith("## ") or line.startswith("### "):
            out.append(line.lstrip("# ").strip())
    for key in ("h2_answer:", "h2_facts:", "h2_next:", "faq_heading:"):
        for line in fm.split("\n"):
            if line.startswith(key):
                out.append(line[len(key):].strip().strip('"'))
    for line in fm.split("\n"):
        s = line.strip()
        if s.startswith("- q: "):
            out.append(s[5:].strip().strip('"'))
    return out


def main() -> int:
    failures = []
    for rel, content in PAGES.items():
        for h in headings_of(content):
            for ch in BAD:
                if ch in h:
                    failures.append(f"{rel}: 标题含禁用标点 {ch!r} -> {h!r}")
        for m in re.finditer(r"\]\((/[^)]*)\)", content):
            href = m.group(1)
            if href.startswith("/de/") or href.startswith("/#"):
                continue
            failures.append(f"{rel}: 站内链缺 /de/ 前缀 -> {href}")
        # 短代码计数必须与 en 侧逐个一致（dual-sim 原版就没有短代码，不能强加）
        en = (ROOT / rel.replace("content/de/", "content/en/")).read_text(encoding="utf-8")
        en_sc = sorted(re.findall(r"\{\{<\s*([a-z-]+)\s*>\}\}", en))
        de_sc = sorted(re.findall(r"\{\{<\s*([a-z-]+)\s*>\}\}", content))
        if en_sc != de_sc:
            failures.append(f"{rel}: 短代码与 en 侧不一致 -> en={en_sc} de={de_sc}")

    if failures:
        print("前置校验失败：")
        for f in failures:
            print("  -", f)
        return 1

    changed = 0
    for rel, content in PAGES.items():
        p = ROOT / rel
        data = content.encode("utf-8")
        if p.exists() and p.read_bytes() == data:
            print(f"  已是目标内容  {rel}")
            continue
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_bytes(data)
        b = p.read_bytes()
        assert b"\r\n" not in b, f"{rel} 出现 CRLF"
        print(f"  写入 {rel}  {len(b)} bytes  (标题 {len(headings_of(content))} 个)")
        changed += 1

    print(f"\n写入 {changed} 个文件。")
    return 0


if __name__ == "__main__":
    sys.exit(main())
