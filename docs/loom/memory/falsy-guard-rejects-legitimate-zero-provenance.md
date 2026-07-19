---
name: falsy-guard-rejects-legitimate-zero-provenance
description: A required-field/provenance guard written `if not point.get(field)` rejects a LEGITIMATE falsy value (integer 0, empty string) as "missing" — render the field as a truthy token at the producer boundary (e.g. table index 0 → `table:0`), or test `is None`, rather than weakening the guard to admit falsy-absent alike
type: gotcha
origin: feat-8k-earnings-kpi-intake T4 (8-K KPI confirm-gate commit, investing-toolkit 2.26.0, 2026-07-19)
---

The tier-① store's `kpi_store._require_provenance` refuses a point missing
any provenance field via `if not point.get(field)`. A Route B candidate's
`source_table_id` is the exhibit's integer table INDEX — and the very first
table is index `0`, which is falsy. So a perfectly-present provenance value
(`source_table_id == 0`) was read by the store's guard as "missing" and the
point was wrongly refused. The naive "fix" — loosen the guard to
`if point.get(field) is None` — would have WEAKENED the store's trust
guarantee (a genuinely-absent-but-falsy field, e.g. `""`, would then slip
through). Instead the producer boundary (`_candidate_to_point`) renders the
integer index as a truthy token `table:<i>` (so `table:0` is truthy), while a
genuinely-absent id stays `None` and is still refused by the un-weakened
guard. RED tests pin BOTH halves: integer-0 → `table:0` lands; `None` → refused.

**Why:** `if not x` conflates two different states — "x is absent" and "x is
a legitimate falsy value (0 / '' / False)". A required-field guard must reject
only the first. Weakening the guard to fix the false-reject re-opens the
false-accept; the correct fix is upstream — make the legitimate value
non-falsy at the boundary, or discriminate `is None` explicitly, so the guard
keeps rejecting true absence. Same falsy-test root as
[[tri-state-aggregate-filter-with-is-not-falsy]] (there the falsy test
miscounts the N/A state; here it misreads a legitimate 0 as missing).

**How to apply:** when a value that can be legitimately falsy (an integer
index, a count, an empty string) flows into a required-field / provenance /
presence guard that uses `if not value`, do NOT weaken the guard. Either
render the value as an unambiguously-truthy token at the producer seam (the
`table:0` pattern), or change the guard to discriminate absence explicitly
(`is None` / `field in point`). Pin both directions with tests: the legitimate
falsy value must PASS, a truly-absent field must still be REFUSED — one test
alone (only the pass, or only the refuse) leaves the other half unguarded.
Related: [[cache-key-collision-across-migration]] (same store-contract seam
class caught by a per-task reviewer tracing values, not by the happy-path test).
