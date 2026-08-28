"""Contract pins for SDD's portable reviewer-context dispatch.

Task 3 of the cross-host review-gate hardening plan.  The orchestration
skill is prompt data, so these tests pin the required dispatch vocabulary:
one installed-plugin resolution per reviewer fan-out and unchanged packet
delivery to every spec, quality, or prose-review role.
"""

from __future__ import annotations

import re
from pathlib import Path

from heading_window import line_leading as _line_leading


REPO_ROOT = Path(__file__).resolve().parents[2]
SDD_SKILL = REPO_ROOT / "loom-code" / "skills" / "subagent-driven-development" / "SKILL.md"


def _normalized_skill() -> str:
    return re.sub(r"\s+", " ", SDD_SKILL.read_text(encoding="utf-8")).strip()


def test_sdd_reviewer_dispatch_carries_portable_context_packet() -> None:
    """Every reviewer fan-out resolves exactly one immutable portable packet."""
    text = _normalized_skill()

    assert 'review_context.py" --repo <target_repo>' in text

    # How the root is resolved, how many times the resolver runs, and how
    # the result travels are three separate things an orchestrator DOES.
    # Pinned as rule-carrying tokens inside the acquisition clause rather
    # than as whole sentences.
    packet_clause = text[
        text.index("resolve the installed root") : text.index(
            "Write the packet JSON to a file"
        )
    ]
    assert "host adapter" in packet_clause
    assert "once per reviewer fan-out" in packet_clause
    assert "verbatim" in packet_clause

    for field in ("target_repo", "reviewed_sha", "plugin_version", "resources"):
        assert field in text

    for role in ("spec-reviewer", "code-quality-reviewer", "docs-reviewer"):
        assert role in text

    assert "approved absolute paths" in text
    assert "never derive plugin paths from `target_repo`" in text
    assert "`git diff <base>..<reviewed_sha>`" not in text
    assert "paths at `<reviewed_sha>`" in text
    assert "changed-artifact list and diff scope are the ones at `<reviewed_sha>`" in text
    assert "${CLAUDE_PLUGIN_ROOT}/scripts/review_context.py" not in text

    # The docs-reviewer "receives the same immutable packet" -- the real
    # invariant is that it does not re-derive its own scope: no second
    # review_context.py invocation inside the Prose-substitution clause.
    substitution = text[
        text.index("Prose review-weight substitution") : text.index(
            "Record-class scope narrowing"
        )
    ]
    assert "review_context.py" not in substitution


def test_sdd_dispatch_uses_sha_bound_scope_and_cross_reads() -> None:
    """Every SDD reviewer receives only snapshot-bound review evidence."""
    text = _normalized_skill()

    cross_read_cmd = '`git -C "<target_repo>" show <reviewed_sha>:<path>`'
    assert cross_read_cmd in text
    assert (
        "only reviewer artifact scope is the repository-relative file list "
        "declared in the task packet's `Files touched` field"
    ) in text

    # All three reviewer roles must be handed the cross-read contract --
    # narrowed to the clause that introduces it, not whole-file presence.
    give_window = text[
        text.index("Give every") : text.index(cross_read_cmd) + len(cross_read_cmd)
    ]
    for role in ("spec-reviewer", "code-quality-reviewer", "docs-reviewer"):
        assert role in give_window

    # A missing file at <reviewed_sha> REFUSES the fan-out -- pin the
    # control keyword inside the window it governs, not whole-file text.
    cat_file_check = 'git -C "<target_repo>" cat-file -e "<reviewed_sha>:<path>"'
    refuse_window = text[
        text.index(cat_file_check) : text.index(
            "Do not run", text.index(cat_file_check)
        )
    ]
    assert "REFUSES" in refuse_window

    # The positive pins above say what reviewers MUST read (the snapshot
    # command, at <reviewed_sha>). None of them forbids ALSO reading the
    # mutable working tree, which is the way the evidence rule actually
    # fails -- an agent that runs the git-show command and then reads the
    # worktree anyway satisfies every assertion above. This prohibition is
    # its own invariant and is pinned separately.
    assert "Do not use mutable working-tree reads for reviewer evidence." in text


def test_sdd_per_task_reviewer_scope_uses_declared_task_files() -> None:
    """A task triad must review its own declared files, never branch scope."""
    skill = SDD_SKILL.read_text(encoding="utf-8")
    # Anchor at a line start so a same-named `###` subheading earlier in
    # the file can't retarget this window.
    _proc_heading = "## Process — per-task triad"
    _proc_start = _line_leading(skill, _proc_heading)
    assert _proc_start != -1, f"expected {_proc_heading!r} heading"
    process = skill[_proc_start:skill.index("**Parallel dispatch")]
    step1 = process[process.index("1. **Dispatch"):process.index("2. **Read")]
    step3 = process[process.index("3. **If"):process.index("4. **Resolve")]

    assert "plan task's existing `Files touched` declaration unchanged into the task packet" in step1
    assert "task packet's `Files touched` field" in step3
    assert "only reviewer artifact scope" in step3
    assert "non-empty repository-relative `Files touched` list" in step3
    assert "otherwise REFUSE the fan-out" in step3
    assert 'git -C "<target_repo>" cat-file -e "<reviewed_sha>:<path>"' in step3
    assert 'python3 "<review_scope>"' not in step3
