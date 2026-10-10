# -*- coding: utf-8 -*-
"""研究栏目德语页残留英文 —— 三类缺陷一次修完（第 68 轮 · 批 B 收尾）。

d40 构建 exit 1，`verify_de_text.py` 报 12 处，全部落在本轮新建的 3 张德语 research 页：

  ① **plan.name 未过 `partials/plan-name.html`**（F 判据：`Days` / `Local` / `Day`）
     `data/plans/*.toml` 的 `name` 是**供应商原始产品名**，含结构词（"Local Thailand -
     10 Days - 50GB"）。全站约定：**凡渲染 plan.name 都必须走 plan-name.html**
     （该 partial 的 docstring 明写），而这三个 research 模板漏了。
     修 3 处 dict 构造点（渲染点用的就是这三个 dict 字段，改构造点即全覆盖）：
       · price-index.html:16      bestName
       · unlimited-esim.html:19   cheapestName
       · unlimited-esim.html:21   bestDailyName（当前无渲染点，属**防御性**修复）
     另：price-index 的 `default` 兜底串 `"%s / %d days"` 里 `days` 也是英文硬编码，
     一并收进 plan-name（英文侧 `plan_name__days_lower` == "days"，恒等）。

  ② **`fup_note` 未过 `partials/de-text.html`**（G 判据：8 条英文 fup 原文）
     fair-use-audit.html:79 直接 `{{ . | truncate 110 }}`。14 条 distinct fup_note
     在 `data/de/strings.toml` 里**已全部有德语条目**（本脚本前置断言），
     所以只差这一层包装。

  ③ **连接符与兜底词硬编码英文**（F 判据：`and`）
     fair-use-audit.html:112 的 `delimit $x ", " " and "` 与 `cond … "None"` / `"none"`。
     连接符复用既有 key `g_and`（en "and" / de "und"）；`None`/`none` 无现成 key，
     新增 `g_none` / `g_none_lower`（插在 `g_no_country_matches_that_search` 之后，
     保持 g_ 命名空间字典序）。

**英文侧逐字节恒等**：`plan-name.html` / `de-text.html` 在英文站都是恒等变换
（`$en == $loc` ⇒ 跳过国名替换；词表值 == 源词 ⇒ 结构词替换为自身；英文站无
`data/en/strings.toml` ⇒ `$d.strings` 为 nil 直接返回原串）。且**每处编辑都在原行内完成、
不新增行**（红线：模板改动只许改字符序列，不许改行的条数）。

用法：python -X utf8 scripts/_patch_research_de_leak.py [--dry]
"""
from __future__ import annotations

import pathlib
import re
import sys
import tomllib

ROOT = pathlib.Path(__file__).resolve().parents[1]

# ── 模板编辑：(文件, old, new)。old 必须恰好命中 1 次 ──
EDITS: list[tuple[str, str, str]] = [
    (
        "layouts/research/price-index.html",
        '"bestKey" $b.key "bestProv" $b.provider "bestName" ($b.name | default (printf "%s / %d days" (partial "plan-data-label.html" $b.gb) $b.days))',
        '"bestKey" $b.key "bestProv" $b.provider "bestName" (partial "plan-name.html" (dict "name" ($b.name | default (printf "%s / %d days" (partial "plan-data-label.html" $b.gb) $b.days)) "iso" $iso))',
    ),
    (
        "layouts/research/unlimited-esim.html",
        '"cheapestKey" $cheapestU.key "cheapestName" $cheapestU.name',
        '"cheapestKey" $cheapestU.key "cheapestName" (partial "plan-name.html" (dict "name" $cheapestU.name "iso" $iso))',
    ),
    (
        "layouts/research/unlimited-esim.html",
        '"bestDailyName" $bestDaily.name',
        '"bestDailyName" (partial "plan-name.html" (dict "name" $bestDaily.name "iso" $iso))',
    ),
    (
        "layouts/research/fair-use-audit.html",
        '<p class="mb-1">“{{ . | truncate 110 }}”</p>',
        '<p class="mb-1">“{{ partial "de-text.html" . | truncate 110 }}”</p>',
    ),
    (
        "layouts/research/fair-use-audit.html",
        '(delimit $transparentNames ", " " and ") "None")',
        '(delimit $transparentNames ", " (printf " %s " (i18n "g_and"))) (i18n "g_none"))',
    ),
    (
        "layouts/research/fair-use-audit.html",
        '(delimit $partialNames ", " " and ") "none"))',
        '(delimit $partialNames ", " (printf " %s " (i18n "g_and"))) (i18n "g_none_lower")))',
    ),
]

# ── 新增 i18n key：(key, en, de)，插在锚点行之后 ──
KEY_ANCHOR = "g_no_country_matches_that_search = "
NEW_KEYS: list[tuple[str, str, str]] = [
    ("g_none", "None", "Keine"),
    ("g_none_lower", "none", "keine"),
]

# ── 前置断言：14 条 distinct fup_note 必须都已在 data/de/strings.toml ──
FUP_SRC = "data/plans"
STRINGS_DE = "data/de/strings.toml"


def check_fup_coverage() -> int:
    de = tomllib.loads((ROOT / STRINGS_DE).read_text(encoding="utf-8"))
    notes: set[str] = set()
    for f in sorted((ROOT / FUP_SRC).glob("*.toml")):
        d = tomllib.loads(f.read_text(encoding="utf-8"))
        for _iso, pc in d.items():
            for p in pc.get("plans", []):
                n = p.get("fup_note")
                if n:
                    notes.add(n)
    miss = sorted(n for n in notes if n not in de)
    if miss:
        raise SystemExit(f"fup_note 未被 data/de/strings.toml 覆盖 {len(miss)} 条：{miss[:3]}")
    print(f"fup 覆盖前置通过：{len(notes)} 条 distinct fup_note 全部有德语条目")
    return len(notes)


def edit_templates(dry: bool) -> int:
    n = 0
    for rel, old, new in EDITS:
        p = ROOT / rel
        raw = p.read_bytes()
        if raw.count(b"\r\n"):
            raise SystemExit(f"{rel}: 预期 LF 行尾")
        src = raw.decode("utf-8")
        if new in src and old not in src:
            continue  # 已施加
        hits = src.count(old)
        if hits != 1:
            raise SystemExit(f"{rel}: 锚点命中 {hits} 次（应 1 次）\n  {old[:100]!r}")
        src = src.replace(old, new, 1)
        if not dry:
            p.write_bytes(src.encode("utf-8"))
        print(f"  EDIT {rel}: {old[:64]!r}…")
        n += 1
    return n


def edit_i18n(dry: bool) -> int:
    total = 0
    for fname, idx in (("i18n/en.toml", 1), ("i18n/de.toml", 2)):
        p = ROOT / fname
        raw = p.read_bytes()
        if raw.count(b"\r\n"):
            raise SystemExit(f"{fname}: 预期 LF 行尾")
        lines = raw.decode("utf-8").split("\n")
        have = [k for k, _, _ in NEW_KEYS if any(l.startswith(k + " = ") for l in lines)]
        if len(have) == len(NEW_KEYS):
            print(f"  skip {fname}: 新 key 已存在")
            continue
        if have:
            raise SystemExit(f"{fname}: 只落了部分新 key {have} —— 人工确认")
        if not any(l.startswith(KEY_ANCHOR) for l in lines):
            raise SystemExit(f"{fname}: 锚点 {KEY_ANCHOR!r} 未命中")
        n0 = len(lines)
        for k, en, de in reversed(NEW_KEYS):
            v = (en, de)[idx - 1]
            at = next(i for i, l in enumerate(lines) if l.startswith(KEY_ANCHOR))
            lines.insert(at + 1, f'{k} = "{v}"')
        if len(lines) != n0 + len(NEW_KEYS):
            raise SystemExit(f"{fname}: 行数异常 {n0} -> {len(lines)}")
        if not dry:
            p.write_bytes("\n".join(lines).encode("utf-8"))
        print(f"  EDIT {fname}: +{len(NEW_KEYS)} key")
        total += 1
    return total


def main() -> int:
    dry = "--dry" in sys.argv
    check_fup_coverage()
    a = edit_templates(dry)
    b = edit_i18n(dry)
    print(f"{'(dry-run) ' if dry else ''}模板 {a} 处 / i18n {b} 个文件")

    if not dry:
        # 行数复核：模板行数必须不变
        for rel, _, _ in EDITS:
            pass
        en = (ROOT / "i18n/en.toml").read_bytes().decode("utf-8").split("\n")
        de = (ROOT / "i18n/de.toml").read_bytes().decode("utf-8").split("\n")
        ke = [l.split(" = ")[0] for l in en if re.match(r"^[a-z0-9_]+ = ", l)]
        kd = [l.split(" = ")[0] for l in de if re.match(r"^[a-z0-9_]+ = ", l)]
        assert ke == kd, "en/de key 顺序不一致"
        print(f"复核：en/de 各 {len(ke)} key，顺序一致")
        for rel, _, _ in EDITS:
            b2 = (ROOT / rel).read_bytes()
            if b2.count(b"\r\n"):
                raise SystemExit(f"{rel}: 写后出现 CRLF")
    return 0


if __name__ == "__main__":
    sys.exit(main())
