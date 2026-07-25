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
the id is derived deterministically from the FULL dimensional signature
(concept + every breakdown axis:member + a non-default consolidation
qualifier), never a human-authored slug and never keyed on a single axis. A
fact's identity is its FULL signature (memory
`match-kpi-on-full-dimensional-signature-not-one-axis`). It is injective UP TO
CASE, not absolutely: two signatures the consumer treats as distinct always
mint distinct ids, but two that differ ONLY in spelling case — a filer's 10-Q
vs 10-K tagging drift, e.g. `DataCenterMember` vs `DatacenterMember` — mint
the SAME id on purpose (`derive_kpi_id`'s own docstring documents the
case-folded digest that guarantees this). `_claim_kpi_id` mirrors that same
fold: it raises on a genuinely distinct claimant, but ACCEPTS a second
claimant whose claim key is case-insensitively equal to the incumbent's, so
both spellings' selectors feed the one shared series. The
`srt:ConsolidationItemsAxis` is treated as a SEPARATE reconciliation qualifier,
NOT a breakdown axis — folding it in would make every segment filer look
falsely cross-dimensioned, but a NON-DEFAULT member still discriminates the
id. The same signature across vintages -> the same id (so they group).

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
import hashlib
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
    token (a name that IS the suffix, in any case, is kept as-is).

    The suffix match is CASE-INSENSITIVE (`str.casefold()` on the trailing
    slice, not a raw `.endswith()`). Close-out finding (whole-branch review,
    feat-kpi-id-consolidation-axis): a case-sensitive match only stripped
    conventionally-cased spellings (`...Member`); a spelling whose case
    drift happened to land ON the suffix itself (e.g. `DataCenterMEMBER`,
    `DataCenterMember`'s all-caps 10-Q variant) kept the suffix attached,
    producing a readable PREFIX that disagreed with the DIGEST (which
    casefolds the whole raw string and was never suffix-sensitive) —
    minting a second kpi_id for the identical signature, invisible to the
    `_claim_kpi_id` guard because it is keyed on kpi_id and the two ids
    never meet (`test_derive_kpi_id_folds_every_spelling_of_one_identity`).
    """
    for suffix in ("Axis", "Member"):
        if len(name) > len(suffix) and name[-len(suffix):].casefold() == suffix.casefold():
            return name[: -len(suffix)]
    return name


def _slug_token(qname: str) -> str:
    """One signature token: local-name, Axis/Member suffix stripped, then
    CASEFOLDED (not merely lowercased) — `.casefold()` is the stricter fold
    for the identity-bearing half, agreeing with the digest on non-ASCII
    case (e.g. German sharp-s: `"Straße".casefold() == "STRASSE".casefold()
    == "strasse"`, whereas `.lower()` alone leaves them different strings).

    ORDER, re-verified at the same close-out that made the suffix match
    case-insensitive (see `_strip_axis_member_suffix`): strip-then-casefold
    (this call shape) and casefold-then-strip now produce the IDENTICAL
    output, because the suffix match itself is case-insensitive — it no
    longer matters which side of `.casefold()` it runs on. Before that fix,
    order WAS load-bearing (a case-SENSITIVE match had to see the un-folded
    original to recognize `Axis`/`Member` at all, e.g. `MEMBER` would not
    match if folding ran first without also folding the suffix literals).
    This keeps strip-then-fold, unchanged, only because there is no reason
    to reorder a working call with no behavioral difference either way.
    """
    return _strip_axis_member_suffix(_local_name(qname)).casefold()


def _ordered_breakdown_pairs(pairs) -> list:
    """Order `(axis, member)` breakdown pairs by their CASEFOLDED identity —
    never by raw (case-sensitive) text. This is the ONE sort both
    `_canonical_dimension_fold` (folded output, for the digest) and
    `derive_kpi_id`'s readable prefix (raw slug output) delegate to, so the
    prefix's token order agrees with the digest's identity BY CONSTRUCTION:
    two pair-sets that are byte-identical once folded but arrived in a
    DIFFERENT raw order — e.g. one selector's axis spelled `Alpha`, another's
    spelled `alpha`, which flips a raw `sorted()`'s ordering when a second
    axis is also present — must still land in the identical sequence here.
    """
    return sorted(pairs, key=lambda pair: (pair[0].casefold(), pair[1].casefold()))


def _canonical_dimension_fold(pairs) -> tuple:
    """The ONE canonical case-folded identity of a set of `(axis, member)`
    breakdown-dimension pairs: order by the casefolded key via
    `_ordered_breakdown_pairs` FIRST, then casefold each pair — never the
    reverse. Sorting after folding (not folding an already-sorted-by-raw-text
    order in place) is the whole point (see `_ordered_breakdown_pairs`).

    `derive_kpi_id`'s digest and `_casefold_claim_key`'s collision-guard
    comparison both call this ONE function rather than each re-deriving the
    fold, so "same identity under the CASE fold" is decided in exactly one
    place — the guard's notion of "distinct" must equal the consumer's (here,
    the digest's) notion of "same"
    (`docs/loom/memory/derived-durable-id-slug-is-a-lossy-one-way-door.md`).

    SCOPE, precisely: this unifies the CASE regime, not every axis decision.
    One divergence remains and is deliberate-for-now — `derive_kpi_id` drops
    `srt:ConsolidationItemsAxis` out of the breakdown pairs while
    `_signature_key` leaves it in, so a fact carrying that axis INSIDE
    `dimensions` (rather than in its own `consolidation` field) still yields
    one id but two claim keys, and the guard raises a FALSE collision. The
    shipped SEC producer cannot emit that shape — `_dimension_signature`
    allowlists four breakdown axes and routes the consolidation axis to its
    own field — so this is reachable only via a hand-built pack, and it fails
    LOUD rather than merging. Filed as a BACKLOG next-touch; do not assume the
    two key builders agree on anything but case.
    """
    return tuple(
        (axis.casefold(), member.casefold())
        for axis, member in _ordered_breakdown_pairs(pairs)
    )


def derive_kpi_id(concept: str, dimensions: dict, consolidation=None) -> str:
    """Deterministic, injective (up to case) kpi_id from the FULL dimensional
    signature.

    READABLE PREFIX: `concept` + every breakdown `axis=member` pair, ordered
    by `_ordered_breakdown_pairs`'s CASEFOLDED key (the same ordering the
    digest below uses) — never raw `sorted()` text, which two axis names
    differing only in case can flip relative to each other while folding to
    the identical identity — each token reduced to its local-name with the
    Axis/Member suffix stripped and CASEFOLDED. The `ConsolidationItemsAxis`
    reconciliation qualifier is EXCLUDED from that breakdown loop (a segment
    filer is not cross-dimensioned by it) but is not simply dropped:
    `consolidation` — the CONSUMER-normalized qualifier
    (`kpi_xbrl._normalize_consolidation`'s output, e.g. via `_signature_key`),
    never a raw fact value — appends its own `__<member-slug>` token when it
    is anything OTHER than the default `OperatingSegmentsMember` view,
    compared CASE-INSENSITIVELY so a differently-cased spelling of that same
    default (e.g. `OperatingsegmentsMember`) still adds no token. A default
    or absent (`None`) qualifier adds no token, so two facts differing only
    on that default-vs-absent distinction still fold to one id
    (`test_ingest_collapses_consolidation_variants_of_one_signature`); a
    genuinely NON-default member (e.g. `IntersegmentEliminationMember`)
    discriminates the id instead of silently merging into the default series
    (`test_ingest_splits_default_and_non_default_consolidation_into_distinct_series`
    pins the resulting two-series split).

    DIGEST: a 12-lowercase-hex sha1 of the CASE-FOLDED consumer identity
    tuple — `(concept.casefold(), sorted (axis.casefold(), member.casefold())
    breakdown pairs, normalized-consolidation.casefold())`, NUL-separated —
    is appended after a final `__`. This mirrors `kpi_store._series_key`'s
    readable-stem-plus-digest precedent (`kpi_store.py:71-92`): a readable
    prefix alone is not collision-proof (e.g. two dimension members whose
    local names happen to coincide after Axis/Member-suffix stripping), so a
    digest of the EXACT identity tuple is appended to guarantee two
    structurally distinct signatures never share an id. Case is FOLDED, not
    preserved, in that digest: the 47-filer probe
    (`tests/data/fixtures/kpi_id_identity_probe_2026-07-25.json`) measured 21
    series whose 10-Q and 10-K spellings of one member differ only by case
    (e.g. `DataCenterMember` vs `DatacenterMember`) — preserving case would
    permanently file each such series' quarterly history apart from its
    annual history in this append-only store, so the digest folds case the
    same way the readable prefix already does. `casefold()` — the stricter
    fold for the identity-bearing half — is used for BOTH the digest and the
    readable prefix's own tokens, so they agree on non-ASCII case too (e.g.
    German sharp-s: `Straße` vs `STRASSE`), not only on the ASCII XBRL names
    the observed corpus happens to carry. `consolidation` is normalized
    (`kpi_xbrl._normalize_consolidation`) before folding, so an absent
    qualifier and the explicit default member digest identically — matching
    the readable prefix's own fold.

    Shape: `<concept>__<axis>-<member>[__<axis>-<member>...]
    [__<consolidation-member>]__<12-hex-digest>` — the `__`/`-` delimiters
    keep distinct signatures on distinct ids, and the trailing digest makes
    that guarantee exact rather than merely readable-slug-shaped.

    An empty `dimensions` (the top-level total) still yields a full digest-
    suffixed id. The driver never uses that value — a flat fact is routed to
    the fixed canonical `_TOP_LINE_KPI_ID` instead — but the function stays
    total.
    """
    import kpi_xbrl

    breakdown_pairs = [
        (axis, dimensions[axis])
        for axis in dimensions
        if _slug_token(axis) != _CONSOLIDATION_AXIS_LOCAL
    ]
    # Ordered by the FOLDED key (same helper the digest uses below) so the
    # prefix's token order agrees with the digest's identity by construction
    # — never by raw `sorted()` text, which an axis name's case alone can
    # flip relative to another axis present in the same signature.
    parts = [
        f"{_slug_token(axis)}-{_slug_token(member)}"
        for axis, member in _ordered_breakdown_pairs(breakdown_pairs)
    ]
    concept_token = _slug_token(concept)
    prefix = concept_token if not parts else concept_token + "__" + "__".join(parts)
    if consolidation and consolidation.casefold() != (
        kpi_xbrl._DEFAULT_CONSOLIDATION_MEMBER.casefold()
    ):
        prefix += "__" + _slug_token(consolidation)

    folded_pairs = _canonical_dimension_fold(breakdown_pairs)
    normalized_consolidation = kpi_xbrl._normalize_consolidation(consolidation)
    digest_fields = [concept.casefold()]
    for axis_fold, member_fold in folded_pairs:
        digest_fields.append(axis_fold)
        digest_fields.append(member_fold)
    digest_fields.append(normalized_consolidation.casefold())
    digest = hashlib.sha1(
        "\x00".join(digest_fields).encode("utf-8")
    ).hexdigest()[:12]

    return f"{prefix}__{digest}"


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
    consumer collapses it. `concept` and the breakdown `dimensions` stay
    exact, so two genuinely distinct breakdowns deriving one kpi_id still
    trip `_claim_kpi_id`. The qualifier itself is normalized here, never
    dropped: two DIFFERENT NON-DEFAULT members (e.g.
    `IntersegmentEliminationMember` vs `CorporateNonSegmentMember` — neither
    is the default `OperatingSegmentsMember` view) are NOT folded together by
    `_normalize_consolidation`, so each keeps its own claim key — matching
    `derive_kpi_id`, which appends each non-default member's own token and so
    mints each its own kpi_id rather than colliding (pinned by
    `test_derive_kpi_id_discriminates_non_default_consolidation`'s
    `elimination`-vs-`corporate` assertion). Dropping the qualifier from this
    key entirely would instead make two such members share one claim key,
    silently discarding the distinction the consumer still draws between
    them.
    """
    return (
        concept,
        tuple(sorted(dimensions.items())),
        _consumer_consolidation(consolidation),
    )


def _casefold_claim_key(claim_key: tuple) -> tuple:
    """Case-fold every string component of a `_signature_key` claim key, so two
    claim keys that differ ONLY in letter case — INCLUDING an axis NAME's case,
    not just a member's — compare equal here, agreeing with `derive_kpi_id`'s
    own digest fold (Task 2) BY CONSTRUCTION rather than by coincidence of
    input order. The guard's notion of "same" must equal the id's notion of
    "same": since two spellings of one signature (e.g. `DataCenterMember` /
    `DatacenterMember`) now derive the IDENTICAL kpi_id, comparing claim keys
    on their raw (un-folded) text would read that as a distinct-signature
    collision and raise on exactly the fold the id derivation intends.

    The `dims` component is delegated to `_canonical_dimension_fold` — the
    SAME function `derive_kpi_id`'s digest calls — rather than casefolding
    each `(axis, member)` pair IN PLACE. `dims` arrives sorted by its RAW
    (case-sensitive) text (`_signature_key`'s `sorted(dimensions.items())`),
    the identical sort basis `derive_kpi_id`'s prefix uses; with >=2 axes, an
    axis NAME's case alone can flip that raw ordering between two selectors
    that the digest still folds identically. Casefolding in place — without
    re-sorting by the FOLDED value — would then compare the two pair-lists in
    mismatched element order and report them unequal, contradicting this
    function's own "mirrors the digest fold" invariant.
    """
    concept, dims, consolidation = claim_key
    return (
        concept.casefold(),
        _canonical_dimension_fold(dims),
        consolidation.casefold() if consolidation is not None else None,
    )


def _claim_kpi_id(claimed_by: dict, kpi_id: str, claim_key: tuple) -> None:
    """Record that `claim_key` owns `kpi_id`. A second key landing on an
    already-claimed kpi_id is ACCEPTED when it is case-insensitively equal to
    the incumbent's claim key — both selectors then feed the SAME store
    series, matching `derive_kpi_id`'s case-folded digest (Task 2): two
    spellings of one signature mint one id on purpose, so the guard must not
    raise on the exact pair the id derivation folds together.
    `_fact_matches` is untouched by this relaxation — each selector still
    exact-matches only its own spelling's facts, so the union of both
    selectors' facts is what lands under the shared id, never a superset.

    Every OTHER second claimant still raises: both selector dicts are deduped
    by key (same key -> same dict entry), so a case-insensitively DIFFERENT
    key landing on an already-claimed kpi_id here is BY CONSTRUCTION a
    distinct-signature collision, never a same-signature vintage regroup —
    fail loud rather than silently merging two different breakdowns into one
    durable store series. The top-line lane claims once, under
    `_TOP_LINE_CLAIM_KEY`, so its many flat concepts never trip this.
    """
    prior_sig = claimed_by.get(kpi_id)
    if prior_sig is not None and prior_sig != claim_key:
        if _casefold_claim_key(prior_sig) == _casefold_claim_key(claim_key):
            return
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
        kpi_id = derive_kpi_id(
            match["concept"], match["dimensions"], match["consolidation"]
        )
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
