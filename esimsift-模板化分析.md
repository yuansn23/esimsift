# eSIM 对比页模板化 / Google SEO 合规分析

> 分析对象：
> - https://www.esimsift.com/compare/austria/alosim/
> - https://www.esimsift.com/compare/austria/airalo/
>
> 方法来源：`claude-seo` 的 `seo-content`（内容质量 / E-E-A-T）+ 机械 diff 对比
>
> 分析日期：2026-10-07

---

## 一、分析方法（可复用到任意页面）

本方法分三层，先用脚本做**确定性机械对比**，再套用 `seo-content` 技能做**启发式评分**，最后对照 Google 官方政策定**风险结论**。

### Step 1：抓取线上渲染后的 HTML

用带浏览器 User-Agent 的请求抓完整静态 HTML（本站为 Hugo 静态站，curl 可拿全文）：

```bash
UA="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0 Safari/537.36"
curl -s -L -A "$UA" "<URL>" -o page.html
```

> 注意：部分站有 Cloudflare 墙，直接 curl 不带 UA 会拿到 403 拦截页而非正文；先看返回的 title 是否为 `Attention Required! | Cloudflare` 再决定是否换 UA。

### Step 2：抽取正文结构（标题树 + 正文文本 + JSON-LD）

用 Python 的 `HTMLParser` 抽取，**排除** `nav / footer / script / style / svg`，只保留主内容：

- `<title>`、`<meta name="description">`
- H1 / H2 / H3 完整层级树
- 正文逐行文本（p / li / td / blockquote 等）
- 所有 `application/ld+json` 块的 `@type` 及数量
- `<link rel="canonical">`、`<html lang>`、`og:title`

```python
from html.parser import HTMLParser
# 关键：handle_data 时跳过 script/style/nav/footer，并分别捕获标题层级与正文文本
```

### Step 3：逐句 diff —— 量化模板化程度

把两个页面的正文文本做**两级归一化**后求集合差集：

1. **品牌名归一化**：`aloSIM` → `@`，`Airalo` → `@`
2. **数字归一化**：`\d+(\.\d+)?` → `#`

然后计算：

| 指标 | 含义 |
|---|---|
| `shared (品牌归一化)` | 逐字相同的句子数 → 锅炉话术占比 |
| `shared (品牌+数字归一化)` | 连数字都去掉后仍相同的句子 → 纯模板骨架 |
| `only_a / only_b` | 真正差异化 prose 的行数 → 原创占比 |

判断标准：
- **结构 100% 相同**（H2/H3 骨架逐条一致）+ **品牌归一化后 > 60% 句子逐字相同** → 高度模板化
- 再看 `only_*` 里是「换了措辞的真差异化」（如 fair-use 表述不同）还是「只换了数字」（伪差异化）

### Step 4：套用 seo-content 的 E-E-A-T 评分

按技能权重（Trust 30 > Expertise/Authoritativeness 各 25 > Experience 20，合计 100）打分，并对照 Google "Who / How / Why" 三问：

| 问 | 查什么 |
|---|---|
| **Who** 谁写的 | 是否有作者署名、bio、资质 |
| **How** 怎么做的 | 是否披露流程、是否有原始数据/一手证据 |
| **Why** 为什么存在 | 是"帮人"还是"骗点击"、是否有凑字数/刷新鲜度痕迹 |

### Step 5：对照 Google 官方政策定风险

最后把机械结论映射到 Google 政策原文：
- **规模化内容滥用（scaled content abuse）**：判定原文是 *"producing many pages … that are **substantially the same regardless of minor variations**"*
- 辅助检查：`FAQPage` 富结果已废弃（2023）、无作者署名、正文有效词数

---

## 二、本案例分析结果

### 1. 结论：高度模板化（典型 programmatic SEO）

两个 URL 是**同一个模板**，只替换品牌名（aloSIM ↔ Airalo）和数据库数字（12↔24 套餐、价格、排名）。

### 2. 量化证据

| 指标 | 结果 |
|---|---|
| H2/H3 骨架 | **10 个 H2 + 子标题完全相同**，仅品牌名和数字不同 |
| 品牌名归一化后共享句 | 162 / 234 行 = **69% 逐字重复** |
| 品牌+数字归一化后 | 仍共享 146 行，**真正 unique prose 仅 27 行（aloSIM）/ 19 行（Airalo）** |

**逐字相同的模板指纹句子（非数据，最该差异化却重复）：**
- FAQ 答案：`"Both work in Austria, and the answer depends on how much data you will actually use rather than on either brand."`
- 运营商描述（A1/Drei/Magenta 三段在两个品牌页完全一致）：
  - `"Austria's benchmark — the best alpine and rural coverage plus fast city 5G."`
  - `"The cheapest plans and improving fast; patchier in the high mountains."`
  - `"Strong in cities and valleys; a close second nationally."`
- 竞品对比卡片库（8 张整段复用）：
  - `"LotusFlare's travel eSIM with per-country local plans"`
  - `"Global 4G/5G eSIM from Transatel, an NTT company"`
  - `"App-first travel eSIM with 24/7 activation"` 等
- Section 骨架标签：
  - `"Beyond the price tag"` `"Fine print decoded"` `"The masts behind the plan"`
  - `"Who it fits"` `"Honest trade-offs"` `"The other side by side"`

**真正做了差异化的部分（占比过低，但值得保留）：**
- Fair-use 措辞：aloSIM `"slow to roughly 512 Kbps … hard-capped"` vs Airalo `"pass 2 GB in a day … 128 Mbps … resetting 24 hours"` ✅
- Tethering 措辞：`"shares the same data pool"` vs `"no cap on connected devices"` ✅
- Strengths / Watch out for 列表、Buy it if / Look elsewhere if、套餐名（Airalo 为 `Servus Austria - 2GB`）、promo code（`ESIMTWEAKS` vs `NEWTOAIRALO`）✅

### 3. Google SEO 合规评估

**技术层：合格甚至优秀 ✅**
- Title / H1 / Meta description / canonical 每页唯一、关键词合理
- JSON-LD 完整：`Product + Brand + AggregateOffer + Offer×12/24 + FAQPage + BreadcrumbList + Organization + WebSite + WebPage`
- `lang="en"`、OG 标签、自引用 canonical 正确，HTTPS，日期戳 `Sep 30, 2026`

**内容层：风险点 ⚠️**

| 维度 | 得分 | 说明 |
|---|---|---|
| Trustworthiness | ~20/30 | 有方法论链接、日期、免责声明、Organization schema，正文无物理地址/评价 |
| Expertise | ~10/25 | 数据准确、技术深度够，**无作者署名** |
| Experience | ~7/20 | 无原创编辑洞见，数据库驱动，Strengths 略有编辑判断 |
| Authoritativeness | ~8/25 | 新品牌，无外链/权威引用佐证 |
| **合计** | **~45/100** | 规模化站点 "at risk" 区间 |

**最大合规风险 —— 规模化内容滥用（scaled content abuse）：**
当 `167 套餐 × 9 运营商 × N 国家 = 上千页` 都共享约 70% 锅炉 prose + 100% 相同骨架时，正好命中 Google 政策原文 *"substantially the same regardless of minor variations"*。数据本身真实、有用、诚实（非 doorway 垃圾页），但重复 prose 比例和雷同骨架把它拖进风险区。

**次要问题：**
- `FAQPage` schema 已不再产生 Google 富结果，且 4–5 个 FAQ 问+答几乎全是固定模板
- 无作者/编辑署名，`Who` 偏弱
- 主内容词数 2182 / 2211，去掉表格后原创 prose 不足 500 词

### 4. 建议（按优先级）

1. **删或变量化骨架标签** —— `"Beyond the price tag"` 这类段间小标题是模板指纹。
2. **重写 3 个"该差异化却重复"的段落** —— 判定段、FAQ 5 问答、运营商段落，每页给**独有论点**，而非品牌名+数字替换。
3. **FAQ 换成真实用户问题**（从 PAA / 搜索词挖），不要固定模板问。
4. **加作者署名 + "数据方法论 / 编辑团队"页**，补上 `Who/How`（非 YMYL 价格对比站性价比最高的 E-E-A-T 提升）。
5. 保留现有差异化优点（fair-use / tethering / strengths 已做到不同），把差异化 prose 占比从 ~15% 提到 50%+。

---

## 三、局限与声明

- 抓取的是线上渲染后静态 HTML；「模板化」是**确定性机械结论**，可信度高。
- 「Google 合规」是 `seo-content` 技能自己的**启发式评分模型，非 Google 内部信号**（该技能自身也声明这一点）。真正定生死的是 Search Console 表现，而非第三方打分。
- E-E-A-T 权重（30/25/25/20）为该技能内部模型，Google 官方从未公布数字权重，只声明「Trust 最重要」。
