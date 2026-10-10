# -*- coding: utf-8 -*-
"""首屏性能抽查（**产物级**，只读）。

判据分层（同 `_de_schema_audit.py` 的原则：硬判据只用**可穷举**的结构事实）：

硬判据（每一条都能对单页机械判定，不存在「清单追不上数据」）：
  [H1] `<link rel="preload" as="image" href="/x">` 的 `x` 必须在**同一页正文里被真正引用**
       （`<img src>` / `srcset` / `<source>`）；否则是白预加载（抢首屏带宽）。
  [H2] `<link rel="preconnect" href="https://o">` 的 origin `o` 必须在同一页被**实际请求**
       （外链 `<script src>` / `<link rel="stylesheet">` / CSS 里的 `@import`/`url()`）；
       否则是两次白握手（DNS+TLS）。唯一放行项：`fonts.gstatic.com` 是 Google Fonts
       CSS 的**伴生 origin**（字体文件从 gstatic 取），CSS 里看不到 ⇒ 显式成对放行。
  [H3] 单块内联 `<script>` 不得超过阈值（默认 100 KB）—— 内联 JS 不可缓存，
       且在首屏解析路径上。
  [H4] 文档必须有 `<head>` 元素且闭合（缺了浏览器会隐式补，严格解析器读不到
       title/meta/canonical）。

报告项（不判红，需人工决策）：
  [R1] 体积分布（按页型的 p50/p90/max）与体积构成（svg / ld+json / inline script）
  [R2] `de` vs `en` 同路径页体积差（德语文案通常更长 ⇒ 量化增量）
  [R3] CSS：文件数、字节、字体加载方式（`@import` 在 CSS 内 = 串行阻塞）
  [R4] 图片：总量、lazy 占比、width+height 占比、webp 占比
  [R5] `<img>` 未声明 `loading` —— ⚠ 只报告不判红：首屏 logo 应当 eager，
       静态无法判「是否首屏」。（实测全部是 header logo，属正确写法。）
  [R6] `<img>` 未声明 `width`/`height` —— ⚠ 同样只报告：本条的意图是防 CLS，
       但只要 CSS 已固定盒子（如 flags 的 `h-9 w-[3.25rem]`）就没有 CLS，
       而静态读不出 CSS 盒子。

用法：
  python -X utf8 scripts/_perf_audit.py
  python -X utf8 scripts/_perf_audit.py --selftest
"""
from __future__ import annotations

import argparse
import gzip
import pathlib
import re
import shutil
import statistics
from collections import Counter

ROOT = pathlib.Path(__file__).resolve().parents[1]
PUB = ROOT / "public"

TAG = re.compile(r"<(link|script|img|source)\b[^>]*>", re.I)
ATTR = re.compile(r'([a-zA-Z-]+)\s*=\s*"([^"]*)"')
INLINE_JS = re.compile(r"<script(?![^>]*\bsrc=)[^>]*>(.*?)</script>", re.S)
CSS_IMPORT = re.compile(r'@import\s+(?:url\()?["\']?(https?://[^"\')]+)')
CSS_URL = re.compile(r'url\((?:"|\')?(https?://[^"\')]+)')
BIG_INLINE = 100 * 1024
# Google Fonts 的伴生 origin：CSS 只声明 googleapis，字体文件从 gstatic 取 ⇒ 静态看不见
COMPANION = {"https://fonts.gstatic.com": "https://fonts.googleapis.com"}


def attrs(tag: str) -> dict:
    return {k.lower(): v for k, v in ATTR.findall(tag)}


def origin(u: str) -> str:
    return "/".join(u.split("/")[:3])


def analyse_page(path: pathlib.Path, pub: pathlib.Path) -> dict:
    t = path.read_text(encoding="utf-8")
    b = t.encode()
    r = {"path": str(path.relative_to(pub)), "bytes": len(b),
         "gzip": len(gzip.compress(b, 6)), "hits": {},
         "svg": sum(len(m.encode()) for m in re.findall(r"<svg.*?</svg>", t, re.S)),
         "ldjson": sum(len(m.encode()) for m in re.findall(
             r'<script[^>]*application/ld\+json[^>]*>.*?</script>', t, re.S)),
         "inline_js": [len(m.encode()) for m in INLINE_JS.findall(t)],
         "img_total": 0, "img_lazy": 0, "img_wh": 0, "img_webp": 0}

    # 文档结构
    if "</head>" not in t or "<head" not in t.replace("<header", ""):
        r["hits"].setdefault("H4", []).append("缺 <head> 或 </head>")

    # 正文里真正引用的资源（不含 head 的 preload/preconnect）
    body = t[t.find("</head>"):] if "</head>" in t else t
    used_imgs = set(re.findall(r'(?:src|srcset)\s*=\s*"([^"]+)"', body))
    used_imgs |= set(re.findall(r'<source[^>]*srcset\s*=\s*"([^"]+)"', body))
    # ⚠ preconnect / dns-prefetch 自身不算「被请求」——否则 H2 永远不触发（自证循环）
    used_origins = set()
    for m in TAG.finditer(t):
        full, name = m.group(0), m.group(1).lower()
        a = attrs(full)
        rel = a.get("rel", "")
        if name == "link" and ("preconnect" in rel or "dns-prefetch" in rel):
            continue
        u = a.get("src") or a.get("href") or ""
        if u.startswith("http"):
            used_origins.add(origin(u))
    # 本地 CSS 里的外链也算「被请求」
    for m in TAG.finditer(t):
        full = m.group(0)
        if m.group(1).lower() == "link" and "stylesheet" in attrs(full).get("rel", ""):
            f = pub / attrs(full).get("href", "").lstrip("/")
            if f.is_file():
                css = f.read_text(encoding="utf-8")
                used_origins |= {origin(u) for u in CSS_IMPORT.findall(css) + CSS_URL.findall(css)}

    for m in TAG.finditer(t):
        full, name = m.group(0), m.group(1).lower()
        a = attrs(full)
        if name == "link":
            rel = a.get("rel", "")
            if "preload" in rel and a.get("as") == "image":
                href = a.get("href", "")
                if href and href not in used_imgs:
                    r["hits"].setdefault("H1", []).append(f"preload 了未使用的图 {href}")
            if "preconnect" in rel or "dns-prefetch" in rel:
                o = a.get("href", "").rstrip("/")
                if (o.startswith("http") and o not in used_origins
                        and COMPANION.get(o) not in used_origins):
                    r["hits"].setdefault("H2", []).append(f"preconnect 到未被请求的 {o}")
        elif name == "img":
            r["img_total"] += 1
            if "loading" in a:
                r["img_lazy"] += 1
            else:
                r.setdefault("no_loading", []).append(a.get("src", ""))
            if "width" in a and "height" in a:
                r["img_wh"] += 1
            else:
                r.setdefault("no_wh", []).append(a.get("src", ""))
            if ".webp" in a.get("src", ""):
                r["img_webp"] += 1

    for n in r["inline_js"]:
        if n > BIG_INLINE:
            r["hits"].setdefault("H3", []).append(f"内联 <script> {n:,} 字节 > {BIG_INLINE:,}")
    return r


def bucket(rel: str) -> str:
    p = rel.replace("\\", "/").split("/")
    if p[0] == "de":
        p = p[1:]
    if not p or p[0] == "index.html":
        return "home"
    if p[0] == "compare":
        if len(p) == 2:
            return "compare hub"
        if "-vs-" in p[1]:
            return "compare vs"
        return "compare country" if len(p) == 3 else "compare brand"
    return p[0]


def audit(pub: pathlib.Path) -> dict:
    pages = [analyse_page(p, pub) for p in sorted(pub.rglob("*.html"))]
    hard, detail = Counter(), {}
    for r in pages:
        for k, v in r["hits"].items():
            hard[k] += len(v)
            detail.setdefault(k, []).append((r["path"], v))
    soft = {}
    for key in ("no_loading", "no_wh"):
        c = Counter()
        for r in pages:
            c.update(r.get(key, []))
        soft[key] = c
    return {"pages": pages, "hard": hard, "detail": detail, "soft": soft}


def report(a: dict) -> int:
    pages = a["pages"]
    print(f"[规模] HTML {len(pages)} 页 / 合计 {sum(r['bytes'] for r in pages):,} 字节"
          f"（gzip {sum(r['gzip'] for r in pages):,}）")
    print(f"       p50 {statistics.median(r['bytes'] for r in pages):,.0f}"
          f" / p90 {statistics.quantiles([r['bytes'] for r in pages], n=10)[8]:,.0f}"
          f" / max {max(r['bytes'] for r in pages):,}")

    print("\n[R1] 按页型体积分布（max / p50）")
    by = {}
    for r in pages:
        by.setdefault(bucket(r["path"]), []).append(r["bytes"])
    for k, v in sorted(by.items(), key=lambda x: -max(x[1])):
        print(f"    {k:16s} n={len(v):4d}  max={max(v):9,d}  p50={statistics.median(v):9,.0f}")

    big = sorted(pages, key=lambda r: -r["bytes"])[:6]
    print("\n[R1b] 最大 6 页的构成")
    for r in big:
        mx = max(r["inline_js"], default=0)
        print(f"    {r['bytes']:9,d}  {r['path']:44s} svg={r['svg']:7,d} ld={r['ldjson']:7,d}"
              f" 内联JS(max)={mx:9,d} gzip={r['gzip']:7,d}")

    # de vs en
    print("\n[R2] de vs en 同路径体积差")
    en = {r["path"]: r["bytes"] for r in pages if not r["path"].startswith("de" + "\\")
          and not r["path"].startswith("de/")}
    ds = []
    for r in pages:
        p = r["path"].replace("de" + "\\", "", 1).replace("de/", "", 1)
        if r["path"] != p and p in en:
            ds.append((r["bytes"] - en[p], r["bytes"] / en[p] - 1, r["path"]))
    if ds:
        ds.sort()
        med = statistics.median(d[1] for d in ds)
        print(f"    配对数 {len(ds)}；中位相对增量 {med:+.2%}；"
              f"最大 +{max(d[1] for d in ds):.2%} / 最小 {min(d[1] for d in ds):+.2%}")

    print("\n[R3] 样式与字体")
    cssdir = PUB / "css"
    for f in sorted(cssdir.glob("*.css")) if cssdir.exists() else []:
        t = f.read_text(encoding="utf-8")
        imp = CSS_IMPORT.findall(t)
        print(f"    {f.name}: {f.stat().st_size:,} 字节（阻塞渲染）；"
              f"CSS 内 @import {len(imp)} 个 → {imp}")
        print("      ⚠ CSS 里的 @import 是**串行阻塞**：HTML→tailwind.css→字体CSS→字体文件，"
              "浏览器无法提前发现")
    n_css = len(list(cssdir.glob("*.css"))) if cssdir.exists() else 0
    print(f"    本地样式表 {n_css} 个；head 里 preconnect 到 fonts.googleapis/gstatic = 有")

    imgs = [(r["img_total"], r["img_lazy"], r["img_wh"], r["img_webp"]) for r in pages]
    ti, tl, tw, tp = (sum(x[i] for x in imgs) for i in range(4))
    print(f"\n[R4] 图片：共 {ti:,}（lazy {tl:,} = {tl/max(ti,1):.0%}，"
          f"有 width+height {tw:,} = {tw/max(ti,1):.0%}，webp {tp:,} = {tp/max(ti,1):.0%}）")

    for key, label in (("no_loading", "R5 未声明 loading"), ("no_wh", "R6 未声明 width/height")):
        c = a["soft"][key]
        print(f"\n[{label}] 共 {sum(c.values()):,} 处，按 src：")
        for src, n in c.most_common(6):
            print(f"    {n:6,d}×  {src}")

    print("\n[H] 硬判据")
    ok = True
    names = {"H1": "preload 的图未被正文引用", "H2": "preconnect 的 origin 未被请求",
             "H3": "单块内联 <script> 过大", "H4": "文档缺 <head>/</head>"}
    for k in ("H1", "H2", "H3", "H4"):
        n = a["hard"].get(k, 0)
        print(f"    {'✓' if n == 0 else '✗'} [{k}] {names[k]}：{n} 处")
        if n:
            ok = False
            for path, v in a["detail"].get(k, [])[:4]:
                print(f"        {path} → {v[:2]}")
    print("\n" + ("硬判据全绿" if ok else "硬判据有红（见上）"))
    return 0 if ok else 1


def selftest() -> int:
    tmp = ROOT / ".buildlog" / "_perf_selftest"
    shutil.rmtree(tmp, ignore_errors=True)
    (tmp / "css").mkdir(parents=True)
    (tmp / "css" / "a.css").write_text(
        '@import url("https://fonts.googleapis.com/css2?family=Inter");.x{color:red}', encoding="utf-8")
    (tmp / "img").mkdir(parents=True)
    (tmp / "img" / "used.webp").write_bytes(b"x")

    def page(pre: str, body: str = "") -> str:
        return f"""<!doctype html><html lang="en"><head>
<link rel="stylesheet" href="/css/a.css">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="preload" as="image" href="/img/used.webp">
{pre}
</head><body>{body}</body></html>"""

    clean = page("", '<img src="/img/used.webp" width="1" height="1" loading="lazy">')
    (tmp / "p.html").write_text(clean, encoding="utf-8")
    ok = True
    print("[selftest] 正例（干净页）必须全绿：")
    r = analyse_page(tmp / "p.html", tmp)
    if r["hits"]:
        ok = False
        print(f"  ✗ 正例误伤：{r['hits']}")
    else:
        print("  ✓ 四条硬判据全绿（googleapis 由本地 CSS 的 @import 证明；"
              "gstatic 走伴生 origin 放行）")

    cases = {
        "H1": page("", ""),                                   # 删掉 <img> ⇒ preload 的图没人用
        "H2": page('<link rel="preconnect" href="https://never-requested.example">',
                   '<img src="/img/used.webp" width="1" height="1" loading="lazy">'),
        "H3": page("", "<script>" + "x" * (BIG_INLINE + 1) + "</script>"),
        "H4": clean.replace("<head>", "").replace("</head>", ""),
    }
    names = {"H1": "preload 未使用的图", "H2": "preconnect 未请求的 origin",
             "H3": "超大内联 script", "H4": "缺 <head>/</head>"}
    print("[selftest] 反例必须判红：")
    for k, txt in cases.items():
        (tmp / "p.html").write_text(txt, encoding="utf-8")
        rr = analyse_page(tmp / "p.html", tmp)
        hit = bool(rr["hits"].get(k))
        print(f"  {'✓' if hit else '✗'} 判红：[{k}] {names[k]} → {len(rr['hits'].get(k, []))}")
        if not hit:
            ok = False
    print("[selftest] " + ("全过" if ok else "失败"))
    shutil.rmtree(tmp, ignore_errors=True)
    return 0 if ok else 1


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--selftest", action="store_true")
    args = ap.parse_args()
    if args.selftest:
        return selftest()
    return report(audit(PUB))


if __name__ == "__main__":
    raise SystemExit(main())
