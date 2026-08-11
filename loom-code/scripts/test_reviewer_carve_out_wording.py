"""Prose-pin test: four reviewer contracts carry adapted carve-outs,
a purpose anchor, and the packet-interface (attention-list) rule.

@req: none (dispatch carries no registered REQ-ids for this plan)
"""
import re
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent.parent

CODE_QUALITY_REVIEWER = REPO_ROOT / "loom-code/agents/code-quality-reviewer.md"
CODE_REVIEWER = REPO_ROOT / "loom-code/agents/code-reviewer.md"
SPEC_REVIEWER = REPO_ROOT / "loom-code/agents/spec-reviewer.md"
DOCS_REVIEWER = REPO_ROOT / "loom-code/agents/docs-reviewer.md"

ALL_FOUR = [CODE_QUALITY_REVIEWER, CODE_REVIEWER, SPEC_REVIEWER, DOCS_REVIEWER]

CARVE_OUT_CODE_QUALITY_REVIEWER = (
    "You **may** run tests READ-ONLY as verdict evidence — running the "
    "package suite, re-running a RED, or probing a mutant on an extracted "
    "copy or isolated worktree is permitted and preferred over trusting "
    "reported `test_results`; you must leave no tracked file modified "
    "(after any probe, verify zero residual diff), and a test run is "
    "evidence-gathering, never a substitute for reading the artifact."
)

CARVE_OUT_CODE_REVIEWER = (
    "You **may** run tests READ-ONLY as verdict evidence — same "
    "permission and zero-residual-diff duty as the per-task reviewers; "
    "`verification-before-completion` remains the finishing gate your "
    "run does not replace."
)

CARVE_OUT_SPEC_REVIEWER = (
    "You **may** run tests READ-ONLY to verify a spec claim — e.g. that "
    "a named RED test exists and discriminates; you must leave no "
    "tracked file modified, and running tests never extends your scope "
    "into quality dimensions."
)

CARVE_OUT_DOCS_REVIEWER = (
    "Prose has no suite to run; but when `### Read context` includes "
    "code whose claims cite tests, you **may** run that suite READ-ONLY "
    "to verify the claim, leaving no tracked file modified — code-side "
    "verification remains `verification-before-completion`'s gate."
)

PURPOSE_ANCHOR = (
    "Your product is an evidence-grade verdict: prefer independent "
    "execution over reported results and experiments over static "
    "suspicion — reading the artifact is the foundation; tools only "
    "corroborate it."
)

ATTENTION_LIST_SENTENCE = (
    "The packet may carry an attention list (e.g. `Scrutinize: …`); "
    "such a list only ADDS focus — it never narrows the dimension set "
    "you must cover and never pre-judges a conclusion."
)

ABSENT_PROHIBITION = "may not** run tests"

ANTI_PATTERN_OUT_OF_SCOPE = "Running tests — out of scope"
ANTI_PATTERN_VERIFICATION_JOB = (
    "Running tests — `verification-before-completion`'s job"
)

RESIDUE_BULLET = (
    "- Leaving any tracked file modified after a test run or probe — "
    "the zero-residual-diff duty is absolute."
)

FILES_WITH_RESIDUE_BULLET = [CODE_QUALITY_REVIEWER, SPEC_REVIEWER, CODE_REVIEWER]

SSOT_REVIEWER_DISCIPLINE = REPO_ROOT / "loom-code/scripts/_reviewer-discipline.md"
REQUESTING_CODE_REVIEW_SKILL = (
    REPO_ROOT / "loom-code/skills/requesting-code-review/SKILL.md"
)

CONTRACT_CLASS_QUALIFIER = (
    "Where docs-reviewer is the routing target for authored prose, that "
    "routing is scoped to contract-class `.md` only — see "
    "`requesting-code-review/SKILL.md` §\"Classification: contract-class "
    "vs record-class\"; record-class prose is review-exempt from this "
    "routing."
)


def _normalize(text):
    return re.sub(r"\s+", " ", text).strip()


def test_code_quality_reviewer_carve_out_present():
    text = _normalize(CODE_QUALITY_REVIEWER.read_text(encoding="utf-8"))
    assert _normalize(CARVE_OUT_CODE_QUALITY_REVIEWER) in text


def test_code_reviewer_carve_out_present():
    text = _normalize(CODE_REVIEWER.read_text(encoding="utf-8"))
    assert _normalize(CARVE_OUT_CODE_REVIEWER) in text


def test_spec_reviewer_carve_out_present():
    text = _normalize(SPEC_REVIEWER.read_text(encoding="utf-8"))
    assert _normalize(CARVE_OUT_SPEC_REVIEWER) in text


def test_docs_reviewer_carve_out_present():
    text = _normalize(DOCS_REVIEWER.read_text(encoding="utf-8"))
    assert _normalize(CARVE_OUT_DOCS_REVIEWER) in text


def test_purpose_anchor_present_in_all_four():
    for path in ALL_FOUR:
        text = _normalize(path.read_text(encoding="utf-8"))
        assert _normalize(PURPOSE_ANCHOR) in text, f"missing in {path}"


def test_attention_list_sentence_present_in_all_four():
    for path in ALL_FOUR:
        text = _normalize(path.read_text(encoding="utf-8"))
        assert _normalize(ATTENTION_LIST_SENTENCE) in text, f"missing in {path}"


def test_absolute_prohibition_absent_from_all_four():
    for path in ALL_FOUR:
        text = _normalize(path.read_text(encoding="utf-8"))
        assert _normalize(ABSENT_PROHIBITION) not in text, f"still present in {path}"


def test_anti_pattern_test_ban_bullets_gone_residue_bullet_exact_three():
    """Falsified-neighbor sweep (round 2): rule 2 now permits READ-ONLY
    test runs, so the anti-pattern bullets that still banned running
    tests outright contradicted the new rule in the same file. They are
    replaced with a residue-ban bullet (rule 2's absolute condition —
    zero residual diff — not the run itself) in exactly the three files
    that had a test-ban anti-pattern bullet; docs-reviewer.md's
    anti-patterns section never had one and stays untouched."""
    for path in ALL_FOUR:
        text = _normalize(path.read_text(encoding="utf-8"))
        assert _normalize(ANTI_PATTERN_OUT_OF_SCOPE) not in text, f"still present in {path}"
        assert _normalize(ANTI_PATTERN_VERIFICATION_JOB) not in text, f"still present in {path}"

    for path in FILES_WITH_RESIDUE_BULLET:
        text = _normalize(path.read_text(encoding="utf-8"))
        assert _normalize(RESIDUE_BULLET) in text, f"missing in {path}"

    docs_text = _normalize(DOCS_REVIEWER.read_text(encoding="utf-8"))
    assert _normalize(RESIDUE_BULLET) not in docs_text


def _extract_glob_literal(text):
    """Pull the contract-class glob-pattern sentence out of a section — the
    literal path patterns, not the surrounding bold label (which is
    legitimately cased differently at sentence-start vs mid-sentence)."""
    match = re.search(r"paths matching.*?\(incl\. `docs/\*\*`\)\.", text, re.DOTALL)
    assert match, "contract-class glob literal not found"
    return _normalize(match.group(0))


def test_contract_class_qualifier_and_lockstep():
    """@req: none (dispatch carries no registered REQ-ids for this plan)

    Task 13: the shared carve-out sentence naming docs-reviewer
    (`_reviewer-discipline.md:8`) gains a contract-class qualifier —
    authored-prose routing to docs-review applies to contract-class `.md`
    only, citing Task 8's SSOT heading. Pins: (1) the qualifier ships in
    the SSOT and every synced agent copy; (2) the contract-class glob
    literal in `requesting-code-review/SKILL.md` §Classification and its
    copy in `agents/docs-reviewer.md` §Scope contract stay byte-equal
    (after whitespace normalization) — the cross-file lockstep that makes
    Tasks 7/8's authoring order irrelevant.
    """
    ssot_text = _normalize(SSOT_REVIEWER_DISCIPLINE.read_text(encoding="utf-8"))
    assert _normalize(CONTRACT_CLASS_QUALIFIER) in ssot_text

    for path in ALL_FOUR:
        text = _normalize(path.read_text(encoding="utf-8"))
        assert _normalize(CONTRACT_CLASS_QUALIFIER) in text, f"missing in {path}"

    skill_glob = _extract_glob_literal(
        REQUESTING_CODE_REVIEW_SKILL.read_text(encoding="utf-8")
    )
    docs_reviewer_glob = _extract_glob_literal(
        DOCS_REVIEWER.read_text(encoding="utf-8")
    )
    assert skill_glob == docs_reviewer_glob, (
        "contract-class glob literal drifted between "
        f"requesting-code-review/SKILL.md and docs-reviewer.md:\n"
        f"  SKILL.md:       {skill_glob}\n"
        f"  docs-reviewer:  {docs_reviewer_glob}"
    )
