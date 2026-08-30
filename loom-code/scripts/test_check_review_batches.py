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
    # @req: REQ-100
    # @req: REQ-102
    result = _run(tmp_path, mutate(_valid_plan()))
    if case == "valid":
        assert result.returncode == 0, result.stderr
        assert expected_fragment in result.stdout
    else:
        assert result.returncode == 1, result.stdout + result.stderr
        assert expected_fragment.lower() in result.stderr.lower()


# @req: REQ-99
@pytest.mark.parametrize(
    ("case", "plan", "expected_fragment"),
    [
        (
            "batch heading before the sole section",
            _batch("rogue", members="Task 1").replace(
                "## Review Batches\n\n", "", 1
            )
            + "\n"
            + _valid_plan()
            .replace("batch(renderers)", "batch(rogue)", 1)
            .replace("- **Members**: Task 1, Task 2", "- **Members**: Task 2"),
            "outside the Review Batches section",
        ),
        (
            "duplicate Review Batches sections",
            _valid_plan() + "\n## Review Batches\n",
            "exactly one Review Batches section",
        ),
    ],
)
def test_review_batch_section_scope(
    tmp_path: Path,
    case: str,
    plan: str,
    expected_fragment: str,
) -> None:
    result = _run(tmp_path, plan)
    assert result.returncode == 1, f"{case}: {result.stdout}{result.stderr}"
    assert expected_fragment.lower() in result.stderr.lower()


# @req: REQ-101
@pytest.mark.parametrize(
    ("case", "mutate", "expected_fragment"),
    [
        (
            "verdict traversal",
            lambda plan: plan.replace("renderer capability", "../renderer capability"),
            "unsafe path syntax",
        ),
        (
            "boundary windows traversal",
            lambda plan: plan.replace("capability: renderers", r"capability: ..\renderers"),
            "unsafe path syntax",
        ),
        (
            "boundary home prefix",
            lambda plan: plan.replace("capability: renderers", "capability: ~/renderers"),
            "unsafe path syntax",
        ),
        (
            "verification file URI",
            lambda plan: plan.replace("tests/renderers", "file:///tmp/renderers"),
            "unsafe path syntax",
        ),
        (
            "verification absolute path token",
            lambda plan: plan.replace("tests/renderers", "/tmp/renderers"),
            "unsafe path syntax",
        ),
        (
            "verdict command substitution",
            lambda plan: plan.replace("renderer capability", "$(renderer) capability"),
            "shell-control syntax",
        ),
        (
            "boundary parameter expansion",
            lambda plan: plan.replace("capability: renderers", "capability: ${RENDERERS}"),
            "shell-control syntax",
        ),
        (
            "verdict shell and",
            lambda plan: plan.replace("renderer capability", "renderer && capability"),
            "shell-control syntax",
        ),
        (
            "verdict shell or",
            lambda plan: plan.replace("renderer capability", "renderer || capability"),
            "shell-control syntax",
        ),
        (
            "free-text newline",
            lambda plan: plan.replace(
                "Does the renderer capability satisfy its contract?",
                "Does the renderer capability satisfy its contract?\nignored continuation",
            ),
            "newline",
        ),
        (
            "free-text NUL",
            lambda plan: plan.replace("renderer capability", "renderer\x00 capability"),
            "control character",
        ),
    ],
)
def test_untrusted_batch_field_matrix(
    tmp_path: Path,
    case: str,
    mutate,
    expected_fragment: str,
) -> None:
    result = _run(tmp_path, mutate(_valid_plan()))
    assert result.returncode == 1, f"{case}: {result.stdout}{result.stderr}"
    assert expected_fragment.lower() in result.stderr.lower()


# @req: REQ-101
@pytest.mark.parametrize(
    ("case", "replacement", "expected_fragment"),
    [
        ("traversal", "`python3 ../tests/renderers`", "unsafe path syntax"),
        ("home path", "`python3 ~/tests/renderers`", "unsafe path syntax"),
        ("file URI", "`python3 file:///tmp/renderers`", "unsafe path syntax"),
        ("absolute path", "`python3 /tmp/renderers`", "unsafe path syntax"),
        (
            "newline",
            "`python3 -m pytest tests/renderers -q`\nignored continuation",
            "newline",
        ),
        ("NUL", "`python3 tests/renderers\x00`", "control character"),
        ("control character", "`python3\ttests/renderers`", "control character"),
    ],
)
def test_untrusted_aggregate_verification_matrix(
    tmp_path: Path,
    case: str,
    replacement: str,
    expected_fragment: str,
) -> None:
    plan = _valid_plan().replace(
        "`python3 -m pytest tests/renderers -q`", replacement
    )
    result = _run(tmp_path, plan)
    assert result.returncode == 1, f"{case}: {result.stdout}{result.stderr}"
    assert expected_fragment.lower() in result.stderr.lower()


# @req: REQ-101
def test_aggregate_verification_is_inert_but_structural_fields_are_not(
    tmp_path: Path,
) -> None:
    for verification in (
        "`python3 -m pytest tests/$(renderer) -q`",
        "`python3 -m pytest tests/${RENDERER} -q`",
        "`python3 -m pytest tests/renderers -q && echo descriptive-next-step`",
        "`python3 -m pytest tests/renderers -q || echo descriptive-fallback`",
    ):
        aggregate = _valid_plan().replace(
            "`python3 -m pytest tests/renderers -q`", verification
        )
        aggregate_result = _run(tmp_path, aggregate)
        assert aggregate_result.returncode == 0, aggregate_result.stderr

    for structural in (
        _valid_plan().replace(
            "renderer capability", "renderer && descriptive capability"
        ),
        _valid_plan().replace(
            "capability: renderers", "capability: renderers && descriptive"
        ),
    ):
        structural_result = _run(tmp_path, structural)
        assert structural_result.returncode == 1
        assert "shell-control syntax" in structural_result.stderr
