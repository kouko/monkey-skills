"""Wave-end:0 adversarial top-up for 2026-09-04-checker-seams.

Re-runs (via the package command) against the NOW-IMPLEMENTED W0-02/W0-03/
W0-04 code, and adds attacks the W0-01 adversary could not write because
the implementations did not exist yet. Each case is executed for real
against the actual `loom_checker.py` module/CLI at HEAD -- no mocking of
git topology or subprocess execution.

Findings recorded here are `xfail(strict=True)` with a `wave-end:0-NN`
tag; everything else is a floor case kept green to guard the behaviour
the finding sits next to.
"""
from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[5]
sys.path.insert(0, str(REPO_ROOT / "loom-code" / "scripts"))

import loom_checker  # noqa: E402 -- module under attack

CHECKER = REPO_ROOT / "loom-code" / "scripts" / "loom_checker.py"


def git(repo: Path, *args: str) -> str:
    return subprocess.run(
        ["git", "-C", str(repo), *args], capture_output=True, text=True, check=True
    ).stdout.strip()


def run_checker(*args: str, cwd: Path) -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, str(CHECKER), *args], capture_output=True, text=True, cwd=str(cwd)
    )


def blocked_rules(result: subprocess.CompletedProcess) -> set[str]:
    return {
        line.split(":", 1)[0].removeprefix("BLOCK ").strip()
        for line in result.stderr.splitlines()
        if line.startswith("BLOCK ")
    }


def _init_repo(tmp_path: Path, *, branch: str = "main") -> Path:
    repo = tmp_path / "repo"
    repo.mkdir()
    git(repo, "init", "-q", "-b", branch)
    git(repo, "config", "user.email", "t@example.com")
    git(repo, "config", "user.name", "T")
    (repo / "seed.txt").write_text("seed\n", encoding="utf-8")
    git(repo, "add", "seed.txt")
    git(repo, "commit", "-q", "-m", "seed")
    return repo


def _intent_relpath(change_id: str) -> str:
    return f"docs/loom/intent/{change_id}.md"


INTENT_TEXT = """# {title}
originator: kouko
kind: product
needs-design: yes — {reason}
status: confirmed {date}

## Problem
people cannot see something they need to see.

## Proposed outcome
show it to them plainly.

## Acceptance
1. it works.

## Constraints
- none

## Out of scope
- none

## Open questions
- none
"""


def _write_intent_on_branch(repo: Path, change_id: str, *, reason: str, commit_message: str) -> None:
    path = repo / _intent_relpath(change_id)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(INTENT_TEXT.format(title=change_id, reason=reason, date=change_id[:10]), encoding="utf-8")
    git(repo, "add", _intent_relpath(change_id))
    git(repo, "commit", "-q", "-m", commit_message)


# --- (1) FINDING: stale origin/main short-circuits the trunk candidate loop -


@pytest.mark.xfail(
    strict=True,
    reason="finding wave-end:0-01: _squash_note()'s REOPEN_TRUNK_CANDIDATES loop "
    "returns None as soon as the first EXISTING candidate fails the ancestor "
    "check, instead of trying the next candidate -- a stale origin/main "
    "falsely blocks a genuine squash commit that IS on local main.",
)
def test_stale_origin_main_falsely_blocks_squash_reachable_via_local_main(
    tmp_path: Path,
) -> None:
    """Acceptance #3: "分支上把 needs-design 改掉而 commit 訊息沒帶那行：照樣
    被擋" must NOT fire for a genuine squash commit that IS on the local
    trunk. `_squash_note()`'s candidate loop
    (`loom_checker.py` REOPEN_TRUNK_CANDIDATES = origin/main, main,
    origin/master, master) returns None as soon as the FIRST candidate that
    *exists* fails the ancestor check -- it never falls through to try the
    next candidate. A repo whose `origin/main` remote-tracking ref is stale
    (common: a shallow fetch, a fetch run before the merge, CI checking out
    a commit git hasn't fetched the latest origin/main for) has `origin/main`
    exist but NOT be an ancestor of the just-merged squash commit, even
    though local `main` (the real trunk here) IS an ancestor. The genuine
    squash commit is then wrongly BLOCKED by `intent.needs-design-reason` --
    a false positive on exactly the case Acceptance #3 says must pass.
    A failure of this case means: any workflow where `origin/main` is not
    freshly fetched (very common) can turn a legitimate squash-merged intent
    red for no correctable reason -- the author cannot fix their own commit
    message after the squash.
    """
    repo = _init_repo(tmp_path)
    change_id = "2099-04-01-stale-origin"
    git(repo, "checkout", "-q", "-b", "feature")
    _write_intent_on_branch(
        repo,
        change_id,
        reason="new page for the team to see something",
        commit_message=(
            f"docs(loom): intent {change_id} confirmed\n\n"
            "needs-design: yes — new page for the team to see something"
        ),
    )
    git(repo, "checkout", "-q", "main")
    # origin/main exists but is STALE: it points at seed, before the squash.
    git(repo, "update-ref", "refs/remotes/origin/main", "HEAD")
    git(repo, "merge", "--squash", "feature", "-q")
    git(repo, "commit", "-q", "-m", f"docs(loom): intent {change_id} confirmed (#12)")
    sha = git(repo, "rev-parse", "HEAD")
    # Confirm the attack's precondition: ancestor of local main, NOT of
    # stale origin/main.
    assert (
        subprocess.run(["git", "-C", str(repo), "merge-base", "--is-ancestor", sha, "main"]).returncode
        == 0
    )
    assert (
        subprocess.run(
            ["git", "-C", str(repo), "merge-base", "--is-ancestor", sha, "origin/main"]
        ).returncode
        != 0
    )
    result = run_checker("intent", _intent_relpath(change_id), cwd=repo)
    assert result.returncode == 0, (
        "finding wave-end:0-01: stale origin/main falsely blocked a squash commit "
        f"that IS reachable via local main; stderr={result.stderr}"
    )


# --- (2) floor: master-only trunk (no `main` at all) still recognizes squash -


def test_master_only_trunk_recognizes_squash_shape(tmp_path: Path) -> None:
    """Boundary the plan names explicitly ("trunk 為 master 不是 main"):
    REOPEN_TRUNK_CANDIDATES includes `master`/`origin/master` precisely for
    a repo whose default branch was never renamed. No `main` ref exists at
    all here, so the loop must reach the `master` candidate."""
    repo = _init_repo(tmp_path, branch="master")
    change_id = "2099-04-02-master-trunk"
    git(repo, "checkout", "-q", "-b", "feature")
    _write_intent_on_branch(
        repo,
        change_id,
        reason="new page for the team to see something",
        commit_message=(
            f"docs(loom): intent {change_id} confirmed\n\n"
            "needs-design: yes — new page for the team to see something"
        ),
    )
    git(repo, "checkout", "-q", "master")
    git(repo, "merge", "--squash", "feature", "-q")
    git(repo, "commit", "-q", "-m", f"docs(loom): intent {change_id} confirmed (#7)")
    assert (
        subprocess.run(["git", "-C", str(repo), "rev-parse", "--verify", "main^{commit}"]).returncode
        != 0
    )
    result = run_checker("intent", _intent_relpath(change_id), cwd=repo)
    assert result.returncode == 0, result.stderr


# --- (3) FINDING: artifact path spelled two ways bypasses the W0-04 dedup --


def _record(artifact: str, sha: str) -> dict:
    return {
        "kind": "adversarial",
        "command": f"python3 {artifact}",
        "sha": sha,
        "result": "pass",
        "artifact": artifact,
    }


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
    path = repo / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        "import pathlib\n"
        f"pathlib.Path({str(counter)!r}).open('a').write('1\\n')\n"
        f"raise SystemExit({exit_code})\n",
        encoding="utf-8",
    )


@pytest.mark.xfail(
    strict=True,
    reason="finding wave-end:0-02: check_probes_adversarial()'s pending dict is "
    "keyed on the raw un-normalized artifact string, so './probe.py' and "
    "'probe.py' -- which command_names_artifact() itself treats as the same "
    "file -- land in two different groups and the file is executed twice.",
)
def test_dotslash_vs_bare_artifact_string_bypasses_per_file_dedup(tmp_path: Path) -> None:
    """`command_names_artifact()` deliberately normalizes so `./x/y.py` and
    `x/y.py` both count as naming the same file (its own docstring says so
    verbatim). But `check_probes_adversarial()`'s dedup groups records with
    `pending.setdefault(artifact, [])` keyed on the RAW, un-normalized
    string. Two records for the identical physical file -- one spelled
    `probe.py`, one spelled `./probe.py` -- both pass every per-record
    check (git cat-file -e accepts both spellings; command_names_artifact
    accepts both) and land in two DIFFERENT dict keys, so the file is
    executed twice. That contradicts the rule's own stated invariant
    ("a file named by many records is attacked once and that one verdict
    is applied to every record naming it") and Acceptance #4's "同一探針檔
    被引用 N 筆時 push 只執行它一次". A failure of this case means the
    execution-count claim in `--list-rules` / the rule's docstring is not
    actually true for every spelling of the same path -- an agent (or a
    careless human) writing two records for one file with a stray `./`
    silently doubles the real subprocess cost the rule advertises it
    eliminated.
    """
    repo = _init_branch_repo(tmp_path)
    counter = tmp_path / "counter.txt"
    _commit_counting_artifact(repo, "probe.py", counter)
    git(repo, "add", "probe.py")
    git(repo, "commit", "-q", "-m", "feat: probe")
    sha = git(repo, "rev-parse", "HEAD")

    review = {
        "probes": [
            _record("probe.py", sha),
            _record("probe.py", sha),
            _record("./probe.py", sha),
        ]
    }
    failures = loom_checker.check_probes_adversarial(repo, review, sha)
    assert failures == []  # floor (3) met either way -- not what this asserts
    assert loom_checker.check_probes_adversarial.__doc__  # sanity: docstring exists
    assert (
        _count_lines(counter) == 1
    ), "finding wave-end:0-02: dedup ran the same physical file twice for two spellings of its path"


def _count_lines(path: Path) -> int:
    return path.read_text(encoding="utf-8").count("1") if path.is_file() else 0


# --- (4) floor: one artifact, mixed correct/wrong sha records -------------


def test_wrong_sha_record_stays_unusable_correct_sha_record_still_counts(
    tmp_path: Path,
) -> None:
    """Same artifact named by two records with DIFFERENT `sha` values, one
    matching the reviewed commit and one not (a stale or copy-pasted probe
    entry). The per-record sha check runs before any grouping, so the
    wrong-sha record must be refused (and reported) on its own, while the
    correct-sha records still make the file run and count toward the
    floor."""
    repo = _init_branch_repo(tmp_path)
    counter = tmp_path / "counter.txt"
    _commit_counting_artifact(repo, "probe.py", counter)
    git(repo, "add", "probe.py")
    git(repo, "commit", "-q", "-m", "feat: probe")
    sha = git(repo, "rev-parse", "HEAD")
    wrong_sha = "0" * 40

    review = {
        "probes": [
            _record("probe.py", sha),
            _record("probe.py", sha),
            _record("probe.py", sha),
            _record("probe.py", wrong_sha),
        ]
    }
    failures = loom_checker.check_probes_adversarial(repo, review, sha)
    assert failures == []
    assert _count_lines(counter) == 1  # one distinct-artifact execution


# --- (5) floor: timeout on a multiply-referenced artifact reports once ----


def test_timeout_reported_once_for_artifact_referenced_by_several_records(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch,
) -> None:
    """A hung artifact referenced by several records must fail the gate
    with ONE `did not finish within Ns` reason, not one per record --
    otherwise a slow but real case would flood the block message N times
    for what is a single execution event."""
    repo = _init_branch_repo(tmp_path)
    path = repo / "hang.py"
    path.write_text("import time\ntime.sleep(9999)\n", encoding="utf-8")
    git(repo, "add", "hang.py")
    git(repo, "commit", "-q", "-m", "feat: hang probe")
    sha = git(repo, "rev-parse", "HEAD")

    real_run = subprocess.run

    def fake_run(argv, *args, **kwargs):  # noqa: ANN001
        # Only the artifact-execution call (argv[0] is the artifact's own
        # interpreter, not "git") is made to hang; git plumbing calls the
        # checker itself issues along the way must keep working.
        head = argv[0] if argv else b""
        if isinstance(head, bytes):
            head = head.decode("utf-8", "surrogateescape")
        if head != "git":
            raise subprocess.TimeoutExpired(cmd=argv, timeout=kwargs.get("timeout"))
        return real_run(argv, *args, **kwargs)

    monkeypatch.setattr(loom_checker.subprocess, "run", fake_run)

    review = {"probes": [_record("hang.py", sha) for _ in range(4)]}
    failures = loom_checker.check_probes_adversarial(repo, review, sha)
    assert len(failures) == 1
    rule, message = failures[0]
    assert rule == "push.probes-adversarial"
    assert message.count("did not finish within") == 1
