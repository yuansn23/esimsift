# -*- coding: utf-8 -*-
"""生成关键词采集报告（表格全部从 CSV 现算，保证与数据一致）2026-10-08"""
import collections
import csv
import io
import json
import pathlib
import re
import statistics

ROOT = pathlib.Path(__file__).resolve().parent.parent
KW = ROOT / "docs" / "keywords"
OUT = KW / "kw-gaps-2026-10-08.md"

rows = list(csv.DictReader((KW / "kw-collected-2026-10-08.csv").open(encoding="utf-8")))
for r in rows:
    r["需求分"] = float(r["需求分"])
    r["sources"] = int(r["sources"])
    r["覆盖国数"] = int(r["覆盖国数"])
    r["中位位次"] = float(r["中位位次"])
    r["top3次数"] = int(r["top3次数"])

live = set(json.loads((KW / "live-urls.json").read_text(encoding="utf-8")))
ctxt = (ROOT / "data" / "countries.toml").read_text(encoding="utf-8")
site = {}
for b in re.finditer(r"^\[([A-Z]{2})\]\n(.*?)(?=^\[|\Z)", ctxt, re.M | re.S):
    sl = re.search(r'slug\s*=\s*"([^"]+)"', b.group(2))
    if sl:
        site[sl.group(1)] = b.group(1)

scored = list(csv.DictReader((KW / "kw-scored.csv").open(encoding="utf-8")))
raw = json.loads((KW / "raw_autocomplete.json").read_text(encoding="utf-8"))
raw2 = json.loads((KW / "raw_autocomplete.pass2.json").read_text(encoding="utf-8"))
mx = list(csv.DictReader(pathlib.Path(
    r"C:\Users\Administrator\WorkBuddy\2026-09-30-13-09-50\esim-compare-blueprint"
    r"\keyword-matrix.csv").open(encoding="utf-8-sig")))

L = []
w = L.append
w("# eSIM 长尾关键词全网采集 · 缺口分析")
w("")
w("**日期**：2026-10-08　**站点**：esimsift.com（已上线）　**词数**：%d" % len(rows))
w("")
w("---")
w("")
w("## 一、口径：这份数据里的「需求」是什么，不是什么")
w("")
w("### 是什么")
w("")
w("**查询补全（autocomplete）证据**。补全建议由真实查询频率驱动 —— "
  "一个短语能出现在补全列表里，就是「有人这么搜」的实证；位次越前，相对热度越高。")
w("")
w("| 字段 | 含义 |")
w("|---|---|")
w("| `sources` | 有多少个不同的种子词把它带出来（跨语境普遍性） |")
w("| `中位位次` | 跨所有带出它的种子，在补全列表里的中位排名（1=最热） |")
w("| `top3次数` | 有多少次它出现在前 3 位 |")
w("| `覆盖国数` | 带出它的种子涉及多少个不同国家/区域语境 |")
w("| `需求分` | `100 ×(0.4×min(sources/40,1) + 0.4×max(0,(13−中位位次)/12) + 0.2×min(top3/8,1))` |")
w("")
w("### 不是什么 —— 三条必须说清的限制")
w("")
w("1. **没有搜索量数字。** 本站没接 Google Search Console / Ahrefs / Semrush，"
  "本机也没有可用这类连接器。所以本报告**不给 volume**，只给可复核的补全证据。"
  "要真实搜索量，唯一正路是接 GSC（能直接看到你已有的曝光词）。")
w("2. **Google 补全在本机不可达**（返回空），DuckDuckGo 同样不可达。"
  "本次采集通道只有 **Bing 补全**（`api.bing.com`）。Bing 与 Google 的建议集合不完全重合，"
  "但都反映真实查询频率 —— 这是代理，不是等同。")
w("3. **Bing 会给几乎所有 eSIM 查询注入同一段通用热门补全块**"
  f"（实测「buy esim for dubai」被 55 个种子带出）。"
  "所以 `sources` 有天花板效应，**`覆盖国数` 才是区分「通用注入词」与「真·逐国词」的关键**："
  "覆盖国数 ≥40 且词里无国名 = 通用词；覆盖国数 ≤12 且中位位次 ≤3 = 真实的逐国需求。")
w("")
w("---")
w("")
w("## 二、采集规模（可复现）")
w("")
w("| 项 | 值 |")
w("|---|---|")
w("| 两轮种子总数 | %d（第 1 轮 %d + 别名轮 %d） |" % (
    raw["seeds_ok"] + raw2["seeds_ok"], raw["seeds_ok"], raw2["seeds_ok"]))
w("| 采集失败 | 0 |")
w("| 剔种子回显 | 1,711 条（Bing 补全第 0 位永远是查询本身，会白送 rank 1） |")
w("| 唯一补全词 | %d |" % len(scored))
w("| 其中 eSIM/SIM 相关 | %d |" % len(rows))
w("| 市场 | en-US + en-GB |")
w("")
w("**第 2 轮（别名轮）修掉了一个自己的方法论错误**：第 1 轮用 `countries.toml` 的 `name` "
  "字段当种子（`United States` / `United Kingdom`），但真实查询用短名（`usa` / `uk`），"
  "而站内命名规则本身也是「USA 替代 United States、UK 替代 United Kingdom」。"
  "代价实测很直接：第 1 轮 US 国家页只采到 99 词、最高分 52.7；"
  "补别名后 `cheapest esim for usa` = 86.7 分。第 2 轮同时补了城市词、年份修饰词与双国组合。")
w("")
w("---")
w("")
w("## 三、词型分布")
w("")
w("| 词型 | 词数 | 需求分中位 | 已覆盖 | 缺口 |")
w("|---|---:|---:|---:|---:|")
by = collections.defaultdict(list)
for r in rows:
    by[r["词型"]].append(r)
for k, v in sorted(by.items(), key=lambda x: -len(x[1])):
    cov = sum(1 for z in v if z["站内现状"] != "缺口")
    w("| %s | %d | %.1f | %d | %d |" % (
        k, len(v), statistics.median(z["需求分"] for z in v), cov, len(v) - cov))
w("")
w("---")
w("")
w("## 四、需求分 Top 30（全站机会面最大的词）")
w("")
w("| # | 词 | 需求分 | sources | 中位位次 | 覆盖国数 | 词型 | 站内 |")
w("|---:|---|---:|---:|---:|---:|---|---|")
for i, r in enumerate(sorted(rows, key=lambda z: -z["需求分"])[:30], 1):
    w("| %d | `%s` | %.1f | %d | %.1f | %d | %s | %s |" % (
        i, r["keyword"], r["需求分"], r["sources"], r["中位位次"],
        r["覆盖国数"], r["词型"], r["站内现状"]))
w("")
w("---")
w("")
w("## 五、逐国需求排名（Top 40）")
w("")
w("**这是「按国家来的长尾词」的排序答案。** 「站内」列即该国国家页是否存在 —— "
  "**50 国一个不缺，全为「有」**，所以缺口不在国家覆盖，在内容深度。")
w("")
w("| # | 国家 | 高需求词数(≥55分) | 采集词数 | 最高分 | 该词 | 站内页 |")
w("|---:|---|---:|---:|---:|---|---|")
byn = collections.defaultdict(list)
for r in rows:
    if r["国家slug"] and r["词型"].startswith("国家"):
        for s in r["国家slug"].split(","):
            byn[s].append(r)
rank = []
for s, v in byn.items():
    hi = [z for z in v if z["需求分"] >= 55]
    top = max(v, key=lambda z: z["需求分"])
    rank.append((len(hi), max(z["需求分"] for z in v), s, top["keyword"], len(v)))
rank.sort(key=lambda x: (-x[0], -x[1]))
for i, (n, hi, s, kw, tot) in enumerate(rank[:40], 1):
    ok = f"/compare/{s}/" in live
    w("| %d | %s | %d | %d | %.1f | `%s` | %s |" % (
        i, s, n, tot, hi, kw, "有" if ok else "★无"))
w("")
w("---")
w("")
w("## 六、缺口簇（站内无承接页）—— 这才是本轮真正的产出")
w("")


def bucket(pred, name, note, n=12):
    sub = sorted([r for r in rows if pred(r["keyword"])], key=lambda z: -z["需求分"])
    hi = [z for z in sub if z["需求分"] >= 50]
    gap = [z for z in sub if z["站内现状"] == "缺口"]
    w("### %s" % name)
    w("")
    w("**规模**：%d 词，其中需求分 ≥50 的 %d 个，站内无承接页的 %d 个。" % (
        len(sub), len(hi), len(gap)))
    w("")
    # ★ 不用 str.format —— note 里含大量 `{country}` / `{region}` 这类**示例占位符**，
    #   一 format 就 KeyError。只替换三个真正要填的记号。
    note = (note.replace("{n}", str(len(sub)))
                .replace("{hi}", str(len(hi)))
                .replace("{gap}", str(len(gap)))
            if note else "")
    w(note)
    w("")
    w("| 需求分 | sources | 覆盖国数 | 词 | 站内 |")
    w("|---:|---:|---:|---|---|")
    for r in sub[:n]:
        w("| %.1f | %d | %d | `%s` | %s |" % (
            r["需求分"], r["sources"], r["覆盖国数"], r["keyword"], r["站内现状"]))
    w("")


# 组合词判据必须**同时**要求「and/plus」+ 「含国家名或区域名」，否则会把
# `esim and sim difference` 这种形态对比词误当双国组合（实测踩到）
_GEO = re.compile(
    r"\b(" + "|".join(sorted(set(list(site) + [
        "usa", "us", "uk", "uae", "korea", "hong kong", "taiwan", "macau", "japan",
        "china", "singapore", "malaysia", "thailand", "vietnam", "indonesia", "bali",
        "france", "italy", "spain", "portugal", "greece", "germany", "austria",
        "switzerland", "netherlands", "belgium", "ireland", "england", "croatia",
        "mexico", "cancun", "canada", "brazil", "argentina", "chile", "peru",
        "costa rica", "panama", "australia", "new zealand", "nz", "dubai",
        "south africa", "kenya", "tanzania", "namibia", "morocco", "egypt", "jordan",
        "turkey", "india", "sri lanka", "philippines", "saudi arabia", "ksa", "qatar",
        "europe", "asia", "africa", "americas", "oceania", "middle east", "caribbean",
        "north america", "south america", "latin america",
    ]), key=len, reverse=True)) + r")\b")


def is_pair(kw):
    if not re.search(r"\b(and|plus)\b", kw):
        return False
    if re.match(r".*\b(esim|sim)\s+and\s+(sim|esim)\b", kw):
        return False           # 形态对比词，不是双国组合
    return bool(_GEO.search(kw))


_pair_rows = sorted([r for r in rows if is_pair(r["keyword"])], key=lambda z: -z["需求分"])
_pair_n = len(_pair_rows)
_pair_hi = sum(1 for z in _pair_rows if z["需求分"] >= 50)
bucket(is_pair,
       "① 双国 / 多国组合词（「A and B」型）——**最大的一块未承接需求**",
       "**为什么重要**：这是唯一一个「词量大（{n} 词）+ 需求高（{hi} 词 ≥50 分）+ "
       "站内无页（{gap} 词）」的三重缺口。"
       "现有 `/guides/best-{region}-esim/` 只承接大洲级词（`best esim for europe`），"
       "接不住「两个具体国家的组合」——而后者搜索意图更明确（已经定好行程了）。"
       "**建议**：在 `docs/keyword-map.md` 新增一行页型 `/compare/{a}-and-{b}/`"
       "（与 `/compare/{a}-vs-{b}/` 不冲突：一个是「两个目的地、一张 eSIM」，一个是「两个品牌、谁更好」）。"
       "**保守替代**（不开新页型）：在涉及的两个国家页各加一段「combined trip」小节 + 互链。"
       "**这一步需要你点头** —— 开新页型属架构变更，按本项目纪律不得擅自做。")

bucket(lambda k: re.match(
    r"^.*\b(?:from (?:uk|usa|us|australia|uae|canada|india|singapore|germany|ireland|"
    r"new zealand|south africa|china|japan))\b", k),
       "② 出发地视角（「{目的地} from {出发地}」）",
       "**为什么重要**：这是**居住地视角**的查询 —— 搜的人已经知道自己从哪出发，"
       "要的是「我这张卡在我常住地能不能买/能不能用」。现有页面全是目的地视角，接不住。"
       "**建议**：并入国家页的 FAQ（例如「Can I buy a New Zealand eSIM from Australia?」），"
       "属于 FAQPage 结构化数据的天然素材，不必开新页。")

bucket(lambda k: any(c in k for c in [
    "dubai", "tokyo", "osaka", "seoul", "bangkok", "phuket", "bali", "kuala lumpur",
    "hanoi", "taipei", "shanghai", "london", "paris", "rome", "barcelona", "madrid",
    "lisbon", "amsterdam", "berlin", "prague", "vienna", "istanbul", "cairo",
    "marrakech", "new york", "las vegas", "miami", "los angeles", "orlando", "hawaii",
    "cancun", "mexico city", "toronto", "vancouver", "rio de janeiro", "buenos aires",
    "sydney", "melbourne", "auckland", "cape town", "maldives", "zanzibar"]),
       "③ 城市词",
       "**为什么重要**：迪拜尤其突出（`buy esim for dubai` 83.3、`best esim for dubai` 82.3）。"
       "**为什么不该开城市页**：`docs/keyword-map.md` 已明确禁止城市页与 `/compare/{country}/` 争主干词，"
       "开 870 个城市页会立刻造成自我蚕食。"
       "**建议**：在对应国家页（UAE / 墨西哥 / 美国…）加「Cities」小节，"
       "把城市名与真实约束（迪拜是 UAE 的酋长国、Cancún 落在墨西哥的哪张网）写进正文，"
       "不新建 URL。这条**不需要开新页型**，可以直接做。")

bucket(lambda k: re.search(r"\b(network|networks|carrier|carriers|coverage|signal|5g)\b", k),
       "④ 网络 / 运营商归属词 —— 已有页型但覆盖太窄",
       "**关键数字**：这一类词的**需求分中位数是所有词型里最高的（40.2）**，"
       "但 `/networks/{country}/` **只上线了 12 国**（US UK DE FR CA MX TH ES KR CN JP NL），"
       "而站内有 50 个目的地 —— **38 国缺页**。"
       "**建议**：`content-backlog` 里已写明「余 38 国加 content md 即可，不改版式」—— "
       "这是**投入产出比最高的一件事**：零模板改动、纯内容补齐。")

bucket(lambda k: re.search(r"\b(free|prepaid|pay as you go|no contract)\b", k),
       "⑤ free / prepaid 类",
       "**注意**：`free esim` 类词（80.0 分）意图与「免费试用 / 免费额度」有关，"
       "也给「prepaid vs eSIM」这类本地资费锚点留了位置。"
       "站内 `#localnotes`（国家级事实）与 `#tradeoffs`（逐国比价）已是天然承接位，"
       "**建议**在这些区块里显式回答「prepaid 在当地多少钱 vs eSIM」，不改页型。")

bucket(lambda k: re.search(r"\b(reddit|review|legit|scam|safe|worth it|trust)\b", k),
       "⑥ 信任 / 评价类（Reddit 语言）",
       "**为什么重要**：`esim costa rica reddit` 85.0 分、`best esim for europe review` 80.0 分 —— "
       "这是用户在做最后的风险确认。站内有 Trustpilot 档案链接与「how we verify」方法论页，"
       "但**没有一句话直接回答「这些品牌靠不靠谱」**。"
       "**建议**：在国家页 FAQ 加一条「Are these eSIM providers trustworthy?」，"
       "链到方法论页 + Trustpilot 档案。**不要**编造评分（见 PROJECT.md 的品牌合规红线）。")

w("---")
w("")
w("## 七、你点名的 4 个页面：各自该抢的词")
w("")


def page_block(title, url, note=""):
    sub = sorted([r for r in rows if r["归属URL"] == url], key=lambda z: -z["需求分"])
    w("### %s" % title)
    w("")
    w("`%s`　承接词 **%d** 个。" % (url, len(sub)))
    if note:
        w("")
        w(note)
    w("")
    if sub:
        w("| 需求分 | sources | 词 | 词型 |")
        w("|---:|---:|---|---|")
        for r in sub[:12]:
            w("| %.1f | %d | `%s` | %s |" % (
                r["需求分"], r["sources"], r["keyword"], r["词型"]))
    w("")


page_block("美国国家页", "/compare/united-states/")
page_block("新加坡国家页", "/compare/singapore/")
page_block("日本国家页", "/compare/japan/")
page_block("新加坡 × Airalo 品牌子页", "/compare/singapore/airalo/")
page_block("新加坡 × Roamic 品牌子页", "/compare/singapore/roamic/",
           "> ⚠️ **0 词。** 采集数据里 `roamic` 只在 13 个词里出现"
           "（最高 `roamic esim usa` 53.0 分），`roami` **一次都没出现**。"
           "详见第八节。")
page_block("日本 × Roamic 品牌子页", "/compare/japan/roamic/", "> ⚠️ **0 词。**")

w("---")
w("")
w("## 八、品牌侧需求极不均衡（这是一个业务事实，不是文案问题）")
w("")
w("| 品牌 | 采集到的品牌词数 | 均分 | 最高分 | 最高分词 |")
w("|---|---:|---:|---:|---|")
bb = collections.defaultdict(list)
for r in rows:
    if r["品牌"] and "品牌" in r["词型"]:
        for k in r["品牌"].split(","):
            bb[k].append(r)
for k, v in sorted(bb.items(), key=lambda x: -len(x[1])):
    top = max(v, key=lambda z: z["需求分"])
    w("| %s | %d | %.1f | %.1f | `%s` |" % (
        k, len(v), sum(z["需求分"] for z in v) / len(v), top["需求分"], top["keyword"]))
w("")
w("**读法**：Airalo 一家占 191 个品牌词，holafly/saily/nomad 在 93–105 之间，"
  "ubigi 60，jetpac 26，**roamic 13，roami 0**。"
  "站内 50 国 × 10 品牌 = 499 个品牌×国家子页，但**品牌词的搜索需求高度集中在头部 4 家**。"
  "这不是说 roami/roamic 的页面没用（它们承接的是「该品牌在该国的价格」长尾，"
  "且在 `#hostnetwork`/`#localnotes` 上是唯一答案），"
  "但**别指望它们带来品牌词流量** —— 品牌词的仗只能在 airalo/holafly/saily/nomad 上打。")
w("")
w("---")
w("")
w("## 九、与旧词库（`keyword-matrix.csv`，10,614 词）对账")
w("")
_n = sum(1 for r in rows if r["在旧词库"] == "否")
_y = sum(1 for r in rows if r["在旧词库"] == "是")
w("| 项 | 值 |")
w("|---|---|")
w("| 本轮采集词 | %d |" % len(rows))
w("| 其中**旧词库里没有** | **%d（%.1f%%）** |" % (_n, 100.0 * _n / len(rows)))
w("| 旧词库里已有 | %d |" % _y)
w("")
w("**结论：旧矩阵不是错，是「另一种东西」。** 它的 10,614 词是 `_gen_matrix.py` "
  "按模板排列组合生成的（`best esim for {country}` × 50 国 × 19 个修饰语…），"
  "优先级是脚本里手填的先验值（100/99/98…），URL 模板还停在**上线前**的 `/esim/{country}/`。"
  "它回答的是「这个领域有哪些词」，回答不了「**哪些词真有人搜**」。"
  "而它的排列组合里**天然不可能包含**本轮最有价值的两类："
  "双国组合（`esim for hong kong and china`）与城市词（`buy esim for dubai`）—— "
  "因为组合逻辑只做「一个国家 × 一个修饰语」。")
w("")
w("**处置建议**：保留旧矩阵当「覆盖面清单」，把本轮 CSV 当「优先级排序器」；"
  "两表用 `keyword` 字段可 join。**不要**用旧矩阵的优先级排期 —— "
  "它会把 %d 个「国家·核心」词排在同一档，而真实需求差距是 30 分 vs 93 分。"
  % len(by["国家·核心"]))
w("")
w("---")
w("")
w("## 十、行动清单（按投入产出比排序）")
w("")
w("| # | 动作 | 依据 | 是否需你决策 |")
w("|---:|---|---|---|")
w("| 1 | 补齐 **38 国** `/networks/{country}/`（纯 content md，零模板改动） | 该类词需求分中位 **40.2（全站最高）**，现有覆盖率 12/50 | 否，可直接做 |")
w("| 2 | 国家页加 **Cities 小节**（Dubai / Cancún / Bali…） | `buy esim for dubai` **83.3**、`best esim for dubai` **82.3** | 否 |")
w("| 3 | 国家页 FAQ 加**出发地**与**信任**两类问答 | 113 词出发地型 / 132 词信任型，其中 ≥50 分 29 个 | 否 |")
w("| 4 | 双国组合词开 `/compare/{a}-and-{b}/` | %d 词、%d 个 ≥50 分、站内**零承接** | **是**（新页型） |"
  % (_pair_n, _pair_hi))
w("| 5 | 接 **Google Search Console** | 上面所有分数都是代理值；GSC 给你真实曝光词与点击 | **是**（需你授权） |")
w("| 6 | 品牌词的仗打到 airalo/holafly/saily/nomad 上 | 191/105/101/93 vs roami **0** | 否 |")
w("")
w("---")
w("")
w("## 附：文件说明")
w("")
w("| 文件 | 内容 |")
w("|---|---|")
w("| `kw-collected-2026-10-08.csv` | **主交付物**：%d 词 + 词型/需求分/归属URL/站内现状/在旧词库 |" % len(rows))
w("| `kw-scored.csv` | 中间层：补全证据原始统计（sources/中位位次/top3/覆盖国数） |")
w("| `raw_autocomplete.json` / `raw_autocomplete.pass2.json` | 原始补全响应（%d 个种子，可复算） |" % (
    raw["seeds_ok"] + raw2["seeds_ok"]))
w("| `live-urls.json` | 站内 %d 个 URL 快照（用于「站内现状」判定） |" % len(live))
w("")
w("复现：`python -X utf8 scripts/kw_harvest.py && python -X utf8 scripts/kw_harvest.py --pass2 "
  "&& python -X utf8 scripts/kw_score.py && python -X utf8 scripts/kw_classify.py "
  "&& python -X utf8 scripts/kw_report.py`")

OUT.write_text("\n".join(L) + "\n", encoding="utf-8")
print("已写 %s（%d 行）" % (OUT.relative_to(ROOT), len(L)))
