# 德语（de）上线步骤 —— 从零到 `/de/` 可访问

> 项目：`D:\esimsift\esimsift`（Hugo v0.159.1）
> 前提：多语言基础设施已于 2026-10-03 建成（i18n 词表 / 数据层深合并 / 语言规则 / 五重校验）
> 本文写给不熟悉 Hugo 的人：每一步都给出「改哪个文件 → 粘贴什么 → 敲什么命令 → 看到什么算成功」

---

## 〇、先回答你的三个问题

### Q1「只复制一个 i18n 德语文件就够了吗？」

**不够。** 一句话版：`i18n/de.toml` 只管**模板里写死的按钮 / 标题 / 说明文字**（749 条）。

德语站实际需要 **4 样东西**，缺一样都不行：

| | 要什么 | 放到哪 | 它解决什么 | 少了会怎样 |
|:--|:--|:--|:--|:--|
| ① | 语言声明 | `hugo.toml` 里的 `[languages.de]` | 告诉 Hugo「世界上存在德语这个站点」 | 完全不生成 `/de/` |
| ② | 词表 | `i18n/de.toml` | 模板文案（749 条 key） | **构建直接 FAIL**（key 对不齐） |
| ③ | 页面本体 | `content/de/` | 每个 URL 的标题与正文 | `/de/` 只剩一个首页，或**整个构建失败** |
| ④ | 数据散文（可选） | `data/de/` | 国家名、本地规则、FAQ | 德文页里夹着英文段落 |

打个比方：

- `hugo.toml` = 报户口（登记「这个站有德语版」）
- `i18n/de.toml` = 界面按钮的德语对照表（"Compare" → "Vergleichen"）
- `content/de/` = 德语版的每一页纸（标题、正文、SEO 描述）
- `data/de/` = 数据库里的德语文本（国家名、注意事项）

**所以「复制 i18n 文件」只是第 2 步，而且是最小的一步。**

### Q2「语言切换器改哪里？」

**只改 1 个文件**：`layouts/partials/header.html`。
但它牵动另外 2 件事：① 要往 `i18n/en.toml` 和 `i18n/de.toml` **各加同样 2 条 key**；② 新增的 CSS class 要重编 CSS。详见 Phase 2。

### Q3「还有哪些遗漏？」

Phase 3 有完整清单（我逐项 grep 过），按「必须修 / 建议修 / 可延后」三档。
其中 **A1（142 处内链）** 和 **A2（6 处首页链接）** 不修的话，德文站点几下就跳回英文页。

---

## Phase 0 —— 开工前的 3 件准备（约 10 分钟）

### 0.1 停掉正在跑的 `hugo server`【必须】

原因：`hugo server` 默认会把**开发态页面写进 `public/`**（注入 `livereload.js`、把域名改成 `localhost:1313`）。开着它构建，产物不可信；此时部署 = 把 `localhost:1313` 发布到线上。

```bash
# 查有没有
tasklist | grep -i hugo
netstat -ano | grep 1313
```

找到后在任务管理器结束 `hugo.exe`（或 `taskkill /PID <进程号> /F`），确认 `tasklist | grep hugo` 输出为空。

> 这是项目红线 42。已把 `package.json` 的 `dev` 改成 `hugo server --renderToMemory`，但**要重启 dev server 才生效**。

### 0.2 先把当前改动提交，建立干净基线【强烈建议】

原因：德语是「新增语言」。出错时你要能用一条命令回到「只有英文」的状态。

```bash
cd /d/esimsift/esimsift
git status --porcelain=v1 | wc -l      # 当前约 51 项（45 改 + 6 新增）
```

用 `/commit` 提交，或自己：

```bash
git add -A && git commit -m "chore: i18n 基础设施（词表 / 数据层深合并 / 语言规则 / 守卫）"
```

### 0.3 记下改前的产物数字【验收要用】

```bash
cd /d/esimsift/esimsift && npm run build 2>&1 | tail -20
```

记下 3 个数字（这是英文站的「健康基线」）：

| 指标 | 当前值 |
|:--|:--|
| Hugo `Pages` | **539** |
| `check_output` | **528 files / 2184 JSON-LD** |
| `check_headings` | **8098 h2/h3 · 0 bad** |

德语上线后，**英文部分的这 3 个数字一个都不能变**（只会多出德语的份数）。

---

## Phase 1 —— 最小可构建（目标是 `/de/` 首页能打开）

### 1.1 改 `hugo.toml`

**文件**：`D:\esimsift\esimsift\hugo.toml`
**位置**：**文件最末尾**（现在是 `[languages.en]` 块，后面就没有内容了）

**粘贴**（缩进是 2 个空格，不要用 Tab）：

```toml
[languages.de]
  languageCode = "de-de"
  languageName = "Deutsch"
  contentDir = "content/de"
  weight = 2
```

三个细节，逐个说清：

1. **`contentDir` 必须写**。不写的话 Hugo 会**静默**把 `content/en` 也给德语站用 —— 你会看到 `/de/` 里全是英文页，而且不报错，很难查。
2. **`languageCode` 用 `de-de`**，不是 `de`。`hreflang` 和 `og:locale` 直接读这个值：`de-de` → 输出 `hreflang="de-de"` 和 `og:locale="de_DE"`。
3. **`weight = 2`** 决定 hreflang 的顺序和切换器里语言的排列顺序（英文已经是 1）。

改完**先别急着构建**，继续 1.2、1.3。

---

### 1.2 新建 `i18n/de.toml`

```bash
cd /d/esimsift/esimsift
cp i18n/en.toml i18n/de.toml
```

然后打开 `i18n/de.toml`，**逐条把等号右边的英文换成德文。**

铁律（违反会直接构建失败或页面出错）：

| # | 规则 | 原因 |
|:--|:--|:--|
| 1 | **key（等号左边）一条都不能动、不能删、不能改名** | 749 条 key 必须齐全。少一条 → `check_i18n.py` 判 ERROR → `npm run build` FAIL |
| 2 | **`&` 要写成 `&amp;`**（en.toml 里有 6 条是这样） | 这些值是 `\| safeHTML` 渲染的，写裸 `&` 会变成非法 HTML |
| 3 | **不要往值里塞 HTML 标签**（`<strong>`、`<br>`） | 现在 0 条。一旦塞了会**原样注入**页面，可能坏版式 |
| 4 | 值必须用**双引号**包起来；德语里的 `„…“` 是普通字符没问题，但要写 ASCII 双引号时必须转义成 `\"` | TOML 语法 |
| 5 | 占位符（`%s`、`%d` 等）**位置可以挪，但一个都不能丢** | printf 会报错或输出错乱 |

**这一阶段不追求翻得漂亮** —— 只要 key 对齐、能构建就行。把它当「能跑的骨架」，后面再润色。

key 名的读法（方便你知道每条在哪儿显示）：

- `index__compare_travel_esim_plans_prices` → 来自 `layouts/index.html`
- `partials_header__compare_esims` → 来自 `layouts/partials/header.html`
- `g_compare` → 跨文件复用的通用短词（107 条），出现次数最多、优先译对
- 前缀分布（最大的几块）：`networks_list` 81 条、`esim_deals_list` 70 条、`compare_single` 53 条、`tools_list` 48 条、`esim_providers_single` 47 条

---

### 1.3 新建 `content/de/` 骨架【不做这一步，构建一定失败】

#### 为什么必须做

以下 **5 个地方**都写了「先取 `/compare` 这个栏目，然后立刻取它的页面列表」，**没有做 nil 保护**：

- `layouts/partials/header.html`（导航大菜单）
- `layouts/partials/footer.html`（页脚）
- `layouts/index.html`（首页）
- `layouts/index.catalog.json`（机器可读价格库）
- `layouts/index.llms.txt`（AI 检索文件）

写法长这样：

```
{{ $compare := site.GetPage "/compare" }}
{{ $countryPages := where $compare.Pages ... }}      ← 这里会炸
```

德语站如果没有 `/compare` 这个栏目，就会报
`nil pointer evaluating page.Pages`，
**结果不是「德语页少了」，而是「整个 `npm run build` 红掉，连英文站也构建不出来」**。

#### A. 首页 + 静态页（7 个）

```
content/de/_index.md
content/de/about.md
content/de/contact.md
content/de/disclosure.md
content/de/methodology.md
content/de/privacy.md
content/de/terms.md
```

做法：把 `content/en/` 下对应的 7 个文件拷过来，把 `title` / `seo.description` / 正文换成德语。

```bash
cd /d/esimsift/esimsift
cp content/en/_index.md content/en/about.md content/en/contact.md \
   content/en/disclosure.md content/en/methodology.md \
   content/en/privacy.md content/en/terms.md content/de/
```

#### B. 栏目索引页（7 个）—— **这是保命的一步**

```bash
cd /d/esimsift/esimsift
mkdir -p content/de/compare content/de/esim-providers content/de/esim-deals \
         content/de/guides content/de/networks content/de/research content/de/tools
```

然后 **每个目录下都要建一个 `_index.md`**，最少内容长这样：

```markdown
---
title: "德语标题"
seo:
  description: "德语描述"
---
```

（`_index.md` 如果完全空着，Hugo 会用目录名当标题，很难看；而且 list 模板可能要读 `seo.description`，建议照上面写。）

> ⚠️ `content/de/compare/_index.md` **绝对不能漏**。

#### C. 真正的内容页（先不做也能跑，按优先级补）

| 目录 | 英文文件数 | 说明 | 建议做法 |
|:--|--:|:--|:--|
| `content/en/compare/<国>/<品牌>.md` | 400 | 50 国 × 8 品牌子页 | **正文字段基本为空，只有 front matter** → 写脚本批量生成 |
| `content/en/compare/*.md` | 80 | 品牌对决页（`airalo-vs-holafly` 等） | 脚本生成 front matter + 人工补正文 |
| `content/en/guides/*.md` | 11 | 长文教程 | 人工翻译 |
| `content/en/networks/*.md` | 13 | 运营商深度页，长文 | 人工翻译 |
| `content/en/research/*.md` | 4 | 研究报告 | 人工翻译 |
| `content/en/esim-providers/*.md` | 9 | 品牌页 | 半自动 |
| `content/en/esim-deals/` | 1 | 促销页 | 人工 |

**省钱省力的关键发现**：`content/en/compare/<国>/<品牌>.md` 这 400 个文件**正文是空的**，只有 front matter（`title` / `iso` / `provider` / `layout` / `seo.description`）。
→ **这 400 个不要手工翻译**，写脚本复制骨架、只替换 `title` 和 `seo.description` 就行。

#### D. 文件路径必须与英文一一对应【重要】

Hugo 靠**相对路径**把「英文页」和「德文页」认成同一篇文章的两种语言，`.Translations` 和 `hreflang` 都依赖这个配对。

**所以：德文文件必须放在与英文完全相同的相对路径、用完全相同的文件名。**

```
content/en/compare/japan.md        ↔  content/de/compare/japan.md
content/en/compare/japan/holafly.md ↔  content/de/compare/japan/holafly.md
```

- 路径对不上 → `hreflang` 少一对、语言切换器在该页退化成「跳到对方语言首页」
- **v1 建议目录名和文件名都用英文**（`/de/compare/japan/`）。想要 `/de/vergleich/japan/` 这种德语 URL，属于第二个阶段的事，改起来要同步动 `slug` 和所有内链

#### E. 关于 `content/de/` 与「首页输出」

`layouts/index.catalog.json` 和 `layouts/index.llms.txt` 是**首页的额外输出格式**。加了德语后，德语首页也会生成 `/de/catalog.json` 和 `/de/llms.txt`，它们同样依赖 `/compare` 栏目存在 → 回到上面的 B 步。

---

### 1.4 构建 + 五重校验

```bash
cd /d/esimsift/esimsift
npm run build 2>&1 | tail -30
```

这条命令会依次跑：
`build:css`（Tailwind）→ `validate.py`（数据层）→ `check_css_sync.py`（CSS 同步）→ **`check_i18n.py`（i18n 守卫）** → `hugo`（构建）→ `check_output.py`（产物层）→ `check_headings.py`（标题标点）

**Phase 1 的通过标准：**

- [ ] `npm run build` 退出码 0（输出里没有 `FAIL`）
- [ ] `public/de/index.html` 文件存在
- [ ] `grep -c 'lang="de"' public/de/index.html` ≥ 1
- [ ] 英文站数字**没变**：Pages 仍是 **539**（总数变成 539 + 德语页数）
- [ ] `check_output` 的 528 → 528 + 德语文件数，且无 error
- [ ] **根路径 URL 没变**：`public/index.html` / `public/compare/japan/index.html` 等 539 个英文 URL 原样保留（因为 `defaultContentLanguageInSubdir = false`）

**没通过就别往下走。** 把报错贴出来。

顺手确认 `hugo.toml` 的 hreflang 门控开始生效了：

```bash
grep -c 'rel="alternate" hreflang' public/index.html      # 应为 2（en + de）
grep -c 'rel="alternate" hreflang' public/de/index.html   # 应为 2
```

---

## Phase 2 —— 语言切换器

现状：`layouts/partials/header.html` **完全没有语言切换 UI**（我通读过全文，一个都没有）。要动 3 处。

### 2.1 加 2 条 i18n key（两个文件**都要**加）

**文件 1**：`i18n/en.toml` 末尾追加

```toml
lang_switcher__label = "Language"
```

**文件 2**：`i18n/de.toml` 末尾追加**同名 key**，值译成德语

```toml
lang_switcher__label = "Sprache"
```

> ⚠️ **必须成对加。** 只加一边 → `check_i18n.py` 报「key 不对齐」→ 构建 FAIL。

### 2.2 改 `layouts/partials/header.html`（桌面端）

在文件里找到这一行（桌面导航的最后一个元素）：

```html
    <a href="/compare/" class="btn-primary ml-auto hidden text-xs md:inline-flex">{{ i18n "partials_header__compare_esims" | safeHTML }}</a>
```

**在它上面插入**下面这一整段：

```html
    {{/* 语言切换器：逐语言列出；当前页有对应译文就用译文页，没有就退回该语言首页 */}}
    {{ if gt (len hugo.Sites) 1 }}
    <div class="group relative ml-auto">
      <button type="button" aria-haspopup="true" aria-label="{{ i18n "lang_switcher__label" | safeHTML }}" class="flex items-center gap-1.5 rounded-lg px-2.5 py-2 text-sm font-semibold text-ink-700 transition-colors hover:bg-ink-50 hover:text-ink-950">
        <span class="uppercase">{{ .Language.Lang }}</span>
        <svg class="text-ink-300 transition-transform duration-200 group-hover:rotate-180" width="10" height="10" viewBox="0 0 12 12" fill="none" aria-hidden="true"><path d="M2 4l4 4 4-4" stroke="currentColor" stroke-width="2" stroke-linecap="round"/></svg>
      </button>
      <div class="nav-mega left-auto right-0 w-44">
        {{ range hugo.Sites }}
          {{ $target := .Home }}
          {{ range $.AllTranslations }}{{ if eq .Language.Lang $target.Language.Lang }}{{ $target = . }}{{ end }}{{ end }}
          <a href="{{ $target.RelPermalink }}" hreflang="{{ $target.Language.LanguageCode }}"{{ if eq $target.Language.Lang $.Language.Lang }} aria-current="true"{{ end }} class="mega-link">
            <span class="font-semibold">{{ $target.Language.LanguageName }}</span>
          </a>
        {{ end }}
      </div>
    </div>
    {{ end }}
```

**同时**：把原来那一行 `btn-primary` 上的 `ml-auto` **删掉**，改成：

```html
    <a href="/compare/" class="btn-primary hidden text-xs md:inline-flex">{{ i18n "partials_header__compare_esims" | safeHTML }}</a>
```

（两个 `ml-auto` 会打架，把布局挤歪。）

**这段代码为什么这么写（三个要点）：**

1. **用 `hugo.Sites`，不用 `.Translations`。**
   `.Translations` 只包含「有翻译的页面」；德语页还没建完时，很多英文页没有德语对应，用 `.Translations` 会导致切换器**时有时无**。逐语言遍历 `hugo.Sites` 才稳定。
2. **`$.AllTranslations` 里找当前语言的对应页**：找到就用那一页的真实 URL；没找到就用默认值 `$target := .Home`（该语言首页）。
3. **`{{ if gt (len hugo.Sites) 1 }}` 门控**：只有一种语言时**一个字节都不输出**。这是这条改动能安全合入的原因 —— 加德语之前，英文站产物与现在**逐字节相同**（和 `head.html` 里 hreflang 块同一个手法）。

### 2.3 移动端也加一个

`header.html` 下方还有一段 `<nav class="nav-scroll ... md:hidden">`（移动端横向滚动导航）。在它的最后一个 `<a>` 后面加：

```html
    {{ if gt (len hugo.Sites) 1 }}{{ range hugo.Sites }}{{ if ne .Language.Lang $.Language.Lang }}<a href="{{ .Home.RelPermalink }}" hreflang="{{ .Language.LanguageCode }}" class="whitespace-nowrap rounded-full bg-ink-50 px-3.5 py-1.5 text-xs font-semibold text-ink-700">{{ upper .Language.Lang }}</a>{{ end }}{{ end }}{{ end }}
```

### 2.4 新增的 class 必须重编 CSS

```bash
cd /d/esimsift/esimsift && npm run build:css
```

原因：`.nav-mega` / `.mega-link` / `w-44` 这些 class 必须真实存在于 `static/css/tailwind.css`，否则 `check_css_sync.py` 会判 FAIL（它专门防「写了个没有 CSS 规则的 class」）。
`npm run build` 的第一步就是 `build:css`，所以直接跑 `npm run build` 也行。

### 2.5 验收

- [ ] 英文页右上角出现语言按钮，点开有 **English / Deutsch**
- [ ] `/de/` 页面上的「English」指向 `/`（不是 `/de/`）
- [ ] 在**没有德语译文的英文页**上，「Deutsch」指向 `/de/`（回退到德语首页），**不能是 404**
- [ ] 产物里 hreflang 成对出现：
  ```bash
  grep -c 'rel="alternate" hreflang' public/index.html      # 2
  grep -c 'rel="alternate" hreflang' public/de/index.html   # 2
  ```

---

## Phase 3 —— 遗漏清单（逐项查过，按严重程度分档）

### A 档：必须修 —— 不修就是功能错（德文站里会跳回英文页）

| # | 位置 | 问题 | 怎么修 |
|:--|:--|:--|:--|
| **A1** | `layouts/` 下 **142 处**硬编码根路径内链，如 `href="/compare/"`（21 处）、`/methodology/`（28 处）、`/esim-providers/`（11 处）、`/esim-deals/`（10 处）、`/tools/`、`/networks/`、`/disclosure/` 等 | 德文页点导航会跳到**英文页** | 全部改成 `{{ relLangURL "compare/" }}`，或 `{{ with site.GetPage "/compare" }}{{ .RelPermalink }}{{ end }}` |
| **A2** | `layouts/compare/provider.html`、`layouts/compare/vs-single.html`、`layouts/esim-providers/single.html`（2 处）、`layouts/partials/breadcrumbs.html`、`layouts/partials/footer.html`、`layouts/partials/header.html` —— 把 `{{ .Site.BaseURL }}` 当「首页」链接用（**共 6 处**） | 德文页面包屑 / logo 的「Home」点回**英文首页** | 改成 `{{ site.Home.RelPermalink }}` |
| **A3** | `hugo.toml` 的 `[params]` 里 `tagline` / `description` 是英文，被模板直接引用 | 德文站的 SEO 描述是英文 | 改成 `i18n` key，或在 `[languages.de.params]` 里覆盖 |
| **A4** | `content/de/compare/<国>/<品牌>.md`（400 个）只补了 front matter 时页面正文很空 | 页面「没内容」而非报错 | Phase S4 用脚本批量补 |

> 补充：`layouts/` 里另外 **5 处** `/favicon.svg`、`/img/site/home-hero.webp`、`/css/tailwind.css` 是**静态资源**，**不要改**（142 + 5 = 147）。

### B 档：建议修 —— 不修就是「中英混排」（用户一眼看出来）

| # | 位置 | 问题 | 规模 |
|:--|:--|:--|:--|
| **B1** | `layouts/` 里的**拼装句碎片** | 德语页面出现英文残句。例：`layouts/index.html` 的 `'Real prepaid plans from'` | **704 处**，要重写成带命名占位符的整句：`{{ i18n "x" (dict "n" $n) }}` |
| **B2** | `printf` 生成的英文整句 | 德文页夹英文长句 | **141 处**；`layouts/esim-providers/single.html` 一个文件占 **80 处**，`compare/single.html` 49 处 |
| **B3** | 内联 `<script>` 里的用户可见英文 | JS 上下文不能用 `i18n` | **5 处**，例：`layouts/compare/vs-single.html` 的 `'Opening the computed '` → 改成模板输出 `data-*`、JS 读属性 |
| **B4** | `data/countries.toml` 的 **50 国 `quirks`**（每国 2–3 条长句）+ `name` | 德文国家页的「本地规则」段落是英文 | 约 130 条，人工；放 `data/de/countries.toml` |
| **B5** | `data/faqs/*.toml` 的 **300 条 `q` / 300 条 `a`**（50 个文件，文件名为 ISO 码） | 德文页 FAQ 全是英文 | 放 `data/de/faqs/<iso>.toml`，机翻 + 人工校 |
| **B6** | `content/de/*` 的 `seo.description` | 搜索结果摘要语言不对 | 随页面一起翻 |
| **B7** | `layouts/index.llms.txt` 全文英文长句 + `absURL` 硬编码英文路径 | AI 检索到德文站时拿到英文资料、链接指向英文页 | 需整体多语言化，或明确只保留英文版 |

**B4 / B5 的落地方式（数据层深合并）**：

```
data/de/countries.toml     ← 只写 name 和 quirks，其余（slug/flag/images/region）自动继承
data/de/faqs/jp.toml       ← 只写这个国家的 FAQ
data/de/plans/…            ← 一般不需要动
```

模板通过 `partialCached "i18n-data.html" . site.Language.Lang` 拿到合并后的字典，`merge` 对 map **递归合并**：

- ✅ `name` 被德语覆盖，`slug` / `flag` / `images` 自动保留
- ⚠️ **数组是整体替换，不是逐条合并**。你写 `quirks = ["只写一条德语"]`，结果不是「第 1 条变德语、后 2 条留英文」，而是**后 2 条直接消失**。所以 `quirks` / `carriers` / `neighbors` / `images` 这类数组字段，要么整段重写，要么别写

### C 档：可延后（不影响功能，但影响专业度）

| # | 位置 | 问题 | 建议 |
|:--|:--|:--|:--|
| C1 | JSON-LD **完全没有 `inLanguage`**（全仓搜过，0 处） | 结构化数据没声明语言，Google 可能判错语种 | `layouts/partials/schema*.html` 里加 `"inLanguage": "{{ .Language.LanguageCode }}"` |
| C2 | `layouts/sitemap.xml` 是自定义模板，每个语言各生成一份 | 多语言下的**根 sitemap** 行为需要实机确认 | 构建后看 `public/sitemap.xml` 第一行：是 `<urlset` 就去 GSC 分别提交 `/sitemap.xml` 和 `/de/sitemap.xml`；是 `<sitemapindex` 就什么都不用做 |
| C3 | `layouts/robots.txt` 的 `Sitemap: {{ .Site.BaseURL }}sitemap.xml` | 每个语言都写同一个（根）sitemap | 够用，可不改 |
| C4 | hreflang **缺 `x-default`** | Google 建议给一个默认语言版本 | 在 `head.html` 的 hreflang 块里补一条指向英文版 |
| C5 | `data/plans/*.toml` 的 `name`（**7776 条**）与 `fup_note`（**2684 条**）是数据里拼好的英文文案 | 直接翻译要 10460 条译文 | **不要翻译，改成模板渲染**：`name` 实测只有 2 个主模式（`{N}GB / {N} Days` 2100 条 + `Unlimited / {N} Days` 1882 条），`fup_note` 单条占 1753 条、top 6 模式覆盖 >95% |
| C6 | 数字格式：`$1.99` 在德语里习惯写 `1,99 $` | 会牵动计价逻辑 | **建议先不做**：全站统一 USD + `$` 前缀 |
| C7 | 日期格式 | 模板已用 `":date_medium"`（16 处），德语下自动出德语日期 | 已就位，抽查一页确认即可 |
| C8 | `layouts/404.html` | 会为 `/de/` 生成 404（文案已走 i18n） | 无需改，但 404 里的链接正确性依赖 A1 修完 |

---

## Phase 4 —— 分阶段推进（别一次做完）

| 阶段 | 做什么 | 产出 | 验收 |
|:--|:--|:--|:--|
| **S1** | 0.1–0.3 + 1.1 + 1.2 + 1.3（A/B） | `hugo.toml` + `i18n/de.toml` + `content/de` 骨架 | `/de/` 首页 + 7 个栏目空壳能打开；`npm run build` 绿；英文数字不变 |
| **S2** | Phase 2 语言切换器 | 右上角能切换 | 切换器在所有页面都对；hreflang 成对 |
| **S3** | A1 + A2 + A3（142 处内链 + 6 处首页链接 + params） | 德文站不再跳英文 | 随机点 20 个内链，URL 都在 `/de/` 下 |
| **S4** | content/de 内容页（400 个壳页脚本生成 + 长文人工翻） | 德文站有内容 | 页面数达标；抽查 10 页正文是德语 |
| **S5** | B1–B3（704 碎片 + 141 printf + 5 script） | 不再中英混排 | 抽查 10 页无英文残句 |
| **S6** | B4/B5（`data/de` 覆盖 quirks + FAQ）+ C1/C2/C4 | 完整德语站 | 五重校验全绿 |

---

## 附录 1 —— 「改哪些文件」总表

| 文件 / 目录 | 操作 | 阶段 |
|:--|:--|:--|
| `hugo.toml` | 末尾追加 `[languages.de]` 块 | S1 |
| `i18n/de.toml` | **新建**，从 `en.toml` 复制，749 key 全部译成德语 | S1 |
| `content/de/_index.md` + 6 个静态页 | 新建（从 content/en 拷 + 改文案） | S1 |
| `content/de/{compare,esim-providers,esim-deals,guides,networks,research,tools}/_index.md` | 新建（**`compare` 必须有，否则构建失败**） | S1 |
| `content/de/compare/<国>/<品牌>.md`（400 个） | 脚本批量生成 | S4 |
| `content/de/compare/*.md`（80 个） | 脚本 + 人工 | S4 |
| `content/de/guides/*.md`、`networks/*.md`、`research/*.md` | 人工翻译 | S4 |
| `layouts/partials/header.html` | 加桌面端 + 移动端语言切换器；删掉一个 `ml-auto` | S2 |
| `i18n/en.toml` + `i18n/de.toml` | 各加 `lang_switcher__label`（**成对**） | S2 |
| `layouts/**` 的 142 处 `href="/..."` | 改 `relLangURL` | S3 |
| `layouts/**` 的 6 处 `.Site.BaseURL`（当首页用） | 改 `site.Home.RelPermalink` | S3 |
| `hugo.toml` 的 `[params]` tagline / description | 改 i18n 或 `[languages.de.params]` 覆盖 | S3 |
| `layouts/partials/head.html` | 补 `x-default` hreflang | S6 |
| `layouts/partials/schema*.html` | 补 `inLanguage` | S6 |
| `layouts/sitemapindex.xml` | 新建（视 C2 检查结果决定要不要） | S6 |
| `data/de/countries.toml` | 新建，只写 `name` + `quirks`（**数组整段重写**） | S6 |
| `data/de/faqs/*.toml` | 新建 50 个文件 | S6 |

---

## 附录 2 —— 每次改完必跑的 3 条命令

```bash
cd /d/esimsift/esimsift

# 1) 全套构建 + 五重校验（一条顶五条，最重要）
npm run build 2>&1 | tail -30

# 2) 只看 i18n 守卫（快，改完 de.toml 就单独跑它）
python -X utf8 scripts/check_i18n.py

# 3) 确认产物没被 dev server 污染（两个都必须是 0）
grep -rl "livereload" public/ | wc -l
grep -rl "localhost:1313" public/ | wc -l
```

---

## 附录 3 —— 出错了怎么退回

```bash
cd /d/esimsift/esimsift

# 先把德语文案备份出来（git clean 会删掉新文件）
cp i18n/de.toml /c/Users/Administrator/WorkBuddy/2026-09-30-13-09-50/de.toml.bak

git checkout -- hugo.toml
git clean -fd i18n content/de data/de
npm run build 2>&1 | tail -20
```

前提是 Phase 0.2 已经把当前改动提交过。**备份那一步别省** —— `i18n/de.toml` 里是简体中文以外最贵的东西（译好的词表）。

---

## 附录 4 —— 最容易踩的 5 个坑（提前知道能省一天）

1. **忘了 `contentDir`** → Hugo 静默把英文内容也给德语站，`/de/` 全是英文页，不报错。**必须显式写 `contentDir = "content/de"`**。
2. **`content/de/compare/_index.md` 没建** → `nil pointer evaluating page.Pages`，**整站构建失败**（不是「德语页少」）。
3. **`i18n/de.toml` 少 key** → `check_i18n.py` ERROR，构建 FAIL。**key 只能改右边**。
4. **i18n 值里的 `&` 没写成 `&amp;`** → 页面出现非法 HTML。因为这些值是 `| safeHTML` 渲染的。
5. **`data/de` 里写数组时以为会逐条合并** → `merge` 对数组是**整体替换**，后几条会凭空消失。
