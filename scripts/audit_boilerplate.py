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


def norm(s: str, brand: str) -> str:
    if brand:
        s = re.sub(r"(?i)" + re.escape(brand), "@", s)
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
    freq: dict[str, set[str]] = defaultdict(set)
    slots = 0
    for slug, ss in pages.items():
        seen = set()
        for s in ss:
            slots += 1
            if s not in seen:
                seen.add(s)
                freq[s].add(slug)
    n = len(pages)
    thr = max(2, int(n * 0.8 + 0.5))
    boiler = {k: v for k, v in freq.items() if len(v) >= thr}
    bslots = sum(len(v) for v in boiler.values())
    pct = 100 * bslots / slots if slots else 0.0
    return dict(pages=n, slots=slots, thr=thr, boiler=boiler, bslots=bslots, pct=pct)


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
        print(f"{'分组':18} {'页数':>5} {'槽位':>7} {'模板槽位':>9} {'占比':>7}  判读")
        for g, pages in sorted(groups.items()):
            if len(pages) < args.min_pages:
                continue
            r = analyse(pages)
            verdict = ("✅ 健康" if r["pct"] < 20
                       else "⚠ 偏模板" if r["pct"] <= 40
                       else "❌ 需动手")
            print(f"{g:18} {r['pages']:>5} {r['slots']:>7} {r['bslots']:>9} "
                  f"{r['pct']:>6.0f}%  {verdict}")
            if args.show:
                top = sorted(r["boiler"].items(), key=lambda kv: -len(kv[1]))[:args.show]
                for k, v in top:
                    print(f"      {len(v):>3}/{r['pages']}  {k[:110]}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
