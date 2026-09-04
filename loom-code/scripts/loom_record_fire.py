#!/usr/bin/env python3
"""Shared Codex hook firing recorder
(docs/loom/2026-09-04-codex-hook-trust-covers-every-definition-and-worktree
/plan.md `## 設計決定`).

Every hook definition in ``.codex/hooks.json`` — loom's own PreToolUse Bash
shim and any hooks an adopting repo defines for itself — pipes its stdin
payload through this recorder before doing its real work. Codex' hook trust
is bound to the DEFINITION (event + command), not to any one script's
content, so this appends one line per firing to the shared ledger at
``.codex/hooks/.loom-hook-fired``::

    <hook_event_name>\\t<command>\\t<tool_name>

``command`` is always the calling hook's own path (its ``$0``), resolved
relative to the repo root — never absolute, so the ledger stays comparable
across machines and worktrees. ``tool_name`` is recorded for a human reading
the ledger; ``--trusted`` attributes firings by ``(event, command)`` alone,
because Codex' name for ``apply_patch`` under PostToolUse has never been
live-verified and matching on it would risk a false "never".

Never fatal: a hostile or truncated payload, a missing argv[1], or an
unwritable ledger must never surface as a crash to the caller — the real
hook's own verdict is what has to reach Codex, not this recorder's. On any
error this silently no-ops (exit 0, nothing written) — chosen over writing a
line with empty fields, since a line that cannot be attributed to a real
definition is worse than no evidence at all (loom_checker.py's own
fail-closed-but-say-why principle, applied to a component that must not be
allowed to fail closed itself).

Writes nothing at all when the ``LOOM_SELF_TEST`` env var is set: that marks
the one caller that is NOT Codex' hook engine — codex_scaffold.py
--self-test spawns the shim (and therefore this recorder) itself, and a
ledger line written then would let --trusted vouch for a trust decision
Codex never made.

The append is unsynchronised: two hooks on the same event (PostToolUse
carries two commands here) may write concurrently and no lock is taken. A
line lost that way degrades to a ``never`` false negative — one more
/hooks ask — and can never manufacture a ``fired``, which is why the lock
was left out (branch-end nit, 2026-09-05).
"""
from __future__ import annotations

import json
import os
import sys
from pathlib import Path

SELF_TEST_ENV = "LOOM_SELF_TEST"
LEDGER_NAME = ".loom-hook-fired"
# This file always lives at .codex/hooks/loom_record_fire.py in an adopting
# repo (codex_scaffold.py ships it as a sibling of the shim): stripping the
# filename gives .codex/hooks/, then two more .parent calls give .codex/
# and the repo root.
_PARENT_CALLS_TO_REPO = 3


def _repo_root() -> Path:
    root = Path(os.path.abspath(__file__))
    for _ in range(_PARENT_CALLS_TO_REPO):
        root = root.parent
    return root


def _relative_command(raw: str, repo: Path) -> str:
    return os.path.relpath(os.path.abspath(raw), repo)


def record(argv: list[str], stdin_text: str, env: dict) -> None:
    """Append one ledger line, or do nothing — see the module docstring for
    every condition that means "do nothing"."""
    if env.get(SELF_TEST_ENV):
        return
    if len(argv) < 2 or not argv[1]:
        return
    try:
        payload = json.loads(stdin_text)
    except (json.JSONDecodeError, TypeError, ValueError):
        return
    if not isinstance(payload, dict):
        return
    event = payload.get("hook_event_name")
    tool_name = payload.get("tool_name")
    if not event or not tool_name:
        return

    repo = _repo_root()
    command = _relative_command(argv[1], repo)
    ledger = repo / ".codex" / "hooks" / LEDGER_NAME
    ledger.parent.mkdir(parents=True, exist_ok=True)
    with open(ledger, "a", encoding="utf-8") as fh:
        fh.write(f"{event}\t{command}\t{tool_name}\n")


def main(argv: list[str] | None = None) -> int:
    argv = sys.argv if argv is None else argv
    try:
        stdin_text = sys.stdin.read()
    except Exception:
        stdin_text = ""
    try:
        record(argv, stdin_text, os.environ)
    except Exception:
        # Never fatal — a broken recorder must never block the real hook's
        # own verdict from reaching Codex.
        pass
    return 0


if __name__ == "__main__":
    sys.exit(main())
