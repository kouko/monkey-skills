"""Regression guard: spec-toolkit is registered in the root marketplace.json.

Pure-config test (tdd-iron-law exemption) — asserts the plugins[] entry
exists, points at ./spec-toolkit/, and carries a non-empty description.
"""

import json
from pathlib import Path

MARKETPLACE = Path(__file__).parents[2] / ".claude-plugin" / "marketplace.json"


def _load_plugins():
    data = json.loads(MARKETPLACE.read_text(encoding="utf-8"))
    return data["plugins"]


def test_marketplace_is_valid_json():
    # Fails loud if the file is missing or malformed JSON.
    json.loads(MARKETPLACE.read_text(encoding="utf-8"))


def test_exactly_one_spec_toolkit_entry():
    entries = [p for p in _load_plugins() if p.get("name") == "spec-toolkit"]
    assert len(entries) == 1, f"expected exactly one spec-toolkit entry, got {len(entries)}"


def test_spec_toolkit_source():
    entry = next(p for p in _load_plugins() if p.get("name") == "spec-toolkit")
    assert entry["source"] == "./spec-toolkit/", f"unexpected source: {entry.get('source')!r}"


def test_spec_toolkit_description_non_empty():
    entry = next(p for p in _load_plugins() if p.get("name") == "spec-toolkit")
    assert entry.get("description", "").strip(), "spec-toolkit description must be non-empty"
