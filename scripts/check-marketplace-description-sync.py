#!/usr/bin/env python3
"""Verify .claude-plugin/marketplace.json descriptions match each plugin.json description.

Why: Claude Desktop reads ONLY from marketplace.json when listing plugins —
it does NOT follow the `source` path to fetch each plugin's plugin.json.
Claude Code CLI follows source and reads plugin.json. Therefore the
description must be present in BOTH places, identical.

Same-PR drift rule: when you change a description in plugin.json, mirror
the change to marketplace.json in the same commit. This script enforces it.

Exit codes:
  0  all in sync
  1  drift or missing description
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
MARKETPLACE = ROOT / ".claude-plugin" / "marketplace.json"


def main() -> int:
    if not MARKETPLACE.exists():
        print(f"FAIL: {MARKETPLACE} not found", file=sys.stderr)
        return 1
    market = json.loads(MARKETPLACE.read_text(encoding="utf-8"))

    errors: list[str] = []
    checked = 0
    for entry in market.get("plugins", []):
        name = entry.get("name", "<unnamed>")
        marketplace_desc = entry.get("description")
        if not marketplace_desc:
            errors.append(f"{name}: marketplace.json entry missing 'description'")
            continue

        source = entry.get("source", "").lstrip("./").rstrip("/")
        plugin_json = ROOT / source / ".claude-plugin" / "plugin.json"
        if not plugin_json.exists():
            errors.append(f"{name}: plugin.json not found at {plugin_json.relative_to(ROOT)}")
            continue

        plugin_desc = json.loads(plugin_json.read_text(encoding="utf-8")).get("description", "")
        if marketplace_desc != plugin_desc:
            errors.append(
                f"{name}: description drift between marketplace.json and "
                f"{plugin_json.relative_to(ROOT)}\n"
                f"  marketplace.json: {marketplace_desc[:90]}{'...' if len(marketplace_desc) > 90 else ''}\n"
                f"  plugin.json:      {plugin_desc[:90]}{'...' if len(plugin_desc) > 90 else ''}"
            )
        checked += 1

    if errors:
        print(f"FAIL: {len(errors)} description issue(s):", file=sys.stderr)
        for err in errors:
            print(f"  {err}", file=sys.stderr)
        print(
            "\nFix: edit .claude-plugin/marketplace.json so each plugin entry's\n"
            "    `description` matches the corresponding plugin.json `description`.",
            file=sys.stderr,
        )
        return 1

    print(f"OK: {checked} plugin description(s) in sync between marketplace.json and plugin.json")
    return 0


if __name__ == "__main__":
    sys.exit(main())
