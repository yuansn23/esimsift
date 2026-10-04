# -*- coding: utf-8 -*-
"""多语言规则表 —— 单一事实源。

新增语言时**只改 hugo.toml**（`[languages.<lang>]`），本文件负责回答两个问题：
  1. 该语言的产物落在 public/ 下哪个目录前缀？
  2. 该语言的标题里允许 en/em dash 吗？

未启用的语言不会出现在任何豁免集合里，因此单语言（当前仅 en）时
所有校验行为与改造前**完全一致**。

注：原先还有一张 LATIN_SCRIPT 语言表 + 非拉丁字符禁令（含合并 data/<lang>/ 的
豁免），2026-10-03 按站点决策整体移除 —— 站点要做多语言，禁令本身是障碍。
"""
from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
HUGO_TOML = ROOT / "hugo.toml"

# 标题里使用 en/em dash 属于正常排版的语言
DASH_OK = {
    "de", "fr", "es", "it", "pt", "nl", "pl", "cs", "sk", "sv", "da", "no",
    "fi", "hu", "ro", "ru", "uk", "ja", "ko", "zh",
}


def _read() -> str:
    return HUGO_TOML.read_text(encoding="utf-8")


def enabled_langs() -> tuple[list[str], str]:
    """返回 (全部已声明语言, 默认语言)。"""
    txt = _read()
    m = re.search(r'^defaultContentLanguage\s*=\s*"([^"]+)"', txt, re.M)
    default = m.group(1) if m else "en"
    return re.findall(r"^\[languages\.([A-Za-z0-9_-]+)\]", txt, re.M), default


def in_subdir() -> bool:
    m = re.search(r"^defaultContentLanguageInSubdir\s*=\s*(\w+)", _read(), re.M)
    return bool(m and m.group(1) == "true")


def output_prefix(lang: str) -> str:
    """该语言产物在 public/ 下的目录前缀（默认语言不落子目录 → 空串）。"""
    langs, default = enabled_langs()
    if lang == default and not in_subdir():
        return ""
    return f"{lang}/"


def _prefixes(pred) -> set[str]:
    langs, _ = enabled_langs()
    return {output_prefix(l) for l in langs if pred(l)}


def dash_ok_prefixes() -> set[str]:
    """public/ 下标题允许 en/em dash 的目录前缀（空集 = 全站禁止）。"""
    return _prefixes(lambda l: l in DASH_OK)


def under_any(path: str, prefixes: set[str]) -> bool:
    """path 是否落在任一前缀下。空前缀 '' 表示全站命中。"""
    return any(path.startswith(p) for p in prefixes)
