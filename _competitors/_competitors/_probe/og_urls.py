# -*- coding: utf-8 -*-
import re
from pathlib import Path

p = Path(r"D:\HUGO test\29.1_windows-amd64\hugo_0.159.1_windows-amd64\esimsift-main\esimsift-main\_competitors\_probe")
out = Path(r"C:\Users\27197\WorkBuddy\2026-10-04-19-19-25\_parse_out.txt")
for f in ["gigsky_home.html", "quibity_home.html", "jetpac_home.html", "maya_home.html"]:
    h = (p / f).read_text(encoding="utf-8", errors="replace")
    og = re.search(r'property="og:url" content="([^">]+)"', h) or re.search(r"property='og:url' content='([^'>]+)'", h)
    can = re.search(r'rel="canonical" href="([^">]+)"', h) or re.search(r"rel='canonical' href='([^'>]+)'", h)
    out.open("a", encoding="utf-8").write(
        f + " | og:url=" + (og.group(1) if og else "?") + " | canonical=" + (can.group(1) if can else "?") + "\n")
