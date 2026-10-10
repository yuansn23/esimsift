#!/usr/bin/env python3
"""把 `data/devices.toml` 纳入 `scripts/verify_de_text.py` 的 D / G 两条判据。

为什么必须改判据本身，而不是只修数据（2026-10-10 d42 构建实测）：
  `/de/guides/esim-compatibility-check/` 是**本轮新建**的德语页型。它的设备总表由
  `data/devices.toml` 的六个文本字段驱动，此前**没有任何德语页渲染过它们**，于是：
    · F（黑名单：23 短语 + 8 词，靠人想全）—— 只报了首个命中的 `and`；
    · G（穷举，但清单 = `english_data_texts()` = strings.toml 里**已进表**的数据串）
      —— devices 从未进表 ⇒ 清单里没有它 ⇒ 一条不报。
  两条判据同时为绿，而德语页印着整张英文设备表。**页集一变，旧绿灯作废。**

本脚本做 7 处编辑（每处带独立 marker，可重复运行）：
  1 文件头 docstring 的判据 D 说明補 devices
  2 文件头 docstring 的判据 G 说明补 devices
  3 新增 `DEVICES_MODEL_OVERRIDES` 常量 + `load_device_texts()`
  4 `Ctx.__init__` 挂上 `self.devices`
  5 `english_data_texts()` 并入 devices（⇒ G 自动覆盖）
  6 `check_strings()`（判据 D）的 `have` 并入 devices + 统计文案
  7 selftest 补 devices 的**双向**反例（缺条目 / 死条目）

用法：python -X utf8 scripts/_wire_devices_guard.py [--dry]
"""
from __future__ import annotations

import argparse
import ast
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
TARGET = ROOT / "scripts" / "verify_de_text.py"

# ─────────────────────────────────────────────────────────────────────────────
# (old, new) —— old 必须**恰好命中 1 次**；已应用时（new 的独有 marker 在文里）跳过
# ─────────────────────────────────────────────────────────────────────────────

E1_OLD = """  D 覆盖完整  —— 数据里**每一个不同取值**的 `fup_note` / `promo_label` /
                 `info.support` / `info.refund` / `quirks`
                 都必须在 `data/de/strings.toml` 里有德语条目；表里也不许有死条目
"""
E1_NEW = """  D 覆盖完整  —— 数据里**每一个不同取值**的 `fup_note` / `promo_label` /
                 `info.support` / `info.refund` / `quirks` / **`devices.toml` 的六类
                 文本字段**（source_note / name / family / since / note / blocked.*）
                 都必须在 `data/de/strings.toml` 里有德语条目；表里也不许有死条目
"""
E1_MARK = "**`devices.toml` 的六类"

E2_OLD = """     经验（第六十四轮）：`fup_allowance` / `hotspot_note` / `topup_note` 等 policy 字段
     从未进表、模板全是裸插值，德语页整段印英文，而 F 一条没报 —— 因为黑名单里
     「恰好」没有那些词。凡「某类问题已归零」都是断言，先问判据覆盖了哪些写法、哪些页型。
"""
E2_NEW = """     经验（第六十四轮）：`fup_allowance` / `hotspot_note` / `topup_note` 等 policy 字段
     从未进表、模板全是裸插值，德语页整段印英文，而 F 一条没报 —— 因为黑名单里
     「恰好」没有那些词。凡「某类问题已归零」都是断言，先问判据覆盖了哪些写法、哪些页型。
     ★ 第二次同构教训（第七十一轮 · devices 设备表）：**F 与 G 会同时失效**——
     G 的清单来自「已进表的数据串」，一个数据字段若从未进表，G 天然看不见它；
     而 F 只在黑名单命中时报。新页型首次渲染某类数据时，两条都还是绿的。
"""
E2_MARK = "第二次同构教训（第七十一轮 · devices 设备表）"

E3_OLD = '''def load_info_strings() -> set:'''
E3_NEW = '''# `models` 里**唯一**需要在德语页本地化的一条（括号内是英文说明）。
# 351 条机型名是**专有名词**，整体不进 `strings.toml`；而这条若不进表，德语页会印
# `(Europe only)`，且 F 词表（Days/days/Day/Local/and/plans/countries/every）
# 看不见 `only` —— 属静默漏网。
DEVICES_MODEL_OVERRIDES = {"V29 Lite 5G (Europe only)"}


def load_device_texts() -> set[str]:
    """`data/devices.toml` 里需要德语条目的**散文类**文本字段值（含 models 覆盖项）。

    设备总表（`/guides/esim-compatibility-check/`）六个字段都是数据内建英文：
      · 顶层 `source_note`（来源脚注）
      · `[[brand]]` 的 `name` / `family` / `since` / `note`（面板标题、副标、支持起点、变体警示）
      · `[[blocked]]` 的 `brand` / `model` / `why`（不支持机型表三列）
    `models`（机型名）是专有名词、整体豁免，只有 `DEVICES_MODEL_OVERRIDES` 例外。

    ★ 为什么单开这一份（2026-10-10 d42 实测）：`/de/guides/esim-compatibility-check/`
      是本轮才建出的页型 —— 在此之前 devices 字段**没有任何德语页渲染**，
      所以 F（黑名单）与 G（只认「已进表的数据串」）同时为绿。页集一变，绿灯作废。
    """
    d = tomllib.loads((DATA / "devices.toml").read_text(encoding="utf-8"))
    out: set[str] = set()
    sn = d.get("source_note")
    if isinstance(sn, str) and sn.strip():
        out.add(sn)
    for b in d.get("brand", []):
        for fld in ("name", "family", "since", "note"):
            v = b.get(fld)
            if isinstance(v, str) and v.strip():
                out.add(v)
    for bl in d.get("blocked", []):
        for fld in ("brand", "model", "why"):
            v = bl.get(fld)
            if isinstance(v, str) and v.strip():
                out.add(v)
    # 覆盖项必须真的在数据里 —— 否则它就是另一种「死条目」
    all_models = {m for b in d.get("brand", []) for m in b.get("models", [])}
    missing = DEVICES_MODEL_OVERRIDES - all_models
    if missing:
        fail(f"D devices 覆盖项在数据里不存在（死条目）: {sorted(missing)}")
    return out | set(DEVICES_MODEL_OVERRIDES)


def load_info_strings() -> set:'''
E3_MARK = "def load_device_texts() -> set[str]:"

E4_OLD = """        self.quirks = load_quirks()
        self.info = load_info_strings()
"""
E4_NEW = """        self.quirks = load_quirks()
        self.info = load_info_strings()
        self.devices = load_device_texts()
"""
E4_MARK = "self.devices = load_device_texts()"

E5_OLD = """        for v in set(self.fup) | self.promos | self.info | self.quirks:
"""
E5_NEW = """        for v in set(self.fup) | self.promos | self.info | self.quirks | self.devices:
"""
E5_MARK = "| self.quirks | self.devices:"

E6A_OLD = """    have = set(ctx.fup) | ctx.promos | ctx.info | ctx.quirks
"""
E6A_NEW = """    have = set(ctx.fup) | ctx.promos | ctx.info | ctx.quirks | ctx.devices
"""
E6A_MARK = "ctx.quirks | ctx.devices\n"

E6B_OLD = """            f" + info.support/refund {len(ctx.info)} + quirks {len(ctx.quirks)} = {len(have)} 条）"
"""
E6B_NEW = """            f" + info.support/refund {len(ctx.info)} + quirks {len(ctx.quirks)}"
            f" + devices {len(ctx.devices)} = {len(have)} 条）"
"""
E6B_MARK = "f\" + devices {len(ctx.devices)} = {len(have)} 条）\""

E7_OLD = """    expect(any("D 数据串缺德语条目" in p for p in props), "反例：info.support/refund 缺德语条目被抓住")
    expect(any("D 死条目" in p for p in props), "反例：info 死条目被抓住")
"""
E7_NEW = """    expect(any("D 数据串缺德语条目" in p for p in props), "反例：info.support/refund 缺德语条目被抓住")
    expect(any("D 死条目" in p for p in props), "反例：info 死条目被抓住")

    # D 段第五来源（devices 设备表）—— 同样两个方向都要证伪。
    # 素材刻意取一条 **F 看不见**的（不含 F 词表任一词），否则 F 已经能抓，
    # 这条反例无法证明 D 的覆盖面真的扩大了。
    d0 = next(
        (
            s
            for s in sorted(ctx.devices)
            if len(s) > 24
            and not any(re.search(r"\\b%s\\b" % re.escape(w), s) for w in F_FORBIDDEN_WORDS)
        ),
        "",
    )
    expect(bool(d0), f"D devices 素材：找到一条 F 看不见的设备文本 {d0[:44]!r}")
    save_d = problems
    keep_d = ctx.devices
    props = []
    problems = []
    ctx.de_strings = {k: v for k, v in keep.items() if k != d0}
    ctx.devices = {d0}
    check_strings(ctx)
    props += list(problems)
    problems = []
    ctx.de_strings = dict(keep)
    ctx.de_strings["Etwas voellig anderes"] = "x"
    ctx.devices = {d0}
    check_strings(ctx)
    props += list(problems)
    problems = save_d
    ctx.de_strings = keep
    ctx.devices = keep_d
    expect(any("D 数据串缺德语条目" in p for p in props), "反例：devices 缺德语条目被抓住")
    expect(any("D 死条目" in p for p in props), "反例：devices 死条目被抓住")
"""
E7_MARK = '"反例：devices 缺德语条目被抓住"'

EDITS = [
    ("判据 D docstring", E1_OLD, E1_NEW, E1_MARK),
    ("判据 G docstring", E2_OLD, E2_NEW, E2_MARK),
    ("load_device_texts()", E3_OLD, E3_NEW, E3_MARK),
    ("Ctx.devices", E4_OLD, E4_NEW, E4_MARK),
    ("english_data_texts()", E5_OLD, E5_NEW, E5_MARK),
    ("check_strings have", E6A_OLD, E6A_NEW, E6A_MARK),
    ("check_strings info", E6B_OLD, E6B_NEW, E6B_MARK),
    ("selftest 反例", E7_OLD, E7_NEW, E7_MARK),
]


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry", action="store_true")
    args = ap.parse_args()

    b = TARGET.read_bytes()
    if b.count(b"\r\n"):
        print("FAIL 目标文件含 CRLF")
        return 1
    raw = b.decode("utf-8")
    before = len(b)

    fails: list[str] = []
    applied = skipped = 0
    for name, old, new, mark in EDITS:
        if mark in raw:
            skipped += 1
            continue
        c = raw.count(old)
        if c != 1:
            fails.append(f"{name}: 锚点命中 {c} 次（期望 1）")
            continue
        raw = raw.replace(old, new, 1)
        applied += 1
    if fails:
        print("\n".join("FAIL " + f for f in fails))
        return 1

    if applied:
        try:
            ast.parse(raw)
        except SyntaxError as e:
            print(f"FAIL 改后语法错误: {e}")
            return 1

    print(f"编辑：已应用 {applied} 处 / 已存在跳过 {skipped} 处 / 共 {len(EDITS)} 处")
    if args.dry:
        print("（--dry：未写盘）")
        return 0
    if not applied:
        print("无需写盘")
        return 0

    TARGET.write_bytes(raw.encode("utf-8"))
    b2 = TARGET.read_bytes()
    crlf = b2.count(b"\r\n")
    print(f"verify_de_text.py: {before} → {len(b2)} bytes / CRLF={crlf}")
    ast.parse(b2.decode("utf-8"))
    print("语法 OK")
    return 0


if __name__ == "__main__":
    sys.exit(main())
