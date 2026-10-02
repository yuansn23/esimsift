# 关键词 → URL 唯一映射表（Keyword → URL Map）

> 目的：每个关键词簇只有一个排名页（唯一 URL）。新增任何页型/区块前先查本表；
> 两个页面争同一个词 = 自我蚕食。规则源自竞品蓝图 §7.4，由 `scripts/validate.py` 执行静态检查。
> 维护约定：每次新增页面类型或修改页面定位时同步更新本表。

## 1. 主映射表（已上线页型）

| 关键词模式（EN） | 目标 URL | 页型 | 边界（该页**不得**争夺的词） |
|---|---|---|---|
| `best eSIM for {country}` / `cheapest eSIM {country}` / `{country} eSIM` / `{country} unlimited eSIM` / `how to install eSIM in {country}` / `{country} eSIM prices` | `/compare/{country}/` | 国家页 | 不得争全局 how-to（→guides）、不得争 `{A} vs {B}` 头词（→对决页） |
| `{A} {country} eSIM` / `{A} price in {country}` / `{A} plans for {country}` | `/compare/{country}/{A}/` | 品牌×国家子页 | 不得争 `{A} review`（→品牌页）、不得争无国家限定的品牌词 |
| `{A} review` / `is {A} good` / `{A} eSIM prices`（全局） / `how does {A} work` | `/esim-providers/{A}/` | 品牌页 | 品牌页 FAQ 里的 `{A} vs {B}: which is cheaper?` 只答品牌维度总结，头词让给对决页 |
| `{A} vs {B}` / `{B} vs {A}` / `which is better {A} or {B}`（全局） | `/compare/{a}-vs-{b}/`（slug 字母序，双向查询同页承接；layout vs-single） | VS 对决页 | 不得争 `{A} vs {B} for {country}`（→国家页/子页），逐国表格行只做导流 |
| `eSIM provider comparison` / `compare eSIM providers` / `eSIM matchups`（对决列表/导航词） | `/compare/matchups/`（layout matchups, nolist——枢纽索引页） | 对决枢纽页 | 只做导航+计算摘要（closest/lopsided），卡片文案不抢 `{A} vs {B}` 头词（→单对决页） |
| `{A} promo code` / `{A} discount code` / `eSIM deals` | `/esim-deals/` | 折扣码页 | 品牌页/国家页的 promo 模块是展示，canonical 归 deals 页 |
| `eSIM data calculator` / `how much data do I need for travel`（全局） | `/tools/` | 工具页 | 国家页内"how much data"分档卡只服务国家语境 |
| `eSIM price comparison` / `eSIM prices by country` / `cheapest countries for eSIM data` | `/research/esim-price-index/` | 研究页 | 不得争单国价格词（→国家页） |
| `best unlimited eSIM` / `unlimited data eSIM comparison`（全局） | `/research/unlimited-esim/` | 研究页 | `{country} unlimited eSIM` → 国家页 |
| `what is an eSIM` / `how does an eSIM work` | `/guides/what-is-an-esim/` | 指南 | — |
| `eSIM vs physical SIM` / `prepaid SIM vs eSIM` | `/guides/esim-vs-physical-sim/` | 指南 | 注意：这是**产品形态对比**，不得与 `{A} vs {B}`（品牌对比）混淆，两者词簇无交集 |
| `how to install an eSIM` / `how to activate an eSIM`（全局） | `/guides/how-to-install-an-esim/` | 指南 | `... in {country}` → 国家页安装区 |
| `dual SIM eSIM` / `can I use two eSIMs` | `/guides/dual-sim-and-esim/` | 指南 | — |
| `eSIM compatible phones` / `is my phone eSIM ready` | `/guides/esim-compatibility-check/` | 指南 | Phase 2 工具页上线后承接交互意图，指南保信息意图 |
| `eSIM Sift` / 品牌词 | `/` | 首页 | — |

## 2. 国家语境 vs 全局语境的判定规则

同一关键词带国家限定 → 国家页；不带 → 全局页。执行细节：

- 国家页 FAQ 的品牌对选题（"Is Airalo or Holafly better in Spain?"）与 VS 页**不冲突**：
  前者承接 `{A} vs {B} for {country}` 长尾，后者承接 `{A} vs {B}` 头词。VS 页逐国表
  格行链接国家页，不复制国家页结论。
- `unlimited`：全局 → 研究页榜单；国家 → 国家页（FAQ + 套餐表）。
- `promo code`：任何带国家/品牌限定的折扣码词都指向 `/esim-deals/`（单页全品牌）。

## 3. 预留映射（Phase 2，未上线不得提前内链）

| 关键词模式 | 预留 URL | 条件 |
|---|---|---|
| `best eSIM for Europe` / `{region} eSIM` | `/compare/{region}/` ×5 | 区域套餐数据落地后 |
| `{carrier} eSIM` / `which eSIM uses {carrier}` | `/networks/{carrier}/` | 网络名真实核对后 |
| `eSIM for {device}` / `{device} eSIM compatible` | `/devices/{device}/` | 机型库数据线立项后 |

## 4. 新页面检查清单（进 validate.py）

1. **唯一性**：新增页面前 grep 本表，目标词簇是否已有归属；有 → 改为给现有页加内链，不开新页。
2. **锚文本**：同目标 URL 的相同锚文本 ≤30%；完全匹配锚 ≤20%（模板 grep 统计）。
3. **slug 字母序**：VS 对决 slug 一律 `{a}-vs-{b}`（a<b 字母序），反向查询由同页 FAQ 承接，不建反向 URL。
4. **跨页相似度**：同模板页固定文案占比 ≤30%，其余由数据填充（VS 页 verdict/TL;DR/FAQ 全部含计算数字）。
5. **空壳门槛**：任何新区块子页 <3 时不在 header/footer/sitemap 中推广。
