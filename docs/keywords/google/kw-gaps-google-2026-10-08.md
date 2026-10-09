# eSIM 长尾关键词 · Google 官方通道采集 + 缺口分析

**日期**：2026-10-08　**站点**：esimsift.com（已上线）　**词数**：11454

**数据源**：Google（两条官方通道）

- Google Suggest 补全 —— `suggestqueries.google.com/complete/search`，种子 6977 个（成功 6976，失败 1），市场 en-US、en-GB、en-SG、en-AU、de-DE
- Google Trends 相关查询 —— `trends.google.com/trends/api/widgetdata/relatedsearches`，种子 **181** 个（本次新跑 61 + 合并早前 120）；另有多次查询的批量比较（`multiline`）用于跨词热度，见 §3.5。

> 上一版（2026-10-08 早）用的是 **Bing 补全**。本版按用户要求换成 Google，并新增 Trends 指数维度。两版数据都保留，可互为对照（见 §八）。

---

## 一、口径：这一版的「需求」由什么支撑

### 1.1 三路证据

| 字段 | 来源 | 含义 |
|---|---|---|
| `sources` | Suggest | 有多少个不同种子把这个词带出来（跨语境广度） |
| `中位位次` | Suggest | 在所有带出它的种子里，它在补全列表的中位排名（1 = 最热） |
| `google指数` | **Trends** | **Google 官方的相对搜索指数（0-100）** —— 数值，不是位次 |
| `上升信号` | **Trends** | 该词的上升幅度（`+250%` / `Breakout`），代表**正在涨**的需求 |
| `补全分` | Suggest | 只用补全证据算的 0-100 分 |
| `综合分` | 两者 | `指数存在时 = 0.55×指数 + 0.30×广度 + 0.15×深度`；否则 `0.55×广度 + 0.45×深度` |

### 1.2 这是搜索量吗 —— 不是；而且 `google指数` **不能跨词比大小**

**`google指数` 是 Google Trends 的官方数值**，取值 0-100，但它的含义是「该查询**在它自己**的 12 个月时间序列里的相对位置」（100 = 该词自己的峰值）。于是 `esim` 的 100 和某个长尾词的 100 **是两码事** —— **这个字段只能同一批内互比，不能跨词定序**。本报告只用它做两件事：① 标记「这个词达到了 Trends 的返回门槛」；② 参与 `综合分`。

⚠️ **要拿到真正跨词可比的热度，必须做 Trends 批量比较 + 锚词归一**（每批固定带锚词 `esim`，取「均值比」），结果见 **§3.5**。**只看 `google指数` 的大小来排优先级是错的。**

要拿到绝对搜索量，只有 **Google Search Console**（本站自己的真实曝光/点击）或付费工具（Ahrefs/Semrush）。本机插件市场已核查：**无任何可用的关键词搜索量连接器**。所以本报告不出现任何「月搜索量 1,200」这类编造数字 —— 那种数字无法复核，比没有更糟。

### 1.3 ⚠️ 补全证据 ≠ 真实热度：一个反例

有 `google指数` 的词 69 个，没有的 11385 个。两类**不可直接比高低** —— Trends 只对达到一定体量的查询返回数据，长尾词天然没有指数。排序时请**同时看 `google指数` 与 `证据` 两列**。

但更要紧的是：**补全广度 ≠ 真实热度，而且 `综合分` 会把两者排反**。批量比较（§3.5）量出的硬反证：

| 词 | `sources`（补全广度） | `综合分` | 跨词可比相对热度（锚词 `esim` = 1） |
|---|---|---|---|
| `is esim available in portugal` | **51** | **88.8**（全站仅 17 个词 ≥ 88.8） | **0.0000**（低于 Trends 分辨率） |
| `best esim for japan` | **1** | 69.5 | **0.0054** |

**综合分高出 19.3 分的那个词测不到热度，低 19.3 分的那个测得到。** 逐条查原始补全数据后，两个 `sources` 的来历完全不同：

- `is esim available in portugal` 被 **51 个种子**带回，来源横跨葡萄牙、克罗地亚、西班牙、土耳其/希腊、巴西 —— 它是补全引擎给**一大批国家种子**都挂上的**通用问句模板**，不是某个具体的搜索需求。
- `best esim for japan` 被 **1 个种子**带回，而且那个种子是 `best esim` ——**如果我当初没撒这个种子，日本页最有价值的词根本不会出现在数据集里。**

→ **`sources` 低不是「没人搜」，而是「我没撒对种子」；`sources` 高也可能只是「句式通用」。**发现词靠补全，排优先级靠 §3.5 的热度 —— **两者冲突时，信热度。**

---

## 二、采集通道（可复现）

### 2.1 本机网络事实（实测）

| 观察 | 结论 |
|---|---|
| `curl https://www.google.com/` 超时 | 直连不可用 |
| `nslookup www.google.com` → `31.13.92.37` | **DNS 污染**（那是 Facebook 的 IP 段） |
| 环境变量 `https_proxy=http://127.0.0.1:62216` | **沙箱代理，不通 Google** —— 而且 curl 默认读它，会让所有请求静默失败 |
| `127.0.0.1:7890`（本机 Clash 混合端口） | **可通 Google** —— 脚本必须显式指定 `--proxy` |

**这一条是最容易踩的坑**：不显式指定代理时，请求会继承环境变量里的沙箱代理并**全部失败**，而失败现象是「空响应」而不是报错 —— 很容易被误判成「Google 没有补全」。

### 2.2 为什么这次换成 Google

两个原因：**用户要求**，以及 **Google Trends 能给出热度数值**（Bing 通道完全没有这个维度）。

**顺带更正上一版报告里的一处不准确论断。** 上一版写「Bing 会往几乎所有 eSIM 查询里注入同一段通用热门块」。本轮做了对照实测 —— 取 6 个互不相关的种子，分别向两个引擎取补全，算两两 Jaccard 重叠率：

| 引擎 | 平均重叠率 | 最大重叠率 | 被 ≥3 个互不相关种子共同带出的词 |
|---|---|---|---|
| Google | 0.000 | 0.000 | 0 个 |
| Bing | 0.000 | 0.000 | 0 个 |

**两个引擎都不存在全局通用块** —— 上一版的论断是错的。

真相是**地理簇内共享**：上一版里 `buy esim for dubai` 的 57 个来源种子，逐条查过，**全部**是中东相关种子（`saudi arabia` / `united arab emirates` / `qatar` / `israel` / `middle east`），**不是**「毫不相关的种子」。

所以正确结论是：**`sources` 在种子密集的语境里会饱和**（一个国家有 20+ 个种子时，该国会被大量带出），这是一切补全引擎的共性，不是 Bing 的缺陷。上一版据此推出的「改用 Google 就不会有这个问题」也是错的 —— 本版仍保留「覆盖国数」这个判别字段，就是因为它对两个引擎都必要。

### 2.3 请求规模与稳定性

| 项 | 值 |
|---|---|
| Suggest 种子 | 6977（成功 6976 / 失败 1） |
| Trends 种子 | 181（本次 61 + 合并 120） |
| 并发 | Suggest 12 / Trends 2（Trends 限速严格，必须低并发 + 指数退避） |
| Suggest 限速 | 连发 40 次：36 次 200、4 次超时、**0 次 429** |
| Trends 限速 | **429 非常频繁**（约每 2-3 个请求一次）→ 指数退避 6/12/24/48s 可稳定穿透 |

---

## 三、需求全景

### 3.1 词型分布

| 词型 | 词数 | 综合分中位 | 综合分最高 | 有指数 |
|---|---|---|---|---|
| 国家·核心 | 3240 | 35.1 | 88.8 | 30 |
| 品牌×国家 | 1481 | 35.1 | 69.5 | 9 |
| 区域 | 1273 | 31.4 | 85.0 | 6 |
| 城市 | 965 | 32.8 | 49.1 | 0 |
| 国家·价格/交易 | 887 | 35.1 | 70.9 | 0 |
| 国家·规格/流量 | 856 | 37.0 | 52.8 | 4 |
| 品牌（全局） | 744 | 31.4 | 100.0 | 13 |
| 通用·其他 | 544 | 35.1 | 88.8 | 3 |
| 国家·设备兼容 | 241 | 35.1 | 49.8 | 0 |
| 通用·问题 | 203 | 35.1 | 88.8 | 0 |
| 通用·设备兼容 | 176 | 35.1 | 88.8 | 1 |
| 通用·规则/规格 | 169 | 35.1 | 47.8 | 0 |
| 通用·价格交易 | 158 | 32.1 | 88.8 | 2 |
| 国家·落地渠道 | 157 | 31.4 | 47.8 | 0 |
| 国家·对比 | 129 | 42.6 | 46.4 | 0 |
| 国家·网络覆盖 | 76 | 42.6 | 46.4 | 0 |
| 通用·全球 | 74 | 34.1 | 88.8 | 1 |
| 通用·对比 | 63 | 34.5 | 88.8 | 0 |
| 品牌对决 | 18 | 36.0 | 46.4 | 0 |

### 3.2 站内承接现状

| 站内现状 | 词数 | 综合分中位 |
|---|---|---|
| 已覆盖 | 9564 | 35.1 |
| 缺口 | 1890 | 32.8 |

⚠️ **「已覆盖」的判定比字面宽松，必须读清楚**：它只表示「该词的主干意图已有页面承接」（例如 `{country}` 词 → 该国 `/compare/{country}/` 存在；`{A} {country}` 词 → 子页存在）。它**不代表**该词有专门内容。

举例：`jetpac esim costa rica review` 落进「已覆盖」，是因为 `/compare/costa-rica/jetpac/` 存在 —— 但那个页承接的是「价格/套餐」意图，**不是**「review」意图。所以「已覆盖」这一列不可当作「这个词已经做好了」来读；真正需要动作的是**缺口**那一列，以及已覆盖词里的**意图错配**（本报告未逐词审）。

### 3.3 旧词库覆盖

- 在旧矩阵（`keyword-matrix.csv`）= 否：**11230** 词（98.0%）
- 在旧矩阵（`keyword-matrix.csv`）= 是：**224** 词（2.0%）

### 3.4 各词型的头部词（综合分 Top 8）

⚠️ **综合分跨词型不可直接比** —— 通用词被上百个种子带出，`sources` 天然高于长尾词，这反映的是「查询普遍性」而不是「商业价值」。所以必须**分型看**：通用词对应枢纽/指南页，国家词对应国家页，品牌×国家词对应子页。

⚠️⚠️ **而且 `综合分` 本身只是「补全证据」的排序，不是热度排序** —— §3.5 的批量比较已证明它会**把词排反**（`is esim available in portugal` 综合分 88.8，实测热度 **0.0000**；`best esim for japan` 综合分 69.5，实测热度 **0.0054**）。本节的表请当作「**词型内部有哪些词**」来读，**不要**当作排期依据；排期请用 §3.5 里测到非零热度的词。

**国家·核心**（3240 词 · 中位 35.1）

| 综合分 | 指数 | 上升 | 站内 | 词 |
|---|---|---|---|---|
| 88.8 | - |  | 已覆盖 | `is esim available in portugal` |
| 85.0 | - |  | 已覆盖 | `is esim available in philippines` |
| 85.0 | - |  | 已覆盖 | `is there an esim in the philippines` |
| 82.9 | - |  | 已覆盖 | `is esim available in egypt` |
| 82.9 | - |  | 已覆盖 | `is esim available in kenya` |
| 82.9 | - |  | 已覆盖 | `is esim available in saudi arabia` |
| 82.2 | - |  | 已覆盖 | `does esim work in china` |
| 79.5 | - |  | 已覆盖 | `is esim available in australia` |

**品牌×国家**（1481 词 · 中位 35.1）

| 综合分 | 指数 | 上升 | 站内 | 词 |
|---|---|---|---|---|
| 69.5 | 100 | +550% | 已覆盖 | `saily esim canada` |
| 47.8 | - |  | 已覆盖 | `airalo esim uae reddit` |
| 47.8 | - |  | 已覆盖 | `does nomad esim work in new zealand` |
| 47.8 | - |  | 已覆盖 | `does saily esim work in costa rica` |
| 47.8 | - |  | 已覆盖 | `does saily esim work in south africa` |
| 47.8 | - |  | 已覆盖 | `jetpac esim costa rica review` |
| 47.8 | - |  | 已覆盖 | `nomad esim reddit canada` |
| 47.8 | - |  | 已覆盖 | `roamic esim discount code uk` |

**区域**（1273 词 · 中位 31.4）

| 综合分 | 指数 | 上升 | 站内 | 词 |
|---|---|---|---|---|
| 85.0 | - |  | 已覆盖 | `esim providers in europe` |
| 49.1 | - |  | 缺口 | `esim for austria and germany` |
| 48.1 | - |  | 缺口 | `uae and qatar esim` |
| 47.8 | - |  | 缺口 | `best esim for australia and new zealand reddit` |
| 47.8 | - |  | 缺口 | `best esim for belgium and netherlands` |
| 47.8 | - |  | 缺口 | `best esim for croatia and italy` |
| 47.8 | - |  | 缺口 | `best esim for fiji from australia` |
| 47.8 | - |  | 缺口 | `best esim for hong kong and china` |

**城市**（965 词 · 中位 32.8）

| 综合分 | 指数 | 上升 | 站内 | 词 |
|---|---|---|---|---|
| 49.1 | - |  | 缺口 | `bogota airport esim` |
| 49.1 | - |  | 缺口 | `esim brussels airport` |
| 49.1 | - |  | 缺口 | `esim rio de janeiro` |
| 49.1 | - |  | 缺口 | `esim riyadh airport` |
| 49.1 | - |  | 缺口 | `macau esim unlimited data` |
| 48.1 | - |  | 缺口 | `esim rio de janeiro reddit` |
| 47.8 | - |  | 缺口 | `barcelona esim card` |
| 47.8 | - |  | 缺口 | `best esim for auckland` |

**国家·价格/交易**（887 词 · 中位 35.1）

| 综合分 | 指数 | 上升 | 站内 | 词 |
|---|---|---|---|---|
| 70.9 | - |  | 已覆盖 | `cheapest esim canada` |
| 64.0 | - |  | 已覆盖 | `esim price usa` |
| 63.4 | - |  | 已覆盖 | `cheapest esim singapore` |
| 60.6 | - |  | 已覆盖 | `cheapest esim plan singapore` |
| 59.9 | - |  | 已覆盖 | `cheapest us esim` |
| 58.9 | - |  | 已覆盖 | `cheapest esim plan canada` |
| 55.8 | - |  | 已覆盖 | `cheapest esim plan usa` |
| 49.1 | - |  | 已覆盖 | `cheapest esim argentina reddit` |

**国家·规格/流量**（856 词 · 中位 37.0）

| 综合分 | 指数 | 上升 | 站内 | 词 |
|---|---|---|---|---|
| 52.8 | - |  | 已覆盖 | `esim australia unlimited data` |
| 51.9 | - |  | 已覆盖 | `esim czech republic unlimited data` |
| 49.1 | - |  | 已覆盖 | `esim croatia unlimited data` |
| 49.1 | - |  | 已覆盖 | `unlimited data colombia esim` |
| 48.1 | - |  | 已覆盖 | `best esim for czech republic unlimited data` |
| 48.1 | - |  | 已覆盖 | `egypt esim unlimited data reddit` |
| 48.1 | - |  | 已覆盖 | `netherlands esim unlimited data reddit` |
| 47.8 | - |  | 已覆盖 | `esim austria unlimited data` |

**品牌（全局）**（744 词 · 中位 31.4）

| 综合分 | 指数 | 上升 | 站内 | 词 |
|---|---|---|---|---|
| 100.0 | - |  | 已覆盖 | `yesim esim prices` |
| 92.5 | - |  | 已覆盖 | `ubigi esim price` |
| 88.8 | - |  | 已覆盖 | `ubigi esim plans` |
| 88.0 | - |  | 已覆盖 | `yesim esim review` |
| 85.0 | - |  | 已覆盖 | `how does airalo esim work` |
| 73.0 | 100 |  | 已覆盖 | `roamic esim reviews` |
| 70.8 | 100 |  | 已覆盖 | `jetpac esim review` |
| 70.8 | 100 | +90% | 已覆盖 | `saily esim review` |

**通用·其他**（544 词 · 中位 35.1）

| 综合分 | 指数 | 上升 | 站内 | 词 |
|---|---|---|---|---|
| 88.8 | - |  | 已覆盖 | `esim phone plans` |
| 88.8 | - |  | 已覆盖 | `esim size` |
| 85.0 | - |  | 已覆盖 | `esim explained` |
| 85.0 | - |  | 已覆盖 | `esim requirements` |
| 75.0 | - |  | 已覆盖 | `esim prepaid plans` |
| 67.6 | 100 |  | 已覆盖 | `best esim for turkey` |
| 66.4 | - |  | 已覆盖 | `esim review` |
| 65.4 | - |  | 已覆盖 | `esim country list` |

**国家·设备兼容**（241 词 · 中位 35.1）

| 综合分 | 指数 | 上升 | 站内 | 词 |
|---|---|---|---|---|
| 49.8 | - |  | 已覆盖 | `esim compatible phones australia` |
| 46.5 | - |  | 已覆盖 | `esim compatible phones canada` |
| 46.4 | - |  | 已覆盖 | `best esim fiji for iphone` |
| 46.4 | - |  | 已覆盖 | `best esim for germany iphone` |
| 46.4 | - |  | 已覆盖 | `best esim italy for iphone` |
| 46.4 | - |  | 已覆盖 | `brazil esim for iphone` |
| 46.4 | - |  | 已覆盖 | `china esim iphone 16` |
| 46.4 | - |  | 已覆盖 | `colombia esim for iphone` |

**通用·问题**（203 词 · 中位 35.1）

| 综合分 | 指数 | 上升 | 站内 | 词 |
|---|---|---|---|---|
| 88.8 | - |  | 已覆盖 | `can esim be used internationally` |
| 88.8 | - |  | 已覆盖 | `can i get an esim` |
| 88.8 | - |  | 已覆盖 | `how to apply for an esim` |
| 88.8 | - |  | 已覆盖 | `which is the best esim` |
| 85.0 | - |  | 已覆盖 | `can i use data from esim` |
| 85.0 | - |  | 已覆盖 | `does esim work internationally` |
| 85.0 | - |  | 已覆盖 | `which network has esim` |
| 78.1 | - |  | 已覆盖 | `which provider has esim` |

**通用·设备兼容**（176 词 · 中位 35.1）

| 综合分 | 指数 | 上升 | 站内 | 词 |
|---|---|---|---|---|
| 88.8 | - |  | 已覆盖 | `esim iphone how many` |
| 63.9 | 100 |  | 已覆盖 | `esim iphone` |
| 61.2 | - |  | 已覆盖 | `countries that support esim iphone` |
| 58.5 | - |  | 已覆盖 | `how to get esim for iphone` |
| 54.0 | - |  | 已覆盖 | `can you use esim only` |
| 49.2 | - |  | 已覆盖 | `where to buy esim for iphone` |
| 46.8 | - |  | 已覆盖 | `esim not working iphone 12` |
| 46.4 | - |  | 已覆盖 | `esim esim iphone` |

**通用·规则/规格**（169 词 · 中位 35.1）

| 综合分 | 指数 | 上升 | 站内 | 词 |
|---|---|---|---|---|
| 47.8 | - |  | 已覆盖 | `esim turkey unlimited data` |
| 46.4 | - |  | 已覆盖 | `best esim for hotspot tethering` |
| 46.4 | - |  | 已覆盖 | `esim america unlimited data` |
| 46.4 | - |  | 已覆盖 | `esim brasil 10gb` |
| 46.4 | - |  | 已覆盖 | `esim free trial 1gb` |
| 46.4 | - |  | 已覆盖 | `esim hotspot device` |
| 46.4 | - |  | 已覆盖 | `esim indonesien 10gb` |
| 46.4 | - |  | 已覆盖 | `esim italia 10gb` |

**通用·价格交易**（158 词 · 中位 32.1）

| 综合分 | 指数 | 上升 | 站内 | 词 |
|---|---|---|---|---|
| 88.8 | - |  | 已覆盖 | `cheap esim data plans` |
| 88.8 | - |  | 已覆盖 | `cheapest esim data plan` |
| 86.9 | - |  | 已覆盖 | `esim cheapest plan` |
| 85.0 | - |  | 已覆盖 | `esim price` |
| 79.5 | - |  | 已覆盖 | `does telcel offer esim` |
| 79.5 | - |  | 已覆盖 | `esim cheap plans` |
| 74.0 | - |  | 已覆盖 | `how much is an esim plan` |
| 68.0 | 100 |  | 已覆盖 | `cheapest esim phone` |

**国家·落地渠道**（157 词 · 中位 31.4）

| 综合分 | 指数 | 上升 | 站内 | 词 |
|---|---|---|---|---|
| 47.8 | - |  | 已覆盖 | `esim australia sydney airport` |
| 47.8 | - |  | 已覆盖 | `esim japan airport price` |
| 47.8 | - |  | 已覆盖 | `esim ksa for visitors` |
| 46.8 | - |  | 已覆盖 | `taiwan esim unlimited data klook` |
| 46.4 | - |  | 已覆盖 | `australia sim card for tourist at airport` |
| 46.4 | - |  | 已覆盖 | `best esim for vietnam klook` |
| 46.4 | - |  | 已覆盖 | `buy esim hong kong airport` |
| 46.4 | - |  | 已覆盖 | `costa rica airport esim` |

**国家·对比**（129 词 · 中位 42.6）

| 综合分 | 指数 | 上升 | 站内 | 词 |
|---|---|---|---|---|
| 46.4 | - |  | 已覆盖 | `china esim vs sim` |
| 46.4 | - |  | 已覆盖 | `compare esim plans singapore` |
| 46.4 | - |  | 已覆盖 | `esim australia price comparison` |
| 46.4 | - |  | 已覆盖 | `esim china price comparison` |
| 46.4 | - |  | 已覆盖 | `esim egypt price comparison` |
| 46.4 | - |  | 已覆盖 | `esim japan price comparison` |
| 46.4 | - |  | 已覆盖 | `esim morocco price comparison` |
| 46.4 | - |  | 已覆盖 | `esim thailand price comparison` |


### 3.5 跨词可比的 Google 官方热度（Trends 批量比较）

§3.4 的 `google指数` 来自 relatedQueries，是**每个词相对于它自己峰值**的 0-100 值，**不能跨词比较**。要拿到跨词可比的热度，必须用 Trends 的批量比较：把多个词放进同一次查询，再用**锚词 `esim` 归一**（`相对热度 = 均值(词) / 均值(esim)`；锚词 12 个月的真实热度固定，除掉它就能把不同批拉回同一把尺子）。

**本批 90 个词，分 23 批跑**（每批锚词 `esim` + 4 个目标词；Trends 单次比较上限 5 项）。

**锚词自证**：锚词 `esim` 在各批里的批内均值是 **76.55 – 76.57**（几乎不动）——这说明「按批归一化」被锚词除干净了，跨批可比。若锚词在各批漂移很大，本表作废。

⚠️ **本批有 80 / 90 个词（89%）的相对热度是 0.0000** —— 意思是「在整个 12 个月里，Google 几乎把它的每个时间点都四舍五入成 0」，**低于 Trends 的分辨率**，而不是「它和另一个 0 一样热」。只有 **10 个词**测到了非零热度。

| 相对热度 | 目标内指数 | 站内 | 归属页 | 词型 | 词 |
|---|---|---|---|---|---|
| 0.0619 | 100.0 | 已覆盖 | `/` | 通用·价格交易 | `esim price` |
| 0.0182 | 29.4 | 已覆盖 | `/` | 通用·其他 | `esim size` |
| 0.0145 | 23.4 | 已覆盖 | `/` | 通用·其他 | `esim requirements` |
| 0.0059 | 9.5 | 已覆盖 | `/compare/united-states/` | 国家·价格/交易 | `esim price usa` |
| 0.0054 | 8.7 | 已覆盖 | `/compare/japan/` | 国家·核心 | `best esim for japan` |
| 0.0052 | 8.4 | 已覆盖 | `/compare/canada/saily/` | 品牌×国家 | `saily esim canada` |
| 0.0030 | 4.8 | 已覆盖 | `/compare/united-states/` | 国家·核心 | `best esim for usa` |
| 0.0030 | 4.8 | 已覆盖 | `/` | 通用·其他 | `esim phone plans` |
| 0.0012 | 1.9 | 已覆盖 | `/compare/united-kingdom/` | 国家·核心 | `best esim for uk` |
| 0.0007 | 1.1 | 已覆盖 | `/guides/` | 通用·全球 | `esim international number` |
| 0.0000 | 0.0 | 已覆盖 | `/compare/portugal/` | 国家·核心 | `is esim available in portugal` |
| 0.0000 | 0.0 | 已覆盖 | `/compare/philippines/` | 国家·核心 | `is esim available in philippines` |
| 0.0000 | 0.0 | 已覆盖 | `/compare/philippines/` | 国家·核心 | `is there an esim in the philippines` |
| 0.0000 | 0.0 | 已覆盖 | `/compare/egypt/` | 国家·核心 | `is esim available in egypt` |
| 0.0000 | 0.0 | 已覆盖 | `/compare/kenya/` | 国家·核心 | `is esim available in kenya` |
| 0.0000 | 0.0 | 已覆盖 | `/compare/saudi-arabia/` | 国家·核心 | `is esim available in saudi arabia` |
| 0.0000 | 0.0 | 已覆盖 | `/compare/china/` | 国家·核心 | `does esim work in china` |
| 0.0000 | 0.0 | 已覆盖 | `/compare/australia/` | 国家·核心 | `is esim available in australia` |
| 0.0000 | 0.0 | 已覆盖 | `/compare/canada/` | 国家·核心 | `is esim available in canada` |
| 0.0000 | 0.0 | 已覆盖 | `/compare/south-africa/` | 国家·核心 | `is esim available in south africa` |
| 0.0000 | 0.0 | 已覆盖 | `/compare/mexico/` | 国家·核心 | `does esim work in mexico` |
| 0.0000 | 0.0 | 已覆盖 | `/compare/united-arab-emirates/` | 国家·核心 | `is esim available in uae` |
| 0.0000 | 0.0 | 已覆盖 | `/compare/singapore/` | 国家·核心 | `is esim available in singapore` |
| 0.0000 | 0.0 | 已覆盖 | `/compare/ireland/` | 国家·核心 | `is esim available in ireland` |
| 0.0000 | 0.0 | 已覆盖 | `/compare/saudi-arabia/` | 国家·核心 | `best esim for saudi arabia` |
| 0.0000 | 0.0 | 已覆盖 | `/compare/singapore/` | 国家·核心 | `best esim singapore` |
| 0.0000 | 0.0 | 已覆盖 | `/compare/new-zealand/` | 国家·核心 | `is esim available in new zealand` |
| 0.0000 | 0.0 | 已覆盖 | `/compare/italy/` | 国家·核心 | `best esim for italy` |
| 0.0000 | 0.0 | 已覆盖 | `/compare/malaysia/` | 国家·核心 | `best esim for malaysia` |
| 0.0000 | 0.0 | 已覆盖 | `/compare/new-zealand/` | 国家·核心 | `best esim for new zealand` |
| 0.0000 | 0.0 | 已覆盖 | `/compare/malaysia/` | 国家·核心 | `is esim available in malaysia` |
| 0.0000 | 0.0 | 已覆盖 | `/compare/united-arab-emirates/airalo/` | 品牌×国家 | `airalo esim uae reddit` |
| 0.0000 | 0.0 | 已覆盖 | `/compare/new-zealand/nomad/` | 品牌×国家 | `does nomad esim work in new zealand` |
| 0.0000 | 0.0 | 已覆盖 | `/compare/costa-rica/saily/` | 品牌×国家 | `does saily esim work in costa rica` |
| 0.0000 | 0.0 | 已覆盖 | `/compare/south-africa/saily/` | 品牌×国家 | `does saily esim work in south africa` |
| 0.0000 | 0.0 | 已覆盖 | `/compare/costa-rica/jetpac/` | 品牌×国家 | `jetpac esim costa rica review` |
| 0.0000 | 0.0 | 已覆盖 | `/compare/canada/nomad/` | 品牌×国家 | `nomad esim reddit canada` |
| 0.0000 | 0.0 | 已覆盖 | `/compare/united-kingdom/roamic/` | 品牌×国家 | `roamic esim discount code uk` |
| 0.0000 | 0.0 | 已覆盖 | `/compare/spain/roamic/` | 品牌×国家 | `roamic esim reviews spain` |
| 0.0000 | 0.0 | 已覆盖 | `/compare/canada/saily/` | 品牌×国家 | `saily esim canada price` |

⚠️ **怎么读**：`相对热度` 是相对于 `esim` 这个头部词的比值（`esim` = 1.0）。因为 `esim` 是绝对的通用大词，具体查询的比值通常在 0.0x 甚至 0.000x 量级，这是正常的 —— `目标内指数` 列把本表内最热的目标词当作 100，用来在本表内部排序。

---

## 四、逐国需求排名

按「该国高需求词数」排序。`站内` 列来自真实产物目录比对。

### 4.1 Top 30

`高需求词` = 综合分 ≥ **46.4**（全站前 10% 阈值，现算）。

| # | 国家 slug | 高需求词(≥46) | 总词 | 最高分 | 最高指数 | 站内国家页 | 最高分词 |
|---|---|---|---|---|---|---|---|
| 1 | united-states | 38 | 311 | 71.5 | 100 | 有 | best esim for usa |
| 2 | united-kingdom | 37 | 325 | 65.2 | 100 | 有 | best esim for uk |
| 3 | australia | 35 | 215 | 79.5 | 100 | 有 | is esim available in australia |
| 4 | japan | 33 | 276 | 69.5 | 100 | 有 | best esim for japan |
| 5 | singapore | 31 | 161 | 73.6 | 100 | 有 | is esim available in singapore |
| 6 | china | 30 | 201 | 82.2 | 100 | 有 | does esim work in china |
| 7 | philippines | 29 | 154 | 85.0 | 0 | 有 | is esim available in philippines |
| 8 | egypt | 29 | 129 | 82.9 | 0 | 有 | is esim available in egypt |
| 9 | malaysia | 26 | 129 | 67.0 | 100 | 有 | best esim for malaysia |
| 10 | costa-rica | 25 | 74 | 49.1 | 0 | 有 | cheapest esim costa rica reddit |
| 11 | canada | 24 | 207 | 78.1 | 0 | 有 | is esim available in canada |
| 12 | italy | 24 | 149 | 67.0 | 100 | 有 | best esim for italy |
| 13 | thailand | 24 | 213 | 60.8 | 100 | 有 | best esim for thailand |
| 14 | indonesia | 24 | 103 | 59.5 | 100 | 有 | best esim for indonesia |
| 15 | germany | 24 | 116 | 53.0 | 0 | 有 | esim providers in germany |
| 16 | saudi-arabia | 23 | 107 | 82.9 | 100 | 有 | is esim available in saudi arabia |
| 17 | south-africa | 22 | 110 | 76.4 | 100 | 有 | is esim available in south africa |
| 18 | mexico | 22 | 120 | 74.0 | 0 | 有 | does esim work in mexico |
| 19 | new-zealand | 22 | 163 | 69.9 | 100 | 有 | is esim available in new zealand |
| 20 | vietnam | 22 | 179 | 65.1 | 100 | 有 | best esim for vietnam |
| 21 | south-korea | 22 | 149 | 47.8 | 0 | 有 | best esim for seoul korea |
| 22 | portugal | 21 | 87 | 88.8 | 0 | 有 | is esim available in portugal |
| 23 | greece | 21 | 95 | 49.1 | 0 | 有 | cheapest esim for greece and turkey |
| 24 | peru | 21 | 67 | 49.1 | 0 | 有 | cheapest esim peru reddit |
| 25 | france | 21 | 117 | 47.8 | 0 | 有 | esim france unlimited data |
| 26 | kenya | 20 | 59 | 82.9 | 0 | 有 | is esim available in kenya |
| 27 | india | 20 | 201 | 53.4 | 52 | 有 | esim use in india |
| 28 | brazil | 20 | 68 | 47.8 | 0 | 有 | cheap esim brazil reddit |
| 29 | ireland | 19 | 101 | 70.9 | 0 | 有 | is esim available in ireland |
| 30 | spain | 19 | 121 | 63.3 | 100 | 有 | best esim for spain |

**高需求但站内无国家页的：0 个**

### 4.2 逐国词数（全部 49 国）

united-kingdom(325)、united-states(311)、japan(276)、australia(215)、thailand(213)、canada(207)、china(201)、india(201)、vietnam(179)、new-zealand(163)、singapore(161)、philippines(154)、italy(149)、south-korea(149)、egypt(129)、malaysia(129)、spain(121)、mexico(120)、france(117)、germany(116)、hong-kong(112)、south-africa(110)、saudi-arabia(107)、indonesia(103)、united-arab-emirates(102)、ireland(101)、morocco(101)、greece(95)、portugal(87)、taiwan(84)、netherlands(76)、costa-rica(74)、switzerland(71)、brazil(68)、peru(67)、qatar(61)、kenya(59)、colombia(59)、argentina(54)、georgia(47)、iceland(46)、poland(44)、israel(44)、austria(40)、fiji(40)、croatia(40)、belgium(35)、czechia(20)、macao(3)

---

## 五、品牌侧需求真相

站上 10 个品牌在 Google 补全里的出现次数：

| 品牌 | 词数 | 最高综合分 | 最高指数 | 代表词 |
|---|---|---|---|---|
| airalo | 597 | 85.0 | 60 | how does airalo esim work |
| holafly | 442 | 47.8 | 40 | holafly esim ireland and uk |
| saily | 491 | 70.8 | 100 | saily esim review |
| nomad | 343 | 47.8 | 32 | does nomad esim work in new zealand |
| ubigi | 228 | 92.5 | 33 | ubigi esim price |
| alosim | 18 | 46.4 | - | alosim esim europe review |
| yesim | 45 | 100.0 | - | yesim esim prices |
| jetpac | 120 | 70.8 | 100 | jetpac esim review |
| roamic | 121 | 73.0 | 100 | roamic esim reviews |
| roami | 2 | 38.9 | - | roami esim promo code |


⚠️ **`roami` 与 `roamic` 是两个不同实体**，补全里出现的以 `roamic` 为主。品牌词的需求量差距极大 —— 这直接决定「品牌×国家」页型能带来多少自然流量。

---

## 六、你点名的页面各该抢什么

⚠️ **先读这条**：下表的 `★热度` 列**只在抽样比较过的那 90 个词里有值**。显示 `-` 表示「这个词没进比较样本」，**不等于**「测到 0」；显示 `0.0000` 才是「进了样本但低于 Trends 分辨率」。两者别混。

### US 国家页（/compare/united-states/）

共 **252** 词，其中 **2** 个测到非零热度。

**★ 测到热度的（按热度降序）**：`esim price usa`(0.0059)、`best esim for usa`(0.0030)

Top 12（按综合分，仅表示词型归属，**不是热度**）：

| 综合分 | ★热度 | 指数 | 上升 | 词型 | 词 |
|---|---|---|---|---|---|
| 71.5 | 0.0030 | 100 |  | 国家·核心 | `best esim for usa` |
| 64.0 | 0.0059 | - |  | 国家·价格/交易 | `esim price usa` |
| 61.6 | - | - |  | 国家·核心 | `esim us number` |
| 60.8 | - | - |  | 国家·核心 | `is esim available in usa` |
| 59.9 | - | - |  | 国家·价格/交易 | `cheapest us esim` |
| 58.9 | - | 77 | +50% | 国家·核心 | `esim usa` |
| 48.1 | - | - |  | 国家·核心 | `does airtel esim work in usa` |
| 47.8 | - | - |  | 国家·核心 | `esim for europe travel from us` |
| 47.8 | - | - |  | 国家·核心 | `esim usa tourist reddit` |
| 46.8 | - | 56 |  | 国家·核心 | `esim usa travel` |
| 46.8 | - | 61 |  | 国家·核心 | `travel esim usa` |
| 46.4 | - | - |  | 国家·核心 | `best esim for europe and usa` |

### 新加坡国家页（/compare/singapore/）

共 **141** 词，其中 **0** 个测到非零热度。

Top 12（按综合分，仅表示词型归属，**不是热度**）：

| 综合分 | ★热度 | 指数 | 上升 | 词型 | 词 |
|---|---|---|---|---|---|
| 73.6 | - | - |  | 国家·核心 | `is esim available in singapore` |
| 70.8 | - | 100 |  | 国家·核心 | `best esim singapore` |
| 63.4 | - | - |  | 国家·价格/交易 | `cheapest esim singapore` |
| 52.4 | - | - |  | 国家·核心 | `what is esim singapore` |
| 46.4 | - | - |  | 国家·核心 | `best sim card for tourists in singapore` |
| 46.4 | - | - |  | 国家·对比 | `compare esim plans singapore` |
| 46.4 | - | - |  | 国家·规格/流量 | `esim data plan singapore` |
| 46.4 | - | - |  | 国家·核心 | `esim singapore` |
| 46.4 | - | - |  | 国家·设备兼容 | `esim singapore iphone` |
| 46.4 | - | - |  | 国家·核心 | `esim singapore reddit ph` |
| 46.4 | - | - |  | 国家·核心 | `esim singapore review` |
| 46.4 | - | - |  | 国家·核心 | `esim singapore tourist reddit` |

### 日本国家页（/compare/japan/）

共 **219** 词，其中 **1** 个测到非零热度。

**★ 测到热度的（按热度降序）**：`best esim for japan`(0.0054)

Top 12（按综合分，仅表示词型归属，**不是热度**）：

| 综合分 | ★热度 | 指数 | 上升 | 词型 | 词 |
|---|---|---|---|---|---|
| 69.5 | 0.0054 | 100 |  | 国家·核心 | `best esim for japan` |
| 61.9 | - | 93 | +60% | 国家·核心 | `esim japan` |
| 56.1 | - | - |  | 国家·核心 | `is esim available in japan` |
| 47.8 | - | - |  | 国家·核心 | `best esim for tokyo japan` |
| 47.8 | - | - |  | 国家·落地渠道 | `esim japan airport price` |
| 46.4 | - | - |  | 国家·核心 | `best esim for japan 2026 reddit` |
| 46.4 | - | - |  | 国家·核心 | `best esim for japan reddit` |
| 46.4 | - | - |  | 国家·核心 | `best esim for long stay in japan` |
| 46.4 | - | - |  | 国家·核心 | `best esim japan 2026 reddit` |
| 46.4 | - | - |  | 国家·核心 | `best japan sim card for tourists` |
| 46.4 | - | - |  | 国家·价格/交易 | `cheap esim japan reddit` |
| 46.4 | - | - |  | 国家·价格/交易 | `cheapest esim for japan reddit` |

### 新加坡 × Roamic（/compare/singapore/roamic/）

**本轮 Google 采集里没有词归到这个 URL。**

### 日本 × Roamic（/compare/japan/roamic/）

共 **4** 词，其中 **0** 个测到非零热度。

Top 12（按综合分，仅表示词型归属，**不是热度**）：

| 综合分 | ★热度 | 指数 | 上升 | 词型 | 词 |
|---|---|---|---|---|---|
| 46.4 | - | - |  | 品牌×国家 | `roamic esim japan erfahrungen` |
| 44.5 | - | - |  | 品牌×国家 | `roamic esim japan review` |
| 38.9 | - | - |  | 品牌×国家 | `roamic esim japan reddit` |
| 20.1 | - | - |  | 品牌×国家 | `roamic esim reviews japan` |

### 新加坡 × Airalo（/compare/singapore/airalo/）

共 **4** 词，其中 **0** 个测到非零热度。

Top 12（按综合分，仅表示词型归属，**不是热度**）：

| 综合分 | ★热度 | 指数 | 上升 | 词型 | 词 |
|---|---|---|---|---|---|
| 42.6 | - | - |  | 品牌×国家 | `airalo esim singapore review` |
| 38.9 | - | - |  | 品牌×国家 | `airalo esim singapore not working` |
| 38.9 | - | - |  | 品牌×国家 | `does airalo esim work in singapore` |
| 31.4 | - | - |  | 品牌×国家 | `airalo esim singapore reddit` |

---

## 七、缺口簇

### ① 双国 / 多国组合词（「A and B」型）

**规模**：807 词；其中 ≥46 分（全站前 10%）78 个；站内无承接页 674 个。

**为什么重要**：搜索意图最明确（行程已定），且站内**零承接**。现有 `/guides/best-{region}-esim/` 只接大洲级词，接不住「两个具体国家」。**建议**：新增页型 `/compare/{a}-and-{b}/`（与 `/compare/{a}-vs-{b}/` 不冲突 —— 一个是「两个目的地、一张 eSIM」，一个是「两个品牌、谁更好」）。**这属架构变更，按项目纪律需你点头。**

| 综合分 | 指数 | 上升 | 词 | 站内 |
|---|---|---|---|---|
| 49.1 | - |  | `esim for austria and germany` | 缺口 |
| 48.1 | - |  | `uae and qatar esim` | 缺口 |
| 47.8 | - |  | `best esim for australia and new zealand reddit` | 缺口 |
| 47.8 | - |  | `best esim for belgium and netherlands` | 缺口 |
| 47.8 | - |  | `best esim for croatia and italy` | 缺口 |
| 47.8 | - |  | `best esim for hong kong and china` | 缺口 |
| 47.8 | - |  | `best esim for hong kong and china reddit` | 缺口 |
| 47.8 | - |  | `best esim for ireland and uk` | 缺口 |
| 47.8 | - |  | `best esim for singapore and malaysia` | 缺口 |
| 47.8 | - |  | `best esim for switzerland and italy` | 缺口 |
| 47.8 | - |  | `best esim for thailand and vietnam reddit` | 缺口 |
| 47.8 | - |  | `best esim for usa and canada travel` | 缺口 |

### ② 城市词

**规模**：965 词；其中 ≥46 分（全站前 10%）80 个；站内无承接页 965 个。

**禁开城市页**（`docs/keyword-map.md` 的蚕食禁区）→ 只能并入所在国家页的 Cities 小节，或做 FAQ 问答。

| 综合分 | 指数 | 上升 | 词 | 站内 |
|---|---|---|---|---|
| 49.1 | - |  | `bogota airport esim` | 缺口 |
| 49.1 | - |  | `esim brussels airport` | 缺口 |
| 49.1 | - |  | `esim rio de janeiro` | 缺口 |
| 49.1 | - |  | `esim riyadh airport` | 缺口 |
| 49.1 | - |  | `macau esim unlimited data` | 缺口 |
| 48.1 | - |  | `esim rio de janeiro reddit` | 缺口 |
| 47.8 | - |  | `barcelona esim card` | 缺口 |
| 47.8 | - |  | `best esim for auckland` | 缺口 |
| 47.8 | - |  | `best esim for barcelona reddit` | 缺口 |
| 47.8 | - |  | `best esim for istanbul turkey` | 缺口 |

### ③ 信任 / 评价类（Reddit 语言）

**规模**：1608 词；其中 ≥46 分（全站前 10%）349 个；站内无承接页 175 个。

旅行者在下单前的最后一问。**建议**：国家页 FAQ 增加「这些品牌靠不靠谱」，链到方法论页。⚠️ **不要编评分** —— 站内已有 Trustpilot 链接纪律（只给档案链接、不印分数）。

| 综合分 | 指数 | 上升 | 词 | 站内 |
|---|---|---|---|---|
| 88.0 | - |  | `yesim esim review` | 已覆盖 |
| 73.0 | 100 |  | `roamic esim reviews` | 已覆盖 |
| 70.8 | 100 |  | `jetpac esim review` | 已覆盖 |
| 70.8 | 100 | +90% | `saily esim review` | 已覆盖 |
| 66.4 | - |  | `esim review` | 已覆盖 |
| 53.0 | 60 | +50% | `airalo esim review` | 已覆盖 |
| 49.1 | - |  | `best esim for czech republic reddit` | 已覆盖 |
| 49.1 | - |  | `cheapest esim argentina reddit` | 已覆盖 |
| 49.1 | - |  | `cheapest esim colombia reddit` | 已覆盖 |
| 49.1 | - |  | `cheapest esim costa rica reddit` | 已覆盖 |

### ④ 出发地视角（`{dest} from {origin}`）

**规模**：247 词；其中 ≥46 分（全站前 10%）38 个；站内无承接页 191 个。

**建议**：并入国家页 FAQ —— FAQPage 天然素材，且不新增页型。

| 综合分 | 指数 | 上升 | 词 | 站内 |
|---|---|---|---|---|
| 47.8 | - |  | `best esim for fiji from australia` | 缺口 |
| 47.8 | - |  | `cheapest esim for india from uk` | 缺口 |
| 47.8 | - |  | `cheapest esim for indonesia from australia` | 缺口 |
| 47.8 | - |  | `cheapest esim for italy from uk` | 缺口 |
| 47.8 | - |  | `cheapest esim for saudi arabia from uk` | 缺口 |
| 47.8 | - |  | `cheapest esim for south africa from uk` | 已覆盖 |
| 47.8 | - |  | `cheapest esim for spain from uk` | 缺口 |
| 47.8 | - |  | `do i need an esim for new zealand from australia` | 缺口 |
| 47.8 | - |  | `do i need an esim for usa from uk` | 缺口 |
| 47.8 | - |  | `esim for europe travel from us` | 已覆盖 |

### ⑤ 免费 / 预付类

**规模**：299 词；其中 ≥46 分（全站前 10%）21 个；站内无承接页 12 个。

意图混合：既有「找免费方案」也有「避免合约」。建议 FAQ 承接。

| 综合分 | 指数 | 上升 | 词 | 站内 |
|---|---|---|---|---|
| 75.0 | - |  | `esim prepaid plans` | 已覆盖 |
| 56.1 | - |  | `is there prepaid esim` | 已覆盖 |
| 47.8 | - |  | `cheapest esim netherlands prepaid` | 已覆盖 |
| 47.8 | - |  | `esim belgium prepaid` | 已覆盖 |
| 46.4 | - |  | `cheap esim australia prepaid` | 已覆盖 |
| 46.4 | - |  | `esim free trial 1gb` | 已覆盖 |
| 46.4 | - |  | `esim free trial australia` | 已覆盖 |
| 46.4 | - |  | `esim free trial usa` | 已覆盖 |

### ⑥ 语音 / 号码类

**规模**：254 词；其中 ≥46 分（全站前 10%）15 个；站内无承接页 9 个。

站内 `#reality` 已有 voice 政策卡（`data/providers.toml` 的 voice 字段）。建议：把这些词接进品牌子页 FAQ。

| 综合分 | 指数 | 上升 | 词 | 站内 |
|---|---|---|---|---|
| 46.4 | - |  | `best esim for india with phone number` | 已覆盖 |
| 46.4 | - |  | `china esim card with phone number` | 已覆盖 |
| 46.4 | - |  | `esim canada plans with phone number` | 已覆盖 |
| 46.4 | - |  | `esim for australia data and calls` | 已覆盖 |
| 46.4 | - |  | `esim sms empfangen` | 已覆盖 |
| 46.4 | - |  | `esim sms not working` | 已覆盖 |
| 46.4 | - |  | `esim voice calls europe` | 已覆盖 |
| 46.4 | - |  | `esim with phone number singapore` | 已覆盖 |

---

## 八、Google 通道 vs Bing 通道（上一版）—— 批判性对照

| 指标 | Bing 版（上一版） | Google 版（本版） |
|---|---|---|
| 词数 | 4579 | 11454 |
| 两版交集 | \- | **1060**（占 Google 版 9.3%） |
| 只有本版有 | \- | **10394** |
| 有热度数值 | 无（只有位次） | **69 个词带 Google 指数** |
| 最高热度数值 | \- | 100 |

### 只看 Bing 会漏掉的词（本版新增、且综合分 ≥55 —— 全站前 1% 阈值，现算）

| 综合分 | 指数 | 词 | 词型 |
|---|---|---|---|
| 100.0 | - | `yesim esim prices` | 品牌（全局） |
| 92.5 | - | `ubigi esim price` | 品牌（全局） |
| 88.8 | - | `can i get an esim` | 通用·问题 |
| 88.8 | - | `cheap esim data plans` | 通用·价格交易 |
| 88.8 | - | `cheapest esim data plan` | 通用·价格交易 |
| 88.8 | - | `cheapest international esim` | 通用·全球 |
| 88.8 | - | `does esim work on international roaming` | 通用·全球 |
| 88.8 | - | `esim international number` | 通用·全球 |
| 88.8 | - | `esim iphone how many` | 通用·设备兼容 |
| 88.8 | - | `esim phone plans` | 通用·其他 |
| 88.8 | - | `esim size` | 通用·其他 |
| 88.8 | - | `how to apply for an esim` | 通用·问题 |
| 88.8 | - | `is esim available in portugal` | 国家·核心 |
| 86.9 | - | `esim cheapest plan` | 通用·价格交易 |
| 85.0 | - | `can i use data from esim` | 通用·问题 |


### 结论

1. **Google 是唯一给出热度数值的通道** —— Bing 补全只有位次，无法定权重。
2. **两版交集只有 9.3%** —— 说明补全引擎的语料差异很大，**任何单通道采集都是不完整的视角**。本版以 Google 为准（用户要求 + 有数值），Bing 版保留作对照。
3. **两版 `sources` 不可直接比较** —— 两个引擎的语料与泛化行为不同（本版已实测澄清：差异不在「注入通用块」，而在各自的语料侧重）。

---

## 九、行动清单

站内缺口共 **1890** 词，其中 ≥46 分（全站前 10%）**199** 个。

**★ 先说最硬的两条**（依据 §3.5 的抽样比较，不是补全分）：

1. **全站 11,573 个词里，抽样比较的 90 个词只有 10 个测到非零热度。** 而**最热的前三个都不是国家词，是 `esim price`(0.0619) / `esim size`(0.0182) / `esim requirements`(0.0145) —— 它们归的都是首页 `/`**。说明「eSIM 价格/规格」类通用词才是本领域真正的大流量入口，首页与指南页该正面接这几个词。
2. **测到热度的国家类词集中在 `best esim for {国家}` / `esim price {国家}` 两个句式**（`esim price usa`(0.0059)、`best esim for japan`(0.0054)、`saily esim canada`(0.0052)、`best esim for usa`(0.0030)、`best esim for uk`(0.0012)）——而补全高频的 `is esim available in X` 一个都没测到。**国家页的 H2 该抢前者，不是后者。**

| 优先级 | 动作 | 依据 | 需你决策 |
|---|---|---|---|
| 1 | 首页/指南页正面接 `esim price` / `esim size` / `esim requirements` | 抽样里最热的三个词（§3.5），且已归 `/` | 否 |
| 2 | 补 `/networks/{country}/`（缺 37 国） | 纯内容补齐、零模板改动 | 否 |
| 3 | 国家页 H2 用 `best esim for {country}` 句式 | 唯一测到热度的国家类句式（§3.5） | 否 |
| 4 | 国家页加 Cities 小节 | 城市词 965 个 | 否 |
| 5 | 国家页 FAQ 加信任/出发地两类问答 | 信任 1608 + 出发地 247 词 | 否 |
| 6 | 开 `/compare/{a}-and-{b}/` | 双国组合 807 词、零承接 | **是**（新页型） |
| 7 | 接 Google Search Console | 唯一能拿到真实曝光/点击的路，也能校准本报告的口径 | **是**（需授权） |


---

## 附：复算方式

```bash
python -X utf8 scripts/kw_harvest_google.py      # Google Suggest 全量（约 30 分钟）
python -X utf8 scripts/kw_trends.py              # Google Trends 相关查询（约 10 分钟）
python -X utf8 scripts/kw_score_google.py        # 三路证据打分
python -X utf8 scripts/kw_trends_compare.py      # ★ 跨词可比热度（批量比较 + 锚词归一，约 10 分钟）
python -X utf8 scripts/kw_classify_google.py     # 分类 + 归属 + 站内对账
python -X utf8 scripts/kw_report_google.py       # 生成本报告
```

原始响应：`docs/keywords/google/raw_google_suggest.json`、`raw_google_trends.json` —— 任何人可离线重算，无需联网。
