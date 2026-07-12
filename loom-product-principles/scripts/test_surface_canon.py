"""Structural grep-test guarding the UI surface-treatments research doc.

This doc grounds the ~6 UI surface-treatment paradigms (skeuomorphism, flat,
material-as-surface-treatment, neumorphism, glassmorphism, spatial / Liquid
Glass) that the Axis-B canon file cites — mirroring how
canon-design-visual.md cites
docs/loom/research/2026-07-10-principles-canon-base-lists.md §3. House
discipline: "ground in sources before cataloging."

No REQ-ids are registered for this dispatch; @req tags are intentionally
omitted per the implementer contract.

Stdlib + pytest only, path-based. Resolve the research doc relative to this
file (loom-product-principles/scripts/ -> repo root -> docs/loom/research/).
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
    REPO_ROOT
    / "loom-product-principles"
    / "skills"
    / "product-principles"
    / "references"
    / "canon-design-surface.md"
)

MIN_SURFACE_ROWS = 5
ROW_LINK_RE = re.compile(r"\]\(https?://[^)]+\)")
_SEPARATOR_CELL_RE = re.compile(r":?-{2,}:?")


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
        "canon-design-surface.md must cite the Task-1 grounding research "
        "doc path"
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
