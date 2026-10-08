#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""跨页 boilerplate 普查器 —— 句子级同质化度量（2026-10-07 第四十六轮）。

── 为什么要有它 ────────────────────────────────────────────────────────────
已有的「反同质化判据」是**块级 md5 去重 = N**（跨页模块抽文本算 md5，去重后必须等于页数）。
这条判据**是必要条件，不是充分条件** —— 一个区块只要含**一个**页内专属数字，
md5 就唯一，于是「95% 的句子逐字雷同、只换了一个价格」的区块照样全绿。

实证（奥地利 10 个品牌子页）：10 个区块的块级去重 **10/10 全唯一**，
但句子级有 **74% 的正文句子槽位**落在「≥8/10 页逐字相同」的句子上。
所以需要这把更细的尺子。

── 口径（重要，决定了数字可不可比）────────────────────────────────────────
1. 只取 **prose 标签**：`p / li / blockquote / figcaption`。
   表格单元格（`td`）与标签文字（列头、徽章）**不算** —— 它们本来就是数据/UI，
   算进来会把重复率虚高（本器首版就吃过这个亏：按「行」算 69%，按「句子槽位」算 74%，
   两个数不可混用；报告里必须写清用的是哪个）。
2. 跳过 `script / style / nav / footer / header / svg / noscript`。
3. 按 `[.!?]` 切句，丢弃 < 25 字符的碎片。
4. **两级归一化**：品牌名 → `@`；数字 → `#`。
   归一化后仍相同的句子 = 只换了品牌名/数字的模板句。
5. 指标 = **占用的槽位比例**，不是「不同句子数」：
       槽位 = 该分组全部页面的句子总数
       模板槽位 = Σ(该模板句出现的页数)
   「10 页里 33 条句子逐字相同」听上去不多，但它占用 330 个槽位。

── 判读 ────────────────────────────────────────────────────────────────────
    < 20%   健康
    20–40%  偏模板但可接受（同国家不同品牌本来就该共享国家级事实）
    > 40%   需动手：点名具体句子去差异化
本器只**报告**，不改文件、不失败（它是诊断工具，不是守卫）。

用法：
  python -X utf8 scripts/audit_boilerplate.py                      # 全页型
  python -X utf8 scripts/audit_boilerplate.py --type provider_sub
  python -X utf8 scripts/audit_boilerplate.py --type provider_sub --show 25
  python -X utf8 scripts/audit_boilerplate.py --group-by country   # 同国内跨品牌
"""
from __future__ import annotations

import argparse
import re
import sys
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PUB = ROOT / "public"

PROSE_RE = re.compile(r"<(p|li|blockquote|figcaption)\b[^>]*>(.*?)</\1>", re.S | re.I)
DROP_RE = re.compile(
    r"<(script|style|nav|footer|header|svg|noscript)\b.*?</\1>", re.S | re.I
)
NUM_RE = re.compile(r"\d+(?:\.\d+)?")
MIN_LEN = 25

# 页型 → public 下 glob；depth 用于剔掉同 glob 误命中的别的页型
PAGE_TYPES = {
    "provider_sub": ("compare/*/*/index.html", 4),
    "vs": ("compare/*-vs-*/index.html", 3),
    "country": ("compare/*/index.html", 3),
    "provider_hub": ("esim-providers/*/index.html", 3),
    "guides": ("guides/*/index.html", 3),
    "research": ("research/*/index.html", 3),
    "networks": ("networks/*/index.html", 3),
}


def brand_of(html: str) -> str:
    """该页自称的品牌名 —— 归一化成 @ 用。取不到就返回空串（不归一化）。"""
    m = re.search(r"<h1[^>]*>(.*?)</h1>", html, re.S)
    if not m:
        return ""
    h1 = re.sub(r"\s+", " ", re.sub(r"<[^>]+>", "", m.group(1))).strip()
    for pat in (r"Is (.+?) the right", r"(.+?)\s+\w+ eSIM", r"(.+?) eSIM",
                r"(.+?)\s+review", r"^(.+?)\s+[A-Z]"):
        m2 = re.match(pat, h1)
        if m2:
            cand = m2.group(1).strip()
            if 1 < len(cand) <= 24:
                return cand
    return ""


def sentences(html: str) -> list[str]:
    body = DROP_RE.sub("", html)
    out: list[str] = []
    for m in PROSE_RE.finditer(body):
        s = re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", m.group(2))).strip()
        if not s:
            continue
        for sent in re.split(r"(?<=[.!?])\s+", s):
            sent = sent.strip()
            if len(sent) >= MIN_LEN:
                out.append(sent)
    return out


def _names() -> list[str]:
    """归一化用的名字表：全部国家名 + 全部品牌名。

    ★ 2026-10-08 修订：此前只归一化「该页自己的品牌名」，国家名**完全不归一化**。
    后果 —— 同品牌跨国家的分组里，「...in Japan」与「...in Croatia」原文不同、
    被误判为「各页独立」，把 50 个国家页的共享率压到 54.5%（实际 86.8%）。
    同时，同组内若只有部分国名被硬编码归一化，各国口径还不一致
    （austria 独占 6 句 vs netherlands 独占 38 句），数字根本不可比。
    国名必须全量归一化。
    """
    ns: set[str] = set()
    cp = ROOT / "data" / "countries.toml"
    if cp.exists():
        try:
            import tomllib
            C = tomllib.loads(cp.read_text(encoding="utf-8"))
            for v in C.values():
                if not isinstance(v, dict):
                    continue
                if v.get("name"):
                    ns.add(str(v["name"]))
                sl = v.get("slug")
                if sl:
                    ns.add(str(sl))
                    ns.add(str(sl).replace("-", " ").title())
        except Exception:
            pass
    for f in (ROOT / "data" / "plans").glob("*.toml"):
        ns.add(f.stem)
        ns.add(f.stem.capitalize())
    return sorted((n for n in ns if len(n) > 2), key=len, reverse=True)


NAME_RE = re.compile("|".join(re.escape(n) for n in _names()), re.I)


def norm(s: str, brand: str) -> str:
    if brand:
        s = re.sub(r"(?i)" + re.escape(brand), "@", s)
    s = NAME_RE.sub("@", s)
    return NUM_RE.sub("#", s)


def collect(ptype: str, group_by: str):
    """→ { 分组名: { slug: [归一化后的句子, …] } }"""
    pattern, depth = PAGE_TYPES[ptype]
    groups: dict[str, dict[str, list[str]]] = defaultdict(dict)
    for f in sorted(PUB.glob(pattern)):
        rel = f.relative_to(PUB)
        if len(rel.parts) != depth:
            continue
        # compare/<x>/index.html 与 compare/<a>-vs-<b>/index.html 深度相同，靠名字剔掉后者
        if ptype == "country" and "-vs-" in rel.parts[1]:
            continue
        html = f.read_text(encoding="utf-8", errors="replace")
        brand = brand_of(html)
        sents = [norm(s, brand) for s in sentences(html)]
        if group_by == "country":
            g = rel.parts[1]
        elif group_by == "brand":
            g = rel.parts[depth - 2]
        else:
            g = "_all"
        groups[g][str(rel)] = sents
    return groups


def analyse(pages: dict[str, list[str]]):
    """★ 2026-10-08 修订：模板槽位改为「按出现次数」计（原为「按出现页数」计）。

    旧口径分子分母不对等：分母 slots 数的是**含页内重复**的句子总数，
    分子却把「出现在 N 页的某句」只记 N 次 —— 于是同一句话在一页里出现 3 次时，
    分母 +3、分子只 +1，**系统性低估**。
    实测 roamic 50 国子页：旧口径 73%，严格口径 86.8%（差 13.8 个点，
    全部来自 #reality / #fup / #faq 三区块的页内复述）。

    现改为自洽的「槽位视角」：分母 = Σ每页句子数，
    分子 = Σ每页中模板句的出现次数。
    另单独返回 dup_slots（同页内重复的句子数）——
    页内重复是独立问题，不混进跨页指标。
    """
    from collections import Counter as _C
    freq: dict[str, set[str]] = defaultdict(set)
    per_page: dict[str, _C] = {}
    slots = 0
    for slug, ss in pages.items():
        c = _C(ss)
        per_page[slug] = c
        slots += len(ss)
        for s in c:
            freq[s].add(slug)
    n = len(pages)
    thr = max(2, int(n * 0.8 + 0.5))
    boiler = {k: v for k, v in freq.items() if len(v) >= thr}
    bslots = sum(per_page[slug][k] for k, slugs in boiler.items() for slug in slugs)
    dup_slots = sum(len(ss) - len(per_page[slug]) for slug, ss in pages.items())
    pct = 100 * bslots / slots if slots else 0.0
    return dict(pages=n, slots=slots, thr=thr, boiler=boiler, bslots=bslots,
                pct=pct, dup_slots=dup_slots)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--type", default=None, choices=sorted(PAGE_TYPES))
    ap.add_argument("--group-by", default="all", choices=["all", "country", "brand"])
    ap.add_argument("--show", type=int, default=0)
    ap.add_argument("--min-pages", type=int, default=4)
    args = ap.parse_args()

    types = [args.type] if args.type else sorted(PAGE_TYPES)
    for t in types:
        groups = collect(t, args.group_by)
        if not groups:
            print(f"\n### {t}: public 下无产物（先 npm run build）")
            continue
        print(f"\n### {t}   分组 = {args.group_by}")
        print(f"{'分组':18} {'页数':>5} {'槽位':>7} {'模板槽位':>9} "
              f"{'占比':>7} {'页内重复':>8}  判读")
        for g, pages in sorted(groups.items()):
            if len(pages) < args.min_pages:
                continue
            r = analyse(pages)
            verdict = ("✅ 健康" if r["pct"] < 20
                       else "⚠ 偏模板" if r["pct"] <= 40
                       else "❌ 需动手")
            print(f"{g:18} {r['pages']:>5} {r['slots']:>7} {r['bslots']:>9} "
                  f"{r['pct']:>6.0f}% {r['dup_slots']:>8}  {verdict}")
            if args.show:
                top = sorted(r["boiler"].items(), key=lambda kv: -len(kv[1]))[:args.show]
                for k, v in top:
                    print(f"      {len(v):>3}/{r['pages']}  {k[:110]}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
