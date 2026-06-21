#!/bin/bash
# Skill folder structure validator (Anthropic skill convention enforcement).
# Plugin-shipped variant — fires for any repo where dev-workflow is installed
# AND the file being written is under a /skills/<name>/ tree.
#
# This is the "B" hook from the conversation; coexists with the optional
# repo-level "D" hook at <repo>/.claude/hooks/validate-skill-folder-structure.sh.
# To avoid double-firing, this script SKIPS when D is detected in the current
# repo (D handles it; B retreats).
#
# Rule: a skill directory may contain SKILL.md plus single-level subdirectories
# (assets/, scripts/, agents/, references/, etc.). Subdirectories MUST NOT
# themselves contain subdirectories.
#
#   ✅ skills/init/assets/foo.md
#   ✅ skills/init/scripts/bar.py
#   ❌ skills/init/assets/scripts/foo.py    (nested — assets/scripts/)
#   ❌ skills/init/agents/sub/bar.md        (nested — agents/sub/)
#
# Exit codes:
#   0 — no violation (or skipped due to D-active dedup)
#   2 — violation found (blocking; message printed to stderr)

set -e

# --- Dedup with repo-level "D" hook ---
# If the current repo has its own .claude/hooks/validate-skill-folder-structure.sh,
# defer to it (avoid double-firing). This is the explicit B + D coexistence
# contract: D is authoritative inside repos that ship it; B fills the gap
# everywhere else.
REPO_ROOT=$(git rev-parse --show-toplevel 2>/dev/null || true)
if [ -n "$REPO_ROOT" ] && [ -x "$REPO_ROOT/.claude/hooks/validate-skill-folder-structure.sh" ]; then
  exit 0
fi

# --- Read PostToolUse event from stdin ---
INPUT=$(cat 2>/dev/null || echo '{}')

FILE_PATH=""
if command -v jq >/dev/null 2>&1; then
  FILE_PATH=$(echo "$INPUT" | jq -r '.tool_input.file_path // .tool_input.notebook_path // empty' 2>/dev/null || echo "")
fi

# --- Find skill root from the modified file path ---
# Pattern: <repo>/.../skills/<skill-name>/...
# If the modified file isn't under a skills/ tree, exit clean (most edits aren't skill files).
SKILL_ROOT=""
if [ -n "$FILE_PATH" ] && echo "$FILE_PATH" | grep -q '/skills/'; then
  candidate=$(echo "$FILE_PATH" | sed -E 's|(.*/skills/[^/]+).*|\1|')
  if [ -d "$candidate" ] && [ -f "$candidate/SKILL.md" ]; then
    SKILL_ROOT="$candidate"
  fi
fi

[ -z "$SKILL_ROOT" ] && exit 0

# --- Check for nested subdirectories under skill root ---
# find at depth ≥2 means: a directory inside a directory under <skill-root>.
nested=$(find "$SKILL_ROOT" -mindepth 2 -type d 2>/dev/null || true)

if [ -n "$nested" ]; then
  cat >&2 <<EOF
❌ Skill folder structure violation (dev-workflow plugin hook)

Anthropic skill convention: subfolders of subfolders under a skill root are forbidden.
A skill may contain SKILL.md + any number of single-level subdirectories
(assets/, scripts/, agents/, references/, etc.). Those subdirectories
themselves must be flat — no nested subdirectories inside them.

Skill root: ${SKILL_ROOT}
Nested directory paths found:
$(echo "$nested" | sed 's|^|  |')

Fix: move files up one level; remove the nested subdirectory.
Or: split the grouping into parallel top-level dirs at skill root
(e.g. scripts-redshift/ + scripts-snowflake/ instead of scripts/redshift/
+ scripts/snowflake/).

See skill-dev-toolkit:skill-creator-advance § "Folder structure must be flat"
for full guidance and examples.
EOF
  exit 2
fi

exit 0
