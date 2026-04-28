#!/usr/bin/env bash
# tsundoku_paths.sh — resolve and emit canonical paths for the tsundoku plugin.
#
# Source-able OR runnable. When sourced (`source tsundoku_paths.sh`), it sets
# variables in the caller's shell. When run as a script, it prints them as
# `KEY=VALUE` lines on stdout.
#
# Layout (single root, per-platform subdirs):
#
#   ~/.tsundoku/                    ← TSUNDOKU_ROOT
#   ├── kobo/                        Kobo platform state
#   │   ├── auth/                     chmod 700
#   │   │   └── kobodl.json           chmod 600  (Kobo session credentials)
#   │   └── bin/kobodl-macos          14 MB upstream binary
#   ├── tmp/                         shared TMPDIR override (PYI-1270 fix)
#   └── cache/                       regenerable derived data, wipe-able
#       ├── kobo/library.json         cached `book list --export-library`
#       └── markdown/<book>/...       EPUB → chunked Markdown (platform-agnostic)
#
#   ~/Books/kobo/                   ← TSUNDOKU_DOWNLOADS (user-visible EPUBs)
#
# Future Kindle / Apple Books siblings would mirror under kobo/ as kindle/, etc.
#
# Two decision-point env vars override the layout:
#   TSUNDOKU_ROOT       (default: ~/.tsundoku)
#   TSUNDOKU_DOWNLOADS  (default: ~/Books/kobo)
#
# Derived vars are computed and exported for convenience — DO NOT set them
# directly. Override TSUNDOKU_ROOT instead.
#
#   Plugin-wide:
#     TSUNDOKU_TMPDIR
#     TSUNDOKU_MARKDOWN_DIR     (cache/markdown — platform-agnostic)
#
#   Kobo-specific (TSUNDOKU_KOBO_* namespace):
#     TSUNDOKU_KOBO_CONFIG       Kobo session credentials (kobodl.json)
#     TSUNDOKU_KOBO_BINARY       kobodl binary
#     TSUNDOKU_KOBO_LIBRARY_JSON cached library export

TSUNDOKU_ROOT="${TSUNDOKU_ROOT:-$HOME/.tsundoku}"
TSUNDOKU_DOWNLOADS="${TSUNDOKU_DOWNLOADS:-$HOME/Books/kobo}"

# Plugin-wide derived
TSUNDOKU_TMPDIR="$TSUNDOKU_ROOT/tmp"
TSUNDOKU_MARKDOWN_DIR="$TSUNDOKU_ROOT/cache/markdown"

# Kobo-specific derived
TSUNDOKU_KOBO_CONFIG="$TSUNDOKU_ROOT/kobo/auth/kobodl.json"
TSUNDOKU_KOBO_BINARY="$TSUNDOKU_ROOT/kobo/bin/kobodl-macos"
TSUNDOKU_KOBO_LIBRARY_JSON="$TSUNDOKU_ROOT/cache/kobo/library.json"

# Detect: was this script sourced or executed?
_tsundoku_paths_sourced=false
if [[ -n "${BASH_SOURCE[0]:-}" && "${BASH_SOURCE[0]}" != "${0}" ]]; then
    _tsundoku_paths_sourced=true
elif [[ -n "${ZSH_EVAL_CONTEXT:-}" && "$ZSH_EVAL_CONTEXT" == *:file* ]]; then
    _tsundoku_paths_sourced=true
fi

if [[ "$_tsundoku_paths_sourced" == true ]]; then
    export TSUNDOKU_ROOT TSUNDOKU_DOWNLOADS \
           TSUNDOKU_TMPDIR TSUNDOKU_MARKDOWN_DIR \
           TSUNDOKU_KOBO_CONFIG TSUNDOKU_KOBO_BINARY TSUNDOKU_KOBO_LIBRARY_JSON
    unset _tsundoku_paths_sourced
else
    cat <<EOF
TSUNDOKU_ROOT=$TSUNDOKU_ROOT
TSUNDOKU_DOWNLOADS=$TSUNDOKU_DOWNLOADS
TSUNDOKU_TMPDIR=$TSUNDOKU_TMPDIR
TSUNDOKU_MARKDOWN_DIR=$TSUNDOKU_MARKDOWN_DIR
TSUNDOKU_KOBO_CONFIG=$TSUNDOKU_KOBO_CONFIG
TSUNDOKU_KOBO_BINARY=$TSUNDOKU_KOBO_BINARY
TSUNDOKU_KOBO_LIBRARY_JSON=$TSUNDOKU_KOBO_LIBRARY_JSON
EOF
    unset _tsundoku_paths_sourced
fi
