#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""lang_new_audit.py —— 新语言「就位度」体检（**只读**，不写任何文件）。

为什么需要它
    本站已跑通 en（默认）+ de 双语。要上第 3 种语言时，最容易出的不是「报错」，
    而是**静默降级**：`contentDir` 忘写 → /fr/ 里全是英文页；`data/fr/` 少了几个键
    → 那几句渲染回英文；`i18n/fr.toml` 少了 key → 构建直接失败（这条反而是好的）。
    这五种「沉默的错」有四种不会让构建失败。本脚本把它们逐层摆出来。

设计原则
    · **只读**：不创建、不修改、不删除任何文件。
    · **不抄第二份规则**：语言列表从 `hugo.toml` 读（与 `scripts/lang_rules.py` 同源），
      不在本文件里维护语言白名单。
    · **缺失即报告，不自行修复**：输出「下一步该做什么」的清单，动手交给人。
    · 退出码：0 = 该语言已就位（或仅剩内容翻译）；1 = 结构性缺口；2 = 用法错误。

用法
    python -X utf8 scripts/lang_new_audit.py fr                  # 体检法语
    python -X utf8 scripts/lang_new_audit.py fr --repo D:/x/y    # 指定仓库根
    python -X utf8 scripts/lang_new_audit.py --selftest          # 自检（正例 + 反例）

配套文档：`docs/add-a-language.md`（逐文件操作手册）
"""
from __future__ import annotations

import argparse
import io
import re
import sys
import tempfile
import tomllib
from pathlib import Path

# --------------------------------------------------------------------------- 基础设施

DEFAULT_LANG = "en"
LINE_KV = re.compile(r"^([A-Za-z0-9_]+)\s*=", re.M)
LANGCODE_OK = re.compile(r"^[a-z]{2,3}(-[A-Za-z]{2,4})?$")
# Hugo shortcode `{{< … >}}` / `{{% … %}}` —— 合法且会被 Hugo 替换，判「模板残留」时必须挖掉
SHORTCODE = re.compile(r"\{\{[<%][\s\S]*?[>%]\}\}")

# 需要为每种语言单独提供一份的 data 覆盖文件（缺哪个报哪个）
DATA_FILES = [
    ("countries.toml", "50 国国名（卡片 / H1 / 正文里的国名）"),
    ("providers.toml", "品牌档案 tagline / strengths / weaknesses / policy.* / promo_*"),
    ("carriers.toml", "运营商 profile 的 note + detail[].strong/.weak"),
    ("networkreports.toml", "Opensignal 事实 + Ookla 说明 + opensignal_date"),
    ("strings.toml", "fup_note / promo_label / info.support / info.refund / quirks / devices"),
    ("titlesegments.toml", "国家页 <title> 片段"),
]

# content/<lang>/ 下与英语侧必须逐目录对齐的栏目
CONTENT_DIRS = ["compare", "esim-deals", "esim-providers", "guides", "networks", "research", "tools"]

# 名字/逻辑绑定 de 的守卫 —— 新语言在它们眼里「不存在」（不报错，是看不见）
DE_ONLY_GUARDS = [
    ("scripts/verify_de_text.py", "数据层英文文案本地化守卫（判据 A–J 全德语）"),
    ("scripts/verify_de_data.py", "data/de 覆盖层逐字段守卫"),
    ("scripts/_de_schema_audit.py", "JSON-LD 8 条判据（de↔en 同路径对比）"),
    ("scripts/_de_link_leak_audit.py", "译文页站内链接语言泄漏 + 畸形 href"),
    ("scripts/check_inline_copy.py", "内联 JS 英文残留（LANG_MARKERS 只列 de）"),
    ("scripts/check_faq_facts.py", "FAQ 数字对账（KIND_OF_LANG 只有 en/de）"),
    ("scripts/check_printf_arity.py", "printf 格式串参数个数（\"de\" 块）"),
    ("scripts/check_headings_source.py", "标题标点（selftest 按 en/de 分派）"),
]


class Report:
    """收集问题：OK / WARN / FAIL 三级，FAIL 决定退出码。

    note 与 warn 的区别：note = 「操作提示」（永远不阻塞），warn = 「不处理会降低质量」。
    """

    def __init__(self, lang: str, silent: bool = False) -> None:
        self.lang = lang
        self.silent = silent
        self.fails: list[str] = []
        self.warns: list[str] = []

    def layer(self, title: str) -> None:
        if not self.silent:
            print(f"\n── {title} " + "─" * max(0, 62 - len(title)))

    def ok(self, msg: str) -> None:
        if not self.silent:
            print(f"  [OK]   {msg}")

    def note(self, msg: str) -> None:
        """操作提示 —— 不计入 warns，不会让结论变成「未就位」。"""
        if not self.silent:
            print(f"  [note] {msg}")

    def warn(self, msg: str) -> None:
        if not self.silent:
            print(f"  [WARN] {msg}")
        self.warns.append(msg)

    def fail(self, msg: str) -> None:
        if not self.silent:
            print(f"  [FAIL] {msg}")
        self.fails.append(msg)


# --------------------------------------------------------------------------- 各层检查


def read_toml(path: Path) -> dict:
    try:
        with path.open("rb") as fh:
            return tomllib.load(fh)
    except Exception:
        return {}


def i18n_keys(path: Path) -> list[str]:
    """按出现顺序返回 key 列表（值可能含转义，行级解析即可）。"""
    if not path.exists():
        return []
    return LINE_KV.findall(path.read_text(encoding="utf-8", errors="replace"))


def rel_md_set(root: Path) -> set[str]:
    if not root.exists():
        return set()
    return {str(p.relative_to(root)).replace("\\", "/") for p in root.rglob("*.md")}


def check_l0(repo: Path, lang: str, rep: Report) -> dict:
    rep.layer("L0 声明层 · hugo.toml")
    path = repo / "hugo.toml"
    doc = read_toml(path)
    if not doc:
        rep.fail("hugo.toml 读不出来（不存在或不是合法 TOML）")
        return {}

    langs = doc.get("languages", {}) or {}
    default_lang = doc.get("defaultContentLanguage", DEFAULT_LANG)
    in_subdir = str(doc.get("defaultContentLanguageInSubdir", False)).lower() == "true"

    if lang not in langs:
        rep.fail(f"hugo.toml 里没有 [languages.{lang}] —— 语言未注册，产物为 0")
        return {"declared": False}

    block = langs[lang] or {}
    rep.ok(f"[languages.{lang}] 已声明（weight={block.get('weight', '?')}）")

    code = block.get("languageCode", "")
    if not code:
        rep.fail("缺 languageCode —— hreflang 与 og:locale 会拿到空值")
    elif not LANGCODE_OK.match(code):
        rep.warn(f"languageCode = {code!r} 形态可疑（惯例 xx-yy，如 fr-fr；直接喂 hreflang 与 og:locale）")
    else:
        rep.ok(f"languageCode = {code}（→ hreflang=\"{code}\"，og:locale={code.split('-')[0]}_{code.split('-')[-1].upper()}）")

    if not block.get("languageName"):
        rep.warn("缺 languageName —— 语言切换器会显示语言代码")
    else:
        rep.ok(f"languageName = {block['languageName']}")

    cdir = block.get("contentDir", "")
    if not cdir:
        rep.fail(
            "★ 缺 contentDir —— Hugo 会静默把默认语言的内容目录也当成该语言，"
            "新语言页全是英文且**构建不报错**（已知最难查的一种）"
        )
    elif cdir != f"content/{lang}":
        rep.warn(f"contentDir = {cdir!r}，与惯例 content/{lang} 不一致（确认是有意为之）")
    else:
        rep.ok(f"contentDir = {cdir}")

    params = block.get("params", {}) or {}
    for k in ("tagline", "description"):
        if k in params:
            rep.ok(f"[languages.{lang}.params].{k} 已覆盖")
        else:
            rep.fail(f"缺 [languages.{lang}.params].{k} —— 该语言页的 meta description / 页脚标语会印英文")

    for other in langs:
        if other != lang and (langs[other] or {}).get("contentDir") == cdir:
            rep.fail(f"contentDir 与 [languages.{other}] 重复（{cdir}）—— 两个语言会渲染同一批内容")

    if in_subdir:
        rep.warn("defaultContentLanguageInSubdir = true —— 默认语言会落到 /en/，已收录 URL 全变（上线站请确认这是有意为之）")
    else:
        rep.ok("defaultContentLanguageInSubdir = false（英文留在根路径，既有 URL 零变更）")

    # robots.txt 的 sitemap 声明（硬编码点，加语言必须手改）
    robots = repo / "layouts" / "robots.txt"
    if robots.exists():
        txt = robots.read_text(encoding="utf-8", errors="replace")
        if re.search(rf"Sitemap:\s*\{{\{{[^}}]*\}}\}}{re.escape(lang)}/sitemap\.xml", txt):
            rep.ok(f"layouts/robots.txt 已声明 {lang}/sitemap.xml")
        else:
            rep.fail(
                f"layouts/robots.txt 未声明 {lang}/sitemap.xml —— "
                "该行是手写的（不在 hugo.toml 里），加语言必须手动加一行"
            )
    else:
        rep.warn("layouts/robots.txt 不存在（跳过 sitemap 声明检查）")

    return {
        "declared": True,
        "default_lang": default_lang,
        "in_subdir": in_subdir,
        "prefix": "" if (lang == default_lang and not in_subdir) else f"{lang}/",
    }


def check_l1(repo: Path, lang: str, rep: Report) -> None:
    rep.layer("L1 界面词表层 · i18n/")
    en_p, xx_p = repo / "i18n" / "en.toml", repo / "i18n" / f"{lang}.toml"
    if not xx_p.exists():
        rep.fail(f"缺 i18n/{lang}.toml —— check_i18n.py 会直接判构建失败（先 cp i18n/en.toml i18n/{lang}.toml）")
        return

    en_keys, xx_keys = i18n_keys(en_p), i18n_keys(xx_p)
    en_set, xx_set = set(en_keys), set(xx_keys)
    rep.ok(f"i18n/{lang}.toml 存在：{len(xx_keys)} key（对照 en {len(en_keys)}）")

    missing, extra = en_set - xx_set, xx_set - en_set
    if missing:
        rep.fail(f"缺 {len(missing)} 个 key（前 3：{sorted(missing)[:3]}）—— 构建会失败")
    if extra:
        rep.fail(f"多 {len(extra)} 个 key（前 3：{sorted(extra)[:3]}）—— 构建会失败")

    # 顺序：只报首个错位位置（后面会连锁，报全部没意义）
    if not missing and not extra and en_keys != xx_keys:
        for i, (a, b) in enumerate(zip(en_keys, xx_keys)):
            if a != b:
                rep.warn(f"★ key 顺序不一致（第 {i + 1} 项：en={a!r} vs {lang}={b!r}）—— check_i18n 只校验集合，顺序靠纪律；顺序乱了 diff 就废了")
                break

    # 未译比例（值 == 英文原值即视为未译；专有名词会误判约 3%，不影响「还剩多少」）
    en_val = dict(re.findall(r'^([A-Za-z0-9_]+)\s*=\s*"(.*)"\s*$', en_p.read_text(encoding="utf-8"), re.M))
    xx_val = dict(re.findall(r'^([A-Za-z0-9_]+)\s*=\s*"(.*)"\s*$', xx_p.read_text(encoding="utf-8"), re.M))
    same = sum(1 for k, v in xx_val.items() if en_val.get(k) == v)
    if xx_val:
        pct = 100.0 * (len(xx_val) - same) / len(xx_val)
        msg = f"已译约 {pct:.1f}%（{len(xx_val) - same}/{len(xx_val)}；同形专有名词会误判约 3%）"
        (rep.ok if pct > 99 else rep.warn)(msg)
    rep.note(f"下一步：python -X utf8 scripts/i18n_coverage.py {lang}    # 看未译清单")


def check_l2(repo: Path, lang: str, rep: Report) -> None:
    rep.layer("L2 数据覆盖层 · data/")
    data_en, data_xx = repo / "data", repo / "data" / lang
    if not data_xx.exists():
        rep.fail(f"缺 data/{lang}/ —— 数据层的内建英文句子会原样印在该语言页上（**构建不报错**）")
        return

    for fname, what in DATA_FILES:
        p = data_xx / fname
        if p.exists():
            # 顶层键数（countries/titlesegments 是 ISO 表；其余是品牌/结构表）
            doc = read_toml(p)
            rep.ok(f"data/{lang}/{fname} 存在（{len(doc)} 个顶层键）— {what}")
        else:
            rep.fail(f"缺 data/{lang}/{fname} — {what}")

    # countries：ISO 集合必须与英语侧一致
    en_c = read_toml(data_en / "countries.toml")
    xx_c = read_toml(data_xx / "countries.toml")
    if en_c:
        miss = set(en_c) - set(xx_c)
        if miss:
            rep.fail(f"data/{lang}/countries.toml 缺 {len(miss)} 个 ISO（{sorted(miss)[:5]}）—— 这些国家的国名会回退英文")
        elif xx_c:
            rep.ok(f"countries.toml ISO 覆盖完整（{len(xx_c)}/{len(en_c)}）")

    # faqs：文件名 = 小写 ISO，必须逐国对齐
    en_f, xx_f = data_en / "faqs", data_xx / "faqs"
    if en_f.exists():
        if not xx_f.exists():
            rep.fail(f"缺 data/{lang}/faqs/ —— 所有国家的 FAQ 会整段印英文")
        else:
            a = {p.stem for p in en_f.glob("*.toml")}
            b = {p.stem for p in xx_f.glob("*.toml")}
            m = a - b
            if m:
                rep.fail(f"data/{lang}/faqs/ 缺 {len(m)} 个文件（{sorted(m)[:5]}）—— 这些国家的 FAQ 印英文")
            else:
                rep.ok(f"faqs/ 覆盖完整（{len(b)}/{len(a)}，文件名 = 小写 ISO）")
            bad = [p.name for p in xx_f.glob("*.toml") if p.stem != p.stem.lower()]
            if bad:
                rep.warn(f"faqs/ 有非小写 ISO 文件名：{bad[:3]}（模板按 lower(iso) 取，会静默取不到）")

    rep.note("★ 深合并语义：map 递归、**数组整体替换** —— 覆盖数组必须整段重写并把机器字段带上")


def check_l3(repo: Path, lang: str, rep: Report) -> None:
    rep.layer("L3 内容本体层 · content/")
    c_en, c_xx = repo / "content" / DEFAULT_LANG, repo / "content" / lang
    if not c_xx.exists():
        rep.fail(f"缺 content/{lang}/ —— 该语言一个页面都不会产出")
        return

    en_all, xx_all = rel_md_set(c_en), rel_md_set(c_xx)
    rep.ok(f"content/{lang}/ 有 {len(xx_all)} 个 .md（对照 en {len(en_all)}）")

    for d in CONTENT_DIRS:
        a = {p for p in en_all if p.startswith(d + "/")}
        b = {p for p in xx_all if p.startswith(d + "/")}
        if not a:
            continue
        if len(b) == len(a):
            rep.ok(f"{d}/: {len(b)}/{len(a)} 对齐")
        elif not b:
            rep.fail(f"{d}/: 0/{len(a)} —— 整栏目缺失（导航会回退英文页）")
        else:
            miss = sorted(a - b)
            rep.fail(f"{d}/: {len(b)}/{len(a)}，缺 {len(miss)}（前 3：{miss[:3]}）")

    root_a = {p for p in en_all if "/" not in p}
    root_b = {p for p in xx_all if "/" not in p}
    if len(root_b) != len(root_a):
        rep.fail(f"根页: {len(root_b)}/{len(root_a)}，缺 {sorted(root_a - root_b)[:5]}")
    else:
        rep.ok(f"根页: {len(root_b)}/{len(root_a)} 对齐（_index / about / contact / disclosure / methodology / privacy / terms）")

    extra = sorted(xx_all - en_all)
    if extra:
        rep.warn(f"content/{lang}/ 有 {len(extra)} 个英语侧不存在的页（前 3：{extra[:3]}）—— 不会有译文配对，也无法互切语言")

    # 正文里不该有**未被 Hugo 处理**的模板定界符。
    # ★ 必须挖掉 shortcode `{{< … >}}` / `{{% … %}}` —— 它们是合法且会被 Hugo 替换的。
    #   实测（2026-10-11）：content/de 有 68 个正文文件含 `{{`，**全部是 shortcode
    #   （`{{< count-countries >}}` 这类），真残留 0**；不加这层豁免会一次假红 68 页。
    #   与 check_output.py 判据 4 同源 —— 它扫**产物**，shortcode 已展开故不需豁免。
    bad = []
    for p in sorted(c_xx.rglob("*.md")):
        t = SHORTCODE.sub("", p.read_text(encoding="utf-8", errors="replace"))
        if "{{" in t:
            bad.append(str(p.relative_to(c_xx)))
    if bad:
        rep.fail(f"{len(bad)} 个正文含未被处理的 '{{{{'（前 3：{bad[:3]}）—— Markdown 不解析模板，会原样印给读者")
    else:
        rep.ok("正文无未渲染的模板定界符（shortcode 已豁免）")

    # noindex 开关（只看 front matter，不看正文里的同名字样）
    noindex = 0
    for p in sorted(c_xx.rglob("*.md")):
        txt = p.read_text(encoding="utf-8", errors="replace")
        m = re.match(r"^---\r?\n(.*?)\r?\n---", txt, re.S)
        if m and re.search(r"^noindex:\s*true", m.group(1), re.M):
            noindex += 1
    if noindex:
        rep.warn(f"{noindex} 页仍带 noindex: true（未完成标记；解禁前必须先关掉两个生成器的 NOINDEX 开关）")
    else:
        rep.ok("无 noindex 页（该语言已全量提交索引）")
    rep.note("正文里的站内链接必须手写 /<lang>/ 前缀 —— 正文不过模板管线，relLangURL 在这里无效")


def check_l4(repo: Path, lang: str, rep: Report) -> None:
    rep.layer("L4 守卫层 · scripts/")

    # 生成器的语言白名单（硬编码点）
    for script, pat in (
        ("scripts/gen_provider_pages.py", r'if\s+LANG\s+not\s+in\s+\(([^)]*)\)'),
        ("scripts/gen_vs_pages.py", r'if\s+LANG\s+not\s+in\s+\(([^)]*)\)'),
    ):
        p = repo / script
        if not p.exists():
            rep.note(f"{script} 不存在（跳过）")
            continue
        m = re.search(pat, p.read_text(encoding="utf-8", errors="replace"))
        if not m:
            rep.warn(f"{script}：找不到 LANG 白名单（可能已参数化，请人工确认）")
        elif f'"{lang}"' in m.group(1):
            rep.ok(f"{script}：LANG 白名单已含 {lang}")
        else:
            rep.fail(f"{script}：LANG 白名单 {m.group(1).strip()} 不含 {lang} —— 跑 --lang {lang} 会直接 sys.exit")

    # lang_rules 的 DASH_OK
    p = repo / "scripts" / "lang_rules.py"
    if p.exists():
        m = re.search(r"DASH_OK\s*=\s*\{([^}]*)\}", p.read_text(encoding="utf-8", errors="replace"))
        if m and f'"{lang}"' in m.group(1):
            rep.ok(f"lang_rules.py：DASH_OK 含 {lang}（标题允许破折号）")
        elif m:
            rep.warn(f"lang_rules.py：DASH_OK 不含 {lang} —— 该语言标题按英文口径禁破折号（若不符合该语言排版习惯，加进去）")

    # de 专用守卫
    hit = [g for g, _ in DE_ONLY_GUARDS if (repo / g).exists()]
    if lang != "de" and hit:
        rep.note(
            f"以下 {len(hit)} 个守卫**绑定 de**，{lang} 页在它们眼里不存在（不报错，是看不见）："
        )
        for g, what in DE_ONLY_GUARDS:
            if (repo / g).exists():
                rep.note(f"    · {g} — {what}")
        rep.warn(
            f"★ 建议先把这 {len(hit)} 个守卫改成 --lang 参数化，再开始翻译内容 —— "
            "否则你会在「守卫全绿但页面全是英文」的假安全里工作"
        )
    else:
        rep.ok("通用守卫（check_i18n / check_hreflang / check_dates / check_output / verify_no_regression / check_css_sync / check_links / lang_rules / check_hardcoded）自动覆盖该语言")


def check_l5(repo: Path, lang: str, prefix: str, rep: Report) -> None:
    rep.layer("L5 产物层 · public/（未构建则跳过）")
    pub = repo / "public"
    out = pub / prefix.rstrip("/") if prefix else pub
    if not pub.exists() or not out.exists():
        rep.note("public/ 下还没有该语言的产物 —— 跑 `npm run build` 后再看这一层（注意：一律别加管道取退出码）")
        return

    htmls = sorted(out.rglob("*.html"))
    rep.ok(f"public/{prefix}: {len(htmls)} 个 HTML")

    noidx = sum(1 for p in htmls if re.search(r'<meta\s+name="robots"\s+content="[^"]*noindex', p.read_text(encoding="utf-8", errors="replace")))
    (rep.warn if noidx else rep.ok)(f"noindex 页 {noidx} 个" + ("（未完成标记，解禁前别提交索引）" if noidx else ""))

    sm = out / "sitemap.xml"
    if sm.exists():
        n = len(re.findall(r"<loc>", sm.read_text(encoding="utf-8", errors="replace")))
        (rep.ok if n else rep.warn)(f"sitemap.xml 有 {n} 条（noindex 页不应出现）")
    else:
        rep.warn("该语言没有 sitemap.xml（Hugo 只为已声明语言产出，确认 L0 是否生效）")

    # 站内链接语言泄漏：不带 hreflang 的 <a href> 指向站内时必须落在该语言前缀下
    leak = 0
    sample = ""
    for p in htmls[:200]:
        body = p.read_text(encoding="utf-8", errors="replace")
        body = re.sub(r"<(script|style)\b.*?</\1>", "", body, flags=re.S | re.I)
        for m in re.finditer(r'<a\s[^>]*href="(/[^"]*)"[^>]*>', body):
            tag, href = m.group(0), m.group(1)
            if "hreflang" in tag:
                continue          # 语言切换器天然指向另一语言
            if href.startswith("//") or not href.startswith("/"):
                continue
            if not href.startswith("/" + prefix.rstrip("/")):
                leak += 1
                if not sample:
                    sample = f"{p.relative_to(pub)} → {href}"
    if leak:
        rep.fail(f"抽样 {min(200, len(htmls))} 页发现 {leak} 处站内链接语言泄漏（例：{sample}）—— 读者会被送到默认语言站")
    else:
        rep.ok(f"抽样 {min(200, len(htmls))} 页：站内链接无语言泄漏")


# --------------------------------------------------------------------------- selftest


MINI = {
    "hugo.toml": """baseURL = "https://example.com/"
defaultContentLanguage = "en"
defaultContentLanguageInSubdir = false

[languages.en]
  languageCode = "en-us"
  languageName = "English"
  contentDir = "content/en"
  weight = 1

[languages.zz]
  languageCode = "zz-zz"
  languageName = "Zzz"
  contentDir = "content/zz"
  weight = 2

[languages.zz.params]
  tagline = "T"
  description = "D"
""",
    "i18n/en.toml": 'a = "A"\nb = "B"\n',
    "i18n/zz.toml": 'a = "A"\nb = "B"\n',
    "layouts/robots.txt": "Sitemap: {{ .Site.BaseURL }}sitemap.xml\nSitemap: {{ .Site.BaseURL }}zz/sitemap.xml\n",
    "data/countries.toml": '[JP]\nname = "Japan"\n',
    "data/faqs/jp.toml": "[[faq]]\nq = \"Q\"\n",
    "data/zz/countries.toml": '[JP]\nname = "Nippon"\n',
    "data/zz/faqs/jp.toml": "[[faq]]\nq = \"F\"\n",
    "content/en/_index.md": "---\ntitle: T\n---\n",
    "content/en/compare/_index.md": "---\ntitle: T\n---\n",
    "content/zz/_index.md": "---\ntitle: T\n---\n",
    "content/zz/compare/_index.md": "---\ntitle: T\n---\n",
}
for f in DATA_FILES:
    if f[0] == "countries.toml":
        continue          # 上面已显式给过（[JP]），用于 ISO 对齐的正例
    MINI[f"data/zz/{f[0]}"] = '[X]\nk = "v"\n'


def build_mini(root: Path, mutate=None) -> None:
    files = dict(MINI)
    if mutate:
        mutate(files)
    for rel, text in files.items():
        p = root / rel
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_bytes(text.encode("utf-8"))


def run_audit(repo: Path, lang: str, quiet: bool = False) -> tuple[int, Report]:
    rep = Report(lang, silent=quiet)
    if not quiet:
        print(f"新语言就位度体检 —— lang={lang!r}  repo={repo}")
    l0 = check_l0(repo, lang, rep)
    if not l0.get("declared"):
        return 1, rep
    check_l1(repo, lang, rep)
    check_l2(repo, lang, rep)
    check_l3(repo, lang, rep)
    check_l4(repo, lang, rep)
    check_l5(repo, lang, l0.get("prefix", f"{lang}/"), rep)
    return (1 if rep.fails else 0), rep


def selftest() -> int:
    """两侧都证：干净仓库必须过，逐条反例必须红。"""
    print("=== selftest：新语言体检脚本 ===")
    bad = 0
    with tempfile.TemporaryDirectory(prefix="langaudit-") as td:
        root = Path(td)

        # 正例
        build_mini(root)
        code, rep = run_audit(root, "zz", quiet=True)
        ok = code == 0 and not rep.fails
        print(f"  {'OK  ' if ok else 'MISS'} 正例（完整迷你仓）        fails={len(rep.fails)} warns={len(rep.warns)}")
        if not ok:
            bad += 1
            for f in rep.fails:
                print(f"        意外 FAIL: {f}")

        # 反例：逐个破坏一项，断言「必须 FAIL」
        def drop_countries(files):
            del files["data/zz/countries.toml"]

        def drop_contentdir(files):
            files["hugo.toml"] = files["hugo.toml"].replace('contentDir = "content/zz"\n', "")

        def drop_robots(files):
            files["layouts/robots.txt"] = "Sitemap: {{ .Site.BaseURL }}sitemap.xml\n"

        def drop_i18n_key(files):
            files["i18n/zz.toml"] = 'a = "A"\n'

        def drop_params(files):
            files["hugo.toml"] = files["hugo.toml"].replace('[languages.zz.params]\n  tagline = "T"\n  description = "D"\n', "")

        def drop_content_dir(files):
            del files["content/zz/compare/_index.md"]

        def drop_faqs(files):
            del files["data/zz/faqs/jp.toml"]

        def put_template_in_body(files):
            files["content/zz/_index.md"] = "---\ntitle: T\n---\n\n{{/* TODO */}}\n"

        cases = [
            ("删掉 data/zz/countries.toml", drop_countries, "countries.toml"),
            ("删掉 contentDir", drop_contentdir, "contentDir"),
            ("robots.txt 去掉 zz sitemap", drop_robots, "sitemap.xml"),
            ("i18n 少一个 key", drop_i18n_key, "缺 1 个 key"),
            ("删掉 languages.zz.params", drop_params, "params"),
            ("content/zz 少一页", drop_content_dir, "compare/"),
            ("删掉一个 faq 文件", drop_faqs, "faqs/"),
            ("正文里写 {{ }}", put_template_in_body, "{{"),
        ]
        for label, mutate, needle in cases:
            with tempfile.TemporaryDirectory(prefix="langaudit-neg-") as td2:
                r2 = Path(td2)
                build_mini(r2, mutate)
                c2, rep2 = run_audit(r2, "zz", quiet=True)
                hit = c2 == 1 and any(needle in f for f in rep2.fails)
                print(f"  {'OK  ' if hit else 'MISS'} 反例：{label:<28} exit={c2} 命中={hit}")
                if not hit:
                    bad += 1
                    print(f"        期望 FAIL 含 {needle!r}，实得：{rep2.fails[:2]}")

        # 反例：语言未注册
        with tempfile.TemporaryDirectory(prefix="langaudit-neg2-") as td3:
            r3 = Path(td3)
            build_mini(r3)
            c3, _ = run_audit(r3, "qq", quiet=True)
            hit = c3 == 1
            print(f"  {'OK  ' if hit else 'MISS'} 反例：未注册语言 qq          exit={c3}")
            if not hit:
                bad += 1

        # ★ 防误伤：正文里的 shortcode 是**合法**的（Hugo 会替换），不许报红。
        #   这一条是真实教训：首版判据对 content/de 一次假红 68 页，全是 `{{< count-countries >}}`。
        def put_shortcode_in_body(files):
            files["content/zz/_index.md"] = "---\ntitle: T\n---\n\nInsgesamt {{< count-countries >}} Länder.\n"

        with tempfile.TemporaryDirectory(prefix="langaudit-pos-") as td4:
            r4 = Path(td4)
            build_mini(r4, put_shortcode_in_body)
            c4, rep4 = run_audit(r4, "zz", quiet=True)
            hit = c4 == 0 and not any("{{" in f for f in rep4.fails)
            print(f"  {'OK  ' if hit else 'MISS'} 防误伤：正文含 shortcode       exit={c4}")
            if not hit:
                bad += 1
                print(f"        不该红却红了：{rep4.fails[:2]}")

    print(f"\n{'OK: selftest 全过' if bad == 0 else f'FAIL: {bad} 项不符'}")
    return 0 if bad == 0 else 1


# --------------------------------------------------------------------------- main


def main() -> int:
    ap = argparse.ArgumentParser(description="新语言就位度体检（只读）")
    ap.add_argument("lang", nargs="?", help="语言码，如 fr / ja")
    ap.add_argument("--repo", default=None, help="仓库根（默认本脚本的上一级目录）")
    ap.add_argument("--selftest", action="store_true", help="自检：正例 + 逐条反例")
    args = ap.parse_args()

    if args.selftest:
        return selftest()

    if not args.lang:
        ap.error("需要语言码（或 --selftest）")

    repo = Path(args.repo).resolve() if args.repo else Path(__file__).resolve().parents[1]
    code, rep = run_audit(repo, args.lang)

    print("\n" + "═" * 66)
    print(f"结论：{rep.lang} —— FAIL {len(rep.fails)} 项 / WARN {len(rep.warns)} 项")
    if rep.fails:
        print("\n必须处理（构建会失败，或页面会静默印错内容）：")
        for i, f in enumerate(rep.fails, 1):
            print(f"  {i}. {f}")
    if rep.warns:
        print("\n建议处理（不阻塞，但会降低质量）：")
        for i, w in enumerate(rep.warns, 1):
            print(f"  {i}. {w}")
    if not rep.fails and not rep.warns:
        print("该语言已完整就位。")
    print("\n逐文件操作手册：docs/add-a-language.md")
    return code


if __name__ == "__main__":
    sys.exit(main())
