"""Adversarial probes for W1-04 — `cat-file --batch` in
`read_base_graduated_ids` (check_map_fog.py).

Oracle = today's `git show`-per-ticket implementation. Every literal
message and returned-set value below was observed by actually running
the current code (not guessed), so a post-fix implementation must
reproduce them verbatim or these probes go red for the right reason.

Run: python3 -m pytest docs/loom/2026-09-07-loom-script-performance/evidence/probes/test_abuse_fog_cat_file_batch.py -q
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

_SCRIPTS_DIR = (
    Path(__file__).resolve().parents[5]
    / "loom-workflow"
    / "skills"
    / "decision-map"
    / "scripts"
)
sys.path.insert(0, str(_SCRIPTS_DIR))

import check_map_fog  # noqa: E402
import map_store  # noqa: E402

MAP_ID = "wayfinder"


def _git(args: list[str], cwd: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["git", *args], cwd=cwd, capture_output=True, text=True, check=True
    )


def _init_repo(repo_root: Path) -> None:
    repo_root.mkdir(parents=True)
    _git(["init", "-b", "main"], repo_root)
    _git(["config", "user.email", "test@example.com"], repo_root)
    _git(["config", "user.name", "Test"], repo_root)


def _map_dir(repo_root: Path) -> Path:
    return repo_root / "docs" / "loom" / "maps" / MAP_ID


def _write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def _commit(repo_root: Path, message: str) -> str:
    _git(["add", "-A"], repo_root)
    _git(["commit", "-m", message], repo_root)
    return _git(["rev-parse", "HEAD"], repo_root).stdout.strip()


# --- 1. spawn count -------------------------------------------------


def test_read_base_graduated_ids_twenty_tickets_two_git_spawns(tmp_path: Path) -> None:
    """20 tickets at base (10 graduated, 10 not) must be read with
    exactly 2 git subprocess spawns, and the returned set must equal
    the set produced by today's per-file `git show` loop."""
    repo_root = tmp_path / "repo"
    _init_repo(repo_root)
    map_dir = _map_dir(repo_root)
    tickets = map_dir / "tickets"
    _write(map_dir / "MAP.md", "hello\n")

    expected: set[str] = set()
    for i in range(20):
        grad = f"F-{i}" if i % 2 == 0 else None
        text = "---\nstatus: open\n"
        if grad:
            text += f"graduated-from: {grad}\n"
            expected.add(grad)
        text += "---\nbody\n"
        _write(tickets / f"ticket-{i:02d}.md", text)
    base_ref = _commit(repo_root, "20 tickets")

    calls: list[list[str]] = []
    original = check_map_fog._run_git

    def counting(
        args: list[str], cwd: Path, *a, **kw
    ) -> subprocess.CompletedProcess[str]:
        calls.append(args)
        return original(args, cwd, *a, **kw)

    check_map_fog._run_git = counting
    try:
        result = check_map_fog.read_base_graduated_ids(
            repo_root, base_ref, map_dir / "MAP.md"
        )
    finally:
        check_map_fog._run_git = original

    assert result == expected
    assert len(calls) == 2, f"expected 2 git spawns, got {len(calls)}: {calls}"


# --- 2. error-text equivalence ---------------------------------------


def test_read_base_graduated_ids_missing_tickets_dir_returns_empty_set(
    tmp_path: Path,
) -> None:
    """Base ref has no `tickets/` dir at all — today's `ls-tree`
    silently returns empty output (no exception), so the function
    returns an empty set. A fix must not turn this into a
    SchemaViolation — that would be a new, illegal failure mode."""
    repo_root = tmp_path / "repo"
    _init_repo(repo_root)
    map_dir = _map_dir(repo_root)
    _write(map_dir / "MAP.md", "hello\n")
    base_ref = _commit(repo_root, "base, no tickets dir")

    result = check_map_fog.read_base_graduated_ids(
        repo_root, base_ref, map_dir / "MAP.md"
    )
    assert result == set()


def test_read_base_graduated_ids_unparsable_ticket_raises_verbatim_schema_violation(
    tmp_path: Path,
) -> None:
    """A ticket blob at base with no frontmatter fence must raise
    SchemaViolation with today's exact message text."""
    repo_root = tmp_path / "repo"
    _init_repo(repo_root)
    map_dir = _map_dir(repo_root)
    _write(map_dir / "MAP.md", "hello\n")
    _write(map_dir / "tickets" / "bad.md", "no frontmatter here\n")
    base_ref = _commit(repo_root, "bad ticket")

    try:
        check_map_fog.read_base_graduated_ids(repo_root, base_ref, map_dir / "MAP.md")
        raise AssertionError("expected SchemaViolation")
    except map_store.SchemaViolation as exc:
        assert str(exc) == (
            "base Ticket history 'docs/loom/maps/wayfinder/tickets/bad.md' "
            "fails to parse: missing frontmatter opening '---' fence"
        )


def test_read_base_graduated_ids_nonexistent_base_ref_raises_verbatim_schema_violation(
    tmp_path: Path,
) -> None:
    """A base ref that resolves to nothing at all (never committed)
    must raise SchemaViolation with today's exact listing-failure
    message, not crash some other way."""
    repo_root = tmp_path / "repo"
    _init_repo(repo_root)
    map_dir = _map_dir(repo_root)
    _write(map_dir / "MAP.md", "hello\n")
    _commit(repo_root, "base")
    bogus_ref = "deadbeefdeadbeefdeadbeefdeadbeefdeadbeef"

    try:
        check_map_fog.read_base_graduated_ids(repo_root, bogus_ref, map_dir / "MAP.md")
        raise AssertionError("expected SchemaViolation")
    except map_store.SchemaViolation as exc:
        assert str(exc) == (
            f"cannot enumerate base Ticket history at {bogus_ref!r}"
        )


# --- 3. hostile blob content and paths --------------------------------


def test_read_base_graduated_ids_hostile_paths_and_sizes_match_old_code(
    tmp_path: Path,
) -> None:
    """A >1MB ticket body, a path with a space, a non-ASCII path, a
    non-`.md` file, and `graduated-from: null` must all resolve to the
    same set today's per-file `git show` loop produces.

    Observed (not assumed) today: the non-ASCII path is a LATENT BUG,
    not a clean pass — `ls-tree --name-only` quote-escapes it as
    `"...\\346\\227\\245....md"` (a trailing `"` after `.md`), so
    `name.endswith(".md")` is False and its `graduated-from: F-3` is
    silently dropped. This probe pins that buggy-but-real behavior as
    the oracle: F-3 is deliberately ABSENT below. See adversary finding
    on quoted-path handling in the new `ls-tree -r` (no `--name-only`)
    parser — it must not inherit or worsen this silent drop."""
    repo_root = tmp_path / "repo"
    _init_repo(repo_root)
    map_dir = _map_dir(repo_root)
    tickets = map_dir / "tickets"
    _write(map_dir / "MAP.md", "hello\n")

    big_body = "x" * (2 * 1024 * 1024)
    _write(tickets / "big.md", f"---\ngraduated-from: F-4\n---\n{big_body}\n")
    _write(tickets / "with space.md", "---\ngraduated-from: F-2\n---\nbody\n")
    _write(tickets / "日本語.md", "---\ngraduated-from: F-3\n---\nbody\n")
    _write(tickets / "notes.txt", "---\ngraduated-from: F-99\n---\n")
    _write(tickets / "nullgrad.md", "---\ngraduated-from: null\n---\nbody\n")
    _write(tickets / "nokey.md", "---\nstatus: open\n---\nbody\n")
    base_ref = _commit(repo_root, "hostile tickets")

    result = check_map_fog.read_base_graduated_ids(
        repo_root, base_ref, map_dir / "MAP.md"
    )
    assert result == {"F-2", "F-4"}


def test_read_base_graduated_ids_symlink_ticket_raises_schema_violation(
    tmp_path: Path,
) -> None:
    """A `.md` ticket that is actually a symlink (mode 120000) is
    listed by `ls-tree` alongside real files and its blob content is
    the link target text, not YAML frontmatter — today's `git show`
    reads it anyway and `parse_frontmatter` rejects it. A fix must
    preserve this same failure, not silently skip symlinks."""
    repo_root = tmp_path / "repo"
    _init_repo(repo_root)
    map_dir = _map_dir(repo_root)
    tickets = map_dir / "tickets"
    _write(map_dir / "MAP.md", "hello\n")
    _write(tickets / "normal.md", "---\ngraduated-from: F-1\n---\nbody\n")
    (tickets / "link.md").symlink_to("normal.md")
    base_ref = _commit(repo_root, "symlink ticket")

    try:
        check_map_fog.read_base_graduated_ids(repo_root, base_ref, map_dir / "MAP.md")
        raise AssertionError("expected SchemaViolation")
    except map_store.SchemaViolation as exc:
        assert "link.md" in str(exc)
        assert "fails to parse" in str(exc)


# --- 4. empty / absent boundary ---------------------------------------


def test_read_base_graduated_ids_empty_tickets_dir_returns_empty_set(
    tmp_path: Path,
) -> None:
    """`tickets/` exists at base but is empty (only reachable via a
    placeholder committed then removed from the tree, since git does
    not track empty dirs) — must return an empty set, not raise."""
    repo_root = tmp_path / "repo"
    _init_repo(repo_root)
    map_dir = _map_dir(repo_root)
    _write(map_dir / "MAP.md", "hello\n")
    placeholder = map_dir / "tickets" / ".gitkeep"
    _write(placeholder, "")
    _commit(repo_root, "placeholder")
    placeholder.unlink()
    _git(["add", "-A"], repo_root)
    base_ref = _commit(repo_root, "empty tickets dir")

    result = check_map_fog.read_base_graduated_ids(
        repo_root, base_ref, map_dir / "MAP.md"
    )
    assert result == set()


# --- 5. dependency failure ---------------------------------------------


def test_read_base_graduated_ids_blob_read_failure_raises_not_partial_set(
    tmp_path: Path,
) -> None:
    """If the git invocation that reads a ticket's blob content fails
    (non-zero exit), the whole call must raise SchemaViolation — it
    must never return a partial set silently missing that ticket's
    graduation."""
    repo_root = tmp_path / "repo"
    _init_repo(repo_root)
    map_dir = _map_dir(repo_root)
    tickets = map_dir / "tickets"
    _write(map_dir / "MAP.md", "hello\n")
    _write(tickets / "a.md", "---\ngraduated-from: F-1\n---\nbody\n")
    _write(tickets / "b.md", "---\ngraduated-from: F-2\n---\nbody\n")
    base_ref = _commit(repo_root, "two tickets")

    original = check_map_fog._run_git
    call_count = {"n": 0}

    def failing(
        args: list[str], cwd: Path, *a, **kw
    ) -> subprocess.CompletedProcess[str]:
        call_count["n"] += 1
        if call_count["n"] == 1:
            return original(args, cwd, *a, **kw)
        return subprocess.CompletedProcess(args=args, returncode=128, stdout="", stderr="fatal: bad object")

    check_map_fog._run_git = failing
    try:
        try:
            result = check_map_fog.read_base_graduated_ids(
                repo_root, base_ref, map_dir / "MAP.md"
            )
            raise AssertionError(
                f"expected SchemaViolation, got a result instead: {result!r}"
            )
        except map_store.SchemaViolation:
            pass
    finally:
        check_map_fog._run_git = original


def test_read_base_graduated_ids_cat_file_missing_blob_marker_raises_schema_violation(
    tmp_path: Path,
) -> None:
    """Named risk in the plan: `cat-file --batch` reports a genuinely
    missing blob inline as `<sha> missing` on stdout with exit 0,
    rather than a non-zero process exit. A batched reader that only
    checks the process return code would silently drop that ticket's
    graduation. This fakes the two-call batched shape (ls-tree, then
    one blob-reading call) and requires the missing-blob marker to
    still surface as a SchemaViolation naming the ticket."""
    repo_root = tmp_path / "repo"
    _init_repo(repo_root)
    map_dir = _map_dir(repo_root)
    tickets_rel = "docs/loom/maps/wayfinder/tickets"

    original = check_map_fog._run_git
    calls: list[list[str]] = []

    def fake(args: list[str], cwd: Path, *a, **kw) -> subprocess.CompletedProcess[str]:
        calls.append(args)
        if "ls-tree" in args:
            return subprocess.CompletedProcess(
                args=args,
                returncode=0,
                stdout=(
                    f"100644 blob deadbeefdeadbeefdeadbeefdeadbeefdeadbeef\t"
                    f"{tickets_rel}/ghost.md\n"
                ),
                stderr="",
            )
        # any other spawn stands in for the blob-reading call
        # (cat-file --batch or equivalent, run with binary=True),
        # reporting the blob as missing inline per git's documented
        # format. Reads the blob sha list back out of whatever
        # stdin-carrying argument the production call used, instead of
        # re-hardcoding it, so this double stays correct regardless of
        # how that plumbing works. Returns BYTES stdout — the
        # production reader now runs this call in binary mode
        # (`binary=True`) and indexes/slices raw bytes, never `str`.
        stdin_bytes = kw.get("stdin") or (a[0] if a else b"")
        if isinstance(stdin_bytes, str):
            stdin_bytes = stdin_bytes.encode()
        first_sha = stdin_bytes.decode().strip().splitlines()[0]
        return subprocess.CompletedProcess(
            args=args,
            returncode=0,
            stdout=f"{first_sha} missing\n".encode(),
            stderr=b"",
        )

    check_map_fog._run_git = fake
    try:
        try:
            result = check_map_fog.read_base_graduated_ids(
                repo_root, "HEAD", map_dir / "MAP.md"
            )
            raise AssertionError(
                f"expected SchemaViolation for a missing blob, got: {result!r}"
            )
        except map_store.SchemaViolation as exc:
            assert "ghost.md" in str(exc)
    finally:
        check_map_fog._run_git = original
