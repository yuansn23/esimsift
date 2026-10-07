# 新增品牌（BNESIM / GigSky / Jetpac / Nomad）× 50 国 —— 影响面分析与实施方案

> 起草：2026-10-06 · 状态：**Nomad ✅、Jetpac ✅（2026-10-07 落地并验收通过），gigsky / bnesim 待接**（见 §7 / §8）
> 数据源：`D:\esimsift\esimsift\_competitors\_competitors\raw\{bnesim,gigsky,jetpac,nomad}\`
> 起草时基线（复核订正）：8 品牌 × 50 国 = 400 品牌子页 / **7,776** 套餐 / **584** 页（原稿写 8,776 / 582，均误）
> 现行基线（Nomad 接入后）：**9 品牌 × 50 国 = 450 品牌子页 / 36 对决页 / 8,218 套餐 / 643 页 / sitemap 585 URL**
> **现行基线（Jetpac 接入后，2026-10-07）**：**10 品牌 / 499 品牌子页（9×50 + jetpac 49）/ 45 对决页 / 9,095 套餐 / 702 页 / sitemap 644 URL**

---

## 0. 结论先行

**是"牵一发而动全身"，但动的是同一根轴：数据层。** 站点的模板几乎全是数据驱动的
（`range $d.providers` / `partial "country-stats.html"` / `partial "vs-agg.html"`），
所以**改动集中在 L1 数据层，L3 模板层大部分会自愈**。

真正"全身"的地方不是"要改几个模板"，而是**每个页面上的数字和结论都会变**：

| 会变的东西 | 为什么 | 波及面 |
|:---|:---|:---|
| 每国"谁最便宜" | 多了 4 个竞争者 | 50 国家 hub + 现有 400 品牌子页的排名/结论 |
| `#N of 8` → `#N of 12` | 排名分母 | 400 条 seo.description 全部重写（脚本） |
| "from 8 providers" | 国家页描述里的计数 | 50 条国家页 description（脚本） |
| 50 条国家页 title 的价格锚 | "From $0.36/GB" 由数据算 | 50 条 title 变（脚本） |
| 300 条国家 FAQ 的答案 | "最便宜的 eSIM 是 Roami…" / "All 10 unlimited plans" | 50 个 `data/faqs/*.toml` 事实过期 |

**页面量：582 → 约 821 页**（+197 品牌子页 / +38 对决页 / +4 品牌 hub）。

---

## 1. 现状盘点（已核实）

### 1.1 数据已经在本地备好了，但没接入站点
`_competitors/` 是**独立目录**（`_` 前缀，Hugo 直接忽略），`build_plans.py` 已把它们归一化成
项目 TOML 格式，但文件头自带一句声明：

> `# NOTE: this file is a SEPARATE capture set - it is not wired into data/plans/.`

| 品牌 | 来源 | 国家覆盖 | 套餐数 | 已归一化产物 |
|:---|:---|:---|:---|:---|
| Nomad | esimdb.com | 50 / 50 | 442 | `_competitors/plans/nomad.toml` |
| Jetpac | esimdb.com | **49** / 50（Fiji 空） | 877 | `_competitors/plans/jetpac.toml` |
| GigSky | esimdb.com | 50 / 50 | 619 | `_competitors/plans/gigsky.toml` |
| BNESIM | **bnesim.com 官方 API** | **48** / 50 | 528 | `_competitors/plans/bnesim.toml` |

配套资产也齐：品牌档案 `_competitors/brand/*.json`、促销 `_competitors/promos/*.json`（含各自折扣码）。

### 1.2 raw 目录里其实有 **9 个**品牌
`bnesim / firsty / gigsky / gomoworld / jetpac / maya / nomad / quibity / roamless`。
你这次点名 4 个（**注意：你写的是"3 个品牌"，但列了 4 个名字**）。

### 1.3 现有 8 品牌 / 50 国全覆盖
`airalo 985 / alosim 915 / holafly 298 / roami 1181 / roamic 1791 / saily 471 / ubigi 483 / yesim 1652`
= **8,776 条**，每品牌都是 50/50 国。

---

## 2. 影响面分级（"牵一发动全身"的逐条清单）

### L1 数据层 —— 改动的源头（必须手改）

| # | 文件 | 做什么 | 备注 |
|:---|:---|:---|:---|
| 1 | `data/plans/<brand>.toml` × 4 | 从 `_competitors/plans/` 落地 | 需 4 项清洗，见 §3 |
| 2 | `data/providers.toml` | +4 条顶层条目 | 必填 `name/tagline/type/founded/color/initials/strengths/weaknesses`（`validate.py` 会拦） |
| 3 | `data/providers.toml [x.info]` | +4 条 | hq / website / trustpilot / support / refund |
| 4 | `data/providers.toml [x.policy]` | +4 条 | 热点 / FUP / 充值 / voice —— **只填核实过的，未核实就不写**（模板会渲染 `Not checked yet`） |
| 5 | `data/providers.toml promo_*` | +4 条 | 缺了就上不了 `/esim-deals/` 的码榜 |
| 6 | `hugo.toml [params.outbound.targets.<key>]` × 4 | +4 条 | **全站唯一出站出口 `cta-out.html` 依赖它**，缺了 CTA 按钮无链接 |
| 7 | `data/plans/*.toml` 的 `networks` | 跑 `backfill_networks_uniform.py` | 铁律：`plans[ISO].networks` 恒等于 `countries[ISO].carriers` |

### L2 内容层 —— 脚本可批量重生成

| # | 目标 | 现状 → 目标 | 生成方式 |
|:---|:---|:---|:---|
| 8 | `content/en/compare/<国>/<品牌>.md` | 400 → **597** | ✅ 有生成器 `scripts/gen_provider_pages.py`（重建全部，自动清理失效页） |
| 9 | `content/en/compare/<国>.md`（国家 hub） | 50 条 description **全变** | ✅ 有生成器 `scripts/regen_meta_brand.py` |
| 10 | `data/titlesegments.toml` | 50 条 title **全变**（价格锚） | ✅ 有生成器 `scripts/_solve_titles.py` |
| 11 | `content/en/esim-providers/<品牌>.md` | 8 → **12** | ⚠️ 半手工：需新写 4 篇 hub 文案 |
| 12 | `content/en/compare/<a>-vs-<b>.md` | 28 → **66** | ❌ **没有生成器**，需新写一个（C(12,2)=66） |
| 13 | `data/faqs/*.toml` × 50（约 300 条） | 事实过期 | ❌ **最费人工的一块**，见 §3.4 |

### L3 模板层 —— 大部分自愈，少数要改

**自愈（数据驱动，零改动）**：
首页品牌墙、`/compare/` 枢纽的全部榜单、`/tools/` 品牌网格、`/esim-deals/` 码榜、
`/compare/matchups/` 对决索引、`/esim-providers/` 列表、各页计数徽章、面包屑、JSON-LD。

**必须手改的硬编码点（已 grep 定位）**：
- `i18n/en.toml` + `de.toml` 三处把品牌名写进了长句：
  `tools_list__two_brands_on_your_shortlist_every_pairing_airalo_vs_hol…`、
  `research_price_index__airalo_vs_holafly…`、`research_unlimited_esim__holafly_vs_airalo…`
- `esim_deals_list__params_verdict_body`：正文点名 Roami / Saily / Yesim 的码
- `compare_single__plans_are_delivered…`：点名 Roami 和 Saily
- 首页品牌墙是 `flex` 网格，8 → 12 个 logo 需目视确认换行不破版

### L4 校验/守卫层

| 脚本 | 影响 |
|:---|:---|
| `validate.py` | plans ↔ providers 对齐、vs 页字母序 —— 做对了就绿 |
| `verify_provider_pages.py` | 逐页检查，能自动扩到 597 页（docstring 里的"400"只是注释） |
| `verify_no_regression.py` | 全站不变量能跑，但**基线 manifest 必须重建**（几乎全站都会变） |
| `audit_meta.py` | title 全站去重 —— 新增 197+66 页后要重跑 |
| `check_dates.py` | 品牌列表从数据推导，自动适配；但品牌 hub 的 `dateModified` 需新品牌 `profile_checked` |
| `check_i18n.py` | 只要动 i18n 就必须 en/de 成对 |

### L5 页面量与 SEO

`582 → 约 821` 页；全站 title/description 大范围重算；`sitemap.xml` /
`catalog.json` / `llms.txt` 自动重生成（模板已动态 range，无需手改）。

---

## 3. 三个必须先解决的硬问题

### 3.1 ★ bnesim 是 **EUR** 计价
`build_plans.py` 自己标了：`# CURRENCY: bnesim API prices are EUR`。
现站 `price` 列是 **USD**，`/compare/` 的"最低入门价"、$/GB 榜、$/day 全部按下标比较。
直接落库会让 BNESIM 凭空便宜 ~8%。
**方案（三选一）**：① 按一个公开固定汇率换算成 USD 并在数据文件头记汇率与日期；
② 本期排除 bnesim；③ price 单元加 `currency` 字段（要改全站价格渲染，成本最高）。

### 3.2 jetpac 缺 Fiji、bnesim 缺 2 国
不影响正确性（生成器会跳过），但意味着**"12 家"不是普遍成立**——
好在所有计数都由数据推导，页面会自动显示真实数字。要确认的只是：这两个品牌在
缺失国家**不出现在任何 "N providers" 断言里**。

### 3.3 ★ 新数据里的 `United States` / `United Kingdom` 与现站口径冲突
第三十五轮已把全站统一为 **USA / UK**，现站 `data/plans/*.toml` 里 `United States` 出现次数 = **0**。
而 4 个新品牌的归一化产物里：nomad 11 处、gigsky 10 处、bnesim 10 处、jetpac 2 处。
**必须先跑改名再落地**（`scripts/_rename_us_gb.py` 可复用逻辑，套餐名那部分要单独处理）。
（非拉丁字符已检测：4 个品牌全部 clean，无反罗马化需求。）

### 3.4 50 个国家的 FAQ 事实会过期（最费人工）
例：`data/faqs/us.toml` 写着
- "**Roami** … 是最便宜的" —— 新品牌进来后可能易主
- "All **10** 'unlimited' plans here" —— 计数变了
- "Airalo or Holafly for the USA?" 这类二选一问答，面对 12 家已不完整

300 条逐条重写成本高。建议**规则化 + 脚本重算数字**，只人工过语义冲突的条目。

---

## 4. 实施方案（分 6 步）

### Step 0 · 冻结与净数据（不改站点）
- 停 dev server → `npm run build` → 存基线 `verify_no_regression.py --write-manifest`
- 4 个品牌的 plan name 做 USA/UK 改名 + 检查 `clean_plan_name` 口径
- bnesim 汇率定案
- 产出 `data/plans/{nomad,jetpac,gigsky,bnesim}.toml`（**先落在临时目录复核**）

### Step 1 · 数据层落地
- 4 个 plans 文件入库 + `backfill_networks_uniform.py`
- `providers.toml` +4 条（含 info / policy / promo_*）
- `hugo.toml` outbound targets +4 条
- `python -X utf8 scripts/validate.py` → 必须 0 error 0 warning

### Step 2 · 内容层批量重生成
- `gen_provider_pages.py` → 597 子页
- 新写 4 个 vs 页生成器 → 66 对决页
- 手写 4 篇品牌 hub（`content/en/esim-providers/*.md`）
- `regen_meta_brand.py` + `_solve_titles.py` → 国家页 meta/title 重算
- FAQ 数字重算 + 人工过语义冲突

### Step 3 · 硬编码点清理
- i18n 三处品牌名长句 → 品牌无关化或补新品牌（en/de 成对）
- 首页品牌墙 12 logo 版式核验

### Step 4 · 全量校验（`npm run build` **十项全绿** + 两个未进 build 的审计）

`npm run build` 本身已串入全部十项守卫（`validate` / `check_css_sync` / `check_i18n` / `check_output` /
`check_headings` / `verify_provider_pages` / `check_faq_facts` / `check_dates` / `verify_no_regression` + `hugo`），
**改完直接跑它即可**。下列两个不在 build 里（一个要网络、一个耗时），按需单独跑：
```
npm run build                        # 十项全绿（含 R10 骨架 / R11 邻国问答 / 日期口径）
scripts/audit_meta.py                # 全站 title/description 去重与长度
scripts/check_links.py               # 0 死链（新页 4 条入链路径）
scripts/verify_no_regression.py --diff docs/regression-manifest.json   # 先看变了哪些页
scripts/verify_no_regression.py --write-manifest                       # 确认无误后重建基线
```
外加三条自查：450 品牌×国家子页的 Offer 数 == 表格行数；`#N of 9` 全站一致；入链四条全通。

### Step 5 · 文档与记忆
`PROJECT.md` 覆盖表、`STATUS.md` 本轮节、`docs/keyword-map.md` 新品牌词归属。

---

## 5. 验收判据（一句话版）

1. `validate.py` 0 error 0 warning
2. 450 子页（9 品牌 × 50 国）+ 36 对决页 + 9 品牌 hub 全部有产物、0 死链
3. 全站 `#N of M` 的 M 与实际品牌数一致（分国家核算，jetpac/bnesim 缺国要正确少一）
4. `grep -c localhost public/llms.txt` == 0（部署前）
5. 反向测试：任一断言故意造违规必须失败

---

## 6. 待拍板

| # | 问题 | 选项 |
|:---|:---|:---|
| A | 品牌范围 | 只做这 4 个 / 把 raw 里其余 5 个（quibity、roamless、gomoworld、maya、firsty）一起做 |
| B | bnesim 的 EUR | 汇率换算成 USD / 本期排除 / 加 currency 字段 |
| C | 执行节奏 | 先做 1 个品牌（Nomad，50/50 数据最干净）打通全链路再批量 / 4 个一次性上 |
| D | FAQ 300 条 | 脚本重算数字 + 人工只过冲突条目 / 本轮不动 FAQ（接受短期事实过期） → **2026-10-07 第四十一轮已按"更彻底"的第四种做法解决：三条含数字的答案改成构建期现算（`{token}`），从此不存在"重算"这个动作，见 §7.5** |

---

## 6.1 拍板结果（2026-10-06）

| # | 决定 |
|:---|:---|
| A | **只做这 4 个**（bnesim / gigsky / jetpac / nomad），raw 里其余 5 家不做 |
| B | **统一 USD** —— bnesim 的 EUR 按汇率折算（汇率值与日期在接入 bnesim 时定并记录） |
| C | **Nomad 试点先行**，验收通过再批量上其余 3 个 |
| D | **本轮不动 FAQ**（99 条既有债见 §7.4，等单独一轮处理） |

另加一条执行口径：**国家名一律 USA / UK** —— 新数据里的 `United States` / `United Kingdom` 先改名再落地
（Nomad 已用 `_rename_us_gb.py` 处理 25 处）。

---

## 7. Nomad 试点结果（2026-10-06，已验收）

### 7.1 落地量

| 项 | 结果 |
|:---|:---|
| `data/plans/nomad.toml` | **442 条 / 50 国**（data 292 + unlimited 150；0 条 days≤0 / price≤0 / 坏名） |
| `data/providers.toml` | `[nomad]` + `[nomad.info]` + `[nomad.policy]` + `promo_*`（`BEYOND20` 20%，alt = FALL30 30% / ESIMDNOMAD20 20%） |
| `hugo.toml` | `[params.outbound.targets.nomad]`（**不配 `country_path`** —— 逐国 slug 口径与本站不对齐） |
| 页面 | 450 品牌子页 / 36 对决页（28 旧逐字节未动 + 8 新）/ 9 品牌 hub / 643 页 / sitemap 585 URL |
| 套餐总数 | 7,776 → **8,218** |

### 7.2 校验（九项全绿）

`validate` 0-0 ／ `OK: 645 files (643 pages), 3694 JSON-LD blocks` ／ `16291 h2/h3 bad: 0` ／
品牌子页 450/450（天数按钮无假档位 448/450）／ 政策未核实页 0 ／ A/B/C 全过 ／ `check_links` 168,632 href 坏链 0。

### 7.3 产物体量断言

footer 品牌链接 9 ／ 50 国 hub 品牌链分布 `{9: 50}` ／ **nomad 卡片 50 页去重 md5 = 50**（反同质化）／
50 国 hub 全链 nomad 子页 0 缺失 ／ matchups 去重对决链接 36 = 落地 36。

### 7.4 ★ 试点暴露出的 6 个隐蔽触点（这才是本轮的真正产出）

1. **零回归守卫 `verify_no_regression.py` 的 `BRANDS` 写死 8 家** → 新品牌子页掉进 `static` 兜底
   → **401 条假失败**。已改为从 `providers.toml` 推导 + 补 2 条分类自测。
   **通用规则：页型判据依赖的数据集变了，判据必须跟着变。**
2. **`toml_write.py` 的 `CHECKED` 是首批抓取日** → 新品牌补抓必须 `--checked YYYY-MM-DD`（已加），
   否则页面 / `dateModified` / sitemap 三处一起报旧日期。
3. **`_rename_us_gb.py` 会改 `data/plans/*.toml` 的套餐名**（`PLAN_RULES` + `PLAN_TARGETS`）——
   别按文档串猜它的作用域，**看代码**。
4. **元数据重建的真实改动面 ≈ 50 国家页 + 28 旧对决页 + 8 品牌 hub**；`regen_meta_brand.py` 报 82 个文件
   是可信的，但要逐条 diff 确认（不能只信计数）。
5. **国家页 title 的价格锚会因新竞争者易主**：`_solve_titles.py --write` 重算 50 条，**6 条变化**
   （AU/GB/SA/TH/US/ZA）—— 不做这一步，标题里的 "From $x/GB" 会是错的。
6. **i18n 里"按百分比枚举品牌"的手写句子会漏新品牌**：
   `esim_deals_list__params_verdict_body` 原列 "Saily's 25% and Yesim's 20%"，
   Nomad 的 `BEYOND20` 也是 20% 却缺席 → 已补（en/de 成对）。

### 7.5 FAQ 数字断言（**2026-10-07 第四十一轮已修**，不再是遗留）

`scripts/audit_faq_facts.py`（当时新写的一次性审计器，已删除）首跑：
**99 条断言过期** = `cheap_bad 49`（49 国「最便宜 eSIM 是 X、$Y」）+ `unl_bad 50`（50 国「All N unlimited plans」）。
**排除 Nomad 跑一遍仍是 99 条** → 改动前就全是过期的；Nomad 让其中 45 国的断言"发生变化"。
例：US FAQ 说 "Roami … $2.99 最便宜"（实际 Yesim $0.51）、"All 10 unlimited"（实际 94 条）。
该审计器还有个匹配缺陷：按 `q.startswith("What is the cheapest")` 匹配，**jp 的自定义问法被整条跳过**
（jp 写"$1.99 for 1GB over 7 days"，实际是 3 天）。

**修法（第四十轮列的三个选项之外的第 4 个，也是最彻底的一个）**：
不重算数字，而是让数字**不可能过期** —— 三条答案只留 `{token}` 占位，
值由 `layouts/partials/faq-live-tokens.html` 在构建期从 `data/plans` 现算；
新守卫 `scripts/check_faq_facts.py` 读**产物**独立重算对账（R1–R9，带 `--selftest`），已挂进 `check:output`。
**所以再接入 gigsky / jetpac / bnesim 时，FAQ 不需要任何人工动作** —— build 会自动对账；
只有"新品牌把某国最优解抢走后文案口吻想跟进"才是可选的润色（§7.1 PROJECT.md 遗留）。
唯一要留神的：jp 的 Q3 写死了「neither is the cheapest on this page」，
守卫 R8 会在最便宜品牌变成 Airalo/Holafly 时报错 —— 那时改文案，不要改守卫。

**补充（2026-10-07 第四十二轮）**：上述修法只解决了「**数字**会过期」，「**句架**仍重复」的问题在本轮一并解决 ——
49 国（jp 手写除外）三条答案各拆 open / body / close 三槽 × 每槽 7 片段，
用**拉丁方阵** `a = i % 7`、`b = i // 7`、`c = (a + b) % 7` 分配（i = ISO 升序位次）⇒ **任意两页最多共用一句**；
库 = `scripts/faq_frames.py`（三职合一：分配 / 迁移 / `--check` 离线断言）。
守卫加 **R10**（源级，判句架）+ **R11**（产物级，判 Q6 逐国不同），`check_faq_facts.py --selftest` 13 项。
**对「接入新品牌」的含义不变**：新品牌落地后 build 会自动对账，FAQ 同样**不需要人工动作**；
唯一新增的注意点是——**i 是按 ISO 升序位次算的，国家集合不变 ⇒ 分配不变 ⇒ 接品牌不会打乱句架**。
（若将来新增/删除**国家**，位次会整体位移，届时跑一次 `python -X utf8 scripts/faq_frames.py --force` 重刷全站并重建基线。）

### 7.6 Nomad 收尾：logo 归位 + 日期自动盖章（2026-10-07 第四十三轮）

| 项 | 结果 |
|:---|:---|
| **logo 归位** | 用户给的 `static/img/logo/` 只是**素材下载区**、不生效；已把 `nomad.png` 放到生效目录 **`static/img/providers/nomad.png`**（512×512 合法 PNG）。产物里 **603 页**已渲染真 logo、monogram `Nd` 残留 **0** |
| **价格核对日** | 50 国 `checked` 10-04 → **2026-10-07**（用户要求：数据驱动内容更新了，日期就得是当前系统日期）。四处同源已验：可见文案 `Prices checked Oct 7, 2026` / 子页 / JSON-LD `dateModified` / sitemap `lastmod` |
| **品牌档案日** | 保持 **10-06**（那是真核验日，不是本轮改的）。品牌 hub 的 `Last updated` = max(价格, 档案) = **Oct 7** ✓；`prices as checked on` 只取价格日 = **Oct 7** ✓（不对称口径仍成立） |
| **日期机制** | 新增 `scripts/stamp_checked.py`（按**内容指纹**自动盖章，已挂 `npm run build` 第一步，台账 `docs/checked-state.json` 必须提交）。**Nomad 之后再改数据，日期会自己跟上**，不用手跑 `bump_checked.py` |
| **变更面** | 627 页 = **603**（徽标 monogram → 真 logo）+ **24**（引用了 nomad 价格日的 guides/networks/research），**0 页未解释**；基线已重建（643 文件） |

⚠️ **接第二批品牌时必须注意**：
- **logo 只认 `static/img/providers/<key>.png|.webp`**。素材区：`gigsky.png` ✓ 待归位；~~`jetpac.webp`~~ ✅ 2026-10-07 已归位；
  `bensim.jpg` ✗ —— **品牌 key 应为 `bnesim`（当前素材文件名拼成了 `bensim`），且 jpg 探测不到**，
  须转 png/webp 并改名。（另注意品牌名不要与自家 `roami` / `roamic` 混淆。）
- **新品牌 TOML 入库后日期会自动盖当天**（`stamp_checked.py` 把台账里没有的单元当作「新入库」），
  **但首次建台账是例外**（保留现值）——所以第一次跑之前要确认 `toml_write.py` 的 `--checked` 传对了。
- **`--checked` 传 raw 的真实抓取日，不是「今天」**（jetpac 的 raw 是 10-04 抓的，写成 10-07 就是文件头印假日期）；
  之后再 `bump_checked --brand <b>` 把**页面声明的核对日**推到当天。同时在 `providers.toml` 给 `<brand>` 顶层写
  `profile_checked`（jetpac = 10-07）—— 品牌 hub 的 `Last updated` 取 max(价格日, 档案日)。
- **`backfill_networks_uniform.py` 是全局脚本**，不是「只补新品牌」：跑一次会把历史品牌遗留的空 `networks`
  一并补真（Jetpac 那次顺带修好了 nomad 的 `networks = []`，**单独实测影响 123 页**）。做变更面归因时要分开记账。
- **Jetpac 的官网是 SPA，深链不可用**：`/product-details/{slug}-esim` 对任意路径返回 **200**、标题由 slug 现场拼接、
  价格回落 $1 占位 —— 只有 `japan` 有真内容。**状态码不能当证据**。按 Nomad 先例**只走 base，不加 `country_path`**。

---

## 8. 剩余 2 家接入手册（按 Nomad / Jetpac 两次沉淀的完整顺序）

数据规模：**gigsky 50/50 · 619 条** ／ **bnesim 48/50 · 528 条（EUR，需 EUR→USD 折算并诚实披露口径）**。
（**jetpac ✅ 已于 2026-10-07 完成**：49/50 国 · 877 条 / 499 子页 / 45 对决页 / 702 页，实测步骤与坑见 §8 下方注释。）

每家按此顺序，**每一步都要过上一节的产物断言**：

```bash
# 0) bnesim 专有：EUR → USD 折算（先定汇率 + 汇率日期，写进 plans 文件头注释）
#    并在 providers.toml [bnesim] 记录折算口径（诚实披露）
# 1) raw JSON 进 scripts/scrape/raw/<brand>/（数量 = 覆盖国数：50/49/48）
python -X utf8 scripts/scrape/toml_write.py <brand> --checked <raw 的真实抓取日> --dry-run  # 确认 0 problems
python -X utf8 scripts/scrape/toml_write.py <brand> --checked <raw 的真实抓取日>
python -X utf8 scripts/backfill_networks_uniform.py                      # networks 补齐（⚠ 全局脚本）
python -X utf8 scripts/_rename_us_gb.py --dry-run && python -X utf8 scripts/_rename_us_gb.py
# 2) providers.toml 加 <brand> 块（含 info / policy / promo_*）+ profile_checked
# 3) hugo.toml 加 [params.outbound.targets.<brand>]
# 4) content/en/esim-providers/<brand>.md（title 48-54 无品牌词 / description 120-140 含 "eSIM Sift"）
# 5) gen_provider_pages.py → gen_vs_pages.py → regen_meta_brand.py → _solve_titles.py --write
# 6) npm run build → verify_no_regression --diff → --write-manifest
```

> **`--checked` 写抓取日，不写今天**（2026-10-07 踩过）：raw JSON 是 10-04 抓的，
> 却在 `--checked` 里传 10-07，文件头就印出「Scraped … on 2026-10-07」——**不实陈述**。
> 正确姿势：`--checked <raw 的真实抓取日>`（落文件头 + 块内初始值），
> 之后 `python -X utf8 scripts/bump_checked.py --brand <brand>` 把**页面声明的核对日**
> 推到当天。文件头 = 抓取日，块内 `checked` = 页面核对日，两者本来就不是同一个东西。

> **`backfill_networks_uniform.py` 是全局脚本，不是「只补新品牌」**（2026-10-07 实测）：
> 它按 `countries[ISO].carriers` 给**所有**品牌的 `plans[ISO].networks` 做统一回填。
> 接 Jetpac 时跑一次，把 nomad 此前遗留的 `networks = []` 一并补成了真实运营商 ——
> 这会让 nomad 的 50 个子页 `#hostnetwork` 从降级态变成正常渲染，**属于第二个变量**。
> 做变更面归因时必须把它和「新品牌接入」分开记账，否则会把 nomad 的改动算到 Jetpac 头上。

> **删品牌时必须同时清理对决页**（2026-10-07 实测）：`gen_provider_pages.py` 有陈旧子页
> 清理（`removed`），但**没有**清理 `content/en/compare/*-vs-*.md` 的逻辑。残留一个引用
> 已删品牌的 vs 页，hugo 不是静默降级而是**直接失败**：
> `ERROR compare/vs-single: unknown provider "x"` → `nil pointer evaluating interface {}.name`
> （`vs-single.html` 拿空的 `$pa` 去取 `.name`），整站构建退出码 1、产物写不全。
> 这是「fail loud」而非静默，但顺序上会让人误以为新品牌数据有问题。

**缺国必须正确传播**：jetpac 缺 Fiji、bnesim 缺 2 国 →
任何 `#N of M`、`from N providers`、"All N unlimited plans" 的 **N 要按国核算**，
不能让缺国页写出比实际多的竞争者数。接入后逐国核对一次
（`find public/compare/<country>/ -maxdepth 1 -type d | wc -l` 应等于该国实际品牌数）。

**三家都上完后的目标态**：12 品牌 / 597 子页 / 66 对决页 / 12 品牌 hub / sitemap ≈ 790 URL。
