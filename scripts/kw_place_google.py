# -*- coding: utf-8 -*-
"""把 Google 采集到的关键词分配到「主题 → 落点位置」。

为什么要这一层：`kw_classify.py` 已经回答了「这个词归哪个 URL」，
但它回答不了「归到这个页面的**哪一段**」。品牌×国家子页有 1,481 个词，
落点全是同一个 URL —— 而它们要的东西完全不同：
    `airalo esim japan review`      → 要「这家稳不稳」
    `airalo esim price japan`       → 要「多少钱」
    `airalo esim japan aktivieren`  → 要「怎么开通」
    `airalo esim china vpn`         → 要「能不能上外网」
一个 URL 装不下这四种意图，所以必须再补一层「**主题 → 页面内的语义位**」。

本脚本只做分配与统计，**不改任何页面**。
输出：docs/keywords/google/kw-placement.csv
    keyword, 词型, 主题, 落点页型, 落点位置, 综合分, 相对热度, 语言, 站内现状
"""
import csv
import pathlib
import re

ROOT = pathlib.Path(__file__).resolve().parent.parent
G = ROOT / "docs" / "keywords" / "google"

# ── 语言判定：德语词要去德语页（/de/…），不能塞进英文页 ──
DE_MARK = re.compile(
    r"erfahrung|funktioniert|bewertung|g(ü|u)nstig|kosten|preis|aktivier|"
    r"\bohne\b|\bkarte\b|welche|\bbeste|\bnetz\b|empfang|zahlen|"
    r"\bf(ü|u)r\b|\bmit\b|\bund\b|\bim\b|\bder\b|\bdie\b|\bdas\b",
    re.I)

# ── 主题规则：**顺序敏感**（先命中先定），每条给「主题 / 落点页型 / 落点位置」──
#    落点位置写的是**语义位**（页面里的一段/一问/一列），不是 CSS 选择器。
RULES = [
    # ── 品牌 × 国家（1,481 词，55% 是验证类）──
    ("品牌×国家",
     r"erfahrung|bewertung|funktioniert nicht|aktivier|g(ü|u)nstig|\bkosten\b",
     "验证·德语评价", "品牌×国家子页（/de/）", "德文 FAQ：Erfahrungen / Aktivierung"),
    ("品牌×国家",
     r"vpn|\bchina\b|hong kong",
     "场景·VPN/受限网络", "品牌×国家子页（中国/中国香港）", "该页 FAQ：VPN 与网络限制"),
    ("品牌×国家",
     r"\breviews?\b|reddit|trustpilot|\blegit\b|scam|worth it|is .{0,14}good",
     "验证·评价", "品牌×国家子页", "新 FAQ Q6：用户反馈与口碑"),
    ("品牌×国家",
     r"not working|doesn.t work|work in|works in|working in|cover|reliable",
     "验证·可用性", "品牌×国家子页", "新 FAQ Q7：用不了怎么办 / 覆盖范围"),
    ("品牌×国家",
     r"activat|install|setup|set up|\bapn\b|\bqr\b|how to",
     "使用·激活", "品牌×国家子页", "新 FAQ Q8：开通与安装步骤"),
    ("品牌×国家",
     r"\brefund|support|cancel|expire|renew|extension",
     "使用·售后", "品牌×国家子页", "新 FAQ Q9：退款与延期"),
    ("品牌×国家",
     r"\bprice|prices|pricing|cost|cheap|discount|deal|coupon|promo|\bcode\b",
     "购买·价格", "品牌×国家子页", "已有 FAQ Q1（价格）+ #plans 表"),
    ("品牌×国家",
     r"\bplans?|packages?|unlimited|top ?up|data|\bgb\b|\bdays?\b",
     "购买·套餐档位", "品牌×国家子页", "已有 #plans 表 + FAQ Q2（无限）"),
    ("品牌×国家",
     r"coverage|network|speed|\b5g\b|lte|carrier|signal|roaming",
     "使用·网络", "品牌×国家子页", "已有 #hostnetwork + FAQ Q4"),
    # ★ 兜底：`airalo esim japan` / `saily esim canada` 这类「品牌+国家」光板词
    ("品牌×国家", r".",
     "品牌×国家·光板词", "品牌×国家子页", "#verdict + H2 已含品牌与国家名"),

    # ── 国家（3,240 词）──
    ("国家·核心",
     r"best esim|best .{0,10}esim|top esim|which esim",
     "国家·选哪家", "国家页", "H1 下方的 verdict 段 + #plans 表头"),
    ("国家·核心",
     r"is esim available|does esim work|do i need|can i get|is there",
     "国家·可用性问答", "国家页", "新 FAQ：这个国家能用 eSIM 吗"),
    ("国家·核心",
     r"reddit|review|worth it|\blegit\b",
     "国家·口碑", "国家页", "新 FAQ：真实用户怎么说（只给入口不印分）"),
    ("国家·核心",
     r"esim for (long stay|student|nomad)|long stay|digital nomad|student",
     "国家·场景/长住", "国家页", "#localnotes 场景段"),
    # ★ 兜底：`esim japan` / `japan esim` —— 这就是 H1 本体
    ("国家·核心", r".",
     "国家·核心", "国家页", "H1 / <title> 主体"),
    ("国家·价格/交易",
     r".", "国家·价格", "国家页", "#plans 表头 + 价格 FAQ"),
    ("国家·规格/流量",
     r"unlimited|data|gb|how much data|\bdays?\b",
     "国家·流量与有效期", "国家页", "#plans 列说明 + 流量 FAQ"),
    ("国家·规格/流量",
     r"number|calls?|voice|sms|text",
     "国家·号码与通话", "国家页", "新 FAQ：要不要本地号码"),
    ("国家·规格/流量", r".", "国家·流量与有效期", "国家页", "#plans 列说明"),
    ("国家·设备兼容",
     r".", "国家·设备", "国家页", "新 FAQ：手机支持吗（链兼容性检查器）"),
    ("国家·落地渠道",
     r"airport|where to buy|buy at|store|kiosk|sim card",
     "国家·落地购买", "国家页", "#localnotes 购买渠道段"),
    ("国家·落地渠道", r".", "国家·落地购买", "国家页", "#localnotes 购买渠道段"),
    ("国家·对比",
     r".", "国家·对比", "国家页", "#tradeoffs 对照段"),
    ("国家·网络覆盖",
     r".", "国家·网络", "国家页", "#localnotes 网络段（已有运营商数据）"),

    # ── 通用（归属首页/指南）──
    ("通用·问题", r"how to|how do|can i|can you|should i|do i|is it",
     "通用·操作问答", "首页 + 指南页", "首页 FAQ / #how-it-works"),
    ("通用·问题", r"what is|what are|explained|meaning|why",
     "通用·定义原理", "指南页", "/guides/what-is-esim/ 正文"),
    ("通用·问题", r".", "通用·操作问答", "首页 + 指南页", "首页 FAQ"),
    ("通用·价格交易", r"price|cost|cheap|cheapest|plan|per gb|gb",
     "通用·价格", "首页", "#price 与 #price-floor 区块"),
    ("通用·价格交易", r".", "通用·价格", "首页", "#price 与 #price-floor 区块"),
    ("通用·规则/规格", r"size|how many|storage|gb|requirement",
     "通用·规格条件", "指南页", "/guides/what-is-esim/ 规格表"),
    ("通用·规则/规格", r".", "通用·规格条件", "指南页", "/guides/what-is-esim/ 规格表"),
    ("通用·设备兼容", r".", "通用·设备兼容", "/guides/esim-compatibility-check/", "正文 + 机型清单"),
    ("通用·全球", r"international|roaming|abroad|global|worldwide",
     "通用·国际漫游", "首页 + 指南页", "首页 FAQ / 漫游指南"),
    ("通用·全球", r"number|calls?|voice|sms",
     "通用·号码通话", "指南页", "新指南段落"),
    ("通用·全球", r".", "通用·国际漫游", "首页 + 指南页", "首页 FAQ"),
    ("通用·对比", r".", "通用·对比", "首页 + 指南页", "#tradeoffs 型对照"),
    ("通用·其他", r"free|trial|prepaid",
     "通用·免费/预付", "首页", "免费试用类问答"),
    # ★ 兜底：`esim size` / `esim requirements` / `esim phone plans` / `esim price`
    #    —— 这几个正是**测到热度**的词，必须落到首页/指南而不是「未归类」
    ("通用·其他", r"size|how many|storage|requirement|spec",
     "通用·规格条件", "指南页", "/guides/what-is-esim/ 规格表"),
    ("通用·其他", r"price|cost|cheap|plan|fee|monthly",
     "通用·价格", "首页", "#price 区块"),
    ("通用·其他", r".", "通用·通用问答", "首页", "首页 FAQ / 指南入口"),

    # ── 其它页型 ──
    ("区域", r".", "区域", "（无区域页）", "建议：区域枢纽页 / 现有区域指南"),
    ("城市", r".", "城市", "（无城市页）", "建议：并入对应国家页 Cities 小节"),
    ("品牌（全局）", r".", "品牌·全局", "品牌 Hub 页", "已有 6 区块（#reality/#whobeats/…）"),
    ("品牌对决", r".", "品牌·对决", "品牌 vs 页", "#verdict 对照段"),
    ("通用·落地渠道", r".", "通用·落地购买", "首页 + 指南页", "购买渠道指南"),

    # ── 兜底 ──
    ("*", r".", "未归类", "（待人工复核）", "—"),
]


def theme_of(kw, typ):
    for want_typ, pat, theme, page, slot in RULES:
        if want_typ != "*" and typ != want_typ:
            continue
        if re.search(pat, kw, re.I):
            return theme, page, slot
    return "未归类", "（待人工复核）", "—"


def main():
    rows = list(csv.DictReader((G / "kw-google-collected.csv").open(encoding="utf-8")))
    heat = {}
    tip = G / "kw-trends-index.csv"
    if tip.is_file():
        for r in csv.DictReader(tip.open(encoding="utf-8")):
            heat[r["keyword"]] = float(r["相对热度"] or 0)

    out = []
    for r in rows:
        theme, page, slot = theme_of(r["keyword"], r["词型"])
        out.append({
            "keyword": r["keyword"],
            "词型": r["词型"],
            "主题": theme,
            "落点页型": page,
            "落点位置": slot,
            "综合分": r["综合分"],
            "相对热度": heat.get(r["keyword"], ""),
            "语言": "de" if DE_MARK.search(r["keyword"]) else "en",
            "站内现状": r["站内现状"],
        })
    out.sort(key=lambda z: (z["主题"], -(float(z["相对热度"]) if z["相对热度"] != "" else -1),
                            -float(z["综合分"])))

    dst = G / "kw-placement.csv"
    with dst.open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=["keyword", "词型", "主题", "落点页型", "落点位置",
                                          "综合分", "相对热度", "语言", "站内现状"])
        w.writeheader()
        w.writerows(out)

    # ── 汇总（现算，不硬编码）──
    import collections
    n = {t: collections.Counter() for t in ("主题", "落点页型", "语言", "站内现状")}
    for r in out:
        for k in n:
            n[k][r[k]] += 1
    gaps = collections.Counter()
    for r in out:
        if r["站内现状"] == "缺口":
            gaps[r["主题"]] += 1

    print("=" * 78)
    print("主题分布（共 %d 词）" % len(out))
    print("=" * 78)
    for t, c in n["主题"].most_common():
        print("  %-22s %6d   其中站内缺口 %d" % (t, c, gaps.get(t, 0)))
    print()
    print("落点页型分布")
    for t, c in n["落点页型"].most_common():
        print("  %-34s %6d" % (t, c))
    print()
    print("语言：", dict(n["语言"]))
    print()
    print("=" * 78)
    print("测到非零热度的词（按主题）")
    print("=" * 78)
    hot = [r for r in out if r["相对热度"] != "" and float(r["相对热度"]) > 0]
    for r in sorted(hot, key=lambda z: -float(z["相对热度"])):
        print("  %8.4f  %-18s %-30s %s" % (
            float(r["相对热度"]), r["主题"], r["落点位置"], r["keyword"]))
    print()
    print("产物 -> %s（%d 行）" % (dst.relative_to(ROOT), len(out)))


if __name__ == "__main__":
    main()
