"""Two-lane top-line seam probe (Task 6, docs/loom/plans/2026-07-25-company-
total-revenue.md): a REAL Lane A backfill pack and a REAL-shaped Lane B pack
for the same ticker, driven through the SHIPPED CLIs
`kpi_xbrl_ingest ingest` -> `kpi_store dump` -> `tearsheet_format`, over an
ISOLATED `KPI_STORE_DIR`. Mirrors `test_kpi_xbrl_to_tearsheet_e2e.py` (arc
(d)'s seam probe): no chain logic is re-implemented here, and the durable
store is never touched.

WHY A SEPARATE E2E AT ALL. Every unit test on both lanes hand-builds the pack
envelope it feeds to `ingest_pack` (`test_kpi_xbrl_ingest.py::_pack` adds a
`fiscal_calendars` map). This file instead ingests the envelope
`pack_us.pack_kpi_topline_backfill` ACTUALLY EMITS, which is what a real
operator runs — the one thing no unit test on either side of the seam can see
(memory `cross-module-field-contracts-execute-probes.md`).

ASYMMETRY, STATED. That claim holds for LANE A ONLY, and the difference is
load-bearing enough to spell out rather than let a reader assume symmetry:

  - LANE A runs for real. `_build_lane_a_pack` calls the real
    `pack_kpi_topline_backfill` over the real `build_top_line_backfill`, with
    ONLY the network boundary (`resolve_cik` / `fetch_facts`) stubbed. The
    envelope is consumed exactly as returned — never reshaped, never topped up.
  - LANE B IS HAND-BUILT (`_aapl_lane_b_pack`, `_intc_lane_b_pack`) — the very
    construction this file criticises above. `pack_kpi_quarterly` reaches its
    facts through edgartools `Filing` objects, which an offline suite cannot
    stub with two patches, so the stand-in imitates the envelope instead.
    Real `pack_kpi_quarterly` emits seven keys (`pack_us.py:973` docstring,
    `:1033-1039` return): `{pack, ticker, fetched_at, company, facts,
    fiscal_calendars, coverage}`. The AAPL stand-in supplies five of those
    (no `fetched_at`, no `coverage`); the INTC one, built on the restatement
    capture, supplies four (also no `pack`).
  - CONSEQUENCE: the defect class caught on Lane A is NOT covered on Lane B.
    Task 2's flat top-line emission never crosses the extractor→ingest seam in
    any test in this repo, and Lane B's `fiscal_calendars` map is present here
    BY INSPECTION of `pack_kpi_quarterly`'s merge + return
    (`pack_us.py:1017-1020,1038`, verified 2026-07-25), not because this test
    executed the producer that builds it. Filed as a BACKLOG follow-up
    (`docs/loom/backlog/2026-07-25-investing-toolkit-top-line-revenue-lane-2-36-0-post-ship-follow-ups.md`,
    item (c), Lane B's envelope contract) rather than
    left as a silent hole; closing it needs a `Filing`-level fixture, which is
    a task of its own and deliberately NOT attempted here.

HISTORY — WHAT THIS FILE FOUND, AND WHAT IT NOW PINS. On first write the four
AAPL tests were RED, and the RED was a real defect rather than a missing
fixture: `pack_kpi_topline_backfill` emitted no `fiscal_calendars`, so
`facts_to_points`' `_require_source_form` (`kpi_xbrl.py:289-309`) rejected
EVERY Lane A fact ("fact's source form is underivable — the pack's
fiscal_calendars carries no readable dei fiscal_period_focus for accession
…"), and brief Smallest End State #2 was unreachable end-to-end. The fix went
to the PRODUCER (`pack_us.py:1098-1104`, `build_top_line_backfill`'s
`fiscal_calendars` map), NOT into this file: injecting the map in-test would
have turned the suite green while leaving the shipped lane broken.

All nine tests pass now, and those four are the REGRESSION PIN for it —
drop `fiscal_calendars` from the Lane A envelope again and all four fail at
ingest (verified by mutation, see below).

MUTATION-VERIFIED, because none of these can be RED against missing
production code any more (Tasks 1-5/7/11 shipped the chain). Each mutation was
run against this tree and the production file restored byte-identical:

  - drop `fiscal_calendars` from the Lane A envelope -> the four AAPL tests
    error at ingest (the original defect, re-armed);
  - `_TOP_LINE_SOURCE_KIND` -> `"xbrl-dimensional"` -> the two provenance
    tests and the sole-authority test fail;
  - `_TOP_LINE_KPI_ID` renamed -> every test that names the canonical series
    fails (3 failed + 4 errored);
  - `FISCAL_BOUNDARY_TOLERANCE_DAYS` -> 0 -> the New-Year-CROSSING skip case
    here, its sibling in `test_sec_edgar_top_line_backfill.py`, and the
    sole-authority test fail (3). The December-year-end tests correctly stay
    green: they assert the guard does NOT fire, which no narrowing can break;
  - `_is_near_new_year_boundary` restored to its ORIGINAL SYMMETRIC form (the
    `for jan1_year in (year, year + 1)` loop) -> the two December-year-end
    tests fail (`test_december_year_end_filer_is_backfilled_and_agrees_with_
    lane_b` here, reporting `appended: 0`, and
    `test_backfill_keeps_december_year_end_row_both_lanes_label_alike` in the
    data suite). That mutation is the SHIPPED BUG this pair was written
    against, not a hypothetical: the symmetric guard skipped the entire Lane A
    backfill of every December-fiscal-year-end filer;
  - Lane A reads the row's `fy` trap instead of its own period end -> the
    identical-label, Lane-A-only-year and Lane-A-provenance tests fail.
    NOTE it does NOT fail the shared-year VALUE test: that test's property is
    value agreement, whose fires-loudly direction is owned by
    `test_kpi_xbrl_ingest.py::test_cross_lane_value_disagreement_raises`;
  - `_companyconcept_row`'s `"form"` -> `"10-Q"` -> the crossing-skip and
    December-year-end tests fail and the four AAPL tests error (see that
    helper: the carrier-form gate is why).

TWO FILERS, AND THE ASYMMETRY THAT DECIDES WHICH ONE CARRIES WHICH HALF.
The plan's Amendment 5(c) asks that "both lanes emit an IDENTICAL `period`
label for a shared fiscal year, using a near-New-Year-FYE filer", and it IS
satisfiable — INTC (FYE 2025-12-27) is exactly that filer and does have a
shared, identically-labelled fiscal year. An earlier revision of this file
recorded 5(c) as unsatisfiable, on the belief that 5(b)'s skip removed every
near-New-Year row from Lane A. That belief was wrong, and the false premise
outlived eleven task reviews because this docstring asserted it and no probe
checked it.

THE HAZARD 5(b) GUARDS IS ONE-SIDED (probed against both label functions,
2026-07-25). Lane B's `_derive_fiscal_label` walks to the first nominal
fiscal-year end at-or-after `period_end`, so:

  period_end     Lane A (period-end year)  Lane B (dei walk)  agree?
  2025-12-27     2025                      2025               yes
  2024-12-31     2024                      2024               yes
  2026-01-03     2026                      2025               NO  <- the hazard

Only a year-end that has CROSSED INTO January diverges. A December year-end,
however close to Jan 1, gets the same label from both rules — so the skip
buys nothing there and costs the entire Lane A backfill of most of the US
market. `_is_near_new_year_boundary` therefore fires on the after-Jan-1 side
only, and the three properties are pinned on the two filers that can carry
them:

  - INTC's REAL year-end (2025-12-27, a real 52/53-week filer, 5 days from
    Jan 1) — the DECEMBER half: Lane A backfills it and derives the SAME
    label Lane B does, so the shared year holds exactly one point under one
    label (`test_december_year_end_filer_is_backfilled_and_agrees_with_lane_b`
    — this is 5(c), literally). INTC is also the repo's only REAL captured
    cross-filing recast, so it carries the tearsheet/dagger assertion too.
  - INTC under the COUNTERFACTUAL crossing window (2026-01-03) — the
    CROSSING half: Lane A skips with a NAMED coverage reason, Lane B stays
    sole authority, and no second, divergently-labelled point lands in the
    series (so one filing can never mint a fabricated restatement dagger).
  - AAPL (FYE 2025-09-27, ~3 months from Jan 1, nowhere near the boundary):
    the ordinary-filer control, where the identical-value AND
    identical-`period`-label property is pinned free of any boundary logic.

FIXTURE PROVENANCE (no financial value below is hand-authored):
  - `tests/data/fixtures/topline_probe_2026-07-25.json` — the committed
    8-filer live probe (Task 1). Source of AAPL's and INTC's real top-line
    concept, period window, value and accession, captured 2026-07-25.
  - `fixtures/xbrl_aapl_factpack.json` — real AAPL FY2025 10-K facts
    (accession 0000320193-25-000079, filed 2025-10-31), machine-captured via
    edgartools; used here ONLY for its real annual label group and its real
    `fiscal_calendars` entry.
  - `fixtures/xbrl_restatement_factpack.json` — the real INTC FY2020 CCG
    cross-filing recast (two vintages, accessions 0000050863-22-000007 /
    0000050863-23-000006), the same capture arc (d)'s e2e drives.
  - THREE constructed elements, none of them a value — every dollar figure,
    concept and accession above is captured. Each mutates only a period
    window (or the label that window implies) on a real captured row, the
    convention `test_sec_edgar_top_line_backfill.py::_row` and
    `test_sec_edgar_dimensional.py::test_annual_out_of_tolerance_unclassifiable`
    already use (memory `hand-authored-fixture-is-a-fabrication-risk`:
    fabrication is about inventing VALUES, not about constructing a
    boundary-condition date):
      1. `_AAPL_LANE_A_ONLY_WINDOW` — AAPL's real FY2024 window, carrying the
         real FY2025 value, to give Lane A a year Lane B does not cover.
      2. `_INTC_NEW_YEAR_CROSSING_WINDOW` — a 52/53-week year rolling past
         New Year. No filer in the probe has one, and without it the
         "the skip prevents divergence" property is untestable (see the
         constant, and `test_near_new_year_skip_leaves_lane_b_the_sole_authority`).
      3. The dei calendar entry `_intc_lane_b_pack` builds for that window —
         a `fiscal_year_focus`/`fiscal_year` label (2025) against a period
         ending 2026-01-03. INTC never filed this combination; it is the
         divergence hazard rendered concrete, and it is what Lane B must hold
         alone.

Run offline (no network marker; part of the default `not network` suite):
  PYTHONDONTWRITEBYTECODE=1 uv run --quiet --with pytest --with 'pyyaml>=6.0' \
    pytest investing-toolkit/tests/ -m "not network" -q --tb=short
"""
from __future__ import annotations

import importlib
import json
import os
import subprocess
import sys
from pathlib import Path
from unittest import mock

import pytest

from conftest import FIXTURES, KPI_STORE_SCRIPT, ROOT, SKILLS

INGEST_SCRIPT = SKILLS / "analysis-kpi" / "scripts" / "kpi_xbrl_ingest.py"
TEARSHEET_SCRIPT = SKILLS / "report-kpi-tearsheet" / "scripts" / "tearsheet_format.py"
MARKETS_SCRIPTS = SKILLS / "data-markets" / "scripts"

DATA_FIXTURES = ROOT / "tests" / "data" / "fixtures"
TOPLINE_PROBE = DATA_FIXTURES / "topline_probe_2026-07-25.json"
AAPL_FACTPACK = FIXTURES / "xbrl_aapl_factpack.json"
RESTATEMENT_FIXTURE = FIXTURES / "xbrl_restatement_factpack.json"

# Both filers report their top line under the ASC-606 contract concept and
# NOTHING earlier in the allowlist -- read off the probe's `A_flat` buckets,
# never assumed (AAPL and INTC each have exactly this one flat candidate).
_TOP_LINE_CONCEPT = "us-gaap:RevenueFromContractWithCustomerExcludingAssessedTax"
_TOP_LINE_CONCEPT_LOCAL = _TOP_LINE_CONCEPT.split(":")[1]

# CIKs read off the probe's own accession prefixes (0000320193 / 0000050863) --
# the stubbed `resolve_cik` must return what the real one would.
_AAPL_CIK = 320193
_INTC_CIK = 50863

# AAPL's FY2025 10-K filing date, machine-captured in
# tests/data/fixtures/xbrl_quarterly_completeness_aapl.json (`fy2025_10k`) and
# carried identically on every fact of fixtures/xbrl_aapl_factpack.json.
_AAPL_FILED = "2025-10-31"

# The probe captured no `filed` date for INTC's FY2025 10-K. This is the SAME
# stand-in `test_kpi_xbrl_ingest.py::_INTC_FY2025_AS_OF` uses, for the same
# reason: it serves only as the store's bitemporal `as_of` key (and must stay
# consistent with the accession's own 26- year segment), and no assertion here
# depends on its real-world accuracy.
_INTC_FILED = "2026-01-22"

# AAPL's real FY2024 window (`period_end` 2024-09-28 is captured verbatim in
# fixtures/xbrl_aapl_factpack.json; its `start` is the day after the FY2023
# year-end, the 52/53-week convention). Used for the LANE-A-ONLY year: the row
# reuses AAPL's REAL captured FY2025 top-line VALUE unchanged -- only the
# period window is counterfactual, so no dollar figure is invented.
_AAPL_LANE_A_ONLY_WINDOW = ("2023-10-01", "2024-09-28")

# The plan's own worked hazard (Amendment note 5(b)): a 52/53-week fiscal year
# that ROLLS PAST New Year, so the filing's dei calendar calls it FY2025 while
# the period ends in calendar 2026. This is the ONE case where the two lanes'
# labelling rules can actually DIVERGE, and no filer in the captured probe has
# such a window -- so it is a counterfactual WINDOW (363 days ~ 52 weeks) over
# INTC's real captured value/accession, never an invented figure. Without it
# the "the skip prevents divergence" assertion would be untestable: for INTC's
# real year-end (2025-12-27) both rules answer 2025 anyway.
_INTC_NEW_YEAR_CROSSING_WINDOW = ("2025-01-05", "2026-01-03")
_INTC_NEW_YEAR_CROSSING_DEI_LABEL = 2025


# --------------------------------------------------------------------------
# Captured-fixture readers
# --------------------------------------------------------------------------

def _probe_record(ticker: str) -> dict:
    for record in json.loads(TOPLINE_PROBE.read_text(encoding="utf-8")):
        if record["ticker"] == ticker:
            return record
    raise AssertionError(f"probe fixture carries no {ticker!r} record")


def _probe_flat_sample(ticker: str) -> dict:
    """The captured flat top-line `A_flat` sample: real concept, real
    `period_start`/`period_end` window, real value."""
    return _probe_record(ticker)["A_flat"][_TOP_LINE_CONCEPT]["sample"]


def _aapl_annual_label_group() -> dict:
    """AAPL's REAL FY2025 annual 10-K label group, read off
    fixtures/xbrl_aapl_factpack.json's flat FY2025 record (`fiscal_year`,
    `fiscal_quarter`, `duration_months`, `calendar_year`, `calendar_quarter`,
    `derivation_basis`, `accession`, `filed`) -- the exact field-set
    `classify_fact_period` consumes, derived by the REAL producer against
    AAPL's dei calendar. Only the concept/value/window are replaced below.
    """
    facts = json.loads(AAPL_FACTPACK.read_text(encoding="utf-8"))["facts"]
    for fact in facts:
        if fact["fiscal_year"] == 2025 and fact["axis"] is None:
            return fact
    raise AssertionError("AAPL factpack carries no flat FY2025 annual fact")


def _aapl_fiscal_calendars() -> dict:
    """AAPL's real per-accession dei calendar map, read off the same capture."""
    return json.loads(AAPL_FACTPACK.read_text(encoding="utf-8"))["fiscal_calendars"]


# --------------------------------------------------------------------------
# Lane B packs (the per-filing parse's emitted shape)
# --------------------------------------------------------------------------

def _aapl_lane_b_pack() -> dict:
    """AAPL's Lane B pack: ONE flat top-line fact for FY2025. Built from the
    real FY2025 annual label group with the top-line identity fields replaced
    by the probe's captured concept / window / value -- the same
    "real-shaped derivative" construction `test_kpi_xbrl_ingest.py::
    _flat_topline_fact` uses.

    HAND-BUILT ENVELOPE — see the module docstring's ASYMMETRY paragraph. The
    `fiscal_calendars` entry is the capture's own, and the envelope's shape was
    taken by INSPECTION of `pack_us.py:1017-1020,1038` (five of the seven keys
    `pack_kpi_quarterly` returns; no `fetched_at`, no `coverage`). This is NOT
    a claim that the producer was executed — it was not, and an unverified
    "this is what the producer emits" assertion is precisely the species of
    claim whose Lane A counterpart was false and cost this arc a defect.
    """
    sample = _probe_flat_sample("AAPL")
    fact = dict(_aapl_annual_label_group())
    for old_shape_key in ("axis", "member"):
        fact.pop(old_shape_key, None)
    fact.update(
        concept=_TOP_LINE_CONCEPT,
        dimensions={},
        consolidation=None,
        value=sample["value"],
        period_start=sample["period_start"],
        period_end=sample["period_end"],
    )
    return {
        "pack": "kpi-quarterly",
        "ticker": "AAPL",
        "company": "AAPL",
        "facts": [fact],
        "fiscal_calendars": _aapl_fiscal_calendars(),
    }


def _intc_lane_b_pack(window: tuple[str, str] | None = None, fiscal_year: int = 2025) -> dict:
    """INTC's Lane B pack: the REAL two-vintage FY2020 CCG restatement
    (dimensional) PLUS INTC's captured FY2025 flat top-line fact -- the
    both-kinds-of-fact-in-one-pack shape a per-filing parse really emits.
    Mirrors `test_kpi_xbrl_ingest.py::_mixed_pack`.

    `window` overrides the flat fact's period window ONLY (value, concept and
    accession stay the capture's), for the New-Year-crossing hazard shape; the
    `fiscal_year` stays the label the FILING's dei calendar declares, which is
    exactly what can diverge from Lane A's period-end-year rule.
    """
    pack = json.loads(RESTATEMENT_FIXTURE.read_text(encoding="utf-8"))
    for fact in pack["facts"]:
        # The producer's `period_start` (arc (d) Task 1). INTC FY2020 was a
        # 52-week year ending 2020-12-26 -> it began 2019-12-29; both vintages
        # report the SAME window, which is what lets `same_period` group them
        # into the one restatement entry. Same augmentation the sibling e2e
        # (`test_kpi_xbrl_to_tearsheet_e2e.py`) applies.
        fact["period_start"] = "2019-12-29"

    sample = _probe_flat_sample("INTC")
    period_start, period_end = window or (sample["period_start"], sample["period_end"])
    flat = dict(pack["facts"][0])
    flat.update(
        concept=_TOP_LINE_CONCEPT,
        dimensions={},
        consolidation=None,
        value=sample["value"],
        period_start=period_start,
        period_end=period_end,
        fiscal_year=fiscal_year,
        calendar_year=int(period_end[:4]),
        accession=_probe_record("INTC")["accession"],
        filed=_INTC_FILED,
    )
    pack["facts"].append(flat)
    pack["fiscal_calendars"][flat["accession"]] = {
        "fiscal_period_focus": "FY",
        # INTC's real nominal year-end, left at the capture's value on purpose.
        # Under the New-Year-crossing window it is deliberately incoherent with
        # `period_end` (--12-26 against a period ending 2026-01-03); nothing on
        # this path consumes it -- `_require_source_form` reads only
        # `fiscal_period_focus` -- so it is kept real rather than invented to
        # match a window INTC never filed.
        "fiscal_year_end": "--12-26",
        "fiscal_year_focus": str(fiscal_year),
    }
    pack["ticker"] = "INTC"
    return pack


# --------------------------------------------------------------------------
# Lane A packs -- built by the REAL producer, not hand-shaped
# --------------------------------------------------------------------------

@pytest.fixture
def markets_modules():
    """`sec_edgar_client` + `pack_us` with `edgar`/`requests` stubbed in
    sys.modules and restored afterwards -- the convention
    `test_sec_edgar_top_line_backfill.py::sec_client` uses, so this analysis-
    side suite can drive the real data-layer producer offline.
    """
    if str(MARKETS_SCRIPTS) not in sys.path:
        sys.path.insert(0, str(MARKETS_SCRIPTS))
    saved = {name: sys.modules.get(name) for name in ("edgar", "requests", "sec_edgar_client")}
    sys.modules["edgar"] = mock.MagicMock(name="edgar")
    sys.modules["requests"] = mock.MagicMock(name="requests")
    sys.modules.pop("sec_edgar_client", None)
    sec_edgar_client = importlib.import_module("sec_edgar_client")
    pack_us = importlib.import_module("pack_us")
    try:
        yield sec_edgar_client, pack_us
    finally:
        for name, module in saved.items():
            if module is not None:
                sys.modules[name] = module
            else:
                sys.modules.pop(name, None)


def _companyconcept_row(*, start: str, end: str, value: float, accession: str, filed: str) -> dict:
    """One raw `companyconcept` `units.USD[]` row (`summarize_concept`'s input
    shape).

    `fy`/`fp` are stamped with the FILING's own focus on every row -- the
    live-confirmed trap (plan §Notes) `build_top_line_backfill` must never
    read.

    `"form": "10-K"` is LOAD-BEARING, not decoration. Since the producer fix,
    `build_top_line_backfill` gates each row on its carrier form
    (`_TOP_LINE_ANNUAL_CARRIER_FORMS`, currently exactly `{"10-K": "FY"}`)
    BEFORE it reaches the `_is_near_new_year_boundary` check, so a row on any
    other form is skipped as `carrier_form_not_allowlisted` and the
    near-New-Year tests below would never reach the behaviour they claim to
    pin. Mutating it to "10-Q" fails them, which is how that was confirmed
    rather than assumed.

    Note the allowlist is narrower than "annual": the captured form domain
    (`tests/data/fixtures/companyconcept_form_domain_2026-07-25.json`, 32
    observations over 8 filers, 2026-07-25) shows annual-span rows also
    arriving on `20-F` and `20-F/A`, which are annual reports the allowlist
    still excludes — which is why the skip type names the ALLOWLIST rather
    than annual-ness. Any claim here about that domain comes from that
    capture, not from prose.

    (Cited by SYMBOL, not line: `sec_edgar_client.py` is large and actively
    edited, so its line numbers drift; a stale `:NNNN` in a docstring is the
    kind of quiet falsehood this file exists to avoid.)
    """
    return {
        "start": start, "end": end, "val": value, "accn": accession,
        "form": "10-K", "fy": 2026, "fp": "FY", "filed": filed,
    }


def _build_lane_a_pack(markets_modules, ticker: str, cik: int, rows: list[dict]) -> dict:
    """The pack `pack.py --pack kpi-topline-backfill --ticker <T>` really
    emits: the REAL `pack_kpi_topline_backfill` over the REAL
    `build_top_line_backfill`, with ONLY `resolve_cik`/`fetch_facts` stubbed.
    Nothing about the envelope is asserted or reshaped here -- that is the
    whole point of this file.
    """
    sec_edgar_client, pack_us = markets_modules

    def _fetch(fetched_cik, concept):
        assert fetched_cik == cik
        if concept == _TOP_LINE_CONCEPT_LOCAL:
            return {"data": {"units": {"USD": rows}}}
        return {"error": f"no data for {concept}"}

    with mock.patch.object(
        sec_edgar_client, "resolve_cik", return_value={"cik": cik, "ticker": ticker},
    ), mock.patch.object(sec_edgar_client, "fetch_facts", side_effect=_fetch):
        return pack_us.pack_kpi_topline_backfill(ticker)


def _aapl_lane_a_pack(markets_modules) -> dict:
    """AAPL's Lane A pack: the shared FY2025 year (captured verbatim) plus ONE
    older year Lane B does not cover (counterfactual WINDOW only)."""
    sample = _probe_flat_sample("AAPL")
    accession = _probe_record("AAPL")["accession"]
    older_start, older_end = _AAPL_LANE_A_ONLY_WINDOW
    rows = [
        _companyconcept_row(
            start=sample["period_start"], end=sample["period_end"],
            value=sample["value"], accession=accession, filed=_AAPL_FILED,
        ),
        _companyconcept_row(
            start=older_start, end=older_end,
            value=sample["value"], accession=accession, filed=_AAPL_FILED,
        ),
    ]
    return _build_lane_a_pack(markets_modules, "AAPL", _AAPL_CIK, rows)


def _intc_lane_a_pack(markets_modules, window: tuple[str, str] | None = None) -> dict:
    """INTC's Lane A pack over ONE annual window. The default is its REAL
    captured FY2025 window, ending 2025-12-27 -- 5 days BEFORE Jan 1, and
    therefore KEPT: the New-Year guard is one-sided (see the module
    docstring's probe table), and both lanes label this year 2025. Pass
    `_INTC_NEW_YEAR_CROSSING_WINDOW` for the after-Jan-1 case Lane A skips.
    """
    sample = _probe_flat_sample("INTC")
    start, end = window or (sample["period_start"], sample["period_end"])
    rows = [
        _companyconcept_row(
            start=start, end=end,
            value=sample["value"], accession=_probe_record("INTC")["accession"],
            filed=_INTC_FILED,
        ),
    ]
    return _build_lane_a_pack(markets_modules, "INTC", _INTC_CIK, rows)


# --------------------------------------------------------------------------
# Shipped-CLI drivers (no chain logic re-implemented in the test)
# --------------------------------------------------------------------------

def _isolated_env(store_dir: Path) -> dict:
    return {
        **os.environ,
        "KPI_STORE_DIR": str(store_dir),
        # Explicit so a standalone run cannot write __pycache__ into the skill
        # dirs (the CLIs import same-dir modules).
        "PYTHONDONTWRITEBYTECODE": "1",
    }


def _ingest(pack: dict, path: Path, env: dict) -> subprocess.CompletedProcess:
    path.write_text(json.dumps(pack), encoding="utf-8")
    return subprocess.run(
        ["uv", "run", "--script", str(INGEST_SCRIPT), "ingest", "--pack", str(path)],
        capture_output=True, text=True, timeout=60, env=env,
    )


def _ingest_ok(pack: dict, path: Path, env: dict) -> dict:
    result = _ingest(pack, path, env)
    assert result.returncode == 0, (
        f"ingest failed: stdout={result.stdout!r} stderr={result.stderr!r}"
    )
    return json.loads(result.stdout)


def _dump(company: str, env: dict) -> dict:
    result = subprocess.run(
        ["uv", "run", "--script", str(KPI_STORE_SCRIPT), "dump", "--company", company],
        capture_output=True, text=True, timeout=60, env=env,
    )
    assert result.returncode == 0, (
        f"dump failed: stdout={result.stdout!r} stderr={result.stderr!r}"
    )
    return json.loads(result.stdout)


def _series(dump: dict, kpi_id: str) -> dict:
    for series in dump["series"]:
        if series["kpi_id"] == kpi_id:
            return series
    raise AssertionError(
        f"dump carries no {kpi_id!r} series; got {[s['kpi_id'] for s in dump['series']]}"
    )


def _period_entry(series: dict, period: str) -> dict:
    """The dump's entry for one fiscal period. Entries are grouped by
    `same_period` (the RAW date pair), NOT by the display label, and each
    records every distinct label observed under `period_labels` — which is
    precisely why a lane that labelled the shared year differently would show
    up here as a SECOND label on the one entry rather than a second entry.
    """
    matches = [entry for entry in series["periods"] if period in entry["period_labels"]]
    if len(matches) != 1:
        raise AssertionError(
            f"series {series['kpi_id']!r} must carry exactly one entry labelled "
            f"{period!r}; got {[e['period_labels'] for e in series['periods']]}"
        )
    return matches[0]


def _table_row(rendered: str, kpi_id: str) -> str:
    """The tearsheet's Markdown TABLE row whose first cell is `kpi_id`.

    Scoped deliberately: a bare `kpi_id in rendered` substring check is also
    satisfied by the `## Revisions` heading or any legend, so it cannot tell a
    rendered row from a mention. Matching `| <kpi_id> |` at line start pins the
    row itself, which is what lets the caller assert the figure and the id
    appear TOGETHER.
    """
    prefix = f"| {kpi_id} |"
    matches = [line for line in rendered.splitlines() if line.startswith(prefix)]
    if len(matches) != 1:
        raise AssertionError(
            f"expected exactly one rendered table row for {kpi_id!r}; "
            f"got {matches} in:\n{rendered}"
        )
    return matches[0]


def _stored_points(store_dir: Path) -> list[dict]:
    """Every point durably written under `store_dir`, read straight off disk
    (the series filename embeds a digest of (company, kpi_id), so glob)."""
    points: list[dict] = []
    for path in sorted(store_dir.glob("*.json")):
        points.extend(json.loads(path.read_text(encoding="utf-8"))["points"])
    return points


@pytest.fixture
def aapl_both_lanes(tmp_path, markets_modules):
    """AAPL ingested through BOTH lanes, Lane B first, into an isolated store.
    Returns `(store_dir, env)`.

    Both summaries are asserted here so no test downstream can pass vacuously
    on Lane B's points alone: Lane A must really have produced both of its
    years under the canonical series.
    """
    store_dir = tmp_path / "store"
    env = _isolated_env(store_dir)

    lane_b = _ingest_ok(_aapl_lane_b_pack(), tmp_path / "aapl-lane-b.json", env)
    assert lane_b == {"company": "AAPL", "kpi_ids": ["total_revenue"], "appended": 1}, lane_b

    lane_a = _ingest_ok(_aapl_lane_a_pack(markets_modules), tmp_path / "aapl-lane-a.json", env)
    assert lane_a == {"company": "AAPL", "kpi_ids": ["total_revenue"], "appended": 2}, lane_a

    return store_dir, env


# --------------------------------------------------------------------------
# (a) A fiscal year covered by BOTH lanes -- ordinary filer, FYE far from Jan 1
# --------------------------------------------------------------------------

def test_shared_fiscal_year_resolves_to_the_same_value_from_both_lanes(aapl_both_lanes):
    """AAPL's FY2025 is covered by Lane B (per-filing parse) AND Lane A
    (companyconcept backfill). Both must land the SAME captured value in the
    one `total_revenue` series, with NO disagreement -- brief Smallest End
    State #3's first clause. AAPL's FYE (2025-09-27) is ~3 months from Jan 1,
    so Lane A does not skip it and the year is genuinely shared.
    """
    _, env = aapl_both_lanes
    entry = _period_entry(_series(_dump("AAPL", env), "total_revenue"), "2025")

    captured = _probe_flat_sample("AAPL")["value"]
    assert {obs["value"] for obs in entry["observations"]} == {captured}, (
        f"both lanes must resolve FY2025 to the captured {captured!r}; got {entry}"
    )
    # Asserted as a CONSEQUENCE, not as the guard: after dedup this entry holds
    # one observation, and `disagreement` needs >=2 observations AND >=2
    # distinct canonical values (`kpi_store.py:526`), so this direction cannot
    # fail here. The fires-loudly direction -- a genuine cross-lane value
    # disagreement raising at ingest -- is owned by
    # `test_kpi_xbrl_ingest.py::test_cross_lane_value_disagreement_raises`.
    assert entry["disagreement"] is False, (
        f"two agreeing lanes must not flag a restatement dagger; got {entry}"
    )


def test_shared_fiscal_year_carries_the_identical_period_label_from_both_lanes(
    aapl_both_lanes,
):
    """The two lanes derive the fiscal-year label by DIFFERENT rules -- Lane B
    from the filing's dei calendar, Lane A from the period-end year -- so a
    divergent label would give them different dedup keys, hide them from the
    cross-lane disagreement guard, and mint a fabricated second point for one
    fiscal year.

    The store groups a period by its RAW date pair and records every distinct
    label it saw under `period_labels`, so divergence is directly observable:
    ONE label means the two lanes agreed, and the shared year is consequently
    held by exactly ONE point.
    """
    store_dir, env = aapl_both_lanes
    entry = _period_entry(_series(_dump("AAPL", env), "total_revenue"), "2025")
    assert entry["period_labels"] == ["2025"], (
        f"both lanes must label AAPL's shared fiscal year identically; got {entry}"
    )

    fy2025 = [
        point for point in _stored_points(store_dir)
        if point["kpi_id"] == "total_revenue" and point["period"] == "2025"
    ]
    assert len(fy2025) == 1, (
        "agreeing labels mean coinciding dedup keys, so ONE point is stored; "
        f"got {fy2025}"
    )


# --------------------------------------------------------------------------
# (b)/(c) Lane-A-only years, and each lane's own provenance
# --------------------------------------------------------------------------

def test_lane_a_only_fiscal_year_joins_the_same_total_revenue_series(aapl_both_lanes):
    """The older year only Lane A covers lands in the SAME `total_revenue`
    series as the shared year -- brief Smallest End State #2 (the backfill
    fills years older than the filings Lane B fetched, appended to the same
    series), not a second parallel series.
    """
    _, env = aapl_both_lanes
    series = _series(_dump("AAPL", env), "total_revenue")
    labels = sorted(label for entry in series["periods"] for label in entry["period_labels"])
    assert labels == ["2024", "2025"], series


def test_lane_a_only_point_carries_companyfacts_provenance(aapl_both_lanes):
    """Lane A's pack declares `source_kind: "xbrl-companyfacts"` on its
    envelope; Lane B declares none and defaults to `"xbrl-topline"`. The
    shared year is written by whichever lane got there first (identical dedup
    key + identical value = a store no-op), so provenance is asserted where it
    is unambiguous: the Lane-A-only year must carry the companyfacts label.
    """
    store_dir, _ = aapl_both_lanes
    by_period = {
        point["period"]: point["source_kind"]
        for point in _stored_points(store_dir)
        if point["kpi_id"] == "total_revenue"
    }
    assert by_period["2024"] == "xbrl-companyfacts", by_period
    assert by_period["2025"] == "xbrl-topline", by_period


def test_lane_b_pack_assigns_provenance_per_lane_in_one_ingest(tmp_path):
    """A Lane B pack carries BOTH kinds of fact, so one pack-wide label would
    be wrong for half of it: in the SAME ingest call the dimensional points
    must stay `"xbrl-dimensional"` while the flat top-line points take
    `"xbrl-topline"`.
    """
    store_dir = tmp_path / "store"
    env = _isolated_env(store_dir)
    _ingest_ok(_intc_lane_b_pack(), tmp_path / "intc-lane-b.json", env)

    by_lane: dict[bool, set] = {}
    for point in _stored_points(store_dir):
        by_lane.setdefault(point["kpi_id"] == "total_revenue", set()).add(
            point["source_kind"]
        )
    assert by_lane[False] == {"xbrl-dimensional"}, by_lane
    assert by_lane[True] == {"xbrl-topline"}, by_lane


# --------------------------------------------------------------------------
# The near-New-Year filer, both sides of Jan 1: the CROSSING row is skipped
# (that skip is what guarantees label agreement), the DECEMBER row is not
# --------------------------------------------------------------------------

def test_new_year_crossing_filer_lane_a_skips_with_a_named_reason(markets_modules):
    """The counterfactual 52/53-week roll ends 2026-01-03 -- inside
    `FISCAL_BOUNDARY_TOLERANCE_DAYS` AFTER Jan 1, the ONE side where Lane A's
    period-end-year rule diverges from Lane B's dei walk (2026 against 2025)
    and Lane A has no dei calendar to check against. It must emit a NAMED
    coverage skip and NO fact, never a guessed (and divergently-labelled) point.

    THE HAZARD IS ONE-SIDED. INTC's REAL year-end, 2025-12-27, is equally close
    to Jan 1 and is NOT skipped: Lane B's walk to the first nominal fiscal-year
    end at-or-after `period_end` answers 2025 there, exactly as Lane A's
    period-end-year rule does. That case is pinned in the opposite direction by
    `test_december_year_end_filer_is_backfilled_and_agrees_with_lane_b`.
    """
    pack = _intc_lane_a_pack(markets_modules, _INTC_NEW_YEAR_CROSSING_WINDOW)

    assert pack["facts"] == [], (
        f"Lane A must not label a New-Year-crossing annual row; got {pack['facts']}"
    )
    skipped = pack["coverage"]["skipped_rows"]
    reasons = [row["type"] for row in skipped]
    assert reasons == ["new_year_boundary_ambiguous"], skipped
    assert _INTC_NEW_YEAR_CROSSING_WINDOW[1] in skipped[0]["reason"], skipped


def test_december_year_end_filer_is_backfilled_and_agrees_with_lane_b(
    tmp_path, markets_modules,
):
    """INTC's REAL captured fiscal year ends 2025-12-27 -- 5 days before Jan 1,
    and the shape most of the US market files. Lane A must BACKFILL it, and the
    label it derives must coincide with Lane B's, so the year lands as exactly
    ONE point under ONE label.

    This is the December-FYE half of the asymmetry, end-to-end. A guard that
    fired on this side too would leave the whole assertion vacuous the quiet
    way: Lane A would contribute nothing, the single point would be Lane B's
    alone, and the arc's headline capability (a general history backfill) would
    be silently unavailable to every December-fiscal-year-end filer.
    """
    store_dir = tmp_path / "store"
    env = _isolated_env(store_dir)
    _ingest_ok(_intc_lane_b_pack(), tmp_path / "intc-lane-b.json", env)
    lane_a = _ingest_ok(
        _intc_lane_a_pack(markets_modules), tmp_path / "intc-lane-a.json", env,
    )
    # Asserted on the LANE A summary, not only on the merged store: it is the
    # one place a silent zero-fact backfill cannot hide behind Lane B's point.
    assert lane_a == {
        "company": "INTC", "kpi_ids": ["total_revenue"], "appended": 1,
    }, lane_a

    entry = _period_entry(_series(_dump("INTC", env), "total_revenue"), "2025")
    assert entry["period_labels"] == ["2025"], (
        f"a December year-end must get the SAME label from both lanes; got {entry}"
    )
    top_line = [
        point for point in _stored_points(store_dir)
        if point["kpi_id"] == "total_revenue"
    ]
    assert len(top_line) == 1, (
        f"agreeing labels mean coinciding dedup keys, so ONE point; got {top_line}"
    )
    assert entry["disagreement"] is False, (
        f"two agreeing lanes must not flag a restatement dagger; got {entry}"
    )


def test_near_new_year_skip_leaves_lane_b_the_sole_authority(tmp_path, markets_modules):
    """The consequence of that skip, end-to-end, on the ONE shape where the two
    lanes could actually disagree: a fiscal year the filing's dei calendar calls
    2025 but whose period ENDS in calendar 2026. Lane A's rule would label it
    2026; because it skips instead, the series carries exactly ONE point under
    Lane B's single label -- so one filing can never mint a fabricated
    restatement dagger out of a labelling disagreement with itself.

    THE WINDOW HERE IS CONSTRUCTED, and it has to be: no filer in the captured
    probe has a fiscal year that rolls past New Year, and INTC's real year-end
    (2025-12-27) makes BOTH labelling rules answer 2025, so the divergence this
    test exists to rule out cannot arise from captured data alone. Only the
    window and its dei label are constructed -- value, concept and accession
    stay INTC's real capture. See `_INTC_NEW_YEAR_CROSSING_WINDOW` and the
    module docstring's provenance ledger (item 2 and 3).
    """
    store_dir = tmp_path / "store"
    env = _isolated_env(store_dir)
    _ingest_ok(
        _intc_lane_b_pack(
            window=_INTC_NEW_YEAR_CROSSING_WINDOW,
            fiscal_year=_INTC_NEW_YEAR_CROSSING_DEI_LABEL,
        ),
        tmp_path / "intc-lane-b.json",
        env,
    )
    _ingest_ok(
        _intc_lane_a_pack(markets_modules, _INTC_NEW_YEAR_CROSSING_WINDOW),
        tmp_path / "intc-lane-a.json",
        env,
    )

    top_line = [
        point for point in _stored_points(store_dir)
        if point["kpi_id"] == "total_revenue"
    ]
    assert len(top_line) == 1, (
        f"Lane B must remain the sole authority for INTC's fiscal year; got {top_line}"
    )
    assert top_line[0]["source_kind"] == "xbrl-topline", top_line[0]
    assert top_line[0]["value"] == _probe_flat_sample("INTC")["value"], top_line[0]

    entry = _period_entry(_series(_dump("INTC", env), "total_revenue"), "2025")
    assert entry["period_labels"] == ["2025"], (
        f"the skip must leave exactly Lane B's label on the period; got {entry}"
    )
    assert entry["disagreement"] is False, (
        f"a single-lane fiscal year must not flag a restatement; got {entry}"
    )


# --------------------------------------------------------------------------
# (d) The tearsheet renders the total beside the segments, dagger unchanged
# --------------------------------------------------------------------------

def test_tearsheet_renders_total_row_beside_segment_rows(tmp_path):
    """The whole point of the arc, rendered: the canonical `total_revenue` row
    appears in the SAME tearsheet as the dimensional segment row, and the
    shipped restatement behaviour is unchanged -- the real FY2020 CCG recast
    still carries its dagger on the latest vintage and lists both vintages
    under `## Revisions`, while the single-vintage total row carries NO dagger
    (no fabricated restatement).
    """
    store_dir = tmp_path / "store"
    env = _isolated_env(store_dir)
    summary = _ingest_ok(_intc_lane_b_pack(), tmp_path / "intc-lane-b.json", env)

    segment_ids = [kpi_id for kpi_id in summary["kpi_ids"] if kpi_id != "total_revenue"]
    assert len(segment_ids) == 1, summary

    dump_path = tmp_path / "intc-dump.json"
    dump_path.write_text(json.dumps(_dump("INTC", env)), encoding="utf-8")
    render = subprocess.run(
        [sys.executable, str(TEARSHEET_SCRIPT), "--in", str(dump_path),
         "--as-of", "2026-06-01"],
        capture_output=True, text=True, timeout=60,
    )
    assert render.returncode == 0, render.stderr
    out = render.stdout

    # Both rows are rendered, each carrying its OWN figure -- asserted on the
    # row rather than on the whole document, so a heading or legend mentioning
    # the id cannot satisfy it.
    total_row = _table_row(out, "total_revenue")
    segment_row = _table_row(out, segment_ids[0])

    # The shipped dagger behaviour, unchanged (same assertion arc (d)'s e2e
    # makes): the latest FY2020 vintage is marked, the superseded one is not.
    assert "40,535,000,000†" in segment_row, segment_row
    assert "40,057,000,000†" not in out, out
    assert "## Revisions" in out, out

    # ...and the total row, having ONE vintage, carries its figure unmarked.
    captured = f"{int(_probe_flat_sample('INTC')['value']):,}"
    assert captured in total_row, total_row
    assert f"{captured}†" not in out, out
