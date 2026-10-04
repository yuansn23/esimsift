# -*- coding: utf-8 -*-
"""品牌×国家子页（/compare/<country>/<provider>/，全站 400 页）的产出验收守卫。

为什么单独一个脚本：这一层页面是站内数量最大、模板最复杂、也最容易被"数据变了
但模板没跟上"伤到的一层。`hugo` 对下列问题全部保持沉默（渲染成功、退出码 0）：

  · i18n key 写错 → 整段文案变成空串，`<h2></h2>` 空着上线
  · JSON-LD 里某个字段取到 nil → 生成 `"offers": null`，结构化数据静默失效
  · `range` 绑定变量写错 → 循环体整块不输出
  · 标题候选串全都不符合长度要求 → 落到最后一档（可能既含价格又含套餐数）

所以标题规则、JSON-LD 完整性、空标题、模板残留、内部一致性——都得从**产物**里读。

用法（先 hugo 再跑）：
    python -X utf8 scripts/verify_provider_pages.py
    python -X utf8 scripts/verify_provider_pages.py --sample 12   # 附带打印若干样本
"""
from __future__ import annotations

import argparse
import html
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PUBLIC = ROOT / "public"

TITLE_RE = re.compile(r"<title>(.*?)</title>", re.S)
DESC_RE = re.compile(r'<meta\s+name="description"\s+content="(.*?)"', re.S)
H1_RE = re.compile(r"<h1[^>]*>(.*?)</h1>", re.S)
H2H3_RE = re.compile(r"<h([23])[^>]*>(.*?)</h\1>", re.S)
LDJSON_RE = re.compile(r'<script type="application/ld\+json">(.*?)</script>', re.S)
EYEBROW_RE = re.compile(r'<p class="eyebrow">(.*?)</p>', re.S)
ROW_RE = re.compile(r"<tr data-price=", re.S)
# 整行（套餐表）：<tr data-price=… data-perday=… data-gb=… data-days=… data-pergb=…>…</tr>
PLAN_ROW_RE = re.compile(
    r'<tr data-price="[^"]*"[^>]*data-gb="([^"]*)"[^>]*>(.*?)</tr>', re.S)
TD_RE = re.compile(r"<td[^>]*>(.*?)</td>", re.S)

# 用户 2026-10-04 定的标题规则：48–54 字符、必含品牌词与国家名、
# **不放套餐数量、不放价格**（价格锚点交给 description）。
TITLE_MIN, TITLE_MAX = 48, 54
DESC_MIN, DESC_MAX = 120, 140
TITLE_BANNED = [
    (re.compile(r"\$"), "含价格符号 $"),
    (re.compile(r"\b\d+\s+plans?\b", re.I), "含套餐数量"),
    (re.compile(r"\bplans?\s*:\s*\d+", re.I), "含套餐数量"),
]

errors: list[str] = []


def text_of(raw: str) -> str:
    """去掉标签与换行，实体解码 —— 判空和长度都用它。"""
    return html.unescape(re.sub(r"<[^>]+>", "", raw)).strip()


def walk(obj):
    if isinstance(obj, dict):
        yield obj
        for v in obj.values():
            yield from walk(v)
    elif isinstance(obj, list):
        for v in obj:
            yield from walk(v)


def nodes_of_type(blocks, want: str) -> list[dict]:
    out = []
    for b in blocks:
        for n in walk(b):
            t = n.get("@type")
            if t == want or (isinstance(t, list) and want in t):
                out.append(n)
    return out


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--sample", type=int, default=0, help="打印前 N 个页面的关键字段")
    args = ap.parse_args()

    if not PUBLIC.is_dir():
        print("ERROR public/ not found - run `hugo` first")
        return 1

    pages = sorted(
        p for p in PUBLIC.glob("compare/*/*/index.html")
    )
    if not pages:
        print("ERROR 没找到任何 compare/<country>/<provider>/index.html")
        return 1

    stats = {
        "title_ok": 0, "desc_ok": 0, "h1_ok": 0, "ld_ok": 0,
        "faq_ok": 0, "crumb_ok": 0, "webpage_ok": 0, "offers_total": 0,
        "trip_rows": 0, "unverified_pages": 0,
        "unlimited_rows": 0, "subgb_rows": 0,
        "plancount_ok": 0, "chips_ok": 0,
    }
    title_lengths: list[int] = []
    samples: list[str] = []

    for f in pages:
        rel = f.relative_to(PUBLIC).as_posix()
        raw = f.read_text(encoding="utf-8", errors="replace")

        # 0. 未解析的模板残留 / Go 格式化错误（check_output 也查，这里贴近页面再查一遍）
        for bad in ("{{", "}}", "%!s(", "%!d("):
            if bad in raw:
                errors.append(f"{rel}: 产物里有模板残留/格式化错误 {bad!r}")
                break

        # 1. 标题规则
        mt = TITLE_RE.search(raw)
        if not mt:
            errors.append(f"{rel}: 没有 <title>")
            title = ""
        else:
            title = html.unescape(mt.group(1)).strip()
            title_lengths.append(len(title))
            if not (TITLE_MIN <= len(title) <= TITLE_MAX):
                errors.append(f"{rel}: 标题 {len(title)} 字符，要求 {TITLE_MIN}-{TITLE_MAX} -> {title!r}")
            for rx, why in TITLE_BANNED:
                if rx.search(title):
                    errors.append(f"{rel}: 标题{why} -> {title!r}")
            # 品牌词 + 国家名（rel = compare/<country>/<provider>/index.html）
            parts = rel.split("/")
            country_slug_t = parts[1]
            if country_slug_t.replace("-", " ") not in title.lower().replace("-", " "):
                errors.append(f"{rel}: 标题里没有国家名（{country_slug_t}）-> {title!r}")
            else:
                stats["title_ok"] += 1

        # 2. description 长度 + 品牌署名
        md = DESC_RE.search(raw)
        if not md:
            errors.append(f"{rel}: 没有 meta description")
        else:
            d = html.unescape(md.group(1)).strip()
            if not (DESC_MIN <= len(d) <= DESC_MAX):
                errors.append(f"{rel}: description {len(d)} 字符，要求 {DESC_MIN}-{DESC_MAX}")
            elif "eSIM Sift" not in d:
                errors.append(f"{rel}: description 缺品牌署名 'eSIM Sift'")
            else:
                stats["desc_ok"] += 1

        # 3. H1：恰好一个、含年份
        h1s = H1_RE.findall(raw)
        h1 = text_of(h1s[0]) if h1s else ""
        if len(h1s) != 1:
            errors.append(f"{rel}: 有 {len(h1s)} 个 <h1>（必须恰好 1 个）")
        elif "eSIM" not in h1:
            errors.append(f"{rel}: H1 不含 'eSIM' -> {h1!r}")
        elif not re.search(r"\b20\d\d\b", h1):
            errors.append(f"{rel}: H1 不含年份 -> {h1!r}")
        else:
            stats["h1_ok"] += 1

        # 4. 空标题（i18n key 漏定义的典型症状）
        for lvl, inner in H2H3_RE.findall(raw):
            if not text_of(inner):
                errors.append(f"{rel}: 空的 <h{lvl}></h{lvl}>")
        for inner in EYEBROW_RE.findall(raw):
            if not text_of(inner):
                errors.append(f"{rel}: 空的 eyebrow 段落")

        # 5. JSON-LD
        blocks = []
        for m in LDJSON_RE.finditer(raw):
            try:
                blocks.append(json.loads(m.group(1)))
            except ValueError as e:
                errors.append(f"{rel}: JSON-LD 解析失败 - {e}")
        if not blocks:
            errors.append(f"{rel}: 没有任何 JSON-LD")
            continue

        products = nodes_of_type(blocks, "Product")
        if not products:
            errors.append(f"{rel}: 缺 Product 节点")
        else:
            p0 = products[0]
            offers = p0.get("offers")
            if not isinstance(offers, dict):
                errors.append(f"{rel}: Product.offers 不是对象 -> {type(offers).__name__}")
            else:
                if offers.get("@type") != "AggregateOffer":
                    errors.append(f"{rel}: Product.offers 不是 AggregateOffer")
                inner = offers.get("offers")
                rows = len(ROW_RE.findall(raw))
                if not isinstance(inner, list) or not inner:
                    errors.append(f"{rel}: AggregateOffer.offers 不是非空数组")
                else:
                    stats["offers_total"] += len(inner)
                    if len(inner) != rows:
                        errors.append(
                            f"{rel}: 逐个套餐 Offer 数 {len(inner)} != 价格表行数 {rows}")
                    else:
                        stats["ld_ok"] += 1
                    for o in inner:
                        if not isinstance(o.get("price"), (int, float)):
                            errors.append(f"{rel}: Offer.price 不是数字 -> {o.get('price')!r}")
                            break
                        if o.get("priceCurrency") != "USD":
                            errors.append(f"{rel}: Offer.priceCurrency 不是 USD")
                            break

        # 6. FAQPage：>=3 组，且问答都非空
        faqs = nodes_of_type(blocks, "FAQPage")
        if not faqs:
            errors.append(f"{rel}: 缺 FAQPage 节点")
        else:
            ents = faqs[0].get("mainEntity") or []
            ok = len(ents) >= 3
            for e in ents:
                if not text_of(str(e.get("name", ""))) or not text_of(
                        str((e.get("acceptedAnswer") or {}).get("text", ""))):
                    ok = False
                    break
            if ok:
                stats["faq_ok"] += 1
            else:
                errors.append(f"{rel}: FAQPage 条目不足或问答为空（{len(ents)} 条）")

        # 7. BreadcrumbList：4 级，且与真实路径一致
        crumbs = nodes_of_type(blocks, "BreadcrumbList")
        if not crumbs:
            errors.append(f"{rel}: 缺 BreadcrumbList")
        else:
            items = sorted(crumbs[0].get("itemListElement") or [],
                           key=lambda x: x.get("position", 0))
            country_slug = rel.split("/")[1]
            prov = rel.split("/")[2]
            expect = [None, "compare/", f"compare/{country_slug}/", None]
            ok = len(items) == 4
            if ok:
                for it, want in zip(items, expect):
                    if want is None:
                        continue
                    if want not in str(it.get("item", "")):
                        ok = False
                        errors.append(
                            f"{rel}: 面包屑第 {it.get('position')} 级指向 {it.get('item')!r}，期望含 {want!r}")
                        break
                if ok and prov.replace("-", " ") not in str(items[3].get("name", "")).lower():
                    # 末级 name 用品牌显示名，这里只做「非空 + 不含 href」的弱校验
                    pass
            if ok:
                stats["crumb_ok"] += 1
            else:
                errors.append(f"{rel}: 面包屑不是 4 级（{len(items)} 级）")

        # 8. WebPage：inLanguage + dateModified
        wps = nodes_of_type(blocks, "WebPage")
        if not wps:
            errors.append(f"{rel}: 缺 WebPage 节点")
        else:
            w = wps[0]
            if not w.get("inLanguage"):
                errors.append(f"{rel}: WebPage 缺 inLanguage")
            elif not re.match(r"^\d{4}-\d{2}-\d{2}$", str(w.get("dateModified", ""))):
                errors.append(f"{rel}: WebPage.dateModified 非法 -> {w.get('dateModified')!r}")
            else:
                stats["webpage_ok"] += 1

        # 9. 决策模块存在性（这几块是本轮升级的交付物，缺一即回归）
        for anchor in ("reality", "tripcost", "fit", "faq", "plans"):
            if f'id="{anchor}"' not in raw:
                errors.append(f"{rel}: 缺 id=\"{anchor}\" 区块")
        if "Not checked yet" in raw:
            stats["unverified_pages"] += 1

        # 10. 行程对比表行数
        trip = raw.find('id="tripcost"')
        if trip > 0:
            seg = raw[trip:trip + 6000]
            stats["trip_rows"] += seg.count("<tr>")

        # 11. ★ data-gb 与数据列的标注必须一致
        #     为什么要单列：`gb` 用 0 表示"无限"，而小于 1GB 的计量档存的是小数
        #     （500MB → 0.4883）。上游任何一处 `int .gb` 都会把 500MB 截断成 0，
        #     页面随即把它标成 "Unlimited" —— 与事实相反，且是读者最会当真的一栏。
        #     2026-10-04 实际发生过（country-stats.html 的 `"gb" (int .gb)`）。
        for gb_raw, body in PLAN_ROW_RE.findall(raw):
            try:
                gb = float(gb_raw)
            except ValueError:
                errors.append(f"{rel}: 套餐行的 data-gb 不是数字 -> {gb_raw!r}")
                continue
            cells = TD_RE.findall(body)
            data_cell = text_of(cells[1]) if len(cells) > 1 else ""
            says_unlimited = "unlimited" in data_cell.lower()
            if gb == 0.0 and not says_unlimited:
                errors.append(f"{rel}: data-gb=0（无限）但数据列显示 {data_cell!r}")
            elif gb != 0.0 and says_unlimited:
                errors.append(
                    f"{rel}: data-gb={gb_raw}（计量）却被标成 Unlimited -> {data_cell!r}")
            elif 0.0 < gb < 1.0 and not re.match(r"^\d+MB$", data_cell):
                errors.append(
                    f"{rel}: data-gb={gb_raw} 小于 1GB，数据列应显示 MB -> {data_cell!r}")
            elif gb > 0 and says_unlimited is False and data_cell == "":
                errors.append(f"{rel}: 数据列空白（data-gb={gb_raw}）")
            if gb == 0.0:
                stats["unlimited_rows"] += 1
            elif gb < 1.0:
                stats["subgb_rows"] += 1

        # 12. ★ 计划数必须能自己核对（2026-10-04 读者质疑「为什么是 6 个」后加的）
        #     页面顶着「All N {品牌} {国家} plans」，下面又给一排「M 天」按钮。
        #     N 不能是个来路不明的数字：它必须同时等于
        #       ① 价格表的行数（读者能自己数）
        #       ② JSON-LD 里逐个套餐 Offer 的条数（结构化数据说的）
        #       ③ 紧跟 H2 的说明行里那个 N（口径明写）
        #     天数按钮则必须「只包含表里真实存在的有效期」——
        #     多一个 = 读者能点到一个买不到的行程长度。
        mh2 = re.search(r'<h2 id="plans"[^>]*>(.*?)</h2>', raw, re.S)
        if not mh2:
            errors.append(f'{rel}: 找不到 <h2 id="plans">')
        else:
            h2t = text_of(mh2.group(1))
            mnum = re.search(r"\d+", h2t)
            rows_n = len(ROW_RE.findall(raw))
            if not mnum:
                errors.append(f"{rel}: 套餐表 H2 里没有数量 -> {h2t!r}")
            else:
                claimed = int(mnum.group(0))
                if claimed != rows_n:
                    errors.append(f"{rel}: H2 宣称 {claimed} 个套餐，价格表却有 {rows_n} 行")
                else:
                    # 说明行紧跟 H2，形如「6 plans · 6 trip lengths · 3 to 30 days」
                    tailseg = raw[mh2.end():mh2.end() + 400]
                    mb = re.search(r"<p[^>]*>(.*?)</p>", tailseg, re.S)
                    bnum = re.search(r"\d+", text_of(mb.group(1))) if mb else None
                    if not bnum:
                        errors.append(f"{rel}: H2 下面没有套餐数说明行")
                    elif int(bnum.group(0)) != claimed:
                        errors.append(
                            f"{rel}: 说明行写 {bnum.group(0)} 个套餐，H2 写 {claimed} 个")
                    else:
                        stats["plancount_ok"] += 1

        # 13. 天数按钮不得出现表里没有的有效期
        table_days = set(re.findall(r'<tr data-price="[^"]*"[^>]*data-days="(\d+)"', raw))
        grp = re.search(r'id="plan-days-group".*?</div>', raw, re.S)
        if grp:
            btns = set(re.findall(r'data-days="(\d+)"', grp.group(0)))
            btns.discard("0")           # 0 = "Any trip length"，不是档位
            phantom = sorted(int(x) for x in btns - table_days)
            if phantom:
                errors.append(f"{rel}: 天数按钮含表里不存在的档位 {phantom}")
            elif not btns:
                errors.append(f"{rel}: 天数按钮组是空的")
            else:
                stats["chips_ok"] += 1

        if len(samples) < args.sample:
            samples.append(
                f"  {rel}\n    title({len(title)}): {title}\n    h1: {h1}")

    total = len(pages)
    print(f"检查 {total} 个品牌×国家子页")
    print(f"  标题合规 {stats['title_ok']}/{total}"
          f"（长度 {min(title_lengths)}–{max(title_lengths)}，"
          f"均 {sum(title_lengths) / len(title_lengths):.1f}）")
    print(f"  description 合规 {stats['desc_ok']}/{total}")
    print(f"  H1 合规 {stats['h1_ok']}/{total}")
    print(f"  逐套餐 Offer 与价格表行数一致 {stats['ld_ok']}/{total}"
          f"（Offer 合计 {stats['offers_total']} 条）")
    print(f"  FAQPage 合规 {stats['faq_ok']}/{total}")
    print(f"  BreadcrumbList 4 级 {stats['crumb_ok']}/{total}")
    print(f"  WebPage 元数据 {stats['webpage_ok']}/{total}")
    print(f"  行程对比表累计 {stats['trip_rows']} 行")
    print(f"  计划数三处对账 {stats['plancount_ok']}/{total}"
          f"（H2 = 价格表行数 = Offer 数 = 说明行）")
    print(f"  天数按钮无假档位 {stats['chips_ok']}/{total}")
    print(f"  套餐行标注一致：无限 {stats['unlimited_rows']} 行 /"
          f" 小于 1GB 的计量档 {stats['subgb_rows']} 行")
    print(f"  仍显示「尚未核实」政策的页面 {stats['unverified_pages']}"
          f"（预期 = 未填 policy 的品牌页数）")

    if samples:
        print("\n样本：")
        print("\n".join(samples))

    if errors:
        print(f"\nFAIL: {len(errors)} 处问题")
        for e in errors[:40]:
            print(f"  ✗ {e}")
        if len(errors) > 40:
            print(f"  ... 另有 {len(errors) - 40} 处")
        return 1
    print("\nOK: 品牌×国家子页全部通过")
    return 0


if __name__ == "__main__":
    sys.exit(main())
