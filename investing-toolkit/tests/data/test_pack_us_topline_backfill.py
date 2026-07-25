"""test_pack_us_topline_backfill.py — Task 4, docs/loom/plans/2026-07-25-
company-total-revenue.md: the `kpi-topline-backfill` pack.

Pins three behaviors: (1) the envelope shape mirrors `pack_kpi_quarterly`
plus the mandatory `source_kind` literal `"xbrl-companyfacts"` (the plan's
§Notes envelope provenance contract — Task 5 reads this exact literal off
the envelope, independently, per that contract); (2) the pack name
resolves through `SUPPORTED_PACKS` / `build_pack`; (3) a loud error slot
from the producer rides through verbatim (no fabricated facts key),
mirroring `pack_kpi_quarterly`'s failure-honesty convention.

Offline: `build_top_line_backfill` is stubbed at the `sec_edgar_client`
module boundary via `sys.modules`, mirroring `test_pack_facade.py`'s
`_stub_extractor` convention — `pack_us` lazy-imports the producer from
`sec_edgar_client` at call time (same lazy-import pattern
`pack_kpi_quarterly` uses for `extract_dimensional_revenue`), so the
offline suite never touches `requests`/`edgar`.

Run offline (no network marker; part of the default `not network` suite):
  PYTHONDONTWRITEBYTECODE=1 uv run --quiet --with pytest --with 'pyyaml>=6.0' \
    pytest investing-toolkit/tests/ -m "not network" -q --tb=short
"""
from __future__ import annotations

import sys
import types
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
MARKETS_SCRIPTS = ROOT / "skills" / "data-markets" / "scripts"

if str(MARKETS_SCRIPTS) not in sys.path:
    sys.path.insert(0, str(MARKETS_SCRIPTS))

import pack_us  # noqa: E402

# The ONE reshaped annual row `build_top_line_backfill` (Task 3) actually
# produces for NVDA's real captured FY2026 10-K fact (committed fixture
# `topline_probe_2026-07-25.json`: concept `us-gaap:Revenues`, value
# 215,938,000,000, period 2025-01-27->2026-01-25, accession
# 0001045810-26-000021, filed 2026-02-25 — the same real value/period/
# accession triple `test_sec_edgar_top_line_backfill.py`'s `_NVDA_*`
# constants pin). This exact dict is NOT hand-assembled: it is the
# verbatim output of invoking the real `build_top_line_backfill` with
# ONLY `resolve_cik`/`fetch_facts` stubbed to return that one real row
# (test_sec_edgar_top_line_backfill.py's `_stub_fetch` convention),
# copied here so this pack-layer test can stub the producer at its own
# call boundary without re-deriving the reshape logic (memory
# `hand-authored-fixture-is-a-fabrication-risk`: pairing a real value with
# a mismatched period/accession is exactly the failure this avoids).
#
# Provenance cite (memory `hand-authored-fixture-is-a-fabrication-risk`
# §How to apply): source accession 0001045810-26-000021, verified live
# 2026-07-25 (topline_probe_2026-07-25.json capture date). Regenerate by
# calling `sec_edgar_client.build_top_line_backfill("NVDA")` with only
# `resolve_cik` and `fetch_facts` stubbed (see `_stub_fetch` /
# `test_backfill_keeps_annual_rows_with_period_derived_fiscal_year` in
# test_sec_edgar_top_line_backfill.py) and copying its `facts[0]` verbatim.
ANNUAL_ROWS = [
    {
        "concept": "us-gaap:Revenues",
        "dimensions": {},
        "value": 215938000000.0,
        "period_start": "2025-01-27",
        "period_end": "2026-01-25",
        "accession": "0001045810-26-000021",
        "filed": "2026-02-25",
        "duration_months": 12,
        "duration_weeks": 52,
        "week_lane_band": "FY",
        "fiscal_year": 2026,
        "fiscal_quarter": "FY",
        "calendar_year": 2026,
        "calendar_quarter": "Q1",
    },
]


# The per-accession dei-shaped calendar map `build_top_line_backfill` emits
# alongside those facts, for the SAME real accession. `kpi_xbrl.
# _require_source_form` (kpi_xbrl.py:289-309) reads
# `fiscal_calendars[accession]["fiscal_period_focus"]` off the ENVELOPE, so a
# pack layer that drops this key rejects 100% of Lane A's facts at ingest —
# which is precisely what the two-lane e2e caught. Same provenance as
# ANNUAL_ROWS above (regenerate the same way).
FISCAL_CALENDARS = {
    "0001045810-26-000021": {
        "fiscal_period_focus": "FY",
        "fiscal_year_end": None,
        "fiscal_year_focus": None,
    },
}


def _stub_backfill(monkeypatch, fake_backfill) -> None:
    """`pack_kpi_topline_backfill` lazy-imports `build_top_line_backfill`
    from `sec_edgar_client` at call time; a sys.modules stub intercepts
    that import so the offline suite never touches requests/edgar."""
    fake_mod = types.ModuleType("sec_edgar_client")
    fake_mod.build_top_line_backfill = fake_backfill
    monkeypatch.setitem(sys.modules, "sec_edgar_client", fake_mod)


def test_topline_backfill_pack_envelope(monkeypatch):
    """Envelope carries pack name + the mandatory source_kind literal, and
    the producer's facts/coverage pass through verbatim (no analysis in
    the pack layer)."""
    calls: list[str] = []

    def fake_backfill(ticker):
        calls.append(ticker)
        return {
            "company": ticker,
            "facts": ANNUAL_ROWS,
            "coverage": {"skipped_rows": []},
            "fiscal_calendars": FISCAL_CALENDARS,
        }

    _stub_backfill(monkeypatch, fake_backfill)

    payload = pack_us.pack_kpi_topline_backfill("NVDA")

    assert payload["pack"] == "kpi-topline-backfill"
    assert payload["source_kind"] == "xbrl-companyfacts"
    assert payload["ticker"] == "NVDA"
    assert payload["facts"] == ANNUAL_ROWS
    assert payload["coverage"] == {"skipped_rows": []}
    assert payload["fiscal_calendars"] == FISCAL_CALENDARS
    assert calls == ["NVDA"]


def test_topline_backfill_pack_name_resolves_through_registry(monkeypatch):
    """`kpi-topline-backfill` is registered in `SUPPORTED_PACKS` and
    `build_pack` dispatches it to `pack_kpi_topline_backfill`, carrying
    the same envelope contract through the facade path."""
    _stub_backfill(
        monkeypatch,
        lambda ticker: {
            "company": ticker,
            "facts": ANNUAL_ROWS,
            "coverage": {"skipped_rows": []},
            "fiscal_calendars": FISCAL_CALENDARS,
        },
    )

    assert "kpi-topline-backfill" in pack_us.SUPPORTED_PACKS

    via_registry = pack_us.build_pack("kpi-topline-backfill", ["NVDA"])

    assert via_registry["pack"] == "kpi-topline-backfill"
    assert via_registry["source_kind"] == "xbrl-companyfacts"
    assert via_registry["facts"] == ANNUAL_ROWS
    assert via_registry["fiscal_calendars"] == FISCAL_CALENDARS


def test_topline_backfill_pack_passes_through_producer_error_slot(monkeypatch):
    """A loud error slot from `build_top_line_backfill` (e.g. no allowlist
    concept returned rows) rides through the envelope verbatim — mirrors
    `pack_kpi_quarterly`'s failure-honesty convention: no fabricated
    `facts` key on failure."""
    def fake_backfill(ticker):
        return {
            "error": f"SEC EDGAR top-line backfill failed for {ticker!r}: none",
            "error_class": "top_line_backfill_failed",
            "identifier": ticker,
        }

    _stub_backfill(monkeypatch, fake_backfill)

    payload = pack_us.pack_kpi_topline_backfill("ZZZZ")

    assert payload["pack"] == "kpi-topline-backfill"
    assert payload["error"] == (
        "SEC EDGAR top-line backfill failed for 'ZZZZ': none"
    )
    assert "facts" not in payload
