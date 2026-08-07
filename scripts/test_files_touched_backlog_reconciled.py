"""RED-then-GREEN diagnostic for Task 4 — reconcile the declared-vs-actual
`Files touched` check backlog entry with the 2026-08-07 wire-in decision.

Grep-based on purpose (robust to prose rewording around the load-bearing
substrings, not to exact whitespace): the entry file is prose, and a
byte-exact match would break on any harmless rewrap. What must hold is:

  (a) the entry records the wire-in decision — placement in
      `finishing-a-development-branch` Step 8, and that the script stays
      at repo root (not moved into loom-code/scripts/).
  (b) each of the 6 obligations that remain deferred after that decision
      carries a `start:` re-trigger condition in the body.

Before the entry is edited (decision-pending state), neither holds — the
entry has no decision record and zero `start:` fields — so the pin test
fails RED first. The companion test proves the pin is load-bearing:
mutating any single required token out of the current entry makes the
check flag it, so a future silent weakening cannot pass unnoticed.
"""

import re
from pathlib import Path

ENTRY = (
    Path(__file__).resolve().parent.parent
    / "docs"
    / "loom"
    / "backlog"
    / "2026-08-01-declared-vs-actual-files-touched-check-measured-wire-in-decision-pending.md"
)

# Each required token paired with the label reported when it is missing.
# The `flat` flag marks tokens checked against the whitespace-normalized
# copy (they may legitimately wrap across lines in prose).
_REQUIRED_TOKENS = [
    ("finishing-a-development-branch", "wiring-site skill name", False),
    ("Step 8", "Step 8 placement", False),
    ("orchestrator-only", "orchestrator-only framing", False),
    ("scripts/check_files_touched.py", "script name", False),
    ("stays at repo root", "script-stays-at-repo-root decision", True),
]


def _missing_problems(text: str) -> list[str]:
    """Return the labels of every requirement the entry text fails.

    (a) each required decision token is present (some against a
    whitespace-normalized copy so a line wrap does not defeat the grep);
    (b) at least 6 `start:` re-triggers, one per still-deferred obligation.
    """
    flat = " ".join(text.split())
    problems: list[str] = []
    for token, label, use_flat in _REQUIRED_TOKENS:
        haystack = flat if use_flat else text
        if token not in haystack:
            problems.append(label)
    # Case-sensitive lowercase "start:" so this doesn't accidentally match a
    # frontmatter `Start:`-style bullet the backlog charter's field-agreement
    # check treats specially.
    if text.count("start:") < 6:
        problems.append("6 start: re-triggers")
    return problems


def test_entry_records_decision_and_retriggers():
    assert _missing_problems(ENTRY.read_text(encoding="utf-8")) == [], (
        "backlog entry must record the wire-in decision (placement + "
        "script-stays-at-root) and carry a start: re-trigger per deferred "
        "obligation"
    )


def test_missing_problems_check_is_not_vacuous():
    """Prove the pin is load-bearing: removing any single required token
    from the real entry makes the check flag exactly that requirement."""
    text = ENTRY.read_text(encoding="utf-8")
    assert _missing_problems(text) == [], "baseline: real entry must be clean"
    for token, label, _use_flat in _REQUIRED_TOKENS:
        # Whitespace-flexible removal so a token that legitimately wraps
        # across lines in the raw prose (e.g. "stays at repo root") is still
        # excised — a plain str.replace would miss the wrapped form and the
        # flat-checked requirement would falsely stay satisfied.
        pattern = r"\s+".join(re.escape(w) for w in token.split())
        mutated = re.sub(pattern, "<removed>", text)
        assert label in _missing_problems(mutated), (
            f"removing {token!r} should flag {label!r}, but the check stayed silent"
        )
    # And dropping the re-triggers below the floor must flag them.
    stripped = text.replace("start:", "was-here:")
    assert "6 start: re-triggers" in _missing_problems(stripped)
