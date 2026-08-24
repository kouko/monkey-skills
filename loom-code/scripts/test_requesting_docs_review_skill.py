"""Structural grep-window test guarding the standalone
`requesting-docs-review` skill (Task 2 of
`docs/loom/plans/2026-07-30-requesting-docs-review-standalone-skill.md`).

SKILL.md is a prompt/contract artifact, not executable code: nothing
importable observes whether the orchestrator actually honors the
bounded cap (2 rounds plus at most one mechanically-conditioned
auto-delta round) or hands round-1 findings to round 2 verbatim. This
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

REFERENCE_MD = (
    Path(__file__).parents[1]
    / "skills"
    / "requesting-docs-review"
    / "references"
    / "convergence-contract.md"
)

DOCS_REVIEWER_MD = Path(__file__).parents[1] / "agents" / "docs-reviewer.md"


def _text() -> str:
    assert SKILL_MD.is_file(), f"SKILL.md is absent at {SKILL_MD}"
    return SKILL_MD.read_text(encoding="utf-8")


def _reference_text() -> str:
    """The full verbatim convergence-contract body extracted from
    SKILL.md's `## Process` (A2, docs/loom/plans/
    2026-08-07-loom-arc4a-prose-slim.md Task 1). SKILL.md keeps only a
    pointer, a compact per-directive summary, and the hand-the-user
    decision surface; the detailed directive text -- what these pins
    check -- now lives here."""
    assert REFERENCE_MD.is_file(), (
        f"convergence-contract.md is absent at {REFERENCE_MD}"
    )
    return REFERENCE_MD.read_text(encoding="utf-8")


def _norm(s: str) -> str:
    """Collapse whitespace so a re-wrapped line still matches, and strip
    markdown emphasis markers so bold text (e.g. "last **minted**
    round") is not falsely distinct from the equivalent plain phrase
    ("last minted round") when a test checks a phrase's presence or
    absence -- three prior vacuous-pin variants in this arc were hard
    wrap, whitespace, and inline bold; this closes the inline-bold
    gap."""
    s = s.replace("*", "")
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
    assert "host-specific" in low and "fresh whole-artifact" in low, (
        "frontmatter must preserve the host-specific confirmation routes"
    )
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
    requesting-code-review.

    The trigger's scope now comes from the review-scope resolver
    (`review_scope.py`) rather than a raw `git diff` invocation --
    `docs/loom/plans/2026-08-03-review-scope-resolver.md` Task 6 requires
    deleting the unconditional branch-diff call, so this pin follows the
    new mechanism instead of the retired one."""
    low = _norm(_steps_window(_text())).lower()
    assert "review_scope.py" in low, (
        "must name the resolver CLI that supplies the scope -- an "
        "orchestrator at any tier must be able to run this mechanically"
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


def test_classification_scope_citation():
    """T9 review-round-1 fix (spec gap 1): the plan's item (a) --
    'scope -- cite Task 8's SSOT (point, don't copy)' -- was entirely
    absent from the shipped SKILL.md. A cold reader resolving scope
    before dispatching (Step 1) must be told this station reviews
    contract-class `.md` only, pointing at requesting-code-review's
    classification SSOT heading rather than re-deriving or copying the
    glob rule."""
    raw_steps = _steps_window(_text())
    low = _norm(raw_steps).lower()
    assert "contract-class" in low, (
        "Step 1 must state this station reviews contract-class `.md` "
        "only"
    )
    assert (
        "requesting-code-review" in low
        and "classification: contract-class vs record-class" in low
    ), (
        "must point at requesting-code-review's classification SSOT "
        "heading by name, not copy the glob rule inline"
    )
    # point, don't copy: the glob literals themselves must NOT be
    # duplicated here -- that would be a copy, not a citation, and would
    # drift out of lockstep with the SSOT the moment either side edits.
    # Checked against the RAW (un-normalized) window: _norm strips `*`,
    # which would silently eat the glob wildcards and vacuously pass.
    assert "<plugin>/skills/**/*.md" not in raw_steps, (
        "must cite the SSOT heading, not copy its glob literals inline "
        "-- a copy drifts; a citation cannot"
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
        "re-run §aggregation rule on the union — per-dimension score is "
        "re-aggregated from that dimension's union findings, not either "
        "arm's own: two arms contributing different findings to one "
        "dimension can each score clean alone yet union to "
        "needs_revision, which either arm's own score would miss — "
        "never adopt one arm's own verdict"
    )
    assert key_phrase in low, (
        "test fixture assumption broken -- SKILL.md wording changed "
        "under this test; update key_phrase to match"
    )
    mutated = low.replace(key_phrase, "adopt the stricter arm's verdict")

    with pytest.raises(AssertionError):
        _assert_reaggregate_never_adopt_one_arm(mutated)


def _assert_per_dimension_score_is_union_recomputed(low: str) -> None:
    """Raise AssertionError unless `low` states each minted dimension
    score is RE-AGGREGATED from that dimension's union findings, not
    copied from either arm's own score (I1 fix: worse-of-arms
    understates when the two arms contribute DIFFERENT findings to one
    dimension -- two arms that each score a dimension clean alone can
    still union to NEEDS_REVISION there, which worse-of-arms would miss
    since neither arm alone carried a 🟡/🔴 in it)."""
    assert "per-dimension score" in low, (
        "must state how the orchestrator computes per-dimension panel "
        "scores for the minted verdict"
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


def test_per_dimension_score_is_union_recomputed():
    """The minted per-dimension score is RE-AGGREGATED from that
    dimension's union findings, not the worse of the two arms' own
    scores -- worse-of-arms silently understates a dimension where the
    two arms found DIFFERENT defects (1 instruction-class 🟡 each ->
    union has 2 -> NEEDS_REVISION at the verdict level, while
    worse-of-arms still reads PASS_WITH_NOTES since neither arm alone
    crossed the threshold)."""
    low = _norm(_steps_window(_text())).lower()
    _assert_per_dimension_score_is_union_recomputed(low)


def test_per_dimension_score_union_recompute_mutation_guard():
    """Mutation probe: reverting the union-recompute wording back to
    worse-of-arms must fail this pin -- proves the pin is sensitive to
    the regression it exists to catch (the verdict/dimension_scores
    contradiction I1 closes), not just to the section going absent."""
    low = _norm(_steps_window(_text())).lower()
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


def test_convergence_directives():
    """The convergence contract sits at the dispatch moment (the window
    extraction pins placement): SKILL.md carries an imperative pointer to
    the extracted reference plus a compact per-directive summary; the
    single-round-with-confirmation contract's full text -- round 1 as the
    only full review, delta confirmation by the SAME reviewer via
    SendMessage, the "no gating findings" terminal state, and the
    session-death fallback -- lives verbatim in
    references/convergence-contract.md (Task 9 + absorbed Task 19,
    docs/loom/plans/2026-08-11-review-cost-reduction.md). This REPLACES
    the former bounded 2-round-cap-plus-auto-delta-round design in full."""
    low = _norm(_convergence_window(_text())).lower()
    ref = _norm(_reference_text()).lower()

    # placement + pointer: an imperative Read instruction to the
    # reference sits at the dispatch moment, before step 1.
    assert "read" in low and "references/convergence-contract.md" in low, (
        "SKILL.md's Process section must carry an imperative pointer to "
        "the extracted reference file"
    )
    assert "binding" in low, (
        "the pointer must state the reference's directives are binding"
    )

    # Directive 1 -- round 1 is the only full review; no gating findings
    # -> done; gating verdict -> fix, then delta confirmation.
    assert "round 1" in low and "only full review" in low, (
        "the inline summary must state round 1 is the only full review"
    )
    assert "round 1 is the only full review" in ref, (
        "the reference must state round 1 is the only full review, "
        "verbatim"
    )
    assert "no round 2, no round cap" in ref, (
        "the reference must retire the round cap explicitly"
    )
    assert "no gating findings" in low and "no gating findings" in ref, (
        "both the inline summary and the reference must state the "
        "no-gating-findings terminal outcome"
    )
    assert "delta confirmation" in low and "delta confirmation" in ref, (
        "both the inline summary and the reference must name delta "
        "confirmation as what follows a gating verdict"
    )

    # Directive 2 -- one shared post-fix packet. Claude uses the same
    # reviewer and delta; Codex uses a fresh whole-artifact review, but both
    # normalize into the two terminal confirmation outcomes.
    assert "same reviewer" in ref, (
        "the reference must state the SAME reviewer confirms the fix"
    )
    assert "sendmessage" in ref, (
        "the reference must state confirmation is dispatched via "
        "SendMessage, never a fresh Agent dispatch"
    )
    assert "fresh whole-artifact review" in low and "fresh whole-artifact review" in ref, (
        "both the inline summary and the reference must name Codex's "
        "fresh whole-artifact confirmation delivery"
    )
    assert "confirmed_resolved" in ref and "still_blocking" in ref, (
        "the reference must name both confirmation verdicts"
    )
    assert "still_blocking" in low, (
        "the inline summary must also name the STILL_BLOCKING verdict"
    )
    assert "after this one fix cycle" in ref and "stop" in ref, (
        "the reference must state STILL_BLOCKING after this one fix "
        "cycle STOPs"
    )
    assert "explicit user authorization" in ref, (
        "the reference must forbid a second cycle or a fallback round "
        "without explicit user authorization"
    )

    # Directive 3 -- terminal state is "no gating findings", never
    # "clean".
    assert "clean round is not a reachable state" in ref, (
        "the reference must state a clean round is not a reachable "
        "state (pool-arithmetic rationale)"
    )
    assert 'never as "the doc is clean."' in ref or "never \"clean\"" in ref, (
        "the reference must forbid reporting the terminal state as "
        "'clean'"
    )

    # Directive 4 -- session death before confirmation -> one fresh
    # single round.
    assert "session death" in ref or "session dies" in ref, (
        "the reference must state the session-death fallback"
    )
    assert "one fresh single round" in ref, (
        "the reference must state the fallback is one fresh single "
        "round"
    )

    # old bounded-cap machinery is gone -- both inline and reference.
    assert "2 review rounds" not in low and "2 review rounds" not in ref, (
        "the old bounded-cap phrase '2 review rounds' must not survive"
    )
    assert "auto-delta" not in low and "auto-delta" not in ref, (
        "the old auto-delta-round machinery must not survive"
    )
    assert "fourth round" not in low and "fourth round" not in ref, (
        "the old fourth-round-authorization ladder must not survive"
    )
    assert "no prior_findings_check" in ref or "prior_findings_check`" in ref, (
        "the reference must explicitly retire prior_findings_check"
    )


def test_codex_confirmation_packet_is_consistent_with_binding_convergence_contract():
    """Both hosts must judge the same post-fix evidence and normalize
    their host-native replies into the same terminal confirmation result.

    Claude's same-session delivery and Codex's fresh-review delivery may
    differ, but neither may omit the original gated findings or the delta
    evidence that binds the confirmation to the repair being judged.
    """
    ref = _norm(_reference_text()).lower()
    skill = _norm(_steps_window(_text())).lower()
    reviewer = _norm(DOCS_REVIEWER_MD.read_text(encoding="utf-8")).lower()

    required_packet = (
        "post-fix confirmation packet",
        "target_repo",
        "reviewed_sha",
        "plugin_version",
        "resources",
        "original gating findings",
        "delta evidence",
    )
    for phrase in required_packet:
        assert phrase in ref, (
            "the binding convergence reference must define the complete "
            f"post-fix confirmation packet field `{phrase}`"
        )

    for text, owner in ((skill, "SKILL.md"), (reviewer, "docs-reviewer.md")):
        assert "post-fix confirmation packet" in text, (
            f"{owner} must require the binding post-fix confirmation packet"
        )
        assert "original gating findings" in text and "delta evidence" in text, (
            f"{owner} must hand both original findings and delta evidence "
            "to every confirmation route"
        )

    frontmatter = _norm(_frontmatter(_text())).lower()
    assert "host-specific" in frontmatter and "fresh whole-artifact" in frontmatter, (
        "the dispatch-visible description must preserve both host routes"
    )

    assert "claude code" in ref and "sendmessage" in ref, (
        "the binding reference must name Claude's same-session delivery"
    )
    assert "codex" in ref and "fresh whole-artifact review" in ref, (
        "the binding reference must name Codex's fresh-review delivery"
    )
    assert "pass" in ref and "pass_with_notes" in ref and "confirmed_resolved" in ref, (
        "the binding reference must map non-gating ordinary verdicts to "
        "CONFIRMED_RESOLVED"
    )
    assert "needs_revision" in ref and "still_blocking" in ref, (
        "the binding reference must map a gating ordinary verdict to "
        "STILL_BLOCKING"
    )

    # The reviewer prompt itself must no longer carry the retired execution
    # contract. These are instruction-bearing packet/schema fields, not
    # historical prose: their presence tells a reviewer to run the old
    # two-round carrier alongside the portable post-fix confirmation packet.
    for retired in (
        "## delta-confirmation duty",
        "### round scope",
        "### prior-round findings",
        "prior_findings_check:",
        "older 2-round contract",
    ):
        assert retired not in reviewer, (
            "docs-reviewer.md must not retain the retired confirmation "
            f"execution contract `{retired}`"
        )

    assert "same session via `sendmessage`" in reviewer, (
        "docs-reviewer.md may name SendMessage only as Claude's "
        "same-session packet delivery"
    )
    assert "codex" in reviewer and "ordinary verdict" in reviewer, (
        "docs-reviewer.md must describe Codex's fresh ordinary verdict "
        "before the orchestrator normalizes it"
    )
    assert "the orchestrator normalizes each host's ordinary verdict as:" in reviewer, (
        "only the orchestrator may map each host's ordinary verdict to a "
        "confirmation outcome"
    )
    assert "in either delivery, normalize the outcome as:" not in reviewer, (
        "docs-reviewer.md must not instruct a fresh reviewer to normalize "
        "its own ordinary verdict"
    )


def test_delta_scope_rationale_carries_no_unsourced_magnitudes():
    """The delta-scope rationale sentence (Directive 1) may state only
    what the cited audit records -- direction without magnitude. The
    audit (docs/loom/audits/2026-08-04-docs-review-convergence-experiment.md)
    carries neither an edit count nor a size label for either round's
    fixes; both phrases were unsourced (I3). This rationale sentence
    moved verbatim to references/convergence-contract.md (A2, docs/loom/
    plans/2026-08-07-loom-arc4a-prose-slim.md Task 1)."""
    low = _norm(_reference_text()).lower()
    assert "four one-to-two-sentence edits" not in low, (
        "the delta-scope rationale must not carry the unsourced edit "
        "count 'four one-to-two-sentence edits' -- the audit records no "
        "such count"
    )
    assert "broad rewrite" not in low, (
        "the delta-scope rationale must not carry the unsourced size "
        "label 'broad rewrite' -- the audit records no such label"
    )


def test_delta_scope_rationale_is_size_grounded_and_attribution_correct():
    """Task 9's single-round-plus-confirmation rewrite retires the
    round-1-vs-round-2 magnitude comparison this test used to pin
    (docs/loom/plans/2026-08-11-review-cost-reduction.md Task 9, absorbing
    Task 19's convergence-contract.md rewrite): there is no round 2 to
    compare a delta size against any more, so 'larger delta' / 'smaller
    delta' no longer has anything to hang on and must NOT reappear as an
    unsourced magnitude claim. What survives from the original defect
    (Task 8, docs/loom/plans/2026-08-04-docs-review-0490-defect-fixes.md):
    the same audit citation now backs Directive 3's pool-arithmetic
    rationale honestly -- direction ('a clean round is not a reachable
    state') without a fabricated count or a mis-attributed 'next round'
    catch."""
    low = _norm(_reference_text()).lower()

    assert "three gating defects" not in low, (
        "the terminal-state rationale must not carry the unsourced count "
        "'three gating defects' from the old (b)/(c) risk sentence"
    )
    assert "the next round caught" not in low, (
        "the terminal-state rationale must not attribute a defect catch "
        "to 'the next round' -- there is no round 2 any more"
    )
    assert "larger delta" not in low and "smaller delta" not in low, (
        "the round-1-vs-round-2 delta-size comparison must not survive "
        "-- there is no round 2 to compare against under the "
        "single-round-plus-confirmation contract"
    )
    assert "2026-08-04-docs-review-convergence-experiment.md" in low, (
        "the pool-arithmetic rationale (Directive 3) must still cite the "
        "measured audit"
    )
    assert "pool-arithmetic rationale" in low, (
        "the audit citation must be attached to the pool-arithmetic "
        "rationale, not a magnitude claim"
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


def test_threshold_provenance_sentence():
    """The Aggregation rule states the inherited-threshold provenance
    honestly: the 2-🟡 bar is inherited unexamined from
    requesting-code-review, where it sits on top of a passing test
    suite the docs arm has none of."""
    low = _norm(_heading_window(_text(), "Aggregation rule")).lower()
    assert "inherited unexamined" in low, (
        "the Aggregation rule must state the thresholds are inherited "
        "unexamined from requesting-code-review"
    )
    assert "instruction-class findings only" in low, (
        "the instruction-class-only needle must survive this edit"
    )
    assert "grep-window" in low, (
        "the contrast with a passing test suite must qualify itself: "
        "the docs arm still has a grep-window test floor beneath it, "
        "per the Cross-skill contract's sibling-gate row"
    )


def test_class_default_provenance_marker():
    """The finding schema's `class:` line may carry an optional
    `(defaulted)` annotation when the reviewer fail-closed defaulted to
    `instruction` instead of judging it -- and the aggregation-equivalence
    sentence must say so verbatim, inside `## Verdict structure` (I5)."""
    section = _norm(_heading_window(_text(), "Verdict structure")).lower()
    assert "(defaulted)" in section, (
        "§Verdict structure must show the optional `(defaulted)` tag on "
        "the `class:` line"
    )
    assert "treated exactly as" in section, (
        "§Verdict structure must state the `(defaulted)` tag is treated "
        "exactly as `instruction` by the aggregation rule"
    )
    assert "class: instruction | evidence" in _heading_window(
        _text(), "Verdict structure"
    ), "the pinned `class: instruction | evidence` literal must survive"


def test_verdict_structure_retires_prior_findings_check():
    """T9 review-round-1 fix (cq 1 fatal + 1 should-fix, spec gap 2):
    §Verdict structure still carried the round-N `prior_findings_check`
    machinery, contradicting the single-round-plus-confirmation contract
    shipped in the same commit AND convergence-contract.md's own "no
    `prior_findings_check`" retirement line. Formally retire the field
    (reviewers' option (a)): the fence, its round-after-round-1 comment,
    and the resurfaced-status sentence that referenced it are gone;
    `reviewed_sha` and `out_of_scope` keep their fields but lose their
    round-N-vocabulary comments."""
    text = _text()
    section = _heading_window(text, "Verdict structure")

    # the field itself is gone -- whole file, not just the window,
    # matching the acceptance grep.
    assert "prior_findings_check" not in text, (
        "the retired prior_findings_check field must not survive "
        "anywhere in SKILL.md"
    )
    assert "resurfaced" not in text, (
        "the `resurfaced` status literal belonged to the retired field "
        "-- it must not survive either"
    )

    # reviewed_sha: field stays (still useful for provenance / the
    # delta-confirmation anchor), but the stale round-range comment
    # is gone.
    assert "reviewed_sha:" in section, (
        "reviewed_sha must survive -- it anchors the delta confirmation"
    )
    assert "next-round range" not in section, (
        "the stale 'Directive 2's next-round range starts here' comment "
        "must not survive -- there is no next round"
    )
    assert "delta" in section.lower() and (
        "provenance" in section.lower() or "anchor" in section.lower()
    ), (
        "reviewed_sha's comment must be rewritten to describe its role "
        "as delta-confirmation provenance/anchor, not a dropped comment"
    )

    # out_of_scope: field stays, but its comments no longer speak of "an
    # unbounded round" or "this round's raise scope (Directive 2)" --
    # Directive 2 is delta confirmation now, not a raise-scope rule.
    assert "out_of_scope:" in section, "out_of_scope must survive"
    assert "unbounded round" not in section, (
        "the stale 'omit on an unbounded round' comment must not survive"
    )
    assert "raise scope (directive 2)" not in section.lower(), (
        "the stale 'this round's raise scope (Directive 2)' comment "
        "must not survive -- Directive 2 no longer defines a raise scope"
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


def test_prior_findings_carrier_every_later_round():
    """The old round-N-handoff carrier (Directive 2's multi-round
    `prior_findings_check` propagation) is RETIRED, not generalized: one
    portable post-fix packet replaces it. Claude sends that packet to the
    same reviewer; Codex receives it in a fresh whole-artifact review; both
    normalize to CONFIRMED_RESOLVED or STILL_BLOCKING. No
    round-2-specific OR round-N-generalized carrier language may survive
    anywhere in the shipped text."""
    ref = _norm(_reference_text()).lower()
    assert "post-fix confirmation — one portable packet, one cycle" in ref, (
        "Directive 2 must define one portable post-fix packet and one cycle"
    )
    assert "sendmessage" in ref and "fresh whole-artifact review" in ref, (
        "Directive 2 must state both host-native confirmation deliveries"
    )
    assert "round-n handoff" not in ref, (
        "the retired round-N-handoff carrier must not survive in the "
        "reference"
    )
    assert "round 2 only" not in ref, (
        "no round-2-only restriction may survive in the reference -- "
        "Task 9 retires the mechanism entirely, not generalizes it"
    )
    assert "no `prior_findings_check`" in ref, (
        "the reference must explicitly retire prior_findings_check as a "
        "carrier, not silently drop the phrase"
    )

    low = _norm(_convergence_window(_text())).lower()
    assert "confirmed_resolved" in low and "closes the review" in low, (
        "the inline hand-the-user summary must state CONFIRMED_RESOLVED "
        "closes the review"
    )
    assert "still_blocking" in low and "hands the finding" in low, (
        "the inline hand-the-user summary must state STILL_BLOCKING "
        "hands the finding back to the user"
    )
    assert "round 2 only" not in low and "round-n handoff" not in low, (
        "the SKILL.md inline summary must not carry round-2-only or "
        "round-N-handoff language either"
    )

    steps = _norm(_steps_window(_text())).lower()
    assert "round 2 only" not in steps and "round-n handoff" not in steps, (
        "Step 3's dispatch-packet enumeration must not carry a "
        "round-2-only or round-N-handoff synonym copy"
    )


def test_round_accounting_is_session_scoped():
    """The already-reviewed-branch bullet in `## When NOT to use` must
    retract the false claim that round accounting persists across a
    session boundary. Nothing restores an orchestrator's round count
    when a new session resumes review -- the count restarts, so the
    bounded cap guards each session independently, weaker than
    continuous accounting would be. Directive 2's surrounding prose
    already covers the ledger/sha carrier gap (D2, Task 4); this bullet
    stays scoped to the round-COUNT truth, not a restatement of that
    (D3)."""
    window = _norm(_heading_window(_text(), "When NOT to use")).lower()
    assert "round accounting continues, it does not reset" not in window, (
        "must retract the false cross-session round-accounting "
        "continuity claim"
    )
    assert "session-scoped" in window, (
        "must state round accounting is session-scoped"
    )
    assert "restarts" in window, (
        "must state the round count restarts across a session boundary"
    )


def _out_of_scope_fence_window(text: str) -> str:
    """The `out_of_scope:` fence entry inside `## Verdict structure` --
    from the `out_of_scope:` line to the next top-level key line, or to
    the end of the heading window (it is the fence's last key, so there
    normally is no next key)."""
    verdict = _heading_window(text, "Verdict structure")
    lines = verdict.splitlines(keepends=True)
    start = None
    for i, line in enumerate(lines):
        if line.strip().startswith("out_of_scope:"):
            start = i
            break
    assert start is not None, (
        "`## Verdict structure` carries no `out_of_scope:` fence"
    )
    end = len(lines)
    for j in range(start + 1, len(lines)):
        if re.match(r"^[a-z_]+:", lines[j]):
            end = j
            break
    return "".join(lines[start:end])


def test_out_of_scope_not_claimed_persisted():
    """`out_of_scope:` entries carry no `severity:`, never match the
    ledger's finding regex (`_FINDING_RE`, loom_gate_markers.py), and
    nothing re-injects them into round N+1 -- the panel verdict text
    goes to an unspecified temp file. "Deferred on the record" overclaims
    a persistence the mechanism does not provide. State the honest fact
    instead: surfaced to the user with the verdict, persisted nowhere --
    deferral survives only if the user or orchestrator acts on it (D5).
    Both copies of the claim must retract: the Aggregation rule's
    out_of_scope prose bullet, and the Verdict structure fence's own
    comment."""
    agg = _norm(_heading_window(_text(), "Aggregation rule")).lower()
    assert "deferred on the record" not in agg, (
        "the Aggregation rule's out_of_scope bullet must not claim a "
        "deferred defect is 'deferred on the record' -- nothing "
        "persists it"
    )
    assert "persisted nowhere" in agg, (
        "the Aggregation rule's out_of_scope bullet must state the "
        "honest fact: surfaced to the user with the verdict, persisted "
        "nowhere"
    )

    fence = _norm(_out_of_scope_fence_window(_text())).lower()
    assert "deferred on the record" not in fence, (
        "the Verdict structure out_of_scope fence comment must not "
        "claim a suppressed defect is 'deferred on the record'"
    )
    assert "persisted nowhere" in fence, (
        "the Verdict structure out_of_scope fence comment must state "
        "the honest fact: persisted nowhere"
    )


def test_post_fix_out_of_scope_cannot_suppress_a_new_gating_problem():
    """Codex's fresh whole-artifact confirmation may find a new blocker.

    `out_of_scope` is reserved for non-gating observations on either host;
    a new gating problem must remain an ordinary scored finding so the
    orchestrator maps NEEDS_REVISION to STILL_BLOCKING.
    """
    skill = _norm(_out_of_scope_fence_window(_text())).lower()
    reviewer = _norm(DOCS_REVIEWER_MD.read_text(encoding="utf-8")).lower()

    assert "non-gating observation" in skill, (
        "the station schema must limit out_of_scope to non-gating observations"
    )
    assert "never use for a new gating problem" in skill, (
        "the station schema must forbid suppressing a new confirmation blocker"
    )
    assert "scoped to the delta only" not in skill, (
        "the station schema must not impose Claude's delta scope on Codex"
    )
    assert "non-gating observation" in reviewer, (
        "the reviewer schema must share the host-neutral out_of_scope boundary"
    )
    assert "never use for a new gating problem" in reviewer, (
        "the reviewer must keep a new confirmation blocker in findings[]"
    )


def test_window_precision():
    """Windows are narrow, not whole-file greps in disguise: each
    window's distinctive phrase exists in the file exactly where
    asserted and NOT in the sibling windows. Since Task 9
    (docs/loom/plans/2026-08-11-review-cost-reduction.md, absorbing Task
    19's convergence-contract.md rewrite) the single-round-plus-
    confirmation contract's mechanical detail lives in
    references/convergence-contract.md, not in SKILL.md's convergence
    window -- the boundary check moves with it."""
    text = _text()
    conv = _norm(_convergence_window(text)).lower()
    steps = _norm(_steps_window(text)).lower()
    agg = _norm(_heading_window(text, "Aggregation rule")).lower()
    ref = _norm(_reference_text()).lower()

    # aggregation-only phrase stays out of the convergence directives.
    assert "instruction-class findings only" in agg
    assert "instruction-class findings only" not in conv, (
        "the convergence window must not swallow the aggregation rule"
    )
    # a distinctive Directive-2 sentence lives in the extracted reference
    # only, not inline in SKILL.md's convergence window or its steps.
    distinctive = "both hosts receive this entire packet"
    assert distinctive in ref
    assert distinctive not in conv, (
        "Directive 2's full mechanical detail must not have leaked back "
        "into SKILL.md's convergence window -- it belongs in the "
        "extracted reference only"
    )
    assert distinctive not in steps, (
        "the steps window must not swallow the convergence directives"
    )
    # pre-pass script name stays out of the aggregation window.
    assert "check_doc_citations.py" in steps
    assert "check_doc_citations.py" not in agg, (
        "the aggregation window must not swallow the dispatch steps"
    )


def test_docs_dispatch_carries_portable_context_and_terminal_sha():
    """Task 4: the docs station resolves one immutable packet, copies it
    unchanged to both reviewers, and binds its docs-only marker to that
    packet's reviewed SHA.  This prevents a standalone installation from
    reconstructing plugin paths below the consumer repository or minting a
    pass for a later commit than the panel reviewed."""
    text = _text()
    steps = _norm(_steps_window(text)).lower()

    assert "active host adapter" in steps, (
        "the docs station must ask the host that loaded it to resolve its "
        "installed plugin root"
    )
    assert 'python3 "${claude_plugin_root}/scripts/review_context.py"' not in steps, (
        "a dual-host docs station must not treat Claude's environment "
        "variable as its portable root source"
    )
    assert "once" in steps and "full immutable context packet" in steps, (
        "the docs station must resolve one full immutable packet before "
        "dispatching reviewers"
    )
    for field in ("target_repo", "reviewed_sha", "plugin_version", "resources"):
        assert field in steps, (
            f"the docs station must name immutable packet field {field!r}"
        )

    dispatch_match = re.search(
        r"^3\.\s+\*\*Dispatch TWO `docs-reviewer`.*?(?=^4\.\s)",
        text,
        re.MULTILINE | re.DOTALL,
    )
    assert dispatch_match is not None, "Step 3 dispatch section must exist"
    dispatch = dispatch_match.group(0).lower()
    assert "copied verbatim" in dispatch, (
        "both docs-reviewer prompts must receive the packet unchanged"
    )
    assert "approved absolute" in dispatch and "resources" in dispatch, (
        "reviewer resource paths must remain the packet's approved "
        "absolute paths"
    )

    mint_match = re.search(
        r"^4\.\s+\*\*Wait for BOTH verdicts.*?(?=^5\.\s)",
        text,
        re.MULTILINE | re.DOTALL,
    )
    assert mint_match is not None, "Step 4 mint section must exist"
    mint = mint_match.group(0).lower()
    assert "<resources.gate_markers>" in mint, (
        "docs-only minting must use the packet-approved gate-marker path"
    )
    assert "--expected-head <reviewed_sha>" in mint, (
        "docs-only minting must bind to the packet reviewed SHA"
    )
    assert "python3 loom-code/scripts" not in text, (
        "the docs station must not reconstruct plugin scripts below the "
        "consumer repository"
    )


def test_docs_context_handoff_and_post_fix_terminal_routes_are_executable():
    """T4 remediation: an upstream packet wins over local resolution, and
    each host has a current-SHA terminal route that produces a marker-valid
    PASS artifact instead of trying to mint a confirmation token itself.

    The mutation probes keep this as a behavioral contract: merely naming
    packets, hosts, or a SHA elsewhere cannot satisfy the routing rule.
    """
    text = _text()
    steps = _steps_window(text)
    step1_match = re.search(r"^1\.\s.*?(?=^2\.\s)", steps, re.M | re.S)
    step6_match = re.search(r"^6\.\s.*?(?=^## |\Z)", steps, re.M | re.S)
    assert step1_match is not None and step6_match is not None
    step1 = _norm(step1_match.group(0)).lower()
    step6 = _norm(step6_match.group(0)).lower()

    def assert_handoff_route(value: str) -> None:
        assert "complete immutable context packet" in value
        assert "handed down" in value
        assert "consume it verbatim" in value
        assert "do not invoke review_context.py" in value
        assert "only when no complete packet was handed down" in value

    assert_handoff_route(step1)
    with pytest.raises(AssertionError):
        assert_handoff_route(
            step1.replace("do not invoke review_context.py", "may resolve again")
        )

    def assert_terminal_routes(value: str) -> None:
        assert "claude code" in value and "sendmessage" in value
        assert "same reviewer" in value
        assert "codex" in value and "fresh whole-artifact review" in value
        assert "post-fix sha" in value and "fresh immutable context packet" in value
        assert "must not mint confirmed_resolved directly" in value
        assert "schema-valid terminal wrapper" in value
        for required in ("standards_version", "reviewed_sha", "verdict: pass"):
            assert required in value
        assert "<resources.gate_markers>" in value
        assert "--expected-head <reviewed_sha>" in value

    assert_terminal_routes(step6)
    with pytest.raises(AssertionError):
        assert_terminal_routes(
            step6.replace("schema-valid terminal wrapper", "terminal note")
        )


def test_docs_station_uses_only_packet_resources_and_preserves_r3_floor():
    """Part 4 T9: direct docs review must be host-neutral and immutable.

    A station may make one context packet when none was handed down, but it
    must ask the active host adapter for that operation.  Once it has the
    packet, both scope and citation evidence are restricted to the approved
    paths and its SHA.  Terminal wrapping may make a marker-schema artifact,
    but it must not erase the R3 ``PASS_WITH_NOTES`` evidence floor.
    """
    text = _text()
    steps = _steps_window(text)
    step1_match = re.search(r"^1\.\s.*?(?=^2\.\s)", steps, re.M | re.S)
    step2_match = re.search(r"^2\.\s.*?(?=^3\.\s)", steps, re.M | re.S)
    step6_match = re.search(r"^6\.\s.*?(?=^## |\Z)", steps, re.M | re.S)
    assert step1_match is not None and step2_match is not None
    assert step6_match is not None
    step1 = _norm(step1_match.group(0)).lower()
    step2 = _norm(step2_match.group(0)).lower()
    step6 = _norm(step6_match.group(0)).lower()

    assert "active host adapter" in step1
    assert "${claude_plugin_root}" not in step1
    assert "<plugin-root>" not in step1
    assert "resources.review_scope" in step1
    assert "--reviewed-sha <reviewed_sha>" in step1

    assert "resources.doc_citation_checker" in step2
    assert "--reviewed-sha <reviewed_sha>" in step2
    assert "<plugin-root>" not in step2

    assert "pass_with_notes" in step6
    assert "r3" in step6
    assert "must not upgrade" in step6
    assert "--repo <target_repo>" in step6


def test_citation_prepass_refuses_only_operational_failures():
    """A cited-document finding is review evidence, not a broken station.

    The checker returns 1 for findings, so treating every nonzero status as
    a refusal would silently remove the pre-pass from a normal docs review.
    Conversely, usage/status 2 or a failed process means its evidence cannot
    be trusted and must stop before panel dispatch or marker minting.
    """
    steps = _steps_window(_text())
    match = re.search(r"^2\.\s.*?(?=^3\.\s)", steps, re.M | re.S)
    assert match is not None
    prepass = _norm(match.group(0)).lower()

    def assert_exit_contract(value: str) -> None:
        assert "exit 0" in value and "exit 1" in value
        assert "exit 2" in value
        assert "execution failure" in value
        assert "refuse" in value
        assert "do not dispatch" in value and "do not mint" in value
        assert "stderr" in value

    assert_exit_contract(prepass)
    with pytest.raises(AssertionError):
        assert_exit_contract(prepass.replace("exit 2", "exit 1"))
