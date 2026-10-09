# -*- coding: utf-8 -*-
"""Google Trends 相关查询采集（2026-10-08 第五十三轮）

为什么需要这条通道：
  Google Suggest 给的是「有人这么搜」的存在性证据（位次 = 相对顺序），
  但**没有数值**。Google Trends 的 relatedQueries 返回的是
  **带相对搜索指数的相关查询**（value 0-100，Breakout 用倍数表示）——
  这是 Google 官方唯一的公开热度数值，能直接当权重用。

接口（两条，成对使用）：
  ① GET /trends/api/explore?req=<urlencoded json>   -> widgets[]，其中 RELATED_QUERIES 带 token
  ② GET /trends/api/widgetdata/relatedsearches?req=<该 widget 的 request>&token=<token>
     -> {default:{rankedList:[{rankedKeyword:[{query,value,formattedValue,hasData}]}]}}
  响应体以 ")]}'" 开头（Google 的 XSSI 防护前缀），需剥掉再 json.loads。

★ 限速实测：429 非常频繁（单 IP 下大约每 2-3 个请求撞一次）。
  必须**指数退避**（6/12/24/48s）—— 实测这样能稳定穿透；线性短退避无效。
  steady 状态下速率约 1 请求/6-8s，故本脚本默认 --workers 2。

★ 噪音实测：Rising/Breakout 列表里会混进**与种子毫无关系**的词
  （查 "esim" 的 breakout 里出现 medvi / shop lc / embody —— 这是 Google
  把全站暴涨词塞进 breakout 的已知行为）。本脚本**照原样保存**，不做删除，
  由 kw_report 层按「与种子词元是否相交」过滤 —— 原始数据保持可复核。

用法：
  python -X utf8 scripts/kw_trends.py --probe        # 3 个种子自检
  python -X utf8 scripts/kw_trends.py --limit 8      # 小批
  python -X utf8 scripts/kw_trends.py                # 全量（约 130 种子 / 260 请求）
"""
import argparse
import gzip
import http.cookiejar
import json
import pathlib
import re
import threading
import time
import urllib.parse
import urllib.request
from concurrent.futures import ThreadPoolExecutor

ROOT = pathlib.Path(__file__).resolve().parent.parent
OUT_DIR = ROOT / "docs" / "keywords" / "google"

PROXY = "http://127.0.0.1:7890"
UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36")

_cj = http.cookiejar.CookieJar()
_op = urllib.request.build_opener(
    urllib.request.ProxyHandler({"http": PROXY, "https": PROXY}),
    urllib.request.HTTPCookieProcessor(_cj))
_lock = threading.Lock()
_done = [0]


def _get_json(url, tries=6, base=6):
    """带指数退避的 GET。返回 (parsed | None, 重试次数)。"""
    for i in range(tries):
        try:
            req = urllib.request.Request(url, headers={
                "User-Agent": UA, "Accept-Language": "en-US,en;q=0.9",
                "Accept-Encoding": "gzip", "Referer": "https://trends.google.com/"})
            raw = _op.open(req, timeout=30).read()
            if raw[:2] == b"\x1f\x8b":
                raw = gzip.decompress(raw)
            t = raw.decode("utf-8", "replace")
            if t.startswith(")]}'"):
                t = t.split("\n", 1)[1]
            return json.loads(t), i
        except Exception:
            if i == tries - 1:
                return None, tries
            time.sleep(base * (2 ** i))
    return None, tries


def prime_cookie():
    """Trends 需要 NID cookie；首页本身也可能 429，退避重试。"""
    for i in range(5):
        try:
            _op.open(urllib.request.Request(
                "https://trends.google.com/trends/explore?geo=US&q=esim",
                headers={"User-Agent": UA}), timeout=30).read()
            return True
        except Exception:
            time.sleep(5 * (i + 1))
    return False


def explore(kw, geo="US", tf="today 12-m"):
    req = {"comparisonItem": [{"keyword": kw, "geo": geo, "time": tf}],
           "category": 0, "property": ""}
    u = ("https://trends.google.com/trends/api/explore?hl=en-US&tz=0&req="
         + urllib.parse.quote(json.dumps(req, separators=(",", ":"))))
    return _get_json(u)


def related(kw, geo="US", tf="today 12-m"):
    d, a1 = explore(kw, geo, tf)
    if not d:
        return None, a1
    w = next((x for x in d.get("widgets", []) if x["id"] == "RELATED_QUERIES"), None)
    if not w:
        return None, a1
    q = urllib.parse.urlencode({"hl": "en-US", "tz": "0",
        "req": json.dumps(w["request"], separators=(",", ":")), "token": w["token"]})
    r, a2 = _get_json("https://trends.google.com/trends/api/widgetdata/relatedsearches?" + q)
    if not r:
        return None, a1 + a2
    out = {"top": [], "rising": []}
    for rl in (r.get("default", {}) or {}).get("rankedList", []):
        items = rl.get("rankedKeyword", [])
        if not items:
            continue
        # 用 value 的量级区分 top（0-100）与 rising（倍数 / Breakout）
        is_rising = any(k.get("formattedValue") in ("Breakout",) or
                        (isinstance(k.get("formattedValue"), str)
                         and k["formattedValue"].startswith("+")) for k in items)
        key = "rising" if is_rising else "top"
        for k in items:
            out[key].append({"query": k["query"], "value": k.get("value"),
                             "formatted": k.get("formattedValue"),
                             "hasData": k.get("hasData", True)})
    return out, a1 + a2


# ── 种子集：头部词（Trends 请求昂贵，只跑最有价值的）────────────────────
def build_seeds():
    import importlib.util
    spec = importlib.util.spec_from_file_location(
        "kh", str(ROOT / "scripts" / "kw_harvest_google.py"))
    kh = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(kh)
    countries = kh.read_countries()
    brands = kh.read_brands()
    seeds = []
    for c in countries:
        f = kh.ALIASES.get(c["slug"], [c["name"].lower()])[0]
        seeds.append(f"esim {f}")
        seeds.append(f"esim for {f}")
    for b in brands:
        seeds.append(f"{b['name'].lower()} esim")
    seeds += ["esim", "best esim", "cheapest esim", "unlimited esim", "travel esim",
              "esim europe", "esim asia", "esim usa", "esim uk",
              "esim japan and korea", "esim hong kong and china",
              "esim for europe and usa", "global esim"]
    seen, out = set(), []
    for s in seeds:
        if s not in seen:
            seen.add(s)
            out.append(s)
    return out


def probe():
    print("prime cookie:", prime_cookie(), "| cookie 数:", len(_cj))
    for kw in ["esim", "esim japan", "airalo"]:
        r, att = related(kw)
        n = "FAIL" if r is None else f"top={len(r['top'])} rising={len(r['rising'])}"
        print(f"  {kw!r:16s} {n}  (重试 {att})")
        if r:
            for k in r["top"][:4]:
                print(f"        {k['value']:>6}  {k['query']}")
        time.sleep(3)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--probe", action="store_true")
    ap.add_argument("--limit", type=int, default=0)
    ap.add_argument("--workers", type=int, default=2)
    ap.add_argument("--geo", default="US")
    ap.add_argument("--from-scored", type=int, default=0,
                    help="额外把 kw-google-scored.csv 里综合分最高的 N 个「无指数」词当种子"
                         "（指数覆盖率提升用；这些是补全证据最强但 Trends 未覆盖的词）")
    ap.add_argument("--merge", action="store_true",
                    help="与已存在的 raw_google_trends.json 合并（不覆盖旧结果）")
    args = ap.parse_args()

    if args.probe:
        probe()
        return

    ok_cookie = prime_cookie()
    print(f"cookie 就绪={ok_cookie}（{len(_cj)} 个）", flush=True)

    seeds = build_seeds()
    if args.from_scored:
        import csv as _csv
        sp = OUT_DIR / "kw-google-scored.csv"
        if sp.is_file():
            srows = list(_csv.DictReader(sp.open(encoding="utf-8")))
            extra = [r["keyword"] for r in srows if not r["google指数"]][:args.from_scored]
            seeds = extra + seeds
            print(f"补种子：从打发表取 {len(extra)} 个无指数高分词", flush=True)
    # merge 模式下跳过已有结果的种子（否则会白白重跑）
    have = set()
    _p = OUT_DIR / "raw_google_trends.json"
    if args.merge and _p.is_file():
        have = set((json.loads(_p.read_text(encoding="utf-8")).get("related") or {}))
        before = len(seeds)
        seeds = [s for s in seeds if s not in have]
        print(f"跳过已有 {before - len(seeds)} 个种子", flush=True)
    if args.limit:
        seeds = seeds[:args.limit]
    print(f"Trends 种子 {len(seeds)} 个 × 2 请求，并发 {args.workers}", flush=True)

    res, fails = {}, []
    t0 = time.time()

    def work(kw):
        r, att = related(kw, geo=args.geo)
        with _lock:
            _done[0] += 1
            if _done[0] % 10 == 0:
                print(f"  {_done[0]}/{len(seeds)}  {time.time()-t0:.0f}s  "
                      f"失败={len(fails)}", flush=True)
            if r is None:
                fails.append(kw)
            else:
                res[kw] = {"top": r["top"], "rising": r["rising"], "retries": att}

    with ThreadPoolExecutor(max_workers=args.workers) as ex:
        list(ex.map(work, seeds))

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    p = OUT_DIR / "raw_google_trends.json"
    this_run_ok = len(res)
    merged = 0
    if args.merge and p.is_file():
        old = json.loads(p.read_text(encoding="utf-8"))
        for k, v in (old.get("related") or {}).items():
            if k not in res:
                res[k] = v
                merged += 1
        print(f"合并旧结果 {merged} 个种子", flush=True)
    p.write_text(json.dumps({
        "generated": time.strftime("%Y-%m-%dT%H:%M:%S"), "channel": "google_trends",
        "geo": args.geo, "timeframe": "today 12-m", "proxy": PROXY,
        "seeds_total": len(seeds), "this_run_ok": this_run_ok,
        "seeds_ok": len(res), "seeds_failed": len(fails),
        "merged_from_previous": merged,
        "failed_seeds": fails, "related": res,
    }, ensure_ascii=False, indent=1), encoding="utf-8")

    ntop = sum(len(v["top"]) for v in res.values())
    nris = sum(len(v["rising"]) for v in res.values())
    print(f"\n完成 {len(res)}/{len(seeds)}；top {ntop} 条 / rising {nris} 条")
    print(f"-> {p.relative_to(ROOT)}")
    for kw in list(res)[:6]:
        print(f"\n  ### {kw}")
        for k in res[kw]["top"][:6]:
            print(f"      {k['value']:>6}  {k['query']}")


if __name__ == "__main__":
    main()
