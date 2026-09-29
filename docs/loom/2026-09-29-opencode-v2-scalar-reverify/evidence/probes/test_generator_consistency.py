"""Adversarial probe: generator consistency.

Tests that all 21 loaders are byte-identical modulo the plugin name,
i.e., they all match the single template exactly.

This is an adversarial probe — it should FAIL if any loader deviates
from the template.
"""

concern: generated loaders may deviate from the single template (byte-identity check)

import sys
from pathlib import Path

REPO_ROOT = Path(__file__).parent.parent.parent.parent
TEMPLATE_FILE = REPO_ROOT / "scripts" / "opencode-loader.template.js"

# All 21 plugins
PLUGINS = [
    "ascii-graph-toolkit",
    "briefing-toolkit",
    "collab-toolkit",
    "copywriting-toolkit",
    "dbt-wiki",
    "deconstruct-toolkit",
    "domain-teams",
    "four-dx-coach",
    "gws-toolkit",
    "investing-toolkit",
    "legal-toolkit",
    "obsidian",
    "philosophers-toolkit",
    "repo-wiki",
    "research-toolkit",
    "salesforce-toolkit",
    "skill-dev-toolkit",
    "systems-thinking-toolkit",
    "think-orbit",
    "translation-toolkit",
    "tsundoku",
]

PLACEHOLDER = "{{PLUGIN}}"


def render_template(plugin: str) -> str:
    """Render the template for a given plugin name."""
    template = TEMPLATE_FILE.read_text()
    if PLACEHOLDER not in template:
        raise ValueError("Template is missing the {plugin} placeholder")
    return template.replace(PLACEHOLDER, plugin)


def get_loader_path(plugin: str) -> Path:
    return REPO_ROOT / plugin / ".opencode-plugin" / "index.js"


def test_all_loaders_match_template():
    """Test that all loaders match the template exactly."""
    mismatches = []

    for plugin in PLUGINS:
        expected = render_template(plugin)
        path = get_loader_path(plugin)

        if not path.exists():
            mismatches.append(f"{plugin}: Loader file missing at {path}")
            continue

        actual = path.read_text()
        if actual != expected:
            # Find the first difference
            for i, (e_char, a_char) in enumerate(zip(expected, actual)):
                if e_char != a_char:
                    # Show context around the difference
                    start = max(0, i - 50)
                    end = min(len(expected), i + 50)
                    mismatches.append(
                        f"{plugin}: Loader does not match template at position {i}\n"
                        f"  Expected: ...{repr(expected[start:end])}...\n"
                        f"  Actual:   ...{repr(actual[start:end])}..."
                    )
                    break
            else:
                # One string is a prefix of the other
                if len(expected) != len(actual):
                    mismatches.append(
                        f"{plugin}: Length mismatch - expected {len(expected)} chars, got {len(actual)}"
                    )

    if mismatches:
        raise AssertionError(f"Generator consistency FAILED - {len(mismatches)} mismatches:\n" + "\n".join(mismatches))

    print(f"All {len(PLUGINS)} loaders match template exactly")
    return True


def test_template_placeholder_present():
    """Test that the template contains the placeholder."""
    template = TEMPLATE_FILE.read_text()
    assert PLACEHOLDER in template, f"Template missing placeholder {PLACEHOLDER}"
    print("Template placeholder test PASSED")


def test_all_loader_files_exist():
    """Test that all 21 loader files exist."""
    missing = []
    for plugin in PLUGINS:
        path = get_loader_path(plugin)
        if not path.exists():
            missing.append(str(path))

    if missing:
        raise AssertionError(f"Missing loader files: {', '.join(missing)}")

    print(f"All {len(PLUGINS)} loader files exist")
    return True


def test_loader_id_matches_plugin():
    """Test that each loader's id field matches the plugin name."""
    for plugin in PLUGINS:
        path = get_loader_path(plugin)
        content = path.read_text()
        expected_id = f'monkey-skills-{plugin}'
        assert expected_id in content, f"{plugin}: Loader missing expected id '{expected_id}'"

    print("All loader IDs match plugin names")
    return True


def test_no_stale_placeholders():
    """Test that no loader still contains the raw placeholder."""
    for plugin in PLUGINS:
        path = get_loader_path(plugin)
        content = path.read_text()
        assert PLACEHOLDER not in content, f"{plugin}: Loader still contains unrendered placeholder"

    print("No stale placeholders in any loader")
    return True


if __name__ == "__main__":
    test_template_placeholder_present()
    test_all_loader_files_exist()
    test_loader_id_matches_plugin()
    test_no_stale_placeholders()
    test_all_loaders_match_template()
    print("\nAll generator consistency tests PASSED")