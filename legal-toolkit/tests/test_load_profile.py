"""Tests for legal-document-draft/scripts/load_profile.py.

load_profile.py reads legal-playbook/profile.yml + validates against the
JSON Schema at legal-document-draft/assets/profile-schema.yml. Schema
validation uses jsonschema (Draft 2020-12).
"""
from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[2]
SCRIPTS = REPO / "legal-toolkit" / "skills" / "legal-document-draft" / "scripts"
FIXTURES = REPO / "legal-toolkit" / "tests" / "fixtures-document-draft"


def _load_module(filename: str):
    spec = importlib.util.spec_from_file_location("load_profile", SCRIPTS / filename)
    assert spec and spec.loader
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


# ---------------------------------------------------------- T-P-1: minimal valid
def test_minimal_profile_loads_and_validates(tmp_path):
    load_profile = _load_module("load_profile.py")

    profile_path = FIXTURES / "profile-minimal.yml"
    result = load_profile.load_profile(profile_path)

    assert result.valid is True
    assert result.data["company_name"] == "範例股份有限公司"
    assert result.data["company_id"] == "12345678"
    assert result.data["dpo"]["email"] == "dpo@example.com"
    assert result.errors == []


# ---------------------------------------------------------- T-P-2: full profile
def test_full_profile_loads_and_validates():
    load_profile = _load_module("load_profile.py")

    profile_path = FIXTURES / "profile-full.yml"
    result = load_profile.load_profile(profile_path)

    assert result.valid is True
    assert len(result.data["cross_border_destinations"]) == 2
    assert result.data["governing_law"]["preferred_court"] == "臺灣臺北地方法院"
    assert result.errors == []


# ---------------------------------------------------------- T-P-3: missing required
def test_missing_dpo_email_fails_validation(tmp_path):
    load_profile = _load_module("load_profile.py")

    bad = tmp_path / "bad-profile.yml"
    bad.write_text(
        """
schema_version: 1
company_name: 缺 DPO 的公司
company_id: "12345678"
registered_address: 台北市
general_contact:
  email: contact@example.com
dpo:
  name: 沒填 email
""",
        encoding="utf-8",
    )

    result = load_profile.load_profile(bad)

    assert result.valid is False
    assert any("email" in err.lower() for err in result.errors), (
        f"Expected an error mentioning 'email', got: {result.errors}"
    )


# ---------------------------------------------------------- T-P-4: schema version mismatch
def test_schema_version_mismatch_fails(tmp_path):
    load_profile = _load_module("load_profile.py")

    bad = tmp_path / "version-mismatch.yml"
    bad.write_text(
        """
schema_version: 99
company_name: 版本錯誤
company_id: "12345678"
registered_address: 台北市
general_contact:
  email: contact@example.com
dpo:
  name: x
  email: x@example.com
""",
        encoding="utf-8",
    )

    result = load_profile.load_profile(bad)

    assert result.valid is False
    assert any("schema_version" in err for err in result.errors), (
        f"Expected schema_version error, got: {result.errors}"
    )
