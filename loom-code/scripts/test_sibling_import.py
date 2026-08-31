"""Tests for the shared sibling-module loader `sibling_import.load_sibling`."""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

from sibling_import import load_sibling


def test_load_sibling_registers_under_given_name():
    """load_sibling must register the loaded module in sys.modules under the
    caller-chosen name, and the returned module must be the real thing
    (its functions callable) -- this is the contract the five duplicated
    `_load`/`_review_batch_oracle`/`_oracle` sites relied on."""
    try:
        module = load_sibling("heading_window.py", name="probe_alias")
        assert sys.modules["probe_alias"] is module
        assert callable(module.line_leading)
    finally:
        sys.modules.pop("probe_alias", None)


def test_load_sibling_missing_file_raises_import_error():
    """A missing sibling file must surface as ImportError (spec is None),
    matching the existing callers' `if spec is None or spec.loader is None`
    guard so they can wrap it into their own exception type."""
    with pytest.raises(ImportError):
        load_sibling("does_not_exist_anywhere.py", name="probe_missing")
    sys.modules.pop("probe_missing", None)
