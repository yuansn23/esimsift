# -*- coding: utf-8 -*-
"""英语 compare 正文事实槽位对账（只读）。

背景：`content/en/compare/*.md` 正文里的数字来自「8 品牌时期」的手写快照，
而同页 front matter 的 `seo.description` 由 `regen_meta_brand.py` 实时现算
⇒ 同一页两处数字互相打脸（读者与 Google 都能看见）。

★★ 单一真源（红线 8）：槽位抽取**不许在本文件里重抄正则**，一律委托
  `scripts/_en_compare_fix.py :: collect_stale` → `scripts/_en_compare_lib.py`。
  本文件首版把正则内联抄了第二份，且抄漏两处：
    ① `RE_ENTRY` 的 `(?! a day)` 负向断言 → 把 12 页的**盈亏平衡句**
       （"…only makes sense past about 3.6GB a day"）误当入口槽位；
    ② `tech_phrase` 的 `{4G}` → `all 4G` 分支 → 把 FJ 正确的「all 4G」判成 mix。
  合计 13 处假红，而同期 `_en_compare_fix.py --verify` 报 0 处真实过期。
  第三类同源问题（japan，编辑性长文）由修复器早已用 `SKIP` 排除，本文件
  现在也共用同一份 `SKIP`，并在报告里**显式列出**例外页而非静默丢弃。

输出：
  - 每页每个**确实过期**的槽位 (正文值, 现算值)
  - 汇总：哪些槽位过期、共几页
  - 槽位覆盖率：哪些页压根没用某个句式（**不是缺陷**，只是这些页的该项事实
    由别的槽位承载，例如没用「$X/GB ⇒ 能跑 N GB」句式的页，其入口事实由
    `entry_price` / `entry_size` / `ratio` 承载）

用法：
  python -X utf8 scripts/_en_compare_stale_audit.py
  python -X utf8 scripts/_en_compare_stale_audit.py --json out.json
  python -X utf8 scripts/_en_compare_stale_audit.py --selftest
"""
from __future__ import annotations

import argparse
import importlib.util
import json
import pathlib
import re

ROOT = pathlib.Path(__file__).resolve().parents[1]
EN = ROOT / "content" / "en" / "compare"


def _load(mod_name: str, rel: str):
    spec = importlib.util.spec_from_file_location(mod_name, ROOT / rel)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)  # type: ignore[union-attr]
    return mod


_facts = _load("_facts", "scripts/_compare_de_facts.py")
_fix = _load("_fix", "scripts/_en_compare_fix.py")
L = _fix.L
# 例外页集与修复器共用同一份（单一真源）：japan 整页是编辑性长文，其数字是
# 桶价区间 / 日价 flat / 单 GB 价 / 档位价，不属标准槽位词汇 ⇒ 只列不改、需人工核对。
SKIP = _fix.SKIP


def body_of(text: str) -> str:
    parts = text.split("---\n", 2)
    return parts[2].strip() if len(parts) > 2 else ""


def audit() -> dict:
    """逐页对账。槽位抽取复用修复器（单一真源），本文件只做汇总与呈现。"""
    out: dict[str, dict] = {}
    for f in sorted(EN.glob("*.md")):
        if f.stem in SKIP or "-vs-" in f.stem:
            continue
        parts = f.read_text(encoding="utf-8").split("---\n", 2)
        if len(parts) < 3:
            continue
        iso_m = re.search(r"^iso:\s*(\w+)", parts[1], re.M)
        if not iso_m:
            continue
        iso = iso_m.group(1)
        if not _facts.collect(iso):
            continue
        lv = L.live_values(iso)
        lv["iso"] = iso
        bad = _fix.collect_stale(f.stem, body_of(f.read_text(encoding="utf-8")), lv)
        if bad:
            out[f.stem] = {
                "iso": iso,
                "slug": f.stem,
                "stale": sorted({b[0] for b in bad}),
                "slots": {b[0]: [b[1], b[2]] for b in bad},
            }
    return out


def coverage() -> None:
    """槽位覆盖率（报告项，非判红项）：统计哪些页没用某个句式。"""
    groups: dict[str, list[str]] = {
        "T": L.RE_T,
        "U": L.RE_U,
        "rate": [L.RE_RATE_GB, L.RE_RATE_GIG],
        "entry": [L.RE_ENTRY],
        "daily": L.RE_DAILY,
        "breakeven": L.RE_BREAKEVEN,
    }
    miss: dict[str, list[str]] = {k: [] for k in groups}
    n = 0
    for f in sorted(EN.glob("*.md")):
        if f.stem in SKIP or "-vs-" in f.stem:
            continue
        body = body_of(f.read_text(encoding="utf-8"))
        n += 1
        for k, pats in groups.items():
            if not any(re.search(p, body) for p in pats):
                miss[k].append(f.stem)
    print(f"\n== 槽位覆盖率（共 {n} 页；下面只说明「该句式未被使用」，不是缺陷）==")
    for k, v in miss.items():
        print(f"  {k:10} " + ("✔ 全覆盖" if not v else f"· 未使用 {len(v)}: {v}"))


# ── 自检：两侧都要证（正例不误伤 + 反例会判红）──
def selftest() -> int:
    lv = {
        "iso": "XX", "T": "100", "U": "50", "rate": "1.00",
        "entry_mb": "1024", "entry_gb": "1.0", "ratio": "2.0",
        "daily": "1.50", "breakeven": "2.0",
        "speed_min": "10", "speed_top": "100", "tech": "all 4G",
        "entry_price": "1.00", "plan_entry": "X 1GB / 7 Days",
        "entry_brand": "Roamic", "best_rate_brand": "Roamic",
        "unlimited_brand": "Roamic",
    }
    n_ok = n_bad = 0

    def expect(name: str, got, want_present: bool) -> None:
        nonlocal n_ok, n_bad
        if bool(got) == want_present:
            n_ok += 1
            print(f"  ok   {name}")
        else:
            n_bad += 1
            print(f"  ✗    {name}（got={got!r}，want_present={want_present}）")

    def slots(body: str) -> list[str]:
        return [s for s, _, _ in _fix.collect_stale("x", body, lv)]

    # ── ① 首版假红类 A：盈亏平衡句被当成入口槽位 ──
    b = "Since buckets cost $0.64/GB, the daily plan only makes sense past about 3.6GB a day."
    expect("正例：盈亏平衡句不产生 entry_* 槽位",
           [s for s in slots(b) if s.startswith("entry_")], False)
    expect("正例：上句的 3.6GB 被 breakeven 槽位正确接收", "breakeven" in slots(b), True)

    # ── ② 真入口槽位：写对不判红 / 写错必判红 ──
    good = "Put $1.00 through the $1.00/GB rate and you would clear about 1.0GB."
    wrong = "Put $1.00 through the $1.00/GB rate and you would clear about 9.9GB."
    expect("正例：entry_gb 写对不判红", "entry_gb" in slots(good), False)
    expect("反例：entry_gb 写错判红", "entry_gb" in slots(wrong), True)

    # ── ③ 首版假红类 B：{4G} 必须映射成 all 4G，不能落进 mix 分支 ──
    expect("正例：全 4G 写 all 4G 不判红", "tech" in slots("Local networks run all 4G."), False)
    expect("反例：全 4G 写成 all 5G 判红", "tech" in slots("Local networks run all 5G."), True)

    # ── ④ 首版假红类 A 的孪生：`…MB a day` 同样不得当入口 ──
    b2 = "Buckets win until you need about 800MB a day on the road."
    expect("正例：`about 800MB a day` 不产生 entry_mb 槽位",
           [s for s in slots(b2) if s.startswith("entry_")], False)

    # ── ⑤ 与修复器同源：两者对同一段文本的判定必须一致 ──
    expect("一致性：本文件与 _en_compare_fix 结论同源（同一函数）",
           _fix.collect_stale("x", wrong, lv) == _fix.collect_stale("x", wrong, lv), True)

    print(f"\n[selftest] 通过 {n_ok} / 失败 {n_bad}")
    return 1 if n_bad else 0


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--json")
    ap.add_argument("--selftest", action="store_true")
    args = ap.parse_args()

    if args.selftest:
        return selftest()

    data = audit()
    skipped = sorted(f.stem for f in EN.glob("*.md")
                     if f.stem in SKIP and f.stem not in ("_index", "matchups") and "-vs-" not in f.stem)
    total_pages = sum(1 for f in EN.glob("*.md")
                      if f.stem not in SKIP and "-vs-" not in f.stem)
    print(f"英语 compare 国家页 {total_pages} 页；含过期槽位的 {len(data)} 页\n")
    slotcnt: dict[str, int] = {}
    for slug, rec in data.items():
        print(f"── {slug:24} stale={','.join(rec['stale'])}")
        for k in rec["stale"]:
            got, want = rec["slots"][k]
            print(f"      {k:16} 正文={got!r:28} 现算={want!r}")
            slotcnt[k] = slotcnt.get(k, 0) + 1
    print("\n== 过期槽位汇总 ==")
    if not slotcnt:
        print("  （无）")
    for k, v in sorted(slotcnt.items(), key=lambda x: -x[1]):
        print(f"  {k:18} {v} 页")
    if skipped:
        print(f"\n== 例外页（与修复器共用 SKIP，整页数字属编辑性口径，需人工核对）==")
        for s in skipped:
            print(f"  · {s}")
    coverage()

    if args.json:
        pathlib.Path(args.json).write_text(
            json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
        print(f"\n[json] → {args.json}")
    return 1 if data else 0


if __name__ == "__main__":
    raise SystemExit(main())
