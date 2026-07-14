"""test_sec_edgar_dimensional_live.py — live-API anchor for
`sec_edgar_client.extract_dimensional_revenue` (Task 5,
docs/loom/plans/2026-07-14-operational-kpi-companyfacts-pilot.md).

Fetches AAPL's latest 10-K XBRL via real edgartools and asserts the
extractor's normalized dimensional-revenue fact-pack (the shape
tests/analysis/fixtures/xbrl_aapl_factpack.json declares) contains a real
aapl:IPhoneMember (srt:ProductOrServiceAxis) revenue fact — proving BOTH the
srt:* namespace path is reachable AND the full declared key set is emitted.
The 2018 tagging-regime shift moved Apple's product-line axis from
us-gaap:ProductOrServiceAxis to srt:ProductOrServiceAxis (the "Apple
false-negative lesson" the plan names) — a single-namespace filter would
silently drop this fact.

Marked @pytest.mark.network (registered in tests/data/conftest.py) so the
offline suite (`pytest -m "not network"`) stays green; `edgar` /
`sec_edgar_client` are imported inside the test body so offline collection
stays clean when edgartools is not installed. Run live:
  uv run --with pytest --with edgartools==5.42.0 --with requests \
    pytest investing-toolkit/tests/data/test_sec_edgar_dimensional_live.py \
    -m network
"""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
SCRIPTS = ROOT / "skills" / "data-markets" / "scripts"

_FACT_PACK_KEYS = {
    "concept", "axis", "member", "value",
    "period_end", "fiscal_year", "accession", "filed",
}


@pytest.mark.network
def test_extract_dimensional_revenue_aapl_live():
    if str(SCRIPTS) not in sys.path:
        sys.path.insert(0, str(SCRIPTS))
    import sec_edgar_client

    pack = sec_edgar_client.extract_dimensional_revenue("AAPL")

    assert "error" not in pack, f"extract_dimensional_revenue failed: {pack}"
    assert pack["company"] == "AAPL"
    facts = pack["facts"]
    assert isinstance(facts, list) and facts, "expected a non-empty facts list"

    for fact in facts:
        assert _FACT_PACK_KEYS <= set(fact), (
            f"fact missing a declared fact-pack key: {sorted(fact)}"
        )

    # The srt:* namespace path is reachable: Apple's post-2018 iPhone
    # product-line revenue is tagged srt:ProductOrServiceAxis /
    # aapl:IPhoneMember, NOT the pre-2018 us-gaap:ProductOrServiceAxis —
    # filtering a single namespace would silently drop this fact.
    iphone_facts = [
        f for f in facts
        if f["member"] == "aapl:IPhoneMember" and f["axis"] == "srt:ProductOrServiceAxis"
    ]
    assert iphone_facts, (
        "expected a real aapl:IPhoneMember revenue fact under "
        f"srt:ProductOrServiceAxis; got members={sorted({f['member'] for f in facts})}"
    )
    assert any(f["value"] > 100e9 for f in iphone_facts), (
        f"expected an iPhone revenue value > 100e9: {iphone_facts}"
    )

    # fiscal_year must be DERIVED from period_end (the year the fiscal
    # period ENDS), never taken from edgartools' raw `fiscal_year` column —
    # that column is unreliable for prior-year comparatives: in AAPL's 2025
    # 10-K, the iPhone fact with period_end 2024-09-28 is column-labeled
    # fiscal_year=2025 but is really FY2024. A prior-year comparative fact
    # (period_end starting "2024") must be labeled fiscal_year == 2024.
    prior_year_iphone_facts = [
        f for f in iphone_facts
        if f["period_end"] and f["period_end"].startswith("2024")
    ]
    assert prior_year_iphone_facts, (
        "expected a prior-year (period_end starting '2024') iPhone "
        f"comparative fact; got period_ends="
        f"{sorted({f['period_end'] for f in iphone_facts})}"
    )
    assert all(f["fiscal_year"] == 2024 for f in prior_year_iphone_facts), (
        "fiscal_year must derive from period_end, not edgartools' raw "
        f"fiscal_year column: {prior_year_iphone_facts}"
    )
