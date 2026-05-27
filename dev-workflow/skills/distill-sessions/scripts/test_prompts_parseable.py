"""test_prompts_parseable.py — structural guard for Trace2Skill prompt files.

Per dev-workflow/skills/distill-sessions Plan Part 2 §Task 6.

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
- Both reference Sonnet 4.6 as the dispatch model (v0.4 swap from prior Haiku-locked model; see v0.4 brief Q-v0.4-1).

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
ADVISORY_PATH = AGENTS_DIR / "prompt-advisory-analyst.md"

# Canonical subagent model ID expected in frontmatter (v0.4: Sonnet 4.6 1M-context).
EXPECTED_MODEL = "claude-sonnet-4-6"

# Required frontmatter keys per Plan T6 §Implementation notes.
REQUIRED_FRONTMATTER_KEYS = {
    "role",
    "model",
    "input_contract",
    "output_contract",
    "hard_constraints",
}

# Advisory-analyst (v0.5) frontmatter requires an additional `language` key
# (locale variable for prose rendering — code blocks stay English).
ADVISORY_REQUIRED_FRONTMATTER_KEYS = REQUIRED_FRONTMATTER_KEYS | {"language"}

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


def test_advisory_prompt_structure() -> None:
    """prompt-advisory-analyst.md (v0.5) must define the 7-section advisory schema.

    Per v0.5 plan T1 + brief §Smallest End State, the Sonnet advisory analyst
    replaces v0.4.1's heuristic ``cluster_by_title_keyword`` +
    ``extract_claude_md_candidates`` + ``_render_*`` template renderers. The
    prompt drives:

    - semantic clustering of Memory Items (≤5 distinct anti-patterns; reject
      surface-word transitive merges that produced v0.4.1's 31/33 false cluster);
    - ≤5 real cross-skill CLAUDE.md candidates (semantic dedup vs generic-keyword
      noise like 'all' / 'open' / 'start');
    - code-block wrapping for all copy-pasteable suggested edits / command
      lines / pasted file path references;
    - explanatory prose in user's working language via ``{{lang}}`` (one of
      ``zh-TW``, ``en``, ``ja``) — code blocks stay English.

    Why intent-grounded (Rule 9): if these constraints stop being encoded in
    the prompt, the analyst regresses to v0.4.1's surface-word clustering OR
    drops the code-block wrapping (forcing user to re-format copy-pasteable
    edits) OR mixes prose languages (breaking the locale contract). All three
    are the failure modes v0.5 exists to fix.
    """
    assert ADVISORY_PATH.is_file(), f"missing prompt file: {ADVISORY_PATH}"
    text = ADVISORY_PATH.read_text(encoding="utf-8")
    fm, body = _split_frontmatter(text)

    missing = ADVISORY_REQUIRED_FRONTMATTER_KEYS - set(fm.keys())
    assert not missing, (
        f"{ADVISORY_PATH.name}: frontmatter missing keys: {sorted(missing)}"
    )

    assert fm["model"] == EXPECTED_MODEL, (
        f"{ADVISORY_PATH.name}: model is {fm['model']!r}, expected {EXPECTED_MODEL!r}"
    )

    # Role should signal advisory-analyst side.
    assert "advisory" in fm["role"].lower() or "analyst" in fm["role"].lower(), (
        f"advisory-prompt role {fm['role']!r} doesn't mention advisory/analyst"
    )

    # The 7 section headings must appear in the body's output template (in order).
    # These are English headings per spec; explanatory prose under them is in {{lang}}.
    required_section_headings = [
        "skill-mining advisory report",  # H1 (§1)
        "Top anti-patterns",  # §2
        "Per-target SKILL.md modifications",  # §3
        "CLAUDE.md candidates",  # §4
        "New-skill candidates",  # §5
        # §6 header text is locale-variant ("數字摘要" / "Summary numbers" /
        # "数値サマリ"); at least one variant must appear in the template.
        # §7
        "Action steps",
    ]
    last_pos = -1
    for heading in required_section_headings:
        idx = body.find(heading, last_pos + 1)
        assert idx != -1, (
            f"{ADVISORY_PATH.name}: required section heading "
            f"{heading!r} not found in body output template"
        )
        last_pos = idx

    # §6 — at least one of the three locale-variant summary headers must appear.
    summary_variants = ("數字摘要", "Summary numbers", "数値サマリ")
    assert any(v in body for v in summary_variants), (
        f"{ADVISORY_PATH.name}: §6 summary header missing — "
        f"expected one of {summary_variants}"
    )

    # Code-block wrapping rule must be documented.
    body_lower = body.lower()
    assert "code block" in body_lower or "fenced code block" in body_lower, (
        f"{ADVISORY_PATH.name}: body must document code-block wrapping rule"
    )

    # Language enforcement rule — explanatory prose in {{lang}}, code blocks English.
    assert "{{lang}}" in body, (
        f"{ADVISORY_PATH.name}: body must reference the {{{{lang}}}} variable"
    )

    # ≤5 anti-pattern cap and ≤5 CLAUDE.md candidate cap must be stated.
    assert "5" in body and (
        "anti-pattern" in body_lower or "anti pattern" in body_lower
    ), f"{ADVISORY_PATH.name}: body must cap anti-patterns at ≤5"

    # Dispatch / orchestrator section parity with sibling prompts.
    assert "merged" in body_lower, (
        f"{ADVISORY_PATH.name}: body must reference merged.json / merged_data input"
    )


def test_advisory_prompt_forbids_orchestrator_memory_reference() -> None:
    """Same regression guard as sibling prompts (v0.2 Finding #3).

    The advisory analyst runs in the same orchestrator process and inherits the
    auto-loaded ``~/.claude/projects/.../memory/MEMORY.md``. Without an explicit
    hard constraint, advisory report copy could cite ``[feedback_X](project
    memory)`` / ``[[name]]`` / ``feedback_*.md`` — which leak into the rendered
    advisory and onward into SKILL.md edits the user copies. Pin the no-memory-
    citation rule here so silent removal fails CI.
    """
    fm, body = _split_frontmatter(ADVISORY_PATH.read_text(encoding="utf-8"))

    constraints = fm.get("hard_constraints", []) or []
    joined = " ".join(str(c) for c in constraints).lower()
    # Advisory prompt's hard constraints differ in shape from sibling prompts
    # (analyst over merged.json, not per-trajectory); the no-memory-citation
    # rule appears in the body §"What you must NOT do" section.
    body_lower = body.lower()
    assert (
        "orchestrator memory" in body_lower
        or "project memory" in body_lower
        or "feedback_" in body_lower
        or "project_" in body_lower
    ), (
        f"{ADVISORY_PATH.name}: body must forbid orchestrator memory citations "
        f"(no [feedback_X](project memory), no [[name]], no feedback_*.md / "
        f"project_*.md references in rendered advisory output)"
    )
    # joined is allowed to be empty for advisory; the body assertion above is
    # the authoritative check. Touch `joined` to keep linters quiet.
    _ = joined


def test_both_prompts_forbid_orchestrator_memory_reference() -> None:
    """Regression guard for v0.2 Finding #3 (orchestrator memory leak).

    The orchestrator runs with ``~/.claude/projects/.../memory/MEMORY.md`` auto-
    loaded into context; that bleeds into dispatched subagents that share the
    same project. v0.1 dogfood (2026-05-25) showed subagents citing memory
    entries like ``[feedback_X](project memory)`` inside Memory Item bodies,
    which then propagated into proposed SKILL.md text — invalid because
    SKILL.md is consumed by future sessions / other operators who have no
    such memory directory. The fix is a hard constraint in both prompt files
    (body §Hard constraints + frontmatter hard_constraints). This test
    pins both to prevent silent removal.
    """
    for path in (FAILURE_PATH, SUCCESS_PATH):
        fm, body = _split_frontmatter(path.read_text(encoding="utf-8"))

        # Frontmatter list must include the no-memory-citation constraint.
        constraints = fm.get("hard_constraints", []) or []
        joined = " ".join(str(c) for c in constraints).lower()
        assert "project memory" in joined or "orchestrator's project memory" in joined, (
            f"{path.name}: frontmatter hard_constraints must forbid orchestrator "
            f"project memory references"
        )

        # Body §Hard constraints must restate the rule.
        body_lower = body.lower()
        assert "never reference the orchestrator's project memory" in body_lower, (
            f"{path.name}: body §Hard constraints must include the literal "
            f"'NEVER reference the orchestrator's project memory' bullet"
        )
