#!/usr/bin/env python3
# /// script
# requires-python = ">=3.10"
# dependencies = []
# ///
"""
XBRL fact -> kpi_store point adapter (operational-kpi tier-② XBRL pilot).

Layer 2 (Analysis) PURE-COMPUTE — mirrors kpi_parse.py / kpi_validate.py:
stdlib only, dict-in -> dict-out. This module is NOT a durable store: it
does NOT import `_store_fs`, does NOT resolve a store dir, does NOT lock
or write files, and touches neither the network nor an LLM.

`facts_to_points(fact_pack, kpi_id, match, company, source_kind)` selects
every fact in `fact_pack["facts"]` matching `match` (a
`{"concept", "dimensions"}` selector — `dimensions` compared by dict
EQUALITY, so an absent/empty `dimensions` matches only a flat fact's own
empty `dimensions`, i.e. the top-level total) and maps each matched fact
into a kpi_store-shaped point:

  - `source_accession` = fact `accession`
  - `source_form`      = "10-K" | "10-Q" (Task 9), threaded from the
                          pack's per-accession `fiscal_calendars` dei read:
                          `fiscal_period_focus` FY -> 10-K, Q1..Q4 -> 10-Q —
                          the form is a property of the carrying FILING
                          (keyed by accession), never guessed from a fact's
                          own duration (a 10-K carries 3mo comparatives). A
                          fact whose form cannot be grounded (no calendar
                          entry / unreadable focus) is REJECTED loud naming
                          the accession — never emitted formless.
                          PROVENANCE SHAPES (Task 9 ratifies T8's
                          anti-masquerade choice): a REPORTED point carries
                          the SINGULAR `source_accession`/`source_form`; a
                          DERIVED point (derive_q4_points) carries ONLY the
                          PLURAL `source_accessions`/`source_forms` (aligned
                          pairwise) — a consumer reading the singular keys
                          can never silently receive a computed value.
  - `source_table_id`  = `"xbrl:dimensional"` (fact has real breakdown
                          axes) or `"xbrl:companyfacts"` (fact `dimensions`
                          is empty, flat)
  - `source_cell_ref`  = `concept` (flat) or
                          `concept + "|" + <stable-sorted "axis=member" join>`
                          (dimensional, e.g.
                          `"concept|ProductOrService=StreamingMember"`)
  - `as_of`            = fact `filed`
  - `period`           = the fact's EMITTED `fiscal_year` label (Task 5,
                          docs/loom/plans/2026-07-16-operational-kpi-quarterly.md
                          — the data layer derives it per-fact from the fact's
                          own period_end against the filing's dei calendar,
                          dei-grounded and fail-loud; this module is a pure
                          CONSUMER of that label and never re-derives fiscal
                          geometry). NEVER `period_end[:4]` — that is the
                          CALENDAR year (the scope-B ruled latent bug: NVDA
                          FY2026-Q3 ends 2025-10-26), carried instead on each
                          point as the honest `calendar_year`/`calendar_quarter`
                          pair (the calendarization basis). And STILL never
                          edgartools' raw `fiscal_year` dataframe COLUMN, which
                          mislabels prior-year comparatives — the historical
                          trap holds; our derived label is distinguished from
                          that column by the full emitted label group
                          (`fiscal_year` + `fiscal_quarter` + `duration_months`):
                          a fact carrying a bare `fiscal_year` without its group
                          is treated as unclassifiable, never trusted.
  - `period_type`      = classified from the emitted labels (Task 5):
                          `fiscal_quarter` (Q1|Q2|Q3|Q4|FY) consumed as-is,
                          with `duration_class` (3mo|6mo-YTD|9mo-YTD|12mo-FY)
                          and the `cumulative` flag derived from
                          `duration_months` — see `classify_fact_period`.
  - `value`            = fact `value`
  - plus `company`, `kpi_id`, `source_kind`

The CORE property is FAIL-LOUD (mirrors kpi_parse's UnparseableCell
discipline): a matched fact missing `value`/`accession`/`filed`/`period_end`,
carrying a non-numeric `value`, or a malformed (non-YYYY-MM-DD) `period_end`,
RAISES a distinct `ValueError` naming the offending field — this module
never emits a fabricated `0` or a period `"None"`. A true numeric `0` is a
real value, not a missing one. Two further fail-loud branches (Task 5):
(a) a fact pack carrying an `error`/`error_class` slot (e.g. the
foreign-private-issuer `foreign_private_issuer_no_quarterly_xbrl` N/A) is
branched on BEFORE `facts` is read — it RAISES, never consumed as a real
empty series; (b) a fact missing the emitted label group (a pre-schema
stub, or a filing whose per-filing dei calendar was unreadable/None) is
surfaced as UNCLASSIFIABLE — never guessed from period_end/calendar
position, never keyed by the calendar year.

Task 7 extends `build_series_with_break` with the single-granularity view
(annual vs quarterly, never mixed), the fiscal-range output filter on each
fact's OWN emitted fiscal label, and the `no_quarterly_coverage` coverage
flag — delegated to the data layer's pure `_dimension_quarterly_absence`
via a deliberate FUNCTION-LEVEL import (module-level imports here stay
stdlib + kpi_series so the module remains offline-importable; see
`_dimension_quarterly_absence_flags`).

Task 8 adds `derive_q4_points`: an untagged Q4 single-quarter is DERIVED
as (FY total − 9mo-YTD) over resolve_binding's output points — flagged
computed (DQC `derived_q4`, BOTH contributing accessions recorded),
carried in a SEGREGATED lane (`derived: True`; `build_series_with_break
(..., reported_only=True)` excludes it), skipped-and-surfaced when a
source is missing, and REFUSED (`q4_basis_mismatch`, a flag DISTINCT
from the clean derived flag) when the inputs differ in restatement
vintage, XBRL unit/scale, or their source filings' declared fiscal
calendars — never a silent subtraction across incompatible bases.

Task 6 adds a thin argparse CLI (`build`), mirroring `kpi_memo_feed.py`'s
CLI shape and fail-loud exit-code convention: reads a fact-pack JSON from
`--file`/stdin and a binding JSON from `--binding`, calls `resolve_binding`
and prints the resulting points. 0 on success; 1 on a `resolve_binding`
ValueError (e.g. ambiguous binding); 2 on malformed or non-object
fact-pack JSON (nothing computed, no raw traceback).

Task 2 (docs/loom/plans/2026-07-18-memo-quarterly-kpi-wiring.md) adds
`build_quarterly_series` + the `quarterly-series` subcommand: PER
full-dimensional-signature group present in the fact-pack (concept +
whole `dimensions` map + the normalized consolidation QUALIFIER — never
one axis member, per docs/loom/memory/match-kpi-on-full-dimensional-
signature-not-one-axis.md; no binding config needed), it ORCHESTRATES
the existing chain `resolve_binding` -> `derive_q4_points` ->
`build_series_with_break(granularity="quarterly", facts=<group>)` and
prints `{series: [{signature, points, derived_points, gaps}],
coverage_flags}` — parallel calendar/fiscal labels intact on every
point, derived points still carrying `derived: True` + the PLURAL
`source_accessions`/`source_forms`. Same exit-code convention as
`build`. NOTE: the coverage-flag path lazily imports the data layer
(sec_edgar_client -> `import requests`), so running THIS subcommand
under a bare `uv run --script` isolated env (dependencies=[]) requires
an interpreter env where `requests` is importable.
"""
from __future__ import annotations

import argparse
import json
import sys
from datetime import date, timedelta
from pathlib import Path

# Resolve same-dir modules without a package (mirrors kpi_series.py's own
# import shim for kpi_break) so `import kpi_series` works both under
# `uv run --script` and importlib test loading. Only kpi_series is
# imported — NOT kpi_break: the declared/pre-applied break here
# intentionally bypasses kpi_break's persisted FLAGGED->CONFIRMED->APPLIED
# review-queue lifecycle.
_SCRIPT_DIR = Path(__file__).resolve().parent
if str(_SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(_SCRIPT_DIR))
import kpi_series  # noqa: E402


_DEFAULT_CONSOLIDATION_MEMBER = "OperatingSegmentsMember"

# Task 5 (scope B quarterly): period_type is CLASSIFIED from the data
# layer's emitted labels — `fiscal_quarter` ∈ {Q1..Q4, FY} consumed as-is,
# `duration_class` + the cumulative flag mapped from `duration_months`.
# The producer derives fiscal_quarter JOINTLY with the duration (a
# 12-month fact is FY, never a bare Q4), so the two must agree here.
_DURATION_CLASS_BY_MONTHS = {3: "3mo", 6: "6mo-YTD", 9: "9mo-YTD", 12: "12mo-FY"}
_CUMULATIVE_DURATION_CLASSES = frozenset({"6mo-YTD", "9mo-YTD"})
_FISCAL_QUARTERS = frozenset({"Q1", "Q2", "Q3", "Q4", "FY"})

# Task 3 (docs/loom/plans/2026-07-18-52-53-week-filer-support.md): week-lane
# `duration_class` string morphology, keyed by the SHARED `_WEEK_BANDS`
# label (sec_edgar_client.py) — follows the shipped month-lane pattern
# ("9mo-YTD"/"12mo-FY"): a single-quarter-length band gets no suffix
# ("16wk"), a YTD cumulative gets "-YTD" ("36wk-YTD"), the FY band gets
# "-FY" ("52wk-FY"). Only "week-Q4" (16/17wk) and "YTD-through-Q3" (36wk)
# are ever actually reached in practice — "quarter"/"H1"/"FY" band members
# already round into the month lane, which has precedence (plan Notes:
# class-lane precedence) — but the map covers every shipped band label so
# a genuine miss is never silently unmapped.
_WEEK_LANE_DURATION_CLASS_FORMAT = {
    "quarter": "{weeks}wk",
    "week-Q4": "{weeks}wk",
    "H1": "{weeks}wk-YTD",
    "YTD-through-Q3": "{weeks}wk-YTD",
    "FY": "{weeks}wk-FY",
}


def _week_lane_duration_class(week_lane_band, duration_weeks) -> str | None:
    """Fallback week-lane `duration_class` lookup (Task 3) — consulted by
    `classify_fact_period` ONLY when `duration_months` misses the month
    lane (class-lane precedence, plan Notes: the month map is tried
    first).

    Fix round 2 (spec-reviewer NEEDS_REVISION on 111e4530): this is now a
    PURE TRANSCRIPTION of the producer's OWN classification decision —
    `week_lane_band` is `sec_edgar_client._build_dimensional_revenue_fact`'s
    emitted `_week_lane_class(span_days)` result (the SAME tight
    [weeks*7-1, weeks*7] window Gate P's day-span classification uses).
    The ORIGINAL implementation instead re-decided membership from
    `duration_weeks` (the producer's ALREADY-ROUNDED int, `_week_count`)
    via exact membership in a band's week-count tuple — but
    `duration_weeks = round(span_days / 7)` has up to +-3d slop, WIDER
    than `_week_lane_class`'s tight window: a 253-day span rounds to 36
    weeks (matching the old int check) even though `_week_lane_class(253)`
    returns None (253 is outside the genuine 251/252-day window),
    reproducing the exact edgartools #816 two-path desync the shared
    `_week_lane_class` primitive exists to prevent (docs/loom/plans/
    2026-07-18-52-53-week-filer-support.md, plan Notes: ONE shared
    classification decision, never a second copy re-derived here).

    Returns None (fail-closed, never guessed) when `week_lane_band` is
    missing/unrecognized (the producer made no week-lane claim — or the
    fact predates this field) or `duration_weeks` is missing/non-int."""
    if week_lane_band not in _WEEK_LANE_DURATION_CLASS_FORMAT:
        return None
    if not isinstance(duration_weeks, int) or isinstance(duration_weeks, bool):
        return None
    return _WEEK_LANE_DURATION_CLASS_FORMAT[week_lane_band].format(weeks=duration_weeks)


def _is_cumulative_duration_class(duration_class: str) -> bool:
    """True for a YTD cumulative `duration_class` on EITHER lane — the
    month lane's fixed set, or any week-lane class ending "wk-YTD" (Task
    3; the format table above is the only producer of that suffix)."""
    return duration_class in _CUMULATIVE_DURATION_CLASSES or duration_class.endswith(
        "wk-YTD"
    )


def _is_fy_duration_class(duration_class: str) -> bool:
    """True for an FY `duration_class` on EITHER lane — the month lane's
    "12mo-FY", or a week-lane class ending "wk-FY" (Task 3)."""
    return duration_class == "12mo-FY" or duration_class.endswith("wk-FY")

# Task 9: a filing's SEC form derives from its own dei cover tag
# `DocumentFiscalPeriodFocus` (threaded through the pack's per-accession
# `fiscal_calendars`): an annual report declares FY, a quarterly report
# declares its quarter. Anything else is unreadable — rejected, never guessed.
_SOURCE_FORM_BY_FOCUS = {
    "FY": "10-K", "Q1": "10-Q", "Q2": "10-Q", "Q3": "10-Q", "Q4": "10-Q",
}

# The ONE DQC-flag schema (plan kickoff decision, docs/loom/plans/
# 2026-07-16-operational-kpi-quarterly.md: 'all instances of the ONE
# existing DQC schema (type, old, new, accessions, reason) — no per-class
# schema variants'). Flags MAY carry additional locating fields (period,
# source_cell_ref, the identifying signature) on top of the required five.
_DQC_REQUIRED_KEYS = ("type", "old", "new", "accessions", "reason")


def assert_dqc_schema(flag: dict) -> dict:
    """Validate one DQC flag against the ONE schema — `{type, old, new,
    accessions, reason}` (Task 9): `type` a non-empty str, `accessions` a
    non-empty list of non-empty accession strs, `reason` a non-empty str;
    `old`/`new` present (None is a legal value for flag classes with no
    old/new pair). Extra LOCATING fields are allowed; missing required
    fields — including the retired restatement shape's
    superseded_accession/kept_accession in place of `accessions` — RAISE.
    Called at every analysis-layer emission site (self-enforcing schema)
    and exported for tests/consumers."""
    if not isinstance(flag, dict):
        raise ValueError(
            f"kpi_xbrl.assert_dqc_schema: DQC flag must be a dict, got "
            f"{type(flag).__name__}"
        )
    missing = [key for key in _DQC_REQUIRED_KEYS if key not in flag]
    if missing:
        raise ValueError(
            f"kpi_xbrl.assert_dqc_schema: DQC flag (type="
            f"{flag.get('type')!r}) is missing required field(s) {missing} "
            f"— every flag follows the ONE schema {list(_DQC_REQUIRED_KEYS)}"
        )
    if not isinstance(flag["type"], str) or not flag["type"]:
        raise ValueError(
            f"kpi_xbrl.assert_dqc_schema: DQC flag 'type' must be a "
            f"non-empty str, got {flag['type']!r}"
        )
    accessions = flag["accessions"]
    if (
        not isinstance(accessions, list)
        or not accessions
        or not all(isinstance(a, str) and a for a in accessions)
    ):
        raise ValueError(
            f"kpi_xbrl.assert_dqc_schema: DQC flag (type={flag['type']!r}) "
            f"'accessions' must be a non-empty list of accession strings, "
            f"got {accessions!r}"
        )
    if not isinstance(flag["reason"], str) or not flag["reason"]:
        raise ValueError(
            f"kpi_xbrl.assert_dqc_schema: DQC flag (type={flag['type']!r}) "
            f"'reason' must be a non-empty str, got {flag['reason']!r}"
        )
    return flag


def _require_source_form(fact: dict, fiscal_calendars: dict | None) -> str:
    """The carrying filing's SEC form ("10-K" | "10-Q"), threaded from the
    pack's `fiscal_calendars[accession]["fiscal_period_focus"]` (Task 9).
    The form is a FILING property: a 10-K's prior-year 3mo comparative is
    still 10-K-sourced, so the fact's own duration/quarter labels can never
    stand in. Fails loud naming the accession when the pack carries no
    readable focus for it — a point is never emitted formless."""
    accession = fact.get("accession")
    calendar = (fiscal_calendars or {}).get(accession) or {}
    focus = calendar.get("fiscal_period_focus")
    form = _SOURCE_FORM_BY_FOCUS.get(focus)
    if form is None:
        raise ValueError(
            f"kpi_xbrl.facts_to_points: fact's source form is underivable — "
            f"the pack's fiscal_calendars carries no readable dei "
            f"fiscal_period_focus for accession {accession!r} "
            f"(focus={focus!r}, concept={fact.get('concept')!r}) — rejected, "
            f"never emitted formless and never guessed from the fact's own "
            f"duration"
        )
    return form


def _unclassifiable(fact: dict, reason: str) -> ValueError:
    """A distinct, loud unclassifiable-fact error (spec: 'a transition or
    unclassifiable period is surfaced, not guessed'): the fact is SURFACED
    by name — period_type is never inferred from period_end/calendar
    position, the period key is never `period_end[:4]` (the calendar year),
    and a bare `fiscal_year` without its emitted label group (the old
    edgartools raw-column shape, unreliable for comparatives) is never
    trusted."""
    return ValueError(
        f"kpi_xbrl: fact is unclassifiable — {reason} "
        f"(concept={fact.get('concept')!r}, period_end="
        f"{fact.get('period_end')!r}, accession={fact.get('accession')!r}) "
        f"— surfaced, never guessed: no period_type is inferred and the "
        f"calendar year is never keyed in its place"
    )


def classify_fact_period(fact: dict) -> dict:
    """Classify one fact's `{period_type, cumulative, duration_class}` by
    CONSUMING the data layer's emitted label group — `fiscal_quarter` +
    `duration_months` + `fiscal_year` (Task 5; rebuild-findings §RESOLVED:
    the data layer derives, the analysis layer consumes — fiscal geometry
    is NEVER re-derived here). A comparative fact classifies from its OWN
    labels (the producer derives them per-fact, never the filing focus).

    Raises the distinct unclassifiable `ValueError` when the label group is
    missing/invalid (a pre-schema stub pack, or a filing whose dei calendar
    was unreadable — e.g. a `None` entry in the pack's `fiscal_calendars`
    leaves its facts with no derivable labels) or internally inconsistent
    (FY without a 12-month duration or vice versa — the producer derives
    them jointly, so disagreement is producer corruption, surfaced rather
    than resolved by guessing which label to trust)."""
    fiscal_year = fact.get("fiscal_year")
    fiscal_quarter = fact.get("fiscal_quarter")
    duration_months = fact.get("duration_months")
    if not isinstance(fiscal_year, int) or isinstance(fiscal_year, bool):
        raise _unclassifiable(fact, "missing/non-integer emitted fiscal_year label")
    if fiscal_quarter not in _FISCAL_QUARTERS:
        raise _unclassifiable(
            fact,
            f"missing/unknown emitted fiscal_quarter label ({fiscal_quarter!r})",
        )
    duration_class = _DURATION_CLASS_BY_MONTHS.get(duration_months)
    if duration_class is None:
        # Class-lane precedence (plan Notes): the month map is tried
        # FIRST; only on a miss does the week lane get a chance, via the
        # fact's own emitted `duration_weeks` (Task 3).
        duration_class = _week_lane_duration_class(
            fact.get("week_lane_band"), fact.get("duration_weeks"),
        )
    if duration_class is None:
        raise _unclassifiable(
            fact,
            f"missing/non-standard duration_months ({duration_months!r}, "
            f"expected one of {sorted(_DURATION_CLASS_BY_MONTHS)}) and no "
            f"week-lane match for duration_weeks "
            f"({fact.get('duration_weeks')!r})",
        )
    if (fiscal_quarter == "FY") != _is_fy_duration_class(duration_class):
        raise _unclassifiable(
            fact,
            f"inconsistent labels: fiscal_quarter={fiscal_quarter!r} with "
            f"duration_class={duration_class!r} (the producer derives them "
            f"jointly — a 12-month fact is FY, never a bare quarter)",
        )
    return {
        "period_type": fiscal_quarter,
        "cumulative": _is_cumulative_duration_class(duration_class),
        "duration_class": duration_class,
    }


def _require_facts(fact_pack: dict) -> list:
    """Read `fact_pack["facts"]` AFTER branching on an explicit error/N-A
    slot (Task 5, Wave-1 review finding): the data layer's gap-slot idiom
    (`error` + `error_class`, e.g. the foreign-private-issuer
    `foreign_private_issuer_no_quarterly_xbrl` N/A, which deliberately
    omits `facts`) must NEVER be consumed as a real empty series by a
    `.get()` default — exactly the silent-empty failure the slot exists to
    prevent (see `_foreign_private_issuer_na_slot`'s contract in
    sec_edgar_client.py)."""
    error_class = fact_pack.get("error_class")
    if error_class is not None or "error" in fact_pack:
        raise ValueError(
            f"kpi_xbrl: fact pack is an explicit error/N-A slot "
            f"(error_class={error_class!r}, identifier="
            f"{fact_pack.get('identifier')!r}): "
            f"{fact_pack.get('reason') or fact_pack.get('error')!r} — "
            f"never consumed as an empty series"
        )
    return fact_pack.get("facts", [])


def _normalize_consolidation(value):
    """Normalize a `consolidation` qualifier (srt:ConsolidationItemsAxis
    member): an absent/None value means the fact/source carries no
    reconciliation tag at all, which defaults to the top-level
    OperatingSegmentsMember view — never a distinct falsy category of its
    own. `consolidation` is a QUALIFIER, not a breakdown axis: it is never
    part of the `dimensions` equality check in `_fact_matches`.
    """
    return value if value else _DEFAULT_CONSOLIDATION_MEMBER


def _fact_matches(fact: dict, match: dict) -> bool:
    """EXACT-match a fact's full dimensional signature against `match` =
    `{concept, dimensions, consolidation}`. `dimensions` is compared by dict
    EQUALITY — a match with an empty/absent `dimensions` matches ONLY a fact
    whose own `dimensions` is empty (the top-level total); a fact carrying
    EXTRA breakdown axes beyond `match`'s does NOT match (de-conflates e.g.
    a NFLX streaming total from its per-region slices). `consolidation` is
    compared separately as a reconciliation QUALIFIER (normalized default
    "OperatingSegmentsMember" on both sides) — it is NEVER folded into the
    `dimensions` signature, so a segment binding is not falsely cross-dim.
    """
    return (
        fact.get("concept") == match.get("concept")
        and fact.get("dimensions", {}) == match.get("dimensions", {})
        and _normalize_consolidation(fact.get("consolidation"))
        == _normalize_consolidation(match.get("consolidation"))
    )


def _require_value(fact: dict) -> float:
    if "value" not in fact or fact["value"] is None:
        raise ValueError(
            f"kpi_xbrl.facts_to_points: fact missing required 'value' "
            f"(concept={fact.get('concept')!r}, fiscal_year="
            f"{fact.get('fiscal_year')!r}) — rejected, never fabricated as 0"
        )
    value = fact["value"]
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise ValueError(
            f"kpi_xbrl.facts_to_points: fact 'value' is non-numeric "
            f"({value!r}, concept={fact.get('concept')!r}, fiscal_year="
            f"{fact.get('fiscal_year')!r}) — rejected, never fabricated as 0"
        )
    return value


def _require_period(fact: dict) -> str:
    """The fact's series period key = its EMITTED `fiscal_year` label
    (Task 5 migration — `period_end[:4]` is the CALENDAR year, the ruled
    latent bug: NVDA's FY2026-Q3 ends 2025-10-26 and must key under 2026).
    Still validates `period_end` (the raw window stays a required,
    well-formed field) and requires the FULL label group via
    `classify_fact_period` — a bare `fiscal_year` without its group is the
    untrusted edgartools raw column, surfaced unclassifiable instead."""
    period_end = fact.get("period_end")
    if not isinstance(period_end, str) or not period_end:
        raise ValueError(
            f"kpi_xbrl.facts_to_points: fact missing required 'period_end' "
            f"(concept={fact.get('concept')!r}) — rejected, never fabricated "
            f'as period "None"'
        )
    try:
        date.fromisoformat(period_end)
    except ValueError:
        raise ValueError(
            f"kpi_xbrl.facts_to_points: fact 'period_end' is malformed "
            f"({period_end!r}, concept={fact.get('concept')!r}) — expected "
            f'YYYY-MM-DD, rejected, never fabricated as period "None"'
        ) from None
    classify_fact_period(fact)  # label-group guard; raises unclassifiable
    return str(fact["fiscal_year"])


def _require_field(fact: dict, field: str) -> str:
    value = fact.get(field)
    if not value:
        raise ValueError(
            f"kpi_xbrl.facts_to_points: fact missing required {field!r} "
            f"(concept={fact.get('concept')!r}, fiscal_year="
            f"{fact.get('fiscal_year')!r}) — rejected, never fabricated"
        )
    return value


def facts_to_points(
    fact_pack: dict,
    kpi_id: str,
    match: dict,
    company: str,
    source_kind: str,
) -> list[dict]:
    """Map every fact in `fact_pack["facts"]` matching `match` into a
    kpi_store-shaped point. See module docstring for the provenance
    mapping and the fail-loud field-by-field taxonomy.
    """
    points = []
    for fact in _require_facts(fact_pack):
        if not _fact_matches(fact, match):
            continue

        value = _require_value(fact)
        accession = _require_field(fact, "accession")
        filed = _require_field(fact, "filed")
        classification = classify_fact_period(fact)
        period = _require_period(fact)
        source_form = _require_source_form(
            fact, fact_pack.get("fiscal_calendars")
        )

        concept = fact.get("concept")
        dimensions = fact.get("dimensions") or {}

        if dimensions:
            source_table_id = "xbrl:dimensional"
            dims_joined = ",".join(f"{k}={v}" for k, v in sorted(dimensions.items()))
            source_cell_ref = f"{concept}|{dims_joined}"
        else:
            source_table_id = "xbrl:companyfacts"
            source_cell_ref = concept

        point = {
            "company": company,
            "kpi_id": kpi_id,
            "period_type": classification["period_type"],
            "cumulative": classification["cumulative"],
            "duration_class": classification["duration_class"],
            "period": period,
            # The parallel CALENDAR basis stays available on every point
            # (cross-company calendarization — rebuild-findings §RESOLVED),
            # honestly named, never conflated with the fiscal period key.
            "calendar_year": fact.get("calendar_year"),
            "calendar_quarter": fact.get("calendar_quarter"),
            # The RAW WINDOW end stays on the point (Task 8: Q4 derivation
            # needs each input's own window; validated by _require_period).
            "period_end": fact["period_end"],
            "as_of": filed,
            "value": value,
            "source_accession": accession,
            "source_form": source_form,
            "source_table_id": source_table_id,
            "source_cell_ref": source_cell_ref,
            "source_kind": source_kind,
        }
        # A fact carrying an XBRL `unit` passes it through (Task 8: the Q4
        # derivation's unit/scale-mismatch guard compares the two inputs'
        # units; the producer emits no unit today — the $-unit gate filters
        # upstream — so the passthrough is the forward-defensive channel).
        if fact.get("unit") is not None:
            point["unit"] = fact["unit"]
        # A fact's own `duration_weeks` (Task 1, sec_edgar_client.py: emitted
        # on EVERY duration fact regardless of lane) passes through onto the
        # point — Task 4's week-lane Q4 derivation needs each input's own
        # week count to compute the derived Q4's duration_weeks (FY_weeks -
        # YTD_weeks).
        if fact.get("duration_weeks") is not None:
            point["duration_weeks"] = fact["duration_weeks"]
        # A cross-filing restatement (overlap policy C, resolved upstream in
        # resolve_binding) tags the kept fact with a machine-readable `dqc`
        # flag; carry it through onto the emitted point unchanged.
        if fact.get("dqc"):
            point["dqc"] = fact["dqc"]
        points.append(point)
    return points


def _reduce_window_group(
    kpi_id: str,
    source: dict,
    fiscal_calendars: dict,
    period_end: str,
    duration_class: str,
    group: list[dict],
) -> dict:
    """Reduce ONE identity window's matched facts (same signature,
    period_end, duration_class — Task 6's duration-qualified key) to
    exactly one representative fact (extracted from `resolve_binding`'s
    dedup loop, Task 9 opportunistic refactor — behavior unchanged):

    - all facts AGREE on value, one fiscal label -> the first fact, as-is;
    - agree on value, labels DIVERGE (two filings' dei calendars label the
      same window differently — FYE drift/change) -> `label_conflict` DQC
      (both labels + both source calendars), later-filed label survives
      deterministically;
    - DISAGREE on value within a SINGLE accession -> intra-filing
      ambiguity, RAISES — never resolved arbitrarily;
    - disagree across accessions -> cross-filing RESTATEMENT (overlap
      policy C): newest-filed wins, `restatement` DQC preserves old value,
      new value, and both accessions ([superseded, kept] + reason)."""
    period_key = _require_period(group[0])
    values = {fact.get("value") for fact in group}
    if len(values) == 1:
        # exactly one distinct value across the group (1 or more identical
        # facts) -> keep one representative for this window.
        labels = {
            (fact.get("fiscal_year"), fact.get("fiscal_quarter"))
            for fact in group
        }
        if len(labels) == 1:
            return group[0]
        return _label_conflict_survivor(
            group, fiscal_calendars, period_end, duration_class,
        )

    # The group DISAGREES on value. Discriminate an INTRA-filing ambiguity
    # (a SINGLE accession reporting conflicting numbers for the same
    # (signature, period) — a genuine defect, still fatal) from a
    # CROSS-filing restatement (overlap policy C): adjacent 10-Ks over the
    # multi-filing span recast the same value, which must NOT abort the
    # whole series.
    values_by_accession: dict[str, set] = {}
    for fact in group:
        values_by_accession.setdefault(
            fact.get("accession"), set()
        ).add(fact.get("value"))
    if any(len(vals) > 1 for vals in values_by_accession.values()):
        raise ValueError(
            f"kpi_xbrl.resolve_binding: signature for kpi_id {kpi_id!r} "
            f"matches {len(group)} facts with different values for "
            f"period {period_key!r} within a SINGLE filing "
            f"(concept={source.get('concept')!r}) — intra-filing "
            f"ambiguity, never resolved arbitrarily"
        )
    return _restatement_survivor(group, period_end, duration_class)


def _later_filed_order(group: list[dict]) -> list[dict]:
    """`group` sorted oldest-first by (filed, accession) — the shared
    policy-C/label-conflict ordering: the LAST element is the kept
    (most-recently-filed, tie-break higher accession) fact."""
    return sorted(
        group,
        key=lambda f: ((f.get("filed") or ""), (f.get("accession") or "")),
    )


def _label_conflict_survivor(
    group: list[dict], fiscal_calendars: dict, period_end: str,
    duration_class: str,
) -> dict:
    """Identical-value duplicates whose fiscal labels DIVERGE: keep the
    later-filed filing's fact/label deterministically, flagged
    `label_conflict` with both labels AND both source filings' dei
    calendars (the ONE DQC schema; old/new carry the diverging labels)."""
    ordered = _later_filed_order(group)
    kept = ordered[-1]
    kept_label = (kept.get("fiscal_year"), kept.get("fiscal_quarter"))
    superseded = next(
        fact
        for fact in reversed(ordered[:-1])
        if (fact.get("fiscal_year"), fact.get("fiscal_quarter")) != kept_label
    )
    kept_with_dqc = dict(kept)
    kept_with_dqc["dqc"] = assert_dqc_schema({
        "type": "label_conflict",
        "old": {
            "fiscal_year": superseded.get("fiscal_year"),
            "fiscal_quarter": superseded.get("fiscal_quarter"),
            "accession": superseded.get("accession"),
            "fiscal_calendar": fiscal_calendars.get(
                superseded.get("accession")
            ),
        },
        "new": {
            "fiscal_year": kept.get("fiscal_year"),
            "fiscal_quarter": kept.get("fiscal_quarter"),
            "accession": kept.get("accession"),
            "fiscal_calendar": fiscal_calendars.get(kept.get("accession")),
        },
        "accessions": [
            superseded.get("accession"), kept.get("accession"),
        ],
        "reason": (
            f"identical value reported for period_end "
            f"{period_end!r} ({duration_class}) by two filings "
            f"whose dei calendars yield different fiscal labels "
            f"(FY{superseded.get('fiscal_year')}-"
            f"{superseded.get('fiscal_quarter')} vs "
            f"FY{kept.get('fiscal_year')}-"
            f"{kept.get('fiscal_quarter')}) — later-filed label "
            f"kept deterministically, never an arbitrary pick"
        ),
    })
    return kept_with_dqc


def _restatement_survivor(
    group: list[dict], period_end: str, duration_class: str,
) -> dict:
    """Cross-filing restatement (policy C): keep the value from the
    most-recently-FILED filing (tie-break higher accession) and tag the
    superseded value onto the kept fact as a machine-readable `dqc`
    restatement flag (carried through to the emitted point by
    facts_to_points). The superseded fact is the most recent OLDER fact
    whose value differs from the kept one. The ONE DQC schema (Task 9
    migrated the former superseded_accession/kept_accession field names):
    accessions ordered [superseded, kept] — old-first, the same convention
    as label_conflict — with the roles named in `reason`; the audit
    content is fully preserved (policy-C parity with scope-A)."""
    ordered = _later_filed_order(group)
    kept = ordered[-1]
    superseded = next(
        fact
        for fact in reversed(ordered[:-1])
        if fact.get("value") != kept.get("value")
    )
    kept_with_dqc = dict(kept)
    kept_with_dqc["dqc"] = assert_dqc_schema({
        "type": "restatement",
        "old": superseded.get("value"),
        "new": kept.get("value"),
        "accessions": [
            superseded.get("accession"), kept.get("accession"),
        ],
        "reason": (
            f"cross-filing restatement (overlap policy C) for "
            f"period_end {period_end!r} ({duration_class}): value "
            f"{superseded.get('value')!r} from filing "
            f"{superseded.get('accession')!r} superseded by "
            f"{kept.get('value')!r} from the later-filed "
            f"{kept.get('accession')!r} — newest-filed wins, the "
            f"superseded value preserved for audit"
        ),
    })
    return kept_with_dqc


def resolve_binding(fact_pack: dict, binding: dict, company: str) -> list[dict]:
    """Resolve a logical-KPI binding onto the fact-pack's full dimensional
    signatures: `binding` = `{kpi_id, sources: [{concept, dimensions,
    consolidation, source_kind}]}` (`consolidation` optional).

    A fact matches a source when `fact["concept"] == source["concept"]` AND
    `fact["dimensions"] == source["dimensions"]` EXACTLY (dict equality — an
    absent/empty `dimensions` matches ONLY the top-level total; a fact
    carrying extra breakdown axes does NOT match a narrower source) AND the
    fact's `consolidation` (srt:ConsolidationItemsAxis member — a
    reconciliation QUALIFIER, NEVER a breakdown axis) matches the source's
    `consolidation`, each normalized with default "OperatingSegmentsMember"
    when absent/None. A source may specify `consolidation` to disambiguate a
    non-default view (e.g. an eliminations view); otherwise a segment
    binding resolves the operating-segments view without falsely colliding
    with a different consolidation view sharing the same `dimensions`. A
    matched fact is emitted (via `facts_to_points`, reusing its provenance
    mapping) under the single logical `kpi_id`. A fact matching no source is
    skipped, never fabricated. A fact matching more than one source RAISES —
    an ambiguous binding. INVARIANT: exactly ONE point per (signature,
    period_end, duration_class) — the identity key is the fact's RAW WINDOW
    plus its duration class (Task 6, docs/loom/plans/2026-07-16-operational-
    kpi-quarterly.md): a 3-month single quarter and a 9-month YTD sharing
    one signature/period_end are DISTINCT series points, never deduped and
    never raised against each other; the emitted point's `period_type`
    (CLASSIFIED fiscal quarter, `classify_fact_period`) and `period` (the
    emitted `fiscal_year` label, Task 5 — never the calendar year) are
    ATTRIBUTES of the kept fact, not part of the grouping key — grouping on
    the raw window is what lets a cross-filing fiscal-LABEL divergence
    (52/53-week FYE drift or a mid-history FYE change: the same window
    labeled differently by two filings' dei calendars) be CAUGHT at dedup
    instead of silently emitting duplicate points. When a single source's
    signature matches TWO OR MORE facts for the SAME window, they collapse
    to exactly one point — if every matched fact agrees on `value`, the
    identical duplicate(s) are DEDUPED down to one point (never
    double-counted downstream); if their fiscal labels diverge, the
    conflict is surfaced as a `dqc` `label_conflict` flag (ONE DQC schema:
    type, old, new, accessions, reason — old/new carry both diverging
    labels WITH both source filings' dei calendars from the pack's
    `fiscal_calendars`) and the LATER-FILED filing's fact (tie-break higher
    accession) survives with its label — a deterministic survivor, never an
    arbitrary pick. If the matched facts
    DISAGREE on `value`, the disagreement is discriminated by ACCESSION
    (overlap policy C): a SINGLE accession reporting conflicting values for
    the same (signature, period) is a genuine INTRA-filing ambiguity and
    RAISES ValueError naming the kpi_id + period — never resolved
    arbitrarily; but a CROSS-filing disagreement (distinct accessions, as
    adjacent 10-Ks recast a value over the multi-filing span) is a
    RESTATEMENT — resolve_binding keeps the value from the most-recently-
    FILED 10-K (tie-break higher accession) and surfaces a machine-readable
    `dqc` restatement flag on the emitted point — the ONE DQC schema
    `{type, old, new, accessions, reason}` with `accessions` ordered
    `[superseded, kept]` (old-first, same convention as `label_conflict`;
    Task 9 migrated the former superseded_accession/kept_accession field
    names into `accessions` + `reason`, audit content preserved) — rather
    than aborting the whole series. A period with exactly one matching fact
    resolves cleanly, unchanged.
    """
    kpi_id = binding["kpi_id"]
    sources = binding["sources"]

    facts_by_source_idx: list[list[dict]] = [[] for _ in sources]

    for fact in _require_facts(fact_pack):
        matched_indices = []
        for idx, source in enumerate(sources):
            selector = {
                "concept": source["concept"],
                "dimensions": source.get("dimensions", {}),
                "consolidation": source.get("consolidation"),
            }
            if _fact_matches(fact, selector):
                matched_indices.append(idx)

        if len(matched_indices) > 1:
            raise ValueError(
                f"kpi_xbrl.resolve_binding: fact matches {len(matched_indices)} "
                f"sources for kpi_id {kpi_id!r} (concept={fact.get('concept')!r}, "
                f"period_end={fact.get('period_end')!r}) — ambiguous binding, "
                f"never resolved arbitrarily"
            )
        if matched_indices:
            facts_by_source_idx[matched_indices[0]].append(fact)

    # Reduce each source's matched facts to exactly ONE fact per identity
    # key (Task 6: the RAW WINDOW — period_end + duration_class — so a
    # single-quarter and a YTD at one period_end stay DISTINCT points): a
    # window with >1 matching fact that all AGREE on value is deduped down
    # to a single representative fact (never double-counted downstream as
    # two identical points), with a cross-filing fiscal-LABEL divergence
    # inside the group flagged and resolved to the later-filed label; a
    # window with matching facts that DISAGREE on value RAISES intra-filing
    # (a genuine conflict, never resolved arbitrarily) or resolves
    # cross-filing per policy C — all four branches in `_reduce_window_group`.
    fiscal_calendars = fact_pack.get("fiscal_calendars") or {}
    deduped_facts_by_source_idx: list[list[dict]] = [[] for _ in sources]
    for idx, source in enumerate(sources):
        matched_facts = facts_by_source_idx[idx]
        by_window: dict[tuple[str, str], list[dict]] = {}
        for fact in matched_facts:
            # _require_period validates the raw window AND the emitted label
            # group (fiscal keying, Task 5 — never the calendar year); the
            # identity key itself is the duration-qualified window (Task 6).
            _require_period(fact)
            identity_key = (
                fact["period_end"],
                classify_fact_period(fact)["duration_class"],
            )
            by_window.setdefault(identity_key, []).append(fact)
        for (period_end, duration_class), group in by_window.items():
            deduped_facts_by_source_idx[idx].append(
                _reduce_window_group(
                    kpi_id, source, fiscal_calendars,
                    period_end, duration_class, group,
                )
            )

    points = []
    for idx, source in enumerate(sources):
        matched_facts = deduped_facts_by_source_idx[idx]
        if not matched_facts:
            continue
        sub_pack = {
            "company": fact_pack.get("company"),
            "facts": matched_facts,
            # Task 9: the per-accession calendar channel rides along so
            # facts_to_points can ground each point's source_form.
            "fiscal_calendars": fact_pack.get("fiscal_calendars"),
        }
        selector = {
            "concept": source["concept"],
            "dimensions": source.get("dimensions", {}),
            "consolidation": source.get("consolidation"),
        }
        points.extend(
            facts_to_points(sub_pack, kpi_id, selector, company, source["source_kind"])
        )
    return points


def _q4_input_window_end(point: dict, role: str) -> date:
    """A Q4-derivation input point's raw-window end as a date — fail loud
    on a point missing/malforming `period_end` (an input that cannot be
    windowed can never ground a derived window)."""
    period_end = point.get("period_end")
    try:
        return date.fromisoformat(period_end)
    except (TypeError, ValueError):
        raise ValueError(
            f"kpi_xbrl.derive_q4_points: {role} input point carries no "
            f"well-formed 'period_end' ({period_end!r}, kpi_id="
            f"{point.get('kpi_id')!r}, period={point.get('period')!r}) — "
            f"cannot mint the derived Q4 window, never guessed"
        ) from None


def _require_duration_weeks(point: dict, role: str) -> int:
    """A week-lane Q4-derivation input's own `duration_weeks` (Task 4,
    docs/loom/plans/2026-07-18-52-53-week-filer-support.md) — fail loud on
    a point missing/malforming it: the derived Q4's own week count
    (FY_weeks - YTD_weeks) is never guessed from a duration_class string."""
    weeks = point.get("duration_weeks")
    if not isinstance(weeks, int) or isinstance(weeks, bool):
        raise ValueError(
            f"kpi_xbrl.derive_q4_points: {role} input point carries no "
            f"well-formed 'duration_weeks' ({weeks!r}, kpi_id="
            f"{point.get('kpi_id')!r}, period={point.get('period')!r}) — "
            f"cannot mint the derived week-lane Q4, never guessed"
        )
    return weeks


def _q4_basis_mismatch_reason(
    fy: dict, ytd9: dict, fiscal_calendars: dict | None,
) -> str | None:
    """The refusal reason when the FY total and the 9mo-YTD are NOT on one
    basis (spec, critic-found: 'Q4 derivation refuses across mismatched
    restatement vintages or units'), or None when the bases agree.

    Three checks, first hit wins:
    (1) XBRL unit/scale — the points' passed-through `unit` values differ
        (absent on both sides = agree: the producer's $-unit gate already
        guarantees currency amounts today).
    (2) Restatement vintage — exactly ONE input carries an upstream
        policy-C restatement DQC: its value was recast by a later filing
        while the other input was never re-reported on that newer basis,
        so the subtraction would mix vintages. When BOTH inputs are
        restated (Task 9, T8 spec-reviewer residual), the two RESTATING
        accessions (`dqc["accessions"][-1]`, the kept/newest filing) must
        be the SAME filing — two different restating filings are two
        vintages and refuse, the same declared calendar notwithstanding;
        both restated by ONE filing = one shared newest basis, no
        mismatch.
    (3) Declared fiscal calendars — the two source filings' dei calendars
        (from the pack's `fiscal_calendars`, keyed by accession) disagree
        on `fiscal_year_end`, or either filing's calendar is absent/None
        (an unverifiable basis is refused, never assumed — docs/loom/
        memory/fiscal-year-derive-per-fact-against-filing-calendar.md:
        fail loud on an unreadable calendar, never a fallback).
    """
    if fy.get("unit") != ytd9.get("unit"):
        return (
            f"XBRL unit/scale differs between the FY total "
            f"({fy.get('unit')!r}) and the 9mo-YTD ({ytd9.get('unit')!r})"
        )
    fy_restated = (fy.get("dqc") or {}).get("type") == "restatement"
    ytd9_restated = (ytd9.get("dqc") or {}).get("type") == "restatement"
    if fy_restated != ytd9_restated:
        restated_role = "FY total" if fy_restated else "9mo-YTD"
        return (
            f"restatement vintages differ: the {restated_role} was recast "
            f"by a later filing (policy C) while the other input was never "
            f"re-reported on that basis"
        )
    if fy_restated and ytd9_restated:
        # accessions is [superseded, kept] — the kept (last) entry is the
        # RESTATING filing whose basis the policy-C value now rests on.
        fy_restating = (fy["dqc"].get("accessions") or [None])[-1]
        ytd9_restating = (ytd9["dqc"].get("accessions") or [None])[-1]
        if fy_restating != ytd9_restating:
            return (
                f"restatement vintages differ: the FY total was recast by "
                f"filing {fy_restating!r} but the 9mo-YTD by a DIFFERENT "
                f"filing {ytd9_restating!r} — two distinct restating "
                f"filings are two vintages, the same declared calendar "
                f"notwithstanding"
            )
    calendars = fiscal_calendars or {}
    fy_cal = calendars.get(fy.get("source_accession"))
    ytd9_cal = calendars.get(ytd9.get("source_accession"))
    if fy_cal is None or ytd9_cal is None:
        return (
            f"a source filing's dei fiscal calendar is unavailable "
            f"(FY accession {fy.get('source_accession')!r}: {fy_cal!r}, "
            f"9mo-YTD accession {ytd9.get('source_accession')!r}: "
            f"{ytd9_cal!r}) — the shared-basis check cannot run, refused "
            f"rather than assumed"
        )
    if fy_cal.get("fiscal_year_end") != ytd9_cal.get("fiscal_year_end"):
        return (
            f"the two source filings declare DIFFERENT fiscal calendars "
            f"(FY 10-K {fy.get('source_accession')!r}: "
            f"{fy_cal.get('fiscal_year_end')!r}; 9mo-YTD 10-Q "
            f"{ytd9.get('source_accession')!r}: "
            f"{ytd9_cal.get('fiscal_year_end')!r})"
        )
    return None


def _q4_group_gap(
    gap_type: str, accessions: list, reason: str, period, cell_ref,
) -> dict:
    """One surfaced Q4-derivation skip/refusal in the ONE DQC schema, plus
    the locating `period`/`source_cell_ref` fields (extracted from
    `derive_q4_points`, Task 9 opportunistic refactor — behavior
    unchanged)."""
    return assert_dqc_schema({
        "type": gap_type,
        "old": None,
        "new": None,
        "accessions": accessions,
        "reason": reason,
        "period": period,
        "source_cell_ref": cell_ref,
    })


def _q4_candidate_gap(
    fy_candidates: list[dict], ytd_candidates: list[dict], period, cell_ref,
    *, ytd_role: str = "9mo-YTD", mixed_lane_candidates: list[dict] | None = None,
) -> dict:
    """Classify a group that cannot supply exactly ONE FY total + ONE
    YTD anchor (extracted from `derive_q4_points`, Task 9 opportunistic
    refactor — behavior unchanged): a MISSING side is `q4_source_missing`
    (skipped and surfaced, never fabricated); multiple survivors on a side
    are ambiguous inputs — `q4_basis_mismatch` (refused, never an
    arbitrary pick). `ytd_role` names which YTD lane is being reported —
    "9mo-YTD" (the default, month lane, byte-identical to pre-Task-4
    behavior) or "36wk-YTD" (Task 4's week lane).

    `mixed_lane_candidates`, when non-empty, names a DIFFERENT YTD lane's
    candidates that ALSO survived alongside `ytd_candidates` in the same
    group (fix round 2, quality-reviewer finding on 1465a8bd): the
    derivation basis itself is ambiguous — month lane vs week lane is
    undecidable — and refuses as `q4_basis_ambiguous`, distinct from
    `q4_basis_mismatch` (multiple survivors within ONE lane). Takes
    precedence over the absent/multiple checks below: a mixed-lane group
    is refused as ambiguous even when each individual lane carries exactly
    one candidate."""
    if mixed_lane_candidates:
        present_accessions = sorted(
            p.get("source_accession")
            for p in fy_candidates + ytd_candidates + mixed_lane_candidates
        )
        reason = (
            f"ambiguous Q4 derivation basis: this group carries BOTH a "
            f"9mo-YTD candidate and a 36wk-YTD candidate — month-lane vs "
            f"week-lane is undecidable, refused rather than silently "
            f"preferring either lane"
        )
        return _q4_group_gap(
            "q4_basis_ambiguous", present_accessions, reason, period, cell_ref
        )
    absent = []
    if not fy_candidates:
        absent.append("12mo-FY total")
    if not ytd_candidates:
        absent.append(ytd_role)
    present_accessions = sorted(
        p.get("source_accession") for p in fy_candidates + ytd_candidates
    )
    if absent:
        gap_type = "q4_source_missing"
        reason = (
            f"missing {' and '.join(absent)} source for the Q4 "
            f"derivation — skipped and surfaced, never fabricated"
        )
    else:
        gap_type = "q4_basis_mismatch"
        reason = (
            f"ambiguous inputs: {len(fy_candidates)} FY totals and "
            f"{len(ytd_candidates)} {ytd_role} points survive dedup "
            f"for one signature/fiscal year — refused, never an "
            f"arbitrary pick"
        )
    return _q4_group_gap(gap_type, present_accessions, reason, period, cell_ref)


def _mint_derived_q4_point(
    fy: dict, ytd_point: dict, period, cell_ref, *, week_lane: bool = False,
) -> dict:
    """Mint the derived Q4 point (FY total minus the matching YTD point)
    for one clean, basis-checked input pair (extracted from
    `derive_q4_points`, Task 9 opportunistic refactor — behavior
    unchanged): the segregated-lane markers (`derived: True`, PLURAL
    `source_accessions`/`source_forms`), the three label groups minted
    from the derived window against the 10-K's calendar, and the
    `derived_q4` DQC recording both contributing accessions.

    `week_lane=True` (Task 4, docs/loom/plans/2026-07-18-52-53-week-filer-
    support.md) mints the week-lane Q4 instead — FY total minus the
    matching `36wk-YTD` point — with `duration_weeks` = FY_weeks −
    YTD_weeks (16 or 17) and `duration_class` TRANSCRIBED from T3's shipped
    `_WEEK_LANE_DURATION_CLASS_FORMAT["week-Q4"]` (never invented here);
    every other field (tagging, label groups, DQC schema) is identical to
    the month-lane mint, and `week_lane=False` (the default) is
    byte-identical to the pre-Task-4 behavior."""
    fy_end = _q4_input_window_end(fy, "FY-total")
    ytd_role = "36wk-YTD" if week_lane else "9mo-YTD"
    ytd_point_end = _q4_input_window_end(ytd_point, ytd_role)
    value = fy["value"] - ytd_point["value"]
    accessions = [fy.get("source_accession"), ytd_point.get("source_accession")]
    point = {
        "company": fy.get("company"),
        "kpi_id": fy.get("kpi_id"),
        "period_type": "Q4",
        "cumulative": False,
        "duration_class": "3mo",
        "period": period,
        "calendar_year": fy_end.year,
        "calendar_quarter": f"Q{(fy_end.month - 1) // 3 + 1}",
        "period_start": (ytd_point_end + timedelta(days=1)).isoformat(),
        "period_end": fy["period_end"],
        "as_of": max(fy.get("as_of") or "", ytd_point.get("as_of") or ""),
        "value": value,
        "source_accessions": accessions,
        "source_forms": [fy.get("source_form"), ytd_point.get("source_form")],
        "source_table_id": fy.get("source_table_id"),
        "source_cell_ref": cell_ref,
        "source_kind": fy.get("source_kind"),
        "derived": True,
        "dqc": assert_dqc_schema({
            "type": "derived_q4",
            "old": (
                {"fy_total": fy["value"], "ytd36": ytd_point["value"]}
                if week_lane
                else {"fy_total": fy["value"], "ytd9": ytd_point["value"]}
            ),
            "new": value,
            "accessions": accessions,
            "reason": (
                f"untagged Q4 derived as FY total minus {ytd_role} for "
                f"fiscal year {period} — computed, never reported; "
                f"segregated from directly-reported points"
            ),
        }),
    }
    if week_lane:
        fy_weeks = _require_duration_weeks(fy, "FY-total")
        ytd_weeks = _require_duration_weeks(ytd_point, "36wk-YTD")
        derived_weeks = fy_weeks - ytd_weeks
        point["duration_weeks"] = derived_weeks
        point["duration_class"] = _WEEK_LANE_DURATION_CLASS_FORMAT[
            "week-Q4"
        ].format(weeks=derived_weeks)
    return point


def derive_q4_points(points: list[dict], *, fiscal_calendars: dict | None) -> dict:
    """Derive the untagged Q4 single-quarter as (FY total − 9mo-YTD) per
    (signature, fiscal year) over `points` — resolve_binding's OUTPUT, so
    dedup/policy C have already run on every input. Returns
    `{"points": [derived Q4 points], "gaps": [surfaced skips/refusals]}`
    (spec: 'Q4 single-quarter is derived by subtraction, guarded, and
    segregated' — user governance decision A, 2026-07-16).

    - A directly-tagged Q4 3-month point SHORT-CIRCUITS its group: the
      reported point is used as-is (it is already in `points`), no
      derivation runs, no computed flag is minted.
    - A clean derivation emits a point flagged computed — DQC
      `derived_q4` recording BOTH contributing accessions — and
      segregated (`derived: True`, plural `source_accessions` +
      `source_forms` (aligned pairwise, Task 9) instead of the singular
      `source_accession`/`source_form`): a derived value never
      masquerades as directly reported, and `build_series_with_break(...,
      reported_only=True)` excludes the lane wholesale.
    - The derived point carries the THREE label groups (critic round 2),
      minted from the derived 3-month window: RAW WINDOW (`period_start`
      = day after the 9mo-YTD end, `period_end` = the FY end,
      duration_class "3mo"), CALENDAR label (the calendar quarter
      containing that period_end — the producer's DATACQTR rule), and
      FISCAL label (`period` = the 10-K FY point's emitted fiscal_year —
      itself dei-grounded fail-loud upstream — with period_type "Q4" by
      construction of a 3-month window ending on the fiscal year end).
    - A missing source is SKIPPED and SURFACED as a `q4_source_missing`
      gap naming the absent input — never fabricated. A year with
      neither input (e.g. an in-progress year of pure single quarters)
      has no derivation basis at all and is not a gap.
    - A basis mismatch (`_q4_basis_mismatch_reason`: unit/scale,
      restatement vintage, or the two filings' declared dei calendars
      disagreeing) REFUSES with a `q4_basis_mismatch` gap — DISTINCT
      from the clean `derived_q4` flag, never a silent subtraction.
    Gaps follow the ONE DQC schema (type, old, new, accessions, reason)
    plus the locating `period`/`source_cell_ref` fields.

    Week lane (Task 4, docs/loom/plans/2026-07-18-52-53-week-filer-support.
    md): a group carrying a genuine `36wk-YTD` sibling derives FY total
    minus that point instead, with `duration_weeks` = FY_weeks − YTD_weeks
    and `duration_class` transcribed from T3's week-Q4 format — gated on
    the SIBLING'S PRESENCE, never on the FY point's own `duration_weeks`
    (a month-lane calendar-year FY also carries one). A missing week-lane
    sibling falls through to the same `q4_source_missing` refusal as the
    month lane, unchanged. A group carrying BOTH a genuine `9mo-YTD` AND a
    genuine `36wk-YTD` candidate (fix round 2, quality-reviewer finding on
    1465a8bd) REFUSES as `q4_basis_ambiguous` — never an arbitrary pick of
    either lane.
    """
    groups: dict[tuple, list[dict]] = {}
    for point in points:
        key = (point.get("source_cell_ref"), point.get("period"))
        groups.setdefault(key, []).append(point)

    derived: list[dict] = []
    gaps: list[dict] = []
    for (cell_ref, period), group in sorted(
        groups.items(), key=lambda item: (str(item[0][0]), str(item[0][1]))
    ):
        if any(
            p.get("period_type") == "Q4" and not p.get("derived")
            for p in group
        ):
            continue  # directly-tagged Q4: reported used as-is, no flag
        fy_candidates = [
            p for p in group
            if _is_fy_duration_class(p.get("duration_class") or "")
        ]
        ytd9_candidates = [
            p for p in group if p.get("duration_class") == "9mo-YTD"
        ]
        # Task 4 (52/53-week filer support): a genuine week-lane YTD
        # sibling (duration_class "36wk-YTD") in this group routes
        # derivation onto the week lane — gated on the SIBLING'S PRESENCE,
        # never on the FY point's own duration_weeks alone (a month-lane
        # 365d calendar-year FY also carries duration_weeks 52; plan
        # Notes: correctness guard). Absent that sibling, behavior is
        # byte-identical to pre-Task-4 (month-lane 9mo-YTD).
        ytd36wk_candidates = [
            p for p in group if p.get("duration_class") == "36wk-YTD"
        ]
        if not fy_candidates and not ytd9_candidates and not ytd36wk_candidates:
            continue  # no derivation basis at all — not a gap
        if ytd9_candidates and ytd36wk_candidates:
            # Fix round 2 (quality-reviewer finding on 1465a8bd): BOTH lanes
            # carry a genuine candidate — the basis itself is ambiguous,
            # refused rather than silently preferring the week lane and
            # dropping the month-lane candidate with no trace.
            gaps.append(_q4_candidate_gap(
                fy_candidates, ytd9_candidates, period, cell_ref,
                mixed_lane_candidates=ytd36wk_candidates,
            ))
            continue
        week_lane = bool(ytd36wk_candidates)
        ytd_candidates = ytd36wk_candidates if week_lane else ytd9_candidates
        ytd_role = "36wk-YTD" if week_lane else "9mo-YTD"
        if len(fy_candidates) != 1 or len(ytd_candidates) != 1:
            gaps.append(_q4_candidate_gap(
                fy_candidates, ytd_candidates, period, cell_ref,
                ytd_role=ytd_role,
            ))
            continue

        fy, ytd9 = fy_candidates[0], ytd_candidates[0]
        mismatch = _q4_basis_mismatch_reason(fy, ytd9, fiscal_calendars)
        if mismatch is not None:
            gaps.append(_q4_group_gap(
                "q4_basis_mismatch",
                sorted([
                    fy.get("source_accession"), ytd9.get("source_accession"),
                ]),
                f"{mismatch} — refused, never a silent subtraction across "
                f"incompatible bases",
                period, cell_ref,
            ))
            continue

        derived.append(
            _mint_derived_q4_point(fy, ytd9, period, cell_ref, week_lane=week_lane)
        )
    return {"points": derived, "gaps": gaps}


_SERIES_GRANULARITIES = frozenset({"annual", "quarterly"})
_SINGLE_QUARTER_TYPES = frozenset({"Q1", "Q2", "Q3", "Q4"})


def _point_fiscal_year(point: dict) -> int:
    """A point's fiscal-year key as an int — `period` is the EMITTED
    fiscal_year label (`str(fiscal_year)` by construction, `_require_period`).
    A point with no integer-parseable period is surfaced loud — never
    silently kept in (or dropped from) a range-filtered series."""
    try:
        return int(point["period"])
    except (KeyError, TypeError, ValueError):
        raise ValueError(
            f"kpi_xbrl.build_series_with_break: point carries no integer "
            f"fiscal period key (period={point.get('period')!r}, "
            f"kpi_id={point.get('kpi_id')!r}) — cannot range-filter, "
            f"surfaced rather than guessed in or out of range"
        ) from None


def _validate_fiscal_range(fiscal_range) -> tuple[int, int]:
    """`(since_year, until_year)` as validated ints, fail-loud on any other
    shape — a malformed range must never silently emit everything."""
    try:
        since, until = fiscal_range
    except (TypeError, ValueError):
        raise ValueError(
            f"kpi_xbrl.build_series_with_break: fiscal_range must be a "
            f"(since_year, until_year) pair, got {fiscal_range!r}"
        ) from None
    for bound in (since, until):
        if isinstance(bound, bool) or not isinstance(bound, int):
            raise ValueError(
                f"kpi_xbrl.build_series_with_break: fiscal_range bounds must "
                f"be integers, got {fiscal_range!r}"
            )
    if since > until:
        raise ValueError(
            f"kpi_xbrl.build_series_with_break: fiscal_range is inverted "
            f"({since} > {until}) — an empty-by-construction range is "
            f"surfaced, never silently an empty series"
        )
    return since, until


def _filter_single_granularity(points: list[dict], granularity: str) -> list[dict]:
    """The single-granularity view of `points` (spec: 'A series carries a
    single granularity'): `"annual"` keeps only FY totals; `"quarterly"`
    keeps only single-quarter points (Q1-Q4, non-cumulative — the spec's
    quarterly-series scenario admits 'only single-quarter (and, if enabled,
    derived-Q4) points', so FY totals AND 6mo/9mo YTD cumulatives are both
    off-granularity, excluded — never averaged or concatenated in)."""
    if granularity == "annual":
        return [p for p in points if p.get("period_type") == "FY"]
    return [
        p for p in points
        if p.get("period_type") in _SINGLE_QUARTER_TYPES and not p.get("cumulative")
    ]


def _dimension_quarterly_absence_flags(facts: list[dict]) -> list[dict]:
    """Partition `facts` by the emitted label group (fiscal_quarter FY =
    annual/10-K, anything else = quarterly/10-Q) and delegate to the data
    layer's PURE `_dimension_quarterly_absence` (sec_edgar_client.py) —
    its production caller, re-homed to the series build per the plan's
    2026-07-17 Decision Log (the spec's WHEN — 'when the quarterly series
    is built' — lives here, and calling the existing helper avoids a
    reimplementation drifting from the data layer's signature/window
    semantics).

    The import is FUNCTION-LEVEL on purpose: sec_edgar_client does a
    module-level `import requests`, so importing it at kpi_xbrl module
    scope would break this module's offline importability (docs/loom/
    memory/importing-a-module-runs-its-module-level-imports.md) — kpi_xbrl's
    module-level imports stay stdlib + kpi_series, and the data layer is
    paid for only when absence flagging is actually requested. The helper
    itself is pure dict->list compute (no network call); offline tests stub
    requests/edgar in sys.modules before exercising this path."""
    data_scripts = _SCRIPT_DIR.parent.parent / "data-markets" / "scripts"
    if str(data_scripts) not in sys.path:
        sys.path.insert(0, str(data_scripts))
    import sec_edgar_client  # noqa: PLC0415 — deliberate lazy cross-layer import

    annual = [f for f in facts if f.get("fiscal_quarter") == "FY"]
    quarterly = [f for f in facts if f.get("fiscal_quarter") != "FY"]
    raw_flags = sec_edgar_client._dimension_quarterly_absence(annual, quarterly)
    # Task 9: re-shape the data layer's identity-only entries into the ONE
    # DQC schema (type, old, new, accessions, reason) — `accessions` names
    # the annual filing(s) that DID tag the signature (the provenance of
    # the absence claim), the identifying signature fields ride along as
    # locating extras, and NO `value` key is ever added (absence is never
    # zero-filled).
    flags = []
    for raw in raw_flags:
        accessions = sorted({
            f["accession"] for f in annual
            if f.get("concept") == raw.get("concept")
            and (f.get("dimensions") or {}) == (raw.get("dimensions") or {})
            and f.get("consolidation") == raw.get("consolidation")
            and f.get("fiscal_year") == raw.get("fiscal_year")
            and f.get("accession")
        })
        flags.append(assert_dqc_schema({
            "type": "no_quarterly_coverage",
            "old": None,
            "new": None,
            "accessions": accessions,
            "reason": (
                f"dimensional signature tagged in the 10-K(s) "
                f"{accessions} but in NO 10-Q for fiscal year "
                f"{raw.get('fiscal_year')!r} — missing quarterly tagging "
                f"only: never zero-filled, never a discontinued-segment "
                f"verdict (that judgment stays the caller's)"
            ),
            "concept": raw.get("concept"),
            "dimensions": raw.get("dimensions"),
            "consolidation": raw.get("consolidation"),
            "fiscal_year": raw.get("fiscal_year"),
        }))
    return flags


def build_series_with_break(
    points: list[dict],
    break_at_period: str,
    *,
    granularity: str | None = None,
    fiscal_range: tuple[int, int] | None = None,
    facts: list[dict] | None = None,
    reported_only: bool = False,
) -> dict:
    """Split `points` at a declared structural boundary `break_at_period`,
    delegating to `kpi_series.split_series` (plain-args pure compute, NO
    persisted break lifecycle) — never a naive concatenation across a
    tagging-regime change.

    Builds a local `applied_breaks = [{"break_period": break_at_period}]`
    from the declared boundary and returns `split_series`'s dict
    (`{as_reported, recast, break_markers}`). This is NOT a
    reimplementation of the partitioning logic — kpi_series.split_series
    owns it.

    Task 7 (docs/loom/plans/2026-07-16-operational-kpi-quarterly.md):

    - `granularity` ("annual" | "quarterly") requests a SINGLE-granularity,
      granularity-LABELED series (the result carries `granularity`):
      off-granularity points are excluded per `_filter_single_granularity`.
      With NO granularity requested, a mixed FY + sub-annual point set is
      REJECTED loud — a series carries a single granularity, and the mix is
      never silently averaged or concatenated (spec: 'mixing granularities
      is rejected').
    - `fiscal_range` = (since_year, until_year): only points whose OWN
      emitted fiscal label falls in-range are emitted (spec, critic round
      2: 'emitted points are range-filtered by each fact's OWN fiscal
      label'). The filter applies to EMITTED points — upstream
      resolve_binding already used out-of-range-filing comparatives for
      dedup/restatement, and that internal work is never undone here.
    - `reported_only` (Task 8 — spec: 'a reported-only request excludes
      derived Q4'): True excludes every derived-lane point (`derived:
      True`, e.g. a derive_q4_points Q4) from the built series; the
      directly-reported points remain. Default False keeps the derived
      lane in (it stays distinguishable point-by-point via its
      `derived` marker + `derived_q4` DQC flag).
    - `facts` (requires granularity="quarterly"): the fact set the series
      was built from; 10-K-only dimensional signatures with no 10-Q fact
      for the same fiscal year surface as `coverage_flags` entries
      (`no_quarterly_coverage` in the ONE DQC schema plus the identifying
      signature as locating fields — no `value` key: distinct from a real
      zero, and never a discontinued-segment verdict) via the data
      layer's `_dimension_quarterly_absence`.
    """
    if granularity is not None and granularity not in _SERIES_GRANULARITIES:
        raise ValueError(
            f"kpi_xbrl.build_series_with_break: unknown granularity "
            f"{granularity!r} — expected one of "
            f"{sorted(_SERIES_GRANULARITIES)} or None"
        )
    if facts is not None and granularity != "quarterly":
        raise ValueError(
            "kpi_xbrl.build_series_with_break: `facts` (the no-quarterly-"
            "coverage flagging input) requires granularity='quarterly' — "
            "the dimension-absent-from-quarterlies flag is defined for the "
            "quarterly series build only"
        )
    if reported_only:
        points = [p for p in points if not p.get("derived")]
    if fiscal_range is not None:
        since, until = _validate_fiscal_range(fiscal_range)
        points = [p for p in points if since <= _point_fiscal_year(p) <= until]
    if granularity is not None:
        points = _filter_single_granularity(points, granularity)
    elif any(p.get("period_type") == "FY" for p in points) and any(
        p.get("period_type") != "FY" for p in points
    ):
        raise ValueError(
            "kpi_xbrl.build_series_with_break: points mix annual (FY) and "
            "sub-annual period types — a series carries a single "
            "granularity; request granularity='annual' or 'quarterly' to "
            "select one (off-granularity points are then excluded). The "
            "mix is rejected, never silently averaged or concatenated."
        )

    applied_breaks = [{"break_period": break_at_period}]
    result = kpi_series.split_series(points, applied_breaks)
    if granularity is not None:
        result["granularity"] = granularity
    if facts is not None:
        flags = _dimension_quarterly_absence_flags(facts)
        if fiscal_range is not None:
            # A flag for a fiscal year outside the requested range is
            # out-of-range noise; a flag whose fiscal_year is not an int
            # cannot be placed and stays SURFACED, never silently dropped.
            flags = [
                f for f in flags
                if not isinstance(f.get("fiscal_year"), int)
                or isinstance(f.get("fiscal_year"), bool)
                or since <= f["fiscal_year"] <= until
            ]
        result["coverage_flags"] = flags
    return result


# The quarterly-series CLI's series JSON shape carries no as-reported/
# recast lineage split (no break input this slice), so the declared
# boundary passed to build_series_with_break is an INERT sentinel that
# every fiscal-period label sorts before — the whole series lands in
# `as_reported` and the emitted view is the flat concatenation.
_QUARTERLY_SERIES_INERT_BREAK = "9999"


def _fact_signature_key(fact: dict) -> tuple:
    """A fact's FULL dimensional signature as a grouping key: concept +
    the whole `dimensions` map (stable-sorted items) + the NORMALIZED
    consolidation qualifier (absent -> the default operating-segments
    view). Never one axis member — a single-member key conflates a total
    with its cross-dimensioned slices (docs/loom/memory/
    match-kpi-on-full-dimensional-signature-not-one-axis.md)."""
    return (
        str(fact.get("concept")),
        tuple(sorted((fact.get("dimensions") or {}).items())),
        _normalize_consolidation(fact.get("consolidation")),
    )


def build_quarterly_series(fact_pack: dict) -> dict:
    """Build the quarterly KPI series for EVERY full-dimensional-signature
    group present in `fact_pack["facts"]` (Task 2, docs/loom/plans/
    2026-07-18-memo-quarterly-kpi-wiring.md — no per-ticker binding config
    this slice: the groups ARE the pack's signatures).

    Pure ORCHESTRATION of the existing chain, per signature group:
    `resolve_binding` (a single-source binding minted from the group's own
    signature — classification, dedup, restatement policy C all run as
    production wires them) -> `derive_q4_points` (segregated derived-Q4
    lane) -> `build_series_with_break(granularity="quarterly",
    facts=<group facts>)` (single-granularity view + no_quarterly_coverage
    flags). No stage's logic is reimplemented here.

    Returns `{"series": [{"signature", "points", "derived_points",
    "gaps"}], "coverage_flags"}` — `signature` = `{concept, dimensions,
    consolidation}` (consolidation normalized), `points` = the emitted
    reported quarterly points (parallel calendar/fiscal labels intact),
    `derived_points` = the emitted derived-lane points (`derived: True` +
    PLURAL `source_accessions`/`source_forms`), `gaps` = the derivation's
    surfaced skip/refusal flags, `coverage_flags` = the aggregated
    per-group coverage flags. Groups are emitted in stable signature
    order. Fail-loud: a pack missing `company` raises ValueError (points
    are stamped with it); error/N-A slot packs raise via `_require_facts`.
    """
    company = fact_pack.get("company")
    if not isinstance(company, str) or not company:
        raise ValueError(
            "kpi_xbrl.build_quarterly_series: fact pack missing required "
            f"'company' (got {company!r}) — every emitted point is stamped "
            "with it, never fabricated"
        )

    groups: dict[tuple, list[dict]] = {}
    for fact in _require_facts(fact_pack):
        groups.setdefault(_fact_signature_key(fact), []).append(fact)

    fiscal_calendars = fact_pack.get("fiscal_calendars")
    series_entries = []
    coverage_flags: list[dict] = []
    for key in sorted(groups):
        concept, dims_items, consolidation = key
        dimensions = dict(dims_items)
        if dimensions:
            dims_joined = ",".join(f"{k}={v}" for k, v in sorted(dimensions.items()))
            kpi_id = f"{concept}|{dims_joined}"
        else:
            kpi_id = concept
        if consolidation != _DEFAULT_CONSOLIDATION_MEMBER:
            kpi_id = f"{kpi_id}|consolidation={consolidation}"

        binding = {
            "kpi_id": kpi_id,
            "sources": [{
                "concept": concept,
                "dimensions": dimensions,
                "consolidation": consolidation,
                # Mirrors facts_to_points' source_table_id taxonomy: real
                # breakdown axes -> dimensional, flat -> companyfacts.
                "source_kind": (
                    "xbrl-dimensional" if dimensions else "xbrl-companyfacts"
                ),
            }],
        }
        points = resolve_binding(fact_pack, binding, company)
        derived = derive_q4_points(points, fiscal_calendars=fiscal_calendars)
        series = build_series_with_break(
            points + derived["points"],
            _QUARTERLY_SERIES_INERT_BREAK,
            granularity="quarterly",
            facts=groups[key],
        )
        emitted = series["as_reported"] + series["recast"]
        series_entries.append({
            "signature": {
                "concept": concept,
                "dimensions": dimensions,
                "consolidation": consolidation,
            },
            "points": [p for p in emitted if not p.get("derived")],
            "derived_points": [p for p in emitted if p.get("derived")],
            "gaps": derived["gaps"],
        })
        coverage_flags.extend(series["coverage_flags"])

    return {"series": series_entries, "coverage_flags": coverage_flags}


def _cli_quarterly_series(args: argparse.Namespace) -> int:
    """`quarterly-series` subcommand: read a fact-pack JSON from `--file`
    (or stdin when omitted) and print `build_quarterly_series`'s series
    JSON. Mirrors `_cli_build`'s exit-code contract: malformed JSON or a
    non-object fact_pack -> 2 (nothing computed); a chain rejection
    (ValueError, e.g. missing company / N-A slot pack / intra-filing
    ambiguity) -> 1; success -> 0."""
    if args.file is not None:
        raw = Path(args.file).read_text(encoding="utf-8")
    else:
        raw = sys.stdin.read()

    try:
        fact_pack = json.loads(raw)
    except json.JSONDecodeError as exc:
        print(
            f"kpi_xbrl quarterly-series: invalid fact-pack JSON input: {exc}",
            file=sys.stderr,
        )
        return 2

    if not isinstance(fact_pack, dict):
        print(
            "kpi_xbrl quarterly-series: expected a JSON object (fact_pack), "
            f"got {type(fact_pack).__name__} — nothing computed",
            file=sys.stderr,
        )
        return 2

    try:
        result = build_quarterly_series(fact_pack)
    except ValueError as exc:
        print(f"kpi_xbrl quarterly-series: {exc}", file=sys.stderr)
        return 1

    json.dump(result, sys.stdout, ensure_ascii=False)
    sys.stdout.write("\n")
    return 0


def _cli_build(args: argparse.Namespace) -> int:
    """`build` subcommand: read a fact-pack JSON from `--file` (or stdin
    when omitted) and a binding JSON from `--binding`, call
    `resolve_binding(fact_pack, binding, company)` and print the resulting
    points list. Mirrors `kpi_memo_feed._cli_build`'s exit-code contract:
    malformed JSON or a non-object fact_pack/binding -> 2 (nothing
    computed); a `resolve_binding` rejection (ValueError, e.g. an
    ambiguous binding) -> 1; success -> 0.
    """
    if args.file is not None:
        raw = Path(args.file).read_text(encoding="utf-8")
    else:
        raw = sys.stdin.read()

    try:
        fact_pack = json.loads(raw)
    except json.JSONDecodeError as exc:
        print(f"kpi_xbrl build: invalid fact-pack JSON input: {exc}", file=sys.stderr)
        return 2

    if not isinstance(fact_pack, dict):
        print(
            "kpi_xbrl build: expected a JSON object (fact_pack), got "
            f"{type(fact_pack).__name__} — nothing computed",
            file=sys.stderr,
        )
        return 2

    binding_raw = Path(args.binding).read_text(encoding="utf-8")
    try:
        binding = json.loads(binding_raw)
    except json.JSONDecodeError as exc:
        print(f"kpi_xbrl build: invalid --binding JSON: {exc}", file=sys.stderr)
        return 2

    if not isinstance(binding, dict):
        print(
            "kpi_xbrl build: expected a JSON object (--binding), got "
            f"{type(binding).__name__} — nothing computed",
            file=sys.stderr,
        )
        return 2

    try:
        points = resolve_binding(fact_pack, binding, args.company)
    except ValueError as exc:
        print(f"kpi_xbrl build: {exc}", file=sys.stderr)
        return 1

    json.dump(points, sys.stdout, ensure_ascii=False)
    sys.stdout.write("\n")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description=(
            "XBRL fact -> kpi_store point adapter CLI "
            "(build, quarterly-series)."
        )
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    build_parser = subparsers.add_parser(
        "build",
        help="Resolve an era-specific binding against a fact-pack and print the points.",
    )
    build_parser.add_argument("--company", required=True)
    build_parser.add_argument(
        "--binding", type=Path, required=True,
        help="Path to a JSON file holding the binding ({kpi_id, sources: [...]}).",
    )
    build_parser.add_argument(
        "--file", type=Path, default=None,
        help="Path to a JSON file holding the fact_pack (default: read stdin).",
    )
    build_parser.set_defaults(func=_cli_build)

    quarterly_parser = subparsers.add_parser(
        "quarterly-series",
        help=(
            "Build the per-full-dimensional-signature quarterly series "
            "(reported + derived-Q4 lanes + coverage flags) from a fact-pack."
        ),
    )
    quarterly_parser.add_argument(
        "--file", type=Path, default=None,
        help="Path to a JSON file holding the fact_pack (default: read stdin).",
    )
    quarterly_parser.set_defaults(func=_cli_quarterly_series)

    args = parser.parse_args()
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
