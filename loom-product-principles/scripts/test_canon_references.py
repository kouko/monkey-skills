"""Structural grep-test guarding the four agent-facing canon base lists.

These four files are recall insurance against LLM popularity bias when the
product-principles skill proposes canon candidates at the propose-candidates
step (docs/loom/design/2026-07-10-designer-pm-loop-architecture.md §4). They
are agent-facing only — never shown raw to the user — so the structural
contract this test enforces is:

  - each of the four files exists under references/ (flat, no subfolders);
  - each states "including but not limited to" (the agent-facing/breadth
    framing, not a closed menu);
  - each names its popularity-head entries (the ones an LLM over-proposes
    without this audit), so the agent knows what to look past;
  - each carries >=14 entries, and every entry row carries a source URL
    (name + fits-when + stability alone, with no citable source, is not
    enough to counter popularity bias).

No REQ-ids are registered for this dispatch; @req tags are intentionally
omitted per the implementer contract.

Stdlib + pytest only, path-based. Resolve references/ relative to this file.
"""

import re
from pathlib import Path

import pytest

REFERENCES_DIR = (
    Path(__file__).parents[1]
    / "skills"
    / "product-principles"
    / "references"
)

CANON_FILES = [
    "canon-product.md",
    "canon-design-interaction.md",
    "canon-design-visual.md",
    "canon-engineering.md",
]

MIN_ENTRIES = 14
LINK_RE = re.compile(r"\]\(https?://[^)]+\)")
_SEPARATOR_CELL_RE = re.compile(r":?-{2,}:?")


def _text(name: str) -> str:
    path = REFERENCES_DIR / name
    assert path.is_file(), f"{name} is absent at {path}"
    return path.read_text(encoding="utf-8")


def _table_data_rows(text: str) -> list[str]:
    """Return markdown table data rows (header + separator rows excluded).

    Walks line-by-line: a pipe-delimited separator row (---|---|---) flips
    'inside a table body' on; any subsequent non-pipe line flips it back off
    (so a header row, which precedes the separator, is never counted).
    """
    rows: list[str] = []
    in_body = False
    for raw_line in text.splitlines():
        line = raw_line.strip()
        if line.startswith("|") and line.endswith("|"):
            cells = [c.strip() for c in line.strip("|").split("|")]
            if all(_SEPARATOR_CELL_RE.fullmatch(c) for c in cells):
                in_body = True
                continue
            if in_body:
                rows.append(line)
        else:
            in_body = False
    return rows


@pytest.mark.parametrize("name", CANON_FILES)
def test_canon_file_exists(name):
    _text(name)


@pytest.mark.parametrize("name", CANON_FILES)
def test_canon_file_states_including_but_not_limited_to(name):
    text = _text(name)
    assert "including but not limited to" in text.lower(), (
        f"{name} must state 'including but not limited to' — this is a "
        "breadth audit list, not a closed menu"
    )


@pytest.mark.parametrize("name", CANON_FILES)
def test_canon_file_names_popularity_head(name):
    text = _text(name)
    assert "popularity head" in text.lower(), (
        f"{name} must name its popularity-head entries so the agent knows "
        "which candidates to look past"
    )


@pytest.mark.parametrize("name", CANON_FILES)
def test_canon_file_has_at_least_14_entries_each_with_url(name):
    text = _text(name)
    rows = _table_data_rows(text)
    assert len(rows) >= MIN_ENTRIES, (
        f"{name} has {len(rows)} table entries; need >= {MIN_ENTRIES}"
    )
    for row in rows:
        assert LINK_RE.search(row), (
            f"{name} entry row missing a source URL: {row}"
        )


def test_visual_canon_is_axis_a_only():
    """canon-design-visual.md is Axis A (cultural/graphic movements) only.

    The collapsed surface-treatment row ("Flat -> skeuo -> neumorphic ->
    glassmorphic cycle") duplicated content whose expanded home is now
    canon-design-surface.md — it must be gone from this file, and this
    file must point agents at canon-design-surface.md for UI surface
    treatments (docs/loom/plans/2026-07-12-visual-style-movement-anchor-
    and-quality-separation.md, Task 3)."""
    text = _text("canon-design-visual.md")
    assert "glassmorphic cycle" not in text, (
        "canon-design-visual.md must not contain the collapsed "
        "surface-treatment row; its expanded home is canon-design-surface.md"
    )
    assert "canon-design-surface.md" in text, (
        "canon-design-visual.md must point to canon-design-surface.md "
        "for UI surface treatments (Axis A vs surface-treatment split)"
    )


@pytest.mark.parametrize("name", CANON_FILES)
def test_canon_file_has_no_doctrine_body(name):
    """Entries carry name + fits-when + stability + source only — doctrine
    content stays in the model (copying it re-acquires the canon-copy
    maintenance liability the research note flags)."""
    text = _text(name)
    # A doctrine body would show up as prose paragraphs outside the table
    # and popularity-head note; guard against accidental essay-length
    # sections by capping non-table, non-header line length.
    for raw_line in text.splitlines():
        line = raw_line.strip()
        if line.startswith("|") or line.startswith("#") or not line:
            continue
        assert len(line) <= 400, (
            f"{name} has a long prose line ({len(line)} chars) outside the "
            f"table — looks like doctrine content, not a fits-when hint: "
            f"{line[:80]}..."
        )
