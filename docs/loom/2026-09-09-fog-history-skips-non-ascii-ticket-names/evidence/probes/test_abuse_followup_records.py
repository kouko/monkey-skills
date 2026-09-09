"""Adversarial probes for the two records this branch adds.

The branch carries no executable behaviour: one memory-store entry and one
open intent. What can still be wrong is the machine-read shape of those
records -- an entry the generated index does not list, frontmatter the
store's own integrity check rejects, an intent the checker refuses, or a
`needs-design:` line that does not appear verbatim in the commit that
decided it. Each probe below attacks one of those, by running the real
checkers rather than by reading the files and agreeing with them.

Run: python3 -m pytest docs/loom/2026-09-09-fog-history-skips-non-ascii-ticket-names/evidence/probes/test_abuse_followup_records.py -q
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[5]
INTENT = REPO / "docs/loom/intent/2026-09-09-fog-history-skips-non-ascii-ticket-names.md"
ENTRY = (
    REPO
    / "docs/loom/memory/cat-file-batch-sizes-are-bytes-and-text-mode-collapses-crlf.md"
)
CHECKER = REPO / "loom-code/scripts/loom_checker.py"
INTEGRITY = REPO / "scripts/check_loom_memory_integrity.py"


def _run(*args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, *args], cwd=REPO, capture_output=True, text=True, timeout=300
    )


def test_memory_store_integrity_accepts_the_new_entry() -> None:
    """The store's own integrity check passes with the entry in place.

    It fails when an entry's frontmatter is malformed or when the
    generated index does not carry a line for it, which is the failure
    mode a hand-written entry reaches most often.
    """
    result = _run(str(INTEGRITY))
    assert result.returncode == 0, result.stdout + result.stderr


def test_memory_index_lists_the_new_entry_by_its_own_slug() -> None:
    """The index line is keyed by the entry's `name:` slug.

    A file whose frontmatter slug and filename disagree indexes under one
    name and is opened under another; the store's format rule exists to
    make those the same string.
    """
    readme = (REPO / "docs/loom/memory/README.md").read_text(encoding="utf-8")
    slug = "cat-file-batch-sizes-are-bytes-and-text-mode-collapses-crlf"
    assert ENTRY.name == f"{slug}.md"
    assert f"{slug}.md" in readme
    frontmatter_name = next(
        line.split(":", 1)[1].strip()
        for line in ENTRY.read_text(encoding="utf-8").splitlines()
        if line.startswith("name:")
    )
    assert frontmatter_name == slug


def test_intent_passes_the_contract_checker() -> None:
    """The checker accepts the intent file and its deciding commit.

    This covers `intent.schema` (required frontmatter and H2 sections,
    with a non-empty Open questions section) and
    `intent.needs-design-reason`, which compares the file's
    `needs-design:` line against the commit message character for
    character.
    """
    result = _run(str(CHECKER), "intent", str(INTENT.relative_to(REPO)))
    assert result.returncode == 0, result.stdout + result.stderr


def test_intent_needs_design_line_appears_verbatim_in_its_commit() -> None:
    """The deciding commit carries the needs-design line unchanged.

    Re-wrapping or translating that line in the commit message is the
    ordinary way this rule is broken, and it is invisible to a reader
    who only opens the intent file.
    """
    line = next(
        raw
        for raw in INTENT.read_text(encoding="utf-8").splitlines()
        if raw.startswith("needs-design:")
    )
    log = subprocess.run(
        ["git", "log", "--format=%B", "-n", "20"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=300,
    ).stdout
    assert line in log.splitlines()


def test_intent_status_stays_open_until_a_decision_point() -> None:
    """Nobody has confirmed this intent yet, so its status must read open.

    An abandoned change's follow-up is easy to record as `confirmed`
    out of momentum; the confirmation belongs to the user, and a
    prematurely confirmed intent lets a plan be written against a
    problem nobody agreed to solve.
    """
    status = next(
        raw
        for raw in INTENT.read_text(encoding="utf-8").splitlines()
        if raw.startswith("status:")
    )
    assert status.strip() == "status: open"
