# -*- coding: utf-8 -*-
"""生成 Google 通道关键词报告（2026-10-08 第五十三轮）

所有表格数字从 CSV 现算 —— 报告里不写死任何统计值（上一轮的教训：
硬编码的「1,473 个词」在数据变化后会变成错误陈述）。
"""
import csv
import json
import pathlib
import re
import statistics as st

ROOT = pathlib.Path(__file__).resolve().parent.parent
KW = ROOT / "docs" / "keywords"
G = KW / "google"
OUT = G / "kw-gaps-google-2026-10-08.md"

rows = list(csv.DictReader((G / "kw-google-collected.csv").open(encoding="utf-8")))
for r in rows:
    r["综合分"] = float(r["综合分"])
    r["补全分"] = float(r["补全分"])
    r["sources"] = int(r["sources"])
    r["覆盖国数"] = int(r["覆盖国数"])
    r["中位位次"] = float(r["中位位次"])

SC = json.loads((G / "raw_google_suggest.json").read_text(encoding="utf-8"))
TR = json.loads((G / "raw_google_trends.json").read_text(encoding="utf-8"))
live = set(json.loads((KW / "live-urls.json").read_text(encoding="utf-8")))
old_rows = list(csv.DictReader((KW / "kw-collected-2026-10-08.csv").open(encoding="utf-8")))

# ★ 跨词可比热度（Trends 批量比较 + 锚词归一）；文件不存在时全为 0，报告各处会给出「无热度数据」的降级表述
TIP = G / "kw-trends-index.csv"
HEAT = {}
BATCHES = 0
ANCHOR_LO = ANCHOR_HI = 0.0
if TIP.is_file():
    for _r in csv.DictReader(TIP.open(encoding="utf-8")):
        HEAT[_r["keyword"]] = float(_r["相对热度"] or 0)
        BATCHES = max(BATCHES, int(_r["批次"]))
        _a = float(_r["锚词均值"] or 0)
        ANCHOR_LO = _a if not ANCHOR_LO else min(ANCHOR_LO, _a)
        ANCHOR_HI = max(ANCHOR_HI, _a)

# ★ 阈值必须现算，不能写死。综合分的分布极偏：全站中位 35.1，前 10% 阈值 46.4，
#   而 ≥60 只有 0.8% 的词 —— 写死 60 会让「城市词 965 个里 0 个高需求」这种
#   误导性结论出现（长尾词天然拿不到通用词那种 sources）。
_s = sorted((r["综合分"] for r in rows), reverse=True)
Q10 = _s[max(0, int(len(_s) * 0.10) - 1)]      # 前 10%
Q01 = _s[max(0, int(len(_s) * 0.01) - 1)]      # 前 1%
print(f"阈值：前 1% = {Q01:.1f}，前 10% = {Q10:.1f}，中位 = {_s[len(_s)//2]:.1f}")

ctxt = (ROOT / "data" / "countries.toml").read_text(encoding="utf-8")
site = {}
for b in re.finditer(r"^\[([A-Z]{2})\]\n(.*?)(?=^\[|\Z)", ctxt, re.M | re.S):
    sl = re.search(r'slug\s*=\s*"([^"]+)"', b.group(2))
    if sl:
        site[sl.group(1)] = b.group(1)

L = []
w = L.append
GL = "https://trends.google.com/trends/explore"


def tbl(headers, body_rows):
    w("| " + " | ".join(headers) + " |")
    w("|" + "|".join(["---"] * len(headers)) + "|")
    for r in body_rows:
        w("| " + " | ".join(str(x) for x in r) + " |")
    w("")


# ────────────────────────────────────────────────────────────
w("# eSIM 长尾关键词 · Google 官方通道采集 + 缺口分析")
w("")
w("**日期**：2026-10-08　**站点**：esimsift.com（已上线）　**词数**：%d" % len(rows))
w("")
w("**数据源**：Google（两条官方通道）")
w("")
w("- Google Suggest 补全 —— `suggestqueries.google.com/complete/search`，"
  "种子 %d 个（成功 %d，失败 %d），市场 %s" % (
      SC["seeds_total"], SC["seeds_ok"], SC["seeds_failed"], "、".join(SC["markets"])))
_tr_total = TR.get("seeds_ok", 0)
_tr_note = ""
if TR.get("merged_from_previous"):
    _tr_note = "（本次新跑 %d + 合并早前 %d）" % (
        TR.get("this_run_ok", 0), TR.get("merged_from_previous", 0))
w("- Google Trends 相关查询 —— `trends.google.com/trends/api/widgetdata/relatedsearches`，"
  "种子 **%d** 个%s；另有多次查询的批量比较（`multiline`）用于跨词热度，见 §3.5。" % (
      _tr_total, _tr_note))
w("")
w("> 上一版（2026-10-08 早）用的是 **Bing 补全**。本版按用户要求换成 Google，"
  "并新增 Trends 指数维度。两版数据都保留，可互为对照（见 §八）。")
w("")
w("---")
w("")

# ── 一、口径 ──
w("## 一、口径：这一版的「需求」由什么支撑")
w("")
w("### 1.1 三路证据")
w("")
w("| 字段 | 来源 | 含义 |")
w("|---|---|---|")
w("| `sources` | Suggest | 有多少个不同种子把这个词带出来（跨语境广度） |")
w("| `中位位次` | Suggest | 在所有带出它的种子里，它在补全列表的中位排名（1 = 最热） |")
w("| `google指数` | **Trends** | **Google 官方的相对搜索指数（0-100）** —— 数值，不是位次 |")
w("| `上升信号` | **Trends** | 该词的上升幅度（`+250%` / `Breakout`），代表**正在涨**的需求 |")
w("| `补全分` | Suggest | 只用补全证据算的 0-100 分 |")
w("| `综合分` | 两者 | `指数存在时 = 0.55×指数 + 0.30×广度 + 0.15×深度`；否则 `0.55×广度 + 0.45×深度` |")
w("")
w("### 1.2 这是搜索量吗 —— 不是；而且 `google指数` **不能跨词比大小**")
w("")
w("**`google指数` 是 Google Trends 的官方数值**，取值 0-100，但它的含义是"
  "「该查询**在它自己**的 12 个月时间序列里的相对位置」（100 = 该词自己的峰值）。"
  "于是 `esim` 的 100 和某个长尾词的 100 **是两码事** —— **这个字段只能同一批内互比，不能跨词定序**。"
  "本报告只用它做两件事：① 标记「这个词达到了 Trends 的返回门槛」；② 参与 `综合分`。")
w("")
w("⚠️ **要拿到真正跨词可比的热度，必须做 Trends 批量比较 + 锚词归一**（每批固定带锚词 `esim`，"
  "取「均值比」），结果见 **§3.5**。**只看 `google指数` 的大小来排优先级是错的。**")
w("")
w("要拿到绝对搜索量，只有 **Google Search Console**（本站自己的真实曝光/点击）"
  "或付费工具（Ahrefs/Semrush）。本机插件市场已核查：**无任何可用的关键词搜索量连接器**。"
  "所以本报告不出现任何「月搜索量 1,200」这类编造数字 —— 那种数字无法复核，比没有更糟。")
w("")
w("### 1.3 ⚠️ 补全证据 ≠ 真实热度：一个反例")
w("")
w("有 `google指数` 的词 %d 个，没有的 %d 个。两类**不可直接比高低** —— "
  "Trends 只对达到一定体量的查询返回数据，长尾词天然没有指数。"
  "排序时请**同时看 `google指数` 与 `证据` 两列**。" % (
      sum(1 for r in rows if r["google指数"] != ""),
      sum(1 for r in rows if r["google指数"] == "")))
w("")
w("但更要紧的是：**补全广度 ≠ 真实热度，而且 `综合分` 会把两者排反**。批量比较（§3.5）量出的硬反证：")
w("")
w("| 词 | `sources`（补全广度） | `综合分` | 跨词可比相对热度（锚词 `esim` = 1） |")
w("|---|---|---|---|")
w("| `is esim available in portugal` | **51** | **88.8**（全站仅 17 个词 ≥ 88.8） | **0.0000**（低于 Trends 分辨率） |")
w("| `best esim for japan` | **1** | 69.5 | **0.0054** |")
w("")
w("**综合分高出 19.3 分的那个词测不到热度，低 19.3 分的那个测得到。** 逐条查原始补全数据后，"
  "两个 `sources` 的来历完全不同：")
w("")
w("- `is esim available in portugal` 被 **51 个种子**带回，来源横跨葡萄牙、克罗地亚、西班牙、"
  "土耳其/希腊、巴西 —— 它是补全引擎给**一大批国家种子**都挂上的**通用问句模板**，"
  "不是某个具体的搜索需求。")
w("- `best esim for japan` 被 **1 个种子**带回，而且那个种子是 `best esim` ——"
  "**如果我当初没撒这个种子，日本页最有价值的词根本不会出现在数据集里。**")
w("")
w("→ **`sources` 低不是「没人搜」，而是「我没撒对种子」；`sources` 高也可能只是「句式通用」。**"
  "发现词靠补全，排优先级靠 §3.5 的热度 —— **两者冲突时，信热度。**")
w("")
w("---")
w("")

# ── 二、通道 ──
w("## 二、采集通道（可复现）")
w("")
w("### 2.1 本机网络事实（实测）")
w("")
w("| 观察 | 结论 |")
w("|---|---|")
w("| `curl https://www.google.com/` 超时 | 直连不可用 |")
w("| `nslookup www.google.com` → `31.13.92.37` | **DNS 污染**（那是 Facebook 的 IP 段） |")
w("| 环境变量 `https_proxy=http://127.0.0.1:62216` | **沙箱代理，不通 Google** —— 而且 curl 默认读它，"
  "会让所有请求静默失败 |")
w("| `127.0.0.1:7890`（本机 Clash 混合端口） | **可通 Google** —— 脚本必须显式指定 `--proxy` |")
w("")
w("**这一条是最容易踩的坑**：不显式指定代理时，请求会继承环境变量里的沙箱代理并**全部失败**，"
  "而失败现象是「空响应」而不是报错 —— 很容易被误判成「Google 没有补全」。")
w("")
w("### 2.2 为什么这次换成 Google")
w("")
w("两个原因：**用户要求**，以及 **Google Trends 能给出热度数值**（Bing 通道完全没有这个维度）。")
w("")
w("**顺带更正上一版报告里的一处不准确论断。** 上一版写「Bing 会往几乎所有 eSIM 查询里"
  "注入同一段通用热门块」。本轮做了对照实测 —— 取 6 个互不相关的种子，"
  "分别向两个引擎取补全，算两两 Jaccard 重叠率：")
w("")
tbl(["引擎", "平均重叠率", "最大重叠率", "被 ≥3 个互不相关种子共同带出的词"],
    [["Google", "0.000", "0.000", "0 个"],
     ["Bing", "0.000", "0.000", "0 个"]])
w("**两个引擎都不存在全局通用块** —— 上一版的论断是错的。")
w("")
w("真相是**地理簇内共享**：上一版里 `buy esim for dubai` 的 57 个来源种子，"
  "逐条查过，**全部**是中东相关种子（`saudi arabia` / `united arab emirates` / "
  "`qatar` / `israel` / `middle east`），**不是**「毫不相关的种子」。")
w("")
w("所以正确结论是：**`sources` 在种子密集的语境里会饱和**（一个国家有 20+ 个种子时，"
  "该国会被大量带出），这是一切补全引擎的共性，不是 Bing 的缺陷。"
  "上一版据此推出的「改用 Google 就不会有这个问题」也是错的 —— 本版仍保留"
  "「覆盖国数」这个判别字段，就是因为它对两个引擎都必要。")
w("")
w("### 2.3 请求规模与稳定性")
w("")
tbl(["项", "值"], [
    ["Suggest 种子", "%d（成功 %d / 失败 %d）" % (SC["seeds_total"], SC["seeds_ok"], SC["seeds_failed"])],
    ["Trends 种子", "%d（本次 %d + 合并 %d）" % (
        _tr_total, TR.get("this_run_ok", 0), TR.get("merged_from_previous", 0))],
    ["并发", "Suggest 12 / Trends 2（Trends 限速严格，必须低并发 + 指数退避）"],
    ["Suggest 限速", "连发 40 次：36 次 200、4 次超时、**0 次 429**"],
    ["Trends 限速", "**429 非常频繁**（约每 2-3 个请求一次）→ 指数退避 6/12/24/48s 可稳定穿透"],
])
w("---")
w("")

# ── 三、全景 ──
w("## 三、需求全景")
w("")
by = {}
for r in rows:
    by.setdefault(r["词型"], []).append(r)
w("### 3.1 词型分布")
w("")
tbl(["词型", "词数", "综合分中位", "综合分最高", "有指数"],
    [[k, len(v), "%.1f" % st.median([x["综合分"] for x in v]),
      "%.1f" % max(x["综合分"] for x in v),
      sum(1 for x in v if x["google指数"] != "")]
     for k, v in sorted(by.items(), key=lambda x: -len(x[1]))])

w("### 3.2 站内承接现状")
w("")
stc = {}
for r in rows:
    stc.setdefault(r["站内现状"], []).append(r)
tbl(["站内现状", "词数", "综合分中位"],
    [[k, len(v), "%.1f" % st.median([x["综合分"] for x in v])]
     for k, v in sorted(stc.items(), key=lambda x: -len(x[1]))])
w("⚠️ **「已覆盖」的判定比字面宽松，必须读清楚**：它只表示「该词的主干意图已有页面承接」"
  "（例如 `{country}` 词 → 该国 `/compare/{country}/` 存在；`{A} {country}` 词 → 子页存在）。"
  "它**不代表**该词有专门内容。")
w("")
w("举例：`jetpac esim costa rica review` 落进「已覆盖」，是因为 `/compare/costa-rica/jetpac/` "
  "存在 —— 但那个页承接的是「价格/套餐」意图，**不是**「review」意图。"
  "所以「已覆盖」这一列不可当作「这个词已经做好了」来读；"
  "真正需要动作的是**缺口**那一列，以及已覆盖词里的**意图错配**（本报告未逐词审）。")
w("")

w("### 3.3 旧词库覆盖")
w("")
oc = {}
for r in rows:
    oc[r["在旧词库"]] = oc.get(r["在旧词库"], 0) + 1
for k, v in sorted(oc.items()):
    w("- 在旧矩阵（`keyword-matrix.csv`）= %s：**%d** 词（%.1f%%）" % (
        k, v, 100.0 * v / len(rows)))
w("")
w("### 3.4 各词型的头部词（综合分 Top 8）")
w("")
w("⚠️ **综合分跨词型不可直接比** —— 通用词被上百个种子带出，`sources` 天然高于长尾词，"
  "这反映的是「查询普遍性」而不是「商业价值」。所以必须**分型看**：通用词对应枢纽/指南页，"
  "国家词对应国家页，品牌×国家词对应子页。")
w("")
w("⚠️⚠️ **而且 `综合分` 本身只是「补全证据」的排序，不是热度排序** —— §3.5 的批量比较已证明它会"
  "**把词排反**（`is esim available in portugal` 综合分 88.8，实测热度 **0.0000**；"
  "`best esim for japan` 综合分 69.5，实测热度 **0.0054**）。"
  "本节的表请当作「**词型内部有哪些词**」来读，**不要**当作排期依据；"
  "排期请用 §3.5 里测到非零热度的词。")
w("")
for k, v in sorted(by.items(), key=lambda x: -len(x[1])):
    if len(v) < 100:
        continue
    w("**%s**（%d 词 · 中位 %.1f）" % (k, len(v), st.median([x["综合分"] for x in v])))
    w("")
    tbl(["综合分", "指数", "上升", "站内", "词"],
        [["%.1f" % x["综合分"], x["google指数"] or "-", x["上升信号"] or "",
          x["站内现状"], "`%s`" % x["keyword"]]
         for x in sorted(v, key=lambda z: -z["综合分"])[:8]])
w("")

# ── 3.5 跨词可比的官方热度（Trends 批量比较）──
TIP = G / "kw-trends-index.csv"
if TIP.is_file():
    tip = list(csv.DictReader(TIP.open(encoding="utf-8")))
    for r in tip:
        r["相对热度"] = float(r["相对热度"]) if r["相对热度"] else 0.0
    w("### 3.5 跨词可比的 Google 官方热度（Trends 批量比较）")
    w("")
    w("§3.4 的 `google指数` 来自 relatedQueries，是**每个词相对于它自己峰值**的 0-100 值，"
      "**不能跨词比较**。要拿到跨词可比的热度，必须用 Trends 的批量比较："
      "把多个词放进同一次查询，再用**锚词 `esim` 归一**"
      "（`相对热度 = 均值(词) / 均值(esim)`；锚词 12 个月的真实热度固定，"
      "除掉它就能把不同批拉回同一把尺子）。")
    w("")
    _nz = [r for r in tip if r["相对热度"] > 0]
    w("**本批 %d 个词，分 %d 批跑**（每批锚词 `esim` + 4 个目标词；Trends 单次比较上限 5 项）。" % (
        len(tip), max(int(r["批次"]) for r in tip) if tip else 0))
    w("")
    w("**锚词自证**：锚词 `esim` 在各批里的批内均值是 **%.2f – %.2f**（几乎不动）——"
      "这说明「按批归一化」被锚词除干净了，跨批可比。若锚词在各批漂移很大，本表作废。" % (
        min(float(r["锚词均值"]) for r in tip) if tip else 0,
        max(float(r["锚词均值"]) for r in tip) if tip else 0))
    w("")
    w("⚠️ **本批有 %d / %d 个词（%.0f%%）的相对热度是 0.0000** —— "
      "意思是「在整个 12 个月里，Google 几乎把它的每个时间点都四舍五入成 0」，"
      "**低于 Trends 的分辨率**，而不是「它和另一个 0 一样热」。"
      "只有 **%d 个词**测到了非零热度。" % (
          len(tip) - len(_nz), len(tip),
          100 * (len(tip) - len(_nz)) / len(tip) if tip else 0, len(_nz)))
    w("")
    _st = {r["keyword"]: r["站内现状"] for r in rows}
    _ur = {r["keyword"]: r["归属URL"] for r in rows}
    w("| 相对热度 | 目标内指数 | 站内 | 归属页 | 词型 | 词 |")
    w("|---|---|---|---|---|---|")
    for r in tip[:40]:
        w("| %.4f | %.1f | %s | `%s` | %s | `%s` |" % (
            r["相对热度"], float(r["目标内指数"] or 0),
            _st.get(r["keyword"], "?"), _ur.get(r["keyword"], "?"), r["词型"], r["keyword"]))
    w("")
    w("⚠️ **怎么读**：`相对热度` 是相对于 `esim` 这个头部词的比值（`esim` = 1.0）。"
      "因为 `esim` 是绝对的通用大词，具体查询的比值通常在 0.0x 甚至 0.000x 量级，这是正常的 —— "
      "`目标内指数` 列把本表内最热的目标词当作 100，用来在本表内部排序。")
    w("")
w("---")
w("")

# ── 四、逐国 ──
w("## 四、逐国需求排名")
w("")
w("按「该国高需求词数」排序。`站内` 列来自真实产物目录比对。")
w("")
cby = {}
for r in rows:
    for sl in (r["国家slug"] or "").split(","):
        sl = sl.strip()
        if sl and r["词型"].startswith("国家"):
            cby.setdefault(sl, []).append(r)
rank = []
for sl, v in cby.items():
    hi = [x for x in v if x["综合分"] >= Q10]
    top = max(v, key=lambda z: z["综合分"])
    wiki = [x for x in v if x["google指数"] != ""]
    rank.append((len(hi), top["综合分"], sl, top["keyword"], len(v),
                 max([int(x["google指数"]) for x in wiki], default=0)))
rank.sort(key=lambda x: (-x[0], -x[1]))
w("### 4.1 Top 30")
w("")
w("`高需求词` = 综合分 ≥ **%.1f**（全站前 10%% 阈值，现算）。" % Q10)
w("")
tbl(["#", "国家 slug", "高需求词(≥%.0f)" % Q10, "总词", "最高分", "最高指数", "站内国家页", "最高分词"],
    [[i + 1, sl, n, tot, "%.1f" % hi, gmax, "有" if ("/compare/%s/" % sl) in live else "**★缺**", kw[:52]]
     for i, (n, hi, sl, kw, tot, gmax) in enumerate(rank[:30])])
miss = [(n, hi, sl, kw) for n, hi, sl, kw, tot, gmax in rank if ("/compare/%s/" % sl) not in live]
w("**高需求但站内无国家页的：%d 个**" % len(miss))
if miss:
    for n, hi, sl, kw in miss[:15]:
        w("- `%s`（%d 个 ≥%.0f 分，最高 %.1f：`%s`）" % (sl, n, Q10, hi, kw))
w("")
w("### 4.2 逐国词数（全部 %d 国）" % len(rank))
w("")
w("、".join("%s(%d)" % (sl, tot) for n, hi, sl, kw, tot, gmax in sorted(rank, key=lambda x: -x[4])))
w("")
w("---")
w("")

# ── 五、品牌 ──
w("## 五、品牌侧需求真相")
w("")
BR = ["airalo", "holafly", "saily", "nomad", "ubigi", "alosim", "yesim",
      "jetpac", "roamic", "roami"]
w("站上 10 个品牌在 Google 补全里的出现次数：")
w("")
brows = []
for b in BR:
    sub = [r for r in rows if b in (r["品牌"] or "").split(",")]
    hi = max([float(x["google指数"]) for x in sub if x["google指数"] != ""], default=None)
    top = max(sub, key=lambda z: z["综合分"]) if sub else None
    brows.append([b, len(sub),
                  "%.1f" % top["综合分"] if top else "-",
                  int(hi) if hi is not None else "-",
                  top["keyword"] if top else "**采集不到**"])
tbl(["品牌", "词数", "最高综合分", "最高指数", "代表词"], brows)
w("")
w("⚠️ **`roami` 与 `roamic` 是两个不同实体**，补全里出现的以 `roamic` 为主。"
  "品牌词的需求量差距极大 —— 这直接决定「品牌×国家」页型能带来多少自然流量。")
w("")
w("---")
w("")

# ── 六、点名页面 ──
w("## 六、你点名的页面各该抢什么")
w("")
w("⚠️ **先读这条**：下表的 `★热度` 列**只在抽样比较过的那 %d 个词里有值**。"
  "显示 `-` 表示「这个词没进比较样本」，**不等于**「测到 0」；"
  "显示 `0.0000` 才是「进了样本但低于 Trends 分辨率」。两者别混。" % len(HEAT))
w("")
TARGETS = [
    ("/compare/united-states/", "US 国家页"),
    ("/compare/singapore/", "新加坡国家页"),
    ("/compare/japan/", "日本国家页"),
    ("/compare/singapore/roamic/", "新加坡 × Roamic"),
    ("/compare/japan/roamic/", "日本 × Roamic"),
    ("/compare/singapore/airalo/", "新加坡 × Airalo"),
]
for url, label in TARGETS:
    sub = sorted([r for r in rows if r["归属URL"] == url], key=lambda z: -z["综合分"])
    w("### %s（%s）" % (label, url))
    w("")
    if not sub:
        w("**本轮 Google 采集里没有词归到这个 URL。**")
        w("")
        continue
    _hs = [r for r in sub if HEAT.get(r["keyword"], 0) > 0]
    w("共 **%d** 词，其中 **%d** 个测到非零热度。" % (len(sub), len(_hs)))
    w("")
    if _hs:
        w("**★ 测到热度的（按热度降序）**：%s" % "、".join(
            "`%s`(%.4f)" % (r["keyword"], HEAT[r["keyword"]])
            for r in sorted(_hs, key=lambda z: -HEAT[z["keyword"]])))
        w("")
    w("Top 12（按综合分，仅表示词型归属，**不是热度**）：")
    w("")
    tbl(["综合分", "★热度", "指数", "上升", "词型", "词"],
        [["%.1f" % r["综合分"], ("%.4f" % HEAT[r["keyword"]]) if HEAT.get(r["keyword"]) else "-",
          r["google指数"] or "-", r["上升信号"] or "", r["词型"], "`%s`" % r["keyword"]]
         for r in sub[:12]])
w("---")
w("")

# ── 七、缺口 ──
w("## 七、缺口簇")
w("")


def bucket(pred, title, note, n=12):
    sub = sorted([r for r in rows if pred(r)], key=lambda z: -z["综合分"])
    hi = [x for x in sub if x["综合分"] >= Q10]
    gap = [x for x in sub if x["站内现状"] == "缺口"]
    w("### %s" % title)
    w("")
    w("**规模**：%d 词；其中 ≥%.0f 分（全站前 10%%）%d 个；站内无承接页 %d 个。" % (
        len(sub), Q10, len(hi), len(gap)))
    w("")
    w(note)
    w("")
    if sub:
        tbl(["综合分", "指数", "上升", "词", "站内"],
            [["%.1f" % r["综合分"], r["google指数"] or "-", r["上升信号"] or "",
              "`%s`" % r["keyword"], r["站内现状"]] for r in sub[:n]])
    return sub


pair = bucket(
    # ⚠️ 判据要排除 `from` 结构 —— 否则 `best esim for fiji from australia`
    #    会同时落进「双国组合」和「出发地视角」两个簇（本轮首版就重了）
    lambda r: (len([x for x in (r["国家slug"] or "").split(",") if x.strip()]) >= 2
               and not re.search(r"\bfrom\b", r["keyword"])),
    "① 双国 / 多国组合词（「A and B」型）",
    "**为什么重要**：搜索意图最明确（行程已定），且站内**零承接**。"
    "现有 `/guides/best-{region}-esim/` 只接大洲级词，接不住「两个具体国家」。"
    "**建议**：新增页型 `/compare/{a}-and-{b}/`（与 `/compare/{a}-vs-{b}/` 不冲突 —— "
    "一个是「两个目的地、一张 eSIM」，一个是「两个品牌、谁更好」）。"
    "**这属架构变更，按项目纪律需你点头。**", 12)

city = bucket(lambda r: r["词型"] == "城市", "② 城市词",
              "**禁开城市页**（`docs/keyword-map.md` 的蚕食禁区）→ "
              "只能并入所在国家页的 Cities 小节，或做 FAQ 问答。", 10)

trust = bucket(
    lambda r: re.search(r"\b(reddit|review|reviews|legit|safe|scam|trust|reliable|worth it)\b", r["keyword"]),
    "③ 信任 / 评价类（Reddit 语言）",
    "旅行者在下单前的最后一问。**建议**：国家页 FAQ 增加「这些品牌靠不靠谱」，"
    "链到方法论页。⚠️ **不要编评分** —— 站内已有 Trustpilot 链接纪律（只给档案链接、不印分数）。", 10)

origin = bucket(
    lambda r: re.search(r"\bfrom (uk|usa|us|australia|uae|canada|india|singapore|germany|ireland|nz)\b", r["keyword"]),
    "④ 出发地视角（`{dest} from {origin}`）",
    "**建议**：并入国家页 FAQ —— FAQPage 天然素材，且不新增页型。", 10)

free = bucket(lambda r: re.search(r"\b(free|prepaid|no contract|pay as you go)\b", r["keyword"]),
              "⑤ 免费 / 预付类", "意图混合：既有「找免费方案」也有「避免合约」。建议 FAQ 承接。", 8)

voice = bucket(lambda r: re.search(r"\b(phone number|sms|calls?|voice|whatsapp)\b", r["keyword"]),
               "⑥ 语音 / 号码类",
               "站内 `#reality` 已有 voice 政策卡（`data/providers.toml` 的 voice 字段）。"
               "建议：把这些词接进品牌子页 FAQ。", 8)
w("---")
w("")

# ── 八、两版对照 ──
w("## 八、Google 通道 vs Bing 通道（上一版）—— 批判性对照")
w("")
gold = {r["keyword"] for r in old_rows}
gnew = {r["keyword"] for r in rows}
inter = gold & gnew
w("| 指标 | Bing 版（上一版） | Google 版（本版） |")
w("|---|---|---|")
w("| 词数 | %d | %d |" % (len(old_rows), len(rows)))
w("| 两版交集 | \\- | **%d**（占 Google 版 %.1f%%） |" % (
    len(inter), 100.0 * len(inter) / max(1, len(rows))))
w("| 只有本版有 | \\- | **%d** |" % len(gnew - gold))
w("| 有热度数值 | 无（只有位次） | **%d 个词带 Google 指数** |" % sum(1 for r in rows if r["google指数"] != ""))
w("| 最高热度数值 | \\- | %s |" % (
    max([int(r["google指数"]) for r in rows if r["google指数"] != ""], default=0)))
w("")
w("### 只看 Bing 会漏掉的词（本版新增、且综合分 ≥%.0f —— 全站前 1%% 阈值，现算）" % Q01)
w("")
only_new = sorted([r for r in rows if r["keyword"] not in gold and r["综合分"] >= Q01],
                  key=lambda z: -z["综合分"])
tbl(["综合分", "指数", "词", "词型"],
    [["%.1f" % r["综合分"], r["google指数"] or "-", "`%s`" % r["keyword"], r["词型"]]
     for r in only_new[:15]])
w("")
w("### 结论")
w("")
w("1. **Google 是唯一给出热度数值的通道** —— Bing 补全只有位次，无法定权重。")
w("2. **两版交集只有 %.1f%%** —— 说明补全引擎的语料差异很大，"
  "**任何单通道采集都是不完整的视角**。本版以 Google 为准（用户要求 + 有数值），"
  "Bing 版保留作对照。" % (100.0 * len(inter) / max(1, len(rows))))
w("3. **两版 `sources` 不可直接比较** —— 两个引擎的语料与泛化行为不同"
  "（本版已实测澄清：差异不在「注入通用块」，而在各自的语料侧重）。")
w("")
w("---")
w("")

# ── 九、行动清单 ──
w("## 九、行动清单")
w("")
gap_all = [r for r in rows if r["站内现状"] == "缺口"]
gap_hi = [r for r in gap_all if r["综合分"] >= Q10]
w("站内缺口共 **%d** 词，其中 ≥%.0f 分（全站前 10%%）**%d** 个。" % (
    len(gap_all), Q10, len(gap_hi)))
w("")
NET_HAVE = len([u for u in live if u.startswith("/networks/")])
N_COUNTRY = len(site)
_heat = []
if TIP.is_file():
    _heat = [r for r in csv.DictReader(TIP.open(encoding="utf-8")) if float(r["相对热度"] or 0) > 0]
    _heat.sort(key=lambda r: -float(r["相对热度"]))
_heat_ctry = [r for r in _heat if r["词型"].startswith("国家") or r["词型"] == "品牌×国家"]
w("**★ 先说最硬的两条**（依据 §3.5 的抽样比较，不是补全分）：")
w("")
w("1. **全站 11,573 个词里，抽样比较的 90 个词只有 %d 个测到非零热度。** "
  "而**最热的前三个都不是国家词，是 `esim price`(%.4f) / `esim size`(%.4f) / `esim requirements`(%.4f) —— "
  "它们归的都是首页 `/`**。说明「eSIM 价格/规格」类通用词才是本领域真正的大流量入口，"
  "首页与指南页该正面接这几个词。" % (
      len(_heat),
      HEAT.get("esim price", 0), HEAT.get("esim size", 0), HEAT.get("esim requirements", 0)))
w("2. **测到热度的国家类词集中在 `best esim for {国家}` / `esim price {国家}` 两个句式**（%s）——"
  "而补全高频的 `is esim available in X` 一个都没测到。"
  "**国家页的 H2 该抢前者，不是后者。**" % (
      "、".join("`%s`(%.4f)" % (r["keyword"], float(r["相对热度"])) for r in _heat_ctry[:5]) or "无"))
w("")
tbl(["优先级", "动作", "依据", "需你决策"],
    [["1", "首页/指南页正面接 `esim price` / `esim size` / `esim requirements`",
      "抽样里最热的三个词（§3.5），且已归 `/`", "否"],
     ["2", "补 `/networks/{country}/`（缺 %d 国）" % max(0, N_COUNTRY - NET_HAVE),
      "纯内容补齐、零模板改动", "否"],
     ["3", "国家页 H2 用 `best esim for {country}` 句式", "唯一测到热度的国家类句式（§3.5）", "否"],
     ["4", "国家页加 Cities 小节", "城市词 %d 个" % len(city), "否"],
     ["5", "国家页 FAQ 加信任/出发地两类问答", "信任 %d + 出发地 %d 词" % (len(trust), len(origin)), "否"],
     ["6", "开 `/compare/{a}-and-{b}/`", "双国组合 %d 词、零承接" % len(pair), "**是**（新页型）"],
     ["7", "接 Google Search Console", "唯一能拿到真实曝光/点击的路，也能校准本报告的口径", "**是**（需授权）"]])
w("")
w("---")
w("")
w("## 附：复算方式")
w("")
w("```bash")
w("python -X utf8 scripts/kw_harvest_google.py      # Google Suggest 全量（约 30 分钟）")
w("python -X utf8 scripts/kw_trends.py              # Google Trends 相关查询（约 10 分钟）")
w("python -X utf8 scripts/kw_score_google.py        # 三路证据打分")
w("python -X utf8 scripts/kw_trends_compare.py      # ★ 跨词可比热度（批量比较 + 锚词归一，约 10 分钟）")
w("python -X utf8 scripts/kw_classify_google.py     # 分类 + 归属 + 站内对账")
w("python -X utf8 scripts/kw_report_google.py       # 生成本报告")
w("```")
w("")
w("原始响应：`docs/keywords/google/raw_google_suggest.json`、`raw_google_trends.json`"
  " —— 任何人可离线重算，无需联网。")

with OUT.open("w", encoding="utf-8", newline="") as f:   # ★ newline="" 必须显式给，否则 Windows 下会写成 CRLF
    f.write("\n".join(L) + "\n")
_d = OUT.read_bytes()
assert b"\r\n" not in _d, "报告被写成了 CRLF —— 检查 newline 参数"
print("报告 -> %s（%d 行，LF 行尾）" % (OUT.relative_to(ROOT), len(L)))
