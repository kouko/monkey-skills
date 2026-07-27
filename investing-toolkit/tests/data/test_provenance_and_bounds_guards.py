"""test_provenance_and_bounds_guards.py — the guards that let bad rows through.

Third batch from the 2026-07-27 sampled mutation pass. Where
`test_silent_arithmetic_guards.py` covers calculations that return a wrong
number, this file covers the checks that decide whether a row is USABLE at
all — a weakened `or`, a flipped bounds test, a diagnostic that names the
wrong field. Their failure mode is the one this repo has spent the day
removing: something unusable is admitted, or something admitted is described
wrongly, and nothing raises.
"""
from __future__ import annotations

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

import exhibit_tables  # noqa: E402
import pack_us  # noqa: E402
import sec_edgar_client as sec  # noqa: E402


# ---------------------------------------------------------------------------
# Mutants: sec_edgar_client.py:3617 `or` -> `and`
#          sec_edgar_client.py:3621 `if not present` -> `if present`
# ---------------------------------------------------------------------------

def _row(**over):
    row = {"start": "2023-01-01", "end": "2023-12-31",
           "accn": "0000320193-24-000123", "form": "10-K"}
    row.update(over)
    return row


@pytest.mark.parametrize("missing,kept", [("form", "accession"),
                                          ("accn", "form")])
def test_a_row_missing_either_provenance_field_is_skipped(missing, kept):
    """The lane's stated contract is that it "emits no fact whose provenance
    (accession/form) it cannot state". Weakening the `or` to `and` admits a
    row that is missing exactly ONE of the two — the common case, since a row
    missing both is rare — so a fact ships with unstatable provenance."""
    flag = sec._statement_carrier_flag(
        "us-gaap:Revenues", _row(**{missing: None}), ticker="AAPL"
    )

    assert flag is not None, (
        f"a row with no {missing!r} must be skipped, not admitted"
    )
    assert flag["type"] == "source_filing_unidentifiable"


def test_the_skip_message_names_the_field_that_is_missing_not_the_one_present():
    """The message is the whole diagnostic value of the skip. Inverting the
    filter makes it name the field that IS there, so an operator reading
    "carries no companyfacts form" goes looking at a row whose form is fine
    and whose accession is the actual problem."""
    flag = sec._statement_carrier_flag(
        "us-gaap:Revenues", _row(accn=None), ticker="AAPL"
    )

    # Scope the assertion to the field list itself: the sentence ends with the
    # boilerplate "(accession/form)", which names BOTH fields and would make a
    # whole-message substring check pass no matter which one was reported.
    reason = flag["reason"]
    assert "carries no companyfacts " in reason and ", so its" in reason, (
        f"the message no longer has the span this assertion scopes to, so it "
        f"cannot say which field was named: {reason}"
    )
    named = reason.split("carries no companyfacts ")[1].split(", so its")[0]

    assert named == "accession", (
        f"the message must name the missing field, not the present one: "
        f"{named!r} in {flag['reason']}"
    )


def test_a_row_carrying_both_provenance_fields_is_not_skipped_for_provenance():
    """The other direction, so the assertions above are discriminating rather
    than merely non-None: a complete row must pass this particular guard."""
    flag = sec._statement_carrier_flag(
        "us-gaap:Revenues", _row(), ticker="AAPL"
    )

    assert flag is None or flag["type"] != "source_filing_unidentifiable"


# ---------------------------------------------------------------------------
# Mutant: sec_edgar_client.py:1116  `form is not None` -> `form is None`
# ---------------------------------------------------------------------------

def test_an_acquisition_error_carries_the_form_it_was_asked_for():
    """`_acquire_error`'s slot is what a reader sees when a filing cannot be
    fetched. Inverting the guard drops `form` whenever it is known and inserts
    `None` whenever it is not — so the one field that says WHICH filing failed
    is present exactly when it is useless."""
    with_form = sec._acquire_error("resolution", "no such filing",
                                   identifier="X", form="10-K")
    without_form = sec._acquire_error("resolution", "no such filing",
                                      identifier="X")

    assert with_form["form"] == "10-K"
    assert "form" not in without_form, (
        f"an unknown form must be omitted, not stored as None: {without_form}"
    )


# ---------------------------------------------------------------------------
# Mutant: sec_edgar_client.py:690  `i < len(...)` -> `i >= len(...)`
# ---------------------------------------------------------------------------

def test_a_short_parallel_column_yields_none_not_another_rows_value(monkeypatch):
    """SEC omits a column entirely when no row uses it, and `list_filings`
    reads the parallel arrays POSITIONALLY. The bounds test is what turns a
    short column into `None` for the rows past its end; flipping it reads the
    column exactly where it does NOT reach and skips it where it does."""
    recent = {
        "form": ["10-K", "10-K"],
        "filingDate": ["2026-02-01", "2025-02-01"],
        "accessionNumber": ["acc-2026", "acc-2025"],
        "primaryDocument": ["a.htm", "b.htm"],
        "primaryDocDescription": ["10-K"],          # short by one row
        "items": ["", ""],
        "reportDate": ["2026-02-01", "2025-02-01"],
    }
    monkeypatch.setattr(
        sec, "fetch_submissions",
        lambda cik: {"data": {"filings": {"recent": recent}}},
    )

    rows = sec.list_filings(1, ["10-K"], 5)

    assert [r["primaryDocDescription"] for r in rows] == ["10-K", None], (
        f"row 2 must carry None, never row 1's description: {rows}"
    )


# ---------------------------------------------------------------------------
# Mutant: pack_us.py:491  `i < len(long_term_debt)` -> `i >= len(...)`
# ---------------------------------------------------------------------------

def _annual(end, value):
    return {"end": end, "val": value, "value": value, "filed": "2024-02-01",
            "form": "10-K", "start": f"{end[:4]}-01-01", "fy": int(end[:4]),
            "fp": "FY"}


def test_total_debt_treats_a_missing_component_as_zero_not_as_a_gap():
    """`total_debt` aligns two series of unequal length, and the documented
    rule is "missing components -> 0". Flipping the bounds test reads the
    shorter list exactly where it has no entry (IndexError) or substitutes 0
    where a real figure exists — either way the debt series stops matching the
    filer's own numbers."""
    ltd_concept = pack_us.DCF_CONCEPT_MAPPING["long_term_debt"][0]
    std_concept = pack_us.DCF_CONCEPT_MAPPING["short_term_debt"][0]
    raw = {
        ltd_concept: {"observations": [_annual("2023-12-31", 500.0),
                                       _annual("2022-12-31", 400.0)]},
        std_concept: {"observations": [_annual("2023-12-31", 50.0)]},
    }

    out = pack_us._normalize_dcf(raw)

    assert out["balance_sheet"]["total_debt"] == [550.0, 400.0], (
        "the year with no short-term component must total the long-term "
        f"figure alone: {out['balance_sheet']['total_debt']}"
    )


# ---------------------------------------------------------------------------
# Mutant: exhibit_tables.py:135  `return 1` -> `return 2` (span default)
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("garbage", [None, "", "abc", "2.5", {}])
def test_an_unparseable_span_defaults_to_one_column(garbage):
    """A cell whose colspan attribute is missing or malformed occupies ONE
    column. Defaulting to 2 silently doubles that cell's width, shifting every
    value to its right into the wrong column — on untrusted filer HTML, where
    malformed attributes are exactly what this function exists for."""
    assert exhibit_tables._span(garbage) == 1


def test_a_well_formed_span_is_honoured_and_clamped():
    assert exhibit_tables._span("3") == 3
    assert exhibit_tables._span(0) == 1          # floor
    assert exhibit_tables._span(10**9) == exhibit_tables._MAX_SPAN  # ceiling


# ---------------------------------------------------------------------------
# Mutant: sec_edgar_client.py:122  `status_code == 429` -> `!= 429`
# ---------------------------------------------------------------------------

class _Resp:
    def __init__(self, status, payload=None, retry_after=None):
        self.status_code = status
        self._payload = payload
        self.headers = {"Retry-After": retry_after} if retry_after else {}

    def json(self):
        return self._payload


def _stub_requests(monkeypatch, responses):
    """Replace the module's `requests` alias with a scripted sequence, and
    neutralise the throttle/backoff sleeps so the test is fast."""
    calls = []

    def _get(url, **kw):
        calls.append(url)
        return responses[min(len(calls) - 1, len(responses) - 1)]

    stub = mock.MagicMock(name="requests")
    stub.get = _get
    stub.exceptions.Timeout = TimeoutError
    stub.exceptions.ConnectionError = ConnectionError
    monkeypatch.setattr(sec, "_requests", stub)
    monkeypatch.setattr(sec.time, "sleep", lambda *_a, **_k: None)
    return calls


def test_a_429_is_retried_and_a_200_is_not(monkeypatch):
    """SEC's fair-access policy makes 429 handling a compliance surface, not
    an optimisation. Inverting the comparison retries every SUCCESSFUL
    response — three requests where one was asked for, against a rate limit —
    and returns a rate-limited 429 body straight through as data."""
    calls = _stub_requests(monkeypatch, [
        _Resp(429, retry_after="1"),
        _Resp(200, {"ok": True}),
    ])

    out = sec._sec_get("https://data.sec.gov/probe")

    assert out == {"ok": True}
    assert len(calls) == 2, f"a 429 must be retried exactly once here: {calls}"


def test_a_200_is_returned_on_the_first_request(monkeypatch):
    """The discriminating half: with the comparison inverted a plain 200 is
    treated as rate-limited and re-requested."""
    calls = _stub_requests(monkeypatch, [_Resp(200, {"ok": True})])

    out = sec._sec_get("https://data.sec.gov/probe")

    assert out == {"ok": True}
    assert len(calls) == 1, f"a 200 must not be retried: {calls}"


def test_persistent_rate_limiting_ends_in_a_typed_error(monkeypatch):
    """After MAX_RETRIES the client must say it was rate-limited rather than
    hand back the 429 body as if it were data."""
    calls = _stub_requests(monkeypatch, [_Resp(429)])

    out = sec._sec_get("https://data.sec.gov/probe")

    assert out == {"error": "SEC EDGAR rate-limited (429) after retries"}
    assert len(calls) == sec.MAX_RETRIES
