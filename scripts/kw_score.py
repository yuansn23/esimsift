# -*- coding: utf-8 -*-
"""补全词需求强度打分（2026-10-08）—— 从 raw_autocomplete*.json 离线重算，不联网

为什么要把打分单独拿出来：
  1. **必须剔除「种子回显」** —— Bing 的补全响应第 0 位永远是查询本身。
     不剔除的话，任何被我当种子探过的词都会白拿一个 rank 1。
     （实测剔除 891 条）
  2. **best_rank 单值太脆** —— 一个通用热门块里的 rank 1 就能把它顶到榜首。
     改用 **中位位次**（跨所有把它带出的种子）+ **top3 命中数**，抗单点噪声。
  3. **sources 有天花板** —— Bing 会给几乎所有 eSIM 查询注入同一段通用补全块
     （实测「buy esim for dubai」被 57 个种子带出），所以 sources 只能当
     「广度」的粗信号，不能单独定序。
  4. **位次要夹取** —— 补全列表可能长于 12 条，中位位次 > 13 时会算出负分。

三维口径（0-100）：
  需求分 = 100 × (0.4×min(sources/40,1) + 0.4×max(0,(13-中位位次)/12) + 0.2×min(top3/8,1))
  - 广度 sources   ：跨语境普遍性
  - 深度 中位位次   ：在该语境下「是不是人们接下来要打的词」
  - top3 命中率    ：稳定站在前列的种子占比

★ 判别「通用注入词」vs「真·逐国词」的关键字段是 **覆盖国数**：
  覆盖国数 ≥ 40 且词里无国名 = 通用热门块注入（全局词的信号）；
  覆盖国数 ≤ 12 且中位位次 ≤ 3 = 真实的逐国需求（钱词）。

输出：docs/keywords/kw-scored.csv
"""
import glob
import json
import pathlib
import re
import statistics
from collections import defaultdict

ROOT = pathlib.Path(__file__).resolve().parent.parent
KW = ROOT / "docs" / "keywords"

# ---- 种子「语境域」词表：国名 + 短名 + 城市 + 区域 ----
def build_scope_tokens():
    txt = (ROOT / "data" / "countries.toml").read_text(encoding="utf-8")
    toks = set()
    for m in re.finditer(r'^name\s*=\s*"([^"]+)"', txt, re.M):
        toks.add(m.group(1).lower())
    toks |= {"usa", "us", "uk", "england", "uae", "dubai", "korea", "seoul",
             "macau", "macao", "taipei", "czech republic", "turkey", "istanbul",
             "holland", "amsterdam", "nz", "ksa", "viet nam", "bali", "bangkok",
             "cancun", "manila", "prague", "riyadh", "cape town",
             "europe", "asia", "africa", "middle east", "caribbean", "oceania",
             "north america", "south america", "latin america", "international",
             "global", "worldwide", "abroad", "overseas"}
    return toks


SCOPE_TOKENS = build_scope_tokens()

# 读取所有非冒烟的原始文件（第 1 轮 + 别名轮）
files = [f for f in sorted(glob.glob(str(KW / "raw_autocomplete*.json")))
         if ".smoke" not in f]
print(f"读取原始文件 {len(files)} 个：")
for f in files:
    d = json.loads(pathlib.Path(f).read_text(encoding="utf-8"))
    print(f"  {pathlib.Path(f).name}  pass={d.get('pass','?')}  "
          f"种子 {d['seeds_ok']}/{d['seeds_total']}  建议 {len(d['suggestions'])}")

agg = {}
echo_drop = 0
seed_total = 0
for f in files:
    d = json.loads(pathlib.Path(f).read_text(encoding="utf-8"))
    for key, sugg in d["suggestions"].items():
        seed_total += 1
        seed, mkt = key.rsplit("|", 1)
        seed = seed.strip().lower()
        scopes = {t for t in SCOPE_TOKENS if t in seed}
        for i, s in enumerate(sugg):
            s = s.strip().lower()
            if not s or len(s) < 5:
                continue
            if s == seed and i == 0:          # ★ 剔除种子回显
                echo_drop += 1
                continue
            r = agg.setdefault(s, {"kw": s, "ranks": [], "seeds": set(),
                                   "scopes": set(), "markets": set(),
                                   "best_seed": None})
            r["ranks"].append(i + 1)
            r["seeds"].add(seed)
            r["scopes"] |= scopes
            r["markets"].add(mkt)
            if r["best_seed"] is None or i + 1 < min(r["ranks"][:-1], default=99):
                r["best_seed"] = seed

rows = []
for r in agg.values():
    n = len(r["seeds"])
    med = statistics.median(r["ranks"])
    top3 = sum(1 for x in r["ranks"] if x <= 3)
    s_breadth = min(n / 40.0, 1.0)
    s_depth = max(0.0, (13.0 - med) / 12.0)     # ★ 夹取，别出负分
    s_top3 = min(top3 / 8.0, 1.0)
    rows.append({
        "keyword": r["kw"],
        "需求分": round(100 * (0.4 * s_breadth + 0.4 * s_depth + 0.2 * s_top3), 1),
        "sources": n,
        "中位位次": med,
        "top3次数": top3,
        "best_rank": min(r["ranks"]),
        "best_seed": r["best_seed"],
        "覆盖国数": len(r["scopes"]),
        "markets": ",".join(sorted(r["markets"])),
    })

rows.sort(key=lambda x: (-x["需求分"], -x["sources"], x["keyword"]))
out = KW / "kw-scored.csv"
import csv
with out.open("w", encoding="utf-8", newline="") as f:
    w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
    w.writeheader()
    w.writerows(rows)

print(f"\n种子总数 {seed_total}；剔除种子回显 {echo_drop}；唯一补全词 {len(rows)}")
print(f"-> {out.relative_to(ROOT)}")
print("\n=== 需求分 Top 35 ===")
for r in rows[:35]:
    print(f'  {r["需求分"]:5.1f}  {r["sources"]:3d}源 中位{r["中位位次"]:4.1f} '
          f'top3={r["top3次数"]:2d} 域{r["覆盖国数"]:2d}  {r["keyword"]}')
