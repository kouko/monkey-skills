#!/usr/bin/env python3
"""kpi_us_statements.py — US as-reported statement-pack -> kpi_store point
adapter (pure-compute, plan Task 3,
docs/loom/plans/2026-07-26-us-as-reported-statement-lane.md).

Layer-2 producer helper for the US-market as-reported statement lane. This
module takes an ALREADY-FETCHED statement-pack envelope (the ## Notes PIN'd
shape: `{"pack", "ticker", "fetched_at", "source_kind", "company", "facts",
"coverage"}`) as a dict — it does NOT fetch from `data.sec.gov` and MUST NOT
import any data-markets module. Crossing the analysis<->data-markets
boundary is forbidden here ([[durable-store-mirrors-cache-util-not-imports-
it]], mirroring kpi_tw.py:1-13); the caller (Task 5's producer, wrapped by
Task 8's `pack_us.pack_statement_backfill`) fetches and shapes the pack in
the data layer and hands it in.

kpi_id IDENTITY — the load-bearing rule this module exists to encode: the id
is the filer's OWN qname VERBATIM, namespace preserved (`us-gaap:Revenues`
stays `us-gaap:Revenues`). There is NO slug derivation, no lowercasing, no
digest. The id IS the source key, so it is injective by construction with
respect to the CONCEPT axis — no derivation step can collapse two DIFFERENT
qnames onto one id (there is nothing to collide there: two facts can only
share a kpi_id by sharing the same qname, which is the same series by
definition). This is deliberate and DIFFERS from both
`kpi_xbrl_ingest.derive_kpi_id` (digests a dimensional signature — a fact's
identity there is the concept PLUS its breakdown axes) and
`kpi_tw._tw_kpi_id` (lowercases a canonical field name drawn from a
repo-owned allowlist, a LOSSY normalization needing its own injective
guard). Neither applies here: an as-reported statement fact carries no
breakdown dimensions (Task 5's pack is flat, annual, one value per
concept+period) and is keyed on the filer's own tag, not a repo-canonical
field name.

That kpi_id-derivation guarantee is narrower than "no duplicate handling is
needed": it says nothing about two facts that share BOTH the same concept
AND the same period — the PIN's `facts` shape does not forbid that, and
`_require_no_intra_pack_disagreement` below is the guard for it (see its
docstring for the polarity).

stdlib only.
"""
from __future__ import annotations

from typing import Any

# Mirrors kpi_tw.py's `_SOURCE_TABLE_ID` convention — one fixed provenance
# label for every point this producer emits (## Notes PIN, Task 3).
_SOURCE_TABLE_ID = "xbrl:companyfacts-statement"
_SOURCE_KIND = "xbrl-companyfacts"

# companyfacts reports every figure at full magnitude, so no rescaling is
# applied. Named rather than inlined because `_require_no_intra_pack_
# disagreement` compares raw `value`s and its safety argument DEPENDS on this
# being invariant — parameterizing scale must break that argument visibly.
_SCALE = 1


def store_company(pack: dict[str, Any]) -> Any:
    """The value every point of this pack is KEYED on in the store — the
    envelope's `ticker`, falling back to its `company`.

    PUBLIC (no leading underscore) because `kpi_us_statements_ingest` calls
    it too, and that is the whole point: the driver's malformed-envelope
    guard and its returned summary must name the SAME key the points are
    stamped with. Two expressions of "which field keys the store", one in
    the mapper and one in the driver, is how they drift apart.

    TICKER FIRST, mirroring `kpi_xbrl_ingest.ingest_pack` (kpi_xbrl_ingest.py:
    530, `fact_pack.get("ticker") or fact_pack.get("company")`, whose
    docstring states "Company identity is the ticker ... the store/dump key").
    That is not a local preference — it is the key a CONSUMER uses.
    `kpi_spine_view.derive_spine` reads a `kpi_store dump --company <C>`
    payload, and `<C>` must select ONE filer's whole history: the shipped
    dimensional/top-line lane already writes under the ticker, and
    `kpi_tw_ingest` (kpi_tw_ingest.py:143) keys TW points on `co_id`, that
    market's ticker-equivalent. All three markets therefore agree.

    THE TWO ENVELOPE FIELDS, and what each MEANS from here on:
      - `ticker` — the store/dump KEY. Set by `pack_us.pack_statement_
        backfill` (pack_us.py:1144), uppercased there, so the key is stable
        against a lowercase `--ticker aapl` invocation.
      - `company` — DISPLAY metadata: the SEC `entityName`
        (`sec_edgar_client.py:3757`). It stays on the envelope deliberately
        and is not to be deleted: `build_statement_backfill`'s CIK-decoy
        rejection names it, which is what makes that error readable ("this
        CIK belongs to X, not the ticker you asked for"). It is simply not
        an identity the store may be keyed on — an entity name is a
        display string that renames (a filer's legal name changes; the
        ticker is the stable handle), and keying on it SPLIT this lane's
        points away from every other lane's for the same filer.

    The fallback exists for a bare hand-fed pack carrying only `company`
    (the same allowance `kpi_xbrl_ingest` makes for a bare captured pack);
    every pack the shipped producer emits carries `ticker`.
    """
    return pack.get("ticker") or pack.get("company")


def _period_fields(fact: dict[str, Any]) -> tuple:
    """Map one PIN'd fact's period fields to the store's period identity
    fields: `(period_start, period_end, period_kind, period_label)`.

    `period_label` is the write-side dedup discriminator: kpi_store.append
    keys its idempotency 5-tuple on `point["period"]` (kpi_store
    `_DEDUP_KEY_FIELDS`), so a filing's current period and its prior-year
    comparative — which otherwise share every other field (same concept,
    same accession, same as_of) — MUST carry distinct `period` values or the
    store collapses them to one key and silently drops the comparative
    (mirrors `kpi_tw._period_fields`'s docstring precedent). An instant
    labels by its own date (there is no span to pair); a duration labels by
    `"<start>/<end>"` so two durations sharing an end but not a start (or
    vice versa) still get distinct labels.
    """
    if fact.get("period_kind") == "instant":
        end = fact.get("period_end")
        return None, end, "instant", end
    start = fact.get("period_start")
    end = fact.get("period_end")
    return start, end, "duration", f"{start}/{end}"


def _require_field(fact: dict[str, Any], field: str) -> Any:
    """Refuse a fact whose `field` is absent, None, or empty — mirrors
    `kpi_xbrl._require_field` (kpi_xbrl.py:479), same shape, same polarity.

    This is what makes the "every emitted point carries complete provenance"
    invariant REAL rather than incidental. `kpi_store.append` enforces the
    same completeness via `_require_provenance` (kpi_store.py:178), but it
    fires INSIDE the caller's per-point loop and each `append` commits
    independently — so a pack shaped `[valid, valid, incomplete]` would
    durably write the first two points and only then raise, a partial write
    into an append-only store that cannot be un-written. Checking here, at
    BUILD time, means such a pack never reaches an append loop at all: the
    whole pack is refused before a single point exists.

    The message names the offending fact (`concept` + `period_end`) so the
    rejection is actionable from stderr alone.
    """
    value = fact.get(field)
    if not value:
        raise ValueError(
            f"kpi_us_statements.us_statement_pack_to_points: fact missing "
            f"required {field!r} (concept={fact.get('concept')!r}, "
            f"period_end={fact.get('period_end')!r}) — rejected, never "
            f"fabricated, nothing written"
        )
    return value


def _require_value(fact: dict[str, Any]) -> Any:
    """Refuse a fact whose `value` is absent, None, or non-numeric — mirrors
    `kpi_xbrl._require_value` (kpi_xbrl.py:435-449), same shape, same
    polarity. `bool` is excluded even though Python's `bool` is an `int`
    subclass: a naive `isinstance(value, (int, float))` check would admit
    `True`/`False` as a legitimate reported figure.

    This checks ABSENCE and TYPE only, never truthiness — zero IS a
    legitimate value (a real reported figure, e.g. zero preferred
    dividends), so `if not value` would wrongly reject it.
    """
    if "value" not in fact or fact["value"] is None:
        raise ValueError(
            f"kpi_us_statements.us_statement_pack_to_points: fact missing "
            f"required 'value' (concept={fact.get('concept')!r}, "
            f"period_end={fact.get('period_end')!r}) — rejected, never "
            f"fabricated, nothing written"
        )
    value = fact["value"]
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise ValueError(
            f"kpi_us_statements.us_statement_pack_to_points: fact 'value' "
            f"is non-numeric ({value!r}, concept={fact.get('concept')!r}, "
            f"period_end={fact.get('period_end')!r}) — rejected, never "
            f"fabricated"
        )
    return value


def _require_no_intra_pack_disagreement(points: list[dict[str, Any]]) -> None:
    """Refuse two points in the SAME pack that coincide on the store's full
    dedup key (`kpi_store._DEDUP_KEY_FIELDS`: `company, kpi_id, period,
    as_of, source_accession`) but carry DIFFERENT values.

    This is `kpi_xbrl_ingest._require_no_stored_disagreement`'s
    (kpi_xbrl_ingest.py:446) same rule, applied INTRA-pack instead of
    against the store — the two lanes there arrive in separate calls and
    can only be compared through the store; here both facts are already in
    hand in one pack, so the check is a local scan, no store read needed.
    Same polarity:

      - same period + SAME `source_accession` + DIFFERENT value -> RAISE.
        Two facts for the same concept, period, AND accession are two
        parses of the SAME filing, so a mismatch means one of them is
        wrong — `kpi_store.append` would otherwise treat the second as a
        no-op and silently keep whichever arrived first.
      - same period + DIFFERENT `source_accession` -> never raise, whatever
        the values. That is a LEGITIMATE RESTATEMENT across filings — the
        dedup key does not coincide, so the store correctly appends BOTH as
        bitemporal history. This guard must never touch that case.
      - same full key AND the same `value` passes through undeduped, leaving
        idempotency to the store (documented choice, not an oversight).
        NOTE the scope: "harmless" holds for two IDENTICAL points. Two facts
        agreeing on the full key AND `value` but differing on a NON-key field
        (`unit`, `source_form`, an instant/duration `period_kind` mismatch)
        still collapse first-wins in the store and the second's differing
        field is silently lost — this guard compares `value` only, mirroring
        the store's own value-blindness on non-key fields.

    `scale` is not consulted here (unlike the store-layer guard, which goes
    through `kpi_store._canonical_value`): every point this module builds
    carries `_SCALE`, so raw `value` equality already IS canonical-value
    equality. That equivalence is why the constant exists rather than a bare
    literal at the emission site — the day someone parameterizes `scale`,
    this justification must break VISIBLY. It would otherwise fail SILENTLY
    in the dangerous direction: two points with the same raw `value` at
    different scales share the full dedup key, this guard sees equal values
    and does not raise, and the store keeps the first — a 10^n disagreement
    lost. (The reverse — one figure at two scales — only over-raises, which
    is loud.)
    """
    seen_values: dict[tuple, Any] = {}
    for point in points:
        key = (
            point["company"],
            point["kpi_id"],
            point["period"],
            point["as_of"],
            point["source_accession"],
        )
        if key in seen_values and seen_values[key] != point["value"]:
            raise ValueError(
                f"kpi_us_statements: value disagreement on one dedup key "
                f"concept={point['kpi_id']!r} period={point['period']!r} "
                f"accession={point['source_accession']!r} — "
                f"{seen_values[key]!r} vs {point['value']!r} within the "
                f"SAME statement pack; one of them is wrong, rejected, "
                f"nothing written"
            )
        seen_values[key] = point["value"]


def us_statement_pack_to_points(pack: dict[str, Any]) -> list[dict[str, Any]]:
    """Map a ## Notes PIN'd statement-pack envelope into kpi_store points —
    one point per (concept, period, ACCESSION) fact in `pack["facts"]`: the
    intra-pack dedup key above (`_require_no_intra_pack_disagreement`)
    already keys on `source_accession` alongside concept and period, so
    multiple accessions reporting the SAME window are restatement vintages
    the store keeps side by side, never collapsed at write time.

    `pack` is passed IN as a dict (this module never imports data-markets —
    the analysis<->data-markets boundary). Field derivations (## Notes PIN):
    `company` = `store_company(pack)`, i.e. the envelope's TICKER (see that
    function for why the entity name may not key the store);
    `kpi_id` = the fact's `concept` VERBATIM (namespace preserved, no
    transformation); `as_of` = the fact's `filed` date; `source_accession` =
    `accession`; `source_form` = `form`; `source_cell_ref` = `concept`
    (mirrors `kpi_id` — both point at the filer's own tag);
    `source_table_id` = `"xbrl:companyfacts-statement"`; `source_kind` =
    `"xbrl-companyfacts"` (a fixed literal, not read off the fact — matches
    the envelope's own declared `source_kind`); `scale` = 1 (companyfacts
    values are already base-scale, no magnitude folding needed); `unit` is
    copied from the fact verbatim.

    PROVENANCE COMPLETENESS IS ENFORCED, NOT ASSUMED. Every fact's `concept`
    and `accession` go through `_require_field` BEFORE its point is built,
    so this function either returns points that ALL carry a complete
    provenance triple (`source_accession`/`source_table_id`/
    `source_cell_ref`) or raises and returns none. Callers may rely on that:
    it is what lets a driver drain the returned list into
    `kpi_store.append` without the store's per-point `_require_provenance`
    (kpi_store.py:178) firing mid-loop and leaving a partial write. `as_of`
    is deliberately NOT validated here — see `_require_field`'s docstring
    and `kpi_us_statements_ingest`'s module docstring for where that check
    lives and why it lives there. `value` is separately validated by
    `_require_value` (absent/None/non-numeric all rejected, zero admitted)
    — not part of the provenance triple, but the same never-fabricated
    guarantee applied to the figure itself.

    Before returning, every point is checked against every other for a
    same-dedup-key value disagreement — `_require_no_intra_pack_disagreement`
    (see its docstring for the restatement-vs-fabrication polarity).
    """
    company = store_company(pack)

    points: list[dict[str, Any]] = []
    for fact in pack.get("facts", []):
        # Provenance completeness is checked HERE, before the point exists —
        # see `_require_field` for why the store's own identical check is
        # too late. `concept` feeds BOTH `kpi_id` and `source_cell_ref`;
        # `accession` feeds `source_accession`. `source_table_id` is a
        # module constant and needs no check. `value` is checked via
        # `_require_value` for the same never-fabricated reason — a bare
        # `.get("value")` would let an absent/None/non-numeric value ride
        # through as a durably-written point.
        concept = _require_field(fact, "concept")
        accession = _require_field(fact, "accession")
        value = _require_value(fact)
        period_start, period_end, period_kind, period_label = _period_fields(fact)
        points.append(
            {
                "company": company,
                "kpi_id": concept,
                "period": period_label,
                "period_start": period_start,
                "period_end": period_end,
                "period_kind": period_kind,
                "scale": _SCALE,
                "value": value,
                "as_of": fact.get("filed"),
                "source_accession": accession,
                "source_form": fact.get("form"),
                "source_table_id": _SOURCE_TABLE_ID,
                "source_cell_ref": concept,
                "source_kind": _SOURCE_KIND,
                "unit": fact.get("unit"),
            }
        )
    _require_no_intra_pack_disagreement(points)
    return points
