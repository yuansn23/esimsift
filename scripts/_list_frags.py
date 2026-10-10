# -*- coding: utf-8 -*-
"""列出 layouts/ 全部「拼装句碎片」（按文件分组；llms 文件的逐条展开）。"""
import collections
import os
import sys

sys.path.insert(0, "scripts")
from i18n_extract import collect  # noqa: E402

c = collections.defaultdict(list)
for dp, dn, fn in os.walk("layouts"):
    for f in sorted(fn):
        if not f.endswith((".html", ".txt", ".json", ".xml")):
            continue
        full = os.path.join(dp, f)
        src = open(full, encoding="utf-8", newline="").read()
        rel = os.path.relpath(full, ".").replace(os.sep, "/")
        _te, _ae, fr, _ba = collect(rel, src)
        if fr:
            c[rel] = fr

tot = 0
for k, v in sorted(c.items(), key=lambda x: -len(x[1])):
    tot += len(v)
    print(f"{len(v):3}  {k}")
    if "llms" in k:
        for x in v:
            print("        ", repr(x))
print("total frags", tot, "files", len(c))
