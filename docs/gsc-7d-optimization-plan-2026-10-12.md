# GSC 7 天数据体检与 SEO 优化方案

- 数据源：`docs/esimsift.com-Performance-on-Search-2026-10-12.xlsx`
- 数据窗口：**2026-10-05 ~ 2026-10-12**（近 7 天）
- 两张表：`查询数`（387 条）+ `网页`（241 条）
- 复算脚本：`.buildlog/r84_gsc_analysis.py`（只读，不依赖 openpyxl）
- 本文所有数字均由该脚本独立复算，未转录任何现成分析

---

## 0. 结论先行

站点的问题**不是收录、也不是页面不够**。7 天全站 **2949 展示 / 6 点击 / CTR 0.20%**，病因是两条：

**① 一个页面吃掉 18% 的展示，却 0 点击。**
`/compare/canada/saily/` = 532 展示、位置 10.86、**0 点击**。机械原因是它的 SERP 摘要里写着
`best $2.20/GB (#9 of 10)` —— 搜 `saily esim canada` 的人读到「这牌子在 10 家排第 9」，转头去点 saily.com。
**这个写法覆盖 449/499 个排列页（90%），合计承担全站 40% 的展示。**

**② 整站在「非品牌商业词」上没有排名。**
143 条 best / cheapest / unlimited 类查询，位置中位数 **78**，**只有 4 条进前 30（合计 5 次展示）**。

而站点**已经证明能排的**是另一类词 —— 品牌 × 具体限定：
`saily esim canada` 9.9 · `saily esim korea` 5 · `roamic saudi arabia` 6 · `holafly esim egypt` **1** · `saily coupon code` 9.5。

> ⇒ **优化方向是「放大已经赢的形态」，不是「去卷 head 词」。**

---

## 1. 数据体检（先证伪前提）

### 1.1 ⚠️ 两张表对不上账 —— 这条必须先修

| 表 | 行数 | 展示 | 点击 | CTR |
|---|---:|---:|---:|---:|
| 查询数 | 387 | **1548** | 0 | 0.00% |
| 网页 | 241 | **2949** | 6 | 0.20% |
| **差** | — | **+1401** | **+6** | — |

查询表只覆盖了**约一半**的展示量。因此「所有查询点击都是 0」是**假结论** —— 那 6 个点击所属的查询根本不在表里，基于查询表的判断有一半是盲的。

**动作**：GSC 里把日期设为 2026-10-05 ~ 2026-10-11（整日，避开半天），两个标签页**同一次**导出；或走 Search Analytics API。**下一次诊断前必须先让两表对上账。**

### 1.2 全站盘子

- 产出页面 **1291**（en 646 + de 645），其中**只有 241 页有展示**（18.7%）
- 7 天：**2949 展示 / 6 点击 / CTR 0.20%**
- 387 条查询里 **222 条只有 1 次展示** —— 长尾极长、极薄

### 1.3 集中度：靠一个页面 + 一个词撑着

| | Top1 | Top5 | Top10 |
|---|---:|---:|---:|
| 查询 | **33.5%**（`saily esim canada` 519 展示 @9.9） | 43.6% | 48.4% |
| 网页 | **18.0%**（`/compare/canada/saily/` 532 展示 @10.86） | 29.5% | 37.2% |

### 1.4 位置分布

**查询**（387 条）

| 位置 | 条数 | 展示 | 展示占比 |
|---|---:|---:|---:|
| 1–3 | 6 | 11 | 0.7% |
| 3–10 | 39 | **656** | **42.4%** |
| 10–20 | 29 | 57 | 3.7% |
| 20–30 | 14 | 39 | 2.5% |
| 30–50 | 36 | 101 | 6.5% |
| **50–100** | **259** | **680** | **43.9%** |
| 100+ | 4 | 4 | 0.3% |

⇒ **67% 的查询（259/387）落在 50–100 名的死区。** 真正的问题不是「没排名」，是「有排名、无点击」。

**网页**（241 条）

| 位置 | 条数 | 展示 | 点击 |
|---|---:|---:|---:|
| 1–3 | 2 | 31 | 0 |
| 3–10 | 44 | 445 | 1 |
| **10–20** | **20** | **707** | **0** |
| 20–30 | 18 | 256 | 0 |
| 30–50 | 29 | 329 | 3 |
| 50–100 | 72 | 996 | 2 |
| 100+ | 56 | 185 | 0 |

⇒ 位置 **10–20 的 20 个页面拿了 707 展示（24%）却 0 点击**。这个量级不可能用运气解释。

---

## 2. 三条诊断

### 诊断 A｜站点的「排名能力」= 页面与查询的字面稀缺度

能进前 10 的词，形态高度一致：

| 查询 | 展示 | 位置 |
|---|---:|---:|
| saily esim canada | 519 | 9.9 |
| saily canada | 2 | 2 |
| saily esim korea | 4 | 5 |
| saily esim south korea | 3 | 5.33 |
| esim comparison south africa | 4 | 5.5 |
| airalo prices | 3 | 6 |
| roamic saudi arabia | 1 | 6 |
| saily esim canada price | 1 | 8 |
| saily vs alosim | 9 | 8.89 |
| saily coupon code | 2 | 9.5 |
| holafly esim egypt | 2 | **1** |
| brazil iot sim card plan lte-m cat-m1 monthly cost claro vivo tim 2025 2026 | 2 | **2** |
| unilink esim app price saudi arabia 5 days 7 days kgs review screenshot | 1 | **4** |

对照**排不动的**：

| 查询 | 展示 | 位置 |
|---|---:|---:|
| best esim for asia | 15 | 81.67 |
| best esim for south africa | 14 | 59.5 |
| best esim for egypt | 11 | 80.91 |
| esim colombia | 34 | 92.35 |
| colombia esim | 10 | 97.4 |
| esim croatia | 13 | 87.85 |
| best esim for poland | 6 | 72.5 |
| best esim for europe | 2 | 86.5 |

**规律**：只要「全世界只有我们有这一页」，就进前 10；只要「已有上千页在抢」，就掉到 60–100。

`/compare/<国>/<品牌>/` 恰好是前者（我们为每个「品牌 × 国家」都单独建了页），而 `best esim for X` / `esim <国>` 是后者。

数量化佐证：

| 查询子集 | 条数 | 展示 | 位置中位 |
|---|---:|---:|---:|
| 含品牌名 | 145 | 916 | **29** |
| 不含品牌名 | 242 | 632 | **80** |
| 其中商业意图词（best/cheap/cheapest/unlimited/compare/vs） | 143 | 414 | **78**（仅 4 条 ≤30） |

### 诊断 B｜CTR 塌陷有明确的机械原因

`/compare/canada/saily/` 的 SERP 摘要（产物原文）：

```
eSIM Sift compares Saily eSIM plans for Canada: 11 plans from $5.29,
best $2.20/GB (#9 of 10) — ranked against 221 Canada plans.
```

**「(#9 of 10)」是自我否定。** 搜 `saily esim canada` 的人想看 Saily，我们只告诉他一件事：这牌子在 10 家里排第 9。

全站扫描结果：

```
描述里含「#N of M」的排列页 = 449 / 499   （90%）
模板命中统计：327 次同一个模板
  eX X compares X eX plans for X: N plans from $N, best $N/X (#N of N) — ranked against N X plans.
```

⇒ 这是**模板级**缺陷，不是个别页。

**其它「位置够好、0 点击」且展示量够大的页**：

| 页面 | 展示 | 位置 |
|---|---:|---:|
| /compare/canada/saily/ | 532 | 10.86 |
| /networks/ | 105 | 4.43 |
| /compare/ireland/saily/ | 41 | 18.05 |
| /networks/united-states/ | 38 | 4.18 |
| /compare/united-states/ | 31 | 6.45 |
| /networks/netherlands/ | 26 | 15.15 |

（完整 44 页清单见脚本输出；7 天可挽回点击估算 ≈ 44，而全站真实点击 = 6。）

### 诊断 C｜内容投入与排名能力**完全错配**

| 内容型 | 总页数 | 有展示 | 展示 | 中位位置 | 判断 |
|---|---:|---:|---:|---:|---|
| **networks 国家子页** | 12 | 10 | 168 | **15.2** | ★ 唯一被验证的赢家 |
| research | 3(+hub) | 4 | 43 | 33.8 | ★ 好 |
| esim-providers 品牌 hub | 10 | 9 | 153 | 29.3 | 尚可 |
| country hub | 50 | 49 | 863 | 46.3 | 中游，展示第二大 |
| perm 排列页 | 499 | 132 | **1182** | 77.8 | 展示最大，靠极少数撑 |
| vs 对决页 | 45 | 15 | 143 | **96.0** | 差（30/45 页零展示） |
| **guides** | 10 | 8 | 140 | **110.2** | ★ 最差，却是投入最重的内容 |

看具体行：

- `/guides/best-asia-esim/` 55 展示 @82.76
- `/guides/best-africa-middle-east-esim/` 12 @**143.42**
- `/guides/esim-vs-physical-sim/` 10 @**167.2**
- `/guides/how-to-install-esim/` 11 @110.18
- 反过来：`/research/esim-price-index/` 12 @20.5 · `/research/unlimited-esim/` 17 @33.76 · `/networks/` 105 @4.43

⇒ **站点的比较优势是「我们手里有别人没有的数据」（9095 条套餐、$/GB、Opensignal/Ookla），不是「我们会写 best-eSIM 导购」。现在资源投反了。**

---

## 3. 优化方案（按 ROI 排序）

### P0 · 排列页 SERP 摘要重写 —— 本周可做，影响 40% 展示

- **范围**：499 个 `/compare/<国>/<品牌>/` 页的 `<title>` + `<meta description>`
- **改法（三处）**：
  1. **删掉 `(#N of 10)`**，或只在该品牌真的好时才用正向表述（"2nd-cheapest of 10"）
  2. **把「时长档」写进 title** —— 数据里 `saily esim canada 15 days price` 已经排到第 6，但我们没有页面把「15 天」放进标题
  3. **把 `eSIM Sift compares` 这种品牌自述换成读者要的信息**（计划数 / 起价 / 天数区间 / 热点规则）
- **示例**（`/compare/canada/saily/`）：
  - title：`Saily Canada eSIM: 11 Plans, 7–30 Days, From $5.29`
  - desc：`All 11 Saily plans for Canada side by side — 7, 15 and 30-day bundles from $5.29. See the cheapest Saily tier for your trip length, and how it stacks up against the other 9 providers on $/GB.`
- **预期**：canada/saily 的 CTR 从 **0% → 1.5–2%**，即 **+8–10 点击/周**（当前全站 6 点击/周）
- **施工纪律**：动 499 页产物 ⇒ 必须完整构建 + `--diff` + 基线刷新；**不得改数据、不得动 `checked` 日期**

> ### ✅ 执行结果（2026-10-12 第八十五轮，用户指令「P0-P1 全部优化」）
>
> **用户对 P0 的口径修正（逐字）**：`守卫 verify_provider_pages.py 里有 TITLE_BANNED 硬规则：标题里禁止出现 $ 和「N plans」 这个废除。description 重写`
> ⇒ 上面「示例」里建议的 `Saily Canada eSIM: 11 Plans, 7–30 Days, From $5.29` **正是原 TITLE_BANNED 要拦的形状**，用户明确废除该规则**采用它**。
>
> | 项 | 结果 |
> |---|---|
> | `TITLE_BANNED` | **已废除**（删 3 条正则 + 检查循环）。代价已知并接受：标题由构建期现算 ⇒ **每次数据变动都会改标题** |
> | `(#N of M)` | 998 页（en 499 + de 499）命中 **→ 0** |
> | title（新增 `seo.title`） | en `44–54: 499/499` · de `44–54: 499/499`，**零重复**，必含国名 |
> | description | en/de **双向 499/499 落在 120–140**，**零重复**，必含 `eSIM Sift` |
> | 模板改动 | **零**（走 `head.html` 已有的 `$lockedTitle` 锁） |
> | 归属证明 | 旧产物 vs 基线 **1291/1291 全等**；新 vs 旧 = **998 个排列页 × 每页恰好 4 行**（`<title>`/desc/og:title/og:description），其余 **0 字节**变化 |
> | 顺带 | 拆掉 `gen_provider_pages.py` 的 `NOINDEX = LANG != "en"`（否则下次重跑会复活 499 个德语页的 noindex）+ 清 499 个德语 md 的过期 `TODO(de)` |
>
> **⚠ 未修（本轮明确只改 `<title>` + `<meta description>`）**：正文里另有**三处同款自我否定** ——
> ① `compare_provider__verdict_met_rank` 印 `… rank #9 of 10 …`；② FAQ 答案 / JSON-LD `compare_provider__faq_a_price_met` 印 `… ranks #9 of 10 providers we track for this destination.`；
> ③ 产物含 `of 10` 的页 = en `compare` **511** + de `compare` **540**（另 networks / esim-providers / esim-deals / guides 若干）。
> **Google 会从正文抽摘要 ⇒ 只改 meta 的修复是半残的**，建议紧随其后单独一轮处理。

### P1 · 放大已验证的赢家：networks 从 12 → 50 国

- 现在 12 个子页，中位位置 **15.2**；`/networks/` 枢纽 105 展示 @4.43
- 对应查询：`mobile operators netherlands` / `mobile operators thailand` / `kt vs lg u+` / 德语 `welche lokalen netze nutzt saily in taiwan?`（位置 7）
- 数据源已有（`data/carriers.toml` + Opensignal/Ookla），只是页数没铺开
- **风险最低、ROI 最高的一步**

> ### ⚠ 证据更正 + 执行结果（2026-10-12 第八十五轮）
>
> **用户选定**：`先做证据最强的 12 国`（Colombia 79 · Croatia 55 · South Africa 50 · Egypt 37 · Taiwan 25 · Vietnam 25 · Morocco 25 · Kenya 25 · Poland 17 · Georgia 17 · Switzerland 15 · Saudi Arabia 12，合计 382 展示）
>
> **必须更正上面两处表述**：
> 1. 「对应查询：`mobile operators netherlands` …」—— 本轮把 xlsx 里「网络 / 运营商意图」的查询全部提出来复算，**7 天全站只有 8 条、合计 8 次展示**，其中 2 条还是已覆盖国家。⇒**现有 12 个子页的 168 展示无法归因到这批意图词**；「放大已验证的赢家」站得住的是**页型实测表现**（12 页中位 15.2），不是「网络意图词有量」。
> 2. 「数据源已有」—— 准确说法是：**素材**已有（profiles / Opensignal / Ookla 都在 `data/` 里），但**德语覆盖层**与**逐页正文**要单独产出，单位成本是**一篇 13–17KB 的手写深度页 / 国 / 语言**。
>
> **★ 目标 12 国的数据就位度（实测，非推测）**：
> | 检查项 | 结果 |
> |---|---|
> | `data/carriers.toml` profiles | **50 国全有**（12 国全中） |
> | `data/networkreports.toml`（英语报告） | **47 国**，缺 `IS` `GE` `KE` ⇒ **Georgia 与 Kenya 没有「独立实测」事实源，不能编** |
> | `data/de/networkreports.toml`（德语覆盖） | CO/HR/ZA/EG/TW/VN/MA/PL/CH/SA **10 国就位** |
> | 首屏配图 + 邻国配置 | 12 国全有 4 张图 |
>
> **本轮进度**：首批 **3 国（Colombia / Croatia / South Africa，184 展示 = 12 国的 48%）已完成 en + de**（6 个新文件，每页含 8 条带真实数字的 FAQ + 3 城市覆盖实况），事实**全部外部核实**。
> **剩余**：EG / TW / VN / MA / PL / CH / SA **7 国**（数据已齐） + **GE / KE 2 国阻塞**（缺英语网络报告，需先补 `data/networkreports.toml` 的英文条目并找到可核实来源，或改用「无报告」变体版式 —— 后者属**版式变更，需用户点头**）。

> **✅ P1 首批归属证明（2026-10-12 第八十五轮 · 构建 2）**
>
> 构建 `BUILD_EXIT=0`（9m26s）· **1297 pages**（1291 + 6）· 13 道产物闸门 + 5 道源码闸门全绿（hreflang 3882 标签 / 1294 页 · 品牌×国家子页 · R10/R11 骨架不重复 · 语言闸门）。
>
> **产物断言**（`.buildlog/r85_p1_verify.py`）：6 页 × A–H 全过 —— `<title>`/`og:title` == front matter 的 `seo.title`、`description`/`og:description` == `description`（**逐字**，非"产物==产物"空断言）；hreflang 三向自洽（`en-us`/`de-de`/`x-default`）互指同 slug；canonical 自指；**日期三处同源 = sitemap lastmod = 2026-10-07（数据核对日，非 front matter 的 2026-10-12、非构建日）**；德语页用德语国名。
>
> **归属法 v3**（`.buildlog/r85_p1_attrib3.py`）：新增 **6** / 删除 **0** / 共有 **1291** = **1223 页逐字节不变 + 68 页可归因**（66 个新国 `compare/<国>/*` 内链升级 + `/networks/`·`/de/networks/` 索引新增卡片）；**越界 0**；每页计数**恰好一处** +3（12 → 15，其余 13/18/8/8/3/6 纹丝不动）；998 个排列页 = **938 逐字节不变 + 60（全为新国）内链升级** ⇒ **零误伤**。基线已 `--write-manifest` 前进到 **1297 文件**。
>
> **⚠ 新增的一条成本事实**：`/networks/<slug>/` 一旦存在，模板会**自动**把该国 `compare/` 页指向 `/networks/` 索引的说明句升级为指向该页的内链 ⇒ **每新增 1 国 = 全站 1297 页导航重生成 + 该国 22 个 compare 页内链升级**（见 `PROJECT.md` 红线 115）。

### P2 · 开「多品牌对比」页型

- 证据：`compare saily, nomad et yesim` @7.17 · `compare saily vs nomad vs yesim` @8 · `saily vs alosim` @8.89 —— 用户已经在用这种写法，而且我们能排
- 现状只有两两对决（45 页，中位 96）
- 建议先做 15–20 个「按需求挑选」的三品牌组合页（C(10,3)=120，不要一次全出）
- ⚠️ 开新页型属架构变更，**需要你点头**

### P3 · 「价格与折扣」专题（竞品空白、转化最高）

- 证据：`saily coupon code` @9.5 · `holafly discount code` @8 · `saily free` @10.5 · `saily pricing` @26 · `airalo prices` @6 · `ubigi price` @7 · `yesim cost` @6 · `esim pris`(SV) @9
- 动作：品牌 hub 加「价格档位表」+ `Offer` / `PriceSpecification` 结构化数据；可考虑「eSIM 折扣码」聚合页
- ⚠️ 合规：只写可核实的官方价，不编造折扣码

### P4 · 德语站真正上线（纯增量）

- `/de/` 在全站导出里只有 **1 页**有展示（6 展示 @4.5）
- 但德语需求已经打到**英文页**上：
  - `vergleiche saily, nomad und yesim` @**8.33**
  - `welche lokalen netze nutzt saily in taiwan?` @**7**
  - `beste esim südafrika` @68.67 · `esim kroatien` @89.25 · `roamic bewertung` @83
- 另有：法语 `esim colombie` @88.75 · 西语 `mejor esim para colombia` @86 · 瑞典语 `esim pris` @9 · 波兰语 `esim filipiny` @91 · 印尼语 `esim terbaik indonesia` @77 · 阿拉伯语 @74 —— 共 **14 条非英文查询**
- ⇒ 德语页索引 = 直接接住这批需求，且不与英文页互抢

### P5 · 明确的「不投」清单（省下时间）

- `best esim for X` 全系列（中位 78）
- `esim <国>` 全系列（colombia 92 / croatia 88 / south-africa 59 …）
- 通用信息词（`what is esim` 94 · `install esim` 90 · `how to install esim` 110）
- 品牌导航主词（`saily.com` 5.83 · `airalo` 19.67 · `holafly` 37.08）—— 用户就是要去官网，拿不到点击

---

## 4. 长尾词作战表

### A 层｜已经在赢 → 加固（改摘要、加时长档、加结构化数据）

`saily esim canada` · `saily esim korea` · `saily esim south korea` · `saily canada` · `saily italy` · `saily esim japan` · `saily esim costa rica` · `holafly esim egypt` · `holafly iceland` · `airalo prices` · `airalo taiwan esim` · `ubigi price` · `ubigi peru` · `yesim cost` · `roamic nederland` · `roamic saudi arabia` · `esim comparison south africa` · `saily coupon code` · `holafly discount code`

### B 层｜40–60 名，推一把能进前 30

| 查询 | 展示 | 位置 | 备注 |
|---|---:|---:|---|
| best esim for kenya and tanzania | 18 | 48.11 | **多国组合**词，明显好于单词的 78 |
| airalo esim argentina | 7 | 36.29 | |
| ubigi korea | 6 | 32.33 | |
| roamic review | 5 | 27 | |
| saily pricing | 15 | 26 | |
| holafly vs saily | 4 | 37 | |
| best esim for iceland 2026 | 1 | 43 | 样本仅 1 次，方向参考：加年份后比 `best esim for iceland`（68）前进 25 位 |

### C 层｜60–100 死区 → 不投

`holafly vs airalo`（41 展示 @70.6，是展示量最大的对决词，也是最卷的）· `best esim for X` 全系列 · `esim <国>` 全系列

---

## 5. 复测口径（2–4 周后）

1. **先修导出**：重导一次，确认「查询表展示 = 网页表展示」
2. 看三个数：
   - `/compare/canada/saily/` 的 CTR（0% → ?）
   - 位置 10–20 那 20 页的点击（0 → ?）
   - 非品牌商业词的位置中位数（78 → ?）
3. **重要时序提醒**：本数据窗口是 **10-05 ~ 10-12**，而 10-11 提交的 `closestmatchups`（国家页对决入口）+ `fityour`（对决页分档段）**尚未反映在这份数据里**。那批改动要等下一个窗口才能评。

---

## 6. 本轮做了什么 / 没做什么

**做了**：只读复算脚本 `.buildlog/r84_gsc_analysis.py` + 本文件。
**没做**：没有改任何源码、数据、模板；没有动 `checked` 日期；没有提交。
