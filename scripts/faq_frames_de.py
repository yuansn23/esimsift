#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""德语 FAQ 生成器 —— 写出 data/de/faqs/<iso>.toml（50 国）。

── 与英语侧的关系 ─────────────────────────────────────────────────────────
英语侧 data/faqs/*.toml 由 scripts/faq_frames.py 维护（拉丁方阵分配 + 幂等迁移）。
本文件是它的**德语对应物**，用**同一套拉丁方阵**（i%7, i//7, (a+b)%7）——
所以德语页的修辞结构逐国镜像英语页，且任意两国至多共用一句（同一个不变量）。

── 三条纪律 ───────────────────────────────────────────────────────────────
① **只用已注册的 token**。德语额外需要 `{country_acc}`（für / über 后）与
   `{country_dat}`（in / von / bei 后）—— 德语介词支配格，裸名会写出
   「für Türkei」这种错句。两个 token 已在 layouts/partials/faq-live-tokens.html
   注册（英语侧不用它们，故英语产物恒等）。data/de/countries.toml 里
   name_acc / name_dat 只给需要冠词的 7 国写了值，其余回退裸名。
② **数字与品牌名一律走 token**，德语片段里不得出现 `${...}` 写死价格。
   价格锚点由 faq-live-tokens.html 构建期现算 —— 与英语页读同一个值。
③ **能转录就别重算**：Q5 的运营商清单、Q4 的标准句式判据，都从英语侧读出来，
   不在这里重新推导。只有德语译文本身是新写的。

运行：
    python -X utf8 scripts/faq_frames_de.py            # 只报告
    python -X utf8 scripts/faq_frames_de.py --write    # 写 data/de/faqs/*.toml
"""
from __future__ import annotations

import io
import json
import re
import sys
import tomllib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
EN_FAQ = ROOT / "data" / "faqs"
DE_FAQ = ROOT / "data" / "de" / "faqs"

POOL = 7

# ══════════════════════════════════════════════════════════════════════════════
# Q1 最便宜 —— open 必须含 {cheap_brand} 与 ${cheap_price}
# ══════════════════════════════════════════════════════════════════════════════
Q1 = {
    "open": [
        "{cheap_plan} von {cheap_brand} ist der günstigste Tarif für {country_acc} – ${cheap_price}.",
        "Beim Einstiegspreis liegt {cheap_brand} für {country_acc} vorn: {cheap_plan} für ${cheap_price}.",
        "Der niedrigste Preis auf dieser Seite: {cheap_plan} von {cheap_brand} für ${cheap_price}.",
        "{cheap_brand} hält für {country_acc} die Bestmarke: {cheap_plan} für ${cheap_price}.",
        "Günstigster Tarif für {country_acc}: {cheap_plan} von {cheap_brand}, ${cheap_price}.",
        "Starte mit {cheap_brand}: {cheap_plan} ist mit ${cheap_price} der günstigste Tarif für {country_acc}.",
        "Für ${cheap_price} ist {cheap_plan} von {cheap_brand} der günstigste Weg ins Netz in {country_dat}.",
    ],
    "body": [
        "Das ergibt ${cheap_perday} pro Tag über die Laufzeit des Tarifs.",
        "Über die {plan_count} Tarife für {country_acc} von {brand_count} Anbietern auf dieser Seite liegt der beste Preis pro Gigabyte bei {value_plan} von {value_brand} mit ${value_pergb}/GB.",
        "Der nächstgünstigere Anbieter ist {runner_brand} mit ${runner_price}.",
        "Preis und Gegenwert sind zwei verschiedene Messungen, und pro Gigabyte gewinnt {value_plan} von {value_brand} mit ${value_pergb}/GB.",
        "Das sind ${cheap_perday} pro Tag, was eher zu einem kurzen Aufenthalt passt als zu einem langen.",
        "Der beste Wert pro Gigabyte ist eine eigene Frage, und die Antwort lautet hier {value_plan} von {value_brand} mit ${value_pergb}/GB.",
        "{runner_brand} folgt mit ${runner_price}, und die stärkste Rate pro Gigabyte kommt von {value_plan} von {value_brand} mit ${value_pergb}/GB.",
    ],
    "close": [
        "Richte den Tarif nach deiner Reisedauer statt nach der niedrigsten Zahl.",
        "Lege zuerst Tage und ungefähren Datenbedarf fest und wähle dann den Tarif, der zu beidem passt.",
        "Kleine Pakete passen zu Städtereisen, bei längeren Aufenthalten ist ein größerer Tarif pro Gigabyte meist günstiger.",
        "Wenn du nur Karten und Nachrichten brauchst, reicht der Einstiegspreis, und wer streamt, sollte nach $/GB wählen.",
        "Prüfe neben dem Preis auch die Gültigkeitsdauer, denn ein billiger Tarif, der früh abläuft, ist nicht billig.",
        "Die Tabelle oben sortiert jede Option, vergleiche also auch die Form eines Tarifs und nicht nur den Preis.",
        "Kaufe für die Reise, die du wirklich machst, und nicht für die niedrigste Zahl auf der Seite.",
    ],
}

# ══════════════════════════════════════════════════════════════════════════════
# Q2 真的无限吗 —— open 必须含独立成词的 {unl_count}；body 含 {unl_brand} 与 ${unl_perday}
# ⚠ {unl_count} 前后必须带空格（守卫用 " N " 匹配）
# ⚠ {unl_allowance} 的值可能是整句，只能放在冒号之后
# ══════════════════════════════════════════════════════════════════════════════
Q2 = {
    "open": [
        "Nicht ganz – alle {unl_count} unbegrenzten Tarife für {country_acc} haben eine Fair-Use-Regel.",
        "Nein. Jeder der {unl_count} unbegrenzten Tarife für {country_acc} deckelt sein Tagesvolumen bei voller Geschwindigkeit.",
        "Groß statt grenzenlos: {unl_count} unbegrenzte Tarife für {country_acc} unterliegen Fair-Use-Regeln.",
        "Gedeckelt statt unbegrenzt – die {unl_count} unbegrenzten Tarife für {country_acc} drosseln, sobald das Tagesvolumen aufgebraucht ist.",
        "Nur innerhalb der Grenzen. Die {unl_count} unbegrenzten Tarife für {country_acc} fallen nach einem festgelegten Tagesvolumen auf eine veröffentlichte Geschwindigkeit zurück.",
        "Unbegrenzt heißt hier unbegrenztes Datenvolumen und nicht unbegrenzte Geschwindigkeit: {unl_count} Tarife für {country_acc} setzen Fair-Use-Grenzen.",
        "Behandle sie als gedeckelt: {unl_count} unbegrenzte Tarife für {country_acc} nennen jeweils ein Tagesvolumen und eine Rückfallgeschwindigkeit.",
    ],
    "body": [
        "Die Tagessätze liegen zwischen {unl_perday_range}, und der günstigste ist {unl_brand} mit ${unl_perday}/Tag – ${unl_price} für {unl_days} Tage.",
        "{unl_brand} bietet den besten Tagessatz mit ${unl_perday} ({unl_days} Tage für ${unl_price}), gegenüber einer Marktspanne von {unl_perday_range}.",
        "Die Spanne ist weit – {unl_perday_range} pro Tag – und {unl_brand} liegt mit ${unl_perday}/Tag über {unl_days} Tage am unteren Ende.",
        "{unl_brand} ist pro Tag am günstigsten mit ${unl_perday}, und die volle Spanne reicht hier über {unl_perday_range}.",
        "Die Laufzeit bewegt den Satz ebenso wie die Grenze: {unl_perday_range} pro Tag über die Auswahl, mit {unl_brand} am niedrigsten bei ${unl_perday} für {unl_days} Tage.",
        "Der beste Tagessatz gehört {unl_brand} – ${unl_perday} für ein Paket über {unl_days} Tage zu ${unl_price} – und der Markt reicht über {unl_perday_range}.",
        "Die Preise liegen je nach Laufzeit bei {unl_perday_range} pro Tag, und {unl_brand} ist mit ${unl_perday}/Tag am günstigsten.",
    ],
    "close": [
        "Was {unl_brand} veröffentlicht: {unl_allowance}; danach {unl_drop}.",
        "Was viele übersehen, ist das, was nach der Grenze passiert: {unl_drop}.",
        "Zwei Werte entscheiden, ob ein gedeckelter Tarif zu dir passt, und {unl_brand} nennt beide: {unl_allowance}, dann {unl_drop}.",
        "Prüfe die Rückfallgeschwindigkeit vor dem Kauf, denn das ist das, was du nach dem Tagesvolumen bekommst: {unl_drop}.",
        "Nimm die veröffentlichten Bedingungen als echte Grenze: {unl_allowance}, dann {unl_drop}.",
        "Drosselung statt Abschaltung ist der Kompromiss, mit Geschwindigkeiten bis hinunter zu {unl_drop}, sobald das Volumen aufgebraucht ist.",
        "Vergleiche die Grenzen der Anbieter vor dem Kauf, denn die gedrosselte Geschwindigkeit ist der entscheidende Wert, und bei {unl_brand} ist sie {unl_drop}.",
    ],
}

# ══════════════════════════════════════════════════════════════════════════════
# Q3 Airalo 还是 Holafly —— body 含 ${ah_airalo_pergb}；close 含 ${ah_holafly_price}
# ══════════════════════════════════════════════════════════════════════════════
Q3 = {
    "open": [
        "Sie verkaufen verschiedene Dinge, die Antwort hängt also davon ab, wie du Daten nutzt.",
        "Verschiedene Produkte: Airalo verkauft feste Datenpakete, Holafly verkauft unbegrenzte Tage.",
        "Keiner von beiden ist der günstigste Tarif auf dieser Seite, und sie konkurrieren auch nicht zu denselben Bedingungen.",
        "Es kommt auf die Form an – Datenpakete gegen unbegrenzte Tage.",
        "Wähle nach Nutzungsmuster, denn die beiden Marken bepreisen ganz unterschiedlich.",
        "Airalo und Holafly lösen verschiedene Probleme, vergleiche also die Modelle vor den Preisen.",
        "Die ehrliche Antwort ist, dass diese beiden nicht austauschbar sind.",
    ],
    "body": [
        "Die beste Rate von Airalo für {country_acc} ist ${ah_airalo_pergb}/GB – {ah_airalo_plan} für ${ah_airalo_price} – und das ist ein festes Paket statt eines Tagesvolumens.",
        "Airalo verkauft Pakete: Die schärfste Rate für {country_acc} ist ${ah_airalo_pergb}/GB ({ah_airalo_plan}, ${ah_airalo_price}).",
        "Auf Airalos Seite ist der beste Wert ${ah_airalo_pergb}/GB – {ah_airalo_plan} für ${ah_airalo_price} – pro Gigabyte bepreist statt pro Tag.",
        "{ah_airalo_plan} von Airalo ergibt ${ah_airalo_pergb}/GB für ${ah_airalo_price}, und was du kaufst, ist was du bekommst.",
        "Für {country_acc} ist Airalos günstigste Rate pro Gigabyte ${ah_airalo_pergb} ({ah_airalo_plan}, ${ah_airalo_price}).",
        "Airalos Angebot für {country_acc} ist ein Datenpaket – {ah_airalo_plan} für ${ah_airalo_price}, oder ${ah_airalo_pergb}/GB an der schärfsten Stelle.",
        "Airalos stärkstes Angebot für {country_acc} ist ${ah_airalo_pergb}/GB, verkauft als {ah_airalo_plan} für ${ah_airalo_price}.",
    ],
    "close": [
        "Holafly verkauft stattdessen unbegrenzte Tage, das kleinste Paket für {country_acc} umfasst {ah_holafly_days} Tage für ${ah_holafly_price} (${ah_holafly_perday}/Tag).",
        "Holaflys Modell ist täglich unbegrenzt, ab {ah_holafly_days} Tagen für ${ah_holafly_price} – ${ah_holafly_perday}/Tag – schwere Nutzung kostet also dasselbe wie leichte.",
        "Holafly verkauft nur tageweise unbegrenzt: {ah_holafly_days} Tage für ${ah_holafly_price}, oder ${ah_holafly_perday} pro Tag.",
        "Nimm Holafly, wenn du lieber keine Gigabyte zählst, denn seine Pakete für {country_acc} beginnen bei ${ah_holafly_price} für {ah_holafly_days} Tage (${ah_holafly_perday}/Tag); nimm Airalo für eine leichte, kurze Reise.",
        "Holaflys Einstiegspreis für {country_acc} ist ${ah_holafly_price} über {ah_holafly_days} Tage (${ah_holafly_perday}/Tag), ohne Datenzähler zum Beobachten.",
        "Die Flatrate-Option ist Holafly, mit {ah_holafly_days} Tagen ab ${ah_holafly_price} – ${ah_holafly_perday}/Tag, egal wie viel du nutzt.",
        "Wo Holafly gewinnt, ist die Planbarkeit, ab ${ah_holafly_price} für {ah_holafly_days} Tage (${ah_holafly_perday}/Tag), und wo Airalo gewinnt, ist eine kurze, leichte Reise.",
    ],
}

# ══════════════════════════════════════════════════════════════════════════════
# Q6 一张 eSIM 能覆盖 X 和邻国吗 —— 每个变体都必须含 {country_acc}
# ⚠ {neighbor} / {neighbors_all} 的无邻国兜底是小写短语，不能让它们起句
# ⚠ 不用「nach + 邻国」（支配与格）—— 只让邻国出现在宾格位置（nach 换成「mitzunehmen」等）
# ══════════════════════════════════════════════════════════════════════════════
Q6 = [
    "Nicht mit einem Ein-Land-Tarif. Alles in unseren Tabellen gilt nur für {country_acc}, eine Reise, die auch {neighbor} einschließt, braucht also einen zweiten Landestarif oder ein regionales Paket.",
    "Nur mit einem regionalen Paket, denn die Landestarife auf dieser Seite überschreiten keine Grenzen. Die Märkte rund um {country_acc} haben hier eigene Tabellen – {neighbors_all} gehören dazu – rechne ein regionales Paket also gegen zwei Einzeltarife.",
    "Nicht mit einem Landestarif allein, weil Tarife für {country_acc} an der Grenze enden. {neighbor} dazu bedeutet ein regionales Paket oder einen zweiten Tarif, und diese Rechnung lohnt sich vor dem Kauf.",
    "Nicht mit einem Ein-Land-Tarif. Führt die Reise von {country_dat} weiter, und {neighbor} soll dabei sein, vergleiche ein regionales Paket mit zwei separaten Tarifen, denn die Tabellen hier bepreisen jeden Markt für sich.",
    "Ja, aber nur über einen Multi-Land-Tarif, denn nichts in unseren Tabellen für {country_acc} deckt ein zweites Land ab. Suche ein regionales Paket, das {neighbor} einschließt, und vergleiche dessen $/GB mit zwei Einzeltarifen.",
    "Ein Land pro Tarif, eine für {country_acc} gekaufte eSIM endet also an der Grenze. Ein regionales Paket oder ein zweiter Tarif bringt {neighbor} dazu, und beide lohnen den Vergleich mit zwei Einzelkäufen.",
    "Nur über einen regionalen Tarif, denn die Tabellen für {country_acc} gelten für einen Markt. Um {neighbor} mitzunehmen, brauchst du ein regionales Paket oder einen zweiten Tarif – der Preis pro Gigabyte unterscheidet sie.",
]

# ══════════════════════════════════════════════════════════════════════════════
# Q7 这国能用 eSIM 吗
# ══════════════════════════════════════════════════════════════════════════════
Q7 = {
    "open": [
        "Ja – {brand_count} Anbieter verkaufen Tarife für {country_acc}; das Land gehört zur üblichen Reise-eSIM-Landkarte.",
        "Eine eSIM funktioniert in {country_dat}, und nichts am Reiseziel verhindert das.",
        "Ja, es funktioniert. Keine länderspezifische Sperre steht zwischen einer Reise-eSIM und den Netzen in {country_dat}.",
        "Ja, und in dieser Hinsicht gibt es keine Besonderheit – keine lokale Registrierung und keine Genehmigung nötig.",
        "Für {country_acc} sind {plan_count} Tarife von {brand_count} Anbietern gelistet, und jeder davon ist nutzbar.",
        "Reise-eSIMs für {country_acc} werden von jedem Anbieter verkauft, den wir führen, und keiner braucht eine lokale Adresse.",
        "Ja – was eine eSIM in {country_dat} stoppen kann, liegt auf deiner Seite und nicht am Land.",
    ],
    "body": [
        "Alle {plan_count} Tarife in unserer Tabelle für {country_acc} registrieren sich in den heimischen Netzen statt im Roaming, es gibt also keine Abdeckungshürde.",
        "Die Wahl dreht sich hier um Preis und Volumen und nicht um Verfügbarkeit: {plan_count} Tarife von {brand_count} Anbietern.",
        "{brand_count} Anbieter verkaufen {plan_count} separate Tarife für {country_acc} auf dieser Seite – ein Markt zu groß, als dass Verfügbarkeit die Einschränkung wäre.",
        "Von den {plan_count} hier gelisteten Tarifen für {country_acc} ist keiner auf eine bestimmte Region des Landes begrenzt.",
        "Was variiert, ist der Preis und nicht der Zugang – {plan_count} Tarife von {brand_count} Anbietern, alle in denselben nationalen Netzen.",
        "Die Verfügbarkeit ist mit den {plan_count} oben gelisteten Tarifen geklärt, offen sind also Dauer und Datenvolumen.",
        "Jeder der {brand_count} Anbieter hier verkauft Tarife für {country_acc} – das beantwortet die Frage, ob eSIMs dort funktionieren, bereits.",
    ],
    "close": [
        "Prüfe zuerst dein Handy und wähle dann den Tarif, der zu deiner Reisedauer passt.",
        "Mach den Kompatibilitätstest und vergleiche die Tarife oben nach $/GB und $/Tag.",
        "Kläre die Handy-Frage, den Rest erledigt der Vergleich oben.",
        "Bestätige, dass das Gerät eSIM unterstützt und entsperrt ist, und wähle dann aus der Tabelle oben.",
        "Der Gerätecheck dauert dreißig Sekunden, und die Tarife oben sind alle auf einer Skala bepreist.",
        "Prüfe dein Handy und lass dann die $/GB-Spalte zwischen den Tarifen oben entscheiden.",
        "Kläre die Handy-Frage vor dem Kauf und vergleiche den Rest über den Preis.",
    ],
}

# ══════════════════════════════════════════════════════════════════════════════
# Q8 我的手机行不行
# ══════════════════════════════════════════════════════════════════════════════
Q8 = {
    "open": [
        "Wenn dein Handy eSIM unterstützt und keinen Netlock hat, funktioniert es in {country_dat} – das Reiseziel hat darauf keinen Einfluss.",
        "Dein Gerät entscheidet hier, nicht das Reiseziel.",
        "Es hängt vom Gerät ab und nicht vom Land, denn jeder Tarif auf dieser Seite ist ein Standard-eSIM-Profil.",
        "Derselbe Test wie überall: Wähle *#06# und suche eine EID-Nummer.",
        "Ein eSIM-fähiges, entsperrtes Handy funktioniert in {country_dat} ohne zusätzlichen Schritt.",
        "Kompatibilität ist reine Gerätesache, und das Reiseziel stellt keine eigene Anforderung.",
        "Ja, sofern das Handy eSIM-Hardware hat und keinen Netlock trägt.",
    ],
    "body": [
        "Regionale Varianten sind die Falle, die es zu prüfen gilt: Dasselbe Modell kann je nach Verkaufsmarkt mit oder ohne eSIM-Chip ausgeliefert werden.",
        "Die zwei entscheidenden Prüfungen sind Hardware und Sperrstatus – die {plan_count} Tarife hier installieren auf einem Handy, das beide besteht, und scheitern an einem, das eine nicht besteht.",
        "Veröffentlichte Kompatibilitätslisten hinken neuen Modellen hinterher, der Test im Wählfeld an deinem eigenen Gerät schlägt also jede Liste, auch unsere.",
        "Der eSIM-Chip ist bei der Fertigung festgelegt, ein ohne ihn gebautes Handy kann ihn später nicht erhalten, egal wie viele Tarife für {country_acc} wir listen.",
        "Ein in einem anderen Markt gekauftes Gerät ist der übliche Auslöser, und das hat nichts mit {country_dat} selbst zu tun.",
        "Von den {plan_count} Tarifen für {country_acc} auf dieser Seite braucht keiner mehr als ein Standard-eSIM-Profil.",
        "Keiner der {brand_count} Anbieter hier verlangt ein bestimmtes Handy, nur dass das Gerät den Chip hat und entsperrt ist.",
    ],
    "close": [
        "Mach den *#06#-Test vor dem Tarifkauf.",
        "Prüfe zuerst auf eine EID-Nummer und einen Netlock ohne Einschränkungen.",
        "Kläre beide Prüfungen zu Hause im WLAN statt am Flughafen.",
        "Teste das Handy jetzt, dann wird die Tarifwahl eine Preisfrage statt einer Kompatibilitätsfrage.",
        "Bestätige, dass die EID erscheint, und vergleiche dann die Tarife oben.",
        "Prüfe zuerst das Gerät, denn die Tarife oben helfen nur, wenn es besteht.",
        "Mach die zwei Prüfungen und komm zur Tabelle oben zurück.",
    ],
}

# ══════════════════════════════════════════════════════════════════════════════
# Q9 要不要本地号码
# ══════════════════════════════════════════════════════════════════════════════
Q9 = {
    "open": [
        "Für eine normale Reise nicht – eine Reise-eSIM für {country_acc} ist ein Datenprodukt und keine Telefonleitung.",
        "Eine lokale Nummer ist nicht nötig, um in {country_dat} eine eSIM zu nutzen.",
        "Nein, außer du brauchst ausdrücklich Anrufe über eine lokale Nummer.",
        "Für Nachrichten und Karten brauchst du keine.",
        "Nur wenn lokale Anrufe für dich zählen, denn die {plan_count} hier gelisteten Tarife für {country_acc} sind Datenprodukte.",
        "Für Besucher nicht. Eine eSIM für {country_acc} gibt dir Konnektivität, die Nummer bleibt bei deiner Heimleitung.",
        "Mit einer Reise-eSIM für {country_acc} wird keine Nummer ausgegeben.",
    ],
    "body": [
        "Sprache ist meist nicht Teil des Angebots, und Anrufe laufen über eine App statt über das Mobilfunknetz.",
        "Die Heimleitung im physischen Slot zu lassen ist die übliche Lösung, und nur so kommen Verifizierungscodes weiterhin an.",
        "Zwei-Faktor-Codes sind der übliche Grund für die Frage, und die kommen über die Heimleitung an, solange sie aktiv bleibt.",
        "Wo Sprache existiert, ist sie app-basiert statt eine echte lokale Nummer – was die meisten Reisenden tatsächlich brauchen.",
        "Reise-eSIMs werden als Daten verkauft, wer eine für Sprache kauft, zahlt für das falsche Produkt.",
        "Wenn wirklich eine lokale Nummer nötig ist, bedeutet das den Kauf einer lokalen SIM und meist eine Registrierung im Laden.",
        "Die praktische Aufteilung ist Daten auf der eSIM und die bestehende Nummer auf der physischen SIM, mit ausgeschaltetem Roaming auf der Heimleitung.",
    ],
    "close": [
        "Lass deine Heim-SIM für Anrufe und Codes aktiv und lass die eSIM die Daten tragen.",
        "Plane Daten von der eSIM und deine bestehende Nummer von der Heimleitung.",
        "Entscheide, ob du wirklich eine lokale Nummer brauchst, bevor du einen zweiten Kauf machst.",
        "Lass die Heimleitung im Handy und schalte ihre Daten ab.",
        "Nutze die eSIM für Daten und die Heimleitung für alles, was die Nummer braucht.",
        "Füge nur dann eine lokale SIM hinzu, wenn lokale Anrufe eine echte Anforderung sind.",
        "Lass beide Leitungen im Handy und stelle Daten auf die eSIM.",
    ],
}

# ══════════════════════════════════════════════════════════════════════════════
# Q10 口碑 / 评价
# ══════════════════════════════════════════════════════════════════════════════
Q10 = {
    "open": [
        "Wir bündeln keine Bewertungen, die ehrliche Antwort hier betrifft also die Methode und nicht die Noten.",
        "Bewertungsnoten lassen wir bewusst weg, weil eine einzelne Zahl die Streuung dahinter verbirgt.",
        "Statt einer Sternebewertung beantwortet diese Seite die Frage mit Zahlen.",
        "Wir führen keine Bewertung für eSIMs in {country_dat}, und das ist eine Entscheidung und kein Versehen.",
        "Die Bewertungen selbst stehen auf den Seiten der Anbieter und in den App-Stores.",
        "Kein aggregierter Wert von uns. Was diese Seite stattdessen bietet, ist die Rechnung.",
        "Wir beantworten die Bewertungsfrage mit Messung statt mit Gefühl.",
    ],
    "body": [
        "Der Grund: Dieselbe Marke schneidet je nach Region des Bewerters anders ab, eine einzelne Zahl als Wahrheit zu zitieren wäre irreführend.",
        "Fair-Use-Bedingungen, Hotspot-Regeln und Rückerstattungsfristen sind die Stellen, an denen die echten Unterschiede liegen, und die sind dokumentiert statt gewählt.",
        "Preis, Volumen und die Fair-Use-Schwelle sind prüfbare Fakten, und genau die stellen die Tabellen oben nebeneinander.",
        "Ein Fünf-Sterne-Schnitt und ein Ein-Stern-Schnitt beschreiben meist verschiedene Reisen statt verschiedene Produkte.",
        "Die veröffentlichten Bedingungen sind der Teil, den niemand bewertet und jeder lesen sollte, deshalb zitieren wir sie.",
        "Wo ein Anbieter seine eigene Support- und Rückerstattungsrichtlinie veröffentlicht, verlinken wir sie direkt, damit du die Quelle liest statt einer Zusammenfassung.",
        "Der Vergleich oben schickt alle {plan_count} Tarife für {country_acc} von {brand_count} Anbietern durch eine Formel – was keine Bewertungsseite behaupten kann.",
    ],
    "close": [
        "Lies zuerst die Zahlen oben und prüfe dann die eigenen Bewertungen des Anbieters für die menschliche Seite.",
        "Nutze die Tabellen oben für die Fakten und die eigenen Kanäle des Anbieters für die Stimmung.",
        "Vergleiche die Tarife oben nach Preis und lies dann die Bedingungen des Anbieters vor dem Kauf.",
        "Nimm die Zahlen oben als Grundlage und prüfe die Rückgaberichtlinie an der Quelle.",
        "Der gemessene Vergleich steht oben, und Meinungen liest man am besten dort, wo sie gepostet wurden.",
        "Prüfe die Fair-Use- und Rückerstattungsseiten des Anbieters direkt, bevor du dich festlegst.",
        "Nimm die Tabellen oben als die prüfbare Hälfte und lies Bewertungen für den Rest.",
    ],
}

# ── Q4 身份验证：标准句式（35 国）+ 15 国例外（德语逐国写）───────────────────
Q4_TPL = ("Nein – für Reise-eSIMs in {country_dat} ist kein Identitätsnachweis nötig. Die Regeln "
          "für lokale SIM-Karten unterscheiden sich, aber die Tarife auf dieser Seite kommen vorregistriert.")

Q4_EXC = {
    "AE": "Ja – eine Touristen-SIM für die VAE verlangt beim Kauf einen Passscan, und die Anbieter, die wir führen, behalten denselben Schritt in ihrer App oder im Checkout. Eine Emirates ID ist nicht nötig, was die eSIM für einen kurzen Aufenthalt zum schnellen Weg macht.",
    "AR": "Ja, und es kostet dich nichts. Die Registrierung einer lokalen SIM verlangt von Einwohnern eine DNI und von Besuchern einen Pass-Durchlauf, während eine Reise-eSIM für Argentinien vom Verkäufer beim Kauf registriert wird. Kauf vorab, und die Regel berührt deine Reise nie.",
    "CN": "Das ist das eine Reiseziel, bei dem die Frage in die falsche Richtung zeigt. Eine Reise-eSIM für das Festland von China verlangt von dir keinen Identitätsschritt, weil die Registrierung außerhalb des Landes passiert – und genau deshalb erreicht sie Google und WhatsApp ohne VPN, was eine lokale SIM nicht kann.",
    "EG": "Ja, und der Weg über die eSIM ist der, der den Papierkram vermeidet. Eine lokale ägyptische SIM zu registrieren bedeutet Passfotos in einem offiziellen Laden, während eine Reise-eSIM vom Anbieter im Checkout registriert wird – nichts mitzubringen und kein Büro zu finden.",
    "ID": "Ja – indonesisches Recht verlangt einen Pass-Upload, wenn eine eSIM registriert wird, und die Anbieter sammeln ihn beim Kauf ein. Das vor dem Flug zu erledigen lohnt sich hier, weil der Archipel sein gutes Signal ungleich verteilt: Telkomsel hält außerhalb von Java und Bali durch, wo günstigere Tarife auf Indosat-Basis es nicht tun.",
    "IL": "Ja – israelisches Recht verlangt für jede SIM-Leitung einen Ausweis, und Reise-eSIMs sind nicht ausgenommen. Der Anbieter sammelt ihn beim Kauf ein, die Frage, die einen Israel-Kauf wirklich entscheidet, ist also, über welches Netz der Tarif läuft, und nicht, wie die Registrierung abläuft.",
    "IN": "Ja. Indische Regeln binden die Registrierung auch bei Reise-eSIMs an einen Pass, und die Anbieter, die wir führen, schließen diese Prüfung in etwa zwei Minuten in der App ab. Erledige sie im Heim-WLAN: Die Prüfung ist schnell, aber sie nach der Landung zu machen kostet dich die erste Stunde der Reise.",
    "KE": "Ja. Eine lokale kenianische SIM zu registrieren bedeutet, einen Pass persönlich vorzulegen, während ein Reise-eSIM-Anbieter dieselbe Prüfung digital beim Kauf durchführt. Das ist der ganze Unterschied – kein Gang zu einem Safaricom-Laden – und die Abdeckung folgt trotzdem dem Netz, über das der Tarif läuft.",
    "MA": "Ja – marokkanische SIMs werden gegen einen Pass registriert, und die Verkäufer, die wir führen, sammeln ihn beim eSIM-Kauf ein statt an einem Maroc-Telecom-Schalter. Vor Ort ist das Signal in der Altstadt das größere Hindernis: Die Gassen der Medina in Fes überfordern jedes Netz, nimm also Offline-Karten mit.",
    "MX": "Ja, aber nicht über denselben Weg wie eine lokale Leitung. Die mexikanische Registrierung einer lokalen SIM läuft über eine CURP oder eine persönliche Ausweisprüfung, während eine Reise-eSIM vom Anbieter beim Kauf registriert wird – die Reise selbst ändert sich nur darin, dass du den Schalter überspringst.",
    "PH": "Ja, und es ist ein Selfie-Schritt statt eines Formulars. Die philippinische SIM-Registrierung verlangt ein Ausweis-Selfie, und ein eSIM-Kauf läuft durch dieselbe Prüfung. Einmal erledigt, funktionieren deine Daten in dem Netz, das die Insel deiner Wahl abdeckt, denn Smart und Globe ergänzen sich statt austauschbar zu sein.",
    "SA": "Ja. Saudische Touristen-eSIMs verlangen Passdaten, und die Anbieter, die wir führen, prüfen sie in der App innerhalb weniger Minuten. Es gibt keinen lokalen Bürgen und keinen Adress-Schritt, die Registrierung sollte einen Kauf also nicht aufhalten.",
    "TR": "Ja – türkische SIM-Regeln binden die Registrierung an einen Pass, und die Verkäufer, die wir führen, sammeln die Daten beim Checkout ein statt über einen Schalter. Das ist der praktische Unterschied zu einem Turkcell-Touristenpaket: kein Flughafenschalter, keine Schlange, und das Profil ist schon auf deinem Handy, wenn du landest.",
    "VN": "Ja, Vietnam registriert jede SIM gegen einen Pass und Reise-eSIMs sind keine Ausnahme, rechne also mit einem schnellen Ausweis-Upload beim Kauf. Er passiert im Checkout des Anbieters statt an einem Schalter, und eine vietnamesische Adresse ist nicht nötig. Viettel ist das Netz, auf das die meisten Reisetarife zurückgreifen, weshalb sie auch auf der Halong-Bucht und den Bergrouten des Nordens durchhalten.",
    # JP 不在此表：jp 全 10 条手写，见下方 JP_PAIRS
}

# ── Q5 网络：德语模板（运营商清单从英语侧转录）+ JP 特殊 ────────────────────
Q5_TPL = ("Die Tarife auf dieser Seite laufen über {carriers}. Unterschiede zeigen sich vor allem "
          "außerhalb der großen Städte – die Netz-Spalte in der Haupttabelle zeigt, über welches Netz jeder Tarif läuft.")

Q5_JP = ("Alle. Jeder Anbieter, den wir führen – {brands_list} – verbindet sich mit denselben drei "
         "nationalen Netzen in Japan (NTT Docomo, SoftBank und KDDI), die Marke auf dem Voucher entscheidet "
         "also nicht über deine Abdeckung. Was sich zwischen Anbietern unterscheidet, sind Preis pro GB, "
         "Tarifformen, Hotspot-Regeln und Support. Docomo hat die weiteste Reichweite auf dem Land, was auf "
         "Bergrouten und beim Inselhüpfen zählt, aber weil jeder Japan-Tarif, den wir listen, auf alle drei "
         "Netze zurückfällt, wählt dein Handy das stärkste verfügbare Signal statt an einem Mast zu hängen.")

# ── JP：10 条手写德语（保留英语侧的分析口吻）────────────────────────────────
JP_PAIRS = [
    ("Was ist die günstigste eSIM für Japan?",
     "Unter den großen Anbietern hat {cheap_brand} derzeit den niedrigsten Einstiegspreis für {country}, nämlich ${cheap_price} für das Paket {cheap_plan}, und {runner_brand} ist mit ${runner_price} der nächste Verfolger. Wenn du nur Karten und Nachrichten brauchst, deckt jeder der beiden Tarife eine kurze Städtereise ab – aber pro GB ist {value_plan} von {value_brand} mit ${value_pergb}/GB der stärkste Wert, den wir führen."),
    ("Ist unbegrenztes eSIM-Datenvolumen in Japan wirklich unbegrenzt?",
     "Nur innerhalb der Grenzen. Jeder der {unl_count} unbegrenzten Tarife, die wir für {country} führen, deckelt das Volumen bei voller Geschwindigkeit pro Tag und drosselt dann, und der Tagessatz liegt über alle hinweg zwischen {unl_perday_range}. Am günstigsten pro Tag ist {unl_brand} mit ${unl_price} für {unl_days} Tage (${unl_perday}/Tag); veröffentlicht: Volumen {unl_allowance}, danach {unl_drop}. Lies den Tagespreis und die Fair-Use-Grenze zusammen, bevor du kaufst."),
    ("Ist Airalo oder Holafly besser für Japan?",
     "Verschiedene Produkte, es hängt also davon ab, wie du Daten nutzt. Airalo verkauft feste Pakete – die beste Rate für {country} ist ${ah_airalo_pergb}/GB ({ah_airalo_plan} für ${ah_airalo_price}) – was leichte Nutzung bedient und die Fair-Use-Frage ganz umgeht. Holafly verkauft unbegrenzte Daten nur tageweise, ab ${ah_holafly_price} für {ah_holafly_days} Tage (${ah_holafly_perday}/Tag), was starke Streamer bedient, die keine Gigabyte zählen wollen. Für dieselbe Datenmenge ist keiner von beiden der günstigste auf dieser Seite: {cheap_brand} führt mit ${cheap_price}."),
    ("Brauche ich einen Reisepass oder Ausweis für eine eSIM in Japan?",
     "Nein – nicht bei Reise-eSIMs. Das japanische Recht verlangt eine Passprüfung für lokale Prepaid-SIM-Karten von SoftBank, NTT Docomo und KDDI, aber Reise-eSIMs umgehen diese Registrierung vollständig. Jede Marke, die wir für Japan führen, verkauft ohne Dokumenten-Upload: kaufen, QR-Code scannen, verbinden."),
    ("Welches japanische Netz nutzt welcher Anbieter?",
     Q5_JP),
    ("Kann eine eSIM Japan und Südkorea auf derselben Reise abdecken?",
     "Ja – mehrere Anbieter verkaufen regionale Asien-Pakete, die Japan mit Korea, Taiwan und Hongkong bündeln. Wenn du zwei oder mehr Länder besuchst, schlägt ein regionales Paket meist den Kauf separater Landes-eSIMs. Prüfe unseren Regionalvergleich, bevor du zwei Einzeltarife kaufst."),
    ("Kann ich eine eSIM in Japan nutzen?",
     "Eine eSIM funktioniert in Japan wie überall sonst: Das Profil registriert sich bei der Landung in einem japanischen Netz, und nichts am Land blockiert es. Alle {brand_count} Anbieter, die wir führen, verkaufen Japan-Tarife, und die {plan_count} oben gelisteten Pakete verbinden sich mit denselben drei nationalen Netzen. Was über den Erfolg entscheidet, ist dein Handy und nicht das Reiseziel."),
    ("Funktioniert mein Handy mit einer eSIM in Japan?",
     "Japan stellt keine eigene Handy-Anforderung, ein eSIM-fähiges und entsperrtes Handy funktioniert also mit den Tarifen auf dieser Seite. Die Falle ist das Handy und nicht das Land: Dasselbe Modell kann je nach Verkaufsmarkt mit oder ohne eSIM-Chip ausgeliefert werden, und ein in Festlandchina gekauftes Gerät hat gar keinen Chip. Wähle *#06# vor dem Kauf; erscheint eine EID-Nummer, installiert sich ein Japan-Tarif."),
    ("Brauche ich eine lokale Nummer in Japan?",
     "Eine japanische Telefonnummer ist für eine Reise-eSIM nicht nötig, und die Tarife auf dieser Seite sind reine Datenprodukte. Lokale Sprach-SIMs in Japan gehen mit Identitätsprüfungen einher, die Reise-eSIMs ganz überspringen, weshalb die Nummer, unter der man dich erreicht, deine eigene bleibt. Lass die physische SIM für Anrufe und Verifizierungscodes aktiv und lass die eSIM die Daten tragen."),
    ("Was sagen Reisende über eSIMs in Japan?",
     "Statt einer Sternebewertung beantwortet diese Seite die Bewertungsfrage mit Messungen – die {plan_count} Japan-Tarife von {brand_count} Anbietern, gereiht nach einer $/GB- und $/Tag-Formel. Bewertungsnoten derselben Marke unterscheiden sich je nach Region des Bewerters, eine einzelne Zahl wäre also irreführend. Lies die Zahlen oben für die prüfbare Hälfte und die eigenen Kanäle des Anbieters für die Stimmung."),
]

# 德语问句模板：{CACC}=宾格名 {CDAT}=与格名。**必须是完整问句** ——
# 英语侧 Q2 的完整问句是「Is unlimited eSIM data in X actually unlimited?」，
# 只写前缀会生成半句（早期版本踩过）。
SLOTS = [
    ("Was ist die günstigste eSIM für {CACC}?", Q1, "q1"),
    ("Ist unbegrenztes eSIM-Datenvolumen in {CDAT} wirklich unbegrenzt?", Q2, "q2"),
    ("Airalo oder Holafly für {CACC}?", Q3, "q3"),
    ("Kann ich eine eSIM in {CDAT} nutzen?", Q7, "q7"),
    ("Funktioniert mein Handy mit einer eSIM in {CDAT}?", Q8, "q8"),
    ("Brauche ich eine lokale Nummer in {CDAT}?", Q9, "q9"),
    ("Was sagen Reisende über eSIMs in {CDAT}?", Q10, "q10"),
]

Q4_Q = "Brauche ich einen Identitätsnachweis für eine eSIM in {CDAT}?"
Q5_Q = "Welche Netze nutzen eSIMs in {CDAT}?"
Q6_Q = "Kann eine eSIM {CACC} und {NB} abdecken?"
Q6_Q_REGION = "Kann eine eSIM {CACC} und weitere Länder der Region abdecken?"


def de_countries() -> dict:
    return tomllib.load(io.open(ROOT / "data" / "de" / "countries.toml", "rb"))


def read_en() -> dict[str, dict]:
    out = {}
    for f in sorted(EN_FAQ.glob("*.toml")):
        out[f.stem.upper()] = tomllib.load(io.open(f, "rb"))
    return out


def name_case(iso: str, case: str, de: dict, base: dict) -> str:
    """德语国名：acc / dat 用 name_acc / name_dat，缺失回退裸名。"""
    d = de.get(iso, {})
    n = d.get("name") or base[iso]["name"]
    if case == "acc":
        return d.get("name_acc") or n
    if case == "dat":
        return d.get("name_dat") or n
    return n


def en_name(iso: str, base: dict) -> str:
    return base[iso]["name"]


def main() -> int:
    de = de_countries()
    base = tomllib.load(io.open(ROOT / "data" / "countries.toml", "rb"))
    en = read_en()

    isos = sorted(i for i in base if isinstance(base[i], dict) and base[i].get("name"))
    en_isos = [i for i in isos if i in en]
    if sorted(en_isos) != sorted(en):
        print(f"WARN 英语侧与 countries 集合不一致: {set(en) ^ set(en_isos)}")

    order = [i for i in en_isos if i != "JP"]
    assign: dict[str, dict] = {}
    for idx, iso in enumerate(order):
        a, b = idx % POOL, idx // POOL
        assign[iso] = {"q1": (a, b, (a + b) % POOL), "q3": (a, b, (a + b) % POOL),
                       "q2": (a, b, (a + b) % POOL), "q7": (a, b, (a + b) % POOL),
                       "q8": (a, b, (a + b) % POOL), "q9": (a, b, (a + b) % POOL),
                       "q10": (a, b, (a + b) % POOL), "q6": idx % POOL}
    no_nb = [i for i in order if not base[i].get("neighbors")]
    for rank, iso in enumerate(no_nb):
        assign[iso]["q6"] = rank

    errs: list[str] = []
    files: dict[str, list[tuple[str, str]]] = {}

    for iso in en_isos:
        n = len(en[iso].get("faq", []))
        if n != 10:
            errs.append(f"{iso}: 英语侧 {n} 条问答 != 10，德语版结构无法对齐")
            continue
        name_acc = name_case(iso, "acc", de, base)
        name_dat = name_case(iso, "dat", de, base)

        if iso == "JP":
            files[iso] = JP_PAIRS
            continue

        plan = assign[iso]
        out: list[tuple[str, str]] = []
        # slot0-2
        for qtpl, pools, key in SLOTS[:3]:
            out.append((fill_q(qtpl, name_acc, name_dat), answer(pools, plan[key])))
        # slot3 ID
        q3 = Q4_EXC.get(iso)
        if q3 is None:
            out.append((fill_q(Q4_Q, name_acc, name_dat), Q4_TPL))
        else:
            out.append((fill_q(Q4_Q, name_acc, name_dat), q3))
        # slot4 networks —— 运营商清单从英语侧转录
        carriers = extract_carriers(en[iso]["faq"][4]["a"])
        if carriers is None:
            errs.append(f"{iso}: 英语侧 Q5 不匹配标准句式，无法转录运营商清单")
            continue
        out.append((fill_q(Q5_Q, name_acc, name_dat), Q5_TPL.format(carriers=carriers)))
        # slot5 Q6 —— 邻国从英语侧问题里转录（空串 = 英语侧是 region 兜底）
        nb = extract_neighbor(en[iso]["faq"][5]["q"], base)
        if nb is None:
            errs.append(f"{iso}: 英语侧 Q6 问题里找不到邻国: {en[iso]['faq'][5]['q'][:70]!r}")
            continue
        if nb == "":
            q6q = fill_q(Q6_Q_REGION, name_acc, name_dat)
        else:
            q6q = fill_q(Q6_Q, name_acc, name_dat, NB=name_case(nb, 'acc', de, base))
        out.append((q6q, Q6[plan["q6"]]))
        # slot6-9
        for qtpl, pools, key in SLOTS[3:]:
            out.append((fill_q(qtpl, name_acc, name_dat), answer(pools, plan[key])))
        files[iso] = out

    # ── 校验 ──
    for iso, pairs in files.items():
        if len(pairs) != 10:
            errs.append(f"{iso}: 生成 {len(pairs)} 条 != 10")
        for q, a in pairs:
            for m in re.findall(r"\$\d", a):
                errs.append(f"{iso}: 答案里写死了价格 {m!r}")
            bad = [t for t in re.findall(r"\{[a-z_]+\}", a + q)
                   if t not in KNOWN_TOKENS]
            if bad:
                errs.append(f"{iso}: 用了未注册 token {bad}")

    print(f"生成 {len(files)} 国（英语侧 {len(en)} 国）")
    lens = [len(a) for pairs in files.values() for _, a in pairs]
    print(f"答案长度: min={min(lens)} med={sorted(lens)[len(lens)//2]} max={max(lens)}")
    print(f"校验错误: {len(errs)}")
    for e in errs[:20]:
        print("  " + e)

    if errs:
        print("\nERROR 不写盘")
        return 1
    if "--write" in sys.argv:
        DE_FAQ.mkdir(parents=True, exist_ok=True)
        for iso, pairs in files.items():
            buf = [f"# {iso} FAQ (Deutsch) – erzeugt von scripts/faq_frames_de.py, nicht von Hand ändern.",
                   "# Zahlen und Markennamen laufen über {token}; Werte berechnet "
                   "layouts/partials/faq-live-tokens.html zur Build-Zeit.", ""]
            for q, a in pairs:
                buf.append("[[faq]]")
                buf.append(f"q = {json.dumps(q, ensure_ascii=False)}")
                buf.append(f"a = {json.dumps(a, ensure_ascii=False)}")
                buf.append("")
            io.open(DE_FAQ / f"{iso.lower()}.toml", "wb").write(
                ("\n".join(buf).rstrip("\n") + "\n").encode("utf-8"))
        print(f"\nWROTE {len(files)} Dateien nach {DE_FAQ.relative_to(ROOT).as_posix()}/")
    return 0


# ── helpers ──────────────────────────────────────────────────────────────────
KNOWN_TOKENS = {
    "{country}", "{country_acc}", "{country_dat}", "{neighbor}", "{neighbors_all}",
    "{plan_count}", "{brand_count}", "{brands_list}",
    "{cheap_brand}", "{cheap_plan}", "{cheap_price}", "{cheap_perday}", "{cheap_pergb}",
    "{runner_brand}", "{runner_price}", "{value_brand}", "{value_plan}", "{value_pergb}",
    "{unl_count}", "{unl_brand}", "{unl_days}", "{unl_price}", "{unl_perday}",
    "{unl_allowance}", "{unl_drop}", "{unl_perday_range}",
    "{ah_airalo_pergb}", "{ah_airalo_plan}", "{ah_airalo_price}",
    "{ah_holafly_days}", "{ah_holafly_price}", "{ah_holafly_perday}",
}



def fill_q(tpl: str, acc: str, dat: str, NB: str = "") -> str:
    """把问句模板里的 {CACC} / {CDAT} / {NB} 填成德语国名（问句用**字面国名**，
    与英语侧一致 —— 英语侧的问句也是写死的英文国名，不走运行时 token）。"""
    return tpl.replace("{CACC}", acc).replace("{CDAT}", dat).replace("{NB}", NB)


def answer(pools: dict, idx: tuple[int, int, int]) -> str:
    a, b, c = idx
    return " ".join([pools["open"][a], pools["body"][b], pools["close"][c]])


def extract_carriers(en_a: str) -> str | None:
    m = re.match(r"^Plans on this page run on (.+?)\. Differences matter", en_a)
    return m.group(1) if m else None


def extract_neighbor(en_q: str, base: dict) -> str | None:
    """从英语侧 Q6 问题里取出邻国 ISO。

    英语侧 Q6 有两种形态：
      · 「… and <邻国>?」/「… and <邻国> on the same trip?」   → 有具体邻国
      · 「… and the rest of <Region>?」                       → 7 个无邻国国家的兜底
    邻国名可能是短名（`the USA` / `the UK`）—— 只这两个别名，其余与 countries.name 一致。
    """
    m = re.match(r"^Can one eSIM cover (.+?) and (.+?)(?: on the same trip)?\?$", en_q)
    if not m:
        return None
    nb = m.group(2)
    if nb.startswith("the rest of "):
        return ""                      # 空串 = region 兜底（调用方走通用德语问句）
    if nb in ALIAS:
        return ALIAS[nb]
    for iso, v in base.items():
        if isinstance(v, dict) and v.get("name") == nb:
            return iso
    return None


ALIAS = {"the USA": "US", "the UK": "GB", "USA": "US", "UK": "GB"}


if __name__ == "__main__":
    sys.exit(main())
