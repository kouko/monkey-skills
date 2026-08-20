"""Tests for check_direction_freshness.find_unlanded_direction_changes
and the module's queue-relation gate + CLI.

Each test builds a THROWAWAY git repo under tmp_path — never asserts
against this repo's live branch state, which changes over time.
"""
from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

from check_direction_freshness import find_unlanded_direction_changes

SCRIPT = Path(__file__).parent / "check_direction_freshness.py"
AGENTS_MD = Path(__file__).parents[2] / "AGENTS.md"

_ENV = dict(os.environ, PYTHONDONTWRITEBYTECODE="1")


def _run_cli(repo: Path, brief_path: Path) -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, str(SCRIPT), str(brief_path), "--repo-root", str(repo)],
        capture_output=True,
        text=True,
        env=_ENV,
    )


def _git(repo: Path, *args: str) -> str:
    result = subprocess.run(
        ["git", "-C", str(repo), *args],
        check=True,
        capture_output=True,
        text=True,
    )
    return result.stdout.strip()


def _commit(repo: Path, message: str, *, date: str) -> str:
    env = os.environ.copy()
    env["GIT_AUTHOR_DATE"] = date
    env["GIT_COMMITTER_DATE"] = date
    subprocess.run(["git", "-C", str(repo), "add", "-A"], check=True, capture_output=True)
    subprocess.run(
        ["git", "-C", str(repo), "commit", "-q", "-m", message],
        check=True,
        capture_output=True,
        env=env,
    )
    return _git(repo, "rev-parse", "HEAD")


def _init_repo(tmp_path: Path) -> Path:
    repo = tmp_path / "repo"
    repo.mkdir()
    _git(repo, "init", "-q", "-b", "main")
    _git(repo, "config", "user.email", "test@example.com")
    _git(repo, "config", "user.name", "Test User")
    return repo


_DIRECTION_WITH_NOW_ENTRY = """# Direction

## Now

- widget-revamp — rescope the widget flow

## Next
"""


def _write_direction(repo: Path, body: str = _DIRECTION_WITH_NOW_ENTRY) -> None:
    (repo / "docs" / "loom").mkdir(parents=True, exist_ok=True)
    (repo / "docs" / "loom" / "DIRECTION.md").write_text(body, encoding="utf-8")


def test_reports_unlanded_change_to_a_now_entry(tmp_path: Path) -> None:
    """A side branch edits a ## Now entry's backlog file; the change
    never lands on main. The function must report it — this is the
    exact failure mode (kumiko's nine-day stale ## Now) the gate exists
    to catch."""
    repo = _init_repo(tmp_path)
    _write_direction(repo)
    backlog_dir = repo / "docs" / "loom" / "backlog"
    backlog_dir.mkdir(parents=True, exist_ok=True)
    entry = backlog_dir / "widget-revamp.md"
    entry.write_text("status: OPEN\nname: widget-revamp\n", encoding="utf-8")
    _commit(repo, "initial", date="2026-01-01T00:00:00 +0000")

    _git(repo, "checkout", "-q", "-b", "rescope")
    entry.write_text("status: OPEN\nname: widget-revamp\nrescoped: true\n", encoding="utf-8")
    _commit(repo, "rescope widget-revamp", date="2026-01-05T00:00:00 +0000")

    findings = find_unlanded_direction_changes(repo, base_branch="main")

    assert len(findings) == 1
    assert findings[0] == (
        "rescope — docs/loom/backlog/widget-revamp.md (tip 2026-01-05)"
    )


def test_squash_landed_change_yields_empty_list(tmp_path: Path) -> None:
    """A side branch's edit is squash-landed onto main with identical
    final content. Ancestry would call this branch unmerged (its tip is
    not an ancestor of main's new tip) — the intersection test must
    clear it because the file no longer differs from main."""
    repo = _init_repo(tmp_path)
    _write_direction(repo)
    backlog_dir = repo / "docs" / "loom" / "backlog"
    backlog_dir.mkdir(parents=True, exist_ok=True)
    entry = backlog_dir / "widget-revamp.md"
    entry.write_text("status: OPEN\nname: widget-revamp\n", encoding="utf-8")
    _commit(repo, "initial", date="2026-01-01T00:00:00 +0000")

    _git(repo, "checkout", "-q", "-b", "rescope")
    entry.write_text("status: OPEN\nname: widget-revamp\nrescoped: true\n", encoding="utf-8")
    _commit(repo, "rescope widget-revamp", date="2026-01-05T00:00:00 +0000")

    _git(repo, "checkout", "-q", "main")
    entry.write_text("status: OPEN\nname: widget-revamp\nrescoped: true\n", encoding="utf-8")
    _commit(repo, "squash-land rescope", date="2026-01-06T00:00:00 +0000")

    findings = find_unlanded_direction_changes(repo, base_branch="main")

    assert findings == []


def test_unrelated_file_change_yields_empty_list(tmp_path: Path) -> None:
    """A side branch changes a file outside the governing set — must
    not be reported."""
    repo = _init_repo(tmp_path)
    _write_direction(repo)
    backlog_dir = repo / "docs" / "loom" / "backlog"
    backlog_dir.mkdir(parents=True, exist_ok=True)
    (backlog_dir / "widget-revamp.md").write_text(
        "status: OPEN\nname: widget-revamp\n", encoding="utf-8"
    )
    (repo / "README.md").write_text("hello\n", encoding="utf-8")
    _commit(repo, "initial", date="2026-01-01T00:00:00 +0000")

    _git(repo, "checkout", "-q", "-b", "unrelated")
    (repo / "README.md").write_text("hello again\n", encoding="utf-8")
    _commit(repo, "edit readme", date="2026-01-05T00:00:00 +0000")

    findings = find_unlanded_direction_changes(repo, base_branch="main")

    assert findings == []


def test_missing_direction_file_yields_empty_list(tmp_path: Path) -> None:
    """No `docs/loom/DIRECTION.md` at all — empty list, not a raise."""
    repo = _init_repo(tmp_path)
    (repo / "README.md").write_text("hello\n", encoding="utf-8")
    _commit(repo, "initial", date="2026-01-01T00:00:00 +0000")

    _git(repo, "checkout", "-q", "-b", "side")
    (repo / "README.md").write_text("hello again\n", encoding="utf-8")
    _commit(repo, "edit readme", date="2026-01-05T00:00:00 +0000")

    findings = find_unlanded_direction_changes(repo, base_branch="main")

    assert findings == []


# --- CLI / queue-relation gate ------------------------------------------


def _init_repo_no_direction(tmp_path: Path) -> Path:
    repo = _init_repo(tmp_path)
    (repo / "README.md").write_text("hello\n", encoding="utf-8")
    _commit(repo, "initial", date="2026-01-01T00:00:00 +0000")
    return repo


def _write_brief(tmp_path: Path, queue_relation_body: str | None) -> Path:
    brief = tmp_path / "brief.md"
    text = "# Brief: x\n\n"
    if queue_relation_body is not None:
        text += f"## Queue relation\n\n{queue_relation_body}\n\n"
    text += "## Problem\n\nsome job.\n"
    brief.write_text(text, encoding="utf-8")
    return brief


def test_missing_queue_relation_exits_two_with_a_relayable_question(tmp_path: Path) -> None:
    """No `## Queue relation` section at all: exit 2, and stderr carries
    a question the caller can relay verbatim to the user."""
    repo = _init_repo_no_direction(tmp_path)
    brief = _write_brief(tmp_path, None)

    result = _run_cli(repo, brief)

    assert result.returncode == 2, f"stdout: {result.stdout}\nstderr: {result.stderr}"
    assert "Queue relation" in result.stderr
    assert "?" in result.stderr


def _write_direction_with_now_entry(repo: Path) -> None:
    (repo / "docs" / "loom").mkdir(parents=True, exist_ok=True)
    (repo / "docs" / "loom" / "DIRECTION.md").write_text(
        _DIRECTION_WITH_NOW_ENTRY, encoding="utf-8"
    )


def test_in_queue_naming_a_now_entry_exits_zero(tmp_path: Path) -> None:
    repo = _init_repo_no_direction(tmp_path)
    _write_direction_with_now_entry(repo)
    brief = _write_brief(tmp_path, "in-queue: widget-revamp")

    result = _run_cli(repo, brief)

    assert result.returncode == 0, f"stdout: {result.stdout}\nstderr: {result.stderr}"


def test_unqueued_with_reason_exits_zero(tmp_path: Path) -> None:
    repo = _init_repo_no_direction(tmp_path)
    brief = _write_brief(tmp_path, "unqueued — not part of any queued arc")

    result = _run_cli(repo, brief)

    assert result.returncode == 0, f"stdout: {result.stdout}\nstderr: {result.stderr}"


def test_unqueued_with_hyphen_separator_exits_two(tmp_path: Path) -> None:
    """`_UNQUEUED_RE` requires an em dash '—' separator, matching the
    same strictness `_NOW_ENTRY_RE` already defends — a plain hyphen
    in the brief's own `unqueued` declaration must not satisfy the
    gate (Decision Log: strictness stays on the parser, not the
    grammar)."""
    repo = _init_repo_no_direction(tmp_path)
    brief = _write_brief(tmp_path, "unqueued - not part of any queued arc")

    result = _run_cli(repo, brief)

    assert result.returncode == 2, f"stdout: {result.stdout}\nstderr: {result.stderr}"
    assert "Queue relation" in result.stderr


def test_displaces_a_now_entry_exits_zero(tmp_path: Path) -> None:
    repo = _init_repo_no_direction(tmp_path)
    _write_direction_with_now_entry(repo)
    brief = _write_brief(
        tmp_path, "displaces: widget-revamp — this is more urgent"
    )

    result = _run_cli(repo, brief)

    assert result.returncode == 0, f"stdout: {result.stdout}\nstderr: {result.stderr}"


def test_displaces_with_hyphen_separator_exits_two(tmp_path: Path) -> None:
    """`_DISPLACES_RE` requires an em dash '—' separator between the
    displaced entry's name and the reason — a plain hyphen in the
    brief's own `displaces:` declaration must not satisfy the gate
    (Decision Log: strictness stays on the parser, not the grammar).

    The Now entry's own name is deliberately hyphen-free
    ('widgetrevamp'), unlike the shared 'widget-revamp' fixture — a
    hyphen inside the name would let a loosened separator regex's
    non-greedy name group swallow only the name's own internal hyphen
    and still land on an unrelated-name rejection, masking the
    separator mutation this test exists to catch."""
    repo = _init_repo_no_direction(tmp_path)
    _write_direction(
        repo,
        body=(
            "# Direction\n\n## Now\n\n"
            "- widgetrevamp — rescope the widget flow\n\n## Next\n"
        ),
    )
    brief = _write_brief(
        tmp_path, "displaces: widgetrevamp - this is more urgent"
    )

    result = _run_cli(repo, brief)

    assert result.returncode == 2, f"stdout: {result.stdout}\nstderr: {result.stderr}"
    assert "Queue relation" in result.stderr


def test_pending_exits_two(tmp_path: Path) -> None:
    repo = _init_repo_no_direction(tmp_path)
    brief = _write_brief(tmp_path, "pending")

    result = _run_cli(repo, brief)

    assert result.returncode == 2, f"stdout: {result.stdout}\nstderr: {result.stderr}"
    assert "Queue relation" in result.stderr


def test_named_entry_absent_from_now_exits_two(tmp_path: Path) -> None:
    """A typo'd or nonexistent entry name must not silently satisfy
    the gate — this is the plan's explicit anti-typo validation."""
    repo = _init_repo_no_direction(tmp_path)
    _write_direction_with_now_entry(repo)
    brief = _write_brief(tmp_path, "in-queue: totally-made-up-entry")

    result = _run_cli(repo, brief)

    assert result.returncode == 2, f"stdout: {result.stdout}\nstderr: {result.stderr}"
    assert "totally-made-up-entry" in result.stderr


def test_hyphen_separated_now_entry_message_names_em_dash_requirement(
    tmp_path: Path,
) -> None:
    """`_NOW_ENTRY_RE` requires an em dash '—' separator (the same
    canonical form `backlog_index.py:38` documents); a plain hyphen
    entry is silently dropped by `_parse_now_entry_names`, so
    `widget-revamp` never lands in `now_names` even though it visibly
    sits under '## Now'. The message must not assert the entry is
    absent from the section (a reader can see it there) — it must
    instead name the real cause: the parser's em-dash requirement."""
    repo = _init_repo_no_direction(tmp_path)
    direction_with_hyphen = (
        "# Direction\n\n## Now\n\n"
        "- widget-revamp - rescope the widget flow\n\n## Next\n"
    )
    (repo / "docs" / "loom").mkdir(parents=True, exist_ok=True)
    (repo / "docs" / "loom" / "DIRECTION.md").write_text(
        direction_with_hyphen, encoding="utf-8"
    )
    brief = _write_brief(tmp_path, "in-queue: widget-revamp")

    result = _run_cli(repo, brief)

    assert result.returncode == 2, f"stdout: {result.stdout}\nstderr: {result.stderr}"
    assert "is not in DIRECTION.md's" not in result.stderr, (
        "message must not assert the entry is absent from a section "
        f"it visibly sits in: {result.stderr}"
    )
    assert "em dash" in result.stderr
    assert "widget-revamp" in result.stderr


def test_missing_brief_file_exits_one(tmp_path: Path) -> None:
    repo = _init_repo_no_direction(tmp_path)
    brief = tmp_path / "does-not-exist.md"

    result = _run_cli(repo, brief)

    assert result.returncode == 1, f"stdout: {result.stdout}\nstderr: {result.stderr}"


def test_advisory_printed_alongside_resolved_declaration(tmp_path: Path) -> None:
    """Task 1's findings print even on the exit-0 path when the
    declaration resolves — the report rides the co-print, not a
    separate scrollable output."""
    repo = _init_repo_no_direction(tmp_path)
    _write_direction_with_now_entry(repo)
    backlog_dir = repo / "docs" / "loom" / "backlog"
    backlog_dir.mkdir(parents=True, exist_ok=True)
    entry = backlog_dir / "widget-revamp.md"
    entry.write_text("status: OPEN\nname: widget-revamp\n", encoding="utf-8")
    _commit(repo, "add now entry", date="2026-01-02T00:00:00 +0000")

    _git(repo, "checkout", "-q", "-b", "rescope")
    entry.write_text("status: OPEN\nname: widget-revamp\nrescoped: true\n", encoding="utf-8")
    _commit(repo, "rescope widget-revamp", date="2026-01-05T00:00:00 +0000")
    _git(repo, "checkout", "-q", "main")

    brief = _write_brief(tmp_path, "in-queue: widget-revamp")

    result = _run_cli(repo, brief)

    assert result.returncode == 0, f"stdout: {result.stdout}\nstderr: {result.stderr}"
    assert "Unlanded direction change" in result.stdout
    assert "rescope" in result.stdout


def test_non_git_repo_root_does_not_gate(tmp_path: Path) -> None:
    """`--repo-root` pointed at a directory that is not a git work tree,
    but that does carry a DIRECTION.md with a non-empty '## Now', must
    not turn the advisory's git failure into a gating exit code. Only
    the '## Queue relation' declaration may gate; here it resolves, so
    the correct exit is 0 regardless of the advisory's git failure."""
    repo = tmp_path / "not-a-repo"
    repo.mkdir()
    _write_direction(repo)
    brief = _write_brief(tmp_path, "unqueued — testing")

    result = _run_cli(repo, brief)

    assert result.returncode == 0, f"stdout: {result.stdout}\nstderr: {result.stderr}"


def test_non_git_repo_root_announces_degraded_advisory_on_stderr(tmp_path: Path) -> None:
    """The advisory's inability to inspect branches must still be
    visible (Rule 12, fail-loud) — a silent empty advisory is a check
    that went green by matching nothing."""
    repo = tmp_path / "not-a-repo"
    repo.mkdir()
    _write_direction(repo)
    brief = _write_brief(tmp_path, "unqueued — testing")

    result = _run_cli(repo, brief)

    assert "advisory" in result.stderr.lower() or "unlanded" in result.stderr.lower(), (
        f"stderr must name what could not be inspected: {result.stderr}"
    )
    assert "git" in result.stderr.lower()


def _direction_freshness_entry() -> str:
    """The ONE command-surface bullet that declares check_direction_freshness.py.

    Sliced (not just searched) so the content pins below can only be
    satisfied by text living inside this entry — the same words parked
    in a neighbouring bullet would declare nothing about this command.
    """
    assert AGENTS_MD.is_file(), f"AGENTS.md is absent at {AGENTS_MD}"
    text = AGENTS_MD.read_text(encoding="utf-8")
    start = text.index("BEGIN command-surface (managed)")
    end = text.index("END command-surface (managed)")
    managed_block = text[start:end]
    assert "check_direction_freshness.py" in managed_block, \
        "AGENTS.md managed command-surface block must declare check_direction_freshness.py"

    entry_start = managed_block.index("- **Check a brief's direction freshness**")
    tail = managed_block[entry_start + 1:]
    next_bullet = tail.find("\n- **")
    stop = len(managed_block) if next_bullet == -1 else entry_start + 1 + next_bullet
    return managed_block[entry_start:stop]


def test_agents_md_declares_direction_freshness_script_exit_codes():
    """Command-surface accretion obligation: AGENTS.md's managed
    command-surface block must declare check_direction_freshness.py, and
    the entry's stated exit-2 meaning must match the script's actual
    behavior — a missing or malformed '## Queue relation' declaration —
    not just the script's mere presence in the block."""
    entry = _direction_freshness_entry()
    low = entry.lower()

    assert "exit 2" in low, "must state the exit-2 meaning"
    assert "queue relation" in low and (
        "missing or malformed" in low
    ), (
        "exit-2 must be documented as the queue relation being missing "
        "or malformed, matching the script's actual gate"
    )
    exit0_idx = low.index("exit 0")
    exit1_idx = low.index("exit 1")
    exit2_idx = low.index("exit 2")
    exit0_clause = low[exit0_idx:exit1_idx]
    exit1_clause = low[exit1_idx:exit2_idx]
    assert "resolve" in exit0_clause, (
        "exit-0 clause must pin the queue relation resolving, not just "
        "the token 'exit 0'"
    )
    assert "brief-path" in exit1_clause and "missing" in exit1_clause, (
        "exit-1 clause must pin brief-path being missing, not just the "
        "token 'exit 1'"
    )
