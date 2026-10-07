# -*- coding: utf-8 -*-
"""Inspect bnesim pricing API JSON structure."""
import json
from pathlib import Path

P = Path(__file__).resolve().parent
OUT = Path(r"C:\Users\27197\WorkBuddy\2026-10-04-19-19-25\_probe_result.txt")


def log(*a):
    OUT.open("a", encoding="utf-8").write(" ".join(str(x) for x in a) + "\n")


data = json.loads((P / "bnesim_pricing_api.json").read_text(encoding="utf-8"))


def shape(node, depth=0, name="$"):
    pad = "  " * depth
    if depth > 4:
        return
    if isinstance(node, dict):
        log(f"{pad}{name}: dict keys={list(node.keys())[:14]}")
        for k, v in list(node.items())[:3]:
            shape(v, depth + 1, str(k))
    elif isinstance(node, list):
        log(f"{pad}{name}: list len={len(node)}")
        if node:
            shape(node[0], depth + 1, "[0]")
    else:
        s = str(node)
        log(f"{pad}{name}: {type(node).__name__} = {s[:80]}")


shape(data)
