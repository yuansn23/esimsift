# -*- coding: utf-8 -*-
"""生成 data/de/strings.toml —— 数据层英文串的德语映射。

三类来源（键必须与数据里的英文**逐字节相同**，脚本读数据全集逐条核对）：
  1. data/plans/*.toml 的 fup_note
  2. data/providers.toml[<brand>].promo_label
  3. data/countries.toml[<ISO>].quirks（国家须知短句，**按 ISO 分组 + 组内同序**配对，
     并用「数字集合」做错配断言 —— 不必手抄英文长句）
缺一条 / 数据改了措辞 / 表里有死条目 → assert 失败，闸门当场变红。
"""
import glob
import re
import tomllib
from collections import Counter
from pathlib import Path

ROOT = Path(r"D:\esimsift\esimsift")

FUP = {
    "3 GB per day at full speed, then ∞ at 1Mbps": "3 GB pro Tag mit voller Geschwindigkeit, danach ∞ mit 1 Mbit/s",
    "5 GB per day at full speed, then ∞ at 1Mbps": "5 GB pro Tag mit voller Geschwindigkeit, danach ∞ mit 1 Mbit/s",
    "2 GB per day at full speed, then ∞ at 1Mbps": "2 GB pro Tag mit voller Geschwindigkeit, danach ∞ mit 1 Mbit/s",
    "3 GB per day at full speed, then ∞ at 1kbps": "3 GB pro Tag mit voller Geschwindigkeit, danach ∞ mit 1 kbit/s",
    "5 GB per day at full speed, then ∞ at 1kbps": "5 GB pro Tag mit voller Geschwindigkeit, danach ∞ mit 1 kbit/s",
    "3 GB per day at full speed, then ∞ at 384kbps": "3 GB pro Tag mit voller Geschwindigkeit, danach ∞ mit 384 kbit/s",
    "5 GB per day at full speed, then ∞ at 2Mbps": "5 GB pro Tag mit voller Geschwindigkeit, danach ∞ mit 2 Mbit/s",
    "60 GB per month at full speed, then ∞ at 2Mbps (auto-renewing monthly subscription)": "60 GB pro Monat mit voller Geschwindigkeit, danach ∞ mit 2 Mbit/s (automatisch verlängertes Monatsabo)",
    "Always On backup plan: 1GB of data monthly to keep you connected no matter what.": "Always-On-Backup-Tarif: 1 GB Datenvolumen pro Monat, damit du immer verbunden bleibst.",
    "20 GB per month (auto-renewing subscription)": "20 GB pro Monat (automatisch verlängertes Abo)",
    "5 GB per month (auto-renewing subscription)": "5 GB pro Monat (automatisch verlängertes Abo)",
    "5 GB per month for 12 months (annual subscription)": "5 GB pro Monat für 12 Monate (Jahresabo)",
    "2 GB per month for 12 months (annual subscription)": "2 GB pro Monat für 12 Monate (Jahresabo)",
    "20 GB per month for 12 months (annual subscription)": "20 GB pro Monat für 12 Monate (Jahresabo)",
}
PROMO = {
    "20% off your entire order": "20 % Rabatt auf die gesamte Bestellung",
    "15% off your first order (new customers)": "15 % Rabatt auf die erste Bestellung (Neukunden)",
    "5% off all destination eSIMs": "5 % Rabatt auf alle Länder-eSIMs",
    "25% off Saily eSIMs": "25 % Rabatt auf Saily-eSIMs",
    "20% off Yesim eSIM plans": "20 % Rabatt auf Yesim-eSIM-Tarife",
    "15% off unlimited-data plans": "15 % Rabatt auf Unlimited-Tarife",
    "10% off all plans": "10 % Rabatt auf alle Tarife",
    "15% off every plan": "15 % Rabatt auf jeden Tarif",
    "20% off selected plans (autumn campaign)": "20 % Rabatt auf ausgewählte Tarife (Herbstaktion)",
    "15% off eSIM plans": "15 % Rabatt auf eSIM-Tarife",
}

# 品牌档案信息类字段（第六十三轮新增）：
#   info.support —— 客服渠道（10 品牌，其中两条英文完全相同 ⇒ 合成一个键）
#   info.refund  —— 退款政策（10 品牌，每条不同；长句，数字必须原样保留）
# 与 FUP/PROMO 同一套「英文原文 = 键」约定；数字由 main() 断言不得凭空增加。
# 为什么必须做：这两个字段在 /esim-providers/<brand>/ 的 #support 区块与 FAQ 答案里
# 直接渲染，德语页曾整段印英文（探针页 /de/esim-providers/airalo/ 实测 F 段报 2 处）。
INFO = {
    # ── support ──────────────────────────────────────────────────────────
    "24/7 live chat (website and in-app) and email":
        "24/7 Live-Chat (Website und App) und E-Mail",
    "24/7 human support (online assistance 365 days) and email":
        "24/7 persönliche Beratung (Online-Hilfe an 365 Tagen) und E-Mail",
    "24/7 live chat in multiple languages, WhatsApp (+1 661 384 8482) and email":
        "24/7 Live-Chat in mehreren Sprachen, WhatsApp (+1 661 384 8482) und E-Mail",
    "24/7 live chat in the Saily app, web support tickets and email (no phone support)":
        "24/7 Live-Chat in der Saily-App, Web-Support-Tickets und E-Mail (kein Telefonsupport)",
    "24/7 live chat in the Yesim app, contact form and email":
        "24/7 Live-Chat in der Yesim-App, Kontaktformular und E-Mail",
    "Chat (24/7 virtual assistant) and a web contact form; no published support email or phone":
        "Chat (24/7 virtueller Assistent) und ein Web-Kontaktformular; "
        "keine veröffentlichte Support-E-Mail oder Telefonnummer",
    "24/7 live chat and email; phone +34 91 791 94 91":
        "24/7 Live-Chat und E-Mail; Telefon +34 91 791 94 91",
    "Live chat (website and in-app) and email, available 24 hours a day, 365 days a year; phone +1 877-278-3625":
        "Live-Chat (Website und App) und E-Mail, rund um die Uhr an 365 Tagen im Jahr; "
        "Telefon +1 877-278-3625",
    "24/7 live chat, WhatsApp and email":
        "24/7 Live-Chat, WhatsApp und E-Mail",
    # ── refund ───────────────────────────────────────────────────────────
    "Roami's worry-free refund policy promises a full refund if the plan doesn't work or remains unused. The same 24/7 team handles activation, refunds and travel questions.":
        "Roamis sorgenfreie Rückgaberichtlinie verspricht eine vollständige Rückerstattung, "
        "wenn der Tarif nicht funktioniert oder ungenutzt bleibt. Dasselbe 24/7-Team kümmert "
        "sich um Aktivierung, Rückerstattungen und Reisefragen.",
    "Airalo lets you withdraw within 14 days of purchase, but the right expires once the eSIM is activated or used. If an activated eSIM fails because of an Airalo error and cannot be restored, you can claim a replacement or refund within 30 days of the issue. Refunds arrive as Airmoney credit or to the original payment method (up to 30 business days).":
        "Airalo erlaubt den Widerruf innerhalb von 14 Tagen nach dem Kauf, doch das Recht "
        "erlischt, sobald die eSIM aktiviert oder genutzt wurde. Lässt sich eine aktivierte "
        "eSIM wegen eines Fehlers von Airalo nicht wiederherstellen, kannst du innerhalb von "
        "30 Tagen nach dem Problem Ersatz oder Rückerstattung verlangen. Rückerstattungen "
        "kommen als Airmoney-Guthaben oder auf die ursprüngliche Zahlungsmethode "
        "(bis zu 30 Werktage).",
    "Holafly gives you up to 6 months from purchase to request a refund. A full change-of-mind refund requires buying direct from Holafly (not a reseller) and never activating the eSIM; device-incompatibility refunds need an unscanned QR code and a screenshot as proof. Connection issues during a trip qualify for full or partial refunds (partial ones may carry a $3.50 administrative fee), paid back to the original payment method within 5-10 business days.":
        "Holafly gewährt bis zu 6 Monate nach dem Kauf Zeit für einen Rückerstattungsantrag. "
        "Eine vollständige Rückerstattung wegen Meinungsänderung setzt voraus, dass du direkt "
        "bei Holafly (nicht bei einem Wiederverkäufer) gekauft und die eSIM nie aktiviert hast; "
        "bei Geräte-Inkompatibilität brauchst du einen ungescannten QR-Code und einen "
        "Screenshot als Nachweis. Verbindungsprobleme während der Reise berechtigen zu "
        "vollständigen oder teilweisen Rückerstattungen (teilweise mit $3.50 "
        "Bearbeitungsgebühr), ausgezahlt auf die ursprüngliche Zahlungsmethode innerhalb von "
        "5-10 Werktagen.",
    "Refunds can be requested within 30 days of activation and while the data package is still valid. Unused packages are refunded in full and barely-used ones (under about 1% of data consumed) partially, all via Saily's self-service refund center; if you can't install the eSIM within 30 days you can also get a refund.":
        "Rückerstattungen lassen sich innerhalb von 30 Tagen nach der Aktivierung beantragen, "
        "solange das Datenpaket noch gültig ist. Ungenutzte Pakete werden vollständig "
        "erstattet, kaum genutzte (unter etwa 1 % verbrauchtem Datenvolumen) teilweise — "
        "alles über Sailys Selbstbedienungs-Erstattungscenter; kannst du die eSIM nicht "
        "innerhalb von 30 Tagen installieren, ist ebenfalls eine Rückerstattung möglich.",
    "Yesim refunds only completely unused and unactivated services, requested within 30 days of purchase. Technical-issue refunds must be reported within 1 hour of the failure and can take up to 15 business days to review. Amounts of €10 or less may be paid in Ycoins loyalty credit instead of cash.":
        "Yesim erstattet nur vollständig ungenutzte und nicht aktivierte Dienste, beantragt "
        "innerhalb von 30 Tagen nach dem Kauf. Rückerstattungen wegen technischer Probleme "
        "müssen innerhalb von 1 Stunde nach dem Fehler gemeldet werden und können bis zu "
        "15 Werktage zur Prüfung dauern. Beträge von €10 oder weniger können statt in bar als "
        "Ycoins-Treueguthaben ausgezahlt werden.",
    "Ubigi data plans are non-refundable once use has started — even partially used. Any refund must be requested within 15 days of payment and only applies to completely unused plans. Monthly plans carry a 3-month minimum commitment before cancellation.":
        "Ubigi-Datentarife sind nicht erstattungsfähig, sobald die Nutzung begonnen hat — "
        "auch bei teilweiser Nutzung. Eine Rückerstattung muss innerhalb von 15 Tagen nach der "
        "Zahlung beantragt werden und gilt nur für vollständig ungenutzte Tarife. Monatstarife "
        "haben eine Mindestlaufzeit von 3 Monaten vor der Kündigung.",
    "Roamic's homepage promises a no-questions-asked refund if your eSIM goes unused within 6 months. The formal policy notes eSIMs are digital products that can't be returned once purchased, and sends buyers with problems to the support team (chat or email), who handle refunds without hassle when a plan must be changed.":
        "Roamics Startseite verspricht eine Rückerstattung ohne Rückfragen, wenn deine eSIM "
        "innerhalb von 6 Monaten ungenutzt bleibt. Die formale Richtlinie weist darauf hin, "
        "dass eSIMs digitale Produkte sind, die nach dem Kauf nicht zurückgegeben werden "
        "können, und verweist Betroffene an das Support-Team (Chat oder E-Mail), das "
        "Rückerstattungen unkompliziert abwickelt, wenn ein Tarif gewechselt werden muss.",
    "aloSIM offers a 30-day money-back guarantee: a full refund if you can't install the eSIM or hit connectivity issues, including discovering your device isn't eSIM-compatible. You need your original receipt, and the team may ask why you're requesting the refund.":
        "aloSIM bietet eine 30-Tage-Geld-zurück-Garantie: vollständige Rückerstattung, wenn du "
        "die eSIM nicht installieren kannst oder Verbindungsprobleme auftreten — auch wenn "
        "sich zeigt, dass dein Gerät nicht eSIM-fähig ist. Du brauchst deinen ursprünglichen "
        "Beleg, und das Team fragt möglicherweise nach dem Grund.",
    "Nomad lets you ask for a refund or a change before the eSIM is installed or activated; after activation it refunds only when the fault is a technical problem originating from Nomad. Whether a given plan qualifies is stated in that plan's own description, so check it before buying. Complaints go through the Help Center in the app or website, or by email to hello-cs@getnomad.app.":
        "Bei Nomad kannst du vor der Installation oder Aktivierung der eSIM eine "
        "Rückerstattung oder Änderung verlangen; nach der Aktivierung wird nur erstattet, wenn "
        "der Fehler ein technisches Problem von Nomad ist. Ob ein Tarif dafür in Frage kommt, "
        "steht in der Beschreibung des jeweiligen Tarifs — prüfe das vor dem Kauf. Beschwerden "
        "laufen über das Help Center in der App oder auf der Website oder per E-Mail an "
        "hello-cs@getnomad.app.",
    "Jetpac's Terms & Conditions treat an installed eSIM as used: once it is installed, no refund is offered. The exception is a technical fault that stops the eSIM installing or working - then you can ask for a refund or a replacement, and the request must be made within 30 days of purchase. Unused data left when a plan's validity period ends is not refunded or compensated.":
        "Jetpacs Allgemeine Geschäftsbedingungen behandeln eine installierte eSIM als genutzt: "
        "Nach der Installation gibt es keine Rückerstattung. Ausnahme ist ein technischer "
        "Defekt, der die Installation oder Funktion der eSIM verhindert — dann kannst du "
        "Rückerstattung oder Ersatz verlangen, und der Antrag muss innerhalb von 30 Tagen nach "
        "dem Kauf gestellt werden. Ungenutztes Datenvolumen am Ende der Gültigkeit wird nicht "
        "erstattet oder ausgeglichen.",
}

# 国家须知（#quirks 区块正文）：按 ISO 分组，组内顺序与 data/countries.toml 的 quirks 数组一致。
# 品牌名 / 运营商名 / 城市名 / 数字保留（数字有断言兜底）；口语口径与全站 de 文案一致（du-Form）。
QUIRKS_DE = {
    "JP": [
        "Das japanische Recht verlangt eine Passprüfung für lokale Prepaid-SIMs (SoftBank, Docomo, KDDI) — Reise-eSIMs umgehen das komplett.",
        "SoftBanks eigene Touristen-SIM lässt sich nur zwischen 09:00 und 21:00 JST aktivieren; Reise-eSIMs sind 24/7 aktiv — wichtig bei Nachtankunft in Narita oder Haneda.",
        "Pocket-WiFi-Verleih ist Japans Klassiker unter den Konnektivitätsoptionen. Für Gruppen ab 3 Personen gewinnt er, Alleinreisende zahlen mit einer eSIM fast immer weniger.",
    ],
    "US": [
        "Verizon ist beim Reise-eSIM-Support spät eingestiegen — die meisten Tarife laufen weiter über T-Mobile oder AT&T: stark in Städten, dünner in Nationalparks.",
        "US-amerikanische „Unlimited\u201c-Reisetarife drosseln in der Regel nach 2–5 GB pro Tag; das Kleingedruckte zur Fair-Use-Policy zählt hier mehr als irgendwo sonst.",
    ],
    "GB": [
        "EE gewinnt britische Tests zur ländlichen Abdeckung konstant; Three ist am günstigsten, wird in den Highlands aber dünn.",
        "Die „Unlimited\u201c-Touristentarife von Three drosseln Video auf 1080p — am Handy in Ordnung, nervig, wenn du einen Laptop per Hotspot versorgst.",
    ],
    "FR": [
        "Free ist berühmt günstig, aber in der Provence ungleichmäßig; Orange bleibt der Abdeckungskönig auf dem Land.",
        "Die Orange-Holiday-Pakete sind am CDG stark im Preis — kaufe die eSIM vorher online, dann sparst du dir die Warteschlange am Schalter.",
    ],
    "IT": [
        "TIM gehört der ländliche Raum Italiens weiterhin; günstige eSIMs auf WindTre-Basis tun sich in den Hügelstädten Umbriens schwer.",
        "Italienisches Recht begrenzt die Gültigkeit von Touristen-SIMs auf 90 Tage — für Reise-eSIMs irrelevant, sie laufen ohnehin mit dem Tarif ab.",
    ],
    "TH": [
        "Die SIM-Schalter am Suvarnabhumi sind 24/7 besetzt und fahren aggressive Touristenpreise — der seltene Fall, in dem physische SIMs vor Ort konkurrenzfähig sind.",
        "True und DTAC haben ihre Netze fusioniert; die meisten eSIMs landen im kombinierten Netz, wodurch das Marketing mit der „Netzwahl\u201c weitgehend gegenstandslos wird.",
    ],
    "KR": [
        "Koreanische Anbieter-Apps verlangen oft eine lokale ARS-Verifizierung — Reise-eSIMs umgehen das mit vorregistrierten Profilen.",
        "KT und SK deckeln ihre Touristentarife trotz 5G-Ausbau weiter bei LTE; prüfe, ob dein Tarif 5G ausweist, bevor du mehr zahlst.",
    ],
    "SG": [
        "Touristen-SIMs sind stark im Preis, am Changi aber nur physisch an den Schaltern erhältlich; bei Ankünften um 1 Uhr nachts gewinnen eSIMs bei der Bequemlichkeit.",
        "Alle drei Netze in Singapur sind hervorragend — die günstigste eSIM kostet dich hier selten Abdeckung.",
    ],
    "ES": [
        "Movistar deckt die Küsten und Inseln am besten ab; günstige Tarife auf Yoigo-Basis roamen ohnehin dort hinein.",
        "Das spanische Recht verlangt einen Ausweis für lokale SIMs; Reise-eSIMs überspringen den Pass-Scan komplett.",
    ],
    "DE": [
        "Das Telekom-Netz ist der Abdeckungsmaßstab; eSIMs auf O2-Basis sparen Geld, verblassen aber außerhalb der Städte.",
        "Das deutsche Prepaid-Recht verlangt einen Ausweis für lokale SIMs — Reise-eSIMs umgehen die Ausweisprüfung.",
    ],
    "AU": [
        "Telstra ist die Lebenslinie im Outback — Optus erreicht 98,5 % der Bevölkerung, aber nur einen Bruchteil der Fläche; abseits der Küste zählt eine eSIM auf Telstra-Basis.",
        "Australische „Unlimited\u201c-Touristen-eSIMs haben immer eine tägliche Geschwindigkeitsgrenze nach 2–3 GB.",
    ],
    "TW": [
        "Taiwans Touristen-SIMs sind günstig, aber nur am Flughafenschalter erhältlich; die Online-Preise für eSIMs liegen nah genug, dass das Überspringen der Warteschlange meist gewinnt.",
        "FarEasTone-Touristenkarten drosseln nach einem Tageslimit; Airalo-Tarife laufen mit voller Geschwindigkeit, bis das Datenvolumen leer ist.",
    ],
    "HK": [
        "Hongkong ist einer der wenigen Märkte, in denen lokale Prepaid-SIMs eSIMs beim Preis wirklich schlagen — sie müssen aber in Convenience-Stores abgeholt werden.",
        "CSL betreibt die dichteste Metro-Abdeckung; die meisten Reise-eSIMs fahren im selben Netz, günstige Tarife kosten dich also selten Signal.",
    ],
    "MO": [
        "Macau presst drei Netze in eine winzige Fläche — die Abdeckungsunterschiede sind vernachlässigbar; kaufe nach Preis.",
        "Viele Hongkong-eSIMs enthalten Macau ohne Aufpreis; prüfe regionale Tarife, bevor du einen Ein-Land-Tarif kaufst.",
    ],
    "MY": [
        "Malaysische Touristen-SIMs brauchen eine Passregistrierung am Schalter; eSIMs sparen sich den Papierkram komplett.",
        "DiGis ländliche Abdeckung hinkt Maxis und Celcom hinterher — steht Borneo auf dem Programm, prüfe, welches Netz deine eSIM nutzt.",
    ],
    "VN": [
        "Vietnam verlangt eine Passregistrierung für jede SIM, auch für eSIMs — rechne beim Kauf mit einem kurzen ID-Upload.",
        "Viettel ist das einzige Netz, das die Halong-Bucht und die Bergrouten im Norden zuverlässig abdeckt; die meisten Reise-eSIMs nutzen es standardmäßig.",
    ],
    "ID": [
        "Indonesiens Inseln machen die Netzwahl entscheidend — Telkomsel dominiert außerhalb von Java und Bali; günstige Indosat-Tarife verlieren auf Lombok das Signal.",
        "Das indonesische Recht verlangt einen Pass-Upload für die eSIM-Registrierung; die Anbieter erledigen das in der App.",
    ],
    "PH": [
        "Die Abdeckung von Smart und Globe außerhalb von Luzon ist lückenhaft und komplementär — ein Dual-eSIM-Handy mit je einer davon ist der starke Zug für Inselhüpfer.",
        "Die philippinische SIM-Registrierung verlangt per Gesetz ein ID-Selfie; eSIM-Käufe enthalten denselben Schritt.",
    ],
    "IN": [
        "Indische Regeln verlangen selbst für Reise-eSIMs eine passgebundene Registrierung — Airalo und Saily erledigen das in der App in etwa zwei Minuten.",
        "Jios Abdeckung überragt Airtel außerhalb der Städte; die meisten Reise-eSIMs fahren auf Airtel — gut für das Goldene Dreieck, schwächer in Ladakh.",
    ],
    "CN": [
        "Reise-eSIMs für China laufen über Gateways in Hongkong — sie brauchen kein VPN für Google und WhatsApp, anders als lokale SIMs.",
        "China Unicom akzeptiert ausländische eSIMs am zuverlässigsten; Telecom verlangt gelegentlich manuelle APN-Eingabe.",
    ],
    "PT": [
        "Das Festland von Portugal ist für alle Netze einfach; die Azoren und Madeira bevorzugen Tarife auf MEO-Basis.",
        "Lissabon und Porto haben 5G in jedem Netz; die Preislücke dazwischen bringt dir in Städten nichts.",
    ],
    "NL": [
        "Das Land ist klein und flach — alle drei Netze sind praktisch gleich; kaufe nach Preis.",
        "Niederländische Verbraucherregeln begrenzen die Drosselung von „Unlimited\u201c — einer der wenigen Orte, an denen das Etikett etwas bedeutet.",
    ],
    "BE": [
        "Die Abdeckung ist in allen Netzen ein gelöstes Problem; der Zug Brüssel–Brügge hat WLAN, große Datenpakete bleiben also ungenutzt.",
        "Belgisches lokales Prepaid verlangt einen Ausweis; Reise-eSIMs sparen ihn sich.",
    ],
    "CH": [
        "Die Schweiz ist NICHT im EU-Roaming — EU-eSIMs zahlen hier Aufschläge; ein Schweiz-spezifischer Tarif rechnet sich innerhalb von Stunden.",
        "Schweizer Daten sind die teuersten Europas; die Alpenabdeckung von Swisscom ist unerreicht — und genauso bepreist.",
    ],
    "AT": [
        "Die Alpenabdeckung gehört A1; eSIMs auf Magenta-Basis verlieren in den Tiroler Tälern.",
        "Österreichisches lokales Prepaid verlangt eine Registrierung; Reise-eSIMs kommen vorregistriert an.",
    ],
    "GR": [
        "Cosmote gehört die Inselwelt; günstige eSIMs auf Vodafone-Basis verlieren beim Inselhüpfen zwischen den Kykladen das Signal.",
        "Juli und August belasten die Inselfunkmasten — keine Tarifwahl behebt die Stoßzeit-Überlastung.",
    ],
    "TR": [
        "Die Türkei blockiert einige VPN-Protokolle standardmäßig — Reise-eSIMs routen international und umgehen die Sperre.",
        "Die Touristenpakete von Turkcell sind ordentlich im Preis, aber nur am Flughafen erhältlich; online konkurrieren eSIM-Preise eng.",
    ],
    "IE": [
        "Three Ireland deckt die Westküste am besten ab; Vodafone gewinnt das Mittelland.",
        "Das ländliche Signal folgt der M8 — auf dem Ring of Kerry zählen Offline-Karten mehr als die Netzwahl.",
    ],
    "PL": [
        "Play hat sich vom Billiganbieter zum Abdeckungsführer entwickelt; in Städten sind alle vier Netze in Ordnung.",
        "Die Busse von Krakau nach Zakopane durchqueren Funklöcher von Play — Netzwechsel wie bei Telkomsel greifen hier nicht; lade einfach Offline-Karten herunter.",
    ],
    "CZ": [
        "Prag ist bei der Abdeckung trivial; das burgenreiche ländliche Böhmen bevorzugt T-Mobile.",
        "Tschechisches lokales Prepaid verlangt eine Registrierung; Reise-eSIMs sparen sich den Papierkram.",
    ],
    "HR": [
        "Die Inseln sind Hrvatski-Telekom-Territorium; Tarife auf A1-Basis verblassen südlich von Split.",
        "Fährrouten wechseln mitten in der Meerenge den Funkmast — rechne in jedem Netz mit einer Datenpause von 30 Sekunden zwischen den Inseln.",
    ],
    "IS": [
        "Die Ringstraße wird von allen Netzen abgedeckt; die Hochland-F-Straßen haben gar nichts — Offline-Karten unabhängig von der SIM.",
        "Isländische Daten sind überall teuer; es gibt keinen Billigtrick, nur Optimierung pro GB.",
    ],
    "GE": [
        "Die Bergregionen gehören Magti; Dual-SIM-Handys kombinieren eine physische Magti-SIM mit einer Reise-eSIM für das Beste aus beiden Welten.",
        "Für georgische eSIMs ist keine Registrierung nötig — einer der einfachsten Käufe Europas.",
    ],
    "CA": [
        "Die Big Three teilen sich die Netze — eine „Rabatt\u201c-eSIM von Telus läuft oft auf denselben Masten wie Bell.",
        "Kanadische Daten gehören zu den teuersten der Welt; Tagespässe der Anbieter sind fast immer schlechter als eine Reise-eSIM.",
    ],
    "MX": [
        "Telcel ist das einzige Netz, das Chiapas und Oaxaca richtig abdeckt; eSIMs auf AT&T-Basis sind stark in Städten, dünn auf dem Land.",
        "Das mexikanische Recht verlangt eine CURP-/ID-Registrierung für lokale SIMs; Reise-eSIMs sparen den Gang zum Schalter.",
    ],
    "BR": [
        "Vivo führt bei der nationalen Abdeckung; günstige eSIMs auf TIM-Basis tun sich in Amazonas schwer.",
        "Brasilianisches lokales Prepaid verlangt eine CPF — Ausländer haben selten eine; Reise-eSIMs umgehen das Problem komplett.",
    ],
    "AR": [
        "Buenos Aires ist in jedem Netz in Ordnung; Patagonien gehört Personal.",
        "Die lokale SIM-Registrierung verlangt für Einwohner eine DNI; Touristen brauchen einen Pass-Durchlauf — eSIMs sparen sich das alles.",
    ],
    "CO": [
        "Claro gehört das ländliche Kolumbien; die Straßen der Kaffeeregion verlieren Movistar-Signal schnell.",
        "Flüge von Bogotá nach Cartagena machen große Datenpakete sinnlos — das WLAN im Hotel trägt die Hauptlast.",
    ],
    "PE": [
        "Entel deckt Cusco und Machu Picchu am besten ab; Claro gewinnt Lima.",
        "Andenpässe verlieren jedes Netz — auf der Salkantay-Route zählen Offline-Karten mehr als die Tarifwahl.",
    ],
    "CR": [
        "Das staatliche Kolbi deckt den Dschungel ab; Touristen-eSIMs auf Claro-Basis verlieren auf der Osa-Halbinsel das Signal.",
        "Die Touristen-SIM-Schalter am SJO schließen um 22:00 — eSIMs aktivieren bei der Landung, egal wann.",
    ],
    "AE": [
        "Beide Netze der VAE sind hervorragend — und beide drosseln VoIP-Apps; Reise-eSIMs, die international routen, stellen WhatsApp-Anrufe wieder her.",
        "Touristen-SIMs der VAE verlangen einen Pass-Scan beim Kauf; eSIMs behalten ihn in der App.",
    ],
    "SA": [
        "STC führt bei der Abdeckung auf dem Korridor Riad–Dschidda und bei den Projekten am Roten Meer; Tarife auf Zain-Basis hinken in AlUla hinterher.",
        "Saudi-arabische Touristen-eSIMs brauchen Passdaten; die Anbieter prüfen in der App innerhalb von Minuten.",
    ],
    "QA": [
        "Zwei Netze, nahezu identische Abdeckung in Doha — kaufe nach Preis.",
        "Die Funkmasten im Stadionviertel überlasten an Veranstaltungsabenden; keine Tarifwahl behebt das.",
    ],
    "IL": [
        "Das israelische Recht verlangt einen Ausweis für alle SIMs; Reise-eSIMs für Israel sind überraschend knapp — prüfe die Abdeckungslisten, bevor du annimmst, dass dein Anbieter eine verkauft.",
        "Die Gassen der Altstadt von Jerusalem bevorzugen Cellcom; die Industriezonen von Petach Tikwa sind überall in Ordnung.",
    ],
    "EG": [
        "Vodafone deckt das Niltal und die Küste am Roten Meer ab; Routen im Landesinneren des Sinai brauchen Etisalat.",
        "Die ägyptische SIM-Registrierung verlangt Passfotos in offiziellen Geschäften — eSIMs kürzen die Bürokratie.",
    ],
    "MA": [
        "Maroc Telecom deckt die Atlas-Routen und den Rand der Sahara ab; Tarife auf Inwi-Basis enden in Marrakesch.",
        "Die Gassen der Medina von Fès töten das Signal in jedem Netz — zuerst Offline-Karten, dann Daten.",
    ],
    "ZA": [
        "Vodacom und MTN teilen das Land; die Städte der Garden Route bevorzugen Vodacom.",
        "Load-Shedding trifft die Funkmasten — keine SIM-Wahl behebt einen Stromausfall, aber Offline-Karten mildern ihn.",
    ],
    "KE": [
        "Safaricom deckt die Maasai Mara ab; eSIMs auf Airtel-Basis verblassen außerhalb von Nairobi und Mombasa.",
        "Die kenianische SIM-Registrierung verlangt einen Pass persönlich — eSIMs erledigen das digital.",
    ],
    "NZ": [
        "Spark gewinnt die Westküste der Südinsel; günstige Tarife auf 2degrees-Basis verblassen in Fiordland.",
        "Der Milford Sound hat in keinem Netz Abdeckung — lade vor der Fahrt herunter.",
    ],
    "FJ": [
        "Vodafone deckt die Mamanucas ab; Digicel gewinnt die Außeninseln — Fähren zwischen den Inseln wechseln mitten in der Meerenge das Netz.",
        "Das WLAN im Resort ist limitiert und langsam; eine eSIM mit bescheidenem Datenvolumen schlägt die Raten des Hotels.",
    ],
}

HEAD = """# 数据层英文串的德语映射（**语言覆盖层**：英文站没有 data/de/ ⇒ partial 恒等返回原串）
#
# 覆盖四类「数据里内建的英文句子」，它们会原样渲染到德语页上：
#   1. data/plans/*.toml 的 `fup_note` —— 《#fup》表的一列（14 个取值 / 3,159 条套餐）
#   2. data/providers.toml[<brand>].promo_label —— 《#providers》区块的促销句（10 个取值）
#   3. data/providers.toml[<brand>].info.support / .info.refund
#      —— 《#support》区块的「客服渠道」与「退款政策」正文，以及 FAQ 答案（第六十三轮新增）
#   4. data/countries.toml[<ISO>].quirks —— 《#quirks》国家须知（101 条 / 50 国）
#
# ⚠ **`providers.toml[<brand>.policy]` 的文本字段故意不进本表**（第六十四轮查清）：
#   它们由 **`data/de/providers.toml` 深度覆盖**提供德语（10 品牌 × 6 字段 = 60/60 全覆盖），
#   模板读的是合并后的 `$d.providers`，所以德语站拿到的**本来就是德语**。
#   若这里再放一份，就是同一事实的第二份译文 —— 实测两份会立刻漂移
#   （data/de/providers.toml 用 `Sie` + `Mbps` + `unbegrenzte Tarife`，
#    本表若写 `du` + `Mbit/s` + `Unlimited-Tarife`，同一个德语站就出现两种口径）。
#   覆盖完整性改由 `verify_de_text.py` 的**判据 H** 断言（缺键即红），不靠这张表兜。
#   `policy` 的 `hotspot` / `voice` / `fup_kind` 是**枚举**（判据读、i18n 出词），同样不进本表。
#
# ⚠ 键必须与数据里的英文**逐字节相同**（大小写、空格、∞、单位、连字符）。
#   `scripts/verify_de_text.py` 会断言「数据里每一个取值都有德语条目」+「表里没有死条目」，
#   漏一条 / 数据改了措辞 → 闸门当场变红，而不是静默地在德语页上印英文。
#
# ⚠⚠ **顶层就是这些句子键，绝不能再包一层 `[strings]` 表头。**
#   取数处是 `$d.strings`，而 `index hugo.Data "<lang>"` 的 `strings` 键的值
#   **就是本文件的内容**；再包一层 ⇒ `$d.strings` = `{strings: {…}}` ⇒ 查表永远落空
#   ⇒ 德语页静默印英文（2026-10-09 第六十二轮实测：套餐名已本地化、fup/promo 却全英文）。
#   对比：`countries.toml` / `providers.toml` 的顶层键本就是 ISO / 品牌键，所以它们没有这个坑。
#
# 本文件由 `scripts/_gen_de_strings.py` 依据数据全集生成（那份脚本里的德译文是权威来源）。

"""


def toml_escape(s: str) -> str:
    return s.replace("\\", "\\\\").replace('"', '\\"')


def main():
    fup = Counter()
    for f in glob.glob(str(ROOT / "data" / "plans" / "*.toml")):
        for line in open(f, encoding="utf-8"):
            m = re.match(r'\s*fup_note\s*=\s*"(.*)"\s*$', line)
            if m:
                fup[m.group(1)] += 1
    promo = set()
    d = tomllib.loads((ROOT / "data" / "providers.toml").read_text(encoding="utf-8"))
    for k, v in d.items():
        if isinstance(v, dict) and v.get("promo_label"):
            promo.add(v["promo_label"])

    info: set[str] = set()
    for k, v in d.items():
        if isinstance(v, dict) and isinstance(v.get("info"), dict):
            for fld in ("support", "refund"):
                val = v["info"].get(fld)
                if val:
                    info.add(val)

    countries = tomllib.loads((ROOT / "data" / "countries.toml").read_text(encoding="utf-8"))
    en_quirks = {
        iso: v["quirks"]
        for iso, v in countries.items()
        if isinstance(v, dict) and v.get("quirks")
    }

    missing = [k for k in fup if k not in FUP]
    assert not missing, "fup_note 缺德语:\n  " + "\n  ".join(missing)
    missing = [k for k in promo if k not in PROMO]
    assert not missing, "promo_label 缺德语:\n  " + "\n  ".join(missing)
    dead = [k for k in FUP if k not in fup] + [k for k in PROMO if k not in promo]
    assert not dead, "死条目（数据里不存在）:\n  " + "\n  ".join(dead)

    # quirks：按 ISO 分组 + 组内同序配对，靠条数与数字集合兜住错配
    assert set(en_quirks) == set(QUIRKS_DE), (
        "quirks ISO 集合不一致：数据侧多 %s / 德语侧多 %s"
        % (sorted(set(en_quirks) - set(QUIRKS_DE)), sorted(set(QUIRKS_DE) - set(en_quirks)))
    )
    quirks = {}
    for iso, en_list in en_quirks.items():
        de_list = QUIRKS_DE[iso]
        assert len(en_list) == len(de_list), f"quirks 条数不一致 [{iso}]：数据 {len(en_list)} / 德语 {len(de_list)}"
        for en, de in zip(en_list, de_list):
            en_digits = set(re.findall(r"\d+", en))
            de_digits = set(re.findall(r"\d+", de))
            assert de_digits <= en_digits, (
                f"quirks 数字错配 [{iso}]：德语多出 {sorted(de_digits - en_digits)}\n  en={en}\n  de={de}"
            )
            if en_digits != de_digits:
                print(f"  ⚠ 数字未完全对应 [{iso}] 缺 {sorted(en_digits - de_digits)}：{en[:60]}…")
            quirks[en] = de

    missing = [k for k in info if k not in INFO]
    assert not missing, "info 串缺德语:\n  " + "\n  ".join(missing)
    dead = [k for k in INFO if k not in info]
    assert not dead, "死条目（数据里不存在）:\n  " + "\n  ".join(dead)
    for en_s, de_s in INFO.items():
        extra = set(re.findall(r"\d+", de_s)) - set(re.findall(r"\d+", en_s))
        assert not extra, f"info 数字错配：德语多出 {sorted(extra)}\n  en={en_s}\n  de={de_s}"

    # 各来源的键不得相交 —— 输出时用 `or` 串联，相交会**静默取到另一条的值**
    srcs = {"FUP": set(FUP), "PROMO": set(PROMO), "INFO": set(INFO)}
    names = list(srcs)
    overlap: set[str] = set()
    for i, a in enumerate(names):
        for b in names[i + 1:]:
            overlap |= srcs[a] & srcs[b]
    assert not overlap, f"键相交（会静默取错值）：{sorted(overlap)}"

    lines = [HEAD]
    for k in sorted(FUP) + sorted(PROMO) + sorted(INFO) + sorted(quirks):
        v = FUP.get(k) or PROMO.get(k) or INFO.get(k) or quirks.get(k)
        lines.append(f'"{toml_escape(k)}" = "{toml_escape(v)}"\n')
    out = ROOT / "data" / "de" / "strings.toml"
    out.write_bytes("".join(lines).encode("utf-8"))
    b = out.read_bytes()
    assert b.count(b"\r\n") == 0
    print(
        f"{out}: {len(FUP)} fup_note + {len(PROMO)} promo_label + {len(INFO)} info "
        f"+ {len(quirks)} quirks = "
        f"{len(FUP) + len(PROMO) + len(INFO) + len(quirks)} entries, "
        f"{len(b)} bytes"
    )
    print(
        f"数据侧 fup_note {len(fup)} 个不同取值 / {sum(fup.values())} 条；promo_label {len(promo)} 个；"
        f"info.support/refund {len(info)} 个不同取值；quirks {len(quirks)} 条 / {len(en_quirks)} 国"
    )


if __name__ == "__main__":
    main()
