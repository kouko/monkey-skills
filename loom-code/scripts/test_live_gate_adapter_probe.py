"""Executable contract tests for the package-local live adapter probe."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path


SCRIPT = Path(__file__).with_name("live_gate_adapter_probe.py")


def _run(*arguments: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(SCRIPT), *arguments],
        capture_output=True,
        text=True,
    )


def test_loaded_reference_probe_emits_typed_refusal_for_relative_path() -> None:
    result = _run(
        "loaded-reference",
        "--host",
        "codex",
        "--loaded-reference-path",
        "relative/codex-tools.md",
    )

    assert result.returncode == 3
    assert json.loads(result.stdout) == {
        "type": "loom.live-gate.adapter-refusal",
        "case": "invalid-reference",
        "reason": "loaded-reference-path-not-absolute",
    }
    assert result.stderr == ""

def test_post_fix_probe_emits_typed_refusal_for_unchanged_sha() -> None:
    reviewed_sha = "a" * 40
    result = _run(
        "post-fix-sha",
        "--initial-sha",
        reviewed_sha,
        "--post-fix-sha",
        reviewed_sha,
    )

    assert result.returncode == 3
    assert json.loads(result.stdout) == {
        "type": "loom.live-gate.adapter-refusal",
        "case": "unchanged-post-fix",
        "reason": "post-fix-sha-unchanged",
    }
    assert result.stderr == ""
