# -*- coding: utf-8 -*-
"""第五十六轮（批 4-7）产物级验收 —— 全部走「文本抽取 + 断言」，不做截图。

覆盖：
  批4 国家页 FAQ 追加 4 问 / 批5 #verdict 句式 / 批6 品牌 Hub #reviews
  批7a 国家页 #quirks 城市-机场句 / 批7b 区域指南 FAQ
外加两条反同质化自证（跨页模块 md5 去重必须 = 页数）。
"""
import glob
import hashlib
import html
import io
import os
import re
import sys
from pathlib import Path

PUB = Path(__file__).resolve().parents[1] / "public"
ROOT = Path(__file__).resolve().parents[1]
ok = 0
bad = []


def check(name, cond, detail=""):
    global ok
    if cond:
        ok += 1
        print(f"  [OK]   {name}" + (f"  {detail}" if detail else ""))
    else:
        bad.append(name)
        print(f"  [FAIL] {name}  {detail}")


def read(p):
    return io.open(p, encoding="utf-8", errors="replace").read()


def strip_tags(s):
    s = re.sub(r"<script\b.*?</script>", " ", s, flags=re.S | re.I)
    s = re.sub(r"<style\b.*?</style>", " ", s, flags=re.S | re.I)
    s = re.sub(r"<[^>]+>", " ", s)
    return re.sub(r"\s+", " ", html.unescape(s)).strip()


# ══ 批 5：国家页 #verdict 句式 ══════════════════════════════════════════════
print("\n批 5 · #verdict 用 best eSIM for {country}")
for slug, name in [("japan", "Japan"), ("italy", "Italy"), ("united-states", "USA"),
                   ("united-kingdom", "UK"), ("argentina", "Argentina")]:
    p = PUB / "compare" / slug / "index.html"
    t = read(p)
    h2 = re.search(r'<h2 id="verdict"[^>]*>(.*?)</h2>', t, re.S)
    got = strip_tags(h2.group(1)) if h2 else ""
    check(f"{slug} H2 含 'best eSIM for {name}'",
          got == f"What is the best eSIM for {name}?", repr(got))
    # 旧句式只允许残留在右侧/手机 TOC 的导航空锚文本里（i18n key compare_single__toc_verdict），
    # 正文与任何 <h2>/<h3> 里都不许再有。
    check(f"{slug} 旧句式不在任何标题里",
          not re.search(r"<h[23][^>]*>[^<]*is best for your trip", t))
    check(f"{slug} 旧句式残留 = 2（两个 TOC）",
          t.count("is best for your trip") == 2, str(t.count("is best for your trip")))

# 德语页走同一模板，但国名取自 data/de/countries.toml → 是德语国名（Italien）。
# ⚠ 已知 i18n 缺口：句子本身仍是英文硬编码，与页面上其余 12 个 H2 同源，非本轮引入。
de = read(PUB / "de" / "compare" / "italy" / "index.html")
deh2 = re.search(r'<h2 id="verdict"[^>]*>(.*?)</h2>', de, re.S)
check("de/compare/italy H2 同步更新（国名为德语 Italien）",
      strip_tags(deh2.group(1)) == "What is the best eSIM for Italien?",
      repr(strip_tags(deh2.group(1))))

# ══ 批 7a：城市 + 机场句 ══════════════════════════════════════════════════
print("\n批 7a · #quirks 城市与机场句")
import tomllib
cty = tomllib.loads(io.open(ROOT / "data" / "countries.toml", encoding="utf-8").read())
car = tomllib.loads(io.open(ROOT / "data" / "carriers.toml", encoding="utf-8").read())

n_city_rendered = 0
for iso, b in cty.items():
    if not isinstance(b, dict):
        continue
    slug = b["slug"]
    p = PUB / "compare" / slug / "index.html"
    if not p.exists():
        continue
    t = read(p)
    cities = (car.get(iso, {}) or {}).get("info", {}).get("cities", [])
    if not cities:
        continue
    n_city_rendered += 1
    check(f"{slug} 城市句渲染", "no airport counter to queue at" in t)
    check(f"{slug} 列出真实城市", cities[0] in t and cities[-1] in t,
          f"{cities[0]}…{cities[-1]}")
    if n_city_rendered >= 3:
        break
check("城市句覆盖国家数（抽查 3 国即停）", n_city_rendered == 3)

# ══ 批 4：国家页 10 条 FAQ + jp 手写条 token 已替换 ════════════════════════
print("\n批 4 · 国家页 FAQ 10 问")
for slug in ("japan", "ireland", "indonesia", "italy", "argentina"):
    t = read(PUB / "compare" / slug / "index.html")
    seg = t[t.find('id="faq"'):]
    seg = seg[:seg.find("</section>")] if "</section>" in seg else seg
    qs = re.findall(r"<summary>(.*?)<span class=\"faq-icon", seg, re.S)
    check(f"{slug} FAQ 条数 = 10", len(qs) == 10, f"实得 {len(qs)}")
    for token in ("{country}", "{plan_count}", "{brand_count}", "{neighbor}"):
        check(f"{slug} 无残留 {token}", token not in seg)

for slug, name in [("ireland", "Ireland"), ("argentina", "Argentina"),
                   ("indonesia", "Indonesia"), ("italy", "Italy")]:
    t = read(PUB / "compare" / slug / "index.html")
    check(f"{slug} 无 'a {name}'", f"a {name}" not in t)

# jp 特殊分支：4 条是**手写**的（不套模板池），但 Q7/Q10 仍含现算 token，必须已替换成真数字
jp = read(PUB / "compare" / "japan" / "index.html")
check("jp Q9 手写答案渲染", "A Japanese phone number is not required for a travel eSIM" in jp)
check("jp Q10 现算 token 已替换",
      re.search(r"the \d+ Japan plans from \d+ providers", jp) is not None,
      (re.search(r"the \d+ Japan plans from \d+ providers", jp) or ["未匹配"])[0])

# ══ 批 6：品牌 Hub #reviews ══════════════════════════════════════════════
print("\n批 6 · 品牌 Hub #reviews 区块")
brands = [os.path.basename(os.path.dirname(p))
          for p in glob.glob(str(PUB / "esim-providers" / "*" / "index.html"))]
check("品牌 Hub 页数 = 10", len(brands) == 10, str(len(brands)))

rev_texts = {}
for b in sorted(brands):
    t = read(PUB / "esim-providers" / b / "index.html")
    check(f"{b} 有 #reviews H2", 'id="reviews"' in t)
    check(f"{b} H2 含 eSIM reviews", "eSIM reviews and how to read them" in t)
    check(f"{b} 有读法三条", t.count("One-star reviews that name a specific failure") == 1)
    check(f"{b} 有论坛段", "Forums such as Reddit" in t)
    check(f"{b} 无评分摘要漏出", '"ratingValue"' not in t and "aggregateRating" not in t)
    # 口碑去向卡（原 #reading 的卡已搬来，页尾只剩 2 张）
    reading = t[t.find('id="reading"'):]
    check(f"{b} #reading 卡片数 = 2", reading.count('<div class="card p-6">') == 2,
          f"实得 {reading.count('<div class=\"card p-6\">')}")
    seg = t[t.find('id="reviews"'):t.find('id="howworks"')]
    rev_texts[b] = hashlib.md5(strip_tags(seg).encode()).hexdigest()

check("反同质化：#reviews 10 页文本两两不同",
      len(set(rev_texts.values())) == 10, f"去重 {len(set(rev_texts.values()))}")

# ══ 批 7b：区域指南 FAQ ══════════════════════════════════════════════════
print("\n批 7b · 区域指南 FAQ（6 问，5 篇互不相同）")
reg_qs = {}
for f in sorted(glob.glob(str(PUB / "guides" / "best-*-esim" / "index.html"))):
    slug = os.path.basename(os.path.dirname(f))
    t = read(f)
    seg = t[t.find('id="faq"'):]
    qs = re.findall(r"<h3 class=\"contents font-sans text-ink-900\">(.*?)</h3>", seg)
    check(f"{slug} FAQ 条数 = 6", len(qs) == 6, f"实得 {len(qs)}")
    reg_qs[slug] = tuple(strip_tags(q) for q in qs)
    check(f"{slug} 含 providers 问", any("Which providers sell eSIMs" in q for q in reg_qs[slug]))

# 新增的两问在 5 篇里必须都是不同句子（不能只换区域名）
new_q6 = [reg_qs[s][4] for s in reg_qs]
new_q7 = [reg_qs[s][5] for s in reg_qs]
check("新增 Q5 五篇互不相同", len(set(new_q6)) == 5, str(len(set(new_q6))))
check("新增 Q6 五篇互不相同", len(set(new_q7)) == 5, str(len(set(new_q7))))

# ── 反同质化：城市句 50 页文本唯一 ─────────────────────────────────────────
print("\n反同质化 · #quirks 城市句（全 50 国）")
city_hashes = {}
for f in sorted(glob.glob(str(PUB / "compare" / "*" / "index.html"))):
    slug = os.path.basename(os.path.dirname(f))
    t = read(f)
    m = re.search(r'<p class="mt-4 border-t border-ink-100 pt-3 text-sm leading-relaxed text-ink-600">(.*?)</p>', t, re.S)
    if m:
        city_hashes[slug] = hashlib.md5(strip_tags(m.group(1)).encode()).hexdigest()
check("城市句渲染页数 = 50（en）", len(city_hashes) == 50, str(len(city_hashes)))
check("反同质化：城市句 50 页文本唯一",
      len(set(city_hashes.values())) == len(city_hashes),
      f"去重 {len(set(city_hashes.values()))}/{len(city_hashes)}")

print(f"\n通过 {ok} 项，失败 {len(bad)} 项")
if bad:
    for b in bad:
        print("   FAIL: " + b)
sys.exit(1 if bad else 0)
