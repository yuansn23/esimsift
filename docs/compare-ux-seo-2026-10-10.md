# /compare/ 交互与对决页 SEO 治理 · 第七十八轮

日期：2026-10-10 ｜ 项目：esimsift.com（Hugo 0.159.1，en + de）
状态：**改动全部留在工作区，未 commit、未部署**。构建 12 项产物闸门 + 2 项新增源码闸门全绿。

---

## 0. 一句话结论

本轮按「导航 hover → 对决页过滤/决策路径 → 品牌页过滤 → 仓库卫生 → 同质化治理」五条线落地。
**关于「已发现，尚未编入索引」：实测证明这些对决页不是逐字复制粘贴型同质化，真正的机械病灶是
站内可达性 —— 45 个对决页里有 39 个全站只有 49 条入链（其余 6 个有 646 条），已修到 45 页全部 646 条。**

---

## 1. 七项诉求 → 落点与产物证据

| # | 诉求 | 改动文件 | 产物级证据（可复跑） |
|---|---|---|---|
| 1a | 导航 hover 出品牌对决并可点击 | `layouts/partials/nav-matchups.html`（新）、`layouts/partials/header.html`、`i18n/{en,de}.toml` | 45 个对决页逐页扫描：导航内对决链接 **44/45 个不同 URL + 1 个「全部对决」入口** = 45 条；面板 3 列网格 + `All N matchups →` |
| 1b | 删掉 `/compare/matchups/` 的「Compare country by country」整块 | `layouts/compare/matchups.html`、`assets/css/main.css`、`i18n/{en,de}.toml` | 产物内 `matchup-more` 命中 **0**；4 个死 key 已删，`.matchup-more` CSS 整段删除（`main.css` 10582 → 10001 bytes） |
| 2 | matchups 页内容单薄 | 同上 | 新增 10 行品牌战绩榜 + 4 条 FAQ + `ItemList` + `FAQPage` 结构化数据；正文词数 1945 → 2397（中位） |
| 3a | 胜者徽章点击跳到 `/compare/{国家}/{品牌}/` | `layouts/compare/vs-single.html` | 45 页逐行核对：**行数 = 胜者链接 + 并列徽章**，零例外；链接目标全部存在 |
| 3b | 对决页加「按国家 + 按 GB」过滤 | 同上、`layouts/partials/vs-agg.html` | 45 页均有 `#vs-country-filter` + 8 档数据量 chip + 计数模板；每行带 `data-name/data-agb/data-bgb`；档位只渲染真实有货的桶 |
| 4 | `/compare/{国家}/{品牌}/` 加「按 GB」过滤 | `layouts/compare/provider.html` | 499 个子页：**chip 档位集合 == 该页实际有货的档位集合**（零假档位）；499 页全部有数据量控件 |
| 5 | 垃圾文件不进 GitHub | `.gitignore` | 索引 2664 → **2041**（暂存删除 623 条）；`.buildlog` / `public` / `_competitors` / `_net_results` / `docs/internal` 跟踪数 **全部为 0**；根级只剩 9 个被跟踪文件 |
| 6 | 「已发现未编入索引」是否同质化所致 | 本轮新增的两支探针 + `footer.html` | 见 §2（量化结论）与 §3（修复） |

### 关于第 3a 项的额外交付（决策路径）

原表格 「Cheaper entry」列只是一个静态徽章文字。现在：
- 唯一赢家 ⇒ 徽章变成**链接**，指向 `/compare/{国家}/{赢家}/`（读者下一步真的想看的页面）；
- 并列 ⇒ 保持无链接的 `tie` 徽章（**不给错的一页发链接**）；
- `aria-label` 服务端渲染整句（`See {brand} plans for {country}`），德语走 `name_acc` 宾格。

### 关于第 3b / 4 项的口径

数据量过滤是**预算型需求**，用区间（左开右闭）而不是 `≥`；`gb = 0` 只进「无限」桶，>20GB 归 `20p` 桶。
对决页每行是「两家各自的入门价」，读者要买哪家未知 ⇒ **任一方入门套餐落进区间即命中**，该口径写在 `aria-label` 与页内小字里；chip 文案复用既有 `compare_single__size_*` key（同一事实不留第二份译文）。

---

## 2. 对决页同质度：先纠正口径，再给结论

### 2.1 骨架口径会骗人

「抹掉数字与品牌名后还剩几种句子骨架」这个口径必然虚高 —— programmatic SEO 的数据驱动句在骨架层一定同形
（`X is cheaper than Y in N of M countries` 抹掉变量后只剩一句）。实测：**骨架重复率 93.4%**，但这不是缺陷。

Google 文档里的 *minor variations* 指**正文文本本身逐字相同**，只是换了城市名/关键词。
所以真正的判据是**逐字相同的句子**。本轮新增 `.buildlog/p78_vs_dup_probe.py` 同时给出两个口径：

| 指标 | 改造前 | 改造后 | 变化 |
|---|---|---|---|
| 正文（`<main>`）逐字句 总数 | 1877 | 2012 | +135 |
| 正文逐字句 去重 | 999 | 1070 | +71 |
| **正文逐字重复率** | 46.8% | **46.8%** | ±0 |
| **全站 ≥40 次逐字复制句** | 16 | **16** | ±0 |
| **只出现 1 次的逐字句**（真正独占） | 963 | **1021** | **+58** |
| 正文骨架 去重 | 124 | 185 | +61 |
| 骨架重复率（辅口径） | 93.4% | **90.8%** | −2.6pp |
| 只出现 1 次的骨架 | 66 | **112** | +46 |

**去重后 96.4% 的句子是「全站只出现一次」的**，每页独有句中位 42 → 48 条。
⇒ 这些页面**不是**逐字复制粘贴型同质化。

### 2.2 那 16 条逐页复制句是什么

回查 i18n 后发现构成是：
- **6 条是站内共用控件/披露**（对比构建器、条形图图例、方法/披露链接）—— 逐页相同**是正确的**，不应改；
- **10 条是说明句与 FAQ 答案**（表格用法说明、退货/优惠/网络等问答）—— 可以继续数据化，但收益递减。

### 2.3 真正的机械病灶：站内可达性

| 指标 | 改造前 | 改造后 |
|---|---|---|
| 对决页入链页数 min / 中位 / max | 49 / 49 / **646** | **646 / 646 / 646** |
| 属于「孤岛」（只有 49 条入链）的对决页 | **39 / 45** | **0 / 45** |

根因是 `layouts/partials/footer.html` 里**写死的 6 组「Popular matchups」**出现在**每一页**的页脚 ——
于是那 6 个对决页各拿到 646 条入链，其余 39 个只从自己的兄弟页拿到 49 条。
这直接对应 Google 的「已发现，尚未编入索引」：页面被 sitemap 声明（Discovered）但站内几乎无路可达（优先级/信号不足）。

**修复**：页脚改为**上下文相关**（当前对决页 → 同品牌的其他对决；品牌页 → 该品牌的对决；其他页 → 兜底 6 组），
并复用与导航同一个真源 `partials/nav-matchups.html`。现在 45 个对决页入链完全拉平。

### 2.4 其余 SEO 信号（改造前已达标，未动）

| 项 | 值 |
|---|---|
| title 唯一性 | 45 / 45 |
| H1 唯一性 | 45 / 45 |
| self-canonical | 正确 |
| robots | 无 meta（可索引） |
| hreflang | 3 条 |
| 正文词数 min/中位/max | 1912/1945/1987 → **2359/2397/2435** |

---

## 3. 本轮新增的两个**构建前**闸门

一次全量构建 ≈ 11–12 分钟。本轮撞了两次「改文案 → 等 11 分钟 → 才在末端报错」，
所以按项目既有纪律（「判据必须前移到源码/数据层」）把两条判据前移，接进 `npm run validate`（秒级）。

### 3.1 `scripts/check_printf_arity.py` —— i18n 调用契约

**为什么**：本轮在 matchups 的 FAQ 里写了 `printf (i18n "…") $total`，而那条 i18n 值**一个 `%` 占位符都没有**，
Go 把多余实参打印成 `%!(EXTRA int=45)` 并**印到读者页面上**（4 个页面）。格式串住在 `i18n/*.toml` 的值里、
实参个数住在 `layouts/**` 里 —— 这条跨文件契约此前无人守。

**判据**：
1. `printf (i18n "K") A1…An`：K 的值（每种语言）里 Go 格式动词个数必须等于 n；
2. 值里出现**非格式动词的裸 `%`**（如 `20% off` 被当格式串）报错；
3. `i18n "K" (dict …)`：模板必须覆盖**该 key 各语言占位符的并集**，否则会印 `<no value>`；
4. 各语言占位符集合**互不相同不报** —— 德语要 `country_acc`/`country_dat` 的格变化，这是刻意设计。

**校准过程（值得记住）**：第一版把「多传 dict 键」一律判为漂移，在 `provider.html` 上误报 **160 处** ——
那 160 处全是德语格变化的按需供给。改成「任何语言都没用到才算冗余」后降到 55 处真冗余（非阻塞 WARN）。

**自检**：正例 10 / 硬反例 9 / 软反例 2，共 21 项两侧都证（`未被正确处理的情形: 0`）。
正式扫描：**ERR 0 / WARN 55**（WARN 是「模板传了任何语言都没用到的 dict 键」，Go 静默忽略，无可见缺陷）。

### 3.2 `scripts/check_headings_source.py` —— h2/h3 标点

**为什么**：本轮新加的一条德语 H2 里带逗号，跑满一次构建后才在 `check_headings.py` 报 `bad: 45`。
`check_headings.py` 是**产物级**守卫，只能事后发现。

**判据**：从 `scripts/lang_rules.py` 读同一份语言规则（**不抄第二份正则**）：
en 禁 `, ; : — –`、de 等语言禁 `, ; :`；来源三处 —— `<h2>/<h3>` 块内的 i18n key、`$xH2 = i18n "…"` 的间接赋值形态、`content/{lang}/**/*.md` 的 Markdown 标题。

**边界（写在 docstring 里）**：值里的 `{{ .x }}` 占位符**代入后**才出现的标点、以及数据层国名/品牌名带进来的标点，本脚本看不见 ⇒ **产物级 `check_headings.py` 必须保留**。

**自检**：4 组正反例 + 模板侧识别（含 H1 不参与）共 5 项全过；正式扫描 **0 处违规**（与产物级 `bad: 0` 一致）。

---

## 4. 本轮踩到并已写进纪律的坑

1. **「一句话」只能有一个句号**。把段落前半句做成数字驱动、留后半句静态 ⇒ 后半句仍是一条 45× 复制句（探针按句末标点切句）。本轮栽了两次。
2. **改文案前先预测分散度**，别用构建试错：`.buildlog/p78_sentence_variance.py` 从**当前产物转录**数字，比较候选变量集的去重数后一次改对。
3. **断言脚本的反例必须真的注入到判据所在的位置**：⑦ 的「删一个并列徽章」删到了别的模块（MISS）、⑩ 的正则缺 DOTALL 导致反例未生效（`assert t2 != orig` 才暴露）。
4. **量纲不能混**：战绩榜的「对战数」是场次、赢/输/平是国家数之和，两者不可相加；正确的不变量是「Σ赢 = Σ输」「Σ平为偶」「Σ对战数 = 2×场次」+ 一条**跨源对账**（Σ(赢+输+平) = 2 × 45 张对决页行数合计 = 4482）。
5. **Python 非 raw 字符串里的 `\$` 是非法的**：`SyntaxWarning` 之后原样写进 TOML → `validate` 直接报「无法解析的 TOML 值」。
6. **selftest 会复制整棵产物树并逐条全树扫描**，别与全量构建并行（会互相拖慢、快照还可能不完整）。

---

## 5. 产物级验证（全部现算，非转录）

| 验证 | 结果 |
|---|---|
| 全量构建（`npm run build`，`.buildlog/build_r78e.log`） | `EXIT=0`；`stamp` 无改动（数据没变，日期保持不动）；`validate` 0 error；hugo `Total in 416976 ms`；`check:output` 12 项全绿 |
| `check_headings.py` | `checked 1291 html files, 33248 h2/h3, bad: 0` |
| 产物断言 `.buildlog/p78_assert.py`（10 条） | **合计问题 0**；含跨源对账 `Σ(赢+输+平)=4482 = 2 × 2241 行 ✓` |
| 断言自检 `--selftest` | **正例 10/10 全绿（0 误伤）+ 反例 18/18 全被抓（`MISS` 0 次）**；逐条隔离注入、每条独立还原后重跑，见 `.buildlog/p78_selftest4.log` |
| 同质度双口径 `.buildlog/p78_vs_dup_probe.py` | 见 §2.1 |
| 厚度与内链 `.buildlog/p78_vs_seo_probe.py` | 词数 2359/2397/2435；**英语侧**入链 646/646/646（口径见 §5.1）；title、H1 45/45 唯一 |
| 回归基线 | 已刷新（`generated_at` 09:02:32Z → **10:57:47Z**，1291 文件、13 类页型不变）；`--diff` → **变更 0 / 新增 0 / 删除 0** |

### 5.1 独立第二来源复核（`.buildlog/p78_side_probe6.py`）

单个断言脚本的结论不够 —— 本轮另跑一支**完全独立**的探针，判定规则**全部从源码读出**（不靠印象猜），
结果 `EXIT=0`、**0 条问题**：

| 检查面 | 覆盖 | 结果 |
|---|---|---|
| provider 页 数据量 chip | 994 页（渲染了过滤栏的） | chip 集合 **==** 页面真实桶集合 |
| provider 页 天数 chip | 994 页 | chip 集合 **==** `$dayOpts` 规则算出的集合，且 **⊆ 真实有效期档位**（绝不点到不存在的档） |
| provider 页 过滤栏守卫 | 998 页 | 渲染 **⟺** 套餐数 > 3；`fiji/saily`、`fiji/ubigi` 各只有 3 条 ⇒ 不渲染（**设计如此**，非缺失） |
| 对决页 数据量 chip | 90 页 | chip 集合 **==** 两国入门套餐的真实桶**并集** |
| 对决页 胜者徽章 | 4482 行 | 胜者 4318 + 并列 164 **= 4482**；胜者链接**同国同品牌**、并列行**无链接** |
| 对决页 计数文案 | 90 页 | `#vs-note` 与页头徽章里的数字 **== 真实行数** |
| matchups 页 | 2 页 | 旧块残留 0；`ItemList` + `FAQPage` 俱在 |
| 导航面板 对决链接 | 1290 页（en 645 + de 645） | 每页**恒 45 条**；**语言前缀错误 0 处**（德语页全部 `/de/compare/…`） |
| 页脚 对决链接 | 1290 页 | 每页**恒 6 条**；**53 种不同组合**（改造前是写死的同 1 组）；语言前缀错误 0 |
| 45 个对决页 全站入链 | 45 页 | **最少 1388 / 中位 1590 / 最多 1812**；**零孤岛** |

**★ 这支探针前 5 版全部报假红，逐条查明全是探针自己的错**（产物一直是对的）：

1. chip 我按 `id="…-X"` 猜 —— 真实是 **`data-sz="…"`** ⇒ 第 1 版的「档位集合种类数 = 1」是**全部空集的假通过**；
2. 天数 chip 我按「页面里出现过的天数」判 —— 真实规则（`provider.html:131-146`）是 `$tiers` 去重后**超过 12 档就换成阶梯**；
3. 徽章类名 `badge bg-brand-50 text-brand-700` **被复用**（页头 `<span>` 也是它，只是不带 `href`）⇒ 全页计数恒多 1；
4. 一行里「Airalo from / Roami from」**两格本身也是链接**（这正是本轮要的决策路径）⇒ 胜者徽章必须限定在**第 4 个 `<td>`** 内判定；
5. 我的计数正则写了英文 `countries` —— 德语页是 `Länder` ⇒ **探针也不许有英文硬编码判据**（与守卫同一条纪律）。

⇒ 再次印证红线 94：**假红比漏检更危险** —— 它会引你去改本来正确的产物。
**规则只能从源码读出来**，凡「按印象猜」的判据都要先拿真实仓库校准。

**★ 内链口径说明（避免下轮误读）**：`p78_vs_seo_probe.py` 的正则要求 `href="/compare/` **紧跟**，
`/de/compare/…` 因此不计入 ⇒ 它报的 **646 是「英语侧入链页数」**；
`p78_side_probe6.py` 与本次全站计数含 en + de 两棵树 ⇒ **1388–1812 是「全站入链次数」**。
两者不矛盾（645 英语页导航 + 645 德语页导航 ≈ 1290，再加两侧页脚即 1388+）—— **引用时必须带口径**。

---

## 6. 未完成 / 待你决策

1. **未 commit、未部署** —— 按你的要求，改动全部留在工作区（+ 623 条已暂存的删除）。
2. **`.buildlog/` 仍在仓库目录内**（已被 `.gitignore` 忽略，跟踪数 0，不会再进 GitHub）。
   若你想让它物理上离开仓库根，需要一并改我那些脚本的相对路径 —— 说一声我就搬。
3. **`scripts/_*.py` 里约 50 个一次性补丁/对账脚本**（如 `_patch_de_*.py`、`_compare_de_*.py`）也在 `scripts/`，
   会被提交。其中 `_de_schema_audit.py`、`_de_link_leak_audit.py` 是**构建闸门**不能动，其余可归档到 `docs/internal/scratch/`。**要不要清？**
4. **残留 10 条模板说明句 / FAQ 答案**可以继续数据化（收益递减），要做我就按 §4 第 1、2 条流程做。
5. **德语**：本轮新增的两句德语文案已避开「介词支配国名」（数据层没有与格）的陷阱，但**全站德语译文仍未经有资质审校** —— 这是本项目唯一的能力缺口。
6. **既有的一处同义重复（登记不擅自改）**：`content/en/compare/matchups.md` 正文写
   "One page per pair, one verdict per page: every matchup below is **computed from the same dated price snapshot, country by country**, with no editorial adjustment."，
   而图表 `<figcaption>`（i18n key `compare_matchups__every_matchup_verdict_is_computed_country_by_country_fro`）写的是
"Every matchup verdict is **computed country by country from the same dated price snapshot**." —— 两句近乎同义。
   英语侧正文自 **2026-10-02** 就在（本轮未改），德语版是本轮新译 ⇒ **顺手把它译进去等于把重复也复制了一份**。
   修法（一行）：把 `figcaption` 改成描述图表本身读法（例如「每一格 = 两国入门价之差」），别再复述口径。
   它**不是 SEO 违规**（页内重复 2 页 ≪ 阈值 40，且 96.4% 的句子仍全站唯一），故未在你没点名时擅自改。
   —— **要不要顺手改掉？**
---

# 第七十九轮追加：Versus 下拉收窄为 6 组编辑精选（2026-10-10）

## 7.1 诉求与落点

> 「Versus 下的品牌对比，只需要 airalo 对 holafly / airalo 对 yesim / airalo 对 nomad /
> airalo 对 saily / airalo 对 jetpac / airalo 对 roamic，只需要这几个。」

| 项 | 落点 |
|---|---|
| 精选清单（唯一真源） | **新建** `layouts/partials/nav-matchups-featured.html` —— 6 个**页面 slug 全形**，从 `partialCached "nav-matchups.html"` 的 45 组里按 `printf "%s-vs-%s" .ka .kb` 命中 |
| 面板本体 | `layouts/partials/header.html`：`w-[36rem]` → **`w-[26rem]`**、`grid-cols-3` → **`grid-cols-2`**、计数取 `$vsItems`（= 6）、尾链取 **`$vsAll`**（= 45） |
| 全量 45 组 | `nav-matchups.html` **一字未动** —— 页脚上下文推荐 + `/compare/matchups/` 枢纽页仍用全量 |

★ **收窄导航 ≠ 删页**：未被精选的 39 组仍在 sitemap、枢纽页、以及页脚的上下文推荐里，
所以不存在「菜单里看不见 = 站内不可达」的问题。

## 7.2 产物级证据（全部现算）

| 判据 | 结果 |
|---|---|
| 面板对决链接数 | **1290 / 1290 页恒 6 条**（另 1 页 `/en/index.html` 是无 `<nav>` 的 meta-refresh 别名壳） |
| 链接集合 | **全站只有 1 种**，出现 1290 次，顺序正是指定的 6 组 |
| 面板可见数字 | 恒 **{6, 45}** —— 菜单计数 6、尾链「All 45 matchups →」/「Alle 45 Duelle →」 |
| 语言前缀 | **0 处错误**（en 页全 `/compare/…`，de 页全 `/de/compare/…`） |
| 枢纽页 | en / de 各仍列 **45** 组 |
| 页脚 | **53 种**上下文组合、每页 6 条（第七十八轮的修法未被削弱） |
| 45 组全站入链 | **min / 中位 / max = 98 / 300 / 1812**，**零孤岛** |

⚠️ **必须说清的代价**：第七十八轮那 45 页的入链是 **1388–1812**（导航在每页都给全部 45 组一条），
本轮导航只给精选 6 组 ⇒ **未被精选的 39 组入链降到 98–300**（页脚 + 枢纽页 + 卡片）。
98 条站内入链对 Google 足够（且零孤岛），但**这是收窄菜单的必然代价**，若日后 GSC 仍显示
「已发现，尚未编入索引」，第一顺位动作就是把精选清单加回几组，**而不是去改文案**。

## 7.3 逐字节归属：不跑第二次全量渲染也能证明「零外溢」

本轮只动了 1 个模板文件的 1 个区域。归属判据（`.buildlog/p79_attribution.py`）：

> 把新产物里那段 Versus 面板**还原成改动前的渲染形态**（45 组 / `w-[36rem]` / `grid-cols-3` / 计数 45），
> 整页 sha256 应当等于第七十八轮基线 `docs/regression-manifest.json`。

**结果：1291 / 1291 页全部相等**（有面板 1290 页走还原路径，别名壳 1 页原样比对）。
⇒ 改动被完全限制在面板区域内，**页内其余部分零漂移**。

与 `verify_no_regression.py --diff` **互为交叉验证**：变更 **1290**、新增 **0**、删除 **0**，
未变的正是那 1 个重定向壳 —— 两把尺子给出同一答案。随后刷基线（旧 `10:57:47Z` → 新 **`14:02:33Z`**，1291 文件，纯 LF）。

★ 还原所需的文案与顺序**全部从真源读**（`data/providers.toml` 的字母序两两组合 + `i18n/*.toml` 的
`g_vs` / `head_to_head_pairs` / `every_pair_note` / `all_matchups`），**不手抄** —— 否则「相等」只证明我抄对了。

## 7.4 本轮踩的三个坑（都已写进 PROJECT.md 红线 98/99/100）

1. **☠ 静默降级**：精选清单第一版写成 `airalo-holafly`，而比对串是 `printf "%s-vs-%s"` 产出的
   `airalo-vs-holafly` ⇒ 6 组**全部匹配不上**，partial 返回空切片，`{{ if gt (len $vsItems) 0 }}`
   走 `{{ else }}` ⇒ **Versus 菜单变成一个单链接，Hugo 一声不响**。
   修法：清单写**页面 slug 全形**，并在 partial 里 `errorf` 断言「匹配数 == 清单数」
   （已验证：把一个组合改成不存在的 `airalo-vs-ubigi` ⇒ `HUGO_EXIT=1` + 明确报错）。
2. **☠ 结构边界用错了层**：切面板时用「面板起点 → 本段 `</nav>`」，而 Versus 后面**还挂着
   Tools / eSIM deals / Guides（自带大菜单）/ Network map / Research** ⇒ 切出来的「面板」混进半个导航，
   数字判据被别的面板污染（数出 `0`、`26` 这类 **class 里的数字**）。
   正解：**`<div>` 深度配平**。
3. **`errorf` 的效果不能靠猜**：第一次验证时我拿 `[baseURL: "…"]` 当 TOML 写（非法）⇒ 构建本来就会失败，
   「`errorf` 生效」是**假结论**。改成合法 `baseURL = "…"` 后重测，才真正证到 `HUGO_EXIT=1`。

## 7.5 仓库卫生问答（关于 `.buildlog` / `scripts`）

| 目录 | 能否在 git 时整目录排除 | 依据 |
|---|---|---|
| `.buildlog/` | ✅ **能** | 已被 `.gitignore` 忽略，**被跟踪文件数 0**（物理 866 MB，纯构建日志与对照快照） |
| `scripts/` | ❌ **不能** | `package.json` 的 `build` / `validate` / `check:output` / `stamp` / `dev` 共引用 **23 个**脚本（含传递 `import`）。排除后**新克隆一条命令都跑不了** |
| `scripts/scrape/` | ❌ **不能**（曾被误判为垃圾） | 519 个被跟踪文件 / 7.8 MB，是**数据管线的采集工具 + 原始抓取证据**：`PROJECT.md` 明写「`scrape/raw/` 原始抓取 JSON（证据留存，勿删）」，`data/plans/*.toml` 由 `toml_write.py` 从 `raw/<brand>/` 生成，改数据走「重抓 → 重转」 |

**本轮真正清掉的垃圾**：`scripts/__pycache__/backfill_networks.cpython-314.pyc`（1 个，8 KB）
—— 已在 `.gitignore` 补 `__pycache__/` + `*.pyc` 并 `git rm --cached`，`scripts/` 下 pyc 跟踪数 **0**。

**构建链必需的 23 个脚本**（`scripts/` 里其余 101 个是一次性脚本，理论上可排除、但体积极小且是历史审计记录）：
`validate.py` · `check_css_sync.py` · `check_i18n.py` · `check_printf_arity.py` · `check_headings_source.py` ·
`check_output.py` · `check_headings.py` · `verify_provider_pages.py` · `check_faq_facts.py` · `check_dates.py` ·
`check_hreflang.py` · `check_article_agreement.py` · `verify_de_text.py` · `verify_de_data.py` ·
`verify_no_regression.py` · `stamp_checked.py` · `_de_schema_audit.py` · `_de_link_leak_audit.py` ·
`lang_rules.py` · `bump_checked.py` · `_loc_de_dates.py` · `i18n_extract.py` · `unlimited_labels.py`
