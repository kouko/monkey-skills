"""test_sec_narrative.py — US SEC narrative extractor (edgartools migration).

Offline unit tests for the narrative acquisition / segmentation path.

edgartools (~100MB, pyarrow) is deliberately NOT installed in offline CI, so
`edgar` is injected as a `sys.modules` mock BEFORE importing sec_edgar_client —
the module's lazy `import edgar` then resolves to that stub. This is the
established pattern for every offline test in this file (later migration tasks
mock the real edgartools object shape captured by the @pytest.mark.network
live anchors in test_data_markets_live.py).

Run offline (exact CI command — no extra --with):
  uv run --quiet --with pytest --with 'pyyaml>=6.0' \
    pytest investing-toolkit/tests/ -m "not network" -q --tb=short

External-surface grounding: edgartools 5.42.0 —
  edgar.set_identity("<name> <email>") / env EDGAR_IDENTITY. The library does
  NOT fail-fast on an unset identity (get_identity() prompts interactively, then
  raises TimeoutError after ~60s), so this module's pre-send guard
  (_ensure_edgar_identity) is the load-bearing enforcer of SEC fair-access
  identity. Source: primary-source research (PyPI edgartools JSON + GitHub
  dgunning/edgartools source), captured 2026-07-12; see plan Notes
  §edgartools grounding in docs/loom/plans/2026-07-12-us-sec-narrative.md.

Task-2 acquisition grounding (D7): the acquire_filing mocks below mirror the
REAL edgartools 5.42.0 Filing shape captured by the live anchor
test_data_markets_live.py::test_edgartools_acquire_real_10k_shape —
  edgar.Company(id).get_filings(form=...).latest() / get_by_accession_number(acc);
  Filing.accession_no(str) / cik(int) / form(str) / filing_date(datetime.date,
  NOT str) / period_of_report(str) / filing_url / homepage_url. edgartools has
  NO `primary_document` attr (the plan's documented name was wrong) — the
  primary-doc filename is the last path segment of filing_url. Company.not_found
  (bool) + Company.cik are the verified resolution-failure signals. Captured
  live 2026-07-12 against AAPL FY2024 10-K, accession 0000320193-24-000123;
  sources PyPI edgartools JSON + GitHub dgunning/edgartools.
"""
from __future__ import annotations

import datetime
import importlib
import sys
from pathlib import Path
from types import SimpleNamespace
from unittest import mock

import pytest

ROOT = Path(__file__).resolve().parents[2]
MARKETS_SCRIPTS = ROOT / "skills" / "data-markets" / "scripts"


@pytest.fixture
def sec_client():
    """Import sec_edgar_client with `edgar` stubbed in sys.modules.

    Offline CI has no edgartools; the stub persists in sys.modules so the
    module's lazy `import edgar` resolves to it. The fixture restores the
    prior sys.modules state on teardown so tests stay isolated.
    """
    if str(MARKETS_SCRIPTS) not in sys.path:
        sys.path.insert(0, str(MARKETS_SCRIPTS))
    edgar_stub = mock.MagicMock(name="edgar")
    saved_edgar = sys.modules.get("edgar")
    saved_client = sys.modules.get("sec_edgar_client")
    sys.modules["edgar"] = edgar_stub
    sys.modules.pop("sec_edgar_client", None)
    module = importlib.import_module("sec_edgar_client")
    module.edgar_stub = edgar_stub
    try:
        yield module
    finally:
        if saved_edgar is not None:
            sys.modules["edgar"] = saved_edgar
        else:
            sys.modules.pop("edgar", None)
        if saved_client is not None:
            sys.modules["sec_edgar_client"] = saved_client
        else:
            sys.modules.pop("sec_edgar_client", None)


def test_acquire_rejects_when_identity_unset(sec_client, monkeypatch):
    # No @req tag: this dispatch's plan/spec traces by
    # `<change-id> / Requirement / Scenario` join keys, not registered REQ-ids,
    # so per the implementer contract @req is omitted (see report).
    # Scenario: `SEC EDGAR fair-access compliance / Missing User-Agent is
    # rejected before send`.
    monkeypatch.setattr(sec_client, "USER_AGENT", "")

    def _boom(*args, **kwargs):
        raise AssertionError(
            "network boundary (_sec_get) must NOT be hit when SEC identity is unset"
        )

    monkeypatch.setattr(sec_client, "_sec_get", _boom)

    result = sec_client.action_narrative("0001045810-24-000316")

    assert isinstance(result, dict)
    assert "error" in result, f"expected a loud error slot, got: {result!r}"


# ---------------------------------------------------------------------------
# Task 2 — acquire_filing (edgartools acquisition + two distinct error classes)
# ---------------------------------------------------------------------------
# Fixtures mirror the REAL edgartools 5.42.0 Filing shape captured by the live
# anchor test_data_markets_live.py::test_edgartools_acquire_real_10k_shape.


def _real_shape_filing() -> SimpleNamespace:
    """A SimpleNamespace mirroring the live-captured edgartools Filing shape.

    SimpleNamespace (not MagicMock) so an access to a non-existent attribute
    RAISES — exactly as the real Filing raised AttributeError for
    `primary_document` — keeping the fixture honest to the producer shape
    (fixtures-mirror-producer-shape). `filing_date` is a datetime.date, not a
    string, matching the live capture.
    """
    return SimpleNamespace(
        accession_no="0000320193-24-000123",
        cik=320193,
        form="10-K",
        filing_date=datetime.date(2024, 11, 1),  # a date object, NOT a string
        period_of_report="2024-09-28",
        filing_url=(
            "https://www.sec.gov/Archives/edgar/data/320193/"
            "000032019324000123/aapl-20240928.htm"
        ),
        homepage_url=(
            "https://www.sec.gov/Archives/edgar/data/320193/"
            "0000320193-24-000123-index.html"
        ),
    )


def _assert_success_ref(ref: dict) -> None:
    assert "error" not in ref, f"expected a filing ref, got error slot: {ref!r}"
    assert ref["accession"] == "0000320193-24-000123"
    assert ref["cik"] == 320193
    assert ref["form"] == "10-K"
    assert ref["filingDate"] == "2024-11-01"  # datetime.date serialized to ISO str
    assert ref["period_of_report"] == "2024-09-28"
    assert ref["primaryDocument"] == "aapl-20240928.htm"
    url = ref["url"]
    assert url.startswith("https://www.sec.gov/Archives/edgar/data/320193/")
    assert "000032019324000123" in url  # accession-no-dashes segment
    assert url.endswith("aapl-20240928.htm")  # reconstructable, no extra lookup


@pytest.mark.parametrize("case", ["success", "not_found", "form_unavailable"])
def test_acquire_filing(sec_client, case):
    # No @req tag: this dispatch's plan/spec trace by
    # `<change-id> / Requirement / Scenario` join keys, not registered REQ-ids
    # (see report) — @req omitted per the implementer contract.
    # Scenarios: `Filing Acquisition via edgartools / {Successful filing
    # acquisition | Ticker or CIK not found | Requested form type not available}`.
    stub = sec_client.edgar_stub
    company = mock.MagicMock(name="Company")
    company.not_found = False
    company.cik = 320193
    stub.Company.return_value = company

    if case == "success":
        company.get_filings.return_value.latest.return_value = _real_shape_filing()
        ref = sec_client.acquire_filing("AAPL", form="10-K")
        _assert_success_ref(ref)
    elif case == "not_found":
        company.not_found = True  # verified edgartools resolution-failure signal
        company.cik = None
        ref = sec_client.acquire_filing("ZZZZINVALID", form="10-K")
        assert "error" in ref, f"unresolved identifier must be a loud slot: {ref!r}"
        assert ref["error_class"] == "resolution"
        assert "ZZZZINVALID" in ref["error"], (
            "resolution error must name the unresolved identifier"
        )
    else:  # form_unavailable
        # resolved filer, but the requested form yields an empty Filings whose
        # .latest() is None (verified live) — NOT a resolution error.
        company.get_filings.return_value.latest.return_value = None
        ref = sec_client.acquire_filing("AAPL", form="8-K")
        assert "error" in ref, f"missing form must be a loud slot: {ref!r}"
        assert ref["error_class"] == "form_unavailable"
        assert ref["error_class"] != "resolution", (
            "form-unavailable must be DISTINCT from the resolution-error class"
        )
        assert "8-K" in ref["error"], (
            "form-unavailable error must name the requested form"
        )


@pytest.mark.parametrize("found", [True, False])
def test_acquire_filing_by_accession(sec_client, found):
    # No @req tag (see test_acquire_filing).
    # Scenario: `Filing Acquisition via edgartools / Successful filing
    # acquisition` (accession mode); the not-found leg exercises the same
    # loud resolution slot for an accession that does not resolve to a filing.
    stub = sec_client.edgar_stub
    if found:
        stub.get_by_accession_number.return_value = _real_shape_filing()
        ref = sec_client.acquire_filing(accession="0000320193-24-000123")
        _assert_success_ref(ref)
    else:
        stub.get_by_accession_number.return_value = None
        ref = sec_client.acquire_filing(accession="9999999999-99-999999")
        assert "error" in ref
        assert ref["error_class"] == "resolution"
        assert "9999999999-99-999999" in ref["error"]
