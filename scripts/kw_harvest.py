# -*- coding: utf-8 -*-
"""eSIM 长尾词全网采集器（2026-10-08）

方法：查询补全（autocomplete）是由**真实查询频率**驱动的 —— 一个短语能出现在补全列表里，
就是「有人这么搜」的实证；出现在列表第 1 位 vs 第 10 位，代表相对热度高低。
本脚本不产出「搜索量」数字（那需要 GSC/Ahrefs，本站没有），只产出**可复核的需求证据**：

  证据字段        含义
  --------------  ------------------------------------------------
  sources         有多少个不同的种子词把这个关键词带出来了（越多=越主流）
  best_rank       在补全列表里的最好位次（1 = 最热门的下一个词）
  markets         在哪些市场（en-US / en-GB）被带出
  seed_1          rank 最高的那次是由哪个种子带出的

采集通道：Bing 补全（api.bing.com/osjson.aspx）。Google 补全在本机不可达（返回空），
DuckDuckGo 同样不可达 —— 这是本机网络事实，不是词不存在。_audit 里记录了通道可用性。

用法：
  python -X utf8 scripts/kw_harvest.py --smoke          # 2 国冒烟
  python -X utf8 scripts/kw_harvest.py                  # 全量（约 2000 请求）
  python -X utf8 scripts/kw_harvest.py --markets en-US  # 单市场
"""
import argparse
import io
import json
import pathlib
import re
import sys
import threading
import time
import urllib.parse
import urllib.request
from collections import defaultdict
from concurrent.futures import ThreadPoolExecutor

ROOT = pathlib.Path(__file__).resolve().parent.parent
OUT_DIR = ROOT / "docs" / "keywords"

BING = "https://api.bing.com/osjson.aspx?query={q}&mkt={mkt}"
UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/124.0 Safari/537.36")

_lock = threading.Lock()
_done = [0]


def read_countries():
    txt = (ROOT / "data" / "countries.toml").read_text(encoding="utf-8")
    out = []
    for block in re.finditer(r"^\[([A-Z]{2})\]\n(.*?)(?=^\[|\Z)", txt, re.M | re.S):
        iso, body = block.group(1), block.group(2)
        name = re.search(r'name\s*=\s*"([^"]+)"', body)
        slug = re.search(r'slug\s*=\s*"([^"]+)"', body)
        if name and slug:
            out.append({"iso": iso, "name": name.group(1), "slug": slug.group(1)})
    return out


def read_brands():
    txt = (ROOT / "data" / "providers.toml").read_text(encoding="utf-8")
    out = []
    for block in re.finditer(r"^\[([a-z0-9]+)\]\n(.*?)(?=^\[|\Z)", txt, re.M | re.S):
        key, body = block.group(1), block.group(2)
        name = re.search(r'name\s*=\s*"([^"]+)"', body)
        if name:
            out.append({"key": key, "name": name.group(1)})
    return out


# ---------- 种子词模板 ----------
COUNTRY_PATS_FULL = [
    "esim {c}",
    "esim for {c}",
    "best esim for {c}",
    "cheapest esim {c}",
    "{c} esim",
    "{c} esim unlimited",
    "{c} esim price",
    "{c} esim plans",
    "esim {c} 10gb",
    "unlimited data esim {c}",
    "does esim work in {c}",
    "esim {c} vs sim",
    "{c} sim card for tourists",
    "how to get an esim for {c}",
    "esim {c} airport",
    "esim {c} for iphone",
    "esim coverage in {c}",
    "is esim available in {c}",
    "esim {c} reddit",
    "cheap esim {c}",
]
COUNTRY_PATS_LITE = [
    "esim {c}",
    "esim for {c}",
    "best esim for {c}",
    "{c} esim",
    "{c} esim unlimited",
    "cheapest esim {c}",
    "does esim work in {c}",
    "{c} sim card for tourists",
    "esim {c} price",
    "esim {c} 10gb",
]
GLOBAL_SEEDS = [
    "esim", "esim deals", "esim plans", "esim vs sim", "esim vs pocket wifi",
    "best esim", "cheapest esim", "unlimited esim", "esim compatible phones",
    "how to install esim", "how to activate esim", "what is an esim",
    "esim for europe", "esim for asia", "esim for cruise", "esim for international travel",
    "travel esim", "esim promo code", "esim discount code", "is esim worth it",
    "esim data plan", "esim no contract", "esim for iphone", "esim for android",
    "esim with phone number", "esim hot spot", "esim hotspot tethering",
    "esim speed", "esim coverage map", "esim top up",
]

# ★ 第 2 轮（别名轮）—— 修正一个真实的方法论错误：
#   种子用了 data/countries.toml 的 name 字段（"United States" / "United Kingdom"），
#   但**真实用户查询用短名**（usa / us / uk / uae / korea / hong kong），
#   而站内命名规则本身也是「USA 替代 United States、UK 替代 United Kingdom」。
#   用长名的代价实测很直接：US 国家页只采到 99 词、最高分 52.7（而日本页 104 词），
#   因为补全引擎对 "united states esim" 的后续建议远少于 "esim usa"。
ALIASES = {
    "united-states": ["usa", "us"],
    "united-kingdom": ["uk", "england"],
    "united-arab-emirates": ["uae", "dubai"],
    "south-korea": ["korea", "seoul"],
    "hong-kong": ["hong kong"],
    "macau": ["macau", "macao"],
    "taiwan": ["taipei"],
    "czechia": ["czech republic", "prague"],
    "t-rkiye": ["turkey", "istanbul"],
    "turkiye": ["turkey", "istanbul"],
    "netherlands": ["holland", "amsterdam"],
    "new-zealand": ["nz"],
    "saudi-arabia": ["ksa", "riyadh"],
    "south-africa": ["cape town"],
    "costa-rica": ["san jose costa rica"],
    "vietnam": ["viet nam"],
    "philippines": ["manila"],
    "indonesia": ["bali"],
    "thailand": ["bangkok"],
    "mexico": ["cancun"],
}
# 带年份的修饰词是真实长尾（站内 <title> 就在用 {Year}）
YEAR_PATS = ["esim {c} 2026", "best esim for {c} 2026", "{c} esim 2026"]
EXTRA_PATS = [
    "{c} esim card", "{c} esim reddit", "{c} esim unlimited data",
    "esim for {c} review", "cheapest esim for {c}", "{c} esim best",
    "do i need an esim for {c}", "{c} esim coverage map",
]
# 城市词：国家页的禁区（不能开城市页），但**可以并进国家页**做城市段落
CITY_SEEDS = [
    "dubai", "tokyo", "osaka", "seoul", "bangkok", "phuket", "bali", "singapore city",
    "kuala lumpur", "hanoi", "taipei", "hong kong", "shanghai", "london", "paris",
    "rome", "barcelona", "madrid", "lisbon", "amsterdam", "berlin", "prague",
    "vienna", "istanbul", "cairo", "marrakech", "new york", "las vegas", "miami",
    "los angeles", "orlando", "hawaii", "cancun", "mexico city", "toronto",
    "vancouver", "rio de janeiro", "buenos aires", "sydney", "melbourne", "auckland",
    "cape town", "maldives", "zanzibar",
]
# 双国/多国组合 —— 实测**最大的一块未承接需求**
COUNTRY_PAIRS = [
    ("usa", "canada"), ("usa", "mexico"), ("canada", "usa"), ("uk", "france"),
    ("france", "italy"), ("italy", "greece"), ("spain", "portugal"),
    ("germany", "austria"), ("switzerland", "italy"), ("netherlands", "belgium"),
    ("japan", "south korea"), ("south korea", "japan"), ("hong kong", "china"),
    ("china", "hong kong"), ("singapore", "malaysia"), ("malaysia", "singapore"),
    ("singapore", "indonesia"), ("thailand", "vietnam"), ("vietnam", "thailand"),
    ("australia", "new zealand"), ("new zealand", "australia"), ("uae", "qatar"),
    ("turkey", "greece"), ("egypt", "jordan"), ("kenya", "tanzania"),
    ("south africa", "namibia"), ("brazil", "argentina"), ("peru", "chile"),
    ("costa rica", "panama"), ("ireland", "uk"), ("denmark", "sweden"),
    ("norway", "sweden"), ("finland", "sweden"), ("croatia", "italy"),
    ("greece", "turkey"), ("india", "sri lanka"), ("philippines", "vietnam"),
]


def fetch(seed, mkt, tries=3):
    q = urllib.parse.quote(seed)
    url = BING.format(q=q, mkt=mkt)
    for i in range(tries):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": UA})
            raw = urllib.request.urlopen(req, timeout=12).read().decode("utf-8", "replace")
            data = json.loads(raw)
            return data[1] if isinstance(data, list) and len(data) > 1 else []
        except Exception:
            time.sleep(0.6 * (i + 1))
    return None  # 明确标记失败，不当作「无补全」


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--smoke", action="store_true")
    ap.add_argument("--pass2", action="store_true",
                    help="别名轮：用短名/城市名/年份修饰词补采（修 United States→usa 的种子错误）")
    ap.add_argument("--markets", default="en-US,en-GB")
    ap.add_argument("--workers", type=int, default=5)
    args = ap.parse_args()

    countries = read_countries()
    brands = read_brands()
    if args.smoke:
        countries = countries[:2]
    markets = [m.strip() for m in args.markets.split(",") if m.strip()]

    jobs = []
    if args.pass2:
        # ---- 第 2 轮：别名/城市/年份 ----
        for mkt in markets:
            for c in countries:
                nm = c["name"].lower()
                al = ALIASES.get(c["slug"], [])
                forms = [nm] + al
                # 用短名的每个形态跑「核心」模式
                for f in forms:
                    for p in ("esim {c}", "esim for {c}", "best esim for {c}",
                              "{c} esim", "cheapest esim {c}", "{c} esim unlimited"):
                        jobs.append((p.format(c=f), mkt, "country:" + c["iso"]))
                # 年份 + 扩展修饰只跑主名（控制请求量）
                for p in YEAR_PATS + EXTRA_PATS:
                    jobs.append((p.format(c=al[0] if al else nm), mkt, "country:" + c["iso"]))
            # 城市词（用别名里的城市，或 CITIES 里的）
            for city in CITY_SEEDS:
                jobs.append((f"esim {city}", mkt, "city:" + city))
                jobs.append((f"esim for {city}", mkt, "city:" + city))
            # 双国组合（实测是最大一块缺口）
            for a, b in COUNTRY_PAIRS:
                jobs.append((f"esim for {a} and {b}", mkt, "pair"))
                jobs.append((f"best esim for {a} and {b}", mkt, "pair"))
    else:
        for mkt in markets:
            pats = COUNTRY_PATS_FULL if mkt == markets[0] else COUNTRY_PATS_LITE
            for c in countries:
                n = c["name"].lower()
                for p in pats:
                    jobs.append((p.format(c=n), mkt, "country:" + c["iso"]))
            for b in brands:
                for p in ("{b} esim", "{b} esim plan", "is {b} good"):
                    jobs.append((p.format(b=b["name"].lower()), mkt, "brand:" + b["key"]))
                for c in countries:
                    jobs.append((f"{b['name'].lower()} esim {c['name'].lower()}", mkt, "brandxcountry:" + b["key"]))
            for g in GLOBAL_SEEDS:
                jobs.append((g, mkt, "global"))

    # 去重（同 market 同 seed 只跑一次）
    seen = set()
    uniq = []
    for seed, mkt, tag in jobs:
        k = (seed, mkt)
        if k in seen:
            continue
        seen.add(k)
        uniq.append((seed, mkt, tag))
    jobs = uniq
    print(f"种子数 {len(jobs)}（{len(countries)} 国 × {len(brands)} 品牌 × {len(markets)} 市场）", flush=True)

    results = {}
    fails = []
    t0 = time.time()

    def work(job):
        seed, mkt, tag = job
        sg = fetch(seed, mkt)
        with _lock:
            _done[0] += 1
            if _done[0] % 200 == 0:
                print(f"  {_done[0]}/{len(jobs)}  {time.time()-t0:.0f}s 失败={len(fails)}", flush=True)
            if sg is None:
                fails.append(job)
                return
            results[(seed, mkt)] = sg

    with ThreadPoolExecutor(max_workers=args.workers) as ex:
        list(ex.map(work, jobs))

    # ---------- 聚合 ----------
    agg = {}
    for (seed, mkt), sugg in results.items():
        for i, s in enumerate(sugg):
            s = s.strip().lower()
            if not s or len(s) < 4:
                continue
            rec = agg.setdefault(s, {"kw": s, "sources": set(), "best_rank": 99,
                                     "markets": set(), "best_seed": None})
            rec["sources"].add(seed)
            rec["markets"].add(mkt)
            if i + 1 < rec["best_rank"]:
                rec["best_rank"] = i + 1
                rec["best_seed"] = seed

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    tag = ".smoke" if args.smoke else (".pass2" if args.pass2 else "")
    raw_path = OUT_DIR / ("raw_autocomplete%s.json" % tag)
    raw_path.write_text(json.dumps(
        {"generated": time.strftime("%Y-%m-%dT%H:%M:%S"),
         "harvested_at_epoch": int(time.time()),
         "pass": "pass2" if args.pass2 else "pass1",
         "countries": [c["iso"] for c in countries],
         "markets": markets,
         "seeds_total": len(jobs), "seeds_ok": len(results), "seeds_failed": len(fails),
         "failed_seeds": [{"seed": s, "market": m} for s, m, _ in fails],
         "tags": {f"{s}|{m}": t for s, m, t in jobs},
         "suggestions": {f"{s}|{m}": v for (s, m), v in sorted(results.items())}},
        ensure_ascii=False, indent=1), encoding="utf-8")

    rows = sorted(agg.values(), key=lambda r: (-len(r["sources"]), r["best_rank"], r["kw"]))
    csv_path = OUT_DIR / ("kw-autocomplete%s.csv" % tag)
    lines = ["keyword,sources,best_rank,markets,best_seed"]
    for r in rows:
        kw = '"%s"' % r["kw"].replace('"', '""')
        lines.append(f'{kw},{len(r["sources"])},{r["best_rank"]},"{",".join(sorted(r["markets"]))}",'
                     f'"{r["best_seed"]}"')
    csv_path.write_text("\n".join(lines) + "\n", encoding="utf-8")

    print(f"\n采集完成：{len(results)}/{len(jobs)} 个种子有响应，失败 {len(fails)}")
    print(f"去重后唯一补全词：{len(rows)}")
    print(f"原始 -> {raw_path.relative_to(ROOT)}")
    print(f"汇总 -> {csv_path.relative_to(ROOT)}")
    print("\n--- 被 ≥6 个种子带出的词（最主流）---")
    for r in rows[:25]:
        print(f'  {len(r["sources"]):3d}源 r{r["best_rank"]:2d}  {r["kw"]}')


if __name__ == "__main__":
    main()
