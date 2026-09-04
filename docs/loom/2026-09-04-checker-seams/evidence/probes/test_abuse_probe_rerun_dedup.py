"""Adversarial probes against W0-04 (probes rerun per-artifact, not
per-record), written BEFORE W0-04 exists, per plan task W0-01.

Target (does not exist yet at W0-01 time): `check_probes_adversarial()` in
`loom-code/scripts/loom_checker.py` grouping formatting-valid `kind:
adversarial` records by `artifact` and running `subprocess.run` ONCE per
distinct artifact, applying that one result to every record naming it --
not once per record (intent Acceptance #4 / plan W0-04).

Called directly (unit-level, like `loom_checker.py`'s own body calls it)
rather than through the full `push` pipeline: `check_probes_adversarial`
is the exact function under attack, it takes a real git repo + a `review`
dict + `reviewed_id`, and it runs the artifact for real via
`subprocess.run` -- exercising it directly still attacks the real
execution path, without needing the unrelated `push.verdicts` /
`push.dispatch-covers-tasks` / etc. scaffolding `test_loom_checker_push.py`
carries for the full-pipeline tests.

Execution count is proven, not asserted from memory: every fixture's
artifact appends one line to a counter file living OUTSIDE the git repo (so
counting invocations never collides with the "working tree must stay
clean to re-run" check the rule itself enforces).

Plan-fact correction: the plan's Current State Evidence says the
2026-09-03-loom-post-merge-seams review.json holds "23 筆對抗紀錄指向 2 個
檔案" (23 adversarial records naming 2 files). The actual file
(docs/loom/2026-09-03-loom-post-merge-seams/review.json) holds 126 records
of `kind: adversarial`: 116 non-spec ones naming 3 distinct code artifacts
(60 + 55 + 1 records) and 10 more `scope: spec` red-team records each
naming its own unique `.md` file (so 13 distinct artifacts total, not 2).
This file does not try to replay that exact historical review.json (its
`sha` values do not match a clean-tree checkout at HEAD, so the rule would
reject every record on the sha check before dedup ever mattered); instead
it reproduces the SHAPE the plan's "existing records keep their verdict"
requirement actually needs -- many records over one artifact, and several
over one artifact plus a few singletons over others -- and shows the floor
outcome is unchanged by dedup, which is the part of Acceptance #4 that is
checkable without a historical checkout.

No mutation/fuzz tool is declared for this repo, so this file is the
required executable abuse/boundary cases (5 here, floor is 3).
"""
from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[5]
sys.path.insert(0, str(REPO_ROOT / "loom-code" / "scripts"))

import loom_checker  # noqa: E402 -- the module under attack


def git(repo: Path, *args: str) -> str:
    return subprocess.run(
        ["git", "-C", str(repo), *args], capture_output=True, text=True, check=True
    ).stdout.strip()


def _init_branch_repo(tmp_path: Path) -> Path:
    repo = tmp_path / "repo"
    repo.mkdir()
    git(repo, "init", "-q", "-b", "main")
    git(repo, "config", "user.email", "t@example.com")
    git(repo, "config", "user.name", "T")
    (repo / "seed.txt").write_text("seed\n", encoding="utf-8")
    git(repo, "add", "seed.txt")
    git(repo, "commit", "-q", "-m", "seed")
    git(repo, "checkout", "-q", "-b", "work")
    return repo


def _commit_counting_artifact(repo: Path, rel: str, counter: Path, *, exit_code: int = 0) -> None:
    """A committed `.py` artifact that appends one line to `counter`
    (living OUTSIDE the repo) every time it actually runs, then exits
    `exit_code`. artifact_types() types any top-level path `code` via the
    manifest's trailing `**` rule, which is what makes this a `kind:
    adversarial`-eligible change in the first place."""
    path = repo / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        "import pathlib\n"
        f"pathlib.Path({str(counter)!r}).open('a').write('1\\n')\n"
        f"raise SystemExit({exit_code})\n",
        encoding="utf-8",
    )


def _records(artifact: str, sha: str, count: int) -> list[dict]:
    return [
        {
            "kind": "adversarial",
            "command": f"python3 {artifact}",
            "sha": sha,
            "result": "pass",
            "artifact": artifact,
        }
        for _ in range(count)
    ]


def _count(path: Path) -> int:
    return path.read_text(encoding="utf-8").count("1") if path.is_file() else 0


# --- (1) same artifact, N records: RED until W0-04 (executes N times today) -


@pytest.mark.xfail(
    strict=True,
    reason=(
        "RED until W0-04: check_probes_adversarial() runs the artifact once per "
        "record, not once per distinct artifact. Observed today (verified live): "
        "4 records naming the same file -> 4 real subprocess runs (expected 1 "
        "after the fix)."
    ),
)
def test_same_artifact_referenced_by_four_records_runs_once_after_fix(
    tmp_path: Path,
) -> None:
    repo = _init_branch_repo(tmp_path)
    counter = tmp_path / "counter.txt"
    _commit_counting_artifact(repo, "probe.py", counter)
    git(repo, "add", "probe.py")
    git(repo, "commit", "-q", "-m", "feat: probe")
    sha = git(repo, "rev-parse", "HEAD")

    review = {"probes": _records("probe.py", sha, 4)}
    failures = loom_checker.check_probes_adversarial(repo, review, sha)
    assert failures == []  # floor (3) met either way -- not what this case tests
    assert _count(counter) == 1


# --- (2) failing artifact, 3 records: message repeats N times today --------


@pytest.mark.xfail(
    strict=True,
    reason=(
        "RED until W0-04: a failing artifact named by N records produces N "
        "copies of the same failure text today (verified live: 3 records -> the "
        "phrase 'exited 1 when the checker ran it' appears 3 times in one "
        "message); all N records should be marked unusable from a single "
        "execution and the message should appear once."
    ),
)
def test_failing_artifact_referenced_by_three_records_reports_message_once_after_fix(
    tmp_path: Path,
) -> None:
    repo = _init_branch_repo(tmp_path)
    counter = tmp_path / "counter.txt"
    _commit_counting_artifact(repo, "bad.py", counter, exit_code=1)
    git(repo, "add", "bad.py")
    git(repo, "commit", "-q", "-m", "feat: bad probe")
    sha = git(repo, "rev-parse", "HEAD")

    review = {"probes": _records("bad.py", sha, 3)}
    failures = loom_checker.check_probes_adversarial(repo, review, sha)
    assert len(failures) == 1
    rule, message = failures[0]
    assert rule == "push.probes-adversarial"
    needle = "exited 1 when the checker ran it"
    assert message.count(needle) == 1


# --- (3) two distinct artifacts, floor met with mixed record counts --------


def test_two_distinct_artifacts_each_pass_floor_met(tmp_path: Path) -> None:
    """Floor semantics unchanged by dedup: counted in RECORDS, not distinct
    files (plan risk note -- this is why #785's one-file-six-records shape
    must not become disqualified by a file-level floor). Two artifacts, two
    records each, all passing -> floor (3) is met and the change passes,
    both today and after W0-04."""
    repo = _init_branch_repo(tmp_path)
    counter = tmp_path / "counter.txt"
    _commit_counting_artifact(repo, "a.py", counter)
    _commit_counting_artifact(repo, "b.py", counter)
    git(repo, "add", "a.py", "b.py")
    git(repo, "commit", "-q", "-m", "feat: two probes")
    sha = git(repo, "rev-parse", "HEAD")

    review = {"probes": _records("a.py", sha, 2) + _records("b.py", sha, 2)}
    failures = loom_checker.check_probes_adversarial(repo, review, sha)
    assert failures == []
    # Both artifacts actually ran at least once, whatever the dedup count.
    assert _count(counter) >= 2


# --- (4) N records over ONE passing file already meets the floor -----------


def test_six_records_over_one_passing_file_meets_floor_both_today_and_after(
    tmp_path: Path,
) -> None:
    """Mirrors the #785-shaped precedent the plan cites ("一檔六筆"): a
    single artifact referenced by many records must satisfy the floor
    (3) on record count, not distinct-file count -- true before W0-04
    (today, by brute re-execution) and required to stay true after
    (by cached dedup)."""
    repo = _init_branch_repo(tmp_path)
    counter = tmp_path / "counter.txt"
    _commit_counting_artifact(repo, "solo.py", counter)
    git(repo, "add", "solo.py")
    git(repo, "commit", "-q", "-m", "feat: solo probe")
    sha = git(repo, "rev-parse", "HEAD")

    review = {"probes": _records("solo.py", sha, 6)}
    failures = loom_checker.check_probes_adversarial(repo, review, sha)
    assert failures == []


# --- (5) a record whose command doesn't name its artifact: always refused --


def test_command_not_naming_its_artifact_is_refused_regardless_of_dedup(
    tmp_path: Path,
) -> None:
    """`command_names_artifact` is a per-record parse check that happens
    before any grouping/execution could dedupe anything -- a record that
    fails it must stay refused whether or not W0-04's grouping exists."""
    repo = _init_branch_repo(tmp_path)
    counter = tmp_path / "counter.txt"
    _commit_counting_artifact(repo, "probe.py", counter)
    other = repo / "other.py"
    other.write_text("raise SystemExit(0)\n", encoding="utf-8")
    git(repo, "add", "probe.py", "other.py")
    git(repo, "commit", "-q", "-m", "feat: probes")
    sha = git(repo, "rev-parse", "HEAD")

    records = [
        {
            "kind": "adversarial",
            # names "other.py" on the command line, but claims "probe.py"
            # as its artifact -- no argument of the command IS the artifact.
            "command": "python3 other.py",
            "sha": sha,
            "result": "pass",
            "artifact": "probe.py",
        }
        for _ in range(3)
    ]
    failures = loom_checker.check_probes_adversarial(repo, {"probes": records}, sha)
    assert len(failures) == 1
    rule, message = failures[0]
    assert rule == "push.probes-adversarial"
    assert "0 are usable" in message
    assert "passes its artifact probe.py to nothing" in message
