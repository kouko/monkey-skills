#!/usr/bin/env python3
# /// script
# requires-python = ">=3.10"
# dependencies = []
# ///
"""
Memo-feed contract assembly (operational-kpi capability, slice 8 — final
offline slice).

Layer 2 (Analysis) PURE-ASSEMBLY — mirrors kpi_validate.py: stdlib only,
does NOT import `_store_fs`, does NOT resolve a store dir, does NOT lock
or write files. It takes the series data (`kpi_series`) as a caller-
supplied argument rather than querying `kpi_store` directly — decoupled
from the store, like kpi_validate/kpi_series.

Task 1 ships `build_memo_feed(company, schema_version, kpi_series,
generated_at)`: it queries `kpi_gate.is_trusted(company, schema_version)`
(same-skill import, slice 5's reliability gate — reused, NOT
reimplemented) and assembles a typed feed dict:

  - TRUSTED     -> {"_memo_feed_schema_version", "company",
                    "schema_version", "status": "TRUSTED",
                    "kpi_feeds": [...from kpi_series], "generated_at"}
  - NOT TRUSTED -> {..., "status": "WITHHELD",
                    "withheld_reason": <kpi_gate.gate_verdict(...)>,
                    "kpi_feeds": [], "generated_at"} — NO series values
                    bundled: a below-bar or never-evaluated company must
                    never leak extracted figures into the memo artifact.

`kpi_series` shape: a list of dicts, each `{"kpi_id", "points", "provenance"?}`
(`points` a list of dicts, each `{"period", "value", "source_accession",
"source_table_id", "source_cell_ref"}`; a top-level `provenance` key is
optional per-series metadata, NOT what Task 2's check reads) — each entry
is bundled into `kpi_feeds` verbatim.

Task 2 adds a provenance-completeness REFUSAL at the TRUSTED-path
boundary: every point in every series entry must carry all three of
`source_accession`/`source_table_id`/`source_cell_ref` directly on the
point dict (absent/None/empty any one -> `build_memo_feed` raises
`ValueError` naming the missing field + kpi_id, nothing returned). A
WITHHELD feed carries no points, so this only bites the TRUSTED path.

`generated_at` is caller-supplied — this module never reads the wall
clock, mirroring `kpi_schema.confirm`'s / `kpi_gate.evaluate`'s
`evaluated_at` convention.

Task 3 adds a thin argparse CLI (`build`) wrapping `build_memo_feed`,
mirroring `kpi_gate.py`'s CLI shape and fail-loud exit-code convention:
0 on ANY built feed (INCLUDING a WITHHELD feed — a validly-withheld
company is not a CLI error), 1 on a provenance ValueError, 2 on malformed
or non-array `kpi_series` JSON (isinstance guard, no raw traceback).

Quarterly/XBRL arm (memo quarterly-KPI wiring slice, envelope 1.1):
`build_quarterly_memo_feed(company, series_payload, generated_at)` +
`build-quarterly` CLI assemble a memo feed from the `quarterly-series`
CLI's output (`kpi_xbrl.build_quarterly_series`: `{series: [{signature,
points, derived_points, gaps}], coverage_flags}`).

XBRL-lane trust ruling (user-ratified 2026-07-18, docs/loom/plans/
2026-07-18-memo-quarterly-kpi-wiring.md §Decision Log): this arm does
NOT call `kpi_gate.is_trusted` — the store-based reliability gate covers
the tier-① append-only-store lane only (manually-confirmed extractions).
Admission on the quarterly/XBRL lane is machine-verified, fail-closed:

  - every reported point carries a non-blank `source_accession` and a
    non-blank `kpi_id` (the point-level concept identifier in the series
    shape — the concept + full dimensional signature);
  - every derived point carries `derived: True` plus non-empty PLURAL
    `source_accessions`/`source_forms` (each element non-blank);
  - every `coverage_flags` entry passes `kpi_xbrl.assert_dqc_schema`
    (the ONE DQC schema) and is then passed through VERBATIM.

Any violation raises ValueError naming the field + series signature —
nothing returned (mirrors the v1.0 whitespace-rejecting refusal). There
is no WITHHELD state on this arm: the feed is TRUSTED or refused. If
quarterly series ever ingest manually-corrected values via the store,
merge the gates then — envelope 1.1 makes that migration detectable.
CLI exit codes mirror `build`: 0 built, 1 provenance/DQC ValueError,
2 malformed JSON or a non-object payload.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

# Resolve same-dir modules without a package (mirrors kpi_gate.py's /
# kpi_store.py's own same-dir import shim), so `import kpi_gate` works both
# under `uv run --script` and under importlib test loading.
_SCRIPT_DIR = Path(__file__).resolve().parent
if str(_SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(_SCRIPT_DIR))
import kpi_gate  # noqa: E402
import kpi_xbrl  # noqa: E402 — assert_dqc_schema only (stdlib-only module)

# A feed-shape change here is a detectable migration, not a silent misread
# (mirrors kpi_store.STORE_SCHEMA_VERSION / kpi_schema.SCHEMA_ENVELOPE_VERSION
# / kpi_gate.GATE_ENVELOPE_VERSION).
MEMO_FEED_SCHEMA_VERSION = "1.0"

# The quarterly/XBRL arm's envelope version. Tier-① `build_memo_feed`
# stays at 1.0 byte-identically; only the new arm emits 1.1 — a consumer
# can tell the two feed shapes apart without sniffing keys.
#
# Additive-field ruling (Task 5, docs/loom/plans/2026-07-18-52-53-week-
# filer-support.md): per-point `duration_weeks` and the supplementary
# `week_normalized_yoy` field do NOT bump this version. The envelope's
# top-level shape (`series`/`coverage_flags`, passed through VERBATIM by
# `build_quarterly_memo_feed`) is unchanged, and both fields are OPTIONAL
# per-point additions a consumer that doesn't recognize them can safely
# ignore — unlike the 1.0->1.1 jump, which was a wholesale different
# envelope shape (kpi_feeds/status vs series/coverage_flags), this is not
# a detectable migration. Stays "1.1" — pinned by
# test_kpi_memo_feed.py::test_build_quarterly_memo_feed_carries_week_lane_fields.
MEMO_FEED_QUARTERLY_SCHEMA_VERSION = "1.1"

# Every series-point bundled into a TRUSTED feed must carry ALL THREE of
# these directly on the point dict — absent/None/empty any one of them
# means the value can never be traced back to its source cell, so it must
# never be bundled into the artifact the memo trusts.
_REQUIRED_POINT_PROVENANCE_FIELDS = (
    "source_accession", "source_table_id", "source_cell_ref",
)


def _check_series_provenance(kpi_series: list) -> None:
    """Raise ValueError, loud, naming the missing field + kpi_id, if ANY
    point in ANY series entry lacks complete provenance. Never bundle an
    unattributed value into the TRUSTED feed (Task 2's refusal contract).
    """
    for series in kpi_series:
        kpi_id = series.get("kpi_id")
        for point in series.get("points", []):
            for field in _REQUIRED_POINT_PROVENANCE_FIELDS:
                # Reject absent / None / empty AND whitespace-only — a
                # blank-looking provenance value is effectively unattributed
                # (docs/loom/memory/required-identity-guard-must-reject-whitespace-not-just-empty).
                if not str(point.get(field, "")).strip():
                    raise ValueError(
                        f"kpi_memo_feed: kpi_id={kpi_id!r} has a point missing "
                        f"required provenance field {field!r} — refusing to "
                        "bundle an unattributed value into the memo feed"
                    )


def build_memo_feed(company: str, schema_version, kpi_series: list, generated_at) -> dict:
    """Assemble the memo-feed contract for `(company, schema_version)`.

    Fail-closed on the reliability gate: only a TRUSTED verdict
    (`kpi_gate.is_trusted`) bundles `kpi_series` into `kpi_feeds`; any other
    verdict (WITHHELD / NOT_EVALUATED / no gate record at all, all of which
    `kpi_gate.is_trusted` reads as False) returns an empty `kpi_feeds` and
    surfaces the gate's own recorded verdict string as `withheld_reason` —
    never fabricated, never silently substituted with a generic message.
    """
    if kpi_gate.is_trusted(company, schema_version):
        _check_series_provenance(kpi_series)
        return {
            "_memo_feed_schema_version": MEMO_FEED_SCHEMA_VERSION,
            "company": company,
            "schema_version": schema_version,
            "status": "TRUSTED",
            "kpi_feeds": list(kpi_series),
            "generated_at": generated_at,
        }

    return {
        "_memo_feed_schema_version": MEMO_FEED_SCHEMA_VERSION,
        "company": company,
        "schema_version": schema_version,
        "status": "WITHHELD",
        "withheld_reason": kpi_gate.gate_verdict(company, schema_version),
        "kpi_feeds": [],
        "generated_at": generated_at,
    }


def _is_blank(value) -> bool:
    """Absent/None/empty/whitespace-only — a blank-looking identifier is
    effectively unattributed (docs/loom/memory/
    required-identity-guard-must-reject-whitespace-not-just-empty)."""
    return not str(value if value is not None else "").strip()


def _check_quarterly_provenance(series_entries: list) -> None:
    """Raise ValueError, loud, naming the offending field + series
    signature, if ANY point violates the quarterly/XBRL lane's
    machine-verified provenance rule (module docstring: reported points
    need non-blank `source_accession` + `kpi_id`; derived points need
    `derived: True` + non-empty plural `source_accessions`/`source_forms`).
    """
    for entry in series_entries:
        signature = entry.get("signature") if isinstance(entry, dict) else None
        for point in entry.get("points", []):
            for field in ("source_accession", "kpi_id"):
                if _is_blank(point.get(field)):
                    raise ValueError(
                        f"kpi_memo_feed: quarterly series signature="
                        f"{signature!r} has a reported point missing required "
                        f"provenance field {field!r} — refusing to bundle an "
                        "unattributed value into the memo feed"
                    )
        for point in entry.get("derived_points", []):
            if point.get("derived") is not True:
                raise ValueError(
                    f"kpi_memo_feed: quarterly series signature={signature!r} "
                    f"has a derived-lane point without 'derived': True — a "
                    "derived value must never masquerade as reported"
                )
            for field in ("source_accessions", "source_forms"):
                values = point.get(field)
                if (
                    not isinstance(values, list)
                    or not values
                    or any(_is_blank(v) for v in values)
                ):
                    raise ValueError(
                        f"kpi_memo_feed: quarterly series signature="
                        f"{signature!r} has a derived point missing required "
                        f"plural provenance field {field!r} (non-empty list "
                        "of non-blank entries) — refusing to bundle an "
                        "unattributed derived value into the memo feed"
                    )


def build_quarterly_memo_feed(company: str, series_payload: dict, generated_at) -> dict:
    """Assemble the quarterly/XBRL-arm memo feed (envelope 1.1) from a
    `quarterly-series` payload (`{series, coverage_flags}`).

    Fail-closed WITHOUT the store gate (XBRL-lane trust ruling, module
    docstring): admission = per-point provenance completeness
    (`_check_quarterly_provenance`) + `kpi_xbrl.assert_dqc_schema` on every
    coverage flag; `series` and `coverage_flags` are then passed through
    VERBATIM. Either the whole payload is admitted as TRUSTED or a
    ValueError names the violation — no WITHHELD state on this arm.
    """
    if not isinstance(series_payload, dict):
        raise ValueError(
            "kpi_memo_feed: series_payload must be a dict (the "
            "quarterly-series output object), got "
            f"{type(series_payload).__name__}"
        )
    series_entries = series_payload.get("series")
    if not isinstance(series_entries, list):
        raise ValueError(
            "kpi_memo_feed: series_payload is missing its 'series' list — "
            "nothing to admit into the memo feed"
        )
    coverage_flags = series_payload.get("coverage_flags")
    if not isinstance(coverage_flags, list):
        raise ValueError(
            "kpi_memo_feed: series_payload is missing its 'coverage_flags' "
            "list — coverage honesty is part of the quarterly-arm contract"
        )

    _check_quarterly_provenance(series_entries)
    for flag in coverage_flags:
        kpi_xbrl.assert_dqc_schema(flag)

    return {
        "_memo_feed_schema_version": MEMO_FEED_QUARTERLY_SCHEMA_VERSION,
        "company": company,
        "status": "TRUSTED",
        "series": list(series_entries),
        "coverage_flags": list(coverage_flags),
        "generated_at": generated_at,
    }


def _cli_build(args: argparse.Namespace) -> int:
    """`build` subcommand: read `kpi_series` as a JSON array from `--file`
    (or stdin when omitted), call `build_memo_feed(company, schema_version,
    kpi_series, generated_at)` and print the resulting feed. Mirrors
    `kpi_gate._cli_add_labels`'s exit-code contract: malformed JSON or a
    non-array body -> 2 (nothing computed); a provenance rejection
    (ValueError) -> 1; success -> 0 — INCLUDING a WITHHELD feed, since a
    validly-withheld company is not a CLI error.
    """
    if args.file is not None:
        raw = Path(args.file).read_text(encoding="utf-8")
    else:
        raw = sys.stdin.read()

    try:
        kpi_series = json.loads(raw)
    except json.JSONDecodeError as exc:
        print(f"kpi_memo_feed build: invalid JSON input: {exc}", file=sys.stderr)
        return 2

    if not isinstance(kpi_series, list):
        print(
            "kpi_memo_feed build: expected a JSON array (kpi_series), got "
            f"{type(kpi_series).__name__} — nothing computed",
            file=sys.stderr,
        )
        return 2

    try:
        feed = build_memo_feed(
            args.company, args.schema_version, kpi_series,
            generated_at=args.generated_at,
        )
    except ValueError as exc:
        print(f"kpi_memo_feed build: {exc}", file=sys.stderr)
        return 1

    json.dump(feed, sys.stdout, ensure_ascii=False)
    sys.stdout.write("\n")
    return 0


def _cli_build_quarterly(args: argparse.Namespace) -> int:
    """`build-quarterly` subcommand: read a `quarterly-series` payload
    object from `--file` (or stdin when omitted), call
    `build_quarterly_memo_feed` and print the 1.1 feed. Exit codes mirror
    `build`: malformed JSON or a non-object payload -> 2 (nothing
    computed); a provenance/DQC rejection (ValueError) -> 1; built -> 0.
    """
    if args.file is not None:
        raw = Path(args.file).read_text(encoding="utf-8")
    else:
        raw = sys.stdin.read()

    try:
        series_payload = json.loads(raw)
    except json.JSONDecodeError as exc:
        print(
            f"kpi_memo_feed build-quarterly: invalid JSON input: {exc}",
            file=sys.stderr,
        )
        return 2

    if not isinstance(series_payload, dict):
        print(
            "kpi_memo_feed build-quarterly: expected a JSON object (the "
            "quarterly-series payload), got "
            f"{type(series_payload).__name__} — nothing computed",
            file=sys.stderr,
        )
        return 2

    try:
        feed = build_quarterly_memo_feed(
            args.company, series_payload, generated_at=args.generated_at,
        )
    except ValueError as exc:
        print(f"kpi_memo_feed build-quarterly: {exc}", file=sys.stderr)
        return 1

    json.dump(feed, sys.stdout, ensure_ascii=False)
    sys.stdout.write("\n")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Memo-feed contract CLI (build, build-quarterly)."
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    build_parser = subparsers.add_parser(
        "build", help="Assemble the memo-feed contract for a company/schema_version."
    )
    build_parser.add_argument("--company", required=True)
    build_parser.add_argument(
        "--schema-version", required=True, dest="schema_version"
    )
    build_parser.add_argument(
        "--generated-at", default=None, dest="generated_at"
    )
    build_parser.add_argument(
        "--file", type=Path, default=None,
        help="Path to a JSON file holding the kpi_series array (default: read stdin).",
    )
    build_parser.set_defaults(func=_cli_build)

    quarterly_parser = subparsers.add_parser(
        "build-quarterly",
        help="Assemble the quarterly/XBRL-arm memo feed (envelope 1.1) "
             "from a quarterly-series payload.",
    )
    quarterly_parser.add_argument("--company", required=True)
    quarterly_parser.add_argument(
        "--generated-at", default=None, dest="generated_at"
    )
    quarterly_parser.add_argument(
        "--file", type=Path, default=None,
        help="Path to a JSON file holding the quarterly-series payload "
             "object (default: read stdin).",
    )
    quarterly_parser.set_defaults(func=_cli_build_quarterly)

    args = parser.parse_args()
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
