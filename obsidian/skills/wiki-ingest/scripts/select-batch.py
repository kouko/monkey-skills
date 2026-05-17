#!/usr/bin/env python3
# select-batch.py — Choose which vault files to ingest next (part of wiki-ingest).
#
# Usage:
#   scan-vault.sh <vault-root> \
#     | python3 select-batch.py
#
# Reads vault-relative candidate paths from stdin (one per line).
# Consults .manifest.json to skip UNCHANGED files.
# Sorts NEW + MODIFIED files by date (3-tier: filename → frontmatter → mtime)
# and outputs the first BATCH_CAP entries as JSON.
#
# Required env vars:
#   BATCH_ORDER     oldest-first | newest-first  (default: oldest-first)
#   BATCH_CAP       int (default: 15)
#   MANIFEST_PATH   absolute path to <vault-root>/wiki/.manifest.json
#   VAULT_ROOT      absolute path to the vault root
#
# Optional env vars:
#   TOPIC_FILTER    substring to match against basename / tags / aliases
#                   (case-insensitive); unset or empty → no-op
#
# Output (stdout, JSON):
#   {
#     "batch":              [...],   # ≤ BATCH_CAP vault-relative paths
#     "remaining":          [...],   # deferred paths
#     "skipped_unchanged":  N,
#     "scope_summary": {
#       "first_date":          "YYYY-MM-DD",
#       "last_date":           "YYYY-MM-DD",
#       "remaining_count":     N,
#       "remaining_first_date":"YYYY-MM-DD",
#       "remaining_last_date": "YYYY-MM-DD"
#     }
#   }
#
# Exit codes:
#   0   normal
#   2   invalid env / unreadable manifest
#
# Python >= 3.10, stdlib only.

from __future__ import annotations

import hashlib
import json
import os
import re
import sys
from pathlib import Path

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

_DATE_RE = re.compile(r"^(\d{4}-\d{2}-\d{2})")
_FRONTMATTER_RE = re.compile(
    r"^---\s*\n(.*?)\n---", re.DOTALL | re.MULTILINE
)
_FM_FIELD_RE = re.compile(
    r"^(?:date|upload_date|processed_at)\s*:\s*(\d{4}-\d{2}-\d{2})",
    re.MULTILINE,
)

# Matches a YAML list field header (tags or aliases) and captures values.
# Handles both block-list (- item) and inline list (tags: [a, b]) forms.
_FM_LIST_BLOCK_RE = re.compile(
    r"^(?:tags|aliases)\s*:\s*\[([^\]]*)\]|^(?P<key>tags|aliases)\s*:\s*\n((?:[ \t]*-[ \t]*\S[^\n]*\n?)+)",
    re.MULTILINE,
)

# Sentinel for files whose date falls back to mtime (sort to tail).
_UNDATED = "undated"


# ---------------------------------------------------------------------------
# Env validation
# ---------------------------------------------------------------------------

def _load_env() -> tuple[str, int, str, str]:
    """Return (batch_order, batch_cap, manifest_path, vault_root).

    Exits with code 2 on missing or invalid values.
    """
    missing = [
        v for v in ("MANIFEST_PATH", "VAULT_ROOT")
        if not os.environ.get(v)
    ]
    if missing:
        print(
            f"Error: missing required env vars: {', '.join(missing)}",
            file=sys.stderr,
        )
        sys.exit(2)

    batch_order = os.environ.get("BATCH_ORDER", "oldest-first").strip()
    if batch_order not in ("oldest-first", "newest-first"):
        print(
            f"Error: BATCH_ORDER must be 'oldest-first' or 'newest-first', "
            f"got: {batch_order!r}",
            file=sys.stderr,
        )
        sys.exit(2)

    raw_cap = os.environ.get("BATCH_CAP", "15").strip()
    try:
        batch_cap = int(raw_cap)
        if batch_cap < 1:
            raise ValueError
    except ValueError:
        print(
            f"Error: BATCH_CAP must be a positive integer, got: {raw_cap!r}",
            file=sys.stderr,
        )
        sys.exit(2)

    manifest_path = os.environ["MANIFEST_PATH"].strip()
    vault_root = os.environ["VAULT_ROOT"].strip()

    return batch_order, batch_cap, manifest_path, vault_root


# ---------------------------------------------------------------------------
# Manifest
# ---------------------------------------------------------------------------

def _load_manifest(manifest_path: str) -> dict:
    """Return manifest dict.  Missing file → {}.  Parse error → exit 2."""
    p = Path(manifest_path)
    if not p.exists():
        return {}
    try:
        return json.loads(p.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        print(f"Error: cannot read manifest: {exc}", file=sys.stderr)
        sys.exit(2)


# ---------------------------------------------------------------------------
# Hashing
# ---------------------------------------------------------------------------

def _sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


# ---------------------------------------------------------------------------
# Date resolution (3-tier)
# ---------------------------------------------------------------------------

def _date_from_filename(name: str) -> str | None:
    """Extract YYYY-MM-DD from a filename prefix, e.g. '2024-01-15-note.md'."""
    m = _DATE_RE.match(name)
    return m.group(1) if m else None


def _date_from_frontmatter(text: str) -> str | None:
    """Extract first date field (date/upload_date/processed_at) from frontmatter."""
    fm_match = _FRONTMATTER_RE.match(text)
    if not fm_match:
        return None
    block = fm_match.group(1)
    fm = _FM_FIELD_RE.search(block)
    return fm.group(1) if fm else None


def _fm_list_values(fm_block: str, field: str) -> list[str]:
    """Return lowercased list values for `field` (tags or aliases) from a frontmatter block.

    Handles both:
      tags: [a, b, c]          (inline)
      tags:
        - a
        - b                    (block)
    """
    values: list[str] = []
    # Inline form: field: [val1, val2, ...]
    inline_re = re.compile(
        rf"^{field}\s*:\s*\[([^\]]*)\]",
        re.MULTILINE,
    )
    m = inline_re.search(fm_block)
    if m:
        for v in m.group(1).split(","):
            v = v.strip().strip('"').strip("'")
            if v:
                values.append(v.casefold())
        return values

    # Block form: field:\n  - val
    block_re = re.compile(
        rf"^{field}\s*:\s*\n((?:[ \t]*-[ \t]*\S[^\n]*\n?)+)",
        re.MULTILINE,
    )
    m = block_re.search(fm_block)
    if m:
        for line in m.group(1).splitlines():
            v = line.strip().lstrip("-").strip().strip('"').strip("'")
            if v:
                values.append(v.casefold())
    return values


def _matches_topic_filter(rel: str, abs_path: Path, topic_filter: str) -> bool:
    """Return True if `rel` should be kept given `topic_filter` (already casefolded).

    Checks (a) basename, (b) frontmatter tags, (c) frontmatter aliases.
    """
    # (a) basename
    if topic_filter in Path(rel).name.casefold():
        return True

    # (b) + (c) frontmatter tags and aliases
    try:
        text = abs_path.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return False

    fm_match = _FRONTMATTER_RE.match(text)
    if not fm_match:
        return False

    block = fm_match.group(1)
    for field in ("tags", "aliases"):
        if topic_filter in _fm_list_values(block, field):
            return True

    return False


def _resolve_date(abs_path: Path) -> tuple[str | None, str]:
    """Return (date_str, tier) where tier ∈ 'filename'|'frontmatter'|'mtime'.

    date_str is None when tier == 'mtime' (undated).
    """
    # Tier 1: filename prefix
    date = _date_from_filename(abs_path.name)
    if date:
        return date, "filename"

    # Tier 2: frontmatter
    try:
        text = abs_path.read_text(encoding="utf-8", errors="replace")
        date = _date_from_frontmatter(text)
        if date:
            return date, "frontmatter"
    except OSError:
        pass

    # Tier 3: mtime fallback (undated → sort to tail)
    return None, "mtime"


# ---------------------------------------------------------------------------
# Sorting key
# ---------------------------------------------------------------------------

def _sort_key(item: dict, reverse: bool) -> tuple:
    """Return a tuple for sorting.

    Dated items sort before undated:
      (0, date_str) — dated; date_str sorts lexicographically (ISO 8601 safe)
      (1, mtime)    — undated; always at tail, sorted by mtime asc within tail
    """
    if item["date"] is None:
        # Undated always at tail; sort within tail by mtime asc (regardless of order)
        return (1, item["mtime"])
    # Dated: primary bucket 0; within dated, direction controlled by caller
    date_str = item["date"]
    if reverse:
        # Flip lexicographic order: prefix with a negated value is awkward for
        # strings, so invert via a tuple trick: (0, '') sorts before (0, 'z').
        # For newest-first we want larger dates first, which means reversed sort.
        # We return the tuple normally but the caller uses reverse=True on the
        # dated items; undated still go to tail regardless.
        # Simpler: use a decorated sort below.
        return (0, date_str)
    return (0, date_str)


# ---------------------------------------------------------------------------
# Scope summary helpers
# ---------------------------------------------------------------------------

def _dates_of(items: list[dict]) -> list[str]:
    """Extract non-None dates from a list of item dicts."""
    return [i["date"] for i in items if i["date"] is not None]


def _first_last(dates: list[str]) -> tuple[str | None, str | None]:
    if not dates:
        return None, None
    return min(dates), max(dates)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> None:
    batch_order, batch_cap, manifest_path, vault_root = _load_env()
    manifest = _load_manifest(manifest_path)
    topic_filter = os.environ.get("TOPIC_FILTER", "").strip().casefold()

    vault = Path(vault_root)

    # Read candidate paths from stdin (vault-relative, one per line)
    candidates: list[str] = [
        line.strip()
        for line in sys.stdin
        if line.strip()
    ]

    # Bucket into NEW / MODIFIED / UNCHANGED
    to_process: list[dict] = []  # NEW + MODIFIED
    skipped_unchanged = 0

    for rel in candidates:
        abs_path = vault / rel
        try:
            digest = _sha256(abs_path)
        except OSError:
            # File unreadable — skip silently (scan-vault already emitted valid paths)
            continue

        entry = manifest.get(rel)
        if entry is not None and entry.get("sha256") == digest:
            skipped_unchanged += 1
            continue

        # NEW or MODIFIED — resolve sort date
        date, _tier = _resolve_date(abs_path)
        try:
            mtime = abs_path.stat().st_mtime
        except OSError:
            mtime = 0.0

        to_process.append({
            "path": rel,
            "date": date,
            "mtime": mtime,
        })

    # Apply TOPIC_FILTER (after bucket, before sort+cap).
    # UNCHANGED count is already fixed; filter only reduces to_process.
    # A MODIFIED file excluded by filter is simply not re-ingested this run;
    # its manifest entry remains and it will reappear in future runs if still MODIFIED.
    if topic_filter:
        to_process = [
            item for item in to_process
            if _matches_topic_filter(item["path"], vault / item["path"], topic_filter)
        ]

    # Sort: dated items by date (asc or desc), undated at tail by mtime asc
    reverse_dated = (batch_order == "newest-first")

    dated = [i for i in to_process if i["date"] is not None]
    undated = [i for i in to_process if i["date"] is None]

    dated.sort(key=lambda i: i["date"], reverse=reverse_dated)
    undated.sort(key=lambda i: i["mtime"])  # always mtime asc within tail

    sorted_items = dated + undated

    # Split into batch and remaining
    batch_items = sorted_items[:batch_cap]
    remaining_items = sorted_items[batch_cap:]

    # Build scope_summary
    batch_dates = _dates_of(batch_items)
    remaining_dates = _dates_of(remaining_items)

    b_first, b_last = _first_last(batch_dates)
    r_first, r_last = _first_last(remaining_dates)

    scope_summary: dict = {
        "first_date": b_first,
        "last_date": b_last,
        "remaining_count": len(remaining_items),
        "remaining_first_date": r_first,
        "remaining_last_date": r_last,
    }

    output = {
        "batch": [i["path"] for i in batch_items],
        "remaining": [i["path"] for i in remaining_items],
        "skipped_unchanged": skipped_unchanged,
        "scope_summary": scope_summary,
    }

    print(json.dumps(output, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
