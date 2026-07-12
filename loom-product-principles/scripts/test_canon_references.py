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


def _framing(name: str) -> str:
    """Return the file's framing header (prose above the table), flattened.

    Markdown emphasis stripped and whitespace collapsed, so an assertion can
    pin a phrase that the source wraps across physical lines (the
    doctrine-body test caps every prose line at 400 chars).
    """
    text = _text(name)
    header = text.split("| Entry", 1)[0]
    header = re.sub(r"[*_`]", "", header)
    return re.sub(r"\s+", " ", header).lower()


def test_visual_canon_framed_as_downstream_mood_inspiration():
    """Axis A is stage-3 mood inspiration under the tone & manner anchor.

    Industry practice anchors visual direction on values -> 3-5 tone & manner
    adjectives; art movements are downstream mood/creative-direction input,
    not a formal selection criterion (brief 2026-07-12 §Research). Framing
    Axis A as a co-equal pick-one menu over-claims convention — it is the
    shape of the original costume-menu bug. The framing must therefore say:
    (a) it is downstream of the tone & manner anchor, (b) it supplies
    mood/creative-direction inspiration and is NOT a pick-one menu, and
    (c) the general anti-costume law — a movement never overrides a
    PRINCIPLES value — with the Memphis case as its worked example.
    """
    framing = _framing("canon-design-visual.md")

    assert "tone & manner" in framing, (
        "canon-design-visual.md framing must name the tone & manner "
        "adjective anchor as the primary visual anchor it sits under"
    )
    assert "downstream of the tone & manner anchor" in framing, (
        "canon-design-visual.md framing must state Axis A is downstream of "
        "the tone & manner anchor, not a co-equal anchoring axis"
    )
    assert "mood / creative-direction inspiration" in framing, (
        "canon-design-visual.md framing must state Axis A supplies mood / "
        "creative-direction inspiration (stage-3 input)"
    )
    assert "never a pick-one menu" in framing, (
        "canon-design-visual.md framing must state Axis A is never a "
        "pick-one menu — that framing is the costume-menu bug"
    )
    assert "anti-costume law" in framing, (
        "canon-design-visual.md framing must state the anti-costume law as "
        "a general law, not a one-off Memphis example"
    )
    assert "never overrides a principles value" in framing, (
        "the anti-costume law must say a movement may enrich candidates but "
        "never overrides a PRINCIPLES value"
    )
    assert "memphis" in framing, (
        "the anti-costume law must carry the low-stimulus/Memphis case as "
        "its worked example"
    )


CULTURE_REGION_ENTRIES = [
    "Pop Art",        # Euro-American
    "Ukiyo-e",        # Japan
    "Socialist Realism",  # Soviet
    "Dunhuang",       # Greater China
]

COSTUME_RISK_ENTRIES = [
    "Cyberpunk",
    "Vaporwave",
    "City Pop",
    "Socialist Realism",
    "Cultural-Revolution",
    "Guochao",
]

PROPAGANDA_ORIGIN_ENTRIES = ["Socialist Realism", "Cultural-Revolution"]


def _row_by_entry(rows: list[str], needle: str) -> str:
    """Return the single table row whose FIRST cell (Entry) names `needle`.

    Matching on the Entry cell, not the whole row, keeps a cross-reference in
    another row's fits-when hint (the Cultural-Revolution row cites Soviet
    Socialist Realism by name) from colliding with the entry it references.
    """
    matches = [
        row for row in rows
        if needle.lower() in row.strip("|").split("|")[0].lower()
    ]
    assert len(matches) == 1, (
        f"expected exactly one canon entry named {needle!r}; got {len(matches)}"
    )
    return matches[0]


def test_visual_canon_covers_culture_regions_and_flags_costume_risk():
    """Axis A must span art/subculture + non-Western traditions, safely.

    The canon was Western professional-graphic-design history plus two Japan
    rows — which starves the divergent-candidate mechanism it exists to feed
    (brief 2026-07-12 §Axis A expansion). Breadth here is not decoration: a
    candidate the agent cannot recall is a candidate it cannot diverge toward.

    But breadth raises costume risk, so the widening is conditional on the
    guard travelling WITH it: the six high-risk entries carry a per-row
    anti-costume caveat (the framing law alone is too far from the row an
    agent actually reads), and the two propaganda-origin entries additionally
    bound the borrowing to formal vocabulary only — never the propaganda
    freight.
    """
    rows = _table_data_rows(_text("canon-design-visual.md"))

    for entry in CULTURE_REGION_ENTRIES:
        _row_by_entry(rows, entry)

    for entry in COSTUME_RISK_ENTRIES:
        row = _row_by_entry(rows, entry).lower()
        assert "costume risk" in row, (
            f"high-costume-risk entry {entry!r} must carry a per-row "
            "anti-costume caveat, not rely on the framing law alone"
        )

    for entry in PROPAGANDA_ORIGIN_ENTRIES:
        row = _row_by_entry(rows, entry).lower()
        assert "formal visual vocabulary only" in row, (
            f"propaganda-origin entry {entry!r} must bound the borrowing to "
            "its formal visual vocabulary"
        )
        assert "never the propaganda freight" in row, (
            f"propaganda-origin entry {entry!r} must state that the "
            "propaganda freight is never borrowed"
        )

    # Lineage is evidence-bounded: the sources license descent-then-divergence
    # (Soviet academy training 1949-57, then the doctrinal break into 紅光亮),
    # NOT a bare "regional variant" — that overstates continuity (brief
    # §Lineage note).
    cr_row = _row_by_entry(rows, "Cultural-Revolution")
    assert "descended from Soviet Socialist Realism" in cr_row, (
        "the Cultural-Revolution row must use the source-licensed "
        "descent-then-divergence wording"
    )
    assert "variant" not in cr_row.lower(), (
        "the Cultural-Revolution row must not call the style a 'variant' of "
        "Socialist Realism — the sources record a doctrinal break"
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
