"""Tests for legal-toolkit/scripts/distribute.py.

distribute.py exposes ROUTE / ROOT / CANONICAL_DIR (constants) and
iter_canonical_files (this task); distribute() + main() are added in
Tasks 3-4. verify-drift.py imports ROUTE / CANONICAL_DIR / ROOT only.
"""
from __future__ import annotations

import os
import subprocess
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


# ---------------------------------------------------------- T-D-3: distribute()
def test_distribute_creates_byte_identical_copies(fake_plugin):
    import distribute

    payload = b'{"key": "value", "n": 42}\n'
    src = fake_plugin / "scripts" / "canonical" / "legal-sources.json"
    src.write_bytes(payload)

    route = {
        "legal-sources.json": [
            "skills/legal-contract-review/assets/legal-sources.json",
        ],
    }
    distribute.distribute(route=route, root=fake_plugin)

    dst = fake_plugin / "skills" / "legal-contract-review" / "assets" / "legal-sources.json"
    assert dst.exists()
    assert dst.read_bytes() == payload


def test_distribute_creates_parent_dirs(fake_plugin):
    import distribute

    src = fake_plugin / "scripts" / "canonical" / "legal-sources.json"
    src.write_bytes(b"x")

    # skills/legal-contract-review/assets/ does NOT exist beforehand.
    assert not (fake_plugin / "skills" / "legal-contract-review").exists()

    route = {
        "legal-sources.json": [
            "skills/legal-contract-review/assets/legal-sources.json",
        ],
    }
    distribute.distribute(route=route, root=fake_plugin)

    assert (fake_plugin / "skills" / "legal-contract-review" / "assets" / "legal-sources.json").exists()


def test_distribute_is_idempotent(fake_plugin):
    import distribute

    payload = b'{"version": 1}'
    src = fake_plugin / "scripts" / "canonical" / "legal-sources.json"
    src.write_bytes(payload)

    route = {
        "legal-sources.json": [
            "skills/legal-contract-review/assets/legal-sources.json",
        ],
    }
    distribute.distribute(route=route, root=fake_plugin)
    distribute.distribute(route=route, root=fake_plugin)  # second call

    dst = fake_plugin / "skills" / "legal-contract-review" / "assets" / "legal-sources.json"
    assert dst.read_bytes() == payload


# ---------------------------------------------------------- T-D-4: CLI
def test_distribute_cli_writes_copy_and_summary(fake_plugin):
    """Invoke distribute.py as a script, with ROOT pointing at the fake plugin
    via a tiny wrapper script.
    """
    import distribute

    src = fake_plugin / "scripts" / "canonical" / "legal-sources.json"
    src.write_bytes(b'{"a": 1}')

    wrapper = fake_plugin / "run.py"
    wrapper.write_text(
        f"""
import sys
sys.path.insert(0, {str(SCRIPTS)!r})
import distribute
distribute.ROOT = __import__('pathlib').Path({str(fake_plugin)!r})
distribute.CANONICAL_DIR = distribute.ROOT / 'scripts' / 'canonical'
distribute.ROUTE = {{
    'legal-sources.json': ['skills/legal-contract-review/assets/legal-sources.json'],
}}
sys.exit(distribute.main())
"""
    )
    result = subprocess.run(
        [sys.executable, str(wrapper)],
        capture_output=True,
        text=True,
        env={**os.environ, "PYTHONDONTWRITEBYTECODE": "1"},
    )

    assert result.returncode == 0, result.stderr
    assert "[deploy]" in result.stdout
    assert "1 copies" in result.stdout or "1 file" in result.stdout
    dst = fake_plugin / "skills" / "legal-contract-review" / "assets" / "legal-sources.json"
    assert dst.read_bytes() == b'{"a": 1}'


# ---------------------------------------------------------- T-D-5: SP3b SSOT extension
def test_distribute_includes_sp3b_canonical_files():
    """ROUTE must include pdpa-current-state.md / tbd-migration-template.md
    / profile-schema.yml / load_profile.py mapped to SP3a + SP3b destinations."""
    import distribute

    for canonical_name in (
        "pdpa-current-state.md",
        "tbd-migration-template.md",
        "profile-schema.yml",
        "load_profile.py",
    ):
        assert canonical_name in distribute.ROUTE, (
            f"ROUTE missing canonical entry: {canonical_name}"
        )
        destinations = distribute.ROUTE[canonical_name]
        assert any("legal-document-draft" in d for d in destinations), (
            f"{canonical_name} missing SP3a (legal-document-draft) destination"
        )
        assert any("legal-incident-response" in d for d in destinations), (
            f"{canonical_name} missing SP3b (legal-incident-response) destination"
        )


def test_distribute_routes_profile_schema_v2_migration_to_both_skills():
    """profile-schema-v2-migration.md (canonical/) must distribute to both
    SP3a + SP3b references/ as byte-identical functional copies."""
    import distribute

    assert "profile-schema-v2-migration.md" in distribute.ROUTE
    dests = distribute.ROUTE["profile-schema-v2-migration.md"]
    assert any("legal-document-draft/references" in d for d in dests), (
        "migration doc missing SP3a destination"
    )
    assert any("legal-incident-response/references" in d for d in dests), (
        "migration doc missing SP3b destination"
    )
