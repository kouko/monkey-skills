#!/usr/bin/env python3
"""Search prior dated notes for an evolving story — the history backbone for
daily-news-digest's 事件進程 (event-progression) analysis.

Given keywords (OR logic) and a date window, this scans the vault's dated notes
(references/ + investing/ by default) and emits a date-sorted, compact JSON
manifest of matching notes. The skill's AI step reads it to build a timeline /
trend chart and a 趨勢分析 paragraph — so the goal is cheap, deterministic
gathering of *which notes on which dates touched this story*, plus a snippet
around the first keyword hit (where the day's number/fact usually sits).

Usage:
  collect_history.py "美伊,イラン,Hormuz,荷莫茲" . --since 2026-03-01 --until 2026-06-14
  collect_history.py "油價,WTI,原油" . --until 2026-06-14 --per-day 2

Notes:
  - Keywords are comma- OR space-separated; matching is case-insensitive
    substring (CJK-safe, no word boundaries).
  - --until usually = the digest date MINUS one day (you want *prior* context;
    today's notes are already in the digest). Defaults: since = 90 days of
    filename scan is cheap, so since defaults to open; until defaults to open.
  - --per-day caps notes kept per date (default 3) to keep the manifest compact;
    the dropped count is reported so nothing is silently hidden.
  - No third-party dependencies.
"""

import argparse
import json
import re
import sys
from pathlib import Path

DATE_RE = re.compile(r"(\d{4}-\d{2}-\d{2})")
SNIPPET_CHARS = 360
DEFAULT_FOLDERS = ("references", "investing")


def split_body(text):
    if text.startswith("---"):
        m = re.match(r"^---\s*\n.*?\n---\s*\n?(.*)$", text, re.DOTALL)
        if m:
            return m.group(1)
    return text


def title_of(text, stem):
    m = re.search(r"^title:\s*(.+)$", text, re.MULTILINE)
    if m:
        return m.group(1).strip().strip('"').strip("'")
    return stem


def keyword_snippet(body, kws_lower):
    """Snippet around the first keyword hit; falls back to lead prose."""
    flat = re.sub(r"\s+", " ", body)
    low = flat.lower()
    pos = min((low.find(k) for k in kws_lower if k in low), default=-1)
    if pos == -1:
        return ""
    start = max(0, pos - 60)
    return flat[start:start + SNIPPET_CHARS].strip()


def in_range(date_str, since, until):
    if since and date_str < since:
        return False
    if until and date_str > until:
        return False
    return True


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("keywords")
    ap.add_argument("vault_root", nargs="?", default=".")
    ap.add_argument("--since")
    ap.add_argument("--until")
    ap.add_argument("--per-day", type=int, default=3)
    ap.add_argument("--folders", default=",".join(DEFAULT_FOLDERS))
    args = ap.parse_args()

    for d in (args.since, args.until):
        if d and not re.fullmatch(r"\d{4}-\d{2}-\d{2}", d):
            print(f"error: date must be YYYY-MM-DD, got {d!r}", file=sys.stderr)
            sys.exit(2)

    kws = [k.strip() for k in re.split(r"[,\s]+", args.keywords) if k.strip()]
    kws_lower = [k.lower() for k in kws]
    vault_root = Path(args.vault_root).resolve()

    by_date = {}
    for folder in args.folders.split(","):
        base = vault_root / folder.strip()
        if not base.exists():
            continue
        for p in base.rglob("*.md"):
            m = DATE_RE.search(p.name)
            if not m:
                continue
            date = m.group(1)
            if not in_range(date, args.since, args.until):
                continue
            try:
                text = p.read_text(encoding="utf-8")
            except (OSError, UnicodeDecodeError):
                continue
            hay = (p.stem + "\n" + text).lower()
            if not any(k in hay for k in kws_lower):
                continue
            body = split_body(text)
            by_date.setdefault(date, []).append({
                "date": date,
                "path": str(p.relative_to(vault_root)),
                "wikilink": p.stem,
                "folder": str(p.parent.relative_to(vault_root)),
                "title": title_of(text, p.stem),
                "snippet": keyword_snippet(body, kws_lower),
            })

    timeline, dropped = [], 0
    for date in sorted(by_date):
        notes = by_date[date]
        if len(notes) > args.per_day:
            dropped += len(notes) - args.per_day
            notes = notes[:args.per_day]
        timeline.extend(notes)

    manifest = {
        "keywords": kws,
        "range": {"since": args.since, "until": args.until},
        "counts": {
            "dates": len(by_date),
            "notes_kept": len(timeline),
            "notes_dropped_by_cap": dropped,
        },
        "timeline": timeline,
    }
    print(json.dumps(manifest, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
