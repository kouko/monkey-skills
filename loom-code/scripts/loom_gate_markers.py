"""Gate-marker CLI for loom-code's mechanical push gates.

The SDD orchestrator runs this to mint the markers that
`hooks/git-guard.py` (built in parallel on this branch) reads before
allowing a push. Marker contract (frozen; every field asserted by
`test_loom_gate_markers.py`):

Dir: `<git-dir>/loom/` resolved via `git rev-parse --git-dir` from
`--repo` (default cwd); created if missing. Exception: `origin-ledger.json`
(below) resolves its directory via `git rev-parse --git-common-dir`
instead (`resolve_common_marker_dir`) — see its own entry for why.

- `review-pass.json`  {"schema": 1, "branch", "head_sha", "verdict",
  "written_at", optional "base_sha"/"patch_id"} — written ONLY after the
  reviewer's verdict text passes schema validation (the audit's schema
  gate: a marker can only exist if a schema-valid verdict text exists).
  NEEDS_REVISION never mints a marker (exit 3); a malformed verdict
  never mints one either (exit 4, missing keys listed). Quote
  verification (below) does NOT gate this marker (Task 8) — the
  `origin_quote_tiers` field this marker used to carry is REMOVED; the
  origin ledger below supersedes it (a per-run snapshot restated the
  same population-mismatch defect the ledger exists to fix — see
  `docs/loom/backlog/2026-08-02-origin-quote-tier-counts-have-no-durable-ledger.md`).
- `verified.json`     {"schema": 1, "head_sha", "run_cmd", "exit_code",
  "output_tail", "written_at", optional "base_sha"/"patch_id"} — minted
  ONLY after `--run "<cmd>"` actually executes in `--repo` and exits 0;
  records the command run + a bounded tail of its captured output. This
  is auditability, NOT unforgeability: an agent can still pass
  `--run "true"` and mint a marker with no real suite behind it. The
  bar is raised from "type any string" to "a real command must run and
  exit 0, and is recorded" — local execution cannot cryptographically
  prove a genuine suite ran.
- `base_sha`/`patch_id` (both markers, both optional): merge-base with
  the default branch and `git diff base..HEAD | git patch-id --stable`
  at write time, recorded ONLY when every step resolves (default
  branch found, merge-base succeeds, diff+patch-id subprocesses
  succeed, output non-empty). Any failure omits BOTH fields — never a
  partial pair — so `hooks/git-guard.py` falls back to strict
  `head_sha` equality. Lets a message-only amend or a
  content-preserving rebase keep passing the push gate without a
  fresh review (see `compute_patch_id`).
- `waiver.json`       {"schema": 1, "scope": "push", "reason",
  "written_at"} — requires a real justification (>= 10 chars) and
  shouts on stderr that the review gate is being bypassed one-shot.
- `origin-ledger.json` {"schema": 1, "branches": {<branch>: [{"round",
  "verdict", "head_sha", "written_at", "findings": [{"arm", "dimension",
  "origin_raw", "quote_status"}, ...]}, ...]}} — append-only, never
  reset, written on EVERY `review-pass` invocation (including
  NEEDS_REVISION and schema-failure paths, both of which mint no
  `review-pass.json`) so the sample of recorded findings is never
  biased by which rounds happened to pass (see `_append_origin_ledger`).
  Its directory is resolved via `git rev-parse --git-common-dir`, NOT
  `--git-dir` like the three markers above (`resolve_common_marker_dir`)
  — every `git worktree` checkout of a repo shares one git-common-dir,
  so a round run from a worktree (the normal case this plugin's
  `using-git-worktrees` skill exists for) lands in the SAME ledger the
  main checkout reads, and `git worktree remove` cannot delete it (a
  worktree's own `--git-dir` is a private
  `<main>/.git/worktrees/<name>/` that DOES vanish with `remove` — the
  three per-checkout markers correctly keep using it; only the ledger
  needs the shared directory). The read-modify-write is held under an
  exclusive `fcntl.flock` on a dedicated `origin-ledger.json.lock` file
  (`_ledger_lock`) — concurrent `review-pass` invocations from separate
  worktrees are the normal case this ledger's shared directory exists
  for, and an unlocked read-modify-write silently loses every
  concurrent round but one (whole-branch review finding 1, reproduced
  live: 8 concurrent processes recorded only 2 of 8 rounds). Lock
  contention beyond 10s degrades through the same swallow-and-report
  path as any other write failure rather than blocking forever. A write
  failure here is reported on stderr and swallowed — it never changes
  the exit code or blocks `review-pass.json` (unlike every other marker
  above, whose write failures ARE fatal). Five corrupt-ledger shapes are
  recovered, not silently dropped forever (`_load_or_recover_ledger`):
  unparseable JSON, a directory sitting at the ledger path, and three
  valid-JSON-but-wrong-shape variants (non-dict top level, non-dict
  `branches`, a non-list per-branch value) — each is moved aside as
  `origin-ledger.json.corrupt-<UTC timestamp>` and a fresh ledger
  starts, both reported on stderr, so no single corruption shape can
  bias every future round to empty (see `_append_origin_ledger`).
  `quote_status`
  (Task 8) is a REAL verification result, computed on every round (even
  NEEDS_REVISION ones — quote verification no longer only runs on a
  round that already made it past the mint gate): `"absent"` (no
  `origin:` line), `"none"` (the literal value `none`), `"duplicate"`
  (two or more `origin:` lines in the block — also grammar-refused, see
  `_finding_problems`, but distinct from `"absent"`: that label means no
  `origin:` line existed at all, which is false here — neither of the
  two quotes is kept since which one was intended is ambiguous, so
  `origin_raw` is `null`), `"malformed"`
  (a single `origin:` line present but not grammar-valid — the round refuses
  on that ground regardless, see `_finding_problems`), `"verified-exact"`
  / `"verified-normalised"` (the quote matched the committed file at
  that tier), or `"unverified-<reason>"` for the five ways a
  grammar-valid quote can fail to verify — `sha-unresolvable`,
  `file-absent`, `not-a-file`, `undecodable-blob` (all four named after
  `_show_committed_file`'s failure kinds) and `quote-absent` (the file
  read fine but never contained the quote). None of the
  `unverified-<reason>` outcomes block the mint (see `_finding_quote_status`).

Exit codes: 0 marker written; 2 not a git repo; 3 NEEDS_REVISION
verdict; 4 malformed/nonconforming input. Writes are atomic
(tmp file + os.replace); existing markers are overwritten silently
(latest wins) — except `origin-ledger.json`, which is read-modify-write
appended, never overwritten wholesale.

`validate --verdict-file <path> [--suite-line "<text>"]` is a
dry-run of the exact same schema checks, but reports EVERY violation
in one pass instead of exiting on the first (today's writers exit-4
on the first problem, forcing a fix/rerun/fix retry loop). Writes
nothing; takes no `--repo` (no marker write, no HEAD resolution
needed). Exit 0 when clean, 4 when any violation is found.

Stdlib only.
"""
from __future__ import annotations

import argparse
import contextlib
import errno
import json
import os
import re
import subprocess
import sys
import tempfile
import time
import unicodedata
from datetime import datetime, timezone
from pathlib import Path

try:
    import fcntl
except ImportError:  # pragma: no cover - fcntl is POSIX-only; a host
    # without it must not lose `validate`/`waiver`/`verified` (none of
    # which touch the ledger) just because the ledger's locking helper
    # imports a module those subcommands never call. `_ledger_lock`
    # checks this sentinel and degrades to an unlocked append instead.
    fcntl = None

ALLOWED_VERDICTS = {"PASS", "PASS_WITH_NOTES", "NEEDS_REVISION"}
MIN_WAIVER_REASON_CHARS = 10

# NOTE: value-capturing regexes use [^\S\n]* (horizontal whitespace),
# not \s*, after the colon — under re.M, \s* spans the newline and
# wrongly captures the NEXT line as the value of an empty key.
_KEY_RE = {
    "standards_version": re.compile(
        r"^\s*standards_version:[^\S\n]*(\S.*)$", re.M
    ),
    "verdict": re.compile(r"^\s*verdict:[^\S\n]*([A-Z_]+)[^\S\n]*$", re.M),
    "dimension_scores": re.compile(r"^\s*dimension_scores:", re.M),
}
_FINDING_RE = re.compile(r"^\s*-\s*severity\s*:")
_WHERE_RE = re.compile(r"^\s*where\s*:[^\S\n]*(\S.*)$")
_DIMENSION_RE = re.compile(r"^\s*dimension\s*:[^\S\n]*(.*)$")
_ORIGIN_RE = re.compile(r"^\s*origin\s*:[^\S\n]*(.*)$")
_INDENT_RE = re.compile(r"^[ \t]*")

# §Pinned dimension partition (verified disjoint 2026-08-02). A finding
# whose `dimension:` both parses and falls in the docs-arm set is
# exempt from `origin:`; everything else — code-arm, unrecognized, or
# unparseable (absent/empty) — requires it (fail closed, see
# `_origin_required`).
_CODE_ARM_DIMENSIONS = {
    "security", "architecture", "correctness", "naming", "tests",
    "refactoring", "cross-task-coherence", "external-surface-grounding",
    "principles-conformance", "deliberate-simplification",
}
_DOCS_ARM_DIMENSIONS = {
    "omission", "ambiguity", "inconsistency", "incorrect-fact",
    "missing-population",
}


def _check_arm_disjoint(code_arm: set[str], docs_arm: set[str]) -> None:
    """Raise if `code_arm` and `docs_arm` share any dimension name.

    Makes the pin's "verified disjoint" claim load-bearing rather than
    a comment: a future edit that lets a dimension into both sets would
    make `_origin_required`'s docs-arm lookup ambiguous. Not an `assert`
    statement — those are stripped under `python -O`, and this check
    must still fire then."""
    overlap = code_arm & docs_arm
    if overlap:
        raise AssertionError(
            "_CODE_ARM_DIMENSIONS and _DOCS_ARM_DIMENSIONS overlap on "
            f"{sorted(overlap)} — §Pinned dimension partition requires "
            "them disjoint"
        )


_check_arm_disjoint(_CODE_ARM_DIMENSIONS, _DOCS_ARM_DIMENSIONS)
_TOP_KEY_RE = re.compile(r"^\S+\s*:")
_PASSED_RE = re.compile(r"(\d+) passed")
# where: value counts as location-like if it has a path separator /
# extension dot, or is a bare commit SHA (reviewer output contract
# allows `where: <commit SHA>`).
_PATHLIKE_RE = re.compile(r"[/.]|\b[0-9a-f]{7,40}\b")
# Word-boundary so green "2 xfailed" summaries don't trip the filter
# while "3 failed" / "1 error" still do.
_SUITE_REJECT_RE = re.compile(r"\b(failed|errors?)\b")


def _git(repo: Path, *args: str) -> str | None:
    """Run git in `repo`; return stripped stdout, or None on any failure."""
    try:
        result = subprocess.run(
            ["git", "-C", str(repo), *args],
            capture_output=True,
            text=True,
        )
    except OSError:
        return None
    if result.returncode != 0:
        return None
    return result.stdout.strip()


_SHA_UNRESOLVABLE = "sha-unresolvable"
_FILE_ABSENT = "file-absent"
_NOT_A_FILE = "not-a-file"
_UNDECODABLE_BLOB = "undecodable-blob"


def _show_committed_file(
    repo: Path, head_sha: str, path: str
) -> tuple[str | None, str | None]:
    """Read `path` as it exists at `head_sha` in the git object store —
    NEVER the worktree (brief §Resolved Questions 1: an uncommitted edit
    must not be able to satisfy the quote check).

    Returns `(content, failure_kind)`: `failure_kind` is None on success,
    `_SHA_UNRESOLVABLE` when `head_sha` does not resolve to a commit,
    `_FILE_ABSENT` when `git cat-file -t <sha>:<path>` exits non-zero —
    which covers both "path genuinely absent at that sha" AND, when the
    linked commit object is NOT present in the local object store,
    "path is a submodule gitlink" (see the THIRD verified quirk below;
    the two are NOT distinguished by this helper in that state),
    `_NOT_A_FILE` when `cat-file -t` exits zero but reports a type
    other than `blob` — a directory (git tree) is one measured case,
    and a submodule gitlink whose linked commit object IS present in
    the local object store (type `commit`) is a second, also covered
    below — or `_UNDECODABLE_BLOB` when the blob is not valid UTF-8.

    Reuses `_git`'s subprocess invocation shape but NOT its collapse-to-
    `None` contract (Task 2 Reuse-adequacy) — GREEN needs these failure
    modes distinguishable. The sha is checked to resolve to a commit
    FIRST, independently of the file read: `git show <sha>:<path>` on an
    unresolvable sha can print a misleading "exists on disk, but not in"
    message (a verified git quirk — a 40-hex-char string that resolves
    to no object still gets treated as a treeish by `<rev>:<path>`
    parsing), so failure-kind is never inferred from that command's
    stderr text.

    A SECOND verified quirk, caught in code-quality review: `git show
    <sha>:<dir>` also exits 0 — it prints a git-generated tree listing
    (`tree <hash>:<dir>` followed by the directory's entries), not
    repository content. Without a type check, a quote naming any
    filename in that listing (or the literal word "tree") mints with no
    knowledge of any real document. `git cat-file -t <sha>:<path>` is
    checked and must report `blob` before `git show` ever runs, so a
    directory is refused as `_NOT_A_FILE` before its listing is read.

    A THIRD verified quirk, caught in code-quality review round 2 and
    CORRECTED in round 3 after a reviewer reproduced the opposite of an
    earlier, unconditional version of this paragraph: a submodule path
    (a gitlink, git tree entry mode 160000) classifies CONDITIONALLY on
    whether the linked commit object happens to be present in this
    repo's local object store — that is state, not a fixed property of
    gitlinks, and both states are real:

    - Object ABSENT locally (the common case — nobody has fetched the
      submodule into this repo): `git cat-file -t <sha>:<path>` exits
      128 ("could not get object info") instead of exiting 0 with a
      non-blob type, and `git show <sha>:<path>` fails outright too.
      Measured against a throwaway repo holding a gitlink whose target
      commit is never fetched (`git update-index --add --cacheinfo
      160000,<sub-sha>,mysub` then commit, object store otherwise
      lacking `<sub-sha>`): both commands fail outright rather than
      reporting a type or a listing. This lands in `_FILE_ABSENT`.
    - Object PRESENT locally (e.g. after `git fetch <path-to-submodule-
      repo> <branch>:refs/remotes/<name>/<branch>` pulls the linked
      commit into THIS repo's own object store — an ordinary fetch, no
      exotic config): `git cat-file -t <sha>:<path>` exits 0 and
      reports type `commit`, and `git show <sha>:<path>` exits 0 and
      prints that commit's log rather than failing. This lands in
      `_NOT_A_FILE`, the same branch a directory takes, just with type
      `commit` instead of `tree`. Exercised by a live test (grep
      `classifies_gitlink_with_object_present` in the test module).

    Either way this helper never returns real repository content for a
    gitlink, so no code path mints a quote from one — but the "does not
    exist" message the caller prints for `_FILE_ABSENT` is imprecise in
    the object-absent state (the path does exist, just not as a
    `<sha>:<path>`-resolvable object this helper can read), and this
    helper cannot tell "path genuinely absent" from "path is a
    submodule whose object is missing locally" apart in that state.

    SYMLINK POLICY (decided here, not left implicit): a symlink's git
    object type is ALSO `blob` — its content is the literal target path
    string, e.g. `../other.md`. This helper does not special-case that:
    `git cat-file -t` reports `blob`, so a symlink is read and matched
    like any other blob. This is a deliberate policy choice, not a gap
    the type check missed. The contract this helper serves is "verify
    the quote against `path`'s committed content at `head_sha`" — a
    symlink's committed content genuinely IS its target string, so
    matching against it is correct per that contract's letter, and
    distinguishing symlinks would need a second `ls-tree`/mode lookup
    for a case with no measured incidence in this repo's findings.
    """
    if _git(repo, "rev-parse", "--verify", "-q", f"{head_sha}^{{commit}}") is None:
        return None, _SHA_UNRESOLVABLE
    try:
        type_result = subprocess.run(
            ["git", "-C", str(repo), "cat-file", "-t", f"{head_sha}:{path}"],
            capture_output=True,
            text=True,
        )
    except OSError:
        return None, _SHA_UNRESOLVABLE
    if type_result.returncode != 0:
        return None, _FILE_ABSENT
    if type_result.stdout.strip() != "blob":
        return None, _NOT_A_FILE
    try:
        result = subprocess.run(
            ["git", "-C", str(repo), "show", f"{head_sha}:{path}"],
            capture_output=True,
        )
    except OSError:
        return None, _SHA_UNRESOLVABLE
    if result.returncode != 0:
        return None, _FILE_ABSENT
    try:
        content = result.stdout.decode("utf-8")
    except UnicodeDecodeError:
        return None, _UNDECODABLE_BLOB
    return content, None


def _default_branch_ref(repo: Path) -> str | None:
    """Best-effort default-branch ref for merge-base computation.

    Tries origin/HEAD's symbolic ref, then local `main`, then local
    `master`. Returns None when none resolve — callers then omit the
    patch-id fields entirely (fail-closed: the fallback never activates
    for that marker; strict head_sha equality remains the only path).
    """
    origin_head = _git(repo, "symbolic-ref", "-q", "refs/remotes/origin/HEAD")
    if origin_head:
        ref = origin_head.removeprefix("refs/remotes/")
        if _git(repo, "rev-parse", "--verify", "-q", ref) is not None:
            return ref
    for candidate in ("main", "master"):
        if _git(repo, "rev-parse", "--verify", "-q", candidate) is not None:
            return candidate
    return None


def compute_patch_id(repo: Path) -> tuple[str, str] | None:
    """(base_sha, patch_id) for merge-base(default-branch, HEAD)..HEAD.

    Returns None on ANY resolution/subprocess/parse failure — the two
    fields are then simply omitted from the marker (fail-closed: a
    missing pair means the patch-id fallback never activates; strict
    head_sha equality is the only path `git-guard.py` can take).
    """
    ref = _default_branch_ref(repo)
    if ref is None:
        return None
    base_sha = _git(repo, "merge-base", ref, "HEAD")
    if base_sha is None:
        return None
    try:
        diff = subprocess.run(
            ["git", "-C", str(repo), "diff", f"{base_sha}..HEAD"],
            capture_output=True,
            text=True,
        )
        if diff.returncode != 0:
            return None
        patch_id_result = subprocess.run(
            ["git", "-C", str(repo), "patch-id", "--stable"],
            input=diff.stdout,
            capture_output=True,
            text=True,
        )
    except OSError:
        return None
    if patch_id_result.returncode != 0 or not patch_id_result.stdout.strip():
        return None
    return base_sha, patch_id_result.stdout.split()[0]


def resolve_marker_dir(repo: Path) -> Path | None:
    """Return `<git-dir>/loom` for `repo`, or None if not a git repo."""
    git_dir = _git(repo, "rev-parse", "--git-dir")
    if git_dir is None:
        return None
    git_path = Path(git_dir)
    if not git_path.is_absolute():
        git_path = repo / git_path
    return git_path / "loom"


def resolve_common_marker_dir(repo: Path) -> Path | None:
    """Return `<git-common-dir>/loom` for `repo`, or None if not a git repo.

    Used ONLY for the origin ledger (`_append_origin_ledger`) — every
    other marker keeps using `resolve_marker_dir` (`--git-dir`), which is
    correct for them (per-checkout, must die with the checkout). The
    ledger's contract is the opposite: it must accumulate across every
    `git worktree` checkout of the same repo. `git rev-parse
    --git-common-dir` resolves to the ONE directory every worktree
    agrees on — verified empirically: from a worktree, `--git-dir` prints
    `<main>/.git/worktrees/<name>` (a private directory `git worktree
    remove` deletes outright) while `--git-common-dir` prints `<main>/.git`
    (absolute); from the main checkout itself both print `.git` (relative,
    identical) — so this function's behavior never regresses the
    non-worktree case, it only changes the worktree one."""
    git_common_dir = _git(repo, "rev-parse", "--git-common-dir")
    if git_common_dir is None:
        return None
    git_path = Path(git_common_dir)
    if not git_path.is_absolute():
        git_path = repo / git_path
    return git_path / "loom"


def _write_marker(marker_dir: Path, name: str, payload: dict) -> Path:
    """Atomically write `payload` as JSON to `marker_dir/name`; return path."""
    marker_dir.mkdir(parents=True, exist_ok=True)
    path = marker_dir / name
    fd, tmp = tempfile.mkstemp(dir=str(marker_dir), prefix=name, suffix=".tmp")
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            json.dump(payload, f, indent=2)
            f.write("\n")
        os.replace(tmp, path)
    finally:
        if os.path.exists(tmp):
            os.unlink(tmp)
    return path


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


_ORIGIN_LEDGER_FILENAME = "origin-ledger.json"
_LEDGER_LOCK_FILENAME = "origin-ledger.json.lock"
_LEDGER_LOCK_TIMEOUT_SECONDS = 10.0
_LEDGER_LOCK_POLL_SECONDS = 0.05


class _LedgerLockTimeout(Exception):
    """Raised by `_ledger_lock` when the exclusive lock is genuinely
    CONTENDED (another process holds it) and stays held past
    `_LEDGER_LOCK_TIMEOUT_SECONDS` — caught by `_append_origin_ledger`'s
    existing swallow-and-report `except Exception`, so contention
    degrades exactly like any other ledger-write failure (reported on
    stderr, mint proceeds regardless) instead of hanging the caller
    forever. NOT raised when locking is structurally impossible (see
    `_STRUCTURAL_LOCK_ERRNOS` and `_ledger_lock`'s fallback) — that case
    degrades immediately to an unlocked append instead of waiting out
    this timeout, since waiting cannot change a structural outcome."""


# Round-3 review finding A: errno values observed when `flock` itself is
# unsupported by the underlying filesystem (some NFS/CIFS/FUSE mounts) —
# NOT contention. Before this set existed, `_ledger_lock` treated every
# `OSError` from `flock()` identically to "someone else holds it", so a
# filesystem in this state stalled every single invocation for the full
# `_LEDGER_LOCK_TIMEOUT_SECONDS` and still lost the round afterward
# (measured: 10.2s stall per invocation). `ENOLCK` ("no locks available",
# the common NFSv3-without-lockd case), `ENOSYS`/`EOPNOTSUPP` (the
# operation is not implemented/supported at all) are recognized here and
# fall back to an unlocked append immediately — waiting cannot change a
# structural outcome. Genuine contention still raises `EAGAIN`/
# `EWOULDBLOCK` under `LOCK_NB`, which is NOT in this set and keeps
# polling/timing out exactly as before.
_STRUCTURAL_LOCK_ERRNOS = frozenset({errno.ENOLCK, errno.ENOSYS, errno.EOPNOTSUPP})


def _warn_ledger_lock_unavailable(lock_path: Path, reason: str) -> None:
    """One stderr line: the origin ledger append is proceeding WITHOUT its
    exclusive lock because acquiring it is structurally impossible here —
    NOT contention (`_ledger_lock`'s docstring covers the three observed
    shapes: a directory sitting at `lock_path`, a lock file this process
    cannot open/write, `fcntl` itself unavailable, or a filesystem that
    rejects `flock` outright). An unlocked append is strictly better than
    losing the round: locking is impossible in these environments
    regardless of how long a caller waits, so refusing to record would
    regress the ledger from "lossy under concurrency" (the pre-lock
    state) to "total loss always" — worse than shipping with no lock at
    all, and the inverse of this branch's own binding constraint
    (persistence, not enforcement)."""
    print(
        f"loom-gate-markers: origin ledger lock unavailable at {lock_path} "
        f"({reason}); appending to the ledger WITHOUT a lock instead of "
        "losing this round — see _ledger_lock's docstring.",
        file=sys.stderr,
    )


@contextlib.contextmanager
def _ledger_lock(ledger_dir: Path):
    """Hold an exclusive `fcntl.flock` on `<ledger_dir>/origin-ledger.json.lock`
    for the duration of the read-modify-write below — the real mutual
    exclusion whole-branch review found missing (finding 1): concurrent
    `review-pass` invocations from different worktrees (the ledger's whole
    reason for living under `--git-common-dir` — every worktree of a repo
    shares one) used to race an unlocked read-modify-write and silently
    lose every round but one. Reproduced live: 8 concurrent processes
    against one repo recorded only 2 of 8 rounds, all exiting 0, nothing
    on stderr. (Parameter renamed from `marker_dir` — round-3 review
    finding C: every OTHER marker's directory is `<git-dir>/loom`, but
    this ledger's directory is `<git-common-dir>/loom`
    (`resolve_common_marker_dir`) — a genuinely different directory, and
    the old shared name invited exactly the conflation this branch
    already fixed once.)

    A DEDICATED lock file, never the ledger file itself: locking the
    ledger file directly would mean a reader that opens it for its own
    `flock` attempt (rather than `flock`ing before ANY read) still races
    the writer's tmpfile+`os.replace` swap, and would conflate "I hold the
    lock" with "the ledger's bytes are mid-write" in a single fd's
    lifecycle. A separate file sidesteps both.

    Polls `LOCK_EX | LOCK_NB` in a loop rather than a blocking `flock` —
    a blocking call has no timeout on POSIX, so a wedged holder (crashed
    mid-critical-section, holding the fd) would hang every future caller
    forever. Beyond `_LEDGER_LOCK_TIMEOUT_SECONDS` this raises
    `_LedgerLockTimeout` for GENUINE contention (`EAGAIN`/`EWOULDBLOCK`),
    which the caller's existing swallow-and-report path handles like any
    other ledger-write failure — recording is allowed to be lost under a
    stuck lock (never silently, always on stderr), but the mint itself
    must never be blocked by it. One stderr line fires at the FIRST
    contended attempt (round-3 review 🟢) — before this, the wait was
    silent until it gave up, so a caller at 9s into a 10s wait had no way
    to distinguish "about to succeed" from "about to time out".

    Round-3 review finding A — acquiring the lock at all can be
    STRUCTURALLY impossible, a different failure class than contention:
    `fcntl` unavailable on this platform (see the module-level
    try/except import), a directory sitting at `lock_path`
    (`IsADirectoryError` from `open()`), a lock file this process cannot
    write (`PermissionError` from `open()`, e.g. another user's umask in
    a shared checkout), or a filesystem that rejects `flock` outright
    (`_STRUCTURAL_LOCK_ERRNOS`, e.g. NFS without a lock daemon). None of
    these can be waited out — the OLD behavior treated every one of them
    as contention (or, for `open()` failures, let the exception escape
    uncaught into the caller's blanket swallow, losing the round on
    EVERY future invocation too, since the directory/permission problem
    never self-heals). The fix: recognize each shape and fall back to an
    unlocked append with `_warn_ledger_lock_unavailable`, immediately —
    an unlocked append is strictly better than losing the round in an
    environment where locking can never succeed."""
    lock_path = ledger_dir / _LEDGER_LOCK_FILENAME
    if fcntl is None:
        _warn_ledger_lock_unavailable(lock_path, "fcntl module unavailable")
        yield
        return
    try:
        lock_file = open(lock_path, "a+")
    except (IsADirectoryError, PermissionError) as exc:
        _warn_ledger_lock_unavailable(lock_path, str(exc))
        yield
        return
    except OSError as exc:
        if exc.errno in _STRUCTURAL_LOCK_ERRNOS:
            _warn_ledger_lock_unavailable(lock_path, str(exc))
            yield
            return
        raise
    try:
        deadline = time.monotonic() + _LEDGER_LOCK_TIMEOUT_SECONDS
        warned_contention = False
        locked = False
        while True:
            try:
                fcntl.flock(lock_file.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
                locked = True
                break
            except OSError as exc:
                if exc.errno in _STRUCTURAL_LOCK_ERRNOS:
                    _warn_ledger_lock_unavailable(lock_path, str(exc))
                    break
                if not warned_contention:
                    print(
                        f"loom-gate-markers: origin ledger lock at "
                        f"{lock_path} is held by another process; "
                        f"waiting up to {_LEDGER_LOCK_TIMEOUT_SECONDS}s...",
                        file=sys.stderr,
                    )
                    warned_contention = True
                if time.monotonic() >= deadline:
                    raise _LedgerLockTimeout(
                        f"could not acquire {lock_path} within "
                        f"{_LEDGER_LOCK_TIMEOUT_SECONDS}s"
                    ) from None
                time.sleep(_LEDGER_LOCK_POLL_SECONDS)
        try:
            yield
        finally:
            if locked:
                fcntl.flock(lock_file.fileno(), fcntl.LOCK_UN)
    finally:
        lock_file.close()


def _is_valid_ledger_shape(data: object) -> bool:
    """True iff `data` has the ledger's minimal load-bearing shape: a
    dict with a dict `branches`, each of whose values is a list. The
    read-modify-write below needs `.setdefault`/`.append` to succeed on
    exactly this shape — a schema-1 ledger that is valid JSON but has any
    other shape (top-level list/null, non-dict `branches`, or a
    per-branch value that isn't a list) is corrupt in the same
    load-bearing sense a JSON syntax error is (whole-branch review
    finding 2 — the docstring's "a single corruption cannot bias every
    future round to empty" claim was false for exactly these three
    shapes, each of which used to raise deep inside `.setdefault`/
    `.append` and fall through to the blanket swallow, permanently
    dropping every future round)."""
    if not isinstance(data, dict):
        return False
    branches = data.get("branches")
    if not isinstance(branches, dict):
        return False
    return all(isinstance(value, list) for value in branches.values())


def _recover_corrupt_ledger(path: Path, reason: str) -> dict:
    """Move `path` aside as `origin-ledger.json.corrupt-<UTC timestamp>`
    (preserved for a human to inspect, never deleted) and return a fresh
    empty ledger dict. Shared by every recoverable corruption shape
    (unparseable JSON, a directory sitting at the ledger path, and the
    three valid-JSON-wrong-shape variants) — all are corrupt in the same
    load-bearing sense, so all get the identical treatment and stderr
    wording."""
    corrupt_path = path.with_name(
        f"{_ORIGIN_LEDGER_FILENAME}.corrupt-"
        f"{datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S%f')}"
    )
    path.replace(corrupt_path)
    print(
        "loom-gate-markers: origin-ledger.json was corrupt "
        f"({reason}); moved aside to {corrupt_path.name} and started "
        "a fresh ledger — future rounds keep recording instead of "
        "being dropped forever.",
        file=sys.stderr,
    )
    return {"schema": 1, "branches": {}}


def _load_or_recover_ledger(path: Path) -> dict:
    """Read `<ledger_dir>/origin-ledger.json`, recovering a fresh empty
    ledger from any of five corrupt shapes (whole-branch review finding
    2) instead of raising into the caller's blanket swallow: unparseable
    JSON text, a directory sitting at the ledger path (`IsADirectoryError`
    from the read itself, before `json.loads` ever runs), and three
    valid-JSON-but-wrong-shape variants — see `_is_valid_ledger_shape`."""
    try:
        raw = path.read_text(encoding="utf-8")
    except FileNotFoundError:
        return {"schema": 1, "branches": {}}
    except IsADirectoryError as exc:
        return _recover_corrupt_ledger(path, str(exc))
    try:
        data = json.loads(raw)
    except json.JSONDecodeError as exc:
        return _recover_corrupt_ledger(path, str(exc))
    if not _is_valid_ledger_shape(data):
        return _recover_corrupt_ledger(
            path, f"unexpected ledger shape ({type(data).__name__})"
        )
    return data


def _append_origin_ledger(
    ledger_dir: Path,
    branch: str,
    verdict: str | None,
    head_sha: str | None,
    findings: list[dict],
) -> None:
    """Append one round entry to `<ledger_dir>/origin-ledger.json`, keyed
    by `branch`; append-only, never reset (Task 7 — the re-cut's binding
    constraint: persistence, not enforcement). Deliberately NOT built on
    `_write_marker`: that helper's whole-file overwrite is exactly the
    semantic the ledger must not have — this reads the existing file
    (if any), appends, and writes the merged result back, still via
    tmpfile+`os.replace` for atomicity, and the whole read-modify-write
    is held under `_ledger_lock` (finding 1) so concurrent invocations —
    the normal case from separate `git worktree` checkouts sharing this
    one file — cannot race and silently lose each other's round.

    Parameter renamed from `marker_dir` (round-3 review finding C): every
    OTHER marker's directory really is `<git-dir>/loom`
    (`resolve_marker_dir`), but the caller always passes THIS function
    `resolve_common_marker_dir(repo) or marker_dir` — a different
    directory (`<git-common-dir>/loom`) in the normal (non-fallback)
    case. Naming the parameter `marker_dir` here invited exactly the
    conflation between the two directories this branch already fixed
    once (see the module docstring's `origin-ledger.json` entry).

    `findings` is precomputed by the caller (`_ledger_finding_entries`,
    Task 8: real quote verification against `head_sha`) rather than
    derived here from raw text — this function only assembles the round
    envelope and writes it, so the one git-touching computation is never
    duplicated between the ledger write and any stdout reporting the
    caller does with the same results.

    Recording must NEVER block a mint or change an exit code: every
    failure (unwritable directory, a wedged lock, anything not handled
    by `_load_or_recover_ledger`) is reported on stderr and swallowed
    here — this function raises nothing to its caller. Five corrupt
    ledger shapes ARE recovered rather than swallowed-and-forgotten
    (moved aside, never deleted, fresh ledger starts) — see
    `_load_or_recover_ledger`."""
    path = ledger_dir / _ORIGIN_LEDGER_FILENAME
    try:
        ledger_dir.mkdir(parents=True, exist_ok=True)
        with _ledger_lock(ledger_dir):
            data = _load_or_recover_ledger(path)
            rounds = data.setdefault("branches", {}).setdefault(branch, [])
            rounds.append(
                {
                    "round": len(rounds) + 1,
                    "verdict": verdict,
                    "head_sha": head_sha,
                    "written_at": _now_iso(),
                    "findings": findings,
                }
            )
            fd, tmp = tempfile.mkstemp(
                dir=str(ledger_dir), prefix=_ORIGIN_LEDGER_FILENAME, suffix=".tmp"
            )
            try:
                with os.fdopen(fd, "w", encoding="utf-8") as f:
                    json.dump(data, f, indent=2)
                    f.write("\n")
                os.replace(tmp, path)
            finally:
                if os.path.exists(tmp):
                    os.unlink(tmp)
    except Exception as exc:  # noqa: BLE001 — recording must never block a mint
        print(
            f"loom-gate-markers: could not record origin ledger entry: {exc}",
            file=sys.stderr,
        )


def validate_verdict_text(text: str) -> tuple[str | None, list[str]]:
    """Validate reviewer verdict text against the schema gate.

    Returns (verdict_value, problems). `verdict_value` is None unless a
    well-formed verdict line with an allowed value was found. `problems`
    is empty iff the text is schema-valid (verdict value included).
    Tolerant line-regex matching — the input is YAML-ish, not strict YAML.
    """
    problems: list[str] = []

    sv = _KEY_RE["standards_version"].search(text)
    if not sv:
        problems.append("standards_version: missing or empty")

    verdict: str | None = None
    vm = _KEY_RE["verdict"].search(text)
    if not vm:
        problems.append("verdict: missing")
    elif vm.group(1) not in ALLOWED_VERDICTS:
        problems.append(
            f"verdict: invalid value {vm.group(1)!r} "
            f"(allowed: {', '.join(sorted(ALLOWED_VERDICTS))})"
        )
    else:
        verdict = vm.group(1)

    if not _KEY_RE["dimension_scores"].search(text):
        problems.append("dimension_scores: block missing")

    problems.extend(_finding_problems(text))
    return verdict, problems


def _origin_required(dimension_value: str | None) -> bool:
    """True unless `dimension_value` both parses and is in the docs-arm
    set. The requirement is the default; the docs-arm exemption is the
    only branch that returns False — an absent (`None`), empty/
    whitespace-only, or unrecognized value all require `origin:`
    (§Pinned dimension partition, fail-closed clause)."""
    if dimension_value is None:
        return True
    value = dimension_value.strip()
    if not value:
        return True
    return value not in _DOCS_ARM_DIMENSIONS


def _finding_arm(dimension_value: str | None) -> str:
    """`"docs"` iff `_origin_required` would exempt this dimension (i.e. it
    both parses and falls in the docs-arm set); `"code"` otherwise —
    reuses `_origin_required` rather than re-deriving the partition, so
    the ledger's arm classification can never drift from the gate's own
    requirement/exemption logic (§Pinned dimension partition, fail
    closed: absent/blank/unrecognized all land on `"code"`)."""
    return "docs" if not _origin_required(dimension_value) else "code"


def _parse_origin(
    origin_value: str | None,
) -> tuple[tuple[str, str] | None, str | None]:
    """The ONE place `origin:` values parse — collapses what were two
    duplicate split/blank-check/quoted-check copies (grammar validation,
    quote extraction), whose drift let three mutants survive undetected
    in the extraction copy alone (deleted blank-check, deleted
    quoted-check, `find`->`rfind` split). One parse site makes that
    mutant class impossible to express.

    Returns `(spec, problem)`: `problem` is None iff `origin_value` is
    `none` or a grammar-valid `<path> :: "<quote>"`, else a violation
    description. `spec` is `(path, quote)` — quote WITHOUT its wrapping
    `"` — when extracted; None for `none`, absent, or malformed.

    Split on the FIRST ` :: `: a path may not contain it, a quote may —
    so the first occurrence is the boundary (§Notes kickoff decision,
    corrected 2026-08-02: the earlier "split on the LAST ` :: `"
    mis-parsed a quote containing the separator into a truncated path
    and an unquoted remainder). No backslash-escape convention. The
    quote's interior must be non-blank: `""` and `"   "` are refused —
    an empty quote is not a verbatim quote, and Task 2 verifies by
    substring, so an empty quote would match every file and pass the
    whole gate as a well-formed origin.

    No minimum length or width beyond non-blank (amendment 2026-08-02,
    user decision, deleting a display-width floor that shipped and was
    then measured against this repo's committed `.md` files: the
    benefit it bought was small next to the review cost of getting
    there. The axis was wrong, not the constant — see the plan's
    §Notes for the measurement and the four superseded token/width
    rules it replaced)."""
    if origin_value is None:
        return None, "no origin: line"
    value = origin_value.strip()
    if value == "none":
        return None, None
    idx = value.find(" :: ")
    if idx == -1:
        return None, (
            f"origin: {origin_value!r} is not 'none' or '<path> :: \"<quote>\"'"
        )
    # `path` is always non-empty here: `value` is already stripped (so
    # value[0] is non-whitespace) and the separator starts with a space,
    # so idx can never be 0 — value[:idx] always contains value[0].
    path, quote = value[:idx], value[idx + 4 :]
    if len(quote) < 2 or quote[0] != '"' or quote[-1] != '"':
        return None, f"origin: {origin_value!r} quote is not fully quoted"
    inner = quote[1:-1]
    if not inner.strip():
        return None, f"origin: {origin_value!r} quote is empty or blank"
    return (path, inner), None


def _origin_grammar_problem(origin_value: str | None) -> str | None:
    """Thin wrapper over `_parse_origin`: the problem text (Task 1)."""
    return _parse_origin(origin_value)[1]


def _origin_path_quote(origin_value: str | None) -> tuple[str, str] | None:
    """Thin wrapper over `_parse_origin`: the extracted spec (Task 2)."""
    return _parse_origin(origin_value)[0]


def _finding_quote_status(
    origin_value: str | None,
    repo: Path,
    head_sha: str | None,
    file_cache: dict[str, tuple[str | None, str | None]],
) -> str:
    """The origin ledger's `quote_status` (Task 7 shape, Task 8
    verification): `"absent"` when no `origin:` line exists at all,
    `"none"` when the value is literally `none`, `"malformed"` when a
    value is present but not grammar-valid (the round refuses on that
    ground regardless — see `_finding_problems` — but the ledger still
    gets an entry for it, so this needs its own label, distinct from
    the five real verification-failure reasons below which all
    presuppose a grammar-valid path/quote pair to check).

    Otherwise this is real verification against `head_sha`'s committed
    content, reusing `_show_committed_file`'s failure-kind constants
    directly as the `unverified-<reason>` suffix so the ledger's wording
    can never drift from that helper's own vocabulary:
    `unverified-sha-unresolvable`, `unverified-file-absent`,
    `unverified-not-a-file`, `unverified-undecodable-blob`, or (the file
    read fine but never contained the quote) `unverified-quote-absent`.
    A verifying quote records `verified-exact` or `verified-normalised`.

    NONE of the `unverified-<reason>` outcomes are returned to the
    caller as a mint-blocking problem (Task 8 re-cut: verification is a
    recorded fact, not a refusal) — only the caller's own grammar check
    still refuses.

    `head_sha` may be `None` (an unresolvable HEAD) even though in
    every observed git state that happens exactly when `branch` is also
    `None` — and the caller only appends to the ledger when `branch` is
    not `None` — so this path should be unreachable in practice. Guarded
    explicitly anyway rather than assumed: a quote needs a real sha to
    check against, and this function must never call `_show_committed_file`
    with one it does not have."""
    if origin_value is None:
        return "absent"
    if origin_value.strip() == "none":
        return "none"
    spec = _origin_path_quote(origin_value)
    if spec is None:
        return "malformed"
    path, quote = spec
    if head_sha is None:
        return f"unverified-{_SHA_UNRESOLVABLE}"
    if path not in file_cache:
        file_cache[path] = _show_committed_file(repo, head_sha, path)
    content, failure_kind = file_cache[path]
    if failure_kind is not None:
        return f"unverified-{failure_kind}"
    tier = _quote_match_tier(content, quote)
    if tier is None:
        return "unverified-quote-absent"
    return f"verified-{tier}"


# §Notes kickoff decision (quote-match strictness): fold typographic
# quotes/dashes/NBSP to their ASCII equivalents. Deliberately narrow —
# only the marks the decision names, nothing broader.
_TYPOGRAPHIC_FOLD = {
    "‘": "'",  # LEFT SINGLE QUOTATION MARK
    "’": "'",  # RIGHT SINGLE QUOTATION MARK
    "“": '"',  # LEFT DOUBLE QUOTATION MARK
    "”": '"',  # RIGHT DOUBLE QUOTATION MARK
    "–": "-",  # EN DASH
    "—": "-",  # EM DASH
    " ": " ",  # NO-BREAK SPACE
}


def _normalize_for_quote_match(text: str) -> str:
    """NFC-normalize, fold typographic quotes/dashes/NBSP to ASCII, then
    collapse each run of whitespace to a single space. Case-sensitive;
    does NOT strip `**` or backticks (§Notes kickoff decision — the SAME
    normaliser is applied to both the quote and the haystack)."""
    text = unicodedata.normalize("NFC", text)
    for typographic, ascii_form in _TYPOGRAPHIC_FOLD.items():
        text = text.replace(typographic, ascii_form)
    return re.sub(r"\s+", " ", text)


def _quote_match_tier(haystack: str, quote: str) -> str | None:
    """"exact" if `quote` occurs byte-for-byte in `haystack`; "normalised"
    if it occurs only after both sides pass through the identical
    normaliser; else None. Two-stage per §Notes kickoff decision — this
    repo hard-wraps prose, so a truthful one-line quote of a multi-line
    passage fails byte-exact matching by construction."""
    if quote in haystack:
        return "exact"
    if _normalize_for_quote_match(quote) in _normalize_for_quote_match(haystack):
        return "normalised"
    return None


class _FindingInfo:
    """One `- severity:` finding block's sibling-field values, as read by
    `_iter_findings`. `dimension_value`/`origin_value` are None when the
    field is absent OR duplicated (a duplicate is unparseable, not
    resolved first/last-wins — see `_iter_findings`)."""

    __slots__ = (
        "start_line",
        "where_ok",
        "dimension_value",
        "origin_value",
        "duplicate_origin",
        "duplicate_dimension",
    )

    def __init__(
        self,
        start_line: int,
        where_ok: bool,
        dimension_value: str | None,
        origin_value: str | None,
        duplicate_origin: bool,
        duplicate_dimension: bool,
    ) -> None:
        self.start_line = start_line
        self.where_ok = where_ok
        self.dimension_value = dimension_value
        self.origin_value = origin_value
        self.duplicate_origin = duplicate_origin
        self.duplicate_dimension = duplicate_dimension


def _iter_findings(text: str):
    """Yield one `_FindingInfo` per `- severity:` finding block. Shared by
    `_finding_problems` (Task 1's grammar/requirement checks) and
    `_ledger_finding_entries` (Task 8's real quote verification) so both
    read `origin:` through the identical block-scoping rule — a value nested
    inside e.g. a `note: |` block-literal must never count as a sibling
    field of either reader."""
    lines = text.splitlines()
    starts = [i for i, line in enumerate(lines) if _FINDING_RE.match(line)]
    for n, start in enumerate(starts):
        end = starts[n + 1] if n + 1 < len(starts) else len(lines)
        # A dedented top-level key also terminates the block.
        for j in range(start + 1, end):
            if _TOP_KEY_RE.match(lines[j]):
                end = j
                break
        where_ok = False
        dimension_values: list[str] = []
        origin_values: list[str] = []
        # Sibling fields (where:/dimension:/origin:) must sit at the SAME
        # column as the first NON-BLANK line following `- severity:` — not
        # at any indentation. A line nested deeper (e.g. inside a `note: |`
        # block-literal that happens to quote `dimension: ...` from a
        # pasted verdict-schema example) is content, not a sibling field,
        # and must not be read as one. The column is whatever indent the
        # block actually uses (never a hardcoded width), so a well-formed
        # finding indented at 6 spaces mints exactly like one at 4. A blank
        # line right after `- severity:` is ordinary formatting, not a
        # signal — it is skipped when hunting for the column.
        column = None
        for line in lines[start + 1 : end]:
            if line.strip():
                column = _INDENT_RE.match(line).group(0)
                break
        if column is not None:
            for line in lines[start + 1 : end]:
                if _INDENT_RE.match(line).group(0) != column:
                    continue
                wm = _WHERE_RE.match(line)
                if wm and _PATHLIKE_RE.search(wm.group(1)):
                    where_ok = True
                dm = _DIMENSION_RE.match(line)
                if dm:
                    dimension_values.append(dm.group(1))
                om = _ORIGIN_RE.match(line)
                if om:
                    origin_values.append(om.group(1))
        yield _FindingInfo(
            start_line=start + 1,
            where_ok=where_ok,
            # Two or more `dimension:` (or `origin:`) lines in one block is
            # malformed: YAML readers disagree on which value wins (first
            # vs last), so a duplicate is treated as unparseable rather
            # than resolved either way — fail closed (§Pinned dimension
            # partition).
            dimension_value=(
                dimension_values[0] if len(dimension_values) == 1 else None
            ),
            origin_value=origin_values[0] if len(origin_values) == 1 else None,
            duplicate_origin=len(origin_values) > 1,
            duplicate_dimension=len(dimension_values) > 1,
        )


def _finding_problems(text: str) -> list[str]:
    """Every `- severity:` finding block must carry a path-like `where:`,
    and — unless its `dimension:` both parses and falls in the docs-arm
    set — an `origin:` line valued `none` or `<path> :: "<quote>"`
    (§Pinned dimension partition; requirement is the default, the
    docs-arm exemption is the explicit branch).

    That exemption governs only whether `origin:` must be CARRIED. An
    `origin:` line that IS present is grammar-checked on every arm,
    docs included — the exemption never excuses a malformed value a
    docs-arm finding chose to write (bare path, unterminated quote,
    blank quote). Skipping this on the exempt branch was a real bug: a
    docs-arm finding with a malformed `origin:` used to sail through
    with no `origin:` requirement AND no grammar check on the one it
    carried, minting clean.

    A duplicate `dimension:` line is refused here for the SAME reason a
    duplicate `origin:` is (whole-branch review finding 3, mirroring the
    prior `origin:` fix onto `dimension:`): which of two `dimension:`
    values is intended is genuinely ambiguous, and `dimension` directly
    drives the arm partition (`_finding_arm`) that decides whether
    `origin:` is even required. Before this check, a duplicate
    `dimension:` line was invisible to `_finding_problems` — as long as
    `origin:` was ALSO present and valid (or dimension's own fail-closed
    default happened to already force an `origin:` requirement that was
    separately satisfied), the finding minted at exit 0, landing in the
    ledger byte-identical to a finding with no `dimension:` line at all
    (`dimension: null`, `arm: "code"`) and silently contaminating the
    population partition the ledger exists to keep clean. The ledger's
    OWN recording needs no schema change for this: `dimension_value` is
    already `None` for a duplicate exactly as it is for an absent line
    (`_iter_findings`), and `_finding_arm`'s fail-closed default already
    treats every unparseable dimension — absent, blank, or duplicate —
    identically as `"code"` (§Pinned dimension partition); the gap was
    purely that nothing refused the MINT on this ambiguity the way
    `duplicate_origin` already does."""
    problems: list[str] = []
    for info in _iter_findings(text):
        if not info.where_ok:
            problems.append(
                f"finding at line {info.start_line}: no where: line with a "
                "path-like token in its block"
            )
        if info.duplicate_dimension:
            problems.append(
                f"finding at line {info.start_line}: duplicate dimension: "
                "lines (exactly one is required)"
            )
        if info.duplicate_origin:
            problems.append(
                f"finding at line {info.start_line}: duplicate origin: lines "
                "(exactly one is required)"
            )
        elif info.origin_value is None:
            if _origin_required(info.dimension_value):
                problems.append(
                    f"finding at line {info.start_line}: no origin: line"
                )
        else:
            origin_problem = _origin_grammar_problem(info.origin_value)
            if origin_problem:
                problems.append(
                    f"finding at line {info.start_line}: {origin_problem}"
                )
    return problems


def _ledger_finding_entries(
    text: str, repo: Path, head_sha: str | None
) -> list[dict]:
    """One dict per `- severity:` finding block, for the origin ledger
    (Task 7 shape) — reuses `_iter_findings` unchanged so the ledger's
    notion of "a finding" never diverges from the gate's. `dimension`
    and `origin_raw` are the values verbatim (or `null`); `arm` is
    derived via `_finding_arm`. `quote_status` (Task 8) is REAL
    verification against `head_sha`'s committed content via
    `_finding_quote_status` — never the worktree (brief §Resolved
    Questions 1) — computed here (not left as Task 7's `"pending"`
    placeholder) so a round that never reaches the mint step (schema
    failure, NEEDS_REVISION) still leaves a real verified/unverified
    record; measured on this repo, 0 of 24 severity-🔴 findings ever
    reached the old mint-time-only verification call. One file-content
    cache shared across every finding in this call's `text` — a path
    quoted by more than one finding is read from committed content once.

    A duplicate `origin:` (`info.duplicate_origin`) is special-cased
    BEFORE `_finding_quote_status` ever runs: that function's own
    `origin_value is None` branch returns `"absent"`, which is correct
    for a finding with no `origin:` line but wrong for one with TWO —
    `_iter_findings` sets `origin_value` to `None` in both cases (see its
    docstring), so without this guard a duplicate would be recorded
    byte-identically to "no origin: line existed", discarding both
    quotes under a false label. `origin_raw` is `null` for a duplicate:
    which of the two quotes was intended is genuinely ambiguous, so
    neither is kept rather than guessing first-or-last."""
    file_cache: dict[str, tuple[str | None, str | None]] = {}
    entries = []
    for info in _iter_findings(text):
        if info.duplicate_origin:
            entries.append(
                {
                    "arm": _finding_arm(info.dimension_value),
                    "dimension": info.dimension_value,
                    "origin_raw": None,
                    "quote_status": "duplicate",
                }
            )
            continue
        entries.append(
            {
                "arm": _finding_arm(info.dimension_value),
                "dimension": info.dimension_value,
                "origin_raw": info.origin_value,
                "quote_status": _finding_quote_status(
                    info.origin_value, repo, head_sha, file_cache
                ),
            }
        )
    return entries


def _record_origin_ledger_round(
    repo: Path,
    marker_dir: Path,
    branch: str | None,
    verdict: str | None,
    text: str,
) -> tuple[str | None, Path, list[dict]]:
    """Resolve `head_sha`, compute this round's ledger findings (Task 8's
    real quote verification), and append them to the origin ledger —
    extracted out of `_cmd_review_pass` (round-3 review finding D: that
    function exceeded the house 50-line ceiling with no documented
    rationale; this block and the normalised-quote advisory below were
    both self-contained and extractable, so the standard's
    document-an-exception escape hatch does not apply).

    Ledger recording — INCLUDING real quote verification (Task 8) —
    happens on EVERY invocation that got this far, ahead of every early
    return the caller takes below it (NEEDS_REVISION, schema-failure,
    unresolvable HEAD), all of which used to return before writing
    anything or verifying anything (Task 7/8 re-cut: the binding
    constraint is persistence, not enforcement; verification is a
    recorded fact, not a mint-time-only refusal). `_ledger_finding_entries`
    is safe to call even when `head_sha` is `None` — it never touches
    git in that case (`_finding_quote_status`'s own guard) — so no
    ordering dependency on the caller's HEAD-resolution check is needed.

    The ledger lives under git-common-dir, not git-dir (see
    `resolve_common_marker_dir`) — a worktree checkout must append to
    the SAME ledger the main checkout reads. Falls back to `marker_dir`
    only if common-dir resolution itself fails, which should not happen
    given `resolve_marker_dir` already succeeded to reach `_cmd_review_pass`
    at all. Computed unconditionally (not just when `branch` resolves)
    so the caller's advisory can always name the real path — printing
    the bare filename used to imply the same directory as
    `review-pass.json`, which is false from a worktree (whole-branch
    review finding 4).

    Returns `(head_sha, ledger_dir, ledger_findings)` — all three are
    needed by the caller after this returns, for the marker payload, the
    branch/head_sha resolvability check, and the normalised-quote
    advisory respectively."""
    head_sha = _git(repo, "rev-parse", "HEAD")
    ledger_findings = _ledger_finding_entries(text, repo, head_sha)
    ledger_dir = resolve_common_marker_dir(repo) or marker_dir
    if branch is not None:
        _append_origin_ledger(ledger_dir, branch, verdict, head_sha, ledger_findings)
    return head_sha, ledger_dir, ledger_findings


def _print_normalised_quote_advisory(
    ledger_findings: list[dict], ledger_dir: Path
) -> None:
    """Print one aggregated advisory line naming how many findings this
    round matched only after normalisation — printing the identical
    sentence once per finding gave a reader no way to tell which
    finding(s) it referred to. Extracted out of `_cmd_review_pass`
    (round-3 review finding D, alongside `_record_origin_ledger_round`
    above) — self-contained and does not need any of that function's
    other local state."""
    normalised_count = sum(
        1 for entry in ledger_findings if entry["quote_status"] == "verified-normalised"
    )
    if normalised_count:
        plural = "" if normalised_count == 1 else "s"
        ledger_path = ledger_dir / _ORIGIN_LEDGER_FILENAME
        print(
            f"loom-gate-markers: {normalised_count} origin quote{plural} "
            f"matched only after normalisation — see {ledger_path} for "
            "detail. (This entry may be missing if the ledger write "
            "above was itself swallowed — see stderr.)"
        )


def _cmd_review_pass(repo: Path, marker_dir: Path, args: argparse.Namespace) -> int:
    try:
        text = Path(args.verdict_file).read_text(encoding="utf-8")
    except OSError as exc:
        print(f"loom-gate-markers: cannot read verdict file: {exc}", file=sys.stderr)
        return 4

    verdict, problems = validate_verdict_text(text)
    branch = _git(repo, "rev-parse", "--abbrev-ref", "HEAD")
    head_sha, ledger_dir, ledger_findings = _record_origin_ledger_round(
        repo, marker_dir, branch, verdict, text
    )

    if problems:
        print(
            "loom-gate-markers: verdict text failed schema validation; "
            "no marker written:",
            file=sys.stderr,
        )
        for problem in problems:
            print(f"  - {problem}", file=sys.stderr)
        return 4
    if verdict == "NEEDS_REVISION":
        print(
            "loom-gate-markers: verdict is NEEDS_REVISION — a failed review "
            "does not mint a pass marker.",
            file=sys.stderr,
        )
        return 3

    if branch is None or head_sha is None:
        print("loom-gate-markers: cannot resolve HEAD.", file=sys.stderr)
        return 2

    # Quote verification no longer gates the mint (Task 8): a finding
    # whose quote does not verify — absent, file absent, not a file,
    # undecodable, sha unresolvable — is recorded above in the ledger as
    # `unverified-<reason>`, and the mint proceeds regardless. Only the
    # deterministic grammar check (`problems`, above) still refuses — it
    # fails CLOSED (never a silent fail-open exemption), but is NOT
    # false-positive-free: two indent-drift shapes (an outlier first
    # field; a tab against spaces) over-refuse a well-formed verdict,
    # tracked OPEN at
    # docs/loom/backlog/2026-08-02-finding-block-field-scanner-false-refuses-on-indent-drift.md.
    # Quote verification, measured on this repo, was blocking a push on
    # exactly the tail of findings it could never see anyway — which is
    # why it no longer gates.
    payload = {
        "schema": 1,
        "branch": branch,
        "head_sha": head_sha,
        "verdict": verdict,
        "written_at": _now_iso(),
    }
    patch_id_fields = compute_patch_id(repo)
    if patch_id_fields is not None:
        payload["base_sha"], payload["patch_id"] = patch_id_fields
    path = _write_marker(marker_dir, "review-pass.json", payload)
    print(path)
    _print_normalised_quote_advisory(ledger_findings, ledger_dir)
    return 0


def validate_suite_line(line: str) -> list[str]:
    """All problems with `line` as a green pytest-style summary; []
    when clean. Used only by `_cmd_validate` (the dry-run text check).
    The `verified` WRITE path no longer accepts a self-typed suite line —
    it executes a real command via `run_verification` instead."""
    problems: list[str] = []
    m = _PASSED_RE.search(line)
    if not m or int(m.group(1)) == 0:
        problems.append(
            f'suite_line: {line!r} has no "N passed" (N > 0) — not a green run'
        )
    if _SUITE_REJECT_RE.search(line.lower()):
        problems.append(
            f"suite_line: {line!r} contains a failed/error token — not a green run"
        )
    return problems


# Bounded tail of the verification run's combined stdout+stderr, recorded
# in the marker for a human/auditor to inspect. 4 KB is enough to carry a
# pytest summary line plus context without bloating the marker file.
VERIFY_OUTPUT_TAIL_CHARS = 4000


def run_verification(repo: Path, command: str) -> tuple[int, str]:
    """Execute `command` in `repo` via the shell; return (exit_code,
    output_tail) where output_tail is the last VERIFY_OUTPUT_TAIL_CHARS
    chars of combined stdout+stderr. A launch failure (OSError) is
    reported as a non-zero exit so the caller mints no marker.

    HONEST RESIDUAL (do not over-claim): this binds the `verified` marker
    to a command that really ran and really exited 0, and records that
    command — but it is NOT cryptographic proof a genuine test suite ran.
    An agent can still pass `--run "true"`. This raises the bar from
    "type a suite-line string" (zero execution) to "a real command must
    run and exit 0, and is recorded for auditability"; local execution
    cannot guarantee more."""
    try:
        result = subprocess.run(
            command,
            shell=True,
            cwd=str(repo),
            capture_output=True,
            text=True,
        )
    except OSError as exc:
        return 1, f"loom-gate-markers: could not launch --run command: {exc}"
    combined = (result.stdout or "") + (result.stderr or "")
    return result.returncode, combined[-VERIFY_OUTPUT_TAIL_CHARS:]


def _cmd_verified(repo: Path, marker_dir: Path, args: argparse.Namespace) -> int:
    command = args.run
    exit_code, output_tail = run_verification(repo, command)
    if exit_code != 0:
        print(
            f"loom-gate-markers: verification command exited {exit_code} "
            f"(not a green run); no marker written. Command: {command!r}",
            file=sys.stderr,
        )
        return 4

    head_sha = _git(repo, "rev-parse", "HEAD")
    if head_sha is None:
        print("loom-gate-markers: cannot resolve HEAD.", file=sys.stderr)
        return 2
    payload = {
        "schema": 1,
        "head_sha": head_sha,
        "run_cmd": command,
        "exit_code": exit_code,
        "output_tail": output_tail,
        "written_at": _now_iso(),
    }
    patch_id_fields = compute_patch_id(repo)
    if patch_id_fields is not None:
        payload["base_sha"], payload["patch_id"] = patch_id_fields
    path = _write_marker(marker_dir, "verified.json", payload)
    print(path)
    return 0


def _cmd_waiver(repo: Path, marker_dir: Path, args: argparse.Namespace) -> int:
    reason = args.reason.strip()
    if len(reason) < MIN_WAIVER_REASON_CHARS:
        print(
            "loom-gate-markers: waiver reason must be a real justification "
            f"(>= {MIN_WAIVER_REASON_CHARS} chars); no marker written.",
            file=sys.stderr,
        )
        return 4

    path = _write_marker(
        marker_dir,
        "waiver.json",
        {
            "schema": 1,
            "scope": "push",
            "reason": args.reason,
            "written_at": _now_iso(),
        },
    )
    print(
        "loom-gate-markers: WARNING — waiver written. This BYPASSES the "
        "review gate for the next push (one-shot). Reason recorded: "
        f"{args.reason}",
        file=sys.stderr,
    )
    print(path)
    return 0


def _cmd_validate(args: argparse.Namespace) -> int:
    """Dry-run schema check: same rules `review-pass`/`verified` apply
    at write time, but reports EVERY violation in one pass instead of
    exiting on the first (today's writers exit-4 on the first problem,
    forcing a fix-rerun-fix retry loop). Writes nothing; needs no repo."""
    try:
        text = Path(args.verdict_file).read_text(encoding="utf-8")
    except OSError as exc:
        print(f"loom-gate-markers: cannot read verdict file: {exc}", file=sys.stderr)
        return 4

    _, problems = validate_verdict_text(text)
    if args.suite_line is not None:
        problems += validate_suite_line(args.suite_line)

    # `validate` takes no --repo, so it has no HEAD to verify a quote
    # against — quote verification is a `review-pass`-only step. Say so
    # loudly here rather than passing silently: a silent skip on exactly
    # the pre-flight path `requesting-code-review` Step 3 tells reviewers
    # to use would be a fail-open (§Notes kickoff decision).
    quoted_origin_count = sum(
        1 for info in _iter_findings(text) if _origin_path_quote(info.origin_value)
    )
    if quoted_origin_count:
        print(
            "loom-gate-markers: quote verification did not run for "
            f"{quoted_origin_count} quoted origin(s) — `validate` takes "
            "no --repo and cannot check committed content. Run "
            "review-pass to verify."
        )

    if problems:
        print("loom-gate-markers: validation found problems:", file=sys.stderr)
        for problem in problems:
            print(f"  - {problem}", file=sys.stderr)
        return 4
    print("loom-gate-markers: clean — no violations found.")
    return 0


def main(argv: list[str] | None = None) -> int:
    """CLI entry: `review-pass --verdict-file <path>` /
    `verified --run "<cmd>"` / `waiver --reason "<text>"` /
    `validate --verdict-file <path> [--suite-line "<text>"]`,
    each of the first three with optional `--repo <path>` (default
    cwd). `validate` is a dry-run text check — no repo, no marker
    write — so it takes no `--repo`."""
    parser = argparse.ArgumentParser(
        description="Write loom gate markers for hooks/git-guard.py"
    )
    # --repo lives ONLY on the subparsers (post-subcommand position).
    # Defining it on the parent too is a silent-wrong-repo trap: argparse
    # subparser defaults clobber the parent-parsed value, so
    # `--repo /x review-pass ...` would fall back to cwd. The
    # pre-subcommand form now fails loudly (unrecognized argument).
    subparsers = parser.add_subparsers(dest="command", required=True)

    rp = subparsers.add_parser("review-pass")
    rp.add_argument("--repo", default=".", help="repo path (default: cwd)")
    rp.add_argument("--verdict-file", required=True)
    rp.set_defaults(func=_cmd_review_pass)

    vf = subparsers.add_parser("verified")
    vf.add_argument("--repo", default=".", help="repo path (default: cwd)")
    vf.add_argument(
        "--run",
        required=True,
        help="verification command to execute in --repo; the marker is "
        "minted ONLY if it exits 0 (records the command + output tail)",
    )
    vf.set_defaults(func=_cmd_verified)

    wv = subparsers.add_parser("waiver")
    wv.add_argument("--repo", default=".", help="repo path (default: cwd)")
    wv.add_argument("--reason", required=True)
    wv.set_defaults(func=_cmd_waiver)

    vd = subparsers.add_parser("validate")
    vd.add_argument("--verdict-file", required=True)
    vd.add_argument("--suite-line", default=None)

    args = parser.parse_args(argv)
    if args.command == "validate":
        return _cmd_validate(args)
    repo = Path(args.repo)
    marker_dir = resolve_marker_dir(repo)
    if marker_dir is None:
        print(f"loom-gate-markers: not a git repository: {repo}", file=sys.stderr)
        return 2
    return args.func(repo, marker_dir, args)


if __name__ == "__main__":
    raise SystemExit(main())
