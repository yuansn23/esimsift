#!/usr/bin/env python3
"""数据层英文文案本地化守卫 —— layouts/partials/plan-name.html + layouts/partials/de-text.html

为什么需要它：`data/` 里有**内建的英文串**，它们不是模板文案，i18n 管不到：
  ① `data/plans/*.toml` 的 `name`（供应商原始产品名，9,095 条）与 `fup_note`（3,159 条 / 14 个取值）
  ② `data/providers.toml[<brand>].promo_label`（10 个取值）
  ③ `data/providers.toml[<brand>].info.support` / `.info.refund`（品牌档案事实陈述，20 个取值）
  ④ `data/countries.toml[<ISO>].quirks`（101 条国家须知）
这些串在德语页上原样渲染。模板写错、数据里冒出新的写法 —— 产物里只是「多一个英文词」，
构建不会失败，别的守卫也不认识这些字段。本脚本把「规则」用 Python 重实现一遍再对账。

判据（全部可证伪）：
  A 英文恒等  —— 套餐名词表在英语侧必须**就是源词**：同样的规则用 en 词表跑一遍必须逐字等于原串。
                 这是「英文产物逐字节不变」的充分条件。
  B 不误伤    —— 每条套餐名只能提到**本页目的地的国名**（9,095 条实测如此），
                 所以「国名 + Mobile」这种品牌名形态必须被识别（`Canada Mobile` / `Macao Mobile`）；
                 出现新的国家名 + Mobile → FAIL（提示人工确认）。
  C 不漏译    —— 德语套餐名里不得残留任何「英文名 ≠ 德语名」的国名，也不得残留别名表未覆盖的写法。
  D 覆盖完整  —— 数据里**每一个不同取值**的 `fup_note` / `promo_label` /
                 `info.support` / `info.refund` / `quirks` / **`devices.toml` 的六类
                 文本字段**（source_note / name / family / since / note / blocked.*）
                 都必须在 `data/de/strings.toml` 里有德语条目；表里也不许有死条目
                 （数据改了措辞而表没跟 → 当场红，而不是德语页静默印英文）。

  H policy 覆盖 —— `provider.policy` 的每个文本字段必须被 `data/de/providers.toml` 覆盖
                 （缺键 = 英文泄漏 / 值 == 英文 = 等于没译）。**policy 不走 strings.toml**：
                 模板读的是深合并后的 `$d.providers`，德语站拿到的本就是德语，
                 所以这条故障在 D / E4 / G 三条链上完全看不见。详见该函数 docstring。

产物侧（public/ 存在时）：
  E1 德语国家页的套餐名单元格不得含英文结构词（Days / Unlimited / Data / Local …）
  E2 德语国家页的套餐名单元格不得含「英文名 ≠ 德语名」的国名（Mobile 品牌形态例外）
  E3 英文国家页的套餐名单元格必须逐字 ∈ 原始名集合（恒等的产物级铁证）
  E4 德语国家页正文不得再出现 `fup_note` / `promo_label` 的英文原文
  E5 德语国家页**整页可见文本**不得出现英文结构词（Days/Day/Local/Plan/and）——
     这些词还会出现在散文里（FAQ 的套餐名 token、列表连接词），单元格扫描看不见

  F  全站德语页（`public/de/**/index.html`，不只 50 个国家页）不得出现
     「模板层硬编码英文」——见 F_FORBIDDEN_PHRASES / F_FORBIDDEN_WORDS 的注释。
     E1–E5 的盲区正是「页型」：它们只扫 `/de/compare/<国家>/`，
     而 `/de/research/`、`/de/networks/`、`/de/compare/` 索引页**完全没被覆盖**
     （2026-10-09 第六十三轮实测：`/de/research/` 一页有 9 句英文）。

  G  全站德语**文本产物**（HTML 页 + `llms.txt` / `catalog.json` / `*.xml`，**含 JSON-LD**）不得出现「**数据层**英文原文」——
     清单 = `english_data_texts()`（strings.toml 里已有德语译文的英文原串），**穷举**而非黑名单。
     ★ F 与 G 的分工：F 的清单靠人想全（且大小写敏感 —— `plans` 抓不到 `Plans`），
     G 的清单来自数据本身；**新增数据字段时不需要加黑名单**，只要译文进了表就会红。
     经验（第六十四轮）：`fup_allowance` / `hotspot_note` / `topup_note` 等 policy 字段
     从未进表、模板全是裸插值，德语页整段印英文，而 F 一条没报 —— 因为黑名单里
     「恰好」没有那些词。凡「某类问题已归零」都是断言，先问判据覆盖了哪些写法、哪些页型。
     ★ 第二次同构教训（第七十一轮 · devices 设备表）：**F 与 G 会同时失效**——
     G 的清单来自「已进表的数据串」，一个数据字段若从未进表，G 天然看不见它；
     而 F 只在黑名单命中时报。新页型首次渲染某类数据时，两条都还是绿的。
     ★ 第三次同构教训（第七十四轮 · 非 HTML 产物）：**G 的扫描面本身也会漏**——
     判据一直枚举 `**/index.html`，而 `/de/llms.txt`、`/de/catalog.json`、RSS XML
     同样是读者 / 爬虫 / AI 直接读的德语产物。实测这两处 10 条 promo_label +
     14 条 fup_note 全是英文原文而闸门全绿。「穷举清单」只解决了「清单要全」，
     没解决「产物要全」—— 问「判据覆盖了哪些页型」之外，还要问「覆盖了哪些产物」。

  J  全站德语页不得**裸印英文区域名**（`Asia` / `Europe` / `Americas` /
     `Africa & Middle East` / `Oceania`）—— 显示必须过 `partials/region-label.html`。
     为什么 F 装不下它：区域串既是字典键又是 `data-region` 值，键必须保持英文；
     而 F 是整页字面扫，收了 `Asia` 就会与真实套餐名 `Asia Pacific 40GB` 撞（假红）。
     J 因此按**文本节点**判断（节点 == 区域名，或以 ' ' + 区域名 结尾）——
     2026-10-09 d35 实测精确命中原有的 61 文件 / 155 处，零误伤。

用法：python -X utf8 scripts/verify_de_text.py [--selftest]
"""
from __future__ import annotations

import argparse
import html
import re
import sys
import tempfile
import tomllib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
I18N = ROOT / "i18n"
PUBLIC = ROOT / "public"

WORD_KEYS = [
    "plan_name__unlimited_data",
    "plan_name__unlimited",
    "plan_name__unlimited_caps",
    "plan_name__unlimited_lower",
    "plan_name__day_plan",
    "plan_name__days",
    "plan_name__days_lower",
    "plan_name__day",
    "plan_name__local",
]

# E5 的词表：德语国家页**整页可见文本**里不得以独立词形态出现的英文词。
#
# 为什么不能只看单元格（2026-10-09 第六十三轮）：套餐名还会出现在**散文**里 ——
#   FAQ 的 {cheap_plan} / {value_plan} / {ah_airalo_plan} token、计算器、卡片 ——
#   而 cells_of() 只覆盖 <td>/<strong>/<p class="mt-3 font-display …"> 三种。
#   盲区实测漏掉的样子（50 页共 71 处）：
#     `… 199MB / 1 Day von Yesim`、`… 60GB / 365 Days von Ubigi`、
#     `… Local Colombia - 7 Days - 1 GB von Nomad`、`… Japan and Südkorea …`、
#     `… Nomad Tag Plan -Südkorea …`
# 词表口径 =「只会以英文形态出现在套餐名 / 列表连接里」的词：
#   Day(s) / Local 是套餐名的结构词；`Plan` 是 Nomad 产品线里的结构词
#   （Day Plan）；`and` 是列表连接词（德语应为 und，走 faq_tokens__list_conjunction）。
# ⚠ 明确**不在**表内、且理由已记档：
#   · `unlimited` —— 德语页有意保留它作借词（实测 995 处），统一策略未定；
#   · `Data` / `Month` / `Week` —— 先量再定，不靠猜（猜错会造出假红）。
STRUCT_WORDS = ["Days", "days", "Day", "Local", "Plan", "and"]

# ── 判据 F：全站德语页的「模板层硬编码英文」清单 ────────────────────────────────
#
# 为什么要单开一条（2026-10-09 第六十三轮）：E1–E5 只扫 `/de/compare/<国家>/`，
# 于是**页型**成了盲区。实测 `public/de/` 55 个页面里，`/de/research/`（9 句）、
# `/de/compare/` 索引（整句 figcaption + 11 处未本地化套餐名）、`/de/networks/`
# （aside 的 `All 50 destinations →`）都在漏英文，而守卫全绿。
#
# 口径：**短语优先**（多词短语几乎不可能误报），单词表只收「德语里根本不存在
# 且不会被引用文本带进来」的词。每条都写明它是谁漏出来的 —— 源头修好后，
# 这里保留是**回归网**：同样的硬编码再回来，立刻变红。
F_FORBIDDEN_PHRASES = [
    # layouts/compare/list.html:115（figcaption）
    "real plans across",
    "one table per country",
    # layouts/partials/aside-destinations.html:45
    " destinations →",
    # layouts/compare/list.html:284（#matchups 卡片；德语 vs 页建好后会渲染）
    "starts cheaper in",
    "Nearly even across",
    "identical entry prices in",
    # layouts/research/list.html:52 / 61 / 70 / 99 / 103 / 118 / 119 / 133 / 137 / 141
    "unlimited plans audited",
    "prices checked",
    "cheapest unlimited",
    "vs priciest",
    "/GB avg",
    "countries · best ",
    "more in ",
    "than in ",
    "at each country's best rate",
    "Where you travel sets what you pay",
    "Right now",
    "the full league table ranks",
    "Best daily rate right now",
    "Daily-rate rankings",
    # layouts/esim-providers/list.html:28 / 52 / 55
    "Read the full",
    "countries · best $/GB in",
    "· from $",
]
#
# ⚠ 明确**不在**表内、理由已记档（否则就是造假红）：
#   · `May 2026` / `Mobile Network Experience Report` / `Consistent Quality` /
#     `Reliability` / `Ookla Global Index` —— Opensignal / Ookla 的**报告官方标识**，
#     是引文链接文本，有意逐字保留（见 docs/de-l10n-plan.md §12.14）；
#   · `unlimited` —— 德语页有意保留的借词（实测 995 处），统一策略未定；
#   · 品牌名 / 城市名 / `FAQ` / `JSON` —— 专有名词与通用缩写。
F_FORBIDDEN_WORDS = ["Days", "days", "Day", "Local", "and", "plans", "countries", "every"]
#   `plans` / `countries` / `every` 收进来的依据：德语页上它们**只**来自
#   research 那几句硬编码；修完后实测为 0（见本轮 55 页全量扫描）。
#   `Plan` 不收：`Plan` 是**德语词**（"ein Plan"），收了会造出假红 —— 这条
#   与 STRUCT_WORDS 的差异是刻意的：那一条只在套餐名语境（国家页）里成立。

# 已知的「国名 + Mobile」品牌形态（ISO）。新增即需人工确认，见判据 B。
KNOWN_MOBILE_BRANDS = {"CA", "MO"}

# 区域英文串（判据 J）。它们**同时是字典键与 data-region 值**（见
# layouts/partials/region-label.html 的说明），键必须保持英文，显示必须过转换。
REGION_EN = ("Asia", "Europe", "Americas", "Africa & Middle East", "Oceania")

problems: list[str] = []
infos: list[str] = []


def fail(msg: str) -> None:
    problems.append(msg)


def info(msg: str) -> None:
    infos.append(msg)


# --------------------------------------------------------------------------- 载入
def load_i18n(path: Path) -> dict:
    out = {}
    for line in path.read_text(encoding="utf-8").splitlines():
        if not line or line.startswith("#") or " = " not in line:
            continue
        k, v = line.split(" = ", 1)
        out[k.strip()] = tomllib.loads("x = " + v)["x"]
    return out


def load_names(path: Path) -> dict:
    txt = path.read_text(encoding="utf-8")
    out = {}
    for blk in re.split(r"\n(?=\[[A-Z]{2}\])", txt):
        m = re.match(r"\[([A-Z]{2})\]", blk)
        if not m:
            continue
        m2 = re.search(r'\nname\s*=\s*"([^"]+)"', blk)
        if m2:
            out[m.group(1)] = m2.group(1)
    return out


def load_plan_names() -> dict:
    """{iso: [(brand, name), …]}"""
    out: dict[str, list[tuple[str, str]]] = {}
    for f in sorted((DATA / "plans").glob("*.toml")):
        brand = f.stem
        cur = None
        for line in f.read_text(encoding="utf-8").splitlines():
            m = re.match(r"\[([A-Z]{2})\]", line.strip())
            if m:
                cur = m.group(1)
                continue
            m = re.match(r'\s*name\s*=\s*"(.*)"\s*$', line)
            if m and cur:
                out.setdefault(cur, []).append((brand, m.group(1)))
    return out


def load_fup_notes() -> dict:
    """{fup_note 英文原文: 出现次数}"""
    out: dict[str, int] = {}
    for f in sorted((DATA / "plans").glob("*.toml")):
        for line in f.read_text(encoding="utf-8").splitlines():
            m = re.match(r'\s*fup_note\s*=\s*"(.*)"\s*$', line)
            if m:
                out[m.group(1)] = out.get(m.group(1), 0) + 1
    return out


def load_promo_labels() -> set:
    d = tomllib.loads((DATA / "providers.toml").read_text(encoding="utf-8"))
    return {v["promo_label"] for v in d.values() if isinstance(v, dict) and v.get("promo_label")}


def load_quirks() -> set:
    """data/countries.toml[<ISO>].quirks 的全部英文原句（《#quirks》区块正文，走同一张 strings 表）"""
    d = tomllib.loads((DATA / "countries.toml").read_text(encoding="utf-8"))
    return {q for v in d.values() if isinstance(v, dict) for q in (v.get("quirks") or [])}


# `models` 里**唯一**需要在德语页本地化的一条（括号内是英文说明）。
# 351 条机型名是**专有名词**，整体不进 `strings.toml`；而这条若不进表，德语页会印
# `(Europe only)`，且 F 词表（Days/days/Day/Local/and/plans/countries/every）
# 看不见 `only` —— 属静默漏网。
DEVICES_MODEL_OVERRIDES = {"V29 Lite 5G (Europe only)"}


def load_device_texts() -> set[str]:
    """`data/devices.toml` 里需要德语条目的**散文类**文本字段值（含 models 覆盖项）。

    设备总表（`/guides/esim-compatibility-check/`）六个字段都是数据内建英文：
      · 顶层 `source_note`（来源脚注）
      · `[[brand]]` 的 `name` / `family` / `since` / `note`（面板标题、副标、支持起点、变体警示）
      · `[[blocked]]` 的 `brand` / `model` / `why`（不支持机型表三列）
    `models`（机型名）是专有名词、整体豁免，只有 `DEVICES_MODEL_OVERRIDES` 例外。

    ★ 为什么单开这一份（2026-10-10 d42 实测）：`/de/guides/esim-compatibility-check/`
      是本轮才建出的页型 —— 在此之前 devices 字段**没有任何德语页渲染**，
      所以 F（黑名单）与 G（只认「已进表的数据串」）同时为绿。页集一变，绿灯作废。
    """
    d = tomllib.loads((DATA / "devices.toml").read_text(encoding="utf-8"))
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
    # 覆盖项必须真的在数据里 —— 否则它就是另一种「死条目」
    all_models = {m for b in d.get("brand", []) for m in b.get("models", [])}
    missing = DEVICES_MODEL_OVERRIDES - all_models
    if missing:
        fail(f"D devices 覆盖项在数据里不存在（死条目）: {sorted(missing)}")
    return out | set(DEVICES_MODEL_OVERRIDES)


def load_info_strings() -> set:
    """data/providers.toml[<brand>].info 的 support / refund 全部英文原句。

    这两个字段**不在 i18n 里**（它们是品牌档案的事实陈述，跟价格一样属于数据），
    但会在德语页上渲染两处：`#info` 的渠道/退款条目，以及 `#faq` 的
    「<brand> offers <support>」答案句 —— 都走 de-text.html。
    （2026-10-09 第六十四轮补：这两处曾是 F 段实测抓到的裸英文。）
    """
    d = tomllib.loads((DATA / "providers.toml").read_text(encoding="utf-8"))
    out: set[str] = set()
    for v in d.values():
        if not isinstance(v, dict):
            continue
        i = v.get("info")
        if not isinstance(i, dict):
            continue
        for fld in ("support", "refund"):
            val = i.get(fld)
            if val:
                out.add(val)
    return out


class Ctx:
    def __init__(self):
        self._cache: dict = {}
        self._en_res: dict = {}
        self._alias_res: dict = {}
        self.en_words = load_i18n(I18N / "en.toml")
        self.de_words = load_i18n(I18N / "de.toml")
        self.en_names = load_names(DATA / "countries.toml")
        self.de_names = load_names(DATA / "de" / "countries.toml")
        self.aliases = tomllib.loads((DATA / "planaliases.toml").read_text(encoding="utf-8"))
        # 顶层即「英文原串 → 德文」映射：**不要再取 .get("strings")**，
        # 因为 hugo.Data.<lang>.strings 的值就是该文件内容本身（包一层就多一层，见文件头注释）。
        self.de_strings = tomllib.loads((DATA / "de" / "strings.toml").read_text(encoding="utf-8"))
        self.plans = load_plan_names()
        self.fup = load_fup_notes()
        self.promos = load_promo_labels()
        self.quirks = load_quirks()
        self.info = load_info_strings()
        self.devices = load_device_texts()
        for k in WORD_KEYS:
            if k not in self.en_words:
                fail(f"i18n/en.toml 缺 key {k}")
            if k not in self.de_words:
                fail(f"i18n/de.toml 缺 key {k}")

    # 词表顺序必须与模板一致：长词在前（Unlimited Data 先于 Unlimited）
    def word_pairs(self, lang: str):
        table = self.en_words if lang == "en" else self.de_words
        keys = sorted(WORD_KEYS, key=lambda k: -len(self.en_words.get(k, "")))
        return [(re.escape(self.en_words[k]), table[k]) for k in keys]

    def mobile_guard(self, name: str, iso: str) -> bool:
        en = self.en_names.get(iso, "")
        return bool(en and re.search(r"\b%s\b\s+Mobile" % re.escape(en), name))

    def localize(self, name: str, iso: str, lang: str) -> str:
        key = (name, iso, lang)
        if key in self._cache:
            return self._cache[key]
        n = name
        en = self.en_names.get(iso, "")
        loc = self.de_names.get(iso, "") if lang == "de" else en
        if en and loc and en != loc and not self.mobile_guard(name, iso):
            for al in (self.aliases.get(iso) or {}).get("aliases", []):
                n = self._alias_re(al).sub(loc, n)
            n = self._en_re(iso).sub(loc, n)
        for esc, val in self.word_pairs(lang):
            n = re.sub(r"\b%s\b" % esc, val.replace("\\", "\\\\"), n)
        self._cache[key] = n
        return n

    def _en_re(self, iso: str):
        if iso not in self._en_res:
            self._en_res[iso] = re.compile(r"(?i)\b%s\b" % re.escape(self.en_names.get(iso, "\x00")))
        return self._en_res[iso]

    def _alias_re(self, al: str):
        if al not in self._alias_res:
            self._alias_res[al] = re.compile(r"(?i)\b%s\b" % re.escape(al))
        return self._alias_res[al]

    def english_data_texts(self) -> list[str]:
        """数据里出现、且德语译文与英文不同的原串（这些不该再出现在德语页上）。"""
        out = []
        for v in set(self.fup) | self.promos | self.info | self.quirks | self.devices:
            if self.de_strings.get(v, v) != v:
                out.append(v)
        return sorted(out, key=len, reverse=True)

    def forbidden_country_tokens(self) -> set[str]:
        """英文名与德语名不同的国家 → 德语页上不该再出现这些英文名。"""
        out = {en for iso, en in self.en_names.items() if self.de_names.get(iso, en) != en and en}
        for iso, v in self.aliases.items():
            out.update(v.get("aliases", []))
        return out


# --------------------------------------------------------------------------- 源级
def check_source(ctx: Ctx) -> None:
    # A 英文恒等
    bad = 0
    for iso, rows in ctx.plans.items():
        for _brand, name in rows:
            if ctx.localize(name, iso, "en") != name:
                bad += 1
                if bad <= 3:
                    fail(f"A 英文不恒等: [{iso}] {name!r} → {ctx.localize(name, iso, 'en')!r}")
    if bad:
        fail(f"A 英文恒等失败 {bad} 条")
    else:
        info(f"A 英文恒等通过（{sum(len(v) for v in ctx.plans.values())} 条套餐名）")

    # B 国名只能是自己 + Mobile 品牌形态
    cross = 0
    unknown_mobile = set()
    pats = [
        (iso2, re.compile(r"(?i)\b%s\b" % re.escape(en2)), re.compile(r"(?i)\b%s\b\s+Mobile" % re.escape(en2)))
        for iso2, en2 in ctx.en_names.items()
        if en2
    ]
    for iso, rows in ctx.plans.items():
        for _brand, name in rows:
            for iso2, pat, mpat in pats:
                if iso2 == iso:
                    continue
                if pat.search(name):
                    if mpat.search(name):
                        unknown_mobile.add(iso2)
                        continue
                    cross += 1
                    if cross <= 3:
                        fail(f"B [{iso}] 套餐名提到别国 {ctx.en_names[iso2]!r}: {name!r}")
            if ctx.mobile_guard(name, iso) and iso not in KNOWN_MOBILE_BRANDS:
                unknown_mobile.add(iso)
    if cross:
        fail(f"B 跨页国名 {cross} 条（plan-name.html 只按本页 ISO 取替换目标，前提被破坏）")
    else:
        info("B 国名归属通过（无跨页国名）")
    if unknown_mobile:
        fail(
            "B 出现新的「国名 + Mobile」形态: "
            + ", ".join(sorted(unknown_mobile))
            + f" —— 已知仅 {sorted(KNOWN_MOBILE_BRANDS)}，请人工确认是否为品牌名"
        )
    else:
        info(f"B Mobile 品牌例外清单未扩张（已知 {sorted(KNOWN_MOBILE_BRANDS)}）")

    # C 德语结果不漏译
    forb = ctx.forbidden_country_tokens()
    leak = 0
    for iso, rows in ctx.plans.items():
        for _brand, name in rows:
            if ctx.mobile_guard(name, iso):
                continue
            out = ctx.localize(name, iso, "de")
            for tok in forb:
                if re.search(r"(?i)\b%s\b" % re.escape(tok), out):
                    leak += 1
                    if leak <= 5:
                        fail(f"C [{iso}] 德语结果残留英文国名 {tok!r}: {out!r}")
                    break
    if leak:
        fail(f"C 漏译 {leak} 条（补 data/planaliases.toml 或核对词表）")
    else:
        info(f"C 不漏译通过（禁词表 {len(forb)} 条）")

    # C' 别名表无死条目
    used = set()
    for iso, v in ctx.aliases.items():
        for al in v.get("aliases", []):
            if any(re.search(r"(?i)\b%s\b" % re.escape(al), n) for _b, n in ctx.plans.get(iso, [])):
                used.add(al)
            else:
                fail(f"C 别名死条目（数据里不存在）: [{iso}] {al!r}")
    if used:
        info(f"C 别名表 {len(used)} 条全部命中数据")


# --------------------------------------------------------------------------- 产物级
CELL_PATTERNS = [
    r'<td class="text-ink-700">(.*?)</td>',
    r'<strong class="text-ink-950">(.*?)</strong>',
    r'<p class="mt-3 font-display text-sm font-bold leading-snug text-ink-950">(.*?)</p>',
]


def visible(path: Path) -> str:
    t = path.read_text(encoding="utf-8")
    t = re.sub(r"<(script|style|svg|noscript)[\s\S]*?</\1>", " ", t, flags=re.I)
    t = re.sub(r"<[^>]+>", " ", t)
    t = html.unescape(t)
    return re.sub(r"\s+", " ", t)


def cells_of(path: Path) -> list[str]:
    t = path.read_text(encoding="utf-8")
    out = []
    for p in CELL_PATTERNS:
        for m in re.finditer(p, t):
            out.append(html.unescape(re.sub(r"<[^>]+>", "", m.group(1))).strip())
    return out


def check_products(ctx: Ctx, root: Path = PUBLIC) -> None:
    slugs = {}
    txt = (DATA / "countries.toml").read_text(encoding="utf-8")
    for blk in re.split(r"\n(?=\[[A-Z]{2}\])", txt):
        m = re.match(r"\[([A-Z]{2})\]", blk)
        if not m:
            continue
        m2 = re.search(r'\nslug\s*=\s*"([^"]+)"', blk)
        if m2:
            slugs[m2.group(1)] = m.group(1)

    en_words = [ctx.en_words[k] for k in WORD_KEYS]
    forb = ctx.forbidden_country_tokens()
    raw = {iso: {n for _b, n in rows} for iso, rows in ctx.plans.items()}
    n_de = n_en = 0

    for lang, label, prod in (("de", "德语", root / "de" / "compare"), ("en", "英语", root / "compare")):
        if not prod.exists():
            info(f"产物侧跳过（{prod} 不存在）")
            continue
        for d in sorted(prod.iterdir()):
            page = d / "index.html"
            if not page.exists():
                continue
            iso = slugs.get(d.name)
            if not iso:
                continue
            for cell in cells_of(page):
                if lang == "de":
                    n_de += 1
                    for w in en_words:
                        if re.search(r"\b%s\b" % re.escape(w), cell):
                            fail(f"E1 [{iso}] 德语页残留结构词 {w!r}: {cell!r}")
                            break
                    # 「国名 + Mobile」是品牌名（Canada Mobile / Macao Mobile），模板按设计跳过国名替换
                    if not ctx.mobile_guard(cell, iso):
                        for tok in forb:
                            if re.search(r"(?i)\b%s\b" % re.escape(tok), cell):
                                fail(f"E2 [{iso}] 德语页残留英文国名 {tok!r}: {cell!r}")
                                break
                else:
                    n_en += 1
                    if raw.get(iso) and cell not in raw[iso]:
                        fail(f"E3 [{iso}] 英语页套餐名不是原始串: {cell!r}")
            if lang == "de":
                text = visible(page)
                for v in ctx.english_data_texts():
                    if v in text:
                        fail(f"E4 [{iso}] 德语页残留英文数据串: {v!r}")
                # E5 整页扫描：散文里的套餐名 / 列表连接词（单元格判据的盲区）
                for w in STRUCT_WORDS:
                    m = re.search(r"(?<![A-Za-zÀ-ÿ])%s(?![A-Za-zÀ-ÿ])" % re.escape(w), text)
                    if m:
                        lo, hi = max(0, m.start() - 60), min(len(text), m.end() + 60)
                        fail(f"E5 [{iso}] 德语页残留英文结构词 {w!r}：…{text[lo:hi]}…")
    info(f"产物侧扫过 德语单元格 {n_de} / 英语单元格 {n_en}")


# --------------------------------------------------------------------------- 全站德语页
def check_de_pages(root: Path = PUBLIC) -> int:
    """判据 F：**每一个**德语页（`<root>/de/**/index.html`）的整页可见文本
    都不得含模板层硬编码英文（清单见 F_FORBIDDEN_PHRASES / F_FORBIDDEN_WORDS）。

    ★ 与 E 段的区别是**页型覆盖**，不是判据强度：E1–E5 只走 `/de/compare/<国家>/`，
      德语站现有的另外 5 类页（`/de/` 首页、`/de/compare/` 索引、`/de/guides/`、
      `/de/networks/`、`/de/research/`）此前一条判据都没管。新增页型时这条自动覆盖。
    """
    d = root / "de"
    if not d.exists():
        info(f"F 跳过（{d} 不存在）")
        return 0
    pages = sorted(d.glob("**/index.html"))
    n = 0
    for page in pages:
        text = visible(page)
        rel = page.relative_to(root).as_posix()
        for ph in F_FORBIDDEN_PHRASES:
            m = re.search(re.escape(ph), text)
            if m:
                n += 1
                lo, hi = max(0, m.start() - 60), min(len(text), m.end() + 60)
                fail(f"F [{rel}] 德语页残留英文短语 {ph!r}：…{text[lo:hi]}…")
        for w in F_FORBIDDEN_WORDS:
            m = re.search(r"(?<![A-Za-zÀ-ÿ])%s(?![A-Za-zÀ-ÿ])" % re.escape(w), text)
            if m:
                n += 1
                lo, hi = max(0, m.start() - 60), min(len(text), m.end() + 60)
                fail(f"F [{rel}] 德语页残留英文词 {w!r}：…{text[lo:hi]}…")
    if not n:
        info(
            f"F 全站德语页无硬编码英文（{len(pages)} 页 × 短语 {len(F_FORBIDDEN_PHRASES)} 条"
            f" + 词 {len(F_FORBIDDEN_WORDS)} 条）"
        )
    return n


# --------------------------------------------------------------------------- 区域名（判据 J）
_NODE_SS = re.compile(r"<(script|style|svg|noscript)[\s\S]*?</\1>", flags=re.I)
_NODE = re.compile(r">([^<]+)<")


def region_leaks(path: Path) -> list:
    """返回该页**文本节点**里裸印的英文区域名 [(区域, 节点), …]。

    ★ 为什么必须按**节点**判断，不能整页字面扫：真实套餐名里就存在
      `Asia Pacific 40GB` / `Southeast Asia 10GB`（d35 实测 singapore 页 39 处）——
      整页扫描会把 `Asia` 全部命中，一上线就是几十条假红。
      节点规则 = 「节点恰好等于区域名」或「节点以 ' ' + 区域名 结尾」，
      在 d35 产物上实测精确命中原有的 61 文件 / 155 处，零误伤。
    """
    body = _NODE_SS.sub(" ", path.read_text(encoding="utf-8"))
    out = []
    for m in _NODE.finditer(body):
        node = " ".join(html.unescape(m.group(1)).split())
        if not node:
            continue
        for r in REGION_EN:
            if node == r or node.endswith(" " + r):
                out.append((r, node))
                break
    return out


def check_region_labels(root: Path = PUBLIC) -> int:
    """判据 J：德语页不得裸印英文区域名（显示必须过 partials/region-label.html）。

    为什么单列一条：`Asia` / `Europe` / `Americas` / `Africa & Middle East` /
    `Oceania` 既是字典键又是前端过滤的 `data-region` 值，所以**键必须保持英文**；
    显示层转换只允许存在于 `region-label.html` 一处。漏掉转换时页面不报错、
    构建不失败、判据 F 也看不见（F 的单词表装不下 `Asia`，收了就会与套餐名
    `Asia Pacific` 撞）—— 2026-10-09 d35 实测 61 文件 / 155 处。
    """
    d = root / "de"
    if not d.exists():
        info(f"J 跳过（{d} 不存在）")
        return 0
    pages = sorted(d.glob("**/index.html"))
    n = 0
    for page in pages:
        for r, node in region_leaks(page):
            n += 1
            fail(f"J [{page.relative_to(root).as_posix()}] 德语页裸印英文区域名 {r!r}"
                 f"（节点 {node!r}）—— 显示必须过 partials/region-label.html")
    if not n:
        info(f"J 全站德语页无裸印英文区域名（{len(pages)} 页）")
    return n


# --------------------------------------------------------------------------- 数据串泄漏（全站·穷举）
def ldjson_text(path: Path) -> str:
    """页面里 JSON-LD 块的文本（`visible()` 会把 `<script>` 整段挖掉，结构化数据要看这里）。"""
    t = path.read_text(encoding="utf-8")
    out = " ".join(
        m.group(1)
        for m in re.finditer(
            r'<script[^>]*type="application/ld\+json"[^>]*>([\s\S]*?)</script>', t, flags=re.I
        )
    )
    return html.unescape(out)


DE_TEXT_SUFFIXES = (".txt", ".json", ".xml")


def _json_text(p: Path) -> str:
    """JSON 产物文本：Hugo `jsonify` 把 `<` `>` `&` 写成 `\\u003c` 等转义，不还原就漏判。"""
    t = p.read_text(encoding="utf-8", errors="replace")
    return re.sub(r"\\u([0-9a-fA-F]{4})", lambda m: chr(int(m.group(1), 16)), t)


def _leaks(text: str, strs: list[str]) -> list[str]:
    """返回 text 里出现的「数据层英文原文」（按 strs 顺序，每条至多计一次）。

    ⚠ 左边界必须查「前一个字符不是数字 / 小数点 / 逗号」：德语把小数点写成逗号，
      所以 `65,1 Mbps` 天然含子串 `1 Mbps`、`3,5 GB` 含 `5 GB`。不带这条边界，
      `/de/networks/` 的 Ookla 段落一次报出 7 条假红 —— 这正是
      「守卫变成噪音源 → 被优化掉 → 等于没有守卫」的典型路径。

      为什么手写 `str.find` 而不用正则：语义等价于逐串 `(?<![\\d.,])<串>`，但
      回溯型正则在 185 条串 × 3 MB 的 catalog.json 上要 33 s，`str.find` 只要 0.3 s；
      644 个德语 HTML 页 256 s → 8 s（这段原本占全量构建的四分之一）。
      换实现前已在 644 个页上与正则版**逐页比对命中集合**：完全一致。
    """
    out = []
    for s in strs:
        start = 0
        while True:
            i = text.find(s, start)
            if i < 0:
                break
            if i == 0 or text[i - 1] not in "0123456789.,":
                out.append(s)
                break
            start = i + 1
    return out


def check_data_leaks(ctx: Ctx, root: Path = PUBLIC, strs: list[str] | None = None) -> int:
    """判据 G：德语站的**每一个文本产物**（HTML 页 + 非 HTML）都不得出现「数据层英文原文」。

    清单 = `english_data_texts()`，即「strings.toml 里已有德语译文的英文原串」。
    与 F 的分工是这条判据最重要的一层经验：

      · **F 是黑名单** —— 23 条短语 + 8 个词，靠人「想全」，且大小写敏感。
        德语页 <title> 印着 `… Unlimited Data Plans` 而 F 无感，就因为清单里写的是
        小写 `plans`；`fup_allowance` 的 `3 GB/day on unlimited plans` 同理。
      · **G 是穷举** —— 清单来自数据本身。**新增一个数据字段不需要人来加黑名单**：
        只要它的德语译文进了表，它在德语页上出现就必红。
      · G 覆盖 JSON-LD：`check_output` 只管 JSON-LD 的**合法性**，
        `visible()` 又把 `<script>` 整段挖掉 —— 50 个德语国家页的
        `"name": "Best <Land> eSIM plans ranked by cost per GB"` 曾同时躲过两条判据。
      · G 也覆盖**非 HTML 产物**（第七十四轮扩）：`/de/llms.txt`、`/de/catalog.json`、
        RSS XML 同样是读者 / 爬虫 / AI 直接读的德语产物，而 `glob("**/index.html")`
        一条都覆盖不到。实测这两处 10 条 promo_label + 14 条 fup_note 全是英文原文。

    ⚠ **数字左边界**见 `_leaks()`：德语小数点写逗号，带不上这条边界立刻报出一堆假红。
    """
    d = root / "de"
    if not d.exists():
        info(f"G 跳过（{d} 不存在）")
        return 0
    strs = ctx.english_data_texts() if strs is None else strs
    if not strs:
        info("G 跳过（没有带德语译文的数据串）")
        return 0
    pages = sorted(d.glob("**/index.html"))
    files = sorted(f for f in d.rglob("*") if f.is_file() and f.suffix in DE_TEXT_SUFFIXES)
    n = 0
    for page in pages:
        text = visible(page) + " " + ldjson_text(page)
        for s in _leaks(text, strs):
            n += 1
            fail(f"G [{page.relative_to(root).as_posix()}] 德语页残留英文数据串: {s[:90]!r}")
    for f in files:
        text = _json_text(f) if f.suffix == ".json" else html.unescape(
            f.read_text(encoding="utf-8", errors="replace"))
        for s in _leaks(text, strs):
            n += 1
            fail(f"G [{f.relative_to(root).as_posix()}] 德语产物残留英文数据串: {s[:90]!r}")
    if not n:
        info(f"G 全站德语产物无数据层英文残留"
             f"（{len(pages)} 页 + {len(files)} 个非 HTML 文件 × {len(strs)} 条数据串，含 JSON-LD）")
    return n


# --------------------------------------------------------------------------- policy 覆盖（判据 H）
# `provider.policy` 的字段分两类，只允许存在一份德语来源：
#   · 文本字段（下表）→ 由 data/de/providers.toml **深度覆盖**提供德语，**不进 strings.toml**
#   · 枚举字段 → 判据读它们、i18n 出词，同样不进 strings.toml
POLICY_TEXT_FIELDS = (
    "fup_note",
    "hotspot_note",
    "topup_note",
    "fup_allowance",
    "fup_drop",
    "hotspot_allowance",
)
POLICY_ENUM_FIELDS = ("hotspot", "voice", "fup_kind")


def check_policy_coverage(ctx: Ctx, en: dict | None = None, de: dict | None = None) -> int:
    """判据 H：`provider.policy` 的**每一个文本字段**都必须被 `data/de/providers.toml` 覆盖。

    为什么单开一条：policy 字段**不走 de-text**（模板读的是深合并后的 `$d.providers`，
    德语站`$pol.fup_note` 拿到的本来就是德语），所以「德语页印英文」这一类故障在
    D / E4 / G 三条链上**完全看不见** —— 而 policy 恰恰是最容易漏的一类：
    它不在 i18n 里，`data/de/providers.toml` 少一个键，德语页就静默继承英文，
    所有闸门全绿。（2026-10-09 第六十四轮实测：我先在 strings.toml 里补了 51 条
    policy 译文，才发现德语覆盖层**早已 60/60 全覆盖** —— 那是同一事实的第二份译文，
    且两份口径已经不同：`Sie`/`du`、`Mbps`/`Mbit/s`。**发现重复要删一份，不是留两份。**）

    判据（品牌 × 非空文本字段）：
      · 德语覆盖层缺键         → 英文泄漏（模板继承英语侧）
      · 值 == 英文原文         → 等于没译（同一陷阱的另一种形态）
      · `policy` 下**除枚举白名单外的所有字符串字段**自动纳入 → 新增字段不会漏

    ⚠ 这里的字段清单是**判据侧的契约**，与 `_gen_de_strings.py` 无关（那张表只管
      fup_note / promo_label / info / quirks）。
    """
    en = tomllib.loads((DATA / "providers.toml").read_text(encoding="utf-8")) if en is None else en
    de = tomllib.loads((DATA / "de" / "providers.toml").read_text(encoding="utf-8")) if de is None else de
    bad = 0
    brands = 0
    fields: set[str] = set()
    for brand, v in en.items():
        p = v.get("policy") if isinstance(v, dict) else None
        if not isinstance(p, dict):
            continue
        hit = False
        dp = ((de.get(brand) or {}).get("policy") or {})
        for fld, val in p.items():
            if fld in POLICY_ENUM_FIELDS:
                continue
            if not isinstance(val, str) or not val.strip():
                continue
            hit = True
            fields.add(fld)
            dv = dp.get(fld)
            if not isinstance(dv, str) or not dv.strip():
                bad += 1
                fail(f"H [{brand}.policy.{fld}] 德语覆盖层缺键 —— 德语页会印英文: {val[:60]!r}")
            elif dv == val:
                bad += 1
                fail(f"H [{brand}.policy.{fld}] 德语覆盖层与英文同形（等于没译）: {val[:60]!r}")
        brands += 1 if hit else 0
    if not bad:
        miss = sorted(p for p in POLICY_TEXT_FIELDS if p not in fields)
        info(
            f"H policy 覆盖完整（{brands} 品牌 × {len(fields)} 个文本字段"
            + (f"；⚠ 契约列出但数据里没有的字段 {miss}" if miss else "")
            + "）"
        )
    return bad

# --------------------------------------------------------------------------- 德语单位（判据 I）
# 德语单位写法固定为 `Mbit/s` / `Kbit/s` / `Gbit/s`。
# 为什么单开一条：这不是「译没译」的问题，而是**同一条链上两种口径并存**——
# `data/de/networkreports.toml`（56 处）与 `data/de/providers.toml`（14 处）都已合规，
# 只有 `i18n/de.toml` 漏了 8 个值带着 `Mbps`，于是德语页出现「{{ .max }}（数据层 Mbit/s 口径）
# + 字面 Mbps」同句混用，实测命中 550 个德语页；而 F（黑名单）/ G（数据串穷举）都看不见它 ——
# `Mbps` 既不在 F 的词表里，也不是 `strings.toml` 里的英文原串。
# （第七十轮：`scripts/_fix_de_units.py` 规则化修好后补上这条判据，防回退。）
UNIT_BAD = ("Mbps", "Kbps", "Gbps")


def _unit_hits(values: dict, where: str) -> list[str]:
    out: list[str] = []
    for k, v in values.items():
        if not isinstance(v, str):
            continue
        for u in UNIT_BAD:
            if re.search(r"(?<![A-Za-z])" + u + r"(?![A-Za-z])", v):
                out.append(f"{where} {k}: {u} → 应为 {u[:-1]}it/s")
    return out


def _walk_strings(node, prefix: str, out: dict) -> None:
    """递归收集 TOML 里所有字符串叶子（policy 是「品牌 → 字段」两层，只走一层会漏）。"""
    if isinstance(node, str):
        out[prefix] = node
    elif isinstance(node, dict):
        for k, v in node.items():
            _walk_strings(v, f"{prefix}.{k}" if prefix else str(k), out)
    elif isinstance(node, list):
        for i, v in enumerate(node):
            _walk_strings(v, f"{prefix}[{i}]", out)


def check_de_units(i18n_de: dict | None = None, data_de: dict | None = None) -> int:
    """判据 I：德语侧（i18n 值 + data/de 所有字符串值）不得出现 Mbps/Kbps/Gbps。

    ⚠ 只看**解析后的值**，不看文件原文 —— `data/de/strings.toml` 的注释里就写着 `Mbps`
      （在解释历史口径），扫原文会立刻假红。
    """
    hits: list[str] = []
    if i18n_de is None:
        i18n_de = load_i18n(I18N / "de.toml")
    hits += _unit_hits(i18n_de, "i18n/de.toml")

    if data_de is None:
        data_de = {}
        for f in sorted((DATA / "de").glob("*.toml")):
            data_de[f.name] = tomllib.loads(f.read_text(encoding="utf-8"))
    flat: dict[str, str] = {}
    _walk_strings(data_de, "", flat)
    hits += _unit_hits(flat, "data/de")

    for h in hits:
        fail(f"I 德语单位不合规 —— {h}")
    if not hits:
        info(f"I 德语单位统一（i18n {len(i18n_de)} 值 + data/de {len(flat)} 字符串，无 Mbps/Kbps/Gbps）")
    return len(hits)


# --------------------------------------------------------------------------- 数据串覆盖
def check_strings(ctx: Ctx) -> None:
    """判据 D：数据层英文串必须有德语条目，且表里没有死条目。"""
    before = len(problems)
    have = set(ctx.fup) | ctx.promos | ctx.info | ctx.quirks | ctx.devices
    for v in sorted(have):
        if v not in ctx.de_strings:
            fail(f"D 数据串缺德语条目: {v!r}")
    for k in ctx.de_strings:
        if k not in have:
            fail(f"D 死条目（数据里不存在）: {k!r}")
    if len(problems) == before:
        info(
            f"D 数据串覆盖通过（fup_note {len(ctx.fup)} + promo_label {len(ctx.promos)}"
            f" + info.support/refund {len(ctx.info)} + quirks {len(ctx.quirks)}"
            f" + devices {len(ctx.devices)} = {len(have)} 条）"
        )


# --------------------------------------------------------------------------- 自测
def selftest(ctx: Ctx) -> int:
    global problems
    print("== selftest ==")
    ok = True

    def expect(cond, label):
        nonlocal ok
        print(("  ok   " if cond else "  FAIL ") + label)
        if not cond:
            ok = False

    # 规则本身
    expect(ctx.localize("50GB / 30 Days", "AT", "en") == "50GB / 30 Days", "en 恒等（Days）")
    expect(ctx.localize("Unlimited Data / 7 Days", "JP", "en") == "Unlimited Data / 7 Days", "en 恒等（Unlimited Data）")
    expect(
        ctx.localize("Austria eSIM Unlimited Data / 7 Days", "AT", "de")
        == "Österreich eSIM Unbegrenztes Datenvolumen / 7 Tage",
        "de 全量替换",
    )
    expect(ctx.localize("Czech Republic eSIM 5GB", "CZ", "de").startswith("Tschechien"), "别名 Czech Republic")
    expect(ctx.localize("Turkey 5GB", "TR", "de").startswith("Türkei"), "别名 Turkey")
    expect(ctx.localize("republic of ireland", "IE", "de") == "Irland", "别名 Republic of Ireland（小写）")
    expect(ctx.localize("Canada Mobile - 1 GB", "CA", "de") == "Canada Mobile - 1 GB", "Mobile 品牌名不被误译")
    expect(ctx.localize("Canada 20GB 30 days", "CA", "de") == "Kanada 20GB 30 Tage", "同页非品牌串仍译")
    expect(ctx.localize("Uki Mobile - 5 GB", "GB", "de") == "Uki Mobile - 5 GB", "UK 不误伤 Uki")

    # 数据串映射
    fup_en = "3 GB per day at full speed, then ∞ at 1Mbps"
    expect(ctx.de_strings.get(fup_en, "").startswith("3 GB pro Tag"), "D 德语映射命中（fup_note）")
    expect(
        ctx.de_strings.get("15% off unlimited-data plans", "") == "15 % Rabatt auf Unlimited-Tarife",
        "D 德语映射命中（promo_label）",
    )
    q0 = sorted(ctx.quirks)[0]
    expect(ctx.de_strings.get(q0, "") != q0, "D 德语映射命中（quirks）")

    # 判据 I：德语单位写法（Mbit/s，不是 Mbps）
    problems = []
    check_de_units(i18n_de={"a": "Band bis 25 Mbit/s"}, data_de={})
    expect(problems == [], "I 正例：Mbit/s 不报")
    problems = []
    check_de_units(i18n_de={"a": "Band bis 25 Mbps"}, data_de={})
    expect(any("Mbps" in p for p in problems), "I 反例：i18n 里的 Mbps 被抓住")
    problems = []
    check_de_units(i18n_de={}, data_de={"b": {"policy": "512 Kbps Drossel"}})
    expect(any("Kbps" in p for p in problems), "I 反例：data/de 嵌套值里的 Kbps 被抓住")
    problems = []
    check_de_units(i18n_de={"a": "Mbpx ist keine Einheit"}, data_de={})
    expect(problems == [], "I 反例边界：形近词 Mbpx 不误伤")
    problems = []

    # 判据 J：德语页裸印英文区域名（节点级）
    with tempfile.TemporaryDirectory() as td:
        troot = Path(td)
        (troot / "de" / "compare" / "at").mkdir(parents=True)
        (troot / "de" / "esim-providers" / "x").mkdir(parents=True)
        f = troot / "de" / "compare" / "at" / "index.html"

        f.write_text('<span class="badge">Europe</span>', encoding="utf-8")
        problems = []
        check_region_labels(troot)
        expect(any("裸印英文区域名 'Europe'" in p for p in problems),
               "J 反例：裸印的 `Europe` 被抓住")

        # 关键边界：套餐名里的区域词**不是**泄漏（整页字面扫会在这里造假红）
        f.write_text("<p>harmlos</p>", encoding="utf-8")   # 先清掉上一份夹具，否则会串味
        (troot / "de" / "esim-providers" / "x" / "index.html").write_text(
            '<td>Asia Pacific 40GB</td><td>Southeast Asia 10GB</td>', encoding="utf-8")
        problems = []
        check_region_labels(troot)
        expect(problems == [], "J 边界：套餐名 `Asia Pacific 40GB` 不误伤")

        # 句尾形式也要抓（阅读链接 `Beste eSIM für Asia`）
        f.write_text("<a>Beste eSIM für Asia</a>", encoding="utf-8")
        problems = []
        check_region_labels(troot)
        expect(any("'Asia'" in p for p in problems), "J 反例：句尾区域名被抓住")

        # 德语写法与 `&amp;` 转义写法都必须放过
        f.write_text("<span>Europa</span><span>Afrika &amp; Nahost</span>", encoding="utf-8")
        (troot / "de" / "esim-providers" / "x" / "index.html").write_text("<p>ok</p>", encoding="utf-8")
        problems = []
        check_region_labels(troot)
        expect(problems == [], "J 正例：德语区域名不报")
        problems = []

    save = problems
    problems = []
    keep = ctx.de_strings
    ctx.de_strings = {k: v for k, v in keep.items() if k != fup_en}
    check_strings(ctx)
    red = list(problems)
    problems = save
    expect(any("D 数据串缺德语条目" in p for p in red), "反例：数据串缺德语条目被抓住")
    problems = []
    ctx.de_strings = dict(keep)
    ctx.de_strings["Nichts dergleichen"] = "x"
    check_strings(ctx)
    red = list(problems)
    problems = save
    ctx.de_strings = keep
    expect(any("D 死条目" in p for p in red), "反例：死条目被抓住")
    q1 = sorted(ctx.quirks)[0]
    keep_q = ctx.quirks
    problems = []
    ctx.de_strings = {k: v for k, v in keep.items() if k != q1}
    ctx.quirks = {q1}
    check_strings(ctx)
    red = list(problems)
    problems = save
    ctx.de_strings = keep
    ctx.quirks = keep_q
    expect(any("D 数据串缺德语条目" in p for p in red), "反例：quirks 缺德语条目被抓住")

    # D 段第四来源（info.support / info.refund）—— 两个方向都要证伪，
    # 否则「扩了覆盖面」只是把 have 集合改大，判据有没有真的生效无从检验。
    i0 = sorted(ctx.info)[0]
    keep_i = ctx.info
    props = []
    problems = []
    ctx.de_strings = {k: v for k, v in keep.items() if k != i0}
    ctx.info = {i0}
    check_strings(ctx)
    props += list(problems)
    problems = []
    ctx.de_strings = dict(keep)
    ctx.de_strings["Etwas ganz anderes"] = "x"
    ctx.info = {i0}
    check_strings(ctx)
    props += list(problems)
    problems = save
    ctx.de_strings = keep
    ctx.info = keep_i
    expect(any("D 数据串缺德语条目" in p for p in props), "反例：info.support/refund 缺德语条目被抓住")
    expect(any("D 死条目" in p for p in props), "反例：info 死条目被抓住")

    # D 段第五来源（devices 设备表）—— 同样两个方向都要证伪。
    # 素材刻意取一条 **F 看不见**的（不含 F 词表任一词），否则 F 已经能抓，
    # 这条反例无法证明 D 的覆盖面真的扩大了。
    d0 = next(
        (
            s
            for s in sorted(ctx.devices)
            if len(s) > 24
            and not any(re.search(r"\b%s\b" % re.escape(w), s) for w in F_FORBIDDEN_WORDS)
        ),
        "",
    )
    expect(bool(d0), f"D devices 素材：找到一条 F 看不见的设备文本 {d0[:44]!r}")
    save_d = problems
    keep_d = ctx.devices
    props = []
    problems = []
    ctx.de_strings = {k: v for k, v in keep.items() if k != d0}
    ctx.devices = {d0}
    check_strings(ctx)
    props += list(problems)
    problems = []
    ctx.de_strings = dict(keep)
    ctx.de_strings["Etwas voellig anderes"] = "x"
    ctx.devices = {d0}
    check_strings(ctx)
    props += list(problems)
    problems = save_d
    ctx.de_strings = keep
    ctx.devices = keep_d
    expect(any("D 数据串缺德语条目" in p for p in props), "反例：devices 缺德语条目被抓住")
    expect(any("D 死条目" in p for p in props), "反例：devices 死条目被抓住")

    # H 反例：policy 覆盖层（德语侧唯一来源）—— 缺键 / 未译两个方向
    _en_h = {"x": {"policy": {"fup_drop": "1 Mbps", "voice": "data-only"}}}
    save = problems
    problems = []
    check_policy_coverage(ctx, en=_en_h, de={"x": {"policy": {}}})
    h1 = list(problems)
    problems = []
    check_policy_coverage(ctx, en=_en_h, de={"x": {"policy": {"fup_drop": "1 Mbps"}}})
    h2 = list(problems)
    problems = []
    check_policy_coverage(ctx, en=_en_h, de={"x": {"policy": {"fup_drop": "1 Mbit/s"}}})
    h3 = list(problems)
    problems = save
    expect(any("缺键" in p for p in h1), "反例：H 抓住德语覆盖层缺键")
    expect(any("同形" in p for p in h2), "反例：H 抓住德语覆盖层未译（值 == 英文）")
    expect(not h3, "正例：H 正确覆盖零告警")
    expect(not any("voice" in p for p in h1), "H 不把枚举字段（voice）当文本字段")

    # 反例注入：产物判据必须会红
    tmp = ROOT / ".selftest-plan-names"
    (tmp / "de" / "compare" / "austria").mkdir(parents=True, exist_ok=True)
    (tmp / "compare" / "austria").mkdir(parents=True, exist_ok=True)
    (tmp / "de" / "compare" / "austria" / "index.html").write_text(
        '<td class="text-ink-700">Austria eSIM 50GB / 30 Days</td><p>%s</p>' % fup_en, encoding="utf-8"
    )
    (tmp / "compare" / "austria" / "index.html").write_text(
        '<td class="text-ink-700">50GB / 30 Tage</td>', encoding="utf-8"
    )
    save = problems
    problems = []
    check_products(ctx, tmp)
    red = list(problems)
    problems = save
    expect(any("E1" in p for p in red), "反例：德语页英文结构词被抓住")
    expect(any("E2" in p for p in red), "反例：德语页英文国名被抓住")
    expect(any("E3" in p for p in red), "反例：英语页非原始串被抓住")
    expect(any("E4" in p for p in red), "反例：德语页英文数据串被抓住")

    # E5 反例：英文结构词出现在**散文**里 —— 单元格判据（E1）看不见这种形态
    (tmp / "de" / "compare" / "austria" / "index.html").write_text(
        '<p class="mt-3 text-ink-600">Günstigster Tarif: 199MB / 1 Day von Yesim.</p>'
        '<p class="mt-3 text-ink-600">Die Märkte ringsum – Deutschland and Schweiz gehören dazu.</p>',
        encoding="utf-8",
    )
    save = problems
    problems = []
    check_products(ctx, tmp)
    red = list(problems)
    problems = save
    expect(any("E5" in p and "'Day'" in p for p in red), "反例：散文里的英文结构词被抓住（Day）")
    expect(any("E5" in p and "'and'" in p for p in red), "反例：散文里的列表连接词被抓住（and）")
    expect(not any("E1" in p for p in red), "E5 反例确实绕过了单元格判据（E1 未红）")

    (tmp / "de" / "compare" / "austria" / "index.html").write_text(
        '<td class="text-ink-700">Österreich eSIM 50GB / 30 Tage</td>'
        '<p class="mt-3 text-ink-600">Günstigster Tarif: 199MB / 1 Tag von Yesim.</p>'
        '<p class="mt-3 text-ink-600">Die Märkte ringsum – Deutschland und Schweiz gehören dazu.</p>',
        encoding="utf-8",
    )
    (tmp / "compare" / "austria" / "index.html").write_text(
        '<td class="text-ink-700">Austria eSIM 50GB / 30 Days</td>', encoding="utf-8"
    )
    save = problems
    problems = []
    check_products(ctx, tmp)
    red = list(problems)
    problems = save
    expect(not red, "正例：正确产物零告警")

    import shutil

    # ── 判据 F 反例（2026-10-09 第六十三轮）──────────────────────────────────
    # 反例必须同时证明两件事：① 模板层硬编码英文会被抓住；② **有意保留**的英文
    # 不会被误伤（Opensignal 报告标识 / `unlimited` 借词 / 德语词 `Plan`）。
    # 只证 ① 会把守卫做成噪音源 —— 那时它会被「优化掉」，等于没有守卫。
    tmpf = ROOT / ".selftest-de-pages"
    (tmpf / "de" / "research").mkdir(parents=True, exist_ok=True)
    (tmpf / "de" / "networks").mkdir(parents=True, exist_ok=True)
    (tmpf / "de" / "research" / "index.html").write_text(
        "<p>9095 real plans across 50 destinations — one table per country.</p>"
        "<p>prices checked 30.09.2026 · 4602 unlimited plans audited with every fair-use cap.</p>"
        "<p>18 countries · best Frankreich at $0.30/GB</p>"
        "<p>Quelle: Australia, May 2026, Mobile Network Experience Report · "
        "Zuverlässigkeit (Reliability) · Unlimited-Tarife · ein Plan deckt die Reise ab.</p>",
        encoding="utf-8",
    )
    (tmpf / "de" / "networks" / "index.html").write_text(
        '<p>All 50 destinations →</p>', encoding="utf-8"
    )
    save = problems
    problems = []
    check_de_pages(tmpf)
    red = list(problems)
    problems = save
    # ⚠ 断言只能看「被判定的词」那一段，不能看整条消息：消息里带 ±60 字上下文，
    #   相邻段落的 `May 2026` 会被卷进来 → 「不误伤」这类断言会假红（本轮踩过）。
    reason = [m.split("：", 1)[0] for m in red]
    expect(any("real plans across" in p for p in reason), "反例：F 抓住硬编码英文短语")
    expect(any("'countries'" in p for p in reason), "反例：F 抓住硬编码英文词")
    expect(any("destinations →" in p for p in reason), "反例：F 抓住 aside 的英文链接")
    expect(not any("'May" in p for p in reason), "F 不误伤 Opensignal 报告标识（有意保留）")
    expect(not any("'unlimited'" in p for p in reason), "F 不误伤 unlimited 借词")
    expect(not any("'Plan'" in p for p in reason), "F 不误伤德语词 Plan")
    # 正例：全德语（含有意保留的英文标识）→ 零告警
    (tmpf / "de" / "research" / "index.html").write_text(
        "<p>Alle 50 Reiseziele →</p><p>Preise geprüft am 30.09.2026. "
        "Quelle: Australia, May 2026, Mobile Network Experience Report</p>",
        encoding="utf-8",
    )
    (tmpf / "de" / "networks" / "index.html").write_text(
        "<p>Ein Plan deckt die ganze Reise ab.</p>", encoding="utf-8"
    )
    save = problems
    problems = []
    check_de_pages(tmpf)
    red = list(problems)
    problems = save
    expect(not red, "正例：全站德语页正确产物零告警")

    # ── 判据 G 反例（2026-10-09 第六十四轮）──────────────────────────────────
    # 「G 补的是 F 的盲区」这句话必须先证明：素材得是一条**F 段看不见**的数据串
    # （不含黑名单词、不含黑名单短语）。否则 G 只是 F 的副本，白加一条判据。
    leak = next(
        (
            s
            for s in ctx.english_data_texts()
            if not any(re.search(r"\b%s\b" % re.escape(w), s) for w in F_FORBIDDEN_WORDS)
            and not any(p in s for p in F_FORBIDDEN_PHRASES)
        ),
        "",
    )
    expect(bool(leak), f"G 素材：找到一条 F 看不见的数据串 {leak[:44]!r}")

    (tmpf / "de" / "research" / "index.html").write_text(
        f"<p>Ein Tarif ohne Angabe: {leak}.</p>", encoding="utf-8"
    )
    (tmpf / "de" / "networks" / "index.html").write_text("<p>Alles gut.</p>", encoding="utf-8")
    save = problems
    problems = []
    check_de_pages(tmpf)
    f_red = list(problems)
    problems = []
    check_data_leaks(ctx, tmpf)
    g_red = list(problems)
    problems = save
    expect(not f_red, "G 素材确实绕过了 F（F 段零告警）")
    expect(any("G [" in p for p in g_red), "反例：G 抓住可见文本里的英文数据串")

    # G 的第二形态：只出现在 JSON-LD 里 —— `visible()` 把 `<script>` 整段挖掉，
    # 这正是 50 个德语国家页 `"name": "Best … ranked by cost per GB"` 躲过所有判据的原因。
    (tmpf / "de" / "research" / "index.html").write_text(
        '<p>Ein Tarif ohne Angabe.</p>'
        '<script type="application/ld+json">{"name": "%s"}</script>' % leak,
        encoding="utf-8",
    )
    save = problems
    problems = []
    check_de_pages(tmpf)
    f2 = list(problems)
    problems = []
    check_data_leaks(ctx, tmpf)
    g2 = list(problems)
    problems = save
    expect(not f2, "JSON-LD 形态确实绕过 F")
    expect(any("G [" in p for p in g2), "反例：G 抓住 JSON-LD 里的英文数据串")

    # 正例：换成德语译文 → G 零告警（否则守卫会变成噪音源，然后被「优化掉」）
    (tmpf / "de" / "research" / "index.html").write_text(
        "<p>%s</p>" % ctx.de_strings[leak], encoding="utf-8"
    )
    save = problems
    problems = []
    check_data_leaks(ctx, tmpf)
    g3 = list(problems)
    problems = save
    expect(not g3, "正例：G 不误伤德语译文")

    # ⚠ 假阳性边界：德语小数点写逗号 ⇒ `65,1 Mbps` 天然含子串 `1 Mbps`。
    #   没有 `(?<![\\d.,])` 这条左边界，/de/networks/ 的 Ookla 段落一次报 7 条假红。
    #   **注入清单**而不是取真实数据：真实禁串会随数据演变，边界判据不该跟着它漂。
    (tmpf / "de" / "research" / "index.html").write_text(
        "<p>SoftBank gewann die Download-Geschwindigkeit mit 65,1 Mbps und "
        "die 5G-Geschwindigkeit mit 268,1 Mbps.</p>"
        "<p>Ein Tarif ohne Angabe: 1 Mbps.</p>",
        encoding="utf-8",
    )
    save = problems
    problems = []
    check_data_leaks(ctx, tmpf, ["1 Mbps"])
    g4 = list(problems)
    problems = save
    expect(len(g4) == 1 and "1 Mbps" in g4[0], "G 只抓独立出现的 `1 Mbps`，放过 `65,1 Mbps` / `268,1 Mbps`")

    # ── G 的第三形态：**非 HTML 德语产物**（2026-10-10 第七十四轮）─────────────
    # `/de/llms.txt` / `/de/catalog.json` / RSS XML 都在 `glob("**/index.html")` 之外，
    # 却同样是读者 / 爬虫 / AI 直接读的德语产物。这一组反例同时钉三件事：
    #   ① 扫描面确实扩到了非 HTML；② 换实现（正则 → `str.find`）后数字左边界没丢；
    #   ③ 干净 XML 不被误伤 —— 只证 ① 会把守卫做成噪音源，那时它会被「优化掉」。
    (tmpf / "de" / "llms.txt").write_text(
        "Anbieter:\n- Nomad: %s\n" % leak.replace('"', "'"), encoding="utf-8"
    )
    (tmpf / "de" / "catalog.json").write_text(
        '{"notes": "ok", "fairUse": "%s"}' % leak.replace('"', "'"), encoding="utf-8"
    )
    (tmpf / "de" / "sitemap.xml").write_text(
        "<urlset><loc>https://www.esimsift.com/de/</loc></urlset>", encoding="utf-8"
    )
    save = problems
    problems = []
    check_data_leaks(ctx, tmpf)
    g5 = list(problems)
    problems = save
    expect(any("G [de/llms.txt]" in p for p in g5), "反例：G 抓住 llms.txt 里的英文数据串")
    expect(any("G [de/catalog.json]" in p for p in g5), "反例：G 抓住 catalog.json 里的英文数据串")
    expect(not any("sitemap.xml" in p for p in g5), "正例：干净 XML 不误伤")

    # 换成德语译文 → 非 HTML 产物零告警
    (tmpf / "de" / "llms.txt").write_text(
        "Anbieter:\n- Nomad: %s\n" % ctx.de_strings[leak].replace('"', "'"), encoding="utf-8"
    )
    (tmpf / "de" / "catalog.json").write_text(
        '{"fairUse": "%s"}' % ctx.de_strings[leak].replace('"', "'"), encoding="utf-8"
    )
    save = problems
    problems = []
    check_data_leaks(ctx, tmpf)
    g6 = list(problems)
    problems = save
    expect(not g6, "正例：G 不误伤非 HTML 产物里的德语译文")

    # ⚠ 证明「换实现后左边界仍在」：朴素 `in` 判断会让 `65,1 Mbps` 命中子串 `1 Mbps`。
    # 先把上一步留在 HTML 页里的独立 `1 Mbps` 中和掉 —— 否则下面这条正例
    # 会因为**同一 strs 也扫 HTML** 而误红（判据本身没错，是测试素材没清干净）。
    (tmpf / "de" / "research" / "index.html").write_text("<p>Alles gut.</p>", encoding="utf-8")
    (tmpf / "de" / "llms.txt").write_text("Tempo: 65,1 Mbps und 268,1 Mbps.", encoding="utf-8")
    (tmpf / "de" / "catalog.json").write_text('{"x": "ok"}', encoding="utf-8")
    save = problems
    problems = []
    check_data_leaks(ctx, tmpf, ["1 Mbps"])
    g7 = list(problems)
    problems = save
    expect(not g7, "正例：非 HTML 产物同样放过德语小数点逗号（65,1 Mbps 不误伤）")

    # JSON `\uXXXX` 还原：Hugo `jsonify` 把 `&` 写成 `\u0026`，不还原就漏判
    (tmpf / "de" / "catalog.json").write_text('{"fairUse": "A \\u0026 B plan"}', encoding="utf-8")
    save = problems
    problems = []
    check_data_leaks(ctx, tmpf, ["A & B plan"])
    g8 = list(problems)
    problems = save
    expect(any("catalog.json" in p for p in g8), "反例：JSON 转义还原后仍被抓住")

    shutil.rmtree(tmpf, ignore_errors=True)

    shutil.rmtree(tmp, ignore_errors=True)
    print("== selftest", "通过" if ok else "失败", "==")
    return 0 if ok else 1


# --------------------------------------------------------------------------- main
def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--selftest", action="store_true")
    args = ap.parse_args()

    ctx = Ctx()
    if problems:
        for p in problems:
            print("FAIL " + p)
        return 1

    if args.selftest:
        return selftest(ctx)

    check_source(ctx)
    check_strings(ctx)
    check_policy_coverage(ctx)
    check_de_units()
    check_products(ctx)
    check_de_pages()
    check_region_labels()
    check_data_leaks(ctx)

    for i in infos:
        print("  " + i)
    if problems:
        print()
        for p in problems[:40]:
            print("FAIL " + p)
        if len(problems) > 40:
            print(f"… 另有 {len(problems) - 40} 条")
        print(f"\n数据层文案本地化守卫：{len(problems)} 处问题")
        return 1
    print("\n数据层文案本地化守卫：全部通过")
    return 0


if __name__ == "__main__":
    sys.exit(main())
