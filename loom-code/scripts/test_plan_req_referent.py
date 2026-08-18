"""Structural grep-test guarding the REQ-<n> referent, kind (d).

Three consumers of the `Brief item covered` grammar must name kind (d): a
`REQ-<n>` id declared by an id-mode change-folder header, or the id-form join
key `<change-id> / REQ-<n> / Scenario: <name>` — plus OQ-3's semantics (a bare
id covers every scenario under that requirement).

- loom-code/skills/writing-plans/references/plan-format.md — the SSOT for the
  `Brief item covered` field grammar; gains kind (d) and keeps the single-field
  rule (test_traceability_generalization.py's existing pin).
- loom-code/skills/writing-plans/references/plan-document-reviewer-prompt.md —
  Check 3's accepted-kinds list gains "(d) a REQ-<n> id or id-form join key".
- loom-code/skills/writing-plans/SKILL.md — the join-key mandate sentence
  gains the id-mode citation form.

Stdlib only (pathlib + re). Resolve reference files relative to this test.
"""

import re
from pathlib import Path

_ROOT = Path(__file__).parents[1]
_REFS = _ROOT / "skills" / "writing-plans" / "references"
PLAN_FORMAT = _REFS / "plan-format.md"
REVIEWER = _REFS / "plan-document-reviewer-prompt.md"
SKILL_MD = _ROOT / "skills" / "writing-plans" / "SKILL.md"

_REQ_ID_RE = re.compile(r"REQ-<n>")


def _text(path: Path) -> str:
    assert path.is_file(), f"reference file is absent at {path}"
    return path.read_text(encoding="utf-8")


def _names_req_id(text: str) -> bool:
    """The REQ-<n> token must appear (kind (d) names the requirement id)."""
    return bool(_REQ_ID_RE.search(text))


def _names_req_join_key(text: str) -> bool:
    """The id-form join key `<change-id> / REQ-<n> / Scenario: <name>` must
    appear co-located, so it reads as ONE referent shape rather than
    scattered mentions."""
    low = text.lower()
    if not ("change-id" in low and "req-" in low and "scenario" in low):
        return False
    lines = low.splitlines()
    for i, line in enumerate(lines):
        if "change-id" in line:
            window = "\n".join(lines[max(0, i - 3):i + 6])
            if "req-" in window and "scenario" in window:
                return True
    return False


def test_plan_format_reviewer_and_skill_name_the_req_referent():
    """All three consumers name kind (d): the REQ-<n> id and the id-form
    join key. plan-format.md must still declare exactly ONE
    `Brief item covered` field (the existing single-field pin)."""
    for path, label in (
        (PLAN_FORMAT, "plan-format.md"),
        (REVIEWER, "plan-document-reviewer-prompt.md"),
        (SKILL_MD, "SKILL.md"),
    ):
        text = _text(path)
        assert _names_req_id(text), \
            f"{label} must name the REQ-<n> referent token (kind (d))"
        assert _names_req_join_key(text), \
            (f"{label} must name the id-form join key "
             "(<change-id> / REQ-<n> / Scenario: <name>), co-located as one "
             "referent")

    # plan-format.md keeps the single-field rule: only ONE
    # `Brief item covered` field label, no competing field name introduced.
    plan_format_text = _text(PLAN_FORMAT)
    assert "Brief item covered" in plan_format_text, \
        "plan-format.md must still name the `Brief item covered` field"
    low = plan_format_text.lower()
    for stray in ("spec item covered", "scenario covered",
                  "requirement covered", "change-folder covered",
                  "req covered"):
        assert stray not in low, \
            f"must keep ONE field — found a competing field name: {stray!r}"

    # OQ-3 semantics: a bare id covers every scenario of that requirement —
    # must be stated in plan-format.md.
    assert "oq-3" in low or "every scenario" in low or "all its scenarios" in low or "requirement-level" in low, \
        ("plan-format.md must state OQ-3's semantics: a bare REQ-<n> id "
         "covers every scenario under that requirement")

    # plan-format.md must point at the id-rules SSOT rather than restate it.
    assert "requirement-identifiers.md" in plan_format_text, \
        ("plan-format.md must point at "
         "loom-design/skills/spec-expansion/references/requirement-identifiers.md "
         "for the id rules, not restate them")
