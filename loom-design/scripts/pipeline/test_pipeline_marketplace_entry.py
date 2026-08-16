"""RED-first test: loom-design must be registered in marketplace.json,
in sync with its own plugin.json description."""
import json
from pathlib import Path


def test_entry_present_and_synced():
    repo_root = Path(__file__).parents[3]
    marketplace = json.loads(
        (repo_root / ".claude-plugin" / "marketplace.json").read_text()
    )
    plugin = json.loads(
        (repo_root / "loom-design" / ".claude-plugin" / "plugin.json").read_text()
    )

    entries = [p for p in marketplace["plugins"] if p["name"] == "loom-design"]
    assert len(entries) == 1, "expected exactly one loom-design entry in marketplace.json"

    entry = entries[0]
    assert entry["source"] == "./loom-design/"
    assert entry["description"] == plugin["description"]
