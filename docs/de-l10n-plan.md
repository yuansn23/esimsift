# 德语（de）正式上线方案 —— 从「首页测试」到「德语站可索引」

> 项目：`D:\esimsift\esimsift`（Hugo v0.159.1 + Tailwind CLI）
> 撰写：2026-10-04
> 起点：多语言基础设施已建成；`/de/` 首页已上线（测试用，让整体效果可见）；其余德语页是 `noindex` 占位
> **本文替代仓库根的 `de-duoyuyan-l10n-steps.md`** —— 那份写于实施之前，里面的「749 key」等数字已过时，可删。

---

## 0. 先读这段：三条红线

做德语的任何一步，都不能碰这三条：

| # | 红线 | 为什么 | 怎么守 |
|:--|:--|:--|:--|
| 1 | **英文产物零回归** | 英文站 526 条 URL 全在**根路径**（`/compare/japan/`，不是 `/en/compare/japan/`），已经在 Google 有排名。改错了等于把线上站换掉 | 每次改完跑 `python -X utf8 verify_de.py`，它会做全站 527 个英文页的逐行白名单判定 |
| 2 | **key 必须各语言对齐** | `scripts/check_i18n.py` 是 ERROR 级守卫：`i18n/xx.toml` 与 `en.toml` 的 key 集合不一致 → **构建直接失败** | 往 `en.toml` 加 key 时，同一次改动手动加到所有 `i18n/*.toml` |
| 3 | **模板里不许再出现硬编码文案** | 硬编码一旦存在，新语言页就会混英文（因为 i18n 根本管不到它） | `python -X utf8 scripts/check_i18n.py --strict` 归零后才能算 Phase 1 完成 |

---

## 1. 现状快照（起点）

### 1.1 已经建成的部分

| 文件 / 目录 | 作用 | 状态 |
|:--|:--|:--|
| `hugo.toml` → `[languages.de]` | 声明「存在德语站」，`contentDir = "content/de"`、`weight = 2` | ✅ 已就位 |
| `hugo.toml` → `[languages.de.params]` | 德语站自己的 `tagline` / `description`（不覆盖就是英文） | ✅ 已就位 |
| `i18n/de.toml` | 界面文案词表（777 key） | ⚠️ 只译了 **130 条（16.7%）** |
| `content/de/` | 德语页面本体（55 个 md） | ⚠️ 只有首页可用，其余是占位 |
| `data/de/countries.toml` | 50 国德语国名 | ✅ 已就位 |
| `layouts/partials/lang-href.html` | 站内链接的「三层兜底」解析器（本语言 → 英文 → 原路径） | ✅ 已就位 |
| `layouts/partials/og-locale.html` | Open Graph 的 `language_TERRITORY` 格式 | ✅ 已就位 |
| `layouts/partials/region-label.html` | 区域名的唯一转换点（`Asia` → `Asien`） | ✅ 已就位 |
| `layouts/sitemapindex.xml` + `partials/sitemap-urls.html` | 保证根 `/sitemap.xml` 仍是英文的 `<urlset>` | ✅ 已就位 |
| `layouts/partials/head.html` → `noindex` 开关 | 逐页 `noindex: true` 能力 | ✅ 已就位 |
| `scripts/i18n_coverage.py` | 翻译进度报告（本文档配套） | ✅ 新增 |

### 1.2 产物现状（`npm run build` 之后）

| URL | 可索引？ | 内容 |
|:--|:--|:--|
| `/sitemap.xml` | — | `<urlset>` **526 条英文根 URL**，与加德语之前**逐字节一致**（58749 字节） |
| `/de/sitemap.xml` | — | `<urlset>` **1 条**：`https://www.esimsift.com/de/` |
| `/`（首页） | ✅ 可索引 | 英文，canonical `https://www.esimsift.com/` |
| `/de/`（首页） | ✅ 可索引 | **全德语**，canonical `https://www.esimsift.com/de/` |
| `/de/compare/` 与 50 个 `/de/compare/<国>/` | ❌ `noindex, follow` | 只有德语标题与 SEO 描述，正文空 |
| `/de/guides/`・`/de/networks/`・`/de/research/` | ❌ `noindex, follow` | 列表骨架 |
| `/de/esim-providers/`・`/de/esim-deals/`・`/de/tools/` | — | **不存在**，德语导航会回退到英文页 |
| `/de/404.html` | — | 404 页 |

页面计数：**英文 527 个 HTML / 德语 56 个**（另有 1 个 `/en/index.html` 影子文件，见 §11.3）。

### 1.3 翻译进度

```
de.toml —— 777 key
  已译       130  [██████··································]  16.7%
  英文占位   647   ← 待翻译的量
  ✅ key 与 en 完全对齐
```

查看方式（随时可跑）：

```bash
python -X utf8 scripts/i18n_coverage.py            # 总览
python -X utf8 scripts/i18n_coverage.py de         # 只看德语
python -X utf8 scripts/i18n_coverage.py de --prefix compare_single --limit 40
```

> ⚠️ **口径提醒**：值等于英文原值就算「未译」。少数词德语与英文同形（`eSIM`、`SMS`、`Roami`），会被误判成未译，误差约 3%，不影响判断。

---

## 2. 总览：正式上线要动的 5 类东西

```
                 ┌─────────────────────────────────────────┐
   Phase 1 ──────│ 模板硬编码英文 → 抽成 i18n key            │  改 layouts/ + i18n/*.toml
                 └─────────────────────────────────────────┘
                                     ↓
                 ┌─────────────────────────────────────────┐
   Phase 2 ──────│ i18n/de.toml 的 647 条英文占位 → 德语      │  只改 i18n/de.toml
                 └─────────────────────────────────────────┘
                                     ↓
                 ┌─────────────────────────────────────────┐
   Phase 3 ──────│ 数据层散文 → data/de/                    │  改 data/de/*
                 └─────────────────────────────────────────┘
                                     ↓
                 ┌─────────────────────────────────────────┐
   Phase 4 ──────│ 页面本体 → content/de/                   │  改 content/de/*
                 └─────────────────────────────────────────┘
                                     ↓
                 ┌─────────────────────────────────────────┐
   Phase 5 ──────│ 逐页删 noindex → 自动进 sitemap/hreflang  │  front matter + robots.txt
                 └─────────────────────────────────────────┘
```

**顺序不能乱**：Phase 1 必须在 2 之前（否则抽出来的 key 还得再改一次）；Phase 5 必须在 4 之后（正文空就解除 noindex ＝ 让空页进索引）。

---

## 3. Phase 1 · 消掉模板里的硬编码英文（前置）

> 判定标准：`python -X utf8 scripts/check_i18n.py` 保持 **0 ERROR**（当前就是 0），
> 并且下面这 4 组「漏网硬编码」被清掉。
>
> ⚠️ 别用 `--strict` 当验收：它会把 **688 处拼装句碎片**和 5 处内联脚本文案也判为失败 ——
> 那些是全站历史欠账（大部分在 `layouts/index.llms.txt` 等非 HTML 产物里），
> 与德语无关，`--strict` 归零是长期目标而不是本阶段门槛。

目前 `check_i18n.py` 的输出是：`0 处硬编码文案 / 688 处拼装句碎片 / 5 处内联脚本文案`。
下面这 4 组的共同特点是**只影响德语页、不影响英文页**（英文页里这些字符串的生成路径不同），
所以 `check_i18n.py` 抓不到它们，必须人工处理。

### Step 1.1 —— `layouts/compare/single.html`（★ 最重要）

国家页 H1 与 3 个 h2 是**硬编码英文**，这也正是「德语国家页 H1 还是 `Best eSIM for Japan in 2026`」的原因。

| 行号 | 现状 | 要改成 |
|:--|:--|:--|
| L38 | `alt="{{ $country.name }} flag"` | 走 i18n（带 `name` 占位符） |
| **L42** | `<h1 ...>Best eSIM for {{ $country.name }} in {{ now.Year }}</h1>` | `{{ i18n "compare_single__h1" (dict "name" $country.name "year" now.Year) }}` |
| L44 | `Every prepaid eSIM plan for {{ $country.name }} from every major provider, ranked by ...` | i18n 带 `name` 占位符 |
| L60 | `<figcaption>{{ $country.name }} eSIM plans — N options from M providers, updated ...` | i18n 带 `name`/`plans`/`providers`/`date` 占位符 |
| L86 | `<h2 ...>Which {{ $country.name }} eSIM is best for your trip?</h2>` | i18n |
| L87 | `<p ...>The best {{ $country.name }} eSIM depends on how you travel. Three picks ...` | i18n |
| L140 | `<h2 ...>All {{ $country.name }} eSIM plans compared</h2>` | i18n |
| L303 | `<h2 ...>What {{ $country.name }} eSIM prices reveal</h2>` | i18n |
| L312 | `<h2 ...>Is unlimited eSIM data really unlimited in {{ $country.name }}?</h2>` | i18n |

做法：

1. 在 `i18n/en.toml` 追加这 9 个 key（`compare_single__h1` … `compare_single__figcaption`），值**原样照抄**现在模板里的英文。
2. 同一次改动里，在 `i18n/de.toml` 的对应位置加德语译文（否则 build FAIL）。
3. 模板改成 `{{ i18n "..." (dict ...) | safeHTML }}`。

> ⚠️ **占位符语法（本机实测）**：TOML 值里写 `{{ .name }}`，调用时 `(dict "name" ...)` 传参 —— `{{ i18n "k" (dict "n" 5) }}` ✅ 可用；`{{ i18n "k" | replace "NN" "5" }}` ❌ **管道顺序不生效**，别用。
>
> ⚠️ **标题标点**：`check_headings.py` 对 h2/h3 禁止 `,;:`（全语言），`—–` 只对白名单语言放行。德语标题里**不要用逗号**，用 `ohne` / `statt` / `und` 之类的连词替代。

### Step 1.2 —— `layouts/guides/region.html`

有 2 段硬编码英文。翻完后再建德语区域页（见 Phase 4），否则产出半英半德。

### Step 1.3 —— region 裸 key 的 3 处

`layouts/networks/list.html` L257 等 3 处仍在直接打印英文 region key（`{{ . }}` / `{{ $region }}`）。首页和 header 已经改走 `partial "region-label.html"`，这几处照做即可：

```
{{ partial "region-label.html" $c.region | safeHTML }}
```

### Step 1.4 —— 内联 `<script>` 里的 5 处用户可见英文

`check_i18n.py` 会 WARN。JS 上下文不能用 `i18n`（转义规则不同），做法是把文案用 `data-*` 属性注入 DOM，JS 从 `dataset` 读。参考 `layouts/index.html` 里已经改好的写法。

### Step 1.5 —— 验收

```bash
python -X utf8 scripts/check_i18n.py              # 保持 0 ERROR（不要求 --strict）
npm run build                                     # 五重校验
python -X utf8 verify_de.py                       # 英文页零回归
```

---

## 4. Phase 2 · 翻 `i18n/de.toml` 的 647 条

### 4.1 建议批次（按「影响力 ÷ 工作量」排序）

| 批次 | 前缀 | 条数 | 影响哪些页面 | 建议 |
|:--|:--|--:|:--|:--|
| A | `g_*` | 77 | **全站导航/按钮/徽章的通用短词**（Compare / Providers / Networks…） | 最先做，单价最低、收益最广 |
| B | `compare_single` | 53 | 50 个国家页 + 品牌页 | 配合 Phase 4，做国家页前必须完成 |
| C | `compare_list` / `compare_provider` / `compare_matchups` / `compare_vs_single` | 49 | `/compare/` 与对比页 | 二期 |
| D | `partials_*` / `404` / `home_*` | ~30 | 页头页脚、404 | 顺手做 |
| E | `esim_providers_single` / `esim_providers_list` | 54 | 品牌页 8 个 + 列表 | 三期 |
| F | `networks_list` / `networks_single` | **105** | 网络地图栏目 | 三期（量最大） |
| G | `esim_deals_list` | 70 | 折扣页 | 三期 |
| H | `tools_list` | 48 | 工具页 | 三期 |
| I | `guides_single` / `guides_region` | 42 | 11 篇指南 + 5 张区域卡 | 四期 |
| J | `research_*` | **141** | 4 个研究栏目 | 四期（写作量最大） |

### 4.2 每批的做法

```bash
# 1. 看这一批还剩哪些没译
python -X utf8 scripts/i18n_coverage.py de --prefix compare_single

# 2. 用编辑器打开 i18n/de.toml，只改这些 key 的值（不要动 key 名、不要动行顺序）

# 3. 校验（key 对齐 + 构建 + 回归）
python -X utf8 scripts/i18n_coverage.py de
npm run build
python -X utf8 verify_de.py
```

### 4.3 四条硬性注意

1. **只改值，不改 key**，也不要重排 `i18n/de.toml` 的行 —— 保持与 `en.toml` 同序，方便对读。
2. **`&` 的转义风格必须与英文原值一致**。所有 i18n 值都用 `| safeHTML` 渲染，值里若出现 `&`：
   - 英文原值写的是 `&amp;` → 德语也写 `&amp;`
   - 英文原值是裸 `&` → 德语也写裸 `&`
   写错会产出非法 HTML 或让文案显示成 `&amp;`。
3. **落在 h2/h3 位的值不能含 `,;:`**（`check_headings.py` 全语言禁止）。
4. **`i18n/de.toml` 里现有那 647 条英文占位不要删** —— 删了 build 立刻 FAIL（key 不齐）。它们是「占位」不是「多余」。

---

## 5. Phase 3 · 数据层散文 → `data/de/`

`data/de/` 目前**只有 `countries.toml`**（50 国国名）。其余数据文件的散文全是英文。

### 5.1 清单

| 文件 | 散文量 | 现在德语页会显示 | 优先级 |
|:--|:--|:--|:--|
| `data/countries.toml` → `quirks` | **101 条**（约 2 条/国） | 英文 | 高（国家页正文核心） |
| `data/faqs/<iso>.toml` | 50 文件 × 6 组 = **300 组 Q/A** | 英文 | 高（首页/国家页 FAQ） |
| `data/titlesegments.toml` | **50 条** `<title>` 片段 | **英文**（德语国家页 `<title>` 现在是 `Best Japan eSIM 2026: …`） | 高（**能直接看到**） |
| `data/providers.toml` → `strengths` / `weaknesses` / `tagline` / `brand.info` | 8 品牌 × 约 8 条 ≈ **65 条** | 英文 | 中 |
| `data/plans/<brand>.toml` → `fup_note` | 2684 条，**但只有 13 个不同值** | 英文 | 中（见下方技巧） |
| `data/carriers.toml` | 50 国 × 若干网络档案的文案字段 | 英文 | 中（网络栏目用） |
| `data/networkreports.toml` | 50 国的 Ookla/Opensignal 归属引用 | 英文 | 低（专有名词多，多数不必译） |
| `data/devices.toml` | 机型/品牌名 + `source_note` | 英文 | 低（品牌型号本来就不译） |

### 5.2 两条关键技巧

**① `fup_note`：13 条 vs 2684 条**

```
2684 条 fup_note 去重后只有 13 个值，最高频的一条出现 1753 次：
  "3 GB per day at full speed, then ∞ at 1Mbps"
```

所以**不要**去翻 400 个 plan 文件。两条路：

- **省事版**：只译这 13 条，写一个脚本按值替换 `data/plans/*.toml` 里的 `fup_note`（或在模板层做 `$d.fupMap` 映射）。
- **正确版**（推荐）：把 `fup_note` 从自由文本改成**结构化字段**（如 `fup_gb = 3` / `fup_speed = "1Mbps"`），模板层用 i18n 模板拼 —— 这样加第三、第四种语言时**零翻译成本**。E 类改动，但一劳永逸。

**② 深合并的数组陷阱**

Hugo 的 `data` 深合并规则：**map 递归合并，数组整体替换**。

```
merge (dict "JP" (dict "name" "Japan" "quirks" ["a" "b"]))
      (dict "JP" (dict "name" "Japan-de" "quirks" ["a-de" "b-de"]))
→ name 被覆盖 ✅，quirks 被整体替换 ✅（不是逐条合并）
```

含义：`quirks` / `carriers` / `neighbors` / `images` 这些数组字段，**要么不写（继承英文），要么整段重写**。不能只补第 2 条。

### 5.3 做法模板

```bash
# 建目录
mkdir -p data/de/faqs

# 复制结构（值仍是英文，然后逐条译）
cp data/faqs/*.toml data/de/faqs/

# 校验（data 层没有自动守卫，靠构建 + 目视）
npm run build
```

> ⚠️ `data/de/` 下的文件名必须与英文侧**完全一致**（`jp.toml` 不是 `JP.toml`）：模板用 `index site.Data.faqs (lower .Params.iso)` 取值。

---

## 6. Phase 4 · 页面本体 → `content/de/`

### 6.1 待办清单与优先级

| 优先级 | 目标 | 数量 | 现状 | 做法 |
|:--|:--|--:|:--|:--|
| ★1 | `content/de/compare/<国>.md` | 50 | 占位（德语 title/desc + `noindex`，正文空） | 手工写导语 + 依赖数据层自动生成的表格 |
| ★2 | `content/de/compare/_index.md` | 1 | 骨架 + `noindex` | 写栏目导语，删 `noindex` |
| ★3 | `content/de/guides/best-<区域>-esim.md` | 5 | **不存在** | 需先完成 Step 1.2 + `guides_region__*` 15 条 key |
| ★4 | `content/de/esim-providers/`、`esim-deals/`、`tools/`、`guides/`、`networks/`、`research/` 的 `_index.md` | 3 新建 + 3 补齐 | 缺 3 个 | 复制英文骨架改德语 |
| 5 | 根页面 `about` / `contact` / `privacy` / `terms` / `disclosure` / `methodology` | 6 | **不存在** | 法务页可后置，但 `privacy`/`terms` **建议早做**（法律要求本地语言） |
| 6 | `content/de/compare/<国>/<品牌>.md` | **400** | 不存在 | 正文本来就是空的（只有 front matter）→ **脚本批量生成**，不要手工 |
| 7 | `content/de/compare/<a>-vs-<b>.md` + `matchups.md` | 29 | 不存在 | 脚本批量生成 |
| 8 | `content/de/guides/<slug>.md`（教程类） | 6 | 不存在 | 手写 |
| 9 | `content/de/research/<slug>.md` | 3 | 不存在 | 手写（写作量最大） |
| 10 | `content/de/networks/<slug>.md` | 12 | 不存在 | 手写 |

**总量参考**：英文侧共 `compare 480 + networks 13 + guides 11 + esim-providers 9 + research 4 + tools 1 + esim-deals 1 + 根页 6 ≈ 525 页`。建议按上表分 3～4 个交付批次，不要试图一次做完。

### 6.2 关键：400 个品牌页为什么不用手写

`content/en/compare/<国>/<品牌>.md` 的**正文是空的**（只有 front matter），页面内容全部由模板从 `data/plans/*.toml` 推导。所以德语侧只需生成 front matter：

```
---
title: "<品牌德语名> <国德语名> eSIM"
iso: JP
provider: airalo
seo:
  description: "…德语…"
noindex: true        # ← 正文写作完成前保留
---
```

> ⚠️ **为什么 `content/de/compare/*.md` 必须存在**：首页的国家网格用 `site.GetPage "/compare"` → `.Pages` 渲染。
> 缺一个 md → 首页少一张卡；缺 `content/de/compare/_index.md` → **整站构建失败**（5 个模板对 `/compare` 没有 nil 保护，会 `nil pointer evaluating page.Pages`）。

### 6.3 每条页面的做法

1. 复制英文同名文件（保留 front matter 结构：`title` / `iso` / `provider` / `seo.description` / `hero`…）。
2. 译 `title` 与 `seo.description`（**控制长度**：`<title>` 目标 48–54 字符）。
3. 写正文（如该页需要）。
4. 正文写完后**删掉 `noindex: true`** 这一行（见 Phase 5）。
5. 构建 + 回归校验。

---

## 7. Phase 5 · 解除 `noindex` 与 SEO 收尾

### 7.1 解除 noindex

现在有 **54 个**德语页带 `noindex: true`（`compare/` 下 51 个 = 50 个国家页 + `compare/_index.md`，另有 `guides/`・`networks/`・`research/` 各 1 个栏目页），每处都留了注释：

```
# TODO(de)：正文待翻译。此页当前只有德语标题与 SEO 描述，正文为空，
#     因此前置项写了 noindex: true —— 翻好正文后请把这一行删掉，才会被收录。
```

**只删 `noindex: true` 这一行**，不要删注释里的说明（留着给同页其它字段的人看）。删了之后三件事自动发生：

| 自动变化 | 机制 |
|:--|:--|
| 出现在 `/de/sitemap.xml` | `layouts/partials/sitemap-urls.html` 里有 `{{- if not .Params.noindex -}}` 过滤 |
| 生成 `hreflang` 配对 | `layouts/partials/head.html` 只对「可索引」的译文发 hreflang（本轮刚修，见 §10.4） |
| 出现在 `de/sitemap.xml` 的 URL 计数里 | 同上 |

### 7.2 `x-default`（可选）

目前没有 `x-default`。Google 不强制，但对「有语言选择器」的站点是推荐做法。加的话在 `layouts/partials/head.html` 的 hreflang 块里补一行：

```
<link rel="alternate" hreflang="x-default" href="{{ site.Home.Permalink }}">
```

> ⚠️ 这会**改变英文页产物**（每页多一行），属于预期变更，但要同步更新 `verify_de.py` 的白名单。

### 7.3 `robots.txt` 声明德语 sitemap（可选）

`layouts/robots.txt` L45 现在只有：

```
Sitemap: {{ .Site.BaseURL }}sitemap.xml
```

德语页多起来后建议加一行（`/de/sitemap.xml` 现在没法从 robots.txt 发现，只能靠 hreflang 抓到）：

```
Sitemap: {{ .Site.BaseURL }}de/sitemap.xml
```

### 7.4 Google Search Console

1. 提交 `https://www.esimsift.com/sitemap.xml`（英文，原有）与 `https://www.esimsift.com/de/sitemap.xml`。
2. 「国际化」报告里确认 en/de 配对无 error（若出现 `hreflang → noindex` 就是 §10.4 的问题复现了）。
3. 「覆盖率」确认德语页随 `noindex` 删除逐步转为「已编入索引」。

### 7.5 全部完成后的一次总验收

```bash
npm run build                                                 # 五重校验全绿
python -X utf8 verify_de.py                                   # 六个分组全 ✅
python -X utf8 scripts/i18n_coverage.py de                    # 已译 = 777（100%）
python -X utf8 scripts/check_i18n.py --strict                 # ERROR/WARN 均为 0
grep -rl "noindex" content/de/ | wc -l                        # 应为 0
```

---

## 8. Phase 6 · 加第三种语言（fr / es / it / ja / …）

把本文的 5 个 Phase 完整复制一遍即可，另外注意这 4 个「第二语言时不需要、第三语言时必须」的点：

1. **`hugo.toml` 的 `weight`**：`en = 1`，后续按 `2, 3, 4...` 递增。**默认语言永远 weight 最小**，`hugo.Sites` 是按 weight 排序的，语言切换器的顺序、以及 `index hugo.Sites 0` 取「默认语言站」都依赖它。
2. **`i18n/<lang>.toml` 必须一次性建齐 777 个 key**（英文值占位也行）—— 少一个 key 就 build FAIL。
3. **`content/<lang>/compare/_index.md` 必须存在** —— 同上，缺了整站构建失败。
4. **`data/<lang>/` 只放要覆盖的文件** —— 深合并会继承英文，不必整目录复制。

新语言的「最小可跑」清单（照抄德语即可）：

```
hugo.toml                 → [languages.xx] + [languages.xx.params]
i18n/xx.toml              → 777 key（可全英文占位）
content/xx/_index.md      → 首页 front matter（写 <html lang> 就靠它）
content/xx/compare/_index.md → 保命项
content/xx/{guides,networks,research}/_index.md → 栏目骨架
data/xx/countries.toml    → 国名（可先不翻）
```

---

## 9. 命令速查

| 目的 | 命令 |
|:--|:--|
| 完整构建（上线前必跑） | `npm run build` |
| 只重建 Tailwind（改过模板里的 class） | `npm run build:css` |
| 英文页零回归 + 德语体检 | `python -X utf8 verify_de.py` |
| 翻译进度 | `python -X utf8 scripts/i18n_coverage.py de` |
| 硬编码守卫 | `python -X utf8 scripts/check_i18n.py --strict` |
| 产物校验 | `npm run check:output` |
| 本地预览 | `npm run dev`（⚠️ 见 §11.1） |

---

## 10. 坑清单（都是本机实测踩过的）

### 10.1 `public/` 被 dev server 覆盖成 localhost ★最危险

`npm run dev` 起的 `hugo server` 会把 `public/` 重写成 `baseURL = http://localhost:1313/` 的版本。

**症状**：`public/sitemap.xml`、每页的 `<link rel="canonical">` 全变成 `http://localhost:1313/...`。

**后果**：如果直接把这个 `public/` 上传，等于告诉 Google「我的站搬到了 localhost」—— 是事故级的。

**上线前必做**：

```bash
# 1. 确认没有 hugo server 在跑
tasklist | grep -i hugo        # 应无输出

# 2. 跑生产构建
npm run build

# 3. 确认 canonical 是生产域名
grep -o '<link rel="canonical"[^>]*>' public/index.html
# 期望：<link rel="canonical" href="https://www.esimsift.com/">
```

### 10.2 `contentDir` 不写会「静默出错」

`[languages.de]` 里不写 `contentDir`，Hugo 会把 `content/en` 也当成德语内容 —— `/de/` 下全是英文页，**且不报任何错**。必须在 `hugo.toml` 显式写上。

### 10.3 根 sitemap 会被换成 `<sitemapindex>`

加了第二个语言后，Hugo 默认把根 `/sitemap.xml` 从 `<urlset>` 换成指向 `/en/sitemap.xml` + `/de/sitemap.xml` 的 `<sitemapindex>`。

英文 URL 明明在根路径，这样等于宣告「英文站在 `/en/` 下」→ 已用 `layouts/sitemapindex.xml` 覆盖成默认语言的 `<urlset>`，并用 `verify_de.py` 的 E 组锁死「与改造前逐字节一致」。

### 10.4 `hreflang` 指向 `noindex` 页会造成 GSC 报错

占位阶段德语页是 `noindex`，但英文页照样会给它发 `<link rel="alternate" hreflang="de-de">` → Search Console 会把「hreflang 指向 noindex 页」判为错误。

**已修**：`layouts/partials/head.html` 的 hreflang 块现在只对**可索引**的译文发送（`{{ if not .Params.noindex }}`）。删掉 `noindex` 后 hreflang 会自动恢复。

### 10.5 `{{ if }}` 不裁剪左侧空白

新增条件块时若不写 `{{- if }}` / `{{- end }}`，会给**每一页**多输出一个换行。这个差异人眼几乎看不出来，但 `verify_de.py` 的逐行比对会抓到。

### 10.6 数据岛里的本地化字段必须 `htmlUnescape`

首页的国家搜索索引是 JSON。若 i18n 值里 `&` 写作 `&amp;`（HTML 约定），直接 `jsonify` 会产出字面量 `\u0026amp;` —— 前端拿到的就是坏数据。

**规矩**：同一个本地化字段若既有 HTML 渲染点又有 JSON 渲染点，**JSON 那一路必须加 `| htmlUnescape`**。

### 10.7 Go `html/template` 在 `<script>` 里必然把 `/` 转义成 `\/`

`/de/compare/` 会渲染成 `\/de\/compare\/`。`safeJS` / `safeHTML` / `safeURL` / `safeHTMLAttr` / `printf` / `string` **六种写法全绕不开**。JS 里 `'\/' === '/'`，语义恒等，接受它即可（`verify_de.py` 已做归一化）。真要干净就别把路径插进 JS 字符串。

### 10.8 深合并：map 递归，数组整体替换

`quirks` / `carriers` / `neighbors` / `images` 这些数组字段**不能只补一条**，要么继承英文，要么整段重写。

### 10.9 `check_headings.py` 的标点禁令是全语言的

`STRICT = [,;:—–]` 对所有语言禁止 h2/h3 里的这些标点；`RELAXED = [,;:]` 只对白名单语言（含 `de`）额外放行 `—–`。**逗号/分号/冒号任何语言都不许出现在 h2/h3 里。**

### 10.10 bash heredoc 会吞掉 Python 正则里的反斜杠

本项目已踩两次（`\s` 被 shell 吃掉）。**规矩：正则一律先写进文件再执行，不要用 heredoc 或 `-c` 里传。**

### 10.11 模板空白语义别靠推理，用 5 秒微型 probe

建一个只有 1 个 layout + 1 个 content 的临时 Hugo 站点，把可疑片段放进去渲染一遍看 `repr()`。比推理 10 分钟可靠得多（本机已用此法解决 head 空白、JS 转义两处）。

---

## 11. 附：发布与 SEO 影响评估

### 11.1 现在可以发布吗？

**可以，英文 SEO 不会受影响。** 依据：

| 检查项 | 结果 |
|:--|:--|
| 根 `/sitemap.xml` | 与加德语之前**逐字节一致**（58749 字节 · 526 条 URL · SHA256 相同 · 无 `/en/` 前缀） |
| 全站 527 个英文页 | 逐行白名单判定 → **非预期变更 0**。唯一差异是 head 里多了 hreflang/og:locale 块、header 里多了语言切换器 |
| 页面丢失/新增 | 英文页**没有消失、没有新增** |
| 德语入库范围 | 只有 `/de/` 首页可索引；其余 **54 个**德语页全部 `noindex, follow` |
| `hreflang` 一致性 | ✅ 已修（§10.4）—— 不再指向 noindex 页 |

**发布前必做一件事**：跑 §10.1 的三步，确认 `public/` 是生产构建（不是 localhost）。

### 11.2 对英文排名的影响预估

| 项 | 影响 |
|:--|:--|
| 英文 526 条 URL | **零影响**（URL 未变、canonical 未变、内容未变） |
| 新增 `/de/` 首页 | 中性偏正：独立语言页，与英文首页互相 hreflang，不构成重复内容 |
| 页面级 PageRank | 英文首页链接到 `/de/` 会分走极少量权重（一个链接位，可忽略） |
| 德语流量 | 目前约 0 —— 只有 1 个德语页进了索引，且德语词的竞争页是英文页 |

### 11.3 三个「知道就好」的残留

1. **`/en/index.html` + `/en/sitemap.xml` 影子文件**
   Hugo 自动生成的，**config 里关不掉**（实测 `disableKinds = ["sitemap"]` 也照生成）。二者都没被任何页面链接、也没提交给 GSC，对搜索是中性的。若不想让 `/en/` 出现在产物里，可在构建脚本末尾加一步删除。

2. **德语国家页的 `<title>` 仍是英文**
   来自 `data/titlesegments.toml`（`head.html` L57 读取），德语侧没有对应文件 → 回退英文。因为页面是 `noindex`，**当前不影响 SEO**，但 Phase 3 要补 `data/de/titlesegments.toml`。

3. **德语国家页 H1 是英文**
   `layouts/compare/single.html` L42 硬编码。同样因 `noindex` 不影响 SEO，但 **Phase 4 做国家页之前必须先在 Phase 1 修掉**。

### 11.4 建议的发布节奏

```
第 1 步（现在）   → 发布当前状态：英文全量 + /de/ 首页（其余 noindex 占位）
                    目的：验证多语言管线在线上无副作用
第 2 步           → Phase 1 + Phase 2 批次 A/B（约 130 条 key）
                    → 补 data/de/titlesegments.toml + countries quirks
                    → 删 50 个国家页的 noindex → 德语站第一次真正「有内容」
第 3 步           → 补齐栏目页与品牌页（脚本批量）
第 4 步           → guides / research / networks（手写量大，最后做）
```

---

## 附录 A · 本次（测试阶段）实际改动的文件清单

新增：

```
i18n/de.toml
content/de/_index.md
content/de/compare/_index.md
content/de/compare/<50 国>.md
content/de/guides/_index.md
content/de/networks/_index.md
content/de/research/_index.md
data/de/countries.toml
layouts/partials/og-locale.html
layouts/partials/region-label.html
layouts/partials/lang-href.html
layouts/partials/sitemap-urls.html
layouts/sitemapindex.xml
scripts/i18n_coverage.py
```

修改：

```
hugo.toml                          [languages.de] + [languages.de.params]
i18n/en.toml                       追加 28 key（749 → 777，只 append）
layouts/index.html                 首页全量 i18n 化 + 内链走 lang-href
layouts/partials/head.html         noindex 开关 + hreflang 过滤 + og:locale
layouts/partials/header.html       导航 i18n + 语言切换器 + region-label
layouts/partials/footer.html       页脚 i18n
layouts/partials/country-card.html 区域/tagline i18n + region-label
layouts/sitemap.xml                改为共用 sitemap-urls.html
layouts/robots.txt                 （未改，可选加 de sitemap）
其余 layouts/**                    约 202 处内链改走 partial "lang-href.html"
```

## 附录 B · 未提交状态

以上改动 + 上一轮多语言基础设施改造，**全部尚未 git commit**（约 60 项）。建议在发布前先提交一版基线，方便出问题时回滚。
