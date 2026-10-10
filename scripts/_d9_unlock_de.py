# -*- coding: utf-8 -*-
"""D9 —— 德语分层发布解禁：删掉 content/de/**/*.md 里的 noindex 与配套 TODO 注释。

背景（分层发布）：德语译文分批落地期间，除 /de/ 首页外全部标 `noindex, follow`，
避免半成品页被 Google 收录。译完（批 C/D/E 收口）后在这一轮统一解禁。

noindex 有两种形态（实测 643 页 = 79 + 564）：
  A. 成对（79 页，批 B/C/D/E 新建的正文页）：
       noindex: true
       # TODO(de)：分层发布 —— 全站德语译文解禁（D9 那一轮）时删掉上面这行。
     ⇒ 两行一起删。
  B. 单行（564 页，模板驱动页 —— 45 个 vs 页 + 499 个品牌子页 + 顶层静态页）：
       noindex: true
     ⇒ 只删这一行（这些页当初就没有 TODO 注释）。

⚠ 只删 noindex（+ 配套 TODO），不动 front matter 里任何其他行。
⚠ `sitemap-urls.html` 以 `.Params.noindex` 过滤 ⇒ 删净后 /de/sitemap.xml 自动补全，
   不需要另写 URL 清单（机制已用 `layouts/sitemap.xml` + `partials/sitemap-urls.html` 核实）。

用法：
  python -X utf8 scripts/_d9_unlock_de.py --dry
  python -X utf8 scripts/_d9_unlock_de.py
"""
from __future__ import annotations

import argparse
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
DE = ROOT / "content" / "de"

NOINDEX = "noindex: true"
TODO = "# TODO(de)：分层发布 —— 全站德语译文解禁（D9 那一轮）时删掉上面这行。"


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry", action="store_true")
    args = ap.parse_args()

    files = sorted(DE.rglob("*.md"))
    if not files:
        print("✗ 找不到 content/de/**/*.md")
        return 1

    touched: list[tuple[str, str]] = []
    problems: list[str] = []
    for f in files:
        raw = f.read_bytes()
        try:
            text = raw.decode("utf-8")
        except UnicodeDecodeError as e:
            problems.append(f"{f}: 不是 UTF-8（{e}）")
            continue
        n_no = text.count(NOINDEX)
        n_td = text.count(TODO)
        if n_no == 0 and n_td == 0:
            continue
        # ① 必须「一行 noindex」，且 TODO 至多一行
        if n_no != 1 or n_td > 1:
            problems.append(f"{f.relative_to(ROOT)}: noindex={n_no} todo={n_td}（期望 noindex=1、todo∈{{0,1}}）")
            continue
        rel = str(f.relative_to(ROOT))
        if n_td == 1:
            # A. 成对：TODO 必须紧跟在 noindex 的**下一行**
            pair = NOINDEX + "\n" + TODO + "\n"
            if pair not in text:
                problems.append(f"{rel}: noindex 与 TODO 不相邻")
                continue
            text = text.replace(pair, "", 1)
            touched.append((rel, "A 成对"))
        else:
            # B. 单行：noindex 必须自成一行
            line = NOINDEX + "\n"
            if line not in text:
                problems.append(f"{rel}: noindex 不是独立整行")
                continue
            text = text.replace(line, "", 1)
            touched.append((rel, "B 单行"))
        if NOINDEX in text or TODO in text:
            problems.append(f"{rel}: 删除后仍有残留")
            continue
        if not args.dry:
            out = text.encode("utf-8")
            # ② 换行守恒：德语 md 全为 LF
            if raw.count(b"\r\n") != out.count(b"\r\n"):
                problems.append(f"{rel}: 换行被改动")
                continue
            f.write_bytes(out)

    if problems:
        print("✗ 发现 %d 处异常，未写盘：" % len(problems))
        for p in problems[:20]:
            print("   ", p)
        return 1

    mode = "[dry] " if args.dry else "[written] "
    n_a = sum(1 for _, k in touched if k.startswith("A"))
    print(f"{mode}解禁 {len(touched)} 页（A 成对 {n_a} / B 单行 {len(touched) - n_a}）")

    if args.dry:
        return 0

    # 复核
    left_no = sum(1 for f in files if NOINDEX in f.read_text(encoding="utf-8"))
    left_td = sum(1 for f in files if TODO in f.read_text(encoding="utf-8"))
    crlf = sum(f.read_bytes().count(b"\r\n") for f in files)
    print(f"[verify] content/de/**/*.md 剩余 noindex = {left_no} · 剩余 TODO = {left_td} · CRLF = {crlf}")
    return 0 if (left_no == 0 and left_td == 0 and crlf == 0) else 1


if __name__ == "__main__":
    sys.exit(main())
