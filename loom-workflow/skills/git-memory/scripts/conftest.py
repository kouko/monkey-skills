"""Keep the skill directory flat by suppressing pytest's incidental subdirs.

Why this exists: `.claude/hooks/validate-skill-folder-structure.sh` (PostToolUse
on Write|Edit) blocks any nested subdir under a skill folder. Pytest defaults
generate `__pycache__/` adjacent to test files. `sys.dont_write_bytecode = True`
catches the bulk of bytecode but conftest.py's *own* bytecode is written before
this line runs — the chicken-and-egg case. `pytest_sessionfinish` mops up the
leftover after each run, so the next Claude Write/Edit sees a clean tree and the
hook stays green.

Paired with `pytest.ini` in the same dir, which redirects `.pytest_cache/` to
/tmp for the same reason. Byte-identical convention to
loom-workflow/skills/distill-sessions/scripts/conftest.py.

This file also hosts `fast_import_commits` (exposed to the probe modules via
the session-scoped `bulk_history` fixture), the shared bulk fixture builder
that replaces per-commit `git commit` spawning in the two large probe
fixtures. It is a fixture rather than a module-level import on purpose:
`pytest.ini` here sets no `importmode`, so the default `prepend` mode imports
every package-less `conftest.py` in the repo under the bare module name
`conftest` — nine of them exist, so `import conftest` from a test module
would resolve to whichever one landed in `sys.modules` first. Requesting it
as a fixture is resolved by pytest against *this* directory's conftest, and
therefore works identically whether one probe file or the whole directory is
collected.
"""

import calendar
import shutil
import subprocess
import sys
import time
from dataclasses import dataclass
from pathlib import Path
from types import SimpleNamespace
from typing import Callable, Mapping

import pytest

sys.dont_write_bytecode = True


def pytest_sessionfinish(session, exitstatus):  # noqa: ARG001  (pytest signature)
    cache = Path(__file__).parent / "__pycache__"
    if cache.is_dir():
        shutil.rmtree(cache, ignore_errors=True)


# ─── shared bulk fixture builder ────────────────────────────────────
#
# The two big probe fixtures (`_build_perf_repo` in
# test_probes_memory_grep_single_pass.py, `_build_records_repo` in
# test_probes_memory_grep_render.py) used to spawn three `git` processes per
# commit, which cost ~18s of the group's ~28s. `git fast-import` writes the
# whole history in one process instead.
#
# The one thing fast-import cannot do in a single pass: a `Supersedes:`
# trailer cites the sha of an EARLIER commit, and a commit's sha is only
# known once it has been written. So the stream is split into waves — a wave
# ends just before the first commit whose cited sha is still unknown, the
# wave is imported with `--export-marks`, the marks file yields the shas, and
# the next wave continues on the same ref. A supersession chain therefore
# costs one process per link rather than one per commit (the 200-commit perf
# fixture needs four).
#
# Grounding for the marks behaviour this relies on: git-fast-import(1),
# `--export-marks=<file>` (https://git-scm.com/docs/git-fast-import) — the
# option "dumps the internal marks table to <file> when complete", i.e. the
# marks defined during *that* run. Because no wave passes `--import-marks`,
# each wave's marks file holds only its own commits, and the `mark :<n>`
# numbering (spec index + 1) is what maps a line back to its spec. The file
# is therefore overwritten, not appended, on every wave — the wave loop reads
# it straight after the run that wrote it and accumulates into `resolved`
# itself.

DEFAULT_IDENTITY = "Fixture Bot <fixture@example.com>"


@dataclass(frozen=True)
class CommitSpec:
    """One commit to import.

    `date` is an ISO day (YYYY-MM-DD), committed at 00:00:00 +0000 — the same
    instant the per-commit helpers pin via GIT_AUTHOR_DATE/GIT_COMMITTER_DATE.
    `subject` is str; `body` is raw bytes so a hostile byte sequence never
    round-trips through a shell argument. `files` maps a path (relative to the
    repo root) to its text content; an empty/omitted mapping leaves the parent
    tree untouched, which is what `git commit --allow-empty` with nothing
    staged produces.

    When the body must cite an earlier commit's sha, leave `body` None and set
    `supersedes_index` (the index of that earlier spec in the same list)
    together with `body_from_sha`, which is called with the resolved full sha.
    """

    date: str
    subject: str
    body: bytes | None = None
    files: Mapping[str, str] | None = None
    supersedes_index: int | None = None
    body_from_sha: Callable[[str], bytes] | None = None


def _epoch_utc(date: str) -> int:
    """Seconds since the epoch for `<date>T00:00:00+0000`."""
    return calendar.timegm(time.strptime(date, "%Y-%m-%d"))


def _cleanup_whitespace(msg: bytes) -> bytes:
    """Reproduce git's default `--cleanup=whitespace` for `commit -F -`.

    fast-import stores the `data` payload verbatim, while `git commit -F -`
    first strips trailing whitespace from each line, drops leading and
    trailing empty lines, collapses runs of empty lines, and terminates the
    message with a newline. Applying it here is what keeps a fast-imported
    commit byte-identical to the same commit made with the per-commit helper.

    "Whitespace" here is git's own set, not Python's: git strips only space,
    tab, CR and LF (its `sane_isspace` excludes vertical tab 0x0b and form
    feed 0x0c, which Python's argument-less `bytes.rstrip()` would strip),
    so this function strips exactly `b" \\t\\r\\n"` and leaves 0x0b/0x0c in
    place the way git does. Equivalence is claimed for that set only.
    """
    lines = [line.rstrip(b" \t\r\n") for line in msg.split(b"\n")]
    out: list[bytes] = []
    for line in lines:
        if not line and (not out or not out[-1]):
            continue
        out.append(line)
    while out and not out[-1]:
        out.pop()
    if not out:
        return b""
    return b"\n".join(out) + b"\n"


def _commit_block(
    spec: CommitSpec,
    index: int,
    branch: str,
    identity: str,
    body: bytes | None,
    emit_from: bool,
) -> bytes:
    """One `commit` command in fast-import stream syntax.

    Field order is fixed by fast-import's grammar — git-fast-import(1),
    "commit" (https://git-scm.com/docs/git-fast-import#_commit): `commit
    <ref>`, then optional `mark`, `original-oid`, `author`, then the
    required `committer`, then `data`, then the optional `from`/`merge`,
    then the filemodify and friends. The `data` command's trailing LF is
    optional but recommended — that sentence lives in its own section,
    git-fast-import(1), "data"
    (https://git-scm.com/docs/git-fast-import#_data), not in "commit".
    This emitter omits that LF, so the next command's own line starts
    immediately after the payload — which is why a message that already
    ends in LF must not gain a second one here.
    """
    msg = spec.subject.encode()
    if body:
        msg += b"\n\n" + body
    msg = _cleanup_whitespace(msg)
    stamp = f"{identity} {_epoch_utc(spec.date)} +0000"
    block = (
        f"commit {branch}\n"
        f"mark :{index + 1}\n"
        f"author {stamp}\n"
        f"committer {stamp}\n"
        f"data {len(msg)}\n"
    ).encode() + msg
    if emit_from:
        block += f"from {branch}^0\n".encode()
    for name, content in (spec.files or {}).items():
        payload = content.encode()
        block += f"M 100644 inline {name}\ndata {len(payload)}\n".encode() + payload + b"\n"
    return block


def fast_import_commits(
    repo: Path,
    specs: list[CommitSpec],
    *,
    branch: str = "refs/heads/main",
    identity: str = DEFAULT_IDENTITY,
) -> list[str]:
    """Import `specs` into an already-initialised `repo` and return their
    full shas, indexed like `specs`.

    The repo must already exist with HEAD pointing at `branch` (the probe
    modules' own `_init_repo` does that, and also pins core.abbrev=7 and
    commit.gpgsign=false, which this function deliberately does not touch).
    The worktree is populated by a final hard reset, so a caller can read the
    tracked files afterwards exactly as it could after a `git commit`.

    An empty `specs` is a clean no-op: it returns no shas, runs no git, and
    leaves `branch` unborn. Without this guard the wave loop is skipped but
    the final hard reset still runs and dies on `fatal: ambiguous argument
    'refs/heads/main'`, turning "nothing to import" into a confusing crash.
    """
    if not specs:
        return []

    resolved: dict[int, str] = {}
    marks_path = repo / ".git" / "fixture-fast-import-marks"
    index = 0
    first_wave = True

    while index < len(specs):
        wave: list[bytes] = []
        wave_start = index
        while index < len(specs):
            spec = specs[index]
            body = spec.body
            if spec.supersedes_index is not None:
                target = resolved.get(spec.supersedes_index)
                if target is None:
                    # Its sha is written but not yet exported — end the wave
                    # here so the marks file can supply it to the next one.
                    break
                assert spec.body_from_sha is not None, (
                    f"spec {index} sets supersedes_index without body_from_sha"
                )
                body = spec.body_from_sha(target)
            wave.append(
                _commit_block(
                    spec,
                    index,
                    branch,
                    identity,
                    body,
                    emit_from=(index == wave_start and not first_wave),
                )
            )
            index += 1
        assert wave, f"no progress importing spec {index}: unresolvable supersession"

        # `--export-marks` writes only this run's marks (no `--import-marks`
        # anywhere here), so the file is read immediately below and its
        # contents accumulated into `resolved` — see the marks grounding in
        # this module's "shared bulk fixture builder" comment block.
        subprocess.run(
            ["git", "-C", str(repo), "fast-import", "--quiet", f"--export-marks={marks_path}"],
            input=b"".join(wave),
            check=True,
        )
        for line in marks_path.read_text().splitlines():
            mark, sha = line.split()
            resolved[int(mark[1:]) - 1] = sha
        first_wave = False

    subprocess.run(["git", "-C", str(repo), "reset", "-q", "--hard", branch], check=True)
    marks_path.unlink(missing_ok=True)
    return [resolved[i] for i in range(len(specs))]


def read_commit_shape(repo: Path) -> list[tuple[str, str]]:
    """Every commit on HEAD, oldest first, as (full sha, full message).

    One `git log` call — the oracle the rebuilt builders assert their own
    output against, so a fixture that silently drifts to the wrong record
    shape fails loudly at build time instead of quietly relaxing whatever
    the probe was meant to bind.
    """
    out = subprocess.run(
        ["git", "-C", str(repo), "log", "--reverse", "--format=%H%x1f%B%x1e"],
        capture_output=True, text=True, check=True,
    ).stdout
    records = []
    for chunk in out.split("\x1e"):
        chunk = chunk.strip("\n")
        if not chunk:
            continue
        sha, _, message = chunk.partition("\x1f")
        records.append((sha, message))
    return records


@pytest.fixture(scope="session")
def bulk_history():
    """The three pieces above, handed to a probe module as one fixture.

    `.spec` is CommitSpec, `.build` is fast_import_commits, `.read_shape` is
    read_commit_shape. See this module's docstring for why the probes take
    these as a fixture instead of importing them.
    """
    return SimpleNamespace(
        spec=CommitSpec,
        build=fast_import_commits,
        read_shape=read_commit_shape,
    )
