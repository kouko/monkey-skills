"""Adversarial cases against the rebuilt test fixtures.

Six cases, every one executable and run by `finalize-review`:

1. `test_shell_fixture_object_id_is_pinned` — the frozen oracle. The shell
   builder's 2,000-commit fixture must hash to the object id the pre-change
   per-commit builder produced. A commit id covers every message byte, the
   tree, both identities and both dates, so any silent drift in the fixture
   flips it. This is the case that would have caught the local-time epoch
   bug the rewrite nearly shipped.
2. `test_cleanup_whitespace_matches_real_git` — `conftest.py` reimplements
   git's `--cleanup=whitespace`, which `commit -F -` applies and
   `fast-import` does not. Hostile whitespace bodies go through both paths
   and the stored message bytes must match, byte for byte.
3. `test_hostile_body_bytes_survive_the_stream` — a body whose lines read as
   fast-import commands (`commit refs/heads/main`, `data 5`, `from`) plus a
   lone CR and a UTF-8 multi-byte run must land verbatim. `data <n>` is
   length-prefixed, so it should be safe; this proves it rather than
   assuming it.
4. `test_forward_citation_fails_loudly` — a spec citing a LATER spec can
   never resolve. The builder must raise, not spin or emit a fixture with an
   empty supersession body.
5. `test_supersedes_index_without_body_from_sha_fails_loudly` — the same
   contract for a half-declared citation.
6. `test_empty_spec_list_leaves_head_unborn` — the zero boundary: no
   commits, no crash, and no ref invented.

The file loads `conftest.py` by path rather than relying on pytest fixture
resolution: nine package-less `conftest.py` files share the bare module name
`conftest` in this repo, and these cases must run from anywhere.
"""
from __future__ import annotations

import importlib.util
import subprocess
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[5]
SCRIPTS = REPO / "loom-workflow/skills/git-memory/scripts"
PERF_SH = REPO / "loom-workflow/tests/test-memory-grep-perf.sh"

# The object id the PRE-change per-commit builder produced for
# build_perf_repo <dir> 2000 300 20, measured on the branch base 89cf5d224.
PINNED_PERF_HEAD = "6ee5166a1f445bdf9708c3adbb6825bf806fb011"


def _load_conftest():
    spec = importlib.util.spec_from_file_location(
        "git_memory_bulk_conftest", SCRIPTS / "conftest.py"
    )
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


BULK = _load_conftest()


def _init_repo(path: Path) -> None:
    subprocess.run(["git", "init", "-q", str(path)], check=True)
    subprocess.run(["git", "-C", str(path), "symbolic-ref", "HEAD", "refs/heads/main"], check=True)
    for key, value in (
        ("user.email", "fixture@example.com"),
        ("user.name", "Fixture Bot"),
        ("commit.gpgsign", "false"),
    ):
        subprocess.run(["git", "-C", str(path), "config", key, value], check=True)


def _message_bytes(repo: Path, ref: str = "HEAD") -> bytes:
    return subprocess.run(
        ["git", "-C", str(repo), "log", "-1", "--format=%B", ref],
        capture_output=True, check=True,
    ).stdout


def test_shell_fixture_object_id_is_pinned(tmp_path):
    """The committed shell builder must reproduce the pre-change object id."""
    target = tmp_path / "perf"
    script = (
        f"set -eu\n"
        f'eval "$(sed -n \'/^build_perf_repo() {{/,/^}}/p\' {PERF_SH!s})"\n'
        f"build_perf_repo {target!s} 2000 300 20\n"
    )
    subprocess.run(["bash", "-c", script], check=True)
    head = subprocess.run(
        ["git", "-C", str(target), "rev-parse", "HEAD"],
        capture_output=True, text=True, check=True,
    ).stdout.strip()
    count = subprocess.run(
        ["git", "-C", str(target), "rev-list", "--count", "HEAD"],
        capture_output=True, text=True, check=True,
    ).stdout.strip()
    assert count == "2000", f"expected 2000 commits, got {count}"
    assert head == PINNED_PERF_HEAD, (
        "the shell fixture no longer matches the object id the per-commit "
        f"builder produced: {head} != {PINNED_PERF_HEAD}"
    )
    tracked = subprocess.run(
        ["git", "-C", str(target), "status", "--porcelain"],
        capture_output=True, text=True, check=True,
    ).stdout
    assert tracked == "", f"fixture worktree not populated cleanly: {tracked!r}"
    assert (target / "content.txt").is_file(), "content.txt missing; --path cases would match nothing"


@pytest.mark.parametrize(
    "body",
    [
        b"Decision: trailing spaces   \nand more   \n",
        b"Decision: trailing blank lines\n\n\n\n",
        b"Decision: leading blanks\n",
        b"\n\nDecision: body opening with blank lines\n",
        b"Decision: no final newline",
        b"Decision: interior   blank\n\n\n\nlines kept\n",
        b"   \n",
    ],
)
def test_cleanup_whitespace_matches_real_git(tmp_path, body):
    """The reimplemented cleanup must agree with `git commit -F -`."""
    subject = "chore: whitespace oracle"
    real = tmp_path / f"real-{abs(hash(body))}"
    real.mkdir()
    _init_repo(real)
    (real / "f.txt").write_text("x\n")
    subprocess.run(["git", "-C", str(real), "add", "f.txt"], check=True)
    subprocess.run(
        ["git", "-C", str(real), "commit", "-q", "-F", "-"],
        input=subject.encode() + b"\n\n" + body,
        check=True,
        env={"GIT_AUTHOR_DATE": "2020-01-01T00:00:00+0000",
             "GIT_COMMITTER_DATE": "2020-01-01T00:00:00+0000",
             "PATH": __import__("os").environ["PATH"],
             "HOME": str(tmp_path)},
    )

    imported = tmp_path / f"imported-{abs(hash(body))}"
    imported.mkdir()
    _init_repo(imported)
    BULK.fast_import_commits(imported, [
        BULK.CommitSpec(date="2020-01-01", subject=subject, body=body, files={"f.txt": "x\n"}),
    ])

    assert _message_bytes(imported) == _message_bytes(real), (
        f"cleanup mismatch for {body!r}: "
        f"imported={_message_bytes(imported)!r} real={_message_bytes(real)!r}"
    )


def test_hostile_body_bytes_survive_the_stream(tmp_path):
    """Lines that read as fast-import commands must not be interpreted."""
    hostile = (
        b"Decision: hostile\n"
        b"commit refs/heads/main\n"
        b"mark :99\n"
        b"data 5\n"
        b"from refs/heads/main^0\n"
        b"M 100644 inline evil.txt\n"
        b"done\n"
        b"lone carriage return ->\rback\n"
        b"multi-byte: \xe6\xb8\xac\xe8\xa9\xa6 \xf0\x9f\x94\xa5\n"
    )
    repo = tmp_path / "hostile"
    repo.mkdir()
    _init_repo(repo)
    BULK.fast_import_commits(repo, [
        BULK.CommitSpec(date="2021-02-03", subject="chore: hostile body",
                        body=hostile, files={"f.txt": "x\n"}),
    ])
    count = subprocess.run(
        ["git", "-C", str(repo), "rev-list", "--count", "HEAD"],
        capture_output=True, text=True, check=True,
    ).stdout.strip()
    assert count == "1", f"the hostile body created {count} commits, expected 1"
    assert not (repo / "evil.txt").exists(), "an inline command inside the body created a file"
    stored = _message_bytes(repo)
    for needle in (b"commit refs/heads/main", b"data 5", b"done",
                   b"\rback", b"\xe6\xb8\xac\xe8\xa9\xa6", b"\xf0\x9f\x94\xa5"):
        assert needle in stored, f"{needle!r} did not round-trip; stored={stored!r}"


def test_forward_citation_fails_loudly(tmp_path):
    """A spec citing a later spec can never resolve; the builder must raise."""
    repo = tmp_path / "forward"
    repo.mkdir()
    _init_repo(repo)
    specs = [
        BULK.CommitSpec(date="2020-01-01", subject="chore: cites the future",
                        supersedes_index=1, body_from_sha=lambda s: b"Supersedes: " + s.encode(),
                        files={"f.txt": "a\n"}),
        BULK.CommitSpec(date="2020-01-02", subject="chore: later",
                        body=b"Decision: later\n", files={"f.txt": "b\n"}),
    ]
    with pytest.raises(AssertionError, match="unresolvable supersession"):
        BULK.fast_import_commits(repo, specs)


def test_supersedes_index_without_body_from_sha_fails_loudly(tmp_path):
    """A half-declared citation must raise rather than emit an empty body."""
    repo = tmp_path / "half"
    repo.mkdir()
    _init_repo(repo)
    specs = [
        BULK.CommitSpec(date="2020-01-01", subject="chore: base",
                        body=b"Decision: base\n", files={"f.txt": "a\n"}),
        BULK.CommitSpec(date="2020-01-02", subject="chore: half-declared",
                        supersedes_index=0, files={"f.txt": "b\n"}),
    ]
    with pytest.raises(AssertionError, match="body_from_sha"):
        BULK.fast_import_commits(repo, specs)


def test_empty_spec_list_leaves_head_unborn(tmp_path):
    """The zero boundary: no commits, no crash, no invented ref."""
    repo = tmp_path / "empty"
    repo.mkdir()
    _init_repo(repo)
    BULK.fast_import_commits(repo, [])
    resolved = subprocess.run(
        ["git", "-C", str(repo), "rev-parse", "--verify", "--quiet", "refs/heads/main"],
        capture_output=True, text=True,
    )
    assert resolved.returncode != 0, (
        f"an empty spec list created a ref at {resolved.stdout.strip()}"
    )
