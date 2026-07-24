#!/usr/bin/env python3
# /// script
# requires-python = ">=3.10"
# dependencies = []
# ///
"""
XBRL fact-pack -> kpi_store DRIVER (operational-kpi store-feed wiring).

The missing wiring: `kpi_xbrl.facts_to_points` is pure-compute (dict-in ->
list-of-points), and `kpi_store.append` is the durable bitemporal store, but
nothing joined them — a US ticker's dimensional fact-pack never reached the
store, so a tearsheet needed hand glue. This thin driver closes that gap:

  fetched dimensional fact-pack (pack_us.pack_kpi_quarterly shape)
    -> for each distinct dimensional SIGNATURE: derive a kpi_id
    -> kpi_xbrl.facts_to_points  (NON-collapsing — every vintage survives)
    -> kpi_store.append          (one durable point per vintage)

NO COLLAPSE. This routes through `facts_to_points`, NOT `resolve_binding` /
`_restatement_survivor` (those collapse cross-filing vintages to a single
survivor — which would erase the restatement the store's bitemporal † exists
to surface). Each vintage of one period lands as its own store point so the
store has >=2 vintages to disagree on.

PURITY. This module imports `kpi_xbrl` (pure-compute) and `kpi_store`; it adds
NO store-write path inside `kpi_xbrl.py` (that module stays pure). This mirrors
`kpi_prose_candidates.commit_to_store`'s shipped intra-skill "map candidates ->
append each" pattern.

kpi_id DERIVATION (`derive_kpi_id`) — a user-confirmed ONE-WAY-DOOR decision:
the id is derived DETERMINISTICALLY and INJECTIVELY from the FULL dimensional
signature (concept + every breakdown axis:member), never a human-authored slug
and never keyed on a single axis. A fact's identity is its FULL signature
(memory `match-kpi-on-full-dimensional-signature-not-one-axis`). The
`srt:ConsolidationItemsAxis` is treated as a SEPARATE reconciliation qualifier,
NOT a breakdown axis — folding it in would make every segment filer look
falsely cross-dimensioned. Distinct signatures -> distinct ids; the same
signature across vintages -> the same id (so they group). An EMPTY signature
(the top-level total) is OUT OF SCOPE this arc — the dimensional extractor
emits none; a flat fact, if present, is skipped.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

_SCRIPT_DIR = Path(__file__).resolve().parent
if str(_SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(_SCRIPT_DIR))

# Every dimensional fact-pack fact carries this trusted source_kind (mirrors
# tests/analysis/test_kpi_xbrl.py and kpi_gate.TRUSTED_SOURCE_KINDS).
_SOURCE_KIND = "xbrl-dimensional"

# The ConsolidationItemsAxis local-name after its `Axis` suffix is stripped and
# lowercased — a reconciliation QUALIFIER, excluded from the kpi_id signature.
_CONSOLIDATION_AXIS_LOCAL = "consolidationitems"


def _local_name(qname: str) -> str:
    """Local name of an XBRL QName: drop any `prefix:` (e.g. `us-gaap:` /
    `srt:`). A bare name passes through unchanged.
    """
    return str(qname).split(":")[-1]


def _strip_axis_member_suffix(name: str) -> str:
    """Strip a trailing `Axis` or `Member` suffix (canonical XBRL dimension
    naming) so the slug reads as the bare concept — never stripping the whole
    token (a name that IS the suffix is kept as-is).
    """
    for suffix in ("Axis", "Member"):
        if name.endswith(suffix) and len(name) > len(suffix):
            return name[: -len(suffix)]
    return name


def _slug_token(qname: str) -> str:
    """One signature token: local-name, Axis/Member suffix stripped, lowercased."""
    return _strip_axis_member_suffix(_local_name(qname)).lower()


def derive_kpi_id(concept: str, dimensions: dict) -> str:
    """Deterministic, injective kpi_id from the FULL dimensional signature.

    `concept` + every breakdown `axis=member` pair (axes sorted for
    determinism), each token reduced to its local-name with the Axis/Member
    suffix stripped and lowercased. The `ConsolidationItemsAxis` reconciliation
    qualifier is dropped from the signature (a segment filer is not cross-
    dimensioned by it). Shape: `<concept>__<axis>-<member>[__<axis>-<member>...]`
    — the `__`/`-` delimiters keep distinct signatures on distinct ids.

    An empty `dimensions` (the top-level total) yields the bare concept slug;
    that case is OUT OF SCOPE for the driver (skipped before this is called),
    but the function stays total.
    """
    parts = []
    for axis in sorted(dimensions):
        axis_token = _slug_token(axis)
        if axis_token == _CONSOLIDATION_AXIS_LOCAL:
            continue  # reconciliation qualifier, not a breakdown axis
        member_token = _slug_token(dimensions[axis])
        parts.append(f"{axis_token}-{member_token}")
    concept_token = _slug_token(concept)
    if not parts:
        return concept_token
    return concept_token + "__" + "__".join(parts)


def _signature_key(concept: str, dimensions: dict, consolidation) -> tuple:
    """Grouping key for one facts_to_points call: the exact selector a
    `_fact_matches` comparison keys on — concept, the breakdown dimensions, and
    the (falsy-normalized) consolidation qualifier — so each call filters to
    exactly one signature+qualifier and every matched vintage is appended.
    """
    return (
        concept,
        tuple(sorted(dimensions.items())),
        consolidation or None,
    )


def ingest_pack(fact_pack: dict, source_kind: str = _SOURCE_KIND) -> dict:
    """Map every distinct dimensional signature in `fact_pack` to a kpi_id and
    append EVERY matching fact's vintage as its own store point.

    Company identity is the ticker (`fact_pack["ticker"]`, the store/dump key),
    falling back to `fact_pack["company"]` for a bare captured pack that carries
    only the latter. Flat facts (empty `dimensions` — the top-level total) are
    skipped: OUT OF SCOPE this arc.

    Returns `{"company", "kpi_ids": [...sorted...], "appended": <n>}`.
    """
    import kpi_store
    import kpi_xbrl

    company = fact_pack.get("ticker") or fact_pack.get("company")
    if not company:
        raise ValueError(
            "kpi_xbrl_ingest: fact_pack missing both 'ticker' and 'company' — "
            "cannot key the store, rejected, nothing written"
        )

    # One selector per distinct (concept, breakdown-dimensions, consolidation);
    # facts_to_points filters the whole pack to it, so every vintage matching
    # the signature is emitted and appended.
    selectors: dict = {}
    for fact in fact_pack.get("facts", []):
        dimensions = fact.get("dimensions") or {}
        if not dimensions:
            continue  # flat top-level total — OUT OF SCOPE this arc
        concept = fact.get("concept")
        consolidation = fact.get("consolidation")
        key = _signature_key(concept, dimensions, consolidation)
        selectors.setdefault(
            key,
            {
                "concept": concept,
                "dimensions": dimensions,
                "consolidation": consolidation,
            },
        )

    appended = 0
    kpi_ids: set = set()
    # kpi_id -> the DISTINCT signature key that first claimed it. `selectors`
    # is already deduped by signature (same signature -> same dict entry), so
    # a second signature landing on an already-claimed kpi_id here is BY
    # CONSTRUCTION a distinct-signature collision, never a same-signature
    # vintage regroup — fail loud rather than silently merging two different
    # dimensional breakdowns into one durable store series.
    claimed_by: dict = {}
    for sig_key, match in selectors.items():
        kpi_id = derive_kpi_id(match["concept"], match["dimensions"])
        prior_sig = claimed_by.get(kpi_id)
        if prior_sig is not None and prior_sig != sig_key:
            raise ValueError(
                f"kpi_xbrl_ingest: kpi_id collision — distinct dimensional "
                f"signatures {prior_sig!r} and {sig_key!r} both derive "
                f"kpi_id {kpi_id!r}; refusing to silently merge two "
                f"different breakdowns into one store series"
            )
        claimed_by[kpi_id] = sig_key
        kpi_ids.add(kpi_id)
        points = kpi_xbrl.facts_to_points(
            fact_pack, kpi_id, match, company, source_kind
        )
        for point in points:
            kpi_store.append(point)
            appended += 1

    return {"company": company, "kpi_ids": sorted(kpi_ids), "appended": appended}


def _cli_ingest(args: argparse.Namespace) -> int:
    """`ingest` subcommand: read the fact-pack JSON at `--pack`, append every
    vintage to the store (honoring `KPI_STORE_DIR` via kpi_store), and print a
    one-line JSON summary. A rejection (ValueError from the store's provenance/
    as_of guards or a malformed pack) propagates as a non-zero exit.
    """
    fact_pack = json.loads(args.pack.read_text(encoding="utf-8"))
    summary = ingest_pack(fact_pack)
    json.dump(summary, sys.stdout, ensure_ascii=False)
    sys.stdout.write("\n")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description=(
            "XBRL fact-pack -> kpi_store driver: append each dimensional "
            "vintage as its own store point (no collapse)."
        )
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    ingest_parser = subparsers.add_parser(
        "ingest",
        help=(
            "Append every dimensional fact's vintage from a fact-pack to the "
            "kpi_store (honors KPI_STORE_DIR)."
        ),
    )
    ingest_parser.add_argument(
        "--pack", type=Path, required=True,
        help="Path to a JSON file holding the fetched dimensional fact-pack.",
    )
    ingest_parser.set_defaults(func=_cli_ingest)

    args = parser.parse_args()
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
