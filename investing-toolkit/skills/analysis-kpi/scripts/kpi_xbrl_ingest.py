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
signature across vintages -> the same id (so they group).

TWO LANES. A pack may carry both kinds of fact, and they are routed apart:

  - the DIMENSIONAL lane (`dimensions` non-empty) keeps the derived signature
    id above and the `"xbrl-dimensional"` provenance label;
  - the TOP-LINE lane (`dimensions == {}`, the company total) lands in the ONE
    fixed canonical series `total_revenue` — NEVER `derive_kpi_id`'s bare-
    concept slug, which would tie a durable series identity to whichever
    concept string a filer happened to tag that year (memory
    `derived-durable-id-slug-is-a-lossy-one-way-door`). Its provenance comes
    from the envelope's declared `"source_kind"` when the pack carries one, and
    is `"xbrl-topline"` otherwise.

Both labels are checked against `kpi_gate.TRUSTED_SOURCE_KINDS` before any
write, and a top-line point that DISAGREES with an already-stored point on the
same dedup key is refused — see `_require_no_stored_disagreement` for the
polarity that separates a fabrication from a legitimate restatement.
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

# The FIXED canonical series identity for the company's top line. It names the
# ECONOMIC meaning, not the tag: a filer that switches from `us-gaap:Revenues`
# to the ASC-606 contract concept across years must stay ONE series.
_TOP_LINE_KPI_ID = "total_revenue"

# Provenance for flat top-line facts that arrive with NO envelope-declared kind
# (Lane B — the per-filing XBRL parse). Lane A's backfill pack declares
# `"xbrl-companyfacts"` on its envelope instead.
_TOP_LINE_SOURCE_KIND = "xbrl-topline"

# The whole top-line lane claims `_TOP_LINE_KPI_ID` under this ONE key, so the
# collision guard sees a single claimant no matter how many distinct flat
# concepts the pack carries. It is deliberately NOT a `_signature_key` tuple —
# no concept signature can equal it, so a DIMENSIONAL signature that somehow
# derived `total_revenue` would still collide and fail loud.
_TOP_LINE_CLAIM_KEY = ("<top-line>",)

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

    An empty `dimensions` (the top-level total) yields the bare concept slug.
    The driver never uses that value — a flat fact is routed to the fixed
    canonical `_TOP_LINE_KPI_ID` instead — but the function stays total.
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


def _consumer_consolidation(consolidation):
    """The consolidation qualifier as the CONSUMER sees it — delegated to
    `kpi_xbrl._normalize_consolidation`, the same function `_fact_matches`
    applies to both sides of its comparison. Named for the DIRECTION of that
    delegation (this driver asking its consumer) rather than for the operation,
    so it does not read as a near-homograph of the delegate it calls.

    Deliberate reach into a private name, mirroring `_require_no_stored_
    disagreement`'s use of `kpi_store._dedup_key`: the identity rule must be
    read from its owner, never restated here. A local copy of the default
    member would be a second definition free to drift from the one that
    actually decides which facts match.
    """
    import kpi_xbrl

    return kpi_xbrl._normalize_consolidation(consolidation)


def _signature_key(concept: str, dimensions: dict, consolidation) -> tuple:
    """Grouping key for one facts_to_points call: the exact selector a
    `_fact_matches` comparison keys on — concept, the breakdown dimensions, and
    the consolidation qualifier NORMALIZED THROUGH THE CONSUMER's own rule — so
    each call filters to exactly one signature+qualifier and every matched
    vintage is appended.

    The qualifier is normalized, not carried raw, because `_fact_matches`
    (`kpi_xbrl.py:428-432`) normalizes it on BOTH sides: an absent tag means the
    default `OperatingSegmentsMember` view, so to the consumer `None` and
    `"OperatingSegmentsMember"` ARE the same series. A raw key would split them
    into two selectors — and because each selector then matches BOTH variants'
    facts, that split is wrong in both directions at once: the collision guard
    OVER-FIRES on a pair the consumer would have merged correctly (aborting the
    whole ingest — the live INTC Lane B failure of 2026-07-25, where FY2026
    10-Qs dropped the ConsolidationItemsAxis tag their FY2023-25 predecessors
    carried), and were the guard absent, the two selectors would each hand
    `kpi_store.append` every matched fact TWICE. That second effect stops at the
    store: `append` is idempotent on the dedup key (`kpi_store.py:352-355`), so
    the durable record count is unchanged and the visible damage is a doubled
    `appended` count in this driver's CLI summary — a reporting lie plus wasted
    work, not durable corruption. The decision to collapse rests on the
    consumer's identity rule, not on that consequence. The guard's notion of
    "distinct" must equal the consumer's notion of "same"
    (`docs/loom/memory/derived-durable-id-slug-is-a-lossy-one-way-door.md`).

    Only the reconciliation-qualifier axis collapses, and only where the
    consumer collapses it. `concept` and the breakdown `dimensions` stay exact,
    so two genuinely distinct breakdowns deriving one kpi_id still trip
    `_claim_kpi_id` — and so do two NON-DEFAULT qualifier members (e.g.
    `OperatingSegmentsMember` vs `IntersegmentEliminationMember`), which
    `_normalize_consolidation` does NOT fold together. Dropping the qualifier
    from this key entirely would silently discard one of that pair; it is
    normalized here, never deleted (pinned by
    `test_ingest_raises_on_two_non_default_consolidation_members`).
    """
    return (
        concept,
        tuple(sorted(dimensions.items())),
        _consumer_consolidation(consolidation),
    )


def _claim_kpi_id(claimed_by: dict, kpi_id: str, claim_key: tuple) -> None:
    """Record that `claim_key` owns `kpi_id`, raising if a DIFFERENT key already
    claimed it. Both selector dicts are deduped by key (same key -> same dict
    entry), so a second key landing on an already-claimed kpi_id here is BY
    CONSTRUCTION a distinct-signature collision, never a same-signature vintage
    regroup — fail loud rather than silently merging two different breakdowns
    into one durable store series. The top-line lane claims once, under
    `_TOP_LINE_CLAIM_KEY`, so its many flat concepts never trip this.
    """
    prior_sig = claimed_by.get(kpi_id)
    if prior_sig is not None and prior_sig != claim_key:
        raise ValueError(
            f"kpi_xbrl_ingest: kpi_id collision — distinct dimensional "
            f"signatures {prior_sig!r} and {claim_key!r} both derive "
            f"kpi_id {kpi_id!r}; refusing to silently merge two "
            f"different breakdowns into one store series"
        )
    claimed_by[kpi_id] = claim_key


def _require_trusted_source_kinds(*source_kinds: str) -> None:
    """Reject any provenance label outside `kpi_gate.TRUSTED_SOURCE_KINDS` —
    checked BEFORE any point is built or written, so an untrusted kind can never
    ride into the durable store alongside trusted XBRL provenance (which is what
    `kpi_gate.attest_source` reads to grant TRUSTED without a labelled sample).
    """
    import kpi_gate

    untrusted = sorted(
        {kind for kind in source_kinds if kind not in kpi_gate.TRUSTED_SOURCE_KINDS}
    )
    if untrusted:
        raise ValueError(
            f"kpi_xbrl_ingest: source_kind(s) {untrusted!r} are outside "
            f"kpi_gate.TRUSTED_SOURCE_KINDS "
            f"({sorted(kpi_gate.TRUSTED_SOURCE_KINDS)!r}) — rejected, "
            f"nothing written"
        )


def _require_no_stored_disagreement(point: dict) -> None:
    """Refuse a top-line point that DISAGREES with an already-stored point on
    the SAME dedup key. The polarity here is the whole point, so it is spelled
    out:

      - same period + SAME `source_accession` (and same `as_of`) + DIFFERENT
        value -> RAISE. Both lanes read the SAME filing — `companyconcept` rows
        carry the same accession and filed date as the per-filing parse of that
        filing — so their dedup keys COINCIDE and one of them must be wrong.
        `kpi_store.append` would otherwise treat it as a no-op and keep the
        FIRST record (`kpi_store.py:321-325`): a wrong number stored silently.
      - same period + DIFFERENT `source_accession` + different value -> APPEND,
        never raise. That is a LEGITIMATE RESTATEMENT and rendering it is what
        the store's bitemporal `†` exists for. This mirrors the repo's shipped
        anti-fabrication raise (`kpi_xbrl._reduce_window_group`), which buckets
        values BY ACCESSION and fires only within a single accession.

    The check is STORE-AWARE rather than intra-pack because the two lanes arrive
    in SEPARATE `ingest_pack` calls, so the other lane's point is only visible
    through the store. `history` is a READ API (never-raise, no write). It
    matches by `same_period` over the RAW DATE PAIR, whereas `_dedup_key` keys
    on the period LABEL, so `history`'s candidate set is not a superset of the
    exact dedup key by construction — it is one in PRACTICE here, because both
    lanes read the window from the same filing's context and Lane A skips the
    New-Year-boundary rows where the two labelling rules could diverge (plan
    Task 3). If that upstream skip is ever relaxed, a divergent label would make
    this guard blind and the assumption must be re-derived.

    Values are compared through the store's OWN `_canonical_value`, not raw
    `!=`: `scale` is an explicit per-point field owned by each producer, and a
    scaled lane already exists in this store (`kpi_8k_candidates.py:332`).
    Comparing raw would both raise spuriously on one figure stored at two scales
    and miss a real 10^n disagreement — and would answer differently from the
    store's own `history`, which flags `disagreement` via `_canonical_value`.
    """
    import kpi_store

    stored = kpi_store.history(point["company"], point["kpi_id"], point)
    key = kpi_store._dedup_key(point)  # the store's OWN key definition (SSOT)
    for observation in stored["observations"]:
        if kpi_store._dedup_key(observation) != key:
            continue
        if kpi_store._canonical_value(observation) != kpi_store._canonical_value(point):
            raise ValueError(
                f"kpi_xbrl_ingest: top-line value disagreement on one dedup "
                f"key {key!r} — stored {observation.get('value')!r} vs "
                f"incoming {point.get('value')!r} from the SAME filing "
                f"(accession {point.get('source_accession')!r}); one of the "
                f"two lanes is wrong, so this is a fabricated restatement, "
                f"not a recast — rejected, nothing written"
            )


def ingest_pack(fact_pack: dict, source_kind: str = _SOURCE_KIND) -> dict:
    """Map every distinct signature in `fact_pack` to a kpi_id and append EVERY
    matching fact's vintage as its own store point.

    Company identity is the ticker (`fact_pack["ticker"]`, the store/dump key),
    falling back to `fact_pack["company"]` for a bare captured pack that carries
    only the latter.

    TWO LANES (see the module docstring): dimensional facts keep their derived
    signature id and `source_kind`; flat facts (empty `dimensions`) all land in
    the fixed canonical `_TOP_LINE_KPI_ID` series under the envelope-declared
    `"source_kind"` (default `_TOP_LINE_SOURCE_KIND`).

    THIS DRIVER's rejections — an untrusted provenance label, a kpi_id
    collision, a top-line value disagreement with the stored series — all fire
    BEFORE the first `kpi_store.append`, so a pack rejected by one of them
    writes nothing and leaves no partial state. That is why points are built in
    full first and appended after: without the split, a flat fact rejected at
    the END of a mixed pack would leave that pack's DIMENSIONAL points already
    committed to an append-only store. The claim is scoped to this driver:
    `kpi_store.append` enforces its OWN preconditions (provenance completeness,
    accession-derived `as_of`) inside the drain loop, and one of those firing
    mid-drain WOULD leave a partial write. That is unreachable through
    `facts_to_points` output, which always populates both, so it is a documented
    boundary rather than a live hole.

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

    # ABSENT means "undeclared, use the Lane B default"; an EMPTY/None declared
    # value is a MALFORMED envelope, not a default — it is passed through so
    # `_require_trusted_source_kinds` rejects it by name rather than silently
    # stamping `xbrl-topline` into durable provenance.
    declared_kind = fact_pack.get("source_kind")
    top_line_source_kind = (
        declared_kind if declared_kind is not None else _TOP_LINE_SOURCE_KIND
    )
    _require_trusted_source_kinds(source_kind, top_line_source_kind)

    # One selector per distinct (concept, breakdown-dimensions, consolidation);
    # facts_to_points filters the whole pack to it, so every vintage matching
    # the signature is emitted and appended. Flat facts get their own selector
    # dict: `_fact_matches` compares `concept` exactly, so a filer that switched
    # tagging still needs one call PER concept — they merely share one kpi_id.
    selectors: dict = {}
    top_line_selectors: dict = {}
    for fact in fact_pack.get("facts", []):
        dimensions = fact.get("dimensions") or {}
        concept = fact.get("concept")
        consolidation = fact.get("consolidation")
        key = _signature_key(concept, dimensions, consolidation)
        target = selectors if dimensions else top_line_selectors
        target.setdefault(
            key,
            {
                "concept": concept,
                "dimensions": dimensions,
                # The NORMALIZED qualifier, matching the key. Carrying the
                # first-seen RAW value would make the selector depend on fact
                # ORDER — harmless today (`_fact_matches` normalizes both sides,
                # so either raw value selects the identical fact set) but a
                # gratuitous order-dependence in a value that is stored and
                # passed onward.
                "consolidation": _consumer_consolidation(consolidation),
            },
        )

    kpi_ids: set = set()
    claimed_by: dict = {}  # kpi_id -> the key that claimed it
    pending: list = []

    for sig_key, match in selectors.items():
        kpi_id = derive_kpi_id(match["concept"], match["dimensions"])
        _claim_kpi_id(claimed_by, kpi_id, sig_key)
        kpi_ids.add(kpi_id)
        pending.extend(
            kpi_xbrl.facts_to_points(fact_pack, kpi_id, match, company, source_kind)
        )

    if top_line_selectors:
        _claim_kpi_id(claimed_by, _TOP_LINE_KPI_ID, _TOP_LINE_CLAIM_KEY)
        kpi_ids.add(_TOP_LINE_KPI_ID)
        for match in top_line_selectors.values():
            for point in kpi_xbrl.facts_to_points(
                fact_pack, _TOP_LINE_KPI_ID, match, company, top_line_source_kind
            ):
                _require_no_stored_disagreement(point)
                pending.append(point)

    for point in pending:
        kpi_store.append(point)

    return {"company": company, "kpi_ids": sorted(kpi_ids), "appended": len(pending)}


def _cli_ingest(args: argparse.Namespace) -> int:
    """`ingest` subcommand: read the fact-pack JSON at `--pack`, append every
    vintage of BOTH lanes (dimensional + top-line) to the store (honoring
    `KPI_STORE_DIR` via kpi_store), and print a one-line JSON summary. A
    rejection (ValueError from the store's provenance/as_of guards, this
    driver's untrusted-source-kind / kpi_id-collision / top-line
    value-disagreement guards, or a malformed pack) propagates as a non-zero
    exit.
    """
    fact_pack = json.loads(args.pack.read_text(encoding="utf-8"))
    summary = ingest_pack(fact_pack)
    json.dump(summary, sys.stdout, ensure_ascii=False)
    sys.stdout.write("\n")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description=(
            "XBRL fact-pack -> kpi_store driver: append each dimensional and "
            "top-line vintage as its own store point (no collapse)."
        )
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    ingest_parser = subparsers.add_parser(
        "ingest",
        help=(
            "Append every dimensional and flat top-line fact's vintage from a "
            "fact-pack to the kpi_store (honors KPI_STORE_DIR)."
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
