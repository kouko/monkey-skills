"""Compaction guard for the using-loom-pipeline entrypoint."""

import re
from pathlib import Path


SKILL = (
    Path(__file__).resolve().parents[2]
    / "skills"
    / "using-loom-pipeline"
    / "SKILL.md"
)
TEXT = SKILL.read_text(encoding="utf-8")
BODY = TEXT.split("---", 2)[2]
LOWER = BODY.lower()


def _section(body: str, heading: str) -> str:
    start = body.index(heading)
    end = body.find("\n## ", start + len(heading))
    return body[start:] if end == -1 else body[start:end]


def test_entrypoint_preserves_availability_driver_gates_and_queue_lifecycle():
    assert "<SUBAGENT-STOP>" in BODY and "Workflow tool is available" in BODY
    assert "Codex hosts: N/A by definition" in BODY and "no fallback path" in BODY
    assert "## §Run inputs" in BODY and "## §Segments" in BODY
    assert "## §Human gates" in BODY and "## §Batch mode" in BODY


def test_availability_boundary_and_six_field_driver_contract():
    assert "do not re-derive" in BODY
    assert "loom-design" in BODY and "loom-code" in BODY
    assert "loom-design: N/A" in BODY
    assert "never fake the orchestration inline" in BODY

    inputs = _section(BODY, "## §Run inputs")
    assert len(re.findall(r"^\| \*\*[^|]+\*\* \|", inputs, re.MULTILINE)) == 6
    for field in (
        "change-id",
        "target project path",
        "token budgets",
        "model policy",
        "resumeRunId",
        "skillsRoot",
    ):
        assert f"**{field}**" in inputs
    invocation = _section(BODY, "## §Invocation")
    assert "absolute" in invocation
    assert "assets/loom-pipeline.js" in invocation
    assert "one call per segment" in invocation
    assert "never one call for the whole run" in BODY


def test_three_segments_and_exactly_four_human_gates():
    segments = _section(BODY, "## §Segments")
    assert len(re.findall(r"^\d\. \*\*Segment [123]", segments, re.MULTILINE)) == 3
    for contract in (
        "product-principles",
        "design-system",
        "interaction-flows",
        "design-critic",
        "spec-expansion",
        "completeness-critic",
        "validator",
        "subagent-driven-development",
        "requesting-code-review",
        "ui-verification",
    ):
        assert contract in segments
    gates = _section(BODY, "## §Human gates")
    gates_flat = " ".join(gates.split())
    assert len(re.findall(r"^\([a-d]\) \*\*", gates, re.MULTILINE)) == 4
    for contract in ("Change-id minting", "brief-before-asking", "Cost policy", "Final merge"):
        assert contract in gates
    assert "The pipeline never merges; it returns PR branches plus the ledger for human action." in gates_flat


def test_conductor_prohibitions_and_stable_prefix_remain_explicit():
    for prohibition in (
        "never edits station artifacts",
        "never produces verdicts",
        "never merges",
        "never parses the queue file",
        "never composes git commands",
        "never diagnoses failures mid-batch",
    ):
        assert prohibition in LOWER
    assert "stable-prefix" in LOWER and "appended, never prepended" in LOWER


def test_batch_intent_freeze_and_safe_argv_contracts():
    batch = _section(BODY, "## §Batch mode")
    for contract in (
        "QUEUE.toml",
        "queue-state.json",
        "human's **intent**",
        "machine's **state**",
        "Change-folder form",
        "Brief+plan form",
        "argument vector (argv)",
        "JSON list of strings",
        "urlsafe_b64encode",
        "argv_exec.py",
    ):
        assert contract in batch


def test_batch_lifecycle_recovery_exit_codes_and_terminal_state():
    batch = _section(BODY, "## §Batch mode")
    batch_flat = " ".join(batch.split())
    for contract in (
        '["reconcile", "--project", projectPath]',
        '["next", "--project", projectPath, "--skills-root", pluginRoot]',
        '["mark-running", id, "--run-id", workflowRunId, "--session-dir", sessionDir, "--project", projectPath]',
        '["mark", id, outcome, "--project", projectPath, "--run-id", workflowRunId]',
        "skip this `mark-running` call rather than guess", "human operator only",
        "SUSPECT-COMPLETE", "AUTO-FAILED", "dispatcher-only",
        "circuit-breaker HALT", "PR-ready",
    ):
        assert contract in batch
    for code in ("| 0 |", "| 1 |", "| 2 |", "| 3 |"):
        assert code in batch
    assert re.search(r"never mutates state\s+for either\s+of these two flags", batch)
    assert "where outcome is exactly `done` or `failed`" in batch_flat
    assert "Merge remains human under gate (d)." in batch_flat
    assert "human-only merge boundary" in batch_flat
