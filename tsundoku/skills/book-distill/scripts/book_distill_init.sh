#!/usr/bin/env bash
# book_distill_init.sh — bootstrap a book-distill working directory from an
# already-extracted book in $TSUNDOKU_MARKDOWN_DIR.
#
# This is the bridge between book-extract (which produces chapter markdown
# + metadata.json) and book-distill (which expects a working directory
# under $TSUNDOKU_ROOT/cache/distilled/<slug>/).
#
# What this script does NOT do:
#   - It does not run any LLM step. Distillation is Claude-driven, following
#     the methodology + extractor prompts.
#   - It does not write BOOK_OVERVIEW.md content. It only sets up the
#     working directory and seeds metadata.snapshot.json so the LLM has a
#     starting point.
#
# What it DOES:
#   - Verifies the source book has been processed by book-extract
#   - Creates $TSUNDOKU_ROOT/cache/distilled/<slug>/ with:
#       candidates/ rejected/ (empty subdirs, audit-trail-ready)
#       BOOK_OVERVIEW.md.draft   ← copy of template, ready for Stage 0 fill
#       metadata.snapshot.json   ← copy of book-extract's metadata.json
#       chapters.list            ← list of chapter MD paths in spine order
#
# Usage:
#   bash book_distill_init.sh <book-slug-id8>
#   bash book_distill_init.sh 一九八四-b9152ffe
#
# Exit codes:
#   0  ready
#   1  source book missing
#   2  argument error
#   3  pre-existing distill dir (use --force to overwrite)

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PATHS_SCRIPT="$SCRIPT_DIR/../../../lib/tsundoku_paths.sh"
# shellcheck source=../../../lib/tsundoku_paths.sh
source "$PATHS_SCRIPT"

FORCE=false
SLUG=""

while [[ $# -gt 0 ]]; do
    case "$1" in
        --force) FORCE=true; shift ;;
        -h|--help) grep '^#' "$0" | sed 's/^# \{0,1\}//'; exit 0 ;;
        -*) echo "book_distill_init: unknown option: $1" >&2; exit 2 ;;
        *) SLUG="$1"; shift ;;
    esac
done

if [[ -z "$SLUG" ]]; then
    echo "book_distill_init: missing <book-slug-id8>" >&2
    echo "usage: $0 <book-slug-id8> [--force]" >&2
    exit 2
fi

SRC="$TSUNDOKU_MARKDOWN_DIR/$SLUG"
DST="$TSUNDOKU_ROOT/cache/distilled/$SLUG"
TEMPLATE_DIR="$SCRIPT_DIR/../templates"

# Verify source
if [[ ! -d "$SRC" ]]; then
    cat >&2 <<EOF
book_distill_init: source book directory not found:
                   $SRC

Did you run book-extract first?

  source ${TSUNDOKU_ROOT%/*}/lib/tsundoku_paths.sh
  EPUB="\$TSUNDOKU_DOWNLOADS/<author> - <title> <id8>.epub"
  python3 .../book-extract/scripts/epub_to_markdown.py --epub "\$EPUB" \\
      --strip-images --strip-frontmatter
EOF
    exit 1
fi

if [[ ! -f "$SRC/metadata.json" ]]; then
    echo "book_distill_init: $SRC has no metadata.json — re-run book-extract" >&2
    exit 1
fi

if [[ ! -f "$SRC/index.md" ]]; then
    echo "book_distill_init: $SRC has no index.md — re-run book-extract" >&2
    exit 1
fi

# Check for pre-existing
if [[ -d "$DST" && "$FORCE" != true ]]; then
    cat >&2 <<EOF
book_distill_init: distill dir already exists:
                   $DST
                   Use --force to overwrite (will preserve audit trail).
EOF
    exit 3
fi

# Create
mkdir -p "$DST/candidates" "$DST/rejected"

# Seed metadata.snapshot.json
cp "$SRC/metadata.json" "$DST/metadata.snapshot.json"

# Seed chapter list (in spine order, from index.md table)
# index.md has a markdown table where the 4th column has [filename](filename)
# We extract just the filename, skip skipped/missing rows.
{
    echo "# Chapter spine order (extracted from index.md)"
    echo ""
    grep -E '^\| [0-9]+ \|' "$SRC/index.md" | \
        awk -F'|' '{print $5}' | \
        grep -oE '\[[^]]+\]' | \
        tr -d '[]' || true
} > "$DST/chapters.list"

# Copy the BOOK_OVERVIEW template as a draft (Claude will fill it during Stage 0)
cp "$TEMPLATE_DIR/BOOK_OVERVIEW.md.template" "$DST/BOOK_OVERVIEW.md.draft"

# Sentinel marker
cat > "$DST/.book-distill-state" <<EOF
stage: 0
initialized_at: $(date -Iseconds)
source_book_slug: $SLUG
source_markdown_dir: $SRC
EOF

cat <<EOF
[init] book-distill working directory ready:
       $DST

Source:        $SRC
Title:         $(python3 -c "import json; print(json.load(open('$SRC/metadata.json'))['title'])")
Authors:       $(python3 -c "import json; print(', '.join(json.load(open('$SRC/metadata.json'))['authors']))")
Total tokens:  $(python3 -c "import json; print(f\"{json.load(open('$SRC/metadata.json'))['total_tokens']:,}\")")
Chapters:      $(grep -cE '^\| [0-9]+ \|' "$SRC/index.md" || echo "?")

Next: Claude follows book-distill's SKILL.md, starting with Stage 0
(Adler analytical read), filling BOOK_OVERVIEW.md.draft → BOOK_OVERVIEW.md.

Cache layout:
  $DST/
  ├── BOOK_OVERVIEW.md.draft   ← Claude fills this (Stage 0)
  ├── metadata.snapshot.json   ← reference data for Stage 0
  ├── chapters.list            ← spine order, for chapter iteration
  ├── candidates/              ← Stage 1 outputs
  ├── rejected/                ← Stage 1.5 audit
  └── .book-distill-state      ← pipeline state marker
EOF
