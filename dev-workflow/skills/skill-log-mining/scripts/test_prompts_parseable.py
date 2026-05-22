"""test_prompts_parseable.py — structural guard for Trace2Skill prompt files.

Per dev-workflow/skills/skill-log-mining Plan Part 2 §Task 6.

The two prompt files at agents/prompt-{failure,success}-analysis.md are
bundled subagent prompts the v0.1 Stage 3 orchestrator dispatches via
``code-toolkit:dispatching-parallel-agents``. The files are markdown with
YAML frontmatter (``role / model / input_contract / output_contract /
hard_constraints``) plus a 4-step body that mirrors Trace2Skill's
``analysis/error_analysis_system_llm.txt`` and
``analysis/success_analysis_system_llm.txt``.

This test is a STRUCTURAL guard, not a content review. It asserts:

- Both files exist at the expected paths.
- Each file's frontmatter parses and carries the required keys.
- Each file's body contains the 4 numbered workflow steps.
- Each file documents the Memory Item schema (``Title / Description /
  Content``).
- Failure-side enforces the ground-truth-blind hard constraint
  verbatim ("NEVER mention ground truth", Trace2Skill source line).
- Success-side enforces the dead-end-stripping discipline
  ("Lean Solution Path", Trace2Skill source phrase).
- Both reference Haiku 4.5 as the dispatch model.

Why intent-grounded (Rule 9): if the Trace2Skill constraints stop being
encoded in our prompts, the v0.1 Stage 3 subagents lose their
hindsight-bias protection (failure side) or solution-path-distillation
discipline (success side) — the prompts would become free-form review
templates, undermining the architecture's borrowed grounding.
"""

from __future__ import annotations

from pathlib import Path

import pytest

try:
    import yaml  # PyYAML
except ImportError:  # pragma: no cover — environment guard
    yaml = None


SKILL_ROOT = Path(__file__).resolve().parent.parent
AGENTS_DIR = SKILL_ROOT / "agents"
FAILURE_PATH = AGENTS_DIR / "prompt-failure-analysis.md"
SUCCESS_PATH = AGENTS_DIR / "prompt-success-analysis.md"

# Canonical Claude Haiku 4.5 model ID expected in frontmatter.
EXPECTED_MODEL = "claude-haiku-4-5-20251001"

# Required frontmatter keys per Plan T6 §Implementation notes.
REQUIRED_FRONTMATTER_KEYS = {
    "role",
    "model",
    "input_contract",
    "output_contract",
    "hard_constraints",
}

# 4-step workflow per Trace2Skill error_analysis_system_llm.txt §Required Workflow.
REQUIRED_STEP_MARKERS = [
    "1.",  # Understand the task
    "2.",  # Identify what went wrong / went right
    "3.",  # Trace to behavior
    "4.",  # Write structured Memory Items
]

# Memory Item schema fields (Trace2Skill OUTPUT FORMAT (STRICT)).
MEMORY_ITEM_FIELDS = ["Title", "Description", "Content"]


def _split_frontmatter(text: str) -> tuple[dict, str]:
    """Return (parsed_frontmatter_dict, body_text).

    Raises pytest.fail if frontmatter delimiters missing or YAML parse fails.
    """
    if yaml is None:  # pragma: no cover
        pytest.skip("PyYAML not available")
    if not text.startswith("---\n"):
        pytest.fail("file does not start with YAML frontmatter delimiter '---'")
    rest = text[len("---\n") :]
    end_idx = rest.find("\n---\n")
    if end_idx == -1:
        pytest.fail("closing frontmatter delimiter '---' not found")
    fm_text = rest[:end_idx]
    body = rest[end_idx + len("\n---\n") :]
    parsed = yaml.safe_load(fm_text)
    if not isinstance(parsed, dict):
        pytest.fail(f"frontmatter did not parse to a dict; got {type(parsed).__name__}")
    return parsed, body


def _assert_common_shape(path: Path) -> tuple[dict, str]:
    """Common structural assertions for both prompt files.

    Returns (frontmatter_dict, body_text) for side-specific assertions.
    """
    assert path.is_file(), f"missing prompt file: {path}"
    text = path.read_text(encoding="utf-8")
    fm, body = _split_frontmatter(text)

    missing = REQUIRED_FRONTMATTER_KEYS - set(fm.keys())
    assert not missing, f"{path.name}: frontmatter missing keys: {sorted(missing)}"

    assert fm["model"] == EXPECTED_MODEL, (
        f"{path.name}: model is {fm['model']!r}, expected {EXPECTED_MODEL!r}"
    )

    # 4 numbered steps must be present in body (in order, even if other
    # text intervenes).
    last_pos = -1
    for marker in REQUIRED_STEP_MARKERS:
        idx = body.find(marker, last_pos + 1)
        assert idx != -1, f"{path.name}: workflow step marker {marker!r} not found"
        last_pos = idx

    # Memory Item schema section.
    assert "Memory Item" in body, (
        f"{path.name}: 'Memory Item' schema heading missing from body"
    )
    for field_name in MEMORY_ITEM_FIELDS:
        assert field_name in body, (
            f"{path.name}: Memory Item field {field_name!r} not documented in body"
        )

    # Dispatch section.
    assert "How the orchestrator dispatches this prompt" in body, (
        f"{path.name}: dispatch section heading missing"
    )

    return fm, body


def test_failure_prompt_structure() -> None:
    """prompt-failure-analysis.md must enforce ground-truth-blind reasoning."""
    fm, body = _assert_common_shape(FAILURE_PATH)

    # Role should signal failure-analysis side.
    assert "failure" in fm["role"].lower(), (
        f"failure-prompt role {fm['role']!r} doesn't mention failure"
    )

    # Hard constraint: NEVER mention ground truth (Trace2Skill verbatim).
    body_lower = body.lower()
    assert "never mention ground truth" in body_lower or "ground truth" in body_lower, (
        "failure-prompt body must reference the ground-truth-blind constraint"
    )
    assert "never mention ground truth" in body_lower, (
        "failure-prompt must include the literal Trace2Skill hard constraint "
        "'NEVER mention ground truth'"
    )

    # Max 3 Memory Items cap.
    assert (
        "no more than 3" in body_lower
        or "max 3" in body_lower
        or "maximum of 3" in body_lower
    ), "failure-prompt must cap Memory Items at 3"


def test_success_prompt_structure() -> None:
    """prompt-success-analysis.md must enforce Lean Solution Path distillation."""
    fm, body = _assert_common_shape(SUCCESS_PATH)

    # Role should signal success-analysis side.
    assert "success" in fm["role"].lower(), (
        f"success-prompt role {fm['role']!r} doesn't mention success"
    )

    # Lean Solution Path requirement (Trace2Skill verbatim phrasing).
    assert "Lean Solution Path" in body, (
        "success-prompt must reference 'Lean Solution Path' (Trace2Skill phrasing)"
    )

    # Dead-end stripping discipline.
    body_lower = body.lower()
    assert any(
        marker in body_lower
        for marker in ("strip", "dead end", "dead-end", "failed attempt")
    ), (
        "success-prompt body must require stripping dead ends / failed attempts"
    )

    # Max 3 Memory Items cap.
    assert (
        "no more than 3" in body_lower
        or "max 3" in body_lower
        or "maximum of 3" in body_lower
    ), "success-prompt must cap Memory Items at 3"


def test_both_prompt_files_have_required_sections() -> None:
    """Top-level GREEN assertion — both files exist and pass common shape."""
    assert FAILURE_PATH.is_file(), f"missing: {FAILURE_PATH}"
    assert SUCCESS_PATH.is_file(), f"missing: {SUCCESS_PATH}"
    # Re-run common shape; if the two side-specific tests above passed,
    # this is belt-and-suspenders. Failure here means the file flipped
    # shape between tests (shouldn't happen in one run).
    _assert_common_shape(FAILURE_PATH)
    _assert_common_shape(SUCCESS_PATH)
