#!/usr/bin/env python3
# -*- coding: utf-8 -*-
r"""第六十三轮：compare/provider.html 的 9 处「数据串裸插值」接线。

这是 D7 的硬前置：不接线，生成的 499 个德语品牌×国家子页会整列印英文。
已实测（探针页 /de/compare/germany/holafly/）：
  · 套餐名 `Unlimited / 3 Days` 原样进表格（同行 Gültigkeit 列已是 "3 Tage"）
修复依据（探针页证据 + 静态审计）：
  · plan-name.html —— 套餐名（国名 + 结构词本地化），compare/single.html 已用 12 处
  · de-text.html   —— 数据层英文串查 data/de/strings.toml，compare/single.html 已用 3 处

★ 恒等保证：两个 partial 在英语侧都恒等返回
  （plan-name: $en == $loc ⇒ 词表值 == 源词；de-text: en 站无 data/en/strings.toml ⇒ $d.strings 为 nil）
  ⇒ 英语产物必须逐字节不变。构建后用 verify_no_regression.py --diff 复核。

不做的事：`fup_allowance` / `fup_drop` 也接 de-text，但**表里暂无条目**
（D 段只覆盖 fup_note / promo_label / quirks），故这两列暂时仍显示英文 ——
接线本身不会更糟（de-text 未命中即原样返回），补表是下一批。
"""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
P = ROOT / "layouts" / "compare" / "provider.html"

# (旧片段, 新片段) —— 全部带足上下文，保证唯一
EDITS: list[tuple[str, str]] = [
    # ① JSON-LD 逐套餐 Offer 的 name
    ('      "@type" "Offer"\n      "name" .name\n',
     '      "@type" "Offer"\n'
     '      "name" (partial "plan-name.html" (dict "name" .name "iso" $iso))\n'),
    # ② 主价格表套餐名
    ('<span class="font-semibold text-ink-950">{{ .name }}</span>',
     '<span class="font-semibold text-ink-950">'
     '{{ partial "plan-name.html" (dict "name" .name "iso" $iso) }}</span>'),
    # ③ FUP 表套餐名
    ('<td class="text-ink-700">{{ .name }}</td>',
     '<td class="text-ink-700">{{ partial "plan-name.html" (dict "name" .name "iso" $iso) }}</td>'),
    # ④ #reality 的 FUP 额度
    ('<p class="mt-2 font-display text-lg font-bold text-ink-950">{{ .fup_allowance }}</p>',
     '<p class="mt-2 font-display text-lg font-bold text-ink-950">'
     '{{ partial "de-text.html" .fup_allowance }}</p>'),
    # ⑤ #reality 的限速值（单位串，表里未收录，接线后仍原样）
    ('<p class="mt-1 text-xs font-semibold text-accent-700">{{ i18n "compare_provider__fup_drop_to" | safeHTML }} {{ . }}</p>',
     '<p class="mt-1 text-xs font-semibold text-accent-700">{{ i18n "compare_provider__fup_drop_to" | safeHTML }} {{ partial "de-text.html" . }}</p>'),
    # ⑥ #reality 的 FUP 说明（表里已有 14 条）
    ('<p class="mt-2 text-sm leading-relaxed text-ink-500">{{ .fup_note }}</p>',
     '<p class="mt-2 text-sm leading-relaxed text-ink-500">'
     '{{ partial "de-text.html" .fup_note }}</p>'),
    # ⑦ FUP 表的那一列
    ('<td class="text-xs leading-relaxed text-ink-500">{{ .fup | default (i18n "compare_provider__no_fup_published" | safeHTML) }}</td>',
     '<td class="text-xs leading-relaxed text-ink-500">'
     '{{ partial "de-text.html" .fup | default (i18n "compare_provider__no_fup_published" | safeHTML) }}</td>'),
    # ⑧ 本地须知 quirks
    ('        <span>{{ . }}</span>\n',
     '        <span>{{ partial "de-text.html" . }}</span>\n'),
    # ⑨ 促销标签（de-text 已有 10 条）
    ('{{ i18n "compare_provider__promo_line" (dict "label" $p.promo_label) | safeHTML }}',
     '{{ i18n "compare_provider__promo_line" (dict "label" (partial "de-text.html" $p.promo_label)) | safeHTML }}'),
]


def main() -> int:
    dry = "--dry" in sys.argv
    text = P.read_bytes().decode("utf-8")
    if "\r\n" in text:
        print("!! 前置就含 CRLF"); return 1

    errs: list[str] = []
    for old, new in EDITS:
        n = text.count(old)
        if n != 1:
            errs.append(f"片段命中 {n} 次（期望 1）：{old[:70]!r}")
    # 反向断言：这些 partial 在改之前不该被调用超过已知次数
    for name, want in (("plan-name.html", 0), ("de-text.html", 0)):
        got = text.count(f'partial "{name}"')
        if got != want:
            errs.append(f'{name} 改前已有 {got} 次调用（期望 {want}）—— 模板可能已被改过')
    if errs:
        for e in errs:
            print(f"!! {e}")
        print(f"\n{len(errs)} 处问题，未写盘。")
        return 1
    print(f"断言全过：{len(EDITS)} 处片段各命中 1 次；改前两个 partial 均 0 次调用。")
    if dry:
        print("--dry：未写盘。")
        return 0

    for old, new in EDITS:
        text = text.replace(old, new, 1)
    data = text.encode("utf-8")
    if b"\r\n" in data:
        print("!! 产物出现 CRLF"); return 1
    P.write_bytes(data)

    after = P.read_bytes().decode("utf-8")
    print(f"OK 接线 {len(EDITS)} 处（provider.html {len(data)} B）")
    print(f"   plan-name.html 调用 {after.count('partial \"plan-name.html\"')} 次"
          f" / de-text.html 调用 {after.count('partial \"de-text.html\"')} 次")
    return 0


if __name__ == "__main__":
    sys.exit(main())
