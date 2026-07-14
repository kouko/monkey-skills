"""test_sec_xval.py — offline unit coverage for Source A statement-cell
extraction (`sec_edgar_client.extract_statement_cells`), addressing the
code-quality-reviewer round-1 NEEDS_REVISION findings on Task 1
(docs/loom/plans/2026-07-13-us-sec-financial-table-xval.md):

  - FINDING 1: a row_index miss (a fact concept with no matching
    `get_statement` row) must surface visibly via `_log`, not silently
    degrade `citation.row` to `None`.
  - FINDING 2: `extract_statement_cells`' own logic (NaN-skip,
    instant/duration period branching, dimension building, row/col
    citation join) had zero offline-CI-exercised coverage — the only
    existing test is `@pytest.mark.network`
    (test_data_markets_live.py::test_extract_statement_cells_live_shape),
    which never runs in offline CI (no edgartools installed there).

The fact records below mirror the REAL edgartools 5.42.0 shape captured
live 2026-07-13 (sec_edgar_client.py module-header note, lines ~1582-1605)
cross-checked against tests/analysis/fixtures/xval_source_a_aapl_bs.json —
never hand-invented (fixtures-mirror-producer-shape discipline). A
plain-object stand-in for `filing` implements only the exact 3-call
surface `extract_statement_cells` reads (`.xbrl().get_statement(name)`,
`.xbrl().facts.to_dataframe().to_dict("records")`, `.accession_no`), so no
real pandas DataFrame or edgartools install is needed offline.

This file is also where the accompanying testability refactor in
sec_edgar_client.py pays off: the production code used to filter with
pandas boolean indexing (`facts_df[facts_df["statement_type"] ==
statement_name]`) BEFORE `.to_dict("records")`; it now calls
`.to_dict("records")` first and filters with a plain list comprehension,
so `_build_statement_cells` (the actual cell-building loop) runs on plain
dicts and needs no real pandas to exercise.

Run offline (exact CI command — no extra --with):
  uv run --quiet --with pytest --with 'pyyaml>=6.0' \
    pytest investing-toolkit/tests/ -m "not network" -q --tb=short

Task 2 (StatementNotFound fail-loud wrapping, same plan) extends this SAME
file with its own test(s) — the `sec_client` fixture below is written to
be reused, not reworked.

No `@req` tags: this dispatch (code-quality-reviewer round-1 revision on
Task 1) carries no registered REQ-ids — see implementer report.
"""
from __future__ import annotations

import importlib
import importlib.util
import sys
from pathlib import Path
from unittest import mock

import pytest

ROOT = Path(__file__).resolve().parents[2]
MARKETS_SCRIPTS = ROOT / "skills" / "data-markets" / "scripts"
XVAL_SCRIPT = ROOT / "skills" / "analysis-xval" / "scripts" / "xval_compute.py"


@pytest.fixture
def sec_client():
    """Import sec_edgar_client with `edgar` AND `requests` stubbed in
    sys.modules. Offline CI installs ONLY pytest + pyyaml, so neither
    edgartools nor requests is importable there. `extract_statement_cells`
    itself never touches either module (it operates purely on the `filing`
    object passed in), but the module's top-level `import requests as
    _requests` still runs at import time and would fail without the stub
    (identical pattern + reasoning as test_sec_narrative.py's `sec_client`
    fixture). Restores prior sys.modules state on teardown."""
    if str(MARKETS_SCRIPTS) not in sys.path:
        sys.path.insert(0, str(MARKETS_SCRIPTS))
    edgar_stub = mock.MagicMock(name="edgar")
    requests_stub = mock.MagicMock(name="requests")
    saved_edgar = sys.modules.get("edgar")
    saved_requests = sys.modules.get("requests")
    saved_client = sys.modules.get("sec_edgar_client")
    sys.modules["edgar"] = edgar_stub
    sys.modules["requests"] = requests_stub
    sys.modules.pop("sec_edgar_client", None)
    module = importlib.import_module("sec_edgar_client")
    try:
        yield module
    finally:
        if saved_edgar is not None:
            sys.modules["edgar"] = saved_edgar
        else:
            sys.modules.pop("edgar", None)
        if saved_requests is not None:
            sys.modules["requests"] = saved_requests
        else:
            sys.modules.pop("requests", None)
        if saved_client is not None:
            sys.modules["sec_edgar_client"] = saved_client
        else:
            sys.modules.pop("sec_edgar_client", None)


class _FakeRecordTable:
    """Stand-in for the pandas DataFrame `filing.xbrl().facts.to_dataframe()`
    returns — implements only `.to_dict("records")`, the sole method
    `extract_statement_cells` calls on it post-refactor."""

    def __init__(self, records):
        self._records = records

    def to_dict(self, orient):
        assert orient == "records", f"extract_statement_cells must ask for records, got {orient!r}"
        return self._records


class _FakeFacts:
    def __init__(self, records):
        self._records = records

    def to_dataframe(self):
        return _FakeRecordTable(self._records)


class _FakeXBRL:
    def __init__(self, rendered_rows, fact_records):
        self._rendered_rows = rendered_rows
        self.facts = _FakeFacts(fact_records)

    def get_statement(self, name):
        return self._rendered_rows


class _FakeFiling:
    """Stand-in for edgartools' Filing — the exact surface
    `extract_statement_cells` reads: `.xbrl()` and `.accession_no`."""

    def __init__(self, accession, rendered_rows, fact_records):
        self.accession_no = accession
        self._xb = _FakeXBRL(rendered_rows, fact_records)

    def xbrl(self):
        return self._xb


ACCESSION = "0000320193-25-000079"

# Rendered rows mirror get_statement's row-ordered list (module-header note
# + fixture xval_source_a_aapl_bs.json rows 30/31): row POSITION is reused
# as the cell citation's `row`.
RENDERED_ROWS = [
    {"concept": "us-gaap_AccountsReceivableNetCurrent"},  # row 0
    {"concept": "us-gaap_NontradeReceivablesCurrent"},  # row 1
]


def _instant_fact(**overrides):
    """A baseline real-shaped BalanceSheet fact record (mirrors
    xval_source_a_aapl_bs.json's first cell), overridable per test."""
    fact = {
        "concept": "us-gaap:AccountsReceivableNetCurrent",
        "statement_type": "BalanceSheet",
        "value": "39777000000",
        "numeric_value": 39777000000.0,
        "decimals": "-6",
        "period_type": "instant",
        "period_instant": "2025-09-27",
        "period_start": None,
        "period_end": None,
        "period_key": "instant_2025-09-27",
        "is_dimensioned": False,
        "dimension": None,
        "member": None,
        "label": "Accounts receivable, net",
        "context_ref": "c-20",
        "fact_id": "f-163",
    }
    fact.update(overrides)
    return fact


def test_extract_statement_cells_builds_instant_cell_with_row_col_citation(sec_client):
    facts = [_instant_fact()]
    filing = _FakeFiling(ACCESSION, RENDERED_ROWS, facts)

    cells = sec_client.extract_statement_cells(filing, "BalanceSheet")

    assert len(cells) == 1
    cell = cells[0]
    assert cell["concept"] == "us-gaap:AccountsReceivableNetCurrent"
    assert cell["period"] == {"type": "instant", "instant": "2025-09-27"}
    assert cell["dimension"] is None
    assert cell["numeric_value"] == 39777000000.0
    assert cell["decimals"] == "-6"
    assert cell["citation"] == {
        "accession": ACCESSION,
        "statement_name": "BalanceSheet",
        "row": 0,
        "col": "instant_2025-09-27",
        "label": "Accounts receivable, net",
        "context_ref": "c-20",
        "fact_id": "f-163",
    }


def test_extract_statement_cells_skips_nan_numeric_value(sec_client):
    facts = [
        _instant_fact(numeric_value=float("nan"), context_ref="c-nan", fact_id="f-nan"),
        _instant_fact(),
    ]
    filing = _FakeFiling(ACCESSION, RENDERED_ROWS, facts)

    cells = sec_client.extract_statement_cells(filing, "BalanceSheet")

    assert len(cells) == 1, "the NaN placeholder-concept fact must be skipped, never fabricated"
    assert cells[0]["citation"]["fact_id"] == "f-163"


def test_extract_statement_cells_duration_period(sec_client):
    facts = [
        _instant_fact(
            concept="us-gaap:NontradeReceivablesCurrent",
            period_type="duration",
            period_instant=None,
            period_start="2024-09-29",
            period_end="2025-09-27",
            period_key="duration_2024-09-29_2025-09-27",
            context_ref="c-30",
            fact_id="f-200",
        )
    ]
    filing = _FakeFiling(ACCESSION, RENDERED_ROWS, facts)

    cells = sec_client.extract_statement_cells(filing, "BalanceSheet")

    assert len(cells) == 1
    assert cells[0]["period"] == {
        "type": "duration",
        "start": "2024-09-29",
        "end": "2025-09-27",
    }
    assert cells[0]["citation"]["row"] == 1


def test_extract_statement_cells_dimensional_fact_builds_axis_member(sec_client):
    facts = [
        _instant_fact(
            is_dimensioned=True,
            dimension="srt:ProductOrServiceAxis",
            member="aapl:IPhoneMember",
            context_ref="c-dim",
            fact_id="f-dim",
        )
    ]
    filing = _FakeFiling(ACCESSION, RENDERED_ROWS, facts)

    cells = sec_client.extract_statement_cells(filing, "BalanceSheet")

    assert len(cells) == 1
    assert cells[0]["dimension"] == {
        "axis": "srt:ProductOrServiceAxis",
        "member": "aapl:IPhoneMember",
    }


def test_extract_statement_cells_filters_to_requested_statement_type(sec_client):
    facts = [
        _instant_fact(statement_type="IncomeStatement", context_ref="c-other", fact_id="f-other"),
        _instant_fact(),
    ]
    filing = _FakeFiling(ACCESSION, RENDERED_ROWS, facts)

    cells = sec_client.extract_statement_cells(filing, "BalanceSheet")

    assert len(cells) == 1, "a fact from a different statement_type must not leak in"
    assert cells[0]["citation"]["fact_id"] == "f-163"


def test_extract_raises_on_absent_statement(sec_client):
    """Task 2: an absent/unparseable statement (edgartools' `StatementNotFound`
    on `get_statement`) must surface as a loud extraction-failure slot — never
    an uncaught crash bubbling out unclassified, and never a silent empty
    cell list or a regex/free-text-scraped fallback value."""

    class _StatementNotFound(Exception):
        """Stand-in for edgartools' real StatementNotFound; the production
        code catches broadly (matching this file's existing acquire-error
        convention at `_acquire_raw_filing`/`_extraction_error_slot`), so a
        plain Exception subclass is sufficient here."""

    class _RaisingXBRL:
        def get_statement(self, name):
            raise _StatementNotFound(f"statement {name!r} not found")

    filing = _FakeFiling(ACCESSION, RENDERED_ROWS, [])
    filing._xb = _RaisingXBRL()

    result = sec_client.extract_statement_cells(filing, "CashFlowStatement")

    assert isinstance(result, dict), (
        "an absent statement must surface a loud error-slot dict — not raise "
        "uncaught, and not return a silent empty/fabricated cell list"
    )
    assert result["error_class"] == "statement_not_found"
    assert result["statement_name"] == "CashFlowStatement"
    assert "CashFlowStatement" in result["error"]


def _load_xval_compute():
    """Load xval_compute.py directly via importlib (same convention as
    tests/analysis/test_analysis_xval.py's `xval_module` fixture) so the
    Source-B pack producer/consumer contract round-trip below exercises the
    REAL `build_source_b_index`, not a re-implementation of its logic."""
    spec = importlib.util.spec_from_file_location("xval_compute_roundtrip", XVAL_SCRIPT)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules["xval_compute_roundtrip"] = module
    spec.loader.exec_module(module)
    return module


def _raw_companyfacts_payload():
    """Mirror the REAL SEC companyfacts JSON nesting: `data["facts"][taxonomy][tag]`
    is a units-object (label/description/units), NOT a bare row list — `units.USD`
    carries the row series `summarize_concept` already knows how to flatten."""
    return {
        "cik": 320193,
        "entityName": "Apple Inc.",
        "facts": {
            "us-gaap": {
                "Revenues": {
                    "label": "Revenues",
                    "description": "Amount of revenue recognized from goods sold...",
                    "units": {
                        "USD": [
                            {
                                "start": "2023-10-01",
                                "end": "2024-09-28",
                                "val": 391035000000,
                                "accn": "0000320193-24-000123",
                                "fy": 2024,
                                "fp": "FY",
                                "form": "10-K",
                                "filed": "2024-11-01",
                                "frame": "CY2024",
                            },
                        ]
                    },
                }
            }
        },
    }


def test_build_companyfacts_pack_shape(sec_client):
    """Task 1 (plan: docs/loom/plans/2026-07-13-us-sec-xval-memo-wiring.md) —
    the Open-Q2 keystone: `build_companyfacts_pack(cik)` fetches via the
    existing `fetch_facts` and reshapes the raw companyfacts payload into the
    EXACT Source-B pack shape `xval_compute.build_source_b_index` requires:
    `{"cik", "facts": {"<taxonomy>": {"<tag>": [<row>, ...]}}}`, each row in
    the `summarize_concept` shape."""
    cik = 320193
    fetched = {
        "cik": cik,
        "concept": None,
        "fetched_at": "2026-07-13T00:00:00Z",
        "_cache": "miss",
        "data": _raw_companyfacts_payload(),
    }
    with mock.patch.object(sec_client, "fetch_facts", return_value=fetched) as mocked:
        pack = sec_client.build_companyfacts_pack(cik)

    mocked.assert_called_once_with(cik, None)
    assert pack["cik"] == cik
    assert set(pack["facts"].keys()) == {"us-gaap"}
    rows = pack["facts"]["us-gaap"]["Revenues"]
    assert rows == [
        {
            "start": "2023-10-01",
            "end": "2024-09-28",
            "value": 391035000000,
            "accn": "0000320193-24-000123",
            "form": "10-K",
            "fy": 2024,
            "fp": "FY",
            "filed": "2024-11-01",
        }
    ], "each row must be exactly the summarize_concept shape (start/end/value/accn/form/fy/fp/filed)"

    # Contract round-trip (the seam that bit the arc): the built pack must
    # feed the REAL build_source_b_index without error and produce a
    # non-empty index, proving the producer emits exactly what the consumer
    # needs.
    xval_compute = _load_xval_compute()
    index = xval_compute.build_source_b_index(pack)
    assert index, "round-trip through build_source_b_index must be non-empty"
    assert ("us-gaap:Revenues", ("duration", "2023-10-01", "2024-09-28")) in index


def test_build_companyfacts_pack_returns_error_slot_on_fetch_failure(sec_client):
    """On a companyfacts fetch error, `build_companyfacts_pack` must return a
    loud error slot (mirroring this file's `_acquire_error` convention) —
    NEVER a fabricated/empty Source-B pack."""
    cik = 320193
    with mock.patch.object(
        sec_client,
        "fetch_facts",
        return_value={"error": "SEC EDGAR rate-limited (429) after retries"},
    ):
        pack = sec_client.build_companyfacts_pack(cik)

    assert "error" in pack
    assert "error_class" in pack
    assert "facts" not in pack, "a fetch failure must never fabricate a Source-B pack"


def test_extract_statement_cells_logs_on_row_index_miss(sec_client, capsys):
    """FINDING 1: a fact concept with no matching get_statement row must
    surface via `_log` (sec_edgar_client.py's `row = row_index.get(row_key)`
    branch) — never silently degrade `citation.row` to `None` unnoticed."""
    facts = [
        _instant_fact(
            concept="us-gaap:SomeUnrenderedOrphanConcept",
            context_ref="c-orphan",
            fact_id="f-orphan",
        )
    ]
    filing = _FakeFiling(ACCESSION, RENDERED_ROWS, facts)

    cells = sec_client.extract_statement_cells(filing, "BalanceSheet")

    assert len(cells) == 1
    assert cells[0]["citation"]["row"] is None  # schema unchanged: row may still be None
    stderr = capsys.readouterr().err
    assert "SomeUnrenderedOrphanConcept" in stderr, (
        f"expected the orphaned concept named in stderr for visibility, got: {stderr!r}"
    )
