"""Structural grep-window test guarding the finding-class taxonomy added to
`requesting-code-review/SKILL.md`'s docs-only dispatch mode (Task 1 of
`docs/loom/plans/2026-07-30-docs-review-blocking-class.md`).

SKILL.md is a prompt/contract artifact: nothing importable observes
whether a dispatched reviewer actually tags a finding `class: instruction
| evidence`. This file IS the instruction the orchestrator and the
dispatched reviewers read, so its correctness condition is the PRESENCE
of the load-bearing phrases that make the class taxonomy executable by
that reader -- same convention as `test_docs_review_mode.py`.

Scope: two measured neighbourhood windows, per
`docs/loom/memory/grep-tests-scope-to-measured-neighborhood.md` --
whole-file substring greps go false-green when the asserted phrase
pre-exists elsewhere (e.g. "evidence" already appears once in this file's
prose at the §Asking the user boundary note, well outside either window
below).

1. The "Docs-only dispatch mode" sub-bullet under Process Step 1 (same
   section `test_docs_review_mode.py` isolates) -- covers both class
   names, both worked examples, and the fail-closed sentence.
2. The `findings:` YAML key in §Verdict structure -- covers the new
   `class:` line and its docs-mode-only marker comment.

Both windows are proven RED against the pre-change file via
`git show HEAD:loom-code/skills/requesting-code-review/SKILL.md` before
the SKILL.md edit landed (see implementer report) -- a green suite alone
never demonstrates a grep test is load-bearing.

Stdlib + pytest only (pathlib, re).
"""
from __future__ import annotations

import re
from pathlib import Path

import pytest

SKILL_MD = (
    Path(__file__).parents[1]
    / "skills"
    / "requesting-code-review"
    / "SKILL.md"
)


def _text() -> str:
    assert SKILL_MD.is_file(), f"SKILL.md is absent at {SKILL_MD}"
    return SKILL_MD.read_text(encoding="utf-8")


def _docs_mode_section(text: str) -> str:
    """Isolate the docs-only dispatch mode sub-bullet under Process Step 1.

    Runs from the line naming "Docs-only dispatch mode" to the next
    top-level Process step (a line starting with `<digit>. ` at column
    0), or end of file if none follows. Mirrors
    `test_docs_review_mode.py::_docs_mode_section`.
    """
    lines = text.splitlines(keepends=True)
    start = None
    for i, line in enumerate(lines):
        if "docs-only dispatch mode" in line.lower():
            start = i
            break
    assert start is not None, (
        "requesting-code-review/SKILL.md carries no 'Docs-only dispatch "
        "mode' text -- this section must be findable, not absent"
    )
    end = len(lines)
    for j in range(start + 1, len(lines)):
        if re.match(r"^\d+\.\s", lines[j]):
            end = j
            break
    return "".join(lines[start:end])


def _findings_block(text: str) -> str:
    """Isolate the `findings:` YAML key in §Verdict structure.

    Runs from the line `findings:` (column 0, inside the fenced verdict
    schema) to the next top-level YAML key at column 0 (e.g.
    `simplification_ledger:`), or end of file if none follows.
    """
    lines = text.splitlines(keepends=True)
    start = None
    for i, line in enumerate(lines):
        if line.strip() == "findings:":
            start = i
            break
    assert start is not None, (
        "requesting-code-review/SKILL.md carries no top-level `findings:` "
        "key in §Verdict structure"
    )
    end = len(lines)
    for j in range(start + 1, len(lines)):
        if re.match(r"^[A-Za-z_][\w-]*:", lines[j]):
            end = j
            break
    return "".join(lines[start:end])


def _norm(s: str) -> str:
    """Collapse whitespace so a re-wrapped line still matches."""
    return re.sub(r"\s+", " ", s).strip()


def _aggregation_rule_section(text: str) -> str:
    """Isolate the `**Aggregation rule**` section in §Verdict structure.

    Runs from the line naming "**Aggregation rule**" (column 0) to the
    line naming its actual next sibling heading, "**Panel union**"
    (measured against the real file -- Task 2 adds a "**Docs-only
    mode**" sub-heading INSIDE this section, so a generic
    next-bold-heading-at-column-0 scan would stop early and exclude
    it; anchoring on the real sibling name is deliberate, not a
    shortcut). Preceding this section is an unrelated
    `standards_version` paragraph, which the start anchor already
    excludes.
    """
    lines = text.splitlines(keepends=True)
    start = None
    for i, line in enumerate(lines):
        if line.lstrip().lower().startswith("**aggregation rule**"):
            start = i
            break
    assert start is not None, (
        "requesting-code-review/SKILL.md carries no '**Aggregation "
        "rule**' heading -- this section must be findable, not absent"
    )
    end = len(lines)
    for j in range(start + 1, len(lines)):
        if lines[j].lstrip().lower().startswith("**panel union**"):
            end = j
            break
    assert end != len(lines), (
        "requesting-code-review/SKILL.md carries no '**Panel union**' "
        "heading after Aggregation rule -- this window's end anchor "
        "must be findable, not absent"
    )
    return "".join(lines[start:end])


def test_docs_dispatch_defines_finding_classes():
    """The docs-only dispatch mode's clause (d) names both finding
    classes with inline definitions, one worked example per class drawn
    from the source audit, and the fail-closed default; the
    `findings:` block in §Verdict structure documents the same `class:`
    key as present for docs-mode dispatches only."""
    text = _text()

    # --- window 1: the docs-only dispatch mode sub-bullet ---
    dispatch_low = _norm(_docs_mode_section(text)).lower()

    assert "class: instruction | evidence" in dispatch_low, (
        "clause (d) must state the tag literally as `class: instruction "
        "| evidence`"
    )

    # instruction class: named, defined, and one worked example from
    # audit §2 (kpi_id derived from a canonical field slug vs. shipped
    # code doing the opposite).
    assert "instruction" in dispatch_low and (
        "text a reader or executor will act on" in dispatch_low
    ), (
        "instruction must be named and defined inline (text a reader or "
        "executor will act on)"
    )
    assert (
        "kpi_id" in dispatch_low and "canonical field slug" in dispatch_low
    ), (
        "instruction's worked example must be the audit §2 finding: a "
        "bullet instructing an implementer to derive `kpi_id` from a "
        "canonical field slug while the shipped code does the opposite"
    )
    assert "audit §2" in dispatch_low, (
        "instruction's worked example must cite its source, audit §2"
    )

    # evidence class: named, defined, and one worked example from audit
    # §4.3 (a claim attributed to a source section that does not state
    # it -- the audit attributed a variant to the brief's §Users, which
    # says "three comparative years" with no statement-type distinction).
    assert "evidence" in dispatch_low and (
        "narrative claim about what happened or is true" in dispatch_low
    ), (
        "evidence must be named and defined inline (a narrative claim "
        "about what happened or is true)"
    )
    assert "audit §4.3" in dispatch_low, (
        "evidence's worked example must cite its source, audit §4.3"
    )
    assert "attributed" in dispatch_low and (
        "§users" in dispatch_low or "attribution was wrong" in dispatch_low
    ), (
        "evidence's worked example must be a claim attributed to a "
        "source section that does not state it"
    )

    # fail-closed default.
    assert "is tagged `instruction`" in dispatch_low or (
        "tagged instruction" in dispatch_low
    ), (
        "a finding whose class is unclear must be tagged `instruction` "
        "(fail closed)"
    )
    assert "fail closed" in dispatch_low, (
        "the fail-closed rationale must be stated explicitly"
    )

    # --- window 2: the `findings:` block in §Verdict structure ---
    findings_low = _norm(_findings_block(text)).lower()

    assert "class: instruction | evidence" in findings_low, (
        "the `findings:` block must document `class: instruction | "
        "evidence` as a key, in the same shape as the existing `where:` "
        "key's inline comment"
    )
    assert "docs-mode" in findings_low and (
        "only" in findings_low
    ), (
        "the `class:` line's comment must mark it present for docs-mode "
        "dispatches only"
    )


def test_aggregation_filters_to_instruction_class():
    """The `**Aggregation rule**` section states that in docs-only mode
    the rule is applied to instruction-class findings only, that the
    rule itself is unchanged (docs mode selects its input, not its
    thresholds), that a finding missing `class:` fails closed to
    instruction, and that an evidence-class finding against settled
    narrative prose is superseded by an appended correction rather than
    edited in place (Task 2 of
    docs/loom/plans/2026-07-30-docs-review-blocking-class.md)."""
    text = _text()
    section = _norm(_aggregation_rule_section(text)).lower()

    # docs-mode filter sentence: rule applies to instruction-class
    # findings only; evidence-class findings are recorded, not a veto.
    assert "instruction-class findings only" in section, (
        "the Aggregation rule section must state that in docs-only "
        "mode the rule applies to instruction-class findings only"
    )
    assert "evidence-class findings" in section and "do not gate" in section, (
        "the Aggregation rule section must state that evidence-class "
        "findings are carried into the verdict as recorded "
        "observations that do not gate"
    )

    # aggregation-rule-unchanged statement.
    assert "rule above is unchanged" in section, (
        "the section must state explicitly that the aggregation rule "
        "itself is unchanged"
    )
    assert "docs mode selects what is fed into it" in section, (
        "the section must state that docs mode selects the rule's "
        "input, not its thresholds"
    )

    # fail-closed sentence, consistent with the existing `where:` rule.
    assert "missing `class:` counts as instruction" in section, (
        "a finding missing `class:` must count as instruction (fail "
        "closed)"
    )
    assert (
        "finding missing `where:` flipping the whole verdict" in section
    ), (
        "the fail-closed sentence must draw the explicit parallel to "
        "the existing missing-`where:` rule"
    )

    # supersede-not-edit sentence.
    assert "superseded by an appended correction" in section, (
        "an evidence-class finding against settled narrative prose "
        "must be superseded by an appended correction"
    )
    assert "naming what it replaces" in section, (
        "the correction must name what it replaces"
    )
    assert "never edited in place" in section, (
        "the supersede sentence must forbid editing in place"
    )

    # "settled" must be operationally defined, not left to judgment:
    # tied to the docs-only dispatch's UNCHANGED-claim vocabulary
    # (§Process Step 1(a)), not a free-standing undefined term.
    assert "left unchanged" in section and "§process step 1(a)" in section, (
        "the supersede sentence must anchor 'settled' to §Process "
        "Step 1(a)'s UNCHANGED-claim vocabulary, not leave it "
        "undefined"
    )

    # --- window precision: excludes the nearest sibling sections ---
    following_sibling = "each arm's own `verdict:` is advisory only"
    preceding_paragraph = (
        "lets downstream readers tell whether a verdict was scored "
        "under the rules in effect now"
    )
    full_low = _norm(text).lower()
    assert following_sibling in full_low, (
        "test fixture assumption broken -- the Panel union sentence "
        "this test checks for moved or was reworded"
    )
    assert preceding_paragraph in full_low, (
        "test fixture assumption broken -- the standards_version "
        "paragraph this test checks for moved or was reworded"
    )
    assert following_sibling not in section, (
        "the Aggregation rule window must exclude the following "
        "Panel union sibling section"
    )
    assert preceding_paragraph not in section, (
        "the Aggregation rule window must exclude the preceding "
        "standards_version paragraph"
    )


PLUGIN_JSON = Path(__file__).parents[1] / ".claude-plugin" / "plugin.json"
CHANGELOG_MD = Path(__file__).parents[1] / "CHANGELOG.md"


def test_plugin_version_and_changelog_at_0_41_0():
    """Task 3 of docs/loom/plans/2026-07-30-docs-review-blocking-class.md:
    plugin.json is bumped to 0.41.0 and CHANGELOG.md carries a matching
    `## [0.41.0]` heading. Both read from the WORKING TREE, never a
    committed blob -- an implementer cannot commit, so a test that reads
    committed content can never go green in this workflow
    (docs/loom/BACKLOG.md, "what 0.39.0 does NOT close", item 2)."""
    plugin_text = PLUGIN_JSON.read_text(encoding="utf-8")
    assert '"version": "0.41.0"' in plugin_text, (
        "loom-code/.claude-plugin/plugin.json must read version 0.41.0"
    )

    changelog_text = CHANGELOG_MD.read_text(encoding="utf-8")
    assert "## [0.41.0]" in changelog_text, (
        "loom-code/CHANGELOG.md must carry a `## [0.41.0]` heading"
    )


def test_finding_class_window_excludes_unrelated_evidence_mention():
    """Sanity guard: window 1 and window 2 do not accidentally swallow
    the pre-existing, unrelated use of the word 'evidence' in this
    file's §Asking the user boundary note -- proves the windows are
    narrow, not whole-file greps in disguise."""
    text = _text()
    unrelated_anchor = "MUST stay machine-precise and keep every evidence citation"
    assert unrelated_anchor in text, (
        "test fixture assumption broken -- the unrelated 'evidence' "
        "mention this test checks for moved or was reworded"
    )
    assert unrelated_anchor not in _docs_mode_section(text)
    assert unrelated_anchor not in _findings_block(text)
