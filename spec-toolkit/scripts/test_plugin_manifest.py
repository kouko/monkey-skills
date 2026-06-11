"""Regression guard for the spec-toolkit plugin manifest.

plugin.json is pure config (a tdd-iron-law exemption), so these are
cheap presence/validity assertions, not iron-law-mandated logic tests.
Path is resolved relative to this file so the test runs from any cwd.
"""

import json
import re
from pathlib import Path

MANIFEST = Path(__file__).parent.parent / ".claude-plugin" / "plugin.json"
SEMVER = re.compile(r"^\d+\.\d+\.\d+$")


def _load():
    assert MANIFEST.exists(), f"plugin.json missing at {MANIFEST}"
    return json.loads(MANIFEST.read_text(encoding="utf-8"))


def test_manifest_is_valid_json():
    # Why: a malformed manifest silently breaks plugin discovery.
    _load()


def test_name_is_spec_toolkit():
    # Why: name must match the plugin dir + marketplace source for resolution.
    assert _load()["name"] == "spec-toolkit"


def test_version_is_semver():
    # Why: marketplace + version pinning rely on a parseable semver.
    assert SEMVER.match(_load()["version"]), "version must be MAJOR.MINOR.PATCH"


def test_description_is_non_empty():
    # Why: an empty description gives the host nothing to surface to users.
    assert _load()["description"].strip()


def test_license_is_mit():
    # Why: repo convention is MIT across plugins (see research-toolkit).
    assert _load()["license"] == "MIT"
