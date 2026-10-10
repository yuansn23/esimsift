#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""第 9 批德语 i18n —— 只覆盖**德语站已经在线的页型**（第七十轮 d33 前）。

范围与依据（为什么是这些、不是研究页那 109 条）：
  `find public/de -name index.html` 实测德语站只有这几类页：
    · /de/compare/<国家>/（50 枢纽）  → i18n 组 `compare_single__*`
    · /de/compare/<国>/<品牌>/（499） → `compare_provider__*`
    · /de/esim-providers/<品牌>/（10）→ `esim_providers_single__*`
    · /de/networks/（1 列表页）      → `networks_list__*`
    · /de/、/de/esim-deals/、/de/tools/、法务页
  `/de/guides/*`、`/de/research/*`、`/de/networks/<slug>/` 的正文页**尚不存在**
  （只有各自 `_index.md`），所以它们的 109 + 43 条留到建页那一轮 —— 那几轮还要
  先把对应模板里的硬编码英文碎片 i18n 化，否则新页一上线就是半英文。

两类操作：
  · REPLACE：key 已存在、当前德语值逐字节等于英文值 → 原地替换（防覆盖已审校译文）
  · NEW    ：key 不存在 → 追加到 en.toml 与 de.toml **尾部同一位置**（顺序必须对齐）

四条断言（对两类都生效）：key 存在性 / 不覆盖已译值 / 占位符集合相等 / 德语不凭空多数字。

用法：
  python -X utf8 scripts/_patch_de_p9.py --selftest
  python -X utf8 scripts/_patch_de_p9.py --dry
  python -X utf8 scripts/_patch_de_p9.py
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
I18N = ROOT / "i18n"
RE_GO = re.compile(r"\{\{\s*\.\w+\s*\}\}")
RE_NUM = re.compile(r"\d+")

# ── 原地替换：key 已存在，当前德语值仍是英文 ────────────────────────────────
REPLACE: dict[str, str] = {
    # compare_single（国家枢纽页）—— 这些页德语站已经在线
    "compare_single__7_days": "7+ Tage",
    "compare_single__14_days": "14+ Tage",
    "compare_single__30_days": "30+ Tage",
    "compare_single__buy_before_you_fly": "Kaufe vor dem Abflug.",
    "compare_single__cheapest_price": "Günstigster Preis",
    "compare_single__install_on_wi_fi": "Installiere über WLAN.",
    "compare_single__land_and_it_just_works": "Landen und es läuft einfach.",
    "compare_single__longest_validity": "Längste Gültigkeit",
    "compare_single__sort_by": "Sortieren nach",
    "compare_single__plans_are_delivered_instantly_by_email_marketplace_provi":
        "Tarife werden sofort geliefert — per E-Mail (Marktplatz-Anbieter) oder in der App "
        "(App-Anbieter wie Roami und Saily).",
    "compare_single__scan_the_qr_code_or_tap_the_in_app_install_button_the_es":
        "Scanne den QR-Code oder tippe auf die Installationsschaltfläche in der App — "
        "das eSIM-Profil lädt in Sekunden.",
    "compare_single__works_on_esim_capable_phones_iphone_xs_and_newer_most_20":
        "Läuft auf eSIM-fähigen Telefonen (iPhone XS und neuer, die meisten "
        "Android-Flaggschiffe ab 2019). Deine physische SIM läuft daneben weiter.",
    # compare_provider（品牌×国家子页，499 页）—— 单位必须走德语写法
    "compare_provider__speed_mbps": "{{ .min }}–{{ .max }} Mbit/s",
    # esim_providers_single（品牌 Hub，10 页）
    "esim_providers_single__calc_unit_unl": "unbegrenzt",
    # networks_list（/de/networks/ 列表页）
    "networks_list__speed_band": "{{ .min }}–{{ .max }} Mbit/s",
}

# ── 新增：修复 tools 模板硬编码英文所必需的 key ──────────────────────────────
#   这些 key 不存在于任何语言文件；值必须让**英文侧产物逐字节不变** ——
#   所以前导/尾随空格、破折号、%d 位置都按模板原文逐字对齐。
NEW: dict[str, tuple[str, str]] = {
    "tools_list__video_calls_voip": ("Video calls (VoIP)", "Videotelefonie (VoIP)"),
    "tools_list__sd_video_streaming": ("SD video streaming", "SD-Video-Streaming"),
    "tools_list__hd_video_streaming": ("HD video streaming", "HD-Video-Streaming"),
    "tools_list__figcaption_live_from_n_tracked": (
        "From app hours to gigabytes to the cheapest real plan — "
        "computed live from %d tracked listings.",
        "Von App-Stunden über Gigabyte zum günstigsten echten Tarif — "
        "live aus %d erfassten Angeboten berechnet.",
    ),
    # ⚠ 下面两条**前导空格是文案的一部分**：模板里是 `{{ .mb }} MB/hour` 与 `> / day<`，
    #   换成 i18n 后空格必须还在值里，否则英文产物会少一个空格（空白也是字节）。
    "tools_list__per_day_suffix": (" / day", " / Tag"),
    "tools_list__mb_per_hour": (" MB/hour", " MB/Stunde"),
    "tools_list__hours": ("hours", "Stunden"),
    "tools_list__photos": ("photos", "Fotos"),
    "tools_list__countries_covered": ("countries covered", "Länder abgedeckt"),
    "tools_list__cheapest_in": ("cheapest in", "am günstigsten in"),
    "tools_list__from_is_the_cheapest_plan_any_provider_sells": (
        "“From” is the cheapest plan any provider sells in that country. "
        "All %d destinations are in the",
        "„Ab“ ist der günstigste Tarif, den irgendein Anbieter in diesem Land verkauft. "
        "Alle %d Reiseziele stehen im",
    ),
}


def load(p: Path) -> dict[str, str]:
    out: dict[str, str] = {}
    for line in p.read_text(encoding="utf-8").splitlines():
        s = line.strip()
        if s and not s.startswith("#") and " = " in line:
            k, v = line.split(" = ", 1)
            out[k.strip()] = json.loads(v.strip())
    return out


def audit(en: dict[str, str], de: dict[str, str]) -> list[str]:
    errs: list[str] = []
    for k, v in REPLACE.items():
        if k not in en:
            errs.append(f"[replace] {k} 不在 en.toml（拼错？）")
            continue
        if k not in de:
            errs.append(f"[replace] {k} 不在 de.toml")
            continue
        if de[k] != en[k]:
            errs.append(f"[replace] {k} 的德语值已不是英文占位（已审校？）拒绝覆盖：{de[k]!r}")
        a, b = set(RE_GO.findall(en[k])), set(RE_GO.findall(v))
        if a != b:
            errs.append(f"[replace] {k} 占位符不一致：en={sorted(a)} de={sorted(b)}")
        extra = set(RE_NUM.findall(v)) - set(RE_NUM.findall(en[k]))
        if extra:
            errs.append(f"[replace] {k} 德语凭空多出数字 {sorted(extra)}")
    for k, (e, d) in NEW.items():
        if k in en or k in de:
            errs.append(f"[new] {k} 已存在 —— 应改用 REPLACE，否则会写出第二份译文")
        a, b = set(RE_GO.findall(e)), set(RE_GO.findall(d))
        if a != b:
            errs.append(f"[new] {k} 占位符不一致：en={sorted(a)} de={sorted(b)}")
        if set(RE_NUM.findall(d)) - set(RE_NUM.findall(e)):
            errs.append(f"[new] {k} 德语凭空多出数字")
        # `%d` / `%s` 之类的格式符必须一一对应，否则 printf 会打印出 %!d(MISSING)
        if re.findall(r"%[-+ #0-9.]*[a-zA-Z%]", e) != re.findall(r"%[-+ #0-9.]*[a-zA-Z%]", d):
            errs.append(f"[new] {k} printf 格式符不匹配：{e!r} vs {d!r}")
    return errs


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

    global REPLACE, NEW
    keep_r, keep_n = REPLACE, NEW

    en = {"a": "7+ days", "b": "{{ .min }}–{{ .max }} Mbps", "c": "20% off"}
    de = dict(en)
    REPLACE, NEW = {"a": "7+ Tage", "b": "{{ .min }}–{{ .max }} Mbit/s"}, {}
    chk(not audit(en, de), "正例 A：普通替换 + 单位替换通过")

    REPLACE, NEW = {"c": "20 % Rabatt"}, {}
    chk(not audit(en, de), "正例 B：`20%` → `20 %` 写法差异不算多数字")

    REPLACE, NEW = {}, {"n1": ("From %d listings.", "Aus %d Angeboten.")}
    chk(not audit(en, de), "正例 C：新 key + printf 格式符一致通过")

    REPLACE, NEW = {"zz": "x"}, {}
    chk(bool(audit(en, de)), "反例 A：替换 key 不存在被抓住")

    REPLACE, NEW = {"b": "{{ .min }} Mbit/s"}, {}
    chk(bool(audit(en, de)), "反例 B：漏占位符被抓住")

    REPLACE, NEW = {"a": "7+ Tage (Frühbucher)"}, {}
    e2 = dict(en)                 # a = "7+ days"
    d2 = dict(de); d2["a"] = "7+ Tage"   # 已人工审校过的德语
    chk(bool(audit(e2, d2)), "反例 C：覆盖已译值被拒绝")

    REPLACE, NEW = {}, {"n2": ("From %d listings.", "Aus vielen Angeboten.")}
    chk(bool(audit(en, de)), "反例 D：新 key 的 %d 在德语里丢了被抓住")

    REPLACE, NEW = {}, {"a": ("x", "y")}
    chk(bool(audit(en, de)), "反例 E：新 key 与既有 key 撞名被抓住")

    REPLACE, NEW = keep_r, keep_n
    print(f"\nselftest: {ok} 通过 / {bad} 失败")
    raise SystemExit(1 if bad else 0)


if "--selftest" in sys.argv:
    selftest()

DRY = "--dry" in sys.argv
en_p, de_p = I18N / "en.toml", I18N / "de.toml"
en, de = load(en_p), load(de_p)
errs = audit(en, de)
if errs:
    print(f"!! {len(errs)} 项断言失败：")
    for e in errs[:40]:
        print("   " + e)
    raise SystemExit(1)

print(f"断言通过：替换 {len(REPLACE)} 条 + 新增 {len(NEW)} 条"
      f"（en 现有 {len(en)} key / de 现有 {len(de)} key）")
if DRY:
    raise SystemExit(0)

# ── 1. 追加新 key（两份文件尾部、同一顺序）────────────────────────────────
for p in (en_p, de_p):
    raw = p.read_bytes()
    txt = raw.decode("utf-8")
    add = ""
    for k, (e, d) in NEW.items():
        v = e if p is en_p else d
        add += f"{k} = {json.dumps(v, ensure_ascii=False)}\n"
    if raw.endswith(b"\n"):
        p.write_bytes(raw + add.encode("utf-8"))
    else:
        p.write_bytes(raw + b"\n" + add.encode("utf-8"))

# ── 2. 原地替换 —— **只动 de.toml**。en.toml 保持原英文值不变
#      （若把 REPLACE 一并写回 en.toml，就等于把英文站改成德语 —— 灾难性事故）
for p, table in ((de_p, REPLACE),):
    raw = p.read_bytes()
    crlf = raw.count(b"\r\n")
    text = raw.decode("utf-8")
    lines = text.split("\n")
    out: list[str] = []
    done: set[str] = set()
    for line in lines:
        m = re.match(r"^([A-Za-z0-9_]+) = ", line)
        if m and m.group(1) in table:
            k = m.group(1)
            out.append(f"{k} = {json.dumps(table[k], ensure_ascii=False)}")
            done.add(k)
        else:
            out.append(line)
    if done != set(table):
        raise SystemExit(f"ERROR: {p.name} 只替换了 {len(done)}/{len(table)}")
    p.write_bytes("\n".join(out).encode("utf-8"))
    assert p.read_bytes().count(b"\r\n") == crlf, f"{p.name} CRLF 被改变"

# en.toml 必须一个字节都没动（除了前面追加的新 key）—— 显式复核
assert load(en_p)["compare_single__7_days"] == "7+ days", "en.toml 被误写成德语！"

en2, de2 = load(en_p), load(de_p)
assert len(en2) == len(de2) == len(en) + len(NEW), "两侧 key 总数不一致"
assert list(en2) == list(de2), "两侧 key 顺序漂了"
assert list(en2)[-len(NEW):] == list(NEW), "新增 key 不在两侧尾部同一位置"

# ⚠ 不能直接复用 audit() 复查：它的 `[new]` 分支断言「key 不存在」，
#   写完之后必然报「已存在」—— 那是**写前**的不变式，写后用会把正确的写入判成失败。
#   写后要查的是三件事：英文侧未被污染、德语侧确实落盘、其余 key 原封不动。
for k, (e, d) in NEW.items():
    assert en2[k] == e, f"en.toml 的 {k} 值不对：{en2[k]!r}"
    assert de2[k] == d, f"de.toml 的 {k} 值不对：{de2[k]!r}"
for k, v in REPLACE.items():
    assert en2[k] == en[k], f"en.toml 的 {k} 被动了（英文侧必须原封不动）：{en2[k]!r}"
    assert de2[k] == v, f"de.toml 的 {k} 值不对：{de2[k]!r}"
assert {k: v for k, v in en2.items() if k not in NEW} == en, "en.toml 出现非预期改动"
assert {k: v for k, v in de2.items() if k not in NEW and k not in REPLACE} == \
       {k: v for k, v in de.items() if k not in NEW and k not in REPLACE}, "de.toml 出现非预期改动"
print(f"OK 替换 {len(REPLACE)} 条 + 新增 {len(NEW)} 条；"
      f"en/de 各 {len(en2)} key，顺序对齐，英文侧逐 key 未变")
