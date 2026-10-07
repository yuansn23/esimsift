# `_competitors/` — 竞品采集数据（独立目录，不接入站点）

> ⚠️ **这个目录不属于 Hugo 站点。** 目录名以 `_` 开头，Hugo 会忽略它；
> 这里的数据**没有**写进 `data/plans/` 或任何现有文件。要上线需你手工合并。

采集时间：**2026-10-04**（第二轮扩展 4 个品牌）

## 品牌与数据来源

| 品牌 | 官网 | 官网能采吗 | 实际来源 | 国家覆盖 | 套餐数 |
|---|---|---|---|---|---|
| Nomad eSIM | nomadesim.com | ❌ 代理拦截（超时） | esimdb.com | 50/50 | 442 |
| Jetpac Travel eSIM | jetpacglobal.com | ⚠️ 仅 Japan 是真产品页 | esimdb.com | 49/50 | 877 |
| GigSky | gigsky.com | ❌ HTML 无套餐表 | esimdb.com | 50/50 | 619 |
| Quibity eSIM | quibity.com | ❌ SPA，无内嵌数据 | esimdb.com | 50/50 | 308 |
| **Roamless** | roamless.com | ➖ 未尝试（esimdb 已全） | esimdb.com | 50/50 | 1,304 |
| **GoMoWorld** | gomoworld.com | ➖ 未尝试（esimdb 已全） | esimdb.com | 50/50 | 200 |
| Maya Mobile | maya.net | ✅ **是**（Angular SSR 内嵌 JSON） | maya.net 官网 | 50/50 | 500 |
| **BNESIM**（= bensim） | bnesim.com | ✅ **是**（**公开定价 API**） | bnesim.com 官方 API | 48/50 | 528 |
| **Firsty** | firsty.app | ✅ 是，但只卖**全球统一价** | firsty.app 官网 | 全球 1 条 | 6 |

**合计 4,784 条套餐（9 个品牌）。**

## 目录结构

```
_competitors/
├── README.md              本文件
├── COVERAGE.md            品牌 × 国家 覆盖率矩阵（含缺口清单）
├── coverage.json          机器可读的覆盖率统计
├── plans/                 规范化后的套餐数据（项目 TOML 格式）
│   └── nomad.toml  jetpac.toml  gigsky.toml  quibity.toml  roamless.toml
│       gomoworld.toml  maya.toml  bnesim.toml  firsty.toml
├── plans_all.csv          扁平汇总表，4,784 行（UTF-8 BOM，Excel 可直接开）
├── brand/                 品牌档案（含 Trustpilot 占位）
│   └── nomad.json  jetpac.json  gigsky.json  quibity.json  roamless.json
│       gomoworld.json  maya.json  bnesim.json  firsty.json
├── raw/                   原始抓取留档
│   ├── nomad/ jetpac/ gigsky/ quibity/ roamless/ gomoworld/   每国 1 个 JSON（esimdb 卡片原文）
│   ├── bnesim/                          每国 1 个 JSON（官网 API 产品，含运营商）
│   ├── firsty/                          _global.json（全球统一价模型）
│   ├── jetpac_official/                 jetpac 官网 JSON-LD（仅 Japan 有效）
│   └── maya/                            每国 1 个 JSON（plans[] + 181 国运营商映射）
├── 抓取/构建脚本（见文末）
├── promos/                折扣码 / 优惠结构化数据（第三轮，见下节）
│   ├── README.md           promos 数据集 schema + 口径 + 刷新方法
│   ├── <brand>.json × 16   2026-10-04 快照：airalo holafly nomad jetpac gigsky
│   │                       quibity bnesim roamless gomoworld maya yesim
│   │                       ubigi alosim firsty roamic saily
│   ├── promos.json         全部品牌合并对象（brands[] + meta）
│   └── promos_all.csv      扁平行表，120 行（UTF-8 BOM）
├── _probe/                站点结构侦察产物（HTML 样本、探测脚本）
├── _probe_promo/          优惠码侦察（Playwright 渲染页 + 抽取脚本）
└── _superseded/           已废弃的旧脚本 + 一次性探针留档
    └── _probe_out_of_scope/   BNESIM/Firsty 的官网抓取原文（HTML、定价 API dump）
```

> **注意**：BNESIM / Firsty 的原始抓取件（`bnesim_pricing_api.json`、
> `firsty_home.html` 等）在 `_superseded/_probe_out_of_scope/`。
> `parse_bnesim.py` / `parse_firsty.py` / `stage_official_raw.py` 都指向这个目录。

## 数据格式

`plans/*.toml` 与你项目 `data/plans/*.toml` **同构**，可直接对照：

```toml
[US]
checked = "2026-10-04"
source = "esimdb.com"
url = "https://esimdb.com/usa/nomad"
networks = []

[[US.plans]]
name = "Local United States - 30 Days - 5 GB"
gb = 5
days = 30
type = "data"          # data | unlimited
price = 10.00
```

字段说明：

- `gb` — 总流量。日包已换算为总量（`1GB/Day × 7 天 → gb = 7`）；`days = 0` 表示**无固定有效期**（Roamless 的 No-Expiry、BNESIM 的 `duration = -1`）
- `type` — `data` 或 `unlimited`
- `price` — 挂牌价（未计折扣）。**货币见 CSV 的 `currency` 列**：esimdb 与 maya 为 USD，`bnesim` / `firsty` 为 **EUR**
- `fup_note` — 限速说明，如 `2 GB per day for 7 days`
- `networks` — 该品牌在该国的运营商。**maya 与 bnesim 有**（官网内嵌/API 返回真实运营商名）；esimdb 不暴露运营商，故为空数组
- `source` / `url` — 溯源，便于复核

## 数据清洗规则

1. **只保留有价格的套餐**。esimdb 页面会混入无价格的导航/区域卡片（如 gigsky 页的
   `United States` + `100MB` + 无价），已剔除。
2. **合并纯外观重复项**。去重键 = 归一化名称 + 天数 + 价格。例如 maya 的
   `3 Days - Unlimited Global Data` 与 `3 Days Unlimited Global Data`（同价）合并为一条；
   名称相同但**价格不同**的保留为独立行（属不同 SKU）。
3. **日包换算**：`1GB/Day` 型 → `gb = 单价 × 天数`，并在 `fup_note` 记录原始口径。
4. **无限量**：`type = "unlimited"`，`gb = 0`。

## 已知缺口

- **Jetpac / Fiji**：esimdb 返回 404，jetpac 官网也无 fiji 产品页 → 两边都没有，故 49/50。
- **BNESIM / 中国香港 + 中国澳门**：只有区域包，没有单国产品 → 48/50（区域包留档在 `raw/bnesim/<slug>.json -> regional_options`）。
- **Nomad 官网**：本环境所有出网流量走代理（`127.0.0.1:61157`），`nomadesim.com` 超时，无法直采。
- GigSky / Quibity 官网虽有页面，但套餐由客户端 JS 渲染，HTML 里无结构化数据，按你允许的规则退回 esimdb。
- **Firsty**：官网只公开定价模型（Free / Classic / Unlimited）、底价与少量样例价，**完整 GB 阶梯仅在 App 内** → 只有 6 行，未做任何推断。

## Maya 的特殊说明

Maya 只卖一个**全球无限量**产品，所以 50 个国家页上的套餐阶梯完全相同
（`3/7/14/30 天`，USD 9.99 / 19.99 / 27.99 / 49.99），另有 Global + Cruise 档。
差异体现在 `networks` 字段 —— 那是 Maya 官网内嵌的**真实逐国运营商**。

## BNESIM（= bensim）的特殊说明

esimdb 上**没有**这个品牌（`/usa/bensim` → 404）。它是 **BNESIM**（BNESIM Limited，
中国香港），官网是 Gatsby SPA，HTML 里没有价格；但套餐由**公开无鉴权 API** 下发：

```
https://api.bnesim.com/v0.1/sim_card_landing_pricing/
```

一次返回 1,771 个产品（`amount / unit / price / duration / coverages / carriers /
networks / networkSpeed`），因此数据比 esimdb 更全——**含真实运营商名**（如 JP →
`KDDI`），可直接喂 brand-network 管线。

- 价格币种：**EUR**（API 固定 EUR，与展示货币无关）。
- `duration = -1` 表示**未标注固定天数**，写入 `days = 0`。
- 香港/澳门无单国产品，仅区域包。

## Firsty 的特殊说明

Firsty 卖的是**一份全球统一价目**（"Same price, every country"），
55 个国家页只是复述同一模型，**没有逐国定价**：

| 档位 | 计费 | 起价 |
|---|---|---|
| Free | 看广告解锁 | €0（~20 MB @ 1 Mbps，可叠加，7 天有效） |
| Classic | 按 GB 预付包 | **€0.98/GB 起**（0.5–50 GB） |
| Unlimited | 按天 | **€2/天 起**（每日 5 GB 高速，之后 512 Kbps） |

官网正文里两个 10 GB 价格（€17.00 / €19.50）互相矛盾，**两条都原样保留**，不擅自取一。

## 折扣码 / 优惠数据集（`promos/`，2026-10-04）

与上面的 `plans/` **互补**：`plans/` 存挂牌价，`promos/` 存「怎么买更便宜」。

**16 个品牌 × 120 条 offer**，抓取快照日 **2026-10-04**。品牌的别名对应：

| 用户口径 | `brand_key` | 说明 |
|---|---|---|
| bensim | `bnesim` | 正确拼写是 **BNESIM** |
| yesim / saily | `yesim` + `saily` | 是两个独立品牌 |
| 其余 | 同名小写 | roamless gomoworld nomad jetpac gigsky quibity holafly airalo ubigi roamic alosim |

另补采了 `maya`、`firsty`、`roamic` 三个用户未点名但相关的品牌。

### 每条 offer 记录什么

折扣码（`code`）、优惠类型（`kind` 8 类）、折扣幅度（`discount`/`percent`/`amount`）、
适用人群（`audience`）、门槛与封顶（`min_spend`/`max_discount`）、是否可叠加（`stackable`）、
使用次数（`uses`）、适用范围（`scope`）、到期日（`expires`）、**完整使用规则（`terms`）**、
来源链（`source`/`source_url`）与**置信度**（`confidence`）。

### 置信度三档（关键）

| confidence | 含义 | 本轮条数 |
|---|---|---|
| `official` | 官网在架活动，渲染页面上直接可见 | 38 |
| `verified-thirdparty` | 第三方站声明已在官方结算页实测通过 | 28 |
| `reported` | 仅聚合站列出，未实测 | 53 |

> **红线**：`reported` 档仅作候选，**不得当作事实**写进站点正文。

### 分类分布

`coupon` 81 · `referral` 13 · `bonus_data` 10 · `loyalty` 6 · `free_trial` 4 ·
`card_benefit` 2 · `student` 2 · `cashback` 2

### 已知坑

- **Airalo** 自动化屏蔽最严（ProxyError + Cloudflare）→ 数据来自官方新闻稿 + 聚合站交叉验证。
- **GigSky** `/promotions` `/refer` 是 SPA，直接抓返回 "Oops! Something went wrong" → 条款取自 flight JSON 与官方 Visa 页。
- **Firsty** 官网 JSON `discountPercent=0`，确认无常设折扣码。
- **失效码**已刻意排除：Saily `SAILY50`/`SAILY20`、BNESIM `BNESIMFREE`/`BNESIM50`。

详见 `promos/README.md`。

## Trustpilot（预留，未采集）

按你的要求不抓。5 个 `brand/<brand>.json` 里各有一个 `trustpilot` 对象，字段已就位待填：

```json
"trustpilot": {
  "url": "https://www.trustpilot.com/review/www.nomadesim.com",
  "rating": null, "review_count": null, "trust_score": null,
  "five_star_pct": null, "verified_reviews": null,
  "last_checked": null, "recent_reviews": [],
  "note": "PLACEHOLDER - to be filled manually by the user"
}
```

## 品牌档案已采到什么

- **jetpac** — 最完整：官方 `Organization` JSON-LD（成立年份、地址、联系方式、社交链接）
  + App Store 评分 `4.2/5 (113 条)`
- **gigsky** — 首页渲染文本：Visa 官方合作、`4.3/5 基于 5.9K 评价`、App Store `4.8/5`、`1M+ users`
- **maya** — 首页文本：全球 165+ 国、`USD 1.67/day` 起、真无限量
- **quibity** — About 页事实句 + 邮箱 + 社交链接
- **nomad** — ❌ 官网不可达，仅有 esimdb 侧的套餐数据

## 复现 / 重跑

```bash
cd <project>/_competitors
export PATH="/c/Python314:$PATH"      # 该解释器已装 playwright 1.60 + requests

# 1) esimdb 系（含新品牌 roamless / gomoworld），可断点续跑
python -X utf8 scrape_esimdb_brands.py nomad jetpac gigsky quibity roamless gomoworld
# 2) 官网系
python -X utf8 scrape_maya_official.py
python -X utf8 scrape_jetpac_official.py
python -X utf8 scrape_brand_profiles.py
python -X utf8 scrape_brand_about.py
# 3) 第二轮新增官网品牌
python -X utf8 parse_bnesim.py         # BNESIM 公开定价 API -> plans/bnesim/
python -X utf8 parse_firsty.py         # Firsty 全球定价模型 -> plans/firsty/
python -X utf8 stage_official_raw.py   # 落 raw/bnesim/ 与 raw/firsty/
python -X utf8 make_brand_profiles_round2.py   # brand/*.json（4 个新品牌）
# 4) 归一化与报告
python -X utf8 build_plans.py          # raw -> plans/*.toml + plans_all.csv
python -X utf8 report.py               # -> COVERAGE.md
python -X utf8 audit_raw.py            # raw 质量审计
# 5) 折扣码 / 优惠数据集（第三轮）
python -X utf8 build_promos.py         # -> promos/<brand>.json ×16 + promos.json + promos_all.csv
```

`_probe_promo/` 下的抓取辅助脚本（非构建链，按需调用）：

| 脚本 | 用途 |
|---|---|
| `fetch_pw.py` | Playwright 抓被 Cloudflare/WAF 拦截的站点 |
| `fetch_promo_pw.py` | Playwright 渲染 JS 重的官方促销页（含滚动触发懒加载），落 `.html` + `.txt` |
| `extract2.py` | 从 HTML 抽可见文本 + 折扣关键词上下文 + JSON `promoCode`/`discountPercent` |

> `build_promos.py` **整体重写** `promos/`，因此数据改动必须落在脚本里的 `BRANDS` 字典（单一真源），
> 直接编辑生成的 JSON 会在下次运行时丢失。

脚本均支持断点续跑：已存在的输出文件会跳过，加 `--force` 重抓。

`build_plans.py` 的 `SOURCES` 表带 `kind` 字段（`esimdb` / `maya` / `bnesim` /
`firsty`），新品牌按对应 kind 走各自的归一化分支。
