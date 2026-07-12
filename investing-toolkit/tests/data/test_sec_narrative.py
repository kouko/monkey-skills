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

Task-3 segmentation grounding (D7): the TenK/TenQ mocks below mirror the REAL
edgartools 5.42.0 typed section-API shape captured by the live anchor
test_data_markets_live.py::test_edgartools_segment_real_10k_shape —
  filing.obj() -> TenK / TenQ. TenK exposes `management_discussion` (Item 7,
  MD&A) and `risk_factors` (Item 1A) as `str` properties; an item absent from
  THIS filing yields `None` (edgartools issue #710). TenQ has NO
  `management_discussion` property — Item 2 (MD&A) is read via the subscript
  `obj["Part I, Item 2"]` -> `str` (also `None` when absent). Both typed objects
  also expose `obj.items` (list of item ids). Captured live 2026-07-12 against
  AAPL FY2024 10-K (0000320193-24-000123) + AAPL latest 10-Q; sources PyPI
  edgartools JSON + GitHub dgunning/edgartools.

Task-4 8-K grounding (D7): the _MockEightK / _MockPressRelease mocks below
mirror the REAL edgartools 5.42.0 8-K shape captured LIVE 2026-07-12 against
AAPL's earnings 8-K accession 0000320193-26-000011 (Item 2.02 + Exhibit 99.1),
anchored by test_data_markets_live.py::test_edgartools_segment_real_8k_shape.
Two plan-grounding corrections found live (documented so a re-reader trusts the
mock over the plan):
  - filing.obj() on an 8-K returns type ``CurrentReport``, NOT ``EightK`` (the
    plan's documented type name was wrong).
  - the press-release exhibits, ``obj.press_releases`` -> a ``PressReleases``
    collection of ``PressRelease`` objects, each exposing ``.document`` (the
    EX-99.x filename, e.g. ``a8-kex991q2202603282026.htm``) + ``.text()`` (a
    METHOD returning the exhibit body) — but NO ``.document_type`` attr (that
    attr lives only on ``filing.attachments``' ``Attachment`` objects, a
    distinct surface). So the exhibit-following path reads ``obj.press_releases``
    (already narrowed to EX-99.x press releases by edgartools) and needs no
    ``document_type`` filtering. ``obj.items`` is a list of item-id strings
    (``['Item 2.02', 'Item 9.01']``). Sources: live edgartools 5.42.0 + PyPI
    edgartools JSON + GitHub dgunning/edgartools, captured 2026-07-12.

Section-object contract established by Task 3 (reused by Tasks 4-12):
`segment_filing(filing)` returns a LIST of per-item section dicts, in requested
order. A SUCCESS section is a plain dict `{"item": <item id>, "text": <text>}`
that later tasks EXTEND in place (T6 provenance, T7 `text_path`, T9
`disclosure_status`). A FAILURE slot is a sentinel-compatible dict
`{"item": <item id>, "error": <why>, "error_class": "absent_item"}` — it names
the missing item, never an empty/fabricated section, and its top-level `error`
key is read unchanged by pack.py's `_status`.
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
    """Import sec_edgar_client with `edgar` AND `requests` stubbed in sys.modules.

    Offline CI installs ONLY pytest + pyyaml, so neither edgartools nor requests
    is importable there. Both are stubbed BEFORE the import:
      - `edgar`: the module's lazy `import edgar` resolves to the stub.
      - `requests`: sec_edgar_client's top-level `import requests` serves the
        LEGACY XBRL/`_sec_get` HTTP path only, which these narrative tests never
        exercise (they mock the edgartools boundary and, where `_sec_get` is
        relevant, monkeypatch it directly). Stubbing it keeps these offline unit
        tests free of a real HTTP client — without a stub the whole module fails
        to import and every test errors at setup ("works on my machine" gap).
    The fixture restores the prior sys.modules state on teardown so tests stay
    isolated.
    """
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
    module.edgar_stub = edgar_stub
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


@pytest.fixture(autouse=True)
def _isolated_cache(tmp_path, monkeypatch):
    """Pin the toolkit cache dir at a pytest tmp_path so the section-text files
    Task 7 writes at RUNTIME (`text_path`) stay isolated and never pollute the
    real cache or the repo tree (F.I.R.S.T). Exercises the real
    cache_util.resolve_cache_dir precedence (INVESTING_TOOLKIT_CACHE wins)."""
    monkeypatch.setenv("INVESTING_TOOLKIT_CACHE", str(tmp_path))
    yield


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
# Task 1 (this plan, 2026-07-13-us-sec-narrative-memo-wiring) — list_filings
# preserves the submissions API's `items` and `reportDate` fields.
# ---------------------------------------------------------------------------
# Live-verified 2026-07-13 against CIK 0000320193: `data.sec.gov` submissions
# `filings.recent` is a dict of parallel, index-aligned arrays that already
# includes `items` (comma-joined 8-K item codes, e.g. "2.02,9.01") and
# `reportDate` (period of report); a 10-K row's `items` is an empty string,
# not a missing entry. Stubs fetch_submissions directly (the real producer
# boundary list_filings calls), per fixtures-mirror-producer-shape.


def test_list_filings_preserves_items_and_report_date(sec_client, monkeypatch):
    # No @req tag: this dispatch's plan/spec trace by
    # `<change-id> / Requirement / Scenario` join keys, not registered REQ-ids
    # (see report) — @req omitted per the implementer contract.
    stub_submissions = {
        "data": {
            "filings": {
                "recent": {
                    "form": ["10-K", "8-K", "8-K"],
                    "filingDate": ["2024-11-01", "2024-05-01", "2024-02-01"],
                    "accessionNumber": [
                        "0000320193-24-000123",
                        "0000320193-24-000099",
                        "0000320193-24-000050",
                    ],
                    "primaryDocument": [
                        "aapl-20240928.htm",
                        "a8-k-may.htm",
                        "a8-k-feb.htm",
                    ],
                    "primaryDocDescription": ["10-K", "8-K", "8-K"],
                    # 3rd row's items/reportDate entries are MISSING (short
                    # arrays) — exercises the index-guard idiom below.
                    "items": ["", "2.02,9.01"],
                    "reportDate": ["2024-09-28", "2024-03-30"],
                }
            }
        }
    }
    monkeypatch.setattr(sec_client, "fetch_submissions", lambda cik: stub_submissions)

    rows = sec_client.list_filings(320193, None, limit=10)

    by_accn = {r["accessionNumber"]: r for r in rows}
    tenk = by_accn["0000320193-24-000123"]
    eightk_recent = by_accn["0000320193-24-000099"]
    eightk_short = by_accn["0000320193-24-000050"]

    # 10-K: items is the API's own empty-string representation, NOT None/missing.
    assert tenk["items"] == ""
    assert tenk["reportDate"] == "2024-09-28"

    # 8-K carries the comma-joined item codes verbatim, un-parsed/un-interpreted.
    assert eightk_recent["items"] == "2.02,9.01"
    assert eightk_recent["reportDate"] == "2024-03-30"

    # index-guard: a row past the end of the items/reportDate arrays mirrors the
    # existing `i < len(...)` idiom used for the other parallel arrays -> None.
    assert eightk_short["items"] is None
    assert eightk_short["reportDate"] is None


# ---------------------------------------------------------------------------
# Task 2 (this plan, 2026-07-13-us-sec-narrative-memo-wiring) —
# select_narrative_filings: a pure, offline-testable quarter-anchored
# filing-selection policy over already-fetched `list_filings` rows.
# ---------------------------------------------------------------------------
# Live-verified 2026-07-13 against AAPL: the MOST RECENT 8-K at probe time was
# items="5.02" (an executive-change filing), while the actual earnings release
# was an OLDER 8-K in the same quarter, items="2.02,9.01". "Take the latest
# 8-K" silently selects the wrong filing — selection must be by item code
# (exact membership in the comma-separated `items`, never substring), and the
# window must be anchored in TIME (quarters), never filing count.


def _filing_row(
    *, form, accession, filing_date, report_date="", items="", primary_document=""
):
    """A row shaped exactly like `list_filings`'s output (Task 1, landed)."""
    return {
        "form": form,
        "filingDate": filing_date,
        "accessionNumber": accession,
        "primaryDocument": primary_document,
        "primaryDocDescription": form,
        "items": items,
        "reportDate": report_date,
    }


def test_select_narrative_filings_picks_earnings_8k_by_item_not_recency(sec_client):
    # No @req tag: this dispatch's plan/spec trace by
    # `<change-id> / Requirement / Scenario` join keys, not registered REQ-ids
    # (see report) — @req omitted per the implementer contract.
    import datetime as _dt

    rows = [
        _filing_row(
            form="10-K", accession="10K-OLD", filing_date="2024-11-01",
            report_date="2024-09-28",
        ),
        _filing_row(
            form="10-K", accession="10K-LATEST", filing_date="2025-11-01",
            report_date="2025-09-27",
        ),
        _filing_row(
            form="10-Q", accession="10Q-OLD", filing_date="2025-08-01",
            report_date="2025-06-28",
        ),
        _filing_row(
            form="10-Q", accession="10Q-LATEST", filing_date="2026-05-01",
            report_date="2026-03-28",
        ),
        # 2026Q2: the MOST RECENT 8-K is a 5.02 executive-change filing; an
        # OLDER 8-K in the SAME quarter is the real 2.02 earnings release.
        _filing_row(
            form="8-K", accession="8K-EXEC-CHANGE", filing_date="2026-05-05",
            report_date="2026-05-01", items="5.02",
        ),
        _filing_row(
            form="8-K", accession="8K-EARNINGS-Q2", filing_date="2026-04-30",
            report_date="2026-04-30", items="2.02,9.01",
        ),
        # 2026Q1: a normal earnings 8-K.
        _filing_row(
            form="8-K", accession="8K-EARNINGS-Q1", filing_date="2026-02-01",
            report_date="2026-01-31", items="2.02,9.01",
        ),
        # 2025Q4: an 8-K exists, but NONE carries item 2.02 -> must be a gap.
        _filing_row(
            form="8-K", accession="8K-Q4-OTHER", filing_date="2025-11-15",
            report_date="2025-11-01", items="5.07",
        ),
        # 2026Q3 (the anchor quarter itself): no 8-K at all -> must be a gap.
    ]
    as_of = _dt.date(2026, 7, 15)  # anchors the window at 2026Q3

    result = sec_client.select_narrative_filings(rows, n_quarters=4, as_of=as_of)

    selected_by_role_quarter = {
        (r["role"], r.get("quarter")): r for r in result["selected"]
    }

    tenk = selected_by_role_quarter[("10-K", None)]
    assert tenk["accessionNumber"] == "10K-LATEST", "must pick the LATEST 10-K"

    tenq = selected_by_role_quarter[("10-Q", None)]
    assert tenq["accessionNumber"] == "10Q-LATEST", "must pick the LATEST 10-Q"

    q2 = selected_by_role_quarter[("8-K", "2026Q2")]
    assert q2["accessionNumber"] == "8K-EARNINGS-Q2", (
        "must select the item-2.02 filing, NOT the more-recent 5.02 filing "
        "in the same quarter (selection is by item code, never recency)"
    )
    assert "8K-EXEC-CHANGE" not in {r["accessionNumber"] for r in result["selected"]}

    q1 = selected_by_role_quarter[("8-K", "2026Q1")]
    assert q1["accessionNumber"] == "8K-EARNINGS-Q1"

    # 2025Q4 has an 8-K, but none with item 2.02 -> explicit gap, not silence.
    gaps_by_quarter = {g.get("quarter"): g for g in result["gaps"]}
    assert "2025Q4" in gaps_by_quarter, (
        f"expected an explicit gap for 2025Q4, got gaps: {result['gaps']!r}"
    )
    gap_q4 = gaps_by_quarter["2025Q4"]
    assert "error" in gap_q4, f"gap must be a loud error slot: {gap_q4!r}"
    assert "2025Q4" in gap_q4["error"], "gap error must name the quarter"

    # 2026Q3 (the anchor quarter) has no 8-K at all -> also an explicit gap.
    assert "2026Q3" in gaps_by_quarter

    # requested is FIXED by the policy (2 + n_quarters), independent of what
    # actually matched — this is what makes an incomplete result arithmetically
    # detectable downstream rather than a short list that looks complete.
    assert result["requested"] == 2 + 4 == 6


def test_select_narrative_filings_requested_is_policy_fixed(sec_client):
    # No @req tag (see test_select_narrative_filings_picks_earnings_8k_by_item_not_recency).
    # `requested` must equal `2 + n_quarters` regardless of how many filings
    # actually matched — even an EMPTY filings list still reports the full
    # policy-fixed count, with every slot showing up as a gap.
    result = sec_client.select_narrative_filings([], n_quarters=4)
    assert result["requested"] == 6
    assert len(result["selected"]) + len(result["gaps"]) == 6

    result3 = sec_client.select_narrative_filings([], n_quarters=3)
    assert result3["requested"] == 5


def test_select_narrative_filings_item_code_is_exact_not_substring(sec_client):
    # No @req tag (see test_select_narrative_filings_picks_earnings_8k_by_item_not_recency).
    # A hypothetical "12.02" must NOT be treated as an earnings 8-K: membership
    # of "2.02" must be a proper set-membership check over the comma-split
    # `items` field, never a substring search.
    import datetime as _dt

    rows = [
        _filing_row(
            form="8-K", accession="8K-DECOY", filing_date="2026-05-05",
            report_date="2026-05-01", items="12.02",
        ),
    ]
    as_of = _dt.date(2026, 5, 15)  # anchors the window at 2026Q2

    result = sec_client.select_narrative_filings(rows, n_quarters=1, as_of=as_of)

    assert not any(
        r["role"] == "8-K" and r["accessionNumber"] == "8K-DECOY"
        for r in result["selected"]
    ), "items='12.02' must NOT match item code '2.02' via substring"
    gaps_by_quarter = {g.get("quarter"): g for g in result["gaps"]}
    assert "2026Q2" in gaps_by_quarter, (
        "the decoy-only quarter must still surface as an explicit gap"
    )


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


# ---------------------------------------------------------------------------
# Task 3 — segment 10-K (Item 7 + Item 1A) / 10-Q (Item 2) via the edgartools
# typed section API; a requested-but-absent item → a loud named error slot.
# ---------------------------------------------------------------------------
# TenK/TenQ mocks mirror the REAL edgartools 5.42.0 section-API shape captured
# by test_data_markets_live.py::test_edgartools_segment_real_10k_shape (see the
# Task-3 segmentation grounding in this module's docstring).


class _MockTenK:
    """Mirror edgartools 5.42.0 ``TenK`` typed object (``filing.obj()``) — the
    ALL-ITEM surface ``_segment_10k`` enumerates post-pivot.

    Live probe 2026-07-12: ``obj.items`` is the full ordered item-id list (an
    AAPL 10-K enumerates all 23 items — Item 1, 1A, 1B, 1C, 2..16 incl 7A/9A/
    9B/9C) and ``obj[item_id]`` returns that item's text as ``str`` (or ``None``
    when the item is absent from THIS filing — issue #710). Plain ``items`` /
    ``__getitem__`` (no MagicMock) so a subscript on a NON-enumerated key reads
    as absent (``None``) exactly as the live capture, and a renamed producer
    surface RAISES rather than silently passing (fixtures-mirror-producer-shape;
    the version-drift guard on a non-``str`` return value is Task 10, below).

    Two construction modes — both a faithful subset of the SAME producer surface:
      - ``item_texts={id: text-or-None, ...}``: an explicit ordered item set
        (the all-item shape); ``obj.items`` enumerates EVERY id, including one
        whose text is ``None`` (enumerated-but-absent — issue #710).
      - ``management_discussion=`` / ``risk_factors=``: the legacy 2-item
        (Item 7 + Item 1A) convenience the pre-pivot tests use — sugar for
        ``item_texts={"Item 7": md, "Item 1A": rf}``.
    """

    def __init__(self, *, management_discussion=None, risk_factors=None, item_texts=None):
        if item_texts is None:
            item_texts = {"Item 7": management_discussion, "Item 1A": risk_factors}
        self._item_texts = dict(item_texts)
        self.items = list(self._item_texts)

    def __getitem__(self, key):
        return self._item_texts.get(key)


class _MockTenQ:
    """Mirror edgartools 5.42.0 ``TenQ`` typed object (``filing.obj()``) — the
    ALL-ITEM surface ``_segment_10q`` enumerates post-pivot.

    Like ``TenK``, ``obj.items`` is the full ordered item-id list and each item's
    text is read via the ``obj[item_id]`` subscript -> ``str`` (or ``None`` when
    absent). Mirrors the subscript-returns-None-on-absent shape; a real ``TenQ``
    subscript on a missing key returned ``None``, not ``KeyError``. The MD&A item
    id is ``"Part I, Item 2"`` (the grounded subscript key), now enumerated on
    ``obj.items`` alongside the filing's other items.
    """

    def __init__(self, sections):
        self._sections = dict(sections)
        self.items = list(self._sections)

    def __getitem__(self, key):
        return self._sections.get(key)


def _segmentable_filing(form: str, typed_obj) -> SimpleNamespace:
    """A mock edgartools ``Filing`` whose ``.obj()`` returns a typed TenK/TenQ
    mock, carrying the T2 provenance attrs ``segment_filing`` reads for its
    error slots. SimpleNamespace so a missing attr RAISES
    (fixtures-mirror-producer-shape)."""
    return SimpleNamespace(
        accession_no="0000320193-24-000123",
        cik=320193,
        form=form,
        filing_date=datetime.date(2024, 11, 1),
        period_of_report="2024-09-28",
        filing_url=(
            "https://www.sec.gov/Archives/edgar/data/320193/"
            "000032019324000123/aapl-20240928.htm"
        ),
        homepage_url=(
            "https://www.sec.gov/Archives/edgar/data/320193/"
            "0000320193-24-000123-index.html"
        ),
        obj=lambda: typed_obj,
    )


def _read_text_path(section) -> str:
    """Read a SUCCESS section's file-backed body, asserting the text is NOT
    inlined (Task 7 contract: a section carries a `text_path` to a file, never
    an inline `text` key). Used by every SUCCESS-section text assertion below."""
    assert "text" not in section, f"section text must NOT be inlined: {section!r}"
    assert "text_path" in section, f"success section must carry text_path: {section!r}"
    return Path(section["text_path"]).read_text(encoding="utf-8")


def test_segment_10k_emits_all_items(sec_client):
    # No @req tag: this dispatch's plan/spec trace by
    # `<change-id> / Requirement / Scenario` join keys, not registered REQ-ids
    # (see report) — @req omitted per the implementer contract.
    # Scenario: `Full-Body Item Segmentation (10-K/10-Q) / 10-K all-item
    # segmentation` + `Enumerated item absent or empty in this filing`.
    # D7 grounding (live probe 2026-07-12): ``obj.items`` on a TenK is the full
    # ordered item-id list (AAPL 10-K = 23 items) and ``obj[item_id]`` -> str-or
    # -None (issue #710) — anchored live by
    # test_data_markets_live.py::test_edgartools_segment_real_10k_shape. Post-pivot
    # the data layer emits a section for EVERY enumerated item (pure acquisition,
    # no curated Item-7/1A filter); an enumerated item whose subscript is None is a
    # loud named gap, never dropped or fabricated.
    tenk = _MockTenK(
        item_texts={
            "Item 1": "Item 1.\xa0\xa0Business body ...",
            "Item 1A": "Item 1A.\xa0\xa0Risk Factors body ...",
            "Item 1B": None,  # enumerated but absent in THIS filing (issue #710)
            "Item 7": "Item 7.\xa0\xa0Management's Discussion body ...",
            "Item 8": "Item 8.\xa0\xa0Financial Statements body ...",
        }
    )
    filing = _segmentable_filing("10-K", tenk)

    sections = sec_client.segment_filing(filing)

    assert isinstance(sections, list)
    by_item = {s["item"]: s for s in sections}
    # EVERY enumerated item is emitted — incl. Item 1 Business + Item 8 Financial
    # Statements, not just the retired Item 7 + Item 1A curated subset.
    assert set(by_item) == {"Item 1", "Item 1A", "Item 1B", "Item 7", "Item 8"}, (
        "10-K must emit a section for EVERY item obj.items enumerates, not a "
        "hand-picked subset"
    )
    # present items are distinct success sections with file-backed text (Task 7)
    for item_id in ("Item 1", "Item 1A", "Item 7", "Item 8"):
        assert "error" not in by_item[item_id], f"{item_id} must be a success section"
    assert _read_text_path(by_item["Item 1"]) == "Item 1.\xa0\xa0Business body ..."
    assert _read_text_path(by_item["Item 1A"]) == "Item 1A.\xa0\xa0Risk Factors body ..."
    assert _read_text_path(by_item["Item 7"]) == "Item 7.\xa0\xa0Management's Discussion body ..."
    assert _read_text_path(by_item["Item 8"]) == "Item 8.\xa0\xa0Financial Statements body ..."
    # the enumerated-but-absent item is a loud, named gap — never empty/fabricated
    gap = by_item["Item 1B"]
    assert "error" in gap, f"absent enumerated item must be a loud slot: {gap!r}"
    assert gap["error_class"] == "absent_item"
    assert "Item 1B" in gap["error"], "gap must name the absent item"
    assert not gap.get("text"), "no fabricated text for an absent item"


def test_segment_10q_emits_all_items(sec_client):
    # No @req tag (see test_segment_10k_emits_all_items).
    # Scenario: `Full-Body Item Segmentation (10-K/10-Q) / 10-Q all-item
    # segmentation`. Same all-item contract as the 10-K: EVERY item obj.items
    # enumerates is its own section (the MD&A id "Part I, Item 2" among them),
    # never a curated subset.
    tenq = _MockTenQ(
        {
            "Part I, Item 1": "Item 1.\xa0\xa0Financial Statements body ...",
            "Part I, Item 2": "Item 2.\xa0\xa010-Q MD&A body ...",
            "Part II, Item 1A": "Item 1A.\xa0\xa0Risk Factors update ...",
        }
    )
    filing = _segmentable_filing("10-Q", tenq)

    sections = sec_client.segment_filing(filing)

    by_item = {s["item"]: s for s in sections}
    assert set(by_item) == {"Part I, Item 1", "Part I, Item 2", "Part II, Item 1A"}, (
        "10-Q must emit a section for EVERY item obj.items enumerates"
    )
    for item_id in ("Part I, Item 1", "Part I, Item 2", "Part II, Item 1A"):
        assert "error" not in by_item[item_id], f"{item_id} must be a success section"
    # text is file-backed (Task 7): read it back, assert the SAME content.
    assert _read_text_path(by_item["Part I, Item 2"]) == "Item 2.\xa0\xa010-Q MD&A body ..."


def test_segment_absent_item_emits_error_slot(sec_client):
    # No @req tag (see test_segment_10k_item7_and_item1a).
    # Scenario: `10-K/10-Q Item Segmentation / Requested item absent from this
    # filing`. Item 1A omitted under a permitted exception → risk_factors is
    # None (edgartools issue #710).
    tenk = _MockTenK(
        management_discussion="Item 7.\xa0\xa0Management's Discussion body ...",
        risk_factors=None,
    )
    filing = _segmentable_filing("10-K", tenk)

    sections = sec_client.segment_filing(filing)

    by_item = {s["item"]: s for s in sections}
    # the present item is still emitted normally (text is file-backed, Task 7)
    assert "error" not in by_item["Item 7"]
    assert _read_text_path(by_item["Item 7"])
    # the absent item is a loud, named error slot — never empty/fabricated
    slot = by_item["Item 1A"]
    assert "error" in slot, f"absent item must be a loud slot: {slot!r}"
    assert "Item 1A" in slot["error"], "error slot must name the missing item"
    assert slot["error_class"] == "absent_item"
    assert not slot.get("text"), "no fabricated text for an absent item"


def test_segment_unsupported_form_fails_loud(sec_client):
    # No @req tag: a DEFENSIVE case beyond the three named 10-K/10-Q/absent
    # scenarios (contract rule 11 — omit @req, note it). Documents that only
    # 10-K/10-Q are on this migration slice's segmentation path (8-K follows in
    # a later task via a new registry entry); a form with no registered
    # extractor must fail loud, not silently return an empty section list.
    filing = _segmentable_filing(
        "S-1", _MockTenK(management_discussion="x", risk_factors="y")
    )
    with pytest.raises(ValueError):
        sec_client.segment_filing(filing)


# ---------------------------------------------------------------------------
# Task 4 — segment an 8-K by reported item code (2.02 / 7.01 / 8.01), sourcing
# each item's narrative text from its Exhibit 99.x attachment (the 8-K body
# carries only the announcement; the substance lives in the exhibit), and
# recording the source exhibit filename in the section provenance.
# ---------------------------------------------------------------------------
# _MockEightK / _MockPressRelease mirror the REAL edgartools 5.42.0 8-K shape
# captured by test_data_markets_live.py::test_edgartools_segment_real_8k_shape
# (see the Task-4 8-K grounding in this module's docstring). Plain-attribute
# classes so a renamed producer attr RAISES rather than silently reading as
# absent (fixtures-mirror-producer-shape). Post-pivot _MockEightK DOES expose
# __getitem__ (the body subscript): every reported item is emitted, and a
# non-exhibit-bearing item is sourced from its own body text. An exhibit-bearing
# item's section text still comes from the EXHIBIT, not the body — the RED
# assertion below (section text == exhibit) is what proves that.


class _MockPressRelease:
    """Mirror an edgartools 5.42.0 ``PressRelease`` (an EX-99.x press-release
    exhibit yielded by ``CurrentReport.press_releases``).

    Live capture confirmed ``.document`` (the EX-99.x filename) is an attribute
    and ``.text()`` is a METHOD returning the exhibit body; a ``PressRelease``
    has NO ``.document_type`` (that attr is on ``filing.attachments``'
    ``Attachment`` objects, a distinct surface)."""

    def __init__(self, *, document, text):
        self.document = document
        self._text = text

    def text(self):
        return self._text


class _MockEightK:
    """Mirror an edgartools 5.42.0 8-K typed object (``filing.obj()``; the real
    runtime type is ``CurrentReport``, not ``EightK`` — plan-grounding
    correction).

    ``items`` is a list of reported item-id strings (e.g.
    ``['Item 2.02', 'Item 9.01']``); ``press_releases`` is the collection of
    EX-99.x press-release exhibits.

    Post-pivot the data layer emits a section for EVERY reported item, so a
    non-exhibit-bearing item (e.g. Item 9.01) is read from its OWN body text via
    the ``obj[item_id]`` subscript — the SAME surface the real ``CurrentReport``
    exposes (a live probe 2026-07-12 showed AAPL's 8-K reporting
    ``['Item 2.02', 'Item 9.01']`` with each item's body reachable by subscript).
    ``body_texts={item_id: str-or-None}`` supplies those bodies; a subscript on a
    key absent from the map reads as ``None`` (the enumerated-but-absent gap),
    mirroring the producer. An exhibit-bearing item's body MAY be seeded too — the
    RED assertion that its section text equals the EXHIBIT (not the body) is what
    proves the exhibit-following path never sources from the 8-K body announcement
    (fixtures-mirror-producer-shape: the real object DOES expose the body; the code
    simply doesn't read it for exhibit-bearing items)."""

    def __init__(self, *, items, press_releases, body_texts=None):
        self.items = list(items)
        self.press_releases = list(press_releases)
        self._body_texts = dict(body_texts or {})

    def __getitem__(self, key):
        return self._body_texts.get(key)


def test_segment_8k_item_2_02_from_ex99_1(sec_client):
    # No @req tag: this dispatch's plan/spec trace by
    # `<change-id> / Requirement / Scenario` join keys, not registered REQ-ids
    # (see report) — @req omitted per the implementer contract.
    # Scenario: `8-K Item Segmentation with Exhibit-Following / 8-K Item 2.02
    # with Exhibit 99.1 present`.
    exhibit_text = (
        "Exhibit 99.1\nApple reports second quarter results\n"
        "March quarter records for total company revenue ..."
    )
    eightk = _MockEightK(
        items=["Item 2.02", "Item 9.01"],  # 9.01 = the exhibit-list item, own body text
        press_releases=[
            _MockPressRelease(document="a8-kex991q2202603282026.htm", text=exhibit_text),
        ],
        body_texts={"Item 9.01": "Item 9.01.\xa0\xa0Financial Statements and Exhibits"},
    )
    filing = _segmentable_filing("8-K", eightk)

    sections = sec_client.segment_filing(filing)

    by_item = {s["item"]: s for s in sections}
    # post-pivot every reported item is emitted; this test focuses on the
    # exhibit-bearing 2.02 → EX-99.1 following (Item 9.01's body leg is covered by
    # test_segment_8k_emits_all_reported_items).
    assert "Item 2.02" in by_item, "the reported exhibit-following item is emitted"
    slot = by_item["Item 2.02"]
    assert "error" not in slot, f"exhibit-present item must be a success section: {slot!r}"
    # text is sourced from the EX-99.1 exhibit, NOT the 8-K body announcement;
    # file-backed via text_path (Task 7), read back to assert the SAME content.
    section_text = _read_text_path(slot)
    assert section_text == exhibit_text
    assert "second quarter results" in section_text
    # the source exhibit filename is recorded in provenance
    assert slot["exhibit"] == "a8-kex991q2202603282026.htm"


@pytest.mark.parametrize("item_code", ["Item 7.01", "Item 8.01"])
def test_segment_8k_item_7_01_8_01_from_ex99_x(sec_client, item_code):
    # No @req tag (see test_segment_8k_item_2_02_from_ex99_1).
    # Scenario: `8-K Item Segmentation with Exhibit-Following / 8-K Item
    # 7.01/8.01 with Exhibit 99.x present`.
    exhibit_text = f"Exhibit 99.1\nMaterial disclosure body for {item_code} ..."
    eightk = _MockEightK(
        items=[item_code, "Item 9.01"],
        press_releases=[_MockPressRelease(document="ex99-1.htm", text=exhibit_text)],
        body_texts={"Item 9.01": "Item 9.01.\xa0\xa0Financial Statements and Exhibits"},
    )
    filing = _segmentable_filing("8-K", eightk)

    sections = sec_client.segment_filing(filing)

    by_item = {s["item"]: s for s in sections}
    assert set(by_item) == {item_code, "Item 9.01"}, (
        "post-pivot the 8-K emits a section for EVERY reported item — the "
        "exhibit-bearing item AND Item 9.01 (its own body text)"
    )
    slot = by_item[item_code]
    assert "error" not in slot
    # text sourced from the corresponding exhibit, not the 8-K body alone;
    # file-backed via text_path (Task 7), read back to assert the SAME content.
    section_text = _read_text_path(slot)
    assert section_text == exhibit_text
    assert item_code in section_text
    assert slot["exhibit"] == "ex99-1.htm"
    # Item 9.01 (non-exhibit) carries its own body text, filed (not furnished).
    nine = by_item["Item 9.01"]
    assert "error" not in nine, f"Item 9.01 must be a filed success section: {nine!r}"
    assert nine["disclosure_status"] == "filed"
    assert "exhibit" not in nine, "a body-sourced item carries no exhibit provenance"


def test_segment_8k_emits_all_reported_items(sec_client):
    # No @req tag: this dispatch's plan/spec trace by
    # `<change-id> / Requirement / Scenario` join keys, not registered REQ-ids
    # (see report) — @req omitted per the implementer contract.
    # Scenario: `8-K Full-Item Segmentation with Exhibit-Following / 8-K all
    # reported items, exhibit-bearing item sourced from Exhibit 99.1` +
    # `Furnished-vs-filed status propagates to the memo / Exhibit 99.x marked
    # furnished`.
    # D7 grounding (live probe 2026-07-12): a real AAPL 8-K reported
    # ``obj.items == ['Item 2.02', 'Item 9.01']`` — the exhibit-bearing item's
    # substance lives in ``obj.press_releases`` (EX-99.x) while every OTHER
    # reported item is read from ``obj[item_id]`` body text; anchored live by
    # test_data_markets_live.py::test_edgartools_segment_real_8k_shape. Post-pivot
    # (pure acquisition, no curated 2.02/7.01/8.01 filter) the layer emits a
    # section for EVERY reported item: exhibit-bearing → furnished-from-exhibit,
    # others → filed-from-body.
    exhibit_text = (
        "Exhibit 99.1\nApple reports second quarter results\n"
        "March quarter records for total company revenue ..."
    )
    ninety_body = "Item 9.01.\xa0\xa0Financial Statements and Exhibits\n(d) Exhibit 99.1"
    eightk = _MockEightK(
        items=["Item 2.02", "Item 9.01"],
        press_releases=[
            _MockPressRelease(document="a8-kex991q2202603282026.htm", text=exhibit_text),
        ],
        body_texts={
            # the 8-K BODY announcement for 2.02 — a sentinel that must NOT be the
            # text source (the exhibit is); if the code read this the text assert
            # below would catch it.
            "Item 2.02": "8-K BODY ANNOUNCEMENT for Item 2.02 — must NOT be sourced",
            "Item 9.01": ninety_body,
        },
    )
    filing = _segmentable_filing("8-K", eightk)

    sections = sec_client.segment_filing(filing)

    by_item = {s["item"]: s for s in sections}
    # EVERY reported item is emitted — the exhibit-bearing 2.02 AND Item 9.01,
    # not only the curated exhibit-item subset.
    assert set(by_item) == {"Item 2.02", "Item 9.01"}, (
        "8-K must emit a section for EVERY reported item obj.items enumerates"
    )

    # --- exhibit-bearing item: sourced from EX-99.1, furnished ---
    two = by_item["Item 2.02"]
    assert "error" not in two, f"exhibit-present item must be a success: {two!r}"
    two_text = _read_text_path(two)
    assert two_text == exhibit_text, (
        "the exhibit-bearing item's text must come from the EX-99.x exhibit, "
        "NEVER the 8-K body announcement"
    )
    assert two["disclosure_status"] == "furnished"
    assert two["exhibit"] == "a8-kex991q2202603282026.htm"

    # --- every other reported item: own body text, filed (not furnished) ---
    nine = by_item["Item 9.01"]
    assert "error" not in nine, f"Item 9.01 must be a filed success section: {nine!r}"
    assert _read_text_path(nine) == ninety_body, (
        "a non-exhibit reported item carries its own obj[item] body text"
    )
    assert nine["disclosure_status"] == "filed", (
        "a body-sourced 8-K item is filed, not furnished"
    )
    assert "exhibit" not in nine, "a body-sourced item carries no exhibit provenance"

    # --- T5 missing-exhibit gap still fires for an exhibit-bearing item whose
    #     99.x is absent (re-asserted here per the plan) ---
    no_exhibit = _MockEightK(
        items=["Item 2.02", "Item 9.01"],
        press_releases=[],  # exhibit-bearing 2.02 reported, but no EX-99.x present
        body_texts={"Item 9.01": ninety_body},
    )
    gap_sections = {
        s["item"]: s for s in sec_client.segment_filing(_segmentable_filing("8-K", no_exhibit))
    }
    assert set(gap_sections) == {"Item 2.02", "Item 9.01"}
    gap = gap_sections["Item 2.02"]
    assert gap["error_class"] == "missing_exhibit", (
        "an exhibit-bearing item lacking its 99.x must still be a loud gap"
    )
    assert not gap.get("text_path"), "no fabricated text on a missing-exhibit gap"
    # the non-exhibit item is unaffected — still filed-from-body
    assert gap_sections["Item 9.01"]["disclosure_status"] == "filed"


# ---------------------------------------------------------------------------
# Task 5 — a reported 8-K exhibit-bearing item (2.02 / 7.01 / 8.01) that LACKS a
# resolvable Exhibit 99.x is a LOUD named gap (naming accession + item code),
# never a silent skip, an empty section, or an uncaught IndexError. Also folds
# in the T4 code-quality finding on `_segment_8k`'s positional item[i] ->
# releases[i] pairing: it must NOT silently mis-attribute an exhibit when >= 2
# exhibit-bearing items are reported (per-item correspondence not determinable),
# nor raise an uncaught IndexError on a count mismatch — both become loud gaps.
# ---------------------------------------------------------------------------
# Reuses the Task-4 8-K grounding (this module's docstring) UNCHANGED — the
# missing / ambiguous exhibit is modelled on the same ``obj.press_releases``
# path (an empty or count-mismatched press_releases list is the real
# missing-exhibit signal there, per the live 5.42.0 capture), so no NEW
# edgartools attribute is touched by Task 5.


def test_8k_reported_item_without_exhibit_emits_gap(sec_client):
    # No @req tag: this dispatch's plan/spec trace by
    # `<change-id> / Requirement / Scenario` join keys, not registered REQ-ids
    # (see report) — @req omitted per the implementer contract.
    # Scenario: `8-K Missing-Exhibit Gap / Reported item without exhibit`.
    eightk = _MockEightK(
        items=["Item 2.02", "Item 9.01"],  # 2.02 reported, but no EX-99.x present
        press_releases=[],  # empty press_releases = the missing-exhibit signal
        body_texts={"Item 9.01": "Item 9.01.\xa0\xa0Financial Statements and Exhibits"},
    )
    filing = _segmentable_filing("8-K", eightk)

    sections = sec_client.segment_filing(filing)

    by_item = {s["item"]: s for s in sections}
    # the reported exhibit-bearing item is NOT omitted from output
    assert "Item 2.02" in by_item, (
        "a reported item lacking its exhibit must still appear as a gap slot, "
        "never be dropped from output"
    )
    slot = by_item["Item 2.02"]
    assert "error" in slot, f"missing-exhibit item must be a loud slot: {slot!r}"
    assert slot["error_class"] == "missing_exhibit"
    assert "Item 2.02" in slot["error"], "gap must name the item code"
    assert "0000320193-24-000123" in slot["error"], "gap must name the accession"
    assert not slot.get("text"), "no fabricated/empty text for a missing-exhibit item"


@pytest.mark.parametrize(
    "release_count",
    [
        # (i) >= 2 exhibit-bearing items reported with >= 2 exhibits — per-item
        # correspondence is NOT determinable; positional pairing would SILENTLY
        # mis-attribute an exhibit to the wrong item.
        pytest.param(2, id="two-items-two-releases-nonpositional"),
        # (ii) count mismatch — positional releases[i] would raise an UNCAUGHT
        # IndexError out of segment_filing.
        pytest.param(1, id="two-items-one-release-count-mismatch"),
    ],
)
def test_8k_unsafe_pairing_emits_gap_per_item(sec_client, release_count):
    # No @req tag (see test_8k_reported_item_without_exhibit_emits_gap).
    # Folds the T4 code-quality finding: silent positional mis-attribution +
    # uncaught IndexError -> a loud named gap per affected item (arc mandate:
    # silent-wrong is the enemy — fail loud, never mis-attribute).
    press = [
        _MockPressRelease(document=f"ex99-{n}.htm", text=f"exhibit body {n}")
        for n in range(1, release_count + 1)
    ]
    eightk = _MockEightK(
        items=["Item 2.02", "Item 7.01", "Item 9.01"],  # 2 exhibit-bearing items
        press_releases=press,
        body_texts={"Item 9.01": "Item 9.01.\xa0\xa0Financial Statements and Exhibits"},
    )
    filing = _segmentable_filing("8-K", eightk)

    # must NOT raise an uncaught IndexError out of segment_filing
    sections = sec_client.segment_filing(filing)

    by_item = {s["item"]: s for s in sections}
    for item_code in ("Item 2.02", "Item 7.01"):
        assert item_code in by_item, f"{item_code} must not be dropped from output"
        slot = by_item[item_code]
        assert "error" in slot, (
            f"unsafe pairing must be a loud gap, not a positional guess: {slot!r}"
        )
        assert slot["error_class"] == "missing_exhibit"
        assert item_code in slot["error"], "gap must name the item code"
        assert "0000320193-24-000123" in slot["error"], "gap must name the accession"
        assert not slot.get("text"), "no mis-attributed exhibit text on an unsafe gap"


# ---------------------------------------------------------------------------
# Task 6 — every SUCCESS section carries a complete provenance tuple (accession,
# cik, item id, filingDate + period_of_report where available) AND a
# reconstructable SEC Archives URL to the SECTION'S OWN source document: the
# filing's primary doc for a 10-K/10-Q section, the sourced Exhibit 99.x for an
# 8-K section — reconstructable WITHOUT an additional lookup.
# ---------------------------------------------------------------------------
# Reuses the Task-2 Filing-shape grounding (D7) UNCHANGED — provenance reads only
# accession_no / cik / filing_date / period_of_report / filing_url, the SAME
# attrs _filing_ref already reads (anchored live by test_data_markets_live.py::
# test_edgartools_acquire_real_10k_shape; filing_date a datetime.date, NOT str).
# No NEW edgartools attribute is touched by Task 6, so no new live anchor is
# required. The exact URL exemplars below are pinned against the fixture values.


def test_every_section_carries_full_provenance(sec_client):
    # No @req tag: this dispatch's plan/spec trace by
    # `<change-id> / Requirement / Scenario` join keys, not registered REQ-ids
    # (see report) — @req omitted per the implementer contract.
    # Scenario: `Section Provenance Completeness / Provenance tuple present on
    # every section`. Exercises BOTH URL branches: a 10-K (primary-doc) AND an
    # 8-K (exhibit-doc), so a section's URL points at its OWN source, not always
    # the primary doc.

    # --- 10-K: primary-doc URL branch (both Item 7 + Item 1A sections) ---
    tenk = _MockTenK(
        management_discussion="Item 7.\xa0\xa0Management's Discussion body ...",
        risk_factors="Item 1A.\xa0\xa0Risk Factors body ...",
    )
    tenk_filing = _segmentable_filing("10-K", tenk)

    tenk_sections = sec_client.segment_filing(tenk_filing)

    assert tenk_sections, "10-K must emit at least one section"
    for section in tenk_sections:
        assert "error" not in section, f"expected a success section: {section!r}"
        assert section["item"], "provenance carries the item id"
        assert section["accession"] == "0000320193-24-000123"
        assert section["cik"] == 320193
        assert section["filingDate"] == "2024-11-01"  # disclosure date, ISO str
        assert section["period_of_report"] == "2024-09-28"
        # URL points at the filing's PRIMARY document, reconstructable from the
        # tuple fields alone: data/{cik}/{accession-no-dashes}/{primary doc}.
        assert section["url"] == (
            "https://www.sec.gov/Archives/edgar/data/320193/"
            "000032019324000123/aapl-20240928.htm"
        )

    # --- 8-K: exhibit-doc URL branch (URL is the section's OWN exhibit) ---
    exhibit_text = (
        "Exhibit 99.1\nApple reports second quarter results\n"
        "March quarter records for total company revenue ..."
    )
    eightk = _MockEightK(
        items=["Item 2.02", "Item 9.01"],
        press_releases=[
            _MockPressRelease(document="a8-kex991q2202603282026.htm", text=exhibit_text),
        ],
        body_texts={"Item 9.01": "Item 9.01.\xa0\xa0Financial Statements and Exhibits"},
    )
    eightk_filing = _segmentable_filing("8-K", eightk)

    # post-pivot the 8-K emits a section per reported item; the exhibit-doc URL
    # branch under test is Item 2.02's (its URL points at ITS OWN exhibit).
    eightk_by_item = {s["item"]: s for s in sec_client.segment_filing(eightk_filing)}
    section = eightk_by_item["Item 2.02"]

    assert "error" not in section, f"exhibit-present item must be a success: {section!r}"
    assert section["item"] == "Item 2.02"
    assert section["accession"] == "0000320193-24-000123"
    assert section["cik"] == 320193
    assert section["filingDate"] == "2024-11-01"
    assert section["period_of_report"] == "2024-09-28"
    # the 8-K section's URL points at ITS OWN source exhibit, not the primary doc
    assert section["url"] == (
        "https://www.sec.gov/Archives/edgar/data/320193/"
        "000032019324000123/a8-kex991q2202603282026.htm"
    )


# ---------------------------------------------------------------------------
# Task 7 — paths-not-content: each SUCCESS section's text is written to a file
# under the toolkit cache dir and referenced by `text_path`; the section dict
# (and thus the JSON result) does NOT inline the section body.
# ---------------------------------------------------------------------------
# Reuses the Task-3 TenK grounding UNCHANGED — no NEW edgartools attribute is
# touched: the section text is already extracted, Task 7 only moves it out of
# the section dict into a file. The cache dir is pinned to a pytest tmp_path by
# the autouse `_isolated_cache` fixture so these runtime-written files never
# pollute the real cache or the repo tree.


def test_section_text_written_to_path_not_inlined(sec_client):
    # No @req tag: this dispatch's plan/spec trace by
    # `<change-id> / Requirement / Scenario` join keys, not registered REQ-ids
    # (see report) — @req omitted per the implementer contract.
    # Scenario: `Paths-Not-Content Section Emission / Section text written to
    # file`.
    mda_text = "Item 7.\xa0\xa0Management's Discussion body — long narrative ..."
    risk_text = "Item 1A.\xa0\xa0Risk Factors body — long narrative ..."
    tenk = _MockTenK(management_discussion=mda_text, risk_factors=risk_text)
    filing = _segmentable_filing("10-K", tenk)

    sections = sec_client.segment_filing(filing)

    by_item = {s["item"]: s for s in sections}
    # the section dict does NOT inline the body; it carries a path to a file
    # whose contents equal the extracted section text (assert BOTH sections so
    # per-(accession,item) keying is exercised — two files, distinct bodies).
    assert _read_text_path(by_item["Item 7"]) == mda_text
    assert _read_text_path(by_item["Item 1A"]) == risk_text

    # re-running is deterministic (same path per accession+item, stable body) —
    # never wall-clock-derived; a warm re-run reads back the same content.
    resegmented = {s["item"]: s for s in sec_client.segment_filing(filing)}
    assert resegmented["Item 7"]["text_path"] == by_item["Item 7"]["text_path"]
    assert _read_text_path(resegmented["Item 7"]) == mda_text


def test_section_text_path_contains_traversal_attempt(sec_client, tmp_path):
    # No @req tag: this dispatch's plan/spec trace by
    # `<change-id> / Requirement / Scenario` join keys, not registered REQ-ids
    # (see report). Defense-in-depth hardening (security-checklist CHK-SEC-004,
    # path traversal): a crafted accession / item id containing `../` must be
    # sanitized + containment-guarded so the section-text write can NEVER escape
    # <cache>/sec_edgar/sections/ — structurally certifiable for ANY segment,
    # not just the digit-dash accessions the real SEC flow produces.
    sections_root = (tmp_path / "sec_edgar" / "sections").resolve()

    crafted_accession = "../../../../etc/0000-99-000001"  # traversal in accession
    crafted_item = "../../Item ../evil"                    # traversal in item id

    # 1) the computed path is contained (pure computation, no I/O) — this is the
    #    line that fails RED before the accession segment is sanitized.
    computed = sec_client._section_text_path(crafted_accession, crafted_item).resolve()
    assert computed.is_relative_to(sections_root), (
        f"crafted accession/item escaped the sections dir: {computed}"
    )

    # 2) the write lands under the sections dir and reads back the exact body.
    written = Path(
        sec_client._write_section_text(crafted_accession, crafted_item, "sensitive body")
    ).resolve()
    assert written.is_relative_to(sections_root), (
        f"section-text write escaped the sections dir: {written}"
    )
    assert written.read_text(encoding="utf-8") == "sensitive body"


# ---------------------------------------------------------------------------
# Task 8 — fail-loud per-section aggregation: a per-item extraction THROW is
# ISOLATED into that item's error slot (the other items still segment, nothing
# crashes segment_filing), and the aggregate section list classifies through
# pack.py's REAL _classify_result as partial (some fail) / failed (all fail) —
# never a fabricated/silent-empty section, never a propagated exception.
# ---------------------------------------------------------------------------
# Reuses the Task-3 TenK grounding: management_discussion (Item 7) / risk_factors
# (Item 1A) are the real edgartools 5.42.0 TenK properties. To model a real
# extraction failure (edgartools raising WHILE parsing one item), the mock below
# makes the risk_factors PROPERTY raise on access while management_discussion
# returns text normally (fixtures-mirror-producer-shape — a property that raises
# mid-parse is a real edgartools failure mode, sibling to issue #710's None). The
# all-fail case models filing.obj() itself raising (primary doc unparseable).


class _RaisingRiskFactorsTenK:
    """A ``TenK`` whose Item 1A subscript RAISES on access while Item 7 extracts
    normally — mirrors edgartools raising mid-parse for a single item
    (fixtures-mirror-producer-shape: a real subscript that raises, not an invented
    shape). Item 1A stays ENUMERATED on ``obj.items`` (the throw is at extraction,
    not enumeration), so ``segment_filing`` isolates the throw to that one item's
    slot while Item 7 still segments."""

    def __init__(self, *, management_discussion):
        self._management_discussion = management_discussion
        self.items = ["Item 7", "Item 1A"]

    def __getitem__(self, key):
        if key == "Item 1A":
            raise ValueError("edgartools failed to parse Item 1A (risk_factors)")
        return {"Item 7": self._management_discussion}.get(key)


def _obj_raising_filing(form: str = "10-K") -> SimpleNamespace:
    """A mock ``Filing`` whose ``.obj()`` itself RAISES — the whole primary
    document cannot be fetched/parsed (all-requested-sections-fail scenario).
    Carries the T2 provenance attrs ``segment_filing`` reads for its error
    slots."""
    filing = _segmentable_filing(form, None)

    def _raise():
        raise RuntimeError(
            "edgartools could not build the typed filing object (obj())"
        )

    filing.obj = _raise
    return filing


def _pack_classify(sections: list) -> tuple:
    """Classify a section LIST through pack.py's REAL ``_classify_result`` — the
    same downstream ``_status`` classifier the memo pipeline feeds. Proves
    partial-vs-failed is what the real classifier returns, not merely the
    per-section dict shape. pack.py is pure stdlib, importable offline, and lives
    in the same scripts dir already on sys.path."""
    if str(MARKETS_SCRIPTS) not in sys.path:
        sys.path.insert(0, str(MARKETS_SCRIPTS))
    pack = importlib.import_module("pack")
    return pack._classify_result({"sections": sections})


def test_segment_one_section_throws_isolated_partial(sec_client):
    # No @req tag: this dispatch's plan/spec trace by
    # `<change-id> / Requirement / Scenario` join keys, not registered REQ-ids
    # (see report) — @req omitted per the implementer contract.
    # Scenario: `Fail-Loud Per-Section Extraction / One section fails within a
    # multi-section filing`.
    tenk = _RaisingRiskFactorsTenK(
        management_discussion="Item 7.\xa0\xa0Management's Discussion body ..."
    )
    filing = _segmentable_filing("10-K", tenk)

    # must NOT crash out of segment_filing (RED: the raising property propagates)
    sections = sec_client.segment_filing(filing)

    by_item = {s["item"]: s for s in sections}
    assert set(by_item) == {"Item 7", "Item 1A"}, (
        "the throwing item is isolated, not dropped; the other item still segments"
    )
    # Item 7 emitted normally (text file-backed, Task 7)
    assert "error" not in by_item["Item 7"]
    assert (
        _read_text_path(by_item["Item 7"])
        == "Item 7.\xa0\xa0Management's Discussion body ..."
    )
    # Item 1A is a loud, named extraction-error slot — never empty/fabricated
    slot = by_item["Item 1A"]
    assert "error" in slot, f"throwing item must be a loud slot: {slot!r}"
    assert slot["error_class"] == "extraction_error"
    assert "Item 1A" in slot["error"], "error slot must name the failing item"
    assert not slot.get("text"), "no fabricated text for a failed item"
    # feeds _status: the REAL pack.py classifier calls this PARTIAL, not success
    status, degraded = _pack_classify(sections)
    assert status == "partial", (
        f"one-fails-within-many must classify partial via pack.py, got {status!r}"
    )


def test_all_sections_fail_form_level_when_obj_raises(sec_client):
    # No @req tag (see test_segment_one_section_throws_isolated_partial).
    # Scenario: `Fail-Loud Per-Section Extraction / All requested sections fail`.
    # Post-pivot the item set is DYNAMIC (`obj.items`), so once `filing.obj()`
    # fails wholesale the items are UNKNOWABLE — the all-fail path emits a SINGLE
    # form-level error slot (as the 8-K path already does), never a hardcoded
    # item list.
    filing = _obj_raising_filing("10-K")

    # must NOT crash out of segment_filing (RED: the filing.obj() raise propagates)
    sections = sec_client.segment_filing(filing)

    by_item = {s["item"]: s for s in sections}
    assert set(by_item) == {"form 10-K"}, (
        "a wholesale 10-K obj() failure emits a single form-level slot — the item "
        "set is unknowable once obj() itself raises"
    )
    slot = by_item["form 10-K"]
    assert "error" in slot, f"all-fail slot must be loud: {slot!r}"
    assert slot["error_class"] == "extraction_error"
    assert not slot.get("text"), "no fabricated text on a wholesale failure"
    # feeds _status: the REAL pack.py classifier calls this FAILED — no top-level
    # success is claimed.
    status, degraded = _pack_classify(sections)
    assert status == "failed", (
        f"all-requested-fail must classify failed via pack.py, got {status!r}"
    )


def test_segment_8k_all_fail_when_obj_raises(sec_client):
    # No @req tag: DEFENSIVE completeness for the all-fail branch on a form whose
    # requested items (8-K reported item codes) live on obj() and are unreadable
    # once obj() itself raises — the handler must still fail loud with a named
    # slot, never crash on an unenumerable form (contract rule 11; the recall
    # lesson test-except-branches-explicitly — every branch of the all-fail
    # handler is exercised, not just the 10-K static-item path).
    filing = _obj_raising_filing("8-K")

    sections = sec_client.segment_filing(filing)

    assert sections, "8-K wholesale failure must still emit at least one loud slot"
    for slot in sections:
        assert "error" in slot, f"8-K all-fail slot must be loud: {slot!r}"
        assert slot["error_class"] == "extraction_error"
        assert not slot.get("text"), "no fabricated text on a wholesale 8-K failure"
    status, _ = _pack_classify(sections)
    assert status == "failed", (
        f"8-K wholesale failure must classify failed via pack.py, got {status!r}"
    )


# ---------------------------------------------------------------------------
# Task 9 — furnished-vs-filed disclosure status: an 8-K Item 2.02/7.01/8.01
# section sourced from an Exhibit 99.x carries `disclosure_status == "furnished"`
# (a legal-status tag derived from the SOURCE TYPE — 8-K exhibit = furnished — NOT
# read from edgartools), DISTINCT from a 10-K/10-Q section's `"filed"`.
# ---------------------------------------------------------------------------
# Reuses the Task-3 TenK grounding + Task-4 8-K grounding UNCHANGED — no NEW
# edgartools attribute is touched: disclosure_status is derived form-statically
# (8-K exhibit-following path vs 10-K/10-Q filed path), not read from any
# producer surface.


def test_8k_exhibit_section_marked_furnished(sec_client):
    # No @req tag: this dispatch's plan/spec trace by
    # `<change-id> / Requirement / Scenario` join keys, not registered REQ-ids
    # (see report) — @req omitted per the implementer contract.
    # Scenario: `Furnished-vs-filed status propagates to the memo / Exhibit 99.x
    # marked furnished`. Asserts BOTH legs so the distinction is proven, not just
    # the presence of the key: an 8-K exhibit section is "furnished" AND a 10-K
    # section is "filed".

    # --- 8-K exhibit-sourced section → "furnished" ---
    exhibit_text = (
        "Exhibit 99.1\nApple reports second quarter results\n"
        "March quarter records for total company revenue ..."
    )
    eightk = _MockEightK(
        items=["Item 2.02", "Item 9.01"],
        press_releases=[
            _MockPressRelease(document="a8-kex991q2202603282026.htm", text=exhibit_text),
        ],
        body_texts={"Item 9.01": "Item 9.01.\xa0\xa0Financial Statements and Exhibits"},
    )
    eightk_filing = _segmentable_filing("8-K", eightk)

    # post-pivot the 8-K emits a section per reported item; the exhibit-bearing
    # Item 2.02 is the furnished-from-exhibit leg under test here (Item 9.01's
    # body leg is filed, covered by test_segment_8k_emits_all_reported_items).
    eightk_by_item = {s["item"]: s for s in sec_client.segment_filing(eightk_filing)}
    furnished = eightk_by_item["Item 2.02"]

    assert "error" not in furnished, f"exhibit-present item must be a success: {furnished!r}"
    assert furnished["disclosure_status"] == "furnished", (
        f"8-K exhibit-sourced section must be tagged furnished: {furnished!r}"
    )

    # --- 10-K section → "filed" (the distinct filed status) ---
    tenk = _MockTenK(
        management_discussion="Item 7.\xa0\xa0Management's Discussion body ...",
        risk_factors="Item 1A.\xa0\xa0Risk Factors body ...",
    )
    tenk_filing = _segmentable_filing("10-K", tenk)

    filed_sections = sec_client.segment_filing(tenk_filing)

    assert filed_sections, "10-K must emit at least one section"
    for section in filed_sections:
        assert "error" not in section, f"expected a success section: {section!r}"
        assert section["disclosure_status"] == "filed", (
            f"10-K section must be tagged filed: {section!r}"
        )
    # the tag is DISTINCT across source types, not a single constant
    assert furnished["disclosure_status"] != filed_sections[0]["disclosure_status"], (
        "furnished (8-K exhibit) must be distinct from filed (10-K)"
    )


# ---------------------------------------------------------------------------
# Task 10 — Distinct acquisition failure classes: timeout (retryable) + version
# drift (shape guard). A timed-out fetch is its OWN `error_class="timeout"` — NOT
# merged into the generic `extraction_error`/gap — carved out ABOVE the generic
# `except Exception` in BOTH the inner per-thunk and the outer
# obj()/extractor-build handlers (narrower-except-first). A successfully-thunked
# section value that is not the pinned-5.42.0 `str` (a plausible post-upgrade
# shape) fails loud as `error_class="version_drift"`, never emitted as
# possibly-wrong section text.
# ---------------------------------------------------------------------------
# D7 grounding: on the pinned edgartools 5.42.0, a TenK/TenQ section accessor
# (`management_discussion` / `risk_factors` / `obj["Part I, Item 2"]`) resolves
# to a `str` (or `None` when the item is absent — issue #710) — the shape the
# segmenters and `_build_section` already assume. edgartools does its HTTP over
# `httpx`, so a real fetch timeout surfaces as `httpx.TimeoutException` (a family
# NOT importable in offline CI); the builtin `TimeoutError` stands in for it here
# and the module classifies both via `_TIMEOUT_EXC_TYPES`. A future major (v5 was
# itself a rewrite; `TenK.items` canonicalization already changed across 3.x)
# could change a section accessor to return a structured object instead of a
# `str`; the shape guard turns that drift into a loud `version_drift` slot rather
# than silently emitting a wrong body. Source: plan Notes §edgartools grounding
# (Drift) + Task 10 External surfaces, captured 2026-07-12.


class _TimeoutRiskFactorsTenK:
    """A ``TenK`` whose Item 1A subscript raises the builtin ``TimeoutError`` on
    access while Item 7 extracts normally — models a per-item fetch that exceeds
    the timeout (fixtures-mirror-producer-shape: edgartools does its HTTP over
    ``httpx``, so a real per-item timeout is an ``httpx.TimeoutException``, not
    importable in offline CI; the builtin ``TimeoutError`` is its offline stand-in
    and both are classified by the module's ``_TIMEOUT_EXC_TYPES``). Item 1A stays
    ENUMERATED on ``obj.items`` so the timeout is isolated to its slot."""

    def __init__(self, *, management_discussion):
        self._management_discussion = management_discussion
        self.items = ["Item 7", "Item 1A"]

    def __getitem__(self, key):
        if key == "Item 1A":
            raise TimeoutError("edgartools fetch of Item 1A exceeded the timeout")
        return {"Item 7": self._management_discussion}.get(key)


def test_timeout_is_distinct_class(sec_client):
    # No @req tag: this dispatch's plan/spec trace by
    # `<change-id> / Requirement / Scenario` join keys, not registered REQ-ids
    # (see report) — @req omitted per the implementer contract.
    # Scenario: `Distinct acquisition failure classes / Network timeout is its
    # own class` (inner per-thunk handler).
    tenk = _TimeoutRiskFactorsTenK(
        management_discussion="Item 7.\xa0\xa0Management's Discussion body ..."
    )
    filing = _segmentable_filing("10-K", tenk)

    sections = sec_client.segment_filing(filing)

    by_item = {s["item"]: s for s in sections}
    assert set(by_item) == {"Item 7", "Item 1A"}, (
        "the timed-out item is isolated, not dropped; the other item still segments"
    )
    # Item 7 still segments normally (text file-backed, Task 7)
    assert "error" not in by_item["Item 7"]
    assert (
        _read_text_path(by_item["Item 7"])
        == "Item 7.\xa0\xa0Management's Discussion body ..."
    )
    # Item 1A is a DISTINCT timeout class — NOT merged into extraction_error/gap
    slot = by_item["Item 1A"]
    assert "error" in slot, f"timed-out item must be a loud slot: {slot!r}"
    assert slot["error_class"] == "timeout", (
        f"a timeout must be its own class, not extraction_error/absent_item: {slot!r}"
    )
    assert slot["error_class"] not in ("extraction_error", "absent_item"), (
        "timeout must NOT be merged into the generic gap/error classes"
    )
    assert slot.get("retryable") is True, "a timeout is a retryable failure class"
    assert not slot.get("text"), "no fabricated text for a timed-out item"


def test_timeout_all_sections_when_obj_times_out(sec_client):
    # No @req tag (see test_timeout_is_distinct_class).
    # Scenario: `Distinct acquisition failure classes / Network timeout is its
    # own class` — the OUTER handler (filing.obj()/extractor build) timing out
    # must ALSO carve timeout out above the generic all-fail extraction_error, so
    # a wholesale timeout classifies the form-level slot as timeout.
    filing = _segmentable_filing("10-K", None)

    def _timeout():
        raise TimeoutError("edgartools timed out building the typed filing object")

    filing.obj = _timeout

    sections = sec_client.segment_filing(filing)

    by_item = {s["item"]: s for s in sections}
    assert set(by_item) == {"form 10-K"}, (
        "a wholesale 10-K obj() timeout emits a single form-level slot — the item "
        "set is unknowable once obj() itself times out"
    )
    slot = by_item["form 10-K"]
    assert slot["error_class"] == "timeout", (
        f"a wholesale timeout must classify the form-level slot as timeout: {slot!r}"
    )
    assert slot.get("retryable") is True
    assert not slot.get("text"), "no fabricated text on a wholesale timeout"


def test_version_drift_fails_loud(sec_client):
    # No @req tag (see test_timeout_is_distinct_class).
    # Scenario: `Distinct acquisition failure classes / edgartools version-drift
    # is caught, not silently trusted`. On the pinned 5.42.0 a section accessor
    # returns a `str`; a post-upgrade structured shape must fail loud, not be
    # written out as possibly-wrong text.
    tenk = _MockTenK(
        # a plausible post-upgrade structured shape instead of the pinned `str`
        management_discussion={"heading": "MD&A", "body": "structured, not a str"},
        risk_factors="Item 1A.\xa0\xa0Risk Factors body ...",  # still a valid str
    )
    filing = _segmentable_filing("10-K", tenk)

    sections = sec_client.segment_filing(filing)

    by_item = {s["item"]: s for s in sections}
    assert set(by_item) == {"Item 7", "Item 1A"}
    # Item 1A (a valid str) still segments normally (text file-backed, Task 7)
    assert "error" not in by_item["Item 1A"]
    assert _read_text_path(by_item["Item 1A"])
    # Item 7 returned an unexpected shape → a loud version-drift slot, never text
    slot = by_item["Item 7"]
    assert "error" in slot, f"unexpected shape must be a loud slot: {slot!r}"
    assert slot["error_class"] == "version_drift", (
        f"a shape mismatch must fail loud on version drift: {slot!r}"
    )
    assert "text_path" not in slot, "possibly-wrong section text must NOT be emitted"
    assert not slot.get("text"), "no fabricated/possibly-wrong text on a shape mismatch"


# ---------------------------------------------------------------------------
# Task 11 — SEC fair-access: rate-limit backoff preserved + filing cache reuse.
# A cached narrative-section fetch (`fetch_narrative_sections`) reads OUR
# cache_util layer on a warm accession instead of re-hitting edgartools
# (Scenario "Filing cache avoids re-fetch"); a simulated transient 429/403 on
# the edgartools acquisition path is surfaced LOUDLY and never swallowed into a
# silent drop / fabricated success / poisoned cache, leaving edgartools' OWN
# pyrate-limiter/stamina backoff authoritative (Scenario "Rate-limit backoff").
# ---------------------------------------------------------------------------
# D7 grounding: edgartools 5.42.0 ships its own rate-limit + retry stack
# (`pyrate-limiter` + `stamina` + `httpxthrottlecache`) OVER `httpx` — NOT the
# legacy `requests`-based `_sec_get` throttle (which never covered the
# edgartools path). A 429/403 is retried WITH jitter INSIDE the edgartools
# acquisition call (edgar.get_by_accession_number / Company(...).get_filings),
# so the retry itself is edgartools-internal and exercised only on the network
# path. The offline-testable slice AT OUR WRAPPER BOUNDARY is that we (a) actually
# ENTER the edgartools acquisition path (never pre-empt it before that backoff
# can act) and (b) surface a transient failure loudly WITHOUT swallowing it or
# caching it as success. The cache layer is cache_util envelope v2.0 (immutable
# TTL, key `narrative_{accession}`) — keyed by disclosure IDENTITY, never
# wall-clock (the as_of invariant: a same-day re-run of the same accession is a
# HIT, not a double-fetch). Sources: plan Notes §edgartools grounding + in-repo
# cache_util.py:170-252, captured 2026-07-12.


def test_filing_cache_avoids_refetch(sec_client):
    # No @req tag: this dispatch's plan/spec trace by
    # `<change-id> / Requirement / Scenario` join keys, not registered REQ-ids
    # (see report) — @req omitted per the implementer contract.
    # Scenario: `SEC EDGAR fair-access compliance / Filing cache avoids re-fetch`.
    # Mocks the REAL edgartools producer boundary (`edgar.get_by_accession_number`
    # returning a RAW Filing), NOT `acquire_filing` — so the acquire->segment seam
    # (`fetch_narrative_sections` must obtain the RAW filing, never the JSON ref
    # dict) runs end-to-end and a masked dict-crash cannot slip through
    # (fixtures-mirror-producer-shape). The call-count spy is the stub's own
    # `.call_count` on the edgartools boundary.
    accession = "0000320193-24-000123"
    tenk = _MockTenK(
        management_discussion="Item 7.\xa0\xa0Management's Discussion body ...",
        risk_factors="Item 1A.\xa0\xa0Risk Factors body ...",
    )
    filing = _segmentable_filing("10-K", tenk)

    stub = sec_client.edgar_stub
    stub.get_by_accession_number.return_value = filing

    first = sec_client.fetch_narrative_sections(accession)
    assert stub.get_by_accession_number.call_count == 1, (
        "a cold accession must hit the edgartools boundary exactly once"
    )
    assert first.get("_cache") == "miss", f"cold run must be a cache miss: {first!r}"
    first_items = {s["item"] for s in first["sections"]}
    assert first_items == {"Item 7", "Item 1A"}, "cold run segments the 10-K"

    second = sec_client.fetch_narrative_sections(accession)

    # the warm re-run read cache — ZERO additional edgartools calls
    assert stub.get_by_accession_number.call_count == 1, (
        "a warm accession must read cache, not re-hit edgartools: "
        f"{stub.get_by_accession_number.call_count} calls"
    )
    assert second.get("_cache") == "hit", f"warm run must be a cache hit: {second!r}"
    second_items = {s["item"] for s in second["sections"]}
    assert second_items == first_items, "cached sections must match the cold-run sections"


def test_rate_limit_backoff_not_swallowed(sec_client):
    # No @req tag (see test_filing_cache_avoids_refetch).
    # Scenario: `SEC EDGAR fair-access compliance / Rate-limit backoff`.
    # Honest offline slice (edgartools owns the internal retry, see the D7 note
    # above): a transient 429/403 escaping the edgartools acquisition path AFTER
    # edgartools' own backoff is surfaced LOUDLY — never swallowed into a silent
    # drop / fabricated success / poisoned cache — and the edgartools acquisition
    # path IS entered (we never pre-empt it before that backoff can act).
    stub = sec_client.edgar_stub
    accession = "0000320193-24-000123"

    class _RateLimited(Exception):
        """Stand-in for the edgartools httpx 429/403 that escapes
        get_by_accession_number AFTER edgartools' own `stamina` retries are
        exhausted (real type: httpx.HTTPStatusError, status 429 — not importable
        offline; edgartools does its HTTP over httpx per plan Notes)."""

    stub.get_by_accession_number.side_effect = _RateLimited(
        "429 Too Many Requests (SEC fair-access ceiling)"
    )

    result = sec_client.fetch_narrative_sections(accession)

    # (1) the edgartools acquisition path was actually ENTERED — we never
    #     short-circuit before edgartools' own pyrate-limiter/stamina backoff runs
    assert stub.get_by_accession_number.called, (
        "the edgartools acquisition path must be entered, not pre-empted"
    )
    # (2) the transient failure is surfaced LOUDLY, not swallowed into a silent
    #     drop or a fabricated empty-sections success
    assert isinstance(result, dict)
    assert "error" in result, f"a transient 429/403 must surface loudly: {result!r}"
    assert not result.get("sections"), "no fabricated sections on a failed acquisition"
    # (3) the failure is NOT cached as success — a re-run re-enters acquisition
    #     (no poisoned cache), so edgartools' backoff stays authoritative. Checks
    #     the ACTUAL edgartools cache key (`narrative_sections_`), the one this
    #     function writes — not the retired legacy `narrative_` key (which this
    #     function never touches, so asserting on it would pass vacuously).
    path = sec_client.cache_util.cache_path(
        "sec_edgar", f"narrative_sections_{accession}"
    )
    assert not path.exists(), "a failed acquisition must NOT be cached as success"


def test_edgartools_cache_key_distinct_from_legacy(sec_client):
    # No @req tag (see test_filing_cache_avoids_refetch).
    # Scenario: `SEC EDGAR fair-access compliance / Filing cache avoids re-fetch`
    # — regression guard. The LEGACY regex `fetch_narrative` wrote
    # `narrative_{accession}` with `sections` as a DICT (item->body); the new
    # edgartools `fetch_narrative_sections` emits `sections` as a LIST. Both share
    # the immutable TTL + envelope v2.0, so if they shared the SAME cache key a
    # machine with a warm LEGACY entry would get a schema-passing HIT of the WRONG
    # shape (dict where a list is expected) — a never-self-healing landmine under
    # immutable TTL. This asserts the edgartools payload uses a DISTINCT key: a
    # pre-seeded legacy dict-shaped entry must NOT be read by the new function.
    # Mocks the REAL edgartools producer boundary (get_by_accession_number) and
    # spies its call count — so the legacy key NOT being aliased shows up as a
    # fresh edgartools hit (fixtures-mirror-producer-shape; the acquire->segment
    # seam runs end-to-end).
    accession = "0000320193-24-000123"

    # pre-seed the LEGACY key with a legacy DICT-shaped payload (as fetch_narrative
    # would have written it on a real machine before the T12 rewire)
    legacy_path = sec_client.cache_util.cache_path("sec_edgar", f"narrative_{accession}")
    sec_client.cache_util.save_cache(
        legacy_path,
        {"accession": accession, "sections": {"Item 7": "legacy dict body ..."}},
    )

    tenk = _MockTenK(
        management_discussion="Item 7.\xa0\xa0Management's Discussion body ...",
        risk_factors="Item 1A.\xa0\xa0Risk Factors body ...",
    )
    filing = _segmentable_filing("10-K", tenk)
    stub = sec_client.edgar_stub
    stub.get_by_accession_number.return_value = filing

    result = sec_client.fetch_narrative_sections(accession)

    # the legacy dict-shaped entry is NOT aliased — the new function used its own
    # distinct key, so it was a MISS and freshly acquired + segmented via edgartools
    assert stub.get_by_accession_number.call_count == 1, (
        "the edgartools fetch must NOT read the legacy narrative_ key — distinct "
        f"cache key required (edgartools calls={stub.get_by_accession_number.call_count})"
    )
    assert isinstance(result["sections"], list), (
        f"sections must be the edgartools LIST shape, never the legacy dict: {result!r}"
    )
    assert {s["item"] for s in result["sections"]} == {"Item 7", "Item 1A"}


def test_fetch_narrative_sections_wrapper_surfaces_partial_failure(sec_client):
    # No @req tag: this dispatch's plan/spec trace by
    # `<change-id> / Requirement / Scenario` join keys, not registered REQ-ids
    # (see report) — @req omitted per the implementer contract.
    # Scenario: whole-branch review 🟡 remediation — the per-section fail-loud
    # state must be visible on the RESULT WRAPPER itself, not only on the bare
    # `sections` list. A downstream consumer (e.g. the future memo pipeline
    # embedding this wrapper as a sub-field) inspects the WHOLE wrapper; the
    # section-level error slots sit below `sections` where a one-level classifier
    # walking a dict sub-field never reaches them, so the wrapper must carry its
    # OWN `narrative_status` + `failed_items` health summary. Drives
    # `fetch_narrative_sections` at the edgartools boundary (the established
    # `edgar_stub.get_by_accession_number` mock), NOT a bare-list reclassification.
    stub = sec_client.edgar_stub

    # --- PARTIAL: Item 7 extracts, Item 1A raises mid-parse (one of two fails) ---
    partial_acc = "0000320193-24-000123"
    partial_filing = _segmentable_filing(
        "10-K",
        _RaisingRiskFactorsTenK(
            management_discussion="Item 7.\xa0\xa0Management's Discussion body ..."
        ),
    )
    stub.get_by_accession_number.return_value = partial_filing
    partial = sec_client.fetch_narrative_sections(partial_acc)
    assert partial.get("narrative_status") == "partial", (
        "a wrapper with one failed section must surface narrative_status=partial "
        f"WITHOUT a consumer unwrapping `sections`: {partial!r}"
    )
    assert partial.get("failed_items") == ["Item 1A"], (
        f"the wrapper must NAME the failing item id, not hide it in sections: {partial!r}"
    )
    # additive-only: the 5 CLI contract keys survive unchanged alongside the summary
    assert {"accession", "cik", "form", "filingDate", "sections"} <= set(partial)

    # --- FAILED: obj() raises wholesale → a single form-level error slot ---
    failed_acc = "0000320193-24-000900"
    stub.get_by_accession_number.return_value = _obj_raising_filing("10-K")
    failed = sec_client.fetch_narrative_sections(failed_acc)
    assert failed.get("narrative_status") == "failed", (
        f"a wrapper whose every section errors must surface failed: {failed!r}"
    )
    assert failed.get("failed_items") == ["form 10-K"], (
        f"the wholesale form-level failed slot must be named on the wrapper: {failed!r}"
    )

    # --- HEALTHY: every section extracts → ok, no failure signal ---
    ok_acc = "0000320193-24-000700"
    ok_filing = _segmentable_filing(
        "10-K",
        _MockTenK(
            management_discussion="Item 7.\xa0\xa0MD&A body ...",
            risk_factors="Item 1A.\xa0\xa0Risk Factors body ...",
        ),
    )
    stub.get_by_accession_number.return_value = ok_filing
    healthy = sec_client.fetch_narrative_sections(ok_acc)
    assert healthy.get("narrative_status") == "ok", (
        f"an all-sections-ok wrapper must read healthy: {healthy!r}"
    )
    assert healthy.get("failed_items") == [], (
        f"a healthy wrapper carries no failed items: {healthy!r}"
    )


# ---------------------------------------------------------------------------
# Task 12 — Preserve the `--action narrative` CLI surface across the edgartools
# migration + retire the legacy regex internals. `action_narrative(accession)`
# must return the SAME contract keys (accession/cik/form/filingDate/sections)
# with the SAME exit-code discipline (1 iff `error`), now populated via
# edgartools (`fetch_narrative_sections`), NOT the legacy regex `fetch_narrative`.
# And the retired TOC-vs-body regex path (`parse_item_sections`,
# `_ITEM_HEADER_RE`, the legacy `fetch_narrative` + its `_TextExtractor` /
# exhibit-index skip heuristic) must no longer be on the code path — asserted via
# removal (`not hasattr`). No new edgartools attribute is touched: the wiring
# reuses acquire_filing + segment_filing (mocked as in Tasks 2-11).
# ---------------------------------------------------------------------------


def test_cli_narrative_contract_preserved(sec_client, monkeypatch):
    # No @req tag: this dispatch's plan/spec trace by
    # `<change-id> / Requirement / Scenario` join keys, not registered REQ-ids
    # (see report) — @req omitted per the implementer contract.
    # Scenario: `CLI Surface Preserved Across the edgartools Migration / Existing
    # CLI invocation still resolves`. The narrative action returns the SAME
    # contract keys, now populated via edgartools, with exit-code discipline
    # `1 iff error` — on BOTH a cold (miss) and a warm (hit) invocation.
    accession = "0000320193-24-000123"
    # Post-pivot the 10-K enumerates its FULL item set (not the retired Item 7/1A
    # subset), so the contract must hold with an all-items `sections` list.
    tenk = _MockTenK(
        item_texts={
            "Item 1": "Item 1.\xa0\xa0Business body ...",
            "Item 1A": "Item 1A.\xa0\xa0Risk Factors body ...",
            "Item 7": "Item 7.\xa0\xa0Management's Discussion body ...",
            "Item 8": "Item 8.\xa0\xa0Financial Statements body ...",
        }
    )
    filing = _segmentable_filing("10-K", tenk)
    # Mock the REAL edgartools producer boundary (get_by_accession_number returns
    # a RAW Filing), NOT acquire_filing — so the acquire->segment seam runs
    # end-to-end. Mocking acquire_filing would inject a RAW filing acquire_filing
    # never actually produces (it returns a JSON ref DICT), masking the dict-crash
    # on the real path (fixtures-mirror-producer-shape).
    stub = sec_client.edgar_stub
    stub.get_by_accession_number.return_value = filing

    # --- cold run (cache miss): contract keys populated via edgartools ---
    result = sec_client.action_narrative(accession)

    for key in ("accession", "cik", "form", "filingDate", "sections"):
        assert key in result, (
            f"CLI narrative contract dropped key {key!r}: {result!r}"
        )
    assert result["accession"] == accession
    assert result["cik"] == 320193
    assert result["form"] == "10-K"
    assert result["filingDate"] == "2024-11-01"  # disclosure date, ISO str
    # `sections` preserves the KEY; the VALUE is now the edgartools LIST shape
    # (the new internal representation), not the legacy dict
    assert isinstance(result["sections"], list), (
        f"sections must be the edgartools LIST shape: {result!r}"
    )
    assert {s["item"] for s in result["sections"]} == {
        "Item 1",
        "Item 1A",
        "Item 7",
        "Item 8",
    }, f"sections must enumerate the full item set post-pivot: {result!r}"
    assert result.get("action") == "narrative"
    # exit-code discipline: a success carries NO top-level error → sys.exit(0)
    assert "error" not in result, f"a successful narrative must not carry error: {result!r}"

    # --- warm run (cache hit): the contract keys survive the cache round-trip ---
    warm = sec_client.action_narrative(accession)
    assert warm.get("_cache") == "hit", f"warm run must be a cache hit: {warm!r}"
    for key in ("accession", "cik", "form", "filingDate", "sections"):
        assert key in warm, (
            f"warm-cache narrative dropped contract key {key!r}: {warm!r}"
        )
    assert warm["cik"] == 320193 and warm["form"] == "10-K"
    assert warm["filingDate"] == "2024-11-01"

    # --- error leg: exit-code discipline `1 iff error` (identity unset) ---
    monkeypatch.setattr(sec_client, "USER_AGENT", "")
    err = sec_client.action_narrative(accession)
    assert "error" in err, f"identity-unset narrative must surface a loud error: {err!r}"
    assert err.get("action") == "narrative"


def test_regex_internals_off_code_path(sec_client):
    # No @req tag (see test_cli_narrative_contract_preserved).
    # Scenario: `CLI Surface Preserved Across the edgartools Migration / Regex
    # internals no longer on the code path`. The legacy TOC-vs-body regex
    # segmentation is RETIRED from the module — asserted via removal, the
    # strongest form of "not invoked on any narrative segmentation".
    assert not hasattr(sec_client, "parse_item_sections"), (
        "legacy parse_item_sections (TOC-vs-body regex) must be retired from the "
        "code path — edgartools' section API performs segmentation instead"
    )
    assert not hasattr(sec_client, "_ITEM_HEADER_RE"), (
        "legacy _ITEM_HEADER_RE regex must be retired from the code path"
    )
    assert not hasattr(sec_client, "fetch_narrative"), (
        "legacy regex fetch_narrative must be retired — action_narrative now "
        "resolves via the edgartools fetch_narrative_sections"
    )
    assert not hasattr(sec_client, "_TextExtractor"), (
        "the regex-only HTML _TextExtractor must be retired once its sole "
        "consumer (fetch_narrative) is gone"
    )
