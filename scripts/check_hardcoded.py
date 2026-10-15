# -*- coding: utf-8 -*-
"""Hardcoded-count guard: fail if hand-written content hardcodes site totals
that must stay data-derived (countries / providers / plans / tiers).

Rule (2026-10-02, extended 2026-10-15):
  - layouts/*.html  → must use {{ len hugo.Data.* }}
  - content bodies  → must use {{< count-countries >}} / {{< count-providers >}}
                      （新增计数一律走短代码，构建期现算）
  - front matter    → **number-free wording**（front matter 跑不了短代码，
                      所以只能改写；「我们追踪的每一份」这类自更新量词是正解）
  - EXEMPT: content/<lang>/compare/** 的 `seo:` 块 —— 由 scripts/regen_meta_brand.py
            （国家页）/ scripts/_compare_de_lib.py（德语）/ scripts/gen_provider_pages.py
            （499 个品牌子页）从实时数据重生成 ⇒ 里面的计数**不是手写快照**，安全靠重生成。
  - DEFERRED: content/<lang>/compare/<country>.md 的**正文**计数 —— 已知存量，
            2026-10-15 用户决定「先登记、暂不改」（见 STATUS.md）。本守卫把它们
            单独列出并 STILL 失败，让待办量永远可见、只减不增。

── 为什么要有它（2026-10-15 第九十五轮）────────────────────────────────────
纽约指南的 `facts` 格写了「254 across ten brands」，而文章上线时并无守卫发现 ——
因为**本脚本从未接进 `npm run validate` / `check:output`**，规则写了、守卫写了、
但没通电。用户的原话：「万一我后续新增其他品牌的美国esim咋办」。

── 判据的边界（同一天实测定死）──────────────────────────────────────────────
只收**会因外部数据增长而失效**的计数：品牌数 / 套餐数 / 档位数 / 比例计数。
刻意**不收**：
  · **价格与价格派生量**（$0.51 / $0.60·GB / 23.9 倍）—— 有复核日锚
    （"last verified on 7 October 2026"），且是本项目按红线必须现算的内容主体。
  · **稳定地理事实**（`all three countries` = 美/加/墨）—— 收进来会让
    esim-new-york / esim-vs-physical-sim / networks/{united-states,south-korea}
    四页**假红**（第九十五轮实测 76 处命中里就有这 4 处）。
  · **区域策展集合的规模**（`18 destinations` / `8 Countries`）—— 只有「我主动扩区」
    才会变，不是外部数据增长；要动态化得先给每个区域建数据源，是独立议题。

用法：
    python -X utf8 scripts/check_hardcoded.py
    python -X utf8 scripts/check_hardcoded.py --selftest   # 注入反例，两侧证
"""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BASES = ("content/en", "content/de", "layouts", "hugo.toml")

# ── 只判「会因数据增长失效」的结构计数 ────────────────────────────────────
PATTERNS: list[tuple[str, re.Pattern]] = [
    ("国家/目的地总数", re.compile(r"\b(?:50|fifty)\s+(?:countries|destinations)\b", re.I)),
    ("品牌总数（数字）", re.compile(r"\b(?:8|eight|9|nine|10|ten|11|eleven|12|twelve)\s+(?:eSIM\s+)?providers?\b", re.I)),
    ("品牌总数（数词）", re.compile(r"\b(?:all\s+)?(?:ten|eleven|twelve|nine|eight)\s+(?:eSIM\s+)?brands?\b", re.I)),
    ("品牌总数（德语）", re.compile(r"\b(?:zehn|elf|zwölf|neun|acht)\s+(?:Marken|Anbietern?|Anbieter)\b", re.I)),
    ("对决对数", re.compile(r"\b28\s+(?:provider\s+)?matchups", re.I)),
    ("对决对数（All 28）", re.compile(r"\bAll\s+28\b")),
    ("品牌总数（eight-plus）", re.compile(r"\beight-plus\b", re.I)),
    ("套餐数", re.compile(
        # ⚠ `(?<![\d.,])` 是必须的：少了它 `$0.51 plan` 会被当成「51 plan」（实测
        #    content/en/compare/_index.md:14 假红）。
        r"(?<![\d.,])\b\d{2,4}\b\s+(?:real\s+|echte\s+)?(?:prepaid\s+|Prepaid-)?(?:eSIM[-\s])?(?:plans?|Tarife[n]?)\b", re.I)),
    ("比例计数", re.compile(
        r"(?<![\d.,])\b\d+\b\s+(?:of|der|von)\s+(?:the\s+|den\s+)?\d+\s+(?:plans?|Tarife[n]?)\b", re.I)),
    ("档位数", re.compile(r"\b(?:six|seven|sechs|sieben)\s+(?:tiers?|Stufen)\b", re.I)),
    # 每页第二个死数字：`…, 100 sold as unlimited` / `…, 86 of them unlimited`
    # 与套餐数成对出现，性质完全相同（新增品牌后一起失效）。
    ("不限量计数", re.compile(
        r"(?<![\d.,])\b\d{1,4}\b\s+(?:sold as unlimited|of them unlimited|carrying an unlimited label"
        r"|are unlimited|davon unbegrenzt|sind unbegrenzt)\b", re.I)),
]

# HTML 注释不出现在产物里，里面的历史说明会假红（实测：aside-destinations.html 里
# 一句「此前那行是写死的英文，/de/networks/ 上直接印出 All 50 destinations」——
# 那是在**记录一个已修好的 bug**，不是违反规则）。
# ⚠ 三种形态都要收：`{{/* … */}}`、带裁剪符的 `{{- /* … */ -}}`（aside-destinations.html
#   的开头就是这一种，只写 `{{/*` 会漏掉它 ⇒ 假红）、以及裸 `<!-- … -->`。
COMMENT_RE = re.compile(r"\{\{-?[ \t]*/\*.*?\*/[ \t]*-?\}\}|<!--.*?-->", re.S)

# 生成器重写的 `seo:` 块（块内计数不是手写快照）
SEO_BLOCK_RE = re.compile(r"^seo:[ \t]*\n(?:[ \t]+\S.*\n)*", re.M)


def mask_comments(text: str) -> str:
    """把注释换成等量空行 —— 保住行号，删掉内容。"""
    return COMMENT_RE.sub(lambda m: "\n" * m.group(0).count("\n"), text)


def strip_seo_block(text: str) -> str:
    """删 `seo:` 块内容、保行号（生成器会重写它，不是手写快照）。"""
    return SEO_BLOCK_RE.sub(lambda m: "\n" * m.group(0).count("\n"), text)


def is_compare(rel: str) -> bool:
    return rel.startswith("content/en/compare/") or rel.startswith("content/de/compare/")


def scan_text(rel: str, text: str) -> tuple[list[str], list[str]]:
    """→ (violations, exempted)。

    compare 页的 `seo:` 块先剥掉 —— 里面的计数由生成器重写，不是手写快照。
    ⚠ 豁免量用**「剥前命中数 − 剥后命中数」**求差，不要拿掩码后的 offset 去查原串：
      掩码把注释换成了等量换行，**长度已经变了**，offset 会漂。
    """
    body = mask_comments(text)
    found_all = _hits(rel, body)
    if not is_compare(rel):
        return found_all, []
    found_no_seo = _hits(rel, strip_seo_block(body))
    exempted = [f"{rel}: {h.split(': ', 1)[-1]}" for h in found_all[: len(found_all) - len(found_no_seo)]]
    return found_no_seo, exempted


def _hits(rel: str, body: str) -> list[str]:
    found: list[str] = []
    for label, pat in PATTERNS:
        for m in pat.finditer(body):
            line = body[: m.start()].count("\n") + 1
            found.append(f"{rel}:{line}: {label} \u2014 {m.group(0)!r}")
    return found


def collect() -> tuple[list[str], list[str]]:
    violations: list[str] = []
    exempted: list[str] = []
    for base in BASES:
        p = ROOT / base
        files = [p] if p.is_file() else sorted(x for x in p.rglob("*") if x.is_file())
        for f in files:
            rel = f.relative_to(ROOT).as_posix()
            try:
                text = f.read_text(encoding="utf-8")
            except UnicodeDecodeError:
                continue
            v, e = scan_text(rel, text)
            violations += v
            exempted += e
    return violations, exempted


def selftest() -> int:
    """注入反例：正例不误伤、反例必红。两侧都要证。"""
    good = [
        ("content/en/guides/x.md", "All three countries get the same towers."),
        ("content/en/guides/x.md", "18 destinations sit in the table."),
        ("content/en/guides/x.md", "The cheapest plan is $0.51 per 5GB."),
        ("content/en/guides/x.md", "Across {{< count-providers >}} brands the file runs on."),
        ("content/en/guides/x.md", "the board runs to {{< count-plans >}} plans for the USA"),
        ("layouts/partials/a.html", "{{/* \u6b64\u524d\u90a3\u884c\u662f\u5199\u6b7b\u7684\u82f1\u6587\uff0c/de/networks/ \u4e0a\u76f4\u63a5\u5370\u51fa All 50 destinations \u2192 */}}"),
        ("content/en/compare/chile.md", 'seo:\n  description: "160 real plans from 10 providers"\n'),
    ]
    bad = [
        ("content/en/guides/x.md", "All ten brands we track run on the same three networks."),
        ("content/en/guides/x.md", "Our database tracks 254 prepaid plans."),
        ("content/en/guides/x.md", "100 of the 254 plans are unlimited."),
        ("content/en/guides/x.md", "with six tiers from 3 days to 30 days"),
        ("content/de/guides/x.md", "Zehn Marken verkaufen in die USA."),
        ("content/de/guides/x.md", "100 der 254 Tarife sind unbegrenzt."),
        ("layouts/partials/a.html", "We track 50 countries here."),
    ]
    failed = 0
    print("  ── 正例（必须 0 命中）──")
    for rel, text in good:
        v, _ = scan_text(rel, text)
        ok = not v
        failed += 0 if ok else 1
        print(f"  {'OK  ' if ok else 'MISS'} {text[:58]!r} -> {len(v)}")
        if not ok:
            print(f"        {v}")
    print("  ── 反例（必须命中）──")
    for rel, text in bad:
        v, _ = scan_text(rel, text)
        ok = bool(v)
        failed += 0 if ok else 1
        print(f"  {'OK  ' if ok else 'MISS'} {text[:58]!r} -> {len(v)}")
    print(f"\n自测{'通过' if not failed else f'失败 {failed} 项'}")
    return 1 if failed else 0


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--selftest", action="store_true")
    args = ap.parse_args()
    if args.selftest:
        return selftest()

    violations, exempted = collect()
    print(f"scanned: {', '.join(BASES)}")
    print(f"regenerated-SEO hits (exempt): {len(exempted)}")
    if not violations:
        print("OK: no hardcoded totals outside the registered exceptions")
        return 0
    deferred = [v for v in violations if is_compare(v.split(":")[0])]
    hard = [v for v in violations if not is_compare(v.split(":")[0])]
    if hard:
        print(f"\nHARDCODED TOTALS ({len(hard)}):")
        for v in hard:
            print("  !", v)
    if deferred:
        files = sorted({v.split(":")[0] for v in deferred})
        print(f"\nDEFERRED — compare 正文存量（{len(deferred)} 处 / {len(files)} 文件，"
              f"2026-10-15 用户决定先登记）:")
        print(f"  例：{deferred[0]}")
        print(f"  涉及：{files[0]} … {files[-1]}")
    print("\nFix: layouts → {{ len hugo.Data.* }} · content body → {{< count-countries >}} / "
          "{{< count-providers >}} · front matter → number-free wording")
    return 1


if __name__ == "__main__":
    sys.exit(main())
