# 德语（de）上线实施方案 —— 第二版

> 项目：`D:\esimsift\esimsift`（Hugo v0.159.1 + Tailwind CLI）
> 第一版：2026-10-04（多语言基础设施刚建成时）
> **第二版：2026-10-09 全量复测重写**
> 第一版的数字（777 key / 647 未译 / 527 英文页 / 688 碎片 / `verify_de.py`）**全部过时** ——
> 这 5 天里站经历了第四十六～五十六轮改造（反同质化、FAQ 6→10 问、关键词植入七批、两道新守卫）。
> **本文为准。** 仓库根的 `de-duoyuyan-l10n-steps.md`（key 数写的是 749）可删。

---

## 0. 先读这段：三条红线

做德语的任何一步，都不能碰这三条：

| # | 红线 | 为什么 | 怎么守 |
|:--|:--|:--|:--|
| 1 | **英文产物零回归** | 英文站 644 条 URL 全在**根路径**（`/compare/japan/`，不是 `/en/`），已在 Google 有排名。改错等于把线上站换掉 | 每批做完跑 `python -X utf8 scripts/verify_no_regression.py --diff docs/regression-manifest.json`（**`verify_de.py` 已废弃，不要再引用**） |
| 2 | **key 必须各语言对齐** | `scripts/check_i18n.py` 是 ERROR 级守卫：`i18n/xx.toml` 与 `en.toml` key 集合不一致 → **构建直接失败** | 往 `en.toml` 加 key 时，**同一次改动**手动加到所有 `i18n/*.toml` |
| 3 | **模板里不许再出现硬编码文案** | 硬编码一旦存在，新语言页必然混英文（i18n 根本管不到它） | `check_i18n.py` **ERROR 必须 0**（当前就是 0）；另外 **566 处拼装句碎片是 WARN，见 §3** |

---

## 1. 现状快照（2026-10-09 复测，全部现算）

### 1.1 基础设施 —— 已就位，不用动

| 文件 / 目录 | 作用 | 状态 |
|:--|:--|:--|
| `hugo.toml` → `[languages.de]` + `[languages.de.params]` | 声明德语站、德语站自己的 tagline/description | ✅ |
| `layouts/partials/lang-href.html` | 站内链接三层兜底（本语言 → 英文 → 原路径） | ✅ |
| `layouts/partials/og-locale.html` · `region-label.html` | `de_DE` 格式 · 区域名唯一转换点 | ✅ |
| `layouts/sitemapindex.xml` + `partials/sitemap-urls.html` | 保证根 `/sitemap.xml` 仍是英文 `<urlset>` | ✅ |
| `layouts/partials/head.html` | `noindex` 开关 + hreflang 双侧过滤（第五十三轮修正） | ✅ |
| `layouts/partials/header.html` | 语言切换器（走 `hugo.Sites` + `AllTranslations`） | ✅ |
| `scripts/check_hreflang.py` · `check_i18n.py` · `i18n_coverage.py` | 守卫与进度报告 | ✅ |
| `data/de/countries.toml` | 50 国德语国名（`Japan` / `Italien` / `Österreich`） | ✅ |

**结论：基础设施不用再动。剩下的全是「内容与文案」，不是「管线」。**

### 1.2 产物现状

| URL | 可索引？ | 内容 |
|:--|:--|:--|
| `/sitemap.xml` | — | `<urlset>` **644 条英文根 URL** |
| `/de/sitemap.xml` | — | `<urlset>` **1 条**：`https://www.esimsift.com/de/` |
| `/`（首页） | ✅ | 英文 |
| `/de/`（首页） | ✅ | 全德语 |
| `/de/compare/` + 50 个 `/de/compare/<国>/` | ❌ `noindex, follow` | 德语标题/描述，**正文平均 64.2% 仍是英文** |
| `/de/{guides,networks,research}/` 栏目页 | ❌ `noindex, follow` | 列表骨架 |
| `/de/{esim-providers,esim-deals,tools}/` | — | **不存在**，导航回退英文页 |
| `/de/compare/<国>/<品牌>/`（499 页） | — | **不存在** |

计数：**英文 646 / 德语 56 个 HTML**（另 1 个 `/en/index.html` 影子文件，见 §11.3）。

### 1.3 五个缺口面的量化 —— 这张表就是「活」的全部

> ① 与 ② 两行是 **2026-10-09 第六十三轮复测**（现算）；③–⑤ 仍是当日早先的读数。

| # | 面 | 缺口 | 德语页现在的表现 |
|:--|:--|:--|:--|
| ① | **模板文案** | **100 处拼装句碎片**（`i18n_extract.collect()` 全仓口径，含 `.txt/.json/.xml`）+ 5 处内联脚本 | 55 个德语页里曾有 3 页漏英文（`/de/research/` 9 句、`/de/compare/` 索引整句 + 11 处套餐名、`/de/networks/` 的 aside 链接）—— **第六十三轮已修**，判据 F 已上闸门（§12.14） |
| ② | **界面词表** | `i18n/de.toml` **617 条英文占位 / 1671**（已译 1054 = **63.1%**） | 现有页型的界面词已德语；**未译的 617 条几乎全部属于「德语页还不存在的页型」**（D7/D8 的前置，见 §12.14） |
| ③ | **数据层散文** | `data/de/` 只有 `countries.toml` | FAQ、须知、`<title>` 片段、FUP 说明全英文 |
| ④ | **页面本体** | `content/de/` **55 文件** vs `content/en/` **644** → **缺 589** | 499 品牌子页 / 45 vs 页 / 10 品牌 Hub / 12 networks / 5 guides 单页 / 5 research / 6 根页 **全部不存在** |
| ⑤ | **索引状态** | **54 页 `noindex`**（de 共 56 页） | 德语站在 Google 眼里 ≈ 只有 1 个首页 |

**①的实测拆解**（`i18n_extract.collect()` 口径）：

```
layouts: 0 处硬编码文案（ERROR 级 = 0，因为「紧邻 {{ }} 的英文」被归为碎片而非硬编码）
        566 处拼装句碎片（.html 模板内，会污染德语页）
         37 处拼装句碎片（.llms.txt/.json/.xml，不进德语页，优先级低）
          5 处内联 <script> 用户文案（JS 上下文，须改 data-* 注入）

碎片 Top6（占 67%）：
  113  layouts/esim-providers/single.html
   79  layouts/compare/single.html          ← 德语国家页的主战场
   79  layouts/compare/vs-single.html
   50  layouts/networks/single.html
   44  layouts/networks/list.html
   42  layouts/guides/region.html
```

### 1.4 与第一版的关键差异（为什么旧文档不能用）

| 项 | 第一版（2026-10-04） | 现在（2026-10-09） | 成因 |
|:--|--:|--:|:--|
| `i18n` key 总数 | 777 | **1671** | 第五十二～第六十三轮新增大量文案 key |
| 英文占位（待译） | 647 | **617** | 现有页型已翻完；余量集中在「德语页还不存在的页型」（§12.14） |
| 英文页数 | 527 | **647** | 新增 vs 页 / 品牌 Hub / research 等页型（全站 702 = 647 en + 55 de） |
| 拼装句碎片 | 688 | **100** | D1–D3 + 第六十三轮把国家页与索引页的散文抽干净 |
| 待生成 vs 页 | 29 | **45** | 对决页扩容 |
| 品牌 Hub | 9 | **10** | 第五十二轮新增 |
| `data/faqs` 每组问答 | 6 组 | **10 组** | 第五十六轮 +4 问 |
| 德语校验脚本 | `verify_de.py`（已删） | `verify_no_regression.py` | 第五十二轮统一到全站回归基线 |

---

## 2. 实施路线：5 个阶段 / 9 个批次

### 2.1 依赖顺序（不能乱）

```
阶段 A  模板整句化（566 碎片 → i18n key）        D1–D4    ← 必须最先，否则后面做的页都要返工
   ↓
阶段 B  翻 i18n/de.toml（896 占位 + A 阶段新增）   D5
   ↓
阶段 C  data/de/ 数据层散文                       D6
   ↓
阶段 D  content/de/ 页面本体（脚本批量 → 手写长文） D7–D8
   ↓
阶段 E  解除 noindex + SEO 收尾                   D9      ← 必须最后，正文空就解禁＝让空页进索引
```

### 2.2 批次表

| 批 | 内容 | 改哪 | 影响面 | 依赖 |
|:--|:--|:--|:--|:--|
| **D1** | 模板整句化 · `compare/single.html`(79) + 共享 partials（header/footer/breadcrumb/faq/country-card 等） | `layouts/compare/single.html`、`layouts/partials/*` | 德语 **50 国家页** | — |
| **D2** | 模板整句化 · `networks/single`(50) + `networks/list`(44) + `guides/region`(42) + `guides/single`(20) | 4 个模板 | 德语 12+1+5 页 | — |
| **D3** | 模板整句化 · `esim-providers/single`(113) + `compare/vs-single`(79) + `compare/matchups`(19) + `esim-deals/list`(27) | 4 个模板 | 德语品牌 / vs / 促销页型 | — |
| **D4** | 模板整句化 · research ×3(53) + `compare/list`(12) + `tools/list`(11) + `_default/*`(3) + 5 处内联脚本 | 8 个文件 | 德语 research / tools | — |
| **D5** | 翻 `i18n/de.toml`：896 占位 + D1–D4 新增（估 +250） | `i18n/de.toml` | 全站 UI | D1–D4 |
| **D6** | `data/de/`：`faqs/` 50 文件 × 10 组 · `quirks` 101 条 · `titlesegments` 50 条 · `carriers` · `providers` 散文 · `plans` 的 `fup_note`+`name` | `data/de/*` | 德语页所有数据段 | D5 |
| **D7** | `content/de/` **脚本批量**：499 品牌子页 + 45 vs 页 + `matchups.md` + 10 品牌 Hub 的 md | `content/de/*` | **+555 页** | D6 |
| **D8** | `content/de/` **手写长文**：5 区域指南 + 5 guides 单页 + 12 networks + 4 research + tools/deals + 6 根页 | `content/de/*` | +34 页 | D6 |
| **D9** | 逐页删 `noindex` + `x-default` + `robots.txt` 声明 de sitemap + GSC 提交 | front matter、`head.html`、`robots.txt` | **645 页进索引** | D7/D8 |

**规模参考**：模板与词表约 **1,200 处**编辑；内容层 **589 个新文件**（= 644 − 55）；数据层 **50 个新文件**。

### 2.3 ★ 每批的验收判据（这一节比批次表更重要）

D1–D5 全是**恒等变换**（把 `All {{ $c }} eSIM plans compared` 改成
`{{ i18n "k" (dict "country" $c) | safeHTML }}`，值精确等于原字面量），
所以有一个**极强且零成本的判据**：

| 批次 | 判据 | 期望 |
|:--|:--|:--|
| **D1–D4** | `npm run build` + `verify_no_regression.py --diff` | **变更 0 / 新增 0 / 删除 0** —— 英文 646 页逐字节不变 |
| **D5** | 同上 | 变更 0（只动 `de.toml`，英文不读它） |
| **D6** | `i18n_coverage.py` + 抽 3 国德语页读一遍 | 占位归零；数字与英文侧一致 |
| **D7** | 产物计数 + `check_dates.py` 完整性 | de 页数 56 → **611**；sitemap de 同步 |
| **D8** | 反同质化自证（跨页模块 md5 去重 = N） | 见 §6.4 |
| **D9** | `check_hreflang.py` + `grep -rl noindex content/de` | 互惠配对 0 error；noindex 归零 |

⚠️ **D1–D4 若 `--diff` 不为 0，说明整句化写错了**（丢词、丢空格、多空格、转义不一致）。
这比任何人工通读都可靠 —— **恒等变换的产物必须逐字节相等**。

---

## 3. 阶段 A · 模板整句化（D1–D4）

### 3.1 什么是「拼装句碎片」，为什么它是第一优先级

看真实例子（`layouts/compare/single.html`）：

```html
<h2 id="table" class="...">All {{ $country.name }} eSIM plans compared</h2>
```

`i18n_extract` 把 `"All "` 判为**碎片**（紧邻 `{{ }}`），不判为硬编码 —— 所以
`check_i18n.py` 报 0 ERROR **并不代表模板干净**。这句在德语页渲染出来就是
`All Japan eSIM plans compared`（国名换成 `Japan`，句子还是英文）。

**为什么必须先做**：德语页的正文有 64.2% 的句子就是这么来的。不先整句化，
后面做的 589 个内容页全部要返工。

### 3.2 做法（一个碎片 → 一个 key + 两处值）

```go
{{/* 改前 */}}
<h2>All {{ $country.name }} eSIM plans compared</h2>

{{/* 改后 */}}
<h2>{{ i18n "compare_single__table_h2" (dict "country" $country.name) | safeHTML }}</h2>
```

```toml
# i18n/en.toml —— 值必须与改前字面量**逐字节相同**（含空格位置）
compare_single__table_h2 = "All {{ .country }} eSIM plans compared"
# i18n/de.toml
compare_single__table_h2 = "Alle {{ .country }}-eSIM-Tarife im Vergleich"
```

四条硬性注意（§3.9 的实测结论，别凭直觉）：

1. **一律 `| safeHTML`** —— 不加会把 `&` 转成 `&amp;`、`'` 转成 `&#39;`，产物就变了。
2. **属性值也用 `| safeHTML`**（`| safeHTMLAttr` 会二次转义成 `&amp;amp;`）；
   属性值里含 `'` / `"` 的**不要抽**（`safeHTML` 拦不住 `&#39;`）。
3. **内联 `<script>` 的文案不要走 i18n** —— 改 `data-*` 属性注入，JS 只读不算。
4. **`.llms.txt` / `.json` 输出同样会转义，一样要 `| safeHTML`**。

### 3.3 判定标准

`check_i18n.py` 的 WARN 计数从 **603 → 37**（剩下的 37 是非 HTML 产物，不进德语页；
5 处内联脚本由 D4 单独处理），并且 **`--diff` 必须为 0**。

---

## 4. 阶段 B · 翻 `i18n/de.toml`（D5）

口径与批次：

```bash
python -X utf8 scripts/i18n_coverage.py                    # 总览
python -X utf8 scripts/i18n_coverage.py de --prefix compare_single --limit 40
```

现在 **896 条待译**，按前缀分组（Top）：

| 组 | 条数 | 说明 |
|:--|--:|:--|
| `esim_providers_single` | 123 | D3 新增后还会涨 |
| `esim_deals_list` | 119 | |
| `compare_provider` | 114 | 品牌×国家子页（499 页都读它，**优先级最高**） |
| `g_*`（全站通用短词） | 81 | 按钮/标签，影响每页 |
| `networks_list` | 81 | |
| `compare_single` | 69 | 国家页 |
| `tools_list` | 48 | |
| `research_*`（4 组） | 141 | |
| 其余 | 120+ | |

四条纪律：

1. **德语用 du-form**（`dein` / `dir`，不用 `Ihr`）—— 全站已定，别混。
2. **不翻的清单**：品牌名（Airalo / Yesim / Ubigi）、套餐名（`Élan` / `Fáilte`）、
   机构名（Ookla / Opensignal / GSMA）、外部报告标题（**逐字引用是 E-E-A-T 信号**）。
3. **德语合成词会长 15–30%** —— `<title>` / 按钮 / 表格列头要复查溢出
   （`<title>` 目标仍 48–54 字符）。
4. **占位不是多余**：英文占位不要删，删了 build 立刻 FAIL。

---

## 5. 阶段 C · 数据层散文 → `data/de/`（D6）

`data/de/` 目前**只有 `countries.toml`**。

| 文件 | 散文量 | 德语页现在显示 | 优先级 |
|:--|:--|:--|:--|
| `data/faqs/<iso>.toml` | 50 文件 × **10 组** Q/A = **500 组** | 英文 | ★高（国家页 FAQ） |
| `data/countries.toml` → `quirks` | **101 条** | 英文 | ★高（国家页须知段） |
| `data/titlesegments.toml` | **50 条** `<title>` 片段 | 英文（`Best Japan eSIM 2026: …`） | ★高（**用户直接看到**） |
| `data/carriers.toml` | `info.detail[].strong/weak`、`profiles[].note` | 英文 | 中（网络段） |
| `data/providers.toml` → `tagline`/`strengths`/`weaknesses`/`brand.info`/`policy.*_note` | 10 品牌 × 约 8 条 ≈ **80 条** | 英文 | 中（品牌页） |
| `data/plans/<brand>.toml` → `fup_note` / `plan.name` | `fup_note` 数千条但**只有十几个不同值**；`name` 同理 | 英文 | 中（见下方技巧） |
| `data/networkreports.toml` | 50 国 Ookla/Opensignal 引用 | 英文 | 低（专有名词多，多数不译） |
| `data/devices.toml` | 机型名 + `source_note` | 英文 | 低（型号本来不译） |

**两条技巧**

**① `fup_note` 不要逐个翻** —— 先去重看有几个值，再决定：

```bash
python -X utf8 -c "
import re,collections,pathlib
c=collections.Counter()
for f in pathlib.Path('data/plans').glob('*.toml'):
    c.update(re.findall(r'fup_note\s*=\s*\"([^\"]*)\"', f.read_text(encoding='utf-8')))
print(len(c),'个不同值'); [print(v,k) for k,v in c.most_common(8)]"
```

- **省事版**：只译那十几个值，脚本按值批量替换。
- **正确版**（推荐，一劳永逸）：把 `fup_note` 改成**结构化字段**
  （`fup_gb = 3` / `fup_speed = "1Mbps"`），模板用 i18n 拼 —— 加第三第四种语言时**零翻译成本**。
  ⚠️ 这与 `fup_allowance` 拆分（长期未动的欠账）是同一件事，**建议合并成一轮做**。

**② 深合并的数组陷阱** —— Hugo 的 `data` 合并：**map 递归合并，数组整体替换**。

```
merge (dict "JP" (dict "name" "Japan" "quirks" ["a" "b"]))
      (dict "JP" (dict "name" "Japan-de" "quirks" ["a-de" "b-de"]))
→ name 覆盖 ✅  quirks 整体替换 ✅（不是逐条合并）
```

含义：`quirks` / `carriers` / `neighbors` / `images` 这些数组**要么不写（继承英文），要么整段重写**。

⚠️ `data/de/` 下文件名必须与英文侧**完全一致**（`jp.toml` 不是 `JP.toml`）——
模板用 `index site.Data.faqs (lower .Params.iso)` 取值。

---

## 6. 阶段 D · 页面本体 → `content/de/`（D7–D8）

### 6.1 待办与做法

| 批 | 目标 | 数量 | 做法 |
|:--|:--|--:|:--|
| **D7** | `content/de/compare/<国>/<品牌>.md` | **499** | ★**脚本批量**，正文本来就是空的（只有 front matter），见 §6.2 |
| D7 | `content/de/compare/<a>-vs-<b>.md` + `matchups.md` | 45 | 脚本批量 |
| D7 | `content/de/esim-providers/<品牌>.md` | 10 | 脚本（正文编辑层需手写，2–3 段） |
| D7 | 缺失栏目 `_index.md`（`esim-providers` / `esim-deals` / `tools`） | 3 | 复制英文骨架改德语 |
| **D8** | `content/de/guides/best-<区域>-esim.md` | 5 | 手写（依赖 D2 的 `guides/region` 整句化） |
| D8 | `content/de/guides/<slug>.md`（教程类） | 5 | 手写 |
| D8 | `content/de/networks/<国>.md` | 12 | 手写（每篇 5–6 个该国独有 H2） |
| D8 | `content/de/research/<slug>.md` | 5 | 手写（写作量最大） |
| D8 | `content/de/tools/`、`esim-deals/`、`methodology`、`disclosure`、`about`、`contact`、`privacy`、`terms` | 8 | 手写；`privacy`/`terms` **建议早做**（法律要求本地语言） |

> **★ D7 的两个前置（第六十三轮补记，缺一不可）**
> 1. **先翻 i18n**：`compare_provider`(112) + `esim_providers_single`(124) + `compare_vs_single`(17) +
>    `compare_matchups`(15) + `esim_providers_list`(7) ≈ **275 条**仍是英文占位 —— `i18n/de.toml` 不翻，
>    生成出来的 554 张德语页就是「德语 URL + 英文正文」。
> 2. **先补 `layouts/compare/provider.html` 的本地化接线**：可见套餐名（第 379 / 558 行的裸 `plan.name`）
>    要过 `partials/plan-name.html`、JSON-LD 的 `Offer.name`（第 243 行）同理、`.fup` 与 `.fup_note`
>    要过 `partials/de-text.html`（`#reality` 区块的 `.fup_allowance` 目前仍是英文展示值）、
>    `$country.quirks` 同理。**这四处不补，499 页一生成就是英文。**

### 6.2 ★ 499 个品牌子页为什么不用手写

`content/en/compare/<国>/<品牌>.md` 的**正文是空的**（只有 front matter），
页面内容全部由 `layouts/compare/provider.html` 从 `data/plans/*.toml` 推导。
所以德语侧**只需生成 front matter**：

```yaml
---
title: "Airalo Japan eSIM"
iso: JP
provider: airalo
seo:
  description: "…德语…"
---
```

⚠️ **这些 md 必须存在**：`/de/compare/<国>/` 的「Which eSIM providers cover X」段与
`/de/compare/` 索引用它渲染 `.Pages`；缺一个 → 少一张卡。

⚠️ **`content/de/compare/_index.md` 是保命项** —— 缺了不是「少一页」而是**整站构建失败**
（5 个模板对 `/compare` 栏目直接 `.Pages` 没有 nil 保护 → `nil pointer evaluating page.Pages`，
**连英文站也构建不出来**）。已有 ✅，别删。

### 6.3 脚本化的正确姿势（三条）

1. **从英文侧复制骨架，只换 `title` + `seo.description` + 删 `noindex`**。
2. **`iso` / `provider` / `layout` 等机器字段原样保留**，绝不改。
3. **日期的处理**：`lastmod` 不要用构建日（第五十三轮的定稿口径 —— 页面上每个日期都要能回溯到一条自动规则）。
   新页首次生成时用 `date` = 生成当日即可，之后由 `stamp_checked.py` 机制接管。

### 6.4 ★ 反同质化自证（D7/D8 的验收）

新生成的 499 + 45 页**很容易变成「换个国名的同一页」**。落完后跑：

```bash
python -X utf8 scripts/audit_boilerplate.py --type provider_sub --group-by brand
python -X utf8 scripts/audit_boilerplate.py --type provider_sub --group-by country
```

判据（第五十六轮定稿）：

- **反同质化靠「逐页派生量」**，不靠「换措辞」（换措辞是反向操作，Google 判定原文是
  *"substantially the same regardless of minor variations"*）。
- **跨页模块 md5 去重 = N**：把某模块在全部 N 页产物里抽文本算 md5，去重后必须 = N。
- **槽位要覆盖到每一个字段，包括手写的**（第五十六轮 Q4 的教训：14 国共用套话躲过所有检查）。
- 德语侧的额外风险：**德语的搭配与语序**会让「模板化」更明显（合成词长、句式固定），
  所以德语页的品牌卡/FAQ 尤其要检查。

---

## 7. 阶段 E · 解除 `noindex` 与 SEO 收尾（D9）

### 7.1 解除 noindex

现在有 **54 个**德语页带 `noindex: true`（50 国家页 + `compare/` 栏目 + `guides/` + `networks/` + `research/`），
每处都留了注释。**只删 `noindex: true` 这一行**，注释留着。删了之后三件事自动发生：

| 自动变化 | 机制 |
|:--|:--|
| 进 `/de/sitemap.xml` | `partials/sitemap-urls.html` 有 `{{- if not .Params.noindex -}}` 过滤 |
| 生成 hreflang 配对 | `partials/head.html` 只对可索引译文发 hreflang（第五十三轮修好） |
| 与英文页互指 | 同上 |

⚠️ **顺序铁律**：D9 必须在 D7/D8 之后。**正文还是英文就解禁 = 让 50 个半英半德页进索引**，
比 `noindex` 更糟（薄内容 + 语言混杂会拖累整个 `de-DE` 站点的质量评估）。

### 7.2 `x-default`（可选，但推荐）

`head.html` 的 hreflang 块补一行：

```html
<link rel="alternate" hreflang="x-default" href="{{ site.Home.Permalink }}">
```

⚠️ 这会给**每一页**（含英文 646 页）加一行 → 属预期变更，要**同步重建零回归基线**
（`--write-manifest`），并确认 diff 只多这一行。

### 7.3 `robots.txt` 声明德语 sitemap

```
Sitemap: {{ .Site.BaseURL }}sitemap.xml
Sitemap: {{ .Site.BaseURL }}de/sitemap.xml
```

### 7.4 Google Search Console

1. 提交 `https://www.esimsift.com/de/sitemap.xml`。
2. 「国际化」报告确认 en/de 配对无 error（若出现 `hreflang → noindex` 就是 §10.4 的问题复现了）。
3. 「覆盖率」确认德语页随 `noindex` 删除逐步转为「已编入索引」。
4. 观察德国区曝光是否起来（→ `de-DE` 的 `<html lang>` 与 `og:locale` 已在基础设施里就位）。

### 7.5 总验收

```bash
npm run build                                                  # 十一项闸门全绿
python -X utf8 scripts/verify_no_regression.py --diff docs/regression-manifest.json   # 英文零回归
python -X utf8 scripts/i18n_coverage.py de                     # 已译 = 1173（100%）
python -X utf8 scripts/check_i18n.py                           # ERROR 0 / WARN 37
python -X utf8 scripts/check_hreflang.py                       # 配对 0 error
grep -rl "noindex" content/de/ | wc -l                         # 应为 0
find public/de -name '*.html' | wc -l                          # 应从 56 涨到 645
```

---

## 8. 加第三种语言（fr / es / it / ja / …）

阶段 A–E 完整复制一遍。另外这 4 点「第二语言时不需要、第三语言时必须」：

1. **`hugo.toml` 的 `weight`**：`en = 1`，后续 `2, 3, 4…`。
   `hugo.Sites` 按 weight 排序，切换器顺序与「取默认语言站」都依赖它。
2. **`i18n/<lang>.toml` 必须一次性建齐 1173 个 key**（英文占位也行）—— 少一个就 build FAIL。
3. **`content/<lang>/compare/_index.md` 必须存在** —— 缺了整站构建失败（§6.2）。
4. **`data/<lang>/` 只放要覆盖的文件** —— 深合并会继承英文。

最小可跑清单：

```
hugo.toml                    → [languages.xx] + [languages.xx.params]（重写 tagline/description）
i18n/xx.toml                 → 1173 key（可全英文占位）
content/xx/_index.md         → 首页 front matter（<html lang> 靠它）
content/xx/compare/_index.md → 保命项
content/xx/{guides,networks,research}/_index.md
data/xx/countries.toml       → 国名（可先不翻）
```

---

## 9. 命令速查

| 目的 | 命令 |
|:--|:--|
| 完整构建（上线前必跑） | `npm run build` |
| 只重建 Tailwind（改过模板 class） | `npm run build:css` |
| **英文零回归 + 变更归因** | `python -X utf8 scripts/verify_no_regression.py --diff docs/regression-manifest.json` |
| 确认改动无误后重建基线 | `python -X utf8 scripts/verify_no_regression.py --write-manifest docs/regression-manifest.json` |
| 翻译进度 | `python -X utf8 scripts/i18n_coverage.py de` |
| 模板硬编码/碎片清点 | `python -X utf8 scripts/check_i18n.py` |
| hreflang 配对 | `python -X utf8 scripts/check_hreflang.py` |
| 反同质化 | `python -X utf8 scripts/audit_boilerplate.py --type provider_sub --group-by brand` |
| 本地预览 | `npm run dev`（⚠️ §10.1） |

---

## 10. 坑清单（本机实测踩过）

### 10.1 `public/` 被 dev server 覆盖成 localhost ★最危险

`hugo server` 会把 `public/` 重写成 `baseURL = http://localhost:1313/` 的版本 ——
`public/sitemap.xml` 和每页 canonical 全变成 localhost。**直接把这份 `public/` 上传 = 事故级。**
（已用 `--renderToMemory` 缓解，但仍要按下面三步确认。）

```bash
tasklist | grep -i hugo                                       # 应无输出
npm run build
grep -o '<link rel="canonical"[^>]*>' public/index.html       # 必须是 https://www.esimsift.com/
```

第五十二轮起 `check_dates.py` 的 A 组已把这条变成构建闸门（`public/` 含 `localhost` 直接 FAIL）。

### 10.2 `contentDir` 不写会「静默出错」

`[languages.de]` 里不写 `contentDir`，Hugo 会把 `content/en` 也当德语内容 ——
`/de/` 下全是英文页，**且不报错**。

### 10.3 根 sitemap 会被换成 `<sitemapindex>`

加第二个语言后 Hugo 默认把根 `/sitemap.xml` 换成指向 `/en/` + `/de/` 的 index。
英文 URL 在根路径，这样等于宣告「英文站在 `/en/` 下」→
已用 `layouts/sitemapindex.xml` 覆盖成默认语言的 `<urlset>`。

⚠️ `sitemapindex.xml` 的上下文**不是 Page**，里面写 `.Data.Pages` 会**静默中止构建**
（`hugo --quiet | tail` 看起来像"模板没生效"，实际是构建失败、`public/` 留的是上一版）。

### 10.4 `hreflang` 双侧都要守

只守目标侧不够 —— 第五十三轮实测：54 个 `noindex` 德语页向外发 `hreflang="en-us"`，
英文侧因译文 noindex 而不回指 → **单向标注**，GSC 报 *No return tags* 并**整体忽略这组标注**。
修法：`{{ if and (not .Params.noindex) (ne .Kind "404") }}` 把**自引用与译文 range 一起**包住。
守卫 `check_hreflang.py`（A 自身 noindex 不发／B 目标产物必须存在／C 必须互惠／D 目标不得 noindex）。

### 10.5 `{{ if }}` 不裁剪左侧空白

新增条件块不写 `{{- if }}` / `{{- end }}`，会给**每一页**多输出一个换行。
第五十三轮真实踩到：给 `head.html` 写 6 行模板注释 → **701 页**各多一个 `\n`，
归因数字从 555 跳到 701 当场作废。**`layouts/**` 里的模板注释一律写单行。**

### 10.6 数据岛里的本地化字段必须 `htmlUnescape`

同一个本地化字段若既有 HTML 渲染点又有 JSON 渲染点，**JSON 那一路必须 `| htmlUnescape`**
（`jsonify` 会把 `&amp;` 编成 `\u0026amp;`，前端拿到字面量 `&amp;`）。HTML 点不要脱。

### 10.7 Go `html/template` 在 `<script>` 里必然把 `/` 转义成 `\/`

`/de/compare/` → `\/de\/compare\/`。`safeJS`/`safeHTML`/`safeURL`/`safeHTMLAttr`/`printf`/`string`
**六种写法全绕不开**。JS 里 `'\/' === '/'` 语义恒等，**别为它折腾**，在验证脚本的归一化里处理即可。
真要干净就别把路径插进 JS 字符串（改 `data-*` 属性）。

### 10.8 深合并：map 递归，数组整体替换

见 §5 技巧②。

### 10.9 `check_headings.py` 的标点禁令是全语言的

`STRICT = [,;:—–]` 对所有语言禁止 h2/h3 里的这些标点；`RELAXED = [,;:]` 只对白名单语言
（含 `de`）额外放行 `—–`。**逗号/分号/冒号任何语言都不许出现在 h2/h3 里。**

### 10.10 bash heredoc 会吞掉 Python 正则里的反斜杠

已踩两次（`\s` 被 shell 吃掉，替换静默失败）。**规矩：正则先写进文件再执行**，
或用单引号 heredoc（`<<'PY'`）。

### 10.11 模板空白语义别靠推理，用微型 probe

建一个只有 1 个 layout + 1 个 content 的临时 Hugo 站点，把可疑片段渲染一遍看 `repr()`。
比推理 10 分钟可靠（本机已用此法解决 head 空白、JS 转义两处）。

### 10.12 改仓库文本文件一律用 bytes

`Path.write_text()` 在 Windows 下会把 LF 转成 CRLF（第五十二轮把 `i18n/en.toml` 整份转掉、
`git diff` 只显示 13 行变化，极具迷惑性）。
**规矩：非新建文件一律 `read_bytes()` → `decode` → 处理 → `encode` → `write_bytes()`**，
改完立刻 `read_bytes().count(b'\r\n')` 复核。

### 10.13 ★★ `i18n` 的值会被 Hugo **当 Go 模板执行** —— 值里只能写 `{{ .name }}`

2026-10-09 D3 实测事故：`esim_deals_list__code_math_tail` 的值写成了

```toml
esim_deals_list__code_math_tail = "... in how many of our {{ len $d.countries }} tracked countries ..."
```

产物里那一整句**直接消失**（`<p>A code changes what <em>you</em> </p>`），
而**十一项闸门全绿** —— 因为所有守卫只查「产物里有没有残留 `{{`」，
而这里是**一句话整个没了**，没有残留可查。

根因：Hugo 的 `i18n` 拿到 `(dict …)` 之后，把值字符串**当 Go 模板执行**（data = 那个 dict）。
`len` 不是 Go 模板函数、`$d` 也不存在 → 求值失败 → Hugo **把整条值渲染成空串**，不报错不警告。

**正确写法**：值里只放 `{{ .n }}`，由调用方传值 ——

```go
{{ i18n "esim_deals_list__code_math_tail" (dict "n" (len $d.countries)) | safeHTML }}
```

已固化为守卫：`check_i18n.py` 的 `bad_placeholders()` —— 两侧语言文件的**每个值**里，
出现的 `{{ … }}` 必须是 `{{ .name }}` 形状，否则 ERROR。`--selftest` 双向自证
（反例 `{{ len $d.countries }}` / `{{ $x }}` 必须红，正例 `{{ .a }} and {{ .b }}` 必须绿）。

### 10.14 ★★ 守卫不许有**英文硬编码判据**（语言盲）

同一天的第二个事故：德语页把 `g_unlimited` 从英文占位 `Unlimited` 译成 `Unbegrenzt` 之后，
`verify_no_regression.py` 的 `[C]` 检查（`"unlimited" in cell.lower()`）把
**50 个德语国家 Hub 页的 4602 处完全正常的套餐行**全判违规 —— 而英文侧一处没问题。

危险点在于**它是被「翻译进展」触发的**：占位还是英文时它看起来一切正常，
一旦 D5 真的开始翻译，惩罚就落到**做得对**的那一侧。同类问题在
`verify_provider_pages.py` 第 11 项里抄了第二份（当时因为德语品牌子页还没生成而侥幸没炸）。

**解法**：判据从数据现读，不从字面量推。新增 `scripts/unlimited_labels.py`，
从 `i18n/*.toml` 现读 `g_unlimited` + `compare_provider__trip_data_unlimited` 的**全部语言取值**，
两个守卫共用同一份（**别抄第二份 —— 抄第二份就是第二处会错的地方**）。
加第三种语言（fr/es/…）自动生效。`--selftest` 扩到 **17 项**：既证明「放过正确译文」，
也证明「计量档却标成 `Unbegrenzt` 仍要红」—— 只加前者等于把检查改瞎。

### 10.15 改**既有** key 的值之前，先查它的**调用形态**

D3 收尾时差点造成一次全站事故：我给 vs/ep 模板抽了一个「since + 年份」的共用 key，
名字选了 `g_since`。而 `g_since` **早就存在**，且

```go
{{/* layouts/compare/single.html:632 */}}
<p class="text-xs text-ink-400">{{ i18n "g_since" | safeHTML }} {{ $p.founded }}</p>
```

是**不带 dict** 调的 —— 值只能是裸词 `since`。把值改成 `"since {{ .year }}"`
就会让 **100 个国家页**渲染出 `since <no value>`（`check_output.py` 会抓，但代价是一次全量构建）。

**规矩**：`i18n_add.py` 报「**~N 原地更新**」而不是「+N 追加」时，**先停下来查这 N 个 key**。
`grep -rn '"<key>"' layouts/` 看调用点，`git show HEAD:i18n/en.toml | grep '^<key>'` 看是否新增。
本次的正解是**复用既有调用形态**：`{{ i18n "g_since" | safeHTML }} {{ $p.founded }}`，
一个 key 都不新增。

---

### 10.16 ★★ `default "…"` 里的兜底文案是**守卫的盲区** —— 一次藏了 1515 处英文

D5 做「哪些未译 key 真的渲染在德语页上」的排查时才发现：`check_i18n.py` 报
**「0 处硬编码文案」**，而 `layouts/compare/single.html:482` 是这样的：

```go
<td>{{ .fup | default "No fair-use policy published — treat speed claims with caution" }}</td>
```

同一句话在 `layouts/compare/provider.html:561` 用的是 `default (i18n "…")` —— 两处**写法不一致**，
而走 `compare/single.html` 的那条路径正好服务 `/de/compare/<country>/`。
于是 **50 个德语国家页上一共印了 1515 次英文**，而十一项闸门全绿。

**为什么守卫看不见**：`i18n_extract` 收的是**紧邻 `{{ }}` 的文本**与属性值；
`default` 是管道算子，它的字面量实参两头都被 `{{ }}` 夹着，既不是 text_edits 也不是 frags。

**修法（已固化在 `check_i18n.py`）**：新增 `hardcoded_defaults()`，判据是
「字面量含空格 **且** 含一个 ≥4 个连续拉丁字母的 token **且** 不含 `$` `{` `\`」。
这样 CSS 类（`btn-out` / `h-9 w-9`）、数据哨兵（`official` / `compare`）不误报，
真文案必中。实测一次报出 **4 处**，全部是真文案；`its region` 是唯一需要显式白名单的
（50 国 `region` 字段实测 0 缺失 → 兜底永不触发，且它插进的是 `data/faqs` 的英文句子 = D6）。
`--selftest` 加了两组双向自证（7 个正例 / 3 个反例）。

**教训**：**「零硬编码」是个断言，不是事实 —— 它只覆盖扫描器看得见的写法。**
凡是宣称「某类问题已归零」的守卫，都要再问一句「它的判据覆盖了哪些**写法**」。
本次的 4 处里有 2 处（`The short answer` / `eSIM research questions people ask`）
只在英文页可见，属于**潜伏**，不改也会在「德语内容补齐后」突然变成泄漏。

### 10.17 ★★ 三条「改模板 = 改产物字节」的坑（第六十三轮，三条全是实测踩出来的）

本轮改的全是**纯文案**（把模板里的英文字面量换成 `i18n`）。理论上英文侧产物应当
**逐字节不变**，实际连撞三次 —— 三次都不在文案上，而在**模板动作周围的空白**。

**坑① 新增一个「独立的注释动作块」，会让产物多出空行。**

注释本身不输出，但**它前后的换行与缩进是字面文本**，会跟着写进 HTML：

```go
{{/* 这里写说明 */}}          ← 这个块自己占一行 → 产物多一个 \n
<div class="…">
```

一次改动里我加了 3 个这样的块，`--diff` 立刻报 **22 处变更、其中 18 个是英文页**
（英文页本来就该 0 变更）。全部是空白，与逻辑无关。
→ **修法：把说明并进「本来就存在」的注释块**（`aside-destinations.html` 顶部那块、
`compare/list.html` 的 `{{/* 排序键：… */}}`）—— 既有块的换行早已在产物里，加字不增行。

**坑② 在模板「头部」（首个输出标签之前）多插一行动作 = 多一个换行。**

`compare/list.html` 的 `{{ range }}` 里我需要一个 ISO 变量，于是加了：

```go
{{ range $c := $countries }}
  {{ $iso := . }}          ← 这行在首个输出 <div> 之前 → 产物多一个 \n
  <div class="…">
```

`--diff` 只报 1 个文件，而且是**英文页 `compare/index.html`**。逐一比对渲染文本
（`figcaption` / `starts cheaper in` / `Airalo vs`）**全部逐字节相同** —— 证明差异是空白不是文案。
→ **修法：不新建变量，直接在 `with` 作用域内传 `.`**：`(dict "name" $pick.name "iso" .)`。
（`{{ if }}` 不改变 `$` 绑定，但 `with` 内的 `.` 才是当前 ISO 串 —— 两者语义不同，别混。）

**坑③ 注释块里出现「成对的花括号」，会让注释文字被判成硬编码文案。**

`i18n_extract.scan()` 只把 `<!-- -->` 当注释，**`{{/* */}}` 不是** —— 它见到 `{{`
就当模板动作的开始，去找配对的 `}}`。于是注释里写了一句示例：

```
调用：{{ partial "aside-destinations.html" . }}
```

`scan()` 把 `{{ partial … }}` 当动作边界，**其后到注释末尾的说明文字成了「模板文本节点」**
→ `check_i18n.py` 报 2 处 `ERROR 硬编码文案未抽 i18n`，构建退出码 1。
→ **修法：注释里的示例去掉花括号**（写成 `partial "aside-destinations.html" .` 并注明「示例里不写花括号」）。
这条与 §10.13「`i18n` 的值会被当 Go 模板执行」同源，但**暴露在守卫侧**：
`{{ }}` 写在注释里不渲染，却会**改变扫描器对文件的解析**。

**教训：恒等判据（英文侧逐字节不变）不只在文案上成立 —— 空白也是字节。**
改模板前先问一句「我这一行**在产物里**占不占位」；`--diff` 报出「不该变的页」时，
**第一步是逐字节比对那份产物**（`cmp` / sha256），先分清「文案变了」还是「空白变了」，
再去找逻辑原因 —— 本轮三次全是空白，逻辑一次都没错。

---

## 11. 附：SEO 影响评估与发布节奏

### 11.1 现在可以发布吗？

**可以，英文 SEO 不受影响。** 依据：

| 检查项 | 结果 |
|:--|:--|
| 根 `/sitemap.xml` | 644 条英文根 URL，无 `/en/` 前缀 |
| 英文 646 页 | 零回归基线锁死（`verify_no_regression.py`） |
| 德语入库范围 | 只有 `/de/` 首页可索引；其余 **54 页** `noindex, follow` |
| `hreflang` 一致性 | ✅ 双侧已修（§10.4） |

发布前必做 §10.1 三步。

### 11.2 做完之后的收益预期

| 项 | 影响 |
|:--|:--|
| 英文 644 条 URL | **零影响**（URL / canonical / 内容都不变） |
| 德语可索引页 | 1 → **645** |
| 德语流量 | 从 ≈0 起量。德语长尾（`beste esim für japan` / `esim japan erfahrungen` / `esim kaufen ohne vertrag`）**是英文站拿不到的词** |
| 与英文站的关系 | 独立语言页 + 互相 hreflang → 不构成重复内容 |

### 11.3 三个「知道就好」的残留

1. **`/en/index.html` + `/en/sitemap.xml` 影子文件** —— Hugo 自动生成，config 关不掉。
   没被任何页面链接、也没提交给 GSC，对搜索中性。
2. **德语国家页 `<title>` 来自 `data/titlesegments.toml`** —— 德语侧没有对应文件时回退英文。
   这是 **D6 必须补的**，`noindex` 期间不影响 SEO。
3. **德语国家页 H1/H2 硬编码** —— 见 §1.3①，**D1 必须修**。

### 11.4 建议的发布节奏

```
第 1 步（现在）  → 发布当前状态：英文全量 + /de/ 首页（其余 noindex 占位）
第 2 步          → D1 + D5 的相应子批
                   → 德语站第一次真正「有德语内容」
第 3 步          → D2–D4 → D5 完成（全站 UI 德语化）
第 4 步          → D6 → D7（50 国家页 + 499 品牌子页解禁，德语站起量）
第 5 步          → D8（长文页）→ D9 收尾
```

**每个「发布」动作都要先跑 §0 红线 1 的 `--diff`**，确认英文零回归。

---

## 12. 执行记录

### 12.1 D1 已完成（2026-10-09）

范围：`layouts/compare/single.html`（德语 50 个国家页）+ `data/de/countries.toml`。

| 项 | 结果 |
|:--|:--|
| 碎片（`check_i18n.py`） | **79 → 1**（仅剩 `Opensignal ·`，品牌名，有意保留） |
| 全站碎片 | 603 → **525** |
| 新增 i18n key | **+103**（28 标题层 + 30 文本碎片 + 45 模板字面量），1173 → **1274** |
| 德语覆盖率（5 国国页样本，德/英功能词占比） | 19.3% → **33.7%**（英词 −2,987） |
| 十一项闸门 | 全绿 |
| 英文产物 | **652 页逐字节不变，英文页差异 = 0** |

三批 key 前缀：`compare_single__`（本轮新增 103 个全部落在这个命名空间）。

### 12.2 ★ 恒等判据当场抓出两个 bug（必须进坑清单）

D1 的第一条规则就是「英文侧是恒等变换 → 产物逐字节相同」。**第一次跑就红了**，
抓到两个只在德语站显现、肉眼极难发现的错误：

1. **i18n 值里已经带了 `$` 或标点时，模板里不要再补空格。**
   `{{ i18n "g_from_price" }} {{ printf "%.2f" }}` 渲染成 `from $ 7.00`，而改前是 `from $7.00`。
   正确写法是两个 `{{ }}` **直接相邻**。→ 每条替换都要按「渲染后字符串」比对，不能按「读起来像」比对。

2. **跨 key 传 dict 时，别把 `(dict "country" …)` 当成「值」嵌进外层 dict。**
   我定义了 `EDGE = '(dict "country" ($country.name_dat | default $country.name))'`，
   在 `i18n "k" EDGE` 位（**参数形态**）是对的，但写进 `(dict "brand" X "country" EDGE)`
   就成了嵌套 map，页面印出 **`All Airalo plans in map[country:Canada]`**。
   → **辅助常量必须分成「参数形态」与「值形态」两个变量**，一个变量两用必翻车。

### 12.3 ★ 验证装置变更：改用 HEAD 对照构建树

`verify_no_regression.py --diff` 的基线**每天都会失效**，原因见 §12.4①。
所以 D1–D5 的「英文零回归」判据改用**同一天构建的对照树**：

```bash
CTL="C:/Users/Administrator/WorkBuddy/2026-09-30-13-09-50/headctl"
mkdir -p "$CTL" && cd "D:/esimsift/esimsift" && git archive HEAD | tar -x -C "$CTL"
cd "$CTL" && hugo -d public      # 后台跑
```

然后逐字节比对 `$CTL/public` 与 `$ROOT/public` 的全部 `*.html`。
**判据：差异必须恰好 = 本批目标页；英文页差异必须 = 0。**

- 用 `git archive` 而非 `git worktree`/`git stash` —— 零 stash 风险、不污染主仓 `git status`。
- ⚠️ **Hugo 全量构建实测 362 秒（约 6 分钟）**，`npm run build` 全程 2–8 分钟。
  用 300 秒超时跑它会**被 SIGTERM 打断**，且伴随的 `git stash pop` 不会执行 ——
  **凡是「改源码再构建」的探测，一律用 `git archive` 到独立目录，绝不 stash。**
- 对照树不必每批重建（同日构建即可）；跨天后再比对要先重建。

### 12.4 ★ 顺带发现的两个既有缺陷（都不是本轮引入）

1. **`layouts/networks/single.html:115` 用构建日当「最后更新」**
   `<span class="badge …">Updated {{ time.Format ":date_medium" now }}</span>`
   → 实测同页：可见徽章 `Updated Oct 9, 2026`，而 sitemap 里同一页 `lastmod 2026-10-07`。
   **同页两个矛盾日期**，正是第二十五轮撤回 `now` 要修的毛病；`check_dates.py` 没拦住（守卫盲区）。
   代价：12 个 `/networks/*` 页每次部署都被无意义重写，`lastmod` 发噪声。
   **修复归入 D2**（`networks/single.html` 本就是 D2 的文件）。

2. **`check_i18n.py` 看不到 Go 模板里的字符串字面量**（只扫 HTML 文本节点）。
   `compare/single.html` 的 `$tiers` / `$personas` / `$gf` / `$guideCards` 里藏着
   **约 30 处用户可见英文**，守卫完全静默、产物直接印英文。
   → **§1.3 的「566 处碎片」低估了模板侧英文约 30–40%。**
   D1 已把这 30 处一并整句化（只照碎片列表做会漏掉它们）。
   **后续建议**：给 `check_i18n.py` 加一条「模板字符串字面量」扫描
   （判据：`dict`/`slice` 里的 `label`/`hint`/`why`/`blurb`/`head`/`sub` 等用户可见字段，
   值不是 `i18n` 调用即告警），否则 D2–D4 会重复踩这个盲区。

### 12.5 下一步（D2，已完成 → 见 §12.6）

按 §2.2 推进 **D2**：`networks/single.html`(50 碎片) + `networks/list.html`(44)
+ `guides/region.html`(42) + `guides/single.html`(20)，
并在这一批顺手修掉 §12.4① 的 `now` 日期缺陷。

---

### 12.6 D2 已完成（2026-10-09）

范围：`layouts/networks/single.html` + `layouts/networks/list.html` + `layouts/guides/region.html`
+ `layouts/guides/single.html`（四个模板），并修掉 §12.4① 的 `now` 缺陷。

| 项 | 结果 |
|:--|:--|
| 四模板碎片 | **156 → 4**（`networks/single` 50→4、`networks/list` 44→0、`guides/region` 42→0、`guides/single` 20→0） |
| 全站碎片 | 525 → **373** |
| 新增 i18n key | **+123**（122 条批次 + 1 条 `networks_list__speed_band`），1274 → **1397**（en = de 逐 key 对齐） |
| 模板引用 key | **1367**，未定义 **0** |
| 十一项闸门 | **EXIT=0**（`0 error / 0 warning`，模板层硬编码 0） |
| 恒等判据 | 702 页中差异 **63**：50 `de/compare/*`（D1）+ 1 `de/networks/index.html`（D2 首次生效）+ 12 `en/networks/*`（`now` 修复）。**英文非预期变更 = 0** |
| 德语覆盖（德语功能词 ÷ 德+英功能词，现算） | `de/compare` 50 国：**41.3% → 59.7%**；`/de/networks/`：**8.4% → 23.1%** |
| 英文侧一致性 | `en/networks` 12 页 改前/改后 功能词计数 **753 / 11117 完全相同** |

`networks/single.html` 残留的 4 处碎片是 `Opensignal` / `Ookla` 两个**品牌名**（各出现 2 次），
**有意保留** —— 它们不是文案，是专有名词，翻译反而是缺陷。

**`now` 缺陷修复 —— 三处同源（`networks/canada/index.html` 实证）：**

| 落点 | 修复前（HEAD） | 修复后 |
|:--|:--|:--|
| 页首徽章 | `Updated Oct 9, 2026`（= 构建日） | `Updated Oct 7, 2026`（= 数据核对日） |
| 正文脚注 ×2 | `at the Oct 9, 2026 snapshot` | `at the Oct 7, 2026 snapshot` |
| `sitemap.xml` `lastmod` | `2026-10-07T00:00:00Z`（**与徽章矛盾**） | `2026-10-07T00:00:00Z`（一致） |

实现：`layouts/networks/single.html` 取 `$s.checkedDate`（来自 `partials/country-stats.html`），
缺日期时回退 `compare_single__date_monthly` —— 沿用第二十五轮的四口径纪律：**绝不 fallback 到 `now`**。
全站复扫后**只剩 `now.Year`**（年度粒度，在 `<title>` 里，可接受）→
**回归基线从此日期稳定**，`verify_no_regression.py --diff` 的日常判据重新可用
（已 `--write-manifest` 重置为 **702 页**；`--selftest` 16 项通过）。

### 12.7 ★ D2 新立的三条坑（都关于「产物字节」）

1. **「不新增行」纪律（本轮最重要的操作约束）。**
   整句化在英文侧是恒等变换，但**每新加一行都会往产物里多写一个换行** → 恒等判据必红。
   所以：**新变量的定义必须挂到已有行的行尾**；**说明文字必须写进已有的 `{{/* */}}` 块内部**（块内换行不产出）。
   D2 第一次构建正因此红了 65 页；把 4 处「独立占行的变量 / 注释」并回已有行后收敛到 63（全部预期）。
   行数变化：`networks/single` 425→422、`guides/region` 263→260、`guides/single` 412→411。

2. **`i18n` 值不做 HTML 转义 —— 转义形态必须在模板或数据侧解决。**
   数据里的 `&` `+` `<` `>` 原本在模板**文本上下文**被 Hugo 转义成 `&amp;` / `&#43;`，
   搬进 i18n 值 + `| safeHTML` 后就成了裸字符 → 产物变化。D2 当场抓到两处：
   - `partials/region-label.html` 的返回值是**已转义**形态（`g_africa_amp_middle_east = 'Africa &amp; Middle East'`）：
     HTML 里用 `| safeHTML`（正确）；**喂 JSON-LD 前必须先 `htmlUnescape`**，否则 JSON 中会出现 `&amp;`。
   - `data/devices.toml` 的 `other.since = "misc. 2022+ models"`：只把前缀搬进 i18n，
     **`{{ $b.since }}` 留在模板里**（保住 Hugo 的 `&#43;`）。

3. **`i18n` 的返回值不要再当参数喂给 `i18n`。**
   变量里**存 key 名**，取值处再 `{{ i18n $key }}`。
   （`$box` / `$boxTitleKey` / `$boxIntroKey` / `$boxNoteKey`、`$gfKey` 都是这么改的。）

另有一条**空格教训**：**把「空白 + 文本」一起收进 key 时，空格必然丢一次。**
`"</a>. Sources: "` 整段收进 key 后渲染成 `.Sources:` → **空格留模板**（`</a>. {{ i18n … }}`），值只留 `Sources:`。
凡是收进 key 的字符串，都要数一遍首尾空格。

### 12.8 判据装置经验（D2 追加）

- **恒等判据是本阶段唯一铁证。** 英文侧整句化的产物**必须逐字节相等** ——
  这比任何人工通读都可靠，能抓到肉眼看不见的丢词、丢空格、多空格、转义不一致。
- **对照树的 11 个「假差异」要会认。** `git archive HEAD` 在 `core.autocrlf=true` 下会把
  `static/` 里的 `favicon.svg` 与 `img/flags/*.svg`（共 11 个）**导成 CRLF**，而未带 `eol=lf` 属性的
  `static/**` 在构建时不转换 → 逐字节比对恒差。判法：**CRLF 归一后相等**即为假差异。
  （`.gitattributes` 目前只锁 `layouts/**` 与 `i18n/**` 为 LF；`static/**`、`docs/**`、`content/**`、`data/**` 未锁。）
- **`css/tailwind.css` 只在产物侧存在**（`static/css/` 是构建产物、未进版本库）→ 「仅 PUB 有」属正常，不是缺陷。

### 12.9 下一步（D3）

按 §2.2 推进 **D3**：`layouts/esim-providers/single.html`(113) + `layouts/compare/vs-single.html`(79)
+ `layouts/compare/matchups.html`(19) + `layouts/esim-deals/list.html`(27) —— 合计 **238 处碎片**。

⚠️ 本批两个额外注意事项：
1. `vs-single.html` 的 **5 处内联 `<script>` 用户文案**是已知欠账（`check_i18n.py` 会 WARN）——
   要么并入本批改成 `data-*` 注入，要么明确记入后续批次。
2. `esim-providers/single.html` 里的品牌档案（`strengths` / `weaknesses` / `info`）是**数据层英文**，
   属 D6 范畴；本批只做模板层整句化，别越界。

### 12.10 D3 已完成（2026-10-09）

范围：`layouts/esim-deals/list.html` + `layouts/compare/matchups.html`
+ `layouts/compare/vs-single.html` + `layouts/esim-providers/single.html`（四个模板，全部 `.html`）。

| 项 | 结果 |
|:--|:--|
| 四模板碎片 | **238 → 0**（`matchups` 19→0、`deals/list` 27→0、`vs-single` 79→0、`esim-providers/single` 113→0） |
| 全站碎片 | 373 → **135**（余下是 D4 的 research/tools/`_default` + 非页面产物） |
| 内联脚本文案 | **5 处，未动**（按 §3.3 归属 D4，见下） |
| 新增 i18n key | **+101**（`matchups` 8 + `deals` 20 + `vs` 25 + `providers` 48 − 复用；`g_since`/`g_from_price`/`g_vs`/`g_app_based` 走复用） |
| i18n 总 key | 1397 → **1498**（en = de 逐 key 对齐，**德语值与 en 同批写入，不留新占位**） |
| 模板引用 key | **1468**，未定义 **0** |
| 十一项闸门 | **EXIT=0**（`0 error / 0 warning`；`check_headings` 18303 个 h2/h3 `bad: 0`） |
| ★ 恒等判据 | 全树 1297 文件比对：**逐字节相同 1217 / 假差异 11（CRLF）/ 真差异 68**。68 处全部是**德语页**（196 条翻译生效）+ **`en/networks/*` 12 页**（D2 的 `now` 修复，§12.6 已记）。**D3 对英文侧非预期变更 = 0** |

**恒等判据是本批最硬的证据**：`esim-deals/index.html`（440109 B）、`compare/matchups/index.html`
（108000 B）、45 张 `compare/*-vs-*/index.html`、11 张 `esim-providers/*/index.html`、
499 品牌子页、101 国家页 —— **与 HEAD 对照树逐字节相同**。
238 处整句化里任何一处丢词、丢空格、多空格、转义不一致、Hugo 动作写法不一致，都会当场变红。

**做法（四步固定流程，可复用）**：
1. `scripts/fragdump2.py`（临时工具，复用 `i18n_extract.scan()`）导出**碎片 + 左右 70 字上下文**——
   不做子串猜测，位置是实测的；
2. 一个碎片组 → 一个 key + `dict` 参数，**en 值经渲染后必须等于原字面量**（逐字节）；
3. 规则脚本用「每条 `old` 恰好命中 N 次」做前置断言，**全部通过才 `write_bytes`**（原子性）；
4. 落盘后重扫碎片必须 **0**，再跑全量构建 + 对照树比对。

**本批的三个事故（全部已固化为守卫，见 §10.13/10.14/10.15）**：
- `{{ len $d.countries }}` 写进 i18n 值 → **整句渲染成空**而十一项闸门全绿（§10.13）；
- `[C]` 守卫的英文硬编码判据 → 德语页 **4602 处正常行误报**（§10.14）；
- `g_since` 是个**既有且不带 dict 调用**的 key → 差点让 100 个国家页输出 `<no value>`（§10.15）。

**未做（明确归属 D4，不算欠账）**：`vs-single.html` 的 5 处内联 `<script>` 文案
（`'Pick two providers'` / `'Opening the computed … '` / `'One more pick …'` 等）。
按 §3.3 归 D4 统一改 `data-*` 注入 —— 本批**故意不动**：改了会改 `public/compare/*-vs-*/`
里的 `<script>` 源码，等于往「恒等判据」里掺进一类**非恒等**变更，把本批唯一的铁证弄浑。

**下一批（D4）**：`research ×3`(53) + `compare/list`(12) + `tools/list`(11) + `_default/*`(3)
+ 上述 5 处内联脚本。之后 D5 翻 `i18n/de.toml`（现 **710 条占位**，含本批 101 条已译 → 实际待译更少）。

---

### 12.11 D5 第一批已完成（2026-10-09）—— 德语 i18n 面收口

**先修口径，再动手。** D3/D4 一直用「de 值 == en 值」当「未译」的判据，得到 **710 条**；
但 710 里绝大多数**根本不会渲染在德语页上**（德语侧只有 55 页：`/de/compare/` 索引 + 50 国
+ `/de/research/` + `/de/networks/` + `/de/` + `/de/guides/`）。两次收紧：

| 口径 | 数 | 问题 |
|:--|--:|:--|
| ① de 值 == en 值 | 710 | 不含「是否真的渲染」 |
| ② 文本匹配（en 长字面量出现在德语产物里） | 121 | **短串误命中**：`Capped`/`unlimited`/`Region` 这种词会撞上别处的英文 |
| ③ **德语模板闭包 ∩ 未译** | 150 | 权威口径：从德语页真正使用的 14 个根模板出发，递归展开 21 个 partial |
| ④ ③ **∩ 产物文本命中** 并剔除非德语页型 | **99** | 最终工作清单 |

③→④ 剔掉的三类（**都不是 i18n 的活**）：

- `guides_single` 27 + `guides_region` 16 = **43**：德语侧**根本没有 guides 内容页**
  （`content/de/guides/` 只有 `_index.md`）→ 属**内容本地化**，不是 key 翻译；
- `networks_single` 1：德语侧只有 `/de/networks/` 索引，无子页；
- 7 个 `g_*`（`g_esim`/`g_gb`/`g_link`/`g_sift`/`g_tools`/`g_unit_gb`/`g_unit_mb`）
  = **德英同形词**（eSIM / $/GB / Link / Sift / Tools / GB / MB），本来就该一样。

**本批成绩**

| 项 | 结果 |
|:--|:--|
| 译入 | **93 条**（`compare_list` 7 + `compare_provider` 1 + `compare_single` 53 + `research_list` 32） |
| 有意保留（同形） | **6 条**（`Multi-IMSI` / `{{ .min }}–{{ .max }} Mbps` / `Ookla Speedtest Global Index` / `, Opensignal.` / 两个 `$…·…·…` 格式串） |
| ★ **守卫盲区** | `default "…"` 兜底文案 4 处（见 §10.16），其中 1 处**在 50 个德语页上印了 1515 次英文** |
| 新增 i18n key | **+2**（`g_view_deal`、`research_list__faq_heading_default`）+ 1 条补译 → 1498 → **1500** |
| ★ 恒等判据 | 产物 vs 改动前快照：**逐字节相同 1247 / 真差异 50 / 仅A 0 / 仅B 0**。50 处**全部是德语国家页**（FUP 译文）→ **英文侧 0 变更**，证明 `default "…"` → `i18n` 的重构对英文是**行为保持**的 |
| 十一项闸门 | **EXIT=0**；`check_i18n` **0 硬编码 / 0 default 兜底文案 / 1500 key / 未定义 0** |
| 零回归基线 | 已刷为 **702 文件**，复验「0 变更、逐字节相同」 |

**德语可见未译：150 → 57**（产物体文本铁证可见的从 **77 → 2**，那 2 条是专有名词）。
57 的构成：`guides_*` 43（内容本地化）+ 同形词 13 + `networks_single` 1 ——
**可执行的 i18n 项 = 0**。

**剩余英文在哪（诊断，决定下一批）**：`/de/compare/<country>/` 的德语功能词占比 **62.1%**
（英文 18711 / 德语 30606）。拆开看：

| 区块 | 英文 / 德语 | 德语占比 |
|:--|--:|--:|
| **FAQ 问答块** | 226 / 1 | **0.4%** ← 全站 50 页合计 **7953 个英文功能词 = 42.5%** |
| 表内 `<table>` | 160 / 250 | 61.0% |
| 表外 `<p>` 段落 | 262 / 272 | 50.9% |

→ **德语页剩余英文的主体是 `data/faqs/*.toml`（D6 数据层），不是 i18n。**
D5（i18n 面）到此收口，**下一批应该做 D6**：`data/faqs` 德语版 + `data/plans` /
`data/providers.toml` 里的 `policy.*_note` 与 `fup_note`（英文数据层文案）。

**本批新立的纪律**

1. **「未译」必须同时满足「值 == 英文」与「真的渲染在该语言页面上」** —— 只看前者会把
   710 里的 617 当成待办（实际是别的语言/页型的事），只看文本匹配会被短串骗。
   权威判据 = **该语言页型的模板闭包 ∩ 未译 key**。
2. **同一句话在 `default "…"` 与 `default (i18n "…")` 两种写法下必须统一** ——
   不一致就是「一条路径有翻译、另一条没有」，而**只有前者会被守卫漏掉**。
3. **德英同形词要显式记账**，不能靠「值 != 英文」的判据假装归零（`eSIM`/`GB`/`$/GB` 本来就相同）。



### 12.12 D6 第二批已完成（2026-10-09）—— 套餐名 `name` 本地化

§12.11 量出「`/de/compare/<country>/` 德语功能词占比 62.1%」里剩余英文的**第二大块**，就是套餐表里的
`data/plans/*.toml` 的 `name`（供应商原始产品名）。本批把它按**词**本地化。

**机制**（新增 `layouts/partials/plan-name.html`，11 个渲染位点全部改走它）：

| 层 | 事实来源 | 例 |
|:--|:--|:--|
| 目的地国名 | `data/countries.toml[iso].name` → `data/de/countries.toml[iso].name` | `Austria eSIM 50GB / 30 Days` → `Österreich eSIM 50GB / 30 Tage` |
| 非规范国名别名 | **新数据文件** `data/planaliases.toml` | CZ `Czech Republic` / TR `Turkey` / IE `Republic of Ireland` |
| 结构词 | `i18n` 新增 `plan_name__*` **8 个 key** | `Unbegrenztes Datenvolumen` / `Tage` / `Tag` / `Lokal` |

**三条支撑事实（可复算，守卫逐年断言）**：

1. 9,095 条套餐名里**没有任何一条提到别的国家** —— 全部是本页目的地的名字 ⇒ 按 ISO 取一个替换目标就够。
2. 「国名 + ` Mobile`」在数据里**只有** `Canada Mobile` / `Macao Mobile` 两个品牌形态 ⇒ 该形态必须跳过国名替换。
3. 品牌名（`Abrazo!` / `Belganet` / `Uki Mobile` / `Chinacom` …）是商标，**一律不译**。

**恒等**：只在该语言与英语的国名不同（`$en != $loc`）时才做国名替换，i18n 的英文值就是源词本身 ⇒
**英文侧恒等返回原串**。实测 `--diff`：变更 **50 全部是 `de/compare/*`**，新增 0 / 删除 0。

**成效（绝对量）**：德语国家页套餐名单元格 **13,697** 个，本地化前 **11,820（86.3%）** 含英文结构词 → **0**；
全页德语功能词占比 **61.6% → 83.0%**（+21.4 点，50 页汇总）。

**新守卫 `scripts/verify_de_text.py`（已挂 `check:output`；本条写作时的闸门序号见当轮 STATUS）**，`--selftest` 41 项：
（⚠ 订正：本条曾写作 `scripts/verify_plan_names.py` —— **该文件从来不存在**。套餐名校验从第一版起就在 `verify_de_text.py` 的 A/B/C 段与产物级 E1–E3。）

- 源级：A 英文恒等（9,095 条）/ B 国名不跨页 + Mobile 形态未扩张 / C 德语结果不漏译 + 别名表无死条目
- 产物级：E1 德语单元格无英文结构词 / E2 无「英文名 ≠ 德语名」的国名 / E3 英语单元格逐字 ∈ 原始名集合
- **双向验证**：对改造前的旧产物跑 → **17,780 处问题**（其中英语侧 0 误报）；对修完的跑 → **14,197 + 14,197** 个单元格零告警

**本批新立的四条纪律**

1. **查找串要覆盖数据里的「非规范写法」** —— CZ 的规范英文名是 `Czechia`，供应商写的是
   `Czech Republic`；只按规范名替换会**静默漏译**（构建全绿、页面留着英文）。别名必须单独记账，
   并由守卫反过来断言「别名表没有死条目」。
2. **Hugo 的 `replaceRE` 是 Go RE2，没有 lookahead** —— `(?!…)` 不可用。「国名后面不跟 ` Mobile`」
   只能写成**前置 `findRE` 判定整条跳过**，不能写成负向断言。
3. **`index` 链要防 nil** —— `index (index site.Data.x $k) "y"` 在 `$k` 不存在时是 `index nil "y"`，
   **直接报错**（不是返回空），必须 `with` 包一层。
4. **只译结构词与目的地国名，品牌名不译** —— 这不是保守，是「供应商产品名」这个字段的性质；
   与 §12.11 第 2 条同源（`default` 两种写法必须统一），都是「一个字段两种处理路径」的坑。

**已知残留（可接受）**：`Local USA …` → `Lokal Vereinigte Staaten …`（正式国名在德语里带复数冠词，
「Lokal」缺形容词词尾）；`Canada Mobile` / `Macao Mobile` 保持英文（品牌名，按设计）。

### 12.13 D6 第三批已完成（2026-10-09 第六十二轮）—— fup_note / promo_label / quirks 三类英文句子

**机制**：一张表 `data/de/strings.toml`（**125 条** = fup_note 14 + promo_label 10 + quirks 101）+ 一个 partial
`de-text.html`（查表，**未命中恒等返回原串**）+ 12 个渲染位点（`#fup` 表 1、`#providers` 促销句 1、`#quirks` 正文 50×2~3）。

**本批修掉的三个真问题**

| # | 问题 | 修法 |
|:--|:--|:--|
| 1 | `data/de/strings.toml` 多写一层 `[strings]` 表头 ⇒ `$d.strings` = `{strings:{…}}` ⇒ **静默印英文** | 顶层直接放句子键；文件头写警告；`verify_de_text.py` 读法同步 |
| 2 | `compare/single.html:1012-1013` 锚文本是 `printf` 硬编码英文（153 处） | 新增 `compare_single__anchor_*` 3 个 key，整句 i18n + `printf "%s"` 保持转义路径 |
| 3 | `quirks` 101 条从未本地化 | 接进同一张表；生成器按 ISO 分组配对 + 数字集合断言（不手抄英文键） |

**量产翻译的安全做法（本批确立）**：`_gen_de_strings.py` **不手抄英文长句**，而是
「德语按 ISO 分组 → 与 `data/countries.toml` 的 `quirks` 数组**组内同序**配对 → 断言条数一致 →
断言 `set(德语数字) ⊆ set(英文数字)`」。101 条一次跑出**零错配**；数字集合不一致会当场变红。
（因为查表是**精确字节匹配**，键由脚本从数据侧取，所以键永不写错 —— 唯一风险是「德语译到了别的句子」，数字断言就是防这个。）

**下一批（未做）**

1. **`data/networkreports.toml`** —— 需要先定口径：`opensignal_title` 是**报告官方标题**（应保留原文），
   `opensignal_facts` / `ookla_note` 是**归属引用**（该文件头写着「Ookla 页脚禁止商业转载其数据 ⇒ 只做
   『获奖者 + 报告期 + 单个数字』的新闻式引用 + 链接」）。也就是先决定「哪几个字段译、报告标题与数字如何保留」。
2. **`data/carriers.toml` 的 `info.detail`**（146 条运营商介绍）。
3. `/de/research/index.html` 的 31 处英文（量小）。

合起来约 **300+ 条句子**，属纯翻译工程 —— 建议与「德语审校」一起排，**不要用未经审校的译文上线**。

### 12.14 D6 第四批已完成（2026-10-09 第六十三轮）—— 模板层硬编码英文（**非国家页页型**）+ 判据 F

**触发**：本要接着收 D6 的数据层尾账，先做了一次「**全部 55 个德语页**」（不只 50 个国家页）的英文残留普查，
发现 **E1–E5 的盲区是「页型」而不是「写法」**：E 段只走 `/de/compare/<国家>/`，
而德语站现有的另外 5 类页（`/de/`、`/de/compare/` 索引、`/de/guides/`、`/de/networks/`、`/de/research/`）
此前**一条判据都没管**。实测 3 页在漏英文。

**修掉的 4 类真缺口（全部是模板层硬编码）**

| # | 位置 | 症状 | 修法 |
|:--|:--|:--|:--|
| 1 | `partials/aside-destinations.html` | `All {{ len $d.countries }} destinations →` 写死英文 → `/de/networks/` 印出 `All 50 destinations →` | 复用既有 key `partials_header__all_destinations`（en `All {{ .n }} destinations →` / de `Alle {{ .n }} Reiseziele →`）—— **同一句话只允许一份定义** |
| 2 | `compare/list.html` figcaption | `{{ $totalPlans }} real plans across {{ $isoCount }} destinations — one table per country, …` 整句英文 → `/de/compare/` 索引 | 新增 `compare_list__figcaption_plans_destinations` |
| 3 | `compare/list.html` 入门价榜 + FAQ | `$r.cheapPlan` 直接印 `plan.name` → 索引页 **11 处 `500MB / 1 Day`**，且同一条串经 `compare_list__faq_a2` 的 `plan` 占位符又印一次 | 在**聚合处**（`$cheap` 的 append）过一次 `partials/plan-name.html` → 榜单与 FAQ 两处同时干净 |
| 4 | `research/list.html` | **9 句英文**（`prices checked` / `cheapest unlimited, $x/day` / `vs priciest` / `/GB avg` / `N countries · best x at $y/GB` / `Right now … the full league table ranks…` / `N unlimited plans audited…` / `Best daily rate right now is…` / `Daily-rate rankings…`）→ `/de/research/` 曾是全站最差的德语页 | 9 个 `research_list__*` key（`printf "%d …"` 那条改成 `printf (i18n …)`） |

顺手把 `esim-providers/list.html` 的 3 处英文（`N countries · from $x` / `of N countries · best $/GB in` /
`Read the full <brand> review`）也抽了 key —— `/de/esim-providers/` 还没建，属于**先修模板再建页**，
不修的话 D7 一生成就是英文页。⚠ 注意 `g_country` / `g_countries` **不能复用**：它们是 `Country` / `Countries`
（首字母大写，做表头），而这里要小写 `country` / `countries`（英寸 byte 恒等要求），故另立两条小写 key。
⚠ `vs` 不用新建 —— `g_vs` 早已存在（en `vs` / de `vs.`）。

**新增判据 F（`verify_de_text.py`）：全站德语页硬编码英文**

- 扫描面 = `public/de/**/index.html`（**新增页型自动纳入**），判据 = 无硬编码英文痕迹。
- 清单 **23 条短语 + 8 个词**，每条在注释里写明「它是谁漏出来的」，源头修好后**保留当回归网**。
- 词表刻意与 E5 不同：**不收 `Plan`**（`Plan` 是德语词「ein Plan」，收了会造假红）—— 这条差异是刻意的。
- 改造前对**旧产物**跑一遍（自测之外的独立取证）：`EXIT=1`，命中 **23 处 / 3 页**
  （`de/research/` 17、`de/compare/` 索引 5、`de/networks/` 1），而 `May 2026` / `unlimited` / `Plan` **零误报**。
- 改造后：`F 全站德语页无硬编码英文（55 页 × 短语 23 条 + 词 8 条）`，`--selftest` **23 → 30 项**。
  ⚠ 自测断言只能比对「被判定的词」那一段：失败消息带 ±60 字上下文，相邻段落的 `May 2026` 会被卷进来
  → 「不误伤」类断言会假红（本轮踩过一次，已改成 `split("：")[0]` 再断言）。

**同时修掉的日期机制缺陷（本轮开头，独立事件）**

`stamp_checked.py` 的日期单元段边界按「行物理位置」切 → 10 家的 `[<brand>.policy]` 表全堆在文件末尾、
排在最后一个顶层段 `[jetpac]` 之后 → **这 10 张表全被算进 jetpac 的段**：实测给 `[holafly.policy]`
加一行 `fup_kind = "none"`，翻的是 **jetpac** 的档案核对日（`10-07 → 10-09`），holafly 自己反而不翻。
已改为按品牌名归组、段体允许多个不连续区间（`parse_prov_blocks`），并加 `--resync` 迁移模式
（重算全部指纹、**保留每个单元的现值日期**、不动任何 toml）；`--selftest` 写死的「450 价格单元 / 9 档案单元」
随品牌接入腐烂已久 → 改**现算**（41 项全过）。已复原 jetpac 的 `2026-10-07`。

**量化（全部现算）**

| 德语页型 | 本轮前 | 本轮后 |
|:--|--:|--:|
| `/de/compare/` 索引 | 94.9% | **100.0%**（德 276 / 英 0） |
| `/de/research/` | 73.7% | **98.3%**（英 31 → 2） |
| `/de/networks/` | 99.1% | **99.2%**（英 9 → 8） |
| `/de/` · `/de/guides/` | 100% | 100% |
| `/de/compare/*` 50 国 | 98.5% | 98.5%（本轮未动） |

**全站剩余英文只剩三类，且都不是缺口**：① `unlimited` 借词（995 处，统一策略仍未定）；
② Opensignal 引文里的 `May 2026`（6 处，报告官方标识）；③ `Plan`（1 处，德语词本身）。

**恒等判据**：`--diff` = **变更 3，全部是德语页**（`de/compare/index` / `de/networks/index` / `de/research/index`），
**英文侧 0 变更**；基线刷新（702 文件）后复验 `0/0/0`、702 页逐字节相同。
模板层拼装句碎片 **136 → 100**；`i18n` key **1649 → 1671**。

**本轮新增的三条坑（都关于「产物字节」）**

1. **新增一个「独立的注释动作块」会改变产物字节** —— 注释本身不输出，但它前后的**换行与缩进是字面文本**。
   第一次构建 `--diff` 报 **22 处**（含 18 个英文页！）全是纯空白差异。→ 说明一律**并进既有注释块**，
   或把注释放在 `{{- … -}}` 这类两端裁剪的动作里。
2. **模板头部（第一个输出型标签之前）多插一行代码 = 多一个换行** —— `compare/list.html` 的聚合层在
   页头 `<div>` 之前，加一行 `$iso := .` 就让英文索引页变了一个字节。→ 能用作用域里的 `.` 就别新开变量。
3. **注释块里不许出现「成对花括号」** —— `scripts/i18n_extract.py` 的扫描器把注释内的那个写法
   当作**动作边界**，紧跟其后的文字会被误判成「模板层硬编码文案」，`check_i18n.py` 直接报 **ERROR**。
   （与记忆里那条「模板注释里的 i18n 调用会被渲染，示例要去掉花括号」同源，这次是**守卫**侧的表现。）

**★ 本轮最重要的发现：D7/D8 的真正前置不是页面，而是 `i18n/de.toml`**

`scripts/i18n_coverage.py de` 现算：**1671 key，已译 1054 = 63.1%，仍有 617 条英文占位**。
未译量按前缀分布（也就是「哪些页型还不存在」）：

| 前缀 | 未译 | 关联批次 |
|:--|--:|:--|
| `esim_providers_single` | 124 | D7 品牌 Hub |
| `compare_provider` | 112 | **D7 品牌×国家子页（499 页都读它，优先级最高）** |
| `esim_deals_list` | 112 | D7/D8 |
| `tools_list` | 48 | D8 |
| `research_*`（三篇） | 109 | D8 |
| `guides_single` / `guides_region` | 27 / 16 | D8 |
| `compare_single` | 17 | 国家页的剩余短串 |
| `compare_vs_single` / `compare_matchups` | 17 / 15 | D7 vs 页 |
| `g_*` 全站通用 | 10 | —— |
| `esim_providers_list` / `networks_list` | 7 / 2 | D7 |

**结论：先翻 D7 那三组（`compare_provider` 112 + `esim_providers_single` 124 + vs/matchups 32 ≈ 268 条），
再跑 `content/de/` 生成脚本 —— 反过来的话，生成出来的 499 + 45 + 10 张德语页会是「德语 URL + 英文正文」。**

**下一批（按依赖顺序）**

1. **D5 尾部**：翻 `compare_provider` / `compare_vs_single` / `compare_matchups` / `esim_providers_single` /
   `esim_providers_list`（≈268 条），验收 = `i18n_coverage.py de` 对应前缀未译归零 + `check_i18n.py` 全绿。
2. **D7**：`content/de/compare/<a>-vs-<b>.md`(45) + `matchups.md` + `content/de/esim-providers/<brand>.md`(10)
   + 3 个缺失栏目 `_index.md` + **499 个品牌子页**（脚本：只换 `title` + `seo.description` + 删 `noindex`，
   机器字段原样）。⚠ `compare/provider.html` 的**可见套餐名**（第 379 / 558 行）与 **JSON-LD `Offer.name`**
   还是裸 `plan.name`、`.fup` / `.fup_note` / `$country.quirks` 还没接 `de-text.html` ——
   **这些必须在 D7 生成页面前补上**，否则 499 页立刻是英文。
3. D8（手写长文，`privacy`/`terms` 优先）→ D9（解 noindex + sitemap + robots + `x-default`）。


### 12.15 研究栏目收口已完成（2026-10-10 第六十八轮）—— #125 + 3 子页 + 索引正文

**范围**：`layouts/research/{price-index,unlimited-esim,fair-use-audit}.html` 三个模板的英文硬编码
全部抽成「带占位符的整句 + `safeHTML`」（28 处 / +25 −2 key）；`content/de/research/` 补齐 3 张子页 +
索引的 `hero` / `hero_alt` / `faq_heading` / 6 条 `faqs` / 3 段正文。

**英文侧恒等**：d38→d39 与 d40→d41 两次逐字节比对都成立（后者的唯一差异是那 3 张德语页本身）。

★ **本节要记的不是「做完了」，而是「做完之后才暴露的缺陷类」**（§14 红线 79 / 80）：

- 首建德语页时 d40 构建 **exit 1**，`verify_de_text.py` 报 12 处 —— **三类都是一个毛病**：
  模板里裸渲染了「本该走 partial 的东西」（`plan.name` / `fup_note`）或「本该走 i18n 的东西」
  （`delimit` 的末位连接符 `and`、`cond` 的兜底词 `None`）。
- **为什么此前一直绿**：德语侧当时只有 55 页、**没有 research 页**，F 的词表注释里那句
  「修完后实测为 0」是按当时页集写的。**页集一变，旧判据的结论就作废** —— 必须重跑。
- **为什么英文侧看不出来**：`plan-name.html` / `de-text.html` 在英语站都是恒等变换，
  所以这一整类缺陷**只在译文页存在时才存在**。
- 现在德语侧 **627 页**（其中 499 页品牌子页），F/G 的覆盖页集已比立判据时扩大 11 倍。

**顺带修正的两处仪器缺陷**：`_patch_research_de_pages.py` 的四花括号短代码；
`_patch_research_de_keys.py` 的幂等断言（含德语同形词 `Region` 的假阳性）。

**验收**：d41 `npm run build` **EXIT=0**，十项闸门全绿；差异 `变更 3 / 新增 0 / 消失 0`。

### 12.16 批 C（5 篇教程）+ 批 D（12 篇 networks）已完成（2026-10-10 第六十九/七十轮）

#### 批 C 的 d42 构建 **exit 1** —— F 判据只报了 1 处 `and`，真因是一整类

**根因**：`/de/guides/esim-compatibility-check/` 是本轮**新建**的德语页型，其设备总表由
`data/devices.toml` 的**六个散文文本字段**驱动（`source_note` / `brand.name` / `brand.family` /
`brand.since` / `brand.note` / `blocked.brand|model|why`）。此前**没有任何德语页渲染过它们** ⇒

- **F 判据**（黑名单：23 短语 + 8 词，靠人想全、大小写敏感）只报首个命中的 `and`；
- **G 判据**（穷举，但清单 = `english_data_texts()` = 「`strings.toml` 里**已进表**的数据串」）
  —— devices 从未进表 ⇒ **一条不报**。

**两条判据同时为绿，而德语页印着整张英文设备表。** 这是 §12.15（research 那次）的**同构缺陷
第二次出现**，结论要写进纪律：**页集一变，旧判据的绿灯作废**。

**修法（两条）**：

1. `scripts/_patch_devices_de.py` —— **79 条德语条目**（78 条散文 + 1 条 models 特例
   `V29 Lite 5G (Europe only)` → `V29 Lite 5G (nur Europa)`）+ **9 处模板接线**
   （`layouts/guides/single.html` 全在**行内**替换，**411 行 / 25704 bytes 逐字不变**）。
   落点 `data/de/strings.toml`：**176 → 266 行 / 36815 → 43989 bytes**，223 条目；`data-s` 搜索键
   **保持原文**（`$b.name`），只包显示层。
   - ⚠ **为什么不走 `data/de/devices.toml`**：`i18n-data.html` 的 `merge` 语义是
     **map 递归、数组整体替换**，而 `[[brand]]` 是数组 ⇒ 必须重抄 351 条机型名 ⇒
     违反「一份事实一份真源」。**正确路线是 `de-text.html` + `strings.toml`**
     （与 `fup_note` / `promo_label` / `quirks` 同构）。
   - 恒等条目（品牌名 / 机型串）**照建** —— D 判据要求「数据里每个取值都有条目 + 表里无死条目」，
     恒等条目恰是「数据改了措辞」的报警器。断言放宽为「同名键值必须一致」（`Huawei` / `Xiaomi`
     在 `brand.name` 与 `blocked.brand` 各出现一次、值相同，合法）。
2. `scripts/_wire_devices_guard.py` —— **8 处接线**（每条带独立 marker 判已施加），新增
   `load_device_texts()` 并把 devices 并入 `english_data_texts()` ⇒ **G 自动覆盖**；
   `check_strings()` 的 `have` 并入 devices + 统计文案 `+ devices {n}`；
   selftest 补 **双向反例**（缺条目 / 死条目，素材刻意选 **F 看不见**的）。
   `scripts/verify_de_text.py` **54805 → 58878 bytes**。

**新判据的双向证明（两边都要证）**：

- **反证**：拿新判据对 **d42 旧产物**跑一遍 → **40 条 FAIL**（1 F + 39 G），逐条精确指向
  `de/guides/esim-compatibility-check/index.html`（`.buildlog/d43_precheck.txt`）。
- **正证**：`--selftest` 全绿，含新增 3 条（`D devices 素材` / `反例：devices 缺德语条目被抓住` /
  `反例：devices 死条目被抓住`）。
- 构建输出从红转绿的那一行：
  `D 数据串覆盖通过（fup_note 14 + promo_label 10 + info.support/refund 19 + quirks 101 + devices 79 = 223 条）`。

**顺带修掉的仪器缺陷**：`_patch_devices_de.py` 的 `HEAD_NEW` 以 `HEAD_OLD` 为**前缀** ⇒
「复跑时注释块再插一份」（+616 B）。判据改用**独立 `HEAD_MARK`**，并用
`.buildlog/fix_devices_head_dup.py` 把两份压回一份（`44605 → 43989 bytes`）。

**批 C 验收**：d43 `npm run build` **EXIT=0**，十项闸门全绿；d42→d43 逐字节差异
**`变更 1 / 新增 0 / 消失 0`**，唯一变更就是那张德语 guides 页
（`ffe535785c39 → 5260f1afa626`）⇒ **英语侧零变更**，`de-text.html` 的恒等性再次得证。

#### 批 D —— 12 篇 networks 德语正文（合计 179,716 bytes）

canada / china / france / germany / japan / mexico / netherlands / south-korea / spain / thailand /
united-kingdom / united-states。全部 `CRLF=0`，断言覆盖：front matter 字段集与顺序（德语侧只允许多出
`noindex`）、h2/h3 条数与层级一一对应、德语 h2/h3 禁 `,;:`、站内链 `/de/` 前缀、禁 `Mbps`、
`{{< count-providers >}}` 保留。

- 术语一致性扫描抓到 **3 组不统一**（`Download Speed` 3 种写法 / `Coverage Experience` 3 种 /
  `Best Network` 2 种）⇒ `scripts/_patch_networks_de_terms.py` 统一 **12 处**。
  **权威词表**（本文件与脚本 docstring 同源）：
  `Download Speed → Download-Geschwindigkeit` · `Download Speed Experience → Download-Geschwindigkeitserfahrung` ·
  `5G Download Speed → 5G-Download-Geschwindigkeit` · `Coverage Experience → Abdeckungserfahrung` ·
  `5G Coverage Experience → 5G-Abdeckungserfahrung` · `Reliability Experience → Zuverlässigkeitserfahrung` ·
  `Voice App Experience → Sprach-App-Erfahrung` · `Video Experience → Video-Erfahrung`（统一
  `Erlebnis` → `Erfahrung`）· `Time on Network → Zeit im Netz` · `Best Network → Bestes Netz` ·
  `5G Availability → 5G-Verfügbarkeit`。**保留英文**：`Speed Score` / `RootScore` /
  `Speedtest Global Index` / `Mobile Network Experience Report`（报告官方标识，见 §12.14）。
  **规则**：外来词合成加连字符（`Download-Geschwindigkeitserfahrung`），纯德语合成词不加（`Abdeckungserfahrung`）。
  > ⚠ **本词表在第七十二轮改过一次方向**：初版定的是 `Download-Tempo`（批 D 当时的写法），
  > 但批 E 收尾时实测发现 `Tempo` 是**批 D 的局部方言**（76 处，全部在 `content/de/networks/*.md`），
  > 而全站标准是 `Geschwindigkeit`（**215 处**：i18n 28 / data/de 119 / 其余正文）。
  > 且记分板表格（数据层）与正文**渲染在同一页** ⇒ 同页两词打架。
  > 已由 `scripts/_patch_networks_tempo.py` 归并 75 处正文 + 80 处生成源字面量，详见 §12.17。
- `Sie` / `Ihre` **逐条核上下文：全部是第三人称代词**（`die Tabelle … Sie zählt`），**0 处敬称误用**。
  人称惯例实测：**除 research 栏目用 `Sie`，全站（guides / networks / compare / tools）一律 `du`**。



### §12.17 批 E —— 51 页 compare 德语正文（50 国家 + 1 hub）

**范围澄清（先侦察后动手）**：`content/{en,de}/compare/` 顶层各 97 个 `.md`，批 E 只覆盖 **51 页**：
50 个国家页 + `_index.md`（hub）。另外 46 个是**模板驱动** —— `matchups.md` + 45 个 `*-vs-*.md`
（`layout: matchups|vs-single`），正文来自 `data/`；再外加 50 个国家子目录 × 10 品牌 = 500 个
`layout: provider` 页。这三类**不写正文**，只需 D9 统一删 `noindex`。

**零写死的数据源**：`scripts/_compare_de_facts.py` 从 `data/plans/*.toml` + `data/countries.toml` +
`data/carriers.toml` 现算 50 国事实表 → `.buildlog/compare_de_facts.json`。数字口径全部复现英语正文：
`total_plans` / `unlimited_plans` / `provider_count` / `cheapest_entry`（价格升序，同价取 gb 小者）/
`best_rate = price/gb`（仅计量档）/ `breakeven_gb_day` / `entry_at_rate_mb = price / best_rate × 1024`。
**复现证据**：AR `@$1.30/GB → 402MB`、AU `@$0.66/GB → 792MB` 与英语站逐字一致。

**★ 本轮最重要的发现：同一页两处数字自相矛盾**

| 位置 | 计划数口径 | 判定 |
|---|---|---|
| 英语 `seo.description` | 实时现算 | **50/50 正确** |
| 英语**正文** | 8 品牌时期快照 | **43/50 过期** |
| 英语正文 best rate | 同 | **16/50 过期** |
| 英语正文 unlimited 数 | 同 | **48/50 过期** |
| 德语 `seo.description` | 修前 = 旧口径 | 本轮**已刷成现算** |
| 德语正文 | 本轮现算 | — |

⇒ 德语侧当场修正（校验：德语 vs 英语 description 的**数字序列** 51 页 **0 不一致**）。
**英语正文不改**（超出批 E 范围，且英语已上线）—— 登记为**独立缺陷**，见 §14。
`fiji` 特例：只有 9 个品牌有 FJ 方案 ⇒ `provider_count = 9`（其余 49 国 = 10），德语 `9 Anbietern` 正确。

**hub 外壳本就已本地化**：`/de/compare/` 渲染 `50 Länder` / `10 Anbieter` / `9095 Tarife erfasst` /
`Alle·Asien·Europa·Amerika·Afrika Nahost·Ozeanien` / 卡片 `10 Anbieter · 254 Tarife · ab $0.51` / 5 条 FAQ 全德语。
⇒ 该页 TODO 注释里「卡片标签/排序控件仍走英文占位 key」**已过时**，本轮只写 6 个 h2 正文。

**反同质化取证（`scripts/_audit_de_batch_e.py` 现算）**：段级唯一 **170/170 = 100%**、
句级唯一 **729/729 = 100%（0 重复句）**；德/英正文可见字符 **69,191 / 62,215 = 1.112**
（逐页区间见 `--json`）。

**术语一致性（现算）**：`Mbit/s` 49 / `Mbps` **0** / `Kbps` **0**；品牌名小写变体 **0**；
`unbegrenzt` 家族 149 / `unlimited` **0**；价格 **251 处点号 / 0 处逗号**；
数据量 **186 处带空格 / 0 处无空格**；小数一律逗号。

**新增假红与修法**：`F` 禁词表含 `countries`，撞上短代码**源码文本** `{{< count-countries >}}`
（产物层安全 —— 那时已渲染成数字）⇒ `_compare_de_lib.py` 加 `_strip_shortcodes()`，
F 三张表统一**先挖短代码**再判。

**规模**：51 页 = **88,018 bytes**（英语侧 73,427），全 `CRLF=0`；段数/h2 数/短代码集合与英语**逐页对齐**；
`noindex: true` 保留；`TODO(de)` 统一为分层发布措辞。5 分册 + hub 全部幂等（复跑「应用 0 / 跳过 51」）。

### §12.18 d44 构建 exit 1 —— `awards` 数组从未本地化（F 只报 12 条，真实 77 个字段）

**现象**：d44（批 D + 批 E 首次合体）`EXIT=1`，F 判据 12 条，**全部在 `/de/networks/*`**，
而 `content/de/networks/*.md` 正文里根本没有这些串。

**根因**：`data/networkreports.toml` 的 `[[XX.awards]]`（记分板表格，`layouts/networks/single.html:244`）
在 `data/de/networkreports.toml` 里**一组都没覆盖**（英语 **35 组** / 德语 **0 组**）。
Hugo 的 data 深合并是「map 递归、**数组整体替换**」⇒ 整表静默回退英文，构建不报错。

**为什么此前全绿**：
- `awards` **只在 networks 页渲染**，而这 11 个国家的德语 networks 页是**批 D 才建出来的**
  （`check_output` 页数 1279 → 1291）。在此之前没有任何德语页承载这些串 ⇒ F（黑名单）绿；
- G 只认「已进 `strings.toml` 的数据串」，`awards` 从未进表 ⇒ G 天然失明。
**页集一变，绿灯作废** —— §14「F 与 G 会同时失效」的第一次实证。

**★ 黑名单永远是下限**：F 只抓到含 `and`/`every` 的 **12** 条（11×`and` + 1×`every`），
真实是 **35 组 × 3 字段中 77 个非空字段全英文** —— **低估 6.4 倍**。

**修法（三段）**：
1. `scripts/_patch_awards_de.py` —— 11 国 35 组德语写入 `data/de/networkreports.toml`
   （21,762 → 30,279 bytes，CRLF 341 → 532）。`carrier` 是专有名词、逐字继承（模板按它建
   carrier→award 映射）；数字用德语逗号小数；单位一律 `Mbit/s`；括注**取自本文件既有的**
   `opensignal_facts` 德译（`Abdeckungserfahrung (Coverage Experience)` /
   `Gleichbleibende Qualität (Consistent Quality)` / `Zuverlässigkeit (Reliability)` /
   `Zeit im Netz (Time on Network)` / `Download-Geschwindigkeitserfahrung (Download Speed Experience)`），
   **不发明新译法**。
2. `scripts/verify_de_data.py::check_reports()` 补 `awards` 判据：整国缺失 / 组数不符 /
   `carrier` 被改动 / 字段未译 / 数字不符 / 德语侧死条目。自测 **31 → 34 项**。
3. 新增产物级 `check_award_products()` —— **双向**断言（英语串不在 **且** 德语串在）。
   只证「英文不在」会被「整张记分板走 `{{ if $awards }}` 的 else 分支」骗过去（假绿）。

**取证**：
- 新守卫跑**改造前**产物 → **154 处问题 = 77 字段 × 2**（英文在 + 德语缺），核对 11 国 —— 守卫有效性反证。
- d45 构建 `EXIT=0` 十项全绿：`F 全站德语页无硬编码英文（644 页）` ✔、
  `G 全站德语页无数据层英文残留（644 页 × 185 条数据串）` ✔、
  `I 德语单位统一（i18n 1730 值 + data/de 1416 → 1556 字符串，无 Mbps/Kbps/Gbps）` ✔、
  `产物级：记分板 77 个字段（11 国）已双向核对` ✔。

### §12.19 术语归一 —— `Tempo` 方言并回 `Geschwindigkeit`

**同页两词打架**：`/de/networks/{land}/` 的正文（`:213` `{{ .Content }}`）与记分板（`:244`）
**渲染在同一页**，正文用 `Download-Tempo`、记分板（数据层）用 `Download-Geschwindigkeit`。

**实测分布**：`Geschwindigkeit` 家族 **215**（i18n 28 / data/de 119 / 其余正文）vs
`Tempo` 家族 **76**（**全部**在 `content/de/networks/*.md`）⇒ `Tempo` 是批 D 的**局部方言**，向西对齐。

`scripts/_patch_networks_tempo.py`：**75 处正文 + 80 处生成源字面量**一起归并。

- ⚠ `Tempo` 是中性、`Geschwindigkeit` 是阴性 ⇒ 需要 14 条**变格表**逐条手写
  （`beim Tempo`→`bei der Geschwindigkeit`、`mit einem Download-Tempo`→`mit einer …`、
  `Dein eigenes Tempo`→`Deine eigene …`、`bei rohem Tempo`→`bei roher …`、`für reines Tempo`→`für reine …`、
  `über das Tempo, das du`→`über die Geschwindigkeit, die du` …）。
- ⚠ 变格自查必须带**右边界**：`ein Geschwindigkeitstest` 是合法复合词，裸子串匹配会假红（首跑确实踩了）。
- **生成源必须一起改**：`_patch_networks_de_{1,a,b,c,batch}.py` 按「内容与字面量比对」决定是否写盘，
  留着旧方言 = 重跑就把方言写回去；`_patch_networks_de_terms.py` 更直接 —— 它以
  「old 命中 0 且 new 已存在」判幂等，术语一改就 **FAIL**。
- **复核**：6 个脚本 `--dry` 全部 `断言全过` / `已应用 0 / 已存在跳过 12`
  ⇒ 字面量与落盘内容**逐字一致**，单源恢复。

**未改（有据）**：`Durchsatz`（22 处）保留。英语原文是 `Throughput`（与 `Speed` **不同的词**），
`Durchsatz` 是忠实翻译；同一页的 `Upload Speed` **奖项名**则译 `Upload-Geschwindigkeit`。两者都对。


### §12.20 d47 验收 + D9 解禁（德语正式发布那一轮）

#### ① 批 E 的最终验收（d47，`EXIT=0` 十项全绿）

`content/de/compare/*.md` 51 页（50 国家 + hub）落盘后重建，`npm run build` 十项闸门全绿。
德语判据：`F 全站德语页无硬编码英文（644 页）` · `J 裸印英文区域名（644 页）` ·
`G 数据层英文残留（644 页 × 185 条，含 JSON-LD）` · `I 单位统一（i18n 1730 值 + data/de 1556 字符串）` ·
新增 `产物级：记分板 77 个字段（11 国）已双向核对`（§12.18 的 awards 缺陷闭合取证）。

**产物归属（`pub_manifest --diff pub_d43`）＝ 变更 650 / 新增 12 / 消失 0**，逐类归因：

| 类别 | 页数 | 原因 |
|---|---|---|
| `de/compare/<国>/<品牌>` | 499 | **导航栏条件渲染**：`partials/header.html:31` `{{ with site.GetPage (printf "/networks/%s" $c.slug) }}` —— 批 D 建出 → `/de/networks/` 后，德语站每页导航多出「Netzkarte」入口 |
| `de/compare/<slug>` | 96 | 50 国家页（批 E 正文 + `seo.description`）+ 45 个 vs 页（导航）+ hub（批 E） |
| `de/networks` | 12 **新增** | 批 D 德语 networks 首次进入产物 |
| `networks`（**英语**） | 12 | 德语对应页出现 ⇒ 语言切换器从 `/de/`（首页 fallback）改为 `/de/networks/<slug>/`，并新增 `og:locale:alternate = de_DE` |
| 其余德语页 | 26 | 导航 + `llms.txt` / `sitemap.xml` |
| **英语其他页** | **0** | ✔ 逐字节恒等 |

★ 结论：**「不该变的页」= 0**。英语侧唯一的 12 页变更**有明确且正确的理由**（语言切换器指向真实译文页）。

#### ② D9 —— 德语分层发布解禁

| 动作 | 前 → 后 |
|---|---|
| `noindex: true` | `content/de/**` **643 → 0**（A 成对 79 页 + B 单行 564 页） |
| `/de/sitemap.xml` | **1 条 → 644 条**（机制：`partials/sitemap-urls.html` 以 `.Params.noindex` 过滤，删净即自动补全，**无需另写 URL 清单**） |
| `layouts/robots.txt` | 新增 `Sitemap: https://www.esimsift.com/de/sitemap.xml` |
| `layouts/partials/head.html` | 新增 **x-default**：指向默认语言（en）版本；en 页指向自身；**无译文组的页不发**（避免孤立 x-default） |
| 全站 hreflang | **647 tags / 645 页 → 3864 tags / 1288 页**（= 1288 × 3：self + 译文 + x-default，数学自洽） |
| `docs/regression-manifest.json` | 重刷（1291 文件）；`--diff` 复核 **逐字节相同** |

**643 页有两种 noindex 形态**（脚本按形态分别处理，`scripts/_d9_unlock_de.py`）：
- **A 成对（79 页）**：`noindex: true` + 紧跟 `# TODO(de)：分层发布 …（D9 那一轮）时删掉上面这行。` ⇒ 两行一起删；
- **B 单行（564 页）**：模板驱动页（45 vs + 499 品牌子页 + 顶层静态页）当初就没有 TODO ⇒ 只删一行。
⚠ 脚本对两者都做**成对性 / 相邻性 / 换行守恒**断言，不匹配即拒写。

**★ 解禁后的产物级验证（D9 生效证据）**：
- 德语产物里 `noindex` = **0 处**；
- `hreflang="x-default"` = **1288 页**；
- 德语页 hreflang 组：`de-de`(self) + `en-us`(英语版) + `x-default`(→英语版)；
  英语页：`en-us`(self) + `de-de`(德语版) + `x-default`(→自身) —— 两组互为回指，`check_hreflang.py` 判据 A–D 全过。
- 产物归属（`pub_d47 → d48`）＝ **变更 1290 / 新增 0 / 消失 0**，且
  `1290 = 644 德语 HTML + 644 英语 HTML + de/sitemap.xml + robots.txt`
  —— 变更集合**恰好等于「全部 hreflang 页 + 两个声明文件」**，**无任何意外变更**。

**已知副作用（无害，如实登记）**：`check_i18n.py` 的「拼装句碎片」**48 → 49** ——
新增的 1 处是 `layouts/robots.txt` 里新加的 `Sitemap: {{ .Site.BaseURL }}de/sitemap.xml`
（已用 `i18n_extract.collect()` 直接定位：该文件的 frags 2 → 3）。
robots 的 `Sitemap:` 是**机器指令**不是用户可见文案，脚本仍 `EXIT=0`、`OK: 模板层无新增硬编码`。
无法在不引入更差判据（`printf` 格式串 0 → 1）的前提下消除。

#### ③ 德语完成度终检（现算）

| 维度 | 数值 |
|---|---|
| `content/{en,de}` md 一一对应 | **644 = 644，缺口 0** |
| i18n key | en = de = **1730**，已译 **1706**，完全相同 24（**全部**是公式 / 专有名词 / 德英同形词） |
| 「未译」24 条性质 | `${{ .price }} · {{ .size }}`、`{{ .n }} GB`、`GB`/`MB`/`$/GB`、`FAQ`、`Ookla Speedtest Global Index`、`App Store ↗`、`Google Play ↗`、`eSIM`、`Multi-IMSI`、`Link`、`Region`、`transparent` ⇒ **无实质漏译** |
| 可索引德语页 | **644 / 644**（解禁后无 noindex） |
| 产地判据 | F / G / H / I / J + E1–E5 全绿；`check_output` 1291 pages / 7412 JSON-LD blocks |

**⚠ 唯一未闭合的能力缺口（不因本轮改变）**：德语译文**尚未经有资质的人工审校**。
机器判据只能证明「没有英文残留、单位统一、术语自洽、结构对齐」，**不能替代母语审校**。

### §12.21 第七十四轮 —— 英语 compare 正文现算口径 + 德语上线前技术收尾（d49/d50）

> 交付文档：`esimsift-德语上线前技术收尾-2026-10-10.md`（§0–§6，含全部现算数字）。

#### ① 英语 compare 正文按现算口径重写（红线 84 已修）

49/50 页正文重写，**`japan` 逐字节未变**（编辑性长文，无 `N plans` / `$/GB` 句）。真实变更
**98 行 / 305 token** = 品牌名归一 147 + 数字与计量 152 + 其它 6。`--verify` 0 处过期、`--dry` 幂等 0 处、
`content/en/compare` 52/52 仍纯 CRLF。★ 纪律：**只换槽位，绝不重写句式**（50 套独立手写句式是反同质化资产）。

#### ② `/de/llms.txt` 德语化

`layouts/index.llms.txt` 的静态英文全部抽成 i18n：**44 个 `llms__*` key** + 19 条字面替换，
英语字节由**结构等价证明**保证（`flatten()` 逐占位符用原表达式回填）。碎片 **49 → 14**（该文件 35 处全消）。
i18n **1730 → 1777**。

#### ③ 结构化数据抽查（4 个真缺陷已修）

| # | 缺陷 | 范围 |
|---|---|---|
| D1 | `publishingPrinciples` 指向英语 `/methodology/` | 645 页 → `/de/methodology/` |
| D2 | JSON-LD `BreadcrumbList` 硬编码 `Home` | 645 页 → `(i18n "g_home")` |
| D3 | 同上，硬编码 `Compare countries` | 499 页 → `(i18n "g_compare_countries")` |
| D4 | `esim-providers/single.html` 4 条 `additionalProperty.name` 硬编码英文 | 10 页 |

判据 `scripts/_de_schema_audit.py`：[1] JSON 合法性 / [4] URL 语言前缀（**资源类 URL 豁免**）/
[5] 同页重复 `@type` / [6] de-en 同路径 `@type` 集合差异 / [7] 同 `@type` 键集合差异 —— 全绿。
4 个假红源已写进 docstring（**红线 87**）。

#### ④ 首屏性能抽查（1 个真缺陷已修）

H1：首页 hero `/img/site/home-hero.webp`（373 KB）被**全站无条件 preload**，而该图只有
`layouts/index.html:57` 一处渲染 ⇒ **1288 页白预加载**。改为 `{{- if .IsHome }}…{{- end }}`，
并用**最小 Hugo 探针站**证明「首页逐字节相同 + 子页恰好少那一行」。
判据 `scripts/_perf_audit.py`：[H2] `preconnect` 须被实际请求（`fonts.gstatic.com` 为伴生 origin，成对放行）；
[H3] 单块内联 `script` ≤ 100 KB；[H4] 有 `<head>` 且闭合。
**P1/P2/P3 三项登记待决策**（`/tools/` 1.16 MB 内联脚本 / **1290 页无 `<head>`** / CSS `@import` 串行阻塞）。

#### ⑤ ★ 非 HTML 德语产物 —— 判据 G 的扫描面本身漏了一整类产物（**红线 88**）

`verify_de_text.py` 的 F/G/J 都只枚举 `d.glob("**/index.html")`，而德语站对外可读的**非 HTML 产物**
（`/de/llms.txt`、`/de/catalog.json`、RSS `*.xml`、`/de/sitemap.xml`）**一条都扫不到**。实测抓到 3 个缺陷：

| # | 缺陷 | 证据 |
|---|---|---|
| D5 | `/de/llms.txt` **10 条 `promo_label` 是英文**（★ 本轮引入）：`promo_label` 在 `data/de/strings.toml`（走 `de-text`），不在 `data/de/providers.toml` | 站内 5 处渲染全包了 `de-text`，只有新写的 llms 模板漏了 |
| D6 | `promo_expires` 为空时印 `, expires )` / `, gültig bis )`（**9/10 品牌**） | 站点既有惯例是 `esim-providers/single.html:466` 的 `with/else` |
| D7 | `/de/catalog.json` 的 `fairUse` 漏 de-text（**2271 条** `fup_note` 英文）+ `notes` 是**两语都硬编码**的模板字面量 | 该模板本身是语言感知的（`$c.name` 出来是 `Vereinigte Staaten`） |

**守卫改造**：① 先换实现 —— 逐串带回溯正则（185 条 × 3 MB）**33 s** → 手写 `str.find` + 手动查左边界 **0.3 s**；
644 个德语 HTML 页 **256 s → 8.3 s**，且**换实现前后逐页比对命中集合完全一致**；
② 扫描面扩到 `DE_TEXT_SUFFIXES = (".txt", ".json", ".xml")`，新增 `_json_text()` 还原 Hugo `jsonify` 的 `\uXXXX`；
③ **先对新守卫跑改造前的旧产物**：`24 处问题 / EXIT=1`（10 + 14）；④ 补 7 条 selftest 正/反例。
**构建提速**：全量 **15m26s → 9m02s**。

#### ⑥ 验收（d50，`EXIT=0` 十项全绿）

`I 德语单位统一（i18n **1779** 值 + data/de 1556 字符串）` · `F（644 页）` · `J（644 页）` ·
**`G 全站德语产物无数据层英文残留（644 页 + 11 个非 HTML 文件 × 185 条数据串，含 JSON-LD）`** ·
`check_hreflang 3864 tags / 1288 页` · `check_output 1291 pages / 7412 JSON-LD blocks`。

**逐字节归属**：`--diff` 与 d49 **逐类计数完全相同**（变更 1289 / 新增 0 / 删除 0 / 非品牌子页 291）
⇒ d50 未引入额外 HTML 变更（补强：新 2 个 key 只被两个非 HTML 模板引用）。

| 产物 | 结果 |
|---|---|
| `public/catalog.json`（英语） | ✅ **逐字节不变** |
| `public/de/catalog.json` | ✅ 只变 `notes` + 2271 条 `fairUse`，结构与其余键逐项相等 |
| `public/llms.txt`（英语） | ✅ 只变 9 行，全是删掉 `, expires )` |
| `public/de/llms.txt` | ✅ 促销句 10 条全德语，英文数据串残留 0 |

#### ⑦ 顺带修好的既有缺陷（诚实登记）

45 个**英语** `compare/*-vs-*` 页改变字节：d49 把 JSON-LD 面包屑第 2 级换成 `(i18n "g_compare_countries")`
（英语值就是 `Compare countries`，本意零变化），却暴露出**可见面包屑第 2 级原本用的是国家页 title 口径**
（`All eSIM providers`）⇒ 原有的 JSON-LD/可见层口径矛盾被顺带修好。**是修复，不是回归。**

#### ⑧ 同轮发现的失效守卫

`scripts/_llms_de_l10n.py`（**不在 build 流水线里**）的 `--selftest` 早就红着：迁移落盘后 `old == new`，
而 `audit(old, new, env)` 两侧**共用同一个 `env`** ⇒「改英文值会判红」这条反例**结构上失效**。
修法：反例**自带基线**（`flatten(new, ENV)`）；`--dry` 遇「片段计数全为 0」判为迁移已完成。
★ **不在流水线里的守卫必须定期手跑 `--selftest`。**
