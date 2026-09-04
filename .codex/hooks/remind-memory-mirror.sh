#!/usr/bin/env bash
# Thin shim over .claude/hooks/remind-memory-mirror.sh (the real check).
# Written by W1-02 — the command string below must never change: Codex
# binds hook trust to the DEFINITION, not to file content.
#
# Resolve the real hook relative to THIS SHIM's own location, never the
# caller's cwd — a cwd-relative exec crashes from a non-root cwd (a
# worktree, a nested skill folder) while an earlier version of this shim
# still recorded (below) that the definition fired.
HERE="$(cd "$(dirname "$0")" && pwd)"
TARGET="$HERE/../../.claude/hooks/remind-memory-mirror.sh"
# Read stdin once — the recorder and the real hook must see the same
# payload, and a pipe can only be drained once.
INPUT=$(cat 2>/dev/null || true)
if [ ! -x "$TARGET" ]; then
  echo "BLOCK: .codex/hooks/remind-memory-mirror.sh cannot find its target $TARGET" >&2
  exit 2
fi
printf '%s' "$INPUT" | python3 "$HERE/loom_record_fire.py" "$0" >/dev/null 2>&1 || true
printf '%s' "$INPUT" | exec "$TARGET"
