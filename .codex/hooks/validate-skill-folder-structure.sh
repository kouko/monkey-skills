#!/bin/bash
# Skill folder structure validator (Anthropic skill convention enforcement).
#
# Triggered: PostToolUse on Write|Edit (configured in .claude/settings.json).
#
# Rule: a skill directory may contain SKILL.md plus any number of single-level
# subdirectories (assets/, scripts/, agents/, references/, protocols/, etc.).
# Subdirectories MUST NOT themselves contain subdirectories.
#
#   ✅ skills/init/assets/foo.md
#   ✅ skills/init/scripts/bar.py
#   ❌ skills/init/assets/scripts/foo.py    (nested — assets/scripts/)
#   ❌ skills/init/agents/sub/bar.md        (nested — agents/sub/)
#
# Exit codes:
#   0 — no violation
#   2 — violation found (blocking; message printed to stderr)

set -e

# Read PostToolUse event from stdin (Claude Code hook contract).
# We extract tool_input.file_path; if absent, we silently fall back to a
# repo-wide scan (slower but safe).
INPUT=$(cat 2>/dev/null || echo '{}')

FILE_PATH=""
if command -v jq >/dev/null 2>&1; then
  FILE_PATH=$(echo "$INPUT" | jq -r '.tool_input.file_path // .tool_input.notebook_path // empty' 2>/dev/null || echo "")
fi

# Find the skill root(s) we need to check.
# - If file is under a /skills/<name>/ tree → check only that one skill (fast).
# - Else → no check needed (most edits aren't to skill files).
SKILL_ROOTS=()
if [ -n "$FILE_PATH" ] && echo "$FILE_PATH" | grep -q '/skills/'; then
  # Extract: prefix .../<plugin>/skills/<skill-name>/ (single skill name component)
  skill_root=$(echo "$FILE_PATH" | sed -E 's|(.*/skills/[^/]+).*|\1|')
  if [ -d "$skill_root" ] && [ -f "$skill_root/SKILL.md" ]; then
    SKILL_ROOTS+=("$skill_root")
  fi
fi

# No skill touched → exit clean (most Write/Edit ops won't trigger validation).
if [ "${#SKILL_ROOTS[@]}" -eq 0 ]; then
  exit 0
fi

# For each affected skill, check for nested subdirectories.
violations=""
for skill_root in "${SKILL_ROOTS[@]}"; do
  # find at depth ≥2 from skill_root means: a directory inside a directory.
  # Excludes: the skill root itself (depth 0), top-level subfolders (depth 1).
  nested=$(find "$skill_root" -mindepth 2 -type d 2>/dev/null || true)
  if [ -n "$nested" ]; then
    violations+="
  ${skill_root}:
$(echo "$nested" | sed 's|^|    |')
"
  fi
done

if [ -n "$violations" ]; then
  cat >&2 <<EOF
❌ Skill folder structure violation detected

Anthropic skill convention: subfolders of subfolders under a skill root are forbidden.
A skill may contain SKILL.md + any number of single-level subdirectories
(assets/, scripts/, agents/, references/, etc.). Those subdirectories
themselves must be flat — no nested subdirectories inside them.

Nested directory paths found:${violations}
Fix: move files up one level; remove the nested subdirectory.
See CLAUDE.md "Skill Structure" section for the full rule + examples.
EOF
  exit 2
fi

exit 0
