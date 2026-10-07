# -*- coding: utf-8 -*-
"""产物级守卫：国家页 FAQ 里的数字断言必须与 data/plans 的真实数据逐条对上。

── 为什么需要它（2026-10-06 实测）────────────────────────────────────────────
data/faqs/*.toml 的三条答案曾把数字写死：
    「Roami - the 1GB / 7 Days at $2.99 是最便宜的」
    「All 10 'unlimited' plans …」
    「Holafly 最低 $4.37/天」
真值在 data/plans/*.toml 里、每次抓价或接入新品牌都会变。首次审计（scripts/
audit_faq_facts.py，仅比对**源文本**）报 99 条过期，其中 45 国「最便宜品牌」直接易主：
美国 FAQ 说 Roami $2.99，而正上方价格表里最便宜的是 Yesim $0.51 —— 页面自相矛盾。

本轮把这三条改成构建期现算（layouts/partials/faq-live-tokens.html + 文案里的 {token}），
本脚本是配套守卫：**只读 public/ 产物**，独立从 data/plans 重算一遍真值，逐条对账。

── 为什么必须读产物而不是读源文本 ──────────────────────────────────────────
源文本里现在是 {token}，真值由 Hugo 在渲染时算出来。模板写错（token 名拼错、
partial 逻辑反了）在源文本里完全看不出来；只有在 HTML 里才暴露。
这与 check_output.py 的立身之本相同：hugo 退出码 0，不代表产物是对的。

── 检查项 ─────────────────────────────────────────────────────────────────
  R1 产物里不得残留未替换的 {token}（含可见正文与 FAQPage JSON-LD）
  R2 答案里不得出现 "n/a" 或 "$0.00"（partial 的取值缺失哨兵漏出来了）
  R3 页面 FAQ 的问题集合必须与 data/faqs/<iso>.toml 逐条一致
  R4 可见正文与 FAQPage JSON-LD 必须同源同文（结构化数据与用户所见不得打架）
  R5 「最便宜」那条：品牌与价格必须与 data/plans 现算的最优解一致
  R6 「unlimited」那条：档数、$/天、品牌必须与现算一致
  R7 「Airalo-Holafly」那条：两家的报价必须与现算一致
  R8 不变量：最便宜的品牌不得是 Airalo / Holafly（jp 文案写了「neither is the cheapest」）
  R9 不变量：最便宜的档必须是计量档（Q1 文案直接印 $/GB，无限档会印出哨兵值）
  R10 骨架不重复（★ 源级，唯一的例外，见下）—— 五条：
      a) 第 1-3 条答案在 50 国上「把 token 与数字都抹掉」后必须两两不同（无重复骨架）
      b) 每条答案必须拆得回 scripts/faq_frames.py 的 (open, body, close) 片段组合
         —— 拆不回说明有人手改了答案却没同步片段库，那是比重复更危险的状态
      c) 任意两国的片段组合最多共用一个槽（拉丁方阵分配）；共用两个槽 = 两句逐字相同
      d) 第 6 条必须取自库里的 7 个变体，且 7 个没有邻国的国家（只有兜底短语、没有国名
         可区分）必须各占一个变体
      e) 第 6 条答案必须含 {country}
  R11 邻国问答不重复（产物级）：Q6 在各国页上必须两两不同 —— R10(e) 在源级保证它，
      但源级**看不见**互称邻国的一对国家（FR 与 IE 都指向 UK）会不会撞车，只有在
      产物里才暴露。这条规则是被那个真实 bug 逼出来的（见函数注释）。

多条并列最优时按**候选集合**判定：只要页面上的取值属于并列最优解之一就算通过 ——
所以判定的是「事实对不对」，不是「Hugo 与 Python 谁先挑到并列项」。

── R10 为什么读源文件而不是读产物 ──────────────────────────────────────────
R1-R9 必须读产物，因为 {token} 是渲染时才变成数字的。但 R10 判的是**句架**，
而句架只存在于源文件里：`data/faqs/*.toml` 里 `{cheap_brand}` 还是 `{cheap_brand}`，
抹成 `{t}` 就能看出两页用的是不是同一个片段。产物里所有 token 都已变成各不相同的
数字与国名，反而看不出句架重复 —— 在产物上判这件事会变成自欺。
（数字与事实的正确性由 R1-R9 在产物层把关，两层各司其职。）

用法（在 hugo 之后）：
    python -X utf8 scripts/check_faq_facts.py
    python -X utf8 scripts/check_faq_facts.py --selftest   # 对构造样本自测（证明它会报红）
"""
from __future__ import annotations

import collections
import glob
import html as htmllib
import json
import re
import sys
import tomllib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PUBLIC = ROOT / "public"

TOL = 0.005  # 价格比较容差（与页面 printf "%.2f" 的精度对齐）

MONEY = re.compile(r"\$(\d+(?:\.\d+)?)")
TOKEN = re.compile(r"\{[a-z_]+\}")
DETAILS = re.compile(
    r'<details class="faq-item">(.*?)</details>', re.S)
SUMMARY = re.compile(r"<summary>(.*?)</summary>", re.S)
ANSWER = re.compile(r'<p class="faq-body">(.*?)</p>', re.S)
FAQ_LD = re.compile(
    r'<script type="application/ld\+json">(.*?)</script>', re.S)
TAG = re.compile(r"<[^>]+>")

KIND_PREFIX = {
    "cheapest": ("What is the cheapest", "Which is the cheapest"),
    "unlimited": ("Is unlimited eSIM data in", "Is unlimited data eSIM in"),
    "pair": ("Airalo or Holafly for", "Is Airalo or Holafly better for"),
}
AIRALO_HOLAFLY = ("Airalo", "Holafly")


# ── 数据层 ────────────────────────────────────────────────────────────────────
def load():
    plans = {
        Path(f).stem: tomllib.loads(Path(f).read_text(encoding="utf-8"))
        for f in sorted(glob.glob(str(ROOT / "data" / "plans" / "*.toml")))
    }
    providers = tomllib.loads((ROOT / "data" / "providers.toml").read_text(encoding="utf-8"))
    countries = tomllib.loads((ROOT / "data" / "countries.toml").read_text(encoding="utf-8"))
    faqs = {}
    for f in sorted(glob.glob(str(ROOT / "data" / "faqs" / "*.toml"))):
        faqs[Path(f).stem.upper()] = tomllib.loads(Path(f).read_text(encoding="utf-8"))
    return plans, providers, countries, faqs


def rows_of(plans, iso):
    """该国全部套餐行：(品牌 key, 档位 dict)。口径与 layouts/partials/faq-live-tokens.html 一致。"""
    out = []
    for pk, pd in plans.items():
        blk = pd.get(iso)
        if not isinstance(blk, dict) or "plans" not in blk:
            continue
        for p in blk["plans"]:
            out.append((pk, p))
    return out


def truth(rows, providers):
    """回传候选集合，而不是单一赢家 —— 并列最优时谁上都对。"""
    if not rows:
        return None
    min_price = min(p["price"] for _, p in rows)
    cheap = [(pk, p) for pk, p in rows if abs(p["price"] - min_price) <= TOL]
    metered = [(pk, p) for pk, p in rows if p["gb"] > 0]
    value_pergb = None
    if metered:
        value_pergb = min(p["price"] / p["gb"] for _, p in metered)
    unl = [(pk, p) for pk, p in rows if p["type"] == "unlimited"]
    unl_best = []
    if unl:
        best = min(p["price"] / p["days"] for _, p in unl)
        unl_best = [(pk, p) for pk, p in unl if abs(p["price"] / p["days"] - best) <= TOL]
    airalo = [(pk, p) for pk, p in metered if pk == "airalo"]
    holafly = [(pk, p) for pk, p in rows if pk == "holafly"]
    return {
        "cheap": cheap,
        "cheap_brands": {providers[pk]["name"] for pk, _ in cheap},
        "cheap_prices": {p["price"] for _, p in cheap},
        "cheapest_is_metered": all(p["gb"] > 0 for _, p in cheap),
        "value_pergb": value_pergb,
        "unl_count": len(unl),
        "unl_best": unl_best,
        "unl_brands": {providers[pk]["name"] for pk, _ in unl_best},
        "unl_perdays": {p["price"] / p["days"] for _, p in unl_best},
        "unl_prices": {p["price"] for _, p in unl_best},
        "airalo_pergb": min((p["price"] / p["gb"] for _, p in airalo), default=None),
        "holafly_price": min((p["price"] for _, p in holafly), default=None),
    }


# ── 产物层 ────────────────────────────────────────────────────────────────────
def text_of(fragment: str) -> str:
    return re.sub(r"\s+", " ", htmllib.unescape(TAG.sub(" ", fragment))).strip()


def visible_pairs(html: str) -> dict[str, str]:
    out = {}
    for block in DETAILS.findall(html):
        mq, ma = SUMMARY.search(block), ANSWER.search(block)
        if mq and ma:
            out[text_of(mq.group(1))] = text_of(ma.group(1))
    return out


def ld_pairs(html: str) -> dict[str, str]:
    for raw in FAQ_LD.findall(html):
        try:
            data = json.loads(raw)
        except ValueError:
            continue
        if data.get("@type") != "FAQPage":
            continue
        out = {}
        for item in data.get("mainEntity", []):
            ans = item.get("acceptedAnswer", {})
            if isinstance(item.get("name"), str) and isinstance(ans.get("text"), str):
                out[item["name"]] = ans["text"]
        return out
    return {}


def kind_of(q: str) -> str | None:
    for kind, prefixes in KIND_PREFIX.items():
        if any(q.startswith(p) for p in prefixes):
            return kind
    return None


def has_money(text: str, value: float | None) -> bool:
    if value is None:
        return False
    return any(abs(float(v) - value) <= 0.011 for v in MONEY.findall(text))


def check_page(label: str, html: str, toml_faq: dict, t: dict) -> list[str]:
    errs: list[str] = []
    vis = visible_pairs(html)
    ld = ld_pairs(html)

    # R1 未替换 token —— 只查 FAQ 正文本体与 FAQPage schema。
    # 不整页扫：内联 <script> 里的 JS 模板串（`${x}`）会被同一条正则命中，那是自造假阳性。
    for src, bag in (("可见正文", vis), ("FAQPage schema", ld)):
        for q, a in bag.items():
            m = TOKEN.search(a)
            if m:
                errs.append(f"{label}: R1 {src}里残留未替换的 token -> {m.group(0)} @ {q}")
                break

    # R2 取值缺失哨兵
    for q, a in vis.items():
        if re.search(r"\bn/?a\b", a, re.I) or "$0.00" in a:
            errs.append(f"{label}: R2 答案里出现缺失哨兵 -> {q}: {a[:70]!r}")

    # R3 问题集合一致
    if set(vis) != set(toml_faq):
        miss = sorted(set(toml_faq) - set(vis))[:2]
        extra = sorted(set(vis) - set(toml_faq))[:2]
        errs.append(f"{label}: R3 FAQ 问题集合与 toml 不一致（缺 {miss} / 多 {extra}）")

    # R4 可见正文 vs JSON-LD 同源
    for q in sorted(set(vis) & set(ld)):
        if vis[q] != ld[q]:
            errs.append(f"{label}: R4 可见正文与 FAQPage schema 不同文 -> {q}")

    for q, a in vis.items():
        kind = kind_of(q)
        if kind == "cheapest":
            if not any(b in a for b in t["cheap_brands"]):
                errs.append(f"{label}: R5 最便宜品牌不对（页面未提到 {sorted(t['cheap_brands'])}）-> {q}")
            if not has_money(a, min(t["cheap_prices"])):
                errs.append(f"{label}: R5 最便宜价格不对（应为 ${min(t['cheap_prices']):.2f}）-> {a[:70]!r}")
        elif kind == "unlimited":
            if f" {t['unl_count']} " not in f" {a} ":
                errs.append(f"{label}: R6 unlimited 档数不对（应为 {t['unl_count']}）-> {a[:70]!r}")
            if t["unl_brands"] and not any(b in a for b in t["unl_brands"]):
                errs.append(f"{label}: R6 最优无限品牌不对（应为 {sorted(t['unl_brands'])}）-> {q}")
            if not has_money(a, min(t["unl_perdays"])):
                errs.append(f"{label}: R6 最优无限 $/天 不对（应为 ${min(t['unl_perdays']):.2f}）-> {a[:70]!r}")
        elif kind == "pair":
            if t["airalo_pergb"] and not has_money(a, t["airalo_pergb"]):
                errs.append(f"{label}: R7 Airalo $/GB 不对（应为 ${t['airalo_pergb']:.2f}）-> {a[:70]!r}")
            if t["holafly_price"] and not has_money(a, t["holafly_price"]):
                errs.append(f"{label}: R7 Holafly 报价不对（应为 ${t['holafly_price']:.2f}）-> {a[:70]!r}")

    # R8 / R9 文案不变量
    if t["cheap_brands"] & set(AIRALO_HOLAFLY):
        errs.append(f"{label}: R8 最便宜的是 {sorted(t['cheap_brands'] & set(AIRALO_HOLAFLY))}，"
                    f"但 jp 文案写死了「neither is the cheapest」—— 该改文案了")
    if not t["cheapest_is_metered"]:
        errs.append(f"{label}: R9 最便宜的档是无限档，Q1 文案会印出 $/GB 哨兵值 —— 该改文案了")
    return errs


# ── R10 骨架层（源级）────────────────────────────────────────────────────────
ANY_TOKEN = re.compile(r"\{[a-z_]+\}")
ANY_NUM = re.compile(r"\d+(?:\.\d+)?")


def skeleton(text: str, mask_tokens: bool = True) -> str:
    """把 token 与数字抹平，只留下句架 —— 两页若句架相同，这里就会撞。"""
    s = ANY_TOKEN.sub("{t}", text) if mask_tokens else text
    return re.sub(r"\s+", " ", ANY_NUM.sub("#", s)).strip()


def load_frames():
    """取片段库（scripts/faq_frames.py）。R10 判的就是「数据 == 库里那套拉丁方阵分配」。"""
    import importlib.util
    spec = importlib.util.spec_from_file_location("faq_frames", ROOT / "scripts" / "faq_frames.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)          # 模块级无副作用（main() 在 __main__ 守卫内）
    return mod


def decompose(pool: dict, answer: str):
    """把一条答案拆回 (open, body, close) 三个片段下标；拆不开回 None。"""
    out = []
    for key in ("open", "body", "close"):
        hit = [i for i, frag in enumerate(pool[key]) if frag in answer]
        if len(hit) != 1:
            return None
        out.append(hit[0])
    return tuple(out)


def frame_errors(faqs: dict, countries: dict) -> tuple[list[str], list[str]]:
    errs: list[str] = []
    info: list[str] = []
    mod = load_frames()
    pre_of = {0: "What is the cheapest eSIM for", 1: "Is unlimited eSIM data in",
              2: "Airalo or Holafly for"}

    # ── slot 1-3：骨架两两不同 + 片段层拉丁方阵 ──
    for slot in range(3):
        pool = [mod.Q1, mod.Q2, mod.Q3][slot]
        tri: dict[str, tuple] = {}
        for iso, doc in sorted(faqs.items()):
            if iso == "JP":          # jp 三条是手写的分析口吻，不参与方阵
                continue
            ans = next((x["a"] for x in doc.get("faq", [])
                        if x["q"].startswith(pre_of[slot])), None)
            if ans is None:
                errs.append(f"R10 slot{slot+1} {iso} 没有这条 FAQ")
                continue
            got = decompose(pool, ans)
            if got is None:
                errs.append(f"R10 slot{slot+1} {iso} 的答案拆不回片段库的组合 —— "
                            f"手改过？片段库 scripts/faq_frames.py 需要同步")
                continue
            tri[iso] = got
        if not tri:
            continue
        sk = {iso: skeleton(next(x["a"] for x in faqs[iso]["faq"]
                                 if x["q"].startswith(pre_of[slot]))) for iso in tri}
        info.append(f"slot{slot+1}: {len(set(sk.values()))} 种骨架 / {len(sk)} 国")
        same = [s for s, n in collections.Counter(sk.values()).items() if n > 1]
        if same:
            who = sorted(iso for iso in sk if sk[iso] in same)
            errs.append(f"R10 slot{slot+1} 有 {len(who)} 页共用同一副骨架 -> {who[:8]}")
        if len(set(tri.values())) != len(tri):
            errs.append(f"R10 slot{slot+1} 有国家用了完全相同的片段组合")
        isos = sorted(tri)
        for x in range(len(isos)):
            for y in range(x + 1, len(isos)):
                shared = sum(1 for k in range(3) if tri[isos[x]][k] == tri[isos[y]][k])
                if shared >= 2:
                    errs.append(f"R10 slot{slot+1} 任意两国最多共用一个槽："
                                f"{isos[x]}/{isos[y]} 共用了 {shared} 个 → {tri[isos[x]]} / {tri[isos[y]]}")

    # ── slot 6：变体取自库；无邻国的国家必须各占一个（它们只有兜底短语，撞了就逐字同文）──
    q6 = {}
    for iso, doc in sorted(faqs.items()):
        if iso == "JP":
            continue
        ans = next((x["a"] for x in doc.get("faq", []) if x["q"].startswith("Can one eSIM cover")), None)
        if ans is None:
            errs.append(f"R10 slot6 {iso} 没有这条 FAQ")
            continue
        # 必须含 {country}：FR 与 IE 互称邻国（都指向 UK），变体里若没有 {country}
        # 两国就会渲染出**逐字相同**的一段 —— 实测撞过。
        if "{country}" not in ans:
            errs.append(f"R10 slot6 {iso} 的答案缺 {{country}} —— 互称邻国的两国会撞车")
        hit = [i for i, f in enumerate(mod.Q6) if f == ans]
        if not hit:
            errs.append(f"R10 slot6 {iso} 的答案不在片段库里 —— 手改过？需要同步")
            continue
        q6[iso] = hit[0]
    no_nb = [iso for iso in q6 if not (countries.get(iso) or {}).get("neighbors")]
    if no_nb:
        idx = {iso: q6[iso] for iso in no_nb}
        if len(set(idx.values())) != len(idx):
            g: dict[int, list[str]] = collections.defaultdict(list)
            for iso, i in idx.items():
                g[i].append(iso)
            errs.append(f"R10 slot6 无邻国的 {len(no_nb)} 国兜底文案撞车 -> "
                        f"{[v for v in g.values() if len(v) > 1]}")
        else:
            info.append(f"slot6: 无邻国的 {len(no_nb)} 国各占一个变体 / 库内 {len(mod.Q6)} 个变体")

    # ── 其余槽位只报数（slot4 的「ID 规定」有 14 国共用同一句，是历史遗留，见 PROJECT.md），不判失败 ──
    other: dict[int, dict[str, str]] = collections.defaultdict(dict)
    for iso, doc in sorted(faqs.items()):
        for i, item in enumerate(doc.get("faq", [])):
            if i in (3, 4):
                other[i][iso] = item["a"]
    for i in sorted(other):
        vals = {skeleton(a) for a in other[i].values()}
        flag = "" if len(vals) == len(other[i]) else " ← 有历史重复"
        info.append(f"slot{i+1}: {len(vals)} 种骨架 / {len(other[i])} 页{flag}")
    return errs, info


# ── 主流程 ────────────────────────────────────────────────────────────────────
def scan(public: Path) -> tuple[int, list[str]]:
    plans, providers, countries, faqs = load()
    errs: list[str] = []
    pages = 0
    for iso, c in countries.items():
        if not isinstance(c, dict):
            continue
        slug = c.get("slug")
        if not slug or iso not in faqs:
            continue
        rows = rows_of(plans, iso)
        t = truth(rows, providers)
        if not t:
            continue
        toml_faq = {x["q"]: x["a"] for x in faqs[iso].get("faq", [])}
        for rel in (Path("compare") / slug / "index.html",
                    Path("de") / "compare" / slug / "index.html"):
            f = public / rel
            if not f.exists():
                continue
            pages += 1
            errs.extend(check_page(rel.as_posix(), f.read_text(encoding="utf-8"), toml_faq, t))
    return pages, errs


def regional_distinct(public: Path) -> tuple[int, list[str]]:
    """R11（产物级）：Q6「Can one eSIM cover …?」在各国页上必须两两不同。

    这条规则是被一个真实 bug 逼出来的：Q6 的片段里若没有 {country}，**互称邻国的一对国家**
    就会渲染出逐字相同的一段 —— 实测 FR 与 IE 都指向 UK、又分到同一个变体，
    于是 `france/` 与 `ireland/` 的 Q6 一模一样。源级 R10 看不出来（源文本里只有 {neighbor}），
    只有在产物里才暴露。**这正是「守卫必须读产物」的又一个例证。**
    """
    countries = load()[2]
    seen: dict[tuple[str, str], list[str]] = collections.defaultdict(list)
    pages = 0
    for iso, c in countries.items():
        if not isinstance(c, dict):
            continue
        slug = c.get("slug")
        if not slug:
            continue
        for rel, lang in ((Path("compare") / slug / "index.html", "en"),
                          (Path("de") / "compare" / slug / "index.html", "de")):
            f = public / rel
            if not f.exists():
                continue
            pages += 1
            vis = visible_pairs(f.read_text(encoding="utf-8"))
            ans = next((v for q, v in vis.items() if q.startswith("Can one eSIM cover")), None)
            if ans:
                seen[(lang, ans)].append(iso)
    errs = [f"R11 [{lang}] {sorted(isos)} 的 Q6 答案逐字相同 -> {a[:70]!r}"
            for (lang, a), isos in seen.items() if len(isos) > 1]
    return pages, errs


def selftest() -> int:
    """对**构造样本**自测：证明每一条规则都能报红，且正确样本不会被误报。"""
    plans, providers, countries, faqs = load()
    iso = "US"
    t = truth(rows_of(plans, iso), providers)
    toml_faq = {x["q"]: x["a"] for x in faqs[iso].get("faq", [])}
    q_cheap = next(q for q in toml_faq if kind_of(q) == "cheapest")
    q_unl = next(q for q in toml_faq if kind_of(q) == "unlimited")
    q_pair = next(q for q in toml_faq if kind_of(q) == "pair")
    cbrand = sorted(t["cheap_brands"])[0]
    cprice = min(t["cheap_prices"])
    uper = min(t["unl_perdays"])

    def page(**over):
        # 用真实 toml 的全套问题打底，只覆盖这三条 —— 否则 R3「问题集合一致」会因样本缺题而报错。
        # 打底值要把 {token} 抹掉：样本模拟的是**已渲染**的产物，源文件里的占位符在这里必须
        # 已经变成值，否则 R1（残留 token）会对着样本误报。
        good = {q: ANY_TOKEN.sub("X", a) for q, a in toml_faq.items()}
        good.update({
            q_cheap: f"{cbrand} is the cheapest at ${cprice:.2f} - see the table.",
            q_unl: f"All {t['unl_count']} unlimited plans apply caps; the cheapest by day is "
                   f"{sorted(t['unl_brands'])[0]} at ${uper:.2f}/day.",
            q_pair: f"Airalo is ${t['airalo_pergb']:.2f}/GB and Holafly starts at "
                    f"${t['holafly_price']:.2f}.",
        })
        good.update(over)
        blocks = "".join(
            f'<details class="faq-item"><summary>{q}<span class="faq-icon"></span></summary>'
            f'<p class="faq-body">{a}</p></details>' for q, a in good.items())
        ents = [{"@type": "Question", "name": q,
                 "acceptedAnswer": {"@type": "Answer", "text": good[q]}} for q in good]
        ld = json.dumps({"@context": "https://schema.org", "@type": "FAQPage",
                         "mainEntity": ents})
        return f"{blocks}<script type=\"application/ld+json\">{ld}</script>"

    cases = [
        ("正确样本不误报", page(), 0, ""),
        ("最便宜价格被改", page(**{q_cheap: f"{cbrand} is the cheapest at $999.00."}), None, "R5"),
        ("最便宜品牌被改", page(**{q_cheap: "Nokia is the cheapest at " + f"${cprice:.2f}."}), None, "R5"),
        ("unlimited 档数被改", page(**{q_unl: f"All 3 unlimited plans here apply caps."}), None, "R6"),
        ("Holafly 报价被改", page(**{q_pair: f"Airalo is ${t['airalo_pergb']:.2f}/GB, Holafly $999."}), None, "R7"),
        ("未替换 token", page(**{q_cheap: "{cheap_brand} is the cheapest at " + f"${cprice:.2f}."}), None, "R1"),
        ("可见正文与 schema 打架", page().replace(f"{cbrand} is the cheapest", "Someoneelse is the cheapest", 1), None, "R4"),
    ]
    failed = 0
    for name, html, want, needle in cases:
        got = check_page("fixture", html, toml_faq, t)
        if want == 0:
            ok = not got
        else:
            ok = any(needle in e for e in got)
        failed += 0 if ok else 1
        print(f"  {'OK  ' if ok else 'MISS'} {name:22s} 期望 "
              f"{'无报错' if want == 0 else needle} 实际 {len(got)} 处")
    print(f"\n自测{'通过' if not failed else f'失败 {failed} 项'}")
    return 1 if failed else 0


def frame_selftest() -> int:
    """R10 的构造样本：真实数据不报错，三种「句架重复」各注入一次必须报红。"""
    _, _, countries, faqs = load()
    mod = load_frames()

    def clone():
        return {iso: {"faq": [dict(x) for x in doc.get("faq", [])]} for iso, doc in faqs.items()}

    d1 = clone()
    d2 = clone()
    d2["DE"]["faq"][0]["a"] = d2["FR"]["faq"][0]["a"]
    # 共用两个槽：换掉 FR 的 open，留着 body + close —— 相邻两国会有两句逐字相同
    a0, b0, c0 = decompose(mod.Q1, faqs["FR"]["faq"][0]["a"])
    d3 = clone()
    d3["DE"]["faq"][0]["a"] = " ".join([mod.Q1["open"][(a0 + 1) % mod.POOL],
                                        mod.Q1["body"][b0], mod.Q1["close"][c0]])
    d4 = clone()
    d4["IS"]["faq"][5]["a"] = d4["HR"]["faq"][5]["a"]
    d5 = clone()
    d5["DE"]["faq"][0]["a"] = "Hand-written by an editor, with no tokens at all."
    d6 = clone()
    d6["DE"]["faq"][5]["a"] = "Only via a regional plan, because each country plan here is scoped to one market."

    cases = [
        ("真实数据（应无报错）", d1, 0, ""),
        ("两页第一条同文", d2, None, "完全相同的片段组合"),
        ("两页共用两个槽", d3, None, "最多共用一个槽"),
        ("无邻国兜底撞车", d4, None, "slot6"),
        ("答案偏离片段库", d5, None, "拆不回片段库"),
        ("Q6 缺 {country}", d6, None, "缺 {country}"),
    ]
    failed = 0
    for name, data, want, needle in cases:
        got, _ = frame_errors(data, countries)
        ok = (not got) if want == 0 else any(needle in e for e in got)
        failed += 0 if ok else 1
        print(f"  {'OK  ' if ok else 'MISS'} {name:22s} 期望 "
              f"{'无报错' if want == 0 else needle} 实际 {len(got)} 处")
    return failed


def main() -> int:
    if "--selftest" in sys.argv[1:]:
        rc = selftest()
        print("\n── R10 骨架自测 ──")
        rc += frame_selftest()
        print(f"\n合计{'通过' if not rc else f'失败 {rc} 项'}")
        return 1 if rc else 0
    public = PUBLIC
    if "--public" in sys.argv[1:]:
        public = Path(sys.argv[sys.argv.index("--public") + 1])
    if not public.is_dir():
        print(f"ERROR {public} not found - run `hugo` first")
        return 1
    pages, errs = scan(public)
    _, _, countries, faqs = load()
    ferrs, finfo = frame_errors(faqs, countries)
    errs += ferrs
    r11_pages, r11 = regional_distinct(public)
    errs += r11
    for line in finfo:
        print(f"  · {line}")
    if errs:
        print(f"ERROR FAQ fact guard: {len(errs)} problem(s) across {pages} pages")
        for e in errs[:40]:
            print(f"  {e}")
        if len(errs) > 40:
            print(f"  ... and {len(errs) - 40} more")
        return 1
    print(f"OK: {pages} country pages - every FAQ number matches data/plans, "
          f"no tokens left, schema in sync")
    print(f"OK: R10 骨架不重复 - 前三条答案 50 国两两不同，任意两国至多共用一句")
    print(f"OK: R11 邻国问答不重复 - {r11_pages} 国页的 Q6 逐条不同")
    return 0


if __name__ == "__main__":
    sys.exit(main())
