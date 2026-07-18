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

    # --- (c) SUPPORTED_PACKS carries data-us/scripts/pack.py's --pack choices ---
    # Exact-prefix, not exact-equality: the migration contract is that no
    # historical data-us pack was dropped or renamed. Packs ADDED after the
    # consolidation (kpi-quarterly, 2026-07-18 memo-quarterly-kpi-wiring
    # Task 1) are appended after the migrated five and are not this
    # migration test's concern.
    assert pack_us.SUPPORTED_PACKS[:5] == (
        "snapshot", "memo-fetch", "comps-multiples", "screener-batch", "regime-pack",
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
