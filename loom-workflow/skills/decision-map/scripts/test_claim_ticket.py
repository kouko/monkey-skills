"""Tests for conservative stale-claim recovery."""

from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parent))

import claim_ticket  # noqa: E402


def _write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def _commit(repo: Path, message: str, date: str, time: str = "12:00:00") -> None:
    subprocess.run(["git", "add", "."], cwd=repo, check=True)
    env = os.environ | {
        "GIT_AUTHOR_DATE": f"{date}T{time}+00:00",
        "GIT_COMMITTER_DATE": f"{date}T{time}+00:00",
    }
    subprocess.run(["git", "commit", "-qm", message], cwd=repo, env=env, check=True)


def _repo(
    tmp_path: Path,
    claim: str,
    *,
    commit_date: str = "2026-07-01",
    commit_time: str = "12:00:00",
) -> tuple[Path, Path]:
    tmp_path.mkdir(parents=True)
    subprocess.run(["git", "init", "-q"], cwd=tmp_path, check=True)
    subprocess.run(["git", "config", "user.email", "test@example.com"], cwd=tmp_path, check=True)
    subprocess.run(["git", "config", "user.name", "Test"], cwd=tmp_path, check=True)
    ticket = tmp_path / "docs" / "loom" / "maps" / "outcome" / "tickets" / "slice.md"
    _write(
        ticket,
        "---\n"
        "type: delivery\n"
        "status: claimed\n"
        f"claim: {claim}\n"
        "graduated-from: null\n"
        "---\n\nShip a slice.\n",
    )
    _commit(tmp_path, "record claim", commit_date, commit_time)
    return tmp_path, ticket


def test_reclaim_requires_dated_claim_and_no_post_claim_git_change(
    tmp_path: Path,
) -> None:
    # @req: REQ-97
    missing_repo, missing_ticket = _repo(tmp_path / "missing", "alice")
    missing_before = missing_ticket.read_bytes()
    with pytest.raises(claim_ticket.ClaimRecoveryError, match="dated"):
        claim_ticket.reclaim(
            missing_ticket,
            new_owner="bob",
            takeover_date="2026-08-30",
            stale_before="2026-08-15",
            repo_root=missing_repo,
        )
    assert missing_ticket.read_bytes() == missing_before

    changed_repo, changed_ticket = _repo(
        tmp_path / "changed", "alice, 2026-08-01"
    )
    changed_ticket.write_text(
        changed_ticket.read_text(encoding="utf-8") + "\nObservable work.\n",
        encoding="utf-8",
    )
    _commit(changed_repo, "work after claim", "2026-08-20")
    changed_before = changed_ticket.read_bytes()
    with pytest.raises(claim_ticket.ClaimRecoveryError, match="post-claim"):
        claim_ticket.reclaim(
            changed_ticket,
            new_owner="bob",
            takeover_date="2026-08-30",
            stale_before="2026-08-15",
            repo_root=changed_repo,
        )
    assert changed_ticket.read_bytes() == changed_before

    stale_repo, stale_ticket = _repo(tmp_path / "stale", "alice, 2026-08-01")
    claim_ticket.reclaim(
        stale_ticket,
        new_owner="bob",
        takeover_date="2026-08-30",
        stale_before="2026-08-15",
        repo_root=stale_repo,
    )
    text = stale_ticket.read_text(encoding="utf-8")
    assert "claim: bob, 2026-08-30" in text
    assert text.count("takeover: alice -> bob") == 1
    assert "basis: claim dated 2026-08-01; no post-claim Git change" in text


def test_reclaim_preserves_owner_when_last_change_is_on_claim_date(
    tmp_path: Path,
) -> None:
    # @req: REQ-97
    repo, ticket = _repo(
        tmp_path / "repo",
        "alice, 2026-08-01",
        commit_date="2026-08-01",
        commit_time="09:00:00",
    )
    ticket.write_text(
        ticket.read_text(encoding="utf-8") + "\nChanged at 18:00 on claim day.\n",
        encoding="utf-8",
    )
    _commit(repo, "same-day work", "2026-08-01", "18:00:00")
    before = ticket.read_bytes()

    with pytest.raises(claim_ticket.ClaimRecoveryError, match="ambiguous"):
        claim_ticket.reclaim(
            ticket,
            new_owner="bob",
            takeover_date="2026-08-30",
            stale_before="2026-08-15",
            repo_root=repo,
        )

    assert ticket.read_bytes() == before


def test_reclaim_reads_exactly_one_authoritative_frontmatter_claim(
    tmp_path: Path,
) -> None:
    # @req: REQ-97
    repo, ticket = _repo(tmp_path / "null", "null")
    ticket.write_text(
        ticket.read_text(encoding="utf-8")
        + "\nA body example must not become authority:\nclaim: alice, 2026-08-01\n",
        encoding="utf-8",
    )
    _commit(repo, "body example", "2026-07-01")
    before = ticket.read_bytes()
    with pytest.raises(claim_ticket.ClaimRecoveryError, match="frontmatter"):
        claim_ticket.reclaim(
            ticket,
            new_owner="bob",
            takeover_date="2026-08-30",
            stale_before="2026-08-15",
            repo_root=repo,
        )
    assert ticket.read_bytes() == before

    duplicate_repo, duplicate = _repo(
        tmp_path / "duplicate", "alice, 2026-08-01"
    )
    duplicate.write_text(
        duplicate.read_text(encoding="utf-8").replace(
            "claim: alice, 2026-08-01",
            "claim: alice, 2026-08-01\nclaim: carol, 2026-07-01",
        ),
        encoding="utf-8",
    )
    _commit(duplicate_repo, "duplicate claim", "2026-07-01")
    duplicate_before = duplicate.read_bytes()
    with pytest.raises(claim_ticket.ClaimRecoveryError, match="exactly one"):
        claim_ticket.reclaim(
            duplicate,
            new_owner="bob",
            takeover_date="2026-08-30",
            stale_before="2026-08-15",
            repo_root=duplicate_repo,
        )
    assert duplicate.read_bytes() == duplicate_before


def test_reclaim_cas_preserves_concurrent_ticket_edit(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    # @req: REQ-97
    repo, ticket = _repo(tmp_path / "repo", "alice, 2026-08-01")
    audited = ticket.read_bytes()

    def concurrent_edit() -> None:
        ticket.write_bytes(audited + b"\nConcurrent body edit.\n")

    monkeypatch.setattr(claim_ticket, "_before_claim_replace", concurrent_edit)
    with pytest.raises(claim_ticket.ClaimRecoveryError, match="changed"):
        claim_ticket.reclaim(
            ticket,
            new_owner="bob",
            takeover_date="2026-08-30",
            stale_before="2026-08-15",
            repo_root=repo,
        )

    assert ticket.read_bytes() == audited + b"\nConcurrent body edit.\n"
    assert b"claim: alice, 2026-08-01" in ticket.read_bytes()
