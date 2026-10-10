# -*- coding: utf-8 -*-
"""把「日期本地化」判据（G）接进 scripts/verify_de_data.py。

背景：`data/de/networkreports.toml` 长期原样继承英语侧的 `opensignal_date` /
顶层 `accessed`，理由是「机器字段」。但这两个值有 4 处**读者可见**的渲染落点
（compare/single.html:883 的 eyebrow、:906 的正文、networks/list.html:319 的来源行），
于是 51 个德语产物文件印出 232 处英文月名，而当时十一项校验全绿 —— 没有一条
守卫读「日期字段是否本地化」。守卫现在补上，并做 1:1 断言。

为什么不手改、要用脚本：`verify_de_data.py` 是**全 CRLF** 文件。手改/编辑器保存
容易把 CRLF 换成 LF，产生与内容无关的整文件 diff。本脚本 bytes 读写 + 断言
「无裸 LF」，并把「每条锚点恰好命中一次」写进前置条件（锚点漂了就拒改，
不会静默改到别处）。

用法：
  python -X utf8 scripts/_wire_de_dates_guard.py --dry
  python -X utf8 scripts/_wire_de_dates_guard.py
"""
from __future__ import annotations

import ast
import hashlib
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TARGET = ROOT / "scripts" / "verify_de_data.py"
EN_DATA = ROOT / "data" / "networkreports.toml"

# ── ① 文档：判据清单补 G ──────────────────────────────────────────────────────
DOC_OLD = """                   ★ CITY_DE 的**唯一真源**在 `scripts/_gen_de_data.py`，
                     本脚本用 ast 读它 —— 绝不抄第二份（抄了就会漂移）。
"""
DOC_NEW = DOC_OLD + """  G. 日期本地化  —— `opensignal_date` 与顶层 `accessed` 是**可见文案**
                   （compare/single.html 的 eyebrow 与正文、networks/list.html 的来源行），
                   必须 1:1 本地化，且不得残留**形变**英文月名。
                   ⚠ April / August / September / November 德英**同形**，不在黑名单内
                     —— 拿全部 12 个月名当黑名单会把正确的德语写法误伤
                     （同类事故：`.buildlog/audit_de_lang.py` 曾因把 unlimited/data/
                     plans 等德语借词当英语，一次性假红 1389 段）。
                   ★ 月名映射的**唯一真源**在 `scripts/_loc_de_dates.py`，本脚本 import 它。
"""

# ── ② 新函数 + 导入 ──────────────────────────────────────────────────────────
FUNC_ANCHOR = 'POL_TXT = ["hotspot_allowance", "hotspot_note", "fup_note", "topup_note"]'

FUNC_NEW = '''# --- 判据 G：日期字段本地化 ---------------------------------------------------
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


'''

# ── ③ 「机器字段不得改写」清单旁加一句说明（opensignal_date 故意不在清单里） ──
MACHINE_OLD = ('        for k in ("opensignal_title", "opensignal_url", "ookla_slug", '
               '"ookla_mobile", "ookla_url", "ookla_date"):')
MACHINE_NEW = ('        # ⚠ `opensignal_date` **故意不在**这张清单里 —— 它不是机器字段，\n'
               '        #   是可见文案，由判据 G 断言必须本地化（见 check_report_dates）。\n'
               + MACHINE_OLD)

# ── ④ main() 接线 ────────────────────────────────────────────────────────────
MAIN_OLD = "    check_reports(r_en, r_de)"
MAIN_NEW = MAIN_OLD + "\r\n    check_report_dates(r_en, r_de)"

# ── ⑤ selftest 正例接线 ──────────────────────────────────────────────────────
SELF_OLD = ('    run("正例（真实数据）", lambda: (check_carriers(c_en, c_de), '
            'check_reports(r_en, r_de), check_providers(p_en, p_de)), want_red=False)')
SELF_NEW = ('    run("正例（真实数据）", lambda: (check_carriers(c_en, c_de), '
            'check_reports(r_en, r_de), check_report_dates(r_en, r_de), '
            'check_providers(p_en, p_de)), want_red=False)')

# ── ⑥ selftest 反例 + 边界 ───────────────────────────────────────────────────
CASE_ANCHOR = "    ok = sum(1 for _, good, _ in cases if good)"
CASE_NEW = '''    # G 反例：该国缺 date 覆盖（德语页会印英文月名）
    bR = {k: dict(v) for k, v in r_de.items()}
    bR["US"] = {k: v for k, v in bR["US"].items() if k != "opensignal_date"}
    run("G opensignal_date 缺失", lambda: check_report_dates(r_en, bR))
    # G 反例：date 仍是英文月名
    bR2 = {k: dict(v) for k, v in r_de.items()}
    bR2["US"] = dict(bR2["US"])
    bR2["US"]["opensignal_date"] = "July 2026"
    run("G date 仍是英文月名", lambda: check_report_dates(r_en, bR2))
    # G 反例：date 被改成别的德语月（值不符）
    bR2b = {k: dict(v) for k, v in r_de.items()}
    bR2b["US"] = dict(bR2b["US"])
    bR2b["US"]["opensignal_date"] = "August 2026"
    run("G date 与英语侧不对应", lambda: check_report_dates(r_en, bR2b))
    # G 反例：accessed 未本地化
    bR3 = {k: dict(v) for k, v in r_de.items()}
    bR3["accessed"] = "October 2026"
    run("G accessed 未本地化", lambda: check_report_dates(r_en, bR3))
    # G 正例：德语月名正确 -> 不许红（同形月 August 在真实数据里就存在）
    gR = {k: dict(v) for k, v in r_de.items()}
    gR["US"] = dict(gR["US"])
    gR["US"]["opensignal_date"] = "Juli 2026"
    run("G 正确德语月名不误伤", lambda: check_report_dates(r_en, gR), want_red=False)

    # G 边界：黑名单**只能**含形变月，否则 `August 2026` 这种正确写法会被误伤
    assert _MONTH_ANY.search("August 2026") is None, "黑名单含同形月 April/August/…"
    assert _MONTH_ANY.search("Oktober 2026") is None
    assert _MONTH_ANY.search("October 2026") is not None
    assert _MONTH_ANY.search("December 2025") is not None

''' + CASE_ANCHOR

# ── ⑦ selftest：networkreports 多了顶层标量 `accessed`，按 ISO 复制前必须滤掉它 ──
RDE_ANCHOR = '    r_de = load(DE / "networkreports.toml")'
RDE_NEW = RDE_ANCHOR + '''
    # ⚠ networkreports 现在多了一个**顶层标量** `accessed` —— 凡是「按 ISO 做可变副本」
    #   的地方都要先滤掉它，否则 `dict("Oktober 2026")` 直接抛 ValueError。
    r_iso = {k: v for k, v in r_de.items() if isinstance(v, dict)}'''
RDE_ALL_OLD = "for k, v in r_de.items()}"
RDE_ALL_NEW = "for k, v in r_iso.items()}"


def _crlf(s: str) -> str:
    """把字面量里的换行统一成 CRLF。

    本脚本内联的锚点/替换串一律用 `\\n` 写（可读），目标文件是全 CRLF —— 由这里收口。
    先归一到 LF 再补 CR，避免已经手写 `\\r\\n` 的地方被写成 `\\r\\r\\n`。
    """
    return s.replace("\r\n", "\n").replace("\n", "\r\n")


EDITS = [(name, _crlf(old), _crlf(new), all_, marker) for name, old, new, all_, marker in [
    ("判据清单补 G", DOC_OLD, DOC_NEW, False, "  G. 日期本地化  ——"),
    ("新函数 check_report_dates + import", FUNC_ANCHOR, FUNC_NEW + FUNC_ANCHOR, False,
     "def check_report_dates(en: dict, de: dict) -> None:"),
    ("机器字段清单旁加说明", MACHINE_OLD, MACHINE_NEW, False,
     "# ⚠ `opensignal_date` **故意不在**这张清单里"),
    ("main() 接线", MAIN_OLD, MAIN_NEW, False, "    check_report_dates(r_en, r_de)"),
    ("selftest 正例接线", SELF_OLD, SELF_NEW, False,
     "check_report_dates(r_en, r_de), check_providers(p_en, p_de)"),
    ("selftest 反例 + 边界", CASE_ANCHOR, CASE_NEW, False, "G opensignal_date 缺失"),
    ("selftest 定义 r_iso", RDE_ANCHOR, RDE_NEW, False,
     "    r_iso = {k: v for k, v in r_de.items() if isinstance(v, dict)}"),
    ("selftest 一律改用 r_iso", RDE_ALL_OLD, RDE_ALL_NEW, True, "for k, v in r_iso.items()}"),
]]


def apply(raw: str) -> tuple[str, list[str]]:
    """**幂等**补丁器：已施加的编辑跳过，未施加的按「锚点恰好命中一次」施加。

    ⚠ 幂等判据必须用**独立 marker**，不能判 `new in raw` —— 因为本脚本内有一条
      `all_` 编辑（把 `r_de.items()` 全量换成 `r_iso.items()`）会改写**其它编辑的
      产物**：它跑完之后，第 6 条的 `new` 就不再是 `raw` 的子串了，于是第二次运行
      会重新施加一次。用 marker 才不会互相干扰。
    """
    log = []
    for name, old, new, all_, marker in EDITS:
        if marker in raw:
            log.append(f"{name}  (已施加，跳过)")
            continue
        n = raw.count(old)
        if all_:
            if n == 0:
                raise SystemExit(f"[{name}] 标称 all，但锚点命中 0 次 —— 与状态不符")
            raw = raw.replace(old, new)
            log.append(f"{name}  ({n} 处)")
            continue
        if n != 1:
            raise SystemExit(f"[{name}] 锚点命中 {n} 次（必须恰好 1 次），拒绝改写")
        raw = raw.replace(old, new)
        log.append(f"{name}  (+{new.count(chr(10)) - old.count(chr(10))} 行)")
    return raw, log


def main() -> int:
    dry = "--dry" in sys.argv[1:]
    before = TARGET.read_bytes().decode("utf-8")
    en_hash = hashlib.sha256(EN_DATA.read_bytes()).hexdigest()[:16]

    after, log = apply(before)

    # 前置：行尾，全 CRLF 且新增行也是 CRLF（替换串里我手写了 \r\n 的地方要正确）
    assert after.count("\r\n") == after.count("\n"), "出现裸 LF"
    assert "\n" not in after.replace("\r\n", ""), "出现裸 LF"
    # 前置：语法必须可解析
    tree = ast.parse(after)
    names = {n.name for n in ast.walk(tree) if isinstance(n, ast.FunctionDef)}
    assert "check_report_dates" in names, "新函数没进文件"
    # 前置：import 与调用都到位
    for needle in ("check_report_dates(r_en, r_de)", "from _loc_de_dates import",
                   "check_report_dates(r_en, bR)", "check_report_dates(r_en, gR)"):
        assert after.count(needle) >= 1, f"缺少 {needle}"
    # 幂等：再跑一次必须**逐字节不变**（补丁器本身幂等，这是它的核心保证）
    again, again_log = apply(after)
    if again != after:
        raise SystemExit("非幂等：重复执行会改字节")
    if not all("跳过" in l or "无需改动" in l for l in again_log):
        raise SystemExit(f"非幂等：重复执行仍在改写 -> {again_log}")

    print(f"英文数据文件未触碰: {en_hash}")
    for l in log:
        print("  ·", l)
    print(f"scripts/verify_de_data.py  {len(before.encode('utf-8'))} → "
          f"{len(after.encode('utf-8'))} bytes  CRLF {after.count(chr(13) + chr(10))} 行  裸LF=0")

    if dry:
        print("（--dry：未写盘）")
        return 0
    TARGET.write_bytes(after.encode("utf-8"))
    assert TARGET.read_bytes() == after.encode("utf-8"), "落盘字节与预期不符"
    print("已写盘并复核")
    return 0


if __name__ == "__main__":
    sys.exit(main())
