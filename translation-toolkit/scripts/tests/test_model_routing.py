"""Tests for scripts/lib/model_routing.py — per-role model routing.

Covers Phase B of translation-toolkit v0.3.0 Tier 2 plan:
  1. test_validate_string_form               — non-empty str accepted
  2. test_validate_dict_with_default_only    — minimal dict accepted
  3. test_validate_dict_missing_default_raises
  4. test_validate_dict_unknown_role_warns   — forward-compat warn, no raise
  5. test_validate_dict_empty_value_raises
  6. test_resolve_string_form_returns_same
  7. test_resolve_dict_role_present
  8. test_resolve_dict_role_absent_returns_default
  9. test_resolve_extractor_role             — cheap-model split case
"""
from __future__ import annotations

import sys
import warnings
from pathlib import Path

import pytest

# tests/ -> scripts/
SCRIPTS_DIR = Path(__file__).resolve().parent.parent
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))

from lib.model_routing import (  # noqa: E402
    KNOWN_ROLES,
    resolve_model_for_role,
    validate_model_field,
)


# -------------------- 1. validate: string form --------------------

def test_validate_string_form() -> None:
    """A non-empty string is accepted (v0.2.0 baseline form)."""
    validate_model_field("claude-opus-4-7")


def test_validate_empty_string_raises() -> None:
    """Empty string is rejected for symmetry with empty-default rejection."""
    with pytest.raises(ValueError):
        validate_model_field("")


# -------------------- 2-5. validate: dict form --------------------

def test_validate_dict_with_default_only() -> None:
    """Minimal dict form — only `default` key — is accepted."""
    validate_model_field({"default": "claude-opus-4-7"})


def test_validate_dict_missing_default_raises() -> None:
    """`default` is mandatory; dict without it must raise ValueError."""
    with pytest.raises(ValueError):
        validate_model_field({"writer": "claude-opus-4-7"})


def test_validate_dict_unknown_role_warns() -> None:
    """Unknown role keys emit a UserWarning but do not raise (forward-compat).

    The warning message must mention the unknown role name so callers can
    diagnose typos quickly.
    """
    with pytest.warns(UserWarning, match="future_role"):
        validate_model_field(
            {"default": "claude-opus-4-7", "future_role": "claude-haiku-4-5"}
        )


def test_validate_dict_empty_value_raises() -> None:
    """Empty-string values (including for `default`) are rejected."""
    with pytest.raises(ValueError):
        validate_model_field({"default": ""})


def test_validate_dict_known_roles_all_accepted() -> None:
    """Every key in KNOWN_ROLES + `default` is accepted without warning."""
    full = {"default": "opus"}
    for role in KNOWN_ROLES:
        full[role] = "haiku"
    # Guard: should not warn for any known role.
    with warnings.catch_warnings():
        warnings.simplefilter("error")  # turn warnings into errors
        validate_model_field(full)


def test_validate_non_string_non_dict_raises() -> None:
    """Other types (int, list, None) must raise ValueError."""
    for bad in (None, 123, ["claude-opus-4-7"]):
        with pytest.raises(ValueError):
            validate_model_field(bad)  # type: ignore[arg-type]


# -------------------- 6-9. resolve --------------------

def test_resolve_string_form_returns_same() -> None:
    """str form: every role resolves to the single string."""
    model = "claude-opus-4-7"
    for role in KNOWN_ROLES:
        assert resolve_model_for_role(model, role) == "claude-opus-4-7"


def test_resolve_dict_role_present() -> None:
    """dict form: a role with an explicit override returns that override."""
    model = {"default": "claude-opus-4-7", "writer": "claude-sonnet-4-5"}
    assert resolve_model_for_role(model, "writer") == "claude-sonnet-4-5"


def test_resolve_dict_role_absent_returns_default() -> None:
    """dict form: a role without an override falls back to `default`."""
    model = {"default": "claude-opus-4-7", "writer": "claude-sonnet-4-5"}
    assert resolve_model_for_role(model, "critic") == "claude-opus-4-7"


def test_resolve_extractor_role() -> None:
    """Cheap-model split: extractor override returns the cheap model."""
    model = {"default": "opus", "extractor": "haiku"}
    assert resolve_model_for_role(model, "extractor") == "haiku"
    # Other roles still see the default.
    assert resolve_model_for_role(model, "writer") == "opus"
