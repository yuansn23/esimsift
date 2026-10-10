#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""把 de.toml 里残留的英制单位统一成德语写法（Mbps → Mbit/s、Kbps → Kbit/s）。

为什么需要：德语单位纪律是 `Mbit/s` / `Kbit/s`（见 `_gen_de_data.py` 的 `units()`），
`data/de/networkreports.toml` 已 56 处合规、`data/de/providers.toml` 已 14 处合规，
`data/de/strings.toml` 的 fup_note 也是 `Mbit/s`。**只有 i18n/de.toml 漏了 8 个值**，
于是德语页上出现「25 Mbps = 25 Mbit/s 混用」，且同一句里 `{{ .max }}`（数据层 Mbit/s 口径）
与字面 `Mbps` 并存 —— 实测 550 个德语页命中。

规则化做的（不手打德语）：只替换单位 token，其它字符逐字节不动。

断言：
  ① 只有 i18n/de.toml 被改；en.toml 一个字节不动
  ② 每个被改的 key：占位符集合不变、数字多重集合不变
  ③ 改完后 de.toml 里 Mbps/Kbps 出现次数为 0，Mbit/s 增量 == 原 Mbps 数
  ④ CRLF 数不变、key 总数不变、两侧 key 顺序仍一致

用法：python -X utf8 scripts/_fix_de_units.py [--dry]
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
EN, DE = ROOT / "i18n" / "en.toml", ROOT / "i18n" / "de.toml"
MAP = {"Mbps": "Mbit/s", "Kbps": "Kbit/s", "Gbps": "Gbit/s"}
RE_GO = re.compile(r"\{\{\s*\.\w+\s*\}\}")
RE_NUM = re.compile(r"\d+(?:[.,]\d+)?")


def load(p: Path) -> dict[str, str]:
    out = {}
    for line in p.read_text(encoding="utf-8").splitlines():
        s = line.strip()
        if s and not s.startswith("#") and " = " in line:
            k, v = line.split(" = ", 1)
            out[k.strip()] = json.loads(v.strip())
    return out


def selftest() -> None:
    ok = bad = 0

    def chk(c: bool, n: str) -> None:
        nonlocal ok, bad
        if c:
            ok += 1
            print(f"  [OK] {n}")
        else:
            bad += 1
            print(f"  [!!] {n}")

    chk(convert("rund 268,1 Mbps") == "rund 268,1 Mbit/s", "正例 A：Mbps → Mbit/s")
    chk(convert("Die Mbps-Spannen je Netz") == "Die Mbit/s-Spannen je Netz", "正例 B：复合词 Mbps-Spannen")
    chk(convert("512 Kbps Band") == "512 Kbit/s Band", "正例 C：Kbps → Kbit/s")
    chk(convert("{{ .min }}–{{ .max }} Mbps.") == "{{ .min }}–{{ .max }} Mbit/s.",
        "正例 D：占位符不动")
    chk(convert("schon Mbit/s") == "schon Mbit/s", "反例 A：已合规的值不变（幂等）")
    chk(convert("Mbpx 不是单位") == "Mbpx 不是单位", "反例 B：形近词不误伤")
    print(f"\nselftest: {ok} 通过 / {bad} 失败")
    raise SystemExit(1 if bad else 0)


def convert(v: str) -> str:
    for a, b in MAP.items():
        v = re.sub(r"(?<![A-Za-z])" + a + r"(?![A-Za-z])", b, v)
    return v


if "--selftest" in sys.argv:
    selftest()

DRY = "--dry" in sys.argv
en, de = load(EN), load(DE)
plan = {k: convert(v) for k, v in de.items() if convert(v) != v}

errs: list[str] = []
for k, new in plan.items():
    if set(RE_GO.findall(de[k])) != set(RE_GO.findall(new)):
        errs.append(f"{k} 占位符被改动")
    if sorted(RE_NUM.findall(de[k])) != sorted(RE_NUM.findall(new)):
        errs.append(f"{k} 数字被改动：{sorted(RE_NUM.findall(de[k]))} -> {sorted(RE_NUM.findall(new))}")
    if k not in en:
        errs.append(f"{k} 不在 en.toml")
if errs:
    print(f"!! {len(errs)} 项断言失败：")
    for e in errs:
        print("   " + e)
    raise SystemExit(1)

before_mbps = sum(v.count("Mbps") for v in de.values())
before_mbit = sum(v.count("Mbit/s") for v in de.values())
print(f"待改 {len(plan)} 个值；当前 de.toml 含 Mbps {before_mbps} 处 / Mbit/s {before_mbit} 处")
for k in plan:
    print(f"  {k}")
if DRY:
    raise SystemExit(0)
if not plan:
    print("无需改动（幂等）")
    raise SystemExit(0)

raw = DE.read_bytes()
crlf = raw.count(b"\r\n")
lines = raw.decode("utf-8").split("\n")
out: list[str] = []
done: set[str] = set()
for line in lines:
    m = re.match(r"^([A-Za-z0-9_]+) = ", line)
    if m and m.group(1) in plan:
        k = m.group(1)
        out.append(f"{k} = {json.dumps(plan[k], ensure_ascii=False)}")
        done.add(k)
    else:
        out.append(line)
assert done == set(plan), f"只替换了 {len(done)}/{len(plan)}"
DE.write_bytes("\n".join(out).encode("utf-8"))

de2 = load(DE)
assert DE.read_bytes().count(b"\r\n") == crlf, "CRLF 被改变"
assert len(de2) == len(de), "key 总数变了"
assert list(de2) == list(de), "key 顺序变了"
rest = [k for k, v in de2.items() if "Mbps" in v or "Kbps" in v]
assert not rest, f"仍有 {len(rest)} 个值含 Mbps/Kbps：{rest[:5]}"
for k in plan:
    assert de2[k] == plan[k]
assert {k: v for k, v in de2.items() if k not in plan} == {k: v for k, v in de.items() if k not in plan}, \
    "出现非预期改动"
after_mbit = sum(v.count("Mbit/s") for v in de2.values())
assert after_mbit == before_mbit + before_mbps - sum(v.count("Kbps") for v in de.values()), "Mbit/s 增量不符"
print(f"OK 改了 {len(plan)} 个值；de.toml 现在 Mbps 0 处 / Mbit/s {after_mbit} 处")
