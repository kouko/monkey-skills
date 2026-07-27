"""test_sec_submissions_pagination.py — `fetch_submissions` must follow
`filings.files[]`.

SEC packs at most one year, or the most recent 1,000 filings (whichever is
more), into `submissions/CIK##########.json`'s `filings.recent` block; older
filings live in the archive documents enumerated by `filings.files[]`. Reading
only `recent` truncates a filer's history by its TOTAL filing volume, so the
most actively-filing companies return the LEAST history — measured 2026-07-27,
JPM returned 1 of its 27 10-Ks, BAC 1 of 32, META 2 of 14, while low-volume
Coca-Cola returned all 8 requested. Brief:
docs/loom/specs/2026-07-27-sec-submissions-pagination.md.

Offline: `requests` is injected as a `sys.modules` stub BEFORE importing
sec_edgar_client (its module-level `import requests` runs at import time, not
at call time), and every test stubs `_sec_get` — no network.

External-surface grounding (live, 2026-07-27, real SEC responses):
  - `filings.files[]` entries carry `{name, filingCount, filingFrom, filingTo}`;
    `name` is a bare filename, e.g. `CIK0001326801-submissions-001.json`,
    fetched from `https://data.sec.gov/submissions/<name>`.
  - Each archive document's TOP LEVEL is the same parallel-array dict shape as
    `filings.recent` (`form`, `filingDate`, `accessionNumber`, ...) — it is NOT
    wrapped in another `filings`/`recent` layer.
  - Page counts are wildly uneven: 28 of the 33 flagged filers have 0-3 pages,
    but JPM has 68, C has 39, BAC has 20.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path
from unittest import mock

import pytest

ROOT = Path(__file__).resolve().parents[2]
MARKETS_SCRIPTS = ROOT / "skills" / "data-markets" / "scripts"

if "requests" not in sys.modules:  # module-level `import requests` runs on import
    sys.modules["requests"] = mock.MagicMock(name="requests")
if str(MARKETS_SCRIPTS) not in sys.path:
    sys.path.insert(0, str(MARKETS_SCRIPTS))

import cache_util  # noqa: E402
import sec_edgar_client as sec  # noqa: E402

CIK = 1326801

# The parallel-array keys `list_filings` reads (sec_edgar_client.py:464-471).
ARRAY_KEYS = (
    "form",
    "filingDate",
    "accessionNumber",
    "primaryDocument",
    "primaryDocDescription",
    "items",
    "reportDate",
)


def _rows(*specs):
    """Build a `recent`-shaped parallel-array dict from (form, date) pairs."""
    block = {k: [] for k in ARRAY_KEYS}
    for form, date in specs:
        block["form"].append(form)
        block["filingDate"].append(date)
        block["accessionNumber"].append(f"acc-{form}-{date}")
        block["primaryDocument"].append(f"{form}-{date}.htm")
        block["primaryDocDescription"].append(form)
        block["items"].append("")
        block["reportDate"].append(date)
    return block


def _main_doc(recent, files):
    return {
        "cik": CIK,
        "name": "Meta Platforms, Inc.",
        "filings": {"recent": recent, "files": files},
    }


@pytest.fixture(autouse=True)
def _isolated_cache(tmp_path, monkeypatch):
    monkeypatch.setenv("INVESTING_TOOLKIT_CACHE", str(tmp_path / "cache"))
    yield


@pytest.fixture
def responder(monkeypatch):
    """Stub `_sec_get` with a URL→payload map that records every call."""
    calls: list[str] = []
    routes: dict[str, object] = {}

    def _get(url, *, as_json=True):
        calls.append(url)
        if url not in routes:
            return {"error": f"unrouted test URL: {url}"}
        payload = routes[url]
        return payload() if callable(payload) else payload

    monkeypatch.setattr(sec, "_sec_get", _get)
    return type("Responder", (), {"calls": calls, "routes": routes})()


def _url_main(cik=CIK):
    return sec.SEC_SUBMISSIONS_URL.format(cik=cik)


def _url_page(name):
    return f"https://data.sec.gov/submissions/{name}"


# ---------------------------------------------------------------------------
# 1. The defect itself: archive pages must be merged into `recent`.
# ---------------------------------------------------------------------------

def test_fetch_submissions_merges_archive_pages_into_recent(responder):
    """The whole defect in one assertion: a filer with two archive pages must
    come back with ALL its 10-Ks, not just the ones the recent block held."""
    responder.routes[_url_main()] = _main_doc(
        _rows(("10-K", "2026-01-29"), ("8-K", "2025-10-29")),
        [
            {"name": "CIK0001326801-submissions-001.json", "filingCount": 2,
             "filingFrom": "2020-01-29", "filingTo": "2024-01-31"},
            {"name": "CIK0001326801-submissions-002.json", "filingCount": 1,
             "filingFrom": "2013-02-01", "filingTo": "2013-02-01"},
        ],
    )
    responder.routes[_url_page("CIK0001326801-submissions-001.json")] = _rows(
        ("10-K", "2024-01-31"), ("10-K", "2020-01-29"),
    )
    responder.routes[_url_page("CIK0001326801-submissions-002.json")] = _rows(
        ("10-K", "2013-02-01"),
    )

    out = sec.fetch_submissions(CIK)

    assert "error" not in out, out
    recent = out["data"]["filings"]["recent"]
    assert recent["form"].count("10-K") == 4, (
        "all four 10-Ks must be present — one from `recent`, three from the "
        f"archive pages; got {recent['form']}"
    )
    assert "2013-02-01" in recent["filingDate"], (
        "the oldest archive page's rows must survive the merge"
    )


def test_merged_block_keeps_every_parallel_array_aligned(responder):
    """`list_filings` indexes the arrays positionally (`accn_list[i]`), so a
    merge that appends to some arrays and not others silently mislabels
    filings rather than failing."""
    responder.routes[_url_main()] = _main_doc(
        _rows(("10-K", "2026-01-29")),
        [{"name": "p1.json", "filingCount": 2,
          "filingFrom": "2024-01-31", "filingTo": "2025-01-31"}],
    )
    responder.routes[_url_page("p1.json")] = _rows(
        ("10-K", "2025-01-31"), ("10-Q", "2024-01-31"),
    )

    recent = sec.fetch_submissions(CIK)["data"]["filings"]["recent"]

    lengths = {k: len(recent[k]) for k in ARRAY_KEYS}
    assert len(set(lengths.values())) == 1, f"parallel arrays diverged: {lengths}"
    assert lengths["form"] == 3
    # Positional integrity: each row's accession must still match its own form+date.
    for i, (form, date) in enumerate(zip(recent["form"], recent["filingDate"])):
        assert recent["accessionNumber"][i] == f"acc-{form}-{date}", (
            f"row {i} lost positional alignment: {recent['accessionNumber'][i]}"
        )


def test_list_filings_reaches_the_archive_pages(responder):
    """The consumer-level statement of the bug: `list_filings` asking for 3
    10-Ks must get 3, not just the 1 the recent block held."""
    responder.routes[_url_main()] = _main_doc(
        _rows(("10-K", "2026-01-29"), ("8-K", "2025-11-01")),
        [{"name": "p1.json", "filingCount": 2,
          "filingFrom": "2024-01-31", "filingTo": "2025-01-31"}],
    )
    responder.routes[_url_page("p1.json")] = _rows(
        ("10-K", "2025-01-31"), ("10-K", "2024-01-31"),
    )

    rows = sec.list_filings(CIK, ["10-K"], 3)

    assert len(rows) == 3, f"expected 3 10-Ks across recent+archives, got {rows}"


# ---------------------------------------------------------------------------
# 2. Cache contract — the merged payload must not alias the truncated one.
# ---------------------------------------------------------------------------

def test_does_not_serve_the_legacy_truncated_cache_entry(responder):
    """A cache entry written by the OLD code is a truncated history that a
    reader cannot distinguish from a complete one. If the fixed code reads the
    legacy key, a warm 24h cache serves truncation from fixed code — the exact
    condition that makes a verification run lie
    (docs/loom/memory/cache-key-collision-across-migration.md)."""
    legacy_path = cache_util.cache_path("sec_edgar", f"submissions_{CIK:010d}")
    legacy_path.parent.mkdir(parents=True, exist_ok=True)
    cache_util.save_cache(legacy_path, {
        "cik": CIK,
        "fetched_at": "2026-07-27T00:00:00+00:00",
        "data": _main_doc(_rows(("10-K", "2026-01-29")), []),
    })

    responder.routes[_url_main()] = _main_doc(
        _rows(("10-K", "2026-01-29")),
        [{"name": "p1.json", "filingCount": 1,
          "filingFrom": "2025-01-31", "filingTo": "2025-01-31"}],
    )
    responder.routes[_url_page("p1.json")] = _rows(("10-K", "2025-01-31"))

    out = sec.fetch_submissions(CIK)

    recent = out["data"]["filings"]["recent"]
    assert recent["form"].count("10-K") == 2, (
        "the legacy (truncated) cache entry was served instead of a fresh "
        f"merged fetch: {recent['form']}"
    )


def test_archive_pages_are_not_refetched_when_the_main_document_expires(
    responder, monkeypatch
):
    """Archive pages are historical — the page covering 1994-2003 does not
    change — so they get their own longer-lived cache. Without it, JPM's 68
    pages are re-paid on every main-document TTL expiry."""
    responder.routes[_url_main()] = _main_doc(
        _rows(("10-K", "2026-01-29")),
        [{"name": "p1.json", "filingCount": 1,
          "filingFrom": "2025-01-31", "filingTo": "2025-01-31"}],
    )
    responder.routes[_url_page("p1.json")] = _rows(("10-K", "2025-01-31"))

    monkeypatch.setattr(sec, "TTL_SUBMISSIONS", 0)  # main doc always a miss

    sec.fetch_submissions(CIK)
    sec.fetch_submissions(CIK)

    page_fetches = [u for u in responder.calls if u.endswith("p1.json")]
    main_fetches = [u for u in responder.calls if u == _url_main()]
    assert len(main_fetches) == 2, "the main document should have been re-fetched"
    assert len(page_fetches) == 1, (
        f"archive page re-fetched {len(page_fetches)}x — pages must be cached "
        "independently of the main document's TTL"
    )


# ---------------------------------------------------------------------------
# 3. Failure must be an error, never a shorter answer.
# ---------------------------------------------------------------------------

def test_failed_archive_page_returns_an_error_not_a_partial_merge(responder):
    """A partial merge is the defect being fixed wearing a different hat: the
    caller cannot tell 'this filer has 3 10-Ks' from 'page 2 of 5 failed'."""
    responder.routes[_url_main()] = _main_doc(
        _rows(("10-K", "2026-01-29")),
        [
            {"name": "ok.json", "filingCount": 1,
             "filingFrom": "2025-01-31", "filingTo": "2025-01-31"},
            {"name": "broken.json", "filingCount": 1,
             "filingFrom": "2024-01-31", "filingTo": "2024-01-31"},
        ],
    )
    responder.routes[_url_page("ok.json")] = _rows(("10-K", "2025-01-31"))
    responder.routes[_url_page("broken.json")] = {
        "error": "SEC EDGAR HTTP 503: broken.json"
    }

    out = sec.fetch_submissions(CIK)

    assert "error" in out, f"a failed archive page must surface as an error: {out}"
    assert "data" not in out or not out.get("data"), (
        "a failed page must not return a silently-partial history alongside "
        f"the error: {out}"
    )


def test_a_failed_page_is_not_cached(responder):
    """`fetch_submissions` already declines to cache `_sec_get` errors
    (sec_edgar_client.py:411-412); a page failure must inherit that, or one
    503 poisons the filer's history for the whole TTL."""
    responder.routes[_url_main()] = _main_doc(
        _rows(("10-K", "2026-01-29")),
        [{"name": "flaky.json", "filingCount": 1,
          "filingFrom": "2025-01-31", "filingTo": "2025-01-31"}],
    )
    state = {"fail": True}

    def _flaky():
        if state["fail"]:
            state["fail"] = False
            return {"error": "SEC EDGAR HTTP 503: flaky.json"}
        return _rows(("10-K", "2025-01-31"))

    responder.routes[_url_page("flaky.json")] = _flaky

    first = sec.fetch_submissions(CIK)
    second = sec.fetch_submissions(CIK)

    assert "error" in first
    assert "error" not in second, f"the retry should succeed, got {second}"
    assert second["data"]["filings"]["recent"]["form"].count("10-K") == 2


# ---------------------------------------------------------------------------
# 4. Regression: the no-archive filer must behave exactly as before.
# ---------------------------------------------------------------------------

def test_filer_without_archive_pages_is_unchanged(responder):
    """Coca-Cola-shaped: everything requested already fits in `recent`."""
    responder.routes[_url_main()] = _main_doc(
        _rows(("10-K", "2026-02-20"), ("10-K", "2025-02-20")), []
    )

    out = sec.fetch_submissions(CIK)

    assert "error" not in out
    assert out["data"]["filings"]["recent"]["form"] == ["10-K", "10-K"]
    assert responder.calls == [_url_main()], (
        f"a filer with no archive pages must make exactly one request: "
        f"{responder.calls}"
    )


def test_cached_merged_payload_is_not_merged_a_second_time(responder):
    """The merged payload keeps SEC's own `filings.files[]` alongside a
    `recent` block that already contains those pages' rows. Re-merging such a
    payload would double every archived filing, so the cache-hit path must
    return it untouched."""
    responder.routes[_url_main()] = _main_doc(
        _rows(("10-K", "2026-01-29")),
        [{"name": "p1.json", "filingCount": 2,
          "filingFrom": "2024-01-31", "filingTo": "2025-01-31"}],
    )
    responder.routes[_url_page("p1.json")] = _rows(
        ("10-K", "2025-01-31"), ("10-K", "2024-01-31"),
    )

    first = sec.fetch_submissions(CIK)
    second = sec.fetch_submissions(CIK)

    assert second.get("_cache") == "hit", "second call should be a cache hit"
    assert (
        second["data"]["filings"]["recent"]["form"]
        == first["data"]["filings"]["recent"]["form"]
        == ["10-K", "10-K", "10-K"]
    ), f"rows changed between calls: {second['data']['filings']['recent']['form']}"


def test_ragged_recent_block_does_not_mislabel_filings(responder):
    """`merged_rows` is the LONGEST column in `recent`, so a SHORT column in
    the same block silently absorbs the next page's first rows — every filing
    after the gap gets another filing's accession number. `list_filings`'s
    `i < len(...)` guards turn this into wrong data rather than a crash, which
    is how it reaches `pack_reconstruct` as the wrong document filed under the
    wrong year."""
    ragged = _rows(
        ("10-K", "2026-04-01"), ("10-K", "2025-04-01"), ("10-K", "2024-04-01"),
    )
    ragged["accessionNumber"] = ragged["accessionNumber"][:2]  # 3 rows, 2 accessions
    ragged["reportDate"] = ragged["reportDate"][:2]
    responder.routes[_url_main()] = _main_doc(
        ragged,
        [{"name": "p1.json", "filingCount": 1,
          "filingFrom": "2023-04-01", "filingTo": "2023-04-01"}],
    )
    responder.routes[_url_page("p1.json")] = _rows(("10-K", "2023-04-01"))

    recent = sec.fetch_submissions(CIK)["data"]["filings"]["recent"]

    assert len(recent["filingDate"]) == len(set(recent["filingDate"])), (
        f"a filing date was duplicated by the join: {recent['filingDate']}"
    )
    for form, date, accession in zip(
        recent["form"], recent["filingDate"], recent["accessionNumber"]
    ):
        assert accession in (None, f"acc-{form}-{date}"), (
            f"row {date} carries accession {accession!r} — another filing's"
        )


def test_column_absent_from_recent_is_backfilled_not_left_short(responder):
    """SEC omits a column entirely when no row in a block uses it. A column
    appearing for the FIRST time in an archive page must be back-filled to the
    rows already merged, or every one of its values lands against the wrong
    row."""
    recent = _rows(("10-K", "2026-04-01"), ("10-K", "2025-04-01"))
    del recent["items"]  # no row in `recent` used it
    page = _rows(("8-K", "2024-04-01"))
    page["items"] = ["2.02"]
    responder.routes[_url_main()] = _main_doc(
        recent,
        [{"name": "p1.json", "filingCount": 1,
          "filingFrom": "2024-04-01", "filingTo": "2024-04-01"}],
    )
    responder.routes[_url_page("p1.json")] = page

    merged = sec.fetch_submissions(CIK)["data"]["filings"]["recent"]

    assert len(merged["items"]) == len(merged["form"]) == 3, (
        f"`items` was not back-filled to the merged length: {merged['items']}"
    )
    assert merged["items"][2] == "2.02", (
        f"the 8-K's item code landed on the wrong row: {merged['items']}"
    )
    assert merged["items"][:2] == [None, None]


def test_short_column_in_an_archive_page_is_padded_to_the_page_length(responder):
    """The tail back-fill: a page whose row count exceeds one of its own
    columns must not shorten that column relative to the others."""
    page = _rows(("10-K", "2024-04-01"), ("10-K", "2023-04-01"))
    page["primaryDocDescription"] = page["primaryDocDescription"][:1]
    responder.routes[_url_main()] = _main_doc(
        _rows(("10-K", "2026-04-01")),
        [{"name": "p1.json", "filingCount": 2,
          "filingFrom": "2023-04-01", "filingTo": "2024-04-01"}],
    )
    responder.routes[_url_page("p1.json")] = page

    merged = sec.fetch_submissions(CIK)["data"]["filings"]["recent"]

    lengths = {k: len(v) for k, v in merged.items()}
    assert set(lengths.values()) == {3}, f"columns diverged: {lengths}"
    assert merged["filingDate"] == ["2026-04-01", "2024-04-01", "2023-04-01"]


def test_files_entry_without_a_name_is_an_error_not_a_silent_skip(responder):
    """An entry naming 1,138 filings but carrying no `name` cannot be fetched.
    Dropping it returns a clean success over a history missing those 1,138
    filings — indistinguishable from a complete one, which is the defect this
    whole change exists to remove."""
    responder.routes[_url_main()] = _main_doc(
        _rows(("10-K", "2026-01-29")),
        [{"filingCount": 1138, "filingFrom": "2005-01-03", "filingTo": "2017-02-02"}],
    )

    out = sec.fetch_submissions(CIK)

    assert "error" in out, (
        f"an unfetchable `files[]` entry must surface as an error, got {out}"
    )


def test_limit_selects_the_newest_filings_across_a_page_boundary(responder):
    """`list_filings` with `limit` alone stops at the FIRST `limit` matching
    rows in array order, and its docstring deliberately refuses to assume the
    arrays are date-descending. Post-merge, "first N" equals "newest N" only
    while SEC lists `files[]` newest-archive-first — verified across 28 of 28
    paginated filers on 2026-07-27. Pinning it here means a change in that
    external property fails a test instead of silently returning a filing from
    a decade earlier."""
    responder.routes[_url_main()] = _main_doc(
        _rows(("10-K", "2026-03-01")),
        [
            {"name": "newer.json", "filingCount": 2,
             "filingFrom": "2024-03-01", "filingTo": "2025-03-01"},
            {"name": "older.json", "filingCount": 2,
             "filingFrom": "2015-03-01", "filingTo": "2016-03-01"},
        ],
    )
    responder.routes[_url_page("newer.json")] = _rows(
        ("10-K", "2025-03-01"), ("10-K", "2024-03-01"),
    )
    responder.routes[_url_page("older.json")] = _rows(
        ("10-K", "2016-03-01"), ("10-K", "2015-03-01"),
    )

    rows = sec.list_filings(CIK, ["10-K"], 3)

    assert [r["filingDate"] for r in rows] == [
        "2026-03-01", "2025-03-01", "2024-03-01",
    ], f"`limit` did not take the newest three across the page boundary: {rows}"


def test_cache_bust_clears_the_merged_entry_and_every_archive_page(responder):
    """The CLI's `--no-cache` is the one lever an operator has to re-verify a
    filer against SEC. It unlinked `submissions_{cik}` — the key nothing reads
    any more — while the merged entry and the 7-day archive pages survived, so
    the flag reported a bust and then served the warm cache."""
    page_name = f"CIK{CIK:010d}-submissions-001.json"
    responder.routes[_url_main()] = _main_doc(
        _rows(("10-K", "2026-01-29")),
        [{"name": page_name, "filingCount": 1,
          "filingFrom": "2025-01-31", "filingTo": "2025-01-31"}],
    )
    responder.routes[_url_page(page_name)] = _rows(("10-K", "2025-01-31"))

    sec.fetch_submissions(CIK)
    merged_path = cache_util.cache_path("sec_edgar", f"submissions_full_{CIK:010d}")
    assert merged_path.exists()

    sec.bust_cik_caches(CIK)

    assert not merged_path.exists(), "the merged submissions entry survived the bust"
    survivors = list(merged_path.parent.glob("submissions_page_*"))
    assert survivors == [], f"archive pages survived the bust: {survivors}"


# ---------------------------------------------------------------------------
# 9. `--no-cache` REPORTS what it removed.
#
# `bust_cik_caches` is tested directly above, one layer below the CLI. These
# drive `main()` itself, because the reported count is a user-facing guarantee
# in the CHANGELOG and the two `_log` calls that make it true were deletable
# with the whole suite staying green.
# ---------------------------------------------------------------------------

def _run_main(monkeypatch, argv, ticker_map):
    """Drive `main()` for its `--no-cache` block only, then stop before the
    action runs. `--action cik` is the cheapest required action; `action_cik`
    is stubbed so nothing reaches the network, and `SystemExit` is expected
    because `main()` always exits after printing its result."""
    monkeypatch.setattr(sec, "load_ticker_map", lambda: ticker_map)
    monkeypatch.setattr(sec, "action_cik", lambda t: {"ticker": t, "cik": CIK})
    monkeypatch.setattr(sys, "argv", ["sec_edgar_client.py", *argv])
    monkeypatch.setattr(sec, "_QUIET", False)
    with pytest.raises(SystemExit):
        sec.main()


def test_no_cache_reports_how_many_entries_it_removed(
    monkeypatch, capsys, responder
):
    """The count is the whole point: without it an operator cannot tell a bust
    that cleared 70 files from one that cleared nothing."""
    page_name = f"CIK{CIK:010d}-submissions-001.json"
    responder.routes[_url_main()] = _main_doc(
        _rows(("10-K", "2026-01-29")),
        [{"name": page_name, "filingCount": 1,
          "filingFrom": "2025-01-31", "filingTo": "2025-01-31"}],
    )
    responder.routes[_url_page(page_name)] = _rows(("10-K", "2025-01-31"))
    sec.fetch_submissions(CIK)  # warm: 1 merged entry + 1 archive page

    _run_main(
        monkeypatch,
        ["--action", "cik", "--ticker", "META", "--no-cache"],
        {"tickers": {"META": {"cik": CIK}}},
    )

    assert "2 entries removed" in capsys.readouterr().err


def test_no_cache_reports_zero_when_the_ticker_does_not_resolve(
    monkeypatch, capsys
):
    """A bust that silently does nothing is indistinguishable from one that
    worked — the failure this flag exists to rule out."""
    _run_main(
        monkeypatch,
        ["--action", "cik", "--ticker", "NOSUCH", "--no-cache"],
        {"tickers": {}},
    )

    err = capsys.readouterr().err
    assert "0 entries removed" in err
    assert "not resolved" in err


def test_no_cache_names_an_unreadable_ticker_map_as_the_cause(
    monkeypatch, capsys
):
    """`load_ticker_map` failing is NOT an unknown ticker — reporting it as one
    points the operator at their own input instead of at SEC."""
    _run_main(
        monkeypatch,
        ["--action", "cik", "--ticker", "META", "--no-cache"],
        {"error": "SEC EDGAR HTTP 503: company_tickers.json"},
    )

    err = capsys.readouterr().err
    assert "0 entries removed" in err
    assert "ticker map unavailable" in err
    assert "503" in err


def test_no_cache_also_reports_the_accession_branch(monkeypatch, capsys):
    """The block comment legislates "the count is REPORTED rather than
    assumed" for the whole `--no-cache` block, and the `--accession` branch
    lives under it. Silence there would exempt the branch its own governing
    comment covers."""
    accession = "0001045810-24-000316"
    path = cache_util.cache_path("sec_edgar", f"narrative_sections_{accession}")
    path.parent.mkdir(parents=True, exist_ok=True)
    cache_util.save_cache(path, {"sections": {}})

    monkeypatch.setattr(sec, "action_narrative", lambda a: {"accession": a})
    monkeypatch.setattr(sec, "load_ticker_map", lambda: {"tickers": {}})
    monkeypatch.setattr(
        sys, "argv",
        ["sec_edgar_client.py", "--action", "narrative",
         "--accession", accession, "--no-cache"],
    )
    monkeypatch.setattr(sec, "_QUIET", False)
    with pytest.raises(SystemExit):
        sec.main()

    err = capsys.readouterr().err
    assert f"{accession}: 1 entries removed" in err
    assert not path.exists()


def test_main_document_error_still_propagates_uncached(responder):
    responder.routes[_url_main()] = {"error": "SEC EDGAR 404: nope"}

    out = sec.fetch_submissions(CIK)

    assert out == {"error": "SEC EDGAR 404: nope"}
