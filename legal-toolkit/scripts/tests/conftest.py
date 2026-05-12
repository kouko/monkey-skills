"""Shared pytest fixtures for distribute / verify-drift tests.

Each test builds an isolated synthetic plugin tree under pytest's
tmp_path so we never touch the real legal-toolkit/ skills/ tree.
"""
from __future__ import annotations

from pathlib import Path

import pytest


@pytest.fixture
def fake_plugin(tmp_path: Path) -> Path:
    """Return a tmp_path that looks like a plugin root: scripts/canonical/
    pre-created, skills/ empty.

    Tests put canonical files under <fake_plugin>/scripts/canonical/, and
    assert distribute() / verify_drift() behavior against the synthetic tree.
    """
    (tmp_path / "scripts" / "canonical").mkdir(parents=True)
    (tmp_path / "skills").mkdir()
    return tmp_path
