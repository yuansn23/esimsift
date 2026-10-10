#!/usr/bin/env python3
"""批 C 配套：`data/devices.toml` 数据层英文串的德语覆盖 + 模板接线。

背景（2026-10-10 d42 构建实测，EXIT=1）：
  `/de/guides/esim-compatibility-check/` 是本轮新建的德语页，它的设备总表由
  `data/devices.toml` 驱动 —— 六个文本字段（`source_note` / `name` / `family` /
  `since` / `note` / `blocked.{brand,model,why}`）**全是数据内建英文**，
  模板里 9 处裸渲染。F 判据只报了第一条命中的 `and`（它在每页首个命中就停），
  实际是**整张设备表在德语页上印英文**。

  ★ 这是 research 那次（第七十轮）的**同构缺陷**：新页型首次出现 ⇒
    旧判据的绿灯作废。`verify_de_text.py` 的 F 清单是**黑名单**（靠人想全），
    G 清单是「`strings.toml` 里已有德语译文的数据串」——devices 从未进表，
    所以 G 也看不见它。两条判据同时失效。

本脚本做两件事（都是行内、幂等）：
  ① `data/de/strings.toml` 追加 devices 的 **78 条** distinct 散文文本 + 1 条
     models 特例（`V29 Lite 5G (Europe only)`）= 79 条。
     ⚠ **不新建 `data/de/devices.toml`**：`i18n-data.html` 的 `merge` 对**数组整体
     替换**，`[[brand]]` 是数组 ⇒ 德语文件必须重抄 351 条机型名（专有名词），
     违反「一份事实只允许一份真源」。走既有 `strings.toml` 与
     `fup_note` / `promo_label` / `quirks` 完全同构。
  ② `layouts/guides/single.html` 9 处渲染点包 `de-text.html`。
     该 partial 语言无关：英语站没有 `data/en/` ⇒ `$d.strings` 为 nil ⇒
     恒等返回原串 ⇒ **英文产物逐字节不变**。

用法：python -X utf8 scripts/_patch_devices_de.py [--dry]
行尾：全 LF（本脚本写前先断言）。
"""
from __future__ import annotations

import argparse
import pathlib
import sys
import tomllib

ROOT = pathlib.Path(__file__).resolve().parents[1]

STRINGS = ROOT / "data" / "de" / "strings.toml"
TPL = ROOT / "layouts" / "guides" / "single.html"
DEVICES = ROOT / "data" / "devices.toml"

# ─────────────────────────────────────────────────────────────────────────────
# devices.toml 的德语译文（键 = 英文原文**逐字节**，值 = 德语）
# 分组顺序沿用数据文件：source_note → brand(name/family/since/note) → blocked
# 人称：全站 guides/networks/compare 一律 `du`（仅 research 栏目用 Sie）
# 单位：`GB` 不变；无 Mbps/Kbps（判据 I）
# 恒等条目（品牌名 / 机型串）照建 —— D 判据要求「数据里每个取值都有条目 +
# 表里无死条目」，恒等条目恰好是「品牌名改了措辞」的报警器。
# ─────────────────────────────────────────────────────────────────────────────
ENTRIES: list[tuple[str, str]] = [
    # ── 顶层 source_note（1）
    (
        "Compiled from manufacturer spec sheets, cross-checked against the compatibility lists "
        "published by major eSIM providers. Last reviewed October 2026.",
        "Zusammengestellt aus den Datenblättern der Hersteller und abgeglichen mit den "
        "Kompatibilitätslisten der großen eSIM-Anbieter. Letzte Prüfung im Oktober 2026.",
    ),
    # ── brand.name（14）
    ("Apple iPhone", "Apple iPhone"),
    ("Apple iPad", "Apple iPad"),
    ("Samsung Galaxy", "Samsung Galaxy"),
    ("Google Pixel", "Google Pixel"),
    ("Huawei", "Huawei"),
    ("Oppo", "Oppo"),
    ("Sony Xperia", "Sony Xperia"),
    ("Xiaomi", "Xiaomi"),
    ("Motorola", "Motorola"),
    ("Sharp AQUOS", "Sharp AQUOS"),
    ("Rakuten", "Rakuten"),
    ("Honor", "Honor"),
    ("vivo", "vivo"),
    ("Other brands", "Weitere Marken"),
    # ── brand.family（14）
    ("iPhone", "iPhone"),
    ("iPad (cellular models)", "iPad (Cellular-Modelle)"),
    ("Galaxy", "Galaxy"),
    ("Pixel", "Pixel"),
    ("P / Mate series", "P-/Mate-Serie"),
    ("Find / Reno", "Find / Reno"),
    ("Xperia", "Xperia"),
    ("Xiaomi / Redmi / Poco", "Xiaomi / Redmi / Poco"),
    ("Razr / Edge / Moto G", "Razr / Edge / Moto G"),
    ("AQUOS", "AQUOS"),
    ("Hand / Big / Mini", "Hand / Big / Mini"),
    ("Magic / numbered", "Magic / nummeriert"),
    ("X / V series", "X-/V-Serie"),
    ("OnePlus, Nokia, Nothing and more", "OnePlus, Nokia, Nothing und weitere"),
    # ── brand.since（14）
    ("iPhone XR and XS (2018)", "iPhone XR und XS (2018)"),
    ("cellular iPads", "Cellular-iPads"),
    ("Galaxy S20 / Z Flip (2020)", "Galaxy S20 / Z Flip (2020)"),
    ("Pixel 3 (2018)", "Pixel 3 (2018)"),
    ("P40 (2020)", "P40 (2020)"),
    ("Find X3 Pro (2021)", "Find X3 Pro (2021)"),
    ("Xperia 10 III (2021)", "Xperia 10 III (2021)"),
    ("Xiaomi 12T Pro (2022)", "Xiaomi 12T Pro (2022)"),
    ("Razr (2019)", "Razr (2019)"),
    ("AQUOS sense4 lite (2020)", "AQUOS sense4 lite (2020)"),
    ("Rakuten Hand (2020)", "Rakuten Hand (2020)"),
    ("Magic 4 Pro (2022)", "Magic 4 Pro (2022)"),
    ("X80 Pro (2022)", "X80 Pro (2022)"),
    ("misc. 2022+ models", "diverse Modelle ab 2022"),
    # ── brand.note（9 非空；空串不进表 —— 模板 `{{ with $b.note }}` 判空后不渲染）
    (
        "Chinese-mainland iPhones ship without eSIM. iPhone 14 and 15 bought in the US are "
        "eSIM-only (no physical SIM slot); the iPhone Air is eSIM-only worldwide and is the "
        "first iPhone that works with eSIM even in mainland China.",
        "iPhones für Festlandchina werden ohne eSIM ausgeliefert. In den USA gekaufte "
        "iPhone 14 und 15 sind eSIM-only (kein physischer SIM-Slot); das iPhone Air ist "
        "weltweit eSIM-only und das erste iPhone, das selbst in Festlandchina mit eSIM "
        "funktioniert.",
    ),
    (
        "Only cellular (Wi-Fi + Cellular) iPads carry an eSIM — Wi-Fi-only models do not.",
        "Nur Cellular-iPads (Wi-Fi + Cellular) haben eine eSIM — reine Wi-Fi-Modelle nicht.",
    ),
    (
        "The variant matters. US-bought S20 and S21 and the S20 FE have no eSIM; "
        "Hong Kong Samsungs do not either (Z Flip SM-F700F is the one exception); "
        "Korean-bought S20 to S22, Fold and Flip models lack eSIM. "
        "An international or European unit is the safe bet.",
        "Die Variante entscheidet. In den USA gekaufte S20 und S21 sowie das S20 FE haben "
        "keine eSIM; Samsung-Geräte aus Hongkong ebenfalls nicht (einzig das Z Flip "
        "SM-F700F ausgenommen); in Korea gekaufte S20 bis S22 sowie Fold- und Flip-Modelle "
        "haben keine eSIM. Ein internationales oder europäisches Gerät ist die sichere Wahl.",
    ),
    (
        "All Hong Kong Pixels lack eSIM. Pixel 3 units sold in Australia, Taiwan and Japan "
        "and Pixel 3a units from South-East Asia, Japan and Verizon are also excluded; "
        "Pixel 2 only on Google Fi.",
        "Alle Pixel aus Hongkong haben keine eSIM. Auch in Australien, Taiwan und Japan "
        "verkaufte Pixel-3-Geräte sowie Pixel-3a-Geräte aus Südostasien, Japan und von "
        "Verizon sind ausgenommen; das Pixel 2 nur bei Google Fi.",
    ),
    (
        "Only these models carry eSIM — the P40 Pro+ and P50 Pro do not. Huawei phones also "
        "ship without Google services, which blocks most travel-eSIM apps at setup.",
        "Nur diese Modelle haben eine eSIM — das P40 Pro+ und das P50 Pro nicht. "
        "Huawei-Geräte kommen zudem ohne Google-Dienste, was die Einrichtung der meisten "
        "Reise-eSIM-Apps blockiert.",
    ),
    (
        "Support is limited to international and Japanese variants — carrier-locked models "
        "often drop eSIM.",
        "Unterstützt werden nur internationale und japanische Varianten — bei "
        "carrier-gelockten Modellen fehlt die eSIM häufig.",
    ),
    (
        "Japanese domestic models — most relevant for eSIMs that list Japan coverage.",
        "Japanische Inlandsmodelle — vor allem relevant für eSIMs mit Japan-Abdeckung.",
    ),
    (
        "Japanese-market phones sold by Rakuten Mobile.",
        "Für den japanischen Markt bestimmte Geräte von Rakuten Mobile.",
    ),
    (
        "The V29 Lite 5G supports eSIM in Europe only.",
        "Das V29 Lite 5G unterstützt eSIM nur in Europa.",
    ),
    # ── blocked.brand（5；品牌名，德语同形）
    ("Apple", "Apple"),
    ("Samsung", "Samsung"),
    ("Google", "Google"),
    ("Huawei", "Huawei"),
    ("Xiaomi", "Xiaomi"),
    # ── blocked.model（12）
    ("iPhone X and older", "iPhone X und älter"),
    ("Chinese-mainland iPhones", "iPhones für Festlandchina"),
    ("Galaxy S10 and older", "Galaxy S10 und älter"),
    ("Galaxy S20 FE", "Galaxy S20 FE"),
    ("US-bought Galaxy S20 and S21", "In den USA gekaufte Galaxy S20 und S21"),
    ("Hong Kong Samsung models", "Samsung-Modelle aus Hongkong"),
    ("Korean-bought S20 to S22, Fold and Flip", "In Korea gekaufte S20 bis S22, Fold und Flip"),
    ("Hong Kong Pixels", "Pixel aus Hongkong"),
    ("Pixel 3 from Australia, Taiwan or Japan", "Pixel 3 aus Australien, Taiwan oder Japan"),
    (
        "Pixel 3a from South-East Asia, Japan or Verizon",
        "Pixel 3a aus Südostasien, Japan oder von Verizon",
    ),
    ("P40 Pro+ and P50 Pro", "P40 Pro+ und P50 Pro"),
    ("Xiaomi 12T (non-Pro)", "Xiaomi 12T (non-Pro)"),
    # ── blocked.why（11 distinct；`These variants lack eSIM.` 在数据里出现 2 次）
    (
        "No eSIM chip — the first eSIM iPhones are the XR and XS (2018).",
        "Kein eSIM-Chip — die ersten eSIM-iPhones sind XR und XS (2018).",
    ),
    ("Ship without eSIM (iPhone Air excepted).", "Werden ohne eSIM ausgeliefert (außer iPhone Air)."),
    ("eSIM arrived with the S20 generation.", "Die eSIM kam mit der S20-Generation."),
    ("No eSIM in any market.", "In keinem Markt mit eSIM."),
    ("US variants dropped the eSIM.", "US-Varianten haben die eSIM gestrichen."),
    (
        "No eSIM — the Z Flip SM-F700F is the one exception.",
        "Keine eSIM — einzig das Z Flip SM-F700F ausgenommen.",
    ),
    ("Korean variants lack eSIM.", "Koreanische Varianten haben keine eSIM."),
    ("Hong Kong units ship without eSIM.", "Geräte aus Hongkong werden ohne eSIM ausgeliefert."),
    ("These variants lack eSIM.", "Diese Varianten haben keine eSIM."),
    ("Listed without eSIM support.", "Ohne eSIM-Unterstützung gelistet."),
    ("Only the 12T Pro carries eSIM.", "Nur das 12T Pro hat eine eSIM."),
    # ── models 特例（1）：351 条机型名是**专有名词**、整体豁免；
    #    只有这条在括号里带了英文说明，单独进表（守卫侧对应 DEVICES_MODEL_OVERRIDES）
    ("V29 Lite 5G (Europe only)", "V29 Lite 5G (nur Europa)"),
]

# ─────────────────────────────────────────────────────────────────────────────
# `layouts/guides/single.html` 的 9 处渲染点：old → new（**整行内**替换，不新增行）
# ⚠ 只包可见文本；`data-tab` / `data-sec` / `data-b` / `data-s` 是搜索与控制键，
#   保持英文原值（德语用户搜 "apple" 仍应命中）。
# ⚠ `{{ . }}` 在 L144（note）与 L147（model）各出现一次 ⇒ 必须带上下文定位。
# ─────────────────────────────────────────────────────────────────────────────
TPL_EDITS: list[tuple[str, str]] = [
    # ① 品牌 tab 按钮
    (
        'hover:border-ink-400">{{ .name }} <span class="tnum opacity-60">{{ len .models }}</span></button>',
        'hover:border-ink-400">{{ partial "de-text.html" .name }} <span class="tnum opacity-60">{{ len .models }}</span></button>',
    ),
    # ② 品牌卡片 h3
    (
        '<h3 class="font-display text-base font-bold text-ink-900">{{ $b.name }}</h3>',
        '<h3 class="font-display text-base font-bold text-ink-900">{{ partial "de-text.html" $b.name }}</h3>',
    ),
    # ③ family（i18n 参数）+ since
    (
        '{{ i18n "guides_single__brand_meta" (dict "family" $b.family) | safeHTML }} {{ $b.since }}',
        '{{ i18n "guides_single__brand_meta" (dict "family" (partial "de-text.html" $b.family)) | safeHTML }} {{ partial "de-text.html" $b.since }}',
    ),
    # ④ 变体警示 note
    (
        '{{ i18n "guides_single__variant_watch" | safeHTML }}</span> {{ . }}</p>{{ end }}',
        '{{ i18n "guides_single__variant_watch" | safeHTML }}</span> {{ partial "de-text.html" . }}</p>{{ end }}',
    ),
    # ⑤ 机型名（`data-s` 搜索键保持 `$b.name` 原文）
    (
        'hover:bg-brand-50/40 hover:text-brand-800">{{ . }}</li>',
        'hover:bg-brand-50/40 hover:text-brand-800">{{ partial "de-text.html" . }}</li>',
    ),
    # ⑥⑦⑧ 不支持机型表三列
    (
        '<td class="font-medium text-ink-800">{{ .brand }}</td>',
        '<td class="font-medium text-ink-800">{{ partial "de-text.html" .brand }}</td>',
    ),
    (
        '<td>{{ .model }}</td>',
        '<td>{{ partial "de-text.html" .model }}</td>',
    ),
    (
        '<td class="text-sm text-ink-600">{{ .why }}</td>',
        '<td class="text-sm text-ink-600">{{ partial "de-text.html" .why }}</td>',
    ),
    # ⑨ 来源脚注
    (
        '<p class="mt-3 text-xs text-ink-400">{{ $d.devices.source_note }}</p>',
        '<p class="mt-3 text-xs text-ink-400">{{ partial "de-text.html" $d.devices.source_note }}</p>',
    ),
]

# strings.toml 头部注释：「覆盖四类」→「覆盖五类」
HEAD_OLD = "#   4. data/countries.toml[<ISO>].quirks —— 《#quirks》国家须知（101 条 / 50 国）\n"
# ⚠ HEAD_NEW **以 HEAD_OLD 为前缀** ⇒ 判「是否已应用」必须用 HEAD_OLD 里**没有**的
#   独立 marker，否则复跑时 `HEAD_OLD in raw` 恒真、注释块每跑一次膨胀一份。
HEAD_MARK = "#   5. data/devices.toml 的设备表文本字段"
HEAD_NEW = (
    "#   4. data/countries.toml[<ISO>].quirks —— 《#quirks》国家须知（101 条 / 50 国）\n"
    "#   5. data/devices.toml 的设备表文本字段 —— name / family / since / note /\n"
    "#      blocked.brand / blocked.model / blocked.why / source_note（78 条 distinct）\n"
    "#      + models 里带英文说明的 1 条（`V29 Lite 5G (Europe only)`）。\n"
    "#      ⚠ 351 条机型名是**专有名词**，整体不进表；渲染走 `de-text.html`，\n"
    "#        查得到就译、查不到原样返回。（2026-10-10 d42 构建实测：新页型\n"
    "#        `/de/guides/esim-compatibility-check/` 首次出现 ⇒ 整表印英文，\n"
    "#        F 是黑名单、G 只认「已进表的数据串」，两条同时失效。）\n"
)

TRAILER = (
    "\n"
    "# ── data/devices.toml（设备总表）────────────────────────────────────────────\n"
    "# 键 = 英文原文逐字节；值 = 德语。生成器：scripts/_patch_devices_de.py\n"
    "# 覆盖完整性由 verify_de_text.py 的判据 D 断言（缺键 = 红 / 死条目 = 红）。\n"
)


def device_texts() -> set[str]:
    """从数据文件复现「需要德语条目的设备文本」集合（含 models 特例）。"""
    d = tomllib.loads(DEVICES.read_bytes().decode("utf-8"))
    out: set[str] = set()
    sn = d.get("source_note")
    if isinstance(sn, str) and sn.strip():
        out.add(sn)
    for b in d.get("brand", []):
        for fld in ("name", "family", "since", "note"):
            v = b.get(fld)
            if isinstance(v, str) and v.strip():
                out.add(v)
    for bl in d.get("blocked", []):
        for fld in ("brand", "model", "why"):
            v = bl.get(fld)
            if isinstance(v, str) and v.strip():
                out.add(v)
    return out


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry", action="store_true")
    args = ap.parse_args()

    fails: list[str] = []

    # ── 前置：行尾必须是 LF ────────────────────────────────────────────────
    for p in (STRINGS, TPL, DEVICES):
        b = p.read_bytes()
        if b.count(b"\r\n"):
            fails.append(f"{p.relative_to(ROOT)} 含 CRLF —— 本脚本只处理 LF")
    if fails:
        print("\n".join("FAIL " + f for f in fails))
        return 1

    # ── 断言 1：ENTRIES 同名键的值必须一致（`Huawei`/`Xiaomi` 在 brand.name
    #            与 blocked.brand 各出现一次 —— 合法，落盘时去重）──────────────
    table: dict[str, str] = {}
    for k, v in ENTRIES:
        if k in table and table[k] != v:
            fails.append(f"ENTRIES 键冲突（值不同）: {k!r}")
        table[k] = v

    # ── 断言 2：ENTRIES 覆盖集合 == 数据里的设备文本集合 ────────────────────
    want = device_texts()
    want_all = want | {"V29 Lite 5G (Europe only)"}
    miss = want_all - set(table)
    extra = set(table) - want_all
    if miss:
        fails.append(f"ENTRIES 漏 {len(miss)} 条: {sorted(miss)[:5]}")
    if extra:
        fails.append(f"ENTRIES 多 {len(extra)} 条: {sorted(extra)[:5]}")
    if fails:
        print("\n".join("FAIL " + f for f in fails))
        return 1
    print(f"断言通过：ENTRIES {len(table)} 条 == 数据设备文本集合")

    # ── 断言 3：德语值不得含 F 判据禁词（防自造红） ─────────────────────────
    F_WORDS = ["Days", "days", "Day", "Local", "and", "plans", "countries", "every"]
    import re as _re

    for k, v in table.items():
        for w in F_WORDS:
            if _re.search(r"(?<![A-Za-zÀ-ÿ])%s(?![A-Za-zÀ-ÿ])" % _re.escape(w), v):
                fails.append(f"德语值含 F 禁词 {w!r}: {v[:70]!r}")
    if fails:
        print("\n".join("FAIL " + f for f in fails))
        return 1
    print(f"断言通过：{len(table)} 条德语值均不含 F 禁词")

    # ── 目标 1：strings.toml 追加 ─────────────────────────────────────────
    raw = STRINGS.read_bytes().decode("utf-8")
    before_lines = raw.count("\n")
    present = [k for k in table if f'"{k}" = ' in raw]
    todo = [(k, v) for k, v in table.items() if k not in present]

    # ⚠ HEAD_NEW 以 HEAD_OLD 为**前缀** ⇒ 不能用 `HEAD_OLD in raw` 判「已应用」
    #   （替换后 HEAD_OLD 仍在，复跑会无限膨胀注释块 —— 首次执行时实测 +616 B）。
    #   判据改用**独立 marker**：HEAD_NEW 里独有的那一行。
    if HEAD_MARK in raw:
        raw2 = raw  # 已应用
    elif HEAD_OLD in raw:
        raw2 = raw.replace(HEAD_OLD, HEAD_NEW, 1)
    else:
        fails.append("strings.toml 头部注释锚点未命中（HEAD_OLD / HEAD_MARK 都没有）")
        raw2 = raw

    if todo:
        add = TRAILER + "".join(
            '"%s" = "%s"\n' % (k.replace("\\", "\\\\").replace('"', '\\"'),
                               v.replace("\\", "\\\\").replace('"', '\\"'))
            for k, v in todo
        )
        if not raw2.endswith("\n"):
            raw2 += "\n"
        raw2 += add
    STRINGS_ADDED = len(todo)

    # ── 目标 2：模板 9 处替换 ─────────────────────────────────────────────
    tpl = TPL.read_bytes().decode("utf-8")
    tpl_before_lines = tpl.count("\n")
    tpl_todo = 0
    for old, new in TPL_EDITS:
        c = tpl.count(old)
        if c == 1:
            tpl = tpl.replace(old, new, 1)
            tpl_todo += 1
        elif c == 0 and new in tpl:
            pass  # 已应用
        else:
            fails.append(f"模板锚点命中 {c} 次（期望 1）: {old[:60]!r}")
    if tpl.count("\n") != tpl_before_lines:
        fails.append("模板行数变化（禁止：空白也是产物字节）")

    if fails:
        print("\n".join("FAIL " + f for f in fails))
        return 1

    print(f"计划：strings.toml 追加 {STRINGS_ADDED} 条 / 模板替换 {tpl_todo} 处")
    if args.dry:
        print("（--dry：未写盘）")
        return 0

    STRINGS.write_bytes(raw2.encode("utf-8"))
    TPL.write_bytes(tpl.encode("utf-8"))

    # ── 复核 ──────────────────────────────────────────────────────────────
    b1 = STRINGS.read_bytes()
    b2 = TPL.read_bytes()
    print(f"strings.toml: {before_lines} → {b1.count(b'\\n')} 行 / {len(b1)} bytes / CRLF={b1.count(b'\\r\\n')}")
    print(f"single.html : {tpl_before_lines} → {b2.count(b'\\n')} 行 / {len(b2)} bytes / CRLF={b2.count(b'\\r\\n')}")
    d = tomllib.loads(b1.decode("utf-8"))
    print(f"strings.toml 解析 OK：{len(d)} 条目")
    return 0


if __name__ == "__main__":
    sys.exit(main())
