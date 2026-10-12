# 新增一种语言 —— 逐文件操作手册

> 项目：`D:\esimsift\esimsift`（Hugo v0.159.1 + Tailwind CLI，en 默认语言 + de 第二语言）
> 编写：2026-10-11（第八十三轮），**全部数字现算**（对照对象：已完成的德语站）
> 用途：要上第 3 种语言（法语 / 西语 / 意大利语 / 日语……）时，照本手册从上往下走。
> ⚠ 手册里所有路径都以**仓库根**为基准。凡标「★」的是真踩过的坑，别跳。

---

## 0. 一页速览：一种语言 = 五层

```
                        ┌──────────────────────────────────────────────┐
                        │  L0 声明层   hugo.toml  [languages.<lang>]   │  告诉 Hugo「有这门语言」
                        └───────────────────────┬──────────────────────┘
                                                │ 之后 Hugo 会为它渲染一整套产物
        ┌───────────────────────────────────────┼───────────────────────────────────────┐
        ▼                                       ▼                                       ▼
┌──────────────────┐                ┌──────────────────────┐              ┌──────────────────────┐
│ L1 界面词表      │                │ L2 数据覆盖层        │              │ L3 内容本体层        │
│ i18n/<lang>.toml │                │ data/<lang>/         │              │ content/<lang>/      │
│ 模板里的按钮/标题│                │ 数据里内建的英文句子 │              │ 644 个页面本体       │
│ 1841 个 key      │                │ 6 个 toml + 50 faq   │              │ 596+1+11+11+13+4+7   │
└──────────────────┘                └──────────────────────┘              └──────────────────────┘
        │                                       │                                       │
        └───────────────────────────────────────┼───────────────────────────────────────┘
                                                ▼
                        ┌──────────────────────────────────────────────┐
                        │  L4 守卫层   scripts/*.py                    │  保证上面 4 层不漂移
                        │  通用 9 个（自动覆盖）· de 专用 8 个（要复制）│
                        └──────────────────────────────────────────────┘
```

| 层 | 目录 / 文件 | 是什么 | 德语站实况（= 你的模板量） | 缺了会怎样 |
|:--|:--|:--|:--|:--|
| **L0 声明** | `hugo.toml` → `[languages.<lang>]` + `[languages.<lang>.params]` | 语言注册 + 该语言自己的站点 slogan/描述 | 2 个块 | 完全不产物；或**静默产出英文页**（最难查） |
| **L1 界面词表** | `i18n/<lang>.toml` | 模板层的界面文案（栏目标题、按钮、表头、CTA…） | **1841 key**（与 en 逐 key 同序） | 每页混英文；`check_i18n.py` 直接构建失败 |
| **L2 数据覆盖** | `data/<lang>/` （7 类） | `data/` 里**内建的英文句子**的译文（模板管不到） | 6 个 toml + `faqs/` 50 个 | **静默回退英文**，构建不报错 |
| **L3 内容本体** | `content/<lang>/` | 页面本身（front matter + 正文） | **644 个 .md** | 无此页 → 导航回退英文页（`lang-href` 兜底） |
| **L4 守卫** | `scripts/*.py` | 让上面 4 层永不漂移 | 通用 9 + de 专用 8 | 新语言页在部分守卫里是**盲区** |

**一句话**：L0 是开关，L1/L2/L3 是「翻译哪三层文本」，L4 是「怎么知道你没漏」。

---

## 1. L0 声明层 —— `hugo.toml`

### 1.1 改哪里

文件：`hugo.toml`（**CRLF**，9210 B）
在 `[languages.de]` 之后追加：

```toml
# 法语站（/fr/）
[languages.fr]
  languageCode = "fr-fr"        # ← ① 见 1.2
  languageName = "Français"     # ← ②
  contentDir = "content/fr"     # ← ③ 必须显式写
  weight = 3                    # ← ④

# 法语站的站点参数覆盖（英文值在顶层 [params] 里）
[languages.fr.params]
  tagline = "Comparez les forfaits eSIM de voyage"
  description = "…"
```

### 1.2 四个键分别是什么意思（每个都别写错）

| 键 | 值 | 作用 | 写错的后果 |
|:--|:--|:--|:--|
| `languageCode` | `fr-fr`（**不是 `fr`**） | 直接喂给 `hreflang="…"` 与 `og:locale`（经 `partials/og-locale.html` 转成 `fr_FR`） | 写 `fr` → `hreflang="fr"`。虽合法但丢失地域信号，且与 en(`en-us`)/de(`de-de`) 口径不一致 |
| `languageName` | `Français` | 语言切换器里显示的名字 | 切换器显示语言代码，很业余 |
| `contentDir` | `content/fr` | **内容从哪里读**。不写 → Hugo 默认取 `content/` 或复用默认语言目录 | ★ **最危险**：不写会静默把 `content/en` 也当成法语内容，`/fr/` 里全是英文页**且不报错** |
| `weight` | 3（递增） | 站点排序；`hugo.Sites` 按它排序，而 `lang-href.html` 的第二层兜底依赖「默认语言排第一」 | 乱序一般无害，但别让非默认语言排到默认语言前面 |

### 1.3 `[languages.<lang>.params]` 为什么必须写

`params.tagline` / `params.description` 在顶层 `[params]` 里是**英文**，会进入：
- 每页 `<meta name="description">` 的兜底值
- 页脚标语

不覆盖 → 法语页的 meta description 与页脚是英文。**构建完全不会报错。**

### 1.4 不用改的地方（已验证）

| 项 | 为什么不用改 |
|:--|:--|
| `defaultContentLanguageInSubdir = false` | 保持英文在**根路径**（`/compare/japan/` 而非 `/en/compare/japan/`）—— 644 条已收录 URL 零变更。这个值一旦改 true，**整个英文站的 URL 全会变**，等于换站 |
| `layouts/sitemapindex.xml` | 它固定输出默认语言（en）的 `<urlset>` 当根 `/sitemap.xml`。第三语言由 `layouts/sitemap.xml` 自动产出 `/fr/sitemap.xml`，**不需要动** |
| `layouts/partials/head.html` 的 hreflang 块 | 写法是 `{{ range .Translations }}` —— **N 个语言自动互相标注**。x-default 逻辑也自动（非 en 页从 `.Translations` 里找 en 页） |
| `layouts/partials/header.html` 语言切换器 | 走 `hugo.Sites` 遍历，**N 个语言自动出 N 个选项** |
| `layouts/partials/lang-href.html`、`i18n-data.html`、`de-text.html`、`og-locale.html`、`region-label.html` | 全部走 `site.Language.Lang` 动态取值。★ 注意 `de-text.html` **名字带 de 但完全通用**，别被名字骗了去复制一份 |
| `scripts/lang_rules.py` 的 `output_prefix()` | 从 `hugo.toml` 推导，自动认识新语言 |

### 1.5 ★ 三处**硬编码了语言**、加语言时必须手改的地方

| 文件 | 位置 | 现状 | 改法 |
|:--|:--|:--|:--|
| `layouts/robots.txt` | 末两行 | `Sitemap: {{ .Site.BaseURL }}sitemap.xml` 与 `Sitemap: {{ .Site.BaseURL }}de/sitemap.xml` | **手工加一行** `Sitemap: {{ .Site.BaseURL }}fr/sitemap.xml`。不加 → 新语言的 sitemap 不被声明（不致命，但等于少一条发现通道） |
| `scripts/gen_provider_pages.py` | L46 | `if LANG not in ("en", "de"): sys.exit(...)` | 把 `"fr"` 加进白名单；同时该脚本里 `LOC` 的加载逻辑要能读 `data/fr/countries.toml` 的国名 |
| `scripts/gen_vs_pages.py` | L45 | `if LANG not in ("en", "de"): sys.exit(...)` | 同上；另外 `TITLE_MIN/MAX`、`DESC_MIN/MAX` 是**按语言给的长度区间**，法语要实测一套 |
| `scripts/lang_rules.py` | `DASH_OK` 集合 | 已含 de/fr/es/it/pt/ja/ko/zh… | 若要上的语言不在集合里、且标题允许破折号，加进去；否则 `check_headings_source.py` 会按英文口径禁破折号 |

---

## 2. L1 界面词表层 —— `i18n/<lang>.toml`

### 2.1 文件形态

`i18n/en.toml`（**纯 LF**，199554 B，**1841 key**）与 `i18n/de.toml`（216100 B，1841 key）。

格式是**一行一个 key**、值用双引号包裹的**单行转义字符串**：

```toml
compare_single__h2h_h2 = "The closest eSIM matchups for {{ .country }}"
g_see_the_verdict = "See the verdict"
```

**不是**多行 TOML 字符串 —— 跨行文本写成字面 `\r\n`。

### 2.2 初始化（30 秒）

```bash
cp i18n/en.toml i18n/fr.toml     # 键名与顺序直接继承，值先留英文占位
```

这样 `check_i18n.py`（key 集合必须与 en 对齐）**立刻是绿的**，翻译可以慢慢来。

### 2.3 三条铁律

| # | 铁律 | 为什么 |
|:--|:--|:--|
| 1 | **key 必须与 `en.toml` 逐 key 同序**，不只是集合相同 | `check_i18n.py` 只校验**集合**，顺序靠纪律。顺序乱了以后 `diff en.toml de.toml` 就废了，维护成本指数上升 |
| 2 | 值里**只能**写 `{{ .name }}` 这类**占位符** | ★ 写别的 Go 模板语法会被当普通文本印给读者（i18n 值不过模板管线） |
| 3 | 值里**不许贴** `a` / `an` 这类冠词到占位符前 | 品牌名首音随机，`a {{ .brand }}` 会渲染出 "a Airalo"。产物级守卫 `check_article_agreement.py` 会抓 |

### 2.4 配套工具

| 命令 | 作用 |
|:--|:--|
| `python -X utf8 scripts/i18n_coverage.py fr` | 进度报告：翻了几成 / 未译 Top N 前缀 / `--prefix xxx` 列明细 |
| `python -X utf8 scripts/i18n_add.py batch.json` | **批量追加一批 key**（保证 en 与所有语言**同顺序**追加）。`--apply` 才写盘 |
| `python -X utf8 scripts/i18n_extract.py` | 从 `layouts/` 抽「纯静态文本节点」进 `en.toml`（只在英文侧新增硬编码时才跑） |
| `python -X utf8 scripts/check_i18n.py` | 守卫：① 模板不许新增硬编码 ② 各语言 key 集合对齐 ③ 碎片 WARN ④ 内联 `<script>` 英文（**ERROR**）⑤ `printf` 格式串英文 ⑥ `dict "q" "…"` 这类文案键 |

### 2.5 ★ 新增 key 的标准动作（唯一正确的顺序）

任何一次「给模板加文案」都必须**同一批**做完这 3 件事：

1. 在 `i18n/en.toml` 末尾追加 `new_key = "English copy"`
2. **同一位置**在所有 `i18n/<lang>.toml` 末尾追加同名 key（未译就先抄英文占位）
3. 模板里改成 `{{ i18n "new_key" | safeHTML }}`

做完跑 `npm run validate`（内含 `check_i18n.py`）。漏一个语言 → **构建直接失败**（这是设计如此）。

---

## 3. L2 数据覆盖层 —— `data/<lang>/`

### 3.1 为什么需要这一层

`data/` 里有一批**内建的英文句子**，它们不是模板文案，`i18n` 完全管不到：

- `data/plans/*.toml` 的 `fup_note`（公平使用说明，如 `"3 GB per day at full speed, then ∞ at 1Mbps"`）
- `data/providers.toml` 的品牌档案（tagline / strengths / weaknesses / policy.* / promo_label）
- `data/countries.toml` 的 `quirks`（国家须知短句）
- `data/networkreports.toml` 的 Opensignal 事实与 Ookla 说明
- `data/devices.toml` 的设备表文本字段

**不覆盖 → 这些句子原样渲染到新语言页上，构建零报错。** 这就是 L2 存在的全部理由。

### 3.2 逐文件清单（对照德语站实况）

| 文件 | 覆盖什么 | 德语站规模 | 缺了会怎样 |
|:--|:--|:--|:--|
| `data/<lang>/countries.toml` | 50 国国名（`Japan` → `Japan` / `Italien` …） | 2833 B | 卡片、H1、正文里的国名印英文 |
| `data/<lang>/providers.toml` | 品牌档案：`tagline` / `strengths` / `weaknesses` / `policy.*` 六个文本字段 / `promo_*` | 23395 B | 品牌页整段英文 |
| `data/<lang>/carriers.toml` | 运营商 profile 的 `note` + `info.detail[].strong/.weak` | 38995 B | 网络页的运营商描述印英文 |
| `data/<lang>/networkreports.toml` | `opensignal_facts[]` + `ookla_note` + `opensignal_date` | 30279 B | 网速报告整段英文（**含日期**） |
| `data/<lang>/strings.toml` | 四个「数据里的句子」的映射表：`fup_note` / `promo_label` / `info.support` / `info.refund` / `quirks` / `devices.*` | 43989 B | FUP 表、促销句、客服/退款正文、国家须知印英文 |
| `data/<lang>/titlesegments.toml` | 50 个国家页的 `<title>` 片段（带价格锚点） | 3401 B | 国家页 `<title>` 印英文 |
| `data/<lang>/faqs/<iso>.toml` | **逐国 FAQ**，文件名 = **小写 ISO**（`jp.toml` / `gb.toml`） | 50 个文件 | 该国 FAQ 印英文 |

### 3.3 ★ 深合并语义（`partials/i18n-data.html`）

```
map  → 递归合并（你只写要覆盖的键）
数组 → 【整体替换】（不是逐元素覆盖！）
```

**这是最容易出事的语义**。举例：`networkreports.toml` 里

```toml
opensignal_facts = [
  { carrier = "NTT Docomo", speed_min = 45.2, speed_top = 112.0, note = "…" },
]
```

要译 `note` 就必须**整段重写这个数组**，并把 `carrier` / `speed_min` / `speed_top` 等**机器字段原样带上**。少写一个字段 = 那个字段在新语言页上消失（不是回退，是**没了**）。

> 守卫：`verify_de_data.py` 判据 B「机器字段一致」就是专门抓这个的。

### 3.4 ★ `strings.toml` 的两个致命细节

1. **顶层不允许再包一层 `[strings]` 表。** `hugo.Data.<lang>.strings` 的值**就是文件内容本身**。包一层 → `$d.strings` 变成 `{strings:{…}}` → 查表恒落空 → **静默印英文**。（第六十二轮真实事故）
2. **`provider.policy` 的文本字段故意不进 `strings.toml`** —— 它们由 `data/<lang>/providers.toml` **深度覆盖**提供。同一事实**只允许一份译文**：两份会立刻漂移（德语实测：一处用 `Sie` + `unbegrenzte Tarife`，另一处用 `du` + `Unlimited-Tarife`，同一个站出现两种口径）。

### 3.5 初始化做法

```bash
mkdir -p data/fr/faqs
# ① 有生成器就直接跑（德语是 scripts/_gen_de_data.py / _gen_de_strings.py）
#    新语言建议：复制德语的生成器，把输入译文 JSON 换成新语言的
# ② 手工兜底：只写「确实会渲染」的键，缺的键会回退英文（安全，但不完整）
```

**验收**：改动后跑 `python -X utf8 scripts/verify_de_data.py` 的对应版本（见 §5）。

---

## 4. L3 内容本体层 —— `content/<lang>/`

### 4.1 精确构成（644 个 .md，与 `content/en/` **完全对称**）

| 子路径 | 数量 | 怎么来 | 正文在哪 |
|:--|--:|:--|:--|
| `compare/<slug>.md` | **50** | **手写/翻译**（每页 3 段 ~2000 B 的国别长文） | 在 md 正文里 |
| `compare/<slug>/<brand>.md` | **499** | `python -X utf8 scripts/gen_provider_pages.py --lang fr` | 空（由 `layouts/compare/provider.html` 渲染） |
| `compare/{a}-vs-{b}.md` | **45** | `python -X utf8 scripts/gen_vs_pages.py --lang fr` | 空（由 `layouts/compare/vs-single.html` 渲染） |
| `compare/_index.md` | 1 | 手写译文（Hub 页长文） | 在 md 正文里 |
| `compare/matchups.md` | 1 | 手写译文（对决枢纽页） | 在 md 正文里 |
| `esim-providers/*.md` | 11 | 10 个品牌 Hub + `_index` —— 正文由模板渲染 | 少量 md 正文 |
| `guides/*.md` | 11 | 5 篇区域指南 + 5 篇主题指南 + `_index` | 在 md 正文里 |
| `networks/*.md` | 13 | 12 个国家网络页 + `_index` | 在 md 正文里 |
| `research/*.md` | 4 | 3 篇研究长文 + `_index` | 在 md 正文里 |
| `esim-deals/_index.md`、`tools/_index.md` | 2 | 手写译文 | 在 md 正文里 |
| 根页：`_index.md` / `about` / `contact` / `disclosure` / `methodology` / `privacy` / `terms` | 7 | 手写译文 | 在 md 正文里 |
| **合计** | **644** | | |
| `compare/` 小计 | **596** | = 1 + 50 + 1 + 45 + 499 | |

### 4.2 三种页面形态的差别（决定了你要写多少字）

| 形态 | 例 | front matter | 正文 | 工作量 |
|:--|:--|:--|:--|:--|
| **A. 模板驱动**（骨架页） | `compare/japan/airalo.md`（430 B） | `title` / `iso` / `provider` / `layout: provider` / `seo.description` | **空** | 只需译 front matter 的 2 个字段（title、seo.description）→ **脚本可批量** |
| **B. 手写长文** | `compare/japan.md`（2070 B） | `title` / `iso` / `seo.description` | **3 段国别分析** | 必须**人工翻译**（50 页 × 3 段） |
| **C. 混合** | `guides/how-to-install-esim.md` | `title` / `description` | 多段正文 + 可能含 shortcode | 人工翻译 |

### 4.3 ★ 五条内容层纪律

| # | 纪律 | 为什么 |
|:--|:--|:--|
| 1 | **目录名 / slug 一律复用英文**（`united-states`，**不是** `vereinigte-staaten`） | URL 与 `hugo.toml` 无关，靠**文件名对齐**做翻译配对（`.Translations` 就是这么找到对方的）。改了 slug → `lang-href` 找不到译文页 → 语言切换器退化回首页 |
| 2 | **正文里的站内链接必须手写 `/<lang>/` 前缀** | ★ 正文**不过模板管线** —— `relLangURL` 在这里无效。德语实况：`[hier](/de/disclosure/)`。写 `(/disclosure/)` → 新语言页把读者送回英文站 |
| 3 | **正文里绝对不写 `{{ }}`** | Hugo 只解析模板文件，不解析正文。写了会被 Goldmark 当**普通段落**原样印给读者（真实事故：`/de/` 50 个国家页上公开展示 `TODO(de)：正文待翻译…`）。守卫 `check_output.py` 第 4 条专门抓这个 |
| 4 | **`noindex: true` 是你的「未完成」开关** | front matter 加一行即生效（`head.html` 读 `.Params.noindex`）。⚠ 两个连带效应：① 该页**不进 sitemap**（`sitemap-urls.html` 过滤）② 该页**不发 hreflang**（避免单向标注触发 GSC "No return tags"）。所以**正文没翻完就别解禁**，解禁要整类一起解 |
| 5 | **同一数字只有一个来源** | 国家页正文里的价格锚点（如 `$1.05/GB`）在英语侧是现算的；新语言若硬编码数字，English 数据一更新就漂移。`data/<lang>/titlesegments.toml` 的注释写明「价格锚点从英语侧转录：同一数字只有一份来源」 |

### 4.4 生成骨架页

```bash
# 品牌×国家子页（499 个）
python -X utf8 scripts/gen_provider_pages.py --lang fr --dry   # 先看会写什么
python -X utf8 scripts/gen_provider_pages.py --lang fr

# A-vs-B 对决页（45 个）
python -X utf8 scripts/gen_vs_pages.py --lang fr --dry-run
python -X utf8 scripts/gen_vs_pages.py --lang fr
```

两个脚本的共同特点（很重要）：

- 从 **`data/` 现算**，所以指标（排名、套餐数、最低 $/GB）在 en/fr **共享同一份实现** → 两侧不会算出两个不同数字
- **永不重写已存在的文件**（`gen_vs_pages.py` 对 en 侧 45 页完全不动）
- 生成时**自动带 `noindex: true`**（`NOINDEX = LANG != "en"`）→ 未完成时不会污染索引

---

## 5. L4 守卫层 —— 这张表决定「你会不会静默出错」

### 5.1 通用守卫（**自动覆盖新语言，你什么都不用做**）

| 脚本 | 管什么 | 为什么自动 |
|:--|:--|:--|
| `scripts/check_i18n.py` | 各语言 key 对齐 / 模板硬编码 / 内联脚本英文 / printf 英文 | 遍历 `i18n/*.toml` 全目录 |
| `scripts/check_hreflang.py` | hreflang 四条：自身 noindex 不发 / 目标必须存在 / **互惠** / 不指向 noindex | 读 `public/` 全量产物 + 从 `hugo.toml` 取 baseURL |
| `scripts/check_dates.py` | 产物域名卫生（localhost）/ 日期三处同源 / sitemap 完整性 | 按 URL 路径分派页型，语言无关 |
| `scripts/check_output.py` | Go 格式串残留 / JSON-LD 合法 / 评分范围 / **模板残留 `{{`** / `href="/https:/` | 扫 `public/**` |
| `scripts/verify_no_regression.py` | 逐页 sha256 对比基线（**英文产物零回归**的最终防线） | 基线是逐文件指纹，新语言页会自动算「新增」 |
| `scripts/check_css_sync.py` | 模板用的 Tailwind class 必须在编译 CSS 里 | 与语言无关 |
| `scripts/check_links.py` | 全站死链（**不进 build**，上线前单独跑） | 扫产物 |
| `scripts/lang_rules.py` | 语言规则单一事实源（产物前缀、破折号豁免） | 从 `hugo.toml` 推导 |
| `scripts/check_hardcoded.py` | 正文不许硬编码站点总数（要过 shortcode） | 扫 `content/**` |

### 5.2 ★ de 专用守卫（**新语言不会自动被守 —— 这是最大的坑**）

以下 8 个脚本**名字或内部逻辑绑定了 `de`**。上第 3 种语言时，新语言页在它们眼里**完全不存在**（不是报错，是**看不见**）：

| 脚本 | 绑定点 | 新语言要做什么 |
|:--|:--|:--|
| `scripts/verify_de_text.py` | 判据 A–J 全德语：`load_names(DATA/"de"/"countries.toml")`、`data/de/strings.toml`、德语黑名单词表、`root/"de"/"compare"` | 复制成 `verify_<lang>_text.py`，把语言码与词表参数化；或重构成接受 `--lang` 的通用版 |
| `scripts/verify_de_data.py` | `DE = DATA/"de"`、`PUB = ROOT/"public"/"de"`；`CITY_DE` / 月名映射从德语生成器 ast 读取 | 同上；★ 月名映射、城市名表的「唯一真源」在 `scripts/_gen_de_data.py` / `scripts/_loc_de_dates.py`，**新语言要建自己的一份真源，不许抄第二份规则** |
| `scripts/_de_schema_audit.py` | 8 条 JSON-LD 判据，de↔en 同路径页对比 | 参数化语言码 |
| `scripts/_de_link_leak_audit.py` | 德语页**站内链接语言泄漏**（不带 hreflang 的 `<a href>` 必须落在 `/de`）+ 畸形 href + 非 HTML 产物（`.txt/.json/.xml`） | 参数化语言码。★ 它抓的是「新语言页把人送回英文站」，**新语言必须要有这条** |
| `scripts/check_inline_copy.py` | `LANG_MARKERS = {"de": DE_MARKERS}`、`LANG_CHARS = {"de": "äöüßÄÖÜ"}` | 为新语言加一组「该语言特有标记」+「该语言特有字符」 |
| `scripts/check_faq_facts.py` | `KIND_OF_LANG = {"en": …, "de": …}`、`ROOT/"data"/"de"/"faqs"`、产品路径 `Path("de")/"compare"/…` | 加语言分支 |
| `scripts/check_printf_arity.py` | `"de": {…}` 块（德语 printf 格式串的参数个数核对） | 加语言块 |
| `scripts/check_headings_source.py` | selftest 里按 `en`/`de` 分别给期望值；实体逻辑从 `lang_rules.dash_ok_prefixes()` 读（**这部分是通用的**） | selftest 加语言夹具 |

> **建议**：上第 3 种语言时，**先把这 8 个脚本改成 `--lang` 参数化**，再开始翻译内容。否则你会在一个「守卫全绿但实际全是英文」的假安全里工作 ——
> 德语站历史上就吃过这个亏：47 页在 `<script>` 里印英文而 5 道闸门全绿。

### 5.3 完整闸门清单

| 命令 | 内容 |
|:--|:--|
| `npm run validate` | 5 道：`validate.py` → `check_css_sync.py` → `check_i18n.py` → `check_printf_arity.py` → `check_headings_source.py`（**源码层**） |
| `npm run check:output` | 13 道：`check_output.py` → `check_headings.py` → `verify_provider_pages.py` → `check_faq_facts.py` → `check_dates.py` → `check_hreflang.py` → `check_article_agreement.py` → `verify_de_text.py` → `verify_de_data.py` → `verify_no_regression.py` → `_de_schema_audit.py` → `_de_link_leak_audit.py` → `check_inline_copy.py`（**产物层**） |
| `npm run build` | `stamp` → `build:css` → `validate` → `hugo` → `check:output` |

★ **构建退出码必须重定向到文件再取 `$?`，禁管道**（`| tail` 会让 `$?` 变成 tail 的退出码，失败报全绿）。

### 5.4 配套体检脚本 `scripts/lang_new_audit.py`（**不进 build**）

```bash
python -X utf8 scripts/lang_new_audit.py fr          # 体检目标语言
python -X utf8 scripts/lang_new_audit.py --selftest  # 自检（1 正例 + 9 反例 + 1 防误伤）
```

它把上面 5 层逐层摆出来，只读、无副作用，退出码 `0` = 就位、`1` = 有结构性缺口。
**不用加进 `package.json`** —— 它是「上语言时用一次」的工具，不是每次构建都该跑的门。

实测两个方向都对：

| 跑法 | 结果 |
|:--|:--|
| `lang_new_audit.py de`（已完成的语言） | **FAIL 0 / 退出码 0** —— L0–L5 全绿（644 内容页逐栏目对齐、600 卡片、sitemap 644 条、抽样 200 页零语言泄漏）；唯一 WARN 是「已译 98.3%」这一真实状态 |
| `lang_new_audit.py ja`（未注册） | **FAIL 1 / 退出码 1**，且**短路**在 L0 —— 不会往下跑无意义的检查 |

「两侧都证」在这份脚本上是这样落实的：**同一份判据，对一个完整的语言必须全绿，对缺项必须逐条报红**。9 条反例分别破坏：`data/<lang>/countries.toml` / `contentDir` / robots 的 sitemap 行 / 一个 i18n key / `[languages.<lang>.params]` / 一页内容 / 一个 FAQ 文件 / 正文写 `{{ }}` / 语言未注册。

---

## 6. 执行步骤（8 个阶段，按序，每阶段带验收）

> 每个阶段的验收都**必须跑**，别跳。这个项目的教训是「构建绿 ≠ 页面对」。

### Phase 0 · 预检（不动任何文件）

```bash
# ① 体检目标语言的就位度（本手册配套脚本，只读）
python -X utf8 scripts/lang_new_audit.py fr

# ② 记下当前英文基线，后面要比对
git status --porcelain                          # 应为空或只有你已知的改动
python -X utf8 scripts/verify_no_regression.py --diff docs/regression-manifest.json
```

**验收**：体检脚本报告逐层缺口清单 + 基线「变更 0 / 新增 0 / 删除 0」。

### Phase 1 · 注册语言（L0）

改 `hugo.toml`（4 个键 + params 覆盖）+ `layouts/robots.txt`（加 sitemap 行）。

```bash
npm run build > .buildlog/lang_fr_p1.txt 2>&1; echo "EXIT=$?" >> .buildlog/lang_fr_p1.txt
```

**验收**：`EXIT=0`；`public/fr/index.html` 存在；`public/fr/sitemap.xml` 存在。
⚠ 此时 `check_i18n.py` 会因「`i18n/fr.toml` 不存在」或 key 不对齐而**失败** —— 那就直接进 Phase 2。

### Phase 2 · 界面词表（L1）

```bash
cp i18n/en.toml i18n/fr.toml
npm run validate > .buildlog/lang_fr_p2.txt 2>&1; echo "EXIT=$?" >> .buildlog/lang_fr_p2.txt
python -X utf8 scripts/i18n_coverage.py fr        # 看进度：起步应是 0%
```

**验收**：`EXIT=0`（`check_i18n.py` key 对齐通过）；`i18n_coverage.py` 能报出未译数。
之后可以分批翻译：`i18n_add.py batch.json` 或直接改 `fr.toml`。

### Phase 3 · 数据覆盖层（L2）

建 `data/fr/` 下 7 类文件（建议复制德语生成器 + 换译文源）。

```bash
npm run build > .buildlog/lang_fr_p3.txt 2>&1; echo "EXIT=$?" >> .buildlog/lang_fr_p3.txt
```

**验收**：`EXIT=0`；抽 `public/fr/compare/japan/index.html` 确认国名/FUP/促销句是法语。

### Phase 4 · 内容骨架（L3-A）

```bash
python -X utf8 scripts/gen_provider_pages.py --lang fr    # 499 个品牌子页
python -X utf8 scripts/gen_vs_pages.py --lang fr          # 45 个对决页
```

**验收**：`content/fr/compare/*/` 下 499 个文件、`content/fr/compare/*-vs-*.md` 45 个；每页都带 `noindex: true`。

### Phase 5 · 内容长文（L3-B，**最耗时**）

手写 50 个国家页 + `compare/_index.md` + `matchups.md` + 11 guides + 13 networks + 4 research + 2 deals/tools + 7 根页。

**验收（每批做完就跑）**：

```bash
npm run build > .buildlog/lang_fr_p5.txt 2>&1; echo "EXIT=$?" >> .buildlog/lang_fr_p5.txt
python -X utf8 scripts/verify_no_regression.py --diff docs/regression-manifest.json
```

★ 第二条是本项目最重要的一条：**英文产物必须逐页逐字节不变**（`变更 0 / 新增 N / 删除 0`，N = 新语言页数）。

### Phase 6 · 守卫扩展（L4）

把 §5.2 的 8 个 de 专用脚本参数化 / 复制成新语言版，并**接入 `package.json` 的 `check:output`**。

★ **两侧都证**：每个新守卫都要 `--selftest` 注入反例，证明「正例不误伤 + 反例会红」。且**新判据必须先对「改造前的旧产物」跑一遍**。

### Phase 7 · 解禁 + 索引 + 收尾

1. **整类解禁 `noindex: true`**（正文全部翻完之后，不要半途解禁）—— 两步缺一不可：
   - **a. 关掉生成器开关**：`scripts/gen_provider_pages.py` 与 `scripts/gen_vs_pages.py` 里的 `NOINDEX = LANG != "en"` —— 不关的话下次重跑又会写回来
   - **b. 删掉已存在文件里的那一行**（用 bytes 脚本，别用 `sed -i`，见 §8 注释）

   ```bash
   grep -rl "noindex: true" content/fr/ | wc -l     # 解禁前应有的数（德语站当年是 564）
   ```
2. 加 `x-default`（`head.html` 已自动，无需改）
3. 检查 `robots.txt` 已声明 `/fr/sitemap.xml`
4. **刷新回归基线**（新增整类页面之后必须刷新，否则下次 `--diff` 满屏「新增」）
   ```bash
   python -X utf8 scripts/verify_no_regression.py --write-manifest
   git diff --stat docs/regression-manifest.json
   ```
5. **上线前必须单独跑**（不依赖上一次构建帮你看着）
   ```bash
   python -X utf8 scripts/check_dates.py     # 产物卫生：localhost / 日期同源 / sitemap 完整
   python -X utf8 scripts/check_links.py     # 全站死链
   ```
6. 同步四份文档：`PROJECT.md`（规模 / 覆盖表）、`STATUS.md`、`docs/keyword-map.md`、`docs/pre-launch-checklist.md`

---

## 7. 坑清单（每条都对应一次真实事故）

| # | 坑 | 症状 | 正解 |
|:--|:--|:--|:--|
| 1 | `contentDir` 没写 | `/fr/` 里全是英文页，**构建全绿** | 显式写 `contentDir = "content/fr"` |
| 2 | `i18n` 值里写了 `{{ }}` 之外的东西 | 页面印出 `{{ .x }}` 原文 | 值里只放占位符 |
| 3 | 正文里写 `{{/* TODO */}}` | 读者看到 `TODO(fr)：正文待翻译…` | 正文用 `<!-- -->` 或干脆不写；`check_output.py` 抓 |
| 4 | `strings.toml` 包了 `[strings]` 表 | 查表恒落空 → **静默印英文** | 顶层即句子键 |
| 5 | 数组覆盖忘了带机器字段 | 字段「消失」（不是回退） | 整段重写数组，机器字段原样带上 |
| 6 | 正文内链写成 `(/disclosure/)` | 新语言读者被送回英文站 | 手写 `(/fr/disclosure/)` |
| 7 | slug 翻译成新语言 | `lang-href` 找不到译文 → 切换器退化 | slug 复用英文 |
| 8 | 模板标签之间插了一行（注释/缩进） | 全站多 1 行空白，`--diff` 无法归因 | ★「空白也是字节」：并进既有行或既有注释块 |
| 9 | 新模块 id 复用了别的页型的 id | 构建闸门当场报 N 处失败 | 查 `verify_no_regression.py` 的 `MARKER_ALLOWED` 白名单 |
| 10 | 外链走了 `relURL` / `lang-href` | `href="/https:/www…"` 死链 | 外链禁过相对路径通道；`check_output.py` 第 5 条守 |
| 11 | 手敲 `hugo server`（端口被占 → Hugo 自选端口） | **全站 canonical 与 sitemap 变成 localhost** | 预览只用 `npm run dev`；`check_dates.py` 断言 A 守 |
| 12 | 构建/体检加了管道取退出码 | 失败报全绿 | 退出码重定向到文件再 `$?` |
| 13 | 用 `hugo` 裸命令代替 `npm run build` | HTML 对、样式全无（Tailwind JIT 静默忽略未知 class） | 一律 `npm run build` |
| 14 | 未完成就解禁 `noindex` | 空正文页进索引 = 实打实的 SEO 损失 | 整类翻完再解禁 |
| 15 | 译文页单独发 hreflang | GSC 报 "No return tags" 并忽略整组 | `head.html` 已双侧守，别绕过 |
| 16 | 「一份事实两份真源」 | 同一站出现两种口径 | 城市名 / 月名映射 / 单位 / 政策字段各只有一份真源 |
| 17 | 译文页英文字符串黑名单永远追不上数据 | 新字段漏网 | 用**穷举**口径（「en.toml 已有译文的英文原串必须在新语言页消失」），不用人工黑名单 |
| 18 | 行尾被跨机器 checkout 改掉 | **`layouts/**`、`i18n/**`** 会直接改产物字节，`--diff` 无法归因 | `.gitattributes` 已锁这两个目录 `eol=lf`。★ `content/**` 与 `data/**` **未锁且无需锁** —— 实测：`content/en` 是 **607 CRLF + 37 LF 的混合**，`content/de` 是 **644 个纯 LF**，而 `public/**/*.html` **1291 个文件含 CR = 0** ⇒ **内容层的行尾不外溢到产物**（正文换行被 Markdown 渲染器规范化）。行尾在 content/data 里只是生成器留下的痕迹，各语言内部一致即可 |
| 19 | ★ **新写的「模板残留」判据把 shortcode 当残留** | 对 `content/de` 一次假红 **68 页**（全是 `{{< count-countries >}}`），而真残留是 **0**；产物侧 `public/de` 含 `{{` 的页数也是 0 | 判「未渲染的 `{{`」时**必须先挖掉 shortcode** `{{< … >}}` / `{{% … %}}` —— 它们合法且会被 Hugo 替换。`check_output.py` 第 4 条扫的是**产物**（shortcode 已展开）所以不需要这层豁免，但**扫源码的判据必须自己加**。这就是「穷举判据必须带防误伤边界」的又一实例 |
| 20 | 新守卫只证「该红的红了」 | 忘了证「不该红的没红」 | 每条新判据都要**两侧都证**：正例不误伤 + 反例会红。第 19 条就是靠补上「正文含 shortcode 必须过」这条用例才发现的 |

### 7.1 ★ 一个现存的尾巴（与新语言无关，但会影响你抄作业）

`content/de/` 下有 **564 个文件**仍留着历史注释 `# TODO(de)：…D9 解禁时统一删掉上面 noindex 行。`。D9 已经做完（全站 noindex = 0），这些注释是**无害但过期**的（`#` 在 front matter 里是注释，不产生产物）。

**别照抄这个模式**：新语言直接用 `noindex: true` 开关，翻完就删这一行，不要在注释里留 TODO。

---

## 8. 一页速查：最小可行路径

```bash
L=fr                                    # ← 目标语言码

# ① 体检（只读）
python -X utf8 scripts/lang_new_audit.py $L

# ② 注册
#    改 hugo.toml：[languages.fr] 4 键 + [languages.fr.params]
#    改 layouts/robots.txt：加 Sitemap: .../fr/sitemap.xml

# ③ 界面词表
cp i18n/en.toml i18n/$L.toml
python -X utf8 scripts/i18n_coverage.py $L

# ④ 数据覆盖
mkdir -p data/$L/faqs                    # 再按 §3.2 建 6 个 toml + 50 个 faq

# ⑤ 内容骨架
python -X utf8 scripts/gen_provider_pages.py --lang $L
python -X utf8 scripts/gen_vs_pages.py --lang $L

# ⑥ 长文（人工）

# ⑦ 构建 + 零回归
npm run build > .buildlog/lang_${L}.txt 2>&1; echo "EXIT=$?" >> .buildlog/lang_${L}.txt
python -X utf8 scripts/verify_no_regression.py --diff docs/regression-manifest.json

# ⑧ 解禁 + 刷新基线
#    A. 先把两个生成器的 NOINDEX 关掉（LANG != "en" → False），未来生成的页不再带
#    B. 再删已存在文件里的那一行 —— ⚠ 别用 `sed -i`：它在 Git Bash/Windows 上会改行尾、
#       甚至留 .bak，而 content 目录没有 .gitattributes 保护。写个一次性 Python 脚本，
#       用 read_bytes/write_bytes 删行（保持原有换行风格），并复核 CR 计数变化。
python -X utf8 scripts/verify_no_regression.py --write-manifest
python -X utf8 scripts/check_dates.py
python -X utf8 scripts/check_links.py
```

---

## 附：本手册涉及的文件总表

| 层 | 文件 / 目录 | 现况 |
|:--|:--|:--|
| L0 | `hugo.toml` | CRLF，9210 B，2 个语言块 |
| L0 | `layouts/robots.txt` | **LF**，810 B，硬编码 `de/sitemap.xml` |
| L1 | `i18n/en.toml` · `i18n/de.toml` | **LF**，199554 / 216100 B，**1841:1841 key** |
| L2 | `data/de/{countries,providers,carriers,networkreports,strings,titlesegments}.toml` | 2833 / 23395 / 38995 / 30279 / 43989 / 3401 B |
| L2 | `data/de/faqs/*.toml` | 50 个（文件名 = 小写 ISO） |
| L3 | `content/de/**/*.md` | 644 个，**全部纯 LF**（0 个 CRLF） |
| L3 | `content/en/**/*.md` | 644 个，**607 CRLF + 37 LF（脚本生成的那批）**，混合 |
| L4 | `scripts/check_i18n.py` · `check_hreflang.py` · `check_dates.py` · `check_output.py` · `verify_no_regression.py` · `check_css_sync.py` · `check_links.py` · `lang_rules.py` · `check_hardcoded.py` | 通用 |
| L4 | `scripts/verify_de_text.py` · `verify_de_data.py` · `_de_schema_audit.py` · `_de_link_leak_audit.py` · `check_inline_copy.py` · `check_faq_facts.py` · `check_printf_arity.py` · `check_headings_source.py` | **de 专用，需扩展** |
| L4 | `scripts/lang_new_audit.py` | **本手册配套体检脚本**（只读，不进 build） |
| L4 | `package.json` | 组装 `validate`(5) / `check:output`(13) / `build` |
