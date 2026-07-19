#!/usr/bin/env python3
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""
kpi_prose_candidates.py — investing-toolkit prose KPI candidate producer.

Sibling of the Route B table producer (kpi_8k_candidates.py), one layer BELOW the
LLM: it turns the canonical flattened EX-99 PROSE surface into RAW KPI candidate
points anchored to verbatim source bytes. As with the table route, the exact
printed token + source offsets never pass through an LLM; the SEMANTIC slots
(kpi_id / unit / period) are LLM-proposed and human-ratified downstream.

This file grows across Part-1 tasks (propose / gate / confirm / commit / store).
Landed so far: the mechanical `propose` producer (crossing to data-markets
`exhibit_prose` by SUBPROCESS, mirroring the sibling ↔ exhibit_tables) and the
anti-fabrication substring `passes_substring_gate` predicate below.

Anti-fabrication substring gate (the load-bearing trust rail):
  A prose candidate carries a VERBATIM matched token (the number exactly as
  printed, e.g. "1,576,000") plus a verbatim_quote snippet, alongside a NORMALIZED
  numeric `value` DERIVED from the token (comma-stripped, e.g. 1576000). The gate
  admits a candidate ONLY when its verbatim token AND its verbatim_quote are both
  literal substrings of the canonical exhibit text. It NEVER checks the normalized
  value — a printed "1,576,000" legitimately has no "1576000" anywhere in the
  source, so requiring the normalized form to appear would false-reject every
  separator-bearing number. Checking the verbatim token instead is what stops any
  layer (an LLM especially) from committing a value not present in the source.
"""
from __future__ import annotations

import json
import subprocess
import sys
import tempfile
from pathlib import Path

# The number LOCATOR is the data-markets prose surface producer
# (exhibit_prose.py). analysis-kpi reaches it by SUBPROCESS, not import — the
# analysis-* -> data-markets layer boundary is crossed by PROCESS, mirroring
# the sibling kpi_8k_candidates.run_exhibit_tables -> exhibit_tables.py
# crossing (and analysis-comps/scripts/etf_aggregator.py -> pack.py). Crossing
# by process keeps the boundary explicit, honors exhibit_prose's PEP-723
# declared env, and avoids mutating this process's global sys.path[0] (which
# would shadow stdlib — see docs/loom/memory, select.py shadowed stdlib
# select). analysis-kpi/scripts -> analysis-kpi -> skills ->
# data-markets/scripts.
_SCRIPT_DIR = Path(__file__).resolve().parent
_EXHIBIT_PROSE = (
    _SCRIPT_DIR.parent.parent / "data-markets" / "scripts" / "exhibit_prose.py"
)

# Explicit list of the SEMANTIC slots the LLM layer must fill before the human
# confirm-all gate lets a prose point commit (mirrors kpi_8k_candidates).
_SEMANTIC_FIELDS = ("kpi_id", "unit", "period")


def _normalize_value(token: str):
    """Normalize a PLAIN located token into its numeric `value`: strip thousands
    separators, then int for an integer token or float for a decimal one (e.g.
    "1,576,000" -> 1576000, "3.56" -> 3.56, "0" -> 0). PLAIN only — word-scale
    multipliers ("billion"/"million") are a later part and are NOT parsed here.
    """
    stripped = token.replace(",", "")
    return float(stripped) if "." in stripped else int(stripped)


def run_exhibit_prose(canonical_text: str) -> list[dict]:
    """Subprocess data-markets `exhibit_prose.py --locate` on `canonical_text`,
    returning its located-number list (`[{"token", "start", "end"}, ...]`).

    SUBPROCESS not import: the analysis->data-markets layer boundary is crossed
    by process (mirrors kpi_8k_candidates.run_exhibit_tables -> exhibit_tables.py
    and etf_aggregator.py -> pack.py). The locator's `--locate` mode runs on the
    given text VERBATIM (no re-flatten), so every returned offset stays relative
    to `canonical_text` — the anchor the substring gate verifies against. We hand
    it the text and an `--out` temp path and read the JSON back.
    """
    with tempfile.TemporaryDirectory() as tmp:
        text_path = Path(tmp) / "canonical.txt"
        out_path = Path(tmp) / "located.json"
        text_path.write_text(canonical_text, encoding="utf-8")
        proc = subprocess.run(
            ["uv", "run", str(_EXHIBIT_PROSE),
             "--locate", "--text", str(text_path), "--out", str(out_path)],
            capture_output=True, text=True, timeout=120,
        )
        if proc.returncode != 0:
            raise RuntimeError(
                f"exhibit_prose.py --locate failed: {proc.stderr[:300]}"
            )
        return json.loads(out_path.read_text(encoding="utf-8"))


def build_candidates(located_numbers: list[dict]) -> list[dict]:
    """Pure transform: the located-number list (already crossed the data-markets
    boundary) -> RAW candidate points. Each candidate carries ONLY mechanical
    fields — a `value` DERIVED from the verbatim token, the verbatim
    `matched_token`/`verbatim_quote`, and the `char_offset_span` anchor — with
    every SEMANTIC slot (kpi_id/unit/period) explicit null and
    `needs_semantic=True`. The value + coordinates are set here and NEVER pass
    through an LLM: that is the "values + coordinates never pass through the LLM"
    anti-fabrication contract (mirroring Route B's kpi_8k_candidates).

    Part 1 walking skeleton: `verbatim_quote` IS the matched token, and the
    advisory `unit_hint`/`period_hint` are present-but-null — sophisticated hint
    extraction is a later part and is deliberately NOT built here.
    """
    candidates: list[dict] = []
    for located in located_numbers:
        token = located["token"]
        candidates.append({
            "matched_token": token,
            "verbatim_quote": token,
            "value": _normalize_value(token),
            "char_offset_span": [located["start"], located["end"]],
            "unit_hint": None,
            "period_hint": None,
            "source_kind": "prose",
            "kpi_id": None,
            "unit": None,
            "period": None,
            "needs_semantic": True,
        })
    return candidates


def propose(canonical_text: str) -> list[dict]:
    """MECHANICAL prose-KPI producer: cross the data-markets boundary by process
    to locate the number tokens of the canonical prose surface, then wrap them
    into RAW candidate points. Thin caller over `run_exhibit_prose` (subprocess)
    + `build_candidates` (pure) — the split keeps the wrapping logic unit-
    testable without a subprocess (mirroring Route B's propose ->
    run_exhibit_tables + build_candidates).
    """
    return build_candidates(run_exhibit_prose(canonical_text))


def passes_substring_gate(candidate: dict, canonical_text: str) -> bool:
    """Return True iff the candidate's verbatim matched token AND its
    verbatim_quote are both literal substrings of `canonical_text`.

    The gate deliberately does NOT inspect the normalized numeric `value`: that
    field is DERIVED from the token (comma-stripped), so a source that prints
    "1,576,000" has no "1576000" to match — requiring it would false-reject every
    separator-bearing figure. Grounding the verbatim token + quote is the actual
    anti-fabrication guarantee; a token absent from the source is rejected.
    """
    matched_token = candidate.get("matched_token")
    verbatim_quote = candidate.get("verbatim_quote")
    # Fail-CLOSED on the STRING grounding fields: missing / None / "" all mean
    # "no verbatim grounding" -> reject. An empty token/quote would otherwise
    # slip through (`"" in text` is always True), admitting a candidate that
    # grounds nothing — the fail-OPEN direction this anti-fabrication rail exists
    # to prevent. NOTE: this falsy guard is correct ONLY for these string fields;
    # it must NOT be applied to the numeric `value` (a legitimate 0), per
    # docs/loom/memory/falsy-guard-rejects-legitimate-zero-provenance.md.
    if not matched_token or not verbatim_quote:
        return False
    return matched_token in canonical_text and verbatim_quote in canonical_text


def commit(candidates: list[dict], confirmed: bool = False) -> list[dict]:
    """Tier-① confirm-all trust GATE: return the candidates ACCEPTED for commit.

    A prose candidate is accepted for commit ONLY after an explicit human
    confirm-all (`confirmed=True`). There is NO auto-commit: `confirmed` defaults
    False, so an omitted/False confirm accepts NOTHING (the fail-CLOSED
    direction). Moving a candidate located->committed WITHOUT the human confirm
    step is ILLEGAL and refused here — this is the three-layer trust boundary
    (mechanical produce -> LLM propose -> HUMAN confirm) that keeps unratified
    candidates out of the store. Mirrors Route B's confirm idiom
    (kpi_8k_candidates.commit gates on a falsy `confirmed`); here the confirm-all
    is a single explicit parameter covering the set.

    Interim no-taxonomy filter: a confirmed candidate is accepted REGARDLESS of
    its (LLM-labeled or merely plausible) kpi_id — there is NO fixed-taxonomy
    check gating commit. A fixed KPI taxonomy is a deferred hardening, not a
    commit precondition.

    Scope: THIS is the GATE only — it produces the accepted-for-commit set. The
    ACTUAL append into kpi_store (with the prose anchor + attribution provenance
    shape) is Task 7, which will consume this accepted set; kpi_store is NOT
    imported or appended here.
    """
    if not confirmed:
        return []
    return list(candidates)


def _prose_candidate_to_point(candidate: dict, company: str,
                              confirmer: str, confirmed_at: str) -> dict:
    """Map a confirmed prose candidate to a kpi_store-shaped point.

    Mirrors Route B's kpi_8k_candidates._candidate_to_point: values + source
    coordinates pass through VERBATIM (never re-parsed); `company` is supplied
    by the caller (one filing = one company). The prose adaptations:

    - The offset anchor is the `source_cell_ref`-analog `prose:{start}-{end}`,
      built from the candidate's `char_offset_span`. It is a TRUTHY string, so
      the store's falsy-provenance guard (`if not point.get(field)`) admits it
      cleanly — the same reason Route B renders `table:{i}` rather than a bare
      index 0. No store guard is weakened here.
    - `source_table_id` has no prose analog (prose is not tabular); it carries
      the self-describing source-kind token `"prose"` — truthy, so the store's
      provenance guard is satisfied without a table locator (the offset lives
      in `source_cell_ref`). Same source-kind-prefixed shape as Route B's
      `table:<i>` and kpi_xbrl's `xbrl:companyfacts`.
    - `as_of` is the ACCESSION-derived filing date carried on the candidate,
      DISTINCT from the wall-clock `confirmed_at`. Both are passed IN (never
      read from the clock here) so the append is deterministic; the store
      rejects a wall-clock as_of, and this one is disclosure-anchored.
    - `verbatim_quote` + filing attribution (`source_document`, `filing_date`)
      + confirmer identity (`confirmer`, `confirmed_at`) ride along so a number
      surfaced later stays citable to its source bytes and its ratifier.
    """
    start, end = candidate["char_offset_span"]
    return {
        "company": company,
        "kpi_id": candidate["kpi_id"],
        "period": candidate["period"],
        "unit": candidate["unit"],
        "value": candidate["value"],
        "as_of": candidate["as_of"],
        "source_kind": "prose",
        "source_accession": candidate["source_accession"],
        "source_table_id": "prose",
        "source_cell_ref": f"prose:{start}-{end}",
        "verbatim_quote": candidate["verbatim_quote"],
        "source_document": candidate.get("source_document"),
        "filing_date": candidate.get("filing_date"),
        "confirmer": confirmer,
        "confirmed_at": confirmed_at,
    }


def commit_to_store(candidates: list[dict], company: str, confirmer: str,
                    confirmed_at: str, confirmed: bool = False) -> dict:
    """Append human-confirmed prose candidates into the EXISTING tier-① store.

    Closes the walking skeleton: mechanical produce (`propose`) -> LLM propose
    -> HUMAN confirm (`commit`) -> DURABLE store append (here). Composes the
    confirm-all GATE with the store append — ONLY the `commit`-accepted set
    reaches `kpi_store.append`. Fail-CLOSED: `confirmed` defaults False, so
    without an explicit human confirm-all NOTHING is appended (no bypass path
    that skips the confirm step and writes straight to the store).

    Each accepted candidate is mapped by `_prose_candidate_to_point` and handed
    to the UNMODIFIED `kpi_store.append`: the store's own provenance /
    accession-derived-as_of guards run un-weakened (a point that fails them
    raises, nothing is written). kpi_store / kpi_validate are neither imported-
    for-mutation nor reimplemented — the append reuses the existing store.
    Returns `{"committed": <n>}` (points appended this call).
    """
    accepted = commit(candidates, confirmed=confirmed)

    # Lazy sibling import (mirrors kpi_8k_candidates.commit): keep the mechanical
    # `propose`/`build_candidates` path free of the store dependency, and share
    # the same kpi_store module a caller/test resolves by name off this dir.
    if str(_SCRIPT_DIR) not in sys.path:
        sys.path.insert(0, str(_SCRIPT_DIR))
    import kpi_store

    committed = 0
    for candidate in accepted:
        kpi_store.append(
            _prose_candidate_to_point(candidate, company, confirmer, confirmed_at)
        )
        committed += 1

    return {"committed": committed}
