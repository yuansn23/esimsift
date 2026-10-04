#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Round 22 i18n patch: long-tail H2, external-source line, days selectors.

Applies the same key set to en.toml and de.toml so check_i18n.py stays aligned.
Idempotent-ish: re-running reports MISS instead of duplicating keys.
"""
import pathlib, sys

ROOT = pathlib.Path(__file__).resolve().parent.parent

# (old_key_or_None, new_line_without_newline)
EN = [
    # 1. long-tail H2 - brand + country + the three intent words in this block
    ("compare_provider__reality_h2",
     'compare_provider__reality_h2 = "{{ .brand }} {{ .country }} eSIM hotspot 5G and fair-use rules"'),
    # 2. the plan-table note no longer describes a sort control
    ("compare_provider__sorted_by_gb_unlimited_plans_listed_last",
     'compare_provider__plans_order_note = "cheapest first · unlimited plans listed last"'),
    # 3. calculator lead: pick, don't type
    ("compare_provider__calc_lead",
     'compare_provider__calc_lead = "Pick your trip length and this re-reads the plan table above on the spot — the cheapest plan whose validity still covers the whole trip, against the cheapest rival in the same country."'),
]

EN_NEW = [
    'compare_provider__official_site = "Official site"',
    'compare_provider__network_sources = "Typical speeds are our editors\' reads of each operator\'s own coverage data. The independent national benchmark is <a href=\\"{{ .url }}\\" target=\\"_blank\\" rel=\\"noopener nofollow\\" class=\\"font-semibold text-brand-700 hover:underline\\">Ookla\'s Speedtest Global Index for {{ .country }}</a>."',
    'compare_provider__plan_days_label = "Trip length"',
    'compare_provider__plan_days_any = "Any trip length"',
    'compare_provider__plan_days_option = "{{ .n }} days"',
    'compare_provider__plan_days_count = "Showing {{ .shown }} of {{ .total }} plans that cover a {{ .n }}-day trip"',
]

DE = [
    ("compare_provider__reality_h2",
     'compare_provider__reality_h2 = "{{ .brand }} {{ .country }} eSIM Hotspot 5G und Fair-Use-Regeln"'),
    ("compare_provider__sorted_by_gb_unlimited_plans_listed_last",
     'compare_provider__plans_order_note = "günstigste zuerst · Unlimited zuletzt"'),
    ("compare_provider__calc_lead",
     'compare_provider__calc_lead = "Wähle deine Reisedauer und die Tabelle oben wird neu ausgewertet — der günstigste Tarif, dessen Laufzeit die ganze Reise abdeckt, gegen den günstigsten Konkurrenten im selben Land."'),
]

DE_NEW = [
    'compare_provider__official_site = "Offizielle Seite"',
    'compare_provider__network_sources = "Die typischen Geschwindigkeiten sind unsere Einschätzung der Coverage-Daten der jeweiligen Betreiber. Der unabhängige Landesvergleich ist <a href=\\"{{ .url }}\\" target=\\"_blank\\" rel=\\"noopener nofollow\\" class=\\"font-semibold text-brand-700 hover:underline\\">Ooklas Speedtest Global Index für {{ .country }}</a>."',
    'compare_provider__plan_days_label = "Reisedauer"',
    'compare_provider__plan_days_any = "Beliebige Reisedauer"',
    'compare_provider__plan_days_option = "{{ .n }} Tage"',
    'compare_provider__plan_days_count = "Angezeigt werden {{ .shown }} von {{ .total }} Tarifen, die eine {{ .n }}-Tage-Reise abdecken"',
]

ANCHOR = 'compare_provider__plans_eyebrow'


def patch(path: pathlib.Path, repl, new_lines):
    text = path.read_text(encoding="utf-8")
    lines = text.split("\n")
    hits, already = 0, 0
    out = []
    for ln in lines:
        # skip a key we are going to add if it somehow already exists
        if any(ln.startswith(nl.split(" = ")[0] + " = ") for nl in new_lines):
            already += 1
            continue
        done = False
        for old_key, new_line in repl:
            if ln.startswith(old_key + " = "):
                out.append(new_line); hits += 1; done = True; break
        if done:
            continue
        out.append(ln)
        if ln.startswith(ANCHOR + " = "):
            out.extend(new_lines)
    path.write_text("\n".join(out), encoding="utf-8", newline="\n")
    print(f"{path.name}: replaced {hits}/{len(repl)}, skipped {already} pre-existing, added {len(new_lines)}")
    if hits != len(repl):
        print("   WARN not every replacement matched - check key names")


patch(ROOT / "i18n" / "en.toml", EN, EN_NEW)
patch(ROOT / "i18n" / "de.toml", DE, DE_NEW)

import tomllib
for name in ("en", "de"):
    with (ROOT / "i18n" / f"{name}.toml").open("rb") as fh:
        d = tomllib.load(fh)
    print(f"{name}: {len(d)} keys, parse OK")
