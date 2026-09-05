"""Checkpoint-adversary probes against the wave-1 delta (scope `wave-end:1`).

The build-phase adversary wrote `test_abuse_rehearse_probes.py` before
`loom-code/scripts/rehearse_probes.py` existed. This file attacks what is
now written, at `294d85ea`, and it attacks the states the implementation
forgot rather than the ones it was designed against:

- the junit nodeid reconstruction, which owns every name a human reads out
  of the report -- a test inside a class, a parametrized id carrying `/`
  and `.`;
- the caller-supplied test path in its absolute form, which decides whether
  the run happens in the CI-shaped clone at all;
- the default glob when it expands to nothing, which decides whether the
  rehearsal is scoped or unbounded;
- states of the caller's own repository: a HEAD reachable only through the
  detached `HEAD` ref, an explicit path that collects no test at all;
- the report's own vocabulary, where an expected failure arrives dressed as
  a skip.

For W1-02 (the nine deleted history-bound tests) it re-checks the two
claims that deletion rests on: nothing in the graduated suite still reaches
for a deleted helper, and every deleted test name is either preserved in
its own change's evidence original or belongs to a helper this change
removed outright.

Every case builds its own throwaway git repository under `tmp_path` (real
`git init`, real commits, `core.autocrlf` pinned false) and drives the
script as a subprocess; none of them writes to this repository.

Probes whose assertion message opens with `REPRODUCED:` are red on
purpose: they hold a defect measured at `294d85ea` and stay red until the
script changes. They are not weakened to pass.
"""
from __future__ import annotations

import ast
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[5]
SCRIPT = REPO_ROOT / "loom-code" / "scripts" / "rehearse_probes.py"
SCRIPTS_DIR = REPO_ROOT / "loom-code" / "scripts"

TIMEOUT = 300


# --------------------------------------------------------------------------
# harness
# --------------------------------------------------------------------------

def _git(repo: Path, *args: str) -> str:
    proc = subprocess.run(
        ["git", "-C", str(repo), *args], capture_output=True, text=True, timeout=TIMEOUT
    )
    assert proc.returncode == 0, f"git {' '.join(args)} failed: {proc.stderr}"
    return proc.stdout.strip()


def make_repo(root: Path, *, trunk: str = "main", name: str = "work") -> Path:
    """A minimal working tree with one commit on `trunk`."""
    repo = root / name
    repo.mkdir(parents=True)
    subprocess.run(["git", "init", "-q", str(repo)], check=True, capture_output=True)
    _git(repo, "symbolic-ref", "HEAD", f"refs/heads/{trunk}")
    _git(repo, "config", "core.autocrlf", "false")
    _git(repo, "config", "user.email", "adversary@example.invalid")
    _git(repo, "config", "user.name", "Adversary")
    _git(repo, "config", "commit.gpgsign", "false")
    (repo / "README").write_text("committed content\n", encoding="utf-8")
    _git(repo, "add", "README")
    _git(repo, "commit", "-q", "-m", "first commit")
    return repo


def commit_file(repo: Path, relpath: str, text: str, message: str) -> Path:
    path = repo / relpath
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")
    _git(repo, "add", relpath)
    _git(repo, "commit", "-q", "-m", message)
    return path


def run_rehearse(*args: str, repo: Path) -> subprocess.CompletedProcess:
    assert SCRIPT.is_file(), f"{SCRIPT} is absent"
    return subprocess.run(
        [sys.executable, str(SCRIPT), "--repo", str(repo), *args],
        capture_output=True, text=True, timeout=TIMEOUT, cwd=str(REPO_ROOT),
    )


def out(proc: subprocess.CompletedProcess) -> str:
    return proc.stdout + proc.stderr


def reported_nodeids(text: str, marker: str) -> list[str]:
    """The nodeids the report lists under `FAILED`/`SKIPPED`, in order.

    The header line (`FAILED (1)`) is excluded; a SKIPPED entry's trailing
    `: <reason>` is stripped, so both markers yield bare nodeids.
    """
    found = []
    for line in text.splitlines():
        if not line.startswith(marker + " "):
            continue
        rest = line[len(marker) + 1:]
        if rest.startswith("("):
            continue
        found.append(rest.split(":", 1)[0] if marker == "SKIPPED" and "::" in rest else rest)
    return [n.strip() for n in found]


def selects_exactly_one(repo: Path, nodeid: str) -> subprocess.CompletedProcess:
    """Ask pytest, inside `repo`, to collect the single test `nodeid` names."""
    return subprocess.run(
        [sys.executable, "-m", "pytest", "--collect-only", "-q",
         "-p", "no:cacheprovider", nodeid],
        capture_output=True, text=True, timeout=TIMEOUT, cwd=str(repo),
    )


CLASS_TEST = (
    "class TestThing:\n"
    "    def test_thing_alwaysFalse_fails(self):\n"
    "        assert False\n"
)

PARAM_TEST = (
    "import pytest\n\n"
    "@pytest.mark.parametrize('value', ['a/b.py', 'x.y'])\n"
    "def test_param_hostileIds_fails(value):\n"
    "    assert value == 'nope'\n"
)

XFAIL_TEST = (
    "import pytest\n\n"
    "@pytest.mark.xfail(reason='known limitation')\n"
    "def test_expected_knownLimitation_failsOnPurpose():\n"
    "    assert False\n"
)


# --------------------------------------------------------------------------
# the junit nodeid reconstruction
# --------------------------------------------------------------------------

def test_rehearsalReport_failureInsideATestClass_namesANodeidPytestCanSelect(
    tmp_path: Path,
) -> None:
    """A failing method of a test class must be reported under a nodeid a
    reader can paste back into pytest. `_parse_junit` builds the nodeid from
    the junit `classname` attribute, which carries the class name as its last
    dotted segment, so the class becomes a directory in a fabricated path."""
    repo = make_repo(tmp_path, name="cls")
    rel = "loom-code/scripts/test_probes_cls.py"
    commit_file(repo, rel, CLASS_TEST, "class-based probe")

    proc = run_rehearse(rel, repo=repo)
    failed = reported_nodeids(out(proc), "FAILED")
    assert len(failed) == 1, f"expected one FAILED line, got {failed}\n{out(proc)}"

    collected = selects_exactly_one(repo, failed[0])
    assert collected.returncode == 0, (
        "REPRODUCED: the report names a nodeid pytest cannot select -- "
        f"{failed[0]!r}; the real nodeid is {rel}::TestThing::"
        "test_thing_alwaysFalse_fails. `_parse_junit` splices the junit "
        "`classname` (module dots plus the class name) into a file path, so "
        "every class-based graduated probe is reported under a path that "
        "does not exist.\n" + collected.stdout + collected.stderr
    )


def test_rehearsalReport_parametrizedIdsCarryingSlashAndDot_surviveIntoTheNodeid(
    tmp_path: Path,
) -> None:
    """A parametrized id containing `/` and `.` -- the two characters the
    nodeid reconstruction itself manipulates -- must reach the report intact
    and stay selectable."""
    repo = make_repo(tmp_path, name="param")
    rel = "loom-code/scripts/test_probes_param.py"
    commit_file(repo, rel, PARAM_TEST, "parametrized probe")

    proc = run_rehearse(rel, repo=repo)
    failed = reported_nodeids(out(proc), "FAILED")
    assert failed == [
        f"{rel}::test_param_hostileIds_fails[a/b.py]",
        f"{rel}::test_param_hostileIds_fails[x.y]",
    ], f"parametrized ids were mangled: {failed}\n{out(proc)}"
    for nodeid in failed:
        collected = selects_exactly_one(repo, nodeid)
        assert collected.returncode == 0, (
            f"the report names a nodeid pytest cannot select: {nodeid!r}\n"
            + collected.stdout + collected.stderr
        )


def test_rehearsalReport_xfailedTest_staysOutOfTheSkippedList(tmp_path: Path) -> None:
    """An expected failure is not a skip. The report's SKIPPED section is the
    section a human reads for probes that verified nothing, and junit encodes
    an xfail as a `<skipped>` element, so an xfail lands there with its own
    reason attached and inflates the count the intent's Acceptance 4 reads."""
    repo = make_repo(tmp_path, name="xf")
    rel = "loom-code/scripts/test_probes_xf.py"
    commit_file(repo, rel, XFAIL_TEST, "xfail probe")

    proc = run_rehearse(rel, repo=repo)
    text = out(proc)
    skipped = reported_nodeids(text, "SKIPPED")
    assert skipped == [], (
        "REPRODUCED: an xfailed test is listed as a skip -- "
        f"{skipped}; junit writes an xfail as a `<skipped>` element and "
        "`_parse_junit` reads every one of them, so the SKIPPED count a "
        "reader is told to audit mixes expected failures in with probes that "
        "genuinely verified nothing.\n" + text
    )


# --------------------------------------------------------------------------
# which tree actually runs
# --------------------------------------------------------------------------

def test_rehearseProbes_absoluteTestPathInsideTheRepo_runsTheCloneNotTheWorkingTree(
    tmp_path: Path,
) -> None:
    """An absolute test path passes `_validate_test_path` and is then handed
    to pytest verbatim with `cwd` set to the clone -- so it addresses the
    caller's own working tree, and the uncommitted edit the clone exists to
    exclude runs after all."""
    repo = make_repo(tmp_path, name="abs")
    rel = "loom-code/scripts/test_probes_abs.py"
    path = commit_file(
        repo, rel, "def test_abs_committedContent_passes():\n    assert True\n", "green probe"
    )
    path.write_text(
        "def test_abs_committedContent_passes():\n"
        "    assert False, 'the uncommitted working-tree copy ran'\n",
        encoding="utf-8",
    )

    proc = run_rehearse(str(path), repo=repo)
    text = out(proc)
    assert proc.returncode == 0 and "the uncommitted working-tree copy ran" not in text, (
        "REPRODUCED: an absolute test path escapes the CI-shaped clone -- the "
        "rehearsal ran the caller's uncommitted working-tree file instead of "
        "the committed copy in the clone, which is the one thing the clone "
        "exists to prevent. `_validate_test_path` accepts the absolute form "
        "and `main` forwards it unchanged to a pytest whose cwd is the "
        f"clone.\nexit={proc.returncode}\n{text}"
    )


def test_rehearseProbes_defaultGlobMatchingNothing_staysScopedToTheProbeGlob(
    tmp_path: Path,
) -> None:
    """With no positional paths and no `test_probes_*.py` in the tree,
    `_default_paths` returns an empty list and `main` runs pytest with no
    path argument at all -- which collects the whole clone."""
    repo = make_repo(tmp_path, name="glob")
    commit_file(
        repo, "othertests/test_unrelated.py",
        "def test_unrelated_notAProbe_fails():\n    assert False\n",
        "an unrelated failing test",
    )

    proc = run_rehearse(repo=repo)
    text = out(proc)
    assert "othertests/test_unrelated.py" not in text, (
        "REPRODUCED: the default run is unbounded when the probe glob matches "
        "nothing -- an unrelated test outside `loom-code/scripts/"
        "test_probes_*.py` was collected and reported. An empty expansion "
        "must be refused by name, since a rehearsal that silently widens to "
        f"the entire repository reports failures nobody asked about.\n{text}"
    )


# --------------------------------------------------------------------------
# states of the caller's own repository
# --------------------------------------------------------------------------

def test_rehearseProbes_headReachableOnlyThroughDetachedHead_rehearsesThatCommit(
    tmp_path: Path,
) -> None:
    """A working tree sitting on a detached HEAD whose commit no branch
    contains still has to be the commit rehearsed -- `git clone` advertises
    the source `HEAD` ref itself, so the commit does travel."""
    repo = make_repo(tmp_path, name="detached")
    rel = "loom-code/scripts/test_probes_detached.py"
    commit_file(repo, rel, "def test_detached_onBranch_passes():\n    assert True\n", "on branch")
    _git(repo, "checkout", "-q", "--detach", "HEAD")
    (repo / rel).write_text(
        "def test_detached_onlyOnDetachedHead_fails():\n    assert False\n", encoding="utf-8"
    )
    _git(repo, "add", rel)
    _git(repo, "commit", "-q", "-m", "reachable only through HEAD")
    head = _git(repo, "rev-parse", "HEAD")

    proc = run_rehearse(rel, repo=repo)
    text = out(proc)
    assert head in text, f"the report names a sha other than the caller's HEAD\n{text}"
    assert "test_detached_onlyOnDetachedHead_fails" in text and proc.returncode != 0, (
        "the detached-HEAD-only commit was not the commit rehearsed: its "
        f"failing test is absent from the report (exit {proc.returncode})\n{text}"
    )


def test_rehearseProbes_explicitPathCollectingNoTest_exitsNonZero(tmp_path: Path) -> None:
    """A named test file that collects nothing (pytest exit code 5) is a
    rehearsal that verified nothing; the exit code has to carry that."""
    repo = make_repo(tmp_path, name="empty")
    rel = "loom-code/scripts/test_probes_empty.py"
    commit_file(repo, rel, "# a probe file with no test in it\n", "empty probe file")

    proc = run_rehearse(rel, repo=repo)
    assert proc.returncode != 0, (
        "a probe path that collects no test exited zero, so a graduated file "
        f"whose tests all vanished would rehearse green\n{out(proc)}"
    )


# --------------------------------------------------------------------------
# W1-02: the nine deleted history-bound tests
# --------------------------------------------------------------------------

DELETED_HELPERS = (
    "_confirm_intent_sha",
    "_skip_if_language_policy_shipped",
    "_language_policy_intent_closed",
    "_LANGUAGE_POLICY_INTENT",
    "_distinct_wave_ids",
    "_verdict_rounds_so_far",
    "LANGUAGE_POLICY_TEST",
    "LANGUAGE_POLICY_BRANCH_END_TEST",
)

EDITED_FILES = (
    "test_probes_complexity_wave_end.py",
    "test_probes_language_policy.py",
    "test_probes_language_policy_branch_end.py",
    "test_probes_memory_step_wave_end.py",
)

# deleted test name -> the evidence original that still holds it
DELETED_TESTS_WITH_ORIGINALS = {
    "test_every_w1_implementer_started_precedes_its_first_task_commit":
        "docs/loom/2026-09-05-review-sees-complexity-and-process-cost/evidence/probes/"
        "test_abuse_complexity_wave_end.py",
    "test_dispatch_commit_count_within_waves_plus_rounds_bound":
        "docs/loom/2026-09-05-review-sees-complexity-and-process-cost/evidence/probes/"
        "test_abuse_complexity_wave_end.py",
    "test_branchdiff_scope_clean":
        "docs/loom/2026-09-03-artifact-language-policy/evidence/probes/"
        "test_abuse_language_policy.py",
    "test_VersionStamps_acrossAllFiles_agree":
        "docs/loom/2026-09-03-artifact-language-policy/evidence/probes/"
        "test_abuse_language_policy_branch_end.py",
    "test_BranchDiff_docsLoomPaths_scopedToChangeId":
        "docs/loom/2026-09-03-artifact-language-policy/evidence/probes/"
        "test_abuse_language_policy_branch_end.py",
    "test_skipguard_realintentfile_currentlyclosed":
        "docs/loom/2026-09-05-memory-step-before-branch-end-and-prose-pin-rule/evidence/probes/"
        "test_abuse_memory_step_wave_end.py",
}

# deleted with the helper it tested, so no evidence original is expected
DELETED_TESTS_OF_DELETED_HELPERS = (
    "test_LanguagePolicyGuard_syntheticIntentTexts_decidesSkip",
    "test_skipguard_statusclosedinfencedcodespan_notfrontmattertriggered",
)


def _graduated_sources() -> dict[str, str]:
    return {
        path.name: path.read_text(encoding="utf-8")
        for path in sorted(SCRIPTS_DIR.glob("test_probes_*.py"))
    }


def test_deletedHelpers_wholeGraduatedSuite_keepNoResidualReference() -> None:
    """Deleting a guard leaves the tests that called it broken by name, not by
    assertion (the W1-02 commit hit exactly that across file boundaries via an
    `exec`). No graduated probe may still mention one."""
    sources = _graduated_sources()
    residue = {
        name: sorted(h for h in DELETED_HELPERS if h in text)
        for name, text in sources.items()
    }
    residue = {name: hits for name, hits in residue.items() if hits}
    assert residue == {}, (
        "graduated probes still reach for helpers this change deleted: "
        f"{residue}"
    )


def test_deletedTests_graduatedSuiteAndEvidenceOriginals_areRecoverableByName() -> None:
    """Every deleted test name is gone from the graduated suite, and is either
    preserved in its own change's evidence original -- the frozen record W1-02
    promises stays untouched -- or belongs to a helper deleted outright."""
    sources = _graduated_sources()
    joined = "\n".join(sources.values())

    still_live = [
        name for name in
        (*DELETED_TESTS_WITH_ORIGINALS, *DELETED_TESTS_OF_DELETED_HELPERS)
        if f"def {name}" in joined
    ]
    assert still_live == [], f"deleted tests are still in the graduated suite: {still_live}"

    missing_originals = []
    for name, original in DELETED_TESTS_WITH_ORIGINALS.items():
        path = REPO_ROOT / original
        if not path.is_file() or f"def {name}" not in path.read_text(encoding="utf-8"):
            missing_originals.append((name, original))
    assert missing_originals == [], (
        "the evidence original that was supposed to keep the deleted test "
        f"readable no longer carries it: {missing_originals}"
    )

    live_subjects = [
        helper for helper in ("_language_policy_intent_closed", "_load_guard")
        if helper in joined
    ]
    assert live_subjects == [], (
        "a self-test was deleted as 'testing a helper that is going away', "
        f"but the helper is still in the graduated suite: {live_subjects}"
    )


def test_editedProbeFiles_afterTheDeletions_importNothingUnused() -> None:
    """The orphan rule: a removal that leaves its imports behind is the
    cheapest way to tell that the deletion was mechanical rather than read."""
    unused: dict[str, list[str]] = {}
    for name in EDITED_FILES:
        path = SCRIPTS_DIR / name
        source = path.read_text(encoding="utf-8")
        tree = ast.parse(source)
        imported: set[str] = set()
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    imported.add(alias.asname or alias.name.split(".")[0])
            elif isinstance(node, ast.ImportFrom) and node.module != "__future__":
                for alias in node.names:
                    imported.add(alias.asname or alias.name)
        used = {n.id for n in ast.walk(tree) if isinstance(n, ast.Name)}
        used |= {
            n.value.id for n in ast.walk(tree)
            if isinstance(n, ast.Attribute) and isinstance(n.value, ast.Name)
        }
        # a name mentioned only inside an exec'd or quoted string still counts
        leftover = sorted(
            imp for imp in imported
            if imp not in used and source.count(imp) < 2
        )
        if leftover:
            unused[name] = leftover
    assert unused == {}, f"the deletions left unused imports behind: {unused}"
