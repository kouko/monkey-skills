#!/usr/bin/env python3
# /// script
# requires-python = ">=3.10"
# dependencies = []
# ///
"""
XBRL fact -> kpi_store point adapter (operational-kpi tier-② XBRL pilot).

Layer 2 (Analysis) PURE-COMPUTE — mirrors kpi_parse.py / kpi_validate.py:
stdlib only, dict-in -> dict-out. This module is NOT a durable store: it
does NOT import `_store_fs`, does NOT resolve a store dir, does NOT lock
or write files, and touches neither the network nor an LLM.

`facts_to_points(fact_pack, kpi_id, match, company, source_kind)` selects
every fact in `fact_pack["facts"]` matching `match` (a
`{"concept", "dimensions"}` selector — `dimensions` compared by dict
EQUALITY, so an absent/empty `dimensions` matches only a flat fact's own
empty `dimensions`, i.e. the top-level total) and maps each matched fact
into a kpi_store-shaped point:

  - `source_accession` = fact `accession`
  - `source_table_id`  = `"xbrl:dimensional"` (fact has real breakdown
                          axes) or `"xbrl:companyfacts"` (fact `dimensions`
                          is empty, flat)
  - `source_cell_ref`  = `concept` (flat) or
                          `concept + "|" + <stable-sorted "axis=member" join>`
                          (dimensional, e.g.
                          `"concept|ProductOrService=StreamingMember"`)
  - `as_of`            = fact `filed`
  - `period`           = the fact's EMITTED `fiscal_year` label (Task 5,
                          docs/loom/plans/2026-07-16-operational-kpi-quarterly.md
                          — the data layer derives it per-fact from the fact's
                          own period_end against the filing's dei calendar,
                          dei-grounded and fail-loud; this module is a pure
                          CONSUMER of that label and never re-derives fiscal
                          geometry). NEVER `period_end[:4]` — that is the
                          CALENDAR year (the scope-B ruled latent bug: NVDA
                          FY2026-Q3 ends 2025-10-26), carried instead on each
                          point as the honest `calendar_year`/`calendar_quarter`
                          pair (the calendarization basis). And STILL never
                          edgartools' raw `fiscal_year` dataframe COLUMN, which
                          mislabels prior-year comparatives — the historical
                          trap holds; our derived label is distinguished from
                          that column by the full emitted label group
                          (`fiscal_year` + `fiscal_quarter` + `duration_months`):
                          a fact carrying a bare `fiscal_year` without its group
                          is treated as unclassifiable, never trusted.
  - `period_type`      = classified from the emitted labels (Task 5):
                          `fiscal_quarter` (Q1|Q2|Q3|Q4|FY) consumed as-is,
                          with `duration_class` (3mo|6mo-YTD|9mo-YTD|12mo-FY)
                          and the `cumulative` flag derived from
                          `duration_months` — see `classify_fact_period`.
  - `value`            = fact `value`
  - plus `company`, `kpi_id`, `source_kind`

The CORE property is FAIL-LOUD (mirrors kpi_parse's UnparseableCell
discipline): a matched fact missing `value`/`accession`/`filed`/`period_end`,
carrying a non-numeric `value`, or a malformed (non-YYYY-MM-DD) `period_end`,
RAISES a distinct `ValueError` naming the offending field — this module
never emits a fabricated `0` or a period `"None"`. A true numeric `0` is a
real value, not a missing one. Two further fail-loud branches (Task 5):
(a) a fact pack carrying an `error`/`error_class` slot (e.g. the
foreign-private-issuer `foreign_private_issuer_no_quarterly_xbrl` N/A) is
branched on BEFORE `facts` is read — it RAISES, never consumed as a real
empty series; (b) a fact missing the emitted label group (a pre-schema
stub, or a filing whose per-filing dei calendar was unreadable/None) is
surfaced as UNCLASSIFIABLE — never guessed from period_end/calendar
position, never keyed by the calendar year.

Task 6 adds a thin argparse CLI (`build`), mirroring `kpi_memo_feed.py`'s
CLI shape and fail-loud exit-code convention: reads a fact-pack JSON from
`--file`/stdin and a binding JSON from `--binding`, calls `resolve_binding`
and prints the resulting points. 0 on success; 1 on a `resolve_binding`
ValueError (e.g. ambiguous binding); 2 on malformed or non-object
fact-pack JSON (nothing computed, no raw traceback).
"""
from __future__ import annotations

import argparse
import json
import sys
from datetime import date
from pathlib import Path

# Resolve same-dir modules without a package (mirrors kpi_series.py's own
# import shim for kpi_break) so `import kpi_series` works both under
# `uv run --script` and importlib test loading. Only kpi_series is
# imported — NOT kpi_break: the declared/pre-applied break here
# intentionally bypasses kpi_break's persisted FLAGGED->CONFIRMED->APPLIED
# review-queue lifecycle.
_SCRIPT_DIR = Path(__file__).resolve().parent
if str(_SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(_SCRIPT_DIR))
import kpi_series  # noqa: E402


_DEFAULT_CONSOLIDATION_MEMBER = "OperatingSegmentsMember"

# Task 5 (scope B quarterly): period_type is CLASSIFIED from the data
# layer's emitted labels — `fiscal_quarter` ∈ {Q1..Q4, FY} consumed as-is,
# `duration_class` + the cumulative flag mapped from `duration_months`.
# The producer derives fiscal_quarter JOINTLY with the duration (a
# 12-month fact is FY, never a bare Q4), so the two must agree here.
_DURATION_CLASS_BY_MONTHS = {3: "3mo", 6: "6mo-YTD", 9: "9mo-YTD", 12: "12mo-FY"}
_CUMULATIVE_DURATION_CLASSES = frozenset({"6mo-YTD", "9mo-YTD"})
_FISCAL_QUARTERS = frozenset({"Q1", "Q2", "Q3", "Q4", "FY"})


def _unclassifiable(fact: dict, reason: str) -> ValueError:
    """A distinct, loud unclassifiable-fact error (spec: 'a transition or
    unclassifiable period is surfaced, not guessed'): the fact is SURFACED
    by name — period_type is never inferred from period_end/calendar
    position, the period key is never `period_end[:4]` (the calendar year),
    and a bare `fiscal_year` without its emitted label group (the old
    edgartools raw-column shape, unreliable for comparatives) is never
    trusted."""
    return ValueError(
        f"kpi_xbrl: fact is unclassifiable — {reason} "
        f"(concept={fact.get('concept')!r}, period_end="
        f"{fact.get('period_end')!r}, accession={fact.get('accession')!r}) "
        f"— surfaced, never guessed: no period_type is inferred and the "
        f"calendar year is never keyed in its place"
    )


def classify_fact_period(fact: dict) -> dict:
    """Classify one fact's `{period_type, cumulative, duration_class}` by
    CONSUMING the data layer's emitted label group — `fiscal_quarter` +
    `duration_months` + `fiscal_year` (Task 5; rebuild-findings §RESOLVED:
    the data layer derives, the analysis layer consumes — fiscal geometry
    is NEVER re-derived here). A comparative fact classifies from its OWN
    labels (the producer derives them per-fact, never the filing focus).

    Raises the distinct unclassifiable `ValueError` when the label group is
    missing/invalid (a pre-schema stub pack, or a filing whose dei calendar
    was unreadable — e.g. a `None` entry in the pack's `fiscal_calendars`
    leaves its facts with no derivable labels) or internally inconsistent
    (FY without a 12-month duration or vice versa — the producer derives
    them jointly, so disagreement is producer corruption, surfaced rather
    than resolved by guessing which label to trust)."""
    fiscal_year = fact.get("fiscal_year")
    fiscal_quarter = fact.get("fiscal_quarter")
    duration_months = fact.get("duration_months")
    if not isinstance(fiscal_year, int) or isinstance(fiscal_year, bool):
        raise _unclassifiable(fact, "missing/non-integer emitted fiscal_year label")
    if fiscal_quarter not in _FISCAL_QUARTERS:
        raise _unclassifiable(
            fact,
            f"missing/unknown emitted fiscal_quarter label ({fiscal_quarter!r})",
        )
    duration_class = _DURATION_CLASS_BY_MONTHS.get(duration_months)
    if duration_class is None:
        raise _unclassifiable(
            fact,
            f"missing/non-standard duration_months ({duration_months!r}, "
            f"expected one of {sorted(_DURATION_CLASS_BY_MONTHS)})",
        )
    if (fiscal_quarter == "FY") != (duration_class == "12mo-FY"):
        raise _unclassifiable(
            fact,
            f"inconsistent labels: fiscal_quarter={fiscal_quarter!r} with "
            f"duration_class={duration_class!r} (the producer derives them "
            f"jointly — a 12-month fact is FY, never a bare quarter)",
        )
    return {
        "period_type": fiscal_quarter,
        "cumulative": duration_class in _CUMULATIVE_DURATION_CLASSES,
        "duration_class": duration_class,
    }


def _require_facts(fact_pack: dict) -> list:
    """Read `fact_pack["facts"]` AFTER branching on an explicit error/N-A
    slot (Task 5, Wave-1 review finding): the data layer's gap-slot idiom
    (`error` + `error_class`, e.g. the foreign-private-issuer
    `foreign_private_issuer_no_quarterly_xbrl` N/A, which deliberately
    omits `facts`) must NEVER be consumed as a real empty series by a
    `.get()` default — exactly the silent-empty failure the slot exists to
    prevent (see `_foreign_private_issuer_na_slot`'s contract in
    sec_edgar_client.py)."""
    error_class = fact_pack.get("error_class")
    if error_class is not None or "error" in fact_pack:
        raise ValueError(
            f"kpi_xbrl: fact pack is an explicit error/N-A slot "
            f"(error_class={error_class!r}, identifier="
            f"{fact_pack.get('identifier')!r}): "
            f"{fact_pack.get('reason') or fact_pack.get('error')!r} — "
            f"never consumed as an empty series"
        )
    return fact_pack.get("facts", [])


def _normalize_consolidation(value):
    """Normalize a `consolidation` qualifier (srt:ConsolidationItemsAxis
    member): an absent/None value means the fact/source carries no
    reconciliation tag at all, which defaults to the top-level
    OperatingSegmentsMember view — never a distinct falsy category of its
    own. `consolidation` is a QUALIFIER, not a breakdown axis: it is never
    part of the `dimensions` equality check in `_fact_matches`.
    """
    return value if value else _DEFAULT_CONSOLIDATION_MEMBER


def _fact_matches(fact: dict, match: dict) -> bool:
    """EXACT-match a fact's full dimensional signature against `match` =
    `{concept, dimensions, consolidation}`. `dimensions` is compared by dict
    EQUALITY — a match with an empty/absent `dimensions` matches ONLY a fact
    whose own `dimensions` is empty (the top-level total); a fact carrying
    EXTRA breakdown axes beyond `match`'s does NOT match (de-conflates e.g.
    a NFLX streaming total from its per-region slices). `consolidation` is
    compared separately as a reconciliation QUALIFIER (normalized default
    "OperatingSegmentsMember" on both sides) — it is NEVER folded into the
    `dimensions` signature, so a segment binding is not falsely cross-dim.
    """
    return (
        fact.get("concept") == match.get("concept")
        and fact.get("dimensions", {}) == match.get("dimensions", {})
        and _normalize_consolidation(fact.get("consolidation"))
        == _normalize_consolidation(match.get("consolidation"))
    )


def _require_value(fact: dict) -> float:
    if "value" not in fact or fact["value"] is None:
        raise ValueError(
            f"kpi_xbrl.facts_to_points: fact missing required 'value' "
            f"(concept={fact.get('concept')!r}, fiscal_year="
            f"{fact.get('fiscal_year')!r}) — rejected, never fabricated as 0"
        )
    value = fact["value"]
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise ValueError(
            f"kpi_xbrl.facts_to_points: fact 'value' is non-numeric "
            f"({value!r}, concept={fact.get('concept')!r}, fiscal_year="
            f"{fact.get('fiscal_year')!r}) — rejected, never fabricated as 0"
        )
    return value


def _require_period(fact: dict) -> str:
    """The fact's series period key = its EMITTED `fiscal_year` label
    (Task 5 migration — `period_end[:4]` is the CALENDAR year, the ruled
    latent bug: NVDA's FY2026-Q3 ends 2025-10-26 and must key under 2026).
    Still validates `period_end` (the raw window stays a required,
    well-formed field) and requires the FULL label group via
    `classify_fact_period` — a bare `fiscal_year` without its group is the
    untrusted edgartools raw column, surfaced unclassifiable instead."""
    period_end = fact.get("period_end")
    if not isinstance(period_end, str) or not period_end:
        raise ValueError(
            f"kpi_xbrl.facts_to_points: fact missing required 'period_end' "
            f"(concept={fact.get('concept')!r}) — rejected, never fabricated "
            f'as period "None"'
        )
    try:
        date.fromisoformat(period_end)
    except ValueError:
        raise ValueError(
            f"kpi_xbrl.facts_to_points: fact 'period_end' is malformed "
            f"({period_end!r}, concept={fact.get('concept')!r}) — expected "
            f'YYYY-MM-DD, rejected, never fabricated as period "None"'
        ) from None
    classify_fact_period(fact)  # label-group guard; raises unclassifiable
    return str(fact["fiscal_year"])


def _require_field(fact: dict, field: str) -> str:
    value = fact.get(field)
    if not value:
        raise ValueError(
            f"kpi_xbrl.facts_to_points: fact missing required {field!r} "
            f"(concept={fact.get('concept')!r}, fiscal_year="
            f"{fact.get('fiscal_year')!r}) — rejected, never fabricated"
        )
    return value


def facts_to_points(
    fact_pack: dict,
    kpi_id: str,
    match: dict,
    company: str,
    source_kind: str,
) -> list[dict]:
    """Map every fact in `fact_pack["facts"]` matching `match` into a
    kpi_store-shaped point. See module docstring for the provenance
    mapping and the fail-loud field-by-field taxonomy.
    """
    points = []
    for fact in _require_facts(fact_pack):
        if not _fact_matches(fact, match):
            continue

        value = _require_value(fact)
        accession = _require_field(fact, "accession")
        filed = _require_field(fact, "filed")
        classification = classify_fact_period(fact)
        period = _require_period(fact)

        concept = fact.get("concept")
        dimensions = fact.get("dimensions") or {}

        if dimensions:
            source_table_id = "xbrl:dimensional"
            dims_joined = ",".join(f"{k}={v}" for k, v in sorted(dimensions.items()))
            source_cell_ref = f"{concept}|{dims_joined}"
        else:
            source_table_id = "xbrl:companyfacts"
            source_cell_ref = concept

        point = {
            "company": company,
            "kpi_id": kpi_id,
            "period_type": classification["period_type"],
            "cumulative": classification["cumulative"],
            "duration_class": classification["duration_class"],
            "period": period,
            # The parallel CALENDAR basis stays available on every point
            # (cross-company calendarization — rebuild-findings §RESOLVED),
            # honestly named, never conflated with the fiscal period key.
            "calendar_year": fact.get("calendar_year"),
            "calendar_quarter": fact.get("calendar_quarter"),
            "as_of": filed,
            "value": value,
            "source_accession": accession,
            "source_table_id": source_table_id,
            "source_cell_ref": source_cell_ref,
            "source_kind": source_kind,
        }
        # A cross-filing restatement (overlap policy C, resolved upstream in
        # resolve_binding) tags the kept fact with a machine-readable `dqc`
        # flag; carry it through onto the emitted point unchanged.
        if fact.get("dqc"):
            point["dqc"] = fact["dqc"]
        points.append(point)
    return points


def resolve_binding(fact_pack: dict, binding: dict, company: str) -> list[dict]:
    """Resolve a logical-KPI binding onto the fact-pack's full dimensional
    signatures: `binding` = `{kpi_id, sources: [{concept, dimensions,
    consolidation, source_kind}]}` (`consolidation` optional).

    A fact matches a source when `fact["concept"] == source["concept"]` AND
    `fact["dimensions"] == source["dimensions"]` EXACTLY (dict equality — an
    absent/empty `dimensions` matches ONLY the top-level total; a fact
    carrying extra breakdown axes does NOT match a narrower source) AND the
    fact's `consolidation` (srt:ConsolidationItemsAxis member — a
    reconciliation QUALIFIER, NEVER a breakdown axis) matches the source's
    `consolidation`, each normalized with default "OperatingSegmentsMember"
    when absent/None. A source may specify `consolidation` to disambiguate a
    non-default view (e.g. an eliminations view); otherwise a segment
    binding resolves the operating-segments view without falsely colliding
    with a different consolidation view sharing the same `dimensions`. A
    matched fact is emitted (via `facts_to_points`, reusing its provenance
    mapping) under the single logical `kpi_id`. A fact matching no source is
    skipped, never fabricated. A fact matching more than one source RAISES —
    an ambiguous binding. INVARIANT: exactly ONE point per (signature,
    period_type, period) — `period_type` is the CLASSIFIED fiscal quarter
    (Q1..Q4|FY, consumed from the emitted labels via `classify_fact_period`)
    and `period` is the emitted `fiscal_year` label (Task 5 — never the
    calendar year). When a single source's signature matches TWO OR MORE facts for
    the SAME period, they collapse to exactly one point — if every matched
    fact agrees on `value`, the identical duplicate(s) are DEDUPED down to
    one point (never double-counted downstream). If the matched facts
    DISAGREE on `value`, the disagreement is discriminated by ACCESSION
    (overlap policy C): a SINGLE accession reporting conflicting values for
    the same (signature, period) is a genuine INTRA-filing ambiguity and
    RAISES ValueError naming the kpi_id + period — never resolved
    arbitrarily; but a CROSS-filing disagreement (distinct accessions, as
    adjacent 10-Ks recast a value over the multi-filing span) is a
    RESTATEMENT — resolve_binding keeps the value from the most-recently-
    FILED 10-K (tie-break higher accession) and surfaces a machine-readable
    `dqc` restatement flag `{type, old, new, superseded_accession,
    kept_accession}` on the emitted point, rather than aborting the whole
    series. A period with exactly one matching fact resolves cleanly,
    unchanged.
    """
    kpi_id = binding["kpi_id"]
    sources = binding["sources"]

    facts_by_source_idx: list[list[dict]] = [[] for _ in sources]

    for fact in _require_facts(fact_pack):
        matched_indices = []
        for idx, source in enumerate(sources):
            selector = {
                "concept": source["concept"],
                "dimensions": source.get("dimensions", {}),
                "consolidation": source.get("consolidation"),
            }
            if _fact_matches(fact, selector):
                matched_indices.append(idx)

        if len(matched_indices) > 1:
            raise ValueError(
                f"kpi_xbrl.resolve_binding: fact matches {len(matched_indices)} "
                f"sources for kpi_id {kpi_id!r} (concept={fact.get('concept')!r}, "
                f"period_end={fact.get('period_end')!r}) — ambiguous binding, "
                f"never resolved arbitrarily"
            )
        if matched_indices:
            facts_by_source_idx[matched_indices[0]].append(fact)

    # Reduce each source's matched facts to exactly ONE fact per period: a
    # period with >1 matching fact that all AGREE on value is deduped down
    # to a single representative fact (never double-counted downstream as
    # two identical points); a period with matching facts that DISAGREE on
    # value RAISES (a genuine conflict, never resolved arbitrarily).
    deduped_facts_by_source_idx: list[list[dict]] = [[] for _ in sources]
    for idx, source in enumerate(sources):
        matched_facts = facts_by_source_idx[idx]
        by_period: dict[tuple[str, str], list[dict]] = {}
        for fact in matched_facts:
            # Task 5: the identity key is (classified period_type, emitted
            # fiscal_year) — never the calendar year of period_end.
            # LOOM-SIMPLIFY: shortcut=identity key omits duration_class, so a single-quarter and a YTD fact sharing one fiscal quarter+year collide on the key (surfaced via the value-disagreement RAISE below, never silently merged) | ceiling=first binding resolved over a fact pack carrying dual-duration facts for one signature (every real Q2/Q3 10-Q) | upgrade=extend the key with duration_class per plan Task 6 | ref=docs/loom/plans/2026-07-16-operational-kpi-quarterly.md §Task 6
            period_key = _require_period(fact)
            identity_key = (classify_fact_period(fact)["period_type"], period_key)
            by_period.setdefault(identity_key, []).append(fact)
        for (_, period_key), group in by_period.items():
            values = {fact.get("value") for fact in group}
            if len(values) == 1:
                # exactly one distinct value across the group (1 or more
                # identical facts) -> keep one representative for this period.
                deduped_facts_by_source_idx[idx].append(group[0])
                continue

            # The group DISAGREES on value. Discriminate an INTRA-filing
            # ambiguity (a SINGLE accession reporting conflicting numbers for
            # the same (signature, period) — a genuine defect, still fatal)
            # from a CROSS-filing restatement (overlap policy C): adjacent
            # 10-Ks over the multi-filing span recast the same value, which
            # must NOT abort the whole series.
            values_by_accession: dict[str, set] = {}
            for fact in group:
                values_by_accession.setdefault(
                    fact.get("accession"), set()
                ).add(fact.get("value"))
            if any(len(vals) > 1 for vals in values_by_accession.values()):
                raise ValueError(
                    f"kpi_xbrl.resolve_binding: signature for kpi_id {kpi_id!r} "
                    f"matches {len(group)} facts with different values for "
                    f"period {period_key!r} within a SINGLE filing "
                    f"(concept={source.get('concept')!r}) — intra-filing "
                    f"ambiguity, never resolved arbitrarily"
                )

            # Cross-filing restatement (policy C): keep the value from the
            # most-recently-FILED 10-K (tie-break higher accession) and tag
            # the superseded value onto the kept fact as a machine-readable
            # `dqc` restatement flag (carried through to the emitted point by
            # facts_to_points). The superseded fact is the most recent OLDER
            # fact whose value differs from the kept one.
            ordered = sorted(
                group,
                key=lambda f: ((f.get("filed") or ""), (f.get("accession") or "")),
            )
            kept = ordered[-1]
            superseded = next(
                fact
                for fact in reversed(ordered[:-1])
                if fact.get("value") != kept.get("value")
            )
            kept_with_dqc = dict(kept)
            kept_with_dqc["dqc"] = {
                "type": "restatement",
                "old": superseded.get("value"),
                "new": kept.get("value"),
                "superseded_accession": superseded.get("accession"),
                "kept_accession": kept.get("accession"),
            }
            deduped_facts_by_source_idx[idx].append(kept_with_dqc)

    points = []
    for idx, source in enumerate(sources):
        matched_facts = deduped_facts_by_source_idx[idx]
        if not matched_facts:
            continue
        sub_pack = {"company": fact_pack.get("company"), "facts": matched_facts}
        selector = {
            "concept": source["concept"],
            "dimensions": source.get("dimensions", {}),
            "consolidation": source.get("consolidation"),
        }
        points.extend(
            facts_to_points(sub_pack, kpi_id, selector, company, source["source_kind"])
        )
    return points


def build_series_with_break(points: list[dict], break_at_period: str) -> dict:
    """Split `points` at a declared structural boundary `break_at_period`,
    delegating to `kpi_series.split_series` (plain-args pure compute, NO
    persisted break lifecycle) — never a naive concatenation across a
    tagging-regime change.

    Builds a local `applied_breaks = [{"break_period": break_at_period}]`
    from the declared boundary and returns `split_series`'s dict
    (`{as_reported, recast, break_markers}`) unchanged. This is NOT a
    reimplementation of the partitioning logic — kpi_series.split_series
    owns it.
    """
    applied_breaks = [{"break_period": break_at_period}]
    return kpi_series.split_series(points, applied_breaks)


def _cli_build(args: argparse.Namespace) -> int:
    """`build` subcommand: read a fact-pack JSON from `--file` (or stdin
    when omitted) and a binding JSON from `--binding`, call
    `resolve_binding(fact_pack, binding, company)` and print the resulting
    points list. Mirrors `kpi_memo_feed._cli_build`'s exit-code contract:
    malformed JSON or a non-object fact_pack/binding -> 2 (nothing
    computed); a `resolve_binding` rejection (ValueError, e.g. an
    ambiguous binding) -> 1; success -> 0.
    """
    if args.file is not None:
        raw = Path(args.file).read_text(encoding="utf-8")
    else:
        raw = sys.stdin.read()

    try:
        fact_pack = json.loads(raw)
    except json.JSONDecodeError as exc:
        print(f"kpi_xbrl build: invalid fact-pack JSON input: {exc}", file=sys.stderr)
        return 2

    if not isinstance(fact_pack, dict):
        print(
            "kpi_xbrl build: expected a JSON object (fact_pack), got "
            f"{type(fact_pack).__name__} — nothing computed",
            file=sys.stderr,
        )
        return 2

    binding_raw = Path(args.binding).read_text(encoding="utf-8")
    try:
        binding = json.loads(binding_raw)
    except json.JSONDecodeError as exc:
        print(f"kpi_xbrl build: invalid --binding JSON: {exc}", file=sys.stderr)
        return 2

    if not isinstance(binding, dict):
        print(
            "kpi_xbrl build: expected a JSON object (--binding), got "
            f"{type(binding).__name__} — nothing computed",
            file=sys.stderr,
        )
        return 2

    try:
        points = resolve_binding(fact_pack, binding, args.company)
    except ValueError as exc:
        print(f"kpi_xbrl build: {exc}", file=sys.stderr)
        return 1

    json.dump(points, sys.stdout, ensure_ascii=False)
    sys.stdout.write("\n")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="XBRL fact -> kpi_store point adapter CLI (build)."
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    build_parser = subparsers.add_parser(
        "build",
        help="Resolve an era-specific binding against a fact-pack and print the points.",
    )
    build_parser.add_argument("--company", required=True)
    build_parser.add_argument(
        "--binding", type=Path, required=True,
        help="Path to a JSON file holding the binding ({kpi_id, sources: [...]}).",
    )
    build_parser.add_argument(
        "--file", type=Path, default=None,
        help="Path to a JSON file holding the fact_pack (default: read stdin).",
    )
    build_parser.set_defaults(func=_cli_build)

    args = parser.parse_args()
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
