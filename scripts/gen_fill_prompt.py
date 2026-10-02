#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Generate a paste-ready prompt the user can hand to an AI to fill the host-networks
data. Self-contained: embeds the canonical MNO names so the AI can't invent names."""
import tomllib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
countries = tomllib.load(open(ROOT / "data" / "countries.toml", "rb"))
carriers = tomllib.load(open(ROOT / "data" / "carriers.toml", "rb"))

BRANDS = ["airalo", "saily", "ubigi", "holafly", "yesim", "alosim", "roamic"]
by_name = sorted(countries.items(), key=lambda kv: kv[1]["name"])

L = []
L.append("# 提示词（直接复制下面整段发给 AI）\n")
L.append("```\n")
L.append("你是 eSIM 行业数据助手。请帮我补齐一份「7 家 eSIM 品牌 × 50 国，各自连接哪些本地运营商」的清单。\n")
L.append("品牌：airalo、saily、ubigi、holafly、yesim、alosim、roamic（共 7 家）。\n")
L.append("【运营商名称约束 —— 最重要】")
L.append("每个国家只能用下面列出的规范名，一个字都不能改，不得自造、不得翻译、不得用缩写或俗称：")
for iso, c in by_name:
    names = ", ".join(p["name"] for p in carriers.get(iso, {}).get("profiles", []))
    L.append(f"{iso} {c['name']} = {names}")
L.append("【输出格式】")
L.append("每个品牌一个区块，标题写 `### {品牌}`；区块内每国一行：`- {ISO} {国家名}: {运营商1;运营商2}`，多个用英文分号 `;` 分隔。")
L.append("示例：\n### airalo\n- JP Japan: NTT Docomo;SoftBank\n- US United States: T-Mobile;AT&T\n- CN China: ")
L.append("【纪律】")
L.append("1. 只填你能核实的（优先查各品牌官网对应国家页的 host networks；查不到就依据可靠常识，但绝不能瞎猜）。")
L.append("2. 拿不准的国家/品牌，整行留空（`- CN China: ` 冒号后什么都不写），严禁编造运营商名。")
L.append("3. 全部 50 国 × 7 家都要输出，不确定的留空即可，不要省略行。")
L.append("现在开始，输出完整清单。\n")
L.append("```\n")
L.append("\n（上面的规范名表共 50 国，已包含全部允许使用的运营商名。）")

(ROOT / "_fill_prompt_for_ai.md").write_text("\n".join(L) + "\n", encoding="utf-8")
print("wrote _fill_prompt_for_ai.md (%d countries embedded)" % len(by_name))
