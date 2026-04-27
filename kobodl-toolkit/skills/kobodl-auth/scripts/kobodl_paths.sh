#!/usr/bin/env bash
# kobodl_paths.sh — resolve and emit canonical paths for the toolkit.
#
# Source-able OR runnable. When sourced (`source kobodl_paths.sh`), it sets
# variables in the caller's shell. When run as a script, it prints them as
# `KEY=VALUE` lines on stdout.
#
# Four-category split (XDG-respecting):
#   KOBODL_HOME      ~/.config/claude-kobodl/       config — auth (chmod 700)
#   KOBODL_DATA      ~/.local/share/claude-kobodl/  data — binary, persistent state
#   KOBODL_CACHE     ~/.cache/claude-kobodl/        cache — regenerable, droppable
#   KOBODL_DOWNLOADS ~/Books/kobo/                  user-visible EPUB downloads
#
# Resolution order (highest priority first):
#   1. KOBODL_* env vars (toolkit-specific overrides)
#   2. XDG_CONFIG_HOME / XDG_DATA_HOME / XDG_CACHE_HOME (XDG Base Dir Spec)
#   3. Defaults above
#
# Outputs (and exports when sourced):
#   KOBODL_HOME             config dir
#   KOBODL_DATA             data dir
#   KOBODL_CACHE            cache dir
#   KOBODL_DOWNLOADS        download dir
#   KOBODL_BINARY           absolute path to kobodl-macos
#   KOBODL_CONFIG           absolute path to kobodl.json
#   KOBODL_LIBRARY_JSON     absolute path to library.json (cached export)
#   KOBODL_MARKDOWN_DIR     absolute path to extracted markdown root
#   KOBODL_TMPDIR           absolute path to tmp/ (set TMPDIR to this)

_xdg_config="${XDG_CONFIG_HOME:-$HOME/.config}"
_xdg_data="${XDG_DATA_HOME:-$HOME/.local/share}"
_xdg_cache="${XDG_CACHE_HOME:-$HOME/.cache}"

KOBODL_HOME="${KOBODL_HOME:-$_xdg_config/claude-kobodl}"
KOBODL_DATA="${KOBODL_DATA:-$_xdg_data/claude-kobodl}"
KOBODL_CACHE="${KOBODL_CACHE:-$_xdg_cache/claude-kobodl}"
KOBODL_DOWNLOADS="${KOBODL_DOWNLOADS:-$HOME/Books/kobo}"

KOBODL_BINARY="$KOBODL_DATA/bin/kobodl-macos"
KOBODL_CONFIG="$KOBODL_HOME/kobodl.json"
KOBODL_TMPDIR="$KOBODL_DATA/tmp"

# Cache-tier paths (regenerable derived data)
KOBODL_LIBRARY_JSON="$KOBODL_CACHE/library.json"
KOBODL_MARKDOWN_DIR="$KOBODL_CACHE/markdown"

unset _xdg_config _xdg_data _xdg_cache

# Detect: was this script sourced or executed?
# Bash: ${BASH_SOURCE[0]} != ${0} when sourced. Zsh: ZSH_EVAL_CONTEXT contains "file".
_kobodl_paths_sourced=false
if [[ -n "${BASH_SOURCE[0]:-}" && "${BASH_SOURCE[0]}" != "${0}" ]]; then
    _kobodl_paths_sourced=true
elif [[ -n "${ZSH_EVAL_CONTEXT:-}" && "$ZSH_EVAL_CONTEXT" == *:file* ]]; then
    _kobodl_paths_sourced=true
fi

if [[ "$_kobodl_paths_sourced" == true ]]; then
    export KOBODL_HOME KOBODL_DATA KOBODL_CACHE KOBODL_DOWNLOADS \
           KOBODL_BINARY KOBODL_CONFIG KOBODL_LIBRARY_JSON \
           KOBODL_MARKDOWN_DIR KOBODL_TMPDIR
    unset _kobodl_paths_sourced
else
    cat <<EOF
KOBODL_HOME=$KOBODL_HOME
KOBODL_DATA=$KOBODL_DATA
KOBODL_CACHE=$KOBODL_CACHE
KOBODL_DOWNLOADS=$KOBODL_DOWNLOADS
KOBODL_BINARY=$KOBODL_BINARY
KOBODL_CONFIG=$KOBODL_CONFIG
KOBODL_LIBRARY_JSON=$KOBODL_LIBRARY_JSON
KOBODL_MARKDOWN_DIR=$KOBODL_MARKDOWN_DIR
KOBODL_TMPDIR=$KOBODL_TMPDIR
EOF
    unset _kobodl_paths_sourced
fi
