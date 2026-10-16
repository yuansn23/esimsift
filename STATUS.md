# eSIMSift — 项目状态

> 独立 eSIM 比价站。单一数据源（`data/*.toml`），模板层推导一切派生指标。
> 基座：Hugo 0.159.1 + Tailwind CLI。语言：**英语（根路径）+ 德语（`/de/`，2026-10-10 第七十二轮 D9 解禁，
> 无 noindex）** —— ✅ **德语站已全量落地：`content/de` 656 个文件（644 个提交于 2026-10-10 的 `3b0d4af`，其余为后续各轮的 networks 新页），全站 noindex = 0**（2026-10-11 第八十二轮复核实测）；i18n **1907 key**（en = de 逐 key 同序对齐，未定义 0）。**产物 1317 页**（2026-10-16 第一百轮实测）。
> **`npm run validate` 现有 6 道源码层闸门**（第七十八轮新增 `check_printf_arity` / `check_headings_source`，第九十轮新增 `check_page_container`，见对应小节）；
> **`npm run check:output` 现有 13 道产物闸门**（第十三项 `check_inline_copy.py` = 2026-10-11 第八十一轮新增）。

## 命令

```bash
npm run build     # 数据日期自动盖章 → Tailwind CSS → 数据校验 + CSS 同步校验 → hugo → 产物校验（上线前的完整管线）
npm run dev       # 同上（含盖章）+ hugo server
npm run stamp     # 单独跑「数据变了就把核对日推到今天」（见 §4.3；台账 docs/checked-state.json 必须提交）
npm run validate  # 单独跑校验（validate.py + check_css_sync.py + check_i18n.py
                  #   + check_printf_arity.py + check_headings_source.py + check_page_container.py）—— 6 道，秒级，构建前拦
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

## 已完成（GSC 7 天诊断的 P0 全量落地 + P1 首批 3 国，2026-10-12 第八十五轮）

**触发（用户逐字）**：`请你把P0-P1 全部优化， 记得德语的也一起优化`
**用户澄清**：① P0 标题 → `守卫 verify_provider_pages.py 里有 TITLE_BANNED 硬规则：标题里禁止出现 $ 和「N plans」 这个废除。description 重写`；② P1 规模 → `先做证据最强的 12 国`

### P0｜排列页 SERP 摘要重写（998 页 = en 499 + de 499，承担全站 40% 展示）

| 项 | 结果 |
|---|---|
| **废除 `TITLE_BANNED`** | `verify_provider_pages.py`（22396 → 22571 B）删掉 3 条正则与检查循环，注释记录「代价：标题由构建期现算，**每次数据变动都会改标题**，是刻意取舍，复现时不要当回归」 |
| **description 全量重写** | 删净 `(#N of M)`（命中 998 → **0**）；en/de 双向 **499/499 落在 120–140**；**零重复**；必含 `eSIMSift` |
| **SERP 标题（新增 `seo.title`）** | en `44–54: 499/499`（48–54: 478）· de `44–54: 499/499`（48–54: 480）；**零重复**；必含国名；纯不限量品牌（Holafly）丢关键词 **0** |
| **模板零改动** | 走 `head.html` **已有的标题锁**（`$lockedTitle`）⇒ `title`（H1）与 `seo.title`（SERP）从此是**两个字段、两个面**：H1 留 `Plans & Prices`，SERP 带套餐数/天数档/起价 |
| **顺手拆掉一颗地雷** | `gen_provider_pages.py` 的 `NOINDEX = LANG != "en"` 整体移除（否则**下次重跑生成器会把 499 个德语页的 noindex 复活**）；同时清掉 499 个德语 md 里过期的 `TODO(de)` 注释 |
| 样例 | `Saily Canada eSIM: 11 Plans, 5-30 Days, From $5.29` / `Saily Kanada eSIM: 11 Tarife, 5-30 Tage, ab $5.29`；desc：`All 11 Saily plans for Canada in one table: 5-30 days from $5.29, $2.20/GB at the cheapest tier. eSIMSift prices every option in one table.` |

### 逐字节归属法（红线 99/106）—— 本轮做到「旧产物与基线全等」这一层

1. `git archive HEAD content` 导出旧内容树（先证明 **已跟踪 1288 = 在盘 1288、未跟踪 0**）
2. **★ 坑：`hugo.toml` 的逐语言 `contentDir` 会静默压掉命令行 `-c/--contentDir`** ⇒ 第一次重建出来的「旧产物」其实是新内容，归属脚本因此报**假阳性的「0 处变化」**。正解：`hugo --config hugo.toml,.buildlog/r85_oldcfg.toml -d <目标>`
3. 旧产物 vs `docs/regression-manifest.json`：**1291/1291 逐字节全等**（同时证明「基线就是改造前状态」+「构建可确定复现」）
4. 新产物 vs 旧产物（`.buildlog/r85_attrib2.py`）：

| 断言 | 结果 |
|---|---|
| A 文件集合 | common 1291 / 新增 **0** / 删除 **0** |
| B 变化文件 | **998 个，全是排列页**；非排列页变化 **0** |
| C 差异行数 | **每个文件恰好 4 行**（`<title>` / `<meta description>` / `og:title` / `og:description`），**零越界** |
| D 产物↔md | 998 页 × 4 个值全部等于 md 的 `seo.title` / `seo.description`，不符 **0** |

`verify_no_regression.py --diff` 复核：**变更 998 = provider_sub=998 · 新增 0 · 删除 0**。基线已刷新。

### P1｜networks 国家页扩量（首批 3 国：Colombia / Croatia / South Africa）

- **数据源就位度实测**：`data/carriers.toml` 50 国全有 profiles；`data/networkreports.toml` **47 国**（缺 `IS`/`GE`/`KE`）；`data/de/networkreports.toml` 德语覆盖 **45 国**（缺 `AE`/`QA`/`EG`/`GE`/`KE`/`SA`/`VN`/`TW`/`MA`… 见下）
- **★ 目标 12 国里有 10 国德语数据已就位**（CO/HR/ZA/EG/TW/VN/MA/PL/CH/SA）；**KE 与 GE 连英语报告都没有** ⇒ 这两国缺「独立实测」事实源，不能编
- 首批 3 国（按 7 天展示量 CO 79 / HR 55 / ZA 50 = 184，占 12 国 382 的 48%）已写完 en + de 共 6 页（每页 ~15KB，含 8 条带真实数字的 FAQ + 3 城市覆盖实况 + 网络维度结论层）
- **事实全部外部核实**（WebSearch 一手/二手交叉）：哥伦比亚 = 预付费强制护照登记 + CRC 设备 IMEI 注册制（国际漫游豁免）+ Claro eSIM 仅后付费；克罗地亚 = 预付费护照登记 + 边境（波黑/黑山/塞尔维亚）不在 EU 漫游区；南非 = **RICA 强制登记且明确覆盖 eSIM**（Vodacom 官方口径）+ 外国护照 + 可能追加地址证明
- 新增源码级预检脚本 `.buildlog/r85_p1_preflight.py`（shortcode 存在性 / 德语禁英文国名 / 德语禁英文城市名 / H2 标点 / `cities_detail` 起首 / 换行），**当场抓到 1 处德语 H2 逗号**


#### P1 首批验收（构建 2 + 产物断言 + 归属法 v3）

| 项 | 结果 |
|---|---|
| 构建 2 | `BUILD_EXIT=0`（9m26s）· **1297 pages**（1291 + 6）· hreflang 3882 标签 / 1294 页 · 品牌×国家子页 / R10·R11 骨架不重复 / 语言闸门 **全绿** |
| 产物断言 `.buildlog/r85_p1_verify.py` | 6 页 × A–H 全过：`<title>`+`og:title` == `seo.title`、`description`+`og:description` == `description`（**逐字**）；hreflang 三向自洽（`en-us`/`de-de`/`x-default`）互指同 slug；canonical 自指；**日期三处同源 = sitemap lastmod = 2026-10-07**；德语页用德语国名 |
| **★ 日期口径澄清** | front matter 的 `date`/`lastmod`（2026-10-12 = **页面创建日**）**不参与渲染**；networks 页三处日期（徽章 / sitemap lastmod / 脚注）同源取 `$s.checkedDate`（**数据核对日**），既有页同样写 `date: 2026-10-03` ⇒ 惯例一致，非缺陷 |
| 归属法 v3 `.buildlog/r85_p1_attrib3.py` | 见下表 |

**★ 归属法连挂三次才立住（全部写进 `PROJECT.md` 红线 115）**：

| 版本 | 结果 | 真因 |
|---|---|---|
| v1 | 报 **1290「越界」** | 白名单写窄：**没意识到全站导航是数据驱动的** |
| v2 | 仍报 1290 | 只 mask 了**第一个** `nav-mega`（导航分布在桌面 mega menu / 移动菜单 / footer 多处） |
| v3 | **全过** | 规范化比对 = 删 `mega-link` 锚点 + 占位计数 + 折叠循环空白 |

最终断言：

| 断言 | 结果 |
|---|---|
| A 集合 | 新增 **6**（3 国 × 2 语言，en/de 成对）· 删除 **0** · 共有 **1291** |
| B 完全不变 | **1223 页逐字节相同** |
| B2 可归因变化 | **68 页** = `compare/{CO,HR,ZA}/*` 66 + `/networks/`·`/de/networks/` 索引 2；差异行 **100% 含 networks 内链** |
| B3 越界 | **0** |
| C 计数 | 每页**恰好一处** +3（12 → 15），其余计数（13/18/8/8/3/6）**纹丝不动** |
| D P0 成果保护 | 998 个排列页 = **938 逐字节不变 + 60（全为新国）内链升级** ⇒ **零误伤** |

数学闭环：60 + 8 = 68；1223 + 68 = 1291。`verify_no_regression.py --diff` 报「非品牌子页变化 298」= 292 逐字节变化 + 6 新增，与此一一对应；基线已 `--write-manifest` 前进到 **1297 文件**（`generated_at 2026-10-12T07:19:27Z`）。

**★ 由此得到一条新成本事实**：`/networks/<slug>/` 一旦存在，模板会**自动**把对应 `compare/<国家>/` 页里那条指向 `/networks/` 索引的说明句升级为指向该页的内链 ⇒ **每新增 1 国 networks 页 = 全站 1297 页导航重生成 + 该国 22 个 compare 页内链升级**。这不是缺陷，但决定了「加一国」的真实构建代价。
### 本轮新发现、**尚未修**的三件事

1. **★ 正文里另有三处同款「自我否定」**（P0 只改了 meta）：① `compare_provider__verdict_met_rank` 印 `… rank #9 of 10; the country benchmark is …`；② FAQ 答案 / JSON-LD `compare_provider__faq_a_price_met` 印 `… which ranks #9 of 10 providers we track for this destination.`；③ 产物含 `of 10` 的页 = en `compare` **511** + de `compare` **540** + networks / esim-providers / esim-deals / guides / 首页若干。**Google 会从正文抽摘要 ⇒ 只改 meta 修复是半残的。**
2. **★ `opensignal_title` 是「机器字段」误判（与 `opensignal_date` 同构，后者已修）**：`verify_de_data.py` L242 明令**禁止**德语侧写 `opensignal_title`（判为机器字段应继承英文），但 `layouts/networks/single.html` 把它当**可见链接文字**渲染。产物实测：**11 个德语 networks 页全部印出英文报告标题** `… , <Month> <Year>, Mobile Network Experience Report`。**本轮产物断言实测：新增 3 个德语页各印 1 处 ⇒ 受影响 = 原有 11 + 新增 3 = 14 页**。**根因**：`verify_de_text.py` 的英语国名判据只在**源级 C 判据**与 `/de/compare/<国>/` 的 **E 段**生效，而 F 段（全站德语页）的单词表**不含国名** ⇒ **networks 产物根本不在覆盖范围**，所以「构建全绿」与「德语页印英文报告标题」可以同时成立。**修法**（照 `opensignal_date` 的先例）：把它移出机器字段清单 → 德语侧逐国补 `opensignal_title` → 守卫 `--selftest` 两侧都证。
3. **工具坑：bash heredoc 会吞掉反斜杠转义**（实测 `\s` 落盘成 `/s`，脚本静默失效）。**`.buildlog/` 下的脚本一律用 Write 工具落盘**，或刻意不写反斜杠（用 `[ ]` 字符类、lambda 代替 `\1` 反向引用）。

→ 上面第 1、2 两项**已在第八十六～八十七轮修复**（正文 `#N of M` 三处清零 + 德语报告标题逐国补齐），见下一节。

### 纪律
- **未 `git commit`、未部署**（改动全部留工作区）
- 改已存在文件全部 bytes 读写并复核换行；`content/en|de/compare/*.md` 998 个由生成器重写，**en 499 纯 CRLF / de 499 纯 LF，零混合**；`content/*/networks/*.md` 本目录实测**两侧全 LF**（与 `compare/` 不同，按文件不按目录猜）
- `stamp_checked.py` 指纹只覆盖 `data/plans/**` 与 `data/providers.toml` ⇒ 本轮改 md/scripts **未误盖任何 `checked` 日期**

## 已完成（四页型「新鲜度 / 可探索性」补强；用户 13 条逐条核到源码/产物级，2026-10-13 第九十轮）

> 用户本轮逐字：`你帮我看看这些如何优化，能修改渲染模板是最好， 这样就不需要动数据文件，当然一定要动数据文件也可以，怎么方便怎么来 记得同时要兼容德语的`
> （AskUserQuestion 应答）执行范围 → `全部真缺项（推荐）`

### 1｜先把用户清单逐条核到源码 / 产物级 —— **3 条已成立、1 条做不到**

| 用户判断 | 实测结论 |
|---|---|
| 首页·三步后缺交互入口 | ✅ 真缺 —— 三步之后直接跳「信任」段，大 CTA 远在页尾 |
| 首页·无「最近更新」 | ✅ 真缺 —— 全页只有一句 `home__prices_checked` |
| `/compare/`·无排序筛选 | ⚠️ **部分不成立** —— 区域 chip + 国家级搜索框 + 搜索索引数据岛**已有**；真缺的只有**国家网格排序** |
| `/compare/`·缺热门目的地 | ✅ 真缺（但 `countries.toml[ISO].featured = true` 已是现成真源，**实测 12 国**，无需新数据） |
| 国家页·缺叙述性内容 | ⚠️ **部分不成立** —— `#verdict`（3 卡结论）+ `#bytrip`（行程档位 + 4 种人物画像各带 why）已有 |
| 国家页·底部缺指南交叉链接 | ❌ **已存在** —— `#guides` 区已有 5 张指南卡 + 轮换锚文本 + blurb（`$rot := mod (len $country.slug) 3`） |
| 国家页·价格趋势 | ❌ **做不到（诚实告知）** —— `data/plans/*.toml` 每个 (品牌, 国家) 只存**当前价 + 核对日**，**零历史价点**；要「最近降价」必须先建历史快照层，且**只能从今天起积累、回填不了过去** |
| 指南页·索引无预告 | ✅ 真缺 —— 原先只用 `.LinkTitle`，front matter 里现成的 `.Description` 完全没用上 |
| 指南页·数量偏少 | 事实（guides 10 篇 + research 3 篇）—— 属**内容生产**，非模板问题 |
| 方法论·可视化标注 | ✅ 可做 —— 但**用真实数据现场渲染**，不做截图（截图会过期，且本站没有这类资产） |
| 方法论·数据更新日志 | ✅ 可做**真台账**（`plans/*.toml` 的 `checked` 现算；数据里只有 2 个日期，回填不了更早） |

### 2｜改动点（**四个页型，纯模板层 + i18n，零新数据文件**）

| 页型 | 改了什么 | 文件 |
|---|---|---|
| 首页 | ① 三步之后的**行动条**（三按钮；措辞与 hero 的两个按钮**故意不重复** —— 同页同一目标的锚文本重复会稀释排名信号）② `#latest-updates` **最近更新三卡**（三个数据面各自的最后核对日；脚注链 `/methodology/#updates`） | `layouts/index.html`（2 处） |
| `/compare/` | ① `#featured-destinations` **12 国 chips**（真源 `featured`，带国旗 + 该国最低价；**刻意叫 Featured 不叫 Popular** —— 本站没有访问量数据）② `#sort-chips` **客户端排序四档** | `layouts/compare/list.html`（4 处）+ `partials/country-card.html`（新增 `data-price` / `data-count`） |
| `/guides/` | 索引从 `.LinkTitle` 单行链接列表 → **分组卡片**（按 `layout: region` 分「区域指南 5 / 基础指南 5」；每卡 description + `min read` + `Reviewed <日期>`） | `layouts/_default/list.html`（整文件覆写） |
| `/methodology/` | 新建专用版式：`#anatomy` 一行**真实套餐**的字段解剖（6 编号字段卡 + 7 条来源图例）+ `#updates` **数据更新日志** | `layouts/_default/methodology.html`（新建）+ `content/{en,de}/methodology.md` 加 `layout:` / `example_iso:` |

i18n：**+49 key ×2**（en 201072 → 204725 B、de 217718 → 221636 B），**key 集合 1904 / 1904 完全对齐**。
四个页型的**新区块 id 全部不在** `verify_no_regression.py` 的 `MARKER_ALLOWED` 表内 ⇒ 无需登记、也不该登记（登记 = 宣布它是「跨页型共享区块」，而它们各自只属于一个页型）。

### 3｜四条设计决策（都写进代码注释，避免下一轮被「优化」掉）

- **首页「最近更新」按数据面（3 个）而非按国家** —— 实测 50 国的 `max(checked)` **全部 = `2026-10-07`**，按国家做零信息量；三张卡的日期**本来就不同**，合并成一个日期就是不实陈述
- **compare 排序首档叫 `Featured first` 不叫 `A to Z`** —— 网格默认序其实是各国 compare 页 front matter 的 `weight`（编辑序，实测首三 `united-states / united-kingdom / france`），叫 A to Z 就是假标签
- **排序只重排 DOM、不改 display** —— 与区域 chip / 搜索过滤互不干扰；`serverOrder` 先把服务端序存下来，所以「Featured first」能原样还原（不是再排一次猜）；**无 JS 时保持服务端序，控件不生效但页面完整**
- **指南标题不进 `<h3>`**（含冒号会触发 `check_headings.py`）+ **方法论页另开模板**（不动服务五页的 `_default/single.html`）+ **`example_iso` 走 front matter**（不把国别写死在模板里）

### 4｜三次构建失败 → 三个**真缺陷**（没有一个是「配置问题」）

| # | 报错 | 真因 | 修法 |
|---|---|---|---|
| d1 | `baseof.html:24:1: apply base template failed: template: list.html:24: comment ends before closing delimiter` | 模板注释里写 `content/**/guides/*.md`（`*` 紧跟 `/` 就是 `*/`，Go 在第一个 `*/` 处提前闭合注释） | 改 `content/&lt;lang&gt;/...`；同步修 `index.html` 的 `content/*/networks/*.md`。★ **源码层 5 道闸门全是正则式的，一条都拦不住这种错**，只有 Hugo 真解析模板才报（→ §14 红线 128） |
| d2 | `error calling sort: desc is neither a struct field, a method nor a map element of type string` | `sort` 的 `"desc"` 只对 map / struct 切片成立；`[]string` 不支持三参形态 | 改为「升序 + 反转」；**最小站点夹具**实测（→ §14 红线 129） |
| d3 | `check_inline_copy.py` FAIL：`1 条可疑字面量 'plans'`（`de/compare/index.html` 脚本体） | 排序键取名 `plans`，撞该守卫的单 token `EN_STRONG` 封闭词表 —— **判据对了、命名错了**（机器 token 与英语自然词同形） | 改名 `count`（`data-count` / `'count'`）；**不是**去给守卫加白名单（那等于削薄一条真捕到过缺陷的防线）。连带：注释里也不许带引号写该词（→ §14 红线 130） |

### 5｜验收（全部产物文本断言，按约定**不做截图**）

- **全量 `npm run build` EXIT=0**，**13 道产物闸门全绿**（`hugo` 阶段 Total in 414 s —— ★ 更正：这是 Hugo 自报的**渲染段**耗时，且同机近七次实测 233–591 s 波动由负载主导，**本轮不作「变慢」论断**；上一轮 r89 实为 483 s，此前写的「244 s」既非上一轮口径也不可比）
- 规模：`1315 files (1313 pages)` · `7526 JSON-LD` · `34148 h2/h3 bad: 0` · 499 品牌子页全过 · `hreflang 3930 条 / 1310 页` · `sitemap 655 URL` · `i18n 1904 key en=de` · 德语 `F/G 全绿（655 页）· check_inline_copy 脚本体 0 残留`
- 新增 `.buildlog/r90_assert.py`：**74 项产物断言全绿**（期望值全部**现算** —— 价格库日期从 `plans/*.toml` 现算、Featured 集合从 `countries.toml` 现算、网格序从 front matter `weight` 现算、更新日志行数与计数从 `checked` 现算；**不抄常量**）。★ 首跑 12 项红，**逐条查清全是我的断言路径少写一个前导斜杠**（产物正确）—— 又一次印证「验收脚本的 FAIL 先查断言，再查产物」
- **归属（逐字节）**：`verify_no_regression.py --diff docs/regression-manifest.json` 报 **变更 8 / 新增 0 / 删除 0** —— 恰好 = 4 页型 × 2 语言（`index` / `compare/index` / `guides/index` / `methodology` 各 en+de），**与预期逐一对应，零意外变更**
- 基线重建 **1313 文件**，复跑 `--diff` **0 / 0 / 0**（构建确定性自证）
- **★ 高危告警（本轮已修）**：开工时实测 `public/` 有 **1337 个文件**含 `http://localhost:1313/`（`public/index.html` 的 canonical、`sitemap.xml` 的 `<loc>` 全是 localhost；时间戳 13:07–13:09，上一轮干净构建是 12:30）⇒ **裸 `hugo server` 写盘**。这份 `public/` 一旦部署 = 告诉 Google 站点搬到了 localhost。本轮全量构建已重写整个 `public/`，收工断言 `localhost` 计数 = **0**；今后**预览只用 `npm run dev`**（带 `--renderToMemory`），永不手敲 `hugo server`（→ §14 红线 131）
- **诚实说明**：**没有字节级旧快照可做「块级替换」深证**（改动前的 `public/` 正是被污染的 dev server 产物，页页 sha 都不等于基线）⇒ 归属证据链 = 页级 sha256 三分类 diff（8/0/0）+ 74 项产物断言 + 13 道产物闸门

### 6｜纪律与登记

- **未 `git commit`、未部署**（改动全部留工作区）
- 改已存在文件全部 **bytes 读写 + 复核换行**：`i18n/{en,de}.toml` 两侧**纯 LF**；`layouts/{index,_default/list,compare/list,_default/methodology,partials/country-card}.html` **纯 LF**；★ **`content/en/methodology.md` 是 CRLF、`content/de/methodology.md` 是 LF**（同目录不同格局 —— 又一次证明「按文件实测、别按目录猜」）
- **未动但登记在案的观察项**：`layouts/_default/list.html` 的指南卡复核日已改用 **front-matter-only** 口径（`or .Params.lastmod .Params.date`），而 `layouts/guides/single.html:83` 的「Last reviewed」仍用 `.Lastmod`。两者**当前取值相同、产物零差异**（10 篇指南都只写 `date` 不写 `lastmod`），但那是「同一事实两处推导」—— 待哪天某篇两字段皆缺时会分叉（`.Lastmod` 会落回文件 mtime 而撒谎）。属独立决策，本轮**未改该文件**
- **下一轮可选**：① 首页`#latest-updates` 的「网络实测」卡目前取的是 networks **页级发布日**的最大值（现为 `2026-10-13`）——值得确认它在读者眼里是否等价于「测速数据的新鲜度」；② `/compare/` 的排序在前端完成，若将来要 SEO 友好的排序落地页（`/compare/cheapest/` 之类）属**新页型**，需先点头；③ 指南扩篇（内容生产）

## 已完成（品牌全站统一 `eSIMSift` + 指南索引图文卡 + 正文去吸顶 + 作者头像 + 城市长尾，2026-10-15 第九十四轮）

**用户指令**（逐字，5 条）：① `eSIM Sift Data Team` 需要一个头像，可以就使用 logo；② 这个页面右侧的 2 个模块，不要搞成吸顶的效果；③ 这个 esim-new-york 的文章是植入了哪些关键词，有 usa esim 吗，以及该国家 esim 长尾词吗；④ `/guides/` 这个页面都是标题和描述的文章，需要他们对应的图片也显示出来，一排 3 个文章即可；⑤ 首页 `<title>` 里的 `eSIM Sift` 为什么要分开，不能 `eSIMSift` 吗 —— 用户只会输入 `eSIMSift`，中间不会有空格。

★ 经 AskUserQuestion 由用户拍板两件：**品牌改动范围 = 全站一致**；**文章关键词 = 补城市长尾**。

### 1｜品牌全站统一 `eSIM Sift` / `eSIM-Sift` → `eSIMSift`

- 依据：页头字标本来就是 `{{ i18n "g_esim" }}{{ i18n "g_sift" }}` = `eSIMSift`（无空格）、与域名同形 ⇒ `<title>`／页脚／元数据写「eSIM Sift」是**站内自相不一致**
- 规模：**1281 个文件 / 1427 处**（content 1255 / scripts 13 / docs 5 / i18n 2 / layouts 2 / hugo.toml 1 / static 1 / PROJECT.md、STATUS.md 各 1）；逐文件 **bytes** 读写，`count(b"\r\n")` **逐文件守恒**
- 必须同步（不改就出事）：`scripts/verify_provider_pages.py:202` 是**构建闸门**（硬要求 provider 描述含品牌，不改直接挂构建）；`scripts/_de_link_leak_audit.py:191` 存着 `llms.txt` 的**期望值** `"# eSIM Sift\n"`；`gen_provider_pages.py` / `gen_vs_pages.py` / `regen_meta_*.py` 是**内容生成器**（下次一跑就覆盖回去）；`audit_meta.py:16` 的 `BRAND`
- 排除区：`scripts/__pycache__/`（`.pyc` 是产物）、`docs/internal/`（历史归档，改了就**假造历史**）
- **连带修复**：`content/en/terms.md` 描述因品牌短 1 字符由 **120 → 119**，回填为 **124**（`our price-data` → `our full price-data`）—— 否则违反 `audit_meta.py` 的 120–140
- **盲替换副作用（已修）**：`STATUS.md:1669` 原写「用标准拼写，不拆成 X 两种写法」，替完全句**自相矛盾** ⇒ 改为「不拆成『带空格 / 不带空格』两种写法」
- **未改**：`g_esim` / `g_sift`（页头**双色字标故意两段**，合并会丢设计）；`docs/internal/` 4 个历史文件

### 2｜指南索引 `/guides/`：卡片加配图 + 一排 3 个

- `layouts/_default/list.html`（**guides 是唯一回落该模板的 section** ⇒ 爆炸半径 = 2 页）：`sm:grid-cols-2` → `sm:grid-cols-2 lg:grid-cols-3`；`gap-3` → `gap-5`（带图后 12px 太挤）
- 配图取 front matter **已有的 `hero`** —— 11 篇指南 en/de **全部已有**，**零内容改动**；宽高走 `imageConfig` 实测值防 CLS；全部插图统一 **2848×1470（1.9374）** ⇒ 用 `h-auto w-full` **原生比例、零裁切**，各卡高度天然一致
- 产物实测：en/de 索引各 **11 张图**、`lg:grid-cols-3` ×2（两个分组）；11 张全带 `alt="" width="2848" height="1470" loading="lazy"`

### 3｜指南正文右侧两模块去吸顶

- `layouts/guides/single.html`：`<div class="sticky top-24 max-h-[calc(100vh-7rem)] overflow-y-auto pr-1">` → `<div class="pr-1">`（两处注释同步改，别留假话）
- 产物实测：24 个 guides 页里含 sticky aside 的 = **0**；用 `guides/single.html` 的 6 篇 × 2 语言 = **12 页**含 `<div class="pr-1">`（5 篇区域指南走 `guides/region.html`，本就无侧栏）
- **未误伤**：`compare` 侧仍保留 sticky 的 **50 页**（`layouts/compare/single.html:1215` 同款类串仍在用）

### 4｜作者卡头像（E-E-A-T）

- `layouts/partials/author-box.html`：加 48×48 圆形头像，源文件 `/apple-touch-icon.png`（**180×180**，与页头字标、`schema-org.html` 的 Organization `logo` 是**同一份品牌资产**）；`alt=""`（紧随其后的 `<h2>` 就是同一个名字，重复朗读是噪音）
- 产物实测：两篇 `esim-new-york`（en/de）均命中头像类串

### 5｜文章补齐城市长尾（用户第 3 问的答复 + 执行）

- **实测答复**：核心词 `esim new york`（正文 **13** 次 / 全文件 25 次）；**`usa esim` 正文仅 1 次** —— 这是**刻意**的，按既定防蚕食规则归 `/compare/united-states/`；城市长尾 `best/cheapest eSIM for New York` 原为 **0 次**（真实缺口）
- 执行：在「Which eSIM to buy for a New York week」首段补 **`cheapest eSIM for New York` ×2 + `best eSIM for New York` ×1**；德语镜像 **`günstigste eSIM für New York` ×2 + `beste eSIM für New York` ×1**
- EN 正文 **2500 词** / DE **2308 词**；**H2=9、H3=5 未变**（ItemList 只抓 `.Content` 的 H2，不受影响）；EN/DE 标题层**逐条同构 14/14**、front matter **14 键同序**

### 6｜验收

- `npm run build` **`BUILD_EXIT=0`**；`hugo` 段 **`Total in 209351 ms`**（口径同前：是 hugo **渲染段**，不是 `npm run build` 墙钟）
- **13 道产物闸门全绿**：`1317 files (1315 pages)` · `7538 JSON-LD` · `34212 h2/h3 bad 0` · 499 品牌子页全过 · `hreflang 3936 条 / 1312 页` · `sitemap 656 URL` · i18n 1907 key en=de · 德语 F/G/J 全绿（656 页）· 语言泄漏 0 · **`livereload` / `localhost` 计数 0**
- **逐字节归属**：把旧快照的 dev-server 污染与三处已知成因归一化后，**1309 / 1315 页逐字节全等**；余 **6 页全部是「本轮有意改动」**（2 篇文章 + `terms` + 2 个索引页）
- **基线刷新 → 1315 文件**，复跑 `--diff` = **0 / 0 / 0**；`--diff` 对旧基线报 **变更 1314 / 新增 0 / 删除 0**，唯一未变的正是 `alias_shell`（270 B 裸跳转壳，本就不含品牌）

### 7｜★ 本轮两次「派生量」差点被当成外溢

- **自动派生锚点 slug**：`## Why eSIM Sift exists` 的 `id` 由 Hugo slugify 成 `why-esimsift-exists`（2 页：`/about/`、`/de/about/`）
- **`.ReadingTime`**：`eSIM Sift`(2 词) → `eSIMSift`(1 词) ⇒ 正文每出现一次 **-1 词**；5 篇指南各 -1 词，只有 `how-to-install-esim` 压在 213 整数倍边界 ⇒ `10 min` → **`9 min`**；`esim-new-york` 因加长尾句 2343 → 2410 词 ⇒ `11 min` → **`12 min`**；索引卡「N min read」随之变
- ★ 已写进 `PROJECT.md §14` **红线 140–143**

### 8｜★ 旧快照是「混合态」（本轮归属的最大障碍）

- 开工时 `public/` 是**裸 `hugo server`** 写盘的**第 4 次**（红线 131 与第九十轮日志已两度记载）：1314 页含 `livereload.js`、1315 页含 `localhost`
- 更麻烦：它是**混合态** —— 用户当时浏览过 `/guides/` 与 `/guides/esim-new-york/`，这两页已被重渲染成「模板改后」，其余仍是「模板改前」（还带 sticky aside）⇒ **不能整树当基线**（B 组残差里恰好缺 `guides/esim-new-york`（en）、却含德语版，反过来印证了这一点）
- 处理：污染归一化后逐字节比对；模板类改动改用**产物结构断言**直接证（guides sticky = 0 / `pr-1` = 12 / compare 侧 50 页仍 sticky）
- 快照放在**仓库外** `D:\esimsift\_r94_prev_html`（1315 个 HTML / 250.8 MB）

### 9｜纪律与登记

- **未 `git commit`、未部署**（改动全部留工作区，HEAD 仍 `5b7bac4`）
- 改已存在文件全部 **bytes 读写 + 复核换行**：`content/**` 1255 个（多数纯 LF；★ `content/en/terms.md` 是 **CRLF** —— 又一次「按文件实测、别按目录猜」）、`hugo.toml` / `i18n/*.toml` / `layouts/**` 纯 LF，**逐文件 CRLF 计数守恒**
- 新增红线：**140**（改名类改动必算四件事：长度下限 / 德语连字符形态 / `.py` 生成器与闸门常量 / 对比式表述）、**141**（`public/` 归属先验证再当基线）、**142**（品牌字串与页头字标是两件事）、**143**（派生量：slug / ReadingTime / 索引卡时长）
- **登记未动**：① `content/en/_index.md` 首页 title **46 → 45** 字符，**本就低于 `audit_meta.py` 的 48–54 带**（改名使它更远；建议加 ` 2026` → 50 字，未做，等你点头）；② **57 条 description 本来就 >140**（德语国家页 —— `audit_meta.py` 非构建闸门，所以一直没人拦）；③ `layouts/guides/single.html:83` 的 `.Lastmod` 与索引卡 front-matter-only 口径分叉；④ `check_dates.py` 的 `COUNTRY_HUB` 拿 slug 当 ISO、`/de/` 无守卫
- **STATUS.md 结构观察（未动）**：第 222 行「第九十轮」标题与第 223 行「第九十三轮」标题相邻，第九十轮的正文（`### 3`–`### 6`，约 288–316 行）被隔在第九十三轮小节之后 —— 属上一轮插入时的错位，本轮**不重构**，仅登记

## 已完成（guides 左栏 On this page 列宽：用真实字体度量 140 条 H2 定案 272 px，2026-10-16 第一百轮）

**用户原话**：`这个guides/下的文章的布局如下优化 只需要修改渲染文件即可 1.左侧是文章导航On this page h2的标题显示太窄了只能容纳3个单词 然后就换行了？ 你在搞什么， 这样部美观`
⇒ 只动 `layouts/guides/single.html` 的注释与一个栅格类（外加重跑 `build:css` 生成新任意值类），**数据层、内容层零改动**。**是我上一轮把 176 px 当"够用"定的，错在我。**

### 1 根因（不是"审美"，是一个可算错的数）
左栏 176 px 只是**栏宽**，真正放标题的空间要扣三层固定损耗：卡片 `p-5` 40 + `toc-l2` 的 `pl-3` 12 + `toc-link` 的 `pr-2` 8 = **52 px** ⇒ **只剩 116 px**。13 px 字号下 ≈ 22 字符/行，而本站 H2 普遍 **42–54 字符**（德语更长）⇒ 栏宽够不够的判据被我上一轮漏算了。

### 2 ★ 方法论：把"够不够宽"从估算改成实测
`Add-Type`（PowerShell 的 `System.Drawing` 度量）**被安全策略硬拦**（`Add-Type compiles and loads .NET code at runtime`）；托管 Python 也**不带 PIL**。改走隔离 venv：
```
~/.workbuddy/binaries/python/envs/default/Scripts/python.exe -m pip install pillow
~/.workbuddy/binaries/python/envs/default/Scripts/python.exe .buildlog/r100_wrap.py   # 只读 content/，不写 public/
```
- 字体 `C:/Windows/Fonts/segoeui.ttf` @ **13 px**（`.toc-link` 的 `text-[13px]`；CSS px 与 PIL `size=13` 同义），站点用 Inter 而 Windows 无 Inter 本体 ⇒ 按 Inter 约宽 3~5% 取 **×1.05**
- `font.getlength()` 拿真实 advance 宽度 + 贪心折行，覆盖 `content/{en,de}/guides/*.md` 全部 **140 条 H2**
- **为什么不能用估算法**：英文正文在 16 px 下实测平均只有 **6.96 px/字符**（2129 字符样本）—— 按"0.5 em/字符"估会系统性高估约 15%，**正是它把 116 px 判成够用**

**实测行数分布（140 条 H2）**
| 可用文字宽 | 对应栏宽 | 1 行 | 2 行 | 3 行以上 | 最长 |
|---|---|---|---|---|---|
| 116 px | 176（旧值） | 0 | 33 | **107（76%）** | **6 行** |
| 180 px | 240（第一版改动） | 12 | 105 | 23 | 4 行 |
| **212 px** | **272（最终采用）** | 29 | 104 | **7（5%）** | **3 行** |
| 228 px | 288 | 37 | 98 | 5 | 3 行 |

⇒ 176→272：**3 行以上从 107 条降到 7 条，最长 6 行降到 3 行**；再加宽到 288 只再降 2 条却要吃掉 16 px 正文 ⇒ **边际收益已尽，定 272**。

### 3 ★ 同时推翻旧约束"正文必须守 720 px"
720 px 在 `.prose` 16 px 下实为 **104 字符/行**（6.96 px/字符），**本来就偏宽**；640 px ≈ 92 字符/行反而更合排版规范。⇒ **"与 networks 阅读列一致"不是目的，可读性才是** —— 上一轮为了对齐这个数字才把侧栏饿死，本轮改掉。

### 4 最终列宽（改一个类）
- 栅格：`xl:grid-cols-[176px_minmax(0,1fr)_272px] xl:gap-8` → **`xl:grid-cols-[272px_minmax(0,1fr)_272px] xl:gap-6`**
- 容器 `xl:max-w-7xl` **保持不变** —— 它等于 header/footer 的 `max-w-7xl`，**绝不超过**，否则正文区比 logo 还宽、左右边缘对不齐
- 算式：1280 − `sm:px-6` 48 − 左 272 − 右 272 − `xl:gap-6`×2 48 = **正文 640 px**
- **左 272 / 右 272 对称**；**右栏不能收**（`aside-destinations` 的 `United Kingdom` 在 256 px 就被 `truncate`，且同一 partial 还挂在 networks 的 300 px 栏里）
- lg（1024–1279）**未动**：仍是「正文 720 + 右栏 300」，目录文字宽 240 px（98% ≤2 行），用户未抱怨
- `build:css` 必须重跑：任意值类 `xl:grid-cols-[272px…]` 不在 CSS 里 `check_css_sync.py` 会拦；产物 CSS 实测 `272px minmax(0,1fr) 272px` ✓、旧 `240px_minmax`/`176px` 残留 **0**

### 5 验收
| 项 | 结果 |
|---|---|
| 源码层 | `VALIDATE_EXIT=0`（6 道） |
| 产物层 | **`OUTPUT_EXIT=0`**（13 道：1319 files / 1317 pages / 7550 JSON-LD / sitemap 657 / 3942 hreflang / 德语语言泄漏 0 / baseURL 正确） |
| `hugo` 段 | `HUGO_EXIT=0`，`Total in 470567 ms`（第一次 496972 ms） |
| 归属 | **变更 14 / 新增 0 / 删除 0** = 7 篇文章 × 2 语言；**5 篇区域指南走 `region.html` 未变** |
| 产物断言 | 中英两页 `class="… xl:grid-cols-[272px_minmax(0,1fr)_272px] xl:gap-6"` 实测到位，`176px` 计数 **0** |
| 卫生 | `localhost` **0** / `livereload` **0** |
| 基线 | 刷至 1317 文件，复跑 `--diff` **归零** |

★ **附带证实**：上一轮那个"`guides/index` × 2 也变了、查不出原因"的登记项，**本轮同样的改动下它没有出现** ⇒ 坐实它是一次性脏写残留（来自被中断的那次构建），不是模板缺陷。归属脚本只哈希 `.html`，故 `static/css/tailwind.css` 的字节变化不计入 14 项之内。

**未 `git commit`、未部署**（HEAD 仍 `6f00c2c`）。改动文件：`layouts/guides/single.html`、`static/css/tailwind.css`（重编译产物）、`PROJECT.md`（红线 154 改写 + 新增 156）、`STATUS.md`、`docs/regression-manifest.json`。

## 已完成（guides 文章页改「左目录 + 正文 + 右目的地」三栏且两侧吸顶 + 抓出 hugo 一次性写入拦截，2026-10-16 第九十九轮）

**用户原话**：`这个guides/下的文章的布局如下优化 只需要修改渲染文件即可 数据驱动文件不动 渲染文件如下优化 1.左侧是文章导航On this page 2右侧是Popular destinations 而且这2个都是吸顶的方式， 明白吗`
⇒ 只动 `layouts/guides/single.html`（外加 `assets/css/main.css` 的注释同步），**数据层、内容层零改动**。走 `single.html` 的是 7 篇文章（`dual-sim-and-esim` / `esim-compatibility-check` / `esim-in-china` / `esim-new-york` / `esim-vs-physical-sim` / `how-to-install-esim` / `what-is-an-esim`）；另 5 篇区域指南走 `layouts/guides/region.html`，**不受影响**。

### 1 断点是本轮唯一的技术决策点
「左侧 TOC + 正文 + 右侧 destinations」= **三栏**。**lg（1024–1279）放不下** —— `max-w-6xl` 容器在该档内容宽只剩约 976 px，扣掉左 176 + 右 272 + 两个 gap 后**正文只剩约 450 px**，阅读列就塌了。
⇒ 定案：**三栏只在 xl（≥1280）启用**；lg 维持「正文 + 右下栏」（目录暂留右栏，靠 `xl:hidden` 在 xl 档隐藏）；移动端仍走 `<details>` 那一份。
- 容器：`max-w-6xl` → 追加 `xl:max-w-7xl`
- 栅格：`lg:grid-cols-[minmax(0,720px)_300px]` → 追加 `xl:grid-cols-[176px_minmax(0,1fr)_272px] xl:gap-8`
- **正文列宽守住 720 px**：`xl:max-w-7xl`(1280) − `sm:px-6` 48 − 左 176 − 右 272 − `gap-8`×2 64 = **720**，与 `networks/single.html` 的阅读列**严格一致**

### 2 改动清单（逐处）
| 位置 | 改动 |
|---|---|
| 容器 div | 追加 `xl:max-w-7xl` |
| 栅格 div | 追加 `xl:grid-cols-[176px_minmax(0,1fr)_272px] xl:gap-8` |
| `<article>` **之前** | **新增**左侧吸顶 `<aside class="hidden xl:block xl:sticky xl:top-24 xl:max-h-[calc(100vh-7rem)] xl:overflow-y-auto">`，内为 TOC 卡 |
| 右侧 `<aside>` | `hidden lg:block` → `hidden lg:block lg:sticky lg:top-24 lg:max-h-[calc(100vh-7rem)] lg:overflow-y-auto lg:pr-1`；内层 TOC 卡加 `xl:hidden`；摘掉中间层 `<div class="pr-1">`（`pr-1` 上并到 aside） |
| `assets/css/main.css` | `.toc-link` 段落注释同步（`build:css` 带 `--minify` ⇒ 注释不进产物，**不改变 CSS 产物字节**） |

★ 本轮**推翻**第九十四轮用户定的「本页这两块不吸顶」（当时摘掉 sticky / top-24 / max-h / overflow-y-auto）—— 改判与新日期已写进模板注释，避免下一轮又当成「有人违规加回来」。

### 3 同一个 partial 渲染三份 TOC（有意为之）
`aside-toc.html` 现在被渲染 **3 次**（移动端 `<details>` / 左栏 / 右栏卡），产物里 **3 条 `<nav data-toc>`**。目录高亮 JS 是 `querySelectorAll('[data-toc] a[data-toc-link]')` ⇒ 同一 id 在三份里同设 `aria-current`，用不上的那份只是不可见，**无重复 id、无冲突**。没有改用「Grid 列位搬同一份 DOM」是因为那要在 lg/xl 两个断点间切 `col-start`，脆；三份的代价只有约 1–2 KB/页。

### 4 构建：撞上一次**一次性**写入拦截（已定案）
全量 `hugo` 跑到最后（`Total in 468911 ms`、1317 pages）报
`ERROR error building site: render: [de v1.0.0 guest] failed to render pages: open D:\esimsift\esimsift\public\de\compare\netherlands\alosim\index.html: Access is denied.`
并被沙箱标为 `Blocked by Security Center rules`。**只读诊断三步**：
1. 该文件权限正常（`-rw-r--r--`，非只读）；
2. 1313 端口上的 `hugo.exe`(PID 9056) 是 `npm run dev`（父进程 `cmd /c npm run stamp && npm run build:css && hugo server --renderToMemory`）⇒ **`--renderToMemory` 不写 public，不是冲突源**；
3. mtime 分桶（按 10 分钟）显示 **1316/1317 个产物已更新**，只剩这一个没写 —— **而它恰是全站唯一残留 dev 污染的文件**（54 处 `localhost` + 1 处 `livereload`，来自更早某次裸 `hugo server` 的产物）。

**处置**：向用户摊开证据并请其定夺，用户选「重跑一次构建」⇒ **原样重跑 `HUGO_EXIT=0` 一次通过**（`Total in 474771 ms`），该文件被重写为干净版本，全站 `localhost` 0 / `livereload` 0。⇒ 判定为**一次性拦截**，不是配置或权限问题（红线 155）。

### 5 验收
| 项 | 结果 |
|---|---|
| 源码层 | `VALIDATE_EXIT=0`（6 道全绿：`check_css_sync` 识别到 11 个新 `xl:` 类已全部编译进 `static/css/tailwind.css`；`check_page_container` 22 个页型模板都有容器） |
| 产物层 | **`OUTPUT_EXIT=0`**（13 道全绿：`1319 files (1317 pages)` / 7550 JSON-LD / sitemap 657 / **3942 hreflang tags on 1314 pages** / `baseURL = https://www.esimsift.com/` / 德语 657 页语言泄漏 0 / URL 语言前缀违规 0） |
| 归属 | **变更 16 / 新增 0 / 删除 0** —— 恰为 **7 篇文章 × 2 语言 + `guides/index` × 2**，页型分布 `{'guides': 16}`；5 篇区域指南未变（走 `region.html`） |
| 产物断言 | 三篇抽样（`esim-in-china` / `de/esim-new-york` / `what-is-an-esim`）实测：`xl:grid-cols-[176px` ×1、`xl:max-w-7xl` ×1、`xl:sticky` ×1、`lg:sticky` ×1、`xl:hidden` ×1、`data-toc` 三份齐 |
| 基线 | 刷至 1317 文件，复跑归属 `--diff` 归零 |

### 6 一处**未定位**的登记项（不是缺陷）
`guides/index` × 2 出现在变更名单里，但**逐项核验不含本轮任何标记**（无 `xl:` 断点类、无 `data-toc`、无 sticky），且与 dev server（`--renderToMemory`）的同一页**逐行对比只差 dev 注入的 URL**（livereload script / localhost canonical / hreflang / og:url），其可辨识内容全部正确（12 篇卡片齐全、含中国新文章、双语对应、无污染）。⇒ **判定：非本轮改动引入、无内容缺陷**，无法用本轮改动解释，已随新基线归档。留作待查项，**不阻塞上线**。

---



**用户指令**（逐字，两条）：① `为什么标题不用 China eSIM: Paying Without a Chinese Phone Number 因为China eSIM 是核心词`；② `另外 文章的开头是否需要一个文章更新日期，这样日期就是最新的 / 你的日期是放到了h2中 / Last reviewed / Oct 15, 2026`

### 1｜问题①：一半是我错了，一半要否掉

规则在 `docs/keyword-map.md` 主映射表 **L27**，是**两句话**，必须同时满足：**① 不打头**（国家页 `/compare/{country}/` 的 `title` 就是 `China eSIM`，独占该精确词形）、**② 要含**（文章 H1「可以且应当含国家词」，定例 = 纽约 `eSIM for New York: What a USA eSIM Costs in 2026`）。

| 我的原题 | ① 不打头 | ② 要含国家词 |
|---|---|---|
| `eSIM in China: Paying Without a Chinese Phone Number` | ✅ 遵守（介词形态打头） | ❌ **整条标题没有 `China eSIM` 词形 —— 真缺陷** |

- 用户提的 `China eSIM: Paying Without a Chinese Phone Number`（49 字符）**打头会被①否掉**（两页争同一 query，Google 只保一个 = 真蚕食）。
- ★ 但**「标题里根本没有 `China eSIM`」确实是我的错** ⇒ 改成 **`eSIM in China: A China eSIM Without a Local Number`**（EN **51** 字符）/ **`eSIM in China: Eine China-eSIM ohne lokale Nummer`**（DE **50** 字符，德语连字符形，与既有 H2 `Was eine China-eSIM tatsächlich löst` 一致），两版都落回 `audit_meta.py` 的 **48–54 字符**带。⇒ 立**红线 153**。
- ★ 副产物：无城市词的国家文章（中国这类）**没有城市词可打头** ⇒ 一律用**介词形态**（`esim in china`，Trends 0.0095 独立 query）打头、后半句带国家页词形。

### 2｜问题②：日期确实被埋在 H2 里 —— 已上移到首屏

- **取证**：`Last reviewed / Oct 15, 2026` 原先渲染在 `layouts/guides/single.html` 的**「关键事实」`<dl>` 栅格第 2 格**（H2 = `China eSIM payment facts` 之内）⇒ 首屏看不见、且与「阅读时长」并列成两条**非事实**的元信息。用户判断准确。
- **改法（`layouts/guides/single.html`）**：在 **H1 正下方**新增一行元信息（`Last reviewed Oct 15, 2026 · 11 min` / `Zuletzt geprüft 15.10.2026 · 11 Min.`），并把这两项从 `<dl>` **移出**（**不是复制** —— 红线 8 一份真源；`<dl>` 现在只剩 front matter 的 6 条真事实，实测 `dt` 6 个）。
- ★ **顺手关掉一条长期登记项**：原第 83 行读 `.Lastmod`，与 `/guides/` 索引卡（`_default/list.html` 用 `or .Params.lastmod .Params.date`）**口径分叉**；现统一为 **`or .Params.lastmod .Params.date`**，**只读 front matter**，与索引卡 / sitemap `<lastmod>` / JSON-LD `dateModified` 同源；**绝不 fallback 到 `now`**（同红线 7）。实测各页各取自己的 date：`how-to-install-esim` → `Oct 1, 2026`、`esim-new-york` / `esim-in-china` → `Oct 15, 2026`。

### 3｜★★ 意外收获：`public/` 已被裸 `hugo server` **全量污染**（我上轮的卫生判据漏了）

- 我上轮宣布「产物干净」，依据是 `grep -rl livereload public` **且** `grep -rl "localhost:1313" public` 都为 0。**本轮实测**：`grep -oE "localhost:[0-9]+"` = **54,772 处 / 1341 文件 / 端口 `58194`** —— Hugo 在 1313 被占用时**换端口**，而我的判据**把端口写死了**。
- **仓库本来就拦得住**：`scripts/check_dates.py` 检查 [A]「`public/` 不得含 localhost + sitemap host 必须等于 baseURL」**早在 `check:output` 链上**，单独跑一次即报 **11 条问题 / 1341 文件**（`baseURL = https://www.esimsift.com/`，却出现 `http://localhost:58194/guides/best-europe-esim/`）⇒ **是我自己的手工判据漏了，不是仓库缺守卫**。⇒ 立**红线 151**（含「手工判据要么删掉、要么与仓库守卫同源」）。
- ★ **同轮我又踩了「守卫加管道」**：`python scripts/check_dates.py | head -20` 让 `$?` 取到 `head` 的 `0` —— **11 条问题报出来却显示 `EXIT=0`**。凡跑守卫一律 `> log 2>&1; echo "EXIT=$?"`。
- ★ 附带确认：`npm run dev` 用的是 `hugo server --renderToMemory`（**不落盘**）⇒ 污染只可能来自**裸 `hugo server`**（红线 7 第 5 次 → **第 6 次**）。**重跑 `npm run build` 即完全复原**：重建后 `localhost` **0** / `livereload` **0**。

### 4｜构建的两个真坎（都不是「配置问题」）

| # | 症状 | 真因与修法 |
|---|---|---|
| 1 | `BUILD_EXIT=1`，`validate` 报 `ERROR 硬编码文案未抽 i18n -> layouts/guides/single.html: text '&middot;'` | 守卫抽「可见文本节点」后按**像不像英文单词**判硬编码，而**实体名 `middot` 恰好是 6 个拉丁字母**；裸 `·`（U+00B7）不含字母直接跳过。仓库既有惯例就是裸 `·`（`compare/vs-single.html:360`）⇒ 改用裸 `·`。立**红线 152**。★ `aria-hidden="true"` **不是**豁免理由（守卫不读 aria 属性） |
| 2 | 第二次构建 **SIGTERM**（`Exit Code 1`），日志停在 `check:output` 中途 | `hugo` 段本轮 **`Total in 468806 ms`**（≈7.8 min，第九十七轮 196 s ⇒ 波动 2.4 倍），加上 `validate`+`css` 已近 500 s，撑爆 600 s 前台上限。**修法**：`hugo` 已完成（`1317 pages`）⇒ 单独补跑 `npm run check:output`（只读），`OUTPUT_EXIT=0` |

### 5｜验收（全部产物文本断言，**按约定不做截图**）

| 项 | 结果 |
|---|---|
| 源码层 | `VALIDATE_EXIT=0`；6 道全绿（`i18n en 1907 / de 1907 key`、模板引用 1872 key 未定义 0、h2/h3 标点 0 处违规、22 个页型模板容器 OK） |
| 产物层 | **`OUTPUT_EXIT=0`**；13 道全绿：`1319 files (1317 pages) / 7550 JSON-LD` · `499 品牌子页全过（Offer 9095）` · `sitemap 657 URL` · `3942 hreflang tags on 1314 pages` · `baseURL = https://www.esimsift.com/`（**[A] localhost 0**）· 冠词一致 · de 657 页语言泄漏 0 |
| 标题 | EN 产物 `<title>` = `<h1>` = `eSIM in China: A China eSIM Without a Local Number`（51 字符）；DE = `eSIM in China: Eine China-eSIM ohne lokale Nummer`（50 字符） |
| 元信息行 | 位于 **`</h1>` 之后、`<figure>` 配图之前**；`Last reviewed` / `Zuletzt geprüft` **全页各出现 1 次**（无重复）；`<time datetime="2026-10-15">`；各页取自己的 front matter date |
| 事实栅格 | `id="keyfacts"` 段内 `dt` 恰好 **6** 个（全部 front matter 事实，元信息已移出） |
| 卫生 | `localhost` **0 文件** · `livereload` **0 文件** |
| 逐字节归属 | **变更 16 / 新增 0 / 删除 0**，页型分布 `{'guides': 16}` = **7 篇 `single.html` 指南 × 2 语言**（`dual-sim-and-esim` / `esim-compatibility-check` / `esim-in-china` / `esim-new-york` / `esim-vs-physical-sim` / `how-to-install-esim` / `what-is-an-esim`）+ **`/guides/` 索引 × 2**（卡片标题变）—— **与开工前的预测逐条吻合**；5 篇区域指南**未变**（走 `region.html`，不渲染元信息行与相关阅读卡） |
| 基线 | 已刷至 **1317 文件**；复跑 `--diff` ⇒ **变更 0 / 新增 0 / 删除 0** |

### 6｜纪律与登记

- **未 `git commit`、未部署**（改动全部留工作区；HEAD 仍 `6f00c2c`）。
- 新增红线：**151**（手工卫生 grep 禁写死端口 + 守卫禁加管道）、**152**（装饰符用裸 `·` 不用 `&middot;`）、**153**（文章 title 必须「含」国家页词形且不得打头）。
- **关闭登记项**：`layouts/guides/single.html:83` 的 `.Lastmod` 口径分叉 —— 已统一为 front-matter-only。
- **沿用待办**：compare 50 国正文计数动态化（159 处 / 86 文件）；首页 EN title 45 字符；57 条 description >140；`check_dates.py` 的 `COUNTRY_HUB` 拿 slug 当 ISO 与 `/de/` 无守卫；`STATUS.md` 第 222/223 行标题错位（不重构）。
- ⚠ **给用户的提醒**：页面「Last reviewed」的日期取 front matter 的 `date`（现 **2026-10-15**）。若你希望它显示为**发布当天**，只需改这一处字段，索引卡 / sitemap `<lastmod>` / JSON-LD `datePublished`+`dateModified` / 首屏元信息行会**一起跟着走**（不 fallback `now`，红线 7）。

## 已完成（中国文章 `esim-in-china`：支付与号码轴 + 27 词 Trends 实测 + 自审判据双向校准，2026-10-15 第九十七轮）

**用户指令**（逐字）：`继续帮我围绕中国esim，写文章`

**用户拍板两项**：① 选题轴 = **支付与号码轴**（微信支付 / 支付宝 / 号码问题）；② 覆盖范围 = **一篇中国大陆文章 + 文内港澳提示**，**不新建** `/networks/hong-kong/`。

**交付**（两份纯 LF，**零模板改动** —— `layouts/guides/single.html` 的 `hero` / `hero_alt` / `prompt_answer` / `h2_answer` / `h2_facts` / `facts` / `faqs` / `byline` / `h2_next` 机制直接可用）

| 文件 | 大小 | 行 | `<h1>` | title 字符 | description 字符 |
|---|---|---|---|---|---|
| `content/en/guides/esim-in-china.md` | 18436 B | 149 | `eSIM in China: Paying Without a Chinese Phone Number` | 52 | 140 |
| `content/de/guides/esim-in-china.md` | 20398 B | 149 | `eSIM in China: Zahlen ohne chinesische Rufnummer` | 48 | 132 |

- 首屏图 `travel-esim-illustration-009.webp`。图池 **132 张**，本轮前已占用 **12** 个编号 ⇒ 本轮后占用 **13** / 可用 **119**（`r97_hero.py` 现算）。
- `target_keyword: "esim in china"`（**介词形态**，见 §2）；作者署名 **`eSIMSift Data Team` / `eSIMSift Datenteam`**（团队署名，不造假个人 —— `schema.html` 明文约定）。
- 正文引用型外链 **3 处 / 3 个不同实体**：腾讯微信帮助中心 · 腾讯官方新闻稿 · Apple eSIM 机型页；内链 **11 处**（en/de 各 11，含 `/networks/china/#carriers` 锚点）。

### 1｜选题：先把证据摊开再动笔 —— 我首选的方向被自己的实测验否

我最初想写「香港 + 中国大陆 双目的地」，**我自己在动笔前把它否掉了**，三条独立证据：

1. **Trends 实测**：`esim hong kong and china` 相对锚词 **0.0000**（词表把它标成「缺口 / 47.8」，**补全分 ≠ 真实需求**）。
2. **覆盖度盘点**：`/guides/best-asia-esim/` 的 L17 / L25 **已经写过**「香港 + 中国大陆」；`/compare/china/` L13 也已占住。
3. **数据层**：10/10 品牌在港澳**各自单独成线**，**零区域套餐** ⇒ 双目的地没有产品支撑，写了就是凑字。

⇒ 改用 **AskUserQuestion 把证据摊给用户**，用户选定「支付与号码轴」+「大陆为主 + 港澳提示」。

**27 个候选词 / 4 批 Trends 实测**（`r97_trends_cn*.py`，锚词 `esim` 均值 **75.49**，四批同日一致；本轮收尾时**全部复跑并逐词复现**）

| 轴 | 词 | 相对锚词 |
|---|---|---|
| 核心（国家页已占） | `esim china` / `china esim` / `esim china esim` | 0.0252 / 0.0252 / 0.0257 |
| **★ 定案：介词形态** | **`esim in china`** | **0.0095** |
| 邻区 | `esim hong kong` | 0.0062 |
| 区域 | `esim asia` | 0.0052 |
| 设备（微弱） | `esim china iphone` | 0.0035 |
| 规格（≈0） | `esim china unlimited` / `esim hong kong china` | 0.0002 / 0.0002 |
| 城市轴 · 全零 | `esim beijing` / `esim shanghai` / `esim shenzhen` / `esim guangzhou` | 0.0000 |
| 政策场景轴 · 全零 | `esim china vpn` / `china esim wechat pay` / `alipay esim china` / `esim china firewall` | 0.0000 |
| 设备落地轴 · 全零 | `china esim number` / `esim china airport` / `esim hong kong airport` | 0.0000 |
| 来源国轴 · 全零 | `esim for china from uk` / `esim for china from usa` / `buy esim for china` | 0.0000 |
| 其余 · 全零 | `does esim work in china` / `esim hong kong and china` / `esim for china trip` / `how to get esim for china` | 0.0000 |

- ★ **`esim in china` = 0.0095 是本轮唯一可用的文章词**：它是**独立 query**（与 `esim china` / `china esim` 的 0.0252 不同），量级与既有可用城市词 `esim new york`（**0.0098**）持平 —— 已立为**红线 149**。
- ★ **`esim china esim` 也测出 0.0257**，与 `esim china` 同值 ⇒ 佐证「词序归并」，进一步支撑 149 的「同词不同介词形态是两个独立 query」。
- 政策场景轴（vpn / wechat pay / alipay / firewall）**四个词全零** ⇒ 用户关心的「支付」方向**在 Trends 里没有独立检索量**，文章只能**承接国家页的意图**而不是自造需求。

### 2｜★ 改轴之前先做全站覆盖度盘点（红线 150 的来源）

中国方向只有五条可用轴，逐条盘点**全站是否已有内容占位**：

| 轴 | 全站现状 | 结论 |
|---|---|---|
| GFW / 路由轴 | `/networks/china/` 已写 | 已占 |
| 「在中国买的手机」轴 | `/networks/china/` 已写 | 已占 |
| 香港 + 中国大陆 | `/compare/china/` L13 + `/guides/best-asia-esim/` 两条 FAQ | 已占（这就是我第一版选题被否的原因） |
| 城市 / 政策场景轴 | 无内容占位 | ★ **但 Trends 全零** ⇒ 不可写 |
| **支付与号码轴** | **`grep -ri "wechat\|alipay" content/` = 0 命中** | ★ **唯一零覆盖且可写** |

### 3｜事实取证：只写「运营方自己页面上写着的」那一组（红线 8）

- **★ 核心反转论点**：eSIM 的价值**不是**给你中国号码，而是**给支付 App 供网**（「No data, no payment」—— 支付二维码是**在线生成**的，不是存在手机里的图片）。
- **`https://cs.help.wechat.com/.../How-to-Set-Up-International-Cards-for-Weixin-Pay`**（腾讯微信帮助中心官方英文页，实测 200）：明文写着 **「Do I need a Chinese Mainland (+86) phone number? **A: No.**」**+ 单笔 6,500 元 / 月度 50,000 元 / 年度 65,000 元上限 + 200 元门槛 / 3% 费率。
- **`https://www.tencent.com/index.php/en-us/articles/2202338.html`**（腾讯官方新闻稿，实测 200）：首次绑国际卡享**连续 90 个自然日**手续费减免（日额度 ≤1,000 元），须 **2026-12-31 前**绑定；**2026 全年**单笔 ≤200 元继续免 3%；PayPal World 互联互通**首期面向美国用户**。
- **★ 主动砍掉的内容**：支付宝限额在第三方来源上有**三组互斥数字**（USD 5,000/50,000 · CNY 35,000/100,000/500,000 · CNY 3,000/50,000/60,000）⇒ 按红线 8「一份事实只允许一份真源」，**只写腾讯页明确的那组（Weixin Pay）**，**不写有争议的 Alipay 数字**。
- 三条正文断言全部对上产物：`en 0.51 dollars for a 100MB` / `de 0,51 US-Dollar für 100MB` … 共 **20 组 / 两侧各 1**（`r97_audit.py` 的核心数据点断言段）。

### 4｜所有数字现算（`data/plans/*.toml` + `data/providers.toml`，核对日 **2026-10-07**）

- **基数与 `/compare/china/` 声称值逐条对齐**：总档 **203** ✓ / 无限 **98** ✓ / 全表最低价 **$0.51**（yesim 100MB / 1 Day）✓ / 最佳 $/GB **$0.48**（roamic 50GB / 30 Days）✓ —— **四个数与国家页完全一致**（`r97_cn_decide.py` Q1）。
- **表格四行（天数与数据量同时满足，两个维度都卡）**：

| 场景 | 最便宜匹配 | 价格 |
|---|---|---|
| 几天·地图与消息 | roami 1GB / 7 Days | $1.99 |
| 正常一周 | roamic 5GB / 21 Days | $5.00 |
| 一周含视频与热点 | roamic 10GB / 30 Days | $9.00 |
| 重度或长住 | roamic 50GB / 30 Days | $24.00（= $0.48/GB） |

- **FUP 真阈值八条**（只读 `data/providers.toml` 的 `policy`）：Saily **5GB/天** · Airalo / Jetpac / Roamic **3GB/天** · Nomad **2GB/天** · aloSIM **1.5–2GB/天→512Kbps** · Yesim **500MB–2GB/天** · Ubigi **逐 plan** · Holafly **不公布** · Roami **自称 30GB/天但自家页面互相矛盾**。
- **同规格价差 > 3 倍**（举一反三的论据）：同为 5GB 且有效 ≥7 天，最低 **$5.00**（roamic 21 天）vs 最贵 **$16.00**（alosim 30 天）。
- **无限值不值**：覆盖整周的最便宜无限 = **$15.00**；5GB 定量覆盖一周 = **$5.00** ⇒ **3 倍差价**，正文据此写成「无限买的是确定性，不是速度」。
- **港澳节（数据支撑，非口头提示）**：HK **185 档 / 97 无限 / 10 品牌**，起价 **$0.57**，最佳 $/GB **$0.52**；MO **127 档 / 53 无限 / 10 品牌**，起价 **$0.51**，最佳 $/GB **$0.54**。港澳各自 carrier 组合数 = 1（HK: CSL / 3HK / SmarTone；MO: CTM / 3 Macau / China Telecom）；**10/10 品牌双覆盖、零区域套餐** ⇒ 正文「HK 3GB/3天 $2.99 + CN 5GB $5.00 ≈ $8 数据开销」。

### 5｜★ 自审判据 4 条假红 —— 靠「拿已验收产物做双向校准」才抓出来（红线 148）

`r97_audit.py` 首轮跑出 4 条 FAIL，**方向一致指向「改正确正文」** —— 我没有改正文，而是**加了一个 `AUDIT_FILES` 环境变量入口**，把**同一批判据拿去跑已验收的 `esim-new-york`**，于是 4 条全部翻案：

| # | 判据（错） | 纽约文章的实测值 | 修法 |
|---|---|---|---|
| ① | `target_keyword` 精确命中 **≥8** | 纽约只有 **1** 次（且只在字段本身） | 改判「**词族**（含主题词的各种形态）≥20」 |
| ② | `target_keyword` 必须**精确**出现在 title | 纽约 title = `eSIM for New York`，**不含**精确串 | 改判「title 含 `esim` + 主题词」 |
| ③ | 主题词族 ≥20（**硬编码 `china`**） | 换国必失败 | 主题词从 `target_keyword` **去停用词推导** |
| ④ | 德语内链**必须带 `/de/`** | **5 条假红**：`/css/tailwind.css` · `/favicon.ico` · `/favicon.svg` · `/apple-touch-icon.png` 是**静态资源**；`/guides/<slug>/` 是**语言切换器的 English 项 + `hreflang="en-us"` + `x-default`** | 静态资源与跨语言切换器进**豁免** |

- ★ **判据 ④ 在产物层以 5 个路径的形态再出现一次**（`r97_prod.py` 首轮 `FAIL 1 条`，列出同 5 个路径）⇒ **同一个根因在两个脚本里各报一次**，修完 `prod2` 才 `PASS`。
- ★ 这个「**自审判据必须先拿已验收的既有产物做双向校准**」已立为**红线 148**。若不做校准，本轮会把 4 条正确的正文改坏。

### 6｜反同质化：段落 md5 判据（技能 §4 的硬约定）

`r97_dedup.py`：EN **38 段** / DE **39 段**（≥60 字符），与**全部 12 篇既有 guides**（`_index` + 5 篇区域 + 6 篇指南）**重复 = 0**；en / de 各自**自重复 = 0**。⇒ 新文章**没有复用**第一篇（纽约）的 H2 骨架与段落。

### 7｜验收（全部产物文本断言，**按约定不做截图**）

| 项 | 结果 |
|---|---|
| 构建 | **`BUILD_EXIT=0`**；`hugo` 段 **`Total in 195937 ms`**（★ 口径 = hugo 渲染段，非 `npm run build` 墙钟） |
| 产物闸门 | **13 道全绿**：`1319 files (1317 pages) / 7550 JSON-LD` · `499 品牌子页全过（Offer 9095）` · `100 country pages` FAQ 与数据一致 · `sitemap 657 URL` · `3942 hreflang tags on 1314 pages` · 冠词一致 · `de 657 页` 语言泄漏 **0** · 英文残留 **0** · `livereload` **0** · `localhost:1313` **0** |
| 页面级断言 | EN 产物 **105696 B** / DE **109599 B**；`<h1>` 各 1 个；`<h2>` 各 **14** 个（8 正文 + 4 front matter + 2 版块）；JSON-LD **6 块**（`Article` / `BreadcrumbList` / `FAQPage` / `ItemList` / `Organization` / `WebSite`）；作者卡 `id="byline"` 存在；锚点链接 **9** 个且**目标 `id` 在同语言产物里存在**（`/networks/china/#carriers` 两侧均 True） |
| 逐字节归属 | `--diff` ⇒ **变更 14 / 新增 2 / 删除 0**。变更 14 = **7 页 × 2 语言**（`esim-new-york` · `dual-sim-and-esim` · `esim-compatibility-check` · `esim-vs-physical-sim` · `how-to-install-esim` · `what-is-an-esim` · `guides/index`）；新增 2 = 两个 `esim-in-china/index.html` |
| ★ 归属归因 | 5 篇**区域**指南（`best-africa-middle-east` / `best-americas` / `best-asia` / `best-europe` / `best-oceania`）**没变**，不是漏报 —— 它们**本来就不渲染文章卡片**（实测 `grep -l "esim-in-china" public/guides/*/index.html` 恰好命中上述 7 页，`best-europe-esim` = **0**） |
| 结构计数守卫 | `check_hardcoded.py` 仍 `EXIT=1`，但**只有 `DEFERRED 159 处 / 86 文件`**（compare 正文存量，按用户决定先登记）；**文章类 0 处** ⇒ 「正文不写品牌数与套餐数」这条规则**机器验证通过** |
| 部署前卫生 | `livereload` **0** · `localhost:1313` **0** · `public` 文件总数 **1915** |
| 基线 | 已刷至 **1317 文件**（`--write-manifest`），代表第九十七轮构建后状态 |

### 8｜纪律与登记

- **未 `git commit`、未部署**。★ **注意 HEAD 已变**：本轮开始时 HEAD 是 **`6f00c2c`（"10-15-3"，2026-10-15 21:53:30 由用户自行提交，内容 = 第九十六轮收尾）**，不是我此前记录的 `5b7bac4`。本轮改动**全部留工作区**：`PROJECT.md`（改）、`docs/regression-manifest.json`（改）、`content/{en,de}/guides/esim-in-china.md`（未跟踪）。
- 改已存在文件一律 **bytes 读写 + 复核换行**：`STATUS.md` **纯 LF / 3821 行 / 413571 B**（改前实测）、`PROJECT.md` **纯 LF**；两份新文章**纯 LF**、149 行、`CRLF=0`。
- 新增红线：**148**（自审判据先拿已验收产物做双向校准）、**149**（同词不同介词形态是两个独立 query）、**150**（换轴前先做全站覆盖度盘点）。
- **沿用待办**：compare 50 国正文计数动态化（159 处 / 86 文件）；首页 EN title 45 字符；57 条 description >140；`layouts/guides/single.html:83` 的 `.Lastmod`；`check_dates.py` 盲区（`COUNTRY_HUB` 拿 slug 当 ISO、`/de/` 无守卫）；`STATUS.md` 第 222/223 行标题错位（**本轮不重构**，仅登记）。
- **德语译文未审校**（用户明确不作为上线阻塞）。

## 已完成（「AI 味句式」维度举一反三 + 两个 i18n 死键 + 沙箱构建坑，2026-10-15 第九十六轮）

**用户指令**（逐字）：`纽约esim文章：` / `开头的The New York eSIM answer in one paragraph` / `这个不像是正常人会这样写的标题，一看就是ai味道 ，这个改 吗` / `What 254 USA eSIM plans actually cost` / `不要出现254 以后新增套餐怎么办？数量难道以后又更新吗` / `Plans we price for the USA` / `254 across ten brands`

**用户拍板两项**：① 同族句式改动范围 = **全部改**（内容层 6 处 + i18n 2 句）；② 纽约事实格两个英文标签 = **改**。

### 1｜「这个改 吗」—— 全部已改（第九十五轮就做了），并回答「为什么你还能看到」

| 用户贴的串 | 现状 | 现在页面上是（EN / DE） |
|---|---|---|
| `The New York eSIM answer in one paragraph` | ✅ 第九十五轮已改 | `What a USA eSIM changes for a New York week` / `Was eine USA-eSIM für eine Woche New York ändert` |
| `What 254 USA eSIM plans actually cost` | ✅ 第九十五轮已改 | `What USA eSIM plans actually cost` / `Was USA-eSIM-Tarife tatsächlich kosten` |
| `254 across ten brands` | ✅ 第九十五轮已改 | `Every prepaid plan sold into the USA` / `Jeder Prepaid-Tarif, der in den USA verkauft wird` |
| `Plans we price for the USA` | ✅ 本轮改 | label 改成 `Plans in the USA file`（它本来就是事实格**标签**、不含数字） |

- **唯一存活处 = `STATUS.md` 第九十五轮小节的「改前」对照列** —— `in one paragraph` / `What 254` / `254 across ten brands` 在**源码 0 处、产物 0 处**（`254` 全页唯一命中是图标 SVG 路径 `L1.254`）。你看的是我的报告，不是文章。
- ★ **给这篇文章取证不能用 `git diff`**：它是第九十二轮**新建、从未提交**的**未跟踪文件**（`git status` = `??`）⇒ `git diff` 对它**输出为空**，会把「已改」误判成「没改」。同侧证据：线上 `/guides/esim-new-york/` = **HTTP 404**、线上 `/guides/` 内 `new york` 命中 **0** ⇒ 文章**未上线**。

### 2｜举一反三：新维度「AI 味压缩句式」（上一轮把它判错了方向）

- ★★ **红线 144 ③ 里那条「假红：各页自身的标题」是判错的** —— `eSIM vs physical SIM at a glance` 确实不属于「结构计数」判据范围，但**它不是「假红」，是「第二个独立维度」**。「假红」的语义是「本项检查本来就该忽略它」⇒ 一旦这么记，**下一轮我再也不会去看它**，直到用户点回来才发现。已把该例从 144 ③ 移除并**另立红线 146**。
- 正则**跑了两轮**：首轮模式漏 `in short` 类 ⇒ 只抓 1 条；补 `in short|in brief|the short version|…` 才收全（与第九十五轮「先探针再定判据」同一条教训）。

**最终清单（16 处替换 / 7 文件，en/de 严格 1:1）**

| # | 位置 | 改前 | 改后 |
|---|---|---|---|
| 1 | `content/en/guides/esim-vs-physical-sim.md:9` | `Which one to choose in short` | `Which one wins for your trip` |
| 2 | `content/en/guides/esim-vs-physical-sim.md:54`（H2） | `eSIM vs physical SIM at a glance` | `eSIM and physical SIM side by side` |
| 3 | `content/de/guides/esim-vs-physical-sim.md:9` | `Welche Variante kurz gesagt gewinnt` | `Welche Variante für deine Reise gewinnt` |
| 4 | `content/de/guides/esim-vs-physical-sim.md:54`（H2） | `eSIM gegen physische SIM auf einen Blick` | `eSIM und physische SIM Seite an Seite` |
| 5 | `content/en/guides/how-to-install-esim.md:9` | `Installing a travel eSIM in short` | `Installing a travel eSIM step by step` |
| 6 | `content/de/guides/how-to-install-esim.md:9` | `Reise-eSIM installieren kurz erklärt` | `Reise-eSIM installieren Schritt für Schritt` |
| 7 | `i18n/en.toml:543` | `Coverage at a glance` | `Where it is cheapest` |
| 8 | `i18n/de.toml:546` | `Abdeckung auf einen Blick` | `Wo er am günstigsten ist` |
| 9 | `i18n/en.toml:671` | `The refund policy in short` | `How refunds work` |
| 10 | `i18n/de.toml:674` | `Die Rückgabepolitik in Kürze` | `So funktioniert die Rückgabe` |
| 11 | `i18n/en.toml:1368`（**死键**） | `{{ .country }} eSIM networks at a glance` | `How {{ .country }} eSIM networks compare` |
| 12 | `i18n/de.toml:1371`（**死键**） | `eSIM-Netze in {{ .country }} auf einen Blick` | `Wie die eSIM-Netze in {{ .country }} abschneiden` |
| 13 | `i18n/en.toml:1430`（**死键**） | `{{ .region }} eSIM prices at a glance` | `Where {{ .region }} eSIM prices land` |
| 14 | `i18n/de.toml:1433`（**死键**） | `eSIM-Preise in {{ .region }} auf einen Blick` | `Wo die eSIM-Preise in {{ .region }} landen` |
| 15 | `content/en/guides/esim-new-york.md` facts | `Plans we price for the USA` | `Plans in the USA file` |
| 16 | `content/en/guides/esim-new-york.md` facts | `Networks any of them uses` | `Networks behind every plan` |

**假红两处（不动）**：`content/{en,de}/esim-new-york.md` byline 的 `in this article`（自然句）；`public/de/guides/esim-vs-physical-sim/index.html` 里的 `Ka` + `uf einen Blick` + ` darauf` —— 德语习语「看一眼」，`auf einen Blick` 是**跨词切出来的假象**（★ 新坑：**朴素 grep 该短语必假红**）。

### 3｜★★ 新缺陷类别：两个「永不渲染」的 i18n 死键

`layouts/networks/single.html:49` 与 `layouts/guides/region.html:74` 都写作：

    {{ $x := .Params.h2_answer | default (i18n "networks_single__h2_answer" …) }}

实测（本轮脚本阶段 0 断言）：`content/{en,de}/networks/*.md` **除 `_index.md` 外 50 国全部**定义 `h2_answer`；`content/{en,de}/guides/best-*-esim.md` **5 篇区域指南全部**定义 ⇒ 两个 i18n 兜底值**永不渲染**（改前产物 `at a glance` 只命中 2 个文件即可反证）。

★ **风险不是多一行文案，是潜伏雷**：以后**新增国家 / 区域页时漏写 `h2_answer`**，页面就会静默漏出旧句式 —— 而**所有守卫都看不见**（值在 `i18n/*.toml`，而 `check_hardcoded.py` 的 `BASES` 只含 `content/en` `content/de` `layouts` `hugo.toml`）。已顺手把兜底值改成同风格，**零渲染影响**。

### 4｜★★ 本轮真踩的坑：沙箱拦 `public/` 写盘（已立红线 147）

五次构建才绿，其中**三次不是内容错**：

| 次 | 结果 | 真因 |
|---|---|---|
| 1（后台 + 越权） | `Access is denied` @ `public/compare/malaysia/alosim/index.html` | **后台越权不弹同意框 ⇒ 仍在沙箱内**；Hugo 只给裸错误，看不出是沙箱 |
| 2（前台 + 越权，默认 120 s 超时） | SIGTERM，日志停在 `WARN deprecated: .Site.Data` | 超时被杀，**日志里没有 `Total in`** |
| 3（后台 + 越权） | stderr 才给明话：`[sandbox] 命令被沙箱拦截：… public/de/compare/japan/alosim/index.html (file-write)` | 同上 |
| 4（前台 + 越权 + `timeout: 600000`） | 跑到 `check:output`，报**真缺陷**（见 §5） | ✅ 姿势正确 |
| 5 | **`BUILD5_EXIT=0`** | —— |

★ **被拒文件每次不同**（`compare/malaysia/alosim` → `de/compare/japan/alosim`）⇒ **别当成「某个品牌页坏了」去改数据**。★ 诊断口诀：**先看 `Total in … ms` 有没有出现** —— 出现 = 渲染已完成、错在写盘；这几次的日志里源码 6 道闸门**全是绿的**，这就是「不是内容问题」的铁证。

### 5｜★ 第 4 次构建抓到我自己的真缺陷（红线 6 的活证据）

`check_article_agreement.py` 报：

    ERROR i18n/en.toml:1368 冠词紧邻占位符 -> "a {{ .country"（渲染后可能是 a Argentina / a Airalo）

即我给 `networks_single__h2_answer` 写的 `The networks behind a {{ .country }} eSIM` 把 `a` **直贴在占位符前** —— 正是红线 6 禁止的写法。改语序为 `How {{ .country }} eSIM networks compare` 后 `ART_EXIT=0`。★ **教训：改 i18n 兜底值时，占位符语序必须与前端冠词规则一起想**。

### 6｜验收

| 项 | 结果 |
|---|---|
| 主改动脚本 | **16 处替换 / 7 文件 / `APPLY_EXIT=0`**；落盘前 16 条旧串**逐条断言唯一命中 1**，任一不符即整体中止（★ 给记忆脚本时**真的触发过一次断言，未写半个文件**） |
| 换行 | 7 个目标文件**实测全部纯 LF**；落盘后逐文件 `CRLF`/`LF` 计数守恒 |
| i18n 完整性 | `tomllib` 解析 OK；`en=1907 / de=1907`，**key 集合完全一致** |
| 构建 | **`BUILD5_EXIT=0`**；`hugo` 段 `Total in 189555 ms` |
| 产物闸门 | 13 道全绿：`1317 files (1315 pages)` / `7538 JSON-LD` / `34212 h2h3 bad 0` / `sitemap 656` / `hreflang 3936 tags on 1312 pages` / `499 品牌子页全过（Offer 9095）` / 冠词一致 / `de 657 页` 语言泄漏 0 / `livereload` **0** / `localhost:1313` **0** |
| 逐字节归属 | `--diff docs/regression-manifest.json` ⇒ **变更 27 / 新增 0 / 删除 0**（`guides=5`：2 篇指南 × 2 语言 + `en/esim-new-york`；`provider_hub=22`：10 品牌页 × 2 语言 + 2 个索引页）—— **与预期逐条吻合，无传播型外溢** |
| 残留扫描 | 产物 `at a glance` **0** / `in short` **0** / `The refund policy in short` **0** / `Coverage at a glance` **0**；`auf einen Blick` **1**（= 上述跨词假象） |
| 结构计数守卫 | `check_hardcoded.py` 仍是 `EXIT=1`，但**只有 `DEFERRED 159 处 / 86 文件`**（compare 正文存量，按用户决定先登记）；**文章类 0 处**，豁免 901 条 |
| 基线 | 已刷至 **1315 文件**（`--write-manifest`），代表第九十六轮构建后状态 |

### 7｜纪律与登记
- **未 `git commit`、未部署**（HEAD 仍 `5b7bac4`）
- 新增红线：**146**（「AI 味句式」是独立维度 / 把「范围外」记成「假红」= 永久屏蔽 / i18n `default` 兜底是死键高发区）、**147**（沙箱拦 `public/` 写盘；后台越权不生效；诊断先看 `Total in`）
- 修正红线 **144 ③**：把 `eSIM vs physical SIM at a glance` 从「假红」清单移除（翻案 + 已改）
- **沿用待办**：compare 50 国正文计数动态化（159 处 / 86 文件）；首页 EN title 45 字符；57 条 description >140；`single.html:83` 的 `.Lastmod`；`check_dates.py` 盲区

## 已完成（纽约文章去 AI 味 + 全站「会过期的结构计数」清剿 + `check_hardcoded.py` 通电，2026-10-15 第九十五轮）

**用户指令**（逐字）：`纽约esim文章：` / `开头的The New York eSIM answer in one paragraph` / `这个不像是正常人会这样写的标题，一看就是ai味道` / `New York eSIM facts at a glance` / `这个不要写多少品牌，多少个套餐，万一我后续新增其他品牌的美国esim咋办` / `请你举一反三` / `另外为什么h1h2的标题不能植入usa esim这个是核心词？`

**用户拍板两项**：① 改动范围 = **只改文章类，compare 先登记**；② `usa esim` 的植入方式 = **H1 也植入国家词**（明知会与 `/compare/united-states/` 的 title `USA eSIM` 争词形）。

### 1｜三问逐条对账

| 问 | 答复 / 处置 |
|---|---|
| 两个 H2 太「AI 味」 | `The New York eSIM answer in one paragraph` → **`What a USA eSIM changes for a New York week`**；`New York eSIM facts at a glance` → **`New York eSIM price facts`**（德语同构：`Was eine USA-eSIM für eine Woche New York ändert` / `eSIM-Preisfakten zu New York`）。两键由 `layouts/guides/single.html` 内建渲染（`h2_answer` / `h2_facts`），**零模板改动** |
| 事实格不许写死品牌数 / 套餐数 | 纽约文章 **16 处替换 ×2 语言**（`254 across ten brands` → `Every prepaid plan sold into the USA`；`…identical in all 254 plans` → `…identical in every one`；H2 `What 254 USA eSIM plans actually cost` → `What USA eSIM plans actually cost`；`100 of the 254 plans` → `A large share of the plans in our file`；`six tiers from 3 days to 30 days` → `running from 3 days to 30 days`…）。**理由**逐字：新增品牌后这些数字会静默变谎 |
| 为什么 H1/H2 不能植入 `usa esim` | 查明 `content/en/compare/united-states.md` 的 front matter `title` **就是 `USA eSIM`**（`iso: US` / `weight: 2`），`layouts/compare/single.html` 用 `$lockedTitle` 取它作 H1 ⇒ 国家页独占该精确词形（两页争同一 query = 真蚕食）。**原规则「国家词只作背景、正文 ≤1 次」经用户推翻**：城市文章**应当**在 H1/H2 含国家词，只要**以城市词起头**保住主词位。已实施 `eSIM for New York: What a USA eSIM Costs in 2026`（**EN 48 / DE 48 字符**，落在 `audit_meta.py` 的 48–54 带内），`docs/keyword-map.md` 的城市文章行同步重写 |

### 2｜举一反三（探针驱动：76 处 / 19 文件 → 清 44 处 / 登记 159 处）

- **探针 v1**（6 类候选判据：国家数 / 品牌数 / 套餐数 / 比例计数 / 档位数 / 不限量计数）对**改造前源码**全量跑 ⇒ **34 处命中、零误伤**；**v2** 补「区域目的地数」类 ⇒ **76 处 / 19 文件**。★ v1 **漏掉** 4 篇区域指南的 `Ten brands` 与 `networks/japan` 的 `177 plans` ⇒ **先跑探针、再定判据**（顺序反了必漏）。
- **本轮清掉（12 文件 / 44 处，`r95_apply.py` EXIT=0）**：纽约文章 ×2 语言（16+16）、4 篇区域指南 ×2 语言（各 1）、`content/{en,de}/networks/japan.md`（各 2）。
- **`networks/japan.md:55` 同类最恶**：`{{< count-providers >}}`（渲染 **10**）后面紧跟只列 **8** 个品牌名的括号列表 ⇒ **删列表**（动态计数是唯一真源）；`:59` 的 `all 177 plans` → `every plan`。
- **登记待办（本轮不动，用户决定）**：**compare 50 国正文 159 处 / 86 文件**（如 `content/en/compare/united-states.md:9` 的 `254 plans`；`layouts/partials/country-stats.html` 已返回 `planCount`，**动态化可做**）。

### 3｜`scripts/check_hardcoded.py` 扩写为可运行判据 + 加手动入口（**本项目最严重的「写了没通电」案例**）

- 实测：该守卫 docstring 早在 **2026-10-02** 就写明四条规则（`layouts` → `{{ len hugo.Data.* }}` / `content bodies` → `{{< count-countries >}}` 等短代码 / `front matter` → **number-free wording** / EXEMPT `content/en/compare/<country>.md` 的 `seo.description`），**但它从未出现在 `npm run validate` 也不在 `check:output`** ⇒ 开工一跑已经 `EXIT=1`（`content/en/compare/costa-rica/airalo.md:8` 的 `All 28`、`layouts/partials/aside-destinations.html:21` 的 `50 destinations` —— 后者其实是**注释里的历史说明**）。
- 重写后：11 类判据 + 注释掩码（`{{/* … */}}` / 带裁剪符 `{{- /* … */ -}}` / 裸 `<!-- -->` **三形态**）+ `seo:` 块豁免 + `--selftest` **7 正例 / 7 反例全过**；违规分 **`HARDCODED TOTALS`（非 compare = 硬错）** 与 **`DEFERRED`（compare 存量 = 登记待办）**，**两者都返回 1**（让待办量永远可见、只减不增）。
- 两条硬细节：`(?<![\d.,])\b\d{2,4}\b` 的负向后视（否则 `content/en/compare/_index.md:14` 的 `a $0.51 plan` 被判成 `51 plan`）；豁免量必须用**「剥前命中数 − 剥后命中数」求差**（掩码把注释换成等量换行，**长度已变**，拿掩码后的偏移查原串必然漂）。
- 现成替代品（本轮复用）：`layouts/shortcodes/{count-providers,count-countries,count-app-providers,count-direct-providers}.html`；`layouts/partials/country-stats.html` 返回 `planCount` / `unlimitedCount` / `minPrice` / `minPerGB` / `maxGB` / `providerCount`。
- **★ 本轮实测**（`npm run check:hardcoded`，`package.json` 新增的手动入口）⇒ `EXIT=1`：**文章类命中已归零**，只剩 `DEFERRED — compare 正文 159 处 / 86 文件`；豁免（`compare/*.md` 的 `seo.description`，生成器会重写）**901 条**；`--selftest` **7 正例 / 7 反例全过**。
- **★ 诚实说明**：新入口 `npm run check:hardcoded` 只是**手动入口**，**未进 `npm run validate` / `check:output`** —— compare 159 处待办会让它**恒红**。等 compare 清完再入闸（判据本身已就绪）。**「有守卫」≠「闸门在跑」** 这条纪律本轮对自己也适用。

### 4｜假红五条（全部真实出现，已逐一排除）

| 假红 | 实例 | 为何不改 |
|---|---|---|
| 价格与价格派生量 | `$0.51 plan` 等 | 有 `checked` 复核日锚，会定期重核 |
| 稳定地理事实 | `all three countries`（美/加/墨，4 页） | 不随品牌 / 套餐增长而变 |
| 策展集合的规模 | `18 destinations` / `Eight Countries` | 只有主动扩区才变，非外部数据增长 |
| 历史日志 | `public/methodology/index.html` 的 `Brands involved: Airalo, … Yesim`（8 个） | 是 **2026-09-30 的变更日志**，改了即**篡改历史** |
| 各页自身的标题 | `eSIM vs physical SIM at a glance`（2 页） | 是**该页自己的 H2**，与纽约文章无关 |

### 5｜验收（产物文本断言，**无截图**）

| 项 | 结果 |
|---|---|
| `npm run build` | **`BUILD_EXIT=0`**；`Total in 492020 ms`（`hugo` 段，后台总耗时 15m2s） |
| 源码 6 道闸门 | 全过 |
| 13 道产物闸门 | 全绿：`1317 files (1315 pages)` · `7538 JSON-LD` · `34212 h2/h3 bad 0` · sitemap **656** · hreflang **3936 条 / 1312 页** · 499 品牌子页全过 · `de` 页 **657** · 语言泄漏 **0** · `livereload` **0** · `localhost:1313` **0** |
| **逐字节归属** | `verify_no_regression.py --diff docs/regression-manifest.json` ⇒ **变更 24 / 新增 0 / 删除 0**，`EXIT=0` |
| **确定性自证** | 第二次全量构建（`BUILD2_EXIT=0`，`Total in 265320 ms`）后拿**同一份**改造前基线复跑 ⇒ 仍 **24 / 0 / 0**、同样 `guides=22, networks=2` ⇒ 构建是确定性的、24 处变更真实；基线已刷至 **1315 文件** |
| 残留扫描（1315 HTML） | 本轮清掉的旧文案 **全站零残留**（`ten brands` / `Zehn Marken` / `zehn Anbieter` / `177 plans` / `six tiers` / `sechs Stufen` / `100 of the`）；`254 plans` 的 26 个命中**全部落在 `compare/united-states/**`** = 已登记待办 |
| 产物文本核对 | EN `<title>`/H1 = `eSIM for New York: What a USA eSIM Costs in 2026`（48）、description 133 含品牌；DE 48 / 130 含品牌；`public/guides/esim-new-york/index.html` 内 `ten brands\|254\|six tiers\|100 of the\|at a glance\|in one paragraph` **文案零残留**（唯一 `254` 命中是 SVG path 的 `L1.254`） |

**★ 24 处变更逐条归因**：`guides` 单页 **20**（10 篇 × 2 语言）+ `guides/index.html` **×2** + `networks/japan` **×2**。其中**直接变更 10 篇**（纽约 + 4 篇区域指南）×2；**被动变更 10 篇**（`dual-sim-and-esim` / `esim-compatibility-check` / `esim-vs-physical-sim` / `how-to-install-esim` / `what-is-an-esim`）—— 探针证实这些页里纽约新标题**恰好出现 1 次**，位置是 `card card-hover` 的「更多指南卡片」⇒ **guides 单页列出全部 guides 的 title + description，单篇标题一变则同语言全栏目页全变**（红线 143③ 的推广）。

### 6｜★ 基线归属（本轮最大的障碍与结论）

- 开工时 `public/` 与仓库外快照 `D:\esimsift\_r94_prev_html`（1315 HTML / 250.8 MB）**都不是干净基线**：快照里 `index.html` 含 `<script src="/livereload.js?…&port=1313…">` + `canonical="http://localhost:1313/"` + 旧品牌字串 `eSIM Sift` ⇒ 是**第九十四轮开工前的 dev server 污染产物**，页页 sha 都不等于基线（与红线 141 同源）。★ 拿快照当基线前**先 grep `livereload` 与 `localhost:1313`**。
- **真正可用的基线是 `docs/regression-manifest.json`**（17:00 改动前写入、18:2x 构建完成 —— 顺序正确）—— 但它**只存 `sha256` / `cls` / `title_len`，不含内容** ⇒ 只能做**页级三分类 diff**，**不能**做块级替换深证。
- 归属证据链 = 页级 sha256 三分类（**24 / 0 / 0**）+ 24 条归因探针 + 全站残留扫描 + 13 道产物闸门。

### 7｜纪律与登记

- **未 `git commit`、未部署**（改动全部留工作区，HEAD 仍 `5b7bac4`）
- 改已存在文件全部 **bytes 读写 + 复核换行**：本轮 14 个目标文件**实测全部纯 LF**（`content/{en,de}/guides/*.md`、`content/{en,de}/networks/japan.md`）
- **每条字节替换落盘前先断言「旧串唯一命中数」**，不符即整体中止、不写半个文件
- **另改 3 个非内容文件**：`scripts/check_hardcoded.py`（扩写判据）、`package.json`（**新增手动入口 `check:hardcoded`**；纯 LF、`json.loads` 合法）、`docs/keyword-map.md`（城市文章行重写）
- 新增红线：**144**（「会过期的结构计数」缺陷类别 + 探针驱动的举一反三 + 五类假红 + **守卫写了不等于通电** + 同句两种口径）、**145**（产物基线两种形态：指纹型只能页级、内容型必须先验净）
- **登记未动**：① compare 50 国正文 **159 处 / 86 文件**；② 首页 EN title **45** 字符（低于 `audit_meta.py` 的 48–54 带）；③ **57 条** description >140（德语国家页，既有问题）；④ `layouts/guides/single.html:83` 的 `.Lastmod` 与索引卡 front-matter-only 口径分叉；⑤ `check_dates.py` 的 `COUNTRY_HUB` 拿 slug 当 ISO、`/de/` 无守卫；⑥ 本轮新发现 `content/en/compare/costa-rica/airalo.md:8` 的 `All 28`（随 compare 批量项一起处理）

## 已完成（`/guides/` 宽度修复 + 新增「页型模板容器」守卫，2026-10-13 第九十轮补记）
## 已完成（博客文章生产线 + 首篇国家文章 `esim-new-york`，2026-10-15 第九十三轮）

**用户指令**（逐字）：「文章放 ① 进 content/en/guides/；文章开头还需要一个图片……另外如果是牵涉到运营商的信息，你可以链接到内部链接……国家和国家之前的文章内容不能重复，你写完整个文章后，就沉淀下技能或者记忆，免得以后犯错。」

### 1｜交付

- **新增 2 页产物**（en + de，共 **1315** 页）：`content/{en,de}/guides/esim-new-york.md`；guides 每语言 `_index.md` + **11 篇**（原 10 篇）
- 文章 **en 2391 词 / de 2199 词**，各 **9 个 H2 + 5 个 H3**（共 14 标题）、**15 条内链**（锚文本全不同、目标页与锚点逐条实测可达）、**3 条权威外链**（Ookla / RootMetrics / Apple 支持）、**6 条 FAQ**（正文与 FAQPage schema 同源）
- **新增共享组件**：`layouts/partials/author-box.html`（团队署名卡，**只在 front matter 有 `byline` 时渲染**）+ `layouts/guides/single.html` **1 行调用** + `i18n/{en,de}.toml` 各 **+3 key**（1904 → **1907**）
- 作者署名按用户拍板 = **团队署名**（`eSIMSift Data Team` / `eSIMSift Datenteam`）—— 不编个人，符合 `schema.html` 既有原则「无真实团队资料时不造假个人」

### 2｜防蚕食与防国间重复

- 国家页已占满**八条轴**（比价 / 价格 / FUP / 流量档位 / 行程长度 / 品牌 / 网络 / FAQ）⇒ 文章**换轴**：城市词 + 到达首小时 + 与漫游/机场 SIM 对比 + 跨境延伸
- 规则写进 `docs/keyword-map.md`（+1 行）与技能 `esimsift-country-article`（含「同系列第二篇起不得复用第一篇 H2 骨架、通用段落必须并进共享 partial、段落 md5 去重后重复数必须 0」三条判据）

### 3｜验收（全部产物文本断言，**无截图**）

| 项 | 结果 |
|---|---|
| `npm run build` | **`EXIT=0`**；`Total in 495423 ms`（`hugo` 段，落在实测区间 233–591 s 内） |
| 13 道产物闸门 | 全绿：`1317 files (1315 pages)` · `7538 JSON-LD` · `34212 h2/h3 bad 0` · sitemap **656** URL · hreflang **3936 条 / 1312 页** · 499 品牌子页全过 · `check_faq_facts` R1–R11 · `verify_de_text` **656 页** F/G 全绿 · `check_inline_copy` 0 残留 |
| 产物断言 `.buildlog/r93_verify.py` | **通过 40 / 失败 0**（首轮 36/4，四条 FAIL **全部定性为判据假红**并已修留痕，见 §14 红线 138） |
| 英文自审 `.buildlog/r93_audit.py` | 通过 35 / 失败 0（SEO title **52** 字符 / description **135** 字符 / 12 个 LSI 词全命中 / 29 个数据点齐全） |
| 德语自审 `.buildlog/r93_audit_de.py` | 通过 29 / 失败 0 |
| 产物卫生 | `livereload` / `localhost` 计数均 **0** |
| 零外溢 | `--diff` **变更 12 / 新增 2 / 删除 0**：12 = 2（guides 索引卡）+ 10（5 篇单页 × 2 语言的「相关阅读」），**其余 1301 页逐字节不变**（归因见 §14 红线 137） |
| 基线 | `--write-manifest` → **1315 文件**，复跑 `--diff` **0 / 0 / 0** |

### 4｜纪律与数据

- **未 `git commit`、未部署**（改动全部留工作区，HEAD 仍为 `5b7bac4`）
- 新增 / 修改文件全部 **bytes 读写 + 复核换行**：`content/{en,de}/guides/esim-new-york.md`、`docs/keyword-map.md`、`layouts/partials/author-box.html`、`layouts/guides/single.html`、`i18n/{en,de}.toml` **均纯 LF**
- **数据全部现算**（`.buildlog/r93_us_decide.py`）：美国 **254 套餐 / 10 品牌**（154 计量 + 100 无限），网络 **100% 一致**（T-Mobile / AT&T / Verizon 各 254/254，**唯一网络组合数 = 1**），最低 **$0.51**（yesim 500MB/1d）、最佳 **$/GB $0.60**（nomad 50GB/30d $30）、倍差 **23.9**
- **★ 写作铁律（本轮真错更正）**：「某档最低价」**必须同时卡有效期** —— 原稿写「10GB 档最低 $7.99」其实那是 **3 天有效**、撑不过一周；覆盖一周的是 **roamic 10GB/30d $8.00**（数字对、场景错）
- **★ 旧草稿「Roami 无 FUP」是错的** —— 读 `data/providers.toml` 真源为 `30 GB/day`，且 `fup_note` 自承与自家 UK 指南的 `2 GB/day` 矛盾 ⇒ 文章改写为「publishes 30GB per day, yet its own pages disagree with each other」
- **★ 德语首版正文漏逗号（真缺陷，已整篇重写）** —— 我把「标题层免逗号」误推广到正文；德语从句逗号是**硬语法**，缺了就是错的德语

### 5｜沉淀

- 技能 `~/.workbuddy/skills/esimsift-country-article/SKILL.md`（12 节：铁律 10 条 / 关键词真实性验证 / 防蚕食表 / 防国间重复三规范 / 取数模板 / front matter 契约 / 内链语言陷阱 + **EN↔DE 锚点对照表** / 自审口径 / 作者署名与 E-E-A-T / 验收交付 / 闸门口径速查）
- `MEMORY.md` 再压缩并把「博客 / 文章生产」章节**前移**（注入预算实测 **≈9.3 KB** —— 由注入截断点反推，比原先按归档文件估的 17.4 KB **紧一倍**）
- `PROJECT.md` §11「操作手册 E」+ §14 **新增红线 135–139**

**用户报告**：「/guides/ 这个页面是不是太宽了，和其他页面的布局不一样的，宽度不协调，宽度都跑到屏幕外了」。

### 1｜取证（先量再动，`.buildlog/r90b_width_probe.py`）

| 页 | `<main>` 之后第一个元素 | 有容器？ |
|---|---|---|
| **/guides/** | `<div class="py-4">` | ❌ **无** `mx-auto` / `max-w-*` / `px-*` |
| /compare/ · /esim-providers/ · /esim-deals/ · /tools/ · /research/ | `mx-auto max-w-7xl px-4 py-8 sm:px-6` | ✅ |
| /networks/ | `mx-auto max-w-7xl px-4 py-6 sm:px-6` | ✅ |
| /about/ 等静态页 | `mx-auto max-w-3xl` | ✅（无 `px-*`） |

根因：`layouts/_default/baseof.html` 只有 `<main class="flex-1">` —— **不给宽度、不给居中、不给内边距**，容器由**每个页型模板自负**；`layouts/_default/list.html`（只服务 `/guides/` 与 `/de/guides/`）是第一层就 `<div class="py-4">` 的那个**全站孤例**（22 个页型模板里唯一）。
★ 诚实归属：`git diff` 证明 `py-4` 那行**不是第九十轮改出来的**，是长期存在；上一轮把指南卡加厚后才被用户看出来。
★ 用户 13 条清单里的「/compare/ 无排序筛选」上一轮已核过，本轮**没有**顺手动它。

### 2｜修法（手术式：同一行内替换、零新增行）

`<div class="py-4">` → `<div class="mx-auto max-w-7xl px-4 py-8 sm:px-6">`
· 与 `/compare/` `/esim-providers/` `/esim-deals/` `/tools/` `/research/` 五个同级索引页**逐字节相同**；
· `py-4` → `py-8` 一并归一（垂直内边距与其他索引页一致，「不一致」本身就是问题）；
· 所有 class 都是站内已在用的 ⇒ `check_css_sync` 无新增 unsynced class。

### 3｜新增守卫 `scripts/check_page_container.py`（已入 `npm run validate` 链尾，第 6 道）

判据：扫 `layouts/**` 所有含 `{{ define "main" }}` 的模板，断言 main 块内**至少一个真实元素**的 class 同时含 `mx-auto` 与**页面级** `max-w-2xl…8xl`。
· 判「**块内存在**」而非「首元素必须是」—— 让首页 / 404 的满幅 hero（`relative overflow-hidden bg-hero-mesh` + 内部容器）合法通过；
· 注释里 / action 字符串里 / 正文文字里的 `mx-auto max-w-7xl` **都不算**（各有反例守护）；
· `max-w-md` 这种**组件级**居中短句不算容器；
· **WARN 不红**：有页面级 `max-w-*` 但无 `px-*`（`_default/single.html` + `_default/methodology.html` 的 `mx-auto max-w-3xl`，涉 12 个产物页）—— 属独立决策，只提示。
★ **顺序证明**：先写守卫 → **先对改造前的真实 `layouts/` 跑** → 报 `FAIL _default/list.html:1`（恰是用户报的那一页）+ 2 条 WARN → 改完再跑 → `OK: 22 个页型模板`。**先红后绿，两侧都证**。
★ `--selftest` 10 正例 / 10 反例：正例含 hero 满幅 / 嵌套块 / 外层裸 div / **注释里写 `{{ end }}`** / 多行 action；反例含注释、action、正文、别的 `define`、组件级宽度**五种伪容器**。
★ 守卫第一版**被真实源码咬出假红**：`tools/list.html` 第 51–59 行的说明注释正文里写着 `` `{{- end }}` ``，括号平衡提前归零、把真容器整段切掉 ⇒ 对 21 个正常模板里的它报红。修法：**先掩注释再平衡**（等长空格掩码，偏移 / 行号 1:1 不变）。

### 4｜验收

- `npm run validate` **6 道全绿**（新增第 6 道 `check_page_container` → `OK: 22 个页型模板`）
- `npm run build` **`BUILD_EXIT=0`**：`1315 files (1313 pages)` · `7526 JSON-LD` · `34148 h2/h3 bad 0` · 499 品牌子页全过 · `hreflang 3930 条 / 1310 页` · sitemap 655 URL · i18n 1904 key en=de · 德语四道守卫全绿
- **归属：变更 2 / 新增 0 / 删除 0**，恰为 `guides/index.html` + `de/guides/index.html`（该模板只服务这两页）
- **★ 逐字节归属深证**（比 diff 更强）：把新产物里那一段类串还原成 `py-4`，整页 sha256 **等于基线旧 sha** ——
  `guides/index.html 839a45e4…70`（70645 → 70614 B）、`de/guides/index.html e4c7b846…77`（72373 → 72342 B）
  ⇒ **这两页除那一处类串外，一个字节都没动**
- 17 项产物断言全绿（`.buildlog/r90b_assert.py`）：容器逐字节同串 / 全站 `class="py-4"` 容器清零 /
  该容器类串覆盖 12 页（6 个索引模板 × 2 语言）/ 分组区与 10 张卡与 10/10 阅读时长与复核日与 10 篇 ItemList 全部仍在 /
  `public/` 无 `localhost` 无 `livereload`
- 基线刷新 → **1313 文件**（`generated_at 2026-10-13T08:32:52Z`），复跑 `--diff` = **0 / 0 / 0**

### 5｜登记未动项

`_default/single.html` 与 `_default/methodology.html` 的容器 `mx-auto max-w-3xl` **没有 `px-*`**（窄视口正文贴边）—— 守卫只报 WARN，未改（会动 12 个产物页）。已写进 `PROJECT.md §5.1` 与 skill §3.5.1 的规格表。

## 已完成（networks 子页日期口径：新增页面按发布日，2026-10-13 第八十九轮）

### 1｜问题与口径
`/networks/<国>/` 的「最后更新」徽章原先无条件取 `country-stats.checkedDate`（= 该国全部品牌的最大
`checked`）。于是本轮新建的 GE 页（10-13 发布）印着 **Oct 7** —— 一个页面顶着它诞生之前的日期。
口径改为 **页级日期 = `max(数据核对日, 页面自身的发布日)`**：徽章与 sitemap `lastmod` 取它；
两处脚注的 `at the <d> snapshot` 是**数据快照日**，仍取数据核对日 —— 同一页**允许并存两个日期**。

### 2｜影响面（独立复算，逐页对账）
| 组 | 页面发布日 | 数据核对日 | 生效 | 页数 |
|---|---|---|---|---|
| GE（本轮新增） | 10-13 | 10-07 | **10-13** | 2（en+de） |
| 10-12 建的那批（CO·HR·EG·MA·PL·SA·ZA·CH·TW·VN） | 10-12 | 10-07 | **10-12** | 20 |
| 10-03 建的那批（12 国） | 10-03 | 10-07 | 10-07（不变） | 24 |

### 3｜改动点（模板行数不变）
`layouts/networks/single.html`（徽章取值改 `$effDate`，**422 行不变**）·
`layouts/partials/sitemap-urls.html`（新增 ②b 分支，全部 `{{- … -}}` 裁白）·
`scripts/check_dates.py`（`networks_sub` 判据放宽 + 新增 `load_networks_page_dates()` + 自测 2 例）。

### 4｜两侧取证（全部产物文本断言）
- `check_dates.py --selftest` **19 项全绿**（含「发布日正例」与「构建日 Oct 14 仍必须红」）
- 新判据**先对改造前产物跑**：精确报出 **11 页** sitemap lastmod 未跟上（GE + 10 页）⇒ 判据有牙
- 多行注释 / 8 行新增**零字节外溢**（最小站点夹具实测：`PRE<<…>>POST` 恰一行）
- `npm run validate` 5 道全绿 · 全量构建 13 道产物闸门全绿 · 基线 `--diff` 变更集 = 预期

## 已完成（P3 第一件：品牌 hub 价格档位表 + `UnitPriceSpecification`；GE networks 建页（照 CN 路线），2026-10-13 第八十八轮）

> 用户指令逐字：`P3 的第一件：品牌 hub 加价格档位表` / `GE 建页（照 CN 路线）` / `优化执行这个即可`

### 1｜品牌 hub 价格档位表 + `Product.priceSpecification`（20 页 = 10 品牌 × en·de）

**为什么做**：品牌 hub 的 `#calc` 段是 **JS**，服务端只吐空容器（`<p id="calc-c1-v"></p>`）⇒ **搜索引擎与 AI 抓不到任何价格内容**。P3 要接住 `saily coupon code` @9.5 · `holafly discount code` @8 · `airalo prices` @6 · `ubigi price` @7 · `yesim cost` @6 这批词，先得让价格**静态可抓**。

**新增区块 ⑤c**（`layouts/esim-providers/single.html`，`id="pricing"`）：

- **表一（有量档位，4 列）**：档位 / 在售目的地数 / 最低价（带来源国）/ 最低 `$/GB`（带来源国）
- **表二（无限量档位，3 列）**：行程天数 / 在售目的地数 / 最低价（带来源国）—— 因 holafly **纯无限量**（0 个有量档），只做表一会让它整段消失
- **`MIN_DEST = 10` 覆盖门槛**：只保留在 ≥10 个目的地在售的档位，滤掉单国长尾档（airalo 的 2GB、ubigi 的 200GB 之类）；**门槛数在脚注对读者明说**，不藏口径变化
- **脚注还写明**：`Where several destinations tie on price the table names one of them.`（并列只取一个名字，不合成假事实）
- **`$/GB` 与「最低价」可以来自不同国家** ⇒ 两格各自带来源国标签；导语声明 `The cost per gigabyte comes from that same plan`（一句话的事实必须来自同一次选优）
- **与既有 `#spread` 的分工（不重复）**：`spread` 比**同一档位在不同国家**的入场价高低；`#pricing` 比**同一国家不同档位**的 `$/GB` —— 正交两问，故新开 id
- **`priceSpecification`**：每条 = 一个档位的起步价 + 容量（`referenceQuantity` 用 UN/CEFACT `unitCode: E34`），与表**共用同一份 `$tierRows` 推导**，不重算第二遍
- i18n **14 个新 key × 2 语言**（1841 → **1855**，en/de 逐 key 同序对齐：12 个价格档位表 key + 2 个「只有无限量表」变体 key）

| 品牌 | 有量档 | 无限量档 | 品牌 | 有量档 | 无限量档 |
|---|---:|---:|---|---:|---:|
| airalo | 6 | 6 | roami | 8 | 4 |
| alosim | 7 | 6 | roamic | 6 | 30 |
| holafly | **0** | 6 | saily | 5 | 6 |
| jetpac | 8 | 9 | ubigi | 10 | 1 |
| nomad | 6 | 4 | yesim | 7 | 30 |

### 2｜GE networks 建页（en + de）—— **照 CN 路线**（只 Ookla、无 Opensignal）

**先纠正上一轮我自己的错误表述**：GE 的阻塞**不是版式问题**（`layouts/networks/single.html:276–301` 早有「无 awards → 事实列表」回退分支，文件头设计注释 12–13 行原话「缺 awards 时回退为事实列表布局，不报错」），**是事实源问题**。而替代通路**有两条**，CN 是站内活先例：

| | GE 格鲁吉亚 | KE 肯尼亚 | CN（已上线先例） |
|---|---|---|---|
| Opensignal 报告 | ❌ | ❌ | ❌ |
| **Ookla 移动数据** | **✅ Rank 19 / 229.03 Mbps / Aug 2026** | **❌ 列为 N/A**（只收录固网 Rank 135） | ✅ Rank 21 / 221.77 |
| 结论 | **可做** | **真阻塞** | 已上线 |

- **事实源交叉验证**：`https://insights.opensignal.com/reports/georgia/` 返回 Page not found；`data/networkreports.toml` 文件头第 11 行早已登记「无近期 Opensignal 国家报告（只出 Global Index 链接）：**IS GE KE MO CN**」；Ookla Global Index 主榜 August 2026 Georgia 第 19 / 229.03 Mbps（前 Estonia 236.52、后 New Zealand 225.90），**同榜 China = 21 / 221.77 与既有 `[CN]` 条目逐字吻合** ⇒ 口径一致
- **数据**：`data/networkreports.toml` +`[GE]`（3 字段 `ookla_note`/`ookla_url`/`ookla_date`）、`data/de/networkreports.toml` +`[GE].ookla_note`（德语小数逗号 `229,03` + 单位 `Mbit/s`）—— **两文件均纯 CRLF**；`ookla_url`/`ookla_date` 是语言无关机器字段，留 en 层由深合并继承（与 `[CN]` 完全同构）
- **页面**：`content/{en,de}/networks/georgia.md`，**22 个 front matter key、顺序与 `colombia.md` 逐 key 一致**（含 7 个 `h2_*` 覆盖）、正文 6 个 H2、8 条 FAQ、3 条 `cities_detail`；纯 LF
- **不编**：开篇与 FAQ 首条都**主动写明**「Georgia has no Opensignal Mobile Network Experience report … The Ookla figure is a country-level median: it tells you the market is fast, and it does not tell you which carrier to prefer.」
- **未链 Türkiye**（站内无该国 networks 页，避免死链）

### 验收（全部产物文本断言，不做截图）

| 项 | 结果 |
|---|---|
| `npm run build` | **`BUILD2_EXIT=0`**（17m06s，与旧侧构建并行）· **1313 页 / 1315 文件 / 7526 JSON-LD 块** |
| 13 道产物闸门 + 德语守卫 | 全绿：`check_headings` **34140 h2/h3 `bad: 0`**；`check_hreflang` **1313 页 / 3930 标签 / 1310 页**（GE 三向互指、targets 全部存在）；`check_dates`（`networks_sub` 含 GE）；`verify_provider_pages` 499/499；`check_faq_facts` R10/R11；`verify_de_text` / `verify_de_data` / `_de_schema_audit` / `_de_link_leak_audit` / `check_inline_copy` 全部通过 |
| **独立复算**（`.buildlog/r88_pricing_verify.py`） | **20 页 / FAIL 0** —— 档位标签、目的地数、最低价、最低 `$/GB`、`priceSpecification`（`name`/`price`/`referenceQuantity.value`/`unitCode=E34`）、脚注门槛，全部与 `data/plans/*.toml` **独立重算**一致（不读模板、不看产物结构，把表**当数据解析**） |
| **逐字节归属法**（`.buildlog/r88_attrib.py`） | **新增 2 / 删除 0**；**L1：1266 页「除 header 外逐字节相同」**（1 页完全未变）；**L2：44/44 差异块全部被声明类别归因**（品牌 hub 20 / 说明句变体切换 20 / 从句追加 2 / 索引卡链接 2）；**L3 空白预算**全部为模板缩进 |
| GE 页取证 | sitemap `<loc>…/networks/georgia/</loc><lastmod>2026-10-07T00:00:00Z</lastmod>`（= **数据核对日，不是构建日**）；可见日期 en `Oct 7, 2026` / de `07.10.2026`；站内链 135 条 **0 死链**；Ookla 外链在、**Opensignal 外链 0** |
| 基线 | `--write-manifest` → **1313 文件 / `networks 48`**（`generated_at 2026-10-13T02:52:02Z`），随后 `--diff` 自证 **变更 0 / 新增 0 / 删除 0** |

### ★ 本轮踩到的一个真缺陷 + 一条归属法升级（已写进 PROJECT.md 红线 123、124）

1. **☠ 模板赋值块会「逐行吐空白」，而且循环体内被每个数据行各吐一次** —— 我的档位聚合块写成普通 `{{ }}`（本文件既有风格都不裁白，我照抄了），结果**每个套餐行都往产物里吐一次行尾换行 + 缩进**：airalo 页多出 **12052 行空白（+89 KB）**、holafly 页 +22 KB。`check_output` / `check_headings` / `verify_no_regression` **一条都不报**（产物合法、只是胖）。**修法**：整段改 `{{- … -}}` 全裁白，**首行不加前裁**（保住上面那行原有的空行）、**末行加后裁**，使整段对产物贡献**恰好 0 字节**。修后残差恒为 **+327~+336 B 且与套餐数完全无关**。★ 纪律：**新写赋值/循环块前先问「这段会不会被数据行乘出来」**；判断方法不是读模板，是**量产物字节**。
2. **归属法升级为三层（L1/L2/L3）** —— v1 用**字符级** difflib 逐对比较 1310 个 ~300 KB 文件，O(n²)，**跑到被 kill**。改成 L1 定向替换重建（O(n)，秒级）/ L2 非空白恒等式 / L3 空白预算。★ 为什么 L1 要换**整块 `<header>`** 而不是只换 mega 区块：`partials/header.html` 的**数据计算块内联渲染**在 logo 与 `<nav>` 之间（第 11–43 行），其中 `{{ with site.GetPage "/networks/{slug}" }}` 首次命中会多吐 **16 个空白字符**。

### 本轮的结构性影响（已登记）

- **`verify_no_regression.py`**：`MARKER_ALLOWED_HUB` 新增第 5 项 `'id="pricing"': {"provider_hub"}`；`--selftest` 按纪律**两侧都证**（漏到 `guides/` 要红 + 落在品牌 hub 要放过），两项均 OK。
- **「加一国 networks 页」的连带改动（本轮实测出精确清单）**：① 该国 `compare/<国>/` 国家页多一个从句（`, and this destination has its own [X carrier breakdown]`，`compare/single.html:872` 的 `{{ with }}`）② 该国 10 个 `compare/<国>/<品牌>/` 品牌子页的说明句**整句换变体**（`compare/provider.html:665-669` 的 `{{ if }}`/`{{ else }}`）③ `/networks/` 索引页的该国卡片多一个 `Carrier breakdown →` 链接 ④ **全站每一页**的 header 菜单计数 +1、菜单多一项、且 **+16 空白字符** ⑤ sitemap +1 URL ⑥ 全站导航重生成 ⇒ 这就是「加一国的真实构建代价」（上一轮已记，本轮给出了**逐类精确字节数**）。

### 未做 / 仍阻塞

- **KE（Kenya）仍真阻塞**：Ookla 把它列为 **N/A**（只收录固网 Rank 135），Opensignal 报告亦无 ⇒ **两条通路都缺**。唯一出路是换事实源类型（需要你点头）。
- **P2（三品牌组合页）· P3 第二件（「eSIM 折扣码」聚合页）** —— 都是**新页型**，属架构变更，**未获授权、未动**。
- 观察项：networks 页的 Ookla 来源行目前印机器字段原文 `2026-08`（形如 `Source: Ookla report , 2026-08.`），CN 页同样如此 —— 属既有形态，本轮**未擅自改**（改它会同时改到 CN 等页，超出指令范围）。
- 全部改动**未 `git commit`、未部署**（用户明令「一旦提交就是正式发布」）。

### 补｜holafly 页「文案与它渲染的表不同真」—— 自查出的第二个缺陷（同日第八十八轮续）

**缺陷**：`id="pricing"` 段的 H2 与导语是**无条件**渲染的，而两张表分别由 `{{ with $tierRows }}` / `{{ with $unlRows }}` 门控。`holafly` 是站内唯一**纯无限量**品牌（有量档 = 0）⇒ 它只出表二，页面上却印着 H2 `Holafly pricing at each data tier` 与导语 `…The cost per gigabyte comes from that same plan, so the two columns always describe one purchase.` —— **既没有数据档位、也没有 $/GB 列**。

**修法**（作用面 = 仅 holafly 的 en/de 两页）：H2 与导语各加一个「只有无限量表」的变体，由 `$tierRows` 是否非空切换；表二的 H3 也只在表一存在时渲染（否则 H2 与 H3 同义）。**零新增行**：行内 `cond (gt (len $tierRows) 0) "key_a" "key_b"` 切 i18n key，H3 用同行 `{{ if }}…{{ end }}` 包住 ⇒ 条件为真时该行产物逐字节不变。i18n **+2 key × 2 语言（1853 → 1855）**。

| 项 | 结果 |
|---|---|
| `npm run validate`（源码 5 道） | **`VALIDATE_EXIT=0`**（en/de 各 **1855** key，逐 key 同序） |
| `npm run build` | **`BUILDB_EXIT=0`**（14m52s）· **1313 页 / 1315 文件 / 7526 JSON-LD 块**；13 道产物闸门全绿，`check_headings` **34138 h2/h3 `bad: 0`**（= 上一步 34140 减去 holafly 两语言各一个 H3）、`check_hreflang` **1313 页 / 3930 标签 / 1310 页** |
| **归属判据**（`verify_no_regression.py --diff` 对**改动前**的基线） | **变更 2 / 新增 0 / 删除 0**，且正是 `esim-providers/holafly/index.html` 与 `de/esim-providers/holafly/index.html` ⇒ 其余 18 个品牌 hub 页**逐字节未变** |
| **文案同真验收**（`.buildlog/r88b_verify.py`） | **断言 122 条 / FAIL 0**：holafly 侧所有「有量表」措辞（`at each data tier` / `cost per gigabyte` / `Lowest cost per GB` / `Unlimited plans by trip length`）**全部消失**，「按行程天数」措辞全部到位；其余 9 品牌 × 2 语言的**原措辞逐字仍在** |
| **独立复算**（`.buildlog/r88_pricing_verify.py`） | **FAIL 0**（表格与 JSON-LD 内容不受影响） |
| 基线 | 刷新为 **1313 文件**，随后 `--diff` 自证 **0 / 0 / 0** |

**★ 附带修掉一个我自己的工具事故**：`.buildlog/r88b_fix_lead.py` 写成 `old → new`（`new` 没回带 `old`）⇒ **把 `h2_pricing` 与 `pricing_lead` 两个原 key 顶掉了**；线索是「键数没涨、`lone_LF` 没涨」。已用 `.buildlog/r88b_restore_i18n.py` 按改动前的逐行读取留痕还原并**逐字复核原值**。⇒ 已写进 `PROJECT.md` 红线 **125 / 126**。

## 已完成（A 德语报告标题守卫缺口 + B P1 剩余 7 国 networks 页 + C 正文 `#N of M` 自我否定清零，2026-10-12 第八十六～八十七轮）

**触发（用户逐字）**：`A,BC 全部完成即可` —— 对上一轮给出的三个选项要求 **三个全做**：
**A** = 先修 `opensignal_title` 守卫缺口（德语 networks 页印英文报告标题）**再**补 7 国；**B** = 直接补 P1 剩余 7 国；**C** = 补完 P0 的另一半（正文三处 `of N` 自我否定）。

### A｜德语 networks 页印英文报告标题（红线 119 的收口）

| 层 | 落盘 |
|---|---|
| 数据 | `data/de/networkreports.toml` 逐国补 `opensignal_title`（**44 国**，34175 B / 582 CRLF，德语覆盖层） |
| 施加器 | `scripts/_loc_de_dates.py`：`de_title()` + `COUNTRY_ALIASES` + 幂等；真源 = `data/countries.toml[ISO].name` + 月名映射；`--selftest 25/25` |
| 守卫 | `scripts/verify_de_data.py` 新增判据 **H `check_report_titles`**；`--selftest 40/40` |
| 真源去重 | `scripts/_gen_de_data.py` 删掉 HEADER 的**第二副本**，改 `from _loc_de_dates import HEADER`（红线 8：一份事实只允许一份真源） |
| **两侧都证** | 对**改造前产物**跑：**13 个德语页印英文标题**（红）→ 改造后 **0**（`.buildlog/r87_assert_A.py`，P1–P4 四段 + 反例注入） |
| 全量 | 本轮构建输出「数据层德语覆盖守卫：全部通过」 |

### C｜正文里三处同款「自我否定」（红线 113 的补全）

改 `i18n/{en,de}.toml` 三个 key：`verdict_met_rank`（verdict **非冠军**分支）、`faq_a_price_met`（FAQ 答案 **+ 同源 JSON-LD**）、`trust_ranked`（Trust 段）。
**刻意保留 2 处**（红线 120）：`of_n_on_gb`（stat tile `#9` + `of 10 on $/GB`）与 `op_market_v1/v2/v3`（**对手向** `Airalo ranks 7 of 10`，且不带 `#`）。

| 项 | 改造前 | 改造后 |
|---|---|---|
| EN 品牌子页**可见文本**含 `#N of M` | **449 / 499** | **0** |
| —（旧侧「干净」的 50 张 **全是 Holafly**：纯不限量品牌走 `verdict_unl` / `faq_a_price_unl` / `trust_unlimited`，本来就没这个说法） | | |
| stat tile / 对手向竞品卡 | 499 / 499 | 499 / 499（**原样保留**） |
| DE 品牌子页 | 对称 | 对称 |

**★ 改完自检出我自己引入的指代漂移（红线 121）**：产物成了
`Saily's best rate in Canada is $2.20/GB; the country benchmark is $0.64/GB — the lowest rate among the 10 providers we track.`
—— 「the lowest rate」紧贴主语 brand ⇒ 读者会读成「**Saily 是 10 家里最低价**」，而 Saily 在加拿大是 **#9**（$2.20 vs $0.64）⇒ 为了消灭自我否定反而写出**自相矛盾的假话**。
修法：让限定语留在它修饰的那个从句里 ⇒ `…$0.64/GB</strong> among the {{ .total }} providers we track.`（de 对称：`… unter den {{ .total }} Anbietern, die wir erfassen.`）。产物级断言加**歧义句黑名单**（`the lowest rate among the` / `der niedrigste Wert unter den`），双侧为 **0**。

### B｜P1 剩余 7 国 networks 页（en + de = 14 篇）

- 7 国：**EG / TW / VN / MA / PL / CH / SA**。站内 `opensignal_facts`（en+de）全部摘自 `networkreports`；外部事实 WebSearch 逐国核实（EG 反恐法护照登记 + 指纹 / TW 实名制 + 机场仅需护照 / VN Decree 49 护照原件 + 活体自拍 + `5G150T` 150,000 VND/5GB/天 / MA 所有 SIM 强制护照登记 + 5G 2025-11-10 三网同日商用 / PL 反恐法每张 SIM 登记 / CH BÜPF 强制登记 + Swisscom 含 Jungfraujoch 3454 m / SA 生物识别强制 + STC 覆盖 AlUla·NEOM）
- 结构照 `content/en/networks/colombia.md`：**21 个 front matter key / 5 个 H2 / 8 条 FAQ / 3 条 `cities_detail`**；`.buildlog/r87c_h2_en.py` 按站内 h2 约定（骨架 + 国家置换，`h2_scoreboard` 点出该国运营商名）改写 14 行
- **源码级预检 12 条全绿**（`.buildlog/r87_preflight.py`：纯 LF / key 集合 / 计数 shortcode 恰好 1 处 / H2 标点（en 禁 `,;:—–`、de 禁 `,;:`）/ `cities_detail` 以 name 起首 / 无整日期 / 德语禁英文国名城市名 / 德语禁 F 黑名单词 / `title`·`seo.title` 无 `$` 与 `#N of M` / 站内链接目标存在 / FAQ 恰 8 条且跨页不重复 / 德语无英文月名）—— 首跑抓到 **4 处德语 H2 逗号**，当场修；另自查出 3 处语病（`Graubunden` 隐式第四张网、挪威…实为法国地名的 Chamonix、`Russia-fast`）
- 页数：**networks 子页 15 → 22（每语言）**（`_index.md` 不算），总页 **1297 → 1311**

### 验收（构建 + 产物断言 + 归属法）

| 闸门 / 断言 | 结果 |
|---|---|
| `npm run build` | **`BUILD_EXIT=0`**（9m23s）· **1311 页 / 1313 文件 / 7516 JSON-LD 块** |
| 13 道产物闸门 | 全绿：`check_headings` **34038 h2/h3 `bad: 0`**；`verify_provider_pages` **499/499**（标题 44–54，均 50.5）；`check_faq_facts` 100 国页 + R10/R11 唯一性；`check_dates`（networks_sub 22）；`check_hreflang` 1311 页 / 3924 标签 / 1308 页；`verify_de_text` A–D·H·I 全绿 + F/J/G 覆盖 **654 德语页**（单元格 14197/14197）；`verify_de_data` 全过（304 数据串 / 38 城市 / 77 记分板）；`_de_schema_audit` JSON 失败 **0**；`check_inline_copy` 0 残留 |
| 页型 | networks **32 → 46**；de 655 / en 656 |
| **A 产物断言** | 130 个页型实例：德语页只印德语标题、英语页只印英语标题；P4 反例注入 OK |
| **C 产物断言** | 499 + 499：`#N of M` 归零；stat tile / 对手卡 499/499 保留；verdict 冠军 50 / 非冠军 449，歧义句残留 **0** |
| **归属法**（`.buildlog/r87_attrib.py`） | 见下表 |

**★ 归属法这次先被自己的旧侧坑了两次（新增红线 117/118）**：

| 版本 | 结果 | 真因 |
|---|---|---|
| v1 | 1895 文件**全变了** | 旧侧 `.buildlog/pub_r87_old` 是 **dev server 产物**：**1296/1297 页含 `<script src="/livereload.js…">`** |
| v2 | 换 `git HEAD` 重建旧侧后仍报 100 未分类 + 52 标题归因失败 | 配置覆盖**只写了 `contentDir`**（漏 `dataDir`/`i18nDir`）⇒ 拿**新 data + 新 i18n** 当旧侧 |
| **v3.3** | **全过** | 修 slug 提取（`country_slug()`）+ 双向判据 + 索引页用链接全集 + 双语正则 |

**★ 顺带更正上一轮的一个错误结论（红线 117）**：上轮据 `verify_no_regression.py --diff` 报「变更 1297 / 1297 全需确认」断定 `docs/regression-manifest.json` **已过期**。**基线从未过期** —— 从 `git HEAD` 重建的旧侧 vs manifest = **1297/1297 sha256 全等**；是当时的 `public/` 被 dev server 污染了（「变更页数 1296」与「含 livereload 的 1296 页」**完全重合**，那正是线索）。

最终断言：

| 断言 | 结果 |
|---|---|
| A 集合 | 共有 **1895** 文件 · 新增 **14**（全是 networks 页，en/de 成对）· 删除 **0** |
| B 计数 | 每页 `tnum font-semibold text-ink-300` 计数序列**恰 1 处**变化且为 **15 → 22**；无导航的别名壳 1 页（`/en/index.html`）跳过 |
| C 分类 | 规范化比对（删 `mega-link` 锚块 + 计数占位 + 折叠空行）后：HTML **变化 974 / 未变 339**；**未分类 0** —— `E3-compare-brand 912` · `E4-hub-de 41` · `E2-networks-de 12` · `E4-hub-en 7` · `E2-networks-list 2` |
| D 资源 | 9 个非 HTML 文本资源（`sitemap.xml`×2 / `llms.txt`×2 / `index.xml`×4 / `en/sitemap.xml`）全部白名单点名；**二进制资源变化 0** |
| **E 归因** | **无法解释的变化行 0**；被判据归因为「去 `#N of M`」的变更行合计 **3492 = 1746 × 2 语言**（与上一轮独立测得的 1746 **完全吻合**） |
| F C | compare 品牌子页 998 张：可见文本含 `#N of M` **449 → 0** |
| G 反例 | 注入 `— rank #9 of 10;` 后 C 判据翻红（判据非恒真） |

数学闭环：`974 变化 + 339 未变 = 1313 个文本产物`；`1311 页 = 1297 旧 + 14 新`；`46 networks = 22 × 2 子页 + 2 索引`。

**基线已刷新**：`verify_no_regression.py --write-manifest` → **1311 文件 / `networks 46`**（`generated_at 2026-10-12T16:12:45Z`），随后 `--diff` 自证 **变更 0 / 新增 0 / 删除 0**；`--selftest` 通过（含 classify 正反例）。

### 纪律
- **未 `git commit`、未部署** —— 改动全部留工作区：**14 个新 md 未跟踪** + **6 个已跟踪文件修改**（`data/de/networkreports.toml`、`i18n/en.toml`、`i18n/de.toml`、`scripts/_gen_de_data.py`、`scripts/_loc_de_dates.py`、`scripts/verify_de_data.py`）
- 改已存在文件一律 **bytes 读写** + 复核换行：`i18n/*.toml` 纯 LF（1897/1898 行，改后不变）、`data/de/networkreports.toml` 纯 CRLF（582）不变
- `stamp_checked.py` 指纹只覆盖 `data/plans/**` 与 `data/providers.toml` ⇒ 本轮改 md/scripts/i18n **未误盖任何 `checked` 日期**

## 已完成（GSC「已发现 – 尚未编入索引」治理：国家页新增「价差最紧 6 对」对决入口 + 对决页补「按行程类型怎么选」段 + 去模板句，2026-10-11 第八十二轮）

**触发（用户逐字）**：3 个对决页 URL（`airalo-vs-alosim` / `airalo-vs-roamic` / `alosim-vs-saily`）+「很多这样的竞品页面，谷歌搜索控制台，提示已发现，尚未编入索引 应该如何优化」
**用户选定范围**：`P2 vs 页专属段落 + 去模板句` 与 `P0 国家页 + 品牌 hub 对决入口`（明确**不做** P1 sitemap 分片、**不做**「先只观察」）

### 诊断：**抓取侧**问题，不是质量侧
- 线上 sitemap **644 条**的页型配比：`/compare/{国}/{品牌}/` 排列页 **499 = 77.5%**、vs 对决页 **45 = 7.0%**、国家页 51 = 7.9% ⇒ 抓取预算被排列页稀释
- 入站来源实测（`roamic-vs-saily`）：**48 条 = 45 个其他对决页 + 2 个品牌 hub + 1 个 matchups 枢纽页；国家页 0、首页 0** ⇒ 45 个对决页互链，**互链双方都没被爬过** = 抓取死锁
- 已排除（实测正常）：canonical = `.Permalink`、hreflang 双侧齐、robots Allow all 且声明 en+de 两条 sitemap、无 noindex、vs 页 247 KB / gzip 19 KB

### P0-a 品牌 hub 对决入口 —— **实测无需改动（我原判为误判）**
- 10 个品牌 hub 每个已链出**恰好 9 个** `/compare/{a}-vs-{b}/` = 全部对手（10−1）；`⑥ 对比对手` 段早已覆盖全量
- 我最初的「只链 2 个」是把「每个 vs 页从品牌 hub 获得 **2 条**入链」误读成「hub 只链 2 个」，源头是一次 `curl` 静默截断造成的连锁误判

### P0-b 国家页新增「该国价差最紧的 6 对」入口（`layouts/compare/single.html` + 5 个 i18n 键）
- 100 个国家页（en 50 + de 50）新增 `#closestmatchups` 段：6 张卡片，每张给出两国在该国的真实入门价 + **价差数字**，链向对应对决页
- **选组口径用数据选**（`python -X utf8 .buildlog/r82_pick_modes.py` —— 六种口径用同一把尺子量「不同组合集数 / 最高重复次数」，50 国 / 10 品牌）：

  | 口径 | 不同组合集数 | 最高重复次数 |
  |---|---|---|
  | 价差最大（绝对） | 38 | 5 |
  | 价差最大（相对） | 42 | 4 |
  | 最便宜 4 强两两组合 | 24 | 9 |
  | 冠军 vs 其后 5 名 | 38 | 5 |
  | 6 强内部固定 6 对 | 24 | 9 |
  | **相邻名次里价差最小的 6 组 ← 采用** | **47** | **2** |

- 目标页存在性：slug 空间**闭合** —— `scripts/gen_vs_pages.py` 生成完整 C(10,2) = 45 对，`content/<lang>/compare/` 下 45 个 vs 页全在，文件名规则同为「按 key 字母序 `a<b`」

### P2 对决页补「按行程类型怎么选」段（`partials/vs-agg.html` + `compare/vs-single.html` + 2 个 i18n 键）
- 档位边界**单点定义**在 `vs-agg.html`（轻量 `0 < GB ≤ 5` / 重载 `GB > 10`；无限档两档都不收），文案里的数字由该文件返回值注入 ⇒ 杜绝「代码改了、文案没改」
- 90 个对决页（en 45 + de 45）新增 `#fityour` 段：两国在共同国家里「谁更便宜」的胜 / 平计数

### 去模板句
- 实测 45 个对决页共享的**唯一**正文段落是 `compare_vs_single__lead` 的第二句（`… every verdict on this page is a literal sort of our dated price database.` 45× 逐字）
- 按红线 93 纪律①**并进含变量的那句**（披露措辞**一字未动**，只由独立句降为句中从句）⇒ 旧句命中 **45 → 0**（en / de 双侧）

### 验收（全部为**产物文本断言**，按用户约定不做截图）
- `npm run build` **BUILD_EXIT=0**；5 道源码闸门 + 13 道产物闸门全绿
- **逐字节归属法**（`.buildlog/r82_attrib.py`）：国家页产物 = 旧产物 + 恰好 **3 段插入**（2 条 TOC `<li>` + 1 个段落块）；对决页 = **1 处单行替换**（lead 并句）+ **1 段插入**；其余字节与改造前快照**完全相同** ⇒ 零外溢
- **独立复算对账**（不看模板）：国家页 **600 张卡片**（en 300 + de 300）逐条等于从 `data/plans/*.toml` 直接重算的结果，**0 死链**；P2 段落 **144 条**逐条一致
- **反同质化前后量化**（`p78_vs_dup_probe.py`，45 个对决页正文区）：逐字句 2012 → 2039（−45 并句 + 72 新增）、去重 1070 → 1140、**逐字重复率 46.8% → 44.1%**、只出现 1 次的句子 1021 → **1093**
- 守卫两侧自检：`.buildlog/r82_guard_selftest.py` 4 例全过（正例不误伤 / 反例必红）

### 本轮踩到两个新坑（已写进 PROJECT.md 红线 107–110）
1. **复用品牌 hub 的 `id="headtohead"`** ⇒ `verify_no_regression.py` 检查 A **当场报 100 处**「出现了只属于 `['provider_hub']` 的区块」。修法是**新开专属 id**（`closestmatchups`）+ 在表里登记，**不是**放宽白名单
2. **TOC 登记行新占一行** ⇒ 每条 `{{ $toc = … append … }}` 都往产物吐 1 个 `\n`，100 个国家页各多 1 行空白。按红线 106 的修法**并进既有行**后产物 delta = 0

### 未做 / 后续观察
- P1（sitemap 分片）与 P3（先只观察）按用户选择不做
- 全部改动**未 `git commit`、未部署**（部署由用户自行进行；Jetpac 用户已确认线上已上线）
- 复测建议：部署后 2–4 周看 GSC「已发现」计数是否下降；45 个对决页自此各获得来自 100 个国家页的上下文入链（此前国家页入链为 0）

## 已完成（德语 JS 文案漏译 **已修复** + 新增第 13 道产物闸门；逐字节归属法证明零外溢，2026-10-11 第八十一轮续跑）

**触发（用户逐字）**：「A 修这 3 个模板（约 20 处，会变产物字节，需逐字节归属法证明零外溢）；B 只建那条缺失的守卫 `check_inline_copy.py`（防下次再漏，不动产物）；C 先修 A 里的「跳英语站」3 处硬编码路径（影响转化，收益最高）  这些全部优化」。

### B · 新守卫 `scripts/check_inline_copy.py`（23348 B，进 `check:output` 第 13 项）

三条判据，全部 **ERROR**：`[1]` 脚本体英文残留 · `[2]` 站内路径字面量 · `[3]` head 元数据（`title`/`og:*`/`twitter:*`/`description`/`ld+json` 全部字符串值）。
- 扫 **`public/**/*.html` 全量**，不只 `*/index.html` —— `public/<lang>/404.html` 不是 index.html，这是红线 88 的**第二形态**（本仓原有产物守卫只 glob index）。
- 用**英语封闭词类密度**判据，不用黑名单（`verify_de_text.py` 的 F 段自承「清单永远追不上数据」）。
- **`--selftest` 11 项**（含 `bad-path-dup` 反例）；**新判据必须先对旧产物跑出红** —— 已加 `--root DIR` 参数专为此。
- 实测：`--root .buildlog/pub_r81_pre` = **FAIL 26 条 / 324 处**（exit 1）→ `public/` = **0 / 0 / 0**。两条独立路径互相印证。

### A + C · 改了 5 个模板 + 14 个 i18n key

| 文件 | 改动 |
|---|---|
| `layouts/compare/vs-single.html` | 45 对决页 × 2 语言：5 处 JS 文案改 `{{ i18n \| jsonify \| safeJS }}` + `T()` `%s` 顺序替换；**`'/compare/'` → `{{ relLangURL "compare/" }}`（C：勾选两品牌后不再跳英语站）** |
| `layouts/tools/list.html` | `/de/tools/`：11 处 JS 文案 + **3 处硬编码路径（C）** + 国家下拉 `<optgroup label>` 改本地化（`REGIONS` 数据岛）+ **套餐名过 `plan-name.html`**（原本裸 `.name`） |
| `layouts/partials/head.html` | `<title>`：`cond (eq .Kind "404") (i18n "404__page_not_found") .Title` |
| `layouts/partials/schema.html` | BreadcrumbList 当前页 `name` 同上 |
| `layouts/esim-providers/single.html` | **新守卫当场揪出的第 4 处病灶**：JSON-LD `Offer.name` 裸 `$c1.name` → 过 `plan-name.html`（德语品牌 Hub 曾印 `aloSIM republic of ireland eSIM`） |
| `i18n/{en,de}.toml` | 各 +14 key（197641→198512 / 213989→214945），**1832 : 1832 且顺序逐 key 一致** |
| `scripts/check_i18n.py` | 判据 4 **WARN → ERROR**（红线 104：能发现用户可见缺陷的判据必须 ERROR） |
| `package.json` | `check:output` 12 → **13 道** |

**判据 4 转 ERROR 的前置条件已满足**：`validate` 报「内联脚本文案 5 处 → **0 处**」。

### 逐字节归属法（`scripts/_r81_attrib.py`，用户点名要求）

`npm run build` **三次**（修 2 轮自坑后重跑），末次 `BUILD_EXIT=0`、13 道产物闸门全绿。

| 层 | 断言 | 结果 |
|---|---|---|
| L1 | 未变更页 sha256 与改造前相同 | **1188 / 1188** |
| L2 | 90 对决页共用同一差异块、逐字节还原；剥掉脚本体后**非脚本区不变** | **90 / 90** |
| L3 | tools 2 页：差异**全在 `<script>` 内**（服务端渲染的可见 HTML 一个字节不动）；404 页 3 处全为 head 元数据 | ✓ |
| L4 | 品牌 Hub 10 页：行数不变，**107 处变更全为 JSON-LD `"name"` 值**，前后缀字节不变 | ✓ |

**变更集合恰为 103 页 = 45 `vs_en` + 45 `vs_de` + 10 `hub_de` + `tools_en` + `tools_de` + `404_de`**，无 `ADDED`/`DELETED`。

### ★ 归属法当场揪出 3 处**我自己引入**的漂移（都已修）

1. **`' GB'` → `"GB"` 丢空格**（EN/DE 同时 `5.00 GB` → `5.00GB`）。`GB` 既不是英语词也不是路径 ⇒ **非受迫改动**，已回原为 `' ' + {{ i18n "g_unit_gb" }}`。
2. **`&amp;` 漏退实体**：`REGIONS` 数据岛直接吃 `partial "region-label.html"` 的 HTML 值，`og.label`（**DOM 属性，不解析 HTML**）会印出 `Afrika &amp; Nahost`。`layouts/index.html` L243 的注释**逐字写明了这个坑**（+ `| htmlUnescape`）—— 我引用了真源却漏抄。已补 + 注释。
3. **2 个换行被吃掉**：新增的 `{{- /* … */ -}} … {{- end -}}` 纯逻辑块两端 dash 吃掉了 HEAD 本就存在的空白 ⇒ `tools/index.html` 少 2 字节。修法：尾部 `{{- end }}` **故意不写 dash**。

**唯一保留的 EN 排版变化（受迫，非缺陷）**：`$2.50/day` → `$2.50 / day` —— 德语必须显示 `/ Tag`，而全站唯一的 `/day` 后缀真源是既有 key `tools_list__per_day_suffix`（值 `" / day"`），复用它就把同页服务端渲染的 `— GB / day` 统一了；另建 key 会违反红线 8。

**顺手修正的守卫缺陷**：`de/tools/index.html` 的 `subUrl`/`countryUrl` 去转义后都是 `/compare/` ⇒ 46 页被报成 47 页。加 `_uniq`，按「**页**」计数，并补 `bad-path-dup` 反例进自测。

### 交付与状态

- 新守卫 `scripts/check_inline_copy.py`、归属法骨架 `scripts/_r81_attrib.py`、对照快照 `.buildlog/pub_r81_pre/`（改造前 1291 页，已证与已提交基线逐字节相同）
- 改动同步 `PROJECT.md`（红线 103 补「已建 + `@graph` 是容器 + 只 glob index 两形态」；**新增 105/106**）、`STATUS.md`（本节）、`docs/de-audit-2026-10-11.md` §6
- ⚠ **回归基线 `docs/regression-manifest.json` 尚未刷新**（见下方待办）；**未 `git commit`、未部署**

## 已完成（德语站审核：SEO 合格；静态文案 100% 德语化，**JS 运行时文案 47 页漏译**，2026-10-11 第八十一轮 · 仅审核、零改动）

**触发（用户两问，逐字）**：「你在德语的 确定每个页面，每个功能都翻译成德语了吗， 以及每个页面的技术 seo是否符合要求，在审核下」。

**结论（一句话）**：**SEO 合格；翻译的静态层 100% 完成，但「JS 运行时生成的交互文案」漏译 47 个页面** ——
根因是**全站所有德语文案守卫都会先挖掉 `<script>` 再判**（正确做法），于是写在 `<script>` 里的用户可见文案**没有任何一条守卫看得见**。

**② 技术 SEO：德语 644 页逐页实测，13 类判据 0 违规**（`lang` / `title` / `description` / `canonical` 自指 /
`hreflang` + `x-default` / `noindex` / OG / `twitter:card` / `viewport` / `H1==1` / JSON-LD 合法 / `<img alt>` 0 缺 /
内链语言 0 泄漏）。158526 张图**无一张缺 alt**。唯一命中页是 `public/en/index.html`（Hugo `alias` 壳，按设计无 SEO 元素）。
软性优化项：`title` >65 字符 **2 页**、`description` >160 字符 **77 页**（全在 `compare/<country>/[holafly/]`）。

**① 翻译：分层现算**

| 层 | 结果 |
|---|---|
| i18n | en 1818 : de 1818 key，集合差集 **0**；de 空值 **0**；`de 值 == en 值` 仅 **31** 条且全天然不可译（`GB`/`eSIM`/`FAQ`/`Code`/`App Store ↗`/占位符模板） |
| 内容 | `content/en` 644 : `content/de` 644 md，差集 **0**；与英语逐字节相同的德语正文 **0** 篇；555 篇「正文为空」是**设计**（vs 页 / 子页正文由模板+数据渲染） |
| 静态可见文本 | 644 页，用**不依赖黑名单**的「英语特有词密度」判据 → **0 页含英文** |
| 属性层 | `alt` / `aria-label` / `placeholder` / `title=` → **0 处英文** |
| 标题摘要 | 644 页的 `title`/`description`/`og:title`/`og:description`/`H1` → **0 页含英文** |
| **JS 运行时文案** | ❌ **47 页有英文**（见下） |

**★ 缺口：47 / 645 个德语 HTML（3 个模板，全部绕过 `layouts/index.html` 已验证的正确范式
`{{ i18n "…" }}` + `{{ relLangURL "…" }}` 服务端注入 JS）**

1. **`layouts/compare/vs-single.html` → 德语 45/45 对决页全中**：L517-526 六句 JS 文案全英文
   （`'Compare ' + … + ' →'` / `'Pick two providers'` / `'Tick exactly two — …'` / `'One more pick — …'` /
   `'Opening the computed … head-to-head.'`）；**且 L516 `href = '/compare/' + …` 硬编码 → 勾选两个品牌后按钮跳英语站**。
2. **`layouts/tools/list.html` → `/de/tools/`，程度最重（四类）**：
   (a) 11 句 JS 文案英文（`'Our pick'` / `'Other matching plans'` / `'No plan matches — … (unlimited …).'` /
   `'See '` / `'Read '` / `'Compare all '` / `' days'` / `'/day'` / `'Your estimate · '`）；
   (b) **国家下拉 `<optgroup label>` = 英文区域名**（L252-254 `og.label = r`，`r` 是英文区域键）；
   (c) **结果卡片显示供应商原始英文产品名**（L12 用 `.name` 原文、**未过 `partials/plan-name.html`**）→ 产物现算 **7884 处**英文
   （3400 种，例 `'Unlimited / 7 Days'`×182、`'United Arab Emirates (UAE)'`×37、`'republic of ireland'`×32）；
   (d) 3 处硬编码站内路径（L281-283 `/compare/`、`/esim-providers/`）→ 三个按钮跳英语站。
3. **`/de/404.html`**：`<title>` / `og:title` / JSON-LD BreadcrumbList `name` = `404 Page not found`（模板正文本身是德语）。

**为什么 5 道守卫全绿却漏了**（判据盲区，写进 PROJECT.md 红线）：
`verify_de_text` **E1–E5** 扫可见文本但**先挖 `<script>`**；**F** 是黑名单（23 短语 + 8 词，`Pick two providers` 不在内）；
**G** 的清单来自「已进 `strings.toml` 的数据串」，JS 硬编码文案不是数据层字符串；
`check_i18n` 的内联脚本判据 ① 只 `warns.append`（**WARN 不失败构建**）② 正则要求字面量 ≥14 字符 → `'Compare '`（8 字符）**静默漏报**；
`_de_link_leak_audit` **[1]** 读产物 `<a href>`，而 JS 运行时赋值的 href 不在其中。

**附带发现**：审核开始时 `public/` 有 **1315 个文件**被 `hugo server` 污染（baseURL = `http://localhost:1313`，
`check_output` **EXIT=1**、sitemap 全 localhost）→ 已重跑 `npm run build` 修复（**BUILD_EXIT=0**，hugo **287.9s**，sitemap 644 条域名正确）。
另：两个 sitemap **均无 `xhtml:link` hreflang 注解**、根 sitemap 无 `sitemapindex`（只有 644 条英语 loc）—— **不影响发现**
（`robots.txt` 已声明 2 行 Sitemap、页面级 3864 个 hreflang tag 互指 OK）。

**交付**：`docs/de-audit-2026-10-11.md`（完整报告：逐处证据 + 判据盲区表 + 修复方案 + 复现命令）；
探针 3 个（均带 `--selftest`）：`.buildlog/p81_page_audit.py`（SEO 13 判据）、`.buildlog/p81_js_audit.py`、`.buildlog/p81_de_text_audit.py`。
**本轮未改任何源码/数据/产物，未 commit、未部署。**

## 已完成（「线上 old」≠「本地坏」：德语站从未提交 + public 被 localhost 污染，2026-10-10 第八十轮 · d55）

**触发（用户四问，逐字）**：「`https://www.esimsift.com/de/sitemap.xml`  为什么这个 xml 中 德语的其他页面都没有， 搞什么
/ 这个 robots.txt https://www.esimsift.com/robots.txt 是不是 应该加上 de/sitemap.xml
/ 定位到 https://www.esimsift.com/de/ 后 为什么底部的菜单导航， 还有很多没有 /de/， 顶部菜单导航也没有
/ 是否还存在其他类似问题， 请一并检查」。

**结论（一句话）**：**不是模板坏了，是「提交进 Git 的德语站根本不完整」。**
`content/de/` 在 **HEAD（= 线上正在跑的那个提交）只有 55 个文件**，其中 **54 个 `noindex: true`**；工作区 **644 个、noindex 全解禁**。
三个现象是**同一个原因的三个投影**，只差**提交 + 部署**。

**线上 = HEAD 的构建（6 条判据全部对上）**

| 判据 | 线上实测 | HEAD 源码 |
|---|---|---|
| `/sitemap.xml` 条目 | **644** | `content/en/*.md` = 644 |
| `/de/sitemap.xml` 条目 | **1** | 55 − 54 noindex = 1 |
| `robots.txt` 的 `Sitemap:` 行数 | **1** | `HEAD:layouts/robots.txt` = 1 行 |
| `/compare/matchups/` 含 `ItemList`/`FAQPage` | **0 / 0** | `HEAD:…matchups.html` = 0 / 0 |
| `/de/` 首页 footeren 带 `/de/` 的链接 | 8 条 | 那 3 类德语页在 HEAD **存在** |
| `/de/` 首页 footer 不带 `/de/` 的链接 | 20 条 | 那 20 类德语页在 HEAD **不存在** |

**① `de/sitemap.xml` 只有 1 条**：`sitemap-urls.html:36` 的 `{{- if not .Params.noindex -}}` 会把 noindex 页排除（设计如此，避免 GSC
报 *Submitted URL marked 'noindex'*）⇒ 55 − 54 = 1。本地工作区产物实测 **`public/de/sitemap.xml` = 644 条**、**645 个德语 HTML 里 0 个带 robots meta**。

**content/de 的 HEAD vs 工作区**：`(根) 1→7` · `compare 51→596` · `guides 1→11` · `networks 1→13` · `research 1→4` ·
`esim-providers 0→11` · `esim-deals 0→1` · `tools 0→1`。**新增未提交 589 个**（compare 545 / networks 12 / esim-providers 11 /
guides 10 / 根 6 / research 3 / esim-deals 1 / tools 1），**改过（删 noindex）54 个**。
`content/en` : `content/de` = **644 : 644**，页面型 **636 : 636**，零缺失。

**② `robots.txt` 无 `de/sitemap.xml`**：`Sitemap: {{ .Site.BaseURL }}de/sitemap.xml` 这一行**在工作区、未提交**（HEAD 只有根那一行）。

**③ footer/header 缺 `/de/`**：`lang-href.html` 是**三层兜底** —— ① 当前语言有该页 → `.RelPermalink`；② **别的语言**有该页 → **那个语言的
`.RelPermalink`（英语 URL，没有 `/de/`）**；③ 都没有 → `relURL`。所以「德语页缺失」**不报 404，而是静默退化成英语 URL**。
线上德语站只有首页有内容 ⇒ 30 条链接退化。**本地实测越界 = 0**（德语页里指回英语路径的站内链接 646 种 / 1290 处，**100% 是语言切换器**：
645 × `/`（`en`）+ 每页 1 条 `English`，两者本就该指英语）。

**④ 其他同类问题（已全量扫过）**：`_de_link_leak_audit.py` **[1][2][3] = 0/0/0**；`check_hreflang` **OK 1291 页 / 3864 tags / 1288 页**；
德语页 `<html lang>` **645/645 = `de`**；`canonical` / `og:url` 路径 **645/645 带 `/de/`**。**SEO 面无非同类泄漏。**
唯一真问题在**本地产物**：见下。

**★ 另一处真问题：本地 `public/` 被 `localhost` 污染 —— 1315 个文件**（`.html` 1291 / `.xml` 19 / `.txt` 3 / `.json` 2），
mtime **10-10 22:19–22:21**（在最后一次构建**之后**）。成因：**手敲了不带 `--renderToMemory` 的 `hugo server`**，它用
`http://localhost:1313/` 覆盖 baseURL 并**把整站写进 `public/`**（`public/sitemap.xml` 644 个 `<loc>` 全变 localhost、
`public/robots.txt` 写成 `Sitemap: http://localhost:1313/…`）。守卫原文已抓到：
`[A] 1315 个产物含 localhost —— 本地 hugo server 的 baseURL 泄漏进了 public/（重新跑 npm run build 即可修复）`。
⇒ **本轮已重跑 `npm run build` 恢复**（复核见下）。**再次重申：预览只用 `npm run dev`。**

**附带发现（未擅自改）**：**563 个德语内容文件**的 front matter 里留着已过期的注释
`# TODO(de)：… D9 解禁时统一删掉上面 noindex 行。`——而「上面那行」**早已删掉**（54 行 noindex 已全移除）。
它只是 YAML 注释、**不进产物**、对读者与 SEO **零影响**，但会误导后来人。清理 = 563 文件各删 1 行、**产物逐字节不变**。

**交付文档**：`docs/de-deployment-diagnosis-2026-10-10.md`（含「部署后 4 条复核命令」）。
**纪律沉淀**：PROJECT.md 红线 **101**（线上现象先分「本地产物 / 已部署产物」两侧再判）/ **102**（`lang-href` 三层兜底的副作用是
**语言泄漏而非 404** ⇒ 「德英页数 1:1」是硬不变量）。**改动仍未 `git commit`、未部署。**

## 已完成（Versus 导航下拉收窄为 6 组编辑精选 + 逐字节归属证明，2026-10-10 第七十九轮 · d54）

> 诉求（用户逐字）：「Versus 下的品牌对比，只需要 airalo 对 holafly / yesim / nomad / saily / jetpac / roamic，只需要这几个。」

**① 落点**
- **新建** `layouts/partials/nav-matchups-featured.html` —— 6 个**页面 slug 全形**，从
  `partialCached "nav-matchups.html"` 的 45 组里按 `printf "%s-vs-%s" .ka .kb` 命中，返回**同构** `[]dict{url,ka,kb,na,nb}`。
- `layouts/partials/header.html`（19715 → **20045 bytes**，纯 LF）：`w-[36rem]` → **`w-[26rem]`**、
  `grid-cols-3` → **`grid-cols-2`**、面板计数取 `$vsItems`（= 6）、尾链「All N matchups →」取
  **`$vsAll`**（= 45，指枢纽页里的全量）；新增变量**并进既有行**、说明**并进既有注释块**（红线 3）。
- `nav-matchups.html` **一字未动** ⇒ 页脚上下文推荐与 `/compare/matchups/` 枢纽页仍用全量 45 组。
  **收窄导航 ≠ 删页**。

**② 产物级证据（现算）**
- 面板对决链接：**1290 / 1290 页恒 6 条**（另 1 页 `/en/index.html` 是无 `<nav>` 的 meta-refresh 别名壳）。
- 链接集合**全站只有 1 种**（出现 1290 次），顺序正是指定的 6 组；**语言前缀错误 0 处**。
- 面板**可见数字恒 {6, 45}**（计数 6 + 尾链 45）。
- 枢纽页 en/de 各仍列 **45** 组；页脚仍 **53 种**上下文组合、每页 6 条。
- 45 组对决页全站入链 **min / 中位 / max = 98 / 300 / 1812**，**零孤岛**。
- ⚠ **代价说清**：第七十八轮那 45 页入链 **1388–1812**（导航每页都给全部 45 组），收窄后未被精选的
  39 组降到 **98–300**。98 条站内入链对 Google 足够，但这是收窄的必然代价 —— 若 GSC 仍报未编入索引，
  **第一顺位是往精选清单加组，而不是改文案**。

**③ 逐字节归属（不跑第二次全量渲染）** —— `.buildlog/p79_attribution.py`
- 判据：把新产物里那段面板**还原成改动前的渲染形态**（45 组 / `w-[36rem]` / `grid-cols-3` / 计数 45），
  整页 sha256 应等于第七十八轮基线。**结果 1291 / 1291 页全部相等** ⇒ 改动零外溢、页内其余部分零漂移。
- 与 `verify_no_regression.py --diff` 交叉验证：变更 **1290** / 新增 **0** / 删除 **0**，未变者正是那个重定向壳。
- 基线已刷：`generated_at` `10:57:47Z` → **`14:02:33Z`**（1291 文件，纯 LF）。
- ★ 还原所需文案/顺序**全部从真源读**（`providers.toml` 字母序两两组合 + `i18n/*.toml`），不手抄。

**④ 构建与闸门** —— `.buildlog/build_r79b.log`：**`BUILD_EXIT=0`**；hugo `Total in 198917 ms`；
`validate` 5 道 0 error（`531 layout classes all present in compiled CSS`）；`check:output` **12 项全绿**
（1293 files / 1291 pages，7416 JSON-LD）；`check_headings` **33248 h2/h3, bad: 0**。
旁证 `.buildlog/p79_nav_probe.py`：**自检 7/7（含 5 条硬反例）+ 正式扫描 0 问题**。

**⑤ 仓库卫生**
- `.gitignore` 295 → **419 bytes**（补 `__pycache__/` + `*.pyc`）；`git rm -r --cached scripts/__pycache__`
  ⇒ `scripts/` 下 pyc 跟踪数 **0**。
- 结论（给用户问的「能否整目录排除」）：`.buildlog/` ✅ 能（已忽略、跟踪 0）；`scripts/` ❌ **不能**
  —— `package.json` 的 build/validate/check:output/stamp/dev 共引用 **23 个**脚本，排除后新克隆跑不起来；
  `scripts/scrape/`（519 文件 / 7.8 MB）**不是垃圾**，是数据管线的采集工具 + 原始抓取证据（PROJECT.md 明写「勿删」）。

**⑥ 本节未动**：`header.html` 的其它面板、页脚、枢纽页、i18n key 数（仍 **1818 key**，本轮**没加也没删**）。

## 已完成（导航 hover 对决菜单 + matchups 充实 + 对决页/品牌页过滤器 + 仓库卫生 + 「已发现未编入索引」量化归因，2026-10-10 第七十八轮 · d53）

**触发**（用户点名 7 问，原文见工作日志）：① 导航 hover 出品牌对决并可点击；② 删掉 `/compare/matchups/` 的「Compare country by country」；③ matchups 页内容单薄；④ 对决页胜者徽章点击要跳到 `/compare/{国家}/{品牌}/`；⑤ 对决页要加「按国家 + 按 GB」过滤；⑥ 品牌×国家页要加「按 GB」过滤；⑦ `.buildlog` 等垃圾文件别进 GitHub；⑧ 对决页 GSC 报「已发现，尚未编入索引」，是不是同质化所致。
**思路**：①②③④⑤⑥ 改渲染文件 + i18n + CSS；⑦ 只做 `.gitignore` + 退跟踪（**`.buildlog` 头一次被忽略**）；⑧ **先量化再动手** —— 建两支探针，实测后才知道该修什么。
**一句话结论**：**不是逐字复制粘贴型同质化**（去重后 96.4% 的句子全站唯一）；真因是**站内可达性** —— 39/45 个对决页全站只有 49 条入链，已修到 **45 页全部 ≥ 646 条（英语侧）/ 1388–1812 条（全站 en+de，零孤岛）**。

### ① 导航 hover 对决菜单（`partials/nav-matchups.html` 新建 + `header.html`）

- **新真源** `partials/nav-matchups.html`：从 `i18n-data.html` 推导 10 品牌 → 45 组两两组合 → `site.GetPage` 门控后返回 `[]dict{url,ka,kb,na,nb}`；`partialCached` 缓存。**导航与页脚共用它**，不抄第二份清单。
- VS 项从单链接改成 `group relative` + `.nav-mega w-[36rem] right-0` 三列网格：列出全部 45 组 `A VS B` + 面板尾「All N matchups →」；`group-focus-within:*` 保证**键盘可达**（移动端仍是抽屉菜单）。
- `{{ if gt (len $vsItems) 0 }}` 门控，`{{ else }}` 退回单链接（与既有 Network map 降级逻辑同构）。
- `header.html` 17326 → 19715 bytes（186 → 212 行）。

### ② ③ matchups 页：删 `<details>`、充实内容、补结构化数据（`layouts/compare/matchups.html`）

- **删**：上一轮自己加的 `<details class="matchup-more">` 整块 + `$diff` 计算 + `"top"` 字段 + 4 个 i18n 死 key + `.matchup-more` CSS 整段（`main.css` 10582 → **10001 bytes**，回到第七十七轮之前的体积）。
- **加 §scoreboard**：10 行品牌战绩榜（名次/对战数/赢国/输国/平局），品牌名链到 `/esim-providers/{key}/`。
- **加 §faq**：4 条 `details.faq-item`。
- **加两段 JSON-LD**：`ItemList`（45 个 `ListItem` + `numberOfItems`）+ `FAQPage`；`_de_schema_audit` [5] 的「同页同 `@type` 不得出现两次」约束下，**不能再借 `partials/schema.html` 已产出的 `BreadcrumbList`**。
- 卡片恢复单 `<a class="card card-hover group p-5">`（上一轮为塞 `<details>` 才拆的 wrapper 一并收敛）。
- 10471 → 15078 bytes（125 → 197 行）。

### ④ ⑤ 对决页：胜者徽章变决策出口 + 国家/GB 双过滤（`layouts/compare/vs-single.html`、`partials/vs-agg.html`）

- **胜者徽章 → 链接**：唯一赢家 ⇒ `<a href="/compare/{国家}/{赢家}/">`（读者下一步真的想看的页）；**并列 ⇒ 保持无链接 `tie` 徽章**（不给错的一页发链接）；`aria-label` 服务端渲染整句，德语走 `name_acc` 宾格。
- **新增「Cheaper entry 那一条套餐的数据量」列**：`vs-agg.html` 新增 `aMinGB`/`bMinGB`，**与 `aMin`/`bMin` 共用同一个 if 分支赋值** ⇒ 结构上不可能「价格取自这条、数据量取自那条」。
- **过滤条**：国家搜索框（`data-name` 用**本语言**国名）+ 8 档数据量 chip + 计数（服务端渲染整句）+ 计数模板 + 空态。档位只渲染**真出得现**的桶（`$szCnt`）。
- **新增 §gap**：本页价差最大的 3 国卡片（各自 3 条内链 → `/compare/{国家}/{赢家}/`）。
- 30799 → 43485 bytes（391 → 542 行）。

### ⑥ 品牌×国家页：数据量区间过滤（`layouts/compare/provider.html`）

- 在既有「旅行时长」chip 旁加**同形**的数据量区间 chip（8 档）+ 计数行；**两个过滤器互不重置**（`curDays` 记忆）。
- 语义：**天数 = 覆盖型需求 → `≥` 正确**；**数据量 = 预算型需求 → 区间**（左开右闭，`gb=0` 只进无限桶）。这条铁律与第七十七轮一致，两页 chip 语义完全同构。
- `apply(n)` 改为 `hidden` 式过滤；套餐 ≤3 的页面按设计不渲染筛选器。
- 92843 → 97681 bytes（1259 → 1326 行）。

### ⑦ 仓库卫生（`.gitignore`）

根因：`.buildlog/`（**实测一次累积到 258MB**）、`_competitors/`、`_net_results/`、`docs/internal/` 全在仓库目录里且**从未被忽略**。
- `.gitignore` 176 → 295 bytes：加 `.buildlog/`、`docs/internal/`、`_competitors/`、`_net_results/`。
- 索引 **2664 → 2041** 文件（`git rm --cached` 暂存删除 **623** 条，未 commit）；四类目录跟踪数 **全部 0**；根级只剩 **9** 个被跟踪文件。
- **核查结论**：`??` 203 条全是真实站点资产（`content/de/**`、`data/de/**`、`scripts/**`、`nav-matchups.html`）⇒ **没有任何垃圾会进 GitHub**。

### ⑧ 「已发现，尚未编入索引」量化归因（**本轮最有价值的部分**）

**修复后的独立复核**（`.buildlog/p78_side_probe6.py`、`.buildlog/p78_lang_prefix_probe2.py`）：
- 页脚对决链接已**真上下文相关**：1290 页共出现 **53 种不同组合**（改造前是写死的同 1 组）；
  单个对决页的**页脚**入链最少 **102** 条（改造前最低 **49** 条）。
- **45 个对决页全站入链 1388–1812 条 / 零孤岛**；导航面板 1290 页每页恒 45 条、**语言前缀错误 0**。
- ⚠ **口径**：英语侧口径 646（正则 `href="/compare/` 紧跟，不含 `/de/`）；全站口径 1388–1812（含 en+de）。


**先纠正口径。** 「句子骨架去重率」这个口径必然虚高：programmatic SEO 的数据驱动句抹掉变量后一定同形。Google 的 *minor variations* 指**正文文本逐字相同**。故新建双口径探针 `.buildlog/p78_vs_dup_probe.py`（正文区 `<main>`，两口径并列）：

| 指标 | 改造前 | 改造后 | 变化 |
|---|---|---|---|
| 正文逐字句 总数 / 去重 | 1877 / 999 | 2012 / 1070 | +135 / +71 |
| **正文逐字重复率** | 46.8% | **46.8%** | **±0（没有做坏也没做假）** |
| **全站 ≥40 次逐字复制句** | 16 | **16** | ±0 |
| **只出现 1 次的逐字句（真正独占）** | 963 | **1021** | **+58** |
| 正文骨架去重（辅口径） | 124 | 185 | +61 |
| 骨架重复率（辅口径） | 93.4% | **90.8%** | −2.6pp |
| 只出现 1 次的骨架 | 66 | **112** | +46 |
| 每页独有句中位 | 42 | **48** | +6 |
| 正文词数 min/中位/max | 1912/1945/1987 | **2359/2397/2435** | 中位 +452 |

**16 条逐页复制句的成分**（已逐条回查 i18n key）：**6 条是站内共用控件/披露**（对比构建器、条形图图例、方法/披露链接）—— 逐页相同**是正确的，不该改**；**10 条是说明句与 FAQ 答案** —— 可继续数据化，收益递减。

**真因（内链可达性）**：

| 指标 | 改造前 | 改造后 |
|---|---|---|
| 对决页入链页数 min / 中位 / max | 49 / 49 / **646** | **646 / 646 / 646** |
| 属于「孤岛」（只有 49 条入链） | **39 / 45 页** | **0 / 45 页** |

根因：`partials/footer.html` 里**写死的 6 组「Popular matchups」**出现在**每一页**页脚 ⇒ 那 6 个页各拿 646 条入链、其余 39 个只从兄弟页拿 49 条。sitemap 声明过（= Discovered）但站内几乎无路可达（= 优先级/信号不足）—— 与 GSC 的提示**逐字对应**。
**修复**：页脚改为**上下文相关**（对决页 → 同品牌的其他对决；品牌页 → 该品牌的对决；其他页 → 兜底 6 组），复用与导航同一个真源 `nav-matchups.html`；`{{ .RelPermalink }}` 排除自身。
**未动（改造前已达标）**：title 45/45 唯一、H1 45/45 唯一、self-canonical 正确、无 `robots` meta（可索引）、hreflang 3 条。

### ⑨ 新增两道**构建前**闸门（本轮撞了两次「改文案 → 等 11 分钟 → 末端才报错」）

一次全量构建 ≈ 11–12 分钟；按项目既有纪律「判据必须前移到源码/数据层」，把两条判据前移进 `npm run validate`（秒级）。

**`scripts/check_printf_arity.py` —— i18n 调用契约**。事故：本轮在 matchups 的 FAQ 里写了 `printf (i18n "…") $total`，而该 i18n 值**一个 `%` 占位符都没有** ⇒ Go 把多余实参印成 `%!(EXTRA int=45)` **到读者页面上**（4 页）。格式串住在 `i18n/*.toml`、实参个数住在 `layouts/**` —— 这条**跨文件契约此前无人守**。
判据：① 动词数必须等于实参数；② 值里有非格式动词的裸 `%`（如 `20% off` 被当格式串）报错；③ `i18n "K" (dict …)` 必须覆盖**该 key 各语言占位符的并集**，否则印 `<no value>`；④ **各语言占位符集合互不相同不报**（德语要 `country_acc`/`country_dat`，是刻意设计）。
**校准教训**：第一版把「多传 dict 键」一律判为漂移 ⇒ 在 `provider.html` **误报 160 处**（全是德语格变化的按需供给）。改成「任何语言都没用到才算冗余」后降到 55 处真冗余（非阻塞 WARN）。**守卫必须先用真实仓库校准边界**。
自检：正例 10 / 硬反例 9 / 软反例 2 = **21 项两侧都证**；正式扫描 **ERR 0 / WARN 55**。

**`scripts/check_headings_source.py` —— h2/h3 标点（构建前）**。事故：本轮新加的一条**德语 H2 带逗号**，跑满一次构建才在 `check_headings.py` 报 `bad: 45`。
判据从 `scripts/lang_rules.py` 读**同一份**语言规则（**不抄第二份正则**）：en 禁 `, ; : — –`、de 禁 `, ; :`；来源三处 —— `<h2>/<h3>` 内的 i18n key、`$xH2 = i18n "…"` 的**间接赋值形态**、`content/{lang}/**/*.md` 标题。
**边界写进 docstring**：值里 `{{ .x }}` 代入后才出现的标点、数据层国名带进来的标点本脚本看不见 ⇒ **产物级 `check_headings.py` 必须保留**。
自检 5 项全过；正式扫描 **0 处违规**（与产物级 `bad: 0` 一致）。

### ⑩ 验收（全部现算；`.buildlog/build_r78e.log` EXIT=0、12 项产物闸门全绿）

- `stamp` 报「无改动：数据没变，日期保持不动」；`build:css` OK；`validate` **0 error**；hugo `Total in 416976 ms`。
- `check_headings`：`checked 1291 html files, 33248 h2/h3, **bad: 0**`。
- **产物断言 `.buildlog/p78_assert.py`（10 条）：合计问题 0**，含一条**跨源对账** `Σ(赢+输+平)=4482 = 2 × 2241 行 ✓`（战绩榜 ↔ 45 张对决页行数合计）。
- **断言自检 `--selftest`**：正例 0 误伤；**逐条反例隔离注入**（每条独立还原后重跑，避免多条反例互相掩盖）。
- **同质度双口径** / **厚度与内链**：见上表。
- 回归基线：`generated_at` 09:02:32Z → **10:57:47Z**；1291 文件、13 类页型**完全相同**；`--diff` → **变更 0 / 新增 0 / 删除 0**。

### ⑪ 本轮踩到并已写进纪律的坑（详见 `docs/compare-ux-seo-2026-10-10.md §4`）

1. **「一句话」只能有一个句号**：把段落前半句做成数字驱动、留后半句静态 ⇒ 后半句仍是一条 45× 复制句（探针按句末标点切句）。**本轮栽了两次。**
2. **改文案前先预测分散度**，别用构建试错：`.buildlog/p78_sentence_variance.py` 从**当前产物转录**数字（不重算 vs-agg），比较候选变量集后一次改对。实测 `(metered,unlim,total)` 只 10 种组合、最大重复 15 页；加 `$lo` 后最大重复降到 6 页。
3. **断言脚本的反例必须真注入到判据所在位置**：⑦ 删徽章删到了别的模块（MISS）、⑩ 正则缺 `(?s)` 导致反例根本未生效（靠 `assert t2 != orig` 才暴露）。
4. **量纲不能混**：战绩榜「对战数」是场次、赢/输/平是国家数之和 ⇒ 正确不变量是「Σ赢=Σ输」「Σ平为偶」「Σ对战数=2×场次」+ 跨源对账。
5. **Python 非 raw 字符串里的 `\$` 非法**：`SyntaxWarning` 后原样写进 TOML ⇒ `validate` 直接报「无法解析的 TOML 值」。
6. **`@esimsift` selftest 会复制整棵产物树 + 逐条全树扫描**，别与全量构建并行（互相拖慢、快照可能不完整）。

### 未动但登记在案

- **改动全部留在工作区，未 `git commit`、未部署**（含 623 条已暂存的删除）。
- `.buildlog/` 仍在仓库目录内（已忽略、跟踪数 0）；若要物理搬出仓库根，需一并改脚本相对路径。
- `scripts/_*.py` 里约 50 个一次性补丁/对账脚本会被提交；其中 `_de_schema_audit.py`、`_de_link_leak_audit.py` 是**构建闸门不能动**，其余可归档到 `docs/internal/scratch/`。
- 残留 10 条模板说明句 / FAQ 答案可继续数据化（收益递减）。
- 第七十七轮遗留全部仍在：`/de/catalog.json` 的 `plan` 9095 条与英语逐字相同（O1）· 146 页 JSON-LD 缺 `inLanguage` · sitemap 无 `xhtml:link` · `de/404.html` 段落硬编码 · 全站无 RSS 自动发现 `<link>` · 国家页选中天数后只隐藏不重排。
- **德语译文尚未经有资质审校**（本轮新增两句已避开「介词支配国名」的与格陷阱）。



**触发**（用户点名 4 问）：① `/de/compare/united-states/` 的 `✓ Preise geprüft am 07.10.2026` 是否该改成当天？② `/de/networks/germany/` 同问（理由：新语言未上架）；③ 国家比较页「选 3GB 会把所有 >3GB 的都显示出来」，过滤该怎么设计、是否改渲染文件；④ `/de/compare/matchups/` 品牌对比是否该像国家页那样「鼠标放上去就展开」。
**用户拍板**：③ → **加按 GB 选择的过滤**；④ → **`<details>` 可展开对比表**。
**思路**：①② 只实测 + 论证，**不改任何日期**；③④ 改两个渲染文件（en/de 共用）+ i18n + CSS；另做一件必做收尾 —— 把 `--diff` 报出的 **1290 页变更**归因清楚再刷基线。

### ① ② 日期口径：**不改**（页面日期 = **数据核对日**，不是构建日）

`partials/country-stats.html` 取该国所有品牌 `[ISO].checked` 的**最大值**，同一日期喂三处：可见文案 / JSON-LD `dateModified` / sitemap `<lastmod>`。
- US / DE 实测：8 家 = `2026-09-30`，**jetpac + nomad = 2026-10-07** → max = **2026-10-07** = 页面显示值。
- `python -X utf8 scripts/stamp_checked.py --check` → **EXIT=0**「OK：日期与数据一致（499 价格单元 + 10 档案单元，今天 2026-10-10）」⇒ 07.10 是**真话**。
- `/de/networks/germany/` 同源（`networks/single.html:34` 的 `$s.checkedDate` → 徽章 `:120` / 计数脚注 `:195` / 侧栏脚注 `:416`）；其「运营商归属」来自同一数据块 `[ISO].networks` ⇒ **自洽**。
- **改今天的代价**：① 「今天核过价」是**不实陈述**；② `lastmod` 每次部署翻新 → Google 判无信息量 → **整体忽略**（第二十三轮试过 `now` 又撤回）；③ 一旦被判定不可信，真更新也不加分。
- **德语层未部署 ⇒ Google 从没见过 07.10 ⇒ 不存在「陈旧」问题。** 要「看起来新」的唯一诚实路径：`python -X utf8 scripts/bump_checked.py --brand X --countries US,DE`（真重核 → 指纹变 → 自动盖当天）。

### ③ 数据量区间过滤（`layouts/compare/single.html`）

**先纠一个误判**：这页原本**没有 GB 过滤** —— `3+/10+` 那两组是 `Reisedauer`（**天**）。用户描述的「超集」现象**真实存在**，只是发生在天数上（US 254 行实测：`3+ Tage`→剩 241，其中**恰好 3 天的只有 17 条**；`≥3GB`→232；`≥10GB`→184）。
**★ 设计铁律**：**天数 = 覆盖型需求 → `≥` 正确**（去 3 天，30 天套餐也满足）；**数据量 = 预算型需求 → `≥` 错误，必须区间**（用户只为 3GB 付费，不该看到 20GB）。
- 7 档桶：`Unbegrenzt`（`gb === 0`）/ `≤1` / `1–3` / `3–5` / `5–10` / `10–20` / `20+`；边界**左开右闭**（`gb > lo && gb <= hi`），**`gb === 0` 只进 `u`、不泄漏进 `0-1`**。
- **空桶不渲染**（`{{ if gt (index $szCnt "x") 0 }}`）—— 某国没该档位就不给按钮，避免点出空结果。
- 桶计数由**数据推导**、文案**服务端渲染整句**（JS 只做筛选，不拼句子）；纯客户端 JS，254 行全文服务端渲染 ⇒ **对 SEO 零风险**。
- 文件：81371 → 85087 bytes（1134 → 1183 行）。

### ④ matchups `<details>`（`layouts/compare/matchups.html`）

**为什么不是 hover**：① **移动端无 hover**（一半流量）；② hover 内 JS 动态插入的内容 **Google 可能读不到**；③ `<details>/<summary>` **零 JS、可键盘、可索引、移动端天然可用**。
现状佐证：**全站 70 处 `group-hover` 全是颜色/透明度，无一处展开内容** —— 没有可抄的既有范式。
- 卡片由 `<a class="card">` 拆成 **`<div>` wrapper + 大块可点 `<a>` + `<details>` 兄弟节点**（**interactive content 不能嵌在 `<a>` 里**）。
- 展开内容 = 价差最大的 **5 国** `A $X vs B $Y`（取自 `partials/vs-agg.html` 已有的 `aMin/bMin`）+ 一行汇总说明；复用既有 `.faq-icon`（旋转 45° 加号）。
- 文件：8025 → 10471 bytes（89 → 125 行）；`i18n` 各 **+10 key → 1789**（en = de 逐 key 同序，差集空）；`main.css` +581 bytes（`.matchup-more`）。

### ⑤ 验收（全部现算，`npm run build` EXIT=0、**12 项闸门全绿**）

- 德语 US 页新控件 en/de 对称：`Jede Größe / ≤ 1 GB / 1–3 / 3–5 / 5–10 / 10–20 / 20+ GB / Unbegrenzt` ↔ `Any size / … / 20+ GB / Unlimited`。
- **空桶省略（真反例）**：隔离探针工程 `.buildlog/szprobe/**`（fixture `gb = 0/0.4883/2/4/8/30`，**故意让 `10–20` 空**）→ 渲染桶 `['any','0-1','1-3','3-5','5-10','20p','u']`，**`10–20` 被省、其余 7 个在** ✓
- **全 50 国**：渲染桶集合 == 有货桶集合，**不一致页数 = 0**。
- **JS 区间语义**（node 从模板抽 `szMatch` 真源）：**12/12 全过**；**分区性** 16 个样本各**恰好落进 1 桶**、违规 **0**（含 `gb=0`）。
- **matchups**：`matchup-more` 只在 **en hub + de hub 2 个文件**（`layouts/compare/matchups.html` 就是 hub 模板）；DE/EN 各 **45 个 `<details>`**、每块 **5 国 × 3 列**。样例（DE）：`Land für Land vergleichen` / `Günstigster Tarif je Land: Airalo gegen aloSIM` / `Kanada | $7.00 | $3.50`。
- 德语守卫全过：`verify_de_text`（644 页）/ `verify_de_data`（i18n **1789 值** + `data/de` 1556 串）/ `check_hreflang`（1291 pages / 3864 tags）/ `_de_schema_audit` [4] **0 处 0 页** / `_de_link_leak_audit` [1][2][3] 全 **0**。
- **守卫只读性专项**：12 项守卫的写入**只落 `tempfile.TemporaryDirectory()` 夹具或 `docs/regression-manifest.json`（仅 `--write-manifest`）** ⇒ **无一处写 `public/`**。

### ⑥ 1290 页 diff 归因（本轮最大工作量，方法论见红线 91）

**现象**：`--diff` 报 **1290 / 1291 页变更**（新增 0 / 删除 0），与「上一轮英语侧 0 变更」矛盾。
**三条排除**：CSS 无内联（`grep "<style" public --include=*.html` = **0**，产物是**外链无指纹**的 `<link rel=stylesheet>`）· 无构建日注入（`stamp` 报「无改动」、全站含 `2026-10-10` 的 HTML = 0）· **渲染确定**（`hugo -d .buildlog/_det` 与 `public/` 逐字节比对：**1889 文件 identical 1889 / differing 0**）。
**真因**：基线写在 **14:29:19**，而 **15:15:17** 有一批改动落盘 —— `partials/{breadcrumbs,header,footer,schema}.html` + `compare/{provider,vs-single}.html` + `esim-providers/single.html` + `index.html`；**这些全局 partial 被每个页面引用 ⇒ 改一处全站皆变**。另 15:18:33 `guides/region.html`、15:35:09 `index.llms.txt` + research 两页。
**★ 自洽锚点**：全站唯一**未变**页 = `en/index.html`（`alias_shell`，270 bytes 裸跳转壳，**无 `partial` / `<header` / `<footer` / `og:site_name`**）⇒ 结构上天然免疫。**1291 − 1 = 1290，精确等于报告数。**
**结论：不是功能回归，是上一轮合法改动未折进基线。**

### ⑦ 基线刷新

`_det`（与 `public/` 逐字节相同）保留为 `.buildlog/pub_d77`（375M，供后续恒等证明；此前**从未存在** `pub_d77`，未误删）。
`python -X utf8 scripts/verify_no_regression.py --write-manifest` → **EXIT=0**，检查 A / B / C 全过。
`generated_at` **06:29:19Z → 09:02:32Z**；文件数 **1291 → 1291**；**`class_counts` 13 类完全相同**（仅内容更新、**结构零变化**）。
`--diff` → **变更 0 / 新增 0 / 删除 0**、「与基线完全一致（1291 页逐字节相同）」✓

### 未动但登记在案

上一轮遗留全部仍在：`/de/catalog.json` 的 `plan` 9095 条与英语逐字相同（O1）· 146 页 JSON-LD 缺 `inLanguage`（两语对称）· sitemap 无 `xhtml:link`（两语对称）· `de/404.html` 段落硬编码 · **全站无 RSS 自动发现 `<link>`** · 国家页选中天数后**只隐藏不重排**（品牌页已做「可覆盖置前」，国家页未对齐 → 本轮只加 GB 过滤，未动重排）。
**仍未 `git commit`、未部署**（工作区改动累积）。

## 已完成（德语上线前第二轮：多语言内链泄漏清零 + 两条产物级守卫入闸，2026-10-10 第七十五轮 · d51）

**触发**（用户点名）：「德语译文未经人工审校这条忽略；**其他的是否都是德语的？是否能正式上线德语的，以及德语技术 SEO 是否还存在问题**」。
**思路**：不加新页型、不改数据层，只做「产物级实测 → 手术式修复 → 守卫入闸」。
**交付文档**：`esimsift-德语上线前技术收尾-2026-10-10.md` §7–§8（数字全部现算）。

### ① 根因：`.Site.BaseURL` 与 `absURL` 在多语言站都解析到「默认语言根」

`hugo.toml` 是 `defaultContentLanguageInSubdir = false` + 顶层 `baseURL`、**无 per-language baseURL**
⇒ 德语页里 `.Site.BaseURL` / `absURL "x/"` 全部产出 `https://www.esimsift.com/x/`。**4 处独立缺陷 / 13 个模板文件**：
① JSON-LD 面包屑 `item` **1643 处 / 645 页**；② 可见面包屑「回首页」+ header/footer logo **645 页**；
③ `/de/llms.txt` **68 处**英语根内链（`index.llms.txt` 15 处 `absURL`）；④ 德语 research 页指向
`catalog.json` 的 **2 处**（而 `/de/catalog.json` 确实存在，3.03 MB、`notes` 已是德语）。
★ 正解分两类：**Page 路径**用 `.Site.Home.Permalink`（英语下与 `.Site.BaseURL` 逐字节等价）或
`partial "lang-href.html"`；**非 Page 的生成文件**（catalog.json / llms.txt / RSS）`lang-href` 兜不住
（`site.GetPage` 找不到 ⇒ 退回 `relURL` ⇒ 仍指英语根），**必须 `absLangURL`**。
★ **故意保留 `.Site.BaseURL` 的 10 处**（组织身份 5 / 图片资源 2 / robots 站点级 sitemap 2 / catalog url 1）。**详见红线 90**。

### ② 畸形转义：`i18n/de.toml` 17 条值写成三层转义 `\\\"`

产物里落成 `href=\"/methodology/\"`（带**字面反斜杠** ⇒ 链接点不动）**96 处 / 11 页**（英语侧 0 处）。
34 处 `\\\"` → `\"`；同时给 13 处内部 href 补 `/de/` 前缀。key 数仍 **1779**（en = de 逐 key 同序对齐，0 差集），纯 LF 守恒。

### ③ 两条产物级守卫**新接入** `check:output`（10 → 12 项）

- `scripts/_de_schema_audit.py` —— **它第七十三轮就写出来了，但从未进流水线**（「有守卫」≠「守卫在跑」）。
  本轮收紧判据 [4]：补 `/de`（**无尾斜杠**，面包屑首页项经 `TrimSuffix "/"`）这条**临界边界** ——
  不补的话「模板改对了、守卫反而报 645 页假红」；加**组织身份豁免**（`Organization`/`WebSite` 的 `url`/`@id`，
  实测 1815 处）且**只豁免身份键**（同宿主的 `publishingPrinciples` 仍须 `/de/`，防过度豁免）。
- `scripts/_de_link_leak_audit.py`（**新建**）—— [1] HTML `<a href>` 全形态（双/单/无引号）+ 自有域名**绝对写法** +
  语言切换器豁免 + 先挖 `<script>`/`<style>`；[2] 畸形反斜杠 href；[3] **非 HTML 产物**（`.txt`/`.json`/`.xml`）语言泄漏
  （红线 88：首版只扫 `*.html`，`/de/llms.txt` 的 68 处整片漏掉）。
- `--selftest`：**13/13** + **16/16**（正例、逐条反例、边界两侧都证；[3] 对**改造前产物**实测判红 2 处 + 68 处）。

### ④ 验收（全部现算，`npm run build` EXIT=0、12 项闸门全绿）

- **英语侧逐字节恒等**：1889 文件 **0 增 0 删**、变更 **646 条全部落在德语侧**、**英语侧变更 = 0**
  —— 硬证 `.Site.Home.Permalink ≡ .Site.BaseURL`、`absLangURL ≡ absURL` 在默认语言下等价。
- 德语侧泄漏 **1643 / 96 / 93 / 68 → 全部 0**；`/de/llms.txt` **143 处**自有域名 URL 全带 `/de/`。
- 德语 SEO 面：`<html lang="de">` **645/645**、canonical 自指 **645/645**、robots `noindex` **0**、
  `og:locale de_DE` **645/645**、`/de/sitemap.xml` **644 条全 `/de/`**、`robots.txt` 声明两个 sitemap、
  `/de/index.xml` language `de-de` 且 **637/637** link 指 `/de/`。

### ⑤ 未动但登记在案（需用户决策）

`/de/catalog.json` 的 `plan` 字段 **9095 条与英语侧逐条相同**（`Unlimited` 4038 条），
而德语 HTML 印的是 `Unbegrenzt`（265 处）— 同一事实两套渲染（O1，机器导出 vs 读者可见的口径取舍）。
`/de/sitemap.xml` 无 `xhtml:link` alternate（英语侧同样 0，两语对称）；JSON-LD `inLanguage` 缺 **146 页**（两语对称）；
RSS `<title>` 尾巴 `on eSIMSift` 两语相同；`de/404.html` 段落硬编码；**全站无 RSS 自动发现 `<link rel="alternate" type="application/rss+xml">`**。

## 已完成（英语 compare 正文现算口径 + 德语上线前技术收尾，2026-10-10 第七十四轮 · d49/d50）

**本轮目标**（用户点名）：① 按现算口径重写英语 compare 正文数字（消掉自相矛盾）；
② 德语上线前的技术收尾 —— `llms.txt` 德语化 / 结构化数据抽查 / 首屏性能。
**交付文档**：`esimsift-德语上线前技术收尾-2026-10-10.md`（§0–§6，全部数字现算）。

### ① 英语 compare 正文（红线 84 已修）

49/50 页重写，**`japan` 逐字节未变**。真实变更 **98 行 / 305 token** = 品牌名归一 147 + 数字与计量 152 + 其它 6。
`--verify` 0 处过期、`--dry` 幂等 0 处、`content/en/compare` **52/52 仍纯 CRLF**。
★ 纪律：**只换槽位，绝不重写句式**（50 套独立手写句式是反同质化资产）；
★ **`626` 是正则匹配次数不是「变化处数」**（`sub_group()` 对每个匹配 +1，含幂等命中）。

### ② `/de/llms.txt` 德语化

44 个 `llms__*` key + 19 条字面替换；英语字节由**结构等价证明**（`flatten()` 逐占位符回填原表达式）保证。
`check_i18n` 拼装句碎片 **49 → 14**（该文件 35 处全消）。

### ③ 结构化数据抽查 —— 4 个真缺陷已修

`publishingPrinciples` 指向英语 `/methodology/`（**645 页**）；JSON-LD 面包屑硬编码 `Home`（645 页）与
`Compare countries`（499 页）；`esim-providers/single.html` 4 条 `additionalProperty.name`（10 页）。
判据 `scripts/_de_schema_audit.py` 五条硬判据全绿；**4 个假红源**写进 docstring（**红线 87**）。

### ④ 首屏性能抽查 —— 1 个真缺陷已修

首页 hero（373 KB）被**全站无条件 preload**，而它只有 `layouts/index.html:57` 一处渲染 ⇒ **1288 页白预加载**。
改为 `{{- if .IsHome }}…{{- end }}`，用**最小 Hugo 探针站**证明「首页逐字节相同 + 子页恰好少那一行」。
判据 `scripts/_perf_audit.py`。**P1/P2/P3 登记待决策**（`/tools/` 1.16 MB 内联脚本 /
**1290 页无 `<head>`** / CSS `@import` 串行阻塞）。

### ⑤ ★ 非 HTML 德语产物 —— 判据 G 的扫描面本身漏了一整类产物（**红线 88**）

F/G/J 都只枚举 `glob("**/index.html")` ⇒ `/de/llms.txt`、`/de/catalog.json`、RSS `*.xml`、`sitemap.xml`
**一条都扫不到**。实测抓到 3 个缺陷（**十项闸门当时全绿**）：

| # | 缺陷 |
|---|---|
| D5 | `/de/llms.txt` **10 条 `promo_label` 是英文**（★ 本轮引入）：它在 `data/de/strings.toml`（走 `de-text`），**不在** `data/de/providers.toml` —— 同一行相邻的 `tagline` 却走深合并 |
| D6 | `promo_expires` 为空时印 `, expires )` / `, gültig bis )`（**9/10 品牌**）；站点既有惯例是 `esim-providers/single.html:466` 的 `with/else` |
| D7 | `/de/catalog.json` 的 `fairUse` 漏 de-text（**2271 条** `fup_note`）+ `notes` 是**两语都硬编码**的模板字面量 |

**守卫改造**：① 先换实现 —— 逐串带回溯正则 **33 s → `str.find` 0.3 s**（644 个 HTML 页 **256 s → 8.3 s**），
且**逐页比对命中集合完全一致**；② 扫描面扩到 `.txt/.json/.xml` + `_json_text()` 还原 `jsonify` 的 `\uXXXX` 转义；
③ **先对新守卫跑改造前的旧产物**：`24 处问题 / EXIT=1`；④ 补 7 条正/反例。
**构建提速：15m26s → 9m02s。**

### ⑥ 验收（d50，`EXIT=0` 十项全绿）

`I 德语单位统一（i18n **1779** 值）` · `F（644 页）` · `J（644 页）` ·
**`G 全站德语产物无数据层英文残留（644 页 + 11 个非 HTML 文件 × 185 条，含 JSON-LD）`** ·
`check_hreflang 3864 tags / 1288 页` · `check_output 1291 pages / 7412 JSON-LD blocks`。

`--diff` 与 d49 **逐类计数完全相同**（变更 1289 / 新增 0 / 删除 0 / 非品牌子页 291）⇒ 未引入额外 HTML 变更。
字节断言：`public/catalog.json` **逐字节不变**；`public/de/catalog.json` 只变 `notes` + 2271 条 `fairUse`；
`public/llms.txt` 只变 9 行（全是删 `, expires )`）；`public/de/llms.txt` 促销句全德语、残留 0。

### ⑦ 待决策（9 项，本轮未改）

**性能**：P1 `/tools/` 1.16 MB 内联脚本 · P2 1290 页无 `<head>` · P3 CSS `@import` 串行阻塞。
**结构化数据**：E1 146 页缺 `inLanguage` 且两语不对称 · E4 JSON-LD 与可见标签口径差。
（E3 已在 ⑧ 顺带修好。）**其它**：O1 `/de/catalog.json` 的 `"plan"` 未过 `plan-name.html`（两语 9,095 条同形，
而德语 HTML 显示 `Unbegrenzt`）。
**欠账**：第五十二轮起改动**全部未 `git commit`、未部署**；德语译文**尚未经有资质审校**。

### ⑧ 顺带修好的既有英语缺陷（诚实登记）

45 个英语 `compare/*-vs-*` 页改字节：JSON-LD 面包屑第 2 级换成 `(i18n "g_compare_countries")`（英语值即
`Compare countries`，本意零变化），暴露出**可见面包屑第 2 级原本用国家页 title 口径**（`All eSIM providers`）
⇒ 原有的 JSON-LD/可见层矛盾被顺带修好。**是修复，不是回归。**

### ⑨ 同轮发现的失效守卫

`scripts/_llms_de_l10n.py`（**不在 build 流水线里**）的 `--selftest` 早就红着：迁移落盘后 `old == new`，
而 `audit(old, new, env)` 两侧**共用同一个 `env`** ⇒ 反例**结构上失效**。已修（反例自带基线 + `--dry` 幂等）。
★ **不在流水线里的守卫必须定期手跑 `--selftest`。**

### ⑩ 交付后复核：英语 compare 对账器**假红 13 处**（**红线 89**）

`scripts/_en_compare_stale_audit.py`（只读对账器）报 **13 处过期**（12 页 `entry_gb` + `fiji` 的 `tech`），
而 `scripts/_en_compare_fix.py --verify` 报 **0 处** —— 两个工具对同一批 50 页结论**相反**。
逐条把命中位置打印出上下文句子后确认 **13 处全是假红**，根因是该对账器**内联抄了第二份抽取正则**：

- 抄漏 `RE_ENTRY` 的 `(?! a day)` 负断言 ⇒ 12 页的**盈亏平衡句**（`…only makes sense past about 3.6GB a day`）
  被当成入口档位，拿去比 `entry_at_rate_mb / 1024`（且用 `re.search` 只取首个匹配，而非 `finditer`）；
- `tech` 分支只写 `all 5G` / `mix` 两种，**缺 `{4G} → all 4G`** ⇒ `fiji` 正确的 `all 4G` 被判红
  （而 `_en_compare_lib.py :: tech_phrase()` 的注释里**早已写下这同一个教训**）；
- 未共用改写器的 `SKIP` 例外集 ⇒ `japan`（编辑性长文）的 `$3.90 per day flat`（日价）被当成 `entry_price`。

**产物一个字没错**，错的是核对工具。已改为**委托** `_en_compare_fix.collect_stale`（单一真源，连 `SKIP` 一起），
例外页在报告里**显式列出**，并补 `--selftest`。
验收：`--selftest` **8 / 8**（正例 4 + 反例 2 + 边界 2，两侧都证）；隔离目录端到端注入 —— 正例 **0 判红** /
反例（仅把入口 GB 改成 `9.9`）**恰好判 `['entry_gb']`**；改造前 → 后 **13 处假红 → 0 处**（`EXIT 1 → 0`），
与 `--verify` 结论一致；`scripts/_en_compare_stale_audit.py` 改后仍**纯 LF**。


## 已完成（德语 D7 页面生成 + lang-href 语言降级修复，2026-10-09 第六十五轮）

**本轮目标**：把「德语站能否正式发布」从「i18n 覆盖率」推进到**产物级自洽**。

### ① D7 页面批量生成（+564 个德语页）

| 批 | 数量 | 做法 | 说明 |
|:--|--:|:--|:--|
| 品牌×国家子页 | **499** | `gen_provider_pages.py --lang de` | 改为多语言；**指标计算只有一份实现** `metrics()`，两种语言共用 |
| A-vs-B 对决页 | **45** | `gen_vs_pages.py --lang de` | 新增德语 title 候选 7 种**按索引轮换**；英文侧永不写盘（45 页全 skip） |
| 品牌 Hub | **10** | 手写 | 句式刻意不统一（`im Test` / `eSIM-Test 2026` / `Test: …`）|
| 栏目页 | **3** | 手写 | `esim-providers` / `esim-deals` / `tools` 的 `_index.md` |
| `compare/matchups.md` | **1** | 手写 | 页头与页脚都链它 |
| 根页 | **6** | 手写（D8 提前做）| about / contact / disclosure / methodology / privacy / terms |

- 换行符**显式写死**：英文侧历史文件是 CRLF、德语侧全是 LF，`write_text(newline=…)` 必须按语言分支（否则「零内容差异却全文重写」）。
- **恒等判据**：`gen_provider_pages.py --lang en` 重跑后 499 个英文 md **逐字节不变**（sha256 0/0/0）。
- 德语 desc 长度区间另设（品牌子页 **142–165 字符**；英语是 120–140）—— 德语词更长，硬套英文上限会全部越界。

### ② ★ 发现并修掉 `href` 的**语言降级**（18 处 / 6 个模板）
裸 `href="{{ printf "/…" }}"` 不过 `lang-href` ⇒ 德语页写出英文路径。**不 404**，所以死链检查全绿。详见 PROJECT.md 红线 77/78。判据已进 `check_i18n.py` 第 6 项（`raw_lang_href()`，正例 6 / 反例 3）。

### ③ 新审计装置：产物级死链 + 语言降级
`.buildlog/audit_de_links.py --lang de` —— **死链 0**（555 页 × 90062 条站内链接）；**语言降级按目标聚合**（排除语言切换器 `<a hreflang=…>`）→ 这是 D8 的精确待办清单。

### ④ 验收
- `npm run build` d30：**EXIT=0**，`1201 页`（en 646 + de 555），守卫 A–H 全绿；`G 全站德语页无数据层英文残留（554 页 × 144 条数据串，含 JSON-LD）`。
- 499 个德语子页落地后**英文侧产物不变**（德语译文 noindex ⇒ `head.html` 不发 hreflang ⇒ 英文页一条都不变）。
- 构建前判据前移：`.buildlog/audit_head_keys.py` 扩到扫 `content/de/**/*.md` **正文** h2/h3 —— 首跑抓到 1 处（`disclosure.md` 的德语从句逗号），已换句式。

### ⑤ 副作用
全量构建 **3 分钟 → 11.5 分钟**（+499 页 + 守卫扫 555 页）。

### 待办（D8/D9）
- **D8 手写长文**：`guides` 10 篇（`how-to-install-esim` 被 549 页链接）、`networks` 12、`research` 5、`tools`/`esim-deals` 正文
- **`privacy` / `terms` 的法律审校**（英文侧 `# TODO(launch)` 仍在 —— **代码侧做不了**）
- **D9**：解除 620 个德语页的 `noindex` + `/de/sitemap.xml` + `robots.txt` + `head.html` 的 `x-default`

## 已完成（德语 D7 前置 · policy 数据链收口 + 判据 G/H，2026-10-09 第六十四轮）

**目标**：D7（499 品牌子页 / 45 vs 页 / 10 品牌 Hub）**全部前置**收口 —— 页型还没建，先把「数据怎么本地化、怎么判」钉死。

### 一、四条判据的分工（本轮核心产出）

| 判据 | 性质 | 清单来源 | 覆盖 |
|:--|:--|:--|:--|
| E1–E5 | 页内 | 结构词 / 国名 / 数据串原文 / 散文 | 仅 `/de/compare/<国家>/` |
| **F** | **黑名单** | 23 条短语 + 8 个词（人写，大小写敏感） | 全站德语页 |
| **G** | **穷举** | `strings.toml` 里已有德语译文的英文原串 | 全站德语页 **+ JSON-LD** |
| **H** | **契约** | `provider.policy` 文本字段 vs `data/de/providers.toml` | 数据层（德语覆盖完整性） |

**G 首跑 24 处、F 全绿** —— F 的盲区实测：德语 `<title>` 的 `… Unlimited Data Plans`（清单写的是小写 `plans`）、policy 字段的 `3 GB/day on unlimited plans`（黑名单里恰好没有那些词）。修完 G → **0**（60 页 × 144 条数据串）。
**G 防误伤**：首跑在 `/de/networks/` 报 7 条假红 —— 全是德语**小数点逗号**（`65,1 Mbps` 含子串 `1 Mbps`）→ 加左边界 `(?<![\d.,])`；自测用**注入清单**验证该边界（不依赖真实数据演变）。

### 二、数据层四来源（`data/de/strings.toml`，144 条 / 36613 B / LF）

| 来源 | 条数 | 渲染点 |
|:--|--:|:--|
| `plans/*.toml` 的 `fup_note` | 14 | `compare/provider.html` / `compare/single.html` 的 `#fup` 表 |
| `providers.toml` 的 `promo_label` | 10 | `#providers` 促销句 |
| `providers.toml` 的 `info.support` / `info.refund` | 19 | 品牌 Hub `#support` + FAQ 答案（**本轮新增**）|
| `countries.toml` 的 `quirks` | 101 | `#quirks` 国家须知 |

生成器 `_gen_de_strings.py` 断言：无缺 / 无死条目 / 数字守恒 / **各来源键不得相交**（输出用 `or` 串联，相交会静默取错值）。

### 三、★ policy 字段：**不走 `strings.toml`**（判据 H）

`provider.policy` 的六个文本字段（`fup_note` / `hotspot_note` / `topup_note` / `fup_allowance` / `fup_drop` / `hotspot_allowance`）由 **`data/de/providers.toml` 深度覆盖**提供德语（实测 **10 品牌 × 6 字段 = 60/60 全覆盖**），模板读深合并后的 `$d.providers` ⇒ 德语站本就是德语。

- 本轮先误在 `strings.toml` 补了 **51 条** policy 译文，才发现覆盖层早已全覆盖 —— 两份口径**已经漂移**（`Sie`/`du`、`Mbps`/`Mbit/s`、`unbegrenzte Tarife`/`Unlimited-Tarife`）→ **删掉第二份**，改由 **判据 H** 断言覆盖完整。
- **H 首跑抓到 6 处**真问题：`fup_drop` 的德语值与英文**一字不差**（`1 Mbps` / `512 Kbps`，英语缩写）→ 修 `_gen_de_data.py`（新增幂等 `units()`，`Mbps→Mbit/s` / `Kbps→Kbit/s`），**不放宽判据**。
- 反之 `info.support/refund` 覆盖层**故意不写**（继承英语侧）⇒ 必须走 `de-text` + `strings.toml`。**同类字段的两半走两条链，依据是「覆盖层写不写它」。**

### 四、模板接线（20 处，全部走 `partial "de-text.html"`）

`compare/provider.html` 6→16 · `esim-providers/single.html` 5→12 · `faq-live-tokens.html` 0→2（`unl_allowance` / `unl_drop`，**国家页 FAQ 的 `{unl_drop}` 就靠它**）· `research/unlimited-esim.html` 0→1。
脚本 `_wire_policy_text.py`：字段名守恒断言（改前被裸插值的字段 == 改后 de-text 的入参）+ 裸插值归零 + dict 裸值归零；`--selftest` 7 项。

### 五、i18n 覆盖

**1693 key / 已译 1344 = 79.4%**（+0.3 点）。剩余 349 条 = D8 页型（`esim_deals_list` 112 / `tools_list` 48 / `research_*` 109 / `guides_single` 27 / `guides_region` 16）+ `compare_single` 17 + `g_*` 真同形 10 + `esim_providers_single` 白名单 5。

### 六、守卫自测

`verify_de_text.py --selftest` **38 项**（本轮 +8：D 段 info 两向 / H 缺键·未译·正例·枚举隔离 / G 素材·绕过 F·可见文本·JSON-LD·正例·小数点边界）。

### 待办（本轮发现，未做）

- `data/de/providers.toml` 的 **`Sie`-Form 未统一为 `du`**（全站其它德语是 du）；单位已统一，人称未统一 —— 需逐句改，风险高，单独一轮。
- 5 个**探针页**（`content/de/compare/germany/{airalo,holafly}.md`、`content/de/compare/airalo-vs-nomad.md`、`content/de/esim-providers/{airalo.md,_index.md}`）**验收完即删**。
- `scripts/verify_plan_names.py` 的 2 处过时引用（`plan-name.html` 注释）。



**触发**：本要收 D6 数据层尾账，先对**全部 55 个德语页**（不只 50 个国家页）做英文残留普查，
发现 `verify_de_text.py` 的 E1–E5 **盲区是「页型」不是「写法」** —— 只走 `/de/compare/<国家>/`，
德语站另外 5 类页（`/de/`、`/de/compare/` 索引、`/de/guides/`、`/de/networks/`、`/de/research/`）一条判据都没管。实测 3 页在漏。

**修掉 4 类真缺口（全部在模板层）**

| # | 位置 | 症状 | 修法 |
|:--|:--|:--|:--|
| 1 | `partials/aside-destinations.html:45` | 写死 `All {{ len $d.countries }} destinations →` → `/de/networks/` 印 `All 50 destinations →` | **复用**既有 key `partials_header__all_destinations`（同一句话只允许一份定义） |
| 2 | `compare/list.html:115` figcaption | 整句英文 `N real plans across M destinations — one table per country…` → `/de/compare/` 索引 | 新增 `compare_list__figcaption_plans_destinations` |
| 3 | `compare/list.html` 入门价榜 + FAQ | `$cheap*` 直接印 `plan.name` → 索引页 **11 处 `500MB / 1 Day`**，FAQ 又印一次 | 在**聚合处**过一次 `partials/plan-name.html` → 榜单与 FAQ 两处同时干净 |
| 4 | `research/list.html` | **9 句英文**（`prices checked` / `cheapest unlimited, $x/day` / `vs priciest` / `/GB avg` / `N countries · best x at $y/GB` / `Right now …` / `N unlimited plans audited…` / `Best daily rate right now…` / `Daily-rate rankings…`）→ 当时全站最差的德语页 | 10 个 `research_list__*` key（`printf "%d …"` 那条改成 `printf (i18n …)`） |

顺手把 `esim-providers/list.html` 的 3 处英文（`N countries · from $x` / `of N countries · best $/GB in` /
`Read the full <brand> review`）也抽了 key —— `/de/esim-providers/` 还没建，属**先修模板再建页**，
不修的话 D7 一生成就是英文页。⚠ `g_country` / `g_countries` **不可复用**（它们是 `Country` / `Countries`
表头，做表头用），这里要小写 `country` / `countries`（英文 byte 恒等要求）→ 另立两条小写 key；
⚠ `vs` 不新建 —— `g_vs` 早已存在（en `vs` / de `vs.`），新建就是重复定义。

**新增判据 F（`scripts/verify_de_text.py`）：全站德语页硬编码英文**

- 扫描面 = `public/de/**/index.html`（**新增页型自动纳入**）；清单 **23 条短语 + 8 个词**，每条在注释里
  写明「它是谁漏出来的」，源头修好后**保留当回归网**。
- 词表刻意与 E5 不同：**不收 `Plan`**（`Plan` 是德语词「ein Plan」，收了会造假红）。
- 改造前对**旧产物**独立取证（自测之外的第二种证据）：`EXIT=1`，命中 **23 处 / 3 页**
  （`de/research/` 17、`de/compare/` 索引 5、`de/networks/` 1），`May 2026` / `unlimited` / `Plan` **零误报**。
- 改造后：`F 全站德语页无硬编码英文（55 页 × 短语 23 条 + 词 8 条）`；`--selftest` **23 → 30 项**。
  ⚠ 自测断言只能比对「被判定的词」那一段：失败消息带 ±60 字上下文，会把相邻段落的 `May 2026`
  卷进「不误伤」类断言造成假红（本轮踩过一次，已改成 `split("：")[0]` 再断言）。

**同时修掉的日期机制缺陷（本轮开头，独立事件）**

`scripts/stamp_checked.py` 的日期单元段边界按「行物理位置」切 → 10 家的 `[<brand>.policy]` 表全堆在
文件末尾、排在最后一个顶层段 `[jetpac]` 之后 → 这 10 张表全被算进 jetpac 的段：实测给
`[holafly.policy]` 加一行 `fup_kind = "none"`，翻的是 **jetpac** 的档案核对日（`10-07 → 10-09`），
holafly 自己反而不翻。已改为 `parse_prov_blocks`（按品牌名归组、**段体允许多个不连续区间**）
+ `--resync` 迁移模式（重算全部指纹、**保留每个单元的现值日期**、不动任何 toml）；
`--selftest` 里写死的「450 价格单元 / 9 档案单元」随品牌接入腐烂已久 → 改**现算**（41 项全过）。
已复原 jetpac 的 `2026-10-07`。

**量化（全部现算）**

| 德语页型 | 本轮前 | 本轮后 |
|:--|--:|--:|
| `/de/compare/` 索引 | 94.9% | **100.0%**（德 276 / 英 0） |
| `/de/research/` | 73.7% | **98.3%**（英 31 → 2） |
| `/de/networks/` | 99.1% | **99.2%**（英 9 → 8） |
| `/de/` · `/de/guides/` · `/de/compare/*` 50 国 | 100% · 100% · 98.5% | 不变（本轮未动） |

全站剩余英文只剩三类，**都不是缺口**：`unlimited` 借词（995 处，统一策略仍未定）·
Opensignal 引文里的 `May 2026`（6 处，报告官方标识）· `Plan`（1 处，德语词本身）。
模板层拼装句碎片 **136 → 100**；`i18n` key **1649 → 1671**。

**恒等判据**：`--diff` = **变更 3 且全是德语页**（`de/compare/index.html` / `de/networks/index.html` /
`de/research/index.html`），**英文侧 0 变更**；刷新基线（702 个文件）后复验 `变更 0 / 新增 0 / 删除 0`、
**702 页逐字节相同**。

**本轮三条坑（都关于「产物字节」，全部实测；详见 `docs/de-l10n-plan.md` §10.17）**

1. **新增一个「独立的注释动作块」会改变产物字节** —— 注释本身不输出，但它前后的**换行与缩进是字面文本**。
   首轮构建 `--diff` 报 **22 处（含 18 个英文页！）**，全是纯空白差异 → 说明一律**并进既有注释块**。
2. **模板头部（第一个输出型标签之前）多插一行 = 多一个换行** —— `compare/list.html` 聚合层在页头
   `<div>` 之前，加一行 `{{ $iso := . }}` 就让**英文**索引页变了一个字节 → 能用作用域里的 `.` 就别新开变量。
3. **注释块里不许出现「成对花括号」** —— `i18n_extract.scan()` 只把 `<!-- -->` 当注释，`{{/* */}}` 不是；
   注释里写 `{{ partial … }}` 会被当**动作边界**，紧随其后的说明文字被判成「模板层硬编码文案」，
   `check_i18n.py` 直接报 **ERROR**、构建 exit 1（与「模板注释里的 i18n 调用会被渲染」同源，这次是**守卫**侧的表现）。

**★ 本轮最重要的结论：D7/D8 的真正前置不是页面，而是 `i18n/de.toml`**

`scripts/i18n_coverage.py de` 现算：**1671 key，已译 1054 = 63.1%，仍有 617 条英文占位**。
未译量按前缀分布（即「哪些页型还不存在」）：`esim_providers_single` 124 · `compare_provider` **112** ·
`esim_deals_list` 112 · `tools_list` 48 · `research_*` 109 · `guides_single`/`guides_region` 27/16 ·
`compare_single` 17 · `compare_vs_single`/`compare_matchups` 17/15 · `g_*` 10 ·
`esim_providers_list` 7 · `networks_list` 2。

→ **先翻 D7 那几组（≈268 条），再跑 `content/de/` 生成脚本**；反过来的话，生成出来的
499 + 45 + 10 张德语页会是「德语 URL + 英文正文」。
→ 且 `layouts/compare/provider.html` 的**可见套餐名**（第 379 / 558 行）与 **JSON-LD `Offer.name`**（第 243 行）
仍是裸 `plan.name`，`.fup` / `.fup_note` / `$country.quirks` 也还没接 `de-text.html` ——
**这些必须在 D7 生成页面前补上**，否则 499 页立刻是英文。

**下一批（按依赖顺序）**

1. 翻 `compare_provider` / `compare_vs_single` / `compare_matchups` / `esim_providers_single` /
   `esim_providers_list`（≈268 条），验收 = `i18n_coverage.py de` 对应前缀未译归零 + `check_i18n.py` 全绿。
2. 补 `layouts/compare/provider.html` 四处本地化接线（套餐名 / `Offer.name` / `.fup` / `.quirks`）。
3. D7 生成 → D8 手写长文（`privacy` / `terms` 优先）→ D9 解 noindex + sitemap + robots + `x-default`。

## 已完成（德语 D6 数据层 · 三类英文句子全量本地化，2026-10-09 第六十二轮）

**背景**：第六十一轮把套餐名本地化后，`/de/compare/<country>/` 仍残留 **1,193 处**英文。排查发现成因是**两个互不相干**的问题。

**① 根因：`data/de/strings.toml` 多套了一层 `[strings]` 表头（静默失效）**
- `de-text.html` 读 `$d.strings`，而 `index hugo.Data "de"` 的 `strings` 键的值**就是该文件的内容本身** → 文件里再写 `[strings]` ⇒ `$d.strings` = `{strings:{…}}` ⇒ `index . $s` 永远落空 ⇒ **静默返回英文**（套餐名走 `$d.countries`，顶层本就是 ISO 键，所以那一批是好的）。
- 诊断：把 `i18n-data.html` + `de-text.html` + 数据原样拷进**多语言最小站**，探针打印 `hugo.Data` / `index hugo.Data "de"` / `$d.strings` 的键 → 150s 构建换成 50ms 迭代。
- 修法：`data/de/strings.toml` **顶层直接放句子键**；`_gen_de_strings.py` 的文件头警告 + `verify_de_text.py` 的读法同步。

**② 模板硬编码：相关国家卡片的锚文本（`layouts/compare/single.html:1012-1013`）**
- 三个轮换变体 `{Land} eSIM` / `eSIM for {Land}` / `{Land} eSIM prices` 是 `printf` 拼出来的英文片段（国名已德语、片段没有）。
- 修法：新增 3 个 i18n key（`compare_single__anchor_*`；de 用 `eSIM für {{ .country }}` / `eSIM-Preise`，基准取自既有 `compare_list__regions_head`），模板改整句 i18n，并用 `printf "%s"` 包一层**保持与原 `printf` 完全一致的 HTML 转义路径**。

**③ 数据层第三类：`quirks` 国家须知（101 条 / 50 国）**
- 接进同一张 `data/de/strings.toml`（一张「英文原串 → 德文」表覆盖三类），`single.html:698` 改 `{{ partial "de-text.html" . }}`。
- 生成器**不手抄英文键**：按 ISO 分组 + 组内同序 + 条数断言 + `set(德语数字) ⊆ set(英文数字)` → 一次跑出零错配。

**量化（现算；代理指标 = 德语独有词 /（德 + 英独有词））**

| 德语页型 | 占比 |
|:--|--:|
| `/de/`、`/de/guides/` | **100.0%** |
| `/de/compare/*` 50 国 | **97.1%**（125 条英文数据串残留 = **0**） |
| `/de/compare/` 索引 | 94.9% |
| `/de/research/` | 73.7% |
| `/de/networks/` | 60.9% |

**恒等**：`--diff` 变更 **50，全部是 `de/compare/*`**；新增 0 / 删除 0 → **英文侧逐字节未变**；基线刷新后复验 0/0/0，702 页逐字节相同。

**守卫**：`verify_de_text.py` D 段覆盖 125 条（fup 14 + promo 10 + quirks 101），`--selftest` **20 项**（新增 `D 德语映射命中（quirks）` 与 `反例：quirks 缺德语条目被抓住`）。

**D6 仍剩**：`data/networkreports.toml` 的 Ookla/Opensignal **归属引用**（`/de/networks/` 60.9%、`/de/research/` 73.7%）与 `data/carriers.toml` 的 `info.detail`（146 条）—— 约 300+ 条句子，属纯翻译工程，建议与德语审校一起排。详见 `docs/de-l10n-plan.md` §12.13。

## 已完成（德语 D6 数据层 · 套餐名本地化，2026-10-09 第六十一轮）

**背景**：上一批（第六十轮）把德语 i18n 面收口到「可执行项 = 0」，量出 `/de/compare/<country>/`
剩余英文的第二大块是套餐表里的 `data/plans/*.toml` 的 `name`（供应商原始产品名）。

**做了什么**：新增 `layouts/partials/plan-name.html`，**11 个渲染位点**（主表 ×2、FUP 表、TL;DR 三卡、
`#choose` 三条、`#bytrip` 两处、`#networks` 拟合句、JSON-LD ItemList）全部改走它。三层替换：

| 层 | 事实来源 |
|:--|:--|
| 目的地国名 | `data/countries.toml[iso].name` → `data/de/countries.toml[iso].name` |
| 非规范国名别名 | 新数据文件 `data/planaliases.toml`（CZ `Czech Republic` / TR `Turkey` / IE `Republic of Ireland`） |
| 结构词 | `i18n` 新增 `plan_name__*` **8 个 key**（`Unlimited Data` / `Unlimited` / `UNLIMITED` / `unlimited` / `Days` / `days` / `Day` / `Local`） |

**恒等**：`--diff` 变更 **50 = 全部 `de/compare/*`**，新增 0 / 删除 0 —— **英文侧零变更**。

**成效（绝对量）**：德语国家页套餐名单元格 **13,697** 个，本地化前 **11,820（86.3%）** 含英文结构词 → **0**；
全页德语功能词占比 **61.6% → 83.0%**（50 页汇总）。

**新守卫**：`scripts/verify_de_text.py`（A/B/C 源级 + E1–E6 产物级），`--selftest` 41 项；
（⚠ 订正：本条曾写作 `scripts/verify_plan_names.py` —— **该文件从来不存在**，引用前先 `ls`。）
对改造前的旧产物跑报 **17,780 处问题**（英语侧 0 误报），对修完的跑 **14,197 + 14,197** 个单元格零告警。

**零回归基线**：已刷为 **702 文件**，复验「0 变更、逐字节相同」。

⚠ **德语仍不能正式发布**：`/de/` 只有首页可索引，其余 54 页仍 `noindex, follow`；
`content/de/` 只有 55 个 index（**499 品牌子页 + 45 对决页 + 12 networks + 12 guides + 5 research 无德语内容**）。
**一旦解禁 noindex 就会暴露这些缺失** → 提交前必须先跑完 D9（解除 noindex + 德语 sitemap 入站）与 D7/D8（内容本地化），
或维持「只有 `/de/` 首页可索引」的分层发布状态。

## 已完成（关键词采集换 Google 官方通道，2026-10-08 第五十四轮）

**起因**：用户要求「关键词必须从谷歌搜索获取」—— 上一版（同日早）用的是 Bing 补全。

### 通道（本机网络事实，实测）
- 直连 `google.*` 全超时（`nslookup www.google.com` → `31.13.92.37`，**DNS 污染**）
- 环境变量 `https_proxy=http://127.0.0.1:62216` 是**沙箱代理，不通 Google**，而 curl / urllib
  **默认读它** → 所有请求静默失败（现象是空响应，不是报错，极易误判成「Google 没补全」）
- **`127.0.0.1:7890`（本机 Clash 混合端口）可通 Google** —— 脚本必须显式指定代理
- 两条 Google 官方通道：**Suggest 补全**（`suggestqueries.google.com/complete/search`，
  `client=firefox`，种子回显在第 0 位需剔除）+ **Trends**
  （`relatedQueries` 给相关查询；`multiline` 批内比较 + **锚词归一**给跨词可比热度）
- Trends **429 极频繁**（约每 2-3 个请求一次）→ 必须**指数退避 6/12/24/48s**

### 数据规模
| 项 | 值 |
|---|---|
| Suggest 种子 | 6,977（成功 6,976，**100% 覆盖**）× 5 市场（en-US / en-GB / en-SG / en-AU / de-DE） |
| 唯一补全词 | **11,573** |
| 含 esim/sim 的词（主交付物） | **11,454** |
| 站内已覆盖 / 缺口 | 9,564 / **1,890** |
| Trends 种子 | 181（120 基础 + 61 补充） |
| 带 Trends 指数的词 | 69 |
| 跨词可比热度（批量比较） | 90 词 / 23 批，**只有 10 个词测到非零热度** |

### 关键发现
1. **★ 补全证据 ≠ 真实热度，而且 `综合分` 会把词排反**（本轮最重要发现）：
   - `is esim available in portugal`：`sources` **51**、综合分 **88.8**（全站仅 17 词 ≥88.8）→ 实测相对热度 **0.0000**
   - `best esim for japan`：`sources` **1**、综合分 **69.5** → 实测相对热度 **0.0054**
   - 逐条查原始补全数据：前者的 51 个来源种子**横跨葡萄牙/克罗地亚/西班牙/土耳其/巴西** —— 它是补全引擎
     给一大批国家种子都挂上的**通用问句模板**；后者只由 **1 个种子**（`best esim`）带出 ——
     **若当初没撒这个种子，日本页最有价值的词根本不会出现在数据集里**。
   - → **`sources` 低不是「没人搜」，是「没撒对种子」；`sources` 高也可能只是「句式通用」。**
     发现词靠补全，排优先级靠批量比较热度。**抽样 90 词里 80 词（89%）低于 Trends 分辨率**。
2. **最热的不是国家词**：`esim price`(0.0619) / `esim size`(0.0182) / `esim requirements`(0.0145)
   —— 三者归的都是首页 `/`。国家类里测到热度的只有 `best esim for {国家}` / `esim price {国家}` 句式。
3. **两版交集只 9.3%**（Bing 4,579 ∩ Google 11,454 = 1,060）→ **任何单通道采集都是不完整的视角**。
4. **更正上一轮的错误论断**：上一轮写「Bing 会往所有 eSIM 查询注入同一段通用热门块」——**是错的**。
   实测（`scripts/kw_engine_compare.py`）：两引擎的两两 Jaccard 重叠率**都是 0.000**，
   被 ≥3 个互不相关种子共同带出的词**两边都是 0 个**。真相是**地理簇内共享** ——
   `buy esim for dubai` 的 57 个来源种子**全部是中东种子**（saudi arabia / UAE / qatar / israel）。
   → 正确结论仍是「`sources` 在种子密集的语境里会饱和」，但这是一切补全引擎的共性，换 Google 也治不了。
5. **锚词归一验证通过**：`esim` 在 23 个批里的批内均值稳定在 **76.55–76.57** —— 证明跨批可比
   （若锚词在各批漂移很大，批量比较结果作废）。
6. **Trends breakout 含无关暴涨词**（`saily esim` 的 rising 是 medvi / shop lc / embody），
   且**只用「与种子共享词元」过滤会误杀**（`esim japan` 的 top 里有 `saily`）。
   → 判据必须是「命中 eSIM 强领域词白名单（esim/sim + 品牌名 + 国名与别名 + 地区名，实测 141 词）**或**与种子共享实词」。
7. **报告阈值必须现算**：首版写死「综合分 ≥ 60」，得出「城市词 965 个里 **0 个**高需求」的**反向结论** ——
   查分布才知全站中位 35.1 / 前 10% 46.4 / 前 1% 54.8，`≥60` 只有 95 词（0.8%）。现改为分位数现算并标注来源。
8. **顺手修掉一处产物卫生问题**：`kw_report_google.py` 原用 `OUT.write_text()` 且未传 `newline`，
   在 Windows 下把报告写成了 **658 处 CRLF**（红线 38 的同一个坑）。改为 `open(..., newline="")` + 写后断言无 `\r\n`。

### 新增脚本
`kw_harvest_google.py`（Suggest）· `kw_trends.py`（relatedQueries，含 `--from-scored` / `--merge`）
· `kw_trends_compare.py`（批量比较 + 锚词归一）· `kw_score_google.py`（三路证据打分）
· `kw_classify_google.py`（**动态 import `kw_classify.py` 复用分类规则，不复制**）
· `kw_report_google.py`（报告，数字全现算）· `kw_engine_compare.py`（两引擎对照实验）

### 新增产物（`docs/keywords/google/`）
`kw-google-collected.csv`（11,454 词 × 21 列，主交付物）· `kw-gaps-google-2026-10-08.md`（报告）
· `kw-trends-index.csv`（跨词可比热度）· `kw-google-scored.csv` · `raw_google_suggest.json`
· `raw_google_trends.json` · `engine-compare.json`

## 已完成（关键词植入七批全量执行 + 冠词守卫 + FAQ 同质化收口，2026-10-08 第五十六轮）

**起因**：用户指令「就按你的思路开始全部优化执行，执行完成继续审核，审核如果有问题，继续优化迭代」——
即把第五十五轮交付的 `docs/keywords/google/kw-placement-plan-2026-10-08.md` 里 **7 个批次全部执行**，
每批执行完立即审核（构建 11 项闸门 + 零回归 diff + 反同质化自证），审核发现问题继续迭代。

### 七批执行结果

| 批次 | 动作 | 落地 | 变更面 |
|---|---|---|---|
| 1 | 首页 FAQ Q1 含 `eSIM price`；`#price-floor` 小标题含 `eSIM price`；新增免费/预付一问；三步流程补「先查手机」 | `i18n/{en,de}.toml`（4 key 改写 + 2 新增）、`layouts/index.html` | home 2 页 |
| 2 | 兼容性指南加「eSIM 没有尺寸」「eSIM 需要什么才能用」两段；`what-is-an-esim` 加「不需要什么」 | `content/en/guides/esim-compatibility-check.md`、`what-is-an-esim.md` | 指南 6 页（含 4 页因列出被改页 description 而变） |
| 3 | 品牌子页 FAQ 追加 Q6–Q9（口碑 / 可用性 / 激活 / VPN·本地号） | `layouts/compare/provider.html` + 10 个 i18n key | **provider_sub 499** |
| 4 | 50 国 `data/faqs/*.toml` 各追加 4 问（可用性 / 设备 / 号码 / 口碑）→ **6 条变 10 条** | `scripts/faq_frames.py`（SLOTS 2→3 tuple、7 槽、4 个新片段池、追加模式）、196 条模板池 + `jp.toml` 手写 4 条 | country_hub 100 |
| 5 | `#verdict` 句式 → `What is the best eSIM for {country}?` | `layouts/compare/single.html` | country_hub（同上） |
| 6 | 品牌 Hub 新增 `#reviews` 区块（H2 含 `eSIM reviews` + 读法三条 + 论坛段），原页尾 `#reading` 的口碑卡**整体上移**（复用同一批 i18n key，`#reading` 由 3 卡变 2 卡） | `layouts/esim-providers/single.html` + 8 个 i18n key | provider_hub 10 |
| 7 | 区域词并入 5 篇区域指南（Q2 答案补真实双国配对 + 新增 providers / 全区包两问）；城市词并入国家页 `#quirks` 场景段（城市清单取自 `data/carriers.toml` 的 `info.cities`，50/50 国有值且逐国不同） | `content/en/guides/best-*-esim.md`、`layouts/compare/single.html` + 1 个 i18n key | guides 5 + country_hub（同上） |

### ★ 本轮新增第 11 项构建闸门：`check_article_agreement.py`（冠词一致性）

同一个坑**踩了两次**（第二十四轮 `whether a {{ .brand }} plan` → "a Airalo"；本轮 `Does a {{ .brand }} eSIM` → "a Airalo"），
所以改成机器拦。**两道**：

1. **产物级** —— 扫 `public/**/*.html`，剥标签后匹配 `a/an + 名词`，命中品牌名/国名比对期望冠词。
   - `BRANDS_AN = {airalo, alosim}`；`COUNTRIES_AN = {argentina, australia, austria, egypt, ethiopia, iceland, india, indonesia, ireland, israel, italy}`
   - ⚠ **`PRONOUNCED_CONSONANT = {ubigi, united*, uae, ukraine, uganda, uruguay}`** —— 字母是元音但**发音是辅音 /j/**，
     必须配 "a"。用「首字母是不是元音字母」做判据会在这里**误报**（`a Ubigi plan` 是对的）。
2. **源码级** —— 禁止「冠词紧邻专有名词占位符」：`a %s eSIM` / `a {{ .brand }}` / `a {country}` / i18n 里的 `a {{ .brand }}`。
   - **为什么必须有第二道**：产物级只看得到**当前真的渲染出来**的组合。实测品牌 Hub 里 7 个 printf 问句都写成 `a %s eSIM`，
     只有 3 个在当前品牌分层（`$v 1`/`$v 2`）下渲染，另外 4 个 + `networks/single.html` 那句**全绿通过** ——
     等哪天来个元音开头的品牌或国家才暴雷。
   - 禁令**窄化到专有名词占位符**，放过 `a {{ .days }}-day trip` 这类数值（否则满屏误报）。
   - `--selftest` **18 项**（产物级 7 + 源码级 11），双向验证：既证明会抓住，也证明放过合法写法。

**实测战绩**：首跑抓出 **47 处**存量（20 个元音开头国名 × en/de）；修完当轮，守卫又抓出**我新写的 2 处**
（`a {{ .brand }} review`）—— 守卫在同一个回合里拦住了写它的人。

### ★ 审核迭代：Q4「ID 核验」14 国同质化

自证脚本（产物级逐问 md5）跑出：Q1–Q3、Q5–Q10 都是 **50/50 唯一**，只有 **Q4 = 37/50** ——
`kyc_required = true` 的 14 国（vn id ph in cn tr mx ar ae sa il eg ma ke）共用了同一句套话，
而那句话里**既没有国名、也没有该国具体规定**。

而 `data/countries.toml` 的 `quirks` 里其实躺着 14 国各自的真实登记事实。
→ 逐国按各自规定重写（越南身份证上传 / 印尼护照上传 / 菲律宾 ID 自拍 / 印度护照绑定 /
中国反向（走香港网关、无需登记）/ 土耳其护照 / 墨西哥 CURP / 阿根廷 DNI / 阿联酋护照扫描 /
沙特护照 / 以色列 ID / 埃及线下证件照 / 摩洛哥护照 / 肯尼亚线下护照）。
**修完 10 个槽位全部 50/50 唯一。**

同时把 `check_faq_facts.py` 的 R10 从「五条」扩到「**六条**」：新增 **R10(f) —— 第 4、5 条（手写问答，
不走片段库）也必须在 50 国上骨架两两不同**，并加了一条自测反例（`手写槽（ID）撞车` → `slot4`）。
⚠ 并在脚本文档里写明**尺子不能混用**：R10(f) 用的 `skeleton()` 会抹掉国名，所以拿它判 Q6（邻国问答）
永远只有 8/50「唯一」—— 那是**尺子失真不是数据重复**，Q6 的判据一律是产物级 R11。

### 验收（全部走产物文本抽取，**不做截图**）

- `npm run build` **EXIT=0**，11 项闸门全绿（含新守卫 `产物级 0 / 源码级 0`）
- **零回归 `--diff`**：批次 1–7 累计 **634 处**变更，逐页型可解释 ——
  `provider_sub 499`（批 3）+ `country_hub 100`（批 4/5/7）+ `guides 11`（批 1/2/7）+ `networks 12`（冠词修复）+
  `provider_hub 10`（批 6）+ `home 2`（批 1），**零未解释**；迭代那轮再变 28 处 = 14 实名国 × en/de。
  两次确认后均已 `--write-manifest` 覆盖基线。
- `scripts/_verify_round56.py`（新增，**130 项断言全通过**）：H2 句式、城市句真实城市、FAQ 10 问无残留 token、
  品牌 Hub `#reviews` + `#reading` 2 卡、区域指南 6 问、以及三条反同质化自证
  （`#reviews` 10 页唯一 / 城市句 50 页唯一 / 新增区域问答 5 篇互不相同）
- **逐问 md5 去重（用户定的判据）**：10 个槽位 **全部 50/50 唯一**

### 已知缺口（本轮未做，登记在案）

- **德语国家页的 H2 仍是英文硬编码**（如 `What is the best eSIM for Italien?` —— 句子英文、国名德语）。
  与该页其余 12 个 H2 同源，是既有的「德语站 i18n 完整性」欠账，**不是本轮引入**。
- `data/faqs/jp.toml` 顶部禁令（激活/安装类问题归 Roami 站）仍在执行：国家页只加可用性/设备/号码/口碑四类。
- 第五十二～五十六轮改动**全部未 commit、未部署**。

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

- ✅ **规则变更（用户定）**：标题全部收窄到 48-54 字符（原 ≤60）；**内页标题一律不带品牌词**（新站无人搜品牌，字符留给关键词；仅首页标题保留品牌）；描述收窄 120-140（原 120-158）且**每页必含品牌 "eSIMSift"**（用站内标准拼写，不拆成「带空格 / 不带空格」两种写法；2026-10-15 第九十四轮起统一为**无空格** `eSIMSift`）；法务/联系 4 页（privacy/terms/contact/disclosure）豁免 eSIM 关键词检查（不参与关键词竞争，仅受长度+无品牌约束）；404 页全豁免
- ✅ **head.html**：`<title>` 尾缀 `| eSIMSift` 移除（首页标题在 front matter 自带品牌）；国家页/子页标题改**候选串降级链**（从长到短取第一个 ≤54，审计兜底查 ≥48）：国家页 6 档（"8 Providers Compared From" → "All 8 Providers From" → "8 Providers From" → "Compared From" → "Prices From" → "From"），子页计量型 6 档 / 无限流量型 6 档（holafly 长国名自动落 "eSIM Plans From"）
- ✅ **新 `scripts/regen_meta_brand.py`**（幂等，可重跑；dry-run 先行）：A. 50 国 desc 品牌前置版（"eSIMSift compares every {C} eSIM: N real plans…"，数据实时计算）；B. 28 VS 页标题按原家族重建到 48-54（F1 Verdict / F2 Price Comparison / F3 Which One Is Cheaper / roami-vs-roamic 特例）+ desc **3 家族轮换**（i%3，反同质化）；C. 29 个手写页显式 map（**品牌页/枢纽页 lead-in 各不相同**——"How good is aloSIM?"、"Saily is the NordVPN team's eSIM —" 等，8 连排比是模板化信号）；/esim-providers/ 标题 "eSIM Providers A-Z"(18) → "Every eSIM Provider Compared: 2026 Prices and Reviews"(53)；compare 枢纽 + methodology 两页补入（上轮漏网）
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

## 已完成（第二批品牌扩容 · Jetpac 接入 + 三处基础瑕疵修复，2026-10-07 第四十四轮）

**目标**：Jetpac 全链路接入（9 → 10 品牌），沿用 Nomad 试点沉淀的手册顺序。

### 落地（49/50 国 · 877 条）

| 层 | 动作 |
|:---|:---|
| 数据 | `scripts/scrape/raw/jetpac/` 50 个 JSON 入库 → `toml_write.py jetpac --checked 2026-10-04`（**raw 的真实抓取日，不是今天**）→ `backfill_networks_uniform.py` → `_rename_us_gb.py`；产出 `data/plans/jetpac.toml` **49 国 877 条**（unlimited 325 / 计量 552），**FJ 无块**（空国被正确丢弃） |
| 档案 | `providers.toml` 新增 `[jetpac]` / `[jetpac.info]` / `[jetpac.policy]`（10 品牌齐）；`profile_checked="2026-10-07"`；`color="#3C249C"` 从 logo 采样；`promo_code="ESIM15"`（15%）+ 2 个备选码 |
| 接线 | `hugo.toml` 加 `[params.outbound.targets.jetpac]`（**故意不加 `country_path`**，见下）；`content/en/esim-providers/jetpac.md`（title 51 / desc 137）；logo 归位 `static/img/providers/jetpac.webp` |
| 页面 | `gen_provider_pages.py` → **499** 子页（9×50 + 49）；`gen_vs_pages.py` → 新增 9 对决页（C(10,2)=**45**）；`regen_meta_brand.py` 65 文件；`_solve_titles.py --write` **只有 1 行变化**（Qatar 无限最低价 $4.54→$4.50，其余 49 国段分配纹丝不动） |

### ★ 验收：变更面 100% 归因（做了**对照构建**，不是「看着对」）

| 问题 | 方法 | 结果 |
|:---|:---|:---|
| 642 处变更是否全由 Jetpac 引起？ | 把 Jetpac 从**数据层 + providers.toml + content** 三处撤出，重建到项目外，与当前 public 逐字节比 | 共有 **643** 页里 **642 页不同，其中不含 "jetpac" 字样的 = 0**；新增页恰好 **59**（49 子页 + 9 对决页 + 1 hub）；撤掉后**唯一毫无变化**的页是 `en/index.html`（语言重定向壳，不含页脚） |
| 59 个新页收录了吗？ | sitemap | 585 → **644 URL**，59/59 全收录 |
| 缺国（Fiji）传播对不对？ | 逐国读产物计数 | **Fiji 页 `#6 of 9 providers`，荷兰页 `#2 of 10`**；德语站同样正确（`de/compare/fiji/` 正文零 jetpac，只有页脚 2 处链接） |
| 日期盖章对不对？ | 读台账 | 509 单元（459 → +50）：`plans.jetpac.*` **49 个**（缺 FJ）+ profile 1 个，全 `2026-10-07`；8 个老品牌仍各自 `2026-09-30` —— **子页声明自己的核对日，国家页取聚合** |

### 同轮修掉的三处基础瑕疵（都是这轮才暴露的真问题）

1. **`bump_checked.py` 写回丢行尾** —— `raw.rstrip("\r")` 只用于匹配、写回时没还回去，`jetpac.toml` 因此混进 **49 行 LF**（CRLF 文件）。修法：`eol = "\r" if raw.endswith("\r") else ""` 拼回行尾。
2. **`jetpac.toml` 行尾混杂** → 统一为 CRLF（与同目录另外 9 个 plans 文件一致）。**顺带证明零产物影响**：对照实验的差异集只含 nomad 相关页。
3. **`verify_provider_pages.py` 第 13 项从「静默跳过」改成显式双分支** —— 原写法 `if grp:` 让「页面上压根没有按钮组」静默通过，报告只印 `497/499`，分不清「按设计不渲染」与「漏渲染」。真相是模板门槛 `{{ if gt (len $myRows) 3 }}`（斐济的 saily/ubigi 各 2 个套餐）→ 现在 `≤3 且无按钮组` 计入 `chips_na` 并显式打印，`>3 且无按钮组` 直接 FAIL。**按纪律注入反例证明会红**：改名荷兰 jetpac 页的 `id="plan-days-group"` → 如期 `价格表有 15 行却没有天数按钮组` + 退出码 1 → 按字节还原（sha256 一致）。

### ★ 本轮踩的坑（详见 §14 红线 51–53）

- **`Path.write_text()` 在 Windows 默认把 `\n` 转 CRLF** → 对**本来就是 CRLF** 的 `data/plans/*.toml` 写出 `\r\r\n`，注释里的孤立 `\r` 是非法 TOML → hugo `invalid character in comment` **整站构建失败**；同样写法对 LF 的 `providers.toml` 却没事 —— 极易蒙混过关。
- **删品牌时残留对决页 = 构建失败**：对照实验里 `ignoreFiles=['jetpac\.md$']` 漏了 `airalo-vs-jetpac.md` / `jetpac-vs-nomad.md` 两种命名 → `unknown provider "jetpac"` → nil pointer → **产物只写出 559/643 页**。`gen_provider_pages.py` 只清理子页。
- **Jetpac 官网是 SPA，深链不可用**：`/product-details/{slug}-esim` 对任意路径返回 **200**、标题由 slug 现场拼接、价格回落 $1 占位。串行复测（`kenya` 落到 Vatican City、`netherlands`/`united-states` 只有占位价、只有 `japan` 有真内容）→ 按 Nomad 先例**只走 base**。**教训：状态码不能当证据。**
- **`--checked` 要写 raw 的真实抓取日**，不是今天（jetpac raw 是 10-04 抓的）—— 否则文件头写着「Scraped … on 2026-10-07」是不实陈述。

### 一处附带修复（非 Jetpac 特有，已分开记账）

跑了 `scripts/backfill_networks_uniform.py`（**全局脚本**，给所有品牌回填 `plans[ISO].networks`），顺手修好 nomad 此前遗留的 `networks = []`。**单独做了单变量实验量化影响面：123 页**（国家页/对决页 59 + 德语 51 + `/networks/*` 13），**品牌子页 0** —— 因为子页的 `#hostnetwork` 渲染的是**国家级** `carriers.toml`，不是品牌自己的 networks 字段。123 页全部与 nomad 相关（「完全不提 nomad 的差异页」= 0）。

### 验收（全部为**产物文本断言**，按用户约定不做截图）

- `npm run build` 九项全绿：704 文件 / 702 页 / 4028 段 JSON-LD / 17769 个 h2/h3（bad 0）/ 499 子页 13 项全过 / sitemap 644 / A·B·C 三组不变量通过
- 子页 13 项：标题 499/499（46–54，均 50.9）、description 499/499、H1 499/499、逐套餐 Offer 与表行数一致 499/499（Offer 合计 **9095** 条）、FAQPage 499/499、BreadcrumbList 4 级 499/499、WebPage 元数据 499/499、计划数三处对账 499/499、**天数按钮 497/497 + 2 页按设计不渲染**、套餐行标注（无限 4602 / <1GB 计量 48）、「尚未核实」政策页 0
- 零回归基线重建（**702 页**）

---

## 已完成（发布前体检 + 两处必修项，2026-10-07 第四十九轮）

**用户请求**：审核当前这批内容能否正式发布；给出结论后「两处都修」。

### 体检（结论：技术就绪）

- `npm run validate` **真实退出码 0**（0 error / 0 warning）；702 页 / sitemap **644 URL** / 4028 JSON-LD / 品牌子页 499
- `check_links.py`：**187,316 条 href，坏链 0**
- 英文 643 页无 `draft` / 无 `noindex`，全在 sitemap；产物无 localhost、无备份目录泄漏；
  **大写 `SAMPLE`/`TODO`/`PLACEHOLDER` 全为 0**（首查 105 个命中**全是小写误报**：`Speedtest samples` / HTML `placeholder=` / `todo`）
- ⚠️ **`| tail` 会吞掉退出码**：第一次用 `npm run build 2>&1 | tail -40`，取到的 `$?` 是 `tail` 的 0；
  改「重定向到文件 + `$?`」才拿到真值（这条坑记忆里有过，本轮又差点复现）

### 必修项 ①：legal 页把「待办」渲染给了读者

`/privacy/` 与 `/terms/` 的正文里印着 `<p><em>Todo: legal review before launch.</em></p>` ——
`content/en/privacy.md:6` / `terms.md:6` 的编辑备忘被 Markdown 当**斜体正文**渲染，**读者与 Google 都看得到**。
→ 移入 front matter 注释（含移入原因与日期）。
**顺手踩坑**：替换时误把匹配模式里的 `---` 一并删掉，注释落到 front matter **外面** → 页面出现 **4 个 `<h1>`**
→ B 类不变量当场 FAIL（`✗ privacy/index.html: 4 个 <h1>`）。已修，并加断言（`---` 行号必须 == `[0, 6]`）。见红线 59。

### 必修项 ②：`#whobeats` 的问题在判据，不只是文案

导语宣称 *"the same data allowance and the same validity… rather than a bigger bucket"*，
但 `partials/provider-alts.html` 的真实逻辑**只在 ② 同规格分支查天数**，`① unlimited` 与 `③ at-least` 都只比数据量：

| 事实 | 证据 |
|:---|:---|
| 全量 499 个品牌×国家单元的匹配分布 | `same-spec 336` / `at-least 101` / `unlimited 62` / **`entry 0`** |
| **① unlimited 分支**：`无限 3d ↔ 无限 1d` | holafly 页 **10/10 行**全违规（holafly 是纯 unlimited 品牌） |
| **③ at-least 分支**：`1GB/30d → 1GB/7d` 等 | 8 例（yesim 5 · jetpac 2 · roami 1），**对手档覆盖不了行程** |
| 页面可见行（每页 Top-10）规格不符 | **33 / 93 = 35.5%**（上轮口径 31.8%） |
| `mt` 字段 | **死字段** —— 只在 `provider-alts.html` 写入，`layouts/` 全文零读取；而其注释写着「会渲染成标记」 |

**修法（判据 + 文案一起改）**
- `① unlimited` 与 `③ at-least` 两个分支各补 `(ge (int .days) $md)`
- **删掉 ④ 的 entry 回退**（全量 499 单元一次都没触发，且「入门价对入门价」本就不是 like-for-like）→ 无可比项就**该国不列出**
- `who_beats_lead` / `who_beats_caveat`（en/de 同步）改成与三层口径逐字一致
- 头注释加 2026-10-07 修订说明；`mt` 的注释改为「目前没有模板读取」

### 验收

- `npm run build` **EXIT=0** 九项全绿（704 files / 702 pages / 4028 JSON-LD / 499 子页 / FAQ R1–R11 / 日期一致 / A·B·C）
- 产物断言：`/privacy/` `/terms/` **h1 = 1 且正文无 `legal review`/`Todo`**；
  品牌 hub 的 whobeats 表格 **88 行 / 规格不符 0 行**（yesim 由 7 行降到 2 行 —— 判据收紧后只剩真可比项）
- `--diff`：**变更 12 = provider_hub 10 + static 2（privacy / terms）**，新增 0、删除 0 —— 完全归因
- 基线重建 **702 文件**

## 已完成（去同质化方案批判性审核 + 3 项执行，2026-10-08 第五十三轮）

**用户请求**：审核 `esimsift-compare-dehomogenize-prompt.md`（自己整理的批量改写提示词），
**站在 Google SEO 角度用批判思维**判断，对的才执行。

**结论**：诊断方向对（加真正属于该国的实质内容），但**三处关键判断错、处方大部分不该执行**。
采纳并执行 **3 项** —— 其中 1 项是**文件没看出来的真实缺陷**。

### 执行项

| 项 | 内容 |
|:--|:--|
| **① hreflang 真实缺陷（★ 本轮最大发现）** | `head.html` 只守了 hreflang 的**目标侧**（不指向 noindex 页），没守**来源侧** → **54 个德语页在 noindex 状态下向外发 `en-us`**，而英文侧因译文 noindex 而不回指 → **单向标注**，GSC 报 *No return tags* 并整体忽略。改：`{{ if and (not .Params.noindex) (ne .Kind "404") }}` 并纳入译文 range；`404` 也退出分组 |
| **② `#reality` 导语** | `Price is only half of the decision.`（499 页 × 50 国逐字重复的**空泛总评**）→ 换成**来源披露** `Quoted from {brand}'s own published policy rather than paraphrased —` |
| **③ `#localnotes` 导语** | 删掉零信息尾句 `They are here because they decide which plan shape actually makes sense.` |

### 新增工具与守卫

- **`scripts/check_hreflang.py`**（进 `check:output`）：四条判据读产物 —— A 自身 noindex 不得发标签 ／ B 目标产物必须存在 ／ C 必须**互惠** ／ D 目标不得 noindex。**`--selftest` 7 例**。
  **双向验证**：对**改前旧产物**跑 → `ERROR: 54 problem(s)`（正是那 54 个德语页）；`--selftest` 全过；改后跑 → `OK: 702 pages, 647 tags on 645 pages`。
- **`scripts/audit_dup_raw.py`**（常驻诊断，**不进 build**）：诚实口径的重复度量 —— **不做任何归一化**，直接比渲染后的文本。
  动机：`audit_boilerplate.py` 会把数字→`#`、国名/品牌名→`@` 再比骨架，于是「带本页数字的句子」也被算成模板。
  **它适合横向比页型，不适合回答「Google 看到的重复有多少」。**

### 关键数据（诚实口径）

| 品牌 | 逐字重复槽位占比 | 品牌 | 逐字重复槽位占比 |
|:--|--:|:--|--:|
| holafly | 51.5% | alosim | 40.2% |
| airalo | 44.3% | nomad | 40.0% |
| roamic | 43.2% | ubigi | 37.7% |
| roami | 42.4% | saily | 36.5% |
| yesim | 41.4% | jetpac | 41.2%（49 页） |

**逐字重复 ≈ 37–52%**（用户文件的 92%、我那把尺子的 84–88% 都不是这个问题的正确答案 —— 两者都把「带本页数据的句子」算成了模板）。
残余 **18 种句型全部落进「不可能改」三类**：品牌级政策（该品牌全球只有一份政策）／方法论与来源披露（一致性 = E-E-A-T）／UI 与计算器说明。

### 明确不采纳（附理由）

| 文件建议 | 不采纳理由 |
|:--|:--|
| 400 页叙事文案每国重写 | 与**单一事实源**架构正面冲突；产出 4000 段**会静默过期、无法核对**的散文（本项目已有前例：FAQ 手写数字 → 99 条断言过期） |
| 「独特叙事 ≥ 40%」硬指标 | 该指标**只能用文件自己禁止的行为（同义改写）达成**；Google 判定原文是 *substantially the same regardless of **minor variations*** —— 换说法正是 minor variations |
| 4 个 H2 / Title / H1 按国重写 | 现 H2 已含`品牌+国家`直接匹配长尾查询，改写成国别措辞**反丢匹配**；无排名收益；破坏右栏目录镜像与标题硬规则 |
| 「单语站应移除 hreflang / 改 `en`」 | **前提错误** —— 本站是 en+de 双语，hreflang 必需；`en-us` 在美式拼写 + USD 计价下是准确的 |
| FAQ 每国换 1–2 个特有问题 | **没有对应数据源** → 只能是编造；且国家页 FAQ（50 国 × 6 问）已是逐国问答层，再编一套会重复并稀释 |

### 「方向对但要做成数据驱动」的部分（核查后：已在站上）

文件 §3 的三步框架（网络现实 → 旅行者画像 → 意图角度）**方向完全正确**，但实现不该是手写散文。
逐项核对后，**它要的数据已存在且已上屏**：`carriers.toml` 154 条逐国逐运营商 `note`（已渲染在 499 页 `#hostnetwork` 卡片）、
`countries.toml` 101 条 `quirks`（第五十二轮已落 `#localnotes`）、`#tripcost` 逐页现算、`#tradeoffs` 按该国实时排名算出。
**它缺的不是内容，是对现状的正确读数。**

### 验收

- `npm run build` **EXIT=0**，九项 + 新增 hreflang 守卫全绿
- `--diff` 归因吻合：**变更 555 = provider_sub 499（两处文案）+ 56 页（丢掉错误 hreflang：50 德语国家页 + de/compare + de/guides + de/networks + de/research + de/404 + 404）**，新增 0、删除 0
- 产物断言：旧句残留 **0 / 0**；德语页 hreflang **0 条**；`/` 与 `/de/` 各 2 条且互惠；`404` **0 条**
- 基线重建 702 文件 → `--diff` **变更 0 / 新增 0 / 删除 0**
- 报告：`esimsift-去同质化方案审核-回应与执行-2026-10-08.md`

**⚠️ 本轮新增两条纪律**：
1. **模板注释必须写成单行** —— 多行 `{{/* … */}}` 里的换行会被当成**输出文本**，全站每页多一行空白，
   `--diff` 当场报「变更 701」（预期 555），**归因直接失效**。第一版就是这么写的，已改单行重建。
2. **两把尺子量的是两件事，别混用** —— `audit_boilerplate.py`（归一化骨架）用于**横向比页型**；
   `audit_dup_raw.py`（原始文本）用于回答**「Google 看到的重复有多少」**。引用同质化数字必须写明用哪把尺子。

## 已完成（反同质化 P0/P0'/P1/P2 四项整改 + 同尺复算，2026-10-08 第五十二轮）

**用户请求**：站点已全量上线，按我的思路把上一轮（第五十轮）报告里自己提出的 P0 / P0' / P1 / P2 **全部优化**，
完成后**再次审核**，再**迭代**。

**改动前提**：只动模板与 i18n，**不动任何数据集**；全部改动只影响英文站（德语站无 vs 页 / 品牌子页 / 品牌 hub）。

### 四项改动

| 项 | 落点 | 做法 |
|:--|:--|:--|
| **P0** | `layouts/compare/provider.html` | 新增 `#localnotes` 区块，逐条渲染该国 `countries.toml` 的 `quirks`（此前 **400 个品牌子页一条都没有**） |
| **P0'** | `layouts/compare/vs-single.html` | `#more` 区块 44 张卡各印一句 `X starts cheaper in N of M countries.`（全站 1980 条、骨架仅 2 种、同页重复 44 遍）→ **堆叠比例条 + 分数**，口径说明上移区块导语 |
| **P1** | `layouts/compare/provider.html` | `policy.fup_note` 同页出现 3 次（`#reality` 卡 / `#fup` 页脚 / `#faq` 答案）→ 删 `#fup` 页脚；FAQ 两条改写为**结构化字段重组 + 区块内链**（`fup_allowance` / `hotspot_allowance`），答案保持自包含 |
| **P2** | `layouts/esim-providers/single.html` | Q9 退款整段复制 `info.refund` → 「链回卡片 + 讲时间窗口」；Q11 热点内嵌 `hotspot_note` → 用 `hotspot_allowance` 重组；`#alternatives` 9 张卡 `Cheapest in N of M countries.` → 比例条 + 分数 |

`i18n/{en,de}.toml`：新增 9 条 key（en 1174→1178 行 / de 1179→1183 行）+ **改写** 2 条
（`compare_provider__faq_a_unlimited` / `__faq_a_hotspot`，原值是 `"{{ .detail }}"` 直通）。

### 同尺复算（`scripts/audit_boilerplate.py` 全量前后对照）

| 页型 | 页数 | 槽位 前→后 | 模板槽 前→后 | 占比 前→后 | 页内重复 前→后 |
|:--|--:|:--|:--|:--|:--|
| guides | 10 | 819→819 | 0→0 | 0%→0% | 5→5 |
| networks | 12 | 1501→1501 | 279→279 | 19%→19% | 22→22 |
| country | 51 | 6768→6768 | 4364→4364 | 64%→64% | 687→687 |
| **provider_hub** | 10 | 1453→1356 | 996→936 | 69%→69% | **236→133** |
| **provider_sub** | 499 | 40735→**43607** | 23990→**27357** | 59%→**63%** | **3953→1979** |
| **vs** | 45 | 3375→**1485** | 2952→**1062** | **87%→72%** | **1890→0** |

**同品牌跨国家分组 10/10 全面下降**（airalo 87→85 / holafly 90→88 / saily 86→82 / nomad·roamic 86→84 …），
页内重复全部腰斩。**同国跨品牌分组上升 3–5 点**（argentina 74→77 / brazil 74→80 / canada 75→80），
原因是 quirks 属**国家级事实** —— 同国 10 个品牌子页必然共享，分子分母同增但共享部分增得更多。

**为什么这个上升不是问题**：P0 往 400 页**塞进了此前完全不存在的内容**（**+2872 句槽**，其中 101 条完全独立文本）。
消除的重复绝对量为 vs **−1890**、provider_sub **−1974**、provider_hub **−103** ——
**内容变厚而非变薄**；只看占比会得出「改差了」的错误结论（占比对新增内容不敏感）。

**`country` 页 64% 不再动**：22 个模板槽逐条落进「不许改写」类别 —— 方法论披露（`Badges are literal sort positions, not editorial picks`）、
UI 引导（`Try the eSIM trip cost calculator`）、`#bytrip` 的 5 个场景**标签**（tab 标题非句子）。
687 槽「页内重复」经查是**套餐名与运营商名**（数据，非套话）。

### 一个未解释项已结案

`--diff` 报「变更 566 页」时多出 **`networks=12`**（本轮只改了 matchup / provider_hub / provider_sub 三类）。
排查：产物确定性 ✓、networks 页内无本轮任何特征串 ✓、模板不共享 ✓ →
**决定性实验**：把 5 个改动文件临时换回 `HEAD` 版本重建 → networks 页 sha **与本轮改动后完全相同、且都 ≠ 基线**。
**结论**：与本轮无关，是**基线陈旧** —— 基线生成于 `2026-10-07T10:20:58Z`，
用户在 `2026-10-07 18:55` 提交的 `data/plans/{jetpac,nomad}.toml` 落在基线之后。重建基线即覆盖。

### 验收

- `npm run build` **EXIT=0** 九项全绿（704 files / 702 pages / 4028 JSON-LD / 527 layout classes / R10·R11 / A·B·C）
- 产物断言（`scripts/_verify_round52.py`）：`japan/roamic` 的 quirks 1 条 + `localnotes` 锚点存在、
  vs 页 45/45 全部有比例条且 `starts cheaper in` 残留 **0**、四页抽样页内重复 **0**、
  hub 页 `Cheapest in` 残留 1 处（**是表头，不是句子**）✓
- `--diff`：归因吻合（`vs` + `provider_sub` + `provider_hub` 三类），新增 0、删除 0；**基线重建 702 文件**，
  重建后 `--diff` = **变更 0 / 新增 0 / 删除 0**（702 页逐字节相同）
- 交付报告：`esimsift-同质化优化-P0P1P2-2026-10-08.md`；审计原始日志 `docs/audit/{baseline,after}-{all,brand,country}.log`

**⚠️ 本轮新增两条纪律**：
1. **`bytes` 字面量不能含非 ASCII** —— `b'...中文注释...'` 直接 SyntaxError（`bytes can only contain ASCII literal characters`），
   一律 `'...'.encode("utf-8")`。
2. **断言不许撞上自己新写的注释** —— `assert b"starts cheaper in" not in nb` 会被我自己写的替换注释命中；
   `assert b.count(b"fup_note") == 1` 会被注释里的 `policy.fup_note` 命中。
   **断言要只数代码引用**（`{{ .fup_note }}`），并让脚本**幂等**（i18n key 已存在则 `continue`）。

## 已完成（德语正文批 C/D/E + awards 缺陷 + 术语归一 + D9 解禁 —— 德语正式发布那一轮，2026-10-10 第六十九～七十二轮）

**用户逐字请求**：
> `批 C：5 篇 guides 德语正文 ← 现在就可以开始` / `批 D：12 篇 networks 德语正文` /
> `批 E：51 页 compare 正文（50 国家 + 1 hub）` /
> `D9：68 页补完后，单独一轮解禁 noindex + 补 /de/sitemap.xml + x-default + 重刷基线。`
> `全部优化执行，不要每次问我，你自己全部执行完毕，执行后，记得给我审核，在优化`

**前提约束（用户明示）**：`这些德语的页面因为必须达到能正式发布到线上才行，一旦提交就是正式发布。`
⇒ 全程**未 `git commit`**，改动全部留在工作区。

### 四步与体量

| 步 | 内容 | 产物体量 | 轮次 |
|---|---|---|---|
| 批 C | 5 篇 guides 德语正文 | — | 第六十九轮 |
| 批 D | 12 篇 networks 德语正文 | 179,716 bytes | 第七十轮 |
| 批 E | 51 页 compare 正文（50 国家 + hub） | 88,018 bytes | 第七十一轮 |
| awards + 术语 + D9 | 两处真缺陷修复 + 全站解禁 | 见下 | 第七十二轮 |

### ★ d44 `EXIT=1` —— `awards` 数组从未本地化（F 只报 12 条，真实泄漏 77 个字段）

- **现象**：批 D + 批 E 首次合体构建 `EXIT=1`，F 判据 12 条，**全部在 `/de/networks/*`**，而正文里根本没这些串。
- **根因**：`data/networkreports.toml` 的 `[[XX.awards]]`（记分板表格，`layouts/networks/single.html:244`）
  在 `data/de/networkreports.toml` 里**零覆盖**（英语 35 组 / 德语 0 组）。Hugo data 深合并是
  「map 递归、**数组整体替换**」⇒ 整表静默回退英文，**构建 exit 0、check_output 全绿**。
- **为什么此前一直绿**：`awards` 只在 networks 页渲染，而这 11 国的德语 networks 页是**批 D 才建出来的**
  （`check_output` 1279 → 1291 页）。**页集一变，绿灯作废。**
- **F 是黑名单，永远是下限**：只抓到含 `and`/`every` 的 12 条；真实是 **35 组 × 3 字段中 77 个非空字段全英文** ⇒ **低估 6.4 倍**。
- **修法三段**：① `scripts/_patch_awards_de.py` 写 11 国 35 组德语
  （`carrier` 逐字继承 —— 模板按它建映射；数字用德语逗号小数；单位 `Mbit/s`；括注**取自本文件既有 facts 德译**，不发明）；
  ② `verify_de_data.py::check_reports()` 补 `awards` 判据（整国缺失 / 组数不符 / carrier 被改 / 字段未译 / 数字不符 / 死条目），自测 **31 → 34**；
  ③ 新增产物级 `check_award_products()` —— **双向**断言（英语串不在 **且** 德语串在）；
  只证「英文不在」会被 `{{ if $awards }}` 的 else 分支骗过去（假绿）。
- **取证**：新守卫跑**改造前**产物 = **154 处 = 77 字段 × 2**（英文在 + 德语缺），核对 11 国；d45 `EXIT=0` 十项全绿。

### ★ 术语归一 —— `Tempo` 方言并回 `Geschwindigkeit`

- `/de/networks/{land}/` 的正文（`single.html:213`）与记分板（`:244`）**同页渲染**：正文 `Download-Tempo` vs 数据层 `Download-Geschwindigkeit`。
- 实测：`Geschwindigkeit` 家族 **215**（i18n 28 / data/de 119 / 其余）vs `Tempo` **76**（**全部**在 `content/de/networks/*.md`）⇒ `Tempo` 是批 D **局部方言**，向西对齐。
- `scripts/_patch_networks_tempo.py`：**75 处正文 + 80 处生成源字面量**一起归并；
  ⚠ `Tempo` 中性 / `Geschwindigkeit` 阴性 ⇒ 14 条**变格表**逐条手写；
  ⚠ 变格自查须带**右边界**（`ein Geschwindigkeitstest` 是合法复合词，裸子串匹配会假红）。
- **未改（有据）**：`Durchsatz`（22 处）保留 —— 英语原文是 `Throughput`（与 `Speed` 不同的词）。
- **复核**：6 个批 D 生成脚本 `--dry` 全部 `断言全过` / `已应用 0 / 已存在跳过 12` ⇒ 字面量与落盘内容逐字一致。

### ★ D9 —— 德语分层发布解禁（正式发布闸门）

| 动作 | 前 → 后 |
|---|---|
| `noindex: true` | `content/de/**` **643 → 0**（A 成对 79 页 + B 单行 564 页） |
| `/de/sitemap.xml` | **1 条 → 644 条**（`partials/sitemap-urls.html` 以 `.Params.noindex` 过滤，删净即自动补全） |
| `layouts/robots.txt` | 新增 `Sitemap: …/de/sitemap.xml` |
| `layouts/partials/head.html` | 新增 **x-default**（指向 en 版；en 页指自身；**无译文组不发**） |
| 全站 hreflang | **647 tags / 645 页 → 3864 tags / 1288 页**（= 1288 × 3：self + 译文 + x-default） |
| 回归基线 | 重刷（1291 文件）；`--diff` 复核 **逐字节相同** |

**归属闭合**：`d47 → d48` 变更 **1290 = 644 德语 HTML + 644 英语 HTML + de/sitemap.xml + robots.txt**
—— 变更集合**恰好等于「全部 hreflang 页 + 两个声明文件」**，无任何意外变更。

**已知副作用（如实登记）**：`check_i18n` 的「拼装句碎片」**48 → 49**，新增 1 处是 robots.txt 的 `Sitemap:` 行
（机器指令非文案；已用 `i18n_extract.collect()` 定位该文件 frags 2 → 3）。脚本仍 `EXIT=0`。

### 验收（全部产物文本断言，按约定不做截图）

- **d47 / d48 两次 `npm run build` 均 `EXIT=0`，十项闸门全绿。**
- 德语判据：`F 无硬编码英文（644 页）` · `J 无裸印英文区域名（644 页）` ·
  `G 无数据层英文残留（644 页 × 185 条数据串）` · `I 单位统一（i18n 1730 值 + data/de 1556 字符串）` ·
  `H policy 覆盖完整` · 产物级 `城市名 38 处 / 记分板 77 字段` 双向核对。
- `check_output`：1291 pages / 7412 JSON-LD / 499 品牌子页 499 全过 / R10·R11 骨架不重复。
- `check_hreflang`：1291 页扫描，3864 tags / 1288 页，**no tag on noindex/404，all targets exist, all groups reciprocal**。
- 德语完成度终检：`content/{en,de}` md **644 = 644 缺口 0**；i18n **en = de = 1730 key，已译 1706**，
  完全相同 24 条**全部**是公式/专有名词/德英同形词 ⇒ **无实质漏译**。

### ⚠️ 唯一未闭合的能力缺口

**德语译文尚未经有资质的人工审校。** 机器判据能证明「无英文残留 / 单位统一 / 术语自洽 / 结构对齐」，
**不能替代母语审校** —— 这是上线前唯一需要外部资源的事项。

---

## 已完成（研究栏目德语本地化收口：#125 + 3 子页 + 索引正文，2026-10-10 第六十八轮）

**用户逐字请求**：#125（research 模板里的英文硬编码 → 带占位符的整句，保英文侧逐字节恒等）
+ 3 篇 research 子页 + research 索引正文，「做完这一个栏目就整体收口」。

### 三批改动

| 批 | 内容 | 脚本 |
|:--|:--|:--|
| B-1 | `layouts/research/*` 三个模板 **28 处**英文硬编码 → 「带占位符的整句 + `safeHTML`」；**+25 / −2** i18n key | `scripts/_patch_research_i18n.py` |
| B-2 | 107 条德语译文（PI 30 / FU 40 / UE 37） | `scripts/_patch_research_de_keys.py` |
| B-3 | 3 张德语子页 + 索引 `hero`/`faq_heading`/6 条 `faqs`/3 段正文 | `scripts/_patch_research_de_pages.py` |

### 构建轨迹（三次构建，每次差异都做逐字节归属）

- **d39**：B-1 完成，`EXIT=0` 十项全绿 → **英文侧逐字节恒等成立**（d38→d39 只差 `catalog.json` 的构建日戳）
- **d40**：B-2 + B-3 后构建 **`EXIT=1`** —— `verify_de_text.py` 报 12 处，全部落在本轮新建的 3 张德语 research 页
- **d41**：修完复建 **`EXIT=0` 十项全绿**；差异 **变更 3 / 新增 0 / 消失 0**，精确命中那 3 张德语页（英文侧零变更）

### d40 抓到的 12 处 = 三类缺陷（详见 §14 红线 79 / 80）

1. **plan.name 未过 `plan-name.html`**（F：`Days` / `Local` / `Day`）—— 3 处 dict 构造点
2. **`fup_note` 未过 `de-text.html`**（G：8 条英文 fup 原文）—— 1 处渲染点
3. **`delimit … " and "` + `cond … "None"` 硬编码英文**（F：`and`）—— 1 行两处

修法：`scripts/_patch_research_de_leak.py`（6 处模板编辑 + 新增 `g_none` / `g_none_lower`）。
模板**行数不变**（256 / 227 / 157），全文在行内完成 —— 守「模板改动只许改字符序列、不许改行的条数」。

### 验收（全部产物文本断言，按约定不做截图）

| 项 | 结果 |
|:--|:--|
| `npm run build`（d41） | **EXIT=0**，十项闸门 + 数据层守卫全绿 |
| 页面数 | `EN 658 / DE 639`（+3）、`1276 files (1274 pages)`、`7322 JSON-LD blocks` |
| 标题 | `bad: 0`（32520 个 h2/h3） |
| `sitemap` / `hreflang` | `644` / `647 tag(s) on 645 page(s)` —— 与 d40 **逐字不变**（新页 `noindex`） |
| F / G 判据 | `627 页 × 短语 23 条 + 词 8 条` / `627 页 × 144 条数据串（含 JSON-LD）` —— **均由红转绿** |
| 独立探针 `.buildlog/probe_de_research.py` | **OK**：4 张德语 research 页零残留英文；正向断言 `Tage` 99 / `Tag` 140 / `Lokal` 8 / `Unbegrenzt` 18 / `und` 58 |
| 英文侧恒等 | d40→d41 **变更 3 / 新增 0 / 消失 0**，仅那 3 张德语页 |

### 本轮新增/修正的仪器与纪律

- `check_i18n.py` **第 6 条**：`dict "q" "…"` / `dict "a" "…"` 字面量文案（`docs/` 盲区）→ 25288 bytes，`--selftest` 正例 6 / 反例 3 双向自证
- `.buildlog/pub_manifest.py`：`public/` 文本产物指纹（口径 = `.html/.json/.xml/.txt`，与 d36/d38 基线一致）+ `--diff` 三分类
- 修掉 `_patch_research_de_pages.py` 里 `{{{{< count-countries >}}}}` 四花括号（无 `.format()` 却按 format 转义写 → 会原样落盘）
- 修掉 `_patch_research_de_keys.py` 的幂等断言：`pending == mine` 只在首次成立；并显式排除 `research_price_index__region`（德语正确译文就是 `Region`，`de == en` 恒成立 → 判据假阳性）

**下一个栏目**：批 C（5 篇教程）→ 批 D（12 篇 networks）→ 批 E（50 个国家页正文）→ D9 解禁 + 刷基线。

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

### 第五十二轮登记（反同质化下一批候选，均需用户点头）

- [ ] **减少「国家级事实」的复述次数**（唯一站得住的方向）：`provider_sub` 同国分组仍 73–80%，
      剩余共享逐条归因后**可改 0 条**（国家级事实 + 品牌级政策 + 我方披露 + UI）。
      要再降只能把运营商 / 覆盖 / 测速那几块**链出**到 `/networks/<country>/` 或国家页，
      **代价是牺牲页面信息完整性** → 不做句式变体（那是 Google 明文的 *minor variations*，反向操作）。
- [ ] **`fup_allowance` 拆成 `fup_allowance_gb`（数值，可空）+ `fup_allowance_text`（展示）** ——
      现字段**同时供展示层（`#reality` 直接印）与判据层（`#tradeoffs` 用正则抠数字）使用**，很脆弱
      （`"1.5 - 2 GB/day"` 抠到的是上限）。判据只读数值字段。
- [ ] **存量硬编码英文**（`vs` 页 h1/h2/FAQ ≈20 条、hub 页 ≈12 条、国家页 quirks 标题 2 条）——
      **德语站没有这些页型，不构成德语站缺陷**，属工程规范问题，优先级低。
- [ ] **德语站 i18n 完整性**：`i18n/de.toml` 的 `compare_single__*` / `esim_providers_single__*` 一族存英文原文（≈上百条）。
- [ ] 面板外遗留：`/networks/*` 的 `Updated` 徽章取 `now`（见下条 P-A）。

### 第四十八轮（2026-10-07）：两组定向审核（用户点名 4 个 URL）

**触发**：用户点名两对页面要求各审一次 —— **组 1 同国跨品牌**
（`/compare/austria/alosim/` vs `/compare/austria/airalo/`）、**组 2 同品牌跨国家**
（`/compare/united-states/yesim/` vs `/compare/japan/yesim/`）。

- [x] **数字（同一仪器 + 页对页句级交集）**：
      组 1 **共享 59 / 72 句 = 82%**（组内聚合 73%）；组 2 **共享 36 / 74 句 = 48%**（组内聚合 48%）。
- [x] **关键洞察（差值成因）**：组 1 的 10 页**共享同一个国家** → 「国家级事实」整块共享
      （`#hostnetwork` 运营商 + Ookla 基准 + 测速句）；组 2 的 50 页**国家各不同** → 国家级事实完全不重复，
      只剩「品牌档案」那一小块。**「同国」才是同质化的高风险面。**
- [x] **口径副产品**：`norm()` 只归一化数字与品牌名、**不归一化国家名** —— 含国家名的句子在
      **跨国分组**里不算重复、在**同国分组**里算重复。这是正确的（同国页面确实逐字重复），
      但引用数字时必须说明分组维度。
- [x] **逐条归因（这是审核的核心产出）**：
      - 组 1 的 59 条 = `faq` 11 + `others` 8 + `hostnetwork` 8 + `tradeoffs` 7 + `reality` 4 + `fit` 4 + 方法论/UI 17
      - 组 2 的 36 条 = `reality` 8 + `tradeoffs` 7 + `faq` 5 + `fit` 3 + `tc-w-days` 3 + 方法论/UI 10
      - **两组合计 95 条里，可改的 = 0 条** —— 全部落进「国家级事实 / 品牌级档案 / 方法论披露与 UI」三类。
- [x] **查证后排除的三个「疑似缺陷」**（都先核实再下结论）：
      ① `#fit` 里出现 `Yesim's smallest plan…` —— 不是硬编码，是数据驱动取「除自己外最便宜的对手」，
      yesim 页显示的是 Roamic（无自指 bug）；
      ② Hub 页两个同名 H2 —— 分属互斥分支（降级壳页 vs 正常页），同页不会同时出现；
      ③ `#others` 的 8 条共享 —— 同国必然列同一批对手，属**导航职能**的结构性事实。
- [x] **本轮唯一改动**：`compare_provider__faq_a_rival`（**499** 个子页）删掉套话首句
      `Both work in {{ .country }}, and the answer depends on how much data you will actually use rather than on either brand.`
      → 答案直接从事实开始（与第四十六轮对 `faq_a_hotspot` / `faq_a_unlimited` 的处理一致：
      答案引擎摘的是**答案第一句**）。组 1 共享句 **60 → 59**（`faq` 12 → 11）、模板槽位 **604 → 594**。
- [x] **验收**：`npm run build` EXIT=0 九项全绿（704 files / 702 pages / 4028 JSON-LD / 17769 h2h3 bad 0）；
      `--diff` **变更 499 = provider_sub，新增 0、删除 0**（改动只触及品牌子页）；基线重建 702 文件。

**结论：两组到此为正确终点。** 想继续压只有两条路 —— 给 `#others` 换句式（= minor variations，反向操作）
或按品牌裁剪竞品列表（牺牲信息完整性）—— 两条都不该走。将来要降「同国跨品牌」的重复面，
唯一站得住的方向是**减少国家级事实在各页的复述次数**（如把安装说明 / 机型说明链出到 guide），而不是改写句式。

### 第四十七轮（2026-10-07）：模板化同质化 —— 第二轮整改（P1/P2/P3）

**触发**：用户「模板化同质化的问题呢 继续优化」→ 执行第四十六轮登记的 P1/P2/P3。

- [x] **P1 ① 国家页安装卡压缩**：三步有序列表（Buy / Install on Wi-Fi / Land and it works）
      → **一句 + 按钮链到 `/guides/how-to-install-esim/`**。那三步与 guide 是同一份内容、
      在 51 页（50 EN + DE 国家页）上重了 51 遍。新增 key `compare_single__install_oneshot` /
      `compare_single__full_install_guide`（en/de 对齐，德语走 du-form）。
- [x] **P1 ① 延伸**：安装卡的机型说明（`Works on eSIM-capable phones…` + `Your physical SIM keeps working`）
      → **一句 + 链到 `/guides/esim-compatibility-check/`**。完整设备库已有专页，是第二处同类重复。
      新增 key `compare_single__device_compat_link` / `compare_single__device_list_link`。
- [x] **P1 ② 更正上一轮的误判**：`/methodology/` **早已存在**（`content/en/methodology.md` 四节），
      且**已被 699 个产物页链接、链接总数 1679**。上轮只核句子不核链接，把「已存在」写成「待建」。
- [x] **P2 ③ 品牌 Hub `#reality` 导语**：`Price is only half the decision. These four terms decide…`
      → `Quoted from {brand}'s own published policy. Where a brand publishes nothing, we say so rather than guess.`
      （零信息句 → 来源披露；与四张卡不重复）
- [x] **P2 ③ 连带**：删掉 Hub 页**同一句披露的第二次出现**（正常页分支那处 `Rankings and "cheapest" badges…`）。
      页尾另有 `every price, badge and ranking…is a literal sort…` 完整披露，删后不缺口径。
- [x] **P2 ④ 对决页 FAQ 首答末句**（45 页）：`The gap flips by destination, so check your country in the table above.`
      → **`The widest entry-price gap is in {country} — {A} lists ${x} against {B} at ${y}.`**
      由 `$rows` 现算（模板顶部新增 `$gapRow` / `$gapMax`）；全平手时降级为 exact-price-tie 句。
      原句在 `50 win / 0 loss` 的 matchup 上自相矛盾（无「翻盘」可言）。
- [x] **P3 ⑤ 两套说法消解**：Hub 那句被换掉后，`Price is only half (of) the decision.` 不再有两个版本。
- [x] **效果**：国家页模板槽位 3232 → **3182**（51 页）；每页可见文本净减 **274 字符**
      （旧 497 → 新 223），× 51 页 ≈ **14,000 字符**。对决页新句**已不在指纹列**（= 真差异化）。
- [x] **验收**：`npm run build` EXIT=0 九项全绿（704 files / 702 pages / 4028 JSON-LD / 17769 h2h3 bad 0）；
      `--diff` 报 **变更 155 = `country_hub` 100 + `matchup` 45 + `provider_hub` 10，新增 0、删除 0**
      —— **品牌子页 0 变更**，与改动范围完全吻合；基线重建 702 文件。
- [x] **反同质化判据**：三个页型**内容模块全部唯一**；剩余「重复」逐条查证为 **UI 骨架与导航**
      （空容器 / 导航列表 / `calc-*` 计算器控件）—— 这些必须全站一致。
- [x] **德语站**：`/de/compare/austria/` 渲染德语新文案；guide 链接经 `lang-href` 回落英文路径，**无 404**。

**⚠️ 本轮新增两条纪律**：
1. **`模板槽位 / 总槽位` 这个占比对「删内容」不敏感** —— 删重复块时分子分母同步下降，占比可能纹丝不动。
   衡量「减少真实重复」要看**绝对量**（字符数 / 绝对槽位差）。占比适合横截面比页型。
2. **判定「某页/某能力缺失」前先数实际引用** —— `grep -rn "<路径>" layouts/ | wc -l`。
   上轮把已存在且被 699 页链接的 `/methodology/` 判成「待建」，就是从一句话反推整页。

**本轮查证后「不做」（附理由，避免下轮重复劳动）**：
- Hub 的两个同名 H2（`#tradeoffs-pending` / `#tradeoffs`）**分属互斥分支**（降级壳页 vs 正常页），
  同页不会同时出现 —— 不是重复标题。**先确认分支关系再下结论**。
- Hub「客服」「退款」两张卡的来源披露主题不同，合并会丢信息 → 保留。
- 剩余 47%（国家页）/ 55%（hub）的模板槽位成分是**方法论披露 + 区块引导语 + UI 说明 + 来源声明**，
  按「一致性 = E-E-A-T」原则**不应变量化** → 到此为止是正确终点。

**顺带发现（未动，登记在案）**：德语站国家页有**大量英文段落**（`i18n/de.toml` 的
`compare_single__*` / `esim_providers_single__*` 一族存的是英文原文，约上百条）；属 i18n 完整性，应单开一轮。

### 第四十六轮（2026-10-07）：模板化同质化 —— 全站普查 + 首轮整改

**触发**：用户拿 `esimsift-模板化分析.md` 来问 `/compare/austria/alosim/` 与 `/compare/austria/airalo/`
是否模板化、如何优化、其他文件是否同样问题（排除作者署名/bio/资质）。

- [x] **新增诊断工具 `scripts/audit_boilerplate.py`** —— 句子级跨页 boilerplate 普查。
  补上旧判据的盲区：**「跨页模块 md5 去重 = N」是必要不充分条件**（区块含一个页内专属数字就唯一）。
  实测奥地利 10 个品牌子页**块级去重 10/10 全唯一，句子级却是 74% 模板槽位**。
  ⚠ **不进 `npm run build`**（诊断工具不是守卫，给阈值就会被「优化掉」）。
- [x] **全站同质化地图**（整改前）：品牌子页同国内跨品牌 **74–76%**、同品牌跨国家 55–64%、
  品牌 Hub **55%**、国家页 **49%**、对决页 **40%**、networks 16%、guides 0%。
- [x] **竞品卡片去重复**（最大一块）：`#others` 原印 `providers.toml` 全局 tagline，
  11 条 × 449 页 ≈ **4900 槽位**。改为页内算出的「该竞品在**本国**的 $/GB 名次 + 入门档」
  （新增 `compare_provider__op_market_v1..v3` / `op_unl_v1..v2`，en/de 对齐）。
- [x] **去掉同页冗余**：`trip_note` 与 `calc_note` 在同一页把「30 天行程用 30 天档计价」解释两遍。
- [x] **FAQ 去掉通用开场白**：`faq_a_hotspot` / `faq_a_unlimited` 直接给事实
  （答案引擎摘的是答案第一句，不该是套话）。
- [x] **修语法 bug**：`reality_lead` 的 `whether a {{ .brand }} plan` → aloSIM 渲染成 **"a aloSIM"**。
- [x] **效果**：品牌子页全站 **43% → 31%**（模板槽位 18194 → 12772，**−5422，−30%**）。
  **同国内 74% → 74% 基本未动** —— 预期内，印证「剩下的是国家级事实 + 方法论 + 计算器说明，
  正确修法是**合并**不是改写」。
- [x] **验收**：`npm run build` EXIT=0 九项全绿；`--diff` 报
  **「变更 499 = provider_sub，新增 0、删除 0」**（只波及品牌子页）；基线重建 702 文件。
- [x] **交付文档**：`esimsift-模板化分析-回应与整改.md`（含方法论纠偏与后续 P1–P3）。

- [x] ~~**P1 国家页安装说明**~~ 第四十七轮完成：三步列表 → 一句 + 链到 `/guides/how-to-install-esim/`
- [x] ~~**P1 建 `/methodology/` 权威页`~~ **本条是误判 —— 该页早已存在且被 699 页链接/1679 处**（第四十七轮复核更正）
- [x] ~~**P2 品牌 Hub** 两条零信息句~~ 第四十七轮完成：改为 `Quoted from {brand}'s own published policy…`
- [x] ~~**P2 对决页** `The gap flips by destination…`~~ 第四十七轮完成：改为实际最大价差国（`$rows` 现算）
- [x] ~~**P3 跨模板统一**：`Price is only half of the decision.`（子页）vs `…half the decision.`（Hub）~~ 第四十七轮消解（Hub 那句已换掉）
- **不做（附理由）**：不给方法论句做措辞变体（minor variations）；不按品牌改写国家级事实（八品牌 `networks` 完全一致，只能编造）

### P-C 上线前
- [ ] privacy/terms 法律审校（**2026-10-07**：正文里的 `Todo:` 行已移入 front matter 注释，页面不再渲染待办文字；法律审校本身仍未做）
- [ ] GA4 ID 替换 + 与 roamiapp.com 跨域衡量（head.html 占位注释处）
- [ ] OG 图片（每国一张，含最低价数字）
- [ ] 部署（Cloudflare Pages 建议；`/go/` 边缘函数跳板可后加）
