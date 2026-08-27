"""Mechanical marker-grep tests for the loom-memory same-branch timing rule.

Pins two invariants: the charter states the rule, and
finishing-a-development-branch points at it without copying the rule
body (pointer-not-copy).

Source: docs/loom/specs/2026-07-08-loom-memory-same-branch-timing.md
"""

import re
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]

MEMORY_README = REPO_ROOT / "docs/loom/memory/README.md"
FINISHING_SKILL = REPO_ROOT / "loom-code/skills/finishing-a-development-branch/SKILL.md"


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _norm(text: str) -> str:
    return re.sub(r"\s+", " ", text).strip()


def _when_to_record_section(text: str) -> str:
    """Body of the charter's `## When to record` section: from the heading
    to the next `## ` heading or EOF. `docs/loom/memory/README.md` is a
    ~400-line index of many unrelated entries -- "post-merge" alone occurs
    several other places in it (other entries' own topics), so a whole-file
    substring check on that word would stay green even if this section were
    deleted entirely (a false green per B1 hard rule 2). Narrowed to the
    section window instead."""
    start = text.index("## When to record")
    rest = text[start + len("## When to record"):]
    end = rest.find("\n## ")
    return _norm(rest if end == -1 else rest[:end])


def test_charter_has_when_to_record_section():
    """
    The charter (docs/loom/memory/README.md) must gain a `## When to
    record` section stating the same-branch timing rule.
    """
    text = _read(MEMORY_README)
    assert "## When to record" in text
    body = _when_to_record_section(text)
    assert "same branch" in body
    assert "post-merge" in body


def test_finishing_branch_points_at_when_to_record():
    """
    finishing-a-development-branch/SKILL.md Step 8 must point at the
    charter's new section (pointer only) — it must NOT restate the
    charter's rule body (pointer-not-copy).

    The duplication guard is extracted from the charter's LIVE text rather
    than hardcoded: a hardcoded phrase can silently desync from the
    charter's actual wording (this file's own hardcoded "never a separate
    post-merge branch" never matched the charter verbatim to begin with —
    the charter wraps it "post-merge\\nbranch" across a line break) and,
    unnarrowed, only catches ONE literal paraphrase of the rule body while
    missing any other duplication of the same content.
    """
    charter_body = _when_to_record_section(_read(MEMORY_README))
    text = _read(FINISHING_SKILL)
    assert "docs/loom/memory/README.md" in text
    assert "When to record" in text
    # A short, distinctive fragment pulled straight from the charter's own
    # normalized body -- if the charter's phrasing ever changes, this guard
    # tracks it automatically instead of drifting out of sync.
    assert "never a separate post-merge branch" in charter_body, (
        "test fixture assumption: the charter must still state the rule "
        "this way -- if this fails, the charter's wording changed and the "
        "duplication-guard fragment below should be updated to match"
    )
    assert "never a separate post-merge branch" not in _norm(text)
