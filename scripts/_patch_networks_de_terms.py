#!/usr/bin/env python3
"""批 D 收尾：统一 12 篇德语 networks 正文里的 **Opensignal / Ookla 指标名**译法。

为什么需要（2026-10-10 人工复核发现）：12 篇由 3 组并行产出，
`Download Speed` 出现了 `Download-Geschwindigkeit` / `Download-Geschwindigkeit` / `Download Speed`
三种写法，`Coverage Experience` 出现 `Abdeckungserfahrung` / `Abdeckungserlebnis` /
`Coverage Experience` 三种 —— 同一指标在不同页叫法不同，德语读者会以为是不同东西。
判据抓不到这类问题（不残留英文、标点合规、字段对齐全都过），**只能人工统一**。

统一词表（同时是 `docs/de-l10n-plan.md` §12.16 的权威来源）：
  Download Speed            → Download-Geschwindigkeit
  Download Speed Experience → Download-Geschwindigkeitserfahrung
  5G Download Speed         → 5G-Download-Geschwindigkeit
  Coverage Experience       → Abdeckungserfahrung
  5G Coverage Experience    → 5G-Abdeckungserfahrung
  Reliability Experience    → Zuverlässigkeitserfahrung
  Voice App Experience      → Sprach-App-Erfahrung
  Video Experience          → Video-Erfahrung
  Time on Network           → Zeit im Netz
  Best Network              → Bestes Netz
  5G Availability           → 5G-Verfügbarkeit
  ✅ 保留英文（产品/指标专名，全站一致）：Speed Score / RootScore / Speedtest Global Index /
     Mobile Network Experience Report
规则：外来词合成加连字符（Download-Geschwindigkeitserfahrung / 5G-Abdeckungserfahrung），
      纯德语合成词不加（Abdeckungserfahrung / Zuverlässigkeitserfahrung）。

用法：python -X utf8 scripts/_patch_networks_de_terms.py [--dry]
"""
from __future__ import annotations

import argparse
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
NET = ROOT / "content" / "de" / "networks"

# (slug, old, new, 预期命中次数)
EDITS: list[tuple[str, str, str, int]] = [
    # ── mexico（3 处）
    (
        "mexico",
        "mit Download Speed von 46,0 Mbit/s gegen 27,2 von AT&T und einem 5G-Download von "
        "180,7 Mbit/s, mehr als dreimal so viel wie die Konkurrenz. Es hielt außerdem "
        "Zuverlässigkeit bei 863 von 1000, 96 Punkte vor AT&T, und gewann Coverage Experience.",
        "mit einer Download-Geschwindigkeit von 46,0 Mbit/s gegen 27,2 von AT&T und einem 5G-Download "
        "von 180,7 Mbit/s, mehr als dreimal so viel wie die Konkurrenz. Es hielt außerdem "
        "eine Zuverlässigkeitserfahrung bei 863 von 1000, 96 Punkte vor AT&T, und gewann "
        "die Abdeckungserfahrung.",
        1,
    ),
    (
        "mexico",
        "mit Download Speed Experience von 46,0 Mbit/s gegen 27,2 Mbit/s von AT&T und einem "
        "5G-Download von 180,7 Mbit/s — mehr als dreimal so viel wie die Konkurrenz. Es hielt "
        "außerdem Reliability Experience bei 863 Punkten von 1000, 96 Punkte vor AT&T, und "
        "gewann Coverage Experience.",
        "mit einer Download-Geschwindigkeitserfahrung von 46,0 Mbit/s gegen 27,2 Mbit/s von AT&T und "
        "einem 5G-Download von 180,7 Mbit/s — mehr als dreimal so viel wie die Konkurrenz. "
        "Es hielt außerdem eine Zuverlässigkeitserfahrung bei 863 Punkten von 1000, 96 Punkte "
        "vor AT&T, und gewann die Abdeckungserfahrung.",
        1,
    ),
    # ── netherlands（4 处）
    (
        "netherlands",
        "setzte es bei Download Speed Experience mit 146,4 Mbit/s an die Spitze",
        "setzte es bei der Download-Geschwindigkeitserfahrung mit 146,4 Mbit/s an die Spitze",
        1,
    ),
    (
        "netherlands",
        "setzte Odido bei Download Speed Experience mit 146,4 Mbit/s an die Spitze",
        "setzte Odido bei der Download-Geschwindigkeitserfahrung mit 146,4 Mbit/s an die Spitze",
        1,
    ),
    (
        "netherlands",
        "KPN gewann Coverage Experience mit 9,4 von 10 und 5G Coverage Experience mit 8,3 und "
        "stand bei Voice App Experience mit 83,8 Punkten oben — das Maß, das die Anrufqualität "
        "über Apps wie WhatsApp statt über das zellulare Sprachnetz abdeckt. Time on Network "
        "wurde zum statistischen Gleichstand, 99,3 % gegen 99,1 % von Odido.",
        "KPN gewann die Abdeckungserfahrung mit 9,4 von 10 und die 5G-Abdeckungserfahrung mit "
        "8,3 und stand bei der Sprach-App-Erfahrung mit 83,8 Punkten oben — das Maß, das die "
        "Anrufqualität über Apps wie WhatsApp statt über das zellulare Sprachnetz abdeckt. "
        "Die Zeit im Netz wurde zum statistischen Gleichstand, 99,3 % gegen 99,1 % von Odido.",
        1,
    ),
    (
        "netherlands",
        "und KPNs 5G Coverage Experience von 8,3 von 10 beschreibt",
        "und KPNs 5G-Abdeckungserfahrung von 8,3 von 10 beschreibt",
        1,
    ),
    # ── south-korea（4 处）
    (
        "south-korea",
        "SK Telecom gewann Best Network im Opensignal-Bericht vom Dezember 2025 mit neun "
        "Auszeichnungen direkt plus drei geteilten, darunter Download Speed mit 189,3 Mbit/s "
        "und Coverage Experience mit 9,4 von 10. KT nahm den 5G Download Speed mit 486,2 Mbit/s, "
        "der höchsten 5G-Zahl auf irgendeiner Seite unserer Netzlandkarte. LG U+ gewann "
        "5G Availability mit 90,3 %.",
        "SK Telecom gewann den Titel Bestes Netz im Opensignal-Bericht vom Dezember 2025 mit "
        "neun Auszeichnungen direkt plus drei geteilten, darunter Download-Geschwindigkeit mit "
        "189,3 Mbit/s und Abdeckungserfahrung mit 9,4 von 10. KT nahm das 5G-Download-Geschwindigkeit mit "
        "486,2 Mbit/s, der höchsten 5G-Zahl auf irgendeiner Seite unserer Netzlandkarte. "
        "LG U+ gewann die 5G-Verfügbarkeit mit 90,3 %.",
        1,
    ),
    (
        "south-korea",
        "und den Titel Best Network, mit Download Speed bei 189,3 Mbit/s — etwa 35 Mbit/s vor "
        "KT — und Coverage Experience bei 9,4 von 10, der höchste der drei.",
        "und den Titel Bestes Netz, mit einer Download-Geschwindigkeit von 189,3 Mbit/s — etwa 35 Mbit/s "
        "vor KT — und einer Abdeckungserfahrung von 9,4 von 10, der höchste der drei.",
        1,
    ),
    (
        "south-korea",
        "KTs 5G Download Speed kam mit einer Zahl von 486,2 Mbit/s",
        "KTs 5G-Download-Geschwindigkeit kam mit einer Zahl von 486,2 Mbit/s",
        1,
    ),
    (
        "south-korea",
        "Es stand außerdem bei RootMetrics' Overall RootScore für den Raum Seoul bis Incheon "
        "mit 993 von 1000 oben",
        "Es stand außerdem bei RootMetrics' Overall-RootScore für den Raum Seoul bis Incheon "
        "mit 993 von 1000 oben",
        1,
    ),
    # ── france（2 处：统一 Erlebnis → Erfahrung）
    #    `Abdeckungserlebnis` 在 L38 / L73 各一次 ⇒ 预期命中 2
    ("france", "Abdeckungserlebnis", "Abdeckungserfahrung", 2),
    (
        "france",
        "Video-Erlebnis und gleichbleibende Qualität",
        "Video-Erfahrung und gleichbleibende Qualität",
        1,
    ),
]


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry", action="store_true")
    args = ap.parse_args()

    fails: list[str] = []
    applied = skipped = 0
    touched: set[str] = set()

    for slug, old, new, expect in EDITS:
        p = NET / f"{slug}.md"
        b = p.read_bytes()
        if b.count(b"\r\n"):
            fails.append(f"{slug}.md 含 CRLF")
            continue
        raw = b.decode("utf-8")
        c = raw.count(old)
        if c == 0 and new in raw:
            skipped += 1
            continue
        if c != expect:
            fails.append(f"{slug}.md 锚点命中 {c} 次（期望 {expect}）: {old[:52]!r}")
            continue
        if not args.dry:
            p.write_bytes(raw.replace(old, new).encode("utf-8"))
        applied += 1
        touched.add(slug)

    if fails:
        print("\n".join("FAIL " + f for f in fails))
        return 1

    print(f"编辑：已应用 {applied} 处 / 已存在跳过 {skipped} 处 / 共 {len(EDITS)} 处")

    # 复核：全站德语 networks 不得再残留这些英文指标名
    left: list[str] = []
    for p in sorted(NET.glob("*.md")):
        t = p.read_text(encoding="utf-8")
        for w in (
            "Download Speed",
            "Coverage Experience",
            "Voice App Experience",
            "Time on Network",
            "Best Network",
            "5G Availability",
            "5G Download Speed",
            "Reliability Experience",
        ):
            if w in t:
                left.append(f"{p.name}: {w!r}")
    print("复核：残留英文指标名 " + ("0 处" if not left else str(len(left))))
    for x in left:
        print("  ", x)

    if args.dry:
        print("（--dry：未写盘）")
        return 0
    for slug in sorted(touched):
        b = (NET / f"{slug}.md").read_bytes()
        print(f"  {slug}.md → {len(b)} bytes")
    return 1 if left else 0


if __name__ == "__main__":
    sys.exit(main())
