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


def _normalize(text):
    return re.sub(r"\s+", " ", text).strip()


def test_code_quality_reviewer_carve_out_present():
    text = _normalize(CODE_QUALITY_REVIEWER.read_text())
    assert _normalize(CARVE_OUT_CODE_QUALITY_REVIEWER) in text


def test_code_reviewer_carve_out_present():
    text = _normalize(CODE_REVIEWER.read_text())
    assert _normalize(CARVE_OUT_CODE_REVIEWER) in text


def test_spec_reviewer_carve_out_present():
    text = _normalize(SPEC_REVIEWER.read_text())
    assert _normalize(CARVE_OUT_SPEC_REVIEWER) in text


def test_docs_reviewer_carve_out_present():
    text = _normalize(DOCS_REVIEWER.read_text())
    assert _normalize(CARVE_OUT_DOCS_REVIEWER) in text


def test_purpose_anchor_present_in_all_four():
    for path in ALL_FOUR:
        text = _normalize(path.read_text())
        assert _normalize(PURPOSE_ANCHOR) in text, f"missing in {path}"


def test_attention_list_sentence_present_in_all_four():
    for path in ALL_FOUR:
        text = _normalize(path.read_text())
        assert _normalize(ATTENTION_LIST_SENTENCE) in text, f"missing in {path}"


def test_absolute_prohibition_absent_from_all_four():
    for path in ALL_FOUR:
        text = _normalize(path.read_text())
        assert _normalize(ABSENT_PROHIBITION) not in text, f"still present in {path}"
