"""Contract pins for SDD's portable reviewer-context dispatch.

Task 3 of the cross-host review-gate hardening plan.  The orchestration
skill is prompt data, so these tests pin the required dispatch vocabulary:
one installed-plugin resolution per reviewer fan-out and unchanged packet
delivery to every spec, quality, or prose-review role.
"""

from __future__ import annotations

import re
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
SDD_SKILL = REPO_ROOT / "loom-code" / "skills" / "subagent-driven-development" / "SKILL.md"


def _normalized_skill() -> str:
    return re.sub(r"\s+", " ", SDD_SKILL.read_text(encoding="utf-8")).strip()


def test_sdd_reviewer_dispatch_carries_portable_context_packet() -> None:
    """Every reviewer fan-out resolves exactly one immutable portable packet."""
    text = _normalized_skill()

    assert 'review_context.py" --repo <target_repo>' in text
    assert "once per reviewer fan-out" in text
    assert "unchanged immutable context packet" in text

    for field in ("target_repo", "reviewed_sha", "plugin_version", "resources"):
        assert field in text

    for role in ("spec-reviewer", "code-quality-reviewer", "docs-reviewer"):
        assert role in text

    assert "approved absolute paths" in text
    assert "never derive plugin paths from `target_repo`" in text
    assert "The docs-reviewer receives the same immutable packet" in text
    assert "`git diff <base>..<reviewed_sha>`" not in text
    assert "paths at `<reviewed_sha>`" in text
    assert "changed-artifact list and diff scope are the ones at `<reviewed_sha>`" in text
    assert "through the active host adapter" in text
    assert "${CLAUDE_PLUGIN_ROOT}/scripts/review_context.py" not in text


def test_sdd_dispatch_uses_sha_bound_scope_and_cross_reads() -> None:
    """Every SDD reviewer receives only snapshot-bound review evidence."""
    text = _normalized_skill()

    assert '"<review_scope>" --repo <target_repo> --reviewed-sha <reviewed_sha>' in text
    assert "approved packet resource `review_scope`" in text
    assert "immutable repository citation cross-read contract" in text
    assert '`git -C "<target_repo>" show <reviewed_sha>:<path>`' in text
    assert "every spec-reviewer, code-quality-reviewer, and docs-reviewer prompt" in text
    assert "Do not use mutable working-tree reads for reviewer evidence." in text
    assert "If review_scope exits non-zero, REFUSE the fan-out" in text
    assert "do not dispatch any reviewer" in text
    assert "only reviewer artifact scope is the file list printed by review_scope" in text
