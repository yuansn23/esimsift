#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Round 22 i18n patch #2: unify the country-hub day chips with the provider page."""
import pathlib, tomllib

ROOT = pathlib.Path(__file__).resolve().parent.parent

REPL = {
    "en": [("compare_single__any", 'compare_single__any = "Any trip length"')],
    "de": [("compare_single__any", 'compare_single__any = "Beliebige Reisedauer"')],
}
NEW = {
    "en": [
        'compare_single__trip_length = "Trip length"',
        'compare_single__n_days = "{{ .n }}+ days"',
    ],
    "de": [
        'compare_single__trip_length = "Reisedauer"',
        'compare_single__n_days = "{{ .n }}+ Tage"',
    ],
}
ANCHOR = "compare_single__any"

for lang in ("en", "de"):
    p = ROOT / "i18n" / f"{lang}.toml"
    lines = p.read_text(encoding="utf-8").split("\n")
    out, hits, skipped = [], 0, 0
    for ln in lines:
        if any(ln.startswith(nl.split(" = ")[0] + " = ") for nl in NEW[lang]):
            skipped += 1
            continue
        done = False
        for old_key, new_line in REPL[lang]:
            if ln.startswith(old_key + " = "):
                out.append(new_line); hits += 1; done = True; break
        if done:
            continue
        out.append(ln)
        if ln.startswith(ANCHOR + " = "):
            out.extend(n for n in NEW[lang] if n not in out)
    p.write_text("\n".join(out), encoding="utf-8", newline="\n")
    with p.open("rb") as fh:
        d = tomllib.load(fh)
    print(f"{lang}: replaced {hits}, skipped {skipped}, total {len(d)} keys")
