# eSIM Sift 项目文档（交接手册）

> **用途**：隔几天回来接着干时，看这一份就能接上。写了什么、还缺什么、每个文件干嘛的、常见操作怎么做。
> **最后更新**：2026-10-08 **关键词采集换 Google 官方通道**（用户要求「关键词必须从谷歌搜索获取」）。本机网络事实：直连 `google.*` 全超时（DNS 污染 → `31.13.92.37`）；环境变量 `https_proxy=127.0.0.1:62216` 是**沙箱代理不通 Google**，而 curl / urllib 默认读它 → 全部**静默失败**；可用出口是**本机 Clash `127.0.0.1:7890`**，脚本必须显式指定。两条 Google 官方通道：**Suggest**（6,977 种子 × 5 市场，**100% 覆盖** → 11,573 词 / 含 esim 11,454 词）+ **Trends**（`relatedQueries` 给批内指数；`multiline` 批量比较 + **锚词归一**给**跨词可比热度**，锚词 `esim` 在 23 批里稳定 76.5–76.6）。★ **关键发现：补全证据 ≠ 真实热度，而且 `综合分` 会把词排反** —— `is esim available in portugal` 有 **51** 个种子带出、综合分 **88.8**（全站仅 17 词 ≥88.8），但批量比较实测相对热度 **0.0000**；`best esim for japan` 只有 **1** 个种子（种子里只有一个 `best esim`）、综合分 69.5，实测相对热度 **0.0054**。逐条查原始补全数据：前者是补全引擎给一大批国家种子都挂上的**通用问句模板**（来源横跨葡萄牙/克罗地亚/西班牙/土耳其/巴西）；后者若当初没撒那个种子就根本不存在于数据集。→ **`sources` 低不是「没人搜」，是「没撒对种子」；`sources` 高也可能只是「句式通用」。** 抽样 90 词里 **80 词（89%）低于 Trends 分辨率**；最热的是 `esim price`(0.0619)/`esim size`/`esim requirements`，**三者都归首页 `/`**，国家类里只有 `best esim for {国家}` / `esim price {国家}` 测到热度。★ **更正上一轮的错误论断**：不是「Bing 注入通用热门块」（实测两引擎两两 Jaccard 都是 0.000），真相是**地理簇内共享**（`buy esim for dubai` 的 57 个来源全是中东种子）。新增 7 个脚本。见 §5.2 / §14 红线 64–66
> **上一轮**：2026-10-08 **反同质化 P0/P0'/P1/P2 四项整改 + 同尺复算**（站点已全量上线，本轮是线上内容迭代）。① 品牌子页新增 `#localnotes` 区块，逐条渲染该国 `countries.toml` 的 `quirks`（此前 **400 页一条都没有**）；② `vs` 对决页 `#more` 从「每页 44 句 `X starts cheaper in N of M countries.`」改为**堆叠比例条 + 分数**；③ 品牌子页 `fup_note` 同页 3 处复述收敛为 1 处（`#fup` 页脚删除 + FAQ 两条改为结构化字段重组 + 区块内链）；④ 品牌 hub `Q9/Q11/#alternatives` 三处同源重复消除。**`vs` 占比 87%→72%、页内重复 1890→0；品牌子页页内重复 3953→1979；hub 236→133；新增真实内容 +2872 句槽**。基线重建 702 文件。见 §5.1 / §5.2 / §14 红线 60–61
> **上一轮**：2026-10-07 **第二批品牌扩容 · Jetpac 接入**（9 → 10 品牌，全链路打通：plans 877 条 / 49 国（缺 Fiji）/ 品牌档案 / 出站 target / **499** 子页 / **45** 对决页 / 50 国 meta + title 重算；零回归基线重建）。同轮修掉三处基础瑕疵：`bump_checked.py` 写回丢行尾（CRLF 文件混进 49 行 LF）→ 修；`jetpac.toml` 行尾混杂 → 统一 CRLF；`verify_provider_pages.py` 第 13 项（天数按钮）从「静默跳过」→ **显式双分支**。见 §5.2 / §14 红线 51–53
> 同日上一轮：**日期自动盖章 + Nomad 收尾** —— 页面日期不再靠人记得跑脚本：新增 `scripts/stamp_checked.py` 按**内容指纹**维护 `checked` / `profile_checked`（数据真的改了才把日期推到当天；改注释、调格式不动），已挂进 `npm run build` 第一步，台账 `docs/checked-state.json` **必须提交**；Nomad 的 logo 归位 `static/img/providers/`、价格核对日推到当天。见 §4.3 / §5.2 / §7.1 / §14 红线 47–49
> **上一批**：2026-10-06 **第二批品牌扩容·Nomad 试点**（8 品牌 → 9 品牌，全链路打通：plans 442 条 / 品牌档案 / 出站 target / 450 子页 / 36 对决页 / 50 国 meta + 6 条 title 重算；基线重建，见 §7 与 `docs/add-brands-plan-2026-10-06.md`。**jetpac 已于 2026-10-07 完成，gigsky / bnesim 待接**）
> 上一版：2026-10-02 批次G（guides 5 篇深度重写 + 首屏配图 / compat 设备库 UX / research 枢纽区域联赛+问答路由 / 全站去写死三层架构 + 双守卫脚本）+ **P0 host-networks 补真**（`networks` 全量 = 各国运营商，`backfill_networks_uniform.py`，见 §4.3）
> **配套文件**：`STATUS.md`（按时间顺序的施工日志，看"当时为什么这么做"）、`docs/keyword-map.md`（关键词→URL 唯一映射表，上新页型前必查）。

---

## 0. 项目一句话 + 当前状态快照

**eSIM Sift（esimsift.com）**：独立 eSIM 比价站，对标 esimdb.com / mybestsim.com。Hugo 0.159.1 + Tailwind CLI，英语站（目录已为多语言预留）。核心原则：**单一事实源** —— 所有数字只存在于 `data/*.toml`，模板层全部实时推导，改数据 = 全站数字自动刷新，永不手工改页面里的价格。

**当前状态（2026-10-07 Jetpac 接入后）**：

| 指标 | 数值 |
|---|---|
| 品牌 | **10 家**（airalo / holafly / saily / yesim / ubigi / roamic / alosim / nomad / **jetpac** + 自家 roami；**roami ≠ roamic，两个不同品牌**）。2026-10-06 起规划扩到 12 家（第二批 = nomad✅ / **jetpac✅** / gigsky / bnesim） |
| 国家 | 50 国（`data/countries.toml` 锁定）。**jetpac 只覆盖 49 国（缺 Fiji）** —— 所有 `#N of M` / `from N providers` 类计数一律按国实算，Fiji 页写 9 家、其余 49 国写 10 家（中德双语都验过） |
| 套餐总数 | **9095 条真实数据**：airalo 985 / holafly 298（官网 PDP 直抓）/ saily 471 / yesim 1652 / ubigi 483（含 80 条订阅）/ roamic 1791 / alosim 915 / roami 1181 / nomad 442 / **jetpac 877** |
| 构建 | **702 页，0 error**；sitemap 644 URL |
| 页面构成 | 50 国家页 + **499** 品牌×国家子页（9×50 + jetpac 49）+ **45** 品牌对决页（C(10,2)）+ **1** 对决枢纽页 /compare/matchups/ + **10** 品牌详情页 + tools/esim-deals/research×3/guides×5/about 等静态页 |
| 数据验证 | **十二项校验全绿**：`validate.py` 8 组 0 error 0 warning + `check_css_sync`（527 layout classes）+ `check_i18n`（**1514 key**，en/de 逐 key 对齐，模板引用 1484 个 key 未定义 0 个）+ `check_output`（704 文件 / 702 页 / 4028 段 JSON-LD）+ `check_headings`（**18303** 个 h2/h3，bad 0）+ `verify_provider_pages`（499 子页 13 项）+ `check_faq_facts`（R1–R11，`--selftest` **14 项**）+ `check_dates` + `check_hreflang`（647 条 / 645 页）+ **`check_article_agreement`**（冠词，产物级 + 源码级，`--selftest` **18 项**）+ **`verify_de_text`**（数据层文案本地化：fup_note 14 + promo_label 10 + quirks 101 = 125 条；源级 A–D + 产物级 E1–E4 + `--selftest` **20 项**）+ `verify_no_regression`（702 文件基线，`--selftest` 14 项） |
| 样式构建 | **Tailwind CLI 独立产出 `static/css/tailwind.css`（裸 `hugo` 不会重编译）**；`scripts/check_css_sync.py` 守卫模板 class 与编译产物同步（2026-10-03 加装） |
| 增信数据 | `data/devices.toml`（14 品牌 351 机型 + 12 不支持条目，2026-10 核对）+ `data/networkreports.toml`（44 国 Opensignal + 50 国 Global Index 深链）+ **`networks` 补真**（10 品牌全量 = 各国运营商；由 `backfill_networks_uniform.py` 统一回填，**该脚本是全局的**，见 §5.2） |
| 上线状态 | **已部署 esimsift.com**（手动上传 `public/`，无 CI；**本轮 Jetpac 改动尚未部署**）。GA4 已换真（`hugo.toml [params] ga4 = "G-J6SXGGEN8L"`）；折扣码 10/10 全量有码（`promo_verified` 逐条记核验日）；**联盟深链仍是模式假设**（`country_path` 未逐家核实；**jetpac 连 `country_path` 都没有** —— 其官网是 SPA，深链对任意路径返回 200 且标题现场拼接，见 §4.6）；logo **10/10 全有**。**部署前纪律**：停掉所有 `hugo.exe` → `npm run build` → `grep -c localhost public/llms.txt` 必须为 0 |
| 长尾词覆盖 | 关键词矩阵 `docs/keywords/google/`（11,454 词，Google 官方通道）已按 `kw-placement-plan-2026-10-08.md` **七批全部落地**：首页 price 族 / 指南 size·requirements / 子页验证四轴 / 国家页 FAQ 追加 4 问（6→10 问）/ `#verdict` 改 `best eSIM for {country}` / 品牌 Hub `#reviews` / 区域词·城市词并入既有页。**国家页 FAQ 10 个槽位在 50 国上全部逐问 md5 唯一（50/50）**，验收脚本 `scripts/_verify_round56.py`（130 项断言） |
| 反同质化 | **诚实口径（`audit_dup_raw.py`，不做归一化）**：品牌子页**逐字重复 ≈ 37–52%**（holafly 51.5% 最高 / saily 36.5% 最低）；残余 **18 种句型全是**「品牌级政策 + 方法论披露 + UI 说明」三类 —— **逐字一致是正确行为**。**归一化口径（`audit_boilerplate.py`）**：`vs` 72%、`provider_sub` 63%、`country` 64%、`provider_hub` 69%、`networks` 19%、`guides` 0% —— 该尺子把「带本页数字的句子」也算成模板，**只适合横向比页型，不能回答「Google 看到的重复有多少」**（见 §14 红线 63）。**页型级自证（2026-10-08 第五十六轮）**：跨页模块一律「抽文本算 md5 → 去重必须 = N」，实测国家页 FAQ 10 槽 = 50/50、`#quirks` 城市句 = 50/50、品牌 Hub `#reviews` = 10/10、区域指南新增问答 = 5/5 |
| hreflang | **en + de 双语，hreflang 必需**；`en-us` / `de-de`（连字符，非下划线）。**2026-10-08 修正来源侧守卫**：页面自身 noindex 或 404 时**一条都不发**（原先 54 个 noindex 德语页向外发单向标注）；目标侧只指向可索引译文。产物现状：**647 条 / 645 页**（`/` 与 `/de/` 各 2 条且互惠，其余为英文页自引用）。守卫 `scripts/check_hreflang.py` |


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
│   ├── providers.toml     # 9 品牌档案
│   ├── plans/<brand>.toml # 每品牌×国家套餐（9 个文件）
│   ├── carriers.toml      # 50 国运营商画像 + 城市明细
│   ├── devices.toml       # eSIM 兼容设备库（14 品牌 351 机型 + 12 不支持条目）
│   ├── networkreports.toml# 44 国 Opensignal 独立引用（⚠ 文件名禁连字符）
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
- ✅ **9 品牌 × 50 国真实套餐全量入库**（8218 条，来源与口径见各 plans 文件头注释：esimdb.com 单国套餐 USD 牌价；holafly 为官网 PDP USD 价表；**nomad 2026-10-06 接入**，源 `_competitors/*/raw/nomad/` → `scripts/scrape/raw/nomad/`（50 JSON）→ `toml_write.py nomad --checked 2026-10-04`）
- ✅ 抓取管线：esimdb 穿透 AWS WAF（本机 Playwright chromium）、holafly 官网 PDP 抓取器、roami 本地项目提取器、raw→TOML 转换器（断点续跑、坏数据进人工复核清单）
- ✅ 套餐建模规则（`toml_write.py`，详见 §4.3）：固定量 / 日额型 / unlimited（限速徽章识别）/ Ubigi Monthly·Yearly 订阅 / holafly FUP 透传 / 通用名重写
- ✅ `carriers.toml`：50 国 ~154 条运营商画像（速度区间/制式/覆盖特性）+ 50 国 `[ISO.info].cities` 主要城市 + 18 个关键市场 54 条逐运营商 strong/weak
- ✅ `devices.toml`（2026-10-01）：eSIM 兼容设备库 —— 14 品牌组 351 机型 + 9 组变体警告 + 12 条明确不支持；compatibility 指南页交互块（搜索/tab/chips）live 计数，增删机型无需改模板
- ✅ `networkreports.toml`（2026-10-01）：44 国 Opensignal 独立引用 —— 获奖≤3 事实卡 + Ookla 新闻式归属卡（页脚禁商业转载其数据）+ Global Index 深链卡 50 国兜底；HK/MO/TR slug 覆盖，IS/GE/KE/MO/CN/FJ 无报告自动降级 index-only
- ✅ **`plans/*.toml` `networks` 补真（P0，2026-10-02）**：**9 品牌 × 50 国 = 450 条** host-network 全量填充。规则 = **运营商是国家属性、与品牌无关**（同国同运营商），故直接取自 `countries.toml.carriers`（已验证与 `carriers.toml` profiles.name 逐条一致，0 mismatch），`scripts/backfill_networks_uniform.py` 一键幂等填充（**新增品牌转完 TOML 后必跑**）
- ✅ `validate.py` 8 组数据检查挂入 `npm run build`（坏数据进不了构建）

### 2.2 页面型
- ✅ **国家页** `/compare/<country>/`（50 页，全站核心）：TL;DR 三卡（按预算/性价比/长停留推荐，CTA 进站内子页）→ 13 模块：全套餐对比表（排序 + 有效期 chips + **品牌多选 chips + Unlimited only 开关**，纯客户端 data-* 过滤）、怎么选（按用量分档）、按人群×按时长 8 卡推荐矩阵、品牌口碑区（logo+名可点进品牌页）、运营商覆盖区（速度档位 + 主要城市 + 逐运营商优劣势）、**独立网络数据区**（Opensignal 事实卡 + Ookla 归属卡 + Global Index 深链卡，44 国核实 + 无报告国降级 index-only）、FAQ、出站表格、**「First time using an eSIM?」guides 五卡条**（锚文本按 `mod (len slug) 3` 三档轮换防同质化）
- ✅ **品牌×国家子页** `/compare/<country>/<brand>/`（**450 页** = 9 品牌 × 50 国，`gen_provider_pages.py` 生成，描述数字直读数据）
- ✅ **品牌对决页** `/compare/{a}-vs-{b}/`（**36 页** = C(9,2)，verdict-first + 逐国判胜表 + 数据驱动 FAQ + sibling 互链）+ **对决枢纽页** `/compare/matchups/`（**36 卡**全量索引 + closest rivalry/most lopsided 计算瓦片；header/footer/llms.txt 入口）+ vs 页 "Other eSIM comparisons" 勾选选择器（品牌 logo 卡最多勾 2 个，第 3 个挤掉最早勾选，字母序实时拼 `/compare/{a}-vs-{b}/`；**卡片按 `providers.toml` 枚举，加品牌自动出现**）
- ✅ **品牌详情页** `/esim-providers/<key>/`（**9 页**，计算式结论"cheapest in N of M"、竞争力评分、**价格胜负区（全计算：逐国 {B}最低价 vs 全场次优价，赢省%/输溢价% Top5 双卡带链接；>200% 用 ×倍数展示；unlimited-only 品牌带口径脚注；0 胜/0 负空态兜底）**、按区域覆盖清单；公司概况卡含总部/法人 + 官网/双商店链接 chips；客服&退款专区（渠道/邮箱/响应承诺 + 退款摘要）；覆盖区"50 国追踪≠品牌全部目的地"备注；FAQ 含 "{brand} support"/"{brand} refund" 长尾问答；schema 含 Organization(sameAs)；**无数据品牌自动降级为简壳页**）
- ✅ `/tools/` 行程计算器 **+ 用量估算器（对标 mybestsim data-usage-calculator 并反超：竞品止步于"你需要 X GB"，我们闭环到真实套餐）**：8 活动小时步进 → GB/天 → 行程总 GB（20% 余量开关，读取天数滑杆）→ 一键回填 chip 重选套餐；码率参考表（$acts 模板单一来源，11 行含 1GB 折算）；底部 12 热门国家卡 + **9** 品牌卡（全计算生成）+ FAQ×3+schema；`/esim-deals/` 折扣码页（对标 mybestsim 并超越：实码卡（核验日期+条款+折扣后实际价实时计算）→ "折扣码翻盘分析"表（折后价 vs 全场最低价，N/50 翻盘数）→ 无码品牌计算式替代价值 → 5 步使用教程 → 4 条无码省钱路径（全内链）→ FAQ×5+schema → 底部 **9** 品牌入口 + 4 相关页）
- ✅ `/research/` 3 页（price-index 50 国 $/GB 联赛表 / unlimited-esim 日费率榜 + **盈亏平衡分析** / fair-use-audit 逐品牌 FUP 审计）——全部从数据实时推导；**每行/每卡可钻取**（Winning plan 列链品牌×国家子页、区域卡列出全部国家 chips、unlimited 表品牌/套餐双链）；每页含计算洞察区 + 数据驱动 FAQ ×3-4 + FAQPage schema + Related research ×4 互联卡；unlimited-esim 首屏指标已解挤（全宽三卡条 + 品牌覆盖 chips）；**枢纽页 2026-10-02 升级**：首屏两栏配图（hero front matter 同 guides）+ **区域价格联赛**（region 聚合各国最优 $/GB 均值，5 卡排序）+ 最贵/最便宜价差叙事（计算倍数）+ **问答路由卡 ×6**（搜索意图→对应页）+ FAQ×6 schema + 正文 3 段立场声明
- ✅ `/guides/` 5 篇（what-is / how-to-install / vs-physical-sim / dual-sim / compatibility-check）：**2026-10-02 深度重写至 1677-1955 词**（对位竞品博客的信息增量段：SM-DP+ 手动录入、双线来电路由、区域变体机制、验机清单等；FAQ 7-8 条；内链 9-14 条/篇短锚轮换）；**每篇首屏配图**（front matter `hero`+`hero_alt`，imageConfig 宽高 + eager + fetchpriority=high + og:image 联动）；专用 `layouts/guides/single.html` 注入逐篇计算数据盒（$/GB 榜/入门价榜/unlimited 日费率榜/安装方式表，指标互不重复）+ front-matter `faqs` 渲染 FAQ + FAQPage schema + 相关阅读闭环；compatibility-check 篇专属注入 devices.toml 交互设备库（**品牌分组卡片**：搜索 + 品牌 tab + 351 chips + 变体内联警示 + 不支持表，与正文 EID 终审原则互指）
- ✅ 静态页：about / methodology / disclosure / privacy / terms / contact（disclosure 2026-10-01 已去除同司声明，改为佣金模式 + 诚实规则，勿再加回）

### 2.3 SEO / 基建
- ✅ 结构化数据全在模板层：国家页 FAQPage、子页 BreadcrumbList、品牌页 Product+Organization+FAQPage @graph、对决页 FAQPage（**不做假评分** —— 蓝图红线）
  - ⚠️ **品牌页曾挂 `Review`+`reviewRating`，2026-10-03 已移除**。两层原因：① `bestRating` 写成字符串且漏 `worstRating` → Google 退回默认 1–5 区间；② 评分是编辑部按价格库算的指数（多数品牌 0.0–1.2），而 Google 对 `itemReviewed` 为 **Organization/LocalBusiness** 的评分明确规定「評分必須直接來自用戶，請勿依賴人工編輯編制評分資訊」→ 编辑计算分不可充当 rating，会报「评分超出了指定范围」并触碰质量指南。现改为把该指数放进 Product 的 `additionalProperty`（`PropertyValue`）如实携带，页面可见读数不变。**想拿星级只有一条正路：上真实站内用户评分体系**
  - `offers` 的 `lowPrice`/`highPrice`/`offerCount` 必须是 **JSON 数字**（非字符串），由 `scripts/check_output.py` 守卫
- ✅ **AEO/GEO 三层（2026-10-02）**：Organization + WebSite 全站 509 页（`partials/schema-org.html`，实体锚点，sameAs 留空待官方 profile）；Article 自动覆盖 guides/research 8 篇（`partials/schema.html`，`.IsPage` 且 Section∈guides/research 门控）；`layouts/robots.txt` 显式 Allow 15 个 AI 爬虫 + sitemap

**每类页面 → 应带的结构化数据（新增页型时按此查漏）**：

| 页面类型 | JSON-LD schema |
|---|---|
| 首页 `/` | Organization + WebSite + BreadcrumbList |
| 国家页 `/compare/{country}/` | Organization + WebSite + **FAQPage** + BreadcrumbList + Product + AggregateOffer |
| 品牌页 `/esim-providers/{brand}/` | Organization + WebSite + **Product+AggregateOffer+Brand+additionalProperty** + FAQPage + BreadcrumbList（**2026-10-03 起不含 Review/reviewRating**，见 §2.3 说明） |
| 对决页 `/compare/{a}-vs-{b}/` | Organization + WebSite + FAQPage + BreadcrumbList |
| guides / research 文章 | Organization + WebSite + **Article** + FAQPage + BreadcrumbList |
| 工具/折扣页 `/tools/` `/esim-deals/` | Organization + WebSite + FAQPage + BreadcrumbList |
| 列表枢纽 `/compare/` | Organization + WebSite + BreadcrumbList |
- ✅ `llms.txt`（50 国 + 36 对决 + research/guides 自动枚举）、`catalog.json`（机器可读 50 国）、sitemap 585 URL（自定义 `layouts/sitemap.xml`：无 changefreq/priority；lastmod 三层解析——国家页=该国快照日 / 编辑页=自身 date / 其余=全站最新快照日）
- ✅ 出站导流单一出口：全站只有 `partials/cta-out.html` 一个出站点，`hugo.toml [params.outbound]` 一处配置（active 指向、rel、UTM、campaign 按页面类型自动）
- ✅ 品牌 logo：**8/9**（airalo/ubigi/yesim/roamic/roami/alosim=.png，holafly/saily=.webp，**nomad 暂用 monogram**——官网取不到可用 hex，`color="#16456B"` 是占位），prov-logo partial 先探 .png 再探 .webp；放 `static/img/providers/<key>.png|.webp` 即自动切换（零配置）
- ✅ 内链纪律：TL;DR/品牌区/锚文本全部指向站内；漏斗出口只在表格 View 列和 cta-out

---

## 3. 待完成功能（按优先级）

### P-A 数据项（上线前必须）
- [x] ~~折扣码换真~~ **2026-10-01 起，2026-10-04 复核，2026-10-06 随新品牌补齐**：**9/9 品牌全量有码**，`promo_verified` 逐条记核验日 —— roami `web20`(20%) / airalo `NEWTOAIRALO15`(15%) / holafly `MYESIMNOW5`(5%) / saily `VEEPEE25`(25%) / yesim `DREWDEAL`(20%) / ubigi `PROMO15`(15%) / roamic `FYESIM10`(10%) / alosim `ESIMTWEAKS`(15%) / **nomad `BEYOND20`(20%，另有 `FALL30` 30% 满 2 件 / `ESIMDNOMAD20`)**。**遗留**：仅 airalo 有官方过期日（2026-12-31），其余官方未标 → 上线前复核一次；条款/适用面写在各品牌 `promo_scope` / `promo_constraints` / `promo_terms`
- [ ] **联盟深链规则核实**：`hugo.toml [params.outbound.targets.*]` 的 `country_path` 和 `data/countries.toml [ISO.slugs]` 目前是模式假设（roami 假设 `/{slug}/`，其他家没配逐国深链）→ 逐品牌确认联盟链接的国家级 URL 格式
- [x] ~~**networks 补真**~~ **2026-10-02 完成（2026-10-06 随新品牌续填）**：按"同国同运营商"规则，9 品牌 × 50 国 `networks` 全量 = `countries.toml.carriers`（`backfill_networks_uniform.py`）。国家页表格网络列 + ⑦b 区块已自动增强
- [ ] **Opensignal 缺口（可暂缓）**：`networkreports.toml` 目前 44 国 Opensignal；剩 6 国只有 Global Index 深链兜底 —— CN/IS/GE/KE（用户 2026-10-02 决定"这 4 国算了"）+ MO/FJ（Opensignal 无对应市场报告）。若日后要补，格式照抄现有条目，数据由用户人工提供（禁 web 抓取）
- [ ] **carriers.toml 剩余 32 国 detail**：目前只有 18 个关键市场有逐运营商 strong/weak，其余国家只有 cities + 画像
- [ ] carriers.toml 速度区间逐市场核实（现值是编辑常识典型值）
- [ ] 逐国 quirks 人工复核（`countries.toml`，生成内容基于真实常识，上线前过一遍）
- [ ] Ubigi 订阅套餐（days=30/365）在排序/筛选里的显示是否合理，检查一遍

### P-B 内容期
- [ ] 49 国 3 段分析 + 6 条 FAQ 人工润色（生成器已出可读初稿；`content/en/compare/japan.md` + `data/faqs/jp.toml` 是手写样板）
- [ ] validate.py 增加锚文本分布统计（完全匹配 ≤20%）——真实内容产出后做才有意义
- [ ] 变体子页（cheapest/unlimited/long-stay）—— 等主站数据 ≥10 国再上，防关键词蚕食

### P-C 上线前
- [ ] privacy/terms/disclosure 法律审校（**2026-10-07**：原先直接渲染在正文里的 `Todo: legal review before launch.` 已移入 front matter 注释 —— 页面上不再出现待办文字；法律审校本身仍未做）
- [x] ~~GA4 ID 替换~~ **已完成**：`hugo.toml [params] ga4 = "G-J6SXGGEN8L"`，`head.html` 取该参数（`{{ with site.Params.ga4 }}` 门控）。**遗留**：与 roamiapp.com 的跨域衡量未配
- [ ] OG 图片（每国一张，含最低价数字）
- [x] ~~部署~~ **已部署 esimsift.com**（手动上传 `public/`；每次改动需重新上传，见 §16）

### P-2 蓝图 Phase 2（上线后，槽位已留在 docs/keyword-map.md）
- [ ] 区域枢纽页 ×5（/compare/asia/ 等）
- [x] ~~`/networks/{country}/` 单国运营商深度页~~ **2026-10-03 上线 12/50**（Japan ✅ 首版；US / DE / CA / FR / MX / TH / ES / KR / CN / GB / NL 同日批量补齐；余 38 国加 md + `networkreports.awards` 即可，版式零改）：`layouts/networks/single.html`（数据驱动：carrier 画像/品牌→网络表/城市/Opensignal+Ookla 记分板/FAQ schema）
  - **模板层去同质化（2026-10-03 第八轮）**：5 个数据驱动 H2 支持 front matter 覆盖钩子 `h2_carriers` / `h2_scoreboard` / `h2_brands` / `h2_cities` / `h2_next`（不写则落回默认句）；静态导语与「Keep reading / Keep exploring」卡片文案改为随国家与计数变化。**加新国家时不需要动模板**
  - **GEO 层（2026-10-03 第九轮）**：模板内固定三块 —— ① 「The short answer」直答块（front matter `prompt_answer` + 可选 `h2_answer`）；② 关键事实栅格（8 项全部推导 + front matter `fact_registration`，可选 `h2_facts`）；③ 运营商 `ItemList` JSON-LD 实体列表。llms.txt 由 `layouts/index.llms.txt` 动态收录每国页。**加新国家时只需在 md 里写 `prompt_answer` 与 `fact_registration` 两个字段**
  - **入链四条（全部 `site.GetPage` 门控，未建页不产生死链；2026-10-03 第二轮补齐）**：
    ① **页头 `Network map` 二级菜单**（`partials/header.html`）——列出所有已发布深度页（当前 12 条）；**0 个深度页时自动退回单链接**，加国家自动变长，不造假条目
    ② 枢纽 `/networks/` 目的地卡的「Carrier breakdown →」
    ③ 国家页 `/compare/{country}/` 的 Networks 段落内嵌回链
    ④ **品牌×国家子页 `/compare/{country}/{brand}/` 新增「Which network does {A} ride in {C}」段**（原本 400 页一条网络链都没有）——建满 50 国后自动变成 **450** 条入链
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
article = "The"           # 可选：需要定冠词的国家才有（US/GB/PH/NL/AE）。只用在主谓位置
                          #   （`{{ with $country.article }}{{ . }} {{ end }}{{ $country.name }} has N …`）
                          #   定语位置（`in {{ $country.name }}`）不要拼，否则出现 "in the The …"
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
networks = ["NTT Docomo", "SoftBank", "KDDI"]   # 该国本地运营商（= countries.toml carriers；同国同运营商，见下方"networks 规则"）

[[JP.plans]]
name = "Japan - 10GB / 30 Days"
gb = 10                  # unlimited 一律 0
days = 30                # 订阅：Monthly→30，Yearly→365
type = "data"            # "data" | "unlimited"
price = 13.50            # ★ 必须两位小数 float！price = 13 是 int64，Hugo printf "%.2f" 会渲染成 $%!f(int64=13)
fup_note = "…"           # 可选：限速说明/日额说明/订阅性质（fair-use-audit 页直接引用原文）
```

**日期字段 `checked` / `profile_checked` —— 自动盖章（2026-10-07 起）**
页面上四处机器可读的日期只有两个来源，都由 `scripts/stamp_checked.py` 按**内容指纹**自动维护：

| 字段 | 位置 | 喂给谁 |
|---|---|---|
| `checked` | `data/plans/<brand>.toml` 的 `[ISO]` 块 | 国家 hub / 品牌×国家子页 / 品牌 hub 的价格文案 / vs 页 / sitemap `lastmod` |
| `profile_checked` | `data/providers.toml` 的 `[<brand>]` 段 | 品牌 hub 的「Last updated」（与价格日取最大；价格专属文案只取价格日） |

**规则一句话：指纹变了（数据真的改了）→ 日期 = 构建当天；指纹没变 → 日期不动。**
指纹 = 段内容 sha256，**排除日期字段、注释与空行** —— 所以改注释/调格式不会让日期凭空前移
（那是不实陈述），改一个价格必然前移。

- 已挂进 `npm run build` 的**第一步**（`npm run stamp`），不依赖人记得跑。
- **首次建台账**（`docs/checked-state.json` 不存在）只登记现值、**不**改日期；
  台账已在而冒出**新单元**（新品牌 / 新市场入库）→ 直接盖当天。
- **`docs/checked-state.json` 必须提交进版本库**：删掉它等于把所有数据的「最后改动日」抹成未知。
- 手工盖特定日期仍走 `bump_checked.py`；指纹没变时 stamp **尊重你的现值，不会回滚**（真去官网重核过一遍、价格恰好没变的情况）。

⚠️ 口径**不是**「构建日」：用 `now` 会让 `lastmod` 每次部署都翻新，Google 判定本站
`lastmod` 无信息量后**整体忽略**（第二十三轮试过、已撤回）。只有跟着数据走的日期才值得抓取预算。

**目前「不」驱动任何页面日期的数据源**（改了它们，页面日期不动）：
`data/countries.toml`（国家 hub 正文：quirks / region / neighbors …）· `data/de/countries.toml`（德语国名覆盖）·
`data/carriers.toml`（运营商卡 `#hostnetwork`）· `data/refs.toml`（运营商官方外链）·
`data/faqs/<iso>.toml`（FAQ 问答文案）· `data/titlesegments.toml`（标题片段）。
要让它们也驱动日期，得先回答「这些页面的日期印在哪儿」—— 目前这些页面**压根没印日期**，
所以这是产品决定，不是技术缺口（见 §15）。

**networks 规则（P0 已定，2026-10-02）**：运营商是**国家属性、不是品牌属性**——同一个国家里每家 eSIM 品牌骑的都是同一批本地网络。所以 `networks` 直接 = `countries.toml` 里该国的 `carriers` 列表，**不要逐品牌去查**。`toml_write.py` 生成时会先写 `networks = []`，随后跑 `python -X utf8 scripts/backfill_networks_uniform.py` 一键填满全部 9 家（幂等，重跑安全）——**每接入一个新品牌、转完 TOML 后立刻跑一次**。

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
**作用**：国家页 FAQ 模块 + FAQPage schema。文件名 = 小写 ISO（`jp.toml`）。顶层是 `[[faq]]` 数组（模板取值 `.faq`）。6 条 = 前三条**数字类**（最便宜 / unlimited 计数 / Airalo vs Holafly）+ 后三条**事实类**（ID 规定 / 运营商 / 邻国）。只做**对比角度**（激活/安装类问题归 Roami 主站，防 SERP 重叠）。

**规则一：三条数字类答案只写 `{token}`，绝不填真实数字**（2026-10-07 第四十一轮）
这三条的真值随每次抓价变化，写死就会与正上方价格表打架 —— 2026-10-06 实测 99 条断言过期、45 国「最便宜品牌」易主。
值由 `layouts/partials/faq-live-tokens.html` 在构建期现算（32 个 token，口径见该文件头注释），
`compare/single.html` 渲染前做一次替换，可见正文与 FAQPage schema 同源。
- 可用 token 一览就写在 `faq-live-tokens.html` 返回的 dict 里（`cheap_*` / `value_*` / `unl_*` / `ah_*` / `neighbor*` / `brands_list` / `plan_count` …）。
- **拼错 token 名不会报错**：`replace` 找不到就原样留下，页面会出现 `{cheap_brad}`。由 `scripts/check_faq_facts.py` 的 R1 拦住。
- 任一取值缺失时 token 输出 `n/a`（不空着），由守卫的 R2 拦住 —— 别把 `n/a` 当成正常文案。
- **`{country}` 是无冠词形式**（`USA` / `UK` / `Japan`；德语站是 `Vereinigte Staaten`），所以只能写
  `for {country}` / `{country} plans` / `{country} alone`，**不能写 `the {country}`** —— 会渲染成 "the Japan"。

**规则二：49 国的答案骨架由 `scripts/faq_frames.py` 统一分配，别手改**（第四十二轮）
每条答案 = **open（直接回答，最可能被答案引擎摘走的第一句）+ body（数据事实）+ close（行动建议）**，
每槽 7 个片段共 21 个；分配 `a = i % 7`、`b = i // 7`、`c = (a + b) % 7`（i = ISO 升序位次，jp 除外）。
这是**拉丁方阵**：(a,b) / (a,c) / (b,c) 三组对子各把 7×7 的 49 格用满一次 ⇒
**任意两国的三元组至多在一个分量上相同 = 任意两页最多共用一句**。
- 池子必须 ≥ 7：49 国要两两 (a,b) 不重复就需要 `|pool|² ≥ 49`，改成 6 立刻退化。
- **手改某国文案必须同步片段库**，否则守卫 R10 报「拆不回片段库」。这是有意设计：防止数据与库各说各话。
- 片段里禁写 `$数字`；`{unl_allowance}` 只能放在**冒号之后**（ubigi 的值是整句
  "Varies by plan - published per plan page"，冒号后大写是合法英文，内嵌进从句就不成句）。
- `--check` 离线校验分配不变量与片段写法；`--force` 是改了片段库要重刷全站时用的（**会覆盖人工润色**）。
- jp 除外：它三条是手写的分析口吻，不参与方阵（R10 跳过 jp）。

**规则三：Q6（「一张 eSIM 能覆盖 X 和邻国吗」）的问题与 answer token 是一对，改一个要看另一个**（第四十二轮）
- 43 国的问题**点名一个邻国**（`Can one eSIM cover the UK and France?`），而这个点名是**载荷**：
  `{neighbor}` 会去问题里找那个国家名（`faq-live-tokens.html`：`in $q6 .`），找不到才退回 `neighbors[0]`。
  **所以问题里写谁，答案就答谁** —— 英国的问题问法国，答的就是法国（机械取 `neighbors[0]` 会答成爱尔兰）。
- 7 个**没有 `neighbors`** 的国家（HR / IS / CR / IL / MA / ZA / KE）问题**点名 `region`** 而不是邻国
  （`Can one eSIM cover Iceland and the rest of Europe?`）—— 原先是 `Can one eSIM cover Iceland?`，
  同义反复、抓不到任何区域意图。问题文本是**各国静态字符串**（`q` 字段不过 token 替换管线，只有 `a` 会）。
- `{neighbor}` 对无邻国走兜底 `"another country"`（曾写作 `"another market on this site"` —— 内部口吻印进了 12 页）。
- `{neighbors_all}` 对无邻国兜底 `the other {region} markets we cover`（**仅克罗地亚用到，略微自指，已知残留**）。

改完必须跑 `npm run build`（守卫在 `check:output` 里）。

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
| `compare/<slug>/<brand>.md` ×450 | **脚本生成，勿手改** | `gen_provider_pages.py` 重建时会覆盖/增删 |
| `compare/{a}-vs-{b}.md` ×36 | **脚本补缺 + 手写并存** | `providers: [a,b]` 字母序 + `layout: vs-single`；标题/描述由 `regen_meta_brand.py` 按数据重算防同质化。**新增品牌用 `scripts/gen_vs_pages.py` 只补不存在的对，绝不重写已有页** |
| `compare/matchups.md` ×1 | 手写（front matter 即可） | 对决枢纽页：`layout: matchups` + **`nolist: true`**（不进国家网格/catalog/llms 国家清单——全站过滤器第三层）；卡片按 providers.toml 键枚举，**新增品牌自动出现** |
| `esim-providers/<key>.md` ×9 | 手写（front matter 即可） | 品牌详情页正文全部由模板聚合推导 |
| `guides/` ×5 | 手写正文 | **1677-1955 词**（2026-10-02 深度重写，备份 `_guides_backup_20261002/` 在项目根）；front matter 带 `date` + `faq_heading` + `faqs`（7-8 条）+ `hero` + `hero_alt`（首屏图，模板渲染 figure + og:image）；内链 9-14 条/篇（短锚文本全轮换）；正文计数一律 shortcode；数据盒由 guides/single.html 按文件名注入 |
| `research/` ×3 + `_index` | 手写 front matter | 正文由专属模板从数据推导；_index 枢纽 front matter 同 guides 带 `hero`/`faqs`（2026-10-02） |
| `tools/` `esim-deals/` `_index/about/methodology/disclosure/privacy/terms/contact` | 手写 | privacy/terms 的法律审校待办写在 front matter 注释里（**不渲染到页面**；2026-10-07 前是正文行，被 Markdown 当斜体印出来了） |

### 4.8 `static/img/`
`flags/<iso小写>.svg`（countries.toml flag 引用）、`countries/<slug>-01..04.webp`（每国 4 张：页面 3 张 + og:image）、`site/`（home-hero/og-default）、`esim/`、`providers/`（品牌真 logo：`<key>.png` 或 `.webp`，prov-logo 自动探测）。**logo 现状**：**8/8 全量接入**（.png ×6 + .webp ×2）。原始素材备份在 `static/img/logo/`（其中旧的 `logo.png` 是早期素材，已由 `roami.png` 取代）。

**favicon（2026-10-02，在 `static/` 根而非 img/）**：漏斗 = "Sift" 品牌标 —— `favicon.svg`（SVG 主，现代浏览器）+ `favicon.ico`（16/32/48 兜底）+ `favicon.png`/`favicon-16x16.png`/`favicon-32x32.png` + `apple-touch-icon.png`(180)。品牌色 `brand.600 #1A7E6B`。`head.html` 已接 4 个标签（icon×2 + apple-touch + theme-color）。**改图标**：直接覆盖 `static/favicon.*` 同名文件（零配置），想换形状就改 `favicon.svg` 的 `<path>`。

---

## 5. 模板与脚本清单

### 5.1 layouts/ 关键文件

| 文件 | 作用 |
|---|---|
| `compare/single.html` | 国家页（13 模块 + 表格筛选 JS：品牌 chips/Unlimited 开关/排序/有效期） |
| `compare/provider.html` | 品牌×国家子页（499 页共用）。**2026-10-08 第五十二轮**：新增 `#localnotes` 区块（渲染该国 `countries.toml.quirks`，导语如实标注「国家级事实，非品牌卖点」）；删除 `#fup` 表格页脚（`#reality` 政策卡已给同一段）；`faq_a_unlimited` / `faq_a_hotspot` 改为结构化字段（`fup_allowance` / `hotspot_allowance`）重组 + 区块内链（`#fup` / `#reality`），不再逐字复述 note，但答案保持自包含 |
| `compare/vs-single.html` | 对决页（45 页共用）。**2026-10-08**：`#more` 区块 45 张卡从「`X starts cheaper in N of M countries.`」（全站 1980 条 / 骨架 2 种 / 同页 44 遍）改为**堆叠比例条（品牌色=第一家胜、灰=平手、余下=第二家胜）+ `aWins/countries` 分数**；口径说明上移区块导语（`compare_vs_single__bar_split_legend`，每页只说一次）；数据条 `aria-hidden`，链接可访问名称由 `A vs B` + `See the verdict` 提供 |
| `compare/matchups.html` | 对决枢纽页 /compare/matchups/（36 卡 + 计算瓦片） |
| `compare/list.html` | /compare/ 枢纽（国家网格 + #matchups 对决网格） |
| `esim-providers/single.html` | 品牌详情页（含无数据降级简壳）。**2026-10-08**：Q9 退款不再整段复制 `info.refund` →「链回 `#support` 卡片 + 讲时间窗口的实操」；Q11 热点不再内嵌 `hotspot_note` → 用 `hotspot_allowance` 重组；`#alternatives` 9 张竞品卡从 `Cheapest in N of M countries.`（数字撞车时同页逐字重复）改为**比例条 + 分数** |
| `networks/list.html` | /networks/ 网络地图枢纽（目的地卡 + 跨网分组 + 右栏） |
| `networks/single.html` | 单国运营商深度页 /networks/{country}/（数据驱动；版式对齐 guides） |
| `guides/single.html` | 指南页（**版式基线**：窄阅读列 + 首屏配图 + 逐篇数据盒 + FAQ schema + 内链闭环；compatibility 篇注入设备库交互块） |
| `guides/region.html` | 区域指南（5 篇区域聚合表，宽版式，未挂右栏） |
| `partials/aside-destinations.html` | ★ 右侧吸顶内链模块：11 个高价值目的地里按 `hash.FNV32a RelPermalink` 轮转出 6 条（排除当前国），服务端渲染，链 `/compare/{slug}/`。改目的地池只动这一处 `$pool` |
| `partials/country-stats.html` | ★ 全站唯一国家级聚合入口（rows/perDay/perGB/minPrice/unlimitedCount/checkedDate；徽章=排序字面位置） |
| `partials/provider-agg.html` / `vs-agg.html` | 品牌级 / 对决级聚合 |
| `partials/cta-out.html` | ★ 全站唯一出站点（rel/UTM/深链全在这） |
| `partials/prov-logo.html` | logo 自动切换（fileExists 先探 .png 再探 .webp，都没有 → monogram） |
| `partials/head.html` | `<head>` 全量（title/desc/OG/canonical/hreflang/字体/CSS/GA4）。**hreflang 两侧都要守（2026-10-08）**：目标侧只指向可索引译文；**来源侧 —— 页面自身 noindex 或 404 时一条都不发**。⚠ 该文件的模板注释**必须单行**（多行注释里的换行会变成输出文本，全站每页多一行空白，`--diff` 归因失效，见 §14 红线 62）。守卫 `scripts/check_hreflang.py` |
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
| `scrape/toml_write.py` | `python -X utf8 scripts/scrape/toml_write.py <brand> [--dry-run] [--checked YYYY-MM-DD]` → `data/plans/<brand>.toml`。**默认 `CHECKED` 常量 = 首批抓取日 `2026-09-30`**；非首批批次用 `--checked` 显式写 **raw 的真实抓取日**（**不是"今天"** —— jetpac 的 raw 是 10-04 抓的，写成 10-07 就是文件头印假日期，2026-10-07 实测踩过）。之后再 `bump_checked --brand <b>` 把**页面声明的核对日**推到当天 —— **文件头 = 抓取日，块内 `checked` = 页面核对日，两者本来就不是同一个东西**。--dry-run 只报 problems 不写文件 | ⚠ 覆盖该品牌 plans |
| `stamp_checked.py` | `python -X utf8 scripts/stamp_checked.py` **（2026-10-07 加，已挂在 `npm run build` 第一步）**：按**内容指纹**自动维护 `checked` / `profile_checked` —— 指纹变了就把日期盖成当天，没变就不动。首次建台账保留现值；台账已在而出现新单元（新品牌/新市场）盖当天。`--check` 只读、该盖未盖退 1；`--dry-run` 预演；`--date` 指定；`--selftest` **29 项**（含"改注释不触发""新增块盖当天""幂等"等反例）。台账 `docs/checked-state.json` **必须提交**。**它只认 `data/plans/*.toml` 与 `data/providers.toml`**，其余数据源见下方「不驱动日期的数据源」 | ⚠ 改写 plans + providers 的日期行 |
| `bump_checked.py` | `python -X utf8 scripts/bump_checked.py --brand xyz [--countries US,PL] [--date YYYY-MM-DD] [--dry-run]`，`--show` 一览各品牌当前日期（含"全站存在多个数据日期"提示 —— 多日期是**正常**的：每个品牌/国家声明自己的核对日）。**手工**把指定国家盖成指定日期 —— 真去官网核了一遍、价格恰好没变时用；日常刷新**不需要**它。**写回时保持文件原有行尾**（CRLF 文件改完还是 CRLF；丢行尾会让 hugo 因注释里的孤立 `\r` 整站构建失败，见 §14 红线 51） | ⚠ 覆盖该品牌 plans 的日期行 |
| `gen_provider_pages.py` | `python -X utf8 scripts/gen_provider_pages.py` 重建**全部**品牌×国家子页（当前 **499** = 9×50 + jetpac 49；某品牌缺某国就自动不生成，`#N of M` 分母也按国实算）。品牌集变更后必跑；**绝不碰 plans**。会顺手删掉已不在 `providers.toml` 里的品牌子页 —— ⚠ **但它不清理对决页**（见 §14 红线 53） | 安全 |
| `gen_vs_pages.py` | `python -X utf8 scripts/gen_vs_pages.py` **只补** `content/en/compare/{a}-vs-{b}.md` 缺失的品牌对，**绝不重写已有页**（品牌集变更后跑）。标题/描述复用两个标题族 + 字符数 48-54 / 120-140 断言 | 安全（只补缺） |
| `check_faq_facts.py` | `python -X utf8 scripts/check_faq_facts.py` **FAQ 守卫（2026-10-07 加，须在 `hugo` 之后跑）**：**读 `public/` 产物**独立从 `data/plans` 重算真值逐条对账 —— R1 无未替换 `{token}`；R2 无 `n/a`/`$0.00` 哨兵漏出；R3 问题集合与 toml 一致；R4 可见正文与 FAQPage JSON-LD 同文；R5/R6/R7 三条答案的品牌与价格与现算一致；R8/R9 文案不变量（最便宜不是 Airalo/Holafly、最便宜档必须计量）。**必须读产物**：源文本里现在只有 `{token}`，模板写错在源文本里看不出来。**R10 例外地读源文件**（判的是句架，产物里 token 已变成各不相同的数字国名，反而看不出重复）：a) **七个槽的答案**（slot1–3 + q7–q10，2026-10-08 起 SLOTS 是 3-tuple，带 key）49 国骨架两两不同；b) 每条答案必须拆得回 `faq_frames.py` 的片段组合；c) 任意两国最多共用一个槽；d) slot6 取自库内 7 变体且无邻国的 7 国各占一个；e) slot6 必须含 `{country}`。**R11 读产物**：Q6 在各国页上必须两两不同 —— R10(e) 在源级保证它，但**源级看不见**「互称邻国的一对国家（FR/IE 都指向 UK）分到同一变体」会不会撞车，只有在产物里才暴露（这条规则就是被那个真实 bug 逼出来的，实测对修复前的产物跑会精准报出 `R11 [en] ['FR','IE']`）。`--selftest` **13 项**（`selftest()` 7 例 R1-R9 + `frame_selftest()` 6 例 R10，含"正确样本不误报"）。已挂进 `npm run check:output` | 只读 |
| `faq_frames.py` | FAQ 答案骨架库 + 分配 + 迁移（2026-10-07 第四十二轮；**2026-10-08 第五十六轮扩到 7 槽**）。`--check` 离线校验分配不变量；默认只替换**认得的旧骨架**，其余拒绝改写（保护人工润色）；`--force` 重刷全站（覆盖人工润色）。**2026-10-08 起**：`SLOTS` 由 2-tuple 变 **3-tuple**（加 key），共 7 个 slot —— slot1–3 原样 + `q7` 可用性 / `q8` 设备 / `q9` 号码 / `q10` 口碑 四个新片段池（各 7×3 段）；`rewrite()` 新增**追加模式**（末尾追加 `[[faq]]` 块）+ `stats["added"]`，用于把新问答灌进 50 个 `data/faqs/*.toml`（模板池 49 国 × 4 条 = 196 + `jp.toml` 手写 4 条）。⚠ **池子必须 ≥ 7** —— 拉丁方阵 `a=i%7, b=i//7, c=(a+b)%7` 靠 (a,b)/(a,c)/(b,c) 三个双射保证「任意两国最多共用一句」。⚠ **`data/faqs/*.toml` 是 CRLF**（49/50），`Path.write_text()` 会偷偷转 LF，必须 `read_bytes`/`write_bytes` 保持原行尾。**取代**了第四十一轮的一次性 `migrate_faq_frames.py`（已删除） | 幂等（改 faqs 文案） |
| `validate.py` | `python -X utf8 scripts/validate.py` 8 组检查（国家/品牌键/套餐字段/join key/对决页规则/运营商画像） | 只读 |
| `audit_dup_raw.py` | `python -X utf8 scripts/audit_dup_raw.py` **诚实口径重复度量（2026-10-08 第五十三轮加）**：**不做任何归一化**，把产物里的 prose 句子逐字比 —— 输出「逐字重复槽位占比」+「其中不含任何数字/国名/品牌名的纯模板句清单」。**与 `audit_boilerplate.py` 的分工**：后者把数字→`#`、名字→`@` 再比骨架（适合**横向比页型**），前者回答**「Google 看到的重复有多少」**。⚠ 一把尺子回答一个问题，别混用（见 §14 红线 63）。**不进 `npm run build`** | 只读 |
| `check_hreflang.py` | `python -X utf8 scripts/check_hreflang.py` **hreflang 守卫（2026-10-08 第五十三轮加，已挂进 `check:output`）**：读产物判四条 —— A 页面自身 noindex 却发了 hreflang（Google 不处理，且会造成单向标注）／B hreflang 指向的产物必须真实存在／C 必须**互惠**（P 指向 U 则 U 必须回指 P，否则 GSC 报 *No return tags* 并整体忽略）／D 目标不得是 noindex。`--selftest` **7 例**（干净互惠对不误报 / 站外 href 不误判 / A·B·C·D 各一反例）。**新增守卫必须双向验证**：先对改前旧产物跑（实测 `54 problem(s)`，正是 54 个 noindex 德语页），再对修完的产物跑 | 只读 |
| `audit_boilerplate.py` | `python -X utf8 scripts/audit_boilerplate.py [--type <页型>] [--group-by brand\|country] [--show N] [--limit N]` **反同质化诊断（2026-10-07 第四十六轮加）**：只读 `public/`，取 prose 标签（`p/li/blockquote/figcaption`）按 `[.!?]` 切句取 ≥25 字符，**品牌名与国名→`@`、数字→`#`** 两级归一化，输出 = **占用的句子槽位比例**（槽位=全组句子总数；模板槽位=Σ 该模板句出现的页数）+ 页内重复槽位。⚠ **不进 `npm run build`** —— 诊断工具不是守卫，给阈值就会被「优化掉」。⚠ **归一化使它高估重复**（「带本页数字的句子」也被算成模板）→ 报数必须写明口径 | 只读 |
| `kw_harvest_google.py` | `python -X utf8 scripts/kw_harvest_google.py [--probe\|--smoke] [--markets a,b] [--workers N]` **Google Suggest 采集（2026-10-08 第五十四轮加）**：走**显式代理 `http://127.0.0.1:7890`**（脚本内 `PROXY` 常量）—— ⚠ 不显式指定会继承环境变量里的沙箱代理 `62216` 而**全部静默失败**（现象是空响应，不是报错）。种子 6,977 × 5 市场；**种子用「用户真会打的短名」**（usa/uk/uae/turkey，而非 `countries.toml` 的 `name`）。`client=firefox` 返回 `[query,[sugg…],[],{}]`，**第 0 位是种子回显必须剔除**。全量约 25 分钟 | 只读 |
| `kw_trends.py` | `python -X utf8 scripts/kw_trends.py [--probe] [--from-scored N] [--merge] [--workers 2]` **Google Trends 相关查询（第五十四轮加）**：`explore` → `RELATED_QUERIES` widget → `relatedsearches`；响应以 `)]}'` 开头（XSSI 前缀）需剥。⚠️ **429 极频繁**（约每 2-3 请求一次）→ 必须**指数退避 6/12/24/48s**（线性短退避无效）。`top` 的 value 是 0-100、`rising` 的 value 是绝对量且 `formatted` 为 `Breakout`。⚠️ `--from-scored N` 补种子**只能发现新词**，**不会**给这些词自身加指数（指数来自 relatedQueries，列表里不含种子自己） | 只读 |
| `kw_trends_compare.py` | `python -X utf8 scripts/kw_trends_compare.py [--probe]` **跨词可比的官方热度（第五十四轮加）**：5 个词放进同一次 `comparisonItem` 查 `TIMESERIES`（`multiline`）。因 Trends **按批归一化**（批内最热词 = 100）跨批不可比 → 每批固定带**锚词 `esim`**，用 `相对热度 = 均值(词)/均值(锚词)` 归一。**实测锚词在 23 批里稳定 76.5–76.6**，证明归一有效。另出 `目标内指数`（本表最热目标词 = 100）—— 因为长尾词相对 `esim` 只有 0.0x 量级，直接看不好读 | 只读 |
| `kw_score_google.py` | `python -X utf8 scripts/kw_score_google.py` **三路证据打分（第五十四轮加）**：补全广度（sources）+ 位次深度 + **Trends 指数**。★ 过滤 Trends 条目**必须用「强领域词白名单」而非只看词元交集** —— 纯词元过滤会**误杀** `esim japan` 的 top 里的 `saily`（真实词），也会漏掉 `embody`/`shoplc` 这类 Breakout 噪音 | 只读 |
| `kw_classify_google.py` | `python -X utf8 scripts/kw_classify_google.py` 分类 + 归属页型 + 站内对账。**动态 `importlib` 载入 `kw_classify.py` 复用其 `classify()`/`route()`** —— 分类规则是项目资产，只能有一份 | 只读 |
| `kw_report_google.py` | `python -X utf8 scripts/kw_report_google.py` 生成报告。**所有统计数字现算**，不写死任何值；阈值也用**分位数现算**（实测全站中位 35.1 / 前 10% = 46.4 / ≥60 只有 0.8%）—— 写死 60 会得出「城市词 965 个里 0 个高需求」这种误导结论 | 只读 |
| `kw_engine_compare.py` | `python -X utf8 scripts/kw_engine_compare.py` **Google vs Bing 补全对照（第五十四轮加）**：6 个互不相关种子 × 2 引擎，算两两 Jaccard + 「被 ≥3 个种子共同带出的词」。结果**两引擎都是 0.000** —— 用来**推翻**「Bing 注入通用热门块」这个错误论断。⚠️ 异常与空**必须分开计**（Google 限速是**抛异常**，吞成空集会误读成「该词没补全」，本轮踩过一次） | 只读 |
| `_verify_round52.py` | `python -X utf8 scripts/_verify_round52.py` **第五十二轮四项改动的产物断言**：① `japan/roamic` quirks 条目数 + `localnotes` 锚点；② 全站 vs 页比例条数 = 45 且 `starts cheaper in` 残留 = 0；③ 抽样页页内重复句 = 0；④ hub 页 `Cheapest in` 残留（应为 1，**且只能是表头**）。**幂等**（i18n key 已存在则跳过），可反复跑 | 只读 |
| `audit_meta.py` | `python -X utf8 scripts/audit_meta.py [--limit N]` 扫 public/ 渲染产物（2026-10-02 规范 v3）：标题 48-54 内页禁品牌（首页唯一豁免）/ 描述 120-140 必含品牌 / 重复 / 分页型统计（改 meta 后必跑） | 只读 |
| `regen_meta_fixes.py` | 2026-10-01 批次E 一次性修复脚本（已被批次F regen_meta_brand.py 取代，勿重跑） | ⚠ 一次性 |
| `regen_meta_brand.py` | 2026-10-02 批次F meta 品牌规范脚本（幂等可重跑，--dry-run 先行）：50 国 desc 品牌版 / 28 VS 标题+desc（3 家族轮换）/ 29 手写页 map | 可重跑 |
| `check_hardcoded.py` | `python -X utf8 scripts/check_hardcoded.py` 硬编码总量守卫：扫 content/en + layouts + hugo.toml，命中"50 countries / 8 providers / 28 matchups"等写死总量即失败（国家页 seo.description 豁免——脚本再生的）。**新增国家/品牌或改模板后必跑** | 只读 |
| `check_headings.py` | `python -X utf8 scripts/check_headings.py` 渲染产物 h2/h3 标点守卫（`,` `;` `:` `—` `–` 全站 0 豁免；改模板/加内容后跑，需先 build） | 只读 |
| `check_css_sync.py` | `python -X utf8 scripts/check_css_sync.py` **CSS 同步守卫（2026-10-03 加）**：扫 `layouts/`+`content/` 所有 `class="…"`，与 `static/css/tailwind.css` 逐类比对，缺任一即 exit 1。Tailwind JIT 对未知类静默忽略，没这道守卫时「改了模板忘重建 CSS」会静默上线（症状：HTML 结构正确、样式全无）。已挂进 `npm run validate` | 只读 |
| `check_output.py` | `python -X utf8 scripts/check_output.py` **产物守卫（2026-10-03 加，须在 `hugo` 之后跑）**：① 全站扫 Go 格式串泄漏 `%!x(…)`（`math.Round` 返回 float64 喂 `%d`、printf 里字面 `%` 没写 `%%`、有 `%s` 不给参数/没占位符多给参数 —— 三种都会把乱码印在正文里而 `hugo` 不报错）；② 每个 JSON-LD 块必须 `json.loads` 可解析；③ `reviewRating`/`aggregateRating`/独立 `Rating` 的 `ratingValue` 必须是 JSON 数字且落在 `[worstRating‖1, bestRating‖5]`（含"量表写成字符串"这一失败模式）；④ **~~全站扫非拉丁文字~~（2026-10-03 移除）** —— 站点要上多语言，禁令会拦住 ja/ko/zh 的合法产物，按语言划豁免前缀只是把同一个问题往后推。**移除后 ① 的格式串扫描范围扩大到 `.json`**（原先 json 分支只服务于 ④，不扩范围就成了死代码）。数据入口的清洗仍归 `scripts/scrape/toml_write.py::clean_plan_name()`（详见红线 21、§18.4）。已挂进 `npm run check:output`，并在 `npm run build` 末尾 | 只读 |
| `verify_provider_pages.py` | `python -X utf8 scripts/verify_provider_pages.py [--sample N]` **品牌×国家子页守卫（须在 `hugo` 之后跑，已挂进 `npm run check:output`）**：当前 499 个子页逐页 **13 项** —— 标题 48-54 / description 120-140 / 恰好 1 个 h1 / 逐套餐 Offer 数 = 价格表行数 / FAQPage 完整 / BreadcrumbList 4 级 / `WebPage.dateModified` / **计划数三处对账**（H2 = 表行数 = Offer 数 = 说明行）/ **天数按钮无假档位** / `data-gb` 与数据列标注一致（0=无限、<1GB 存小数；任何 `int .gb` 都会把 500MB 印成 Unlimited）。**页数与品牌集一律从 `data/` 推导、绝不写死**（写死 "400" 曾让新增品牌页漏扫而不报错）。第 13 项为**双分支**：`套餐 ≤3 且无按钮组` 计入 `chips_na` 并在报告里显式打印，`>3 且无按钮组` 才 FAIL（2026-10-07 改，见 §14 红线 52） | 只读 |
| `check_dates.py` | `python -X utf8 scripts/check_dates.py` **产物域名 + 日期守卫**：① `public/` 全站不得含 `localhost`（手敲 `hugo server` 会把 dev 地址写进 canonical / sitemap，**已发生两次**）；② 通用组页面对页级日期、价格组对价格日期、`/guides/*` 与 `/research/*` 放宽为 `lastmod == dateModified`；③ sitemap 里每个 URL 都必须有产物。**是 localhost 污染的最后一道网**（2026-10-07 那次 664 文件的污染就是它精准报出来的） | 只读 |
| `verify_no_regression.py` | `python -X utf8 scripts/verify_no_regression.py` **零回归边界守卫**：A 改造标记隔离（`#reality` / `#trip-calc` / `#fit` 等只许出现在该出现的页型，且品牌子页必须**确实**渲染它们）；B 全站不变量（恰好 1 个 h1 / 无 `{{` `}}` `<no value>` `%!x(...)` / 无空 h2h3 / JSON-LD 与注入 JSON 均可解析）；C `gb` 哨兵跨页型一致性（品牌子页 + 国家 Hub）。`--write-manifest` 重建基线 → `docs/regression-manifest.json`（**必须提交**）；`--diff <基线>` 列出**具体哪几个文件**变了并按页型标注「预期 / ★需确认」；`--strict-diff` 让非子页变更直接失败；`--selftest` **14 项**。**验证零回归的正确姿势**：`npm run build` 后先 `--diff` 看变更是否落在预期白名单，确认无误再 `--write-manifest` 覆盖基线 | 只读（`--write-manifest` 写基线） |
| `check_i18n.py` | `python -X utf8 scripts/check_i18n.py` 模板层 i18n 守卫：禁新增硬编码文案 + `en`/`de` key 逐一对齐 + **模板引用的 key 必须已定义**（漏一个就整段文案变空串、`<h2></h2>` 空着上线，而 hugo 全程 exit 0）。已挂进 `npm run validate`；旧的 `check_hardcoded.py` 已并入本脚本 | 只读 |
| `check_printf_arity.py` | `python -X utf8 scripts/check_printf_arity.py` **i18n 调用契约守卫（2026-10-10 第七十八轮加，已挂进 `npm run validate`，构建前秒级）**。**为什么前移**：本轮在 matchups 的 FAQ 里写了 `printf (i18n "…") $total`，而该 i18n 值里一个 `%` 都没有 ⇒ Go 把多余实参印成 `%!(EXTRA int=45)` **到读者页面上**（4 页，含 JSON-LD）；末端 `check_output.py` 判据① 抓得到，但代价是一次 11 分钟全量构建。**根因是跨文件契约**：格式串在 `i18n/*.toml` 的值里、实参个数在 `layouts/**` 里，`check_i18n.py` 只扫 `printf "字面量"` 里的英文文案。**四道判据**：① `printf (i18n "K") A1…An` 的动词数必须 = n；② 值里有非格式动词的裸 `%`（`20% off` 当格式串用）报错；③ `i18n "K" (dict …)` 必须覆盖**该 key 各语言占位符的并集**（否则印 `<no value>`）；④ 各语言占位符集合**互不相同不报**（德语要 `country_acc`/`country_dat` 的格变化，是刻意设计）。**分级**：会让读者看见的 ⇒ ERR；任何语言都没用到的 dict 键 ⇒ WARN（Go 静默忽略）。`--selftest` **21 项**（正例 10 / 硬反例 9 / 软反例 2）。**校准教训见 §14 红线 94**（第一版在 `provider.html` 误报 160 处） | 只读 |
| `check_headings_source.py` | `python -X utf8 scripts/check_headings_source.py` **h2/h3 标点守卫的构建前版（2026-10-10 第七十八轮加，已挂进 `npm run validate`）**。**为什么前移**：本轮新加的一条**德语 H2 带逗号**，跑满一次构建才在末端 `check_headings.py` 报 `bad: 45`（45 个页面全部返工一次构建）。判据从 `scripts/lang_rules.py` 读**同一份**语言规则（**不抄第二份正则**）：en 禁 `, ; : — –`、de 等语言禁 `, ; :`。**三个来源**：`<h2>/<h3>` 块内的 i18n key（含 `printf (i18n …)` 形态）、`$xH2 = i18n "…"` 的**间接赋值形态**（第六十五轮实漏过一处，只能靠变量命名习惯兜）、`content/{lang}/**/*.md` 的 Markdown 标题。**边界（写进 docstring）**：值里 `{{ .x }}` 代入后才出现的标点、以及数据层国名/品牌名带进来的标点，本脚本**看不见** ⇒ **产物级 `check_headings.py` 必须保留**。`--selftest` 5 项（含 H1 不参与、模板侧识别） | 只读 |
| `check_article_agreement.py` | `python -X utf8 scripts/check_article_agreement.py` **冠词一致性守卫（2026-10-08 第五十六轮加，已挂进 `check:output`）**：同一个坑踩了两次（第二十四轮 `whether a {{ .brand }} plan` → "a Airalo"；第五十六轮 `Does a {{ .brand }} eSIM work` → "a Airalo"），所以改成机器拦。**两道**：① **产物级** —— 扫 `public/**/*.html`，剥 script/style/标签后匹配 `\b(a\|an)\s+([A-Za-z…])`，命中品牌名/国名比对期望冠词。`BRANDS_AN={airalo,alosim}`、`COUNTRIES_AN={argentina,australia,austria,egypt,ethiopia,iceland,india,indonesia,ireland,israel,italy}`；⚠ **`PRONOUNCED_CONSONANT={ubigi,united*,uae,ukraine,uganda,uruguay}`** —— 字母是元音但**发音是辅音 /j/**，必须配 "a"（用「首字母是元音」做判据会在这里误报）。② **源码级** —— 禁止「冠词紧邻专有名词占位符」（`a %s eSIM` / `a {{ .brand }}` / `a {country}` / i18n 里的 `a {{ .brand }}`）。**为什么要有第二道**：产物级只看得到**当前真的渲染出来**的组合 —— 实测品牌 Hub 里 7 个 printf 问句都写成 `a %s eSIM`，只有 3 个在当前品牌分层下渲染，另外 4 个 + networks 页那句**全绿通过**，等元音开头的品牌进来才暴雷。禁令窄化到专有名词占位符，放过 `a {{ .days }}-day trip` 这类数值（否则满屏误报）。`--selftest` **18 项**（产物级 7 + 源码级 11），双向验证：既证明会抓住，也证明放过合法写法。**实测战绩**：首跑抓出 **47 处**存量（20 个元音开头国名 × en/de），修完当轮又抓出作者**新写的 2 处** —— 守卫在同一个回合里拦住了写它的人 | 只读 |
| `append_carrier_info.py` | 追加 [ISO.info]（幂等，**已执行过，勿再跑**——再跑也只是提示跳过） | 幂等 |
| `backfill_networks_uniform.py` | `python -X utf8 scripts/backfill_networks_uniform.py` 一键把**所有**品牌的每国 `networks` 填成该国运营商（同国同运营商，幂等）。⚠ **它是全局脚本，不是「只补新品牌」** —— 跑一次会把历史品牌遗留的空数组一并补上（2026-10-07 接 Jetpac 时顺手把 nomad 的 `networks = []` 补真，**影响 123 页**：国家页/对决页 59 + 德语 51 + `/networks/*` 13，品牌子页 0）。做变更面归因时要把它和新品牌接入**分开记账**。新增品牌转完 TOML 后必跑 | 安全 |
| `gen_sample_data.py` | ☠☠☠ **永远禁止整跑** —— 会用 SAMPLE 数据覆盖全部真实抓取结果 | 禁令 |
| `scrape/verify_airalo.py` `probe_*.py` `discover_slugs.py` | 一次性验证/探测工具（airalo 官网对照校验已通过：JP/IT/US 全档一致） | 存档 |

---

## 6. 常用命令速查

```bash
cd "D:/esimsift/esimsift"

npm run build                      # 完整管线：Tailwind CSS → validate(+CSS 同步守卫) → hugo → check:output（上线前必跑）
npm run dev                        # Tailwind 预编译 + hugo server（本机 :1313）
npm run build:css                  # 只重建 Tailwind —— 改过 layouts 里的 class 后必须跑
npm run validate                   # validate.py + check_css_sync.py + check_i18n.py
                                   #   + check_printf_arity.py + check_headings_source.py（后两道 2026-10-10 第七十八轮加，均秒级、构建前拦）
npm run check:output               # 产物守卫（格式串 / JSON-LD / 评分区间 / h2-h3 标点 / 品牌子页 / FAQ 数字 / 日期 / 零回归）—— 须在 hugo 之后跑

# 数据刷新三连（改完 plans 后必做后两步）：
python -X utf8 scripts/gen_provider_pages.py   # ① 子页描述嵌着数字，必须重生成
python -X utf8 scripts/validate.py             # ②
npm run build                                   # ③
```

⚠️ **不要用裸 `hugo` 代替 `npm run build`。** `hugo` 只把 `static/css/tailwind.css` 拷进 `public/`，
不会重编译 Tailwind；改了模板 class 而不重建 CSS，新类没有规则、样式静默失效（2026-10-03 已踩）。

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

## 7. 操作手册 A：新增一个品牌（完整 10 步，每步带检查点）

以新增第 10 家品牌 `xyz` 为例（现 9 家）。**做完一步，先过"✅ 检查点"确认没错，再走下一步**——前一步错了后面全白搭。

> **★ 2026-10-06 Nomad 试点教训：这 10 步之外，还有 5 处会连带受影响，别漏**
>
> | # | 连带项 | 为什么 | 怎么处理 |
> |---|---|---|---|
> | 1 | `scripts/verify_no_regression.py` 的分类基础 | 旧版把 `BRANDS` **写死 8 个**，新品牌子页掉进 `static` 兜底 → 401 条假失败。**页型判据依赖的数据集变了，判据必须跟着变** | 已改为从 `providers.toml` 推导；**以后任何"按品牌分类/枚举"的守卫都照此办理** |
> | 2 | 国家页 / 对决页的 title + description | 描述里的「N providers」「from $x」全是实时数字 | `regen_meta_brand.py --dry-run` 确认后真跑 |
> | 3 | 国家页 title 的价格锚（`data/titlesegments.toml`） | 「From $x/GB」「有无无限档」由全市场数据算，新竞争者可能易主 | `_solve_titles.py --write` 重算（Nomad 让 6/50 条变化），再 `--dry-run` 比对 |
> | 4 | `data/faqs/*.toml` 的事实断言 | 「最便宜是 X、$Y」「All N unlimited plans」会被新品牌改写 | **已不用手动管**：这三条已改成 `{token}`，值由 `partials/faq-live-tokens.html` 构建期现算（2026-10-07）。接完品牌直接 build，`scripts/check_faq_facts.py` 会自动对账；**要改的只有新品牌把某国最优解抢走后的文案口吻**（可选，见 §7.1 遗留） |
> | 5 | 三份文档 | 品牌集/页数/套餐数散落在多处 | `PROJECT.md`（本文件 §0/§2/§4.7/§5）+ `STATUS.md` 本轮节 + `docs/keyword-map.md` 新品牌词归属 |
>
> **新增品牌的"页面总数变化公式"**：`+N 子页（N = 该品牌覆盖国数）+ 1 品牌 hub + (M-1) 对决页`（M = 接入后品牌总数）。Nomad = +50 + 1 + 8 = **+59 页**（复核：584 → **643 页**）。

1. **抓数据**（三选一，产物都是 `scripts/scrape/raw/xyz/*.json`，一国一文件）：
   - esimdb 有专页 → `python -X utf8 -u scripts/scrape/scrape_esimdb.py xyz`
   - 不在 esimdb（像 holafly）→ 参照 `scrape_holafly.py` 写官网 PDP 抓取器（注意 Yoast sitemap 通常不含 PDP，slug 用候选探测）
   - 自家/内部数据 → 参照 `extract_roami.py`
   - **✅ 检查点**：`scripts/scrape/raw/xyz/` 下 json 数量 = 该品牌实际覆盖的国家数；`Read` 一个 json 看里面是真套餐（name/gb/days/price 都有值），不是空数组或反爬错误页。

2. **转 TOML + 填 networks**：
   - `python -X utf8 scripts/scrape/toml_write.py xyz --dry-run --checked YYYY-MM-DD` 确认 `0 problems` → 去掉 `--dry-run` 真写 → `python -X utf8 scripts/backfill_networks_uniform.py`
   - `--checked` **传不传都能自愈，但首次建台账前仍要传对**（2026-10-07 起）：`npm run build` 第一步的 `stamp_checked.py` 按内容指纹把日期盖成「数据实际变化的当天」，所以重抓整批老国家时**忘了传也会被纠正**（旧常量 2026-09-30 不会漏到页面上）。**唯一例外是首次建台账**（`docs/checked-state.json` 不存在）—— 那时它只登记现值、不改日期，所以**新品牌务必传 `--checked $(date +%F)`**，否则整批数据会顶着旧日期直到第一次改动。
   - **✅ 检查点**：
     - dry-run 结尾是 `0 problems`（有 problems 就先把列出的坏数据修掉再真写）；
     - 真写后 `data/plans/xyz.toml` 存在，且 `grep -n "price = [0-9]*$" data/plans/xyz.toml` 命中 **0 行**（= 没有整数价，全是两位小数 float）；
     - backfill 输出 `xyz filled NN/50`，NN = 该国覆盖数；再 `grep -c "networks = \[\]" data/plans/xyz.toml` 得 **0**（= 全部填上了运营商）。

3. **`data/providers.toml`** 加 `[xyz]` 块（字段见 §4.2；founded/公司事实要核实来源，别编）。
   - **✅ 检查点**：`grep -n "\[xyz\]" data/providers.toml` 有且仅一处；`python -X utf8 scripts/validate.py` 不再报"未知品牌键"。

4. **`hugo.toml`** 加 `[params.outbound.targets.xyz]`（base/label/rel="sponsored nofollow"/utm）。
   - **✅ 检查点**：`grep -n "targets.xyz" hugo.toml` 命中；build 后随便开一个国家页，xyz 行的出站按钮文字 = 你配的 `label`。

5. **品牌页**：新建 `content/en/esim-providers/xyz.md`，只写 front matter（title/description），正文由模板聚合。
   - **✅ 检查点**：build 后 `/esim-providers/xyz/` 能打开且出现聚合数字（"cheapest in N of M"、竞争力评分），**不是**"无数据简壳页"——若降级成简壳，说明 plans 没被读到，回头查第 2 步。

6. **对决页**：与每个现有品牌组合，新建 `content/en/compare/{a}-vs-{b}.md`（文件名**严格字母序**）×9 个（**枢纽页 /compare/matchups/ 的卡片按 providers.toml 枚举，新品牌自动出现，无需改它**）。**优先用 `python -X utf8 scripts/gen_vs_pages.py`** —— 它只补缺失的对，已有页一个字不动：
   ```markdown
   ---
   title: "Xyz vs Airalo eSIM Compared: Prices & Verdict 2026"   # 自拟，别和现有 36 个撞框架
   description: "Which eSIM is cheaper, Xyz or Airalo? Computed comparison of entry prices, $/GB and fair-use caps."
   providers: ["airalo", "xyz"]    # 字母序！validate 会查
   layout: vs-single
   ---
   ```
   - **✅ 检查点**：`content/en/compare/` 下新增 9 个含 `xyz` 的文件，且每个文件名里两品牌是字母序（如 `airalo-vs-xyz`、`xyz-vs-yesim`，绝不能 `xyz-vs-airalo`）；validate 不报字母序错误；**已有 36 页的 mtime 不变**（`gen_vs_pages.py` 会打印 `existing NN untouched / created MM`）。

7. **`python -X utf8 scripts/gen_provider_pages.py`** —— 生成 xyz × N 国子页（同时会清掉不在 providers.toml 里的品牌的旧子页）。
   - **✅ 检查点**：脚本结尾 `OK: N provider×country sub-pages written`，N 比加品牌前多了约 50（= xyz 覆盖的国家数）；`content/en/compare/<slug>/xyz.md` 已经出现在各国家目录下。

8. **`python -X utf8 scripts/validate.py && npm run build`** —— 0 error 才算完。
   - **✅ 检查点**：validate 结尾 `0 error(s), 0 warning(s)`；build 正常结束（Hugo 打印 Pages/Total 汇总、无 `Error:` 行）；页面总数比加之前涨约 **60 页**（50 子页 + 1 品牌页 + 9 对决页；子页数按 xyz 实际覆盖国微调）。**涨页数不是全部** —— 全站每一页都会变（`footer.html` 的 `range $d.providers` 有一份全品牌清单），基线 diff 应显示「全站变更 + 新增 N 页」，属预期。

9. **渲染抽查**：`/esim-providers/xyz/`、`/compare/#matchups`（出现新对决卡）、`/compare/japan/xyz/`（子页）、国家页表格出现新品牌 chip、sitemap/llms.txt 自动纳入。
   - **✅ 检查点**：这 5 个 URL 逐一打开、数字都出来了；兜底跑 `grep -rc "%!f" public/ --include="*.html" | grep -v ":0"` 应无输出（= 没有渲染成 nil 的价格）。

10. **可选收尾**：footer "Popular matchups" 列是手挑 6 组（`layouts/partials/footer.html`，缺页会静默跳过所以不必须改）；真 logo 放 `static/img/providers/xyz.png`。
    - **✅ 检查点**：放好 logo 后重新 build，品牌页/卡片从单色字母徽标（monogram）自动切成真 logo。

### 7.1 FAQ 数字断言：已改为**构建期现算**（2026-10-07 第四十一轮，已修）

**问题（存量债）**：`data/faqs/*.toml` 里三条答案把数字写死了 ——
「最便宜是 X、$Y」「All N 'unlimited' plans」「Holafly 最低 $Y/天」。
真值在 `data/plans/*.toml` 里，每次抓价或接入新品牌都会变，于是**页面自相矛盾**：
US 的 FAQ 说「Roami $2.99 最便宜」，而正上方价格表里最低的是 Yesim $0.51。
首次审计（已删除的一次性脚本 `audit_faq_facts.py`）报 **99 条过期**，其中 45 国「最便宜品牌」易主；
且它按 `q.startswith("What is the cheapest")` 匹配，**jp 的自定义问法被整条跳过**（jp 的 $1.99/7 天实际是 3 天）。
排除 nomad 复跑仍是 99 条 → **改动前就过期**，不是某一轮引入的。

**修法（不是重算一遍数字，而是让数字不可能过期）**：
1. 三条答案改写成**只留 `{token}` 占位**的文案（当时用一次性脚本 `scripts/migrate_faq_frames.py`，151 处 / 50 国；
   该脚本已在第四十二轮删除，其 token 化规则并入 `scripts/faq_frames.py` 的历史规则 —— 见下「第二轮」）。
   jp 保留其独有分析口吻，同样 token 化；jp 的 Q5 品牌枚举换成 `{brands_list}`（nomad 接入后它少列了一家）。
2. 值由 `layouts/partials/faq-live-tokens.html` 在**构建期从 `data/plans` 现算**，30 个 token。
3. `layouts/compare/single.html` 组装 `$faqs` 时做一次 `{token}` → 值替换；
   可见正文与 FAQPage JSON-LD 都读同一份 `$faqs`，**structured data 与用户所见天然同源**。
4. 新守卫 `scripts/check_faq_facts.py`（已挂进 `check:output`）**读产物、独立重算对账**（见 §5.2）。

**口径**（与页面其它模块逐字一致，别另立第二套）：
最便宜 = 价格最低 → 同价取流量更大 → 再同取品牌 key 升序；最佳 $/GB 只算**计量档**（无限档 perGB 是 999999 哨兵）；
无限最优按 `$/天`；FUP 取 `providers.toml [<brand>.policy]` 而**不是** plan 的 `fup_note`
（roami/yesim 的 fup_note 全缺、holafly 那条写的是 "Always On" 附加包说明，不可用）。

**收益**：接品牌 / 刷价之后**不需要再动 FAQ**；页面的 FAQ 与价格表不可能再打架；每国文案的每个数字位都随数据变化（反同质化）。

**第二轮（第四十二轮）：句架也不再重复**
第一轮之后，49 国（jp 除外）的三条答案仍是**同一副句架**，只有数字位不同 —— 50 页里同一句话出现 49 次，是模板级重复内容。本轮：
1. 每条答案拆成 **open（直接回答）/ body（数据事实）/ close（行动建议）** 三槽，每槽 7 片段
   （库在 `scripts/faq_frames.py`，共 21 个片段 + Q6 的 7 个变体）。
2. 分配用**拉丁方阵** `a = i % 7`、`b = i // 7`、`c = (a + b) % 7` ⇒ 任意两页最多共用一句（推导见 §4.5）。
3. 顺带修掉 **Q6 的事实缺陷**：原文「Regional Asia/continental plans from Airalo and Nomad bundle
   {country} with neighbors」对法国 / 美国 / 阿根廷是**自相矛盾**的句子（数据集里根本没有区域档，
   只有单国档），且 41 国逐字相同、对欧洲国家读起来荒谬。现改为
   `{neighbor}`（取**问题里点名的那个邻国** —— 英国的问题问「英国和法国」就答法国；
   机械取 `neighbors[0]` 会答成爱尔兰）+ `{neighbors_all}`；
   7 个没有邻国的国家（HR / IS / CR / IL / MA / ZA / KE）走按 region 生成的兜底短语，
   且这 7 国**各占一个变体** —— 否则同 region 的两国（HR / IS 都是 Europe）会渲染出逐字相同的一段。
4. 守卫加 **R10**（见 §5.2 表），把「骨架两两不同 / 最多共用一个槽 / 每条答案拆得回片段库」钉死。
   自测 5 个 R10 反例（同文 / 共用两个槽 / 兜底撞车 / 答案偏离片段库 / 正确样本不误报）。

**收益**：句架层面 50 页两两不同；Q6 从「无数据支撑的断言」变成数据驱动（点名真实邻国）。

**遗留（不是债，是可选）**：
- 后三条里 **slot4「ID 规定」有 14 国共用同一句**（AE AR CN EG ID IL IN KE MA MX PH SA TR VN ——
  都是有实名登记要求的市场，句子本身站得住）。要逐国改写必须先核实当地法规，**没有外部事实来源我不编**。
  守卫把它当 INFO 报数（`slot4: 37 种骨架 / 50 页 ← 有历史重复`），不判失败。
- **德语站的 FAQ 正文仍是英文**（`data/faqs/` 只有英文一份），而句里的国名已经是德语
  （`{country}` → "Vereinigte Staaten"）—— 既有状态，本轮未动。要修就是 50 国 × 6 条 × 翻译，
  应单开一轮，并先决定德语 FAQ 是「翻译」还是「独立的对比视角」（后者 SEO 更好但工作量翻倍）。

**删除品牌**（反向操作）：providers.toml 删块 → hugo.toml 删 target → 删品牌页 md + 相关 vs md → **删 `data/plans/xyz.toml`** → `gen_provider_pages.py`（清子页）→ 删 `raw/xyz/` → `regen_meta_brand.py` + `_solve_titles.py --write`（数字会变）→ validate + build。**✅ 检查点**：build 后 `/esim-providers/xyz/` 返回 404、`/compare/#matchups` 里 xyz 卡片消失、validate 0 error。
> ⚠ **`nomad` 曾走过这条路又回来了**（退场 → 2026-10-06 重新接入，见 §0）。所以别再把 nomad 当"删除品牌"的参考案例 —— **本节的步骤顺序就是参考**，`raw/` 与 `data/plans/*.toml` 的备份别随手真删（Nomad 能回来靠的就是 `_competitors/raw/` 里的原始 JSON 还在）。

---

## 8. 操作手册 B：给现有品牌新增一个国家的套餐

### 情况 A：国家已在 50 国内（如 airalo 新开始卖越南）—— 小操作
1. 数据二选一：
   - **重抓**（正规）：删 `scripts/scrape/raw/<brand>/<slug>.json` → `python -X utf8 -u scripts/scrape/scrape_esimdb.py <brand>`（只补缺的，其余跳过）→ 改 CHECKED → `toml_write.py <brand>`。holafly 用 `scrape_holafly.py`；roami 用 `extract_roami.py`。
   - **手补**（临时）：直接在 `data/plans/<brand>.toml` 加 `[VN]` 块（严格遵守 §4.3 字段规则，尤其 price 两位小数、type 口径）。注意下次重转会覆盖手补内容。
   - **✅ 检查点**：`data/plans/<brand>.toml` 里出现 `[VN]` 块且有 `[[VN.plans]]` 内容、`price` 全两位小数；跑一遍 `python -X utf8 scripts/backfill_networks_uniform.py` 后 `[VN].networks` = 越南运营商（Viettel/Vinaphone/MobiFone），不是空 `[]`。
2. `gen_provider_pages.py` → `validate.py` → `npm run build`。
   - **✅ 检查点**：validate 结尾 `0 error(s), 0 warning(s)`；build 无 `Error` 行。
3. 验证：国家页表格多出该品牌行、`/compare/vietnam/airalo/` 子页出现、对决页判胜数字变化（全部自动）。
   - **✅ 检查点**：打开 `/compare/vietnam/` 看到 airalo 那一行和价格数字；`/compare/vietnam/airalo/` 能打开且有内容。

### 情况 B：新增第 51 个国家 —— 大操作（动 6 个地方）
1. `data/countries.toml` 加 `[XX]` 全字段块（region 必须精确匹配五个筛选值；slug 唯一）。
   - **✅ 检查点**：`grep -n "\[XX\]" data/countries.toml` 有且仅一处；`region` 一字不差等于五个枚举之一（Asia / Europe / Americas / Africa & Middle East / Oceania）；`slug` 与 `content/en/compare/<slug>.md` 文件名一致。
2. `data/faqs/<xx>.toml` 新建（6 条对比角度 FAQ）。
   - **✅ 检查点**：文件名小写 `xx.toml`；内容是顶层 `[[faq]]` 数组；build 后国家页 FAQ 区出现 6 条，页面 HTML 里能搜到 `"FAQPage"`。
3. `content/en/compare/<slug>.md` 新建（front matter `iso = "XX"` + seo.description 占位 + 3 段分析；参考 japan.md 样板）。
   - **✅ 检查点**：front matter 有 `iso: "XX"`；build 后 `/compare/<slug>/` 能打开，TL;DR 三卡 + 全套餐对比表都渲染出来。
4. 图片：`static/img/countries/<slug>-01..04.webp` ×4 + `static/img/flags/<xx>.svg`（路径与 countries.toml 对齐）。
   - **✅ 检查点**：4 张 webp + 1 张 svg 确实存在，文件名 = `countries.toml` 里 `flag`/`images` 写死的那几个路径（对不上就是坏链）。
5. `data/carriers.toml` 加 `[XX]` + `[[XX.profiles]]`（+ 可选 `[XX.info]`）。
   - **✅ 检查点**：profiles 里每个 `name` 都和 `countries.toml [XX].carriers` 逐字一致（validate 会查 join key，不一致就报错）；build 后国家页运营商区渲染出速度档位 + 城市。
6. 每品牌补 `[XX]` 套餐（抓取或手补，同情况 A）。
   - **✅ 检查点**：9 个 `data/plans/*.toml` 里都有 `[XX]` 块；跑一遍 `python -X utf8 scripts/backfill_networks_uniform.py` 把 9 家的 `[XX].networks` 都填成该国运营商。
7. `gen_provider_pages.py` → `validate.py` → **`regen_meta_brand.py --dry-run` 确认后真跑**（新国家的 seo.description 由它按实时数据重写，含品牌词与字符数校验）→ `npm run build` → `audit_meta.py` + `check_hardcoded.py` 双守卫。
   - **✅ 检查点**：validate 结尾 `0 error(s), 0 warning(s)`；regen_meta_brand dry-run 无意外改动；build 无 `Error`；`audit_meta.py` 标题 48-54 / 描述 120-140 合规、`check_hardcoded.py` 无写死总量（两个守卫脚本都 0 命中）。
8. 自动纳入：首页区域网格、header 大菜单、sitemap、catalog.json、llms.txt、guides/research 页数据盒、对决页判胜表、matchups 枢纽 —— 全部无需手工。
   - **✅ 检查点**：首页区域网格出现新国旗卡；`public/sitemap.xml` 里多出该国的 URL；`/compare/<slug>/` 可访问。

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
#    或逐次显式传 --checked YYYY-MM-DD（推荐，不动常量）

# ② 重抓（esimdb 七家，--force 全量；约几十分钟，挂后台）
python -X utf8 -u scripts/scrape/scrape_esimdb.py airalo saily yesim ubigi roamic alosim --force
python -X utf8 -u scripts/scrape/scrape_holafly.py --force
python -X utf8 scripts/scrape/extract_roami.py      # roami 从本机 Roami 项目提
#    nomad 的原始 JSON 在 _competitors/*/raw/nomad/，拷进 scripts/scrape/raw/nomad/ 后同样走 toml_write

# ③ 逐家转换（每家确认 0 problems）
for b in airalo saily yesim ubigi roamic alosim holafly roami nomad; do python -X utf8 scripts/scrape/toml_write.py $b --checked $(date +%F); done

# ④⑤⑥ 三连（日期不用管：npm run build 的第一步会自动盖章）
python -X utf8 scripts/gen_provider_pages.py
python -X utf8 scripts/validate.py
npm run build     # 内含 npm run stamp → 数据变过的品牌，日期自动推到「今天」
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
| VS 对决页 + 对决枢纽页 /compare/matchups/ | ✅ 36/36 + 枢纽索引页（closest/lopsided 计算瓦片） |
| research 数据研究页 | ✅ 3 页（price-index / unlimited / fair-use） |
| guides 指南页 | ✅ 5 篇 + 枢纽 |
| 区域枢纽页 ×5（/compare/asia/ 等） | ⬜ Phase 2 |
| /networks/{carrier}/ 运营商页 | ⬜ Phase 2（数据已就绪：networks 2026-10-02 已补真） |
| /networks/{country}/ 单国运营商深度页 ×50 | 🟡 **12/50**（Japan + US/DE/CA/FR/MX/TH/ES/KR/CN/GB/NL，2026-10-03；模板 `layouts/networks/single.html` 纯数据驱动 + H2 覆盖钩子，余 38 国只需加 content md + FAQ + `networkreports.awards`） |
| /devices/{device}/ 设备兼容页 | ⬜ Phase 2（数据源 devices.toml 已备） |
| tools 第 2/3 个工具 | ⬜ Phase 2（已有行程计算器） |
| sitemap 分片（>1000 URL） | ⬜ 现在 585，暂不需要 |
| 国家页 authority 外链 | ✅ 2026-10-01：50 国 Opensignal/Ookla/Global Index 引用区（networkreports.toml） |
| 城市页 / 假评分 / 词数 KPI | ❌ 蓝图明确不做 |

唯一未落的 Phase 1 项：validate.py 锚文本分布静态检查（归 P-B，理由：真实内容产出后统计才有意义）。

---

## 14. 红线与坑（每条都真踩过）

1. **☠ `gen_sample_data.py` 永远禁止整跑** —— 会用 SAMPLE 覆盖 8218 条真实数据。`gen_provider_pages.py` 才是日常用的生成器（它绝不碰 plans）。
2. **price 必须两位小数 float**（`price = 13.50` 不是 `13`）—— int64 会让 Hugo `printf "%.2f"` 渲染成 `$%!f(int64=13)`（airalo 品牌页真实事故）。生成器已修，**手补数据时是唯一风险点**。修完可用 `grep -rc "%!f" public/` 验证。
3. **禁止 PowerShell Get-Content/Set-Content 批量改文件** —— PS 5.1 GBK 乱码会吃掉 `<` 标签。只用 Edit/Write 工具或 `python -X utf8` 脚本。bash heredoc 里含撇号（'）会挂 —— 脚本一律 Write 工具写文件再执行。
4. **hugo 不清理 public/ 旧页** —— 删页后 `rm -rf public` 再构建，或部署用 `--cleanDestinationDir`（曾经 /vs/ 旧页残留）。
5. **JSON-LD 必须 `| safeJS`**，且 md 正文禁止内联 JSON-LD（--minify 教训）—— 结构化数据全在模板层 `partials/schema.html`。
6. **`site.Data` 已弃用** → 一律 `hugo.Data`（`site.Params`/`site.GetPage` 不受影响）。
7. `[[faq]]` 顶层数组取值要 `.faq`。
8. 国家列表过滤是三层的：`where (where (where .Pages "Params.provider" nil) "Params.providers" nil) "Params.nolist" nil`（排除品牌子页、对决页、nolist 特殊页如 matchups 枢纽）—— 新模板列国家时照抄，别只抄两层。
9. esimdb 有 AWS WAF：curl 全被拦，必须 Playwright 本机 chromium；airalo.com 官网对高频访问限速（verify 脚本要慢跑）。
10. 并行 agent 最多 3 个（API 429）；被内存压力杀掉的后台任务**不自动重启**，等指令再续。
11. **改过 `layouts/` 里的 class 必须重建 CSS**（2026-10-03 版式塌陷事故）—— `static/css/tailwind.css` 是 Tailwind CLI 的独立产物，裸 `hugo` 不会更新它；Tailwind JIT 对未知类**静默忽略、构建不报错**，后果是「HTML 结构对、样式全无」。真实症状：`/networks/japan/` 右侧吸顶内链栏掉到页面底部，因为 `lg:grid-cols-[minmax(0,720px)_300px]` 从未被编译。**对策**：一律 `npm run build`（`build:css` 已前置），并用 `scripts/check_css_sync.py` 兜底；验证时别只看源码，要 `curl -s http://127.0.0.1:1313/css/tailwind.css | grep <类名>` 确认浏览器真拿到了规则。
12. TOML 表数组（如 `[[XX.info.detail]]`）追加在文件末尾合法；validate.py 目前只校验 profiles 的 join key，追加 detail 后跑一遍确认。
13. **标题硬规则（用户定，2026-10-01）**：全站 `<h2>/<h3>` 必须一句话、用户视角，**禁止逗号/冒号/破折号碎片**（"X, honestly" / "A: B" / "W — and L" 全是反例；FAQ H2 一律用户问句如 "What should I know before buying a {C} eSIM"）。**2026-10-03 第十轮起 FAQ 问题本身也是 `<h3>`（见红线 29），所以问句文本同样受这条约束** —— 问句不能靠逗号挂从句（`Which Japan network is fastest, Docomo or SoftBank?` → `Is Docomo or SoftBank the faster Japan network?`）。改模板后跑渲染扫描验证：`python -X utf8 scripts/check_headings.py` 遍历 public/*.html 提取 h2/h3 文本查 `,:—–;`（唯一豁免：/research/ 枢纽卡的文章主标题 "Title: Subtitle" 惯例）。
14. **`data/*.toml` 文件名禁止连字符** —— `network-reports.toml` 的数据键是带 `-` 的 `"network-reports"`，点号 `hugo.Data.networkReports` 取不到，模板静默渲染空卡且**构建不报错**（真实事故：45 国引用卡全部空白才发现）。已改名 `networkreports.toml`；新数据文件一律无连字符命名。
15. Go html/template 会把 href 里的 `(` `)` 编码成 `%28%29`（`| safeURL` 也拦不住；HK/Macao 的 Global Index 链接即如此）—— HTTP 等价，接受即可，别再花时间"修"。
16. `{{ with .field }}` 内 dot 被替换成字段值，再链 `.key` 会报 `can't evaluate field key in type string` —— 需要外层键时用 `range $b := $xs` 显式循环变量。
17. **`content/` 下 `_` 前缀目录不会被 Hugo 隐藏**（`_` 只对 static/data/partials 生效）——放进去的备份会渲染成正式页面（真实事故：guides 备份多渲染 6 个重复内容页）。**备份一律放项目根**（如 `_guides_backup_20261002/`）。
18. **改聚合 dict 键名要全链路改**：list.html 曾把条目键 `minPerGB` 改成 `v` 但下游没跟上 → `$%!f(<nil>)` 静默渲染且**构建 0 报错**。改完 grep `"%!f" public/` 验一遍（与红线 2 同源）。
19. **Go 格式串错误的通用三类（2026-10-03 事故，全站 17 个文件中招）** —— 症状都是**乱码直接印在正文里**（还可能进 JSON-LD FAQ），而 `hugo` 全程 exit 0：
    - `math.Round` 返回 **float64**，喂 `%d` 前必须 `int` 强转 → 否则 `(%!d(float64=84)% of its coverage)`
    - printf 格式串里的**字面百分号要写 `%%`** → 否则 `20% margin` 变成 `20%!m(MISSING)argin`
    - **有 `%s` 就得给够参数、没占位符就别多传参数** → 否则句尾多出 `%!(EXTRA string=Airalo, string=Holafly)`
    通用验证：`grep -rho '%![A-Za-z]*(\([^)]*\))' public/ --include=*.html | sort | uniq -c`，或直接跑 `scripts/check_output.py`。
20. **`itemReviewed` 为 Organization/LocalBusiness 时，评分必须来自真实用户（2026-10-03 GSC 事故）** —— 品牌页曾用编辑部算的「价格竞争力指数」（cheapest 命中国数÷覆盖国数×10）当 `reviewRating`，导致 GSC 报「评分超出了指定范围或默认范围（在 reviewRating 中）」、内容无效。**双因**：① `bestRating` 写成字符串 `"10"` 且漏 `worstRating` → Google 退回默认 1–5；② 8 个品牌里 7 个分值 < 1，本身就落在区间外。**更根本**：Google 明文规定这类评分「評分必須直接來自用戶，請勿依賴人工編輯編制評分資訊」，编辑计算分**永远拿不到星级**且踩质量指南。**对策**：指数改用 `additionalProperty`（`PropertyValue`）如实携带，页面可见读数不变；`offers.lowPrice/highPrice/offerCount` 必须是 **JSON 数字**。想拿星级只有一条正路 —— 上真实站内用户评分体系。
21. **抓来的套餐名可能夹带本地语言，必须英文罗马化（2026-10-03 事故）** —— Airalo 韩国套餐在源头叫 `'짱 Jjang - 1 GB`（`짱` 是韩语"最棒"，外加一个 DOM 残留的前导撇号），直接落在 `/compare/south-korea/`、`/compare/south-korea/airalo/`、`catalog.json`、`/tools/` 四处，在纯英文站上是明显瑕疵。**口诀**：拉丁变音符**保留**（`Élan`/`Fáilte`/`Prosím`/`Hé Hé` 是 Airalo 真实产品名，共 6 国 100+ 条），**非拉丁一律丢**（韩文/汉字/西里尔…）。**两侧守卫（2026-10-03 晚已变更）**：产物层（`check_output.py` ④）与数据层（`validate.py` §3）的**「非拉丁禁令」已整体删除** —— 站点要上多语言，这条禁令会拦住 ja/ko/zh 的合法内容，按语言划豁免前缀只是把同一个问题往后推。**现在唯一的防线是抓取层归一化**：`scripts/scrape/toml_write.py::clean_plan_name()`（丢非拉丁脚本 + 去前导标点 + 收空格），重抓自动清洗并把改动打印出来。`validate.py` §3 保留与语言无关的结构性校验（首尾空白、首字符是标点的残留）。**代价（必须知道）**：若有人**手动**往 `data/plans/` 贴一条带韩文/汉字的套餐名，构建不会再拦 —— **新抓一批数据后请人工看一眼 `clean_plan_name` 的打印输出**。
22. **`static/` 下放任何东西都会原样发布到线上（含内部脚本与笔记）** —— 真实事故：`static/img/esim/图片_backup_20260929/` 是一次图片处理的备份目录，里面还有 `.workbuddy/` 子目录（19 个文件：11 个内部 py 脚本、4 个 process/webp 日志、3 张 png、1 个 memory md）。它被 Hugo 原封不动拷进 `public/`，**线上 `https://www.esimsift.com/img/esim/图片_backup_20260929/.workbuddy/process_log.txt` 实测 HTTP 200**（35KB），且已随 first commit 进了 git。`static/` = 发布目录，**备份/草稿/临时产物一律放项目根**（同红线 17：`_guides_backup_20261002/` 的教训，但那条是 `content/` 渲染成页，这条是 `static/` 直接可下载，更隐蔽）。新加图片资源时只放**页面真的要引用的文件**。
    - **✅ 已于 2026-10-03 清除**：整个目录移出仓库到 `D:\esimsift\_deleted_20261003_图片_backup_20260929\`（站外、非 git 仓库，19 个文件逐个大小校验一致），`static/` 与 `public/` 下的副本已同步删除。**违规只是「位置不对」，不是「内容不该留」——删前一律先做站外备份**，不要真删。
    - **准入检查（每次往 `static/` 加东西前跑一遍）**：`find static -type d -name ".workbuddy" -o -name "*backup*"` 与 `find static -type f \( -name "*.py" -o -name "*.log" -o -name "*.txt" -o -name "*.md" \)` 都应为空。`static/` 只放页面引用的图片/字体/`robots.txt`/`llms.txt` 等**真正的站点资源**。
23. **YAML front matter 里不能写 Hugo 短代码（2026-10-03 事故）** —— 11 篇 networks 页的 `kicker` 与 FAQ 答案里写了 `{{< count-providers >}}`，**front matter 不经过短代码渲染管线**，于是页面直接印出字面量 `{{< count-providers >}}`，而 `hugo` 全程 exit 0、`validate.py` 也不报。**口诀**：短代码只能出现在 `.Content`（md 正文）里；front matter 的值是纯字符串，想动态就留空让模板层去算（title/description/kicker 需要动态数字时，改在模板里 `printf`，不要塞进 front matter）。此类字面量泄漏可被 `scripts/check_output.py` 的 `{{`/`}}` 扫描兜住。
24. **模板里的固定句会跨页逐字重复 = 同质化模板页（2026-10-03 第八轮）** —— 页面型一旦 ×10 以上实例，模板中**不含国家名/计数的静态句子**（导语、卡片副文案、定死的 H2）会在 12 页里逐字相同。内容层写得再用心，谷歌看到的仍是换皮模板。**两条对策**：① 句子尽量带 `{{ $country.name }}` / `{{ len $nets }}` / `{{ $s.planCount }}`；② 定死的 H2 给 **front matter 覆盖钩子**（本站 networks 已落 `h2_carriers` / `h2_scoreboard` / `h2_brands` / `h2_cities` / `h2_next`）。验收标准：跨页重复句（≥60 字符、≥3 页）必须 **0**，H2 全站 **0 碰撞**。
25. **锚文本必须分散，权威外链必须落在正文（2026-10-03 第八轮）** —— 同一 URL 的锚文本在一页里重复 3 次（如三处都写 `methodology`）是明显的过度优化信号；同一目标出现 2+ 次就换说法。同时每页要有 **3–4 条权威外链**（Opensignal 国别报告 + Ookla 国别报告 + 该国监管机构 + GSMA），**分布在该论点出现的位置**而不是页脚堆一排，且**每条 URL 落库前必须 curl/WebFetch 验真**（监管站 403/000 是反爬不是死链）。页头导航 / 面包屑 / 侧栏属站点框架，重复属正常，不必改。
26. **`hugo server` 会往 `public/` 写 dev 输出（2026-10-03 踩坑）** —— 本站是**手动上传 `public/` 部署、无 CI 配置**。开着 dev server 时 `public/` 里是 `baseURL=http://localhost:<port>` + `livereload.js` 的版本，**直接打包上传就会把 localhost 链接发布到线上**（`llms.txt`、sitemap、canonical、og:url 全中招）。**纪律：部署前先停掉所有 `hugo.exe`，再跑一次 `npm run build`，并确认 `grep -c localhost public/llms.txt` = 0。**
27. **改 `static/` 下会被 watcher 监视的目录前，先停 dev server（2026-10-03 踩坑）** —— 删除 `static/img/esim/图片_backup_20260929/` 时 `mv` 报 `Permission denied`，根因不是权限而是**运行中的 hugo server 持有该目录句柄**；删掉后它的文件监视器抛 `The process cannot access the file`，导致 `/` 与 `/compare/japan/` 渲染 500（生产构建本身是好的）。**顺序：停服 → 改 `static/` → 构建 → 起服。**
28. **AI 检索按「块」抓取，段落首句必须自包含（2026-10-03 第九轮 GEO）** —— 内容页的每个 H2 段落，**首句若以 `This / It / They / The three / There are` 开头，或依赖上一段才读得懂，被 AI 引擎单独抽走就失去意义**。GEO 硬规则：① 首句点名实体（国家名 + 运营商名 + 机构名），不靠代词；② 首句本身就是结论，不是过渡；③ 关键数字带来源与日期；④ 表格前给一句摘要句。实测 12 页 61 个 H2 段落里曾有 29 处违规，改写后为 0。**新写任何内容页都要过这一关**（脚本按 `## ` 分段取首句，正则匹配 `^(It|They|This|That|These|Those|There|Both)\b` 或长度 <45）。
29. **FAQ 问题必须是真 `<h3>`，且一律用 `display:contents` 包裹（2026-10-03 第十轮）** —— 站点 FAQ 是 `<details>/<summary>`，`{{ .q }}` 原先只是裸文本，**不是标题元素**，AI 引擎按标题切块时整块 FAQ 丢失。统一改为 `<summary …><h3 class="contents font-sans text-ink-900">{{ .q }}</h3><span …>+</span></summary>`，8 个版式（networks / guides×2 / research×4 / tools）共用同一标记，改一处要全改。三个连带约束：① **`contents` 不能省** —— 全局有 `h1,h2,h3,h4 { @apply font-display text-ink-950; text-wrap: balance }`，裸 `<h3>` 会把问题渲染成 Sora 深色并平衡换行；`display:contents` 让 h3 不生成盒子，才能**零视觉变化**只拿语义（`<h3>` 置于 `<summary>` 内是规范允许的）。② **FAQ 问题现在会被 `check_headings.py` 扫到**，所以问题文本同样禁 `, ; : — –`（曾有 4 条违规，已改写）。③ **FAQ 问题与同页正文 H2 不能近乎同题**，否则产生同页重复标题（曾有 4 处）；同页 FAQ 内部也不允许两条问答同一事实（英国页 Ireland 两条已换成「北爱尔兰 + 边境漂移」，改为信息增量而非删条目）。
30. **禁止「模板化单句」填充，每个区块必须带独有事实（2026-10-03 第十一轮）** —— `/networks/` 的城市块原本是 `carriers.toml[ISO].info.cities`（**只有城市名**）+ 一句 front matter 泛话（`{城市列表} all run fast 5G on every network, and city signal is not the variable that decides a {国家} purchase. The differences appear…`），12 页同构、零城市级信息，被用户判为「太敷衍、毫无信息增益」。**通用判据：一个区块把国家名换掉后句子仍然成立，它就是填充。** 已改为 front matter `cities_detail`（`name` + `reality`，逐城市一条），reality **必须以城市名起首**（补丁脚本 assert 住），并回答**「这座城市之后，问题从哪条路 / 哪片地形 / 哪个区域开始」**；模板用 `{{ replace $r $n (printf "<strong class='…'>%s</strong>" $n) 1 | safeHTML }}` 加粗段首城市名，使 AI 单独抽走一行仍自包含（与红线 28 同源）。12 页 46 行、跨页重复 0。**新增国家页纪律：`cities_note` 只做导语且必须点名该国自己的排名/结构事实；逐城实况一律进 `cities_detail`；`info.cities` 不能删（`compare/single.html` 在用）。**
31. **Hugo 字符串函数参数顺序不一致，拼用会静默失效（2026-10-03 踩坑）** —— `hasPrefix` 是 **STRING PREFIX**（`hasPrefix $reality $name`），`strings.TrimPrefix` 是 **PREFIX STRING**（`strings.TrimPrefix $name $rest`），同一模板里方向相反。按直觉写 `hasPrefix $n $r` 会**静默走 else 分支**：`hugo` exit 0、四重校验全绿，只是加粗没上屏。**不要拼用这两个函数** —— 要「把段首实体加粗」直接 `{{ replace $r $n (printf "<strong class='…'>%s</strong>" $n) 1 | safeHTML }}`（`replace` 是 INPUT OLD NEW，**字面**替换非正则；HTML 属性用单引号可免 Go 字符串转义）。**教训是通用的**：模板层的静默失败不会被 `hugo`/`check_output.py` 发现，必须**直接断言产物**（`audit_cities.py` 数渲染 HTML 里的 `<strong>` 个数）。要确认签名就起最小站点（`layouts/index.html` 打印各函数输出）实测，别猜。
32. **`.Fragments.Headings` 顶层是「合成根节点」，直接 range 会产出空记录（2026-10-03 第十二轮）** —— Hugo 的 `.Fragments.Headings` 顶层有一个 **ID 与 Title 都为空的容器节点**，真正的 `<h2>` 在它的 `.Headings` 子节点里。写 `{{ range $i, $h := .Fragments.Headings }}…$h.ID…{{ end }}` 会**构建成功、四重校验全绿，但只产出一条 `name:"" / url:"…#"` 的空 ItemList**。两种正确写法（均在最小站点实测）：① `{{ range .Fragments.Headings }}{{ range .Headings }}` —— 一层就是 h2，h3 在各自的子节点里；② 用 `.Content` 的 `findRE` 扁平提取：`{{ range $i, $raw := findRE `<h2[^>]*>.+?</h2>` .Content }}`，再用 `replaceRE` 取 `id` 与标题文本。**教训同红线 31：模板层的静默失败只有产物断言能抓** —— `verify_guides.py` 会数 ItemList 的条数与首条 name。
33. **跨页重复句的检查必须覆盖「所有页面族」，不能只查 `/networks/`（2026-10-03 第十二轮）** —— `audit_networks.py` 只扫 networks，于是 guides 里长期存在：3 个模板 H2（`A regional eSIM or single country eSIM` / `eSIM price guides for other regions` / `More eSIM help before you fly`）各跨 5 页逐字重复、4 段模板正文跨 5 页重复、4 条 FAQ 答案跨 4 页重复。**凡写在 `layouts/` 里、又不含页面变量（区域名 / 计数 / 页面名）的静态句子，必然跨页重复。** 修法：把区域名或计数拼进句子（`One {{ .Params.region }} plan or several single country plans`），或给 front matter 覆盖钩子（guides 长文页新增 `h2_next`）。**通用断言：任意两页的正文段落逐字重复数必须为 0**（检查前先剥掉内链卡片 `<a>…</a>`，那里列同族页面的 description 属合理的重复）。
34. **GEO 结构层必须覆盖每一个内容版式，不能只做 `/networks/`（2026-10-03 第十二轮）** —— 第九轮只把「短答块 / 关键事实 / 实体 ItemList」做进了 networks，`/guides/` 的两族页面与枢纽页**三块全缺**，AI 拿不到可单独引用的直答句，也拿不到实体清单。补齐位置与内容：`layouts/guides/region.html`（短答块 + 6 格事实栅格，全部构建期推导 + 逐国家 `Country` ItemList）、`layouts/guides/single.html`（短答块 + 阅读时长/复核日 + front matter `facts` 事实对 + 章节索引 ItemList）、`layouts/_default/list.html`（短答块 + 子页 `Article` ItemList；当前仅 `/guides/` 使用该版式）。**新增任何版式都要过 GEO 四层验收**，`audit_guides.py`（发现层 llms.txt / 结构层三块 / 标题层 H3 / 正文层首句自足 + FAQ 首答自足）就是这一层的验收模板。**正文层同样适用于 FAQ 答案**：以 `Yes.` / `No.` / `Modestly.` / `It depends…` 开头的答案被 AI 单独摘走等于没信息，必须点名实体。

35. **长文页的右侧吸顶目录：状态样式一律走 CSS 属性选择器，绝不能由 JS 切 class（2026-10-03 第十三轮）** —— 「Basics & how-to」5 篇长文页（`layouts/guides/single.html`）加了右侧吸顶栏（`On this page` 目录 + 热门目的地比价内链；移动端收成正文之前的 `<details>` 折叠块，桌面栏 `hidden lg:block`）。三条硬约定：
   ① **目录只扫 `.Content`**（正文 markdown）。模板渲染的短答块 / 关键事实栅格 / FAQ / 相关阅读 **不进目录** —— 它们要么位于正文之前、要么是页尾模块，进目录只会稀释信号。实现用 `findRE `<h[23][^>]*>.+?</h[23]>` .Content` 扁平提取（`.Fragments.Headings` 顶层是合成根节点，见红线 32），再用 `replaceRE` 取 `id` 与文本、`plainify` 去标签，**返回顺序即文档顺序**。
   ② **高亮状态的 class 绝不出现在 JS 里**。`check_css_sync.py` 会**整个跳过含 `{{ }}` 的 class 属性**（`TEMPLATE_MARKERS`），而 Tailwind JIT 对运行时拼出来的类名静默不编译 —— 两头都拦不住，页面只会「看着能用但没有高亮」。做法：`.toc-link` / `.toc-l2` / `.toc-l3` 写进 `assets/css/main.css` 的 `@layer components`，激活态用 `.toc-link[aria-current="true"]`，JS **只 `setAttribute('aria-current','true')`**，一个 class 都不碰（渐进增强：无 JS 时目录依然完整可点可跳）。
   ③ **`class="…"` 属性必须是静态字面量**：层级缩进用 `{{ if eq $lvl 3 }}…{{ else }}…{{ end }}` 渲染**两个完整的 `<a>` 标签**，而不是把变量拼进 class 属性值 —— 否则该属性被跳过校验，真漏编译没人拦。
   **验收**：`verify_toc.py` 断言每页渲染两份目录（桌面 + 移动）、条目数 == md 源 H2+H3 的 2 倍、每个锚点在页面里都有对应 `id`、且**模板 H2（short-answer / keyfacts / faq / more…）零混入**。右栏整栏 `max-h-[calc(100vh-7rem)] overflow-y-auto`，目录长时内部滚动、sticky 不失效。

36. **给长文补 H3 的唯一合法落点：原文已有的并列子主题（2026-10-03 第十三轮）** —— 用户要求目录做两级，但 5 篇正文当时只有 50 个 H2 与 1 个 H3。**不要为了凑层级硬造小节**：本轮 29 处 H3 全部是把原文**已有子结构**提升出来 —— 加粗引导句（`**Installation** is the download…`）、并列分述（`The first is the chip… The second is the profile…`）、既有清单项（三个价格层、三大 Android 品牌）、两种用户画像（`The short-trip traveler` / `The long-stay traveler`）。提升时必须**同步改写该 H3 后首段的首句为自包含句**（红线 28），否则等于把一个代词开头的段落顶到了「会被 AI 单独抽走」的位置 —— 本轮就是这样多出 4 处 `<45 字符`/代词开头首句，已一并修掉。改完硬指标：标题全局唯一、`check_headings.py` bad h2/h3 = 0、H2/H3 后首句违规 0、跨页重复段落 0。**不要动 bullet 清单**（7 条故障排查、4 步选机流程那类），清单项本来就该是列表，H3 化只收益于「有明确分述结构」的 H2。

37. **Hugo `i18n` 返回的是普通字符串，会被转义；一律要 `| safeHTML`（2026-10-03 第十四轮）** —— 把模板硬编码文案抽进 `i18n/*.toml` 时，`{{ i18n "k" }}` 会把 `&` 转成 `&amp;`、`'` 转成 `&#39;`，与原来的字面量**不再逐字节一致**。实测结论（起最小站点验证）：
    - **HTML 文本节点**：`{{ i18n "k" | safeHTML }}` ✅ 与字面量逐字节相同（`&` `'` `"` `<b>` `&#160;` 全部通过）；不带 `safeHTML` ❌。
    - **属性值**：也必须 `| safeHTML`（**不是** `safeHTMLAttr` —— 后者会把已有的 `&amp;` 二次转义成 `&amp;amp;`）。但属性上下文里 `'` 会被转成 `&#39;`、`"` 转成 `&#34;`，`safeHTML` 也拦不住 —— **含这两个字符的属性值不要抽 i18n**（语义等价但字节不同）。
    - **内联 `<script>`**：JS 上下文会转义成 `\u0027`，`| js` 在本版 Hugo 行为异常 —— **脚本里的文案不能走 i18n**，改为模板把结果注入 `data-*` 属性、JS 只读不算。
    - **`.llms.txt` / `.json` 等文本输出格式同样会转义**，一样要 `| safeHTML`。
    - **口诀：把源模板里的字面量原样存进 TOML，渲染时统一 `| safeHTML`** —— 这就是恒等变换。
38. **模板行尾（CRLF/LF）会直接改变产物字节，而 `core.autocrlf=true` 会偷偷改它（2026-10-03 第十四轮，真实事故）** —— Hugo 把模板里**标签之间的换行**原样写进 HTML，所以模板是 CRLF 还是 LF，`public/` 的字节就不同。本站历史状态是 `layouts/` 「26 个 CRLF + 18 个 LF」混合（`git checkout` 写 CRLF、工具写 LF），导致**同一份提交在不同机器上构建出不同的产物**。本轮事故链：`git stash push -- layouts/`（为对比而临时回退模板）触发 git 按 autocrlf 把 26 个文件重写为 CRLF → 全站 527 页产物全变，一度误判为 i18n 改造引入回归。
    - **已修**：`layouts/` 统一为 LF，并新增 `.gitattributes` 锁定 `layouts/** text eol=lf` + `i18n/** text eol=lf`。
    - **代价**：18 个页面（`compare/matchups`、`esim-deals`、`guides/*` 8 页、`index.html`、`research/*` 4 页、`tools/`）相对旧产物有 **CRLF→LF 的纯空白差异**，已逐页断言无语义变化（同一批内容在 LF 与 CRLF 下 splitlines 完全相同）。其中真正"含多行文本节点"的模板只有 10 个：`compare/matchups.html`、`esim-deals/list.html`、`guides/single.html`、`guides/region.html`、`index.html`、`research/{list,price-index,fair-use-audit,unlimited-esim}.html`、`tools/list.html`。
    - **纪律**：① 不要在 Windows 上用 `git stash` 对比模板（会按 autocrlf 重写行尾）；要对比旧产物请用 `git worktree add` + 手动统一 LF。② 写任何会改模板的脚本，读写都必须 `open(..., newline="")`，否则跨行文本节点的换行符会被归一。③ `scripts/i18n_extract.py` 已内置**行尾预检闸门**，模板含 CRLF 直接 exit 1。
39. **Hugo 模板作用域与函数签名的四个坑（2026-10-03 第十四轮，均起最小站点实测）** ——
    - **`{{ define "main" }}` 新建模板命名空间**：在它**之前**声明的变量（如 `{{ $d := partialCached ... }}`）在 `define` 内部**不可见**，报 `undefined variable "$d"`。赋值必须写在 `define` 内部。同理 `{{ block }}`。
    - **`{{ return }}` 不能写在 `{{ if }}` / `{{ range }}` 块内**：会报 `wrong number of args for return: want 0 got 1`。partial 必须**只有一个顶层出口**（把结果算进变量，最后一行 `{{ return $x }}`）。
    - **`site.Languages` 在 Hugo 0.156 起已弃用**（`.Site.Data` 同样，改 `hugo.Data`）；替代是 **`hugo.Sites`**（返回 site 对象，语言取 `.Language.Lang`）。
    - **`.Format ":date_medium"` 无效**（会输出字面量 `:date_medium`），**只有 `time.Format ":date_medium" $t` 生效**。`time.Format ":date_medium"` 与硬编码 `"Jan 2, 2006"` 在英文下输出**完全一致**（实测 `Sep 30, 2026`），可安全替换 15 处硬编码，且自动本地化（日语 → `2026年9月30日`）。
40. **`check_headings.py` 从写出来起就是空转的（2026-10-03 第十四轮发现）** —— 闭合标签正则写成 `</h>`，而真实 HTML 是 `</h2>` / `</h3>`，**一个标题都没匹配过**；它长期报告「527 页 bad h2/h3 = 0」只是因为从没检查。已修成 `</h\1>`，修好后一次扫出 **8098 个 h2/h3**（同一页 31 个，旧正则 0 个）。修完还发现第二个误报源：`&amp;` 里的 `;` 会被标点禁令命中，所以**必须先 `html.unescape()` 再查标点**。两个修复后真实结果仍是 0 违规 —— 标题确实合规，但守卫现在才真正生效。
    - **通用教训**：守卫脚本本身也要验「它真的会失败」。任何 `bad = 0` 的守卫，都要**故意注入一个反例**确认它报错（本轮对 `check_i18n.py` 就做了这一步）。本轮已把 `check_i18n.py` 与 `check_headings.py` 接入 `npm run build`。

41. **「全站禁止非拉丁字符」守卫已整体删除（2026-10-03 第十五轮，用户决策）** —— 站点要上多语言，禁令会拦住 ja/ko/zh 的合法产物；原方案是「按语言划豁免前缀」，用户决定**直接删**（豁免前缀只是把同一个问题往后推，还要养一张 `LATIN_SCRIPT` 语言表）。删除三处：`check_output.py` ④ + 其 `.json` 分支、`validate.py` §3 的 plan name 检查、`lang_rules.py` 的 `LATIN_SCRIPT` 与两个 `non_latin_exempt_*()`。**连带修复**：`check_output.py` 的 Go 格式串扫描从 `.html` 扩到 `.json`（原先 json 分支只服务于那条禁令，不扩就是死代码）。**代价必须知道**：手动贴进 `data/plans/` 的韩文/汉字套餐名**不再有任何守卫拦截**，防线只剩抓取层 `toml_write.clean_plan_name()`（重抓时自动清洗并打印改动）→ **新抓一批数据后人工看一眼它的打印输出**。反向验证方式：往 `data/plans/airalo.toml` 注入 `日本語`、往 `public/index.html` 追加日文 → `validate.py` 与 `check_output.py` 都必须**通过**（第六轮旧规则下它们会报 2 条 + 5 条）。
42. **运行中的 `hugo server` 会把开发态页面写进 `public/`，污染生产产物（2026-10-03 第十五轮，真实事故苗头）** —— `hugo server` **默认渲染到磁盘**（只有 `--renderToMemory` 才不写盘）。现象：`public/compare/portugal/index.html` 出现 `http://localhost:1313/...` 与注入的 `<script src="/livereload.js?...">`，与基线比对时报「非行尾差异」，一度像是改造引入的回归。实证：`touch data/titlesegments.toml` 后 6 秒内，`public/` 里带 livereload 的文件从 **1 → 6**，`index.xml` / `llms.txt` / `catalog.json` / `index.html` 同时被重写。**两个后果**：① `public/` 在 dev server 运行时**不是可信产物**，此时部署 = 把 `localhost:1313` 发布出去（SEO 灾难）；② `check_output.py` / `check_headings.py` 读的就是 `public/`，会对着混合产物下结论。**规矩**：跑 `npm run build` 与任何产物级校验前，先确认没有 `hugo server` 在跑（`tasklist | grep hugo` / `netstat -ano | grep 1313`）；长期解法是把 `package.json` 的 `dev` 改成 `hugo server --renderToMemory`。**教训与红线 40 同源**：拿到「产物不一致」的结论时，先怀疑环境（谁在写这个目录），再怀疑代码。

43. **页面文案里的「可派生数字」一律不得写死（2026-10-07 第四十一轮）** —— 全站每个数字都从 `data/` 推导，唯独 `data/faqs/*.toml` 的答案曾经写死，代价是：接一个品牌就让 **99 条断言过期**、45 国「最便宜品牌」易主，页面与正上方价格表**自相矛盾**（US 正文说 Roami $2.99，表格里最低的是 Yesim $0.51）。现在这三条答案只留 `{token}`，值由 `layouts/partials/faq-live-tokens.html` 构建期现算，`scripts/check_faq_facts.py` 读产物独立对账（R1–R9）。**新增任何"带数字的文案段落"都照此办理**：能派生就必须派生，派生不出来就别往文案里放数字。
    - **判据**：`grep -n '\$[0-9]' data/faqs/*.toml` 必须 **0 行**（`${cheap_price}` 这种占位不算，因为 `$` 后面是 `{`）。
    - 两个具体坑：① **`{{ return }}` 只能有一个顶层出口** —— 本轮再次踩到红线 39（partial 里写了两处 `return`，第二处退化成 Go 关键字，报 `wrong number of args for return: want 0 got 1`；改写成 `if` 包裹即解）；② **数值区间类 token 要把货币符号包进值里** —— `unl_perday_range` 初版只算 `1.67 to 4.14`，套进 `from ${...}` 就成了「from $1.67 to 4.14」，第二个数丢符号。
    - **守卫要双向验证**：新守卫先对**改造前的旧产物**跑一遍（实测 `342 problem(s) / 100 页`，证明它抓得住且抓得到 jp —— 旧审计器因按固定问法匹配而跳过了 jp），再对修完的产物跑（`OK: 100 country pages`）。只做后者等于没验。
44. **文案里的每一句比较级 / 最高级，都必须能指着一条数据说清口径（2026-10-07 第四十二轮，自己写错又自己抓到）** —— 我在 Q1 的 body 片段里写了「It is also the cheapest per day, at ${cheap_perday}」，想当然以为「绝对价最低 = $/天 最低」。**实测 50/50 国全部不成立**：绝对价最低的永远是最小档（US 的 Yesim 500MB/1 天 = $0.51/天），而 $/天 最低的是长周期大流量档（US = $0.06/天）。同类还有 Q3 的「a metered plan never throttles」—— 听上去对，但它是**无法证伪的绝对句**。**规矩**：说不清口径就删掉，或降级成恒等式（`perDay = price / days`）。⚠ **R10 只保证句架不重复，不保证句子为真** —— 事实正确性靠 R5–R9 与人工复核，写新文案时必须自己盯。
45. **按「句数」设计的判据会被「一个片段里含两句」骗到；要判就判真正的不变量（第四十二轮）** —— 反同质化最初写成「任意两国最多共用 1 句」，结果 Q2 的 open[1] 本身就是两句（"No. Each of the … caps its daily full-speed allowance."），任何两国只要用同一个 open 就命中 2 句 → **42 条假失败**，而真正该抓的「两国共用两个片段」反倒看不出来。改成从片段库反解三元组、判「最多共用一个**槽**」后归零。**副产品更有价值**：`decompose()` 拆不开 = 有人手改了文案却没同步片段库 —— 这个「失败」本身就是一条该报的错（已进 selftest 第 5 例）。
    - **同源教训**：判据要建在**不变量**上，不是不变量在某一层的表现形式。句数是表象，片段组合才是那个不变量。
46. **两处「同一份定义抄第二遍」的诱惑，本轮都主动合并了（第四十二轮）** —— ① 片段库只有一处：`scripts/faq_frames.py`；第四十一轮的一次性 `migrate_faq_frames.py` 已删除（它的 token 化规则并进新库的历史规则），否则两处骨架定义迟早各说各话。② `{neighbor}` 的兜底短语生成逻辑只在 `faq-live-tokens.html` 一处。**反过来也成立**：真正的数据（`countries.toml` 的 `neighbors`）也只有一份，德语站的国名覆盖走 `data/de/countries.toml` 深合并，不复制。
47. **字面 md5 去重会被「页内数字」骗成假绿（第四十二轮，第三十七轮判据的补正）** —— 第三十七轮定的反同质化判据是「模块在 N 页产物里抽文本算 md5，去重后必须 = N」。这条判据对**不含页内变量**的模块是对的，但对 FAQ 三条答案**失效**：它们 49 国"逐字只差数字位"，第四十一轮把数字改成构建期现算之后，字面 md5 去重立刻就是 **50/50/50** —— 全绿，可**句架其实只有 1 种**，模板级重复内容一点没少。**判据升级：先把页内变量（token / 数字 / 国名）抹成占位符得到「骨架」再去重，必须 = N**（实现见 `check_faq_facts.py::skeleton()`，断言见 R10）。**附带的度量陷阱**：按「问题文本」分组也会出假象 —— 问题里含国名（`What is the cheapest eSIM for Thailand?`），按字面分组得到的是 `1/50` 而不是 `50/50`；**必须按问法序号分组**。

48. **「日期 = 构建日」和「日期靠人记得跑脚本」都错，正解是「日期 = 数据最后变化日」且自动维护（第四十三轮）** —— ① 用 `now` 会让 `lastmod` 每次部署都翻新，Google 判定本站 `lastmod` 无信息量后**整体忽略**，而且当价格其实是上周抓的时，「今天核过价」本身就是不实陈述（第二十三轮试过、已撤回）。② 但反过来靠人记得跑 `bump_checked.py` 也一样错 —— 会漏：Nomad 10-06 入库、页面却一直宣称 Oct 4，直到用户发现。正解是 `scripts/stamp_checked.py` 按**内容指纹**自动盖章（已挂进 `npm run build` 第一步）。**判据：页面上每一个印出来的日期，都必须能回溯到一条自动规则，而不是某个人的记性。**
49. **指纹的「内容面」必须与产物的「渲染面」对齐（第四十三轮）** —— 第一版 `block_hash` 把整段原始文本（含注释）算进指纹，于是改一句**行内注释**（`color = "#16456B"   # monogram 兜底色…`）就把 Nomad 的品牌档案核对日从 10-06 顶到 10-07 —— **页面一个像素没变，日期却动了，这正是我们本来要消灭的那类不实陈述**。修法：日期字段行 → 纯注释行 → 行内注释（含引号内 `#` 的转义处理）依次剥掉再算 sha。**通用判据：给「内容指纹」下定义时先问「这块内容会进产物吗」，不会进的一律不许进指纹。**
50. **「首次遇到」的语义会分岔，别用一句代码糊过去（第四十三轮）** —— 同一句「这个单元台账里没有」在两种场景下正确行为**相反**：**首次建台账**（状态文件整个不存在）必须**保留现值**，否则全站日期集体跳到今天 = 批量不实陈述；**台账已在而冒出新的单元**（新品牌 / 新市场入库）必须**盖今天**，否则刚入库的数据顶着旧日期（正是 Nomad 那次的毛病）。**判据：凡带「首次」语义的机制，都要问清是「系统首次」还是「这个对象首次」。** 附带纪律：越权/状态类文件（`docs/checked-state.json`、`docs/regression-manifest.json`）**必须提交进版本库**，它们分别是「最后改动日」与「零回归基线」的唯一记忆。
51. **改数据文件的脚本必须显式声明行尾，否则 CRLF 文件会被写成 `\r\r\n` 并让 Hugo 整站失败（第四十四轮）** —— `Path.write_text()` / `open(..., "w")` 在 Windows 上**默认把 `\n` 转成 `os.linesep`（CRLF）**。而 `data/plans/*.toml` **本来就是 CRLF** → 每个行尾变成 `\r\r\n` → 注释行里出现**孤立 `\r`**（TOML 注释只允许以 `\r\n` 结尾，`\r\r` 里的第一个 `\r` 非法）→ hugo 直接 `failed to load data: data\plans\x.toml:1:1 → toml: invalid character in comment` 拒绝构建。**同一写法对 `providers.toml` 却没事**（它是 LF，转完是合法 `\r\n`）—— 所以这个坑只在「本来就是 CRLF 的那批文件」上炸，测试时极易蒙混过关。**纪律三条**：① 改数据文件一律 `io.open(..., newline="")` + `write_bytes`，或读改写时明确保留原行尾；行内正则用 `[^\r\n]*` 而不是 `.*`（`.` 会连 `\r` 一起吃掉）；② `bump_checked.py` 曾把替换行的 `\r` 丢掉（`raw.rstrip("\r")` 只用于匹配、写回时没还回去），于是 `jetpac.toml` 混进 49 行 LF —— 已修，改法是把 `eol = "\r" if raw.endswith("\r") else ""` 拼回行尾；③ 批量归一化行尾用 bytes：`b.replace(b"\r\n", b"\n").replace(b"\n", b"\r\n")`。**判定行尾的唯一正确姿势**：`crlf = b.count(b"\r\n")`，`lf_only = b.count(b"\n") - crlf`，**不要**用文本模式读出来判断。
52. **守卫里的「不适用」必须显式分账；写成 `if 找得到: 检查` 的单支就等于把检查改瞎（第四十四轮）** —— 品牌子页第 13 项「天数按钮无假档位」原写法是 `if grp:`（找到按钮组才检查），于是「页面上压根没有按钮组」**静默通过**。报告只印 `497/499`：既看不出差在哪两页，也**分不清「按设计不渲染」和「漏渲染」** —— 将来真漏了，数字变小而无人警觉。真相是模板有门槛（`{{ if gt (len $myRows) 3 }}`；斐济的 saily / ubigi 各只有 2 个套餐），属于**按设计跳过**。改成双分支后：`有按钮组 → 断言每个档位都在价格表里真实存在` ／ `无按钮组且套餐 ≤3 → 计入 chips_na 并在报告里显式打出来` ／ `无按钮组且套餐 >3 → FAIL`。**通用判据：任何检查都要能回答「这一页为什么没被检查」。** 配套纪律：改完判据必须注入反例证明它会红 —— 本次把荷兰 jetpac 页的 `id="plan-days-group"` 改名，守卫如期报 `价格表有 15 行却没有天数按钮组` + 退出码 1，随后按字节还原（sha256 一致）。自测方法已写进脚本 docstring。
53. **删品牌时残留的对决页不是静默降级，而是构建失败；而 `gen_provider_pages.py` 只清理子页（第四十四轮）** —— 做 Jetpac 的 A/B 对照构建时，用 `ignoreFiles=['jetpac\.md$']` 排除内容，漏了另外两种命名（`airalo-vs-jetpac.md` 结尾是 `-jetpac.md`、`jetpac-vs-nomad.md` 结尾是 `-nomad.md`），hugo 立刻 `ERROR compare/vs-single: unknown provider "jetpac"` → `nil pointer evaluating interface {}.name`（`vs-single.html` 拿空的 `$pa` 去取 `.name`）→ **整站退出码 1、产物只写出 559/643 页**。两层意思：① 这是「fail loud」，比静默降级好；② 但 `gen_provider_pages.py` 的清理逻辑**只删子页**（`removed` 计数），对决页无人管 —— **真到删品牌那天会先炸构建，然后让人误以为新数据本身有问题**（待办见 §15）。附带：`ignoreFiles` 是**正则**匹配整个路径，`jetpac\.md$` 只覆盖结尾恰好是 `jetpac.md` 的，最宽也最省事的写法是直接写 `jetpac`。
54. **「换措辞」治不了模板化，它是反向操作；而方法论披露句必须全站逐字一致（第四十六轮）** —— 用户拿第三方分析文档来问「如何优化」，文档建议「删或变量化骨架标签」。**照做有害**，三条理由：① Google 规模化内容滥用的判定原文是 *"substantially the same regardless of **minor variations**"* —— 把一句话改成 5 种说法**正是 minor variations 的定义**，页面对 Google 仍「实质相同」；② `Only plans whose validity covers the whole trip are counted here.` / `Typical speeds are our editors' reads of each operator's own coverage data.` / `Prices in USD as listed by …` 这类是**方法论披露**，**一致性本身就是 E-E-A-T 信任信号**，逐页变量化 = 扣分；③ **词法指标有地板** —— 任何「每页渲染一次」的区块（竞品卡 9 张、计算器说明、安装步骤），建多少变体都会让每种变体出现在每一页上。**只有两条正确方向**：**A 换实质不换说法**（把零信息量句子换成承载页内数据的句子）、**B 合并而非改写**（把重复的方法论 / 安装说明收拢到单一权威页，各页留一句 + 链接，**那一句必须全站逐字一致**）。**动手前先给每条重复句分类**：品牌内容（可改）／国家级事实（八品牌 ×50 国 `networks` 完全一致，改只能编造）／方法论披露（不许改）／UI 说明（不值得改）。
55. **「跨页模块 md5 去重 = N」是必要不充分条件；同质化必须另跑一把句子级的尺子（第四十六轮）** —— 那条判据（红线见 `SKILL.md` 反同质化条）的漏洞是：区块里只要含**一个**页内专属数字，md5 就唯一 —— 「95% 的句子雷同、只换了一个价格」照样全绿。实测：奥地利 10 个品牌子页**块级去重 10/10 全唯一，句子级模板槽位却是 74%**。补尺子 `scripts/audit_boilerplate.py`（只读 `public/`，不联网）：只取 prose 标签 `p/li/blockquote/figcaption`，剔 `script/style/nav/footer/header/svg`，按 `[.!?]` 切句取 ≥25 字符，**品牌名→`@`、数字→`#` 两级归一化**，指标 = **占用的句子槽位比例**（槽位 = 全组句子总数；模板槽位 = Σ 该模板句出现的页数）。**量化口径必须写明是「按行」还是「按句子槽位」**：同一份产物按行 69%、按槽位 74%，因为按行会把 `td`/列头/徽章算进正文。**它不进 `npm run build`** —— 诊断工具不是守卫，给阈值就会变成可被「优化掉」的指标。**一次分析只允许引用一个仪器的数字**：临时脚本算 404 槽、正式工具算 604 槽，写进交付文档的数必须能用一行命令复现。
56. **`Path.write_text()` 的 CRLF 陷阱不限于 `data/plans/*.toml` —— 改任何仓库文本文件一律用 bytes（第四十六轮）** —— 红线 51 立了「改数据文件用 bytes」的纪律，但没覆盖 `i18n/*.toml`：本轮用 `write_text` 改 4 行文案，把 `i18n/en.toml` 整份从 LF 转成 CRLF（`de.toml` 仍是 LF）。**因为 `git diff` 只显示 13 行变化**（git 自动忽略换行差异，只在警告里提一句），这个改动**极易蒙混过关**。**纪律升级**：只要不是新建文件，就不许用 `write_text` —— 一律 `read_bytes()` → `decode` → 处理 → `encode` → `write_bytes()`（或用 Edit 工具），改完立刻 `read_bytes().count(b"\r\n")` 复核。附带：Windows 下 `glob.glob('dir/*/')` 返回**反斜杠结尾**，`str(rel)` 也是反斜杠，按 `'/'` 切分解析路径会 `IndexError` 或**静默分错组**，一律改用 `pathlib.PurePath(k).parts`。
57. **衡量「减少重复」要看绝对量，不看占比（第四十七轮）** —— `模板槽位 / 总槽位` 是**横截面**指标（适合比页型），对「删内容」**不敏感**：删掉重复块时分子分母同步下降，占比可以纹丝不动（本轮国家页把 51 遍的安装三步删掉，占比只从 49% → 47%）。**单轮改动的成效必须用绝对量报**：本轮是「每页净减 274 字符可见文本（旧 497 → 新 223），× 51 页 ≈ 14,000 字符」。同理，`--diff` 的「变更 N 页」是**归因**证据，不是**成效**证据 —— 两者要分开讲，别用一个数字冒充另一件事。
58. **判定「某页 / 某能力缺失」前，先数它的实际引用数（第四十七轮）** —— 第四十六轮把 `/methodology/` 写成了「待建 P1」，实际它**早已存在、且被 699 个产物页链接、链接总数 1679**（`compare/single.html`、`esim-providers/single.html`、`vs-single.html`、`index.html`、`esim-deals/list.html` 都已在正确位置链出）。错因：**只核了那几句话的文本，没核链接**，于是从「一句话」反推「整页不存在」。**纪律**：断言缺失前跑 `grep -rn "<路径>" layouts/ | wc -l`，产物侧再跑一次 `grep -rl` 数页面数。**语句的存在性 ≠ 页面的存在性 ≠ 该页被链出。**
59. **front matter 注释必须落在两个 `---` 之间，否则会被当成正文渲染成 `<h1>`；重构断言时别顺手改匹配模式（第四十九轮）** —— 为把「给编辑看的待办」移出读者视野，把 `content/en/privacy.md` / `terms.md` 正文里的 `_Todo: legal review before launch._` 改成 front matter 里的 `# …` 注释。改动方向对（原句被 Markdown 当**斜体正文**渲染，读者与爬虫都看得见），但替换时把匹配模式里的 `\r\n---\r\n` **一起删掉了**，注释于是落在 front matter **外面**：Hugo 把 3 行 `#` 当 Markdown → 页面出现 **4 个 `<h1>`** → `verify_no_regression` 的 B 类不变量当场 FAIL（`✗ privacy/index.html: 4 个 <h1>`）。两条纪律：① **改 front matter 后必须断言分隔符位置** —— `[i for i,l in enumerate(text.split("\r\n")) if l == "---"] == [0, N]`，且注释行号落在两者之间；② **断言可以改，被断言的 pattern 不许顺手改** —— 第一版脚本的断言因 NOTE 文本里含原句而误报，第二版改断言时把 pattern 一并改了（**多余重构**），直接把正确结构改坏。这个 bug 之所以能被守住，靠的正是 B 类不变量（h1 计数）——**「改了内容」和「改坏了结构」是两件事，前者该绿灯，后者必须红灯**。

60. **Python `bytes` 字面量不能含非 ASCII；而「断言」极易撞上自己刚写的注释（第五十二轮）** —— 两个都是同一批一次性补丁脚本上踩到的：
    - `b'...中文注释...'` 直接 `SyntaxError: bytes can only contain ASCII literal characters`。写字节一律 `'...'.encode("utf-8")`（源文件已 `# -*- coding: utf-8 -*-`，字符串字面量本身可以有中文，**只有 `b''` 前缀不行**）。
    - `assert b"starts cheaper in" not in nb` 被**我自己在替换文本里写的注释**命中；`assert b.count(b"fup_note") == 1` 被注释里的 `policy.fup_note` 命中 —— **断言看起来在验代码，实际在验我自己的注释**。
    - **纪律**：① 断言要**只数代码引用**（`{{ .fup_note }}` 这种带模板语法的形态），不要数裸标识符；② 补丁脚本必须**幂等**（目标 key 已存在就 `continue`），否则重跑会二次插入或把断言带偏；③ 改完先 `read_bytes()` 复核（行尾计数 + 目标/残留串计数），别只信脚本自己打的 OK。
61. **零回归基线会「陈旧」—— `--diff` 报出的额外变更要先做「HEAD 对照实验」，别直接当成本轮引入的回归（第五十二轮）** —— 本轮只改了 matchup / provider_hub / provider_sub 三类模板，`--diff` 却报「变更 566 页」，多出 **`networks` 12 页**（该页型全站**总共只有 12 页**，全部变了 → 指向全局因素）。排查顺序：① 产物**确定性**（重跑 `hugo`，抽样文件 sha 是否稳定）；② 变更页里**有无本轮特征串**（本轮四个新句子逐页 grep，`networks` 全为 0 → 排除内容渗透）；③ 模板**是否共享**（`networks/single.html` 不 include 本轮改动的任何模板）；④ **决定性实验** —— 把本轮改动的文件临时换回 `HEAD` 版本重建，看这些页 sha 是否**仍 ≠ 基线**（是 → 基线陈旧，与本轮无关）。结论是：基线生成于 `2026-10-07T10:20:58Z`，而用户在 `2026-10-07 18:55` 提交的 `data/plans/{jetpac,nomad}.toml` 落在基线之后 —— **`--diff` 的基线只在「与数据现状同时生成」的前提下才有归因力**。修法是**重建基线**（`--write-manifest`），并**改数据 / 提品牌后顺手重建**。⚠ 做这个对照实验必须保证工作区**逐字节还原**（`finally` 块 + 还原后 sha256 校验），别为了取证把仓库改坏。

62. **模板里的多行注释会把换行写进产物 —— 全站每页多一行空白，`--diff` 归因当场失效（2026-10-08 第五十三轮，自己踩的）** —— 给 `head.html` 的 hreflang 加守卫时把说明写成 6 行 `{{/* … */}}`。Hugo 把注释**内容连同其中的换行**一起输出（注释文本被丢掉，但换行留下来了）→ 702 页里 **701 页**的 HTML 各多一个 `\n`。预期变更是 `555`（499 文案 + 56 丢 hreflang），实测 `701`，多出的 146 页**全是纯空白差异**。**纪律**：① 会进产物的模板（`layouts/**`）里，`{{/* … */}}` 一律写成**单行**；要写多行说明就放到模板外的文档或 `{{- /* … */ -}}`（后者会吃掉两侧空白，但仍要确认产物字节）；② **归因数字对不上时，先怀疑自己的改动引入了空白/行尾漂移**，再怀疑逻辑 —— 本项目在红线 38（CRLF/LF）上踩过同一个坑。
63. **两把尺子量的是两件事，混用就会得出与事实相反的结论（2026-10-08 第五十三轮）** ——
    - `audit_boilerplate.py`：**归一化**（数字→`#`、国名与品牌名→`@`）后比骨架 → 品牌子页「同品牌跨国家」得 **84–88%**。它把「`Entry price is $2.00 against the country floor of $0.51`」和「`$2.10 / $0.95`」算成同一句。
    - `audit_dup_raw.py`：**不归一化**，逐字比渲染文本 → 同一批页得 **37–52%**。
    **Google 看的是渲染后的文本**，所以回答「重复严重不严重」要用**后者**；横向比页型、看趋势用**前者**。用户拿来的第三方分析报「92%」也是归一化口径（且比 `#`/`@` 更狠，连网络名都抹了）——
    **引用任何同质化百分比，都要先问「分母是什么、抹掉了什么」**。判据：模型给出的重复率若高于 `audit_dup_raw.py` 的结果，要能说清多出来的那部分是怎么算的。

64. **环境里的代理变量会「静默吞掉」所有抓取请求 —— 症状是空响应，不是报错（2026-10-08 第五十四轮，排查了 5 步）** —— 要把关键词采集从 Bing 换到 Google，第一次试探就全部失败：`curl` 返回空体、`WebFetch` 报 `fetch failed`、自写脚本拿到空列表。**排查顺序（可复用）**：① **直连**目标域（`curl -m 8` → `code=000`，超时）；② **`nslookup`** 看解析（`www.google.com` → `31.13.92.37`，落在 **Facebook 段** → **DNS 污染**，解析本身就被投毒）；③ **`env | grep -i proxy`** → 发现 `https_proxy=http://127.0.0.1:62216`（**WorkBuddy 沙箱代理，不通 Google**）；④ **扫本机端口**找可用出口（`netstat -ano` + 逐个试探，实测扫过 7880–7900 / 1080 / 10808 / 33210，**只有 `127.0.0.1:7890`（Clash 混合端口）通 Google**）；⑤ 用 `--proxy` 显式指定后全部恢复。
    **根因**：`curl` / `urllib` / `requests` **默认继承 `https_proxy` 环境变量**，于是所有请求被送进一个不通目标站的代理 —— 而失败的**表现是「空响应」而不是「连接被拒」**，极易被自己的代码吞掉（我的第一版测试把异常 `except` 成空集，据此写出「`esim france` 无补全」的错误结论，隔 3 秒重试 4 次其实每次都返回 9+ 条）。
    **纪律**：① 抓外网前先 `env | grep -i proxy`，**不要相信环境的默认代理**；② 脚本里把出口**硬编码成常量**（本项目 `kw_harvest_google.py` / `kw_trends.py` / `kw_trends_compare.py` 统一 `PROXY = "http://127.0.0.1:7890"` + `urllib.request.ProxyHandler`），别依赖环境；③ **空响应 ≠ 目标没有数据**，必须把「拿不到（异常/超时）」与「拿到了但是空的」分成两种状态计数（`kw_engine_compare.py` 的 `status ∈ ok/empty/error`）。
65. **补全证据 ≠ 真实热度 —— 一个词被 45 个种子带出来，真实热度仍可能是锚词的 0.000x（2026-10-08 第五十四轮，本轮最重要发现）** —— `is esim available in portugal` 被 **45 个种子**带回（补全广度极强，按上一版「需求分」会排进头部），但用 Google Trends **批量比较**量出来只有 `esim`（锚词）的 **0.000x**；而 `saily esim canada` 是 **0.4** —— 相差**三个数量级**。
    **机制**：补全词表反映的是「**Google 认为与你输入相关的查询**」，其中包含大量**语法变体、拼错、长句、问答式长尾**，这些在真实查询量上极低；而补全在**种子密集的语境里还会饱和**（同一地理簇的种子会带回同一批词，`sources` 数字虚高）。**批量比较则是 Google 官方在样本期内对实际查询量的直接度量**。
    **正确的跨词热度尺子**：Trends **按批归一化**（同批最热词 = 100），**跨批不可比** → 每批固定塞入**锚词 `esim`**，取 `相对热度 = 均值(词) / 均值(锚词)`。实测锚词在 **23 批里稳定 76.5–76.6**，证明跨批可比（这是方法自洽的**自证**，必须每次都查）。工具：`scripts/kw_trends_compare.py`（`ANCHOR="esim"`、`BATCH=4`，Trends 单次上限 5 项）。
    **排期用法**：补全广度用于**发现词**与判断「这个词是否有人这样搜」，真实热度用于**排优先级**；两者冲突时**信热度**。
66. **报告里的一切阈值必须现算 —— 写死一个「看起来合理」的数字，会得出与事实相反的结论（2026-10-08 第五十四轮）** —— 首版报告我用 `综合分 ≥ 60` 判「高需求」，输出「城市词 **965 个里 0 个**高需求」，看起来像「城市词毫无价值」。**查分布才发现**：全站中位 **35.1**、前 10% 阈值 **46.4**、前 1% 阈值 **54.8**，`≥60` 全站只有 **95 个词（0.8%）** —— 60 这个数**根本不在这个标度的可见范围**，结论是假的。
    **纪律**：① 任何「高/中/低」分档的阈值都从**当次数据的分位数**取（`Q10 = sorted[0.10N-1]`、`Q01 = sorted[0.01N-1]`），并在报告标题里**标注阈值与其来源**；② 报告正文里的**每一个统计数字都现算**，不硬编码 —— 上一轮在别处踩过「硬编码 1,473 个词，数据更新后变成不实陈述」；③ 判「某类词都没价值」之前，**先看该类词在整体分布里的位置**（同类词若整体偏低，可能与分类规则或打分权重有关，而不是「该类目无用」）。

67. **文案里「冠词紧邻占位符」必错 —— 这个坑踩了两次，第二次才改成机器拦（2026-10-08 第五十六轮）** —— 第二十四轮写 `whether a {{ .brand }} plan`，渲染出 "whether **a Airalo** plan"；第五十六轮又写 `Does a {{ .brand }} eSIM work in …`，渲染出 "Does **a Airalo** eSIM work"。两次都是「靠人在写文案时记住」失败的。
    **为什么人工记不住**：品牌名从 Airalo 到 Yesim **混着元音/辅音开头**，国名同理，**一个固定冠词不可能全对**，而且这是**数据修不好的语法错误**。
    **两个反直觉点**：① **不能按「首字母是不是元音字母」判** —— `Ubigi` 的 U 发辅音 /j/，正确写法是 "**a** Ubigi plan"；`United*` / `UAE` / `Ukraine` / `Uganda` / `Uruguay` 同理。用首字母做判据会**误报**，把对的判成错的。② **产物级守卫有盲区** —— 它只看得到**当前真的渲染出来**的组合。实测品牌 Hub 里 **7 个** printf 问句都写成 `a %s eSIM`，当时只有 **3 个**在当前品牌分层（`$v 1`/`$v 2`）下渲染，**另外 4 个 + `networks/single.html` 那句全绿通过** —— 等元音开头的品牌/国家进来才暴雷。
    **纪律**：① 文案里**永远不要**把冠词写在占位符前面 —— 换语序永远可行（`an eSIM from {brand}` 对 Airalo 和 Yesim 都对）；② 守卫必须**两道都做**：产物级（抓已渲染的）+ **源码级（禁写法：`a %s` / `a {{ .x }}` / `a {token}`）**，源码级那条才是防潜伏的；③ 禁令要**窄化到专有名词占位符**，放过 `a {{ .days }}-day trip` 这类数值，否则满屏误报（本项目实测：全站 8 处 `a %s` 全是真问题，0 误报）；④ `scripts/check_article_agreement.py`，`--selftest` **18 项**，**双向验证**（证明抓住 + 证明放过）。**它的战绩**：首跑抓出 **47 处**存量；修完当轮又抓出**我新写的 2 处** —— 守卫在同一个回合拦住了写它的人。
68. **同一个「重复」用两把尺子会得出相反结论 —— 先问「这把尺子抹掉了什么」（2026-10-08 第五十六轮）** —— 判跨页内容是否重复，项目里现在有两把尺子：`skeleton()`（把 token/数字/**国名**都抹掉再比）与**产物级 md5**（逐字比）。拿前者去判国家页的邻国问答（Q6），结论是 **8/50「唯一」**，看起来像大面积重复；拿后者判同一批数据是 **50/50 唯一**。
    **真相**：Q6 的答案**天生靠国名区分**（"…a trip that also takes in Japan needs…"），`skeleton()` 把国名抹了，等于把唯一的区分维度删掉 —— **是尺子失真，不是数据重复**。
    **纪律**：① 判「重复」前先问「这个模块靠什么区分」，**判据里必须保留那个维度**；② 尺子与用途绑定并写进注释（`check_faq_facts.py` 的 R10(f) 用 skeleton 尺子判手写槽，R11 用产物尺子判 Q6，**两处互不越界**）；③ 引用任何一个「唯一率」数字时同时说清**是哪把尺子、分母多少、抹掉了什么**（与红线 63 同源）。
69. **跨页模块的验收判据：抽文本算 md5，去重后必须 = 页数 —— 手写的内容也要纳入断言（2026-10-08 第五十六轮）** —— 本轮自证脚本逐问统计 50 国 FAQ 的答案 md5，结果 **9 个槽位 50/50，只有 Q4「ID 核验」是 37/50** —— `kyc_required = true` 的 **14 国共用同一句套话**，且那句话里**既没有国名、也没有该国具体规定**。而 `countries.toml` 的 `quirks` 里其实躺着 14 国各自的真实登记事实（越南身份证上传 / 墨西哥 CURP / 阿根廷 DNI / 埃及线下证件照 / 中国反向：走香港网关、无需登记……）。
    **两个教训**：① **「守卫不报错」≠「内容没问题」** —— 这条重复是**已知历史遗留**，守卫里明写着「只报数不判失败」，所以构建一直全绿，**只有换一把更硬的尺子（md5 去重）才暴露**；② **手写的内容也必须进断言** —— 池子化（拉丁方阵）的槽位有骨架守卫兜着，手写槽位没有，恰恰是它烂了 14 页。修完把 `check_faq_facts.py` 的 R10 从五条扩到六条（新增 **R10(f)** 判第 4、5 条），并加了 `手写槽（ID）撞车 → slot4` 这条自测反例。
    **判据模板**：任何跨页模块（FAQ / 品牌卡 / 须知块 / 城市句 …）验收时，把该模块在**全部 N 页**产物里抽文本算 md5，**去重后必须 = N**；值 < N 说明模块里含「全局字段」或套话，要换成页内派生量（该国档位数 / 最低价 / 最佳 $/GB / 本地网络 / 算出的排名结论）。

70. **本地化的「查找串」必须覆盖数据里的非规范写法；例外要写在两侧、口径一致（2026-10-09 第六十一轮）** —— 套餐名 `data/plans/*.toml` 的 `name` 是**供应商原始产品名**，德国国家页要按词本地化，踩到三件事：① **规范名匹配不到非规范写法** —— CZ 的规范英文名是 `Czechia`，供应商写的却是 `Czech Republic`，只按规范名替换会**静默漏译**（构建全绿、页面留着英文），所以别名单列 `data/planaliases.toml` 并断言「没有死条目」；② **Hugo 的 `replaceRE` 是 Go RE2，没有 lookahead**，`Canada Mobile` 这种「品牌名里长着国名」的形态不能写成 `(?!\s+Mobile)`，只能**前置 `findRE` 判定整条跳过**；③ **`index` 链要防 nil** —— `index (index site.Data.x $k) "y"` 在 `$k` 不存在时是 `index nil "y"`，**直接报错**，必须 `with` 包一层。守卫是 **`scripts/verify_de_text.py` 的 E1–E3**（E1 无英文结构词 / E2 无英文国名 / E3 英语单元格逐字 ∈ 原始名集合），**它能回答「这一页为什么没被检查」** —— 所以例外（Mobile 品牌形态）同时写在源级断言与产物级判据里。⚠ **订正（2026-10-09 第六十三轮）**：本条曾写作 `scripts/verify_plan_names.py`，**该文件从来不存在**（引用前先 `ls`）；E 段 2026-10-09 已扩到 **A–F**，`--selftest` **30 项**。
71. **多语言的「数据覆盖层」层级必须实测；模板改对了不等于产物改对了（2026-10-09 第六十二轮）** —— 把 `fup_note` / `promo_label` / `quirks` 三类英文句子接进德语页时卡了很久，两个坑各值一条：① **`data/<lang>/*.toml` 的顶层键就是它自己的键** —— 取数处是 `$d.strings`，而 `index hugo.Data "<lang>"` 的 `strings` 的值**就是该文件的内容本身**，文件里再写一层 `[strings]` 表头 ⇒ `$d.strings` = `{strings:{…}}` ⇒ `index . $s` 永远落空 ⇒ **查表静默返回原串、德语页照旧印英文**（对比：`countries.toml` 的顶层本就是 ISO 键，所以没有这个坑）。诊断方法是这一轮最大的收获：**把 partial 与数据原样拷进一个多语言最小 Hugo 站，用探针打印 `index hugo.Data "<lang>"`、`$d.strings` 的键与 `len`** —— 150s 的全量构建换成 50ms 的迭代；另注意 `{{ with $d.strings }}` 对 nil 安全，但 `{{ len $d.strings }}` 在英文站会**直接把站点构建打挂**。② **模板改对了 ≠ 产物改对了** —— 判据必须是产物级的：`verify_de_text.py` 的 E4（德语页不得出现 125 条英文数据串的原文）第一次跑出 **752 处**，而当时 `partial "de-text.html"` 明明已经在模板里。「查表未命中就原样返回」是**有意的降级**，所以覆盖完整性只能靠生成器的断言兜（数据侧每个取值都有条目 + 表里没有死条目），partial 兜不住。③ **大批量翻译不要手抄英文键** —— 101 条 `quirks` 改用「按 ISO 分组 + 组内同序 + 条数断言 + `set(德语数字) ⊆ set(英文数字)`」，一次跑出零错配（数字集合不一致当场变红）。

72. **验收判据的盲区常常是「页型」，不是「写法」（2026-10-09 第六十三轮）** —— 德语站已经有 5 个页型（`/de/`、`/de/compare/` 索引、`/de/guides/`、`/de/networks/`、`/de/research/`），而 `verify_de_text.py` 的 E1–E5 **只走 `/de/compare/<国家>/`** —— 一条判据都没管那 5 类页，实测 3 页在漏英文（`/de/research/` 17 处、索引 5 处、`/de/networks/` 1 处），而十一项闸门全绿。已补**判据 F**（扫 `public/de/**/index.html` **全部**德语页，清单 23 条短语 + 8 个词，每条注明来源页；**新增页型自动纳入**）。★ 教训：**「某类问题已归零」是断言，不是事实 —— 先问「判据覆盖了哪些写法、哪些页型」。** 自测 `--selftest` 23 → 30 项。

73. **改模板会改产物字节 ——「空白也是字节」，恒等判据不只在文案上成立（2026-10-09 第六十三轮）** —— 本轮改的全是**纯文案**（英文字面量 → `i18n`），理论上英文侧产物应**逐字节不变**，实际连撞三次、**三次都不在文案上**：① **新增一个「独立的注释动作块」**——注释本身不输出，但它前后的**换行与缩进是字面文本**，首轮 `--diff` 报 **22 处（含 18 个英文页！）**全是纯空白；→ 说明一律**并进既有注释块**。② **模板头部（第一个输出型标签之前）多插一行 = 多一个换行** —— `compare/list.html` 聚合层在页头 `<div>` 之前，加一行 `{{ $iso := . }}` 就让**英文**索引页变一个字节；→ 能用作用域里的 `.` 就别新开变量。③ **注释块里不许出现「成对花括号」** —— `i18n_extract.scan()` 只把 `<!-- -->` 当注释、`{{/* */}}` **不是**，注释里的 `{{ partial … }}` 会被当**动作边界**，紧随其后的说明文字被判成「模板层硬编码文案」→ `check_i18n.py` 报 **ERROR**、构建 exit 1。★ 教训：`--diff` 报出「不该变的页」时，**第一步是逐字节比对那份产物**（`cmp` / sha256），先分清「文案变了」还是「空白变了」，再找逻辑原因。

74. **`i18n` 的未译量 = 「哪些页型还不存在」的清单 —— 生成页面前必须先翻 key（2026-10-09 第六十三轮）** —— `scripts/i18n_coverage.py de` 现算：**1671 key，已译 1054 = 63.1%，仍有 617 条英文占位**；按前缀分布恰好对应待建的页型（`compare_provider` 112 ↔ 499 个品牌×国家子页 / `esim_providers_single` 124 ↔ 10 个品牌 Hub / `compare_vs_single`+`compare_matchups` 32 ↔ 45 个对决页 / `esim_deals_list` 112 / `tools_list` 48 / `research_*` 109 / `guides_*` 43）。**顺序反了就会产出「德语 URL + 英文正文」。** ⚠ 同一逻辑适用于模板：`layouts/compare/provider.html` 的可见套餐名（379/558 行）与 JSON-LD `Offer.name`（243 行）仍是裸 `plan.name`、`.fup`/`.fup_note`/`$country.quirks` 未接 `de-text.html` —— **先修模板再建页**（`/de/esim-providers/` 那 3 处就是照此提前抽的 key）。

75. **「黑名单」判据必须让位于「穷举」判据；数据层与模板层要分开判（2026-10-09 第六十四轮）** —— 德语站有两条扫「英文残留」的判据，性质完全不同：**F 是黑名单**（23 条短语 + 8 个词，靠人想全，且**大小写敏感**）、**G 是穷举**（清单 = `data/de/strings.toml` 里**已有德语译文的英文原串**，来自数据本身）。本轮实测 F 全绿的同一批页面里：德语 `<title>` 印着 `… Unlimited Data Plans` —— F 无感，因为清单里写的是小写 `plans`；`provider.policy` 的 `fup_allowance` / `hotspot_note` / `topup_note` 从无德语、模板全是裸插值，**德语页整段印英文而 F 一条没报**（黑名单里"恰好"没有那些词）。补上 G 段（扫 `public/de/**/index.html` 全部页型，**含 JSON-LD** —— `visible()` 会把 `<script>` 整段挖掉，50 个德语国家页的 `"name": "Best … ranked by cost per GB"` 曾同时躲过 `check_output` 与 F）后首跑 **24 处**。★ 两条教训：① **F 的清单永远追不上数据** —— 新增一个数据字段时，只要它的德语译文进了表，G 就自动覆盖，不需要人去加黑名单；② **穷举判据必须带防误伤的边界** —— G 首跑在 `/de/networks/` 报 7 条「残留英文」，全是德语**小数点逗号**（`65,1 Mbps` 天然含子串 `1 Mbps`），加左边界 `(?<![\d.,])` 后归零。这正是「守卫变噪音源 → 被优化掉 → 等于没有守卫」的典型路径，自测里专设一条注入清单验证该边界。

76. **同一事实的第二份译文是缺陷，不是备份；发现重复要删一份（2026-10-09 第六十四轮）** —— 修 policy 字段的德语时，我先在 `data/de/strings.toml` 里老老实实译了 **51 条**（10 品牌 × 6 字段），跑通断言、构建全绿 —— 然后才发现 **`data/de/providers.toml` 早就 60/60 全覆盖了**（`_gen_de_data.py` 生成，模板读深合并后的 `$d.providers`，德语站拿到的本就是德语），而且两份口径**已经不同**：德语覆盖层用 `Sie` + `Mbps` + `unbegrenzte Tarife`，我新写的用 `du` + `Mbit/s` + `Unlimited-Tarife` —— 同一个德语站出现两种人称、两种单位写法。★ 判据：**policy 的六个文本字段刻意不进 `strings.toml`**，覆盖完整性改由**判据 H** 断言（对每个品牌 × 每个非空文本字段：德语覆盖层缺键 → 英文泄漏；值 == 英文原文 → 等于没译）。H 段首跑就抓到 **6 处** `fup_drop` 与英文**一字不差**（`1 Mbps` / `512 Kbps`，英语缩写未本地化）—— 正确修法是**改生成器本地化单位**（`_gen_de_data.py` 的 `units()`，幂等），**不是给判据加白名单**（那句话本身就是英语写法）。★ 推广：`info.support/refund` 是反向例子 —— `data/de/providers.toml` **故意不写**这三个字段（继承英语侧），所以它们**必须**走 `de-text.html` + `strings.toml`（19 条）。**同一类字段的两半走两条不同的链**，判断依据是「德语覆盖层写不写它」，不是字段名。

77. **`href` 自己拼站点路径 = 译文站的「静默语言降级」——三道死链检查一道都抓不到（2026-10-09 第六十五轮）** —— `lang-href.html` 的三层兜底（本语言 → 默认语言 → 原路径）**只有经过它才生效**；裸写 `href="{{ printf "/compare/%s/%s/" $slug $key }}"` 会在**德语页上产出英文路径**。它不是死链（目标存在），于是：`check_links.py` 看不出、产物级死链审计也看不出，**53 处链接 / 2 个页型全绿** —— 只有按「语言降级（`/de/` 页链向非 `/de/` 站内链接）」这个口径扫才现形：德语国家页把 `/de/compare/austria/roamic/` 写成了 `/compare/austria/roamic/`，德语用户点「Zum Roamic-Tarif」被静默送到英文页，GSC 还会看到语言不一致的内链。全仓库实测 **18 处 / 6 个模板**（`compare/single.html` 7 处、`esim-providers/single.html` 6 处、`compare/list.html` / `compare/provider.html` / `esim-providers/list.html` / `networks/list.html` 各 1 处）。修法：`href="{{ printf "…" … }}"` → `href="{{ partial "lang-href.html" (printf "…" …) }}"`（`scripts/_wire_lang_href.py`，`--selftest` 8 项：含括号参数、幂等、静态资源不动、一行两处）；并**把判据并进 `check_i18n.py` 第 6 项**（`raw_lang_href()`，正例 6 / 反例 3）。★ 静态资源（favicon / css / img）**不走 `printf`，天然不报** —— 别给它们加语言前缀。★ 教训：**「不 404」不等于「对」**；跨语言的内链要单独一条判据，死链检查永远看不见它。

78. **`lang-href` 的第 2 层兜底让「死链审计」天然失效 —— 审计口径要按语言，不是按存在性（2026-10-09 第六十五轮）** —— 给德语站写产物级死链审计，第一次跑出 **0 死链**，差点直接收工；实际是 `lang-href.html` 第 2 层「默认语言有该页 → 用它的 `.RelPermalink`」把 `/about/`、`/contact/`、`/privacy/`、`/terms/`、`/methodology/`、`/disclosure/` 六条**全降级成了英文路径**。审计要加两个维度才有效：① **语言维度**（只统计 `/de/` 页链向非 `/de/` 的站内页面链接）—— 这才是 D8 的精确待办清单（实测按此列出 6 个根页 + `/guides/how-to-install-esim/` + `/research/*` 等）；② **排除语言切换器**（`<a href="/" hreflang="en-us">` **故意**指英文，按 href 粗扫会每页贡献若干条假降级，把真缺口淹掉）。★ 另一条同源发现：`header.html` 的 mega menu 用 `site.GetPage` + `with`，**缺页则整段不渲染**（语言安全）；页头/页脚的固定链接用 `lang-href`（**静默降级**）—— **同一个 header 里两种模式混用**，只有实测能分清哪条链路需要补内容。★ 慢构建的副作用：加入 499 个德语子页后全量构建 **3 分钟 → 11.5 分钟**，判据前移（`.buildlog/audit_head_keys.py` 扩到扫 `content/de/**/*.md` 正文的 h2/h3）的价值随之上升。

79. **「凡渲染 `plan.name` / `fup_note` 都必须走对应 partial」这条约定只写在 partial 的 docstring 里 —— 约定写在注释里等于没有约定（2026-10-10 第六十八轮）** —— `plan-name.html`（套餐名本地化）与 `de-text.html`（数据层英文句子本地化）的 docstring 都明写「凡渲染它的地方都必须走本 partial」，但**没有任何守卫强制**。建研究栏目 3 张德语页时，三个模板（`price-index` / `unlimited-esim` / `fair-use-audit`）**全部漏接**：plan 名裸 `{{ .name }}`（F 判据抓到 `Days` / `Local` / `Day`）、`fup_note` 裸 `{{ . | truncate 110 }}`（G 判据抓到 8 条英文原文）。★ 三条判据：① **英文侧构建全绿** —— 两个 partial 在英语站是恒等变换（`$en == $loc` 跳过国名替换、词表值 == 源词），缺陷**只在德语页可见**，所以「英文站过了」推不出「译文站过了」；② 这类漏接**只有在那个页型的译文页存在之后**才会暴露 —— 本轮之前德语侧只有 55 页、没有 research 页，F/G 一直是绿的（F 词表的注释写着「修完后实测为 0」，那是按当时的页集写的，**页集变了就要重跑**）；③ 修法必须**改 dict 构造点**而不是逐个渲染点 —— `price-index` 的 `bestName`、`unlimited-esim` 的 `cheapestName` / `bestDailyName` 都是「构造一次、多处渲染」（表格 + FAQ 共用），改构造点一处即全覆盖。★ 没有便宜的自动化守卫：`.name` 在模板里同时是国名/品牌名/运营商名/套餐名，纯正则分不清；可行纪律是**新页型的德语页建好后必须跑 F + G**。

80. **拼接列表的末位连接符与兜底词是语言相关的 —— `delimit $x ", " " and "` / `cond … "None"` 把英语语序写进了模板（2026-10-10 第六十八轮）** —— `layouts/research/fair-use-audit.html` 的 FAQ 答案用 `delimit $names ", " " and "` 拼品牌名单，德语页印出 `… Saily and Ubigi …`（F 判据恰好把 `and` 列进词表才抓到；同一行的 `None` / `none` 两个兜底词**至今不在任何词表里**，属静默漏网）。修法：连接符复用既有 key `g_and`（en `and` / de `und`），兜底词新增 `g_none` / `g_none_lower`。★ 判据：**`delimit` 的三参形态（`COLL DELIM LAST`）与 `cond` 的字面量兜底，都是「写进模板的英语」，必须过 i18n** —— 三参 `delimit` 的第三个参数最容易被当成「分隔符」而不是「语言词」。★ 欠账：全站 i18n 里同时存在 `g_and` 与 `faq_tokens__list_conjunction` 两个「and」key（同一事实两份真源），本轮选了 `g_and`，另一个留给 `faq-live-tokens.html`，**未合并**。


81. **☠ 数据文件里的「数组」不写进 `data/de/` 覆盖层 = 整段静默回退英文，且 F 只看得见零头（2026-10-10 第七十二轮 d44）** —— `data/networkreports.toml` 的 `[[XX.awards]]`（记分板表格，`layouts/networks/single.html:244`）在 `data/de/networkreports.toml` 里**一组都没覆盖**（英语 35 组 / 德语 0 组）。Hugo 的 data 深合并是「**map 递归、数组整体替换**」⇒ 整表回退英文，**构建 exit 0、`check_output` 全绿**。★ 三条通用判据：① **必须为「数组型数据字段」维护一张显式清单**（本项目目前三例：`planaliases` / `info.cities` / `networkreports.awards`），其他两个都已有专项判据，只有 `awards` 漏了；② **F 是黑名单，永远是下限** —— 它只抓到含 `and`/`every` 的 **12** 条，真实是 **35 组 × 3 字段中 77 个非空字段全英文**，**低估 6.4 倍**；③ 覆盖完整性只能靠**逐字段对齐**的源级判据（`verify_de_data.py::check_reports` 现补 `awards`：整国缺失 / 组数不符 / `carrier` 被改动 / 字段未译 / 数字不符 / 德语侧死条目）。★ **为什么此前一直全绿**：`awards` **只在 `/networks/{land}/` 渲染**，而那 11 个国家的德语 networks 页是批 D 才建出来的（`check_output` 页数 1279 → 1291）；页集一变，绿灯作废。★ 产物级断言必须**双向**（英语串不在 **且** 德语串在）：只证「英文不在」会被「整张记分板走 `{{ if $awards }}` 的 else 分支」骗过去（`check_award_products()`，自测 3 例含这条）。**取证**：新守卫跑改造前产物 = **154 处 = 77 字段 × 2**。
82. **「绿灯只在当时的页集下成立」—— 新页型一旦建出，必须重跑 F + G + 数据覆盖守卫（2026-10-10 第七十二轮）** —— 这是红线 79 第②条（research 页建出才暴露模板漏接）的**第二次**实证，而且这次暴露的是**数据层**而不是模板层：`awards` 从未进 `strings.toml`，所以 **F（黑名单）与 G（只认「已进表的数据串」）同时失明** —— G 的设计前提是「已进表」，对**从未进过表**的字段天然看不见。★ 纪律：**新增任何「数据驱动 + 会被译文页渲染」的字段后，三件事一起做** —— ① 写进 `data/de/` 覆盖层；② 写进 `verify_de_data.py` 的逐字段判据；③ 若该字段「只在某一页型渲染」，**在该页型的译文页建出来之后重跑一遍全量守卫**（不能只重跑英文侧）。
83. **同一个术语在「数据层」与「内容层」各译一遍 = 同页两词打架；且改术语必须同步改「生成源脚本的字面量」（2026-10-10 第七十二轮）** —— `/de/networks/{land}/` 的正文（`single.html:213` `{{ .Content }}`）与记分板（`:244`）**渲染在同一页**：正文用 `Download-Tempo`（批 D 方言，76 处，**全部**在 `content/de/networks/*.md`），数据层用 `Download-Geschwindigkeit`（**215 处**：i18n 28 / data/de 119 / 其余正文）。实测分布证明 `Tempo` 是**局部方言**不是全站标准 ⇒ 向西对齐（`scripts/_patch_networks_tempo.py` 归并 75 处正文 + 80 处生成源）。★ 三条硬约束：① **`Tempo` 中性 / `Geschwindigkeit` 阴性** —— 裸替换会写出 `das Geschwindigkeit`，必须逐条手写**变格表**（`beim Tempo`→`bei der Geschwindigkeit`、`mit einem Download-Tempo`→`mit einer …`、`Dein eigenes Tempo`→`Deine eigene …`、`rohem Tempo`→`roher …`、`über das Tempo, das du`→`über die Geschwindigkeit, die du` …）；② **变格自查必须带右边界** —— `ein Geschwindigkeitstest` 是合法复合词，裸子串匹配会假红（首跑确实踩了）；③ **生成源脚本的字面量必须一起改** —— `_patch_networks_de_{1,a,b,c,batch}.py` 按「内容与字面量比对」决定是否写盘，留着旧方言 = **重跑就把方言写回去**；`_patch_networks_de_terms.py` 更直接 —— 它以「old 命中 0 且 new 已存在」判幂等，术语一改就 **FAIL**。验收：6 个脚本 `--dry` 全部 `断言全过` / `已应用 0 / 已存在跳过 12` ⇒ 字面量与落盘内容逐字一致。★ **反例（不许过度归并）**：`Durchsatz`（22 处）**保留** —— 英语原文是 `Throughput`（与 `Speed` 不同的词），而同一页的 `Upload Speed` **奖项名**才译 `Upload-Geschwindigkeit`；先查英文原词再决定要不要统一。
84. **☠ 英语 `compare` 正文的数字是 8 品牌时期快照，与同页 `seo.description` 自相矛盾（2026-10-10 第七十二轮发现，**第七十三轮已修**）** —— `content/en/compare/{50 国}.md` 正文里的计划数 **43/50 过期**、best rate **16/50 过期**、unlimited 数 **48/50 过期**（例：US 计划 220→254、unlimited 91→100；AU best rate `$0.66`→`$0.64` 且品牌 roami→nomad），而同一页 front matter 的 `seo.description` 是 `regen_meta_brand.py` **实时现算的（50/50 正确）** —— 同一页两处数字互相打脸，读者与 Google 都能看见。
    **修法**：新建 `scripts/_en_compare_lib.py`（口径与德语侧同源 `_compare_de_facts.py`，**槽位正则表是唯一真源**）+ `scripts/_en_compare_fix.py`（改写）+ `scripts/_en_compare_changelog.py`（逐条变更表）。
    **验收（全部现算）**：49/50 页正文改写、**`japan` 逐字节未变**（它是编辑性长文：无 `N plans` 句、无 `$/GB` 句，`$4-8`/`$3.90`/`$1.05`/`$18.99` 经核对仍自洽）；真实变更 **98 行 / 305 token** = 品牌名归一 147 + 数字与计量 152 + 套餐规格覆盖 6；`--verify` **0 处过期**、`--dry` **幂等 0 处**；`content/en/compare` **52 页改动后仍 52/52 纯 CRLF**（归一 LF 处理、写回还原）。
    ★ **三条纪律**：① **只换槽位，绝不重写句式** —— 英语正文是 **50 套独立手写句式**（P1/P2/P3 各 50 个不同开头），是反同质化资产，整篇重生成等于自毁；② **`626` 是正则匹配次数不是「变化的处数」** —— `sub_group()` 对每个匹配都 +1（含替换后同值的幂等命中），**引用工具输出前必须先读计数那几行代码**，否则审核表里会写下一个偏大 2 倍的数字；③ **rate 冠军品牌会随数据漂移** —— 上游根因是 `Nomad` 的 `Local {Country} - 30 Days - 50 GB` 在 8 国以更低 $/GB 夺冠（AU/BR/MA/QA/SA/US），另有 `Jetpac`（GE/AE）与 `Nomad`（TH），所以**「某国最便宜费率是谁」不能硬编码进正文**，必须每次现算。
    ★ 别以为德语绿了英语就绿了 —— 这条正是「**同一事实有两份真源（正文手写快照 vs 页脚现算）就一定会漂移**」的实证。

85. **☠ 「解禁类」改动（删 noindex）会一次性改全站 hreflang —— 变更集合必须能被一个等式闭合，且 x-default 有硬语义（2026-10-10 第七十二轮 D9）** —— 德语分层发布解禁后，**不再有 noindex 页**，于是 `head.html` 的两侧守门（`{{ if and (not .Params.noindex) (ne .Kind "404") }}` 与 `{{ range .Translations }}{{ if not .Params.noindex }}`）同时放开：德语页首次发 hreflang，**英语页也首次发指向德语的 `hreflang="de-de"`** ⇒ 全站 1288 页的产物字节全变。★ 三条硬约束：① **变更集合必须闭合** —— 实测 `1290 = 644 德语 HTML + 644 英语 HTML + de/sitemap.xml + robots.txt`，恰好 = 「全部 hreflang 页 + 两个声明文件」；**验收时要把这个等式写出来**，否则「1290 页变了」无法与「哪里出了问题」区分；② **x-default 的语义是「默认语言版本」，不是「当前页」** —— 本站默认语言是 en（`defaultContentLanguageInSubdir = false`，英文在根路径）⇒ **en 页的 x-default 指向自身、de 页的 x-default 指向 en 页**；写法用 `{{ if eq .Language.Lang "en" }}{{ if gt (len .Translations) 0 }}{{ $xdef = .Permalink }}…{{ else }}{{ range .Translations }}{{ if eq .Language.Lang "en" }}…`，**必须加「有译文组才发」的条件**，否则无译文的英语页会挂一条孤立 x-default；③ `check_hreflang.py` 的判据 C（reciprocal）对 `tgt == rel` **跳过**，所以「英语页的 x-default 指向自身」不会假红 —— **加 x-default 前先读判据，别凭直觉以为会红**。★ **已知无害副作用（别当成缺陷修）**：`check_i18n.py` 的「拼装句碎片」**48 → 49**，新增 1 处是 `layouts/robots.txt` 里新加的 `Sitemap: {{ .Site.BaseURL }}de/sitemap.xml` —— robots 的 `Sitemap:` 是**机器指令**不是文案；想消除它只能改用 `printf`，那会把更严的「printf 格式串文案」判据从 0 顶到 1，**得不偿失**。
86. **「新栏目上线会改全站导航」—— 验收出现大批『不该变的页』时，先怀疑「条件渲染的导航/列表」，并能指名到具体模板行（2026-10-10 第七十二轮）** —— 批 D 建出 `/de/networks/` 后，`pub_manifest --diff` 报 **499 个 `de/compare/<国>/<品牌>` 页变更**（另有 45 个 vs 页等）。逐个 `diff` 出的差异是**导航栏多出一项**：`<a href="/de/networks/" aria-haspopup="true" …>Netzkarte` + `<div class="nav-mega left-auto right-0 w-[32rem]">`。真源是 `layouts/partials/header.html:31` 的 `{{ with site.GetPage (printf "/networks/%s" $c.slug) }}` —— **有该国的 networks 页才渲染该项**。★ 纪律：① 大批页面变更**不等于**缺陷，但**必须有指名到模板行的解释**才算归属完成（「大概是导航吧」不算）；② 同类「条件渲染」还有：语言切换器（译文页存在才指向它，否则 fallback 到 `/de/`）、`og:locale:alternate`（有译文才发）—— **建任何一个新栏目/新译文页型，都要预期「全站导航 + 语言切换器」的连带变更**；③ 归属方法：拿一份更早的 `public/` 快照（`.buildlog/pub_dNN/`）做 `difflib` 的**非空行差异**统计，**「只增空行」与「内容变」要分开数**。

87. **「抽查」写出的判据，首个假红源永远是判据自己 —— 四条实例（2026-10-10 第七十三轮，德语上线前技术收尾）** —— 本轮新增两个只读抽查装置 `scripts/_de_schema_audit.py`（结构化数据）与 `scripts/_perf_audit.py`（首屏性能），**每条硬判据都有 `--selftest` 合成正例 + 逐条反例**。当场踩到的四类误报，全部是「判据不够精确」而不是「产物有缺陷」：
    ① **资源类 URL ≠ 语义链接** —— `/de/` 页里 `logo = https://www.esimsift.com/apple-touch-icon.png`（同一张图，语言无关）被「自有 URL 必须带 `/de/` 前缀」判成违规，645 页全红。改成 `RESOURCE_KEYS = {logo, image, contentUrl, thumbnailUrl, urlTemplate}` 豁免后，**同一个判据收敛出唯一真缺陷**：645 页的 `publishingPrinciples` 指向英语 `/methodology/`。
    ② **伴生 origin 静态看不见** —— `preconnect https://fonts.gstatic.com` 被判「未被请求」（1290 页红），因为 CSS 里只写了 `fonts.googleapis.com`，字体文件从 gstatic 取 ⇒ 显式成对放行（`COMPANION`），**H2 归零**。
    ③ **以 CLS 为目的的判据不能只看属性** —— 「每个 `<img>` 必须带 `width`/`height`」报出 3810 处，但 flags 的 `class="h-9 w-[3.25rem]"` **已经固定了盒子**，静态读不出 CSS；「必须带 `loading`」报出 2412 处，全部是首屏 header logo（**eager 才是对的**）。两条一起**降级为报告项**，并在判据 docstring 里写明降级理由 —— **判据的目的是防 CLS，不是凑属性**。
    ④ **「数量级异常」要顺着计数口径往回读代码**（同红线 84 第②条）。
    ★ **反过来，抽查真抓到的四个缺陷**（全部可穷举、可复核）：`publishingPrinciples` 语言错（645 页）；JSON-LD `BreadcrumbList` 硬编码 `Home` / `Compare countries`（645 / 499 页），而**同页可见面包屑走 `g_home` / `g_compare_countries`** ⇒ **同一页两套面包屑互相矛盾**（判据：JSON-LD 里硬编码英文 vs 可见层已 i18n）；`esim-providers/single.html` 的 4 条 `additionalProperty.name` 硬编码英文（10 页）；`head.html` **无条件 preload 首页 hero（373 KB）**，而该图**只有 `layouts/index.html:57` 一处真正渲染** ⇒ 1288 页白预加载（判据 H1：`preload` 的图必须在**同页正文**被引用）。★ 另有两个登记未做的结构性发现：**全站 1290 页根本没有 `<head>` 元素**（`baseof.html` 只写了 `<!DOCTYPE><html>{{ partial "head.html" }}<body>`；浏览器会隐式补，严格解析器读不到 title/meta/canonical）；`/tools/` 把 50 国套餐库以 **1.16 MB 内联 `<script>`** 塞进 HTML（gzip 98 KB，不可缓存）。
    ★ **改模板前先证「产物字节守恒」的正确姿势**（本轮实证）：`head.html` 的 hero preload 改成 `{{- if .IsHome }}…{{- end }}` 时，**第一次写的版本给首页多输出了一个换行**（`{{ end }}` 自己那一行也带换行）。修法不是再猜，而是**搭一个最小 Hugo 探针站**（`.buildlog/_tpl_probe/`，2 页，秒级渲染）分别跑改造前 / 改造后模板，`cmp` 到「首页逐字节相同 **且** 非首页 = 旧产物删掉那一行」才落盘；顺带用同一探针证明了「`{{/* … */}}` 注释由单行改多行**不改产物**」。

88. **「穷举清单」只解决「清单要全」，不解决「产物要全」—— 判据的**扫描面**本身也会漏（2026-10-10 第七十四轮）** —— 判据 G 的清单来自数据自身（`english_data_texts()` 185 条），一直被当作「穷举」那一条，但它的**扫描面**是 `glob("**/index.html")`：`/de/llms.txt`、`/de/catalog.json`、RSS `*.xml`、`sitemap.xml` 全都读不到。实测这两处 —— **`/de/llms.txt` 10 条 `promo_label`（Anbieter 区块促销句）+ `/de/catalog.json` 14 条 `fup_note` + 硬编码英文 `notes`** —— 全是英文原文，而**十项闸门全绿**。★ 三条纪律：① **问「判据覆盖了哪些页型」之外，还要问「覆盖了哪些产物形态」** —— 一个站点的产物不只 HTML（llms.txt / catalog.json / RSS / sitemap / robots 都是对外可读的），**判据枚举什么，就只保护什么**；② **扩扫描面前先换实现** —— 逐串带回溯的 `(?<!\d.,])` 正则（185 条 × 3 MB 的 catalog.json）要 **33 s**，644 个 HTML 页要 **256 s**（≈ 全量构建的四分之一）；改成手写 `str.find` + 手动查左边界后是 **0.3 s / 8 s**，且**换实现前后在 644 个页上逐页比对命中集合完全一致**（「等价」要有证据，不是「看起来一样」）；③ **JSON 产物要还原 `\uXXXX`** —— Hugo `jsonify` 把 `&` 写成 `\u0026`，不还原就漏判；④ **语言覆盖层分两半，模板要认对那一半** —— `promo_label` 在 `data/de/strings.toml`（走 `de-text` partial），`tagline` 在 `data/de/providers.toml`（深合并直接拿到）；**同一行里两个相邻字段走两条完全不同的本地化链路**（`data/de/providers.toml:8` 的注释就是这条分界），漏看一处就会在德语页印出英文。
    ★ **同轮修掉三个由此暴露的德语侧缺陷**：`/de/llms.txt` 的 `promo_label` 未过 `partial "de-text.html"`；`llms.txt` 的 `promo_expires` 为空时印出 `, expires )` / `, gültig bis )` 残句（**9/10 品牌**为空；站点既有惯例是 `esim-providers/single.html:466` 的 `{{ with $p.promo_expires }}…{{ else }}…{{ end }}`，判据是「模板与既有惯例不一致」）；`/de/catalog.json` 的 `fairUse` 同样漏 de-text + `notes` 是**两语都硬编码**的模板字面量。
    ★ **附带发现：「一次性迁移脚本」的 `--selftest` 可能早就红着** —— `scripts/_llms_de_l10n.py` 不在 build 流水线里，迁移落盘后 `old == new`，而 `audit(old, new, env)` 两侧**共用同一个 `env`** ⇒ 「改英文值会判红」这条反例**结构上失效**（同一 `env` 改了两侧 ⇒ 永远相等）。修法是让反例**自带基线**（`flatten(new, ENV)` 充作改造前那种硬编码模板）。**不在流水线里的守卫必须定期手跑 `--selftest`；把「有守卫」当结论，比没有守卫更危险。**

89. **旁路校验器不许重抄主判据的实现 —— 两份抽取代码必然漂移出「假红」（2026-10-10 第七十四轮交付后复核）** —— `scripts/_en_compare_stale_audit.py`（只读对账器）与 `scripts/_en_compare_fix.py`（改写器）对**同一批 50 页**给出**相反**结论：前者报 **13 处过期**（12 页 `entry_gb` + `fiji` 的 `tech`），后者 `--verify` 报 **0 处**。逐条把命中位置打印出上下文句子后确认 **13 处全是假红**，根因是**同一个事实被两个实现分别抽取**：
    ① 对账器把 `_en_compare_lib.RE_ENTRY` **内联抄了第二份**，**抄漏了 `(?! a day)` 负向断言** —— 这条断言存在的意义正是排除**盈亏平衡句**（`…only makes sense past about 3.6GB a day`）；丢了它，12 页的**盈亏平衡值**就被拿去比 `entry_at_rate_mb / 1024`（且用的是 `re.search` 只取首个匹配，而非 `finditer`）；
    ② 对账器的 `tech` 分支只写了 `all 5G` / `a mix of 4G and 5G` 两种，**缺 `{4G} → all 4G`**；而 `_en_compare_lib.py :: tech_phrase()` 的注释里**早就写下过这同一个教训**（「本站只有 FJ 属此情形，写成 mix 会假红（本库首版确实这样错过一次）」）⇒ **主判据改对了，旁路器还停在旧实现**；
    ③ **例外集同理** —— 改写器用 `SKIP = {"japan", …}` 排除编辑性长文，对账器自己另立一份 ⇒ `japan` 的 `$3.90 per day flat`（日价）与 `Below about 5GB of expected usage`（盈亏平衡）被当成 `entry_price` / `entry_gb`。
    ★ 三条纪律：**① 旁路器一律 `import` 主判据的实现（连例外集 `SKIP` 一起），本文件只做汇总与呈现，一行正则都不许自己写；② 交付「0 处」之前，必须能区分这个 0 是「判据跑过且全过」还是「另一个实现根本没跑」；③ 假红比漏检更危险** —— 漏检只是没发现，假红会把人引去改**本来正确的正文**（本轮若照做，就会把 12 页正确的盈亏平衡句与 FJ 正确的 `all 4G` 改错）。这也是红线 8（一份事实只允许一份真源）在**判据层**的表现。
    ★ **验收姿势**：`--selftest` **8 / 8**（正例 4：盈亏平衡句不产 `entry_*`、`about 800MB a day` 不产 `entry_mb`、`entry_gb` 写对不判红、`all 4G` 不判红；反例 2：`entry_gb` 写错判红、`all 4G` 写成 `all 5G` 判红；另 2 项为边界与同源性）；**隔离临时目录**端到端注入 —— 正例（全槽位写真值）**0 判红**、反例（仅把入口 GB 改成 `9.9`）**恰好判 `['entry_gb']`**；改造前 → 后 **13 处假红 → 0 处**（EXIT `1` → `0`），与 `_en_compare_fix.py --verify` 结论一致；`SKIP` 例外页在报告里**显式列出**（不静默丢弃）。

90. **多语言站里 `.Site.BaseURL` 与 `absURL` 都解析到「默认语言根」—— 凡读者点得动、或被爬虫读走的内链都必须带语言前缀；而这类判据有一条 `/de`（无尾斜杠）的临界边界（2026-10-10 第七十五轮，德语上线前技术收尾）** —— `hugo.toml` 是 `defaultContentLanguageInSubdir = false` + 顶层 `baseURL`，**没有 per-language baseURL** ⇒ 德语页里 `.Site.BaseURL` / `absURL "x/"` 统统产出 `https://www.esimsift.com/x/`（**英语根**）。实测 4 处独立缺陷、13 个模板文件：
    ① **JSON-LD 面包屑 `item`**（`partials/schema.html:6/11/13`）—— **1643 处 / 645 页**（其中 645 处是首页项被判成英语根）；
    ② **可见面包屑「回首页」+ 站点 logo**（`partials/breadcrumbs.html:3`、`compare/provider.html:182`、`compare/vs-single.html:55`、`esim-providers/single.html:12`/`:181`、`partials/header.html:4`、`partials/footer.html:4`）—— **645 页**，每页面包屑 1 处 + header/footer 两处 logo；
    ③ **`/de/llms.txt` 的 68 处英语根内链 / 去重 66 种**（`layouts/index.llms.txt` 的 15 处 `absURL`）—— 同一文件里由 `.Permalink` 生成的国家/品牌行却是对的（**两种机制并存**才是最难查的形态）；
    ④ **德语 research 页指向 `catalog.json` 的 2 处**（`research/list.html:196`、`research/price-index.html:250`）—— 而 `/de/catalog.json` **确实存在**（3.03 MB、`notes` 已是德语）。
    ★ **正解分两类，不许用同一个函数**：① **Page 路径**（导航/内容页）用 **`.Site.Home.Permalink`**（= 当前语言首页；英语下与 `.Site.BaseURL` **逐字节等价**）或 `partial "lang-href.html"`（三层兜底、对英文站恒等）；② **非 Page 的生成文件**（`catalog.json` / `llms.txt` / RSS）`lang-href` **兜不住** —— `site.GetPage` 找不到 ⇒ 退回 `relURL` ⇒ 仍指英语根，**必须用 `absLangURL`（或 `relLangURL`）**。
    ★ **必须故意保留 `.Site.BaseURL` 的 10 处**（遍历到不许改，不是漏改）：`Organization` / `WebSite` 的 `url`（**组织身份，指官网根才语义正确**：`compare/provider.html:284`、`schema-org.html:13/27`、`schema.html:47/48` = 5 处）、`Product.image`（图片资源、语言无关：`esim-providers/single.html:431/433` = 2 处）、`robots.txt:45/46` 的两个**站点级** sitemap（2 处）、`index.catalog.json:41` 的 `url`（1 处）。
    ★ **判据层四条硬边界**（写守卫必踩，全在 `--selftest` 里）：① **`/de` 无尾斜杠是合法语言根** —— 面包屑首页项对 `.Site.Home.Permalink` 做了 `TrimSuffix "/"` ⇒ 德语侧落在 `/de`；只认 `/de/` 会把 **645 页判成假红**（**模板改对了、守卫反而报红**，这是本轮最先发现的一条）；② **组织身份 URL 要豁免、但只豁免身份键** —— `Organization`/`WebSite` 的 `url`/`@id` 豁免（实测 1815 处），**同宿主下的 `publishingPrinciples`（披露页）仍必须带 `/de/`**；豁免整张宿主 = 过度豁免；③ **语言泄漏判据必须**：先挖掉 `<script>`/`<style>`（红线 6，`ld+json` 内 `\"` 是合法转义）、href **全形态**提取（双/单/无引号 —— 只认双引号会把 93 条低估成 11 条）、认**自有域名的绝对写法**（`https://www.esimsift.com/…`，否则面包屑「回首页」被当外链放过）、豁免带 `hreflang` 的语言切换器；④ **必须扫非 HTML 产物**（红线 88）—— 首版只扫 `*.html`，`/de/llms.txt` 的 68 处整片漏掉。
    ★ **为什么十项闸门全绿却带着 1600+ 处泄漏**：`scripts/_de_schema_audit.py` 第七十三轮就写出来了，**但它从未进 `package.json` 的 `check:output`**（「有守卫」≠「守卫在跑」，同红线 88 末条）；而 `check_i18n.py` 的「0 处未过 lang-href 的 href」是**模板源码级**判据，看不见三类真源 —— i18n **值**里的硬编码 URL、`.Site.BaseURL` 这类**非 printf 字面量**、以及 `printf` 先赋给变量再经 `%s` 注入 i18n 的写法。本轮把 `_de_schema_audit.py` 与新建的 `_de_link_leak_audit.py` **一并接入**（`check:output` **10 → 12 项**，两者都放**链尾**：未经实战的新守卫失败时不该遮蔽已验证的闸门）。
    ★ **验收（全部现算）**：`--selftest` **13/13** + **16/16**；**英语侧 1889 文件 0 增 0 删、变更 646 条全部落在德语侧、英语侧变更 = 0**（硬证 `.Site.Home.Permalink ≡ .Site.BaseURL`、`absLangURL ≡ absURL` 在默认语言下等价）；德语侧 **1643 处面包屑 + 96 处畸形 href（`i18n/de.toml` 17 条值写成三层转义 `\\\"` ⇒ 链接带字面反斜杠、点不动）+ 93 条英语内链 + 68 处 llms.txt → 全部 0**；`/de/llms.txt` 143 处自有域名 URL 全带 `/de/`；`<html lang="de">` 645/645、canonical 自指 645/645、robots `noindex` 0、`og:locale de_DE` 645/645、`/de/sitemap.xml` 644 条全 `/de/`、`/de/index.xml` language `de-de` 且 637/637 link 指 `/de/`。
91. **☠ 全局 partial 改一行 = 全站 1290 页皆变 —— 「几乎全站皆变」的 diff 必须先用「唯一未变页」自证归因，再刷基线（2026-10-10 第七十七轮）** —— `partials/{head,header,footer,schema,breadcrumbs}.html` 被**每个页面**引用 ⇒ 任意一行改动（哪怕只加一句注释）都会改全部 1291 个 HTML 的字节。本轮 `--diff` 报 **1290 / 1291 页变更**（新增 0 / 删除 0），与「上一轮英语侧 0 变更」直接矛盾 —— 真因是**基线写在 14:29:19，而 15:15:17 有一批全局 partial 改动落盘**（`header` / `footer` / `schema` / `breadcrumbs` + `compare/provider.html` + `compare/vs-single.html` + `esim-providers/single.html` + `index.html`；另 15:18:33 `guides/region.html`、15:35:09 `index.llms.txt` + research 两页），上一轮的合法改动**从未折进基线**。
    ★ **三条纪律**：① **先排除三条假因** —— CSS 是否内联（`grep -rl "<style" public --include="*.html"`，本站 = **0**，产物是**外链无指纹**的 `<link rel=stylesheet>` ⇒ 改 CSS **不改** HTML 字节）、是否有构建日注入（`stamp_checked.py` 是否报「无改动」、全站是否出现今天日期）、渲染是否确定（`hugo -d .buildlog/_det` 与 `public/` **逐文件 sha256 比对**；本站 **identical 1889 / differing 0** ⇒ **Hugo 完全确定性**）。
    ② **★ 用「唯一未变页」做锚点自证（最省力的一条）** —— 全站唯一未变的页是 `en/index.html`（`alias_shell`，**270 bytes 裸跳转壳**：`<title>` + `<link rel=canonical>` + `meta http-equiv=refresh`，**无 `partial` / `<header` / `<footer` / `og:site_name`**）⇒ 结构上**天然免疫**全局 partial 改动。**`1291 − 1 = 1290`，精确等于报告数 ⇒ 归因闭环**。若「总页数 − 未变数」对不上报告数，才需要去逐页 diff。
    ③ **归因清楚了再刷基线，且每轮改完立刻刷** —— 否则下一轮会把上一轮的合法改动当成回归噪声，`--diff` 的「全站皆变」变成常态，**真正的回归就淹没了**。
    ★ 附带一条：**守卫的只读性要单独查一遍** —— 12 项守卫的全部写入必须只落 `tempfile.TemporaryDirectory()` 夹具或 `docs/regression-manifest.json`（仅 `--write-manifest`）；**任何守卫写 `public/` 都是红线违规**（本轮实测 12 项全部合规）。
92. **过滤器的语义由「需求类型」决定：覆盖型用 `≥`，预算型必须用区间（2026-10-10 第七十七轮）** —— 国家比较页新增数据量过滤时定下的规则：**天数 = 覆盖型需求 → `≥` 正确**（去 3 天，30 天套餐也满足）；**数据量 = 预算型需求 → `≥` 错误**（用户只为 3GB 付费，不该被推 20GB）。用 `≥` 做数据量过滤会让用户**越选越多、无法选择**。
    ★ **五条实现纪律**：① 桶位**左开右闭**（`gb > lo && gb <= hi`），否则相邻桶重叠；② **`gb = 0`（无限）必须有独立桶，且不许泄漏进 `0-1`**（`gb === 0` 在 `<= 1` 下会假命中）；③ **空桶不渲染**（`{{ if gt (index $szCnt "x") 0 }}`）—— 某国没有该档位就不给按钮，避免点出空结果；④ 桶计数**由数据推导**（写死会点到不存在的档位）；⑤ 计数文案**服务端渲染整句**，JS 只做筛选、**不拼句子**。
    ★ **验收必须证两侧**：**空桶省略**用隔离探针工程（fixture 故意让某桶为空 → 断言该桶缺失、其余在位）+ 全 50 国「渲染桶集合 == 有货桶集合」；**区间语义 + 分区性**用 node 从模板**抽真源函数**跑（本轮 `szMatch` **12/12**，16 个样本各**恰好落进 1 桶**、违规 **0**）。
    ★ 顺带登记：**交互控件的取舍顺序是「能点一次」>「展开再点」>「hover」** —— hover 展开在**移动端不可用**（一半流量），且 JS 动态插入的内容 **Google 可能读不到**；凡需展开内容一律优先 `<details>/<summary>`（零 JS、可键盘、可索引、移动端天然可用），并**复用既有 `.faq-icon`** 而不是新造交互范式。
93. **☠ 数字驱动的段落「只能有一个句号」—— 留一句静态收尾，等于白做（2026-10-10 第七十八轮，同一坑栽了两次）** —— 对决页要降低模板重复，把说明句改成带本页数字的句子。第一版写成「Counts run … across the 50 countries listed below**. A country stays visible when either provider's entry plan falls in the band, not the size of every plan on the market.**」——前半句有变量，**后半句是纯静态**。而重复度探针**按句末标点 `(?<=[.!?])\s+` 切句** ⇒ 那条静态后半句照样是一条 **45× 逐字复制句**，「≥40 次复制句」从 16 条变 **18** 条 —— 做了一轮"降同质化"，指标反而变差。第二版又犯了同一个错（gap 章首句末尾加了「Open a country to see every plan on both sides.」）。
    ★ **三条纪律**：① **含变量的段落只能有一个句号** —— 其余从句一律用逗号 / 破折号 / **分号**连接（分号不触发切句），并把原来的静态收尾**并进那条含变量的句子**；② **改文案前先量化分散度**，别用构建试错（一次全量 ≈ 11 分钟）：`python -X utf8 .buildlog/p78_sentence_variance.py` 从**当前产物转录**数字（不重算 `vs-agg`，避免第二份真源），比较候选变量集的去重数后一次改对 —— 实测 `(metered, unlim, total)` 只有 **10 种组合、最大重复 15 页**，多带一个「两家更低的那个全球入门价 `$lo`」后降到**最大 6 页**（阈值是 40）；③ **删掉的信息要确认别处已有**（"点国家名会打开完整比较"这句在表格下方那条脚注里本来就有 ⇒ 删得掉）。
    ★ **判据口径**：「骨架重复率」**不能**当同质化判据 —— programmatic SEO 的数据驱动句抹掉变量后必然同形（本站骨架重复率 **93.4%**，但正文**逐字**重复率只有 **46.8%**，且去重后 **96.4% 的句子全站唯一**）。Google 的 *minor variations* 指**正文文本逐字相同**。两口径要并列报，并写清各自抹掉了什么（同红线 63 / 81）。
94. **☠ 新建守卫必须先用真实仓库校准判据边界 —— 一条凭直觉写的规则会在正确代码上误报 160 处（2026-10-10 第七十八轮）** —— 新守卫 `check_printf_arity.py` 的第一版把「`i18n "K" (dict …)` 多传了一个键」一律判为「模板与文案漂移」。跑真实仓库：**`provider.html` 一处误报 160 处**。逐条看才发现那 160 处**全是刻意设计** —— 德语 36 个 key 用宾格/与格国名（`country_acc` / `country_dat`），英语用 `country`，模板因此**同时供给各语言各自需要的形态**；而 Go 对多余的 dict 键**静默忽略**，产物无任何可见差异。
    ★ **纪律**：① **判据分级要按「是否会被读者看见」**，不能按「源码看起来是否冗余」—— 少传占位符 ⇒ 产物印 `<no value>`、格式动词元数不符 ⇒ 印 `%!(EXTRA …)` ⇒ **硬失败**；多传一个任何语言都没用到的键 ⇒ Go 静默忽略 ⇒ **WARN**（实测 55 处真冗余，不阻塞）；② **「必需」= 该 key 各语言占位符的并集**，不是某一语言的集合（用全局并集会把 2608 处无 dict 的 `{{ i18n "k" }}` 全判红）；③ **各语言占位符集合互不相同是允许的**（语法需要），别判；④ **写完立刻对旧源码跑一遍**，误报数就是判据的边界说明书（与红线 7「写完守卫先对改造前产物跑一遍」同源）。
95. **跨文件的「格式串 ↔ 实参」契约必须前移成构建前守卫 —— 产物级闸门抓得到，但要等一次全量构建（2026-10-10 第七十八轮）** —— 本轮在 `/compare/matchups/` 的 FAQ 里写了 `printf (i18n "…") $total`，而该 i18n 值**一个 `%` 占位符都没有** ⇒ Go 把多余实参印成 `%!(EXTRA int=45)` **到读者页面上**（4 个页面，含 JSON-LD）。它被末端 `check_output.py` 判据① 抓到，但代价是**一次 11 分钟的全量构建**。
    ★ **根因是跨文件契约**：格式串住在 `i18n/*.toml` 的**值**里，实参个数住在 `layouts/**` 的**模板**里，而 `check_i18n.py` 只扫「`printf "字面量"` 里有没有英文文案」，管不到这条。**新建 `scripts/check_printf_arity.py`** 并接进 `npm run validate`（秒级、构建前拦）。
    ★ **实现要点**：① **Go 模板的实参不加括号**（`printf (i18n "k") $a` 的圆括号只包住 `i18n`）⇒ 不能靠括号平衡找实参边界，**必须按 action 边界 `{{ … }}` 切**（首个版本就是这么错的，selftest 5/5 MISS 才暴露）；② 格式动词**收窄成白名单** `[sdvqf]`，收全字母表会把 `20% off` 里的 `% o` 当成「合法八进制动词」而漏判（而 `printf "Save 20% off" $x` 在 Go 里正是 `%!o(string=…)`）；③ 自检要分**正例 / 硬反例 / 软反例**三类（本轮 10 + 9 + 2 = 21 项两侧都证）。
96. **☠ 「已发现，尚未编入索引」的机械主因往往是**站内可达性**，不是内容重复 —— 一份写死在全局页脚里的清单会人为制造孤岛（2026-10-10 第七十八轮）** —— GSC 报 45 个对决页「Discovered – currently not indexed」。**先量化再动手**的做法证明真因不在文案：`partials/footer.html` 里**写死的 6 组「Popular matchups」**出现在**每一页**的页脚 ⇒ 那 6 个对决页各拿到 **646** 条入链，而其余 **39** 个只从自己的兄弟页拿到 **49** 条 —— 页面被 `sitemap` 声明（= Discovered）但站内几乎无路可达（= 优先级/信号不足），与 GSC 提示**逐字对应**。
    ★ **修法与纪律**：① **页脚/侧栏的"相关链接"必须上下文相关**（对决页 → 同品牌的其他对决；品牌页 → 该品牌的对决；其余页 → 兜底），并用 `{{ .RelPermalink }}` 排除自身；② **复用同一个真源**（本轮导航与页脚共用新 partial `nav-matchups.html`，不抄第二份清单）；③ **验收看 min/max 之比**：改造前 `49 / 49 / 646`（39 页孤岛）→ 改造后 **`646 / 646 / 646`（英语侧口径）**、**`1388–1812`（全站 en+de 口径，零孤岛）**；页脚已换成**上下文相关**（1290 页共 **53 种不同组合**，单个对决页的页脚入链最低 **102**，改造前最低 **49**）—— ⚠ **引用内链数必须带口径**：探针正则要求 `href="/compare/` **紧跟**，`/de/compare/…` 因此不计入；④ **别把「共用控件逐页相同」当缺陷** —— 45 页里那 16 条逐页复制句中，**6 条是站内共用控件/披露句**（对比构建器、条形图图例、方法/披露链接），它们逐页相同是**正确的**。
97. **☠ 判据的「取值集合」必须当场证非空 —— 空集恒真，那是假绿不是通过（2026-10-10 第七十八轮）** —— 校验导航内链语言前缀时，我按「从 `nav-mega` 起、到第一个 `matchups/"` 止」切区域，实际切出来**是个空集** ⇒ `语言前缀错误 = 0` 打印得漂漂亮亮，**其实一条链接都没检查**。同一轮还出现过「chip 档位集合种类数 = 1」——真相是**每页的档位集合都是空集**，`{()}` 自然只有一种（因为我按 `id="…-X"` 猜，而真实属性是 `data-sz`）。
    ★ **纪律**：① 凡「扫出来的集合」**必先断言基数与期望一致**（本轮改成「1290 页每页必须恰好 45 条」才把判据救活）；② **区域切分只用结构边界**（`</nav>` / `</tbody>` / `</main>`），**不要用「某字符串第一次出现的位置」** —— 标记顺序一变就静默退化成空集；③ **属性名/类名先 `grep` 源码确认再写判据**，猜出来的判据不是判据；④ **假绿比假红更危险**：假红会吵你，假绿**悄悄地什么都没查**（同红线 88 / 94）。
98. **☠ 导航下拉的「精选子集」必须与全量真源分离，且匹配失败要炸构建 —— 空切片会让菜单静默降级（2026-10-10 第七十九轮）** —— 本轮把 Versus 菜单从 45 组收窄到 6 组。精选清单第一版写成 `airalo-holafly`，而比对串是 `printf "%s-vs-%s"` 产出的 `airalo-vs-holafly` ⇒ **6 组全部匹配不上**，partial 返回**空切片**，`{{ if gt (len $vsItems) 0 }}` 走 `{{ else }}` ⇒ **Versus 菜单变成一个单链接，Hugo 一声不响**（第一次全量构建就这么白跑了 7 分钟）。
    ★ **纪律**：① 精选清单必须写**页面 slug 全形**（含 `-vs-`，即 `/compare/<slug>/` 的最后一段）；② partial 里必须 `{{ if ne (len $items) (len $picks) }}{{ errorf … }}{{ end }}` —— 已验证 `errorf` 会让 `HUGO_EXIT=1` 并打印明确原因（把一个组合改成不存在的 `airalo-vs-ubigi` → `picks 6 组，只匹配到 5 组 …`）；③ **收窄导航 ≠ 删页**：其余 39 组的真源、sitemap、枢纽页、页脚上下文推荐全部保留，只是入口减少 —— 但**必须把入链代价算出来并写进文档**（本轮 45 页入链 `1388–1812` → **`98–300`**，零孤岛）。
99. **★ 「只改一个模板的一个区域」也能逐字节归属，不必跑第二次全量渲染（2026-10-10 第七十九轮）** —— 判据：**把新产物里被改动的区域还原成改动前的渲染形态**，整页 sha256 应等于上一轮基线。本轮 **1291 / 1291 页全部相等** ⇒ 一次 6 秒的脚本就完成了「改动零外溢」的证明，并顺带把「未变的那 1 页」锁定为无 `<nav>` 的 meta-refresh 别名壳。
    ★ **前提**：还原所需的文案、顺序、品牌名**必须从真源读**（`data/providers.toml` 的字母序两两组合 + `i18n/*.toml`），**不能手抄** —— 否则「相等」只证明我抄对了，不证明产物没变。
    ★ **用法**：与 `verify_no_regression.py --diff` **互为交叉验证**（本轮两边都给「变更 1290 / 新增 0 / 删除 0 / 未变 1」）。★ 手写还原时必须**自己写 `<div>` 深度配平**来取区域边界，不能靠正则。
100. **☠ 「结构边界」也可能是错的边界 —— 要选「包住目标的那一层」（2026-10-10 第七十九轮）** —— 红线 97 说「区域切分只用结构边界」，本轮立刻踩了它的变形：切 Versus 面板时用「面板起点 → 本段 `</nav>`」，但 Versus 后面**还挂着 Tools / eSIM deals / Guides（自带大菜单）/ Network map / Research**，`</nav>` 落在很下方 ⇒ 切出来的「面板」里混进半个导航，**数字判据被别的面板污染**（数出 `0`、`26` 这类 **class 属性里的数字**：`w-[26rem]`、`calc(100vh-7rem)`、`brand-700`）。
    ★ **纪律**：① 结构边界要**闭合到与目标同层**（面板 → 配平的 `</div>`；表格 → `</tbody>`；列表 → `</ol>`）；② 切完**先打一眼区域长度与内容**再写判据；③ **判据只吃可见文本** —— 数字类判据必须先 `re.sub(r'<[^>]*>', ' ', region)` 剥掉标签，否则 CSS class 里的数字会被算成「页面上的数字」。
101. **☠ 「线上有问题」必须先分成『本地产物』与『已部署产物』两侧再判（2026-10-10 第八十轮）** —— 用户报「`/de/sitemap.xml` 里没有德语页 / `robots.txt` 缺 `de/sitemap.xml` / footer 与 header 大量链接没有 `/de/`」。本地逐条扫：`public/de/sitemap.xml` **644 条**、`robots.txt` **2 行 `Sitemap:`**、德语页越界链接 **0**（除语言切换器）——**本地全绿**。真因是 **HEAD 里的德语站只有 55 个文件**（54 个 `noindex`），而工作区 644 个 ⇒ **线上跑的是「德语只有首页」的旧形态**。
    ★ **判据顺序**：① 线上原文**先落盘**（`curl -o`），② 与本地产物**逐条对照**，③ 再查 `git ls-tree -r HEAD -- content/…` 的规模。跳过第 ③ 步就会在一个**根本没坏**的模板上改半天。
    ★ **伴生坑**：`curl -s … | grep -c` 遇到连接抖动会**静默截断下载**（本轮把 644 条读成 386 条，差点据此下结论）⇒ **取线上数据一律先 `-o` 落盘、`stat` 校验大小，再统计**。
    ★ **推论**：本地守卫再绿也证明不了线上 —— 两端唯一的桥是「提交」，所以「线上对不对」这件事**只能靠部署后复核**（本轮给出 4 条 `curl` 复核命令）。
102. **☠ `lang-href.html` 三层兜底的代价：缺页时它静默退化成**英语 URL（语言泄漏），而不是 404（2026-10-10 第八十轮）** —— 层 2「别的语言有该页 → 返回**那个语言**的 `.RelPermalink`」在半翻译状态下会产出**没有 `/de/` 前缀的链接**。于是「德语侧缺一页」**不报错、不 404**，只是把德语读者丢进英语页 —— 这正是用户看到「footer/header 大量链接没有 `/de/`」的机制（线上德语站只有首页有内容 ⇒ 30 条链接退化；本地 644 页齐全 ⇒ 越界 0）。
    ★ **硬不变量**：`content/en` 与 `content/de` 的**页面型**文件数必须 **1:1**（当前 636 : 636）。任一侧出现差额，**先当成缺陷查，不要用兜底掩盖**。







| 事项 | 影响 |
|---|---|
| ~~真实折扣码~~ | ✅ 2026-10-01 完成（3 家有码 5 家无码，见 providers.toml；仅 promo_expires 需上线前复核） |
| ~~品牌 logo~~ | ✅ 2026-10-07 全 **10 家**接入（`static/img/providers/` 下 7 png + 3 webp，含 Nomad 与 Jetpac）。★ **生效目录是 `static/img/providers/`**，素材放 `static/img/logo/` 不生效；且只认 **png/webp**（jpg 探测不到） |
| **联盟深链格式确认**（每家国家级 URL 规则） | hugo.toml country_path + countries.toml slugs；影响转化归因 |
| **Roami 定价决策** | ⚠ 业务发现：数据算出 **Roamic 在 35/50 国比自家 Roami 便宜**（Roami 只赢 15 国）—— roami-vs-roamic 对决页如实展示了这个结论；要么调价要么接受 |
| ~~networks 逐品牌官方数据来源确认~~ | ✅ 2026-10-02 按"同国同运营商"规则用 `countries.toml.carriers` 补全，无需逐品牌查（见 §4.3） |
| **哪些数据源该驱动页面日期？** | 目前只有 `plans`（价格）与 `providers`（品牌档案）驱动日期。`countries.toml`（国家 hub 正文）/ `carriers.toml` / `refs.toml` / `faqs/<iso>.toml` / `titlesegments.toml` 改了**不会**动任何日期 —— 因为那些页面**现在压根没印日期**。要让它们也驱动，得先定「日期印在哪儿、印给谁看」（见 §4.3 的「不驱动日期的数据源」） |
| **剩余品牌的 logo 归位** | 素材已在 `static/img/logo/`：`gigsky.png` ✓ / ~~`jetpac.webp`~~ ✅ 2026-10-07 已归位到 `providers/` / `bensim.jpg` ✗（BNESIM 拼写为 `bnesim`，且 **jpg 探测不到**，接入时须转 png 或 webp 并改名） |
| **`gen_provider_pages.py` 不清理陈旧对决页** | 删品牌时残留的 `content/en/compare/*-vs-*.md` 会让 hugo **构建失败**（`ERROR compare/vs-single: unknown provider` → nil pointer），而子页会被 `removed` 计数自动清掉。修法：给生成器加一段对称的清理（或删品牌前先手工清 `*-vs-*` 里引用了该品牌的文件），见 §14 红线 53 |

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

---

## 18. 多语言（i18n）基础设施 —— 新增一个语言怎么走

> 2026-10-03 第十四轮完成基础设施改造。**当前仍只有英文**，英文产物与改造前逐字节一致（除红线 38 记录的 18 页纯空白差异）。

### 18.1 已就位的东西

| 位置 | 作用 |
|:---|:---|
| `hugo.toml` `[languages.en]` + `defaultContentLanguageInSubdir = false` | 英文留在根路径，539 个已收录 URL 零变更；新语言落 `public/<lang>/` |
| `i18n/en.toml`（749 key） | 模板层文案单表。key 命名：跨文件复用 → `g_<slug>`；文件独有 → `<filetag>__<slug>` |
| `layouts/partials/i18n-data.html` | 数据层按语言解析。英语下**直接返回 `hugo.Data`（零开销恒等）**；存在 `data/<lang>/` 时深合并覆盖 |
| `data/<lang>/…` 约定 | 与 `data/` 同路径的覆盖文件，只写需要翻译的键（如 `data/ja/countries.toml` 只写 `name` / `quirks`） |
| `scripts/lang_rules.py` | 语言规则单一事实源：产物目录前缀、标题是否允许破折号（原「哪些语言用拉丁字母」一栏随非拉丁禁令一并删除，见 §18.4） |
| `scripts/i18n_extract.py` | 模板文案抽取器（幂等、行尾保真、内置 CRLF 预检） |
| `scripts/check_i18n.py` | 守卫：模板层不得新增硬编码；各语言 key 必须与 `en.toml` 对齐 |
| `layouts/partials/head.html` | `hreflang` + `og:locale`，**仅在 `len hugo.Sites > 1` 时输出**，单语言下零字节 |

### 18.2 新增语言三步

```toml
# 1) hugo.toml 追加（contentDir 必须显式写，不写会静默并入默认语言）
[languages.ja]
  languageCode = "ja-jp"
  languageName = "日本語"
  contentDir  = "content/ja"
  weight      = 2
```
2) 建 `content/ja/`（长文）与 `i18n/ja.toml`（键名与 `i18n/en.toml` 一一对齐 —— 漏一个 `check_i18n.py` 直接失败）
3) 需要覆盖数据层散文时建 `data/ja/…`，路径与 `data/` 对齐

```bash
npm run build          # 已含 check_i18n + check_headings
```
另需确认：`scripts/lang_rules.py` 的 `DASH_OK` 是否包含该语言（决定标题里的 `—`/`–` 是否放行）。**不再需要确认字符脚本** —— 非拉丁禁令已于 2026-10-03 删除（见 §18.4），加日语/中文/韩语不会再被任何守卫拦住。

### 18.3 本轮未完成（新增语言前必须补）

| 项 | 说明 |
|:---|:---|
| **704 处拼装句碎片** | `scripts/check_i18n.py` 会报。它们是紧邻 `{{ }}` 的句子片段（如 `Real prepaid plans from`），**多语言必须整体重写成带命名占位符的整句**（德语/日语语序不同，碎片拼接必崩），不能逐片翻译 |
| **5 处内联 `<script>` 文案** | 改用 `data-*` 属性注入（见红线 37） |
| **语言切换器 UI** | header 里目前**没有**。建议落点在 `layouts/partials/header.html` 主 nav 右侧，用 `{{ if gt (len hugo.Sites) 1 }}` 门控 + `range .AllTranslations` 出链接，class 复用现有 `nav` token；**必须在第二个语言上真机看过再上线** |
| **JSON-LD `inLanguage`** | `schema.html` / `schema-org.html` 尚未加 |
| **141 处 `printf` 生成整句** | 多语言后需要 3×N 套措辞（`esim-providers/single.html` 一个文件占 46 条） |
| **`data/plans` 的 `fup_note` / `name`** | 2684 条仅 6 种模式、7776 条仅 2 个主模式 —— 应当**改造成模板渲染而不是翻译**（一次省 10460 条） |

### 18.4 语言相关的校验豁免机制（2026-10-03 晚已收窄）

**原来的「非拉丁字符禁令」已整体删除**，原因：站点要上多语言，而 ja/ko/zh 的合法产物天然含非拉丁字符。当时的两条路是（a）按语言划豁免前缀、（b）删掉禁令 —— 选了 (b)，因为 (a) 只是把同一个问题往后推，还要维护一张 `LATIN_SCRIPT` 语言表。

删除范围（三处，全部已落地）：
- `check_output.py` ④ 产物层非拉丁扫描 + 其 `.json` 分支 → 删。顺手把 ① 的 Go 格式串扫描**扩展到 `.json`**，避免 json 分支变成死代码
- `validate.py` §3 的 plan name 非拉丁检查 → 删。**保留**与语言无关的结构性校验（首尾空白、首字符是标点）
- `lang_rules.py` 的 `LATIN_SCRIPT` / `non_latin_exempt_prefixes()` / `non_latin_exempt_data_dirs()` → 删

**代价**：手动贴进 `data/plans/` 的非拉丁套餐名不再有任何守卫拦截。防线只剩抓取层 `toml_write.clean_plan_name()`（**重抓数据时**自动清洗并打印），所以红线 21 加了一句「新抓一批数据后人工看一眼打印输出」。

**仍然生效的豁免**：
- `check_headings.py` 在 `public/<非拉丁语言>/` 下放宽 `—`/`–`（`DASH_OK` 表；逗号/分号/冒号**仍全语言禁止**）
- `lang_rules.py` 未启用的语言不出现在任何豁免集合里 → 单语言时校验行为与改造前一致

---

