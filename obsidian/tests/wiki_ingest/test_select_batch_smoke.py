"""Smoke test for select-batch.py — TDD Iron Law evidence (RED → GREEN).

Invokes the script with empty stdin + required env vars,
asserts exit 0 + correct JSON shape.
"""

import json
import os
import subprocess
import sys
from pathlib import Path

SCRIPT = (
    Path(__file__).parent.parent.parent
    / "skills/wiki_ingest/scripts/select-batch.py"
)
# Actual path uses hyphens in the skill folder name
SCRIPT_ACTUAL = (
    Path(__file__).parent.parent.parent
    / "skills/wiki-ingest/scripts/select-batch.py"
)


def test_empty_stdin_returns_valid_json_shape(tmp_path):
    """Exit 0 + JSON with required keys when stdin is empty."""
    manifest_path = tmp_path / "manifest.json"
    vault_root = tmp_path / "vault"
    vault_root.mkdir()

    env = {
        **os.environ,
        "BATCH_ORDER": "oldest-first",
        "BATCH_CAP": "15",
        "MANIFEST_PATH": str(manifest_path),
        "VAULT_ROOT": str(vault_root),
    }

    result = subprocess.run(
        [sys.executable, str(SCRIPT_ACTUAL)],
        input="",
        capture_output=True,
        text=True,
        env=env,
    )

    assert result.returncode == 0, (
        f"Expected exit 0, got {result.returncode}.\n"
        f"stderr: {result.stderr}\nstdout: {result.stdout}"
    )

    data = json.loads(result.stdout)
    required_keys = {"batch", "remaining", "skipped_unchanged", "scope_summary"}
    assert required_keys <= data.keys(), (
        f"Missing keys: {required_keys - data.keys()}"
    )


def test_missing_env_returns_exit_2(tmp_path):
    """Exit 2 when required env vars are absent."""
    # Run with only PATH in env — no BATCH_ORDER/BATCH_CAP/MANIFEST_PATH/VAULT_ROOT
    env = {"PATH": os.environ.get("PATH", "")}

    result = subprocess.run(
        [sys.executable, str(SCRIPT_ACTUAL)],
        input="",
        capture_output=True,
        text=True,
        env=env,
    )

    assert result.returncode == 2, (
        f"Expected exit 2, got {result.returncode}.\n"
        f"stderr: {result.stderr}"
    )
