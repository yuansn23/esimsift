# -*- coding: utf-8 -*-
"""译文站「非可见层」文案守卫 —— 内联 JS 文案 + 站内路径字面量 + head 元数据。

## 为什么需要它（2026-10-11 第八十一轮实测）

全站**所有**德语文案守卫都**先挖掉 `<script>` 再判**：`verify_de_text.py` 的 E1–E5 扫
「整页可见文本」，而整页文本的提取第一步就是剥离 `<script>`/`<style>`；`_de_link_leak_audit`
读产物的 `<a href>`。这个做法本身是**正确**的（`ld+json` 里的 `\\"` 是合法转义，不剥会把
JSON 当文案）。代价是：**写在 `<script>` 里的用户可见文案，没有任何一条守卫看得见。**

实测后果：德语 **47 页印英文而构建全绿** ——
  · `layouts/compare/vs-single.html` → 德语 45/45 对决页（`'Pick two providers'` 等 6 句）
  · `layouts/tools/list.html`        → `/de/tools/`
  · `layouts/404.html` 派生的 `<title>`/`og:title`/JSON-LD `name` = `404 Page not found`

`check_i18n.py` 的「内联脚本」判据（第 4 项）本该兜住①，但①只 `warns.append`
（**WARN 不失败构建**）②正则要求字面量 **≥14 字符** → `'Compare '`（8 字符、被 `+`
拼成整句）**静默漏报**（实测报 5 处 / 真值 6 处）。两条都写进了 PROJECT.md 红线 104。

另外 ③ 之所以漏掉：**本仓所有产物级守卫都只 glob `*/index.html`**，
而 `public/<lang>/404.html` 不是 index.html —— 判据枚举了什么页型，就只保护那些页型
（红线 88 的同构形态）。所以本守卫扫 **`public/**/*.html` 全量**，不只 index.html。

## 判据（产物级）

  [1] **英文残留 · 脚本体** —— 非默认语言页的 `<script>`（排除 `ld+json` / `application/json`）
      里，字符串字面量命中「英文特有词」且**不含任何该语言特有标记** → ERROR。
  [2] **站内路径字面量** —— 非默认语言页的 `<script>` 里出现 `'/seg/…'` 形态的**站内绝对
      路径**字面量（`'/compare/' + slug` 这种）→ ERROR。JS 运行时把它当 `href` 用，读者会被
      **静默送到默认语言页**；而 `_de_link_leak_audit` 读的是产物 `<a href>`，看不见 JS 运行时
      赋的值 —— 本轮 45 个对决页的「对比」按钮就是这么跳进英语站的。
      静态资源目录（`static/` 顶层，**推导**而非写死）豁免。
      **计数口径 = 页**：同一页同一字面量出现多次只算一次（`de/tools/index.html` 的
      `subUrl` / `countryUrl` 去转义后都是 `/compare/`）。
  [3] **英文残留 · head 元数据** —— 非默认语言页的 `<title>` / `og:title` / `og:description` /
      `twitter:*` / `meta[name=description]` / 每个 `ld+json` 里的字符串值 → ERROR。

## 为什么用「封闭词类」而不是「英文单词黑名单」

`verify_de_text.py` 的 F 段是**人工黑名单**（23 短语 + 8 词），docstring 自承
「F 清单永远追不上数据」—— 内容词是开放集合，新文案随时绕开。本判据改用
**封闭词类**（冠词 / 代词 / 介词 / 连词 + 少量英语特有的高频功能词），这类词
数量固定、十年不变；再加「德语特有字符 / 德语封闭词类命中即豁免」做反向保险。
两个方向都不依赖对数据内容的枚举。

⚠️ 该语言未登记特有词表时**不静默放过** —— 打印 EXPLICIT 提示并以失败退出，
   避免「新加语言、本层自动失效」这种最坏的静默退化。

用法：python -X utf8 scripts/check_inline_copy.py [--selftest] [--root DIR]

**新判据必须先对改造前的旧产物跑一遍**（跑出红才证明它能发现该缺陷）：
    python -X utf8 scripts/check_inline_copy.py --root .buildlog/pub_r81_pre
第八十一轮实测：旧产物 = FAIL 26 条可疑字面量 / 324 处命中；改造后 = 0 / 0。
"""
from __future__ import annotations

import argparse
import json
import re
import sys
import tomllib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PUBLIC = ROOT / "public"
CONFIG = ROOT / "hugo.toml"
STATIC = ROOT / "static"

# ── 语言特有词表 ────────────────────────────────────────────────────────────
# 只收**封闭词类**（冠词/代词/介词/连词/否定词）＋极少数「英语独有、德语里不存在」的
# 高频功能词。**不收**易与德语同形或德语借词：plan / test / link / standard / filter /
# installation / unlimited / per / data / mobile / code / region / roaming / solo / top。
# 之所以列这份名单：2026-10-11 实测中 `unlimited` / `per` / `link` / `installation`
# 曾让 106 段**正确德语**被假红（`Ist unlimited wirklich unlimited`）。
# ⚠️ 另刻意**剔出单字母/双字母的歧义词**（a / i / us / it / at / by / in / on / so / as /
#    no / up / down / out / be）：它们既是英语功能词，又大量出现在 HTML 片段与
#    CSS 选择器里（`'<a href="'`、`'a[data-name]'`、`'[data-toc] a[data-toc-link]'`），
#    留着会让**每一页**都假红（实测 3 页起步，且随字段增加而扩散）。英语整句必然还会
#    命中其余的高置信词，召回损失可忽略。
EN_FUNC = {
    # 冠词 / 代词 / 限定词
    "the", "your", "you", "our", "we", "this", "that",
    "these", "those", "their", "them", "they", "his", "her", "my",
    # 介词 / 连词 / 否定 / 助动词
    "of", "to", "for", "with", "and", "or", "but", "if", "than", "from", "into",
    "not", "without", "about", "before", "after", "when", "where", "which",
    "while", "because", "is", "are", "was", "were", "been", "has", "have", "had",
    "will", "would", "can", "could", "should", "must", "does",
    # 英语独有、德语里不存在的功能/动作词（德语用 lesen/vergleichen/mehr/…）
    "see", "read", "pick", "picks", "tick", "open", "opens", "show", "shows",
    "find", "watch", "try", "need", "needs", "keep", "add", "adds", "set", "sets",
    "use", "uses", "more", "less", "other", "others", "all", "any", "some",
    "only", "also", "just", "let", "lets", "replace", "replaces",
    "replaced", "oldest", "third", "exactly", "shorter", "smaller", "cheaper",
    "cheapest", "matching", "matches", "match", "unlocks", "covers", "cover",
    "ranks", "listed", "shown", "recorded", "verified", "based", "each", "found",
    "page",
}
# 单 token 也能定的高置信「英语独有」词（用于只有 1 个 token 的短字面量）
# ⚠️ 刻意**不收** estimate / unlimited / per / link / installation —— 德语借词，
#    2026-10-11 实测它们造成 106 段正确德语被假红。
EN_STRONG = {
    "days", "day", "plans", "see", "read", "pick", "less", "more", "other",
    "review", "reviews", "cheapest", "cheaper", "compare", "matching",
    "provider", "providers", "countries", "country", "matches", "tick",
    "exactly", "trip", "provider",
}
# 德语特有标记：命中即**豁免**（哪怕同时含英文词 —— 那是德语正文里的借词）
DE_MARKERS = {
    "der", "die", "das", "den", "dem", "des", "und", "oder", "aber", "nicht",
    "kein", "keine", "keinen", "keinem", "keiner", "ist", "sind", "war", "waren",
    "sein", "bin", "bist", "wir", "sie", "du", "dein", "deine", "deinem",
    "deinen", "deiner", "deines", "ihr", "ihre", "unser", "unsere", "unseren",
    "unserem", "unseres", "für", "mit", "von", "vom", "im", "zum", "zur", "auf",
    "aus", "bei", "nach", "über", "unter", "vor", "durch", "gegen", "ohne", "um",
    "ein", "eine", "einen", "einem", "eines", "einer", "wenn", "wie", "was", "wo",
    "wer", "welche", "welcher", "auch", "nur", "noch", "mehr", "als", "pro", "ab",
    "an", "es", "hat", "haben", "wird", "werden", "kann", "können", "muss",
    "müssen", "soll", "sollen", "wähle", "wählen", "ansehen", "lesen",
    "vergleiche", "vergleichen", "tage", "tag", "tarif", "tarife", "preis",
    "preise", "anbieter", "länder", "land", "reise", "reisen", "günstig",
    "günstige", "günstigste", "günstigsten", "schätzung", "wahl", "passende",
    "weitere", "alle", "berechnete", "berechneten", "duell", "haken", "ersetzt",
    "älteste", "datenbedarf", "grenzen", "täglich", "tägliche", "versuche",
    "kürzere", "kleineren", "zwei", "genau", "seite", "gefunden", "startseite",
    "umweg", "roaming", "unterschied", "verringern", "erhöhen", "stunden",
    "kostenloses", "tool", "rechner", "verbrauch", "verbrauchsschätzer",
    # ⚠️ `in` / `an` / `ab` / `es` 是**德英同形**的介词/冠词 —— 德语里极常用
    #    （`5G-Netz in China, typisch 20-250 Mbit/s.` 曾被判红），列入豁免侧。
    #    代价是含 "in" 的英语短语（`Sign in`）会漏 —— 但那类短语必然还含别的
    #    高置信词，实际召回损失接近 0。
    "in", "typisch", "netz", "funktioniert", "funktionieren", "meinem",
    "smartphone",
}
LANG_MARKERS: dict[str, set[str]] = {"de": DE_MARKERS}
LANG_CHARS: dict[str, str] = {"de": "äöüßÄÖÜ"}

# 看起来像「路径 / URL / CSS 选择器」的字面量不参与 [1] 判据
# （2026-10-11 自检踩坑：`/img/flags/us.svg` 里的 `us` 被当成英语代词 `us`）
# ⚠️ 必须用 `search` 而不是 `match`：`match` 会把**整个**模式锚在位置 0，于是
#    交替分支 `://` 永远匹配不上 → `https://…` 被当文案（实测 `de/about` 假红）。
_NOT_COPY = re.compile(r"^\s*[/#.]|://|^\s*[a-z][a-z0-9+.\-]*://")
# head 里参与判据的元数据（顺序即报告顺序）
HEAD_META = [
    ("og:title", re.compile(r'<meta[^>]*property="og:title"[^>]*content="(.*?)"', re.S | re.I)),
    ("og:description", re.compile(r'<meta[^>]*property="og:description"[^>]*content="(.*?)"', re.S | re.I)),
    ("twitter:title", re.compile(r'<meta[^>]*name="twitter:title"[^>]*content="(.*?)"', re.S | re.I)),
    ("twitter:description", re.compile(r'<meta[^>]*name="twitter:description"[^>]*content="(.*?)"', re.S | re.I)),
    ("description", re.compile(r'<meta[^>]*name="description"[^>]*content="(.*?)"', re.S | re.I)),
]
TITLE_RE = re.compile(r"<title>(.*?)</title>", re.S | re.I)
LIT_RE = re.compile(r"""'(?:\\.|[^'\\\n])*'|"(?:\\.|[^"\\\n])*"|`(?:\\.|[^`\\])*`""")
SCRIPT_RE = re.compile(r"<script(?P<attrs>[^>]*)>(?P<body>.*?)</script>", re.S | re.I)
PATH_RE = re.compile(r"^/([a-z0-9][a-z0-9\-]*)/")
WORD_RE = re.compile(r"[A-Za-z][A-Za-z'\-]*")
HREFURL_RE = re.compile(r"/[a-z0-9][a-z0-9\-/]*")


def asset_segs() -> set[str]:
    """路径字面量的豁免首段 ——从 static/ 顶层**推导**，不写死。

    再加**各语言目录本身**：`{{ relLangURL "compare/" }}` 在德语页产出的就是
    `/de/compare/`（语言已经正确），不该被判为泄漏。
    """
    segs: set[str] = set()
    if STATIC.is_dir():
        segs |= {p.name for p in STATIC.iterdir() if p.is_dir()}
    _, langs = load_langs()
    segs |= {name for name, _ in langs}
    return segs


def _unescape(raw: str) -> str:
    return re.sub(r"\\(.)", r"\1", raw)


_TAG_RE = re.compile(r"<[a-zA-Z/][^>]*>")
_TAIL_TAG_RE = re.compile(r"<[a-zA-Z/][^>]*$")          # 被 `+` 截断的半截开标签
_VIS_ATTR_RE = re.compile(r'(?:aria-label|title|alt|placeholder)="([^"]*)"')
_ENTITY_RE = re.compile(r"&(?:minus|nbsp|amp|lt|gt|#\d+|#x[0-9a-fA-F]+);")


def copy_text(lit: str) -> str:
    """字面量 → 只保留**用户可见文本**（剥标签，但保留可见属性的值）。

    为什么：JS 里拼 HTML 的字符串把标签名、class 名、`aria-hidden` 一起带进来，
    直接按词判会把 `'<span class="…" aria-hidden="true">→</span></a>'` 判成英文
    （`a` / `true` 之类），实测让每一页都假红。
    """
    def repl(m: re.Match) -> str:
        vals = _VIS_ATTR_RE.findall(m.group(0))
        return " " + " ".join(vals) + " "

    s = _TAIL_TAG_RE.sub(" ", lit)
    s = _TAG_RE.sub(repl, s)
    return _ENTITY_RE.sub(" ", s)


def literals(script_body: str) -> list[str]:
    """取出脚本体里的字符串字面量（不含定界符、已去转义）。

    排除 **对象键**（`{"days": 7}` / `{'provider': 'x'}`）：键后紧跟 `:`、且键前是
    `{` / `,` / `(`。不加这条，德语页的数据 blob（`"days"` / `"provider"` 各成千上万次）
    会让判据被键名淹掉 —— 实测 `'days'` 一项就命中 59234 页。
    ⚠️ 三元表达式 `cond ? 'a' : 'b'` 的 `'a'` 前面是 `?`，不在排除集合里，不会被误当键。
    """
    out: list[str] = []
    for m in LIT_RE.finditer(script_body):
        # ⚠️ 只看前后各 8 字符的**有界窗口** —— 写 `script_body[m.end():]` 会退化成
        #    O(n²)：`tools/index.html` 的 blob 有 ~40 万字符，实测直接跑到超时。
        nxt = script_body[m.end():m.end() + 8].lstrip()[:1]
        if nxt == ":":
            prev = script_body[max(0, m.start() - 8):m.start()].rstrip()[-1:]
            if prev in "{,(":
                continue
        out.append(_unescape(m.group(0)[1:-1]))
    return out


def is_foreign_copy(text: str, lang: str) -> bool:
    """该文本是否是「译文页上的外语（英文）用户文案」。"""
    if _NOT_COPY.match(text):
        return False
    if any(c in text for c in LANG_CHARS.get(lang, "")):
        return False
    # 必须至少有一个小写字母：`AT&T` / `Country` / `GB` 这类无小写全大写/首字母大写
    # 的**专名或 schema 枚举**不该进判据（实测 `'AT&T'` 因 `at` 命中过）
    if not re.search(r"[a-z]", text):
        return False
    words = [w.lower() for w in WORD_RE.findall(text)]
    if not words:
        return False
    markers = LANG_MARKERS.get(lang, set())
    if any(w in markers for w in words):
        return False
    hits = [w for w in words if w in EN_FUNC]
    if len(words) >= 2 and hits:
        return True
    if len(words) == 1 and words[0] in EN_STRONG:
        return True
    return False


def foreign_paths(text: str, allowed: set[str]) -> list[str]:
    """站内绝对路径字面量（`/compare/…` 这种）。静态资源目录豁免。"""
    out: list[str] = []
    for piece in HREFURL_RE.findall(text):
        m = PATH_RE.match(piece)
        if not m or m.group(1) in allowed:
            continue
        if piece not in out:
            out.append(piece)
    return out


def scan_page(lang: str, body: str, allowed: set[str]) -> dict[str, list[str]]:
    """扫一页产物 → {'copy': [...], 'path': [...], 'head': [...]}。"""
    copy_hits: list[str] = []
    path_hits: list[str] = []
    head_hits: list[str] = []
    for m in SCRIPT_RE.finditer(body):
        attrs = m.group("attrs") or ""
        if "ld+json" in attrs:
            continue
        if "application/json" in attrs:
            continue
        for lit in literals(m.group("body")):
            if is_foreign_copy(copy_text(lit), lang):
                copy_hits.append(lit)
            for p in foreign_paths(lit, allowed):
                path_hits.append(p)
    for m in TITLE_RE.finditer(body):
        if is_foreign_copy(m.group(1), lang):
            head_hits.append("title: " + m.group(1))
    for label, rx in HEAD_META:
        for m in rx.finditer(body):
            if is_foreign_copy(m.group(1), lang):
                head_hits.append(f"{label}: {m.group(1)[:80]}")
    for m in re.finditer(
        r'<script[^>]*type="application/ld\+json"[^>]*>(.*?)</script>', body, re.S | re.I
    ):
        try:
            data = json.loads(m.group(1))
        except Exception:
            continue
        for s in _strings(data, skip_at=True):
            if is_foreign_copy(s, lang):
                head_hits.append("ld+json: " + s[:80])
    return {"copy": _uniq(copy_hits), "path": _uniq(path_hits), "head": _uniq(head_hits)}


def _uniq(xs: list[str]) -> list[str]:
    """同页同字面量只计一次 —— 对外报的是「页」，不是「出现次数」。

    ⚠ 实测（第八十一轮）：`de/tools/index.html` 有两个**独立拼装点**
    （`subUrl` / `countryUrl`）在去转义后都等于 `/compare/`，不去重就把
    46 页报成 47 页 —— 判据的**枚举口径**必须和它印出来的单位一致
    （红线 88 的又一同构形态）。
    """
    out: list[str] = []
    for x in xs:
        if x not in out:
            out.append(x)
    return out


_LD_SKIP_KEYS = {"@type", "@context"}


def _strings(node, skip_at: bool = False) -> list[str]:
    """收集 JSON-LD 里的字符串值。

    ⚠️ 只跳过 `@type` / `@context` 这两个**枚举键**（值是 `Country` / `BreadcrumbList` /
    `Question`，不是文案 —— 实测 `'ld+json: Country'` 在 170 页上假红）。

    ★ **不能按 `@` 前缀一刀切**：`@graph` 是**容器**不是枚举，`jsonify (dict "@context" …
    "@graph" (slice …))` 的整棵内容树都挂在它下面。第一版就是这么写的，于是
    `de/esim-providers/alosim` 里一个 14951 字符的 Product 节点**整片失明**，
    里面的 `"name": "aloSIM republic of ireland eSIM"`（英文残留）逃过判据 ——
    与红线 103 同构：**判据挖掉了什么，就看不见什么**。
    """
    if isinstance(node, str):
        return [node]
    if isinstance(node, list):
        return [x for n in node for x in _strings(n, skip_at)]
    if isinstance(node, dict):
        return [
            x
            for k, v in node.items()
            if not (skip_at and str(k) in _LD_SKIP_KEYS)
            for x in _strings(v, skip_at)
        ]
    return []


def load_langs() -> tuple[str, list[tuple[str, str]]]:
    """→ (默认语言, [(语言, 该语言产物目录相对前缀)])，从 hugo.toml 推导。"""
    with open(CONFIG, "rb") as fh:
        cfg = tomllib.load(fh)
    default = cfg.get("defaultContentLanguage", "en")
    in_subdir = bool(cfg.get("defaultContentLanguageInSubdir", False))
    langs: list[tuple[str, str]] = []
    for name in sorted(cfg.get("languages", {})):
        langs.append((name, "" if (name == default and not in_subdir) else name + "/"))
    return default, langs


def lang_of(rel: str, langs: list[tuple[str, str]]) -> str | None:
    """产物相对路径 → 语言；默认语言产物在根，返回 None（不扫 —— 它印英文是对的）。"""
    head = rel.split("/", 1)[0]
    for name, prefix in langs:
        if name == head and prefix:
            return name
    return None


KINDS = [("copy", "[1] 英文残留 · 脚本体"), ("path", "[2] 站内路径字面量"), ("head", "[3] 英文残留 · head 元数据")]


def scan() -> int:
    if not PUBLIC.is_dir():
        print("ERROR public/ 不存在 —— 先跑 npm run build")
        return 1
    default, langs = load_langs()
    targets = [x for x in langs if x[1]]
    allowed = asset_segs()
    print(f"  语言：默认 {default}；译文站产物目录 {[p for _, p in targets] or '（无）'}")
    print(f"  静态资源目录（路径字面量豁免）：{sorted(allowed)}")
    if not targets:
        print("  没有译文站产物目录 —— 本层无对象。")
        return 0
    unregistered = [n for n, _ in targets if n not in LANG_MARKERS]
    if unregistered:
        print(
            f"  ERROR 语言 {unregistered} 未登记特有词表 LANG_MARKERS —— 本层对它**没有任何"
            f"判据**。请先补词表，不要让它静默通过。"
        )
        return 1

    by_lit: dict[tuple[str, str], list[str]] = {}
    pages = 0
    counts = {"copy": 0, "path": 0, "head": 0}
    for p in sorted(PUBLIC.rglob("*.html")):
        rel = p.relative_to(PUBLIC).as_posix()
        lang = lang_of(rel, langs)
        if not lang:
            continue
        pages += 1
        res = scan_page(lang, p.read_text(encoding="utf-8", errors="replace"), allowed)
        for kind in counts:
            for lit in res[kind]:
                counts[kind] += 1
                by_lit.setdefault((kind, lit), []).append(rel)

    print(f"  扫描译文站 HTML {pages} 页")
    for kind, label in KINDS:
        print(f"  {label}：{counts[kind]} 处")
    if not by_lit:
        print("\nOK: 译文站 <script> 层与 head 元数据无英文残留、无站内路径字面量")
        return 0

    print()
    for kind, label in KINDS:
        rows = [(lit, w) for (k, lit), w in by_lit.items() if k == kind]
        if not rows:
            continue
        print(f"  ── {label} ──")
        for lit, where in sorted(rows, key=lambda kv: (-len(kv[1]), kv[0]))[:25]:
            print(f"    ✗ {lit!r}  （{len(where)} 页，例：{where[0]}）")
    total = sum(counts.values())
    print(f"\nFAIL: {len(by_lit)} 条可疑字面量 / {total} 处命中")
    return 1


def selftest() -> int:
    """注入反例自测 —— 两个方向都要证明：正例不误伤、反例必红。"""
    allowed = {"img", "css"}
    good_script = (
        "<script>"
        "var a = 'Wähle zwei Anbieter';"
        "var b = 'Kein Tarif passt — versuche eine kürzere Reise';"
        "var c = '<div class=\"card p-6 text-sm text-ink-500\">Weitere passende Tarife</div>';"
        "var d = 'Unlimited';"                       # 德语借词，不得报
        "var e = 'btn-primary';"
        "var f = '#calc-need .chip';"
        "var g = '/img/flags/us.svg';"               # 静态资源 + `us` 陷阱
        "var h = 'pointer-events-none opacity-50';"
        "var i = 'data-key';"
        "var j = 'Deine Schätzung · ';"
        "</script>"
    )
    bad_copy = (
        "<script>"
        "var a = 'Pick two providers';"
        "var b = 'Compare ' + x + ' vs ' + y + ' →';"
        "var c = '<p class=\"text-xs\">Other matching plans</p>';"
        "var d = 'days';"
        "var e = 'Read ' + p + ' review';"
        "</script>"
    )
    bad_path = (
        "<script>"
        "var u = '/compare/' + slug + '/';"
        "var v = '/esim-providers/' + key + '/';"
        "</script>"
    )
    # 同一页、同一字面量在两个拼装点各出现一次 → 仍只算 **1 页 / 1 处**
    # （去重口径的反例；真身见 de/tools/index.html 的 subUrl + countryUrl）
    bad_path_dup = (
        "<script>"
        "var u = '/compare/' + slug + '/' + k + '/';"
        "var v = '/compare/' + slug + '/';"
        "</script>"
    )
    jsonld = (
        '<script type="application/ld+json">'
        '{"@type":"BreadcrumbList","itemListElement":'
        '[{"name":"Startseite"},{"name":"404 Page not found"}]}</script>'
    )
    good_head = (
        '<title>Beste Argentinien eSIM 2026: Tarife für Reisende</title>'
        '<meta property="og:title" content="Wähle zwei Anbieter">'
    )
    failed = 0
    cases = [
        ("good-copy", good_script, {"copy": 0, "path": 0, "head": 0}),
        # 6 处（不是 5）：`'Read ' + p + ' review'` 被 `+` 拆成两个字面量，
        # 而 `check_i18n.py` 的长度下限（≥14 字符）**两个都看不见** —— 这正是本守卫的补位点
        ("bad-copy", bad_copy, {"copy": 6, "path": 0, "head": 0}),
        ("bad-path", bad_path, {"copy": 0, "path": 2, "head": 0}),
        ("bad-path-dup", bad_path_dup, {"copy": 0, "path": 1, "head": 0}),
        ("jsonld", jsonld, {"copy": 0, "path": 0, "head": 1}),
        ("good-head", good_head, {"copy": 0, "path": 0, "head": 0}),
    ]
    for name, body, want in cases:
        got = {k: len(v) for k, v in scan_page("de", body, allowed).items()}
        ok = got == want
        failed += 0 if ok else 1
        print(f"  {'OK  ' if ok else 'MISS'} {name}: 期望 {want}，实得 {got}")
        if not ok:
            print(f"       命中：{scan_page('de', body, allowed)}")

    # 默认语言页的豁免发生在 lang_of()，不是 scan_page() —— 测在这一层
    _, langs = load_langs()
    for rel, want in (("de/tools/index.html", "de"), ("tools/index.html", None),
                      ("de/404.html", "de"), ("404.html", None)):
        got = lang_of(rel, langs)
        ok = got == want
        failed += 0 if ok else 1
        print(f"  {'OK  ' if ok else 'MISS'} lang_of({rel!r}) = {got!r}（期望 {want!r}）")

    # 未登记语言必须**显式失败**，不能静默放过
    ok = "zz" not in LANG_MARKERS
    failed += 0 if ok else 1
    print(f"  {'OK  ' if ok else 'MISS'} 未登记语言保护：LANG_MARKERS 无 'zz' -> {ok}")

    print(f"\n自测{'通过' if not failed else f'失败 {failed} 项'}")
    return 1 if failed else 0


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--selftest", action="store_true")
    ap.add_argument(
        "--root",
        metavar="DIR",
        help="改扫别的产物目录（默认 public/）。**新判据必须先对改造前的快照跑一遍**："
             "把旧产物放到 .buildlog/pub_r81_pre 后 `--root .buildlog/pub_r81_pre`，"
             "应当**红**；红了才证明这条判据真的能发现该缺陷。",
    )
    args = ap.parse_args()
    if args.root:
        global PUBLIC
        PUBLIC = Path(args.root).resolve()
    return selftest() if args.selftest else scan()


if __name__ == "__main__":
    sys.exit(main())
