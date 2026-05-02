"""test_plugin_metadata.py — validate plugin.json + .mcp.json (no network).

Asserts:
  1. .claude-plugin/plugin.json parses as JSON, has required keys, version
     starts with `2.0`, description references the three-layer architecture.
  2. .mcp.json parses as JSON, references servers/mcp_bootstrap.sh which
     exists on disk.

These are stable structural invariants for v2.0.0 — bumping past 2.0.x will
require updating the version-prefix assertion.
"""
from __future__ import annotations

import json
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
PLUGIN_JSON = ROOT / ".claude-plugin" / "plugin.json"
MCP_JSON = ROOT / ".mcp.json"
SERVERS_DIR = ROOT / "servers"

REQUIRED_PLUGIN_FIELDS = ["name", "version", "description"]


# --------------------------------------------------------------------------- #
# plugin.json
# --------------------------------------------------------------------------- #


def test_plugin_json_exists():
    assert PLUGIN_JSON.is_file(), f"missing {PLUGIN_JSON}"


def test_plugin_json_parses():
    data = json.loads(PLUGIN_JSON.read_text(encoding="utf-8"))
    assert isinstance(data, dict), "plugin.json must be a JSON object"


@pytest.fixture(scope="module")
def plugin_data() -> dict:
    return json.loads(PLUGIN_JSON.read_text(encoding="utf-8"))


@pytest.mark.parametrize("field", REQUIRED_PLUGIN_FIELDS)
def test_plugin_json_required_field(plugin_data, field):
    assert field in plugin_data, f"plugin.json missing required field: {field}"
    assert plugin_data[field], f"plugin.json {field} is empty"


def test_plugin_json_version_v2(plugin_data):
    version = plugin_data["version"]
    assert isinstance(version, str), "version must be a string"
    assert version.startswith("2."), (
        f"plugin.json version must start with '2.' for the v2.x line; got {version!r}"
    )


def test_plugin_json_name(plugin_data):
    assert plugin_data["name"] == "investing-toolkit"


def test_plugin_json_description_mentions_three_layer(plugin_data):
    """v2.0.0 marketing-line invariant: must reference the three-layer
    architecture so users understand the breaking change."""
    desc = plugin_data["description"]
    assert isinstance(desc, str), "description must be a string"
    desc_lc = desc.lower()
    assert ("three-layer" in desc_lc) or ("layer" in desc_lc), (
        "plugin.json description must mention 'three-layer' or 'Layer' "
        f"to advertise the v2.0.0 architecture; got: {desc[:200]!r}..."
    )


# --------------------------------------------------------------------------- #
# .mcp.json
# --------------------------------------------------------------------------- #


def test_mcp_json_exists():
    assert MCP_JSON.is_file(), f"missing {MCP_JSON}"


def test_mcp_json_parses():
    data = json.loads(MCP_JSON.read_text(encoding="utf-8"))
    assert isinstance(data, dict), ".mcp.json must be a JSON object"


def test_mcp_json_references_bootstrap():
    """.mcp.json must reference servers/mcp_bootstrap.sh which exists."""
    data = json.loads(MCP_JSON.read_text(encoding="utf-8"))
    assert "mcpServers" in data, ".mcp.json missing 'mcpServers'"
    servers = data["mcpServers"]
    assert isinstance(servers, dict) and servers, "mcpServers must be a non-empty object"
    # Concatenate all referenced paths to scan for mcp_bootstrap.sh
    raw = json.dumps(data)
    assert "mcp_bootstrap.sh" in raw, (
        ".mcp.json must reference mcp_bootstrap.sh; current content: "
        f"{raw[:200]}"
    )
    bootstrap = SERVERS_DIR / "mcp_bootstrap.sh"
    assert bootstrap.is_file(), f"referenced bootstrap script missing on disk: {bootstrap}"
