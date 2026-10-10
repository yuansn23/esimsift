"""生成 data/de/ 的品牌档案与网络数据德语覆盖。

   · data/de/carriers.toml        —— profiles[].note + info.detail[].strong/.weak
   · data/de/networkreports.toml  —— opensignal_facts[] + ookla_note
   · data/de/providers.toml       —— tagline / strengths / weaknesses / policy.* / promo_* 文本

译文来源：.buildlog/de_out_all.json（键 = 英文原串，值 = 德语）。
Hugo 的 data 深合并：map 递归、**数组整体替换** → 含译文的数组必须整段重写
（含 name / tech / speed_min / speed_top / carrier / code / pct 等机器字段）。

TOML 输出纪律：同一张表里的标量/简单数组必须先写完，再写子表数组
（`[[x.promo_alts]]`），最后才是子表（`[x.policy]`）—— 顺序反了 TOML 直接非法。
"""
import tomllib, pathlib, json, io

ROOT = pathlib.Path(r"D:\esimsift\esimsift")
DATA = ROOT / "data"
B = ROOT / ".buildlog"

M = json.loads((B / "de_out_all.json").read_text(encoding="utf-8"))
missing = []


def load(p):
    return tomllib.loads(pathlib.Path(p).read_text(encoding="utf-8"))


# 德语速率单位（**幂等**）：Mbps → Mbit/s、Kbps → Kbit/s。
#   `Mbps` / `Kbps` 是英语缩写，德语标准写法是 `Mbit/s` / `Kbit/s`；站内另一处
#   （data/de/strings.toml 的 fup_note 德语）本来就用 `Mbit/s` —— 同一个德语站
#   不能同时出现两种写法。
#   由 verify_de_text.py **判据 H** 发现：`provider.policy.fup_drop` 的德语值与英文
#   **一字不差**（`1 Mbps` / `512 Kbps`），它把这种「等于没译」直接报成缺陷。
#   ★ 正确修法是**本地化单位**，不是给判据加白名单 —— 那句话本身就是英语写法。
_UNITS = (("Mbps", "Mbit/s"), ("Kbps", "Kbit/s"))


def units(s: str) -> str:
    for a, b in _UNITS:
        s = s.replace(a, b)
    return s


def de(en):
    if not en:
        return en
    if en in M:
        return units(M[en])
    missing.append(en)
    return en


def q(s):
    return '"' + s.replace("\\", "\\\\").replace('"', '\\"') + '"'


def inline(txt, indent="  "):
    return f"{indent}{q(txt)},\n"


def arr_str(name, items):
    out = f"{name} = [\n"
    for s in items:
        out += inline(de(s))
    return out + "]\n"


# ── 城市名的德语形式：`{ISO: {英文名: 德语名}}`，只列**与英文不同**的条目 ──────
# ★ 为什么必须收录（2026-10-09 第六十三轮）：原先把 `info.cities` 一并归入
#   「不含散文 → 故意不写」，但城市名不是散文、**有既定德语形式**：
#   Vienna→Wien / Rome→Rom / Munich→München / The Hague→Den Haag。
#   德语国家页上出现 `Vienna` 与出现 `Munich` 一样刺眼。
#   ★ 用「英文名→德语名」映射、不用**下标对齐**的整个列表：`data/carriers.toml`
#     的城市是按国家习惯排序的（阿根廷是 Buenos Aires 在前），按下标配对会把
#     `Buenos Aires` 配成 `Córdoba` —— 自测当场抓到过。以英文名为键，顺序随数据走，
#     且「映射里的名字不在数据里」这种死条目能被断言出来。
#   收录口径：只用**德语里已确立且通行**的形式（Duden / 德文维基条目标题）；
#   国际通用写法（Seoul、Mumbai、Taipei、Auckland、Sharjah …）一律不收，宁缺勿错。
#   带重音的拼写（Córdoba / Bogotá / São Paulo）属同一类，一并收。
CITY_DE = {
    "AR": {"Cordoba": "Córdoba"},
    "AT": {"Vienna": "Wien"},
    "BE": {"Brussels": "Brüssel", "Antwerp": "Antwerpen", "Ghent": "Gent"},
    "BR": {"Sao Paulo": "São Paulo", "Brasilia": "Brasília"},
    "CH": {"Zurich": "Zürich", "Geneva": "Genf"},
    "CN": {"Beijing": "Peking"},
    "CO": {"Bogota": "Bogotá", "Medellin": "Medellín"},
    "CR": {"San Jose": "San José", "Limon": "Limón"},
    "CZ": {"Prague": "Prag"},
    "DE": {"Munich": "München"},
    "EG": {"Cairo": "Kairo", "Sharm El Sheikh": "Scharm El-Scheich"},
    "ES": {"Seville": "Sevilla"},
    "FR": {"Nice": "Nizza"},
    "GR": {"Athens": "Athen"},
    "IT": {"Rome": "Rom", "Milan": "Mailand", "Naples": "Neapel", "Florence": "Florenz"},
    "MA": {"Marrakesh": "Marrakesch"},
    "MO": {"Macau Peninsula": "Macau-Halbinsel"},
    "MX": {"Mexico City": "Mexiko-Stadt", "Cancun": "Cancún"},
    "NL": {"The Hague": "Den Haag"},
    "PL": {"Warsaw": "Warschau", "Krakow": "Krakau", "Gdansk": "Danzig"},
    "PT": {"Lisbon": "Lissabon"},
    "SA": {"Riyadh": "Riad", "Jeddah": "Dschidda"},
    "VN": {"Ho Chi Minh City": "Ho-Chi-Minh-Stadt"},
    "ZA": {"Cape Town": "Kapstadt"},
}


def cities_de(iso, en_cities):
    """返回 (德语城市列表 or None, 失败原因)。顺序照抄英文侧，只替换映射命中的名字。"""
    m = CITY_DE.get(iso) or {}
    if not m:
        return None, None
    dead = [k for k in m if k not in en_cities]
    if dead:
        return None, f"映射里的英文名不在数据里（死条目）：{dead}"
    out = [m.get(c, c) for c in en_cities]
    if out == list(en_cities):
        return None, "与英文逐字相同 → 死条目"
    return out, None


# ══════════════════════════ 1) carriers ══════════════════════════
src = load(DATA / "carriers.toml")
buf = io.StringIO()
buf.write("""# 德语运营商画像覆盖 —— 只写「会渲染到德语页且需要本地化」的字段；
# 其余字段由 i18n-data.html 深合并继承。
#
# ⚠ 数组字段是「整体替换」而非逐条合并：profiles / info.detail / info.cities
#   必须整段重写（含 name / tech / speed_min / speed_top / carrier 这些机器字段）。
#   漏写一个国家 → 该国德语页静默回退英文，守卫会发现但页面不报错。
#   info.trips 里只有品牌名与数字（机器字段），**故意不写** → 原样继承英语侧。
#   info.cities **有既定德语形式**（Vienna→Wien / Rome→Rom / The Hague→Den Haag），
#   所以只收录「与英文不同」的国家，其余仍继承 —— 名单见脚本里的 CITY_DE。
#
# 由 scripts/_gen_de_data.py 生成，不要手改。译文对应 data/carriers.toml 的
# profiles[].note、info.detail[].strong / .weak 与 info.cities。
# ⚠ 城市名与英文侧**等长**才算完整（改数据时别只改一边）。

""")
n_prof = n_det = n_city = 0
city_bad = []
for iso, v in src.items():
    buf.write(f"[{iso}]\n")
    for p in v.get("profiles", []) or []:
        buf.write(f"[[{iso}.profiles]]\n")
        buf.write(f"name = {q(p['name'])}\n")
        if p.get("tech"):
            buf.write(f"tech = {q(p['tech'])}\n")
        if p.get("speed_min") is not None:
            buf.write(f"speed_min = {p['speed_min']}\n")
        if p.get("speed_top") is not None:
            buf.write(f"speed_top = {p['speed_top']}\n")
        buf.write(f"note = {q(de(p['note']))}\n")
        n_prof += 1
    en_cities = ((v.get("info") or {}).get("cities") or [])
    de_cities, why = cities_de(iso, en_cities)
    if why:
        city_bad.append((iso, why))
    if de_cities:
        buf.write(f"[{iso}.info]\n")
        buf.write("cities = [\n")
        for c in de_cities:
            buf.write(inline(c))
        buf.write("]\n")
        n_city += 1
    for d in (v.get("info") or {}).get("detail", []) or []:
        buf.write(f"[[{iso}.info.detail]]\n")
        buf.write(f"carrier = {q(d['carrier'])}\n")
        if d.get("strong"):
            buf.write(f"strong = {q(de(d['strong']))}\n")
        if d.get("weak"):
            buf.write(f"weak = {q(de(d['weak']))}\n")
        n_det += 1
    buf.write("\n")
(DATA / "de" / "carriers.toml").write_text(buf.getvalue(), encoding="utf-8")
print(f"data/de/carriers.toml  {len(buf.getvalue()):6d} bytes · {n_prof} profiles · "
      f"{n_det} detail · {n_city} cities")
if city_bad:
    print("  ⚠ 城市名有问题：")
    for iso, why in city_bad:
        print(f"     {iso}: {why}")

# ═══════════════════════ 2) networkreports ═══════════════════════
# ⚠ 月名映射**唯一真源**在 _loc_de_dates.py（那里还有 1:1 断言与自测）。
#   本段只负责生成，不复制那张表 —— 抄一份就是第二处会错的地方。
import sys as _sys
_sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from _loc_de_dates import de_month  # noqa: E402

src = load(DATA / "networkreports.toml")
buf = io.StringIO()
buf.write("""# 德语第三方测速报告覆盖 —— 覆盖会上德语页的**三类**文本：
#   opensignal_facts （数组 → 整段重写）· ookla_note （标量）· opensignal_date （月名本地化）
# opensignal_title / url / ookla_slug / ookla_mobile 全部保持原文
#   （报告标题是官方专有名称，其余是机器字段）→ 故意不写，原样继承。
#
# ★ `opensignal_date` / `accessed` 为什么**要**覆盖：它们不是机器字段，是可见文案 ——
#   compare/single.html 印成 eyebrow `Opensignal · {date}`、正文印 `accessed`，
#   networks/list.html 印进来源行。原样继承会让德语站印出英文月名
#   （2026-10-07 实测 51 文件 / 232 处）。44 个 ISO **一律覆盖**，好让守卫做
#   「EN 有 date ⟺ DE 有 date」的 1:1 断言 —— 新增国家漏译会直接变红。
#   ⚠ April / August / September / November 德英同形，覆盖值与原值相同不是冗余，
#     是让上面那条 1:1 断言成立。
#
# 由 scripts/_gen_de_data.py 生成（其译料 .buildlog/de_out_all.json 已不存在 →
# 现状不可再生）；日期字段由 scripts/_loc_de_dates.py 施加并守卫。

""")
_acc = de_month(src.get("accessed"))
if _acc is None:
    raise SystemExit(f"networkreports.accessed 无法本地化: {src.get('accessed')!r}")
buf.write(f'accessed = {q(_acc)}\n\n')

n_f = n_n = n_d = 0
for iso, v in src.items():
    if not isinstance(v, dict):
        continue
    facts = list(v.get("opensignal_facts") or [])
    note = v.get("ookla_note")
    date = de_month(v.get("opensignal_date")) if v.get("opensignal_date") else None
    if v.get("opensignal_date") and date is None:
        raise SystemExit(f"[{iso}].opensignal_date 无法本地化: {v['opensignal_date']!r}")
    if not facts and not note and not date:
        continue
    buf.write(f"[{iso}]\n")
    if date:
        buf.write(f"opensignal_date = {q(date)}\n")
        n_d += 1
    if facts:
        buf.write(arr_str("opensignal_facts", facts))
        n_f += len(facts)
    if note:
        buf.write(f"ookla_note = {q(de(note))}\n")
        n_n += 1
    buf.write("\n")
(DATA / "de" / "networkreports.toml").write_text(buf.getvalue(), encoding="utf-8")
print(f"data/de/networkreports.toml  {len(buf.getvalue()):6d} bytes · {n_f} facts · "
      f"{n_n} ookla_note · {n_d} opensignal_date")

# ═════════════════════════ 3) providers ═════════════════════════
src = load(DATA / "providers.toml")
old = load(DATA / "de" / "providers.toml")   # 复用已核验的 fup_allowance / fup_drop
POL = ["hotspot_allowance", "hotspot_note", "fup_allowance", "fup_drop", "fup_note", "topup_note"]
# ⚠ promo_label **不在这里** —— 它在 data/de/strings.toml（那 10 条已在第六十一轮
#   核验），渲染处用 partial "de-text.html" 覆盖。同一字段只允许一处真源。
PROMO_STR = ["promo_scope", "promo_coverage", "promo_bestfor",
             "promo_uncond_short", "promo_terms", "promo_expiry_note"]

buf = io.StringIO()
buf.write("""# 德语品牌档案覆盖 —— 覆盖会渲染到德语页的全部品牌散文。
#
# 机制：i18n-data.html 把本文件深合并到 data/providers.toml 之上。
#   · 标量（tagline / promo_*）与 map（policy）→ 逐键覆盖，未写的键继承英语侧
#   · 数组（strengths / weaknesses / promo_constraints / promo_uncond_points /
#     promo_alts）→ **整体替换**，所以要翻就得整段重写（含 code / pct 等机器字段）
#   · 其余机器字段（founded / type / color / promo_code / info.*）**故意不写** → 继承
#   · promo_label **不在这里**（它在 data/de/strings.toml，渲染处走 de-text）
#
# 由 scripts/_gen_de_data.py 生成，不要手改。

""")
n_pol = 0
for brand, v in src.items():
    buf.write(f"[{brand}]\n")
    if v.get("tagline"):
        buf.write(f"tagline = {q(de(v['tagline']))}\n")
    for key in ("strengths", "weaknesses"):
        arr = v.get(key) or []
        if arr:
            buf.write(arr_str(key, arr))
    for k in PROMO_STR:
        if isinstance(v.get(k), str) and v[k]:
            buf.write(f"{k} = {q(de(v[k]))}\n")
    if v.get("promo_constraints"):
        buf.write(arr_str("promo_constraints", v["promo_constraints"]))
    # —— 子表数组（必须在 [brand.policy] 之前）——
    for pt in (v.get("promo_uncond_points") or []):
        buf.write(f"[[{brand}.promo_uncond_points]]\n")
        if pt.get("head"):
            buf.write(f"head = {q(de(pt['head']))}\n")
        if pt.get("sub"):
            buf.write(f"sub = {q(de(pt['sub']))}\n")
    for alt in (v.get("promo_alts") or []):
        buf.write(f"[[{brand}.promo_alts]]\n")
        buf.write(f"code = {q(alt['code'])}\n")
        if alt.get("label"):
            buf.write(f"label = {q(de(alt['label']))}\n")
        if alt.get("audience"):
            buf.write(f"audience = {q(alt['audience'])}\n")
        if alt.get("pct") is not None:
            buf.write(f"pct = {alt['pct']}\n")
    # —— 子表 ——
    pol = v.get("policy") or {}
    rows = []
    for k in POL:
        if k in ("fup_allowance", "fup_drop"):
            ov = ((old.get(brand) or {}).get("policy") or {}).get(k)
            if ov:
                rows.append((k, units(ov)))   # 复用的旧值同样要过单位规范化（幂等）
                continue
        if isinstance(pol.get(k), str) and pol[k]:
            rows.append((k, de(pol[k])))
    if rows:
        buf.write(f"[{brand}.policy]\n")
        for k, val in rows:
            buf.write(f"{k} = {q(val)}\n")
            n_pol += 1
    buf.write("\n")
(DATA / "de" / "providers.toml").write_text(buf.getvalue(), encoding="utf-8")
print(f"data/de/providers.toml  {len(buf.getvalue()):6d} bytes · {n_pol} policy 键")

if missing:
    print("\n⚠ 缺译条目", len(set(missing)))
    for m in list(dict.fromkeys(missing))[:10]:
        print("   ", m[:90])
else:
    print("\n✅ 所有条目都有译文")
