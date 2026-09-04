"""Adversarial probes against W0-02 (package-tests run in parallel):
`loom-code/scripts/test_package_tests_command.py`'s own contract tests, and
the checker rule that consumes their result (`push.probes-package-tests`,
`declared_test_command`/`check_probes_package_tests` in
`loom-code/scripts/loom_checker.py`).

No mutation/fuzz tool is declared for this repo, so this file is the
required >=3 executable abuse/boundary cases. It never edits the real
committed files (docs/loom/KICKOFF-DEFAULTS.md, .github/workflows/
loom-code-ci.yml, requirements-dev.txt) -- every mutation happens on a
scaffolded temp copy that reproduces the relative path shape
`test_package_tests_command.py` depends on (its `REPO` constant is
`Path(__file__).resolve().parents[2]`, i.e. two directories up from
wherever the copied script sits), so the SAME test file under test runs
unmodified against a deliberately broken environment.

Reuses `build_repo`/`run_checker`/`blocked_rules`/`rebuild`/
`recommit_review` from `test_loom_checker_push.py` (same `loom-code/scripts/`
directory) for the checker-side cases, rather than re-deriving a second
fixture builder.

A case that reveals a defect asserts the CORRECT behaviour per spec and is
marked `# DEFECT:` inline so a reviewer reads the assertion as a finding,
not a broken test.

Graduated from docs/loom/2026-09-03-package-tests-run-in-parallel/evidence/
probes/test_abuse_package_tests_command.py, graduated 2026-09-04 (W0-01).
"""
from __future__ import annotations

import shutil
import subprocess
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(Path(__file__).parent))

from test_loom_checker_push import (  # noqa: E402
    PASSING_COMMAND,
    blocked_rules,
    build_repo,
    rebuild,
    recommit_review,
    run_checker,
)

REAL_KICKOFF = REPO_ROOT / "docs" / "loom" / "KICKOFF-DEFAULTS.md"
REAL_CI_WORKFLOW = REPO_ROOT / ".github" / "workflows" / "loom-code-ci.yml"
REAL_REQUIREMENTS_DEV = REPO_ROOT / "requirements-dev.txt"
REAL_UNIT_TEST = REPO_ROOT / "loom-code" / "scripts" / "test_package_tests_command.py"


def _scaffold(tmp_path: Path, *, kickoff: str | None = None,
              ci_workflow: str | None = None,
              requirements_dev: str | None = None) -> Path:
    """A temp repo subset with exactly the files
    `test_package_tests_command.py` reads, so the real (never edited) unit
    test can be run unmodified against a deliberately mutated environment.
    Any of the three text overrides replaces that file's baseline content;
    omitted ones keep the real repo's committed content."""
    repo = tmp_path / "repo"
    (repo / "docs" / "loom").mkdir(parents=True)
    (repo / ".github" / "workflows").mkdir(parents=True)
    (repo / "loom-code" / "scripts").mkdir(parents=True)

    (repo / "docs" / "loom" / "KICKOFF-DEFAULTS.md").write_text(
        kickoff if kickoff is not None else REAL_KICKOFF.read_text(encoding="utf-8"),
        encoding="utf-8",
    )
    (repo / ".github" / "workflows" / "loom-code-ci.yml").write_text(
        ci_workflow if ci_workflow is not None else REAL_CI_WORKFLOW.read_text(encoding="utf-8"),
        encoding="utf-8",
    )
    (repo / "requirements-dev.txt").write_text(
        requirements_dev if requirements_dev is not None
        else REAL_REQUIREMENTS_DEV.read_text(encoding="utf-8"),
        encoding="utf-8",
    )
    shutil.copy(REAL_UNIT_TEST, repo / "loom-code" / "scripts" / "test_package_tests_command.py")
    return repo / "loom-code" / "scripts" / "test_package_tests_command.py"


def _run(node: Path, node_name: str) -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, "-m", "pytest", f"{node}::{node_name}", "-q"],
        capture_output=True, text=True, timeout=60,
    )


# --- (1) sanity: unmutated scaffold reproduces a PASS ----------------------


def test_scaffold_unmutated_reproduces_pass(tmp_path: Path) -> None:
    """Attack: prove the scaffold itself is not the reason mutations fail --
    an unmutated copy of the three real files must still pass the real
    unit test, or every mutation case below would be meaningless.
    Expected: PASS (exit 0).
    Observed: PASS."""
    node = _scaffold(tmp_path)
    result = _run(node, "test_kickoff_and_ci_run_the_same_parallel_command")
    assert result.returncode == 0, result.stdout + result.stderr


# --- (2) KICKOFF-DEFAULTS mutations must be caught -------------------------


def _mutate_kickoff(line_suffix: str) -> str:
    real = REAL_KICKOFF.read_text(encoding="utf-8")
    lines = real.splitlines(keepends=True)
    out = []
    for line in lines:
        if line.startswith("- package-tests:"):
            out.append(
                "- package-tests: " + line_suffix
                + " — mutated by adversarial probe (2026-09-03)\n"
            )
        else:
            out.append(line)
    return "".join(out)


@pytest.mark.parametrize(
    "mutation_name,line_suffix",
    [
        ("drop_n_auto", "python3 -m pytest loom-code/scripts/ scripts/ .claude/hooks/ -q"),
        ("wrong_path", "python3 -m pytest loom-code/scripts/ -q -n auto"),
        ("reordered_tokens", "python3 -m pytest -n auto loom-code/scripts/ scripts/ .claude/hooks/ -q"),
        ("fixed_worker_count", "python3 -m pytest loom-code/scripts/ scripts/ .claude/hooks/ -q -n 4"),
    ],
)
def test_kickoff_mutation_fails_the_parity_test(
    tmp_path: Path, mutation_name: str, line_suffix: str
) -> None:
    """Attack: mutate KICKOFF-DEFAULTS' package-tests line (drop `-n auto`,
    narrow the path, reorder tokens, or pin a fixed worker count) in a temp
    copy only -- the real file is never touched.
    Expected: `test_kickoff_and_ci_run_the_same_parallel_command` FAILS,
    because a test that cannot fail on any of these divergences is not
    actually checking parity.
    Observed: FAILS for all four mutations (see report)."""
    node = _scaffold(tmp_path, kickoff=_mutate_kickoff(line_suffix))
    result = _run(node, "test_kickoff_and_ci_run_the_same_parallel_command")
    assert result.returncode != 0, (
        f"mutation {mutation_name!r} did not fail the test -- it cannot fail, "
        f"so it proves nothing:\n{result.stdout}{result.stderr}"
    )


# --- (3) CI workflow mutations must be caught -------------------------------


def _mutate_ci(*, drop_n_auto: bool = False, drop_requirements: bool = False,
               rename_step: bool = False) -> str:
    text = REAL_CI_WORKFLOW.read_text(encoding="utf-8")
    if drop_n_auto:
        text = text.replace(
            "python3 -m pytest loom-code/scripts/ scripts/ .claude/hooks/ -v -n auto",
            "python3 -m pytest loom-code/scripts/ scripts/ .claude/hooks/ -v",
        )
    if drop_requirements:
        text = text.replace(
            "run: python3 -m pip install --quiet -r requirements-dev.txt",
            "run: python3 -m pip install --quiet pytest pyyaml",
        )
    if rename_step:
        text = text.replace(
            "- name: Install test deps", "- name: Install python test dependencies"
        )
    return text


@pytest.mark.parametrize(
    "mutation_name,kwargs",
    [
        ("drop_n_auto", {"drop_n_auto": True}),
        ("drop_requirements_ref", {"drop_requirements": True}),
        ("rename_install_step", {"rename_step": True}),
    ],
)
def test_ci_workflow_mutation_fails_its_own_test(
    tmp_path: Path, mutation_name: str, kwargs: dict
) -> None:
    """Attack: mutate the CI workflow (drop `-n auto`, stop installing from
    `requirements-dev.txt`, or rename the `Install test deps` step the W0-01
    test locates by name) in a temp copy only.
    Expected: the matching real unit test FAILS (or errors, for the renamed
    step, since `workflow_text.index("Install test deps")` raises
    `ValueError` -- still a nonzero exit, still loud, never a silent pass).
    Expected node: `test_kickoff_and_ci_run_the_same_parallel_command` for
    the `-n auto` drop; `test_dev_requirements_declare_xdist_and_ci_installs_from_them`
    for the requirements-ref drop and the step rename.
    Observed: nonzero exit for all three (see report)."""
    node = _scaffold(tmp_path, ci_workflow=_mutate_ci(**kwargs))
    test_name = (
        "test_kickoff_and_ci_run_the_same_parallel_command"
        if mutation_name == "drop_n_auto"
        else "test_dev_requirements_declare_xdist_and_ci_installs_from_them"
    )
    result = _run(node, test_name)
    assert result.returncode != 0, (
        f"mutation {mutation_name!r} did not fail its test:\n"
        f"{result.stdout}{result.stderr}"
    )


# --- (4) requirements-dev.txt without pytest-xdist must be caught ----------


def test_requirements_dev_without_xdist_fails_w0_01_test(tmp_path: Path) -> None:
    """Attack: comment out `pytest-xdist` in a temp copy of
    requirements-dev.txt -- the file still installs the rest, so a
    less-precise check (e.g. \"file is nonempty\") would pass this by
    accident.
    Expected: `test_dev_requirements_declare_xdist_and_ci_installs_from_them`
    FAILS, because a commented-out dependency is not an installed one.
    Observed: the real unit test STILL PASSES -- its assertion is
    `"pytest-xdist" in requirements_text`, a bare substring check that
    matches `# pytest-xdist` (the comment token) exactly as well as an
    active requirement line. DEFECT, not a broken probe -- this assertion
    encodes the correct spec and is left red on purpose (see docstring of
    `test_kickoff_and_ci_run_the_same_parallel_command`'s sibling probes
    above for the same convention).
    Fixed at W0-01 fix commit: the W0-01 test now fails on the
    commented-out line as expected."""
    real = REAL_REQUIREMENTS_DEV.read_text(encoding="utf-8")
    mutated = "\n".join(
        f"# {line}" if line.strip() == "pytest-xdist" else line
        for line in real.splitlines()
    ) + "\n"
    assert "pytest-xdist" not in [
        ln.strip() for ln in mutated.splitlines() if not ln.startswith("#")
    ]
    node = _scaffold(tmp_path, requirements_dev=mutated)
    result = _run(node, "test_dev_requirements_declare_xdist_and_ci_installs_from_them")
    # DEFECT (loom-code/scripts/test_package_tests_command.py:23): the real
    # assertion `"pytest-xdist" in requirements_text` is a substring check
    # that a commented-out `# pytest-xdist` line still satisfies -- this
    # probe asserts the CORRECT behaviour (a comment is not a declaration)
    # and therefore fails red against the current code, on purpose.
    assert result.returncode != 0, result.stdout + result.stderr


# --- (5) absent input: KICKOFF-DEFAULTS with no package-tests line ---------


def test_kickoff_missing_package_tests_line_fails_loudly(tmp_path: Path) -> None:
    """Attack: hostile/absent input -- a KICKOFF-DEFAULTS.md that carries no
    `- package-tests:` line at all (e.g. the key renamed or deleted
    upstream).
    Expected: the test errors out (nonzero exit) rather than silently
    skipping or reporting a false PASS -- `next(...)` with no default raises
    `StopIteration`, which pytest turns into a loud collection/run error.
    Observed: nonzero exit, StopIteration surfaced."""
    stripped = "\n".join(
        line for line in REAL_KICKOFF.read_text(encoding="utf-8").splitlines()
        if not line.startswith("- package-tests:")
    ) + "\n"
    node = _scaffold(tmp_path, kickoff=stripped)
    result = _run(node, "test_kickoff_and_ci_run_the_same_parallel_command")
    assert result.returncode != 0, result.stdout + result.stderr


# --- (6) checker: a probe missing the `-n auto` token is rejected ----------


def test_checker_rejects_recorded_probe_missing_n_auto_token(tmp_path: Path) -> None:
    """Attack: KICKOFF-DEFAULTS declares `-n auto`, but the recorded
    package-tests probe's command string drops that one token (a "close
    enough" command that would still exit 0, since dropping `-n auto` just
    makes the run serial instead of parallel).
    Expected per spec (`push.probes-package-tests` /
    `check_probes_package_tests`): BLOCKED -- the checker compares the
    recorded command against the declared one via `_squeeze`, and a
    token-level mismatch is not close enough.
    Observed: BLOCKED, `push.probes-package-tests` in blocked rules."""
    declared = f"{PASSING_COMMAND} -n auto"
    repo = build_repo(tmp_path, package_tests=declared)
    body = rebuild(repo)
    for probe in body["probes"]:
        if probe.get("kind") == "package-tests":
            probe["command"] = PASSING_COMMAND  # drops "-n auto"
    recommit_review(repo, body)
    result = run_checker("push", cwd=repo)
    assert result.returncode == 1, result.stdout + result.stderr
    assert "push.probes-package-tests" in blocked_rules(result)


# --- (7) boundary: -n auto degrades cleanly to a single worker -------------


def test_n_1_boundary_still_passes_on_the_real_suite(tmp_path: Path) -> None:
    """Attack: boundary case for `-n auto` on a hypothetical 1-core box --
    force exactly one xdist worker (`-n 1`) on the REAL, unmutated
    `test_package_tests_command.py` module and confirm the suite still
    passes; a design that only works at N>1 workers would be a hidden
    single-point-of-failure the CI's own multi-core runner would never
    surface.
    Expected: PASS (exit 0).
    Observed: PASS."""
    result = subprocess.run(
        [sys.executable, "-m", "pytest",
         str(REAL_UNIT_TEST), "-q", "-n", "1"],
        cwd=str(REPO_ROOT), capture_output=True, text=True, timeout=60,
    )
    assert result.returncode == 0, result.stdout + result.stderr


if __name__ == "__main__":
    sys.exit(pytest.main([__file__, "-q"]))
