"""RED-first tests for analysis-kpi/scripts/kpi_spine_view.py — the pure
read-time view that resolves the 14 canonical spine fields out of the
store's AS-REPORTED concept series (plan
docs/loom/plans/2026-07-26-us-as-reported-statement-lane.md, Task 4).

Every fixture here is built by the REAL producer: points are appended
through `kpi_store.append` into a tmp store (`KPI_STORE_DIR`) and the input
payload is whatever `kpi_store.dump_company` actually emits — never a
hand-shaped guess at the pinned schema. The repo has been burned by
fixtures that encoded the consumer's assumption instead of the producer's
shape, and this module's whole contract is "consume the producer's payload,
emit the same shape".

The script paths are resolved locally (not via tests/analysis/conftest.py)
because this task's Files-touched list does not include conftest.py.

No `@req` tag: this dispatch's plan binds tasks by "Brief item covered", not
by registered loom-spec REQ-ids, so there is no id in the living-spec
namespace to bind these tests to (same convention as
test_kpi_store_read_cli.py).
"""
from __future__ import annotations

import importlib.util
import json
import os
import subprocess
import sys
from pathlib import Path

import pytest

_ROOT = Path(__file__).resolve().parents[2]
_SKILLS = _ROOT / "skills"
KPI_STORE_SCRIPT = _SKILLS / "analysis-kpi" / "scripts" / "kpi_store.py"
KPI_SPINE_VIEW_SCRIPT = _SKILLS / "analysis-kpi" / "scripts" / "kpi_spine_view.py"
TEARSHEET_FORMAT_SCRIPT = (
    _SKILLS / "report-kpi-tearsheet" / "scripts" / "tearsheet_format.py"
)

# A real accession shape, so the store's accession-derived `as_of` guard
# accepts every fixture point (a wall-clock or absent as_of is rejected).
_ACCESSION = "0000789019-25-000010"


def _load(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


@pytest.fixture
def store(tmp_path, monkeypatch):
    monkeypatch.setenv("KPI_STORE_DIR", str(tmp_path))
    return _load("kpi_store_for_spine_view", KPI_STORE_SCRIPT)


@pytest.fixture
def spine_view():
    return _load("kpi_spine_view_under_test", KPI_SPINE_VIEW_SCRIPT)


def _point(
    company: str,
    concept: str,
    label: str,
    start: str | None,
    end: str,
    value,
    as_of: str,
    kind: str = "duration",
) -> dict:
    """One store-valid as-reported point: the filer's own qname verbatim as
    `kpi_id` (Task 3's pin), full provenance, accession-derived as_of.
    """
    return {
        "company": company,
        "kpi_id": concept,
        "period": label,
        "period_start": start,
        "period_end": end,
        "period_kind": kind,
        "as_of": as_of,
        "value": value,
        "unit": "USD",
        "scale": 1,
        "source_accession": _ACCESSION,
        "source_table_id": "xbrl:companyfacts-statement",
        "source_cell_ref": concept,
    }


def _dump_of(store, company: str, points: list[dict]) -> dict:
    for point in points:
        store.append(point)
    return store.dump_company(company)


def _series_ids(payload: dict) -> list[str]:
    return [entry["kpi_id"] for entry in payload["series"]]


def _series(payload: dict, kpi_id: str) -> dict:
    matches = [e for e in payload["series"] if e["kpi_id"] == kpi_id]
    assert len(matches) == 1, f"expected exactly one {kpi_id!r} series, got {matches}"
    return matches[0]


def _values_by_end(entry: dict) -> dict[str, object]:
    return {
        period["period_end"]: period["latest"]["canonical_value"]
        for period in entry["periods"]
    }


def test_resolves_a_different_concept_per_period(store, spine_view):
    """A filer that switched revenue tags mid-history yields ONE continuous
    `revenue` series spanning both eras.

    This is the reason the store holds as-reported concepts instead of
    pre-resolved canonical values: resolution is per PERIOD, not per company.
    A per-company winner (the shipped top-line lane's `break`-on-first-hit)
    would keep only the pre-switch years and silently truncate the history.
    """
    company = "SWITCHER"
    dump = _dump_of(
        store,
        company,
        [
            _point(company, "us-gaap:Revenues", "FY2016", "2016-01-01", "2016-12-31", 85320000000, "2017-02-01"),
            _point(company, "us-gaap:Revenues", "FY2017", "2017-01-01", "2017-12-31", 89950000000, "2018-02-01"),
            _point(
                company,
                "us-gaap:RevenueFromContractWithCustomerExcludingAssessedTax",
                "FY2018", "2018-01-01", "2018-12-31", 110360000000, "2019-02-01",
            ),
            _point(
                company,
                "us-gaap:RevenueFromContractWithCustomerExcludingAssessedTax",
                "FY2019", "2019-01-01", "2019-12-31", 125843000000, "2020-02-01",
            ),
        ],
    )

    derived = spine_view.derive_spine(dump)

    revenue = _series(derived, "revenue")
    assert _values_by_end(revenue) == {
        "2016-12-31": 85320000000,
        "2017-12-31": 89950000000,
        "2018-12-31": 110360000000,
        "2019-12-31": 125843000000,
    }
    # Provenance survives: each period still names the concept it came from,
    # so a reader can tell WHICH tag carried the field in that period.
    concepts = [p["latest"]["kpi_id"] for p in revenue["periods"]]
    assert concepts == [
        "us-gaap:Revenues",
        "us-gaap:Revenues",
        "us-gaap:RevenueFromContractWithCustomerExcludingAssessedTax",
        "us-gaap:RevenueFromContractWithCustomerExcludingAssessedTax",
    ]
    assert derived["company"] == company


def test_a_field_no_concept_ever_tagged_yields_no_row(store, spine_view):
    """Honest absence: a spine field whose chain concepts appear nowhere in
    the store produces NO series entry at all — never a 0, never a derived
    guess, never an empty placeholder row.

    Measured on the 46-filer probe: 22 filers report no gross profit and 13
    never tag a total `Liabilities`. A hole is the truth about the filing,
    not a defect in the view.
    """
    company = "NO-GROSS-PROFIT"
    dump = _dump_of(
        store,
        company,
        [
            _point(company, "us-gaap:Revenues", "FY2020", "2020-01-01", "2020-12-31", 12000, "2021-02-01"),
            _point(company, "us-gaap:Assets", "FY2020", None, "2020-12-31", 44000, "2021-02-01", kind="instant"),
        ],
    )

    derived = spine_view.derive_spine(dump)

    assert _series_ids(derived) == ["revenue", "total_assets"]
    assert "gross_profit" not in _series_ids(derived)
    assert derived["warnings"] == dump["warnings"]


def test_chain_order_resolves_a_same_period_overlap(store, spine_view):
    """When two chain concepts BOTH carry the same period, the chain's order
    is the tiebreak — first present wins, deterministically.

    Order is a same-period tiebreak only; it is never a per-company winner
    (the previous test proves the loser still supplies the periods the
    winner does not cover).
    """
    company = "OVERLAP"
    dump = _dump_of(
        store,
        company,
        [
            _point(company, "us-gaap:Revenues", "FY2021", "2021-01-01", "2021-12-31", 700, "2022-02-01"),
            _point(
                company,
                "us-gaap:RevenueFromContractWithCustomerExcludingAssessedTax",
                "FY2021", "2021-01-01", "2021-12-31", 690, "2022-02-01",
            ),
            _point(
                company,
                "us-gaap:RevenueFromContractWithCustomerExcludingAssessedTax",
                "FY2022", "2022-01-01", "2022-12-31", 810, "2023-02-01",
            ),
        ],
    )

    derived = spine_view.derive_spine(dump)

    revenue = _series(derived, "revenue")
    assert _values_by_end(revenue) == {"2021-12-31": 700, "2022-12-31": 810}
    assert revenue["periods"][0]["latest"]["kpi_id"] == "us-gaap:Revenues"


def test_null_axis_key_periods_are_never_merged_across_concepts(store, spine_view):
    """A `period_axis_key` of null means "not proven to be the same period",
    NOT "no period" — so two null-key entries from two concepts must never
    collapse into one resolved period.

    A 15-month transition FY is the real shape: the store refuses to size it
    to 1..4 quarters, so its axis key is null. Keying resolution on the raw
    null would silently drop one filer-reported figure.
    """
    company = "TRANSITION-FY"
    dump = _dump_of(
        store,
        company,
        [
            _point(company, "us-gaap:Revenues", "FY2014T", "2013-10-01", "2014-12-31", 51, "2015-02-01"),
            _point(
                company,
                "us-gaap:RevenueFromContractWithCustomerExcludingAssessedTax",
                "FY2014T", "2013-10-01", "2014-12-31", 52, "2015-02-01",
            ),
        ],
    )
    stored_keys = {
        period["period_axis_key"]
        for entry in dump["series"]
        for period in entry["periods"]
    }
    assert stored_keys == {None}, "fixture precondition: the store cannot size this span"

    derived = spine_view.derive_spine(dump)

    revenue = _series(derived, "revenue")
    assert len(revenue["periods"]) == 2
    assert sorted(p["latest"]["canonical_value"] for p in revenue["periods"]) == [51, 52]


def test_derived_payload_renders_through_the_tearsheet_formatter(store, spine_view):
    """The emitted payload is the SAME pinned schema the shipped formatter
    already consumes — so `kpi_store dump | kpi_spine_view derive |
    tearsheet_format` composes with tearsheet_format.py untouched.
    """
    company = "RENDERABLE"
    dump = _dump_of(
        store,
        company,
        [
            _point(company, "us-gaap:Revenues", "FY2016", "2016-01-01", "2016-12-31", 85320000000, "2017-02-01"),
            _point(
                company,
                "us-gaap:RevenueFromContractWithCustomerExcludingAssessedTax",
                "FY2018", "2018-01-01", "2018-12-31", 110360000000, "2019-02-01",
            ),
            _point(company, "us-gaap:NetIncomeLoss", "FY2018", "2018-01-01", "2018-12-31", 16571000000, "2019-02-01"),
        ],
    )
    formatter = _load("tearsheet_format_for_spine_view", TEARSHEET_FORMAT_SCRIPT)

    derived = spine_view.derive_spine(dump)
    derived["as_of"] = "2026-07-26"
    rendered = formatter.render_tearsheet(derived)

    assert "| revenue |" in rendered
    assert "| net_income |" in rendered
    assert "85,320,000,000 USD" in rendered
    assert "110,360,000,000 USD" in rendered
    assert "us-gaap:" not in rendered


def test_cli_derive_reads_a_dump_from_stdin_or_path(store, spine_view, tmp_path):
    """`kpi_spine_view.py derive --dump <path>` (stdin when omitted) — the
    pinned invocation shape, so the render pipeline is a plain pipe.
    """
    company = "CLI"
    dump = _dump_of(
        store,
        company,
        [_point(company, "us-gaap:Assets", "FY2020", None, "2020-12-31", 44000, "2021-02-01", kind="instant")],
    )
    expected = spine_view.derive_spine(dump)
    raw = json.dumps(dump)

    piped = subprocess.run(
        ["uv", "run", "--script", str(KPI_SPINE_VIEW_SCRIPT), "derive"],
        input=raw, capture_output=True, text=True, timeout=120,
        env={**os.environ, "PYTHONDONTWRITEBYTECODE": "1"},
    )
    assert piped.returncode == 0, piped.stderr
    assert json.loads(piped.stdout) == expected

    dump_path = tmp_path / "dump.json"
    dump_path.write_text(raw, encoding="utf-8")
    from_path = subprocess.run(
        ["uv", "run", "--script", str(KPI_SPINE_VIEW_SCRIPT), "derive", "--dump", str(dump_path)],
        capture_output=True, text=True, timeout=120,
        env={**os.environ, "PYTHONDONTWRITEBYTECODE": "1"},
    )
    assert from_path.returncode == 0, from_path.stderr
    assert json.loads(from_path.stdout) == expected
