"""Structural grep-test guarding the Axis-B UI surface-treatment canon.

The canon lives in this plugin because a surface treatment is a stage-4
design-language sub-decision — it is picked at the DESIGN stage, downstream
of the PRINCIPLES-stage tone & manner anchor. (It previously sat in
loom-product-principles with a forward-note recording the mis-placement;
this file is its home now.)

Two guards:
  - the canon file's own contract (extensible framing, agent-facing framing,
    the Currency column, a WCAG risk flag, a per-row source URL);
  - the repo-level research doc that grounds it — mirroring how
    canon-design-visual.md cites its own grounding doc. House discipline:
    "ground in sources before cataloging."

No REQ-ids are registered for this dispatch; @req tags are intentionally
omitted per the implementer contract.

Stdlib + pytest only, path-based. The canon resolves inside this plugin;
the research doc resolves at the repo root (loom-interface-design/scripts/
-> repo root -> docs/loom/research/).
"""

import re
from pathlib import Path

REPO_ROOT = Path(__file__).parents[2]
RESEARCH_DOC = (
    REPO_ROOT / "docs" / "loom" / "research"
    / "2026-07-12-ui-surface-treatments-canon.md"
)

MIN_SOURCE_LINKS = 5
MIN_YEAR_TOKENS = 5
LINK_RE = re.compile(r"https?://\S+")
YEAR_RE = re.compile(r"\b(?:19|20)\d{2}\b")

SEED_TREATMENT_NAMES = [
    "skeuomorphism",
    "flat",
    "material",
    "neumorphism",
    "glassmorphism",
    "spatial",
]

SURFACE_CANON = (
    Path(__file__).parents[1]
    / "skills"
    / "design-system"
    / "references"
    / "canon-design-surface.md"
)

# Raised from the 5-row relocation floor once the catalog was grown to the
# full era cycle (6 seed rows + the 12 researched expansion candidates).
MIN_SURFACE_ROWS = 15
ROW_LINK_RE = re.compile(r"\]\(https?://[^)]+\)")
_SEPARATOR_CELL_RE = re.compile(r":?-{2,}:?")

# One row per treatment — pinned as EXACTLY one match apiece, which also
# encodes the research doc's finding that Frutiger Aero's 2023- revival is a
# Currency-cell update, NOT a second row.
EXPANSION_ENTRY_NAMES = [
    "geocities",
    "gel",
    "frutiger aero",
    "long-shadow",
    "dark mode",
    "aurora",
    "claymorphism",
    "material you",
    "neubrutalism",
    "retro-terminal",
    "anti-design",
    "bento",
]

# The six entries the research doc's "WCAG risk flags" subsection names.
# Each must carry the flag in its OWN row — a reader picking a candidate
# reads the row, not the prose below the table.
WCAG_FLAGGED_ENTRIES = [
    "dark mode",
    "material you",
    "aurora",
    "claymorphism",
    "neubrutalism",
    "anti-design",
]


def _surface_table_data_rows(text: str) -> list[str]:
    """Return markdown table data rows (header + separator rows excluded).

    Mirrors test_canon_references.py's _table_data_rows: a pipe-delimited
    separator row (---|---|---) flips 'inside a table body' on; any
    subsequent non-pipe line flips it back off.
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


def test_surface_canon_file_contract():
    assert SURFACE_CANON.is_file(), (
        f"canon-design-surface.md absent at {SURFACE_CANON}"
    )
    text = SURFACE_CANON.read_text(encoding="utf-8")
    lower = text.lower()

    assert "including but not limited to" in lower, (
        "canon-design-surface.md must state 'including but not limited to' "
        "— extensible framing, not a closed menu"
    )
    assert "never shown raw to the user" in lower, (
        "canon-design-surface.md must state 'never shown raw to the user' "
        "— agent-facing framing"
    )
    assert "2026-07-12-ui-surface-treatments-canon" in text, (
        "canon-design-surface.md must cite the grounding research doc path"
    )
    assert "wcag" in lower, (
        "canon-design-surface.md must carry >=1 risk-flag note mentioning "
        "WCAG (e.g. neumorphism's low-contrast risk)"
    )

    # Find the table header row containing "Currency" as a column, in
    # addition to Entry / Fits when.../ Stability / Source.
    header_lines = [
        raw_line.strip()
        for raw_line in text.splitlines()
        if raw_line.strip().startswith("|") and raw_line.strip().endswith("|")
    ]
    currency_header = next(
        (
            line
            for line in header_lines
            if "currency" in line.lower() and "entry" in line.lower()
        ),
        None,
    )
    assert currency_header is not None, (
        "canon-design-surface.md table header must include a 'Currency' "
        "column alongside Entry / Fits when… / Stability / Source"
    )

    rows = _surface_table_data_rows(text)
    assert len(rows) >= MIN_SURFACE_ROWS, (
        f"canon-design-surface.md has {len(rows)} table entries; "
        f"need >= {MIN_SURFACE_ROWS}"
    )
    for row in rows:
        assert ROW_LINK_RE.search(row), (
            f"canon-design-surface.md entry row missing a source URL: {row}"
        )


def _entry_cell(row: str) -> str:
    """First cell of a markdown table row — the treatment's own name.

    'One row per treatment' is a claim about the ENTRY column: another row's
    Currency cell may legitimately cross-reference a treatment (the Web 2.0
    gel row cites Frutiger Aero's shared era) without being a second row for
    it. Matching the whole row would mistake that prose for a duplicate.
    """
    return row.strip("|").split("|")[0].strip()


def test_surface_canon_covers_the_full_era_cycle():
    """The catalog spans the whole cycle, not just the 6 seed treatments.

    A 6-row canon cannot fuel a real 3-5 candidate round at the DESIGN
    stage — the popularity head (flat / Material) eats the whole set. This
    pins the 12 researched expansion candidates, one row apiece, each still
    source-linked, and each WCAG-risky entry flagging its risk IN ITS ROW.
    """
    text = SURFACE_CANON.read_text(encoding="utf-8")
    rows = _surface_table_data_rows(text)

    assert len(rows) >= MIN_SURFACE_ROWS, (
        f"canon-design-surface.md has {len(rows)} table entries; the full "
        f"era cycle needs >= {MIN_SURFACE_ROWS}"
    )

    for name in EXPANSION_ENTRY_NAMES:
        matches = [row for row in rows if name in _entry_cell(row).lower()]
        assert len(matches) == 1, (
            f"expansion entry {name!r} must name exactly one canon row's "
            f"Entry cell; found {len(matches)}"
        )
        assert ROW_LINK_RE.search(matches[0]), (
            f"expansion entry {name!r} row missing a markdown-link source "
            f"URL: {matches[0]}"
        )

    for name in WCAG_FLAGGED_ENTRIES:
        row = next(row for row in rows if name in _entry_cell(row).lower())
        assert "wcag" in row.lower(), (
            f"entry {name!r} carries a WCAG risk in the grounding research "
            f"doc; its canon row must flag it: {row}"
        )


def test_surface_research_doc_grounds_seed():
    assert RESEARCH_DOC.is_file(), f"research doc absent at {RESEARCH_DOC}"
    text = RESEARCH_DOC.read_text(encoding="utf-8")
    lower = text.lower()

    for name in SEED_TREATMENT_NAMES:
        assert name in lower, (
            f"seed surface-treatment name {name!r} not found in "
            f"{RESEARCH_DOC.name}"
        )

    links = LINK_RE.findall(text)
    assert len(links) >= MIN_SOURCE_LINKS, (
        f"{RESEARCH_DOC.name} has {len(links)} http(s) source links; "
        f"need >= {MIN_SOURCE_LINKS}"
    )

    years = YEAR_RE.findall(text)
    assert len(years) >= MIN_YEAR_TOKENS, (
        f"{RESEARCH_DOC.name} has {len(years)} four-digit year tokens; "
        f"need >= {MIN_YEAR_TOKENS} as currency evidence"
    )
