"""Regression tests for W1-04 — `read_base_graduated_ids` reads base
Ticket history with one `git cat-file --batch` spawn instead of one
`git show` per ticket.

Oracle: `check_map_fog.read_base_graduated_ids`'s pre-existing per-
ticket `git show` loop. Both cases below were chosen from the plan's
named test bullets for this task.
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

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
    # Pin explicitly: this machine's global git config is
    # `autocrlf=input`, which would silently normalize a fixture's
    # CRLF content away on `git add`, masking the CRLF regression case
    # below (repo memory already records this false-green trap).
    _git(["config", "core.autocrlf", "false"], repo_root)


def _map_dir(repo_root: Path) -> Path:
    return repo_root / "docs" / "loom" / "maps" / MAP_ID


def _write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def _write_bytes(path: Path, data: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(data)


def _commit(repo_root: Path, message: str) -> str:
    _git(["add", "-A"], repo_root)
    _git(["commit", "-m", message], repo_root)
    return _git(["rev-parse", "HEAD"], repo_root).stdout.strip()


def test_graduated_set_identical_20_tickets_two_git_spawns(tmp_path: Path) -> None:
    """20 tickets at base (10 graduated, 10 not): the returned set must
    equal what the old per-ticket `git show` loop produces, and the
    read must cost exactly 2 git subprocess spawns (one `ls-tree`, one
    `cat-file --batch`) regardless of ticket count."""
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


def test_missing_tree_and_unparsable_ticket_verbatim_schema_violation(
    tmp_path: Path,
) -> None:
    """Negative case: a nonexistent base ref (tree cannot be
    enumerated) and a ticket blob with no frontmatter fence must both
    raise SchemaViolation with today's exact message text."""
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

    bogus_ref = "deadbeefdeadbeefdeadbeefdeadbeefdeadbeef"
    try:
        check_map_fog.read_base_graduated_ids(repo_root, bogus_ref, map_dir / "MAP.md")
        raise AssertionError("expected SchemaViolation")
    except map_store.SchemaViolation as exc:
        assert str(exc) == f"cannot enumerate base Ticket history at {bogus_ref!r}"


def test_multibyte_content_does_not_corrupt_batch_blob_boundaries(
    tmp_path: Path,
) -> None:
    """`cat-file --batch` reports `<size>` in BYTES, but `_run_git`
    decodes stdout to `str` (`text=True`) — a naive
    `output[pos:pos+size]` slices CHARACTERS, not bytes. A ticket body
    containing multi-byte (CJK) content therefore drifts the blob
    boundary for every ticket that follows it in the batch stream: the
    old per-ticket `git show` loop read each ticket independently and
    was immune to this, so it is the oracle here (both graduated ids
    present, no exception).

    Ticket 1's body is CJK-heavy (byte length far exceeds char length);
    tickets 2 and 3 each carry `graduated-from`. A byte/char-confused
    reader either loses F-2 (drifted past it) or raises outright — both
    the un-fixed batched code have been observed to do here."""
    repo_root = tmp_path / "repo"
    _init_repo(repo_root)
    map_dir = _map_dir(repo_root)
    tickets = map_dir / "tickets"
    _write(map_dir / "MAP.md", "hello\n")

    cjk_body = "日本語テキスト" * 5  # 35 chars, 105 UTF-8 bytes
    _write(tickets / "ticket-01.md", f"---\nstatus: open\n---\n{cjk_body}\n")
    _write(tickets / "ticket-02.md", "---\ngraduated-from: F-2\n---\nbody\n")
    _write(tickets / "ticket-03.md", "---\ngraduated-from: F-3\n---\nbody\n")
    base_ref = _commit(repo_root, "multibyte content")

    result = check_map_fog.read_base_graduated_ids(
        repo_root, base_ref, map_dir / "MAP.md"
    )
    assert result == {"F-2", "F-3"}


def test_crlf_content_does_not_corrupt_batch_blob_boundaries(tmp_path: Path) -> None:
    """`subprocess.run(text=True)` applies universal-newline
    translation (`\\r\\n` -> `\\n`, lone `\\r` -> `\\n`) on the way in.
    Re-encoding the already-translated `str` back to bytes therefore
    yields FEWER bytes than git's declared `<size>` for any blob with
    CRLF line endings — the boundary drifts by one byte per CRLF,
    exactly the failure a bytes-mode batch read must avoid.

    `a.md` has CRLF frontmatter fences and a 60-line CRLF body; `b.md`
    and `c.md` are plain LF, each carrying `graduated-from`. The old
    per-ticket `git show` loop reads each blob's raw bytes independent
    of any other blob's line endings, so all three ids together are
    the oracle here."""
    repo_root = tmp_path / "repo"
    _init_repo(repo_root)
    map_dir = _map_dir(repo_root)
    tickets = map_dir / "tickets"
    _write(map_dir / "MAP.md", "hello\n")

    crlf_body = "line\r\n" * 60
    a_content = f"---\r\ngraduated-from: F-1\r\n---\r\n{crlf_body}".encode("utf-8")
    _write_bytes(tickets / "a.md", a_content)
    _write(tickets / "b.md", "---\ngraduated-from: F-2\n---\nbody\n")
    _write(tickets / "c.md", "---\ngraduated-from: F-3\n---\nbody\n")
    base_ref = _commit(repo_root, "crlf content")

    result = check_map_fog.read_base_graduated_ids(
        repo_root, base_ref, map_dir / "MAP.md"
    )
    assert result == {"F-1", "F-2", "F-3"}
