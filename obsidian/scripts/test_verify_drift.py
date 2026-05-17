#!/usr/bin/env python3
"""Tests for verify-drift.py — TDD iron-law RED before GREEN."""
from __future__ import annotations

import importlib.util
import sys
import types
from pathlib import Path

# Load verify_drift module without executing __main__
SCRIPTS_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPTS_DIR))


def _load_module(name: str) -> types.ModuleType:
    spec = importlib.util.spec_from_file_location(name, SCRIPTS_DIR / f"{name}.py")
    assert spec and spec.loader
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)  # type: ignore[union-attr]
    return mod


# ── Tests ─────────────────────────────────────────────────────────────────────


def test_help_exits_zero(tmp_path: Path) -> None:
    """--help should be parseable and not raise (argparse calls sys.exit(0))."""
    import subprocess, sys  # noqa: E401

    result = subprocess.run(
        [sys.executable, str(SCRIPTS_DIR / "verify-drift.py"), "--help"],
        capture_output=True,
    )
    assert result.returncode == 0, f"--help exited {result.returncode}"


def test_all_in_sync_exits_zero() -> None:
    """On the post-T1 worktree all copies are in sync; main() must return 0."""
    vd = _load_module("verify-drift")
    rc = vd.main([])
    assert rc == 0, f"Expected 0, got {rc}"


def test_drift_exits_nonzero(tmp_path: Path, monkeypatch) -> None:  # type: ignore[no-untyped-def]
    """When a copy is corrupted, main() must return non-zero."""
    import distribute  # type: ignore[import]

    # Pick first target and write drifted content
    first_target = distribute.TARGETS[0]
    copy_path = distribute.OBSIDIAN_ROOT / first_target
    original = copy_path.read_bytes()
    try:
        copy_path.write_bytes(original + b"\ndrift\n")
        vd = _load_module("verify-drift")
        rc = vd.main([])
        assert rc != 0, "Expected non-zero on drift"
    finally:
        copy_path.write_bytes(original)


def test_drift_output_names_path(capsys, monkeypatch) -> None:  # type: ignore[no-untyped-def]
    """Drift output must include the path of the drifted file."""
    import distribute  # type: ignore[import]

    first_target = distribute.TARGETS[0]
    copy_path = distribute.OBSIDIAN_ROOT / first_target
    original = copy_path.read_bytes()
    try:
        copy_path.write_bytes(original + b"\ndrift\n")
        vd = _load_module("verify-drift")
        vd.main([])
        captured = capsys.readouterr()
        output = captured.out + captured.err
        # Output should mention the target path
        assert first_target in output, f"Path {first_target!r} not in output: {output!r}"
    finally:
        copy_path.write_bytes(original)


if __name__ == "__main__":
    import pytest

    sys.exit(pytest.main([__file__, "-v"]))
