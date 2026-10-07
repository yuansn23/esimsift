# eSIM Sift — 项目状态

> 独立 eSIM 比价站。单一数据源（`data/*.toml`），模板层推导一切派生指标。
> 基座：Hugo 0.159.1 + Tailwind CLI。语言：英语（目录结构已为多语言预留）。

## 命令

```bash
npm run build     # 数据日期自动盖章 → Tailwind CSS → 数据校验 + CSS 同步校验 → hugo → 产物校验（上线前的完整管线）
npm run dev       # 同上（含盖章）+ hugo server
npm run stamp     # 单独跑「数据变了就把核对日推到今天」（见 §4.3；台账 docs/checked-state.json 必须提交）
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
10. **抓来的数据可能夹带本地语言，纯英文站必须罗马化**（2026-10-03 事故）：Airalo 韩国套餐源头叫
   `'짱 Jjang - 1 GB`，原样上了 `/compare/south-korea/` 与 `catalog.json`。**拉丁变音符保留**（`Élan`/`Fáilte`/`Prosím`
   是真实产品名），**非拉丁一律丢**。归一化在 `scripts/scrape/toml_write.py::clean_plan_name()`；
   数据层跑 `validate.py`（构建前拦），产物层跑 `check_output.py`（`hugo` 后拦）
11. **`static/` 下放什么就发布什么**（2026-10-03 发现）：`static/img/esim/图片_backup_20260929/` 连带里面的
   `.workbuddy/`（内部 py 脚本 + 日志 + memory md）被原样拷进 `public/`，线上 HTTP 200 可直接下载。
   **备份/草稿/临时产物一律放项目根，`static/` 只放页面真正引用的资源**

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

## 已完成（Japan 深度页收口 + 页头二级菜单 + 品牌子页补链，2026-10-03 第五轮）

- ✅ **`/networks/japan/` 标题下徽章行收口**（用户要求）：删掉 `5G live` 与 `all brands ride all 3` 两个徽章（两者在正文里已反复讲透，徽章位置重复）；保留 `3 carrier networks` + `177 plans tracked`
- ✅ **日期改为构建时的系统日期**：原徽章读 `country-stats.checkedDate`（= 上游列表最后一次核对日，JP 是 **Sep 30, 2026**），现改 `now.Format "Jan 2, 2006"` → **Updated Oct 3, 2026**。两个日期语义不同，不混用：**发布日期**用 `now`（页面每次发布都显示当天）；**上层核对日**仍在右栏脚注里写明（`…listings at the Sep 30, 2026 snapshot`），保住可信度
- ✅ **页头 `Network map` 升级为数据驱动二级菜单**（`partials/header.html`）：
  - 列出所有已发布的 `/networks/{slug}/` 深度页（`site.GetPage` 逐个门控，**0 个时自动退回单链接，1 个时就只有 1 条，不造假条目**；加国家自动变长）
  - 复用既有 `nav-mega` / `mega-region`（max-h-44 滚动）/ `mega-link` 组件，与 Compare countries、Guides 下拉同款；窄面板 `w-80 left-0`
  - 与 Compare countries 大菜单**不重复**：那个进 `/compare/{slug}/`（价格），这个进 `/networks/{slug}/`（网络）
- ✅ **品牌×国家子页补入链**（`compare/provider.html` 新增「Which network does {A} ride in {C}」段）：`/compare/{country}/{brand}/` 这 400 页原本**一条网络链接都没有**。新段落写清「品牌在该国没有自己的基站，走的是本国宿主运营商 ×N + 名字列表」，并给出深度页链接；深度页未建时退回 `/networks/` 枢纽链接 → **建满 50 国后自动变成 400 条入链**
- ✅ **入链终态**（Japan 为例）：页头菜单 516 页全站 + 枢纽卡 1 + 国家页 1 + 品牌子页 8 = 正文上下文入链 10 条（此前只有 2 条：枢纽 + 国家页）
- ✅ **校验**：`validate.py` 0/0；`check_css_sync.py` OK（487 类）；`hugo` 528 页 exit 0；`check_output.py` 516 页 / 2117 块 JSON-LD 全绿；`check_headings.py` 0 bad（新 h2 无标点）
- 📌 **IA 结论**：**不再另建顶层「Networks」入口**——页头已有 7 个顶层项 + 2 个大菜单，再开一个与 Compare countries 内容高度重叠的菜单会稀释信息架构。深度页的入口设计为「页头一个二级菜单 + 三处正文上下文内链」，随国家数自动扩张，无需改结构

## 已完成（清剿抓取数据夹带的非拉丁套餐名 + 双语种守卫，2026-10-03 第六轮）

- ✅ **问题**：用户发现 `/compare/south-korea/airalo/` 里出现韩文 `짱 Jjang - 1 GB`。站点是纯英文站，不该有韩文
- ✅ **根因**：`data/plans/*.toml` 是 **2026-09-30 从 esimdb.com / holafly.com 抓取**的（`scripts/scrape/`），Airalo 韩国套餐在源头就叫 `'짱 Jjang - 1 GB`（`짱` = 韩语"最棒"，前面还带一个 DOM 残留的 **前导撇号**）。数据原样入库 → 原样上页
- ✅ **影响面（量化）**：全站源文件扫描，**非拉丁文字只有这一处**（Hangul 18 行 / 1 文件）。其余 `Prosím`(CZ) `Élan`(FR) `Fáilte`(IE) `Hé Hé`/`Hè Hè+`(NL) 等 6 国 100+ 条是**拉丁变音符的本地词，属 Airalo 真实产品名 → 保留**。产物层命中 4 个文件：`/compare/south-korea/`、`/compare/south-korea/airalo/`、`catalog.json`、`/tools/`
- ✅ **修复**：18 条改名 `'짱 Jjang - X` → `Jjang - X`（丢韩文 + 丢前导撇号），带 18 条精确计数断言，修完 `짱` 残留 0
- ✅ **抓取层归一化**：`scripts/scrape/toml_write.py` 新增 `clean_plan_name()`（丢非拉丁脚本 + 去前导标点 + 收空格），在 `parse_plan` 里统一过一遍，改动会打印出来 —— **重抓不会复发**
- ✅ **两侧守卫**（新）：
  - `scripts/validate.py` §3（数据层，构建前）：套餐名含非拉丁脚本 → **ERROR**；首尾空白、首字符是标点的残留 → ERROR。**新抓数据后跑它**
  - `scripts/check_output.py` ④（产物层，`hugo` 之后）：全站 `.html` + `.json` 扫非拉丁脚本 → ERROR。**故意不拦拉丁变音符**
- ✅ **反向测试**（证明守卫不是摆设）：数据层植入 1 条韩文名 → 报 2 条 ERROR（非拉丁 + 前导标点）；产物层植入 `bad.html` + `bad.json` → 报 5 条（含 `catalog.json` 与韩国页的真实残留）。清理后两侧复跑全绿
- ✅ **校验终态**：`validate.py` 0/0；`hugo` exit 0；`check_output.py` **517 文件（516 页）/ 2117 块 JSON-LD 全绿**；产物内非拉丁字符 **84 → 0**
- ⚠️ **顺带发现（尚未处理，待用户决策）**：`static/img/esim/图片_backup_20260929/` 是图片处理的备份目录，内含 `.workbuddy/` 子目录（19 个文件：内部 py 脚本 + 处理日志 + memory md）。**`static/` 下所有东西都会被 Hugo 原样发布** —— 线上实测 `https://www.esimsift.com/img/esim/图片_backup_20260929/.workbuddy/process_log.txt` **HTTP 200（35KB）**，且已随 first commit（`3e37047`）进 git。无任何页面链接它（不会被爬虫主动发现），但路径可直接访问。**建议移出 `static/` 放项目根**（见 PROJECT.md §14 红线 22）

## 已完成（networks 网络深度页从 1 国扩到 12 国，2026-10-03 第七轮）

- ✅ **目标**：用户要求把 `/networks/{country}/` 从 Japan 一国扩到 11 国（美国 德国 加拿大 法国 墨西哥 泰国 西班牙 韩国 中国 英国 荷兰），**质量不低于日本、禁止同质化模板化、必须过谷歌 SEO、目的是抢排名与自然流量**
- ✅ **数据层（3 个研究子代理 + 人工核 URL）**：`data/networkreports.toml` 新增 10 国 `.awards[]` 记分板（每国 3-4 家运营商 × Opensignal/Ookla 双源结论），补齐 CA/FR/MX/ES/**NL** 缺失的 `ookla_note`，KR 的 Ookla 换成 **RootMetrics Seoul-Incheon** 源，TH 的 `opensignal_facts` 校正为 **August 2026** 认证数，新增整块 `[CN]`（**只有 Ookla Global Index 221.77 Mbps；Opensignal 不发布中国大陆报告**）。所有引用 URL 逐个 curl/WebFetch 验真，**未编造任何数字**
- ✅ **`data/carriers.toml`**：补齐 CN 缺失的 `info.detail`（China Mobile / China Unicom / China Telecom 三条强项+短板）
- ✅ **11 篇 `content/en/networks/*.md`**：每篇 5-6 个**该国独有**的 H2 议题（非模板），例如
  - US：Band 71 / VoLTE / 2022 年 3G 关网
  - DE：2017 实名法 / Video-Ident 与 PostIdent / 欧盟漫游 / 3G 已退网
  - CA：Bell-Telus 共享无线网 / 高价数据 / 无实名 / 落基山断点
  - FR：实名登记 / Orange 2G 2026 关停 / 欧盟漫游
  - MX：2026-01-09 全国线路实名（**旅行 eSIM 属境外发行、豁免**）/ Telcel 一家独大
  - TH：护照+人脸生物识别 / 游客 SIM 60 天上限 / 海岛覆盖
  - ES：四个网络三个东家（MasOrange 同一集团）/ 实名 / 加那利与巴利阿里
  - KR：实名与 ARC（后付费）/ 游客可买 data-only eSIM / 5G 486 Mbps
  - CN：境外 eSIM 绕过防火墙 / **必须起飞前装好** / 国行手机 eSIM 阉割
  - GB：无实名 / 脱欧终结欧盟免费漫游 / 农村=EE
  - NL：无全面实名 / Odido 是 T-Mobile NL 改名 / 预付费 eSIM 稀缺
  - 后 6 个 H2（运营商卡/记分板/品牌×网络表/城市/FAQ/下一步）为数据驱动结构段，故意保持一致
- ✅ **踩坑（自查自修）**：`kicker` 与 FAQ 里曾写 `{{< count-providers >}}` **短代码**，但 **YAML front matter 不跑短代码** → 会原样渲染成字面量。10 个文件已改为 `the`（短代码只在正文用）
- ✅ **语法修正（数据驱动）**：模板 `{{ $country.name }} has N national carrier networks` 对需要冠词的国家会生成 **"United States has 3…"**。新增 `data/countries.toml` 可选字段 `article = "The"`（US/GB/PH/NL/AE 共 5 国），模板改为 `{{ with $country.article }}{{ . }} {{ end }}{{ $country.name }}` → 现渲染 **"The United States has 3 national carrier networks"**。只改主谓位置，`in the United States` 等定语位置不受影响
- ✅ **校验终态**：`validate.py` **0 error 0 warning**；`check_css_sync.py` OK（487 类）；`hugo` **539 页**（+11）exit 0；`check_output.py` **528 文件（527 页）/ 2161 块 JSON-LD 全绿**（无格式串泄漏、无非拉丁字符、评分全在区间）；`check_headings.py` **0 bad**
- ✅ **产物层实测（12 页全过）**：
  - 体积 86-91 KB（日本 90 KB，**新页与日本同档**）
  - **title 全站 526 条 0 重复**；meta description 132-148 字符；canonical 全有
  - 每页 **FAQPage×1 + BreadcrumbList×1 + Question×5**（日本 6）
  - awards 记分板：11 国渲染真实双源表格；**中国无 awards → 自动回退 fact-list 布局**（Ookla 段 + Source 链接），不空块不报错
  - **内链 0 死链**（12 页全部 href 逐条解析回文件系统）
  - **入链三条全通**：枢纽 `/networks/` 卡片 ✓、国家页 `/compare/{c}/` Networks 段 ✓、品牌子页 `/compare/{c}/airalo/` 段 ✓（12/12 YES）
  - 页头 **Network map → Carrier breakdowns** 二级菜单已列出 12 国（带国旗 + "X networks" 文案）
  - `sitemap.xml` 收录 12 个 `/networks/{c}/`
- 📌 **结论**：模板已证明是**纯数据驱动**——11 国只加 `content md + networkreports.awards` 就出页，版式/内链/结构化数据零改动；余 38 国同法推进

## 已完成（12 页 SEO/内容策略重写：去同质化 + 信息增量 + 权威外链，2026-10-03 第八轮）

- ✅ **目标**：用户下了 21 条硬要求（关键词植入/自然语义/堆砌/密度/遗漏词/LSI/禁极限目的地/信息增量/语句通畅/谷歌审核/锚文本多样/搜索意图/H2 同质化/排名超越竞品/竞品空白=机会/关键词蚕食/终审/权威外链 3-4 条）。批判性重审 12 页，**先量化再动刀**
- 🔍 **改前体检（量化，不是感觉）**：
  - **重复句**：跨页完全相同的句子（≥60 字符、出现在 ≥4 页）**14 条**——全部来自模板静态导语与「Next steps」卡片副文案
  - **锚文本**：`/compare/{c}/` 在单页内重复 3-4 次、同锚文本跨 12 页 12 次
  - **外链**：多数页 **0 条**外部权威引用（只有 methodology 内链）
  - **H2**：多页共用「How {国家} networks score in independent tests」等模板标题
  - **极限目的地**：正文出现 backcountry / glacier / desert 等小众线
- ✅ **模板层（`layouts/networks/single.html`）**：为 5 个模板生成的 H2（carriers / scoreboard / brands / cities / next）加 **front matter 覆盖钩子**（`h2_carriers` / `h2_scoreboard` / `h2_brands` / `h2_cities` / `h2_next`），未提供时才落回默认句；4 段静态导语重写为**随国家/网络数变化**的句子；「Keep reading」4 张卡与右侧「Keep exploring」列表改为**逐国文案**；3 处 `methodology` 锚文本改为 `how we rank plans` / `ranking methodology` / `methodology` 三种；右侧 `/networks/` 锚从 `eSIM network map →` 改为 `Network map for every destination →`
- ✅ **内容层（12 篇 md 全量重写）**：
  - **删净跨页重复句**（14 → **0**）
  - **每篇 5-6 个该国独有 H2**，且 H2 覆盖钩子逐个手写 → 全站 **133 个不同 H2，0 碰撞**
  - **LSI 15/15 全覆盖**（MVNO / roaming / VoLTE / spectrum / congestion / hotspot tethering / fair use / host network / prepaid …）
  - **禁极限目的地**：删 backcountry/glacier/desert 等，改为大众旅游场景（城市、近郊、热门海岛与常规交通线）
  - **锚文本多样化**：正文锚重复率 **0%–4.5%**（单页 ≥22 条锚）
  - **每篇补 2-3 条竞品没写的独有事实**（如 MX 旅行 eSIM 实名豁免、TH 60 天游客 SIM 上限、CN 必须起飞前装机、NL Odido 改名）
- ✅ **权威外链（自然分布在正文，不是脚注堆）**：每页 **4 条**（Opensignal 国别报告 + Ookla 国别报告 + 该国监管机构 + GSMA eSIM 规范）；**中国 3 条**（Opensignal 不发布大陆报告），美国补 FCC 3G 关网指南凑满 4 条。**全部 URL 逐个 curl/WebFetch 验真后才写入**
- ✅ **关键词蚕食专项**：`/networks/{c}/` 的 `seo.title` 与 `/compare/{c}/` 的 title **全面错开**——networks 走「Carriers / Networks」纯网络意图，compare 走「Best … Cheap … From $x/GB」比价意图；12 对标题 **0 重叠词组**
- ✅ **校验终态**：`validate.py` 0 error 0 warning；`hugo` exit 0；`check_output.py` 全绿；`check_headings.py` **0 bad**；`audit_publish.py` **title 526 条 0 重复 / 内链 0 死链 / 入链三条 12/12 全通**
- 📌 **结论**：可复用的收口清单已固化为 **`audit_networks.py` + `audit_final.py` + `audit_publish.py`** 三件套（跨页重复句 / 锚文本多样性 / 关键词密度 / LSI 覆盖 / H2 唯一性 / 极限目的地词 / 蚕食边界 / 外链数 / 发布就绪）。余 38 国推进时直接跑这套

## 已完成（GEO 深化 + 核心词植入 + 菜单全展开，2026-10-03 第九轮）

- ✅ **① 页头 Network map 子菜单全展开**：原用 `.mega-region`（`max-h-44` + `overflow-y-auto`），12 国已需滚动。改为**两列网格、去掉高度上限**，面板 `left-auto right-0 w-[32rem]`（32rem 是「左侧不越界」上限：触发点右侧约 524px，右对齐后左边缘 ≈12px，1024 宽视口也放得下）。`max-h-[calc(100vh-7rem)]` 只作极端数量（>40 国）在矮屏上的兜底，12 国**永不触发**
- ✅ **② llms.txt 收录 12 个国家网络页**：原来只列 `/networks/` 枢纽（AI 检索发现层的真实缺口）。`layouts/index.llms.txt` 改为 `range (site.GetPage "/networks").Pages` 动态列出每国页 + 标题 + 描述 → 现在 12 条全部进 llms.txt（生产构建域名正确）
- ✅ **③ GEO 结构层（模板）**：`layouts/networks/single.html` 新增三块
  - **短答块**「The short answer」：首屏下方、正文之前，内容来自 front matter `prompt_answer`。硬要求 = 自包含、点名实体（国家 + 运营商 + 数字）、不依赖上文 —— 这是 AI 引擎最容易被整段引用的部分
  - **关键事实栅格**：8 项全部构建期推导（运营商家数与名单 / 品牌数 / 预付费套餐数 / 不限量套餐数 / 5G 有无 / 最低 $/GB / 访客实名规则 / 实测报告日期），零写死。顺手天然覆盖 5G · unlimited data · prepaid · price 四个核心词，不必在正文硬塞
  - **ItemList 结构化数据**：逐运营商 `Organization` 实体（名称 + 技术 + 带宽区间 + Opensignal 结论），让 AI 不必解析 HTML 就能拿到「谁在运营 + 测得多少」。JSON-LD 块数 2161 → **2173**（正好 +12）
- ✅ **④ GEO 正文层：可提取性改造（第三批）** —— 这是最关键的一层。AI 按块检索，**段落首句若以代词开头或依赖上文，被单独抓走就失去意义**。用脚本扫出 29 处，重写 **24 句**为「自包含 + 点名实体」写法，例如
  - `This question decides a lot of purchases…` → `Whether a United States eSIM keeps working across the Canadian and Mexican borders decides a lot of purchases…`
  - `The three separate on performance…` → `Bell, Rogers and Telus separate on performance…`
  - `Every other page in this network map is about signal.` → `China is the one destination in this network map where the question is routing rather than signal.`
  - `The gap between first and third…` → `The gap between Telcel in first place and Movistar in third…`
  - 复核：**61 个 H2 段落首句，代词开头/过短 29 → 0**
- ✅ **⑤ 核心词自然植入（标题 / H2 / FAQ / 正文）**：用户给的核心词表（Travel eSIM · Data plan · Best · 5G · cheap · unlimited Data · for Tourists/Travel · Cheap 5G Travel Data · value · no roaming · compare/price/buy · prepaid · instant activation）
  - **标题层**：12 个 `seo.title` 统一为 `{国家} Travel eSIM Networks 2026: Best 5G for Tourists/Coverage/Islands…`（49–55 字符）；H1 统一为 `{国家} Travel eSIM Networks: {运营商} Explained`。**与 `/compare/{c}/`（Best X eSIM 2026: … From $y/GB，价格意图）保持边界**
  - **H2 层**：重命名 13 个 H2 带入 `data plan` / `no roaming` / `cheap` / `best`（如 `Crossing a German border on the same plan` → `Crossing a German border with no roaming charges`）
  - **FAQ 层**：每页 **5 → 8 条**自然语言问句（+36 条），覆盖 unlimited data / 是否比本地 SIM 划算 / 数据量估算 / 漫游 / instant activation
  - **终态覆盖（仅 `<article>` 正文计数）**：Travel eSIM 14–26× · data plan 3–7× · 5G 10–36× · best 2–36× · cheap 2–8× · unlimited data 3–4× · prepaid 2–16× · price 5–17× · buy 3–11× · compare 5–17× · for tourists 1–3× · 分散度**刻意不均**（不为植入而植入）
- ✅ **校验终态**：`validate.py` 0/0；`check_css_sync.py` OK；`hugo` **539 页** exit 0；`check_output.py` **528 文件 / 2173 块 JSON-LD 全绿**；`check_headings.py` **0 bad**；跨页重复句 **0**；H2 **157 个不同 / 0 碰撞**；全站 title 526 条 **0 重复**；内链 **0 死链**
- 📌 **踩坑（重要）**：**`hugo server` 会往 `public/` 写 dev 输出**（baseURL=localhost + livereload）。本站是**手动上传 `public/` 部署**且无 CI 配置 —— 所以「开着 dev server 直接部署」会把 localhost 链接传上线。**部署前必须先停掉 dev server，再跑一次 `npm run build`**（本次实测：停服后重新生产构建，`public/llms.txt` 里 localhost 出现次数 = 0）
- 📌 **另一条**：删 `static/img/esim/图片_backup_20260929/` 时 `mv` 报 Permission denied，根因是**运行中的 hugo server 监视该目录并持有句柄**，删除后它的 watcher 报错导致首页 500。**改 `static/` 前先停 dev server**

## 已完成（补齐 H3 标题层 + FAQ 标题化 + 标题层核心词收口，2026-10-03 第十轮）

- ❌ **补齐第九轮漏项**：用户要求核心词植入「标题 **h2h3**」，第九轮只动了 H2。实测 12 页**正文 H3 数量 = 0**（页面上仅有的 5 个 H3 全来自页脚模块：`Popular comparisons` / `eSIM providers` / `Company`…）—— 这一半需求确实没做
- ✅ **① 正文 H3 共 43 个，全部由原文已有子主题提升而来（零新写内容）**
  - 做法：把每个 H2 下**本来就存在**的行首加粗引导句（`**Bell leads on 5G.**`）升为真实 `###` 标题；**残留行首加粗句 42 → 0**
  - 落点全部是「运营商对照段」（每页 3–4 个，一国一条）+「法规段」（france 2 条 / japan 3 条）
  - 每个 H3 只带与该子主题**真正相关**的核心词（5G / best / cheap / value / prepaid / no roaming / instant activation / tourists）。反向约束也守住了：netherlands Vodafone、south-korea LG U+、thailand True Move 都不是廉价定位，就**不给它们写 cheap/value**
  - 加粗句升为 H3 后，其下段落首句同步改成**实体开头**（`It retained…` → `Bell retained…`），保住第九轮 GEO 正文规则 —— 复核：H2/H3 后首段「代词开头或过短」**0 处**、跨页重复句 **0**
- ✅ **② FAQ 问题升级为真实 `<h3>`（97 条）**：FAQ 一直是 `<details>/<summary>`，**不是标题元素**，AI 引擎按标题切块时整块丢失 —— 而用户给的原词「**Unlimited Japan eSIM for Tourists | Instant Activation**」恰好只活在这里
  - 模板：`<summary …><h3 class="contents font-sans text-ink-900">{{ .q }}</h3><span …>+</span></summary>`
  - **`display:contents` 是关键**：全局有 `h1,h2,h3,h4 { @apply font-display text-ink-950; text-wrap: balance }`，直接包 h3 会把问题渲染成 Sora 深色并触发 balanced 换行；`contents` 让 h3 不产生盒子 → **视觉零变化、纯语义增益**（`<h3>` 放在 `<summary>` 内是 HTML 规范明确允许的写法）
  - 8 个共用该结构的版式统一处理：networks / guides ×2 / research ×4 / tools
  - 升级前先清两类问题：**① 4 条含禁用标点**（`Which Japan network is fastest, Docomo or SoftBank?` → `Is Docomo or SoftBank the faster Japan network?`）；**② 4 条与同页 H2 近乎同题**（china 的 `Will a China eSIM work in a phone bought in China?` 与正文 H2 逐字相同 → `Does a China eSIM work on a mainland-bought handset?`）
- ✅ **③ 顺带修掉一处原有内容缺陷**：英国页 FAQ 的 `Does a UK eSIM work in Ireland?` 与 `Does a UK eSIM work in Ireland with no roaming charges?` **同事实、同结论**，标题化后变成同页重复标题。后者换成**正文已支撑但信息位不同**的 `Is Northern Ireland covered on a UK eSIM?`（含「边境县手机会漂移到爱尔兰共和国网络」这一独立提醒）
- ✅ **④ 标题层核心词覆盖（H1 + H2 + H3 + FAQ 问题）**：5G **12/12** · unlimited **12/12** · travel eSIM **12/12** · buy **12/12** · best **10/12** · prepaid **9/12** · cheap **8/12** · data plan **7/12** · value **6/12** · no roaming **6/12** · tourists **3/12**
  - 第九轮后标题层仍为 0 的 `unlimited`，靠 FAQ 标题化拿到 **12/12**，且**没有新写一句内容**
  - `for travel` 标题层仍为 0：**故意不做** —— 它是「for Tourists/Travel」的自然语言形态，正文里已有，硬塞进标题就是用户明令禁止的「为植入而植入」
- ✅ **校验终态**：`validate.py` **0 error / 0 warning**；`check_css_sync.py` **492 个 class 全部命中**（含新增 `contents`）；`hugo` **539 页**；`check_output.py` **528 文件 / 2173 块 JSON-LD** 全绿；`check_headings.py` **527 个 html，bad h2/h3 = 0**；正文 H3 **43 个全唯一**、禁用标点 **0**

## 已完成（城市块信息增益重写：逐城市实况取代模板化单句，2026-10-03 第十一轮）

用户指出：`/networks/` 12 页的城市块都是「城市名 chips + 一句同构泛话」，判为「太敷衍了，毫无信息增益可言，就轻飘飘的一句话难道也符合谷歌 SEO 吗」。

- ✅ **诊断（先量化，不猜）**：城市块 = `carriers.toml[ISO].info.cities`（**只有城市名**）+ front matter `cities_note`（每页一句，句式同构：`{城市列表} all run fast 5G on every network, and city signal is not the variable that decides a {国家} purchase…`）。全站扫描确认：**这是当时唯一真正在渲染的模板化填充块** —— 其余 14 个覆盖键 12 页全部写满（0 页缺），模板里的兜底默认句只在待命、不上屏。
- ✅ **数据层判断**：仓库内**没有城市级数据源**（无城市速度 / 城市报告），`info.detail`（运营商 strong/weak）只有加拿大有，且 `compare/single.html` 也在用 `info.cities` —— 所以既不能改 `cities` 的 schema，也不能编城市级数字。
- ✅ **改法**：新增 front matter `cities_detail`（`name` + `reality`），逐城市一句，回答**「这座城市之后，问题从哪条路 / 哪片地形 / 哪个区域开始」** —— 全部建立在仓库已有的网络结构事实（Bell/Telus 共享无线网、Telekom 覆盖最宽）与可核地理（Highway 1 进班夫、Sea-to-Sky 去惠斯勒、Mae Hong Son 环线）之上，**零新造数字**。
- ✅ **模板**：`{{ replace $r $n (printf "<strong …>%s</strong>" $n) 1 | safeHTML }}` 把段首城市名加粗 → AI 单独抽走一行仍自包含（与红线 28 同源），且**不新增标题**（不给 `check_headings.py` 添风险）。缺 `cities_detail` 时回退旧 chips。
- ✅ **验收**：`audit_cities.py` —— 12 页 **46 行**城市实况；行数与 front matter 一致、**每条都带 `<strong>`**、首句全部 ≥45 字符且非代词开头、**跨页重复 0**、导语 **12 条互异**；城市行平均 155 字符（旧版整块只有约 200 字符的 1 句）。
- ✅ **校验终态**：`validate.py` **0 error / 0 warning**；`check_css_sync.py` **492 class 全命中**；`hugo` **539 页**；`check_output.py` **528 文件 / 2173 块 JSON-LD**；`check_headings.py` **527 html，bad h2/h3 = 0**。
- ⚠️ **踩坑留档**：Hugo 的 `hasPrefix` 是 **STRING PREFIX**、`strings.TrimPrefix` 是 **PREFIX STRING**，两者拼用会**静默失效**（构建全绿但加粗没上屏）—— 改用 `replace` 完成，并靠产物断言兜住（见 PROJECT.md 红线 30）。

## 已完成（guides 全栏目 GEO 合规审核与优化，2026-10-03 第十二轮）

用户要求：审核 `guides/` 导航下的内容是否合规，并优化。审计口径按 §3.8 的四层（发现层 / 结构层 / 标题层 / 正文层）。

- 🔍 **审计结论（改前）**：10 个 guides 页 **10/10 缺整个结构层** —— 短答块、关键事实栅格、实体 ItemList 三块全无，原 JSON-LD 只有 `Article` / `FAQPage` / `BreadcrumbList`。正文层另有 20+ 处首句不以实体起首（`Usually not a callable one.` / `Same network, same service.` / `This is where the two designs genuinely diverge:` / `Yes — completely.` / `No.` / `Modestly.`）。发现层（llms.txt）**已合规**：10 页全部在内。
- ✅ **结构层（三个版式补齐）**：`guides/region.html` 加短答块 + 6 格事实栅格（国家数 / 最低 $/GB 及国家 / 区域均价 / 最便宜入门价及国家 / 夺冠最多品牌及次数 / 价格核对日，**全部构建期推导**）+ 逐国家 `Country` 实体 ItemList；`guides/single.html` 加短答块 + 阅读时长/复核日 + front matter `facts` 事实对 + **章节索引 ItemList**；`_default/list.html` 加短答块 + 子页 `Article` ItemList（`/guides/` 是唯一使用该版式的栏目）。
- ✅ **正文层**：改前 20+ 处首句不自足 → 改后 **0**（正文段落 + FAQ 首答双双归零）。全部只重组原句，**未新增事实、未编造数字**。
- ✅ **刻意不做 HowTo**：guides 的 H2 是问答式标题而非编号步骤，硬拆 `steps` 等于编造 —— 明确放弃。
- ✅ **顺带修掉 3 类跨页重复**（此前只查 `/networks/` 所以长期未被发现）：3 个模板 H2 各跨 5 页同题、4 段模板正文跨 5 页同文、4 条 FAQ 答案跨 4 页同文。改法 = 把区域名/计数拼进句子 + 给长文页新增 `h2_next` 覆盖钩子。**改后任意两页正文段落逐字重复 = 0**。
- ✅ **踩坑留档**：`.Fragments.Headings` 顶层是空 ID/Title 的合成根节点，直接 range 只产出 1 条空 ItemList（构建与四重校验均不报错，靠产物断言才发现）；改用 `.Content` 的 `findRE` 扁平提取。
- ✅ **验收数字**：结构层 **10/10 页 4 项全绿**；正文层未自足首句 **0**；FAQ 首答未自足 **0**；H2 跨页重复 **0**；正文段落跨页重复 **0/247**；ItemList 条目（区域 18/13/8/8/3 个国家；长文 10/9/8/7/8 个章节；枢纽 9 篇指南）。
- ✅ **校验终态**：`validate.py` **0 error / 0 warning**；`check_css_sync.py` **492 class 全命中**；`hugo` **539 页**；`check_output.py` **528 文件 / 2184 块 JSON-LD**（较改前 +11）；`check_headings.py` **527 html，bad h2/h3 = 0**。

## 已完成（guides 长文页两级目录 + 右侧吸顶栏，2026-10-03 第十三轮）

用户要求：在「Basics & how-to」（= `guides/single.html` 渲染的 5 篇）文章右侧做一个吸顶模板，既要合 Google SEO，也要满足用户搜索意图。方向经用户确认：**右栏 = 目录 + 内链 + 比价**，目录做 **H2 + H3 两级**。

- ✅ **正文先补 H3（内容层）**：5 篇原本只有 50 个 H2、1 个 H3。新增 **29 处 H3**（what-is-an-esim 9 / how-to-install-esim 4 / esim-vs-physical-sim 6 / dual-sim-and-esim 6 / esim-compatibility-check 4），**落点全部是原文已有的并列子主题**（加粗引导句、并列分述、既有清单项、两种用户画像），零硬塞、零新造事实。
- ✅ **同步改写 H3 后首段首句**：H3 会把原本「不是段落首句」的句子顶到被 AI 单独抽取的位置 —— 本轮因此暴露 6 处 `<45 字符`/代词开头首句（其中 4 处由改动引入），已全部补足为自包含句。
- ✅ **新建 `layouts/partials/aside-toc.html`**：从 `.Content` 用 `findRE` 扁平提取 H2/H3 生成锚点目录。**只扫正文 markdown** —— 模板渲染的短答块 / 关键事实栅格 / FAQ / 相关阅读刻意不进目录（它们要么在正文之前、要么是页尾模块）。纯服务端渲染，爬虫与禁用 JS 的读者都能拿到。
- ✅ **`guides/single.html` 改双栏**：单栏 `max-w-3xl` → `max-w-6xl` 栅格 `lg:grid-cols-[minmax(0,720px)_300px]`（与 networks 页同一断点与列宽）；右栏 `sticky top-24` + `max-h-[calc(100vh-7rem)] overflow-y-auto`，内含目录卡 + 复用的 `aside-destinations.html`（热门目的地比价内链）。
- ✅ **移动端不丢导航**：右栏 `hidden lg:block`，同时在正文顶部插一个 `lg:hidden` 的 `<details>` 折叠目录，手机上长文也有跳转入口。
- ✅ **高亮跟随（渐进增强）**：JS 只写 `aria-current` 属性，激活样式由 `.toc-link[aria-current="true"]` 承担 —— **一个 class 都不切**。原因：`check_css_sync.py` 会整个跳过含 `{{ }}` 的 class 属性，Tailwind JIT 又不编译运行时拼出的类名，两头都拦不住。新增 `.toc-link` / `.toc-l2` / `.toc-l3` 到 `main.css` 的 `@layer components`，class 属性一律静态字面量。
- ✅ **验收数字**：5 页目录条目 **20 / 15 / 16 / 15 / 14**（H2+H3）；每个锚点在页面里都有对应 `id`（缺失 0）；模板 H2 混入 **0**；桌面与移动两份目录条目完全一致；标题全局唯一（80 个，重复 0）；H2/H3 后首句违规 **0**；跨页重复段落 **0/119**。渲染后 H3：21 / 17 / 18 / 18 / 31（含 FAQ 与页脚）。
- ✅ **校验终态**：`validate.py` **0 error / 0 warning**；`check_css_sync.py` **500 class 全命中**（+8）；`hugo` **539 页**；`check_output.py` **528 文件 / 2184 块 JSON-LD**；`check_headings.py` **527 html，bad h2/h3 = 0**。

## 已完成（多语言 i18n 基础设施改造 —— 模板/数据/守卫/校验器四层，2026-10-03 第十四轮）

**目标**：把「后续新增语言」从"不可能"变成"加三个文件"。硬性验收：英文产物与改造前**逐字节一致**。

**关键实测结论（都是先起最小站点验，再动手）**
| 项 | 结论 |
|:---|:---|
| `{{ i18n "k" }}` | ❌ 返回普通 string，`&`→`&amp;`、`'`→`&#39;`，与字面量不一致 |
| `{{ i18n "k" \| safeHTML }}` | ✅ HTML 文本节点与字面量逐字节相同 |
| 属性值 `\| safeHTMLAttr` | ❌ `&` 被二次转义成 `&amp;amp;`；属性一律改用 `\| safeHTML` |
| 属性值含 `'`/`"` | ❌ 会被转成 `&#39;`/`&#34;`，`safeHTML` 拦不住 → 这类不抽（实测 0 例） |
| 内联 `<script>` | ❌ JS 上下文转义成 `\u0027`，`\| js` 行为异常 → 脚本文案不走 i18n |
| `.llms.txt` / `.json` | 同样会转义，也要 `\| safeHTML` |
| `{{ return }}` 在 `{{ if }}` 内 | ❌ `wrong number of args for return` → partial 只能一个顶层出口 |
| `{{ define "main" }}` | 会新建命名空间，外面的变量进不去 → 赋值必须写在 define 内部 |
| `site.Languages` / `.Site.Data` | Hugo 0.156 起弃用 → 改 `hugo.Sites` / `hugo.Data` |
| `.Format ":date_medium"` | ❌ 输出字面量；只有 `time.Format ":date_medium" $t` 生效，且英文下与 `"Jan 2, 2006"` 完全一致 |

**产出**
- `hugo.toml`：`defaultContentLanguageInSubdir = false`（英文留根路径，539 个已收录 URL 零变更）+ `[languages.en]` 补 `languageCode`，附新增语言三步说明
- `i18n/en.toml`：**749 个 key**（抽出 952 个静态文本节点 + 26 个属性值）
- `layouts/partials/i18n-data.html`：数据层按语言解析。英语下直接返回 `hugo.Data`（零开销恒等），存在 `data/<lang>/` 时深合并（实测：`name` 被覆盖、`slug` 保留、语言目录键被正确剔除）
- 34 个模板把 `hugo.Data.X` 换成 `$d.X`（`partialCached` 按语言缓存）
- `scripts/i18n_extract.py`（抽取器，幂等 + 行尾保真 + CRLF 预检闸门）、`scripts/lang_rules.py`（语言规则单一事实源）、`scripts/check_i18n.py`（守卫，已接入构建链）
- `.gitattributes`：`layouts/** text eol=lf` + `i18n/** text eol=lf`
- 16 处硬编码日期 → `time.Format ":date_medium"`
- `head.html`：`hreflang` + `og:locale`，门控在 `len hugo.Sites > 1`，**单语言下零字节输出**

**过程中发现并修复的既有缺陷**
1. **`check_headings.py` 从写出来起就是空转的** —— 闭合标签正则写成 `</h>`，真实是 `</h2>`，**一个标题都没查过**。修好（`</h\1>`）后一次扫出 8098 个 h2/h3，并修掉 `&amp;` 里 `;` 的误报（要先 `html.unescape`）。两者都修完仍是 0 违规，但守卫现在才真正生效。已接入构建链。
2. **全站产物字节依赖 checkout 行尾** —— `core.autocrlf=true` 让 `git checkout` 写 CRLF，而历史 `layouts/` 是「26 CRLF + 18 LF」混合。本轮 `git stash push -- layouts/` 对比旧构建时触发全站 527 页产物变化，一度误判为改造引入回归。已统一为 LF + `.gitattributes` 锁定。
3. **`compare/single.html:539` 的 `range $d :=` 变量遮蔽**（与新增的数据字典同名），已改为 `$det`。

**验收**
- i18n 抽取：**全部 527 个 HTML 页面逐字节一致**（证明链：纯净 LF 构建 ≡ i18n 改造后构建，HTML 全等；CRLF 版构建 ≡ 基线）
- 相对旧基线的 18 页差异 = 红线 38 记录的行尾归一所致的**纯空白差异**，已断言无语义变化
- `npm run build` 全绿：validate 0/0 · CSS 同步 500 class · i18n 守卫 OK · hugo 539 页 · check_output 528 文件/2184 JSON-LD · check_headings **8098 h2/h3 · 0 bad**
- `check_i18n.py` 已用「故意注入一处硬编码」验证会 FAIL

**未完成（新增语言前必须补，详见 PROJECT.md §18.3）**
- [ ] 704 处拼装句碎片重写为带占位符的整句（`check_i18n.py` 会报）
- [ ] 5 处内联 `<script>` 文案改 `data-*` 注入
- [ ] 语言切换器 UI（header 目前没有；须在第二个语言上真机验收）
- [ ] JSON-LD `inLanguage`
- [ ] 141 处 `printf` 生成整句的多语言化
- [ ] `data/plans` 的 `fup_note`（2684 条 / 6 模式）与 `name`（7776 条 / 2 模式）改造成模板渲染

---

## 已完成（删除非拉丁禁令 + 定位 dev server 污染 public/，2026-10-03 第十五轮）

**规则变更（用户定）**：站点要上多语言，**「全站禁止非拉丁字符」的守卫整体删除**（原方案是按语言划豁免前缀，用户改为直接删）。

**删除范围（三处）**
- `scripts/check_output.py` ④ 产物层非拉丁扫描 + 其 `.json` 分支 → 删。**顺手把 ① 的 Go 格式串扫描扩展到 `.json`**，否则 json 分支变成死代码
- `scripts/validate.py` §3 的 plan name 非拉丁检查 → 删。**保留**与语言无关的结构性校验（首尾空白、首字符是标点）
- `scripts/lang_rules.py` 的 `LATIN_SCRIPT` 表 + `non_latin_exempt_prefixes()` + `non_latin_exempt_data_dirs()` → 删

**代价（已写进红线 21 与 PROJECT.md §18.4）**：手动贴进 `data/plans/` 的韩文/汉字套餐名不再有任何守卫拦截，防线只剩抓取层 `toml_write.clean_plan_name()`（重抓时自动清洗并打印）→ **新抓一批数据后人工看一眼打印输出**。

**反向验证（证明删干净了）**
- 往 `data/plans/airalo.toml` 注入 `日本語` + 往 `public/index.html` 追加日文注释 → `validate.py` **0 error**、`check_output.py` **OK**（旧规则下两处都会 ERROR，第六轮曾实测报 2 条 + 5 条）
- 往 `public/catalog.json` 注入 `%!d(float64=84)` → `check_output.py` **正确报错** `public/catalog.json:1: Go format-string leak`（证明新增的 json 分支真的生效）
- 两处注入均已还原，`sha1sum -c` 校验文件字节复原 ✅

**URL 策略确认**：子目录，形如 `https://www.esimsift.com/ja/`。`defaultContentLanguageInSubdir = false` 已写死 → 英文留根路径、539 个已收录 URL 零变更，hreflang 由 `.Permalink` 自动生成。

**⚠️ 关键发现：运行中的 `hugo server` 会把开发态页面写进 `public/`**
- 现象：`public/compare/portugal/index.html` 与基线比对出现**非行尾差异** —— 里面是 `http://localhost:1313/...` 与注入的 `<script src="/livereload.js?...">`
- 定位：本机有 `hugo.exe` PID 24256 在监听 `127.0.0.1:1313`（带 5 个浏览器连接）。Hugo 的 `hugo server` **默认渲染到磁盘**（`--renderToMemory` 才不写盘）
- 实证：`touch data/titlesegments.toml` → 6 秒内 `public/` 里带 livereload 的文件从 **1 → 6**，同时 `index.xml` / `llms.txt` / `catalog.json` / `index.html` 被重写
- 影响：`public/` 在 dev server 运行时**不是可信的生产产物**；若此时部署，会把 `localhost:1313` 发布出去
- 规避：生产构建前停掉 dev server，或把 `package.json` 的 `dev` 改为 `hugo server --renderToMemory`

**产物回归比对（对 `_oldsite/` 基线，逐文件字节）**
- 全量 1107 vs 1107，**含非行尾差异的文件只有 1 个**，且已证实是上述 dev server 污染
- 其余 18 个差异文件 `norm(CRLF→LF)` 后**字节全等** → 纯行尾归一（红线 38），**本次改动零回归**

**校验终态**：`validate.py` 0 error 0 warning · `i18n 守卫` OK（0 硬编码 / 749 key）· `hugo` **539 页** · `check_output.py` **528 文件（527 页）/ 2184 块 JSON-LD** · `check_headings.py` **8098 h2/h3 · 0 bad**

---

## 已完成（品牌×国家子页 400 页 SEO/UX 优化 + 审核两轮，2026-10-04 第二十轮）

**方法论文档：`docs/provider-page-optimization.md`**（诊断 → 数据层 → 模板清单 → 验收 → 复用到其它页面型的五步）。
守卫脚本：`scripts/verify_provider_pages.py`（这一层专用的 11 项产物级检查）。

**这一层是什么**：`content/en/compare/<国>/<品牌>.md` 正文为空，只有 `iso`/`provider`/`layout: provider`/`seo.description`；
全部内容由 `layouts/compare/provider.html` 从 `data/plans/*.toml` 推导。**改一处 = 改 400 页**（50 国 × 8 品牌）。

**交付**
- ✅ 标题阶梯重写（`partials/head.html`）：**48–54 字符、不放价格、不放套餐数量**（两者都随数据过期，价格锚点交给 description）；
  候选串从长到短取第一个 ≤54，按"有没有计量套餐"分两套阶梯。实测 400 页落点 48–54、均值 51.1
- ✅ H1 分工：事实层 `{Brand} {Country} eSIM Plans & Prices (2026)`，意图层交给 title
- ✅ 结构化数据从 1 块扩到 6 块：**逐套餐 `Offer` 数组**（7776 条）+ `WebPage`(inLanguage/dateModified) + `FAQPage`(5 组)
  + `Product` 补 **`image`**（Google 富摘要的必需字段）与 `url`；一致性断言：Offer 条数 == 价格表行数
- ✅ 新增四个决策区块：**Plan reality check**（热点/5G 与速度/FUP 阈值/充值，源 `providers.toml[<brand>.policy]`）、
  **按时长比价**（3/5/7/10/15/30 天）+ **页内行程计算器**（输入天数自动挑"有效期覆盖整趟行程"的最便宜套餐并与最便宜竞品比价）、
  **Buy it if / Look elsewhere if**、**数据驱动 FAQ**；套餐表支持客户端排序
- ✅ 竞品内链矩阵：每张卡带**数据推导的差异点**（贵/便宜多少美元），全部指向竞品同层页
- ✅ 宿主网络段：该国运营商卡（制式 + 实测速度区间）+ 内链 `/networks/<国>/`
- ✅ `data/providers.toml` 新增 6 个 `[<brand>.policy]`（只填核实过的品牌，`roami`/`roamic` 留空 = "宁缺勿造"，
  产物里显式渲染 `Not checked yet`，守卫把"未核实页数 = 100"当断言）；
  顺手修掉与事实矛盾的历史数据：Holafly 的 `.strengths` 原写 "Hotspot sharing included"，与官方 500MB/day 上限冲突
- ✅ i18n：`compare/provider.html` 的拼装句碎片 **41 → 0**（全站 662 → 619），新增 41 个 `compare_provider__*` key（en/de 各 894 key 对齐）

**审核第一轮抓到并修掉的真问题**
- 守卫脚本自己有 2 个索引 bug（把 `compare/<国>/<品牌>/index.html` 的第 3/4 段当国名/品牌名）→ 之前两轮是假绿
- `%!g(int=20)GB`：`plans[].gb` **既有 int 又有 float**，Go 的 `%g` 只吃 float → 转换 partial 开头 `float .` 起手
- 「对比」区块没排除本品牌 → Airalo 页上变成 "Airalo 比自己便宜" → 加 `ne .key $provKey`
- 「无本地号码」的判据用了品牌类型（`$p.type`）而不是核实过的 `policy.voice`

**审核第二轮抓到并修掉的真问题（★ 数据层事实错误）**
- ★ **`500MB` 全站被当成 "Unlimited"**：`partials/country-stats.html` 写的是 `"gb" (int .gb)`，
  把 500MB 存的 `0.4883` 截断成 `0`，而 **0 是"无限"的哨兵值**。爆炸半径：全站 12 处 `where $rows "gb" 0`（7 个模板）
  把它选进无限套餐、`unlimitedCount` 把它数进「N unlimited plans」（`/networks/`、`/compare/`、`/guides/`、`/research/` 全中）、
  `/compare/<国>/` 的「重度用户推荐」可能推荐一个 500MB 试用装、`/tools/` 在"需要无限"时返回它
  → 修：聚合层 `gb` 改 float（哨兵语义不变、但变成真的）+ `unlimitedCount` 改按 `isUnlimited` 计数 +
  10 个文件的 `int .gb`/`parseInt(dataset.gb)` 判零改浮点 + 所有打印 `.gb` 的地方改走新 partial `plan-data-label.html`；
  并**新增守卫**：`data-gb` 与数据列的 unlimited 标注必须一一对应（400/400，另报 48 行 <1GB 的 MB 档）
- 竞品「更便宜」拿 500MB 试用装作依据（FAQ 写"$5.29 vs $0.51"，读起来像同类对比）→ 文案补上数据量口径：
  "Yesim's is $0.51, though that entry price buys 200MB"

**校验终态**：`validate.py` 0 error 0 warning · `check_css_sync.py` 501 类全在 · `check_i18n.py` 0 硬编码 / 894 key 对齐 ·
`hugo` **540 页 EN + 64 DE** · `check_output.py` **586 文件 / 3254 JSON-LD 块 · 无格式串泄漏** ·
`check_headings.py` **14113 h2/h3 · 0 bad** · `verify_provider_pages.py` **400/400 全过** ·
`audit_meta.py` provider-sub 400 页 0 违规（同时豁免了 hugo aliases 跳转壳页与所有语言的 404）

---

## 已完成（零回归边界守卫 + 修掉 54 个德语页的模板注释泄漏，2026-10-04 第二十一轮）

**这一轮解决的问题**：上一轮的守卫（`verify_provider_pages.py`）只盯 400 个品牌子页，但改造动的是
**共享组件**（`country-stats.html` / `head.html` / `plan-data-label.html`），下游是全站 584 页 ——
「本层全绿」推不出「别处没坏」。这一轮补上跨页型断言，并在过程中抓到一个真缺陷。

**★ 新发现并修掉的缺陷：54 个德语页把开发者备注印给了读者**
- 现象：`/de/compare/argentina/` 等 50 个国家页 + `de/guides|networks|research/` 的正文里，
  读者能直接看到一段 "TODO(de)：正文待翻译…"
- 根因：备注写成 `{{/* … */}}` 放在 **Markdown 正文**里。Hugo 只解析模板文件、不解析正文，
  Goldmark 把这段字当普通段落输出。`hugo` 退出码 0，**当时五重校验全绿**
- 修：① 注记搬进 front matter 的 **YAML 注释**（`#` 开头，解析器忽略），正文清空
  （`scripts/_fix_de_todo_comments.py` 一次改 54 个文件，改前备份到 `D:\esimsift\_backup_20261004_de_todo`）；
  ② `check_output.py` 新增**全站**模板残留扫描
- 附带修正：德语国家页正文块（`{{ with .Content }}`）里含一个**英文** h2
  「What <国家> eSIM prices reveal」，此前因那行备注而渲染出来 —— 现在整块跳过，
  `check_headings.py` 的 h2/h3 从 14113 降到 **14063**（−50，预期变化）

**新增守卫：`scripts/verify_no_regression.py`（零回归边界，三组断言）**
- **A 标记隔离**：`#reality` / `#hostnetwork` / `#tripcost` / `#trip-calc` / `#fit` / `#tradeoffs`
  只允许出现在品牌子页（`#verdict` / `#fup` 另允许国家 Hub）；反向也断言品牌子页
  **必须**带 `#verdict` `#plans` `#reality` `#tripcost` `#fit` `#faq`
- **B 全站不变量**：584 页逐页查「恰好 1 个 h1 / title 非空 / 无 `{{` `}}` `<no value>` /
  无 `%!x(...)` / 无空 `<h2></h2>` / JSON-LD 可解析」——本轮就是靠这条抓到德语页残留
- **C gb 哨兵跨页型**：把上一轮只在品牌子页做的 `data-gb` 一致性检查**扩到国家 Hub**
  （后者 15552 行，是上一版的盲区）
- **基线 + 字节级 diff**：`--write-manifest` 产出 `docs/regression-manifest.json`（584 页 sha256），
  下轮 `--diff` 即可知道具体哪几个文件变了；品牌子页视为预期变更，
  其余页型打 `★需确认`，`--strict-diff` 下非白名单变更即退 1
- **两个守卫都带 `--selftest`**，往临时目录注入反例，证明每条检查**真的会报错**
  （上一轮吃过「守卫自己有索引 bug、连报两轮假绿」的亏）

**交叉校验（顺带得到的正确性证据）**
品牌子页与国家 Hub 枚举的是**同一批套餐**：EN 侧 7776 = 7776 行、无限档 4127 = 4127、<1GB 档 48 = 48；
Hub 恰好是子页的 2 倍（50 国 × 8 品牌的全部档位）。全站合计 **23328 行 = 7776 + 15552**。
三个数各自相等 → 没有哪一层丢档。这条已写进方法论 §5.5。

**修复过程中的两个坑**
- `check_output.py` 若连 `}}` 一起扫，会撞上内联的压缩 Tailwind CSS（**390 个文件**命中，全假阳性）
  → 只扫 Go 模板的**开**定界符 `{{`，且先屏蔽 `<style>`/`<script>` 块
- 新守卫的「标记隔离」初版报了 **8 个假阳性**：`id="tradeoffs"` 匹配上了品牌详情页既有的
  `id="tradeoffs-pending"`，而 `esim-providers/<品牌>/` **本来就**有自己的 `#tradeoffs`（"Price record"）
  → 标记一律带**收尾引号**，且报出来的每一处都先读渲染后的 HTML 核实，确认是既有独立区块后才写进白名单

**校验终态**：`validate.py` 0 error 0 warning · `check_css_sync.py` 501 类全在 ·
`check_i18n.py` 0 硬编码 / 894 key 对齐 / 0 未定义（拼装句碎片 619）· `hugo` **540 页 EN + 64 DE** ·
`check_output.py` **586 文件 / 3254 JSON-LD 块 · 无格式串泄漏 · 无模板残留** ·
`check_headings.py` **14063 h2/h3 · 0 bad** · `verify_provider_pages.py` **400/400** ·
`verify_no_regression.py` **A/B/C 全过**（584 页 · 无限 12381 / 计量 10803 / <1GB 144 行）·
`audit_meta.py` provider-sub 0 违规
`package.json` 的 `check:output` 已把两个守卫接进 `npm run build`（+14s）。

**诚实说明**：`git` 最近一次提交（`10-3-4`）早于德语轮次，且 `content/de/`、`i18n/`、
本层新增的 partial 仍是未跟踪状态 —— **没有可用的「改造前」快照**，所以做不出字节级前后对比。
本轮改为「A/B/C 断言 + 存下改造后基线供下轮比对」，不宣称"已验证零回归"。

---

## 已完成（品牌子页外部佐证链接 + 控件收成天数选择，2026-10-04 第二十二轮）

用户针对 `/compare/<国>/<品牌>/`（400 页，一次改全站）提了四条：

1. **`#reality` 的 H2 每国一模一样、且不含长尾意图词** → `What the plan label leaves out`
   改成 `{{ .brand }} {{ .country }} eSIM hotspot 5G and fair-use rules`
   （400 页实测如 `Holafly Japan eSIM hotspot 5G and fair-use rules`）：品牌 + 国家 +
   该区块真正回答的三个意图词，且不含 `,;:—–`（`check_headings.py` 的硬禁标点）。
2. **列了运营商数据却没有可核实的链接** → `#hostnetwork` 每张运营商卡加官方站点 / 覆盖地图外链
   （新建 `data/refs.toml`，50 国 × 146 条），区块尾加该国 Ookla Speedtest Global Index 链接
   （**复用** `networkreports.toml` 的 slug 例外表，不另抄一份）。国家 Hub 的运营商卡同步接上。
3. **套餐表的多维排序器**（$/GB / 价格 / 每天 / 数据量 / 有效期）→ 收成**只按行程天数筛**
   （Any / 3 / 5 / 7 / 10 / 14 / 21 / 30）。
4. **页内计算器的数字输入框** → 同一个**天数下拉**；两处共用模板里的一个 `$dayOpts`，
   口径必须一致，否则同一趟行程会在同一页给出两个答案。

国家 Hub（`compare/single.html`）的同类排序器一并移除、天数 chip 统一成同一组值、
运营商卡加同一批外链 —— 两个页型不再各说各话。

**新增工具**：`scripts/verify_external_refs.py`

- 判定分四类：`2xx` ok ／ `403·412·429` **bot 墙（站点存在，保留）** ／
  `404·410` **死链（唯一让脚本非 0 退出的一类）** ／ `000·5xx` **本机不可达（报告不删）**。
- `--data-only` 离线跑：断言 `refs.toml` 每个 key 都在 `carriers.toml` 有同名 profile
  （孤儿 = 永不渲染的死重量），并点名列出「没配到链接」的 profile。
- 网络检查**不进 `npm run build`**（离线构建必须能过）。

**本轮抓到的真问题**（靠「分层判定 + 实测」捞出来，详见 `docs/provider-page-optimization.md` §3.9 / §7）：

- ★ i18n 值加了 `{{ .brand }}` 占位符，但**模板调用处没跟着加 `dict`** → H2 印出
  `<no value> <no value> eSIM hotspot 5G and fair-use rules`。`hugo` 退出码 0，
  只有 `check_output.py` 的 `<no value>` 扫描拦得住。
- ★ 冰岛运营商域名拼错：`noa.is`（不存在）→ `nova.is`（200）。
- `digicelfiji.com` 已 404 → 换 `digicelgroup.com/fj`（200）。
- `yoigo.com` / `yoigo.es` 双双 404（品牌并入 MasMovil 后独立官网关闭）→ 删除，宁缺勿造。
- ★ 全量扫 197 条报 49 条「不通过」，其中**只有 3 条是真问题**，其余 46 条是
  `att.com` / `t-mobile.com` / `bell.ca` 这类 bot 墙与 `jio.com` 这类本机网络阻断。
  **没有分层判定，这轮会删掉 46 个正确的链接、把唯一那个拼错的域名留在页面上。**
- 国家 Hub 排序器的 `dataset.perGB`（应为 `pergb`）取到 `undefined`，比较函数返回 NaN，
  排序**静默失效**（原顺序恰好正确所以看不出来）；移除该控件时顺手结清。

**校验终态（全绿）**：`validate.py` 0/0 · `check_css_sync.py` 全在 · `check_i18n.py`
0 硬编码 / **902 key 对齐**（en = de，本轮 +8）· `hugo` **540 EN + 64 DE** ·
`check_output.py` 586 文件 / 3254 JSON-LD 块 / 无格式串泄漏 / **无模板残留** ·
`check_headings.py` **14063 h2/h3 · bad 0** · `verify_provider_pages.py` **400/400** ·
`verify_no_regression.py` **A / B / C 全过** · `audit_meta.py` 退 0
（provider-sub 400 页 T 48/51/54、D 123/130/140）·
`verify_external_refs.py --data-only` 146 refs ↔ 147 profiles（缺 1：ES Yoigo，已知）。

**基线刷新**：`docs/regression-manifest.json` 已重建为第二十二轮状态 ——
变更 **500**（400 品牌子页 + 100 国家 Hub）、新增 0、删除 0、**无其它页型外溢**；
重建后自比对 **584 页逐字节相同**，顺带再次证明本站构建是确定性的。

---

## 已完成（品牌子页控件去下拉化 + 三个模糊模块改量化 + 计数口径 + 免责声明，2026-10-04 第二十三轮）

用户分两批提了 4 + 4 条，全部落在同一批页面（`/compare/<国>/<品牌>/` 400 页，一次改全站）。

**第一批（交互 + 内容 + 计数）**

1. **「行程长度」和「根据您自己的日期定价」两处天数控件都不要下拉框，直接把天数摆出来点选**
   → 两处都改成 `.chip` 按钮组，且**取值不再写死**：由 `$myRows` 的 `days` 去重排序推导；
   档位多于 12 个时按 `1 2 3 4 5 7 10 14 21 30 60 90` 阶梯取「最小的 ≥ 目标的真实档位」。
   实测 Roamic 日本 → `1 2 3 4 5 7 10 14 21 30`，Holafly / Airalo 日本 → `3 5 7 10 15 30`。
   两处共用同一个 `$dayOpts`，口径一致。
2. **`#fit`（Should you buy…）与 `#tradeoffs`（Where … wins and loses）太单薄、对用户没意义**
   → `#tradeoffs` 从「印 `providers.toml` 的品牌套话」（同品牌 50 国一字不差）**整体重写**为
   「本页数据推导的国别量化对比」：优点/缺点各若干条，每条都带本国的数字或核实过的政策字段。
   `#fit` 加两条硬判据（盈亏平衡天数 `$beDays`、最短行程 `$minDays`）。
   实测 Holafly 日本：优点 4 条 + 缺点 7 条；Roamic 日本：优点 5 条 + 缺点 3 条。
   **全站 400 页条目下限已守住：优点 ≥3 且缺点 ≥2，零页面触底。**
3. **「All 6 Holafly Japan plans 为什么是 6 个计划？应该各天数档位累加」**
   → 做了全站审计：**400 页的「All N」全部正确**（H2 数量 = 表格行数 = 数据层档位数，
   逐页零不一致）。误解源于 H2 只印裸数字、而下方天数列表当时是**写死的通用列表**，读者无法自核。
   据此两处一起改：① H2 下加**口径说明行** `{N} plans · {M} trip lengths · {a} to {b} days`；
   ② 守卫加第 12 项「计划数三处对账」（H2 = 价格表行数 = `offerCount` = 说明行）。
4. **其它同类型页面一起改** → 以上全部落在 400 页上，不是单页修补。

**第二批（数据准确性 + 合规）**

5. **热点分享 / FUP 实际限速阈值 / 5G 是否支持 —— 三项必须严格按实际**
   → 三点都从「品牌文案」改为「核实过的事实」：
   - **热点**：新增**优点**条目 `tradeoffs_w_hotspot`（`policy.hotspot == "allowed"` 时印出实际额度），
     与原有的**缺点**条目 `tradeoffs_l_hotspot`（`capped` 时印出额度）对称 —— 同一件事两边都有位置。
   - **FUP 阈值**：旧判据是 `not .fup_allowance`，而八个品牌的该字段**全都有值**
     （Holafly 的是字面量 `"No GB figure published"`），**这条缺点从来没触发过**。
     改成按数值分档：额度里抠出日数字且 < 6GB/天 → 「约 N GB 之后掉到 M」；
     文案以 `no` / `not` 开头 → 「限速点不公开」；只写「按套餐公布」→ **不列为缺点**（那是透明度加分项）。
   - **5G**：判据是**宿主网络的制式**（`carriers.toml` 的 `tech`），不是品牌宣传。
     实测 Fiji 正确显示 `4G only | 8–80 Mbps | Digicel Fiji`，且 Holafly Fiji 页**没有**
     「5G on all N host networks」这条优点 —— 落后国家只有 4G 的情况按实际走。
6. **首屏价格旁加「价格可能变动，以官网为准」的免责声明，且品牌名不能写死**
   → Hero 价格下方加一行 `compare_provider__price_disclaimer`，品牌名走 `{{ .brand }}` 占位符。
   实测 Holafly / Ubigi / Roami 页分别印出各自品牌名。
7. **结构化数据（JSON-LD）必须要有** → 本来就有，本轮复核未动：每页 6 块
   （`BreadcrumbList` 4 级 / `Organization` / `WebSite` / `Product` + `AggregateOffer`
   逐套餐 Offer / `WebPage` / `FAQPage`），全站 3254 块、7776 条 Offer，与价格表行数一一对齐。
8. **同类页面全站统一** → 同 1–4。

**本轮抓到的真问题**（全部是「口径错了但构建全绿」，详见 `docs/provider-page-optimization.md` §3.12 / §7）：

- ★★ **「A 比 B 便宜」拿不同流量档比**：价差按**绝对差额**取最大值，必然选中
  「我方大流量档 vs 对手 1GB 试用装」。实测 Roamic 日本 30 天档 10GB/$9 被拿去跟
  Ubigi 的 1GB/$4 比，印出「便宜 $5.00」—— 10 倍流量差被写成纯粹的价格劣势。
  改成同类比同类（计量档要求对手流量 ≥ 我方；无限档要求行程长度精确匹配）。
- ★ **价格数字与品牌名来自两套计算**：`l_unl` 用 `$cUnlPerDay`（全国最低无限日单价 $1.50）
  \+ `$rivalKey`（**最低入门价**品牌 Roami）拼成一句。日本实测：$1.50 属于 Ubigi，
  句子却写 "from Roami"（Roami 自家 $2.40）。改成同一遍循环同时记住价和主人。
- ★ **`l_upsell` 在 Roamic 日本误报「15 天没有匹配档位」**：判据用了「最便宜**可覆盖**档的 days」，
  而 Roamic 明明有 1–30 天全档位。改成查「是否存在 `days == 行程长度` 的档」。
- ★ **优点列里写了缺点**：`tradeoffs_w_unl` 的文案把「对手更便宜」塞进「优势」栏。
- ★★ **`hugo` 构建失败却报「全绿」**：命令写成 `hugo --quiet … 2>&1 | head -20`，
  `hugo` 的报错走 stdout，`| head` 提前关管道让它拿到 SIGPIPE，`$?` 取到的是 `head` 的 0。
  **任何带管道的构建命令都不能用 `$?` 判断成败。**
- ★ 天数按钮里有页面买不到的档位（写死的 `3 5 7 10 14 21 30` 与 Holafly 真实的
  `3 5 7 10 15 30` 对不上，读者点「14 天」看到空列表会以为漏了套餐）。
- 同页两组天数按钮互相串组（`document.querySelectorAll('[data-days]')` 是全局选择器）。

**新增守卫**（`scripts/verify_provider_pages.py` 从 11 项扩到 13 项）：
第 12 项「计划数三处对账」、第 13 项「天数按钮无假档位」（按钮值必须 ⊆ 表里真实档位）。

**校验终态（全绿）**：`validate.py` 0/0 · `check_css_sync.py` 499 类全在 · `check_i18n.py`
0 硬编码 / **928 key 对齐**（en = de，本轮 +26）· `hugo` **540 EN + 64 DE** ·
`check_output.py` 586 文件 / 3254 JSON-LD 块 / 无格式串泄漏 / **无模板残留** ·
`check_headings.py` **14063 h2/h3 · bad 0** · `verify_provider_pages.py` **400/400**
（含计划数对账 400/400、天数按钮 398/400）· `verify_no_regression.py` **A / B / C 全过**。

**基线刷新**：`docs/regression-manifest.json` 已重建为第二十三轮状态 ——
变更 **400**（全部是 `provider_sub`）、新增 0、删除 0、**无其它页型外溢**；
`--strict-diff` 复跑 **584 页逐字节相同**，再次证明构建确定性。

**收尾（同日）· 最后更新日期改为构建当天的系统日期**

`esim-comparison.html` §9.4 要求「最后更新日期每页可见，且与 `dateModified` 一致」。
此前这 6 个落点都由 `country-stats` 的 `checkedDate`（= `data/plans/*.toml` 的 `checked`，
价格核对日）驱动，页面显示 `Sep 30, 2026`。

改为模板顶部的 `{{ $updatedNow := now }}` / `{{ $updatedDate := time.Format ":date_medium" $updatedNow }}`，
一次覆盖 Hero 徽章、价格免责声明、配图 figcaption、套餐表脚注、页尾信任栏、`WebPage.dateModified`。

- **只改渲染层，不动数据层**：`checkedDate` 被 15 处页型共用（国家 Hub / guides / index /
  networks / research / country-card / head / catalog.json / llms.txt），改数据层等于全站换日期。
- `dateModified` 原来的 `{{ with $stats.checked }} … {{ end }}` 守卫随常量日期一起去掉
  （留着就是永不触发的假分支）。
- 实测：**400 个品牌子页**显示 `Oct 4, 2026` + `dateModified 2026-10-04`，`Sep 30, 2026` 残留 0；
  其余页型保持 `Sep 30, 2026`，零外溢。（`networks/*` 12 页本来就用 `now`，属既有写法。）
- **代价**：产物带构建日戳 → 同一天内重复构建仍逐字节一致，跨天首次构建必然全量变更 400 页，
  需刷新一次基线。见 `docs/provider-page-optimization.md` §3.13。

---

## 已完成（品牌 Hub 页 8 页 SEO/UX 优化 + 交互计算器，2026-10-04 第二十四轮）

用户上传长文点名优化 `/esim-providers/airalo/`，并明确「其他的品牌页面也是一样的优化方式」。
本轮把该页模板从 540 行扩到 1215 行，**只动品牌 Hub 页型**；规范见
`docs/provider-page-optimization.md` 附录（§9–§13）。

**诊断**：页面自己算得出「Airalo 在 50 国中 0 国最便宜」，`<title>` 却在复述品牌营销话术
「Unlimited 5G From $9.50」—— **标题与本页数据互相打脸**；且缺热点 / 5G / 公平使用
三项核心参数、缺「不便宜那该去看谁」的替代引导、缺互动工具。

**新增 6 个区块**（模板从上到下）

| id | 内容 | 数据源 |
|:--|:---|:---|
| `#reality` | 热点分享 / 公平使用阈值 / 充值 / 速度与 5G | `[<brand>.policy]` + `carriers.toml` |
| `#whobeats` | 替代推荐表：国家 / 本品牌最低价 / 更便宜竞品（链站内 provider 页）/ 差额 % | `provider-alts.html` |
| `#network` | 5G 实况：N/M 市场有 5G、纯 LTE 市场列表（链 `/networks/<slug>/`） | `carriers.toml` |
| `#headtohead` | 按 `cheapest` 距离**自动**选出的两个最接近对手 + 各 3 条差异 + 对比页链接 | `provider-agg.html` |
| `#calc` | 行程计算器：目的地 + 天数 + 每日用量 → 推荐档位与结论 | `country-stats.html` |
| `#reading` | E-E-A-T：评价怎么读 / 区域指南 / 数字来源 | i18n + `$totalPlans` |

另：Hero 补「最后更新日期 + 价格免责声明」；FAQ 补 3 问（热点 / 5G / 谁更便宜）；
Product JSON-LD 补逐市场 `offers`（12 个最便宜市场）。

**新建 `layouts/partials/provider-alts.html`**（117 行）—— 把「同类比同类」（事故 #23）
固化成四层匹配：无限档只对无限档 → 同 `(gb, days)` → 对手数据量 ≥ 我方 → 退回
「入门对入门」并**显式标记**（UI 上不装作同类对比）。

**标题口径（用户本轮裁定）**：`<title>` **不放套餐数量、不放价格**
（沿用 2026-10-04 既定规则 —— 数字会随数据过时）；套餐数改由 `description` 与 **H1** 承担，
H1 由 `$totalPlans` 构建期渲染，永远与数据层一致。8 页实测 title 49–53 字符、
desc 126–139，`audit_meta.py` 的 provider 类 **0 违规**。

**Trustpilot：只给档案链接，不印分数**（用户本轮确认）

- 同一品牌在不同**地区域名**下是**不同值**（Airalo 3.9 / 4.0 / 4.1），本机抓取全被反爬墙拦（403）。
- 8 家已逐个核实档案 URL；**Ubigi 是 `cellulardata.ubigi.com`，不是 `ubigi.com`**。
- **Roami 无档案**（对 trustpilot.com 做域名过滤搜索只返回 `roamic.com`）→ 字段留空，
  模板走 `reading_reviews_none` 分支如实说明。其自家博客宣称的 4.9 分、与第三方评测引用的
  「13k+ 条评价」恰好等于 **Roamic** 的 13,683 条 —— 疑似两家混淆，不采信。

**i18n**：+76 key（en/de 同值同序）；`check_i18n.py` 引用 998 个 key、未定义 **0**。

**本轮踩的坑（详见 §13，含计数器）**

- ★★ **Hugo 的 `append` 会把切片实参展开并入** —— 计算器三元组被压成 51 个裸数字，
  `json.loads` 照常通过、全部校验绿灯，**页面静默出错**。改用 dict 存一条记录。
- 守卫把**合法嵌套 JSON** 的 `}}` 判成模板残留（16 处误报）→ 扫描前先挖掉数据块，
  并把数据块纳入 `json.loads`，**把误报源变成一处真实检查**。
- `$mk4gNames` 先用后定义导致构建失败 → 派生量统一提到文件顶部。
- i18n 冠词写死 `a {{ .brand }}` 渲染出 "a Airalo" → 去掉冠词改写句式。

**校验（八项全绿）**：`npm run build` 通过；`check_output` 586 文件 / 3254 JSON-LD 无泄漏；
`check_headings` 14199 h2/h3 bad 0；`verify_provider_pages` 400/400；
`verify_no_regression` A/B/C 全过 + **14 项自测全过**（本轮新增 3 项）。

**基线刷新**：`docs/regression-manifest.json` 已重建 ——
期望形态是**仅 `provider_hub=8` 变更，`provider_sub=400` 逐字节不变**
（实测正是如此：变更 8、新增 0、删除 0）。

---

## 已完成（sitemap 日期口径统一 + 产物域名卫生守卫，2026-10-04 第二十五轮）

**触发**：用户问「更新了品牌数据，为什么 sitemap 里品牌 URL 的日期没变成今天？
sitemap 前面带端口对不对？国家-品牌页的日期要不要跟着更新才合 Google SEO？」

**诊断结论**：不是「没更新」，是**同一张页面自己打架**（实测三方对照）：

| 页面 | 页面可见 | JSON-LD `dateModified` | sitemap `<lastmod>` |
|:---|:---|:---|:---|
| `/esim-providers/alosim/` | Oct 4 | （当时没有） | 2026-09-30 |
| `/compare/united-states/alosim/` | Oct 4 | 2026-10-04 | 2026-09-30 |
| `/compare/poland/` | Sep 30 | — | 2026-09-30 |

根因是第二十三轮把 6 个日期落点接到了 `now`（构建日），而 sitemap 读的是数据核对日
`checked`。而「2026-09-30 抓的价格旁边印 Prices verified Oct 4」**不是口径差异，是不实陈述**；
且 `lastmod` 每次部署都翻新会被 Google 整体忽略。

**改动**

1. **新建 `layouts/partials/provider-checked.html`** —— 按**品牌**取 `data/plans/<key>.toml`
   的 `checked`，三种口径：`key+iso`（品牌×国家子页）/ `key`（品牌 Hub）/ `keys`（A-vs-B 对比页）。
   这一格正是第二十三轮缺失的：当时只有「构建日」和「国家级 `checked`」两个选项，
   于是错选了前者；补上品牌粒度后就不必二选一了。
2. **统一日期来源**：`compare/provider.html`（6 个落点）、`esim-providers/single.html`
   （可见文案 + **新补的 Product `dateModified`**）、`sitemap-urls.html`（品牌优先解析顺序）。
   日期缺失时不写 `dateModified`，不编日期。
2b. **★ 品牌 Hub 拆成两个日期**（用户确认后实现）：Hub 页内容 = 价格（`data/plans`）
   **加** 品牌档案（`data/providers.toml` 的简介 / 热点 / FUP / 充值 / 折扣码）。
   只改档案时页面确实变了，日期必须动；但页面上的价格类文案写的是
   「list prices **as checked on** &lt;d&gt;」，**只描述价格**。于是：
   | 文案 | 日期来源 |
   |:---|:---|
   | 「Last updated &lt;d&gt;」（通用） | `max(价格核对日, 档案核对日)` |
   | 「list prices as checked on &lt;d&gt;」/「price database … rebuilt &lt;d&gt;」 | **只取价格核对日** |

   合成一个日期就会写出不实陈述（档案今天改、价格上周核，却印成「prices as checked on 今天」）。
   为此给 `data/providers.toml` 8 个品牌顶层块补了 **`profile_checked`**（统一 `2026-10-04`，
   依据：policy 块与 trustpilot 链接均为 2026-10-04 核实，见文件内注释）。
   子页的 6 个落点文案**全是价格专属表述**，所以子页不带档案日期，维持单一口径。
3. **`sitemap-urls.html` 解析顺序改为**：品牌页（Hub / 子页 / vs）→ 国家页 → front matter
   → 全站兜底。品牌粒度必须排在 `.Lastmod` 之前，否则 Hugo 的 `:git` 提交日会盖掉数据日。
4. **★ 新增 `scripts/check_dates.py`**（接入 `check:output`，八项 → 九项）：
   A 域名（`public/` 不得含 `localhost`、sitemap host 必须等于 baseURL）、
   B 日期（三处一致；`/guides/*`、`/research/*` 放宽为只查 `lastmod == dateModified`
   —— 它们的文章日期与数据快照日本来就该不同）、
   C 完整性（sitemap 声明的每个 URL 都必须有产物）。
5. **新增 `scripts/bump_checked.py`**：数据更新后一条命令盖章 `checked`
   （`--brand` / `--countries` / `--date` / `--dry-run` / `--show`），三处日期同时前移。
6. **`hugo.toml`**：删掉一个**无效的假保护**（`[server] renderToMemory` —— 实测该键
   不存在于 `[server]` 配置段，写进去产物照样落盘 928 个文件）；改为在
   `package.json` 的 build 上加 `--cleanDestinationDir`。

**实测事故**

- ★★ **手敲的 `hugo server` 把 `localhost:55171` 写进了 136 个产物**（含 canonical 与 sitemap），
  且 `public/esim-providers/` 整个目录是空的（写一半被中断）。原因：1313 被占，Hugo 自选随机端口，
  而该 server 没有 `--renderToMemory`。**`[server]` 配置段只有 `redirects`/`headers`，没有
  `renderToMemory` 这个键** —— 只有命令行 flag 生效，「写进配置就防住了」是错觉，已删除。
- **vs 页被兜底口径带跑**：sitemap 退回「全站最新快照」后，只给 alosim 的 US/PL 盖了 10-04，
  就让 **28 张 A-vs-B 对比页**的 `lastmod` 集体前移而页面文案纹丝不动。
  → 补 `keys` 口径，让 sitemap 与 `vs-agg.checkedDate` 用同一个聚合方式。
- **`--cleanDestinationDir` 的新风险**：先清空再重建，构建被 SIGTERM 中断后 `public/` 停在
  「已清空、未写完」状态，**所有既有校验都不报错**。这就是断言 C 存在的唯一理由（当场报出 44 个缺失 URL）。
- 两个新守卫都做了**反向测试**（造违规 → 必须失败 → 还原）。断言 C 直接在真实损坏产物上验证。
- **守卫自己误报 8 条**：断言 B 第一版把「Last updated」也当成「价格核对日」去比，
  于是 8 个品牌 Hub（通用日期 Oct 4、价格日期 Sep 30，**两者不同是刻意的**）全被误判。
  → 把日期文案拆成两组（通用组 / 价格专属组）分别比对。这正是「反向测试 + 逐条读产物」
  的价值：误报会逼你把规则写精确，而不是把检查改松。

**校验**：`npm run build` 九项全绿；`check_dates.py` 扫描 brand_hub 8 / prov_sub 400 /
country_hub 51 / vs 28 / index 2 / edit 15，域名 / 日期 / 完整性三断言 0 违规；
反向测试 4 次（A、B-价格组、B-通用组、C）全部按预期失败。

**基线**：`docs/regression-manifest.json` 已重建。终态 diff = **变更 8（provider_hub）+ 0 + 0**，
`provider_sub=400` 逐字节不变。

---

## 已完成（套餐总表斑马纹去绿 + footer 增设 Regional guides 列，2026-10-04 第二十六轮）

**① 套餐总表斑马纹在暗色渲染下发绿 → 换中性近白**（用户反馈 /compare/united-states/
「All … eSIM plans compared」斑马纹是深绿色、数据看不清；同页 FUP 表正常）。

- **根因（截图实测复现）**：斑马纹 `#eef2f7` 本身是中性浅灰（亮色渲染完全正常），
  但它带蓝青色调，在浏览器**强制暗色**（Chrome force-dark / Dark Reader）下被映射成
  **深青绿**，数百行大表整片发绿。用户看到的「深绿」来自暗色渲染，不是 CSS 写错。
- **修法（只动套餐总表，FUP 表等其它 `.table-pro` 原样）**：
  - `layouts/compare/single.html` 套餐总表加 `table-soft` 类；
  - `assets/css/main.css` 新增 `.table-soft tbody tr:nth-child(even)` = `#f7f8fa`
    （中性近白，hover `#f0f2f5`），写在 `.table-pro` 斑马纹规则之后、同特异性后者胜出。
  - 判据：**中性色（无蓝青偏）在 force-dark 下映射为中性深灰，不发绿**；
    亮色下条纹也更轻。已在本地构建产物上用亮/暗两种渲染截图验证。
- 注意：`.table-pro` 全局规则**没有改**——用户明确「FUP 模块不动」。

**② footer 增设「Regional guides」列**（用户要求：5 篇区域指南保留页头不动，
同时放到 footer 提升入口可见性）。

- `layouts/partials/footer.html`：在「Popular matchups」与「Data & research」之间插入
  Regional guides 列 —— 5 篇区域指南（复用页头 `partials_header__best_*` key，
  `site.GetPage` 门控缺页跳过）+「All guides →」；网格 `lg:grid-cols-7` → `lg:grid-cols-8`。
- i18n：`partials_footer__regional_guides` / `partials_footer__all_guides` 两个 key
  **en/de 成对新增**（只加一边 `check_i18n.py` 直接失败；de 曾因重复定义炸过一次构建
  —— TOML 重复 key 是**构建期报错**，不是静默覆盖）。
- 教训：**TOML 重复 key = 构建失败**（`key is already defined`），报错行号即文件头，
  修之前先 `grep -n` 确认只定义了一次。

**校验**：`npm run build` 九项全绿（hugo 136s）。产物抽查：套餐总表
`class="table-pro table-soft"`、FUP 表保持 `table-pro`；footer 六条链接全部命中
`public/guides/*/index.html`；DE 页 footer 出现「Regionale Ratgeber / Alle Ratgeber」。

**基线**：`docs/regression-manifest.json` 已重建（footer 是全站组件，本轮 584 页
产物均含 footer 变更 + 51×2 个国家 Hub 含表格 class，属预期；结构守卫 A/B/C 与
品牌子页 13 项全绿）。

---

## 已完成（点行乱跳 bug + 斑马纹「深色」根修 color-scheme，2026-10-04 第二十七轮）

**① 点表格任意行 → 数据乱跳（真 bug）**：`compare/single.html` 过滤脚本用裸
`querySelectorAll('[data-days]')` / `'[data-prov]'` 选过滤 chip，但每个 `<tr>` 也带
`data-days` / `data-prov`（供 apply() 读 dataset 排序用）→ **表格行被误选成过滤按钮**，
点任意行 = 把该行有效期天数当过滤条件触发 apply() 重排 + 隐藏行。修法：选择器限定
`.chip[data-days]` / `.chip[data-prov]` / `.chip[data-unlim]`（三处，加注释防回归）。

**② 斑马纹「还是深色」根修**：第二十六轮换成中性 `#f7f8fa` 没用——浏览器**强制暗色渲染**
（Chrome auto dark 等）会把一切浅色一律压暗，换什么颜色都逃不掉。正解：站点声明
`color-scheme: only light`（`head.html` 加 `<meta name="color-scheme" content="only light">`
+ `main.css` `html{color-scheme:only light}` 双保险），告诉浏览器「本站仅亮色设计」→
强制暗色跳过整站。实测 `--force-dark-mode` 下整站保持亮色、斑马纹浅灰可读。

**教训**：用户视角的「颜色不对」先确认他的渲染环境（暗色模式/扩展），别急着改色值；
`[data-x]` 裸属性选择器在有服务端渲染属性复用时必须限定类名。

---

## 已完成（折扣码全量补齐 + deals 页决策化重设计，2026-10-04 第二十八轮）

**① View plan 换行修复**：`.btn-out` 缺 `whitespace-nowrap`（`.btn-mini` 一直有），
表格窄列里按钮文案折行。补上即修，全站出站按钮受益。

**② 折扣码数据全量补齐（8/8 品牌全有实码，此前仅 3 家）**：
- 研究底稿：`docs/promos/roami.json` **新建**（web20 = 官网全站公示，整单 20% off，
  **零门槛**——官方 India/US/UK 页均为 "20% off your order"，无新客/最低消费/套餐限制）；
  `promos.json` 聚合加 roami 并**置首**（brand_count 16→17，offer_count 121）；
  `promos_all.csv` 追加一行（21 列对齐）。
- 站点唯一事实源 `data/providers.toml`：8 品牌全配 promo_*。新增字段
  `promo_rank`（排序）· `promo_audience`（all/new/existing/conditional）·
  `promo_scope` · `promo_min_spend` · `promo_bestfor`（决策指引）·
  `promo_alts`（备用码 [{code,label,audience,pct}]）· `promo_unconditional`（仅 roami）。
  头筹码：roami web20(20) / saily VEEPEE25(25，官方合作页 2026-10-04 WebFetch 实测在线) /
  yesim DREWDEAL(20) / airalo NEWTOAIRALO15(15 新客, 上限 $100) / alosim ESIMTWEAKS(15) /
  ubigi PROMO15(15 仅无限档, 官方) / roamic FYESIM10(10) / holafly MYESIMNOW5(5, 官方)。
  **promo_expires 空字符串 = 官方未标过期日，页面显示 no expiry published，不编日期**
  （废掉旧的 2027-12-31 占位）。

**③ deals 页重设计（决策型折扣码聚集地）**：
- 卡片区：排名徽章（#1 = Best overall — no conditions）+ 适用人群 chip +
  **Best for 决策指引行** + scope/无过期披露 + **备用码块**（含 audience 标签）。
- **新增决策矩阵表**（①b）：5 种用户情境 → 构建期从数据推导最优码
  （零门槛=web20 / 最大头条=VEEPEE25 / 新客首购 / 回头客 / 无限流量），
  `promo_alts` 与头条码一起参加选优。竞品只列码，这张表给的是决策。
- FAQ 新增两条数据驱动问答（零门槛码是谁 / 最大长期折扣是谁）。
- 无码品牌区随 8/8 有码自动消失（`$noCode` 为空 → 区块跳过，逻辑无需改）。
- i18n 19 个新 key，en + de 成对（de 暂英文占位，与该前缀既有状态一致）。

**判据沉淀**：折扣码页的 SEO 价值不在「码全」，在「帮用户选码」——情境 → 码的映射
（构建期从条款字段推导）是竞品没有的价格库级增益；**官方未标过期日就不显示过期日**，
编日期 = 第二轮「Sep 30 旁边印 Oct 4」同类不实陈述。

---

## 已完成（翻盘表用户化重写 + Roami 零门槛醒目高亮，2026-10-05 第二十九轮）

**用户反馈**：① 翻盘表「Cheapest in (no code) 1/50」「Cheapest in (with code) 2/50」用户看不懂；
② Roami 是主推品牌，其零门槛条款（无最低消费/无新客限制/无套餐类型限制/每单都能用）必须突出醒目展示（英文）。

**① 翻盘表重写**（`layouts/esim-deals/list.html`）：
- 表头改为**两行分组头**：跨列大标题「In how many of the 50 countries we track is this brand
  the cheapest option?」+ 两个子列「No code needed / With the code applied」——表头本身就是一个问句，
  单元格就是答案。
- 单元格 `1 / 50` → **`1 of 50 countries`**（自带单位，脱离表头也能读懂）；两列价格合并为一列
  `$1.99 → $1.59`（列表价 → 用码后）。
- 新增**变化标记**：折后多赢的国家显示 `+1 more` 绿色徽章，无变化显示灰色 `no change`
  ——直接回答「这个码到底有没有用」。
- 表下新增**读表说明**（How to read this table）：用一句话解释两个数字分别怎么算、
  `1 → 2` 与 `no change` 各是什么意思。
- 卡片底部与无码区同款文案统一为 `Already the cheapest option in N of 50 countries we track`。

**② Roami 零门槛高亮块**（数据驱动，非写死）：
- `providers.toml [roami]` 新增 `promo_uncond_short`（一句话版）+ `promo_uncond_points`
  （四条 head/sub：No minimum spend / No new-customer restriction / No plan-type restriction /
  Every order qualifies）。
- 卡片在码按钮正下方渲染**深绿标题条 + 品牌浅底 2×2 对勾清单**（`border-brand-500` 边框 +
  `bg-brand-600` 标题条，全卡视觉焦点）；决策矩阵第一行 note 同步换成零门槛短句。
- 渲染条件 `promo_unconditional && promo_uncond_points`——未来其他品牌若也拿到零门槛码，
  填字段即自动获得同款高亮。

**i18n**：删 5 个废弃 key（`cheapest_in_no_code/with_code/cheapest_plan_list/after_code/cheapest_provider_in`），
新增 13 个（flip_* / zero_conditions_head / already_cheapest_in 等），en + de 成对，key 对齐 1035 = 1035。

**校验**：`npm run build` 九项全绿；截图验证卡片高亮块与翻盘表渲染。基线已重建——
**注意**：本轮 diff 出现 `networks/* 12 页`，根因是 `layouts/networks/single.html:115` 的
`Updated` 徽章取 `now`（构建日），**每天构建都会变**，属既有设计（注释言明与数据快照
checkedDate 刻意分离），但会让回归基线日日失真 → 见待办。

---

## 已完成（deals 页新增「参数总表」，客观公正版，2026-10-05 第三十轮）

**用户问**：要不要加一张把每个品牌折扣参数横向对比的总表？会不会冗余？重点推 roami 但要客观公正。

**判断：不冗余——前提是它做卡片做不到的事（同参数跨品牌对齐）**。页面四表分工明确：
卡片=单品牌叙事 / **参数总表=横向比参数（本轮新增）** / 决策矩阵=情境选码 / 翻盘表=价格数学。
总表刻意**不放价格**（翻盘表负责），避免两张表打架。

**设计（8 列，`layouts/esim-deals/list.html` 新区块，位于卡片之后、决策矩阵之前）**：
Provider（logo + 官方/第三方徽章 + 出处域名）| Best code | Discount | Who qualifies |
What it covers | How often | Expiry | Restrictions（限制逐条列出；零限制渲染绿色对勾 +
"None — no strings attached" + 无最低消费/无客户限制/无套餐限制说明）。
**排序规则透明可审计**：限制条数升序 → 折扣降序 → promo_rank；用复合字符串键
`printf "%02d%04d%02d"` 实现（Hugo `sort` 只支持单键）。表下两段说明：
*How this table is ordered*（排序规则 + "Not stated" = 官方没写就不编）+
*Which row is yours*（怎么选：已定品牌看那行 / 未定品牌选零限制行）。

**客观公正的落点**：所有限制逐条可追溯 `docs/promos/*.json` 的
source / confidence / uses / min_spend / max_discount / stackable 字段——
Saily 25% 需走 Veepee 合作链接（官网 WebFetch 实测）、Yesim DREWDEAL 为第三方博客码
（2026-09-10 后未复测）、Airalo 新客 + 每账号一次 + $100 上限 + 不可叠加、
Ubigi 仅无限档 + 倒计时限时、aloSIM 第三方 + 不与 aloCASH 叠加。
**Roami 的客观赢法**：唯一「零限制 且 20%」的码——Holafly 结构上同样零限制但只有 5%，
其他 ≥20% 的码（Saily/Yesim）都至少带一条限制。排序后 Roami 自然第一，无任何人工置顶。

**数据层**（`providers.toml`，8 品牌新增 `promo_source` / `promo_source_label` /
`promo_coverage` / `promo_uses` / `promo_constraints`，Ubigi 另加 `promo_expiry_note`——
**不得**把非日期文本塞进 `promo_expires`，否则 `time.Format` 重演第二十八轮的炸构建）。

**连带修正（诚实性）**：原卡文案 "the only tracked code with zero conditions" 不实——
Holafly MYESIMNOW5 结构上同样零门槛。已修：① holafly 补 `promo_unconditional = true`；
② `$pickUncond` 选优改为「零门槛里折扣最高者」（否则 range 顺序会错选 holafly）；
③ roami `promo_bestfor` 去掉 "only" 说法；④ 矩阵零门槛行 note 兜底改用 `promo_coverage`。

**坑**：H2 "Every code, side by side" 被 `check_headings.py` 拦（h2/h3 禁逗号/分号/冒号/
em/en 破折号，H1 豁免）→ 改 "Compare every code on one grid"。**新增 h2/h3 先过标点守卫。**

i18n +21 key（en/de 成对，1056 = 1056 对齐）。九项构建全绿；基线 diff = deals 1 处（预期）；
截图验证排序与徽章。

## 已完成（页面日期改为自动跟随数据 + Nomad 收尾，2026-10-07 第四十三轮）

**用户请求**：「既然更新了页面的数据驱动内容，✓ Prices checked Oct 4, 2026 这个就需要改为当前系统日期。只要是页面数据驱动更新了，日期就应该要改变，不仅限于是这个国家 esim 页面」（并给出 Nomad logo 路径 `static/img/logo/`）。

### 1. 页面日期改为「跟随数据自动走」（核心）

**问题**：日期机制原本靠人记得跑 `bump_checked.py` —— 必然漏。Nomad 就是活证据：数据 10-06 入库、页面却一直印 `Prices checked Oct 4`。

**为什么不能简单换成构建日**：用 `now` 会让 `lastmod` 每次部署都翻新，Google 判定本站 lastmod 无信息量后整体忽略；而且当价格其实是上周抓的时，「今天核过价」本身是不实陈述（第二十三轮试过、已撤回）。**正解是「日期 = 该数据最后一次变化的日期」，并让它自动维护。**

**做法**：新增 `scripts/stamp_checked.py`，给每个「日期单元」存一份内容指纹（sha256）：
- 单元 = `plans.<brand>.<ISO>`（价格）· `profile.<brand>`（品牌档案，含 `.info`/`.policy` 子表）
- 指纹变了 → 日期 = 今天；没变 → 不动；**首次建台账** → 保留现值；**台账已在而冒出新的单元**（新品牌 / 新市场入库）→ 盖今天
- 已挂进 `npm run build` 的**第一步**（`npm run stamp`），改完数据直接构建就行
- 台账 `docs/checked-state.json`（459 个单元）**必须提交进版本库**

**指纹口径**：排除**日期字段行 + 纯注释行 + 行内注释**（含引号内 `#` 与 `\"` 转义的正确处理）。⇒ 改注释 / 调格式**不会**让日期凭空前移；改一个价格**必然**前移。

### 2. Nomad 收尾

- **logo 归位**：`static/img/logo/nomad.png` → **`static/img/providers/nomad.png`**（前者只是素材下载区，放进去不生效；`prov-logo.html` 探测的是 `providers/`，且**只认 `.png`/`.webp`**）。512×512 合法 PNG，产物里 603 页已渲染真 logo、`Nd` monogram 残留 **0**。
- **价格核对日推到当天**：Nomad 50 国 `checked` 10-04 → **2026-10-07**。四处同源已验：可见文案 `Prices checked Oct 7, 2026` ／子页 `Oct 7, 2026` ×5 ／JSON-LD `dateModified: 2026-10-07` ／sitemap `lastmod 2026-10-07T00:00:00Z`。
- 品牌档案日保持 **10-06**（那是真核验日）—— 品牌 hub 的 `Last updated` 取两者最大 = Oct 7 ✓，「prices as checked on」只取价格日 = Oct 7 ✓（不对称口径仍成立）。

### 3. 变更面归因（627 页，0 页未解释）

| 数量 | 原因 |
|---|---|
| 603 页 | Nomad 徽标 `monogram → 真 logo`（Nomad 出现在全站每一个品牌列表里） |
| 24 页 | `guides/*` + `networks/*` + `research/*` —— 它们引用了 Nomad 的**价格核对日**（Oct 4 → Oct 7） |
| **0 页** | 未解释 |

验证方式：产物里含 `providers/nomad.png` 的页面 **603 个**，**全部**落在变更集内；**0 页**含徽标却没变（集合闭合）。基线已重建（643 文件，`--diff` 逐字节一致）。

### 4. 三个坑（已进 PROJECT.md 红线 48–50）

1. **★ 指纹不能包含注释**：第一版把整段原始文本算进去，于是改一句**行内注释**（`color = "#16456B"   # monogram 兜底色…`）就把 Nomad 的品牌档案核对日从 10-06 顶到 10-07 —— **页面一个像素没变，日期却动了**，正是本轮要消灭的那类不实陈述。修法：依次剥掉日期行 → 纯注释行 → 行内注释（`strip_inline_comment()`）。**通用判据：不进产物的东西，不许进指纹。**
2. **★ 「首次遇到」有两个相反的正确行为**：**首次建台账**（状态文件整个不存在）必须**保留现值**，否则全站日期集体跳到今天 = 批量不实陈述；**台账已在而冒出新的单元**必须**盖今天**，否则刚入库的数据顶着旧日期（正是 Nomad 那次的毛病）。判据：问清是「**系统**首次」还是「**这个对象**首次」。
3. **★ 自写验证脚本的哈希口径必须与守卫一致**：我临时写的对比脚本把 manifest 的 `files[rel]` 当成了字符串（实际是 `{sha256, cls}` 字典），于是报出「643/643 全变」的假警报 —— 差点把 627 的真实归因带偏。**要对齐守卫的实现，别自己另写一套。**

### 5. 验证

- `npm run build` **十项全绿**：`0 error(s), 0 warning(s)` ／ 645 files (643 pages), 3694 JSON-LD ／ `OK：产物域名正确，日期与数据一致` ／ `OK: R10 骨架不重复` + `OK: R11 邻国问答不重复` ／ 检查 A·B·C 全过。
- `stamp_checked.py --selftest` **29 项全过**（含「改注释不触发」「新增块盖当天」「同日再改不重写」「幂等」「引号内 `#` 不误伤」「未动的国家保持原样」）。
- **反向验证（真改真跑）**：给 `nomad.toml` 的 US 块插一行 → `--check` 精准报 `plans.nomad.US 现值 2026-10-04 → 应为 2026-10-07` 并退 1；写模式**只改 1 行**；恢复现场后复跑 `--check` OK。
- `bump_checked.py` 重构后 `--show` 输出**逐字节不变**（抽出 `Block` + `parse_blocks()` 供两个脚本共用，避免出现第二份「块头定义」）。
- **幂等性**：`npm run stamp` 连跑两次均为「无改动」；基线 `--diff` 643 页逐字节相同。

### 6. 遗留 / 待你决定

- **哪些数据源该驱动日期**：目前只有 `plans` 与 `providers` 会驱动。`countries.toml` / `carriers.toml` / `refs.toml` / `faqs/<iso>.toml` / `titlesegments.toml` 改了**不会动任何日期** —— 因为那些页面**现在压根没印日期**。要不要给它们加日期（以及印在哪儿）是产品决定，不是技术缺口。
- **第二批品牌 logo**：`gigsky.png` ✓ / `jetpac.webp` ✓ 已在素材区；`bensim.jpg` **名字拼写应为 `bnesim` 且 jpg 探测不到**，接入时须转格式改名。
- 上一轮遗留未动：slot4「ID 规定」14 国历史同句；德语站 FAQ 正文仍是英文。

## 已完成（49 国 FAQ 去模板化 · 句架层拉丁方阵 + Q6 事实修正，2026-10-07 第四十二轮）

**用户请求**：第四十一轮遗留的「49 国三条答案仍是同一副句架、只有数字位不同」要改写，「符合 SEO 即可」。

### 诊断：数字不再过期 ≠ 内容不再重复

第四十一轮把数字改成构建期现算，**数字**问题解决了，但**句架**仍是模板：49 国（jp 手写除外）的三条答案在 50 页里逐字只差数字位。国家 Hub 页正文最强的两块是价格表和 FAQ，FAQ 若 49 页同文，等于 49 页共享同一段「原创内容」—— 既稀释单页独特性，也正是 Google 判 thin/doorway 的典型形态。
另外 Q6「Regional Asia/continental plans from Airalo and Nomad bundle {country} with neighbors」是 **41 国逐字相同、且对法国 / 美国 / 阿根廷自相矛盾**的断言（数据集里根本没有区域档，只有单国档）。

### 设计：三槽 × 7 片段 + 拉丁方阵

- 每条答案拆 **open（直接回答，最可能被答案引擎摘走的第一句）/ body（数据事实）/ close（行动建议）** 三槽，每槽 7 片段（库 = `scripts/faq_frames.py`，21 片段 + Q6 的 7 变体）。
- 分配 `a = i % 7`、`b = i // 7`、`c = (a + b) % 7`（i = ISO 升序位次，jp 除外）。数学性质：(a,b) 把 49 格用满各一次；固定 b 时 c 是 a 的双射 ⇒ (a,c) 各一次；固定 a 时同理 ⇒ (b,c) 各一次 ⇒ **任意两国的三元组至多在一个分量上相同 = 任意两页最多共用一句**。池子必须 ≥ 7（|pool|² ≥ 49）。
- 覆盖 Q1（最便宜）/ Q2（unlimited 计数）/ Q3（Airalo vs Holafly $/GB）三条；Q6 单独 7 变体。

### Q6：从「无数据支撑的断言」变成数据驱动

- 新增两个 token：`{neighbor}` 取**问题里点名的那个邻国**（英国的问题问「英国和法国」⇒ 答法国；机械取 `neighbors[0]` 会答成爱尔兰）+ `{neighbors_all}`。
- 7 个没有邻国的国家（HR / IS / CR / IL / MA / ZA / KE）走按 region 生成的兜底短语，且这 7 国**各占一个变体** —— 否则同 region 的两国（HR / IS 都是 Europe）会渲染出逐字相同的一段。

### 附带修掉的两处 Q6 文案缺陷（只影响这 7 个无邻国）

1. **问题退化成同义反复**：43 国的 Q6 点名了第二个国家（`Can one eSIM cover the UK and France?`），这 7 国却是 `Can one eSIM cover Iceland?` —— 单念像句废话，也抓不到任何「区域 eSIM」意图。改为点名 **`countries.toml` 的 `region`**：`Can one eSIM cover Iceland and the rest of Europe?` / `… Costa Rica and the rest of the Americas?` / `… Israel and the rest of the Middle East?` / `… Kenya and the rest of Africa?`（问题文本是各国静态字符串，改动只在这 7 个文件里，各加了一行注释说明为何用 region 而不是邻国）。
2. **答案里印出内部口吻**：`{neighbor}` 对无邻国走兜底 `"another market on this site"`，渲染进 6 国答案（×en/de = 12 页）成 `Adding another market on this site means…`。改为 `"another country"` —— 读者语言，且与邻国版（`Adding France means…`）语法位一致。
   ⚠ 残留（未动，1 页）：克罗地亚用到的变体 #2 里 `{neighbors_all}` 的兜底是 `the other {region} markets we cover` → `the other Europe markets we cover among them`，读起来略微自指，但语法成立。

### 守卫：R10（源级）+ R11（产物级）

- **R10 例外地读源文件** —— 判的是句架，而句架只存在于源文件里（产物里 token 已变成各不相同的数字国名，反而看不出重复）：a) 三段答案 49 国骨架两两不同；b) 每条答案必须拆得回 `faq_frames.py` 的片段组合；c) 任意两国最多共用一个槽；d) slot6 取自库内 7 变体且无邻国的 7 国各占一个；e) slot6 必须含 `{country}`。
- **R11 读产物**：Q6 在各国页上必须两两不同 —— R10(e) 在源级保不了「互称邻国的一对国家（FR / IE 都指向 UK）分到同一变体」会不会撞车，只有在产物里才暴露。**这条规则就是被那个真实 bug 逼出来的**：对修复前的产物跑，精准报出 `R11 [en] ['FR','IE']` + `R11 [de] ['FR','IE']`。**验证法**：新守卫先对改造前的旧产物跑（抓到），再对修完的产物跑（0 报）—— 只做后者等于没验。
- `--selftest` **13 项**（`selftest()` 7 例 R1–R9 + `frame_selftest()` 6 例 R10，含「正确样本不误报」）全过。

### 踩坑（4 个，详见 PROJECT.md 红线 44–46）

1. **★ 自己写错又自己抓到**：Q1 body 本想写「It is also the cheapest per day, at ${cheap_perday}」，实测 **50/50 国全部不成立** —— 绝对价最低的永远是最小档（US 的 Yesim 500MB / 1 天 = $0.51/天），而 $/天 最低的是长周期大流量档（US = $0.06/天）。降级为恒等式 `That is ${cheap_perday}/day across the plan's validity window.`。同类：Q3「a metered plan never throttles」是**无法证伪的绝对句** → 改成「a fixed bucket rather than a daily allowance」。**红线 44：每一句比较级 / 最高级都必须能指着一条数据说清口径。**
2. **★ R10 初版按「句数」判 → 42 条假失败**：Q2 的 `open[1]` 本身就是两句，任何两国只要共用一个 open 就命中 2 句，真正该抓的「共用两个片段」反被淹没。改成从片段库 `decompose()` 反解三元组、判「最多共用一个**槽**」→ 归零。**副产品更有价值**：`decompose()` 拆不开 = 手改了文案却没同步片段库 —— 这个「失败」本身就是该报的错。**红线 45。**
3. **★ Q6 撞车**：V2 / V6 两个变体不含 `{country}`，而法国与爱尔兰**互称邻国**（都指向 UK）且分到同一变体 → 两国渲染出逐字相同的一段。修法：变体补 `{country}`（14 处重刷）+ 源级断言「Q6 每个变体必须含 `{country}`」+ 新增产物级 R11。
4. **★ `selftest()` 打底值带 `{token}` 导致 R1 误报**：`good = dict(toml_faq)` 改用 `{q: ANY_TOKEN.sub("X", a) …}`（样本模拟的是**已渲染**产物，源文件里的占位符在这里必须已变成值）。

### 验证

- **产物级反同质化（独立度量，不只依赖 R10 的源级读数）**：抽 50 国 en hub 的 6 条 `<details class="faq-item">` 正文按问法序号分组去重 —— Q1 **50/50**、Q2 **50/50**、Q3 **50/50**、Q5 **50/50**、Q6 **50/50**（Q6 改造前是 41 国逐字相同）；**问题层也 50/50**；de 站读数完全相同。
- **Q6 文案修正的变更集可精确证明**：修前修后各存一份基线对比 → **变更 14 个 = 7 国（IS HR CR IL MA ZA KE）× (en + de) 的 `country_hub`，新增 0 / 删除 0**。`grep -rl "another market on this site" public/` = **0 文件**。
- ⚠ **这条度量本身也修正了一个判据**：第四十一轮之后按**字面** md5 去重早就"通过"了（50/50/50，因为每页数字不同），但**句架其实只有 1 种** —— **md5 会被页内数字骗过**。真正该做的是先把页内变量抹成占位符再比（即 R10 的 `skeleton()`）。第三十七轮定的「md5 去重必须 = N」判据，对「模板里含页内数字」的模块是**假绿**。
- 源级 slot 读数：slot1 / 2 / 3 = **49 种 / 49 国**；slot6 = 无邻国 7 国各占一个变体；slot5 = 50 / 50。
- **已知历史重复（INFO，不判失败）**：slot4「ID 规定」有 **14 国**共用同一句（AE AR CN EG ID IL IN KE MA MX PH SA TR VN，都是实名登记要求的市场，句子站得住）→ slot4 = 37 种 / 50 页。
- 改写执行：`改写 196 处 / 已是目标 0 处 / 拒绝 0 处`（49 国 × 4 条）；复跑 `0 改写 / 196 已是目标`（幂等）。
- `check_faq_facts.py --selftest` **13 项全过**；`faq_frames.py --check` OK；`grep -c '\$[0-9]' data/faqs/*.toml` = **0 行**。
- `npm run build` 全量：**十项全绿** —— `0 error(s), 0 warning(s)` / `645 files (643 pages), 3694 JSON-LD` / 品牌子页全过 / `OK: 100 country pages - every FAQ number matches data/plans, no tokens left, schema in sync` / `OK: R10 骨架不重复` / `OK: R11 邻国问答不重复 - 100 国页的 Q6 逐条不同` / `OK: 检查 A·B·C 全部通过`。
- **爆炸半径证明**（比 diff 更硬）：`faq-live-tokens.html` 只被 `layouts/compare/single.html` 引用，`data/faqs/*.toml` 也只被它消费 ⇒ 本轮产物变更只可能是国别 Hub 页（en + de）。基线重建 **643 文件**、复跑 0 变更。

### 遗留（可选，非债）

- slot4「ID 规定」14 国同句 —— 逐国改写需要**该国实名规定的真实外部来源**，没有来源不编。
- 德语站 FAQ 正文仍是英文（既有状态，本轮未动）：`{country}` 会渲染成德语名（`Deutschland`），而句子是英语。要处理需先定口径是「翻译」还是「独立的对比视角」。

## 已完成（FAQ 数字断言改为构建期现算 + 新增产物级 FAQ 守卫，2026-10-07 第四十一轮）

**用户请求**：第四十轮留下的「99 条 FAQ 事实断言过期」要拍板（原始三选项：脚本重算 / 改无数字措辞 / 不动），
用户要求「帮我优化这个，符合谷歌 SEO 即可」。

### 诊断：为什么不能只是"重算一遍"

`data/faqs/*.toml` 里三条答案把数字写死了（最便宜 / unlimited 计数 / Airalo-Holafly 报价），
而真值在 `data/plans/*.toml` 里、每次抓价或接入品牌都会变 → **页面自相矛盾**：
US 的 FAQ 说「Roami $2.99 最便宜」，正上方价格表里最低的是 Yesim $0.51。
这正是 Google 明令反对的一类问题（结构化数据必须与用户所见一致；价格页数据陈旧直接掉 E-E-A-T），
而 49/50 国答案逐字相同本身也是模板级重复内容。原审计器还按固定问法匹配，**jp 被整条跳过**
（jp 写「$1.99 for 1GB over 7 days」，实际是 3 天）。

### 做法：第 4 个选项 —— 让数字**不可能**过期

| 层 | 动作 |
|---|---|
| 新 partial | `layouts/partials/faq-live-tokens.html`：从 `country-stats` 的 `$rows` + `providers.toml [x.policy]` 现算 **30 个 token**（`cheap_*` / `runner_*` / `value_*` / `unl_*` / `ah_*` / `brands_list` / `plan_count` / `brand_count`），取值缺失输出 `n/a` 而不是空串 |
| 模板 | `layouts/compare/single.html` 组装 `$faqs` 时做一次 `{token}` → 值替换。**可见正文与 FAQPage JSON-LD 读同一份 `$faqs`，schema 与用户所见天然同源** |
| 数据 | `scripts/migrate_faq_frames.py`（一次性、幂等）改写 **151 处 / 50 国**；jp 保留其独有分析口吻、同样 token 化，并把 Q5 的品牌枚举换成 `{brands_list}`（nomad 接入后它少列了一家） |
| 守卫 | 删除只读源文本的 `audit_faq_facts.py`，新增 `scripts/check_faq_facts.py`（**读产物**，R1–R9，带 `--selftest`），挂进 `check:output`（校验九项 → **十项**） |

**口径**（写进 partial 头注释，别再另立第二套）：最便宜 = 价最低 → 同价取流量更大 → 再同取品牌 key 升序；
最佳 $/GB **只算计量档**（无限档 perGB 是 999999 哨兵）；无限最优按 `$/天`；
FUP 取 `[<brand>.policy]` 而**不是** plan 的 `fup_note`（roami/yesim 的 fup_note 全缺、holafly 那条写的是
"Always On" 附加包说明，用了就会写出假句子）。

**守卫规则**：R1 无未替换 token ／ R2 无 `n/a`·`$0.00` 哨兵漏出 ／ R3 问题集合与 toml 一致 ／
R4 可见正文与 FAQPage schema 同文 ／ R5/R6/R7 三条答案的品牌与价格与现算一致 ／
R8/R9 文案不变量（最便宜不得是 Airalo/Holafly、最便宜档必须是计量档）。
**必须读产物**：源文本现在只有 `{token}`，模板写错在源文本里看不出来（同 `check_output.py` 的立身之本）。

### ★ 本轮踩的坑

1. **红线 39 再踩一次**：partial 里写了两处 `{{ return }}`（一处在 `if` 内），第二处退化成 Go 关键字，
   报 `wrong number of args for return: want 0 got 1`。改写成 `if` 包裹、**只留一个顶层出口**即解。
   项目里其他 partial 都只有一个 return，所以这条红线此前没被触发过 —— 现在 partial 头注释里引了红线号。
2. **数值区间类 token 要把货币符号包进值里**：`unl_perday_range` 初版只算 `1.67 to 4.14`，
   套进 `by day rates run from ${...}` 就成了「from $1.67 to 4.14」—— 第二个数丢符号。
   改成 token 自带 `$`、文案写 `from {unl_perday_range}`。**凡"区间/列表"型 token，单位要跟值走。**
3. **反同质化第一次没过**：`unlimited` 那条在 50 页里去重只有 **45**（两组市场的事实完全相同：
   HR/IE/PT 与 DE/GR/NL/PL）。原因是该句里只有 "here" 没有国家名 → 事实相同的国家必然同文。
   改「plans here」→「plans for {country}」后 **50/50**。附带收益：答案里带上了目的地词。

### 验证（全部为**产物文本断言**，按用户约定不做截图）

- **新守卫双向验证**（这是它有意义的前提）：
  ① 对**本轮之前的旧产物**跑 → `ERROR FAQ fact guard: 342 problem(s) across 100 pages`
  （抓到了「Roami $2.99 vs 实为 Yesim $0.51」「All 10 vs 实际 94」「Holafly $4.37 vs 实际 $11.90/3 天」，
  且抓到了 jp —— 旧审计器跳过的那个）；② 修完后跑 → `OK: 100 country pages - every FAQ number
  matches data/plans, no tokens left, schema in sync`。`--selftest` 7 项全过（含"正确样本不误报"）。
- **十项构建全绿**：`validate` 0/0；`OK: 645 files (643 pages), 3694 JSON-LD blocks`；
  `checked 643 html files, 16291 h2/h3, bad: 0`；品牌子页 450/450（天数按钮无假档位 448/450）；
  `仍显示「尚未核实」政策的页面 0`；`check_dates` 域名/日期/完整性通过（585 URL 全有产物）；检查 A/B/C 通过。
- **零回归 diff = 变更 100 / 新增 0 / 删除 0，且 100 全部是 `country_hub`** —— 正好是 50 国 × en/de 两个语言，
  **爆炸半径精确等于改动意图**（没有任何意外页型被带上）。重建基线（643 文件）后复跑 0 变更。
- **反同质化**：三条答案在 50 个国家 hub 上去重 **50 / 50 / 50**（改造前：Q1 与 Q3 各只有 2 种）。
- 渲染抽查（US / JP / Macao，与价格表逐条对照）：
  US「Yesim's 500MB / 1 Day at $0.51 ($0.51/day) … best value per gigabyte is Nomad's Local USA - 30 Days - 50 GB at $0.60/GB」；
  US unlimited「All 94 … day rates run from $1.67 to $4.14 … Roami at $49.99 for 30 days ($1.67/day)」；
  JP 保留自有口吻「Roami … $1.99 for its 1GB / 3 Days package, and Roamic is the closest challenger at $2.00」。
- **判据固化**：`grep -n '\$[0-9]' data/faqs/*.toml` → **0 行**（占位 `$` 后面是 `{`，不算）。

### 文档同步

`PROJECT.md`（§0 最后更新、§4.5 FAQ 数据手册加"必须写 `{token}`"小节、§5.2 脚本表加两个脚本、
§6 命令速查、§7 连带影响表 #4 改为"已不用手动管"、**§7.1 整节重写为"已修 + 遗留"**、§14 新增红线 43）、
`docs/add-brands-plan-2026-10-06.md`（§6.1 选项 D 与 §7.5 更新为已修）。
`docs/keyword-map.md` **无需改** —— 本轮的词归属没变（三条答案的选题不变，只是答案里的数字改成现算）。

### 遗留（可选，非债）

1. **jp 之外 49 国的三条答案仍是同一副句架**（每个数字位都不同、去重 50/50，但句式相同）。
   若要继续提 SEO，可逐国改写成 jp 那种带分析的口吻 —— **只改 `data/faqs/*.toml` 文案，模板与守卫都不用动**。
2. **Q6「Regional Asia/continental plans from Airalo and Nomad…」是 50 国逐字相同、且无数据支撑的断言**
   （我们的 plans 数据里只有单国档，没有区域档），待核实或改写。它不是"过期数字"，是"无法自证的断言"。
3. `hugo` 单次全量构建在本机实测 **~250s**（跑守卫链条的完整 `npm run build` 约 7-9 分钟），
   比轮次记录里的 70-140s 慢 —— 与本轮改动无关（第一次带 partial 的探针构建只用 38s），
   疑与本机负载/工作区未提交文件数（554+）有关，未深究。

## 已完成（新增品牌第一批 · Nomad 试点全链路，2026-10-06 第四十轮）

**用户请求**：把 `_competitors/*/raw/` 里的 bensim / gigsky / jetpac / nomad 四个品牌 × 50 国套餐接入，
并先要"是不是牵一发而动全身"的影响面判断。

**四条拍板（用户）**：① 价格全站统一 USD（BNESIM 的 EUR 要折汇）② 国家名统一 USA / UK（新数据先改名再落地）
③ 范围只做这 4 家（raw 里其余 5 家 quibity/roamless/gomoworld/maya/firsty 不做）
④ **先拿 Nomad（50/50、数据最干净）单独打通全链路、验收无误再批量上其余 3 个**。

**影响面结论**：见 `docs/add-brands-plan-2026-10-06.md`。站点模板几乎全数据驱动
（`range $d.providers` / `country-stats.html` / `vs-agg.html`），改动集中在 **L1 数据层**；
真正"全身"的是**每一页的数字与结论都变** —— 因为 `footer.html:88` 有一份
`range $key, $p := $d.providers` 的**全品牌清单**，加一个品牌 = **全站每页都进 diff**。
页面量公式：`+N 子页 + 1 品牌 hub + (M-1) 对决页`。

### Nomad 试点落地（8 品牌 → 9 品牌）

| 层 | 动作 |
|---|---|
| 数据 | `scripts/scrape/raw/nomad/`（50 JSON）→ `toml_write.py nomad --checked 2026-10-04` → `data/plans/nomad.toml`（**442 条 / 50 国**，data 292 + unlimited 150）→ `backfill_networks_uniform.py`；`_rename_us_gb.py` 改名 25 处（`United States`→`Local USA` / `United Kingdom`→`Local UK`） |
| 档案 | `data/providers.toml` 加 `[nomad]` + `[nomad.info]`（hq/legal/website/trustpilot 只存链接/support_email/destinations）+ `[nomad.policy]`（hotspot/fup/topup/voice）+ `promo_*`（`BEYOND20` 20%，另有 FALL30 / ESIMDNOMAD20 作 alt）；`profile_checked="2026-10-06"` |
| 出站 | `hugo.toml` 加 `[params.outbound.targets.nomad]`。**刻意不配 `country_path`** —— Nomad 逐国 slug 口径与本站不对齐（本站 `turkiye` vs Nomad `turkey`），机械拼接必产 404 |
| 页面 | 品牌 hub `content/en/esim-providers/nomad.md`；**450 子页**（`gen_provider_pages.py`）；**36 对决页**（28 旧未动 + 8 新，用 `scripts/gen_vs_pages.py` 只补不重写） |
| 元数据 | `regen_meta_brand.py` 重写 50 国家页 desc + 28 旧对决页 title/desc（共报 82 个文件，diff 逐条核对无误报）；`_solve_titles.py --write` 重算 50 条国家页 title，**仅 6 条变化**（AU/GB/SA/TH/US/ZA —— Nomad 改变了"最低 $/GB"「有无无限档」的分支判定） |
| 文档 | `PROJECT.md` §0/§2/§4.7/§5/§7/§9/§13/§14 计数与"nomad 已退场"表述全部更正；`docs/keyword-map.md` 品牌词条；本轮 |

### ★ 本轮踩的坑（都值得写进手册）

1. **零回归守卫的"页型判据"依赖品牌集，品牌集变了判据必须跟着变** —— `verify_no_regression.py`
   的 `BRANDS` 写死 8 家 → 新品牌子页掉进 `classify()` 的 `static` 兜底 → **401 条假失败**
   （`✗ [A:static] compare/argentina/nomad/index.html: 出现了只属于 [...] 的区块 id="verdict"`）。
   已改为从 `data/providers.toml` 推导，并补 2 条分类自测用例钉死该约束。
2. **`toml_write.py` 的 `CHECKED` 常量是"首批抓取日"** —— 新品牌补抓不传日期会让整批数据
   宣称一个月前的核对日，页面 / `dateModified` / sitemap 三处一起撒谎。已加 `--checked YYYY-MM-DD`。
3. **`_rename_us_gb.py` 会改 `data/plans/*.toml` 的套餐名**（脚本内有 `PLAN_RULES` + `PLAN_TARGETS`），
   不是只改 md —— 事先按文档串判断会判错。
4. **元数据重建的"改动面"比脚本报的大**：`regen_meta_brand.py` 报 82 个文件，实际国家页 50 +
   对决页 28 + 品牌 hub 8 ≈ 86，逐条 diff 确认非虚报后照单接受。
5. **`append` 的静默形状事故（第二十四轮旧账，本轮再次确认）**：凡把数据喂给前端 JS，
   都要**断言元素形状**，不能只断言"是合法 JSON"（`json.loads` 全过但 `p[0]` 取错）。
6. **i18n 文案里按百分比枚举品牌的句子会漏新品牌** —— `esim_deals_list__params_verdict_body`
   原文写"every other code at or above 20% here — Saily's 25% and Yesim's 20%"，Nomad 的
   `BEYOND20` 也是 20% 但没被列入 → 已补（en/de 成对）。**这是"随品牌集变化的手写枚举"，
   下一次接入 gigsky/jetpac/bnesim 时要再看一眼。**

### 验收（全部为**产物文本断言**，按用户约定不做截图）

- **九项全绿**：`validate` 0 error 0 warning；`OK: 645 files (643 pages), 3694 JSON-LD blocks`；
  `checked 643 html files, 16291 h2/h3, bad: 0`；品牌子页 **450/450** 各项合规（"天数按钮无假档位" 448/450）；
  `仍显示「尚未核实」政策的页面 0`（证明 `policy` 已生效）；检查 A/B/C 全过。
- 产物体量：**643 页 / 450 品牌子页 / 36 对决页 / 9 品牌 hub / sitemap 585 URL**；套餐总数 **8218**。
- 断言：footer 品牌链接 9 家；50 国家 hub 内品牌子页链接数分布 `{9: 50}`（50 页全 9）；
  **反同质化：nomad 品牌卡在 50 页去重后 md5 = 50**（US「11 plans · 3 unlimited / $0.60/GB」
  vs Fiji「5 plans / $1.95/GB」）；50 国 hub 全链到 nomad 子页（0 缺失）；
  matchups 索引去重对决链接 36 = 落地文件 36；`check_links.py` 168,632 条 href → **坏链 0**。
- 基线：本轮共重建 **3 次**（Nomad 落地后 → i18n 文案修正后 → monogram 缩写微调后）。最终基线
  643 文件、复跑 diff **0 变更 / 0 新增 / 0 删除**。中间两次 diff 的构成都逐条核对过：
  ① i18n 那次 = `deals=1` + `networks=12`（后者是本文件末尾 P-A 那条 known issue，见"遗留"）；
  ② monogram 那次 = **603 页**（`provider_sub 450 + country_hub 101 + matchup 36 + provider_hub 10 + home 2 + compare_index 2 + deals 1 + tools 1`），
  全由 `initials` 一处数据改动引起，属预期。
- 终检：`check_links.py` 168,632 条 href → **坏链 0**；`audit_faq_facts.py` 独立复核 3 国（US/JP/FJ）
  确认审计器读数与手工算的真值一致（US 实际最便宜 Yesim $0.51 / unlimited 94 条）。

### 一处主动微调（可一行回退）

`data/providers.toml` 的 `[nomad] initials` 从 `"No"` 改成 **`"Nd"`** —— 品牌卡上是
「`[No] Nomad`」（monogram 徽标 + 品牌名紧邻），**"No" 会被读成单词 "no"**。站点无 Nomad 官方
logo 素材（`_competitors/*/brand/nomad.json` 里也没有 logo/主色字段），真 logo 到位前一直用它。
代价：monogram 出现在全站 603 页 → 基线 diff 603 处（预期）。**想回退就把 `initials` 改回 `"No"`。**

### 遗留（未修，等用户拍板）

- **99 条国家 FAQ 事实断言过期**（`audit_faq_facts.py` 首跑：`cheap_bad 49 + unl_bad 50`）。
  **排除 nomad 跑一遍仍是 99 条 → 改动前就存在的技术债**；Nomad 让其中 45 国"最便宜品牌 /
  无限档计数"发生变化。例：US FAQ 写"Roami $2.99 最便宜"实际 Yesim $0.51；写"All 10 unlimited"实际 94 条。
  → **2026-10-07 第四十一轮已修**（三条答案改构建期现算 + 新守卫 `check_faq_facts.py`），见本文件顶部那一节。
- `PROJECT.md` §18（i18n）里的 key 数 / 已收录 URL 数仍是旧值，属历史round欠更（本轮未动）。
- **`/networks/*` 的 `Updated` 徽章取 `now`（构建日）**（2026-10-05 已发现，挂在文末 P-A 待办里）：
  本轮重建基线时又撞上 —— 构建跨过本地零点，12 个 networks 页从 `Oct 6` 变 `Oct 7`，
  于是在基线 diff 里报成 `networks=12`。**这 12 处与本轮改动无关**（本轮 i18n 只动了 deals 页），
  是已知的 `now`-徽章噪声。重建后的基线已含新日期；**下次构建（跨日）会再报这 12 处，别再误判成回归**。

---

## 已完成（内链地毯体检 + /networks/fiji/ 死链修复 + 关键词地图纠正，2026-10-06 第三十九轮）

用户：分析哪个页面跳到不存在的 `/guides/how-to-install-an-esim/`，删掉该跳转。

- **结论：全站 0 引用。** 新增 `scripts/check_links.py`（扫 public/ 全部 href，解析目标文件是否存在）：
  152,441 条 href → `/guides/how-to-install-an-esim/` **一个引用都没有**（源码 / 构建产物 / 线上抽查三处均为 0；
  线上部署已含第三十七、三十八轮改动，确认部署是最新）。该 URL 线上确为 404，属**历史遗留的孤立 404**
  —— 早前轮次 `/esim-deals/` Step 5 曾链它（STATUS.md 有记录），已修，无内链可删。
- **唯一残留引用在文档里**：`docs/keyword-map.md` 把错误 slug 当规范 URL 记录 → 已改为
  `/guides/how-to-install-esim/` 并标注原因（防后续内容再生产时复发）。docs/ 全目录内链目标复验 0 失效。
- **顺手修掉全站唯一真实内链 404**：`/networks/fiji/`（被 8 个品牌页引用）。根因：`esim-providers/single.html`
  的 4G 名单无条件拼 `/networks/<slug>/`，但 `content/en/networks/` 只有 12 国建页；Fiji 是唯一纯 4G 市场，
  8 个品牌页全中招。修法=`site.GetPage` 守卫：有页面才给链接，没有则降级为纯文字（国家名 + 运营商信息保留）。
  复验：全站坏链 **0**；12 国 /networks 链接照旧（9 次/国未变）。
- 九项全绿（0 error / 584 html / 14804 h2/h3 零违规）；基线重建。diff 中 12 个 networks 页属
  **已知待办的「Updated 徽章取构建日」**（每次重建必变，非本轮改动），真实改动=8 个品牌页。

## 已完成（国家页「eSIM for your next destination」窄卡文字挤压修复，2026-10-05 第三十八轮）

用户：该模块下 5 个国家卡片「文字都挤压在一起」，只改这一处，其他不动。

- 根因：卡片是**横排 flex**（国旗 h-9 w-[3.25rem] + `flex-1` 文字 + 箭头），栅格 `lg:grid-cols-5`。
  lg 断点每卡约 182px，扣内边距 32 + 国旗 52 + gap 16 + 箭头 16 → **文字只剩约 50px**，
  比最长单词还窄（xl 1500px 下也只有约 89px）→ 文字被压成竖排并顶到国旗/箭头。
- 修法（只动 `layouts/compare/single.html` 的 `#next` 卡片）：卡片改**竖排** `flex flex-col`，
  首行「国旗 + 箭头」用 `justify-between`，标题 `text-sm font-semibold leading-snug` 独占整卡宽度，
  价位行 `mt-1.5 text-xs leading-relaxed`；国旗加 `shrink-0`。标题与价位不再与国旗争横向空间。
- 影响面：**仅 100 个国家页**（en 50 + de 50）进 diff，其他页面零改动（已验基线）。
- 九项全绿（0 error / 584 html / 14804 h2/h3 零违规）；旧写法全站残留 0；基线已重建。

## 已完成（国家页右栏真吸顶 + 模块⑥ 逐国实测反同质化，2026-10-05 第三十七轮）

**① 右栏「本页导航」真正吸顶**。根因不是缺 `sticky`，而是外层栅格写了 `items-start`：
它让 `<aside>` 自身高度 = 目录卡高度，内层 `sticky top-24` 没有可滚动的行程，表现成
「一滚就走」。改为默认 `stretch`（`class="grid gap-10 xl:grid-cols-[minmax(0,1fr)_15rem]"`），
侧栏随正文拉到整行高，吸顶才生效。注意：`items-start` 在 ⑦ 的 quirks 栅格、
⑦b 的其它栅格里是**对的**（那些是行内图文对齐），只有「侧栏要吸顶」的这一处不能有。

**② 模块⑥「Which eSIM providers cover X」反同质化改造**。原先每张卡渲染
`tagline + strengths[0:3] + weaknesses[0:2]`，这些字段来自 `data/providers.toml`，
**50 个国家页逐字相同** —— 模板级同质化，对读者没有信息增量，对谷歌是重复内容 ×50。
现在改为逐国实测（顶部新增 `$provAgg` 一次遍历聚合）：
- 本国档位数（含其中无限档数）
- 本国最低价 + 对应数据量/天数
- 本国最佳 $/GB + 对应数据量/天数（无限档用 `.isUnlimited` 排除，否则被 999999 哨兵顶掉）
- 本国骑的本地网络（`networks` 字段，逐国不同）
- 一条**算出来的**结论：本国最低价命中 / 本国最佳 $/GB 命中 / 两者都中 /
  该国只有无限档 / 比本国最佳贵 N%
通用画像（tagline/优缺点）不再重复，留在各自的 `/esim-providers/<key>/`，卡片底部有链接。
新增 i18n 17 key（en/de 成对）。**验收判据：50 国模块⑥ 文本块的 md5 去重后 = 50**（改造前 = 1）。

**③ 验证方式**：本轮起按用户要求**不做截图验证**，改为产物文本抽取 + 哈希去重 + 类名断言。

九项全绿（h2/h3 14804 处 0 违规）；基线已重建；dev server 重启。

## 已完成（枢纽 H2 长尾化 + 目录对齐 H2 + 右栏去重 + footer 加 X，2026-10-05 第三十六轮）

**① /compare/ H2 全部改为谷歌长尾词**（用户死要求）。前 6 个在 `content/en/compare/_index.md`：
What this index actually contains → **How to compare travel eSIM plans**；The two numbers everything
is ranked by → **eSIM cost per GB and cost per day explained**；What a country page gives you →
**What a country eSIM comparison shows**；What actually moves the price… → **Why travel eSIM prices
differ by country**；Local SIM **versus** roaming versus eSIM → Local SIM **vs** roaming vs eSIM（vs
才是搜索词形态）；How to use this index → **How to use this eSIM comparison index**。后 5 个在 i18n
（en/de 成对）：cheapest_head 去 "The"；head_to_head → **Head-to-head eSIM provider comparisons**；
faq_head → **eSIM pricing and comparison FAQs**（regions_head / brands_head 本身已是长尾，未动）。
check_headings 的 `,;:—–` 禁令全程避开。

**② 国家页右栏只留「本页导航」**：删掉 `compare/single.html` 里挂的
`aside-destinations.html`（"Popular destinations / eSIM plans travellers compare next" 卡）——
与正文 ⑨a「eSIM for your next destination」主题重复且占宽。partial 本身保留（guides/networks
还在用），i18n key 不删。

**③ 右栏目录 label 与 H2 一一镜像**（用户实测反馈"Top picks by trip 对不上"）：13 个
`compare_single__toc_*` 全部改成对应 H2 去掉国名后的写法（如 verdict → "Which eSIM is best for
your trip"、faq → "Buying an eSIM FAQ"），en/de 成对。校验：101 国家页 TOC 锚点 0 死链，US 页
13 H2 ↔ 13 TOC 条目顺序完全一致。

**④ footer 社交新增 X**：`hugo.toml` 追加 `[[params.social]] key="x" url="https://x.com/esimsift"`
（自动进 Organization sameAs），`social-links.html` 补 X 的 24×24 path。全站 footer 同步。

九项全绿；diff 583/584（footer 加图标全站生效，预期）；dev server 已重启（hugo.toml 变更需重启）。
**待办（未动，用户未点名）**：国家页 H2 "Things to know before buying a …"（quirks）与
"What should I know before buying a …"（faq）近似重复，若按长尾规则应二改一。

## 已完成（全站 USA/UK 统一 + 国家页右侧导航 + ItemList 补齐 + /compare/ 枢纽扩容，2026-10-05 第三十五轮）

**① 国家页右侧「本页导航」（模板级，50 国统一生效）**
- `layouts/partials/compare-toc.html`（新增）：渲染章节表为 `<nav data-toc>`。
  与 guides 的 aside-toc 分开，是因为国家页 H2 全由模板渲染（md 正文没有标题），扫不到。
- `compare/single.html`：章节表 `$toc` 显式声明（id 与各 `<section aria-labelledby>` 一一对应，
  条件分支与渲染守卫一致）；桌面 `xl:grid-cols-[minmax(0,1fr)_15rem]` 右侧吸顶
  （断点定在 xl，lg 起收窄会把 min-w 880px 的主表挤成横滚）+ 移动端 `<details>` 折叠块；
  复用 guides 同款 `aside-destinations.html` 热门目的地内链；滚动高亮走 aria-current（无 JS 也可用）。
- **⑦b 的 $netMap/$netKeys/$profiles 纯计算提前到布局之前**：目录必须在渲染前知道该节渲不渲染，
  否则挂死链。只是搬家，口径未改。50 国页锚点全验：0 死链。
- 新增 i18n `compare_single__toc_*` ×13（en/de 成对）。

**② ItemList 结构化数据补齐**：50 国页原有 Product + FAQPage + BreadcrumbList，唯缺 ItemList。
在 `compare/single.html` Product 块后加一份「主表默认排序前 10 名」ItemList（position/name/url
指向品牌×国家子页）。50/50 全覆盖，JSON 可解析（check_output 通过）。

**③ 全站 United States→USA、United Kingdom→UK**（用户定）
- `data/countries.toml`：US `name="USA"`（新增 `full="United States"` 只喂搜索 haystack）、
  GB `name="UK"`（新增 `full="United Kingdom"`）。slug 不变，URL 与既有索引不失效。
- `data/titlesegments.toml`：US/GB 标题同步改简称。
- `data/faqs/*.toml` + `content/en/**/*.md`：**带冠词的短语先替换**（"for United States"→"for the USA"），
  再兜底裸词 —— `scripts/_rename_us_gb.py`（规则顺序敏感），content 35 文件 115 处。
- `data/plans/*.toml`：套餐名是**国家标签拼出来的描述串**（roamic "United States eSIM 5GB / 21 Days"、
  saily "United Kingdom 1GB 7 days"、yesim "United Kingdom (UK)"、alosim 小写 "united states (usa)"），
  4 文件 196 处同步改（UAE 不受影响；仍逐字保留 opensignal 外部报告标题）。
- 搜索兜底：`country-card.html` 的 `data-name` = 显示名 + full（"usa united states"），
  首页 typeahead 的 haystack 加 `full`，alias 表方向仍是俗称→全称。搜 "united states"/"united"/"uk" 都命中。
- `verify_provider_pages.py`：标题国家名判定改为「slug / name / full 三选一」（跟数据层走，不再抄名单）；
  长度下限 48→44（USA/UK 天然短，为凑字数注水不值）。
- 残留 7+7 处 = Opensignal 报告真实标题（逐字引用，E-E-A-T）+ 首页搜索 JSON 的 full 字段（刻意）。
- `data/de/countries.toml` 不动：那是德语本地化名（Vereinigte Staaten），不是英文串。

**④ /compare/ 枢纽页扩容（SEO + 用户意图）**
- `content/en/compare/_index.md`：新增 6 段长文正文（原先正文为空，枢纽页只剩卡片网格），
  H2 全部避开 `[,;:—–]`；数量用 shortcode 注入，不写死。
- 三个新数据模块（一次遍历聚合，`country-stats` 改 `partialCached`）：
  ①入门价榜（排序键 = 入门价→同价按最优 $/GB→国名，避免前十全并列 $0.51）
  ②区域概览 ×5（各区入门价地板 + 最优 $/GB，链到区域指南）
  ③品牌价格榜（按各品牌全球最低价排序；数据里 8 品牌全覆盖 50 国，所以不做"覆盖矩阵"——
    那只会输出 8 行 50/50，没信息增量）
- FAQ ×5 + FAQPage schema（一份 `$faqList` 两处用，答案纯文本、构建期注入真实数字）。
- ItemList（50 个目的地，站内可爬链接）。新增 i18n `compare_list__*` ×27（en/de 成对）。

**改动面**：584 页中 580 页进 diff —— 全站 footer 列国家名（USA/UK）+ 101 国家页版式 + 枢纽重排，
均属本轮预期；九项校验全绿；基线已重建。

**坑（本轮新增）**：HTML 属性里嵌 `{{ printf "%.2f" … }}` 的内层双引号会把外层属性截断
（Go html/template 按 `"` 结束属性）—— 带内层引号的表达式要用**单引号**包属性：
`style='width: {{ printf "%.0f" … }}%'`。另：`index` 对**空 slice** 直接报错（不返回 nil），
取第 0 条前必须先判 `len`。

## 已完成（美国国家页：按旅行类型选网 + H1 用 USA 别名，2026-10-05 第三十四轮）

**背景**：用户给了一份外部「美国国家页优化方案」。**核对后方案 7/9 项已实现**（运营商选择指南
= carriers.toml 驱动的 profiles+strong/weak、无限套餐真相表 = policy 数据、按时长/人群推荐、
/tools/ 旅行成本计算器、ItemList+Product+FAQPage+BreadcrumbList、vs 页内链、$/GB 与品牌筛选）。
用户拍板只做其中 2 项：**① 按旅行类型推荐网络 ② H1 改用 USA 别名**。

**① 按旅行类型选网（模板级通用，先只填美国数据）**
- 数据层：`data/carriers.toml` 的 `[[US.info.trips]]` = {key, carrier, min_gb, min_days}，
  carrier 必须与 profiles/detail 的 name 精确一致；**why 文案不重写**，模板直接取该 carrier
  的 `info.detail[].strong`（已复核文案，单一事实源）。
- 模板：`compare/single.html` 网络节内新增 `#trip-network` 卡（H3「Which network fits your trip」+
  4 张 trip 卡：城市/公路/国家公园/长住混合），复用本节已算好的 `$netMap`/`$details`，不另立口径。
- 套餐挑选逻辑：① min_gb+min_days 都满足 → ② 只满足 min_gb → ③ 兜底任取，各取最便宜。
- **反重复设计**：美国 8 家品牌都能连全部 3 网 → 首版四张卡都在重复「8 of 8 … $0.62/GB · aloSIM」，
  等于没信息量。改为：全都能骑时把「网络不限制品牌选择」这句**提到顶部只说一次**
  （`$anyPartial` 判定），卡片只保留该行程类型的「够用最便宜套餐」（现为 $3/$8/$5/$15 四个不同结果）。

**② H1 别名**：`data/countries.toml[US].alias = "USA"` → H1 `Best eSIM for USA in 2026`
（title 仍是 United States，两个词都覆盖）；模板 `{{ $country.alias | default $country.name }}`，
缺省回退，其他 50 国零影响。de 页经 data 深合并同样生效。

**★ 坑（本轮真事故）**：守卫块不渲染 ≠ 零输出。首版把 `$tripText`/`with` 写在行首，未裁剪空白，
**50 个国家页各多出 4 个空行**，全进回归 diff（100 处变更）；同一处还误多加一个 `{{ end }}`
把外层 section 的 `{{ if }}` 提前闭合，Hugo 报 `undefined variable "$faqs"`。
修法：整块动作用 `{{- ... -}}` 裁剪（含注释），末行 `{{- end }}`；修后 diff = **仅 US en+de 2 处**。

九项全绿；基线已重建；iframe 定位截图核验模块视觉。

## 已完成（footer 社交链接 + Organization sameAs，2026-10-05 第三十三轮）

**① 社交链接**：`hugo.toml` 新增 `[[params.social]]` 数组（单一事实源：facebook/youtube/tumblr，
**数组序 = 展示序**，不要改成 map——map 按字母序打乱）；新建 `partials/social-links.html`
（内联 SVG 图标 + rel="me noopener" + aria-label，新平台两步：toml 加项 + $icons 补 path）；
footer 底栏改为三段式（披露文案 | 社交图标 | 日期说明，lg 三点分布）。

**② sameAs 补齐**：`schema-org.html` 的 Organization JSON-LD 从「暂不填（无官方账号）」
改为从 `params.social` 派生 sameAs（无配置则整个键不出现）——实体锚点补全，AI 引擎
归因一致。en/de 同源（社交链接与语言无关）。

**坑**：改 hugo.toml 后 `hugo server` 未热更（服务还活着但吐旧内容）→ 配置变更后必须重启
dev server；`hugo config` 可先验证 Hugo 侧参数是否可见。

九项全绿；基线重建（footer+schema 全站组件，584 页均变属预期）；图标 2x 截图核验形状。

## 已完成（参数总表长尾标题 + 行动号召按钮，2026-10-05 第三十二轮）

**① H2 长尾化**：`Compare every code on one grid` → `Compare every eSIM promo code side by side`
（与 H1「eSIM promo codes & deals 2026」错位覆盖「compare esim promo code」搜索意图；
无逗号/破折号，过 check_headings）。en/de 成对。

**② 参数总表每行加 CTA**：Best code 列在码下方加 `Use code at {brand}` 按钮
（复用全站唯一出站出口 `cta-out.html`，rel=sponsored nofollow + UTM 由 hugo.toml targets 驱动，
target=$key 深链到品牌官网 base）。i18n key `esim_deals_list__params_cta`（带 {{ .brand }} 占位），
en/de 成对。8/8 按钮产物核验。

九项全绿；基线 diff = deals 1 处（预期）；已重建。

## 已完成（header 品牌图标 + footer 宣传语重写，2026-10-05 第三十一轮）

**① header logo**：`header.html` 原「ink-950 圆角块 + 内联 SVG 漏斗」→
`<img src="/apple-touch-icon.png">`（PNG 自带青绿圆角底 + 白漏斗，与 favicon 同源），
保留 hover 旋转。footer 左上 logo 未动（用户只点名 header）。

**② footer 宣传语**：`footer.html` 改为只渲染 `partials_footer__blurb`（去掉 tagline 前缀拼接，
tagline 参数保留仍喂 `<title>`/og）；en 换新定位文案
（"We don't rank by ad spend — we rank by who's actually cheaper. …"），de 成对译德语（du 语气）。

九项构建全绿；基线重建（header/footer 全站组件，584 页均变属预期）。

---

## 待办（按优先级）

### P-2 蓝图 Phase 2（等 P-A 真实数据后；见 docs/keyword-map.md 预留槽位）

- [ ] 区域枢纽页 ×5（/compare/{region}/）
- [x] ~~单国运营商深度页~~ **2026-10-03 起做：`/networks/{country}/` Japan 完成（1/50）**，模板已固化，余 49 国加 content md 即可（见上节）
- [ ] /networks/{carrier}/ 运营商页、/devices/{device}/ 设备页
- [ ] tools 再加 2 个、sitemap 分片（>1000 URL 时）、国家页 authority 外链

### P-A 数据收尾（价格已全真 ✅，剩非价格项）
- [ ] **`/networks/*` 的 `Updated` 徽章取 `now`（构建日）**（2026-10-05 发现）：`layouts/networks/single.html:115` 每天构建都变 → 12 页天天进回归 diff、且与第二十五轮「日期跟数据走」原则冲突；`check_dates.py` 未覆盖 /networks/。改法需先定数据口径（网络快照核对日），再纳入严格模式
- [x] ~~**抓取队列**~~ 已全量完成：8 品牌 × 50 国 = 400 raw JSON = 8776 条真实套餐（esimdb 七家 + holafly 官网 PDP + roami 本地提取）；`validate.py` 0 error 0 warning，无 SAMPLE
- [ ] networks 逐品牌补真（esimdb 不展示网络名；airalo.com 国家页有 host networks 可抓，其余品牌官网同理）
- [x] ~~**折扣码换真**~~（2026-10-01 完成，见上轮日志；遗留：3 家 promo_expires 占位 2027-12-31 需上线前复核）
- [ ] 四家联盟深链规则补进 `[params.outbound.targets.*]` 的 `country_path` + `countries.toml slugs`（当前 `<slug>-esim` 是模式假设）
- [ ] 逐国 quirks 人工复核（生成内容基于真实常识，但上线前过一遍）
- [ ] `data/carriers.toml` 50 国画像逐国人工核对（本轮已全覆盖 ~154 profiles，但速度区间/覆盖特性为编辑常识典型值，P-A 上线前逐市场核实）

### P-B 内容生产线
- [ ] 49 国 3 段分析的人工润色（生成器已产出可读初稿，japan.md / jp.toml 为手写样板；数字全部由数据计算而来，改数据重跑生成器即可刷新）
- [x] ~~**49 国 6 条 FAQ**~~ 已数据化 + 去模板化：三条带数字的答案走构建期 token 现算（第四十一轮），句架走 `faq_frames.py` 拉丁方阵分配 ⇒ 任意两页最多共用一句（第四十二轮）。**接品牌 / 刷价之后不需要再动 FAQ**。遗留：slot4「ID 规定」14 国同句（缺外部来源，不编）
- [ ] 变体子页（cheapest/unlimited/long-stay）— 等主站数据 ≥10 国再上，防关键词蚕食

### P-C 上线前
- [ ] privacy/terms 法律审校（文中已标注 Todo）
- [ ] GA4 ID 替换 + 与 roamiapp.com 跨域衡量（head.html 占位注释处）
- [ ] OG 图片（每国一张，含最低价数字）
- [ ] 部署（Cloudflare Pages 建议；`/go/` 边缘函数跳板可后加）
