"""Shared fixtures for report-* format script tests.

These tests cover the 3 Layer 3 pure-formatter scripts:
  - report-stock-snapshot/scripts/snapshot_format.py
  - report-portfolio-review/scripts/review_format.py
  - report-screener-list/scripts/screener_format.py

The format scripts MUST be pure: zero network, zero subprocess, zero env access.
The discipline is verified per-file via static AST import-checks.
"""
from __future__ import annotations

import ast
import subprocess
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
SKILLS_ROOT = REPO_ROOT / "skills"
FIXTURES_DIR = Path(__file__).parent / "fixtures"

SCRIPTS = {
    "snapshot": SKILLS_ROOT / "report-stock-snapshot" / "scripts" / "snapshot_format.py",
    "review": SKILLS_ROOT / "report-portfolio-review" / "scripts" / "review_format.py",
    "screener": SKILLS_ROOT / "report-screener-list" / "scripts" / "screener_format.py",
}

# Modules that would imply non-pure I/O — script must NOT import any of these.
FORBIDDEN_IMPORTS = {
    "requests",
    "urllib",
    "urllib.request",
    "urllib.parse",
    "httpx",
    "aiohttp",
    "subprocess",
    "yfinance",
    "socket",
}


@pytest.fixture(scope="session")
def fixtures_dir() -> Path:
    return FIXTURES_DIR


@pytest.fixture(scope="session")
def scripts() -> dict[str, Path]:
    return SCRIPTS


def _collect_imports(script_path: Path) -> set[str]:
    """Return the set of top-level module names the script imports."""
    tree = ast.parse(script_path.read_text(encoding="utf-8"))
    names: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                names.add(alias.name.split(".")[0])
        elif isinstance(node, ast.ImportFrom):
            if node.module:
                names.add(node.module.split(".")[0])
    return names


@pytest.fixture(scope="session")
def collect_imports():
    return _collect_imports


@pytest.fixture(scope="session")
def forbidden_imports() -> set[str]:
    return FORBIDDEN_IMPORTS


def _run_script(script_path: Path, args: list[str], timeout: int = 30) -> subprocess.CompletedProcess:
    """Invoke a format script as a CLI subprocess.

    NOTE: subprocess is used here ONLY in the test harness (not in the script
    under test). The script-purity invariant we enforce is verified separately
    via AST inspection in the per-file test modules.
    """
    return subprocess.run(  # noqa: S603 - test harness, paths controlled
        [sys.executable, str(script_path), *args],
        capture_output=True,
        text=True,
        timeout=timeout,
    )


@pytest.fixture(scope="session")
def run_script():
    return _run_script
