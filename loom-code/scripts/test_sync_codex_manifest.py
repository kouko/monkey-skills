"""Tests for sync_codex_manifest.py — the Codex manifest sync + drift gate.

The Codex plugin manifest (`loom-code/.codex-plugin/plugin.json`) DERIVES
its shared fields from the Claude SSOT (`loom-code/.claude-plugin/plugin.json`)
but adds a Codex-only `interface` block. This script keeps the shared fields in
lock-step while preserving `interface` verbatim, and offers a `--check` drift
gate for CI.

These tests drive the pure sync/check logic against in-memory dicts and
tmp_path fixtures so they NEVER mutate the committed (currently divergent)
.codex-plugin/plugin.json — Task 2 syncs that file.

Stdlib only (json + subprocess to exercise the CLI). Resolve the script
relative to this test file.
"""

import json
import subprocess
import sys
from pathlib import Path

SCRIPT = Path(__file__).resolve().parent / "sync_codex_manifest.py"

SHARED_FIELDS = (
    "name",
    "version",
    "description",
    "author",
    "homepage",
    "repository",
    "license",
    "keywords",
)


def _source() -> dict:
    return {
        "name": "loom-code",
        "version": "0.16.0",
        "description": "new description",
        "author": {"name": "kouko", "url": "https://github.com/kouko"},
        "homepage": "https://example.com/home",
        "repository": "https://example.com/repo",
        "license": "MIT",
        "keywords": ["a", "b", "c"],
        "skills": "./skills/",
    }


def _interface() -> dict:
    return {
        "displayName": "loom-code",
        "shortDescription": "short",
        "capabilities": ["Interactive", "Read", "Write"],
        "brandColor": "#2563EB",
    }


def _stale_target() -> dict:
    return {
        "name": "loom-code",
        "version": "0.9.0",
        "description": "old description",
        "author": {"name": "kouko", "url": "https://github.com/kouko"},
        "homepage": "https://old.example.com",
        "repository": "https://example.com/repo",
        "license": "MIT",
        "keywords": ["a"],
        "skills": "./skills/",
        "interface": _interface(),
    }


# --- pure sync logic --------------------------------------------------------

def test_all_shared_fields_copied_from_source():
    import sync_codex_manifest as m

    result = m.sync_shared_fields(_source(), _stale_target())
    for field in SHARED_FIELDS:
        assert result[field] == _source()[field], f"{field} not synced from source"


def test_interface_block_preserved_verbatim():
    import sync_codex_manifest as m

    target = _stale_target()
    result = m.sync_shared_fields(_source(), target)
    assert result["interface"] == _interface()
    # structurally identical, not merged with source
    assert "interface" not in _source()


def test_skills_key_preserved_from_target():
    """Non-shared, non-interface keys on the target survive the sync."""
    import sync_codex_manifest as m

    result = m.sync_shared_fields(_source(), _stale_target())
    assert result["skills"] == "./skills/"


def test_manifests_synced_false_when_divergent():
    import sync_codex_manifest as m

    assert m.manifests_synced(_source(), _stale_target()) is False


def test_manifests_synced_true_when_synced():
    import sync_codex_manifest as m

    synced = m.sync_shared_fields(_source(), _stale_target())
    assert m.manifests_synced(_source(), synced) is True


# --- CLI: --check is a pure read, exits non-zero on divergence -------------

def _write(path: Path, data: dict) -> None:
    path.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")


def _run(argv, src: Path, dst: Path):
    return subprocess.run(
        [sys.executable, str(SCRIPT), *argv, "--source", str(src), "--target", str(dst)],
        capture_output=True,
        text=True,
    )


def test_check_exits_nonzero_when_divergent(tmp_path):
    src = tmp_path / "claude.json"
    dst = tmp_path / "codex.json"
    _write(src, _source())
    _write(dst, _stale_target())

    before = dst.read_text(encoding="utf-8")
    proc = _run(["--check"], src, dst)
    assert proc.returncode != 0, proc.stderr
    # --check must not mutate
    assert dst.read_text(encoding="utf-8") == before


def test_check_exits_zero_when_synced(tmp_path):
    import sync_codex_manifest as m

    src = tmp_path / "claude.json"
    dst = tmp_path / "codex.json"
    _write(src, _source())
    _write(dst, m.sync_shared_fields(_source(), _stale_target()))

    proc = _run(["--check"], src, dst)
    assert proc.returncode == 0, proc.stderr


def test_sync_rewrites_target_shared_fields(tmp_path):
    src = tmp_path / "claude.json"
    dst = tmp_path / "codex.json"
    _write(src, _source())
    _write(dst, _stale_target())

    proc = _run([], src, dst)
    assert proc.returncode == 0, proc.stderr

    written = json.loads(dst.read_text(encoding="utf-8"))
    for field in SHARED_FIELDS:
        assert written[field] == _source()[field]
    assert written["interface"] == _interface()
    # after sync, --check is clean
    assert _run(["--check"], src, dst).returncode == 0


def test_written_file_has_trailing_newline_and_2space_indent(tmp_path):
    src = tmp_path / "claude.json"
    dst = tmp_path / "codex.json"
    _write(src, _source())
    _write(dst, _stale_target())

    _run([], src, dst)
    text = dst.read_text(encoding="utf-8")
    assert text.endswith("\n")
    assert '\n  "name"' in text  # 2-space indent
