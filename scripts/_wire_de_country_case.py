#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""D7 前置②-a：给 layouts/compare/provider.html 的每个 i18n dict 补上
   `country_acc`（宾格：für/über）与 `country_dat`（与格：in/von/bei）。

为什么：德语国名带冠词时三个格不同（`die USA` / `der Türkei` …），
数据层 `data/de/countries.toml` 提供 name / name_acc / name_dat 三份，
模板必须把需要的那份传进去 —— 58 个国家页已用同一手法
（`compare/single.html` 的 `$country.name_acc | default $country.name`），
provider 页此前没接。

英语侧为什么不变：en.toml 的值不引用这两个键；本改动只在既有
`(dict …)` 里追加键值对，不新增空白/换行 → 英文产物应逐字节不变
（由 `verify_no_regression.py --diff` 验证）。
"""
from __future__ import annotations

import sys
from pathlib import Path

P = Path(__file__).resolve().parents[1] / "layouts" / "compare" / "provider.html"
NEEDLE = '"country" $country.name'
EXTRA = (' "country_acc" ($country.name_acc | default $country.name)'
         ' "country_dat" ($country.name_dat | default $country.name)')


def main() -> int:
    raw = P.read_bytes()
    text = raw.decode("utf-8")
    if "country_acc" in text:
        print("SKIP 已接线（幂等）")
        return 0
    n = text.count(NEEDLE)
    if n == 0:
        print("FAIL 一个锚点都没命中")
        return 1
    out = text.replace(NEEDLE, NEEDLE + EXTRA)
    data = out.encode("utf-8")
    if data.count(b"\r\n"):
        print("FAIL 产物出现 CRLF")
        return 1
    if out.count("country_dat") != n:
        print("FAIL 计数不符")
        return 1
    P.write_bytes(data)
    print(f"OK 接线 {n} 处（{len(raw)} -> {len(data)} B）")
    return 0


if __name__ == "__main__":
    sys.exit(main())
