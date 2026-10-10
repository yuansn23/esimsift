# -*- coding: utf-8 -*-
"""批 E · hub：`content/de/compare/_index.md` 的 6 个 h2 德语正文。

对应英语 `content/en/compare/_index.md` 的 6 个 h2，逐节一一对应：
  1 How to compare travel eSIM plans            → 3 段（含 count-countries + count-providers）
  2 eSIM cost per GB and cost per day explained → 5 段（含 2 个粗体定义）
  3 What a country eSIM comparison shows        → 1 段
  4 Why travel eSIM prices differ by country    → 4 段（含 3 个粗体小标题）
  5 Local SIM vs roaming vs eSIM                → 1 段
  6 How to use this eSIM comparison index       → 1 段

⚠ 第 5 节标题必须改写：英语 `Local SIM` 里的 `Local` 在 F 判据禁词表内。

用法：python -X utf8 scripts/_compare_de_hub.py [--dry]
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _compare_de_lib import apply_hub  # noqa: E402

DOCS: list[str] = [
    "## So vergleichst du Reise-eSIM-Tarife",

    "Diese Seite ist die Eingangstür zu unserer gesamten Preisdatenbank. Jeder "
    "Prepaid-Reise-eSIM-Tarif, den wir prüfen können, steht hier drin, sortiert in "
    "{{< count-countries >}} Zieltabellen und {{< count-providers >}} Anbieter — gemessene "
    "Kontingente, tageweise unbegrenzte Tarife und die winzigen Testgrößen, die den Einstiegspreis "
    "auf einer Länderseite setzen.",

    "Nichts auf diesem Index ist redaktionell. Jede Länderkarte zeigt dieselben drei Dinge aus "
    "demselben Snapshot: wie viele Marken dort verkaufen, wie viele Tarife wir erfassen und den "
    "einen günstigsten Tarif, den wir gefunden haben. Die Länderseite hinter der Karte listet dann "
    "jeden Tarif Zeile für Zeile.",

    "## eSIM-Preis pro GB und Preis pro Tag erklärt",

    "Marketing-Seiten für Reise-eSIMs nennen eine Zahl, meist den Einstiegspreis des kleinsten "
    "Tarifs. Diese Zahl ist echt, für die Wahl aber fast nutzlos: ein Tarif für $0.51 ist ein "
    "500-MB-Test, keine Reise.",

    "Deshalb trägt jede Zeile auf dieser Seite zwei abgeleitete Werte, berechnet mit derselben "
    "Formel für jeden Anbieter.",

    "**Preis pro Gigabyte** ist der gelistete Preis geteilt durch das Datenvolumen. Das ist die "
    "Zahl, die dir sagt, ob ein Tarif mit 20 GB besser ist als zehn mit 2 GB, und es ist die "
    "Spalte, die die Standardsortierung auf jeder Länderseite entscheidet.",

    "**Preis pro Tag** ist der gelistete Preis geteilt durch die Gültigkeit in Tagen. Das ist die "
    "Zahl, die zählt, wenn du unbegrenzte Daten kaufst, wo es keine Gigabyte-Zahl zum Teilen gibt.",

    "Wo ein Anbieter unbegrenzte Tarife verkauft, markieren wir sie und listen sie zuletzt, statt "
    "so zu tun, als ließen sie sich nach Gigabyte sortieren. Ihre echten Grenzen stehen in der "
    "Fair-Use-Regel, und die entschlüsseln wir in einer eigenen Tabelle auf jeder Länderseite.",

    "## Was ein Länder-eSIM-Vergleich zeigt",

    "Jede Zielseite folgt derselben Struktur, damit das dritte Land so schnell geht wie das erste: "
    "ein dreizeiliges Fazit, das den günstigsten Tarif, den besten Gegenwert pro Gigabyte und die "
    "beste Option für lange Aufenthalte wählt; die vollständige Tariftabelle mit jedem Anbieter und "
    "jedem Badge; ein Realitätscheck der Fair-Use-Regeln bei den unbegrenzten Tarifen; ein "
    "Netzabschnitt, der erklärt, auf welchen lokalen Betreibern jede Marke fährt; und ein "
    "FAQ-Abschnitt, der die Fragen beantwortet, die die Tabelle nicht kann.",

    "## Warum sich Reise-eSIM-Preise je Land unterscheiden",

    "Drei Dinge, nach Wirkung geordert.",

    "**Großhandelsraten im Ziel.** Eine Reise-eSIM-Marke ist faktisch ein MVNO: Sie kauft "
    "Kapazität von den lokalen Betreibern und verkauft sie weiter. Ziele, in denen "
    "Großhandelsdaten teuer sind — Inselstaaten, Länder mit einem dominierenden Betreiber, Märkte "
    "mit strenger Roaming-Regulierung — starten höher und bleiben höher, egal welche Marke du wählst.",

    "**Wie viele Marken dort konkurrieren.** Beliebte Ziele tragen acht konkurrierende Marken und "
    "scharfe Preise. Dünne Märkte tragen zwei oder drei, und die Spanne zwischen ihnen wird "
    "breiter. Das Kartenraster oben ist so sortiert, dass du siehst, welche Länder das tiefste "
    "Angebot haben.",

    "**Ob der Tarif gemessen oder unbegrenzt ist.** Tageweise unbegrenzte Tarife sind für "
    "Vielnutzer bepreist und meist der falsche Kauf für eine leichte Reise: Bei einer typischen "
    "Tagesrate kostet zwei Wochen unbegrenzt mehr als ein Kontingent, das nie aufgebraucht worden "
    "wäre. Der Umschlagpunkt steht auf jeder Länderseite.",

    "## Lokale SIM vs. Roaming vs. eSIM",

    "Eine Reise-eSIM ist nicht automatisch die günstigste Option — sie ist die günstigste Option, "
    "die funktioniert, bevor du landest. Wo ein Land Prepaid-SIMs frei am Flughafen verkauft, kann "
    "eine lokale SIM eine Reise-eSIM beim Preis unterbieten; der Kompromiss sind die Schlange, die "
    "Registrierungsregeln und die Rufnummer, die du verlierst. Wo Roaming deines Heimatanbieters in "
    "deinem Tarif enthalten ist, kann Roaming beide beim Komfort schlagen. Unsere Zielseiten sagen "
    "dir, welcher Fall vorliegt, und der Abschnitt mit den Länderhinweisen auf jeder Seite deckt "
    "Ausweisregeln, Registrierung und Abdeckungsfallen ab.",

    "## So nutzt du diesen eSIM-Vergleichsindex",

    "Wähle dein Ziel aus dem Raster oder suche danach. Lies zuerst das Drei-Tarife-Fazit oben auf "
    "der Länderseite — es beantwortet die Frage, mit der die meisten ankommen. Ist deine Reise "
    "schwerer als der Durchschnitt, oder brauchst du Hotspot-Sharing, geh in die vollständige "
    "Tabelle und filtere nach Reisedauer. Wenn du noch überlegst, wohin es geht, zeigt die "
    "Rangliste der günstigsten Ziele unten, wo dasselbe Geld die meisten Daten kauft.",
]


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry", action="store_true")
    args = ap.parse_args()
    r = apply_hub(DOCS, dry=args.dry)
    print(f"  [{r:7}] _index.md (hub)\n\n{'（dry-run）' if args.dry else ''}{r}")


if __name__ == "__main__":
    main()
