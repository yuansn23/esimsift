# -*- coding: utf-8 -*-
"""英语 compare 正文事实槽位对账（只读，v2 —— 含品牌与套餐名）。"""
from __future__ import annotations

import importlib.util
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
_spec = importlib.util.spec_from_file_location("_lib", ROOT / "scripts" / "_en_compare_lib.py")
_lib = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_lib)  # type: ignore[union-attr]

report: dict[str, dict[str, list[str]]] = {}
for f in sorted(_lib.EN.glob("*.md")):
    if f.stem in ("_index", "matchups") or "-vs-" in f.stem:
        continue
    text = f.read_text(encoding="utf-8")
    fm = _lib.front_matter(text)
    iso = re.search(r"^iso:\s*(\w+)", fm, re.M).group(1)
    L = _lib.live_values(iso)
    body = _lib.body_of(text)
    bad: dict[str, list[str]] = {}

    def add(slot, got, want):
        if str(got) != str(want):
            bad.setdefault(slot, []).append(f"{got!r} → {want!r}")

    for pat in _lib.RE_T:
        for m in re.finditer(pat, body):
            add("T", m.group(1), L["T"])
    for pat in _lib.RE_U:
        for m in re.finditer(pat, body):
            add("U", m.group(1), L["U"])
    for m in re.finditer(_lib.RE_RATE_GB, body):
        add("rate", m.group(1), L["rate"])
    for m in re.finditer(_lib.RE_RATE_GIG, body):
        add("rate", m.group(1), L["rate"])
    for m in re.finditer(_lib.RE_ENTRY, body):
        if m.group(2) == "MB":
            add("entry_mb", int(float(m.group(1))), L["entry_mb"])
        else:
            add("entry_gb", round(float(m.group(1)), 1), L["entry_gb"])
    for m in re.finditer(_lib.RE_RATIO, body):
        add("ratio", m.group(1), L["ratio"])
    for pat in _lib.RE_DAILY:
        for m in re.finditer(pat, body):
            add("daily", m.group(1), L["daily"])
    for pat in _lib.RE_BREAKEVEN:
        for m in re.finditer(pat, body):
            add("breakeven", m.group(1), L["breakeven"])
    for pat, g1, g2 in _lib.RE_SPEED:
        for m in re.finditer(pat, body):
            add("speed", m.group(1), L["speed_min"])
            add("speed", m.group(2), L["speed_top"])
    for m in re.finditer(_lib.RE_TECH, body):
        add("tech", m.group(1), L["tech"])
    for pat, slot in _lib.RE_BRAND_SLOTS:
        for m in re.finditer(pat, body, re.M):
            g = m.group(1)
            want = L.get(slot + "_brand")
            if want and g.lower() in _lib.BRAND_NAME:
                add("brand@" + slot, _lib.canon(g), want)

    if bad:
        report[f.stem] = bad

print(f"含过期槽位的页：{len(report)} / 50\n")
cnt: dict[str, int] = {}
for slug, bad in report.items():
    print(f"── {slug:24} {', '.join(sorted(bad))}")
    for k in sorted(bad):
        for v in sorted(set(bad[k])):
            print(f"      {k:14} {v}")
        cnt[k] = cnt.get(k, 0) + 1
print("\n== 过期槽位汇总（按页计）==")
for k, v in sorted(cnt.items(), key=lambda x: -x[1]):
    print(f"  {k:16} {v} 页")
