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
| `how to install an eSIM` / `how to activate an eSIM`（全局） | `/guides/how-to-install-esim/` | 指南 | `... in {country}` → 国家页安装区。**slug 无 "an"**（2026-10-06 修：旧文写成 `how-to-install-an-esim`，那是个 404，会误导后续内链） |
| `dual SIM eSIM` / `can I use two eSIMs` | `/guides/dual-sim-and-esim/` | 指南 | — |
| `eSIM compatible phones` / `is my phone eSIM ready` / `does {device} support eSIM` / `{brand} eSIM compatible`（品牌/机型限定兼容查询一并归指南） | `/guides/esim-compatibility-check/` | 指南 | 2026-10-03 决策：设备库单开页与指南重复，已下线（数据与页面备份在仓库外）；机型级查询由指南承接，不再开 /devices/ |
| `eSIM Sift` / 品牌词 | `/` | 首页 | — |
| `best {region} eSIM` / `cheapest eSIM in {region}` / `{region} eSIM prices`（{region} ∈ Europe / Asia / Americas / Africa & Middle East / Oceania） | `/guides/best-{region}-esim/` ×5（layout region） | 区域指南页 | 不得争单国词（`{country} eSIM` → 国家页）、不得争全局 how-to（→guides 单篇）、不得争 `{A} vs {B}`（→对决页） |
| `what network does {A} use in {country}` / `which network does {A} use` / `eSIM network map` / `{country} eSIM which network`（品牌限定网络归属查询）；`which network cross borders` / `regional eSIM plan coverage`（跨国宿主集团）；`what is a host network` / `MVNO` / `multi-IMSI`（网络术语） | `/networks/`（layout networks-list，单页全目的地枢纽） | 网络归属页 | 不得争 `{A} review`/`{A} prices`（→品牌页）、不得争单国价格词（→国家页）、不得争 `{country} eSIM` 单国词（→国家页，本页只做枢纽+外链）；当前实测 9 品牌宿主网络逐国一致，故做单页而非 N 张重复表；页面结构=结论带+决策规则+跨国集团榜+区域分组目的地折叠行+术语表，加国家只增数据不改版式；若未来数据分歧需拆页时先改本表 |

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
| `{carrier} eSIM` / `which eSIM uses {carrier}`（{carrier} = 本地运营商名，如 Movistar） | `/networks/{carrier}/` ×N | 本地运营商↔品牌归属逐运营商核对后；注意与已上线的 `/networks/` 总表同 section，slug 不得冲突 |
| `{country} mobile networks` / `{country} carriers` / `which network does {country} esim use` / `does {carrier} support esim in {country}` | `/networks/{country-slug}/` ×50（**2026-10-03 起上线：已发布 12 国 = JP US DE CA FR MX TH ES KR CN GB NL，余 38 国加 content md 即可，不改版式**） | 承接「国家网络/运营商」意图；**不得争** `{country} eSIM` 价格词（→国家页 compare）、不得争 `{A} vs {B}`（→对决页）、不得争全局网络归属（→`/networks/` 枢纽）。版式 = 模板 `layouts/networks/single.html`（纯数据驱动，加国家只增 content md 不改版式）；每页必带 ①运营商画像卡 ②品牌→网络表（链品牌×国家页）③城市覆盖 ④Opensignal/Ookla 引用 ⑤FAQ(FAQPage)。内链（四条，全部 `site.GetPage` 门控，未建页不产生死链）：①页头 Network map 二级菜单「Carrier breakdowns」逐国列出（`partials/header.html`，有 0 个深度页时自动退回单链接）②枢纽 `/networks/` 目的地卡「Carrier breakdown →」③国家页 `/compare/{country}/` 「Networks」段内嵌回链 ④品牌×国家子页 `/compare/{country}/{brand}/` 「Which network does {A} ride in {C}」段（建满 50 国后 = 450 条入链） |

> 注：原预留的 `best eSIM for Europe / {region} eSIM → /compare/{region}/ ×5` 已上线，
> 实际落地为 `/guides/best-{region}-esim/`（layout region），见主映射表；`/compare/{region}/` 槽位废弃。
>
> **★ 品牌集是数据驱动的，本表的品牌侧一律写 `{A}` / `{B}` 占位，不枚举具体品牌** ——
> 2026-10-06 接入 Nomad（8 → 9 家）时本表**只需改"品牌数"这类描述性数字，映射关系零变更**：
> 新品牌的词簇（`{A} {country} eSIM` / `{A} review` / `{A} vs {B}`）自动落进已有的三类页型
> （品牌×国家子页 / 品牌页 / 对决页），无需新开页型、无需新占关键词。**接入新品牌前只需确认这一点**，
> 别为本表新增行。

### 3.1 `/networks/{country}/` 标题纪律（防与 `/compare/{country}/` 蚕食，2026-10-03 定）

两类页共享「{country} eSIM」这一主干词，靠**修饰语**区分意图，标题层不得重叠：

| 页型 | 承接意图 | `<title>` 写法 | 禁用词 |
|:---|:---|:---|:---|
| `/networks/{country}/` | 「这个国家的网络/运营商是谁、谁强」 | `{Country} eSIM Networks {Year}: {运营商A} {运营商B} and {运营商C}`（H1 另写 `{Country} eSIM Carriers: ... Explained`） | **禁用 `Best`、禁用 `From $x/GB`、禁用 `Cheap`** —— 这些是价格页的钩子 |
| `/compare/{country}/` | 「买哪个最便宜/多少流量」 | `Best {Country} eSIM {Year}: {价格钩子} From ${x}/GB` | 不用 `Carriers` / `Networks` 做主干 |

> 起因：初审发现 France / Netherlands / Spain 三页 networks 标题写成 `Best 5G Networks for Tourists`，与 compare 的 `Best {C} eSIM 2026: ...` 共享 `Best` + `5G` 两个高权重词，构成局部蚕食。已全部改写为纯网络意图标题。新增国家照此表执行。

## 4. 新页面检查清单（进 validate.py）

1. **唯一性**：新增页面前 grep 本表，目标词簇是否已有归属；有 → 改为给现有页加内链，不开新页。
2. **锚文本**：同目标 URL 的相同锚文本 ≤30%；完全匹配锚 ≤20%（模板 grep 统计）。
3. **slug 字母序**：VS 对决 slug 一律 `{a}-vs-{b}`（a<b 字母序），反向查询由同页 FAQ 承接，不建反向 URL。
4. **跨页相似度**：同模板页固定文案占比 ≤30%，其余由数据填充（VS 页 verdict/TL;DR/FAQ 全部含计算数字）。
5. **空壳门槛**：任何新区块子页 <3 时不在 header/footer/sitemap 中推广。
