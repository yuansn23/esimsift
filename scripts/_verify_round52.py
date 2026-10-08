import re, pathlib, html, collections

DROP = re.compile(r"<(script|style|nav|footer|header|svg|noscript)\b.*?</\1>", re.S | re.I)
PROSE = re.compile(r"<(p|li|blockquote|figcaption)\b[^>]*>(.*?)</\1>", re.S | re.I)
HEAD = re.compile(r'<h([23])[^>]*\bid="([^"]+)"', re.S)
TAG = re.compile(r"<[^>]+>")


def sents(h):
    out = []
    for m in PROSE.finditer(h):
        t = html.unescape(TAG.sub(" ", m.group(2)))
        t = re.sub(r"\s+", " ", t).strip()
        for s in re.split(r"(?<=[.!?])\s+", t):
            if len(s) >= 25:
                out.append(s.strip())
    return out


print("=" * 84)
print("① P0 —— 品牌子页 #localnotes（quirks 落地）")
print("=" * 84)
for iso in ["japan", "singapore", "austria"]:
    for brand in ["roamic", "airalo"]:
        p = pathlib.Path(f"public/compare/{iso}/{brand}/index.html")
        h = p.read_text(encoding="utf-8")
        seg = h[h.find('id="localnotes"') - 200: h.find('id="localnotes"') + 2600] if 'id="localnotes"' in h else ""
        items = re.findall(r'<li class="card flex gap-3\.5[^>]*>.*?<span>(.*?)</span>', seg, re.S)
        items = [re.sub(r"\s+", " ", html.unescape(TAG.sub(" ", x))).strip() for x in items]
        print(f"  {iso}/{brand:8s} localnotes={'有' if seg else '!!无!!'} 条目={len(items)}")
        for it in items:
            print(f"      · {it[:96]}")
        break
    print()

print("=" * 84)
print("② P0' —— vs 页 #more 去句子化")
print("=" * 84)
vs = sorted(pathlib.Path("public/compare").glob("*-vs-*/index.html"))
hit_old = hit_bar = hit_leg = 0
for f in vs:
    h = f.read_text(encoding="utf-8")
    if "starts cheaper in" in h: hit_old += 1
    if 'aria-hidden="true">' in h and re.search(r'style="width:[\d.]+%"', h): hit_bar += 1
    if "bar_split_legend" in h or "Each bar splits the countries" in h: hit_leg += 1
print(f"  共 {len(vs)} 页")
print(f"  仍含旧句 'starts cheaper in' = {hit_old}  (应为 0)")
print(f"  含比例条 style=width    = {hit_bar}")
print(f"  含区块口径说明          = {hit_leg}")
h = vs[0].read_text(encoding="utf-8")
i = h.find('id="more"')
seg = re.sub(r"\s+", " ", html.unescape(TAG.sub(" ", h[i:i + 4000])))
print(f"  样例区块文本: {seg[:420]}")

print()
print("=" * 84)
print("③ P1 —— 品牌子页 #reality/#fup/#faq 页内重复")
print("=" * 84)
for p in ["public/compare/japan/roamic/index.html",
          "public/compare/united-states/airalo/index.html",
          "public/compare/austria/alosim/index.html",
          "public/compare/japan/holafly/index.html"]:
    f = pathlib.Path(p)
    h = DROP.sub(" ", f.read_text(encoding="utf-8"))
    heads = [(m.start(), m.group(2)) for m in HEAD.finditer(h)]

    def zone(pos):
        z = "(head)"
        for s, i in heads:
            if s < pos: z = i
            else: break
        return z

    cnt = collections.defaultdict(list)
    for m in PROSE.finditer(h):
        t = html.unescape(TAG.sub(" ", m.group(2)))
        t = re.sub(r"\s+", " ", t).strip()
        for s in re.split(r"(?<=[.!?])\s+", t):
            if len(s) >= 25: cnt[s.strip()].append(zone(m.start()))
    dup = {s: z for s, z in cnt.items() if len(z) > 1}
    print(f"  {p.replace('public/compare/',''):38s} 总槽={sum(len(v) for v in cnt.values()):3d} 页内重复句={len(dup)}")
    for s, z in sorted(dup.items(), key=lambda x: -len(x[1]))[:3]:
        print(f"       ×{len(z)} {sorted(set(z))}  {s[:76]}")

print()
print("=" * 84)
print("④ P2 —— 品牌 hub 页")
print("=" * 84)
for name in ["airalo", "holafly"]:
    p = pathlib.Path(f"public/esim-providers/{name}/index.html")
    h = DROP.sub(" ", p.read_text(encoding="utf-8"))
    heads = [(m.start(), m.group(2)) for m in HEAD.finditer(h)]

    def zone2(pos, heads=heads):
        z = "(head)"
        for s, i in heads:
            if s < pos: z = i
            else: break
        return z

    cnt = collections.defaultdict(list)
    for m in PROSE.finditer(h):
        t = html.unescape(TAG.sub(" ", m.group(2)))
        t = re.sub(r"\s+", " ", t).strip()
        for s in re.split(r"(?<=[.!?])\s+", t):
            if len(s) >= 25: cnt[s.strip()].append(zone2(m.start()))
    dup = {s: z for s, z in cnt.items() if len(z) > 1}
    print(f"  {name:9s} 总槽={sum(len(v) for v in cnt.values()):3d} 页内重复句={len(dup)}")
    for s, z in sorted(dup.items(), key=lambda x: -len(x[1]))[:4]:
        print(f"       ×{len(z)} {sorted(set(z))}  {s[:76]}")
    raw = pathlib.Path(f"public/esim-providers/{name}/index.html").read_text(encoding="utf-8")
    # 比例条真实形态是 style="width:NN.N%"（双引号）——曾用 chr(39) 拼单引号，导致恒为 0 的假阴性
    nbar = len(re.findall(r'style="width:[0-9.]+%"', raw))
    print(f"        'Cheapest in' 残留={raw.count('Cheapest in')}  比例条={nbar}")
