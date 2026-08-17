"""Regression guard: loom-design is registered in the root marketplace.json.

Pure-config test (tdd-iron-law exemption) — asserts the plugins[] entry
exists, points at ./loom-design/, and carries a non-empty description.
"""

import json
from pathlib import Path

MARKETPLACE = Path(__file__).parents[3] / ".claude-plugin" / "marketplace.json"


def _load_plugins():
    data = json.loads(MARKETPLACE.read_text(encoding="utf-8"))
    return data["plugins"]


def test_marketplace_is_valid_json():
    # Fails loud if the file is missing or malformed JSON.
    json.loads(MARKETPLACE.read_text(encoding="utf-8"))


def test_exactly_one_loom_design_entry():
    entries = [p for p in _load_plugins() if p.get("name") == "loom-design"]
    assert len(entries) == 1, f"expected exactly one loom-design entry, got {len(entries)}"


def test_loom_design_source():
    entry = next(p for p in _load_plugins() if p.get("name") == "loom-design")
    assert entry["source"] == "./loom-design/", f"unexpected source: {entry.get('source')!r}"


def test_loom_design_description_non_empty():
    entry = next(p for p in _load_plugins() if p.get("name") == "loom-design")
    assert entry.get("description", "").strip(), "loom-design description must be non-empty"
