#!/usr/bin/env bash
# tsundoku_paths.sh — resolve and emit canonical paths for the tsundoku plugin.
#
# Source-able OR runnable. When sourced (`source tsundoku_paths.sh`), it sets
# variables in the caller's shell. When run as a script, it prints them as
# `KEY=VALUE` lines on stdout.
#
# Single-root layout (Option B):
#
#   ~/.tsundoku/                    ← TSUNDOKU_ROOT
#   ├── auth/                        chmod 700
#   │   └── kobodl.json              chmod 600  (Kobo session credentials)
#   ├── bin/kobodl-macos             14 MB upstream binary
#   ├── tmp/                         TMPDIR override (PYI-1270 fix)
#   └── cache/                       regenerable derived data, wipe-able
#       ├── library.json             cached `book list --export-library`
#       └── markdown/<book>/...      EPUB → chunked Markdown
#
#   ~/Books/kobo/                   ← TSUNDOKU_DOWNLOADS (user-visible EPUBs)
#
# Two decision-point env vars override the layout:
#   TSUNDOKU_ROOT       (default: ~/.tsundoku)
#   TSUNDOKU_DOWNLOADS  (default: ~/Books/kobo)
#
# Five derived vars are computed and exported for convenience — DO NOT set
# them directly. Override TSUNDOKU_ROOT instead:
#   TSUNDOKU_CONFIG, TSUNDOKU_BINARY, TSUNDOKU_LIBRARY_JSON,
#   TSUNDOKU_MARKDOWN_DIR, TSUNDOKU_TMPDIR

TSUNDOKU_ROOT="${TSUNDOKU_ROOT:-$HOME/.tsundoku}"
TSUNDOKU_DOWNLOADS="${TSUNDOKU_DOWNLOADS:-$HOME/Books/kobo}"

TSUNDOKU_CONFIG="$TSUNDOKU_ROOT/auth/kobodl.json"
TSUNDOKU_BINARY="$TSUNDOKU_ROOT/bin/kobodl-macos"
TSUNDOKU_LIBRARY_JSON="$TSUNDOKU_ROOT/cache/library.json"
TSUNDOKU_MARKDOWN_DIR="$TSUNDOKU_ROOT/cache/markdown"
TSUNDOKU_TMPDIR="$TSUNDOKU_ROOT/tmp"

# Detect: was this script sourced or executed?
_tsundoku_paths_sourced=false
if [[ -n "${BASH_SOURCE[0]:-}" && "${BASH_SOURCE[0]}" != "${0}" ]]; then
    _tsundoku_paths_sourced=true
elif [[ -n "${ZSH_EVAL_CONTEXT:-}" && "$ZSH_EVAL_CONTEXT" == *:file* ]]; then
    _tsundoku_paths_sourced=true
fi

if [[ "$_tsundoku_paths_sourced" == true ]]; then
    export TSUNDOKU_ROOT TSUNDOKU_DOWNLOADS \
           TSUNDOKU_CONFIG TSUNDOKU_BINARY TSUNDOKU_LIBRARY_JSON \
           TSUNDOKU_MARKDOWN_DIR TSUNDOKU_TMPDIR
    unset _tsundoku_paths_sourced
else
    cat <<EOF
TSUNDOKU_ROOT=$TSUNDOKU_ROOT
TSUNDOKU_DOWNLOADS=$TSUNDOKU_DOWNLOADS
TSUNDOKU_CONFIG=$TSUNDOKU_CONFIG
TSUNDOKU_BINARY=$TSUNDOKU_BINARY
TSUNDOKU_LIBRARY_JSON=$TSUNDOKU_LIBRARY_JSON
TSUNDOKU_MARKDOWN_DIR=$TSUNDOKU_MARKDOWN_DIR
TSUNDOKU_TMPDIR=$TSUNDOKU_TMPDIR
EOF
    unset _tsundoku_paths_sourced
fi
