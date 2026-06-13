"""Tests for mode_route.py — MODE_VERDICT_SCHEMA shape and `schema` CLI.

Mirrors test_scope_vs.py style: flat imports (`from mode_route import ...`)
plus a subprocess CLI round-trip test.
"""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

SCRIPTS_DIR = Path(__file__).resolve().parent


def test_mode_schema_binary_required_label_optional():
    from mode_route import MODE_VERDICT_SCHEMA

    props = MODE_VERDICT_SCHEMA["properties"]

    # mode_binary is the ONLY required field, enum settled/unsettled
    assert MODE_VERDICT_SCHEMA["required"] == ["mode_binary"]
    assert props["mode_binary"]["enum"] == ["settled", "unsettled"]

    # mode_label is OPTIONAL (NOT in required) — low-confidence soft signal,
    # 4-mode Cynefin enum. The clear/complicated/complex sub-distinction is
    # model-dependent noise, so it must never be a hard required switch.
    assert "mode_label" not in MODE_VERDICT_SCHEMA["required"]
    assert props["mode_label"]["enum"] == [
        "clear",
        "complicated",
        "complex",
        "chaotic",
    ]

    # rationale is an optional free-text string
    assert "rationale" not in MODE_VERDICT_SCHEMA["required"]
    assert props["rationale"]["type"] == "string"

    # CLI round-trip: `schema` prints valid JSON, exit 0
    proc = subprocess.run(
        [sys.executable, str(SCRIPTS_DIR / "mode_route.py"), "schema"],
        capture_output=True,
        text=True,
        env={"PYTHONDONTWRITEBYTECODE": "1"},
    )
    assert proc.returncode == 0
    assert json.loads(proc.stdout) == MODE_VERDICT_SCHEMA


def test_cli_unknown_subcommand():
    proc = subprocess.run(
        [sys.executable, str(SCRIPTS_DIR / "mode_route.py"), "bogus"],
        capture_output=True,
        text=True,
        env={"PYTHONDONTWRITEBYTECODE": "1"},
    )
    assert proc.returncode == 1
    assert proc.stdout.strip() == ""
    assert "bogus" in proc.stderr
