#!/usr/bin/env python3
# /// script
# requires-python = ">=3.10"
# dependencies = []
# ///
"""
TW filing envelope -> kpi_store DRIVER (TW-market kpi_store producer).

The TW analog of `kpi_xbrl_ingest`: the pure-compute mapper
`kpi_tw.tw_canonical_to_points` turns a canonical into store points and
`kpi_store.append` is the durable bitemporal store, but nothing joined them
for a TW filing. This thin driver closes that gap:

  TW filing envelope (canonical + facts + co_id/year/season/report_id)
    -> derive basis (C/A), as_of (board authorisation-for-issue date),
       and TW provenance from the filing coordinates
    -> kpi_tw.tw_canonical_to_points   (one point per KPI field per period)
    -> kpi_store.append                 (idempotent, append-only, no collapse)

INPUT SHAPE. The envelope pairs the canonical with the parsed facts and the
filing coordinates because `run_pipeline` (twse_ixbrl.py) emits the canonical
but NOT the parsed facts (twse_ixbrl.py:156), and `as_of` derivation reads the
auth-date FACT (not a canonical field). A caller (the live dogfood / pack_tw
wiring, Task 4) assembles the envelope from a fetched filing; this driver reads
what it is GIVEN.

PURITY. This module imports `kpi_tw` (pure-compute) and `kpi_store` (durable
store) — both same-dir siblings. It does NOT import any data-markets module
and does NOT reuse data-markets `cache_util`: the canonical + facts are handed
IN via the envelope JSON, never parsed here (the analysis↔data-markets layer
boundary, [[durable-store-mirrors-cache-util-not-imports-it]]). The store roots
under the DATA dir via `kpi_store` (honors `KPI_STORE_DIR`), reused unchanged.

IDEMPOTENCY. Each point's dedup key is the store's 5-tuple
`(company, kpi_id, period, as_of, source_accession)`; re-ingesting the same
filing re-derives identical keys, so `kpi_store.append` no-ops on every point —
a second run adds no duplicate.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

_SCRIPT_DIR = Path(__file__).resolve().parent
if str(_SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(_SCRIPT_DIR))

# TW iXBRL facts are a single filing's flat fact set (no dimensional axes) —
# the source_kind mirrors the US "companyfacts" (flat) lane, distinct from the
# US dimensional lane's "xbrl-dimensional".
_SOURCE_KIND = "xbrl-companyfacts"

# A TW iXBRL statement form (TIFRS = Taiwan-IFRS). Non-empty so the store's
# provenance guard passes; the exact string is display/lineage metadata only.
_SOURCE_FORM = "TIFRS-Q"


def _source_accession(co_id: str, year: int, season: int, report_id: str) -> str:
    """Synthesize the TW source_accession from the filing coordinates.

    TW MOPS filings have no SEC-style accession number, so the durable
    provenance id is composed from the filing's own coordinates:
    `twse:<co_id>:<year>Q<season>:<report_id>` (report_id = C 合併 / A 個體).
    Distinct filings therefore carry distinct accessions, and re-ingesting the
    SAME filing re-derives the SAME accession (the dedup-key stability
    idempotency relies on).
    """
    return f"twse:{co_id}:{year}Q{season}:{report_id}"


def ingest(filing: dict[str, Any]) -> dict[str, Any]:
    """Map one TW filing envelope to store points and append each.

    `filing` carries:
      - `canonical`: the twse_ixbrl `build_canonical` output (statement keys
        + per-field value-lists + parallel `_meta[field]["periods"]`);
      - `facts`: the parsed iXBRL facts (the auth-date fact lives here, not in
        the canonical) — the `as_of` source;
      - `co_id` / `year` / `season` / `report_id`: the filing coordinates.

    Derivations:
      - `basis` = `report_id` (C/A) — TW's only series discriminator;
      - `as_of` = `kpi_tw.extract_tw_authorisation_date(facts)` — the
        non-wall-clock board authorisation-for-issue date the store requires;
      - provenance = `company`(=co_id), `source_accession` (from coordinates),
        `source_form`, `source_kind`.

    Fails loud (ValueError) when a required coordinate is missing or `as_of`
    cannot be derived — a filing with no parseable authorisation date must NOT
    be written with a fabricated/absent `as_of` (the store would reject it, but
    naming the cause here is clearer than an opaque provenance rejection).

    Returns `{"company", "kpi_ids": [...sorted...], "appended": <n>}`.
    """
    import kpi_store
    import kpi_tw

    canonical = filing.get("canonical")
    if not isinstance(canonical, dict):
        raise ValueError(
            "kpi_tw_ingest: filing envelope missing a 'canonical' object — "
            "nothing to ingest"
        )
    facts = filing.get("facts") or []

    co_id = filing.get("co_id")
    year = filing.get("year")
    season = filing.get("season")
    report_id = filing.get("report_id")
    for name, value in (
        ("co_id", co_id), ("year", year), ("season", season), ("report_id", report_id),
    ):
        if value in (None, ""):
            raise ValueError(
                f"kpi_tw_ingest: filing envelope missing required coordinate "
                f"{name!r} — cannot derive TW provenance, nothing written"
            )

    basis = report_id
    as_of = kpi_tw.extract_tw_authorisation_date(facts)
    if not as_of:
        raise ValueError(
            "kpi_tw_ingest: no board authorisation-for-issue date in the "
            "filing facts — as_of must be a non-wall-clock disclosure date, "
            "nothing written"
        )

    provenance = {
        "company": str(co_id),
        "source_accession": _source_accession(str(co_id), year, season, report_id),
        "source_form": _SOURCE_FORM,
        "source_kind": _SOURCE_KIND,
    }

    points = kpi_tw.tw_canonical_to_points(canonical, basis, as_of, provenance)
    for point in points:
        kpi_store.append(point)

    kpi_ids = sorted({point["kpi_id"] for point in points})
    return {"company": str(co_id), "kpi_ids": kpi_ids, "appended": len(points)}


def _cli_ingest(args: argparse.Namespace) -> int:
    """`ingest` subcommand: read the TW filing envelope JSON at `--filing`,
    append every point to the store (honoring `KPI_STORE_DIR` via kpi_store),
    and print a one-line JSON summary. A rejection (ValueError from the store's
    provenance/as_of guards, a malformed envelope, or a missing auth date)
    propagates as a non-zero exit — fail loud, never a silent swallow.
    """
    filing = json.loads(args.filing.read_text(encoding="utf-8"))
    try:
        summary = ingest(filing)
    except ValueError as exc:
        print(f"kpi_tw_ingest ingest: {exc}", file=sys.stderr)
        return 1
    json.dump(summary, sys.stdout, ensure_ascii=False)
    sys.stdout.write("\n")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description=(
            "TW filing envelope -> kpi_store driver: derive basis/as_of/"
            "provenance, map the canonical to points, append each to the "
            "durable store (idempotent, honors KPI_STORE_DIR)."
        )
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    ingest_parser = subparsers.add_parser(
        "ingest",
        help=(
            "Append every KPI point from a TW filing envelope (canonical + "
            "facts + coordinates) to the kpi_store (honors KPI_STORE_DIR)."
        ),
    )
    ingest_parser.add_argument(
        "--filing", type=Path, required=True,
        help="Path to a JSON file holding the TW filing envelope.",
    )
    ingest_parser.set_defaults(func=_cli_ingest)

    args = parser.parse_args()
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
