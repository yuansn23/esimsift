# eSIM Sift 对比页「去同质化」批量改写提示词（AI 可执行版）

> **用途**：交给 AI / agent 对 esimsift.com 的 `/compare/{country}/{brand}/` 页面做批量去同质化改写。
> **适用范围**：不限国家数（50 国 × 多品牌），当前样例品牌为 Roamic，同一套规则可平移到所有品牌页。
> **给 AI 的一句话目标**：把「数据模板」和「叙事文案」解耦——数据照旧注入，叙事文案每个国家重写并差异化搜索意图；不要只换地名。

---

## 0. 你（AI）要做的事，一句话

对每个国家的 `/compare/{country}/{brand}/` 页面：
1. **保留**所有真实数据、结构化数据、内链、canonical、数据表格——这些是对的，一个字都别改。
2. **重写**所有「叙事性」文案（结论、人设、取舍、行程天数结论、intro、部分 H2 标题、部分 FAQ），让每个国家页的叙事文案独特、且服务于该国的搜索意图。
3. **通过质检**：改写后，非表格叙事文案的独特占比 ≥ 40%（现在是 8%）。

---

## 1. 问题诊断（你为什么被叫来做这个）

当前页面存在严重的模板化/同质化，量化证据：

| 指标 | Singapore | Japan | 问题 |
|---|---|---|---|
| 正文块「模板共用」占比（抹掉国家/价格/网络/品牌后相同） | 92% | 92% | 🔴 严重 |
| 真正国家特有块 | 8% | 8% | 增量太低 |
| 正文词数 | 16,255 | 16,333 | 几乎一致 |
| 内链 / 图片数 | 175 / 88 | 175 / 88 | 完全一致 |

- **Title**：`{Brand} {Country} eSIM Review 2026: Data Plans Compared`（仅换国名）
- **H1**：`{Brand} {Country} eSIM Plans & Prices (2026)`（仅换国名）
- **H2/H3 骨架**：10 个 H2、14 个 H3 逐字相同，只把国家名替换。

**风险**：Google 2024/03 spam policy 的「scaled content abuse」和「doorway pages」。50 国铺开后，骨架+文案完全相同 = 极易被判「同一页面换地名」。

**已合格、不要动的部分**（AI 不得改动）：
- JSON-LD：`Product + AggregateOffer`（lowPrice/highPrice/offerCount/priceCurrency + N 个 Offer）、`FAQPage`、`BreadcrumbList`、`Organization`、`WebSite` —— 写法规范。
- `canonical` 自引用正确。
- `meta description` 每页已带独特数据（如「#1 of 10 / 217 plans」vs「#2 of 10 / 211 plans」），长度约 135 字符。
- 内链结构、数据表格、价格/网络/排名/竞对价格数字。

---

## 2. 硬性规则（HARD RULES，违反 = 该页不合格）

### 2.1 绝对不改
- ❌ 不改 JSON-LD、canonical、meta description 模板结构（可保持每页 meta desc 数据唯一，但结构不动）。
- ❌ 不改数据表格、价格数字、$/GB、排名、网络名称与速率、竞对入场价。
- ❌ 不改内链结构、页面外壳（导航/页脚/侧栏）。
- ❌ 不改「数据型」H2 与 H3 的信息含义（plans / unlimited-FUP / networks / vs providers / FAQ 这 5 个信息型 H2 保留）。

### 2.2 必须改
- ✅ 所有叙事段落：verdict 开头与结论、intro、who-it-fits、honest trade-offs、trip-length 结论、各 section 的引导句。
- ✅ 4 个「叙事型」H2 标题按国重写（见 §4 的 H2 清单标注）。
- ✅ FAQ 里至少 1–2 问换成该国特有问题。

### 2.3 绝对禁止（反例见 §7）
- ❌ 只换国家名 + 同义改写（这是你现在正在犯的错）。
- ❌ 编造数据：网络覆盖、速度、价格、竞对价必须来自真实数据源（现有 network map / carrier breakdown / 价格索引），不得虚构。
- ❌ 编造评分、评论、用户数、奖项。
- ❌ 用空话/放诸四海皆准的句子凑字数（如「总的来说，{brand} 是大多数人的不错选择」）。
- ❌ 把英语国家名硬塞进非英语语境（页面是英文，保持英文写作）。

---

## 3. 每国差异化框架（怎么写才不一样）

为每个国家，按下面三步确定一个「主角度」，然后让整页叙事围绕它：

### 第 1 步：确定网络现实（查真实数据）
- 运营商数量、5G 覆盖、城乡差异、最强者。
- 例：新加坡 = 三网近全域覆盖、无死角、含 MRT；日本 = Docomo 覆盖金标准，山区/离岛/地下需 Docomo。

### 第 2 步：确定旅行者画像
- 转机短停留 / 观光长停留 / 商务 / 家庭 / 背包客。
- 例：新加坡 = 樟宜转机、商务、2–5 天；日本 = JR 长途、7–30 天、城乡混走。

### 第 3 步：确定差异化角度（不要总是「哪家便宜」）
从下面选 1 个主角度 + 1 个副角度，写进 verdict / intro / H2 措辞：
- **覆盖确定性**（全岛/全域无死角）
- **乡村/山区覆盖**（离城市后谁靠谱）
- **长停留成本**（30 天 $/GB 与 FUP 撞线）
- **转机/短停留**（3 天内的最小花费）
- **多人共享限制**（热点/FUP 对家庭的影响）
- **本地竞对锚点**（机场卡 / 当地运营商套餐对比）

**示范（真实数据，AI 直接照这个力度写）：**
- **新加坡**：主角度「覆盖确定性 + 短停留」。verdict 写「全岛覆盖近一致（含 MRT），选最便宜即可，不用为覆盖付溢价」；who-it-fits 写「转机/商务 2–5 天」。
- **日本**：主角度「乡村覆盖 + 长停留」。verdict 写「离开城市走 JR/山区，优先 Docomo 底网」；who-it-fits 写「7 天以上城乡混走」；trade-offs 写「长停留会撞 3GB/day FUP」。

---

## 4. 逐区块改写要求（对照现有 10 个 H2）

> 标注：`【数据·保留】` = 不改数据；`【叙事·重写】` = 必须按国重写。

1. **H2「Is {brand} the right eSIM for {country}」(verdict)** — `【叙事·重写】`
   开头第一段必须写该国特色场景（转机 6 小时 / 坐 JR 从东京到大阪…），给出一个基于该国真实数据的明确结论 + 理由，禁止空泛总评。

2. **H2「All N {brand} {country} plans」(套餐表)** — `【数据·保留】`
   表格不动。仅重写表前 1–2 句导语，落到该国具体用法（「只转机 6 小时，1GB 就够」vs「7 天 JR 行程建议 10GB 档」）。

3. **H2「{brand} {country} eSIM hotspot 5G and fair-use rules」** — `【数据·保留 FUP 数值，叙事·重写】`
   FUP 规则数值（如 3GB/day → 1Mbps）如果品牌相同则保留原样；但要写「为什么在该国重要」（日本长停留会撞线；新加坡短停留基本不会）。

4. **H2「Is {brand} unlimited data in {country} really unlimited」** — `【同上】`
   结合该国用法写，不要复读规则。

5. **H2「Which network does {brand} ride in {country}」** — `【叙事·重写，最该差异化的地方】`
   写该国运营商覆盖叙事（把现有 network map / carrier breakdown 的真实覆盖差异放大成段落）：日本写「Docomo 是山道/离岛/地下室的覆盖金标准，SoftBank 城际强，KDDI 均衡」；新加坡写「三网近全域一致，选最便宜即可」。

6. **H2「What {brand} costs by trip length in {country}」** — `【数据·保留表格，结论·重写】`
   结论必须按该国真实排名给（谁在 3/5/7/10/15/30 天更便宜），禁止套「不同天数不同结论」这种万能句。

7. **H2「Should you buy {brand} for {country}」** — `【叙事·重写】`
   「Buy it if」和「Look elsewhere if」按该国画像写（新加坡：短停留/转机→买；日本：要 Docomo 底网或长停留→看别家）。

8. **H2「Where {brand} wins and loses in {country}」** — `【叙事·重写】`
   Strengths / Watch out for 按该国写，不要泛化。

9. **H2「{brand} vs the other providers in {country}」** — `【数据·保留竞对表，导语·重写】`
   导语写该国竞对格局（谁是低价王、谁是无限制王、谁覆盖强）。

10. **H2「{brand} {country} eSIM questions」(FAQ)** — `【1–2 问换成该国特有】`
   保留 3–4 个通用问（多少钱/是否真无限/能否分享热点/哪家网络/与竞对比），至少 1–2 个换成该国特有（日本：北海道/京都农村覆盖吗？新加坡：MRT 地铁里能用吗？）。

---

## 5. 输入 / 输出契约

**输入（每国一次）**：
- `{country}` 国家名、`{brand}` 品牌名
- 该国真实数据：套餐表（价格/流量/天数）、$/GB、排名、国家基准价、竞对入场价、运营商列表+速率+覆盖、FUP 规则、行程天数对比结论
- 该国搜索意图角度（由 §3 框架产出，或由你按 §3 自行判断后列出）

**输出（每国一次）**：
- 改写后的「叙事文案」逐 section（对应 §4 的 10 个 H2）
- 重写后的 4 个叙事型 H2 标题
- 该国特有 FAQ（1–2 问）
- **不输出、不碰**：JSON-LD、canonical、meta description、数据表、内链、数字

---

## 6. 质检门槛（每国改完必须自检，不达标 = 打回）

- [ ] 非表格叙事文案独特占比 ≥ 40%（自测法：抹掉数字/国家名/品牌名/运营商名后，与该品牌另一国页面逐句对比，相同句占比须 ≤ 60%）
- [ ] 10 个 H2 中 ≥ 4 个叙事型 H2 措辞与该国意图相关、非逐字同模板
- [ ] FAQ 有 ≥ 1 个该国特有问题
- [ ] verdict 第一段出现该国具体场景（转机 / 铁路 / 山区 / 城市等），而非空泛总评
- [ ] 未改动任何 JSON-LD / canonical / 数据数字 / meta description 结构
- [ ] meta description 仍每页唯一且含该国数据、≤ 160 字符
- [ ] 全英文写作，无中文，无编造数据

---

## 7. 反例（这些输出直接判不合格）

**❌ 换名改写（禁止）**
> "Roamic is a solid choice for Singapore, offering good value for most travelers."（换成 Japan 一样成立）

**✅ 合格（有国家特异的结论）**
> "Singapore's three networks are near-identical island-wide, including the MRT — so for a 2–5 day stopover there's no reason to pay a coverage premium. Pick the cheapest plan and go."

**❌ 空话（禁止）**
> "Different trip lengths need different plans, so it depends."

**✅ 合格**
> "At 3/5/7 days Roami undercuts Roamic by $0.01–$0.02; from 10 days Roamic flips cheaper. If your Japan leg runs past a week, Roamic's metered 10GB tier is the better buy."

**❌ 编造数据（禁止，一律打回）**
> 任何来源不明的覆盖百分比、速度数值、评分、用户数。
> 只能用 network map / carrier breakdown / 价格索引里的真实数据。

---

## 8. 执行顺序建议（批量场景）

1. 先选定品牌（当前 Roamic），拉出全部国家清单。
2. 每国先用 §3 产出「主角度 + 副角度」一行，批量过一遍，确保 50 国角度不重复。
3. 再按 §4 逐 section 产出叙事文案。
4. 每国跑 §6 自检；不达标的重写叙事段，不要动数据。
5. 同一套流程平移到下一个品牌。

---

## 附录：完整 SEO 分析报告（参考，非执行指令）

> 本附录是原始分析全文，供 AI 和人工参考「为什么这么改」。执行动作以正文 §2–§6 为准。
> 样本：`/compare/singapore/roamic/`（SG） vs `/compare/japan/roamic/`（JP）。

### A. 量化证据

| 指标 | Singapore | Japan | 结论 |
|---|---|---|---|
| 正文总块数 | 147 | 148 | 几乎一致 |
| 模板共用块（抹掉国家/价格/网络/品牌后相同） | 136 (92%) | 137 (92%) | 🔴 同质化严重 |
| 真正国家特有块 | 11 (8%) | 11 (8%) | 增量存在但占比低 |
| 正文词数 | 16,255 | 16,333 | 几乎一致 |
| 内链 / 图片数 | 175 / 88 | 175 / 88 | 完全一致 |

### B. 架构对比（逐字，仅换国家名）

- **Title**：`Roamic {Country} eSIM Review 2026: Data Plans Compared`
- **H1**：`Roamic {Country} eSIM Plans & Prices (2026)`

**10 个 H2（SG 与 JP 逐字相同，仅替换国家名）**：

1. Is Roamic the right eSIM for {Country}
2. All 36 Roamic {Country} plans
3. Roamic {Country} eSIM hotspot 5G and fair-use rules
4. Is Roamic unlimited data in {Country} really unlimited
5. Which network does Roamic ride in {Country}
6. What Roamic costs by trip length in {Country}
7. Should you buy Roamic for {Country}
8. Where Roamic wins and loses in {Country}
9. Roamic vs the other providers in {Country}
10. Roamic {Country} eSIM questions

**14 个 H3 也逐字相同**（含：Hotspot and tethering / Speed and 5G / Fair-use threshold / Top-ups / Price it for your own dates / Buy it if / Look elsewhere if / Strengths / Watch out for / 及页脚导航级 H3）。

### C. 结构化数据（JSON-LD）——合格，勿改

每页 6 组 JSON-LD，写法规范：

| # | 类型 | 状态 |
|---|---|---|
| 1 | `BreadcrumbList`（4 层：Home / Compare / {Country} eSIM / {Brand}） | ✅ |
| 2 | `Organization` | ✅ |
| 3 | `WebSite` | ✅ |
| 4 | `Product` + `Brand` + `AggregateOffer`（lowPrice 2 / highPrice 43 / offerCount 36 / USD + 36 个 Offer） | ✅ 规范 |
| 5 | `WebPage` + `WebSite` | ✅ |
| 6 | `FAQPage`（5 Q&A） | ✅ |

> 结论：`AggregateOffer` 同时带聚合字段（lowPrice/highPrice/offerCount/priceCurrency）和 36 个子 Offer，是正确写法，**不要动**。

### D. SEO 合规评估

**✅ 合格项**：
- 数据增量真实有用：36 套餐、$2.00 起、$/GB 排名（SG #1 $0.40/GB vs JP #2 $0.66/GB）、本地运营商+速率、行程天数对决、9 家竞对入场价——是真数据，非薄内容。
- JSON-LD 齐全且规范（见 C）。
- `canonical` 自引用正确。
- `meta description` 存在且每页带独特数据（SG「#1 of 10 / 217 plans」vs JP「#2 of 10 / 211 plans」），约 135 字符。
- 内链 175 条，hub-spoke 清晰。

**🔴 风险项（按严重度）**：
1. **92% 模板文案 → 规模化内容滥用风险（P0）**：Google 2024/03 spam policy 的「scaled content abuse」与「doorway pages」。50 国 × 多品牌铺开后，骨架+文案完全相同 = 判「同一页面换地名」。
2. **标题/H1/H2 完全同模板 → 无搜索意图差异化（P0）**：每页都在抢同一查询，没按国家意图拉开长尾。
3. **hreflang 只自引用 `en-us`（P2）**：单语站不需要 hreflang，自引用 `en-us` 也不规范（应为 `en` 或移除）。
4. **FAQ 5 问全同模板（P1）**：缺国家特有问题。

### E. 解决方案（优先级汇总）

- **P0**：解耦「数据模板」与「叙事文案」；数据照旧注入，叙事每国重写，独特文案占比 8% → ≥40%。
- **P0**：按国家做搜索意图差异化（网络现实 → 旅行者画像 → 意图角度），见正文 §3。
- **P1**：骨架去同质化——保留 5 个信息型 H2，4 个叙事型 H2 按国重写；FAQ 每国换 1–2 个本地化问题。
- **P1**：增加真实国家上下文（落地场景、当地运营商资费锚点），只用已有真实数据，不编造。
- **P2**：清理 hreflang（移除自引用 `en-us` 或改 `en` + 双向组）。
- **P3**：把「独特文案占比 ≥40%」落成每页硬指标，接入生成/审核流程。

### F. 关键结论（一句话）

数据没问题、技术 SEO 没问题；问题在**骨架和 92% 的句子是同一条模板**。核心动作 = 叙事文案每国重写 + 按意图错开，数据照旧注入即可。
