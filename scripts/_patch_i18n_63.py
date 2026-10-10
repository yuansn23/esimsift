#!/usr/bin/env python3
# -*- coding: utf-8 -*-
r"""第六十三轮：把 23 处 `printf "英文字面串"` 全部 i18n 化（8 个模板文件）。

为什么必须做：这些串**绕过 i18n**，德语页原样印英文。已实测泄漏的：
  · head.html 的 title 候选串 → 德语子页 <title> = "Holafly Deutschland eSIM 2026: Unlimited Data Plans"
  · compare/single.html:220 → 50 个德语国家页的 JSON-LD name 含英文
  · compare/list.html:374 / networks/list.html:432 → 德语索引页 JSON-LD name
  · esim-providers/single.html 的 4 条 FAQ → 品牌 Hub 可见文本
  · vs-single.html:86/87 → 45 个德语 vs 页 CTA
守卫为什么没抓到：F 段是**黑名单**（8 个词、大小写敏感），"Unlimited Data Plans" 一个都不含；
且 F 段只扫可见文本，看不到 JSON-LD；check_i18n 不检测 `printf "字面串"` 形态。

★ 恒等保证：每条的 en.toml 值**逐字节等于被替换的模板原文**（脚本第 4 条断言强制）。
   故英语产物必须逐字节不变，德语侧才换成德语。

用 --dry 只跑断言；用 --selftest 注入反例证明「en 值 == 原文」这条断言没瞎。
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
EN = ROOT / "i18n" / "en.toml"
DE = ROOT / "i18n" / "de.toml"

# (key, 模板里被替换的原文, 德语)
T: list[tuple[str, str, str]] = [
    # ── JSON-LD name（4）────────────────────────────────────────────────
    ("compare_single__jsonld_itemlist_name",
     "Best %s eSIM plans ranked by cost per GB",
     "Beste eSIM-Tarife für %s nach Preis pro GB"),
    ("compare_list__jsonld_itemlist_name",
     "%d eSIM destinations",
     "%d eSIM-Reiseziele"),
    ("networks_list__jsonld_itemlist_name",
     "%s eSIM networks",
     "%s eSIM-Netze"),
    ("compare_provider__jsonld_product_name",
     "%s %s eSIM plans",
     "%s eSIM-Tarife für %s"),
    # ── 品牌 Hub FAQ 与档案（4）─────────────────────────────────────────
    ("esim_providers_single__faq_q_unlimited",
     "Does %s have unlimited data plans?",
     "Bietet %s unbegrenzte Datentarife?"),
    ("esim_providers_single__hq_tail",
     "%s, headquartered in %s",
     "%s mit Sitz in %s"),
    ("esim_providers_single__faq_q_hotspot",
     "Does %s support hotspot sharing?",
     "Unterstützt %s Hotspot-Freigabe?"),
    ("esim_providers_single__faq_q_5g",
     "Does %s support 5G?",
     "Unterstützt %s 5G?"),
    # ── vs 页（2 条 key / 3 处）─────────────────────────────────────────
    ("compare_vs_single__cta_view_plans",
     "View %s plans",
     "%s-Tarife ansehen"),
    ("compare_vs_single__faq_q_unlimited",
     "Does %s or %s offer unlimited data plans?",
     "Bieten %s oder %s unbegrenzte Datentarife?"),
    # ── _default 列表（1）──────────────────────────────────────────────
    ("default_list__guide_index",
     "%s — guide index",
     "%s — Ratgeber-Index"),
    # ── head.html 品牌×国家子页 title 候选串（11）───────────────────────
    ("partials_head__title_unl_1", "%s %s eSIM Review %d: Unlimited Data Plans",
     "%s %s eSIM-Test %d: Unbegrenzte Datentarife"),
    ("partials_head__title_unl_2", "%s %s eSIM %d: Unlimited Data Plans",
     "%s %s eSIM %d: Unbegrenzte Tarife"),
    ("partials_head__title_unl_3", "%s %s eSIM %d: Unlimited Plans Compared",
     "%s %s eSIM %d: Unbegrenzte Tarife im Vergleich"),
    ("partials_head__title_unl_4", "%s %s eSIM Review %d: Unlimited Plans",
     "%s %s eSIM-Test %d: Unbegrenzte Tarife"),
    ("partials_head__title_unl_5", "%s %s eSIM %d: Unlimited Data",
     "%s %s eSIM %d: Unbegrenzte Daten"),
    ("partials_head__title_unl_6", "%s %s eSIM %d: Unlimited Plans",
     "%s %s eSIM %d: Unbegrenzte Tarife"),
    ("partials_head__title_met_1", "%s %s eSIM Review %d: Data Plans Compared",
     "%s %s eSIM-Test %d: Datentarife im Vergleich"),
    ("partials_head__title_met_2", "%s %s eSIM %d: Cheap Data Plans Compared",
     "%s %s eSIM %d: Günstige Datentarife"),
    ("partials_head__title_met_3", "%s %s eSIM %d: Data Plans Compared",
     "%s %s eSIM %d: Datentarife im Vergleich"),
    ("partials_head__title_met_4", "%s %s eSIM %d: Prepaid Data Plans",
     "%s %s eSIM %d: Prepaid-Datentarife"),
    ("partials_head__title_met_5", "%s %s eSIM %d: Data Plans",
     "%s %s eSIM %d: Datentarife"),
]

# 模板改动：(相对路径, 旧片段, 新片段, 期望命中次数)
TPL: list[tuple[str, str, str, int]] = [
    ("layouts/compare/single.html",
     '"name" (printf "Best %s eSIM plans ranked by cost per GB" $country.name)',
     '"name" (printf (i18n "compare_single__jsonld_itemlist_name") $country.name)', 1),
    ("layouts/compare/list.html",
     '"name" (printf "%d eSIM destinations" $isoCount)',
     '"name" (printf (i18n "compare_list__jsonld_itemlist_name") $isoCount)', 1),
    ("layouts/networks/list.html",
     '"name" (printf "%s eSIM networks" .name) "url" (printf "%scompare/%s/" site.BaseURL .slug)',
     '"name" (printf (i18n "networks_list__jsonld_itemlist_name") .name) '
     '"url" (absURL (partial "lang-href.html" (printf "/compare/%s/" .slug)))', 1),
    ("layouts/compare/provider.html",
     '"name" (printf "%s %s eSIM plans" $p.name $country.name)',
     '"name" (printf (i18n "compare_provider__jsonld_product_name") $p.name $country.name)', 1),
    ("layouts/esim-providers/single.html",
     'printf "Does %s have unlimited data plans?" $p.name',
     'printf (i18n "esim_providers_single__faq_q_unlimited") $p.name', 1),
    ("layouts/esim-providers/single.html",
     'printf "%s, headquartered in %s" $a7 .',
     'printf (i18n "esim_providers_single__hq_tail") $a7 .', 1),
    ("layouts/esim-providers/single.html",
     'printf "Does %s support hotspot sharing?" $p.name',
     'printf (i18n "esim_providers_single__faq_q_hotspot") $p.name', 1),
    ("layouts/esim-providers/single.html",
     'printf "Does %s support 5G?" $p.name',
     'printf (i18n "esim_providers_single__faq_q_5g") $p.name', 1),
    ("layouts/compare/vs-single.html",
     '(printf "View %s plans" $na)', '(printf (i18n "compare_vs_single__cta_view_plans") $na)', 1),
    ("layouts/compare/vs-single.html",
     '(printf "View %s plans" $nb)', '(printf (i18n "compare_vs_single__cta_view_plans") $nb)', 1),
    ("layouts/compare/vs-single.html",
     '(printf "Does %s or %s offer unlimited data plans?" $na $nb)',
     '(printf (i18n "compare_vs_single__faq_q_unlimited") $na $nb)', 1),
    ("layouts/_default/list.html",
     '"name" (printf "%s — guide index" $.Title)',
     '"name" (printf (i18n "default_list__guide_index") $.Title)', 1),
]

# head.html 的 11 条：整块两个 slice(...)，逐条精确替换
HEAD_OLD = [
    '(printf "%s %s eSIM Review %d: Unlimited Data Plans" $p.name $c.name $y)',
    '(printf "%s %s eSIM %d: Unlimited Data Plans" $p.name $c.name $y)',
    '(printf "%s %s eSIM %d: Unlimited Plans Compared" $p.name $c.name $y)',
    '(printf "%s %s eSIM Review %d: Unlimited Plans" $p.name $c.name $y)',
    '(printf "%s %s eSIM %d: Unlimited Data" $p.name $c.name $y)',
    '(printf "%s %s eSIM %d: Unlimited Plans" $p.name $c.name $y)',
    '(printf "%s %s eSIM Review %d: Data Plans Compared" $p.name $c.name $y)',
    '(printf "%s %s eSIM %d: Cheap Data Plans Compared" $p.name $c.name $y)',
    '(printf "%s %s eSIM %d: Data Plans Compared" $p.name $c.name $y)',
    '(printf "%s %s eSIM %d: Prepaid Data Plans" $p.name $c.name $y)',
    '(printf "%s %s eSIM %d: Data Plans" $p.name $c.name $y)',
]
HEAD_NEW = [
    '(printf (i18n "partials_head__title_unl_1") $p.name $c.name $y)',
    '(printf (i18n "partials_head__title_unl_2") $p.name $c.name $y)',
    '(printf (i18n "partials_head__title_unl_3") $p.name $c.name $y)',
    '(printf (i18n "partials_head__title_unl_4") $p.name $c.name $y)',
    '(printf (i18n "partials_head__title_unl_5") $p.name $c.name $y)',
    '(printf (i18n "partials_head__title_unl_6") $p.name $c.name $y)',
    '(printf (i18n "partials_head__title_met_1") $p.name $c.name $y)',
    '(printf (i18n "partials_head__title_met_2") $p.name $c.name $y)',
    '(printf (i18n "partials_head__title_met_3") $p.name $c.name $y)',
    '(printf (i18n "partials_head__title_met_4") $p.name $c.name $y)',
    '(printf (i18n "partials_head__title_met_5") $p.name $c.name $y)',
]


def load(path: Path) -> dict[str, str]:
    out: dict[str, str] = {}
    for line in path.read_text(encoding="utf-8").splitlines():
        s = line.strip()
        if s and not s.startswith("#") and " = " in line:
            k, v = line.split(" = ", 1)
            out[k.strip()] = json.loads(v.strip())
    return out


def insert_group(text: str, key: str, value: str) -> tuple[str, str]:
    """把 key 插到同前缀组的最后一行之后；前缀组不存在则追加到文件末尾。"""
    prefix = key.rsplit("__", 1)[0] + "__"
    lines = text.split("\n")
    idx = [i for i, l in enumerate(lines) if l.startswith(prefix)]
    entry = f"{key} = {json.dumps(value, ensure_ascii=False)}"
    if idx:
        lines.insert(idx[-1] + 1, entry)
        return "\n".join(lines), "组内"
    # 退化：追加到末尾（default_list__ 是新前缀）
    while lines and lines[-1] == "":
        lines.pop()
    lines.append(entry)
    lines.append("")
    return "\n".join(lines), "追加末尾"


def literal_of(old: str) -> str | None:
    """从模板旧片段里抽出 printf 的字面串（第一处）。"""
    m = re.search(r'printf\s+"((?:[^"\\]|\\.)*)"', old)
    return m.group(1) if m else None


def key_of(new: str) -> str | None:
    m = re.search(r'i18n\s+"([^"]+)"', new)
    return m.group(1) if m else None


def eq_check(pairs, decl: dict[str, str]) -> list[str]:
    """核心恒等判据：每个新片段的 i18n key 必须在 T 中声明，且**声明的 en 值
    逐字节等于被替换掉的模板原文** —— 否则英语产物会变。

    用「声明表」而非「读 en.toml」是为了在写盘前也能判定（写盘后有回读复核兜底）。
    """
    errs: list[str] = []
    for rel, old, new in pairs:
        lit, k = literal_of(old), key_of(new)
        if lit is None or k is None:
            errs.append(f"{rel}: 片段形态异常 lit={lit!r} key={k!r}")
            continue
        if k not in decl:
            errs.append(f"{rel}: {k} 未在 T 中声明")
            continue
        if decl[k] != lit:
            errs.append(f"{rel}: {k} 声明的 en 值 {decl[k]!r} != 模板原文 {lit!r}")
    return errs


def all_pairs() -> list[tuple[str, str, str]]:
    return [(rel, old, new) for rel, old, new, _ in TPL] + [
        ("layouts/partials/head.html", o, n) for o, n in zip(HEAD_OLD, HEAD_NEW)
    ]


def selftest() -> int:
    """注入反例，证明「en 值 == 模板原文」这条判据真的会红。"""
    decl = {"compare_vs_single__cta_view_plans": "View %s plans"}
    good = ("x.html", '(printf "View %s plans" $na)',
            '(printf (i18n "compare_vs_single__cta_view_plans") $na)')
    cases = [
        ("A 正确配对 → 不报", [good], 0),
        ("B key 指向另一条 → 报", [("x.html", good[1],
                                 '(printf (i18n "compare_list__jsonld_itemlist_name") $na)')], 1),
        ("C key 未声明 → 报", [("x.html", good[1], '(printf (i18n "no__such_key") $na)')], 1),
        ("D 片段无 printf → 报", [("x.html", "$na", good[2])], 1),
        ("E 原文与声明差一个空格 → 报",
         [("x.html", '(printf "View %s plans " $na)', good[2])], 1),
    ]
    ok = 0
    for label, pairs, want in cases:
        got = 1 if eq_check(pairs, decl) else 0
        flag = "ok" if got == want else "!!"
        ok += got == want
        print(f"  [{flag}] {label}  期望报={want} 实报={got}")
    print(f"selftest: {ok}/{len(cases)} 项通过")
    return 0 if ok == len(cases) else 1


def main() -> int:
    dry = "--dry" in sys.argv
    en, de = load(EN), load(DE)
    if "--selftest" in sys.argv:
        return selftest()
    errs: list[str] = []

    # 断言 1：key 不能已存在
    for k, old, _ in T:
        if k in en:
            errs.append(f"{k} 已存在于 en.toml")
        if k in de:
            errs.append(f"{k} 已存在于 de.toml")
    # 断言 2：模板片段必须存在且命中预期次数
    for rel, old, new, want in TPL:
        p = ROOT / rel
        n = p.read_text(encoding="utf-8").count(old)
        if n != want:
            errs.append(f"{rel} 片段命中 {n} 次（期望 {want}）：{old[:60]}")
    hp = ROOT / "layouts/partials/head.html"
    ht = hp.read_text(encoding="utf-8")
    for old, new in zip(HEAD_OLD, HEAD_NEW):
        if ht.count(old) != 1:
            errs.append(f"head.html 片段命中 {ht.count(old)} 次（期望 1）：{old[:60]}")
    # 断言 3（核心）：en 值必须逐字节 == 模板原文（否则英语产物会变）
    errs += eq_check(all_pairs(), {k: old for k, old, _ in T})

    if errs:
        for e in errs:
            print(f"!! {e}")
        print(f"\n{len(errs)} 处问题，未写盘。")
        return 1
    print(f"断言全过：{len(T)} 个新 key 不冲突；{len(all_pairs())} 处模板片段各命中预期次数；")
    print(f"          en 值与模板原文逐字节一致（{len(T)} 条）—— 英语产物恒等。")
    if dry:
        print("--dry：未写盘。")
        return 0

    # 改 i18n
    en_txt = EN.read_bytes().decode("utf-8")
    de_txt = DE.read_bytes().decode("utf-8")
    if en_txt.count("\r\n") or de_txt.count("\r\n"):
        print("!! 前置就含 CRLF"); return 1
    where: dict[str, str] = {}
    for k, old, deval in T:
        en_txt, _w = insert_group(en_txt, k, old)
        de_txt, _w2 = insert_group(de_txt, k, deval)
    data_en = en_txt.encode("utf-8")
    data_de = de_txt.encode("utf-8")
    if b"\r\n" in data_en or b"\r\n" in data_de:
        print("!! 产物出现 CRLF"); return 1
    EN.write_bytes(data_en)
    DE.write_bytes(data_de)

    # 改模板
    changed = 0
    for rel, old, new, _ in TPL:
        p = ROOT / rel
        t = p.read_text(encoding="utf-8")
        t = t.replace(old, new)
        b = t.encode("utf-8")
        if b"\r\n" in b:
            print(f"!! {rel} 出现 CRLF"); return 1
        p.write_bytes(b)
        changed += 1
    ht = ht
    for old, new in zip(HEAD_OLD, HEAD_NEW):
        ht = ht.replace(old, new)
    hb = ht.encode("utf-8")
    if b"\r\n" in hb:
        print("!! head.html 出现 CRLF"); return 1
    hp.write_bytes(hb)
    changed += 1

    # 复核
    en2, de2 = load(EN), load(DE)
    miss_en = [k for k, _, _ in T if k not in en2]
    miss_de = [k for k, _, _ in T if k not in de2]
    bad_eq = [k for k, old, _ in T if en2.get(k) != old]
    print(f"OK 写入 {len(T)} 个 key（en.toml {len(data_en)} B / de.toml {len(data_de)} B）")
    print(f"   改了 {changed} 个模板文件")
    if miss_en or miss_de:
        print(f"!! 回读缺 key en={miss_en} de={miss_de}"); return 1
    if bad_eq:
        print(f"!! en 值 != 模板原文：{bad_eq}"); return 1
    print(f"   en 值与模板原文逐字节一致（{len(T)} 条）—— 英语产物应恒等")
    return 0


if __name__ == "__main__":
    sys.exit(main())
