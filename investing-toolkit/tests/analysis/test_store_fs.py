"""Tests for analysis-kpi/scripts/_store_fs.py — the shared durable-store fs
primitives (Rule-of-Three extract out of kpi_store.py, plan
docs/loom/plans/2026-07-14-operational-kpi-schema-lifecycle.md, Task 1).

The library is exercised by loading `_store_fs.py` via importlib (same
convention as test_kpi_store.py's `kpi_store_module` fixture).
"""
from __future__ import annotations

import importlib.util
import sys

from conftest import STORE_FS_SCRIPT


def test_store_fs_exposes_shared_primitives():
    spec = importlib.util.spec_from_file_location("store_fs_test", STORE_FS_SCRIPT)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules["store_fs_test"] = module
    spec.loader.exec_module(module)

    assert callable(module.resolve_store_dir)
    assert callable(module._atomic_write)
    assert callable(module._acquire_series_lock)
    assert callable(module._release_series_lock)
    assert hasattr(module._UNSAFE_KEY_CHARS, "sub")  # compiled regex
