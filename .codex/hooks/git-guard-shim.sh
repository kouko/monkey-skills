#!/bin/bash
# Codex PreToolUse shim for loom-code's git-guard.py.
#
# Codex's hook payload shape is an UNVERIFIED upstream surface (no spec
# to pin against). This shim reads the hook stdin ONCE, checks it is
# parseable JSON shaped like Claude Code's PreToolUse event (a
# tool_input.command string present), and only then forwards the same
# stdin to loom-code/hooks/git-guard.py unchanged.
#
# On any shape mismatch (unparseable JSON, or valid JSON missing
# tool_input.command) the shim fails OPEN — exit 0 — and prints exactly
# one stderr line, so the gap is loud instead of either crashing or
# silently blocking an unrelated command:
#
#   codex payload shape unknown — gate inactive
#
# Exit codes when forwarded to git-guard.py: 0 = allow, 2 = block
# (stderr shown to the model), matching the PreToolUse contract.

set -euo pipefail

PAYLOAD="$(cat)"

if ! printf '%s' "$PAYLOAD" | python3 -c '
import json
import sys

try:
    data = json.load(sys.stdin)
except ValueError:
    sys.exit(1)
if not isinstance(data, dict):
    sys.exit(1)
tool_input = data.get("tool_input")
if not isinstance(tool_input, dict) or not isinstance(tool_input.get("command"), str):
    sys.exit(1)
' 2>/dev/null; then
  echo "codex payload shape unknown — gate inactive" >&2
  exit 0
fi

# Resolve the monkey-skills repo root from THIS SCRIPT's own location
# (not the invoking process's cwd, which is the tool-call's cwd and may
# point anywhere) so git-guard.py is always found regardless of where
# Codex runs the hook from.
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(git -C "$SCRIPT_DIR" rev-parse --show-toplevel)"

printf '%s' "$PAYLOAD" | python3 "$REPO_ROOT/loom-code/hooks/git-guard.py"
