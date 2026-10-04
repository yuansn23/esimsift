#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""给 data/providers.toml 的 8 个 [<brand>.info] 补 trustpilot 档案字段。

纪律：**只存链接，不存分数。**
原因：同一品牌在不同 Trustpilot 地区域名下聚合成不同值（Airalo 实测 3.9 / 4.0 / 4.1），
且本机抓取被反爬墙拦截（WebFetch 走 "Verifying your connection..."、curl 全 403），
无法给出「有据可查」的单一分数。品牌页因此改为「教读者自己读评价页 + 给可点开的档案链接」。

roami 例外：域名过滤搜索 trustpilot.com 找不到 Roami 档案（返回的全是 roamic.com 与
无关品牌）。Roami 自家博客宣称 "4.9 Trustpilot"，但第三方评测引用的 "13k+ 条评价"
恰好等于 Roamic 的 13,683 条 —— 高度疑似两家被混为一谈。宁缺勿造，留空。
"""
import io
import sys

PATH = "data/providers.toml"

TP = {
    "roami":   None,
    "airalo":  "https://www.trustpilot.com/review/airalo.com",
    "holafly": "https://www.trustpilot.com/review/holafly.com",
    "saily":   "https://www.trustpilot.com/review/saily.com",
    "yesim":   "https://www.trustpilot.com/review/yesim.app",
    "ubigi":   "https://www.trustpilot.com/review/cellulardata.ubigi.com",
    "roamic":  "https://www.trustpilot.com/review/roamic.com",
    "alosim":  "https://www.trustpilot.com/review/alosim.com",
}

HEADER_OLD = (
    '# [brand.info] → 公司档案（HQ/法人/官网/双商店/客服/退款/目的地数），\n'
)
HEADER_NEW = (
    '# [brand.info] → 公司档案（HQ/法人/官网/双商店/客服/退款/目的地数/Trustpilot 档案），\n'
    '#   trustpilot：官方档案 URL 2026-10-04 逐个核实。**只存链接不存分数** —— 分数按\n'
    '#     Trustpilot 地区域名分片（Airalo 3.9/4.0/4.1 三个值），抓取被反爬墙拦截无法\n'
    '#     给出可核实单值；品牌页改为「给档案链接 + 教读者怎么读」。roami 无档案，留空。\n'
)


def main() -> int:
    with io.open(PATH, "r", encoding="utf-8", newline="") as f:
        text = f.read()

    if "trustpilot = " in text:
        print("ABORT: providers.toml 已含 trustpilot 字段，补丁可能已执行过")
        return 1

    lines = text.split("\n")
    out = []
    cur = None          # 当前所在 section 名，如 "airalo.info"
    inserted = set()

    for ln in lines:
        if ln.startswith("["):
            cur = ln.strip().strip("[]")
        # 在 <brand>.info 的 website = 行之后插入 trustpilot
        if cur and cur.endswith(".info") and ln.startswith("website = "):
            brand = cur[: -len(".info")]
            if brand in TP and brand not in inserted:
                out.append(ln)
                url = TP[brand]
                if url:
                    out.append('trustpilot = "%s"' % url)
                else:
                    out.append(
                        '# trustpilot：无 —— 域名过滤搜索 trustpilot.com 无 Roami 档案；'
                        "自家博客宣称的 4.9 分无档案支撑，不采信"
                    )
                inserted.add(brand)
                cur = None
                continue
        out.append(ln)

    text = "\n".join(out)

    # 头部注释
    if HEADER_OLD not in text:
        print("ABORT: 未找到头部 [brand.info] 说明行")
        return 1
    text = text.replace(HEADER_OLD, HEADER_NEW, 1)

    missing = set(TP) - inserted
    if missing:
        print("ABORT: 以下品牌未插入:", sorted(missing))
        return 1

    with io.open(PATH, "w", encoding="utf-8", newline="") as f:
        f.write(text)

    print("OK: 8 个 info 块处理完成")
    for k in ("airalo", "holafly", "saily", "yesim", "ubigi", "roamic", "alosim"):
        print("  %-8s -> %s" % (k, TP[k]))
    print("  %-8s -> (空：无档案)" % "roami")
    return 0


if __name__ == "__main__":
    sys.exit(main())
