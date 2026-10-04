#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""把 layouts/ 里的硬编码英文文案抽成 i18n key（英文产物必须逐字节一致）。

设计约束（均由本机实测得出，勿改）：
  1. 一律用 `| safeHTML` 渲染。Hugo 的 i18n 返回普通 string 会被转义，
     而 safeHTML 透传 TOML 原值 —— 只要把源文件里的字面量原样存进 TOML，
     输出就与改造前逐字节相同。
     反例：`safeHTMLAttr` 会把 `&` 二次转义为 `&amp;amp;`；不带 safeHTML 会转义 `&`。
  2. 属性上下文（aria-label / alt / placeholder / title / label）里，
     html/template 会把 `'` 转成 `&#39;`、`"` 转成 `&#34;`，
     safeHTML 也拦不住 —— 因此含这两个字符的属性值一律跳过。
  3. `<script>` / `<style>` 块整体跳过：JS 上下文转义规则不同（`'`→`\\u0027`）。
     这类文案后续改走 data-* 属性注入。
  4. 只处理「纯静态文本节点」：含 `{{ }}` 的片段不动。
  5. **行尾保真**：本站 `core.autocrlf=true`，工作区模板是 CRLF 而仓库存 LF。
     读取与写回都必须用 `newline=""`（不做换行翻译），否则多行文本节点的
     换行符会被改成 LF，产物立刻出现差异。跨行文本的字面 `\r\n` 原样进 TOML。

用法：
  python scripts/i18n_extract.py --dry     # 只统计，不写文件
  python scripts/i18n_extract.py           # 执行抽取
"""
from __future__ import annotations

import argparse
import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LAYOUTS = os.path.join(ROOT, "layouts")
I18N_EN = os.path.join(ROOT, "i18n", "en.toml")

# 只抽这些用户可见属性
TEXT_ATTRS = ("aria-label", "alt", "placeholder", "title", "label")

VALUE_RE = re.compile(
    r"""(\b(?:%s)\s*=\s*)("[^"]*"|'[^']*')""" % "|".join(TEXT_ATTRS)
)


def find_tag_end(src: str, i: int) -> int | None:
    """从 `<` 找到配对 `>`，尊重属性值里的引号。"""
    n = len(src)
    j = i + 1
    while j < n:
        c = src[j]
        if c in "\"'":
            q = c
            j += 1
            while j < n and src[j] != q:
                j += 1
            j += 1
            continue
        if c == ">":
            return j + 1
        if c == "<":
            return None
        j += 1
    return None


def find_action_end(src: str, i: int) -> int:
    """从 `{{` 找到配对 `}}`，尊重字符串字面量。"""
    n = len(src)
    j = i + 2
    while j < n:
        c = src[j]
        if c in "\"'`":
            q = c
            j += 1
            while j < n and src[j] != q:
                if src[j] == "\\":
                    j += 1
                j += 1
            j += 1
            continue
        if src.startswith("}}", j):
            return j + 2
        j += 1
    return n


def scan(src: str):
    """切分源码为 segments：('text'|'tag'|'action'|'comment'|'rawtext', start, end)。"""
    segs = []
    i, n = 0, len(src)
    while i < n:
        if src.startswith("{{", i):
            j = find_action_end(src, i)
            segs.append(("action", i, j))
            i = j
            continue
        if src.startswith("<!--", i):
            j = src.find("-->", i)
            j = n if j < 0 else j + 3
            segs.append(("comment", i, j))
            i = j
            continue
        if src[i] == "<":
            j = find_tag_end(src, i)
            if j is None:
                segs.append(("text", i, i + 1))
                i += 1
                continue
            tag = src[i:j]
            segs.append(("tag", i, j))
            m = re.match(r"<\s*(script|style)\b", tag, re.I)
            if m and not tag.rstrip().endswith("/>"):
                name = m.group(1).lower()
                close = re.search(r"</\s*" + name + r"\s*>", src[j:], re.I)
                k = n if close is None else j + close.end()
                segs.append(("rawtext", j, k))
                i = k
                continue
            i = j
            continue
        j = i
        while j < n and src[j] != "<" and not src.startswith("{{", j):
            j += 1
        segs.append(("text", i, j))
        i = j
    return segs


CODEISH = re.compile(r"^[A-Z0-9][A-Z0-9\s&/+\-.,%$|]{0,14}$")
HAS_LETTER = re.compile(r"[A-Za-z]")
HAS_LOWER = re.compile(r"[a-z]")
URLISH = re.compile(r"^(https?://|/|mailto:|#)")


def is_translatable(text: str) -> bool:
    if len(text) < 2:
        return False
    if not HAS_LETTER.search(text):
        return False
    if URLISH.match(text):
        return False
    # 纯大写代码串（5G / USD / GB / FAQ 之类）跳过
    if CODEISH.match(text) and not HAS_LOWER.search(text):
        return False
    # 含 Hugo 语法残留的一律不做
    if "{{" in text or "}}" in text or "<" in text or ">" in text:
        return False
    # 单字母词不算
    if len(re.sub(r"[^A-Za-z]", "", text)) < 2:
        return False
    return True


def slug(s: str) -> str:
    s = s.lower()
    s = re.sub(r"[^a-z0-9]+", "_", s)
    return s.strip("_")[:56] or "t"


def filetag(rel: str) -> str:
    p = rel.replace("\\", "/")
    p = re.sub(r"\.(html|txt|json|xml)$", "", p)
    p = p.replace("layouts/", "")
    return re.sub(r"[^a-z0-9]+", "_", p.lower()).strip("_")


def collect(rel: str, src: str):
    """返回 (text_edits, attr_edits, skipped_fragments, skipped_attrs)。"""
    segs = scan(src)
    text_edits, attr_edits = [], []
    frags, bad_attrs = [], []

    for idx, (kind, s, e) in enumerate(segs):
        if kind == "text":
            raw = src[s:e]
            core = raw.strip()
            if not core:
                continue
            pad_l = len(raw) - len(raw.lstrip())
            pad_r = len(raw) - len(raw.rstrip())
            # 相邻 segment 是否为 action（拼装句碎片）→ 记录但先不抽
            prev = segs[idx - 1] if idx > 0 else None
            nxt = segs[idx + 1] if idx + 1 < len(segs) else None
            adjacent_action = (prev and prev[0] == "action") or (
                nxt and nxt[0] == "action"
            )
            if not is_translatable(core):
                continue
            if adjacent_action:
                frags.append(core)
                continue
            text_edits.append((s + pad_l, e - pad_r, core))

        elif kind == "tag":
            tag = src[s:e]
            for m in VALUE_RE.finditer(tag):
                quoted = m.group(2)
                q = quoted[0]
                val = quoted[1:-1]
                if not is_translatable(val):
                    continue
                if "'" in val or '"' in val:
                    bad_attrs.append(val)
                    continue
                if "{{" in val or "}}" in val:
                    continue
                vs = s + m.start(2) + 1
                ve = s + m.end(2) - 1
                attr_edits.append((vs, ve, val))

    return text_edits, attr_edits, frags, bad_attrs


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry", action="store_true")
    ap.add_argument("--only", default=None, help="只处理路径含该子串的文件")
    args = ap.parse_args()

    files = []
    for dp, dn, fn in os.walk(LAYOUTS):
        for f in sorted(fn):
            full = os.path.join(dp, f)
            if not re.search(r"\.(html|txt|json|xml)$", f):
                continue
            rel = os.path.relpath(full, ROOT).replace("\\", "/")
            if args.only and args.only not in rel:
                continue
            files.append((rel, full))
    files.sort()

    # ---- Preflight: 模板必须是 LF ----
    # 混用行尾会让跨行文本节点把 \r\n 带进 TOML，产物随之出现差异。
    # 本站 core.autocrlf=true，git checkout 会写回 CRLF —— 必须先统一成 LF。
    crlf = []
    for rel, full in files:
        with open(full, "rb") as fh:
            if b"\r\n" in fh.read():
                crlf.append(rel)
    if crlf:
        print("!! 以下模板含 CRLF，请先统一为 LF 再抽取：")
        for c in crlf[:20]:
            print("   ", c)
        if len(crlf) > 20:
            print(f"    ... 另有 {len(crlf) - 20} 个")
        print("   （Windows: core.autocrlf=true 会让 git checkout 写回 CRLF）")
        return 1

    data = {}
    for rel, full in files:
        # newline="" 关掉通用换行翻译，原样保留 CRLF / LF
        with open(full, encoding="utf-8", newline="") as fh:
            data[rel] = fh.read()

    # ---- Pass 1: 统计值频次（决定 key 是全局还是按文件作用域） ----
    plan = {}
    freq = {}
    all_entries = []
    for rel, src in data.items():
        te, ae, fr, ba = collect(rel, src)
        plan[rel] = (te, ae, fr, ba)
        for _, _, v in te + ae:
            freq[v] = freq.get(v, 0) + 1
            all_entries.append(v)

    n_text = sum(len(v[0]) for v in plan.values())
    n_attr = sum(len(v[1]) for v in plan.values())
    n_frag = sum(len(v[2]) for v in plan.values())
    n_bad = sum(len(v[3]) for v in plan.values())

    print(f"扫描 {len(files)} 个文件")
    print(f"  可抽取文本节点   : {n_text}")
    print(f"  可抽取属性值     : {n_attr}")
    print(f"  跳过·拼装句碎片  : {n_frag}")
    print(f"  跳过·属性含引号  : {n_bad}")
    if args.dry:
        from collections import Counter

        gg = Counter(v for v in all_entries if freq[v] >= 2)
        print(f"  跨文件复用候选   : {len(gg)} 个不同字符串")
        print("\n  拼装句碎片样例（未抽取）:")
        for rel in sorted(plan):
            for f in plan[rel][2][:2]:
                print(f"    {rel}: {f[:70]!r}")
            if plan[rel][2]:
                break
        print("\n  属性含引号样例（未抽取）:")
        shown = 0
        for rel in sorted(plan):
            for v in plan[rel][3][:2]:
                print(f"    {rel}: {v!r}")
                shown += 1
            if shown >= 6:
                break
        return 0

    # ---- Pass 2: 分配 key 并改写 ----
    bank = {}          # key -> value
    value_global = {}  # value -> key （仅 >=2 文件复用的）
    used = {}

    # 合并既有 key 表：重复运行必须复用已存在的 key，否则会把译好的 key 全冲掉
    if os.path.exists(I18N_EN):
        with open(I18N_EN, encoding="utf-8") as fh:
            for line in fh:
                line = line.strip()
                if not line or line.startswith("#") or "=" not in line:
                    continue
                k, v = line.split("=", 1)
                k = k.strip()
                try:
                    v = json.loads(v.strip())
                except json.JSONDecodeError:
                    continue
                bank[k] = v
                if k.startswith("g_"):
                    value_global.setdefault(v, k)

    def make_key(ft: str, value: str) -> str:
        # 已存在同值 key → 直接复用（保证幂等）
        if value in value_global:
            return value_global[value]
        for k, v in bank.items():
            if v == value and k.startswith(ft + "__"):
                return k
        if freq.get(value, 0) >= 2 and len(value) <= 200:
            k = "g_" + slug(value)
            base = k
            i = 2
            while k in bank and bank[k] != value:
                k = f"{base}_{i}"
                i += 1
            value_global[value] = k
            return k
        k = f"{ft}__{slug(value)}"
        base = k
        i = 2
        while k in bank and bank[k] != value:
            k = f"{base}_{i}"
            i += 1
        return k

    changed = 0
    for rel in sorted(data):
        te, ae, frags, bads = plan[rel]
        if not te and not ae:
            continue
        src = data[rel]
        ft = filetag(rel)
        edits = []
        for s, e, v in te:
            k = make_key(ft, v)
            bank.setdefault(k, v)
            edits.append((s, e, '{{ i18n "%s" | safeHTML }}' % k))
        for s, e, v in ae:
            k = make_key(ft, v)
            bank.setdefault(k, v)
            edits.append((s, e, '{{ i18n "%s" | safeHTML }}' % k))
        edits.sort(key=lambda x: -x[0])
        out = src
        for s, e, new in edits:
            out = out[:s] + new + out[e:]
        if out != src:
            with open(os.path.join(ROOT, rel), "w", encoding="utf-8", newline="") as fh:
                fh.write(out)
            changed += 1

    lines = [
        "# 由 scripts/i18n_extract.py 生成 —— 请勿手改 key 名（会破坏模板引用）",
        "# 值一律以 safeHTML 渲染，必须与源模板字面量逐字节一致",
        "",
    ]
    for k in sorted(bank):
        lines.append(f"{k} = {json.dumps(bank[k], ensure_ascii=False)}")
    lines.append("")

    os.makedirs(os.path.dirname(I18N_EN), exist_ok=True)
    with open(I18N_EN, "w", encoding="utf-8", newline="\n") as fh:
        fh.write("\n".join(lines))

    print(f"\n改写 {changed} 个文件，写入 {len(bank)} 个 key -> i18n/en.toml")
    return 0


if __name__ == "__main__":
    sys.exit(main())
