#!/usr/bin/env python3
# /// script
# requires-python = ">=3.10"
# dependencies = []
# ///
"""
US statement-pack envelope -> kpi_store DRIVER (US-market as-reported
statement lane producer, plan Task 9,
docs/loom/plans/2026-07-26-us-as-reported-statement-lane.md).

The US analog of `kpi_tw_ingest` (verbatim CLI-shape mirror, Kickoff
decision, plan ## Notes): `kpi_us_statements.us_statement_pack_to_points`
is pure-compute (envelope-in -> list-of-points) and `kpi_store.append` is
the durable bitemporal store, but nothing joined them for a US as-reported
statement pack. This thin driver closes that gap:

  US statement-pack envelope (## Notes PIN'd shape: pack/ticker/fetched_at/
  source_kind/company/facts/coverage)
    -> validate source_kind is TRUSTED (BEFORE building any point)
    -> kpi_us_statements.us_statement_pack_to_points  (one point per
       concept+period fact)
    -> validate every built point carries a derivable as_of
    -> kpi_store.append every point                     (idempotent,
       append-only, no collapse)

PURITY. This module imports `kpi_us_statements` (pure-compute), `kpi_gate`
(the trusted-source-kind vocabulary), and `kpi_store` (durable store) — all
same-dir siblings. It does NOT import any data-markets module: the
statement-pack envelope is handed IN as already-fetched JSON, never fetched
here (the analysis<->data-markets layer boundary, mirroring
kpi_tw_ingest.py:27-33 / [[durable-store-mirrors-cache-util-not-imports-
it]]). The store roots under the DATA dir via `kpi_store` (honors
`KPI_STORE_DIR`), reused unchanged.

GUARD ORDERING — build ALL points before the first append. This mirrors
`kpi_xbrl_ingest.ingest_pack`'s documented reasoning (kpi_xbrl_ingest.py:
514-524): this driver's own rejections (an untrusted `source_kind`, a
malformed envelope, a missing `as_of`) all fire BEFORE the first
`kpi_store.append`, so a pack rejected by one of them writes nothing and
leaves no partial state in the append-only store. Without that split, a
fact near the END of a multi-fact pack failing one of these guards would
leave the pack's EARLIER points already committed.

`kpi_store.append` enforces its OWN preconditions (provenance completeness,
non-wall-clock `as_of`) INSIDE the drain loop, and one of those firing
mid-drain WOULD leave a partial write. Each of those preconditions is
therefore established BEFORE the drain, and each in exactly ONE place:

  - provenance completeness (`source_accession`/`source_table_id`/
    `source_cell_ref`) — in the MAPPER, at build time.
    `kpi_us_statements._require_field` refuses a fact whose `concept` or
    `accession` is absent/empty (`source_table_id` is a module constant),
    mirroring `kpi_xbrl.facts_to_points`'s `_require_field`
    (kpi_xbrl.py:507). A pack that cannot yield complete points raises
    before a single point EXISTS, so it never reaches the loop below.
  - a derivable `as_of` — HERE, in `_require_as_of_present` (below), over
    every built point before the first append.

NO PRE-DRAIN PROVENANCE GUARD IN THIS DRIVER — a deliberate choice, not an
omission. `us_statement_pack_to_points` is the only producer of the points
this loop drains, and it now refuses to BUILD an incomplete one, so a
driver-side re-check could never fire: dead code that reads like the real
defence and would draw maintenance away from the seam where the invariant
actually holds. The asymmetry with `as_of` is the same principle applied
consistently: the mapper owns the fields ITS OWN derivations consume
(`concept` -> `kpi_id`/`source_cell_ref`, `accession` -> `source_accession`),
this driver owns `as_of`, and moving `filed` into the mapper too would
merely make `_require_as_of_present` the dead guard instead. Together the
two cover every store precondition reachable on this path, with no
duplicated check. Pinned by
`test_later_malformed_fact_leaves_the_earlier_points_unwritten`
(a valid fact FOLLOWED by a malformed one; asserts the store holds zero
points afterwards, not merely that something was raised).

SOURCE_KIND: ABSENT vs EMPTY/None. The envelope's own `source_kind` key
being ABSENT means "undeclared" and defaults to the PIN's mandatory trusted
literal (`_SOURCE_KIND`, matching `kpi_us_statements._SOURCE_KIND` and the
Task 8 `pack_us` envelope's mandatory literal). An EMPTY or explicit `None`
DECLARED value is a MALFORMED envelope, not a default — it is passed
through UNCHANGED so the trusted-kind check below rejects it BY NAME rather
than silently stamping the default into durable provenance (mirrors
`kpi_xbrl_ingest.ingest_pack`'s `declared_kind` handling, kpi_xbrl_ingest.py:
537-544).

IDEMPOTENCY. Each point's dedup key is the store's 5-tuple
`(company, kpi_id, period, as_of, source_accession)`; re-ingesting the same
statement pack re-derives identical keys, so `kpi_store.append` no-ops on
every point — a second run adds no duplicate.
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

# The PIN's mandatory top-level literal (## Notes, plan Tasks 3/8) — also
# the default when the envelope's own `source_kind` key is ABSENT
# (undeclared). Matches `kpi_us_statements._SOURCE_KIND`.
_SOURCE_KIND = "xbrl-companyfacts"


def _require_trusted_source_kind(source_kind: Any) -> None:
    """Reject a `source_kind` outside `kpi_gate.TRUSTED_SOURCE_KINDS` —
    checked BEFORE any point is built, so an untrusted kind can never ride
    into the durable store (mirrors `kpi_xbrl_ingest._require_trusted_
    source_kinds`, kpi_xbrl_ingest.py:426-443).
    """
    import kpi_gate

    if source_kind not in kpi_gate.TRUSTED_SOURCE_KINDS:
        raise ValueError(
            f"kpi_us_statements_ingest: source_kind {source_kind!r} is "
            f"outside kpi_gate.TRUSTED_SOURCE_KINDS "
            f"({sorted(kpi_gate.TRUSTED_SOURCE_KINDS)!r}) — rejected, "
            f"nothing written"
        )


def _require_as_of_present(points: list[dict[str, Any]]) -> None:
    """Reject the WHOLE pack if any built point carries no derivable
    `as_of` (the statement fact had no `filed` date) — checked over every
    point BEFORE the first append, so a pack with one underivable `as_of`
    writes nothing rather than leaving the earlier points already
    committed.
    """
    for point in points:
        if not point.get("as_of"):
            raise ValueError(
                f"kpi_us_statements_ingest: point for kpi_id="
                f"{point.get('kpi_id')!r} period={point.get('period')!r} "
                f"carries no derivable 'as_of' (the statement fact had no "
                f"'filed' date) — as_of must be accession/disclosure-"
                f"derived, rejected, nothing written"
            )


def ingest(pack: dict[str, Any]) -> dict[str, Any]:
    """Map one US statement-pack envelope to store points and append each.

    `pack` carries the ## Notes PIN'd shape: `pack`/`ticker`/`fetched_at`/
    `source_kind`/`company`/`facts`/`coverage`. Of those, `ticker` is the
    store/dump KEY and `company` (the SEC `entityName`) is display metadata
    — `kpi_us_statements.store_company` owns that rule for both this driver
    and the mapper.

    Guard ordering (see module docstring): the envelope's `source_kind` is
    validated FIRST (before any point is built); then the envelope's
    structural completeness (a resolvable store key, `facts`); then every
    point is built via `kpi_us_statements.us_statement_pack_to_points`
    (which itself refuses an incomplete-provenance fact and an intra-pack
    value disagreement — raising before any point exists); then every built
    point's `as_of` is checked present; only then does the append loop run.

    Returns `{"company", "kpi_ids": [...sorted...], "appended": <n>}` —
    `company` being the key the points were STORED under, so the operator
    can `kpi_store dump --company <that value>` and get what they just
    ingested.
    """
    import kpi_store
    import kpi_us_statements

    # ABSENT means "undeclared, use the PIN's mandatory default"; an
    # EMPTY/None DECLARED value is a MALFORMED envelope, not a default (see
    # module docstring) — passed through so `_require_trusted_source_kind`
    # rejects it by name.
    source_kind = pack["source_kind"] if "source_kind" in pack else _SOURCE_KIND
    _require_trusted_source_kind(source_kind)

    # The store KEY, resolved by the mapper's own `store_company` rather than
    # re-expressed here: this driver's guard and summary must name the exact
    # value the points are stamped with, and two copies of "which envelope
    # field keys the store" is precisely how this lane once split away from
    # the shipped one (see that function).
    company = kpi_us_statements.store_company(pack)
    if not company:
        raise ValueError(
            "kpi_us_statements_ingest: envelope missing both 'ticker' and "
            "'company' — cannot key the store, nothing written"
        )

    facts = pack.get("facts")
    if not isinstance(facts, list):
        raise ValueError(
            "kpi_us_statements_ingest: envelope missing a 'facts' list — "
            "nothing to ingest"
        )

    points = kpi_us_statements.us_statement_pack_to_points(pack)
    _require_as_of_present(points)

    for point in points:
        # NO PRE-DRAIN PROVENANCE GUARD here relies on `points` having come
        # ONLY from `us_statement_pack_to_points` (module docstring). If a
        # future edit adds a SECOND `kpi_store.append` call site inside
        # `ingest()` that bypasses the mapper, that call site would reopen
        # the partial-write hole with nothing LOCAL in this loop to catch
        # it — the mapper's build-time checks are this driver's only
        # defence, and they only cover points the mapper itself built.
        kpi_store.append(point)

    kpi_ids = sorted({point["kpi_id"] for point in points})
    return {"company": str(company), "kpi_ids": kpi_ids, "appended": len(points)}


def _cli_ingest(args: argparse.Namespace) -> int:
    """`ingest` subcommand: read the US statement-pack envelope JSON at
    `--filing`, append every point to the store (honoring `KPI_STORE_DIR`
    via kpi_store), and print a one-line JSON summary. A rejection
    (ValueError from this driver's source_kind/envelope/as_of guards, or
    the store's own provenance/as_of guards) propagates as a non-zero exit
    — fail loud, never a silent swallow.
    """
    pack = json.loads(args.filing.read_text(encoding="utf-8"))
    try:
        summary = ingest(pack)
    except ValueError as exc:
        print(f"kpi_us_statements_ingest ingest: {exc}", file=sys.stderr)
        return 1
    json.dump(summary, sys.stdout, ensure_ascii=False)
    sys.stdout.write("\n")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description=(
            "US statement-pack envelope -> kpi_store driver: validate "
            "source_kind, map the pack via kpi_us_statements, append each "
            "point to the durable store (idempotent, honors KPI_STORE_DIR)."
        )
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    ingest_parser = subparsers.add_parser(
        "ingest",
        help=(
            "Append every KPI point from a US statement-pack envelope to "
            "the kpi_store (honors KPI_STORE_DIR)."
        ),
    )
    ingest_parser.add_argument(
        "--filing", type=Path, required=True,
        help="Path to a JSON file holding the US statement-pack envelope.",
    )
    ingest_parser.set_defaults(func=_cli_ingest)

    args = parser.parse_args()
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
