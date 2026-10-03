# -*- coding: utf-8 -*-
"""Post-build output guard: inspect every page Hugo emitted in `public/`.

Why this exists (2026-10-03 incident):
  Search Console reported "评分超出了指定范围或默认范围（在 reviewRating 中）" on
  /esim-providers/holafly/. Two defects stacked:
    a) `"bestRating" "10"` was emitted as a STRING (and worstRating was absent),
       so Google fell back to its default 1-5 scale;
    b) the rating itself was an editorial price index scoring 0.0-8.4, and seven
       of eight brands scored below 1 -> out of range -> the whole Rating node was
       invalid and ineligible for rich results.
  The same release also shipped three Go format-string bugs that were VISIBLE body
  text: `%!d(float64=84)%`, `%!m(MISSING)argin`, `%!(EXTRA string=Airalo, ...)`.

  None of these are caught by `hugo` (it renders happily), by validate.py (data
  layer only) or by check_css_sync.py (CSS only). They only exist in the OUTPUT,
  so the guard has to read the output.

Checks
  1. no Go fmt error residue (`%!x(...)`) anywhere in public/**/*.html
  2. every <script type="application/ld+json"> block parses as JSON
  3. every Review/reviewRating and AggregateRating is in range:
     ratingValue must be a JSON number and satisfy
     worstRating <= ratingValue <= bestRating, with numeric scales
     (defaults 1 and 5 when omitted, per Google's documentation)

Exit code 1 on any failure. Run AFTER `hugo`:
    python -X utf8 scripts/check_output.py
"""
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PUBLIC = ROOT / "public"

FMT_ERROR = re.compile(r"%![A-Za-z]*(?:\([^)]*\))?")
LDJSON = re.compile(r'<script type="application/ld\+json">(.*?)</script>', re.S)

errors: list[str] = []


def walk(obj):
    """Yield every dict inside a JSON-LD tree (nodes are nested in @graph)."""
    if isinstance(obj, dict):
        yield obj
        for v in obj.values():
            yield from walk(v)
    elif isinstance(obj, list):
        for v in obj:
            yield from walk(v)


def check_rating(node: dict, where: str, handled: set) -> None:
    """Validate ratings whether they hang off a property or stand alone.

    Two shapes exist in the wild:
      {"@type":"Review",  "reviewRating": {...}}     <- nested
      {"@type":"AggregateRating", "ratingValue": 4}  <- standalone node
    `handled` holds the id() of nested rating objects already validated, so the
    standalone branch does not report the same defect a second time when walk()
    descends into them.
    """
    candidates: list[tuple[str, object]] = [
        (k, node.get(k)) for k in ("reviewRating", "aggregateRating")
    ]
    for _, rating in candidates:
        if isinstance(rating, dict):
            handled.add(id(rating))

    types = node.get("@type")
    types = types if isinstance(types, list) else [types]
    if any(t in ("Rating", "AggregateRating") for t in types) and id(node) not in handled:
        candidates.append((str(node.get("@type")), node))

    for name, rating in candidates:
        if not isinstance(rating, dict):
            continue
        value = rating.get("ratingValue")
        if value is None:
            errors.append(f"{where}: {name} has no ratingValue")
            continue
        if not isinstance(value, (int, float)) or isinstance(value, bool):
            errors.append(
                f"{where}: {name}.ratingValue is {value!r} "
                f"(must be a JSON number, not a string)"
            )
            continue

        def scale(prop: str, default: float) -> float:
            v = rating.get(prop, default)
            if not isinstance(v, (int, float)) or isinstance(v, bool):
                errors.append(
                    f"{where}: {name}.{prop} is {v!r} "
                    f"(must be a JSON number, not a string)"
                )
                return default
            return float(v)

        low, high = scale("worstRating", 1), scale("bestRating", 5)
        if high <= low:
            errors.append(f"{where}: {name}.bestRating {high} <= worstRating {low}")
        if not (low <= value <= high):
            errors.append(
                f"{where}: {name}.ratingValue {value} outside [{low:g}, {high:g}] "
                f"(Google: 评分超出了指定范围)"
            )


def main() -> int:
    if not PUBLIC.is_dir():
        print("ERROR public/ not found - run `hugo` first")
        return 1

    pages = sorted(PUBLIC.rglob("*.html"))
    ld_blocks = 0

    for f in pages:
        rel = f.relative_to(ROOT).as_posix()
        text = f.read_text(encoding="utf-8", errors="replace")

        for m in FMT_ERROR.finditer(text):
            line = text.count("\n", 0, m.start()) + 1
            ctx = text[max(0, m.start() - 45):m.end() + 25].replace("\n", " ")
            errors.append(f"{rel}:{line}: Go format-string leak -> {ctx.strip()!r}")

        for m in LDJSON.finditer(text):
            ld_blocks += 1
            try:
                data = json.loads(m.group(1))
            except ValueError as e:
                errors.append(f"{rel}: invalid JSON-LD - {e}")
                continue
            handled: set = set()
            for node in walk(data):
                check_rating(node, rel, handled)

    if errors:
        print(f"ERROR output guard: {len(errors)} problem(s) in public/")
        for e in errors[:40]:
            print(f"  {e}")
        if len(errors) > 40:
            print(f"  ... and {len(errors) - 40} more")
        return 1

    print(f"OK: {len(pages)} pages, {ld_blocks} JSON-LD blocks - no format leaks, all ratings in range")
    return 0


if __name__ == "__main__":
    sys.exit(main())
