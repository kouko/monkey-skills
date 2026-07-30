"""Structural grep-window test guarding the standalone
`requesting-docs-review` skill (Task 2 of
`docs/loom/plans/2026-07-30-requesting-docs-review-standalone-skill.md`).

SKILL.md is a prompt/contract artifact, not executable code: nothing
importable observes whether the orchestrator actually caps the review
loop at 2 rounds or hands round-1 findings to round 2 verbatim. This
file IS the instruction the orchestrator reads at dispatch, so its
correctness condition is the PRESENCE of the load-bearing phrases that
make the docs arm + convergence contract executable by that reader --
same convention as `test_docs_review_mode.py` /
`test_docs_review_blocking_class.py`.

Scope: every assertion is scoped to a measured neighbourhood window
anchored on a section heading, per
`docs/loom/memory/grep-tests-scope-to-measured-neighborhood.md` --
whole-file substring greps go false-green when the asserted phrase
pre-exists elsewhere (e.g. "verbatim" appears in both the convergence
directives and the round-2 step).

Windows:
1. frontmatter -- name + trigger-phrased description (<=1536 chars).
2. convergence directives -- from the CONVERGENCE CONTRACT banner inside
   `## Process` to the first numbered orchestration step at column 0.
   The window construction itself pins PLACEMENT: the directives must
   sit at the dispatch moment, before step 1, never as a trailing prose
   aside (docs/loom/memory/
   imperative-placement-prominence-decides-weak-model-firing.md).
3. numbered steps -- the rest of `## Process`.
4. `## Aggregation rule` section.
5. `## Verdict structure` section.
6. `## Red Flags` / `## Cross-skill contract` sections.

Polarity: `test_whole_artifact_polarity_guard` proves the
whole-artifact assertion is sensitive to the regression it exists to
catch -- inverting the instruction to "reviews only the diff" must fail
the same check that passes on the real text (mirrors
`test_docs_review_mode.py::test_whole_artifact_polarity_guard`).

Stdlib + pytest only (pathlib, re).
"""
from __future__ import annotations

import re
from pathlib import Path

import pytest

SKILL_MD = (
    Path(__file__).parents[1]
    / "skills"
    / "requesting-docs-review"
    / "SKILL.md"
)


def _text() -> str:
    assert SKILL_MD.is_file(), f"SKILL.md is absent at {SKILL_MD}"
    return SKILL_MD.read_text(encoding="utf-8")


def _norm(s: str) -> str:
    """Collapse whitespace so a re-wrapped line still matches."""
    return re.sub(r"\s+", " ", s).strip()


def _frontmatter(text: str) -> str:
    m = re.match(r"^---\n(.*?)\n---\n", text, re.DOTALL)
    assert m is not None, "SKILL.md must open with a YAML frontmatter block"
    return m.group(1)


def _heading_window(text: str, heading: str) -> str:
    """Window from the `## <heading>` line to the next `## ` heading."""
    lines = text.splitlines(keepends=True)
    start = None
    for i, line in enumerate(lines):
        if line.startswith("## ") and heading.lower() in line.lower():
            start = i
            break
    assert start is not None, (
        f"SKILL.md carries no '## {heading}' heading -- this section "
        "must be findable, not absent"
    )
    end = len(lines)
    for j in range(start + 1, len(lines)):
        if lines[j].startswith("## "):
            end = j
            break
    return "".join(lines[start:end])


def _process_section(text: str) -> str:
    return _heading_window(text, "Process")


def _convergence_window(text: str) -> str:
    """The convergence-contract directives inside `## Process`.

    Runs from the line naming "CONVERGENCE CONTRACT" to the first
    numbered orchestration step at column 0 (`<digit>. `). The bold
    directives themselves (`**1. ...`) start with `**` and do not match
    that end anchor. Requiring the banner to live inside `## Process`,
    BEFORE step 1, is the placement pin: an imperative appended as a
    trailing aside after the steps would fail this extraction.
    """
    proc = _process_section(text)
    lines = proc.splitlines(keepends=True)
    start = None
    for i, line in enumerate(lines):
        if "convergence contract" in line.lower():
            start = i
            break
    assert start is not None, (
        "the CONVERGENCE CONTRACT banner must live inside `## Process` "
        "at the dispatch moment -- not elsewhere, not absent"
    )
    end = len(lines)
    for j in range(start + 1, len(lines)):
        if re.match(r"^\d+\.\s", lines[j]):
            end = j
            break
    assert end != len(lines), (
        "numbered orchestration steps must FOLLOW the convergence "
        "directives -- directives placed after the steps are a trailing "
        "aside, the placement regression this window forbids"
    )
    return "".join(lines[start:end])


def _steps_window(text: str) -> str:
    """The numbered orchestration steps of `## Process` (after the
    convergence directives)."""
    proc = _process_section(text)
    lines = proc.splitlines(keepends=True)
    start = None
    for i, line in enumerate(lines):
        if re.match(r"^\d+\.\s", line):
            start = i
            break
    assert start is not None, (
        "`## Process` carries no numbered orchestration step at column 0"
    )
    return "".join(lines[start:])


def _assert_whole_artifact(low: str) -> None:
    """Raise AssertionError unless `low` instructs whole-artifact reading
    (not diff-only) plus the unchanged-claim question."""
    assert "whole" in low, (
        "must instruct reviewers to read each changed artifact whole"
    )
    assert "diff only as context" in low or "diff as context" in low, (
        "must state the diff is context, not the review boundary"
    )
    assert (
        "does any unchanged claim in this file contradict the change, "
        "or the current code?" in low
    ), (
        "must ask the explicit unchanged-claim question verbatim -- the "
        "question that caught rounds 5-7 in the source audit "
        "(docs/loom/audits/2026-07-28-doc-branch-review-loop-audit.md "
        "§3.1)"
    )


# ---------------------------------------------------------------- tests


def test_frontmatter_name_and_trigger_description():
    """Frontmatter names the skill and phrases the description as an
    imperative trigger: fires BEFORE push/merge on docs-heavy branches,
    invoked by requesting-code-review's routing and directly."""
    fm = _frontmatter(_text())
    assert re.search(r"^name:\s*requesting-docs-review\s*$", fm, re.M), (
        "frontmatter must declare `name: requesting-docs-review`"
    )
    desc_match = re.search(
        r"^description:\s*(.*?)(?=^\w+:|\Z)", fm, re.M | re.DOTALL
    )
    assert desc_match is not None, "frontmatter must carry a description"
    desc = _norm(desc_match.group(1))
    assert len(desc) <= 1536, (
        f"description is {len(desc)} chars -- the per-skill listing "
        "budget caps at 1536"
    )
    low = desc.lower()
    assert "before" in low and ("push" in low or "merge" in low), (
        "description must fire BEFORE push/merge (imperative trigger "
        "phrasing, not a capability summary)"
    )
    assert ".md" in low, (
        "description must name the docs-only trigger surface (`.md`)"
    )
    assert "requesting-code-review" in low, (
        "description must state this skill is invoked by "
        "requesting-code-review's routing (and directly)"
    )


def test_docs_only_dispatch_trigger():
    """Step 1 states the mechanical trigger: diff non-empty AND every
    file ends in `.md`; any non-.md file routes back to
    requesting-code-review."""
    low = _norm(_steps_window(_text())).lower()
    assert "git diff main...head --name-only" in low, (
        "must name the exact trigger command -- an orchestrator at any "
        "tier must be able to run this mechanically"
    )
    assert "non-empty" in low, (
        "must state the diff must be non-empty (empty diff is vacuously "
        "true for 'all files end in .md')"
    )
    assert re.search(r"ends in `?\.md`?", low), (
        "must state the trigger predicate: every changed file ends in "
        "`.md`"
    )
    assert "non-`.md`" in low or "non-.md" in low, (
        "must state the fallback: any non-.md file means this is not a "
        "docs-only branch"
    )
    assert "requesting-code-review" in low, (
        "the non-.md fallback must route through requesting-code-review"
    )


def test_panel_dispatch_two_arm_union():
    """The dispatch mirrors requesting-code-review's two-arm convention:
    two docs-reviewer subagents, byte-identical prompts, findings
    unioned by the orchestrator."""
    low = _norm(_steps_window(_text())).lower()
    assert "docs-reviewer" in low, (
        "both arms must dispatch the docs-reviewer agent"
    )
    assert "two" in low and "panel" in low, (
        "must dispatch TWO reviewers as a panel"
    )
    assert "byte-identical" in low, (
        "the two dispatch prompts must be byte-identical to each other"
    )
    assert "union" in low, (
        "the orchestrator must union the two arms' findings"
    )


def test_whole_artifact_scope():
    """Reviewers read each changed artifact WHOLE, the diff as context,
    and ask the unchanged-claim question."""
    low = _norm(_steps_window(_text())).lower()
    _assert_whole_artifact(low)


def test_whole_artifact_polarity_guard():
    """Inverting the whole-artifact instruction to 'reviews only the
    diff' must fail the same check that passes on the real text --
    proves the guard is sensitive to the regression it exists to catch,
    not just to the section's absence (mirrors
    test_docs_review_mode.py:166-185)."""
    low = _norm(_steps_window(_text())).lower()

    # sanity: the real text passes.
    _assert_whole_artifact(low)

    key_phrase = "reads every changed artifact whole, the diff only as context"
    assert key_phrase in low, (
        "test fixture assumption broken -- SKILL.md wording changed "
        "under this test; update key_phrase to match"
    )
    mutated = low.replace(key_phrase, "reviews only the diff")

    with pytest.raises(AssertionError):
        _assert_whole_artifact(mutated)


def test_five_prose_dimensions():
    """All five prose defect dimensions are named with their inline
    definitions in the dispatch step."""
    low = _norm(_steps_window(_text())).lower()
    assert "omission" in low and "obligation or referent" in low, (
        "omission must be named and defined inline"
    )
    assert "ambiguity" in low and "without support" in low, (
        "ambiguity must be named and defined inline"
    )
    for absolute in ("only", "never", "zero"):
        assert absolute in low, (
            f"ambiguity's inline definition must enumerate {absolute!r} "
            "as an example unsupported absolute"
        )
    assert "inconsistency" in low and "changed-vs-unchanged" in low, (
        "inconsistency must be named and defined inline, including the "
        "changed-vs-unchanged case"
    )
    assert "incorrect-fact" in low and "does not support its claim" in low, (
        "incorrect-fact must be named and defined inline"
    )
    assert "missing-population" in low and "denominator" in low, (
        "missing-population must be named and defined inline (a "
        "measured number without its denominator or scope)"
    )


def test_class_taxonomy_fail_closed():
    """Every finding carries `class: instruction | evidence`; an unclear
    class fails closed to instruction."""
    low = _norm(_steps_window(_text())).lower()
    assert "class: instruction | evidence" in low, (
        "must state the tag literally as `class: instruction | evidence`"
    )
    assert "text a reader or executor will act on" in low, (
        "instruction class must be defined inline"
    )
    assert "narrative claim about what happened or is true" in low, (
        "evidence class must be defined inline"
    )
    assert "tagged `instruction`" in low or "tagged instruction" in low, (
        "a finding whose class is unclear must be tagged `instruction`"
    )
    assert "fail closed" in low, (
        "the fail-closed rationale must be stated explicitly"
    )


def test_citation_prepass_rides_dispatch_packet():
    """The check_doc_citations.py pre-pass runs first and its output
    rides the dispatch packet."""
    low = _norm(_steps_window(_text())).lower()
    assert "check_doc_citations.py" in low, (
        "must invoke the citation-check script by name"
    )
    assert "dispatch packet" in low, (
        "must state that the script's output rides the dispatch packet"
    )


def test_verdict_minting_same_marker():
    """The docs arm mints the SAME review-pass marker via
    loom_gate_markers.py; prose dimension names are schema-valid."""
    low = _norm(_steps_window(_text())).lower()
    assert "loom_gate_markers.py review-pass" in low, (
        "the verdict must mint via `loom_gate_markers.py review-pass`"
    )
    assert "same review-pass marker" in low, (
        "must state the docs arm mints the SAME marker as the code arm "
        "(a separate docs marker would break the push gate)"
    )
    assert "schema-valid" in low, (
        "must state that prose dimension names are schema-valid"
    )


def _assert_reaggregate_never_adopt_one_arm(low: str) -> None:
    """Raise AssertionError unless `low` forbids adopting either arm's
    own verdict outright -- re-aggregation over the union is mandatory,
    not stricter-arm selection (mutation probe M4, T2 quality review:
    'adopt the stricter arm's verdict' must NOT satisfy this pin)."""
    assert "re-run" in low and "aggregation rule" in low, (
        "must instruct re-running §Aggregation rule on the union"
    )
    assert "never adopt one arm's own verdict" in low, (
        "must forbid adopting either arm's own verdict verbatim -- "
        "picking the stricter arm's verdict still skips re-aggregation"
    )


def test_union_reaggregation_never_adopts_one_arm():
    """Step 4 forbids shortcutting re-aggregation by adopting one arm's
    own verdict, even the stricter one."""
    low = _norm(_steps_window(_text())).lower()
    _assert_reaggregate_never_adopt_one_arm(low)


def test_union_reaggregation_mutation_guard():
    """Mutation probe M4 (T2 quality review): rewriting 'never adopt one
    arm's own verdict' to 'adopt the stricter arm's verdict' survived all
    15 pre-existing pins as a false green. This pin must fail under that
    exact mutation -- tested in-memory only, no file is mutated."""
    low = _norm(_steps_window(_text())).lower()

    # sanity: the real text passes.
    _assert_reaggregate_never_adopt_one_arm(low)

    key_phrase = (
        "re-run §aggregation rule on the union (per-dimension score = "
        "the worse of the two arms' scores) — never adopt one arm's "
        "own verdict"
    )
    assert key_phrase in low, (
        "test fixture assumption broken -- SKILL.md wording changed "
        "under this test; update key_phrase to match"
    )
    mutated = low.replace(key_phrase, "adopt the stricter arm's verdict")

    with pytest.raises(AssertionError):
        _assert_reaggregate_never_adopt_one_arm(mutated)


def _assert_per_dimension_worse_score(low: str) -> None:
    """Raise AssertionError unless `low` states each minted dimension
    score is the WORSE of the two arms' scores (mirrors
    requesting-code-review's wording, T2 quality review correctness
    finding)."""
    assert "per-dimension score" in low, (
        "must state how the orchestrator computes per-dimension panel "
        "scores for the minted verdict"
    )
    assert "worse of the two arms" in low, (
        "per-dimension score must be the WORSE of the two arms' scores, "
        "mirroring requesting-code-review's wording verbatim"
    )


def test_per_dimension_score_is_worse_of_two_arms():
    """The minted per-dimension score is the WORSE of the two arms'
    scores -- same rule as requesting-code-review's panel aggregation."""
    low = _norm(_steps_window(_text())).lower()
    _assert_per_dimension_worse_score(low)


def test_convergence_directives():
    """The four convergence directives sit at the dispatch moment (the
    window extraction pins placement): 2-round hard cap with
    STOP-and-surface + user-authorized breach; round-1-findings-verbatim
    handoff with fix-verification before anything new; re-litigation
    ban; oscillation stop; appended-corrections rule."""
    low = _norm(_convergence_window(_text())).lower()

    # (a) hard cap 2 rounds -> STOP and surface; breach only by user.
    assert "2 review rounds" in low, (
        "directive (a) must state the hard cap: 2 review rounds"
    )
    assert "ends with needs_revision" in low, (
        "directive (a) must state the cap-STOP trigger explicitly: round 2 "
        "ending with NEEDS_REVISION -- not a bare 'without PASS' that leaves "
        "PASS_WITH_NOTES ambiguous (T4 code-quality review finding)"
    )
    assert "pass_with_notes" in low and "passing verdict" in low, (
        "directive (a) must state PASS and PASS_WITH_NOTES are both "
        "passing verdicts that end the review"
    )
    assert "stop" in low and "surviving findings" in low, (
        "after round 2 ends with NEEDS_REVISION the orchestrator must STOP "
        "and surface the surviving findings to the user"
    )
    assert "without pass" not in low, (
        "polarity guard: directive (a) must not read bare 'without PASS' -- "
        "ambiguous on whether PASS_WITH_NOTES counts; must name "
        "NEEDS_REVISION explicitly"
    )
    assert "third round" in low and "explicit user authorization" in low, (
        "a third round runs ONLY on explicit user authorization "
        "(critics' user-authorized breach precedent)"
    )

    # (b) round-2 handoff: round-1 findings verbatim, verify first.
    assert "findings verbatim" in low, (
        "the round-2 dispatch must carry round 1's findings verbatim"
    )
    assert "before raising anything new" in low, (
        "reviewers must verify each prior finding against quoted "
        "current text BEFORE raising anything new"
    )
    assert "re-raising a closed finding in new words is forbidden" in low, (
        "the re-litigation ban must be stated verbatim"
    )

    # (c) oscillation stop.
    assert "resurfaces after being fix-verified" in low, (
        "directive (c) must define oscillation: a finding resurfacing "
        "after being fix-verified"
    )
    assert "ends the loop immediately" in low, (
        "an oscillation ends the loop immediately -> user"
    )

    # (d) appended corrections.
    assert "appended corrections" in low, (
        "evidence-class fixes for unchanged prose are appended "
        "corrections"
    )
    assert "never in-place rewrites" in low, (
        "directive (d) must forbid in-place rewrites"
    )


def test_aggregation_instruction_class_only():
    """The aggregation rule applies to instruction-class findings ONLY;
    evidence-class findings are recorded observations that never gate;
    missing class fails closed; evidence-class fixes for unchanged prose
    are appended corrections."""
    low = _norm(_heading_window(_text(), "Aggregation rule")).lower()
    assert "instruction-class findings only" in low, (
        "the rule must apply to instruction-class findings only"
    )
    assert "evidence-class findings" in low and "do not gate" in low, (
        "evidence-class findings are recorded observations that do not "
        "gate"
    )
    assert "missing `class:` counts as instruction" in low, (
        "a finding missing `class:` must count as instruction (fail "
        "closed)"
    )
    assert "superseded by an appended correction" in low, (
        "an evidence-class finding against unchanged prose must be "
        "superseded by an appended correction"
    )
    assert "naming what it replaces" in low, (
        "the correction must name what it replaces"
    )
    assert "never edited in place" in low, (
        "the supersede sentence must forbid editing in place"
    )


def test_verdict_structure_prose_dimensions():
    """The verdict schema carries the five prose dimension_scores keys
    and the per-finding class key."""
    section = _heading_window(_text(), "Verdict structure")
    for dim in (
        "omission:",
        "ambiguity:",
        "inconsistency:",
        "incorrect-fact:",
        "missing-population:",
    ):
        assert dim in section, (
            f"§Verdict structure must list the `{dim}` dimension score"
        )
    assert "class: instruction | evidence" in section, (
        "§Verdict structure findings must carry the class key"
    )


def test_red_flags_refuse_one_more_round():
    """Red Flags refuse the 'just one more round' rationalization."""
    low = _norm(_heading_window(_text(), "Red Flags")).lower()
    assert "just one more round" in low, (
        "Red Flags must name and refuse 'just one more round'"
    )


def test_cross_skill_contract_names_callers():
    """Cross-skill contract names requesting-code-review and
    finishing-a-development-branch."""
    low = _norm(_heading_window(_text(), "Cross-skill contract")).lower()
    assert "requesting-code-review" in low, (
        "must name requesting-code-review (routing caller)"
    )
    assert "finishing-a-development-branch" in low, (
        "must name finishing-a-development-branch (upstream orchestrator)"
    )


def test_window_precision():
    """Windows are narrow, not whole-file greps in disguise: each
    window's distinctive phrase exists in the file exactly where
    asserted and NOT in the sibling windows."""
    text = _text()
    conv = _norm(_convergence_window(text)).lower()
    steps = _norm(_steps_window(text)).lower()
    agg = _norm(_heading_window(text, "Aggregation rule")).lower()

    # aggregation-only phrase stays out of the convergence directives.
    assert "instruction-class findings only" in agg
    assert "instruction-class findings only" not in conv, (
        "the convergence window must not swallow the aggregation rule"
    )
    # re-litigation ban lives in the directives, not the steps.
    assert "re-raising a closed finding in new words is forbidden" in conv
    assert (
        "re-raising a closed finding in new words is forbidden" not in steps
    ), (
        "the steps window must not swallow the convergence directives"
    )
    # pre-pass script name stays out of the aggregation window.
    assert "check_doc_citations.py" in steps
    assert "check_doc_citations.py" not in agg, (
        "the aggregation window must not swallow the dispatch steps"
    )
