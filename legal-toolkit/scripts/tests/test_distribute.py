"""Tests for legal-toolkit/scripts/distribute.py.

distribute.py exposes ROUTE / ROOT / CANONICAL_DIR / iter_canonical_files /
distribute(); these are the surface that verify-drift.py imports.
"""
from __future__ import annotations

import sys
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(SCRIPTS))


# ---------------------------------------------------------- T-D-1: surface
def test_distribute_module_exposes_constants():
    import distribute

    assert hasattr(distribute, "ROUTE"), "distribute.ROUTE missing"
    assert hasattr(distribute, "ROOT"), "distribute.ROOT missing"
    assert hasattr(distribute, "CANONICAL_DIR"), "distribute.CANONICAL_DIR missing"
    assert isinstance(distribute.ROUTE, dict)
    assert isinstance(distribute.ROOT, Path)
    assert isinstance(distribute.CANONICAL_DIR, Path)


def test_route_table_well_formed():
    import distribute

    assert distribute.ROUTE, "ROUTE must declare at least one canonical file"
    for canonical_name, destinations in distribute.ROUTE.items():
        assert isinstance(canonical_name, str)
        assert isinstance(destinations, list)
        assert destinations, f"ROUTE['{canonical_name}'] has no destinations"
        for dst in destinations:
            assert isinstance(dst, str)
            assert dst.startswith("skills/"), (
                f"ROUTE destination must be skills-relative: {dst!r}"
            )
