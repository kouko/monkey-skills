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

# A feed-shape change here is a detectable migration, not a silent misread
# (mirrors kpi_store.STORE_SCHEMA_VERSION / kpi_schema.SCHEMA_ENVELOPE_VERSION
# / kpi_gate.GATE_ENVELOPE_VERSION).
MEMO_FEED_SCHEMA_VERSION = "1.0"

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


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Memo-feed contract CLI (build)."
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

    args = parser.parse_args()
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
