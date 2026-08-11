"""Shared pin module for review-scope/loop-shape changes landed by the
2026-08-11 review-cost-reduction plan (docs/loom/plans/2026-08-11-review-
cost-reduction.md). Task 8 adds the first pin function; sibling tasks (7,
9, 10, 11, 12) each add one more pin function to this same module so a
partial cascade (one site updated, another forgotten) fails loudly instead
of passing silently -- plan §Notes "Classification glob SSOT chain".
"""
import re
from pathlib import Path

RCR_SKILL_MD = (
    Path(__file__).resolve().parent.parent
    / "skills"
    / "requesting-code-review"
    / "SKILL.md"
)

DOCS_REVIEWER_AGENT = (
    Path(__file__).resolve().parent.parent / "agents" / "docs-reviewer.md"
)

RDR_SKILL_MD = (
    Path(__file__).resolve().parent.parent
    / "skills"
    / "requesting-docs-review"
    / "SKILL.md"
)

FINISHING_SKILL_MD = (
    Path(__file__).resolve().parent.parent
    / "skills"
    / "finishing-a-development-branch"
    / "SKILL.md"
)

SDD_SKILL_MD = (
    Path(__file__).resolve().parent.parent
    / "skills"
    / "subagent-driven-development"
    / "SKILL.md"
)


def _rcr_text() -> str:
    return RCR_SKILL_MD.read_text(encoding="utf-8")


def _docs_reviewer_text() -> str:
    return DOCS_REVIEWER_AGENT.read_text(encoding="utf-8")


def _norm(s: str) -> str:
    """Collapse whitespace so a hard-wrapped phrase still matches a
    single-line pin, and strip markdown emphasis markers so bold text is
    not falsely distinct from the equivalent plain phrase -- mirrors
    test_docs_reviewer_agent.py's _norm. NOTE: this also strips `*`
    characters, so it must never be used to check a glob literal
    (`**/*.md`) -- check those against the raw, un-normalized slice."""
    return re.sub(r"\s+", " ", s.replace("*", "")).strip()


def _section(text: str, heading_prefix: str) -> str:
    """Slice from the first `## `-heading line starting with
    heading_prefix to the next `## `-heading line (or EOF). Scopes an
    assertion to the one section it names, so a mutation inside that
    section is guaranteed to redden the test that names it -- rather
    than a whole-file substring search a mutation elsewhere could
    accidentally keep green."""
    lines = text.splitlines(keepends=True)
    start = None
    for i, line in enumerate(lines):
        if line.startswith(heading_prefix):
            start = i
            break
    assert start is not None, f"heading {heading_prefix!r} not found in text"
    end = len(lines)
    for j in range(start + 1, len(lines)):
        if lines[j].startswith("## "):
            end = j
            break
    return "".join(lines[start:end])


def _rdr_text() -> str:
    return RDR_SKILL_MD.read_text(encoding="utf-8")


def _finishing_text() -> str:
    return FINISHING_SKILL_MD.read_text(encoding="utf-8")


def _sdd_text() -> str:
    return SDD_SKILL_MD.read_text(encoding="utf-8")


def _bold_lead_section(text: str, lead: str) -> str:
    """Slice from the line containing `lead` to the next bold-paragraph
    lead (a line starting with `**` followed by a capital letter -- the
    house bold-lead-in style subagent-driven-development/SKILL.md uses
    for this part of the file, which does NOT sit under its own `## `
    heading) or EOF. `_section()` above scopes to `## `-headings; this
    is the same clause-scoping idea applied to SKILL.md's bold-lead
    paragraphs -- mirrors test_review_weight_prose.py's `_prose_section`
    convention so a mutation inside the new paragraph is guaranteed to
    redden the test that names it, not a whole-file substring search."""
    lines = text.splitlines(keepends=True)
    start = None
    for i, line in enumerate(lines):
        if lead in line:
            start = i
            break
    assert start is not None, f"lead {lead!r} not found in text"
    end = len(lines)
    for j in range(start + 1, len(lines)):
        if re.match(r"^\*\*[A-Z]", lines[j]):
            end = j
            break
    return "".join(lines[start:end])


def test_rcr_scope_classification():
    """requesting-code-review/SKILL.md must install the contract/record
    classification SSOT (Task 8): the glob rule verbatim, the record-class
    exemption-at-any-mix statement, and the record-only continuity
    mechanism's verb name -- so Task 7's agent copy and Task 14's Python
    encoding have a stable heading + literal to cite."""
    text = _rcr_text()

    # the glob rule, verbatim per the plan's authoring literal (Task 8
    # Description / Task 7 Description, same literal in both)
    assert "<plugin>/skills/**/*.md" in text
    assert "<plugin>/agents/*.md" in text
    assert "<plugin>/hooks/*.md" in text
    assert "<plugin>/scripts/*.md" in text
    assert "README*" in text
    assert "CHANGELOG*" in text
    assert "record-class" in text and "docs/**" in text

    # record-class exemption at any mix (docs arm receives contract-class
    # files ONLY)
    assert "exempt from review at any mix" in text

    # record-only continuity mechanism, named (Task 14's marker verb)
    assert "mint --review-na-record-only" in text

    # Debt (T8 review, ride-along on Task 12): the docs-only and
    # mixed-branch Step-1 bullets' hand-off text must CLAUSE-SCOPE the
    # contract-class-only restriction, not just an unscoped whole-file
    # substring hit -- a mutation that reverts the docs-only bullet to
    # "handing it the WHOLE .md list" must redden this test. Scope
    # first via _section() to the enclosing "## Process" section
    # (excludes §Classification and §Verdict structure, which also say
    # "contract-class subset"), then slice bullet-to-bullet by the
    # literal bold-lead markers the routing prose already pins --
    # _bold_lead_section() can't isolate these because the bullets are
    # indented list items, not its line-start "**" convention.
    process = _section(text, "## Process")
    docs_only_start = process.index("**Docs-only branch**")
    mixed_start = process.index("**Mixed branch**")
    code_only_start = process.index("**Code-only branch**")
    docs_only_bullet = process[docs_only_start:mixed_start]
    mixed_bullet = process[mixed_start:code_only_start]

    assert "ONLY the contract-class subset" in docs_only_bullet, (
        "docs-only hand-off must restrict to the contract-class subset, "
        "not the whole .md list"
    )
    assert "restricted to the contract-class subset" in mixed_bullet, (
        "mixed-branch hand-off must restrict to the contract-class "
        "subset, not the whole .md list"
    )


def test_rcr_m3_upgrade_rule():
    """Task 12 (fix round, T12 code-quality-reviewer 🔴+🟡, both
    confirmed): requesting-code-review/SKILL.md must install the M3
    mechanical upgrade rule directly after Step 1's routing bullets --
    three path-based triggers that set the dispatch packet's OPTIONAL
    `model` field to `opus` (or route a contested finding to a second
    opinion / the user), plus the honesty note that catch-quality-by-
    tier is unmeasured. The 🔴 fix: the packet-field pass-down must
    also appear on the Docs-only and Mixed routing bullets themselves,
    not just in the M3 paragraph -- an inert instruction with no
    execution channel across the rdr boundary is what the reviewer
    caught. The 🟡 fix: the contested-🔴 sentence must be operational
    (who triggers it, when, exactly once, and the top-tier ceiling ->
    user), not a bare "second opinion one tier up" fragment. Clause-
    scoped to the M3 paragraph itself (first _section()-bounded to
    "## Process", then sliced from the "**M3" lead to Step 2's
    numbered marker) plus the two routing bullets sliced the same way
    test_rcr_scope_classification uses, so a mutation inside any one of
    these three clauses is guaranteed to redden this test, not a
    whole-file substring search."""
    text = _rcr_text()
    process = _section(text, "## Process")
    m3_start = process.index("**M3")
    step2_start = process.index("2. **Dispatch TWO")
    m3 = process[m3_start:step2_start]

    docs_only_start = process.index("**Docs-only branch**")
    mixed_start = process.index("**Mixed branch**")
    code_only_start = process.index("**Code-only branch**")
    docs_only_bullet = process[docs_only_start:mixed_start]
    mixed_bullet = process[mixed_start:code_only_start]

    # 🔴 fix: the packet-field pass-down is declared on BOTH routing
    # bullets that hand off to requesting-docs-review -- not just
    # asserted in the M3 paragraph with no execution channel
    assert "OPTIONAL `model` field" in docs_only_bullet, (
        "docs-only hand-off must declare the optional model pass-down "
        "field in its own dispatch-packet list"
    )
    assert "OPTIONAL `model` field" in mixed_bullet, (
        "mixed-branch hand-off must declare the optional model "
        "pass-down field in its own dispatch-packet list"
    )

    # trigger 1: any agents/*.md among changed contract-class files ->
    # packet's model field set to opus
    assert "agents/*.md" in m3
    assert "OPTIONAL `model` field to `opus`" in m3

    # trigger 2: literal threshold 10 (plan kickoff decision, Task 12)
    assert "10 or more contract-class" in m3

    # trigger 3, operationalized (🟡 fix): who triggers (delta
    # confirmation STILL_BLOCKING + fix author disputes), when (that
    # exact moment), exactly once (ONE second-opinion review), and the
    # top-tier ceiling routes to the user instead of looping forever
    assert "🔴" in m3
    assert "STILL_BLOCKING" in m3
    assert "ONE second-opinion review" in m3
    assert "one tier above the arm's current tier" in m3
    assert "already ran at the top tier" in m3 and "the user instead" in m3

    # honesty note, verbatim per the brief
    assert (
        "catch-quality-by-tier is UNMEASURED — the upgrade rule is the "
        "hedge"
    ) in m3


def test_rdr_model_override_pass_down():
    """Fix round (T12 code-quality-reviewer 🔴, confirmed): rcr's M3
    upgrade rule ("dispatch the docs arm with model: opus") has no
    execution channel unless requesting-docs-review's own dispatch-
    packet contract (§Process Step 3) and dispatch instruction both
    consume an optional `model` field. Clause-scoped to Step 3's own
    paragraph (first _section()-bounded to "## Process", then sliced
    from the "3. **Dispatch TWO" lead to Step 4's numbered marker) so
    a mutation inside this one paragraph is guaranteed to redden this
    test, not a whole-file substring search."""
    text = _rdr_text()
    process = _section(text, "## Process")
    step3_start = process.index("3. **Dispatch TWO")
    step4_start = process.index("4. **Wait for BOTH verdicts")
    step3 = process[step3_start:step4_start]

    # packet contract declares the optional field
    assert "OPTIONAL `model` field" in step3

    # Step 3's dispatch instruction actually consumes it: present ->
    # override the dispatch-time model; absent -> frontmatter default
    assert "dispatch both `docs-reviewer` subagents with that `model`" in step3
    assert "frontmatter default" in step3


def test_docs_reviewer_scope_and_confirmation():
    """docs-reviewer.md (Task 7) must carry: (a) the scope contract --
    the SAME glob literal as rcr SKILL.md's SSOT heading (byte-equal;
    Task 13's cross-file lockstep assertion pins the two against each
    other later), the SSOT-citation sentence naming the rcr heading
    (not the bare `SSOT` token, which recurs elsewhere in this file's
    injected boilerplate -- e.g. the baseline/rule-sheet blocks' own
    "SSOT note" headers), and the record-class N/A-loudly jurisdiction
    duty as ONE contiguous restrictive sentence; (b) the NEW
    delta-confirmation duty -- the CONFIRMED_RESOLVED / STILL_BLOCKING
    reply, delta-scoped via SendMessage, with the NEVER polarity on the
    whole-corpus re-sample ban intact (not just the bare noun phrase).

    Each clause is asserted inside `_section()`'s slice of the ONE
    section that carries it -- clause-scoped, not whole-file -- and the
    polarity-bearing phrases are checked as contiguous strings so a
    mutation flipping "never" -> "always", or inverting the
    jurisdiction sentence, reddens this test (manually verified against
    two temp-mutated copies; see the T7 fix-round report)."""
    text = _docs_reviewer_text()
    scope = _section(text, "## Scope contract")
    delta = _section(text, "## Delta-confirmation duty")

    # (a) scope contract: glob literal byte-equal to rcr's SSOT --
    # checked against the RAW (un-normalized) slice: _norm strips `*`,
    # which would silently eat the glob wildcards
    for literal in (
        "<plugin>/skills/**/*.md",
        "<plugin>/agents/*.md",
        "<plugin>/hooks/*.md",
        "<plugin>/scripts/*.md",
        "README*",
        "CHANGELOG*",
    ):
        assert literal in scope, (
            f"glob literal {literal!r} missing from ## Scope contract"
        )
    assert "record-class" in scope and "docs/**" in scope

    norm_scope = _norm(scope)

    # SSOT-citation sentence, contiguous -- naming the exact rcr heading
    # AND the cite-don't-re-derive instruction together, not the bare
    # "SSOT" token alone
    assert (
        'per the SSOT heading `loom-code/skills/requesting-code-review/SKILL.md` '
        '§"Classification: contract-class vs record-class" '
        '([source](../skills/requesting-code-review/SKILL.md)) '
        '— cite it, never re-derive the rule yourself'
    ) in norm_scope, (
        "the SSOT-citation sentence naming the rcr heading must survive "
        "as one contiguous sentence, not scattered independent tokens"
    )

    # record-class OUT of jurisdiction: ONE contiguous restrictive
    # sentence -- flipping "do not review them" to its positive, or
    # dropping "only" from "review only the contract-class remainder",
    # must redden this assertion
    assert (
        "do not review them: state `N/A` for that file, loudly, in your "
        "summary — and review only the contract-class remainder of "
        "the dispatch packet"
    ) in norm_scope, (
        "the jurisdiction sentence must survive as one contiguous "
        "restriction, not two independently-flippable clauses"
    )

    # (b) NEW delta-confirmation duty
    assert "SendMessage" in delta
    assert "CONFIRMED_RESOLVED" in delta
    assert "STILL_BLOCKING" in delta

    norm_delta = _norm(delta)
    assert (
        "never a fresh whole-corpus re-sample of the artifact set"
        in norm_delta
    ), (
        "the NEVER polarity must survive on the whole-corpus re-sample "
        "ban, not just the bare noun phrase"
    )


def test_rdr_single_round_confirmation():
    """requesting-docs-review/SKILL.md (Task 9) must carry the
    single-round-with-confirmation contract that REPLACES the 2-round
    cap + qualifying-shape auto-delta-round design: round 1 whole-artifact
    is the ONLY full review; a gating verdict is fixed then confirmed by
    the SAME reviewer via SendMessage, delta-scoped, never a fresh
    whole-corpus re-sample; STILL_BLOCKING after one fix cycle STOPs and
    surfaces to the user; the terminal state is 'no gating findings',
    never 'clean'; the old bounded-cap machinery (2-round cap, the
    qualifying-shape auto-delta round) is gone from the shipped text."""
    text = _rdr_text()
    low = text.lower()

    assert "round 1" in low and "only full review" in low, (
        "must state round 1 whole-artifact is the ONLY full review"
    )
    assert "delta confirmation" in low, (
        "must name the delta-confirmation step"
    )
    assert "sendmessage" in low, (
        "confirmation must be dispatched via SendMessage, not a fresh "
        "Agent dispatch"
    )
    assert "confirmed_resolved" in low and "still_blocking" in low, (
        "must name both confirmation verdicts"
    )
    assert "stop" in low and "surface" in low, (
        "STILL_BLOCKING after one fix cycle must STOP and surface to "
        "the user"
    )
    assert "no gating findings" in low, (
        "the terminal state must be 'no gating findings', never 'clean'"
    )
    assert "whole-corpus re-sample" in low, (
        "delta confirmation must never be a fresh whole-corpus re-sample"
    )

    # old bounded-cap machinery must be gone from the shipped text.
    assert "2 review rounds" not in low, (
        "the old '2 review rounds' bounded-cap phrase must not survive"
    )
    assert "auto-delta" not in low, (
        "the old auto-delta-round machinery must not survive"
    )
    assert "qualifying-shape" not in low, (
        "the old qualifying-shape auto-delta-round machinery must not "
        "survive"
    )


def test_finishing_confirmation_stop():
    """finishing-a-development-branch/SKILL.md Step 3's docs-arm routing
    (Task 10) must re-point to requesting-docs-review's single-round +
    same-reviewer delta-confirmation contract: a STILL_BLOCKING
    confirmation, dispatched via SendMessage, surfaces to the user --
    replacing the old 2-round-plus-auto-delta cap language. Verdict
    THRESHOLDS at :117/:119/:135-136 (any 🔴 fatal, or 2+ 🟡 should-fix)
    are UNTOUCHED by this task (2026-08-11 user decision) -- this test
    only checks the docs-arm loop-mechanism wording, scoped to the
    '## Default flow' section via `_section()` so a mutation elsewhere
    in the file can't false-green it."""
    section = _section(_finishing_text(), "## Default flow")
    low = section.lower()

    assert "STILL_BLOCKING" in section, (
        "Step 3 must name the STILL_BLOCKING confirmation verdict"
    )
    assert "surface" in low and "user" in low, (
        "Step 3 must surface a STILL_BLOCKING confirmation to the user"
    )
    assert "sendmessage" in low, (
        "Step 3 must name that delta confirmation is dispatched via "
        "SendMessage, matching requesting-docs-review's Directive 2"
    )

    # old 2-round-plus-auto-delta cap machinery must be gone from this section.
    assert "2 rounds" not in low, (
        "the old '2 rounds' bounded-cap phrase must not survive"
    )
    assert "auto-delta" not in low, (
        "the old auto-delta-round machinery must not survive"
    )
    assert "round-2" not in low, (
        "the old round-2 shape language must not survive"
    )
    assert "round-3" not in low, (
        "the old round-3 shape language must not survive"
    )
    assert "bounded-cap" not in low and "bounded cap" not in low, (
        "the old bounded-cap naming must not survive"
    )


def test_sdd_prose_weight_record_class_scope():
    """Task 11: subagent-driven-development/SKILL.md's "Prose
    review-weight substitution" paragraphs must add the record-class
    scope rule -- when a `Review-weight: prose` task's `Files touched`
    are ALL record-class per `requesting-code-review`'s §Classification
    SSOT (cited, not copied -- the glob literals stay in ONE place),
    the docs-reviewer substitution is N/A: dispatch spec-reviewer only
    and record "code-quality slot: N/A -- record-class prose" in the
    task summary; contract-class prose keeps the substitution
    unchanged; a mixed contract+record prose task routes docs-reviewer
    to the contract-class subset only, consistent with rcr's own
    mixed-branch routing. The paragraph must also state HOW this path
    resolves through the §Verdict resolution table (round-1
    code-quality-reviewer 🔴: N/A had no defined row) -- spec-reviewer's
    verdict alone decides, code-quality-reviewer column N/A by
    construction. The §Verdict resolution table itself is a SEPARATE
    2026-08-11 user decision left untouched by this task -- not
    asserted here, verified instead via `git diff` in the report."""
    text = _sdd_text()
    section = _bold_lead_section(text, "**Record-class scope narrowing.**")
    norm = _norm(section)

    # cites the rcr SSOT heading by name; does not copy its glob
    # literals into this file (point, don't copy)
    assert "requesting-code-review" in section
    assert "Classification: contract-class vs record-class" in section
    assert "<plugin>/skills/**/*.md" not in section, (
        "must cite the rcr SSOT heading, not copy its glob literals "
        "into SKILL.md"
    )

    # record-class-only N/A rule, as one contiguous polarity-bearing
    # sentence -- flipping "is N/A" to "still applies", or dropping
    # "only" from "dispatch spec-reviewer only", must redden this
    assert (
        "the docs-reviewer substitution is N/A: dispatch spec-reviewer "
        "only, and record"
    ) in norm, (
        "the record-class N/A rule must survive as one contiguous "
        "sentence, not scattered independently-flippable clauses"
    )
    assert '"code-quality slot: N/A — record-class prose"' in section, (
        "must name the exact task-summary marker string verbatim"
    )

    # round-1 code-quality-reviewer 🔴 fix: verdict-table composition on
    # the record-class N/A path must be spelled out -- contiguous
    # polarity-bearing phrases so a flip (e.g. "both verdicts" instead
    # of "alone", or dropping "by construction") reddens this test
    assert "spec-reviewer's verdict alone" in section, (
        "must state the record-class N/A path resolves on "
        "spec-reviewer's verdict alone, not the two-reviewer table row"
    )
    assert "N/A by construction" in section, (
        "must state the code-quality-reviewer column is N/A by "
        "construction on this path"
    )

    # contract-class prose: substitution stays unchanged
    assert "Contract-class prose keeps the substitution unchanged." in section

    # mixed contract+record prose: docs-reviewer scoped to the
    # contract-class subset only, consistent with rcr's own routing
    assert (
        "routes the docs-reviewer to the contract-class subset only"
    ) in section
    assert "mixed-branch routing" in norm

    # The §Verdict resolution table (heading + rows) is untouched by
    # this task -- verified via git diff in the report, not asserted
    # here by line number (line numbers drift; content-anchor instead).
    # This bold-lead slice must describe the record-class path's
    # resolution WITHOUT repeating the table's own heading text --
    # a belt-and-braces check that the new paragraph did not
    # accidentally swallow the neighboring ### heading.
    assert "Verdict resolution" not in section
