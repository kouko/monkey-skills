"""Prose-pin test for the finishing Step 8 files-touched sibling check.

Pins the Step 8 bullet that wires `scripts/check_files_touched.py` (the
declared-vs-actual `Files touched` comparator) into close-out: once per
branch, the orchestrator joins THIS branch's own plan declarations
against the real commit diffs, so a task that under-declared its touched
files gets caught before the branch ships — not left as a measurement
prototype wired into nothing (docs/loom/specs/2026-08-01-declared-vs-actual-
files-touched-check.md).

Same shape as its Step 8 siblings (Memory-store integrity, Backlog-close):
orchestrator-only / once-per-branch (a per-implementer or per-wave run
would race), a diff-auditable trigger that skips silently when absent
(no plan file for this branch), and a loud N/A when the checker script
itself is absent from the consuming repo (the script ships at the repo
root, in no plugin).

Round-2 fix: the original version of this test asserted its four
house-style tokens ("orchestrator-only", "ONCE per branch", a loud N/A
naming the checker, the exit-1/exit-2 distinction) existed ANYWHERE in
SKILL.md. Two of those strings are not load-bearing at that scope — they
already appear verbatim in the Memory-store-integrity and Backlog-close
sibling bullets' own boilerplate (`orchestrator-only` 7x, `ONCE per
branch` 6x file-wide), so the old test would stay green even if someone
stripped both tokens from THIS bullet specifically. This version instead
extracts the files-touched bullet's OWN text window (from its `- ` list
marker to the next sibling bullet's marker) and scopes every assertion
to that window, then proves the window-scoped check is load-bearing by
mutating a copy of the real window in memory and showing each removed
token gets flagged missing.

Uses the same whitespace-normalized substring technique as
`test_finishing_backlog_close.py` / `scripts/test_state_anchor_carrier_
inventory.py`: collapse hard wraps so a contiguous-phrase match doesn't
depend on line breaks. The window-extraction + mutate-and-catch pattern
follows `scripts/test_state_anchor_carrier_inventory.py`'s
`test_scan_state_anchor_carriers_catches_a_removed_carrier` (proving a
checker isn't vacuous by showing it catches a removed carrier).
"""

import re
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
SKILL_MD = (
    REPO_ROOT
    / "loom-code"
    / "skills"
    / "finishing-a-development-branch"
    / "SKILL.md"
)

# The files-touched bullet is a 3-space-indented `- ` list item in Step 8's
# hygiene list. Its raw window runs from its own marker up to (but not
# including) the next sibling bullet's marker (`- Attached-HEAD check`).
# `check_files_touched.py` is the unique anchor named in the round-2
# finding, but anchoring the regex on the bullet's own lead phrase
# ("Files-touched check") is equally unique in this file (verified: exactly
# one match) and keeps the window's start aligned with the bullet's actual
# start rather than a point mid-sentence.
_BULLET_WINDOW_RE = re.compile(r"\n   - Files-touched check.*?(?=\n   - )", re.DOTALL)

# The four house-style tokens the finding requires, scoped to this bullet's
# own window. Two (N/A, checker script name) are exact-case; the exit-code
# pair is matched case-insensitively, mirroring the original assertions.
_EXACT_CASE_TOKENS = {
    "orchestrator-only tag": "orchestrator-only",
    "once-per-branch scope": "ONCE per branch",
    "loud N/A clause": "N/A",
    "checker script name": "check_files_touched.py",
}
_CASE_INSENSITIVE_TOKENS = {
    "exit-1 gating case": "exit 1",
    "exit-2 loud-empty case": "exit 2",
}


def _bullet_window(text: str) -> str:
    """Extract the files-touched bullet's own text window, whitespace-
    normalized (collapses hard wraps so a contiguous-phrase match doesn't
    depend on line breaks). Fails loud if the bullet marker isn't found,
    rather than silently matching nothing.
    """
    match = _BULLET_WINDOW_RE.search(text)
    if match is None:
        raise AssertionError(
            "files-touched bullet marker '- Files-touched check' not found "
            "in SKILL.md — the bullet moved, was renamed, or was removed"
        )
    return " ".join(match.group(0).split())


def _missing_required_tokens(window: str) -> list[str]:
    """Return labels of any required token missing from `window`; empty
    list means the window carries all four house-style tokens."""
    missing = [
        label for label, token in _EXACT_CASE_TOKENS.items() if token not in window
    ]
    lowered = window.lower()
    missing += [
        label
        for label, token in _CASE_INSENSITIVE_TOKENS.items()
        if token not in lowered
    ]
    return missing


def test_step8_files_touched_bullet_window_carries_house_style_tokens():
    """All four house-style tokens must appear WITHIN the files-touched
    bullet's own window — not merely somewhere in SKILL.md, where
    'orchestrator-only' and 'ONCE per branch' also occur verbatim in
    sibling bullets' boilerplate and would keep a whole-file check green
    even if stripped from this specific bullet."""
    window = _bullet_window(SKILL_MD.read_text(encoding="utf-8"))
    missing = _missing_required_tokens(window)
    assert missing == [], f"files-touched bullet window missing: {missing}"


def test_missing_required_tokens_check_is_not_vacuous():
    """Proves the window-scoped check above is load-bearing, not vacuous.

    The real window currently carries all four tokens, so the test above
    alone would stay green even if `_missing_required_tokens` always
    returned `[]` (e.g. a typo'd predicate). This test takes the REAL
    bullet window, strips each required token out one at a time — pure
    in-memory string mutation, no file writes — and shows the check
    correctly flags exactly that token as missing.
    """
    window = _bullet_window(SKILL_MD.read_text(encoding="utf-8"))
    assert _missing_required_tokens(window) == []  # baseline: real window is clean

    all_tokens = {**_EXACT_CASE_TOKENS, **_CASE_INSENSITIVE_TOKENS}
    for label, token in all_tokens.items():
        mutated = window.replace(token, "<removed>")
        assert token not in mutated, f"mutation didn't remove {token!r}"
        missing = _missing_required_tokens(mutated)
        assert label in missing, (
            f"removing {token!r} from the bullet window should have "
            f"flagged {label!r} as missing, got {missing}"
        )
