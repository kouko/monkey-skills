"""Structural grep-test guarding the generalized plan traceability field.

These two reference files are prompt artifacts, not executable code. Their
correctness is the PRESENCE of the load-bearing rule: the existing
`Brief item covered:` field accepts, in addition to a brainstorming brief item,
a STABLE JOIN-KEY referent for loom-spec change-folder provenance —
`<change-id> / Requirement: <name> / Scenario: <name>` (R5; checkable, à la Kiro
`_Requirements:` / Spec-Kit `FR-###`). It stays ONE field; only the accepted
referent is broadened. plan-document-reviewer Check 3's field-PRESENCE
requirement is unchanged — it now accepts EITHER a brief item OR this spec
join-key referent as valid provenance.

The checks assert on the load-bearing TOKENS (intent), tolerant of surrounding
wording, so the test guards meaning without being brittle.

Stdlib only (pathlib + re). Resolve the reference files relative to this test.
"""

import re
from pathlib import Path

_REFS = Path(__file__).parents[1] / "skills" / "writing-plans" / "references"
PLAN_FORMAT = _REFS / "plan-format.md"
REVIEWER = _REFS / "plan-document-reviewer-prompt.md"


def _text(path: Path) -> str:
    assert path.is_file(), f"reference file is absent at {path}"
    return path.read_text(encoding="utf-8")


# --- the stable join-key referent must be named in BOTH files ---------------

def _names_join_key(text: str) -> bool:
    """The three join-key parts (<change-id>, Requirement, Scenario) must all
    appear, AND be co-located in a window so they read as ONE referent shape
    rather than three unrelated mentions scattered through the file."""
    low = text.lower()
    if not ("change-id" in low and "requirement" in low and "scenario" in low):
        return False
    lines = low.splitlines()
    for i, line in enumerate(lines):
        if "change-id" in line:
            window = "\n".join(lines[max(0, i - 3):i + 6])
            if "requirement" in window and "scenario" in window:
                return True
    return False


def test_plan_format_names_join_key_referent():
    """plan-format.md must document that `Brief item covered:` accepts the
    stable join-key referent `<change-id> / Requirement / Scenario` as
    change-folder provenance."""
    text = _text(PLAN_FORMAT)
    assert "Brief item covered" in text, \
        "plan-format.md must still name the `Brief item covered` field"
    assert _names_join_key(text), \
        ("plan-format.md must name the stable join-key referent "
         "(<change-id> / Requirement: <name> / Scenario: <name>) co-located "
         "as one accepted provenance for `Brief item covered:`")


def test_plan_format_keeps_one_field():
    """The broadening must NOT introduce a second traceability field — the
    join-key referent is an alternative VALUE of the existing field. Guard
    against a stray new field name appearing alongside `Brief item covered`."""
    low = _text(PLAN_FORMAT).lower()
    for stray in ("spec item covered", "scenario covered",
                  "requirement covered", "change-folder covered"):
        assert stray not in low, \
            f"must keep ONE field — found a competing field name: {stray!r}"


def test_reviewer_check3_accepts_join_key_referent():
    """plan-document-reviewer Check 3 must accept EITHER a brief item OR the
    spec join-key referent as valid provenance (field-presence unchanged)."""
    text = _text(REVIEWER)
    assert "Brief item covered" in text, \
        "reviewer prompt must still name the `Brief item covered` field"
    assert _names_join_key(text), \
        ("reviewer Check 3 must name the stable join-key referent "
         "(<change-id> / Requirement: <name> / Scenario: <name>) as accepted "
         "spec provenance, co-located as one referent")
    low = text.lower()
    assert ("either" in low or " or " in low), \
        ("Check 3 must accept EITHER a brief item OR the spec join-key "
         "referent (broadened valid content)")
