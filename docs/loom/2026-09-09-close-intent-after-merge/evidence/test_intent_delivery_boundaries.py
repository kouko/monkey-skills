"""Adversarial boundary checks for derived intent delivery state."""
from __future__ import annotations

import json
import subprocess
import sys
import tempfile
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(REPO_ROOT / "loom-code" / "scripts"))

import loom_checker  # noqa: E402

CHANGE_ID = "2026-09-09-adversarial"


def git(repo: Path, *args: str) -> str:
    return subprocess.run(
        ["git", "-C", str(repo), *args],
        check=True,
        capture_output=True,
        text=True,
    ).stdout.strip()


def write_delivery(repo: Path) -> None:
    intent = repo / "docs/loom/intent" / f"{CHANGE_ID}.md"
    intent.parent.mkdir(parents=True)
    intent.write_text(
        "# Adversarial\nstatus: confirmed 2026-09-09\n",
        encoding="utf-8",
    )
    attestation = repo / "docs/loom" / CHANGE_ID / "attestation.json"
    attestation.parent.mkdir(parents=True)
    attestation.write_text(
        json.dumps(
            {
                "schema": "loom-attestation/v1",
                "change_id": CHANGE_ID,
                "content_digest": "historical",
                "executions": [{
                    "kind": "package-tests", "command": "pytest", "artifact": "",
                    "result": "pass", "command_digest": "fixture",
                }],
                "verdicts": [{
                    "reviewer": "fixture", "vendor": "test", "model": "test",
                    "lens": "code", "verdict": "PASS", "findings": [],
                }],
                "findings": [],
            }
        )
        + "\n",
        encoding="utf-8",
    )
    git(repo, "add", "docs")
    git(repo, "commit", "-q", "-m", "local delivery")


def main() -> None:
    with tempfile.TemporaryDirectory(prefix="loom-intent-adversary-") as directory:
        repo = Path(directory)
        git(repo, "init", "-q", "-b", "main")
        git(repo, "config", "user.email", "test@example.com")
        git(repo, "config", "user.name", "Test")
        write_delivery(repo)

        state, _ = loom_checker.intent_delivery_state(repo, CHANGE_ID)
        assert state == "indeterminate", "local main must not prove remote delivery"

        git(repo, "update-ref", "refs/remotes/other/main", "HEAD")
        git(repo, "symbolic-ref", "refs/remotes/origin/HEAD", "refs/remotes/other/main")
        state, _ = loom_checker.intent_delivery_state(repo, CHANGE_ID)
        assert state == "indeterminate", "origin HEAD must not cross into another remote"

        git(repo, "update-ref", "refs/remotes/origin/trunk", "HEAD")
        git(repo, "symbolic-ref", "refs/remotes/origin/HEAD", "refs/remotes/origin/trunk")
        state, _ = loom_checker.intent_delivery_state(repo, CHANGE_ID)
        assert state == "delivered", "a canonical origin default snapshot must deliver"


if __name__ == "__main__":
    main()
