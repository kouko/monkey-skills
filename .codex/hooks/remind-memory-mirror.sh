#!/usr/bin/env bash
# Thin shim over .claude/hooks/remind-memory-mirror.sh (the real check).
# Written by W1-02 — the command string below must never change: Codex
# binds hook trust to the DEFINITION, not to file content.
#
# Read stdin once — the recorder and the real hook must see the same
# payload, and a pipe can only be drained once.
INPUT=$(cat 2>/dev/null || true)
printf '%s' "$INPUT" | python3 "$(dirname "$0")/loom_record_fire.py" "$0" >/dev/null 2>&1 || true
printf '%s' "$INPUT" | exec .claude/hooks/remind-memory-mirror.sh
