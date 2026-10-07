#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""FAQ 答案骨架库 —— 逐国分配 + 一次性迁移（第四十二轮，2026-10-07）。

── 为什么要有它 ────────────────────────────────────────────────────────────
第四十一轮把三条含数字的答案（最便宜 / unlimited 计数 / Airalo-Holafly 报价）
改成了 {token}，数字从此不会过期。但**句架仍然只有一副**：49 个国家（jp 除外）
逐字相同，只有数字位不同 —— 50 页里同一句话出现 49 次，是模板级重复内容。

本轮把每条答案拆成三个**修辞槽位**，每槽 7 个片段：
    open  直接回答（第一句，最可能被答案引擎摘走的那句）
    body  数据事实（品牌 / 价格 / 计数 / 区间）
    close 行动建议
任意组合都读得通，因为每个槽位只干一件事。

── 分配：拉丁方阵（这决定了「任意两国最多只共用一句话」）────────────────────
    a = i % 7      b = i // 7      c = (a + b) % 7        （i = 0..48）
(a, b) 覆盖 7×7 全部 49 个格子且各一次；固定 b 时 c 是 a 的双射 ⇒ (a, c) 也各一次；
固定 a 时 c 是 b 的双射 ⇒ (b, c) 也各一次。于是**任意两国的三元组至多在一个分量上相同**，
即两页之间最多共用一句。这不是调参调出来的，是结构保证的 —— scripts/check_faq_facts.py
的 R10 会把这个不变量钉死（骨架两两不同 + 至多一句相同）。

⚠ 池子必须 ≥ 7：要 49 个国家两两 (a, b) 不重复，需要 |pool|² ≥ 49。改成 6 就会退化。

── 只替换「已知的旧文本」──────────────────────────────────────────────────
按 q 前缀定位，然后：
    已经是目标文本      -> 跳过（幂等）
    匹配已知的旧骨架    -> 替换
    其他（人工润色过）  -> **拒绝改写并报警**
后一条很重要：本脚本是迁移器不是生成器，`data/faqs/*.toml` 是内容源，不是构建产物。

── 顺带修掉的 Q6 事实缺陷（同批，2026-10-07）────────────────────────────────
49 国的 Q6 原文是「Regional Asia/continental plans from Airalo and Nomad bundle
{country} with neighbors」—— 对法国、美国、阿根廷这类国家是**自相矛盾**的句子
（我们数据集里根本没有区域档，见下），且 41 国逐字相同。现改为用 countries.toml 的
`neighbors` 驱动：答案点名**问题里问的那个邻国**（英国的问题问法国，就答法国），
7 个没有邻国的国家（HR/IS/CR/IL/MA/ZA/KE）走语法成立的兜底短语。

用法：
  python -X utf8 scripts/faq_frames.py --dry     # 只报改动
  python -X utf8 scripts/faq_frames.py           # 真写（只替换认得的旧骨架，其余拒绝）
  python -X utf8 scripts/faq_frames.py --force   # 改了片段库本身要重刷全站时用；会覆盖人工润色
  python -X utf8 scripts/faq_frames.py --check   # 只校验分配的不变量与片段写法，不碰文件
"""
from __future__ import annotations

import json
import sys
import tomllib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FAQ_DIR = ROOT / "data" / "faqs"

POOL = 7  # 每槽片段数；改成小于 7 会破坏「至多共用一句」

# ══════════════════════════════════════════════════════════════════════════════
# Q1「最便宜」—— open 必须含 {cheap_brand} 与 ${cheap_price}（守卫 R5）
# ══════════════════════════════════════════════════════════════════════════════
Q1 = {
    "open": [
        "{cheap_brand}'s {cheap_plan} is the cheapest {country} plan we track, at ${cheap_price}.",
        "On entry price, {cheap_brand} leads {country} with {cheap_plan} at ${cheap_price}.",
        "The lowest price on this page is {cheap_brand}'s {cheap_plan} - ${cheap_price} for {country}.",
        "{cheap_brand} holds the headline number for {country}: {cheap_plan} at ${cheap_price}.",
        "Cheapest plan for {country}: {cheap_brand}'s {cheap_plan}, ${cheap_price}.",
        "Start with {cheap_brand}, whose {cheap_plan} is the cheapest {country} plan at ${cheap_price}.",
        "At ${cheap_price}, {cheap_brand}'s {cheap_plan} is the cheapest way online in {country}.",
    ],
    "body": [
        # ⚠ 不能写「它也是 $/天 最低」——实测 50/50 国**都不成立**：绝对价最低的是最小档，
        #   而 $/天 最低的通常是长周期大流量档。这里只陈述 perDay = price/days 这个恒等式。
        "That is ${cheap_perday}/day across the plan's validity window.",
        "Across the {plan_count} {country} plans from {brand_count} providers on this page, the best cost per gigabyte is {value_brand}'s {value_plan} at ${value_pergb}/GB.",
        "The next cheapest brand is {runner_brand}, at ${runner_price}.",
        "Price and value are different measurements, and on cost per gigabyte the winner is {value_brand}'s {value_plan} at ${value_pergb}/GB.",
        "That works out at ${cheap_perday} a day, which suits a short stop better than a long one.",
        "Best value per gigabyte is a separate question, and the answer here is {value_brand}'s {value_plan} at ${value_pergb}/GB.",
        "{runner_brand} sits next at ${runner_price}, and the strongest per-gigabyte rate comes from {value_brand}'s {value_plan} at ${value_pergb}/GB.",
    ],
    "close": [
        "Match the plan to your trip length rather than chasing the single lowest number.",
        "Decide your days and your rough gigabytes first, then pick the plan that fits both.",
        "Small buckets suit city breaks, while longer stays are usually cheaper per gigabyte with a bigger plan.",
        "If you only need maps and messaging the entry price is enough, and anyone streaming should shop on $/GB.",
        "Check the validity window alongside the price, because a cheap plan that expires early is not cheap.",
        "The table above sorts every option, so compare the shape of a plan as well as its price.",
        "Buy for the trip you are actually taking rather than for the lowest figure on the page.",
    ],
}

# ══════════════════════════════════════════════════════════════════════════════
# Q2「真的无限吗」—— open 必须含独立成词的 {unl_count}，body 必须含 {unl_brand} 与 ${unl_perday}
# ⚠ {unl_count} 必须前后带空格（守卫用 " N " 匹配），不能写成 "({unl_count})"
# ⚠ {unl_allowance} 的值可能是整句（ubigi「Varies by plan - published per plan page」），
#   只能放在**冒号之后**（冒号后大写是合法英文），不能内嵌进从句
# ══════════════════════════════════════════════════════════════════════════════
Q2 = {
    "open": [
        "Not quite - all {unl_count} 'unlimited' {country} plans carry a fair-use policy.",
        "No. Each of the {unl_count} unlimited {country} plans caps its daily full-speed allowance.",
        "Big rather than boundless: {unl_count} unlimited {country} plans all apply fair-use rules.",
        "Capped, not unlimited - the {unl_count} unlimited plans for {country} throttle once the daily allowance is spent.",
        "Only within limits. The {unl_count} unlimited {country} plans slow to a published speed after a set allowance each day.",
        "'Unlimited' here means unlimited data, not unlimited speed: {unl_count} {country} plans apply fair-use caps.",
        "Treat them as capped: {unl_count} unlimited {country} plans each state a daily allowance and a fallback speed.",
    ],
    "body": [
        "Day rates across the set span {unl_perday_range}, and the cheapest is {unl_brand} at ${unl_perday}/day - ${unl_price} for {unl_days} days.",
        "{unl_brand} offers the best daily rate at ${unl_perday} ({unl_days} days for ${unl_price}), against a market range of {unl_perday_range}.",
        "The spread is wide - {unl_perday_range} a day - and {unl_brand} sits at the bottom of it at ${unl_perday}/day over {unl_days} days.",
        "{unl_brand} comes out cheapest per day at ${unl_perday}, and the full band here spans {unl_perday_range}.",
        "Duration moves the rate as much as the cap does: {unl_perday_range} per day across the set, with {unl_brand} lowest at ${unl_perday} for {unl_days} days.",
        "The best day rate belongs to {unl_brand} - ${unl_perday} for a {unl_days}-day package at ${unl_price} - and the market spans {unl_perday_range}.",
        "Prices run {unl_perday_range} per day depending on duration, and {unl_brand} is the cheapest at ${unl_perday}/day.",
    ],
    "close": [
        "What {unl_brand} publishes: {unl_allowance}; after that, {unl_drop}.",
        "The part people miss is what happens after the cap: {unl_drop}.",
        "Two figures decide whether a capped plan suits you, and {unl_brand} publishes both: {unl_allowance}, then {unl_drop}.",
        "Check the fallback speed before you commit, because that is what you get after the daily allowance: {unl_drop}.",
        "Treat the published terms as the real limit: {unl_allowance}, then {unl_drop}.",
        "Throttling rather than disconnection is the trade-off, with speeds falling to {unl_drop} once the allowance is spent.",
        "Compare caps across brands before buying, because the throttled speed is the number that matters and {unl_brand}'s is {unl_drop}.",
    ],
}

# ══════════════════════════════════════════════════════════════════════════════
# Q3「Airalo 还是 Holafly」—— body 必须含 ${ah_airalo_pergb}，close 必须含 ${ah_holafly_price}
# ══════════════════════════════════════════════════════════════════════════════
Q3 = {
    "open": [
        "They sell different things, so the answer depends on how you use data.",
        "Different products: Airalo sells fixed data buckets, Holafly sells unlimited days.",
        "Neither is the cheapest plan on this page, and the two are not competing on the same terms either.",
        "It comes down to shape - buckets of data against unlimited days.",
        "Pick by usage pattern, because the two brands do not price the same way at all.",
        "Airalo and Holafly solve different problems, so compare the models before the prices.",
        "The honest answer is that these two are not interchangeable.",
    ],
    "body": [
        # ⚠ 别写「计量档永不节流」这类绝对化断言 —— 只能陈述「买的是固定流量包」这一构造成立的事实
        "Airalo's best {country} rate is ${ah_airalo_pergb}/GB - {ah_airalo_plan} at ${ah_airalo_price} - and that is a fixed bucket rather than a daily allowance.",
        "Airalo sells buckets: its sharpest {country} rate is ${ah_airalo_pergb}/GB ({ah_airalo_plan}, ${ah_airalo_price}).",
        "On Airalo's side the best value is ${ah_airalo_pergb}/GB - {ah_airalo_plan} at ${ah_airalo_price} - priced per gigabyte rather than per day.",
        "Airalo's {ah_airalo_plan} works out at ${ah_airalo_pergb}/GB for ${ah_airalo_price}, and what you buy is what you get.",
        "For {country}, Airalo's cheapest rate per gigabyte is ${ah_airalo_pergb} ({ah_airalo_plan}, ${ah_airalo_price}).",
        "Airalo's way into {country} is a data bucket - {ah_airalo_plan} at ${ah_airalo_price}, or ${ah_airalo_pergb}/GB at its sharpest.",
        "Airalo's strongest {country} offer is ${ah_airalo_pergb}/GB, sold as {ah_airalo_plan} for ${ah_airalo_price}.",
    ],
    "close": [
        "Holafly sells unlimited days instead, its smallest {country} package being {ah_holafly_days} days for ${ah_holafly_price} (${ah_holafly_perday}/day).",
        "Holafly's model is daily unlimited, starting at {ah_holafly_days} days for ${ah_holafly_price} - ${ah_holafly_perday}/day - so heavy use costs the same as light use.",
        "Holafly only sells unlimited by the day: {ah_holafly_days} days for ${ah_holafly_price}, or ${ah_holafly_perday} a day.",
        "Take Holafly if you would rather not count gigabytes, since its {country} packages start at ${ah_holafly_price} for {ah_holafly_days} days (${ah_holafly_perday}/day), and take Airalo for a light, short trip.",
        "Holafly's floor price for {country} is ${ah_holafly_price} over {ah_holafly_days} days (${ah_holafly_perday}/day), with no data counter to watch.",
        "The flat-rate option is Holafly, at {ah_holafly_days} days from ${ah_holafly_price} - ${ah_holafly_perday}/day whatever you use.",
        "Where Holafly wins is predictability, from ${ah_holafly_price} for {ah_holafly_days} days (${ah_holafly_perday}/day), and where Airalo wins is a short, light trip.",
    ],
}

# ══════════════════════════════════════════════════════════════════════════════
# Q6「一张 eSIM 能覆盖 X 和邻国吗」—— 用 {neighbor} / {neighbors_all}
# ⚠ 两句都不能拿 {neighbor} / {neighbors_all} 起句：无邻国的 7 国兜底短语是小写开头，
#   顶着句号会不成句。必须让它们落在句中。
# ══════════════════════════════════════════════════════════════════════════════
Q6 = [
    "Not with a single-country plan. Everything in our {country} tables is scoped to {country} alone, so a trip that also takes in {neighbor} needs either a second country plan or a regional bundle.",
    "Only with a regional package, because the country plans on this page do not cross borders. The markets around {country} all have their own tables here - {neighbors_all} among them - so price a regional bundle against two single-country plans.",
    # ⚠ 每个变体都必须含 {country}：互称邻国的一对国家（法国↔爱尔兰都指向 UK）若变体里没有
    #   {country}，就会渲染出**逐字相同**的一段（实测撞过）。faq_frames.py --check 与
    #   check_faq_facts.py 的 R10 都断言这一条。
    "Not with a country plan alone, because {country} plans stop at the border. Adding {neighbor} means a regional bundle or a second plan, and the two-country arithmetic is worth doing before you buy.",
    "Not on a single-country plan. If the itinerary continues from {country} into {neighbor}, compare a regional package with two separate plans, since the tables here price each market on its own.",
    "Yes, but only through a multi-country plan, because nothing in our {country} tables covers a second country. Look for a regional package that includes {neighbor} and compare its $/GB with two single-country plans.",
    "One country per plan, so a {country} eSIM stops working at the border. A regional bundle or a second plan is the way to add {neighbor}, and both are worth pricing against simply buying two.",
    "Only via a regional plan, because the {country} tables here are scoped to one market. Crossing into {neighbor} means either a regional package or a second plan, and the per-gigabyte rate is what tells them apart.",
]

SLOTS = [
    ("What is the cheapest eSIM for", Q1),
    ("Is unlimited eSIM data in", Q2),
    ("Airalo or Holafly for", Q3),
]

# ── 旧文本识别：只替换认得的，其余拒绝（保护人工润色）────────────────────────
LEGACY = {
    "What is the cheapest eSIM for": (
        "{cheap_brand}'s {cheap_plan} at ${cheap_price} (${cheap_perday}/day) is the cheapest plan we track.",
    ),
    "Is unlimited eSIM data in": (
        "Not quite. All {unl_count} 'unlimited' plans for {country} apply fair-use policies",
    ),
    "Airalo or Holafly for": (
        "Different animals. Airalo's best rate for {country} is ${ah_airalo_pergb}/GB",
    ),
}
LEGACY_Q6 = (
    "Regional Asia/continental plans from Airalo and Nomad bundle",
    "No single-country plan here bundles neighbors",
)
JP_Q5_OLD = ("Every provider we track - Airalo, aloSIM, Holafly, Roami, Roamic, Saily, Ubigi and Yesim -",)
JP_Q5_NEW = "Every provider we track - {brands_list} -"


# ── 数据 ──────────────────────────────────────────────────────────────────────
def load():
    countries = tomllib.loads((ROOT / "data" / "countries.toml").read_text(encoding="utf-8"))
    known = {k for k, v in countries.items() if isinstance(v, dict) and v.get("name")}
    return countries, known


def order(countries) -> list[str]:
    """分配顺序 = ISO 升序，jp 除外（jp 保留手写的分析口吻）。"""
    return [i for i in sorted(countries) if i != "JP" and isinstance(countries[i], dict)
            and countries[i].get("name")]


def assigned(countries) -> dict[str, dict]:
    """回传 {iso: {"q1": (...), "q2": (...), "q3": (...), "q6": int}}。"""
    isos = order(countries)
    out: dict[str, dict] = {}
    no_nb = [i for i in isos if not countries[i].get("neighbors")]
    for i, iso in enumerate(isos):
        a, b = i % POOL, i // POOL
        c = (a + b) % POOL
        out[iso] = {"q1": (a, b, c), "q2": (a, b, c), "q3": (a, b, c),
                    "q6": i % POOL, "_i": i}
    # 无邻国的 7 国各分到**不同**的 Q6 变体：它们的兜底短语按 region 生成，
    # 同 region（HR/IS 都是 Europe）撞同一变体会渲染出逐字相同的一段话。
    for rank, iso in enumerate(no_nb):
        out[iso]["q6"] = rank
    return out


def answer(pools: dict, idx: tuple[int, int, int]) -> str:
    a, b, c = idx
    return " ".join([pools["open"][a], pools["body"][b], pools["close"][c]])


# ── 校验分配的不变量 ─────────────────────────────────────────────────────────
def verify(countries) -> list[str]:
    errs: list[str] = []
    a = assigned(countries)
    isos = order(countries)
    if len(isos) != 49:
        errs.append(f"参与分配的国家数应为 49，实际 {len(isos)}")
    for key in ("q1", "q2", "q3"):
        tri = [a[i][key] for i in isos]
        if len(set(tri)) != len(tri):
            errs.append(f"{key}: 三元组有重复 —— 会有两页逐字同文")
        for x, y in ((0, 1), (0, 2), (1, 2)):
            pairs = [(t[x], t[y]) for t in tri]
            dup = len(pairs) - len(set(pairs))
            if dup:
                errs.append(f"{key}: 第 {x}/{y} 槽有 {dup} 对重复 —— 两国会共用两句")
    # 池子大小必须 ≥ 7（否则上面的不变量数学上不可能成立）
    for pre, pools in SLOTS:
        for k in ("open", "body", "close"):
            if len(pools[k]) != POOL:
                errs.append(f"{pre}: {k} 片段数 {len(pools[k])} != {POOL}")
            if len(set(pools[k])) != len(pools[k]):
                errs.append(f"{pre}: {k} 有重复片段")
    if len(set(Q6)) != len(Q6):
        errs.append("Q6 有重复变体")
    # 每个 Q6 变体都必须含 {country}：互称邻国的一对国家（FR↔IE 都指向 UK）若变体里没有
    # {country}，渲染出来就是逐字相同的一段 —— 实测撞过。
    for i, f in enumerate(Q6):
        if "{country}" not in f:
            errs.append(f"Q6 V{i} 缺 {{country}} —— 互称邻国的两国会渲染成同一段: {f[:70]}")
    # 片段里不得混入真实数字（必须走 token）
    import re
    for pre, pools in SLOTS:
        for k, frags in pools.items():
            for f in frags:
                if re.search(r"\$\d", f):
                    errs.append(f"{pre}/{k} 片段里写死了价格: {f[:60]}")
                # {country} 的值是 "USA" / "Japan" 这种无冠词形式，"the {country}" 会渲染出 "the Japan"
                if "the {country}" in f:
                    errs.append(f"{pre}/{k} 用了 'the {{country}}': {f[:60]}")
    for f in Q6:
        if re.search(r"\$\d", f):
            errs.append(f"Q6 片段里写死了价格: {f[:60]}")
    # {neighbor} / {neighbors_all} 的无邻国兜底是小写短语，不能顶着句号起句
    for f in Q6:
        for tok in ("{neighbor}", "{neighbors_all}"):
            if f.startswith(tok) or f". {tok}" in f:
                errs.append(f"Q6 让 {tok} 起句了（兜底短语小写会不成句）: {f[:60]}")
    # Q2 的 open 必须让 {unl_count} 前后带空格（守卫 R6 用 " N " 匹配）
    for f in Q2["open"]:
        if " {unl_count} " not in f" {f} ":
            errs.append(f"Q2/open 的 {{unl_count}} 没有独立成词（守卫 R6 会判错）: {f[:60]}")
    return errs


# ── 迁移 ──────────────────────────────────────────────────────────────────────
def rewrite(iso: str, plan: dict | None, dry: bool, stats: dict, force: bool = False) -> list[str]:
    """plan=None 表示只跑「历史附加规则」（jp Q5），不碰三条答案。"""
    path = FAQ_DIR / f"{iso}.toml"
    raw = path.read_bytes().decode("utf-8")
    nl = "\r\n" if "\r\n" in raw else "\n"
    lines = raw.split(nl)

    want: list[tuple[str, str, tuple[str, ...]]] = []
    if plan is not None:
        for (pre, pools), key in zip(SLOTS, ("q1", "q2", "q3")):
            want.append((pre, answer(pools, plan[key]), LEGACY[pre]))
        want.append(("Can one eSIM cover", Q6[plan["q6"]], LEGACY_Q6))

    changes: list[str] = []
    pending: tuple[str, str, tuple[str, ...]] | None = None
    for i, line in enumerate(lines):
        s = line.strip()
        if s.startswith("q = "):
            q = json.loads(s[4:].strip())
            pending = next((w for w in want if q.startswith(w[0])), None)
            continue
        if s.startswith("a = ") and pending:
            old = json.loads(s[4:].strip())
            _, new, legacy = pending
            key = pending[0][:12]
            if old == new:
                stats["skip"] += 1
            elif force or any(old.startswith(x) for x in legacy):
                lines[i] = "a = " + json.dumps(new, ensure_ascii=False)
                stats["done"] += 1
                changes.append(f"  [{iso}] {key}… 旧骨架 -> 新骨架")
            else:
                stats["refuse"] += 1
                changes.append(f"  [{iso}] {key}… ⚠ 内容不认识，拒绝改写: {old[:70]!r}")
            pending = None
            continue
        # 历史规则（第四十一轮已执行，保留以便在干净检出上重跑）：jp Q5 品牌枚举 -> token
        if iso == "JP" and JP_Q5_OLD[0] in line:
            lines[i] = line.replace(JP_Q5_OLD[0], JP_Q5_NEW)
            stats["done"] += 1
            changes.append("  [JP] 品牌枚举 -> {brands_list}")
    if changes and not dry:
        path.write_bytes(nl.join(lines).encode("utf-8"))
    return changes


def main() -> int:
    countries, _ = load()
    mode = sys.argv[1] if len(sys.argv) > 1 else ""
    errs = verify(countries)
    if errs:
        print("ERROR 分配不变量被破坏：")
        for e in errs:
            print("  " + e)
        return 1
    if mode == "--check":
        print("OK: 分配不变量成立（三元组两两不重复 / 任意两槽至多共用一对 / 片段无写死价格）")
        return 0

    dry = mode == "--dry"
    force = "--force" in sys.argv
    plan = assigned(countries)
    stats = {"done": 0, "skip": 0, "refuse": 0}
    all_changes: list[str] = []
    for iso in sorted(plan):
        all_changes += rewrite(iso, plan[iso], dry, stats, force)
    all_changes += rewrite("JP", None, dry, stats, force)  # jp 三条答案保留手写，只跑历史附加规则
    for c in all_changes:
        print(c)
    print(f"\n{'[dry-run] ' if dry else ''}改写 {stats['done']} 处 / 已是目标 {stats['skip']} 处 / "
          f"拒绝 {stats['refuse']} 处（{len(plan)} 国 + jp 附加规则）")
    return 1 if stats["refuse"] else 0


if __name__ == "__main__":
    sys.exit(main())
