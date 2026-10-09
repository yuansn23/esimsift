# -*- coding: utf-8 -*-
"""Google 通道词表分类 / 归属页型 / 站内对账（2026-10-08 第五十三轮）

复用 kw_classify.py 的分类规则（动态 import，不复制、不改动那个文件）——
分类规则是项目资产，只能有一份。

输入：docs/keywords/google/kw-google-scored.csv
输出：docs/keywords/google/kw-google-collected.csv（主交付物）
"""
import csv
import importlib.util
import json
import pathlib
import re
import statistics as st

ROOT = pathlib.Path(__file__).resolve().parent.parent
KW = ROOT / "docs" / "keywords"
G = KW / "google"
MATRIX = pathlib.Path(r"C:\Users\Administrator\WorkBuddy\2026-09-30-13-09-50"
                      r"\esim-compare-blueprint\keyword-matrix.csv")

spec = importlib.util.spec_from_file_location("kc", str(ROOT / "scripts" / "kw_classify.py"))
kc = importlib.util.module_from_spec(spec)
spec.loader.exec_module(kc)

countries = kc.load_countries()
live = set(json.loads((KW / "live-urls.json").read_text(encoding="utf-8")))
print(f"站内 URL {len(live)}；国家 {len(countries)}")

rows = list(csv.DictReader((G / "kw-google-scored.csv").open(encoding="utf-8")))
print(f"读入 Google 词 {len(rows)}")

keep = [r for r in rows if re.search(r"\b(esim|e sim|sim)\b", r["keyword"])]
print(f"含 esim/sim 的 {len(keep)}")

old = set()
if MATRIX.is_file():
    for r in csv.DictReader(MATRIX.open(encoding="utf-8-sig")):
        old.add(kc.norm(r["长尾关键词"]))
    print(f"旧矩阵词库 {len(old)}")

out = []
for r in keep:
    kw = r["keyword"]
    typ, cts, brs, regs, cities = kc.classify(kw, countries)
    url, status, ptype = kc.route(kw, typ, cts, brs, regs, live)
    out.append({
        "keyword": kw,
        "词型": typ,
        "综合分": float(r["综合分"]),
        "补全分": float(r["补全分"]),
        "google指数": r["google指数"],
        "上升信号": r["上升信号"],
        "证据": r["证据"],
        "sources": int(r["sources"]),
        "中位位次": float(r["中位位次"]),
        "top3次数": int(r["top3次数"]),
        "覆盖国数": int(r["覆盖国数"]),
        "markets": r["markets"],
        "best_seed": r["best_seed"],
        "归属页型": ptype,
        "归属URL": url,
        "站内现状": status,
        "国家": ",".join(c["iso"] for c in cts),
        "国家slug": ",".join(c["slug"] for c in cts),
        "品牌": ",".join(brs),
        "在旧词库": "是" if kc.norm(kw) in old else "否",
    })

out.sort(key=lambda x: -x["综合分"])
cols = list(out[0].keys())
p = G / "kw-google-collected.csv"
with p.open("w", encoding="utf-8", newline="") as f:
    w = csv.DictWriter(f, fieldnames=cols)
    w.writeheader()
    w.writerows(out)
print(f"\n主交付物 -> {p.relative_to(ROOT)}（{len(out)} 词）")

print("\n=== 词型分布（词数 / 综合分中位）===")
by = {}
for o in out:
    by.setdefault(o["词型"], []).append(o["综合分"])
for k, v in sorted(by.items(), key=lambda x: -len(x[1])):
    print(f"  {len(v):5d}  中位{st.median(v):5.1f}  {k}")

print("\n=== 站内现状 ===")
stc = {}
for o in out:
    stc[o["站内现状"]] = stc.get(o["站内现状"], 0) + 1
for k, v in sorted(stc.items(), key=lambda x: -x[1]):
    print(f"  {v:5d}  {k}")

print("\n=== 有 Trends 指数的词 ===")
tr = [o for o in out if o["google指数"] != ""]
print(f"  {len(tr)} 个；Top 20：")
for o in tr[:20]:
    print(f'   指数{o["google指数"]:>4}  综合{o["综合分"]:5.1f}  {o["keyword"]}')

print("\n=== 综合分 Top 30（全体）===")
for o in out[:30]:
    gi = f'{o["google指数"]:>4}' if o["google指数"] != "" else "   -"
    print(f'  {o["综合分"]:5.1f}  指数{gi}  {o["sources"]:3d}源  '
          f'{o["词型"]:12s} {o["keyword"]}')
