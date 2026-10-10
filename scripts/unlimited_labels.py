#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""「无限流量」数据列标签的语言无关解析 —— 两个守卫共用一份。

为什么必须单独一份
------------------
`verify_no_regression.py` 的 [C] 检查与 `verify_provider_pages.py` 的第 11 项，
都在判断「套餐行的数据列写的是不是无限」。2026-10-09 之前两处都硬编码了
英文判据 `"unlimited" in cell.lower()` —— 守卫因此是**语言盲**的：

  · 德语页把 `g_unlimited` 从英文占位 `Unlimited` 译成 `Unbegrenzt` 之后，
    50 个德语国家 Hub 页的 **4602 处完全正常的套餐行被判违规**。
  · 在那之前之所以没暴露，只是因为德语值还都是英文占位 —— 翻译一推进它就炸。

这也正是「同一条规则只允许存在一份」的反面教材：抄第二份，就是第二处会错的地方。
现在统一从 `i18n/*.toml` 现读全部语言的取值，加第三种语言（fr/es/…）自动生效，
不需要再改任何守卫。

用法
----
    from unlimited_labels import is_unlimited_label
    if is_unlimited_label(data_cell):
        ...
"""
from __future__ import annotations

import html
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

# 模板侧「无限」这个标签的两个来源：
#   layouts/compare/single.html      → g_unlimited          （国家 Hub 的套餐表）
#   layouts/partials/plan-data-label → compare_provider__trip_data_unlimited
KEYS = ("g_unlimited", "compare_provider__trip_data_unlimited")


def _labels() -> set[str]:
    out = {"unlimited"}          # 英文兜底：万一 key 被改名也不会立刻失效
    for p in sorted((ROOT / "i18n").glob("*.toml")):
        txt = p.read_bytes().decode("utf-8", errors="ignore")
        for k in KEYS:
            pat = re.compile(r"^" + re.escape(k) + r'\s*=\s*"(.*)"\s*$', re.M)
            for m in pat.finditer(txt):
                out.add(html.unescape(m.group(1)).strip().lower())
    return out


UNLIMITED_LABELS: set[str] = _labels()


def is_unlimited_label(cell: str) -> bool:
    """数据列文本是否是「无限」标签（任意语言）。"""
    s = cell.strip().lower()
    return "unlimited" in s or s in UNLIMITED_LABELS


if __name__ == "__main__":
    print(f"ROOT = {ROOT}")
    print(f"UNLIMITED_LABELS = {sorted(UNLIMITED_LABELS)}")
