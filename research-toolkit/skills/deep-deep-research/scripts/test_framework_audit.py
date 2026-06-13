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
