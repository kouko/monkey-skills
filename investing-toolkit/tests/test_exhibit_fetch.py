"""test_exhibit_fetch.py — Route B exhibit acquisition (fetch_exhibit_documents).

Offline unit tests for `sec_edgar_client.fetch_exhibit_documents`, the Route B
8-K earnings-exhibit acquisition path. It resolves the latest earnings 8-K
(Item 2.02) or a given accession, enumerates ALL EX-99.* attachments via
`filing.attachments` (NOT `_segment_8k` / `fetch_narrative_sections`), returns
per-document RAW HTML + metadata, and caches each document under a NEW key
family `exhibit_raw_{accession}_{document}` — never the legacy
`narrative_sections_{accession}` slot (cache-key-collision-across-migration).

edgartools (~100MB, pyarrow) is deliberately NOT installed in offline CI, so
`edgar` AND `requests` are injected as `sys.modules` mocks BEFORE importing
sec_edgar_client (importing-a-module-runs-its-module-level-imports) — the
module's top-level `import requests` and lazy `import edgar` then resolve to the
stubs. Mirrors the established offline fixture in tests/data/test_sec_narrative.py.

External-surface grounding — edgartools 5.42.0 `filing.attachments`:
  probed live 2026-07-19 (edgartools 5.42.0). An ``Attachment`` carries
  ``sequence_number`` / ``description`` / ``document`` (the filename) / ``ixbrl``
  / ``path`` / ``document_type`` (e.g. "EX-99.1") / ``size`` as constructor
  fields, and exposes ``content`` as a PROPERTY that downloads + returns the raw
  document bytes/text. ``filing.attachments`` is iterable, yielding those
  ``Attachment`` objects. This is the surface the Route B spike used
  (scratchpad/route-b-inventory-spike.md, NFLX acc 0001065280-25-000033 —
  ``filing.attachments`` -> the EX-99.1 attachment -> ``.content`` = 429,234
  chars of raw HTML, NOT the flattened ``.text()`` used by ``_segment_8k``).
  The fakes below mirror that shape: plain-attribute classes so a renamed
  producer attr RAISES rather than silently reading as absent
  (fixtures-mirror-producer-shape), and ``.content`` a property that counts its
  reads so a test can prove the fetch path (not a cache alias) ran.

@req: this dispatch's plan (docs/loom/plans/2026-07-19-8k-earnings-kpi-intake.md,
Task 1) traces work by "Brief item covered", NOT registered loom-spec REQ-ids,
so per the implementer contract @req tags are omitted on every test here (see
report). No id is minted to fill the gap.
"""
from __future__ import annotations

import datetime
import importlib
import sys
from pathlib import Path
from unittest import mock

import pytest

ROOT = Path(__file__).resolve().parents[1]
MARKETS_SCRIPTS = ROOT / "skills" / "data-markets" / "scripts"


@pytest.fixture
def sec_client():
    """Import sec_edgar_client with `edgar` AND `requests` stubbed in sys.modules.

    Mirrors tests/data/test_sec_narrative.py::sec_client — both non-stdlib
    module-level/lazy deps are stubbed BEFORE the import so the module builds
    offline, and the prior sys.modules state is restored on teardown.
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
    """Pin the toolkit cache dir at a pytest tmp_path so the exhibit-raw cache
    files stay isolated and never pollute the real cache or the repo tree
    (F.I.R.S.T). Exercises the real cache_util.resolve_cache_dir precedence."""
    monkeypatch.setenv("INVESTING_TOOLKIT_CACHE", str(tmp_path))
    yield


class _FakeAttachment:
    """Mirror an edgartools 5.42.0 ``Attachment`` (a member of
    ``filing.attachments``).

    Constructor fields grounded by a live probe 2026-07-19:
    ``Attachment(sequence_number, description, document, ixbrl, path,
    document_type, size, ...)``. ``content`` is a PROPERTY that (in the real
    object) downloads the document; here it returns a seeded string and counts
    its reads so a test can prove the fetch path ran (rather than a cache
    alias). Plain attributes so a renamed producer field RAISES."""

    def __init__(self, *, document, document_type, content):
        self.sequence_number = "1"
        self.description = document_type
        self.document = document
        self.ixbrl = False
        self.path = f"/Archives/edgar/.../{document}"
        self.document_type = document_type
        self.size = len(content)
        self._content = content
        self.content_reads = 0

    @property
    def content(self):
        self.content_reads += 1
        return self._content


class _FakeFiling:
    """Mirror the raw edgartools ``Filing`` surface fetch_exhibit_documents reads:
    ``accession_no`` / ``cik`` / ``form`` / ``filing_date`` (a ``datetime.date``,
    NOT a str — matching the live capture in sec_edgar_client) and
    ``attachments`` (an iterable of ``_FakeAttachment``)."""

    def __init__(self, *, accession_no, attachments):
        self.accession_no = accession_no
        self.cik = 1065280
        self.form = "8-K"
        self.filing_date = datetime.date(2025, 1, 21)
        self.attachments = list(attachments)


def _nflx_two_exhibit_filing(accession: str) -> _FakeFiling:
    """A 2-exhibit earnings 8-K fixture (EX-99.1 + EX-99.2) plus a non-exhibit
    primary document — proves ALL EX-99.* are returned AND that non-EX-99
    attachments are filtered out."""
    return _FakeFiling(
        accession_no=accession,
        attachments=[
            # the primary 8-K body doc — NOT an EX-99.x exhibit, must be filtered
            _FakeAttachment(
                document="nflx-8k.htm", document_type="8-K",
                content="<html>8-K body announcement</html>",
            ),
            _FakeAttachment(
                document="ex991_q424.htm", document_type="EX-99.1",
                content="<html><table><tr><td>Global Streaming Paid Memberships</td>"
                        "<td>301.63</td></tr></table></html>",
            ),
            _FakeAttachment(
                document="ex992_q424.htm", document_type="EX-99.2",
                content="<html><table><tr><td>Stock buyback</td>"
                        "<td>$1,000</td></tr></table></html>",
            ),
        ],
    )


def test_new_cache_key_never_aliases_legacy_narrative_key(sec_client, monkeypatch):
    # No living-spec REQ-id: this plan traces tasks by Brief item, not REQ-ids.
    # Regression for cache-key-collision-across-migration: a pre-warmed machine
    # with a LEGACY narrative_sections_{accession} entry (a DICT-shaped payload)
    # must NOT be served by fetch_exhibit_documents — it reads its OWN
    # exhibit_raw_* key family, misses (nothing there yet), and runs the fresh
    # attachment-fetch path. Never an alias of the immutable-TTL legacy slot.
    import cache_util

    accession = "0001065280-25-000033"

    # Pre-seed the LEGACY key with a dict-shaped payload (the collision bait).
    legacy_path = cache_util.cache_path("sec_edgar", f"narrative_sections_{accession}")
    cache_util.save_cache(legacy_path, {
        "accession": accession,
        "sections": [{"item": "Item 2.02", "text_path": "/legacy/leg.txt"}],
        "poison": "LEGACY-NARRATIVE-PAYLOAD-MUST-NOT-BE-SERVED",
    })

    # Spy on cache_util.load_cache to record EVERY key path it is asked to read.
    read_paths: list[str] = []
    real_load = cache_util.load_cache

    def _spy_load(path, ttl):
        read_paths.append(str(path))
        return real_load(path, ttl)

    monkeypatch.setattr(cache_util, "load_cache", _spy_load)

    filing = _nflx_two_exhibit_filing(accession)
    sec_client.edgar_stub.get_by_accession_number.return_value = filing

    result = sec_client.fetch_exhibit_documents("NFLX", accession=accession)

    # The legacy narrative key is NEVER read (no alias across the migration seam).
    assert not any("narrative_sections" in p for p in read_paths), (
        f"legacy narrative_sections key must never be read: {read_paths!r}"
    )
    # The fresh fetch path ran — the EX-99.x attachments' content was read.
    ex99 = [a for a in filing.attachments if a.document_type.startswith("EX-99")]
    assert all(a.content_reads >= 1 for a in ex99), (
        "cache miss on the new key must invoke the fresh attachment-fetch path"
    )
    # The returned bytes are the FRESH exhibit HTML, never the legacy payload.
    docs = result["documents"]
    joined = "".join(d["raw_html"] for d in docs)
    assert "LEGACY-NARRATIVE-PAYLOAD-MUST-NOT-BE-SERVED" not in joined
    assert "301.63" in joined, "the real EX-99.1 exhibit HTML must be returned"

    # Cache writes landed under exhibit_raw_* keys ONLY (new family).
    for doc in docs:
        new_path = cache_util.cache_path(
            "sec_edgar", f"exhibit_raw_{accession}_{doc['document']}"
        )
        assert new_path.exists(), f"exhibit cache must land under new key: {new_path}"


def test_multi_exhibit_8k_returns_all_ex99_documents(sec_client):
    # No living-spec REQ-id: this plan traces tasks by Brief item, not REQ-ids.
    # A 2-exhibit earnings 8-K (EX-99.1 + EX-99.2) must return BOTH documents —
    # NOT a >=2-exhibit loud-gap drop. Route B goes via filing.attachments, so
    # _segment_8k's LOOM-SIMPLIFY >=2-exhibit-item gap ceiling is not on the
    # execution path (spike: acc 0001065280-25-000033 tripped that ceiling under
    # the old path; the attachments path sidesteps it).
    accession = "0001065280-25-000033"
    filing = _nflx_two_exhibit_filing(accession)
    sec_client.edgar_stub.get_by_accession_number.return_value = filing

    result = sec_client.fetch_exhibit_documents("NFLX", accession=accession)

    docs = result["documents"]
    by_doc = {d["document"]: d for d in docs}
    # BOTH EX-99.* returned; the non-EX-99 primary 8-K body doc filtered out.
    assert set(by_doc) == {"ex991_q424.htm", "ex992_q424.htm"}, (
        f"both EX-99.* exhibits must be returned, non-EX-99 filtered: {list(by_doc)}"
    )
    assert result["document_count"] == 2

    ex991 = by_doc["ex991_q424.htm"]
    assert ex991["exhibit_type"] == "EX-99.1"
    assert ex991["accession"] == accession
    assert ex991["filingDate"] == "2025-01-21"  # datetime.date serialized to ISO
    assert "301.63" in ex991["raw_html"], "raw HTML, not flattened text"

    ex992 = by_doc["ex992_q424.htm"]
    assert ex992["exhibit_type"] == "EX-99.2"
    assert "Stock buyback" in ex992["raw_html"]


def test_accession_none_resolves_latest_earnings_8k(sec_client, monkeypatch):
    # No living-spec REQ-id: this plan traces tasks by Brief item, not REQ-ids.
    # accession=None → resolve the latest earnings 8-K (Item 2.02) for the
    # ticker, then fetch its EX-99.* exhibits. The resolution reuses the shipped
    # resolve_cik → list_filings → select_narrative_filings policy (item-2.02
    # selection), all monkeypatched here so the test stays offline + deterministic.
    resolved_accession = "0001065280-25-000033"

    monkeypatch.setattr(
        sec_client, "resolve_cik", lambda ticker: {"ticker": ticker, "cik": 1065280}
    )
    earnings_row = {
        "form": "8-K", "filingDate": "2025-01-21", "accessionNumber": resolved_accession,
        "primaryDocument": "nflx-8k.htm", "primaryDocDescription": "8-K",
        "items": "2.02,9.01", "reportDate": "2024-12-31",
    }
    monkeypatch.setattr(sec_client, "list_filings", lambda *a, **k: [earnings_row])

    filing = _nflx_two_exhibit_filing(resolved_accession)

    def _by_accession(accession):
        assert accession == resolved_accession, (
            f"must fetch the RESOLVED earnings-8-K accession, got {accession!r}"
        )
        return filing

    sec_client.edgar_stub.get_by_accession_number.side_effect = _by_accession

    result = sec_client.fetch_exhibit_documents("NFLX")  # accession defaults to None

    assert result["accession"] == resolved_accession
    assert {d["document"] for d in result["documents"]} == {
        "ex991_q424.htm", "ex992_q424.htm",
    }
