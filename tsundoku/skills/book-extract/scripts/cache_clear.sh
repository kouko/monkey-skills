#!/usr/bin/env bash
# cache_clear.sh — wipe the toolkit's cache (regenerable derived data).
#
# By default removes:
#   $TSUNDOKU_MARKDOWN_DIR/*    (all extracted-markdown subdirs)
#   $TSUNDOKU_KOBO_LIBRARY_JSON      (cached library export)
#
# Auth ($TSUNDOKU_ROOT/kobo/auth/), binary ($TSUNDOKU_ROOT/kobo/bin/),
# and downloaded EPUBs ($TSUNDOKU_DOWNLOADS) are NEVER touched.
#
# Usage:
#   cache_clear.sh [--markdown-only|--library-only] [--dry-run] [--book SLUG]
#
# Options:
#   --markdown-only   wipe only the markdown directory; keep library.json
#   --library-only    wipe only library.json; keep markdown
#   --book SLUG       wipe only one book's markdown dir (e.g. 一九八四-b9152ffe)
#   --dry-run         print what would be deleted, do not delete
#
# Exit codes:
#   0  done
#   2  argument error

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PATHS_SCRIPT="$SCRIPT_DIR/tsundoku_paths.sh"
# shellcheck source=./tsundoku_paths.sh
source "$PATHS_SCRIPT"

MODE="all"
DRY_RUN=false
BOOK=""

while [[ $# -gt 0 ]]; do
    case "$1" in
        --markdown-only) MODE="markdown"; shift ;;
        --library-only)  MODE="library"; shift ;;
        --book)          BOOK="$2"; shift 2 ;;
        --dry-run)       DRY_RUN=true; shift ;;
        -h|--help) grep '^#' "$0" | sed 's/^# \{0,1\}//'; exit 0 ;;
        *) echo "kobodl_cache_clear: unknown arg: $1" >&2; exit 2 ;;
    esac
done

run() {
    local desc="$1"; shift
    if [[ "$DRY_RUN" == true ]]; then
        echo "[dry-run] would $desc: $*"
    else
        echo "[run] $desc: $*"
        "$@"
    fi
}

# Per-book wipe takes priority; ignores --mode
if [[ -n "$BOOK" ]]; then
    target="$TSUNDOKU_MARKDOWN_DIR/$BOOK"
    if [[ ! -d "$target" ]]; then
        echo "kobodl_cache_clear: no such book dir: $target" >&2
        exit 0
    fi
    run "remove book dir" rm -rf -- "$target"
    exit 0
fi

if [[ "$MODE" == "all" || "$MODE" == "markdown" ]]; then
    if [[ -d "$TSUNDOKU_MARKDOWN_DIR" ]]; then
        # delete contents but keep the directory itself
        for entry in "$TSUNDOKU_MARKDOWN_DIR"/*; do
            [[ -e "$entry" ]] || continue
            run "remove markdown entry" rm -rf -- "$entry"
        done
    else
        echo "[skip] markdown dir does not exist: $TSUNDOKU_MARKDOWN_DIR"
    fi
fi

if [[ "$MODE" == "all" || "$MODE" == "library" ]]; then
    if [[ -f "$TSUNDOKU_KOBO_LIBRARY_JSON" ]]; then
        run "remove library.json" rm -f -- "$TSUNDOKU_KOBO_LIBRARY_JSON"
    else
        echo "[skip] library.json does not exist: $TSUNDOKU_KOBO_LIBRARY_JSON"
    fi
fi

echo
echo "[done] cache cleared (mode: $MODE${BOOK:+, book: $BOOK})"
echo "       auth ($TSUNDOKU_ROOT/kobo/auth/), binary ($TSUNDOKU_ROOT/kobo/bin/),"
echo "       and downloads ($TSUNDOKU_DOWNLOADS) untouched"
