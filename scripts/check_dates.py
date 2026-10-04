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
DAY = r"\b((?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]* \d{1,2}, \d{4})"

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


def newest(values) -> str:
    vals = [v for v in values if v]
    return max(vals) if vals else ""


def brand_newest(plans, key: str) -> str:
    return newest(plans.get(key, {}).values())


def norm_visible(s: str):
    m = re.match(r"([A-Z][a-z]{2})[a-z]* (\d{1,2}), (\d{4})", s)
    if not m:
        return None
    return "%s-%02d-%02d" % (m.group(3), MONTHS[m.group(1)], int(m.group(2)))


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


def check_dates(base: str, plans, profile) -> list[str]:
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
        elif edit:
            kind = "edit"
        else:
            continue

        stats[kind] += 1
        page_file = PUB / url.lstrip("/") / "index.html"
        if not page_file.exists():
            continue  # 交给断言 C
        html = io.open(page_file, encoding="utf-8", errors="ignore").read()

        if not edit:
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
        else:
            for dm in sorted(set(RE_DATEMOD.findall(html))):
                if lastmod and dm[:10] != lastmod:
                    errs.append(f"[B] {url} dateModified={dm[:10]} ≠ sitemap lastmod={lastmod}")

    print("  页型：" + "、".join(f"{k}={stats[k]}" for k in sorted(stats)))
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


def main() -> int:
    base = base_url()
    print(f"baseURL = {base}")
    plans, profile = load_data()
    errs = check_host(base)
    errs += check_dates(base, plans, profile)
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
