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


def test_absolute_path_normalized_to_vault_relative(tmp_path):
    """stdin candidates may be ABSOLUTE paths under VAULT_ROOT (scan-vault.sh output);
    script must strip prefix + match manifest by vault-relative key.

    Regression for v3.10.0/v3.11.0 bug: scan-vault.sh emits absolute paths,
    but manifest keys are vault-relative (per delta-tracking.md spec). Without
    normalization, every file misses manifest → skipped_unchanged stays 0
    → every run re-ingests existing wiki pages.

    Fix: select-batch.py strips VAULT_ROOT prefix from any absolute path
    before manifest lookup. Verify with a real manifest hit.
    """
    import hashlib
    import json as _json

    vault_root = tmp_path / "vault"
    vault_root.mkdir()
    manifest_path = tmp_path / "manifest.json"

    # Create one file at vault/references/foo.md
    refs = vault_root / "references"
    refs.mkdir()
    src = refs / "foo.md"
    content = "# Foo\nbody\n"
    src.write_text(content, encoding="utf-8")

    # Pre-populate manifest with vault-relative key + matching SHA-256
    sha = hashlib.sha256(content.encode("utf-8")).hexdigest()
    manifest_path.write_text(
        _json.dumps({
            "references/foo.md": {
                "sha256": sha,
                "last_ingested": "2026-05-01T00:00:00Z",
                "wiki_pages": ["entities/foo.md"],
            }
        }),
        encoding="utf-8",
    )

    env = {
        **os.environ,
        "BATCH_ORDER": "oldest-first",
        "BATCH_CAP": "15",
        "MANIFEST_PATH": str(manifest_path),
        "VAULT_ROOT": str(vault_root),
    }

    # Pipe ABSOLUTE path (scan-vault.sh output format) — NOT vault-relative
    abs_path = str(src)
    result = subprocess.run(
        [sys.executable, str(SCRIPT_ACTUAL)],
        input=f"{abs_path}\n",
        capture_output=True,
        text=True,
        env=env,
    )

    assert result.returncode == 0, (
        f"Expected exit 0, got {result.returncode}.\n"
        f"stderr: {result.stderr}\nstdout: {result.stdout}"
    )

    data = json.loads(result.stdout)
    # After normalization, abs path → vault-relative → manifest hit → UNCHANGED
    assert data["skipped_unchanged"] == 1, (
        f"Expected skipped_unchanged=1 (abs path normalized + manifest hit), "
        f"got skipped_unchanged={data['skipped_unchanged']}.\n"
        f"This indicates abs→rel normalization is NOT happening.\n"
        f"Full output: {data}"
    )
    assert data["batch"] == [], (
        f"Expected empty batch (file matched manifest), got: {data['batch']}"
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
