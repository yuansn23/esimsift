#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Generate the missing A-vs-B matchup pages (content/<lang>/compare/{a}-vs-{b}.md).

Why this exists: adding a brand grows the matchup set from C(8,2)=28 to C(9,2)=36.
The 28 originals were hand-written; regenerating them would churn pages that are
already indexed, so this script ONLY creates pairs that do not exist yet and never
rewrites an existing file.

Naming/format rules are the ones the live site already enforces:
  · filename == "{a}-vs-{b}.md" with a < b alphabetically (scripts/validate.py §7)
  · providers = ["a", "b"] in the same alphabetical order
  · layout: vs-single
  · title 48-54 chars (scripts/audit_meta.py) — candidates come from the same
    two families scripts/regen_meta_brand.py uses, so new pages read identically
    to the old ones; first candidate that fits is taken
  · description 120-140 chars and must contain "eSIM Sift"; the family rotates by
    index so the new pages do not all open with the same sentence
    (anti-homogenization — same idea as the anchor rotation in regen_meta_brand)

语言（--lang en|de）：
  en → content/en/compare/…  （历史 45 页已存在 ⇒ 本脚本对它**永不写盘**）
  de → content/de/compare/…  （首次全量创建，带 noindex: true，D9 统一解禁）
  ⚠ vs 页没有 `iso` ⇒ head.html 不做 i18n 标题推导，**front matter 的 title 就是
    `<title>`** —— 所以德语的 title 必须逐条德语化，长度区间也另设（德语更长）。

Usage:
  python -X utf8 scripts/gen_vs_pages.py [--lang de] [--dry-run]
"""
import sys
import tomllib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
DRY = "--dry-run" in sys.argv

LANG = "en"
_a = sys.argv[1:]
for _i, _x in enumerate(_a):
    if _x == "--lang":
        LANG = _a[_i + 1]
    elif _x.startswith("--lang="):
        LANG = _x.split("=", 1)[1]
if LANG not in ("en", "de"):
    sys.exit(f"ERROR: --lang must be en|de, got {LANG!r}")

COMPARE = ROOT / "content" / LANG / "compare"
NOINDEX = LANG != "en"

TITLE_MIN, TITLE_MAX = (48, 54) if LANG == "en" else (48, 64)
DESC_MIN, DESC_MAX = (120, 140) if LANG == "en" else (120, 165)

providers = tomllib.loads((DATA / "providers.toml").read_text(encoding="utf-8"))
brands = {k: v for k, v in providers.items() if isinstance(v, dict) and v.get("name")}


def title_candidates(a: str, b: str) -> list[str]:
    """Same two families as the live pages, longest first."""
    if LANG == "en":
        return [
            f"{a} vs {b} eSIM Compared: Prices and Verdict 2026",
            f"{a} vs {b} eSIM: Prices, Data and Verdict 2026",
            f"{a} vs {b} eSIM: Prices and Verdict 2026",
            f"{a} or {b} eSIM? 2026 Price and Data Comparison",
            f"{a} or {b} eSIM? Full 2026 Price Comparison",
            f"{a} or {b} eSIM? 2026 Price Comparison",
            f"{a} vs {b} eSIM: Which Is Cheaper in 2026?",
            f"{a} vs {b} eSIM: 2026 Price and Data Comparison",
        ]
    return [
        f"{a} vs {b} eSIM im Vergleich: Preise und Fazit 2026",
        f"{a} vs {b} eSIM: Preise, Daten und Fazit 2026",
        f"{a} vs {b} eSIM: Preise und Daten im Vergleich 2026",
        f"{a} vs {b} eSIM: Wer ist 2026 günstiger?",
        f"{a} oder {b} eSIM? Der große Preisvergleich 2026",
        f"{a} oder {b} eSIM? Preisvergleich 2026",
        f"{a} vs {b} eSIM: Preis- und Datenvergleich 2026",
    ]


def desc_candidates(a: str, b: str, i: int) -> list[str]:
    """Three rotated families (anti-homogenization), long form first."""
    if LANG == "de":
        fams = [
            [
                f"eSIM Sift vergleicht {a} und {b}: Einstiegspreise, $/GB und Unlimited-Daten in jedem gemeinsamen Land — ein berechnetes Fazit.",
                f"eSIM Sift vergleicht {a} und {b}: Einstiegspreise, $/GB und Unlimited-Daten in jedem gemeinsamen Land.",
            ],
            [
                f"{a} oder {b} für die Reise? eSIM Sift rechnet das Fazit: günstigster Tarif je Land, bester $/GB, Unlimited-Abdeckung — Live-Preise.",
                f"{a} oder {b} für die Reise? eSIM Sift rechnet das Fazit: günstigster Tarif je Land, bester $/GB, Unlimited-Abdeckung.",
            ],
            [
                f"Welche eSIM ist günstiger, {a} oder {b}? eSIM Sift vergleicht Einstiegspreise, $/GB und Fair-Use-Grenzen in jedem gemeinsamen Land.",
                f"Welche eSIM ist günstiger, {a} oder {b}? eSIM Sift vergleicht Einstiegspreise, $/GB und Fair-Use-Grenzen je Land.",
            ],
        ]
        return fams[i % 3]
    fams = [
        [
            f"eSIM Sift compares {a} and {b} eSIMs: entry prices, $/GB and unlimited data in every shared country — a computed verdict.",
            f"eSIM Sift compares {a} and {b} eSIMs: entry prices, $/GB and unlimited data in every shared country.",
        ],
        [
            f"{a} or {b} for your trip? eSIM Sift computes the verdict: cheapest plan per country, best $/GB, unlimited coverage — live prices.",
            f"{a} or {b} for your trip? eSIM Sift computes the verdict: cheapest plan per country, best $/GB, unlimited coverage.",
        ],
        [
            f"Which eSIM is cheaper, {a} or {b}? eSIM Sift compares entry prices, $/GB and fair-use caps in every shared country — prices change.",
            f"Which eSIM is cheaper, {a} or {b}? eSIM Sift compares entry prices, $/GB and fair-use caps in every shared country.",
        ],
    ]
    return fams[i % 3]


def fit(cands: list[str], lo: int, hi: int) -> str | None:
    return next((c for c in cands if lo <= len(c) <= hi), None)


keys = sorted(brands)
created, skipped, problems = [], [], []

for i, a in enumerate(keys):
    for b in keys[i + 1:]:
        f = COMPARE / f"{a}-vs-{b}.md"
        if f.exists():
            skipped.append(f.name)
            continue
        na, nb = brands[a]["name"], brands[b]["name"]
        tcands = title_candidates(na, nb)
        if LANG == "de":
            # 德语候选 1 对全部品牌名都落在区间内 ⇒ 45 页会共用同一句式。
            # 轮换起点制造句式多样性（同 desc 的 fams 轮换思路）。
            _r = (i + len(created)) % len(tcands)
            tcands = tcands[_r:] + tcands[:_r]
        title = fit(tcands, TITLE_MIN, TITLE_MAX)
        desc = fit(desc_candidates(na, nb, i + len(created)), DESC_MIN, DESC_MAX)
        if not title or not desc:
            problems.append(
                f"{a}-vs-{b}: no candidate fits "
                f"(title cands={[len(c) for c in title_candidates(na, nb)]}, "
                f"desc cands={[len(c) for c in desc_candidates(na, nb, i)]})"
            )
            continue
        lines = [
            "---",
            f'title: "{title}"',
            f'description: "{desc}"',
            f'providers: ["{a}", "{b}"]',
            "layout: vs-single",
        ]
        if NOINDEX:
            lines += ["noindex: true",
                      f"# TODO({LANG})：本页由 scripts/gen_vs_pages.py 生成，"
                      f"正文来自 data/plans/*.toml（模板已本地化）。"
                      f"D9 解禁时统一删掉上面 noindex 行。"]
        lines += ["---", ""]
        body = "\n".join(lines)
        if not DRY:
            # 与德语侧其余 md 一致用 LF；英文侧历史文件是 CRLF
            f.write_text(body, encoding="utf-8", newline="\r\n" if LANG == "en" else "\n")
        created.append((f.name, len(title), len(desc)))

print(f"[{LANG}] existing matchups untouched: {len(skipped)}")
print(f"{'[dry] would create' if DRY else 'created'}: {len(created)}")
for name, tl, dl in created:
    print(f"  {name:32s} title={tl} desc={dl}")
if problems:
    print(f"\n{len(problems)} problem(s):")
    for p in problems:
        print("  " + p)
    sys.exit(1)
