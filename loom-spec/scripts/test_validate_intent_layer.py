"""Tests for the intent-layer (TOP MODEL.md) structural validator.

The intent layer's persistent root carries a TOP-altitude MODEL.md whose
required canonical sections are the cross-cutting model: Invariants, Object
state machines, Out of scope. `check_top_model` grades a MODEL.md that
EXISTS (absence is handled by the aggregator elsewhere).
"""

from __future__ import annotations

from pathlib import Path

from validate_intent_layer import check_top_model

_ALL_SECTIONS = (
    "## Invariants\n\nThe ledger total never goes negative.\n\n"
    "## Object state machines\n\nDraft -> Active -> Archived.\n\n"
    "## Out of scope\n\nMulti-tenant billing.\n"
)


def test_top_model_missing_section_reported(tmp_path: Path) -> None:
    # A MODEL.md missing exactly one required section yields exactly one
    # problem naming that section.
    (tmp_path / "MODEL.md").write_text(
        "## Invariants\n\nNo negative balances.\n\n"
        "## Out of scope\n\nBilling.\n",
        encoding="utf-8",
    )
    problems = check_top_model(tmp_path)
    assert len(problems) == 1
    assert "## Object state machines" in problems[0]
    assert "MODEL.md" in problems[0]


def test_top_model_all_sections_ok(tmp_path: Path) -> None:
    (tmp_path / "MODEL.md").write_text(_ALL_SECTIONS, encoding="utf-8")
    assert check_top_model(tmp_path) == []


def test_top_model_section_only_in_prose_does_not_count(tmp_path: Path) -> None:
    # 'Out of scope' appears only inside prose, never as a `## ` header line,
    # so it must NOT satisfy the check (whole-header-line match).
    (tmp_path / "MODEL.md").write_text(
        "## Invariants\n\nNo negatives.\n\n"
        "## Object state machines\n\nDraft -> Active.\n\n"
        "Note: anything ## Out of scope here is just prose, not a header.\n",
        encoding="utf-8",
    )
    problems = check_top_model(tmp_path)
    assert len(problems) == 1
    assert "## Out of scope" in problems[0]


def test_top_model_absent_returns_empty(tmp_path: Path) -> None:
    # No MODEL.md -> absence handled by aggregator; this check returns [].
    assert check_top_model(tmp_path) == []
