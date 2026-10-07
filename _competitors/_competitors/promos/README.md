# `_competitors/promos/` — eSIM 品牌折扣码 / 优惠结构化数据

竞品折扣情报数据集。覆盖 **16 个品牌 × 120 条 offer**，抓取快照日 **2026-10-04**。
本目录与项目其他文件完全隔离，不改动 Hugo 站点任何内容。

---

## 1. 文件清单

| 文件 | 说明 |
| --- | --- |
| `<brand>.json` | 单品牌一个文件，含该品牌全部 offer + notes + offer_count |
| `promos.json` | 全部品牌合并成一个对象（`brands` 数组 + `meta`） |
| `promos_all.csv` | 扁平表，**一行一个 offer**，UTF-8 BOM（Excel 直接双击不乱码） |
| `README.md` | 本文件：schema 说明 + 口径 + 刷新方法 |

单品牌 JSON 顶层字段：

```jsonc
{
  "brand_key":     "airalo",              // slug，与 _competitors/brand/ 对齐
  "brand_name":    "Airalo",              // 展示名
  "brand_alias":   ["airalo.com"],        // 别名（用户口误拼写等）
  "official_site": "https://www.airalo.com/",
  "captured":      "2026-10-04",          // 抓取快照日
  "offers":        [ /* 见 §2 */ ],
  "notes":         [ "人工总结的可读提示" ],
  "offer_count":   8
}
```

---

## 2. Offer schema（单条优惠）

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| `code` | str | 折扣码本体；纯推荐/返现类无码时为空串 `""` |
| `kind` | str | 优惠类型，见 §3 |
| `discount` | str | 人类可读的优惠标题，如 `15% off`、`$5 off`、`+6 GB` |
| `percent` | float \| null | 直减百分比时的数值（便于排序/计算） |
| `amount` | float \| null | 非百分比时的固定金额 |
| `currency` | str | `amount` 的币种（`USD`/`EUR`/`GBP`…） |
| `audience` | str | `new` / `existing` / `all` / `students` / `cardholders` / `invited_friend` |
| `where` | str | 适用端：`web` / `app` / `web+app` |
| `min_spend` | str \| null | 门槛（如 `plan of 10 GB or more`、`none`） |
| `max_discount` | str \| null | 封顶（如 `100 USD`） |
| `stackable` | str \| null | `no` / `yes` / `one_per_order` / `unknown` |
| `uses` | str \| null | `once_per_account` / `unlimited` / `unknown` |
| `scope` | str | 适用范围（全部套餐 / 仅不限量 / 指定套餐…） |
| `expires` | str \| null | 到期日 `YYYY-MM-DD`，或 `ongoing` / `unknown` |
| `terms` | list[str] \| null | 额外规则条款，逐条列出 |
| `source` | str | `official`（官网）/ `aggregator`（第三方聚合站） |
| `source_url` | str | 证据链 URL |
| `verified` | str | 该条信息被核实的日期（或 `2026-10` 这样的年月粒度） |
| `confidence` | str | 置信度，见 §4 |

CSV 列顺序（`promos_all.csv` 表头）：

```
brand, brand_name, code, kind, discount, percent, amount, currency, audience,
where, min_spend, max_discount, stackable, uses, scope, expires,
source, source_url, verified, confidence, terms
```

`terms` 在 CSV 中用 ` | ` 连接为单串。

---

## 3. `kind` 类型字典（8 类）

| kind | 含义 | 举例 |
| --- | --- | --- |
| `coupon` | 需要输入的折扣码 | `NEWTOAIRALO15`、`OCTOBER20` |
| `referral` | 推荐好友奖励（双向或单向） | Nomad $5、Yesim €5+€5 |
| `loyalty` | 会员/积分/等级权益 | GigSky Rewards、Maya Rewards 6.6% |
| `card_benefit` | 银行卡持卡人权益（走卡组织活动页） | GigSky × Visa 最高 30%、Airalo × Consumer Cellular 15% |
| `student` | 学生认证折扣 | Nomad（Student Beans）、Yesim |
| `free_trial` | 免费试用流量 | GigSky 100 MB、GoMoWorld 1 GB |
| `bonus_data` | 赠流量而非减价 | Roamless `ROAM25/50/75`、GoMoWorld `US_30GB_30_+6GB` |
| `cashback` | 返现/返积分 | BNESIM BNE Coins 5%、Yesim 5% |

> 设计意图：把「减价」和「赠量」分开。赠流量在比价页里应折算成等效单价，而不是当作折扣率。

---

## 4. `confidence` 置信度（3 档）

| 值 | 含义 | 使用建议 |
| --- | --- | --- |
| `official` | 来自品牌官网，且在渲染后的页面上直接可见（本轮 38 条） | 可直接用于正式页面 |
| `verified-thirdparty` | 第三方站声明「已在官方结算页实测通过」（本轮 28 条） | 可用，但建议标注「以结算页为准」 |
| `reported` | 仅被聚合站列出、未验证 / 未实测（本轮 53 条） | 仅作候选，不得当作事实写入正文 |

`verified` 字段与 `confidence` 配合使用：`confidence=official` 时通常等于抓取日，
`verified-thirdparty` 时是发布者的复核日期，`reported` 时可能只有年月。

---

## 5. 数据口径与已知限制

- **时效**：快照日 2026-10-04。折扣码生命周期短，**任何进入正式页面的码都需在使用前一次性复核**。
- **官方 vs 全网**：用户要求「全网最新 + 官网现有」。两者都在，用 `source` + `confidence` 区分，不要混为一谈。
- **Airalo**：站点对代理/自动化屏蔽严格（ProxyError + Cloudflare），数据来自官方新闻稿 + 聚合站交叉验证，无官网 banner 直读。
- **GigSky**：`/promotions`、`/refer` 等页面为 SPA，直接抓取返回 "Oops! Something went wrong"；因此卡权益/推荐条款来自 flight JSON 与官方 Visa 页，非渲染文本。
- **BNESIM**：`/offers` 成功渲染，`OCTOBER20`（20% off ≥10GB，至 2026-10-31）为官网在架活动，已标 `official`。
- **Firsty**：官网 JSON 中 `discountPercent=0`，确认无常设折扣码，仅有推荐计划。
- **失效码黑名单**：Saily 的 `SAILY50`/`SAILY20`、BNESIM 的 `BNESIMFREE`/`BNESIM50` 经核实**不可用**，已刻意不收录或标注。
- **`stackable` 大量为 null/unknown**：多数品牌官网不公开叠加规则，这本身就是信息，不要臆造。

---

## 6. 如何刷新

```bash
# 项目根：D:\HUGO test\29.1_windows-amd64\hugo_0.159.1_windows-amd64\esimsift-main\esimsift-main
C:\Python314\python.exe -X utf8 _competitors\build_promos.py
```

脚本会**整体重写** `promos/` 下全部文件，因此直接改 JSON 会在下次运行时被覆盖 ——
**要改数据请改 `build_promos.py` 里的 `BRANDS` 字典**（单一真源）。

抓取辅助脚本在 `_competitors/_probe_promo/`：

| 脚本 | 用途 |
| --- | --- |
| `fetch_pw.py` | Playwright 抓被 Cloudflare/WAF 拦截的站点（ubigi / airalo / alosim / nomad） |
| `fetch_promo_pw.py` | Playwright 渲染 JS 重的官方促销页，落 `.html` + `.txt`（含滚动触发懒加载） |
| `extract2.py` | 从 HTML 里抽可见文本 + 折扣关键词上下文窗口 + JSON `promoCode`/`discountPercent` |

刷新流程：抓 → 读 → 改 `BRANDS` → 跑 `build_promos.py` → 校对 CSV。

---

## 7. 本轮统计（2026-10-04）

- 品牌 **16**（用户点名的 13 个 + Maya + Firsty + Roamic）
- Offer 总数 **120**
- 含明确折扣码 **83** 条
- 分类分布：`coupon` 81 · `referral` 13 · `bonus_data` 10 · `loyalty` 6 · `free_trial` 4 · `card_benefit` 2 · `student` 2 · `cashback` 2
- 置信度分布：`official` 38 · `verified-thirdparty` 28 · `reported` 53
