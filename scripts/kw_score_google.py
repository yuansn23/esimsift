# -*- coding: utf-8 -*-
"""Google 通道需求分（2026-10-08 第五十三轮）—— 离线重算，不联网

数据来源（两条 Google 官方通道，都在 docs/keywords/google/）：
  ① raw_google_suggest.json  Google Suggest 补全 —— 广度与位次证据
  ② raw_google_trends.json   Google Trends relatedQueries —— **带相对搜索指数**

★ 为什么这次能给「热度数值」而上一轮不能
  上一轮（Bing 通道）只有补全位次，**没有任何数值**，所以只能造一个 0-100 的
  代理分。Google Trends 的 relatedQueries 直接返回 value（0-100，相对于该词
  自身时间序列的峰值）—— 这是 Google 官方唯一的公开热度数值。

★ 三路证据的口径
  breadth   跨语境广度：有多少个不同的种子把这个词带出来（Google 逐查询补全，
            不像 Bing 注入通用热门块，所以这个信号比上一轮可信得多）
  depth     语境内深度：中位位次 + top3 命中率（抗单点噪声）
  gindex    Google 指数：Trends 给出的 value（0-100；rising 用 +N% / Breakout
            另行标注，不混进 0-100 的尺度）

★ 综合分（0-100）
  有 gindex 的词：综合分 = 0.55×gindex + 0.30×breadth分 + 0.15×depth分
  无 gindex 的词：综合分 = 0.55×breadth分 + 0.45×depth分
  ⚠️ 两者**不可直接比较** —— CSV 里 `google指数` 与 `证据` 两列必须一起看，
     只看综合分会把「Trends 没覆盖但补全很强」的长尾词排低。

产出：docs/keywords/google/kw-google-scored.csv
"""
import csv
import json
import pathlib
import re
import statistics
import unicodedata

ROOT = pathlib.Path(__file__).resolve().parent.parent
GDIR = ROOT / "docs" / "keywords" / "google"

_STOP = {"esim", "e", "sim", "for", "in", "the", "a", "an", "of", "to", "and", "or",
         "best", "cheap", "cheapest", "good", "is", "are", "does", "do", "how",
         "what", "which", "with", "on", "at", "my", "your", "buy", "get", "vs"}


def tokens(s):
    s = unicodedata.normalize("NFKD", s.lower())
    return {t for t in re.findall(r"[a-z0-9]+", s) if t not in _STOP and len(t) > 2}


# 种子「语境域」词表：国名 + 短名 + 城市 + 区域（与 kw_score.py 同口径）
def build_scope_tokens():
    txt = (ROOT / "data" / "countries.toml").read_text(encoding="utf-8")
    toks = {m.group(1).lower() for m in re.finditer(r'^name\s*=\s*"([^"]+)"', txt, re.M)}
    toks |= {"usa", "us", "uk", "england", "britain", "uae", "dubai", "abu dhabi",
             "korea", "seoul", "macau", "macao", "taipei", "czech republic", "turkey",
             "istanbul", "holland", "amsterdam", "nz", "ksa", "viet nam", "bali",
             "bangkok", "cancun", "manila", "prague", "riyadh", "cape town", "athens",
             "lisbon", "barcelona", "rome", "paris", "berlin", "tokyo", "beijing",
             "sydney", "toronto", "delhi", "rio", "buenos aires", "lima", "santiago",
             "bogota", "cairo", "marrakech", "nairobi", "zanzibar", "doha", "dublin",
             "vienna", "brussels", "dubrovnik", "reykjavik", "oslo", "stockholm",
             "copenhagen", "helsinki", "warsaw", "budapest", "bucharest", "sofia",
             "belgrade", "tirana", "tbilisi", "yerevan", "tashkent", "almaty",
             "kathmandu", "colombo", "dhaka", "karachi", "siem reap", "luang prabang",
             "yangon", "male", "windhoek", "accra", "lagos", "kigali", "dakar",
             "tel aviv", "beirut", "muscat", "havana", "punta cana", "quito", "la paz",
             "montevideo", "bratislava", "ljubljana", "tallinn", "riga", "vilnius",
             "kyiv", "moscow", "phuket", "hong kong", "kuala lumpur", "hanoi",
             "shanghai", "london", "madrid", "las vegas", "miami", "new york",
             "los angeles", "orlando", "hawaii", "mexico city", "vancouver",
             "melbourne", "auckland", "maldives", "edinburgh",
             "europe", "asia", "africa", "middle east", "caribbean", "oceania",
             "north america", "south america", "latin america", "central america",
             "scandinavia", "balkans", "southeast asia", "international", "global",
             "worldwide", "abroad", "overseas"}
    return toks


SCOPE_TOKENS = build_scope_tokens()


# ── 读两条通道 ───────────────────────────────────────────────────────────
sg_path = GDIR / "raw_google_suggest.json"
tr_path = GDIR / "raw_google_trends.json"
if not sg_path.is_file():
    raise SystemExit(f"缺 {sg_path} —— 先跑 scripts/kw_harvest_google.py")
SG = json.loads(sg_path.read_text(encoding="utf-8"))
TR = json.loads(tr_path.read_text(encoding="utf-8")) if tr_path.is_file() else {"related": {}}

print(f"Google Suggest: 种子 {SG['seeds_ok']}/{SG['seeds_total']} 市场 {SG['markets']}")
print(f"Google Trends : 种子 {TR.get('seeds_ok', 0)}/{TR.get('seeds_total', 0)}")

# ── 聚合补全证据 ────────────────────────────────────────────────────────
agg = {}
for key, sugg in SG["suggestions"].items():
    seed, mkt = key.rsplit("|", 1)
    seed = seed.strip().lower()
    stok = tokens(seed)
    scopes = {t for t in SCOPE_TOKENS if t in seed}
    for i, s in enumerate(sugg):
        s = s.strip().lower()
        if not s or len(s) < 5:
            continue
        r = agg.setdefault(s, {"ranks": [], "seeds": set(), "markets": set(),
                               "scopes": set(), "best_rank": 99, "best_seed": None})
        r["ranks"].append(i + 1)
        r["seeds"].add(seed)
        r["markets"].add(mkt)
        r["scopes"] |= scopes
        if i + 1 < r["best_rank"]:
            r["best_rank"], r["best_seed"] = i + 1, seed

# ── 强领域词白名单（判定 Trends 条目是否与 eSIM 相关）──────────────────
# ★ 只用「与种子共享词元」做过滤会**误杀真实词**：实测 `esim japan` 的 Trends top
#   里有 `saily`（日本语境下用户确实搜 saily），但它与种子无共同词元。
#   同时 `embody` / `shoplc` 这类 Breakout 噪音必须滤掉（Google 会把全站暴涨词
#   塞进 rising，实测 saily esim 的 breakout 里是 medvi / shop lc / embody）。
#   所以判据是：**命中强领域词 或 与种子共享实词** → 保留。
def build_domain():
    words = {"esim", "esims", "sim", "sims", "esimulator"}
    pr = ROOT / "data" / "providers.toml"
    if pr.is_file():
        txt = pr.read_text(encoding="utf-8")
        for m in re.finditer(r'^name\s*=\s*"([^"]+)"', txt, re.M):
            words |= set(re.findall(r"[a-z0-9]+", m.group(1).lower()))
        for m in re.finditer(r"^\[([a-z0-9]+)\]", txt, re.M):
            words.add(m.group(1).lower())
    import importlib.util
    spec = importlib.util.spec_from_file_location(
        "kh", str(ROOT / "scripts" / "kw_harvest_google.py"))
    kh = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(kh)
    for c in kh.read_countries():
        words |= set(re.findall(r"[a-z0-9]+", c["name"].lower()))
        words |= set(re.findall(r"[a-z0-9]+", c["slug"].replace("-", " ")))
        for a in kh.ALIASES.get(c["slug"], []):
            words |= set(re.findall(r"[a-z0-9]+", a))
    words |= {"europe", "asia", "africa", "americas", "oceania", "caribbean",
              "scandinavia", "balkans", "middle", "east"}
    return words


DOMAIN = build_domain()


def relevant(q, stok):
    return bool(set(re.findall(r"[a-z0-9]+", q.lower())) & DOMAIN) or bool(tokens(q) & stok)


# ── 聚合 Trends 指数 ────────────────────────────────────────────────────
tr_top, tr_rise, tr_noise = {}, {}, 0
for seed, blk in (TR.get("related") or {}).items():
    stok = tokens(seed)
    for k in blk.get("top", []):
        q = k["query"].strip().lower()
        if not k.get("hasData", True):
            continue
        if not relevant(q, stok):
            tr_noise += 1
            continue
        prev = tr_top.get(q)
        if prev is None or (k.get("value") or 0) > (prev["value"] or 0):
            tr_top[q] = {"value": k.get("value"), "seed": seed}
    for k in blk.get("rising", []):
        q = k["query"].strip().lower()
        if not relevant(q, stok):
            tr_noise += 1
            continue
        tr_rise.setdefault(q, []).append(
            {"formatted": k.get("formatted"), "value": k.get("value"), "seed": seed})

rows = []
for kw, r in agg.items():
    n = len(r["seeds"])
    med = statistics.median(r["ranks"])
    top3 = sum(1 for x in r["ranks"] if x <= 3)
    s_breadth = min(n / 40.0, 1.0)
    s_depth = max(0.0, (13.0 - med) / 12.0)
    s_top3 = min(top3 / 8.0, 1.0)
    ac_score = 100 * (0.55 * s_breadth + 0.35 * s_depth + 0.10 * s_top3)

    t = tr_top.get(kw)
    gidx = t["value"] if t else None
    rise = tr_rise.get(kw)
    if gidx is not None:
        score = 0.55 * gidx + 0.30 * (100 * s_breadth) + 0.15 * (100 * s_depth)
        ev = "Trends+Suggest"
    else:
        score = 0.55 * (100 * s_breadth) + 0.45 * (100 * s_depth)
        ev = "Suggest"

    rows.append({
        "keyword": kw,
        "综合分": round(score, 1),
        "补全分": round(ac_score, 1),
        "google指数": gidx if gidx is not None else "",
        "上升信号": (rise[0]["formatted"] if rise else ""),
        "sources": n,
        "中位位次": med,
        "top3次数": top3,
        "best_rank": r["best_rank"],
        "best_seed": r["best_seed"],
        "markets": ",".join(sorted(r["markets"])),
        "证据": ev,
        "覆盖国数": len(r["scopes"]),
    })

rows.sort(key=lambda x: (-x["综合分"], x["keyword"]))
out = GDIR / "kw-google-scored.csv"
with out.open("w", encoding="utf-8", newline="") as f:
    w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
    w.writeheader()
    w.writerows(rows)

n_tr = sum(1 for r in rows if r["google指数"] != "")
print(f"\n唯一补全词 {len(rows)}；其中带 Trends 指数 {n_tr}；"
      f"Trends 过滤无关项 {tr_noise} 条")
print(f"-> {out.relative_to(ROOT)}")
print("\n=== 综合分 Top 30 ===")
for r in rows[:30]:
    gi = f'{r["google指数"]:>4}' if r["google指数"] != "" else "   -"
    rs = f' {r["上升信号"]:>9}' if r["上升信号"] else ""
    print(f'  {r["综合分"]:5.1f} (补全{r["补全分"]:5.1f}) 指数{gi} '
          f'{r["sources"]:3d}源  {r["keyword"]}{rs}')
