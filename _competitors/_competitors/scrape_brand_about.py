# -*- coding: utf-8 -*-
"""Supplemental brand facts for brands whose homepage lacks JSON-LD Organization.

Fetches About/company pages and pulls factual sentences (founded / HQ / support /
network partners / pricing model). Merges into _competitors/brand/<brand>.json
under "official.about_facts". Trustpilot stays a placeholder.
"""
import json
import re
from pathlib import Path

import requests

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "_competitors" / "brand"

UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/148.0.0.0 Safari/537.36")

TARGETS = {
    "gigsky": ["https://www.gigsky.com/about-us/", "https://www.gigsky.com/about/",
               "https://www.gigsky.com/company/"],
    "maya": ["https://maya.net/about", "https://maya.net/about-us",
             "https://maya.net/company", "https://maya.net/careers"],
    "quibity": ["https://quibity.com/about", "https://quibity.com/about-us",
                "https://quibity.com/company"],
}

KEYS = re.compile(
    r"(founded|headquarter|based in|HQ\b|established|since \d{4}|network partner|"
    r"partner(?:s|ed)? with|operates? in|coverage|support@|@[\w-]+\.[a-z]{2,}|"
    r"unlimited|pay-as-you-go|no (?:\w+ )?contract)", re.I)


def visible_text(html: str) -> str:
    t = re.sub(r"<script.*?</script>|<style.*?</style>|<noscript.*?</noscript>", " ",
               html, flags=re.S)
    t = re.sub(r"<[^>]+>", " ", t)
    t = t.replace("&amp;", "&").replace("&nbsp;", " ").replace("&#39;", "'")
    return re.sub(r"\s+", " ", t)


def facts(text: str, limit: int = 25):
    out = []
    for s in re.split(r"(?<=[.!?])\s+", text):
        s = s.strip()
        if 30 < len(s) < 400 and KEYS.search(s):
            out.append(s)
        if len(out) >= limit:
            break
    return out


def main():
    s = requests.Session()
    s.headers.update({"User-Agent": UA, "Accept-Language": "en-US,en;q=0.9"})
    for key, urls in TARGETS.items():
        f = OUT / f"{key}.json"
        rec = json.loads(f.read_text(encoding="utf-8"))
        rec.setdefault("official", {})
        about = []
        for u in urls:
            try:
                r = s.get(u, timeout=30)
            except Exception as e:
                print(f"{key:8s} {u} ERR {str(e)[:60]}", flush=True)
                continue
            if r.status_code != 200 or len(r.text) < 5000:
                continue
            txt = visible_text(r.text)
            about.append({"url": u, "bytes": len(r.text),
                          "title": (re.search(r"<title[^>]*>(.*?)</title>", r.text, re.S) or [None, None])[1],
                          "facts": facts(txt),
                          "emails": sorted(set(re.findall(r"[\w.+-]+@[\w-]+\.[\w.]{2,10}", r.text)))[:8]})
            print(f"{key:8s} {u} OK {len(r.text)} facts={len(about[-1]['facts'])}", flush=True)
            if len(about[-1]["facts"]) >= 5:
                break
        rec["official"]["about_facts"] = about
        f.write_text(json.dumps(rec, indent=1, ensure_ascii=False), encoding="utf-8")


if __name__ == "__main__":
    main()
