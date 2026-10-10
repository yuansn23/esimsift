# -*- coding: utf-8 -*-
"""德语页「站内链接语言泄漏」产物级审计（**只读**，不写任何产物）。

判据：
  [1] 语言泄漏（硬）—— 德语页里 `<a href>` 指向**站内**的链接，凡**不带 hreflang**
      属性者（带 hreflang 的是语言切换器，天然指向另一语言），必须落在
      `/de` 或 `/de/…`；指向 `/`、`/compare/…` 等英语路径即为泄漏。
  [2] 畸形 href（硬）—— href 字面量里出现**字面反斜杠**（`href=\\"/x/\\"` 这类三层转义
      残留）⇒ 浏览器把 `\\` 当路径一部分，链接**点不动**。
  [3] **非 HTML 德语产物**的语言泄漏（硬）—— `public/de/**` 里 `.txt` / `.json` / `.xml`
      （`llms.txt` / `catalog.json` / `index.xml` / `sitemap.xml`）里的自有域名 URL，
      同样必须带 `/de/`。⚠ 这是**红线 88**的教训：判据枚举了什么页型，就只保护那些页型
      —— 首版只扫 `*.html`，于是 `/de/llms.txt` 的 **68 处**英语根内链整片漏掉
      （同一份 `index.llms.txt` 模板里，`.Permalink` 生成的行是对的、`absURL` 生成的行是错的）。

⚠ 三条踩过的坑（每条都曾让判据失真）：
  1. **先挖掉 `<script>`/`<style>`**（红线 6）：`ld+json` 里的 `\\"` 是合法转义，不该判红。
     —— 首版没挖，把 96 处合法转义报成畸形。
  2. **href 必须全形态提取**（双引号 / 单引号 / 无引号）。只认双引号会把
     `href=\\"…\\"` 这种转义形态整片漏掉 —— 首版把 93 条泄漏低估成 11 条。
  3. **语言切换器必须豁免**：它是全站唯一**应当**指向另一语言的 `<a>`。
  4. **自有域名的绝对写法也要判**：面包屑「回首页」用 `.Site.Home.Permalink`
     （`https://www.esimsift.com/…` 而非相对路径），只认 `/…` 会把它当外链放过。

用法：
  python -X utf8 scripts/_de_link_leak_audit.py
  python -X utf8 scripts/_de_link_leak_audit.py --selftest
"""
from __future__ import annotations

import argparse
import pathlib
import re
import shutil

ROOT = pathlib.Path(__file__).resolve().parents[1]
PUB = ROOT / "public"
DE = PUB / "de"

SCR = re.compile(r"<script\b.*?</script\s*>", re.S | re.I)
STY = re.compile(r"<style\b.*?</style\s*>", re.S | re.I)
ANCHOR = re.compile(r"<a\b[^>]*>", re.I)
HREF = re.compile(r"""href\s*=\s*(?:"([^"]*)"|'([^']*)'|([^\s>]+))""", re.I)
HREFLANG = re.compile(r"\bhreflang\s*=", re.I)

# 外部 / 协议 / 纯锚点：不参与语言前缀判据
SKIP_PREFIX = ("mailto:", "tel:", "javascript:", "data:", "#")
# ⚠ 自有域名的**绝对**写法也必须纳入判据：面包屑「回首页」用的是
#   `{{ .Site.Home.Permalink }}`（绝对 URL），只认相对路径会把它当外链放过。
SELF_HOSTS = ("https://www.esimsift.com", "http://www.esimsift.com",
              "https://esimsift.com", "http://esimsift.com")


def strip_data_blocks(html: str) -> str:
    return STY.sub("", SCR.sub("", html))


def unescape_href(v: str) -> str:
    """剥掉模板/JSON 转义残留：`\\"`→`"`、`\\'`→`'`，再去掉两端引号与反斜杠。"""
    v = v.strip()
    v = v.replace('\\"', '"').replace("\\'", "'")
    v = v.strip()
    return v.strip('"').strip("'").strip("\\").strip()


def internal_path(v: str) -> str | None:
    """→ 站内路径（`/…`）；外链/非路径返回 None。"""
    if v.startswith("//"):
        return None                                  # 协议相对：外链
    if v.startswith("/"):
        return v
    for h in SELF_HOSTS:
        if v == h or v.startswith(h + "/"):
            return v[len(h):] or "/"
    return None


def scan_html(html: str) -> tuple[list[str], list[str]]:
    """→ (泄漏 href 列表, 畸形 href 列表)。"""
    body = strip_data_blocks(html)
    leaks, broken = [], []
    for tag in ANCHOR.findall(body):
        m = HREF.search(tag)
        if not m:
            continue
        raw = next(g for g in m.groups() if g is not None)
        if "\\" in raw:
            broken.append(raw.strip())
        v = unescape_href(raw)
        if not v or v.startswith(SKIP_PREFIX):
            continue
        if HREFLANG.search(tag):        # 语言切换器：豁免
            continue
        path = internal_path(v)
        if path is None:                # 外链 / 非路径
            continue
        if path == "/de" or path.startswith("/de/"):
            continue
        leaks.append(v)
    return leaks, broken


def analyse(de: pathlib.Path) -> dict:
    res = {"pages": 0, "leak": [], "broken": [], "nonhtml": []}
    for p in sorted(de.rglob("*.html")):
        res["pages"] += 1
        leaks, broken = scan_html(p.read_text(encoding="utf-8", errors="replace"))
        rel = str(p.relative_to(de))
        if leaks:
            res["leak"].append((rel, leaks))
        if broken:
            res["broken"].append((rel, broken))
    for p in sorted(de.rglob("*")):
        if not p.is_file() or p.suffix.lower() not in NONHTML_EXT:
            continue
        bad = scan_nonhtml(p.read_text(encoding="utf-8", errors="replace"))
        if bad:
            res["nonhtml"].append((str(p.relative_to(de)), bad))
    return res


def report(res: dict) -> int:
    n_leak = sum(len(v) for _r, v in res["leak"])
    n_broken = sum(len(v) for _r, v in res["broken"])
    n_nh = sum(len(v) for _r, v in res["nonhtml"])
    print(f"[规模] de 页 {res['pages']}")
    print(f"\n[1] ★ 语言泄漏（HTML，硬判据）：{n_leak} 处 / {len(res['leak'])} 页")
    for rel, v in res["leak"][:15]:
        print(f"    ✗ {rel}  ({len(v)} 处)")
        for h in sorted(set(v))[:4]:
            print(f"        {h}")
    print(f"\n[2] ★ 畸形 href（硬判据）：{n_broken} 处 / {len(res['broken'])} 页")
    for rel, v in res["broken"][:15]:
        print(f"    ✗ {rel}  ({len(v)} 处)  例：{sorted(set(v))[0]}")
    print(f"\n[3] ★ 非 HTML 产物语言泄漏（硬判据）：{n_nh} 处 / {len(res['nonhtml'])} 个文件")
    for rel, v in res["nonhtml"][:15]:
        print(f"    ✗ {rel}  ({len(v)} 处 / 去重 {len(set(v))} 种)")
        for h in sorted(set(v))[:4]:
            print(f"        {h}")
    ok = not (res["leak"] or res["broken"] or res["nonhtml"])
    print("\n[结论] " + ("全绿（HTML 0 泄漏 / 0 畸形；非 HTML 0 泄漏）" if ok else "存在缺陷"))
    return 0 if ok else 1


# ── selftest：合成页做正例 + 逐条反例 ──
CLEAN = """<!doctype html><html lang="de"><head>
<link rel="alternate" hreflang="en" href="https://www.esimsift.com/compare/">
<script type="application/ld+json">{"a":"href=\\"/en/escaped/\\"","b":"x \\u003c y"}</script>
</head><body>
<a href="/de/compare/" class="x">Länder</a>
<a href="/de/compare/argentina/">Argentinien</a>
<a href="https://mybestsim.com/x">extern</a>
<a href="#plans">Sprung</a>
<a href="/compare/" hreflang="en">English</a>
</body></html>"""


def scan_nonhtml(text: str, host: str = "https://www.esimsift.com") -> list[str]:
    """非 HTML 产物里的英语根内链。

    豁免：① 站点根（``""`` / ``/``，语言无关）；② **同一标签内**的 `hreflang` 值
    （语言切换，天然指向另一语言）。②用「往前 120 字符窗口里 `hreflang=` 与当前位置
    之间没有 `>`」判定「同标签」。
    """
    bad = []
    for m in re.finditer(re.escape(host) + r'[^\s"\'<>\)\]},]*', text):
        u = m.group(0).rstrip('.,);')
        i = m.start()
        pre = text[max(0, i - 120):i]
        k = pre.rfind("hreflang=")
        if k >= 0 and pre.rfind(">") < k:
            continue                        # 同标签内的 hreflang → 语言切换，豁免
        tail = u[len(host):]
        if tail in ("", "/") or tail == "/de" or tail.startswith("/de/"):
            continue
        bad.append(u)
    return bad


NONHTML_EXT = (".txt", ".json", ".xml")


def selftest() -> int:
    tmp = ROOT / ".buildlog" / "_de_link_leak_selftest"
    shutil.rmtree(tmp, ignore_errors=True)
    (tmp / "de").mkdir(parents=True)
    f = tmp / "de" / "index.html"
    f.write_text(CLEAN, encoding="utf-8")
    # 非 HTML 正例（[3]）：站点根 + 同标签 hreflang 交替链接都必须豁免
    NHC = {
        "llms.txt": "# eSIM Sift\n"
                    "- [Vergleich](https://www.esimsift.com/de/compare/): alles\n"
                    "- [Tarifdatenbank](https://www.esimsift.com/de/catalog.json): JSON\n"
                    "- [Startseite](https://www.esimsift.com/): Start\n",
        "catalog.json": '{"site":"esimsift","url":"https://www.esimsift.com/",'
                        '"countries":[{"url":"https://www.esimsift.com/de/compare/france/"}]}',
        "sitemap.xml": '<?xml version="1.0"?>\n<urlset>'
                       '<url><loc>https://www.esimsift.com/de/compare/</loc>'
                       '<xhtml:link rel="alternate" hreflang="en" href="https://www.esimsift.com/compare/"/>'
                       '</url></urlset>\n',
    }
    for _n, _b in NHC.items():
        (tmp / "de" / _n).write_text(_b, encoding="utf-8")
    ok = True

    print("[selftest] 正例必须全绿：")
    r = analyse(tmp / "de")
    if r["leak"] or r["broken"] or r["nonhtml"]:
        ok = False
        print(f"  ✗ 正例误伤：leak={r['leak']} broken={r['broken']} nonhtml={r['nonhtml']}")
    else:
        print("  ✓ HTML 0 泄漏 / 0 畸形；非 HTML 0 泄漏（语言切换器、外链、纯锚点、"
              "ld+json 转义、站点根、hreflang 交替链接均已正确豁免）")

    def expect(name: str, mutated: str, key: str) -> None:
        nonlocal ok
        assert mutated != CLEAN, f"{name}: 变异未生效"
        f.write_text(mutated, encoding="utf-8")
        rr = analyse(tmp / "de")
        hit = bool(rr[key])
        print(f"  {'✓' if hit else '✗'} 判红：{name} → {key} = {len(rr[key])}")
        if not hit:
            ok = False

    print("[selftest] 反例必须判红：")
    expect("[1] 站内链接指向英语路径",
           CLEAN.replace('<a href="/de/compare/" class="x">', '<a href="/compare/" class="x">', 1), "leak")
    expect("[1] 站内链接指向站点根 /",
           CLEAN.replace('<a href="#plans">Sprung</a>', '<a href="/">Home</a>', 1), "leak")
    expect('[1] 转义形态 href=\\"/compare/\\"（全形态提取）',
           CLEAN.replace('<a href="#plans">Sprung</a>', '<a href=\\"/compare/\\">Home</a>', 1), "leak")
    expect("[1] 绝对写法 http(s)://自有域名的英语路径",
           CLEAN.replace('<a href="#plans">Sprung</a>',
                         '<a href="https://www.esimsift.com/compare/">Home</a>', 1), "leak")
    expect("[1] 绝对写法指向自有域名根 https://www.esimsift.com/",
           CLEAN.replace('<a href="#plans">Sprung</a>',
                         '<a href="https://www.esimsift.com/">Home</a>', 1), "leak")
    expect("[2] 畸形反斜杠 href",
           CLEAN.replace('<a href="/de/compare/" class="x">', '<a href=\\"/de/compare/\\" class="x">', 1),
           "broken")

    print("[selftest] 边界（必须**不**判红）：")
    for name, mutated in (
        ("语言切换器（带 hreflang）指向另一语言",
         CLEAN.replace('href="/compare/" hreflang="en"', 'href="/es/compare/" hreflang="es"', 1)),
        ("外链指向竞品", CLEAN.replace('href="https://mybestsim.com/x"',
                                      'href="https://mybestsim.com/compare/"', 1)),
        ("协议相对外链 //host/…", CLEAN.replace('<a href="#plans">Sprung</a>',
                                              '<a href="//example.com/compare/">Sprung</a>', 1)),
        ("纯锚点 #fragment", CLEAN.replace('<a href="#plans">Sprung</a>',
                                         '<a href="#faq">Sprung</a>', 1)),
        ("mailto:", CLEAN.replace('<a href="#plans">Sprung</a>',
                                  '<a href="mailto:x@esimsift.com">Mail</a>', 1)),
        ("绝对写法的自有域名德语路径", CLEAN.replace('<a href="#plans">Sprung</a>',
                                              '<a href="https://www.esimsift.com/de/compare/">Sprung</a>', 1)),
        ("ld+json 块内的转义 href=\"…\"（红线 6：数据块须先挖掉）",
         CLEAN.replace('"b":"x \\u003c y"', '"b":"href=\\"/compare/\\" x \\u003c y"', 1)),
    ):
        assert mutated != CLEAN, f"{name}: 边界用例与正例相同（无意义）"
        f.write_text(mutated, encoding="utf-8")
        rr = analyse(tmp / "de")
        hit = bool(rr["leak"] or rr["broken"] or rr["nonhtml"])
        print(f"  {'✓' if not hit else '✗'} 不判红：{name} → leak/broken/nonhtml = "
              f"{len(rr['leak'])}/{len(rr['broken'])}/{len(rr['nonhtml'])}")
        if hit:
            ok = False

    def expect_nh(label: str, fname: str, mutated: str) -> None:
        nonlocal ok
        assert mutated != NHC[fname], f"{label}: 变异未生效"
        (tmp / "de" / fname).write_text(mutated, encoding="utf-8")
        rr = analyse(tmp / "de")
        hit = bool(rr["nonhtml"])
        print(f"  {'✓' if hit else '✗'} 判红：{label} → nonhtml = {len(rr['nonhtml'])}")
        if not hit:
            ok = False
        (tmp / "de" / fname).write_text(NHC[fname], encoding="utf-8")

    print("[selftest] 非 HTML 产物反例必须判红（红线 88：判据枚举什么才保护什么）：")
    expect_nh("[3] llms.txt 的 markdown 链接指向英语根", "llms.txt",
              NHC["llms.txt"].replace("/de/compare/", "/compare/", 1))
    expect_nh("[3] catalog.json 的页面 URL 指向英语根", "catalog.json",
              NHC["catalog.json"].replace("/de/compare/france/", "/compare/france/", 1))
    expect_nh("[3] sitemap.xml 的 <loc> 指向英语根", "sitemap.xml",
              NHC["sitemap.xml"].replace("<loc>https://www.esimsift.com/de/", "<loc>https://www.esimsift.com/", 1))

    print("[selftest] " + ("全过" if ok else "失败"))
    shutil.rmtree(tmp, ignore_errors=True)
    return 0 if ok else 1


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--selftest", action="store_true")
    args = ap.parse_args()
    if args.selftest:
        return selftest()
    return report(analyse(DE))


if __name__ == "__main__":
    raise SystemExit(main())
