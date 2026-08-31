"""Contract guard: the batch proposer is part of the planning contract.

Pins that the two per-task reason fields, the `--check` gate line and the
reviewer's reciprocal check are written into the prose the planner and the
plan reviewer actually read -- using the field names exported by the script
so the grammar cannot drift from the oracle.

Stdlib + pytest only.
"""

from __future__ import annotations

import importlib.util
import re
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parent
WRITING_PLANS = SCRIPTS.parent / "skills" / "writing-plans"
PLAN_FORMAT = WRITING_PLANS / "references" / "plan-format.md"
SKILL = WRITING_PLANS / "SKILL.md"
REVIEWER_PROMPT = WRITING_PLANS / "references" / "plan-document-reviewer-prompt.md"

CHECK_INVOCATION = "propose_review_batches.py --check"


def _load_constants() -> tuple[str, str]:
    spec = importlib.util.spec_from_file_location(
        "propose_review_batches", SCRIPTS / "propose_review_batches.py"
    )
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module.NOT_BATCHED_FIELD, module.OVERSIZED_FIELD


def _read(path: Path) -> str:
    assert path.is_file(), f"required planning contract is absent: {path}"
    return path.read_text(encoding="utf-8")


def _section(text: str, heading: str) -> str:
    """Text from `heading` to the next `### ` subsection, skipping the
    `### Review Batch: <id>` heading that lives inside the schema's own
    fenced example."""
    start = text.index(heading)
    body = text[start + len(heading):]
    nxt = re.search(r"^### (?!Review Batch: )", body, flags=re.M)
    return text[start : start + len(heading) + (nxt.start() if nxt else len(body))]


def test_writing_plans_documents_batch_nudge_fields_and_gate():
    not_batched, oversized = _load_constants()

    review_batches = _section(_read(PLAN_FORMAT), "### Review Batches")
    assert f"- **{not_batched}**: <reason>" in review_batches, (
        f"plan-format.md §Review Batches must define the '{not_batched}' Task field"
    )
    assert f"- **{oversized}**: <reason>" in review_batches, (
        f"plan-format.md §Review Batches must define the '{oversized}' Batch field"
    )

    skill = _read(SKILL)
    gate = skill[skill.index("**Review-Batch gate (unconditional):**") :]
    gate = gate[: gate.index("\n\n")]
    assert CHECK_INVOCATION in gate, (
        "writing-plans SKILL.md's Review-Batch gate must run "
        f"`python3 loom-code/scripts/{CHECK_INVOCATION} <plan-path>`"
    )

    rows = [
        line
        for line in _read(REVIEWER_PROMPT).splitlines()
        if line.strip().startswith("| 23 |")
    ]
    assert rows and CHECK_INVOCATION in rows[0], (
        "plan-document-reviewer-prompt.md needs a `| 23 |` row that runs "
        f"`{CHECK_INVOCATION}` and treats a violation as a gap"
    )
