"""Tests for the intent-layer (TOP MODEL.md) structural validator.

The intent layer's persistent root carries a TOP-altitude MODEL.md whose
required canonical sections are the cross-cutting model: Invariants, Object
state machines, Out of scope. `check_top_model` grades a MODEL.md that
EXISTS (absence is handled by the aggregator elsewhere).
"""

from __future__ import annotations

from pathlib import Path

from validate_intent_layer import (
    check_mid_readmes,
    check_top_model,
    main,
    validate,
)

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


def test_mid_capability_without_readme_reported(tmp_path: Path) -> None:
    # A capability dir lacking the MID README.md yields exactly one problem
    # naming that capability; a sibling capability WITH a README.md yields none.
    (tmp_path / "order").mkdir()
    documented = tmp_path / "payment"
    documented.mkdir()
    (documented / "README.md").write_text("# Payment\n", encoding="utf-8")
    problems = check_mid_readmes(tmp_path)
    assert len(problems) == 1
    assert "order" in problems[0]
    assert str(tmp_path / "order") in problems[0]


def test_mid_all_capabilities_documented_ok(tmp_path: Path) -> None:
    for cap in ("order", "payment"):
        d = tmp_path / cap
        d.mkdir()
        (d / "README.md").write_text(f"# {cap}\n", encoding="utf-8")
    assert check_mid_readmes(tmp_path) == []


def test_mid_no_capability_subdirs_returns_empty(tmp_path: Path) -> None:
    # A spec_dir with no immediate sub-directories -> [].
    (tmp_path / "MODEL.md").write_text("## Invariants\n", encoding="utf-8")
    assert check_mid_readmes(tmp_path) == []


def test_mid_nonexistent_spec_dir_returns_empty(tmp_path: Path) -> None:
    # A non-existent spec_dir -> [] (aggregator's concern).
    assert check_mid_readmes(tmp_path / "does-not-exist") == []


# --- aggregator: validate() composes the two checks + absent-layer tolerance --

def test_absent_layer_is_ok(tmp_path: Path) -> None:
    # spec_dir that does not exist -> the intent layer simply isn't adopted yet;
    # NOT an error (mirrors the ui-flows "if absent, ignore" seam stance).
    ok, problems = validate(tmp_path / "does-not-exist")
    assert ok is True
    assert problems == []


def test_empty_layer_is_ok(tmp_path: Path) -> None:
    # spec_dir exists but has no MODEL.md and no capability subdirs ->
    # mid-adoption repo with no intent layer yet; NOT an error.
    ok, problems = validate(tmp_path)
    assert ok is True
    assert problems == []


def test_nonempty_layer_without_model_md_is_error(tmp_path: Path) -> None:
    # A capability dir present (layer is in use) but MODEL.md absent: the TOP
    # model is required once the layer exists. check_top_model alone returns []
    # on absence, so the aggregator MUST add this presence problem.
    cap = tmp_path / "order"
    cap.mkdir()
    (cap / "README.md").write_text("# Order\n", encoding="utf-8")
    ok, problems = validate(tmp_path)
    assert ok is False
    assert any("MODEL.md" in p for p in problems)


def test_nonempty_layer_surfaces_both_problems(tmp_path: Path) -> None:
    # A defective MODEL.md (missing a TOP section) AND a capability missing its
    # README -> the aggregate surfaces BOTH problems.
    (tmp_path / "MODEL.md").write_text(
        "## Invariants\n\nNo negatives.\n\n"
        "## Out of scope\n\nBilling.\n",
        encoding="utf-8",
    )
    (tmp_path / "order").mkdir()  # capability dir lacking README.md
    ok, problems = validate(tmp_path)
    assert ok is False
    assert any("## Object state machines" in p for p in problems)
    assert any("README.md" in p and "order" in p for p in problems)


def test_well_formed_layer_is_ok(tmp_path: Path) -> None:
    # MODEL.md with all 3 TOP sections + every capability has a README -> ok.
    (tmp_path / "MODEL.md").write_text(_ALL_SECTIONS, encoding="utf-8")
    for cap in ("order", "payment"):
        d = tmp_path / cap
        d.mkdir()
        (d / "README.md").write_text(f"# {cap}\n", encoding="utf-8")
    ok, problems = validate(tmp_path)
    assert ok is True
    assert problems == []


def test_main_exits_zero_on_clean_layer(tmp_path: Path) -> None:
    (tmp_path / "MODEL.md").write_text(_ALL_SECTIONS, encoding="utf-8")
    cap = tmp_path / "order"
    cap.mkdir()
    (cap / "README.md").write_text("# Order\n", encoding="utf-8")
    assert main([str(tmp_path)]) == 0


def test_main_exits_one_on_problems(tmp_path: Path) -> None:
    cap = tmp_path / "order"
    cap.mkdir()
    (cap / "README.md").write_text("# Order\n", encoding="utf-8")  # no MODEL.md
    assert main([str(tmp_path)]) == 1
