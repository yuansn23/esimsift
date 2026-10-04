#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""i18n 翻译进度报告 —— 任意语言「翻了几成 / 下一批翻哪些」。

背景：`scripts/check_i18n.py` 只保证各语言的 key 集合对齐（不漏 key、不多 key），
它**不会**告诉你某条到底还是不是英文。做多语言时最常问的两个问题它答不了：

  1. 德语现在翻了几成？
  2. 下一批该翻哪些 key？

本脚本补上这两件事。

用法
  python -X utf8 scripts/i18n_coverage.py                  # 全部语言总览 + 未译 Top 15 前缀
  python -X utf8 scripts/i18n_coverage.py de               # 只看德语
  python -X utf8 scripts/i18n_coverage.py de --prefix compare_single
                                                           # 列出该前缀下所有未译 key 的值
  python -X utf8 scripts/i18n_coverage.py de --prefix compare_single --limit 40

判定口径（重要）
  值 == 英文原值 → 视为「未译」。
  少数词德语与英文同形（eSIM / SMS / Roami / Ubigi…），会被误判为未译，
  这类误差量级约 3%，忽略即可 —— 它不影响「还剩多少要翻」的判断。

为什么不用 tomllib
  i18n 值是单行带转义的字符串（跨行文本写成字面 \\r\\n），行级解析即可，
  且这样能保留「空值」与「缺失」的区别。
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
I18N_DIR = ROOT / "i18n"

KV_RE = re.compile(r'^([A-Za-z0-9_]+)\s*=\s*"((?:[^"\\]|\\.)*)"', re.M)


def parse(path: Path) -> dict[str, str]:
    """按行解析 key = "value"（值不跨行）。"""
    return {m.group(1): m.group(2) for m in KV_RE.finditer(path.read_text(encoding="utf-8"))}


def prefix_of(key: str) -> str:
    if "__" in key:
        return key.split("__", 1)[0]
    if key.startswith("g_"):
        return "g_*（全站通用短词）"
    return "(无前缀)"


def main(argv: list[str]) -> int:
    langs = sorted(p.stem for p in I18N_DIR.glob("*.toml") if p.stem != "en")
    want = [a for a in argv if not a.startswith("--")]
    prefix = None
    limit = 0
    if "--prefix" in argv:
        i = argv.index("--prefix")
        prefix = argv[i + 1] if i + 1 < len(argv) else None
    if "--limit" in argv:
        i = argv.index("--limit")
        limit = int(argv[i + 1]) if i + 1 < len(argv) else 0

    en_path = I18N_DIR / "en.toml"
    if not en_path.exists():
        print(f"找不到 {en_path}")
        return 1
    en = parse(en_path)
    print(f"基准语言 en.toml：{len(en)} 个 key\n")

    if not langs:
        print("i18n/ 下没有其它语言文件 —— 还没有开第二语言。")
        return 0

    selected = [lang for lang in langs if not want or lang in want]
    if not selected:
        print(f"没有匹配的语言 {want}（可选：{', '.join(langs)}）")
        return 1

    for lang in selected:
        path = I18N_DIR / f"{lang}.toml"
        d = parse(path)
        missing = sorted(k for k in en if k not in d)
        extra = sorted(k for k in d if k not in en)
        translated = [k for k in en if k in d and d[k] != en[k]]
        placeholder = [k for k in en if k in d and d[k] == en[k]]
        pct = (len(translated) / len(en) * 100) if en else 0

        print("=" * 74)
        print(f"{lang}.toml —— {len(d)} key")
        print("=" * 74)
        bar_len = 40
        filled = int(bar_len * len(translated) / len(en)) if en else 0
        print(f"  已译      {len(translated):4d}  [{'█' * filled}{'·' * (bar_len - filled)}] {pct:5.1f}%")
        print(f"  英文占位  {len(placeholder):4d}   ← 待翻译的量")
        if missing:
            print(f"  ❌ 缺失    {len(missing):4d}   （en 有、本语言没有 → build 会 FAIL）")
            for k in missing[:10]:
                print(f"       - {k}")
        if extra:
            print(f"  ❌ 多余    {len(extra):4d}   （本语言有、en 没有 → build 会 FAIL）")
            for k in extra[:10]:
                print(f"       + {k}")
        if not missing and not extra:
            print("  ✅ key 与 en 完全对齐")

        # 按前缀分组（只统计未译）
        groups: dict[str, list[str]] = {}
        for k in placeholder:
            groups.setdefault(prefix_of(k), []).append(k)
        if groups:
            ranked = sorted(groups.items(), key=lambda kv: -len(kv[1]))
            print(f"\n  未译 key 按前缀（共 {len(ranked)} 组，Top 15）：")
            for name, keys in ranked[:15]:
                print(f"    {len(keys):4d}  {name}")

        if prefix:
            hit = groups.get(prefix)
            if not hit:
                print(f"\n  --prefix {prefix}：没有未译 key（要么已译完，要么前缀名不对）")
            else:
                print(f"\n  --prefix {prefix}：{len(hit)} 条未译")
                show = hit[:limit] if limit else hit
                for k in show:
                    print(f'    {k} = "{en[k][:96]}"')
                if limit and len(hit) > limit:
                    print(f"    … 还有 {len(hit) - limit} 条")
        print()

    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
