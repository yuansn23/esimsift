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

⚠ 德语页**带 noindex**（`D9` 才统一解禁）。副作用是**英文侧产物逐字节不变**：
  head.html 只对可索引译文发 hreflang，译文 noindex ⇒ 英文页一条 hreflang 也不变。
  这正是验收「英文侧恒等」的机制。

⚠ 德语目录名 == 英文 slug（`united-states`，不是 `vereinigte-staaten`）——
  与 50 个德语国家页（`content/de/compare/united-states.md`）保持一致。

Usage:
  python -X utf8 scripts/gen_provider_pages.py [--lang de] [--dry]
"""
import shutil
import sys
import tomllib
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
NOINDEX = LANG != "en"

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
        out[pk] = {
            "n": len(my),
            "from_price": min(pl["price"] for pl in my),
            "bpgb": min(pl["price"] / pl["gb"] for pl in metered) if metered else None,
            "bday": min(pl["price"] / pl["days"] for pl in unl) if unl else None,
            "rank": ranked.index(pk) + 1,
            "m": len(best),
            "n_all": n_all,
            "unl_only": not metered,
        }
    return out


# --------------------------------------------------------------------------- 文案
def render_en(pk: str, name: str, mx: dict) -> tuple[str, str]:
    pname = providers[pk]["name"]
    if not mx["unl_only"]:
        core = (f"eSIM Sift compares {pname} eSIM plans for {name}: {mx['n']} plans from "
                f"${mx['from_price']:.2f}, best ${mx['bpgb']:.2f}/GB (#{mx['rank']} of {mx['m']})")
        tails = [
            f" — benchmarked against all {mx['n_all']} {name} eSIMs we track.",
            f" — ranked against {mx['n_all']} {name} plans.",
            " — from our live price index.",
            " — live prices.",
        ]
    else:
        core = (f"eSIM Sift compares {pname} unlimited eSIMs for {name}: {mx['n']} daily "
                f"plans from ${mx['bday']:.2f}/day, fair-use caps decoded")
        tails = [
            f" — benchmarked against all {mx['n_all']} {name} eSIMs we track.",
            f" — {mx['n_all']} {name} eSIMs tracked.",
            " — from our live price index.",
            " — live prices.",
        ]
    return f"{pname} {name} eSIM Plans & Prices", pick(core, tails, 120, 140, pk, name)


def render_de(pk: str, name: str, mx: dict) -> tuple[str, str]:
    pname = providers[pk]["name"]
    if not mx["unl_only"]:
        core = (f"eSIM Sift vergleicht {pname}-Tarife für {name}: {mx['n']} Tarife ab "
                f"${mx['from_price']:.2f}, bester Preis ${mx['bpgb']:.2f}/GB (#{mx['rank']} von {mx['m']})")
        tails = [
            f" — gemessen an allen {mx['n_all']} erfassten {name}-eSIMs.",
            f" — gegen {mx['n_all']} {name}-Tarife verglichen.",
            " — aus unserem Live-Preisindex.",
            " — aktuelle Preise.",
            "",
        ]
    else:
        core = (f"eSIM Sift vergleicht {pname}-Unlimited-Tarife für {name}: {mx['n']} Tages-"
                f"Tarife ab ${mx['bday']:.2f}/Tag, Fair-Use-Grenzen geprüft")
        tails = [
            f" — gemessen an allen {mx['n_all']} erfassten {name}-eSIMs.",
            f" — {mx['n_all']} {name}-eSIMs im Vergleich.",
            " — aus unserem Live-Preisindex.",
            " — aktuelle Preise.",
            "",
        ]
    return f"{pname} {name} eSIM-Tarife & Preise", pick(core, tails, 120, 165, pk, name)


def pick(core: str, tails: list[str], lo: int, hi: int, pk: str, name: str) -> str:
    d = next((c for t in tails if lo <= len(c := core + t) <= hi), None)
    if d is None:
        sys.exit(f"ERROR: desc out of {lo}-{hi} range for {pk}/{name}: "
                 f"core={len(core)}, tails={[len(core + t) for t in tails]}")
    return d


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
        title, desc = RENDER(pk, name, mx)
        d = CONTENT / slug
        md = ["---",
              f'title: "{title}"',
              f"iso: {iso}",
              f"provider: {pk}",
              "layout: provider",
              "seo:",
              f'  description: "{desc}"']
        if NOINDEX:
            md += ["noindex: true",
                   f"# TODO({LANG})：本页由 scripts/gen_provider_pages.py 生成，"
                   f"正文来自 data/plans/*.toml（模板已本地化）。"
                   f"D9 解禁时统一删掉上面 noindex 行。"]
        md += ["---", ""]
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
