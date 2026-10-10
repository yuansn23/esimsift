# -*- coding: utf-8 -*-
"""批 C 之一：content/de/guides/what-is-an-esim.md + how-to-install-esim.md

纪律
----
* 一律 bytes 读写，LF 行尾（德语侧既有文件全为 LF）。
* 幂等：目标文件已存在且内容逐字节相同 -> 跳过。
* front matter 字段与 en 侧逐字段对齐（title/hero/hero_alt/date/description/
  faq_heading/prompt_answer/h2_answer/h2_facts/facts/h2_next/faqs），
  外加德语侧分层发布策略的 noindex + TODO 注释。
* 正文内 h2/h3 与 FAQ 问句（模板渲染成 h3）一律不含 , ; : — –（check_headings.py）。
* 站内链一律显式 /de/ 前缀；短代码原样保留。
* 人称 du（对齐 guides 栏目既有德语样本：guides_single 0 Sie / 5 du）。
"""
import pathlib
import sys

ROOT = pathlib.Path(".")

TODO = "# TODO(de)：分层发布 —— 全站德语译文解禁（D9 那一轮）时删掉上面这行。"

WHAT_IS = '''---
title: "Was ist eine eSIM? Funktionsweise einfach erklärt (2026)"
hero: "travel-esim-illustration-071.webp"
hero_alt: "Eine Reisende hält ein Smartphone neben einen überdimensionalen SIM-Chip und Signalbalken — die Idee hinter einer eingebetteten Reise-eSIM"
date: 2026-10-01
description: "Was ist eine eSIM? eSIM Sift erklärt, wie eine fest eingebaute SIM funktioniert, was beim Installieren tatsächlich auf dem Gerät landet und was das für Anrufe und SMS im Ausland bedeutet."
faq_heading: "Was du vor deiner ersten eSIM wissen solltest"
prompt_answer: "Eine eSIM ist eine digitale SIM, die dein Smartphone auf einem fest eingebauten Chip speichert — es gibt also keine Plastikkarte zum Wechseln. Auf Reisen heißt das: Daten für ein Reiseziel vor dem Abflug kaufen, im WLAN installieren und die heimische SIM für Anrufe und SMS im Gerät lassen."
h2_answer: "Was eine eSIM für Reisende bedeutet"
h2_facts: "eSIM-Fakten für Reisende"
facts:
  - label: "Steht für"
    value: "Embedded SIM, ein fest im Gerät verbauter Chip statt einer Karte zum Einsetzen"
  - label: "Was sie ersetzt"
    value: "Die herausnehmbare Plastik-SIM-Karte"
  - label: "Wie sie ankommt"
    value: "Als herunterladbares Profil, per QR-Code oder über die App des Anbieters"
  - label: "Braucht einen SIM-Schacht"
    value: "Nein, der Chip ist Teil des Geräts"
  - label: "Typische Installationsdauer"
    value: "Unter zwei Minuten im WLAN"
h2_next: "Lerne weiter über eSIM"
noindex: true
{TODO}
faqs:
  - q: "Ersetzt eine eSIM deine physische SIM?"
    a: "Eine eSIM arbeitet neben der physischen SIM, statt sie zu ersetzen. Ein Smartphone mit eSIM-Unterstützung behält seinen physischen SIM-Schacht voll nutzbar, und du wählst pro Leitung, welche Anrufe und welche Daten trägt. Die meisten Reisenden lassen ihre heimische SIM für Nummer und SMS an ihrem Platz und überlassen der eSIM die Daten im Ausland."
  - q: "Kann eine eSIM SMS und Verifizierungscodes empfangen?"
    a: "Die meisten Reise-eSIMs können SMS empfangen, aber nicht alle, und Verifizierungscodes von Banken oder Apps sind der klassische Fehlerfall. Wenn du im Ausland auf OTP-Codes angewiesen bist, halte die heimische Leitung für diese Nachrichten im physischen Schacht aktiv und nutze die eSIM rein für Daten."
  - q: "Wie lange hält eine eSIM?"
    a: "Das installierte Profil bleibt auf dem Smartphone, bis du es löschst, aber der daran gebundene Tarif gilt nur in seinem Gültigkeitsfenster, typischerweise 7 bis 30 Tage ab Aktivierung. Abgelaufene Profile sind inaktiv, du kannst sie behalten oder löschen, und ein neues Paket für die nächste Reise installiert sich als frisches Profil."
  - q: "Ist eine eSIM teurer als eine physische SIM?"
    a: "Eine eSIM ist nicht grundsätzlich teurer als eine physische SIM. Die Preise von Reise-eSIMs schwanken weit stärker nach Reiseziel als nach Technik — über die Reiseziele in unserem Preisindex unterscheidet sich der beste Preis pro Gigabyte um ein Mehrfaches zwischen dem günstigsten und dem teuersten Land. Der eigentliche Vergleich gilt den Preisen am Flughafenkiosk, die Online-Anbieter für Reise-eSIMs regelmäßig unterbieten."
  - q: "Funktioniert eine eSIM in jedem Land?"
    a: "Eine eSIM funktioniert nur in den Ländern, die ihr Tarif abdeckt. Ein Ein-Länder-Tarif bucht sich in Partnernetze in diesem einen Markt ein, ein regionaler Tarif deckt eine Gruppe benachbarter Länder ab, und ein globaler Tarif funktioniert in vielen Reisezielen zu einem anderen Satz. Jeder Tarif listet seine Abdeckung vor dem Kauf, also gleiche diese Liste mit deiner Route ab, statt es anzunehmen."
  - q: "Brauchst du WLAN um eine eSIM zu installieren?"
    a: "Du brauchst während der Installation eine Internetverbindung, aber das kann dein Heim-WLAN, dein aktuelles mobiles Netz oder das Flughafennetz sein — der Download ist winzig und in Sekunden fertig. Die Aktivierung passiert später im Mobilfunknetz des Reiseziels, weshalb die Installation zu Hause im WLAN vor der Abreise der übliche Rat ist."
  - q: "Kannst du eine eSIM auf ein neues Smartphone übertragen?"
    a: "Eine eSIM auf ein neues Smartphone zu übertragen schlägt in der Regel bewusst fehl. Ein Reise-eSIM-Profil bindet sich an das erste Gerät, das es installiert, und denselben QR-Code auf einem zweiten Smartphone zu scannen schlägt bewusst fehl. Die meisten Anbieter stellen das Profil für ein neues Gerät auf Anfrage neu aus, manchmal gegen eine kleine Gebühr oder nur begrenzt oft — prüfe die Richtlinie vor dem Kauf, wenn du mitten auf der Reise aufrüsten willst."
---

Eine eSIM ist eine SIM-Karte, die schon im Werk in dein Smartphone eingebaut wird, statt auf einem Stück Plastik zu kommen. Ein kleiner Chip ist auf die Hauptplatine gelötet, und wenn du eine eSIM „installierst", lädst du ein Anbieterprofil auf diesen Chip — nichts wird eingeschoben, nichts getauscht, und keine Nadel kommt zum Einsatz. Für Reisende ändert genau dieser Unterschied, wie du Mobilfunkdaten im Ausland kaufst: online, im Voraus, mit jedem Preis sichtbar, bevor du dich entscheidest. Dieser Ratgeber geht eine Ebene tiefer als die meisten Erklärungen — der Chip selbst, was ein Profil enthält, wann ein Tarif wirklich beginnt und wo die Sicherheit subtil wird.

## Wofür steht eSIM und wie funktioniert sie

„SIM" steht für Subscriber Identity Module — die Kennung, die einem Mobilfunknetz sagt „diese Leitung gehört mir, rechne sie mit diesem Konto ab". Eine physische SIM speichert diese Kennung auf einer herausnehmbaren Karte, die du per Hand wechselst. Eine eSIM — das „e" steht für *embedded*, also eingebettet — speichert sie auf einem neu beschreibbaren Chip im Gerät, und das Profil darauf lässt sich beliebig oft ersetzen, ohne die Hardware anzufassen.

In der Praxis läuft der Kauf einer Reise-eSIM so ab. Du wählst ein Paket auf der Website oder in der App eines Anbieters — ein Datenvolumen, gültig für einen festen Zeitraum, in einem Land oder einer Region. Der Anbieter erzeugt ein Profil, das an dieses Paket gebunden ist. Du installierst es zu Hause, und es aktiviert sich in der Regel, wenn es sich am Reiseziel erstmals in ein Partnernetz einbucht — nicht im Moment der Installation.

## Der Chip im Gerät und das Profil darauf

Die meisten Erklärungen behandeln eine eSIM als eine einzige Sache, aber sie besteht aus zwei Teilen — und dieser Unterschied erklärt fast alles darüber, wie eSIMs sich verhalten.

### Der eingebettete Chip im Gerät

Ein **eUICC** ist die Hardware-Hälfte des Paares — formal eine embedded universal integrated circuit card, ein winziges Sicherheitselement, das im Werk auf die Hauptplatine deines Smartphones gelötet wird. Stell es dir als neu beschreibbaren Tresor vor, der leer ausgeliefert wird und das Gerät nie verlässt.

### Das Anbieterprofil auf dem Chip

Ein **Profil** ist die Software-Hälfte des Paares, die Kennung eines Anbieters, die in diesem Tresor liegt wie eine Schlüsselkarte für ein bestimmtes Schloss. Jedes Mal, wenn du eine eSIM „installierst", kommt eine neue Schlüsselkarte hinein; jedes Mal, wenn du eine löschst, kommt eine heraus. Der Tresor selbst nutzt sich nie ab.

Diese Trennung ist der Grund, warum ein Smartphone mehrere eSIMs gleichzeitig speichern kann, warum das Löschen eines verbrauchten Tarifs nichts beschädigt und warum eine eSIM nicht wie eine Plastikkarte an ein anderes Smartphone weitergegeben werden kann — die Schlüsselkarten liegen in einem bestimmten Tresor.

## Was eine eSIM nicht braucht

Drei Dinge, die Reisende bei einer eSIM vermuten, die sie aber nicht braucht:

- **Ein anderes Kartenformat.** Es gibt kein eSIM-Äquivalent zu nano, micro oder standard — der Chip ist eingebettet, es gibt also nichts zu messen, zu stanzen oder anzupassen. Wenn du nach der eSIM-Größe für dein Smartphone gesucht hast, trifft die Frage nicht zu.
- **Einen Gang in den Laden.** Die ganze Installation läuft über das Smartphone, per QR-Code oder über die App des Anbieters, im WLAN zu Hause.
- **Dass deine Heimatnummer sich ändert.** Die eSIM übernimmt die Daten, während die physische SIM ihre Nummer und ihre SMS behält — darum geht es im [Dual-SIM-Ratgeber](/de/guides/dual-sim-and-esim/).

Was sie braucht, ist ein kompatibles, nicht netzgesperrtes Gerät — der [Kompatibilitäts-Check](/de/guides/esim-compatibility-check/) klärt das in dreißig Sekunden.

## Was ein eSIM-Profil tatsächlich enthält

### Was ein Profil tatsächlich speichert

Ein Profil ist eine kleine strukturierte Datei, und ihr Inhalt ist enger begrenzt, als die meisten annehmen. Es enthält die Anbieterkennung, die die Leitung gegenüber einem Netz ausweist, die kryptografischen Schlüssel, die die Kennung als echt belegen, die Verbindungseinstellungen — einschließlich des APN, über den deine Daten laufen — und die Liste der Netze, in die sich das Profil einbuchen darf.

### Was ein Profil niemals speichert

Ein Profil enthält nichts Persönliches — keinen Namen, keine Zahlungskarte, keinen Browserverlauf, keine Kontakte. Die Verbindung zwischen einem Profil und einem zahlenden Kunden liegt im Abrechnungssystem des Anbieters, nicht auf deinem Smartphone.

Die Trennung von Chip und Profil enthält eine praktische Lehre. Die Technik entscheidet nicht, wer deine Nutzungsdaten sieht oder wie eine Neuausstellung gehandhabt wird — das entscheidet der Anbieter. Deshalb ist die Wahl des Anbieters mindestens so wichtig wie der eSIM-Standard, und deshalb lohnt vor dem Bezahlen ein Blick in die Bedingungen, nicht nur auf die Preise.

## Was tatsächlich auf deinem Smartphone landet

Die Installation ist ein Download, kein Einsetzen. Du scannst einen QR-Code oder tippst einen Link in der App des Anbieters an, und dein Smartphone spricht mit dem Download-Server des Anbieters — die Branche nennt ihn SM-DP+, aber „der Download-Server, mit dem dein Smartphone spricht" ist alles, was du wissen musst — der den Code prüft und das Profil im WLAN zu Hause in Sekunden auf den Chip liefert. Unsere Schritt-für-Schritt-[Installationsanleitung](/de/guides/how-to-install-esim/) zeigt die genauen Taps für iOS und Android.

Drei Details zum installierten Profil sind wichtig:

- **Das Profil ruht bis zur Aktivierung.** Eine Woche vor dem Flug zu installieren ist sicher — die Gültigkeitsuhr startet meist bei der ersten Verbindung im Ausland, bei einigen wenigen Anbietern aber schon bei der Installation, also prüfe die Tarifbedingungen.
- **Der QR-Code ist meist einmalig.** Ein Reise-eSIM-Profil bindet sich an das erste Gerät, das es installiert. Denselben Code auf einem anderen Smartphone zu scannen schlägt bewusst fehl; ein Gerätewechsel bedeutet in der Regel, den Anbieter um eine Neuausstellung zu bitten.
- **Löschen ist kostenlos und endgültig.** Ein abgelaufenes oder aufgebrauchtes Profil kannst du jederzeit löschen, und die eSIM-Fähigkeit des Geräts wird dabei nicht verbraucht — das Profil für die nächste Reise lässt sich sofort installieren.

Ein Sonderfall ist wichtig — ein vollständiger Werksreset kann auf manchen Geräten installierte eSIM-Profile löschen, also setze das Gerät vor einer Reise zurück, nicht währenddessen.

## Wann ein eSIM-Tarif tatsächlich beginnt

Drei getrennte Ereignisse stecken in der Wendung „eine eSIM aktivieren", und wer sie auseinanderhält, schützt sein Datenvolumen — oder verbrennt es still.

### Die Installation ist nur der Download

Die Installation ist der Download-Schritt, bei dem das Profil auf dem Chip landet und dort inaktiv liegt. Sie kann Tage oder Wochen vor dem Abflug passieren und kostet dich nichts.

### Die Aktivierung bringt den Empfang

Die Aktivierung ist der Moment, in dem der Dienst entsteht — du schaltest die Leitung ein, und das Smartphone bucht sich in ein Netz ein, bei Reise-eSIMs meist in ein Partnernetz am Reiseziel. Bis dahin gibt es keine Verbindung und keinen Verbrauch.

### Der Gültigkeitsbeginn startet die Uhr

Der Gültigkeitsbeginn ist der Start der Paketuhr. Die meisten Anbieter starten sie bei der Aktivierung oder bei der ersten Datennutzung im Ausland, einige aber schon bei der Installation und wenige beim Kauf. Ein Monatsfenster, das bei der Installation startet, verliert still zwei Wochen auf deinem Sofa.

Das sichere Muster nutzt die Tatsache, dass dies getrennte Ereignisse sind — zu Hause installieren, prüfen wann die Uhr startet, landen und verbinden. Anbieter, die das verwischen, schreiben es meist ins Kleingedruckte, und das ist dreißig Sekunden Lesen wert.

## Wie viele eSIMs ein Smartphone speichern kann

Ein aktuelles iPhone speichert üblicherweise acht oder mehr Profile, die meisten aktuellen Android-Geräte fünf oder mehr. Für Daten ist immer nur eines aktiv, und du wechselst in den Einstellungen in Sekunden zwischen ihnen. Dieses Speichermodell macht Reisen durch mehrere Länder mühelos — kaufe eine [Japan-eSIM](/de/compare/japan/) und eine [Thailand-eSIM](/de/compare/thailand/) vor der Abreise, installiere beide und aktiviere jede bei der Ankunft, ohne eine physische Karte anzufassen. Unser [Dual-SIM-Ratgeber](/de/guides/dual-sim-and-esim/) erklärt, wie das Smartphone die Leitungen verwaltet und welche Schalter entscheiden, was Daten nutzt.

## eSIM und physische SIM auf Reisen

Bei internationalen Reisen fallen die Unterschiede zugunsten der eSIM aus:

- **Kauf vor dem Flug.** Eine physische lokale SIM bedeutet, nach der Landung einen Laden zu suchen, zu Flughafenpreisen; eine eSIM kaufst du vom Sofa aus, und sie funktioniert, sobald du aus dem Flugzeug steigst.
- **Deine Heimatnummer bleibt erreichbar.** Die heimische SIM bleibt für Anrufe und SMS im Schacht, während die eSIM die Daten trägt — beide laufen parallel.
- **Preise sind ausgezeichnet statt verhandelt.** Reise-eSIMs werden online verkauft, wo sich die echten Preise jedes Anbieters vor dem Kauf vergleichen lassen — genau das tun unsere [Ländervergleiche](/de/compare/).
- **Sie lässt sich nicht still umstecken.** Ein Dieb kann eine eSIM nicht ohne deine Zugangsdaten auf ein anderes Gerät bringen, weshalb Netzbetreiber sie zunehmend zur Sicherheit einsetzen. Die Kehrseite: Du kannst eine verbrauchte eSIM auch nicht an eine Freundin oder einen Freund weitergeben.

Die ehrlichen Ausnahmen, in denen Plastik noch gewinnt: Du brauchst eine lokale Rufnummer mit Guthaben, dein Gerät stammt aus der Zeit vor eSIM-Unterstützung (der [Kompatibilitäts-Check](/de/guides/esim-compatibility-check/) klärt das in 30 Sekunden), oder dein Smartphone ist netzgesperrt. Unser ausführlicher Vergleich [eSIM gegen SIM](/de/guides/esim-vs-physical-sim/) zeigt, wo jede Variante tatsächlich gewinnt.

## Wie sicher ist eine eSIM

### Warum ein gestohlenes Smartphone das Profil behält

Ein Profil bindet sich an ein Gerät und lässt sich nur über den Anbieter neu binden, es kann also nicht wie eine physische Karte aus einem gestohlenen Smartphone genommen werden. Diese Gerätebindung ist auch der Grund, warum Netzbetreiber Vertragsleitungen zunehmend als eSIM ausgeben — und sie berührt das Thema SIM-Swap-Betrug. Eine eSIM macht Swap-Betrug nicht unmöglich, denn dieser Betrug beginnt meist mit Social Engineering beim Netzbetreiber statt mit der Karte; aber eine Kennung, die sich nicht still zwischen Geräten verschieben lässt, schließt einen der einfacheren Angriffswege.

### Die zwei Sicherheitsvorbehalte bei eSIM

Die Sicherheitsbilanz ist wirklich besser als bei Plastik, und zwei ehrliche Vorbehalte dämpfen sie. Erstens ist der QR-Code faktisch ein Inhaberpapier — wer ihn zuerst scannt, verbraucht das Profil. Veröffentliche ihn nie, verkaufe ihn nie weiter und kaufe keine QR-Codes auf Marktplätzen, auf denen der ursprüngliche Käufer sie schon gescannt haben könnte. Zweitens: Ist deine persönliche Hauptleitung selbst eine eSIM, dann schütze die PIN oder das Passwort deines Anbieterkontos; das Profil auf deinem Smartphone war nie der schwache Punkt.

## Was kostet eine eSIM

Weniger, als die meisten Reisenden erwarten — und das Reiseziel wiegt weit schwerer als der Anbieter oder die Technik. Dasselbe Gigabyte kann in einem Land ein Mehrfaches dessen kosten, was es beim Nachbarn kostet, allein wegen des lokalen Netzwettbewerbs und der Vorleistungskosten. Unser [eSIM-Preisindex](/de/research/esim-price-index/) sortiert die {{< count-countries >}} Reiseziele, die wir erfassen, nach dem besten Preis pro Gigabyte, und der Abstand zwischen dem günstigsten und dem teuersten Land beträgt ein Mehrfaches.

Innerhalb eines Reiseziels bestimmen drei Mechanismen, was du zahlst:

- **Volumen- gegen Tagespreise.** Feste Datenpakete berechnen im Voraus einen festen Betrag; „unlimited" Tagespakete berechnen stattdessen pro Nutzungstag. Tagespreise passen zu leichter, verteilter Nutzung; Pakete passen zu Vielnutzern.
- **Gültigkeitsfenster.** Kurze Fenster kosten weniger, laufen aber hart ab — ein Tarif, der am siebten Tag endet, ist am achten wertlos. Längere Fenster tauschen einen höheren Preis gegen das Überleben der ganzen Reise.
- **Fair-Use-Richtlinien.** „Unlimited"-Tarife drosseln oder pausieren nach einer Tagesgrenze. Wir zitieren die Richtlinie jedes Anbieters wörtlich in der [Fair-Use-Prüfung](/de/research/fair-use-audit/), und unsere [Unlimited-eSIM-Analyse](/de/research/unlimited-esim/) zeigt, wo Tagespreise tatsächlich am günstigsten sind.

Jede Länderseite — [Spanien-eSIM](/de/compare/spain/) oder [Italien-eSIM](/de/compare/italy/) — listet dann jeden Tarif der {{< count-providers >}} Anbieter, die eSIM Sift erfasst, nebeneinander. Unsicher, wie viele Gigabyte du brauchst? Der [Reisekostenrechner](/de/tools/) schätzt es aus dem, was du online tatsächlich tust.

## Bekommst du mit einer Reise-eSIM eine Rufnummer

Eine Reise-eSIM kommt meist ohne anrufbare Rufnummer. Das sind datenorientierte Produkte: Einige enthalten eine Nummer, die SMS empfangen kann, wenige enthalten Guthaben für abgehende Anrufe, und keine ersetzt deine heimische Leitung für Anrufe. Wenn du im Ausland auf Verifizierungscodes angewiesen bist — vor allem auf Bank-OTPs — hält die übliche Einrichtung die heimische SIM für diese Nachrichten aktiv und lässt die eSIM alles andere tragen. Jeder als unlimited beworbene Tarif verdient zudem einen skeptischen Blick in die Fair-Use-Bedingungen, bevor du ihm Arbeitsanrufe oder Tethering anvertraust.

## Wer auf eine Reise-eSIM verzichten sollte

Reise-eSIMs sind das falsche Werkzeug für eine schrumpfende, aber reale Gruppe: alle, die eine lokale Nummer mit Guthaben brauchen, und alle, deren Smartphone den Kompatibilitäts-Check nicht besteht oder noch netzgesperrt ist. Alle anderen sollten beim Reiseziel anfangen — vergleiche Tarife auf den Länderseiten oder lies die [Anbieterbewertungen](/de/esim-providers/), um zu sehen, wie sich die Marken bei Neuausstellungen, Fair Use und App-Qualität unterscheiden, bevor du dich festlegst.
'''

HOW_TO = '''---
title: "Reise-eSIM installieren auf iPhone und Android"
hero: "travel-esim-illustration-007.webp"
hero_alt: "Eine Reisende folgt einer Schritt-für-Schritt-Checkliste auf dem Smartphone, um eine Reise-eSIM zu installieren"
date: 2026-10-01
description: "So installierst du eine eSIM in fünf Minuten: eSIM Sift behandelt den Aktivierungszeitpunkt, QR- und App-Installation und die Fehler, die du vor dem Flug vermeiden solltest."
faq_heading: "Was du vor der Installation einer eSIM wissen solltest"
prompt_answer: "Eine Reise-eSIM zu installieren dauert im WLAN etwa zwei Minuten, und der sicherste Zeitpunkt ist vor dem Flug. Kaufe den Tarif, scanne den QR-Code des Anbieters oder füge ihn über die App des Anbieters hinzu, gib der Leitung einen Namen und lass sie ausgeschaltet, bis du landest. Bei der Ankunft schaltest du die eSIM-Leitung ein und setzt sie als Leitung für mobile Daten."
h2_answer: "Reise-eSIM installieren kurz erklärt"
h2_facts: "Fakten zur eSIM-Installation"
facts:
  - label: "Bester Zeitpunkt"
    value: "Vor dem Flug, solange du noch WLAN hast"
  - label: "Was du brauchst"
    value: "Ein entsperrtes Smartphone und den QR-Code oder die App des Anbieters"
  - label: "Typische Installationsdauer"
    value: "Unter zwei Minuten"
  - label: "Erste Einstellung bei Ankunft"
    value: "Die eSIM-Leitung als Leitung für mobile Daten setzen"
  - label: "Wenn sie nicht aktiviert"
    value: "Netzsperre prüfen und ob der Tarif begonnen hat"
h2_next: "Sortiere den Rest deiner Einrichtung"
noindex: true
{TODO}
faqs:
  - q: "Wie lange vor dem Flug sollte ich eine eSIM installieren?"
    a: "Ein bis drei Tage vor der Abreise ist der beste Zeitpunkt. Das Profil ruht, bis die Gültigkeit des Tarifs beginnt, eine frühe Installation ist also sicher, und zu Hause passiert jedes Problem in deinem eigenen WLAN mit Zeit zum Beheben. Installiere nicht am Flughafengate bei 2 % Akku."
  - q: "Kann ich eine eSIM ohne WLAN installieren?"
    a: "Eine eSIM lässt sich ohne WLAN installieren, aber WLAN ist sicherer. Der Profil-Download beträgt wenige hundert Kilobyte, klein genug für mobile Daten, doch eine abgebrochene Verbindung mitten in der Installation ist die klassische Ursache eines halb installierten Profils, das dann eine Neuausstellung durch den Anbieter braucht. Wenn du unterwegs installieren musst, nutze eine stabile Verbindung."
  - q: "Warum zeigt meine eSIM nach der Landung keinen Dienst?"
    a: "Nach Wahrscheinlichkeit: Daten-Roaming ist für die eSIM-Leitung aus, das Smartphone nutzt weiter die heimische SIM für Daten, das Profil hat sich noch nicht in ein Partnernetz eingebucht, oder die Gültigkeit des Tarifs hat noch nicht begonnen. Schalte zehn Sekunden den Flugmodus ein, prüfe zuerst den Roaming-Schalter und gib der Registrierung nach der Landung ein paar Minuten."
  - q: "Kann ich eine eSIM auf einem anderen Smartphone neu installieren?"
    a: "Denselben QR-Code erneut zu scannen verschiebt eine eSIM nicht auf ein anderes Smartphone. Reise-eSIM-Profile binden sich an das erste Gerät, das sie installiert, und die meisten QR-Codes sind einmalig. Ein Gerätewechsel bedeutet, den Anbieter um eine Neuausstellung zu bitten oder ein frisches Paket zu kaufen — plane entsprechend, wenn du mitten auf der Reise das Gerät wechselst."
  - q: "Kann die heimische SIM im Gerät bleiben?"
    a: "Die heimische SIM muss überhaupt nicht aus dem Smartphone heraus. Eine eSIM installiert sich als zweite Leitung neben der physischen SIM, und beide bleiben gleichzeitig aktiv. Deine Heimatnummer empfängt weiter Anrufe und SMS, während die eSIM im Ausland die Daten trägt — genau so ist die Dual-SIM-Einrichtung gedacht."
  - q: "Verbraucht die Installation einer eSIM viel Datenvolumen?"
    a: "Die Installation einer eSIM kostet sehr wenig Datenvolumen, weil das Profil selbst klein ist. Der Download beträgt meist wenige hundert Kilobyte, weit weniger als ein einzelnes Foto, selbst ein kleines mobiles Kontingent deckt das also ab. WLAN bleibt die sicherere Wahl, weil ein unterbrochener Download ein halb installiertes Profil hinterlassen kann, das eine Neuausstellung braucht."
  - q: "Was ist eine SM-DP+-Adresse?"
    a: "Eine SM-DP+-Adresse ist der Server, den dein Smartphone kontaktiert, um das eSIM-Profil herunterzuladen, geschrieben wie eine Web-Domain. Anbieter senden sie mit der Bestätigung zusammen mit einem passenden Aktivierungscode, und du tippst sie nur bei der manuellen Installation selbst ein, weil ein QR-Code nicht scannt."
---

Eine Reise-eSIM zu installieren dauert etwa fünf Minuten und funktioniert am besten *vor* der Abreise, im WLAN, dem du vertraust. Die genauen Bildschirme unterscheiden sich je Anbieter, doch der Ablauf ist überall gleich: Paket kaufen, Profil installieren, es ruhen lassen, bis die Gültigkeit des Tarifs beginnt. Eine Unterscheidung löst die meisten Verwirrungen: **Installieren** legt das Profil auf dein Smartphone, **Aktivieren** startet die Uhr — das sind getrennte Ereignisse.

Dieser Ratgeber geht den ganzen Weg der Reihe nach durch: die Checks vor dem Bezahlen, die Installationsschritte auf beiden Plattformen, beide Installationswege einschließlich der manuellen Codeeingabe, die die meisten Anleitungen auslassen, die ersten Minuten nach der Landung und die Fehler, die tatsächlich passieren — jeweils mit Lösung.

## Zwei 30-Sekunden-Checks vor dem Kauf

1. **Prüfe ob dein Smartphone eSIM unterstützt.** Wähle `*#06#` — erscheint neben der IMEI eine EID-Nummer, ist die Hardware vorhanden. Die Modellliste, einschließlich der iPhone- und Pixel-Grenzen, steht im [eSIM-Kompatibilitäts-Check](/de/guides/esim-compatibility-check/).
2. **Prüfe dass es nicht netzgesperrt ist.** Ein Smartphone, das noch auf seinen ursprünglichen Netzbetreiber gesperrt ist, verweigert eSIM-Profile Dritter; es akzeptiert eSIMs nur von dem Betreiber, der es gesperrt hat. Ist dein Vertragsgerät abbezahlt, ist die Entsperrung meist eine kostenlose Anfrage bei diesem Betreiber und wirkt in der Regel innerhalb von ein bis zwei Tagen.

Ein dritter Check entscheidet, *wie* die Installation abläuft: {{< count-app-providers >}} der {{< count-providers >}} Anbieter, die wir erfassen, installieren über ihre eigene App, die anderen {{< count-direct-providers >}} über einen einfachen QR-Code oder die Website. Die Live-Tabelle unten zeigt, wer was ist — [Airalo](/de/esim-providers/airalo/), [Holafly](/de/esim-providers/holafly/) und [Roamic](/de/esim-providers/roamic/) installieren direkt per Code, während sich App-Marken am besten zu Hause installieren lassen, bevor eine App-Store-Anmeldung am Reisetag zum Problem wird.

## eSIM auf dem iPhone installieren

1. Kaufe das Paket; der Anbieter mailt einen QR-Code, oder seine App bietet eine direkte Installation an.
2. Öffne *Einstellungen → Mobilfunk → eSIM hinzufügen* (ältere iOS-Versionen nennen das *Mobilfunktarife*).
3. Scanne den QR-Code mit der Kamera, oder bestätige die Installationsaufforderung der Anbieter-App, wenn sie erscheint.
4. Wähle **Sekundär** für die neue Leitung und behalte deine Heimatleitung als Primär.
5. Wähle auf dem letzten Bildschirm **Sekundär für Mobilfunkdaten verwenden** und schalte dann **Daten-Roaming nur für die eSIM-Leitung ein**. Diesen Schritt übersehen die meisten; ohne ihn kann sich die eSIM nicht in ausländische Netze einbuchen.

Das Profil ruht, bis die Gültigkeit des Tarifs beginnt, eine frühe Installation ist bei den meisten Tarifen also sicher. Wie die beiden Leitungen koexistieren — Anrufe auf der einen, Daten auf der anderen — behandelt der [Dual-SIM-Ratgeber](/de/guides/dual-sim-and-esim/).

## eSIM auf Android installieren

1. Öffne *Einstellungen → Netzwerk und Internet → SIMs*; Samsung führt das unter *Verbindungen → SIM-Manager*.
2. Tippe auf **eSIM hinzufügen** — auf manchen Oberflächen **SIM herunterladen** genannt — und scanne den QR-Code des Anbieters.
3. Bestätige den Download im WLAN; das Profil erscheint in der Liste als zweite SIM.
4. Setze **Mobile Daten** auf die neue eSIM und schalte ihren **Daten-Roaming**-Schalter ein.
5. Wenn der Anbieter APN-Einstellungen nennt, gib genau die angezeigte APN-Zeichenkette ein — ein Feld, mehr nicht.

Menünamen wandern über die Android-Oberflächen — Pixel, One UI und MIUI benennen denselben Bildschirm jeweils anders — doch jede von ihnen verbirgt zwei Dinge hinter dem Wort SIM: den eSIM-hinzufügen-Knopf und den Roaming-Schalter pro Leitung. Finde diese zwei, und der Ablauf ist überall identisch.

## QR-Code-Installation gegen App-Installation

Jeder Anbieter nutzt einen von zwei Wegen, und zu wissen welcher, prägt das ganze Erlebnis.

### Installation per QR-Code oder Link

Der **QR- oder Direktweg** läuft vollständig aus der Kaufbestätigung. Der Anbieter mailt einen QR-Code, manchmal zusammen mit einem einfachen Link, der beim Antippen installiert. Du scannst ihn in den Einstellungen, das Profil lädt herunter, und du bist fertig — keine App, kein Konto, nichts weiter zu verwalten. Dieser Weg funktioniert in jeder App-Store-Situation und ist der zu bevorzugende, wenn du schon unterwegs bist oder aus der Ferne auf dem Smartphone eines Familienmitglieds installierst.

### Installation über die App des Anbieters

Ein Anbieter mit **App-Weg** legt den ganzen Kauf in seine eigene Anwendung, die die Zahlung abwickelt, die Installationsaufforderung selbst auslöst und später Aufladungen, Verlängerungen und Länderwechsel an einem Ort verwaltet. Die Kehrseiten sind ein zusätzliches Konto, dessen Zugang du behalten musst, und eine Abhängigkeit vom App-Store — eine regional gesperrte App ist ein echtes Fehlerbild, das weiter unten bei der Fehlersuche behandelt wird.

Beide Wege liefern dasselbe Profil an denselben Platz. Wähle nach Bequemlichkeit, nicht aus Angst.

### Aktivierungscode manuell eingeben

Ein QR-Code sind zwei Zeichenketten in Verkleidung: die Adresse des Download-Servers des Anbieters — die SM-DP+-Adresse, die wie eine Web-Domain aussieht — und ein passender Aktivierungscode. Beide kommen in der Bestätigungsmail oder in der App des Anbieters, weshalb die Installation auch dann funktioniert, wenn der Code selbst nicht scannt: ein verwischter Ausdruck, ein komprimierter Screenshot oder ein QR-Code, der auf genau dem Smartphone angezeigt wird, das ihn scannen soll.

Öffne auf dem iPhone *Einstellungen → Mobilfunk → eSIM hinzufügen*, ignoriere die Kamera und tippe unten im Scanner auf **Details manuell eingeben**. Auf Android verbirgt der QR-Bildschirm auf den meisten Oberflächen einen kleinen Link **Code manuell eingeben** oder **Brauchst du Hilfe**, der dieselben Felder öffnet. Gib die SM-DP+-Adresse in das erste Feld und den Aktivierungscode in das zweite. Die beiden Zeichenketten müssen aus derselben Bestätigung stammen — der Server weist ein nicht zusammenpassendes Paar ab, kopiere also beide frisch aus der Mail, statt sie aus dem Gedächtnis neu zu tippen.

## Wann ein eSIM-Tarif tatsächlich beginnt

Anbieter starten die Gültigkeitsuhr auf eine von drei Arten, und jede diktiert einen anderen Installationszeitpunkt:

| Uhr startet | Verhalten | Wann installieren |
|---|---|---|
| Erste Verbindung am Reiseziel | Ruht bis das Smartphone sich in ein Netz im Ausland einbucht | Jeden Tag vor dem Flug |
| Bei der Installation | Läuft ab dem Download des Profils | Ein bis zwei Tage vor der Abreise |
| Erste Nutzung irgendwo | Startet bei der ersten Datensitzung in irgendeinem Land | Kurz vor oder nach der Landung |

Die erste Zeile ist die häufigste und die nachsichtigste: Der Tarif schläft, bis dein Smartphone ein ausländisches Netz berührt. Die zweite bestraft frühe Installationen — ein 7-Tage-Paket, eine Woche vor einer 7-Tage-Reise installiert, kann bei der Landung verbraucht sein. Die dritte klingt wie die erste, unterscheidet sich aber in einem Wort: irgendwo. Ein Tarif, der bei der ersten Nutzung startet und sein erstes Megabyte am Tag der Installation im heimischen Netz bewegt, hat bereits begonnen, obwohl du nie weg warst. Die Tarifbedingungen nennen den Auslöser, und jede Anbieterseite, die wir veröffentlichen, zitiert diese Zeile an derselben Stelle.

## Installierst du eine eSIM vor oder nach dem Flug

Vorher — mit dem Vorbehalt, den die Tabelle gerade geklärt hat. Installiere ein bis drei Tage vorher: spät genug, dass eine Uhr, die bei der Installation startet, keine Tage verbrennt, früh genug, dass jedes Problem im heimischen WLAN passiert, mit Zeit zum Beheben. Ein gesperrtes Smartphone, das am Abfluggate entdeckt wird, hat keinen guten Ausgang; dasselbe Smartphone, am Dienstag entdeckt, ist ein Anruf.

Zwei Situationen rechtfertigen die Installation erst bei der Ankunft: Der Anbieter startet die Uhr bei der ersten Nutzung, oder der Kalender vor der Reise ließ es einfach nie zu. Beide funktionieren — die Ankunftsroutine unten nimmt die Installation einfach als zusätzlichen Schritt auf.

Passe das Gültigkeitsfenster an die tatsächliche Reise an, nicht an die runde Zahl. Länderseiten sortieren jeden Tarif nach Länge, damit der richtige schnell auftaucht — [Japan](/de/compare/japan/) und [Portugal](/de/compare/portugal/) zeigen das Muster.

## eSIM nach der Landung aktivieren

Eine eSIM bei der Ankunft zu aktivieren ist eine kurze Routine, die unter zwei Minuten dauert.

1. **Flugmodus zehn Sekunden lang an und aus.** Ein, bis zehn zählen, aus. Das zwingt das Modem, das zuletzt gesehene Netz fallen zu lassen und alles Verfügbare neu zu scannen.
2. **Prüfe den Daten-Roaming-Schalter der eSIM-Leitung.** Er muss speziell für die eSIM-Leitung an sein; der Roaming-Schalter der Heimatleitung ist ein separater Schalter, der aus bleibt. Bestätige, dass die eSIM auch die für Mobilfunkdaten gewählte Leitung ist.
3. **Gib der Registrierung ein paar Minuten.** Der erste Kontakt mit einem Partnernetz ist nicht sofort, und bei Tarifen mit Erstverbindungsstart beginnt die Uhr in diesem Moment. Eine Minute Geduld ersetzt die meisten Support-Tickets.

Zwei Fehlerzustände sehen ähnlich aus und brauchen unterschiedliche Lösungen.

### Was kein Dienst bei Ankunft bedeutet

**Kein Dienst** bedeutet, dass sich die Leitung nirgends eingebucht hat — ein Profilproblem, ein Paket für das falsche Land oder ein Netz, das der Tarif nicht abdeckt.

### Was volle Balken ohne Daten bedeuten

**Signalbalken ohne Daten** bedeutet, dass die Registrierung geklappt hat und das Problem in den Einstellungen liegt: der Roaming-Schalter, die Wahl der Datenleitung oder ein fehlender APN. Erst Balken, dann Einstellungen — diese Reihenfolge löst die meisten Ankünfte.

## Wenn eine eSIM nicht aktiviert

- **„eSIM kann nicht aktiviert werden"** — meist ein netzgesperrtes Smartphone oder ein QR-Profil, das schon einmal gescannt wurde. Codes sind meist einmalig; der Anbieter muss neu ausstellen.
- **Keine Daten nach der Landung** — Daten-Roaming ist auf der eSIM-Leitung aus, oder das Smartphone leitet Daten weiter über die heimische SIM. Prüfe beides zuerst.
- **Volle Balken aber nichts lädt** — fehlender APN auf Android oder langsame Partnerregistrierung; zehn Sekunden Flugmodus erzwingen ein frisches Einbuchen.
- **Paket für das falsche Land** — lass es sich nicht verbinden. Kontaktiere den Anbieter, bevor die Gültigkeit startet; die meisten tauschen oder erstatten einen ungenutzten Tarif, und die Richtlinie jeder Marke ist in ihren [Anbieterbewertungen](/de/esim-providers/) zusammengefasst.
- **Halb installiertes Profil** — ein Download, der mitten in der Installation abbrach. Lösche das Teilprofil und bitte um eine Neuausstellung, statt den toten QR-Code erneut zu scannen.
- **Kein freier eSIM-Platz** — Smartphones speichern eine begrenzte Zahl von Profilen; aktuelle iPhones halten eine Handvoll mit zwei aktiven, viele Android-Geräte weniger. Gib einen Platz frei, indem du ein nicht mehr genutztes Profil löschst, auf dem iPhone über *Einstellungen → Mobilfunk →* den Tarif → *eSIM löschen*. Das Löschen eines noch gültigen Reiseprofils verbrennt es meist, also prüfe was aktiv ist, bevor du Platz schaffst.
- **Anbieter-App nicht verfügbar** — der App-Store verweigert den Download, weil die Region deines Kontos die App des Anbieters nicht führt. Deshalb gehört der App-Weg nach Hause: installiere und melde dich vor der Abreise an, oder wechsle zu einem QR-basierten Anbieter, wenn es zu spät ist, die Store-Region zu ändern.

## Kannst du eine eSIM auf ein neues Smartphone übertragen

Reise-eSIM-Profile binden sich an das Gerät, das sie installiert hat. Der QR-Code ist verbraucht, das Profil lebt im sicheren Speicher dieses Smartphones, und denselben Code auf einem zweiten Smartphone zu scannen erweckt es nicht wieder.

Die Verwirrung kommt von Apples **Schnellstart**, der Tarife zwischen iPhones überträgt und so aussieht, als müsste er hier greifen. Tut er nicht, aus einem strukturellen Grund: Der Schnellstart bittet die Systeme des Netzbetreibers, den Tarif auf das neue Smartphone zu schieben, und Reise-eSIM-Anbieter nehmen an diesem Vorgang nicht teil. Ihr Gegenstück ist eine Neuausstellung — kontaktiere den Support, bitte um eine Neuausstellung des Profils auf das neue Gerät, und erwarte, dass die alte Installation aufhört zu funktionieren, wenn die neue aktiv wird. Die Richtlinien unterscheiden sich je Marke, also prüfe statt anzunehmen.

Die praktische Regel ist einfacher. Kaufe keinen lang laufenden Tarif in derselben Woche, in der du ein Smartphone-Upgrade planst — installiere Reiseprofile auf dem Smartphone, das die Reise macht.

## Zwei Gewohnheiten gegen 90 % der Probleme

Installiere im heimischen WLAN mit geladenem Smartphone und mach einen Screenshot der Bestätigung — sie enthält den QR-Code, die SM-DP+-Adresse und den Aktivierungscode, also alles, wonach der Support fragen wird. Dann bei der Landung: Flugmodus zehn Sekunden, aus, eine Minute warten. Noch auf Tarifsuche? Der [Preisvergleich](/de/compare/) von eSIM Sift listet jeden Anbieter für dein Reiseziel — [Frankreich](/de/compare/france/) und [Griechenland](/de/compare/greece/) sind beliebte Einstiege — und der [Kostenrechner](/de/tools/) wählt den günstigsten Tarif, der deine Daten und deinen Zeitraum abdeckt.
'''

PAGES = {
    "content/de/guides/what-is-an-esim.md": WHAT_IS.replace("{TODO}", TODO),
    "content/de/guides/how-to-install-esim.md": HOW_TO.replace("{TODO}", TODO),
}

BAD = [",", ";", ":", "\u2014", "\u2013"]


def headings_of(text: str):
    body = text.split("\n---\n", 1)[1] if "\n---\n" in text else text
    out = []
    for line in body.split("\n"):
        if line.startswith("## ") or line.startswith("### "):
            out.append(line.lstrip("# ").strip())
    return out


def faq_questions(text: str):
    fm = text.split("\n---\n", 1)[0]
    out = []
    for line in fm.split("\n"):
        s = line.strip()
        if s.startswith("- q: "):
            out.append(s[5:].strip().strip('"'))
    return out


def main() -> int:
    failures = []
    for rel, content in PAGES.items():
        # 标题标点守卫（h2/h3 + FAQ 问句，模板会把 FAQ q 渲染成 h3）
        for h in headings_of(content) + faq_questions(content):
            for ch in BAD:
                if ch in h:
                    failures.append(f"{rel}: 标题含禁用标点 {ch!r} -> {h!r}")
        # 站内链必须带 /de/ 前缀（排除外链与站内锚点）
        import re
        for m in re.finditer(r"\]\((/[^)]*)\)", content):
            href = m.group(1)
            if href.startswith("/de/") or href.startswith("/#"):
                continue
            failures.append(f"{rel}: 站内链缺 /de/ 前缀 -> {href}")

    if failures:
        print("前置校验失败：")
        for f in failures:
            print("  -", f)
        return 1

    changed = 0
    for rel, content in PAGES.items():
        p = ROOT / rel
        data = content.encode("utf-8")
        if p.exists():
            old = p.read_bytes()
            if old == data:
                print(f"  已是目标内容  {rel}")
                continue
            # 允许覆盖：本脚本是本文件的唯一作者
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_bytes(data)
        b = p.read_bytes()
        assert b"\r\n" not in b, f"{rel} 出现 CRLF"
        print(f"  写入 {rel}  {len(b)} bytes  (h2/h3 {len(headings_of(content))} 个)")
        changed += 1

    print(f"\n写入 {changed} 个文件。")
    return 0


if __name__ == "__main__":
    sys.exit(main())
