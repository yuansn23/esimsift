"""批 E 审核取数 —— 51 页德语 compare 正文的**现算**指标（全部从盘上重算，不照搬任何文档）。

用法：
  python -X utf8 scripts/_audit_de_batch_e.py
  python -X utf8 scripts/_audit_de_batch_e.py --json out.json
"""
from __future__ import annotations

import argparse
import collections
import json
import pathlib
import re
import sys
import tomllib

ROOT = pathlib.Path(__file__).resolve().parent.parent
EN = ROOT / "content" / "en" / "compare"
DE = ROOT / "content" / "de" / "compare"

# 51 页 = 50 国家页（无 layout 的普通页）+ 1 hub（_index.md）
SKIP_STEMS = {"matchups"}


def body_of(md: str) -> str:
    """取 front matter 之后的正文。"""
    parts = md.split("---\n", 2)
    return parts[2] if len(parts) == 3 else ""


def paragraphs(body: str) -> list[str]:
    return [p.strip() for p in re.split(r"\n\s*\n", body) if p.strip()]


def sentences(text: str) -> list[str]:
    # 德语句号/问号/感叹号；数字里的点不算断句（用后置断言）
    parts = re.split(r"(?<=[.!?])\s+", text)
    return [s.strip() for s in parts if len(s.strip()) > 12]


def seo_desc(fm: str) -> str:
    m = re.search(r'^\s*description:\s*"(.*)"\s*$', fm, re.M)
    return m.group(1) if m else ""


def nums(s: str) -> list[str]:
    """description 里的数值序列（德语逗号小数归一成点号后比较）。"""
    return [x.replace(",", ".") for x in re.findall(r"\d+(?:[.,]\d+)?", s)]


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--json", default="")
    args = ap.parse_args()

    # ① 页集：批 E = 顶层 50 个国家页 + 1 个 hub（`_index.md`）
    #    排除 46 个模板驱动页：`matchups.md` + 45 个 `*-vs-*.md`
    #    （它们的正文来自 `data/`，批 E 不写；只需 D9 统一删 noindex）
    def page_set(d: pathlib.Path) -> list[pathlib.Path]:
        out = []
        for p in sorted(d.glob("*.md")):
            if p.stem in SKIP_STEMS or "-vs-" in p.stem:
                continue
            out.append(p)
        return out

    en_pages = page_set(EN)
    de_pages = page_set(DE)
    res: dict = {
        "en_pages": len(en_pages),
        "de_pages": len(de_pages),
        "files": [],
    }

    para_all: list[str] = []
    sent_all: list[str] = []
    bytes_de = bytes_en = 0
    chars_de = chars_en = 0
    seo_mismatch: list[str] = []
    seo_pairs: list[tuple[str, str, str]] = []

    for dp in de_pages:
        ep = EN / dp.name
        dtext = dp.read_text(encoding="utf-8")
        etext = ep.read_text(encoding="utf-8") if ep.exists() else ""
        dbody, ebody = body_of(dtext), body_of(etext)
        dpar, epar = paragraphs(dbody), paragraphs(ebody)
        dseo, eseo = seo_desc(dtext), seo_desc(etext)
        raw = dp.read_bytes()
        bytes_de += len(raw)
        bytes_en += len(ep.read_bytes()) if ep.exists() else 0
        chars_de += len(re.sub(r"\s+", " ", dbody).strip())
        chars_en += len(re.sub(r"\s+", " ", ebody).strip())
        para_all += dpar
        for p in dpar:
            sent_all += sentences(p)
        # ⚠ 英德 description 本就是两种文字，比**数字**才有意义（比字符串会 51/51 全红）
        if nums(dseo) != nums(eseo):
            seo_mismatch.append(dp.stem)
        seo_pairs.append((dp.stem, dseo, eseo))
        res["files"].append({
            "slug": dp.stem,
            "bytes": len(raw),
            "crlf": raw.count(b"\r\n"),
            "paras_de": len(dpar),
            "paras_en": len(epar),
            "h2_de": len(re.findall(r"^## ", dbody, re.M)),
            "h2_en": len(re.findall(r"^## ", ebody, re.M)),
            "shortcodes_de": sorted(re.findall(r"\{\{<\s*([a-z-]+)\s*>\}\}", dbody)),
            "shortcodes_en": sorted(re.findall(r"\{\{<\s*([a-z-]+)\s*>\}\}", ebody)),
            "noindex": "noindex: true" in dtext,
            "chars_de": len(re.sub(r"\s+", " ", dbody).strip()),
            "chars_en": len(re.sub(r"\s+", " ", ebody).strip()),
        })

    res["bytes_de_total"] = bytes_de
    res["bytes_en_total"] = bytes_en
    res["chars_de"] = chars_de
    res["chars_en"] = chars_en
    res["char_ratio"] = round(chars_de / chars_en, 3) if chars_en else 0

    # ② 反同质化：段级 / 句级唯一率
    res["paras_total"] = len(para_all)
    res["paras_uniq"] = len(set(para_all))
    res["sents_total"] = len(sent_all)
    res["sents_uniq"] = len(set(sent_all))
    dup_s = [s for s, n in collections.Counter(sent_all).items() if n > 1]
    res["dupe_sentences"] = dup_s[:10]
    res["dupe_sentence_count"] = len(dup_s)

    # ③ seo 一致性
    res["seo_mismatch"] = seo_mismatch
    res["seo_checked"] = len(seo_pairs)

    # ④ 术语一致性（在 51 页正文里）
    alltext = "\n".join(body_of(p.read_text(encoding="utf-8")) for p in de_pages)
    fulltext = "\n".join(p.read_text(encoding="utf-8") for p in de_pages)
    terms = {
        "Mbit/s": alltext.count("Mbit/s"),
        "Mbps": len(re.findall(r"\bMbps\b", alltext)),
        "Kbps": len(re.findall(r"\bKbps\b", alltext)),
        "unbegrenzt*": len(re.findall(r"\b[Uu]nbegrenzt", fulltext)),
        "unlimited": len(re.findall(r"(?i)\bunlimited\b", fulltext)),
        "price_dot": len(re.findall(r"\$\d+\.\d", alltext)),
        "price_comma": len(re.findall(r"\$\d+,\d", alltext)),
        "gb_with_space": len(re.findall(r"\d+\s+(?:GB|MB)\b", alltext)),
        "gb_no_space": len(re.findall(r"\d+(?:GB|MB)\b", alltext)),
    }
    res["terms"] = terms

    # ⑤ 品牌名规范形态（首字母大写），禁止小写变体
    prov = tomllib.loads((ROOT / "data" / "providers.toml").read_text(encoding="utf-8"))
    names = [v["name"] for v in prov.values() if isinstance(v, dict) and v.get("name")]
    bad_brand = []
    for n in names:
        low = n.lower()
        if low != n and re.search(r"(?<![A-Za-z])" + re.escape(low) + r"(?![A-Za-z])", alltext):
            bad_brand.append(n)
    res["brands"] = names
    res["brand_lowercase_violations"] = bad_brand

    # 输出
    print(f"页集：de {res['de_pages']} / en {res['en_pages']}（已排除 matchups + vs 页）")
    print(f"bytes：de {bytes_de:,} / en {bytes_en:,}（差 {bytes_de - bytes_en:+,}）")
    print(f"正文可见字符：de {chars_de:,} / en {chars_en:,} → 比 {res['char_ratio']}")
    print(f"段：{res['paras_total']} 段，唯一 {res['paras_uniq']} "
          f"（{res['paras_uniq'] / max(1, res['paras_total']):.1%}）")
    print(f"句：{res['sents_total']} 句，唯一 {res['sents_uniq']} "
          f"（{res['sents_uniq'] / max(1, res['sents_total']):.1%}），重复句 {res['dupe_sentence_count']}")
    for s in res["dupe_sentences"]:
        print(f"    ↻ {s[:80]}")
    print(f"seo.description 逐页比对：{res['seo_checked']} 页，不一致 {len(seo_mismatch)} "
          f"{seo_mismatch if seo_mismatch else ''}")
    print("术语：" + " · ".join(f"{k}={v}" for k, v in terms.items()))
    print(f"品牌名小写变体违规：{len(bad_brand)} {bad_brand if bad_brand else ''}")
    print(f"CRLF 异常页：{[f['slug'] for f in res['files'] if f['crlf']]}")
    print(f"段数不对齐页：{[f['slug'] for f in res['files'] if f['paras_de'] != f['paras_en']]}")
    print(f"h2 数不对齐页：{[f['slug'] for f in res['files'] if f['h2_de'] != f['h2_en']]}")
    print(f"短代码不对齐页：{[f['slug'] for f in res['files'] if f['shortcodes_de'] != f['shortcodes_en']]}")
    print(f"缺 noindex 页：{[f['slug'] for f in res['files'] if not f['noindex']]}")

    if args.json:
        pathlib.Path(args.json).write_text(
            json.dumps(res, ensure_ascii=False, indent=1), encoding="utf-8")
        print(f"[json] {args.json}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
