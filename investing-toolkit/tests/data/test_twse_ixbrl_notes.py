"""test_twse_ixbrl_notes.py — OFFLINE regression test for
twse_ixbrl_notes.extract_curated_notes against the committed TSMC 2330
2024Q3 consolidated iXBRL fixture (docs/loom/plans/2026-07-19-tw-ixbrl-
ingestion.md, Task 4).

Guards two things: (1) the golden curated values (FVOCI current
financial assets, Mainland-China accumulated investment) are pulled
with the correct concept/period from the real fixture facts; (2) a
concept absent from the fixture is OMITTED from the result dict, never
zero-filled — the annual-verification finding (spec §Annual
verification) that motivated a curated field set instead of a general
note-table-reconstruction engine.

Run offline (no network marker; part of the default `not network` suite):
  PYTHONDONTWRITEBYTECODE=1 python3 -m pytest investing-toolkit/tests/ -q -m "not network"
"""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
MARKETS_SCRIPTS = ROOT / "skills" / "data-markets" / "scripts"
FIXTURES = Path(__file__).resolve().parent / "fixtures"


def _load_modules():
    if str(MARKETS_SCRIPTS) not in sys.path:
        sys.path.insert(0, str(MARKETS_SCRIPTS))
    import twse_ixbrl_notes
    import twse_ixbrl_parser
    return twse_ixbrl_parser, twse_ixbrl_notes


def _fixture_facts(parser) -> list[dict]:
    # TW MOPS t164sb01 responses are Big5-encoded; the parser takes an
    # already-decoded str (decoding is the fetch layer's job — Task 2).
    document = (FIXTURES / "twse_ixbrl_2330_2024Q3_C.html").read_text(encoding="big5")
    return parser.parse_ixbrl_facts(document)


def test_curated_notes_tsmc():
    parser, notes_mod = _load_modules()
    facts = _fixture_facts(parser)

    notes = notes_mod.extract_curated_notes(facts)

    # Golden fact 1: current financial assets at FVOCI, AsOf20240930.
    # Fixture raw text "189,649,314" thousand-TWD, scale=3 -> 189,649,314,000.
    fvoci = notes["financial_assets_fvoci"]
    assert fvoci["value"] == 189649314000.0
    assert fvoci["concept"] == (
        "ifrs-full:CurrentFinancialAssetsAtFairValueThroughOtherComprehensiveIncome"
    )
    assert fvoci["period"] == {"type": "instant", "instant": "2024-09-30"}

    # Golden fact 2: Mainland-China accumulated investment, AsOf20240930.
    # Fixture raw text "49,461,079" thousand-TWD, scale=3 -> 49,461,079,000
    # (~494.6億).
    china = notes["mainland_china_accumulated_investment"]
    assert china["value"] == 49461079000.0
    assert china["concept"] == (
        "tifrs-notes:AccumulatedInvestmentInMainlandChinaAtTheEndOfThePeriod"
    )
    assert china["period"] == {"type": "instant", "instant": "2024-09-30"}

    # A concept absent from this fixture must be OMITTED, not zero-filled.
    assert "made_up_field_not_in_fixture" not in notes


def test_curated_notes_field_shape_and_absence():
    parser, notes_mod = _load_modules()
    facts = _fixture_facts(parser)

    notes = notes_mod.extract_curated_notes(facts)

    # Every emitted field has the {value, concept, period} shape.
    for field, entry in notes.items():
        assert set(entry.keys()) == {"value", "concept", "period"}, field

    # related-party aggregate purchase flow: TWO durations tie on the
    # same end date (2024-09-30) — quarterly (Jul-Sep, 1,282,865,000)
    # vs YTD (Jan-Sep, 3,545,858,000). The curated extractor must prefer
    # the longer (YTD/aggregate) duration on an end-date tie.
    purchases = notes["related_party_purchases"]
    assert purchases["value"] == 3545858000.0
    assert purchases["period"] == {
        "type": "duration",
        "start": "2024-01-01",
        "end": "2024-09-30",
    }


def test_curated_notes_empty_facts_omits_everything():
    _, notes_mod = _load_modules()
    assert notes_mod.extract_curated_notes([]) == {}
