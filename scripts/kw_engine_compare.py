# -*- coding: utf-8 -*-
"""Google vs Bing 补全引擎对照实验（2026-10-08 第五十三轮）

用途：给报告里「两个引擎都不存在全局通用块注入」这个论断提供可复现证据。

方法：取 N 个互不相关的种子，分别向两个引擎取补全，算两两 Jaccard 重叠率。
  - 若某引擎「注入通用块」，则不同种子的补全列表应高度重叠 → 平均 Jaccard 高
  - 另算「被 ≥3 个互不相关种子共同带出的词」数量 —— 通用块的直接标志

★ 异常与空必须分开计：本机实测 Google 限速时**抛异常**（不是返回空数组），
  把异常吞成空集会把「限速」误读成「该词没有补全」——本轮就踩过这一次。

用法：python -X utf8 scripts/kw_engine_compare.py
"""
import itertools
import json
import pathlib
import time
import urllib.parse
import urllib.request
from collections import Counter

ROOT = pathlib.Path(__file__).resolve().parent.parent
OUT = ROOT / "docs" / "keywords" / "google" / "engine-compare.json"

PROXY = "http://127.0.0.1:7890"
UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36")
_op = urllib.request.build_opener(
    urllib.request.ProxyHandler({"http": PROXY, "https": PROXY}))

# 互不相关的种子（刻意跨地理簇）
SEEDS = ["esim japan", "esim france", "esim saudi arabia", "esim brazil",
         "esim cruise", "esim kazakhstan"]


def fetch(engine, seed, tries=4):
    """返回 (keyword_set, status)。status: ok / empty / error"""
    for i in range(tries):
        try:
            if engine == "google":
                u = ("https://suggestqueries.google.com/complete/search?client=firefox"
                     f"&hl=en&gl=us&q={urllib.parse.quote(seed)}")
            else:
                u = ("https://api.bing.com/osjson.aspx?query="
                     f"{urllib.parse.quote(seed)}&mkt=en-US")
            d = json.loads(_op.open(urllib.request.Request(
                u, headers={"User-Agent": UA}), timeout=15).read().decode("utf-8", "replace"))
            if not (isinstance(d, list) and len(d) > 1):
                return set(), "error"
            s = {(x or "").strip().lower() for x in d[1]}
            s.discard(seed.strip().lower())          # 剔除种子回显
            return s, ("ok" if s else "empty")
        except Exception:
            if i == tries - 1:
                return set(), "error"
            time.sleep(1.5 * (i + 1))
    return set(), "error"


def main():
    res = {}
    for eng in ("google", "bing"):
        res[eng] = {}
        for s in SEEDS:
            kw, status = fetch(eng, s)
            res[eng][s] = {"status": status, "n": len(kw), "keywords": sorted(kw)}
            print(f"  {eng:6s} {s!r:28s} {status:5s} {len(kw):2d} 条")
            time.sleep(0.8)

    def jac(a, b):
        return len(a & b) / len(a | b) if (a | b) else 0.0

    pairs = list(itertools.combinations(SEEDS, 2))
    summary = {}
    for eng in ("google", "bing"):
        sets = {s: set(res[eng][s]["keywords"]) for s in SEEDS}
        js = [jac(sets[a], sets[b]) for a, b in pairs]
        c = Counter()
        for s in SEEDS:
            for k in sets[s]:
                c[k] += 1
        common = [k for k, n in c.items() if n >= 3]
        errs = [s for s in SEEDS if res[eng][s]["status"] == "error"]
        summary[eng] = {
            "mean_jaccard": round(sum(js) / len(js), 4) if js else None,
            "max_jaccard": round(max(js), 4) if js else None,
            "shared_by_3plus": sorted(common),
            "n_shared_by_3plus": len(common),
            "errors": errs,
            "empty": [s for s in SEEDS if res[eng][s]["status"] == "empty"],
        }

    print()
    for eng, s in summary.items():
        print(f"  {eng:6s} 平均重叠 {s['mean_jaccard']}  最大 {s['max_jaccard']}  "
              f"≥3 源共享词 {s['n_shared_by_3plus']} 个  报错 {len(s['errors'])}")
        if s["shared_by_3plus"]:
            print(f"         共享词: {s['shared_by_3plus'][:12]}")

    OUT.write_text(json.dumps({
        "generated": time.strftime("%Y-%m-%dT%H:%M:%S"),
        "seeds": SEEDS, "proxy": PROXY, "raw": res, "summary": summary,
    }, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"\n-> {OUT.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
