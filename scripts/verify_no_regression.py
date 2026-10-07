# -*- coding: utf-8 -*-
"""零回归边界守卫 —— 回答「这轮改造有没有伤到别的页型」。

为什么需要它：`verify_provider_pages.py` 只盯品牌×国家子页。本轮改造必然
改到共享组件（`country-stats.html` / `head.html` / `plan-data-label.html`），
它们的下游是**全站每一个页**。「本层通过」不等于「别处没坏」。

它做四件事：

  检查 A 改造标记隔离 —— `#reality` / `#trip-calc` / `#fit` 这些本轮新增的区块
         只允许出现在品牌子页；一旦出现在国家 Hub / 指南 / 工具页，说明改错了地方。
         同时正向断言：品牌子页必须**确实**带上这些区块（否则是漏渲染）。

  检查 B 全站不变量 —— 恰好 1 个 h1、title 非空、无 `{{` / `}}` / `<no value>`
         / `%!x(...)` 残留、无空的 h2/h3、JSON-LD 可解析。全站每页都扫。

  检查 C gb 哨兵跨页型一致性 —— `gb` 用 0 表示"无限"、小于 1GB 存小数。
         任何一处 `int .gb` 都会把 500MB 变成"Unlimited"。本项覆盖品牌子页
         **和国家 Hub**（后者是前一版守卫的盲区）。

  检查 D 基线清单 + 字节级 diff —— 产出一份 `docs/regression-manifest.json`
         （每页 sha256）。下一轮改完跑 `--diff` 就能知道**具体哪几个文件变了**，
         并据此判断变化是否落在预期白名单内。

⚠️ 品牌集与页数**一律从 data/ 推导，不写死**（2026-10-06 因写死 8 品牌集，
   新品牌页掉进 static 兜底、报出 401 条假失败）。

  检查 D 基线清单 + 字节级 diff —— 产出一份 `docs/regression-manifest.json`
         （每页 sha256）。下一轮改完跑 `--diff` 就能知道**具体哪几个文件变了**，
         并据此判断变化是否落在预期白名单内。

用法：
    python -X utf8 scripts/verify_no_regression.py                  # 跑 A/B/C
    python -X utf8 scripts/verify_no_regression.py --write-manifest # 另存基线
    python -X utf8 scripts/verify_no_regression.py --diff docs/regression-manifest.json
    python -X utf8 scripts/verify_no_regression.py --strict-diff docs/regression-manifest.json
    python -X utf8 scripts/verify_no_regression.py --selftest       # 注入反例自测
"""
from __future__ import annotations

import argparse
import hashlib
import html
import json
import re
import sys
import tempfile
import tomllib
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PUBLIC = ROOT / "public"
MANIFEST = ROOT / "docs" / "regression-manifest.json"

# 品牌集必须从 data/providers.toml 推导，不能写死。
# 2026-10-06 事故：写死的 8 品牌集不认识新接入的 nomad，于是
# `compare/<国>/nomad/index.html` 被 classify() 落到 "static" 兜底，
# 接着检查 A 报「static 页里出现了品牌子页专属区块」—— 一口气 401 条假失败，
# 而真相只是守卫不认识新品牌。**页型判据依赖的数据集变了，判据必须跟着变。**
BRANDS = {
    k for k, v in (tomllib.loads((ROOT / "data" / "providers.toml").read_text(encoding="utf-8"))).items()
    if isinstance(v, dict) and v.get("name")
}

TITLE_RE = re.compile(r"<title>(.*?)</title>", re.S)
H1_RE = re.compile(r"<h1[^>]*>(.*?)</h1>", re.S)
H2H3_RE = re.compile(r"<h([23])[^>]*>(.*?)</h\1>", re.S)
LDJSON_RE = re.compile(r'<script type="application/ld\+json">(.*?)</script>', re.S)
# 模板注入的**纯数据**块（如品牌页 #prov-calc-data 的计算器输入）。
# 这类块里 `{{`/`}}` 是合法的嵌套 JSON 括号，不是模板残留 —— 必须先从
# 「模板残留」扫描里剔除，否则会误报（踩过：`…"u":[…]}}` 被判成 '}}' 残留）。
APPDATA_RE = re.compile(r'<script[^>]*type="application/json"[^>]*>(.*?)</script>', re.S)
DATA_BLOCK_RE = re.compile(
    r'<script[^>]*type="application/(?:ld\+json|json)"[^>]*>.*?</script>', re.S)
ALIAS_RE = re.compile(r'http-equiv=["\']?refresh', re.I)

# 套餐行：<tr data-price="…" … data-gb="…" …>…</tr>
PLAN_ROW_RE = re.compile(
    r'<tr data-price="[^"]*"[^>]*data-gb="([^"]*)"[^>]*>(.*?)</tr>', re.S)
TD_RE = re.compile(r"<td[^>]*>(.*?)</td>", re.S)

FMT_ERROR = re.compile(r"%![A-Za-z]*(?:\([^)]*\))?")

# ---------------------------------------------------------------- 检查 A 配置
# 本轮新增/重做的区块 id → 允许出现的页型白名单。
# **必须带收尾引号**：`id="tradeoffs"` 会误匹配 `id="tradeoffs-pending"`（踩过）。
MARKER_ALLOWED: dict[str, set[str]] = {
    'id="verdict"':     {"provider_sub", "country_hub"},   # 国家 Hub 也有结论段
    'id="fup"':         {"provider_sub", "country_hub"},
    # 品牌 Hub 的 #reality 是**品牌级**「Plan reality check」（热点/公平使用/充值/5G），
    # 与子页的**国家级**同名区块内容不同、数据源不同（providers.toml policy vs plans）。
    # 2026-10-04 品牌 Hub 改造时新增，属预期扩面，不是模板泄漏。
    'id="reality"':     {"provider_sub", "provider_hub"},
    'id="hostnetwork"': {"provider_sub"},
    'id="tripcost"':    {"provider_sub"},
    'id="trip-calc"':   {"provider_sub"},
    'id="fit"':         {"provider_sub"},
    # 品牌详情页 /esim-providers/<品牌>/ 有自己的「Price record」章节，
    # 恰好也叫 #tradeoffs（2026-10-04 核实过是既有独立区块，不是本轮泄漏）。
    'id="tradeoffs"':   {"provider_sub", "provider_hub"},
    # 同名不同物：工具页 /tools/ 早有跨品牌行程计算器 #calc（line 88），
    # 品牌 Hub 本轮也加了一个**只算本品牌**的 #calc，并被 JSON-LD 的 url
    # `%s#calc` 引用。id 是页内作用域，两者互不冲突，故登记为共享。
    'id="calc"':        {"provider_hub", "tools"},
}
# 品牌详情页本轮新增的互动区块（同样只允许出现在品牌 Hub）。
# 不计入 MARKER_REQUIRED —— 它们依赖 $cov 非空，降级壳页没有覆盖数据。
MARKER_ALLOWED_HUB: dict[str, set[str]] = {
    'id="whobeats"':   {"provider_hub"},
    'id="network"':    {"provider_hub"},
    'id="headtohead"': {"provider_hub"},
    'id="reading"':    {"provider_hub"},
}
# 品牌子页必须**存在**的区块（漏渲染是回归，不是"少一块就少一块"）
MARKER_REQUIRED = ('id="verdict"', 'id="plans"', 'id="reality"', 'id="tripcost"',
                   'id="fit"', 'id="faq"')

# 检查 C：不同页型里「数据量」单元格的 td 下标
# provider_sub: td[0]=品牌 td[1]=数据量
# country_hub : td[0]=品牌 td[1]=套餐名 td[2]=数据量
DATA_CELL_IDX = {"provider_sub": 1, "country_hub": 2}

# 检查 B：允许例外（默认空）。键是相对 public 的路径，值是理由。
TEMPLATE_ALLOW: dict[str, str] = {}


def text_of(raw: str) -> str:
    return html.unescape(re.sub(r"<[^>]+>", "", raw)).strip()


def classify(rel: str) -> str:
    """把产物相对路径归到一个页型。段数不同（`compare/<国>/` vs
    `compare/<国>/<品牌>/`）很容易分类错 —— 这里把判据写死并自测。"""
    parts = rel.split("/")
    if parts and parts[0] == "de":
        parts = parts[1:]
    n = len(parts)
    if n == 4 and parts[0] == "compare" and parts[3] == "index.html" \
            and parts[2] in BRANDS:
        return "provider_sub"
    if n == 3 and parts[0] == "compare" and parts[2] == "index.html":
        return "matchup" if "-vs-" in parts[1] else "country_hub"
    if n == 2 and parts == ["compare", "index.html"]:
        return "compare_index"
    if n == 3 and parts[0] == "esim-providers" and parts[1] in BRANDS:
        return "provider_hub"
    if n == 2 and parts == ["esim-providers", "index.html"]:
        return "provider_hub"
    if n == 2 and parts == ["esim-deals", "index.html"]:
        return "deals"
    for seg in ("guides", "networks", "research", "tools"):
        if parts and parts[0] == seg:
            return seg
    if n == 1 and parts[0] == "index.html":
        return "home"
    if n == 2 and parts[1] == "index.html" and parts[0] == "en":
        return "alias_shell"
    return "static"


def scan(root: Path) -> tuple[list[str], dict, dict, dict]:
    """扫描一棵产物树。返回 (errors, class_counts, per_file_info, stats)。"""
    errors: list[str] = []
    class_counts: Counter[str] = Counter()
    info: dict[str, dict] = {}
    stats = Counter()

    pages = sorted(p for p in root.rglob("*.html"))
    for f in pages:
        rel = f.relative_to(root).as_posix()
        cls = classify(rel)
        class_counts[cls] += 1
        raw = f.read_text(encoding="utf-8", errors="replace")
        is_alias = bool(ALIAS_RE.search(raw))

        # ---- 检查 A：标记隔离 + 必需区块 ----
        for marker, allowed in (*MARKER_ALLOWED.items(), *MARKER_ALLOWED_HUB.items()):
            if marker in raw and cls not in allowed:
                errors.append(
                    f"[A:{cls}] {rel}: 出现了只属于 {sorted(allowed)} 的区块 {marker}")
        if cls == "provider_sub":
            for marker in MARKER_REQUIRED:
                if marker not in raw:
                    errors.append(f"[A:provider_sub] {rel}: 缺必需区块 {marker}")

        # ---- 检查 B：全站不变量 ----
        if not is_alias:
            h1s = H1_RE.findall(raw)
            if len(h1s) != 1:
                errors.append(f"[B] {rel}: {len(h1s)} 个 <h1>（应为 1）")
        mt = TITLE_RE.search(raw)
        title = html.unescape(mt.group(1)).strip() if mt else ""
        if not title:
            errors.append(f"[B] {rel}: <title> 缺失或为空")
        if rel not in TEMPLATE_ALLOW:
            # 先把 application/json / ld+json 数据块挖掉：那里的 `{{`/`}}` 是合法
            # JSON 括号。可执行 <script> 仍然照扫 —— 真正的模板泄漏藏在那里。
            raw_no_data = DATA_BLOCK_RE.sub("<script></script>", raw)
            for bad in ("{{", "}}", "<no value>"):
                if bad in raw_no_data:
                    errors.append(f"[B] {rel}: 产物含模板残留 {bad!r}")
                    break
        mfmt = FMT_ERROR.search(raw)
        if mfmt:
            errors.append(f"[B] {rel}: 产物含 Go 格式化残留 {mfmt.group(0)!r}")
        if not is_alias:
            for lvl, inner in H2H3_RE.findall(raw):
                if not text_of(inner):
                    errors.append(f"[B] {rel}: 空的 <h{lvl}></h{lvl}>")
        for m in LDJSON_RE.finditer(raw):
            try:
                json.loads(m.group(1))
            except ValueError as e:
                errors.append(f"[B] {rel}: JSON-LD 解析失败 - {e}")
        # 模板注入的数据块同样必须是可解析 JSON —— 把它从「误报源」变成一处真实检查。
        for m in APPDATA_RE.finditer(raw):
            try:
                json.loads(m.group(1))
            except ValueError as e:
                errors.append(f"[B] {rel}: 注入数据块 application/json 解析失败 - {e}")

        # ---- 检查 C：gb 哨兵一致性 ----
        idx = DATA_CELL_IDX.get(cls)
        if idx is not None:
            for gb_raw, body in PLAN_ROW_RE.findall(raw):
                if not gb_raw:
                    continue          # 空值是"未指定"，不是无限
                try:
                    gb = float(gb_raw)
                except ValueError:
                    errors.append(f"[C] {rel}: data-gb 不是数字 -> {gb_raw!r}")
                    continue
                cells = TD_RE.findall(body)
                if len(cells) <= idx:
                    errors.append(
                        f"[C] {rel}: 套餐行只有 {len(cells)} 个 td，取不到第 {idx} 格")
                    continue
                cell = text_of(cells[idx])
                says_unl = "unlimited" in cell.lower()
                if gb == 0.0:
                    stats["rows_unlimited"] += 1
                    if not says_unl:
                        errors.append(f"[C] {rel}: data-gb=0（无限）但数据格是 {cell!r}")
                elif gb < 1.0:
                    stats["rows_sub1gb"] += 1
                    if says_unl:
                        errors.append(
                            f"[C] {rel}: data-gb={gb_raw}（计量）却标成 Unlimited -> {cell!r}")
                    elif not re.match(r"^\d+\s?MB$", cell):
                        errors.append(
                            f"[C] {rel}: data-gb={gb_raw} 小于 1GB，数据格应是 MB -> {cell!r}")
                else:
                    stats["rows_metered"] += 1
                    if says_unl:
                        errors.append(
                            f"[C] {rel}: data-gb={gb_raw}（计量）却标成 Unlimited -> {cell!r}")

        info[rel] = {
            "cls": cls,
            "sha256": hashlib.sha256(f.read_bytes()).hexdigest(),
            "title_len": len(title),
        }

    return errors, dict(class_counts), info, dict(stats)


def write_manifest(class_counts: dict, info: dict) -> None:
    MANIFEST.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "generated_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "note": "零回归基线。下一轮改完跑 verify_no_regression.py --diff <本文件>，"
                "即可看出哪些页发生变化；provider_sub 变更是预期的，其余需人工确认。",
        "class_counts": dict(sorted(class_counts.items())),
        "files": dict(sorted(info.items())),
    }
    MANIFEST.write_text(json.dumps(payload, ensure_ascii=False, indent=1),
                        encoding="utf-8", newline="\n")
    print(f"已写基线 -> {MANIFEST.relative_to(ROOT).as_posix()}"
          f"（{len(info)} 个文件）")


def diff_manifest(path: Path, info: dict, strict: bool) -> int:
    old = json.loads(path.read_text(encoding="utf-8"))
    oldf = old.get("files", {})
    changed, added, removed = [], [], []
    for rel, meta in info.items():
        if rel not in oldf:
            added.append(rel)
        elif oldf[rel]["sha256"] != meta["sha256"]:
            changed.append(rel)
    for rel in oldf:
        if rel not in info:
            removed.append(rel)

    def by_class(rels):
        c: dict[str, list[str]] = defaultdict(list)
        for r in rels:
            c[info.get(r, oldf.get(r, {})).get("cls", "?")].append(r)
        return c

    print(f"\n与基线 {path.name} 比对（基线生成于 {old.get('generated_at')}）")
    for label, rels in (("变更", changed), ("新增", added), ("删除", removed)):
        g = by_class(rels)
        total = len(rels)
        print(f"  {label} {total}: " +
              (", ".join(f"{k}={len(v)}" for k, v in sorted(g.items())) if g else "-"))
        for k, v in sorted(g.items()):
            mark = "预期" if k == "provider_sub" else "★需确认"
            if k != "provider_sub":
                for r in v[:5]:
                    print(f"      [{mark}] {r}")
                if len(v) > 5:
                    print(f"      ... 另有 {len(v) - 5} 个")

    unexpected = [r for r in changed + added + removed
                  if info.get(r, oldf.get(r, {})).get("cls") != "provider_sub"]
    if not (changed or added or removed):
        print(f"\n  与基线完全一致（{len(info)} 个页面逐字节相同）"
              f" —— 构建是确定性的，或本轮未改产物")
    elif unexpected:
        print(f"\n  非品牌子页的变化 {len(unexpected)} 处 —— 逐条确认是否为本轮预期改动")
        if strict:
            return 1
    else:
        print("\n  所有变化都落在品牌子页白名单内")
    return 0


def selftest() -> int:
    """注入反例：每个检查都要**证明过它会失败**，否则 bad=0 没有意义。"""
    cases = {
        "template-residue": (
            "guides/broken/index.html",
            "<title>T</title><h1>H</h1><p>{{/* TODO */}}</p>",
            "[B]"),
        "double-h1": (
            "guides/two-h1/index.html",
            "<title>T</title><h1>A</h1><h1>B</h1>",
            "[B]"),
        "marker-leak": (
            "guides/leak/index.html",
            '<title>T</title><h1>H</h1><div id="trip-calc"></div>',
            "[A:guides]"),
        "gb-sentinel": (
            "compare/nowhere/index.html",
            '<title>T</title><h1>H</h1>'
            '<tr data-price="1.00" data-gb="0.4883"><td>X</td>'
            '<td>500MB</td><td>Unlimited</td></tr>',
            "[C]"),
        "gb-sentinel-sub1-mislabelled": (
            "compare/nowhere2/index.html",
            '<title>T</title><h1>H</h1>'
            '<tr data-price="1.00" data-gb="0.4883"><td>X</td><td>Unlimited</td></tr>',
            "[C]"),
        "hub-marker-leak": (
            "guides/hubleak/index.html",
            '<title>T</title><h1>H</h1><div id="whobeats"></div>',
            "[A:guides]"),
        # want=None → 期望**不**报错。这两条一起锁住本次修复的边界：
        # 数据块里的花括号要放过，可执行 <script> 里的真泄漏仍要抓住。
        "json-data-block-braces": (
            "guides/data/index.html",
            '<title>T</title><h1>H</h1>'
            '<script id="d" type="application/json">{"a":{"b":[1,2]}}</script>',
            None),
        "exec-script-still-scanned": (
            "guides/exec/index.html",
            '<title>T</title><h1>H</h1><script>var x = "{{ .Boom }}";</script>',
            "[B]"),
    }
    failed = 0
    with tempfile.TemporaryDirectory() as td:
        tmp = Path(td)
        for name, (rel, body, want) in cases.items():
            p = tmp / rel
            p.parent.mkdir(parents=True, exist_ok=True)
            p.write_text(body, encoding="utf-8")
        errs, _, _, _ = scan(tmp)
        for name, (rel, body, want) in cases.items():
            hit = [e for e in errs if rel in e and (want is None or e.startswith(want))]
            ok = (not hit) if want is None else bool(hit)
            failed += 0 if ok else 1
            label = "期望 无报错" if want is None else f"期望 {want}"
            print(f"  {'OK  ' if ok else 'MISS'} {name:32s} {label}")
            for e in hit[:2]:
                print(f"        -> {e}")
    # 分类自测：段数不同不能混为一谈（踩过一次）
    # 2026-10-06 加最后两条：品牌集必须来自 data/providers.toml —— 写死品牌集时，
    # 新接入的品牌页会掉进 "static" 兜底，触发 401 条假失败。这两条把它钉死。
    cls_cases = [
        ("compare/netherlands/holafly/index.html", "provider_sub"),
        ("compare/netherlands/index.html", "country_hub"),
        ("de/compare/netherlands/index.html", "country_hub"),
        ("compare/airalo-vs-saily/index.html", "matchup"),
        ("esim-providers/holafly/index.html", "provider_hub"),
        ("tools/index.html", "tools"),
        ("compare/netherlands/nomad/index.html", "provider_sub"),
        ("esim-providers/nomad/index.html", "provider_hub"),
    ]
    for rel, want in cls_cases:
        got = classify(rel)
        ok = got == want
        failed += 0 if ok else 1
        print(f"  {'OK  ' if ok else 'MISS'} classify {rel:42s} -> {got}")
    print(f"\n自测{'通过' if not failed else f'失败 {failed} 项'}")
    return 1 if failed else 0


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--write-manifest", action="store_true")
    ap.add_argument("--diff", type=Path, help="与给定基线比对")
    ap.add_argument("--strict-diff", action="store_true",
                    help="非品牌子页出现变更/新增/删除即失败")
    ap.add_argument("--selftest", action="store_true")
    args = ap.parse_args()

    if args.selftest:
        return selftest()

    if not PUBLIC.is_dir():
        print("ERROR public/ not found - run `hugo` first")
        return 1

    errors, class_counts, info, stats = scan(PUBLIC)

    print(f"全站 {sum(class_counts.values())} 个 HTML 页")
    for k, v in sorted(class_counts.items(), key=lambda x: -x[1]):
        print(f"  {v:5d}  {k}")
    print(f"  套餐行：无限 {stats.get('rows_unlimited', 0)} /"
          f" 计量 {stats.get('rows_metered', 0)} /"
          f" 小于 1GB {stats.get('rows_sub1gb', 0)}"
          f"（品牌子页 + 国家 Hub 合计）")

    if args.write_manifest:
        write_manifest(class_counts, info)

    rc = 0
    if args.diff:
        if not args.diff.is_file():
            print(f"ERROR 找不到基线 {args.diff}")
            return 1
        rc = diff_manifest(args.diff, info, args.strict_diff)

    if errors:
        print(f"\nFAIL: {len(errors)} 处问题")
        for e in errors[:40]:
            print(f"  ✗ {e}")
        if len(errors) > 40:
            print(f"  ... 另有 {len(errors) - 40} 处")
        return 1
    print("\nOK: 检查 A（标记隔离）/ B（全站不变量）/ C（gb 哨兵）全部通过")
    return rc


if __name__ == "__main__":
    sys.exit(main())
