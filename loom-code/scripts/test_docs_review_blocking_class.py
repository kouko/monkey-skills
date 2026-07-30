"""Structural grep-window test guarding what remains of the finding-class
taxonomy in `requesting-code-review/SKILL.md` after the docs semantics
relocated to `requesting-docs-review` (Task 3 of
`docs/loom/plans/2026-07-30-requesting-docs-review-standalone-skill.md`).

History: this file previously pinned the inline class taxonomy (clause
(d) definitions, the audit §2 / §4.3 worked examples, the fail-closed
default) and the §Aggregation rule docs-mode paragraph. That content
relocated to `requesting-docs-review/SKILL.md` and its pins now live in
`test_requesting_docs_review_skill.py`; here only two things remain
load-bearing:

1. The `findings:` block in §Verdict structure keeps the `class:` key --
   the mixed-branch per-file split unions `.md`-arm findings (which
   carry `class:`) into the surfaced report, so the schema must still
   document the key, scoped to the docs arm with a pointer to the
   owning skill.
2. The §Aggregation rule section carries a one-line pointer to
   `requesting-docs-review` §Aggregation rule instead of a copy of the
   docs-mode paragraph (anti-drift convention); the relocated phrases
   must be ABSENT.

Scope: measured neighbourhood windows per
`docs/loom/memory/grep-tests-scope-to-measured-neighborhood.md`;
absence assertions run whole-file because absence must hold everywhere.

Stdlib + pytest only (pathlib, re).
"""
from __future__ import annotations

import re
from pathlib import Path

SKILL_MD = (
    Path(__file__).parents[1]
    / "skills"
    / "requesting-code-review"
    / "SKILL.md"
)


def _text() -> str:
    assert SKILL_MD.is_file(), f"SKILL.md is absent at {SKILL_MD}"
    return SKILL_MD.read_text(encoding="utf-8")


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
    line naming its actual next sibling heading, "**Panel union**".
    Preceding this section is an unrelated `standards_version`
    paragraph, which the start anchor already excludes.
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


def test_findings_class_key_scoped_to_docs_arm():
    """The `findings:` block still documents the `class:` key (the
    mixed-branch union carries `.md`-arm findings tagged with it), but
    its comment now scopes it to docs-arm findings and points at
    requesting-docs-review as the semantics owner."""
    findings_low = _norm(_findings_block(_text())).lower()

    assert "class: instruction | evidence" in findings_low, (
        "the `findings:` block must keep documenting `class: "
        "instruction | evidence` -- mixed branches union docs-arm "
        "findings that carry it"
    )
    assert "docs-arm" in findings_low, (
        "the `class:` line's comment must scope the key to docs-arm "
        "findings"
    )
    assert "requesting-docs-review" in findings_low, (
        "the `class:` line's comment must point at "
        "requesting-docs-review as the semantics owner, not restate "
        "the semantics"
    )


def test_aggregation_pointer_replaces_docs_paragraph():
    """The §Aggregation rule section carries a one-line pointer to
    requesting-docs-review instead of the relocated docs-mode
    paragraph; the relocated phrases are absent from the whole file."""
    text = _text()
    section = _norm(_aggregation_rule_section(text)).lower()

    # the pointer.
    assert "requesting-docs-review" in section, (
        "the Aggregation rule section must point docs findings at "
        "requesting-docs-review §Aggregation rule"
    )

    # relocated phrases must be gone -- whole file, not just the window.
    low = _norm(text).lower()
    assert "instruction-class findings only" not in low, (
        "the instruction-only filter sentence relocated to "
        "requesting-docs-review; it must not survive here"
    )
    assert "docs mode selects what is fed into it" not in low, (
        "the rule-unchanged sentence relocated to "
        "requesting-docs-review; it must not survive here"
    )
    assert "missing `class:` counts as instruction" not in low, (
        "the fail-closed class sentence relocated to "
        "requesting-docs-review; it must not survive here"
    )
    assert "superseded by an appended correction" not in low, (
        "the appended-corrections rule relocated to "
        "requesting-docs-review; it must not survive here"
    )
    assert "text a reader or executor will act on" not in low, (
        "the instruction-class inline definition relocated to "
        "requesting-docs-review; it must not survive here"
    )
    assert "kpi_id" not in low and "audit §4.3" not in low, (
        "the audit worked examples relocated to requesting-docs-review; "
        "they must not survive here"
    )

    # window precision: the pointer window excludes its siblings.
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


def test_plugin_version_and_changelog_at_0_42_0():
    """Task 7 of docs/loom/plans/2026-07-30-requesting-docs-review-standalone-skill.md:
    plugin.json is bumped to 0.42.0 and CHANGELOG.md carries a matching
    `## [0.42.0]` heading. Both read from the WORKING TREE, never a
    committed blob -- an implementer cannot commit, so a test that reads
    committed content can never go green in this workflow
    (docs/loom/BACKLOG.md, "what 0.39.0 does NOT close", item 2)."""
    plugin_text = PLUGIN_JSON.read_text(encoding="utf-8")
    assert '"version": "0.42.0"' in plugin_text, (
        "loom-code/.claude-plugin/plugin.json must read version 0.42.0"
    )

    changelog_text = CHANGELOG_MD.read_text(encoding="utf-8")
    assert "## [0.42.0]" in changelog_text, (
        "loom-code/CHANGELOG.md must carry a `## [0.42.0]` heading"
    )


def test_findings_window_excludes_unrelated_evidence_mention():
    """Sanity guard: the `findings:` window does not accidentally
    swallow the pre-existing, unrelated use of the word 'evidence' in
    this file's §Asking the user boundary note -- proves the window is
    narrow, not a whole-file grep in disguise."""
    text = _text()
    unrelated_anchor = "MUST stay machine-precise and keep every evidence citation"
    assert unrelated_anchor in text, (
        "test fixture assumption broken -- the unrelated 'evidence' "
        "mention this test checks for moved or was reworded"
    )
    assert unrelated_anchor not in _findings_block(text)
