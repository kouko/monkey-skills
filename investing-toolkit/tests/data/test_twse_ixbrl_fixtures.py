"""test_twse_ixbrl_fixtures.py — OFFLINE exact-fact-count regression guard
for the real financial-sector (fh) MOPS iXBRL fixtures.

These 7 fixtures are REAL producer bytes captured live from TWSE MOPS
(t164sb01 endpoint), Big5-encoded, verified live 2026-07. They mirror
the real financial-holding / bank / insurance / securities producer so
downstream taxonomy work is tested against producer-shaped data, never
hand-authored input. Provenance (co_id · period · source):

  2882 · 2026Q1 consolidated (C) · MOPS t164sb01 · verified live 2026-07
  2890 · 2026Q1 consolidated (C) · MOPS t164sb01 · verified live 2026-07
  2801 · 2026Q1 consolidated (C) · MOPS t164sb01 · verified live 2026-07
  2820 · 2026Q1 individual   (A) · MOPS t164sb01 · verified live 2026-07
  6005 · 2026Q1 consolidated (C) · MOPS t164sb01 · verified live 2026-07
  2867 · 2026Q1 individual   (A) · MOPS t164sb01 · verified live 2026-07
  2851 · 2025Q1 individual   (A) · MOPS t164sb01 · verified live 2026-07

Each EXPECTED_FACT_COUNTS value is the `fact_count` field from the
matching `<co_id>_<period>_<type>.profile.json` measured beside the raw
body at capture time (fh-measurement rounds). The exact-count assertion
(±0) is the DOM-drop regression tripwire: a naive DOM/tree-repair parse
silently drops facts nested inside <td> (measured on TSMC as 387 vs true
2002), so any drift from the measured count fails loud here.

Run offline (part of the default `not network` suite):
  PYTHONDONTWRITEBYTECODE=1 python3 -m pytest investing-toolkit/tests/ -q -m "not network"
"""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
MARKETS_SCRIPTS = ROOT / "skills" / "data-markets" / "scripts"
FIXTURES = Path(__file__).resolve().parent / "fixtures"

# fixture basename -> exact measured fact_count (source: the matching
# *.profile.json `fact_count` beside each captured body in the fh capture
# rounds; see module docstring for provenance).
EXPECTED_FACT_COUNTS = {
    "twse_ixbrl_2882_2026Q1_C.html": 1753,
    "twse_ixbrl_2890_2026Q1_C.html": 1326,
    "twse_ixbrl_2801_2026Q1_C.html": 1413,
    "twse_ixbrl_2820_2026Q1_A.html": 464,
    "twse_ixbrl_6005_2026Q1_C.html": 1644,
    "twse_ixbrl_2867_2026Q1_A.html": 649,
    "twse_ixbrl_2851_2025Q1_A.html": 477,
}


def _load_parser():
    if str(MARKETS_SCRIPTS) not in sys.path:
        sys.path.insert(0, str(MARKETS_SCRIPTS))
    import twse_ixbrl_parser

    return twse_ixbrl_parser


@pytest.mark.parametrize(
    ("fixture_name", "expected_count"),
    sorted(EXPECTED_FACT_COUNTS.items()),
)
def test_fh_fixture_parses_to_measured_fact_count(fixture_name, expected_count):
    mod = _load_parser()
    # Decode exactly as the production fetch layer does
    # (twse_ixbrl_fetch.py: resp.content.decode("big5hkscs", errors="replace")):
    # these real fh bodies declare charset=big5 yet embed a few UTF-8 bytes
    # (e.g. the CSS font-family "細明體"), so a strict big5 decode raises. The
    # measured fact_count in each *.profile.json was produced through this same
    # tolerant decode; the test must match the producer path, not a stricter one.
    document = (FIXTURES / fixture_name).read_bytes().decode(
        "big5hkscs", errors="replace"
    )
    facts = mod.parse_ixbrl_facts(document)

    assert len(facts) == expected_count, (
        f"{fixture_name} must parse to exactly {expected_count} facts "
        f"(measured fact_count from its *.profile.json) — any drift is the "
        f"DOM-drop regression tripwire"
    )
