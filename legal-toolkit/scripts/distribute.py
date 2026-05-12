#!/usr/bin/env python3
"""Distribute scripts/canonical/* to each routed skill assets/ as byte-identical
functional copies.

SSOT-and-functional-copy pattern (mirror of translation-toolkit/scripts/):
  scripts/canonical/<file>          -> single source of truth (only editable
                                       location)
  skills/<skill>/<subfolder>/<file> -> byte-identical functional copy
                                       (Edit forbidden; CI verifies)

Workflow:
  1. Edit a file under scripts/canonical/.
  2. Run `python3 legal-toolkit/scripts/distribute.py` from the repo root.
  3. Commit canonical edit + functional-copy updates in the same commit.

CI runs verify-drift.py to enforce byte-identical copies.
"""
from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CANONICAL_DIR = ROOT / "scripts" / "canonical"

# Routing table — reflects CURRENT state. Update in the same commit that
# creates the new consuming skill. No auto-skip.
ROUTE: dict[str, list[str]] = {
    "legal-sources.json": [
        "skills/legal-contract-review/assets/legal-sources.json",
    ],
}
