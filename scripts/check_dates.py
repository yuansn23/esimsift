#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""check_dates.py —— 产物「域名」与「日期一致性」守卫。

三件真实事故撑起了这个脚本：

A. 域名污染
   本地 `hugo server` 会把 baseURL 的 host 换成 localhost:<端口>（端口繁忙时 Hugo
   还会自己挑一个随机端口）。一旦这个 server 写了 public/，产物里就带上
   `http://localhost:55171` —— 136 个文件受影响，canonical 与 sitemap 一起中招。
   直接部署等于告诉 Google「本站地址是 localhost」。

B. 日期自相矛盾
   同一张页面有三处机器可读的日期，必须同源：
       · 页面可见文案「Prices checked <日期>」
       · JSON-LD dateModified
       · sitemap <lastmod>
   2026-10-04 实测 /compare/united-states/alosim/ 一边印 Oct 4、一边 sitemap 声明
   09-30，且「今天核过价」本身不实（价格是 09-30 抓的）。

C. 半截产物
   构建被中断（Ctrl-C / 超时）时 public/ 可能停在「清空了一半、没写完」的状态，
   看着是新的、实际整段页面缺失。**所有既有校验都不报错** —— 它们清一色是
   「有则查」，没有一个会问「该有的在不在」。这是唯一能发现它的地方。

── 期望值怎么算（与模板同一套口径，独立重实现）────────────────────────────
  品牌 Hub  /esim-providers/<key>/
     页级日期 = max(该品牌全部市场的最新 price checked,
                    该品牌 providers.toml 的 profile_checked)
     价格文案 = 该品牌全部市场的最新 price checked      ← ★ 不是页级日期！
     因为 Hub 页内容 = 价格 + 品牌档案（简介/热点/FUP/充值/折扣码）。
     只改档案时页级日期该前移，而「Prices … as checked on」是价格专属表述，
     必须留在价格核对日 —— 合并成一个日期就会写出不实陈述。
  品牌×国家子页 /compare/<国>/<品牌>/
     页级日期 = 价格文案日期 = 该品牌在该国的 checked（子页文案全是价格专属）
  A-vs-B 对比页 /compare/<a>-vs-<b>/
     三者 = max(a、b 两个品牌各自全部市场的最新 checked)
     （必须与 vs-agg.checkedDate 完全同口径，否则一个品牌刷新会带跑 28 张 vs 页）
  国家 Hub /compare/<国>/
     三者 = 该国全部品牌的最大 checked
  编辑页 /guides/*、/research/*
     只查 lastmod == dateModified。它们的**文章日期**与**数据快照日**本来就该不同
     （文章 10-02 写、价格 09-30 核），强行拉平会掩盖真实信息。

退出码：0 全部通过；1 有违规。
"""
from __future__ import annotations

import collections
import io
import pathlib
import re
import sys

try:
    import tomllib
except ImportError:  # pragma: no cover
    import tomli as tomllib  # type: ignore

ROOT = pathlib.Path(__file__).resolve().parent.parent
PUB = ROOT / "public"

RE_LOC = re.compile(r"<url><loc>([^<]*)</loc>(?:<lastmod>([^<]*)</lastmod>)?</url>")
RE_DATEMOD = re.compile(r'"dateModified"\s*:\s*"([^"]+)"')

MONTHS = {m: i + 1 for i, m in enumerate(
    "Jan Feb Mar Apr May Jun Jul Aug Sep Oct Nov Dec".split())}
# 日期可见形态有两个（`time.Format ":date_medium"` 跟着站点语言走）：
#   en → "Oct 7, 2026"      de → "07.10.2026"
# 德语那支**从 D9 起才真正进入检查范围**（德语页现在是 noindex、不进 sitemap），
# 但口径必须先写对：等 D9 解禁时守卫要直接可用，而不是那时才发现它不认德语日期。
_DAY_EN = r"(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]* \d{1,2}, \d{4}"
_DAY_DE = r"\d{1,2}\.\d{1,2}\.\d{4}"
DAY = r"\b(" + _DAY_EN + r")"
RE_ANY_DATE = re.compile(r"\b(?:" + _DAY_EN + r"|" + _DAY_DE + r")")

# ★ 日期文案分两组，不能混。品牌 Hub 上这两组的值**故意不同**：
#   「Last updated <d>」是通用表述 → 页级日期（= max(价格核对日, 档案核对日)）
#   「prices … as checked on <d>」是价格专属表述 → 只能等于价格核对日
#   混成一组就会把正确的输出判成违规（第一版就是这么误报 8 条的）。
RE_PAGE_DATE = re.compile(r"(?:Last updated)\s*[^<]{0,60}?" + DAY)
RE_PRICE_DATE = re.compile(
    r"(?:Prices checked|Prices verified|Last checked|checked on|Prices dated"
    r"|prices checked|prices verified|rebuilt)\s*[^<]{0,60}?" + DAY)

BRAND_HUB = re.compile(r"^/esim-providers/([^/]+)/$")
PROV_SUB = re.compile(r"^/compare/([^/]+)/([^/]+)/$")
VS_PAGE = re.compile(r"^/compare/([^/]+)-vs-([^/]+)/$")
COUNTRY_HUB = re.compile(r"^/compare/([^/]+)/$")
EDIT_PAGE = re.compile(r"^/(?:guides|research)/")
INDEX_PAGE = re.compile(r"^/(?:compare|esim-providers)/$")
# /networks/*（2026-10-09 第五十八轮补）—— 这一个页型此前**完全不在守卫范围内**，
# 所以 layouts/networks/single.html 把徽章日期写成 `now`（构建日）后，没有任何检查报错：
# 页面印 "Updated Oct 9"、sitemap 声明 2026-10-07，两个机器可读面互相打脸却全绿。
# 子页（/networks/<slug>/）只显示数据核对日，故"页面上出现的每一个日期都必须等于它"；
# 索引页（/networks/）正文里有一句散文日期（示例日期），不能套这条，按编辑页口径只查 dateModified。
NETWORKS_SUB = re.compile(r"^/networks/([^/]+)/$")
NETWORKS_INDEX = re.compile(r"^/networks/$")

MAX_SHOW = 8


def base_url() -> str:
    txt = io.open(ROOT / "hugo.toml", encoding="utf-8").read()
    m = re.search(r'^baseURL\s*=\s*"([^"]+)"', txt, re.M)
    if not m:
        sys.exit("错误：hugo.toml 里找不到 baseURL")
    return m.group(1)


def load_data():
    """→ (plans, profile)：plans[brand][iso] = checked；profile[brand] = profile_checked"""
    plans: dict[str, dict[str, str]] = {}
    for p in sorted((ROOT / "data" / "plans").glob("*.toml")):
        with io.open(p, "rb") as f:
            d = tomllib.load(f)
        plans[p.stem] = {iso: blk.get("checked", "")
                         for iso, blk in d.items() if isinstance(blk, dict)}
    with io.open(ROOT / "data" / "providers.toml", "rb") as f:
        prov = tomllib.load(f)
    profile = {k: (v.get("profile_checked") or "")
               for k, v in prov.items() if isinstance(v, dict)}
    return plans, profile


def load_networks_iso() -> dict[str, str]:
    """→ {slug: ISO}：从 content/en/networks/<slug>.md 的 front matter 读 `iso: "CA"`。

    /networks/<slug>/ 的期望日期要按 ISO 聚合，而 URL 里只有 slug，
    所以必须从内容文件把两者接上。（读 front matter 而不是写死一张表：
    新增一个目的地就是加一个 md，守卫不该跟着改。）
    """
    out: dict[str, str] = {}
    for p in sorted((ROOT / "content" / "en" / "networks").glob("*.md")):
        if p.stem.startswith("_"):
            continue
        txt = io.open(p, encoding="utf-8", errors="ignore").read()
        m = re.search(r'^iso:\s*"?([A-Za-z]{2})"?', txt, re.M)
        if m:
            out[p.stem] = m.group(1).upper()
    return out


def newest(values) -> str:
    vals = [v for v in values if v]
    return max(vals) if vals else ""


def brand_newest(plans, key: str) -> str:
    return newest(plans.get(key, {}).values())


def norm_visible(s: str):
    m = re.match(r"([A-Z][a-z]{2})[a-z]* (\d{1,2}), (\d{4})", s)
    if m:
        return "%s-%02d-%02d" % (m.group(3), MONTHS[m.group(1)], int(m.group(2)))
    m = re.match(r"(\d{1,2})\.(\d{1,2})\.(\d{4})", s)   # 德语 07.10.2026
    if m:
        return "%s-%02d-%02d" % (m.group(3), int(m.group(2)), int(m.group(1)))
    return None


def check_host(base: str) -> list[str]:
    """A. public/ 不得含 localhost；sitemap 的 host 必须等于 baseURL 的 host。"""
    errs: list[str] = []
    host = re.sub(r"^https?://", "", base).split("/")[0]
    scheme = base.split("://")[0]

    hits: list[str] = []
    for p in PUB.rglob("*"):
        if p.suffix not in (".html", ".xml", ".json", ".txt"):
            continue
        try:
            t = io.open(p, encoding="utf-8", errors="ignore").read()
        except OSError:
            continue
        if "localhost" in t:
            hits.append(str(p.relative_to(PUB)))
    if hits:
        errs.append(f"[A] {len(hits)} 个产物含 localhost —— 本地 hugo server 的 "
                    f"baseURL 泄漏进了 public/（重新跑 npm run build 即可修复）：")
        errs += [f"      · {h}" for h in hits[:MAX_SHOW]]
        if len(hits) > MAX_SHOW:
            errs.append(f"      … 其余 {len(hits) - MAX_SHOW} 个")

    sm = PUB / "sitemap.xml"
    if sm.exists():
        raw = io.open(sm, encoding="utf-8").read()
        for m in RE_LOC.finditer(raw):
            loc = m.group(1)
            if not loc.startswith(scheme + "://" + host):
                errs.append(f"[A] sitemap <loc> 与 baseURL 不同源：{loc}（期望 {base}…）")
                break
    return errs


def check_dates(base: str, plans, profile, net_iso) -> list[str]:
    sm = PUB / "sitemap.xml"
    if not sm.exists():
        return ["[B] public/sitemap.xml 不存在 —— 先跑 hugo"]
    raw = io.open(sm, encoding="utf-8").read()

    fresh = newest(brand_newest(plans, k) for k in plans)
    errs: list[str] = []
    stats = collections.Counter()
    root = base.rstrip("/")

    for m in RE_LOC.finditer(raw):
        loc, lastmod = m.group(1), (m.group(2) or "")[:10]
        url = loc[len(root):] if loc.startswith(root) else loc
        if not url.startswith("/"):
            url = "/" + url.lstrip("/")

        # ── 归类 + 算期望值 ──────────────────────────────────────────
        edit = bool(EDIT_PAGE.match(url))
        page_exp = price_exp = ""
        if (mm := BRAND_HUB.match(url)):
            key = mm.group(1)
            price_exp = brand_newest(plans, key)
            page_exp = newest([price_exp, profile.get(key, "")])
            kind = "brand_hub"
        elif (mm := PROV_SUB.match(url)):
            iso, key = mm.group(1), mm.group(2)
            if key not in plans:
                continue
            price_exp = page_exp = plans[key].get(iso, "")
            kind = "prov_sub"
        elif (mm := VS_PAGE.match(url)):
            a, b = mm.group(1), mm.group(2)
            price_exp = page_exp = newest([brand_newest(plans, a), brand_newest(plans, b)])
            kind = "vs"
        elif (mm := COUNTRY_HUB.match(url)):
            iso = mm.group(1)
            price_exp = page_exp = newest(plans[k].get(iso, "") for k in plans)
            kind = "country_hub"
        elif INDEX_PAGE.match(url):
            price_exp = page_exp = fresh
            kind = "index"
        elif (mm := NETWORKS_SUB.match(url)):
            # /networks/<slug>/ —— 与 country_hub 同一口径（同一批数据、同一个 country-stats）。
            iso = net_iso.get(mm.group(1), "")
            if not iso:
                continue          # 认不出 ISO 就不断言（新增页漏写 iso 由别处发现）
            price_exp = page_exp = newest(plans[k].get(iso, "") for k in plans)
            kind = "networks_sub"
        elif NETWORKS_INDEX.match(url):
            # /networks/ —— 正文含一句示例日期（不是数据日期），只查 dateModified ↔ lastmod。
            kind = "networks_index"
            edit = True
        elif edit:
            kind = "edit"
        else:
            continue

        stats[kind] += 1
        page_file = PUB / url.lstrip("/") / "index.html"
        if not page_file.exists():
            continue  # 交给断言 C
        html = io.open(page_file, encoding="utf-8", errors="ignore").read()
        errs += page_date_errs(url, kind, html, lastmod, page_exp, price_exp)

    print("  页型：" + "、".join(f"{k}={stats[k]}" for k in sorted(stats)))
    return errs


def page_date_errs(url: str, kind: str, html: str, lastmod: str,
                   page_exp: str, price_exp: str) -> list[str]:
    """单页的日期一致性断言（断言 B 的内核）。

    抽成独立函数只有一个理由：**让 `--selftest` 能直接打它**。
    守卫的价值 = 「注入一个反例，它必须变红」。做不到这一点的检查，
    通过与否都说明不了什么（2026-10-09 的 now 回归就是「看起来在查、其实没查」）。
    """
    errs: list[str] = []

    if kind == "edit" or kind == "networks_index":
        # 编辑页（guides/research）与 networks 索引页：自身有文章日期，
        # 只要求它自洽（dateModified ↔ lastmod），不拉平到数据日期。
        for dm in sorted(set(RE_DATEMOD.findall(html))):
            if lastmod and dm[:10] != lastmod:
                errs.append(f"[B] {url} dateModified={dm[:10]} ≠ sitemap lastmod={lastmod}")
        return errs

    if lastmod and page_exp and lastmod != page_exp:
        errs.append(f"[B] {url} sitemap lastmod={lastmod} ≠ 期望页级日期={page_exp}")
    for dm in sorted(set(RE_DATEMOD.findall(html))):
        if page_exp and dm[:10] != page_exp:
            errs.append(f"[B] {url} dateModified={dm[:10]} ≠ 期望页级日期={page_exp}")
    # 通用日期（如「Last updated」）必须等于页级日期
    pg = {norm_visible(x) for x in RE_PAGE_DATE.findall(html)}
    pg.discard(None)
    for v in sorted(pg):
        if page_exp and v != page_exp:
            errs.append(f"[B] {url} 页面可见通用日期={v} ≠ 期望页级日期={page_exp}")
    # 价格专属日期必须等于价格日期（品牌 Hub 上它与页级日期不同，是刻意的）
    pr = {norm_visible(x) for x in RE_PRICE_DATE.findall(html)}
    pr.discard(None)
    for v in sorted(pr):
        if price_exp and v != price_exp:
            errs.append(f"[B] {url} 页面可见「价格核对日」={v} ≠ 期望价格日期={price_exp}")
    # networks 子页：页面上出现的**每一个**日期都必须是数据核对日。
    # 这条比上面两条严 —— 不靠标签识别，直接扫全部日期形态。理由是
    # /networks/<国>/ 页面上只存在一种日期（数据核对日，实测 12 页各 1 个），
    # 所以「出现第二个日期」本身就是异常，不需要先猜它贴着什么标签。
    # 2026-10-09 的 now 回归（徽章印构建日）正是被这条抓住的。
    if kind == "networks_sub":
        for v in sorted({norm_visible(x) for x in RE_ANY_DATE.findall(html)} - {None}):
            if page_exp and v != page_exp:
                errs.append(f"[B] {url} 页面可见日期={v} ≠ 期望数据核对日={page_exp}"
                            "（/networks/ 子页只应出现数据核对日；印出构建日即为 now 回归）")
    return errs


def check_completeness(base: str) -> list[str]:
    """C. sitemap 里声明的每个 URL 都必须真的有产物。"""
    sm = PUB / "sitemap.xml"
    if not sm.exists():
        return ["[C] public/sitemap.xml 不存在 —— 先跑 hugo"]
    raw = io.open(sm, encoding="utf-8").read()
    root = base.rstrip("/")
    missing: list[str] = []
    total = 0
    for m in RE_LOC.finditer(raw):
        loc = m.group(1)
        if not loc.startswith(root):
            continue
        total += 1
        rel = loc[len(root):].lstrip("/")
        p = PUB / rel / "index.html" if (not rel or rel.endswith("/")) else PUB / rel
        if not p.exists():
            missing.append("/" + rel)
    print(f"  完整性：sitemap 声明 {total} 个 URL")
    if missing:
        errs = [f"[C] {len(missing)} 个 sitemap URL 没有对应产物 —— "
                f"public/ 可能是被中断的半截构建，重跑 npm run build："]
        errs += [f"      · {u}" for u in missing[:MAX_SHOW]]
        if len(missing) > MAX_SHOW:
            errs.append(f"      … 其余 {len(missing) - MAX_SHOW} 个")
        return errs
    return []


def selftest() -> int:
    """注入反例，证明断言真的会红。

    ★ 纪律（2026-10-04 起，见 PROJECT.md §14）：**写完守卫必须自测**。
      「只加断言、不证明它会红」等于把检查改瞎 —— 一个永远返回 [] 的检查
      和「没有这个检查」在 CI 里长得一模一样。

    前 4 条是**反例**（必须报错），后 4 条是**正例**（必须不报错）。
    正例同样重要：守卫最容易的坏法不是漏报，而是**误报** ——
    误报会逼着人给检查加白名单，加着加着检查就废了。
    """
    OFF = '<span class="kicker">Canada</span><p>Sources: Canada, August 2026, ' \
          'Mobile Network Experience Report</p>'
    cases = [
        # ── 反例：必须报错 ────────────────────────────────────────────
        ("networks 子页徽章印构建日（2026-10-09 now 回归）", "/networks/canada/",
         "networks_sub", '<span class="badge">Updated Oct 9, 2026</span>',
         "2026-10-07", "2026-10-07", "2026-10-07", True),
        ("networks 子页 sitemap lastmod 与数据脱钩", "/networks/canada/",
         "networks_sub", '<span class="badge">Updated Oct 7, 2026</span>',
         "2026-10-03", "2026-10-07", "2026-10-07", True),
        ("networks 子页德语徽章印错误日期（D9 后德语页进 sitemap 时会走这条）", "/de/networks/canada/",
         "networks_sub", '<span class="badge">Aktualisiert am 09.10.2026</span>',
         "2026-10-07", "2026-10-07", "2026-10-07", True),
        ("prov_sub 价格文案日期不符（回归：重构后既有断言仍有效）", "/compare/canada/airalo/",
         "prov_sub", '<p>Prices verified Oct 4, 2026</p>',
         "2026-10-07", "2026-09-30", "2026-09-30", True),
        # ── 正例：必须不报错 ──────────────────────────────────────────
        ("networks 子页三处同源（正确产物）", "/networks/canada/",
         "networks_sub",
         '<span class="badge">Updated Oct 7, 2026</span>'
         '<p>at the Oct 7, 2026 snapshot. The lowest price…</p>' + OFF,
         "2026-10-07", "2026-10-07", "2026-10-07", False),
        ("networks 子页德语形态（07.10.2026）被正确识别", "/de/networks/canada/",
         "networks_sub", '<span class="badge">Aktualisiert am 07.10.2026</span>',
         "2026-10-07", "2026-10-07", "2026-10-07", False),
        ("networks 索引页的散文日期（April 1, 2026）不被误判", "/networks/",
         "networks_index", '<p>An April 1, 2026 booking would…</p>',
         "2026-10-03", "", "", False),
        ("正例控件：本机真实产物 /networks/canada/ 应为 0 报错", "/networks/canada/",
         "networks_sub", None, "2026-10-07", "2026-10-07", "2026-10-07", False),
    ]

    # 真实产物锚点：直接读 public/ 里那一页，证明「真实产物在真检查下也是 0 报错」
    real_file = PUB / "networks" / "canada" / "index.html"
    real_html = io.open(real_file, encoding="utf-8", errors="ignore").read() \
        if real_file.exists() else ""

    bad = 0
    for name, url, kind, html, lastmod, page_exp, price_exp, want_err in cases:
        body = real_html if html is None else html
        if html is None and not real_html:
            print(f"  跳过 {name}（public/networks/canada/index.html 不存在，先跑构建）")
            continue
        got = page_date_errs(url, kind, body, lastmod, page_exp, price_exp)
        ok = bool(got) == want_err
        if not ok:
            bad += 1
        print(f"  {'OK ' if ok else 'FAIL'} {name}")
        if want_err and got:
            print(f"        -> {got[0]}")
        elif not want_err and not got:
            print("        -> 无报错（符合预期）")
        elif not want_err and got:
            print(f"        -> 误报！{got[0]}")
        else:
            print("        -> 期望报错却报 0 条（断言失效）")

    # 日期归一化：两种语言形态都要能被吃掉
    for raw, want in (("Oct 7, 2026", "2026-10-07"), ("07.10.2026", "2026-10-07"),
                      ("August 2026", None), ("2026-10-07", None)):
        got = norm_visible(raw)
        ok = got == want
        if not ok:
            bad += 1
        print(f"  {'OK ' if ok else 'FAIL'} norm_visible({raw!r}) = {got!r}（期望 {want!r}）")

    if bad:
        print(f"\n自测失败：{bad} 项")
        return 1
    print("\n自测通过")
    return 0


def main() -> int:
    if "--selftest" in sys.argv:
        return selftest()
    base = base_url()
    print(f"baseURL = {base}")
    plans, profile = load_data()
    net_iso = load_networks_iso()
    errs = check_host(base)
    errs += check_dates(base, plans, profile, net_iso)
    errs += check_completeness(base)

    if not errs:
        print("OK：产物域名正确，日期与数据一致。")
        return 0
    print(f"\n发现 {len(errs)} 条问题：")
    for e in errs:
        print("  " + e)
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
