# -*- coding: utf-8 -*-
"""冠词一致性守卫（产物级）：`a` / `an` 与品牌名必须匹配。

── 为什么需要它（同一个坑踩了两次）──────────────────────────────────────────
第二十四轮：i18n 值里写 `whether a {{ .brand }} plan` —— 品牌名从 Airalo 到 Yesim
混着元音/辅音开头，一个固定冠词不可能全对，渲染出 "whether **a Airalo** plan"。
第五十六轮又犯：`Does a {{ .brand }} eSIM work in …` → "Does **a Airalo** eSIM work"。

两次都是「靠人在写文案时记住」失败的。所以这次改成**产物级断言**：
写错就红，不依赖自觉。

── 口径（只做品牌的，不做全部名词）────────────────────────────────────────
  需要 "an" 的品牌：**Airalo**、**aloSIM**（元音发音开头）。
  ⚠ **Ubigi 是例外**：字母 U 开头，但发音 /ˈuːbɪdʒi/ 的起首是辅音 /j/，
    所以正确写法是 "a Ubigi plan"。用「首字母是元音字母」做判据会在这里误报。

  为什么只看品牌名：品牌名是**占位符值**里唯一会随品牌换首音的变量（`{{ .brand }}`），
  其余占位符（数字、天数）不产生 a/an 问题；国名另有 reality_lead 一处，已单独修掉
  并在此脚本里一并覆盖（元音发音开头的国名见 COUNTRIES_AN）。

── 为什么读产物而不是读 i18n 源 ─────────────────────────────────────────────
源文件里写的是 `{{ .brand }}`，看不出渲染后会变成哪个品牌 —— 这跟
check_faq_facts.py 必须读产物是同一个道理。只有 HTML 里才有真值。

── 第二道：源码级「禁止冠词紧邻占位符」（第五十六轮补）──────────────────────
产物级只能抓到**当前真的渲染出来**的错。第五十六轮实测过它的盲区：品牌 Hub 里
7 个 printf 问句都写成 `a %s eSIM`，但只有 3 个在当前品牌分层（$v 1/$v 2）下渲染，
另外 4 个和 networks 页那句属于**同类隐患却没被渲染到** —— 产物级全绿。
等哪天来个元音开头的品牌或国家，就得再修一次。

所以源码级直接**禁写**这种句式：冠词与占位符之间不留空格、紧邻，就是错。
正确写法永远是换个语序（`an eSIM from {brand}` 对 Airalo 和 Yesim 都对），
不存在「必须紧邻」的正当理由。窄化到专有名词占位符，避免误报数字
（`a {days}-day trip` 合法，`a {country} eSIM` 不合法）。

── 适用范围（第六十三轮补）──────────────────────────────────────────────
  产物级**只扫英语页**（`should_scan()`），源码级**仍然全语言**。
  理由：冠词是英语语法。德语 `Sieh dir das gesamte Bild für Deutschland an` 的 `an`
  是可分动词前缀，与下一句品牌名连排后会被误读成 "an Holafly"（实测 1 处误报）。
  译文页的英文残留由 verify_de_text.py 的 C 段负责，判据不重叠。

用法：
    python -X utf8 scripts/check_article_agreement.py
    python -X utf8 scripts/check_article_agreement.py --selftest   # 注入反例，证明会报红
"""
from __future__ import annotations

import glob
import html as htmlmod
import re
import sys
import tomllib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PUBLIC = ROOT / "public"
sys.path.insert(0, str(Path(__file__).resolve().parent))
from lang_rules import non_default_prefixes, under_any  # noqa: E402

# 英语专属规则的适用边界：**只扫英语产物**。
# 为什么（第六十三轮实测）：德语 `Sieh dir das gesamte Bild für Deutschland an` 里
# `an` 是**可分动词 ansehen 的句末前缀**，德语完全正确；但产物与下一句品牌名连排成
# `…für Deutschland an Holafly verkauft…`，本规则按英语读成 "an Holafly" ⇒ 误报。
# 冠词是英语语法；译文页的英文残留由 verify_de_text.py 的 C 段（43 条禁词表）负责，
# 源码级检查（scan_sources）仍是**全语言**的，所以「a {{ .brand }}」这类写法照样拦得住。
_NON_EN = non_default_prefixes()


def should_scan(rel: str) -> bool:
    """该产物路径是否属于英语页（= 需要跑冠词检查）。"""
    return not under_any(rel, _NON_EN)


# 元音**发音**开头的品牌 → 必须用 "an"
BRANDS_AN = {"airalo", "alosim"}
# 元音**发音**开头的国名 → 必须用 "an"（U 开头的 United/UAE 发音是辅音 /j/，不在此列）
COUNTRIES_AN = {"argentina", "australia", "austria", "egypt", "iceland", "india",
                "indonesia", "ireland", "israel", "italy", "ethiopia"}
# 显式排除：字母是元音但发音是辅音，必须配 "a"
PRONOUNCED_CONSONANT = {"ubigi", "united", "uae", "united-arab-emirates", "united-states",
                        "united-kingdom", "ukraine", "uganda", "uruguay"}

STRIP_SCRIPT = re.compile(r"<script\b.*?</script>", re.S | re.I)
STRIP_STYLE = re.compile(r"<style\b.*?</style>", re.S | re.I)
STRIP_TAG = re.compile(r"<[^>]+>")
WS = re.compile(r"\s+")
ARTICLE = re.compile(r"\b(a|an)\s+([A-Za-z][A-Za-z0-9'’\-]*)")

# ── 源码级禁令 ────────────────────────────────────────────────────────────────
# 只针对「会被替换成专有名词」的占位符。紧跟 `-` 或空格的一律放过：
#   `a {{ .days }}-day trip` / `a %s-day package` 合法（值是数字）。
_SRC_LAYOUT = re.compile(r"\b(a|an)\s*%s(?!-)")
_SRC_LAYOUT_TPL = re.compile(
    r"\b(a|an)\s*\{\{[^}]*\.\s*(brand|country|region|provider|name|iso)\b")
_SRC_FAQ = re.compile(r"\b(a|an)\s*\{(country|neighbor|neighbors_all|brand|region|name|iso)\}")
_SRC_I18N = re.compile(r"\b(a|an)\s*\{\{\s*\.\s*(brand|country|region|provider|name|iso)\b")


def load_nouns() -> set[str]:
    """所有会被占位符替换、且可能跟在 a/an 后面的专有名词。"""
    out: set[str] = set(BRANDS_AN)
    prov = tomllib.loads((ROOT / "data" / "providers.toml").read_text(encoding="utf-8"))
    for k, v in prov.items():
        if isinstance(v, dict) and v.get("name"):
            out.add(v["name"].lower())
            out.add(str(k).lower())
    ctry = tomllib.loads((ROOT / "data" / "countries.toml").read_text(encoding="utf-8"))
    for k, v in ctry.items():
        if isinstance(v, dict) and v.get("name"):
            out.add(v["name"].lower())
    out |= COUNTRIES_AN
    return out


def visible(h: str) -> str:
    h = STRIP_SCRIPT.sub(" ", h)
    h = STRIP_STYLE.sub(" ", h)
    h = STRIP_TAG.sub(" ", h)
    return WS.sub(" ", htmlmod.unescape(h))


def need_article(noun_low: str) -> str:
    if noun_low in PRONOUNCED_CONSONANT:
        return "a"
    if noun_low in BRANDS_AN or noun_low in COUNTRIES_AN:
        return "an"
    return "a"


def scan_text(label: str, text: str, nouns: set[str]) -> list[str]:
    errs: list[str] = []
    for m in ARTICLE.finditer(text):
        art, noun = m.group(1), m.group(2)
        low = noun.lower()
        if low not in nouns:
            continue
        want = need_article(low)
        if art != want:
            a, b = max(0, m.start() - 40), min(len(text), m.end() + 40)
            errs.append(f"{label}: 冠词错 -> \"{art} {noun}\"（应为 \"{want} {noun}\"）: …{text[a:b]}…")
    return errs


def scan_sources() -> list[str]:
    """源码级：禁止「冠词紧邻专有名词占位符」。

    产物级只看得到当前渲染出的组合；这一条把「等元音开头的品牌/国家进来才会
    暴雷」的写法当场拦住。命中的修法永远是换语序，所以判为硬错而不是警告。
    """
    errs: list[str] = []

    def walk(rel_glob: str, rules, strip_comment: str | None = None):
        for p in sorted(ROOT.glob(rel_glob)):
            if p.is_dir():
                continue
            for i, line in enumerate(p.read_text(encoding="utf-8",
                                                 errors="replace").splitlines(), 1):
                if strip_comment and line.lstrip().startswith(strip_comment):
                    continue
                if line.lstrip().startswith("#") and p.suffix == ".toml":
                    continue
                for rule in rules:
                    for m in rule.finditer(line):
                        errs.append(
                            f"{p.relative_to(ROOT).as_posix()}:{i} 冠词紧邻占位符 -> "
                            f"\"{m.group(0)}\"（渲染后可能是 a Argentina / a Airalo；"
                            f"请换语序，如 an eSIM from …）")

    walk("layouts/**/*.html", [_SRC_LAYOUT, _SRC_LAYOUT_TPL])
    walk("i18n/*.toml", [_SRC_I18N])
    walk("scripts/faq_frames.py", [_SRC_FAQ])
    return sorted(set(errs))


def selftest_sources() -> int:
    """逐条规则自测（不跨规则累加 —— 真实运行时每种文件只跑它自己那条）。

    只测「放过」和「抓住」两侧：只证明放过 = 把检查改瞎，只证明抓住 = 满屏误报。
    """
    cases = [
        (_SRC_LAYOUT, 'printf "a %s eSIM" $p.name', 1),        # 真实踩过的坑
        (_SRC_LAYOUT, 'printf "an eSIM from %s" $p.name', 0),
        (_SRC_LAYOUT, 'printf "a %s-day trip" $days', 0),      # 数值，合法
        (_SRC_LAYOUT_TPL, 'a {{ .brand }} plan', 1),
        (_SRC_LAYOUT_TPL, 'a {{ .days }}-day trip', 0),
        (_SRC_LAYOUT_TPL, 'than {{ .days }} days', 0),         # "than" 里的 an 不是冠词
        (_SRC_FAQ, 'a {country} eSIM', 1),
        (_SRC_FAQ, 'a {unl_days}-day package', 0),             # 数值 token，合法
        (_SRC_FAQ, 'a travel eSIM for {country}', 0),
        (_SRC_I18N, 'whether a {{ .brand }} plan', 1),
        (_SRC_I18N, 'for a {{ .days }}-day trip', 0),
    ]
    bad = 0
    for rule, text, want in cases:
        got = len(rule.findall(text))
        ok = got == want
        bad += 0 if ok else 1
        print(f"  [{'OK' if ok else 'FAIL'}] 源码级 期望 {want} / 实得 {got}  -> {text!r}")
    return bad


def selftest() -> int:
    nouns = {"airalo", "alosim", "holafly", "ubigi"}
    cases = [
        ("an Airalo plan is fine", 0),
        ("a Holafly plan is fine", 0),
        ("a Ubigi plan is fine", 0),          # U 发辅音 /j/
        ("whether a Airalo plan works", 1),   # 真实踩过的坑
        ("whether an Holafly plan works", 1),
        ("share a aloSIM eSIM", 1),
        ("an Ubigi line", 1),                 # 过度纠正也算错
    ]
    bad = 0
    for text, want in cases:
        got = len(scan_text("selftest", text, nouns))
        ok = got == want
        bad += 0 if ok else 1
        print(f"  [{'OK' if ok else 'FAIL'}] 产物级 期望 {want} 报错 / 实得 {got}  -> {text!r}")
    bad += selftest_sources()

    # 语言隔离（第六十三轮）：英语专属规则不得扫译文页 ——
    # 只证明「抓得住」不够，还要证明「不该看的没看」。
    iso = should_scan("compare/argentina/index.html") and not should_scan("de/compare/argentina/index.html")
    bad += 0 if iso else 1
    print(f"  [{'OK' if iso else 'FAIL'}] 语言隔离：英语页要扫 / 德语页跳过"
          f"（非默认前缀 {sorted(_NON_EN)}）")

    print(f"selftest: {'全部通过' if not bad else f'{bad} 项不符合预期'}")
    return 1 if bad else 0


def main() -> int:
    if "--selftest" in sys.argv:
        return selftest()

    nouns = load_nouns()
    files = sorted(glob.glob(str(PUBLIC / "**" / "*.html"), recursive=True))
    errs: list[str] = []
    skipped = 0
    for f in files:
        p = Path(f)
        rel = p.relative_to(PUBLIC).as_posix()
        if not should_scan(rel):
            skipped += 1
            continue
        errs += scan_text(rel, visible(p.read_text(encoding="utf-8")), nouns)

    src_errs = scan_sources()
    print(f"  产物级：扫描 {len(files) - skipped} 个英语 HTML（跳过 {skipped} 个译文页，"
          f"冠词是英语语法），{len(errs)} 处冠词不一致")
    print(f"  源码级：layouts/i18n/faq_frames 中冠词紧邻占位符 {len(src_errs)} 处")

    if errs or src_errs:
        for e in (src_errs + errs)[:40]:
            print("ERROR " + e)
        print(f"\n共 {len(errs) + len(src_errs)} 处问题")
        return 1
    print("OK: 冠词一致（a/an 与品牌名、国名匹配；源码无「冠词紧邻占位符」写法）")
    return 0


if __name__ == "__main__":
    sys.exit(main())
