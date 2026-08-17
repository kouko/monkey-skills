"""Regression guard: loom-design is registered in the root marketplace.json.

Pure-config test (tdd-iron-law exemption) — asserts the plugins[] entry
exists, points at ./loom-design/, and that its name +
description match the plugin manifest (plugin.json).
"""

import json
from pathlib import Path

MARKETPLACE = Path(__file__).parents[3] / ".claude-plugin" / "marketplace.json"
MANIFEST = Path(__file__).parents[2] / ".claude-plugin" / "plugin.json"


def _load_plugins():
    data = json.loads(MARKETPLACE.read_text(encoding="utf-8"))
    return data["plugins"]


def _load_manifest():
    return json.loads(MANIFEST.read_text(encoding="utf-8"))


def test_marketplace_is_valid_json():
    # Fails loud if the file is missing or malformed JSON.
    json.loads(MARKETPLACE.read_text(encoding="utf-8"))


def test_exactly_one_loom_design_entry():
    entries = [p for p in _load_plugins() if p.get("name") == "loom-design"]
    assert len(entries) == 1, f"expected exactly one loom-design entry, got {len(entries)}"


def test_loom_design_source():
    entry = next(p for p in _load_plugins() if p.get("name") == "loom-design")
    assert entry["source"] == "./loom-design/", f"unexpected source: {entry.get('source')!r}"


def test_entry_matches_manifest():
    entry = next(p for p in _load_plugins() if p.get("name") == "loom-design")
    manifest = _load_manifest()
    assert entry["name"] == manifest["name"], "marketplace name must match manifest name"
    assert entry["description"] == manifest["description"], "marketplace description must match manifest description"
