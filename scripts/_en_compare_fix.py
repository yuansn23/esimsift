# -*- coding: utf-8 -*-
"""① 英语 compare 正文事实数字现算重写（消掉与同页 seo.description 的自相矛盾）。

背景与口径见 `scripts/_en_compare_lib.py` 的 docstring。

做法（**只改槽位，不重写文风**）：
  1. 品牌槽位：把正文里的小写原始 key 改成规范名（`ubigi` → `Ubigi`），
     只替换由**句式锚定**捕获的那一个词；
  2. 套餐规格覆盖：少数页面的「速率冠军套餐」换品牌/换规格，逐页显式改（13 条）；
  3. 数字槽位：T / U / rate / entry_mb / entry_gb / ratio / daily / breakeven /
     speed / tech，逐个按现算值替换被捕获的那一段；
  4. 兜底：把剩下的小写品牌 key 统一成规范名。

用法：
  python -X utf8 scripts/_en_compare_fix.py --dry     # 只打印
  python -X utf8 scripts/_en_compare_fix.py           # 落盘
  python -X utf8 scripts/_en_compare_fix.py --verify  # 复核（应为 0 处过期）
"""
from __future__ import annotations

import argparse
import importlib.util
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
_spec = importlib.util.spec_from_file_location("_lib", ROOT / "scripts" / "_en_compare_lib.py")
L = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(L)  # type: ignore[union-attr]

# ── 少数页面的「速率冠军套餐」规格/品牌在数据里换过，需要逐页显式改 ──
# 只写 **已观察到的原文片段 → 现算事实**，不做泛化猜测。
PLAN_OVERRIDES: dict[str, list[tuple[str, str]]] = {
    "brazil": [("for 60GB over 365 days", "for 50GB over 30 days")],
    "georgia": [("for 50GB over 30 days", "for 40GB")],
    "qatar": [("500MB / 1 Day plan at $1.17/GB", "50GB / 30-day plan at $0.98/GB")],
    "thailand": [("for 50GB over 30 days", "for 50GB over 10 days")],
    "united-arab-emirates": [("50GB / 30 Days plan at $1.36/GB", "10GB plan at $1.10/GB")],
    "united-states": [("a 50GB / 10-day plan", "a 50GB / 30-day plan")],
}

# 逐页特例：japan 整页是编辑性长文（无「N plans」句、无速率冠军句），
# 其数字（$4-8 / $3.90 / $1.05 / $18.99 / $8）经核对与实时数据仍自洽 ⇒ 不动。
SKIP = {"japan", "_index", "matchups"}


def sub_group(text: str, pat: str, fn, flags: int = 0) -> tuple[str, int]:
    """把 pat 的**第 1 捕获组**替换为 fn(旧值)。只动那一小段，其余逐字节不动。"""
    out, last, n = [], 0, 0
    for m in re.finditer(pat, text, flags):
        if m.start(1) < last:
            continue
        out.append(text[last:m.start(1)])
        out.append(fn(m.group(1)))
        last = m.end(1)
        n += 1
    out.append(text[last:])
    return "".join(out), n


def sub_group2(text: str, pat: str, fn1, fn2, flags: int = 0) -> tuple[str, int]:
    """两捕获组（速度区间）版本。"""
    out, last, n = [], 0, 0
    for m in re.finditer(pat, text, flags):
        if m.start(1) < last:
            continue
        out.append(text[last:m.start(1)])
        out.append(fn1(m.group(1)))
        out.append(text[m.end(1):m.start(2)])
        out.append(fn2(m.group(2)))
        last = m.end(2)
        n += 1
    out.append(text[last:])
    return "".join(out), n


def collect_stale(slug: str, body: str, lv: dict) -> list[tuple[str, str, str]]:
    """返回 [(槽位, 正文值, 现算值)]，只列**确实过期**的。"""
    bad: list[tuple[str, str, str]] = []

    def chk(slot, got, want):
        if str(got) != str(want):
            bad.append((slot, str(got), str(want)))

    for pat in L.RE_T:
        for m in re.finditer(pat, body):
            chk("T", m.group(1), lv["T"])
    for pat in L.RE_U:
        for m in re.finditer(pat, body):
            chk("U", m.group(1), lv["U"])
    for pat in (L.RE_RATE_GB, L.RE_RATE_GIG):
        for m in re.finditer(pat, body):
            chk("rate", m.group(1), lv["rate"])
    for m in re.finditer(L.RE_ENTRY, body):
        if m.group(2) == "MB":
            chk("entry_mb", int(float(m.group(1))), lv["entry_mb"])
        else:
            chk("entry_gb", round(float(m.group(1)), 1), lv["entry_gb"])
    for m in re.finditer(L.RE_RATIO, body):
        chk("ratio", m.group(1), lv["ratio"])
    for pat in L.RE_DAILY:
        for m in re.finditer(pat, body):
            chk("daily", m.group(1), lv["daily"])
    for pat in L.RE_BREAKEVEN:
        for m in re.finditer(pat, body):
            chk("breakeven", m.group(1), lv["breakeven"])
    for pat, _, _ in L.RE_SPEED:
        for m in re.finditer(pat, body):
            chk("speed_min", m.group(1), lv["speed_min"])
            chk("speed_top", m.group(2), lv["speed_top"])
    for m in re.finditer(L.RE_TECH, body):
        chk("tech", m.group(1), lv["tech"])
    for pat, slot in L.RE_BRAND_SLOTS:
        for m in re.finditer(pat, body, re.M):
            g = m.group(1)
            want = lv.get(slot + "_brand")
            if want and g.lower() in L.BRAND_NAME:
                chk("brand@" + slot, L.canon(g), want)
    # 入口价（P1 内所有 $X.XX，排除 /GB 与 a gigabyte）
    p1 = body.split("\n\n")[0]
    prices = {m.group(1) for m in re.finditer(L.RE_ENTRY_PRICE, p1)}
    for p in sorted(prices):
        chk("entry_price", p, lv["entry_price"])
    # 入口套餐规格：只与**供应商原始套餐名**比（反推 gb 会假红）
    p1 = body.split("\n\n")[0]
    m = re.search(L.RE_ENTRY_SIZE, p1)
    pm = re.search(L.RE_ENTRY_SIZE, lv["plan_entry"])
    if m and pm:
        got = (m.group(1), m.group(2), int(m.group(3)))
        want = (pm.group(1), pm.group(2), int(pm.group(3)))
        chk("entry_size", got, want)
    return bad


def fix_body(slug: str, body: str, lv: dict) -> tuple[str, int]:
    n = 0
    # ① 品牌槽位（句式锚定，只改捕获的那一个词）
    for pat, slot in L.RE_BRAND_SLOTS:
        want = lv.get(slot + "_brand")
        if not want:
            continue

        def fn(old, want=want):
            return want if old.lower() in L.BRAND_NAME else old

        body, k = sub_group(body, pat, fn, re.M)
        n += k
    # ② 套餐规格显式覆盖
    for old, new in PLAN_OVERRIDES.get(slug, []):
        if old not in body:
            continue
        body = body.replace(old, new)
        n += 1
    # ③ 数字槽位
    r = lv["rate"]

    def rate_fn(_):
        return r

    body, k = sub_group(body, L.RE_RATE_GB, rate_fn); n += k
    body, k = sub_group(body, L.RE_RATE_GIG, rate_fn); n += k

    def entry_fn(v, unit):
        return lv["entry_mb"] if unit == "MB" else lv["entry_gb"]

    out, last, k = [], 0, 0
    for m in re.finditer(L.RE_ENTRY, body):
        out.append(body[last:m.start(1)])
        out.append(lv["entry_mb"] if m.group(2) == "MB" else lv["entry_gb"])
        last = m.end(1)
        k += 1
    out.append(body[last:])
    body = "".join(out); n += k
    for pat in L.RE_T + L.RE_U:
        want = lv["T"] if pat in L.RE_T else lv["U"]

        def fn(_v, want=want):
            return want

        body, k = sub_group(body, pat, fn); n += k
    body, k = sub_group(body, L.RE_RATIO, lambda _: lv["ratio"]); n += k
    for pat in L.RE_DAILY:
        body, k = sub_group(body, pat, lambda _: lv["daily"]); n += k
    for pat in L.RE_BREAKEVEN:
        body, k = sub_group(body, pat, lambda _: lv["breakeven"]); n += k
    for pat, _, _ in L.RE_SPEED:
        body, k = sub_group2(body, pat, lambda _: lv["speed_min"], lambda _: lv["speed_top"]); n += k
    body, k = sub_group(body, L.RE_TECH, lambda _: lv["tech"]); n += k
    # ④ 兜底：剩下的裸小写品牌 key → 规范名
    body, k = sub_group(body, L.BRAND_RE.pattern, lambda old: L.canon(old)); n += k
    return body, n


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry", action="store_true")
    ap.add_argument("--verify", action="store_true")
    args = ap.parse_args()

    files = [f for f in sorted(L.EN.glob("*.md"))
             if f.stem not in SKIP and "-vs-" not in f.stem]
    total_changes = 0
    touched = 0
    all_problems: list[str] = []
    for f in files:
        raw = f.read_bytes()
        # ⚠ content/en/** 是 CRLF：先断言「纯 CRLF」（无裸 LF），再归一成 LF 处理，
        #   写回时还原 —— 这样换行逐字节不变。
        if raw.count(b"\r\n") != raw.count(b"\n"):
            print(f"✗ {f.stem}: 非纯 CRLF，拒绝处理")
            return 1
        text = raw.decode("utf-8").replace("\r\n", "\n")
        fm, body = L.split_doc(text)
        # 重建不变时应当逐字节相同（自检重建逻辑本身）
        assert "---\n" + fm + "---\n\n" + body == text, f"{f.stem}: 重建不等价"
        iso = re.search(r"^iso:\s*(\w+)", fm, re.M).group(1)
        lv = L.live_values(iso)
        lv["iso"] = iso

        stale = collect_stale(f.stem, body, lv)
        if args.verify:
            for slot, got, want in stale:
                all_problems.append(f"{f.stem:24} {slot:18} {got!r} → {want!r}")
            continue

        new_body, n = fix_body(f.stem, body, lv)
        if new_body == body:
            if stale:
                print(f"✗ {f.stem}: 有 {len(stale)} 处过期但改写未命中 → {stale[:3]}")
                all_problems.append(f.stem)
            continue
        touched += 1
        total_changes += n
        if args.dry:
            print(f"── [{f.stem}] {n} 处")
            for slot, got, want in sorted(set(stale)):
                print(f"      {slot:18} {got!r} → {want!r}")
        else:
            out = ("---\n" + fm + "---\n\n" + new_body.strip() + "\n").replace("\n", "\r\n")
            f.write_bytes(out.encode("utf-8"))

    if args.verify:
        if all_problems:
            print(f"✗ 仍有 {len(all_problems)} 处过期：")
            for p in all_problems[:40]:
                print("   ", p)
            return 1
        print(f"✓ 英语 compare 正文 {len(files)} 页全部与现算口径一致（japan 为编辑性长文，单独核对）")
        return 0

    mode = "[dry] " if args.dry else "[written] "
    print(f"{mode}改写 {touched} 页 / {total_changes} 处槽位")
    if not args.dry:
        # 换行守恒：这批文件本来就是纯 CRLF ⇒ 写回后必须仍是纯 CRLF（无裸 LF）
        impure = [f.name for f in files
                  if f.read_bytes().count(b"\r\n") != f.read_bytes().count(b"\n")]
        print(f"[verify] {len(files)} 页纯 CRLF 检查：异常 {len(impure)} {impure[:5]}")
        return 1 if impure else 0
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
