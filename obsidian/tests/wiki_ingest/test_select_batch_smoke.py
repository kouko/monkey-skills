"""Smoke test for select-batch.py — TDD Iron Law evidence (RED → GREEN).

Invokes the script with empty stdin + required env vars,
asserts exit 0 + correct JSON shape.
"""

import json
import os
import subprocess
import sys
from pathlib import Path

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


def test_topic_filter_basename_match(tmp_path):
    """TOPIC_FILTER: only basenames containing the substring appear in batch.

    Two NEW files: one matching (investing-notes.md), one not (cooking-notes.md).
    With TOPIC_FILTER=investing, only the matching file should be in batch.
    The non-matching file should appear in remaining=[].
    skipped_unchanged is unchanged-bucket count (0 here — no manifest entries).
    """
    vault_root = tmp_path / "vault"
    vault_root.mkdir()
    manifest_path = tmp_path / "manifest.json"

    # Create two NEW files (no manifest entry → both NEW)
    matching = vault_root / "investing-notes.md"
    matching.write_text("# Investing Notes\n", encoding="utf-8")

    non_matching = vault_root / "cooking-notes.md"
    non_matching.write_text("# Cooking Notes\n", encoding="utf-8")

    env = {
        **os.environ,
        "BATCH_ORDER": "oldest-first",
        "BATCH_CAP": "15",
        "MANIFEST_PATH": str(manifest_path),
        "VAULT_ROOT": str(vault_root),
        "TOPIC_FILTER": "investing",
    }

    result = subprocess.run(
        [sys.executable, str(SCRIPT_ACTUAL)],
        input="investing-notes.md\ncooking-notes.md\n",
        capture_output=True,
        text=True,
        env=env,
    )

    assert result.returncode == 0, (
        f"Expected exit 0, got {result.returncode}.\n"
        f"stderr: {result.stderr}\nstdout: {result.stdout}"
    )

    data = json.loads(result.stdout)
    assert data["batch"] == ["investing-notes.md"], (
        f"Expected only matching file in batch, got: {data['batch']}"
    )
    assert data["remaining"] == [], (
        f"Expected empty remaining (non-matching excluded, not deferred), "
        f"got: {data['remaining']}"
    )
    assert data["skipped_unchanged"] == 0, (
        "skipped_unchanged should count unchanged-bucket files, not filtered files"
    )
