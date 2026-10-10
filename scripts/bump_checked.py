#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""bump_checked.py —— 更新 data/plans/<brand>.toml 里每个国家的 `checked`（价格核对日）。

为什么需要这个脚本
    站内所有「最后更新」日期只有一个来源：data/plans/<brand>.toml 里每个国家块的
    `checked` 字段。它同时喂给三个机器可读的面：
        · 页面可见文案   「Prices checked <checked>」/「Last updated <checked>」
        · JSON-LD        dateModified = <checked>
        · sitemap        <lastmod> = <checked>
    所以数据一更新，必须**把 checked 一起前移**，否则页面会继续宣称旧日期；
    反过来，不更新数据却改 checked 就是对读者和 Google 撒谎。

用法
    # 看当前各品牌的数据日期
    python scripts/bump_checked.py --show

    # 今天核对了 alosim 的全部 50 个市场
    python scripts/bump_checked.py --brand alosim

    # 只核对了 alosim 的美国和波兰
    python scripts/bump_checked.py --brand alosim --countries US,PL

    # 指定日期 / 预演
    python scripts/bump_checked.py --brand alosim --date 2026-10-04 --dry-run

退出码：0 正常；1 参数或数据错误。
"""
from __future__ import annotations

import argparse
import datetime
import io
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
PLANS_DIR = ROOT / "data" / "plans"

# 国家块头：文件里形如 `[AR]`（顶层、两字母 ISO）。`[[AR.plans]]` 不会被匹配。
RE_ISO_HEADER = re.compile(r"^\[([A-Z]{2})\]\s*$")

# providers.toml 的品牌表头：`[jetpac]` 与带点的子表 `[jetpac.info]` / `[jetpac.policy]`
# 都算**同一个品牌**的段头。
#
# ★ 为什么必须认带点的子表（2026-10-09 第六十三轮，实测事故）：
#   全站 10 家的 `[<brand>.policy]` 表**全部堆在文件末尾**，排在最后一个顶层段
#   `[jetpac]` 之后。旧定义（`^\[(\w+)\]$`，只认不带点的表头）于是把这 10 张
#   子表**全部算进 jetpac 的段范围** —— 实测：给 `[holafly.policy]` 加一行
#   `fup_kind = "none"`，翻的是 **jetpac** 的档案核对日（10-07 → 10-09，一句
#   不实陈述）；而 holafly 自己的政策表挨不到 `[holafly]` 的段，改它**不翻**
#   holafly 的日期。一句话：段的边界必须按**品牌**切，不能按「行物理上排在哪」切。
RE_PROV_HEADER = re.compile(r"^\[([a-z0-9_]+)(?:\.[a-z0-9_]+)?\]\s*$")
RE_CHECKED = re.compile(r"^(\s*)checked\s*=\s*\"([^\"]*)\"(.*)$")
RE_DATE = re.compile(r"^\d{4}-\d{2}-\d{2}$")


def plan_files(brand: str | None) -> list[pathlib.Path]:
    if brand:
        p = PLANS_DIR / f"{brand}.toml"
        if not p.exists():
            avail = ", ".join(sorted(x.stem for x in PLANS_DIR.glob("*.toml")))
            sys.exit(f"错误：找不到 {p}\n可用品牌：{avail}")
        return [p]
    return sorted(PLANS_DIR.glob("*.toml"))


class Block:
    """一份数据里的一个「段」—— plans 的 `[ISO]` 块、providers.toml 的 `[key]` 段。

    stamp_checked.py 靠它做「内容指纹 → 日期」的映射，所以段的边界与
    「哪个字段是日期」必须只有一份定义，就在本文件里。
    """

    __slots__ = ("key", "start", "end", "date_idx", "date", "ranges")

    def __init__(self, key: str, start: int, end: int,
                 date_idx: int = -1, date: str = "", ranges=None):
        self.key = key
        self.start = start        # 段头行下标（含）
        self.end = end            # 段尾行下标（不含）
        self.date_idx = date_idx  # 日期字段所在行；同段出现多个时**只认第一个**
        self.date = date
        # 段体可以**不连续**：providers.toml 的 `[x]` / `[x.info]` / `[x.policy]`
        # 三张表允许隔着别的品牌。None = 「就是 [start, end) 这一整段」。
        # 只有 parse_prov_blocks 会给出多区间；parse_blocks 一律 None。
        self.ranges = ranges


def read_lines(path: pathlib.Path) -> list[str]:
    """按 LF 切行、其余字节原样保留（写回 `"\\n".join(lines)` 即复原）。"""
    with io.open(path, "r", encoding="utf-8", newline="") as f:
        return f.read().split("\n")


def parse_blocks(lines: list[str], header_re, date_re, val_group: int) -> list[Block]:
    """按 header_re 切段，段内用 date_re 抓日期字段（值取 val_group）。"""
    out: list[Block] = []
    cur: Block | None = None
    for i, s in enumerate(lines):
        m = header_re.match(s)
        if m:
            if cur is not None:
                cur.end = i
                out.append(cur)
            cur = Block(m.group(1), i, len(lines))
            continue
        if cur is not None and cur.date_idx < 0:
            m2 = date_re.match(s)
            if m2:
                cur.date_idx = i
                cur.date = m2.group(val_group)
    if cur is not None:
        cur.end = len(lines)
        out.append(cur)
    return out


def parse_prov_blocks(lines: list[str], date_re, val_group: int) -> list[Block]:
    """按**品牌**切 providers.toml：`[x]` / `[x.info]` / `[x.policy]` 归为同一段，
    不论它们在文件里隔着多远。返回顺序 = 品牌首次出现的顺序。

    与 parse_blocks 的区别：parse_blocks 只按行位置切，段体必然连续 —— 对
    `data/plans/*.toml`（每个 `[ISO]` 紧跟自己的 `[[ISO.plans]]`）是对的；对
    providers.toml 末尾那一堆 `[<brand>.policy]` 就是错的（见 RE_PROV_HEADER）。
    """
    order: list[str] = []
    spans: dict[str, list[list[int]]] = {}
    # ① 先按**所有**表头把文件切满：每张表占据「本表头 → 下一个表头（任意品牌）」。
    #    只把相邻表头并成一段是错的 —— 那样 `[roami]` 的区间只剩它自己那一行，
    #    中间几十行字段落在任何区间之外（实测：10 个品牌段体全空、指纹全相同）。
    hits: list[tuple[int, str]] = []
    for i, s in enumerate(lines):
        m = RE_PROV_HEADER.match(s)
        if m:
            hits.append((i, m.group(1)))
    # ② 再按品牌归组：`[x]` / `[x.info]` / `[x.policy]` 合成同一段的多区间。
    for n, (i, key) in enumerate(hits):
        end = hits[n + 1][0] if n + 1 < len(hits) else len(lines)
        if key not in spans:
            order.append(key)
            spans[key] = []
        sp = spans[key]
        if sp and sp[-1][1] == i:      # 与上一区间相接 → 并起来
            sp[-1][1] = end
        else:
            sp.append([i, end])
    out: list[Block] = []
    for key in order:
        sp = spans[key]
        b = Block(key, sp[0][0], sp[-1][1], ranges=[(lo, hi) for lo, hi in sp])
        for lo, hi in b.ranges:
            if b.date_idx >= 0:
                break
            for i in range(lo + 1, hi):
                m2 = date_re.match(lines[i])
                if m2:
                    b.date_idx = i
                    b.date = m2.group(val_group)
                    break
        out.append(b)
    return out


def scan(path: pathlib.Path) -> dict[str, str]:
    """返回 {ISO: checked}，按文件出现顺序。"""
    return {b.key: b.date
            for b in parse_blocks(read_lines(path), RE_ISO_HEADER, RE_CHECKED, 2)
            if b.date}


def apply(path: pathlib.Path, targets: set[str] | None, newdate: str, dry: bool):
    """就地改写 checked 行。targets=None 表示该文件所有国家。
    返回 [(ISO, 旧值, 新值)]。**保持文件原有行尾**（CRLF 文件改完还是 CRLF），
    其它字节不动。

    为什么强调行尾：`data/plans/*.toml` 全部是 CRLF，而 providers.toml 是 LF。
    这里若把替换行写成不带 `\\r` 的 LF，CRLF 文件里就会混进 49 行 LF ——
    TOML 仍然合法（`\\r\\n` 与 `\\n` 都行），但文件从此「行尾混杂」，
    以后任何用**文本模式默认换行**回写它的脚本都会把 `\\r\\n` 变成 `\\r\\r\\n`，
    而注释行里的孤立 `\\r` 是**非法 TOML 字符** → hugo 直接
    `failed to load data ... invalid character in comment` 整站构建失败。
    （2026-10-07 接 Jetpac 时实测踩到，jetpac.toml 有 49 行 LF。）
    """
    with io.open(path, "r", encoding="utf-8", newline="") as f:
        text = f.read()
    lines = text.split("\n")
    cur = None
    changed: list[tuple[str, str, str]] = []
    for i, raw in enumerate(lines):
        s = raw.rstrip("\r")
        m = RE_ISO_HEADER.match(s)
        if m:
            cur = m.group(1)
            continue
        m = RE_CHECKED.match(s)
        if m and cur and (targets is None or cur in targets):
            old = m.group(2)
            if old != newdate:
                eol = "\r" if raw.endswith("\r") else ""   # ★ 还原原行尾
                lines[i] = f'{m.group(1)}checked = "{newdate}"{m.group(3)}{eol}'
                changed.append((cur, old, newdate))
    if changed and not dry:
        with io.open(path, "w", encoding="utf-8", newline="") as f:
            f.write("\n".join(lines))
    return changed


def cmd_show() -> int:
    print(f"{'品牌':<10} {'国家数':>5}  {'最早':<12} {'最新':<12}")
    print("-" * 46)
    grand = set()
    for p in plan_files(None):
        d = scan(p)
        if not d:
            print(f"{p.stem:<10} {0:>5}  (无 checked)")
            continue
        vals = sorted(d.values())
        grand.update(vals)
        print(f"{p.stem:<10} {len(d):>5}  {vals[0]:<12} {vals[-1]:<12}")
    print("-" * 46)
    if len(grand) == 1:
        print(f"全站数据日期一致：{grand.pop()}")
    else:
        print(f"★ 全站存在多个数据日期：{sorted(grand)}")
    return 0


def cmd_bump(args) -> int:
    newdate = args.date or datetime.date.today().isoformat()
    if not RE_DATE.match(newdate):
        sys.exit(f"错误：--date 需要 YYYY-MM-DD，收到 {newdate!r}")
    targets = None
    if args.countries:
        targets = {c.strip().upper() for c in args.countries.split(",") if c.strip()}
        if not targets:
            sys.exit("错误：--countries 解析为空")

    total = 0
    print(f"{'dry-run  ' if args.dry_run else ''}目标日期 {newdate}"
          f"{'  限国家 ' + ','.join(sorted(targets)) if targets else '  全部国家'}\n")
    for p in plan_files(args.brand):
        have = scan(p)
        missing = sorted(targets - set(have)) if targets else []
        if missing:
            sys.exit(f"错误：{p.name} 里没有这些国家块：{', '.join(missing)}")
        changed = apply(p, targets, newdate, args.dry_run)
        total += len(changed)
        if not changed:
            print(f"  {p.stem:<10} 已是 {newdate}，无需改动")
            continue
        print(f"  {p.stem:<10} {len(changed)} 个国家：{changed[0][1]} -> {newdate}"
              f"  ({', '.join(c for c, _, _ in changed[:6])}"
              f"{' …' if len(changed) > 6 else ''})")
    print(f"\n共 {total} 处{'（预演，未写入）' if args.dry_run else ' 已写入'}")
    if total and not args.dry_run:
        print("下一步：npm run build（重建后页面日期 / dateModified / sitemap lastmod 会一起前移）")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description="更新 data/plans/*.toml 的价格核对日 checked")
    ap.add_argument("--brand", help="品牌文件名（不含 .toml），如 alosim；不传则作用于全部品牌")
    ap.add_argument("--countries", help="逗号分隔的 ISO 码，如 US,PL；不传则该品牌全部国家")
    ap.add_argument("--date", help="核对日 YYYY-MM-DD，默认今天")
    ap.add_argument("--dry-run", action="store_true", help="只显示会改什么，不写文件")
    ap.add_argument("--show", action="store_true", help="只列出各品牌当前的数据日期")
    args = ap.parse_args()

    if args.show:
        return cmd_show()
    if not args.brand and args.countries:
        sys.exit("错误：--countries 必须与 --brand 一起使用（跨品牌批量改同一批国家风险过高）")
    return cmd_bump(args)


if __name__ == "__main__":
    raise SystemExit(main())
