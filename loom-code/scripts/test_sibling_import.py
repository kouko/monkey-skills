"""Tests for the shared sibling-module loader `sibling_import.load_sibling`."""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

import sibling_import
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


def test_load_sibling_default_anchor_resolves_beside_this_helper():
    """With no `anchor` given, load_sibling must resolve the sibling file
    relative to sibling_import's own directory (its documented default),
    not the caller's directory -- pins the docstring's corrected claim."""
    try:
        module = load_sibling("heading_window.py", name="probe_default_anchor")
        assert Path(module.__file__) == Path(sibling_import.__file__).with_name(
            "heading_window.py"
        )
    finally:
        sys.modules.pop("probe_default_anchor", None)


def test_load_sibling_missing_file_raises_import_error():
    """A missing sibling file must surface as ImportError (spec is None),
    matching the existing callers' `if spec is None or spec.loader is None`
    guard so they can wrap it into their own exception type."""
    with pytest.raises(ImportError):
        load_sibling("does_not_exist_anywhere.py", name="probe_missing")
    sys.modules.pop("probe_missing", None)
