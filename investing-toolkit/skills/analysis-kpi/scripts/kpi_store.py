#!/usr/bin/env python3
# /// script
# requires-python = ">=3.10"
# dependencies = []
# ///
"""
Append-only bitemporal KPI store (operational-kpi capability, slice 1).

Layer 2 (Analysis) internal persistence — NOT external I/O. Persists a
validated operational-KPI series-point to a **file-per-series JSON** (one
file per company+kpi_id, holding a list of point records) under a durable
DATA dir, so a later restatement/re-extraction APPENDS a superseding record
instead of overwriting history, and a point-in-time query "as of" an earlier
date sees only what was known then (no look-ahead bias).

This slice ships the store scaffold, `append(point)`, provenance/as_of
rejection, idempotent dedup, point-in-time/latest queries,
concurrency-safe locking, and a thin `append`/`query` CLI (plan
docs/loom/plans/2026-07-14-operational-kpi-bitemporal-store.md, Tasks 1-8).

Persistence PATTERN mirrors data-markets/scripts/cache_util.py (key
sanitization, atomic tmp+rename write) but does NOT import it and does
NOT reuse its TTL envelope — a bitemporal series is durable, immutable,
append-only, so it roots under the DATA dir (~/.local/share), not the
evictable cache dir, and never expires. The shared fs primitives
(`resolve_store_dir`, sanitize, `_atomic_write`, series locking) now live
in `_store_fs.py` — a Rule-of-Three extract triggered by a third durable
store; `_series_key`'s digest logic stays here (kpi_store-specific).
"""
from __future__ import annotations

import argparse
import calendar
import hashlib
import json
import re
import sys
from datetime import date
from pathlib import Path

# Resolve same-dir modules without a package, so `import _store_fs` works
# both under `uv run --script` and under importlib test loading (mirrors
# analysis-comps/scripts/comps_compute.py's sector_classifier import shim).
_SCRIPT_DIR = Path(__file__).resolve().parent
if str(_SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(_SCRIPT_DIR))
import _store_fs  # noqa: E402

# Distinct from cache_util's CACHE_SCHEMA_VERSION / `_cache_meta` — a
# record-shape change here is a detectable migration, not a silent misread
# (brief Open Question 2: version the envelope).
STORE_SCHEMA_VERSION = "1.0"

# Re-exported for callers/tests that import resolve_store_dir from
# kpi_store — the primitive itself now lives in _store_fs (Rule-of-Three
# extract, shared with review_queue.py).
resolve_store_dir = _store_fs.resolve_store_dir

# Re-exported: kpi_store's own sanitize usage (_series_key below) still
# needs this regex; it now lives in _store_fs.
_UNSAFE_KEY_CHARS = _store_fs._UNSAFE_KEY_CHARS

# Re-exported so a caller/test can simulate a non-POSIX host (no fcntl) the
# same way as before the extract, by patching THIS module's `fcntl` name —
# `append`'s degrade-loud gate below reads its own `fcntl`/`_warned_no_fcntl`
# (not _store_fs's), so the patch takes effect without touching _store_fs.
fcntl = _store_fs.fcntl
_warned_no_fcntl = False


def _series_key(company: str, kpi_id: str) -> str:
    """Collision-proof `<company>__<kpi_id>__<digest>` filename stem — one
    file per series, for arbitrary input.

    Both components are sanitized independently for PATH SAFETY (every char
    outside `[A-Za-z0-9_-]` → `_`), so a malicious/malformed company or
    kpi_id can never escape the store dir via `../` or a separator. But
    sanitization alone is NOT collision-proof: `_` is in the allowed set, so
    input underscores survive and a shared separator cannot disambiguate —
    e.g. (company="AAPL_", kpi_id="X") and (company="AAPL", kpi_id="_X") both
    sanitize to `AAPL___X`. A 12-hex-char digest of the EXACT raw
    (company, kpi_id) pair, NUL-separated, is appended so distinct raw pairs
    always map to distinct files — preserving the file-per-series invariant
    the later dedup/query/lock slices rely on, while keeping the sanitized
    prefix human-readable.
    """
    company_key = _UNSAFE_KEY_CHARS.sub("_", str(company)) or "_"
    kpi_key = _UNSAFE_KEY_CHARS.sub("_", str(kpi_id)) or "_"
    digest = hashlib.sha1(
        f"{company}\x00{kpi_id}".encode("utf-8")
    ).hexdigest()[:12]
    return f"{company_key}__{kpi_key}__{digest}"


def _series_path(company: str, kpi_id: str) -> Path:
    return resolve_store_dir() / f"{_series_key(company, kpi_id)}.json"


def _load_series(path: Path) -> dict:
    """Read an existing series envelope, or return a fresh empty one.

    Append-only: an existing file's `points` list is preserved and never
    overwritten. A fresh series starts with a versioned `_kpi_store_meta`
    envelope and an empty `points` list.
    """
    if path.exists():
        envelope = json.loads(path.read_text(encoding="utf-8"))
        envelope.setdefault("points", [])
        return envelope
    return {
        "_kpi_store_meta": {"version": STORE_SCHEMA_VERSION},
        "points": [],
    }


_REQUIRED_PROVENANCE_FIELDS = ("source_accession", "source_table_id", "source_cell_ref")


def _require_provenance(point: dict) -> None:
    """Reject a point missing any provenance field (absent/None/empty) —
    fail loud BEFORE any file is touched, never write an unattributed record.
    """
    for field in _REQUIRED_PROVENANCE_FIELDS:
        if not point.get(field):
            raise ValueError(
                f"kpi_store.append: point missing required provenance field "
                f"{field!r} (absent, None, or empty) — rejected, nothing written"
            )


def _require_accession_derived_as_of(point: dict) -> None:
    """Reject a point whose `as_of` is absent/empty, or explicitly flagged
    wall-clock-derived — fail loud BEFORE any file is touched.

    Wall-clock marker convention (pick-one, documented here): a point flags
    itself wall-clock-derived by carrying `as_of_is_wallclock: True`. This
    slice only validates the invariant; deriving `as_of` from an accession
    is an upstream slice's job (plan Task 3 note).
    """
    if not point.get("as_of"):
        raise ValueError(
            "kpi_store.append: point missing required 'as_of' (absent, "
            "None, or empty) — as_of must be accession-derived, rejected, "
            "nothing written"
        )
    if point.get("as_of_is_wallclock"):
        raise ValueError(
            "kpi_store.append: point's 'as_of' is flagged "
            "as_of_is_wallclock=True — as_of must be accession/disclosure-"
            "derived, not wall-clock, rejected, nothing written"
        )


_DEDUP_KEY_FIELDS = ("company", "kpi_id", "period", "as_of", "source_accession")


def _dedup_key(point: dict) -> tuple:
    return tuple(point.get(field) for field in _DEDUP_KEY_FIELDS)


# --- Period identity (read-side) -------------------------------------------
# Two observations of "the same period" from different filings must be
# recognized as the same period so `history`/coverage can group them (brief
# §Period model, backed by a 14-filer / 64,044-group measurement: raw
# (start,end) byte-identical 98.99%). This is PURE READ-SIDE logic over the
# raw `period_start`/`period_end`/`period_kind` fields T2 added to the point;
# it does NOT touch `_DEDUP_KEY_FIELDS` — changing the write-side dedup key
# would silently drop/mis-merge already-stored points (brief §Error), and
# backfill is blocked.
#
# Mean Gregorian quarter = 365.25 / 4 = 91.3125 days; dividing the duration by
# it and rounding buckets a filing's declared span into 1..4 quarters robustly
# against a few days of boundary drift (brief cites SEC FSDS `qtrs`: 0=instant,
# 1..4 duration).
_DAYS_PER_QUARTER = 91.3125


def _parse_iso_date(value):
    """Parse an ISO `YYYY-MM-DD` string to a `date`, or None if absent/
    unparseable — defensive, so an older point without identity dates (or a
    malformed one) can never crash the read-side predicates.
    """
    if not value:
        return None
    try:
        return date.fromisoformat(str(value))
    except ValueError:
        return None


def _snap_month_end(value):
    """Snap an ISO date to the LAST day of its calendar month, or None if it
    does not parse. Two ends in the same calendar month snap equal — this is
    the fallback that absorbs ~1% end-date boundary drift.
    """
    d = _parse_iso_date(value)
    if d is None:
        return None
    last_day = calendar.monthrange(d.year, d.month)[1]
    return date(d.year, d.month, last_day)


def _qtrs(point: dict):
    """Duration length in quarters: 0 for an instant (`period_kind="instant"`),
    else `round(days / 91.3125)` when that rounds INTO 1..4. Returns None for a
    span that cannot be sized to a genuine 1..4-quarter bucket:
      - a DEGENERATE duration (missing/unparseable start or end) — no start
        means no span to measure;
      - an OUT-OF-RANGE span whose rounded quarters fall outside 1..4 — e.g. a
        15-month transition FY (~5 quarters) or a sub-quarter stub. Coercing
        these into [1,4] would let them false-merge with a real annual/quarter,
        so they are refused rather than clamped. A reversed (start>end) pair
        yields a negative day-count, which rounds below 1 and is refused here
        too — no separate guard needed.
    The snap fallback in `same_period` treats a None qtrs as unmatchable, so a
    span that cannot be bucketed never produces a false merge.
    """
    if point.get("period_kind") == "instant":
        return 0
    start = _parse_iso_date(point.get("period_start"))
    end = _parse_iso_date(point.get("period_end"))
    if start is None or end is None:
        return None
    quarters = round((end - start).days / _DAYS_PER_QUARTER)
    if quarters < 1 or quarters > 4:
        return None
    return quarters


def same_period(point_a: dict, point_b: dict) -> bool:
    """True when two points describe the SAME real period.

    EXACT match is tried first: both sides carry a non-None `period_start` AND
    the raw `(period_start, period_end)` pair is byte-identical. A None
    `period_start` (an instant, or an unfinished duration extraction T2 allows)
    is NOT sufficient identity evidence for an exact match — two points sharing
    only `(None, end)` may be different spans (an instant balance vs a dateless
    duration), so exact is skipped and they must earn a match through the SNAP
    fallback below (where an instant's qtrs 0 vs a dateless duration's None qtrs
    still refuses to merge).

    Only when exact fails does the SNAP fallback fire — `period_end` snapped to
    its calendar month-end is equal AND the duration in quarters (`qtrs`;
    0=instant, else 1..4) is equal. Never merges two periods whose snapped-end
    or qtrs differ (e.g. an instant balance vs a full-year duration sharing an
    end-date), and an out-of-[1,4] or degenerate span has None qtrs so it never
    merges. A point lacking a `period_end` cannot match by date -> False.
    """
    end_a = point_a.get("period_end")
    end_b = point_b.get("period_end")
    if not end_a or not end_b:
        return False

    # EXACT: identical raw (start, end) pair, but only when BOTH starts are
    # present — a None start carries no evidence the spans coincide, so it
    # must go through the SNAP fallback instead of matching on (None, end).
    start_a = point_a.get("period_start")
    start_b = point_b.get("period_start")
    if start_a is not None and start_b is not None and (start_a, end_a) == (start_b, end_b):
        return True

    # SNAP fallback: same month-end AND same qtrs.
    snap_a = _snap_month_end(end_a)
    snap_b = _snap_month_end(end_b)
    if snap_a is None or snap_b is None or snap_a != snap_b:
        return False
    qtrs_a = _qtrs(point_a)
    qtrs_b = _qtrs(point_b)
    if qtrs_a is None or qtrs_b is None:
        return False  # degenerate duration — refuse to merge rather than guess
    return qtrs_a == qtrs_b


def _period_sort_key(point: dict) -> tuple:
    """Order key for observations: primary `period_end` (ISO strings sort
    chronologically), then a `qtrs` tiebreak so that on a shared end-date an
    instant (qtrs 0) orders before a longer duration. Missing end -> "" so a
    dateless point sorts first without raising.
    """
    quarters = _qtrs(point)
    return (point.get("period_end") or "", quarters if quarters is not None else 0)


def append(point: dict) -> None:
    """Append one series-point to its file-per-series JSON, verbatim.

    A point is a dict keyed by `(company, kpi_id, period, as_of)` carrying
    `value` + provenance (`source_accession`, `source_table_id`,
    `source_cell_ref`) and optional `lineage`/`restates` (persisted as-is,
    NOT interpreted this slice). Preconditions — provenance completeness
    and an accession-derived `as_of` (see `_require_accession_derived_as_of`
    for the wall-clock marker convention) — are ALL checked BEFORE any file
    is touched — a rejected point writes nothing, no partial state.

    Idempotent dedup: the 5-tuple `(company, kpi_id, period, as_of,
    source_accession)` is the dedup key. Re-appending a point whose key
    already exists in the series is a NO-OP (no second record written) —
    this is the "re-run the same accession" case. A corrected value MUST
    carry a new `as_of` (and typically a new `source_accession`) to
    supersede — that is a DIFFERENT dedup key, so it appends a new record
    and both are retained (append-only, bitemporal — never overwrite). A
    same-dedup-key point carrying a DIFFERENT `value` (a same-accession
    correction that didn't bump `as_of`) is treated as the no-op case too
    — the FIRST record wins and is kept; detecting/rejecting that
    collision as an error is OUT OF SCOPE for this task (a later slice's
    job if needed).

    Concurrency: the full read-modify-write cycle below is guarded by an
    exclusive per-series file lock (`_acquire_series_lock`), so parallel
    appends to the same series serialize and never lose an update; if
    `fcntl` is unavailable the append proceeds unlocked with one loud
    warning. The point is stored unchanged so a later point-in-time query
    reads back exactly what was written.
    """
    _require_provenance(point)
    _require_accession_derived_as_of(point)

    path = _series_path(point["company"], point["kpi_id"])

    lock_file = _store_fs._acquire_series_lock(path) if fcntl is not None else None
    if lock_file is None:
        global _warned_no_fcntl
        if not _warned_no_fcntl:
            print(
                "kpi_store: fcntl unavailable, append not concurrency-safe "
                "on this platform",
                file=sys.stderr,
            )
            _warned_no_fcntl = True
    try:
        envelope = _load_series(path)

        new_key = _dedup_key(point)
        for existing in envelope["points"]:
            if _dedup_key(existing) == new_key:
                return  # identical dedup key already present — no-op

        envelope["points"].append(point)
        _store_fs._atomic_write(path, envelope)
    finally:
        _store_fs._release_series_lock(lock_file)


def _matching_points(company: str, kpi_id: str, period: str) -> list:
    """Read-only: load the series file for (company, kpi_id) and return the
    points matching `period`, or [] if the series file doesn't exist. Never
    writes, mutates, or reorders the stored points.
    """
    path = _series_path(company, kpi_id)
    if not path.exists():
        return []
    envelope = _load_series(path)
    return [p for p in envelope["points"] if p.get("period") == period]


def query_point_in_time(company: str, kpi_id: str, period: str, as_of_date: str):
    """Return the record for (company, kpi_id, period) with the greatest
    `as_of` that is `<= as_of_date`, or None if none qualify (including a
    missing series file).

    `as_of` values are ISO date strings (e.g. "2024-11-01"); ISO date
    strings compare correctly under plain string `<=`/max(), so no date
    parsing is needed here.
    """
    candidates = [
        p for p in _matching_points(company, kpi_id, period)
        if p.get("as_of", "") <= as_of_date
    ]
    if not candidates:
        return None
    return max(candidates, key=lambda p: p.get("as_of", ""))


def query_latest(company: str, kpi_id: str, period: str):
    """Return the record for (company, kpi_id, period) with the greatest
    `as_of` overall, or None if the series has no matching record.
    """
    candidates = _matching_points(company, kpi_id, period)
    if not candidates:
        return None
    return max(candidates, key=lambda p: p.get("as_of", ""))


def _normalized_value(point: dict):
    """PRECISION-normalize a point's `value` against harmless representation
    differences, WITHOUT applying any unit scale: a numeric string is stripped of
    thousands commas/whitespace and parsed to a number, so "93,775,000,000" and
    93775000000 compare equal; a non-numeric value is compared as its stripped
    string. Scale is applied separately by `_scaled_value` — this function is the
    format-only step, kept apart so the two normalizations stay legible.
    """
    value = point.get("value")
    if isinstance(value, str):
        stripped = value.replace(",", "").strip()
        try:
            return float(stripped)
        except ValueError:
            return stripped
    return value


# Scale-word multipliers, matched as WHOLE WORDS against a point's `unit`. A
# stored value is NOT always base-scale: the 8-K TABLE lane commits the RAW,
# unscaled cell value paired with a scale-word `unit` (see
# kpi_8k_candidates commit — value="301.63", unit="millions"; the `(in millions)`
# caption is surfaced only as an advisory unit_hint and the SKILL contract
# forbids altering `value`). So the same figure can be stored as
# (12345, "millions") in one filing and (12345000, "thousands") in another;
# comparing the raw values would manufacture a false disagreement. Scaling the
# value by the unit's magnitude word before comparing reconciles the two.
#
# The magnitude word is matched with word boundaries on BOTH sides plus an
# optional plural `s` (`\bmillions?\b`), so "millions"/"million" both scale while
# a magnitude word that is only a SUBSTRING of a larger word does NOT —
# "billionaire" must not scale as "billion", "millionaire households" must not
# scale as "million" (the Part-2 word-boundary precedent lives in the prose
# locator: exhibit_prose.py's `\b`-guarded magnitude regex + its
# test_exhibit_prose.py boundary tests). A dimensional part around the scale word ("USD millions",
# "$ in millions") is ignored — the multiplier comes from the scale word alone.
_SCALE_WORD_MULTIPLIERS = (
    (re.compile(r"\bthousands?\b", re.IGNORECASE), 10 ** 3),
    (re.compile(r"\bmillions?\b", re.IGNORECASE), 10 ** 6),
    (re.compile(r"\bbillions?\b", re.IGNORECASE), 10 ** 9),
    (re.compile(r"\btrillions?\b", re.IGNORECASE), 10 ** 12),
)


def _scale_multiplier(unit) -> int:
    """The scale multiplier implied by a `unit`'s magnitude word, or 1 when the
    unit carries no scale word (a plain dimensional label like "USD", or None).
    thousand->1e3, million->1e6, billion->1e9, trillion->1e12. See
    `_SCALE_WORD_MULTIPLIERS` for the whole-word matching rationale.
    """
    if not unit:
        return 1
    text = str(unit)
    for pattern, factor in _SCALE_WORD_MULTIPLIERS:
        if pattern.search(text):
            return factor
    return 1


def _scaled_value(point: dict):
    """The value used for disagreement comparison: `_normalized_value` (precision/
    format-normalized), multiplied by the unit's scale-word multiplier when the
    value is numeric. A non-numeric value (an unparseable string) carries no scale
    and is returned as its normalized string. So (12345, "millions") and
    (12345000, "thousands") both scale to 1.2345e10 and compare equal, while a
    genuine restatement (93775 "millions" vs 11111 None) stays distinct.
    """
    normalized = _normalized_value(point)
    if isinstance(normalized, (int, float)):
        return normalized * _scale_multiplier(point.get("unit"))
    return normalized


def history(company: str, kpi_id: str, period_match: dict) -> dict:
    """Every stored observation of ONE fiscal period across filings, ordered by
    `as_of`, with a computed `disagreement` flag — the payoff read of this slice
    (brief §Problem, the J&J shape: FY2021 revenue 93,775,000,000 as first
    reported, re-presented as 78,740,000,000 two years later; a recorded figure
    silently stops being what the company says).

    `period_match` is a REPRESENTATIVE POINT carrying the raw
    `period_start`/`period_end`/`period_kind` identity fields — chosen over
    passing the three values loose because `same_period` is already defined over
    two point dicts, so the probe plugs straight in with zero adaptation (the
    caller typically already holds such a point from `list_series`/`query_latest`
    to use as the probe). Matching is by `same_period` over the raw date pair,
    NEVER exact string equality on the old `period` label — two vintages of one
    period can carry different labels ("FY2021" vs "2021 comparative"); grouping
    them is the whole point.

    Observations are ordered by `as_of` (ISO strings compare chronologically,
    consistent with `query_latest`'s max-on-as_of). EVERY matching observation
    is retained and returned — a superseded value is a valid vintage, never
    marked "wrong" (brief §Constraints 5: J&J spinoff, IFRS 17, 東芝 are three
    causes with one shape; calling the old value an error is a category
    mistake). The flag says "these disagree", not "this one is wrong".

    `disagreement` is a VALUE DIFF across the returned observations, never an
    event/announcement lookup (brief §Constraints 3: TW 施行細則 §6 permits
    sub-threshold corrections with no restatement event, so an event
    subscription misses them by construction): True iff >=2 observations share
    the period AND differ in `value` after precision + scale normalization.

    UNIT handling: `disagreement` is the scaled value diff above; `unit_mismatch`
    is an INDEPENDENT informational flag (True iff the observations do not all
    share one `unit`, None counting as its own unit). A differing `unit` LABEL
    never invents or suppresses a disagreement on its own: the unit feeds the
    scale multiplier (so two scales of ONE figure compare equal), but the
    remaining raw-label difference is reported only via `unit_mismatch`.
    Suppression-by-mismatch was the masking bug both reviewers found (a real
    restatement, e.g. 93,775 vs 11,111, forced to `disagreement=False` merely
    because the observations' unit labels differed, so a caller reading only
    `disagreement` saw "no problem"). `disagreement=False` means "verified equal
    after precision + scale normalization", and it may only ever say that for
    observations we actually compared.

    SCALE normalization: a stored `value` is NOT always base-scale. The 8-K TABLE
    lane commits the RAW, unscaled cell value paired with a scale-word `unit`
    (kpi_8k_candidates commit — value="301.63", unit="millions"; the SKILL
    contract forbids altering `value`, and the `(in millions)` caption is surfaced
    only as an advisory unit_hint). So the SAME figure can arrive as
    (12345, "millions") and (12345000, "thousands"); comparing raw values would
    manufacture a false disagreement. `history` therefore compares each value
    SCALED by its unit's magnitude word (`_scaled_value` -> `_scale_multiplier`,
    thousand/million/billion/trillion matched as WHOLE WORDS). The prose lane's
    values are ALREADY base-scale (`kpi_prose_candidates._normalize_value` folds
    the magnitude word INTO `value` before commit), so a prose point's `unit` MUST
    NOT itself carry a magnitude word — otherwise this would double-scale an
    already-scaled value (e.g. 3,560,000,000 tagged unit="billion" -> 3.56e18).
    That invariant is a WRITE-side contract enforced at prose commit (the prose
    lane rejects a magnitude-word unit); `history` here trusts it rather than
    re-checking per read. A genuine restatement across a scale/unit difference
    (93,775 "millions" vs 11,111 None) stays distinct after scaling. This is a
    minimal scale-word table, NOT a general unit-conversion engine (no dimensional
    conversion, e.g. USD<->count); `unit_mismatch=True` remains the honest caveat
    that the observations' raw unit labels differed.

    Read-only, never-raise on an absent OR corrupt series (matching
    `list_series`): an absent series file, or one that fails to load
    (`json.JSONDecodeError`/`OSError` — an interrupted external edit, a future
    co-writer bug), yields an empty observation list rather than taking down the
    read.
    """
    path = _series_path(company, kpi_id)
    try:
        points = _load_series(path)["points"] if path.exists() else []
    except (json.JSONDecodeError, OSError):
        points = []  # corrupt/unreadable series file — degrade like list_series

    observations = sorted(
        (p for p in points if same_period(p, period_match)),
        key=lambda p: p.get("as_of", ""),
    )

    distinct_values = {_scaled_value(p) for p in observations}
    disagreement = len(observations) >= 2 and len(distinct_values) >= 2
    unit_mismatch = len({p.get("unit") for p in observations}) > 1

    return {
        "company": company,
        "kpi_id": kpi_id,
        "observations": observations,
        "disagreement": disagreement,
        "unit_mismatch": unit_mismatch,
    }


def list_series() -> list:
    """Enumerate the `(company, kpi_id)` pairs held in the store, recovered
    from each series file's stored point CONTENT.

    The filename stem embeds a one-way SHA-1 digest of the raw
    (company, kpi_id) pair (`_series_key`), so the raw identity CANNOT be
    reversed out of the path — it is read back from each point's own
    `company`/`kpi_id` fields (stored verbatim by `append`). One series file
    is one pair, but its points are still iterated (rather than trusting the
    first) so a mixed/legacy file surfaces every identity it holds; the result
    is de-duplicated and sorted for a deterministic, filesystem-order-
    independent return.

    Read-only, and never-raise on an absent store: if `resolve_store_dir()`
    does not exist there are no series, so it returns `[]` — matching
    `_matching_points`/`query_latest`. No lock is taken: enumeration only
    reads, and a concurrent `append`'s atomic tmp+rename means each file is
    seen either fully pre- or post-write, never half-written.

    Degrades PER-FILE, not per-store: this is a long-lived multi-year local
    store, so a single unreadable / malformed / non-dict series file (an
    interrupted external edit, a future co-writer bug) must not take down
    enumeration for every OTHER series. Such a file is skipped and the scan
    continues — a partial-but-truthful listing beats an all-or-nothing raise.
    """
    store_dir = resolve_store_dir()
    if not store_dir.exists():
        return []
    pairs = set()
    for path in store_dir.glob("*.json"):
        try:
            envelope = _load_series(path)
            points = envelope.get("points")
        except (json.JSONDecodeError, OSError):
            continue  # skip a corrupt/unreadable file; keep the rest visible
        if not isinstance(points, list):
            continue
        for point in points:
            if not isinstance(point, dict):
                continue
            company = point.get("company")
            kpi_id = point.get("kpi_id")
            if company is not None and kpi_id is not None:
                pairs.add((company, kpi_id))
    return sorted(pairs)


def list_companies() -> list:
    """The distinct companies held in the store, sorted — a thin projection of
    `list_series`.
    """
    return sorted({company for company, _kpi_id in list_series()})


def list_kpis(company: str) -> list:
    """The distinct kpi_ids held for one company, sorted — a thin projection of
    `list_series`.
    """
    return sorted(
        kpi_id for company_key, kpi_id in list_series() if company_key == company
    )


def _cli_append(args: argparse.Namespace) -> int:
    """`append` subcommand: read ONE point as JSON from `--file` (or stdin
    when omitted), call `append(point)`. A rejection (ValueError from the
    provenance/as_of guards) is printed to stderr and exits non-zero — fail
    loud, never a silent swallow.
    """
    if args.file is not None:
        raw = Path(args.file).read_text(encoding="utf-8")
    else:
        raw = sys.stdin.read()

    try:
        point = json.loads(raw)
    except json.JSONDecodeError as exc:
        print(f"kpi_store append: invalid JSON input: {exc}", file=sys.stderr)
        return 2

    if not isinstance(point, dict):
        print(
            "kpi_store append: expected a JSON object (point), got "
            f"{type(point).__name__} — nothing written",
            file=sys.stderr,
        )
        return 2

    try:
        append(point)
    except ValueError as exc:
        print(f"kpi_store append: {exc}", file=sys.stderr)
        return 1
    return 0


def _cli_query(args: argparse.Namespace) -> int:
    """`query` subcommand: dispatch to `query_point_in_time` (`--as-of`) or
    `query_latest` (`--latest`), printing the resulting record as JSON to
    stdout (or `null` if none matched).
    """
    if args.as_of is not None:
        record = query_point_in_time(args.company, args.kpi_id, args.period, args.as_of)
    else:
        record = query_latest(args.company, args.kpi_id, args.period)

    json.dump(record, sys.stdout, ensure_ascii=False)
    sys.stdout.write("\n")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Append-only bitemporal KPI store CLI (append / query)."
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    append_parser = subparsers.add_parser(
        "append", help="Append one KPI point (JSON) to its series file."
    )
    append_parser.add_argument(
        "--file", type=Path, default=None,
        help="Path to a JSON file holding the point (default: read stdin).",
    )
    append_parser.set_defaults(func=_cli_append)

    query_parser = subparsers.add_parser(
        "query", help="Query a KPI series (point-in-time or latest)."
    )
    query_parser.add_argument("--company", required=True)
    query_parser.add_argument("--kpi-id", required=True, dest="kpi_id")
    query_parser.add_argument("--period", required=True)
    query_mode = query_parser.add_mutually_exclusive_group(required=True)
    query_mode.add_argument(
        "--latest", action="store_true",
        help="Return the greatest-as_of record overall.",
    )
    query_mode.add_argument(
        "--as-of", default=None, dest="as_of",
        help="Return the greatest-as_of record with as_of <= this date "
             "(point-in-time).",
    )
    query_parser.set_defaults(func=_cli_query)

    args = parser.parse_args()
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
