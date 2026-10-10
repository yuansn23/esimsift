# -*- coding: utf-8 -*-
"""把 `data/de/networkreports.toml` 继承来的**英文月名**本地化成德语。

为什么必须做（2026-10-07 实测）：
  `_gen_de_data.py` 当年刻意只覆盖 `opensignal_facts` / `ookla_note`，注释写的是
  「opensignal_title / url / date / ookla_slug / ookla_mobile 全部保持原文（报告标题是
  官方专有名称，其余是**机器字段**）」。前四个确实该保持：标题是官方报告名，url/slug 是
  链接标识。但 `date` **不是机器字段** —— 它有六处渲染落点，全是读者可见文案：

      layouts/compare/single.html:883   eyebrow `Opensignal · {{ $nr.opensignal_date }}`
      layouts/compare/single.html:896   `…, {{ $nr.ookla_date }}.`
      layouts/compare/single.html:906   `{{ $d.networkreports.accessed }}`
      layouts/networks/list.html:319    `{{ $nr.opensignal_title }}, {{ $nr.opensignal_date }}.`
      layouts/networks/single.html:190/255/274  （该页型德语侧尚未建立）

  于是一句「其余是机器字段」让德语站在线页面直接印出英文：
      **51 个德语产物文件 / 232 处**（`October 2026` ×50、`April 2026` ×30、
      `July 2026` ×24 …）—— `hugo` 退出码 0、当时的十项校验全绿，因为
      **没有任何一条守卫读「日期字段是否本地化」**。月份名是单个词，
      `.buildlog/audit_de_lang.py` 的「英语独占功能词」词表也扫不到它。

修法选择（为什么不走模板层）：
  `{{ time.Format "January 2006" (time.Parse "January 2006" …) }}` 看起来更优雅
  （一处改动自动覆盖未来所有日期），但它依赖 Hugo 内置 de locale —— locale 缺失时
  **静默回退成英文**，属于本仓库最忌讳的「失败无声」。改成数据层覆盖后，「EN 有 date
  ⟺ DE 有 date」是一条可断言的 1:1 不变式，新增国家漏译会直接把守卫打红。

为什么用脚本改而不是跑生成器：
  `_gen_de_data.py` 依赖译料 `.buildlog/de_out_all.json`，该文件已不存在 →
  生成器**现状不可复现**。因此本次改动直接施加在数据文件上，并同步修正
  `_gen_de_data.py` 的注释与输出逻辑（保证它若将来恢复可跑，不会把这里改回去）。

行尾纪律：目标文件是**全 CRLF**（286 行）。一律 bytes 读写 + 逐行拼接，
写完断言「无裸 LF」。

用法：
  python -X utf8 scripts/_loc_de_dates.py --dry       # 只报告不写盘
  python -X utf8 scripts/_loc_de_dates.py             # 执行
  python -X utf8 scripts/_loc_de_dates.py --selftest   # 用构造样本证明检查会红
"""
from __future__ import annotations

import hashlib
import re
import sys
import tomllib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
EN_FILE = ROOT / "data" / "networkreports.toml"
DE_FILE = ROOT / "data" / "de" / "networkreports.toml"

# 德语月名。注意 **April / August / September / November 四个月德英同形** ——
# 这是本脚本最容易写错的地方：若守卫拿「全部 12 个月名」当黑名单，
# `August 2026` 这种**正确**的德语写法会被误报成未本地化。
EN_MONTH = {
    "January": "Januar", "February": "Februar", "March": "März", "April": "April",
    "May": "Mai", "June": "Juni", "July": "Juli", "August": "August",
    "September": "September", "October": "Oktober", "November": "November",
    "December": "Dezember",
}
# 只有这 8 个形变；守卫/黑名单只能用它，不能用全部 12 个
EN_ONLY_MONTH = [m for m, de in EN_MONTH.items() if m != de]

MONTH_YEAR = re.compile(r"^(%s) ([0-9]{4})$" % "|".join(EN_MONTH))

HEADER = """# 德语第三方测速报告覆盖 —— 覆盖会上德语页的**三类**文本：
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
# 现状不可再生）；日期字段由 scripts/_loc_de_dates.py 施加并守卫。"""


def de_month(s: str) -> str | None:
    """`May 2026` → `Mai 2026`。无法识别的形态返回 None（例如机器格式 `2026-08`）。"""
    m = MONTH_YEAR.match(s)
    return None if m is None else f"{EN_MONTH[m.group(1)]} {m.group(2)}"


def read_de() -> str:
    """按文本读，保留 CRLF（newline="" 关掉换行翻译）。"""
    with DE_FILE.open(encoding="utf-8", newline="") as fh:
        return fh.read()


def build(en: dict, text: str) -> tuple[str, list[str]]:
    """返回 (新文本, 变更说明)。

    纯函数 + **幂等**：先把本脚本此前生成的字段整段剥掉，再按确定性顺序重建。
    不做「检测已存在就跳过」——那种写法在「值变了解析规则」时会留下旧值。
    """
    notes: list[str] = []
    lines = text.split("\r\n")

    # ---- ① 分离「表头区」与「表体」：表体从第一个 `[ISO]` 段头开始 ----
    head_hdr = re.compile(r"^\[([A-Z]{2})\]$")
    first = next((i for i, l in enumerate(lines) if head_hdr.match(l)), None)
    if first is None:
        raise SystemExit("数据文件里找不到任何 [ISO] 段头")
    head_region, body = lines[:first], lines[first:]

    # ---- ② 幂等：剥掉上一轮生成的字段 ----
    dropped_head = sum(1 for l in head_region
                       if l.startswith('accessed = "') or l.startswith("opensignal_date = "))
    head_region = [l for l in head_region
                   if not (l.startswith('accessed = "') or l.startswith("opensignal_date = "))]
    dropped_body = sum(1 for l in body if l.startswith("opensignal_date = "))
    body = [l for l in body if not l.startswith("opensignal_date = ")]
    stray = [l for l in head_region if l.strip() and not l.startswith("#")]
    if stray:
        raise SystemExit(f"表头区出现非注释内容，拒绝改写: {stray[:3]}")

    # ---- ③ 顶层 accessed ----
    top = en.get("accessed")
    want_acc = de_month(top) if isinstance(top, str) else None
    if want_acc is None:
        raise SystemExit(f"EN 顶层 accessed 无法解析: {top!r}")

    lines = (HEADER.split("\n")
             + ["", f'accessed = "{want_acc}"', ""]
             + body)
    notes.append(f"表头 + accessed：剥旧字段 {dropped_head} 行，写入 accessed={want_acc!r}")

    # ---- ④ 每个 [ISO] 段插 opensignal_date ----
    want = {iso: de_month(v["opensignal_date"])
            for iso, v in en.items()
            if isinstance(v, dict) and isinstance(v.get("opensignal_date"), str)}
    unknown = [iso for iso, v in want.items() if v is None]
    if unknown:
        raise SystemExit(f"以下 ISO 的 opensignal_date 无法解析: {unknown}")

    out: list[str] = []
    seen: set[str] = set()
    for ln in lines:
        out.append(ln)
        m = head_hdr.match(ln)
        if m and m.group(1) in want:
            iso = m.group(1)
            seen.add(iso)
            out.append(f'opensignal_date = "{want[iso]}"')
    lines = out
    missing = sorted(set(want) - seen)
    if missing:
        raise SystemExit(f"数据文件里找不到这些 [ISO] 段: {missing}")
    notes.append(f"opensignal_date: {len(want)} 个 ISO（剥旧 {dropped_body} 行）")

    return "\r\n".join(lines), notes


def invariants(en: dict, before: str, after: str) -> None:
    """写盘前后都要成立的不变式。任何一条不成立就直接抛 —— 宁可不写。"""
    # 1. 行尾：全 CRLF，无裸 LF
    assert after.count("\r\n") == after.count("\n"), "出现裸 LF"
    assert "\n" not in after.replace("\r\n", ""), "出现裸 LF"

    old, new = tomllib.loads(before), tomllib.loads(after)

    # 2. 1:1 —— EN 有 date 的每个 ISO，DE 都必须有，且值等于本地化结果
    want = {iso: de_month(v["opensignal_date"])
            for iso, v in en.items()
            if isinstance(v, dict) and isinstance(v.get("opensignal_date"), str)}
    got = {iso: v["opensignal_date"] for iso, v in new.items()
           if isinstance(v, dict) and "opensignal_date" in v}
    assert got == want, f"date 覆盖不一致，多={sorted(set(got) - set(want))} 缺={sorted(set(want) - set(got))} 值异={[k for k in got if k in want and got[k] != want[k]]}"

    # 3. accessed
    assert new.get("accessed") == de_month(en["accessed"]), new.get("accessed")

    # 4. 德语日期值里不得残留**形变**英文月名（同形月不算，见 EN_ONLY_MONTH）
    bad = [(k, v) for k, v in got.items() if re.search(
        r"(?<![A-Za-z])(" + "|".join(EN_ONLY_MONTH) + r")(?![A-Za-z])", v)]
    assert not bad, f"仍含英文月名: {bad}"
    assert not re.search(r"(?<![A-Za-z])(" + "|".join(EN_ONLY_MONTH) + r")(?![A-Za-z])",
                         new["accessed"]), new["accessed"]

    # 5. **其它一切原封不动**（除本次新增/改写的两类字段）
    for k, v in old.items():
        if k == "accessed":
            continue
        if not isinstance(v, dict):
            assert new.get(k) == v, f"顶层 {k} 被改"
            continue
        nv = new.get(k)
        assert isinstance(nv, dict), f"[{k}] 丢失"
        for kk, vv in v.items():
            if kk == "opensignal_date":
                continue
            assert nv.get(kk) == vv, f"[{k}].{kk} 被改"
        assert set(nv) - set(v) <= {"opensignal_date"}, f"[{k}] 多出键 {set(nv) - set(v)}"


def selftest() -> int:
    cases: list[tuple[str, object, object]] = [
        ("May 2026 → Mai", de_month("May 2026"), "Mai 2026"),
        ("October 2026 → Oktober", de_month("October 2026"), "Oktober 2026"),
        ("December 2025 → Dezember", de_month("December 2025"), "Dezember 2025"),
        ("March 2026 → März", de_month("March 2026"), "März 2026"),
        ("July 2023 → Juli", de_month("July 2023"), "Juli 2023"),
        # 德英同形月：必须原样返回，不得被"顺手改掉"
        ("November 2023 同形不动", de_month("November 2023"), "November 2023"),
        ("August 2026 同形不动", de_month("August 2026"), "August 2026"),
        ("April 2026 同形不动", de_month("April 2026"), "April 2026"),
        # 机器格式不得被当成年月
        ("机器格式 2026-08 拒收", de_month("2026-08"), None),
        ("裸年份 2026 拒收", de_month("2026"), None),
        ("未知月名拒收", de_month("Mai 2026"), None),
        ("多余后缀拒收", de_month("May 2026 (draft)"), None),
    ]
    failed = 0
    for name, got, want in cases:
        ok = got == want
        failed += 0 if ok else 1
        print(f"  {'OK  ' if ok else 'MISS'} {name:28s} 期望 {want!r} 实际 {got!r}")

    # 反例：黑名单只能含 8 个形变月，含同形月就会把正确德语写法误伤
    probe = "August 2026"
    pat = re.compile(r"(?<![A-Za-z])(" + "|".join(EN_ONLY_MONTH) + r")(?![A-Za-z])")
    ok = pat.search(probe) is None
    failed += 0 if ok else 1
    print(f"  {'OK  ' if ok else 'MISS'} 黑名单不含同形月（{probe} 不误伤）  实际 {pat.search(probe)}")
    probe2 = "December 2025"
    ok2 = pat.search(probe2) is not None
    failed += 0 if ok2 else 1
    print(f"  {'OK  ' if ok2 else 'MISS'} 黑名单含形变月（{probe2} 被抓）    实际 {bool(pat.search(probe2))}")

    print(f"\n自测{'通过' if not failed else f'失败 {failed} 项'}（{len(cases) + 2} 项）")
    return 1 if failed else 0


def main() -> int:
    if "--selftest" in sys.argv[1:]:
        return selftest()
    dry = "--dry" in sys.argv[1:]

    en = tomllib.loads(EN_FILE.read_text(encoding="utf-8"))
    before = read_de()
    after, notes = build(en, before)
    invariants(en, before, after)

    # 幂等：同一份输入跑两次必须同结果（否则重复执行会持续堆行）
    again, _ = build(en, after)
    assert again == after, "非幂等：重复执行会改字节"

    en_hash = hashlib.sha256(EN_FILE.read_bytes()).hexdigest()[:16]
    print(f"英文数据文件未触碰: {en_hash}")
    for n in notes:
        print(f"  · {n}")
    d = len(after.encode("utf-8")) - len(before.encode("utf-8"))
    print(f"data/de/networkreports.toml  {len(before.encode('utf-8'))} → "
          f"{len(after.encode('utf-8'))} bytes  ({d:+d})"
          f"  CRLF {after.count(chr(13) + chr(10))} 行  幂等=OK")

    if dry:
        print("（--dry：未写盘）")
        return 0
    if after == before:
        print("已是最新，无需写盘")
        return 0
    with DE_FILE.open("w", encoding="utf-8", newline="") as fh:
        fh.write(after)
    # 复核落盘字节
    assert DE_FILE.read_bytes() == after.encode("utf-8"), "落盘字节与预期不符"
    assert tomllib.loads(DE_FILE.read_text(encoding="utf-8")), "写盘后 TOML 不可解析"
    print("已写盘并复核")
    return 0


if __name__ == "__main__":
    sys.exit(main())
