#!/bin/sh
# scan-vault.sh — Emit absolute paths of vault .md files eligible for wiki ingest.
#
# Usage:
#   scan-vault.sh <vault-root>
#
# Reads OBSIDIAN_EXCLUDE_DIRS from the environment (comma-separated bare dir names).
# Optional: EXTRA_SYS_EXCLUDES (comma-separated) for one-off invocations to add
#           system-level exclusions without editing this script.
#
# Exit codes:
#   0  on success (always; empty output is valid for an empty vault)
#   1  on bad usage / missing vault dir
#
# Behavior:
#   - Scans vault root for top-level directories
#   - Prunes directories matching the system blacklist OR OBSIDIAN_EXCLUDE_DIRS
#   - Recurses into remaining top-level dirs to find *.md files
#   - Also includes loose *.md files at the vault root (depth-1)
#
# Match rule:
#   Top-level only, case-sensitive. Nested directories with the same name
#   (e.g. projects/old/daily/) are NOT excluded.
#
# Filesystem caveat:
#   On case-insensitive filesystems (macOS APFS default, Windows NTFS),
#   `Daily/` and `daily/` are treated as the same physical directory, so
#   listing one excludes the other. Case-sensitive matching only matters
#   on case-sensitive FS (Linux ext4, macOS APFS-Case-Sensitive variant).
#
# Portability:
#   Pure POSIX sh. No bash arrays, no `set -e` on subshells, no associative
#   arrays. Works on macOS / Linux / BSD with /bin/sh.

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

# System always-excluded directories (NOT user-configurable via env).
# Edit this list only when adding new system-level conventions.
SYS_EXCLUDES="wiki,.obsidian,.trash,.git,node_modules,_raw"

# Optional extra system-level exclusions for one-off runs.
EXTRA_SYS_EXCLUDES="${EXTRA_SYS_EXCLUDES:-}"

# User-configured exclusions (from .env or shell env).
USER_EXCLUDES="${OBSIDIAN_EXCLUDE_DIRS:-}"

# Build a normalized newline-separated exclude list:
#   - Concatenate system + user lists with commas
#   - Split on commas
#   - Trim trailing slashes
#   - Trim surrounding whitespace
#   - Drop empty entries
#   - De-duplicate
EXCLUDE_LIST=$(
  printf "%s,%s,%s\n" "$SYS_EXCLUDES" "$EXTRA_SYS_EXCLUDES" "$USER_EXCLUDES" \
  | tr ',' '\n' \
  | sed 's:/*$::; s/^[[:space:]]*//; s/[[:space:]]*$//' \
  | grep -v '^$' \
  | sort -u
)

# For fast "is X in the exclude list?" lookups, build a comma-bracketed
# string we can pattern-match against.
EXCLUDE_BRACKETED=",$(echo "$EXCLUDE_LIST" | tr '\n' ',')"

# Step 1: scan top-level entries of the vault.
# Use -mindepth 1 -maxdepth 1 to enumerate just the immediate children.
find "$VAULT" -mindepth 1 -maxdepth 1 -type d 2>/dev/null | while IFS= read -r topdir; do
  # Extract the basename (top-level directory name) for blacklist comparison.
  topname=$(basename "$topdir")

  # Case-sensitive lookup: does ",<name>," appear in the bracketed exclude list?
  case "$EXCLUDE_BRACKETED" in
    *",$topname,"*)
      # Excluded — skip silently.
      continue
      ;;
  esac

  # Recurse into this top-level dir and emit all .md files found.
  find "$topdir" -type f -name "*.md" 2>/dev/null
done

# Step 2: include loose *.md files at vault root (depth-1 files).
find "$VAULT" -mindepth 1 -maxdepth 1 -type f -name "*.md" 2>/dev/null
