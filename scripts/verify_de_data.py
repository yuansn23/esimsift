"""德语数据覆盖层守卫（D6 剩余部分）—— 审核 data/de/{carriers,networkreports,providers}.toml
是否**逐字段**覆盖了英语侧会渲染到德语页的全部散文。

为什么需要它：Hugo 的 data 深合并对 **map 递归、数组整体替换**。
  · 少写一个国家 → 该国德语页静默回退英文（页面不报错、构建不失败）
  · 数组漏写一个元素 → 整个数组被替换成短的 → 静默丢内容
  · 英语侧改了措辞 → 德语侧成了「旧译文」，没人发现
这三类都不会让 Hugo 报错，所以必须在闸门里显式断言。

判据：
  A. 覆盖完整   —— 英语侧存在的每个散文单元，德语侧都有对应单元（按 ISO / brand / 数组下标对齐）
  B. 机器字段一致 —— profiles 的 name/tech/speed_min/speed_top、detail 的 carrier、
                    promo_alts 的 code/pct/audience 必须逐字继承（数组被替换时最容易丢）
  C. 译文确实不同 —— 德语值必须 ≠ 英语值（防「忘译当已译」）
  D. 数字守恒   —— 数值集合一致（容错小数逗号；`1.5 GB` → `1,5 GB` 是允许的）
  E. 产物级抽查 —— public/de 页面上不应出现这些英文串（专有名词白名单除外）
  F. 城市名     —— `info.cities` 只在「德语形式与英文不同」的国家写，且必须
                   与英文侧**等长**、与 CITY_DE 一致；产物级断言德语页上
                   不出现该国的英文城市名、且德语城市名确实出现。
                   ★ CITY_DE 的**唯一真源**在 `scripts/_gen_de_data.py`，
                     本脚本用 ast 读它 —— 绝不抄第二份（抄了就会漂移）。
  G. 日期本地化  —— `opensignal_date` 与顶层 `accessed` 是**可见文案**
                   （compare/single.html 的 eyebrow 与正文、networks/list.html 的来源行），
                   必须 1:1 本地化，且不得残留**形变**英文月名。
                   ⚠ April / August / September / November 德英**同形**，不在黑名单内
                     —— 拿全部 12 个月名当黑名单会把正确的德语写法误伤
                     （同类事故：`.buildlog/audit_de_lang.py` 曾因把 unlimited/data/
                     plans 等德语借词当英语，一次性假红 1389 段）。
                   ★ 月名映射的**唯一真源**在 `scripts/_loc_de_dates.py`，本脚本 import 它。

用法：
  python -X utf8 scripts/verify_de_data.py            # 全量
  python -X utf8 scripts/verify_de_data.py --selftest  # 注入反例，证明检查会变红
"""
from __future__ import annotations

import argparse
import ast
import html
import pathlib
import re
import sys
import tomllib

ROOT = pathlib.Path(__file__).resolve().parent.parent
DATA = ROOT / "data"
DE = DATA / "de"
PUB = ROOT / "public" / "de"

PROBLEMS: list[str] = []


def fail(msg: str) -> None:
    PROBLEMS.append(msg)


def load(p: pathlib.Path) -> dict:
    return tomllib.loads(p.read_text(encoding="utf-8"))


def load_city_map() -> dict:
    """从生成器源码里取出 CITY_DE（城市德语形式）。

    ★ 唯一真源在 `scripts/_gen_de_data.py`。守卫**读**它、不抄它 ——
      抄一份就是第二处会漂移的事实（本项目的老毛病）。
      用 ast 而不是 import：import 会**执行**生成器（它会真的写 data/de/*.toml），
      守卫必须是只读的。
    """
    src = (ROOT / "scripts" / "_gen_de_data.py").read_text(encoding="utf-8")
    for node in ast.parse(src).body:
        if isinstance(node, ast.Assign) and any(
                getattr(t, "id", None) == "CITY_DE" for t in node.targets):
            got = ast.literal_eval(node.value)
            if not isinstance(got, dict):
                break
            return got
    fail("在 scripts/_gen_de_data.py 里找不到 CITY_DE（城市名的唯一真源）")
    return {}


CITY_MAP = load_city_map()


def digits(s: str) -> set:
    """数值集合（小数逗号归一化）。
    ⚠ 比的是**集合**不是多重集：德语常把第三方奖项名连同英文原名加括注
      （`Zeit in 5G (Time on 5G)`），那会让 `5G` 出现两次，但并没有引入新数值。
      真正要拦的是「引入了原文没有的数字」或「漏掉了原文的数字」→ 集合相等即可。"""
    raw = re.findall(r"\d+(?:[.,]\d+)?", s or "")
    return set(float(x.replace(",", ".")) for x in raw)


UNIT_TOKENS = {"Mbps", "Kbps", "Gbps", "GB", "MB", "TB", "gb", "mb", "day", "days",
               "Tag", "Tage", "GB/Tag", "MB/Tag"}


def is_unit_only(s: str) -> bool:
    """纯单位串（"1 Mbps" / "512 Kbps" / "30 GB/Tag"）—— 这类值本来就不该有译文，
    英语德语逐字相同是**正确**的，不能判成「未译」。"""
    toks = re.findall(r"[A-Za-z/]+", s or "")
    return bool(toks) and all(t in UNIT_TOKENS for t in toks)


def untranslated(en: str, de: str) -> bool:
    """德语值与英语值逐字相同，且不是「纯单位串」→ 视为未译。"""
    return en == de and not (is_unit_only(en) and is_unit_only(de))


# ─────────────────────────── 源级检查 ───────────────────────────
def check_carriers(en: dict, de: dict, strict=True) -> None:
    for iso, v in en.items():
        prof = v.get("profiles") or []
        det = (v.get("info") or {}).get("detail") or []
        if not prof and not det:
            continue
        dv = de.get(iso)
        if dv is None:
            fail(f"carriers[{iso}] 德语侧整国缺失（{len(prof)} profiles / {len(det)} detail 会回退英文）")
            continue
        dprof = dv.get("profiles") or []
        if len(dprof) != len(prof):
            fail(f"carriers[{iso}].profiles 条数不符：英 {len(prof)} / 德 {len(dprof)}（数组整体替换 → 多出的元素静默变英文或丢失）")
        for i, (a, b) in enumerate(zip(prof, dprof)):
            for f in ("name", "tech", "speed_min", "speed_top"):
                if a.get(f) != b.get(f):
                    fail(f"carriers[{iso}].profiles[{i}].{f} 机器字段被改动：{a.get(f)!r} → {b.get(f)!r}")
            if a.get("note") and (not b.get("note")):
                fail(f"carriers[{iso}].profiles[{i}].note 缺德语")
            elif a.get("note") and untranslated(a["note"], b["note"]):
                fail(f"carriers[{iso}].profiles[{i}].note 与英文逐字相同（未译）")
            elif a.get("note") and digits(a["note"]) != digits(b["note"]):
                fail(f"carriers[{iso}].profiles[{i}].note 数字不符 {digits(a['note'])} → {digits(b['note'])}")
        ddet = (dv.get("info") or {}).get("detail") or []
        if len(ddet) != len(det):
            fail(f"carriers[{iso}].info.detail 条数不符：英 {len(det)} / 德 {len(ddet)}")
        for i, (a, b) in enumerate(zip(det, ddet)):
            if a.get("carrier") != b.get("carrier"):
                fail(f"carriers[{iso}].info.detail[{i}].carrier 被改动：{a.get('carrier')!r} → {b.get('carrier')!r}")
            for f in ("strong", "weak"):
                if a.get(f) and not b.get(f):
                    fail(f"carriers[{iso}].info.detail[{i}].{f} 缺德语")
                elif a.get(f) and untranslated(a[f], b[f]):
                    fail(f"carriers[{iso}].info.detail[{i}].{f} 与英文逐字相同（未译）")
                elif a.get(f) and digits(a[f]) != digits(b[f]):
                    fail(f"carriers[{iso}].info.detail[{i}].{f} 数字不符")
        # F 城市名：`info.cities` 是数组（整体替换），但只有**德语形式与英文不同**
        #   的国家才该写。原先把 cities 一并归入「故意不写」是错的 —— 城市名不是
        #   散文，它有既定德语形式（Vienna→Wien / The Hague→Den Haag），
        #   德语页上印 `Vienna` 与印 `Munich` 一样刺眼。
        dinf = dv.get("info") or {}
        ec = (v.get("info") or {}).get("cities") or []
        dc = dinf.get("cities")
        want = CITY_MAP.get(iso) or {}
        dead = [k for k in want if k not in ec]
        if dead:
            fail(f"CITY_DE[{iso}] 里的英文名不在 data/carriers.toml 的城市列表里（死条目）：{dead}")
        if want:
            if dc is None:
                fail(f"carriers[{iso}].info.cities 缺德语覆盖：英语侧 {ec} 中的 "
                     f"{list(want)} 有既定德语形式")
            elif len(dc) != len(ec):
                fail(f"carriers[{iso}].info.cities 条数不符：英 {len(ec)} / 德 {len(dc)}")
            else:
                exp = [want.get(c, c) for c in ec]
                if list(dc) != exp:
                    fail(f"carriers[{iso}].info.cities 与 CITY_DE 不符：{list(dc)} ≠ {exp}")
        elif dc is not None:
            fail(f"carriers[{iso}].info.cities 写了 {list(dc)}，但 CITY_DE 里没有该国的德语形式"
                 f"（要么把它加进 CITY_DE，要么删掉这段死条目）")
        # trips 只有品牌名与数字（机器字段），必须继承英语侧
        if "trips" in dinf:
            fail(f"carriers[{iso}].info.trips 德语侧不该写（数组整体替换会覆盖英语侧）")


def check_reports(en: dict, de: dict) -> None:
    for iso, v in en.items():
        if not isinstance(v, dict):
            continue
        facts = v.get("opensignal_facts") or []
        note = v.get("ookla_note")
        awards = v.get("awards") or []
        if not facts and not note and not awards:
            continue
        dv = de.get(iso)
        if dv is None:
            fail(f"networkreports[{iso}] 德语侧缺失")
            continue
        df = dv.get("opensignal_facts")
        if facts and df is None:
            fail(f"networkreports[{iso}].opensignal_facts 缺德语")
        elif facts:
            if len(df) != len(facts):
                fail(f"networkreports[{iso}].opensignal_facts 条数不符：英 {len(facts)} / 德 {len(df)}")
            for i, (a, b) in enumerate(zip(facts, df)):
                if a == b:
                    fail(f"networkreports[{iso}].opensignal_facts[{i}] 未译")
                elif digits(a) != digits(b):
                    fail(f"networkreports[{iso}].opensignal_facts[{i}] 数字不符")
        if note:
            if not dv.get("ookla_note"):
                fail(f"networkreports[{iso}].ookla_note 缺德语")
            elif untranslated(note, dv["ookla_note"]):
                fail(f"networkreports[{iso}].ookla_note 未译")
            elif digits(note) != digits(dv["ookla_note"]):
                fail(f"networkreports[{iso}].ookla_note 数字不符")
        # 记分板（awards）—— `layouts/networks/single.html` ⑭b 的逐网表格。
        # ★★ 为什么单列这一段（2026-10-10 第七十二轮 d44 实测）：
        #   `awards` 是**数组**，Hugo 深合并对它「整体替换」。在本轮之前德语侧
        #   一组都没写 —— 但那 46 个国家的德语 networks 页**尚未建出**，所以：
        #     · F（黑名单）绿 —— 没有德语页承载这些串
        #     · G（只认「已进 strings.toml 的数据串」）绿 —— awards 从未进表，G 天然失明
        #   批 D 建出 12 篇 `/de/networks/*.md` 后页集一变，12 条 F 立刻炸出；
        #   而 F 只抓到含 `and`/`every` 的 12 条，**真实残留是全量 35 组 × 3 字段**。
        #   黑名单永远是下限 ⇒ 覆盖完整性只能靠这里逐字段对齐来断言。
        dawards = dv.get("awards")
        if awards and dawards is None:
            fail(f"networkreports[{iso}].awards 缺德语（{len(awards)} 组记分板会整表回退英文）")
        elif awards:
            if len(dawards) != len(awards):
                fail(f"networkreports[{iso}].awards 组数不符：英 {len(awards)} / 德 {len(dawards)}"
                     f"（数组整体替换 → 多出的组静默变英文或丢失）")
            else:
                for i, (a, b) in enumerate(zip(awards, dawards)):
                    # carrier 是模板建 carrier→award 映射的键，必须是专有名词原样
                    if a.get("carrier") != b.get("carrier"):
                        fail(f"networkreports[{iso}].awards[{i}].carrier 被改动："
                             f"{a.get('carrier')!r} → {b.get('carrier')!r}（模板按它建映射，改了会整行错位）")
                    for f in ("opensignal", "ookla", "best"):
                        ea, db = a.get(f, ""), b.get(f, "")
                        if ea and not db:
                            fail(f"networkreports[{iso}].awards[{i}].{f} 缺德语")
                        elif ea and untranslated(ea, db):
                            fail(f"networkreports[{iso}].awards[{i}].{f} 与英文逐字相同（未译）")
                        elif ea and digits(ea) != digits(db):
                            fail(f"networkreports[{iso}].awards[{i}].{f} 数字不符 "
                                 f"{sorted(digits(ea))} → {sorted(digits(db))}")
        elif dawards:
            fail(f"networkreports[{iso}].awards 德语侧多出（英语侧没有该数组，死条目）")
        # 机器字段不得被改写
        # ⚠ `opensignal_date` **故意不在**这张清单里 —— 它不是机器字段，
        #   是可见文案，由判据 G 断言必须本地化（见 check_report_dates）。
        for k in ("opensignal_title", "opensignal_url", "ookla_slug", "ookla_mobile", "ookla_url", "ookla_date"):
            if k in dv:
                fail(f"networkreports[{iso}].{k} 德语侧不该写（机器字段应继承英语侧）")


# --- 判据 G：日期字段本地化 ---------------------------------------------------
# 月名映射的**唯一真源**在 _loc_de_dates.py（那里还有 1:1 的施加逻辑与自测）。
# 本脚本 import 它，绝不抄第二份 —— 抄一份就是第二处会错的地方。
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from _loc_de_dates import EN_ONLY_MONTH, de_month  # noqa: E402

_MONTH_ANY = re.compile(r"(?<![A-Za-z])(" + "|".join(EN_ONLY_MONTH) + r")(?![A-Za-z])")


def check_report_dates(en: dict, de: dict) -> None:
    """判据 G：英语侧有 `opensignal_date` 的每个国家，德语侧都要有，且是德语月名。"""
    want: dict[str, str] = {}
    for iso, v in en.items():
        if not isinstance(v, dict) or not v.get("opensignal_date"):
            continue
        got = de_month(v["opensignal_date"])
        if got is None:
            fail(f"networkreports[{iso}].opensignal_date 形态无法本地化: "
                 f"{v['opensignal_date']!r}")
            continue
        want[iso] = got

    have = {iso: v["opensignal_date"] for iso, v in de.items()
            if isinstance(v, dict) and "opensignal_date" in v}

    for iso in sorted(set(want) - set(have)):
        fail(f"networkreports[{iso}].opensignal_date 缺德语覆盖（德语页会印英文月名）")
    for iso in sorted(set(have) - set(want)):
        fail(f"networkreports[{iso}].opensignal_date 德语侧多出（英语侧没有该字段）")
    for iso in sorted(set(want) & set(have)):
        if have[iso] != want[iso]:
            fail(f"networkreports[{iso}].opensignal_date 应为 {want[iso]!r}，"
                 f"实际 {have[iso]!r}")
    for iso, v in sorted(have.items()):
        m = _MONTH_ANY.search(v)
        if m:
            fail(f"networkreports[{iso}].opensignal_date 仍含英文月名 "
                 f"{m.group(1)!r}：{v!r}")

    # 顶层 accessed —— 同样是可见文案
    en_acc = en.get("accessed")
    if en_acc:
        want_acc = de_month(en_acc)
        if de.get("accessed") != want_acc:
            fail(f"networkreports.accessed 应为 {want_acc!r}，实际 {de.get('accessed')!r}")
        elif _MONTH_ANY.search(str(want_acc)):
            fail(f"networkreports.accessed 仍含英文月名：{want_acc!r}")
    extra = [k for k, v in de.items() if not isinstance(v, dict) and k != "accessed"]
    if extra:
        fail(f"networkreports 德语侧出现非预期顶层标量: {extra}")


POL_TXT = ["hotspot_allowance", "hotspot_note", "fup_note", "topup_note"]
POL_SHOW = ["fup_allowance", "fup_drop"]
PROMO_TXT = ["promo_scope", "promo_coverage", "promo_bestfor", "promo_uncond_short",
             "promo_terms", "promo_expiry_note"]


def check_providers(en: dict, de: dict) -> None:
    for brand, v in en.items():
        dv = de.get(brand)
        if dv is None:
            fail(f"providers[{brand}] 德语侧缺失")
            continue
        if v.get("tagline"):
            if not dv.get("tagline"):
                fail(f"providers[{brand}].tagline 缺德语")
            elif untranslated(v["tagline"], dv["tagline"]):
                fail(f"providers[{brand}].tagline 未译")
        for k in ("strengths", "weaknesses"):
            arr = v.get(k) or []
            if not arr:
                continue
            darr = dv.get(k)
            if darr is None:
                fail(f"providers[{brand}].{k} 缺德语（数组整体替换）")
                continue
            if len(darr) != len(arr):
                fail(f"providers[{brand}].{k} 条数不符：英 {len(arr)} / 德 {len(darr)}")
            for i, (a, b) in enumerate(zip(arr, darr)):
                if a == b:
                    fail(f"providers[{brand}].{k}[{i}] 未译")
                elif digits(a) != digits(b):
                    fail(f"providers[{brand}].{k}[{i}] 数字不符")
        pol_en = v.get("policy") or {}
        pol_de = dv.get("policy") or {}
        for k in POL_TXT + POL_SHOW:
            if isinstance(pol_en.get(k), str) and pol_en[k]:
                if not pol_de.get(k):
                    fail(f"providers[{brand}].policy.{k} 缺德语")
                elif untranslated(pol_en[k], pol_de[k]):
                    fail(f"providers[{brand}].policy.{k} 未译")
                elif digits(pol_en[k]) != digits(pol_de[k]):
                    fail(f"providers[{brand}].policy.{k} 数字不符 {digits(pol_en[k])} → {digits(pol_de[k])}")
        for k in PROMO_TXT:
            if isinstance(v.get(k), str) and v[k]:
                if not dv.get(k):
                    fail(f"providers[{brand}].{k} 缺德语")
                elif untranslated(v[k], dv[k]):
                    fail(f"providers[{brand}].{k} 未译")
        for k in ("promo_constraints",):
            arr = v.get(k) or []
            if arr:
                darr = dv.get(k)
                if not darr or len(darr) != len(arr):
                    fail(f"providers[{brand}].{k} 缺德语/条数不符")
                else:
                    for i, (a, b) in enumerate(zip(arr, darr)):
                        if a == b:
                            fail(f"providers[{brand}].{k}[{i}] 未译")
        pts = v.get("promo_uncond_points") or []
        dpts = dv.get("promo_uncond_points") or []
        if pts and len(dpts) != len(pts):
            fail(f"providers[{brand}].promo_uncond_points 条数不符：英 {len(pts)} / 德 {len(dpts)}")
        alts = v.get("promo_alts") or []
        dalts = dv.get("promo_alts") or []
        if alts:
            if len(dalts) != len(alts):
                fail(f"providers[{brand}].promo_alts 条数不符：英 {len(alts)} / 德 {len(dalts)}")
            for i, (a, b) in enumerate(zip(alts, dalts)):
                if a.get("code") != b.get("code") or a.get("pct") != b.get("pct"):
                    fail(f"providers[{brand}].promo_alts[{i}] 机器字段被改动（code/pct）")
                if a.get("label") and untranslated(a["label"], b.get("label") or ""):
                    fail(f"providers[{brand}].promo_alts[{i}].label 未译")
        # 机器字段不该出现
        for k in ("founded", "type", "color", "initials", "promo_code", "promo_pct",
                  "promo_rank", "info", "profile_checked"):
            if k in dv:
                fail(f"providers[{brand}].{k} 德语侧不该写（机器字段应继承英语侧）")


# ─────────────────────────── 产物级抽查 ───────────────────────────
# 这些串即使出现在德语页也不算残留（官方专有名称 / 品牌名）
WHITELIST = re.compile(
    r"(Opensignal|Ookla|Speedtest|Mobile Network Experience Report|Global Index|"
    r"Airalo|aloSIM|Holafly|Nomad|Roami|Roamic|Saily|Ubigi|Yesim|Jetpac|"
    r"App Store|Google Play|LTE|5G|USB)",
)


def visible(p: pathlib.Path) -> str:
    t = p.read_text(encoding="utf-8", errors="replace")
    t = re.sub(r"(?is)<(script|style|svg)\b.*?</\1>", " ", t)
    t = re.sub(r"(?s)<[^>]+>", " ", t)
    return re.sub(r"\s+", " ", html.unescape(t))


def check_products(en_c: dict, en_r: dict, en_p: dict, de_r: dict) -> None:
    if not PUB.exists():
        print("  (public/de 不存在，跳过产物级抽查)")
        return
    want = []
    for iso, v in en_c.items():
        for p in v.get("profiles", []) or []:
            if p.get("note"):
                want.append(p["note"])
        for d in (v.get("info") or {}).get("detail", []) or []:
            for f in ("strong", "weak"):
                if d.get(f):
                    want.append(d[f])
    for iso, v in en_r.items():
        if isinstance(v, dict):
            want += list(v.get("opensignal_facts") or [])
    for brand, v in en_p.items():
        for k in ("strengths", "weaknesses"):
            want += list(v.get(k) or [])
    want = [w for w in want if not WHITELIST.search(w) and len(w) >= 20]
    hits = []
    for p in PUB.rglob("*.html"):
        txt = visible(p)
        for w in want:
            if re.sub(r"\s+", " ", w) in txt:
                hits.append((p.relative_to(ROOT).as_posix(), w))
                break
    for path, w in hits[:10]:
        fail(f"产物残留英文（{path}）：{w[:70]}")
    if hits:
        print(f"  产物级：{len(hits)} 个德语页仍含未译数据串")
    else:
        print(f"  产物级：抽查 {len(want)} 条数据串，德语页 0 残留")

    # ── F 产物级：城市名（拆成独立函数，自测才能用临时目录喂假页面）
    n_city = check_city_products(PUB, load(DATA / "countries.toml"))
    print(f"  产物级：城市名 {n_city} 处（{len(CITY_MAP)} 国）已双向核对")

    # ── 产物级：awards 记分板（本轮新增 —— 批 D 建页后才暴露的那一类）
    n_aw, n_ctry = check_award_products(PUB, en_r, de_r, load(DATA / "countries.toml"))
    print(f"  产物级：记分板 {n_aw} 个字段（{n_ctry} 国）已双向核对")


def check_award_products(pub: pathlib.Path, en_r: dict, de_r: dict, ctry: dict) -> tuple[int, int]:
    """产物级 awards 双向核对：德语 networks 页上英语串**不得**出现、德语串**必须**出现。

    ★ 两端都断言 —— 只证「英文不在」会被「整张记分板没渲染」骗过去：
      `layouts/networks/single.html:244` 是 `{{ if $awards }}`，走 else 分支
      （回退成 opensignal_facts 列表）时英语 awards 自然不在页面上，断言假绿。
    ★ 页不存在的国家**跳过** —— 德语 networks 是分批建的（当前 12 页），
      没有页面就不存在泄漏路径；强行断言「页必须存在」会造出假红。

    返回 (核对字段数, 核对国家数)。
    """
    n = 0
    seen: list[str] = []
    for iso in sorted(en_r):
        v = en_r.get(iso)
        if not isinstance(v, dict) or not v.get("awards"):
            continue
        slug = (ctry.get(iso) or {}).get("slug")
        p = pub / "networks" / str(slug) / "index.html" if slug else None
        if not (p and p.exists()):
            continue
        seen.append(iso)
        txt = visible(p)
        dv = de_r.get(iso)
        dm = {g.get("carrier"): g for g in ((dv or {}).get("awards") or [])}
        for a in v["awards"]:
            dg = dm.get(a.get("carrier")) or {}
            for f in ("opensignal", "ookla", "best"):
                ea = re.sub(r"\s+", " ", a.get(f, "") or "")
                da = re.sub(r"\s+", " ", dg.get(f, "") or "")
                if not ea:
                    continue
                n += 1
                if ea in txt:
                    fail(f"产物残留英文记分板（{slug}·{a.get('carrier')}·{f}）：{ea[:70]}")
                if not da:
                    fail(f"产物记分板缺德语（{slug}·{a.get('carrier')}·{f}）")
                elif da not in txt:
                    fail(f"产物缺德语记分板（{slug}·{a.get('carrier')}·{f}）：{da[:70]}")
    return n, len(seen)


def check_city_products(pub: pathlib.Path, ctry: dict) -> int:
    """产物级城市名双向核对：德语页上该国的英文城市名**不得**出现，德语名**必须**出现。

    ★ 两端都断言 —— 只断言「英文不在」会被「整个城市段落没渲染」骗过去（假绿）。
    """
    n = 0
    for iso in sorted(CITY_MAP):
        slug = (ctry.get(iso) or {}).get("slug")
        p = pub / "compare" / str(slug) / "index.html" if slug else None
        if not (p and p.exists()):
            fail(f"城市名产物核对：找不到 {pub.name}/compare/{slug}/index.html（ISO {iso}）")
            continue
        txt = visible(p)
        for en_c0, de_c0 in (CITY_MAP[iso] or {}).items():
            if en_c0 == de_c0:
                continue
            n += 1
            if re.search(r"(?<![A-Za-zÀ-ÿ])" + re.escape(en_c0) + r"(?![A-Za-zÀ-ÿ])", txt):
                fail(f"产物残留英文城市名（{slug}）：{en_c0!r} 应为 {de_c0!r}")
            if not re.search(r"(?<![A-Za-zÀ-ÿ])" + re.escape(de_c0) + r"(?![A-Za-zÀ-ÿ])", txt):
                fail(f"产物缺德语城市名（{slug}）：{de_c0!r} 未出现（英文侧是 {en_c0!r}）")
    return n


# ─────────────────────────── 自测 ───────────────────────────
def selftest() -> int:
    global PROBLEMS
    c_en = load(DATA / "carriers.toml")
    r_en = load(DATA / "networkreports.toml")
    p_en = load(DATA / "providers.toml")
    c_de = load(DE / "carriers.toml")
    r_de = load(DE / "networkreports.toml")
    # ⚠ networkreports 现在多了一个**顶层标量** `accessed` —— 凡是「按 ISO 做可变副本」
    #   的地方都要先滤掉它，否则 `dict("Oktober 2026")` 直接抛 ValueError。
    r_iso = {k: v for k, v in r_de.items() if isinstance(v, dict)}
    p_de = load(DE / "providers.toml")

    cases = []

    def run(name, fn, want_red=True):
        global PROBLEMS
        PROBLEMS = []
        fn()
        red = len(PROBLEMS) > 0
        cases.append((name, red == want_red, PROBLEMS[0] if PROBLEMS else ""))
        PROBLEMS = []

    # 正例：真实数据应全绿
    run("正例（真实数据）", lambda: (check_carriers(c_en, c_de), check_reports(r_en, r_de), check_report_dates(r_en, r_de), check_providers(p_en, p_de)), want_red=False)
    # A 反例：整国缺失
    run("A 整国缺失", lambda: check_carriers(c_en, {k: v for k, v in c_de.items() if k != "AT"}))
    # B 反例：profiles 条数少一个
    bad = {k: dict(v) for k, v in c_de.items()}
    bad["AT"] = dict(bad["AT"])
    bad["AT"]["profiles"] = bad["AT"]["profiles"][:-1]
    run("B profiles 条数不符", lambda: check_carriers(c_en, bad))
    # B 反例：机器字段被改
    bad2 = {k: dict(v) for k, v in c_de.items()}
    bad2["AT"] = dict(bad2["AT"])
    bad2["AT"]["profiles"] = [dict(p) for p in bad2["AT"]["profiles"]]
    bad2["AT"]["profiles"][0]["speed_min"] = 999
    run("B 机器字段被改", lambda: check_carriers(c_en, bad2))
    # C 反例：未译（与英文相同）
    bad3 = {k: dict(v) for k, v in c_de.items()}
    bad3["AT"] = dict(bad3["AT"])
    bad3["AT"]["profiles"] = [dict(p) for p in bad3["AT"]["profiles"]]
    bad3["AT"]["profiles"][0]["note"] = c_en["AT"]["profiles"][0]["note"]
    run("C 未译（同英文）", lambda: check_carriers(c_en, bad3))
    # D 反例：数字被改
    bad4 = {k: dict(v) for k, v in c_de.items()}
    bad4["AT"] = dict(bad4["AT"])
    bad4["AT"]["profiles"] = [dict(p) for p in bad4["AT"]["profiles"]]
    bad4["AT"]["profiles"][0]["note"] = bad4["AT"]["profiles"][0]["note"] + " 999 GB"
    run("D 数字不符", lambda: check_carriers(c_en, bad4))
    # F 反例：cities 条数不符（AT 在 CITY_DE 内，英语侧 3 个城市）
    bad5 = {k: dict(v) for k, v in c_de.items()}
    bad5["AT"] = dict(bad5["AT"])
    bad5["AT"]["info"] = dict(bad5["AT"].get("info") or {})
    bad5["AT"]["info"]["cities"] = ["Wien"]
    run("F cities 条数不符", lambda: check_carriers(c_en, bad5))
    # F 反例：cities 长度对但内容与 CITY_DE 不符
    bad5b = {k: dict(v) for k, v in c_de.items()}
    bad5b["AT"] = dict(bad5b["AT"])
    bad5b["AT"]["info"] = dict(bad5b["AT"].get("info") or {})
    bad5b["AT"]["info"]["cities"] = ["Wien", "Graz", "Wien"]
    run("F cities 与 CITY_DE 不符", lambda: check_carriers(c_en, bad5b))
    # F 反例：CITY_DE 内的国家漏写 cities（回退英文）
    bad5c = {k: dict(v) for k, v in c_de.items()}
    bad5c["AT"] = dict(bad5c["AT"])
    bad5c["AT"]["info"] = {k: v for k, v in (bad5c["AT"].get("info") or {}).items()
                           if k != "cities"}
    run("F cities 缺覆盖", lambda: check_carriers(c_en, bad5c))
    # F 反例：CITY_DE 外的国家写了 cities（死条目）
    bad5d = {k: dict(v) for k, v in c_de.items()}
    bad5d["AU"] = dict(bad5d["AU"])
    bad5d["AU"]["info"] = dict(bad5d["AU"].get("info") or {})
    bad5d["AU"]["info"]["cities"] = ["Sydney"]
    run("F cities 死条目", lambda: check_carriers(c_en, bad5d))
    # F 反例：trips 误写（只有品牌名与数字，必须继承英语侧）
    bad5e = {k: dict(v) for k, v in c_de.items()}
    bad5e["AT"] = dict(bad5e["AT"])
    bad5e["AT"]["info"] = dict(bad5e["AT"].get("info") or {})
    bad5e["AT"]["info"]["trips"] = [{"key": "city"}]
    run("F trips 误写", lambda: check_carriers(c_en, bad5e))
    # 反例：reports facts 未译
    rb = {k: dict(v) for k, v in r_iso.items()}
    k0 = next(k for k in rb if rb[k].get("opensignal_facts"))
    rb[k0] = dict(rb[k0])
    rb[k0]["opensignal_facts"] = list(rb[k0]["opensignal_facts"])
    rb[k0]["opensignal_facts"][0] = r_en[k0]["opensignal_facts"][0]
    run("reports facts 未译", lambda: check_reports(r_en, rb))
    # 反例：reports 机器字段被写
    rb2 = {k: dict(v) for k, v in r_iso.items()}
    rb2[k0] = dict(rb2[k0])
    rb2[k0]["opensignal_url"] = "x"
    run("reports 机器字段被写", lambda: check_reports(r_en, rb2))
    # ── awards 记分板反例（2026-10-10 第七十二轮）──────────────────────────────
    # 正例已由「正例（真实数据）」覆盖（35 组德语已在 data/de 里）。这里只注入破坏。
    # ⚠ 每例都要**独立深拷贝**：`awards` 是 list[dict]，浅拷贝会让几个反例互相污染
    #   （本项目的老坑：一个反例改完，下一个反例看到的已经不是真实数据了）。
    ka = next(k for k in sorted(r_iso) if isinstance(r_en.get(k), dict) and r_en[k].get("awards"))

    def awards_case(mutate):
        ra = {k: dict(v) for k, v in r_iso.items()}
        ra[ka] = dict(ra[ka])
        ra[ka]["awards"] = [dict(x) for x in ra[ka]["awards"]]
        mutate(ra[ka])
        return ra

    # A 反例：整国 awards 缺失（数组整体替换 → 整表回退英文，构建不报错）
    run("awards 整国缺失", lambda: check_reports(
        r_en, awards_case(lambda v: v.pop("awards"))))
    # B 反例：组数少一组
    run("awards 组数不符", lambda: check_reports(
        r_en, awards_case(lambda v: v.__setitem__("awards", v["awards"][:-1]))))
    # C 反例：carrier 被改动（模板按 carrier 建映射 → 整行错位）
    run("awards carrier 被改动", lambda: check_reports(
        r_en, awards_case(lambda v: v["awards"][0].__setitem__("carrier", "HACKED"))))
    # D 反例：某字段改回英文（「忘译当已译」）
    run("awards 字段未译", lambda: check_reports(
        r_en, awards_case(lambda v: v["awards"][0].__setitem__(
            "best", r_en[ka]["awards"][0]["best"]))))
    # E 反例：数字被改
    run("awards 数字不符", lambda: check_reports(
        r_en, awards_case(lambda v: v["awards"][0].__setitem__(
            "best", v["awards"][0]["best"] + " 999 Mbit/s"))))
    # F 反例：英语侧没有 awards 的国家，德语侧写了（死条目）
    # ⚠ 必须挑一个**会被 check_reports 处理**的国家（英语侧有 facts 或 note），
    #   否则函数在 `continue` 之前就跳过了 —— 那条断言会假绿（白写）。
    k_no = next(k for k in sorted(r_iso)
                if isinstance(r_en.get(k), dict) and not r_en[k].get("awards")
                and (r_en[k].get("opensignal_facts") or r_en[k].get("ookla_note")))
    run("awards 死条目（英语侧没有）", lambda: check_reports(
        r_en, {**{k: dict(v) for k, v in r_iso.items()},
               k_no: {**r_iso[k_no], "awards": [{"carrier": "X", "opensignal": "",
                                                 "ookla": "", "best": "y"}]}}))
    # 反例：providers strengths 条数少
    pb = {k: dict(v) for k, v in p_de.items()}
    pb["airalo"] = dict(pb["airalo"])
    pb["airalo"]["strengths"] = pb["airalo"]["strengths"][:-1]
    run("providers strengths 条数不符", lambda: check_providers(p_en, pb))
    # 反例：promo_alts 机器字段被改
    pb2 = {k: dict(v) for k, v in p_de.items()}
    pb2["airalo"] = dict(pb2["airalo"])
    pb2["airalo"]["promo_alts"] = [dict(x) for x in pb2["airalo"]["promo_alts"]]
    pb2["airalo"]["promo_alts"][0]["code"] = "HACKED"
    run("promo_alts code 被改", lambda: check_providers(p_en, pb2))
    # 反例：policy 未译
    pb3 = {k: dict(v) for k, v in p_de.items()}
    pb3["airalo"] = dict(pb3["airalo"])
    pb3["airalo"]["policy"] = dict(pb3["airalo"]["policy"])
    pb3["airalo"]["policy"]["fup_note"] = p_en["airalo"]["policy"]["fup_note"]
    run("policy.fup_note 未译", lambda: check_providers(p_en, pb3))
    # 反例：机器字段误写
    pb4 = {k: dict(v) for k, v in p_de.items()}
    pb4["airalo"] = dict(pb4["airalo"])
    pb4["airalo"]["founded"] = 1
    run("providers 机器字段误写", lambda: check_providers(p_en, pb4))

    # F 产物级城市名：临时目录里造 24 张假页，先全绿、再把一处改回英文 → 必红
    import tempfile
    ctry = load(DATA / "countries.toml")
    with tempfile.TemporaryDirectory() as td:
        tdp = pathlib.Path(td)

        def build(break_iso: str = "") -> None:
            for iso, m in CITY_MAP.items():
                slug = (ctry.get(iso) or {}).get("slug")
                d = tdp / "compare" / str(slug)
                d.mkdir(parents=True, exist_ok=True)
                ec = (c_en.get(iso, {}).get("info") or {}).get("cities") or []
                names = ec if iso == break_iso else [m.get(c, c) for c in ec]
                (d / "index.html").write_text(
                    "<html><body><p>" + " ".join(names) + "</p></body></html>",
                    encoding="utf-8")

        build()
        run("F 产物级城市名（正例）",
            lambda: check_city_products(tdp, ctry), want_red=False)
        build("IT")      # Rome/Milan/Naples/Florence 回来 → 英文残留
        run("F 产物级残留英文城市名", lambda: check_city_products(tdp, ctry))
        build()
        (tdp / "compare" / "italy" / "index.html").write_text(
            "<html><body><p>Rom, Mailand</p></body></html>", encoding="utf-8")
        run("F 产物级缺德语城市名（只断言「英文不在」会漏掉这条）",
            lambda: check_city_products(tdp, ctry))

    # 产物级 awards 记分板：同一套临时目录套路。★ 三例，含「只断言英文不在会假绿」那条
    with tempfile.TemporaryDirectory() as td2:
        t2 = pathlib.Path(td2)

        def build_aw(mode: str = "de") -> None:
            for iso, v in r_en.items():
                if not isinstance(v, dict) or not v.get("awards"):
                    continue
                slug = (ctry.get(iso) or {}).get("slug")
                d = t2 / "networks" / str(slug)
                d.mkdir(parents=True, exist_ok=True)
                dv = r_iso.get(iso) or {}
                dm = {g.get("carrier"): g for g in (dv.get("awards") or [])}
                parts = []
                for a in v["awards"]:
                    g = dm.get(a.get("carrier")) or {}
                    for f in ("opensignal", "ookla", "best"):
                        src = a if mode == "en" else g
                        if src.get(f):
                            parts.append(src[f])
                body = "" if mode == "blank" else " ".join(parts)
                (d / "index.html").write_text(
                    "<html><body><p>" + body + "</p></body></html>", encoding="utf-8")

        build_aw("de")
        run("产物级 awards（正例：德语记分板齐全）",
            lambda: check_award_products(t2, r_en, r_iso, ctry), want_red=False)
        build_aw("en")
        run("产物级 awards 残留英文", lambda: check_award_products(t2, r_en, r_iso, ctry))
        build_aw("blank")
        run("产物级 awards 整表未渲染（只断言「英文不在」会漏掉这条）",
            lambda: check_award_products(t2, r_en, r_iso, ctry))

    # G 反例：该国缺 date 覆盖（德语页会印英文月名）
    bR = {k: dict(v) for k, v in r_iso.items()}
    bR["US"] = {k: v for k, v in bR["US"].items() if k != "opensignal_date"}
    run("G opensignal_date 缺失", lambda: check_report_dates(r_en, bR))
    # G 反例：date 仍是英文月名
    bR2 = {k: dict(v) for k, v in r_iso.items()}
    bR2["US"] = dict(bR2["US"])
    bR2["US"]["opensignal_date"] = "July 2026"
    run("G date 仍是英文月名", lambda: check_report_dates(r_en, bR2))
    # G 反例：date 被改成别的德语月（值不符）
    bR2b = {k: dict(v) for k, v in r_iso.items()}
    bR2b["US"] = dict(bR2b["US"])
    bR2b["US"]["opensignal_date"] = "August 2026"
    run("G date 与英语侧不对应", lambda: check_report_dates(r_en, bR2b))
    # G 反例：accessed 未本地化
    bR3 = {k: dict(v) for k, v in r_iso.items()}
    bR3["accessed"] = "October 2026"
    run("G accessed 未本地化", lambda: check_report_dates(r_en, bR3))
    # G 正例：德语月名正确 -> 不许红（同形月 August 在真实数据里就存在）
    gR = dict(r_de)  # ⚠ 必须含顶层 accessed（r_iso 已滤掉它）—— 否则正例连基线都过不了
    gR["US"] = dict(gR["US"])
    gR["US"]["opensignal_date"] = "Juli 2026"
    run("G 正确德语月名不误伤", lambda: check_report_dates(r_en, gR), want_red=False)

    # G 边界：黑名单**只能**含形变月，否则 `August 2026` 这种正确写法会被误伤
    assert _MONTH_ANY.search("August 2026") is None, "黑名单含同形月 April/August/…"
    assert _MONTH_ANY.search("Oktober 2026") is None
    assert _MONTH_ANY.search("October 2026") is not None
    assert _MONTH_ANY.search("December 2025") is not None

    ok = sum(1 for _, good, _ in cases if good)
    for name, good, msg in cases:
        print(f"  {'✓' if good else '✗'} {name}" + ("" if good else f"   ← {msg[:80]}"))
    print(f"自测 {ok}/{len(cases)} 项通过")
    if ok != len(cases):
        for name, good, msg in cases:
            if not good:
                print(f"    ✗ {name}: {msg}")
    return 0 if ok == len(cases) else 1


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--selftest", action="store_true")
    args = ap.parse_args()
    if args.selftest:
        return selftest()

    c_en, r_en, p_en = (load(DATA / "carriers.toml"), load(DATA / "networkreports.toml"),
                        load(DATA / "providers.toml"))
    c_de, r_de, p_de = (load(DE / "carriers.toml"), load(DE / "networkreports.toml"),
                        load(DE / "providers.toml"))
    check_carriers(c_en, c_de)
    check_reports(r_en, r_de)
    check_report_dates(r_en, r_de)
    check_providers(p_en, p_de)
    print("源级：carriers / networkreports / providers 覆盖检查完成")
    check_products(c_en, r_en, p_en, r_de)
    if PROBLEMS:
        print(f"\n数据层德语覆盖守卫：{len(PROBLEMS)} 处问题")
        for p in PROBLEMS[:40]:
            print("  ✗", p)
        return 1
    print("数据层德语覆盖守卫：全部通过")
    return 0


if __name__ == "__main__":
    sys.exit(main())
