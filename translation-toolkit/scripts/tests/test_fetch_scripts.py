"""Smoke tests for opt-in fetch scripts. We do NOT actually download
anything in CI — just verify --help works and arg parsing is sane."""
from __future__ import annotations

import subprocess
import sys
from pathlib import Path

SCRIPTS_DIR = Path(__file__).resolve().parent.parent


def test_fetch_microsoft_terms_help():
    result = subprocess.run(
        [sys.executable, str(SCRIPTS_DIR / "fetch-microsoft-terms.py"), "--help"],
        capture_output=True, text=True,
    )
    assert result.returncode == 0
    assert "Microsoft Terminology" in result.stdout


def test_fetch_jpo_utx_help():
    result = subprocess.run(
        [sys.executable, str(SCRIPTS_DIR / "fetch-jpo-utx.py"), "--help"],
        capture_output=True, text=True,
    )
    assert result.returncode == 0
    assert "UTX" in result.stdout
