"""一次性内链体检：扫 public/ 所有 html，找出指向不存在目标的站内链接。
用法：python -X utf8 scripts/_link_audit.py [关键词过滤]
"""
from __future__ import annotations

import re
import sys
from collections import defaultdict
from pathlib import Path
from urllib.parse import unquote

ROOT = Path(__file__).resolve().parents[1]
PUBLIC = ROOT / "public"

HREF_RE = re.compile(r'href="([^"]+)"')
SKIP_PREFIX = ("http://", "https://", "//", "mailto:", "tel:", "#", "javascript:", "data:")


def target_exists(pub_path: str) -> bool:
    p = pub_path.strip()
    if not p.startswith("/"):
        return True  # 相对链接不参与本次判定
    p = unquote(p.split("#")[0].split("?")[0])
    rel = p.lstrip("/")
    cands = []
    if p.endswith("/"):
        cands.append(PUBLIC / rel / "index.html")
    else:
        cands.append(PUBLIC / rel)
        cands.append(PUBLIC / (rel + ".html"))
        cands.append(PUBLIC / rel / "index.html")
    return any(c.is_file() for c in cands)


def main() -> int:
    kw = sys.argv[1] if len(sys.argv) > 1 else None
    broken: dict[str, set[str]] = defaultdict(set)
    total = 0
    for f in sorted(PUBLIC.rglob("*.html")):
        if ".hugo_build" in f.name:
            continue
        src = f.read_text(encoding="utf-8", errors="ignore")
        for m in HREF_RE.finditer(src):
            href = m.group(1)
            total += 1
            if href.startswith(SKIP_PREFIX):
                continue
            if not target_exists(href):
                broken[href.split("#")[0].split("?")[0]].add(
                    str(f.relative_to(PUBLIC)).replace("\\", "/")
                )
    if kw:
        broken = {k: v for k, v in broken.items() if kw in k}
    print(f"扫描 href {total} 条；坏链目标 {len(broken)} 个")
    for href, refs in sorted(broken.items(), key=lambda kv: -len(kv[1])):
        rl = sorted(refs)
        print(f"\n  ✗ {href}   （被 {len(rl)} 个页面引用）")
        for r in rl[:8]:
            print(f"      ← {r}")
        if len(rl) > 8:
            print(f"      ... 还有 {len(rl) - 8} 个")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
