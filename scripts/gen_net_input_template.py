#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Generate ONE fill-in Markdown file with everything the user provides manually.

Output: _network_data_needed.md
  - Part 1: host networks — 7 brands, each a list of `- {ISO} {Country}: ` lines
            (fill the networks after the colon, `;`-separated, canonical names).
  - Part 2: Opensignal / Ookla — fill-in blocks for the 4 gap countries.
  - Part 3: canonical MNO names per country (reference).
"""
import tomllib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
countries = tomllib.load(open(ROOT / "data" / "countries.toml", "rb"))
carriers = tomllib.load(open(ROOT / "data" / "carriers.toml", "rb"))

BRANDS = ["airalo", "saily", "ubigi", "holafly", "yesim", "alosim", "roamic"]
GAP = {"CN": "China", "IS": "Iceland", "GE": "Georgia", "KE": "Kenya"}

by_name = sorted(countries.items(), key=lambda kv: kv[1]["name"])

L = []
L.append("# 需要你人工提供的「网络数据」清单\n")
L.append("> 填写方式：直接改这个文件，改完发回来即可（或把填好的内容贴在对话里）。")
L.append("> Roami 已补齐，无需填写。其余 7 家品牌的 host networks 待填。\n")

# ---- Part 1 ----
L.append("## 一、host networks（7 家品牌 × 50 国）\n")
L.append("每行格式：`- {ISO} {国家}: {运营商名，多个用 ; 分隔}`。名称照抄第三节规范名；不确定就留空。\n")
L.append("例：`- JP Japan: NTT Docomo;SoftBank`\n")
for brand in BRANDS:
    L.append(f"### {brand}\n")
    for iso, c in by_name:
        L.append(f"- {iso} {c['name']}: ")
    L.append("")

# ---- Part 2 ----
L.append("## 二、Opensignal / Ookla 独立测速报告（4 国缺口）\n")
L.append("其余 46 国已有 Opensignal，只有下面 4 国空白。每国填你查得到的即可（Ookla 可选）。\n")
for iso in ["CN", "IS", "GE", "KE"]:
    name = GAP[iso]
    profs = [p["name"] for p in carriers.get(iso, {}).get("profiles", [])]
    L.append(f"### {name}（{iso}）— 本地运营商：{', '.join(profs)}\n")
    L.append("- Opensignal 报告标题: ")
    L.append("- Opensignal 报告 URL: ")
    L.append("- Opensignal 报告月份: ")
    L.append("- Opensignal 下载冠军+Mbps（1–3 条事实）: ")
    L.append("- Ookla 最快网络+分数/Mbps（可选）: ")
    L.append("- Ookla URL+日期（可选）: ")
    L.append("")

# ---- Part 3 ----
L.append("## 三、各国规范运营商名（填第一节时照抄）\n")
L.append("| 国家 | ISO | 规范名 |")
L.append("|---|---|---|")
for iso, c in by_name:
    names = ", ".join(p["name"] for p in carriers.get(iso, {}).get("profiles", []))
    L.append(f"| {c['name']} | {iso} | {names} |")

(ROOT / "_network_data_needed.md").write_text("\n".join(L) + "\n", encoding="utf-8")
print("wrote _network_data_needed.md")
print("brand sections:", len(BRANDS), "| gap countries:", len(GAP), "| countries:", len(by_name))
