#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""stamp_checked.py —— 数据核对日自动盖章：数据驱动的内容变了，日期就变。

规则（2026-10-07 定）
    「只要是页面数据驱动更新了，日期就应该要改变」—— 不限国家 eSIM 页面。

为什么不是直接用构建日
    页面上有四处机器可读的日期，必须同源：
        可见文案「Prices checked <d>」/「Last updated <d>」
        · JSON-LD dateModified · sitemap <lastmod>
        · check_dates.py 的一致性断言
    用 now（构建日，第二十三轮试过又撤回）会让 lastmod 每次部署都翻新 ——
    Google 判定本站 lastmod 无信息量，最终整体忽略；而且「今天核过价」在价格
    其实是上周抓的时候就是一句不实陈述。
    所以口径是 **该数据内容最后一次变化的日期**：数据没变，日期就不动。

机制
    给每个「日期单元」记一份内容指纹（sha256，**排除日期字段本身**）：
        指纹变了  → 日期 = 今天（或 --date）
        指纹没变  → 日期不动（不朝 Google 发无意义的 lastmod 噪声）
        首次遇到  → 只登记指纹、保留现值（bootstrap；不编造「今天核过价」）
    所以「真去官网重核了一遍、价格恰好没变」这种人为改日期**不会被回滚** ——
    指纹没变时以 toml 现值为准，并同步进状态文件。

日期单元（只有这两类会驱动页面日期）
    plans.<brand>.<ISO>   data/plans/<brand>.toml 的 [ISO] 块   → 价格核对日
    profile.<brand>       data/providers.toml 的 [<brand>] 段**连同它的**
                          [<brand>.info] / [<brand>.policy] 子表 → 品牌档案核对日
                          ★ 段按**品牌名**切，不按行位置切 —— 末尾那 10 张
                          `[<brand>.policy]` 是隔着别家堆在一起的，按行位置切会
                          把它们全算到最后一家头上（2026-10-09 实测事故）。

已知缺口（这些数据源目前**不**驱动任何页面日期；改了它们，页面日期不动）
    data/countries.toml        国家 Hub 正文（quirks / region / neighbors …）
    data/de/countries.toml     德语国名覆盖
    data/carriers.toml         运营商卡（#hostnetwork）
    data/refs.toml             运营商官方外链
    data/faqs/*.toml           FAQ 问答文案
    data/titlesegments.toml    标题片段
    要不要让它们也驱动日期是个产品决定 —— 那些页面现在压根没印日期。

用法
    python -X utf8 scripts/stamp_checked.py             # 写：数据变了就盖今天
    python -X utf8 scripts/stamp_checked.py --dry-run   # 只报不写
    python -X utf8 scripts/stamp_checked.py --check     # 只读；该盖未盖退 1
    python -X utf8 scripts/stamp_checked.py --date 2026-10-07
    python -X utf8 scripts/stamp_checked.py --resync    # 口径变更后的一次性迁移
    python -X utf8 scripts/stamp_checked.py --selftest

已挂进 `npm run build` 的**第一步**（hugo 之前），所以「改完数据直接构建」就会
拿到当天日期，不依赖人记得跑 bump_checked.py。

退出码：0 正常；1 参数/数据错误，或 --check 发现「该盖未盖」。
"""
from __future__ import annotations

import argparse
import datetime
import hashlib
import io
import json
import pathlib
import re
import sys
import tempfile

ROOT = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import bump_checked as bc  # noqa: E402  段切分与 `checked` 行的定义只有那一份

PLANS_DIR = ROOT / "data" / "plans"
PROVIDERS = ROOT / "data" / "providers.toml"
STATE_PATH = ROOT / "docs" / "checked-state.json"

# providers.toml 的品牌段头：`[nomad]` 与子表 `[nomad.info]` / `[nomad.policy]`
# 都算同一品牌。★ 只认不带点的表头会让末尾那 10 张 `[<brand>.policy]` 全部落进
# 最后一个品牌（jetpac）的段里 —— 详见 bump_checked.RE_PROV_HEADER 的说明。
RE_TOP = bc.RE_PROV_HEADER
RE_PROFILE_CHECKED = re.compile(r'^\s*profile_checked\s*=\s*"([^"]*)"')
RE_DATE = re.compile(r"^\d{4}-\d{2}-\d{2}$")
# 写回用：`键 = "值"` → 保留缩进与行尾注释
RE_KV = re.compile(r'^(\s*\w+\s*=\s*)"([^"]*)"(.*)$')


# ─────────────────────────── 指纹 ───────────────────────────

def strip_inline_comment(s: str) -> str:
    """剥离行内注释，但跳过引号内的 `#`（TOML 双引号串支持 \\ 转义）。

    ★ 为什么必须剥（2026-10-07 踩过）：`color = "#16456B"   # monogram 兜底色…`
      改这句的**说明文字**，`color` 的值一个字没变、页面一个像素没变，
      但整行进指纹会让档案核对日凭空前移 —— 那就是不实陈述。
    """
    in_str = False
    q = ""
    i, n = 0, len(s)
    while i < n:
        c = s[i]
        if in_str:
            if q == '"' and c == "\\":
                i += 2
                continue
            if c == q:
                in_str = False
        elif c in "\"'":
            in_str = True
            q = c
        elif c == "#":
            return s[:i].rstrip()
        i += 1
    return s.rstrip()


def block_hash(lines: list[str], b: bc.Block) -> str:
    """段内容指纹：排除日期字段行、纯注释行与行内注释，再抹掉行尾空白与空行。

    **只算「会进产物的数据」**，所以：改注释 / 调格式 / 加空行都不触发日期前移，
    改一个价格 / 加减一条套餐 / 改一个档位描述必然触发。
    （把整块数据注释掉也算变化 —— 数据行消失了。）

    段体可能分成多个不连续区间（见 bc.Block.ranges）—— 品牌的
    `[x]` / `[x.info]` / `[x.policy]` 三张表允许隔着别家。
    """
    body = []
    for lo, hi in (b.ranges or [(b.start, b.end)]):
        for i in range(lo + 1, hi):
            if i == b.date_idx:
                continue
            s = strip_inline_comment(lines[i])
            if s.strip():
                body.append(s)
    return hashlib.sha256("\n".join(body).encode("utf-8")).hexdigest()[:16]


# ─────────────────────── 采集日期单元 ───────────────────────

def collect(plans_dir: pathlib.Path = PLANS_DIR,
            providers: pathlib.Path = PROVIDERS) -> list[tuple]:
    """返回 [(unit_key, fingerprint, 现值日期, 文件, 日期行下标), …]"""
    units: list[tuple] = []
    for p in sorted(plans_dir.glob("*.toml")):
        lines = bc.read_lines(p)
        for b in bc.parse_blocks(lines, bc.RE_ISO_HEADER, bc.RE_CHECKED, 2):
            units.append((f"plans.{p.stem}.{b.key}",
                          block_hash(lines, b), b.date, p, b.date_idx))
    if providers.exists():
        lines = bc.read_lines(providers)
        for b in bc.parse_prov_blocks(lines, RE_PROFILE_CHECKED, 1):
            units.append((f"profile.{b.key}",
                          block_hash(lines, b), b.date, providers, b.date_idx))
    return units


# ─────────────────────────── 决策 ───────────────────────────

def decide(units: list[tuple], state: dict, today: str, state_existed: bool = True):
    """纯函数：返回 (ops, new_state, boot, added, manual)。

        ops      [(文件, 行号, 旧值, 新值, unit_key)]  —— 数据变了，日期要前移
        boot     台账里**首次**遇到的单元（仅在台账文件原本不存在时发生）→ 保留现值
        added    台账已存在、却出现的**新单元**（新品牌 / 新市场入库）→ 盖今天
        manual   指纹没变但人改了日期 → 尊重现值，只同步台账

    ★ 为什么区分 boot 与 added：两者的正确行为相反。
      首次建台账时若一律盖今天，全站日期会集体跳到今天 —— 而它们其实分别是
      09-30 / 10-04 核对的，那就是不实陈述；反过来，接新品牌时若一律保留现值，
      刚入库的数据会顶着旧日期（正是 nomad 那次的毛病）。
    """
    ops: list[tuple] = []
    new_state: dict[str, dict] = {}
    boot: list[str] = []
    added: list[str] = []
    manual: list[tuple] = []
    for key, fp, cur, path, idx in units:
        rec = state.get(key)
        if not isinstance(rec, dict) or "hash" not in rec:
            if state_existed:
                new_state[key] = {"hash": fp, "date": today}
                added.append(key)
                if idx >= 0 and cur != today:
                    ops.append((path, idx, cur, today, key))
            else:
                new_state[key] = {"hash": fp, "date": cur}
                boot.append(key)
            continue
        if rec["hash"] == fp:
            if cur and cur != rec.get("date"):
                manual.append((key, rec.get("date"), cur))
            new_state[key] = {"hash": fp, "date": cur or rec.get("date", "")}
        else:
            new_state[key] = {"hash": fp, "date": today}
            if idx >= 0 and cur != today:
                ops.append((path, idx, cur, today, key))
            # cur == today（同一天内又改了一次）→ 无需改写，但指纹已翻新
    return ops, new_state, boot, added, manual


# ─────────────────────────── 落盘 ───────────────────────────

def apply_ops(ops: list[tuple]) -> int:
    """按文件分组、行号倒序改写，避免行号漂移。返回改写行数。"""
    by_file: dict[pathlib.Path, list[tuple]] = {}
    for path, idx, old, new, key in ops:
        by_file.setdefault(path, []).append((idx, old, new))
    n = 0
    for path, items in by_file.items():
        lines = bc.read_lines(path)
        for idx, old, new in sorted(items, reverse=True):
            m = RE_KV.match(lines[idx])
            if not m or m.group(2) != old:
                sys.exit(f"错误：{path} 第 {idx + 1} 行不再是预期的日期行 "
                         f"（期望 {old!r}，实际 {lines[idx]!r}）")
            lines[idx] = f'{m.group(1)}"{new}"{m.group(3)}'
            n += 1
        with io.open(path, "w", encoding="utf-8", newline="") as f:
            f.write("\n".join(lines))
    return n


def load_state(path: pathlib.Path) -> dict:
    if not path.exists():
        return {}
    try:
        raw = json.loads(path.read_text(encoding="utf-8"))
    except Exception as e:  # noqa: BLE001
        sys.exit(f"错误：状态文件 {path} 无法解析：{e}")
    units = raw.get("units") if isinstance(raw, dict) else None
    return units if isinstance(units, dict) else {}


def save_state(path: pathlib.Path, units: dict[str, dict]) -> bool:
    """写状态文件；内容没变则不落盘（避免无意义的 mtime 抖动）。"""
    payload = {
        "_note": "stamp_checked.py 的内容指纹台账：每份数据改动一次，对应单元的日期"
                 "就前移一次。**必须提交进版本库** —— 删掉它等于把所有数据的"
                 "『最后改动日』抹成未知（下次运行会把现值当基线重新登记，"
                 "不会前移，但也就失去了检测能力）。",
        "_version": 1,
        "units": {k: units[k] for k in sorted(units)},
    }
    text = json.dumps(payload, ensure_ascii=False, indent=2) + "\n"
    if path.exists() and path.read_text(encoding="utf-8") == text:
        return False
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8", newline="\n")
    return True


# ─────────────────────────── 自测 ───────────────────────────

def selftest() -> int:
    ok = True

    def check(name: str, got, want):
        nonlocal ok
        good = got == want
        ok = ok and good
        print(f"  {'PASS' if good else 'FAIL'}  {name}"
              + ("" if good else f"\n        期望 {want!r}\n        实际 {got!r}"))

    P = pathlib.Path("fake.toml")
    today = "2026-10-07"

    def unit(key, fp, date, idx=1):
        return (key, fp, date, P, idx)

    # ① 首次建台账（state_existed=False）→ 保留现值，不编造「今天核过价」
    ops, st, boot, added, manual = decide([unit("plans.x.AR", "aaa", "2026-09-30")], {},
                                          today, state_existed=False)
    check("① 首次建台账不写文件", ops, [])
    check("① 保留现值", st["plans.x.AR"]["date"], "2026-09-30")
    check("① 计入 boot 而非 added", (len(boot), len(added)), (1, 0))

    # ①b 台账已在、而这是新单元（新品牌 / 新市场入库）→ 盖今天
    ops, st, boot, added, _ = decide(
        [unit("plans.new.AR", "zzz", "2026-09-30")],
        {"plans.x.AR": {"hash": "aaa", "date": "2026-09-30"}}, today, state_existed=True)
    check("①b 新单元→盖今天", [(o[2], o[3]) for o in ops], [("2026-09-30", today)])
    check("①b 计入 added 而非 boot", (len(boot), len(added)), (0, 1))

    # ② 指纹变了 → 日期前移
    ops, st, _, _, _ = decide([unit("plans.x.AR", "bbb", "2026-09-30")],
                              {"plans.x.AR": {"hash": "aaa", "date": "2026-09-30"}}, today)
    check("② 数据变→前移", [(o[2], o[3]) for o in ops], [("2026-09-30", today)])
    check("② 台账更新", st["plans.x.AR"], {"hash": "bbb", "date": today})

    # ③ 指纹没变、人改了日期 → 不回滚，台账跟随现值
    ops, st, _, _, manual = decide([unit("plans.x.AR", "aaa", "2026-10-02")],
                                   {"plans.x.AR": {"hash": "aaa", "date": "2026-09-30"}}, today)
    check("③ 人工核对日不回滚", ops, [])
    check("③ 台账跟随现值", st["plans.x.AR"]["date"], "2026-10-02")
    check("③ 计入人工清单", manual, [("plans.x.AR", "2026-09-30", "2026-10-02")])

    # ④ 数据变了但现值已等于今天 → 不产生改写，但指纹要翻新
    ops, st, _, _, _ = decide([unit("plans.x.AR", "ccc", today)],
                              {"plans.x.AR": {"hash": "bbb", "date": today}}, today)
    check("④ 同日再改不重写", ops, [])
    check("④ 指纹仍翻新", st["plans.x.AR"]["hash"], "ccc")

    # ⑤ 幂等：同一输入连跑两次，第二次零操作
    u = [unit("plans.x.AR", "ddd", "2026-09-30")]
    _, st1, _, _, _ = decide(u, {"plans.x.AR": {"hash": "aaa", "date": "2026-09-30"}}, today)
    ops2, _, _, _, _ = decide(u, st1, today)
    check("⑤ 幂等", ops2, [])

    # ⑥ 指纹与日期字段无关：改日期不算改内容
    lines_a = ["[AR]", 'checked = "2026-09-30"', "networks = []", "[[AR.plans]]", 'name = "x"']
    lines_b = ["[AR]", 'checked = "2026-10-99"', "networks = []", "[[AR.plans]]", 'name = "x"']
    ba = bc.Block("AR", 0, len(lines_a), 1, "2026-09-30")
    bb = bc.Block("AR", 0, len(lines_b), 1, "2026-10-99")
    check("⑥ 日期不入指纹", block_hash(lines_a, ba) == block_hash(lines_b, bb), True)

    # ⑥b 注释同样不入指纹（纯注释行 + 行内注释），且引号内的 # 不能被误切
    check("⑥ 剥行内注释", strip_inline_comment('price = 5.00  # 促销'), "price = 5.00")
    check("⑥ 引号内 # 不误伤",
          strip_inline_comment('code = "SAVE#20"  # 码里带井号'), 'code = "SAVE#20"')
    check("⑥ 转义引号不误伤",
          strip_inline_comment('t = "say \\"hi #1\\""  # 尾注'), 't = "say \\"hi #1\\""')
    c1 = ["[AR]", 'checked = "2026-09-30"', 'price = 5.00  # 旧说明']
    c2 = ["[AR]", 'checked = "2026-09-30"', 'price = 5.00  # 新说明']
    check("⑥ 只改行内注释 → 指纹不变",
          block_hash(c1, bc.Block("AR", 0, len(c1), 1, "2026-09-30"))
          == block_hash(c2, bc.Block("AR", 0, len(c2), 1, "2026-09-30")), True)

    # ⑦ 真实数据：单元数**现算**，不许写死 ——
    #    （2026-10-09 实测：这两行曾写死「450 / 9」，接完 nomad、jetpac 后实际是
    #     499 / 10，自测早已 FAIL 却没人跑。写死的品牌数就是会烂在这里。）
    real = collect()
    n_plans = sum(1 for u in real if u[0].startswith("plans."))
    n_prof = sum(1 for u in real if u[0].startswith("profile."))
    # 独立口径：直接数源文件里的字面量块头（不走 collect 的解析路径）
    want_plans = sum(len(re.findall(r"(?m)^\[[A-Z]{2}\]$", p.read_text(encoding="utf-8")))
                     for p in sorted(PLANS_DIR.glob("*.toml")))
    want_prof = len(re.findall(r"(?m)^\[[a-z0-9_]+\]$",
                               PROVIDERS.read_text(encoding="utf-8")))
    check("⑦ 价格单元数 == 各品牌计划文件的国家块总和", n_plans, want_plans)
    check("⑦ 档案单元数 == providers.toml 的品牌数", n_prof, want_prof)
    check("⑦ 全部有日期字段", all(u[4] >= 0 for u in real), True)
    check("⑦ 单元键唯一（品牌×国家不重）", len({u[0] for u in real}), len(real))
    check("⑦ 指纹无碰撞", len({u[1] for u in real}), len(real))

    # ⑦b 段边界按**品牌**切：每家的段必须含**自己的**政策表、不含别家的。
    #     修复前：末尾 10 张 `[<brand>.policy]` 全被算进最后一家（jetpac）。
    prov_lines = bc.read_lines(PROVIDERS)
    pbs = bc.parse_prov_blocks(prov_lines, RE_PROFILE_CHECKED, 1)
    pbu = {b.key: b for b in pbs}
    check("⑦b 品牌数 == 顶层段头数", len(pbs), want_prof)
    check("⑦b 段体区间都已归位（无重叠/乱序）",
          all(all(lo < hi for lo, hi in b.ranges)
              and all(b.ranges[i][1] <= b.ranges[i + 1][0]
                      for i in range(len(b.ranges) - 1))
              for b in pbs), True)
    heads = {b.key: {prov_lines[lo].strip() for lo, _ in b.ranges} for b in pbs}
    check("⑦b 每家的段都含自己的 .policy 表",
          [k for k in pbu if f"[{k}.policy]" not in heads[k]], [])
    check("⑦b jetpac 的段不含 holafly 的政策表",
          "[holafly.policy]" in heads["jetpac"], False)

    # ⑦c 行为反例：改 holafly 的一行政策 → holafly 指纹变、jetpac 指纹**不动**
    #     （修复前正好相反：只有 jetpac 会动，holafly 纹丝不动。）
    base = {k: block_hash(prov_lines, b) for k, b in pbu.items()}
    j = next(i for i, s in enumerate(prov_lines)
             if s.startswith('fup_allowance = "No GB figure published"'))
    mutated = list(prov_lines)
    mutated[j] = 'fup_allowance = "1 GB/day"'
    pbu2 = {b.key: b for b in bc.parse_prov_blocks(mutated, RE_PROFILE_CHECKED, 1)}
    now = {k: block_hash(mutated, b) for k, b in pbu2.items()}
    changed = {k for k in base if base[k] != now[k]}
    check("⑦c 改 holafly 政策 → 只有 holafly 的指纹变", sorted(changed), ["holafly"])

    # ⑧ 端到端（临时目录真写盘）：bootstrap → 改数据 → 只动那一个单元 → 幂等
    with tempfile.TemporaryDirectory() as td:
        tdp = pathlib.Path(td)
        (tdp / "plans").mkdir()
        (tdp / "providers.toml").write_text(
            '[aaa]\nprofile_checked = "2026-09-30"\nstrengths = ["x"]\n',
            encoding="utf-8", newline="\n")
        pf = tdp / "plans" / "aaa.toml"
        pf.write_text('[AR]\nchecked = "2026-09-30"\nprice = 1.00\n'
                      'networks = []\n\n[US]\nchecked = "2026-09-30"\nprice = 2.00\n',
                      encoding="utf-8", newline="\n")

        def units():
            return collect(tdp / "plans", tdp / "providers.toml")

        ops, st, boot, added, _ = decide(units(), {}, today, state_existed=False)
        check("⑧ 首次建台账：零改写 / 三单元", (len(ops), len(st), len(boot), len(added)),
              (0, 3, 3, 0))

        # 只改 AR 的价格
        pf.write_text(pf.read_text(encoding="utf-8").replace("price = 1.00", "price = 1.50"),
                      encoding="utf-8", newline="\n")
        ops, st2, _, _, _ = decide(units(), st, today)
        check("⑧ 只有改动的那国被点名", [o[4] for o in ops], ["plans.aaa.AR"])
        check("⑧ 改写一行", apply_ops(ops), 1)
        txt = pf.read_text(encoding="utf-8")
        check("⑧ 文件日期已前移", '[AR]\nchecked = "2026-10-07"' in txt, True)
        check("⑧ 未动的 US 保持原样", '[US]\nchecked = "2026-09-30"' in txt, True)
        ops2, _, _, _, _ = decide(units(), st2, today)
        check("⑧ 改写后幂等", ops2, [])

        # 只加行尾空格 / 注释行（格式与说明，不进产物）不该触发
        pf.write_text(pf.read_text(encoding="utf-8")
                      .replace("price = 2.00", "price = 2.00   ")
                      .replace("[US]", "# 美国市场\n[US]", 1),
                      encoding="utf-8", newline="\n")
        ops3, _, _, _, _ = decide(units(), st2, today)
        check("⑧ 纯格式调整 / 改注释不触发日期", ops3, [])

        # 改品牌档案（strengths）→ 只动 profile 单元
        (tdp / "providers.toml").write_text(
            '[aaa]\nprofile_checked = "2026-09-30"\nstrengths = ["y"]\n',
            encoding="utf-8", newline="\n")
        ops4, _, _, _, _ = decide(units(), st2, today)
        check("⑧ 改档案只动 profile 单元", [o[4] for o in ops4], ["profile.aaa"])

        # 台账已在、冒出第四个单元（新国家入库）→ 盖今天
        (tdp / "providers.toml").write_text(     # 档案还原，免得混进这次断言
            '[aaa]\nprofile_checked = "2026-09-30"\nstrengths = ["x"]\n',
            encoding="utf-8", newline="\n")
        pf.write_text(pf.read_text(encoding="utf-8")
                      + '\n[DE]\nchecked = "2026-09-30"\nprice = 3.00\n',
                      encoding="utf-8", newline="\n")
        ops5, _, boot5, added5, _ = decide(units(), st2, today)
        check("⑧ 新增国家块→盖今天", [(o[4], o[3]) for o in ops5], [("plans.aaa.DE", today)])
        check("⑧ 新单元计入 added", (len(boot5), len(added5)), (0, 1))

        # ★ 政策表堆在文件末尾、且与自家段隔着别家 —— 归属必须仍按**品牌名**切。
        #   修复前：末尾所有 `.policy` 表都算进最后一家（真实数据里是 jetpac）。
        pvf = tdp / "providers.toml"
        pvf.write_text(
            '[aaa]\nprofile_checked = "2026-09-30"\nstrengths = ["x"]\n'
            '\n[zzz]\nprofile_checked = "2026-09-30"\nstrengths = ["x"]\n'
            '\n[aaa.policy]\nhotspot = "allowed"\n',
            encoding="utf-8", newline="\n")
        _, st6, _, _, _ = decide(units(), st2, today)          # 登记两家 + aaa 的政策
        pvf.write_text(pvf.read_text(encoding="utf-8")
                       .replace('hotspot = "allowed"', 'hotspot = "none"'),
                       encoding="utf-8", newline="\n")
        ops6, st7, _, _, _ = decide(units(), st6, today)
        check("⑧ 末尾政策表归属本家（改它只动 aaa）", [o[4] for o in ops6], ["profile.aaa"])
        # 反向：改**最后一家**的档案，不该带上别家
        pvf.write_text(pvf.read_text(encoding="utf-8")
                       .replace('strengths = ["x"]\n\n[aaa.policy]',
                                'strengths = ["Z"]\n\n[aaa.policy]'),
                       encoding="utf-8", newline="\n")
        ops7, _, _, _, _ = decide(units(), st7, today)
        check("⑧ 改末家档案只动末家", [o[4] for o in ops7], ["profile.zzz"])

    print("\n  " + ("自测全部通过" if ok else "★ 自测存在 FAIL"))
    return 0 if ok else 1


# ─────────────────────────── 主流程 ───────────────────────────

def main() -> int:
    ap = argparse.ArgumentParser(
        description="数据核对日自动盖章（数据变了 → 日期=今天）")
    ap.add_argument("--date", help="盖章日期 YYYY-MM-DD，默认系统今天")
    ap.add_argument("--dry-run", action="store_true", help="只显示会改什么，不写文件")
    ap.add_argument("--check", action="store_true", help="只读；有该盖未盖的则退 1")
    ap.add_argument("--resync", action="store_true",
                    help="指纹口径变更后的迁移：重算全部指纹、**保留现值日期**，"
                         "不改任何 toml（跑一次即可，之后照常构建）")
    ap.add_argument("--state", help=f"状态文件（默认 {STATE_PATH.name}）")
    ap.add_argument("--quiet", action="store_true", help="只在有改动时输出")
    ap.add_argument("--selftest", action="store_true", help="跑内建自测")
    args = ap.parse_args()

    if args.selftest:
        return selftest()

    today = args.date or datetime.date.today().isoformat()
    if not RE_DATE.match(today):
        sys.exit(f"错误：--date 需要 YYYY-MM-DD，收到 {today!r}")

    state_path = pathlib.Path(args.state) if args.state else STATE_PATH
    state_existed = state_path.exists()
    units = collect()
    state = load_state(state_path)

    n_plans = sum(1 for u in units if u[0].startswith("plans."))
    n_prof = len(units) - n_plans

    # ── --resync：指纹**口径**变更后的一次性迁移
    #    指纹本身重算了，但每个单元一律**保留现值日期**——因为内容没变，
    #    变的只是「指纹算哪几行」这个定义。跑完必须肉眼过一遍列出的 hash 变更。
    if args.resync:
        changed, new_state = [], {}
        for key, fp, cur, path, idx in units:
            rec = state.get(key) or {}
            if rec.get("hash") != fp:
                changed.append((key, rec.get("hash") or "(新单元)", fp,
                                rec.get("date") or "(无)", cur))
            new_state[key] = {"hash": fp, "date": cur or rec.get("date", "")}
        print("resync —— 重算指纹、保留现值日期（一次性迁移）")
        print(f"  单元 {n_plans} 个价格 + {n_prof} 个档案；指纹变更 {len(changed)} 处")
        for key, old, new, olddate, cur in changed[:20]:
            print(f"    {key:<26} {str(old):<18} → {new:<18}  日期保留 {cur or olddate}")
        if len(changed) > 20:
            print(f"    … 另有 {len(changed) - 20} 处")
        if args.dry_run:
            print("\n  预演结束，未写入任何文件。")
            return 0
        print(f"\n  状态已{'写' if save_state(state_path, new_state) else '无需改动（内容相同）'}"
              f" {state_path.name}")
        print("  注意：本命令**不改任何 toml 里的日期**。迁移前请先手工核对"
              "被误动的日期是否已复原。")
        return 0

    ops, new_state, boot, added, manual = decide(units, state, today, state_existed)

    # ── --check：只读守门
    if args.check:
        if ops:
            print(f"★ 有 {len(ops)} 处数据已变、日期未跟上（应为 {today}）：")
            for path, idx, old, new, key in ops[:12]:
                print(f"    {key:<26} 现值 {old} → 应为 {new}")
            if len(ops) > 12:
                print(f"    … 另有 {len(ops) - 12} 处")
            print(f"\n  跑 `python -X utf8 scripts/stamp_checked.py` 修好再构建。")
            return 1
        if not args.quiet:
            print(f"OK: 日期与数据一致（{n_plans} 个价格单元 + {n_prof} 个档案单元，"
                  f"今天 {today}）")
        return 0

    # ── 写模式
    written = 0
    if ops and not args.dry_run:
        written = apply_ops(ops)
    state_written = False
    if not args.dry_run and not args.check:
        state_written = save_state(state_path, new_state)

    if not args.quiet or ops or boot or added or manual:
        head = "dry-run  " if args.dry_run else ""
        print(f"{head}stamp_checked.py —— 数据核对日自动盖章")
        print(f"  今天 {today} · 状态 {state_path.relative_to(ROOT) if state_path.is_relative_to(ROOT) else state_path}")
        print(f"  单元  {n_plans} 个价格（plans.<品牌>.<ISO>） + {n_prof} 个档案（profile.<品牌>）")
        if ops:
            print(f"\n  ★ 数据已变 → 日期前移 {len(ops)} 处{'（预演，未写入）' if args.dry_run else ''}")
            for path, idx, old, new, key in ops[:12]:
                print(f"      {key:<26} {old} → {new}")
            if len(ops) > 12:
                print(f"      … 另有 {len(ops) - 12} 处")
        if boot:
            print(f"  · 首次建台账 {len(boot)} 个单元（保留现值，未改日期）")
            for k in boot[:3]:
                print(f"      {k}")
            if len(boot) > 3:
                print(f"      … 另有 {len(boot) - 3} 个")
        if added:
            print(f"  · 新入库单元 {len(added)} 个（新品牌 / 新市场 → 盖 {today}）")
            for k in added[:6]:
                print(f"      {k}")
            if len(added) > 6:
                print(f"      … 另有 {len(added) - 6} 个")
        if manual:
            print(f"  · 人工核对日 {len(manual)} 处（指纹没变，尊重现值）")
            for key, old, new in manual[:6]:
                print(f"      {key:<26} {old} → {new}")
        print()
        if args.dry_run:
            print("  预演结束，未写入任何文件。")
        elif ops:
            print(f"  已改写 {written} 行 → 下一步 npm run build"
                  f"（页面日期 / dateModified / sitemap lastmod 会一起前移）")
        else:
            print("  无改动：数据没变，日期保持不动。")
        if state_written:
            print(f"  状态已写 {state_path.name}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
