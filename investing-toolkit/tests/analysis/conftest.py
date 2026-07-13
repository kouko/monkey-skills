"""Shared fixtures and helpers for analysis-* skill tests.

These tests cover the 5 Layer 2 (pure-compute) analysis scripts:
  - analysis-dcf/scripts/dcf_compute.py
  - analysis-screener/scripts/screener_compute.py
  - analysis-technical/scripts/ta_compute.py
  - analysis-portfolio/scripts/portfolio_compute.py
  - analysis-macro-regime/scripts/regime_compose.py

All scripts are pure-compute (no network I/O); fixtures are synthetic JSON/CSV
under tests/analysis/fixtures/.
"""
from __future__ import annotations

import subprocess
from pathlib import Path

import pytest

# Repo root resolves from tests/analysis/conftest.py → up 2 = investing-toolkit
ROOT = Path(__file__).resolve().parents[2]
SKILLS = ROOT / "skills"
FIXTURES = Path(__file__).parent / "fixtures"

DCF_SCRIPT = SKILLS / "analysis-dcf" / "scripts" / "dcf_compute.py"
SCREENER_SCRIPT = SKILLS / "analysis-screener" / "scripts" / "screener_compute.py"
TA_SCRIPT = SKILLS / "analysis-technical" / "scripts" / "ta_compute.py"
PORTFOLIO_SCRIPT = SKILLS / "analysis-portfolio" / "scripts" / "portfolio_compute.py"
REGIME_SCRIPT = SKILLS / "analysis-macro-regime" / "scripts" / "regime_compose.py"
COMPS_SCRIPT = SKILLS / "analysis-comps" / "scripts" / "comps_compute.py"
XVAL_SCRIPT = SKILLS / "analysis-xval" / "scripts" / "xval_compute.py"
KPI_STORE_SCRIPT = SKILLS / "analysis-kpi" / "scripts" / "kpi_store.py"


def run_script(script: Path, *args: str, timeout: int = 60) -> subprocess.CompletedProcess:
    """Invoke a Layer 2 analysis script via `uv run --script`."""
    return subprocess.run(
        ["uv", "run", "--script", str(script), *args],
        capture_output=True,
        text=True,
        timeout=timeout,
        cwd=str(ROOT),
    )


@pytest.fixture
def fixtures_dir() -> Path:
    return FIXTURES


@pytest.fixture
def runner():
    return run_script
