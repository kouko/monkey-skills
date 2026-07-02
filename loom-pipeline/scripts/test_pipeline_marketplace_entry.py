"""RED-first test: loom-pipeline must be registered in marketplace.json,
in sync with its own plugin.json description."""
import json
from pathlib import Path


def test_entry_present_and_synced():
    repo_root = Path(__file__).parents[2]
    marketplace = json.loads(
        (repo_root / ".claude-plugin" / "marketplace.json").read_text()
    )
    plugin = json.loads(
        (repo_root / "loom-pipeline" / ".claude-plugin" / "plugin.json").read_text()
    )

    entries = [p for p in marketplace["plugins"] if p["name"] == "loom-pipeline"]
    assert len(entries) == 1, "expected exactly one loom-pipeline entry in marketplace.json"

    entry = entries[0]
    assert entry["source"] == "./loom-pipeline/"
    assert entry["description"] == plugin["description"]
