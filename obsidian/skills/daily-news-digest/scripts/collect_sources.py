#!/usr/bin/env python3
"""Collect a single day's notes for the daily-news-digest skill.

Given a date (YYYY-MM-DD), this scans the vault for notes whose filename
starts with that date prefix and emits a compact JSON manifest to stdout.
The manifest is what the skill's AI step reads to judge newsworthiness —
so the goal here is cheap, deterministic extraction of the *signals*
(frontmatter category/tags + a short body snippet), NOT full note bodies.

Two buckets are produced:
  - news_candidates: everything under references/*/  (consumed external
    content — the raw material the AI triages into news vs non-news)
  - research:        everything under research/      (the user's own
    notes — these go in the digest's appendix, not the news body)

No third-party dependencies (no PyYAML) so it runs anywhere Python 3 does.
The frontmatter parser is intentionally minimal: it only understands the
flat `key: value` and indented `- item` list shapes these notes actually
use. Anything it can't parse is simply skipped — the body snippet is the
backstop signal.
"""

import json
import re
import sys
from pathlib import Path

# Frontmatter scalar fields worth surfacing to the triage step. Each is a
# cheap, high-signal hint about whether a note is time-sensitive news.
SCALAR_FIELDS = (
    "title",
    "url",
    "channel_name",
    "channel",
    "duration",
    "upload_date",
    "date",
    "language",
    "type",
)
# List fields (category / tags) are the strongest newsworthiness signal:
# "News & Politics" vs "Education", geopolitics/oil-prices vs tutorial/skill-system.
LIST_FIELDS = ("categories", "tags")

SNIPPET_CHARS = 400


def split_frontmatter(text):
    """Return (frontmatter_text, body_text). Empty frontmatter if absent."""
    if not text.startswith("---"):
        return "", text
    # Match the first fenced YAML block: --- ... ---
    m = re.match(r"^---\s*\n(.*?)\n---\s*\n?(.*)$", text, re.DOTALL)
    if not m:
        return "", text
    return m.group(1), m.group(2)


def parse_frontmatter(fm_text):
    """Minimal YAML-ish parser for the flat scalar + indented-list shapes."""
    data = {}
    lines = fm_text.split("\n")
    i = 0
    while i < len(lines):
        line = lines[i]
        # Indented list items belong to the key opened on a prior line; the
        # list-collection branch below consumes them, so a stray one here is
        # just skipped.
        m = re.match(r"^([A-Za-z_][\w-]*):\s*(.*)$", line)
        if not m:
            i += 1
            continue
        key, inline = m.group(1), m.group(2).strip()
        if key in LIST_FIELDS:
            items = []
            # Inline form: `tags: [a, b]`
            if inline.startswith("[") and inline.endswith("]"):
                items = [
                    x.strip().strip('"').strip("'")
                    for x in inline[1:-1].split(",")
                    if x.strip()
                ]
            else:
                # Block form: subsequent `  - item` lines.
                j = i + 1
                while j < len(lines) and re.match(r"^\s*-\s+", lines[j]):
                    items.append(re.sub(r"^\s*-\s+", "", lines[j]).strip().strip('"').strip("'"))
                    j += 1
                i = j - 1
            if items:
                data[key] = items
        elif key in SCALAR_FIELDS and inline:
            data[key] = inline.strip().strip('"').strip("'")
        i += 1
    return data


def extract_snippet(body):
    """First substantive prose paragraph, trimmed to SNIPPET_CHARS."""
    for block in re.split(r"\n\s*\n", body):
        cleaned = block.strip()
        # Skip markdown headers, list-only blocks, code fences, callouts.
        cleaned = re.sub(r"^#{1,6}\s+.*$", "", cleaned, flags=re.MULTILINE).strip()
        if not cleaned or cleaned.startswith(("```", ">", "|", "![", "- ", "* ")):
            continue
        cleaned = re.sub(r"\s+", " ", cleaned)
        if len(cleaned) < 20:  # too short to be a real lead paragraph
            continue
        return cleaned[:SNIPPET_CHARS]
    return ""


def collect_one(path, vault_root):
    try:
        text = path.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError):
        return None
    fm_text, body = split_frontmatter(text)
    fm = parse_frontmatter(fm_text)
    rel = str(path.relative_to(vault_root))
    return {
        "path": rel,
        # wikilink target = filename without .md extension (Obsidian convention)
        "wikilink": path.stem,
        "folder": str(path.parent.relative_to(vault_root)),
        "title": fm.get("title", path.stem),
        "url": fm.get("url", ""),
        "channel": fm.get("channel_name") or fm.get("channel", ""),
        "duration": fm.get("duration", ""),
        "language": fm.get("language", ""),
        "categories": fm.get("categories", []),
        "tags": fm.get("tags", []),
        "snippet": extract_snippet(body),
    }


def scan(glob_root, date, vault_root):
    base = vault_root / glob_root
    if not base.exists():
        return []
    # Recurse at any depth: references/ holds notes at the root, one level
    # deep (references/ai/…), and nested (references/playlist/<series>/…).
    # The date-prefix filename is the relevance filter, not folder depth.
    pattern = f"{date}*.md"
    paths = base.rglob(pattern)
    out = []
    for p in sorted(paths):
        if not p.name.startswith(date):
            continue
        rec = collect_one(p, vault_root)
        if rec:
            out.append(rec)
    return out


def main():
    if len(sys.argv) < 2:
        print("usage: collect_sources.py YYYY-MM-DD [vault_root]", file=sys.stderr)
        sys.exit(2)
    date = sys.argv[1]
    if not re.fullmatch(r"\d{4}-\d{2}-\d{2}", date):
        print(f"error: date must be YYYY-MM-DD, got {date!r}", file=sys.stderr)
        sys.exit(2)
    vault_root = Path(sys.argv[2]) if len(sys.argv) > 2 else Path.cwd()
    vault_root = vault_root.resolve()

    news = scan("references", date, vault_root)
    research = scan("research", date, vault_root)

    manifest = {
        "date": date,
        "vault_root": str(vault_root),
        "counts": {"news_candidates": len(news), "research": len(research)},
        "news_candidates": news,
        "research": research,
    }
    print(json.dumps(manifest, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
