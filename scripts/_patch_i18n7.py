# -*- coding: utf-8 -*-
"""第二十三轮 i18n 补丁：天数按钮 + 计划数口径 + 量化优劣势。

一次性脚本，跑完即弃（保留在 scripts/ 里作为变更记录 —— 站上其它 _patch_*.py 同理）。

改什么：
  1. 新增 19 个 key：套餐数说明行、#tradeoffs 的量化条目、#fit 的两条。
  2. 改写既有 key `compare_provider__tradeoffs_h2`，把国家词加进 H2（长尾锚点）。
     H2 受 check_headings.py 约束：不得出现 , ; : — –（本行干净）。
  3. en / de 必须同步 —— check_i18n.py 的 check_keys() 会比对两侧 key 集合。

注意：i18n/*.toml 是**扁平**表（无 [section]），所以直接追加到文件末尾是安全的。
"""
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]

# (key, en, de)
NEW = [
    # ── 套餐数说清口径：N 个套餐 = 该国在售的 N 个价格档 ──────────────
    ("compare_provider__plans_breakdown",
     "{{ .n }} plans · {{ .tiers }} trip lengths · {{ .lo }} to {{ .hi }} days",
     "{{ .n }} Tarife · {{ .tiers }} Laufzeiten · {{ .lo }} bis {{ .hi }} Tage"),

    # ── #tradeoffs：赢面（每条都带本页数字）────────────────────────
    ("compare_provider__tradeoffs_w_unl_best",
     "Cheapest unlimited plan in {{ .country }} — ${{ .perday }} a day",
     "Günstigster Unlimited-Tarif in {{ .country }} — ${{ .perday }} pro Tag"),
    ("compare_provider__tradeoffs_w_unl",
     "Unlimited data from ${{ .perday }} a day, against ${{ .bench }} a day for the cheapest unlimited rival",
     "Unlimited-Daten ab ${{ .perday }} pro Tag, gegenüber ${{ .bench }} pro Tag beim günstigsten Unlimited-Konkurrenten"),
    ("compare_provider__tradeoffs_w_pergb",
     "Best $/GB in {{ .country }} — ${{ .pergb }} against a ${{ .bench }} benchmark",
     "Bester $/GB-Wert in {{ .country }} — ${{ .pergb }} gegenüber ${{ .bench }} als Benchmark"),
    ("compare_provider__tradeoffs_w_entry",
     "Entry plan at ${{ .price }} — level with the cheapest plan in {{ .country }}",
     "Einstiegstarif ab ${{ .price }} — gleichauf mit dem günstigsten Tarif in {{ .country }}"),
    ("compare_provider__tradeoffs_w_span",
     "One purchase covers trips from {{ .lo }} to {{ .hi }} days",
     "Ein Kauf deckt Reisen von {{ .lo }} bis {{ .hi }} Tagen ab"),
    ("compare_provider__tradeoffs_w_breakeven",
     "From {{ .days }} days up it undercuts the cheapest metered plan in {{ .country }}",
     "Ab {{ .days }} Tagen unterbietet er den günstigsten Volumentarif in {{ .country }}"),

    # ── #tradeoffs：输面 ─────────────────────────────────────────
    ("compare_provider__tradeoffs_l_gap",
     "On a {{ .days }}-day trip {{ .provider }} costs ${{ .price }} against ${{ .mine }} here — ${{ .diff }} less",
     "Bei einer {{ .days }}-Tage-Reise kostet {{ .provider }} ${{ .price }} statt ${{ .mine }} — ${{ .diff }} weniger"),
    ("compare_provider__tradeoffs_l_min",
     "Its shortest plan runs {{ .days }} days, so a shorter trip still pays for {{ .days }}",
     "Sein kürzester Tarif läuft {{ .days }} Tage — eine kürzere Reise zahlt trotzdem {{ .days }}"),
    ("compare_provider__tradeoffs_l_tiers",
     "{{ .brand }} sells {{ .n }} trip lengths here while {{ .rival }} sells {{ .m }}",
     "{{ .brand }} bietet hier {{ .n }} Laufzeiten an, {{ .rival }} dagegen {{ .m }}"),
    ("compare_provider__tradeoffs_l_hotspot",
     "Hotspot sharing is capped at {{ .allowance }}",
     "Hotspot-Nutzung ist auf {{ .allowance }} begrenzt"),
    ("compare_provider__tradeoffs_l_topup",
     "No top-ups — a used-up plan is replaced rather than refilled",
     "Kein Nachbuchen — ein verbrauchter Tarif wird ersetzt, nicht aufgeladen"),
    ("compare_provider__tradeoffs_l_fup",
     "The fair-use throttle threshold is not published",
     "Die Fair-Use-Drosselschwelle wird nicht veröffentlicht"),
    ("compare_provider__tradeoffs_l_voice",
     "Data-only plans with no local phone number",
     "Nur-Daten-Tarife ohne lokale Rufnummer"),
    ("compare_provider__tradeoffs_l_entry",
     "The ${{ .price }} entry price buys only {{ .data }}",
     "Für ${{ .price }} gibt es nur {{ .data }}"),

    # ── 品牌级内容搬到品牌页，这里只留一条内链 ────────────────────
    ("compare_provider__tradeoffs_brand_link",
     "Brand history and track record",
     "Markengeschichte und Bilanz"),

    # ── #fit：两条由数据推导的量化判据 ─────────────────────────────
    ("compare_provider__fit_breakeven",
     "You are staying {{ .days }} days or more — that is where it first undercuts the cheapest metered plan in {{ .country }}",
     "Sie bleiben {{ .days }} Tage oder länger — ab da unterbietet er den günstigsten Volumentarif in {{ .country }}"),
    ("compare_provider__fit_too_short",
     "You are going for fewer than {{ .days }} days — its shortest plan runs {{ .days }} days",
     "Sie reisen kürzer als {{ .days }} Tage — sein kürzester Tarif läuft {{ .days }} Tage"),
]

REWRITE = [
    # H2 加国家词 → 400 页各自的 H2 不再逐字相同（长尾锚点 + 去重）
    ("compare_provider__tradeoffs_h2",
     "Where {{ .brand }} wins and loses in {{ .country }}",
     "Wo {{ .brand }} in {{ .country }} gewinnt und verliert"),
]


def read(p: pathlib.Path) -> str:
    return p.read_text(encoding="utf-8")


def append_keys(path: pathlib.Path, pairs, comment: str) -> int:
    s = read(path)
    if not s.endswith("\n"):
        s += "\n"
    add = [f"\n# ── {comment} ───────────────────────────────\n"]
    n = 0
    for key, val in pairs:
        if f"\n{key} = " in "\n" + s:
            print(f"  SKIP (已存在): {key}")
            continue
        add.append(f'{key} = "{val}"\n')
        n += 1
    path.write_text(s + "".join(add), encoding="utf-8", newline="\n")
    return n


def rewrite(path: pathlib.Path, key: str, val: str) -> bool:
    s = read(path)
    lines = s.split("\n")
    for i, ln in enumerate(lines):
        if ln.startswith(key + " = "):
            lines[i] = f'{key} = "{val}"'
            path.write_text("\n".join(lines), encoding="utf-8", newline="\n")
            return True
    return False


def main() -> int:
    en = ROOT / "i18n" / "en.toml"
    de = ROOT / "i18n" / "de.toml"
    for p in (en, de):
        if not p.exists():
            print("MISSING", p)
            return 1

    print("追加 en:")
    a = append_keys(en, [(k, e) for k, e, d in NEW],
                    "第二十三轮：天数按钮 / 计划数口径 / 量化优劣势")
    print("追加 de:")
    b = append_keys(de, [(k, d) for k, e, d in NEW],
                    "Runde 23: Tages-Buttons / Tarifzählung / quantifizierte Abwägungen")
    print(f"  en +{a}  de +{b}")

    print("改写 tradeoffs_h2:")
    for p, v in ((en, REWRITE[0][1]), (de, REWRITE[0][2])):
        ok = rewrite(p, REWRITE[0][0], v)
        print(f"  {p.name}: {'OK' if ok else 'MISS'}")

    # 复核 key 数是否对齐
    import tomllib
    ce = len(tomllib.loads(read(en)))
    cd = len(tomllib.loads(read(de)))
    print(f"\nkey 总数 en={ce} de={cd} {'✓ 对齐' if ce == cd else '✗ 不齐'}")
    return 0 if ce == cd else 1


if __name__ == "__main__":
    sys.exit(main())
