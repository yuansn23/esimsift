#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""hreflang 守卫（2026-10-08 加）—— 读 public/ 产物，独立于 hugo。

为什么需要它：`layouts/partials/head.html` 原来只守了 hreflang 的**目标侧**
（不指向 noindex 页），没守**来源侧**。后果是德语站 54 个 noindex 页
（内容未翻译、正文为空）在向外发 `hreflang="en-us" -> 英文 URL`：
Google 不处理 noindex 页上的 hreflang，而且英文侧因为译文 noindex 而不回指
（`{{ range .Translations }}{{ if not .Params.noindex }}`）→ 形成单向标注，
GSC 报 "No return tags" 并整体忽略这组标注。

四条判据（全部读产物，不看源码）：
  A. 页面自身 noindex → **一条 hreflang 都不许有**；
  B. 每个 hreflang 的 href 必须能解析到 public/ 下真实存在的产物；
  C. 互惠性：P 指向 U，则 U 必须回指 P（否则整组被忽略）；
  D. 指向的目标不得是 noindex（指向 noindex 页 = 无效标注）。

用法：
  python -X utf8 scripts/check_hreflang.py            # 检查 public/
  python -X utf8 scripts/check_hreflang.py --selftest # 注入反例，证明它会红
"""
import io
import os
import re
import sys
import pathlib

ROOT = pathlib.Path(__file__).resolve().parent.parent
PUBLIC = ROOT / "public"

ALT = re.compile(r'<link\s+rel="alternate"\s+hreflang="([^"]+)"\s+href="([^"]+)"')
NOINDEX = re.compile(r'<meta\s+name="robots"\s+content="[^"]*\bnoindex\b')


def read_base():
    try:
        t = io.open(ROOT / "hugo.toml", encoding="utf-8").read()
    except OSError:
        return "https://www.esimsift.com/"
    m = re.search(r'^\s*baseURL\s*=\s*"([^"]+)"', t, re.M)
    return m.group(1) if m else "https://www.esimsift.com/"


def url_to_rel(url, base):
    """把站内绝对 URL 映射成 public/ 下的相对路径；站外返回 None。"""
    if not url.startswith(base):
        return None
    rest = url[len(base):]
    rest = rest.split("#")[0].split("?")[0]
    if rest == "" or rest.endswith("/"):
        rest += "index.html"
    return rest


def url_to_rel_of(rel, base):
    """public/ 下的相对路径 -> 该页自己的绝对 URL（index.html 折成目录形式）。"""
    if rel.endswith("/index.html"):
        return base + rel[: -len("index.html")]
    if rel == "index.html":
        return base
    return base + rel


def analyse(pages, base, exists=None):
    """pages: {rel_path: html}。exists: 可选的「产物是否真实存在」回调（自测用）。
    返回错误串列表。纯函数 —— 自测直接喂构造样本。"""
    errs = []
    tags = {}
    noindex = {}
    for rel, html in pages.items():
        noindex[rel] = bool(NOINDEX.search(html))
        tags[rel] = ALT.findall(html)

    def present(rel):
        if exists is not None:
            return exists(rel)
        return (PUBLIC / rel).is_file()

    for rel, lst in sorted(tags.items()):
        if not lst:
            continue
        if noindex[rel]:
            errs.append(f"{rel}: A 页面自身 noindex 却发了 {len(lst)} 条 hreflang "
                        f"（Google 不处理，且会造成单向标注）")
            continue
        for _, href in lst:
            tgt = url_to_rel(href, base)
            if tgt is None:
                continue  # 站外，不判
            if not present(tgt):
                errs.append(f"{rel}: B hreflang 指向的产物不存在 -> {href}")
                continue
            if tgt == rel:
                continue
            if tgt not in tags:
                errs.append(f"{rel}: B hreflang 指向的页面没被扫到 -> {href}")
                continue
            if noindex[tgt]:
                errs.append(f"{rel}: D hreflang 指向 noindex 页 -> {href}")
            back = url_to_rel_of(rel, base)
            if back not in {h for _, h in tags[tgt]}:
                errs.append(f"{rel}: C 单向标注 —— {tgt} 没有回指 {back}")
    return errs


def main():
    if "--selftest" in sys.argv[1:]:
        return selftest()

    if not PUBLIC.is_dir():
        print("ERROR public/ not found - run `hugo` first")
        return 1

    base = read_base()
    pages = {}
    for f in sorted(PUBLIC.rglob("*.html")):
        rel = f.relative_to(PUBLIC).as_posix()
        try:
            pages[rel] = f.read_text(encoding="utf-8", errors="replace")
        except OSError:
            continue

    errs = analyse(pages, base)
    total = sum(len(v) for v in (ALT.findall(h) for h in pages.values()))
    paired = sum(1 for h in pages.values() if ALT.search(h))

    if errs:
        print(f"ERROR hreflang guard: {len(errs)} problem(s)")
        for e in errs[:40]:
            print(f"  {e}")
        if len(errs) > 40:
            print(f"  ... and {len(errs) - 40} more")
        return 1

    print(f"OK: {len(pages)} pages scanned, {total} hreflang tag(s) on {paired} page(s) "
          f"- no tag on noindex/404, all targets exist, all groups reciprocal")
    return 0


BASE_FIX = "https://example.test/"


def _doc(alts, noindex=False):
    robots = '<meta name="robots" content="noindex, follow">' if noindex else ""
    tags = "".join(f'<link rel="alternate" hreflang="{l}" href="{u}">' for l, u in alts)
    return f"<html><head>{robots}{tags}</head><body>x</body></html>"


def selftest():
    """每条判据都要有一个「应该红」的反例 —— 一个 bad=0 的守卫只有在
    证明过它会报错之后才有意义。"""
    E = "https://example.test/"
    cases = []

    # 1 干净的互惠对
    pages = {
        "index.html": _doc([("en", E), ("de", E + "de/")]),
        "de/index.html": _doc([("de", E + "de/"), ("en", E)]),
    }
    cases.append(("干净互惠对", pages, 0, ""))

    # 2 A：noindex 页发 hreflang（只留自指，隔离出判据 A）
    pages = {"de/x/index.html": _doc([("de", E + "de/x/")], noindex=True)}
    cases.append(("A noindex 页发标注", pages, 1, "A 页面自身 noindex"))

    # 3 B：指向不存在的产物
    pages = {"index.html": _doc([("en", E), ("de", E + "de/")])}
    cases.append(("B 目标不存在", pages, 1, "B hreflang 指向的产物不存在"))

    # 4 C：单向标注（de 指向 en/，en 只自指、不回指 de）
    pages = {
        "index.html": _doc([("en", E)]),
        "de/index.html": _doc([("de", E + "de/"), ("en", E)]),
    }
    cases.append(("C 单向标注", pages, 1, "C 单向标注"))

    # 5 D：指向 noindex 目标。目标既然 noindex，就不可能同时也是一条合法回指
    #   （发标签 → 判据 A 红；不发 → 判据 C 红），所以这里必然是 2 处。
    pages = {
        "index.html": _doc([("en", E), ("de", E + "de/")]),
        "de/index.html": _doc([], noindex=True),
    }
    cases.append(("D 目标 noindex", pages, 2, "D hreflang 指向 noindex 页"))

    # 6 站外 href 不判（不应误报）
    pages = {"a/index.html": _doc([("en", "https://other.test/a/")])}
    cases.append(("站外 href 不误报", pages, 0, ""))

    # 7 404 页：head.html 用 `ne .Kind "404"` 保证不发；这里证明它若发了就抓得住
    pages = {"404.html": _doc([("en", E + "404.html"), ("de", E + "de/404.html")])}
    cases.append(("404 指向的译文本不存在", pages, 1, "B hreflang 指向的产物不存在"))

    failed = 0
    for name, pages, want, needle in cases:
        got = analyse(pages, E, exists=(lambda rel: rel in pages))
        ok = len(got) == want and (want == 0 or any(needle in g for g in got) or needle == "")
        failed += 0 if ok else 1
        print(f"  {'OK  ' if ok else 'MISS'} {name:24s} 期望 {want} 处（{needle or '任意'}）实际 {len(got)} 处")
        if not ok:
            for g in got:
                print(f"        ... {g}")
    print(f"\n自测{'通过' if not failed else f'失败 {failed} 项'}")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
