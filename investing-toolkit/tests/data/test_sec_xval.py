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
import sys
from pathlib import Path
from unittest import mock

import pytest

ROOT = Path(__file__).resolve().parents[2]
MARKETS_SCRIPTS = ROOT / "skills" / "data-markets" / "scripts"


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
