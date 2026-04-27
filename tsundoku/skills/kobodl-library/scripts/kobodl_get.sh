#!/usr/bin/env bash
# kobodl_get.sh — download books by RevisionId, idempotent.
#
# Takes one or more RevisionIds from command-line args OR stdin (one per line).
# Skips books whose <id8>.epub already exists in $TSUNDOKU_DOWNLOADS.
# Optionally runs Calibre to produce a matching PDF.
#
# Usage:
#   kobodl_get.sh [options] REVISION_ID [REVISION_ID ...]
#   echo REVISION_ID | kobodl_get.sh [options]
#   kobodl_query.py ... --format ids | kobodl_get.sh [options]
#
# Options:
#   --convert-pdf      after each download, convert EPUB → PDF via Calibre
#                      (requires /Applications/calibre.app)
#   --output-dir DIR   override $TSUNDOKU_DOWNLOADS for this run
#   --user EMAIL       scope to a specific Kobo user (multi-user configs)
#   --dry-run          print "would download X" without calling kobodl
#   --quiet            only print resulting filenames to stdout
#
# Output (stdout): one line per book actually downloaded — the EPUB path.
# Progress and skip messages go to stderr.
#
# Exit codes:
#   0  all attempted books succeeded (or were already present)
#   1  one or more downloads failed (others may have succeeded)
#   2  argument or precondition error
#   3  binary or auth missing

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PATHS_SCRIPT="$SCRIPT_DIR/../../../lib/tsundoku_paths.sh"
if [[ ! -f "$PATHS_SCRIPT" ]]; then
    echo "kobodl_get: cannot locate tsundoku_paths.sh at $PATHS_SCRIPT" >&2
    exit 2
fi
# shellcheck source=../../lib/tsundoku_paths.sh
source "$PATHS_SCRIPT"

CONVERT_PDF=false
DRY_RUN=false
QUIET=false
USER_SCOPE=""
OUTPUT_DIR="$TSUNDOKU_DOWNLOADS"
CALIBRE="/Applications/calibre.app/Contents/MacOS/ebook-convert"

POSITIONAL=()
while [[ $# -gt 0 ]]; do
    case "$1" in
        --convert-pdf)  CONVERT_PDF=true; shift ;;
        --dry-run)      DRY_RUN=true; shift ;;
        --quiet)        QUIET=true; shift ;;
        --output-dir)   OUTPUT_DIR="$2"; shift 2 ;;
        --user)         USER_SCOPE="$2"; shift 2 ;;
        -h|--help)
            grep '^#' "$0" | sed 's/^# \{0,1\}//'; exit 0 ;;
        --) shift; POSITIONAL+=("$@"); break ;;
        -*) echo "kobodl_get: unknown option: $1" >&2; exit 2 ;;
        *)  POSITIONAL+=("$1"); shift ;;
    esac
done

# Pre-flight checks
if [[ ! -x "$TSUNDOKU_BINARY" ]]; then
    echo "kobodl_get: binary not installed at $TSUNDOKU_BINARY" >&2
    echo "            run kobodl-auth/scripts/kobodl_install.sh" >&2
    exit 3
fi
if [[ ! -f "$TSUNDOKU_CONFIG" ]]; then
    echo "kobodl_get: no auth at $TSUNDOKU_CONFIG" >&2
    echo "            run kobodl-auth/scripts/kobodl_login.sh add" >&2
    exit 3
fi

mkdir -p "$OUTPUT_DIR"
export TMPDIR="$TSUNDOKU_TMPDIR"
mkdir -p "$TSUNDOKU_TMPDIR"

# Collect IDs: positional first, then stdin (only if stdin is a pipe/file)
IDS=("${POSITIONAL[@]}")
if [[ ! -t 0 ]]; then
    while IFS= read -r line; do
        line="${line%%#*}"           # strip inline comments
        line="${line//[$'\t\r ']/}"  # strip whitespace
        [[ -n "$line" ]] && IDS+=("$line")
    done
fi

if [[ ${#IDS[@]} -eq 0 ]]; then
    echo "kobodl_get: no RevisionIds supplied (args or stdin)" >&2
    exit 2
fi

UUID_RE='^[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}$'

ok=0
skip=0
fail=0
total=${#IDS[@]}
idx=0

USER_ARGS=()
[[ -n "$USER_SCOPE" ]] && USER_ARGS=(-u "$USER_SCOPE")

for id in "${IDS[@]}"; do
    idx=$((idx + 1))
    if [[ ! "$id" =~ $UUID_RE ]]; then
        echo "[$idx/$total] [skip-invalid] not a UUID: $id" >&2
        fail=$((fail + 1))
        continue
    fi

    short_id="${id:0:8}"
    existing=( "$OUTPUT_DIR"/*"${short_id}.epub" )

    if [[ -e "${existing[0]:-}" ]]; then
        epub="${existing[0]}"
        $QUIET || echo "[$idx/$total] [skip] $id → ${epub##*/}" >&2
        skip=$((skip + 1))
    else
        if [[ "$DRY_RUN" == true ]]; then
            echo "[$idx/$total] [dry-run] would download $id" >&2
            continue
        fi
        $QUIET || echo "[$idx/$total] [get] $id" >&2
        if "$TSUNDOKU_BINARY" --config "$TSUNDOKU_CONFIG" "${USER_ARGS[@]}" \
                book get --output-dir "$OUTPUT_DIR" "$id" >&2
        then
            new_files=( "$OUTPUT_DIR"/*"${short_id}.epub" )
            if [[ -e "${new_files[0]:-}" ]]; then
                epub="${new_files[0]}"
                ok=$((ok + 1))
            else
                echo "[$idx/$total] [fail] download succeeded but EPUB not found for $id" >&2
                fail=$((fail + 1))
                continue
            fi
        else
            echo "[$idx/$total] [fail] kobodl get exited non-zero for $id" >&2
            fail=$((fail + 1))
            continue
        fi
    fi

    # Echo the EPUB path so callers can chain
    echo "$epub"

    # Optional PDF conversion
    if [[ "$CONVERT_PDF" == true && "$DRY_RUN" != true ]]; then
        pdf="${epub%.epub}.pdf"
        if [[ -f "$pdf" ]]; then
            $QUIET || echo "[$idx/$total] [pdf-skip] $pdf already exists" >&2
        elif [[ ! -x "$CALIBRE" ]]; then
            echo "[$idx/$total] [pdf-skip] Calibre not at $CALIBRE" >&2
        else
            $QUIET || echo "[$idx/$total] [pdf] converting ..." >&2
            if "$CALIBRE" "$epub" "$pdf" >/dev/null 2>&1; then
                $QUIET || echo "[$idx/$total] [pdf] $pdf" >&2
            else
                echo "[$idx/$total] [pdf-fail] Calibre returned non-zero" >&2
            fi
        fi
    fi
done

# Summary to stderr
echo "" >&2
echo "[summary] downloaded=$ok  already-present=$skip  failed=$fail  total=$total" >&2
[[ "$fail" -eq 0 ]] && exit 0 || exit 1
