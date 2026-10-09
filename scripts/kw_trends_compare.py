# -*- coding: utf-8 -*-
"""Google Trends 批量比较 —— 拿「跨词可比的官方热度」（2026-10-08 第五十四轮）

★ 解决什么问题
  用 relatedQueries 只能拿到「相关查询」的指数，**拿不到某个词自身的指数**。
  而 Trends 的 TIMESERIES 是**按批归一化**的（同批内最热词 = 100），
  所以单批内的值可跨词比较，**跨批不可比**。

  解法（Trends 官方推荐做法）：**每批固定带一个锚词**，用锚词归一 ——
    相对热度(词) = 均值(词) / 均值(锚词)
  锚词的 12 个月真实热度是固定的，它在各批里的数值差异正好反映归一化尺度，
  除掉它就把不同批拉回同一把尺子上。

★ 接口
  ① GET /trends/api/explore?req=<含多个 comparisonItem 的 json>  -> widgets[TIMESERIES]
  ② GET /trends/api/widgetdata/multiline?req=<该 widget 的 request>&token=<token>
     -> default.timelineData[].value = [各词在该时间点的值]

★ 限速同 relatedQueries：429 频繁，必须指数退避（见 kw_trends.py）。

用法：
  python -X utf8 scripts/kw_trends_compare.py --probe     # 1 批自检
  python -X utf8 scripts/kw_trends_compare.py             # 全量（约 19 批）
"""
import argparse
import csv
import gzip
import http.cookiejar
import json
import pathlib
import statistics
import time
import urllib.parse
import urllib.request

ROOT = pathlib.Path(__file__).resolve().parent.parent
G = ROOT / "docs" / "keywords" / "google"

PROXY = "http://127.0.0.1:7890"
UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36")
ANCHOR = "esim"
BATCH = 4                      # 每批目标词数（+1 锚词 = 5，Trends 上限）

_cj = http.cookiejar.CookieJar()
_op = urllib.request.build_opener(
    urllib.request.ProxyHandler({"http": PROXY, "https": PROXY}),
    urllib.request.HTTPCookieProcessor(_cj))


def get_json(url, tries=6, base=6):
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
            return json.loads(t)
        except Exception:
            if i == tries - 1:
                return None
            time.sleep(base * (2 ** i))
    return None


def prime_cookie():
    for i in range(5):
        try:
            _op.open(urllib.request.Request(
                "https://trends.google.com/trends/explore?geo=US&q=esim",
                headers={"User-Agent": UA}), timeout=30).read()
            return True
        except Exception:
            time.sleep(5 * (i + 1))
    return False


def batch_means(words, geo="US", tf="today 12-m"):
    """返回 {word: 时间序列均值}；失败返回 None。"""
    req = {"comparisonItem": [{"keyword": w, "geo": geo, "time": tf} for w in words],
           "category": 0, "property": ""}
    u = ("https://trends.google.com/trends/api/explore?hl=en-US&tz=0&req="
         + urllib.parse.quote(json.dumps(req, separators=(",", ":"))))
    d = get_json(u)
    if not d:
        return None
    wts = next((x for x in d.get("widgets", []) if x["id"] == "TIMESERIES"), None)
    if not wts:
        return None
    q = urllib.parse.urlencode({"hl": "en-US", "tz": "0",
        "req": json.dumps(wts["request"], separators=(",", ":")), "token": wts["token"]})
    r = get_json("https://trends.google.com/trends/api/widgetdata/multiline?" + q)
    if not r:
        return None
    tl = (r.get("default", {}) or {}).get("timelineData", [])
    if not tl:
        return None
    cols = list(zip(*[p.get("value", []) for p in tl]))
    if len(cols) != len(words):
        return None
    return {w: statistics.mean(c) for w, c in zip(words, cols)}


# ── 选词：按词型分层，只取头部（Trends 请求昂贵）────────────────────────
PER_TYPE = {
    "国家·核心": 24, "品牌×国家": 16, "国家·价格/交易": 8, "区域": 8,
    "城市": 4, "国家·规格/流量": 4, "品牌（全局）": 6, "通用·其他": 4,
    "通用·问题": 4, "通用·全球": 4, "通用·价格交易": 4, "国家·对比": 4,
}


def choose(rows):
    by = {}
    for r in rows:
        by.setdefault(r["词型"], []).append(r)
    picked, seen = [], set()
    for t, n in PER_TYPE.items():
        for r in sorted(by.get(t, []), key=lambda z: -float(z["综合分"]))[:n]:
            k = r["keyword"]
            if k not in seen and k != ANCHOR:
                seen.add(k)
                picked.append((k, t))
    return picked


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--probe", action="store_true")
    ap.add_argument("--geo", default="US")
    args = ap.parse_args()

    if args.probe:
        print("cookie:", prime_cookie(), "| cookies:", len(_cj))
        m = batch_means([ANCHOR, "best esim for usa", "esim japan", "saily esim",
                         "esim for europe"])
        print("  结果:", m)
        if m:
            a = m[ANCHOR]
            for k, v in m.items():
                if k != ANCHOR:
                    print(f"    {k:24s} 均值 {v:6.1f}  相对锚词 {v/a:.3f}")
        return

    print("cookie:", prime_cookie(), "| cookies:", len(_cj))
    rows = list(csv.DictReader((G / "kw-google-collected.csv").open(encoding="utf-8")))
    picked = choose(rows)
    groups = [picked[i:i + BATCH] for i in range(0, len(picked), BATCH)]
    print(f"目标词 {len(picked)} -> {len(groups)} 批（每批锚词 {ANCHOR!r} + {BATCH} 词）", flush=True)

    out, failed = [], 0
    for gi, grp in enumerate(groups):
        words = [ANCHOR] + [k for k, _ in grp]
        m, tries = None, 0
        while m is None and tries < 3:
            m = batch_means(words, geo=args.geo)
            tries += 1
            if m is None:
                time.sleep(8 * tries)
        if m is None:
            failed += 1
            print(f"  批 {gi+1}/{len(groups)} 失败", flush=True)
            continue
        a = m.get(ANCHOR) or 0
        for k, t in grp:
            out.append({
                "keyword": k, "词型": t,
                "相对热度": round(m[k] / a, 4) if a else "",
                "批内均值": round(m[k], 2), "锚词均值": round(a, 2), "批次": gi + 1,
            })
        print(f"  批 {gi+1}/{len(groups)} 锚词={a:6.1f}  " +
              "  ".join(f"{k[:20]}={m[k]:7.4f}" for k, _ in grp), flush=True)
        time.sleep(2)

    out.sort(key=lambda x: -(x["相对热度"] if x["相对热度"] != "" else -1))
    # 再加一列「目标内指数」：把本批目标词里最热的那个当作 100。
    # 因为锚词 `esim` 是绝对的头部词，相对值都在 0.0x 量级，直接看不好读。
    mx = max((r["相对热度"] for r in out if r["相对热度"] != ""), default=0)
    for r in out:
        r["目标内指数"] = (round(r["相对热度"] / mx * 100, 1)
                       if mx and r["相对热度"] != "" else "")
    p = G / "kw-trends-index.csv"
    with p.open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=["keyword", "词型", "相对热度", "目标内指数",
                                          "批内均值", "锚词均值", "批次"])
        w.writeheader()
        w.writerows(out)
    print(f"\n-> {p.relative_to(ROOT)}（{len(out)} 词，失败批 {failed}）")
    print(f"\n=== 相对热度 Top 30（锚词 {ANCHOR!r} = 1.0；目标内指数 = 组内归一化）===")
    for r in out[:30]:
        print(f'  {r["相对热度"]:8.4f}  指数{r["目标内指数"]:6.1f}  '
              f'{r["词型"]:12s} {r["keyword"]}')


if __name__ == "__main__":
    main()
