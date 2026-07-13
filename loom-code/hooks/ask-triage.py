#!/usr/bin/env python3
"""PreToolUse card for AskUserQuestion — the ask-moment triage (L2).

Claude Code pipes the hook-event JSON to stdin before every
AskUserQuestion tool call (matcher registered in hooks.json). This
hook does not gate anything — it always allows (exit 0) — it only
injects a static ``hookSpecificOutput.additionalContext`` card
carrying the three-way triage (fact-in-repo → look it up / user-fact
or irreversible-confirmation → ask directly / researchable design
fork → research first, then ask with a recommendation). SSOT for the
triage wording: loom-code/skills/subagent-driven-development/SKILL.md
§Asking the user, gate ①/②.

Scope-leak note: this hook fires on EVERY AskUserQuestion call in any
session with loom-code enabled, including non-coding work — hence the
domain-neutral card wording ("facts checkable within the task's own
sources", not "the codebase") and the explicit clearance line so a
confirmation-type ask in a non-coding session reads the card as
harmless rather than as a deterrent.

stdin content is read but otherwise unused — the card is static
regardless of the question being asked. Malformed/absent stdin still
emits the card (fail-open, never crash the session).

Exit codes follow the PreToolUse contract: 0 = allow (this hook never
blocks). Stdlib only.
"""

import json
import sys

CARD = (
    "Before asking: triage this question. (1) A fact checkable within the "
    "task's own sources (files, config, docs in scope) → look it up "
    "instead of asking. (2) A user-only fact, a preference, or a "
    "confirmation of an irreversible/outward-facing action → ask "
    "directly; this card is never a reason to avoid or delay such asks. "
    "(3) A design/approach fork that industry practice could inform → "
    "research first (loom-code: SDD §Asking the user, gate ②), "
    "then ask WITH a cited recommendation. Questions arriving with options "
    "+ a recommendation respect the user's time; unresearched forks "
    "outsource your work to them."
)


def main():
    sys.stdin.read()  # content unused — card is static regardless of input
    print(json.dumps({
        "hookSpecificOutput": {
            "hookEventName": "PreToolUse",
            "additionalContext": CARD,
        }
    }))
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except SystemExit:
        raise
    except Exception as exc:  # never crash the session — fail open
        print(f"loom ask-triage: internal error ({exc}); fail-open", file=sys.stderr)
        sys.exit(0)
