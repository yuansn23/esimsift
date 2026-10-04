# 品牌×国家子页（`/compare/<country>/<provider>/`）优化规范

> **这份文档解决什么**：全站数量最大、模板最复杂、也最容易被「数据变了但模板没跟上」
> 伤到的一层页面 —— 怎么系统性地把它从「价格表 + 横幅」改成「能回答真实决策问题的页面」，
> 以及改完之后**怎么证明没改坏**。
>
> 沉淀自 2026-10-04 对 `/compare/netherlands/holafly/` 的改造，方法一次性覆盖全站 400 页。
> 配套守卫：`scripts/verify_provider_pages.py`（本章 §5）。

---

## 0. 适用范围与先决条件

| 项 | 值 |
|:---|:---|
| 页面数 | **400** = 50 国 × 8 品牌（`airalo / alosim / holafly / roami / roamic / saily / ubigi / yesim`） |
| 内容文件 | `content/en/compare/<country>/<provider>.md` —— **正文为空**，只有 `iso` / `provider` / `layout: provider` / `seo.description` |
| 渲染模板 | `layouts/compare/provider.html` |
| 标题分支 | `layouts/partials/head.html` 的 `{{ if .Params.provider }}` |
| 数据源 | `data/plans/<brand>.toml` → `partials/country-stats.html` → 模板 |
| i18n 前缀 | 本层新文案一律 `compare_provider__*` |

⚠️ **动手前必须接受的前提**：改 `provider.html` 一处 = 改 400 页。所以**任何改动都要先问
「50 国 × 8 品牌全都成立吗」**，不能只看着荷兰 Holafly 那一个页面满意就收工。
本层的所有分支都必须由数据推导（`if $unlimitedOnly` / `with $pol` / `if $netNames`），
禁止写「假设这家是无尽流量」「假设这个国家有 3 家运营商」这类硬前提。

---

## 1. 诊断：改之前这层页面缺什么

| # | 问题 | 现状 | 目标 |
|:--|:---|:---|:---|
| 1 | **标题标签过长** | `Holafly Netherlands eSIM Unlimited Plans From $11.90`（81 字符，Google 约 60 就截断），且把**套餐数量**与**价格**写进标题 | 48–54 字符，含品牌词 + 核心关键词 + 年份 + 意图词；**不放价格、不放套餐数量**（§3.1） |
| 2 | **H1 与 title 语义重复** | 两者都在喊价格 | H1 承担「Plans & Prices」的事实层，title 承担「Unlimited Data Plans」的意图层 |
| 3 | **结构化数据只有一个区间** | 只有 `Product` + `AggregateOffer`（`lowPrice`/`highPrice`），模型无法把价格和具体档位对应 | 逐套餐 `Offer` 数组 + `WebPage` + `FAQPage` + 4 级 `BreadcrumbList`（§3.5） |
| 4 | **只回答「多少钱」** | 没有回答「值不值」「会不会踩坑」 | 新增 Plan reality check（热点/FUP/5G/充值四张卡）、Buy-it-if / Look-elsewhere-if、数据驱动 FAQ |
| 5 | **无竞品对比锚点** | 页面是品牌宣传页的延长线 | 逐竞品卡片，差异点由数据算（贵/便宜多少美元），并内链到该竞品的同层页 |
| 6 | **无网络覆盖信息** | 读者不知道这张 eSIM 走谁的网 | 宿主运营商卡（技术制式 + 实测速度区间）+ 内链 `/networks/<country>/` |
| 7 | **价格无时效** | 一个价格，没有核对日 | 脚注带 `checkedDate` + methodology 外链 |
| 8 | **表格不可排序** | 只能按 $/GB 固定顺序看 | 原生 JS 按 `$/GB / 价格 / $/天 / 数据量 / 有效期` 排序 |
| 9 | **没有「我的行程」入口** | 只有固定档位表 | 页内行程计算器：输入天数，自动挑「有效期覆盖整趟行程」的最便宜套餐并与最便宜竞品比价（§3.7） |

---

## 2. 数据通路：改这一层必须动哪些文件

```
data/plans/<brand>.toml[ISO].plans[]        # 套餐（gb / days / type / price / fup）
        ↓
layouts/partials/country-stats.html         # 单一聚合入口，返回 rows/providers/minPrice/
        ↓                                   #   minPerGB/has5g/planCount/checkedDate
layouts/compare/provider.html               # 本层模板（全部数字由此推导）
        ↑
data/providers.toml[<brand>].policy         # ★ 本轮新增：价格表答不了的事实
data/carriers.toml[ISO].profiles            # 宿主运营商画像（tech / speed_min / speed_top / note）
data/countries.toml[ISO].carriers           # 该国运营商名单（与 plans 的 networks 恒等）
i18n/en.toml + i18n/de.toml                 # compare_provider__* （必须逐 key 对齐）
```

`country-stats.html` 每行（row）含：
`key provider networks name gb days type price perDay perGB fup isUnlimited`

**铁律**：模板里**不出现任何手写数字**。排名、最低价、$GB、行程总价、竞品差价全部由
`$rows` 现算 —— 这也是为什么这一层能一次改完覆盖 400 页而不需要逐页校对。

---

## 3. 关键设计决策（附理由，别只抄写法）

### 3.1 标题阶梯 —— 为什么不能放价格和套餐数量

用户 2026-10-04 的硬要求：**「标题不要提现多个套餐，也不要体现出价格」**。三条理由：

1. 价格与套餐数**每次抓数据都会变**，写进标题意味着 400 个标题持续过期；
2. 价格锚点已经由 `description` 承担（`6 daily plans from $2.46/day`），标题再放一次是重复；
3. `Unlimited Plans From $11.90` 这类串在 SERP 里被截断后，剩下的部分恰好**丢掉意图词**。

实现（`layouts/partials/head.html`）：候选串**从长到短**排列，取第一个 ≤54 的；都超长就取最后一个。
两套阶梯按「这家在这国有没有计量套餐」分叉：

```html
{{- if eq (len $met) 0 -}}          {{/* 只卖无限流量 */}}
  {{- $cands = slice
    (printf "%s %s eSIM Review %d: Unlimited Data Plans" $p.name $c.name $y)
    (printf "%s %s eSIM %d: Unlimited Data Plans" $p.name $c.name $y)
    (printf "%s %s eSIM %d: Unlimited Plans Compared" $p.name $c.name $y)
    … 6 档递降 … -}}
{{- else -}}                        {{/* 有计量套餐 */}}
  {{- $cands = slice
    (printf "%s %s eSIM Review %d: Data Plans Compared" $p.name $c.name $y)
    (printf "%s %s eSIM %d: Cheap Data Plans Compared" $p.name $c.name $y)
    … 6 档递降 … -}}
{{- end -}}
```

**实测结果**：800 组（50 国 × 8 品牌 × 2 种形态）**全部能取到 ≤54 字符**的候选串，
产物落点 `48–54`、均值 `51.1`、最短 48、最长 54。

H1 与 title 的分工：H1 = `{Brand} {Country} eSIM Plans & Prices (2026)`（事实层，含年份），
title = `{Brand} {Country} eSIM 2026: Data Plans Compared`（意图层）。

### 3.2 `[<brand>.policy]`：单抽一张表，回答价格表答不了的三件事

价格表能回答「多少钱 / 多少 GB / 多少天」，回答不了用户真正踩坑的三件事：
**热点能不能开、满速能跑多少 GB、用完了能不能续充**。

所以新增 `data/providers.toml[<brand>.policy]`：

```toml
[holafly.policy]
hotspot = "capped"                      # capped / allowed / none
hotspot_allowance = "500 MB/day"
hotspot_note = "Holafly's own technical specs cap tethering at 500 MB/day…"
fup_allowance = "No GB figure published"
fup_drop = "256 Kbps - 1 Mbps"
fup_note = "Holafly publishes no daily GB threshold…"
topup = false
topup_note = "Holafly has no top-ups…"
voice = "data-only"                     # 用于判定「没有本地号码」这一步
```

落点：`#reality` 四张卡 + `#fit` 的 Look-elsewhere-if + FAQ 的第 2/3 题。

### 3.3 「宁缺勿造」：没核实就写 Not checked yet

`policy` 表**只填核实过的品牌**（本轮 6 个：airalo / alosim / holafly / saily / ubigi / yesim；
`roami` / `roamic` 故意留空）。模板侧一律：

```html
{{ with $pol }} … 渲染核实过的事实 … {{ else }}
<p class="… text-ink-400">{{ i18n "compare_provider__status_unverified" }}</p>
{{ end }}
```

产物表现：**100 页**（2 个品牌 × 50 国）显示「尚未核实」。
`verify_provider_pages.py` 把这个数字当作**断言**打印出来 —— 它一旦不再是 100，
就说明要么漏填要么错填。

同一条纪律也适用于 `#fit` 的「没有本地号码」条目：判据是 **`policy.voice`**，
**不是**品牌类型。用品牌类型（`$p.type`）推断 = 替所有品牌做了它没做的承诺。

### 3.4 无限流量品牌不参与 `$/GB` 排名

旧逻辑里，只卖无限套餐的品牌（本层 = Holafly）没有 `$/GB`，被当成 `999999` 排到末位，
Hero 上显示成 **`#8 of 8 on $/GB`** —— 既错误又难看。修法：

```html
{{ $unlimitedOnly := and (gt (len $myUnlimited) 0) (eq (len $myMetered) 0) }}
{{ $rankable := not $unlimitedOnly }}
…
{{ if $rankable }}<div class="stat-tile">#{{ $rank }} of {{ $stats.providerCount }} …</div>
{{ else if lt $myBestPerDay 999999.0 }}<div class="stat-tile">${{ printf "%.2f" $myBestPerDay }} best $/day</div>{{ end }}
```

**通用判据**：一个指标对某行数据**不存在**时，页面必须**换一个成立的指标**，而不是显示一个错的。

### 3.5 结构化数据栈：四块，缺一不可

| 块 | 关键点 |
|:---|:---|
| `Product` | **必须带 `image`**（3 张绝对 URL）—— Google 的 Product 富摘要要求 `image`，缺了它 `offers` 再全也不出富摘要。同时带 `url` |
| `AggregateOffer` + **逐套餐 `Offer` 数组** | `lowPrice` / `highPrice` / **每个 `Offer.price` 必须是 JSON 数字**，写成字符串会被 `check_output.py` 拦下 |
| `WebPage` | `inLanguage` + `dateModified`（= **构建当天的系统日期**，见 §3.13）+ `isPartOf` WebSite |
| `FAQPage` | ≥3 组，问答由本页已核验数字拼出；**答案里先算好变量再进 dict**（`dict` 参数位里写 `with/else` 是无效语法） |
| `BreadcrumbList` | **4 级**，中级 `href` 必须与真实路径一致（`.Ancestors` 不含作为普通页的国家层，必须手写） |

一致性断言（`verify_provider_pages.py`）：**逐套餐 `Offer` 条数 == 价格表 `<tr data-price=` 行数**。
这条能同时抓住「JSON-LD 漏了某档」和「表格 `range` 绑定写错导致整块不输出」。

### 3.6 竞品对比：必须排除自己

按时长比价表的右列最初写的是「该国最便宜的计量套餐」，在 Airalo 页上会变成
**Airalo 自己跟自己比**。修法：右列加 `ne .key $provKey`，并把整节文案中性化
（`{Brand} cheapest` vs `Cheapest rival in {Country}`）。

**通用判据**：任何「对比」区块，先问一句「如果这就是那一方自己的页面，还成立吗」。

### 3.7 数据量标签必须走 partial —— `0` 表示「无限」的坑

`plans[].gb` 用 **`0` 表示无限**，而小于 1GB 的计量档存的是**小数**（500MB → `0.4883`）。
于是任何 `int .gb` 的写法都会把 500MB 的试用装截断成 `0`，页面随即把它标成 **"unlimited"** ——
与事实相反，而且正好落在读者最容易当真的一栏。

统一出口 `layouts/partials/plan-data-label.html`（被套餐表 / 行程对比表 / 计算器数据岛三处共用）：

```
gb == 0   → "unlimited"（走 i18n，德语可译）
gb < 1    → "500MB"（×1024 取整）
gb >= 1   → "5GB"
```

⚠️ partial 必须 **`{{ $gb := float . }}`** 起手：`gb` 在数据里**有的是 int（5 / 20）有的是 float
（0.4883）**，Go 的 `%g` 只接受 float，直接喂 int 会渲染出 `%!g(int=20)GB` 并在页面上可见。
第一版就是这么炸的，被 `check_output.py` 在构建期拦下（详见 §7 第 10 条）。

同源的两个衍生坑（一起修掉）：
- 排序脚本里 `parseInt(dataset.gb, 10) === 0` → 500MB 被归进「无限」组排到最末 → 改 `parseFloat(...) === 0`。
- 行程对比表的两列数据量文案原本也在 `int` 后判 `> 0` → 同一处错 → 改走 partial。

**通用判据**：凡是「某个取值表示特殊含义」的字段（`0 = 无限`、`-1 = 未知`），
**必须在读取点走一个具名转换函数**，不能靠调用方记得它。

### 3.8 页内行程计算器：口径要与表格完全一致

固定档位（3/5/7/10/15/30 天）覆盖不了所有人的行程。计算器让读者**按天数选择**
（3/5/7/10/14/21/30，与套餐表的筛选器共用同一组值），口径**与上方表格逐字相同**：
只算「有效期覆盖整趟行程」的套餐。

- 数据岛只装**按 `(品牌, 有效期)` 去重后的最便宜档**（荷兰实测 93 条），页面体积可控；
  去重按 `price` 升序先行，保证留下的是同档最便宜的那个。
- **口径必须写进脚注**：只认有效期、不认数据量；每个选项旁边显示数据量，
  让「500MB 试用装为什么比 5GB 便宜」这件事自证，而不是让读者以为被推荐了假价。
- 文案不写进 JS：JS 里只出现小写 id 与数字，需要显示的词（`days` / `unlimited` / `MB`）
  由服务端渲染成隐藏 span 或预先拼进数据岛的 `d` 字段 —— `check_i18n.py` 会扫内联脚本里的
  大写英文串，而且 JS 上下文根本不能用 `i18n`。

### 3.9 每一行数据都要能点回去 —— 外部佐证链接

这一层列的是「该国由哪些本地运营商承载、典型速度区间、覆盖强弱」。**列出判断却不给核实入口，
等于要读者信仰。** 所以每张运营商卡带一条外链，区块尾部带一条第三方来源。

两层来源含义不同，不能互相替代：

| 层 | 来源 | 回答什么 | 存在哪 |
|:--|:---|:---|:---|
| 一手 | 运营商官网 / 覆盖地图 | 「这是它自己说的」 | `data/refs.toml` `[carriers.<ISO>]` |
| 第三方 | Ookla Speedtest Global Index 该国页 | 「独立测量怎么排」 | `data/networkreports.toml` 的 `ookla_slug` |

**Ookla 的 slug 例外表只允许有一份。** `macao` 与 `turkiye` 都返回 404，正确写法是
`macau-(sar)` 与 `t%C3%BCrkiye`；国家 Hub 早就在 `networkreports.toml` 记着这份例外，
所以品牌页**不能**再写一遍 —— 同一事实写三处，就是三处都会错。品牌页直接复用同一套规则
（模板里 `index $d.networkreports $iso` → `.ookla_slug`，与 `compare/single.html` 逐字相同）。

**验证纪律**（`scripts/verify_external_refs.py`，`--data-only` 可离线只跑一致性）：

- `2xx` → ok；
- `403 / 412 / 429` → **bot 墙**。`att.com`、`t-mobile.com`、`bell.ca` 对脚本全部返回 403，
  但站点明明存在。把 403 判成失败会删掉正确的链接 —— 这是最坏的一种「正确」。
- `404 / 410` → 真死链，**只有这一类让脚本非 0 退出**。
- `000 / 5xx` → **本机不可达 ≠ 坏链**。`jio.com` 在这台机器上返回 000，浏览器里完全正常。
  这类只报告、不自动删。

实测这条纪律的价值：本轮 197 条里 49 条非 2xx，其中只有 **3 条是真问题**
（`noa.is` 域名拼错、`digicelfiji.com` 已 404、`yoigo.com` 品牌站已关闭），
其余 46 条是本机网络与机器人墙的噪音。**没有分层判定，你会删掉 46 个正确的链接，
同时把唯一拼错的域名留在页面上。**

数据层与源数据的一致性由 `check_alignment()` 保证：`refs.toml` 的每个 key 必须在
`carriers.toml` 有同名 profile（孤儿 = 永远不会渲染的死重量），每个 profile 没配到链接时
会被点名列出（漏引用要吵，不要静）。

### 3.10 交互控件：能「点一次」就不要「展开再点」

行程天数出现过三代控件，方向一直是缩短读者到答案的路径：

1. **五维排序器**（$/GB / 价格 / 每天 / 数据量 / 有效期）→ 读者的问题是「我要去 N 天，
   哪个能覆盖」，不是「按 $/GB 排一下」。
2. **数字输入框**（`<input type="number" min="1" max="60">`）→ 要求读者知道该填什么，
   移动端还要唤起键盘。
3. **下拉框** → 已经比前两代好，但仍要「展开 → 扫一遍 → 点」三步。

**现在是按钮组**（`.chip`，与区域过滤同一套样式）：天数摆出来，点一下就筛。
两处控件（套餐表 `#plan-days-group`、页内计算器 `#tc-days-group`）都是按钮。

四条硬规则：

1. **按钮的取值由数据推导，不许写死。** 曾经写死 `3 5 7 10 14 21 30`，而 Holafly 日本
   实际卖 `3/5/7/10/15/30` —— 读者点「14 天」发现下面没有对应档位，会以为页面漏了套餐，
   连带 H2 上那个「All 6 plans」也没法自己核对。现在由 `$myRows` 的 `days` 去重排序得到。
2. **档位太多的品牌要收敛，但不能造假档位。** Roamic / Yesim 按天卖 1–30 天，直接铺就是
   30 个按钮。做法：对阶梯 `1 2 3 4 5 7 10 14 21 30 60 90` 里的每个常用行程长度，
   取**真实档位里最小的 ≥ 它的那个**。于是按钮永远是真能买到的有效期（Roamic 日本 → 10 个），
   而且不会出现买不到的假取值。守卫第 13 项专查这个（按钮 ⊆ 表里的档位）。
3. **两处控件必须是同一组值**（模板里一个 `$dayOpts`）。否则同一趟行程会在同一页给出两个答案。
   国家 Hub（`compare/single.html`）另有自己的 `$dayOpts`，因为那里问的是「你的行程多长」
   而不是「这个品牌卖哪几档」—— 两个问题本来就该有两组值，但**同一页型内必须唯一**。
4. **计数文案不要用 JS 拼。** 服务端把整句渲染进隐藏 span（占位词用 `SHOWNCOUNT` 这种
   纯字母数字），JS 只做三个词替换。JS 里拼句子等于把译者的语序假设写死在代码里。

两个 JS 细节：

- **按容器取按钮，不要全局 `querySelectorAll('[data-days]')`。** 同一页有两组天数按钮
  （套餐表 + 计算器），全局选择器会把两组混在一起。
- `dataset` 键名**全小写**：`data-pergb` → `dataset.pergb`。写成 `dataset.perGB` 会静默取到
  `undefined`，比较函数返回 NaN，「看起来没坏」（因为服务端顺序恰好正确）。国家 Hub 的排序器
  踩过 —— 顺带修掉，别让它带着 bug 退休。

### 3.11 页面上的每个数字都要能自己核对 —— 「All 6 plans」那个 6 是怎么来的

读者质疑过：「为什么是 6 个计划？」。审计结论是**数字没错**（400 页逐页比对：
H2 的数量 = 价格表行数 = `data/plans/*.toml` 的档位数，零不一致），错的是**没说清口径**：

- 那个 6 不是「某个天数下的套餐数」，而是**这个品牌在这个国家在售的全部价格档**。
  无限流量品牌一档就是一个有效期（Holafly 日本 3/5/7/10/15/30 → 6 档）；
  计量品牌一档是「容量 × 有效期」组合（Airalo 日本 17 档）。两种都已经是「加起来的总数」。
- 读者之所以怀疑，是因为下面那排天数按钮当时是**写死的通用列表**，和 6 对不上（见 §3.10）。

所以两件事一起做：

1. H2 下面加一行**口径说明**：`{N} plans · {M} trip lengths · {a} to {b} days`。
   把 N 的来历写出来，读者能自己核对。
2. 守卫加第 12 项：N 必须同时等于 **价格表行数**、**JSON-LD 的 `offerCount`**、
   **说明行里的 N**。三处一起对账，任何一处漂移都会红。

> 另有两条口径要记住：Holafly 官网是「Select number of days」（按天自由选），
> 我们只抓到 6 个**公开价点**，所以 H2 说的是「我们追踪到的在售档位」而不是「它理论上能卖的所有天数」。
> 要写后者就得先有逐日价表，不能靠插值编 —— 宁缺勿造（§3.3）。

### 3.12 说「A 比 B 便宜」之前，先证明 A 和 B 是同一种东西

`#tradeoffs`（Where X wins and loses）从「印 `providers.toml` 的品牌套话」改成
**本页数据推导的国别量化对比**之后，最大的风险不是没话说，而是**说错话**。
反复踩到的都是同一个坑：**比较双方不是同类**。三条硬规则：

| 规则 | 反例（实测） | 正确做法 |
|:---|:---|:---|
| **计量比计量：对手流量 ≥ 我方流量** | Roamic 日本 30 天档 10GB/$9 被拿去跟 Ubigi 的 1GB/$4 比，印出「便宜 $5.00」——10 倍流量差被写成纯粹的价格劣势 | 对手筛选加 `or (eq .gb 0.0) (ge .gb $t.mine.gb)`（对手的无限档也算「流量不少于我」） |
| **无限比无限：行程长度精确匹配** | Ubigi 日本只有 8 / 30 天两档无限。10 天行程被迫买 30 天档 $45，跟 Roamic 的 10 天档 $23 比得出失真的 $22 | 我方筛选用 `eq (int .days) $l`（不是 `ge`）。跳档造成的价差**归专门的「档位错配」条目讲**，不混进价差 |
| **一个句子里的事实必须来自同一次选优** | `l_unl` 用 `$cUnlPerDay`（全国最低无限日单价 $1.50）+ `$rivalKey`（**最低入门价**品牌 Roami）拼句，数字属于 Ubigi 却署名 Roami（Roami 自家 $2.40） | 同一遍循环里同时记下价和主人（`$lkUnlRival`），署名一律 `index $d.providers <那个 key>` |

**推论 —— 「没有 X」类断言必须查 X 的存在性**：
`l_upsell` 第一版说 Roamic「15 天没有匹配档位」，判据却是「最便宜**可覆盖**档的 days」
（15 天最便宜是 5GB/21 天档 → 算出 21 ≠ 15）。而 Roamic 明明有 1–30 天全档位。
改成 `uniq` 一份 `$myTierDays` 后 `in` 判断，只在该长度**确实不存在**档位时才说。

**另外一条对称性约定**：同一件事在两边都要有位置，不能只挑对自己有利的那半边。热点共享
就是例子 —— 允许共享是优势（`tradeoffs_w_hotspot`），被限速才是缺点（`tradeoffs_l_hotspot`），
两者都用核实过的 `policy.hotspot*` 判据；无限流量的限速档同理（明写阈值 / 明说不公布 / 只写
「按套餐公布」三种，**第三种不列为缺点**，那是透明度加分项）。

---

### 3.13 「最后更新日期」只有一个来源 —— 品牌级数据核对日 `checked`

`esim-comparison.html` §9.4 把这条写成硬要求：**「最后更新日期：每页可见，且与 `dateModified` 一致」**。
它同时是一条 E-E-A-T 信号（§1305 的信任层清单也列了同一句），所以不能只改一处。

本层页面上有 **6 个**日期落点，全部同源：

| # | 位置 | 文案 key |
|:--|:---|:---|
| 1 | Hero 徽章 | `g_prices_checked` |
| 2 | Hero 价格免责声明（「as checked on …」） | `compare_provider__price_disclaimer` |
| 3 | Hero 配图 figcaption | `compare_provider__hero_caption` |
| 4 | 套餐表脚注 | `compare_provider__last_checked` |
| 5 | 页尾信任栏 | `compare_provider__prices_verified` |
| 6 | `WebPage` JSON-LD 的 `dateModified` | — |

**来源**：`layouts/partials/provider-checked.html`，读 `data/plans/<key>.toml` 的
`[<ISO>].checked`（品牌 × 国家粒度）：

```go
{{ $checkedISO := partial "provider-checked.html" (dict "key" $provKey "iso" $iso) }}
{{ $updatedDate := "" }}
{{ with $checkedISO }}{{ $updatedDate = time.Format ":date_medium" (time .) }}{{ end }}
```

#### 3.13.1 曾经写错的一次：用 `now`（构建当天），已撤回

第一版（2026-10-04 上午）把 6 个落点接到 `now`，理由是「本层要的是**内容**最后更新时间，
与**价格核对时间**是两个概念」。这个理由站不住，而且实测炸了：

| 页面 | 页面可见 | JSON-LD `dateModified` | sitemap `<lastmod>` |
|:---|:---|:---|:---|
| `/esim-providers/alosim/` | Oct 4 | （当时没有） | 2026-09-30 |
| `/compare/united-states/alosim/` | Oct 4 | 2026-10-04 | 2026-09-30 |
| `/compare/poland/` | Sep 30 | — | 2026-09-30 |

三处矛盾的两个理由，任一条都足以否掉 `now`：

1. **文案本身就在说「价格」**。6 个落点里 5 个的英文是
   `Prices checked …` / `Prices verified …` / `prices as checked on …`。
   在 09-30 抓的价格旁边写「Prices verified Oct 4」不是口径差异，是**不实陈述**。
2. **`lastmod` 只有准确才有价值**。Google 官方立场：`lastmod` 是抓取调度提示，
   长期不准会被**整体忽略**。每次部署都翻新 539 个 URL 的 `lastmod`，
   等于亲手把这个信号废掉。

#### 3.13.2 为什么上一版否掉的方案，这一版成立

上一版否掉 `checkedDate` 的两条理由都对，但都只针对**国家粒度**的 `country-stats`：

- `country-stats.checkedDate` 取的是「该国 8 个品牌里最近的一天」，被 15 处页型共用；
- 品牌页要的是**这一个品牌**的日期。

真正的缺口是：当时手上只有「构建日」和「国家级 `checked`」两个选项，
**没有人把 `checked` 按品牌取出来**。`provider-checked.html` 补的就是这一格，
它不动 `country-stats`，因此不动国家 Hub / guides / networks / research 任何一页。

三种口径，与各页型的可见日期一一对齐：

| 入参 | 取法 | 用在哪 |
|:---|:---|:---|
| `key` + `iso` | 该品牌在该国的价格核对日 | 品牌×国家子页 `/compare/<国>/<品牌>/` |
| `key` | 该品牌全部市场的最新价格核对日 | 品牌 Hub **价格类文案** |
| `key` + `profile` | 上面那个 与 该品牌档案核对日取最大 | 品牌 Hub 的「Last updated」/ `dateModified` / sitemap |
| `keys` | 这几个品牌全部市场的最新价格核对日 | A-vs-B 对比页 `/compare/<a>-vs-<b>/` |

`keys` 这条是实测逼出来的：vs 页的可见日期来自 `vs-agg.checkedDate`
（= 两个品牌的最大 `checked`），若 sitemap 退回「全站最新快照」兜底，
**只要任意一个不相干的品牌刷新数据，28 张 vs 页的 `lastmod` 就会集体前移**
而页面文案纹丝不动 —— 盖章演练时就是这么炸的。两边必须用同一个聚合口径。

#### 3.13.2b ★ 品牌 Hub 为什么要有**两个**日期

品牌 Hub 的内容来自**两份**数据：

- 价格 → `data/plans/<key>.toml` 的 `[<ISO>].checked`
- 品牌档案 → `data/providers.toml` 的 `strengths` / `weaknesses` / `info` / `policy` / `promo_*`

只改档案（例如把热点上限从「不限」改成 500 MB/天）时，页面确实变了，日期必须动；
但页面上的价格类文案写的是 `Prices … as checked on <d>`，**只描述价格**。

于是：

| 文案 | 日期来源 |
|:---|:---|
| `esim_providers_single__last_updated` =「Last updated <d>」（通用） | `max(价格, 档案)` |
| `compare_provider__price_disclaimer` =「list prices as checked on <d>」 | **只取价格** |
| `esim_providers_single__reading_data_note` =「price database … rebuilt <d>」 | **只取价格** |

**合成一个日期就会写出不实陈述** —— 档案今天改的、价格是上周核的，
印成「prices as checked on 今天」就是撒谎。这正是本轮要修的那类毛病，别在原地再犯一次。

`data/providers.toml` 每个品牌顶层块有 `profile_checked`（本轮补，八个品牌统一 `2026-10-04`，
依据见文件内注释：policy 块与 trustpilot 链接均为 2026-10-04 核实）。
改档案就手改这一个字段 —— 比 `plans` 的 `checked` 简单，不需要脚本。

**子页为什么不带档案日期**：`compare/provider.html` 的 6 个日期落点（Hero 徽章 /
价格免责 / figcaption / 套餐表脚注 / 页尾信任栏 / `dateModified`）文案**全是价格专属表述**，
所以 6 处一律只取「该品牌在该国的价格核对日」。

#### 3.13.3 数据更新后怎么让日期前移

```bash
python scripts/bump_checked.py --show                          # 看各品牌当前数据日期
python scripts/bump_checked.py --brand alosim                  # 今天核了 alosim 全部 50 国
python scripts/bump_checked.py --brand alosim --countries US,PL # 只核了美、波两国
npm run build
```

`checked` 一改，页面可见日期 / `dateModified` / sitemap `lastmod` 三处**同时**前移。

#### 3.13.4 代价（必须知道）

- 产物不再带构建日戳：**同一天构建与跨天构建，只要 `checked` 没变，产物逐字节一致** ——
  这比上一版更好，跨天构建不再造成 400 页全量变更，`regression-manifest.json` 也不会天天过期。
- 页面日期会「看起来不动」，直到真的核过价 —— 这是设计目标，不是 bug。
- 日期缺失时 `dateModified` **不写**该字段（宁可少一个字段，不写一个编的日期）。

**接线时的坑**：`dateModified` 原来包在 `{{ with $stats.checked }} … {{ end }}` 里
（用「有没有核对日」当渲染开关）。第一版改成常量日期后这个守卫恒真，必须**把 `with` 连同
`{{ end }}` 一起去掉**，否则留下一个永不触发的假分支 —— 与 §7 里 `l_fup` 那条
「判据永远为假」是同一类静默失败。本版又把它改回**真守卫**（`{{ with $checkedISO }}`），
但这次守卫的判据是「这个品牌这个国家有没有数据」，不是恒真。

---

## 4. 改造后的区块清单（模板从上到下的顺序）

| 顺序 | 区块 | `id` | 作用 |
|:--|:---|:---|:---|
| 1 | 面包屑（手写 4 级） | — | 层级 + BreadcrumbList 对齐 |
| 2 | Hero（旗 + 区域 + **最后更新日** + logo + H1 + 统计瓷砖） | — | 首屏事实 |
| 3 | Product / WebPage JSON-LD | — | 富摘要 + AI 引用凭证 |
| 4 | 折扣码模块（`with $p.promo_code`） | — | 转化 |
| 5 | 计算结论 | `#verdict` | 一句话答「这家在这国值不值」 |
| 6 | 套餐表（**按行程天数筛，天数按钮组由真实档位推导**） | `#plans` | 全部档位 + 口径说明行 + 价格脚注（含最后更新日） |
| 7 | **Plan reality check**（热点 / 5G 与速度 / FUP 阈值 / 充值） | `#reality` | 标签之外的四件事 |
| 8 | FUP 明细表（**只在真卖无限套餐时渲染**） | `#fup` | 无限档的公平使用政策 |
| 9 | 宿主网络（运营商卡 **+ 官方站点外链** + `/networks/` 内链 + **第三方测速来源**） | `#hostnetwork` | 覆盖与速度来自谁、凭什么 |
| 10 | 按时长比价（3/5/7/10/15/30 天）+ **页内计算器（天数按钮组，与 6 同一组取值）** | `#tripcost` | 「我的行程花多少」 |
| 11 | Buy it if / Look elsewhere if | `#fit` | 决策引导（含盈亏平衡天数、最短行程两条数据判据） |
| 12 | 优劣势 | `#tradeoffs` | **全部由本页数据推导**的国别量化对比（§3.12），不再印品牌套话 |
| 13 | 竞品内链矩阵（每张卡带数据推导的差异点） | `#others` | 内容集群 |
| 14 | FAQ（数据驱动）+ FAQPage JSON-LD | `#faq` | 长尾问题 |
| 15 | 回主比较 + Trust | — | 内链闭环 |

区块存在性由守卫断言（`reality` / `tripcost` / `fit` / `faq` / `plans` / `tradeoffs` / `verdict`）。

---

## 5. 验收：命令 + 硬指标

### 5.1 命令（按顺序）

```bash
cd /d/esimsift/esimsift
npm run build                                   # build:css → validate → hugo → check:output
                                                # （check:output 已含下面两个守卫）
python -X utf8 scripts/verify_provider_pages.py --sample 6   # ★ 本层专用守卫，11 项检查
python -X utf8 scripts/verify_no_regression.py               # ★ 零回归边界，A/B/C 三组
python -X utf8 scripts/audit_meta.py                         # 全站 title/description 规则
python -X utf8 scripts/check_i18n.py                         # 模板层硬编码 + i18n key 对齐
python -X utf8 scripts/audit_tradeoffs.py                    # ★ #tradeoffs 条目数分布 + 逐条目页数
```

> `verify_provider_pages.py` 只能对**产物**下结论，所以**必须在 `hugo` 之后跑**。
> 跑之前确认没有 `hugo server` 在写 `public/`（`tasklist | grep -i hugo` 应为空）——
> 否则你验证的是 dev server 写到一半的混合产物。

**改哪个脚本要自测哪个**。两个守卫都带 `--selftest`，会往临时目录注入反例，确认
每条检查**真的会报错**：

```bash
python -X utf8 scripts/verify_no_regression.py --selftest
python -X utf8 scripts/check_output.py --selftest
```

> 为什么强制：本层第一版守卫自己有两个索引 bug，导致「国家名」校验拿 `index.html`
> 去比，**连报两轮假绿**（见 §7 第 5 条）。「bad = 0」只有在证明过它会报错之后才有意义。

### 5.2 硬指标（2026-10-04 实测值，第二十三轮末）

| 指标 | 线 | 实测 |
|:---|:---|:---|
| 品牌×国家子页总数 | 400 | **400** |
| 标题长度合规 | 48–54 | **400/400**（48–54，均 51.1） |
| 标题禁则（无 `$`、无 `N plans`） | 0 违规 | **0** |
| description 长度 + 含 `eSIM Sift` | 120–140 + 必含 | **400/400** |
| H1 恰好 1 个 + 含 `eSIM` + 含年份 | 400/400 | **400/400** |
| 逐套餐 Offer 数 == 价格表行数 | 400/400 | **400/400**（Offer 合计 7776） |
| FAQPage ≥3 组且问答非空 | 400/400 | **400/400** |
| BreadcrumbList 4 级 + 路径一致 | 400/400 | **400/400** |
| WebPage `inLanguage` + 合法 `dateModified` | 400/400 | **400/400** |
| 空 `<h2></h2>` / 空 eyebrow | 0 | **0** |
| 模板残留（`{{` / `%!s(`） | 0 | **0** |
| **`data-gb` 与数据列标注一致** | 400/400 | **400/400**（无限 4127 行 / <1GB 的 MB 档 48 行） |
| **计划数三处对账**（H2 = 价格表行数 = Offer 数 = 说明行） | 400/400 | **400/400** |
| **天数按钮无假档位**（按钮值 ⊆ 表里真实档位） | 400/400 | **398/400**（另 2 页 = `FJ/saily`、`FJ/ubigi` 各只有 2 档，按 `>3` 门控不渲染控件，**不是缺陷**） |
| `check_output.py`（格式串泄漏 / 模板残留 / JSON-LD 合法 / 评分区间） | 全绿 | **OK**（586 文件 / 3254 JSON-LD 块） |
| `check_headings.py`（h2/h3 标点） | bad = 0 | **0**（14063 个 h2/h3） |
| `check_i18n.py` 硬编码 / key 对齐 | 0 硬编码 + 0 未定义 | **0 / 0**（928 key，模板引用 922，拼装句碎片 619） |
| `verify_no_regression.py` A 标记隔离 | 0 外溢 + 品牌子页不缺块 | **OK** |
| `verify_no_regression.py` B 全站不变量 | 584 页 0 违规 | **OK** |
| `verify_no_regression.py` C 跨页型 gb 哨兵 | 0 不一致 | **OK**（全站 23328 行 = 品牌子页 7776 + 国家 Hub 15552） |
| 显示「尚未核实」政策的页面 | 0（八品牌 policy 已全覆盖） | **0** |
| `#tradeoffs` 条目数下限 | 优点 ≥3 且缺点 ≥2 | **400/400 通过**（分布见下） |

`#tradeoffs` 条目分布（第二十三轮末，400 页；由 `scripts/audit_tradeoffs.py` 实测）：

| 优点数 | 3 | 4 | 5 | 6 | 7 | 8 |
|:--|--:|--:|--:|--:|--:|--:|
| 页数 | 5 | 95 | 173 | 54 | 69 | 4 |

| 缺点数 | 2 | 3 | 4 | 5 | 6 | 7 |
|:--|--:|--:|--:|--:|--:|--:|
| 页数 | 18 | 39 | 60 | 187 | 47 | 49 |

> 缺点只有 2 条的 18 页全是 `roamic` 在它确实最强的国家（档位最多、热点允许、可充值、
> 日单价第一），两条都是真短板（FUP 3GB/天→1Mbps、无本地号码）。**不硬凑条数** ——
> 用户投诉的是「套话没信息量」，不是「条数少」。

> `scripts/audit_tradeoffs.py` 是常备审计（不在 `npm run build` 里，按需跑）：
> 它同时看**条目数分布**和**逐条目出现页数**。后者专抓「判据永远为假 → 条目从不出现」
> 这类构建全绿的静默失败（见 §7 #26，FUP 那条缺点曾经一次都没渲染过）。
> `--items` 打印逐条目页数明细。

### 5.3 `verify_provider_pages.py` 的 13 项检查

| # | 检查 | 为什么需要它 |
|:--|:---|:---|
| 0 | 模板残留（`{{` / `}}` / `%!s(` / `%!d(`） | i18n 值少占位符、`%g` 喂了 int 都在这里露头 |
| 1 | 标题：48–54 字符 + **禁 `$`** + **禁 `\b\d+\s+plans?\b`** + 必含国家名 | 价格与档位数会变，写进标题必然过期 |
| 2 | description：120–140 + 必含 `eSIM Sift` | |
| 3 | H1：恰好 1 个 + 含 `eSIM` + 含年份 | |
| 4 | 空 `<h2></h2>` / 空 eyebrow | i18n key 漏定义的典型症状（§7 #3） |
| 5 | `Product.offers` 必须是 `AggregateOffer`，其 `offers` 是**非空数组**、**长度 == 价格表行数**，每项 `price` 是**数字**、`priceCurrency == "USD"` | |
| 6 | `FAQPage` ≥3 组且问答非空 | |
| 7 | `BreadcrumbList` 4 级且中级 `href` 与真实路径一致 | |
| 8 | `WebPage` 有 `inLanguage` + 合法 `dateModified` | |
| 9 | 七个区块锚点存在（`reality` / `tripcost` / `fit` / `faq` / `plans` / `tradeoffs` / `verdict`） | 漏渲染 = 回归 |
| 10 | `data-gb` 与数据列的 unlimited / MB 标注一一对应 | `gb` 的 0 哨兵一旦被 `int` 截断就会把 500MB 标成 unlimited（§7 #6） |
| 11 | 行程对比表行数统计（趋势观察） | |
| 12 | **计划数三处对账**：H2 的数字 == 价格表行数 == `offerCount` == 说明行里的数字 | 「All 6 plans」被质疑过（§3.11）；口径要能被读者自核 |
| 13 | **天数按钮无假档位**：每个按钮的 `data-days` 必须在价格表里真实出现过 | 控件取值一旦写死，读者点到不存在的档位会以为漏了套餐（§7 #21） |

### 5.4 已知豁免（不要当成回归去「修」）

- **`de/` 子树**：德语国家页仍套用英文标题/描述（占位状态），`audit_meta.py` 会把它们
  归到 `static` 类并计入违例 —— 这是**已知状态**，不是本层的回归。
- **Hugo aliases 跳转壳页**（`public/en/index.html`）：`<title>` 是目标 URL，
  已由 `audit_meta.py` 的 `http-equiv="refresh"` 判定跳过。
- **`FJ/saily`、`FJ/ubigi` 不渲染天数按钮组**：这两个页面各只有 2 个档位，
  按 `gt (len $myRows) 3` 门控整块跳过。守卫报的 `398/400` 就是这两页，**不是缺陷**。
- **`/guides/best-*-esim/`（5 页）与首页的标题长度**：属别的页面型的既有欠账
  （42 / 44 / 45 / 46 / 57 字符），不在本层范围内。
- **`#tradeoffs` 缺点只有 2 条的 18 页**：全是 `roamic` 在它确实最强的国家，
  两条都是真短板。**不要为了凑条数加没有数据支撑的缺点**。

### 5.5 零回归边界：怎么证明「只改了这 400 页」

`verify_provider_pages.py` 只盯 400 个品牌子页。但本层必然动**共享组件**
（`country-stats.html` / `head.html` / `plan-data-label.html`），它们的下游是
**全站 584 页**。「本层全绿」不等于「别处没坏」。所以另建
`scripts/verify_no_regression.py`，做三组**跨页型**断言：

| 组 | 断言 | 为什么需要 |
|:--|:---|:---|
| **A 标记隔离** | `#reality` / `#hostnetwork` / `#tripcost` / `#trip-calc` / `#fit` / `#tradeoffs` 只允许出现在 `provider_sub`（`#verdict` / `#fup` 另允许 `country_hub`）；且品牌子页**必须**存在 `#verdict` `#plans` `#reality` `#tripcost` `#fit` `#faq` | 改造溢出到别的页型 = 改错了地方；漏渲染 = 回归。两个方向都要断言 |
| **B 全站不变量** | 584 页逐页：恰好 1 个 `<h1>`、`<title>` 非空、无 `{{` / `}}` / `<no value>`、无 `%!x(...)`、无空 `<h2></h2>`、每个 JSON-LD 可解析 | 本轮就是靠这条抓到 54 个德语页的模板残留 |
| **C gb 哨兵跨页型** | 品牌子页**和国家 Hub**（后者 15552 行，是前一版守卫的盲区）里，`0 < data-gb < 1` 的行必须显示 MB、`data-gb == 0` 必须显示 Unlimited | `gb` 用 0 表示「无限」，任何一处 `int .gb` 都把 500MB 变成「无限」 |

**页型分类是这套检查的地基，也是它最容易错的地方**。`compare/<国>/index.html` 是
3 段、`compare/<国>/<品牌>/index.html` 是 4 段 —— 差一段，`provider_sub` 就变成
`country_hub`，检查会安静地查错集合。所以 `classify()` 被单独自测（`--selftest`
里 6 个路径用例）。**反面教材**：本层第一版 `verify_provider_pages.py` 就是
`rel.split("/")[3]` 把 `index.html` 当成国家名，连报两轮假绿（§7 第 5 条）。

#### 一个可复用的交叉校验：两层枚举的应是同一批套餐

品牌子页（400 页 × 每页本品牌套餐）与国家 Hub（50 页 × 每页 8 品牌全套餐）
枚举的**是同一批行**：

| 集合 | 页数 | 套餐行 | 无限档 | <1GB 档 |
|:--|--:|--:|--:|--:|
| `provider_sub` | 400 | 7776 | 4127 | 48 |
| `country_hub` | 101（50 EN + 50 DE + `compare/index.html`） | 15552 | 8254 | 96 |
| 合计 | — | **23328** | 12381 | 144 |

Hub 恰好是子页的 2 倍（50 国 × 8 品牌 × 与 400 页同源）—— **EN 侧 7776 = 7776、
4127 = 4127、48 = 48**。两层的三个数各自相等，就证明**没有哪一边丢了档**。
这是本层最便宜的一个正确性证据：改完打印这张表，对不上就是有套餐在某层蒸发了。

#### 基线清单与字节级 diff

```bash
python -X utf8 scripts/verify_no_regression.py --write-manifest
#  -> docs/regression-manifest.json：每个页面的 sha256 + 页型 + title 长度

# 下一轮改完：
python -X utf8 scripts/verify_no_regression.py --diff docs/regression-manifest.json
python -X utf8 scripts/verify_no_regression.py --diff docs/regression-manifest.json --strict-diff
```

`--diff` 按页型分组报「变更 / 新增 / 删除」，**品牌子页视为预期变化**，
其余页型逐条打上 `★需确认`；`--strict-diff` 下只要非品牌子页有变动就退 1。

> **本轮的边界**：`git` 里最近一次提交（`10-3-4`）早于德语轮次，且 `content/de/`、
> `i18n/`、本层新增的 partial 都还是未跟踪状态 —— **没有可用的「改造前」快照**，
> 所以本轮做不出字节级前后对比。改为：① 用 A/B/C 三组断言证明改造标记不外溢、
> 全站不变量成立；② 把**改造后**状态存成基线，供**下一轮**做字节级比对。
> 这是诚实的能力边界，不要把它说成「已验证零回归」。
>
> **教训**：德语轮次其实也做过一次「与改造前逐字节一致」的比对，但那个脚本
> （`verify_de.py`）是一次性的、没进仓库，基线也没留 —— 于是这一轮想比对时
> 已经无从下手。所以 `docs/regression-manifest.json` **必须提交进版本库**
> （`docs/` 不在 `.gitignore` 里，`public/` 在，正好）。**基线要能活到下一轮，
> 才算基线。**
>
> **顺带验到的一件事**：写完基线后又完整重建了一次（`npm run build`），
> `--diff` 报「584 个页面逐字节相同」—— 说明本站在同一台机器上**构建是确定性的**，
> 基线这个量具本身可信。

---

## 6. 复用到其它页面型的五步

这套方法不绑定 eSIM，凡是「一个数据层 × 一个模板 × 几百个实例」的页面型都能照做：

1. **先定标**：把用户给的规则翻译成**机器可判定的断言**（字符区间、禁用符号、必含词）。
   写成脚本，别靠人眼 —— 400 页看不完。
2. **找数据缺口**：列出「页面该回答但数据层没存」的问题（本层是热点/FUP/充值）。
   只给**核实过的实例**建字段，其余的显式渲染成「未核实」并对**页数**做断言。
3. **修错的前提，不只补新块**：本层顺手修了两处与事实矛盾的历史数据
   （`.strengths` 里写着「Hotspot sharing included」，与官方 500MB/day 上限矛盾）。
   新块做得再好，放在一句假话旁边也白费。
4. **模板改造一律走分支**：`if $unlimitedOnly` / `with $pol` / `if $netNames` /
   `site.GetPage` 门控。**任何条件不满足时就少渲染，不要渲染错的**。
5. **建守卫再交付**：把「标题规则 / JSON-LD 完整性 / 空标题 / Offer 与表格行数一致 /
   区块存在性」全部机器化，然后**注入一个反例确认它会失败** ——
   「bad = 0」只有在证明过它会报错之后才有意义（见 §7 第 5 条）。

---

## 7. 真实事故（改这一层踩过的坑）

| # | 事故 | 根因 | 对策 |
|:--|:---|:---|:---|
| 1 | `{{ range .:= $tripRows }}` 这行垃圾语法 | 手写模板留下的 | 直接删。**Hugo 对这类错误会报错，但报错行号指向 `baseof.html`**，容易找错地方 |
| 2 | `{{ with $pol }}…{{ else }}…{{ end }}` 写在 `dict` 参数位 | 无效语法（`dict` 的参数是值，不是模板动作） | 把分支**提到前面算成变量**（`$fupDetail` / `$hotspotDetail`）再进 dict |
| 3 | ★ **i18n key 漏定义 → 空 `<h2></h2>` 静默上线** | Hugo 对**字面量**缺失的 key **返回空字符串**：不报错、退出码 0、五重校验全绿 | 三处一起补：① 补 key；② `check_i18n.py` 新增 `check_used_keys()`（模板引用 vs en.toml 比对，缺即 ERROR）；③ `verify_provider_pages.py` 加「空 h2/h3」检查 |
| 4 | `undefined variable "$t"` 构建失败 | `{{ range $tripRows }}` 后面用了 `$t.x`，但 `range` 没绑定变量名 | `{{ range $t := $tripRows }}` |
| 5 | 守卫脚本**自己有两个索引 bug** | `rel.split("/")` 的第 3/4 段取成了国家/品牌（`compare/<country>/<provider>/index.html` 里其实在第 2/3 段），导致「国家名」校验永远在拿 `index.html` 比 | 守卫也要**注入反例自测**；写脚本时把路径段打印出来看一眼 |
| 6 | ★ **`500MB` 全站被当成 "Unlimited"** | **根因在聚合层**：`partials/country-stats.html` 写的是 `"gb" (int .gb)`，把 0.4883 截断成 0，而 **0 是"无限"的哨兵值**。爆炸半径：全站 12 处 `where $rows "gb" 0`（7 个模板）把它选进无限套餐、`unlimitedCount` 把它数进「N unlimited plans」、`/compare/<国>/` 的「重度用户推荐」可能推荐一个 500MB 试用装、`/research/unlimited-esim/` 把它列进无限榜、`/tools/` 在「需要无限」时返回它 | ① 聚合层 `gb` 改 **float**（哨兵语义不变、但变成真的）→ 12 处过滤自动修正；② `unlimitedCount` 改按本来就正确的 `isUnlimited` 计数；③ `$perGB` 条件改 `gt (float .gb) 0.0`；④ 所有 `int .gb` / `parseInt(dataset.gb)` 的判零改浮点比较（10 个文件）；⑤ 所有**直接打印 `.gb`** 的地方改走 `partial "plan-data-label.html"`；⑥ 新增守卫：`data-gb` 与数据列的 unlimited 标注必须一一对应（400/400，另报告 48 行 <1GB 的 MB 档） |
| 11 | 竞品「更便宜」拿 500MB 试用装作依据 | `$rivalMin` 是竞品**最小套餐价**，而最小套餐常是 100–500MB 试用装。FAQ 原文写「Saily 最便宜 $5.29；Yesim 是 $0.51」，读起来像同类对比 —— 而 FAQ 是 AI 引用率最高的一块 | 把竞品最小套餐的**数据量标签**一并算出来（`$provPick`）传进文案：「Yesim's is $0.51, though that entry price buys 500MB」。同一手法用于 `#fit` 的 Look-elsewhere 条目。**判据**：任何「A 比 B 便宜」的断言，都要能回答「便宜在哪一档」 |
| 7 | 在品牌页上说「Airalo 比 Airalo 便宜」 | 对比表的「对手列」没排除本品牌 | `ne .key $provKey`（§3.6） |
| 8 | 「无本地号码」的判据用错了字段 | 拿品牌类型（`$p.type`）推断，等于替所有品牌做承诺 | 改用核实过的 `policy.voice`；**没核实就不说**（§3.3） |
| 9 | 改完模板但 `public/` 没变 | `public/` 是产物目录，被 `hugo server` 占用时会写 dev 产物 | 验证前 `tasklist \| grep -i hugo`；绕开办法 `hugo --destination <临时目录>` |
| 10 | ★ 页面上印出 `%!g(int=20)GB` | `plans[].gb` **既有 int 又有 float**，Go 的 `%g` 只接受 float。`hugo` 退出码 0、`check_i18n` / `check_css_sync` / `check_headings` 全绿，只有 `check_output.py` 拦下 | 转换 partial 开头 `{{ $gb := float . }}`。**判据**：任何 `%g` / `%f` / `%e` 的参数都要先 `float`，不要假设数据层类型统一 |
| 12 | ★ **54 个德语页把开发者备注印给读者看** | `content/de/**/*.md` 的**Markdown 正文**里写了 `{{/* TODO(de)：正文待翻译… */}}`。Hugo 只解析模板文件、不解析正文，这段字被 Goldmark 当普通段落输出 —— 读者能在 `/de/` 的 50 个国家页上直接看到 "TODO(de)：正文待翻译"。`hugo` 退出 0、当时五重校验全绿（`check_output.py` 当时只扫 `%!` 格式串，不扫模板残留） | ① 注记搬进 **front matter 的 YAML 注释**（`#` 开头，解析器会忽略），正文清空；② `check_output.py` 新增全站扫描：**屏蔽 `<style>`/`<script>` 之后**再找 `{{` 与 `<no value>`；③ 只扫 `{{` 不扫 `}}` —— 压缩后的 Tailwind 内联在 `<style>` 里，`}}` 有 390 个文件命中，扫它就是自造假阳性 |
| 13 | 守卫的「标记隔离」报了 8 个假阳性 | 检查里写 `id="tradeoffs"`，把 `esim-providers/single.html` 的 `id="tradeoffs-pending"` 也匹配上了；而品牌详情页**本来就**有自己的 `#tradeoffs`（"Price record"）区块 | ① 标记一律**带收尾引号**；② 报出来的每一处都先**读渲染后的 HTML 核实**，确认是既有独立区块后才写进白名单（`{"provider_sub", "provider_hub"}`），并在代码里注明核实日期。**先看再豁免，不要先豁免再找理由** |
| 14 | ★ 新 H2 印成 `<no value> <no value> eSIM hotspot 5G and fair-use rules` | i18n 值从 `"What the plan label leaves out"` 改成带 `{{ .brand }}` / `{{ .country }}` 的句子，但**模板调用处没跟着加 `dict` 参数**。Hugo 对「有占位符、无实参」不报错，直接渲染 `<no value>` | 改 i18n 值的占位符时，**同一个提交里必须改调用处**。产物级 `check_output.py` 的 `<no value>` 扫描是唯一能拦住它的检查（`hugo` 退出码 0） |
| 15 | ★ 验证器把 **46 个正确的链接判成失败** | 一次全量扫描报「197 条里 49 条不通过」。但 `403` 只说明站点**拒绝机器人**（`att.com` / `t-mobile.com` / `bell.ca` 全是 403），`000` 只说明**本机网络不通**（`jio.com` 本机 000、浏览器正常） | 判定分四类：`2xx` ok / `403·412·429` bot 墙（保留）/ `404·410` 死链（唯一 fail）/ `000·5xx` 本机不可达（报告不删）。**判据**：一个「验证脚本」如果会把 46 个正确链接删掉、只留下 1 个错的，那它不是验证脚本，是清理工具 |
| 16 | ★ 冰岛运营商官网写错：`noa.is` 不存在 | 源数据里品牌名拼作 `Noa`，我照名字猜域名。正确的是 `nova.is`（Nova 是冰岛第三家运营商） | 域名**必须实测**，不要从品牌名推。这条正是被 15 的四类判定捞出来的（`noa.is` → 000，`nova.is` → 200） |
| 17 | `dataset.perGB` 永远取不到值 | `data-pergb` 对应的 dataset 键是**全小写** `pergb`。写成 `dataset.perGB` 得到 `undefined`，比较函数返回 NaN，`Array.sort` 于是**保持原顺序** —— 而原顺序恰好就是正确的，所以这个 bug 在页面上看不出来 | 用 `data-*` 时把键名**全部小写**。顺带：这类「静默失效」只有在**移除该控件**时才会暴露，所以退役旧控件时要把它的老 bug 一起结清 |
| 18 | i18n 补丁脚本「替换成功但没插入新 key」 | 处理被替换的那一行时走了 `continue`，跳过了紧跟其后的插入分支 | 补丁脚本要**断言每组改动都命中**（`hits != len(repl)` 就报错），并在跑完后 `grep` 复核新 key 真的在文件里 |
| 19 | ★★ **`hugo` 构建失败却报「全绿」** | 命令写成 `hugo --quiet --logLevel warn 2>&1 \| head -20`。模板报 `undefined variable "$t"`，但 `hugo` 的**报错走 stdout**，`\| head` 提前关掉管道让 `hugo` 拿到 SIGPIPE，`$?` 取到的是 `head` 的 0 而不是 `hugo` 的失败 | **任何带管道的构建命令都不能用 `$?` 判断成败**。改 `hugo --logLevel warn 2>&1 \| tail -30` + 读 `${PIPESTATUS[0]}`，或直接 `npm run build`（脚本内部有 `set -e`）。判据：一条命令只要经过了管道，「退出码」说的就是最后一个进程的事 |
| 20 | `{{ range $tiers }}{{ $t }}` 未定义变量 | `range` 不绑定变量名时，`. ` 才是当前值；写 `$t` 是访问一个不存在的变量 | 一律 `{{ range $tier := $tiers }}`。**这是本层第二次踩**（见 #4），写 `range` 时先写完变量名再写体 |
| 21 | ★ 天数按钮里有页面买不到的档位 | 取值写死成 `slice 3 5 7 10 14 21 30`，而 Holafly 日本真实档位是 3/5/7/10/**15**/30。读者点「14 天」会看到空列表，以为漏了套餐 | 控件取值**必须由数据推导**（`$myRows` 的 `days` 去重排序）；档位多于 12 个时按 `1 2 3 4 5 7 10 14 21 30 60 90` 阶梯取「最小的 ≥ 目标的真实档位」。新增守卫：按钮的 `data-days` 必须是表里真实出现过的档位（398/400，另 2 页本来只有 2 档、按 `>3` 门控不渲染） |
| 22 | 同页两组天数按钮互相串组 | `document.querySelectorAll('[data-days]')` 是**全局**选择器，套餐表和行程计算器两组按钮会一起命中，点一处两处都变 | 选择器一律从**容器**出发：`group.querySelectorAll('button[data-days]')` |
| 23 | ★★ **「A 比 B 便宜」拿不同流量档比**（#11 的新形态） | 价差按**绝对差额**取最大值，必然选中「我方大流量档 vs 对手 1GB 试用装」。实测：Roamic 日本 30 天档 10GB/$9 被拿去跟 Ubigi 的 1GB/$4 比，得出「便宜 $5」，读起来像同类对比 | **同类比同类**：计量档只在对手流量 ≥ 我的流量时才比（对手的无限档也算「流量不少于我」）。无限档只在**行程长度精确匹配**时才比 —— 否则会把「跳档购买」的价差伪造成「别家更便宜」（Ubigi 日本只有 8/30 天两档，10 天行程被迫买 30 天 $45，跟 Roamic 的 10 天档 $23 比就得出失真的 $22） |
| 24 | 优点列里写了缺点 | `tradeoffs_w_unl` 的文案把「对手更便宜」塞进了「优势」栏，语义反了 | 拆成 `w_unl_best`（真第一）/ `w_unl`（只陈述自家日单价，不带比较），比较放回缺点列 |
| 25 | ★ **价格数字与品牌名来自两套计算** | `l_unl` 用 `$cUnlPerDay`（全国最低无限日单价）+ `$rivalKey`（**最低入门价**品牌）拼成一句。日本实测：数字 $1.50 属于 Ubigi，句子却写 "from Roami"（Roami 自家是 $2.40） | 一个句子里所有事实**必须来自同一次选优**。改成用同一遍循环同时记下「价」和「谁」（`$lkUnlRival`），品牌名一律 `index $d.providers $lkUnlRival`。**判据**：凡出现两个不同变量拼进同一句，先问它们是不是同一次计算的结果 |
| 26 | ★ **FUP 缺点条目从不触发** | 判据写成 `and (gt $myUnlPerDay 0.0) (not .fup_allowance)`，但八个品牌的 `fup_allowance` **全都有值**（Holafly 的是字面量 `"No GB figure published"`），`not` 永远为假 | 改成按数值分档：额度里有明确日数字且 < 6GB/天 → 讲清「多少之后掉到多少」；文案以 `no` / `not` 开头 → 讲清「限速点不公开」；其余（如「按套餐不同，各套餐页公布」）**不列为缺点**（那是透明度加分项）。**判据**：一条缺点如果在 400 页上一次都没出现，先怀疑判据而不是数据 |
| 27 | ★ `l_upsell` 在 Roamic 日本误报「15 天没有匹配档位」 | 判据用了「最便宜**可覆盖**档的 days」（Roamic 15 天最便宜是 5GB/21 天档，于是算出 21≠15），而 Roamic 其实有 1–30 天全档位 | 判据改成「品牌**是否存在** `days == 行程长度` 的档」（`uniq` 一份 `$myTierDays` 后 `in` 判断）。**判据**：「没有 X」这类断言必须查 X 的存在性，不能用别的量的代理指标 |

---

## 8. 仍然待办（明确不在本轮范围内）

- ~~`data/providers.toml` 的 `policy` 只填了 6/8 品牌~~ —— **已完成**，
  八品牌 policy 全覆盖（`roami` / `roamic` 已按各自官网核实补齐），
  「尚未核实」页数 **100 → 0**。
- `fup_allowance` 里的口语化描述（`"No GB figure published"` / `"Varies by plan - published per plan page"`）
  现在是**同时供展示层和判据层**使用的同一个字符串 —— `#reality` 直接印它，
  `#tradeoffs` 用正则从里面抠数字（抠不到就按 `^no` 判断）。
  这很脆弱：**下一轮应把它拆成 `fup_allowance_gb`（数值，可为空）+ `fup_allowance_text`（展示用）**，
  判据只读数值字段。当前做法能跑是因为八个值都在人工控制下，不要在这个字段上再塞新句式。
- `providers.toml` 的 `tagline` 与 `.strengths` / `.weaknesses` 是英文数据层散文，
  跨语言需要 `data/<lang>/providers.toml` 覆盖 —— 属德语站正式启动时的工作。
  注：品牌页的「优缺点」已**不再**读这几个字段（§3.12），改为本页数据推导，
  所以它们现在只影响 `/esim-providers/<brand>/` 品牌中心页。
- `compare_provider__*` 的德语值当前是英文占位（与 en 逐字一致），
  沿用 `compare_single__*` 等既有段落的同一状态。
  例外：本轮新增/改写的 `tradeoffs_*` / `price_disclaimer` 等 20 余条**已写真实德语**，
  上面那条只适用于更早的一批。
- 全站 619 处「拼装句碎片」中，本层贡献的那部分已清零（
  `compare/provider.html` 41 → 0）；其余分布在别的模板，不属本层。
- **德语 50 个国家页现在正文为空**。原先把开发者备注当正文，误打误撞渲染出了
  正文块（含一个英文 h2）。清掉备注后正文块整块跳过，所以德语国家页上线前
  必须补真正的德语正文（`content/de/compare/*.md` 的 body），
  并把 front matter 里的 `noindex: true` 一并删掉。见 §5.2 的 14063 说明。
- **`data/refs.toml` 里 46 条链接「本机不可达」（`000`）**，需要换一个网络环境
  重跑 `scripts/verify_external_refs.py` 才能从「未知」变成「已核实」。
  当前它们照常渲染 —— 判定纪律见 §3.9，不要因为本机连不上就删。
- **`ES | Yoigo` 没有外链**：`yoigo.com` 与 `yoigo.es` 均已 404（品牌并入 MasMovil
  后独立官网关闭）。模板对该运营商会优雅跳过。若日后确认新官网，补回 `refs.toml` 即可。
- `refs.toml` 目前指向运营商**官网首页**，只有日本三家直接指到了覆盖地图
  （`docomo.ne.jp/area/` 等）。要更精确的话应逐国换成覆盖页深链，但那需要逐条实测 ——
  **首页是稳定优先的选择**，不要为了「更精准」引入会失效的深链。
- **`#tradeoffs` 的 5G 判据用的是「宿主网络的制式」**（`carriers.toml` 的 `tech`），
  不是「该品牌的套餐实际接入哪些网络」。前者是国别事实、稳定；后者需要逐品牌
  核实接入协议（只有 `plans[].networks` 有值的品牌才够格说），当前数据不足，
  所以文案写的是「5G on all N host networks in <country>」而不是「这个套餐支持 5G」。
- **`hotspot` / `fup` 的逐国差异没有建模**。`policy` 表是**品牌级**的，
  但 `fup_note` 里已经记下 Roami 的阈值「destination-dependent」（美国页说无限速、
  英国指南写 2GB/天）。所以同一品牌 50 个国家页印的是同一个阈值 ——
  这是当前数据层的边界，不是渲染 bug。要做逐国就得把 policy 下沉成
  `[<brand>.<iso>.policy]`，那是独立一轮的量。

---

# 附：品牌 Hub 页（`/esim-providers/<brand>/`）优化规范

> 2026-10-04 第二轮。上文 §0–§8 讲的是**品牌×国家子页**（400 页）；
> 本节讲**品牌 Hub**（8 页：airalo / alosim / holafly / roami / roamic / saily / ubigi / yesim）。
> 两者共用数据层与 partials，但页型不同、决策也不同 —— 下面有三条**不能照抄**。

## 9. 与子页的三处「不能照抄」

### 9.1 数字放在哪一层：标题 evergreen，H1 数据驱动

子页（§3.1）的结论是「标题不放价格、不放套餐数量」，理由是数字会随数据过时。
**Hub 页沿用同一条结论**，但数字的去处不同：

- `<title>`：不放数量、不放价格（2026-10-04 用户再次确认）。
  保留意图词：Review / Plans / Prices / Unlimited / 5G / Value / Compared / Worth It。
- `description`：承载套餐数 + 「hotspot rules / 5G support / who beats them」意图词。
- `H1`：由 `$totalPlans` **构建期实时渲染**，所以 H1 印得出「985 Plans」——
  它永远与数据层一致，不存在过时问题。

口诀：**标题 evergreen，H1 数据驱动。** 8 个品牌页实测 title 49–53 字符（audit 要求 48–54）。

### 9.2 「A 比 B 便宜」在 Hub 页要聚合到「全市场」维度

子页比的是「同一国家内两个品牌」（§3.12 / 事故 #23）；Hub 页比的是
「本品牌 vs 全场」。`partials/provider-alts.html` 把「同类比同类」固化成四层匹配：

1. 我方是无限档 → 只跟对手的无限档比；
2. 精确匹配同 `(gb, days)`；
3. 对手数据量 ≥ 我方；
4. 都落空时退回「入门对入门」，并**显式标记** `mt="entry"`（UI 上不能装作是同类对比）。

输出 `dict` 含 `rows / n / total / medPct / worst / topAltKey / topAltName / topAltN`。

### 9.3 宿主网络是**国家级**事实 —— 不能编品牌级网络差异

`data/plans/*.toml` 的 `[ISO].networks` 由 `scripts/backfill_networks_uniform.py`
回填，实测**八个品牌 × 50 国完全一致**（每国平均 2.9 个运营商）。
所以 Hub 页的 5G 板块只能讲「**目的地**有没有 5G」+「本品牌在哪些有 5G 的市场同时最便宜」，
绝不能写「Airalo 在韩国只有 LTE」这种品牌级说法（数据不支持）。

另：`carriers.toml` 实测 50 国里**只有 Fiji (FJ) 是纯 4G**，其余 49 国至少一个 5G 宿主网络。

## 10. Hub 页新增区块（模板从上到下）

| id | 回答的问题 | 数据源 |
|:--|:---|:---|
| `#reality` | 热点 / 公平使用阈值 / 充值 / 是否支持 5G | `providers.toml [<brand>.policy]` + `carriers.toml` 的 `tech` |
| `#whobeats` | 哪些国家有更便宜的**同类**档，该去看谁（链接站内 provider 页） | `provider-alts.html` |
| `#network` | 5G 实况：N/M 市场有 5G；纯 LTE 市场列表 | `carriers.toml` |
| `#headtohead` | 最接近的两个对手 + 各 3 条关键差异（按 `cheapest` 距离排序，非人工挑选） | `provider-agg.html` |
| `#calc` | 「我的行程该买哪个档」 | `country-stats.html`（只送本品牌档位 + 该国 3 个基准，避免页面膨胀到 150KB） |
| `#reading` | 评价怎么读 / 区域指南 / 数字从哪来（E-E-A-T） | i18n + `$totalPlans` |

FAQ 另补 3 问：热点、5G 实况、谁更便宜。Product JSON-LD 补逐市场 `offers`（取 12 个最便宜市场）。

## 11. Trustpilot 口径：**只给档案链接，不印分数**

用户要求 `aggregateRating` 必须「有据可查」。实测做不到：

- 同一品牌在不同**地区域名**下聚合成**不同值**（Airalo 实测 3.9 / 4.0 / 4.1）。
- 本机抓取全部被反爬墙拦截（`WebFetch` 拿到 "Verifying your connection..."，`curl` 一律 `403`）。

结论：`data/providers.toml` 的 `[<brand>.info].trustpilot` **只存档案 URL、不存分数**；
`#reading` 文案改为「教读者怎么读评价页」（重点是一星里「落地连不上」那一类问题），
并在**无档案时**走 `reading_reviews_none` 分支说明理由。

⚠️ **域名不能按官网机械拼接**：Ubigi 的档案是
`trustpilot.com/review/cellulardata.ubigi.com`，**不是** `ubigi.com`。

⚠️ **Roami 没有 Trustpilot 档案**：对 `trustpilot.com` 做域名过滤搜索只返回
`roamic.com` 与无关品牌。Roami 自家博客宣称的 4.9 分、以及第三方评测引用的
「13k+ 条评价」，恰好等于 **Roamic** 的 13,683 条 —— 高度疑似两家被混为一谈。
故 `roami` 该字段**留空**（模板自动降级），"宁缺勿造"（§3.3）。

## 12. Hub 页验收

```bash
npm run build
python -X utf8 scripts/audit_meta.py          # provider 类应 0 违规
python -X utf8 scripts/verify_no_regression.py --diff docs/regression-manifest.json
```

基线 diff 的**期望形态**：只有 `provider_hub=8` 变化，`provider_sub=400` **逐字节不变**。

**判据**：改 Hub 页却动到了子页 / 国家 Hub，说明碰到共享组件了
（`country-stats.html` / `provider-agg.html` / `plan-data-label.html` / `head.html`）——
那些是全站下游，必须回滚或逐页复核。

## 13. Hub 页事故（编号接 §7）

| # | 事故 | 根因 | 对策 |
|:--|:---|:---|:---|
| 28 | ★★ **计算器数据被压成裸数字，页面静默出错** | 写成 `$mineList = $mineList \| append (slice gb days price)`。**Hugo 的 `append` 遇到切片实参会逐个展开并入**（等价于 `append $s a b c`），17 个档位于是变成 **51 个裸数字**。`json.loads` 照常通过（合法 JSON）、`check_output.py` 全绿、页面不报错，只有 JS 里 `p[0]/p[1]/p[2]` 静默取错 | 一条记录存成 **dict**：`append (dict "gb" … "days" … "price" …)`。**双层 slice 反包也不行** —— Hugo 直接拒绝：`cannot append slice of []interface {} to slice of interface {}`。判据：`append` 只适合并入**标量或 dict**；要成组并入必须包 dict。**校验**：把 `application/json` 数据块也纳入 `json.loads` + 断言元素形状（当时就是这么发现的） |
| 29 | 守卫把**合法的嵌套 JSON** 判成模板残留 | `verify_no_regression.py` 检查 B 全站扫 `}}`。计算器数据块里 `…"u":[…]}}` 是合法 JSON 收尾，却命中 8 页 × 2 类 = 16 处误报 | 扫之前先**挖掉 `type="application/json"` / `ld+json` 数据块**，可执行 `<script>` 仍照扫（真正的模板泄漏藏在那里）。同时把数据块纳入 `json.loads`，把误报源变成一处**真实检查**。自测要**同时**证明「放过数据块」与「仍抓住真泄漏」 |
| 30 | Hub 页新增区块被判成「泄漏到别的页型」 | `#reality` 在守卫里登记为 `provider_sub` 专属，而 Hub 页新增了同名区块（内容不同：品牌级 policy vs 国家级 plans） | 逐条读**渲染产物**确认是预期新增后，才扩白名单并注明日期与理由（沿用事故 #13 的纪律）。`#calc` 同理 —— 工具页 /tools/ 早有同名区块，登记为 `{"provider_hub", "tools"}`（id 是页内作用域，同名不冲突） |
| 31 | `undefined variable "$mk4gNames"` 构建失败 | 变量在 `#reality` 区块里才算，但渲染顺序更早的 FAQ 已经引用它。**Hugo 不允许先用后定义** | 把派生量统一提到文件顶部、紧跟其依赖的原始数据之后。判据：任何被**两个以上**区块复用的变量，必须定义在**第一个**使用点之前 |
| 32 | 品牌前缀冠词写死成 `a` | `reality_lead` 写成 `whether a {{ .brand }} plan…`，渲染出 "whether **a Airalo** plan"（aloSIM 同样错）。品牌名从 Airalo 到 Yesim 混着元音/辅音开头，一个固定冠词不可能对 | 去掉冠词，改写成 `whether the plan actually works…`。判据：i18n 值里**不要**把 `a/an` 和品牌占位符直接相邻 —— 这是无法靠数据修好的语法错误 |

> 遗留（**不在本轮范围**）：`compare_provider__faq_q_hotspot` /
> `compare_provider__faq_q_price` / `compare_provider__reality_lead` 三条**子页**
> i18n 值有同样的 `a {{ .brand }}` 冠词问题（影响 400 页文案），本轮未动。
> 修法是同一套（去冠词或改写句式），但会改动 400 页产物与基线，应单开一轮。

---

## 14. sitemap `lastmod` 与「产物域名卫生」（第二十五轮）

### 14.1 `lastmod` 的解析顺序（改品牌优先）

`layouts/partials/sitemap-urls.html`，按以下顺序取第一个有值者：

| # | 页型 | 依据 |
|:--|:---|:---|
| 1 | 品牌 Hub | `max(该品牌最新价格核对日, 该品牌 profile_checked)` |
| 1 | 品牌×国家子页 | 该品牌在该国的价格核对日 |
| 1 | A-vs-B 对比页 | 这两个品牌各自最新价格核对日取最大 |
| 2 | 国家 Hub | `country-stats.checked`（该国 8 品牌最大） |
| 3 | 有 `date`/`lastmod` front matter 的编辑页 | 页面自身日期 |
| 4 | 其余数据驱动页 | 全站最新价格核对日 |

**绝不 fallback 到 `now`。** 理由见 §3.13.1。

顺序为什么重要：第 1 档必须排在「`.Lastmod`（git 提交日 / front matter）」之前。
品牌页的 front matter 只有 `title` / `description`，一旦 Hugo 用 `:git` 推出一个提交日，
它就会盖过品牌级 `checked`，日期又跟数据脱钩。**品牌粒度 > 页面粒度 > 兜底。**

### 14.2 三类产物卫生事故的守卫：`scripts/check_dates.py`

已接入 `npm run check:output`（八项校验 → 九项）。三项断言：

| 断言 | 抓什么 | 真实事故 |
|:---|:---|:---|
| **A 域名** | `public/` 任何 `.html/.xml/.json/.txt` 含 `localhost`；sitemap `<loc>` 与 `hugo.toml` 的 baseURL 不同源 | 见 §14.3 |
| **B 日期** | 从 `data/plans/*.toml` + `data/providers.toml` **独立重算**每张页面的期望日期，与 sitemap `lastmod` / JSON-LD `dateModified` / 页面可见日期逐一对账 | 见 §3.13.1 |
| **C 完整性** | sitemap 声明的每个 URL 都必须在 `public/` 有产物 | 见 §14.4 |

**B 的两条细分规则**（都是被误报逼出来的）：

1. **日期文案分两组**。「Last updated &lt;d&gt;」是通用表述 → 对页级日期；
   「prices … as checked on &lt;d&gt;」/「rebuilt &lt;d&gt;」是价格专属 → 对价格日期。
   第一版混成一组，于是 8 个品牌 Hub（两组值**故意不同**）全被误判为违规。
   **误报会逼你把规则写精确，而不是把检查改松。**
2. **页型范围不对称**：`/esim-providers/*`、`/compare/*` 走严格模式；
   `/guides/*`、`/research/*` 只查 `lastmod == dateModified` —— 它们的**文章日期**
   与**数据快照日**本来就该不同（文章 10-02 写、价格 09-30 核），强行拉平会掩盖真实信息。
   第一版把编辑页也纳入严格模式，立刻报 11 处误报，逐页读过才发现两个日期语义不同。

### 14.3 ★★ dev server 把 `localhost:55171` 写进了 136 个产物

**现象**：用户报告 sitemap 里是 `http://localhost:55171/compare/poland/`。
`public/` 里 136 个文件（含 canonical）带 `localhost:55171`，`public/esim-providers/` 整个目录是空的。

**根因**：`hugo server` 会把 baseURL 的 host 换成 `localhost:<端口>`；
1313 被前一个 dev server 占着，Hugo 就自选了 55171。这个 server **没有** `--renderToMemory`，
于是把这套 localhost URL 当成产物写进了 `public/`，并在写一半时被中断。

**注意**：`hugo.toml` 的 `[server]` 配置段**只有 `redirects` 和 `headers` 两个键，
不存在 `renderToMemory`**。实测写进去完全无效（产物照样落盘 928 个文件），
只有命令行 flag 才生效。**这个「假保护」已删除** —— 写进配置却不起作用的注释
比不写更危险，它会让人以为已经防住了。

**对策（三层）**：

1. `npm run dev` 用 `hugo server --renderToMemory`（既有，唯一推荐的预览入口）；
2. `check_dates.py` 断言 A 兜底拦截（任何带 `localhost` 的产物直接构建失败）；
3. 文档写明：**不要手敲 `hugo server`**；万一敲了，务必再跑一次 `npm run build`。

**判据**：本地预览的地址栏里出现 1313 以外的端口，就已经有产物被污染了。

#### 14.3.1 曾试过 `--cleanDestinationDir`，已撤销（附实测耗时）

想法是「构建前先清空 `public/`，残留文件就不可能活下来」。实测代价：

| 构建 | Hugo 阶段耗时 |
|:---|:---|
| `hugo`（无 flag） | **57 s** |
| `hugo --cleanDestinationDir`（public/ 部分重建） | 4 min 17 s |
| `hugo --cleanDestinationDir`（public/ 完整） | **9 min 13 s** |

耗时**随产物规模恶化**（4m17s → 9m13s），像是每次写入都要走一遍目标目录的写法。
对一个 400+ 页、需要频繁重建的站点，这是不可接受的回归，且它解决的问题
（残留文件）已经被断言 A 覆盖。**撤销。**

### 14.4 ★ `--cleanDestinationDir` 暴露的盲区：半截产物（断言 C 的由来）

撤销 flag 之后 `public/` 不再被预清空，但这次试验暴露了一个**独立**的、更重要的盲区：

先清空再重建时，构建一旦被中断（Ctrl-C、终端关闭、超时），`public/` 会停在
「已清空、未写完」的状态 —— 看着是新的，实际整段页面缺失。**这比旧产物危险得多**，
而且**所有既有校验都不会报错**：它们清一色是「有则查」（读到什么检查什么），
没有一个会问「该有的文件在不在」。

这就是断言 C 存在的唯一理由：**唯一能发现「该有的文件不在」的地方**。
本轮实测踩到过一次（构建被 SIGTERM，`public/esim-providers/` 归零），断言 C 当场报出 44 个缺失 URL。

### 14.5 遗留（明确不在本轮）

- `/esim-deals/` 的可见日期（促销复核日，来自 `providers.toml` 的 promo 字段）
  与 sitemap `lastmod` 仍不一致。它不在 `check_dates.py` 的严格范围内，
  也不属于「品牌页 / 国家页」两类。要修就为 promo 数据补一个同类日期口径。
- `/`（首页）的 `lastmod` 来自 front matter，可见日期来自数据快照 —— 语义不同，同上。

