# -*- coding: utf-8 -*-
"""英语 compare 正文「上一轮改写」的**逐条变更表**（只读，输出 Markdown）。

判据装置说明
------------
`scripts/_en_compare_fix.py` 打印的「改写 49 页 / 626 处」里，**626 是正则匹配次数**
（`sub_group()` 对每个匹配都 +1，**包括替换后与原值相同的幂等命中**），不是「变化的处数」。
本脚本用「改造前留档 `.buildlog/en_bodies.txt` ↔ 现存 `content/en/compare/*.md`」做
token 级 diff，给出**真实变化数**，并按类别拆开（品牌名归一 / 数字与计量 / 其它），
以便审核者一眼看清「哪些是事实槽位、哪些只是大小写归一」。

用法：
  python -X utf8 scripts/_en_compare_changelog.py                 # 摘要
  python -X utf8 scripts/_en_compare_changelog.py --md out.md     # 输出完整变更表
"""
from __future__ import annotations

import argparse
import difflib
import pathlib
import re
from collections import Counter

ROOT = pathlib.Path(__file__).resolve().parents[1]
SNAP = ROOT / ".buildlog" / "en_bodies.txt"
EN = ROOT / "content" / "en" / "compare"
DOC = re.compile(r"^---\r?\n(.*?)^---\r?\n", re.M | re.S)

BRANDS = ("roami", "airalo", "holafly", "saily", "yesim", "ubigi", "roamic", "alosim",
          "nomad", "jetpac")
BR_RE = re.compile(r"^(?:" + "|".join(BRANDS) + r")(?:'s)?[.,]?$", re.I)
# 纯数字 / 金额 / 计量 词元（去掉两端标点后判断）
TOK = re.compile(r"^(?:[$£€]?[\d][\d.,]*)(?:MB|GB|/GB|/day|Mbps)?$|^(?:MB|GB)$")


def load_snapshot() -> dict[str, str]:
    raw = SNAP.read_text(encoding="utf-8").replace("\r\n", "\n")
    out = {}
    for blk in re.split(r"^######## ", raw, flags=re.M)[1:]:
        stem = blk.split()[0]
        out[stem] = blk.split("\n", 1)[1].strip() if "\n" in blk else ""
    return out


def load_current() -> dict[str, str]:
    out = {}
    for f in sorted(EN.glob("*.md")):
        if "-vs-" in f.stem:
            continue
        t = f.read_text(encoding="utf-8").replace("\r\n", "\n")
        m = DOC.match(t)
        out[f.stem] = re.sub(r"^(?:\n)+", "", t[m.end():]).strip()
    return out


def classify(tok: str) -> str:
    s = tok.strip(".,;:()")
    if BR_RE.match(tok):
        return "brand"
    if TOK.match(s):
        return "num"
    return "other"


def collect() -> dict:
    old, cur = load_snapshot(), load_current()
    rows = []
    for stem in sorted(cur):
        if stem not in old or cur[stem] == old[stem]:
            continue
        a, b = old[stem].split("\n"), cur[stem].split("\n")
        wa, wb = re.findall(r"\S+", old[stem]), re.findall(r"\S+", cur[stem])
        sm = difflib.SequenceMatcher(None, wa, wb, autojunk=False)
        cats: Counter = Counter()
        pairs = []
        for tag, i1, i2, j1, j2 in sm.get_opcodes():
            if tag == "equal":
                continue
            for k in range(max(i2 - i1, j2 - j1)):
                o = wa[i1 + k] if i1 + k < i2 else ""
                n = wb[j1 + k] if j1 + k < j2 else ""
                cats[classify(o)] += 1
                pairs.append((o, n))
        rows.append({"stem": stem, "lines": sum(1 for x in a if x not in b),
                     "tokens": sum(cats.values()), "cats": dict(cats), "pairs": pairs})
    return {"old_n": len(old), "cur_n": len(cur),
            "unchanged": [s for s in cur if s in old and cur[s] == old[s]],
            "rows": rows}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--md")
    args = ap.parse_args()
    r = collect()
    tot = Counter()
    for x in r["rows"]:
        tot.update(x["cats"])
    lines = sum(x["lines"] for x in r["rows"])
    toks = sum(x["tokens"] for x in r["rows"])

    print(f"改造前留档 {r['old_n']} 页 / 现存 {r['cur_n']} 页")
    print(f"正文有变更 {len(r['rows'])} 页；逐字节未变 {len(r['unchanged'])} 页 {r['unchanged']}")
    print(f"变更行 {lines}；变更 token {toks}")
    print(f"  品牌名归一 {tot['brand']} / 数字与计量 {tot['num']} / 其它 {tot['other']}")
    other = [p[0] for x in r["rows"] for p in x["pairs"] if classify(p[0]) == "other"]
    print(f"  「其它」样例 {other[:20]}")

    if args.md:
        out = ["# 英语 compare 正文改写 —— 逐条变更表", "",
               f"- 改造前留档：`.buildlog/en_bodies.txt`（{r['old_n']} 页）",
               f"- 现存：`content/en/compare/*.md`（{r['cur_n']} 页，含 2 个非国家页）",
               f"- **正文有变更 {len(r['rows'])} 页**；逐字节未变 {len(r['unchanged'])} 页"
               f"（`{r['unchanged'][0]}`）",
               f"- 变更 **{toks} 个 token**（品牌名归一 {tot['brand']} + 数字与计量 "
               f"{tot['num']} + 其它 {tot['other']}），落在 {lines} 行上", "",
               "> ⚠ `_en_compare_fix.py` 报的「626 处」是**正则匹配次数**"
               "（含替换后同值的幂等命中），不是变化处数。", "",
               "| 页 | 变更行 | token | 品牌 | 数字 | 其它 |", "|---|---:|---:|---:|---:|---:|"]
        for x in sorted(r["rows"], key=lambda z: -z["tokens"]):
            c = x["cats"]
            out.append(f"| `{x['stem']}` | {x['lines']} | {x['tokens']} | "
                       f"{c.get('brand',0)} | {c.get('num',0)} | {c.get('other',0)} |")
        out += ["", "## 逐条 old → new", ""]
        for x in sorted(r["rows"], key=lambda z: z["stem"]):
            out.append(f"### {x['stem']}")
            out.append("")
            seen, cnt = set(), Counter()
            for o, n in x["pairs"]:
                cnt[(o, n)] += 1
            for (o, n), k in cnt.items():
                if (o, n) in seen:
                    continue
                seen.add((o, n))
                out.append(f"- `{o}` → `{n}`" + (f" ×{k}" if k > 1 else ""))
            out.append("")
        pathlib.Path(args.md).write_text("\n".join(out) + "\n", encoding="utf-8")
        print(f"[written] {args.md}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
