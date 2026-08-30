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


def _commit(repo: Path, message: str, date: str) -> None:
    subprocess.run(["git", "add", "."], cwd=repo, check=True)
    env = os.environ | {
        "GIT_AUTHOR_DATE": f"{date}T12:00:00+00:00",
        "GIT_COMMITTER_DATE": f"{date}T12:00:00+00:00",
    }
    subprocess.run(["git", "commit", "-qm", message], cwd=repo, env=env, check=True)


def _repo(tmp_path: Path, claim: str) -> tuple[Path, Path]:
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
    _commit(tmp_path, "record claim", "2026-07-01")
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
