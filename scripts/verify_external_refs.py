#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Verify every external reference in data/refs.toml actually resolves.

Why this exists
---------------
The brand x country pages cite host-network data and link out to the sources
behind it. A link that 404s is worse than no link at all: it tells the reader
the data is unsourced *and* wastes their click.

Grading is deliberately three-way, because "did not return 200" hides three
very different situations:
    2xx         -> ok
    403/412/429 -> bot wall. The host answered; the site exists. att.com,
                   t-mobile.com and bell.ca all 403 a script and are fine for
                   a human. Keep them.
    404/410     -> dead. This is the only bucket that fails the run.
    000/5xx     -> unreachable from THIS machine. Local DNS/TLS blocks and
                   geofencing are common (jio.com returns 000 here and loads
                   perfectly in a browser), so these are reported as
                   "re-check elsewhere", never auto-deleted.

Design
------
* Reads data/refs.toml (stdlib tomllib, Python 3.11+).
* [carriers] -> official operator site / coverage map per host carrier.
  (There is deliberately no per-country third-party block here: the Ookla
  Global Index slug rules live in data/networkreports.toml and are shared by
  compare/single.html and compare/provider.html.)
* Before touching the network, check_alignment() proves every refs.toml key
  maps to a real carriers.toml profile and that no profile is silently
  missing a link. A ref pointing at a carrier that does not exist is dead
  weight; a carrier with no ref is a missed citation.
* Requests are serial with a delay and a browser UA. Ookla rate-limits
  hard: a 50-request burst from one IP returns connection failures
  (curl exit 000), not 4xx, so a naive parallel sweep produces false
  negatives and looks like "the whole site is down".
* Retries connection failures and 5xx once after a longer pause.
* --write-report dumps docs/external-refs-report.json for the next round.

Exit code 1 only when a reference is verifiably gone (404/410).
This is a NETWORK check, so it is deliberately NOT part of `npm run build`.

    python -X utf8 scripts/verify_external_refs.py
    python -X utf8 scripts/verify_external_refs.py --only JP
    python -X utf8 scripts/verify_external_refs.py --data-only   # offline
    python -X utf8 scripts/verify_external_refs.py --selftest
"""

from __future__ import annotations

import argparse
import json
import pathlib
import re
import sys
import time
import tomllib
import urllib.error
import urllib.request

ROOT = pathlib.Path(__file__).resolve().parent.parent
REFS = ROOT / "data" / "refs.toml"
REPORT = ROOT / "docs" / "external-refs-report.json"

UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/124.0 Safari/537.36")

DELAY = 1.2          # seconds between requests
RETRY_DELAY = 6.0    # seconds before the single retry
TIMEOUT = 25


def load() -> tuple[dict, dict]:
    if not REFS.is_file():
        print(f"ERROR {REFS.relative_to(ROOT)} not found")
        sys.exit(2)
    with REFS.open("rb") as fh:
        data = tomllib.load(fh)
    return data.get("sources", {}), data.get("carriers", {})


def probe(url: str) -> tuple[int, str]:
    """Return (status, note). status 0 means the request never completed."""
    req = urllib.request.Request(url, headers={
        "User-Agent": UA,
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.9",
    })
    try:
        with urllib.request.urlopen(req, timeout=TIMEOUT) as resp:
            return resp.status, ""
    except urllib.error.HTTPError as exc:
        return exc.code, f"HTTP {exc.code} {exc.reason}"
    except Exception as exc:                      # noqa: BLE001 - report anything
        return 0, type(exc).__name__


def ok(status: int) -> bool:
    return 200 <= status < 300


def blocked(status: int) -> bool:
    """403 / 412 / 429 - the host answered, it just refuses automated clients.

    A 403 is *evidence the site exists*. Grading it as a failure would delete
    correct links (att.com, t-mobile.com, bell.ca all 403 a bot), which is
    exactly the wrong call. These stay, flagged, so a human can spot-check.
    """
    return status in (403, 412, 429)


def dead(status: int) -> bool:
    """404 / 410 - the resource really is gone. Only this fails the run."""
    return status in (404, 410)


def check_alignment(carriers: dict) -> int:
    """refs.toml <-> carriers.toml: no orphans, and count the silent gaps.

    An orphan (a ref for a carrier that carries.toml does not define) means the
    link can never render - dead weight in the file. A carrier with no ref is
    not an error (the template degrades gracefully) but it IS a missed citation,
    so report it loudly instead of letting it hide.
    """
    src = (ROOT / "data" / "carriers.toml").read_text(encoding="utf-8")
    cur, have = None, {}
    for line in src.splitlines():
        m = re.match(r"^\[\[([A-Z]{2})\.profiles\]\]", line)
        if m:
            cur = m.group(1)
            have.setdefault(cur, [])
            continue
        m = re.match(r'^name\s*=\s*"([^"]+)"', line)
        if m and cur:
            have[cur].append(m.group(1))

    orphans, missing = [], []
    for iso, table in sorted(carriers.items()):
        for name in sorted(table):
            if name not in have.get(iso, []):
                orphans.append(f"{iso} | {name}")
    for iso, names in sorted(have.items()):
        got = carriers.get(iso, {})
        for n in names:
            if n not in got:
                missing.append(f"{iso} | {n}")

    total_links = sum(len(v) for v in carriers.values())
    total_prof = sum(len(v) for v in have.values())
    print(f"alignment: {len(carriers)} countries / {total_links} refs "
          f"vs {len(have)} countries / {total_prof} profiles in carriers.toml")
    if orphans:
        print(f"  ORPHAN refs (no such profile) {len(orphans)}:")
        for o in orphans:
            print("   ", o)
    if missing:
        print(f"  profiles without a ref {len(missing)} "
              f"(template skips them; fill in when a source is verified):")
        for m_ in missing[:12]:
            print("   ", m_)
        if len(missing) > 12:
            print(f"    ... and {len(missing) - 12} more")
    if not orphans and not missing:
        print("  complete: every profile has a 1:1 ref")
    return 1 if orphans else 0


def collect(sources: dict, carriers: dict, only: str | None):
    items: list[tuple[str, str, str]] = []        # (kind, label, url)
    for iso, url in sorted(sources.items()):
        if only and iso != only:
            continue
        items.append(("source", iso, url))
    for iso, table in sorted(carriers.items()):
        if only and iso != only:
            continue
        for name, url in sorted(table.items()):
            items.append(("carrier", f"{iso} | {name}", url))
    return items


def selftest() -> int:
    """Prove the checker can fail: bogus host must not report success."""
    print("selftest: a request that cannot complete must not count as OK")
    status, note = probe("https://definitely-not-a-real-host-9f3a.example/")
    print(f"   bogus host -> status={status} note={note!r} ok={ok(status)}")
    if ok(status):
        print("FAIL  an unreachable host was graded as OK")
        return 1
    status, note = probe("https://www.speedtest.net/global-index/zzz-not-a-country")
    print(f"   known 404   -> status={status} ok={ok(status)}")
    if ok(status):
        print("FAIL  a 404 was graded as OK")
        return 1
    print("OK  selftest passed")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--only", help="restrict to one ISO country code")
    ap.add_argument("--write-report", action="store_true")
    ap.add_argument("--data-only", action="store_true",
                    help="offline: only check refs.toml <-> carriers.toml alignment")
    ap.add_argument("--selftest", action="store_true")
    args = ap.parse_args()

    if args.selftest:
        return selftest()

    sources, carriers = load()
    align_rc = check_alignment(carriers)
    if args.data_only:
        return align_rc
    print()
    if align_rc:
        print("refusing to run the network sweep while orphans exist - "
              "fix data/refs.toml first\n")
        return 1

    items = collect(sources, carriers, args.only)
    print(f"Checking {len(items)} external references\n")

    results, failed, pending = [], [], []
    for i, (kind, label, url) in enumerate(items, 1):
        status, note = probe(url)
        # A bot wall (403/412/429) and a hard 404 will not change on a second
        # ask; connection failures (000) and 5xx often will.
        if status == 0 or status >= 500:
            time.sleep(RETRY_DELAY)
            status, note = probe(url)
        if ok(status):
            flag, bucket = "OK  ", "ok"
        elif blocked(status):
            flag, bucket = "BLK ", "blocked"
        elif dead(status):
            flag, bucket = "DEAD", "dead"
        else:
            flag, bucket = "??? ", "unreachable"
        print(f"{flag} [{i:3d}/{len(items)}] {kind:7s} {label:28s} {status} {url}")
        results.append({"kind": kind, "label": label, "url": url,
                        "status": status, "bucket": bucket})
        if bucket == "dead":
            failed.append((kind, label, url, status, note))
        elif bucket == "unreachable":
            pending.append((kind, label, url, status, note))
        time.sleep(DELAY)

    if args.write_report:
        REPORT.parent.mkdir(parents=True, exist_ok=True)
        REPORT.write_text(json.dumps({
            "total": len(results), "failed": len(failed), "results": results,
        }, indent=2, ensure_ascii=False), encoding="utf-8")
        print(f"\nreport -> {REPORT.relative_to(ROOT)}")

    print()
    n_ok = sum(1 for r in results if r["bucket"] == "ok")
    n_blk = sum(1 for r in results if r["bucket"] == "blocked")
    print(f"ok {n_ok} · bot-wall(403/412/429, site exists) {n_blk} · "
          f"unreachable-from-here {len(pending)} · dead {len(failed)}")

    if pending:
        print(f"\nUNREACHABLE from this network {len(pending)} — NOT proof of a bad link.")
        print("  jio.com fails from this machine and loads perfectly elsewhere, so treat")
        print("  a local 000/DNS/TLS failure as 'unknown', not 'broken':")
        for kind, label, url, status, note in pending:
            print(f"   {kind:7s} {label:28s} {status} {note}  {url}")
        print("  Re-check from another network or via a search-engine cache before editing.")

    if failed:
        print(f"\nFAIL {len(failed)} reference(s) are gone (404/410):")
        for kind, label, url, status, note in failed:
            print(f"   {kind:7s} {label:28s} {status} {note}  {url}")
        print("\nReplace or delete every 404/410 in data/refs.toml. Never ship a dead link.")
        return 1

    print(f"\nOK  no dead references ({len(items)} checked)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
