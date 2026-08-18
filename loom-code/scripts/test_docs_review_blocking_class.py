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


def test_plugin_version_and_changelog_at_0_88_0():
    """Originally Task 6 of
    docs/loom/plans/2026-08-02-finding-origin-attribution.md, and rewritten
    by every subsequent bump -- loom-code/CHANGELOG.md is the release
    record, so this docstring does not mirror it (the hand-maintained chain
    that used to live here grew one link per release and had drifted into
    listing its own originating plan as a later supersession).

    plugin.json is bumped to 0.88.0 and CHANGELOG.md carries a matching
    `## [0.88.0]` heading. Both read from the
    WORKING TREE, never a committed blob -- an implementer cannot commit, so a
    test that reads committed content can never go green in this workflow
    (docs/loom/backlog/2026-07-28-plan-stage-fact-grounding-what-0-39-0-does-not-close.md,
    item 2).

    This pin tracks the CURRENT shipping version by design: each bump
    rewrites it, which is what makes a missing bump fail CI rather than
    ship a silent marketplace no-op."""
    plugin_text = PLUGIN_JSON.read_text(encoding="utf-8")
    assert '"version": "0.88.0"' in plugin_text, (
        "loom-code/.claude-plugin/plugin.json must read version 0.88.0"
    )

    changelog_text = CHANGELOG_MD.read_text(encoding="utf-8")
    assert "## [0.88.0]" in changelog_text, (
        "loom-code/CHANGELOG.md must carry a `## [0.88.0]` heading"
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


# ---------------------------------------------------------------------------
# Task 10 of docs/loom/plans/2026-08-02-finding-origin-attribution.md.
#
# The `## [0.45.0]` CHANGELOG entry was written after Task 6 and describes
# the PRE-re-cut behaviour (a quote failure refuses to mint; an
# `origin_quote_tiers` marker key). Tasks 7-9 replaced both with a durable
# per-branch ledger, a grammar-only refusal, and reviewer self-derivation of
# upstream artifacts. This test pins the entry to the SHIPPED mechanism.
#
# Scope: measured window from the `## [0.45.0]` heading to the next `## [`
# heading, per `docs/loom/memory/grep-tests-scope-to-measured-neighborhood.md`
# -- never the whole file, which would let an unrelated older entry's prose
# satisfy either half of this assertion by accident.
# ---------------------------------------------------------------------------


def _changelog_0_45_0_section() -> str:
    text = CHANGELOG_MD.read_text(encoding="utf-8")
    start = text.index("## [0.45.0]")
    next_heading = re.search(r"\n## \[", text[start + 1 :])
    assert next_heading is not None, (
        "no `## [` heading follows `## [0.45.0]` -- window end anchor "
        "must be findable, not absent"
    )
    end = start + 1 + next_heading.start()
    return text[start:end]


def _sentences(text: str) -> list[str]:
    """Coarse sentence split on '.', '!', '?' followed by whitespace --
    good enough for the prose in this changelog (no abbreviations that
    end a bullet mid-sentence)."""
    return re.split(r"(?<=[.!?])\s+", text)


# A sentence claiming a quote-verification FAILURE still blocks the mint --
# the exact false claim the pre-re-cut entry made. Matched per-sentence
# (not merely "somewhere in the window") so two true, unrelated statements
# elsewhere -- "a malformed origin: line still refuses to mint" (still
# true) and "a quote is checked against head_sha" (still true) -- cannot
# combine to trip this; only a SINGLE sentence asserting both halves does.
_QUOTE_FAIL_RE = re.compile(
    r"quote[^.!?]{0,80}?"
    r"(?:does\s+not\s+verify|fails?\s+to\s+verify|is\s+unverif\w+|"
    r"unverifiable|is\s+absent|not\s+found|does\s+not\s+match)",
    re.IGNORECASE,
)
_MINT_REFUSAL_CORE_RE = re.compile(
    r"refus\w*\s+to\s+mint|block\w*\s+the\s+mint|prevent\w*\s+the\s+mint|"
    r"no\s+marker\s+is\s+written|exit\w*\s+4",
    re.IGNORECASE,
)
# A refusal-shaped phrase immediately preceded by a negator ("no longer
# blocks the mint", "never refuses to mint") is the TRUE, shipped claim,
# not the false one -- excluded via a fixed-width lookbehind-style check
# on the text right before the match (re's lookbehind must be fixed
# width, so this is done as a plain slice-and-match instead of baking the
# negation into one regex).
_NEGATED_JUST_BEFORE_RE = re.compile(
    r"(?:no\s+longer|never|does\s+not|doesn't|won't|will\s+not)\s*$",
    re.IGNORECASE,
)


def _claims_mint_refusal(sentence: str) -> bool:
    for m in _MINT_REFUSAL_CORE_RE.finditer(sentence):
        preceding = sentence[max(0, m.start() - 20) : m.start()]
        if _NEGATED_JUST_BEFORE_RE.search(preceding):
            continue
        return True
    return False


def test_changelog_0_45_0_describes_the_ledger_not_a_mint_refusal():
    section = _changelog_0_45_0_section()

    # Positive half: the entry names the durable, append-only, branch-keyed
    # ledger that Tasks 7-8 shipped as the record of truth.
    assert "origin-ledger.json" in section, (
        "0.45.0 entry does not name origin-ledger.json -- the durable "
        "record Tasks 7-8 shipped"
    )
    assert re.search(r"append-only", section, re.IGNORECASE), (
        "0.45.0 entry does not describe the ledger as append-only"
    )
    assert re.search(r"branch", section, re.IGNORECASE), (
        "0.45.0 entry does not describe the ledger as branch-keyed"
    )
    assert "NEEDS_REVISION" in section, (
        "0.45.0 entry does not state the ledger is written even on a "
        "NEEDS_REVISION round"
    )
    for status in (
        "verified-exact",
        "verified-normalised",
        "unverified-",
    ):
        assert status in section, (
            f"0.45.0 entry does not name the recorded quote_status {status!r}"
        )
    assert "self-deriv" in section.lower(), (
        "0.45.0 entry does not describe Task 9's reviewer self-derivation "
        "of upstream planning artifacts"
    )
    assert "origin_quote_tiers" not in section or "REMOVED" in section, (
        "0.45.0 entry mentions origin_quote_tiers without stating it was "
        "removed"
    )

    # Negative half, made to DISCRIMINATE rather than check a literal
    # string's absence (which would be satisfied trivially and forever by
    # construction once this entry is rewritten). Scans every sentence in
    # the window for the co-occurrence of a quote-failure clause and a
    # mint-refusal clause -- the actual false claim the pre-re-cut entry
    # made ("Refusals distinguish quote-absent-at-sha, file-absent-at-sha,
    # ... rather than collapsing to one generic failure"). Proven to fire:
    # pasting a sentence like "A quote that does not verify refuses to
    # mint the marker." into the entry makes this loop fail (see the
    # implementer's report for the before/after run).
    for sentence in _sentences(section):
        if _QUOTE_FAIL_RE.search(sentence):
            assert not _claims_mint_refusal(sentence), (
                "0.45.0 entry has a sentence claiming a quote-verification "
                f"failure still refuses/blocks the mint: {sentence!r}"
            )
