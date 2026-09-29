#!/usr/bin/env python3
"""Generate all OpenCode v2 plugin loaders from a single template.

Each plugin's `<plugin>/.opencode-plugin/index.js` is emitted from
`scripts/opencode-loader.template.js`, with the `{plugin}` placeholder
replaced by the actual plugin name.  All 21 loaders are byte-identical
modulo the plugin name.

Usage:
    python3 scripts/generate_opencode_loaders.py [--check]
"""

import argparse
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
TEMPLATE_FILE = Path(__file__).with_name("opencode-loader.template.js")

# All 21 plugins that ship an OpenCode v2 loader.
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


def render_template(plugin: str) -> bytes:
    """Render the template for a given plugin name (byte-exact)."""
    template = TEMPLATE_FILE.read_bytes()
    if PLACEHOLDER.encode() not in template:
        raise ValueError("Template is missing the {plugin} placeholder")
    return template.replace(PLACEHOLDER.encode(), plugin.encode())


def get_loader_path(plugin: str) -> Path:
    return REPO_ROOT / plugin / ".opencode-plugin" / "index.js"


def generate() -> list[str]:
    """Generate all loaders and return list of written paths."""
    written = []
    for plugin in PLUGINS:
        rendered = render_template(plugin)
        path = get_loader_path(plugin)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(rendered)
        written.append(str(path))
    return written


def check() -> bool:
    """Return True if all loaders are in sync with the template."""
    all_ok = True
    for plugin in PLUGINS:
        expected = render_template(plugin)
        path = get_loader_path(plugin)
        if not path.exists():
            print(f"MISSING: {path}", file=sys.stderr)
            all_ok = False
            continue
        actual = path.read_bytes()
        if actual != expected:
            print(f"OUT OF SYNC: {path}", file=sys.stderr)
            all_ok = False
    return all_ok


def main() -> int:
    parser = argparse.ArgumentParser(description="Generate OpenCode v2 plugin loaders")
    parser.add_argument("--check", action="store_true",
                        help="Only check that loaders are in sync; exit non-zero if not")
    args = parser.parse_args()

    if args.check:
        return 0 if check() else 1

    written = generate()
    print(f"Generated {len(written)} loaders:")
    for p in written:
        print(f"  {p}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
