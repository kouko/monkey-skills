"""Tests for legal-toolkit/scripts/distribute.py.

distribute.py exposes ROUTE / ROOT / CANONICAL_DIR (constants) and
iter_canonical_files (this task); distribute() + main() are added in
Tasks 3-4. verify-drift.py imports ROUTE / CANONICAL_DIR / ROOT only.
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


# ---------------------------------------------------------- T-D-2: scanner
def test_iter_canonical_files_yields_relative_names(fake_plugin):
    import distribute

    (fake_plugin / "scripts" / "canonical" / "a.json").write_text("a")
    (fake_plugin / "scripts" / "canonical" / "b.json").write_text("b")

    result = distribute.iter_canonical_files(fake_plugin / "scripts" / "canonical")

    names = sorted(rel for rel, _ in result)
    assert names == ["a.json", "b.json"]


def test_iter_canonical_files_skips_filesystem_noise(fake_plugin):
    import distribute

    canonical = fake_plugin / "scripts" / "canonical"
    (canonical / "real.json").write_text("real")
    (canonical / ".DS_Store").write_text("mac droppings")
    (canonical / ".gitkeep").write_text("")
    (canonical / "._real.json").write_text("appledouble")

    names = sorted(rel for rel, _ in distribute.iter_canonical_files(canonical))
    assert names == ["real.json"]
