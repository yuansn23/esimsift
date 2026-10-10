"""批 D 术语归一 —— 把 12 篇 networks 正文里的 `Tempo` 方言并回全站标准 `Geschwindigkeit`。

★ 为什么要做（2026-10-10 第七十二轮，批 E 收尾时发现）
  `data/de/networkreports.toml` 的**记分板表格**（`layouts/networks/single.html:244`）与
  正文（同文件 `:213` `{{ .Content }}`）**渲染在同一页**。批 D 的正文用
  `Download-Tempo`，而数据层（既有的 opensignal_facts / 本轮新写的 awards）用
  `Download-Geschwindigkeit` ⇒ 同一个 `/de/networks/{land}/` 页面上同义词打架。
  这就是「同一事实的第二份译文是缺陷不是备份」。

  实测分布（全德语侧 content/de + data/de + i18n）：
    `Geschwindigkeit` 家族 **215** 处 —— i18n/de.toml 28、data/de 119、其余正文
    `Tempo` 家族        **76** 处 —— **全部**集中在 content/de/networks/*.md（批 D 那 12 篇）
  即 `Tempo` 是**批 D 的局部方言**，不是全站标准 ⇒ 向西对齐（改正文，不动数据层）。

★ 德语性数一致
  `Tempo` 是**中性**（das Tempo），`Geschwindigkeit` 是**阴性**（die Geschwindigkeit）。
  裸替换会把 `das Tempo` 变成 `das Geschwindigkeit` ⇒ 冠词/形容词/代词必须同改。
  下面 GRAMMAR 表是**逐条按真实上下文**写的（前 13 条来自全量 dump），
  COMPOUND 表是合成词（无冠词，直接换）。**先 GRAMMAR 后 COMPOUND**，
  且同表内长的排前面（`5G-Tempopreise` 必须在 `5G-Tempo` 之前）。

用法：
  python -X utf8 scripts/_patch_networks_tempo.py --dry
  python -X utf8 scripts/_patch_networks_tempo.py

★ 覆盖范围包含**生成源脚本**（`scripts/_patch_networks_de_{1,a,b,c,batch,terms}.py`）：
  它们是按「内容与字面量比对」决定是否写盘的，字面量留着旧方言 = **重跑就把方言写回去**。
  `_patch_networks_de_terms.py` 更直接 —— 它以「old 命中 0 且 new 已存在」判幂等，
  术语一改它就 FAIL（实测）。所以同一张表必须同时施加到正文与生成源。
"""
from __future__ import annotations

import argparse
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
NET = ROOT / "content" / "de" / "networks"
SRC = ROOT / "scripts"
GEN_SCRIPTS = [
    "_patch_networks_de_1.py",
    "_patch_networks_de_a.py",
    "_patch_networks_de_b.py",
    "_patch_networks_de_c.py",
    "_patch_networks_de_batch.py",
    "_patch_networks_de_terms.py",
]

# ── ① 需要变格的（中性 → 阴性）：长串优先，逐条按上下文写死 ──────────────────
GRAMMAR: list[tuple[str, str]] = [
    ("beim Gesamt-Download-Tempo", "bei der Gesamt-Download-Geschwindigkeit"),
    ("beim kanadischen 5G-Tempo", "bei der kanadischen 5G-Geschwindigkeit"),
    ("mit dem höchsten Median-Download-Tempo", "mit der höchsten Median-Download-Geschwindigkeit"),
    ("mit einem Download-Tempo", "mit einer Download-Geschwindigkeit"),
    ("beim Download-Tempo", "bei der Download-Geschwindigkeit"),
    ("das Download-Tempo", "die Download-Geschwindigkeit"),
    ("beim Tempo", "bei der Geschwindigkeit"),
    ("drosseln meist das Tempo", "drosseln meist die Geschwindigkeit"),
    ("drosseln das Tempo", "drosseln die Geschwindigkeit"),
    ("das Tempo der", "die Geschwindigkeit der"),  # thailand.md「Wo es zählt, ist das Tempo der Verbesserung」
    ("Dein eigenes Tempo", "Deine eigene Geschwindigkeit"),
    ("bei rohem Tempo", "bei roher Geschwindigkeit"),
    ("für reines Tempo", "für reine Geschwindigkeit"),
    ("über das Tempo, das du", "über die Geschwindigkeit, die du"),
]

# ── ② 合成词（带前缀、无冠词）：长串优先 ────────────────────────────────────
COMPOUND: list[tuple[str, str]] = [
    ("Download-Tempo-Erfahrung", "Download-Geschwindigkeitserfahrung"),
    ("Download-Tempo-Preis", "Download-Geschwindigkeitspreis"),
    ("Median-Download-Tempo", "Median-Download-Geschwindigkeit"),
    ("Gesamt-Download-Tempo", "Gesamt-Download-Geschwindigkeit"),
    ("5G-Download-Tempo", "5G-Download-Geschwindigkeit"),
    ("Download-Tempo", "Download-Geschwindigkeit"),
    ("5G-Tempopreise", "5G-Geschwindigkeitspreise"),
    ("5G-Temporekord", "5G-Geschwindigkeitsrekord"),
    ("5G-Tempo", "5G-Geschwindigkeit"),
    ("Tempopreise", "Geschwindigkeitspreise"),
    ("Tempo-Auszeichnungen", "Geschwindigkeitsauszeichnungen"),
    ("Tempo-Tabellen", "Geschwindigkeitstabellen"),
    ("Temporekord", "Geschwindigkeitsrekord"),
    ("Tempokennzahl", "Geschwindigkeitskennzahl"),
    ("Upload-Tempo", "Upload-Geschwindigkeit"),
    ("Downloadgeschwindigkeit", "Download-Geschwindigkeit"),  # 连字符归一（数据层带连字符）
    ("Tempo", "Geschwindigkeit"),                              # 兜底：裸词
]

# 变格后不该出现的形态（阴性名词配中性/阳性冠词）
BAD_FORMS = [
    "das Geschwindigkeit", "dem Geschwindigkeit", "des Geschwindigkeit",
    "ein Geschwindigkeit", "eines Geschwindigkeit", "einem Geschwindigkeit",
    "einen Geschwindigkeit",
]


def _apply(text: str) -> str:
    for a, b in GRAMMAR + COMPOUND:
        text = text.replace(a, b)
    return text


def _check(text: str, label: str) -> str:
    """返回错误说明（空串 = 通过）。"""
    left = text.count("Tempo")
    if left:
        return f"{label} 仍有 {left} 处 Tempo 未归并"
    # ⚠ 必须带**右边界** —— `ein Geschwindigkeitstest` 是合法的复合词，
    # 裸子串匹配会把它判成「错误变格」（本脚本首跑确实这样假红了一次）。
    for bad in BAD_FORMS:
        if re.search(re.escape(bad) + r"(?![A-Za-zÄÖÜäöüß-])", text):
            return f"{label} 出现错误变格 {bad!r}"
    return ""


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry", action="store_true")
    args = ap.parse_args()

    md_files = sorted(NET.glob("*.md"))
    if not md_files:
        print("✗ 找不到 content/de/networks/*.md")
        return 1
    targets = [(f, f.name) for f in md_files] + [
        (SRC / n, "scripts/" + n) for n in GEN_SCRIPTS if (SRC / n).exists()
    ]

    total = 0
    changed: list[tuple[str, int]] = []
    for path, label in targets:
        raw = path.read_bytes()
        text = raw.decode("utf-8")
        before = text.count("Tempo")
        if before == 0:
            continue
        new_text = _apply(text)
        err = _check(new_text, label)
        if err:
            print("✗ " + err)
            return 1
        if not args.dry:
            path.write_bytes(new_text.encode("utf-8"))
        total += before
        changed.append((label, before))

    mode = "[dry] " if args.dry else "[written] "
    print(f"{mode}归并 {total} 处 Tempo → Geschwindigkeit，涉及 {len(changed)} 个文件：")
    for n, c in changed:
        print(f"    {n:34} {c}")

    if args.dry:
        return 0
    # 复核：正文 md 必须 LF-only 且 Tempo 归零
    left = sum(f.read_text(encoding="utf-8").count("Tempo") for f in md_files)
    crlf = sum(f.read_bytes().count(b"\r\n") for f in md_files)
    script_left = sum(
        (SRC / n).read_text(encoding="utf-8").count("Tempo")
        for n in GEN_SCRIPTS if (SRC / n).exists()
    )
    print(f"[verify] 正文剩余 Tempo = {left} · 12 篇 CRLF = {crlf} · 生成源剩余 Tempo = {script_left}")
    return 0 if left == 0 and crlf == 0 and script_left == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
