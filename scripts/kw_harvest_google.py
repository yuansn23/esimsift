# -*- coding: utf-8 -*-
"""eSIM 长尾词采集 —— Google 通道（2026-10-08 第五十三轮）

方法：Google Suggest（autocomplete）的补全列表由**真实查询频率**驱动 ——
一个短语能出现在补全里，就是「有人这么搜」的实证；位次越前 = 相对热度越高。

★ 为什么必须换掉上一轮的 Bing 通道（用户要求「必须从谷歌搜索获取」）
  Bing 会往几乎所有 eSIM 查询里**注入同一段通用热门块**，导致同一批词被几十个
  毫不相关的种子带出（"buy esim for dubai" 被 57 个种子带出，含 "alosim esim saudi arabia"）。
  Google 的补全**逐查询不同**，注入现象弱得多 —— 这直接决定 sources 这个字段可不可信。

★ 本机网络事实（实测，2026-10-08）
  - 直连 google.* = 超时；DNS 被污染（www.google.com -> 31.13.92.37，Facebook 段）
  - 环境变量 https_proxy=http://127.0.0.1:62216 是**沙箱代理，不通 Google**
  - 本机 127.0.0.1:7890（Clash 混合端口）**可通 Google** —— 脚本必须显式用它，
    否则会静默继承错误的 https_proxy 而全部失败
  - 稳定性实测：连发 40 次 → 36 次 200、4 次超时、**0 次 429**；故用重试 + 适度并发

用法：
  python -X utf8 scripts/kw_harvest_google.py --probe           # 通道自检（3 次请求）
  python -X utf8 scripts/kw_harvest_google.py --smoke           # 2 国冒烟
  python -X utf8 scripts/kw_harvest_google.py                   # 全量
  python -X utf8 scripts/kw_harvest_google.py --markets en-US,en-GB,de-DE
"""
import argparse
import json
import pathlib
import re
import threading
import time
import urllib.parse
import urllib.request
from collections import defaultdict
from concurrent.futures import ThreadPoolExecutor

ROOT = pathlib.Path(__file__).resolve().parent.parent
OUT_DIR = ROOT / "docs" / "keywords" / "google"

PROXY = "http://127.0.0.1:7890"
ENDPOINT = "https://suggestqueries.google.com/complete/search"
UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36")

_lock = threading.Lock()
_done = [0]

# ── 市场：hl 语言 / gl 地理 ────────────────────────────────────────────────
MARKETS = {
    "en-US": ("en", "us"), "en-GB": ("en", "gb"), "en-SG": ("en", "sg"),
    "en-AU": ("en", "au"), "en-CA": ("en", "ca"), "en-IE": ("en", "ie"),
    "de-DE": ("de", "de"),
}
# 主市场跑全量种子，其余跑精简种子（控制请求量）
FULL_MARKETS = {"en-US", "de-DE"}


def read_countries():
    txt = (ROOT / "data" / "countries.toml").read_text(encoding="utf-8")
    out = []
    for b in re.finditer(r"^\[([A-Z]{2})\]\n(.*?)(?=^\[|\Z)", txt, re.M | re.S):
        iso, body = b.group(1), b.group(2)
        nm = re.search(r'name\s*=\s*"([^"]+)"', body)
        sl = re.search(r'slug\s*=\s*"([^"]+)"', body)
        if nm and sl:
            out.append({"iso": iso, "name": nm.group(1), "slug": sl.group(1)})
    return out


def read_brands():
    txt = (ROOT / "data" / "providers.toml").read_text(encoding="utf-8")
    out = []
    for b in re.finditer(r"^\[([a-z0-9]+)\]\n(.*?)(?=^\[|\Z)", txt, re.M | re.S):
        nm = re.search(r'name\s*=\s*"([^"]+)"', b.group(2))
        if nm:
            out.append({"key": b.group(1), "name": nm.group(1)})
    return out


# ★ 种子必须用「用户真会打的名字」。data/countries.toml 的 name 是正式全称
#   （United States / United Kingdom / TÃ¼rkiye），而真实查询用短名（usa / uk / turkey）。
#   上一轮实测代价：用 "United States" 当种子，US 页只采到 99 词、最高分 52.7。
ALIASES = {
    "united-states": ["usa", "us", "america"],
    "united-kingdom": ["uk", "england", "britain"],
    "united-arab-emirates": ["uae", "dubai", "abu dhabi"],
    "south-korea": ["korea", "seoul"],
    "north-korea": ["north korea"],
    "hong-kong": ["hong kong"],
    "macau": ["macau", "macao"],
    "taiwan": ["taiwan", "taipei"],
    "czechia": ["czech republic", "prague"],
    "turkiye": ["turkey", "istanbul"],
    "netherlands": ["netherlands", "holland", "amsterdam"],
    "new-zealand": ["new zealand", "nz"],
    "saudi-arabia": ["saudi arabia", "ksa", "riyadh"],
    "south-africa": ["south africa", "cape town"],
    "costa-rica": ["costa rica"],
    "vietnam": ["vietnam", "viet nam"],
    "philippines": ["philippines", "manila"],
    "indonesia": ["indonesia", "bali"],
    "thailand": ["thailand", "bangkok"],
    "mexico": ["mexico", "cancun"],
    "switzerland": ["switzerland"],
    "greece": ["greece", "athens"],
    "portugal": ["portugal", "lisbon"],
    "spain": ["spain", "barcelona"],
    "italy": ["italy", "rome"],
    "france": ["france", "paris"],
    "germany": ["germany", "berlin"],
    "japan": ["japan", "tokyo"],
    "china": ["china", "beijing"],
    "singapore": ["singapore"],
    "malaysia": ["malaysia", "kuala lumpur"],
    "australia": ["australia", "sydney"],
    "canada": ["canada", "toronto"],
    "india": ["india", "delhi"],
    "brazil": ["brazil", "rio"],
    "argentina": ["argentina", "buenos aires"],
    "peru": ["peru", "lima"],
    "chile": ["chile", "santiago"],
    "colombia": ["colombia", "bogota"],
    "egypt": ["egypt", "cairo"],
    "morocco": ["morocco", "marrakech"],
    "kenya": ["kenya", "nairobi"],
    "tanzania": ["tanzania", "zanzibar"],
    "jordan": ["jordan"],
    "qatar": ["qatar", "doha"],
    "ireland": ["ireland", "dublin"],
    "austria": ["austria", "vienna"],
    "belgium": ["belgium", "brussels"],
    "croatia": ["croatia", "dubrovnik"],
    "iceland": ["iceland", "reykjavik"],
    "norway": ["norway", "oslo"],
    "sweden": ["sweden", "stockholm"],
    "denmark": ["denmark", "copenhagen"],
    "finland": ["finland", "helsinki"],
    "poland": ["poland", "warsaw"],
    "hungary": ["hungary", "budapest"],
    "romania": ["romania", "bucharest"],
    "bulgaria": ["bulgaria", "sofia"],
    "serbia": ["serbia", "belgrade"],
    "albania": ["albania", "tirana"],
    "georgia": ["georgia", "tbilisi"],
    "armenia": ["armenia", "yerevan"],
    "uzbekistan": ["uzbekistan", "tashkent"],
    "kazakhstan": ["kazakhstan", "almaty"],
    "mongolia": ["mongolia"],
    "nepal": ["nepal", "kathmandu"],
    "sri-lanka": ["sri lanka", "colombo"],
    "bangladesh": ["bangladesh", "dhaka"],
    "pakistan": ["pakistan", "karachi"],
    "cambodia": ["cambodia", "siem reap"],
    "laos": ["laos", "luang prabang"],
    "myanmar": ["myanmar", "yangon"],
    "brunei": ["brunei"],
    "fiji": ["fiji"],
    "maldives": ["maldives", "male"],
    "mauritius": ["mauritius"],
    "seychelles": ["seychelles"],
    "namibia": ["namibia", "windhoek"],
    "botswana": ["botswana"],
    "ghana": ["ghana", "accra"],
    "nigeria": ["nigeria", "lagos"],
    "rwanda": ["rwanda", "kigali"],
    "uganda": ["uganda"],
    "ethiopia": ["ethiopia"],
    "senegal": ["senegal", "dakar"],
    "tunisia": ["tunisia"],
    "algeria": ["algeria"],
    "israel": ["israel", "tel aviv"],
    "lebanon": ["lebanon", "beirut"],
    "bahrain": ["bahrain"],
    "kuwait": ["kuwait"],
    "oman": ["oman", "muscat"],
    "panama": ["panama"],
    "guatemala": ["guatemala"],
    "belize": ["belize"],
    "cuba": ["cuba", "havana"],
    "dominican-republic": ["dominican republic", "punta cana"],
    "jamaica": ["jamaica"],
    "puerto-rico": ["puerto rico"],
    "bahamas": ["bahamas"],
    "ecuador": ["ecuador", "quito"],
    "bolivia": ["bolivia", "la paz"],
    "uruguay": ["uruguay", "montevideo"],
    "paraguay": ["paraguay"],
    "venezuela": ["venezuela"],
    "suriname": ["suriname"],
    "guyana": ["guyana"],
    "greenland": ["greenland"],
    "malta": ["malta"],
    "cyprus": ["cyprus"],
    "luxembourg": ["luxembourg"],
    "slovakia": ["slovakia", "bratislava"],
    "slovenia": ["slovenia", "ljubljana"],
    "estonia": ["estonia", "tallinn"],
    "latvia": ["latvia", "riga"],
    "lithuania": ["lithuania", "vilnius"],
    "moldova": ["moldova"],
    "ukraine": ["ukraine", "kyiv"],
    "russia": ["russia", "moscow"],
}

COUNTRY_PATS_FULL = [
    "esim {c}", "esim for {c}", "best esim for {c}", "cheapest esim for {c}",
    "esim {c} unlimited", "{c} esim unlimited data", "esim {c} price",
    "esim {c} plans", "esim {c} 10gb", "unlimited data esim {c}",
    "does esim work in {c}", "esim {c} vs sim", "{c} sim card for tourists",
    "how to get an esim for {c}", "esim {c} airport", "esim {c} for iphone",
    "esim coverage in {c}", "is esim available in {c}", "esim {c} reddit",
    "cheap esim {c}", "best esim {c} 2026", "{c} esim card",
    "esim for {c} review", "do i need an esim for {c}", "{c} esim coverage map",
    "which esim is best for {c}", "esim {c} tourist",
]
COUNTRY_PATS_LITE = [
    "esim {c}", "esim for {c}", "best esim for {c}", "cheapest esim for {c}",
    "{c} esim unlimited", "esim {c} price", "does esim work in {c}",
    "{c} sim card for tourists", "which esim is best for {c}",
]
BRAND_PATS = [
    "{b} esim", "{b} esim review", "{b} esim plans", "{b} esim coverage",
    "{b} esim promo code", "is {b} esim good", "{b} esim vs airalo",
    "{b} esim price", "{b} esim unlimited", "{b} esim japan",
]
GLOBAL_SEEDS = [
    "esim", "esim deals", "esim plans", "esim vs sim", "esim vs pocket wifi",
    "best esim", "cheapest esim", "unlimited esim", "esim compatible phones",
    "how to install esim", "how to activate esim", "what is an esim",
    "esim for europe", "esim for asia", "esim for cruise", "esim for international travel",
    "travel esim", "esim promo code", "esim discount code", "is esim worth it",
    "esim data plan", "esim no contract", "esim for iphone", "esim for android",
    "esim with phone number", "esim hotspot", "esim hotspot tethering",
    "esim speed", "esim coverage map", "esim top up",
    "esim mexico", "esim turkey", "esim italy", "esim spain", "esim france",
    "esim germany", "esim portugal", "esim croatia", "esim iceland",
    "best esim 2026", "esim egypt", "esim morocco", "esim canada",
    "esim turkey", "esim uk", "esim usa",
]
# 区域/多国词（站内有 /guides/best-{region}-esim/）
REGION_SEEDS = [
    "esim europe", "best esim for europe", "europe esim unlimited",
    "esim asia", "best esim for asia", "asia esim unlimited",
    "esim south america", "best esim for south america",
    "esim africa", "best esim for africa",
    "esim north america", "esim central america", "esim caribbean",
    "esim middle east", "esim scandinavia", "esim balkans",
    "esim southeast asia", "esim latin america", "esim oceania",
    "esim for europe and usa", "esim world", "global esim", "international esim",
]
CITY_SEEDS = [
    "dubai", "tokyo", "osaka", "seoul", "bangkok", "phuket", "bali",
    "kuala lumpur", "hanoi", "taipei", "hong kong", "shanghai", "beijing",
    "london", "paris", "rome", "barcelona", "madrid", "lisbon", "amsterdam",
    "berlin", "prague", "vienna", "istanbul", "cairo", "marrakech",
    "new york", "las vegas", "miami", "los angeles", "orlando", "hawaii",
    "cancun", "mexico city", "toronto", "vancouver", "rio de janeiro",
    "buenos aires", "sydney", "melbourne", "auckland", "cape town",
    "maldives", "zanzibar", "athens", "dublin", "edinburgh", "reykjavik",
]
COUNTRY_PAIRS = [
    ("usa", "canada"), ("usa", "mexico"), ("uk", "france"), ("france", "italy"),
    ("italy", "greece"), ("spain", "portugal"), ("germany", "austria"),
    ("switzerland", "italy"), ("netherlands", "belgium"),
    ("japan", "south korea"), ("hong kong", "china"), ("singapore", "malaysia"),
    ("singapore", "indonesia"), ("thailand", "vietnam"), ("australia", "new zealand"),
    ("uae", "qatar"), ("turkey", "greece"), ("egypt", "jordan"),
    ("kenya", "tanzania"), ("south africa", "namibia"), ("brazil", "argentina"),
    ("peru", "chile"), ("costa rica", "panama"), ("ireland", "uk"),
    ("denmark", "sweden"), ("norway", "sweden"), ("croatia", "italy"),
    ("india", "sri lanka"), ("philippines", "vietnam"), ("usa", "europe"),
    ("japan", "thailand"), ("vietnam", "cambodia"), ("japan", "vietnam"),
]
# 高意图修饰词（真实长尾）
INTENT_SEEDS = [
    "esim for tourists", "esim for students", "esim for business travel",
    "esim for digital nomad", "esim for backpacking", "esim for cruise ship",
    "esim for road trip", "esim for family", "esim for kids",
    "esim data only", "esim voice calls", "esim sms",
    "esim prepaid", "esim pay as you go", "esim no contract",
    "esim free trial", "esim esim", "best esim deals",
    "esim for long stay", "esim for 1 month", "esim for 2 weeks",
    "esim for 3 days", "esim for 1 week", "esim cheap data",
    "esim 5g", "esim 4g", "esim speed test", "esim latency",
]


def _http(url, tries=4):
    """走显式代理取 JSON。返回 (parsed, ok)。"""
    op = urllib.request.build_opener(
        urllib.request.ProxyHandler({"http": PROXY, "https": PROXY}))
    for i in range(tries):
        try:
            req = urllib.request.Request(url, headers={
                "User-Agent": UA, "Accept-Language": "en-US,en;q=0.9"})
            raw = op.open(req, timeout=15).read().decode("utf-8", "replace")
            return json.loads(raw), True
        except Exception:
            if i == tries - 1:
                return None, False
            time.sleep(0.8 * (i + 1))
    return None, False


def suggest(seed, mkt):
    """Google Suggest。client=firefox 返回 [query, [sugg...], [], {...}]。"""
    hl, gl = MARKETS[mkt]
    url = (f"{ENDPOINT}?client=firefox&hl={hl}&gl={gl}"
           f"&q={urllib.parse.quote(seed)}")
    data, ok = _http(url)
    if not ok or not isinstance(data, list) or len(data) < 2:
        return None
    out = []
    for s in data[1]:
        s = (s or "").strip().lower()
        # ★ 种子回显：Google 把查询本身放在第 0 位
        if not s or s == seed.strip().lower():
            continue
        out.append(s)
    return out


def build_jobs(countries, brands, markets):
    jobs = []
    for mkt in markets:
        full = mkt in FULL_MARKETS
        pats = COUNTRY_PATS_FULL if full else COUNTRY_PATS_LITE
        for c in countries:
            forms = ALIASES.get(c["slug"], [c["name"].lower()])
            # 主形态跑全部模式；别名只跑核心模式（控制量）
            for p in pats:
                jobs.append((p.format(c=forms[0]), mkt, "country:" + c["iso"]))
            for f in forms[1:]:
                for p in ("esim {c}", "esim for {c}", "best esim for {c}", "{c} esim"):
                    jobs.append((p.format(c=f), mkt, "country:" + c["iso"]))
        for b in brands:
            bn = b["name"].lower()
            for p in (BRAND_PATS if full else BRAND_PATS[:5]):
                jobs.append((p.format(b=bn), mkt, "brand:" + b["key"]))
        if full:
            for c in countries:
                f = ALIASES.get(c["slug"], [c["name"].lower()])[0]
                for b in brands:
                    bn = b["name"].lower()
                    jobs.append((f"{bn} esim {f}", mkt, "brandxcountry:" + b["key"]))
        for g in GLOBAL_SEEDS + REGION_SEEDS + INTENT_SEEDS:
            jobs.append((g, mkt, "global"))
        if full:
            for city in CITY_SEEDS:
                jobs.append((f"esim {city}", mkt, "city:" + city))
                jobs.append((f"esim for {city}", mkt, "city:" + city))
            for a, b2 in COUNTRY_PAIRS:
                jobs.append((f"esim for {a} and {b2}", mkt, "pair"))
                jobs.append((f"best esim for {a} and {b2}", mkt, "pair"))
    seen, uniq = set(), []
    for s, m, t in jobs:
        k = (s, m)
        if k in seen:
            continue
        seen.add(k)
        uniq.append((s, m, t))
    return uniq


def probe():
    print(f"代理 {PROXY}")
    for s in ["esim for japan", "esim usa", "airalo esim singapore"]:
        r = suggest(s, "en-US")
        print(f"  {s!r:32s} -> {'FAIL' if r is None else len(r)} 条"
              + (f"  样例: {r[:3]}" if r else ""))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--probe", action="store_true")
    ap.add_argument("--smoke", action="store_true")
    ap.add_argument("--markets", default="en-US,en-GB,en-SG,en-AU,de-DE")
    ap.add_argument("--workers", type=int, default=5)
    ap.add_argument("--tag", default="")
    args = ap.parse_args()

    if args.probe:
        probe()
        return

    countries = read_countries()
    brands = read_brands()
    markets = [m.strip() for m in args.markets.split(",") if m.strip()]
    for m in markets:
        if m not in MARKETS:
            raise SystemExit(f"未知市场 {m}，可选 {list(MARKETS)}")
    if args.smoke:
        countries = countries[:2]
        markets = markets[:1]

    jobs = build_jobs(countries, brands, markets)
    print(f"Google 通道 | 种子 {len(jobs)}（{len(countries)} 国 × {len(brands)} 品牌 × {len(markets)} 市场）",
          flush=True)

    results, fails = {}, []
    t0 = time.time()

    def work(job):
        seed, mkt, tag = job
        sg = suggest(seed, mkt)
        with _lock:
            _done[0] += 1
            if _done[0] % 250 == 0:
                print(f"  {_done[0]}/{len(jobs)}  {time.time()-t0:.0f}s  失败={len(fails)}",
                      flush=True)
            if sg is None:
                fails.append(job)
            else:
                results[(seed, mkt)] = sg

    with ThreadPoolExecutor(max_workers=args.workers) as ex:
        list(ex.map(work, jobs))

    agg = {}
    for (seed, mkt), sugg in results.items():
        for i, s in enumerate(sugg):
            rec = agg.setdefault(s, {"kw": s, "sources": set(), "best_rank": 99,
                                     "markets": set(), "best_seed": None})
            rec["sources"].add(seed)
            rec["markets"].add(mkt)
            if i + 1 < rec["best_rank"]:
                rec["best_rank"], rec["best_seed"] = i + 1, seed

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    suf = args.tag or (".smoke" if args.smoke else "")
    (OUT_DIR / f"raw_google_suggest{suf}.json").write_text(json.dumps(
        {"generated": time.strftime("%Y-%m-%dT%H:%M:%S"),
         "channel": "google_suggest", "endpoint": ENDPOINT, "proxy": PROXY,
         "markets": markets, "seeds_total": len(jobs), "seeds_ok": len(results),
         "seeds_failed": len(fails),
         "failed_seeds": [{"seed": s, "market": m} for s, m, _ in fails],
         "tags": {f"{s}|{m}": t for s, m, t in jobs},
         "suggestions": {f"{s}|{m}": v for (s, m), v in sorted(results.items())}},
        ensure_ascii=False, indent=1), encoding="utf-8")

    rows = sorted(agg.values(), key=lambda r: (-len(r["sources"]), r["best_rank"], r["kw"]))
    with (OUT_DIR / f"kw-google-suggest{suf}.csv").open("w", encoding="utf-8", newline="") as f:
        f.write("keyword,sources,best_rank,markets,best_seed\n")
        for r in rows:
            k = '"%s"' % r["kw"].replace('"', '""')
            f.write(f'{k},{len(r["sources"])},{r["best_rank"]},'
                    f'"{"|".join(sorted(r["markets"]))}","{r["best_seed"]}"\n')

    print(f"\n采集完成：{len(results)}/{len(jobs)} 有响应，失败 {len(fails)}"
          f"（{100*len(results)/max(1,len(jobs)):.1f}% 覆盖）")
    print(f"唯一补全词 {len(rows)}")
    print("\n--- 被 ≥15 个种子带出（最主流）---")
    for r in rows[:30]:
        print(f'  {len(r["sources"]):4d}源 r{r["best_rank"]:2d}  {r["kw"]}')


if __name__ == "__main__":
    main()
