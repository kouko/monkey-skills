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
    """Mirror edgartools 5.42.0 ``TenK`` typed object (``filing.obj()``).

    Live capture confirmed ``management_discussion`` (Item 7) and
    ``risk_factors`` (Item 1A) are ``str`` properties; an item absent from the
    filing yields ``None`` (edgartools issue #710). Plain attributes so a
    renamed property RAISES ``AttributeError`` rather than silently reading as
    absent (fixtures-mirror-producer-shape; the version-drift shape guard on a
    non-``str`` return value is Task 10, below).
    """

    def __init__(self, *, management_discussion, risk_factors):
        self.management_discussion = management_discussion
        self.risk_factors = risk_factors


class _MockTenQ:
    """Mirror edgartools 5.42.0 ``TenQ`` typed object (``filing.obj()``).

    Live capture confirmed ``TenQ`` has NO ``management_discussion`` property;
    Item 2 (MD&A) is read via the subscript ``obj["Part I, Item 2"]`` -> ``str``
    (or ``None`` when the item is absent). Mirrors that subscript-returns-None
    -on-absent shape; a real ``TenQ`` subscript on a 10-K's missing key returned
    ``None``, not ``KeyError``.
    """

    def __init__(self, sections):
        self._sections = dict(sections)

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


def test_segment_10k_item7_and_item1a(sec_client):
    # No @req tag: this dispatch's plan/spec trace by
    # `<change-id> / Requirement / Scenario` join keys, not registered REQ-ids
    # (see report) — @req omitted per the implementer contract.
    # Scenario: `10-K/10-Q Item Segmentation / 10-K MD&A and Risk Factors
    # segmentation`.
    tenk = _MockTenK(
        management_discussion="Item 7.\xa0\xa0Management's Discussion body ...",
        risk_factors="Item 1A.\xa0\xa0Risk Factors body ...",
    )
    filing = _segmentable_filing("10-K", tenk)

    sections = sec_client.segment_filing(filing)

    assert isinstance(sections, list)
    by_item = {s["item"]: s for s in sections}
    assert set(by_item) == {"Item 7", "Item 1A"}, "10-K must emit distinct Item 7 + Item 1A"
    assert by_item["Item 7"] is not by_item["Item 1A"], "distinct section objects"
    assert "error" not in by_item["Item 7"]
    assert "error" not in by_item["Item 1A"]
    # text is file-backed (Task 7): read it back from text_path, assert the SAME
    # content the inline `text` key previously carried (no weakening).
    assert _read_text_path(by_item["Item 7"]) == "Item 7.\xa0\xa0Management's Discussion body ..."
    assert _read_text_path(by_item["Item 1A"]) == "Item 1A.\xa0\xa0Risk Factors body ..."


def test_segment_10q_item2(sec_client):
    # No @req tag (see test_segment_10k_item7_and_item1a).
    # Scenario: `10-K/10-Q Item Segmentation / 10-Q MD&A segmentation`.
    tenq = _MockTenQ({"Part I, Item 2": "Item 2.\xa0\xa010-Q MD&A body ..."})
    filing = _segmentable_filing("10-Q", tenq)

    sections = sec_client.segment_filing(filing)

    by_item = {s["item"]: s for s in sections}
    assert set(by_item) == {"Item 2"}, "10-Q must emit an Item 2 section"
    assert "error" not in by_item["Item 2"]
    # text is file-backed (Task 7): read it back, assert the SAME content.
    assert _read_text_path(by_item["Item 2"]) == "Item 2.\xa0\xa010-Q MD&A body ..."


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
# absent (fixtures-mirror-producer-shape). Deliberately NO __getitem__ on
# _MockEightK: the 8-K BODY announcement (obj["Item 2.02"]) must NOT be the text
# source — reading it would raise here, proving the text comes from the exhibit.


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
    EX-99.x press-release exhibits. No ``__getitem__`` on purpose (see the
    section comment above)."""

    def __init__(self, *, items, press_releases):
        self.items = list(items)
        self.press_releases = list(press_releases)


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
        items=["Item 2.02", "Item 9.01"],  # 9.01 = the exhibit-list item, not a narrative item
        press_releases=[
            _MockPressRelease(document="a8-kex991q2202603282026.htm", text=exhibit_text),
        ],
    )
    filing = _segmentable_filing("8-K", eightk)

    sections = sec_client.segment_filing(filing)

    by_item = {s["item"]: s for s in sections}
    assert set(by_item) == {"Item 2.02"}, (
        "8-K emits a section for the reported exhibit-following item; Item 9.01 "
        "(exhibit list) is not itself a narrative item"
    )
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
    )
    filing = _segmentable_filing("8-K", eightk)

    sections = sec_client.segment_filing(filing)

    by_item = {s["item"]: s for s in sections}
    assert set(by_item) == {item_code}
    slot = by_item[item_code]
    assert "error" not in slot
    # text sourced from the corresponding exhibit, not the 8-K body alone;
    # file-backed via text_path (Task 7), read back to assert the SAME content.
    section_text = _read_text_path(slot)
    assert section_text == exhibit_text
    assert item_code in section_text
    assert slot["exhibit"] == "ex99-1.htm"


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
    )
    eightk_filing = _segmentable_filing("8-K", eightk)

    (section,) = sec_client.segment_filing(eightk_filing)

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
    """A ``TenK`` whose Item 1A (``risk_factors``) extraction RAISES on access
    while Item 7 (``management_discussion``) extracts normally — mirrors
    edgartools raising mid-parse for a single item
    (fixtures-mirror-producer-shape: a real property that raises, not an invented
    shape)."""

    def __init__(self, *, management_discussion):
        self.management_discussion = management_discussion

    @property
    def risk_factors(self):
        raise ValueError("edgartools failed to parse Item 1A (risk_factors)")


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


def test_segment_all_sections_fail_when_obj_raises(sec_client):
    # No @req tag (see test_segment_one_section_throws_isolated_partial).
    # Scenario: `Fail-Loud Per-Section Extraction / All requested sections fail`.
    filing = _obj_raising_filing("10-K")

    # must NOT crash out of segment_filing (RED: the filing.obj() raise propagates)
    sections = sec_client.segment_filing(filing)

    by_item = {s["item"]: s for s in sections}
    assert set(by_item) == {"Item 7", "Item 1A"}, (
        "every requested 10-K item gets an error slot when obj() fails wholesale"
    )
    for item_id in ("Item 7", "Item 1A"):
        slot = by_item[item_id]
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
    )
    eightk_filing = _segmentable_filing("8-K", eightk)

    (furnished,) = sec_client.segment_filing(eightk_filing)

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
# possibly-wrong section text. Plus a static drift-guard test that
# `_FORM_REQUESTED_ITEMS` (the wholesale-all-fail enumeration map — a SECOND
# source of truth) cannot silently diverge from the segmenters' actual requested
# item ids (folded T8 code-quality finding).
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
    """A ``TenK`` whose Item 1A (``risk_factors``) extraction raises the builtin
    ``TimeoutError`` on access while Item 7 (``management_discussion``) extracts
    normally — models a per-item fetch that exceeds the timeout
    (fixtures-mirror-producer-shape: edgartools does its HTTP over ``httpx``, so a
    real per-item timeout is an ``httpx.TimeoutException``, not importable in
    offline CI; the builtin ``TimeoutError`` is its offline stand-in and both are
    classified by the module's ``_TIMEOUT_EXC_TYPES``)."""

    def __init__(self, *, management_discussion):
        self.management_discussion = management_discussion

    @property
    def risk_factors(self):
        raise TimeoutError("edgartools fetch of Item 1A exceeded the timeout")


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
    # a wholesale timeout classifies every requested section as timeout.
    filing = _segmentable_filing("10-K", None)

    def _timeout():
        raise TimeoutError("edgartools timed out building the typed filing object")

    filing.obj = _timeout

    sections = sec_client.segment_filing(filing)

    by_item = {s["item"]: s for s in sections}
    assert set(by_item) == {"Item 7", "Item 1A"}, (
        "every requested 10-K item gets a slot when obj() times out wholesale"
    )
    for item_id in ("Item 7", "Item 1A"):
        slot = by_item[item_id]
        assert slot["error_class"] == "timeout", (
            f"a wholesale timeout must classify every section as timeout: {slot!r}"
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


def test_form_requested_items_match_segmenters(sec_client):
    # No @req tag: a static drift-GUARD test (folded T8 code-quality finding), not
    # one of the two named Task-10 scenarios — @req omitted per contract rule 11.
    # This is a GREEN-on-arrival characterization guard (it locks an existing
    # invariant, so no production code drives it): `_FORM_REQUESTED_ITEMS` (the
    # wholesale-all-fail enumeration map) is a SECOND source of truth for the
    # 10-K/10-Q requested item ids, distinct from what the segmenters actually
    # request. If a segmenter adds/renames an item and the map is not updated, the
    # all-fail path would silently under-report — this test makes that drift fail
    # loud instead.
    tenk = _MockTenK(management_discussion="x", risk_factors="y")
    tenk_ids = tuple(
        entry[0]
        for entry in sec_client._segment_10k(tenk, _segmentable_filing("10-K", tenk))
    )
    assert tenk_ids == sec_client._FORM_REQUESTED_ITEMS["10-K"], (
        "_FORM_REQUESTED_ITEMS['10-K'] drifted from _segment_10k's requested items"
    )

    tenq = _MockTenQ({"Part I, Item 2": "z"})
    tenq_ids = tuple(
        entry[0]
        for entry in sec_client._segment_10q(tenq, _segmentable_filing("10-Q", tenq))
    )
    assert tenq_ids == sec_client._FORM_REQUESTED_ITEMS["10-Q"], (
        "_FORM_REQUESTED_ITEMS['10-Q'] drifted from _segment_10q's requested items"
    )
