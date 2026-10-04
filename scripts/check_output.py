# -*- coding: utf-8 -*-
"""Post-build output guard: inspect every page Hugo emitted in `public/`.

Why this exists (2026-10-03 incident):
  Search Console reported "评分超出了指定范围或默认范围（在 reviewRating 中）" on
  /esim-providers/holafly/. Two defects stacked:
    a) `"bestRating" "10"` was emitted as a STRING (and worstRating was absent),
       so Google fell back to its default 1-5 scale;
    b) the rating itself was an editorial price index scoring 0.0-8.4, and seven
       of eight brands scored below 1 -> out of range -> the whole Rating node was
       invalid and ineligible for rich results.
  The same release also shipped three Go format-string bugs that were VISIBLE body
  text: `%!d(float64=84)%`, `%!m(MISSING)argin`, `%!(EXTRA string=Airalo, ...)`.

  None of these are caught by `hugo` (it renders happily), by validate.py (data
  layer only) or by check_css_sync.py (CSS only). They only exist in the OUTPUT,
  so the guard has to read the output.

Checks
  1. no Go fmt error residue (`%!x(...)`) anywhere in public/**/*.html + *.json
  2. every <script type="application/ld+json"> block parses as JSON
  3. every Review/reviewRating and AggregateRating is in range:
     ratingValue must be a JSON number and satisfy
     worstRating <= ratingValue <= bestRating, with numeric scales
     (defaults 1 and 5 when omitted, per Google's documentation)
  4. no unrendered template residue (`{{` / `<no value>`) in public/**/*.html
     and *.json — outside <style>/<script> blocks

为什么第 4 条要单列（2026-10-04 实际发生）：
  content/de/ 下 54 个占位页把开发者备注写成 `{{/* TODO(de)：… */}}` 放在
  **Markdown 正文**里。Hugo 只解析模板文件，不解析正文，于是这段文字被 Goldmark
  当成普通段落，读者在 /de/ 的 50 个国家页上能直接看到 "TODO(de)：正文待翻译…"。
  `hugo` 退出码 0，五重校验当时全绿 —— 它只在**产物**里看得见。

  只扫 `{{` 不扫 `}}`：压缩后的 Tailwind CSS 内联在 <style> 里，`}}` 每天都会
  出现（390 个文件命中），扫它就是自造假阳性。屏蔽 <style>/<script> 之后
  再扫，剩下的 `{{` 才是真残留。

历史：曾有一条「全站禁止非拉丁字符」的检查（2026-10-03 加，用于抓爬虫带进来的
本地文字，例如 Airalo 的韩文 "짱 Jjang" 混进了 /compare/south-korea/）。
2026-10-03 按站点决策**移除** —— 站点要做多语言，这条禁令会拦住 ja/ko/zh 的
合法产物，而按语言划豁免前缀只是把同一个问题往后推。数据入口的清洗改由
scraper 侧负责（见 scripts/scrape/ 与 toml_write.clean_plan_name）。

Exit code 1 on any failure. Run AFTER `hugo`:
    python -X utf8 scripts/check_output.py
    python -X utf8 scripts/check_output.py --selftest   # 对构造样本自测
"""
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PUBLIC = ROOT / "public"

FMT_ERROR = re.compile(r"%![A-Za-z]*(?:\([^)]*\))?")
LDJSON = re.compile(r'<script type="application/ld\+json">(.*?)</script>', re.S)
# 模板残留：只看 Go 模板的**开**定界符；`}}` 在压缩 CSS 里是常态，扫不得
TEMPLATE_OPEN = re.compile(r"\{\{")
NO_VALUE = re.compile(r"<no value>")
# 屏蔽行内样式 / 脚本块（含 JSON-LD 自身），避免 CSS/JS 里的花括号造假阳性
STYLE_SCRIPT = re.compile(r"<(style|script)\b[^>]*>.*?</\1>", re.S | re.I)

# 允许例外（默认空）：相对 public 的路径 -> 理由。给「指南里贴 Hugo 模板示例」这类
# 合法场景留一道口子，但必须写明理由，避免变成静默豁免。
TEMPLATE_ALLOW: dict[str, str] = {}

errors: list[str] = []


def walk(obj):
    """Yield every dict inside a JSON-LD tree (nodes are nested in @graph)."""
    if isinstance(obj, dict):
        yield obj
        for v in obj.values():
            yield from walk(v)
    elif isinstance(obj, list):
        for v in obj:
            yield from walk(v)


def check_rating(node: dict, where: str, handled: set) -> None:
    """Validate ratings whether they hang off a property or stand alone.

    Two shapes exist in the wild:
      {"@type":"Review",  "reviewRating": {...}}     <- nested
      {"@type":"AggregateRating", "ratingValue": 4}  <- standalone node
    `handled` holds the id() of nested rating objects already validated, so the
    standalone branch does not report the same defect a second time when walk()
    descends into them.
    """
    candidates: list[tuple[str, object]] = [
        (k, node.get(k)) for k in ("reviewRating", "aggregateRating")
    ]
    for _, rating in candidates:
        if isinstance(rating, dict):
            handled.add(id(rating))

    types = node.get("@type")
    types = types if isinstance(types, list) else [types]
    if any(t in ("Rating", "AggregateRating") for t in types) and id(node) not in handled:
        candidates.append((str(node.get("@type")), node))

    for name, rating in candidates:
        if not isinstance(rating, dict):
            continue
        value = rating.get("ratingValue")
        if value is None:
            errors.append(f"{where}: {name} has no ratingValue")
            continue
        if not isinstance(value, (int, float)) or isinstance(value, bool):
            errors.append(
                f"{where}: {name}.ratingValue is {value!r} "
                f"(must be a JSON number, not a string)"
            )
            continue

        def scale(prop: str, default: float) -> float:
            v = rating.get(prop, default)
            if not isinstance(v, (int, float)) or isinstance(v, bool):
                errors.append(
                    f"{where}: {name}.{prop} is {v!r} "
                    f"(must be a JSON number, not a string)"
                )
                return default
            return float(v)

        low, high = scale("worstRating", 1), scale("bestRating", 5)
        if high <= low:
            errors.append(f"{where}: {name}.bestRating {high} <= worstRating {low}")
        if not (low <= value <= high):
            errors.append(
                f"{where}: {name}.ratingValue {value} outside [{low:g}, {high:g}] "
                f"(Google: 评分超出了指定范围)"
            )


def scan_text(text: str, rel: str, is_html: bool) -> list[str]:
    """文本级检查（第 1、4 条）。抽出来是为了能对**构造样本**自测 ——
    一个「bad = 0」只有在证明过它会报错之后才有意义。"""
    out: list[str] = []

    for m in FMT_ERROR.finditer(text):
        line = text.count("\n", 0, m.start()) + 1
        ctx = text[max(0, m.start() - 45):m.end() + 25].replace("\n", " ")
        out.append(f"{rel}:{line}: Go format-string leak -> {ctx.strip()!r}")

    # 4. 未渲染的模板残留
    if rel not in TEMPLATE_ALLOW:
        visible = text if not is_html else STYLE_SCRIPT.sub(" ", text)
        for m in TEMPLATE_OPEN.finditer(visible):
            line = text.count("\n", 0, m.start()) + 1
            ctx = visible[max(0, m.start() - 45):m.end() + 60].replace("\n", " ")
            out.append(
                f"{rel}:{line}: unrendered template residue -> {ctx.strip()!r}")
        for m in NO_VALUE.finditer(visible):
            line = text.count("\n", 0, m.start()) + 1
            ctx = visible[max(0, m.start() - 45):m.end() + 25].replace("\n", " ")
            out.append(
                f"{rel}:{line}: unrendered template residue -> {ctx.strip()!r}")
    return out


def selftest() -> int:
    cases = [
        ("body {{ leak", "<p>{{/* TODO */}}</p>", True, 1, "{{"),
        ("minified CSS }}", "<style>.a{x:1}.b{y:2}}</style>", True, 0, "}}"),
        ("<no value>", "<p>Hi <no value></p>", True, 1, "<no value>"),
        ("fmt leak", "<p>%!d(float64=84)%</p>", True, 1, "%!d"),
        ("json clean", '{"a": 1}', False, 0, ""),
        ("json tmpl leak", '{"a": "{{ .x }}"}', False, 1, "{{"),
    ]
    failed = 0
    for name, body, is_html, want, needle in cases:
        got = scan_text(body, "fixture.html", is_html)
        # want == 0 时没有东西可查 needle（那正是"不该误报"的情形）
        ok = len(got) == want and (want == 0 or any(needle in g for g in got))
        failed += 0 if ok else 1
        print(f"  {'OK  ' if ok else 'MISS'} {name:20s} 期望 {want} 处 "
              f"（{needle or '无'}）实际 {len(got)} 处")
    print(f"\n自测{'通过' if not failed else f'失败 {failed} 项'}")
    return 1 if failed else 0


def main() -> int:
    if "--selftest" in sys.argv[1:]:
        return selftest()

    if not PUBLIC.is_dir():
        print("ERROR public/ not found - run `hugo` first")
        return 1

    pages = sorted(PUBLIC.rglob("*.html"))
    json_files = sorted(PUBLIC.rglob("*.json"))
    ld_blocks = 0
    scanned = 0

    # .html -> format leak + JSON-LD + ratings; emitted .json (catalog.json et al)
    # -> format leak only (same Go template engine emits it, so it can leak there too)
    targets = [(f, True) for f in pages] + [(f, False) for f in json_files]

    for f, is_html in targets:
        rel = f.relative_to(ROOT).as_posix()
        try:
            text = f.read_text(encoding="utf-8", errors="replace")
        except OSError:
            continue
        scanned += 1

        errors.extend(scan_text(text, rel, is_html))

        if not is_html:
            continue

        for m in LDJSON.finditer(text):
            ld_blocks += 1
            try:
                data = json.loads(m.group(1))
            except ValueError as e:
                errors.append(f"{rel}: invalid JSON-LD - {e}")
                continue
            handled: set = set()
            for node in walk(data):
                check_rating(node, rel, handled)

    if errors:
        print(f"ERROR output guard: {len(errors)} problem(s) in public/")
        for e in errors[:40]:
            print(f"  {e}")
        if len(errors) > 40:
            print(f"  ... and {len(errors) - 40} more")
        return 1

    print(f"OK: {scanned} files ({len(pages)} pages), {ld_blocks} JSON-LD blocks "
          f"- no format leaks, no template residue, all ratings in range")
    return 0


if __name__ == "__main__":
    sys.exit(main())
