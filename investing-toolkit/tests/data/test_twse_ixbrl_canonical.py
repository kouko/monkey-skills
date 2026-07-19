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

ROOT = Path(__file__).resolve().parents[2]
MARKETS_SCRIPTS = ROOT / "skills" / "data-markets" / "scripts"
FIXTURES = Path(__file__).resolve().parent / "fixtures"


def _load_modules():
    if str(MARKETS_SCRIPTS) not in sys.path:
        sys.path.insert(0, str(MARKETS_SCRIPTS))
    import twse_ixbrl_canonical
    import twse_ixbrl_parser
    return twse_ixbrl_parser, twse_ixbrl_canonical


def _fixture_facts(parser) -> list[dict]:
    document = (FIXTURES / "twse_ixbrl_2330_2024Q3_C.html").read_text(encoding="big5")
    return parser.parse_ixbrl_facts(document)


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


def test_canonical_fh_fact_set_returns_unsupported_marker():
    _, canonical_mod = _load_modules()

    # Synthetic -fh (financial holding) fact set — no real -fh fixture is
    # committed (deferred sub-arc per plan Decision Log). The financial
    # holding taxonomy uses a "-fh" namespace token in place of "-ci"/
    # "-SCF"; this is a minimal synthetic stand-in for that shape.
    fh_facts = [
        {
            "concept": "tifrs-bsci-fh:InterestIncome",
            "context_ref": "From20240101To20240930",
            "raw_value": 123.0,
            "decimals": "-3",
            "unit": "TWD",
            "period": {"type": "duration", "start": "2024-01-01", "end": "2024-09-30"},
            "entity": "2801",
            "fact_type": "nonFraction",
        },
    ]

    result = canonical_mod.build_canonical(fh_facts)

    assert result.get("unsupported") == "financial-fh", result
