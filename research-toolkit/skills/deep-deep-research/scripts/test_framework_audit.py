"""Tests for framework_audit.py — FRAMEWORK_AUDIT_SCHEMA shape + CLI.

Mirrors test_scope_vs.py style: flat imports (`from framework_audit import
...`) plus subprocess CLI round-trip tests.
"""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

SCRIPTS_DIR = Path(__file__).resolve().parent


def test_schema_subcommand_emits_gap_schema():
    from framework_audit import FRAMEWORK_AUDIT_SCHEMA

    # Top-level: {question, gaps}
    assert set(FRAMEWORK_AUDIT_SCHEMA["required"]) == {"question", "gaps"}

    gaps = FRAMEWORK_AUDIT_SCHEMA["properties"]["gaps"]
    assert gaps["type"] == "array"

    item = gaps["items"]
    # Gap items require the SCOPE_SCHEMA angle fields plus framework + cell.
    assert set(item["required"]) == {"label", "query", "framework", "cell"}
    # rationale is present but optional (mirrors SCOPE_SCHEMA angle shape).
    assert "rationale" in item["properties"]
    assert "rationale" not in item["required"]
    for prop in ("label", "query", "framework", "cell", "rationale"):
        assert item["properties"][prop]["type"] == "string"

    # CLI round-trip: `schema` prints valid JSON equal to the dict, exit 0.
    proc = subprocess.run(
        [sys.executable, str(SCRIPTS_DIR / "framework_audit.py"), "schema"],
        capture_output=True,
        text=True,
        env={"PYTHONDONTWRITEBYTECODE": "1"},
    )
    assert proc.returncode == 0
    assert json.loads(proc.stdout) == FRAMEWORK_AUDIT_SCHEMA


def test_classify_prompt_contains_question_and_routes():
    from framework_audit import classify_prompt

    q = "Is NVDA a buy at current valuation given AI capex cycle risk?"
    prompt = classify_prompt(q)

    # (a) the question text is interpolated verbatim.
    assert q in prompt

    # (b) instructs consulting the routing table to pick frameworks.
    lower = prompt.lower()
    assert "routing table" in lower or "路由表" in prompt
    assert "framework-audit-library.md" in prompt

    # (c) asks for 2–3 frameworks (covers the en-dash and hyphen forms).
    assert ("2–3" in prompt or "2-3" in prompt)
    assert "framework" in lower

    # (d) text-only — positively pins the no-web-search constraint the prompt
    # claims (a "fetch" not-in check would be vacuous: the prompt never emits it).
    assert "no web search" in lower or "no retrieval" in lower

    # CLI round-trip: classify-prompt prints the prompt, exit 0.
    proc = subprocess.run(
        [
            sys.executable,
            str(SCRIPTS_DIR / "framework_audit.py"),
            "classify-prompt",
            "--question",
            q,
        ],
        capture_output=True,
        text=True,
        env={"PYTHONDONTWRITEBYTECODE": "1"},
    )
    assert proc.returncode == 0
    assert q in proc.stdout
    assert "routing table" in proc.stdout.lower() or "路由表" in proc.stdout


def test_cli_unknown_subcommand():
    proc = subprocess.run(
        [sys.executable, str(SCRIPTS_DIR / "framework_audit.py"), "bogus"],
        capture_output=True,
        text=True,
        env={"PYTHONDONTWRITEBYTECODE": "1"},
    )
    assert proc.returncode == 1
    assert proc.stdout.strip() == ""
    assert "bogus" in proc.stderr
