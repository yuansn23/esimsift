# -*- coding: utf-8 -*-
"""把 `layouts/index.llms.txt` 的静态英文抽成 i18n key（德语 /de/llms.txt 德语化）。

背景
----
`layouts/index.llms.txt` 除 `.Site.Title` / `.Site.Params.description` 外**全部硬编码英文**
⇒ `/de/llms.txt` 只有首行导语是德语，小标题与每条描述全是英语；同时它一个文件就贡献了
`check_i18n.py` **35 / 49 处拼装句碎片**。

做法
----
1. 逐条**字面替换**：只把静态英文换成 `{{ i18n "…" }}`，控制流行 / `-}}` 裁剪 / 空行
   一律不动 ⇒ 英语产物的字节由「构造」保证不变；
2. 自检（保留动作占位的**结构等价证明**，比渲染后比对更快且可离线复跑）：把新模板按英文值
   **递归展开**每个 `i18n` 调用（`{{ .x }}` 占位符用模板里原本的表达式回填），`{{ }}` 之外
   的字面量逐字节拼接起来，必须与旧模板**完全相同** ⇒ 英语 `/llms.txt` 产物字节不变；
   且新模板 `{{ }}` 之外不得再残留任何 2 个以上连续 ASCII 字母（完整性证明）。
3. key 追加到 `i18n/en.toml` 与 `i18n/de.toml`，**同序等量**。

用法：
  python -X utf8 scripts/_llms_de_l10n.py --dry        # 迁移完成后：报「已完成」+ 两条无基线判据
  python -X utf8 scripts/_llms_de_l10n.py --selftest   # 正例 + 6 反例
  python -X utf8 scripts/_llms_de_l10n.py              # ★ 不可重复运行（会重复追加 key）

第七十四轮（2026-10-10）追加了一条 key 并改了 promo 行：
  · `$p.promo_label` 改走 `partial "de-text.html"`—— 它是**数据层英文句**（在 data/de/strings.toml），
    直接插值会让 `/de/llms.txt` 印 10 条英文促销句；英语站该 partial 恒等。
  · `promo_expires` 空时不再印 `, expires )` 残句，对齐 `esim-providers/single.html` 的 with/else。
  这两个缺陷正是 `scripts/verify_de_text.py` 判据 G 扩到非 HTML 产物后才能自动抓到的。
"""
from __future__ import annotations

import argparse
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
TPL = ROOT / "layouts" / "index.llms.txt"
EN = ROOT / "i18n" / "en.toml"
DE = ROOT / "i18n" / "de.toml"

# ── key → (英文值, 德文值) ── 英文值必须是原文去掉 `{{ }}` 后的精确文本，
#    动态部分写成 `{{ .x }}` 占位符，由模板侧 dict 用**原来的表达式**填充。
KEYS: list[tuple[str, str, str]] = [
    ("llms__intro_note",
     "Every plan is a listed, purchasable plan at check time; verification dates are shown per page. "
     "Derived metrics ($/GB, $/day) are computed with identical formulas for every provider — "
     "see the methodology page for the rules.",
     "Jeder Tarif ist ein zum Prüfzeitpunkt gelisteter, kaufbarer Tarif; die Prüfdaten stehen auf jeder Seite. "
     "Abgeleitete Kennzahlen ($/GB, $/Tag) werden für jeden Anbieter mit identischen Formeln berechnet — "
     "die Regeln stehen auf der Methodik-Seite."),

    ("llms__h_country_comparisons", "## Country comparisons", "## Ländervergleiche"),
    ("llms__country_head",
     "- [{{ .name }} eSIM comparison — {{ .providers }} providers, {{ .plans }} plans, from ${{ .min }}]({{ .url }}): cheapest ${{ .min }}",
     "- [{{ .name }} eSIM-Vergleich — {{ .providers }} Anbieter, {{ .plans }} Tarife, ab ${{ .min }}]({{ .url }}): günstigster ${{ .min }}"),
    ("llms__country_best_gb", ", best value ${{ .rate }}/GB", ", bester Wert ${{ .rate }}/GB"),
    ("llms__country_largest_cap", ", largest cap {{ .gb }}GB", ", größtes Volumen {{ .gb }} GB"),
    ("llms__country_unlimited", ", {{ .n }} unlimited plans", ", {{ .n }} unbegrenzte Tarife"),
    ("llms__country_checked", ", prices checked {{ .date }}", ", Preise geprüft am {{ .date }}"),

    ("llms__h_brand_country", "## Brand × country pages", "## Marken × Länder"),
    ("llms__brand_country_note",
     "Each country has one page per provider ({{ .pages }} pages, e.g. `/compare/japan/airalo/`) with that "
     "provider's full plan table, its computed rank among all providers on best $/GB, fair-use caps, "
     "and an honest strengths/weaknesses verdict.",
     "Jedes Land hat eine Seite pro Anbieter ({{ .pages }} Seiten, z. B. `/compare/japan/airalo/`) mit der "
     "vollständigen Tariftabelle dieses Anbieters, seiner berechneten Platzierung unter allen Anbietern beim "
     "besten $/GB, den Fair-Use-Grenzen und einem ehrlichen Stärken/Schwächen-Urteil."),

    ("llms__h_providers", "## Providers", "## Anbieter"),
    ("llms__provider_line", "- [{{ .name }}]({{ .url }}): {{ .tagline }}",
     "- [{{ .name }}]({{ .url }}): {{ .tagline }}"),
    ("llms__provider_promo", " — promo code `{{ .code }}` ({{ .label }}, expires {{ .expires }})",
     " — Promo-Code `{{ .code }}` ({{ .label }}, gültig bis {{ .expires }})"),
    # 第七十四轮追加：promo_expires 为空时不再印残句（对齐 esim-providers/single.html 的 with/else）
    ("llms__provider_promo_no_expiry", " — promo code `{{ .code }}` ({{ .label }})",
     " — Promo-Code `{{ .code }}` ({{ .label }})"),

    ("llms__h_matchups", "## Provider matchups", "## Anbieter-Duelle"),
    ("llms__matchups_index_label", "All provider matchups", "Alle Anbieter-Duelle"),
    ("llms__matchups_note",
     "One page per pair, one URL per matchup (slug alphabetical; reversed queries land on the same page). "
     "Full index at [{{ .label }}]({{ .url }}). Each verdict is computed across the countries both providers cover:",
     "Eine Seite pro Paar, eine URL pro Duell (Slug alphabetisch; umgekehrte Suchanfragen landen auf derselben "
     "Seite). Vollständiger Index unter [{{ .label }}]({{ .url }}). Jedes Urteil wird über die Länder berechnet, "
     "die beide Anbieter abdecken:"),
    ("llms__matchup_head",
     "- [{{ .a }} vs {{ .b }} eSIM]({{ .url }}): {{ .a }} cheaper entry in {{ .aWins }} of {{ .countries }} "
     "shared countries, {{ .b }} in {{ .bWins }}",
     "- [{{ .a }} vs. {{ .b }} eSIM]({{ .url }}): {{ .a }} günstigerer Einstieg in {{ .aWins }} von "
     "{{ .countries }} gemeinsamen Ländern, {{ .b }} in {{ .bWins }}"),
    ("llms__matchup_ties", ", {{ .n }} exact ties", ", {{ .n }} exakte Gleichstände"),
    ("llms__matchup_unlim_a", "; unlimited plans: {{ .a }} in {{ .n }} countries",
     "; unbegrenzte Tarife: {{ .a }} in {{ .n }} Ländern"),
    ("llms__matchup_unlim_b", ", {{ .b }} in {{ .n }}", ", {{ .b }} in {{ .n }}"),

    ("llms__h_data_research", "## Data & research", "## Daten & Analysen"),
    ("llms__data_research_note",
     "Original analysis computed from the same plan database as the comparison pages:",
     "Eigene Auswertungen, berechnet aus derselben Tarifdatenbank wie die Vergleichsseiten:"),
    ("llms__entry_line", "- [{{ .title }}]({{ .url }}): {{ .description }}",
     "- [{{ .title }}]({{ .url }}): {{ .description }}"),

    ("llms__h_guides", "## Guides", "## Ratgeber"),

    ("llms__h_network_map", "## eSIM network map", "## eSIM-Netzkarte"),
    ("llms__network_note",
     "Every travel eSIM rides a local host carrier; at the current check the providers we track use identical "
     "hosts in each destination. The map names the host networks per destination, isolates the carrier groups "
     "that cross borders (the lever a regional plan pulls), quotes independent Opensignal and Ookla verdicts "
     "for each destination with links to the originals, and defines the network vocabulary:",
     "Jede Reise-eSIM fährt auf einem lokalen Hostnetz; zum aktuellen Prüfstand nutzen die erfassten Anbieter "
     "in jedem Ziel identische Hosts. Die Karte benennt die Hostnetze je Ziel, isoliert die "
     "grenzüberschreitenden Netzgruppen (den Hebel, an dem ein regionaler Tarif zieht), zitiert unabhängige "
     "Opensignal- und Ookla-Urteile für jedes Ziel samt Links zu den Originalen und definiert das Netz-Vokabular:"),
    ("llms__network_map_label", "eSIM network map", "eSIM-Netzkarte"),
    ("llms__network_map_desc",
     "host carriers for every destination we track, the cross-border carrier groups, cited Opensignal and "
     "Ookla verdicts per destination, and a glossary of eSIM network terms",
     "Hostnetze für jedes erfasste Ziel, die grenzüberschreitenden Netzgruppen, zitierte Opensignal- und "
     "Ookla-Urteile je Ziel und ein Glossar der eSIM-Netzbegriffe"),
    ("llms__network_pages_note",
     "Per-destination carrier breakdowns, one page per country. Each page answers which local networks a "
     "travel eSIM can ride, how those networks score in independent Opensignal and Ookla testing, which "
     "brands ride which host, and what the local registration and identity rules mean for visitors:",
     "Netzaufschlüsselung je Ziel, eine Seite pro Land. Jede Seite beantwortet, auf welchen lokalen Netzen "
     "eine Reise-eSIM fahren kann, wie diese Netze in unabhängigen Opensignal- und Ookla-Tests abschneiden, "
     "welche Marken auf welchem Host fahren und was die lokalen Registrierungs- und Identitätsregeln für "
     "Reisende bedeuten:"),

    ("llms__h_how_we_compare", "## How we compare", "## Wie wir vergleichen"),
    ("llms__sec_methodology", "Methodology", "Methodik"),
    ("llms__methodology_desc", "data collection schedule, derived-metric formulas, badge rules",
     "Erhebungsrhythmus, Formeln der abgeleiteten Kennzahlen, Badge-Regeln"),
    ("llms__sec_disclosure", "Disclosure", "Offenlegung"),
    ("llms__disclosure_desc", "ownership and how the site makes money",
     "Eigentümerschaft und wie die Seite Geld verdient"),
    ("llms__sec_catalog", "Machine-readable price database", "Maschinenlesbare Preisdatenbank"),
    ("llms__catalog_desc", "full plan list as JSON", "vollständige Tarifliste als JSON"),

    ("llms__h_site_sections", "## Site sections", "## Seitenbereiche"),
    ("llms__link_line", "- [{{ .label }}]({{ .url }})", "- [{{ .label }}]({{ .url }})"),
    ("llms__sec_countries", "All country comparisons", "Alle Ländervergleiche"),
    ("llms__sec_matchups", "Provider matchups index", "Index der Anbieter-Duelle"),
    ("llms__sec_providers", "eSIM providers", "eSIM-Anbieter"),
    ("llms__sec_deals", "eSIM deals & promo codes", "eSIM-Angebote & Promo-Codes"),
    ("llms__sec_guides", "Guides", "Ratgeber"),
    ("llms__sec_research", "Data & research", "Daten & Analysen"),
    ("llms__sec_tools", "Tools", "Werkzeuge"),
]

ENV = {k: e for k, e, _ in KEYS}
DEV = {k: d for k, _, d in KEYS}

# ── 模板编辑：(原文片段, 新片段[, 期望出现次数]) ── 默认期望**恰好出现一次**；
#    末尾那条「列表项 = 标题 + 链接 + 描述」在 research / guides / networks 三处逐字节相同 ⇒ 期望 3。
EDITS: list[tuple] = [
    ("# {{ .Site.Title }}\n\n> {{ .Site.Params.description }}\n> Every plan is a listed, purchasable plan at check time; verification dates are shown per page. Derived metrics ($/GB, $/day) are computed with identical formulas for every provider — see the methodology page for the rules.",
     "# {{ .Site.Title }}\n\n> {{ .Site.Params.description }}\n> {{ i18n \"llms__intro_note\" | safeHTML }}"),

    ("## Country comparisons",
     "{{ i18n \"llms__h_country_comparisons\" | safeHTML }}"),

    ("- [{{ $c.name }} eSIM comparison — {{ $s.providerCount }} providers, {{ $s.planCount }} plans, from ${{ printf \"%.2f\" $s.minPrice }}]({{ $p.Permalink }}): cheapest ${{ printf \"%.2f\" $s.minPrice }}{{ if lt $s.minPerGB 999999.0 }}, best value ${{ printf \"%.2f\" $s.minPerGB }}/GB{{ end }}{{ if gt $s.maxGB 0 }}, largest cap {{ $s.maxGB }}GB{{ end }}{{ if gt $s.unlimitedCount 0 }}, {{ $s.unlimitedCount }} unlimited plans{{ end }}{{ with $s.checked }}, prices checked {{ . }}{{ end }}",
     "{{ i18n \"llms__country_head\" (dict \"name\" $c.name \"providers\" $s.providerCount \"plans\" $s.planCount \"min\" (printf \"%.2f\" $s.minPrice) \"url\" $p.Permalink) | safeHTML }}"
     "{{ if lt $s.minPerGB 999999.0 }}{{ i18n \"llms__country_best_gb\" (dict \"rate\" (printf \"%.2f\" $s.minPerGB)) | safeHTML }}{{ end }}"
     "{{ if gt $s.maxGB 0 }}{{ i18n \"llms__country_largest_cap\" (dict \"gb\" $s.maxGB) | safeHTML }}{{ end }}"
     "{{ if gt $s.unlimitedCount 0 }}{{ i18n \"llms__country_unlimited\" (dict \"n\" $s.unlimitedCount) | safeHTML }}{{ end }}"
     "{{ with $s.checked }}{{ i18n \"llms__country_checked\" (dict \"date\" .) | safeHTML }}{{ end }}"),

    ("## Brand × country pages",
     "{{ i18n \"llms__h_brand_country\" | safeHTML }}"),

    ("Each country has one page per provider ({{ mul (len $countries) (len $d.providers) }} pages, e.g. `/compare/japan/airalo/`) with that provider's full plan table, its computed rank among all providers on best $/GB, fair-use caps, and an honest strengths/weaknesses verdict.",
     "{{ i18n \"llms__brand_country_note\" (dict \"pages\" (mul (len $countries) (len $d.providers))) | safeHTML }}"),

    ("## Providers\n\n{{ range $key, $p := $d.providers -}}\n- [{{ $p.name }}]({{ absURL (printf \"esim-providers/%s/\" $key) }}): {{ $p.tagline }}{{ with $p.promo_code }} — promo code `{{ . }}` ({{ $p.promo_label }}, expires {{ $p.promo_expires }}){{ end }}",
     "{{ i18n \"llms__h_providers\" | safeHTML }}\n\n{{ range $key, $p := $d.providers -}}\n{{ i18n \"llms__provider_line\" (dict \"name\" $p.name \"url\" (absURL (printf \"esim-providers/%s/\" $key)) \"tagline\" $p.tagline) | safeHTML }}{{ with $p.promo_code }}{{ if $p.promo_expires }}{{ i18n \"llms__provider_promo\" (dict \"code\" . \"label\" (partial \"de-text.html\" $p.promo_label) \"expires\" $p.promo_expires) | safeHTML }}{{ else }}{{ i18n \"llms__provider_promo_no_expiry\" (dict \"code\" . \"label\" (partial \"de-text.html\" $p.promo_label)) | safeHTML }}{{ end }}{{ end }}"),

    ("## Provider matchups\n\nOne page per pair, one URL per matchup (slug alphabetical; reversed queries land on the same page). Full index at [All provider matchups]({{ absURL \"compare/matchups/\" }}). Each verdict is computed across the countries both providers cover:",
     "{{ i18n \"llms__h_matchups\" | safeHTML }}\n\n{{ i18n \"llms__matchups_note\" (dict \"label\" (i18n \"llms__matchups_index_label\") \"url\" (absURL \"compare/matchups/\")) | safeHTML }}"),

    ("- [{{ $pa.name }} vs {{ $pb.name }} eSIM]({{ absURL (printf \"compare/%s-vs-%s/\" $ka $kb) }}): {{ $pa.name }} cheaper entry in {{ $agg.aWinsPrice }} of {{ $agg.countries }} shared countries, {{ $pb.name }} in {{ $agg.bWinsPrice }}{{ if gt $agg.ties 0 }}, {{ $agg.ties }} exact ties{{ end }}{{ if gt $agg.aUnlimCountries 0 }}; unlimited plans: {{ $pa.name }} in {{ $agg.aUnlimCountries }} countries{{ end }}{{ if gt $agg.bUnlimCountries 0 }}, {{ $pb.name }} in {{ $agg.bUnlimCountries }}{{ end }}",
     "{{ i18n \"llms__matchup_head\" (dict \"a\" $pa.name \"b\" $pb.name \"url\" (absURL (printf \"compare/%s-vs-%s/\" $ka $kb)) \"aWins\" $agg.aWinsPrice \"countries\" $agg.countries \"bWins\" $agg.bWinsPrice) | safeHTML }}"
     "{{ if gt $agg.ties 0 }}{{ i18n \"llms__matchup_ties\" (dict \"n\" $agg.ties) | safeHTML }}{{ end }}"
     "{{ if gt $agg.aUnlimCountries 0 }}{{ i18n \"llms__matchup_unlim_a\" (dict \"a\" $pa.name \"n\" $agg.aUnlimCountries) | safeHTML }}{{ end }}"
     "{{ if gt $agg.bUnlimCountries 0 }}{{ i18n \"llms__matchup_unlim_b\" (dict \"b\" $pb.name \"n\" $agg.bUnlimCountries) | safeHTML }}{{ end }}"),

    ("## Data & research\n\nOriginal analysis computed from the same plan database as the comparison pages:",
     "{{ i18n \"llms__h_data_research\" | safeHTML }}\n\n{{ i18n \"llms__data_research_note\" | safeHTML }}"),

    ("## Guides", "{{ i18n \"llms__h_guides\" | safeHTML }}"),

    ("## eSIM network map\n\nEvery travel eSIM rides a local host carrier; at the current check the providers we track use identical hosts in each destination. The map names the host networks per destination, isolates the carrier groups that cross borders (the lever a regional plan pulls), quotes independent Opensignal and Ookla verdicts for each destination with links to the originals, and defines the network vocabulary:\n\n- [eSIM network map]({{ absURL \"networks/\" }}): host carriers for every destination we track, the cross-border carrier groups, cited Opensignal and Ookla verdicts per destination, and a glossary of eSIM network terms",
     "{{ i18n \"llms__h_network_map\" | safeHTML }}\n\n{{ i18n \"llms__network_note\" | safeHTML }}\n\n{{ i18n \"llms__entry_line\" (dict \"title\" (i18n \"llms__network_map_label\") \"url\" (absURL \"networks/\") \"description\" (i18n \"llms__network_map_desc\")) | safeHTML }}"),

    ("Per-destination carrier breakdowns, one page per country. Each page answers which local networks a travel eSIM can ride, how those networks score in independent Opensignal and Ookla testing, which brands ride which host, and what the local registration and identity rules mean for visitors:",
     "{{ i18n \"llms__network_pages_note\" | safeHTML }}"),

    ("## How we compare\n\n- [Methodology]({{ absURL \"methodology/\" }}): data collection schedule, derived-metric formulas, badge rules\n- [Disclosure]({{ absURL \"disclosure/\" }}): ownership and how the site makes money\n- [Machine-readable price database]({{ absURL \"catalog.json\" }}): full plan list as JSON",
     "{{ i18n \"llms__h_how_we_compare\" | safeHTML }}\n\n"
     "{{ i18n \"llms__entry_line\" (dict \"title\" (i18n \"llms__sec_methodology\") \"url\" (absURL \"methodology/\") \"description\" (i18n \"llms__methodology_desc\")) | safeHTML }}\n"
     "{{ i18n \"llms__entry_line\" (dict \"title\" (i18n \"llms__sec_disclosure\") \"url\" (absURL \"disclosure/\") \"description\" (i18n \"llms__disclosure_desc\")) | safeHTML }}\n"
     "{{ i18n \"llms__entry_line\" (dict \"title\" (i18n \"llms__sec_catalog\") \"url\" (absURL \"catalog.json\") \"description\" (i18n \"llms__catalog_desc\")) | safeHTML }}"),

    ("## Site sections\n\n- [All country comparisons]({{ absURL \"compare/\" }})\n- [Provider matchups index]({{ absURL \"compare/matchups/\" }})\n- [eSIM providers]({{ absURL \"esim-providers/\" }})\n- [eSIM network map]({{ absURL \"networks/\" }})\n- [eSIM deals & promo codes]({{ absURL \"esim-deals/\" }})\n- [Guides]({{ absURL \"guides/\" }})\n- [Data & research]({{ absURL \"research/\" }})\n- [Tools]({{ absURL \"tools/\" }})",
     "{{ i18n \"llms__h_site_sections\" | safeHTML }}\n\n"
     "{{ i18n \"llms__link_line\" (dict \"label\" (i18n \"llms__sec_countries\") \"url\" (absURL \"compare/\")) | safeHTML }}\n"
     "{{ i18n \"llms__link_line\" (dict \"label\" (i18n \"llms__sec_matchups\") \"url\" (absURL \"compare/matchups/\")) | safeHTML }}\n"
     "{{ i18n \"llms__link_line\" (dict \"label\" (i18n \"llms__sec_providers\") \"url\" (absURL \"esim-providers/\")) | safeHTML }}\n"
     "{{ i18n \"llms__link_line\" (dict \"label\" (i18n \"llms__network_map_label\") \"url\" (absURL \"networks/\")) | safeHTML }}\n"
     "{{ i18n \"llms__link_line\" (dict \"label\" (i18n \"llms__sec_deals\") \"url\" (absURL \"esim-deals/\")) | safeHTML }}\n"
     "{{ i18n \"llms__link_line\" (dict \"label\" (i18n \"llms__sec_guides\") \"url\" (absURL \"guides/\")) | safeHTML }}\n"
     "{{ i18n \"llms__link_line\" (dict \"label\" (i18n \"llms__sec_research\") \"url\" (absURL \"research/\")) | safeHTML }}\n"
     "{{ i18n \"llms__link_line\" (dict \"label\" (i18n \"llms__sec_tools\") \"url\" (absURL \"tools/\")) | safeHTML }}"),

    # 三处「列表项 = 标题 + 链接 + 描述」逐字节相同 ⇒ 统一走 llms__entry_line，期望 3 次
    ("- [{{ htmlUnescape .Title }}]({{ .Permalink }}): {{ htmlUnescape .Params.description }}",
     "{{ i18n \"llms__entry_line\" (dict \"title\" (htmlUnescape .Title) \"url\" .Permalink \"description\" (htmlUnescape .Params.description)) | safeHTML }}",
     3),
]

# ── 英语等价性证明 ──
# 判据：**`{{ }}` 之外的字面量 + 把每个 `i18n` 调用按英文值就地展开（`{{ .x }}` 占位符用
# 模板里原本的表达式回填，嵌套 i18n 递归展开）**，两者拼起来，旧模板与新模板必须逐字节相同。
# ⚠ 不能用「把 i18n 调用整段替换成英文值」的朴素做法：字典实参会被丢掉（嵌套 i18n 尤甚）。
_ACT = re.compile(r"\{\{.*?\}\}", re.S)


def strip_actions(s: str) -> str:
    return _ACT.sub("", s)


def _read_paren(s: str, i: int) -> tuple[str, int]:
    """s[i] == '(' ⇒ 返回 (去掉最外层括号的内容, ')' 之后的下标)。引号内括号不计数。"""
    assert s[i] == "(", s[i:i + 40]
    depth, q, j = 0, None, i
    while j < len(s):
        ch = s[j]
        if q:
            if ch == q:
                q = None
        elif ch in "\"'":
            q = ch
        elif ch == "(":
            depth += 1
        elif ch == ")":
            depth -= 1
            if depth == 0:
                return s[i + 1:j], j + 1
        j += 1
    raise ValueError(f"括号不闭合：{s[i:i + 60]!r}")


def _tokens(s: str) -> list[str]:
    """按空白切 token，但括号内与引号内的空白不切。"""
    toks: list[str] = []
    buf: list[str] = []
    depth, q = 0, None
    for ch in s:
        if q:
            buf.append(ch)
            if ch == q:
                q = None
            continue
        if ch in "\"'":
            q = ch
            buf.append(ch)
            continue
        if ch == "(":
            depth += 1
        elif ch == ")":
            depth -= 1
        if ch.isspace() and depth == 0:
            if buf:
                toks.append("".join(buf))
                buf = []
            continue
        buf.append(ch)
    if buf:
        toks.append("".join(buf))
    return toks


def _norm(inner: str) -> str:
    """去掉 `{{-` / `-}}` 裁剪标记与首尾空白；**不动内部空白**（避免误伤字符串字面量）。"""
    inner = inner.strip()
    if inner.startswith("-"):
        inner = inner[1:].strip()
    if inner.endswith("-"):
        inner = inner[:-1].strip()
    return inner


def _expand_expr(e: str, env: dict) -> str:
    e = e.strip()
    if e.startswith("(i18n "):
        sub, _ = _read_paren(e, 0)
        return _expand_action("{{" + sub + "}}", env)
    if e.startswith("("):
        sub, end = _read_paren(e, 0)
        if end == len(e):  # 整个实参被一对括号包住 ⇒ 去括号，还原成原文的 `{{ expr }}`
            e = sub.strip()
    return "{{" + _norm(e) + "}}"


def _expand_action(act: str, env: dict) -> str:
    body = _norm(act[2:-2])
    m = re.match(r'^i18n\s+"([^"]+)"\s*', body)
    if not m:
        return "{{" + body + "}}"
    key, rest, args = m.group(1), body[m.end():], {}
    if rest.startswith("(dict "):
        sub, _ = _read_paren(rest, 0)
        tk = _tokens(sub[len("dict "):])
        assert len(tk) % 2 == 0, tk
        for i in range(0, len(tk), 2):
            assert tk[i][0] == '"' and tk[i][-1] == '"', tk[i]
            args[tk[i][1:-1]] = tk[i + 1]
    val = env.get(key, "")  # 缺失 key 展开为空串 ⇒ ①③ 都会判红，且不会中断审计
    return re.sub(r"\{\{\s*\.([A-Za-z_]\w*)\s*\}\}",
                  lambda mm: _expand_expr(args[mm.group(1)], env), val)


def flatten(tpl: str, env: dict) -> str:
    """把模板折叠成「英语渲染结果的结构等价文本」（`{{ }}` 保留为动作占位，i18n 展开）。"""
    out, i = [], 0
    while True:
        j = tpl.find("{{", i)
        if j < 0:
            out.append(tpl[i:])
            break
        out.append(tpl[i:j])
        k = tpl.find("}}", j)
        out.append(_expand_action(tpl[j:k + 2], env))
        i = k + 2
    return "".join(out)


def audit(old: str, new: str, env: dict) -> list[str]:
    """三条判据，返回失败说明列表（空 = 全过）。供 main 与 --selftest 共用。"""
    bad: list[str] = []

    a, b = flatten(old, env), flatten(new, env)
    if a != b:
        p = next((i for i, (x, y) in enumerate(zip(a, b)) if x != y), min(len(a), len(b)))
        bad.append(f"等价性失败 @{p}: old={a[max(0,p-50):p+50]!r} | new={b[max(0,p-50):p+50]!r} "
                   f"(len {len(a)} vs {len(b)})")

    leftover = [m.group(0) for m in re.finditer(r"[A-Za-z]{2,}", strip_actions(new))]
    if leftover:
        bad.append(f"完整性失败：{{{{ }}}} 之外残留英文 {len(leftover)} 处 {leftover[:8]}")

    used = set(re.findall(r'i18n\s+"([^"]+)"', new))
    if used - set(env):
        bad.append(f"引用了未定义的 key：{sorted(used - set(env))}")
    if set(env) - used:
        bad.append(f"定义了但未使用的 key：{sorted(set(env) - used)}")
    return bad


def selftest() -> int:
    """注入反例：改造前的旧模板是唯一正例，「每类判据至少一个反例」必须被判红。"""
    old = TPL.read_text(encoding="utf-8")
    new = old
    for ent in EDITS:
        new = new.replace(ent[0], ent[1])

    cases: list[tuple[str, str, str, dict]] = []

    # ① 只此一类能抓：dict 实参被调换（`{{ }}` 之外的字面量完全没变）
    cases.append(("① 等价性（dict 实参调换）",
                  old,
                  new.replace('"min" (printf "%.2f" $s.minPrice) "url" $p.Permalink',
                              '"min" $p.Permalink "url" (printf "%.2f" $s.minPrice)', 1),
                  ENV))
    # ① 只此一类能抓：英文值被篡改（原文 "## Guides" → "## Guide"）
    # ⚠ 迁移落盘后脚本不可重复运行 ⇒ `old == new`，而 audit(old, new, env) 两侧共用
    #   同一个 env，改 env 会同时改两边 ⇒ 这条反例**结构上失效**（2026-10-10 第七十四轮
    #   发现 --selftest 常年红着，只因它不在 build 流水线里）。修法：自带基线 ——
    #   把当前模板按**英语值**展开成「改造前那种硬编码模板」当 old。
    old_literal = flatten(new, ENV)
    env_a = dict(ENV)
    env_a["llms__h_guides"] = "## Guide"
    cases.append(("① 等价性（英文值少一个 s）", old_literal, new, env_a))

    # ② 完整性：`{{ }}` 之外塞进英文（① 也会红 —— ② 是「不许有硬编码英文」这条产品要求的
    #    直接表述，与 ① 互为冗余加固，任一失效另一条仍在）
    cases.append(("①②（{{ }} 外残留英文）", old, new + "\nZZ\n", ENV))

    # ②③ 漏改一处：把 `## Guides` 还原成硬编码英文
    cases.append(("② 完整性 + ③ 对账（模板漏改一处）",
                  old,
                  new.replace('{{ i18n "llms__h_guides" | safeHTML }}', "## Guides", 1),
                  ENV))

    # ③ 只此一类能抓：引用不存在的 key
    cases.append(("③ key 对账（引用未定义 key）",
                  old,
                  new.replace('{{ i18n "llms__h_guides" | safeHTML }}',
                              '{{ i18n "llms__nope" | safeHTML }}', 1),
                  ENV))
    # ③ 只此一类能抓：定义了却没人用
    env_u = dict(ENV)
    env_u["llms__zzz_unused"] = "unused"
    cases.append(("③ key 对账（定义了未使用）", old, new, env_u))

    ok = True
    print("[selftest] 正例必须全绿：")
    msgs = audit(old, new, ENV)
    if msgs:
        ok = False
        print(f"  ✗ 正例误伤：{msgs}")
    else:
        print("  ✓ 正例全绿（与 --dry 同一判据）")

    print("[selftest] 反例必须判红：")
    for name, o, n, env in cases:
        msgs = audit(o, n, env)
        if msgs:
            print(f"  ✓ 判红：{name} → {msgs[0][:96]}")
        else:
            ok = False
            print(f"  ✗ 未判红（守卫失效）：{name}")

    print("[selftest] " + ("全过" if ok else "失败"))
    return 0 if ok else 1


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry", action="store_true")
    ap.add_argument("--selftest", action="store_true")
    args = ap.parse_args()

    if args.selftest:
        return selftest()

    old = TPL.read_text(encoding="utf-8")
    new = old
    missing: list[tuple[int, int, str]] = []
    for ent in EDITS:
        o, n = ent[0], ent[1]
        want = ent[2] if len(ent) == 3 else 1
        c = new.count(o)
        if c != want:
            missing.append((c, want, o))
            continue
        new = new.replace(o, n)

    if missing:
        # EDITS 的「原文片段」只存在于**改造前**的模板里；迁移落盘后重跑一条都找不到。
        # 这不是错误，是「已完成」—— 此时 audit 的等价性判据也没有基线（old == new，
        # 同一 env 会同时改两侧），所以只保留 ②「{{ }} 之外无英文」与 ③ key 对账。
        if all(c == 0 for c, _, _ in missing):
            leftover = [m.group(0) for m in re.finditer(r"[A-Za-z]{2,}", strip_actions(new))]
            used = set(re.findall(r'i18n\s+"([^"]+)"', new))
            if leftover:
                print(f"✗ 完整性失败：{{{{ }}}} 之外残留英文 {len(leftover)} 处 {leftover[:8]}")
                return 1
            if used - set(ENV) or set(ENV) - used:
                print(f"✗ key 对账失败：未定义 {sorted(used - set(ENV))} / "
                      f"未使用 {sorted(set(ENV) - used)}")
                return 1
            print(f"✓ 迁移已完成：{len(EDITS)} 条 EDITS 片段均已不在模板中，无需再改")
            print("✓ 完整性：模板 {{ }} 之外再无英文残留")
            print(f"✓ key 对账：模板引用 {len(used)} 个，全部有定义且全部被用")
            return 0
        for c, want, o in missing:
            print(f"✗ 片段出现 {c} 次（期望 {want}）：{o[:80]!r}")
        return 1

    msgs = audit(old, new, ENV)
    if msgs:
        for m in msgs:
            print(f"✗ {m}")
        return 1
    print(f"✓ 等价性：i18n 按英文值展开后与原文逐字节相同（{len(flatten(old, ENV))} 字符）")
    print("✓ 完整性：模板 {{ }} 之外再无英文残留")
    used = set(re.findall(r'i18n\s+"([^"]+)"', new))
    print(f"✓ key 对账：新引用 {len(used)} 个，全部有定义且全部被用")

    if args.dry:
        print(f"[dry] 模板 {len(old.encode('utf-8'))} → {len(new.encode('utf-8'))} 字节；"
              f"新增 i18n key {len(KEYS)} 个")
        return 0

    # ④ 写模板
    TPL.write_bytes(new.encode("utf-8"))

    # ⑤ 追加 i18n key（en / de 同序等量）
    block_en = "\n\n# ═══ llms.txt 德语本地化（2026-10-10）═══\n# 英文值 = 改造前模板字面量的逐字节副本 ⇒ /llms.txt 产物不变。\n"
    block_de = "\n\n# ═══ llms.txt 德语本地化（2026-10-10）═══\n"
    for k, e, d in KEYS:
        assert '"' not in e and '"' not in d, k
        block_en += f'{k} = "{e}"\n'
        block_de += f'{k} = "{d}"\n'
    for path, blk, tag in ((EN, block_en, "en"), (DE, block_de, "de")):
        raw = path.read_bytes()
        assert raw.count(b"\r\n") == 0
        if not raw.endswith(b"\n"):
            raw += b"\n"
        path.write_bytes(raw + blk.encode("utf-8"))
        print(f"[written] i18n/{tag}.toml +{len(blk.encode('utf-8'))} bytes")
    print(f"[written] layouts/index.llms.txt {len(old.encode('utf-8'))} → {len(new.encode('utf-8'))} bytes")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
