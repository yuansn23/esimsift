#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Regenerate brand×country sub-pages (content/<lang>/compare/<slug>/<provider>.md)
from CURRENT data (single source of truth). Also removes sub-pages of providers
that no longer exist in providers.toml.

Unlike gen_sample_data.py this NEVER touches data/plans/*.toml - safe to run
after real scraped data lands. Run after every plans/provider set change.

语言：
  --lang en（默认）  content/en/compare/<slug>/<provider>.md  → /compare/<slug>/<provider>/
  --lang de          content/de/compare/<slug>/<provider>.md  → /de/compare/<slug>/<provider>/

⚠ **指标只有一份实现**（`metrics()`）：排名 / 全国套餐数 / 最低 $/GB / 最低 $/day
  两种语言共用。同一事实若出现两份实现，英文表与德文表迟早会算出两个不同的
  「全国套餐总数」—— 而两个数字都能自洽，谁也发现不了（红线 46）。

⚠ 本生成器**不再写 noindex**（2026-10-12 第八十五轮移除）：德语分层发布已于
  2026-10-10 `D9` 解禁完成，全站 noindex = 0；旧实现 `NOINDEX = LANG != "en"`
  一旦重跑就会给 499 个德语排列页**重新加回 noindex**，而产物侧看不出任何异常。
  这就是当年必须靠人工记着删注释的原因 —— 现在从源头去掉。

⚠ 德语目录名 == 英文 slug（`united-states`，不是 `vereinigte-staaten`）——
  与 50 个德语国家页（`content/de/compare/united-states.md`）保持一致。

Usage:
  python -X utf8 scripts/gen_provider_pages.py [--lang de] [--dry]

⚠ 重跑会**重写全部 499 个 md 的 front matter**（`seo.title` + `seo.description`）。
  跑完必须 `npm run build`（不是裸 hugo）+ `verify_provider_pages.py`。
"""
import itertools
import shutil
import sys
import tomllib
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"

LANG = "en"
_dry = False
_argv = sys.argv[1:]
for _i, _a in enumerate(_argv):
    if _a == "--dry":
        _dry = True
    elif _a == "--lang":
        LANG = _argv[_i + 1]
    elif _a.startswith("--lang="):
        LANG = _a.split("=", 1)[1]
if LANG not in ("en", "de"):
    sys.exit(f"ERROR: --lang must be en|de, got {LANG!r}")

CONTENT = ROOT / "content" / LANG / "compare"
# 年份只在这里取一次：SERP 标题里要写年份，取两次会跨年漂（红线 8）
_year = date.today().year

countries = tomllib.loads((DATA / "countries.toml").read_text(encoding="utf-8"))
providers = tomllib.loads((DATA / "providers.toml").read_text(encoding="utf-8"))
plans = {f.stem: tomllib.loads(f.read_text(encoding="utf-8"))
         for f in sorted((DATA / "plans").glob("*.toml"))}

LOC: dict = {}
if LANG != "en":
    _p = DATA / LANG / "countries.toml"
    if not _p.exists():
        sys.exit(f"ERROR: {_p} 不存在 —— 没有它就拿不到本地化国名")
    LOC = tomllib.loads(_p.read_text(encoding="utf-8"))
    # 启动期拦住「静默生成英文标题」：缺名 ⇒ 当场停，不生成半英文页
    _missing = [iso for iso in countries if not (LOC.get(iso) or {}).get("name")]
    if _missing:
        sys.exit(f"ERROR: data/{LANG}/countries.toml 缺 name 的国家：{_missing}")

unknown = [p for p in plans if p not in providers]
if unknown:
    sys.exit(f"ERROR: plans file without provider entry: {unknown} "
             f"(fix providers.toml or delete the plans file first)")


def local_name(iso: str, en_name: str) -> str:
    """本语言的国家名（英文站即英文名）。"""
    return en_name if LANG == "en" else LOC[iso]["name"]


def metrics(iso: str) -> dict:
    """某 ISO 下每个品牌的指标 + 全国排名。**两种语言共用，只此一份。**"""
    best = {}
    for pk, pdata in plans.items():
        block = pdata.get(iso)
        if not block or not block.get("plans"):
            continue
        pgb = [pl["price"] / pl["gb"] for pl in block["plans"] if pl["gb"] > 0]
        best[pk] = min(pgb) if pgb else float("inf")
    ranked = sorted(best, key=lambda k: best[k])
    n_all = sum(len(pdata[iso]["plans"]) for pk, pdata in plans.items()
                if iso in pdata and pdata[iso].get("plans"))
    out = {}
    for pk in sorted(plans):
        block = plans[pk].get(iso)
        if not block or not block.get("plans"):
            continue
        my = block["plans"]
        metered = [pl for pl in my if pl["gb"] > 0]
        unl = [pl for pl in my if pl["gb"] == 0]
        ds = [int(pl["days"]) for pl in my if pl.get("days")]
        out[pk] = {
            "n": len(my),
            "from_price": min(pl["price"] for pl in my),
            "bpgb": min(pl["price"] / pl["gb"] for pl in metered) if metered else None,
            "bday": min(pl["price"] / pl["days"] for pl in unl) if unl else None,
            "rank": ranked.index(pk) + 1,
            "m": len(best),
            "n_all": n_all,
            "unl_only": not metered,
            # 时长档：标题与描述**共用这一份推导**（红线 8 —— 同一事实只允许一份实现）
            "dmin": min(ds) if ds else 1,
            "dmax": max(ds) if ds else 1,
            "dvals": sorted(set(ds)),
        }
    return out


# --------------------------------------------------------------------------- 文案
# 2026-10-12（第八十五轮）P0 重写。三条约束**先量化再定**，全部由本文件的
# `.buildlog/r85_proto_copy.py` 在 50 国 × 10 品牌 × 2 语言上实测通过：
#
#   ① 标题 44-54 字符（`verify_provider_pages.py` 建档范围），尽量落 48-54
#      （`audit_meta.py` 更严口径）；**必含国名**（守卫第 1 项）。
#   ② 描述 120-140 字符、**必含 "eSIMSift"**（守卫第 2 项）。
#   ③ 同一语言内 499 条标题、499 条描述**零重复**（实测 499/499 唯一）。
#
# 为什么删掉 `(#N of M)`：GSC 7 天里 `/compare/canada/saily/` 拿 532 展示、
# 位置 10.86、**0 点击**，而它的 SERP 摘要原文是
#   "… best $2.20/GB (#9 of 10) — ranked against 221 Canada plans."
# 搜 `saily esim canada` 的人想看 Saily，页面只告诉他「这牌子在 10 家里排第 9」。
# 该写法覆盖 449/499 个排列页（90%），合计承担全站 40% 的展示。
# ⇒ 名次只在**真的好**（≤3）时以正向表述出现，其余整句摘掉。
#
# ⚠ 2026-10-04 用户曾定「标题不放套餐数量、不放价格」；2026-10-12 用户明确
#   **废除**该约束（连带 `verify_provider_pages.py` 的 TITLE_BANNED 硬规则），
#   理由是标题里带套餐数/天数/起价能直接回应用户的比价意图。
#   代价是**每次数据变动都会改标题**（标题由构建期现算，所以永远是当前的，
#   只是会变）。这条取舍是用户拍板的，不要当成回归。

ORD_EN = {1: "Cheapest", 2: "2nd-cheapest", 3: "3rd-cheapest"}
ORD_DE = {1: "Günstigster", 2: "Zweitgünstigster", 3: "Drittgünstigster"}


def dlab(mx):
    """时长档的区间形态（标题用，短）。"""
    return f"{mx['dmin']}" if mx["dmin"] == mx["dmax"] else f"{mx['dmin']}-{mx['dmax']}"


def dlist(mx, conj):
    """时长档的**逐档**形态（描述用）：≤3 个档位就列全（"5, 15 or 30 days"）——
    GSC 里 `saily esim canada 15 days price` 已排第 6，逐档列出才匹配得上
    「我的行程几天」。档位更多（如 Yesim 的 37 个套餐）才退回区间。"""
    v = mx["dvals"]
    if 2 <= len(v) <= 3:
        return ", ".join(str(x) for x in v[:-1]) + f" {conj} " + str(v[-1])
    return dlab(mx)


def _title_profiles(pname, name, mx, lang):
    head = f"{pname} {name} eSIM:"
    d = dlab(mx)
    if not mx["unl_only"]:
        return [((head, [f"{mx['n']} Plans", f"{d} Days",
                         f"From ${mx['from_price']:.2f}"]) if lang == "en" else
                 (head, [f"{mx['n']} Tarife", f"{d} Tage",
                         f"ab ${mx['from_price']:.2f}"]))]
    if lang == "en":
        return [
            (head, [f"{mx['n']} Unlimited Plans", f"{d} Days", f"From ${mx['bday']:.2f}/Day"]),
            (head, [f"{mx['n']} Plans", f"{d} Days", f"From ${mx['bday']:.2f}/Day"]),
            (f"Unlimited {pname} {name} eSIM:", [f"{mx['n']} Plans", f"{d} Days"]),
        ]
    return [
        (head, [f"{mx['n']} unbegrenzte Tarife", f"{d} Tage", f"ab ${mx['bday']:.2f}/Tag"]),
        (head, [f"{mx['n']} Tarife", f"{d} Tage", f"ab ${mx['bday']:.2f}/Tag"]),
        (head, ["Unbegrenzte Datentarife", f"{d} Tage"]),
        (head, ["unbegrenzt", f"{d} Tage", f"ab ${mx['bday']:.2f}/Tag"]),
        (f"{pname} {name} eSIM unbegrenzt:", [f"{mx['n']} Tarife"]),
    ]


def make_title(pname, name, mx, lang, year, pk):
    """head + 段落的全部子集，取「信息最多且塞得进 44-54」的那条。

    纯不限量品牌把 Unlimited / unbegrenzt 作为**硬约束**（长度不够时降级成
    `… eSIM: 6 Unlimited Plans`，而不是把这个词丢掉 —— Holafly 只卖不限量，
    丢了这个词标题就没说清它是什么）。
    """
    profiles = _title_profiles(pname, name, mx, lang)
    ok = []
    for head, segs in profiles:
        for k in range(len(segs), -1, -1):
            for c in itertools.combinations(range(len(segs)), k):
                tail = ", ".join(segs[i] for i in c)
                ok.append(head + (" " + tail if tail else ""))
        ok.append(f"{head[:-1]} {year}:" + " " + ", ".join(segs[:2]))
    if mx["unl_only"]:
        kw = "Unlimited" if lang == "en" else "nbegrenzt"
        kwc = [c for c in ok if kw in c]
        if kwc:
            ok = kwc
    for c in ok:
        if 48 <= len(c) <= 54:
            return c
    for c in ok:
        if 44 <= len(c) <= 54:
            return c
    under = [c for c in ok if len(c) <= 54]
    got = max(under, key=len) if under else min(ok, key=len)
    if not (44 <= len(got) <= 54):
        sys.exit(f"ERROR: title out of 44-54 for {pk}/{name}: [{len(got)}] {got!r}")
    return got


def make_desc(pname, name, mx, lang, pk):
    """开场句 × 价格子句 × 名次句 的笛卡尔积，取第一段落进 120-140 的。

    刻意做成笛卡尔积：手写固定候选在「中等长度国名 + 有 $/GB」的页面（如
    aloSIM/Thailand）上留过一个 112 → 143 的**长度空洞**，实测 149 条出界。
    """
    n, m, unl = mx["n"], mx["m"], mx["unl_only"]
    fp = mx["bday"] if unl else mx["from_price"]
    unit = "/day" if (unl and lang == "en") else ("/Tag" if unl else "")
    dl = dlist(mx, "or" if lang == "en" else "oder")
    if lang == "en":
        mids = ([", fair-use caps decoded.", ", fair-use capped.", "."] if unl else
                [f", ${mx['bpgb']:.2f}/GB at the cheapest tier.",
                 f", ${mx['bpgb']:.2f}/GB cheapest.", f", ${mx['bpgb']:.2f}/GB.", "."])
        opens = [
            f"All {n} {pname} plans for {name} in one table: {dl} days from ${fp:.2f}{unit}",
            f"Every {pname} plan for {name} in one table: {dl} days from ${fp:.2f}{unit}",
            f"All {n} {pname} plans for {name} side by side: {dl} days from ${fp:.2f}{unit}",
            f"Every {pname} plan for {name}: {dl} days from ${fp:.2f}{unit}",
            f"{n} {pname} plans for {name}, {dl} days from ${fp:.2f}{unit}",
        ]
        ranks = [""]
        if not unl and mx["rank"] in ORD_EN:
            ranks = [f"{ORD_EN[mx['rank']]} $/GB of the {m} brands we track.", ""]
        sign = "eSIMSift prices every option in one table."
    else:
        mids = ([", Fair-Use-Grenzen geprüft.", ", Fair-Use geprüft.", "."] if unl else
                [f", ${mx['bpgb']:.2f}/GB im günstigsten Tarif.",
                 f", günstigster Tarif ${mx['bpgb']:.2f}/GB.",
                 f", ${mx['bpgb']:.2f}/GB.", "."])
        opens = [
            f"Alle {n} {pname}-Tarife für {name} in einer Tabelle: {dl} Tage ab ${fp:.2f}{unit}",
            f"Jeder {pname}-Tarif für {name} in einer Tabelle: {dl} Tage ab ${fp:.2f}{unit}",
            f"Alle {n} {pname}-Tarife für {name} im Vergleich: {dl} Tage ab ${fp:.2f}{unit}",
            f"Jeder {pname}-Tarif für {name}: {dl} Tage ab ${fp:.2f}{unit}",
            f"{n} {pname}-Tarife für {name}, {dl} Tage ab ${fp:.2f}{unit}",
        ]
        ranks = [""]
        if not unl and mx["rank"] in ORD_DE:
            ranks = [f"{ORD_DE[mx['rank']]} $/GB-Preis unter {m} Anbietern.", ""]
        sign = "eSIMSift vergleicht jede Option in einer Tabelle."
    cands = []
    for o in opens:
        for mid in mids:
            for r in ranks:
                # ★ 开场句刻意**不带句号**：句末点号由价格子句提供。
                #   两处都带会印出 "$5.29., $2.20/GB cheapest." 与 "ab $4.00.. eSIMSift"。
                cands.append(o + mid + (" " + r if r else "") + " " + sign)
    for c in cands:
        if 120 <= len(c) <= 140:
            return c
    sys.exit(f"ERROR: desc out of 120-140 for {pk}/{name} ({lang}): "
             f"{sorted(set(len(c) for c in cands))}")


def render_en(pk: str, name: str, mx: dict, year: int) -> tuple[str, str, str]:
    pname = providers[pk]["name"]
    return (f"{pname} {name} eSIM Plans & Prices",
            make_title(pname, name, mx, "en", year, pk),
            make_desc(pname, name, mx, "en", pk))


def render_de(pk: str, name: str, mx: dict, year: int) -> tuple[str, str, str]:
    pname = providers[pk]["name"]
    return (f"{pname} {name} eSIM-Tarife & Preise",
            make_title(pname, name, mx, "de", year, pk),
            make_desc(pname, name, mx, "de", pk))


RENDER = {"en": render_en, "de": render_de}[LANG]

# --------------------------------------------------------------------------- 执行
# 1. drop stale sub-pages (provider left the set). 只动 <slug>/ 目录，不碰同层的
#    <slug>.md —— 德语侧国家页正是「扁平文件 + 品牌子目录」并存的结构。
removed = 0
for d in sorted(CONTENT.iterdir()):
    if not d.is_dir():
        continue
    for f in d.glob("*.md"):
        if f.stem not in providers:
            if _dry:
                print(f"  [dry] rm {f.relative_to(ROOT)}")
            else:
                f.unlink()
            removed += 1
    if not any(d.glob("*.md")):
        if _dry:
            print(f"  [dry] rmdir {d.relative_to(ROOT)}")
        else:
            shutil.rmtree(d)

# 2. rebuild every sub-page from current plan data
written = 0
for iso, c in countries.items():
    slug, name = c["slug"], local_name(iso, c["name"])
    mx_all = metrics(iso)
    for pk, mx in mx_all.items():
        title, serp_title, desc = RENDER(pk, name, mx, _year)
        d = CONTENT / slug
        # `seo.title` 走 head.html 里**已有的标题锁**机制（`$lockedTitle`），
        # 所以模板一行都不用改 —— 而 SERP 标题与 H1（front matter 的 title）
        # 从此是**两个字段、两个面**：H1 留「Plans & Prices」，SERP 带套餐数/天数/起价。
        md = ["---",
              f'title: "{title}"',
              f"iso: {iso}",
              f"provider: {pk}",
              "layout: provider",
              "seo:",
              f'  title: "{serp_title}"',
              f'  description: "{desc}"',
              "---", ""]
        if _dry:
            written += 1
            continue
        d.mkdir(parents=True, exist_ok=True)
        # ⚠ 换行符**显式**写死，别依赖平台默认：英文侧历史文件是 CRLF（原实现走
        #   write_text(newline=None) 的 Windows 行为），德语侧 55 个 md 全是 LF。
        #   混用会让同一个文件在两次生成之间「无内容差异却全文重写」。
        (d / f"{pk}.md").write_text("\n".join(md), encoding="utf-8",
                                    newline="\r\n" if LANG == "en" else "\n")
        written += 1

print(f"OK [{LANG}]: {written} provider×country sub-pages"
      f"{' (dry)' if _dry else ''} written, {removed} stale removed.")
