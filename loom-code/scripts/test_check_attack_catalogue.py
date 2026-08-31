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

import pytest

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


def test_checker_refuses_test_name_that_exists_only_inside_a_docstring(tmp_path):
    repo = tmp_path / "repo"
    tests_dir = repo / "tests_fixture"
    tests_dir.mkdir(parents=True)
    (tests_dir / "test_x.py").write_text(
        '"""Example usage:\n\ndef test_fake():\n    pass\n"""\n'
        "def test_real():\n    pass\n",
        encoding="utf-8",
    )
    store = tmp_path / "ATTACK-CATALOGUE.md"
    store.write_text(
        "## Guarded paths\n"
        "- loom-code/scripts/**\n\n"
        "## Instances\n"
        "- F1 x | y | reproduced 2026-08-31 — pinned by test_fake\n\n"
        "## Prose temptations\n"
        "- none\n",
        encoding="utf-8",
    )
    result = _run(store, repo)
    assert result.returncode != 0
    assert "dangling" in result.stderr
    assert "test_fake" in result.stderr


def test_checker_refuses_reproduced_with_empty_pinned_by(tmp_path):
    repo = tmp_path / "repo"
    repo.mkdir()
    store = tmp_path / "ATTACK-CATALOGUE.md"
    store.write_text(
        "## Guarded paths\n"
        "- loom-code/scripts/**\n\n"
        "## Instances\n"
        "- F1 x | y | reproduced 2026-08-31 — pinned by\n\n"
        "## Prose temptations\n"
        "- none\n",
        encoding="utf-8",
    )
    result = _run(store, repo)
    assert result.returncode != 0
    assert "malformed" in result.stderr
    assert "reproduced 2026-08-31" in result.stderr


def test_checker_refuses_unknown_status_token(tmp_path):
    repo = tmp_path / "repo"
    repo.mkdir()
    store = tmp_path / "ATTACK-CATALOGUE.md"
    store.write_text(
        "## Guarded paths\n"
        "- loom-code/scripts/**\n\n"
        "## Instances\n"
        "- F1 x | y | some-other-status\n\n"
        "## Prose temptations\n"
        "- none\n",
        encoding="utf-8",
    )
    result = _run(store, repo)
    assert result.returncode != 0
    assert "malformed" in result.stderr
    assert "some-other-status" in result.stderr


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


def test_checker_refuses_test_name_that_appears_only_in_a_sh_comment(tmp_path):
    repo = tmp_path / "repo"
    tests_dir = repo / "tests"
    tests_dir.mkdir(parents=True)
    (tests_dir / "run.sh").write_text(
        "#!/bin/sh\n"
        "# run_case test_commented_only_case is not really invoked\n"
        "run_case test_shell_pinned_case  # test_commented_only_case\n",
        encoding="utf-8",
    )
    store = tmp_path / "ATTACK-CATALOGUE.md"
    store.write_text(
        "## Guarded paths\n"
        "- loom-code/scripts/**\n\n"
        "## Instances\n"
        "- F1 x | y | reproduced 2026-08-31 — pinned by test_commented_only_case\n\n"
        "## Prose temptations\n"
        "- none\n",
        encoding="utf-8",
    )
    result = _run(store, repo)
    assert result.returncode != 0
    assert "dangling" in result.stderr
    assert "test_commented_only_case" in result.stderr


def test_checker_treats_names_in_an_unparsable_test_file_as_dangling(tmp_path):
    repo = tmp_path / "repo"
    tests_dir = repo / "tests_fixture"
    tests_dir.mkdir(parents=True)
    (tests_dir / "test_x.py").write_text(
        "def test_broken_syntax(:\n"  # SyntaxError: unparsable
        "    pass\n",
        encoding="utf-8",
    )
    store = tmp_path / "ATTACK-CATALOGUE.md"
    store.write_text(
        "## Guarded paths\n"
        "- loom-code/scripts/**\n\n"
        "## Instances\n"
        "- F1 x | y | reproduced 2026-08-31 — pinned by test_broken_syntax\n\n"
        "## Prose temptations\n"
        "- none\n",
        encoding="utf-8",
    )
    result = _run(store, repo)
    assert result.returncode != 0
    assert "dangling" in result.stderr
    assert "test_broken_syntax" in result.stderr


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


def _assert_fails_loud(result: subprocess.CompletedProcess, offending: str) -> None:
    combined = result.stdout + result.stderr
    assert result.returncode != 0, combined
    assert "Traceback" not in result.stderr, result.stderr
    assert offending in combined, combined


def test_checker_fails_loud_on_unreadable_store_path(tmp_path):
    repo = tmp_path / "repo"
    repo.mkdir()

    # a directory where a store file is expected
    store_dir = tmp_path / "store-is-a-dir"
    store_dir.mkdir()
    _assert_fails_loud(_run(store_dir, repo), str(store_dir))

    # a store path that does not exist at all
    missing_store = tmp_path / "does-not-exist.md"
    _assert_fails_loud(_run(missing_store, repo), str(missing_store))


# No behavioral case exercises an unreadable --repo directory: on this
# repo's Python (3.12), pathlib's rglob() silently swallows OSError while
# scanning (glob's traditional behavior, carried into pathlib) — chmod
# 0o000 on a directory produces zero matches, not an exception, so no
# subprocess-level case can observe the guard firing. The CLI boundary in
# main() still wraps the check_store() call in try/except OSError as a
# defensive guard against any OSError a future change to the scan logic
# might introduce (e.g. a stat() call added to the walk).


def test_checker_refuses_duplicate_section_heading(tmp_path):
    repo = tmp_path / "repo"
    repo.mkdir()

    # Instances-shadow: a later '## Instances' would silently replace the
    # earlier one, dropping whatever bullets it held.
    store_instances = tmp_path / "instances-shadow.md"
    store_instances.write_text(
        "## Guarded paths\n"
        "- loom-code/scripts/**\n\n"
        "## Instances\n"
        "- F1 x | y | not-applicable — reason\n\n"
        "## Instances\n"
        "- F2 x | y | not-applicable — reason\n\n"
        "## Prose temptations\n"
        "- none\n",
        encoding="utf-8",
    )
    result = _run(store_instances, repo)
    assert result.returncode != 0, result.stderr
    assert "malformed" in result.stderr
    assert "Instances" in result.stderr

    # Guarded-paths-shadow: a later '## Guarded paths' would silently
    # replace the earlier globs.
    store_guarded = tmp_path / "guarded-shadow.md"
    store_guarded.write_text(
        "## Guarded paths\n"
        "- loom-code/scripts/**\n\n"
        "## Guarded paths\n"
        "- nothing/that/exists/**\n\n"
        "## Instances\n"
        "- F1 x | y | not-applicable — reason\n\n"
        "## Prose temptations\n"
        "- none\n",
        encoding="utf-8",
    )
    result = _run(store_guarded, repo)
    assert result.returncode != 0, result.stderr
    assert "malformed" in result.stderr
    assert "Guarded paths" in result.stderr


def test_checker_refuses_non_iso_or_impossible_dates(tmp_path):
    repo = tmp_path / "repo"
    repo.mkdir()
    _write_pinning_test(repo, "test_some_pin")

    bad_dates = ["yesterday-ish", "banana", "2026-13-45"]

    for i, bad_date in enumerate(bad_dates):
        store = tmp_path / f"reproduced-{i}.md"
        store.write_text(
            "## Guarded paths\n"
            "- loom-code/scripts/**\n\n"
            "## Instances\n"
            f"- F1 x | y | reproduced {bad_date} — pinned by test_some_pin\n\n"
            "## Prose temptations\n"
            "- none\n",
            encoding="utf-8",
        )
        result = _run(store, repo)
        assert result.returncode != 0, bad_date
        assert "malformed" in result.stderr, (bad_date, result.stderr)

    for i, bad_date in enumerate(bad_dates):
        store = tmp_path / f"held-{i}.md"
        store.write_text(
            "## Guarded paths\n"
            "- loom-code/scripts/**\n\n"
            "## Instances\n"
            f"- F1 x | y | held {bad_date}\n\n"
            "## Prose temptations\n"
            "- none\n",
            encoding="utf-8",
        )
        result = _run(store, repo)
        assert result.returncode != 0, bad_date
        assert "malformed" in result.stderr, (bad_date, result.stderr)


def test_checker_refuses_pin_defined_only_under_a_vendored_dir(tmp_path):
    repo = tmp_path / "repo"
    vendor_dir = repo / "vendor" / "node_modules" / "junk"
    vendor_dir.mkdir(parents=True)
    (vendor_dir / "test_forged.py").write_text(
        "def test_gate_refuses_the_forgery():\n    pass\n",
        encoding="utf-8",
    )
    store = tmp_path / "ATTACK-CATALOGUE.md"
    store.write_text(
        "## Guarded paths\n"
        "- loom-code/scripts/**\n\n"
        "## Instances\n"
        "- F1 x | y | reproduced 2026-08-31 — pinned by test_gate_refuses_the_forgery\n\n"
        "## Prose temptations\n"
        "- none\n",
        encoding="utf-8",
    )
    result = _run(store, repo)
    assert result.returncode != 0
    assert "dangling" in result.stderr
    assert "test_gate_refuses_the_forgery" in result.stderr


def test_checker_refuses_pin_under_a_differently_cased_vendored_dir(tmp_path):
    repo = tmp_path / "repo"
    vendor_dir = repo / "fake" / "Vendor" / "tests"
    vendor_dir.mkdir(parents=True)
    (vendor_dir / "test_c.py").write_text(
        "def test_case_forgery():\n    pass\n",
        encoding="utf-8",
    )
    store = tmp_path / "ATTACK-CATALOGUE.md"
    store.write_text(
        "## Guarded paths\n"
        "- loom-code/scripts/**\n\n"
        "## Instances\n"
        "- F1 x | y | reproduced 2026-08-31 — pinned by test_case_forgery\n\n"
        "## Prose temptations\n"
        "- none\n",
        encoding="utf-8",
    )
    result = _run(store, repo)
    assert result.returncode != 0
    assert "dangling" in result.stderr
    assert "test_case_forgery" in result.stderr


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


# ---------------------------------------------------------------------------
# `signal` subcommand — Step 3.5's single runnable command over a real git
# repo's committed diff.
# ---------------------------------------------------------------------------


def _iso_env() -> dict:
    env = dict(os.environ, PYTHONDONTWRITEBYTECODE="1")
    env.pop("GIT_DIR", None)
    env.pop("GIT_WORK_TREE", None)
    env["GIT_CONFIG_GLOBAL"] = ""
    env["GIT_CONFIG_SYSTEM"] = ""
    return env


def _git(repo: Path, *args: str) -> subprocess.CompletedProcess:
    return subprocess.run(
        ["git", "-C", str(repo), *args],
        capture_output=True,
        text=True,
        env=_iso_env(),
        check=True,
    )


def _init_repo(tmp_path: Path, name: str = "repo") -> Path:
    repo = tmp_path / name
    repo.mkdir()
    _git(repo, "init", "-q", "-b", "main")
    _git(repo, "config", "user.email", "signal@example.test")
    _git(repo, "config", "user.name", "Signal Test")
    (repo / "README.md").write_text("# repo\n", encoding="utf-8")
    _git(repo, "add", "README.md")
    _git(repo, "commit", "-q", "-m", "initial")
    return repo


def _commit_file(repo: Path, rel: str, content: str, message: str) -> None:
    path = repo / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")
    _git(repo, "add", rel)
    _git(repo, "commit", "-q", "-m", message)


def _run_signal(
    repo: Path, store: Path, plan: Path | None = None, base: str | None = None
) -> subprocess.CompletedProcess:
    argv = [
        sys.executable,
        str(SCRIPT),
        "signal",
        "--repo",
        str(repo),
        "--store",
        str(store),
    ]
    if plan is not None:
        argv += ["--plan", str(plan)]
    if base is not None:
        argv += ["--base", base]
    return subprocess.run(argv, capture_output=True, text=True, env=_iso_env())


_SIGNAL_STORE = """\
## Guarded paths
- loom-code/hooks/git-guard.py
- **/SKILL.md

## Instances
- F1 x | y | not-applicable — reason

## Prose temptations
- none
"""


def test_signal_base_unresolved_exits_2(tmp_path):
    repo = _init_repo(tmp_path)
    store = repo / "store.md"
    store.write_text(_SIGNAL_STORE, encoding="utf-8")

    result = _run_signal(repo, store, base="not-a-real-ref")

    assert result.returncode == 2, result.stdout + result.stderr
    assert "attack catalogue: base unresolved" in result.stderr


def test_signal_no_header_but_guarded_hit_exits_3(tmp_path):
    repo = _init_repo(tmp_path)
    base_sha = _git(repo, "rev-parse", "HEAD").stdout.strip()
    _commit_file(
        repo, "loom-code/hooks/git-guard.py", "# guard\n", "touch guarded path"
    )
    store = repo / "store.md"
    store.write_text(_SIGNAL_STORE, encoding="utf-8")
    plan = repo / "plan.md"
    plan.write_text(
        "Goal: g\nStage: s\nSafety-bearing: no — routine\n\n"
        "## Task 1 — t\n\n- Status: pending\n",
        encoding="utf-8",
    )

    result = _run_signal(repo, store, plan=plan, base=base_sha)

    assert result.returncode == 3, result.stdout + result.stderr
    assert "attack catalogue: STOP — Safety-bearing: no but" in result.stderr
    assert "loom-code/hooks/git-guard.py" in result.stderr


def test_signal_double_star_prefix_matches_nested_and_root_skill_md(tmp_path):
    repo = _init_repo(tmp_path)
    base_sha = _git(repo, "rev-parse", "HEAD").stdout.strip()
    _commit_file(repo, "a/b/SKILL.md", "nested\n", "nested SKILL.md")
    _commit_file(repo, "SKILL.md", "root\n", "root SKILL.md")
    store = repo / "store.md"
    store.write_text(_SIGNAL_STORE, encoding="utf-8")

    result = _run_signal(repo, store, base=base_sha)

    assert result.returncode == 0, result.stdout + result.stderr
    assert "guarded-hits=2" in result.stdout


def test_signal_exact_path_matches_only_that_path(tmp_path):
    repo = _init_repo(tmp_path)
    base_sha = _git(repo, "rev-parse", "HEAD").stdout.strip()
    _commit_file(
        repo, "loom-code/hooks/git-guard.py", "# guard\n", "exact guarded path"
    )
    _commit_file(
        repo,
        "loom-code/hooks/git-guard-other.py",
        "# not it\n",
        "similar but not exact",
    )
    store = repo / "store.md"
    store.write_text(_SIGNAL_STORE, encoding="utf-8")

    result = _run_signal(repo, store, base=base_sha)

    assert result.returncode == 0, result.stdout + result.stderr
    assert "guarded-hits=1" in result.stdout


def test_signal_output_lines_exact_shape_absent_plan(tmp_path):
    repo = _init_repo(tmp_path)
    base_sha = _git(repo, "rev-parse", "HEAD").stdout.strip()
    _commit_file(repo, "docs/notes.md", "notes\n", "unrelated docs change")
    store = repo / "store.md"
    store.write_text(_SIGNAL_STORE, encoding="utf-8")

    result = _run_signal(repo, store, base=base_sha)

    assert result.returncode == 0, result.stdout + result.stderr
    lines = result.stdout.splitlines()
    assert lines == [
        "adversarial audit: N/A — header=absent; base="
        f"{base_sha}; changed=1; guarded-hits=0; prose-hits=0",
        f"cold reader: N/A — base={base_sha}; changed=1; prose-hits=0",
    ]


def test_signal_prose_hit_fires_cold_reader(tmp_path):
    repo = _init_repo(tmp_path)
    base_sha = _git(repo, "rev-parse", "HEAD").stdout.strip()
    _commit_file(repo, "some-plugin/agents/worker.md", "worker\n", "agent prose file")
    store = repo / "store.md"
    store.write_text(_SIGNAL_STORE, encoding="utf-8")

    result = _run_signal(repo, store, base=base_sha)

    assert result.returncode == 0, result.stdout + result.stderr
    assert f"cold reader: fired — base={base_sha}; changed=1; prose-hits=1" in (
        result.stdout
    )


def test_signal_absent_store_reports_na_lines_and_exits_zero(tmp_path):
    """An absent store (the adopting-repo-without-a-store case) must never
    be treated the same as a present-but-broken one — it degrades to an
    N/A pair on stdout and exits 0, never STOP-blocking Step 5."""
    repo = _init_repo(tmp_path)
    base_sha = _git(repo, "rev-parse", "HEAD").stdout.strip()
    _commit_file(repo, "some-plugin/agents/worker.md", "worker\n", "agent prose file")
    store = repo / "does-not-exist.md"

    result = _run_signal(repo, store, base=base_sha)

    assert result.returncode == 0, result.stdout + result.stderr
    assert "attack catalogue: absent" in result.stderr
    lines = result.stdout.splitlines()
    assert lines == [
        "adversarial audit: N/A — attack catalogue: absent; header=absent; "
        f"base={base_sha}; changed=1; guarded-hits=0; prose-hits=1",
        "cold reader: N/A — attack catalogue: absent; "
        f"base={base_sha}; changed=1; prose-hits=1",
    ]


def test_signal_malformed_store_exits_one(tmp_path):
    """A store that EXISTS but is malformed (here: a duplicate '## Guarded
    paths' heading) is never degraded to N/A — it must still exit 1 with
    the family's Error: line, so a deliberately-corrupted store cannot
    skip the station the way an absent one legitimately does."""
    repo = _init_repo(tmp_path)
    base_sha = _git(repo, "rev-parse", "HEAD").stdout.strip()
    _commit_file(repo, "docs/notes.md", "notes\n", "advance HEAD past base")
    store = repo / "store.md"
    store.write_text(
        "## Guarded paths\n"
        "- loom-code/scripts/**\n\n"
        "## Guarded paths\n"
        "- loom-code/scripts/other/**\n\n"
        "## Instances\n\n"
        "## Prose temptations\n"
        "- none\n",
        encoding="utf-8",
    )

    result = _run_signal(repo, store, base=base_sha)

    assert result.returncode == 1, result.stdout + result.stderr
    assert result.stderr.startswith("Error: malformed")
    assert "attack catalogue: absent" not in result.stderr


def test_signal_refuses_unpinned_reproduced_like_the_legacy_form(tmp_path):
    """`signal` must run the same `check_store` the legacy form runs — an
    unpinned `reproduced` entry is a refusal there, so it cannot be a
    silent `fired`/exit-0 in `signal` (that gap would let a store ship a
    live vector nobody actually pinned)."""
    repo = _init_repo(tmp_path)
    base_sha = _git(repo, "rev-parse", "HEAD").stdout.strip()
    _commit_file(
        repo, "loom-code/hooks/git-guard.py", "# guard\n", "touch guarded path"
    )
    store = repo / "store.md"
    store.write_text(
        "## Guarded paths\n"
        "- loom-code/hooks/git-guard.py\n\n"
        "## Instances\n"
        "- F1 x | y | reproduced 2020-01-01\n\n"
        "## Prose temptations\n"
        "- none\n",
        encoding="utf-8",
    )

    result = _run_signal(repo, store, base=base_sha)

    assert result.returncode == 1, result.stdout + result.stderr
    assert "Error: unpinned" in result.stderr


def test_signal_bad_plan_header_names_plan_path(tmp_path):
    repo = _init_repo(tmp_path)
    base_sha = _git(repo, "rev-parse", "HEAD").stdout.strip()
    _commit_file(repo, "docs/notes.md", "notes\n", "advance HEAD past base")
    store = repo / "store.md"
    store.write_text(_SIGNAL_STORE, encoding="utf-8")
    plan = repo / "plan.md"
    plan.write_text(
        "Goal: g\nStage: s\nSafety-bearing: bogus\n\n## Task 1 — t\n",
        encoding="utf-8",
    )

    result = _run_signal(repo, store, plan=plan, base=base_sha)

    assert result.returncode == 1, result.stdout + result.stderr
    assert str(plan) in result.stderr
    assert "Safety-bearing" in result.stderr


def test_signal_missing_plan_card_module_fails_loud(tmp_path):
    """When only `check_attack_catalogue.py` is copied to a repo root
    (no sibling `plan_card.py`), a `--plan` invocation must fail with a
    named, actionable error — never a raw `ModuleNotFoundError`
    traceback."""
    isolated_dir = tmp_path / "isolated"
    isolated_dir.mkdir()
    isolated_script = isolated_dir / "check_attack_catalogue.py"
    isolated_script.write_text(SCRIPT.read_text(encoding="utf-8"), encoding="utf-8")

    repo = _init_repo(tmp_path)
    base_sha = _git(repo, "rev-parse", "HEAD").stdout.strip()
    _commit_file(repo, "docs/notes.md", "notes\n", "advance HEAD past base")
    store = repo / "store.md"
    store.write_text(_SIGNAL_STORE, encoding="utf-8")
    plan = repo / "plan.md"
    plan.write_text(
        "Goal: g\nStage: s\nSafety-bearing: no — routine\n\n## Task 1 — t\n",
        encoding="utf-8",
    )

    result = subprocess.run(
        [
            sys.executable,
            str(isolated_script),
            "signal",
            "--repo",
            str(repo),
            "--store",
            str(store),
            "--plan",
            str(plan),
            "--base",
            base_sha,
        ],
        capture_output=True,
        text=True,
        env=_iso_env(),
    )

    assert result.returncode == 1, result.stdout + result.stderr
    assert "ModuleNotFoundError" not in result.stderr
    assert "Traceback" not in result.stderr
    assert "plan_card.py beside check_attack_catalogue.py" in result.stderr


# ---------------------------------------------------------------------------
# t35b-audit-verdicts / wb-verdict-arm-a-r2 N1 / wb-verdict-arm-b-r2 N1,C5 —
# `--base` must be a strict ancestor commit of HEAD; a `git` failure inside
# `_changed_paths`/`_tracked_paths` must never silently become an empty
# list; `--store`/`--plan` must resolve inside `--repo`.
# ---------------------------------------------------------------------------


def test_signal_base_must_be_a_strict_ancestor_commit(tmp_path):
    """A `--base` equal to HEAD, or a tree/blob object rather than a
    commit, must never be accepted — either one silently empties the
    diff range and the station goes quiet (wb-verdict-arm-a-r2 N1)."""
    repo = _init_repo(tmp_path)
    head_sha = _git(repo, "rev-parse", "HEAD").stdout.strip()
    tree_sha = _git(repo, "rev-parse", "HEAD^{tree}").stdout.strip()
    store = repo / "store.md"
    store.write_text(_SIGNAL_STORE, encoding="utf-8")

    result_head = _run_signal(repo, store, base="HEAD")
    assert result_head.returncode == 2, result_head.stdout + result_head.stderr
    assert (
        "attack catalogue: base unresolved — HEAD is not a strict ancestor "
        "commit of HEAD" in result_head.stderr
    )

    result_tree = _run_signal(repo, store, base=tree_sha)
    assert result_tree.returncode == 2, result_tree.stdout + result_tree.stderr
    assert (
        f"attack catalogue: base unresolved — {tree_sha} is not a strict "
        "ancestor commit of HEAD" in result_tree.stderr
    )
    assert head_sha  # sanity: repo really has a commit


def test_changed_paths_and_tracked_paths_raise_on_git_failure(tmp_path):
    """`_changed_paths`/`_tracked_paths` must raise on any nonzero `git`
    rather than returning `[]` — an empty list is indistinguishable from
    a clean diff, so a git failure would silently read as N/A
    (wb-verdict-arm-b-r2 N1)."""
    from check_attack_catalogue import GitError, _changed_paths, _tracked_paths

    not_repo = tmp_path / "not-a-repo"
    not_repo.mkdir()

    with pytest.raises(GitError):
        _changed_paths(not_repo, "HEAD")
    with pytest.raises(GitError):
        _tracked_paths(not_repo)


def test_signal_refuses_store_outside_repo(tmp_path):
    """A `--store` (or `--plan`) resolving outside `--repo` must be
    refused — nothing currently checks that the store actually lives in
    the repo being diffed."""
    repo = _init_repo(tmp_path)
    base_sha = _git(repo, "rev-parse", "HEAD").stdout.strip()
    other_repo = tmp_path / "other"
    other_repo.mkdir()
    store = other_repo / "store.md"
    store.write_text(_SIGNAL_STORE, encoding="utf-8")

    result = _run_signal(repo, store, base=base_sha)

    assert result.returncode == 1, result.stdout + result.stderr
    assert str(store) in result.stderr
    assert str(repo) in result.stderr
    assert "outside --repo" in result.stderr


# ---------------------------------------------------------------------------
# F2 — a malformed `## Instances` bullet must never silently vanish; C8 —
# a future reproduced/held date; F3 — a non-UTF-8 store; C9 — memoized AST
# parse.
# ---------------------------------------------------------------------------


def test_instances_bullet_with_no_pipes_is_malformed_not_dropped(tmp_path):
    repo = tmp_path / "repo"
    repo.mkdir()
    store = tmp_path / "store.md"
    store.write_text(
        "## Guarded paths\n"
        "- loom-code/scripts/**\n\n"
        "## Instances\n"
        "- forge an artifact reproduced without any pipes at all\n\n"
        "## Prose temptations\n"
        "- none\n",
        encoding="utf-8",
    )
    result = _run(store, repo)
    assert result.returncode != 0, result.stdout + result.stderr
    assert "malformed" in result.stderr


def test_instances_bullet_with_one_pipe_is_malformed_not_dropped(tmp_path):
    repo = tmp_path / "repo"
    repo.mkdir()
    store = tmp_path / "store.md"
    store.write_text(
        "## Guarded paths\n"
        "- loom-code/scripts/**\n\n"
        "## Instances\n"
        "- forge | reproduced totally-bogus\n\n"
        "## Prose temptations\n"
        "- none\n",
        encoding="utf-8",
    )
    result = _run(store, repo)
    assert result.returncode != 0, result.stdout + result.stderr
    assert "malformed" in result.stderr


def test_checker_refuses_future_reproduced_date(tmp_path):
    repo = tmp_path / "repo"
    vendor_dir = repo / "tests"
    vendor_dir.mkdir(parents=True)
    (vendor_dir / "test_x.py").write_text(
        "def test_future():\n    pass\n", encoding="utf-8"
    )
    store = tmp_path / "store.md"
    store.write_text(
        "## Guarded paths\n"
        "- loom-code/scripts/**\n\n"
        "## Instances\n"
        "- F1 x | y | reproduced 2099-12-31 — pinned by test_future\n\n"
        "## Prose temptations\n"
        "- none\n",
        encoding="utf-8",
    )
    result = _run(store, repo)
    assert result.returncode != 0, result.stdout + result.stderr
    assert "malformed" in result.stderr


def test_checker_refuses_future_held_date(tmp_path):
    repo = tmp_path / "repo"
    repo.mkdir()
    store = tmp_path / "store.md"
    store.write_text(
        "## Guarded paths\n"
        "- loom-code/scripts/**\n\n"
        "## Instances\n"
        "- F1 x | y | held 2099-12-31\n\n"
        "## Prose temptations\n"
        "- none\n",
        encoding="utf-8",
    )
    result = _run(store, repo)
    assert result.returncode != 0, result.stdout + result.stderr
    assert "malformed" in result.stderr


def test_checker_fails_loud_on_non_utf8_store(tmp_path):
    repo = tmp_path / "repo"
    repo.mkdir()
    store = tmp_path / "store.md"
    store.write_bytes(b"## Guarded paths\n- x\n\n## Instances\n- caf\xe9\n")

    result = _run(store, repo)

    _assert_fails_loud(result, str(store))


def test_defined_function_names_is_memoized_per_path_and_mtime(tmp_path):
    from check_attack_catalogue import _defined_function_names_cached

    _defined_function_names_cached.cache_clear()
    test_file = tmp_path / "test_memo.py"
    test_file.write_text("def test_one():\n    pass\n", encoding="utf-8")

    from check_attack_catalogue import _defined_function_names

    _defined_function_names(test_file)
    _defined_function_names(test_file)

    info = _defined_function_names_cached.cache_info()
    assert info.hits >= 1, info
