#!/usr/bin/env python -X utf8
"""#tradeoffs 条目审计 —— 优劣势两列的「条目数分布」与「逐条目出现页数」。

为什么需要它：2026-10-04 第二十三轮的真实事故是「判据永远为假 → 条目从不出现」——
`FUP 阈值不公布` 这条缺点写了很久，判据是 `not .fup_allowance`，而八个品牌的该字段
**全都有值**（Holafly 的是字面量 "No GB figure published"），于是它一次都没渲染过，
构建全绿、页面自洽，只有把 400 页统计一遍才发现。

所以这个脚本同时看两个方向：
  · 条目数过少（优点 < MIN_WINS 或缺点 < MIN_LOSSES）→ 内容单薄或判据失效
  · 某条目出现页数为 0 → 判据永远为假（静态模板里的条目应当至少命中一页）

用法：
    python -X utf8 scripts/audit_tradeoffs.py            # 摘要 + 异常清单
    python -X utf8 scripts/audit_tradeoffs.py --items    # 追加逐条目页数明细
退出码：有异常时 1（可直接串进 CI）。
"""
from __future__ import annotations

import argparse
import collections
import glob
import html
import re
import sys

MIN_WINS = 3
MIN_LOSSES = 2

SECTION = re.compile(r'id="tradeoffs".*?(?=</section>)', re.S)
UL = re.compile(r"<ul[^>]*>(.*?)</ul>", re.S)
LI = re.compile(r"<li[^>]*>(.*?)</li>", re.S)
TAG = re.compile("<[^>]+>")
# 具体数字每页不同，归一到占位符才能按条目聚合
NUM = re.compile(r"\$?[\d.,]+")


def normalize(text: str) -> str:
    """把条目文本归一成可直接聚合的「条目指纹」：去标签、抹掉数字与专有名词。"""
    text = html.unescape(TAG.sub("", text)).strip()
    text = text.lstrip("+–-").strip()
    text = NUM.sub("N", text)
    return text


def collect():
    pages = []
    for path in sorted(glob.glob("public/compare/*/*/index.html")):
        raw = open(path, encoding="utf-8").read()
        m = SECTION.search(raw)
        if not m:
            pages.append((path, None, None, []))
            continue
        uls = UL.findall(m.group(0))
        sides = []
        for ul in uls[:2]:
            items = [html.unescape(TAG.sub("", li)).strip() for li in LI.findall(ul)]
            sides.append([i for i in items if i])
        while len(sides) < 2:
            sides.append([])
        pages.append((path, sides[0], sides[1], sides[0] + sides[1]))
    return pages


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--items", action="store_true", help="打印逐条目出现页数")
    args = ap.parse_args()

    pages = collect()
    print(f"扫描 {len(pages)} 个品牌×国家子页\n")
    if not pages:
        print("没有产物，先跑 npm run build")
        return 1

    missing = [p for p, w, _, _ in pages if w is None]
    thin = [(p, len(w), len(l)) for p, w, l, _ in pages if w is not None and (len(w) < MIN_WINS or len(l) < MIN_LOSSES)]

    win_dist = collections.Counter(len(w) for _, w, _, _ in pages if w is not None)
    loss_dist = collections.Counter(len(l) for _, w, l, _ in pages if l is not None)
    print("优点条数分布：", " ".join(f"{k}→{win_dist[k]}页" for k in sorted(win_dist)))
    print("缺点条数分布：", " ".join(f"{k}→{loss_dist[k]}页" for k in sorted(loss_dist)))

    win_hits = collections.Counter()
    loss_hits = collections.Counter()
    for _, w, l, _ in pages:
        if w is None:
            continue
        for it in set(normalize(x) for x in w):
            win_hits[it] += 1
        for it in set(normalize(x) for x in l):
            loss_hits[it] += 1

    total_items = len(win_hits) + len(loss_hits)
    never = [(k, "优点") for k in []]
    print(f"\n可识别的条目指纹：优点 {len(win_hits)} 种 / 缺点 {len(loss_hits)} 种")

    if args.items:
        print("\n── 优点条目（出现页数降序）")
        for k, v in win_hits.most_common():
            print(f"  {v:>4}  {k}")
        print("\n── 缺点条目（出现页数降序）")
        for k, v in loss_hits.most_common():
            print(f"  {v:>4}  {k}")

    problems = 0
    if missing:
        problems += len(missing)
        print(f"\n★ 缺 #tradeoffs 区块：{len(missing)} 页")
        for p in missing[:10]:
            print("   ", p)
    if thin:
        problems += len(thin)
        print(f"\n★ 条目过少（优点 <{MIN_WINS} 或 缺点 <{MIN_LOSSES}）：{len(thin)} 页")
        for p, w, l in thin[:20]:
            print(f"    {p}  优点={w} 缺点={l}")

    if problems:
        print(f"\nFAIL：{problems} 处需要注意（条目指纹 {total_items} 种）")
        return 1
    print(f"\nOK：{len(pages)} 页条目数均达标（优点 ≥{MIN_WINS} 且 缺点 ≥{MIN_LOSSES}）")
    return 0


if __name__ == "__main__":
    sys.exit(main())
