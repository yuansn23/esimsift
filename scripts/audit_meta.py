# -*- coding: utf-8 -*-
"""Meta title/description audit over rendered public/ HTML.
Usage: python -X utf8 scripts/audit_meta.py [--limit N]
Rules (2026-10-02 user spec v3): title 48-54 chars with NO brand word
(only home may carry "eSIM Sift"); description 120-140 chars that MUST contain
"eSIM Sift"; duplicates; 404 exempt from all checks.
Read-only; run after npm run build.
"""
import io, os, re, sys, html, statistics, collections

ROOT = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "public")
TITLE_RE = re.compile(r"<title>(.*?)</title>", re.S)
DESC_RE = re.compile(r'<meta\s+name="description"\s+content="(.*?)"', re.S)
TITLE_MIN, TITLE_MAX = 48, 54   # user-spec target band (Google truncates ~580px)
DESC_MIN, DESC_MAX = 120, 140
BRAND = "eSIM Sift"

def classify(rel):
    parts = rel.replace("\\", "/").split("/")
    if rel in ("index.html",):
        return "home"
    if parts[0] == "compare":
        if len(parts) == 3:  # compare/<x>/index.html  (country | matchups | vs)
            slug = parts[1]
            if slug == "matchups": return "matchups-hub"
            if "-vs-" in slug: return "vs"
            return "country"
        if len(parts) == 4: return "provider-sub"
    if parts[0] == "esim-providers": return "provider"
    if parts[0] == "guides": return "guides"
    if parts[0] == "research": return "research"
    if parts[0] in ("tools", "esim-deals"): return parts[0]
    if rel == "404.html": return "static-404"
    return "static"

stats = collections.defaultdict(lambda: {"titles": [], "descs": [], "pages": 0})
dup_title = collections.defaultdict(list)
dup_desc = collections.defaultdict(list)
offenders = []

n = 0
for dirpath, _dirs, files in os.walk(ROOT):
    for f in files:
        if not f.endswith(".html"): continue
        full = os.path.join(dirpath, f)
        rel = os.path.relpath(full, ROOT)
        if os.sep != "/": rel = rel.replace(os.sep, "/")
        kind = classify(rel)
        with io.open(full, encoding="utf-8", errors="replace") as fh:
            page = fh.read()
        t = TITLE_RE.search(page)
        d = DESC_RE.search(page)
        title = html.unescape(re.sub(r"\s+", " ", t.group(1)).strip()) if t else ""
        desc = html.unescape(re.sub(r"\s+", " ", d.group(1)).strip()) if d else ""
        s = stats[kind]; s["pages"] += 1
        s["titles"].append(len(title)); s["descs"].append(len(desc))
        dup_title[title].append(rel); dup_desc[desc].append(rel)
        probs = []
        if kind == "static-404":
            pass  # exempt: not an SEO surface
        else:
            if not title: probs.append("no <title>")
            else:
                if len(title) > TITLE_MAX: probs.append("title %d>54" % len(title))
                elif len(title) < TITLE_MIN: probs.append("title %d<48" % len(title))
                if BRAND in title and kind != "home":
                    probs.append("brand in title (only home)")
            if not desc: probs.append("no description")
            else:
                if len(desc) < DESC_MIN: probs.append("desc %d<120" % len(desc))
                elif len(desc) > DESC_MAX: probs.append("desc %d>140" % len(desc))
                if BRAND not in desc: probs.append("desc missing brand")
        if probs: offenders.append((kind, rel, title if title else "-", desc if desc else "-", "; ".join(probs)))
        n += 1

print("pages scanned: %d" % n)
print("\n%-14s %6s %18s %18s" % ("type", "pages", "title len (min/med/max)", "desc len (min/med/max)"))
for kind in sorted(stats):
    s = stats[kind]
    tl, dl = s["titles"], s["descs"]
    print("%-14s %6d %10d/%3d/%3d %12d/%3d/%3d" % (
        kind, s["pages"],
        min(tl), int(statistics.median(tl)), max(tl),
        min(dl), int(statistics.median(dl)), max(dl)))

dups_t = {t: v for t, v in dup_title.items() if t and len(v) > 1}
dups_d = {d: v for d, v in dup_desc.items() if d and len(v) > 1}
print("\nduplicate titles: %d groups" % len(dups_t))
for t, v in sorted(dups_t.items(), key=lambda kv: -len(kv[1]))[:10]:
    print("  [%dx] %s  e.g. %s" % (len(v), t[:70], v[0]))
print("duplicate descriptions: %d groups" % len(dups_d))
for d, v in sorted(dups_d.items(), key=lambda kv: -len(kv[1]))[:10]:
    print("  [%dx] %s...  e.g. %s" % (len(v), d[:60], v[0]))

shown = int(sys.argv[sys.argv.index("--limit") + 1]) if "--limit" in sys.argv else 25
print("\noffenders (%d total, showing %d):" % (len(offenders), min(shown, len(offenders))))
for kind, rel, t, d, why in sorted(offenders, key=lambda o: (o[0], o[1]))[:shown]:
    print("  [%s] %s\n      T(%d): %s\n      D(%d): %s" % (kind, rel, len(t), t[:100], len(d), d[:100]))
    print("      -> %s" % why)
