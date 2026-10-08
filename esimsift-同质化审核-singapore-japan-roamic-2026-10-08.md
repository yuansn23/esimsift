# 品牌×国家子页同质化审核报告

**审核日期**：2026-10-08
**审核对象**（用户点名的两组，URL 已按实际路径纠正笔误）：

| 组 | 维度 | 页面 A | 页面 B |
|:--|:--|:--|:--|
| **A** | 同一个国家 · 不同品牌 | `/compare/singapore/roamic/` | `/compare/singapore/airalo/` |
| **B** | 不同国家 · 同一个品牌 | `/compare/singapore/roamic/` | `/compare/japan/roamic/` |

> 用户在消息中写作 `airlao` / `japane`，实际路径为 `airalo` / `japan`，本报告按实际路径核算。

**取数方式**：全部结论来自 `public/` 已构建产物的文本抽取，未做截图。主指标由仓库脚本 `scripts/audit_boilerplate.py` 产出（可复跑），关键结论另用独立脚本对拍（见 §9.3）。

---

## 一、执行摘要

| 判定项 | 组 A（同国跨品牌） | 组 B（同品牌跨国家） |
|:--|:--|:--|
| **模板槽位占比**（主指标） | **74%**（singapore） | **86%**（roamic） |
| 同维度全量区间 | 50 国：73–75% | 10 品牌：86–90% |
| 每页独有文案 | 15 句 / 18.0% | **6 句 / 7.3%** |
| 两两页面平均重叠 | 79.0% | **86.6%** |
| 页内重复 | 72 槽 | **543 槽** |
| 页面架构 | 10 区块，完全同构 | 10 区块，完全同构 |
| 结构化数据 | 6 类 JSON-LD，完全同构 | 6 类 JSON-LD，完全同构 |
| **同质化风险评级** | **中**（可接受） | **中高**（建议处理） |

**三句话结论**：

1. **两组都存在真实的模板化结构，但程度不同** —— **同品牌跨国家（组 B）比同国跨品牌（组 A）更同质**（86% vs 74%）。这与我此前 2026-10-07 那轮的结论**相反**，原因是那轮的度量脚本有口径错误（详见 §9.2），本轮已修正。
2. **这不是 doorway page，但增量偏薄**。差量集中在「各国套餐表数值」与「宿主网络」两处；其余 8 个区块在 50 页之间几乎完全相同。
3. **有一个现成的、完全没被启用的资产可以立刻改善它**：`data/countries.toml` 里已有 **101 条逐国研究内容（quirks，50 国全覆盖）**，但在品牌子页产物里**命中 0 条**（详见 §六）。

---

## 二、主数据

### 2.1 组 A —— 同国跨品牌（新加坡 · 10 个品牌子页）

```
singapore    10 页   817 槽位   模板槽位 602   → 74%   页内重复 72
```

同维度横向对照（50 个国家组）：**全部落在 73–75%**，无显著离群。

| 国家 | 页数 | 槽位 | 模板槽位 | 占比 | 页内重复 |
|:--|--:|--:|--:|--:|--:|
| austria | 10 | 811 | 594 | 73% | 77 |
| croatia | 10 | 806 | 592 | 73% | 81 |
| **singapore** | 10 | 817 | 602 | **74%** | 72 |
| japan | 10 | 851 | 642 | 75% | 85 |
| united-states | 10 | 821 | 612 | 75% | 77 |

### 2.2 组 B —— 同品牌跨国家（roamic · 50 个国家子页）

```
roamic       50 页  4205 槽位  模板槽位 3617   → 86%  页内重复 543
```

同维度横向对照（全部 10 个品牌）：**86–90%**，roamic 处于区间下沿。

| 品牌 | 页数 | 槽位 | 模板槽位 | 占比 | 页内重复 |
|:--|--:|--:|--:|--:|--:|
| roamic | 50 | 4205 | 3617 | **86%** | 543 |
| nomad | 50 | 4125 | 3538 | 86% | 373 |
| alosim | 50 | 4012 | 3455 | 86% | 385 |
| saily | 50 | 4035 | 3482 | 86% | 397 |
| airalo | 50 | 4048 | 3507 | 87% | 379 |
| roami | 50 | 4031 | 3514 | 87% | 351 |
| jetpac | 49 | 3965 | 3465 | 87% | 344 |
| ubigi | 50 | 3869 | 3395 | 88% | 255 |
| yesim | 50 | 4145 | 3657 | 88% | 435 |
| holafly | 50 | 4300 | 3880 | 90% | 491 |

**结论：组 B 的 86% 不是 roamic 的问题，而是这个页型的系统性水平。**

### 2.3 用户点名的四组「页对页」

| 页对 | 去重句 | 交集 | 重叠 | 各自独有 |
|:--|--:|--:|--:|--:|
| **A** singapore/roamic ↔ singapore/airalo | 72 vs 75 | 58 | **78.9%** | 14 / 17 |
| **B** singapore/roamic ↔ japan/roamic | 72 vs 75 | 58 | **78.9%** | 14 / 17 |

> 两组数字相同不是巧合、也不是脚本错误 —— `singapore/roamic` 是两组共用节点，它的共享面在两种分组下都落在 58 句。已核验：**两组交集彼此重合 48 句**，这 48 句是纯「品牌级档案 + 界面模板」，在两种分组下都会共享。

**注意页对页与组内聚合的差别**：组 A 的页对页（78.9%）≈ 组内平均（79.0%）；但组 B 的页对页（78.9%）**低于**组内平均（86.6%）—— 用户挑的这一对恰好是该组里差异较大的一对。

### 2.4 全站页型基线（新增，用于判断「74% / 86% 算高还是低」）

| 页型 | 页数 | 槽位 | 模板槽位 | 占比 | 页内重复 |
|:--|--:|--:|--:|--:|--:|
| guides（指南） | 10 | 819 | 0 | **0%** | 5 |
| networks（网络地图） | 12 | 1501 | 279 | **19%** | 22 |
| country（国家 Hub） | 51 | 6768 | 4364 | **64%** | 687 |
| provider_hub（品牌 Hub） | 10 | 1453 | 996 | **69%** | 236 |
| provider_sub（品牌×国家，本报告对象） | 499 | 40735 | 23990 | **59%** | 3953 |
| **vs（A-vs-B 对决页）** | 45 | 3375 | 2952 | **87%** | **1890** |

两点值得注意：

- `provider_sub` 合在一起看是 59%，但**拆开分组后同品牌跨国家是 86%** —— 「全页型汇总」会把不同分组方向的差异平均掉，**报这个数会掩盖真实风险**。
- **`vs` 对决页 87%，是全站最高的页型**，且页内重复 1890 槽（45 页，页均 42 槽）。这是本轮顺带发现的**比本报告对象更严重的问题**，建议单独立项。

---

## 三、共享的到底是什么

### 3.1 组 B：出现最广的句子（50/50 页）

按性质归为四类：

| 类别 | 示例 | 性质 |
|:--|:--|:--|
| **品牌级档案** | `– You need a local phone number — these are data-only plans.`<br>`@ states one figure everywhere: # GB at full speed in each #-hour period…`<br>`@'s product pages list hotspot as supported.` | 这是**该品牌的事实**，50 页理应一致 |
| **自身方法论** | `Typical speeds are our editors' reads of each operator's own coverage data.`<br>`Prices in USD as listed by @, excluding promo codes and taxes.`<br>`Last checked Sep #, #.` | 数据来源披露，E-E-A-T 必需 |
| **界面引导** | `Run the trip cost calculator .`<br>`The full calculator handles both.`<br>`Pick your trip length and this re-reads the plan table above…` | 控件说明，必须全站一致 |
| **国家级事实（骨架共享）** | `The fastest of those sustains roughly # Mbps…`<br>`The independent national benchmark is Ookla's Speedtest Global Index for @ .` | 骨架共享、数值各国不同 |

**这四类里没有一条是「为凑字数而写的套话」。** 改写它们只有两个结果 —— 变成 Google 明文点名的 *minor variations*（换说法不换实质），或删掉读者需要的信息。

### 3.2 组 B 的 50 页里，真正「国家专属」的只有两块

`croatia/roamic` vs `argentina/roamic`（毫不相关的两个地区）实测：

- 去重句 71 vs 72，**交集 63，重叠 88.1%**，croatia 仅 5 句独占
- 那 5 句**全部**是国家级事实：

```
+ Best $/GB in @ — $# against a $# benchmark
@ owns no towers in @, so your data rides the local host carriers — A1 Hrvatska, Hrvatski Telekom…
@'s best coverage — the pick for the coast and islands in summer.
Strong in Zagreb and the coastal cities.
```

**即：roamic 的 50 个国家页，差异只来自 `#hostnetwork`（该国运营商/速度/覆盖）与 `#others`（该国竞争对手价格）两块。其余 8 个区块 —— `verdict` / `plans` / `reality` / `fup` / `tripcost` / `fit` / `tradeoffs` / `faq` —— 的文案在 50 页之间基本一致。**

### 3.3 页内重复（本轮顺带量到）

| 页面 | 页内重复句数 | 涉及的区块 |
|:--|--:|:--|
| SG/roamic | 5 条 | `faq` × `reality` × `fup`，其中 3 条在**三个**区块各出现一次 |
| SG/airalo | 3 条 | 同上 |
| JP/roamic | 5 条 | 同上 |

`#reality` / `#fup` / `#faq` **三个区块职责重叠**（都在回答"这个品牌的政策是什么"），于是一句政策说明在**同一页**出现 3 次。这不属于跨页同质化，但稀释内容密度、伤阅读体验。组 B 全量页内重复 543 槽（roamic）、组 A 72 槽。

---

## 四、页面架构与结构化数据

| | SG/roamic | SG/airalo | JP/roamic | AT/roamic |
|:--|:--|:--|:--|:--|
| 区块（h2/h3 id） | 10 个 | 10 个 | 10 个 | 10 个 |
| 区块序列 | `verdict, plans, reality, fup, hostnetwork, tripcost, fit, tradeoffs, others, faq` —— **四页完全相同** |
| JSON-LD | BreadcrumbList / Organization / WebSite / Product / WebPage / FAQPage —— **四页完全相同** |
| `<title>` 模式 | `{Brand} {Country} eSIM Review 2026: Data Plans Compared` |
| `<h1>` 模式 | `{Brand} {Country} eSIM Plans & Prices (2026)` |

**架构同构度：100%。** 三组对比（同国跨品牌、同品牌跨国家、第三国同品牌）的区块序列逐字一致。

`title` / `description` / `h1` 都是**正确差异化**的 —— 均含品牌名 + 国家名 + 该页真实数据：

```
SG/roamic  desc: …compares Roamic eSIM plans for Singapore: 36 plans from $2.00, best $0.40/GB (#1 of 10)
SG/airalo  desc: …compares Airalo eSIM plans for Singapore: 18 plans from $4.00, best $0.96/GB (#5 of 10)
JP/roamic  desc: …compares Roamic eSIM plans for Japan: 36 plans from $2.00, best $0.66/GB (#2 of 10)
```

---

## 五、增量在哪 —— 有，但薄

### 5.1 真实存在的增量

| 增量来源 | 实测 | 是否页页唯一 |
|:--|:--|:--|
| 套餐表数据 | 各页 36–37 行 | **50/50 唯一**（含国家名、价格、$/GB 逐行不同） |
| `#hostnetwork` 文案 | 约 5–9 句 | 是（运营商名、速度、覆盖评价逐国不同） |
| `#others` 对手价格 | 数值 | 是 |
| `title` / `desc` / `h1` | — | 是 |
| 结构化数据 | — | 是（Product 带该国价格） |

### 5.2 增量薄在哪

- **文案只能提供页均 6 句（7.3%）独有内容**。
- **套餐表结构完全相同**：列结构一致，行数只有两种（37 行 × 41 国、36 行 × 9 国）—— 说明 roamic 的套餐清单是**全球统一档位**，各国只是价格不同。
- 加上 §四 的 100% 架构同构，**50 个页面在「文本 + 骨架」层面接近同一份模板填 50 组数值**。

---

## 六、★ 关键发现：一个 50 国全覆盖、却完全没被启用的资产

```
data/countries.toml
  → 50 个国家全部带 `quirks` 字段，合计 101 条逐国研究内容
  → 在 /compare/<country>/<brand>/ 产物里命中：0 条
```

实测抽样（前 6 国，共 13 条 quirks）：

| 国家 | quirks 条数 | 页面命中 |
|:--|--:|--:|
| JP 日本 | 3 | **0** |
| US 美国 | 2 | **0** |
| GB 英国 | 2 | **0** |
| FR 法国 | 2 | **0** |
| IT 意大利 | 2 | **0** |
| TH 泰国 | 2 | **0** |

`japan/roamic` 产物里连 `passport verification`（日本 quirk 原文片段）都搜不到，`quirk` 一词出现 0 次。

**这条资产的内容质量示例**（日本）：

> - Japanese law requires passport verification for local prepaid SIM cards (SoftBank, Docomo, KDDI) — travel eSIMs bypass this entirely.
> - SoftBank's own tourist SIM can only be activated 09:00-21:00 JST; travel eSIMs activate 24/7, which matters for late-night arrivals at Narita or Haneda.
> - Pocket WiFi rental is Japan's classic connectivity option. It wins for groups of 3 or more, but a solo traveler almost always pays less with an eSIM.

**这正是降同质化最有效的东西** —— 逐国独有、有信息量、非模板、且已经在仓库里躺着。启用它能让每页多出 2–3 条**其他 49 页都没有**的句子。

---

## 七、Google SEO 判定

### 7.1 判定依据

Google 对模板化页面的处理**不看字面重复率**，而看三件事：

1. **Doorway 判定**：是否为「同一意图的多变体、把用户导向同一目的地、本身价值低」
2. **独特价值**：该页能否独立满足其目标查询
3. **Minor variations**：页面之间是否只有措辞或地名的机械替换

### 7.2 逐条对照

| 判定项 | 组 A（同国跨品牌） | 组 B（同品牌跨国家） |
|:--|:--|:--|
| 是否 doorway | **否** —— 每页独立满足「X 品牌在 Y 国」的查询 | **否** —— 同上 |
| 是否有独特价值 | **有** —— 该品牌在该国的真实价格/排名/网络 | **有，但较薄** —— 该国真实价格 + 网络 |
| 是否 minor variations | 未触及 —— 差异来自**品牌档案不同** | **接近边界** —— 差异主要是地名与数值替换 |
| 数据真实性 | 真实、可核查（含核对日期） | 真实、可核查 |
| 目标关键词 | 各不相同且与内容匹配 | 各不相同且与内容匹配 |

### 7.3 结论

- **组 A（同国跨品牌，74%）：合规。** 10 页共享国家级事实是合理的（同一个国家，运营商与网络就是同一批），差异来自各品牌真实档案。**无需处理。**
- **组 B（同品牌跨国家，86%）：合规，但站在边界上。** 每页都有真实数据与独立查询意图，**不构成 doorway**；但 86% 槽位共享 + 100% 架构同构，让这 50 页在算法眼里「像同一份模板填了 50 组数值」。风险不是「被判罚」，而是**「只有少数几页被索引、其余因近似重复被稀释收录」**。

**风险量化**：以「页均独有文案 7.3%」为信号，50 页里真正有把握被独立收录的是数据差异大的国家页；长尾国家页的收录概率显著偏低。

---

## 八、建议（按性价比排序）

| 优先级 | 动作 | 预期效果 | 成本 |
|:--|:--|:--|:--|
| **P0** | **启用 `countries.toml` 的 101 条 quirks**，在品牌子页加一个「Local context」区块（每页 2–3 条） | 页均独有内容从 6 句 → 约 9–12 句；模板槽位占比预估降 5–9 个百分点 | 一个模板 + i18n，一次性，收益覆盖 499 页 |
| **P0'** | **单独立项处理 `vs` 对决页**（87% 是全站最高，页内重复 1890 槽） | 收益可能大于本次对象 | 中 |
| **P1** | **压缩品牌档案在每页的复述**（`#reality` / `#fup` / `#tradeoffs` 三块内容高度重叠） | 直接削减大块共享槽位 | 中，需重排区块职责 |
| **P1** | **修页内重复**：让 `#faq` 引用 `#fup` 的结论而非复述 | 每页去掉 3–5 条重复句；全站 provider_sub 页内重复 3953 槽 | 小 |
| **P2** | 给 `#hostnetwork` 增加更多国家专属维度（频谱、漫游协议、当地法规） | 抬高组 B 的核心差异块 | 大，需数据采集 |

**不建议做的**：改写共享句的**措辞**。那会命中 Google 明文的 *minor variations*，比现状更糟。

---

## 九、方法论与自检

### 9.1 口径

- 只取 prose 标签 `p / li / blockquote / figcaption`（`td` / `th` / `h2` / `h3` 不算，避免表格数据把重复率虚高）
- 按 `[.!?]` 切句，丢弃 < 25 字符碎片
- **两级归一化**：品牌名 **与国家名** → `@`；数字 → `#`
- 模板句门槛：出现在 ≥80% 页面（10 页组取 8，50 页组取 40）
- **模板槽位占比** = Σ(模板句在各页的出现次数) / Σ(各页句子数)
- **页内重复** = Σ(每页句子数 − 每页去重句子数)，独立于跨页指标

### 9.2 本轮修正的两处口径错误（重要）

**错误 ①：国家名完全没有归一化**

`scripts/audit_boilerplate.py` 的 `norm()` 原先只归一化「该页自己的品牌名」，**国家名一个字都不处理**。后果 —— 同品牌跨国家的分组里，`…in Japan` 与 `…in Croatia` 原文不同，被误判为「各页独立」。50 个国家页的共享率因此被压到 **54.5%**，而实际是 **86.8%**。

更隐蔽的是：即便手工临时补上国名，若白名单只硬编码少数几个国家，会造成**同组内各国口径不一致** —— 症状是 `austria/roamic` 独占 6 句、而 `netherlands/roamic` 独占 38 句，方向差荒谬。已改为从 `data/countries.toml` **全量读取**（100 项）。

**错误 ②：模板槽位的分子分母不对等**

旧实现：分母数的是**含页内重复**的句子总数，分子却把「出现在 N 页的某句」只记 N 次。于是同一句话在一页里出现 3 次时，分母 +3、分子只 +1 —— **系统性低估**。实测 roamic：旧口径 **73%**，自洽口径 **86%**，差 13 个点，全部来自 `#reality` / `#fup` / `#faq` 的页内复述。已改为自洽的「槽位视角」，并把页内重复单列。

**两处修正叠加后，结论方向翻转：**

| 指标 | 修正前 | 修正后 |
|:--|--:|--:|
| 组 B 模板槽位 | 54.5% | **86.4%** |
| 组 B 页均独占 | 34 句 | **6 句** |
| 组 B 两两重叠 | 53.8% | **86.6%** |

**此前 2026-10-07 那轮对 yesim 组的结论（「同品牌跨国家只有 48%、同国才是高风险面」）同源于错误 ①，现予更正：真实情况相反 —— 同品牌跨国家才是更同质的那一面。**（修正后 yesim = 88%，而各国组是 73–75%。）

### 9.3 自检记录

| 检查 | 结果 |
|:--|:--|
| 页对页两组数字相同 → 是否脚本 bug | 已查证：非 bug，由共用节点 `singapore/roamic` 造成，两组交集彼此重合 48 句 |
| 「零变量逐字」判据是否可信 | 已抽查 5 条，逐页打印原文，确认**真一字不差** |
| 句数对不上（83 vs 72） | 已查证：72 为 `set()` 去重后句数，83 为原始句数，同一事实两种记法 |
| 国名白名单是否一致 | **发现错误并修正**（§9.2 ①） |
| 模板槽位分子分母是否对等 | **发现错误并修正**（§9.2 ②） |
| 表格数据是否被 prose 口径漏掉 | 已用全文本口径交叉验证（92.1%），并单独统计套餐表（50/50 唯一） |
| **修复后的脚本 vs 独立复算对拍** | roamic **86.4% vs 86.8%**（差 0.4 点）；singapore 74% vs 75.8%（差 1.8 点，来自品牌名归一化范围） |

### 9.4 数据快照

- 构建产物：702 页（与 2026-10-07 基线一致）
- 审核页数：组 A 10 页 + 组 B 50 页 + 交叉验证 4 页 + 全站 7 页型
- 品牌数据：`data/plans/*.toml` 10 个品牌；roamic / airalo 各覆盖 50 国
- 复跑命令：

```bash
python -X utf8 scripts/audit_boilerplate.py --type provider_sub --group-by brand   # 同品牌跨国家
python -X utf8 scripts/audit_boilerplate.py --type provider_sub --group-by country # 同国跨品牌
python -X utf8 scripts/audit_boilerplate.py                                        # 全站页型总览
```
