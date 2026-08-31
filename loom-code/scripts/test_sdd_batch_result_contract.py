"""Prose-pin test: the batch-review `--result-file` shape is documented.

`batch_review_cli.py apply-result` parses a JSON result file whose key
set lives only in `_cmd_apply_result`; an orchestrator that guesses the
shape wrong falls back to per-task review exactly when a defect is found.
This pins that `conditional-operations.md` §Batch review and individual
fallback names the shape (`arm_bindings`, `terminal_results`,
`packet_identity`, `ground_ref`, the verbatim rule) and that SKILL.md's
call-contract paragraph points at it.
"""

import re
from pathlib import Path

SDD_SKILL_DIR = (
    Path(__file__).resolve().parents[1]
    / "skills"
    / "subagent-driven-development"
)
CONDITIONAL_OPERATIONS_MD = SDD_SKILL_DIR / "references" / "conditional-operations.md"
SDD_SKILL_MD = SDD_SKILL_DIR / "SKILL.md"

BATCH_HEADING = "## Batch review and individual fallback"
CALL_CONTRACT_LEAD = "The executable form of that sequence is the adapter CLI"


def _batch_section() -> str:
    text = CONDITIONAL_OPERATIONS_MD.read_text(encoding="utf-8")
    start = text.index(BATCH_HEADING) + len(BATCH_HEADING)
    match = re.search(r"^## ", text[start:], flags=re.MULTILINE)
    return text[start : start + match.start()] if match else text[start:]


def _call_contract_paragraph() -> str:
    text = SDD_SKILL_MD.read_text(encoding="utf-8")
    start = text.index(CALL_CONTRACT_LEAD)
    end = text.find("\n\n", start)
    return " ".join(text[start : end if end != -1 else None].split())


def test_conditional_operations_documents_batch_result_file():
    section = _batch_section()
    for needle in (
        "arm_bindings",
        "terminal_results",
        "packet_identity",
        "ground_ref",
        "verbatim",
    ):
        assert needle in section, f"batch section lacks {needle!r}"
    assert "conditional-operations.md" in _call_contract_paragraph()


def test_result_file_section_distinguishes_replay_observe_output():
    # `task_batch_replay.py observe --out` now writes a replay result file;
    # the apply-result section must not claim the script never writes one.
    section = _batch_section()
    assert "never writes a result file" not in section
    assert "observe --out" in section
