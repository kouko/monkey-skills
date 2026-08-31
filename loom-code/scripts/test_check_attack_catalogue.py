"""Tests for check_attack_catalogue.py — the parser and checker for the
repo store `docs/loom/ATTACK-CATALOGUE.md` (plan
`docs/loom/plans/2026-08-31-adversarial-audit-station.md` Task 2).

Exercised as a CLI subprocess (the actual interface: `<store> --repo
<root>`, exit 0 / non-zero) for the refusal/pass behavior, plus direct
imports of `parse_store` and `guarded_path_globs` for the round-trip
contract those two functions owe Task 4 and Task 10.

Stdlib only.
"""

from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

from check_attack_catalogue import parse_store, guarded_path_globs

SCRIPT = Path(__file__).parent / "check_attack_catalogue.py"

_ENV = dict(os.environ, PYTHONDONTWRITEBYTECODE="1")


def _run(store: Path, repo: Path) -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, str(SCRIPT), str(store), "--repo", str(repo)],
        capture_output=True,
        text=True,
        env=_ENV,
    )


_VALID_STORE = """\
## Guarded paths
- loom-code/scripts/**
- loom-code/hooks/**

## Instances
- F1 gate-bypass | check_open_questions.py | reproduced 2026-08-31 — pinned by test_checker_refuses_reproduced_entry_without_pinned_test
- F2 held-example | check_scenario_coverage.py | held 2026-08-30
- F3 not-applicable-example | some-target | not-applicable — no such surface exists

## Prose temptations
- "trust the docstring" shortcut
"""


def _write_pinning_test(repo: Path, name: str) -> None:
    tests_dir = repo / "tests_fixture"
    tests_dir.mkdir(parents=True, exist_ok=True)
    (tests_dir / "test_x.py").write_text(
        f"def {name}():\n    pass\n",
        encoding="utf-8",
    )


def test_checker_refuses_reproduced_entry_without_pinned_test(tmp_path):
    store = tmp_path / "ATTACK-CATALOGUE.md"
    store.write_text(
        "## Guarded paths\n"
        "- loom-code/scripts/**\n\n"
        "## Instances\n"
        "- F1 gate-bypass | check_open_questions.py | reproduced 2026-08-31\n\n"
        "## Prose temptations\n"
        "- none\n",
        encoding="utf-8",
    )
    repo = tmp_path / "repo"
    repo.mkdir()
    result = _run(store, repo)
    assert result.returncode != 0
    assert "unpinned" in result.stderr
    # names the offending line's content
    assert "reproduced 2026-08-31" in result.stderr


def test_checker_passes_when_reproduced_entry_names_real_test(tmp_path):
    repo = tmp_path / "repo"
    repo.mkdir()
    _write_pinning_test(
        repo, "test_checker_refuses_reproduced_entry_without_pinned_test"
    )
    store = tmp_path / "ATTACK-CATALOGUE.md"
    store.write_text(_VALID_STORE, encoding="utf-8")
    result = _run(store, repo)
    assert result.returncode == 0, result.stderr
    assert result.stderr == ""
    assert "3" in result.stdout  # summary line mentions instance count


def test_checker_refuses_dangling_test_name(tmp_path):
    repo = tmp_path / "repo"
    repo.mkdir()
    store = tmp_path / "ATTACK-CATALOGUE.md"
    store.write_text(
        "## Guarded paths\n"
        "- loom-code/scripts/**\n\n"
        "## Instances\n"
        "- F1 x | y | reproduced 2026-08-31 — pinned by test_does_not_exist_anywhere\n\n"
        "## Prose temptations\n"
        "- none\n",
        encoding="utf-8",
    )
    result = _run(store, repo)
    assert result.returncode != 0
    assert "dangling" in result.stderr
    assert "test_does_not_exist_anywhere" in result.stderr


def test_checker_accepts_test_name_inside_sh_under_tests_dir(tmp_path):
    repo = tmp_path / "repo"
    tests_dir = repo / "tests"
    tests_dir.mkdir(parents=True)
    (tests_dir / "run.sh").write_text(
        "#!/bin/sh\nrun_case test_shell_pinned_case\n", encoding="utf-8"
    )
    store = tmp_path / "ATTACK-CATALOGUE.md"
    store.write_text(
        "## Guarded paths\n"
        "- loom-code/scripts/**\n\n"
        "## Instances\n"
        "- F1 x | y | reproduced 2026-08-31 — pinned by test_shell_pinned_case\n\n"
        "## Prose temptations\n"
        "- none\n",
        encoding="utf-8",
    )
    result = _run(store, repo)
    assert result.returncode == 0, result.stderr


def test_checker_refuses_undated_held_entry(tmp_path):
    repo = tmp_path / "repo"
    repo.mkdir()
    store = tmp_path / "ATTACK-CATALOGUE.md"
    store.write_text(
        "## Guarded paths\n"
        "- loom-code/scripts/**\n\n"
        "## Instances\n"
        "- F1 x | y | held\n\n"
        "## Prose temptations\n"
        "- none\n",
        encoding="utf-8",
    )
    result = _run(store, repo)
    assert result.returncode != 0
    assert "undated" in result.stderr
    assert "held" in result.stderr


def test_checker_refuses_empty_guarded_paths(tmp_path):
    repo = tmp_path / "repo"
    repo.mkdir()
    store = tmp_path / "ATTACK-CATALOGUE.md"
    store.write_text(
        "## Guarded paths\n\n"
        "## Instances\n"
        "- F1 x | y | not-applicable — reason\n\n"
        "## Prose temptations\n"
        "- none\n",
        encoding="utf-8",
    )
    result = _run(store, repo)
    assert result.returncode != 0
    assert "unguarded" in result.stderr


def test_checker_refuses_missing_section(tmp_path):
    repo = tmp_path / "repo"
    repo.mkdir()
    store = tmp_path / "ATTACK-CATALOGUE.md"
    store.write_text(
        "## Guarded paths\n"
        "- loom-code/scripts/**\n\n"
        "## Instances\n"
        "- F1 x | y | not-applicable — reason\n",
        encoding="utf-8",
    )
    result = _run(store, repo)
    assert result.returncode != 0
    assert "incomplete" in result.stderr


def test_parse_store_round_trips_fixture_and_guarded_path_globs_order():
    store = parse_store(_VALID_STORE)
    assert guarded_path_globs(store) == [
        "loom-code/scripts/**",
        "loom-code/hooks/**",
    ]
    assert len(store.instances) == 3
    assert store.instances[0].verdict == "reproduced"
    assert store.instances[0].date == "2026-08-31"
    assert store.instances[0].pinned_by == (
        "test_checker_refuses_reproduced_entry_without_pinned_test"
    )
    assert store.instances[1].verdict == "held"
    assert store.instances[1].date == "2026-08-30"
    assert store.instances[2].verdict == "not-applicable"
    assert store.instances[2].reason == "no such surface exists"
    assert store.prose_temptations == ['"trust the docstring" shortcut']
