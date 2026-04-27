#!/usr/bin/env bash
# kobodl_paths.sh — resolve and emit canonical paths for the toolkit.
#
# Source-able OR runnable. When sourced (`source kobodl_paths.sh`), it sets
# variables in the caller's shell. When run as a script, it prints them as
# `KEY=VALUE` lines on stdout.
#
# Resolution order (highest priority first):
#   1. KOBODL_HOME / KOBODL_DATA / KOBODL_DOWNLOADS env vars
#   2. XDG_CONFIG_HOME / XDG_DATA_HOME (XDG Base Dir Spec)
#   3. Defaults: ~/.config/claude-kobodl, ~/.local/share/claude-kobodl, ~/Books/kobo
#
# Outputs (and exports when sourced):
#   KOBODL_HOME           config dir   (holds kobodl.json)
#   KOBODL_DATA           data dir     (holds bin/, library.json, tmp/)
#   KOBODL_DOWNLOADS      download dir (where EPUBs land)
#   KOBODL_BINARY         absolute path to kobodl-macos
#   KOBODL_CONFIG         absolute path to kobodl.json
#   KOBODL_LIBRARY_JSON   absolute path to library.json
#   KOBODL_TMPDIR         absolute path to tmp/ (set TMPDIR to this)

_xdg_config="${XDG_CONFIG_HOME:-$HOME/.config}"
_xdg_data="${XDG_DATA_HOME:-$HOME/.local/share}"

KOBODL_HOME="${KOBODL_HOME:-$_xdg_config/claude-kobodl}"
KOBODL_DATA="${KOBODL_DATA:-$_xdg_data/claude-kobodl}"
KOBODL_DOWNLOADS="${KOBODL_DOWNLOADS:-$HOME/Books/kobo}"

KOBODL_BINARY="$KOBODL_DATA/bin/kobodl-macos"
KOBODL_CONFIG="$KOBODL_HOME/kobodl.json"
KOBODL_LIBRARY_JSON="$KOBODL_DATA/library.json"
KOBODL_TMPDIR="$KOBODL_DATA/tmp"

unset _xdg_config _xdg_data

# Detect: was this script sourced or executed?
# Bash: ${BASH_SOURCE[0]} != ${0} when sourced. Zsh: ZSH_EVAL_CONTEXT contains "file".
_kobodl_paths_sourced=false
if [[ -n "${BASH_SOURCE[0]:-}" && "${BASH_SOURCE[0]}" != "${0}" ]]; then
    _kobodl_paths_sourced=true
elif [[ -n "${ZSH_EVAL_CONTEXT:-}" && "$ZSH_EVAL_CONTEXT" == *:file* ]]; then
    _kobodl_paths_sourced=true
fi

if [[ "$_kobodl_paths_sourced" == true ]]; then
    export KOBODL_HOME KOBODL_DATA KOBODL_DOWNLOADS \
           KOBODL_BINARY KOBODL_CONFIG KOBODL_LIBRARY_JSON KOBODL_TMPDIR
    unset _kobodl_paths_sourced
else
    cat <<EOF
KOBODL_HOME=$KOBODL_HOME
KOBODL_DATA=$KOBODL_DATA
KOBODL_DOWNLOADS=$KOBODL_DOWNLOADS
KOBODL_BINARY=$KOBODL_BINARY
KOBODL_CONFIG=$KOBODL_CONFIG
KOBODL_LIBRARY_JSON=$KOBODL_LIBRARY_JSON
KOBODL_TMPDIR=$KOBODL_TMPDIR
EOF
    unset _kobodl_paths_sourced
fi
