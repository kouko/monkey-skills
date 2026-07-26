"""test_data_markets_us.py — Task 3a migration contract.

Verifies the US client + pack-builder migration into
skills/data-markets/scripts/:

  (a) migrated client files (yfinance_client.py, fred_client.py,
      sec_edgar_client.py) define no local cache-helper boilerplate
      (_CACHE_BASE / CACHE_DIR / CACHE_TTL_* constants,
      get_cache_path / load_cache / save_cache or underscore-variant
      defs) — source-scan check, no execution — and `import cache_util`.
  (b) pack_us.build_pack("snapshot", ["AAPL"]) produces a dict whose
      top-level section keys match the current data-us fixture sample
      (fixture-fed / mocked subprocess — offline, no network).
  (c) pack_us.SUPPORTED_PACKS matches data-us/scripts/pack.py's current
      --pack choices.

Offline: no network calls. The subprocess boundary (run_client) is
mocked in test (b).
"""
from __future__ import annotations

import datetime as _dt
import json
import re
import sys
from pathlib import Path
from unittest import mock

import pytest

ROOT = Path(__file__).resolve().parents[2]
MARKETS_SCRIPTS = ROOT / "skills" / "data-markets" / "scripts"
FIXTURES = ROOT / "tests" / "data" / "fixtures"


@pytest.fixture(autouse=True)
def _stub_requests_for_sec_edgar_client(monkeypatch):
    """pack_us.pack_memo_fetch lazily imports
    sec_edgar_client.select_narrative_filings (a pure function) to decide
    which filings the narrative fetch covers. Offline CI installs
    pytest+pyyaml ONLY, so sec_edgar_client's top-level `import requests`
    would fail without a stub — breaking every test in this file that
    reaches pack_memo_fetch (mirrors test_sec_narrative.py's `sec_client`
    fixture; only `requests` is stubbed here, not `edgar`, because
    select_narrative_filings is a pure function that never reaches the
    edgartools boundary)."""
    if "requests" not in sys.modules:
        monkeypatch.setitem(sys.modules, "requests", mock.MagicMock(name="requests"))


@pytest.fixture(autouse=True)
def _stub_xval_producers_for_memo_fetch(monkeypatch):
    """Task 3: `pack_memo_fetch` now unconditionally calls
    `_fetch_xval_source_a` (which reaches edgartools' real `import edgar`,
    unlike the pure `select_narrative_filings` the fixture above already
    covers) and `build_companyfacts_pack` (a real SEC companyfacts fetch)
    for every memo-fetch. Tests in this file that exercise `pack_memo_fetch`
    but don't assert on xval (the pre-Task-3 narrative/DCF tests) must not
    crash on `ModuleNotFoundError: edgar` or attempt a real network call.

    Stubs at the PRODUCER'S OWN boundary (`sec_edgar_client._acquire_raw_filing`
    / `sec_edgar_client.build_companyfacts_pack`), not `pack_us._fetch_xval_source_a`
    itself -- Task 2's own direct-call tests
    (`test_fetch_xval_source_a_wraps_cells_envelope`,
    `test_fetch_xval_source_a_no_10k_is_wholesale_failure_not_crash`) exercise
    that real function's own logic and would break if this fixture shadowed
    it wholesale. Stubbing `_acquire_raw_filing` with a resolution-error slot
    lets `_fetch_xval_source_a`'s REAL implementation run unmodified, naturally
    producing its own already-tested wholesale-failure shape (harmless for
    tests that don't assert on it); `build_companyfacts_pack` has no direct
    unit test in THIS file (its own is in test_sec_xval.py), so stubbing it
    outright is safe. Tests that DO assert on xval
    (`test_pack_memo_fetch_emits_xval_packs_with_status`,
    `test_us_migration_memo_fetch_section_keys`) override this default with
    their own narrower `mock.patch.object` for the scope of their own `with`
    block."""
    if str(MARKETS_SCRIPTS) not in sys.path:
        sys.path.insert(0, str(MARKETS_SCRIPTS))
    import sec_edgar_client  # noqa: E402

    monkeypatch.setattr(
        sec_edgar_client, "_acquire_raw_filing",
        lambda accession: {
            "error": f"SEC EDGAR filing acquisition failed: accession {accession!r} did not resolve to a filing",
            "error_class": "resolution",
        },
    )
    monkeypatch.setattr(
        sec_edgar_client, "build_companyfacts_pack",
        lambda cik: {"cik": cik, "facts": {}},
    )

CLIENT_FILES = ["yfinance_client.py", "fred_client.py", "sec_edgar_client.py"]

# Local cache boilerplate being deleted per Task 3a — module-level
# constants and function definitions, matched at line start (so a mention
# inside a comment/docstring sentence doesn't false-positive, but an
# actual definition/assignment does).
_LOCAL_CACHE_HELPER_PATTERNS = [
    r"^_CACHE_BASE\s*=",
    r"^CACHE_DIR\s*=",
    r"^CACHE_TTL_\w*\s*=",
    r"^\s*def get_cache_path\(",
    r"^\s*def load_cache\(",
    r"^\s*def save_cache\(",
    r"^\s*def _load_cache\(",
    r"^\s*def _save_cache\(",
    r"^\s*def _cache_path\(",
]


def test_us_migration_contract():
    # --- (a) migrated clients: no local cache boilerplate, cache_util imported ---
    for fname in CLIENT_FILES:
        path = MARKETS_SCRIPTS / fname
        assert path.exists(), f"missing migrated client: {fname}"
        text = path.read_text()

        for pattern in _LOCAL_CACHE_HELPER_PATTERNS:
            assert not re.search(pattern, text, re.MULTILINE), (
                f"{fname} still defines local cache boilerplate matching {pattern!r}"
            )

        assert re.search(r"^import cache_util\s*$", text, re.MULTILINE), (
            f"{fname} does not `import cache_util`"
        )

    pack_us_path = MARKETS_SCRIPTS / "pack_us.py"
    assert pack_us_path.exists(), "missing pack_us.py"

    if str(MARKETS_SCRIPTS) not in sys.path:
        sys.path.insert(0, str(MARKETS_SCRIPTS))
    import pack_us  # noqa: E402  (path-dependent import, must follow sys.path insert)

    # --- (c) SUPPORTED_PACKS matches data-us/scripts/pack.py's current --pack choices ---
    # Exact-equality, not a prefix check: the migration contract is that no
    # historical data-us pack was dropped, renamed, or reordered, AND that
    # any pack added after the consolidation (kpi-quarterly, 2026-07-18
    # memo-quarterly-kpi-wiring Task 1) is deliberately registered here in
    # its exact position. A future unregistered addition or reorder must
    # fail this assertion.
    assert pack_us.SUPPORTED_PACKS == (
        "snapshot", "memo-fetch", "comps-multiples", "screener-batch", "regime-pack",
        "kpi-quarterly", "kpi-topline-backfill", "statement-backfill", "reconstruct",
    ), f"SUPPORTED_PACKS diverges from data-us pack.py --pack choices: {pack_us.SUPPORTED_PACKS}"

    # --- (b) build_pack("snapshot", ...) section keys match fixture (fixture-fed, mocked subprocess) ---
    fixture = json.loads((FIXTURES / "data-us-snapshot-sample.json").read_text())
    expected_keys = set(fixture.keys())

    with mock.patch.object(pack_us, "run_client") as mock_run_client:
        mock_run_client.side_effect = [
            fixture["company_info"],
            fixture["price_history"],
        ]
        result = pack_us.build_pack("snapshot", ["AAPL"])

    assert mock_run_client.call_count == 2, (
        "pack_snapshot should shell out exactly twice (info, history) via run_client"
    )
    assert set(result.keys()) == expected_keys, (
        f"pack_us snapshot section keys diverge from data-us fixture: "
        f"missing={expected_keys - set(result.keys())} "
        f"extra={set(result.keys()) - expected_keys}"
    )
    assert result["ticker"] == "AAPL"
    assert result["company_info"] == fixture["company_info"]
    assert result["price_history"] == fixture["price_history"]


def _mock_run_client_for_memo_fetch(fixture: dict):
    """Route mocked run_client calls to fixture sections by script + args,
    so pack_memo_fetch's ~40 DCF-concept sub-calls (one per XBRL concept in
    DCF_CONCEPT_MAPPING) don't need individually-ordered side_effect entries.
    Concept-fetch calls return {} (no `observations`) — pack_us._fetch_dcf_concepts
    drops those, so income_statement/cash_flow/balance_sheet still assemble
    (as empty-series dicts) without asserting on their inner values here.
    """
    import pack_us  # noqa: E402  (module under test, already on sys.path)

    # accession -> producer-shaped narrative result, keyed from the fixture's
    # own sec_narrative.filings entries (each already carries "accession").
    narrative_by_accession = {
        entry["accession"]: entry
        for entry in fixture.get("sec_narrative", {}).get("filings", [])
        if "accession" in entry
    }

    def _side_effect(script, extra_args, timeout=pack_us.CLIENT_TIMEOUT_SECONDS):
        if script == pack_us.YF:
            if "info" in extra_args:
                return fixture["company_info"]
            return fixture["price_history"]
        if script == pack_us.SEC:
            if "filings" in extra_args:
                return fixture["sec_filings"]
            if "--concept" in extra_args:
                return {}
            if "narrative" in extra_args:
                accession = extra_args[extra_args.index("--accession") + 1]
                return narrative_by_accession.get(accession, {
                    "error": f"no fixture narrative entry for accession {accession!r}",
                })
            return fixture["sec_facts"]
        raise AssertionError(f"unexpected run_client script: {script}")

    return _side_effect


def test_us_migration_memo_fetch_section_keys():
    """pack_us.build_pack("memo-fetch", ...) top-level section keys match
    the data-us memo-fetch fixture (fixture-fed / mocked subprocess —
    offline, no network). Separate from the snapshot test above for
    F.I.R.S.T independence (one pack type's assertion failing must not
    hide the other's).

    Task 3 added two new top-level keys (`xval_source_a`/`xval_source_b`)
    not present in the pre-Task-3 fixture -- added to `expected_keys`
    directly rather than editing the fixture (out of this task's file
    scope). Their own producers (`_fetch_xval_source_a` /
    `build_companyfacts_pack`) are mocked here too, so this section-keys
    test never reaches the real edgartools/companyfacts network boundary
    those two producers touch."""
    if str(MARKETS_SCRIPTS) not in sys.path:
        sys.path.insert(0, str(MARKETS_SCRIPTS))
    import pack_us  # noqa: E402  (path-dependent import, must follow sys.path insert)
    import sec_edgar_client  # noqa: E402

    fixture = json.loads((FIXTURES / "data-us-memo-fetch-sample.json").read_text())
    expected_keys = set(fixture.keys()) | {"xval_source_a", "xval_source_b"}

    with mock.patch.object(pack_us, "run_client") as mock_run_client, mock.patch.object(
        pack_us, "_fetch_xval_source_a",
        return_value={
            "statements": [], "failed_items": [], "requested": 4,
            "succeeded": 4, "failed": 0, "_status": "ok",
        },
    ), mock.patch.object(
        sec_edgar_client, "build_companyfacts_pack",
        return_value={"cik": 320193, "facts": {}},
    ):
        mock_run_client.side_effect = _mock_run_client_for_memo_fetch(fixture)
        result = pack_us.build_pack("memo-fetch", ["AAPL"])

    assert set(result.keys()) == expected_keys, (
        f"pack_us memo-fetch section keys diverge from data-us fixture: "
        f"missing={expected_keys - set(result.keys())} "
        f"extra={set(result.keys()) - expected_keys}"
    )
    assert result["ticker"] == "AAPL"
    assert result["company_info"] == fixture["company_info"]
    assert result["sec_filings"] == fixture["sec_filings"]


# ---------------------------------------------------------------------------
# Task 3 — pack_memo_fetch wires the SEC narrative into a top-level
# `sec_narrative` key (brief §Decision memo-feed contract).
# ---------------------------------------------------------------------------

def _quarter_of(d: _dt.date) -> tuple[int, int]:
    return (d.year, (d.month - 1) // 3 + 1)


def _shift_quarter(year_quarter: tuple[int, int], n: int) -> tuple[int, int]:
    year, q = year_quarter
    total = year * 4 + (q - 1) - n
    return (total // 4, total % 4 + 1)


def _date_in_quarter(year_quarter: tuple[int, int]) -> str:
    year, q = year_quarter
    month = (q - 1) * 3 + 1
    return _dt.date(year, month, 15).isoformat()


def _synthetic_narrative_filings_rows() -> list[dict]:
    """Filings rows (Task 1 shape: `items` + `reportDate`) covering exactly
    what `select_narrative_filings` needs to pick 6/6 with zero gaps: a
    10-K, a 10-Q, and one item-2.02 earnings 8-K per quarter for the last 4
    quarters. Computed off *today* (mirroring `select_narrative_filings`'s
    own `as_of` default, which `pack_memo_fetch` does not override) so this
    test never goes stale."""
    today = _dt.date.today()
    rows = [
        {
            "form": "10-K", "filingDate": today.isoformat(),
            "accessionNumber": "0000320193-26-100001",
            "primaryDocument": "10k.htm", "primaryDocDescription": "10-K",
            "items": "", "reportDate": today.isoformat(),
        },
        {
            "form": "10-Q", "filingDate": today.isoformat(),
            "accessionNumber": "0000320193-26-100002",
            "primaryDocument": "10q.htm", "primaryDocDescription": "10-Q",
            "items": "", "reportDate": today.isoformat(),
        },
    ]
    anchor_yq = _quarter_of(today)
    for n in range(4):
        yq = _shift_quarter(anchor_yq, n)
        rows.append({
            "form": "8-K",
            "filingDate": _date_in_quarter(yq),
            "accessionNumber": f"0000320193-26-20000{n}",
            "primaryDocument": f"8k-{n}.htm",
            "primaryDocDescription": "8-K",
            "items": "2.02,9.01",
            "reportDate": _date_in_quarter(yq),
        })
    return rows


def _producer_narrative(accession: str, *, status: str = "ok", failed_item: str | None = None) -> dict:
    """A producer-shaped `--action narrative` result — mirrors
    sec_edgar_client.fetch_narrative_sections's real emission
    (sec_edgar_client.py:1417-1435): accession/cik/form/filingDate/
    sections/section_count/narrative_status/failed_items/_cache."""
    sections = [{
        "item": "Item 1",
        "text_path": f"/tmp/sections/{accession}/Item_1.txt",
        "disclosure_status": "filed",
        "accession": accession,
        "cik": 320193,
        "filingDate": "2026-05-01",
        "period_of_report": None,
        "url": f"https://www.sec.gov/Archives/edgar/data/320193/{accession}/10k.htm",
    }]
    failed_items: list[str] = []
    if status == "partial" and failed_item:
        sections.append({
            "item": failed_item,
            "error": f"section {failed_item!r} extraction failed for filing {accession!r}",
            "error_class": "extraction_error",
        })
        failed_items = [failed_item]
    return {
        "accession": accession, "cik": 320193, "form": "10-K",
        "filingDate": "2026-05-01", "sections": sections,
        "section_count": len(sections), "narrative_status": status,
        "failed_items": failed_items, "_cache": "miss", "action": "narrative",
    }


def _mock_run_client_for_narrative(filings_rows: list[dict], narrative_by_index: dict | None = None):
    """run_client side_effect for the sec_narrative tests: YF calls return
    `{}` (untested here), the filings call returns `filings_rows`, and each
    `--action narrative` call returns a producer-shaped result.
    `narrative_by_index` maps the Nth narrative call (0-indexed, in
    selection order — 10-K, 10-Q, then one 8-K per quarter n=0..3, per
    `select_narrative_filings`'s own construction order) to an
    `(status, failed_item)` pair; unlisted calls default to "ok"."""
    import pack_us  # noqa: E402  (module under test, already on sys.path)

    narrative_by_index = narrative_by_index or {}
    call_count = {"n": 0}

    def _side_effect(script, extra_args, timeout=pack_us.CLIENT_TIMEOUT_SECONDS):
        if script == pack_us.YF:
            return {}
        if script == pack_us.SEC:
            if "filings" in extra_args:
                return {"filings": filings_rows}
            if "--concept" in extra_args:
                return {}
            if "narrative" in extra_args:
                accession = extra_args[extra_args.index("--accession") + 1]
                idx = call_count["n"]
                call_count["n"] += 1
                status, failed_item = narrative_by_index.get(idx, ("ok", None))
                return _producer_narrative(accession, status=status, failed_item=failed_item)
            return {}
        raise AssertionError(f"unexpected run_client script: {script}")

    return _side_effect


def test_pack_memo_fetch_filings_call_uses_policy_derived_window_not_count_limit():
    """Task 8 (post-live-anchor defect fix): the live-observed false gap
    (2026-07-13, real AAPL run) traced to this exact call site fetching
    filings with `--limit 8` -- a row-COUNT window applied across ALL forms
    combined, so 8-K/10-Q volume could crowd the once-a-year 10-K out
    entirely. Fixed by switching to a policy-derived `--since-days` DATE
    window (`sec_edgar_client.narrative_filings_window_days`) -- a count
    argument must never reach this call again."""
    if str(MARKETS_SCRIPTS) not in sys.path:
        sys.path.insert(0, str(MARKETS_SCRIPTS))
    import pack_us  # noqa: E402
    import sec_edgar_client  # noqa: E402  (pure window function; no edgar/requests call)

    filings_rows = _synthetic_narrative_filings_rows()
    captured_args = {}

    def _side_effect(script, extra_args, timeout=pack_us.CLIENT_TIMEOUT_SECONDS):
        if script == pack_us.YF:
            return {}
        if script == pack_us.SEC:
            if "filings" in extra_args:
                captured_args["filings"] = list(extra_args)
                return {"filings": filings_rows}
            if "--concept" in extra_args:
                return {}
            if "narrative" in extra_args:
                accession = extra_args[extra_args.index("--accession") + 1]
                return _producer_narrative(accession)
            return {}
        raise AssertionError(f"unexpected run_client script: {script}")

    with mock.patch.object(pack_us, "run_client") as mock_run_client:
        mock_run_client.side_effect = _side_effect
        pack_us.build_pack("memo-fetch", ["AAPL"])

    args = captured_args["filings"]
    assert "--limit" not in args, f"filings fetch must not be a count window: {args}"
    assert "--since-days" in args, f"filings fetch must be a date window: {args}"
    since_days = int(args[args.index("--since-days") + 1])
    assert since_days == sec_edgar_client.narrative_filings_window_days(), (
        f"since-days must be the policy-derived window, got {since_days}"
    )


def test_memo_fetch_emits_sec_narrative_with_counts():
    """pack_memo_fetch wires Task 2's selection + one `--action narrative`
    subprocess per selected accession into a new top-level `sec_narrative`
    key: requested is fixed by the policy (2 + 4 quarters = 6), succeeded +
    failed reconciles to requested, failed_items is a top-level list, and
    _status is "ok" when every selected filing narrates cleanly."""
    if str(MARKETS_SCRIPTS) not in sys.path:
        sys.path.insert(0, str(MARKETS_SCRIPTS))
    import pack_us  # noqa: E402

    filings_rows = _synthetic_narrative_filings_rows()

    with mock.patch.object(pack_us, "run_client") as mock_run_client:
        mock_run_client.side_effect = _mock_run_client_for_narrative(filings_rows)
        result = pack_us.build_pack("memo-fetch", ["AAPL"])

    assert "sec_narrative" in result, "pack_memo_fetch did not emit sec_narrative"
    sec_narrative = result["sec_narrative"]
    assert sec_narrative["requested"] == 6
    assert sec_narrative["succeeded"] + sec_narrative["failed"] == sec_narrative["requested"]
    assert isinstance(sec_narrative["failed_items"], list)
    assert sec_narrative["failed_items"] == []
    assert sec_narrative["_status"] == "ok"
    assert len(sec_narrative["filings"]) == 6


def test_memo_fetch_sec_narrative_partial_status_visible_at_depth_1():
    """A selected filing's producer result carrying narrative_status=
    "partial" must (a) flip the wrapper's own _status to "partial" and
    (b) surface that filing's failed item ids in the wrapper's TOP-LEVEL
    failed_items — readable without walking into any nested `sections`
    list (brief Fork A: a status string alone is the documented
    ignored-by-structural-readers failure mode)."""
    if str(MARKETS_SCRIPTS) not in sys.path:
        sys.path.insert(0, str(MARKETS_SCRIPTS))
    import pack_us  # noqa: E402

    filings_rows = _synthetic_narrative_filings_rows()

    with mock.patch.object(pack_us, "run_client") as mock_run_client:
        mock_run_client.side_effect = _mock_run_client_for_narrative(
            filings_rows, narrative_by_index={2: ("partial", "Item 1A")}
        )
        result = pack_us.build_pack("memo-fetch", ["AAPL"])

    sec_narrative = result["sec_narrative"]
    assert sec_narrative["_status"] == "partial"
    assert any(entry.get("item") == "Item 1A" for entry in sec_narrative["failed_items"]), (
        f"failed item not hoisted to depth 1: {sec_narrative['failed_items']}"
    )


def test_memo_fetch_partial_sec_narrative_classifies_whole_pack_partial():
    """End-to-end proof the seam actually works: pack.py's own
    `_classify_result` (Task 4's self-declared-`_status` reader) reports
    the whole pack as partial when sec_narrative degrades — not just that
    the field exists, but that the real structural reader honors it.

    Also pins the depth-1 hoisting itself (not just the derived `_status`
    flag): `_status` alone can go "partial" via `any_partial` even if the
    hoisting loop that populates top-level `failed_items` is deleted, so a
    status-only assertion here would pass under that mutation and prove
    nothing about hoisting. Asserting the hoisted item is present makes
    that mutation fail this test.
    """
    if str(MARKETS_SCRIPTS) not in sys.path:
        sys.path.insert(0, str(MARKETS_SCRIPTS))
    import pack  # noqa: E402
    import pack_us  # noqa: E402

    filings_rows = _synthetic_narrative_filings_rows()

    with mock.patch.object(pack_us, "run_client") as mock_run_client:
        mock_run_client.side_effect = _mock_run_client_for_narrative(
            filings_rows, narrative_by_index={2: ("partial", "Item 1A")}
        )
        result = pack_us.build_pack("memo-fetch", ["AAPL"])

    status, failed_sections = pack._classify_result(result)
    assert status == "partial"
    assert "sec_narrative" in failed_sections

    sec_narrative = result["sec_narrative"]
    assert sec_narrative["failed_items"], (
        "top-level failed_items is empty — the depth-1 hoisting loop that "
        "populates it from a partial filing's own failed_items appears to "
        "have been removed"
    )
    assert any(entry.get("item") == "Item 1A" for entry in sec_narrative["failed_items"]), (
        f"expected the partial filing's failed item 'Item 1A' hoisted to "
        f"depth 1: {sec_narrative['failed_items']}"
    )


def test_us_specific_drops_stale_non_gaap_note():
    """Task 6: `us_specific.non_gaap_eps_note` claimed the non-GAAP EPS gap
    "lives in 8-K narratives" -- true only while the pack had no 8-K
    narrative. Task 3 wired sec_narrative in, so the note is now a stale
    pointer at a gap that no longer exists and must be removed.
    `segment_revenue_note` describes a genuinely still-open gap (XBRL
    segment revenue is NOT wired by this branch) and must survive --
    the guard that this removal did not overreach."""
    if str(MARKETS_SCRIPTS) not in sys.path:
        sys.path.insert(0, str(MARKETS_SCRIPTS))
    import pack_us  # noqa: E402

    filings_rows = _synthetic_narrative_filings_rows()

    with mock.patch.object(pack_us, "run_client") as mock_run_client:
        mock_run_client.side_effect = _mock_run_client_for_narrative(filings_rows)
        result = pack_us.build_pack("memo-fetch", ["AAPL"])

    us_specific = result["us_specific"]
    assert "non_gaap_eps_note" not in us_specific, (
        "non_gaap_eps_note is stale now that sec_narrative is wired in"
    )
    assert "segment_revenue_note" in us_specific, (
        "segment_revenue_note describes a still-open gap and must survive"
    )


def test_fetch_sec_narrative_empty_selection_is_not_vacuously_failed():
    """`failed == requested` is vacuously true when `requested == 0` (an
    empty selection: nothing requested, nothing failed) — that must NOT
    read as `_status: "failed"`. select_narrative_filings never actually
    returns requested=0 through today's fixed `2 + n_quarters` policy, but
    _fetch_sec_narrative must not rely on that invariant holding forever."""
    if str(MARKETS_SCRIPTS) not in sys.path:
        sys.path.insert(0, str(MARKETS_SCRIPTS))
    import pack_us  # noqa: E402
    import sec_edgar_client  # noqa: E402

    with mock.patch.object(
        sec_edgar_client, "select_narrative_filings",
        return_value={"selected": [], "gaps": [], "requested": 0},
    ):
        result = pack_us._fetch_sec_narrative([])

    assert result["requested"] == 0
    assert result["failed"] == 0
    assert result["_status"] == "ok", (
        f"empty selection (requested=0) must not read as failed: {result}"
    )


def test_fetch_xval_source_a_wraps_cells_envelope():
    """Task 2: `_fetch_xval_source_a` selects the latest 10-K accession from
    `sec_filings` rows, acquires it, and calls `extract_statement_cells` per
    primary statement. `extract_statement_cells` returns a BARE cell list on
    success -- this must be WRAPPED into the Source-A envelope
    {accession, statement_name, cells} per statement, never passed through
    bare. A statement whose extraction returns an error dict (StatementNotFound
    surfaces this way, sec_edgar_client.py:1645) is a loud per-statement skip
    recorded in the depth-1 status -- never a crash, never a fabricated
    cells entry."""
    if str(MARKETS_SCRIPTS) not in sys.path:
        sys.path.insert(0, str(MARKETS_SCRIPTS))
    import pack_us  # noqa: E402
    import sec_edgar_client  # noqa: E402

    filings_rows = _synthetic_narrative_filings_rows()
    latest_10k_accession = "0000320193-26-100001"  # the 10-K row above

    bare_cells = [{"concept": "Revenues", "numeric_value": 100.0}]
    stub_filing = mock.MagicMock(name="filing")

    def _extract_side_effect(filing, statement_name):
        assert filing is stub_filing, "extract_statement_cells must receive the acquired filing"
        if statement_name == "IncomeStatement":
            return {
                "statement_name": statement_name,
                "error": f"statement {statement_name!r} extraction failed: StatementNotFound",
                "error_class": "statement_not_found",
            }
        return list(bare_cells)

    with mock.patch.object(
        sec_edgar_client, "_acquire_raw_filing", return_value=stub_filing
    ) as mock_acquire, mock.patch.object(
        sec_edgar_client, "extract_statement_cells", side_effect=_extract_side_effect
    ):
        result = pack_us._fetch_xval_source_a(filings_rows)

    mock_acquire.assert_called_once_with(latest_10k_accession)

    balance_entry = next(
        s for s in result["statements"] if s["statement_name"] == "BalanceSheet"
    )
    assert balance_entry == {
        "accession": latest_10k_accession,
        "statement_name": "BalanceSheet",
        "cells": bare_cells,
    }, f"bare cell list must be WRAPPED into the envelope, not passed through: {balance_entry}"

    assert result["requested"] == len(pack_us.XVAL_PRIMARY_STATEMENTS)
    assert result["succeeded"] + result["failed"] == result["requested"]
    assert any(
        item.get("statement_name") == "IncomeStatement"
        and item.get("error_class") == "statement_not_found"
        for item in result["failed_items"]
    ), f"IncomeStatement failure not recorded as a loud per-statement skip: {result['failed_items']}"
    assert not any(s["statement_name"] == "IncomeStatement" for s in result["statements"]), (
        "a failed statement must never appear as a fabricated cells entry"
    )
    assert result["_status"] == "partial", (
        "one failed statement among several succeeding must read as partial, not ok/failed"
    )


def test_latest_10k_accession_multi_10k_tiebreak_by_filing_date():
    """`_latest_10k_accession` must select the LATEST-FILED 10-K's
    accession when `filings_rows` carries more than one 10-K (e.g. a
    restated/amended-year overlap) -- max by `filingDate`, not first- or
    last-in-list order."""
    if str(MARKETS_SCRIPTS) not in sys.path:
        sys.path.insert(0, str(MARKETS_SCRIPTS))
    import pack_us  # noqa: E402

    rows = [
        {"form": "10-K", "filingDate": "2024-10-25", "accessionNumber": "0000320193-24-000123"},
        {"form": "10-K", "filingDate": "2025-10-31", "accessionNumber": "0000320193-25-000079"},
        {"form": "10-K", "filingDate": "2023-10-27", "accessionNumber": "0000320193-23-000106"},
        {"form": "10-Q", "filingDate": "2026-01-30", "accessionNumber": "0000320193-26-000001"},
    ]

    assert pack_us._latest_10k_accession(rows) == "0000320193-25-000079", (
        "must pick the latest-filed 10-K by filingDate, not list order"
    )


def test_fetch_xval_source_a_no_10k_is_wholesale_failure_not_crash():
    """When `filings_rows` has NO 10-K row, `_latest_10k_accession` returns
    None -- `_acquire_raw_filing(None)` still returns a loud resolution-error
    slot (never a crash, sec_edgar_client.py:906-911), and `_fetch_xval_source_a`
    must read that as a WHOLESALE failure (`_status: "failed"`, every
    statement recorded in `failed_items`) -- never a vacuous/silent success
    with an empty `statements` list passed off as `_status: "ok"`."""
    if str(MARKETS_SCRIPTS) not in sys.path:
        sys.path.insert(0, str(MARKETS_SCRIPTS))
    import pack_us  # noqa: E402
    import sec_edgar_client  # noqa: E402

    filings_rows = [
        {"form": "10-Q", "filingDate": "2026-01-30", "accessionNumber": "0000320193-26-000001"},
        {"form": "8-K", "filingDate": "2026-02-02", "accessionNumber": "0000320193-26-000002"},
    ]
    acquire_error = {
        "error": "SEC EDGAR filing acquisition failed: accession None did not resolve to a filing",
        "error_class": "resolution",
    }

    with mock.patch.object(
        sec_edgar_client, "_acquire_raw_filing", return_value=acquire_error
    ) as mock_acquire:
        result = pack_us._fetch_xval_source_a(filings_rows)

    mock_acquire.assert_called_once_with(None)
    assert result["statements"] == [], "no 10-K acquired must never fabricate a statements entry"
    assert result["requested"] == len(pack_us.XVAL_PRIMARY_STATEMENTS)
    assert result["succeeded"] == 0
    assert result["failed"] == result["requested"]
    assert len(result["failed_items"]) == result["requested"], (
        "every primary statement must be recorded as a failed_items entry, one per statement"
    )
    assert all(item.get("error_class") == "resolution" for item in result["failed_items"])
    assert result["_status"] == "failed", (
        "no 10-K resolved must read as a wholesale failure, not a vacuous ok/partial"
    )


# ---------------------------------------------------------------------------
# Task 3 — pack_memo_fetch wires xval_source_a (Task 2) + xval_source_b
# (Task 1's build_companyfacts_pack) into two new top-level keys, each
# carrying a depth-1 `_status` envelope.
# ---------------------------------------------------------------------------

def _run_client_for_xval_wiring(filings_rows: list[dict], *, cik: int = 320193):
    """run_client side_effect for the Task 3 wiring test: YF calls return
    `{}` (untested here), the filings call returns `filings_rows`, DCF
    `--concept` calls return `{}`, narrative calls return a producer-shaped
    result, and the plain `--action facts` call (no `--concept`) returns a
    CIK-bearing facts result -- `pack_memo_fetch` reuses this `cik` for
    `xval_source_b` rather than re-resolving it."""
    import pack_us  # noqa: E402  (module under test, already on sys.path)

    def _side_effect(script, extra_args, timeout=pack_us.CLIENT_TIMEOUT_SECONDS):
        if script == pack_us.YF:
            return {}
        if script == pack_us.SEC:
            if "filings" in extra_args:
                return {"filings": filings_rows}
            if "--concept" in extra_args:
                return {}
            if "narrative" in extra_args:
                accession = extra_args[extra_args.index("--accession") + 1]
                return _producer_narrative(accession)
            # plain `--action facts` (no --concept): the CIK-bearing result
            return {"ticker": "AAPL", "cik": cik, "action": "facts"}
        raise AssertionError(f"unexpected run_client script: {script}")

    return _side_effect


def test_pack_memo_fetch_emits_xval_packs_with_status():
    """Task 3: pack_memo_fetch wires `build_companyfacts_pack` (Task 1) +
    `_fetch_xval_source_a` (Task 2) into two new top-level keys,
    `xval_source_a` and `xval_source_b`, each carrying a depth-1 `_status`
    envelope with a `{requested, succeeded, failed}` count-triple --
    mirroring `_fetch_sec_narrative`'s own status discipline (never require
    walking into nested `cells`/`facts` to learn completeness). A mocked
    companyfacts fetch failure must surface as a depth-1 failed `_status`
    on `xval_source_b`, not a silent empty."""
    if str(MARKETS_SCRIPTS) not in sys.path:
        sys.path.insert(0, str(MARKETS_SCRIPTS))
    import pack_us  # noqa: E402
    import sec_edgar_client  # noqa: E402

    filings_rows = _synthetic_narrative_filings_rows()
    xval_source_a_stub = {
        "statements": [{
            "accession": "0000320193-26-100001",
            "statement_name": "BalanceSheet",
            "cells": [],
        }],
        "failed_items": [], "requested": 4, "succeeded": 4, "failed": 0,
        "_status": "ok",
    }
    run_client_side_effect = _run_client_for_xval_wiring(filings_rows)

    # -- success path --
    with mock.patch.object(
        pack_us, "run_client", side_effect=run_client_side_effect
    ), mock.patch.object(
        pack_us, "_fetch_xval_source_a", return_value=dict(xval_source_a_stub)
    ), mock.patch.object(
        sec_edgar_client, "build_companyfacts_pack",
        return_value={"cik": 320193, "facts": {"us-gaap": {"Revenues": []}}},
    ) as mock_build:
        result = pack_us.build_pack("memo-fetch", ["AAPL"])

    mock_build.assert_called_once_with(320193)  # reuse the already-resolved CIK, not re-resolve it

    assert "xval_source_a" in result, "pack_memo_fetch did not emit xval_source_a"
    assert "xval_source_b" in result, "pack_memo_fetch did not emit xval_source_b"

    for section, name in (
        (result["xval_source_a"], "xval_source_a"),
        (result["xval_source_b"], "xval_source_b"),
    ):
        assert "_status" in section, f"{name} missing depth-1 _status"
        assert {"requested", "succeeded", "failed"} <= section.keys(), (
            f"{name} missing depth-1 {{requested, succeeded, failed}} triple: {section}"
        )
        assert section["succeeded"] + section["failed"] == section["requested"]

    assert result["xval_source_b"]["_status"] == "ok"
    assert result["xval_source_b"]["facts"] == {"us-gaap": {"Revenues": []}}

    # -- failure path: companyfacts fetch fails --
    with mock.patch.object(
        pack_us, "run_client", side_effect=run_client_side_effect
    ), mock.patch.object(
        pack_us, "_fetch_xval_source_a", return_value=dict(xval_source_a_stub)
    ), mock.patch.object(
        sec_edgar_client, "build_companyfacts_pack",
        return_value={
            "error": "SEC EDGAR companyfacts fetch failed for CIK 320193: boom",
            "error_class": "companyfacts_fetch_failed",
            "identifier": "320193",
        },
    ):
        failed_result = pack_us.build_pack("memo-fetch", ["AAPL"])

    xval_source_b_failed = failed_result["xval_source_b"]
    assert xval_source_b_failed["_status"] == "failed", (
        f"a companyfacts fetch failure must surface as a depth-1 failed "
        f"_status on xval_source_b, not a silent empty: {xval_source_b_failed}"
    )
    assert xval_source_b_failed["failed"] == xval_source_b_failed["requested"] > 0
    assert "error" in xval_source_b_failed, (
        "depth-1 failed status must carry the error, not swallow it"
    )


def test_statement_backfill_envelope_declares_companyfacts_source_kind(monkeypatch):
    """Task 8, docs/loom/plans/2026-07-26-us-as-reported-statement-lane.md:
    `pack_statement_backfill` is pure I/O orchestration mirroring
    `pack_kpi_topline_backfill` (pack_us.py:1043) -- it calls the producer
    (`sec_edgar_client.build_statement_backfill`) and shapes the return into
    the standard envelope, carrying the mandatory top-level `source_kind`
    literal `"xbrl-companyfacts"` (plan's §PIN — statement pack envelope).
    `kpi_xbrl_ingest.ingest_pack` reads this exact literal to assign the
    correct durable provenance label; without it every point would inherit
    a wrong default. Stubs at the producer's own module boundary
    (`sec_edgar_client.build_statement_backfill`), not an intermediate
    projection -- this repo has a recorded incident where mocking one layer
    up let a green suite certify a crash."""
    if str(MARKETS_SCRIPTS) not in sys.path:
        sys.path.insert(0, str(MARKETS_SCRIPTS))
    import pack_us  # noqa: E402
    import sec_edgar_client  # noqa: E402

    fake_facts = [
        {
            "concept": "us-gaap:Revenues",
            "period_start": "2024-01-01",
            "period_end": "2024-12-31",
            "period_kind": "duration",
            "value": 1234000000.0,
            "unit": "USD",
            "accession": "0000320193-25-000079",
            "filed": "2025-10-31",
            "form": "10-K",
        }
    ]
    fake_coverage = {"skipped_rows": []}
    calls: list[str] = []

    def fake_backfill(ticker):
        calls.append(ticker)
        return {
            "pack": "statement-backfill",
            "ticker": ticker.upper(),
            "fetched_at": "2026-07-25T00:00:00+00:00",
            "source_kind": "xbrl-companyfacts",
            "company": "APPLE INC",
            "facts": fake_facts,
            "coverage": fake_coverage,
        }

    monkeypatch.setattr(sec_edgar_client, "build_statement_backfill", fake_backfill)

    payload = pack_us.pack_statement_backfill("aapl")

    assert payload["pack"] == "statement-backfill"
    assert payload["ticker"] == "AAPL"
    assert payload["source_kind"] == "xbrl-companyfacts"
    assert payload["company"] == "APPLE INC"
    assert payload["facts"] == fake_facts
    assert payload["coverage"] == fake_coverage
    assert "fetched_at" in payload
    assert calls == ["aapl"]


def test_statement_backfill_source_kind_overrides_producer_disagreement(monkeypatch):
    """The wrapper's docstring guarantees the envelope carries the
    top-level `source_kind` literal `"xbrl-companyfacts"` -- a promise the
    old wholesale `{**envelope, **result}` merge does NOT keep: the
    producer's own `source_kind` key, if present, wins over the envelope's
    (dict-merge semantics -- the right-hand operand's keys always
    override the left-hand's). Stubs a producer success payload with a
    DIFFERENT `source_kind` (a producer bug/regression -- `build_statement_
    backfill` has exactly one companyfacts code path and no legitimate
    reason to ever emit anything else) and asserts the WRAPPER's own
    literal wins. The wrapper, not the producer, is this lane's single
    source of truth for the provenance label -- matching
    `pack_kpi_topline_backfill`, whose producer (`build_top_line_backfill`)
    never even sets `source_kind`; the wrapper alone owns it there too."""
    if str(MARKETS_SCRIPTS) not in sys.path:
        sys.path.insert(0, str(MARKETS_SCRIPTS))
    import pack_us  # noqa: E402
    import sec_edgar_client  # noqa: E402

    fake_facts = [{"concept": "us-gaap:Revenues", "value": 1.0}]
    fake_coverage = {"skipped_rows": []}

    def fake_backfill_wrong_source_kind(ticker):
        return {
            "pack": "statement-backfill",
            "ticker": ticker.upper(),
            "fetched_at": "2026-07-25T00:00:00+00:00",
            "source_kind": "xbrl-dimensional",  # disagrees with the wrapper
            "company": "APPLE INC",
            "facts": fake_facts,
            "coverage": fake_coverage,
        }

    monkeypatch.setattr(
        sec_edgar_client, "build_statement_backfill", fake_backfill_wrong_source_kind
    )

    payload = pack_us.pack_statement_backfill("AAPL")

    assert payload["source_kind"] == "xbrl-companyfacts"


def test_statement_backfill_source_kind_survives_producer_omission(monkeypatch):
    """Companion to the disagreement test above: even a producer payload
    that OMITS `source_kind` entirely must still resolve to the wrapper's
    own `"xbrl-companyfacts"` literal, proving the docstring's guarantee
    is exercised independently of whatever the producer happens to emit
    (or not emit) -- not trusted as a coincidence between this module and
    `sec_edgar_client.build_statement_backfill`."""
    if str(MARKETS_SCRIPTS) not in sys.path:
        sys.path.insert(0, str(MARKETS_SCRIPTS))
    import pack_us  # noqa: E402
    import sec_edgar_client  # noqa: E402

    fake_facts = [{"concept": "us-gaap:Revenues", "value": 1.0}]
    fake_coverage = {"skipped_rows": []}

    def fake_backfill_no_source_kind(ticker):
        return {
            "pack": "statement-backfill",
            "ticker": ticker.upper(),
            "fetched_at": "2026-07-25T00:00:00+00:00",
            # deliberately no `source_kind` key
            "company": "APPLE INC",
            "facts": fake_facts,
            "coverage": fake_coverage,
        }

    monkeypatch.setattr(
        sec_edgar_client, "build_statement_backfill", fake_backfill_no_source_kind
    )

    payload = pack_us.pack_statement_backfill("AAPL")

    assert payload["source_kind"] == "xbrl-companyfacts"


def test_statement_backfill_pack_passes_through_any_producer_error_slot(monkeypatch):
    """A producer error slot rides through the envelope verbatim with no
    `facts` key -- structurally, not by enumerating known error classes.
    `build_statement_backfill` is being extended concurrently (a CIK-history
    guard adding one more error shape), so this stubs a NOVEL error shape
    (keys no current error class carries) to prove the wrapper doesn't
    special-case any particular error class."""
    if str(MARKETS_SCRIPTS) not in sys.path:
        sys.path.insert(0, str(MARKETS_SCRIPTS))
    import pack_us  # noqa: E402
    import sec_edgar_client  # noqa: E402

    def fake_backfill(ticker):
        return {
            "error": f"CIK history conflict for {ticker}",
            "error_class": "cik_history_conflict",
            "identifier": ticker,
            "prior_cik": "0000320193",
            "current_cik": "0000320194",
        }

    monkeypatch.setattr(sec_edgar_client, "build_statement_backfill", fake_backfill)

    payload = pack_us.pack_statement_backfill("AAPL")

    assert payload["error"] == "CIK history conflict for AAPL"
    assert payload["error_class"] == "cik_history_conflict"
    assert payload["prior_cik"] == "0000320193"
    assert payload["current_cik"] == "0000320194"
    assert "facts" not in payload


def test_build_pack_dispatches_statement_backfill(monkeypatch):
    """Registration gap: `pack_statement_backfill` (Task 8) was never wired
    into `build_pack`'s dispatch, mirroring `kpi-topline-backfill`'s branch
    (pack_us.py:1367). Without it `build_pack("statement-backfill", ...)`
    falls through to the generic `unknown pack` ValueError and the lane is
    unreachable from the CLI facade."""
    if str(MARKETS_SCRIPTS) not in sys.path:
        sys.path.insert(0, str(MARKETS_SCRIPTS))
    import pack_us  # noqa: E402

    calls: list[str] = []

    def fake_pack_statement_backfill(ticker):
        calls.append(ticker)
        return {"pack": "statement-backfill", "ticker": ticker}

    monkeypatch.setattr(
        pack_us, "pack_statement_backfill", fake_pack_statement_backfill
    )

    result = pack_us.build_pack("statement-backfill", ["AAPL"])

    assert calls == ["AAPL"]
    assert result == {"pack": "statement-backfill", "ticker": "AAPL"}


def test_reconstruct_pack_is_registered_and_us_only(monkeypatch, capsys):
    """Task 9, docs/loom/plans/2026-07-26-as-filed-statement-reconstruction.md:
    the as-filed reconstruction verb must be REACHABLE from the CLI facade, and
    reachable ONLY for US filers. Three claims, because two of them can hold
    while the third silently does not:

      1. `reconstruct` is in `pack_us.SUPPORTED_PACKS` — without it `build_pack`
         raises the generic `unknown pack` ValueError and the lane is dead.
      2. It DISPATCHES: `build_pack("reconstruct", ["KO"])` reaches
         `pack_reconstruct`. Registration alone is not dispatch — `statement-
         backfill` shipped registered-but-undispatched (see
         `test_build_pack_dispatches_statement_backfill`), so this is a
         measured failure mode in this exact module, not a hypothetical.
      3. It is REFUSED (exit 64) for a non-US market by the facade's
         `US_ONLY_PACKS` guard, which names the refusal as a market-
         availability problem rather than letting `pack_tw.build_pack`'s
         generic `unknown pack` ValueError misreport it as a pack-name typo.

    The US arm asserts the guard does NOT fire for a US ticker — a guard that
    rejects every market would satisfy claim 3 while making the verb
    unreachable everywhere, so the negative case is what proves the guard is
    market-scoped rather than blanket.

    Offline: the `.TW` arm returns before any market module is called, and the
    US arm's producer is stubbed, so neither reaches SEC EDGAR.
    """
    if str(MARKETS_SCRIPTS) not in sys.path:
        sys.path.insert(0, str(MARKETS_SCRIPTS))
    import pack  # noqa: E402
    import pack_us  # noqa: E402

    # --- 1. registered ---
    assert "reconstruct" in pack_us.SUPPORTED_PACKS, (
        f"reconstruct is not registered: {pack_us.SUPPORTED_PACKS}"
    )

    # --- 2. dispatches through build_pack ---
    calls: list[str] = []

    def fake_pack_reconstruct(ticker):
        calls.append(ticker)
        return {"pack": "reconstruct", "ticker": ticker}

    monkeypatch.setattr(pack_us, "pack_reconstruct", fake_pack_reconstruct)

    result = pack_us.build_pack("reconstruct", ["KO"])
    assert calls == ["KO"]
    assert result == {"pack": "reconstruct", "ticker": "KO"}

    # Ticker-count validation, mirroring every other single-heavy pack.
    with pytest.raises(ValueError, match=r"requires exactly one ticker \(single, heavy\)"):
        pack_us.build_pack("reconstruct", ["KO", "PEP"])

    # --- 3. refused for a non-US market, at the facade ---
    assert "reconstruct" in pack.US_ONLY_PACKS, (
        f"reconstruct is not declared US-only: {sorted(pack.US_ONLY_PACKS)}"
    )

    exit_code = pack.main(["--ticker", "2330.TW", "--pack", "reconstruct"])
    assert exit_code == pack.EXIT_USAGE_ERROR
    refusal = json.loads(capsys.readouterr().out)["_status"]
    assert refusal["status"] == "usage_error"
    assert "US-only" in refusal["message"], (
        f"refusal must name market availability, not a pack-name typo: {refusal}"
    )

    # ...and NOT refused for a US ticker (the guard is market-scoped, not blanket).
    calls.clear()
    us_exit = pack.main(["--ticker", "KO", "--pack", "reconstruct", "--quiet"])
    capsys.readouterr()
    assert calls == ["KO"], "the US arm must reach the producer, not be refused"
    assert us_exit != pack.EXIT_USAGE_ERROR


def _reconstruct_row(concept, label, **over):
    """One `get_statement` presentation row, shaped as the live surface
    carries it (verified key set, plan Task 3 Decision Log). Defaults are a
    real statement line: undimensioned, non-placeholder, non-abstract."""
    row = {
        "concept": concept, "label": label, "level": 0,
        "weight": 1.0, "calculation_parent": None,
        "values": {"FY2017": 1.0}, "is_abstract": False,
        "has_dimension_children": False,
    }
    row.update(over)
    return row


class _FakeXBRL:
    def __init__(self, rows):
        self.presentation_roles = ["http://ko.com/role/ConsolidatedStatementsOfIncome"]
        self._rows = rows

    def get_statement(self, role):
        return list(self._rows)


class _FakeFiling:
    """Answers exactly the two-call surface `statements_for` documents as its
    whole input contract (`.xbrl()` -> `presentation_roles` + `get_statement`)."""

    def __init__(self, rows):
        self._rows = rows

    def xbrl(self):
        return _FakeXBRL(self._rows)


def test_pack_reconstruct_emits_per_accession_statements_with_status(monkeypatch):
    """Task 9's producer body: one company, N accessions, the three statements
    per accession as the filer declared them.

    Stubs at the PRODUCERS' OWN boundaries (`resolve_cik` / `list_filings` /
    `_acquire_raw_filing`) and lets the REAL `statements_for` run over
    live-shaped rows -- this repo has a recorded incident where mocking one
    layer up let a green suite certify a crash, and mocking the reconstruction
    itself would leave the seam this task exists to build entirely unexercised.

    Four claims:
      1. the filer's OWN label and concept survive to the payload, in
         presentation order (labels are display-only but they are what the
         reader recognises; brief §Series identity);
      2. a failed acquisition is a LOUD per-accession skip in `failed_items`,
         never a fabricated statements entry -- mirroring
         `_fetch_xval_source_a`'s already-pinned discipline;
      3. the depth-1 `{requested, succeeded, failed}` triple reconciles and
         `_status` reads `partial`, so the facade's structural walk sees the
         degradation without descending into `filings`;
      4. the payload is JSON-SERIALIZABLE. `statements_for` returns frozen
         DATACLASSES (`Statements` / `Line`); `pack.py` ends in
         `json.dumps(...)`, which cannot serialize them. Without an explicit
         projection the verb crashes at the last line of a ~40s run, and no
         assertion on shape alone would catch it.
    """
    if str(MARKETS_SCRIPTS) not in sys.path:
        sys.path.insert(0, str(MARKETS_SCRIPTS))
    import pack_us  # noqa: E402
    import sec_edgar_client  # noqa: E402

    rows = [
        _reconstruct_row("us-gaap:IncomeStatementAbstract", "INCOME", is_abstract=True),
        _reconstruct_row("us-gaap:Revenues", "NET OPERATING REVENUES"),
        _reconstruct_row("ko:UnusualOrInfrequentItemOperating", "OTHER OPERATING CHARGES"),
        # A segment slice interleaved in the same role — must not leak through.
        _reconstruct_row("us-gaap:Revenues", "Asia Pacific", is_dimension=True),
    ]

    good = "0000021344-18-000008"
    bad = "0000021344-17-000009"
    acquire_error = {
        "error": f"SEC EDGAR filing acquisition failed: accession {bad!r} did not resolve",
        "error_class": "resolution",
    }

    monkeypatch.setattr(sec_edgar_client, "resolve_cik", lambda t: {"cik": 21344})
    monkeypatch.setattr(
        sec_edgar_client, "list_filings",
        lambda cik, forms, limit, min_filing_date=None: [
            {"form": "10-K", "filingDate": "2018-02-23", "accessionNumber": good},
            {"form": "10-K", "filingDate": "2017-02-24", "accessionNumber": bad},
        ],
    )
    monkeypatch.setattr(
        sec_edgar_client, "_acquire_raw_filing",
        lambda accession: _FakeFiling(rows) if accession == good else acquire_error,
    )

    envelope = pack_us.pack_reconstruct("ko")

    assert envelope["pack"] == "reconstruct"
    assert envelope["ticker"] == "KO"
    # Nested under one section so the facade's one-level walk honours the
    # self-declared `_status`; see
    # `test_reconstruct_clean_run_classifies_ok_through_the_facade`.
    payload = envelope["reconstruction"]

    # 1. the filer's own labels + concepts, in presentation order
    assert len(payload["filings"]) == 1
    filing = payload["filings"][0]
    assert filing["accession"] == good
    income = filing["statements"]["income"]
    assert [line["label"] for line in income] == [
        "NET OPERATING REVENUES", "OTHER OPERATING CHARGES"
    ], f"labels/order/segment-leak: {income}"
    assert income[1]["concept"] == "ko:UnusualOrInfrequentItemOperating", (
        "the filer's own custom concept must survive — no fixed concept list "
        "could contain it (brief §Decision)"
    )

    # 2. the failed acquisition is loud, and fabricates nothing
    assert [item["accession"] for item in payload["failed_items"]] == [bad]
    assert payload["failed_items"][0]["error_class"] == "resolution"
    assert all(f["accession"] != bad for f in payload["filings"]), (
        "a failed acquisition must never appear as a fabricated statements entry"
    )

    # 3. depth-1 triple reconciles; degradation visible without descending
    assert payload["requested"] == 2
    assert payload["succeeded"] == 1
    assert payload["failed"] == 1
    assert payload["succeeded"] + payload["failed"] == payload["requested"]
    assert payload["_status"] == "partial"

    # 4. the facade's final `json.dumps` must not crash on a dataclass
    json.dumps(envelope)


def _stub_reconstruct_producers(monkeypatch, accessions_to_rows):
    """Stub the three `sec_edgar_client` producers `pack_reconstruct` calls,
    from an {accession: rows-or-error-slot} map. Ordered as given."""
    if str(MARKETS_SCRIPTS) not in sys.path:
        sys.path.insert(0, str(MARKETS_SCRIPTS))
    import sec_edgar_client  # noqa: E402

    monkeypatch.setattr(
        sec_edgar_client, "resolve_cik",
        lambda t: {"cik": 21344, "title": "COCA COLA CO"},
    )
    monkeypatch.setattr(
        sec_edgar_client, "list_filings",
        lambda cik, forms, limit, min_filing_date=None: [
            {"form": "10-K", "filingDate": "2026-02-20", "accessionNumber": a}
            for a in accessions_to_rows
        ],
    )
    monkeypatch.setattr(
        sec_edgar_client, "_acquire_raw_filing",
        lambda accession: (
            accessions_to_rows[accession]
            if isinstance(accessions_to_rows[accession], dict)
            else _FakeFiling(accessions_to_rows[accession])
        ),
    )


def test_reconstruct_clean_run_classifies_ok_through_the_facade(monkeypatch):
    """A run in which EVERY filing reconstructed must classify `ok` through
    `pack._classify_result` -- the real structural reader, not just the
    producer's own opinion of itself.

    LIVE DOGFOOD DEFECT, 2026-07-26 (KO, real SEC fetch): 4 of 4 filings
    reconstructed, `failed_items == []`, the producer self-declared `_status:
    "ok"` -- and the facade still reported `partial`, exit 2. Two causes, both
    invisible to any test that only inspects the producer's own return:

      1. `_list_section_status` reads an EMPTY LIST as `"failed"` (deliberately
         -- for a ticker fan-out, zero rows means nothing came back). A
         top-level `failed_items: []` is the SUCCESS case, and it was being
         read as the failure case.
      2. `main()` assigns `output["_status"] = _status_block(...)`, so a
         producer's own TOP-LEVEL `_status` is overwritten before anyone reads
         it. Depth-1 status belongs on a named SECTION, which is where every
         other pack in this module puts it (`sec_narrative`, `xval_source_a`).

    The degraded arm is asserted in the same test on purpose: a "fix" that
    stops reporting partial at all would satisfy the ok arm while making real
    degradation invisible -- the strictly more dangerous direction, and the
    one this pack's whole failure-honesty contract exists to prevent.
    """
    if str(MARKETS_SCRIPTS) not in sys.path:
        sys.path.insert(0, str(MARKETS_SCRIPTS))
    import pack  # noqa: E402
    import pack_us  # noqa: E402

    rows = [_reconstruct_row("us-gaap:Revenues", "Net Operating Revenues")]

    # --- every filing reconstructed ---
    _stub_reconstruct_producers(monkeypatch, {"0001628280-26-010047": rows})
    clean = pack_us.pack_reconstruct("ko")

    status, failed_sections = pack._classify_result(clean)
    assert status == "ok", (
        f"a 1-for-1 clean reconstruction must not read as {status!r} "
        f"(failed_sections={failed_sections})"
    )

    # --- one filing failed to acquire: degradation must still be visible ---
    _stub_reconstruct_producers(monkeypatch, {
        "0001628280-26-010047": rows,
        "0000021344-25-000011": {"error": "did not resolve", "error_class": "resolution"},
    })
    degraded = pack_us.pack_reconstruct("ko")

    degraded_status, degraded_sections = pack._classify_result(degraded)
    assert degraded_status == "partial", (
        f"a failed acquisition must stay visible to the facade, got "
        f"{degraded_status!r}"
    )
    assert degraded_sections, "the degraded section must be named, not just counted"


def test_reconstruct_reads_enough_filings_for_the_briefs_ten_years():
    """`RECONSTRUCT_ANNUAL_FILINGS` must be enough to actually deliver the
    brief's Smallest End State: "the three statements as filed, for 10+ years".

    MEASURED 2026-07-26, live KO run: FOUR 10-Ks yielded SIX distinct annual
    periods (2020-2025), not ten. Consecutive 10-Ks overlap by their two
    comparative years, so N filings yield N+2 distinct years -- not 3N. The
    brief's own arithmetic ("Ten years is ~4 filings (each 10-K carries three
    comparative years)", §Users) multiplies where it should overlap, and the
    plan's cost note inherits it; both are refuted by the measurement rather
    than reinterpreted. This test is the guard that the constant tracks the
    REQUIREMENT (10+ years) instead of the refuted estimate (4 filings).
    """
    if str(MARKETS_SCRIPTS) not in sys.path:
        sys.path.insert(0, str(MARKETS_SCRIPTS))
    import pack_us  # noqa: E402

    years_yielded = pack_us.RECONSTRUCT_ANNUAL_FILINGS + 2
    assert years_yielded >= 10, (
        f"{pack_us.RECONSTRUCT_ANNUAL_FILINGS} annual filings yield only "
        f"{years_yielded} distinct years (N+2, measured); the brief asks for 10+"
    )


# Money in the fixtures below is stated in DOLLARS, not millions, because the
# rounding interval is computed from the filer's declared `decimals` (-6 =
# reported to the nearest million) against the fact's own magnitude. A fixture
# stating 35410 with decimals -6 would give every group a tolerance 40x its own
# figures and collapse the four statuses into one.
_M = 1_000_000


def _sampled_era_rows():
    """One income statement whose four declared groups come out as four
    DIFFERENT sum-check statuses — the distinction this envelope must carry.

    Group by group, and the arithmetic is stated so a reader can argue with it
    rather than trust it:

      GrossProfit          35,410 - 13,256 = 22,154 against a reported 22,155.
                           1M off, inside the 1.5M its own declared precision
                           permits ((n+1)/2 units at decimals -6, n=2) ->
                           `within_rounding`. THIS IS THE ONE THAT MATTERS: an
                           exact comparison calls it broken, and 24 of the
                           committed capture's 27 disagreements are this shape
                           (plan Decision Log, Task 4 -> Task 8, "the raw count
                           overstates broken filer arithmetic ~8x").
      OperatingExpenses    12,000 + 1,000 = 13,000 against a reported 18,000.
                           5,000M off, nowhere near the interval -> `disagrees`.
      NonoperatingIncome   its only child carries no value for the period, so
                           no sum was computed at all -> `incomplete`. A
                           comparison that could not be made is not one that
                           failed.
      NetIncomeLoss        6,890 - 5,560 = 1,330 exactly -> `agrees`.
    """
    return [
        _reconstruct_row(
            "us-gaap:Revenues", "NET OPERATING REVENUES",
            values={"FY2017": 35410 * _M}, decimals={"FY2017": -6},
            calculation_parent="us-gaap:GrossProfit", weight=1.0,
            balance="credit",
        ),
        _reconstruct_row(
            "us-gaap:CostOfGoodsSold", "COST OF GOODS SOLD",
            values={"FY2017": 13256 * _M}, decimals={"FY2017": -6},
            calculation_parent="us-gaap:GrossProfit", weight=-1.0,
            balance="debit",
        ),
        _reconstruct_row(
            "us-gaap:GrossProfit", "GROSS PROFIT",
            values={"FY2017": 22155 * _M}, decimals={"FY2017": -6}, weight=None,
        ),
        _reconstruct_row(
            "us-gaap:SellingGeneralAndAdministrativeExpense",
            "SELLING, GENERAL AND ADMINISTRATIVE EXPENSES",
            values={"FY2017": 12000 * _M}, decimals={"FY2017": -6},
            calculation_parent="us-gaap:OperatingExpenses", weight=1.0,
        ),
        _reconstruct_row(
            "ko:UnusualOrInfrequentItemOperating", "OTHER OPERATING CHARGES",
            values={"FY2017": 1000 * _M}, decimals={"FY2017": -6},
            calculation_parent="us-gaap:OperatingExpenses", weight=1.0,
        ),
        _reconstruct_row(
            "us-gaap:OperatingExpenses", "TOTAL OPERATING EXPENSES",
            values={"FY2017": 18000 * _M}, decimals={"FY2017": -6}, weight=None,
        ),
        _reconstruct_row(
            "us-gaap:InterestExpense", "INTEREST EXPENSE",
            values={"FY2017": None}, decimals={"FY2017": -6},
            calculation_parent="us-gaap:NonoperatingIncomeExpense", weight=-1.0,
        ),
        _reconstruct_row(
            "us-gaap:NonoperatingIncomeExpense", "OTHER INCOME (LOSS) - NET",
            values={"FY2017": 500 * _M}, decimals={"FY2017": -6}, weight=None,
        ),
        _reconstruct_row(
            "us-gaap:IncomeLossBeforeIncomeTaxes", "INCOME BEFORE INCOME TAXES",
            values={"FY2017": 6890 * _M}, decimals={"FY2017": -6},
            calculation_parent="us-gaap:NetIncomeLoss", weight=1.0,
        ),
        _reconstruct_row(
            "us-gaap:IncomeTaxExpenseBenefit", "INCOME TAXES",
            values={"FY2017": 5560 * _M}, decimals={"FY2017": -6},
            calculation_parent="us-gaap:NetIncomeLoss", weight=-1.0,
        ),
        _reconstruct_row(
            "us-gaap:NetIncomeLoss", "CONSOLIDATED NET INCOME",
            values={"FY2017": 1330 * _M}, decimals={"FY2017": -6}, weight=None,
        ),
    ]


def _post_sample_era_rows():
    """A modern filing whose one declared group reconciles exactly, so the era
    breakdown has something OTHER than the failing era to report. A report
    showing one era says nothing about whether the rate varies by era, which is
    the whole question the brief says must be measured rather than assumed."""
    return [
        _reconstruct_row(
            "us-gaap:RevenueFromContractWithCustomerExcludingAssessedTax",
            "Net operating revenues",
            values={"FY2025": 47000 * _M}, decimals={"FY2025": -6},
            calculation_parent="us-gaap:GrossProfit", weight=1.0,
            balance="credit",
        ),
        _reconstruct_row(
            "us-gaap:CostOfGoodsAndServicesSold", "Cost of goods sold",
            values={"FY2025": 18000 * _M}, decimals={"FY2025": -6},
            calculation_parent="us-gaap:GrossProfit", weight=-1.0,
            balance="debit",
        ),
        _reconstruct_row(
            "us-gaap:GrossProfit", "Gross profit",
            values={"FY2025": 29000 * _M}, decimals={"FY2025": -6}, weight=None,
        ),
    ]


def _stub_reconstruct_filings(monkeypatch, dated_rows):
    """Stub the three `sec_edgar_client` producers from an ordered
    {accession: (filingDate, rows)} map, so a test can place each filing in a
    KNOWN era. `_stub_reconstruct_producers` dates every filing 2026-02-20,
    which puts a whole run in one era and cannot exercise the breakdown."""
    if str(MARKETS_SCRIPTS) not in sys.path:
        sys.path.insert(0, str(MARKETS_SCRIPTS))
    import sec_edgar_client  # noqa: E402

    monkeypatch.setattr(
        sec_edgar_client, "resolve_cik",
        lambda t: {"cik": 21344, "title": "COCA COLA CO"},
    )
    monkeypatch.setattr(
        sec_edgar_client, "list_filings",
        lambda cik, forms, limit, min_filing_date=None: [
            {"form": "10-K", "filingDate": date, "accessionNumber": accession}
            for accession, (date, _rows) in dated_rows.items()
        ],
    )
    monkeypatch.setattr(
        sec_edgar_client, "_acquire_raw_filing",
        lambda accession: _FakeFiling(dated_rows[accession][1]),
    )


def test_reconstruct_envelope_carries_the_resolution_report_and_sum_checks(monkeypatch):
    """The arc's central promise must reach the only surface that ships it.

    WHOLE-BRANCH REVIEW FINDING, 2026-07-26: "Inside the library the
    distinction is clean: `Cell.state` separates `not_presented` from
    `not_tagged`, `SumCheck.status` separates `within_rounding` from
    `disagrees`, `Unresolved` carries five distinct codes. NONE OF IT SHIPS."
    `pack_reconstruct` emitted raw `Line`s only, and `resolution_report` had
    zero references outside its own module and tests — so a reader holding this
    verb's output still could not tell a pipeline defect from an accounting
    fact, which is the brief's reason for existing (§Problem, "It cannot say
    WHY a cell is empty").

    Four claims, each the difference between a typed answer and a blank:

      1. THE PER-ERA COUNTS SHIP. The 63-of-65 resolution rate was measured on
         filings FILED 2016-2018 only and a 10-year run spans years nobody
         sampled (brief §"A limit this brief must not overclaim"), so a single
         run-wide rate is the overclaim the report exists to prevent. Both eras
         present here, with different outcomes.
      2. EVERY UNRESOLVED STATEMENT NAMES ITS REASON, and the detail names the
         group, so the reader can go argue with the filing rather than with a
         count.
      3. `within_rounding` IS DISTINCT FROM `disagrees` AND `incomplete`.
         Asserted as an exact four-way census rather than as "disagrees == 1",
         because collapsing the rounding residue into the disagreement is the
         measured ~8x overstatement (plan Decision Log, Task 4 -> Task 8) and a
         one-sided assertion passes right through it.
      4. THE PAYLOAD SERIALIZES WITHOUT `default=str`. Every figure on a
         `SumCheck` is a `Decimal` and `json.dumps` raises on one. The facade
         does pass `default=str`, which would paper over this at the last line
         of a ~85s run — and would also silently accept a float, the one
         representation this arc's arithmetic rules out. Pinned here on a bare
         `json.dumps`, so the projection has to be explicit.

    Plus the deliberate omission: `cell_state` is NOT in this envelope, and
    `pack_reconstruct` must SAY so. An undocumented absence leaves a reader
    assuming the four-way taxonomy is present — the same undifferentiated
    blank one layer up.
    """
    if str(MARKETS_SCRIPTS) not in sys.path:
        sys.path.insert(0, str(MARKETS_SCRIPTS))
    import pack_us  # noqa: E402

    _stub_reconstruct_filings(monkeypatch, {
        "0000021344-18-000008": ("2018-02-23", _sampled_era_rows()),
        "0000021344-26-000011": ("2026-02-20", _post_sample_era_rows()),
    })

    envelope = pack_us.pack_reconstruct("ko")
    verification = envelope["reconstruction"]["verification"]

    # 1. the per-era breakdown, both eras, different outcomes
    by_era = {tally["era"]: tally for tally in verification["by_era"]}
    assert sorted(by_era) == ["post_2018", "sampled_2016_2018"], (
        f"both eras in the run must be reported: {verification['by_era']}"
    )
    assert (by_era["sampled_2016_2018"]["resolved"],
            by_era["sampled_2016_2018"]["unresolved"]) == (0, 1)
    assert (by_era["post_2018"]["resolved"],
            by_era["post_2018"]["unresolved"]) == (1, 0)
    assert by_era["sampled_2016_2018"]["reasons"] == [
        {"reason": "sums_do_not_reconcile", "count": 1}
    ], f"the era's failure reasons must ride with its counts: {by_era}"

    # 2. the unresolved statement names its reason AND its group
    unresolved = [s for s in verification["statements"] if not s["resolved"]]
    assert len(unresolved) == 1, f"expected one unresolved statement: {unresolved}"
    assert unresolved[0]["filing_date"] == "2018-02-23"
    assert unresolved[0]["kind"] == "income"
    assert unresolved[0]["groups_checked"] == 4
    assert unresolved[0]["groups_incomplete"] == 1
    assert [r["reason"] for r in unresolved[0]["reasons"]] == ["sums_do_not_reconcile"]
    assert "us-gaap:OperatingExpenses" in unresolved[0]["reasons"][0]["detail"], (
        "a reason code with no group named sends the reader nowhere: "
        f"{unresolved[0]['reasons'][0]}"
    )

    # 3. the four-way census — within_rounding is its own answer
    assert verification["sum_checks"]["by_status"] == {
        "agrees": 2, "within_rounding": 1, "disagrees": 1, "incomplete": 1,
    }, f"the four statuses must stay four: {verification['sum_checks']}"

    disagreements = verification["sum_checks"]["disagreements"]
    assert [d["parent"] for d in disagreements] == ["us-gaap:OperatingExpenses"], (
        "only the genuine disagreement belongs here — a within_rounding group "
        f"listed as one rebuilds the ~8x overstatement: {disagreements}"
    )
    # Exact decimal TEXT, digit for digit. The trailing ".0" on the computed
    # figures is not noise and must not be normalised away: it is the scale
    # `Decimal` carried through Sigma(child x weight) at the filer's own
    # weight of 1.0, and `str` is the only projection that neither rounds it
    # nor routes it back through a binary float.
    assert disagreements[0]["reported"] == "18000000000"
    assert disagreements[0]["computed"] == "13000000000.0"
    assert disagreements[0]["difference"] == "-5000000000.0"
    assert disagreements[0]["tolerance"] == "1500000", (
        "the interval the filer's OWN declared precision permits must ride "
        "with the verdict, so a reader can argue with the interval too: "
        f"{disagreements[0]}"
    )
    for figure in ("reported", "computed", "difference", "tolerance"):
        assert isinstance(disagreements[0][figure], str), (
            f"{figure} must be exact decimal TEXT, never a float: "
            f"{disagreements[0][figure]!r}"
        )

    # 4. serializes with no `default=str` fallback
    json.dumps(envelope)

    # the omission is stated, not left to assumption
    doc = pack_us.pack_reconstruct.__doc__
    assert "cell_state" in doc and "derive_spine_as_filed" in doc, (
        "the envelope carries no per-cell typing; a reader must be TOLD that "
        "and told where it does live, rather than assuming the four-way "
        "taxonomy is present"
    )


def test_reconstruct_verification_failure_degrades_but_keeps_the_statements(monkeypatch):
    """Adding verification must not turn a working verb into a crashing one.

    `kpi_us_statement_check` REFUSES rather than guessing, deliberately and by
    its own docstring: a row presented twice under one calculation parent with
    disagreeing figures raises, and so does a filing date with no readable
    year. Both abort the whole run — "a caller running 56 filers should expect
    to lose the run and not one statement". That posture is right for an
    ORACLE, and wrong for this pack to inherit unexamined: the reconstruction
    of every other filing already succeeded, and letting the exception out
    would trade ~85s of good statements for a traceback, making the arc's
    benefit a REGRESSION in the verb that already worked.

    So the failure is contained to the section it belongs to, and made loud
    there:

      1. the statements still ship — the fidelity layer did its job and is not
         held hostage by the verification layer's refusal;
      2. `verification` carries the refusal's own message, not a bare flag; a
         reader must be able to see WHICH row the oracle refused;
      3. the degradation reaches the facade. This is the part that is not
         obvious: `_section_status` honours a section's self-declared
         `_status` and then NEVER descends, so a `verification._status` nested
         inside `reconstruction` is structurally invisible. The failure has to
         be folded into the `reconstruction` section's own `_status` or it is
         silent — asserted through `pack._classify_result`, the real reader,
         rather than through this pack's opinion of itself.
    """
    if str(MARKETS_SCRIPTS) not in sys.path:
        sys.path.insert(0, str(MARKETS_SCRIPTS))
    import pack  # noqa: E402
    import pack_us  # noqa: E402

    refused_rows = [
        _reconstruct_row(
            "us-gaap:Revenues", "NET OPERATING REVENUES",
            values={"FY2017": 35410 * _M},
            calculation_parent="us-gaap:GrossProfit", weight=1.0,
        ),
        # Same concept, same parent, a DIFFERENT figure. De-duplication keeps
        # the first row, so one of these numbers would vanish from the check —
        # the oracle refuses to pick.
        _reconstruct_row(
            "us-gaap:Revenues", "NET OPERATING REVENUES (RESTATED)",
            values={"FY2017": 41863 * _M},
            calculation_parent="us-gaap:GrossProfit", weight=1.0,
        ),
        _reconstruct_row(
            "us-gaap:GrossProfit", "GROSS PROFIT",
            values={"FY2017": 22155 * _M}, weight=None,
        ),
    ]

    _stub_reconstruct_filings(monkeypatch, {
        "0000021344-18-000008": ("2018-02-23", refused_rows),
    })

    envelope = pack_us.pack_reconstruct("ko")
    section = envelope["reconstruction"]

    # 1. the statements survived the verification failure
    assert [line["label"] for line in section["filings"][0]["statements"]["income"]] == [
        "NET OPERATING REVENUES", "NET OPERATING REVENUES (RESTATED)", "GROSS PROFIT"
    ], "the reconstruction must not be discarded because the check refused"

    # 2. the refusal is reported with its own message, under the `error` key
    #    this repo's `_has_error_marker` already treats as the failure signal —
    #    not a second private flag beside it
    verification = section["verification"]
    assert verification["error_class"] == "verification"
    assert "us-gaap:Revenues" in verification["error"], (
        f"the refused row must be nameable from the report: {verification}"
    )

    # 3. the degradation reaches the facade, which never descends past
    #    `reconstruction`'s own self-declared status
    assert section["_status"] == "partial", (
        "a nested `verification._status` is invisible to `_section_status`; "
        "the section's own status has to carry it"
    )
    status, failed_sections = pack._classify_result(envelope)
    assert status == "partial", (
        f"a run whose verification refused must not read as {status!r}"
    )
    assert "reconstruction" in failed_sections

    json.dumps(envelope)


def test_missing_client_dependency_names_what_to_pass(monkeypatch, capsys):
    """A dependency-free invocation must fail with a message naming what to
    pass -- never a bare `ModuleNotFoundError`.

    MEASURED, not hypothetical: the sibling as-reported lane's live dogfood
    died on `ModuleNotFoundError: No module named 'requests'` until both client
    deps were supplied on the `uv run` invocation (Gotcha trailer, PR #619,
    2026-07-26). `pack.py` is a ZERO-DEPENDENCY facade by design -- the market
    clients' deps are supplied per-invocation via `--with` and are deliberately
    never imported by the facade -- so this failure is reachable by every SEC
    pack, and the facade is the one place that knows the invocation contract.

    The raw traceback is KEPT alongside the message. A guidance string that
    replaced the cause would trade one opaque failure for another: the message
    says what to do, the traceback still says what actually happened.
    """
    if str(MARKETS_SCRIPTS) not in sys.path:
        sys.path.insert(0, str(MARKETS_SCRIPTS))
    import pack  # noqa: E402
    import pack_us  # noqa: E402

    def missing_requests(pack_name, tickers):
        # `name=` is what the IMPORT SYSTEM populates on a real failed import
        # (`sec_edgar_client`'s top-level `import requests`), so the stub sets
        # it too -- a hand-built exception missing `name` would let an
        # implementation that only reads `str(exc)` pass a test the real
        # failure shape would not exercise.
        raise ModuleNotFoundError("No module named 'requests'", name="requests")

    monkeypatch.setattr(pack_us, "build_pack", missing_requests)

    exit_code = pack.main(["--ticker", "KO", "--pack", "reconstruct", "--quiet"])
    status = json.loads(capsys.readouterr().out)["_status"]

    assert exit_code == pack.EXIT_FAILED
    assert status["status"] == "failed"

    message = status.get("message", "")
    assert "requests" in message, f"must name the MISSING module: {message}"
    assert "--with" in message, f"must name the fix, not just the symptom: {message}"
    assert "edgartools" in message, (
        f"must name the SEC lane's other client dep too — supplying only the "
        f"one named in the error just moves the failure one import later "
        f"(exactly how PR #619's dogfood went): {message}"
    )
    assert "ModuleNotFoundError" in status.get("traceback", ""), (
        "the real cause must survive alongside the guidance, not be replaced by it"
    )


def test_reconstruct_exit_code_matches_the_run_through_main(monkeypatch, capsys):
    """The nesting fix, pinned at the surface the live defect was SEEN at.

    `test_reconstruct_clean_run_classifies_ok_through_the_facade` pins
    `_classify_result`, which is the mechanism -- but the 2026-07-26 KO run
    reported the defect as **exit 2** on a clean 8-for-8 reconstruction, and no
    test crossed `main()` to reach an exit code. A future change to how
    `main()` maps status -> exit, or to which section carries `_status`, would
    reintroduce the observed symptom while the mechanism test stayed green.

    Both arms again, for the same reason as the classifier test: a change that
    made everything exit 0 would satisfy the clean arm while hiding real
    degradation, which is the more dangerous direction.
    """
    if str(MARKETS_SCRIPTS) not in sys.path:
        sys.path.insert(0, str(MARKETS_SCRIPTS))
    import pack  # noqa: E402

    rows = [_reconstruct_row("us-gaap:Revenues", "Net Operating Revenues")]

    _stub_reconstruct_producers(monkeypatch, {"0001628280-26-010047": rows})
    clean_exit = pack.main(["--ticker", "KO", "--pack", "reconstruct", "--quiet"])
    clean = json.loads(capsys.readouterr().out)
    assert clean_exit == pack.EXIT_OK, (
        f"a clean reconstruction must exit 0, got {clean_exit} "
        f"(failed_sections={clean['_status']['failed_sections']})"
    )
    assert clean["_status"]["status"] == "ok"

    _stub_reconstruct_producers(monkeypatch, {
        "0001628280-26-010047": rows,
        "0000021344-25-000011": {"error": "did not resolve", "error_class": "resolution"},
    })
    degraded_exit = pack.main(["--ticker", "KO", "--pack", "reconstruct", "--quiet"])
    degraded = json.loads(capsys.readouterr().out)
    assert degraded_exit == pack.EXIT_PARTIAL, (
        f"a failed acquisition must still exit 2, got {degraded_exit}"
    )
    assert "reconstruction" in degraded["_status"]["failed_sections"]


def _run_pack_raising(monkeypatch, capsys, exc):
    """Drive `pack.main` with a `build_pack` that raises `exc`; return
    (exit_code, _status block)."""
    if str(MARKETS_SCRIPTS) not in sys.path:
        sys.path.insert(0, str(MARKETS_SCRIPTS))
    import pack  # noqa: E402
    import pack_us  # noqa: E402

    def boom(pack_name, tickers):
        raise exc

    monkeypatch.setattr(pack_us, "build_pack", boom)
    exit_code = pack.main(["--ticker", "KO", "--pack", "reconstruct", "--quiet"])
    return exit_code, json.loads(capsys.readouterr().out)["_status"]


def test_internal_module_failure_is_not_dressed_as_a_client_dep_error(monkeypatch, capsys):
    """A missing INTERNAL module must not be answered with the client-deps
    message.

    The handler answers `ModuleNotFoundError` with "re-run with `--with ...`".
    That is right for a dependency the user supplies on the invocation, and
    WRONG for one of our own modules: `pack_us.pack_reconstruct` imports
    `kpi_us_statement_shape` ACROSS a skill boundary, so a move or rename
    there raises `ModuleNotFoundError` too -- and the user would be told to
    `--with` a package that does not exist, to fix a breakage that is not on
    their command line at all. An internal breakage wearing a user-error
    costume is the same "system disguises its own failure" mode this arc
    exists to remove, reproduced inside the error path meant to prevent it.

    Such a failure must fall through to the generic handler: a real traceback,
    and NO actionable-looking instruction that cannot work.
    """
    exit_code, status = _run_pack_raising(
        monkeypatch, capsys,
        ModuleNotFoundError(
            "No module named 'kpi_us_statement_shape'", name="kpi_us_statement_shape"
        ),
    )

    assert exit_code == 1
    assert status["status"] == "failed"
    assert "--with" not in status.get("message", ""), (
        f"an internal module must not be reported as a user-invocation error: "
        f"{status.get('message')!r}"
    )
    assert "kpi_us_statement_shape" in status.get("traceback", ""), (
        "the real cause must still be surfaced by the generic handler"
    )


def test_missing_edgartools_names_the_distribution_not_the_import_name(monkeypatch, capsys):
    """A missing edgartools must still be handled AND must name what the user
    can actually pass.

    IMPORT NAME != DISTRIBUTION NAME: `import edgar` (sec_edgar_client.py:853)
    raises `exc.name == "edgar"`, but the installable package is `edgartools`.
    Two consequences, and the first is why this test exists at all:

      1. a membership check written against the DISTRIBUTION names would not
         match `"edgar"`, so a genuinely missing client dep would be re-raised
         into the generic traceback handler -- silently reintroducing the bare
         `ModuleNotFoundError` this lane was built to remove;
      2. `--with edgar` installs the wrong project (or nothing), so the
         message must never tell the user to pass the import name.

    The `requests` arm cannot catch either: there the two names coincide.
    """
    exit_code, status = _run_pack_raising(
        monkeypatch, capsys,
        ModuleNotFoundError("No module named 'edgar'", name="edgar"),
    )

    assert exit_code == 1
    message = status.get("message", "")
    assert "--with" in message, (
        f"a genuinely missing client dep must still get the guidance: {message!r}"
    )
    assert "edgartools" in message, f"must name the installable package: {message!r}"
    assert "--with edgar " not in message and not message.endswith("--with edgar"), (
        f"must never tell the user to pass the IMPORT name: {message!r}"
    )
    assert "'edgar'" not in message.split("Pass the whole set")[-1], (
        f"the closing clause must name the distribution, not the import name: {message!r}"
    )


def _required_third_party_imports(path):
    """Top-level module names `path` REQUIRES that are neither stdlib nor a
    local sibling script — i.e. exactly what a caller must supply.

    Imports inside a `try:` with an except handler are EXCLUDED, because they
    are optional by construction. Observed case: `sec_edgar_client.py:1256`
    imports `httpx` under `try/except` to widen a timeout-exception tuple and
    falls back to the builtin `TimeoutError` when it is absent. Declaring it
    would tell the caller to pass a package the lane works fine without —
    a false instruction, which is the same defect class as the false promise
    this test exists to prevent, pointed the other way.
    """
    import ast  # noqa: E402

    local = {
        p.stem
        for scripts in (MARKETS_SCRIPTS, ROOT / "skills" / "analysis-kpi" / "scripts")
        for p in scripts.glob("*.py")
    }
    tree = ast.parse(path.read_text())

    optional: set[int] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Try) and node.handlers:
            for stmt in node.body:
                for inner in ast.walk(stmt):
                    if isinstance(inner, (ast.Import, ast.ImportFrom)):
                        optional.add(id(inner))

    names: set[str] = set()
    for node in ast.walk(tree):
        if id(node) in optional:
            continue
        if isinstance(node, ast.Import):
            names |= {a.name.split(".")[0] for a in node.names}
        elif isinstance(node, ast.ImportFrom) and node.level == 0 and node.module:
            names.add(node.module.split(".")[0])
    return {n for n in names if n not in sys.stdlib_module_names and n not in local}


def test_client_dependencies_covers_every_third_party_import_of_the_sec_lane():
    """`CLIENT_DEPENDENCIES` must be BOUND to the code, not to three copies of
    a sentence.

    The set is currently restated in `pack.py`'s constant, `pack.py`'s module
    docstring, and `SKILL.md` — and the message built from it promises the
    caller "the WHOLE set". Nothing derived that promise from the real imports,
    so adding a third client dependency would leave the message confidently
    false, which is precisely the PR #619 failure it was written to prevent
    (supply what you were told, fail on the next import anyway).

    Derived by parsing the real modules rather than listing names here: a test
    that hardcoded the same two names would be a fourth copy of the sentence,
    not a binding.
    """
    if str(MARKETS_SCRIPTS) not in sys.path:
        sys.path.insert(0, str(MARKETS_SCRIPTS))
    import pack  # noqa: E402

    # Keyed on IMPORT names — what `ModuleNotFoundError.name` actually carries.
    declared = set(pack.CLIENT_DEPENDENCIES)
    for module in ("sec_edgar_client.py", "pack_us.py"):
        found = _required_third_party_imports(MARKETS_SCRIPTS / module)
        assert found <= declared, (
            f"{module} imports {sorted(found - declared)}, which "
            f"`CLIENT_DEPENDENCIES` does not declare — the message's "
            f"\"pass the whole set\" promise is false for those"
        )


def test_build_pack_statement_backfill_requires_exactly_one_ticker():
    """Pins the ticker-count validation, mirroring `kpi-topline-backfill`'s
    branch (pack_us.py:1367-1372) and its exact error-message shape — a
    pack that dispatches but accepts two tickers is only half-wired."""
    if str(MARKETS_SCRIPTS) not in sys.path:
        sys.path.insert(0, str(MARKETS_SCRIPTS))
    import pack_us  # noqa: E402

    with pytest.raises(ValueError, match=r"requires exactly one ticker \(single, heavy\)"):
        pack_us.build_pack("statement-backfill", ["AAPL", "MSFT"])

    with pytest.raises(ValueError, match=r"requires exactly one ticker \(single, heavy\)"):
        pack_us.build_pack("statement-backfill", [])
