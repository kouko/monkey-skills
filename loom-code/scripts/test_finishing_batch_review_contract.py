"""Regression guard for REQ-110's Batch-versus-branch review boundary.

Batch review is an implementation checkpoint.  This test pins the separate
close-out path that starts after SDD has completed every plan Task, so a green
Batch receipt cannot be treated as a substitute for cumulative review.
"""

from __future__ import annotations

import re
from pathlib import Path


SKILLS = Path(__file__).resolve().parents[1] / "skills"
FINISHING = SKILLS / "finishing-a-development-branch" / "SKILL.md"
REQUESTING = SKILLS / "requesting-code-review" / "SKILL.md"
SDD = SKILLS / "subagent-driven-development" / "SKILL.md"


def _read(path: Path) -> str:
    assert path.is_file(), f"required close-out contract is absent: {path}"
    return path.read_text(encoding="utf-8")


def _between(text: str, start: str, end: str) -> str:
    start_at = text.index(start)
    end_at = text.index(end, start_at + len(start))
    assert start_at < end_at
    return text[start_at:end_at]


def _normalized(text: str) -> str:
    return re.sub(r"\s+", " ", text).strip()


def test_batch_pass_does_not_skip_whole_branch_review() -> None:
    """A completed Batch still enters fresh, authoritative branch review."""
    # @req: REQ-110
    finishing = _read(FINISHING)
    requesting = _read(REQUESTING)
    sdd = _read(SDD)

    # A Batch pass makes its member Tasks done; it does not select a separate
    # close-out route.  The all-Tasks-complete hand-off must still enter the
    # ordinary finishing flow, whose first gate is requesting-code-review.
    batch_checkpoint = _between(
        sdd, "**Batch review checkpoint.**", "**Progress ledger.**"
    )
    batch_checkpoint_norm = _normalized(batch_checkpoint)
    assert "finalize" in batch_checkpoint_norm
    assert "every member's `implemented(<sha>)` to `done(<same-sha>)`" in (
        batch_checkpoint_norm
    )

    sdd_pause_points = _between(sdd, "Pause points the user", "Everything else")
    assert "After all tasks `DONE`" in sdd_pause_points
    assert "finishing-a-development-branch" in sdd_pause_points
    assert "review + verification + push + PR-open" in sdd_pause_points

    flow = _between(finishing, "```\nfinishing-a-development-branch", "```")
    phase_1 = flow.index("Phase 1: requesting-code-review")
    phase_2 = flow.index("Phase 2: verification-before-completion")
    push = flow.index("Phase 5: git push")
    pull_request = flow.index("Phase 6: gh pr create")
    assert phase_1 < phase_2 < push
    assert phase_2 < pull_request

    # The branch reviewer must derive a fresh immutable context and cumulative
    # scope.  A Task/Batch receipt is therefore not an accepted scope source.
    process = _between(requesting, "## Process", "## Verdict structure")
    first_step = _between(
        process,
        "1. **Determine diff scope, then route by file type**",
        "2. **Resolve the dispatch profile**",
    )
    first_step_norm = _normalized(first_step)
    for required in (
        "review_scope.py",
        "reviewed_sha",
        "A stale base, or any failure to establish freshness, REFUSES",
    ):
        assert required in first_step_norm, f"fresh branch scope lost: {required}"

    docs_only = _between(first_step, "**Docs-only branch**", "**Mixed branch**")
    assert "requesting-docs-review" in docs_only
    assert "whole-artifact scope" in docs_only

    # A mixed branch joins the code and docs arms at the branch boundary.  This
    # exact Step-1 neighborhood is the cross-skill authority that prevents a
    # passing Batch/code receipt from erasing a later docs finding.
    mixed_branch = _between(first_step, "**Mixed branch**", "**Code-only branch**")
    mixed_branch_norm = _normalized(mixed_branch)
    assert "orchestrator unions both arms' findings" in mixed_branch_norm
    assert "branch verdict is the WORSE of the two arm verdicts" in mixed_branch_norm
    assert "either arm `NEEDS_REVISION` → branch `NEEDS_REVISION`" in mixed_branch_norm

    # The later cumulative verdict remains authoritative at close-out.
    closeout_step_3 = _between(
        finishing,
        "3. Dispatch requesting-code-review",
        "4. Before applying any review findings from Step 3",
    )
    assert "NEEDS_REVISION" in closeout_step_3
    assert "do NOT push" in closeout_step_3
    assert "fix → re-review" in closeout_step_3
