# eSIM Sift 项目文档（交接手册）

> **用途**：隔几天回来接着干时，看这一份就能接上。写了什么、还缺什么、每个文件干嘛的、常见操作怎么做。
> **最后更新**：2026-10-02 批次G（guides 5 篇深度重写 + 首屏配图 / compat 设备库 UX / research 枢纽区域联赛+问答路由 / 全站去写死三层架构 + 双守卫脚本）
> **配套文件**：`STATUS.md`（按时间顺序的施工日志，看"当时为什么这么做"）、`docs/keyword-map.md`（关键词→URL 唯一映射表，上新页型前必查）。

---

## 0. 项目一句话 + 当前状态快照

**eSIM Sift（esimsift.com）**：独立 eSIM 比价站，对标 esimdb.com / mybestsim.com。Hugo 0.159.1 + Tailwind CLI，英语站（目录已为多语言预留）。核心原则：**单一事实源** —— 所有数字只存在于 `data/*.toml`，模板层全部实时推导，改数据 = 全站数字自动刷新，永不手工改页面里的价格。

**当前状态（2026-10-01 批次D 后）**：

| 指标 | 数值 |
|---|---|
| 品牌 | 8 家（airalo / holafly / saily / yesim / ubigi / roamic / alosim + 自家 roami；**roami ≠ roamic，两个不同品牌**；nomad 已全量退场） |
| 国家 | 50 国（`data/countries.toml` 锁定） |
| 套餐总数 | **8776 条真实数据**：airalo 985 / holafly 298（官网 PDP 直抓）/ saily 471 / yesim 1652 / ubigi 483（含 80 条订阅）/ roamic 1791 / alosim 915 / roami 1181 |
| 构建 | **520 页，0 error**；sitemap 508 URL |
| 页面构成 | 50 国家页 + 400 品牌×国家子页 + 28 品牌对决页 + **1 对决枢纽页 /compare/matchups/** + 8 品牌详情页 + tools/esim-deals/research×3/guides×5/about 等静态页 |
| 数据验证 | `scripts/validate.py` 8 组检查，0 error 0 warning |
| 增信数据 | `data/devices.toml`（14 品牌 351 机型 + 12 不支持条目，2026-10 核对）+ `data/networkreports.toml`（45 国 Opensignal/Ookla 引用 + 50 国 Global Index 深链） |
| 上线状态 | **未部署**。折扣码已换真（roami web20 / saily VEEPEE25 / ubigi WELCOME10，其余 5 家官方无公开码）、联盟深链是模式假设、GA4 是占位、logo 8/8 全量接入 |

---

## 1. 目录结构总览

```
esimsift/
├── hugo.toml              # 站点配置 + 出站导流唯一控制点 [params.outbound]
├── PROJECT.md             # 本文档
├── STATUS.md              # 施工日志（按轮次）
├── docs/keyword-map.md    # 关键词→URL 映射（防蚕食前置门）
├── data/                  # ★ 单一事实源（所有数字在这）
│   ├── countries.toml     # 50 国主数据
│   ├── providers.toml     # 8 品牌档案
│   ├── plans/<brand>.toml # 每品牌×国家套餐（8 个文件）
│   ├── carriers.toml      # 50 国运营商画像 + 城市明细
│   ├── devices.toml       # eSIM 兼容设备库（14 品牌 351 机型 + 12 不支持条目）
│   ├── networkreports.toml# 45 国 Opensignal/Ookla 独立引用（⚠ 文件名禁连字符）
│   └── faqs/<iso>.toml    # 50 国 FAQ（49 个 + jp 样板）
├── content/en/            # 页面正文（哪些手写哪些生成，见 §4.7）
├── layouts/               # 模板（数字全部实时推导）
├── static/img/            # flags / countries / site / esim
├── scripts/               # 抓取/生成/校验脚本（见 §5.2）
│   └── scrape/raw/        # ★ 原始抓取 JSON（证据留存，勿删）
└── public/                # 构建产物（hugo 不清理旧页，见 §14）
```

---

## 2. 已完成功能清单

### 2.1 数据层
- ✅ **8 品牌 × 50 国真实套餐全量入库**（8776 条，来源与口径见各 plans 文件头注释：esimdb.com 单国套餐 USD 牌价；holafly 为官网 PDP USD 价表）
- ✅ 抓取管线：esimdb 穿透 AWS WAF（本机 Playwright chromium）、holafly 官网 PDP 抓取器、roami 本地项目提取器、raw→TOML 转换器（断点续跑、坏数据进人工复核清单）
- ✅ 套餐建模规则（`toml_write.py`，详见 §4.3）：固定量 / 日额型 / unlimited（限速徽章识别）/ Ubigi Monthly·Yearly 订阅 / holafly FUP 透传 / 通用名重写
- ✅ `carriers.toml`：50 国 ~154 条运营商画像（速度区间/制式/覆盖特性）+ 50 国 `[ISO.info].cities` 主要城市 + 18 个关键市场 54 条逐运营商 strong/weak
- ✅ `devices.toml`（2026-10-01）：eSIM 兼容设备库 —— 14 品牌组 351 机型 + 9 组变体警告 + 12 条明确不支持；compatibility 指南页交互块（搜索/tab/chips）live 计数，增删机型无需改模板
- ✅ `networkreports.toml`（2026-10-01）：45 国独立网络数据引用 —— Opensignal 获奖≤3 事实卡 + Ookla 新闻式归属卡（页脚禁商业转载其数据）+ Global Index 深链卡 50 国兜底；HK/MO/TR slug 覆盖，IS/GE/KE/MO/CN 无报告自动降级 index-only
- ✅ `validate.py` 8 组数据检查挂入 `npm run build`（坏数据进不了构建）

### 2.2 页面型
- ✅ **国家页** `/compare/<country>/`（50 页，全站核心）：TL;DR 三卡（按预算/性价比/长停留推荐，CTA 进站内子页）→ 13 模块：全套餐对比表（排序 + 有效期 chips + **品牌多选 chips + Unlimited only 开关**，纯客户端 data-* 过滤）、怎么选（按用量分档）、按人群×按时长 8 卡推荐矩阵、品牌口碑区（logo+名可点进品牌页）、运营商覆盖区（速度档位 + 主要城市 + 逐运营商优劣势）、**独立网络数据区**（Opensignal 事实卡 + Ookla 归属卡 + Global Index 深链卡，45 国核实 + 无报告国降级 index-only）、FAQ、出站表格、**「First time using an eSIM?」guides 五卡条**（锚文本按 `mod (len slug) 3` 三档轮换防同质化）
- ✅ **品牌×国家子页** `/compare/<country>/<brand>/`（400 页，`gen_provider_pages.py` 生成，描述数字直读数据）
- ✅ **品牌对决页** `/compare/{a}-vs-{b}/`（28 页 = C(8,2)，verdict-first + 逐国判胜表 + 数据驱动 FAQ + sibling 互链）+ **对决枢纽页** `/compare/matchups/`（28 卡全量索引 + closest rivalry/most lopsided 计算瓦片；header/footer/llms.txt 入口）+ vs 页 "Other eSIM comparisons" 勾选选择器（8 logo 卡最多勾 2 个，第 3 个挤掉最早勾选，字母序实时拼 `/compare/{a}-vs-{b}/`）
- ✅ **品牌详情页** `/esim-providers/<key>/`（8 页，计算式结论"cheapest in N of M"、竞争力评分、**价格胜负区（全计算：逐国 {B}最低价 vs 全场次优价，赢省%/输溢价% Top5 双卡带链接；>200% 用 ×倍数展示；unlimited-only 品牌带口径脚注；0 胜/0 负空态兜底）**、按区域覆盖清单；公司概况卡含总部/法人 + 官网/双商店链接 chips；客服&退款专区（渠道/邮箱/响应承诺 + 退款摘要）；覆盖区"50 国追踪≠品牌全部目的地"备注；FAQ 含 "{brand} support"/"{brand} refund" 长尾问答；schema 含 Organization(sameAs)；**无数据品牌自动降级为简壳页**）
- ✅ `/tools/` 行程计算器 **+ 用量估算器（对标 mybestsim data-usage-calculator 并反超：竞品止步于"你需要 X GB"，我们闭环到真实套餐）**：8 活动小时步进 → GB/天 → 行程总 GB（20% 余量开关，读取天数滑杆）→ 一键回填 chip 重选套餐；码率参考表（$acts 模板单一来源，11 行含 1GB 折算）；底部 12 热门国家卡 + 8 品牌卡（全计算生成）+ FAQ×3+schema；`/esim-deals/` 折扣码页（对标 mybestsim 并超越：实码卡（核验日期+条款+折扣后实际价实时计算）→ "折扣码翻盘分析"表（折后价 vs 全场最低价，N/50 翻盘数）→ 无码品牌计算式替代价值 → 5 步使用教程 → 4 条无码省钱路径（全内链）→ FAQ×5+schema → 底部 8 品牌入口 + 4 相关页）
- ✅ `/research/` 3 页（price-index 50 国 $/GB 联赛表 / unlimited-esim 日费率榜 + **盈亏平衡分析** / fair-use-audit 逐品牌 FUP 审计）——全部从数据实时推导；**每行/每卡可钻取**（Winning plan 列链品牌×国家子页、区域卡列出全部国家 chips、unlimited 表品牌/套餐双链）；每页含计算洞察区 + 数据驱动 FAQ ×3-4 + FAQPage schema + Related research ×4 互联卡；unlimited-esim 首屏指标已解挤（全宽三卡条 + 品牌覆盖 chips）；**枢纽页 2026-10-02 升级**：首屏两栏配图（hero front matter 同 guides）+ **区域价格联赛**（region 聚合各国最优 $/GB 均值，5 卡排序）+ 最贵/最便宜价差叙事（计算倍数）+ **问答路由卡 ×6**（搜索意图→对应页）+ FAQ×6 schema + 正文 3 段立场声明
- ✅ `/guides/` 5 篇（what-is / how-to-install / vs-physical-sim / dual-sim / compatibility-check）：**2026-10-02 深度重写至 1677-1955 词**（对位竞品博客的信息增量段：SM-DP+ 手动录入、双线来电路由、区域变体机制、验机清单等；FAQ 7-8 条；内链 9-14 条/篇短锚轮换）；**每篇首屏配图**（front matter `hero`+`hero_alt`，imageConfig 宽高 + eager + fetchpriority=high + og:image 联动）；专用 `layouts/guides/single.html` 注入逐篇计算数据盒（$/GB 榜/入门价榜/unlimited 日费率榜/安装方式表，指标互不重复）+ front-matter `faqs` 渲染 FAQ + FAQPage schema + 相关阅读闭环；compatibility-check 篇专属注入 devices.toml 交互设备库（**品牌分组卡片**：搜索 + 品牌 tab + 351 chips + 变体内联警示 + 不支持表，与正文 EID 终审原则互指）
- ✅ 静态页：about / methodology / disclosure / privacy / terms / contact（disclosure 2026-10-01 已去除同司声明，改为佣金模式 + 诚实规则，勿再加回）

### 2.3 SEO / 基建
- ✅ 结构化数据全在模板层：国家页 FAQPage、子页 BreadcrumbList、品牌页 Product+Review+FAQPage @graph、对决页 FAQPage（**不做假评分**，用"最便宜命中率"透明口径 —— 蓝图红线）
- ✅ **AEO/GEO 三层（2026-10-02）**：Organization + WebSite 全站 509 页（`partials/schema-org.html`，实体锚点，sameAs 留空待官方 profile）；Article 自动覆盖 guides/research 8 篇（`partials/schema.html`，`.IsPage` 且 Section∈guides/research 门控）；`layouts/robots.txt` 显式 Allow 15 个 AI 爬虫 + sitemap

**每类页面 → 应带的结构化数据（新增页型时按此查漏）**：

| 页面类型 | JSON-LD schema |
|---|---|
| 首页 `/` | Organization + WebSite + BreadcrumbList |
| 国家页 `/compare/{country}/` | Organization + WebSite + **FAQPage** + BreadcrumbList + Product + AggregateOffer |
| 品牌页 `/esim-providers/{brand}/` | Organization + WebSite + **Product+AggregateOffer+Brand** + **Review+Rating** + FAQPage + BreadcrumbList |
| 对决页 `/compare/{a}-vs-{b}/` | Organization + WebSite + FAQPage + BreadcrumbList |
| guides / research 文章 | Organization + WebSite + **Article** + FAQPage + BreadcrumbList |
| 工具/折扣页 `/tools/` `/esim-deals/` | Organization + WebSite + FAQPage + BreadcrumbList |
| 列表枢纽 `/compare/` | Organization + WebSite + BreadcrumbList |
- ✅ `llms.txt`（50 国 + 28 对决 + research/guides 自动枚举）、`catalog.json`（机器可读 50 国）、sitemap 508 URL（自定义 `layouts/sitemap.xml`：无 changefreq/priority；lastmod 三层解析——国家页=该国快照日 / 编辑页=自身 date / 其余=全站最新快照日）
- ✅ 出站导流单一出口：全站只有 `partials/cta-out.html` 一个出站点，`hugo.toml [params.outbound]` 一处配置（active 指向、rel、UTM、campaign 按页面类型自动）
- ✅ 品牌 logo：**8/8 全量接入**（airalo/ubigi/yesim/roamic/roami/alosim=.png，holafly/saily=.webp），prov-logo partial 先探 .png 再探 .webp；放 `static/img/providers/<key>.png|.webp` 即自动切换（零配置）
- ✅ 内链纪律：TL;DR/品牌区/锚文本全部指向站内；漏斗出口只在表格 View 列和 cta-out

---

## 3. 待完成功能（按优先级）

### P-A 数据项（上线前必须）
- [x] ~~折扣码换真~~ **2026-10-01 完成**：三路代理在 8 家官方页面逐项核验。有公开码：roami `web20`（官网公示·新用户 20%）/ saily `VEEPEE25`（官方合作页 25%）/ ubigi `WELCOME10`（官方 FAQ 首购 10%）；airalo/holafly/yesim/roamic/alosim 官方无公开码（仅有推荐返利计划）→ 无 promo 字段，模块自动隐藏。**遗留**：三家 promo_expires 均为占位 2027-12-31（官方没标过期日），上线前复核一次
- [ ] **联盟深链规则核实**：`hugo.toml [params.outbound.targets.*]` 的 `country_path` 和 `data/countries.toml [ISO.slugs]` 目前是模式假设（roami 假设 `/{slug}/`，其他家没配逐国深链）→ 逐品牌确认联盟链接的国家级 URL 格式
- [ ] **networks 补真**：所有 plans 的 `networks = []`（esimdb 卡片不展示网络名）→ 可从各品牌官网国家页抓（airalo.com 有 "T-Mobile +1 other"）；补上后国家页表格网络列 + ⑦b 区块自动增强
- [ ] **carriers.toml 剩余 32 国 detail**：目前只有 18 个关键市场有逐运营商 strong/weak，其余国家只有 cities + 画像
- [ ] carriers.toml 速度区间逐市场核实（现值是编辑常识典型值）
- [ ] 逐国 quirks 人工复核（`countries.toml`，生成内容基于真实常识，上线前过一遍）
- [ ] Ubigi 订阅套餐（days=30/365）在排序/筛选里的显示是否合理，检查一遍

### P-B 内容期
- [ ] 49 国 3 段分析 + 6 条 FAQ 人工润色（生成器已出可读初稿；`content/en/compare/japan.md` + `data/faqs/jp.toml` 是手写样板）
- [ ] validate.py 增加锚文本分布统计（完全匹配 ≤20%）——真实内容产出后做才有意义
- [ ] 变体子页（cheapest/unlimited/long-stay）—— 等主站数据 ≥10 国再上，防关键词蚕食

### P-C 上线前
- [ ] privacy/terms/disclosure 法律审校（文中已标 Todo）
- [ ] GA4 ID 替换 + 与 roamiapp.com 跨域衡量（`layouts/partials/head.html` 占位注释处）
- [ ] OG 图片（每国一张，含最低价数字）
- [ ] 部署（建议 Cloudflare Pages；见 §16）

### P-2 蓝图 Phase 2（上线后，槽位已留在 docs/keyword-map.md）
- [ ] 区域枢纽页 ×5（/compare/asia/ 等）
- [ ] /networks/{carrier}/ 运营商页、/devices/{device}/ 设备页（设备页数据源 devices.toml 已就绪）
- [ ] tools 再加 2 个
- [ ] sitemap 分片（>1000 URL 时）
- [ ] 国家页 authority 外链

### 明确不做（蓝图红线，勿再议）
- ❌ 城市页（薄页风险；城市名只进国家页运营商区）
- ❌ 假评分 / AggregateRating（用透明计算口径替代）
- ❌ 词数 KPI（不按字数写内容）

---

## 4. 数据与配置文件手册（人工维护看这节）

### 4.1 `data/countries.toml` —— 国家主数据
**作用**：50 国的名称/slug/区域/国旗/邻国/本地运营商/特有问题/图片清单/roami 深链 slug。首页网格、header 大菜单、所有国家页的骨架都从这来。
**维护**：基本冻结。改 `quirks`（逐国特色，国家页正文引用）和 `[ISO.slugs]`（roami 官网深链）最常见。

```toml
[JP]
name = "Japan"            # 显示名（表格/面包屑/标题用）
slug = "japan"            # URL 段，必须与 content/en/compare/japan.md 文件名一致
flag = "img/flags/jp.svg"
region = "Asia"           # 必须精确等于筛选 chip：Asia/Europe/Americas/Africa & Middle East/Oceania
featured = true           # 是否进 header 大菜单"热门"列
neighbors = ["KR", "TW", "HK"]
carriers = ["NTT Docomo", "SoftBank", "KDDI"]   # 本地运营商名，join key 必须与 carriers.toml profiles.name 对齐
kyc_required = false      # 是否需要实名（国家页提示用）
images = ["japan-01.webp", ..., "japan-04.webp"] # static/img/countries/ 下 4 张
quirks = [ "…", "…", "…" ]  # 逐国研究要点（国家页正文引用，P-A 人工复核）

[JP.slugs]
roami = "japan-esim"      # roamiapp.com 上的落地 slug（cta-out 深链用）
```

### 4.2 `data/providers.toml` —— 品牌档案
**作用**：品牌页/品牌卡/对决页的品牌侧信息 + 折扣码模块（deals 页/国家页/子页三处共用）+ 公司档案（品牌页公司概况卡/客服退款区/覆盖备注/FAQ/schema 的数据源）。
**维护**：品牌事实变更；折扣码上下架（`promo_verified` 记录核验日）。

```toml
[airalo]
name = "Airalo"
founded = 2019
tagline = "The original eSIM marketplace"
type = "app"              # app | marketplace（影响"怎么装"三步措辞；roamic 已修正为 marketplace——两家商店都无 App）
color = "#3B6FF5"         # monogram 徽标底色（真 logo 放 static/img/providers/ 后自动弃用）
initials = "Ai"
strengths = ["…", …]
weaknesses = ["…", …]
sponsored = true          # true → 出站 rel="sponsored nofollow"；自家品牌 false → follow
# 折扣码模块（promo_code 存在才显示；删掉全部 promo_* = 模块自动隐藏）
# 2026-10-01 全部换真：roami web20 / saily VEEPEE25 / ubigi WELCOME10；其余 5 家无 promo 字段
promo_code = "VEEPEE25"   # 官方公示码
promo_label = "25% off Saily eSIMs"
promo_pct = 25            # 折扣百分比（int）—— deals 页"折扣后实际价/翻盘分析"用它算
promo_expires = "2027-12-31"   # ⚠ 占位（官方未标过期日），上线前复核
promo_verified = "2026-10-01"  # 核验日期（deals 页展示）
promo_terms = "…"         # 使用条款/适用范围一句话（deals 页展示）

# 公司档案子表（2026-10-01 三路代理在官方页面核验；空字符串 = 官方没有，模板自动跳过）
[airalo.info]
hq = "Singapore"          # 总部（公司概况卡 + 降级壳页）
legal = "AIRGSM Pte. Ltd."  # 法人（概况卡 HQ 行下方小字）
website = "https://www.airalo.com"        # 官网（概况卡 chip；第三方带 sponsored nofollow）
app_android = "https://play.google.com/…" # Google Play（概况卡 chip + schema sameAs；无 App 则 ""）
app_ios = "https://apps.apple.com/…"       # App Store（同上）
support = "24/7 live chat (website and in-app) and email"  # 客服渠道（客服区 + support FAQ）
support_email = "support@airalo.com"       # 官方公示邮箱（mailto；无则 ""）
response_time = ""        # 响应时限承诺（无则 ""；yesim 有"平均 5 分钟"）
refund = "…"              # 退款政策摘要 2-3 句（退款区 + refund FAQ）
destinations = 200        # 品牌自己宣称的目的地数（int；覆盖区"追踪 50 国≠全部"备注用它）
```

### 4.3 `data/plans/<brand>.toml` —— 套餐数据（最常维护）
**作用**：每品牌×国家套餐。全站所有价格的唯一来源。
**生成**：`toml_write.py` 从 `scripts/scrape/raw/<brand>/` 生成 —— **原则上不手写**，改数据走"重抓→重转"；临时手补可以，但下次重转会覆盖，长期修正应改 `toml_write.py` 的解析规则。

```toml
[JP]
checked = "2026-09-30"   # 数据核查日期（表格脚注/research 页引用）
networks = []            # 该品牌在该国用的本地网络（P-A 补真）

[[JP.plans]]
name = "Japan - 10GB / 30 Days"
gb = 10                  # unlimited 一律 0
days = 30                # 订阅：Monthly→30，Yearly→365
type = "data"            # "data" | "unlimited"
price = 13.50            # ★ 必须两位小数 float！price = 13 是 int64，Hugo printf "%.2f" 会渲染成 $%!f(int64=13)
fup_note = "…"           # 可选：限速说明/日额说明/订阅性质（fair-use-audit 页直接引用原文）
```

**type 判定规则**（抓取器的既定口径，人工补数据时保持一致）：
- 卡面 `10GB` → `data, gb=10`
- `1GB/Day` 无限速徽章 → `data, gb=1×days`（日额型，保 $/GB 口径）
- 徽章含 `∞`/限速（"+ ∞ at 1Mbps"）→ `unlimited, gb=0`，fup_note 写 "N GB per day at full speed, then …"
- 名字含 Unlimited + ∞ 徽章、但卡面显示总量（esimdb 1 天卡的显示怪癖）→ `unlimited`
- `5GB/month` + Monthly → `data, days=30, gb=5`，fup_note 注明订阅；Yearly → `days=365, gb=5×12`（年付总额，保 $/GB 诚实）

### 4.4 `data/carriers.toml` —— 运营商画像
**作用**：国家页运营商区（⑦b）数据源。**不依赖 plans.networks**（那是空的也能全量渲染）。

```toml
[US]                      # ISO 块
[[US.profiles]]           # 运营商画像（join key: name 必须与 countries.toml carriers 列表一致）
name = "Verizon"
tech = "5G"               # 枚举: 4G/5G（validate 校验）
speed_min = 25            # 典型实测下限 Mbps（模板据此推导"能干什么"档位：≥25=4K / ≥10=HD / ≥5=基础）
speed_top = 150
note = "…"                # 覆盖特性一句话

[US.info]                 # 城市条（50 国都有）
cities = ["New York", "Los Angeles", "Chicago", "Miami"]   # 每个全国性网络都覆盖的主要城市

[[US.info.detail]]        # 逐运营商优劣势（目前 18 个关键市场有，其余 32 国 P-A 补）
carrier = "Verizon"       # 必须与上面 profiles.name 一致
strong = "The widest rural footprint - …"
weak = "Mid-city and indoor speeds can trail …"
```
**维护**：补剩余 32 国 detail 时直接在该国块后追加 `[[XX.info.detail]]`（TOML 表数组可以追加在文件任何位置，validate 会查 join key）。

### 4.5 `data/faqs/<iso>.toml` —— 国家 FAQ
**作用**：国家页 FAQ 模块 + FAQPage schema。文件名 = 小写 ISO（`jp.toml`）。顶层是 `[[faq]]` 数组（模板取值 `.faq`）。只做**对比角度**（激活/安装类问题归 Roami 主站，防 SERP 重叠）。jp.toml 是手写样板，其余为生成初稿（P-B 润色）。

### 4.5a `data/devices.toml` —— eSIM 兼容设备库
**作用**：/guides/esim-compatibility-check/ 的交互设备表（搜索框 + 品牌 tab + 机型 chips + 变体警示条）+ 不支持机型表。模板 live 计数（总机型数 = range 累加），文章正文只说 "several hundred"——增删机型不用改模板也不用改文章。
**维护**：新机型 → 对应 `[[brand]].models` 追加一行；变体坑 → 品牌 `note`（无 note 的品牌警示条自动隐藏）或 `[[blocked]]` 表加条目；`updated` / `source_note` 顶层字段驱动页内 "last reviewed" 文案，季度刷新。

### 4.5b `data/networkreports.toml` —— 独立网络数据引用
**作用**：国家页「Independent network data for {C}」三卡：Opensignal 事实卡（≤3 条获奖事实 + 原文链接）+ Ookla 归属卡（仅 6 国有可引数据）+ Global Index 深链卡（50 国兜底）；底部 accessed 声明行（E-E-A-T）。
**引用纪律**：**Ookla 页脚禁止商业转载其报告数据 → 只做新闻式归属**（获奖者 + 报告期 + ≤1 个数字 + 链接），数值细节一律用 Opensignal（测均值体验速度；Ookla 是中位，两者不可直接比）。无近期报告的国家（IS/GE/KE/MO/CN）只出 index 卡，**不编造**；旧报告（PT/AR 2023）标 "directional" 诚实收录。
**维护**：季度刷新 `accessed`/`updated` + 逐国事实（格式照抄现有条目，display date 用 "January 2026" 式）。slug 覆盖字段：`ookla_slug`（HK=`hong-kong-(sar)`/MO=`macau-(sar)`/TR=`t%C3%BCrkiye`，**旧 slug turkey/czech-republic 已冻结勿链**）、`ookla_mobile = false`（该国无移动榜 → 卡文案自动切宽带，MO/FJ）。

### 4.6 `hugo.toml` —— 站点配置 + 出站唯一控制点
**作用**：`[params.outbound]` 决定全站流量导给谁、带什么 rel/UTM。**换导流目标只改 `active = "roami"` 一行**。每品牌一个 target 块：

```toml
[params.outbound]
active = "roami"                    # 默认导流目标（自家）

[params.outbound.targets.airalo]    # key 必须与 providers.toml 品牌键一致
base = "https://www.airalo.com"
country_path = "/{slug}/"           # 可选：国家级深链模板，{slug} 会被替换；不配则只链首页
label = "Check on Airalo"           # 按钮文字
rel = "sponsored nofollow"          # 第三方；自家 roami 用 ""（follow）
[params.outbound.targets.airalo.utm]
source = "esimsift"
medium = "referral"
campaign = "partner"                # 页面级 campaign 自动覆盖：compare-<slug> / prov-<key>-<slug> / vs-<a>-<b>
```

### 4.7 `content/en/` —— 哪些手写、哪些生成

| 路径 | 性质 | 说明 |
|---|---|---|
| `compare/<slug>.md` ×50 | 生成初稿 + japan.md 手写样板 | front matter `iso` + `seo.description`，正文 3 段数据驱动分析（P-B 润色） |
| `compare/<slug>/<brand>.md` ×400 | **脚本生成，勿手改** | `gen_provider_pages.py` 重建时会覆盖/增删 |
| `compare/{a}-vs-{b}.md` ×28 | 手写（front matter 即可） | `providers: [a,b]` 字母序 + `layout: vs-single`；标题/描述自拟防同质化 |
| `compare/matchups.md` ×1 | 手写（front matter 即可） | 对决枢纽页：`layout: matchups` + **`nolist: true`**（不进国家网格/catalog/llms 国家清单——全站过滤器第三层）；卡片按 providers.toml 键枚举，**新增品牌自动出现** |
| `esim-providers/<key>.md` ×8 | 手写（front matter 即可） | 品牌详情页正文全部由模板聚合推导 |
| `guides/` ×5 | 手写正文 | **1677-1955 词**（2026-10-02 深度重写，备份 `_guides_backup_20261002/` 在项目根）；front matter 带 `date` + `faq_heading` + `faqs`（7-8 条）+ `hero` + `hero_alt`（首屏图，模板渲染 figure + og:image）；内链 9-14 条/篇（短锚文本全轮换）；正文计数一律 shortcode；数据盒由 guides/single.html 按文件名注入 |
| `research/` ×3 + `_index` | 手写 front matter | 正文由专属模板从数据推导；_index 枢纽 front matter 同 guides 带 `hero`/`faqs`（2026-10-02） |
| `tools/` `esim-deals/` `_index/about/methodology/disclosure/privacy/terms/contact` | 手写 | privacy/terms 有法律审校 Todo 标注 |

### 4.8 `static/img/`
`flags/<iso小写>.svg`（countries.toml flag 引用）、`countries/<slug>-01..04.webp`（每国 4 张：页面 3 张 + og:image）、`site/`（home-hero/og-default）、`esim/`、`providers/`（品牌真 logo：`<key>.png` 或 `.webp`，prov-logo 自动探测）。**logo 现状**：**8/8 全量接入**（.png ×6 + .webp ×2）。原始素材备份在 `static/img/logo/`（其中旧的 `logo.png` 是早期素材，已由 `roami.png` 取代）。

**favicon（2026-10-02，在 `static/` 根而非 img/）**：漏斗 = "Sift" 品牌标 —— `favicon.svg`（SVG 主，现代浏览器）+ `favicon.ico`（16/32/48 兜底）+ `favicon.png`/`favicon-16x16.png`/`favicon-32x32.png` + `apple-touch-icon.png`(180)。品牌色 `brand.600 #1A7E6B`。`head.html` 已接 4 个标签（icon×2 + apple-touch + theme-color）。**改图标**：直接覆盖 `static/favicon.*` 同名文件（零配置），想换形状就改 `favicon.svg` 的 `<path>`。

---

## 5. 模板与脚本清单

### 5.1 layouts/ 关键文件

| 文件 | 作用 |
|---|---|
| `compare/single.html` | 国家页（13 模块 + 表格筛选 JS：品牌 chips/Unlimited 开关/排序/有效期） |
| `compare/provider.html` | 品牌×国家子页（400 页共用） |
| `compare/vs-single.html` | 对决页（28 页共用） |
| `compare/matchups.html` | 对决枢纽页 /compare/matchups/（28 卡 + 计算瓦片） |
| `compare/list.html` | /compare/ 枢纽（国家网格 + #matchups 对决网格） |
| `esim-providers/single.html` | 品牌详情页（含无数据降级简壳） |
| `guides/single.html` | 指南页（逐篇数据盒 + FAQ schema + 内链闭环；compatibility 篇注入设备库交互块） |
| `partials/country-stats.html` | ★ 全站唯一国家级聚合入口（rows/perDay/perGB/minPrice/unlimitedCount/checkedDate；徽章=排序字面位置） |
| `partials/provider-agg.html` / `vs-agg.html` | 品牌级 / 对决级聚合 |
| `partials/cta-out.html` | ★ 全站唯一出站点（rel/UTM/深链全在这） |
| `partials/prov-logo.html` | logo 自动切换（fileExists 先探 .png 再探 .webp，都没有 → monogram） |
| `partials/schema.html` | BreadcrumbList（全站）+ Article（**自动**：`.IsPage` 且 Section∈guides/research 的 5+3 篇，date/author/hero 全取 front matter）—— **jsonify 必须 `| safeJS`**（Hugo 0.146+ 否则二次编码） |
| `partials/schema-org.html` | Organization + WebSite JSON-LD（全站实体锚点，AI 搜索识别品牌；sameAs 留空待官方 profile） |
| `index.llms.txt`（模板） | llms.txt 自动枚举 |
| `robots.txt`（模板） | 显式 Allow 15 个 AI/LLM 爬虫 + sitemap（`enableRobotsTXT=true` 下自定义模板优先） |

### 5.2 scripts/ —— 用法与危险等级

| 脚本 | 用法 | 危险等级 |
|---|---|---|
| `scrape/scrape_esimdb.py` | `python -X utf8 -u scripts/scrape/scrape_esimdb.py <brand>... [--force]` → `scripts/scrape/raw/<brand>/`（断点续跑：已有 json 跳过；重抓删对应 json 或 --force） | 安全（只写 raw/） |
| `scrape/scrape_holafly.py` | 同上，抓 holafly 官网 PDP（UAE 的 slug 是 `esim-dubai`，已在 VARIANTS 里） | 安全 |
| `scrape/extract_roami.py` | 从本机 Roami 项目源数据提取 → `raw/roami/` | 安全 |
| `scrape/toml_write.py` | `python -X utf8 scripts/scrape/toml_write.py <brand> [--dry-run]` → `data/plans/<brand>.toml`。**执行前确认顶部 `CHECKED` 常量是当天日期**（checked 字段全从这来）。--dry-run 只报 problems 不写文件 | ⚠ 覆盖该品牌 plans |
| `gen_provider_pages.py` | `python -X utf8 scripts/gen_provider_pages.py` 重建 400 子页（品牌集变更后必跑；**绝不碰 plans**） | 安全 |
| `validate.py` | `python -X utf8 scripts/validate.py` 8 组检查（国家/品牌键/套餐字段/join key/对决页规则/运营商画像） | 只读 |
| `audit_meta.py` | `python -X utf8 scripts/audit_meta.py [--limit N]` 扫 public/ 渲染产物（2026-10-02 规范 v3）：标题 48-54 内页禁品牌（首页唯一豁免）/ 描述 120-140 必含品牌 / 重复 / 分页型统计（改 meta 后必跑） | 只读 |
| `regen_meta_fixes.py` | 2026-10-01 批次E 一次性修复脚本（已被批次F regen_meta_brand.py 取代，勿重跑） | ⚠ 一次性 |
| `regen_meta_brand.py` | 2026-10-02 批次F meta 品牌规范脚本（幂等可重跑，--dry-run 先行）：50 国 desc 品牌版 / 28 VS 标题+desc（3 家族轮换）/ 29 手写页 map | 可重跑 |
| `check_hardcoded.py` | `python -X utf8 scripts/check_hardcoded.py` 硬编码总量守卫：扫 content/en + layouts + hugo.toml，命中"50 countries / 8 providers / 28 matchups"等写死总量即失败（国家页 seo.description 豁免——脚本再生的）。**新增国家/品牌或改模板后必跑** | 只读 |
| `check_headings.py` | `python -X utf8 scripts/check_headings.py` 渲染产物 h2/h3 标点守卫（`,` `;` `:` `—` `–` 全站 0 豁免；改模板/加内容后跑，需先 build） | 只读 |
| `append_carrier_info.py` | 追加 [ISO.info]（幂等，**已执行过，勿再跑**——再跑也只是提示跳过） | 幂等 |
| `gen_sample_data.py` | ☠☠☠ **永远禁止整跑** —— 会用 SAMPLE 数据覆盖全部真实抓取结果 | 禁令 |
| `scrape/verify_airalo.py` `probe_*.py` `discover_slugs.py` | 一次性验证/探测工具（airalo 官网对照校验已通过：JP/IT/US 全档一致） | 存档 |

---

## 6. 常用命令速查

```bash
cd "/d/HUGO test/29.1_windows-amd64/hugo_0.159.1_windows-amd64/esimsift"

npm run build                      # 完整管线：validate → Tailwind → hugo（上线前必跑）
npm run dev                        # Tailwind 预编译 + hugo server（本机 :1313）
python -X utf8 scripts/validate.py # 单独跑数据验证

# 数据刷新三连（改完 plans 后必做后两步）：
python -X utf8 scripts/gen_provider_pages.py   # ① 子页描述嵌着数字，必须重生成
python -X utf8 scripts/validate.py             # ②
npm run build                                   # ③
```

**Windows 注意**：python 一律带 `-X utf8`；文件编辑用 Edit/Write 工具，**绝不用 PowerShell Get-Content/Set-Content 批量改文件**（PS 5.1 会把无 BOM UTF-8 按 GBK 读写，中文/箭头变乱码还会吞 `<`）；bash 的 `cd` 不跨命令保持，每条命令里自己 cd。

---

## 6.5 操作指南索引（想做什么 → 走哪 + 命名规则）

| 我想…… | 走 | 一句话 |
|---|---|---|
| 新增一个品牌 | §7 | 抓数据 → 转 TOML → providers.toml → hugo.toml → 品牌页 → vs 页 → 生成子页 → 验证 |
| 给现有品牌加某国套餐 | §8 情况 A | 小操作（重抓或手补 `[XX]` 块） |
| 新增一个国家 | §8 情况 B | 大操作（6 处数据 + 生成器 + 双守卫） |
| 刷新价格 | §9 | 三连：重抓 → 转换 → 生成+验证+构建 |
| 新增一篇指南/博客文章 | §11 | 查 keyword-map → 建 md → 导航 → 验证 |
| 优化已有内容/标题/描述/FAQ/模板 | §12 | 改 → build → 三守卫 → 记录 |
| 小改动（折扣码/logo/导流/公司信息） | §10 | 一张表指路 |

**命名规则（新增国家/品牌/文章前先看，写错要回改）**：
- **国家**：`data/countries.toml` 键 `[XX]` = 大写 2 字母 ISO；`slug` = 小写连字符（`united-arab-emirates`）；`region` 必须精确匹配五个枚举（Asia / Europe / Americas / Africa & Middle East / Oceania）；flag = `img/flags/<iso小写>.svg`；`content/en/compare/<slug>.md` 文件名必须 = slug。
- **品牌**：`data/providers.toml` 键 `[key]` = 小写单词（`airalo`/`roamic`/`alosim`）；logo = `static/img/providers/<key>.png|.webp`（自动探测）；vs 页文件名 = `{a}-vs-{b}` **严格字母序**；品牌页 = `esim-providers/<key>.md`。
- **指南/博客文章**：`content/en/guides/<slug>.md`，slug = 小写连字符查询式（`how-to-install-esim`）；标题禁品牌、48-54 字符；描述 120-140 必含 "eSIM Sift"。

## 7. 操作手册 A：新增一个品牌（完整 10 步）

以新增第 9 家品牌 `xyz` 为例：

1. **抓数据**（三选一，产物都是 `scripts/scrape/raw/xyz/*.json`，50 国一文件）：
   - esimdb 有专页 → `python -X utf8 -u scripts/scrape/scrape_esimdb.py xyz`
   - 不在 esimdb（像 holafly）→ 参照 `scrape_holafly.py` 写官网 PDP 抓取器（注意 Yoast sitemap 通常不含 PDP，slug 用候选探测）
   - 自家/内部数据 → 参照 `extract_roami.py`
2. **转 TOML**：先改 `toml_write.py` 顶部 `CHECKED` 为当天 → `python -X utf8 scripts/scrape/toml_write.py xyz --dry-run` 确认 0 problems → 去掉 --dry-run 真写。**抽查文件确认 price 全是两位小数**。
3. **`data/providers.toml`** 加 `[xyz]` 块（字段见 §4.2；founded/公司事实要核实来源，别编）。
4. **`hugo.toml`** 加 `[params.outbound.targets.xyz]`（base/label/rel="sponsored nofollow"/utm）。
5. **品牌页**：新建 `content/en/esim-providers/xyz.md`，只写 front matter（title/description），正文由模板聚合。
6. **对决页**：与每个现有品牌组合，新建 `content/en/compare/{a}-vs-{b}.md`（文件名严格字母序）×8 个（**枢纽页 /compare/matchups/ 的卡片按 providers.toml 枚举，新品牌自动出现，无需改它**）：
   ```markdown
   ---
   title: "Xyz vs Airalo eSIM Compared: Prices & Verdict 2026"   # 自拟，别和现有 28 个撞框架
   description: "Which eSIM is cheaper, Xyz or Airalo? Computed comparison of entry prices, $/GB and fair-use caps."
   providers: ["airalo", "xyz"]    # 字母序！validate 会查
   layout: vs-single
   ---
   ```
7. **`python -X utf8 scripts/gen_provider_pages.py`** —— 生成 xyz × 50 国子页（同时会清掉不在 providers.toml 里的品牌的旧子页）。
8. **`python -X utf8 scripts/validate.py && npm run build`** —— 0 error 才算完。
9. **验证**：`/esim-providers/xyz/` 渲染正常、`/compare/#matchups` 出现新对决卡、sitemap/llms.txt 自动纳入（无需手工）、国家页表格出现新品牌 chip。
10. **可选收尾**：footer "Popular matchups" 列是手挑 6 组（`layouts/partials/footer.html`，缺页会静默跳过所以不必须改）；真 logo 放 `static/img/providers/xyz.png`。

**删除品牌**（反向操作）：providers.toml 删块 → hugo.toml 删 target → 删品牌页 md + 相关 vs md → **删 `data/plans/xyz.toml`** → `gen_provider_pages.py`（清子页）→ 删 `raw/xyz/` → validate + build。参考 nomad 退场就是这么做的。

---

## 8. 操作手册 B：给现有品牌新增一个国家的套餐

### 情况 A：国家已在 50 国内（如 airalo 新开始卖越南）—— 小操作
1. 数据二选一：
   - **重抓**（正规）：删 `scripts/scrape/raw/<brand>/<slug>.json` → `python -X utf8 -u scripts/scrape/scrape_esimdb.py <brand>`（只补缺的，其余跳过）→ 改 CHECKED → `toml_write.py <brand>`。holafly 用 `scrape_holafly.py`；roami 用 `extract_roami.py`。
   - **手补**（临时）：直接在 `data/plans/<brand>.toml` 加 `[VN]` 块（严格遵守 §4.3 字段规则，尤其 price 两位小数、type 口径）。注意下次重转会覆盖手补内容。
2. `gen_provider_pages.py` → `validate.py` → `npm run build`。
3. 验证：国家页表格多出该品牌行、`/compare/vietnam/airalo/` 子页出现、对决页判胜数字变化（全部自动）。

### 情况 B：新增第 51 个国家 —— 大操作（动 6 个地方）
1. `data/countries.toml` 加 `[XX]` 全字段块（region 必须精确匹配五个筛选值；slug 唯一）。
2. `data/faqs/<xx>.toml` 新建（6 条对比角度 FAQ）。
3. `content/en/compare/<slug>.md` 新建（front matter `iso = "XX"` + seo.description 占位 + 3 段分析；参考 japan.md 样板）。
4. 图片：`static/img/countries/<slug>-01..04.webp` ×4 + `static/img/flags/<xx>.svg`（路径与 countries.toml 对齐）。
5. `data/carriers.toml` 加 `[XX]` + `[[XX.profiles]]`（+ 可选 `[XX.info]`）。
6. 每品牌补 `[XX]` 套餐（抓取或手补，同情况 A）。
7. `gen_provider_pages.py` → `validate.py` → **`regen_meta_brand.py --dry-run` 确认后真跑**（新国家的 seo.description 由它按实时数据重写，含品牌词与字符数校验）→ `npm run build` → `audit_meta.py` + `check_hardcoded.py` 双守卫。
8. 自动纳入：首页区域网格、header 大菜单、sitemap、catalog.json、llms.txt、guides/research 页数据盒、对决页判胜表、matchups 枢纽 —— 全部无需手工。

**为什么第 8 步敢说"全部无需手工"（2026-10-02 去写死架构）**：全站总量数字分三层实时推导，没有一处写死"50 国/8 家/28 组"：
- **模板层**：`{{ len hugo.Data.countries }}` / `{{ len hugo.Data.providers }}` / 对决数 `{{ div (mul ...) 2 }}`（首页 hero、matchups、research、guides 相关卡等 7 处已改造）。
- **正文层**：4 个计数 shortcode —— `{{< count-countries >}}` / `{{< count-providers >}}` / `{{< count-app-providers >}}` / `{{< count-direct-providers >}}`（guides 正文、子页安装区用它们）。
- **front matter 层**：front matter 跑不了 shortcode → 一律**无数字措辞**（"every major travel eSIM provider" 而非 "8 providers"）；国家页 seo.description 是唯一例外（脚本从实时数据再生）。
- 守卫：`check_hardcoded.py` 会抓回归；新写内容时记住"数字要么从 data 推导，要么不出现"。

---

## 9. 操作手册 C：价格数据例行刷新（建议每 1-2 周）

```bash
cd "/d/HUGO test/29.1_windows-amd64/hugo_0.159.1_windows-amd64/esimsift"

# ① 改 scripts/scrape/toml_write.py 顶部 CHECKED = 当天日期（一处改，全品牌生效）

# ② 重抓（esimdb 七家，--force 全量；约几十分钟，挂后台）
python -X utf8 -u scripts/scrape/scrape_esimdb.py airalo saily yesim ubigi roamic alosim --force
python -X utf8 -u scripts/scrape/scrape_holafly.py --force
python -X utf8 scripts/scrape/extract_roami.py      # roami 从本机 Roami 项目提

# ③ 逐家转换（每家确认 0 problems）
for b in airalo saily yesim ubigi roamic alosim holafly roami; do python -X utf8 scripts/scrape/toml_write.py $b; done

# ④⑤⑥ 三连
python -X utf8 scripts/gen_provider_pages.py
python -X utf8 scripts/validate.py
npm run build
```

增量刷新（只更新个别国家）：只删对应 `raw/<brand>/<slug>.json` 再跑（不带 --force），转换器照常全量输出。
**刷新后注意**：全站推荐/对决判胜/排行榜/research 全是实时计算，数字会自己变；只有子页描述里的数字靠 ④ 重生成。

---

## 10. 操作手册 D：小改动的入口

| 想改什么 | 改哪里 | 生效范围 |
|---|---|---|
| 换/删折扣码 | `providers.toml` promo_* 字段组（删全组=模块全站隐藏；改 promo_pct 同步改 promo_label） | deals 页/国家页/子页/品牌卡/llms.txt |
| 改品牌公司信息（总部/商店链接/客服/退款） | `providers.toml` `[brand.info]` 子表（空串=该项隐藏） | 品牌页概况卡/客服退款区/覆盖备注/FAQ/schema |
| 换默认导流目标 | `hugo.toml` `[params.outbound] active` 一行 | 全站 cta-out |
| 改某品牌出站 URL/UTM | `hugo.toml` `[params.outbound.targets.<key>]` | 该品牌全部出站 |
| 放真 logo | `static/img/providers/<key>.png` 或 `.webp`（**8/8 已齐**；换新图直接覆盖同名文件） | 全站徽标自动切换 |
| 改 favicon/站点图标 | `static/favicon.svg` 改 `<path>` + 重新生成 `favicon.*`（见 §4.8） | 全站标签页图标 |
| 改国家页"怎么选/人群"推荐 | 不用改 —— 全是排序字面位置，改 plans 数据自动变 | — |
| 改 FAQ | `data/faqs/<iso>.toml`（页面 + schema 同步） | 对应国家页 |
| 改品牌优劣势/口号 | `providers.toml` strengths/weaknesses/tagline | 品牌页/国家页口碑区 |
| 加 guide/博客文章 | 走 §11 完整步骤（`content/en/guides/` 新 md；research 另配专属模板，现有 3 个 layout 参数分发） | 枢纽页自动列出 |

---

## 11. 操作手册 E：新增一篇指南/博客文章

> "博客文章"在本站 = `/guides/` 下的教程/概念解释长文（现 5 篇）。这是唯一的编辑型长文载体；research 是数据研究页（正文模板推导，不属于"写文章"），别混淆。

1. **查 `docs/keyword-map.md`** —— 确认目标关键词没被现有页占用（防蚕食）。guides 定位"教程/how-to/概念解释"长尾，**不抢** `/compare/{country}/` 的价格型关键词。
2. **建 `content/en/guides/<slug>.md`**，front matter 照抄现有 5 篇（六键 + faqs）：
   - `title`：48-54 字符，查询式或陈述式，**不带品牌词**，无冒号尾缀
   - `description`：120-140 字符，**必含 "eSIM Sift"**
   - `date`：当天 `YYYY-MM-DD`
   - `hero` + `hero_alt`：首屏图，从 `static/img/esim/` 133 张挑一张**与现有 6 张主题不撞车**（现用：071 旅行者/SIM 芯片、058 称重对比、007 清单、012 放大镜、018 登机双卡、142 图表研究）
   - `faq_heading` + `faqs`：6-8 条，`- q:`/`a:` 单行、**避免冒号**，走 FAQPage schema 同源
3. **正文 HARD RULE**（违反 = 打回）：h2/h3 禁 `, : — – ;`（用户意图问句/名词短语）；总量数字一律 shortcode（`{{< count-countries >}}` 等，**禁写死"50 国/8 家"**）；不编价格/套餐数字；内链 8-14 条/篇、1-3 词短锚全轮换、只链允许路径；"eSIM Sift" ≤1 次；美式英语；1500-1900 词。
4. **数据盒（可选）**：想要 "Live from our database" 计算盒，就在 `layouts/guides/single.html` 加一个 `else if eq $base "<slug>"` 分支（参考现有 3 个 $/GB 榜/入门价榜/unlimited 榜）。
5. **导航（手动，唯一一处不自动）**：`layouts/partials/header.html` 第 85-89 行 mega menu 加一行（6 篇后会挤，届时改"前 5 + All guides"）。
6. **验证**：`npm run build` → `audit_meta.py`（新页标题/描述合规）→ `check_headings.py` → `check_hardcoded.py`。
7. **自动纳入（无需手工）**：`/guides/` 枢纽列表、llms.txt、sitemap、其它 guide 的"相关阅读"卡。

## 12. 操作手册 F：未来优化标准动作（改内容的完整闭环）

任何"优化"（改标题/描述/正文/FAQ/模板）都走同一闭环，做完才离开：

1. **改前**：记下要动什么；批量改先备份到**项目根**（⚠ 禁止放 `content/` 下，会渲染成正式页面）。
2. **改**：只用 Edit/Write 工具或 `python -X utf8`（禁 PowerShell Get/Set-Content，GBK 乱码）；front matter 数字措辞、正文 shortcode。
3. **验**：`npm run build`（~37s，0 error 才算）+ **三守卫**：
   - `audit_meta.py`（标题 48-54 / 描述 120-140 含品牌 / 无重复）
   - `check_headings.py`（h2/h3 标点）
   - `check_hardcoded.py`（无写死总量）
   - 另加 `grep -rc "%!f" public/ --include="*.html" | grep -v ":0"`（验渲染无 nil）
4. **看**：抽 2-3 个受影响页的渲染 HTML（价格数字/图表/schema 是否真的出来了）。
5. **记**：结论 + 踩坑写进 `STATUS.md`（时间序日志）；结构/红线写进 `PROJECT.md`（红线只进 §14，别散落）。
6. **不要**：跑 ~10 分钟全量 hugo 单独验证（npm run build 已含）；永远不整跑 `gen_sample_data.py`。

## 13. 蓝图对照（还差什么）

蓝图 = 竞品对比报告（esim-comparison）+ `docs/keyword-map.md`。侧翼页型原本 0/6，现状态：

| 蓝图项 | 状态 |
|---|---|
| keyword-map（词簇→URL 唯一映射） | ✅ 完成，上新页型前查它 |
| VS 对决页 + 对决枢纽页 /compare/matchups/ | ✅ 28/28 + 枢纽索引页（closest/lopsided 计算瓦片） |
| research 数据研究页 | ✅ 3 页（price-index / unlimited / fair-use） |
| guides 指南页 | ✅ 5 篇 + 枢纽 |
| 区域枢纽页 ×5（/compare/asia/ 等） | ⬜ Phase 2 |
| /networks/{carrier}/ 运营商页 | ⬜ Phase 2（数据先补 networks） |
| /devices/{device}/ 设备兼容页 | ⬜ Phase 2（数据源 devices.toml 已备） |
| tools 第 2/3 个工具 | ⬜ Phase 2（已有行程计算器） |
| sitemap 分片（>1000 URL） | ⬜ 现在 507，暂不需要 |
| 国家页 authority 外链 | ✅ 2026-10-01：50 国 Opensignal/Ookla/Global Index 引用区（networkreports.toml） |
| 城市页 / 假评分 / 词数 KPI | ❌ 蓝图明确不做 |

唯一未落的 Phase 1 项：validate.py 锚文本分布静态检查（归 P-B，理由：真实内容产出后统计才有意义）。

---

## 14. 红线与坑（每条都真踩过）

1. **☠ `gen_sample_data.py` 永远禁止整跑** —— 会用 SAMPLE 覆盖 8776 条真实数据。`gen_provider_pages.py` 才是日常用的生成器（它绝不碰 plans）。
2. **price 必须两位小数 float**（`price = 13.50` 不是 `13`）—— int64 会让 Hugo `printf "%.2f"` 渲染成 `$%!f(int64=13)`（airalo 品牌页真实事故）。生成器已修，**手补数据时是唯一风险点**。修完可用 `grep -rc "%!f" public/` 验证。
3. **禁止 PowerShell Get-Content/Set-Content 批量改文件** —— PS 5.1 GBK 乱码会吃掉 `<` 标签。只用 Edit/Write 工具或 `python -X utf8` 脚本。bash heredoc 里含撇号（'）会挂 —— 脚本一律 Write 工具写文件再执行。
4. **hugo 不清理 public/ 旧页** —— 删页后 `rm -rf public` 再构建，或部署用 `--cleanDestinationDir`（曾经 /vs/ 旧页残留）。
5. **JSON-LD 必须 `| safeJS`**，且 md 正文禁止内联 JSON-LD（--minify 教训）—— 结构化数据全在模板层 `partials/schema.html`。
6. **`site.Data` 已弃用** → 一律 `hugo.Data`（`site.Params`/`site.GetPage` 不受影响）。
7. `[[faq]]` 顶层数组取值要 `.faq`。
8. 国家列表过滤是三层的：`where (where (where .Pages "Params.provider" nil) "Params.providers" nil) "Params.nolist" nil`（排除品牌子页、对决页、nolist 特殊页如 matchups 枢纽）—— 新模板列国家时照抄，别只抄两层。
9. esimdb 有 AWS WAF：curl 全被拦，必须 Playwright 本机 chromium；airalo.com 官网对高频访问限速（verify 脚本要慢跑）。
10. 并行 agent 最多 3 个（API 429）；被内存压力杀掉的后台任务**不自动重启**，等指令再续。
11. TOML 表数组（如 `[[XX.info.detail]]`）追加在文件末尾合法；validate.py 目前只校验 profiles 的 join key，追加 detail 后跑一遍确认。
12. **标题硬规则（用户定，2026-10-01）**：全站 `<h2>/<h3>` 必须一句话、用户视角，**禁止逗号/冒号/破折号碎片**（"X, honestly" / "A: B" / "W — and L" 全是反例；FAQ H2 一律用户问句如 "What should I know before buying a {C} eSIM"）。改模板后跑渲染扫描验证：`python -X utf8` 遍历 public/*.html 提取 h2/h3 文本查 `,:—–`（唯一豁免：/research/ 枢纽卡的文章主标题 "Title: Subtitle" 惯例）。
13. **`data/*.toml` 文件名禁止连字符** —— `network-reports.toml` 的数据键是带 `-` 的 `"network-reports"`，点号 `hugo.Data.networkReports` 取不到，模板静默渲染空卡且**构建不报错**（真实事故：45 国引用卡全部空白才发现）。已改名 `networkreports.toml`；新数据文件一律无连字符命名。
14. Go html/template 会把 href 里的 `(` `)` 编码成 `%28%29`（`| safeURL` 也拦不住；HK/Macao 的 Global Index 链接即如此）—— HTTP 等价，接受即可，别再花时间"修"。
15. `{{ with .field }}` 内 dot 被替换成字段值，再链 `.key` 会报 `can't evaluate field key in type string` —— 需要外层键时用 `range $b := $xs` 显式循环变量。
16. **`content/` 下 `_` 前缀目录不会被 Hugo 隐藏**（`_` 只对 static/data/partials 生效）——放进去的备份会渲染成正式页面（真实事故：guides 备份多渲染 6 个重复内容页）。**备份一律放项目根**（如 `_guides_backup_20261002/`）。
17. **改聚合 dict 键名要全链路改**：list.html 曾把条目键 `minPerGB` 改成 `v` 但下游没跟上 → `$%!f(<nil>)` 静默渲染且**构建 0 报错**。改完 grep `"%!f" public/` 验一遍（与红线 2 同源）。

---

## 15. 等用户决策/提供的事项（代码侧做不了的）

| 事项 | 影响 |
|---|---|
| ~~真实折扣码~~ | ✅ 2026-10-01 完成（3 家有码 5 家无码，见 providers.toml；仅 promo_expires 需上线前复核） |
| ~~8 张品牌 logo~~ | ✅ 2026-10-01 全量接入（providers/ 下 6 png + 2 webp） |
| **联盟深链格式确认**（每家国家级 URL 规则） | hugo.toml country_path + countries.toml slugs；影响转化归因 |
| **Roami 定价决策** | ⚠ 业务发现：数据算出 **Roamic 在 35/50 国比自家 Roami 便宜**（Roami 只赢 15 国）—— roami-vs-roamic 对决页如实展示了这个结论；要么调价要么接受 |
| networks 逐品牌官方数据来源确认 | 表格网络列 + ⑦b 增强 |

---

## 16. 上线步骤（到时候照着做）

1. P-A 清零（折扣码/深链/legal 审校/GA4/OG 图）。
2. `npm run build` 确认 0 error + `python -X utf8 scripts/validate.py` 0 warning。
3. `rm -rf public && npm run build`（干净产物）。
4. 部署 Cloudflare Pages（建议）：build command `npm run build`，输出目录 `public`，或 hugo 直接 `--cleanDestinationDir`。
5. 上线后：GSC 提交 sitemap.xml、GA4 核对 campaign（compare-<slug>/vs-<a>-<b>/partner）、llms.txt / catalog.json 可访问。
6. 之后进入 Phase 2（§3 P-2）+ 每 1-2 周数据刷新（§9）。

---

## 17. 回来接手时的 5 分钟热身清单

1. 读本文件 §0 状态快照 + `STATUS.md` 最后一节（最近一轮做了什么）。
2. `cd` 到项目目录，跑 `python -X utf8 scripts/validate.py` 确认数据没坏。
3. `npm run dev` 起 :1313 抽查：首页 / `/compare/japan/`（全模块国）/ `/esim-providers/airalo/` / `/compare/roami-vs-roamic/`。
4. 看本文件 §3 待办挑下一件事；动侧翼页型前先查 `docs/keyword-map.md`。
