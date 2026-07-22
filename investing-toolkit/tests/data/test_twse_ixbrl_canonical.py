"""test_twse_ixbrl_canonical.py — OFFLINE regression test for
twse_ixbrl_canonical.build_canonical against facts parsed from the
committed TSMC 2330 2024Q3 consolidated iXBRL fixture (docs/loom/plans/
2026-07-19-tw-ixbrl-ingestion.md, Task 3).

Verifies the canonical mapper reshapes parsed iXBRL facts into the
toolkit's canonical three-statement shape (pack_tw.py's
`_build_canonical_from_yf_financials_tw` :205-311 is the target shape
this mirrors: three top-level keys income_statement/balance_sheet/
cash_flow, each a value-list plus per-line `_meta`). A synthetic `-fh`
(financial holding) fact set must return an explicit unsupported
marker, never raise.

Run offline (no network marker; part of the default `not network` suite):
  PYTHONDONTWRITEBYTECODE=1 python3 -m pytest investing-toolkit/tests/ -q -m "not network"
"""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
MARKETS_SCRIPTS = ROOT / "skills" / "data-markets" / "scripts"
FIXTURES = Path(__file__).resolve().parent / "fixtures"


def _load_modules():
    if str(MARKETS_SCRIPTS) not in sys.path:
        sys.path.insert(0, str(MARKETS_SCRIPTS))
    import twse_ixbrl_canonical
    import twse_ixbrl_parser
    return twse_ixbrl_parser, twse_ixbrl_canonical


def _fixture_facts(parser, filename: str = "twse_ixbrl_2330_2024Q3_C.html") -> list[dict]:
    document = (FIXTURES / filename).read_text(encoding="big5")
    return parser.parse_ixbrl_facts(document)


def _fixture_facts_tolerant(parser, filename: str) -> list[dict]:
    # Producer path (twse_ixbrl_fetch.py): resp.content.decode("big5hkscs",
    # errors="replace"). The real financial (-fh/-basi/-bd/-ins) fixtures
    # embed stray UTF-8 bytes that a strict big5 decode would raise on, so
    # the classifier test must load them the same tolerant way the fetcher
    # does (see test_twse_ixbrl_fixtures.py).
    document = (FIXTURES / filename).read_bytes().decode("big5hkscs", errors="replace")
    return parser.parse_ixbrl_facts(document)


# One fixture per taxonomy family — each real filing carries exactly one
# tifrs-bsci-* namespace family (measured: grep -ao "tifrs-bsci-[a-z]*").
_TAXONOMY_FIXTURES = [
    ("twse_ixbrl_2330_2024Q3_C.html", "ci"),
    ("twse_ixbrl_2882_2026Q1_C.html", "fh"),
    ("twse_ixbrl_2801_2026Q1_C.html", "basi"),
    ("twse_ixbrl_6005_2026Q1_C.html", "bd"),
    ("twse_ixbrl_2867_2026Q1_A.html", "ins"),
]


@pytest.mark.parametrize("filename,expected_tag", _TAXONOMY_FIXTURES)
def test_classify_taxonomy_five_way(filename, expected_tag):
    """classify_taxonomy inspects the tifrs-bsci-* namespace prefix present
    in the fact set and returns the family tag (ci/fh/basi/bd/ins). Replaces
    the old boolean _is_fh_taxonomy with a 5-way classifier."""
    parser, canonical_mod = _load_modules()
    facts = _fixture_facts_tolerant(parser, filename)
    assert canonical_mod.classify_taxonomy(facts) == expected_tag


def test_build_canonical_routes_ci_via_registry_unchanged():
    """Regression: -ci output is byte-unchanged after routing through the
    builder registry (the -ci builder is registered under "ci"). "fh" now
    has its own registered builder (Task 5) so it no longer returns the
    unsupported marker (see test_canonical_fh_from_2882_fixture); "bd" has
    no builder yet (lands in a later task) and must still return the
    unsupported marker."""
    parser, canonical_mod = _load_modules()

    ci_canonical = canonical_mod.build_canonical(_fixture_facts(parser))
    assert 2_025_846_521_000.0 in ci_canonical["income_statement"]["revenue"]
    assert ci_canonical["balance_sheet"]["total_assets"]
    assert ci_canonical["cash_flow"]["operating_cash_flow"]

    bd_result = canonical_mod.build_canonical(
        _fixture_facts_tolerant(parser, "twse_ixbrl_6005_2026Q1_C.html")
    )
    assert bd_result.get("unsupported") == "financial-bd", bd_result


def test_canonical_ci_from_facts():
    parser, canonical_mod = _load_modules()
    facts = _fixture_facts(parser)

    canonical = canonical_mod.build_canonical(facts)

    assert canonical["income_statement"]["revenue"], "income_statement.revenue must be non-empty"
    assert canonical["balance_sheet"]["total_assets"], "balance_sheet.total_assets must be non-empty"
    assert canonical["cash_flow"]["operating_cash_flow"], "cash_flow.operating_cash_flow must be non-empty"

    for statement in ("income_statement", "balance_sheet", "cash_flow"):
        meta = canonical[statement]["_meta"]
        assert meta, f"{statement}._meta must be non-empty"
        for line, line_meta in meta.items():
            assert line_meta["accounting_standard"] == "tifrs", (statement, line)
            assert line_meta["unit"] == "TWD", (statement, line)

    # Traced golden fact: ifrs-full:Revenue, contextRef=From20240101To20240930
    # (2024 YTD Q1-Q3 cumulative revenue). Fixture raw text is
    # "2,025,846,521" with scale=3/decimals=-3 -> true value x1000.
    # (grepped directly from the fixture; the plan's "tifrs-bsci-ci
    # revenue fact" phrasing is loose — the actual concept lives in the
    # ifrs-full namespace for -ci filers, tifrs-bsci-ci covers only
    # TW-specific supplementary line items, not standard Revenue.)
    revenue_fact = [
        f
        for f in facts
        if f["concept"] == "ifrs-full:Revenue"
        and f["context_ref"] == "From20240101To20240930"
    ]
    assert len(revenue_fact) == 1, revenue_fact
    assert revenue_fact[0]["raw_value"] == 2_025_846_521_000.0

    assert 2_025_846_521_000.0 in canonical["income_statement"]["revenue"], (
        "canonical revenue must trace to the real fixture ifrs-full:Revenue "
        "YTD fact value"
    )
    assert canonical["income_statement"]["_meta"]["revenue"]["concept"] == "ifrs-full:Revenue"


def test_canonical_ci_emits_dcf_required_fields():
    """Round 2 fix (code-quality review 🔴): analysis-dcf/scripts/dcf_compute.py
    (:29-34, :192-221) requires balance_sheet.total_debt/cash and uses
    income_statement.ebit + cash_flow.capex/fcf with silent-zero fallbacks —
    the pre-fix _CONCEPT_MAP omitted all five, so net_debt silently computed
    as 0 for every TW ticker. Traced against the real fixture (grepped
    twse_ixbrl_2330_2024Q3_C.html directly, big5 raw bytes — iconv translit
    truncates the file on invalid byte sequences, so grep -a on the original
    is the reliable path).
    """
    parser, canonical_mod = _load_modules()
    facts = _fixture_facts(parser)

    canonical = canonical_mod.build_canonical(facts)

    bs = canonical["balance_sheet"]
    inc = canonical["income_statement"]
    cf = canonical["cash_flow"]

    # cash <- ifrs-full:CashAndCashEquivalents, AsOf20240930: "1,886,780,555" x1000
    assert bs["cash"][0] == 1_886_780_555_000.0
    assert bs["_meta"]["cash"]["concept"] == "ifrs-full:CashAndCashEquivalents"

    # total_debt <- sum of the 3 long-term debt-bearing concepts present in
    # this filer's -ci fact set (LongtermBorrowings +
    # NoncurrentPortionOfNoncurrentBondsIssued + NoncurrentFinanceLeaseLiabilities),
    # AsOf20240930: 26,459,677 + 909,703,588 + 28,208,721 = 964,371,986 (x1000).
    # _DEBT_CONCEPTS also includes 4 short-term/current interest-bearing debt
    # concepts (verified against the debt-heavy Formosa 1301 filer — see
    # test_canonical_ci_total_debt_formosa_includes_short_term); this
    # fixture (TSMC, cash-rich) confirmed-absent all four via grep -a over
    # the raw fixture bytes, so the value here is unchanged.
    assert bs["total_debt"][0] == 964_371_986_000.0
    assert bs["_meta"]["total_debt"]["derivation"]

    # ebit <- alias of operating_income (same concept,
    # ifrs-full:ProfitLossFromOperatingActivities), YTD From20240101To20240930:
    # "896,340,137" x1000
    assert inc["ebit"][0] == 896_340_137_000.0
    assert inc["ebit"][0] == inc["operating_income"][0]
    assert inc["_meta"]["ebit"]["concept"] == "ifrs-full:ProfitLossFromOperatingActivities"

    # capex <- ifrs-full:PurchaseOfPropertyPlantAndEquipmentClassifiedAsInvestingActivities,
    # YTD From20240101To20240930: raw fact is sign="-" "594,058,374" (x1000);
    # canonical convention (pack_us/jp/kr/cn) stores capex as absolute value.
    assert cf["capex"][0] == 594_058_374_000.0

    # fcf <- DERIVED = operating_cash_flow - capex, most-recent period.
    # operating_cash_flow[0] (YTD) = 1,205,971,785 x1000.
    assert cf["operating_cash_flow"][0] == 1_205_971_785_000.0
    assert cf["fcf"][0] == cf["operating_cash_flow"][0] - cf["capex"][0]
    assert cf["fcf"][0] == 611_913_411_000.0
    assert cf["_meta"]["fcf"]["derivation"]

    # All new lines must carry the same accounting_standard/unit shape as the
    # pre-existing lines (test_canonical_ci_from_facts already scans every
    # _meta entry for this; this test pins the specific new lines too).
    for statement, lines in (("balance_sheet", ["cash", "total_debt"]),
                              ("income_statement", ["ebit"]),
                              ("cash_flow", ["capex", "fcf"])):
        meta = canonical[statement]["_meta"]
        for line in lines:
            assert meta[line]["accounting_standard"] == "tifrs", (statement, line)
            assert meta[line]["unit"] == "TWD", (statement, line)


def test_canonical_ci_total_debt_sums_short_term_debt_when_present():
    """Whole-branch review remediation: TW canonical total_debt was
    long-term-debt-only, omitting short-term/current interest-bearing
    borrowings — understating net_debt (analysis-dcf) and overstating
    DCF equity value. _DEBT_CONCEPTS must sum short-term/current
    interest-bearing debt concepts too, when present.

    The committed 2330 fixture carries NO such concepts (grep -a over
    the raw fixture bytes for Shortterm*/Current*Borrowing*/Bond*/Lease*
    turned up only the excluded grab-bag
    tifrs-bsci-ci:LongtermLiabilitiesCurrentPortion — TSMC is cash-rich
    and genuinely has no short-term borrowings this quarter), so this
    uses a synthetic fact set (same pattern as the -fh test below) to
    prove the short-term component is summed in when present, without
    depending on a fixture that may never carry one.
    """
    _, canonical_mod = _load_modules()

    period = {"type": "instant", "instant": "2024-09-30"}

    def _fact(concept: str, value: float) -> dict:
        return {
            "concept": concept,
            "context_ref": "AsOf20240930",
            "raw_value": value,
            "decimals": "-3",
            "unit": "TWD",
            "period": period,
            "entity": "2330",
            "fact_type": "nonFraction",
        }

    facts = [
        _fact("ifrs-full:LongtermBorrowings", 26_459_677_000.0),
        _fact("ifrs-full:NoncurrentPortionOfNoncurrentBondsIssued", 909_703_588_000.0),
        _fact("ifrs-full:NoncurrentFinanceLeaseLiabilities", 28_208_721_000.0),
        _fact("ifrs-full:ShorttermBorrowings", 5_000_000_000.0),
    ]

    canonical = canonical_mod.build_canonical(facts)
    bs = canonical["balance_sheet"]

    # 26,459,677 + 909,703,588 + 28,208,721 + 5,000,000 = 969,371,986 (x1000)
    assert bs["total_debt"][0] == 969_371_986_000.0, (
        "total_debt must include ifrs-full:ShorttermBorrowings alongside "
        "the long-term components — pre-fix _DEBT_CONCEPTS silently "
        "dropped short-term debt, understating net_debt"
    )
    assert "ifrs-full:ShorttermBorrowings" in bs["_meta"]["total_debt"]["components"]


def test_canonical_ci_total_debt_formosa_includes_short_term():
    """Real end-to-end proof that _DEBT_CONCEPTS' 4 short-term/current
    concepts are genuine (not the prior commit's symmetry-guessed
    CurrentPortionOfNoncurrentBondsIssued / CurrentFinanceLeaseLiabilities,
    both confirmed WRONG/absent from real -ci taxonomy usage) — Formosa
    Plastics (1301) is a debt-heavy filer that carries all 7 _DEBT_CONCEPTS
    at once, unlike the cash-rich TSMC (2330) fixture which carries only
    the 3 long-term ones.

    Every component value below is grepped directly from the raw fixture
    bytes (grep -a, Big5 — iconv transliteration truncates on invalid byte
    sequences so grep -a on the original is the reliable path), AsOf20240930:
      ifrs-full:LongtermBorrowings                                              10,068,269
      ifrs-full:NoncurrentPortionOfNoncurrentBondsIssued                        33,459,485
      ifrs-full:NoncurrentFinanceLeaseLiabilities                                1,832,563
      ifrs-full:ShorttermBorrowings                                             27,254,461
      ifrs-full:CurrentPortionOfLongtermBorrowings                             20,951,680
      ifrs-full:CurrentBondsIssuedAndCurrentPortionOfNoncurrentBondsIssued       7,799,061
      ifrs-full:CurrentCommercialPapersIssuedAndCurrentPortionOfNoncurrentCommercialPapersIssued
                                                                                 35,205,850
    Sum = 136,571,369 (x1000, scale=3/decimals=-3) = 136,571,369,000.0
    """
    parser, canonical_mod = _load_modules()
    facts = _fixture_facts(parser, "twse_ixbrl_1301_2024Q3_C.html")

    expected_components = {
        "ifrs-full:LongtermBorrowings": 10_068_269_000.0,
        "ifrs-full:NoncurrentPortionOfNoncurrentBondsIssued": 33_459_485_000.0,
        "ifrs-full:NoncurrentFinanceLeaseLiabilities": 1_832_563_000.0,
        "ifrs-full:ShorttermBorrowings": 27_254_461_000.0,
        "ifrs-full:CurrentPortionOfLongtermBorrowings": 20_951_680_000.0,
        "ifrs-full:CurrentBondsIssuedAndCurrentPortionOfNoncurrentBondsIssued": 7_799_061_000.0,
        "ifrs-full:CurrentCommercialPapersIssuedAndCurrentPortionOfNoncurrentCommercialPapersIssued": 35_205_850_000.0,
    }
    for concept, expected_value in expected_components.items():
        matches = [
            f for f in facts if f["concept"] == concept and f["context_ref"] == "AsOf20240930"
        ]
        assert len(matches) == 1, (concept, matches)
        assert matches[0]["raw_value"] == expected_value, (concept, matches[0]["raw_value"])

    canonical = canonical_mod.build_canonical(facts)
    bs = canonical["balance_sheet"]

    assert bs["total_debt"][0] == 136_571_369_000.0, (
        "canonical total_debt must equal the real fixture's summed ST+LT "
        "debt components, not a symmetry-guessed value"
    )
    for concept in expected_components:
        assert concept in bs["_meta"]["total_debt"]["components"]


def test_canonical_bd_fact_set_returns_unsupported_marker():
    """"bd" (broker-dealer) has no registered builder yet (deferred
    sub-arc); build_canonical must return the parameterized unsupported
    marker "financial-bd", not the old hard-coded "financial-fh" ("fh" and
    "basi" now have their own builders, see test_canonical_fh_from_2882_fixture
    and test_canonical_basi_from_2801_fixture)."""
    _, canonical_mod = _load_modules()

    # Synthetic -bd fact set — a minimal stand-in exercising the
    # registry-fallback path for a still-unbuilt financial family.
    bd_facts = [
        {
            "concept": "tifrs-bsci-bd:InterestIncome",
            "context_ref": "From20240101To20240930",
            "raw_value": 123.0,
            "decimals": "-3",
            "unit": "TWD",
            "period": {"type": "duration", "start": "2024-01-01", "end": "2024-09-30"},
            "entity": "6005",
            "fact_type": "nonFraction",
        },
    ]

    result = canonical_mod.build_canonical(bd_facts)

    assert result.get("unsupported") == "financial-bd", result


def test_canonical_fh_from_2882_fixture():
    """-fh (financial holding) canonical builder (Task 5), traced against
    the real 2882 (國泰金控 Cathay FHC) 2026 Q1 fixture. Measured values
    verbatim from scratchpad/fh-measurement.md §2882.

    net_income maps to ifrs-full:ProfitLossAttributableToOwnersOfParent (the
    consolidated attributable-to-owners bottom line, 31,593,811,000) — NOT
    tifrs-bsci-fh:NetIncomeLoss (72,538,053,000, a different
    pre-elimination subtotal per the measurement doc's Q1 2026 note); this
    test pins the deliberate choice. The key is named net_income (not
    profit) to match the -ci _CONCEPT_MAP convention that pack_tw.py's
    consumer code actually reads (code-quality review round 2 🟡 fix).

    DCF-trigger fields (revenue/ebit/fcf/capex/total_debt) must be absent
    everywhere so downstream DCF fails loud instead of silently zeroing
    against a financial-holding balance sheet DCF was never designed for.
    """
    parser, canonical_mod = _load_modules()
    facts = _fixture_facts_tolerant(parser, "twse_ixbrl_2882_2026Q1_C.html")

    canonical = canonical_mod.build_canonical(facts)

    assert canonical.get("sector_class") == "financial", canonical
    assert canonical.get("taxonomy") == "fh", canonical

    bs = canonical["balance_sheet"]
    inc = canonical["income_statement"]

    assert bs["total_equity"][0] == 817_026_831_000.0
    assert bs["_meta"]["total_equity"]["concept"] == "ifrs-full:Equity"

    # deposits = DepositsFromCustomers + DepositsFromBanks, kept distinct
    # from interest-bearing borrowings (both populated, both non-empty).
    assert bs["deposits"][0] == 4_668_307_129_000.0, (
        "deposits must sum DepositsFromCustomers (4,463,453,341,000) + "
        "DepositsFromBanks (204,853,788,000)"
    )
    assert bs["borrowings"][0] == 490_504_772_000.0, (
        "borrowings must sum BondsIssued (289,577,614,000) + "
        "OtherBorrowings (48,341,814,000) + CommercialPapersIssuedNet "
        "(104,741,415,000) + SecuritiesSoldUnderRepurchaseAgreements "
        "(47,843,929,000) — distinct from deposits"
    )
    assert "ifrs-full:DepositsFromCustomers" in bs["_meta"]["deposits"]["components"]
    assert "ifrs-full:DepositsFromBanks" in bs["_meta"]["deposits"]["components"]
    assert "ifrs-full:BondsIssued" in bs["_meta"]["borrowings"]["components"]
    assert (
        "tifrs-bsci-fh:SecuritiesSoldUnderRepurchaseAgreements"
        in bs["_meta"]["borrowings"]["components"]
    )

    assert inc["net_income"][0] == 31_593_811_000.0
    assert (
        inc["_meta"]["net_income"]["concept"]
        == "ifrs-full:ProfitLossAttributableToOwnersOfParent"
    )
    assert inc["net_interest_income"][0] == 76_415_488_000.0
    assert inc["eps_basic"][0] == 2.15

    # DCF-trigger fields must be absent everywhere (fail loud, not silent-0).
    dcf_trigger_keys = {"revenue", "ebit", "fcf", "capex", "total_debt"}
    for statement in ("balance_sheet", "income_statement", "cash_flow"):
        keys = set(canonical.get(statement, {}))
        assert not (keys & dcf_trigger_keys), (statement, keys & dcf_trigger_keys)


def test_canonical_fh_deposits_borrowings_degrade_gracefully_when_concept_missing():
    """Code-quality review round 2 🟡 fix: real -fh filers do not all carry
    every borrowing/deposit concept (measured: CTBC 2891 has no
    ifrs-full:OtherBorrowings at all — see scratchpad/fh-measurement.md
    §2891). _sum_concepts (shared by deposits/borrowings) must sum only
    whichever components are present rather than crashing on a missing one
    — this pins that graceful-degradation behavior, previously verified
    by hand but untested (mirrors the -ci pattern at
    test_canonical_ci_total_debt_sums_short_term_debt_when_present).
    """
    _, canonical_mod = _load_modules()

    period = {"type": "instant", "instant": "2026-03-31"}

    def _fact(concept: str, value: float) -> dict:
        return {
            "concept": concept,
            "context_ref": "AsOf20260331",
            "raw_value": value,
            "decimals": "-3",
            "unit": "TWD",
            "period": period,
            "entity": "2891",
            "fact_type": "nonFraction",
        }

    facts = [
        # Deposits: only DepositsFromCustomers present (DepositsFromBanks
        # missing).
        _fact("ifrs-full:DepositsFromCustomers", 5_817_260_379_000.0),
        # Borrowings: BondsIssued + repo present, OtherBorrowings ABSENT
        # (the real CTBC gap) and CommercialPapersIssuedNet absent too.
        _fact("ifrs-full:BondsIssued", 212_161_628_000.0),
        _fact(
            "tifrs-bsci-fh:SecuritiesSoldUnderRepurchaseAgreements",
            291_754_911_000.0,
        ),
        # tifrs-bsci-fh concept required so classify_taxonomy routes "fh".
        _fact("tifrs-bsci-fh:NetInterestIncomeExpense", 41_556_941_000.0),
    ]

    canonical = canonical_mod.build_canonical(facts)
    bs = canonical["balance_sheet"]

    assert bs["deposits"][0] == 5_817_260_379_000.0, (
        "deposits must sum only the present component "
        "(DepositsFromCustomers), not crash on missing DepositsFromBanks"
    )
    assert bs["_meta"]["deposits"]["components"] == ["ifrs-full:DepositsFromCustomers"]

    assert bs["borrowings"][0] == 503_916_539_000.0, (
        "borrowings must sum only the present components (BondsIssued + "
        "repo), not crash on missing OtherBorrowings/CommercialPapersIssuedNet"
    )
    assert bs["_meta"]["borrowings"]["components"] == [
        "ifrs-full:BondsIssued",
        "tifrs-bsci-fh:SecuritiesSoldUnderRepurchaseAgreements",
    ]


def test_canonical_basi_from_2801_fixture():
    """-basi (standalone commercial bank / bills-finance) canonical builder
    (Task 6), traced against the real 2801 (彰化商業銀行 Chang Hwa Bank)
    2026 Q1 fixture. Measured values verbatim from
    scratchpad/fh-measurement-round2.md §2801 and cross-checked directly
    against the parsed fixture bytes.

    net_income maps to ifrs-full:ProfitLossAttributableToOwnersOfParent —
    the SAME concept -fh uses (present verbatim for standalone banks too,
    5,221,136,000) — and eps_basic to ifrs-full:BasicEarningsLossPerShare
    (0.44), matching the -ci/-fh net_income/eps_basic key convention (NOT
    profit/eps).

    Deposits reuse the exact same concept pair -fh sums
    (DepositsFromCustomers + DepositsFromBanks — both PRESENT verbatim for
    2801, round2 measurement). Borrowings use the -basi-renamed repo
    concept tifrs-bsci-basi:NotesAndBondsIssuedUnderRepurchaseAgreement —
    2801's analog of -fh's tifrs-bsci-fh:SecuritiesSoldUnderRepurchaseAgreements
    (round2: "renamed, different namespace"); 2801 carries no analog of
    ifrs-full:BondsIssued/OtherBorrowings/tifrs-bsci-fh:CommercialPapersIssuedNet
    at all this quarter (round2: "MISSING all 3", confirmed absent in the
    fixture), so borrowings ends up populated from the repo concept alone.

    DCF-trigger fields (revenue/ebit/fcf/capex/total_debt) must be absent
    everywhere, same as -fh — a standalone bank's balance sheet has no such
    lines and DCF must fail loud rather than silently zero.
    """
    parser, canonical_mod = _load_modules()
    facts = _fixture_facts_tolerant(parser, "twse_ixbrl_2801_2026Q1_C.html")

    canonical = canonical_mod.build_canonical(facts)

    assert canonical.get("sector_class") == "financial", canonical
    assert canonical.get("taxonomy") == "basi", canonical

    bs = canonical["balance_sheet"]
    inc = canonical["income_statement"]

    assert bs["total_equity"][0] == 225_976_725_000.0
    assert bs["_meta"]["total_equity"]["concept"] == "ifrs-full:Equity"
    assert bs["total_assets"][0] == 3_481_563_454_000.0
    assert bs["cash"][0] == 40_993_679_000.0

    # deposits = DepositsFromCustomers (2,774,469,785,000) +
    # DepositsFromBanks (348,285,729,000), kept distinct from borrowings.
    assert bs["deposits"][0] == 3_122_755_514_000.0
    assert "ifrs-full:DepositsFromCustomers" in bs["_meta"]["deposits"]["components"]
    assert "ifrs-full:DepositsFromBanks" in bs["_meta"]["deposits"]["components"]

    # borrowings = the -basi-renamed repo concept alone (32,571,432,000);
    # BondsIssued/OtherBorrowings/CommercialPapersIssuedNet are genuinely
    # absent this quarter (round2 measurement), so they never enter the sum.
    assert bs["borrowings"][0] == 32_571_432_000.0
    assert bs["_meta"]["borrowings"]["components"] == [
        "tifrs-bsci-basi:NotesAndBondsIssuedUnderRepurchaseAgreement"
    ]

    assert inc["net_income"][0] == 5_221_136_000.0
    assert (
        inc["_meta"]["net_income"]["concept"]
        == "ifrs-full:ProfitLossAttributableToOwnersOfParent"
    )
    assert inc["eps_basic"][0] == 0.44

    dcf_trigger_keys = {"revenue", "ebit", "fcf", "capex", "total_debt"}
    for statement in ("balance_sheet", "income_statement", "cash_flow"):
        keys = set(canonical.get(statement, {}))
        assert not (keys & dcf_trigger_keys), (statement, keys & dcf_trigger_keys)


def test_canonical_basi_bills_finance_2820_degrades_gracefully():
    """-basi's bills-finance sub-shape (round4 measurement: 華票 China
    Bills Finance reuses the same tifrs-bsci-basi taxonomy as standalone
    banks) must produce a valid canonical without crashing, even though
    it carries a materially thinner fact set than a bank: no
    ifrs-full:ProfitLossAttributableToOwnersOfParent at all this quarter
    (confirmed absent in the fixture — 2820 only carries the unattributed
    ifrs-full:ProfitLoss, 639,894,000, which is NOT the concept the -basi/
    -fh net_income key maps to) and no ifrs-full:DepositsFromCustomers
    (confirmed absent — round4: "no customer-deposit-taking concepts at
    all"). This pins _sum_concepts' missing-concept tolerance (already
    proven for -fh) extending cleanly to -basi's bills-finance sub-shape.

    Note (measured, narrower than round4's summary framing): 2820 is NOT
    fully deposit-less — ifrs-full:DepositsFromBanks (interbank funding,
    29,462,554,000) IS present, so the "deposits" field ends up populated
    from that component alone; the component list is asserted below to
    confirm DepositsFromCustomers specifically (the true customer-deposit-
    taking signal) is what's absent, not the whole field.
    """
    parser, canonical_mod = _load_modules()
    facts = _fixture_facts_tolerant(parser, "twse_ixbrl_2820_2026Q1_A.html")

    canonical = canonical_mod.build_canonical(facts)

    assert canonical.get("sector_class") == "financial", canonical
    assert canonical.get("taxonomy") == "basi", canonical

    bs = canonical["balance_sheet"]
    inc = canonical["income_statement"]

    assert bs["total_assets"][0] == 264_308_740_000.0
    assert bs["total_equity"][0] == 27_875_094_000.0
    assert bs["cash"][0] == 326_912_000.0

    # net_income degrades gracefully to absent: ProfitLossAttributableTo
    # OwnersOfParent is not in this filer's fact set this quarter, and the
    # builder must not crash or fabricate it from ifrs-full:ProfitLoss.
    assert "net_income" not in inc, inc
    assert inc["eps_basic"][0] == 0.48

    # deposits: only DepositsFromBanks contributes (customer deposits
    # genuinely absent).
    assert bs["_meta"]["deposits"]["components"] == ["ifrs-full:DepositsFromBanks"]
    assert bs["deposits"][0] == 29_462_554_000.0

    # borrowings: the -basi-renamed repo concept is present and, for a
    # bills-finance filer, is the dominant funding line.
    assert bs["borrowings"][0] == 203_085_773_000.0

    dcf_trigger_keys = {"revenue", "ebit", "fcf", "capex", "total_debt"}
    for statement in ("balance_sheet", "income_statement", "cash_flow"):
        keys = set(canonical.get(statement, {}))
        assert not (keys & dcf_trigger_keys), (statement, keys & dcf_trigger_keys)
