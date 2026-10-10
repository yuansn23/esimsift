#!/usr/bin/env python3
# -*- coding: utf-8 -*-
r"""第六十三轮：修 6 条「德语 h2/h3 含 , ; :」的 i18n 值。

起因：`check_headings.py`（产物级）在德语探针页上报 bad=8。
根因不是拼写，而是**德语从句必须用逗号**，而规则对 h2/h3 全语言禁 `, ; :`
（脚本注释明确：德语只放宽破折号，逗号/分号/冒号仍禁）。
英语原文一条都不含逗号（`Buy it if` / `Every head-to-head we track`）。

★ 修法：**换句式，不是删逗号**。德语 "Die zwei Marken, die X am nächsten kommen"
   去掉逗号就是语法错误；必须改成无从句的结构（"Die nächsten Rivalen von X"）。
★ 只改 de.toml，en.toml 一字不动 ⇒ 英语产物恒等。

用 --selftest 证明「禁标点」判据没瞎。
"""
from __future__ import annotations

import html
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
EN = ROOT / "i18n" / "en.toml"
DE = ROOT / "i18n" / "de.toml"

# (key, 新德语值) —— 全部无 , ; :
FIX: list[tuple[str, str]] = [
    ("compare_provider__fit_best", "Greif zu bei"),
    ("compare_provider__fit_skip", "Anderswo suchen bei"),
    ("compare_vs_single__every_head_to_head_we_track", "Alle erfassten Duelle"),
    ("esim_providers_single__reality_h2",
     "5G-Hotspot und Fair-Use-Regeln bei {{ .brand }}"),
    ("esim_providers_single__h2h_h2",
     "Die nächsten Rivalen von {{ .brand }}"),
    ("esim_providers_single__reading_h2",
     "Was vor dem Kauf von {{ .brand }} noch zählt"),
]

BAD = re.compile(r"[,;:]")
RE_GO = re.compile(r"\{\{.*?\}\}", re.S)
VARIANTS = {"{{ .country_acc }}": "{{ .country }}", "{{ .country_dat }}": "{{ .country }}"}
DE_ONLY = {"{{ .country_acc }}", "{{ .country_dat }}"}


def norm(tokens) -> tuple[str, ...]:
    return tuple(sorted(VARIANTS.get(t, t) for t in tokens))


def audit(pairs, en: dict[str, str]) -> list[str]:
    errs: list[str] = []
    for k, v in pairs:
        if k not in en:
            errs.append(f"{k} 不在 en.toml"); continue
        if BAD.search(html.unescape(re.sub(r"\{\{.*?\}\}", "", v))):
            errs.append(f"{k} 新值仍含 , ; : -> {v!r}")
        allow = set(RE_GO.findall(en[k]))
        if "{{ .country }}" in allow:
            allow |= DE_ONLY
        over = set(RE_GO.findall(v)) - allow
        if over:
            errs.append(f"{k} 凭空占位符 {sorted(over)}")
        if norm(RE_GO.findall(en[k])) != norm(RE_GO.findall(v)):
            errs.append(f"{k} 占位符多集不一致 en={norm(RE_GO.findall(en[k]))} de={norm(RE_GO.findall(v))}")
    return errs


def selftest(en: dict[str, str]) -> int:
    k = "compare_provider__fit_best"
    cases = [
        ("A 新值干净 → 不报", [(k, "Greif zu bei")], 0),
        ("B 新值仍带逗号 → 报", [(k, "Greif zu, bei")], 1),
        ("C 新值带冒号 → 报", [(k, "Greif zu: bei")], 1),
        ("D &amp; 实体的分号不算 → 不报", [("esim_providers_single__h2h_h2",
                                       "Rivalen &amp; Alternativen von {{ .brand }}")], 0),
    ]
    ok = 0
    for label, pairs, want in cases:
        got = 1 if audit(pairs, en) else 0
        flag = "ok" if got == want else "!!"
        ok += got == want
        print(f"  [{flag}] {label}  期望报={want} 实报={got}")
    print(f"selftest: {ok}/{len(cases)} 项通过")
    return 0 if ok == len(cases) else 1


def load(path: Path) -> dict[str, str]:
    out: dict[str, str] = {}
    for line in path.read_text(encoding="utf-8").splitlines():
        s = line.strip()
        if s and not s.startswith("#") and " = " in line:
            k, v = line.split(" = ", 1)
            out[k.strip()] = json.loads(v.strip())
    return out


def main() -> int:
    dry = "--dry" in sys.argv
    en = load(EN)
    if "--selftest" in sys.argv:
        return selftest(en)

    errs = audit(FIX, en)
    if errs:
        for e in errs:
            print(f"!! {e}")
        print(f"\n{len(errs)} 处问题，未写盘。")
        return 1
    print(f"断言全过（{len(FIX)} 条）：新值无 , ; :（&amp; 实体除外）/ 占位符与英文一致。")
    if dry:
        print("--dry：未写盘。")
        return 0

    raw = DE.read_bytes()
    text = raw.decode("utf-8")
    for k, v in FIX:
        pat = re.compile(r"(?m)^%s = .*$" % re.escape(k))
        if len(pat.findall(text)) != 1:
            print(f"!! {k} 未唯一命中"); return 1
        text = pat.sub(lambda _m, kk=k, vv=v: f"{kk} = {json.dumps(vv, ensure_ascii=False)}",
                       text, count=1)
    data = text.encode("utf-8")
    if b"\r\n" in data:
        print("!! 产物出现 CRLF"); return 1
    DE.write_bytes(data)
    print(f"OK 改写 {len(FIX)} 条德语（de.toml {len(raw)} -> {len(data)} B）")
    after = load(DE)
    bad = [k for k, v in FIX if after.get(k) != v]
    if bad:
        print(f"!! 回读不符：{bad}"); return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
