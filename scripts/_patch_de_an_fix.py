#!/usr/bin/env python3
# -*- coding: utf-8 -*-
r"""第六十三轮：修 2 条「德语句末可分动词前缀 an」的 i18n 值。

起因：`check_article_agreement.py`（英语冠词守卫，产物级）在德语探针页报
  "an Holafly"（应为 "a Holafly"）—— 纯属语言前提错位：
  · 德语 `Sieh dir das gesamte Bild für Deutschland an` 里 `an` 是**可分动词 ansehen
    的句末前缀**（框架结构），德语完全正确；
  · 但产物是 `…für Deutschland an` + 下一句 `Holafly verkauft…` 连排，
    守卫按英语读成 "an Holafly" ⇒ 判成冠词错。
  · 德语里 `an` 后面跟**品牌名/国名**才会触发（`Seite an Seite` 的 `Seite` 不在名词表里，不触发）。

修法：换掉句末 `an`，改成名词短语式小标题（德语更利落，也不给守卫留歧义）。
  同时把守卫的**产物级**检查限定为英语产物 —— 冠词是英语语法，德语页的英文残留
  由 verify_de_text.py 的 C 段（43 条禁词表）负责，分工不重叠。
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

FIX: list[tuple[str, str]] = [
    # 原：'Sieh dir das gesamte Bild für {{ .country_acc }} an'
    ("compare_provider__trust_h", "Das gesamte Bild für {{ .country_acc }}"),
    # 原：'Sieh dir die grenzüberschreitenden Gruppen an'
    ("networks_list__check_the_cross_border_groups", "Grenzüberschreitende Gruppen prüfen"),
]

BAD = re.compile(r"[,;:]")
RE_GO = re.compile(r"\{\{.*?\}\}", re.S)
VARIANTS = {"{{ .country_acc }}": "{{ .country }}", "{{ .country_dat }}": "{{ .country }}"}
DE_ONLY = {"{{ .country_acc }}", "{{ .country_dat }}"}
TRAILING_AN = re.compile(r"\ban\s*$")


def norm(tokens) -> tuple[str, ...]:
    return tuple(sorted(VARIANTS.get(t, t) for t in tokens))


def audit(pairs, en: dict[str, str]) -> list[str]:
    errs: list[str] = []
    for k, v in pairs:
        if k not in en:
            errs.append(f"{k} 不在 en.toml"); continue
        if TRAILING_AN.search(v):
            errs.append(f"{k} 仍以 an 结尾 -> {v!r}")
        if BAD.search(html.unescape(re.sub(r"\{\{.*?\}\}", "", v))):
            errs.append(f"{k} 含 , ; : -> {v!r}")
        allow = set(RE_GO.findall(en[k]))
        if "{{ .country }}" in allow:
            allow |= DE_ONLY
        over = set(RE_GO.findall(v)) - allow
        if over:
            errs.append(f"{k} 凭空占位符 {sorted(over)}")
        if norm(RE_GO.findall(en[k])) != norm(RE_GO.findall(v)):
            errs.append(f"{k} 占位符多集不一致")
    return errs


def selftest(en: dict[str, str]) -> int:
    k = "compare_provider__trust_h"
    old = "Sieh dir das gesamte Bild für {{ .country_acc }} an"
    new = "Das gesamte Bild für {{ .country_acc }}"
    cases = [
        ("A 新值 → 不报", [(k, new)], 0),
        ("B 旧值（句末 an）→ 报", [(k, old)], 1),
        ("C 带逗号 → 报", [(k, "Das Bild, für {{ .country_acc }}")], 1),
        ("D 凭空占位符 → 报", [(k, "Das Bild für {{ .bogus }}")], 1),
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
    print(f"断言全过（{len(FIX)} 条）：无句末 an / 无 , ; : / 占位符与英文一致。")
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
    after = load(DE)
    bad = [k for k, v in FIX if after.get(k) != v]
    if bad:
        print(f"!! 回读不符：{bad}"); return 1
    print(f"OK 改写 {len(FIX)} 条德语（de.toml {len(raw)} -> {len(data)} B）")
    return 0


if __name__ == "__main__":
    sys.exit(main())
