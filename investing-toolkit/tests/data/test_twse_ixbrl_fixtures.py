"""test_twse_ixbrl_fixtures.py — OFFLINE exact-fact-count regression guard
for the real MOPS iXBRL fixtures.

These 8 fixtures are REAL producer bytes captured live from TWSE MOPS
(t164sb01 endpoint), verified live 2026-07. All declare charset=big5, yet
their bodies are actually UTF-8 — decode via `decode_ixbrl_document`
(UTF-8-first, big5hkscs fallback). Seven mirror the real financial-holding
/ bank / insurance / securities producer (fh/basi/bd/ins family); the
eighth (1101 台泥) is a non-financial -ci industrial filing, added for
endorsement/guarantee-row coverage. 1101 is ALSO UTF-8-despite-charset=big5
(its raw bytes decode cleanly as UTF-8 — 台灣水泥公司 renders correctly —
and are mojibake under big5hkscs). This refines the repo's
tw-financial-ixbrl-served-utf8-despite-big5-declaration memory: the
served-UTF-8-despite-big5 behavior is NOT limited to the financial family —
a -ci industrial filer (1101, 2026Q1) shows it too, so the byte encoding
is NOT predictable from the taxonomy, which is exactly why the UTF-8-first
smart decode (`decode_ixbrl_document`) is the correct production path.
Downstream taxonomy work is thus tested against producer-shaped data,
never hand-authored input.
Provenance (co_id · period · source):

  2882 · 2026Q1 consolidated (C) · MOPS t164sb01 · verified live 2026-07
  2890 · 2026Q1 consolidated (C) · MOPS t164sb01 · verified live 2026-07
  2801 · 2026Q1 consolidated (C) · MOPS t164sb01 · verified live 2026-07
  2820 · 2026Q1 individual   (A) · MOPS t164sb01 · verified live 2026-07
  6005 · 2026Q1 consolidated (C) · MOPS t164sb01 · verified live 2026-07
  2867 · 2026Q1 individual   (A) · MOPS t164sb01 · verified live 2026-07
  2851 · 2025Q1 individual   (A) · MOPS t164sb01 · verified live 2026-07
  1101 · 2026Q1 consolidated (C) · MOPS t164sb01 · -ci industrial · verified live 2026-07

Each EXPECTED_FACT_COUNTS value is a whole-file `fact_count`. For the
seven fh fixtures it is the `fact_count` field from the matching
`<co_id>_<period>_<type>.profile.json` measured beside the raw body at
capture time (fh-measurement rounds); for the dict-only fixtures with no
profile.json sibling (1101, plus the 1301/2330 -ci fixtures referenced in
PRODUCTION_DECODE_EXPECTED_FACT_COUNTS below) the count was measured
empirically by running the parser through both decode paths (they must
agree). The exact-count assertion (±0) is the DOM-drop regression
tripwire: a naive DOM/tree-repair parse silently drops facts nested inside
<td> (measured on TSMC as 387 vs true 2002), so any drift from the
measured count fails loud here.

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

# fixture basename -> exact measured fact_count (fh fixtures: the matching
# *.profile.json `fact_count` from the fh capture rounds; 1101: measured
# empirically via both decode paths — see module docstring for provenance).
EXPECTED_FACT_COUNTS = {
    "twse_ixbrl_2882_2026Q1_C.html": 1753,
    "twse_ixbrl_2890_2026Q1_C.html": 1326,
    "twse_ixbrl_2801_2026Q1_C.html": 1413,
    "twse_ixbrl_2820_2026Q1_A.html": 464,
    "twse_ixbrl_6005_2026Q1_C.html": 1644,
    "twse_ixbrl_2867_2026Q1_A.html": 649,
    "twse_ixbrl_2851_2025Q1_A.html": 477,
    # 1101 台泥 2026Q1 consolidated — a -ci industrial filing that is
    # UTF-8-despite-charset=big5 (same served-UTF-8 pattern as the financial
    # family, refining tw-financial-ixbrl-served-utf8-despite-big5-declaration.md;
    # decode_ixbrl_document handles it UTF-8-first). The sole fixture carrying
    # populated endorsement/guarantee rows (39 endorsers on the
    # CompanyNameOfTheEndorserGuarantor anchor); whole-file fact_count measured
    # empirically via both decode paths (they agree at 7299 — the ix: tags are
    # ASCII, so only text VALUES differ between decodes, not the count).
    "twse_ixbrl_1101_2026Q1_C.html": 7299,
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


# Every fixture with a stored expected fact count, across BOTH families:
# the 7 financial (fh/basi/bd/ins) fixtures above (UTF-8 bodies despite the
# big5 charset declaration) plus the genuine-Big5 -ci fixture whose measured
# count (2002) is pinned in test_twse_ixbrl_parser.py /
# test_data_markets_tw.py. twse_ixbrl_1301_2024Q3_C.html has no stored
# expected count anywhere in the suite, so it is not covered here.
PRODUCTION_DECODE_EXPECTED_FACT_COUNTS = {
    **EXPECTED_FACT_COUNTS,
    "twse_ixbrl_2330_2024Q3_C.html": 2002,
}


@pytest.mark.parametrize(
    ("fixture_name", "expected_count"),
    sorted(PRODUCTION_DECODE_EXPECTED_FACT_COUNTS.items()),
)
def test_fixture_fact_counts_match_under_production_decode(
    fixture_name, expected_count
):
    # The legacy test above decodes via the OLD fetch-layer path
    # (big5hkscs, errors="replace"). Production moved to
    # decode_ixbrl_document (UTF-8-strict first, big5hkscs/replace
    # fallback — see docs/loom/memory/
    # tw-financial-ixbrl-served-utf8-despite-big5-declaration.md) in
    # 2.31.0; this asserts the measured whole-file fact counts hold
    # under the decode path real fetches actually use.
    mod = _load_parser()
    raw = (FIXTURES / fixture_name).read_bytes()
    document = mod.decode_ixbrl_document(raw)
    facts = mod.parse_ixbrl_facts(document)

    assert len(facts) == expected_count, (
        f"{fixture_name} must parse to exactly {expected_count} facts under "
        f"the production decode_ixbrl_document path — a count delta vs the "
        f"measured *.profile.json baseline is a surfaced finding, never a "
        f"re-baseline"
    )
