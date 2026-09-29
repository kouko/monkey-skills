#!/usr/bin/env python3
"""
Test for OpenCode v2 plugin compatibility documentation.
"""

import os
import re


def test_opencode_docs_exists_and_content():
    """Test that docs/opencode.md exists and contains required information."""
    docs_path = "docs/opencode.md"

    # Check if file exists
    assert os.path.exists(docs_path), f"{docs_path} does not exist"

    # Read file content
    with open(docs_path, 'r') as f:
        content = f.read()

    # Check that both tokens are mentioned
    assert "CLAUDE_SKILL_DIR" in content, "CLAUDE_SKILL_DIR not found in docs/opencode.md"
    assert "CLAUDE_PLUGIN_ROOT" in content, "CLAUDE_PLUGIN_ROOT not found in docs/opencode.md"

    # Check that all five affected plugins are mentioned
    required_plugins = [
        "investing-toolkit",
        "tsundoku",
        "think-orbit",
        "obsidian",
        "salesforce-toolkit"
    ]

    for plugin in required_plugins:
        assert plugin in content, f"Plugin {plugin} not found in docs/opencode.md"

    # Check for tested version line
    assert "Tested with opencode v2.0.18" in content, "Tested version line not found"


if __name__ == "__main__":
    test_opencode_docs_exists_and_content()
    print("All tests passed!")