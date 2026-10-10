#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""把一批「新 key」追加进 i18n/*.toml。

为什么需要它：`i18n_extract.py` 只抽「纯静态文本节点」，而本次德语上线的主战场是
**拼装句碎片**（紧邻 `{{ }}` 的英文）与 `printf` 格式串 —— 那些必须人工处理。
人工处理时若直接 `>> i18n/en.toml` 追加，容易漏掉 de、或两边顺序不一致。
本脚本保证 en / de **按同一顺序**追加同一批 key，并顺手校验。

⚠️ **为什么是「追加到末尾」而不是「插入到排序位置」**（2026-10-09 实测）：
`i18n/en.toml` 与 `de.toml` 现有 1173 个 key **并不是全局排序的** —— 历史上分批
追加过（`compare_list__*` 那一块就乱序）。若按排序重写整份文件，会产生一份
上千行的巨型 diff，把本轮真正的改动淹没。追加只新增行，diff 干净。

输入：一个 JSON 文件，形如
    {"compare_single__hero_h1": {"en": "Best eSIM for {{ .country }} in {{ .year }}",
                                 "de": "Beste eSIM für {{ .country }} im Jahr {{ .year }}"}}
（de 缺失或为 null → 以 en 值占位，等价于「未译」，check_i18n.py 仍视为 key 对齐。）

用法：
    python -X utf8 scripts/i18n_add.py path/to/batch.json            # 干跑，只报告
    python -X utf8 scripts/i18n_add.py path/to/batch.json --apply    # 真正写入
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
I18N = ROOT / "i18n"

LINE_RE = re.compile(r"^([A-Za-z0-9_]+)\s*=\s*(.*)$")


def load(path: Path) -> tuple[list[str], dict[str, str], dict[str, int]]:
    """返回 (原始行, key->value 文本, key->所在行号)。"""
    if not path.exists():
        return [], {}, {}
    lines = path.read_bytes().decode("utf-8").split("\n")
    kv: dict[str, str] = {}
    at: dict[str, int] = {}
    for i, ln in enumerate(lines):
        s = ln.strip()
        if not s or s.startswith("#"):
            continue
        m = LINE_RE.match(s)
        if not m:
            continue
        k, v = m.group(1), m.group(2)
        if k in kv:
            raise SystemExit(f"!! {path.name}: key 重复 -> {k}")
        kv[k] = v
        at[k] = i
    return lines, kv, at


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("batch")
    ap.add_argument("--apply", action="store_true")
    args = ap.parse_args()

    batch = json.loads(Path(args.batch).read_text(encoding="utf-8"))
    if not isinstance(batch, dict) or not batch:
        raise SystemExit("!! batch JSON 必须是非空对象 {key: {en, de}}")

    for f in sorted(I18N.glob("*.toml")):
        lang = f.stem  # en / de
        lines, kv, at = load(f)

        vals: dict[str, str] = {}
        for k in batch:                       # 保持 batch 书写顺序 → en/de 同步
            v = batch[k].get(lang)
            if lang != "en" and v is None:
                v = batch[k].get("en")        # 未译 → 英文占位
            if v is None:
                raise SystemExit(f"!! {k} 缺 en 值")
            vals[k] = json.dumps(v, ensure_ascii=False)

        added, updated = [], []
        for k, js in vals.items():
            if k not in kv:
                added.append(k)
            elif kv[k] != js:
                updated.append(k)
                lines[at[k]] = f"{k} = {js}"

        # 收敛尾部空行，保持文件以单个换行结尾
        while len(lines) > 1 and lines[-1] == "" and lines[-2] == "":
            lines.pop()
        if lines and lines[-1] != "":
            lines.append("")
        for k in added:
            lines.append(f"{k} = {vals[k]}")
        if lines[-1] != "":
            lines.append("")

        data = "\n".join(lines).encode("utf-8")
        assert b"\r\n" not in data, "!! 写出了 CRLF"

        print(f"{f.name}: +{len(added)} 追加 / ~{len(updated)} 原地更新 / 共 {len(kv) + len(added)} key")
        if args.apply:
            f.write_bytes(data)
            back = f.read_bytes()
            assert back == data, f"!! {f.name} 写回校验失败"
            assert back.count(b"\r\n") == 0, f"!! {f.name} 出现 CRLF"

    if not args.apply:
        print("\n（干跑。确认后加 --apply 写入）")
    return 0


if __name__ == "__main__":
    sys.exit(main())
