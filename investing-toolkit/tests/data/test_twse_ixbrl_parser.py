"""test_twse_ixbrl_parser.py — OFFLINE regression test for
twse_ixbrl_parser.parse_ixbrl_facts against the committed TSMC 2330
2024Q3 consolidated iXBRL fixture (docs/loom/plans/2026-07-19-tw-ixbrl-
ingestion.md, Task 1).

Guards the DOM-drop gotcha (brief edge case #10): a naive lxml/DOM parse
over this fixture drops facts nested inside <td> via HTML tree-repair
(measured TSMC DOM-iter=387 vs true=2002) — this test's exact-count
assertion is the regression guard against that bug ever creeping back
in via a future library swap. The parser under test extracts via regex
over `ix:nonFraction`/`ix:nonNumeric` tags, never DOM traversal.

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


def _load_parser():
    if str(MARKETS_SCRIPTS) not in sys.path:
        sys.path.insert(0, str(MARKETS_SCRIPTS))
    import twse_ixbrl_parser
    return twse_ixbrl_parser


def _fixture_document() -> str:
    # TW MOPS t164sb01 responses are Big5-encoded; the parser itself takes
    # an already-decoded str (decoding is the fetch layer's job — Task 2).
    return (FIXTURES / "twse_ixbrl_2330_2024Q3_C.html").read_text(encoding="big5")


def test_parse_tsmc_golden():
    mod = _load_parser()
    facts = mod.parse_ixbrl_facts(_fixture_document())

    # Primary guard: the DOM-drop gotcha. Must hold regardless of the
    # per-type split below.
    assert len(facts) == 2002, (
        "must extract exactly 2002 facts — the DOM-drop guard (a DOM/"
        "tree-repair parse over this same fixture silently drops ~85% of "
        "facts nested inside <td>, measured 387 vs true 2002)"
    )

    numeric_facts = [f for f in facts if f["fact_type"] == "nonFraction"]
    text_facts = [f for f in facts if f["fact_type"] == "nonNumeric"]
    assert len(numeric_facts) == 1552
    assert len(text_facts) == 450

    # Traced golden fact: ifrs-full:CurrentFinancialAssetsAtFairValue
    # ThroughOtherComprehensiveIncome, AsOf20240930, decimals=-3.
    # Fixture raw text is "189,649,314"; decimals=-3/scale=3 means the
    # true value is the raw text times 1000.
    golden = [
        f
        for f in facts
        if f["concept"]
        == "ifrs-full:CurrentFinancialAssetsAtFairValueThroughOtherComprehensiveIncome"
        and f["context_ref"] == "AsOf20240930"
    ]
    assert len(golden) == 1, golden
    fact = golden[0]
    assert fact["decimals"] == "-3"
    assert fact["raw_value"] == pytest.approx(189_649_314_000.0), (
        "decimals=-3 raw value must be scaled x1000: 189,649,314 -> "
        "189,649,314,000"
    )
    # context_ref resolved to its period (instant context here) + entity.
    assert fact["period"] == {"type": "instant", "instant": "2024-09-30"}
    assert fact["entity"] == "2330"
    assert fact["unit"] == "TWD"


def test_parse_duration_context_resolves_start_end():
    mod = _load_parser()
    facts = mod.parse_ixbrl_facts(_fixture_document())

    duration_facts = [f for f in facts if f["context_ref"] == "From20240101To20240930"]
    assert duration_facts, "fixture must contain at least one duration-context fact"
    for fact in duration_facts:
        assert fact["period"] == {
            "type": "duration",
            "start": "2024-01-01",
            "end": "2024-09-30",
        }


def test_parse_sign_attribute_negates_value():
    mod = _load_parser()
    facts = mod.parse_ixbrl_facts(_fixture_document())

    # ifrs-full:OtherEquityInterest AsOf20231231 carries sign="-" in the
    # fixture — a negative-value fact must come out negated, not silently
    # dropped or left positive.
    negated = [
        f
        for f in facts
        if f["concept"] == "ifrs-full:OtherEquityInterest"
        and f["context_ref"] == "AsOf20231231"
    ]
    assert len(negated) == 1, negated
    assert negated[0]["raw_value"] < 0


def test_parse_self_closing_nil_fact_is_kept():
    mod = _load_parser()
    # A spec-valid self-closing ix:nonFraction (no paired closing tag) —
    # must be extracted, not silently dropped by the paired-only regex.
    document = """
    <xbrli:context id="AsOf20240101">
      <xbrli:entity><xbrli:identifier>2330</xbrli:identifier></xbrli:entity>
      <xbrli:period><xbrli:instant>2024-01-01</xbrli:instant></xbrli:period>
    </xbrli:context>
    <ix:nonFraction name="ifrs-full:SomeNilFact" contextRef="AsOf20240101"
      unitRef="TWD" decimals="0" xsi:nil="true"/>
    """
    facts = mod.parse_ixbrl_facts(document)

    nil_facts = [f for f in facts if f["concept"] == "ifrs-full:SomeNilFact"]
    assert len(nil_facts) == 1, "self-closing nil fact must not be dropped"
    fact = nil_facts[0]
    assert fact["raw_value"] is None
    assert fact["fact_type"] == "nonFraction"
    assert fact["context_ref"] == "AsOf20240101"
    assert fact["unit"] == "TWD"


def test_parse_fixture_fact_count_unaffected_by_self_closing_support():
    # The real fixture has zero self-closing ix: tags; adding self-closing
    # support must not change (double-count or otherwise) its fact count.
    mod = _load_parser()
    facts = mod.parse_ixbrl_facts(_fixture_document())
    assert len(facts) == 2002


def test_parse_scale_driven_not_decimals_driven_when_they_diverge():
    # tifrs-notes:PercentageOfOwnership4 carries decimals=4/scale=-2 with
    # raw text "100.00" (60+ occurrences in the real fixture, at varying
    # raw values across subsidiaries — this snippet fixes the exact attrs
    # from one such occurrence). scale and decimals diverge here: the
    # spec-correct value is scale-driven: 100.00 * 10**-2 = 1.0. A
    # decimals-driven multiplier would wrongly yield 0.01. This locks the
    # scale-driven behavior against a future regression.
    mod = _load_parser()
    document = (
        '<ix:nonFraction name="tifrs-notes:PercentageOfOwnership4" '
        'contextRef="AsOf20240930" format="ixt:numdotdecimal" scale="-2" '
        'decimals="4" unitRef="Pure">100.00</ix:nonFraction>'
    )
    facts = mod.parse_ixbrl_facts(document)

    assert len(facts) == 1
    fact = facts[0]
    assert fact["decimals"] == "4"
    assert fact["raw_value"] == pytest.approx(1.0), (
        "scale=-2 on raw text 100.00 must scale to 1.0, not 0.01"
    )


def test_parse_nonnumeric_exact_text_value():
    # End-to-end coverage of text-fact extraction beyond the sign case:
    # tifrs-notes:CompanyID is a single, stable nonNumeric fact in the
    # fixture with an exact known stripped value.
    mod = _load_parser()
    facts = mod.parse_ixbrl_facts(_fixture_document())

    company_id = [f for f in facts if f["concept"] == "tifrs-notes:CompanyID"]
    assert len(company_id) == 1, company_id
    assert company_id[0]["raw_value"] == "2330"
    assert company_id[0]["fact_type"] == "nonNumeric"
