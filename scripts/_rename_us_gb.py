# -*- coding: utf-8 -*-
"""一次性改名脚本（2026-10-05 用户定）：United States -> USA、United Kingdom -> UK。

范围与边界（重要）：
  · 只处理**我们自己写的**正文与数据：content/en/**/*.md、data/faqs/*.toml。
  · 不碰 data/plans/*.toml 里的 name —— 那是各家目录里套餐的**原始商品名**，
    改了就和来源对不上账。
  · 不碰 data/networkreports.toml 的 opensignal_title —— 那是外部报告的**真实标题**，
    E-E-A-T 要求逐字引用。同一文件里的 ookla_note 是我们自己的话，另行单条替换。
  · 不碰 data/de/countries.toml —— 那是德语本地化名（Vereinigte Staaten），
    不是英文串 "United States"，德语站该显示德语全名。

替换顺序即优先级：先长模式后短模式，先带冠词的短语后裸词，
否则 "for United States" 会先被裸词规则吃掉、丢掉该补的冠词。

行尾保真：content/ 与 data/ 在工作区是 CRLF，读写都走 newline="" 原样透传。

用法：python -X utf8 scripts/_rename_us_gb.py [--dry]
"""
from __future__ import annotations

import argparse
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# (旧, 新) —— 顺序敏感，勿重排
RULES: list[tuple[str, str]] = [
    # 1) 名词短语：eSIM 复数 / 带不定冠词
    ("United States eSIMs", "USA eSIMs"),
    ("United Kingdom eSIMs", "UK eSIMs"),
    ("a United States eSIM", "a USA eSIM"),
    ("a United Kingdom eSIM", "a UK eSIM"),
    ("the United States", "the USA"),
    ("the United Kingdom", "the UK"),
    # 2) 介词短语：补齐英语需要的冠词
    ("for United States", "for the USA"),
    ("for United Kingdom", "for the UK"),
    ("in United States", "in the USA"),
    ("in United Kingdom", "in the UK"),
    ("of United States", "of the USA"),
    ("of United Kingdom", "of the UK"),
    ("to United States", "to the USA"),
    ("to United Kingdom", "to the UK"),
    ("from United States", "from the USA"),
    ("from United Kingdom", "from the UK"),
    # 3) 句首 / 连词后
    ("No. United States ", "No. The USA "),
    ("No. United Kingdom ", "No. The UK "),
    ("bundle United States with", "bundle the USA with"),
    ("bundle United Kingdom with", "bundle the UK with"),
    ("cover United States and", "cover the USA and"),
    ("cover United Kingdom and", "cover the UK and"),
    ("and United States?", "and the USA?"),
    ("and United Kingdom?", "and the UK?"),
    ("Canada and United States", "Canada and the USA"),
    ("France and United Kingdom", "France and the UK"),
    ("Ireland and United Kingdom", "Ireland and the UK"),
    ("Mexico and United States", "Mexico and the USA"),
    # 4) 兜底：裸词
    ("United States", "USA"),
    ("United Kingdom", "UK"),
]

TARGETS: list[str] = ["content/en", "data/faqs"]

# data/plans/<brand>.toml 里的套餐名是**由国家标签拼出来的描述串**
# （"United States eSIM 5GB / 21 Days" / "United Kingdom (UK)"），
# 不是品牌自己的营销名 —— 全站 3 个文件、215 条命中，全部落在 name = "…" 里
# （已核：无一条出现在注释或其它字段）。国家标签统一后这里必须跟着改，
# 否则国家页的 Plan 列还会显示 United States。
# ⚠ 只匹配 "United States"/"United Kingdom" 全串，
#   "United Arab Emirates (UAE)" 不受影响。
PLAN_RULES: list[tuple[str, str]] = [
    # aloSIM 的目录名是小写原文（"united states (usa)"）—— 同样只是国家标签拼出来的
    ("united states (usa)", "USA"),
    ("united kingdom (uk)", "UK"),
    ("United States (USA)", "USA"),
    ("United Kingdom (UK)", "UK"),
    # ⚠ 顺序敏感：必须排在 ("United States", "USA") **之前**。
    #   Jetpac 的 esimdb 商品名用的是全称 "United States Of America"（Of 大写），
    #   先命中短模式会产出不通顺的 "USA Of America"（2026-10-07 实测）。
    ("United States Of America", "USA"),
    ("United States of America", "USA"),
    ("United States", "USA"),
    ("United Kingdom", "UK"),
]
PLAN_TARGETS: list[str] = ["data/plans"]


def collect(targets: list[str] | None = None) -> list[str]:
    out: list[str] = []
    for t in (targets or TARGETS):
        full = os.path.join(ROOT, t)
        if os.path.isfile(full):
            out.append(full)
            continue
        for dp, _dn, fn in os.walk(full):
            for f in sorted(fn):
                if f.endswith((".md", ".toml")):
                    out.append(os.path.join(dp, f))
    return out


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry", action="store_true")
    args = ap.parse_args()

    groups = [(collect(), RULES), (collect(PLAN_TARGETS), PLAN_RULES)]
    changed, hits = 0, 0
    for paths, rules in groups:
        for path in paths:
            with open(path, encoding="utf-8", newline="") as fh:
                src = fh.read()
            out = src
            local = 0
            for old, new in rules:
                n = out.count(old)
                if n:
                    out = out.replace(old, new)
                    local += n
            if out != src:
                hits += local
                changed += 1
                print(f"  {os.path.relpath(path, ROOT):55s} {local} 处")
                if not args.dry:
                    with open(path, "w", encoding="utf-8", newline="") as fh:
                        fh.write(out)
    print(f"{'[dry] ' if args.dry else ''}改写 {changed} 个文件 / {hits} 处")
    return 0


if __name__ == "__main__":
    sys.exit(main())
