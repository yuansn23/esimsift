#!/usr/bin/env python3
"""把 `data/providers.toml [<brand>.policy]` 的数据文本接到 `partial "de-text.html"`。

背景（2026-10-09 第六十四轮）：policy 下的 6 个文本字段
（fup_note / hotspot_note / topup_note / fup_allowance / fup_drop / hotspot_allowance，51 个取值）
**从来没有**德语条目，模板里也是裸插值 —— 于是德语品牌 Hub 与品牌子页的
「公平使用」「热点」「充值」三张政策卡、#fup 表、FAQ 答案、优缺点清单**整段印英文**，
而十一项闸门全绿（D 段只收集了 plans 的 fup_note，policy 从未被纳入）。

本脚本只做一件事：把 20 处渲染点接上 de-text.html。四条断言：
  ① 每对片段在目标文件里**恰好命中 1 次**（防止锚点漂移后改错地方）；
  ② 改后 `partial "de-text.html"` 的调用数 = 改前 + 本处新增数；
  ③ 改后**不再有**裸插值形态 `{{ .<field> }}`（六个字段全查）；
  ④ 改后**不再有** i18n dict 里的裸值 `"allowance" .` / `"drop" .`。

English 侧恒等：de-text.html 在英语站查表落空即原样返回，所以这 20 处对英文产物是 no-op。

用法：python -X utf8 scripts/_wire_policy_text.py [--dry] [--selftest]
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
L = ROOT / "layouts"

FIELDS = ("fup_allowance", "fup_drop", "fup_note", "hotspot_allowance", "hotspot_note", "topup_note")

# (文件, 改前片段, 改后片段)
EDITS: list[tuple[str, str, str]] = [
    # ── compare/provider.html（品牌×国家子页）─────────────────────────────
    (
        "compare/provider.html",
        '        <p class="mt-2 font-display text-lg font-bold text-ink-950">{{ .hotspot_allowance }}</p>\n'
        '        <p class="mt-2 text-sm leading-relaxed text-ink-500">{{ .hotspot_note }}</p>',
        '        <p class="mt-2 font-display text-lg font-bold text-ink-950">{{ partial "de-text.html" .hotspot_allowance }}</p>\n'
        '        <p class="mt-2 text-sm leading-relaxed text-ink-500">{{ partial "de-text.html" .hotspot_note }}</p>',
    ),
    (
        "compare/provider.html",
        '<p class="mt-2 text-sm leading-relaxed text-ink-500">{{ .topup_note }}</p>',
        '<p class="mt-2 text-sm leading-relaxed text-ink-500">{{ partial "de-text.html" .topup_note }}</p>',
    ),
    (  # #fit 清单：热点受限（在 `with .hotspot_allowance` 块内，`.` 即该字段）
        "compare/provider.html",
        '{{ i18n "compare_provider__fit_hotspot_block" (dict "allowance" .) | safeHTML }}',
        '{{ i18n "compare_provider__fit_hotspot_block" (dict "allowance" (partial "de-text.html" .)) | safeHTML }}',
    ),
    (  # #tradeoffs 优点：热点额度
        "compare/provider.html",
        '{{ $wins = $wins | append (i18n "compare_provider__tradeoffs_w_hotspot" (dict "allowance" .hotspot_allowance)) }}',
        '{{ $wins = $wins | append (i18n "compare_provider__tradeoffs_w_hotspot" (dict "allowance" (partial "de-text.html" .hotspot_allowance))) }}',
    ),
    (  # #tradeoffs 缺点：热点上限
        "compare/provider.html",
        '{{ $loses = $loses | append (i18n "compare_provider__tradeoffs_l_hotspot" (dict "allowance" .hotspot_allowance)) }}',
        '{{ $loses = $loses | append (i18n "compare_provider__tradeoffs_l_hotspot" (dict "allowance" (partial "de-text.html" .hotspot_allowance))) }}',
    ),
    (  # #tradeoffs 缺点：FUP 掉速 —— `drop` 是数据原文，必须过表
        "compare/provider.html",
        '{{ $loses = $loses | append (i18n "compare_provider__tradeoffs_l_fup_cap" (dict "allowance" $fupLabel "drop" .fup_drop)) }}',
        '{{ $loses = $loses | append (i18n "compare_provider__tradeoffs_l_fup_cap" (dict "allowance" $fupLabel "drop" (partial "de-text.html" .fup_drop))) }}',
    ),
    (
        "compare/provider.html",
        '{{ $loses = $loses | append (i18n "compare_provider__tradeoffs_l_fup_none" (dict "drop" .fup_drop)) }}',
        '{{ $loses = $loses | append (i18n "compare_provider__tradeoffs_l_fup_none" (dict "drop" (partial "de-text.html" .fup_drop))) }}',
    ),
    (  # FAQ 答案：内层 `with .fup_allowance` 的 `.`
        "compare/provider.html",
        '{{ $fupAns = i18n "compare_provider__faq_a_unlimited" (dict "brand" $p.name "country" $country.name "country_acc" ($country.name_acc | default $country.name) "country_dat" ($country.name_dat | default $country.name) "allowance" .) }}',
        '{{ $fupAns = i18n "compare_provider__faq_a_unlimited" (dict "brand" $p.name "country" $country.name "country_acc" ($country.name_acc | default $country.name) "country_dat" ($country.name_dat | default $country.name) "allowance" (partial "de-text.html" .)) }}',
    ),
    (
        "compare/provider.html",
        '{{ $hotspotAns = i18n "compare_provider__faq_a_hotspot" (dict "brand" $p.name "country" $country.name "country_acc" ($country.name_acc | default $country.name) "country_dat" ($country.name_dat | default $country.name) "allowance" .) }}',
        '{{ $hotspotAns = i18n "compare_provider__faq_a_hotspot" (dict "brand" $p.name "country" $country.name "country_acc" ($country.name_acc | default $country.name) "country_dat" ($country.name_dat | default $country.name) "allowance" (partial "de-text.html" .)) }}',
    ),
    # ── esim-providers/single.html（品牌 Hub）─────────────────────────────
    (
        "esim-providers/single.html",
        '"a" (i18n "esim_providers_single__faq_a_hotspot" (dict "brand" $p.name "allowance" $pol.hotspot_allowance))',
        '"a" (i18n "esim_providers_single__faq_a_hotspot" (dict "brand" $p.name "allowance" (partial "de-text.html" $pol.hotspot_allowance)))',
    ),
    (
        "esim-providers/single.html",
        '        <p class="mt-2 font-display text-lg font-bold text-ink-950">{{ .hotspot_allowance }}</p>\n'
        '        <p class="mt-2 text-sm leading-relaxed text-ink-500">{{ .hotspot_note }}</p>',
        '        <p class="mt-2 font-display text-lg font-bold text-ink-950">{{ partial "de-text.html" .hotspot_allowance }}</p>\n'
        '        <p class="mt-2 text-sm leading-relaxed text-ink-500">{{ partial "de-text.html" .hotspot_note }}</p>',
    ),
    (
        "esim-providers/single.html",
        '        <p class="mt-2 font-display text-lg font-bold text-ink-950">{{ .fup_allowance }}</p>\n'
        '        {{ with .fup_drop }}<p class="mt-1 text-xs font-semibold text-accent-700">{{ i18n "compare_provider__fup_drop_to" | safeHTML }} {{ . }}</p>{{ end }}\n'
        '        <p class="mt-2 text-sm leading-relaxed text-ink-500">{{ .fup_note }}</p>',
        '        <p class="mt-2 font-display text-lg font-bold text-ink-950">{{ partial "de-text.html" .fup_allowance }}</p>\n'
        '        {{ with .fup_drop }}<p class="mt-1 text-xs font-semibold text-accent-700">{{ i18n "compare_provider__fup_drop_to" | safeHTML }} {{ partial "de-text.html" . }}</p>{{ end }}\n'
        '        <p class="mt-2 text-sm leading-relaxed text-ink-500">{{ partial "de-text.html" .fup_note }}</p>',
    ),
    (
        "esim-providers/single.html",
        '<p class="mt-2 text-sm leading-relaxed text-ink-500">{{ .topup_note }}</p>',
        '<p class="mt-2 text-sm leading-relaxed text-ink-500">{{ partial "de-text.html" .topup_note }}</p>',
    ),
    # ── partials/faq-live-tokens.html（FAQ 池用 token）────────────────────
    (
        "partials/faq-live-tokens.html",
        '"unl_allowance" ($pol.fup_allowance | default $na)',
        '"unl_allowance" (partial "de-text.html" ($pol.fup_allowance | default $na))',
    ),
    (
        "partials/faq-live-tokens.html",
        '"unl_drop"      ($pol.fup_drop | default $na)',
        '"unl_drop"      (partial "de-text.html" ($pol.fup_drop | default $na))',
    ),
    # ── research/unlimited-esim.html（该页德语版尚未生成，先接线防漏）────
    (
        "research/unlimited-esim.html",
        '{{ with .fup }}{{ . | truncate 90 }}',
        '{{ with .fup }}{{ partial "de-text.html" . | truncate 90 }}',
    ),
]

BARE = re.compile(r"\{\{\s*\.(%s)\s*\}\}" % "|".join(FIELDS))
DANGLED = re.compile(r'"(allowance|drop)"\s+\.\s*\)')
F_IN = re.compile(r"\.(%s)\b" % "|".join(FIELDS))
F_ANY = re.compile(r"\b(%s)\b" % "|".join(FIELDS))


def wire(texts: dict[str, str], edits: list[tuple[str, str, str]]) -> tuple[dict[str, str], list[str], dict[str, int]]:
    """把 edits 逐条应用到 texts（纯函数，便于自测）。返回 (改后, 错误, 改前调用数)。"""
    errs: list[str] = []
    before: dict[str, int] = {}
    out: dict[str, str] = {}

    # 断言 ②：字段名守恒 —— 片段里被裸插值的 policy 字段，必须原样出现在替换后的 de-text 调用里。
    # 这条能抓住最危险的手误：把 fup_note 写成 topup_note（结构合法、数量对得上、静默印错内容）。
    for rel, old, new in edits:
        old_f = set(F_IN.findall(old))
        new_f = set(F_ANY.findall(new))
        if old_f != new_f:
            errs.append(
                f"{rel}: 字段名不守恒 —— 改前 {sorted(old_f) or '裸 .'} / 改后 {sorted(new_f) or '无'}"
                f" -> {old[:60]!r}"
            )
        if 'partial "de-text.html"' not in new:
            errs.append(f"{rel}: 替换后没有 de-text 调用 -> {new[:60]!r}")

    for rel, old, new in edits:
        src = out.get(rel, texts[rel])
        if rel not in before:
            before[rel] = src.count('partial "de-text.html"')
        n = src.count(old)
        if n != 1:
            errs.append(f"{rel}: 片段命中 {n} 次（应为 1）-> {old[:70]!r}")
            out[rel] = src
            continue
        out[rel] = src.replace(old, new, 1)

    for rel, txt in sorted(out.items()):
        hits = BARE.findall(txt)
        if hits:
            errs.append(f"{rel}: 仍有裸插值 {sorted(set(hits))}")
        hits = DANGLED.findall(txt)
        if hits:
            errs.append(f"{rel}: i18n dict 里仍有裸值 {sorted(set(hits))}")
    return out, errs, before


def selftest() -> int:
    """反例注入：证明四条断言都会红（否则「全绿」没有意义）。"""
    print("== selftest ==")
    ok = True
    base = {"t.html": 'A {{ .fup_note }} B'}

    def chk(cond: bool, label: str) -> None:
        nonlocal ok
        print(("  ok   " if cond else "  FAIL ") + label)
        if not cond:
            ok = False

    # 正例
    _o, e, _b = wire(base, [("t.html", "{{ .fup_note }}", '{{ partial "de-text.html" .fup_note }}')])
    chk(not e, "正例：正确接线零告警")

    # A 片段不存在（0 命中）
    _o, e, _b = wire(base, [("t.html", "{{ .nope }}", "x")])
    chk(any("命中 0 次" in x for x in e), "反例 A：片段不存在被抓住")

    # B 片段出现 2 次（锚点漂移）
    _o, e, _b = wire({"t.html": "{{ .fup_note }} {{ .fup_note }}"}, [("t.html", "{{ .fup_note }}", "x")])
    chk(any("命中 2 次" in x for x in e), "反例 B：片段出现 2 次被抓住")

    # C 改后仍留裸插值（改的是另一个字段）
    _o, e, _b = wire(
        {"t.html": "{{ .fup_note }} {{ .topup_note }}"},
        [("t.html", "{{ .fup_note }}", '{{ partial "de-text.html" .fup_note }}')],
    )
    chk(any("仍有裸插值" in x and "topup_note" in x for x in e), "反例 C：漏掉的裸插值被抓住")

    # D i18n dict 里的裸值没换（`"allowance" .` 结尾）
    _o, e, _b = wire({"t.html": '(i18n "k" (dict "allowance" .))'}, [("t.html", "X", "Y")])
    chk(any("i18n dict 里仍有裸值" in x for x in e), "反例 D：dict 裸值被抓住")

    # F 字段名被写错（结构合法、数量对得上，但内容印错）—— 最危险的一类手误
    _o, e, _b = wire(
        {"t.html": "{{ .fup_note }}"},
        [("t.html", "{{ .fup_note }}", '{{ partial "de-text.html" .topup_note }}')],
    )
    chk(any("字段名不守恒" in x for x in e), "反例 F：字段名被写错被抓住")

    # G 替换里没有 de-text 调用（等于没接线）
    _o, e, _b = wire({"t.html": "{{ .fup_note }}"}, [("t.html", "{{ .fup_note }}", "{{ .fup_note }}")])
    chk(any("没有 de-text 调用" in x for x in e), "反例 G：替换后未接线被抓住")

    print("== selftest 通过 ==" if ok else "== selftest 失败 ==")
    return 0 if ok else 1


def main(argv: list[str]) -> int:
    if "--selftest" in argv:
        return selftest()
    dry = "--dry" in argv

    texts = {rel: (L / rel).read_text(encoding="utf-8") for rel, _o, _n in EDITS}
    out, errs, before = wire(texts, EDITS)
    if errs:
        for e in errs:
            print("FAIL " + e)
        return 1

    print(f"断言通过：{len(EDITS)} 处片段各命中 1 次，改后裸插值 0 处、dict 裸值 0 处")
    if dry:
        print("--dry：未写盘")
        return 0

    for rel, txt in sorted(out.items()):
        b = txt.encode("utf-8")
        assert b.count(b"\r\n") == 0, f"{rel} 出现 CRLF"
        (L / rel).write_bytes(b)
        print(f"  {rel}: de-text 调用 {before[rel]} -> {txt.count('partial \"de-text.html\"')}")
    print(f"OK 写入 {len(out)} 个模板文件")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
