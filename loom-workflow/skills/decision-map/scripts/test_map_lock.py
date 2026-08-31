"""Tests for map_lock.py's public symlink-component guard.

WHY: assert_no_symlink_components(path, error=...) is the sanctioned
public entry point other decision-map scripts reuse to reject a
symlinked path component while raising their own caller-specific
exception class instead of MapLockError.
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parent))

import map_lock  # noqa: E402


class _CallerError(Exception):
    """Stand-in for a caller-supplied exception class."""


def test_assert_no_symlink_components_raises_caller_supplied_class(
    tmp_path: Path,
) -> None:
    real_dir = tmp_path / "real"
    real_dir.mkdir()
    link = tmp_path / "link"
    link.symlink_to(real_dir)
    target = link / "child"

    with pytest.raises(_CallerError):
        map_lock.assert_no_symlink_components(target, error=_CallerError)


def test_assert_no_symlink_components_defaults_to_map_lock_error(
    tmp_path: Path,
) -> None:
    real_dir = tmp_path / "real"
    real_dir.mkdir()
    link = tmp_path / "link"
    link.symlink_to(real_dir)
    target = link / "child"

    with pytest.raises(map_lock.MapLockError):
        map_lock.assert_no_symlink_components(target)


def test_private_guard_name_is_gone() -> None:
    assert not hasattr(map_lock, "_assert_no_symlink_components")
