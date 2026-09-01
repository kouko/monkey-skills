"""One pytest invocation must collect every loom-design station directory.

Before the scoped `pytest.ini` existed, the five station directories held
test modules with colliding basenames (e.g. `test_marketplace_entry.py` in
both `discovery/` and `interface/`), so a single rootdir-wide collection
failed with `import file mismatch` errors and CI had to fan out into one
pytest job per directory. This test pins the unified invocation so that
fan-out cannot silently come back.
"""
from __future__ import annotations

import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
SUITE_ROOT = Path(__file__).resolve().parent
SUITE = "loom-design/scripts/"
PYTEST_INI = SUITE_ROOT / "pytest.ini"

# Every station directory is a NON-test module basename that could shadow a
# sibling, so it is derived from disk rather than hardcoded: a sixth station
# added tomorrow is guarded on the day it lands. A station is a direct
# subdirectory that actually holds test modules (`fixtures/`, `__pycache__/`
# and the like are not stations).
STATIONS = tuple(
    sorted(
        d.name
        for d in SUITE_ROOT.iterdir()
        if d.is_dir() and not d.name.startswith((".", "__")) and any(d.glob("test_*.py"))
    )
)

# Duplicated NON-test basenames across stations, pinned rather than banned.
# `pythonpath` gives the whole suite ONE sys.path, so such a basename resolves
# for every test from the first station on that line -- both stations' tests
# import the same copy, and the other file is dead to the import system.
# `mint_critic_verdict.py` is a deliberate SSOT/functional-copy pair and is
# tolerated ONLY because interface/test_mint_critic_verdict.py::
# test_lockstep_code_matches_ssot reads BOTH files by path (docstrings
# stripped, ast compared), so a logic divergence still fails despite the
# shadowing. A NEW collision would have no such protection: it belongs here
# only once it has an equivalent guard.
SHADOWED_BASENAMES = {"mint_critic_verdict.py"}


def test_unified_collection_reports_no_errors():
    proc = subprocess.run(
        [sys.executable, "-m", "pytest", SUITE, "--collect-only", "-q"],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
    )
    output = proc.stdout + proc.stderr
    error_lines = [ln for ln in output.splitlines() if ln.startswith("ERROR ")]
    assert not error_lines, (
        "unified collection reported errors:\n" + "\n".join(error_lines)
    )
    assert "during collection" not in output, (
        f"unified collection was interrupted:\n{output[-4000:]}"
    )
    assert proc.returncode == 0, (
        f"unified collection exited {proc.returncode}:\n{output[-4000:]}"
    )
    collected = {
        ln.split("::", 1)[0].strip().split("/")[-2]
        for ln in output.splitlines()
        if "::" in ln and "/" in ln.split("::", 1)[0]
    }
    missing = [st for st in STATIONS if st not in collected]
    assert not missing, (
        "unified collection exited 0 but silently dropped station(s) "
        f"{missing} -- a norecursedirs/collect_ignore narrowing "
        f"would leave the no-ERROR assertions above green. Collected "
        f"station dirs: {sorted(collected)}"
    )


def _pythonpath_entries():
    """The `pythonpath = ...` station list from pytest.ini, in file order."""
    for line in PYTEST_INI.read_text(encoding="utf-8").splitlines():
        if line.startswith("pythonpath"):
            return line.split("=", 1)[1].split()
    raise AssertionError(f"no `pythonpath` line in {PYTEST_INI}")


def _non_test_modules():
    """station name -> set of non-test .py basenames it defines."""
    return {
        station: {
            f.name
            for f in (SUITE_ROOT / station).glob("*.py")
            if not f.name.startswith("test_")
        }
        for station in STATIONS
    }


def test_pythonpath_lists_exactly_the_station_directories():
    entries = _pythonpath_entries()
    assert sorted(entries) == sorted(STATIONS), (
        "pytest.ini's `pythonpath` and the station directories on disk have "
        f"drifted: pythonpath={entries}, stations={list(STATIONS)}. A station "
        "missing from pythonpath loses its bare sibling imports; a stale "
        "entry silently changes which copy of a duplicated basename wins."
    )


def test_duplicated_non_test_basenames_are_only_the_known_shadowed_pair():
    modules = _non_test_modules()
    seen = {}
    for station, names in modules.items():
        for name in names:
            seen.setdefault(name, []).append(station)
    duplicated = {name for name, where in seen.items() if len(where) > 1}

    assert duplicated == SHADOWED_BASENAMES, (
        "duplicated non-test module basenames across the loom-design "
        f"stations changed: {sorted(duplicated)} (pinned: "
        f"{sorted(SHADOWED_BASENAMES)}). Under the shared `pythonpath` a "
        "duplicated basename resolves from the first station on that line "
        "for EVERY test, so the other copy is imported by nobody. Give a new "
        "collision a lockstep guard and pin it here, or rename it."
    )


def test_shadowed_basename_resolves_from_the_expected_station():
    """The `pythonpath` ORDER, not just its contents, decides the winner.

    Reordering the line -- or adding a station sorting before `interface` --
    would swap which copy every test exercises with nothing else failing, so
    the resolution is pinned here explicitly.
    """
    modules = _non_test_modules()
    order = _pythonpath_entries()
    winners = {
        name: next(st for st in order if name in modules.get(st, ()))
        for name in sorted(SHADOWED_BASENAMES)
    }
    assert winners == {"mint_critic_verdict.py": "interface"}, (
        "the station that wins a shadowed import changed: "
        f"{winners}. pythonpath order is {order}."
    )
