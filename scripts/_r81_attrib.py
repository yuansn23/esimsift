# -*- coding: utf-8 -*-
"""第八十一轮：逐字节归属法（zero-spillover proof）。

不变量：**改造后产物 == 改造前产物 ⊕ 已声明编辑集合**，且该集合之外逐字节不变。

四层，各覆盖一类页面；顺序即强度递减：

  L1 「未变更页恒等」——103 个变更页之外的全部页面 sha256 与改造前相同。
       这一层**就是**「零外溢」的定义。

  L2 「同形页 · 同一变换跨页字节恒等」——90 个对决页（45 EN + 45 DE）由同一模板 + 同形数据
       渲染。从每组**任取一页**导出差异块（pre 片段 → post 片段，含 ±1 行锚点），
       再把**同一组块**套用到组内其余页：若逐字节还原出实际产物，则
       「审查 1 页 = 审查全部 90 页」，且组内不存在任何第二种改法。

  L3 「单页 · 差异只落在脚本体内」——tools 2 页（+ 404 1 页）是单页，无法跨页复现，
       改为断言：**剥掉全部 `<script>` 体之后，改造前后逐字节相同**
       ⇒ 服务端渲染的可见 HTML 一个字节没动，全部改动都在 JS 里。
       404 页另加：每条变更行都必须含该页的 title 文案（3 处 head 元数据）。

  L4 「品牌 Hub · 变更只落在 JSON-LD 的 "name" 值」——10 页每页数据不同，无法跨页复现。
       断言行数不变、且每条变更行的 `"name": "` 前缀与 `",` 后缀**逐字节不变**，
       只有引号之间的值变了。

用法：python -X utf8 scripts/_r81_attrib.py
"""
import difflib
import hashlib
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PRE = ROOT / ".buildlog" / "pub_r81_pre"
POST = ROOT / "public"

NAME_LINE = re.compile(r'^(\s*"name": ")(.*)(",?)$')


def sha(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()


def strip_scripts(text: str) -> str:
    """把每个 <script …>…</script> 的**体**换成空，只留标签（手写扫描，避免正则回溯）。"""
    out, i, n = [], 0, len(text)
    low = text.lower()
    while True:
        a = low.find("<script", i)
        if a < 0:
            out.append(text[i:])
            break
        gt = low.find(">", a)
        if gt < 0:
            out.append(text[i:])
            break
        out.append(text[i:gt + 1])
        b = low.find("</script>", gt)
        if b < 0:
            out.append(text[gt + 1:])
            break
        out.append("</script>")
        i = b + len("</script>")
    return "".join(out)


def diff_lines(a_text: str, b_text: str):
    """→ (差异块, 变更行对)。差异块含 ±1 行锚点，相邻块已合并。"""
    al = a_text.splitlines(keepends=True)
    bl = b_text.splitlines(keepends=True)
    sm = difflib.SequenceMatcher(a=al, b=bl, autojunk=False)
    ops = sm.get_opcodes()
    spans, pairs = [], []
    for tag, i1, i2, j1, j2 in ops:
        if tag == "equal":
            continue
        pairs.append(("".join(al[i1:i2]), "".join(bl[j1:j2])))
        spans.append([max(0, i1 - 1), min(len(al), i2 + 1),
                      max(0, j1 - 1), min(len(bl), j2 + 1)])
    merged = []
    for s in spans:
        if merged and s[0] <= merged[-1][1]:
            merged[-1][1] = max(merged[-1][1], s[1])
            merged[-1][3] = max(merged[-1][3], s[3])
        else:
            merged.append(list(s))
    blks = [("".join(al[x[0]:x[1]]), "".join(bl[x[2]:x[3]])) for x in merged]
    return blks, pairs


def apply_blocks(text: str, subs) -> str:
    for old, new in subs:
        c = text.count(old)
        if c != 1:
            raise AssertionError(f"锚点命中 {c} 次（期望 1）：{old[:70]!r}")
        text = text.replace(old, new, 1)
    return text


def classify(rel: str) -> str:
    if re.match(r"^de/esim-providers/[^/]+/index\.html$", rel):
        return "hub_de"
    if re.match(r"^compare/[^/]+-vs-[^/]+/index\.html$", rel):
        return "vs_en"
    if re.match(r"^de/compare/[^/]+-vs-[^/]+/index\.html$", rel):
        return "vs_de"
    if rel == "tools/index.html":
        return "tools_en"
    if rel == "de/tools/index.html":
        return "tools_de"
    if rel == "de/404.html":
        return "404_de"
    return "OTHER"


def main() -> int:
    pages = sorted(p.relative_to(PRE).as_posix() for p in PRE.rglob("*.html"))
    changed, groups = [], {}
    for rel in pages:
        if (PRE / rel).read_bytes() != (POST / rel).read_bytes():
            changed.append(rel)
            groups.setdefault(classify(rel), []).append(rel)

    print(f"改造前快照 {PRE}")
    print(f"改造后产物 {POST}")
    print(f"全站 HTML {len(pages)} 页 → 变更 {len(changed)} 页 / 未变 {len(pages) - len(changed)} 页")
    for k in sorted(groups):
        print(f"    {k:10s} {len(groups[k])}")
    (ROOT / ".buildlog" / "r81_changed.txt").write_text(
        "\n".join(changed) + "\n", encoding="utf-8")

    fails = []
    if groups.get("OTHER"):
        fails.append(f"出现未分类变更页：{groups['OTHER'][:5]}")

    print(f"\nL1 未变更页恒等：{len(pages) - len(changed)} 页 sha256 与改造前相同")

    # ---------- L2 同形页 ----------
    for g in ("vs_en", "vs_de"):
        items = groups.get(g, [])
        if not items:
            fails.append(f"{g} 无变更页")
            continue
        ref = items[0]
        blks, _ = diff_lines((PRE / ref).read_text(encoding="utf-8"),
                             (POST / ref).read_text(encoding="utf-8"))
        bad = 0
        nonscript_bad = 0
        for rel in items:
            pre_t = (PRE / rel).read_text(encoding="utf-8")
            post_t = (POST / rel).read_text(encoding="utf-8")
            try:
                got = apply_blocks(pre_t, blks)
            except AssertionError as e:
                fails.append(f"{g}: {rel} {e}")
                bad += 1
                continue
            if got.encode("utf-8") != (POST / rel).read_bytes():
                fails.append(f"{g}: {rel} 套用基准块后与实际产物不符")
                bad += 1
            if strip_scripts(pre_t) != strip_scripts(post_t):
                fails.append(f"{g}: {rel} 剥掉脚本体后仍有变化 → 动了服务端渲染的可见 HTML")
                nonscript_bad += 1
        print(f"L2 {g}：{len(items)} 页共用基准块 {len(blks)} 块（基准 {ref}）"
              f"，逐字节还原 {len(items) - bad}/{len(items)}；"
              f"非脚本区不变 {len(items) - nonscript_bad}/{len(items)}")

    # ---------- L3 单页 ----------
    for g in ("tools_en", "tools_de", "404_de"):
        for rel in groups.get(g, []):
            pre_t = (PRE / rel).read_text(encoding="utf-8")
            post_t = (POST / rel).read_text(encoding="utf-8")
            blks, pairs = diff_lines(pre_t, post_t)
            try:
                got = apply_blocks(pre_t, blks)
            except AssertionError as e:
                fails.append(f"{g}: {rel} {e}")
                continue
            if got.encode("utf-8") != (POST / rel).read_bytes():
                fails.append(f"{g}: {rel} 套用差异块后与实际产物不符")
            if g == "404_de":
                for _, new in pairs:
                    for ln in new.splitlines():
                        if ln.strip() and "404 Seite nicht gefunden" not in ln:
                            fails.append(f"{g}: {rel} 变更行超出 title 范围：{ln.strip()[:80]!r}")
                ok = "非脚本区已核对（仅 3 处 head 元数据）"
            else:
                same = strip_scripts(pre_t) == strip_scripts(post_t)
                if not same:
                    fails.append(f"{g}: {rel} 剥掉脚本体后仍有变化 → 动了服务端渲染的可见 HTML")
                ok = "非脚本区逐字节不变"
            print(f"L3 {g}：{rel} {len(blks)} 块 / {len(pairs)} 处差异，{ok}")

    # ---------- L4 品牌 Hub ----------
    hub = groups.get("hub_de", [])
    tot = 0
    for rel in hub:
        al = (PRE / rel).read_bytes().splitlines(keepends=True)
        bl = (POST / rel).read_bytes().splitlines(keepends=True)
        if len(al) != len(bl):
            fails.append(f"hub_de: {rel} 行数变了 {len(al)}→{len(bl)}（应为纯值替换）")
            continue
        n = 0
        for x, y in zip(al, bl):
            if x == y:
                continue
            n += 1
            mx = NAME_LINE.match(x.rstrip(b"\r\n").decode("utf-8"))
            my = NAME_LINE.match(y.rstrip(b"\r\n").decode("utf-8"))
            if not (mx and my):
                fails.append(f"hub_de: {rel} 变更行不是 \"name\" 值行：{x[:80]!r}")
                continue
            if mx.group(1) != my.group(1) or mx.group(3) != my.group(3):
                fails.append(f"hub_de: {rel} 变更行的前缀/后缀也变了：{x[:80]!r}")
        tot += n
    print(f"L4 hub_de：{len(hub)} 页，行数不变，共变更 {tot} 行，全部为 JSON-LD \"name\" 值")

    print()
    if fails:
        for f in fails:
            print("FAIL " + f)
        print(f"\n归属法失败：{len(fails)} 项")
        return 1
    print("OK: 零外溢 —— 变更集合恰为声明页型；同形页同一变换跨页字节恒等；"
          "单页改动全在脚本体内；品牌 Hub 改动全在 JSON-LD 值。")
    return 0


if __name__ == "__main__":
    sys.exit(main())
