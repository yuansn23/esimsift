# -*- coding: utf-8 -*-
"""把采集到的补全词分类、判定归属页型、与站内现状 + 旧词库对账（2026-10-08）

输入：docs/keywords/kw-autocomplete.csv（kw_harvest.py 产出）
输出：docs/keywords/kw-collected-<date>.csv   （主交付物）
      docs/keywords/kw-gaps-<date>.md        （缺口与行动清单）

需求分（0-100）是**可复核的观测值**，不是搜索量：
  需求分 = 50 × min(sources/20, 1) + 50 × (13 - best_rank)/12
  - 前半：广度 —— 有多少个不同种子词把它带出来（跨语境普遍性）
  - 后半：深度 —— 它在补全列表里的最好位次（1 = 该语境下最热的下一个词）
口径警告：sources 受种子设计影响（含国名的词会被该国所有种子带出），
         所以**跨国家比较 sources 有效，同国不同修饰语比较 best_rank 更可靠**。
"""
import argparse
import csv
import json
import pathlib
import re
import unicodedata
from collections import defaultdict

ROOT = pathlib.Path(__file__).resolve().parent.parent
KW = ROOT / "docs" / "keywords"
MATRIX = pathlib.Path(r"C:\Users\Administrator\WorkBuddy\2026-09-30-13-09-50"
                      r"\esim-compare-blueprint\keyword-matrix.csv")

BRAND_KEYS = ["roami", "airalo", "holafly", "saily", "yesim", "ubigi",
              "roamic", "alosim", "nomad", "jetpac"]
BRAND_ALIAS = {"roamic": "roamic", "roami": "roami", "alosim": "alosim",
               "airlao": "airalo", "airlo": "airalo", "holefly": "holafly",
               "sailly": "saily", "nomade": "nomad"}
BRAND_DISPLAY = {"roami": "Roami", "airalo": "Airalo", "holafly": "Holafly",
                 "saily": "Saily", "yesim": "Yesim", "ubigi": "Ubigi",
                 "roamic": "Roamic", "alosim": "aloSIM", "nomad": "Nomad",
                 "jetpac": "Jetpac"}

# 短名/别名 → 国家 slug（只按 name 匹配会漏掉真实查询里的短名）
COUNTRY_ALIAS = {
    "united-states": ["usa", "us"],
    "united-kingdom": ["uk", "england", "britain", "great britain"],
    "united-arab-emirates": ["uae"],
    "south-korea": ["korea", "republic of korea"],
    "czechia": ["czech republic"],
    "netherlands": ["holland"],
    "new-zealand": ["nz"],
    "saudi-arabia": ["ksa"],
    "vietnam": ["viet nam"],
    "macau": ["macao"],
}

REGIONS = {
    "europe": ["europe", "eu "],
    "asia": ["asia", "southeast asia", "south east asia", "east asia"],
    "middle east": ["middle east", "gulf", "gcc"],
    "americas": ["north america", "south america", "latin america", "central america", "caribbean"],
    "africa": ["africa"],
    "oceania": ["oceania", "pacific islands"],
    "scandinavia": ["scandinavia", "nordic"],
    "balkans": ["balkans"],
}
# 「国际化」类修饰：**不是地理区域**，不带国名时应归「通用」，不能算区域页
GENERIC = re.compile(r"\b(international|global|worldwide|abroad|overseas|multi ?country|"
                     r"cross ?border|roaming)\b")

CITIES = ["tokyo", "osaka", "kyoto", "seoul", "busan", "bangkok", "phuket", "chiang mai",
          "singapore city", "kuala lumpur", "bali", "jakarta", "manila", "cebu", "hanoi",
          "ho chi minh", "da nang", "taipei", "hong kong", "macau", "shanghai", "beijing",
          "dubai", "abu dhabi", "doha", "riyadh", "jeddah", "istanbul", "cairo", "marrakech",
          "london", "paris", "rome", "milan", "barcelona", "madrid", "lisbon", "amsterdam",
          "berlin", "munich", "vienna", "prague", "budapest", "warsaw", "athens", "zurich",
          "brussels", "copenhagen", "stockholm", "oslo", "helsinki", "dublin", "edinburgh",
          "new york", "los angeles", "san francisco", "las vegas", "miami", "chicago",
          "boston", "seattle", "washington", "orlando", "honolulu", "hawaii", "alaska",
          "toronto", "vancouver", "montreal", "mexico city", "cancun", "tulum", "bogota",
          "lima", "santiago", "buenos aires", "rio de janeiro", "sao paulo", "cusco",
          "sydney", "melbourne", "brisbane", "perth", "auckland", "queenstown", "fiji",
          "cape town", "johannesburg", "nairobi", "zanzibar", "mauritius", "maldives"]

# 词型判据（顺序即优先级，先命中先归类）
SPEC_RE = re.compile(r"\b(\d+\s?(gb|mb|tb)|\d+\s?-?\s?day|\d+\s?-?\s?days|unlimited|"
                     r"validity|data plan|hotspot|tether|top ?up|recharge|esim plan|"
                     r"esim plans|phone number|sms|call|voice)\b")
PRICE_RE = re.compile(r"\b(cheap|cheapest|price|prices|cost|costs|how much|deal|deals|"
                      r"discount|promo|coupon|code|offer|sale|budget|affordable|worth)\b")
CHANNEL_RE = re.compile(r"\b(airport|klook|shopee|lazada|amazon|7-eleven|711|convenience|"
                        r"store|shop|pick ?up|ksa|changi|narita|haneda|incheon)\b")
COMPARE_RE = re.compile(r"\b(vs|versus|or |better|compare|comparison|difference|"
                        r"instead of|replace|alternative)\b")
DEVICE_RE = re.compile(r"\b(iphone|android|pixel|samsung|galaxy|ipad|tablet|watch|"
                       r"smartphone|phone support|compatible|compatibility|esim ready|"
                       r"esim only|unlocked|carrier lock)\b")
QUESTION_RE = re.compile(r"^(does|do|is|are|can|will|what|how|where|which|why|who|should|"
                         r"when|if)\b")
REDDIT_RE = re.compile(r"\b(reddit|review|reviews|legit|safe|scam|trust|reliable|"
                       r"good|worth it|experience)\b")

TYPE_ORDER = [
    "品牌×国家", "品牌（全局）", "品牌对决",
    "国家·核心", "国家·价格/交易", "国家·规格/流量", "国家·网络覆盖",
    "国家·设备兼容", "国家·对比", "国家·落地渠道",
    "城市", "区域"],


def norm(s):
    s = unicodedata.normalize("NFKD", s).encode("ascii", "ignore").decode()
    return re.sub(r"[^a-z0-9]+", " ", s.lower()).strip()


def load_countries():
    txt = (ROOT / "data" / "countries.toml").read_text(encoding="utf-8")
    out = []
    for b in re.finditer(r"^\[([A-Z]{2})\]\n(.*?)(?=^\[|\Z)", txt, re.M | re.S):
        iso, body = b.group(1), b.group(2)
        nm = re.search(r'name\s*=\s*"([^"]+)"', body)
        sl = re.search(r'slug\s*=\s*"([^"]+)"', body)
        if nm and sl:
            out.append({"iso": iso, "name": nm.group(1), "slug": sl.group(1),
                        "n": norm(nm.group(1))})
    return out


def find_countries(kw, countries):
    """返回关键字里的国家（长的优先，避免 'united states' 被 'united kingdom' 干扰）

    同时识别**短名/别名**（usa / uk / uae / korea / hong kong…）—— 真实查询用短名，
    只按 countries.toml 的 name 匹配会把 `esim for korea and japan` 只识别成 1 国。
    """
    hits = []
    for c in countries:
        forms = [c["n"]] + COUNTRY_ALIAS.get(c["slug"], [])
        for f in forms:
            if re.search(r"(?:^|\s)" + re.escape(f) + r"(?:\s|$)", kw):
                hits.append(c)
                break
    seen = set()
    uniq = []
    for c in hits:
        if c["slug"] not in seen:
            seen.add(c["slug"])
            uniq.append(c)
    uniq.sort(key=lambda c: -len(c["n"]))
    # 去掉被更长国名包含的（united arab emirates 里不该再算 emirates/arab）
    keep = []
    for c in uniq:
        if not any(c["n"] in o["n"] and c["n"] != o["n"] for o in uniq):
            keep.append(c)
    return keep


def find_brands(kw):
    hits = []
    for tok in kw.split():
        k = BRAND_ALIAS.get(tok, tok if tok in BRAND_KEYS else None)
        if k and k not in hits:
            hits.append(k)
    return hits


def classify(kw, countries):
    cts = find_countries(kw, countries)
    brs = find_brands(kw)
    regions = [r for r, al in REGIONS.items() if any(a in kw for a in al)]
    cities = [c for c in CITIES if c in kw]
    n_ct = len(cts)

    if n_ct >= 2:
        return "区域", cts, brs, regions, cities
    if brs and n_ct == 1:
        return "品牌×国家", cts, brs, regions, cities
    if brs and len(brs) >= 2:
        return "品牌对决", cts, brs, regions, cities
    if brs:
        return "品牌（全局）", cts, brs, regions, cities
    if n_ct == 1:
        if CHANNEL_RE.search(kw):
            return "国家·落地渠道", cts, brs, regions, cities
        if COMPARE_RE.search(kw):
            return "国家·对比", cts, brs, regions, cities
        if DEVICE_RE.search(kw):
            return "国家·设备兼容", cts, brs, regions, cities
        if PRICE_RE.search(kw):
            return "国家·价格/交易", cts, brs, regions, cities
        if SPEC_RE.search(kw):
            return "国家·规格/流量", cts, brs, regions, cities
        if re.search(r"\b(network|networks|carrier|carriers|coverage|signal|5g|4g|speed)\b", kw):
            return "国家·网络覆盖", cts, brs, regions, cities
        return "国家·核心", cts, brs, regions, cities
    if cities:
        return "城市", cts, brs, regions, cities
    if regions:
        return "区域", cts, brs, regions, cities
    if GENERIC.search(kw):
        return "通用·全球", cts, brs, regions, cities
    if COMPARE_RE.search(kw):
        return "通用·对比", cts, brs, regions, cities
    if DEVICE_RE.search(kw):
        return "通用·设备兼容", cts, brs, regions, cities
    if PRICE_RE.search(kw):
        return "通用·价格交易", cts, brs, regions, cities
    if SPEC_RE.search(kw):
        return "通用·规则/规格", cts, brs, regions, cities
    if QUESTION_RE.match(kw):
        return "通用·问题", cts, brs, regions, cities
    return "通用·其他", cts, brs, regions, cities


REGION_GUIDE = {"europe": "best-europe-esim", "asia": "best-asia-esim",
                "americas": "best-americas-esim",
                "africa": "best-africa-middle-east-esim",
                "middle east": "best-africa-middle-east-esim",
                "oceania": "best-oceania-esim"}


def route(kw, typ, cts, brs, regions, live):
    """判定归属 URL + 站内现状"""
    def ex(u):
        return "已覆盖" if u in live else "缺口"

    if typ == "品牌×国家" and cts and brs:
        u = f"/compare/{cts[0]['slug']}/{brs[0]}/"
        return u, ex(u), "品牌×国家子页"
    if typ == "品牌（全局）" and brs:
        u = f"/esim-providers/{brs[0]}/"
        return u, ex(u), "品牌 Hub"
    if typ == "品牌对决" and len(brs) >= 2:
        a, b = sorted(brs[:2])
        u = f"/compare/{a}-vs-{b}/"
        return u, ex(u), "对决页"
    if typ.startswith("国家") and cts:
        c = cts[0]
        if typ == "国家·网络覆盖":
            u = f"/networks/{c['slug']}/"
            return u, ex(u), "国家网络页"
        if re.search(r"\b(network|carrier|coverage|5g)\b", kw) and f"/networks/{c['slug']}/" in live:
            u = f"/networks/{c['slug']}/"
            return u, ex(u), "国家网络页"
        if re.search(r"\b(unlimited)\b", kw):
            return f"/compare/{c['slug']}/#plans", "已覆盖", "国家页·无限流量区"
        if re.search(r"(gb|mb|tb|day|days|plan|plans|data)", kw) and PRICE_RE.search(kw):
            return f"/compare/{c['slug']}/#plans", "已覆盖", "国家页·套餐表"
        return f"/compare/{c['slug']}/", ex(f"/compare/{c['slug']}/"), "国家页"
    if typ == "城市":
        return "（无城市页，建议并入国家页）", "缺口", "未建页型（禁区）"
    if typ == "区域":
        if brs:
            return f"/esim-providers/{brs[0]}/", ex(f"/esim-providers/{brs[0]}/"), "品牌 Hub·区域覆盖"
        for r in regions:
            if r in REGION_GUIDE and f"/guides/{REGION_GUIDE[r]}/" in live:
                return f"/guides/{REGION_GUIDE[r]}/", "已覆盖", "区域指南"
        return "（无区域页）", "缺口", "未建页型"
    if typ == "通用·全球":
        return "/guides/", "已覆盖", "通用枢纽"
    # 通用
    if re.search(r"(promo|coupon|discount|code|deals?)", kw):
        return "/esim-deals/", ex("/esim-deals/"), "折扣页"
    if DEVICE_RE.search(kw):
        return "/guides/esim-compatibility-check/", ex("/guides/esim-compatibility-check/"), "兼容指南"
    if re.search(r"(vs|versus|difference|regular sim|physical sim|sim card)", kw):
        return "/guides/esim-vs-physical-sim/", ex("/guides/esim-vs-physical-sim/"), "形态对比指南"
    if re.search(r"(install|activate|set ?up|apn|qr)", kw):
        return "/guides/how-to-install-esim/", ex("/guides/how-to-install-esim/"), "安装指南"
    if re.search(r"^(what is|how does)", kw):
        return "/guides/what-is-an-esim/", ex("/guides/what-is-an-esim/"), "概念指南"
    if re.search(r"(how much data|calculator|data need)", kw):
        return "/tools/", ex("/tools/"), "工具页"
    if re.search(r"unlimited", kw):
        return "/research/unlimited-esim/", ex("/research/unlimited-esim/"), "无限流量研究"
    if re.search(r"(price index|cheapest countr|by countr)", kw):
        return "/research/esim-price-index/", ex("/research/esim-price-index/"), "价格指数研究"
    return "/", ex("/"), "首页/枢纽"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--infile", default="kw-scored.csv")
    ap.add_argument("--out", default="kw-collected-2026-10-08.csv")
    args = ap.parse_args()

    countries = load_countries()
    live = set(json.loads((KW / "live-urls.json").read_text(encoding="utf-8")))

    rows = list(csv.DictReader((KW / args.infile).open(encoding="utf-8")))
    print(f"读入补全词 {len(rows)}")

    # 只保留「eSIM/SIM 相关」的补全词
    keep = [r for r in rows if re.search(r"\b(esim|e sim|sim)\b", r["keyword"])]
    print(f"含 esim/sim 的词 {len(keep)}")

    old = set()
    if MATRIX.is_file():
        for r in csv.DictReader(MATRIX.open(encoding="utf-8-sig")):
            old.add(norm(r["长尾关键词"]))
        print(f"旧词库归一后 {len(old)} 词")

    out = []
    for r in keep:
        kw = r["keyword"]
        src = int(r["sources"])
        med = float(r["中位位次"])
        typ, cts, brs, regs, cities = classify(kw, countries)
        url, status, ptype = route(kw, typ, cts, brs, regs, live)
        out.append({
            "keyword": kw, "词型": typ, "需求分": float(r["需求分"]),
            "sources": src, "中位位次": med, "top3次数": int(r["top3次数"]),
            "覆盖国数": int(r["覆盖国数"]), "markets": r["markets"],
            "best_seed": r["best_seed"],
            "归属页型": ptype, "归属URL": url, "站内现状": status,
            "国家": ",".join(c["iso"] for c in cts),
            "国家slug": ",".join(c["slug"] for c in cts),
            "品牌": ",".join(brs),
            "在旧词库": "是" if norm(kw) in old else "否",
        })

    out.sort(key=lambda x: (-x["需求分"], x["keyword"]))
    cols = ["keyword", "词型", "需求分", "sources", "中位位次", "top3次数", "覆盖国数",
            "markets", "best_seed", "归属页型", "归属URL", "站内现状",
            "国家", "国家slug", "品牌", "在旧词库"]
    p = KW / args.out
    with p.open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=cols)
        w.writeheader()
        w.writerows(out)
    print(f"\n主交付物 -> {p.relative_to(ROOT)}（{len(out)} 词）")

    # ---- 统计 ----
    print("\n=== 词型分布（词数 / 需求分中位数）===")
    by = defaultdict(list)
    for o in out:
        by[o["词型"]].append(o["需求分"])
    for k, v in sorted(by.items(), key=lambda x: -len(x[1])):
        import statistics as st
        print(f"  {len(v):5d}  中位{st.median(v):5.1f}  {k}")

    print("\n=== 站内现状 ===")
    stc = defaultdict(int)
    for o in out:
        stc[o["站内现状"]] += 1
    for k, v in sorted(stc.items(), key=lambda x: -x[1]):
        print(f"  {v:5d}  {k}")

    print("\n=== 旧词库是否覆盖 ===")
    om = defaultdict(int)
    for o in out:
        om[o["在旧词库"]] += 1
    for k, v in om.items():
        print(f"  {v:5d}  在旧词库={k}")

    print("\n=== 缺口词（站内无承接页）Top 30 ===")
    gap = [o for o in out if o["站内现状"] == "缺口"]
    for o in gap[:30]:
        print(f'  {o["需求分"]:5.1f}  {o["sources"]:3d}源 国{o["覆盖国数"]:2d}  '
              f'{o["词型"]:10s} {o["keyword"]}')

    print("\n=== 泛化词（覆盖国数 ≥ 40 且无国名）Top 25 —— 全局页的机会 ===")
    gen = [o for o in out if o["覆盖国数"] >= 40 and not o["国家"]]
    for o in gen[:25]:
        print(f'  {o["需求分"]:5.1f}  {o["词型"]:12s} -> {o["归属URL"]:42s} {o["keyword"]}')

    print("\n=== 逐国真需求词（覆盖国数 ≤ 12 且中位位次 ≤ 3）Top 40 ===")
    per = [o for o in out if 0 < o["覆盖国数"] <= 12 and o["中位位次"] <= 3]
    for o in per[:40]:
        print(f'  {o["需求分"]:5.1f}  {o["sources"]:3d}源 国{o["覆盖国数"]:2d} r{o["中位位次"]:4.1f}  '
              f'{o["词型"]:12s} {o["keyword"]}')
    return out


if __name__ == "__main__":
    main()
