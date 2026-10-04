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


def scan(path: pathlib.Path) -> dict[str, str]:
    """返回 {ISO: checked}，按文件出现顺序。"""
    out: dict[str, str] = {}
    with io.open(path, "r", encoding="utf-8", newline="") as f:
        cur = None
        for line in f:
            s = line.rstrip("\r\n")
            m = RE_ISO_HEADER.match(s)
            if m:
                cur = m.group(1)
                continue
            m = RE_CHECKED.match(s)
            if m and cur:
                out[cur] = m.group(2)
    return out


def apply(path: pathlib.Path, targets: set[str] | None, newdate: str, dry: bool):
    """就地改写 checked 行。targets=None 表示该文件所有国家。
    返回 [(ISO, 旧值, 新值)]。文件保持 LF，其它字节不动。"""
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
                lines[i] = f'{m.group(1)}checked = "{newdate}"{m.group(3)}'
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
