#!/usr/bin/env python3
"""Collect a single day's notes for the daily-news-digest skill.

Given a date (YYYY-MM-DD), this scans the WHOLE vault for notes whose filename
starts with that date prefix and emits a compact JSON manifest to stdout. It
casts a wide net on purpose — **every dated note except a small set of excluded
folders is returned as a candidate, and the skill's AI step (triage) decides
what to include and how to classify it** (時效新聞 / 知識與觀點 / research
appendix / drop). The collector does not assume any particular folder layout.

Excluded by default (`--exclude`):
  - wiki/        the LLM-owned wiki layer — never consumed as news
  - news/        this skill's own output — avoid digesting prior digests
  - _templates/  note templates, not content
  - any dot-folder (.obsidian/, .git/, .claude/, …) — config / system

The goal is cheap, deterministic extraction of the *signals* (frontmatter
category/tags + a short body snippet), NOT full note bodies. No third-party
dependencies (no PyYAML) so it runs anywhere Python 3 does.
"""

import argparse
import json
import re
import sys
from pathlib import Path

# Frontmatter scalar fields worth surfacing to the triage step.
SCALAR_FIELDS = (
    "title", "url", "channel_name", "channel", "duration",
    "upload_date", "date", "language", "type",
)
# List fields (category / tags) are the strongest newsworthiness signal.
LIST_FIELDS = ("categories", "tags")
SNIPPET_CHARS = 400
DEFAULT_EXCLUDE = ("wiki", "news", "_templates")


def split_frontmatter(text):
    """Return (frontmatter_text, body_text). Empty frontmatter if absent."""
    if not text.startswith("---"):
        return "", text
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
        m = re.match(r"^([A-Za-z_][\w-]*):\s*(.*)$", line)
        if not m:
            i += 1
            continue
        key, inline = m.group(1), m.group(2).strip()
        if key in LIST_FIELDS:
            items = []
            if inline.startswith("[") and inline.endswith("]"):
                items = [
                    x.strip().strip('"').strip("'")
                    for x in inline[1:-1].split(",") if x.strip()
                ]
            else:
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
        cleaned = re.sub(r"^#{1,6}\s+.*$", "", cleaned, flags=re.MULTILINE).strip()
        if not cleaned or cleaned.startswith(("```", ">", "|", "![", "- ", "* ")):
            continue
        cleaned = re.sub(r"\s+", " ", cleaned)
        if len(cleaned) < 20:
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
    return {
        "path": str(path.relative_to(vault_root)),
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


def excluded(rel, exclude):
    """True if this relative path should be skipped: an excluded top-level
    folder, or any dot-directory component."""
    parts = rel.parts
    if len(parts) > 1 and parts[0] in exclude:
        return True
    # any directory component (not the filename itself) starting with '.'
    return any(part.startswith(".") for part in parts[:-1])


def scan_vault(date, vault_root, exclude):
    out = []
    for p in sorted(vault_root.rglob(f"{date}*.md")):
        if not p.name.startswith(date):
            continue
        rel = p.relative_to(vault_root)
        if excluded(rel, exclude):
            continue
        rec = collect_one(p, vault_root)
        if rec:
            out.append(rec)
    return out


def main():
    ap = argparse.ArgumentParser(description="Collect a day's dated notes for daily-news-digest.")
    ap.add_argument("date")
    ap.add_argument("vault_root", nargs="?", default=".")
    ap.add_argument("--exclude", default=",".join(DEFAULT_EXCLUDE),
                    help="comma-separated top-level folders to skip "
                         f"(default: {','.join(DEFAULT_EXCLUDE)}); dot-folders are always skipped")
    args = ap.parse_args()

    if not re.fullmatch(r"\d{4}-\d{2}-\d{2}", args.date):
        print(f"error: date must be YYYY-MM-DD, got {args.date!r}", file=sys.stderr)
        sys.exit(2)
    vault_root = Path(args.vault_root).resolve()
    exclude = {x.strip() for x in args.exclude.split(",") if x.strip()}

    candidates = scan_vault(args.date, vault_root, exclude)
    manifest = {
        "date": args.date,
        "vault_root": str(vault_root),
        "excluded_folders": sorted(exclude),
        "counts": {"candidates": len(candidates)},
        "candidates": candidates,
    }
    print(json.dumps(manifest, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
