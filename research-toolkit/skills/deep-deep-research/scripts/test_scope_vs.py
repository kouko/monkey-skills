"""Tests for scope_vs.py — SCOPE_VS_SCHEMA shape, constants, and CLI.

Mirrors test_schemas.py style: flat imports (`from scope_vs import ...`)
plus a subprocess CLI round-trip test.
"""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

SCRIPTS_DIR = Path(__file__).resolve().parent


def test_schema_shape():
    from scope_vs import (
        CANDIDATE_COUNT,
        HEAD_K,
        RELEVANCE_FLOOR,
        SCOPE_VS_SCHEMA,
        SELF_CONSISTENCY_RUNS,
        TAIL_K,
    )

    candidates = SCOPE_VS_SCHEMA["properties"]["candidates"]
    assert candidates["minItems"] == 10

    item = candidates["items"]
    assert set(item["required"]) == {"label", "query", "relevance", "typicality_tier"}
    assert item["properties"]["relevance"]["enum"] == ["high", "medium", "low"]
    assert item["properties"]["typicality_tier"]["enum"] == [
        "most-obvious",
        "mid",
        "least-obvious",
    ]
    assert set(SCOPE_VS_SCHEMA["required"]) == {"question", "summary", "candidates"}

    # Constants
    assert HEAD_K == 3
    assert TAIL_K == 2
    assert CANDIDATE_COUNT == 12
    assert SELF_CONSISTENCY_RUNS == 2
    assert RELEVANCE_FLOOR == "medium"

    # CLI round-trip
    proc = subprocess.run(
        [sys.executable, str(SCRIPTS_DIR / "scope_vs.py"), "schema"],
        capture_output=True,
        text=True,
        env={"PYTHONDONTWRITEBYTECODE": "1"},
    )
    assert proc.returncode == 0
    assert json.loads(proc.stdout) == SCOPE_VS_SCHEMA


def test_prompt_instructions():
    from scope_vs import scope_vs_prompt

    prompt = scope_vs_prompt("X")

    # candidate count interpolated
    assert "12" in prompt
    # all three typicality tier names
    assert "most-obvious" in prompt
    assert "mid" in prompt
    assert "least-obvious" in prompt
    # relative-ranking instruction (rank first, then bucket)
    lower = prompt.lower()
    assert "rank" in lower
    assert "then" in lower
    # blind/decoupled scoring cue
    assert "blind" in lower or "decoupl" in lower
    # interpolated question
    assert "X" in prompt

    # CLI round-trip
    proc = subprocess.run(
        [sys.executable, str(SCRIPTS_DIR / "scope_vs.py"), "prompt", "--question", "X"],
        capture_output=True,
        text=True,
        env={"PYTHONDONTWRITEBYTECODE": "1"},
    )
    assert proc.returncode == 0
    assert "X" in proc.stdout


def test_cli_unknown_subcommand():
    proc = subprocess.run(
        [sys.executable, str(SCRIPTS_DIR / "scope_vs.py"), "bogus"],
        capture_output=True,
        text=True,
        env={"PYTHONDONTWRITEBYTECODE": "1"},
    )
    assert proc.returncode == 1
    assert proc.stdout.strip() == ""
    assert "bogus" in proc.stderr
