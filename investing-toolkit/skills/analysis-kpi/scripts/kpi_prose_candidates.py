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
Task 4 lands ONLY the anti-fabrication substring gate below — a pure predicate.

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
