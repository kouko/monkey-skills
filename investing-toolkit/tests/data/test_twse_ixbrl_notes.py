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
from unittest import mock

import pytest

ROOT = Path(__file__).resolve().parents[2]
MARKETS_SCRIPTS = ROOT / "skills" / "data-markets" / "scripts"
FIXTURES = Path(__file__).resolve().parent / "fixtures"

# twse_ixbrl (the pipeline) imports twse_ixbrl_fetch, which does `import
# requests`. CI's offline env has no `requests` (clients ship PEP 723 deps,
# run via `uv run`), so the bare import chain would ModuleNotFoundError at
# collection. setdefault keeps a real `requests` when present, stubs it when
# absent — the routing test never exercises the network seam anyway.
sys.modules.setdefault("requests", mock.MagicMock(name="requests"))


def _load_modules():
    if str(MARKETS_SCRIPTS) not in sys.path:
        sys.path.insert(0, str(MARKETS_SCRIPTS))
    import twse_ixbrl_notes
    import twse_ixbrl_parser
    return twse_ixbrl_parser, twse_ixbrl_notes


def _load_pipeline():
    if str(MARKETS_SCRIPTS) not in sys.path:
        sys.path.insert(0, str(MARKETS_SCRIPTS))
    import twse_ixbrl
    return twse_ixbrl


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


def test_pipeline_now_surfaces_endorsement_guarantee():
    """FLIPPED from the former deferral test (Task 3). Endorsement/guarantee
    was originally deferred out of scope — ix:tuple-structured per-counterparty
    rows with no clean aggregate leaf. Task 2 shipped
    `extract_endorsement_guarantee_notes` (document-order row reconstruction),
    and Task 3 wired it through `twse_ixbrl._extract_notes` by POPULATION. So
    the pipeline now DOES surface it: the 2330 fixture carries 4 populated
    endorser rows, which appear under the `endorsement_guarantee` key
    (structured {"summary", "rows"}, not the flat curated-field shape). The
    curated set itself is unchanged — endorsement is a separate routed field,
    not a `_CURATED_CONCEPTS` entry."""
    parser, _notes_mod = _load_modules()
    twse_ixbrl = _load_pipeline()
    facts = _fixture_facts(parser)

    # -ci industrial (taxonomy absent) → curated path + endorsement merge.
    notes = twse_ixbrl._extract_notes(facts, {"taxonomy": None})

    assert "endorsement_guarantee" in notes
    endo = notes["endorsement_guarantee"]
    assert endo["summary"]["row_count"] == 4
    assert endo["rows"][0]["endorser"] == "台積公司"
    assert endo["rows"][0]["counterparty"] == "TSMC North America"

    # It is a routed field, NOT folded into the flat curated-concept set.
    curated = _notes_mod.extract_curated_notes(facts)
    assert "endorsement_guarantee" not in curated


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

    # npl_ratio: the OTHER percent branch (Non-PerformingLoansRatio).
    # Raw text scale=-2 -> parser raw_value 0.0016; extractor presents
    # 0.16 (x100, same single-conversion rule as coverage_ratio).
    assert cathay_bank["npl_ratio"]["value"] == 0.16
    assert cathay_bank["npl_ratio"]["concept"] == "tifrs-notes:Non-PerformingLoansRatio"

    # gross_loans: the PASSTHROUGH branch (not a percent field) — the
    # parser's own scale-driven scaled value is asserted as-is, no *100.
    assert cathay_bank["gross_loans"]["value"] == 2_946_761_073_000.0
    assert cathay_bank["gross_loans"]["concept"] == "tifrs-notes:GrossLoans"


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


def test_basi_npl_coverage_totalloans_changhwa():
    """-basi NPL/coverage note (Task 10): standalone commercial banks
    (e.g. 2801 彰化銀行) encode the loan category via a CONTEXT_REF
    SUFFIX ("..._TotalLoansMember") plus a "Member"-suffixed concept
    name ("CoverageRatioMember"), NOT ix:tuple attributes (contrast
    Task 9's tuple_ref disambiguation) — the existing generic parser
    already resolves concept + context_ref, so no tuple parsing is
    needed. MEASURED against the real 2801 2026Q1 fixture,
    scratchpad/fh-measurement-round2.md §2801."""
    parser, notes_mod = _load_modules()
    facts = _fixture_facts_smart(parser, "twse_ixbrl_2801_2026Q1_C.html")

    basi = notes_mod.extract_basi_npl_coverage_notes(facts)

    # Raw text scale=-2 -> parser raw_value 8.6467 (the true fraction);
    # the extractor presents it as the percentage 864.67 (single *100
    # conversion, not a second application of the XBRL `scale` attribute).
    assert basi["coverage_ratio"]["value"] == 864.67
    assert basi["coverage_ratio"]["concept"] == "tifrs-notes:CoverageRatioMember"
    assert basi["coverage_ratio"]["period"] == {"type": "instant", "instant": "2026-03-31"}

    # npl_ratio: the OTHER percent branch. Raw value 0.0016 -> 0.16.
    assert basi["npl_ratio"]["value"] == 0.16
    assert basi["npl_ratio"]["concept"] == "tifrs-notes:NonPerformingLoansRatioMember"

    # npl_amount / gross_loans: passthrough branches (not percent fields) —
    # the parser's own scale-driven scaled value is asserted as-is.
    assert basi["npl_amount"]["value"] == 3291281000.0
    assert basi["npl_amount"]["concept"] == "tifrs-notes:AmountOfNon-PerformingLoansMember"
    assert basi["gross_loans"]["value"] == 2116370367000.0
    assert basi["gross_loans"]["concept"] == "tifrs-notes:GrossLoansMember"

    # Company/bank name surfaced (legible via smart-decode).
    assert basi["company_name"]["value"] == "彰化銀行"


def test_basi_npl_coverage_absent_for_bills_finance():
    """Bills-finance -basi filers (e.g. 2820 華票) carry NO NPL/coverage
    note at all (MEASURED: 0 hits for NonPerforming/CoverageRatio
    concepts, scratchpad/fh-measurement-round4.md §2820 Q2 answer) —
    the extractor must degrade to an empty dict gracefully, never
    raise."""
    parser, notes_mod = _load_modules()
    facts = _fixture_facts_smart(parser, "twse_ixbrl_2820_2026Q1_A.html")

    basi = notes_mod.extract_basi_npl_coverage_notes(facts)

    assert basi == {}


def test_endorsement_guarantee_populated_and_empty():
    """Endorsement/guarantee note (Task 2): reconstruct per-endorser ROWS by
    DOCUMENT-ORDER segmentation on the `tifrs-notes:CompanyNameOfTheEndorser
    Guarantor` anchor — the rows have no leaf `tuple_ref` and share only two
    context_refs, so document order is the sole handle (the
    `_fh_npl_tree_segments` trick). Each row's counterparty is the inner
    `tifrs-notes:NameOfTheCompany` (the Counterparty2 tuple) that appears in
    the span. MEASURED against the real 台泥 1101 2026Q1 fixture.

    NOTE — two plan-PIN corrections proven by measurement on the committed
    fixtures (see the implementer report):
    * SUM(ActualAmountProvided) is ENDORSEMENT-SCOPED = 62,786,222,000, NOT
      the plan-PIN 105.9bn. 105.9bn is the doc-wide sum of all 113
      `ActualAmountProvided` facts, but 74 of those precede the first
      endorser anchor and belong to a SEPARATE note (資金貸與/financing-to-
      others: `LimitOfLoanAmountForIndividualCounterparty` /
      `AmountOfSalesToPurchasesFromCounterparty`, both 74x). Summing doc-wide
      would conflate two disclosure tables — an extraction bug. The span-
      scoped sum is the honest endorsement total.
    * The empty/"none" case uses a 0-anchor fixture (2882 財金控, section
      absent). The plan named 台塑 1301 as EMPTY, but 1301 actually carries
      ONE populated endorsement row (endorser 本公司 → 台塑集團(開曼)), so it
      cannot exercise the none-path. 0 anchors → explicit none result covers
      both "section absent" and "section-present-but-empty" identically.
    """
    parser, notes_mod = _load_modules()
    facts = _fixture_facts_smart(parser, "twse_ixbrl_1101_2026Q1_C.html")

    result = notes_mod.extract_endorsement_guarantee_notes(facts)
    rows = result["rows"]
    summary = result["summary"]

    # 39 per-endorser rows reconstructed by document-order segmentation.
    assert len(rows) == 39

    # row0: endorser 台灣水泥公司 → counterparty 聯誠貿易公司 (inner
    # NameOfTheCompany); EndingBalance2 raw 1,420,000 thousand-TWD scaled to
    # 1,420,000,000; ActualAmountProvided 0. Chinese names legible via the
    # production UTF-8-first decode (facts arrive pre-decoded).
    r0 = rows[0]
    assert r0["endorser"] == "台灣水泥公司"
    assert r0["counterparty"] == "聯誠貿易公司"
    assert r0["ending_balance"] == 1_420_000_000.0
    assert r0["actual_provided"] == 0.0
    assert r0["collateral_secured"] == 0.0
    assert r0["individual_limit"] == 120_725_747_000.0
    assert r0["endorser_total_ceiling"] == 241_451_494_000.0
    assert r0["ratio_to_net_asset"] == 0.0059
    assert r0["to_subsidiary_by_parent"] == "Y"
    assert r0["to_parent_by_subsidiary"] == "N"
    assert r0["to_mainland_china"] == "N"

    # row1: same endorser, counterparty 信昌投資公司, ending 2,370,000
    # thousand → 2,370,000,000, actual 1,140,000 thousand → 1,140,000,000.
    r1 = rows[1]
    assert r1["counterparty"] == "信昌投資公司"
    assert r1["ending_balance"] == 2_370_000_000.0
    assert r1["actual_provided"] == 1_140_000_000.0

    # Aggregate summary: span-scoped SUM(ActualAmountProvided) /
    # SUM(EndingBalance2), row + distinct-counterparty counts, peak per-row
    # RatioOfAccumulatedEndorsementGuaranteeAmountToNetAsset..., and a
    # subsidiary-vs-external split from the Y/N relationship flags
    # (33 internal where ToSubsidiaryByParent OR ToParentBySubsidiaries == Y;
    # 6 external; 13 to Mainland-China, orthogonal).
    assert summary["row_count"] == 39
    assert summary["counterparty_count"] == 31
    assert summary["total_actual_provided"] == 62_786_222_000.0
    assert summary["total_ending_balance"] == 107_613_931_000.0
    assert summary["max_ratio_to_net_asset"] == pytest.approx(4.8386)
    assert summary["subsidiary_related_count"] == 33
    assert summary["external_count"] == 6
    assert summary["mainland_china_count"] == 13

    # Empty/"none" case: a 0-anchor filing yields an EXPLICIT empty summary
    # (row_count 0, None peak ratio — never a fake zero) + empty rows list,
    # never a crash or silent zero.
    empty_facts = _fixture_facts_smart(parser, "twse_ixbrl_2882_2026Q1_C.html")
    none_result = notes_mod.extract_endorsement_guarantee_notes(empty_facts)
    assert none_result["rows"] == []
    assert none_result["summary"]["row_count"] == 0
    assert none_result["summary"]["counterparty_count"] == 0
    assert none_result["summary"]["total_actual_provided"] == 0.0
    assert none_result["summary"]["total_ending_balance"] == 0.0
    assert none_result["summary"]["max_ratio_to_net_asset"] is None
    assert none_result["summary"]["subsidiary_related_count"] == 0
    assert none_result["summary"]["external_count"] == 0
    assert none_result["summary"]["mainland_china_count"] == 0


def test_extract_notes_routes_endorsement():
    """Task 3: the endorsement/guarantee curated field is routed through
    `twse_ixbrl._extract_notes` for ANY taxonomy where the section is
    POPULATED — not gated to one taxonomy (contrast the fh/basi NPL split,
    which keys off `canonical["taxonomy"]`). Endorsement lives in the SHARED
    t164sb01 iXBRL, so a populated -ci industrial (台泥 1101, 39 rows) MUST
    surface it, while a 0-anchor filer (2882, fh) MUST NOT — its endorsement
    is the empty 'none' result, which is not attached, preserving the
    empty-notes contract that note-less taxonomies (e.g. insurers → {}) rely
    on. The taxonomy-specific NPL routing must remain untouched by the merge."""
    parser, _notes_mod = _load_modules()
    twse_ixbrl = _load_pipeline()

    # 1101 is -ci (taxonomy absent from canonical) → curated-notes path; the
    # populated endorsement section (39 endorser rows) is merged in.
    facts = _fixture_facts_smart(parser, "twse_ixbrl_1101_2026Q1_C.html")
    notes = twse_ixbrl._extract_notes(facts, {"taxonomy": None})
    assert "endorsement_guarantee" in notes
    endo = notes["endorsement_guarantee"]
    assert endo["summary"]["row_count"] == 39
    assert endo["rows"][0]["endorser"] == "台灣水泥公司"
    assert endo["rows"][0]["counterparty"] == "聯誠貿易公司"

    # 0-anchor fh filer (2882): the endorsement 'none' result is NOT attached
    # (nothing to surface), so notes stays free of the endorsement key — and
    # the fh NPL routing is untouched by the endorsement merge.
    empty_facts = _fixture_facts_smart(parser, "twse_ixbrl_2882_2026Q1_C.html")
    empty_notes = twse_ixbrl._extract_notes(empty_facts, {"taxonomy": "fh"})
    assert "endorsement_guarantee" not in empty_notes
    assert "國泰世華銀行" in empty_notes  # fh routing intact


def test_select_current_fact_ambiguous_period_tie_first_wins_and_is_logged(capsys):
    """Pins the tie-break rule `_select_current_fact` relies on when 2+
    candidates share an IDENTICAL period — as the 2890 fixture's NPL
    table does: it mis-tags its 去年同期 (prior-year) column with the
    same contextRef as 本期 (current), so both a "本期" and a "去年同期"
    fact resolve to the same period. The rule (first-in-document-order
    wins, per the observed 本期-before-去年同期 column emission order) was
    previously silent — with `label` given, an ambiguous tie must also
    be logged (not just resolved) so it's observable rather than an
    incidental dependency on HTML column order that could regress on a
    fixture refresh or a different filer's layout."""
    _, notes_mod = _load_modules()
    same_period = {"type": "instant", "instant": "2026-03-31"}
    current = {"raw_value": 111.0, "period": dict(same_period)}
    prior = {"raw_value": 222.0, "period": dict(same_period)}

    chosen = notes_mod._select_current_fact([current, prior], label="acme/coverage_ratio")

    assert chosen is current
    assert chosen["raw_value"] == 111.0
    err = capsys.readouterr().err
    assert "ambiguous period tie" in err
    assert "acme/coverage_ratio" in err
