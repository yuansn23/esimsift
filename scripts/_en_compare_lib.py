# -*- coding: utf-8 -*-
"""英语 compare 正文「事实槽位」的抽取与改写库（单一真源）。

为什么需要它
------------
`content/en/compare/{slug}.md` 的**正文**是「8 品牌时期」的手写快照，而同页 front
matter 的 `seo.description` 由 `regen_meta_brand.py` **实时现算** ⇒ 同一页两处数字
互相打脸（读者与 Google 都看得见）。德语侧已在批 E 全部刷成现算；本库把英语侧补齐。

设计原则
--------
1. **只改槽位，不重写文风**：50 页英语正文是 50 套独立手写句式（反同质化资产），
   绝不能整篇重生成。本库按「槽位正则」定位事实值，**只替换被捕获的那一段**，
   句子的其余部分逐字节不动。
2. **口径单一真源**：事实值全部来自 `scripts/_compare_de_facts.py`（与德语侧同一套），
   **不另写第二份计算**。
3. **品牌名规范**：正文里的小写原始 key（`yesim`/`ubigi`/`roamic`…）改为
   `data/providers.toml` 的规范名（`Yesim`/`Ubigi`/`Roamic`…）。同文件的
   `seo.description` 本来就写规范名，正文写小写 = 同页两处不一致。
"""
from __future__ import annotations

import importlib.util
import pathlib
import re
import tomllib

ROOT = pathlib.Path(__file__).resolve().parents[1]
EN = ROOT / "content" / "en" / "compare"

_SPEC = importlib.util.spec_from_file_location("_facts", ROOT / "scripts" / "_compare_de_facts.py")
_facts = importlib.util.module_from_spec(_SPEC)
_SPEC.loader.exec_module(_facts)  # type: ignore[union-attr]

PROVIDERS = tomllib.loads((ROOT / "data" / "providers.toml").read_text(encoding="utf-8"))
BRAND_NAME = {k: v["name"] for k, v in PROVIDERS.items()}

# 小写原始 key → 规范名（长 key 优先，避免 roami/roamic 互相咬）
_LOWER_KEYS = sorted((k for k in PROVIDERS if k != k.capitalize()), key=len, reverse=True)
BRAND_RE = re.compile(r"\b(" + "|".join(re.escape(k) for k in _LOWER_KEYS) + r")\b")


def canon(name: str) -> str:
    return BRAND_NAME.get(name.lower(), name)


def tech_phrase(prof: list[dict]) -> str:
    """由券商 tech 集合推导短语。⚠ 只有 {4G} 时是 `all 4G`，不是「mix」
    —— 本站只有 FJ 属此情形，写成 mix 会假红（本库首版确实这样错过一次）。"""
    techs = {p["tech"] for p in prof}
    if techs == {"5G"}:
        return "all 5G"
    if techs == {"4G"}:
        return "all 4G"
    return "a mix of 4G and 5G"


def live_values(iso: str) -> dict:
    """该国的**现算**事实值（与德语侧同源口径）。"""
    s = _facts.collect(iso)
    if not s:
        return {}
    ce, br, cu = s["cheapest_entry"], s["best_rate_row"], s["cheapest_unlim"]
    prof = s["carrier_profiles"]
    ratio = (ce["price"] / ce["gb"]) / s["best_rate"] if ce["gb"] > 0 else 0.0
    return {
        "T": str(s["total_plans"]),
        "U": str(s["unlimited_plans"]),
        "rate": f'{s["best_rate"]:.2f}',
        "rate_brand": canon(br["brand"]),
        "entry_price": f'{ce["price"]:.2f}',
        "entry_brand": canon(ce["brand"]),
        "entry_mb": str(s["entry_at_rate_mb"]),
        "entry_gb": f'{s["entry_at_rate_mb"] / 1024:.1f}',
        "ratio": f"{ratio:.1f}",
        "daily": f'{cu["per_day"]:.2f}' if cu else None,
        "daily_brand": canon(cu["brand"]) if cu else None,
        "breakeven": f'{s["breakeven_gb_day"]:.1f}',
        "speed_min": str(min(p["speed_min"] for p in prof)),
        "speed_top": str(max(p["speed_top"] for p in prof)),
        "tech": tech_phrase(prof),
        "plan_rate": br["name"],
        "plan_entry": ce["name"],
        "plan_daily": cu["name"] if cu else None,
    }


# ── 槽位正则（单捕获组 = 该槽位的值）。每条只捕获事实值本身 ──
RE_T = [
    r"the board runs to (\d+) plans",
    r"there are (\d+) plans for",
    r"listing (\d+) plans for",
    r"list (\d+) plans for",
    r"holds (\d+) plans for",
    r"full board is (\d+) plans for",
    r"among (\d+) options for",
]
RE_U = [
    r"(\d+) sold as unlimited",
    r"(\d+) of them unlimited",
    r"(\d+) carrying an unlimited label",
    r"of which (\d+) are unlimited",
    r"That is (\d+) unlimited plans",
]
RE_RATE_GB = r"\$(\d+\.\d\d)/GB"
RE_RATE_GIG = r"\$(\d+\.\d\d) a gigabyte"
RE_ENTRY = r"(?:nearer|about|reaches about|would give you about|would buy nearer) ([\d.]+)(MB|GB)(?! a day)"
RE_RATIO = r"(\d+\.\d+) times"
# 入口价：P1 里所有**不是** `/GB`、不是 `a gigabyte`、不是 `for {N}GB`（费率写法）的 $X.XX
RE_ENTRY_PRICE = r"\$(\d+\.\d\d)(?!/GB)(?! a gigabyte)(?! for \d+(?:\.\d+)?\s?GB)"
# 入口套餐规格（正文写成 `500MB / 1 Day`）。⚠ 只与**供应商原始套餐名**比 ——
# 用反推的 gb 会比出 `199MB → 200MB` 的假红（原始名才是面向读者的权威数字）。
RE_ENTRY_SIZE = r"(\d+(?:\.\d+)?)\s*(MB|GB)\s*/\s*(\d+)\s*Days?\b"
RE_DAILY = [
    r"\$(\d+\.\d\d) a day",
    r"\$(\d+\.\d\d)/day",
    r"\$(\d+\.\d\d), courtesy of",
    r"cheapest with \w+ at \$(\d+\.\d\d)",
    r"bottoms out at \$(\d+\.\d\d)",
]
RE_BREAKEVEN = [
    r"([\d.]+)GB a day",
    r"demand above ([\d.]+)GB",
    r"stays under ([\d.]+)GB",
]
RE_SPEED = [
    (r"span (\d+) to (\d+) Mbps", "min", "top"),
    (r"run from (\d+) to (\d+) Mbps", "min", "top"),
    (r"between (\d+) and (\d+) Mbps", "min", "top"),
    (r"from about (\d+) Mbps upward, topping out near (\d+)", "min", "top"),
    (r"in a (\d+)-(\d+) Mbps band", "min", "top"),
]
RE_TECH = r"(all \dG|a mix of \dG and \dG)"

# 品牌槽位：'*' = 槽位品牌。只用**已观察到的句式**，避免误伤。
RE_BRAND_SLOTS = [
    (r"comes in under (\w+)'s", "entry"),
    (r"Cheapest of the lot is (\w+)", "entry"),
    (r"The cheapest way in is (\w+)", "entry"),
    (r"(\w+) leads on entry price", "entry"),
    (r"(\w+) holds the entry price", "entry"),
    (r"The lowest price in \w+ is (\w+)", "entry"),
    (r"The cheapest plan in \w+ is (\w+)", "entry"),
    (r"The cheapest option in \w+ is (\w+)", "entry"),
    (r"^Entry in \w+ starts at \$[\d.]+ with (\w+)", "entry"),
    (r"Budget buyers in \w+ land on (\w+)", "entry"),
    (r"The floor in \w+ is (\w+)'s", "entry"),
    (r"The cheapest plan on the board is (\w+)'s", "entry"),
    (r"The cheapest sticker price belongs to (\w+)", "entry"),
    (r"Entry pricing in \w+ bottoms out with (\w+)", "entry"),
    (r"from (\w+) is the cheapest buy", "entry"),
    (r"Best value per gigabyte goes to (\w+)", "rate"),
    (r"Cheapest by the gigabyte is (\w+)", "rate"),
    (r"The best rate here is (\w+)'s", "rate"),
    (r"(\w+) takes the per-gigabyte race", "rate"),
    (r"(\w+) wins on rate", "rate"),
    (r"Per-gigabyte pricing is set by (\w+)", "rate"),
    (r"By rate, (\w+) sets the floor", "rate"),
    (r"On cost per gigabyte (\w+) leads", "rate"),
    (r"The value crown is (\w+)'s", "rate"),
    (r"Value leadership sits with (\w+)", "rate"),
    (r"On cost per gigabyte (\w+) leads with", "rate"),
    (r"Daily-rate unlimited is cheapest with (\w+)", "daily"),
    (r"starts at \$[\d.]+ a day with (\w+)", "daily"),
    (r"(\w+) prices unlimited in \w+ from", "daily"),
    (r"(\w+) holds the cheapest unlimited rate", "daily"),
    (r"comes from (\w+) at \$[\d.]+ a day", "daily"),
    (r"is (\w+)'s, at \$[\d.]+ a day", "daily"),
    (r"unlimited is cheapest with (\w+) at", "daily"),
    (r"floor is \$[\d.]+ with (\w+)", "daily"),
    (r"starts at \$[\d.]+ via (\w+)", "daily"),
    (r"floors at \$[\d.]+/day from (\w+)", "daily"),
    (r"undercuts the field at [\d.]+ a day", "daily"),
    (r"begins at \$[\d.]+, courtesy of (\w+)", "daily"),
    (r"(\w+) undercuts the field", "daily"),
]


_DOC_RE = re.compile(r"^---\r?\n(.*?)^---\r?\n", re.M | re.S)


def split_doc(text: str) -> tuple[str, str]:
    """切 front matter 与正文。⚠ **必须容忍 CRLF** —— `content/en/**` 是 CRLF，
    而 `content/de/**` 是 LF（首版脚本按 `---\\n` 切，在英语侧直接 IndexError）。"""
    m = _DOC_RE.match(text)
    if not m:
        raise ValueError("未找到 front matter")
    body = text[m.end():]
    # 去掉紧跟的分隔空行（CRLF/LF 通用）
    body = re.sub(r"^(?:\r?\n)+", "", body)
    return m.group(1), body


def body_of(text: str) -> str:
    return split_doc(text)[1].strip()


def front_matter(text: str) -> str:
    return split_doc(text)[0]


def paragraphs(body: str) -> list[str]:
    """按空行切段（CRLF/LF 通用）。⚠ 不能用 `split("\\n\\n")` ——
    `a\\r\\n\\r\\nb` 里没有 `\\n\\n`，会整篇当一段。"""
    return [p.strip() for p in re.split(r"\r?\n\r?\n", body) if p.strip()]
