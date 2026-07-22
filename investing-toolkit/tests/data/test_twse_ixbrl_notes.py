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


def _fixture_facts_smart(parser, filename: str) -> list[dict]:
    # Financial-family (-fh/-basi/-bd/-ins) fixtures declare charset=big5
    # but are genuinely UTF-8 (Task 14 finding) — decode via the parser's
    # smart-decode helper so Chinese text (bank subsidiary names) survives
    # instead of being garbled by a forced big5hkscs decode.
    raw = (FIXTURES / filename).read_bytes()
    document = parser.decode_ixbrl_document(raw)
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


def test_curated_notes_excludes_endorsement_guarantee():
    """Endorsement/guarantee is ix:tuple-structured (per-counterparty rows
    sharing one contextRef) with no clean aggregate leaf fact — deferred
    to the note-table-reconstruction sub-arc (brief §Annual verification /
    Task 4 Decision Log). The curated set must not surface it."""
    parser, notes_mod = _load_modules()
    facts = _fixture_facts(parser)

    notes = notes_mod.extract_curated_notes(facts)

    assert "endorsement_guarantee_limit" not in notes
    assert "endorsement_guarantee_secured_with_collateral" not in notes


def test_fh_npl_coverage_totalloans_cathay():
    """-fh NPL/coverage note (Task 9): the TotalLoans row is disambiguated
    from 7 sibling loan-category rows sharing the same contextRef purely
    via the `tuple_ref` attribute ("TL"), and tagged with the banking
    SUBSIDIARY's name (never the FHC group) — MEASURED against the real
    2882 (國泰金控 Cathay FHC) 2026Q1 fixture, scratchpad/fh-measurement.md
    §2882. A tuple-blind concept-keyed pick would silently grab one of
    7 wrong loan-category rows instead."""
    parser, notes_mod = _load_modules()
    facts = _fixture_facts_smart(parser, "twse_ixbrl_2882_2026Q1_C.html")

    npl = notes_mod.extract_fh_npl_coverage_notes(facts)

    cathay_bank = npl["國泰世華銀行"]
    # Raw text "1,031.17" scale=-2 -> parser's raw_value 10.3117 (the
    # true fraction); the extractor presents it as the percentage
    # 1031.17 (do not double-scale — this is the single *100 conversion,
    # not a second application of the XBRL `scale` attribute).
    assert cathay_bank["coverage_ratio"]["value"] == 1031.17
    assert cathay_bank["coverage_ratio"]["concept"] == "tifrs-notes:CoverageRatio"
    assert cathay_bank["coverage_ratio"]["period"] == {
        "type": "instant",
        "instant": "2026-03-31",
    }


def test_fh_npl_coverage_resolves_both_bank_subsidiaries_distinctly():
    """DUP-TREE case (Task 9): 2890 永豐金控 is a post-merger FHC carrying
    TWO duplicated parallel NPL tuple trees (one per bank subsidiary,
    both reusing the same category tuple_ref codes e.g. "TL"/"SCF").
    The extractor must key by subsidiary and resolve BOTH distinctly —
    not collapse them or arbitrarily pick one — MEASURED against
    scratchpad/fh-measurement-round2.md §2890."""
    parser, notes_mod = _load_modules()
    facts = _fixture_facts_smart(parser, "twse_ixbrl_2890_2026Q1_C.html")

    npl = notes_mod.extract_fh_npl_coverage_notes(facts)

    assert set(npl) == {"永豐商業銀行", "京城商業銀行"}
    assert npl["永豐商業銀行"]["coverage_ratio"]["value"] == 1260.54
    assert npl["京城商業銀行"]["coverage_ratio"]["value"] == 2407.94
