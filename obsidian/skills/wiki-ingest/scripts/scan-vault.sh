#!/bin/sh
# scan-vault.sh — Emit absolute paths of vault .md files eligible for wiki ingest.
#
# Usage:
#   scan-vault.sh <vault-root>
#
# Config: reads <vault-root>/.obsidian-wiki.config (shell-sourceable, NOT .env)
#         to set OBSIDIAN_WIKI_EXCLUDE_DIRS. Falls back to env var if config
#         file is missing (useful for testing).
#
# Optional env: EXTRA_SYS_EXCLUDES (newline-separated) for one-off invocations
#               to add system-level exclusions without editing this script.
#
# Exit codes:
#   0  on success (always; empty output is valid for an empty vault)
#   1  on bad usage / missing vault dir
#
# Behavior:
#   - Scans vault root for top-level directories
#   - Prunes directories matching the system blacklist OR OBSIDIAN_WIKI_EXCLUDE_DIRS
#   - Recurses into remaining top-level dirs to find *.md files
#   - Also includes loose *.md files at the vault root (depth-1)
#
# Match rule:
#   Top-level only, case-sensitive. Nested directories with the same name
#   (e.g. projects/old/daily/) are NOT excluded.
#
# Glob patterns:
#   Each entry in OBSIDIAN_WIKI_EXCLUDE_DIRS is a shell glob, matched via
#   `case ... in <pattern>)`. Examples:
#     daily            literal exact match
#     _*               any name starting with underscore (e.g. _raw, _archive)
#     temp?            `temp1`, `temp2`, `tempX` (single wildcard char)
#     [Aa]rchive       case-variant: matches `Archive` or `archive`
#     *.bak            any name ending in .bak
#
# Multi-line value format (NEW in v3.8.0):
#   OBSIDIAN_WIKI_EXCLUDE_DIRS uses one pattern per line within a quoted string,
#   so patterns may contain commas, spaces, CJK, or any character except newline.
#   Example in .obsidian-wiki.config:
#     OBSIDIAN_WIKI_EXCLUDE_DIRS="daily
#     inbox
#     notes, with comma
#     資料夾 with spaces
#     _*"
#
# Filesystem caveat:
#   On case-insensitive filesystems (macOS APFS default, Windows NTFS),
#   `Daily/` and `daily/` are treated as the same physical directory.
#
# Portability:
#   Pure POSIX sh. Works on macOS / Linux / BSD with /bin/sh.

set -u

if [ $# -lt 1 ]; then
  echo "Usage: $0 <vault-root>" >&2
  exit 1
fi

VAULT="$1"

if [ ! -d "$VAULT" ]; then
  echo "Error: vault root does not exist or is not a directory: $VAULT" >&2
  exit 1
fi

# Strip trailing slash from VAULT for clean path concatenation.
VAULT="${VAULT%/}"

# Source the wiki config file if present. Sets OBSIDIAN_WIKI_* vars.
# This avoids the .env tooling collision (anti-secret scanners, Claude
# permission rules, .gitignore defaults all target *.env globs).
CONFIG_FILE="$VAULT/.obsidian-wiki.config"
if [ -f "$CONFIG_FILE" ]; then
  set -a
  # shellcheck disable=SC1090
  . "$CONFIG_FILE"
  set +a
fi

# System always-excluded directories (NOT user-configurable).
# Newline-separated internally so patterns may contain commas / spaces.
SYS_EXCLUDES="wiki
.obsidian
.trash
.git
node_modules
_raw"

# Optional extra system-level exclusions for one-off runs (newline-separated).
EXTRA_SYS_EXCLUDES="${EXTRA_SYS_EXCLUDES:-}"

# User-configured exclusions (newline-separated, from .obsidian-wiki.config).
USER_EXCLUDES="${OBSIDIAN_WIKI_EXCLUDE_DIRS:-}"

# Build normalized newline-separated exclude list:
#   - Concatenate system + extra + user lists (each already newline-separated)
#   - Trim trailing slashes
#   - Trim surrounding whitespace
#   - Drop empty entries
#   - De-duplicate
EXCLUDE_LIST=$(
  printf "%s\n%s\n%s\n" "$SYS_EXCLUDES" "$EXTRA_SYS_EXCLUDES" "$USER_EXCLUDES" \
  | sed 's:/*$::; s/^[[:space:]]*//; s/[[:space:]]*$//' \
  | grep -v '^$' \
  | sort -u
)

# Save to temp file for safe iteration (handles patterns containing spaces,
# commas, or any character except newline). `for pattern in $X` would
# word-split on whitespace and break such patterns.
EXCLUDES_FILE=$(mktemp)
trap 'rm -f "$EXCLUDES_FILE"' EXIT
printf "%s\n" "$EXCLUDE_LIST" > "$EXCLUDES_FILE"

# Helper: is the top-level name $1 matched by any exclude glob pattern?
is_excluded() {
  name="$1"
  while IFS= read -r pattern; do
    [ -z "$pattern" ] && continue
    case "$name" in
      $pattern) return 0 ;;
    esac
  done < "$EXCLUDES_FILE"
  return 1
}

# Step 1: scan top-level entries of the vault.
find "$VAULT" -mindepth 1 -maxdepth 1 -type d 2>/dev/null | while IFS= read -r topdir; do
  topname=$(basename "$topdir")

  if is_excluded "$topname"; then
    continue
  fi

  find "$topdir" -type f -name "*.md" 2>/dev/null
done

# Step 2: include loose *.md files at vault root (depth-1 files).
find "$VAULT" -mindepth 1 -maxdepth 1 -type f -name "*.md" 2>/dev/null
