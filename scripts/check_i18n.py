# -*- coding: utf-8 -*-
"""多语言守卫 —— 防止模板层重新出现硬编码文案，并检查各语言 key 完整性。

为什么需要它：模板文案一旦硬编码，新增语言时就会被漏掉，页面混语言。
改造前全站零 i18n 基础设施，`layouts/` 里有 2462 处英文文案；现已抽出的部分
必须锁住，不能再退回去。

检查项
  1. [ERROR]  layouts/ 中还有「纯静态英文文本节点 / 可翻译属性值」没走 i18n
  2. [ERROR]  i18n/<lang>.toml 与 i18n/en.toml 的 key 不对齐（漏译或多余 key）
  3. [WARN]   紧跟 {{ }} 的「拼装句碎片」—— 数量已知，需人工重写成带占位符的整句
  4. [WARN]   模板内联 <script> 里的用户可见英文（JS 上下文不能用 i18n，须改 data-* 注入）

用法：python -X utf8 scripts/check_i18n.py [--strict]
  --strict 把 WARN 也当作失败（CI 里想彻底锁死时用）
"""
from __future__ import annotations

import json
import os
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(Path(__file__).resolve().parent))

from i18n_extract import collect, filetag  # noqa: E402  (复用同一个扫描器，避免两套口径)

LAYOUTS = ROOT / "layouts"
I18N_DIR = ROOT / "i18n"

errors: list[str] = []
warns: list[str] = []


def scan_layouts():
    hardcoded: list[str] = []
    frags: list[tuple[str, str]] = []
    scripts: list[tuple[str, str]] = []

    for dp, dn, fn in os.walk(LAYOUTS):
        for f in sorted(fn):
            if not re.search(r"\.(html|txt|json|xml)$", f):
                continue
            full = Path(dp) / f
            rel = full.relative_to(ROOT).as_posix()
            with open(full, encoding="utf-8", newline="") as fh:
                src = fh.read()
            if "$d := partialCached \"i18n-data.html\"" not in src and "hugo.Data" not in src:
                pass
            _te, _ae, fr, _ba = collect(rel, src)
            for _s, _e, v in _te:
                hardcoded.append(f"{rel}: text {v[:60]!r}")
            for _s, _e, v in _ae:
                hardcoded.append(f"{rel}: attr {v[:60]!r}")
            for v in fr:
                frags.append((rel, v))

            # 内联 script 里的可疑英文（只抓含空格的句子，避免误报变量名）
            for m in re.finditer(r"<script(?![^>]*type=\"application/ld\+json\")[^>]*>(.*?)</script>", src, re.S | re.I):
                body = m.group(1)
                for sm in re.finditer(r"""["'`]([A-Z][A-Za-z][^"'`\n]{12,})["'`]""", body):
                    scripts.append((rel, sm.group(1)))
    return hardcoded, frags, scripts


def check_keys():
    en = I18N_DIR / "en.toml"
    if not en.exists():
        errors.append("i18n/en.toml 不存在 —— 模板已引用 i18n 但 key 表缺失")
        return {}

    def load(p: Path) -> dict:
        out = {}
        for line in p.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if not line or line.startswith("#") or " = " not in line:
                continue
            k, v = line.split(" = ", 1)
            try:
                out[k.strip()] = json.loads(v.strip())
            except json.JSONDecodeError:
                errors.append(f"{p.name}: 无法解析的 TOML 值 -> {line[:80]}")
        return out

    base = load(en)
    for p in sorted(I18N_DIR.glob("*.toml")):
        if p.name == "en.toml":
            continue
        cur = load(p)
        missing = sorted(set(base) - set(cur))
        extra = sorted(set(cur) - set(base))
        if missing:
            errors.append(
                f"i18n/{p.name}: 缺 {len(missing)} 个 key（相对 en.toml），"
                f"前几个 -> {', '.join(missing[:5])}"
            )
        if extra:
            warns.append(
                f"i18n/{p.name}: 多出 {len(extra)} 个 key（en.toml 没有），"
                f"前几个 -> {', '.join(extra[:5])}"
            )
    print(f"  i18n: en.toml {len(base)} key" + (
        f"，另有 {len(list(I18N_DIR.glob('*.toml'))) - 1} 个语言文件" if len(list(I18N_DIR.glob("*.toml"))) > 1 else "（当前仅英文）"
    ))
    return base


# 模板里字面量写出的 i18n key（动态 key 如 i18n (index $m $k) 无法静态检查，跳过）
I18N_CALL = re.compile(r"""\bi18n\s+(["'])([A-Za-z0-9_]+)\1""")


def check_used_keys(base: dict) -> None:
    """每个模板里写死的 i18n key 都必须在 i18n/en.toml 里存在。

    为什么单列一条：Hugo 对**缺失的 key 静默返回空字符串** —— 不报错、不警告，
    页面直接少一整段文案（整个 <h2> 会渲染成空标签），而 check_keys() 只比对
    语言之间是否对齐，两边一起漏就查不出来。
    2026-10-04 实际踩到：compare_provider__fup_h2 与 __host_network_h2 漏定义，
    两个 <h2></h2> 空着上线，五重校验全绿。这条检查就是为了让同类问题当场失败。
    """
    used: dict[str, str] = {}
    for dp, dn, fn in os.walk(LAYOUTS):
        for f in sorted(fn):
            if not re.search(r"\.(html|txt|json|xml)$", f):
                continue
            full = Path(dp) / f
            rel = full.relative_to(ROOT).as_posix()
            src = full.read_text(encoding="utf-8", errors="replace")
            for m in I18N_CALL.finditer(src):
                used.setdefault(m.group(2), rel)
    missing = {k: v for k, v in used.items() if k not in base}
    print(f"  i18n 引用检查：模板引用 {len(used)} 个 key，未定义 {len(missing)} 个")
    for k, rel in sorted(missing.items()):
        errors.append(f"i18n key 未定义（Hugo 会静默渲染成空串）-> {k}  （首次出现于 {rel}）")


def main() -> int:
    strict = "--strict" in sys.argv

    hardcoded, frags, scripts = scan_layouts()

    for h in hardcoded[:25]:
        errors.append("硬编码文案未抽 i18n -> " + h)
    if len(hardcoded) > 25:
        errors.append(f"... 另有 {len(hardcoded) - 25} 处硬编码文案")

    print(f"  layouts: {len(hardcoded)} 处硬编码文案 / {len(frags)} 处拼装句碎片 / {len(scripts)} 处内联脚本文案")
    base = check_keys()
    if base:
        check_used_keys(base)

    if frags:
        warns.append(f"{len(frags)} 处拼装句碎片待人工重写为带占位符的整句（例：{frags[0][0]} -> {frags[0][1][:50]!r}）")
    if scripts:
        warns.append(f"{len(scripts)} 处内联 <script> 用户文案需改为 data-* 注入（例：{scripts[0][0]} -> {scripts[0][1][:50]!r}）")

    for w in warns:
        print(f"  WARN  {w}")
    for e in errors:
        print(f"  ERROR {e}")

    if errors or (strict and warns):
        print(f"\nFAIL: {len(errors)} error(s), {len(warns)} warning(s)")
        return 1
    print(f"\nOK: 模板层无新增硬编码，i18n key 对齐（{len(warns)} 项已知待办）")
    return 0


if __name__ == "__main__":
    sys.exit(main())
