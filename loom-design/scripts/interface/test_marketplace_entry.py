"""Regression guard: loom-interface-design is registered in the root marketplace.json.

Pure-config test (tdd-iron-law exemption) — asserts the plugins[] entry
exists, points at ./loom-interface-design/, and that its name +
description match the plugin manifest (plugin.json).
"""

import json
from pathlib import Path

MARKETPLACE = Path(__file__).parents[2] / ".claude-plugin" / "marketplace.json"
MANIFEST = Path(__file__).parents[1] / ".claude-plugin" / "plugin.json"


def _load_plugins():
    data = json.loads(MARKETPLACE.read_text(encoding="utf-8"))
    return data["plugins"]


def _load_manifest():
    return json.loads(MANIFEST.read_text(encoding="utf-8"))


def test_marketplace_is_valid_json():
    # Fails loud if the file is missing or malformed JSON.
    json.loads(MARKETPLACE.read_text(encoding="utf-8"))


def test_exactly_one_interface_design_toolkit_entry():
    entries = [p for p in _load_plugins() if p.get("name") == "loom-interface-design"]
    assert len(entries) == 1, f"expected exactly one loom-interface-design entry, got {len(entries)}"


def test_interface_design_toolkit_source():
    entry = next(p for p in _load_plugins() if p.get("name") == "loom-interface-design")
    assert entry["source"] == "./loom-interface-design/", f"unexpected source: {entry.get('source')!r}"


def test_entry_matches_manifest():
    entry = next(p for p in _load_plugins() if p.get("name") == "loom-interface-design")
    manifest = _load_manifest()
    assert entry["name"] == manifest["name"], "marketplace name must match manifest name"
    assert entry["description"] == manifest["description"], "marketplace description must match manifest description"
