# -*- coding: utf-8 -*-
"""一次性修正：content/de/**/*.md 正文里的 {{/* … */}} 备注会原样渲染进页面。

问题：Hugo **不解析 Markdown 正文里的模板语法**，所以写在正文里的
      `{{/* TODO(de)：… */}}` 既不会被当成注释、也不会报错，而是被 Goldmark
      当作普通段落输出 —— 读者在 /de/ 的占位页上能直接看到 "TODO(de)：正文待翻译…"。

修法：把这段注记搬进 front matter 的 YAML 注释（`#` 开头，YAML 解析器会忽略），
      正文清空或只剩正文本身。这样开发者仍看得见待办，读者看不到。

用法：
    python -X utf8 scripts/_fix_de_todo_comments.py --dry    # 先看要改什么
    python -X utf8 scripts/_fix_de_todo_comments.py          # 落盘
"""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CONTENT = ROOT / "content" / "de"

# 跨行、非贪婪的 Hugo 模板注释块
NOTE_RE = re.compile(r"\{\{/\*(.*?)\*/\}\}", re.S)
FRONT_RE = re.compile(r"\A---\r?\n(.*?)\r?\n---[ \t]*\r?\n?", re.S)


def to_yaml_comment(inner: str) -> list[str]:
    """把注释正文转成 YAML 注释行；保留每行原有的相对缩进。"""
    out: list[str] = []
    for line in inner.strip("\n").split("\n"):
        stripped = line.rstrip()
        if not stripped:
            out.append("#")
        elif stripped.lstrip().startswith("#"):
            out.append(stripped)
        else:
            out.append("# " + stripped.lstrip())
    return out


def fix_one(path: Path) -> tuple[str, int] | None:
    raw = path.read_text(encoding="utf-8")
    if "{{" not in raw:
        return None

    m = FRONT_RE.match(raw)
    if not m:
        raise SystemExit(f"{path}: 没有 YAML front matter，人工确认")
    front = m.group(1)
    body = raw[m.end():]

    notes = NOTE_RE.findall(body)
    if not notes:
        return None

    comment_lines: list[str] = []
    for n in notes:
        comment_lines.extend(to_yaml_comment(n))

    # 正文里删掉注释块，并去掉因删除产生的多余空行
    new_body = NOTE_RE.sub("", body)
    new_body = re.sub(r"\n{3,}", "\n\n", new_body).strip("\n")
    new_body = (new_body + "\n") if new_body else ""

    new_front = front.rstrip("\n") + "\n" + "\n".join(comment_lines)
    out = f"---\n{new_front}\n---\n"
    if new_body:
        out += "\n" + new_body

    if out != raw:
        path.write_text(out, encoding="utf-8", newline="\n")
        return out, len(notes)
    return None


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry", action="store_true", help="只报告，不写盘")
    args = ap.parse_args()

    files = sorted(CONTENT.rglob("*.md"))
    hit: list[Path] = []
    total_notes = 0
    for f in files:
        if "{{" not in f.read_text(encoding="utf-8"):
            continue
        hit.append(f)
        if args.dry:
            raw = f.read_text(encoding="utf-8")
            n = len(NOTE_RE.findall(raw))
            print(f"  would fix {f.relative_to(ROOT).as_posix()}  ({n} note block)")
            continue
        res = fix_one(f)
        if res:
            total_notes += res[1]

    if args.dry:
        print(f"\n共 {len(hit)} 个文件待修（dry run，未写盘）")
    else:
        print(f"已修 {len(hit)} 个文件 / {total_notes} 处注释块")

    # 自检：改完不应再有正文级 template 残留
    left = [f for f in files
            if re.search(r"\{\{", f.read_text(encoding="utf-8"))]
    if left and not args.dry:
        print(f"FAIL: 仍有 {len(left)} 个文件含 {{{{")
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
