#!/bin/sh
# scan-vault.sh — Emit absolute paths of vault .md files eligible for wiki ingest.
#
# Usage:
#   scan-vault.sh <vault-root>
#
# Config: reads <vault-root>/.obsidian-wiki.config (shell-sourceable, NOT .env)
#         to set OBSIDIAN_WIKI_EXCLUDE_DIRS and OBSIDIAN_WIKI_EXCLUDE_FILES.
#         Falls back to env vars if config file is missing (useful for testing).
#
# Optional env: EXTRA_SYS_EXCLUDES (newline-separated) for one-off invocations
#               to add system-level dir exclusions without editing this script.
#
# Exit codes:
#   0  on success (always; empty output is valid for an empty vault)
#   1  on bad usage / missing vault dir
#
# Behavior:
#   - Scans vault root for top-level directories
#   - Prunes directories matching the system DIR blacklist OR
#     OBSIDIAN_WIKI_EXCLUDE_DIRS (top-level only match)
#   - Recurses into remaining top-level dirs to find *.md files
#   - Filters every found .md basename through the FILE blacklist (system +
#     OBSIDIAN_WIKI_EXCLUDE_FILES) — applies at any depth
#   - Also scans loose *.md files at the vault root (depth-1), excluding
#     hidden files (.notes.md style)
#
# Match rules (asymmetric by intent):
#   DIR rule:  top-level only, case-sensitive. Nested dirs with the same
#              name (e.g. projects/old/daily/) are NOT excluded.
#              Rationale: directory semantics are location-sensitive
#              (top-level `daily/` is the flow-notes folder; nested
#              `daily/` somewhere is just a sub-grouping).
#   FILE rule: any depth, case-sensitive. Filename `CLAUDE.md` is excluded
#              wherever it appears.
#              Rationale: filename conventions are location-independent
#              (CLAUDE.md is agent config no matter where it lives).
#
# Glob patterns (DIR and FILE both support):
#   Each entry is a shell glob, matched via `case ... in <pattern>)`. Examples:
#     daily            literal exact match
#     _*               any name starting with underscore
#     temp?            single-char wildcard
#     [Aa]rchive       case-variant char class
#     *.bak            suffix glob
#     .*               any name starting with dot (system-default for dirs)
#
# Multi-line value format (NEW in v3.8.0):
#   OBSIDIAN_WIKI_EXCLUDE_DIRS / OBSIDIAN_WIKI_EXCLUDE_FILES use one pattern
#   per line within a quoted string. Patterns may contain commas, spaces,
#   CJK, or any character except newline.
#
#   Example in .obsidian-wiki.config:
#     OBSIDIAN_WIKI_EXCLUDE_DIRS="daily
#     inbox
#     資料夾 with spaces"
#     OBSIDIAN_WIKI_EXCLUDE_FILES="README.md
#     TODO.md"
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
CONFIG_FILE="$VAULT/.obsidian-wiki.config"
if [ -f "$CONFIG_FILE" ]; then
  set -a
  # shellcheck disable=SC1090
  . "$CONFIG_FILE"
  set +a
fi

# ---------------------------------------------------------------------------
# DIR exclude list (top-level only)
# ---------------------------------------------------------------------------

# System always-excluded directories (NOT user-configurable).
# `.*` catches every top-level dir starting with `.` — covers .obsidian,
# .trash, .git, .github, .vscode, .idea, .claude, .cursor, .codex,
# .windsurf, .devcontainer, .husky, .changeset, etc. by Unix convention
# (dot-prefix = hidden / system, never user knowledge).
SYS_EXCLUDE_DIRS="wiki
.*
node_modules
_raw"

EXTRA_SYS_EXCLUDES="${EXTRA_SYS_EXCLUDES:-}"
USER_EXCLUDE_DIRS="${OBSIDIAN_WIKI_EXCLUDE_DIRS:-}"

EXCLUDE_DIRS_LIST=$(
  printf "%s\n%s\n%s\n" "$SYS_EXCLUDE_DIRS" "$EXTRA_SYS_EXCLUDES" "$USER_EXCLUDE_DIRS" \
  | sed 's:/*$::; s/^[[:space:]]*//; s/[[:space:]]*$//' \
  | grep -v '^$' \
  | sort -u
)

EXCLUDE_DIRS_FILE=$(mktemp)
trap 'rm -f "$EXCLUDE_DIRS_FILE" "$EXCLUDE_FILES_FILE"' EXIT
printf "%s\n" "$EXCLUDE_DIRS_LIST" > "$EXCLUDE_DIRS_FILE"

is_excluded_dir() {
  name="$1"
  while IFS= read -r pattern; do
    [ -z "$pattern" ] && continue
    case "$name" in
      $pattern) return 0 ;;
    esac
  done < "$EXCLUDE_DIRS_FILE"
  return 1
}

# ---------------------------------------------------------------------------
# FILE exclude list (any depth)
# ---------------------------------------------------------------------------

# System always-excluded files (NOT user-configurable).
# These are universal agent-config / instruction filenames that should never
# be wiki-distilled regardless of where they sit in the vault tree.
SYS_EXCLUDE_FILES="CLAUDE.md
AGENT.md
AGENTS.md
MEMORY.md"

USER_EXCLUDE_FILES="${OBSIDIAN_WIKI_EXCLUDE_FILES:-}"

EXCLUDE_FILES_LIST=$(
  printf "%s\n%s\n" "$SYS_EXCLUDE_FILES" "$USER_EXCLUDE_FILES" \
  | sed 's:/*$::; s/^[[:space:]]*//; s/[[:space:]]*$//' \
  | grep -v '^$' \
  | sort -u
)

EXCLUDE_FILES_FILE=$(mktemp)
printf "%s\n" "$EXCLUDE_FILES_LIST" > "$EXCLUDE_FILES_FILE"

is_excluded_file() {
  name="$1"
  while IFS= read -r pattern; do
    [ -z "$pattern" ] && continue
    case "$name" in
      $pattern) return 0 ;;
    esac
  done < "$EXCLUDE_FILES_FILE"
  return 1
}

# ---------------------------------------------------------------------------
# Scan
# ---------------------------------------------------------------------------

# Helper: emit a path only if its basename is not in the FILE blacklist.
emit_if_file_allowed() {
  while IFS= read -r f; do
    base=$(basename "$f")
    if ! is_excluded_file "$base"; then
      printf "%s\n" "$f"
    fi
  done
}

# Step 1: scan top-level entries of the vault.
# For each top-level dir not in the DIR blacklist, recurse and find .md files,
# filtered through the FILE blacklist.
find "$VAULT" -mindepth 1 -maxdepth 1 -type d 2>/dev/null | while IFS= read -r topdir; do
  topname=$(basename "$topdir")

  if is_excluded_dir "$topname"; then
    continue
  fi

  find "$topdir" -type f -name "*.md" 2>/dev/null | emit_if_file_allowed
done

# Step 2: include loose *.md files at vault root (depth-1).
# Exclude hidden files (.notes.md style) for consistency with .* dir rule.
# Also filter through FILE blacklist (catches root-level CLAUDE.md, etc.).
find "$VAULT" -mindepth 1 -maxdepth 1 -type f -name "*.md" ! -name ".*" 2>/dev/null | emit_if_file_allowed
