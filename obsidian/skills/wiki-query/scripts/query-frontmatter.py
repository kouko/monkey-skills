#!/usr/bin/env python3
# query-frontmatter.py — Tier 1 entry for wiki-query.
#
# Walks <vault>/wiki/{entities,concepts,references,skills,journal,synthesis}/*.md,
# extracts frontmatter (title / type / summary / tags) via a hand-rolled
# mini YAML parser, scores each candidate against caller-supplied keywords
# using lowercase substring match (title=3 / tag=2 / summary=1), then
# emits the top-K rows as JSON on stdout.
#
# Usage:
#   python3 query-frontmatter.py \
#     --keywords "TSMC,foundry" \
#     --top 5 \
#     --vault-root /path/to/vault \
#     [--type entities]
#
# CLI args:
#   --keywords STR     comma-separated keyword list (NFKC-lowercased before match)
#   --top INT          max rows to return  (default: 5)
#   --vault-root PATH  absolute path containing wiki/  (required)
#   --type NAME        optional; when set, restrict glob to wiki/<NAME>/*.md
#                      (one of: entities, concepts, references, skills,
#                       journal, synthesis); absent → cross-category top-K.
#
# Output (stdout, JSON array; one element per page that scored > 0):
#   [
#     {
#       "path":    "wiki/entities/TSMC.md",
#       "title":   "TSMC",
#       "type":    "wiki-entity",
#       "summary": "Largest pure-play foundry; ...",
#       "tags":    ["tsmc", "semiconductors"],
#       "score":   5
#     },
#     ...
#   ]
#
# Scope:
#   - Task 1: English happy-path (title=3 / tag=2 / summary=1 substring score).
#   - Task 2: NFKC normalization (fullwidth → halfwidth) + CJK substring via
#     Python `in` on the normalized string + --type optional filter +
#     edge cases (empty keywords → []; pages without `summary:` skipped).
#   - Stdlib-only. No PyYAML.
#
# Exit codes:
#   0   normal (empty array if no matches)
#   2   invalid args / missing vault
#
# Python >= 3.10, stdlib only.

from __future__ import annotations

import argparse
import json
import re
import sys
import unicodedata
from pathlib import Path

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

_WIKI_SUBDIRS = ("entities", "concepts", "references", "skills", "journal", "synthesis")

_FRONTMATTER_RE = re.compile(r"^---\s*\n(.*?)\n---", re.DOTALL | re.MULTILINE)

# Scalar field: `key: value` or `key: "value"`  (single line, value on same line)
_SCALAR_FIELD_RE = re.compile(
    r"^([A-Za-z_][A-Za-z0-9_]*)\s*:\s*(.*?)\s*$",
    re.MULTILINE,
)

# Per-field scoring weights (see Decision Q3 in the source brief).
_W_TITLE = 3
_W_TAG = 2
_W_SUMMARY = 1


# ---------------------------------------------------------------------------
# Mini YAML parser — the limited subset wiki/ frontmatter uses
# ---------------------------------------------------------------------------

def _strip_quotes(value: str) -> str:
    """Strip a matching pair of surrounding single or double quotes."""
    if len(value) >= 2 and value[0] == value[-1] and value[0] in ('"', "'"):
        return value[1:-1]
    return value


def _parse_list_inline(raw: str) -> list[str]:
    """Parse `[a, b, "c"]`-style inline list into list of strings.

    Limit: naive comma split — does NOT honor quoted commas, so
    `["a, b", c]` yields `['"a', 'b"', 'c']` rather than `['a, b', 'c']`.
    Not exercised by wiki/ page-format.md (no list field uses quoted-comma
    items). If a future field adds that shape, upgrade to a proper YAML
    flow-sequence parser.
    """
    inner = raw.strip()
    if not (inner.startswith("[") and inner.endswith("]")):
        return []
    inner = inner[1:-1]
    items: list[str] = []
    for piece in inner.split(","):
        piece = _strip_quotes(piece.strip())
        if piece:
            items.append(piece)
    return items


def _parse_list_block(block_text: str, field: str) -> list[str]:
    """Parse block-style list:

        tags:
          - tag1
          - tag2

    Returns the list of strings; empty list if `field:` not in block form.
    """
    # Match `field:` followed (next line onwards) by `  - item` lines.
    pat = re.compile(
        rf"^{re.escape(field)}\s*:\s*\n((?:[ \t]*-[ \t]*\S[^\n]*\n?)+)",
        re.MULTILINE,
    )
    m = pat.search(block_text)
    if not m:
        return []
    items: list[str] = []
    for line in m.group(1).splitlines():
        stripped = line.strip().lstrip("-").strip()
        stripped = _strip_quotes(stripped)
        if stripped:
            items.append(stripped)
    return items


def _parse_frontmatter(text: str) -> dict | None:
    """Extract and parse the YAML frontmatter block; return field dict or None.

    Recognized fields:
      - scalars  (title / type / summary / domain / status / updated / ...)
      - lists    (tags / aliases / contributes_to)  — inline or block form
    """
    fm = _FRONTMATTER_RE.match(text)
    if not fm:
        return None
    block = fm.group(1)

    fields: dict = {}

    # Scalars — single-line `key: value` lines NOT followed by block list.
    for line_match in _SCALAR_FIELD_RE.finditer(block):
        key = line_match.group(1)
        raw_value = line_match.group(2)

        # Empty RHS → possibly a block-list header; defer to list extraction.
        if raw_value == "":
            continue

        # Inline list?
        if raw_value.startswith("["):
            fields[key] = _parse_list_inline(raw_value)
            continue

        fields[key] = _strip_quotes(raw_value)

    # Block-form lists — overwrite if found (block form wins over empty scalar).
    for list_field in ("tags", "aliases", "contributes_to"):
        block_list = _parse_list_block(block, list_field)
        if block_list:
            fields[list_field] = block_list

    return fields


# ---------------------------------------------------------------------------
# Normalization + scoring
# ---------------------------------------------------------------------------

def _norm(s: str) -> str:
    """NFKC-normalize then lowercase. Used everywhere substring match runs.

    NFKC folds fullwidth letters (ＡＢＣ → ABC), halfwidth katakana, ligatures,
    etc. into their canonical halfwidth forms before lowercasing. CJK ideographs
    pass through unchanged — Python `in` then handles CJK substring directly
    without a tokenizer.
    """
    return unicodedata.normalize("NFKC", s).lower()


def _score_page(fields: dict, keywords_lc: list[str]) -> int:
    """Return cumulative score for `fields` against NFKC-lowered keywords.

    Pattern A defensive guard: if `tags` is not a list (e.g. a future scalar
    field leaked through the mini-parser as a string), coerce to [] so we
    don't iterate char-by-char on a string and produce nonsense substrings.
    """
    title_lc = _norm(str(fields.get("title", "")))
    summary_lc = _norm(str(fields.get("summary", "")))
    raw_tags = fields.get("tags", []) or []
    if not isinstance(raw_tags, list):
        raw_tags = []
    tags_lc = [_norm(str(t)) for t in raw_tags]

    score = 0
    for kw in keywords_lc:
        if not kw:
            continue
        if kw in title_lc:
            score += _W_TITLE
        if any(kw in tag for tag in tags_lc):
            score += _W_TAG
        if kw in summary_lc:
            score += _W_SUMMARY
    return score


# ---------------------------------------------------------------------------
# Vault walk
# ---------------------------------------------------------------------------

def _iter_wiki_pages(vault_root: Path, type_filter: str | None = None):
    """Yield (rel_path_str, abs_path) for every .md under vault/wiki/<subdir>/.

    If `type_filter` is given (e.g. "entities"), restrict to wiki/<type>/*.md
    only; unknown type names yield nothing.
    """
    wiki = vault_root / "wiki"
    if not wiki.is_dir():
        return
    if type_filter is not None:
        subdirs = (type_filter,) if type_filter in _WIKI_SUBDIRS else ()
    else:
        subdirs = _WIKI_SUBDIRS
    for sub in subdirs:
        subdir = wiki / sub
        if not subdir.is_dir():
            continue
        for md in sorted(subdir.glob("*.md")):
            rel = md.relative_to(vault_root).as_posix()
            yield rel, md


# ---------------------------------------------------------------------------
# Public API (used by the test suite)
# ---------------------------------------------------------------------------

def query(
    vault_root: Path,
    keywords: list[str],
    top: int = 5,
    type_filter: str | None = None,
) -> list[dict]:
    """Walk vault/wiki/, score against `keywords`, return top-K rows.

    Edge cases:
      - Empty `keywords` (or list of empty strings) → `[]` (no scoring).
      - Pages missing the `summary:` frontmatter field are skipped from
        candidates entirely, even if title/tag would have scored — the
        Tier 1 contract requires summary to surface to the LLM caller.
      - 0 scored candidates → `[]` (not an error).
      - `type_filter` set → only wiki/<type>/*.md considered.

    Empty result list when nothing scores > 0.
    """
    keywords_lc = [_norm(k) for k in keywords if k]
    if not keywords_lc:
        return []

    rows: list[dict] = []

    for rel, abs_path in _iter_wiki_pages(Path(vault_root), type_filter=type_filter):
        try:
            text = abs_path.read_text(encoding="utf-8", errors="replace")
        except OSError:
            continue

        fields = _parse_frontmatter(text)
        if not fields:
            continue

        # Tier 1 contract: page must carry a `summary:` field for the
        # caller LLM to act on. Pages without it are incomplete and
        # excluded from candidates.
        if "summary" not in fields or not str(fields.get("summary", "")).strip():
            continue

        score = _score_page(fields, keywords_lc)
        if score <= 0:
            continue

        # Pattern A defensive guard for emitted tags too — never leak a
        # non-list into JSON output.
        raw_tags = fields.get("tags", []) or []
        if not isinstance(raw_tags, list):
            raw_tags = []

        rows.append({
            "path": rel,
            "title": fields.get("title", ""),
            "type": fields.get("type", ""),
            "summary": fields.get("summary", ""),
            "tags": raw_tags,
            "score": score,
        })

    # Descending score; stable tie-breaker by path for deterministic output.
    rows.sort(key=lambda r: (-r["score"], r["path"]))
    return rows[:top]


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def _parse_args(argv: list[str]) -> argparse.Namespace:
    p = argparse.ArgumentParser(
        description=(
            "Tier 1 wiki-query frontmatter scorer "
            "(NFKC-normalized substring; CJK + multilingual)."
        ),
    )
    p.add_argument(
        "--keywords",
        required=True,
        help="Comma-separated keywords (NFKC-lowercased before match).",
    )
    p.add_argument(
        "--top",
        type=int,
        default=5,
        help="Max rows to return (default: 5).",
    )
    p.add_argument(
        "--vault-root",
        required=True,
        help="Absolute path to the vault root (must contain a wiki/ subdir).",
    )
    p.add_argument(
        "--type",
        default=None,
        choices=_WIKI_SUBDIRS,
        help=(
            "Optional: restrict walk to wiki/<TYPE>/*.md only. "
            "Absent → cross-category top-K."
        ),
    )
    return p.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = _parse_args(argv if argv is not None else sys.argv[1:])

    vault = Path(args.vault_root).resolve()
    if not (vault / "wiki").is_dir():
        print(
            f"Error: {vault} does not contain a 'wiki/' subdirectory",
            file=sys.stderr,
        )
        return 2

    keywords = [k.strip() for k in args.keywords.split(",") if k.strip()]
    rows = query(
        vault_root=vault,
        keywords=keywords,
        top=args.top,
        type_filter=args.type,
    )

    print(json.dumps(rows, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
