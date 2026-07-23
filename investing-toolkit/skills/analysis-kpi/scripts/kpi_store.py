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
import sys
from datetime import date
from decimal import Decimal
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

    Raises `ValueError` (never `AttributeError`) when the file parses to
    valid JSON that is NOT an envelope object — e.g. a truncated write left
    a bare list or scalar. The two never-raise READERS (`history`,
    `list_series`) catch `(json.JSONDecodeError, OSError, ValueError)` around
    it to degrade per-file; the other callers do not catch here — `append`'s
    CLI surfaces the `ValueError` as a clean exit-1 message via
    `_cli_append`, and `_matching_points` (query paths) propagates it, as it
    always propagated the old crash. `ValueError` was chosen over reusing
    `json.JSONDecodeError` (this is a SHAPE error, the JSON parsed fine) —
    the minimal-diff fix that keeps every never-raise-on-read reader honest
    without inventing a new exception surface (kpi-tearsheet plan, T2b:
    round-2 reviewer-reproduced AttributeError from the old bare
    `envelope.setdefault(...)` on a non-dict `json.load` result).
    """
    if path.exists():
        envelope = json.loads(path.read_text(encoding="utf-8"))
        if not isinstance(envelope, dict):
            raise ValueError(
                f"kpi_store: {path.name} parsed to {type(envelope).__name__}, "
                "not a JSON object — corrupt series envelope"
            )
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
    differences, WITHOUT applying the per-point scale: a numeric string is
    stripped of thousands commas/whitespace and parsed to a number, so
    "93,775,000,000" and 93775000000 compare equal; a non-numeric value is
    compared as its stripped string. The scale is applied separately by
    `_canonical_value` — this function is the format-only step, kept apart so the
    two normalizations stay legible.
    """
    value = point.get("value")
    if isinstance(value, str):
        stripped = value.replace(",", "").strip()
        try:
            return float(stripped)
        except ValueError:
            return stripped
    return value


def _canonical_value(point: dict):
    """The base-scale value used for disagreement comparison: the precision/
    format-normalized `value` (`_normalized_value`) multiplied by the point's
    EXPLICIT per-point `scale` when the value is numeric. The multiply goes
    through `Decimal`, NOT binary float, and reduces to an int when the result is
    integral (else float), so two representations of ONE real figure compare and
    hash EQUAL in `history`'s distinct-value set (see the body comment).

    `scale` is the multiplier from the stored/verbatim `value` to the base-scale
    figure, set ONCE at the producer (Slice C, Task 9): the 8-K TABLE lane stores
    the verbatim cell (value="301.63") with `scale=1e6`; the prose lane stores an
    already-base value with `scale` HARDCODED 1; XBRL, if ever stored, is base
    (scale 1). So every lane stores a base-comparable canonical and the read is a
    trivial value diff — no magnitude word is parsed out of the free-text `unit`.

    A point MISSING `scale` defaults to 1 (prose/XBRL are base; an old 8-K point
    predating the explicit field is a known backfill limitation — the append
    dedup key blocks backfill, recorded in the plan). A non-numeric value (an
    unparseable string) carries no scale and is returned as its normalized string.
    """
    normalized = _normalized_value(point)
    if isinstance(normalized, (int, float)):
        # Multiply through Decimal, NOT binary float: `float("1.005") * 1e9` is
        # 1004999999.9999999, so a 2-decimal 8-K cell (value="1.005", scale=1e9)
        # would fabricate a disagreement against the SAME figure stored base
        # (1005000000, scale=1). Decimal multiplies the printed decimal digits
        # exactly. Mirrors kpi_prose_candidates._normalize_value, which routes its
        # own magnitude scaling through Decimal for exactly this hazard. Reduce to
        # an int when the result is integral (else float) — its own int/float
        # convention — so two representations of one real figure compare and hash
        # EQUAL in history's distinct-value set (12345e6 == 12345000e3; an int and
        # a float of the same integral value are `==` and hash alike in Python).
        scaled = Decimal(str(normalized)) * Decimal(str(point.get("scale", 1)))
        return int(scaled) if scaled == scaled.to_integral_value() else float(scaled)
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
    the period AND differ in their CANONICAL value. `disagreement=False` means
    "verified equal after canonicalization", and it may only ever say that for
    observations we actually compared.

    EXPLICIT-SCALE canonicalization: a stored `value` is NOT always base-scale,
    so each value is compared as its CANONICAL `_normalized_value(value) * scale`
    (`_canonical_value`), where `scale` is an EXPLICIT per-point field set once at
    the producer (Slice C, Task 9) — NOT inferred here by parsing a magnitude word
    out of the free-text `unit`. The 8-K TABLE lane commits the verbatim cell
    (value="301.63") with `scale=1e6` computed once from the confirmed unit; the
    prose lane commits an already-base value (`kpi_prose_candidates._normalize_value`
    folds the magnitude INTO `value`) with `scale` HARDCODED 1; XBRL, if ever
    stored, is base (scale 1). So the SAME figure stored as (12345, scale=1e6) and
    (12345000, scale=1e3) canonicalizes equal, while a genuine restatement
    (93,775,000,000 vs 78,740,000,000, both base) stays distinct. Because prose
    scale is hardcoded 1, a prose `unit` of "billion" is inert and can no longer
    double-scale an already-base value — the structural guarantee that RETIRED the
    former read-time scale inference and its write-side magnitude-word guard. The
    `unit` label drives no computation here; it is retained on each observation
    for display only.

    Read-only, never-raise on an absent OR corrupt series (matching
    `list_series`): an absent series file, or one that fails to load
    (`json.JSONDecodeError`/`OSError`/`ValueError` — an interrupted external
    edit, a non-dict envelope, a future co-writer bug), yields an empty
    observation list rather than taking down the read.
    """
    path = _series_path(company, kpi_id)
    try:
        points = _load_series(path)["points"] if path.exists() else []
    except (json.JSONDecodeError, OSError, ValueError):
        points = []  # corrupt/unreadable series file — degrade like list_series

    observations = sorted(
        (p for p in points if same_period(p, period_match)),
        key=lambda p: p.get("as_of", ""),
    )

    distinct_values = {_canonical_value(p) for p in observations}
    disagreement = len(observations) >= 2 and len(distinct_values) >= 2

    return {
        "company": company,
        "kpi_id": kpi_id,
        "observations": observations,
        "disagreement": disagreement,
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
        except (json.JSONDecodeError, OSError, ValueError):
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


def _group_period_entries(points: list) -> list:
    """Group ONE kpi_id's points into pinned-payload period entries (tearsheet
    plan `docs/loom/plans/2026-07-23-kpi-tearsheet.md`, Task 2 pin).

    Grouping is via `same_period` (raw date-pair identity) — NEVER by the
    display-only `point['period']` label, so two vintages carrying different
    labels for the same real period ("FY2021" vs "2021 comparative") still
    merge into one entry (mirrors `history`'s doctrine, generalized from one
    probe period to every period a kpi_id holds).

    `same_period` is NOT transitive (its EXACT branch ignores `period_kind`,
    its SNAP branch requires end+qtrs agreement — a chain A~B~C need not
    imply A~C). Matching every point only against a group's first member
    ("anchor") would make grouping depend on insertion order — same data,
    different result, on the SAME underlying series depending on file-glob
    order. So this groups by EQUIVALENCE CLOSURE instead: a point joins the
    first group where it matches ANY existing member; if it matches members
    of MULTIPLE existing groups, those groups are merged into one. Groups
    can therefore end up holding points that don't ALL pairwise-match each
    other directly (only transitively, through a chain) — including a
    period_kind mix (e.g. an instant chained to a duration via a third
    point) — this is intentional: `same_period` says those points describe
    the same real period, and closure just makes that transitive.

    Each entry's `observations` are sorted ascending by `as_of`, each
    verbatim-plus-`canonical_value` (`_canonical_value` — Decimal, never
    float); `latest` is the max-`as_of` observation (ties broken like
    `query_latest`/`history`: `max()` keeps the first-encountered on an
    equal key); `disagreement` is `history`'s doctrine (>=2 observations AND
    >=2 distinct canonical values); `period_labels` lists every distinct
    label observed, in as_of order. Entries are returned sorted ascending by
    `_period_sort_key` of a representative point (the group's first member
    by input order — under closure grouping this member is GUARANTEED to
    directly `same_period`-match at least one other member, but NOT
    necessarily every member, so its `period_end`/`period_kind` is
    representative display data only, not proof the whole group pairwise
    agrees).

    `period_axis_key` (tearsheet plan, whole-branch review Fix 1) is the
    STORE-OWNED cross-KPI column-alignment identity a consumer joins on
    instead of the raw `(period_start, period_end)` pair: `"<snapped-
    month-end-ISO>|q<qtrs>"`, computed from the representative via the
    same `_snap_month_end`/`_qtrs` helpers `same_period` itself uses, or
    `null` when either is uncomputable (a degenerate span). Two entries
    sharing this key describe the same real period even when their raw
    dates drift within snap tolerance; a `null` key must never be treated
    as equal to another `null` key by a consumer — it means "not proven
    the same", not "no period".
    """
    groups: list = []
    for point in points:
        matched_indices = [
            i for i, group in enumerate(groups)
            if any(same_period(member, point) for member in group)
        ]
        if not matched_indices:
            groups.append([point])
            continue

        first_index = matched_indices[0]
        target = groups[first_index]
        target.append(point)
        # Merge any OTHER groups this point also matched into `target` — the
        # point is the bridge proving they belong to one equivalence class.
        for extra_index in reversed(matched_indices[1:]):
            target.extend(groups.pop(extra_index))

    keyed_entries = []
    for group in groups:
        observations = sorted(group, key=lambda p: p.get("as_of", ""))
        canon_observations = [
            {**p, "canonical_value": _canonical_value(p)} for p in observations
        ]
        distinct_values = {o["canonical_value"] for o in canon_observations}
        disagreement = len(canon_observations) >= 2 and len(distinct_values) >= 2
        latest = max(canon_observations, key=lambda p: p.get("as_of", ""))

        labels = []
        for p in observations:
            label = p.get("period")
            if label not in labels:
                labels.append(label)

        representative = group[0]
        snapped_end = _snap_month_end(representative.get("period_end"))
        quarters = _qtrs(representative)
        period_axis_key = (
            f"{snapped_end.isoformat()}|q{quarters}"
            if snapped_end is not None and quarters is not None
            else None
        )
        entry = {
            "period_start": representative.get("period_start"),
            "period_end": representative.get("period_end"),
            "period_kind": representative.get("period_kind"),
            "period_axis_key": period_axis_key,
            "period_labels": labels,
            "disagreement": disagreement,
            "latest": latest,
            "observations": canon_observations,
        }
        keyed_entries.append((_period_sort_key(representative), entry))

    keyed_entries.sort(key=lambda pair: pair[0])
    return [entry for _key, entry in keyed_entries]


def dump_company(company: str) -> dict:
    """Assemble the tearsheet plan's PINNED dump payload for one company
    (`docs/loom/plans/2026-07-23-kpi-tearsheet.md` ## Notes — SSOT for the
    field names/nesting): `{"company", "series", "warnings"}`, `series`
    sorted by `kpi_id`, each holding period entries from
    `_group_period_entries`.

    Scans every series file (like `list_series`), keeping only points whose
    stored `company` field matches — a series file's raw identity lives in
    its POINTS, not its filename (`_series_key` embeds a one-way digest), so
    filtering by filename alone would miss/mismatch. A corrupt/malformed
    file (unreadable JSON, JSON that doesn't parse to an envelope dict — e.g.
    a truncated write left a bare list/scalar — or a `points` field that
    isn't a list) is skipped and noted in `warnings` as `"skipped corrupt
    series file: <name>"` — unlike `list_series`'s SILENT per-file skip,
    this payload is rendered straight to a report, so the reader must be
    told a series was dropped. Unknown company or an absent/empty store
    returns an empty-`series` payload — never raises (matches the store's
    never-raise-on-read posture).

    Parses each file directly (NOT via `_load_series`) so a non-dict
    envelope can be caught by an explicit `isinstance` check instead of
    surfacing as an `AttributeError` out of `_load_series`'s
    `envelope.setdefault(...)` — every file here is glob-matched to
    already exist, so `_load_series`'s "create a fresh envelope for a
    missing file" branch is not needed on this read path.
    """
    store_dir = resolve_store_dir()
    warnings: list = []
    points_by_kpi: dict = {}

    if store_dir.exists():
        for path in sorted(store_dir.glob("*.json")):
            try:
                envelope = json.loads(path.read_text(encoding="utf-8"))
            except (json.JSONDecodeError, OSError):
                warnings.append(f"skipped corrupt series file: {path.name}")
                continue
            points = envelope.get("points") if isinstance(envelope, dict) else None
            if not isinstance(points, list):
                warnings.append(f"skipped corrupt series file: {path.name}")
                continue
            for point in points:
                if not isinstance(point, dict) or point.get("company") != company:
                    continue
                kpi_id = point.get("kpi_id")
                if kpi_id is None:
                    continue
                points_by_kpi.setdefault(kpi_id, []).append(point)

    series = [
        {"kpi_id": kpi_id, "periods": _group_period_entries(points_by_kpi[kpi_id])}
        for kpi_id in sorted(points_by_kpi)
    ]
    return {"company": company, "series": series, "warnings": warnings}


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


def _cli_list_series(args: argparse.Namespace) -> int:
    """`list-series` subcommand: print `list_series()`'s `(company, kpi_id)`
    pairs as a JSON array of 2-element arrays to stdout. Never raises on an
    absent/empty store — `list_series()` already degrades to `[]`.
    """
    json.dump(list_series(), sys.stdout, ensure_ascii=False)
    sys.stdout.write("\n")
    return 0


def _cli_dump(args: argparse.Namespace) -> int:
    """`dump` subcommand: print `dump_company(--company)`'s pinned payload
    (`docs/loom/plans/2026-07-23-kpi-tearsheet.md` ## Notes) as JSON to
    stdout. Never raises — an unknown company or empty store yields an
    empty-`series` payload, exit 0 (matches the read-side never-raise
    posture).
    """
    payload = dump_company(args.company)
    json.dump(payload, sys.stdout, ensure_ascii=False)
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

    list_series_parser = subparsers.add_parser(
        "list-series",
        help="List the store's (company, kpi_id) pairs as a JSON array.",
    )
    list_series_parser.set_defaults(func=_cli_list_series)

    dump_parser = subparsers.add_parser(
        "dump",
        help="Dump one company's KPI series as the tearsheet-plan pinned JSON payload.",
    )
    dump_parser.add_argument("--company", required=True)
    dump_parser.set_defaults(func=_cli_dump)

    args = parser.parse_args()
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
