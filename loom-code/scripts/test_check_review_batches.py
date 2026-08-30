"""CLI contract matrix for the Review Batch plan-schema oracle."""

from __future__ import annotations

import os
from pathlib import Path
import subprocess
import sys

import pytest


SCRIPT = Path(__file__).with_name("check_review_batches.py")
_ENV = dict(os.environ, PYTHONDONTWRITEBYTECODE="1")


def _task(
    number: int,
    *,
    dependencies: str = "none",
    disposition: str | None = "individual",
    review_weight: str | None = None,
) -> str:
    disposition_line = (
        f"- **Review disposition**: {disposition}\n"
        if disposition is not None
        else ""
    )
    weight_line = (
        f"- **Review-weight**: {review_weight}\n"
        if review_weight is not None
        else ""
    )
    return f"""\
## Task {number} — Task {number}

- **Description**: Implement Task {number}.
- **Module**: `module_{number}.py`
- **Files touched**: `module_{number}.py`
- **Acceptance**:
  - **RED**: fails before Task {number}.
  - **GREEN**: passes after Task {number}.
- **Dependencies**: {dependencies}
{weight_line}{disposition_line}- **Status**: pending
"""


def _batch(
    batch_id: str = "renderers",
    *,
    members: str = "Task 1, Task 2",
    verdict: str | None = "Does the renderer capability satisfy its contract?",
    lane: str | None = "full",
    verification: str | None = "`python3 -m pytest tests/renderers -q`",
    boundary: str | None = (
        "capability: renderers; exclusions: none; consumable: yes"
    ),
) -> str:
    fields = [f"### Review Batch: {batch_id}", f"- **Members**: {members}"]
    for name, value in (
        ("Verdict question", verdict),
        ("Review lane", lane),
        ("Aggregate verification", verification),
        ("Boundary", boundary),
    ):
        if value is not None:
            fields.append(f"- **{name}**: {value}")
    return "## Review Batches\n\n" + "\n".join(fields) + "\n"


def _valid_plan() -> str:
    return (
        _task(1, disposition="batch(renderers)")
        + "\n"
        + _task(
            2,
            dependencies="Task 1 completes first",
            disposition="batch(renderers)",
        )
        + "\n"
        + _task(3)
        + "\n"
        + _batch()
    )


def _run(tmp_path: Path, plan: str) -> subprocess.CompletedProcess[str]:
    plan_path = tmp_path / "plan.md"
    plan_path.write_text(plan, encoding="utf-8")
    return subprocess.run(
        [sys.executable, str(SCRIPT), str(plan_path)],
        capture_output=True,
        text=True,
        env=_ENV,
        check=False,
    )


# @req: REQ-99
# @req: REQ-100
# @req: REQ-101
# @req: REQ-102
@pytest.mark.parametrize(
    ("case", "mutate", "expected_fragment"),
    [
        ("valid", lambda plan: plan, "Review Batch schema valid"),
        (
            "incomplete DAG",
            lambda plan: plan.replace("- **Dependencies**: none\n", "", 1),
            "Dependencies",
        ),
        (
            "dependency cycle",
            lambda plan: plan.replace(
                "- **Dependencies**: none\n", "- **Dependencies**: Task 2 completes first\n", 1
            ),
            "cycle",
        ),
        (
            "missing disposition",
            lambda plan: plan.replace("- **Review disposition**: individual\n", "", 1),
            "exactly one review disposition",
        ),
        (
            "contradictory disposition",
            lambda plan: plan.replace(
                "- **Review disposition**: individual\n",
                "- **Review disposition**: individual\n"
                "- **Review disposition**: batch(renderers)\n",
                1,
            ),
            "exactly one review disposition",
        ),
        (
            "duplicate membership",
            lambda plan: plan.replace(
                "- **Members**: Task 1, Task 2",
                "- **Members**: Task 1, Task 1, Task 2",
            ),
            "duplicate member",
        ),
        (
            "dangling membership",
            lambda plan: plan.replace(
                "- **Members**: Task 1, Task 2",
                "- **Members**: Task 1, Task 2, Task 9",
            ),
            "unknown Task 9",
        ),
        (
            "dangling batch disposition",
            lambda plan: plan.replace("batch(renderers)", "batch(missing)", 1),
            "unknown Review Batch",
        ),
        (
            "missing batch field",
            lambda plan: plan.replace(
                "- **Aggregate verification**: `python3 -m pytest tests/renderers -q`\n",
                "",
            ),
            "Aggregate verification",
        ),
        (
            "ambiguous verdict",
            lambda plan: plan.replace(
                "Does the renderer capability satisfy its contract?", "TBD"
            ),
            "Verdict question",
        ),
        (
            "mixed review lane",
            lambda plan: plan.replace(
                "- **Review disposition**: batch(renderers)\n- **Status**: pending",
                "- **Review-weight**: prose\n"
                "- **Review disposition**: batch(renderers)\n"
                "- **Status**: pending",
                1,
            ),
            "Review lane",
        ),
        (
            "eligibility exclusion",
            lambda plan: plan.replace("exclusions: none", "exclusions: external wait"),
            "exclusions",
        ),
        (
            "unprovable consumability",
            lambda plan: plan.replace("consumable: yes", "consumable: unknown"),
            "consumable",
        ),
    ],
)
def test_plan_contract_matrix(
    tmp_path: Path,
    case: str,
    mutate,
    expected_fragment: str,
) -> None:
    result = _run(tmp_path, mutate(_valid_plan()))
    if case == "valid":
        assert result.returncode == 0, result.stderr
        assert expected_fragment in result.stdout
    else:
        assert result.returncode == 1, result.stdout + result.stderr
        assert expected_fragment.lower() in result.stderr.lower()
