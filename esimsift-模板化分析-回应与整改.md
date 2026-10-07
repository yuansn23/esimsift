# 品牌子页模板化问题 —— 复核、整改与后续方案

> 复核对象：`esimsift.com/compare/austria/alosim/` 与 `/compare/austria/airalo/`
> 方法来源：`esimsift-模板化分析.md`（方法论沿用，口径重算）
> 实施日期：2026-10-07（第四十六轮）
> 范围声明：**不含**作者署名 / bio / 资质（按你的要求暂不处理）

---

## 一、结论：是模板化，而且这是全站性问题

**是**。两个页面的 H2 骨架只有 1 处差异（aloSIM 多一个 `#fup`，因为它卖无限套餐），
9 个 H2 标签同构为 `{brand} … in Austria` 模式。

但我**重算了口径**，因为原文档的「行」把表格单元格、列头、徽章也算成了正文行，
那会把重复率虚高；只取 prose 标签（`p/li/blockquote/figcaption`）才可比。

| 指标 | 原文档 | 我的复算 |
|---|---|---|
| 正文行数 | 234 行 | **269 / 321 行** |
| 品牌+数字归一化后共享 | 146 行 | **101 行（占 alosim 80%、airalo 84%）** |
| 真正 unique prose | 27 / 19 行 | **25 / 19 行** |
| 骨架是否 100% 相同 | 是 | **不是**（10 H2 vs 9 H2） |

**结论一致，但更要紧的是下面这个数字**：按「句子槽位」算（槽位 = 全组句子总数，
模板槽位 = Σ 该模板句出现的页数），奥地利 10 个品牌页的模板槽位占比是 **74%**。
「10 页里有 33 条句子逐字相同」听上去不多，但它占用 330 个槽位。

---

## 二、全站同质化地图（这是原文档没有的部分）

新增工具 `scripts/audit_boilerplate.py` 做**句子级**普查（只读 `public/`，不联网）：

| 页型 | 分组口径 | 页数 | 模板槽位占比 | 判读 |
|---|---|---|---|---|
| **品牌子页** | 同国内跨品牌 | 10/国 | **74–76%** | ❌ 最重 |
| 品牌子页 | 同品牌跨国家 | 50/品牌 | 55–64% | ❌ |
| 品牌 Hub | 全站 | 10 | **55%** | ❌ |
| 国家页 | 全站 | 51 | **49%** | ❌ |
| 对决页 | 全站 | 45 | 40% | ⚠ |
| networks | 全站 | 12 | 16% | ✅ |
| guides | 全站 | 10 | 0% | ✅ |

**所以不只是这两个页面 —— 四个页型都在同一区间。**

### 关键发现：唯一的「跨页型」自我重复

同一句话在两个模板里各写了一个版本：

- 品牌子页：`Price is only half of the decision.`
- 品牌 Hub：`Price is only half **the** decision.`

---

## 三、方法论纠偏：为什么「换措辞」是反向操作

这是本轮最重要的一条，它决定了整改方向。

原文档第 4 节建议「删或变量化骨架标签」。**照做会适得其反**：

1. **Google 判定原文是** *"producing many pages … that are substantially the same
   regardless of **minor variations**"* —— **「换措辞」正好就是 minor variations 的定义**。
   把「The masts behind the plan」改成 5 种说法，页面对 Google 而言仍然「实质相同」。
2. **有些重复是必须的**。`Typical speeds are our editors' reads of each operator's own
   coverage data.`、`Only plans whose validity covers the whole trip are counted here.`
   这类是**方法论披露**。逐页改写成不同说法，等于让读者无法确认口径一致 ——
   **一致性本身就是 E-E-A-T 的信任信号**，改它是在扣分。
3. **词法指标有地板**。任何「每页都渲染一次」的区块（竞品卡、计算方法、安装步骤），
   无论建多少变体，每种变体都会出现在每一页上，指标不会动。
   追这个指标追到零是不可能也不该的。

**正确方向只有两条：**

- **A. 换实质不换说法** —— 把零信息量的句子换成承载页内数据的句子。
- **B. 合并而非改写** —— 把重复的方法论 / 安装说明**收拢到单一权威页**，各页只留一句 + 链接。

---

## 四、本轮已实施（4 项）

### ① 竞品卡片：全局 tagline → 本国名次 + 入门档（最大一块）

`layouts/compare/provider.html` 的 `#others` 区块原本印 `providers.toml` 的全局 tagline
（`The no-logs eSIM from the NordVPN team` 等 11 条），**每条在 449 个页面上逐字出现，
合计约 4900 个正文句子槽位 —— 全站单点最大的一块重复内容**。

改为由页内数据算出的句子（3 个变体按卡序轮换 + 无限专营品牌单独分支）：

```
Airalo    Airalo ranks 3 of 10 on Austria cost per gigabyte — its cheapest plan is 1GB.
Holafly   Holafly sells unlimited Austria plans only — there is no $/GB figure to rank it on.
Ubigi     Ubigi's Austria entry plan is 3GB, which puts it 5 of 10 on cost per gigabyte.
Yesim     Yesim ranks 9 of 10 on Austria cost per gigabyte — its cheapest plan is 500MB.
```

注意 Ubigi 是 3GB、Yesim 是 500MB（其余多为 1GB）—— 说明是**算出来的**，不是套模板。
新增 i18n key：`compare_provider__op_market_v1..v3` / `compare_provider__op_unl_v1..v2`
（en + de 双语，key 已对齐）。

### ② 去掉同页冗余

`#tripcost` 的 `trip_note` 与 `#trip-calc` 的 `calc_note` **在同一页里把同一条规则解释了两遍**
（「30 天行程用 30 天档计价，而不是把短档叠起来」，措辞几乎相同）。
`trip_note` 已缩到只剩表格专属部分 + 本国对手说明。

### ③ FAQ 去掉通用开场白

答案引擎摘走的是答案第一句，而第一句原本是纯套话：

- `faq_a_hotspot`：删掉 `Tethering rules are where travel eSIMs quietly hide their limits.`，直接给政策事实
- `faq_a_unlimited`：删掉 `It depends on what the label means here.`，直接给 FUP 原文

### ④ 修掉一处语法 bug

`reality_lead` 原文是 `whether a {{ .brand }} plan actually works` ——
**aloSIM 会渲染成 "a aloSIM plan"**（品牌名从 Airalo 到 Yesim 混着元音/辅音开头，
一个固定冠词不可能全对）。已改为 `whether the {{ .brand }} pick survives`。

### ⑤ 新增诊断工具 `scripts/audit_boilerplate.py`

- 把「跨页模块 md5 去重 = N」那条判据的**盲区**补上：
  块级去重是**必要不充分**条件 —— 区块里只要有一个页内专属数字，md5 就唯一，
  「95% 句子雷同、只换一个价格」的区块照样全绿。**奥地利 10 个区块块级去重 10/10 全唯一，
  句子级却是 74%** —— 两个尺子必须都跑。
- 用法：`python -X utf8 scripts/audit_boilerplate.py [--type X] [--group-by country|brand] [--show N]`
- **不进 `npm run build`**（它是诊断工具，不是守卫；给阈值会让它变成可被「优化掉」的指标）。

---

## 五、效果（同一把尺子，前后对比）

| 口径 | 前 | 后 | 变化 |
|---|---|---|---|
| 品牌子页全站 槽位 | 42,174 | 41,234 | −940 |
| 品牌子页全站 **模板槽位** | **18,194** | **12,772** | **−5,422（−30%）** |
| 品牌子页全站 占比 | **43%** | **31%** | −12 pt |
| 奥地利同国内 | 623 槽 / 74% | 604 槽 / 74% | 基本未动 |

**同国内几乎没动，这是预期内的**，也正好印证第三节：同国内剩下的重复是
**国家级事实 + 方法论披露 + 计算器说明**，而那三类的正确修法是「合并」不是「改写」。
站点级降了 12 点，主要来自竞品卡片那一块的替换。

---

## 六、剩余问题与后续方案（按优先级）

### P1 —— 国家页的「安装说明」与现成 guide 重复

国家页有一整段「How to install your Austria eSIM」三步（Buy / Install on Wi-Fi / Land and…），
而 `/guides/how-to-install-esim/` **已经是同一份内容**，在 50 个国家页上重了 50 遍。

- **建议**：国家页只留一句 + 链到 guide。移除约 50 段重复块，且不损失任何信息。

### P1 —— 方法论披露收拢成单一页

> **⚠️ 复核更正（2026-10-07 第二轮）**：本条是**误判，实际早已完成**。
> `/methodology/` 页存在（`content/en/methodology.md`，四节：采集口径 / 指标公式 / 公平使用 / 更正政策），
> 且**已被 699 个产物页链接、链接总数 1679**（`compare/single.html:362`、`esim-providers/single.html:41&584`、
> `vs-single.html:114&359`、`index.html:45&178`、`esim-deals/list.html` 等均已在正确位置链出）。
> 上一轮只核了句子文本、没核链接，把「已存在」写成了「待建」。
> **教训**：判定「某页/某能力缺失」前，先 `grep -rn "<路径>" layouts/` 数一遍实际链接数，
> 不要从一句话的存在与否反推整页的存在与否。

`Badges compare against all N … see our methodology`、`Prices in USD as listed by…`、
`Rankings and "cheapest" badges on this site are computed by price alone…`、
`Typical speeds are our editors' reads…`、`Only plans whose validity covers the whole trip…`
这 5 类在美国家页 / 品牌 Hub / 对决页 / 品牌子页上重复出现。

- **建议**：建 `/methodology/` 单一权威页（**这是 E-E-A-T 的加分项，正好补原文档说的
  「作者署名先不管」留下的 How 缺口**），各页保留**一句短披露 + 链接**。
  注意：**保留的那一句必须全站逐字一致** —— 披露不能变量化。

### P2 —— 品牌 Hub 的两条零信息句

- `Price is only half the decision.`（与子页版本还不一致，应统一）
- `These four terms decide whether the plan actually works on the trip you are taking.`

`#reality` 的四个卡片本身已带真数据（hotspot 状态、FUP 阈值、5G），
开场白应把**该品牌自己的政策数字**搬上来，而不是说「价格只是一半」。

### P2 —— 对决页的 FAQ 与脚注

`45/45` 逐字相同的 8 条里，除方法论外还有：
`“Best $/GB” compares each provider's cheapest per-gigabyte rate…`、
`The gap flips by destination, so check your country in the table above.` ——
后者是**零信息量**的祈使句，应换成该 matchup 的**实际翻盘国家数**（数据已有）。

### P3 —— 跨模板文案统一

`Price is only half of the decision.`（子页）vs `Price is only half the decision.`（Hub）
应统一为一句，避免同一站两套说法。

### 不做（并说明理由）

- **不给方法论句做措辞变体** —— 见第三节第 2 条，那是扣分项。
- **不把国家级事实（运营商描述、测速区间）按品牌改写** —— 八品牌 × 50 国
  `networks` 完全一致，逐品牌改写只能靠编造差异。
- **不加作者署名 / bio** —— 按你的要求本次不动。

---

## 七、验收证据（按你的约定：不做截图）

- `npm run build` **EXIT=0**，九项校验全绿：
  `704 files (702 pages), 4028 JSON-LD`；`17769 h2/h3, bad: 0`；品牌子页 13 项全过；
  FAQ 事实校验 `100 country pages OK`（含 R10/R11）；日期一致性 OK；无回归 A/B/C 通过。
- **变更面精确归因**：`verify_no_regression.py --diff` 报
  **「变更 499 = provider_sub，新增 0、删除 0」** —— 改动只波及品牌子页，其他页型零波及。
- 零回归基线已重建（`docs/regression-manifest.json`，702 文件）。
- 新卡片文本已从产物中抽取核对，确认带真数据（Ubigi 3GB / Yesim 500MB）。

---

## 八、一条口径声明

「模板化」是**确定性机械结论**（可复现、可复算），可信度高。
但「Google 会不会惩罚」无法用任何第三方打分预测 —— 真正定生死的是 Search Console 表现。
本文所有整改都是**在不编造事实的前提下提高每页信息密度、并减少真实冗余**，
这两件事无论 Google 怎么判都是正向的。

---

## 九、第二轮整改（2026-10-07，P1/P2/P3）

### 9.1 本轮改动（5 项，全部是「删除/合并真实重复」，不是措辞变体）

| # | 位置 | 改法 | 为什么这是对的 |
|---|---|---|---|
| ① | 国家页 `#choose` 安装卡（50 国 × 双语） | 三步有序列表（Buy / Install on Wi-Fi / Land and it works）→ **一句 + 按钮链到 `/guides/how-to-install-esim/`** | 那三步与 guide 是**同一份内容**，在 51 页上重了 51 遍。正文归到单一 URL |
| ② | 国家页安装卡的机型说明 | `Works on eSIM-capable phones (iPhone XS and newer…)` + `Your physical SIM keeps working` → **一句 + 链到 `/guides/esim-compatibility-check/`** | 同上：完整设备库已有专页，50 页复述简版是第二处重复 |
| ③ | 品牌 Hub `#reality` 导语 | `Price is only half the decision. These four terms decide…` → **`Quoted from {brand}'s own published policy. Where a brand publishes nothing, we say so rather than guess.`** | 原句零信息量（四张卡自带标题与数据）；新句是**来源披露**，与卡内不重复。附带消解了 P3 ⑤ 的「子页 / Hub 两套说法」 |
| ④ | 品牌 Hub 页内重复披露 | 删除 `Rankings and "cheapest" badges…computed by price alone` 的**第二处**（正常页分支那处） | 同一页同一句出现两次；页尾另有 `every price, badge and ranking on this page is a literal sort…` 完整披露，删后不缺口径 |
| ⑤ | 对决页 FAQ 首答末句（45 页） | `The gap flips by destination, so check your country in the table above.` → **`The widest entry-price gap is in {country} — {A} lists ${x} against {B} at ${y}.`**（由 `$rows` 现算） | 原句是零信息祈使句，且在 `50 win / 0 loss` 的 matchup 上自相矛盾（无「翻盘」可言）；新句是**每页不同的真数据**。全平手时降级为 `Every shared country is an exact price tie…` |

### 9.2 效果（同一把尺子）

| 页型 | 模板槽位（前 → 后） | 变化 |
|---|---|---|
| 国家页 `country` | 3232 → **3182**（51 页） | −50 槽 |
| 对决页 `vs` | 1289 → 1289 | 持平，但**新句已不在指纹列**（= 真差异化，非换皮） |
| 品牌 Hub | 792 → 792 | 持平（删 1 句、换 1 句等长；删的第二处属同页重复，不在 fingerprint 采样内） |

**⚠️ 口径警告（本轮新踩）**：`模板槽位 / 总槽位` 这个**占比**对「删内容」不敏感 ——
删掉重复块时分子分母**同步下降**，占比可能纹丝不动。衡量「减少真实重复」必须看
**绝对量**：本轮国家页每页净减 **274 字符**可见文本（旧 497 → 新 223），× 51 页 ≈ **14,000 字符**。
「占比」适合横截面比较不同页型，「绝对量差」才适合衡量单轮改动的成效。

### 9.3 归因与验收

- `npm run build` **EXIT=0**，九项全绿：`704 files (702 pages), 4028 JSON-LD`；`17769 h2/h3, bad 0`；
  品牌子页 13 项全过；FAQ 事实 `100 country pages OK`（R10/R11 骨架与邻国去重均过）；日期一致；A/B/C 全过。
- **变更面精确归因**：`verify_no_regression.py --diff` 报
  **变更 155 = `country_hub` 100（50 EN + 50 DE）+ `matchup` 45 + `provider_hub` 10，新增 0、删除 0**
  —— **品牌子页 0 变更**，与「本轮只碰国家页/对决页/hub」完全吻合。
- **反同质化判据**：三个页型的**内容模块全部唯一**；报出的「重复」模块逐条查证后确认全是
  **UI 骨架与导航**（国家页 `plan-filter-count` 空容器 / `guides` 导航列表；对决页 `k<brand>` 论据容器 / `more` 导航；
  hub 的 17 个 `calc-*` 计算器控件）—— 这些**必须全站一致**，差异化反而是错的。
- 零回归基线已重建（`docs/regression-manifest.json`，702 文件；`class_counts` 13 类）。
- 德语站验证：`/de/compare/austria/` 已渲染**德语**新文案（`Kaufe und installiere die eSIM vor dem Abflug…`），
  两条 guide 链接经 `lang-href` 回落英文路径（德语站无单篇 guides），**不产生 404**。

### 9.4 本轮查证后「不做」的（附理由，避免下一轮重复劳动）

- **Hub 页两个同名 H2**：`#tradeoffs-pending` 与 `#tradeoffs` 文本完全相同，
  但**分属互斥分支**（前者在 `{{ if not $a }}` 价格未入库的降级壳页内，后者在 `{{ else }}` 正常页内），
  同一页面**不会同时出现** —— 不是重复标题。**先确认分支关系再下结论**。
- **Hub 退款/客服两句披露**（`As published on…` / `Summarised from… Full conditions live on…`）：
  分属「客服」与「退款」两张不同卡、主题不同，合并会丢信息 → 保留。
- **剩余 47%（国家页）/ 55%（hub）的模板槽位**：逐条看过，成分是
  **方法论披露 + 区块引导语 + 计算器/UI 说明 + 来源声明**。按 §三第 2 条，
  **一致性本身就是 E-E-A-T 信任信号，变量化是扣分**。到此为止是正确终点，不是遗漏。

### 9.5 顺带发现（本轮未动，登记在案）

1. **德语站国家页有大量英文段落** —— 不只是我改的这两处：抽样 `/de/compare/austria/` 的安装卡标题仍是
   `How to install your Österreich eSIM`，`i18n/de.toml` 里 `compare_single__*` / `esim_providers_single__*`
   一族**存的是英文原文**（约上百条）。德语站无品牌 hub / 无单篇 guides，部分是死键；
   但只要德语国家页存在，这些英文就会露出来。**属 i18n 完整性，非同质化问题**，应单开一轮。
2. **`layouts/esim-providers/single.html` 的两处披露是硬编码英文**（601 / 606 行，未走 i18n）——
   `check_i18n.py` 的「禁新增硬编码」是**白名单式**的，存量仍放行。

---

## 十、两组定向审核（2026-10-07，用户点名 4 个 URL）

用户要求按**两个维度**各审一次：**组 1 同国跨品牌**（`/compare/austria/alosim/` vs `/compare/austria/airalo/`）、
**组 2 同品牌跨国家**（`/compare/united-states/yesim/` vs `/compare/japan/yesim/`）。

### 10.1 两组数字（同一仪器：`audit_boilerplate.py` 的口径 + 页对页句级交集）

| | 组 1 同国跨品牌 | 组 2 同品牌跨国家 |
|---|---|---|
| 页对页句数 | 72 / 71 | 74 / 73 |
| **共享句** | **59（82% / 83%）** | **36（49% / 49%）** |
| 组内聚合（工具口径） | **73%**（811 槽 / 594 模板槽） | **48%**（4145 槽 / 1969 模板槽） |

### 10.2 关键洞察：两组差值（82% vs 48%）的成因

**组 1 的 10 页共享同一个国家** → 「国家级事实」整块共享（`#hostnetwork` 的运营商名单 + Ookla 基准 + 测速句、
`#faq` 里讲运营商与基准的两句、`#reality` 的「最快宿主网络」）。
**组 2 的 50 页国家各不同** → 国家级事实**完全不重复**，剩下的只有「品牌档案」那一小块。

> **口径副产品**：`norm()` 只归一化**数字**与**品牌名**，**不归一化国家名** —— 所以
> `Both work in {{ .country }}, …` 这类句子在**跨国分组**里不算重复（国家名不同），在**同国分组**里算重复（国家名相同）。
> 这是**正确**的：同国页面确实逐字重复同一句。但也意味着**「同国」才是同质化的高风险面**。

### 10.3 共享句逐条归因（59 条 / 36 条，全部定性）

**组 1（同国跨品牌，59 条）**

| 区块 | 条数 | 性质 | 可改？ |
|---|---|---|---|
| `faq` | 11 | 区块标题 1 + 国家级事实 2 + 数据句 5 + 方法论 1 + 链接文本 2 | ❌（本轮已删掉其中唯一的套话，12→11） |
| `others` | 8 | **同国竞品集合相同**（这是事实）+ 竞品数据 | ❌ 结构性：任何句式都会重复同一批对手 |
| `hostnetwork` | 8 | **国家级事实**（运营商 / Ookla 基准 / 测速）+ 方法论 | ❌ 共享是正确行为 |
| `tradeoffs` | 7 | 品牌级事实（data-only、档位跨度） | ❌ |
| `reality` / `fit` | 4 + 4 | 测速句（国家级）+ 事实驱动的「最便宜品牌」反例 | ❌ |
| `tc-w-days` / `plan-rows` / `verdict` / `tc-none` / `plans` / `fup` / `tripcost` / `tc-out` / `trip-calc` | 17 | 方法论披露 + UI 标签 + 计算器说明 | ❌ |

**组 2（同品牌跨国家，36 条）**

| 区块 | 条数 | 性质 | 可改？ |
|---|---|---|---|
| `reality` | 8 | **品牌级档案**（FUP 阈值、热点规则、top-up 政策） | ❌ 一致性 = E-E-A-T 信任信号 |
| `tradeoffs` | 7 | **品牌级档案**（品牌史、档位跨度、FUP 降速） | ❌ |
| `faq` | 5 | 品牌级 + 方法论 | ❌ |
| `fit` / `tc-w-days` | 3 + 3 | 事实驱动 + 计算器说明 | ❌ |
| 其余 10 条 | 10 | 方法论 + UI + 日期 + 链接文本 | ❌ |

**结论：两组剩下的重复，可改的条数是 0。** 它们全部落进第四十六轮定义的「不许改写」三类：
**国家级事实 / 品牌级档案 / 方法论披露与 UI**。唯一还能动的是「套话」，本轮已经删完。

### 10.4 本轮据此做的唯一改动

`compare_provider__faq_a_rival`（影响全部 **499** 个子页）的第一句
`Both work in {{ .country }}, and the answer depends on how much data you will actually use rather than on either brand.`
→ **删除**（与第四十六轮对 `faq_a_hotspot` / `faq_a_unlimited` 的处理一致：答案引擎摘的是**答案第一句**，
不该是套话）。改后答案直接从事实开始：

> `aloSIM's cheapest plan here is $4.00; Yesim's is $0.51, though that entry price buys 500MB. The full ranking …`

**效果**：组 1 共享句 **60 → 59**（`faq` 12 → 11）；组 1 组内模板槽位 **604 → 594**；
组 2 模板槽位不变（该句含国家名，在跨国分组里本来就不计为模板槽位 —— 见 10.2）。
`--diff` 报 **变更 499 = provider_sub，新增 0、删除 0**；基线重建 702 文件。

### 10.5 为什么不继续改（这是审核的结论，不是没做完）

想再往下压只有两条路，**两条都不该走**：

1. **给 `#others`（8 条）换句式** —— 同国 10 页必然列同一批对手，换句式 = 同一句话换一个品牌名 = **minor variations**（第四十六轮已论证是反向操作）。
2. **按品牌裁剪竞品列表**（如只列 3 家最值得对比的）—— 能降指标，但**牺牲信息完整性**（读者看不到全部选项），且 `#others` 承担的是**导航职能**（跳到竞品子页），不是内容填充。

因此两组到此为**正确终点**。若将来要继续降「同国跨品牌」的重复面，
唯一站得住的方向是**减少国家级事实在各页的复述次数**（本轮已把安装说明与机型说明两处链出到 guide），
而不是改写句式。
