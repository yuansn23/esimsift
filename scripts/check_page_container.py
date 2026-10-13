#!/usr/bin/env python -X utf8
"""check_page_container.py —— 每个页型模板的 `main` 块里必须存在**容器**。

## 为什么要有这条判据（2026-10-13 第九十轮补，用户报的缺陷）
用户报「/guides/ 这个页面太宽，和其他页面布局不一样，宽度跑到屏幕外」。
取证（`.buildlog/r90b_width_probe.py`）后确认：`layouts/_default/baseof.html` 的
`<main class="flex-1">` **不带任何宽度 / 居中 / 内边距**，容器一律由各页型模板自负；
而 `layouts/_default/list.html`（服务 `/guides/` 及其德语页）里**一个容器都没有** ——
第一层就是 `<div class="py-4">`，没有 `mx-auto`、没有 `max-w-*`、没有 `px-*`。
其余 21 个页型模板全部有容器（`mx-auto max-w-7xl px-4 py-8 sm:px-6` 这一族）。
后果：内容横铺到视口边缘、居中失效 ⇒ 宽屏上像「宽度跑到屏幕外」。

这不是第九十轮改出来的（`git diff` 证明 `py-4` 那行本轮没动），而是**长期存在**的：
上一轮把指南卡的正文 / 说明 / 元信息加厚后，视觉上才暴露。**用了很久没人发现，
正是因为「容器一致性」此前没有任何判据** —— `check_css_sync.py` 只管 class 编译同步、
`check_output.py` 只管产物文本、`check_headings*.py` 只管标点，没有一条判据知道
「这一页的内容有没有被约束在居中的最大宽度里」。

## 判据（源码层，秒级）
扫 `layouts/**/*.html` 里所有含 `{{ define "main" }}` 的模板，对每个 `main` 块：
  1. 先把 `{{/* … */}}` **注释整体掩成等长空格**（保持偏移与行号不变）；
  2. 用括号平衡（`define|if|with|range|block` ↔ `end`）切出块的**精确范围**
     —— 必须在掩掉注释**之后**做，否则注释正文里写着的 `` `{{- end }}` `` 会把深度提前归零；
  3. 块内再掩掉所有 `{{ … }}` action，然后取 `class="…"`；
  4. 断言**至少有一个**元素的 class 同时含 `mx-auto` 与**页面级**宽度上限
     （`max-w-2xl` … `max-w-8xl`）。
两个合法结构都能过：
  A. 首元素即容器 —— 绝大多数页；
  B. 首元素是**满幅层**（如首页 / 404 的 `relative overflow-hidden bg-hero-mesh`），
     容器在它内部 —— 所以判据是「块内存在」，不是「首元素必须是」。
刻意**不算**容器的地方（各有反例用例守着）：注释里、action 字符串里、正文文字里写着
`mx-auto max-w-7xl`；以及**组件级**宽度（`max-w-xs|sm|md|lg|xl`，如 `<p class="mx-auto
mt-3 max-w-md">` 那种居中短句）—— 只认**页面级**宽度。

**WARN（不红）**：容器有页面级 `max-w-*` 但**没有 `px-*`** —— 窄视口下内容会贴屏幕边。
已知落点：`_default/single.html` 与 `_default/methodology.html` 的
`<article class="mx-auto max-w-3xl">`（about / contact / privacy / terms / disclosure /
methodology 共 12 个产物页）。改它要动 12 个产物页，属**独立决策** ⇒ 只提示、不拦构建。

## 边界（本脚本看不见什么）
  · 容器类若由 `{{ partial }}` 产出（首元素是 partial 调用），本脚本判不了 —— 目前
    `main` 块首元素全是字面标签，无此形态；若将来出现，需先展开再判。
  · JS 动态插入的容器不在此列（本站无此形态）。
  · 它只管「**有没有**容器」，**不管容器选得对不对**（`max-w-3xl` vs `max-w-7xl` 属设计决策）。

用法：
  python -X utf8 scripts/check_page_container.py
  python -X utf8 scripts/check_page_container.py --selftest
"""
from __future__ import annotations

import re
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

DEFINE_MAIN = re.compile(r"\{\{-?\s*define\s+\"main\"\s*-?\}\}")
OPEN_BLOCK = re.compile(r"\{\{-?\s*(?:define|if|with|range|block)\b")
END_BLOCK = re.compile(r"\{\{-?\s*end\s*-?\}\}")
COMMENT = re.compile(r"\{\{-?\s*/\*.*?\*/\s*-?\}\}", re.S)
ACTION = re.compile(r"\{\{-?.*?-?\}\}", re.S)
ANY_TAG = re.compile(r"<([a-zA-Z][a-zA-Z0-9]*)\b([^>]*)>")
CLASS_ATTR = re.compile(r'class\s*=\s*"([^"]*)"')

# 页面级宽度上限（组件级 max-w-xs|sm|md|lg|xl 不算容器）
PAGE_WIDTHS = ("max-w-2xl", "max-w-3xl", "max-w-4xl", "max-w-5xl",
               "max-w-6xl", "max-w-7xl", "max-w-8xl")
NEED_CENTER = "mx-auto"


def mask(m: re.Match) -> str:
    """把匹配段换成等长空格：偏移与行号 1:1 不变。"""
    return " " * (m.end() - m.start())


def line_of(text: str, off: int) -> int:
    return text.count("\n", 0, off) + 1


def main_block_range(masked: str, start: int):
    """在**已掩掉注释**的文本上，用括号平衡找 main 块范围；返回 (begin, end)。"""
    depth = 1
    pos = start
    while pos < len(masked) and depth > 0:
        o = OPEN_BLOCK.search(masked, pos)
        e = END_BLOCK.search(masked, pos)
        if not e:
            return start, len(masked)
        if o and o.start() < e.start():
            depth += 1
            pos = o.end()
        else:
            depth -= 1
            pos = e.end()
            if depth == 0:
                return start, e.start()
    return start, len(masked)


def scan_class_attrs(masked_body: str):
    """入参须是已掩注释的块体；此处再掩 action。返回 [(tag, cls, offset_in_body)]。"""
    clean = ACTION.sub(mask, masked_body)
    out = []
    for m in ANY_TAG.finditer(clean):
        c = CLASS_ATTR.search(m.group(2))
        if c:
            out.append((m.group(1).lower(), c.group(1), m.start()))
    return out


def is_container(cls: str) -> bool:
    return NEED_CENTER in cls and any(w in cls for w in PAGE_WIDTHS)


def check_text(text: str, label: str):
    problems, warns = [], []
    masked = COMMENT.sub(mask, text)          # ① 注释先掩掉（含注释里的 {{ end }}）
    for dm in DEFINE_MAIN.finditer(masked):
        b, e = main_block_range(masked, dm.end())
        attrs = scan_class_attrs(masked[b:e])
        containers = [(t, c, o) for t, c, o in attrs if is_container(c)]
        if not containers:
            first = f'<{attrs[0][0]} class="{attrs[0][1]}">' if attrs else "（没有任何带 class 的元素）"
            problems.append((label, line_of(masked, b),
                             "main 块内没有任何容器（需同时含 mx-auto 与页面级 max-w-2xl…8xl）；"
                             f"首个元素 = {first}"))
            continue
        for t, c, o in containers:
            if "px-" not in c:
                warns.append((label, line_of(masked, b + o),
                              f'容器 <{t}> 有页面级 max-w 但无 px-* ⇒ 窄视口贴边：class="{c}"'))
    return problems, warns


def run_layouts(layouts: Path):
    problems, warns, scanned = [], [], 0
    for f in sorted(layouts.rglob("*.html")):
        text = f.read_bytes().decode("utf-8")
        if not DEFINE_MAIN.search(COMMENT.sub(mask, text)):
            continue                      # partials / baseof：不是页型模板
        scanned += 1
        p, w = check_text(text, f.relative_to(layouts).as_posix())
        problems += p
        warns += w
    return problems, warns, scanned


# ────────────────────────────── selftest ──────────────────────────────
POSITIVE = {
    # A 型：首元素即容器
    "ok_index.html": '{{ define "main" }}\n<div class="mx-auto max-w-7xl px-4 py-8 sm:px-6">\n  <h1>x</h1>\n</div>\n{{ end }}\n',
    "ok_after_comment.html": '{{ define "main" }}\n{{/* 说明：容器见下 */}}\n<div class="mx-auto max-w-3xl px-4">\n</div>\n{{ end }}\n',
    "ok_inline_actions.html": '{{ define "main" }}{{ $d := .Params.x }}\n<div class="mx-auto max-w-6xl px-4 py-8 sm:px-6">\n</div>\n{{ end }}\n',
    "ok_article.html": '{{ define "main" }}\n<article class="mx-auto max-w-3xl px-4">\n</article>\n{{ end }}\n',
    # B 型：首元素是满幅 hero，容器在其内部（首页 / 404 的真实形态）
    "ok_hero_full_bleed.html": '{{ define "main" }}\n<section class="relative overflow-hidden bg-hero-mesh">\n  <div class="mx-auto max-w-7xl px-4 sm:px-6">x</div>\n</section>\n{{ end }}\n',
    # 外层无容器的包裹 div、内层有容器 —— 视觉正常
    "ok_outer_wrapper_no_class.html": '{{ define "main" }}\n<div class="py-4">\n  <div class="mx-auto max-w-7xl px-4">x</div>\n</div>\n{{ end }}\n',
    # 容器在嵌套 if/with 里（块范围判定必须靠括号平衡覆盖到）
    "ok_nested_blocks.html": '{{ define "main" }}\n{{ with .Params.a }}\n<div class="mx-auto max-w-5xl px-4">{{ . }}</div>\n{{ end }}\n{{ end }}\n',
    # ★ 真实陷阱（tools/list.html 的形态）：注释正文里写着 `{{- end }}`，
    #   若不在掩注释之前就做括号平衡，深度会提前归零、把容器整段切掉 ⇒ 假红
    "ok_comment_mentions_end.html": '{{ define "main" }}\n{{/* 这段零输出，但 `{{- end }}` 尾部故意不写 dash */}}\n{{ range .Pages }}x{{ end }}\n<div class="mx-auto max-w-7xl px-4 py-8 sm:px-6">y</div>\n{{ end }}\n',
    # 多行 action（tools/list.html 的 `$acts := slice … }}` 形态）不得打乱偏移
    "ok_multiline_action.html": '{{ define "main" }}\n{{ $acts := slice\n  (dict "id" "browse" "mb" 60)\n}}\n<div class="mx-auto max-w-7xl px-4">y</div>\n{{ end }}\n',
    # 非页型模板（无 define main）必须整份跳过
    "partial_no_define.html": '<div class="py-4">这不是页型模板，必须整份跳过</div>\n',
}

NEGATIVE = {
    # 真实缺陷形态：/guides/ 改造前就是这样
    "bad_bare_py4.html": '{{ define "main" }}\n<div class="py-4">\n  <h1>x</h1>\n</div>\n{{ end }}\n',
    "bad_no_maxw.html": '{{ define "main" }}\n<div class="mx-auto px-4">\n</div>\n{{ end }}\n',
    "bad_no_mxauto.html": '{{ define "main" }}\n<div class="max-w-7xl px-4">\n</div>\n{{ end }}\n',
    "bad_no_class.html": '{{ define "main" }}\n<section>\n</section>\n{{ end }}\n',
    "bad_empty_main.html": '{{ define "main" }}\n{{ end }}\n',
    # ① 容器只写在注释里 —— 不算
    "bad_only_in_comment.html": '{{ define "main" }}\n{{/* mx-auto max-w-7xl */}}\n<div class="py-4">x</div>\n{{ end }}\n',
    # ② 容器只写在 action 字符串里 —— 不算
    "bad_only_in_action.html": '{{ define "main" }}\n{{ $x := "mx-auto max-w-7xl" }}\n<div class="py-4">{{ $x }}</div>\n{{ end }}\n',
    # ③ 容器字样只出现在正文文字里 —— 不算
    "bad_only_in_text.html": '{{ define "main" }}\n<div class="py-4"><p>we use mx-auto max-w-7xl everywhere</p></div>\n{{ end }}\n',
    # ④ 块范围之外有容器（另一个 define 里）—— 不得顶替 main 块自己的容器
    "bad_container_in_other_define.html": '{{ define "main" }}\n<div class="py-4">x</div>\n{{ end }}\n{{ define "extra" }}\n<div class="mx-auto max-w-7xl px-4">y</div>\n{{ end }}\n',
    # ⑤ 只有组件级宽度（居中短句）—— 不算页面容器
    "bad_only_component_width.html": '{{ define "main" }}\n<div class="py-4">\n  <p class="mx-auto mt-3 max-w-md text-ink-300">居中短句，不是页面容器</p>\n</div>\n{{ end }}\n',
}


def selftest() -> int:
    fails = []
    with tempfile.TemporaryDirectory() as td:
        base = Path(td)
        pos_dir, neg_dir = base / "pos", base / "neg"
        pos_dir.mkdir()
        neg_dir.mkdir()
        for name, body in POSITIVE.items():
            (pos_dir / name).write_bytes(body.encode("utf-8"))
        for name, body in NEGATIVE.items():
            (neg_dir / name).write_bytes(body.encode("utf-8"))
        p_problems, _, p_scanned = run_layouts(pos_dir)
        n_problems, n_warns, n_scanned = run_layouts(neg_dir)

    print(f"  [selftest] 正例 {len(POSITIVE)} 份（含 1 份非页型模板）· 反例 {len(NEGATIVE)} 份")
    print("  [selftest] 反例逐条命中：")
    for lbl, ln, msg in sorted(n_problems):
        print(f"      RED  {lbl}:{ln}  {msg[:100]}")

    if p_problems:
        fails.append(f"[正例误伤] {p_problems}")
    if p_scanned != len(POSITIVE) - 1:
        fails.append(f"[正例扫描数] 期望 {len(POSITIVE)-1}（partial 须跳过），实测 {p_scanned}")
    if n_scanned != len(NEGATIVE):
        fails.append(f"[反例扫描数] 期望 {len(NEGATIVE)}，实测 {n_scanned}")
    if len(n_problems) != len(NEGATIVE):
        fails.append("[反例漏报] 期望 %d 条红，实测 %d：%s"
                     % (len(NEGATIVE), len(n_problems), "; ".join(x[0] for x in n_problems)))
    if n_warns:
        fails.append(f"[反例被降级成 WARN] {n_warns}")
    for lbl, ln, msg in n_problems:
        if not isinstance(ln, int) or ln < 1 or not msg:
            fails.append(f"[报错信息不完整] {lbl} {(ln, msg)}")

    if fails:
        for x in fails:
            print(f"  FAIL {x}")
        return 1
    print("  [selftest] OK —— 正例零误伤（hero 满幅 / 嵌套块 / 外层裸 div / "
          "注释里写 `{{ end }}` / 多行 action）· 反例逐条命中（注释 / action / 正文 / "
          "别的 define / 组件级宽度 五种伪容器）· 非页型模板正确跳过")
    return 0


def main() -> int:
    if "--selftest" in sys.argv:
        return selftest()

    layouts = ROOT / "layouts"
    if not layouts.is_dir():
        print(f"FAIL: 找不到 {layouts}")
        return 1
    problems, warns, scanned = run_layouts(layouts)
    print(f"check_page_container.py —— 页型模板 main 块容器判据（扫 {scanned} 个页型模板）")
    for lbl, ln, msg in problems:
        print(f"  FAIL {lbl}:{ln}  {msg}")
    for lbl, ln, msg in warns:
        print(f"  WARN {lbl}:{ln}  {msg}")
    if problems:
        print(f"FAIL: {len(problems)} 个页型模板的 main 块没有容器（另有 {len(warns)} 条 WARN）")
        return 1
    print(f"OK: {scanned} 个页型模板的 main 块都有容器（另有 {len(warns)} 条 WARN，不拦构建）")
    return 0


if __name__ == "__main__":
    sys.exit(main())
