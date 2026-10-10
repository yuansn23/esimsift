"""德语国家页 <title> 生成器 —— 写出 data/de/titlesegments.toml。

── 为什么价格锚点是「转录」而不是「重算」────────────────────────────────────
英语侧的 <title> 由 scripts/_solve_titles.py 从 data/plans 现算价格锚点并落盘
（data/titlesegments.toml）。若德语侧**独立再算一次**，同一个数字就有了第二份来源：
某次改价后只重跑了英语脚本（或只重跑德语脚本），两种语言的 <title> 就会对同一个
国家宣称不同的起步价 —— 而两个页面都是线上可访问的。所以这里改成**转录**：
把英语 title 里那个 `$X.XX`（含 `/GB` 与否）原样搬进德语 title。

对应纪律（见 docs/de-l10n-plan.md §10.17）：**能转录就别重算** ——
重算 = 第二份会漂移的事实；转录 = 单一来源。

── 覆盖纪律 ────────────────────────────────────────────────────────────────
必须覆盖**英语侧的全部 50 国**。漏一个，该国的德语页就会回退到英语 title
（`head.html` 只判 `$seg.title` 是否存在，没有语言守卫）—— 50 国里 6 国的英语
title 不带 `$` 锚点（纯文字），早期版本的正则把它们跳过了，只剩 44 条。

运行：
    python -X utf8 scripts/_solve_titles_de.py            # 只打印报告
    python -X utf8 scripts/_solve_titles_de.py --write    # 写 data/de/titlesegments.toml
"""
from __future__ import annotations

import io
import re
import sys
import tomllib
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
EN_SEG = ROOT / "data" / "titlesegments.toml"
DE_COUNTRIES = ROOT / "data" / "de" / "countries.toml"
OUT = ROOT / "data" / "de" / "titlesegments.toml"

YEAR = 2026

# 德语 <title> 里的短国名 —— 只有「全名 + 前缀」超长度带时才覆盖。
SHORT = {"AE": "VAE", "US": "USA", "GB": "Großbritannien"}

# 带价格锚点的段池。{A}=每GB价（$0.55/GB） {U}=最低无限套餐价 {Z}=最低套餐价
POOL: dict[str, tuple[str, list[str]]] = {
    "cheap": ("A", [
        "Günstigste 5G-Tarife ab {A}",
        "Günstigste 5G-Daten ab {A}",
        "Günstige 5G-Daten ab {A}",
        "Günstiges 5G-Datenvolumen ab {A}",
        "Billigste 5G-Daten ab {A}",
        "Günstiger 5G-Tarif ab {A}",
        "5G-Daten günstig ab {A}",
    ]),
    "unlimited": ("U", [
        "Unbegrenztes Datenvolumen ab {U}",
        "Unbegrenzte Daten ab {U}",
        "Unbegrenzt 5G ab {U}",
        "Daten unbegrenzt ab {U}",
        "Unbegrenzt-Datentarif ab {U}",
        "5G-Flatrate ab {U}",
    ]),
    "tourists": ("A", [
        "5G-Daten für Touristen ab {A}",
        "5G-Tarif für Touristen ab {A}",
        "Für Touristen ab {A}",
        "5G für Touristen ab {A}",
    ]),
    "noroam": ("A", [
        "5G-Daten ohne Roaming ab {A}",
        "5G ohne Roaming ab {A}",
        "Ohne Roaming ab {A}",
        "5G-Tarif ohne Roaming ab {A}",
    ]),
    "dataplan": ("A", [
        "5G-Datentarif ab {A}",
        "5G-Datenvolumen ab {A}",
        "5G-Internet ab {A}",
        "Datenvolumen 5G ab {A}",
    ]),
    "value": ("A", [
        "Preiswerte 5G-Daten ab {A}",
        "5G zum kleinen Preis ab {A}",
        "5G-Daten preiswert ab {A}",
    ]),
    "compare": ("Z", [
        "5G-Tarife vergleichen ab {Z}",
        "eSIM-Tarife vergleichen ab {Z}",
        "Tarife vergleichen ab {Z}",
    ]),
    "prepaid": ("A", [
        "Prepaid 5G-Daten ab {A}",
        "Prepaid-5G-Tarif ab {A}",
        "Prepaid-Daten ab {A}",
    ]),
}

# 无价格锚点的国家（英语侧 6 国）：纯文字德语段
PLAIN = [
    "Günstige 5G-Reisedaten für Touristen",
    "5G-Reisedaten-Tarife für Touristen",
    "5G-Daten für Touristen und Besucher",
    "Günstige 5G-Daten für Touristen",
    "5G-Reisedaten für Touristen",
    "Günstige 5G-Reisedaten",
    "5G-Reisedaten-Tarife",
    "5G-Reisedaten",
    "Für Touristen",
]

BAND = (45, 56)          # 目标长度带（德语比英语长，英语侧是 48–54）
BAND_LOOSE = (42, 62)    # 放宽带：BAND 内无解时才用


def read_en() -> list[tuple[str, str]]:
    txt = io.open(EN_SEG, encoding="utf-8").read()
    return re.findall(r'\[([A-Z]{2})\]\s*\ntitle\s*=\s*"([^"]*)"', txt)


def main() -> int:
    en = read_en()
    en_title = dict(en)
    de = tomllib.load(io.open(DE_COUNTRIES, "rb"))
    names = {k: v.get("name", k) for k, v in de.items() if isinstance(v, dict)}

    missing = [i for i, _ in en if i not in names]
    if missing:
        print(f"ERROR 德语 countries.toml 缺国家名: {missing}")
        return 1

    seg_use: Counter = Counter()
    bucket_use: Counter = Counter()
    assign: dict[str, str] = {}
    seg_of: dict[str, str] = {}

    for iso, et in en:
        name = SHORT.get(iso, names[iso])
        prefix = f"{name}-eSIM {YEAR}: "
        priced = "$" in et
        en_kind = "A" if "/GB" in et else ("U" if "Unlimited" in et else "Z")
        _am = re.search(r"\$[\d.]+(/GB)?", et)
        en_anchor = _am.group(0) if _am else None

        cands = []
        if priced:
            for want in (BAND, BAND_LOOSE):
                for bucket, (kt, segs) in POOL.items():
                    if en_kind == "A" and kt != "A":
                        continue
                    if en_kind == "U" and kt not in ("U", "Z"):
                        continue
                    if en_kind == "Z" and kt != "Z":
                        continue
                    for seg in segs:
                        title = prefix + seg.format(A=en_anchor, U=en_anchor, Z=en_anchor)
                        if want[0] <= len(title) <= want[1]:
                            cands.append((bucket, seg, title))
                if cands:
                    break
        else:
            for seg in PLAIN:
                title = prefix + seg
                if 30 <= len(title) <= 62:
                    cands.append(("plain", seg, title))

        if not cands:
            print(f"WARN {iso} ({name}) 无候选段 —— 段池需要补")
            continue
        cands.sort(key=lambda c: (seg_use[c[1]], bucket_use[c[0]], len(c[2])))
        bucket, seg, title = cands[0]
        assign[iso] = title
        seg_of[iso] = seg
        seg_use[seg] += 1
        bucket_use[bucket] += 1

    # ── 交叉核对 ①：覆盖 50/50 ──
    uncovered = [i for i, _ in en if i not in assign]
    # ── 交叉核对 ②：有价格的国家，锚点必须逐字等于英语侧 ──
    bad = []
    for iso, title in assign.items():
        et = en_title[iso]
        if "$" not in et:
            continue
        da = re.search(r"\$[\d.]+(/GB)?", title)
        ea = re.search(r"\$[\d.]+(/GB)?", et)
        if not da or not ea or da.group(0) != ea.group(0):
            bad.append((iso, da.group(0) if da else None, ea.group(0) if ea else None))
    # ── 交叉核对 ③：50 个 title 全唯一（audit_meta 的判据）──
    dupt = [t for t, n in Counter(assign.values()).items() if n > 1]

    print(f"覆盖 {len(assign)}/{len(en)} 个国家   未覆盖: {uncovered}")
    dups = [s for s, n in seg_use.items() if n > 1]
    print(f"段唯一性: {len(seg_use)} 唯一 / 重复 {len(dups)}: {dups[:6]}")
    print(f"bucket 分布: {dict(bucket_use)}")
    lens = sorted(len(t) for t in assign.values())
    print(f"长度: min={lens[0]} med={lens[len(lens)//2]} max={lens[-1]}")
    print(f"锚点不匹配: {len(bad)} {bad[:6]}")
    print(f"整题重复: {len(dupt)}")
    print()
    for iso in sorted(assign, key=lambda i: SHORT.get(i, names[i])):
        print(f"  {iso} [{len(assign[iso]):2d}] {assign[iso]}")

    if uncovered or bad or dupt:
        print("\nERROR 未通过交叉核对 —— 不写盘")
        return 1

    if "--write" in sys.argv:
        buf = ["# 德语国家页 <title> —— 由 scripts/_solve_titles_de.py 生成，不要手改。",
               "# 价格锚点从 data/titlesegments.toml（英语侧）转录：同一数字只有一份来源。",
               ""]
        for iso, _ in en:
            buf.append(f"[{iso}]")
            buf.append(f'title = "{assign[iso]}"')
        io.open(OUT, "wb").write(("\n".join(buf) + "\n").encode("utf-8"))
        print(f"\nWROTE {OUT.relative_to(ROOT).as_posix()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
