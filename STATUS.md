# eSIM Sift — 项目状态

> 独立 eSIM 比价站。单一数据源（`data/*.toml`），模板层推导一切派生指标。
> 基座：Hugo 0.159.1 + Tailwind CLI。语言：英语（目录结构已为多语言预留）。

## 命令

```bash
npm run build     # 数据验证 → Tailwind → hugo（上线前的完整管线）
npm run dev       # Tailwind 预编译 + hugo server
python scripts/validate.py   # 单独跑数据层验证
```

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

## 待办（按优先级）

### P-2 蓝图 Phase 2（等 P-A 真实数据后；见 docs/keyword-map.md 预留槽位）

- [ ] 区域枢纽页 ×5（/compare/{region}/）
- [ ] /networks/{carrier}/ 运营商页、/devices/{device}/ 设备页
- [ ] tools 再加 2 个、sitemap 分片（>1000 URL 时）、国家页 authority 外链

### P-A 数据采集（最大决策点 — 除 JP-Roami 外全部 ⚠ SAMPLE）
- [ ] 抓取队列收尾：yesim / ubigi / roamic / alosim（esimdb，后台队列中）→ holafly（官网 PDP）→ roami 49 国（自家数据，roamiapp.com 或用户提供；airalo/saily 已完成 50/50 入库）
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
