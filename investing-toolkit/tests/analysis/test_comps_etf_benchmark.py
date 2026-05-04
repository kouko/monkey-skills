"""Tests for runtime --sector-benchmark flag (v2.2.0-c-bench).

Uses offline fixtures for both the anchor pack and a stand-in
sector-etf-aggregate-XLK.json placed under references/. Network-free.
"""
from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
SCRIPTS = ROOT / "skills" / "analysis-comps" / "scripts"
COMPS_SCRIPT = SCRIPTS / "comps_compute.py"
FIXTURES = Path(__file__).resolve().parent / "fixtures"
REFERENCES = ROOT / "skills" / "analysis-comps" / "references"

ENV = {**os.environ, "PYTHONDONTWRITEBYTECODE": "1"}


def _run(args: list[str], timeout: int = 60) -> subprocess.CompletedProcess:
    return subprocess.run(
        ["uv", "run", str(COMPS_SCRIPT), *args],
        capture_output=True, text=True, timeout=timeout, env=ENV, cwd=str(ROOT),
    )


def test_sector_benchmark_flag_accepted(tmp_path):
    """Flag parses; no error path. Behavior tested in later tasks."""
    anchor = FIXTURES / "comps_anchor_aapl.json"
    base = FIXTURES / "comps_anchor_aapl_memo_fetch.json"
    peer = FIXTURES / "comps_peer_msft.json"
    proc = _run([
        "--mode", "compute",
        "--anchor", str(anchor), "--anchor-base", str(base), "--peers", str(peer),
        "--sector-benchmark",
    ])
    # The flag is parsed; either the run succeeds (block emitted with stub) OR
    # it returns 0/0-output without error. We only assert the flag did not
    # cause a parse error (rc != 2).
    assert proc.returncode != 2, f"--sector-benchmark not recognized: {proc.stderr}"
