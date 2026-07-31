"""Structural grep-test guarding CHK-SPEC-009 (Task 4 of
`docs/loom/plans/2026-07-31-reuse-adequacy-declaration-hardening.md`),
the `spec-consistency.md` checklist item that mirrors the
`Reuse-adequacy` schema (`writing-plans/references/plan-format.md`
§`Reuse-adequacy`) and `plan-document-reviewer` Check 17.

spec-consistency.md is prose read by the spec-reviewer subagent, not
executable code -- nothing importable can observe whether a reviewer
applied the checklist item. Its correctness condition is therefore the
PRESENCE of the load-bearing phrases that make the item checkable,
same convention as `test_plan_fact_grounding.py`.

The item has one load-bearing property this test pins: the closed
vocabulary of exactly three source markers must appear VERBATIM,
transcribed from the plan's `## Notes` PIN -- not re-derived, not
paraphrased. A checklist item that names the `Observed` slot but drops
or rewords a marker token is unenforceable against the actual
vocabulary the schema (Task 1) and Check 17 (Task 3) both use.

Stdlib only (pathlib). Reads the functional copy at the loom-code path
named in the plan's acceptance criteria (the file `subagent-driven-
development` actually loads at runtime) -- the canonical SSOT lives at
`domain-teams/skills/code-team/checklists/spec-consistency.md` and is
synced into this copy by `loom-code/scripts/distribute.py`.
"""

from pathlib import Path

CHECKLIST = (
    Path(__file__).parents[1]
    / "skills"
    / "subagent-driven-development"
    / "checklists"
    / "spec-consistency.md"
)

MARKER_TOKENS = (
    "read <repo-relative-path>:<line>",
    "inferred from docstring",
    "unverified assumption — <what would settle it>",
)


def _text() -> str:
    assert CHECKLIST.is_file(), f"spec-consistency.md is absent at {CHECKLIST}"
    return CHECKLIST.read_text(encoding="utf-8")


def test_chk_spec_009_requires_the_source_marker():
    text = _text()

    assert "CHK-SPEC-009" in text, "CHK-SPEC-009 heading is missing"
    assert "[FIXABLE]" in text.split("CHK-SPEC-009", 1)[1].split("\n", 1)[0], (
        "CHK-SPEC-009 must be tagged [FIXABLE] on its own heading line"
    )
    assert "Reuse-adequacy" in text.split("CHK-SPEC-009", 1)[1], (
        "CHK-SPEC-009 must name the Reuse-adequacy block"
    )

    section = text.split("CHK-SPEC-009", 1)[1]
    for token in MARKER_TOKENS:
        assert token in section, (
            f"CHK-SPEC-009 is missing the verbatim source marker: {token!r}"
        )

    # Deleting the opt-in scoping bullet leaves every assertion above green
    # while silently flipping CHK-SPEC-009 from "applies when the task
    # reuses a helper across lanes" to mandatory-on-every-task -- verified
    # empirically against a mutant with the bullet removed before this
    # assertion was added (Task 7 of docs/loom/plans/
    # 2026-07-31-reuse-adequacy-declaration-hardening.md).
    assert "MAY omit the block" in section, (
        "CHK-SPEC-009 must state the opt-in-by-reuse-presence scoping "
        "bullet (tasks that author new logic instead of reusing an "
        "existing helper across lanes MAY omit the block) -- its absence "
        "flips the item to mandatory on every task"
    )
