#!/bin/bash
# Loom memory-store mirror reminder (host-neutral PostToolUse hook).
#
# Triggered: PostToolUse on Write|Edit (configured in .claude/settings.json).
#
# Why: auto-memory notes under */.claude/projects/<slug>/memory/ live
# per-machine and are NOT committed. Project-scoped knowledge (frontmatter
# `type: project`) must also land in the repo's committed store —
# docs/loom/BACKLOG.md (backlog-shaped items) or docs/loom/memory/ (durable
# project notes) — or it silently evaporates on any other machine. This hook
# reminds at the moment such a note is written.
#
# Scope: fires only for a project-type memory-note write. User/feedback
# notes, the curated MEMORY.md index, non-memory paths, and malformed or
# alternate-shaped payloads are silent no-ops — a hook must never break the
# session.
#
# Exit codes:
#   0 — no reminder needed (or payload unreadable / not a memory-note write)
#   2 — project-type memory note written (reminder printed to stderr)

set -e

INPUT=$(cat 2>/dev/null || echo '{}')

FILE_PATH=""
if command -v jq >/dev/null 2>&1; then
  FILE_PATH=$(echo "$INPUT" | jq -r '.tool_input.file_path // .tool_input.notebook_path // empty' 2>/dev/null || echo "")
fi

# Only auto-memory note writes are relevant.
case "$FILE_PATH" in
  */.claude/projects/*/memory/*.md) ;;
  *) exit 0 ;;
esac

# The MEMORY.md index is curated in place — never a mirror candidate.
case "${FILE_PATH##*/}" in
  MEMORY.md) exit 0 ;;
esac

[ -f "$FILE_PATH" ] || exit 0

# Frontmatter = lines between a `---` fence pair OPENING AT LINE 1 (a body
# horizontal-rule pair must not count). Real notes write the type either
# bare (`type: project`) or indented under a `metadata:` key
# (`  type: project`) — match both. Guarded (2>/dev/null || true) so a file
# that vanishes/loses read permission between the -f check and this read
# degrades to an empty frontmatter → silent exit 0, never a raw awk error.
FRONTMATTER=$(awk 'NR==1{if($0!~/^---[[:space:]]*$/)exit; next} /^---[[:space:]]*$/{exit} {print}' "$FILE_PATH" 2>/dev/null || true)

if echo "$FRONTMATTER" | grep -Eq '^[[:space:]]*type:[[:space:]]*project([[:space:]]|$)'; then
  cat >&2 <<EOF
📝 Project-type memory note written (auto-memory is per-machine, NOT committed):
    $FILE_PATH

Mirror the substance into the repo's committed store:
    docs/loom/BACKLOG.md   — backlog-shaped items (Status / Start / Origin / What)
    docs/loom/memory/      — durable project notes

If it is already reflected there, no action needed — then continue.
EOF
  exit 2
fi

exit 0
