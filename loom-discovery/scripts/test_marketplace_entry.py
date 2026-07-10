"""Regression guard: loom-discovery is registered in the root marketplace.json.

Pure-config test (tdd-iron-law exemption) — asserts the plugins[] entry
exists, points at ./loom-discovery/, and carries a non-empty description.
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


def test_exactly_one_loom_discovery_entry():
    entries = [p for p in _load_plugins() if p.get("name") == "loom-discovery"]
    assert len(entries) == 1, f"expected exactly one loom-discovery entry, got {len(entries)}"


def test_loom_discovery_source():
    entry = next(p for p in _load_plugins() if p.get("name") == "loom-discovery")
    assert entry["source"] == "./loom-discovery/", f"unexpected source: {entry.get('source')!r}"


def test_loom_discovery_description_non_empty():
    entry = next(p for p in _load_plugins() if p.get("name") == "loom-discovery")
    assert entry.get("description", "").strip(), "loom-discovery description must be non-empty"
