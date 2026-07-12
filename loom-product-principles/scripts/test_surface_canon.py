"""Structural grep-test guarding the UI surface-treatments research doc.

This doc grounds the ~6 UI surface-treatment paradigms (skeuomorphism, flat,
material-as-surface-treatment, neumorphism, glassmorphism, spatial / Liquid
Glass) that a later task's Axis-B canon file will cite — mirroring how
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

import pytest

REPO_ROOT = Path(__file__).parents[2]
RESEARCH_DOC = (
    REPO_ROOT / "docs" / "loom" / "research"
    / "2026-07-12-ui-surface-treatments-canon.md"
)

MIN_SOURCE_LINKS = 5
MIN_YEAR_TOKENS = 5
LINK_RE = re.compile(r"https?://\S+")
YEAR_RE = re.compile(r"\b(19|20)\d{2}\b")

SEED_TREATMENT_NAMES = [
    "skeuomorphism",
    "flat",
    "material",
    "neumorphism",
    "glassmorphism",
    "spatial",
]


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
