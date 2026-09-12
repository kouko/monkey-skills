"""Adversarial probes for the two records this branch adds.

The branch carries no executable behaviour: one memory-store entry and one
open intent. What can still be wrong is the machine-read shape of those
records -- frontmatter the store's own validator rejects, an index that
has drifted from what a fresh regeneration produces, an intent the
contract checker refuses, or a status line confirmed without the user.
The first three run the repository's real validators; the last reads the
file because no checker owns a status line's value. Each is written to
fail on the mistake it names, not to restate the file. The
`needs-design:` line's verbatim-in-the-commit obligation is deliberately
NOT probed here: rule `intent.needs-design-reason` already owns it, and
a probe that searched a fixed window of recent commits for that line
would pin a branch-moment fact and go red when the trunk moved.

Run: python3 -m pytest docs/loom/2026-09-09-fog-history-skips-non-ascii-ticket-names/evidence/probes/test_abuse_followup_records.py -q
"""

from __future__ import annotations

import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

REPO = Path(__file__).resolve().parents[5]
INTENT = REPO / "docs/loom/intent/2026-09-09-fog-history-skips-non-ascii-ticket-names.md"
ENTRY = (
    REPO
    / "docs/loom/memory/cat-file-batch-sizes-are-bytes-and-text-mode-collapses-crlf.md"
)
CHECKER = REPO / "loom-code/scripts/loom_checker.py"
MEMORY_CLI = REPO / "loom-workflow/skills/loom-memory/scripts/loom_memory.py"
STORE = REPO / "docs/loom/memory"


def _run(*args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, *args], cwd=REPO, capture_output=True, text=True, timeout=300
    )


def test_memory_store_validator_accepts_the_new_entry() -> None:
    """The store's own OKF v0.2 validator passes with the entry in place.

    It fails when an entry's frontmatter is malformed or missing a
    required field -- `name` matching the filename stem, a single-line
    `description`, a `type`, at least one `sources[].resource` -- which
    is the failure mode a hand-written entry reaches most often, and the
    exact one this entry hit when the store moved to the OKF profile.
    """
    result = _run(str(MEMORY_CLI), "validate", str(STORE.relative_to(REPO)))
    assert result.returncode == 0, result.stdout + result.stderr


def test_memory_index_matches_a_fresh_regeneration() -> None:
    """The committed index is byte-identical to a regenerated one.

    The validator treats index drift as a failure rather than a silent
    divergence, so an entry added without regenerating the index -- or an
    index hand-edited afterwards -- is caught here. Regenerating into a
    scratch copy keeps this probe read-only against the real store.
    """
    with tempfile.TemporaryDirectory() as tmp:
        scratch = Path(tmp) / "memory"
        shutil.copytree(STORE, scratch)
        committed = (scratch / "index.md").read_text(encoding="utf-8")
        result = _run(str(MEMORY_CLI), "regenerate-index", str(scratch))
        assert result.returncode == 0, result.stdout + result.stderr
        assert (scratch / "index.md").read_text(encoding="utf-8") == committed


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
