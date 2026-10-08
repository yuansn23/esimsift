# -*- coding: utf-8 -*-
"""诚实口径的重复度量：不做数字/国名归一化，直接比「渲染后的文本」。

动机：audit_boilerplate.py 会把数字→#、国名/品牌名→@ 再比骨架，
于是「Entry price is $2.00 against the country floor of $0.51」(SG)
与「Entry price is $2.10 against the country floor of $0.95」(JP) 被算成同一句。
但 Google 看到的是渲染后的文本 —— 那是两句不同的话、两个不同的事实。

本脚本回答三个问题：
  1. 真正「逐字相同」的句子占多少（出现在 >=80% 页面的句子数 / 总句数）？
  2. 这些逐字相同的句子里，多少是「携带本页数据的」（含数字或国名/品牌名）？
     —— 携带数据的句子逐字相同 = 说明该页数据恰好一样，不是模板。
  3. 剩下「不携带任何本页变量」的逐字重复句，构成是什么（分类列举）？
"""
import re, html, io, pathlib, collections, sys, json

ROOT = pathlib.Path("public")
DROP = re.compile(r"<(script|style|nav|footer|header|svg|noscript)\b.*?</\1>", re.S | re.I)
PROSE = re.compile(r"<(p|li|blockquote|figcaption)\b[^>]*>(.*?)</\1>", re.S | re.I)
TAG = re.compile(r"<[^>]+>")

countries = {}
for line in io.open("data/countries.toml", encoding="utf-8"):
    m = re.match(r'\s*name\s*=\s*"([^"]+)"', line)
    if m:
        countries[m.group(1)] = True
provs = {}
for line in io.open("data/providers.toml", encoding="utf-8"):
    m = re.match(r'\[([a-z0-9_]+)(?:\.([a-z0-9_]+))?\]\s*$', line.strip())
    if m:
        provs[m.group(1)] = True

PAGE = re.compile(r"public/compare/([^/]+)/([^/]+)/index\.html$")


def sents(path):
    h = DROP.sub(" ", path.read_text(encoding="utf-8"))
    out = []
    for m in PROSE.finditer(h):
        t = html.unescape(TAG.sub(" ", m.group(2)))
        t = re.sub(r"\s+", " ", t).strip()
        for s in re.split(r"(?<=[.!?])\s+", t):
            s = s.strip()
            if len(s) >= 25:
                out.append(s)
    return out


def group_brand(brand):
    pages = []
    for p in sorted(ROOT.glob(f"compare/*/{brand}/index.html")):
        pages.append(p)
    return pages


VAR_RE = re.compile(r"\$?\d|" + "|".join(re.escape(c) for c in sorted(countries, key=len, reverse=True))[:0] or r"\d")


def has_page_var(s):
    if re.search(r"\d", s):
        return True
    for c in countries:
        if c in s:
            return True
    for k in provs:
        if len(k) >= 4 and k in s.lower():
            return True
    return False


print("=" * 92)
print("品牌子页：逐字重复（不做任何归一化）")
print("=" * 92)
print(f"{'品牌':<10}{'页数':>5}{'总句槽':>8}{'唯一句':>8}{'逐字重复句型':>13}{'重复槽位':>10}{'占比':>7}{'其中带数据':>11}{'纯模板':>8}")
for brand in ["airalo", "alosim", "holafly", "jetpac", "nomad", "roami", "roamic", "saily", "ubigi", "yesim"]:
    pages = group_brand(brand)
    if len(pages) < 4:
        continue
    cnt = collections.Counter()
    per = []
    for p in pages:
        ss = sents(p)
        per.append(ss)
        for x in set(ss):
            cnt[x] += 1
    total = sum(len(x) for x in per)
    thr = 0.8 * len(pages)
    rep = {s: n for s, n in cnt.items() if n >= thr}
    rep_slots = sum(n for n in rep.values())
    withvar = [s for s in rep if has_page_var(s)]
    print(f"{brand:<10}{len(pages):>5}{total:>8}{len(cnt):>8}{len(rep):>13}{rep_slots:>10}"
          f"{rep_slots/total*100:>6.1f}%{len(withvar):>11}{len(rep)-len(withvar):>8}")

print()
print("=" * 92)
print("roamic：50 页里逐字重复且【不含任何本页变量】的句子（= 真正的模板文字）")
print("=" * 92)
pages = group_brand("roamic")
cnt = collections.Counter()
per = []
for p in pages:
    ss = sents(p)
    per.append(ss)
    for x in set(ss):
        cnt[x] += 1
total = sum(len(x) for x in per)
thr = 0.8 * len(pages)
pure = [(s, n) for s, n in cnt.items() if n >= thr and not has_page_var(s)]
pure.sort(key=lambda x: -x[1])
print(f"（总句槽 {total}，逐字重复且无变量的句型 {len(pure)} 种、占用 {sum(n for _, n in pure)} 槽"
      f" = {sum(n for _, n in pure)/total*100:.1f}%）\n")
for s, n in pure:
    print(f"  {n:>3}/50  {s[:150]}")
