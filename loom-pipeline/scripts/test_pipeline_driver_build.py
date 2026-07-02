"""Tests for loom-pipeline/scripts/build_driver.py."""
# @req: REQ-LOOM-PIPELINE-DRIVER-BUILD-1
from __future__ import annotations

import subprocess
import sys
from pathlib import Path

SCRIPTS_DIR = Path(__file__).resolve().parent
BUILD_DRIVER = SCRIPTS_DIR / "build_driver.py"
REPO_ROOT = SCRIPTS_DIR.parent.parent
AGENTS_MD = REPO_ROOT / "AGENTS.md"


def test_build_to_temp_and_lint(tmp_path):
    # @req: REQ-LOOM-PIPELINE-DRIVER-BUILD-1
    out_path = tmp_path / "loom-pipeline.js"

    result = subprocess.run(
        [sys.executable, str(BUILD_DRIVER), "--out", str(out_path)],
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0, (
        f"build_driver.py failed: stdout={result.stdout!r} stderr={result.stderr!r}"
    )
    assert out_path.exists(), "build_driver.py did not write the --out path"

    content = out_path.read_text(encoding="utf-8")

    assert content.startswith("// GENERATED FILE"), (
        "output must start with a generated-file banner comment"
    )
    assert "build_driver.py" in content.splitlines()[0], (
        "banner must name build_driver.py as the build script"
    )

    # Content from driver_00 (head module) and driver_10 (guard module) must
    # both be present, in filename order (00 before 10).
    assert "meta" in content and "loom-pipeline" in content
    assert "guardArgs" in content
    assert content.index("export const meta") < content.index("function guardArgs")

    node_check = subprocess.run(
        ["node", "--check", str(out_path)],
        capture_output=True,
        text=True,
    )
    assert node_check.returncode == 0, (
        f"node --check failed on assembled driver: {node_check.stderr}"
    )


def test_agents_md_mentions_build_driver():
    # @req: REQ-LOOM-PIPELINE-DRIVER-BUILD-1
    content = AGENTS_MD.read_text(encoding="utf-8")
    assert "build_driver.py" in content, (
        "AGENTS.md must declare the loom-pipeline build_driver.py verb"
    )
