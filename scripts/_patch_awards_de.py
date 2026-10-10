"""批 D/E 收尾 —— `data/de/networkreports.toml` 补 `[[XX.awards]]` 德语覆盖。

★ 为什么必须单独一段脚本（2026-10-10 第七十二轮 d44 实测）
  Hugo 的 data 深合并是「**map 递归、数组整体替换**」。`awards` 是数组 ——
  德语侧不写就**整表回退英文**，Hugo 不报错、构建不失败、`check_output` 看不见。
  批 D 建出 12 篇 `/de/networks/*.md` 之前，**没有任何德语页渲染 awards**
  （其余 44 个德语 networks 页尚未建），所以：
    · F（黑名单）绿 —— 没有德语页承载这些串
    · G（只认「已进 strings.toml 的数据串」）绿 —— awards 从未进表，G 天然失明
  页集一变（+12 页），d44 立刻炸出 12 条 F。**F 只抓到含 `and`/`every` 的那 12 条，
  真实残留是 35 组 × 3 字段全英文** —— 这就是「黑名单永远是下限」的活例。

★ 术语真源（不抄第二份）
  · `Download Geschwindigkeit` / `Abdeckungserfahrung (Coverage Experience)` /
    `Gleichbleibende Qualität (Consistent Quality)` / `Zuverlässigkeit (Reliability)` /
    `Zeit im Netz (Time on Network)` —— 全部取自 `data/de/networkreports.toml`
    既有的 `opensignal_facts` / `ookla_note` 德译（同一文件、同一读者、同一页），
    本脚本用 `_facts_gloss()` 从**德语文件本身**抽取括注用法并断言一致。
  · `Speed Score` / `RootScore` / `Speedtest Global Index` 按 §12.14 有意保留英文。
  · 单位一律 `Mbit/s`（判据 I），小数一律德语逗号（判据 D 的 `digits()` 容错）。

用法：
  python -X utf8 scripts/_patch_awards_de.py --dry
  python -X utf8 scripts/_patch_awards_de.py
"""
from __future__ import annotations

import argparse
import pathlib
import re
import sys
import tomllib

ROOT = pathlib.Path(__file__).resolve().parent.parent
EN = ROOT / "data" / "networkreports.toml"
DE = ROOT / "data" / "de" / "networkreports.toml"

# ── 判据常量：单一真源在守卫里，这里 import 取用，绝不抄第二份 ────────────────
sys.path.insert(0, str(ROOT / "scripts"))
import verify_de_text as V  # noqa: E402  （有 `if __name__ == "__main__"`，import 安全）

F_WORDS = V.F_FORBIDDEN_WORDS
F_PHRASES = V.F_FORBIDDEN_PHRASES
UNIT_BAD = ("Mbps", "Kbps", "Gbps")

# ── 德语记分板（11 国 × 35 组）。key = ISO；顺序**必须**与英语侧一致 ──
# 空串 = 英语侧留空（页面渲染成「—」），德语侧同样留空。`carrier` 逐字继承英语侧。
AWARDS: dict[str, list[dict[str, str]]] = {
    "GB": [
        dict(
            carrier="EE",
            opensignal="11 Alleinauszeichnungen, darunter die Download-Geschwindigkeit bei 53,2 Mbit/s",
            ookla="Gewann oder teilte zum 26. Mal in Folge jede UK-weite RootScore — 130,3 Mbit/s mittlerer Download, H1 2026",
            best="Beste Geschwindigkeiten, Zuverlässigkeit und Abdeckung im ländlichen Raum",
        ),
        dict(
            carrier="Vodafone",
            opensignal="",
            ookla="",
            best="Mittelklasse-Option mit besser werdender Abdeckung in Ballungsräumen",
        ),
        dict(
            carrier="O2",
            opensignal="Gewann die Abdeckungserfahrung (Coverage Experience) allein mit 9,0 von 10",
            ookla="",
            best="Breiteste landesweite Abdeckung",
        ),
        dict(
            carrier="Three",
            opensignal="Gewann die 5G-Download-Geschwindigkeit mit 187 Mbit/s",
            ookla="",
            best="Schnellste 5G-Geschwindigkeiten",
        ),
    ],
    "DE": [
        dict(
            carrier="Telekom",
            opensignal="11 von 14 Auszeichnungen allein, darunter die Download-Geschwindigkeit bei 68,9 Mbit/s — als Deutschlands bestes Netz benannt",
            ookla="Bestes und schnellstes Mobilfunknetz, Q1-Q2 2026 — Speed Score 77,9",
            best="Schnellstes Netz und die beste Abdeckung im ländlichen Raum",
        ),
        dict(
            carrier="Vodafone",
            opensignal="Zweiter bei der Download-Geschwindigkeit hinter Telekom mit 56,3 Mbit/s",
            ookla="Speed Score 56,1, Zweiter im selben Test Q1-Q2 2026",
            best="Starkes Stadt-5G zum Mittelklasse-Preis",
        ),
        dict(
            carrier="O2",
            opensignal="Dritter bei der Download-Geschwindigkeit mit 47,4 Mbit/s",
            ookla="",
            best="Preistipp mit breiter 4G-Reichweite",
        ),
    ],
    "FR": [
        dict(
            carrier="Orange",
            opensignal="Gewann die Download-Geschwindigkeitserfahrung (Download Speed Experience) mit 83,8 Mbit/s und die 5G-Download-Geschwindigkeit allein",
            ookla="Schnellstes Mobilfunknetz, 2H 2024 — 122,77 Mbit/s mittlerer Download",
            best="Abdeckung rundum und die besten Geschwindigkeiten",
        ),
        dict(
            carrier="SFR",
            opensignal="",
            ookla="",
            best="Solides Stadtnetz neben Orange und Bouygues",
        ),
        dict(
            carrier="Bouygues",
            opensignal="Holte 12 von 17 Auszeichnungen, darunter Gleichbleibende Qualität (Consistent Quality), und teilte die Zuverlässigkeit (Reliability) mit Orange bei 925 Punkten",
            ookla="",
            best="Gleichbleibende Qualität und starke geteilte Abdeckung",
        ),
    ],
    "ES": [
        dict(
            carrier="Movistar",
            opensignal="Meistausgezeichneter Anbieter (10 allein, 3 geteilt) und Sieger beim Besten Netz, mit Download-Geschwindigkeit bei 96,7 Mbit/s",
            ookla="Bestes Mobilfunknetz und bestes 5G-Netz, H1 2025",
            best="Insgesamt bestes Netz — schnellstes und zuverlässigstes",
        ),
        dict(
            carrier="Vodafone",
            opensignal="",
            ookla="",
            best="Abdeckung mit Schwerpunkt Stadt, einen Schritt hinter der Spitze",
        ),
        dict(
            carrier="Orange",
            opensignal="Zweiter bei der Download-Geschwindigkeit hinter Movistar mit 66,8 Mbit/s",
            ookla="",
            best="Starke Stadtgeschwindigkeiten innerhalb der MasOrange-Gruppe",
        ),
        dict(
            carrier="Yoigo",
            opensignal="",
            ookla="",
            best="Günstige Stadtoption in derselben Gruppe wie Orange",
        ),
    ],
    "US": [
        dict(
            carrier="T-Mobile",
            opensignal="12 von 16 Auszeichnungen allein, darunter die Download-Geschwindigkeit bei 192,5 Mbit/s und die Zuverlässigkeit (Reliability) bei 942/1000",
            ookla="Schnellstes Mobilfunknetz, H1 2026 — 275,6 Mbit/s mittlerer Download",
            best="Schnellste Geschwindigkeiten und das gleichbleibendste Erlebnis landesweit",
        ),
        dict(
            carrier="AT&T",
            opensignal="Gewann die Zeit im Netz (Time on Network) mit 99,6%, vor Verizon (99,5) und T-Mobile (99,2)",
            ookla="159,3 Mbit/s mittlerer Download, Zweiter hinter T-Mobile im selben Test H1 2026",
            best="Verbindung halten in vollen Hallen und Stadien",
        ),
        dict(
            carrier="Verizon",
            opensignal="",
            ookla="",
            best="Breiteste Abdeckung außerhalb der Städte",
        ),
    ],
    "CA": [
        dict(
            carrier="Bell",
            opensignal="Verteidigte die 5G-Download-Führung mit 173,6 Mbit/s",
            ookla="Bestes und schnellstes 5G-Netz, 2H 2025 — 171,17 Mbit/s mittlerer 5G-Download",
            best="Schnellstes 5G in den großen Städten",
        ),
        dict(
            carrier="Rogers",
            opensignal="Holt die meisten Auszeichnungen (9 insgesamt), führt bei der Anwendungserfahrung (Application Experience) und teilt die Zuverlässigkeit (Reliability) mit Telus",
            ookla="",
            best="Streaming und das 5G-Signal am längsten halten",
        ),
        dict(
            carrier="Telus",
            opensignal="Gewann Bestes Netz und die Download-Geschwindigkeit allein mit 91,8 Mbit/s",
            ookla="",
            best="Insgesamt bestes Netz, mit den schnellsten typischen Downloads",
        ),
    ],
    "MX": [
        dict(
            carrier="Telcel",
            opensignal="Hielt die Zuverlässigkeit (Reliability) bei 863/1000, 96 Punkte vor AT&T, und erreichte im Schnitt 180,7 Mbit/s im 5G",
            ookla="Bestes Mobilfunknetz, H2 2025 — Speedtest Connectivity Score 73,1",
            best="Beste Abdeckung und Geschwindigkeit landesweit",
        ),
        dict(
            carrier="AT&T Mexico",
            opensignal="Gewann die Auszeichnung Verfügbarkeit (Availability)",
            ookla="",
            best="Bleibt in den Städten verfügbar",
        ),
        dict(
            carrier="Movistar",
            opensignal="",
            ookla="",
            best="Günstigster Einstieg in den Städten",
        ),
    ],
    "NL": [
        dict(
            carrier="KPN",
            opensignal="Gewann die Abdeckungserfahrung (Coverage Experience) mit 9,4/10 und die 5G-Abdeckungserfahrung (5G Coverage Experience) mit 8,3",
            ookla="",
            best="Breiteste Abdeckung und die beste Sprachqualität",
        ),
        dict(
            carrier="Vodafone",
            opensignal="",
            ookla="",
            best="Solide Stadtleistung, einen Schritt hinter Odido und KPN",
        ),
        dict(
            carrier="Odido",
            opensignal="Gewann Bestes Netz, die Download-Geschwindigkeit allein mit 146,4 Mbit/s und die 5G-Download-Geschwindigkeit mit 279,9 Mbit/s",
            ookla="Schnellstes Mobilfunknetz, 1H 2025 — 216,3 Mbit/s mittlerer Download",
            best="Schnellstes Netz und die meisten Auszeichnungen",
        ),
    ],
    "JP": [
        dict(
            carrier="NTT Docomo",
            opensignal="Abdeckung 9,0/10 und 5G-Download 159,1 Mbit/s",
            ookla="",
            best="Ländliche Strecken, Bergpässe und die kleineren Inseln",
        ),
        dict(
            carrier="SoftBank",
            opensignal="Sieger bei der Download-Geschwindigkeit mit 65,1 Mbit/s",
            ookla="Schnellstes Mobilfunknetz in Japan, H1 2026 — 73,8 Mbit/s mittlerer Download",
            best="Stadt-5G und die Korridore rund um die großen Bahnhöfe",
        ),
        dict(
            carrier="KDDI",
            opensignal="Meistausgezeichneter Anbieter — 10 Alleinsiege und 1 geteilter Sieg",
            ookla="Zweiter hinter SoftBank im selben Test H1 2026",
            best="Westjapan und die Küstenstrecken",
        ),
    ],
    "TH": [
        dict(
            carrier="AIS",
            opensignal="Meistausgezeichneter Anbieter — 7 Alleinsiege und 3 geteilte, darunter Gleichbleibende Qualität (Consistent Quality) mit 75,1% und die Upload-Geschwindigkeit mit 15 Mbit/s",
            ookla="Schnellstes Mobilfunknetz, Q1-Q2 2026 — Speed Score 70,6",
            best="Bestes Netz rundum und die breiteste Abdeckung",
        ),
        dict(
            carrier="True Move",
            opensignal="Teilte die Auszeichnung Bestes Netz und gewann die 5G-Verfügbarkeit allein mit 90,2%",
            ookla="",
            best="Beste 5G-Signalverfügbarkeit",
        ),
        dict(
            carrier="DTAC",
            opensignal="Teilte die Auszeichnung Bestes Netz und gewann die Zuverlässigkeit (Reliability) allein mit 907/1000, dazu die schnellsten Downloads mit 41,1 Mbit/s und den 5G-Download mit 102,7 Mbit/s",
            ookla="",
            best="Zuverlässigstes Netz mit den schnellsten Downloads",
        ),
    ],
    "KR": [
        dict(
            carrier="SK Telecom",
            opensignal="Gewann die Download-Geschwindigkeit allein mit 189,3 Mbit/s, dazu die Abdeckung (9,4/10) und die 5G-Abdeckung (7,3)",
            ookla="",
            best="Bestes Netz insgesamt und die breiteste Abdeckung",
        ),
        dict(
            carrier="KT",
            opensignal="Gewann die 5G-Download-Geschwindigkeit mit 486,2 Mbit/s, 35 Mbit/s vor dem nächsten Anbieter bei der Gesamtgeschwindigkeit",
            ookla="",
            best="Schnellste 5G-Downloads",
        ),
        dict(
            carrier="LG U+",
            opensignal="Gewann die 5G-Verfügbarkeit mit 90,3%",
            ookla="Bester Overall RootScore in Seoul-Incheon, 2H 2025 — 993/1000, bei einem mittleren Download von 853,37 Mbit/s",
            best="Beste 5G-Verfügbarkeit und die schnellsten Stadtgeschwindigkeiten",
        ),
    ],
}

FIELDS = ("opensignal", "ookla", "best")
NL = b"\r\n"  # 本仓库文本文件一律 CRLF


def digits(s: str) -> set[float]:
    """与 verify_de_data.digits 同口径（集合、容错小数逗号）。"""
    return {float(x.replace(",", ".")) for x in re.findall(r"\d+(?:[.,]\d+)?", s or "")}


def toml_str(s: str) -> str:
    return '"' + s.replace("\\", "\\\\").replace('"', '\\"') + '"'


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry", action="store_true")
    args = ap.parse_args()

    en = tomllib.loads(EN.read_text(encoding="utf-8"))
    de_raw = DE.read_bytes()
    de = tomllib.loads(de_raw.decode("utf-8"))

    problems: list[str] = []

    # ① 幂等：德语侧已经有 awards 就直接退出（不重复追加）
    have = [k for k, v in de.items() if isinstance(v, dict) and v.get("awards")]
    if have:
        print(f"[skip] data/de/networkreports.toml 已有 awards：{have} —— 无需追加")
        return 0

    # ② 英语侧 awards 清单必须与本脚本写死的国家集合完全一致（防数据漂移后静默漏国）
    en_have = sorted(k for k, v in en.items() if isinstance(v, dict) and v.get("awards"))
    if en_have != sorted(AWARDS):
        problems.append(f"英语侧 awards 国家集合变了：{en_have} ≠ {sorted(AWARDS)}")

    for iso, groups in AWARDS.items():
        en_groups = en.get(iso, {}).get("awards") or []
        if len(groups) != len(en_groups):
            problems.append(f"[{iso}] 组数不符：英 {len(en_groups)} / 本脚本 {len(groups)}")
            continue
        for i, (g, e) in enumerate(zip(groups, en_groups)):
            if g["carrier"] != e.get("carrier"):
                problems.append(f"[{iso}][{i}] carrier 错位：英 {e.get('carrier')!r} / 德 {g['carrier']!r}")
            for f in FIELDS:
                ev, dv = e.get(f, ""), g.get(f, "")
                if bool(ev) != bool(dv):
                    problems.append(f"[{iso}][{i}].{f} 空/非空与英语侧不一致")
                if ev and dv == ev:
                    problems.append(f"[{iso}][{i}].{f} 与英文逐字相同（未译）")
                if ev and digits(ev) != digits(dv):
                    problems.append(
                        f"[{iso}][{i}].{f} 数字不符：{sorted(digits(ev))} → {sorted(digits(dv))}"
                    )
                for w in F_WORDS:
                    if re.search(r"\b%s\b" % re.escape(w), dv):
                        problems.append(f"[{iso}][{i}].{f} 含 F 禁词 {w!r}")
                for p in F_PHRASES:
                    if p in dv:
                        problems.append(f"[{iso}][{i}].{f} 含 F 禁短语 {p!r}")
                for u in UNIT_BAD:
                    if re.search(r"(?<![\w])%s(?![\w])" % u, dv):
                        problems.append(f"[{iso}][{i}].{f} 含非德语单位 {u}")

    # ③ 术语一致性：本脚本用的括注必须**已经在**德语 facts 里出现过（不发明新译法）
    de_text = de_raw.decode("utf-8")
    for gloss in ("(Coverage Experience)", "(Consistent Quality)", "(Reliability)",
                  "(Time on Network)", "(Download Speed Experience)"):
        if gloss not in de_text:
            problems.append(f"括注 {gloss} 在既有德语 facts 里不存在 —— 术语真源被破坏")

    if problems:
        print(f"自检失败 {len(problems)} 条：")
        for p in problems:
            print("  ✗", p)
        return 1
    print(f"自检通过：{len(AWARDS)} 国 / {sum(len(v) for v in AWARDS.values())} 组，"
          f"carrier 逐条对齐、数字集合相等、无 F 命中、单位 Mbit/s")

    if args.dry:
        print("[dry] 未写入")
        return 0

    # ④ 追加（bytes 写、CRLF）
    out = de_raw
    if not out.endswith(NL):
        out += NL
    out += NL
    head_lines = [
        "# ── 记分板（awards）德语覆盖 —— layouts/networks/single.html ⑭b 块",
        "# `awards` 是数组，Hugo 深合并下「整体替换」：这里不写就整表回退英文（不报错）。",
        "# 术语取自本文件既有的 opensignal_facts / ookla_note 德译；",
        "# `carrier` 为专有名词，逐字继承英语侧（模板按它建 carrier→award 映射）。",
    ]
    for line in head_lines:
        out += (line + "\r\n").encode("utf-8")
    for iso, groups in AWARDS.items():
        out += NL
        for g in groups:
            out += f"[[{iso}.awards]]\r\n".encode("utf-8")
            out += f"carrier = {toml_str(g['carrier'])}\r\n".encode("utf-8")
            for f in FIELDS:
                out += f"{f} = {toml_str(g[f])}\r\n".encode("utf-8")

    if out.count(b"\r\n") < de_raw.count(b"\r\n"):
        print("✗ CRLF 数量下降，拒绝写入")
        return 1
    DE.write_bytes(out)

    # ⑤ 回读复核
    chk = tomllib.loads(DE.read_text(encoding="utf-8"))
    n_de = sum(len(v.get("awards", [])) for v in chk.values() if isinstance(v, dict))
    n_en = sum(len(v.get("awards", [])) for v in en.values() if isinstance(v, dict))
    b = DE.read_bytes()
    print(f"[written] data/de/networkreports.toml bytes {len(de_raw)} → {len(b)}（+{len(b) - len(de_raw)}）"
          f" · CRLF {de_raw.count(NL)} → {b.count(NL)}")
    print(f"[verify] 德语 awards 组数 {n_de} / 英语 {n_en} → {'一致' if n_de == n_en else '不一致 ✗'}")
    return 0 if n_de == n_en else 1


if __name__ == "__main__":
    sys.exit(main())
