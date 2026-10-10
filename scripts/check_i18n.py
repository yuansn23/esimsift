# -*- coding: utf-8 -*-
"""多语言守卫 —— 防止模板层重新出现硬编码文案，并检查各语言 key 完整性。

为什么需要它：模板文案一旦硬编码，新增语言时就会被漏掉，页面混语言。
改造前全站零 i18n 基础设施，`layouts/` 里有 2462 处英文文案；现已抽出的部分
必须锁住，不能再退回去。

检查项
  1. [ERROR]  layouts/ 中还有「纯静态英文文本节点 / 可翻译属性值」没走 i18n
  2. [ERROR]  i18n/<lang>.toml 与 i18n/en.toml 的 key 不对齐（漏译或多余 key）
  3. [WARN]   紧跟 {{ }} 的「拼装句碎片」—— 数量已知，需人工重写成带占位符的整句
  4. [WARN]   模板内联 <script> 里的用户可见英文（JS 上下文不能用 i18n，须改 data-* 注入）
  5. [ERROR]  `printf "…"` 格式串里的英文文案 —— 含 JSON-LD 的 `"name" (printf "…")`
              与 head.html 的 <title> 候选串（第六十三轮新增；实测 53 个德语页曾印英文而守卫全绿）
  6. [ERROR]  `dict "q" "…"` / `dict "a" "…"` 等**文案键的字面量值** ——
              FAQ 的 q/a 与 JSON-LD 的 name/text 都装在 dict 里，i18n_extract 只扫
              HTML 文本节点与属性值，这一类整个在视野外（第六十八轮实测：
              `research_unlimited_esim` 的 "Does unlimited eSIM mean unlimited speed?"
              曾硬编码进 dict，德语读者会看到英文问句而全部守卫全绿）

用法：python -X utf8 scripts/check_i18n.py [--strict]
  --strict 把 WARN 也当作失败（CI 里想彻底锁死时用）
"""
from __future__ import annotations

import json
import os
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(Path(__file__).resolve().parent))

from i18n_extract import collect, filetag  # noqa: E402  (复用同一个扫描器，避免两套口径)

LAYOUTS = ROOT / "layouts"
I18N_DIR = ROOT / "i18n"

errors: list[str] = []
warns: list[str] = []


def scan_layouts():
    hardcoded: list[str] = []
    frags: list[tuple[str, str]] = []
    scripts: list[tuple[str, str]] = []
    defaults: list[str] = []
    printf_lits: list[str] = []
    raw_hrefs: list[str] = []
    ext_hrefs: list[str] = []
    dict_copies: list[str] = []

    for dp, dn, fn in os.walk(LAYOUTS):
        for f in sorted(fn):
            if not re.search(r"\.(html|txt|json|xml)$", f):
                continue
            full = Path(dp) / f
            rel = full.relative_to(ROOT).as_posix()
            with open(full, encoding="utf-8", newline="") as fh:
                src = fh.read()
            if "$d := partialCached \"i18n-data.html\"" not in src and "hugo.Data" not in src:
                pass
            _te, _ae, fr, _ba = collect(rel, src)
            for _s, _e, v in _te:
                hardcoded.append(f"{rel}: text {v[:60]!r}")
            for _s, _e, v in _ae:
                hardcoded.append(f"{rel}: attr {v[:60]!r}")
            for v in fr:
                frags.append((rel, v))
            for v in hardcoded_defaults(src):
                defaults.append(f"{rel}: default {v[:60]!r}")
            for v in hardcoded_printf(src):
                printf_lits.append(f"{rel}: printf {v[:60]!r}")
            for v in raw_lang_href(src):
                raw_hrefs.append(f"{rel}: {v}")
            for v in external_lang_href(src):
                ext_hrefs.append(f"{rel}: {v}")
            for v in hardcoded_dict_literals(src):
                dict_copies.append(f"{rel}: {v[:60]!r}")

            # 内联 script 里的可疑英文（只抓含空格的句子，避免误报变量名）
            for m in re.finditer(r"<script(?![^>]*type=\"application/ld\+json\")[^>]*>(.*?)</script>", src, re.S | re.I):
                body = m.group(1)
                for sm in re.finditer(r"""["'`]([A-Z][A-Za-z][^"'`\n]{12,})["'`]""", body):
                    scripts.append((rel, sm.group(1)))
    return hardcoded, frags, scripts, defaults, printf_lits, raw_hrefs, ext_hrefs, dict_copies


# i18n 值里允许出现的占位符形态：只准 `{{ .name }}`。
# Hugo 会把 i18n 的值**当 Go 模板执行**（data = 调用时传的 dict `(dict "n" …)`），
# 所以值里写 `{{ len $d.countries }}` 这种表达式时——`len` 不是 Go 模板函数、
# `$d` 也不存在——求值失败，Hugo **把整条值渲染成空串，不报错也不警告**。
PLACEHOLDER_OK = re.compile(r"^\{\{\s*\.[A-Za-z0-9_]+\s*\}\}$")
PLACEHOLDER_ANY = re.compile(r"\{\{(.*?)\}\}", re.S)


def bad_placeholders(kv: dict) -> list[tuple[str, str]]:
    """返回值里出现「非 `{{ .name }}` 形态的 `{{ }}`」的 (key, 片段) 列表。"""
    out: list[tuple[str, str]] = []
    for k, v in kv.items():
        if not isinstance(v, str):
            continue
        for m in PLACEHOLDER_ANY.finditer(v):
            if not PLACEHOLDER_OK.match(m.group(0)):
                out.append((k, m.group(0).strip()))
    return out


# `default "…"` 里的文案 —— 见 hardcoded_defaults() 的 docstring。
# 恰好排除 `$` / `{` / `"` / `\`：带插值的兜底是数据而非文案，不该由本检查拦。
DEFAULT_LIT = re.compile(r'default\s+"([^"$\\{]{0,200})"')
_WORD = re.compile(r"[A-Za-z]{4,}")

# 允许保留的「看起来像文案」的兜底 —— 每一条都必须写明为什么它不是模板层文案。
DEFAULT_COPY_ALLOW = {
    # faq-live-tokens.html：50 国的 region 字段实测全部有值（缺 0 个），此兜底永不触发；
    # 即便触发，它插进的也是 data/faqs/*.toml 的英文句子 —— 那是 D6 数据层，不是模板层。
    "its region",
}


def hardcoded_defaults(src: str) -> list[str]:
    """`default "…"` 参数里的英文兜底 —— i18n_extract 看不见这一类。

    `default` 是 Hugo 管道算子，它的字面量实参既不进 text_edits 也不进 frags，
    于是本脚本曾一边报「0 处硬编码」，一边让 `layouts/compare/single.html` 在
    **50 个德语页**上印出一整句英文（2026-10-09 实测抓到）。

    判据：字面量含空格、且含一个 >=4 个连续拉丁字母的 token、且不含 `$` / `{` / `\\`。
    这样 CSS 类（`btn-out` / `h-9 w-9`）与数据哨兵（`official` / `compare`）不会误报 ——
    它们要么没有空格，要么 token 太短。
    """
    out: list[str] = []
    for m in DEFAULT_LIT.finditer(src):
        lit = m.group(1)
        if " " not in lit or lit in DEFAULT_COPY_ALLOW:
            continue
        if not _WORD.search(lit):
            continue
        out.append(lit)
    return out


# `printf "…"` 的格式串 —— 与 hardcoded_defaults 同一类盲区。
# 为什么看不见：格式串是 `printf` 的**实参**，不是 HTML 文本节点，i18n_extract 不扫它；
#   内联 <script> 的检查又按 `type="ld+json"` 排除掉了 JSON-LD —— 而本类泄漏**恰好**
#   多数发生在 JSON-LD 的 `"name" (printf "…")` 里。
# 实测（2026-10-09 第六十三轮）：53 个德语页曾印英文，守卫**全绿**：
#   · head.html 的 11 条 title 候选串 → 德语子页 <title> = "Holafly Deutschland eSIM 2026: Unlimited Data Plans"
#   · compare/single.html 的 JSON-LD name → 50 个德语国家页 "Best Argentinien eSIM plans ranked by cost per GB"
#   · vs-single.html 的 CTA → "View Airalo plans"（45 页）
#   · esim-providers/single.html 的 4 条 FAQ → "Does Airalo have unlimited data plans?"
# 为什么旧的 F 段（verify_de_text.py）也没抓到：F 是**黑名单**（8 个词、大小写敏感），
#   "Unlimited Data Plans" 一个都不含；且 F 只扫可见文本，JSON-LD 完全在视野外。
PRINTF_LIT = re.compile(r'printf\s+"((?:[^"\\]|\\.)*)"')
_PRINTF_FMT = re.compile(r"%[-+ #0-9.]*[sdvfqxXeEgGtT]")
# 出现这些字符 = 结构化代码串（路径/查询串/内部 key/HTML 片段），不是用户可见英文
_PRINTF_CODE = "/=_@'<>&"


def hardcoded_printf(src: str) -> list[str]:
    """`printf "…"` 格式串里的英文文案。

    判据：去掉格式动词后仍有 >=2 个连续拉丁字母词（每个 >=2 字母），
    且不含路径/查询/内部 key 特征字符。CSS 类与 `%s/%s/` 路径因此不误报。
    `printf (i18n "key")` 形态不含字面串，天然不报。
    """
    out: list[str] = []
    for m in PRINTF_LIT.finditer(src):
        lit = m.group(1)
        if lit.startswith("http") or any(ch in lit for ch in _PRINTF_CODE):
            continue
        body = _PRINTF_FMT.sub(" ", lit)
        if len(re.findall(r"[A-Za-z][A-Za-z'\-]+", body)) >= 2:
            out.append(lit)
    return out


_LANG_HREF_OK = re.compile(r'href="\{\{-?\s*partial\s+"lang-href\.html"')
# 站点路径（以 / 开头）由 printf 直接拼进 href，且这一行没有 lang-href
_LANG_HREF_RAW = re.compile(r'href="\{\{-?\s*printf\s+"/[^"]*"')


def raw_lang_href(src: str) -> list[str]:
    """`href="{{ printf "/…" }}"` —— 站点路径没过 `lang-href`，译文站会**语言降级**。

    为什么单列一条：这类链接**不 404**（默认语言有那个页），所以
    `check_links`（若在闸门里）与产物死链审计**都看不见**。实测：德语国家页
    曾把 `/de/compare/austria/roamic/` 写成 `/compare/austria/roamic/`，
    德语用户被静默送到英文页，53 处链接 / 2 个页型，所有守卫全绿。
    静态资源（favicon/css/img）不走 printf，天然不报。
    """
    out: list[str] = []
    for line in src.splitlines():
        if _LANG_HREF_OK.search(line):
            continue
        if _LANG_HREF_RAW.search(line):
            out.append(line.strip()[:90])
    return out


# `lang-href` 包住了**绝对外链**。lang-href 只处理站内路径，外链要裸 printf。
_LANG_HREF_EXT = re.compile(
    r'partial\s+"lang-href\.html"\s*\(\s*(?:printf\s+)?"https?://')


def external_lang_href(src: str) -> list[str]:
    """`{{ partial "lang-href.html" (printf "https://…") }}` —— 站外链接走错了通道。

    为什么单列一条：`lang-href.html` 第 3 层兜底是 `relURL(原路径)`，而 `relURL("https://x")`
    会得到 **`/https:/x`** —— 一个 404 的站内路径。产物仍是合法 HTML、三个死链检查
    （`check_links` / `audit_de_links` / `check_dates` 的域名检查）**全绿**，因为
    `/https:/…` 既不是 `localhost` 也不是站内路径，只是长得像。
    实测 2026-10-09 第六十六轮：两条模板把 Ookla Global Index 的外链套了 lang-href，
    污染 **102 个产物**（50 英文国家页 + 50 德文国家页 + 2 个 networks 列表页），
    d34 构建全绿。产物级兜底另见 `check_output.py` 的 `_BAD_URL_PREFIX`。
    """
    return [l.strip()[:90] for l in src.splitlines() if _LANG_HREF_EXT.search(l)]


# ── `dict "q" "…"` / `dict "a" "…"`：模板层文案在 dict 字面量里的盲区 ──
# 键列表只收**明确承载用户可见文案**的键；`@type` / `indent` / `id` / `path` / `site`
# 这些是 schema 关键词、缩进、锚点、路径 —— 值再像句子也不是文案。
DICT_COPY_KEYS = ("q", "a", "name", "text", "label", "title", "desc", "lead", "heading", "caption")
DICT_LIT = re.compile(r'dict\s+"(' + "|".join(DICT_COPY_KEYS) + r')"\s*"((?:[^"\\]|\\.)*)"')
_BACKSLASH = chr(92)


def hardcoded_dict_literals(src: str) -> list[str]:
    """`dict "q" "…"` / `dict "a" "…"` —— 模板层文案在 dict 字面量里的盲区。

    为什么单列一条：`i18n_extract` 只扫 HTML **文本节点**与**属性值**，
    `dict "q" "…"` 两者都不是 —— 于是 FAQ 问句/答案一旦写成字面量，
    `check_i18n.py` 会报「0 处硬编码」、产物却把英文原样印给德语读者。
    2026-10-10 实测：`layouts/research/unlimited-esim.html` 的
    `dict "q" "Does unlimited eSIM mean unlimited speed?"` 就是这么漏的
    （同一页其它 4 条 FAQ 都走了 i18n，唯独这条是字面量）。

    判据：值含空格、含 >=2 个 >=2 字母的拉丁词、不含 `{` / 反斜杠（排除插值兜底）。
    正例（不报）：`dict "@type" "Question"`（键不在列表）、`dict "indent" "  "`（无词）、
    `dict "path" "/guides/x"`（无空格）、`dict "q" (i18n "k")`（非字面量）。
    """
    out: list[str] = []
    for m in DICT_LIT.finditer(src):
        lit = m.group(2)
        if " " not in lit or "{" in lit or _BACKSLASH in lit:
            continue
        if len(re.findall(r"[A-Za-z][A-Za-z'\-]+", lit)) >= 2:
            out.append(f"{m.group(1)}: {lit}")
    return out


def check_keys():
    en = I18N_DIR / "en.toml"
    if not en.exists():
        errors.append("i18n/en.toml 不存在 —— 模板已引用 i18n 但 key 表缺失")
        return {}

    def load(p: Path) -> dict:
        out = {}
        for line in p.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if not line or line.startswith("#") or " = " not in line:
                continue
            k, v = line.split(" = ", 1)
            try:
                out[k.strip()] = json.loads(v.strip())
            except json.JSONDecodeError:
                errors.append(f"{p.name}: 无法解析的 TOML 值 -> {line[:80]}")
        return out

    base = load(en)
    for k, frag in bad_placeholders(base)[:10]:
        errors.append(
            f"i18n/en.toml: {k} 的值里有非法占位符 {frag!r}"
            "（只允许 `{{ .name }}`；写 Hugo 表达式会让整条值渲染成空串）")
    for p in sorted(I18N_DIR.glob("*.toml")):
        if p.name == "en.toml":
            continue
        cur = load(p)
        for k, frag in bad_placeholders(cur)[:10]:
            errors.append(
                f"i18n/{p.name}: {k} 的值里有非法占位符 {frag!r}"
                "（只允许 `{{ .name }}`；写 Hugo 表达式会让整条值渲染成空串）")
        missing = sorted(set(base) - set(cur))
        extra = sorted(set(cur) - set(base))
        if missing:
            errors.append(
                f"i18n/{p.name}: 缺 {len(missing)} 个 key（相对 en.toml），"
                f"前几个 -> {', '.join(missing[:5])}"
            )
        if extra:
            warns.append(
                f"i18n/{p.name}: 多出 {len(extra)} 个 key（en.toml 没有），"
                f"前几个 -> {', '.join(extra[:5])}"
            )
    print(f"  i18n: en.toml {len(base)} key" + (
        f"，另有 {len(list(I18N_DIR.glob('*.toml'))) - 1} 个语言文件" if len(list(I18N_DIR.glob("*.toml"))) > 1 else "（当前仅英文）"
    ))
    return base


# 模板里字面量写出的 i18n key（动态 key 如 i18n (index $m $k) 无法静态检查，跳过）
I18N_CALL = re.compile(r"""\bi18n\s+(["'])([A-Za-z0-9_]+)\1""")


def check_used_keys(base: dict) -> None:
    """每个模板里写死的 i18n key 都必须在 i18n/en.toml 里存在。

    为什么单列一条：Hugo 对**缺失的 key 静默返回空字符串** —— 不报错、不警告，
    页面直接少一整段文案（整个 <h2> 会渲染成空标签），而 check_keys() 只比对
    语言之间是否对齐，两边一起漏就查不出来。
    2026-10-04 实际踩到：compare_provider__fup_h2 与 __host_network_h2 漏定义，
    两个 <h2></h2> 空着上线，五重校验全绿。这条检查就是为了让同类问题当场失败。
    """
    used: dict[str, str] = {}
    for dp, dn, fn in os.walk(LAYOUTS):
        for f in sorted(fn):
            if not re.search(r"\.(html|txt|json|xml)$", f):
                continue
            full = Path(dp) / f
            rel = full.relative_to(ROOT).as_posix()
            src = full.read_text(encoding="utf-8", errors="replace")
            for m in I18N_CALL.finditer(src):
                used.setdefault(m.group(2), rel)
    missing = {k: v for k, v in used.items() if k not in base}
    print(f"  i18n 引用检查：模板引用 {len(used)} 个 key，未定义 {len(missing)} 个")
    for k, rel in sorted(missing.items()):
        errors.append(f"i18n key 未定义（Hugo 会静默渲染成空串）-> {k}  （首次出现于 {rel}）")


def selftest() -> int:
    """自测 bad_placeholders + hardcoded_defaults —— 两个方向都要证明。

    只证明「会红」不够：一个恒返回非空的实现能让所有反例通过。
    只证明「会绿」也不够：一个恒返回空的实现能让所有反例溜过去。
    """
    good = {
        "g1": "plain text, no braces",
        "g2": "{{ .n }} items",
        "g3": "{{ .a }} and {{ .b }} differ",
    }
    bad = {
        "b1": "in how many of our {{ len $d.countries }} tracked countries",
        "b2": "{{ .n }} then {{ $x }}",
    }
    failed = 0
    for name, kv, want in (("good", good, 0), ("bad", bad, 2)):
        got = bad_placeholders(kv)
        ok = len(got) == want
        failed += 0 if ok else 1
        print(f"  {'OK  ' if ok else 'MISS'} {name}: 期望 {want} 处，实得 {len(got)} 处 -> {got}")

    # default 兜底：正例必须放过「非文案」（CSS 类 / 数据哨兵 / 插值），
    # 反例必须抓住真文案 —— 只加前者等于把检查改瞎，只加后者必然误报。
    dgood = (
        '{{ .class | default "btn-out" }}',
        '{{ .size | default "h-9 w-9" }}',
        '{{ $p.promo_source | default "official" }}',
        '{{ $.campaign | default "compare" }}',
        '{{ $country.region | default "its region" }}',      # 显式白名单，理由见常量注释
        '{{ $n | default (i18n "g_x") }}',
        '{{ .fup | default (i18n "compare_provider__no_fup_published") }}',
    )
    dbad = (
        '{{ .fup | default "No fair-use policy published — treat speed claims with caution" }}',
        '{{ .label | default "View deal" }}',
        '{{ $.Params.h2_answer | default "The short answer" }}',
    )
    for name, cases, want in (("default-good", dgood, 0), ("default-bad", dbad, 3)):
        got = [x for c in cases for x in hardcoded_defaults(c)]
        ok = len(got) == want
        failed += 0 if ok else 1
        print(f"  {'OK  ' if ok else 'MISS'} {name}: 期望 {want} 处，实得 {len(got)} 处 -> {got}")

    # printf 格式串：正例必须放过路径 / 查询串 / 内部 key / 纯格式动词 / 已走 i18n，
    # 反例必须抓住真文案（含本轮实测泄漏的 4 条原始形态）。
    pfgood = (
        'printf (i18n "g_x") $a $b',
        'printf "%s/%s/" $a $b',
        'printf "static/img/providers/%s.png" $k',
        'printf "%.2f" $x',
        'printf "%s %s" $a $b',
        'printf "compare_provider__op_unl_v%d" 2',
        'printf "utm_source=%s&utm_medium=%s" $a $b',
    )
    pf_bad = (
        'printf "View %s plans" $na',
        'printf "Does %s support 5G?" $p.name',
        'printf "%s %s eSIM Review %d: Unlimited Data Plans" $a $b $y',
        'printf "Best %s eSIM plans ranked by cost per GB" $c',
    )
    for name, cases, want in (("printf-good", pfgood, 0), ("printf-bad", pf_bad, 4)):
        got = [x for c in cases for x in hardcoded_printf(c)]
        ok = len(got) == want
        failed += 0 if ok else 1
        print(f"  {'OK  ' if ok else 'MISS'} {name}: 期望 {want} 处，实得 {len(got)} 处 -> {got}")

    # lang-href：正例放过「已包裹」「静态资源」「路径里带 /」；反例抓住裸 printf 站点路径。
    # 反例含 2026-10-09 实测泄漏的三个原始形态（compare/single.html 的两处 + list 一处）。
    lhgood = (
        'href="{{ partial "lang-href.html" (printf "/compare/%s/%s/" $slug $k) }}"',
        '<link rel="icon" href="/favicon.svg" type="image/svg+xml">',
        '<a href="/about/">x</a>',
        'href="{{ .RelPermalink }}"',
        'href="{{ printf "%s" $x }}"',                       # 非站点路径（不以 / 开头）
        'href="{{ partial "lang-href.html" "/esim-deals/" }}"',
    )
    lh_bad = (
        'href="{{ printf "/compare/%s/%s/" $country.slug .key }}"',
        'href="{{ printf "/esim-providers/%s/" $pk }}"',
        'href="{{ printf "/esim-providers/%s/" $key }}"',
    )
    for name, cases, want in (("lang-href-good", lhgood, 0), ("lang-href-bad", lh_bad, 3)):
        got = [x for c in cases for x in raw_lang_href(c)]
        ok = len(got) == want
        failed += 0 if ok else 1
        print(f"  {'OK  ' if ok else 'MISS'} {name}: 期望 {want} 处，实得 {len(got)} 处 -> {got}")

    # 外链误过 lang-href：正例放过站内路径与裸外链；反例抓住 2026-10-09 实测的两处。
    ext_good = (
        'href="{{ partial "lang-href.html" (printf "/compare/%s/" $slug) }}"',
        'href="{{ printf "https://www.speedtest.net/global-index/%s" $sl | safeURL }}"',
        'href="{{ partial "lang-href.html" "/esim-deals/" }}"',
    )
    ext_bad = (
        'href="{{ partial "lang-href.html" (printf "https://www.speedtest.net/global-index/%s" $ooklaSlug | safeURL) }}"',
        'href="{{ partial "lang-href.html" (printf "http://example.com/%s" $x) }}"',
    )
    for name, cases, want in (("ext-href-good", ext_good, 0), ("ext-href-bad", ext_bad, 2)):
        got = [x for c in cases for x in external_lang_href(c)]
        ok = len(got) == want
        failed += 0 if ok else 1
        print(f"  {'OK  ' if ok else 'MISS'} {name}: 期望 {want} 处，实得 {len(got)} 处 -> {got}")

    # dict 字面量文案：正例必须放过 schema 关键词 / 缩进 / 路径 / 非字面量 / 单词值，
    # 反例必须抓住真文案 —— 含 2026-10-10 实测泄漏的原始形态。
    dlgood = (
        '{{ dict "@type" "Question" }}',
        '{{ dict "indent" "  " }}',
        '{{ dict "path" "/guides/what-is-an-esim" }}',
        '{{ dict "q" (i18n "k") }}',
        '{{ dict "name" "esimsift" }}',
        '{{ dict "a" (printf (i18n "k") $x) }}',
    )
    dlbad = (
        '{{ dict "q" "Does unlimited eSIM mean unlimited speed?" }}',
        "{{ dict \"a\" \"A heavy user's dream market.\" }}",
        '{{ dict "name" "Best eSIM plans ranked by cost per GB" }}',
    )
    for name, cases, want in (("dict-copy-good", dlgood, 0), ("dict-copy-bad", dlbad, 3)):
        got = [x for c in cases for x in hardcoded_dict_literals(c)]
        ok = len(got) == want
        failed += 0 if ok else 1
        print(f"  {'OK  ' if ok else 'MISS'} {name}: 期望 {want} 处，实得 {len(got)} 处 -> {got}")

    print(f"\n自测{'通过' if not failed else f'失败 {failed} 项'}")
    return 1 if failed else 0


def main() -> int:
    if "--selftest" in sys.argv:
        return selftest()

    strict = "--strict" in sys.argv

    hardcoded, frags, scripts, defaults, pf, raw_hrefs, ext_hrefs, dc = scan_layouts()

    for h in hardcoded[:25]:
        errors.append("硬编码文案未抽 i18n -> " + h)
    if len(hardcoded) > 25:
        errors.append(f"... 另有 {len(hardcoded) - 25} 处硬编码文案")

    for d in defaults[:15]:
        errors.append("`default \"…\"` 兜底里的文案未抽 i18n -> " + d)
    if len(defaults) > 15:
        errors.append(f"... 另有 {len(defaults) - 15} 处 default 兜底文案")

    for v in pf[:15]:
        errors.append("`printf \"…\"` 格式串里的文案未抽 i18n -> " + v)
    if len(pf) > 15:
        errors.append(f"... 另有 {len(pf) - 15} 处 printf 格式串文案")

    for v in raw_hrefs[:10]:
        errors.append("`href=\"{{ printf \"/…\"` 未过 lang-href（译文站语言降级）-> " + v)
    if len(raw_hrefs) > 10:
        errors.append(f"... 另有 {len(raw_hrefs) - 10} 处未过 lang-href 的 href")

    for v in ext_hrefs[:10]:
        errors.append("外链被套进 lang-href（产物会变成 /https:/… 的 404 站内路径）-> " + v)
    if len(ext_hrefs) > 10:
        errors.append(f"... 另有 {len(ext_hrefs) - 10} 处外链误过 lang-href")

    for v in dc[:15]:
        errors.append("`dict \"q\"/\"a\"` 字面量文案未抽 i18n -> " + v)
    if len(dc) > 15:
        errors.append(f"... 另有 {len(dc) - 15} 处 dict 字面量文案")

    print(f"  layouts: {len(hardcoded)} 处硬编码文案 / {len(frags)} 处拼装句碎片 / "
          f"{len(scripts)} 处内联脚本文案 / {len(defaults)} 处 default 兜底文案 / "
          f"{len(pf)} 处 printf 格式串文案 / {len(raw_hrefs)} 处未过 lang-href 的 href / "
          f"{len(ext_hrefs)} 处外链误过 lang-href / {len(dc)} 处 dict 字面量文案")
    base = check_keys()
    if base:
        check_used_keys(base)

    if frags:
        warns.append(f"{len(frags)} 处拼装句碎片待人工重写为带占位符的整句（例：{frags[0][0]} -> {frags[0][1][:50]!r}）")
    if scripts:
        warns.append(f"{len(scripts)} 处内联 <script> 用户文案需改为 data-* 注入（例：{scripts[0][0]} -> {scripts[0][1][:50]!r}）")

    for w in warns:
        print(f"  WARN  {w}")
    for e in errors:
        print(f"  ERROR {e}")

    if errors or (strict and warns):
        print(f"\nFAIL: {len(errors)} error(s), {len(warns)} warning(s)")
        return 1
    print(f"\nOK: 模板层无新增硬编码，i18n key 对齐（{len(warns)} 项已知待办）")
    return 0


if __name__ == "__main__":
    sys.exit(main())
