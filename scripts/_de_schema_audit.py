# -*- coding: utf-8 -*-
"""德语页结构化数据抽查（**产物级**，只读，不写任何产物）。

判据分层（教训：「F 清单永远追不上数据」⇒ **硬判据只用结构性可穷举的事实**；
开放式文案黑名单只**报告**、不判红）：

  [1] JSON 合法性          —— 每个 `application/ld+json` 块必须 json.loads 成功。
  [2] @type 覆盖            —— 各类型在 de / en 侧的出现页数（普查，供人工对账）。
  [3] inLanguage            —— 是否存在、值集合、缺失页数（缺 = 结构性缺口，报告）。
  [4] URL 语言前缀（硬）    —— de 页里任何指向本站的 URL，除**语言无关**的两类外，
                               必须落在 `/de` 或 `/de/…`。**可穷举**的结构事实。
                               豁免 ①资源类（logo/image/…，见 RESOURCE_KEYS）；
                               豁免 ②组织身份（宿主 @type ∈ IDENTITY_TYPES 的 url/@id，
                                 指官网根才是语义正确的）。
                               ⚠ 语言根有**两种**合法写法：`/de`（面包屑首页项经
                                 `TrimSuffix "/"`）与 `/de/…`。只认 `/de/` 会假红。
  [5] 同页重复 @type         —— 同一页同一 @type 出现两次（schema 冲突风险），硬判据。
  [6] 与英语同路径页的
      @type 集合差异（硬）   —— de 与 en 同一相对路径页，顶层 @type 集合必须相同。
  [7] 逐 @type 键集合差异    —— 同 @type 在两侧的键集合必须相同（漏字段/多字段），硬判据。
  [8] 文本字段与英语逐字节相同（**报告**）—— 按**数据推导**的不可译白名单剔除后，
                               其余逐条列出供人工复核。

用法：
  python -X utf8 scripts/_de_schema_audit.py
  python -X utf8 scripts/_de_schema_audit.py --selftest   # 合成干净页正例 + 逐条反例
"""
from __future__ import annotations

import argparse
import json
import pathlib
import re
import shutil
import tomllib
from collections import Counter

ROOT = pathlib.Path(__file__).resolve().parents[1]
PUB = ROOT / "public"
DE = PUB / "de"
HOST = "https://www.esimsift.com"
BLOCK_RE = re.compile(r'<script[^>]*type="application/ld\+json"[^>]*>(.*?)</script>', re.S)

TEXT_KEYS = {"name", "headline", "description", "text", "alternateName",
             "caption", "abstract", "articleBody", "title"}
# ⚠ 资源类 URL：图片/模板资源，**语言无关**，不能拿来做 `/de/` 前缀判据
#   （首版判据漏了这条区分 ⇒ 把 645 页的 `logo` 全判成违规 = 误报）
RESOURCE_KEYS = {"logo", "image", "contentUrl", "thumbnailUrl", "urlTemplate"}

# ⚠ 组织身份 URL：`Organization` / `WebSite` 的 `url` / `@id` 标识**全站唯一的组织实体**，
#   指官网根才是语义正确的，**不该**带语言前缀 ⇒ 豁免（否则 645 页假红）。
#   ⚠ **只**豁免身份键。同宿主下的 `publishingPrinciples`（披露页）等**政策/导航**键
#   仍必须落在 `/de/` —— 德语读者该拿到德语披露页，豁免整张宿主 = 过度豁免。
IDENTITY_TYPES = {"Organization", "WebSite"}
IDENTITY_KEYS = {"url", "@id"}
# ⚠ 语言根的两种合法写法：面包屑首页项对 `.Site.Home.Permalink` 做了 `TrimSuffix "/"`
#   ⇒ 德语侧落到 `/de`（**无尾斜杠**）。只认 `/de/` 会把 645 页判成**假红**。


def is_de_url(tail: str) -> bool:
    return tail == "/de" or tail.startswith("/de/")


def known_ok_tokens() -> set[str]:
    """按数据推导「不可译」白名单（站点品牌 / 品牌名 / 供应商 key / 货币 / 语言码 / 单位），不手写文案。"""
    ok = {"eSIM", "USD", "EUR", "de", "en", "GB", "MB"}
    hugo = ROOT / "hugo.toml"
    if hugo.exists():
        m = re.search(r'(?m)^\s*title\s*=\s*"([^"]+)"', hugo.read_text(encoding="utf-8"))
        if m:
            ok.add(m.group(1))
    for path in (ROOT / "data" / "providers.toml", ROOT / "data" / "de" / "providers.toml"):
        if path.exists():
            for k, v in tomllib.loads(path.read_text(encoding="utf-8")).items():
                ok.add(str(v.get("name", k)))
                ok.add(k)
    return ok


def collect_blocks(html: str) -> list:
    return [json.loads(raw) for raw in BLOCK_RE.findall(html)]


def nodes(blocks: list):
    for b in blocks:
        for n in (b if isinstance(b, list) else [b]):
            yield n


def top_types(blocks: list) -> Counter:
    c = Counter()
    for n in nodes(blocks):
        if isinstance(n, dict) and isinstance(n.get("@type"), str):
            c[n["@type"]] += 1
    return c


def walk_types(node, acc: dict):
    if isinstance(node, list):
        for x in node:
            walk_types(x, acc)
        return
    if not isinstance(node, dict):
        return
    t = node.get("@type")
    if isinstance(t, str):
        acc.setdefault(t, set()).update(node.keys())
    for v in node.values():
        if isinstance(v, (dict, list)):
            walk_types(v, acc)


def find_leaves(node, path="", tchain=()):
    """产出 (JSON 路径, 所属 @type 链, 字段名, 值)。"""
    if isinstance(node, list):
        for i, x in enumerate(node):
            yield from find_leaves(x, f"{path}[{i}]" if path else f"[{i}]", tchain)
        return
    if not isinstance(node, dict):
        return
    t = node.get("@type")
    tc = tchain + (t,) if isinstance(t, str) else tchain
    for k, v in node.items():
        p = f"{path}.{k}" if path else k
        if isinstance(v, str):
            yield (p, tc, k, v)
        elif isinstance(v, (dict, list)):
            yield from find_leaves(v, p, tc)


def offending_urls(blocks: list) -> tuple[list[tuple[str, str]], int]:
    """→ (违规列表 [(JSON 路径, 值)], 被豁免的组织身份 URL 数)。

    豁免必须**可见**（数量回传、报告里打印），否则豁免会变成隐藏漏洞。
    """
    bad: list[tuple[str, str]] = []
    exempt = 0
    for b in blocks:
        for p, tc, k, v in find_leaves(b):
            if k in RESOURCE_KEYS or not v.startswith(HOST):
                continue
            owner = next((t for t in reversed(tc) if t), None)
            if owner in IDENTITY_TYPES and k in IDENTITY_KEYS:
                exempt += 1
                continue
            tail = v[len(HOST):]
            if tail in ("", "/") or is_de_url(tail):   # 站点根 / `/de` / `/de/…`
                continue
            bad.append((p, v))
    return bad, exempt


def analyse(pub: pathlib.Path, de: pathlib.Path, known: set[str]) -> dict:
    de_pages = sorted(de.rglob("*.html"))
    en_pages = sorted(p for p in pub.rglob("*.html") if p.relative_to(pub).parts[0] != "de")
    res = {"de_pages": len(de_pages), "en_pages": len(en_pages),
           "broken": [], "types": Counter(), "types_en": Counter(),
           "inlang": Counter(), "no_inlang": [], "url_bad": [], "url_exempt": 0, "dup_type": [],
           "type_diff": [], "key_diff": [], "same_text": [], "block_counts": Counter()}
    for p in de_pages:
        rel = str(p.relative_to(pub))
        try:
            blocks = collect_blocks(p.read_text(encoding="utf-8"))
        except json.JSONDecodeError as e:
            res["broken"].append((rel, str(e)))
            continue
        res["block_counts"][len(blocks)] += 1
        tt = top_types(blocks)
        res["types"].update(tt)
        if tt and max(tt.values()) > 1:
            res["dup_type"].append((rel, sorted(k for k, n in tt.items() if n > 1)))
        if not any(isinstance(n, dict) and "inLanguage" in n for n in nodes(blocks)):
            res["no_inlang"].append(rel)
        for n in nodes(blocks):
            if isinstance(n, dict) and "inLanguage" in n:
                res["inlang"][n["inLanguage"]] += 1
        bad, exempt = offending_urls(blocks)
        res["url_exempt"] += exempt
        if bad:
            res["url_bad"].append((rel, bad))

        ep = pub / p.relative_to(de)
        if not ep.exists():
            continue
        try:
            eblocks = collect_blocks(ep.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            eblocks = []
        ett = top_types(eblocks)
        res["types_en"].update(ett)
        if set(tt) != set(ett):
            res["type_diff"].append((rel, sorted(set(tt) - set(ett)), sorted(set(ett) - set(tt))))
        ka, ke = {}, {}
        walk_types(blocks, ka)
        walk_types(eblocks, ke)
        for t in sorted(set(ka) & set(ke)):
            if ka[t] != ke[t]:
                res["key_diff"].append((rel, t, sorted(ka[t] - ke[t]), sorted(ke[t] - ka[t])))
        ev = {(k, v) for b in eblocks for _p, _tc, k, v in find_leaves(b)}
        for b in blocks:
            for _p, tc, k, v in find_leaves(b):
                if k in TEXT_KEYS and (k, v) in ev and v not in known and len(v) > 3:
                    res["same_text"].append((rel, "·".join(str(x) for x in tc) or "?", k, v[:90]))
    return res


def report(res: dict, known: set[str]) -> int:
    print(f"[规模] de 页 {res['de_pages']} / en 页 {res['en_pages']}；"
          f"ld+json 块数分布 {dict(sorted(res['block_counts'].items()))}")
    ok = True

    print(f"\n[1] JSON 合法性：失败 {len(res['broken'])} 处")
    for rel, e in res["broken"][:10]:
        print(f"    ✗ {rel}: {e}")
    ok &= not res["broken"]

    print("\n[2] @type 覆盖（de / en 页数）：")
    for t, n in res["types"].most_common():
        print(f"    {t:22s} de={n:4d}  en={res['types_en'].get(t, 0):4d}")

    print(f"\n[3] inLanguage：出现 {sum(res['inlang'].values())} 处，值 = {dict(res['inlang'])}；"
          f"完全无 inLanguage 的页 = {len(res['no_inlang'])}")
    for rel in res["no_inlang"][:5]:
        print(f"    · {rel}")

    n_bad = sum(len(b) for _rel, b in res["url_bad"])
    print(f"\n[4] ★ URL 语言前缀（硬判据）：违规 {n_bad} 处 / {len(res['url_bad'])} 页"
          f"（豁免的组织身份 URL {res['url_exempt']} 处，见 IDENTITY_TYPES）")
    for rel, bad in res["url_bad"][:12]:
        print(f"    ✗ {rel}  ({len(bad)} 处)")
        for pp, v in bad[:3]:
            print(f"        {pp} = {v}")
    ok &= not res["url_bad"]

    print(f"\n[5] ★ 同页重复 @type（硬判据）：{len(res['dup_type'])} 页")
    for rel, ts in res["dup_type"][:10]:
        print(f"    ✗ {rel}: {ts}")
    ok &= not res["dup_type"]

    print(f"\n[6] ★ 与英语同路径页的 @type 集合差异（硬判据）：{len(res['type_diff'])} 页")
    for rel, miss, extra in res["type_diff"][:12]:
        print(f"    ✗ {rel}: 缺 {miss} / 多 {extra}")
    ok &= not res["type_diff"]

    print(f"\n[7] ★ 逐 @type 键集合差异（硬判据）：{len(res['key_diff'])} 处")
    for rel, t, miss, extra in res["key_diff"][:12]:
        print(f"    ✗ {rel} [{t}]: 缺 {miss} / 多 {extra}")
    ok &= not res["key_diff"]

    print(f"\n[8] 文本字段与英语逐字节相同（**报告**，白名单 {len(known)} 词项已剔除）："
          f"{len(res['same_text'])} 处")
    for (tc, k, v), n in Counter((tc, k, v) for _, tc, k, v in res["same_text"]).most_common(40):
        print(f"    {n:4d}×  [{tc}] {k}: {v!r}")
    print(f"    （按 @type 汇总：{dict(Counter(tc for _, tc, _k, _v in res['same_text']).most_common(8))}）")
    return 0 if ok else 1


# ── selftest：合成干净页做正例，逐条注入反例 ──
# ⚠ 正例必须**覆盖新边界**（`/de` 无尾斜杠 / 组织身份豁免），否则模板一改就假红。
# ⚠ 反例必须**覆盖防过度豁免**（同宿主下的政策键仍须带 /de/）。
CLEAN_DE = """<!doctype html><html lang="de"><head>
<script type="application/ld+json">
{"@context":"https://schema.org","@type":"BreadcrumbList","inLanguage":"de","itemListElement":[
 {"@type":"ListItem","item":"%HOST%/de","name":"Startseite","position":1},
 {"@type":"ListItem","item":"%HOST%/de/compare/","name":"Ländervergleich","position":2}]}
</script>
<script type="application/ld+json">
{"@context":"https://schema.org","@type":"Organization","inLanguage":"de","name":"Probe Sift",
 "url":"%HOST%/","logo":"%HOST%/apple-touch-icon.png",
 "publishingPrinciples":"%HOST%/de/disclosure/"}
</script>
<script type="application/ld+json">
{"@context":"https://schema.org","@type":"WebSite","inLanguage":"de","name":"Probe Sift","url":"%HOST%/"}
</script>
<script type="application/ld+json">
{"@context":"https://schema.org","@type":"Product","inLanguage":"de","name":"Probe eSIM-Tarife",
 "logo":"%HOST%/apple-touch-icon.png",
 "offers":{"@type":"AggregateOffer","priceCurrency":"USD","lowPrice":"1.00","highPrice":"9.00","offerCount":3},
 "url":"%HOST%/de/compare/probe/"}
</script>
<script type="application/ld+json">
{"@context":"https://schema.org","@type":"ItemList","inLanguage":"de","itemListElement":[
 {"@type":"ListItem","position":1,"name":"Anbieter A Probe","url":"%HOST%/de/compare/probe/a/",
  "item":{"@type":"Country","name":"Probe","url":"%HOST%/de/compare/probe/country/"}}]}
</script>
</head><body>Probe</body></html>"""

CLEAN_EN = CLEAN_DE.replace('"%HOST%/de/', '"%HOST%/') \
    .replace('"item":"%HOST%/de"', '"item":"%HOST%"') \
    .replace('"inLanguage":"de"', '"inLanguage":"en"') \
    .replace("Startseite", "Home").replace("Ländervergleich", "Country comparisons") \
    .replace("Probe eSIM-Tarife", "Probe eSIM plans").replace("Anbieter A Probe", "Provider A probe")


def selftest() -> int:
    tmp = ROOT / ".buildlog" / "_de_schema_selftest"
    shutil.rmtree(tmp, ignore_errors=True)
    (tmp / "de" / "compare" / "probe").mkdir(parents=True)
    (tmp / "compare" / "probe").mkdir(parents=True)
    clean_de = CLEAN_DE.replace("%HOST%", HOST)
    (tmp / "de" / "compare" / "probe" / "index.html").write_text(clean_de, encoding="utf-8")
    (tmp / "compare" / "probe" / "index.html").write_text(
        CLEAN_EN.replace("%HOST%", HOST), encoding="utf-8")

    known = known_ok_tokens()
    ok = True

    print("[selftest] 正例（合成干净 de 页）必须全绿：")
    r = analyse(tmp, tmp / "de", known)
    hard = {k: r[k] for k in ("broken", "url_bad", "dup_type", "type_diff", "key_diff") if r[k]}
    if hard:
        ok = False
        print(f"  ✗ 正例误伤：{hard}")
    else:
        print("  ✓ 五条硬判据全绿")
    # 正例必须真的走到豁免分支（豁免数 > 0），否则豁免是**死代码**、无从证伪
    if r["url_exempt"] <= 0:
        ok = False
        print("  ✗ 正例未触发组织身份豁免（url_exempt = 0）—— 豁免路径未被证明")
    else:
        print(f"  ✓ 组织身份豁免生效：url_exempt = {r['url_exempt']} 处")

    def run(mutated: str) -> dict:
        assert mutated != clean_de, "变异未生效（片段没匹配上）—— selftest 本身失效"
        (tmp / "de" / "compare" / "probe" / "index.html").write_text(mutated, encoding="utf-8")
        return analyse(tmp, tmp / "de", known)

    def expect_red(name: str, mutated: str, key: str = "url_bad") -> None:
        nonlocal ok
        rr = run(mutated)
        hit = bool(rr[key])
        print(f"  {'✓' if hit else '✗'} 判红：{name} → {key} = {len(rr[key])}")
        if not hit:
            ok = False

    def boundary(name: str, mutated: str) -> None:
        """边界正例：**必须不**判红（模板一改最容易在这里假红）。"""
        nonlocal ok
        rr = run(mutated)
        hit = bool(rr["url_bad"])
        print(f"  {'✓' if not hit else '✗'} 不判红：{name} → url_bad = {len(rr['url_bad'])}")
        if hit:
            ok = False

    # 锚点：确保每条变异**只**命中目标字段
    A_ORG_URL = f'"url":"{HOST}/","logo"'                       # Organization.url（带 logo 尾随）
    A_ORG_LOGO = f'"url":"{HOST}/","logo":"{HOST}/apple-touch-icon.png"'   # 仅 Organization（Product 的 url 不同）
    A_PROD_URL = f'"url":"{HOST}/de/compare/probe/"'            # 仅 Product（Country 用 …/probe/country/）
    A_CRUMB2 = f'"item":"{HOST}/de/compare/"'
    A_COUNTRY = '"@type":"Country","name":"Probe","url":"' + f'{HOST}/de/compare/probe/country/"'
    A_POLICY = f'"publishingPrinciples":"{HOST}/de/disclosure/"'
    A_HOME = f'"item":"{HOST}/de"'
    for nm, a in (("A_ORG_URL", A_ORG_URL), ("A_ORG_LOGO", A_ORG_LOGO), ("A_PROD_URL", A_PROD_URL),
                  ("A_CRUMB2", A_CRUMB2), ("A_COUNTRY", A_COUNTRY), ("A_POLICY", A_POLICY),
                  ("A_HOME", A_HOME)):
        assert clean_de.count(a) == 1, f"锚点 {nm} 在正例里出现 {clean_de.count(a)} 次（应为 1）"

    print("[selftest] 反例必须判红：")
    expect_red("[1] JSON 合法性", clean_de.replace('{"@context"', '{oops:"@context"', 1), "broken")
    expect_red("[4] 面包屑 `item` 缺 /de/", clean_de.replace(
        A_CRUMB2, f'"item":"{HOST}/compare/"', 1))
    expect_red("[4] `Country.url` 缺 /de/", clean_de.replace(
        A_COUNTRY, A_COUNTRY.replace(f"{HOST}/de/compare/probe/country/", f"{HOST}/compare/probe/country/"), 1))
    expect_red("[4] `Product.url` 缺 /de/", clean_de.replace(
        A_PROD_URL, f'"url":"{HOST}/compare/probe/"', 1))
    expect_red("[4] 组织身份豁免**不得**过头（publishingPrinciples 仍须 /de/）", clean_de.replace(
        A_POLICY, f'"publishingPrinciples":"{HOST}/disclosure/"', 1))
    expect_red("[5] 同页重复 @type", clean_de.replace(
        "<head>", '<head><script type="application/ld+json">'
        '{"@context":"https://schema.org","@type":"Product","name":"Dup"}</script>', 1), "dup_type")
    i = clean_de.index('<script type="application/ld+json">')
    j = clean_de.index("</script>", i) + len("</script>")
    expect_red("[6] 与英语 @type 集合差异", clean_de[:i] + clean_de[j:], "type_diff")
    expect_red("[7] 逐 @type 键集合差异",
               clean_de.replace('"@type":"Product","inLanguage":"de",', '"@type":"Product",', 1), "key_diff")

    print("[selftest] 边界（**必须不**判红）：")
    # ⚠ 核心边界：面包屑首页项对 `.Site.Home.Permalink` 做 TrimSuffix "/" ⇒ `%HOST%/de`。
    #   该字面量已在正例里、且正例判绿 ⇒ 由正例段证明；此处显式确认字面量存在（防正例被改掉）。
    print(f"  ✓ 正例已含临界字面量 {A_HOME}（无尾斜杠）且判绿")
    boundary(f"面包屑首页项退化为官网根 {HOST}", clean_de.replace(A_HOME, f'"item":"{HOST}"', 1))
    boundary(f"`Organization.url` = {HOST}/en/（组织身份语言无关 ⇒ 豁免）",
             clean_de.replace(A_ORG_URL, f'"url":"{HOST}/en/","logo"', 1))
    boundary(f"`logo` = {HOST}/img/providers/probe.png（资源键豁免，不带 /de/）",
             clean_de.replace(A_ORG_LOGO, f'"url":"{HOST}/","logo":"{HOST}/img/providers/probe.png"', 1))

    print("[selftest] " + ("全过" if ok else "失败"))
    shutil.rmtree(tmp, ignore_errors=True)
    return 0 if ok else 1


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--selftest", action="store_true")
    args = ap.parse_args()
    if args.selftest:
        return selftest()
    return report(analyse(PUB, DE, known_ok_tokens()), known_ok_tokens())


if __name__ == "__main__":
    raise SystemExit(main())
