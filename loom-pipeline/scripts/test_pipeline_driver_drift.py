"""Drift check for the COMMITTED Workflow driver asset (Task 14 of
docs/loom/plans/2026-07-03-loom-pipeline-conductor.md).

The asset at loom-pipeline/skills/using-loom-pipeline/assets/loom-pipeline.js
is a GENERATED file (see build_driver.py's banner). It must never be
hand-edited — any edit that isn't also applied to the driver_NN_*.js
sources would silently drift from what `python3 build_driver.py` produces.
This test is the drift tripwire: it rebuilds to a temp path and asserts
byte-identical output against the committed asset.
"""
from __future__ import annotations

import subprocess
import sys
from pathlib import Path

SCRIPTS_DIR = Path(__file__).resolve().parent
BUILD_DRIVER = SCRIPTS_DIR / "build_driver.py"
PIPELINE_ROOT = SCRIPTS_DIR.parent
ASSET_PATH = (
    PIPELINE_ROOT / "skills" / "using-loom-pipeline" / "assets" / "loom-pipeline.js"
)

# One distinctive token per module, in source order (00 -> 90).
MODULE_MARKERS = [
    "export const meta",
    "function guardArgs",
    "function runStation",
    "function runSegment1",
    "function runSegment2",
    "function runSegment3",
    "function recordLedger",
    "function mainDispatch",
]


def test_asset_matches_rebuild(tmp_path):
    assert ASSET_PATH.exists(), f"committed driver asset missing: {ASSET_PATH}"

    rebuilt_path = tmp_path / "loom-pipeline.js"
    result = subprocess.run(
        [sys.executable, str(BUILD_DRIVER), "--out", str(rebuilt_path)],
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, (
        f"build_driver.py failed: stdout={result.stdout!r} stderr={result.stderr!r}"
    )
    assert rebuilt_path.exists(), "build_driver.py did not write --out path"

    committed_bytes = ASSET_PATH.read_bytes()
    rebuilt_bytes = rebuilt_path.read_bytes()
    assert committed_bytes == rebuilt_bytes, (
        "committed asset has drifted from a fresh build_driver.py rebuild — "
        "the asset must be regenerated via build_driver.py, never hand-edited"
    )

    node_check = subprocess.run(
        ["node", "--check", str(ASSET_PATH)],
        capture_output=True,
        text=True,
    )
    assert node_check.returncode == 0, (
        f"node --check failed on committed asset: {node_check.stderr}"
    )

    content = committed_bytes.decode("utf-8")
    for marker in MODULE_MARKERS:
        assert marker in content, f"module marker missing from asset: {marker}"
