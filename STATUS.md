# eSIM Sift — 项目状态

> 独立 eSIM 比价站。单一数据源（`data/*.toml`），模板层推导一切派生指标。
> 基座：Hugo 0.159.1 + Tailwind CLI。语言：英语（目录结构已为多语言预留）。

## 命令

```bash
npm run build     # Tailwind CSS → 数据校验 + CSS 同步校验 → hugo → 产物校验（上线前的完整管线）
npm run dev       # Tailwind 预编译 + hugo server
npm run validate  # 单独跑校验（validate.py + check_css_sync.py）
npm run check:output # 产物校验（格式串泄漏 / JSON-LD 可解析 / 评分区间）——必须在 hugo 之后跑
npm run build:css # 只重建 Tailwind（改过 layouts 里的 class 后必须跑）
```

⚠️ **不要用裸 `hugo` 代替 `npm run build`。** `hugo` 只把 `static/css/tailwind.css` 拷进 `public/`，
**不会重编译 Tailwind**；改了模板里的 class 而不重建 CSS，新类就没有规则，页面上样式静默失效。

## 数据流（唯一事实源原则）

```
data/countries.toml   国家：name/slug/flag/neighbors/carriers/quirks/[ISO.slugs]
data/providers.toml   品牌：strengths/weaknesses/tagline
data/plans/<brand>.toml   每品牌×国家价格：[ISO] + [[ISO.plans]]（checked/networks/name/gb/days/type/price/fup_note）
data/faqs/<iso>.toml  国家 FAQ（[[faq]] q/a，比较角度）

layouts/partials/country-stats.html  ← 全站唯一聚合入口
  产出 rows/perDay/perGB/minPrice/minPerGB/maxGB/unlimitedCount/checkedDate
  徽章（Cheapest/Best value/Most data）= 排序字面位置，非人工编辑
```

## 出站流量（单一控制点）

`hugo.toml [params.outbound]`：`active = "roami"` 指定默认导流目标；换目标只改这一行。
- Roami（自家）`rel = ""` → follow，深链 `/{slug}/` 取自 `countries.toml [ISO.slugs.roami]`
- 第三方（airalo/holafly/saily/nomad）`rel = "sponsored nofollow"`
- 全站出口只有 `partials/cta-out.html` 一个；UTM 自动追加，页面级 campaign = `compare-<country>`

## 关键防坑（本项目已踩实）

1. **JSON-LD 必须 `| safeJS`**：Hugo 0.146+ 新模板引擎会把 script 内的 jsonify 输出二次编码成字符串
2. **禁止 PowerShell 批量替换模板**：PS 5.1 会把无 BOM UTF-8 按 GBK 读写，中文注释/箭头变乱码且吞 `<`；只用 Edit/Write 工具
3. **`[[faq]]` TOML 顶层数组包在 `faq` 键下**：取值要 `.faq`
4. **`site.Data` 已弃用**：一律 `hugo.Data`（`site.Params`/`site.GetPage` 不受影响）
5. md 正文禁止内联 JSON-LD（沿用 Roami 的 --minify 教训），结构化数据全在模板层
6. **改过 `layouts/` 里的 class 必须重建 CSS**（2026-10-03 版式塌陷事故）：Tailwind CLI 产出的
   `static/css/tailwind.css` 是独立产物，裸 `hugo` 不会更新它；JIT 对未知类**静默忽略不报错**，
   后果是「HTML 结构对、样式全无」。一律 `npm run build`，并靠 `scripts/check_css_sync.py` 兜底
7. **新增模板 class 后，用预览服务核对 CSS 真的送到了浏览器**：`curl -s http://127.0.0.1:1313/css/tailwind.css | grep <类名>`，
   只看源码通过不算通过
8. **Go 格式串错误只有 `public/` 里看得见**（2026-10-03 事故）：`math.Round` 返回 **float64**，喂 `%d` 前必须 `int` 强转；
   printf 里的**字面百分号要写 `%%`**；有 `%s` 就得给够参数、没占位符就别传参数。违反任一条都会把
   `%!d(float64=84)%` / `%!m(MISSING)` / `%!(EXTRA string=…)` 直接印在正文里（还进 JSON-LD FAQ），而 `hugo` 全程 exit 0。
   一律跑 `scripts/check_output.py` 兜底
9. **`itemReviewed` 是 Organization/LocalBusiness 时，评分必须来自真实用户**（2026-10-03 GSC 事故）：编辑部按价格库
   算出的指数**不能**当 `reviewRating`（Google 明文禁止「依賴人工編輯編制評分資訊」）。想携带这类指数用
   `additionalProperty`（`PropertyValue`）；`offers.lowPrice/highPrice/offerCount` 必须是 **JSON 数字**不是字符串。
   一律跑 `scripts/check_output.py` 兜底

## 已完成（本轮）

- ✅ 设计系统全面升级：自定义 ink/brand/accent 色板 + Sora/Inter 字体 + 组件层（btn/card/badge/chip/table-pro/faq-item/figure），重写全部布局（首页 hero-mesh + 区域筛选 + 3 步引导 / compare 列表 / 13 模块国家 hub / providers 品牌头像 / header 下拉 / footer / 404）
- ✅ 50 国数据落地（`scripts/gen_sample_data.py`，确定性生成，重跑结果一致）：
  - `countries.toml` 50 国（region 与筛选 chip 精确匹配 "Asia"/"Europe"/"Americas"/"Africa & Middle East"/"Oceania"；JP quirks/slug 原样保留；每国 4 张配图清单）
  - 5 品牌 × 50 国价格（区域价格系数 0.72–1.45；JP-Roami 全 19 档为真实价格；Holafly 纯 unlimited 按天计价模型 + fup_note）
  - 49 个 compare 页（iso + seo.description + 3 段数据驱动分析，措辞按 hash 轮换）+ 49 个 FAQ 文件（6 条对比角度，含计算数字）
  - 图片分发：200 张 `static/img/countries/<slug>-01..04.webp`（页面用 3 张 + og:image）+ `img/site/home-hero.webp`、`og-default.webp`，alt 均为 SEO 描述
- ✅ 77 页构建绿（5.9s）：llms.txt 50 国 / catalog.json 50 国机器可读 / sitemap 64 URL / 全部出站链接 rel 与 UTM 正确（roami 默认 follow，四家 sponsored nofollow，campaign=compare-<slug>）
- ✅ `scripts/validate.py`：6 类数据检查挂入 `npm run build`，坏数据进不了构建
- ✅ 品牌×国家子页（250 页）：`content/en/compare/<slug>/<provider>.md`（正文空，全由 `layouts/compare/provider.html` 推导）+ `gen_sample_data.py::write_provider_pages()`（描述数字直读 data/plans，JP 真实数据也正确）
- ✅ 区域大菜单（header）：热门列 + 5 区域块各自滚动，180+ 国无需改结构；修复 `.nav-dropdown` translate-y 悬停死角（`::before` 桥）
- ✅ 折扣码模块：`data/providers.toml` 加 `promo_code/promo_label/promo_expires`（⚠ SAMPLE）；`/esim-deals/` 专页（复制到剪贴板）+ 品牌卡/国家页/子页三处展示
- ✅ 品牌 logo 占位符方案：monogram 徽标（providers.toml color/initials 驱动）为占位符；`partials/prov-logo.html` 带 `fileExists` 检测，放 `static/img/providers/<key>.png` 即自动切真 logo，零配置
- ✅ 国家页排序/筛选：客户端 select（Best $/GB / Cheapest / Most data / Longest）+ 有效期 chips（7/14/30+ 天），data-* 驱动零依赖
- ✅ 区块重命名带 esim 核心词：`/deals/→/esim-deals/`、`/providers/→/esim-providers/`（footer 品牌列直达锚点 `/esim-providers/#<key>`）
- ✅ 全站出站 UTM 补齐：四家第三方 target 也加 `[utm]`（source=esimsift），campaign 覆盖 compare-<slug> / prov-<pk>-<slug> / esim-deals
- ✅ 子页独立 4 级面包屑 + BreadcrumbList JSON-LD（`schema.html` 加 `.Params.provider` 分支，`.Ancestors` 不含普通页国家层）
- ✅ 修复国家列表污染：provider 子页属 compare 段普通页，会进 `.Pages`；全站 `where .Pages "Params.provider" nil` 过滤（list/index/header/footer 四处）

## 已完成（品牌详情页 & 框架自审，本轮）

- ✅ 品牌详情页（5 页 `/esim-providers/<key>/`）：`layouts/esim-providers/single.html` + 5 个 content md。全部数字由新 partial `provider-agg.html` 聚合（countries/minPrice/minPerGB/cheapest 命中数/bestValue/覆盖切片）。页内含：计算式结论（"cheapest in N of M"）、透明价格竞争力评分、优劣势 + 套餐形态、按区域分组的覆盖清单（替代 50 国超链接堆砌）、对手对比、数据驱动 FAQ。
- ✅ schema 升级：品牌页 `@graph` = Product(AggregateOffer 含 highPrice) + Review(editorial 评分) + FAQPage；对标 mybestsim 的 Review/Rating/AggregateRating（我们不做假评分，用"最便宜命中率"透明口径）。
- ✅ `/esim-providers/` 列表页重写：品牌卡可点击 → 详情页；"Compared in" 墙改为 "Cheapest in N / best $/GB in M" 摘要 + "Read full review →"。
- ✅ tools 页：单一推荐（Our pick）+ 内部跳转 `See {brand} {country} plans`（→品牌×国家子页）/ `Read {brand} review`（→品牌详情）；"All matching plans" 长列表折叠为 Top3 + "Compare all N →"。
- ✅ 锚文本 SEO：表格裸 "View" → "View plan"；TL;DR "View deal" → "View {brand} deal"；品牌卡/子页补 "Read {brand} review / Full review" 内链。
- ✅ 国家页 UX：表格斑马纹（nth-child）+ 移动网络区块（逐国唯一 networks 徽章，反同质化）。
- ✅ footer/llms.txt 品牌链接 `/esim-providers/#<key>` → `/esim-providers/<key>/`（真详情页）。

## 已完成（国家页搜索意图扩展 & 全站长尾审计，本轮）

- ✅ 表格斑马纹修复（用户反馈）：旧实现 even 行 `rgba(245,247,250,.4)` 几乎不可见、hover 为绿色底洗白（价格/天数看不清）。改为实色 ink-50 斑马（无需交互即可见）+ 中性 hover ink-100 + 品牌 teal 左轨（box-shadow inset），文字对比度不受影响。
- ✅ 国家页新增「怎么选」（⑤b）：数据用量分档（1GB/5GB/10GB+/∞，各档给出实时最便宜套餐名+价格）+ 三步安装激活（按 app/marketplace 差异化措辞）；对标 mybestsim 的 How to Choose / How to Install 且全部挂钩本页数据。
- ✅ 国家页新增「按人群 × 按时长」（⑤c）：4 时长档（3-5/7-10/14/30+ 天，days≥档、gb≥用量、unlimited 视为满足）+ 4 人群（轻量/标准游客/流媒体热点/远程办公），每个推荐都是排序字面位置并给出口径说明，链接到品牌×国家子页 —— 8 张卡 × 49 国 = 长尾矩阵，零手工维护。
- ✅ 网络区升级（⑦b）：徽章墙 → 「每个网络谁在用」（network→providers 反向索引）+ 当地运营商市场对照（eSIM-ready / not on tracked eSIMs 徽章）；运营商信息密度超过竞品。
- ✅ 品牌页补齐对标 review-roamic：「How {brand} works」（app/marketplace 两套三步）+「Company snapshot」（成立/模式/国家数/套餐数/价格区间/关系披露）+「Where cheapest — and priciest」（入口价排序 top3 双列，链接国家页）。
- ✅ 长尾审计（全页型 H1-H3 + title + FAQ 问句）：国家页 6 条 FAQ 覆盖 cheapest/unlimited/品牌对选/ID/网络/多国；title 已含 "Best eSIM for {Country}"；补 TL;DR 引言落 "best {country} eSIM" 正文短语（title-正文呼应）；keyword 标题数每页 ≤6 未超标。
- ⏭ 长尾补充方向（数据阶段再做，防蚕食）：区域卡页（Europe/Asia eSIM）、"{country} SIM card vs eSIM" 文章型、品牌 vs 品牌专题页、季节/事件长尾。

## 已完成（蓝图 Phase 1 · 步骤 1–2：keyword-map + VS 对决页，本轮）

- ✅ `docs/keyword-map.md`：关键词→URL 唯一映射表（15+ 词簇归属、国家/全局语境判定规则、Phase 2 预留槽位、validate 检查清单）——侧翼页型的蚕食治理前置门。
- ✅ **/vs/ 10 组品牌对决页全量上线**（构建 342 页，+10）：
  - `partials/vs-agg.html`：配对聚合单一入口 —— 两国都卖的每个国家算各自最低价/最优 $/GB/unlimited 有无，逐国判胜（并列计 tie），汇总 win/tie/unlimited 计数
  - `layouts/vs/single.html`：verdict-first（胜者计数 + Pick A/B if 数据驱动分支）→ 50 国逐国表（国家列链国家页、价格列链品牌×国家子页）→ 结构差异卡 → 数据驱动 FAQ×6（含反向查询承接）→ sibling 对决互链 ×9 → trust 尾；FAQPage schema；CTA campaign=vs-{a}-{b}
  - `layouts/vs/list.html`：枢纽页 10 卡，每卡实时算胜者摘要（含并列呈现）
  - content ×10：slug 字母序（`{a}-vs-{b}`），标题双模板/描述三框架轮换防同质化
  - 并列显式呈现：SAMPLE 数据下 roami-vs-saily 49 国同价、airalo-vs-nomad 34 国同价 —— stat tile「identical prices」+ verdict 副句 + 枢纽卡「Identical prices in N」（真数据后自然消散）
- ✅ 品牌页「vs the field」卡重构：每对手加 `{self} vs {rival} →` 对决页精确锚文本内链
- ✅ llms.txt 加 Provider matchups 段（10 组，含 win/tie/unlimited 计数）+ 站点区导航加 /vs/
- ✅ 验证：sitemap 11 个 /vs/ URL；50 行表格 + 双方子页链接各 50；Holafly 全 unlimited-only → $/GB 列 50 格正确落「unlimited only」

## 已完成（蓝图 Phase 1 · 步骤 3–6：research + guides + 联动 + 校验，本轮）

- ✅ **步骤 3 `/research/` 3 页上线**（全部从 plans 数据实时推导，零手工数字）：
  - `esim-price-index`：50 国 $/GB 联赛表（每行链国家页）+ 中位数/最贵最便宜 5 极值卡 + 五大区域均价排行
  - `unlimited-esim`：unlimited 日费率榜（perDay 排序，最便宜 $0.93/天）+ 计费方式 3 卡 + 逐国最优 provider
  - `fair-use-audit`：逐 provider FUP 透明度审计（fup_note 原文引用 + distinct 变体计数 + transparent/unstated/not applicable 徽章）
  - `layouts/research/list.html` 枢纽页 + `single.html` 按 `layout:` 参数分发三个专属模板
- ✅ **步骤 4 `/guides/` 5 篇上线**（~500–700 词/篇，用户意图 H2，事实性表述留 hedge）：what-is-an-esim / how-to-install-esim / esim-vs-physical-sim / dual-sim-and-esim / esim-compatibility-check（含 `*#06#` EID 30 秒检测法）。内链纪律：每篇链 /compare/ + 恰好 3 个国家页（跨篇轮换国家）+ /esim-providers/ + 相关 /research/ + 篇间互链
- ✅ **步骤 5 联动**：footer 新增「Popular matchups」列（编辑挑选 6 组，page 缺失静默跳过）+「Data & research」列（3 页短锚文本）；grid 升 md:4 / lg:7；header 桌面加 "Versus" + 移动加 "VS" chip
- ✅ **步骤 6 validate.py 增检（第 7 组）**：vs 页 providers 必须恰好 2 个有效品牌、字母序、filename==`{a}-vs-{b}.md`（坏数据进不了 hugo，layout errorf 只是兜底）
- ✅ llms.txt 补 Data & research + Guides 两段（htmlUnescape 处理引号实体；fair-use-audit 标题改用弯引号从源头规避 Go 模板 `&#34;` 转义）
- ✅ 构建 350 页 0 error（+5 guides）；sitemap 337 URL 全含 /vs/ ×11、/research/ ×4、/guides/ ×6；两个 hub 列出全部子页
- ⏭ 步骤 6 其余两项（锚文本分布统计工具、空壳区块 <3 不推广检查）归入 P-B 内容期 —— research/guides 已非空壳，锚文本统计在真实内容产出后做才有意义

## 已完成（对决页 URL 重构 /compare/ + 50 国运营商画像，本轮）

- ✅ **`/vs/{a}-vs-{b}/` → `/compare/{a}-vs-{b}/`**（用户要求，符合蓝图 §2 原设计；"vs" 泛目录无语义，并入 compare 语义簇）：
  - content ×10 迁至 `content/en/compare/{a}-vs-{b}.md` + `layout: vs-single`；模板迁至 `layouts/compare/vs-single.html`（layout 参数分发，同 research 页模式）；`content/en/vs/`、`layouts/vs/` 删除
  - **对决页与国家页同住 compare 段** → 全站 6 处国家列表过滤升为双层 `where (where .Pages "Params.provider" nil) "Params.providers" nil`（index / catalog / llms.txt / header / footer / compare list）
  - `/vs/` 枢纽页撤销，对决网格并入 `/compare/#matchups`（锚点 + scroll-mt）；header "Versus"/VS chip 与 footer "All matchups →" 全部指向该锚点
  - vs-single sibling 互链改为 providers 键枚举 C(n,2)（不再依赖 hub page）；品牌页 FAQ 内链、备选卡、llms.txt 10 组 URL 同步更新；CTA campaign `vs-{a}-{b}` 不变
  - validate.py：check 4 跳过 `-vs-` 文件、check 7 改新路径 + 增检 `layout: vs-single` 缺失（否则会错误落到国家模板）；keyword-map.md URL 列同步
  - 构建后需 `rm -rf public/vs`（hugo 不清理已删页面；或部署用 `--cleanDestinationDir`）
  - 验证：sitemap 10 个 `/compare/{a}-vs-{b}/`、0 个 `/vs/`；国家网格仍 50 卡；catalog.json 50 国；llms.txt 10 组新 URL；构建 348 页 0 error
- ✅ **carriers.toml 全 50 国补齐**（~154 profiles，validate.py 第 8 组 0 error）：50/50 国家页网络卡渲染「Typical X–Y Mbps — enough for …」（"能干什么"档位由 speed_min 模板推导）+ 覆盖特性 note + 速度口径免责声明（仅在有画像的国显示）

## 已完成（品牌集 8 家定稿 + 真实数据抓取管线，本轮）

- ✅ **品牌集换血（用户 2026-09-30 定稿）**：airalo / holafly / saily / yesim / ubigi / roamic / alosim + 自家 roami（roami ≠ roamic，两个不同品牌）；nomad 全量退场：
  - `data/providers.toml` 8 家（新 4 家事实已核实：Yesim 2019 瑞士 / Ubigi=Transatel 品牌 2017·NTT 2019 / Roamic=Byte Travel 西班牙 2021 / aloSIM=AffinityClick 渥太华 2021）
  - nomad：plans/sub页/品牌页/4 个对决 md/出站 target/footer 对 全部清除
  - 对决页 C(8,2)=28：22 新增（标题 3 框架 + 描述 4 框架轮换；roami-vs-roamic 特化标题点明"两个不同品牌"）；footer 热门对换为含 airalo-vs-yesim、roami-vs-roamic
  - 出站 `[params.outbound.targets]` 新 4 家（yesim.app / ubigi.com / roamic.com / alosim.com，sponsored nofollow）
  - 品牌详情页 md ×4 新增（nomad 删除）
- ✅ **真实数据抓取管线（`scripts/scrape/`）**：
  - **esimdb.com 有 AWS WAF**：curl 全被拦（405 + JS challenge）；**本机 Playwright chromium 可稳定穿透**（真实浏览器自动解 challenge，一次会话 50 国连抓）
  - `scrape_esimdb.py <provider>...`：Single-country tab 过滤（区域套餐不入库）→ 逐卡提取名称/流量/天数/价格/badges → `raw/<provider>/<our-slug>.json`（断点续跑、404/空页记录）
  - 国家 slug 映射 50/50（30 直同 + 20 探测验证：usa/uk/macau/turkey/uae/czechia…；costa-rica、fiji 首轮漏映射已补）
  - `toml_write.py <provider>`：raw → `data/plans/*.toml`；**无限套餐识别规则：限速信息在 badge（"+ ∞ at 1Mbps"）而非流量列** —— data="3GB/day"+∞badge → unlimited+fup_note；"1GB/Day" 无 badge → 日额型 data，gb=日额×天数（保住 $/GB 口径）
  - `verify_airalo.py`：对照 airalo.com 官网三个 tab（Data/Calls/Texts、Fixed data、Unlimited）多元组校验 —— **JP/IT/US 三国全档价格逐档一致**（"差异"均为 Change+/Discover+ 通话档与数据档同 (gb,days) 的键碰撞，属正常分层定价）
  - **airalo 50/50（985 套餐）、saily 50/50（471 套餐）已入库**，validate 0 error，无 SAMPLE 警告
  - `gen_provider_pages.py`：只重建品牌×国家子页（绝不碰 plans/*.toml）—— **gen_sample_data.py 从此禁止整跑**（会用 SAMPLE 覆盖真实数据）
  - `networks = []`：esimdb 卡片不展示网络名；国家页 ⑦b 区块自动隐藏（len 门控），表格网络列显示 —；后续可从各品牌官网补（airalo.com 国家页有 "T-Mobile +1 other"）
  - **Holafly 不在 esimdb（/usa/holafly 404）** → `scrape_holafly.py` 直接抓官网 PDP：`esim.holafly.com/esim-{country}/` 的 `pdp-table`（天数×USD 价全表）+ JSON-LD Product 描述提 FUP（Always On 1GB/月备份）；Yoast sitemap 不含 PDP，slug 用候选探测（turkey/czech-republic/macau 变体已备）
- ⏭ 抓取队列：yesim/ubigi/roamic/alosim（esimdb）→ holafly（官网）→ roami 49 国（用户自有数据/roamiapp.com，JP 已真实）

## 已完成（蓝图复核两轮 + 运营商专业化，本轮）

- ✅ **国家页运营商画像**（用户需求：速度 + 用户视角"能干什么"）：新数据层 `data/carriers.toml`（join key=name 对齐 countries.carriers 与 plans.networks；speed_min/speed_top=典型实测区间；IT/JP 手写样例，其余 48 国 P-A 补）；网络卡升级为 name+tech 徽章+「Typical X–Y Mbps — enough for 4K streaming…」（"能干什么"由 speed_min 模板推导：≥25=4K 档/≥10=HD 档/≥5=基础档，不手写）+ 覆盖特性 note；无数据国自动退回纯归属卡；validate.py 第 8 组校验（join key/tech 枚举/速度区间）
- ✅ **蓝图复核第 1 轮（模板/代码层）发现并修复 2 处遗漏**：
  - 品牌页 FAQ 精确匹配 "{A} vs {B}: which is cheaper?" 与 /vs/ 抢词（报告 §5 明令防止）→ 改非精确问法 "How does {A} compare with {B}?" + 答案内链对决页（FAQ body 改 safeHTML）
  - Research 无 header 导航入口（报告 §3"并入 Guides 或独立"）→ Guides 升级下拉（Basics & how-to 5 篇 + Data & research 3 篇，nav-mega 复用+right-0 锚定），顶层保持 6 项；移动端加 Research chip
- ✅ **第 2 轮（重读报告原文 → 渲染产物核销）**：keyword-map ✓；VS 页 50 子页链接/反向查询承接/sibling×9/FAQPage+BreadcrumbList ✓；research 50 行国家链接+核查日期 ✓；5 篇指南正文恰好各 3 条国家链接（修复 dual-sim 仅 2 条）+ 轮换 ✓；品牌页 vs 区块 ✓；footer 32 链接 ≤130 红线 ✓；不采纳项合规（无 AggregateRating/无 /city//无 /use-cases/）✓；schema 全页 BreadcrumbList ✓
- ⏭ 报告唯一未落项：validate.py 锚文本比例静态检查（完全匹配 ≤20%）——归 P-B（真实内容产出后统计才有意义，已在 P-B 备注）

## 已完成（8 品牌真实数据收官 + 国家页 UX 五修，本轮）

- ✅ **抓取队列全部完成**：roamic 1791 / alosim 915（esimdb）；holafly 298（**官网 PDP 直抓**，UAE=esim-dubai slug；FUP "Always On" 透传到 fup_note）。8/8 品牌 50/50，validate 0 error 0 warning（SAMPLE 清零），构建 519 页 / 507 URL / 400 子页 / 28 对决。
- ✅ **Ubigi 订阅建模**：esimdb 的 Monthly/Yearly（"5GB/month $8/mo"、年付月额×12）→ days=30/365、gb=月额（年付=×12）、订阅性质进 fup_note；首版丢 80 条已全恢复（483 条）。
- ✅ **roamic 1 天卡规则**：esimdb 把 1 天 unlimited 显示为固定量 "3GB"，但名字带 Unlimited + ∞ 徽章 → 判 unlimited（全品牌徽章扫描验证：限速徽章必含 ∞，无误判源）。
- ✅ **整数价格 bug（用户报告 %!f(int64=4)）**：TOML `price = 4` 是 int64，Hugo `printf "%.2f"` 崩 → toml_write.py 永远写两位小数 float，8 品牌 17 文件重转，全站 0 处 `%!f`。
- ✅ **国家页 UX 五修（用户反馈 localhost 实测）**：
  1. TL;DR 三卡 CTA 站外 → 站内品牌×国家子页按钮（出口仍在表格 View 列，漏斗保留）
  2. 主表新增品牌多选 chips（全关=全开兜底）+ "Unlimited only" 开关（同套 data-* 管线）
  3. ⑥ 品牌名+logo 可点 → /esim-providers/<key>/
  4. ⑦b 运营商区脱离 plan networks 依赖：**networks=[] 曾把整块隐藏（carriers.toml 154 条画像根本没渲染）** → 改为从 carriers.toml 直渲染全部本地运营商
  5. 运营商信息增量：`[ISO.info] cities`（50 国主要城市条 "every national network covers"）+ `[[ISO.info.detail]]` 逐运营商 strong/weak（18 个关键市场 54 条，append_carrier_info.py 幂等）；其余 32 国 detail 待补（P-A）
- ⚠ 长尾提示：蓝图明确不建城市页（薄页风险），城市名仅进国家页运营商区（仍可承接 "verizon coverage rural" 类查询的页面内命中）。

## 已完成（research 页钻取内链/增益升级 + 对决枢纽页恢复，本轮）

- ✅ **research 三页"纯数据展示"问题修复（用户反馈：数据不可点、无决策增益）**：
  - price-index 联赛表新增 **Winning plan 列**（套餐名链品牌×国家子页 + 品牌名链品牌详情页，50 行钻取）；extremes 卡补 provider 名；**区域卡从死数字升级为区域内全部国家的可点 chips**（按 $/GB 排序，50 国全链）
  - price-index 新增**计算洞察区**「What the price spread means」：最便宜/最贵 ×倍数、$10 购买力对比、区域价差 ×倍数（3 卡全部带国家内链）
  - unlimited 表品牌名/套餐名双钻取（100 个子页链）；新增**盈亏平衡区**「When is unlimited cheaper than metered」：be = 最优日费 ÷ 最优 $/GB，逐国计算 → median 1.1 GB/天 + 最易赢/最难赢市场（带内链 + FUP 免责尾注）
  - 三页各加**数据驱动 FAQ ×3-4 + FAQPage schema**（研究页此前无 FAQ schema；答案数字全部实时计算，改数据自动刷新）；fair-use 的透明/部分/未声明品牌名单计算进 FAQ 答案
  - 三页各加 **Related research ×4 卡**（研究互链 + 对决枢纽 + 品牌列表）；fair-use md 描述里残留的 Nomad 修复
- ✅ **对决枢纽页 `/compare/matchups/` 恢复（用户反馈"品牌对比页怎么没了"）**：/vs/→/compare/ 重构时枢纽被并为 #matchups 锚点、入口太深 → 新建独立可收录枢纽页（`layout: matchups, nolist: true`）：28 卡全量网格 + **closest rivalry / most lopsided 计算瓦片**（vs-agg 实时算 gap）+ 相关阅读；卡片按 providers.toml 键枚举，**新增品牌自动出现**；header Versus/VS、footer All matchups、llms.txt（导航 + matchups 段首）全部指向新页；`/compare/` 网格改为编辑精选 6 组 + "All matchups →" 按钮（避免与枢纽页整页重复）
- ✅ **全站国家列表过滤双层→三层**：`where … "Params.provider" nil … "Params.providers" nil … "Params.nolist" nil`，6 处（index/catalog.json/llms.txt/header/footer/compare list）；validate.py check4 跳过 matchups.md；keyword-map.md 登记枢纽槽位（`eSIM provider comparison` 归枢纽，卡片不抢单对决头词）
- ✅ 构建 520 页 0 error / sitemap 508 URL（+hub）/ validate 0 error 0 warning / 全站 0 处 `%!f`；验证：hub 28 唯一对决卡、catalog 50 国未污染、region chips 50 国全链、unlimited 100 子页链



## 已完成（品牌档案扩充 + logo 接入 + 折扣码换真 + /esim-deals/ 重写，本轮）

- ✅ **品牌公司档案（8 家全量，三路并行代理在官方页面逐项核验 2026-10-01）**：`providers.toml` 每品牌新增 `[brand.info]` 子表（hq/legal/website/app_android/app_ios/support/support_email/response_time/refund/destinations）。要点：airalo=新加坡 AIRGSM / holafly=都柏林 Holafly Limited / saily=阿姆斯特丹 NordSec B.V. / yesim=楚格 GENESIS GROUP AG（唯一有响应时限承诺：平均 5 分钟）/ ubigi=巴黎 Transatel（无公开客服邮箱）/ roamic=巴塞罗那 Bytetravel S.A.（**两家商店都无 App → type 修正 app→marketplace**）/ alosim=渥太华 AffinityClick / roami=香港 Hong Kong LinZe Co., Limited（Play 无实际链接，仅 App Store 有）
- ✅ **品牌页模板升级**（single.html 6 处）：概况卡加总部/法人行 + 官网/双商店 chips（第三方官网带 sponsored nofollow）；新增③c 客服&退款专区（渠道/邮箱/响应承诺 + 退款摘要，info 缺失自动隐藏）；覆盖区"追踪 50 国≠品牌全部目的地"备注（destinations>50 才显示）；FAQ 加 "{brand} support"/"{brand} refund" 两条长尾；schema 加 Organization(sameAs=官网+商店)；降级壳页同步支持 HQ 行
- ✅ **logo 接入 8/8**：`static/img/logo/` 用户素材复制到 `static/img/providers/`（airalo/ubigi/yesim/roamic/roami/alosim=.png；holafly/saily=.webp）；prov-logo partial 扩展先探 .png 再探 .webp；全站 0 处 monogram 残留。修复一个自引入 bug：重构分支时占位徽标全站消失（$ext 永不为 "none"），重写为 else-if 探测
- ✅ **折扣码全换真**：roami `web20`（官网公示·新用户专享 20%，promo_label 按官方口径修正）/ saily `VEEPEE25`（官方合作页 saily.com/veepee/ 25%）/ ubigi `WELCOME10`（官方帮助中心 FAQ 首购 10%）；airalo/holafly/yesim/roamic/alosim 官方**无公开码**（仅推荐返利计划）→ promo 字段删除，模块全站自动隐藏。新增 promo_pct/promo_verified/promo_terms 三字段。⚠ promo_expires 均为占位 2027-12-31（官方未标过期日）
- ✅ **/esim-deals/ 全面重写**（对标 mybestsim.com/en/esim-discount-codes 且信息增益反超）：实码卡（核验日期+条款+**折扣后实际价实时计算**："最便宜的 Roami 套餐（奥地利）$1.99→$1.59 省 $0.40"）→ **"When a discount code still loses" 翻盘分析表**（逐国算折后价 vs 全场最低价，web20 让 roami 1→2/50 国登顶、VEEPEE25 让 saily 0→1、WELCOME10 让 ubigi 1→1——竞品无价格库做不出）→ 5 家无码品牌计算式替代价值卡（cheapest 命中数+入口价，不留空白）→ 5 步使用教程 → 4 条无码省钱路径（price-index/unlimited/compare/tools 全内链）→ FAQ×5（含"无码谁最便宜"计算式答案）+ FAQPage schema → 底部 8 品牌入口网格 + 4 相关页（对标竞品底部品牌入口并超出）。_index.md 标题/描述升级（2026 入标题）
- ✅ 构建验证：520 页 0 error / sitemap 508 URL / validate 0-0 / 全站 0 处 %!f / 8 品牌页新区块全部渲染（roamic 无商店 chips 正确）/ deals 页 3 实码 0 SAMPLE 残留 / 日本页 promo 模块只出 3 家实码

## 已完成（批次B收尾：tools 对标升级 / research hub 增益 / guides 5 篇重写 / sitemap 修复，本轮）

- ✅ **/tools/ 对标 mybestsim 数据计算器并反超**：竞品算完只给"你需要 X GB"（11 项活动码率表 + 0.5GB 取整 + 20% 余量）；我们闭环到真实价格库——新增「用量估算器」（8 项活动小时步进 → MB/天 → GB/天 → 行程总 GB，读取计算器天数滑杆 + 20% 余量开关，"Find the cheapest plan" 一键回填自定义 chip 并重选真实套餐）+ 「码率参考表」（H2 长尾 How much data each app uses per hour，11 行含 1GB 能买多少小时/照片，模板 $acts 单一来源喂 JS+表格）+ 底部双入口：12 热门国家卡（品牌覆盖数降序，实时最低价）+ 8 品牌卡（prov-logo + 覆盖国数 + 全球最低价及所在国）+ FAQ×3（小时数由码率实时计算）+ FAQPage schema
- ✅ **/research/ hub 信息增益**：原来只有 3 张卡+JSON 链接 → 全站计算瓦片（8776 套餐/50 国/8 品牌/中位 $/GB/最便宜 unlimited 国）+「The cheapest eSIM data in the world right now」实时 Top5 chips（France $0.30 … vs Kenya $1.65）+ 每张研究卡挂实时数据钩子（中位数/最便宜国/unlimited 日费率/审计计划数，按 RelPermalink 精确挂接，改数据自动刷新）+ 补标准容器 max-w-7xl
- ✅ **guides 5 篇全重写（信息增益+内链+长尾+搜索意图）**：新建 `layouts/guides/single.html` 专用模板——正文 + 逐篇**计算数据盒**（what-is→$/GB Top5 / vs-physical→入门价 Top5 / dual-sim→unlimited 日费率 Top5，指标互不重复防同质化）+ 品牌安装方式表（how-to-install 全表 / compatibility 仅 app 要求 5 家，providers.toml type 单一来源）+ front-matter faqs 渲染 FAQ 手风琴 + FAQPage schema 同源 + 相关阅读闭环（其余指南+tools+compare）；正文从 ~500 词扩到 1300–1550 词，H2 全部长尾问句（无冒号），每篇 3-4 条 PAA 型 FAQ；顺手修 _default/single 贴边渲染问题（guides 模板带 px-4）
- ✅ **sitemap 修复（用户反馈：删 changefreq/priority、必须有 lastmod）**：删 hugo.toml `[sitemap]` 块两字段 + 新建 `layouts/sitemap.xml`——**lastmod 三层解析**：①国家页/品牌×国家子页=该国价格快照日期（iso→country-stats）②编辑页=自身 date front matter ③其余数据驱动页=全站最新快照日；验证 508 URL=508 lastmod、changefreq/priority 归零、两层日期正确（快照 2026-09-30 / 今日编辑页 2026-10-01）；guides 5 篇+research 3 篇+tools 补 `date: 2026-10-01`
- ✅ **matchups 枢纽升级**（批次B-2）：28 张对决卡全部双 logo（prov-logo partial + vs 分隔 + 比分徽章 "AIRALO 37–12"/even）+ 首屏 figure（illustration-004）
- ✅ **全站断链修复**：`/research/price-index/` → `/research/esim-price-index/`（3 个模板预存 bug，build 后 grep 0 残留）
- ✅ 构建验证：520 页 0 error；sitemap 508/508 lastmod；guides 5 篇数据盒/schema/相关阅读全渲染；hub 钩子数字与 research 页同源一致（4175 unlimited 双页同值）

### 2026-10-01 批次C（标题规范 + 品牌胜负区重做）

- ✅ **全站标题规范落地（用户硬性规则：一句话、用户视角、无逗号/冒号/破折号碎片）**：渲染后 HTML 全量扫描 `<h2>/<h3>`，分 5 轮模板级修复共 **16+9+6 处源**——FAQ H2 全改用户问句（compare/single "What should I know before buying a {C} eSIM"、vs-single "Is {A} or {B} cheaper for your trip"、esim-providers FAQ H2 三版轮换、guides 5 篇 faq_heading 各自定制）；50 国 "Networks behind {C} eSIMs — and who rides them"→"Which networks do {C} eSIMs run on"；品牌×国家 "…: the caps"→"Is {B} unlimited data in {C} really unlimited"；matchups/deals/price-index/unlimited/fair-use/index 同风格修复；H3 "major cities — covered by"/"Refund policy, in short"/"Per day, not per GB" 等 9 处。**终扫 H2=0、H3=0**（唯一保留：/research/ 枢纽卡渲染的 3 篇文章主标题 "Title: Subtitle" 惯例，非分节标题）
- ✅ **品牌页胜负区重做（用户反馈：对比数据太敷衍、要增益信息+用户意图；8 品牌共用模板）**：`esim-providers/single.html` ④ 区从静态 strengths/weaknesses 三卡 → **全计算双向对比**：逐国重算 `{B}最低价 vs 全场次优价`（country-stats rows 排除自身），赢=省% / 输=溢价%，各取 Top5 带国旗/双价/徽章/国家页链接；intro 概括（严格最便宜 N/50 国、赢时平均省 X%、输时**中位数**差距——均值被 Holafly 类极端值拉爆故弃用）；>200% 溢价改 **×倍数**展示（"11×" 而非 "+978%"），unlimited-only 品牌（Holafly）加口径脚注（入口价=一整天数据 vs 对手小水桶）；Plan shape 卡增中位入门价；空态兜底（0 胜品牌引导 matchups / 0 负品牌给出一致性卖点）。验证：8 品牌全渲染（Yesim 42 胜 −83%×5 / Airalo 0 胜 Egypt $5.50 vs $0.51→11× / Holafly 23×+脚注），与 hero `$a.cheapest` 同源不矛盾（agg 含并列、intro 用"strictly"措辞）
- ✅ 同文件顺带修复：coverage H2 破折号 → "Where you can buy {B} eSIMs"、spread H2 → "Where {B} plans cost the least and the most"、眉标 "The verdict, computed"→"The computed verdict"

### 2026-10-01 批次D（六任务：披露删除 / VS 勾选器 / research 首屏 / guides 排名助推 / 设备兼容库 / 独立网络数据引用）

- ✅ **① 披露页删除同公司声明**：disclosure.md 重写，"Roami (roamiapp.com) 属于同一家公司" 表述移除，改为佣金模式 + 三条诚实规则 + 不做清单（渲染验证 0 残留）
- ✅ **② VS 对决页 "Other eSIM comparisons" 重做**（vs-single.html ⑥ 区）：勾选框选择器（8 品牌 logo 卡片，最多勾 2 个、第 3 个自动挤掉最早勾选、字母序拼 `/compare/{a}-vs-{b}/`、按钮文案实时更新、当前对预勾选）+ 28 张对决卡全部双 logo 开头；peer-checked 摆位坑（检查角标必须是隐藏 input 的直接兄弟）与内联 JS 禁 `{{` 坑均绕过
- ✅ **③ /research/unlimited-esim/ 首屏解挤**：11 个指标从 1.15fr hero 左栏挪出 → 全宽三卡条（最便宜国/覆盖数/盈亏平衡中位数）+ 单行品牌覆盖 chips（覆盖数降序，零填充 rank 串排序）
- ✅ **④ guides 排名助推**：50 国家页统一插「First time using an eSIM?」五卡板块（compare/single.html ⑨b，site.GetPage 取 5 篇）——每篇 50 条 sitewide 内链，锚文本按 `mod (len slug) 3` 三档轮换（如 what-is-an-esim ↔ "eSIM basics"/"what is an eSIM"/"eSIM explained"），每锚全站 ≤17 次不触 40+ 红线
- ✅ **⑤ 兼容设备库（对标 Holafly 列表并清洗）**：新 `data/devices.toml`（14 品牌组 351 机型 + 变体警告 9 组 + 明确不支持 12 条；来源=厂商规格×品牌兼容列表交叉核对 2026-10；去重 Reno/Find-X 重复条目、修正 Morotola 拼写）+ guides/single.html 键控交互块（搜索框 + 15 tab + 351 机型 chips + 品牌变体警示条 + JS 过滤零依赖）+ 不支持机型表；文章重写（iPhone 17/18/Air 与大陆/港版/韩版变体警告、EID 终审原则、新增"不在列表怎么办"FAQ，FAQ 共 5 条）
- ✅ **⑥ 独立网络数据引用（Opensignal/Ookla，45 国数据已核实）**：新 `data/networkreports.toml`（**文件名禁连字符**——`network-reports.toml` 的键带 `-` 无法点号取值，构建静默渲染空卡，已改名并记坑）+ compare/single.html ⑦b「Independent network data for {Country}」：Opensignal 事实卡（标题/月份/≤3 条获奖事实/原文链接）+ Ookla 引用卡（新闻式归属：获奖者+报告期+单数字+链接——**Ookla 页脚禁商业转载其数据，数值细节一律用 Opensignal**）+ Global Index 深链卡（50 国全覆盖；slug 覆盖 HK=`hong-kong-(sar)`/MO=`macau-(sar)`/TR=`t%C3%BCrkiye` 旧 slug 冻结 2024/2020；MO/FJ 无移动榜自动切宽带文案）+ 底部来源声明行（accessed 月份 + methodology 链接，E-E-A-T）
  - 数据纪律：3 个研究 agent 并行核实（2 个被 API 内容过滤杀掉但覆盖面被其余 agent 重复覆盖）；**直接抓取完整获奖表 > 搜索 snippet > 二手报道**，PE 下载速度奖两批矛盾 → 整条弃用；PT/AR 仅存 2023 旧报告 → 标注 "directional, not current" 诚实收录；IS/GE/KE/MO/CN 无近期报告 → 只出 Global Index 链接不编造
- ✅ 验证：全站 h2/h3 标点扫描 7078 个仅 3 处（research 枢纽卡主标题 "Title: Subtitle" 惯例豁免）；US/JP/TR/MO/HK/IS 六国抽查全 PASS（卡片文案/编码 slug/rot 锚文本/index-only 降级）；构建 520 页 0 error
- ⚠ 模板坑两条入档：Go html/template 会把 href 里的 `(` `)` 编码为 `%28%29`（`| safeURL` 也拦不住，HTTP 等价可接受）；`with .field` 内 dot 变字符串后不能 `.key`，必须 `range $b :=` 显式循环变量

### 2026-10-01 批次E（首页文案 + 全站 meta title/desc 合规改造）

- ✅ **首页三件套**（用户给的中文口号英化）：title "Compare eSIMs, Travel Data for Less"（渲染 47 字符含尾缀）、description 151 字符（含 8 品牌/50 国数字）、hero H1 "Compare every travel eSIM. / Pay less abroad."（高亮词换成 "Pay less"）+ 副标微调（数字前置、去 every×3 重复）
- ✅ **全站 meta 审计工具**：新 `scripts/audit_meta.py`（扫 public/ 渲染产物：标题 ≤60 / 描述 120-158 / 重复检测 / 分页型统计；实体已 unescape 防误报）
- ✅ **审计发现三宗罪**：①450 个计算页标题全部超长（68-87 字符）②50 国家页 description 是陈旧稿（全部写着 "51 plans from 5 providers"，japan 手写稿还点名已退场的 Nomad）③8 品牌页 desc 引用不存在/未核实的折扣码（SIFT15/SIFT5/SIFT10）+ hugo.toml 站默认 desc 也带 Nomad
- ✅ **修复**（共 503 文件）：head.html 国家页/子页标题公式改双档自适应（富版装不下 60 字符自动落短版，如 UAE）；50 国 desc 由 plans 数据实时计算重生成（含真实套餐数/品牌数/最便宜品牌）；gen_provider_pages.py desc 模板改双档尾巴 + 重跑 400 子页；28 VS 标题 4 家族统一收短；8 品牌页/5 guides/3 research/matchups/静态页 24 文件显式重写（折扣码全部对齐真码 web20/VEEPEE25/WELCOME10）
- ✅ 验证：509/509 页合规（标题全 ≤60、描述全 120-158、0 重复标题 0 重复描述）；h2/h3 扫描 7078 个 0 违规；validate 0 error 0 warning；构建 520 页 0 error
- ⚠ 坑：audit 脚本里局部变量命名 `html` 会遮蔽 `html` 模块（AttributeError）；heredoc 里 `html = fh.read()` 已改名 `page`。gen_provider_pages.py 的 desc 现在自带 120-158 断言，出界直接报错拒绝生成

### 2026-10-02 批次F（meta 品牌规范 v3：标题 48-54 无品牌 / 描述 120-140 必含品牌）

- ✅ **规则变更（用户定）**：标题全部收窄到 48-54 字符（原 ≤60）；**内页标题一律不带品牌词**（新站无人搜品牌，字符留给关键词；仅首页标题保留品牌）；描述收窄 120-140（原 120-158）且**每页必含品牌 "eSIM Sift"**（用站内标准拼写，不拆成 eSIMSift 两种写法）；法务/联系 4 页（privacy/terms/contact/disclosure）豁免 eSIM 关键词检查（不参与关键词竞争，仅受长度+无品牌约束）；404 页全豁免
- ✅ **head.html**：`<title>` 尾缀 `| eSIM Sift` 移除（首页标题在 front matter 自带品牌）；国家页/子页标题改**候选串降级链**（从长到短取第一个 ≤54，审计兜底查 ≥48）：国家页 6 档（"8 Providers Compared From" → "All 8 Providers From" → "8 Providers From" → "Compared From" → "Prices From" → "From"），子页计量型 6 档 / 无限流量型 6 档（holafly 长国名自动落 "eSIM Plans From"）
- ✅ **新 `scripts/regen_meta_brand.py`**（幂等，可重跑；dry-run 先行）：A. 50 国 desc 品牌前置版（"eSIM Sift compares every {C} eSIM: N real plans…"，数据实时计算）；B. 28 VS 页标题按原家族重建到 48-54（F1 Verdict / F2 Price Comparison / F3 Which One Is Cheaper / roami-vs-roamic 特例）+ desc **3 家族轮换**（i%3，反同质化）；C. 29 个手写页显式 map（**品牌页/枢纽页 lead-in 各不相同**——"How good is aloSIM?"、"Saily is the NordVPN team's eSIM —" 等，8 连排比是模板化信号）；/esim-providers/ 标题 "eSIM Providers A-Z"(18) → "Every eSIM Provider Compared: 2026 Prices and Reviews"(53)；compare 枢纽 + methodology 两页补入（上轮漏网）
- ✅ **gen_provider_pages.py**：desc 模板品牌前置 + 120-140 断言（尾句 4 档自适应：benchmarked → ranked → live price index → live prices），重跑 400 子页
- ✅ **audit_meta.py** 新规则：标题 48-54 / 描述 120-140 / desc 必含品牌 / 内页标题禁品牌 / 404 豁免
- ✅ **research 枢纽 h3 修复**（顺手消掉上批的 3 处豁免）：卡片标题 `replaceRE "^(.+?):.*$" "$1"` 截到冒号前（"eSIM Price Index 2026"），h2/h3 硬规则全站 0 豁免 0 违规
- ✅ 验证：509/509 页合规（标题 48-54×408 + 首页 54 含品牌 + 法务页带 eSIM 词但免检 / 描述全 120-140 且含品牌 / 0 重复标题 0 重复描述）；h2/h3 扫描 0 违规；构建 520 页 0 error 0 warning；regen_meta_brand.py 重跑幂等（0 changed）
- ⚠ 坑：Hugo `replaceRE "^(.+?): "` 只删匹配段不删尾部——要删到行尾须 `":.*$"`；重跑脚本需识别自己上一轮产出的新家族形态（"Which One Is Cheaper"/"Prices, Data and Verdict"），检测条件按子串宽匹配保幂等

## 已完成（批次G：guides 深度重写 + 设备库 UX + 全站首屏图 + /research/ 枢纽升级 + 全站去写死，2026-10-02）

用户四点诉求：① compat 设备列表排版美化 ② Basics & how-to 每篇首屏配图（SEO 合规）③ guides 内容信息增量不足以赢竞品排名 ④ 新增国家时不得回改写死的 "50 国/8 家"。

- ✅ **guides 5 篇全部深度重写**（~800 词 → 1677-1955 词；2 并行 agent + compat 手写——agent 跑 API 内容过滤 400 挂了一次，改手写；备份 `_guides_backup_20261002/` 在**项目根**）：每篇新增竞品没有的深度段（what-is：eUICC/profile 之辨+安装≠激活≠生效+安全节；vs-physical：7 行对照表+LTE 上限诚实说明+多国行程；install：SM-DP+ 手动录入+落地激活流程+转机规则+dual-sim：双线来电/iMessage/WhatsApp 走数据线+Wi-Fi Calling 陷阱+3 个账单惊吓场景逐一对应开关；compat：区域变体机制+平板笔电+验机清单）；FAQ 4-5 → 7-8 条；内链 9-14 条/篇（短锚文本、全轮换）；front matter 六键逐字节保留（diff 验证）
- ✅ **首屏配图**：5 guides + research hub 各一张（flat-vector webp 2848×1470，从 static/img/esim 133 张里按主题挑，避开重复意象）；`hero`+`hero_alt` 进 front matter；guides/single.html 与 research/list.html 渲染 `<figure>`：imageConfig 显式宽高（CLS）+ eager + fetchpriority=high（LCP）+ 描述性 alt；head.html `og:image` 按页取 hero
- ✅ **compat 设备库 UX**：14 品牌从平铺 chips 改**品牌分组卡片**（header 品牌名+家族+年代+计数徽章、amber 变体警示内联、chips 悬停态）；搜索框 + 品牌 tab（aria-pressed 态切换）+ 空段隐藏 + aria-live 计数
- ✅ **/research/ 枢纽升级**：首屏两栏（左文字+统计瓦片，右 hero 图）；新增**区域价格联赛**（countries.toml region 聚合各国最优 $/GB 的均值——欧洲 $0.44 最便宜 / 非洲中东 $1.44 最贵这类结论没有竞品算过）；最贵 vs 最便宜**价差叙事**（6× more in Kenya than in France，全计算）；**问答路由卡 ×6**（搜索意图 → 对应研究/工具页）；FAQ ×6 + FAQPage schema；正文 3 段（computed-not-written 立场）
- ✅ **全站去写死三层架构**（新增国家零回改）：模板层 `{{ len hugo.Data.* }}`（7 处布局改造）+ 正文层 4 个计数 shortcode（count-countries/providers/app-providers/direct-providers）+ front matter 层无数字措辞（9 处重写；国家页 seo.description 例外——regen 脚本再生）；**新守卫 `check_hardcoded.py`**（553 文件 0 违规）
- ✅ **新守卫 `check_headings.py`**：h2/h3 标点扫描固化成脚本（以前是临时 python -c）
- ⚠ 坑：**`content/` 下 `_` 前缀目录不会被 Hugo 隐藏**——备份目录曾放 content/en/ 下导致渲染出 6 个重复内容页（520→527）；备份必须放项目根或其他 Hugo 不挂载的位置。另一坑：重构 list.html 时聚合键 `v`/`minPerGB` 改名不彻底 → `$%!f(<nil>)` 静默渲染（构建不报错），grep `%!f` 验记入红线
- ✅ 修复：esim-price-index 标题 56>54 → "eSIM Price Index 2026: Every Country Ranked by Cost"(51)，md+regen MAP 双处同步
- ✅ 验证：520 页 0 error 0 warning；audit_meta 509 页 0 违规 0 重复；h2/h3 0 违规；check_hardcoded OK；sitemap 508 URL 无备份泄漏；research hub 5 区域卡/6 问答卡/6 FAQ/价差行全部渲染

## 已完成（批次H：AEO/GEO 基础设施 + 前端两处修复，2026-10-02）

- ✅ **AI 搜索引擎优化（AEO/GEO）三层补齐**：
  - `layouts/partials/schema-org.html`（新）：Organization + WebSite JSON-LD 全站 509 页输出（实体锚点 name/url/logo=apple-touch-icon/publishingPrinciples→methodology；**sameAs 留空不造假**，等有官方社交 profile 再补）
  - `layouts/partials/schema.html` 追加 Article JSON-LD：`.IsPage` 且 Section∈(guides,research) 自动覆盖 5 guides + 3 research 文章（headline/description/datePublished/dateModified/author=publisher=站级 Organization/mainEntityOfPage/image=hero）
  - `layouts/robots.txt`（新）：显式 Allow 15 个 AI 爬虫（GPTBot/OAI-SearchBot/ChatGPT-User/ClaudeBot/Claude-User/anthropic-ai/PerplexityBot/Perplexity-User/Google-Extended/GoogleOther/cohere-ai/meta-externalagent/Applebot-Extended 等）+ 声明 sitemap（防御性——AI bot 本就 opt-out）
- ✅ **前端两处修复**：① 品牌筛选 chip 方向写反（原「点=关掉」→ 现「未过滤时点=只看它，其余关掉；已过滤时点=增删切换；全关=重置全开」）② 斑马纹 `#f5f7fa`→`#eef2f7`（略深增行间分隔；用户看到的绿色=浏览器缓存旧 CSS，代码早已中性色）
- ✅ 验证：509 页 0 error；首页 3 个 JSON-LD 块（Org+WebSite+Breadcrumb）；509 页 Organization、8 篇 Article；robots.txt 含 sitemap；无 %!f
- ⏭ 暂缓（等真实资料/上线后）：作者实体 byline（用户无真实团队）、llms-full.txt、speakable、Dataset schema

## 已完成（版式统一 + 全站右侧吸顶内链列，2026-10-03 第二轮）

- ✅ **版式基线确立（用户定）：内容页统一对齐 Basics & how-to 文章版式**
  - `/networks/{country}/` 从 `max-w-4xl` 单列改为 `max-w-6xl` 双栏 grid（正文列 + 300px 吸顶右栏）
  - 补首屏配图（`<figure class="mt-6 overflow-hidden rounded-2xl border border-ink-100 …">`，与 guides 同款：`imageConfig` 取显式宽高防 CLS、`eager + fetchpriority=high` 抢 LCP）
  - **配图取该国第 2 张图**（`countries.images[1]`），刻意避开 `/compare/{country}/` 已用的第 1 张，同国两页不同图；`fileExists` 门控，缺图自动不渲染
  - 两张表（记分板 / 品牌→网络）由裸 `<table>` 改为 `.table-pro` 卡片（`card overflow-hidden p-0` + `overflow-x-auto`），与 guides 的安装方式表同款（斑马纹 + 吸顶表头 + 左轨高亮）
- ✅ **新增 `layouts/partials/aside-destinations.html`（可复用吸顶内链模块）**
  - 候选池 = 11 个高价值目的地（US/GB/CN/JP/DE/FR/ES/IT/AU/CA/HK），自动排除当前页所在国家（`.Params.iso`），避免自链接
  - **每页展示 6 条**；起点由「页面永久链接的 `hash.FNV32a` % 候选数」决定 → 每页组合各不相同（观感随机），但同一页每次构建**结果完全一致**（可 diff、可复现、可缓存）
  - **服务端渲染**（不用 JS 随机）——爬虫直接可见，JS 随机对爬虫等于不存在
  - 每行 = 国旗（`countries.flag`，`alt=""` 装饰性）+ 国家名 + 该目的地最低价（`country-stats.minPrice`）+ 链 `/compare/{slug}/`
- ✅ **接入页面族**：`/networks/{country}/` 单页、`/networks/` 枢纽（追加到现有 aside）
- ⛔ **已回退 → `guides/single.html` 不动**（2026-10-03 第三轮）：用户澄清「参考 Basics & how-to 的版式」= 抄它的壳盖到新页，**参考对象本身不许改**。原「包双栏 + 右栏 + Before you buy 卡」的改动已 `git checkout` 还原，guides 10 篇回到原版 `max-w-3xl` 单列。侧栏现只存在于 `/networks/` 与 `/networks/japan/`
- ✅ **校验**：`validate.py` 0 error 0 warning；hugo exit 0；`check_headings.py` 516 页 bad h2/h3 = 0；全站 515 页重复标题 0；全站真实内链 404 = **0**（逐页 href 映射 public 产物）
- ✅ **顺手修掉的 3 个存量问题**（都不是本轮引入，但守卫脚本正好报出来）：
  1. `check_hardcoded.py` 原本失败（exit 1）→ 两处写死总量：`layouts/index.html` 搜索框 `placeholder="Search 50 countries…"` 改 `{{ len hugo.Data.countries }}`；`content/en/networks/japan.md` 正文与 FAQ 的 "eight brands / eight providers" 改 `{{< count-providers >}}` 短代码 / 无数字措辞。**现 `OK: no hardcoded totals`（exit 0）**
  2. `/esim-deals/` 的 Step 5 链到 `/guides/how-to-install-an-esim/`（**真实 404**，正确 slug 无 "an"）→ 修正
  3. `/networks/japan/` meta 越界（title 46<48、desc 142>140）→ title 改 "Japan eSIM 2026: Best 5G Data Networks for Tourists"（51），desc 收至 138
- ⚠️ **价格口径提醒**：侧栏显示的是 `minPrice`（全站「Cheapest」同口径，如 US = Yesim 500MB/1天 $0.51），已在脚注显式披露「usually a 100–500MB trial size rather than a trip-sized plan」。若要改成「≥1GB 起价」（US $1.99 / GB $1.00 / CA $3.00），需同步改 50 国 title/description，属独立决策
- ⚠️ **`audit_meta.py` 仍有 6 处存量越界（本轮未动，非本轮引入）**：5 篇区域指南 `best-{region}-esim`（title 42–57 越界 + desc 缺品牌词）+ 首页 title 46<48
- ⏭ **未接入（需用户拍板）**：`/compare/{country}/`（50 个国家页）与 `/compare/{country}/{provider}/`（400 品牌页）为 `max-w-7xl` 全宽设计，加右栏需真重构，暂未动；`guides/region.html`（5 篇区域指南）自身已是国家页聚合表，边际收益低，暂未动

## 已完成（单国运营商深度页 /networks/{country}/ 开篇，2026-10-03）

- ✅ **新页面型上线：`/networks/japan/`（1/50）**——`layouts/networks/single.html`（新，纯数据驱动：运营商画像卡（tech/speed 区间/note/strong-weak，全部取自 `carriers.toml`）+ 品牌→宿主网络表（`plans/*.toml[ISO].networks`，逐行链 `/compare/{country}/{provider}/`）+ 城市覆盖（`carriers.info.cities`）+ Opensignal/Ookla 独立引用（`networkreports.toml`）+ FAQ(FAQPage schema) + 内链闭环）＋ `content/en/networks/japan.md`（front matter 承载 kicker/description/faqs，正文 3 段编辑层；H2 无标点合规）。**零写死**：计数、价格、速率全部构建期推导
- ✅ **标题机制修复（通用）**：`head.html` 原逻辑「有 `iso` 参数即套国家页 title」→ 新增 `seo.title` 锁定位（显式标题优先），并让锁定标题页仍取该国首图作 `og:image`。新页 title = "Japan Mobile Networks: Carriers Behind Every eSIM"（49 字符，全站重复标题数 0）
- ✅ **内链入口**：`/networks/` 枢纽目的地卡新增 "Carrier breakdown →" chip（`site.GetPage` 门控，未建的国不生成死链）+ 国家页 ⑦b 段落回链 "Japan carrier breakdown"
- ✅ **校验**：`validate.py` 0 error 0 warning；`check_headings.py` 516 页 bad h2/h3 = 0；新页内链 100% 可达（0 个 404）；sitemap 515 URL
- ⚠️ **待用户决策的数据冲突**：`data/faqs/jp.toml` 第 5 条仍写「Roami/Nomad 三网自动切换、Airalo/Saily 只连 Docomo 或 SoftBank」，与 2026-10-02「同国同运营商」规则（8 品牌 = 同样 3 网）矛盾，建议按新规则重写该条
- ⚠️ **Plan 覆盖度**：新页「品牌→网络表」按 `plans.networks` 渲染，若某品牌该国 networks 为空则整行缺失（当前 8 品牌全有，非阻塞）

## 已完成（修复 CSS 未重建导致版式塌陷 + 新增 CSS 同步守卫，2026-10-03 第三轮）

- 🐞 **事故**：`/networks/japan/` 右侧吸顶内链栏显示在**页面底部**，而非右侧
- 🔍 **根因（非 HTML 结构问题）**：本站 CSS 是**独立构建产物**——`npm run build:css` 用 Tailwind CLI 产出 `static/css/tailwind.css`，`hugo` 只负责把 `static/` 拷进 `public/`。前几轮改版式时**只跑了 `hugo`，从未重建 CSS**，于是新写的任意值类全部没有对应规则：
  - `lg:grid-cols-[minmax(0,720px)_300px]` ← 直接后果：grid 无 `grid-template-columns` → 退回单列 → aside 掉到正文下方
  - `max-w-6xl`（容器宽度没生效，页面通栏）、`lg:justify-center`、`lg:gap-10`、`mt-3.5`
  - Tailwind JIT 对未知类**静默忽略、不报错**，所以构建一直是绿的
- ✅ **修复**：重建 CSS（69,261 → 69,472 bytes，纯新增）。已确认 `static/` 与 `public/` 均为新版，预览服务返回的 CSS 含 `.lg\:grid-cols-\[minmax\(0\2c 720px\)_300px\]{grid-template-columns:minmax(0,720px) 300px}`
- ✅ **新增守卫 `scripts/check_css_sync.py`**：扫 `layouts/` + `content/` 的 `class="…"`，与编译后 CSS 逐类比对，缺任一即 exit 1。已做**复现测试**——手工删除那条 grid 规则，脚本准确报出 `lg:grid-cols-[minmax(0,720px)_300px] → layouts/networks/single.html`
  - 会剥掉 HTML 注释与 Hugo 注释（`{{- /* … */ -}}`），否则注释里的占位符会误报
  - 白名单 JS hook 类：`copy-code`、`est-step`
- ✅ **管线加固**（`package.json`）：`validate` 现在 = `validate.py && check_css_sync.py`；`build` 改为 **`build:css` 先行** → `validate` → `hugo`，一条 `npm run build` 不会再漏编译 CSS
- ✅ **校验**：`validate.py` 0 error 0 warning；`check_css_sync.py` OK（486 类全部有规则）；hugo 528 页 exit 0；`check_headings.py` 0 bad；全站真实内链 404 = 0
- 📌 **结论**：**只要动过 `layouts/` 里的 class，就必须跑 `npm run build`（含 build:css），不能只跑 `hugo`**

## 已完成（GSC 评分越界修复 + 全站格式串泄漏清剿 + 产物守卫，2026-10-03 第四轮）

- 🐞 **GSC 报错**：`/esim-providers/holafly/` — 「评分超出了指定范围或默认范围（在 reviewRating 中），存在此问题的内容无效」
- 🔍 **根因（双因叠加）**：
  1. 模板把 `"bestRating" "10"` 写成**字符串**、且**没写 `worstRating`** → Google 不认该量表，退回默认区间 **1–5**
  2. 评分本身是**编辑部算的价格竞争力指数**（`cheapest 命中国数 ÷ 覆盖国数 × 10`）：8 个有数据品牌里 **7 个低于下限 1**（Holafly/Airalo/AloSIM/Saily = 0.0、Roami/Ubigi = 0.2、Roamic = 1.2）→ 整块 Rating 判为无效
- 🔍 **更根本的合规问题**：Google 明文规定 `itemReviewed` 为 **Organization / LocalBusiness** 时「**評分必須直接來自用戶，請勿依賴人工編輯來創建、精選或編制評分資訊**」。本页评分是价格库算出来的，不是用户打的星 —— 即便区间修好也拿不到星级，且触碰质量指南（可能触发人工处置）
- ✅ **修复（用户拍板：删掉评分标记）**，改 `layouts/esim-providers/single.html` §②：
  - **移除 `Review` + `reviewRating` 节点** → 全站 `reviewRating` 出现次数 **8 → 0**
  - 该指数改用 `additionalProperty`（`PropertyValue`）如实携带：Countries tracked / Cheapest-plan wins / Best value ($/GB) wins / Price competitiveness index (0-10, editorial)
  - `offers` 的 `lowPrice`/`highPrice` 改 **JSON 数字**（原为 `"10.90"` 字符串），`offerCount` 保持整数
  - 补 `url`（canonical）+ `image`（`fileExists` 门控，仅当 `static/img/providers/<key>.{png,webp}` 存在才挂）
  - 页面可见读数照旧（`X.X / 10`），label 改为 `Price competitiveness index (editorial)`，与卡内既有的 "No editorial star-rating — just the numbers" 口径一致
- 🐞 **顺手扫出 3 处 Go 格式串泄漏到正文**（比 GSC 报错更伤页面质量，因为用户直接看得见，且其中两处还进了 JSON-LD FAQ）：

  | 位置 | 页面症状 | 根因 | 修复 |
  |:---|:---|:---|:---|
  | `esim-providers/single.html:92` | `(%!d(float64=84)% of its coverage)` | `math.Round` 返回 **float64**，直接喂 `%d` | 加 `int` 强转 |
  | `research/fair-use-audit.html:24` | `%!d(float64=63)% carry an explicit note` | 同上 | 加 `int` 强转 |
  | `tools/list.html:213` | `20%!m(MISSING)argin` | printf 里的**字面百分号没转义** | `20%` → `20%%` |
  | `compare/vs-single.html:210` | 句尾多出 `%!(EXTRA string=Airalo, string=Holafly)` | printf **无占位符却传了 2 个参数** | 补 `%s`，改成 "one of A or B sells only unlimited…" |

  修复后全站 `%!` 渲染错误 **17 个文件 → 0**
- ✅ **新增守卫 `scripts/check_output.py`**（**产物层**校验，必须在 `hugo` 之后跑），三类只有 `public/` 里才看得见的缺陷：
  1. Go 格式串泄漏 `%!x(…)` —— 全 `public/**/*.html` 扫描
  2. 每个 `<script type="application/ld+json">` 必须 `json.loads` 可解析
  3. 评分区间：`reviewRating` / `aggregateRating` / 独立 `Rating` 节点的 `ratingValue` 必须是 **JSON 数字**且落在 `[worstRating‖1, bestRating‖5]`（含「量表写成字符串」这一失败模式）；已按 `id()` 去重，嵌套节点不会被报两次
  - 已做**复现测试**：植入「字符串量表 + 0.0 越界 + 独立 AggregateRating 9 越界 + JSON 坏块 + 两类格式串泄漏」共 6 个缺陷，脚本全部命中且 exit 1；植入合法 `AggregateRating 4.4/[1,5]` 不误报
- ✅ **管线加固**（`package.json`）：新增 `check:output`；`build` = `build:css` → `validate` → **`hugo`** → **`check:output`**（顺序关键：产物校验必须在构建之后）
- ✅ **校验**：`validate.py` 0 error 0 warning；`check_css_sync.py` OK（486 类）；`hugo` 528 页 exit 0；`check_output.py` **516 页 / 2117 块 JSON-LD 全绿**；`check_headings.py` 0 bad
- 📌 **结论**：`itemReviewed` 为组织/商家的评分**不得**由编辑部计算；想拿星级只有一条正路 —— 上真实的站内用户评分体系

## 待办（按优先级）

### P-2 蓝图 Phase 2（等 P-A 真实数据后；见 docs/keyword-map.md 预留槽位）

- [ ] 区域枢纽页 ×5（/compare/{region}/）
- [x] ~~单国运营商深度页~~ **2026-10-03 起做：`/networks/{country}/` Japan 完成（1/50）**，模板已固化，余 49 国加 content md 即可（见上节）
- [ ] /networks/{carrier}/ 运营商页、/devices/{device}/ 设备页
- [ ] tools 再加 2 个、sitemap 分片（>1000 URL 时）、国家页 authority 外链

### P-A 数据收尾（价格已全真 ✅，剩非价格项）
- [x] ~~**抓取队列**~~ 已全量完成：8 品牌 × 50 国 = 400 raw JSON = 8776 条真实套餐（esimdb 七家 + holafly 官网 PDP + roami 本地提取）；`validate.py` 0 error 0 warning，无 SAMPLE
- [ ] networks 逐品牌补真（esimdb 不展示网络名；airalo.com 国家页有 host networks 可抓，其余品牌官网同理）
- [x] ~~**折扣码换真**~~（2026-10-01 完成，见上轮日志；遗留：3 家 promo_expires 占位 2027-12-31 需上线前复核）
- [ ] 四家联盟深链规则补进 `[params.outbound.targets.*]` 的 `country_path` + `countries.toml slugs`（当前 `<slug>-esim` 是模式假设）
- [ ] 逐国 quirks 人工复核（生成内容基于真实常识，但上线前过一遍）
- [ ] `data/carriers.toml` 50 国画像逐国人工核对（本轮已全覆盖 ~154 profiles，但速度区间/覆盖特性为编辑常识典型值，P-A 上线前逐市场核实）

### P-B 内容生产线
- [ ] 49 国 3 段分析 + 6 条 FAQ 的人工润色（生成器已产出可读初稿，japan.md/jp.toml 为手写样板；数字全部由数据计算而来，改数据重跑生成器即可刷新）
- [ ] 变体子页（cheapest/unlimited/long-stay）— 等主站数据 ≥10 国再上，防关键词蚕食

### P-C 上线前
- [ ] privacy/terms 法律审校（文中已标注 Todo）
- [ ] GA4 ID 替换 + 与 roamiapp.com 跨域衡量（head.html 占位注释处）
- [ ] OG 图片（每国一张，含最低价数字）
- [ ] 部署（Cloudflare Pages 建议；`/go/` 边缘函数跳板可后加）
