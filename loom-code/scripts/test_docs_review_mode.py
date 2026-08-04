"""Structural grep-window test guarding requesting-code-review's Step 1
three-way review routing and the narrowed trivial-skip boundary (Task 3
of `docs/loom/plans/2026-07-30-requesting-docs-review-standalone-skill.md`).

SKILL.md is a prompt/contract artifact, not executable code: nothing
importable observes whether the orchestrator actually delegates a
docs-only branch to `requesting-docs-review` instead of running the code
panel. This file IS the instruction the orchestrator reads at the
routing moment, so its correctness condition is the PRESENCE of the
load-bearing routing phrases -- same convention as
`test_plan_fact_grounding.py`.

History: this file previously pinned the INLINE docs-only dispatch mode
(whole-artifact scope, five prose dimensions, citation pre-pass). That
content relocated to `requesting-docs-review/SKILL.md` and its pins now
live in `test_requesting_docs_review_skill.py`; this file's absence
assertions guard against the relocated paragraph drifting back (the
anti-drift one-line-pointer convention).

Scope: assertions are window-scoped to the Process Step 1 sub-bullet and
the two trivial-skip table rows, per
`docs/loom/memory/grep-tests-scope-to-measured-neighborhood.md`; the
absence assertions alone run whole-file, because absence must hold
everywhere. Section text is whitespace-normalized before matching so a
re-wrapped line still matches.

Polarity: `test_worse_of_polarity_guard` proves the mixed-branch verdict
join assertion is sensitive to the regression it exists to catch --
inverting "the WORSE of the two arm verdicts" to "the better" must fail
the same check that passes on the real text.

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


def _step1_section(text: str) -> str:
    """Isolate Process Step 1 (the diff-scope + routing step).

    Runs from the column-0 line starting `1. **Determine diff scope` to
    the next top-level Process step (a line starting with `<digit>. ` at
    column 0), or end of file if none follows. Sub-bullets are indented,
    so they stay inside the window.
    """
    lines = text.splitlines(keepends=True)
    start = None
    for i, line in enumerate(lines):
        if re.match(r"^1\.\s+\*\*Determine diff scope", line):
            start = i
            break
    assert start is not None, (
        "requesting-code-review/SKILL.md carries no Process Step 1 "
        "'Determine diff scope' line -- the routing step must be "
        "findable, not absent"
    )
    end = len(lines)
    for j in range(start + 1, len(lines)):
        if re.match(r"^\d+\.\s", lines[j]):
            end = j
            break
    return "".join(lines[start:end])


def _norm(s: str) -> str:
    """Collapse whitespace so a re-wrapped line still matches, and strip
    markdown emphasis markers so bold text is not falsely distinct from
    the equivalent plain phrase when a test checks a phrase's presence
    or absence -- mirrors test_requesting_docs_review_skill.py's _norm
    (hard-wrap, whitespace, and inline-bold are the three vacuous-pin
    variants seen in this arc)."""
    s = s.replace("*", "")
    return re.sub(r"\s+", " ", s).strip()


def _assert_worse_of(low: str) -> None:
    """Raise AssertionError unless `low` states the mixed-branch verdict
    join: branch verdict = the WORSE of the two arm verdicts."""
    assert "worse of the two arm verdicts" in low, (
        "must state the mixed-branch join: the branch verdict is the "
        "WORSE of the two arm verdicts"
    )
    assert (
        "either arm `needs_revision` → branch `needs_revision`" in low
    ), (
        "must spell out the consequence: either arm NEEDS_REVISION → "
        "branch NEEDS_REVISION"
    )


def test_step1_routes_three_ways():
    """Step 1 dispatches three ways off the changed-file list: docs-only
    delegates whole to requesting-docs-review (code panel NOT run),
    mixed splits per file across both arms with a worse-of verdict
    join, code-only keeps the unchanged default path."""
    text = _text()
    low = _norm(_step1_section(text)).lower()

    # routing input: the mechanical trigger command. Post-resolver
    # (docs/loom/plans/2026-08-03-review-scope-resolver.md Task 5), the
    # file-list command is `review_scope.py`, not a raw `git diff`.
    assert "review_scope.py" in low, (
        "must name the resolver script -- an orchestrator at "
        "any tier must be able to route mechanically"
    )

    # arm 1: docs-only branch delegates WHOLE to requesting-docs-review.
    assert "non-empty" in low, (
        "docs-only arm must require a non-empty file list (empty diff "
        "is vacuously true for 'all files end in .md')"
    )
    assert re.search(r"ends in `?\.md`?", low), (
        "docs-only arm must state its predicate: every changed file "
        "ends in `.md`"
    )
    assert "requesting-docs-review" in low, (
        "docs-only arm must name the sibling skill it delegates to"
    )
    assert "delegate" in low and "whole" in low, (
        "docs-only arm must delegate the WHOLE review, not a slice"
    )
    assert "do not dispatch the code-reviewer panel" in low, (
        "docs-only arm must forbid running the code panel alongside "
        "the delegation"
    )

    # arm 2: mixed branch splits per file, joins verdicts worse-of.
    assert "per-file split" in low, (
        "mixed arm must be a per-file split, not a whole-branch pick"
    )
    assert "code-reviewer panel" in low, (
        "mixed arm must send non-.md files to the code-reviewer panel"
    )
    assert "docs-reviewer" in low, (
        "mixed arm must send .md files to the docs-reviewer agent"
    )
    assert "unions both arms' findings" in low, (
        "mixed arm must union both arms' findings for the surfaced "
        "report"
    )
    _assert_worse_of(low)

    # arm 3: code-only branch keeps the current path.
    assert re.search(r"no `?\.md`?", low) and "unchanged" in low, (
        "code-only arm must state the default code path is unchanged"
    )


def test_worse_of_polarity_guard():
    """Inverting the verdict join to 'the better of the two arm
    verdicts' must fail the same check that passes on the real text --
    proves the guard is sensitive to the regression it exists to catch,
    not just to the section's absence."""
    text = _text()
    low = _norm(_step1_section(text)).lower()

    # sanity: the real text passes.
    _assert_worse_of(low)

    key_phrase = "worse of the two arm verdicts"
    assert key_phrase in low, (
        "test fixture assumption broken -- SKILL.md wording changed "
        "under this test; update key_phrase to match"
    )
    mutated = low.replace(key_phrase, "better of the two arm verdicts")

    with pytest.raises(AssertionError):
        _assert_worse_of(mutated)


def test_old_inline_docs_mode_paragraph_absent():
    """The relocated docs-mode content must be ABSENT from this file --
    requesting-docs-review owns those semantics now (pinned in
    test_requesting_docs_review_skill.py); a copy here is drift."""
    low = _norm(_text()).lower()

    assert "docs-only dispatch mode" not in low, (
        "the old 'Docs-only dispatch mode' inline paragraph must be "
        "deleted, not kept alongside the delegation"
    )
    assert "score these five prose dimensions" not in low, (
        "the five-prose-dimensions instruction relocated to "
        "requesting-docs-review; it must not survive here"
    )
    assert "an obligation or referent the text needs and lacks" not in low, (
        "the inline dimension definitions relocated to "
        "requesting-docs-review; they must not survive here"
    )
    assert (
        "does any unchanged claim in this file contradict the change"
        not in low
    ), (
        "the whole-artifact unchanged-claim question relocated to "
        "requesting-docs-review; it must not survive here"
    )
    assert "check_doc_citations.py" not in low, (
        "the citation pre-pass invocation relocated to "
        "requesting-docs-review; it must not survive here"
    )


def _step3_section(text: str) -> str:
    """Isolate Process Step 3 (verdict aggregation + marker minting)."""
    lines = text.splitlines(keepends=True)
    start = None
    for i, line in enumerate(lines):
        if re.match(r"^3\.\s+\*\*Wait for BOTH verdicts", line):
            start = i
            break
    assert start is not None, (
        "requesting-code-review/SKILL.md carries no Process Step 3 "
        "'Wait for BOTH verdicts' line -- the mint-marker step must be "
        "findable, not absent"
    )
    end = len(lines)
    for j in range(start + 1, len(lines)):
        if re.match(r"^\d+\.\s", lines[j]):
            end = j
            break
    return "".join(lines[start:end])


def _assert_mint_once_from_joined(low: str) -> None:
    """Raise AssertionError unless the mixed-branch bullet states the
    marker is minted ONCE, from the joined verdict, and that neither
    arm self-mints on a mixed branch."""
    assert "mint the review-pass marker once" in low, (
        "mixed-branch bullet must state the marker is minted ONCE"
    )
    assert "joined verdict" in low, (
        "mixed-branch bullet must tie the single mint to the JOINED "
        "verdict, not either arm's own"
    )
    assert "neither arm mints its own marker on a mixed branch" in low, (
        "mixed-branch bullet must forbid either arm self-minting"
    )


def test_mixed_branch_mints_marker_once_from_joined_verdict():
    """Step 1's mixed-branch bullet must state the review-pass marker
    is minted ONCE from the joined (worse-of) verdict -- neither arm
    mints its own marker. Otherwise a code-arm PASS could mint a valid
    marker at HEAD while the docs arm silently refuses, and git-guard
    would let the push through on a half-reviewed branch."""
    text = _text()
    step1_raw = _step1_section(text)
    low = _norm(step1_raw).lower()
    _assert_mint_once_from_joined(low)

    # naming: the mixed bullet must name the docs arm as a PANEL
    # (requesting-docs-review's two-agent contract), not a singular
    # "the docs-reviewer agent" dispatch.
    assert "the `docs-reviewer` agent" not in step1_raw, (
        "mixed bullet must not imply a single docs-reviewer dispatch; "
        "name the docs arm per requesting-docs-review's panel contract"
    )
    assert "panel contract" in low, (
        "mixed bullet must name the docs arm via "
        "requesting-docs-review's panel contract, not a singular agent"
    )


def test_mint_once_polarity_guard():
    """Mutating 'neither arm mints its own marker' to 'each arm mints
    its own marker' must fail the same check that passes on the real
    text -- proves the guard is sensitive to the regression (a
    per-arm-mint hazard), not just to the section's absence."""
    text = _text()
    low = _norm(_step1_section(text)).lower()
    _assert_mint_once_from_joined(low)

    key_phrase = "neither arm mints its own marker on a mixed branch"
    assert key_phrase in low, (
        "test fixture assumption broken -- SKILL.md wording changed "
        "under this test; update key_phrase to match"
    )
    mutated = low.replace(
        key_phrase, "each arm mints its own marker on a mixed branch"
    )
    with pytest.raises(AssertionError):
        _assert_mint_once_from_joined(mutated)


def test_step3_mint_scoped_away_from_mixed_branch():
    """Step 3's mint instruction (mechanically minting from the code
    panel's own union) must not silently apply on a mixed branch -- it
    must say its own direct mint fires on the code-only path, deferring
    to Step 1's joined-verdict mint otherwise. Without this scoping,
    Step 3 and the mixed bullet contradict: Step 3 reads as "always
    mint here" while the mixed bullet says "mint once elsewhere"."""
    text = _text()
    low = _norm(_step3_section(text)).lower()
    assert "code-only" in low, (
        "Step 3 must scope its own direct mint action to the "
        "code-only path"
    )
    assert "mixed branch" in low, (
        "Step 3 must name the mixed-branch case it defers to Step 1's "
        "joined-verdict mint"
    )


def _assert_per_dimension_score_is_union_recomputed(low: str) -> None:
    """Raise AssertionError unless `low` states each minted dimension
    score is RE-AGGREGATED from that dimension's union findings, not
    copied from either arm's own score (I1 fix: worse-of-arms
    understates when the two arms contribute DIFFERENT findings to one
    dimension -- two arms that each score a dimension clean alone can
    still union to NEEDS_REVISION there, which worse-of-arms would
    miss)."""
    assert "per-dimension score" in low, (
        "Step 3 must state how the panel computes per-dimension scores "
        "for the minted verdict"
    )
    assert "re-aggregated from that dimension's union findings" in low, (
        "per-dimension score must be RE-AGGREGATED from that "
        "dimension's union findings, not copied from either arm"
    )
    assert "worse of the two arms' scores" not in low, (
        "must retire worse-of-arms as the per-dimension score rule -- "
        "it understates when the two arms contribute different "
        "findings to the same dimension"
    )


def test_step3_per_dimension_score_is_union_recomputed():
    """Step 3's minted per-dimension score is RE-AGGREGATED from that
    dimension's union findings, not the worse of the two arms' own
    scores -- worse-of-arms silently understates a dimension where the
    two arms found DIFFERENT defects (1 yellow each -> union has 2 ->
    NEEDS_REVISION at the verdict level, while worse-of-arms still
    reads PASS_WITH_NOTES since neither arm alone crossed the
    threshold). Mirrors requesting-docs-review's Step 4 wording."""
    text = _text()
    low = _norm(_step3_section(text)).lower()
    _assert_per_dimension_score_is_union_recomputed(low)


def test_step3_per_dimension_score_mutation_guard():
    """Mutation probe: reverting the union-recompute wording back to
    worse-of-arms must fail this pin -- proves it is sensitive to the
    regression it exists to catch, not just to the section going
    absent."""
    text = _text()
    low = _norm(_step3_section(text)).lower()
    _assert_per_dimension_score_is_union_recomputed(low)

    key_phrase = (
        "per-dimension score is re-aggregated from that dimension's "
        "union findings, not either arm's own"
    )
    assert key_phrase in low, (
        "test fixture assumption broken -- SKILL.md wording changed "
        "under this test; update key_phrase to match"
    )
    mutated = low.replace(
        key_phrase, "per-dimension score is the worse of the two arms' scores"
    )

    with pytest.raises(AssertionError):
        _assert_per_dimension_score_is_union_recomputed(mutated)


def _when_to_use_trivial_row(text: str) -> str:
    """The §When to use table row for trivial diffs."""
    for line in text.splitlines():
        if "diff is trivial" in line.lower():
            return _norm(line).lower()
    raise AssertionError(
        "requesting-code-review/SKILL.md carries no 'Diff is trivial' "
        "row in §When to use"
    )


def _when_not_to_use_trivial_row(text: str) -> str:
    """The §When NOT to use table row for trivial diffs."""
    for line in text.splitlines():
        if "**trivial diffs**" in line.lower():
            return _norm(line).lower()
    raise AssertionError(
        "requesting-code-review/SKILL.md carries no '**Trivial diffs**' "
        "row in §When NOT to use"
    )


def test_trivial_skip_narrowed_to_mechanical_doc_edits():
    """The trivial-skip exemptions no longer blanket-exempt doc
    changes: only mechanical doc edits (typo fix, version bump,
    generated/sync output) skip; authored prose routes to docs
    review."""
    text = _text()

    row_use = _when_to_use_trivial_row(text)
    assert "mechanical doc edits" in row_use, (
        "the §When to use trivial row must scope its doc exemption to "
        "mechanical doc edits"
    )
    assert "authored prose" in row_use, (
        "the §When to use trivial row must state that authored prose "
        "is not exempt"
    )
    assert "requesting-docs-review" in row_use, (
        "the §When to use trivial row must route authored prose to "
        "requesting-docs-review"
    )
    assert "doc change" not in row_use, (
        "the blanket 'doc change' exemption must be gone from the "
        "§When to use trivial row"
    )

    row_not = _when_not_to_use_trivial_row(text)
    assert "mechanical doc edits" in row_not, (
        "the §When NOT to use trivial row must scope its doc "
        "exemption to mechanical doc edits"
    )
    assert "generated/sync output" in row_not, (
        "the §When NOT to use trivial row must enumerate "
        "generated/sync output as the mechanical category"
    )
    assert "authored prose" in row_not, (
        "the §When NOT to use trivial row must state that authored "
        "prose does not qualify"
    )

    # whole-file: the blanket phrases must be gone everywhere,
    # including the Red Flags restatement of the same exemption.
    low = _norm(text).lower()
    assert "doc-only changes" not in low, (
        "the blanket 'doc-only changes' exemption must be gone"
    )
    assert "doc-only" not in low, (
        "no bare 'doc-only' exemption phrasing may survive (note: "
        "'docs-only' with an s, the routing term, is a different "
        "string and allowed)"
    )
