"""Prose-pin test: R3's opening is a conditional fallback, not an absolute.

@req: none (dispatch carries no registered REQ-ids for this plan)
"""
import re
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent.parent

SSOT_PATH = REPO_ROOT / "loom-code/scripts/_reviewer-discipline.md"
AGENT_PATHS = [
    REPO_ROOT / "loom-code/agents/code-quality-reviewer.md",
    REPO_ROOT / "loom-code/agents/code-reviewer.md",
    REPO_ROOT / "loom-code/agents/spec-reviewer.md",
    REPO_ROOT / "loom-code/agents/docs-reviewer.md",
]
ALL_PATHS = [SSOT_PATH] + AGENT_PATHS

CONDITIONAL_OPENING = (
    "When a dimension's PASS rests on the implementer's reported "
    "`test_results` or other evidence you did not independently confirm — "
    "whether the check could not run (environment, capacity, no runnable "
    "check exists) or you simply did not run it — do not emit a clean "
    "PASS for it"
)

ROUND1_OPENING = (
    "When you could not run the relevant check yourself — environment, "
    "capacity, or no runnable check exists — a dimension's PASS resting on "
    "the implementer's reported `test_results` or other evidence you could "
    "not independently confirm must not ship clean; do not emit a clean "
    "PASS for it"
)

ABSOLUTE_OPENING = "You may not run tests;"


def _normalize(text):
    return re.sub(r"\s+", " ", text).strip()


def test_conditional_opening_present_in_ssot():
    text = _normalize(SSOT_PATH.read_text(encoding="utf-8"))
    assert _normalize(CONDITIONAL_OPENING) in text


def test_conditional_opening_present_in_all_four_agents():
    for path in AGENT_PATHS:
        text = _normalize(path.read_text(encoding="utf-8"))
        assert _normalize(CONDITIONAL_OPENING) in text, f"missing in {path}"


def test_absolute_opening_absent_from_all_five():
    for path in ALL_PATHS:
        text = _normalize(path.read_text(encoding="utf-8"))
        assert _normalize(ABSOLUTE_OPENING) not in text, f"still present in {path}"


def test_round1_opening_absent_from_all_five():
    for path in ALL_PATHS:
        text = _normalize(path.read_text(encoding="utf-8"))
        assert _normalize(ROUND1_OPENING) not in text, f"still present in {path}"


def test_never_false_pass_still_present_in_all_five():
    for path in ALL_PATHS:
        text = _normalize(path.read_text(encoding="utf-8"))
        assert _normalize("Never false-pass") in text, f"missing in {path}"
