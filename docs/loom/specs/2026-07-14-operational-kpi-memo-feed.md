# Brief — operational-kpi slice 8: memo-feed contract (the final offline slice)

Status: brainstorming output, awaiting sign-off → `writing-plans`
Arc: US SEC primary-source layer — capability 3 (`operational-kpi`), **slice 8 of the
multi-slice program — the LAST offline slice** (the remaining work — LLM locate/parse,
HTML table extraction, XBRL cross-check — is the network/LLM layer that needs the pilot +
ground-truth decisions). Stacked on slice 7. Spec:
`docs/loom/2026-07-12-us-sec-primary-source-layer/specs/operational-kpi/spec.md`.

## Design-side on-ramp

Axis 0: brownfield increment; validated change-folder covers discovery. Proceed direct.

## Problem

**Job:** *When the memo pipeline asks for a company's operational-KPI data, I want ONE
defined, typed artifact — trusted series-points + their provenance + the trust/divergence
flags — and I want it to hand over a series ONLY when the reliability gate says TRUSTED;
otherwise it must surface an explicit WITHHELD status with the reason, never a partial or
fabricated series.* (The fail-closed anti-fabrication posture, all the way to the memo.)

This is the **capstone assembly** — the seam the memo pipeline consumes. It reads
`is_trusted` (slice 5's gate), bundles the break-aware series (slice 7), attaches each
point's provenance, and produces a defined-schema feed. A never-evaluated / below-bar
company yields a WITHHELD feed (surfaced), not a best-effort one.

## Users

**Job story:** *When I (the memo writer / investing-team) request a company's KPI feed, I
want a typed object `{company, schema_version, status, kpi_feeds | withheld_reason,
generated_at}` where status is TRUSTED (with the series + per-point provenance) or WITHHELD
(with the gate verdict as the reason, no series values) — so I can cite a trusted number
with its provenance, or surface the gap, but never invent one.*

Consumer: the memo pipeline / `domain-teams:investing-team`. This slice produces the
artifact; wiring it into the actual equity-memo pipeline (like the narrative/xval seams)
is a follow-on once the LLM extraction layer produces real series.

## Smallest End State

A new module `investing-toolkit/skills/analysis-kpi/scripts/kpi_memo_feed.py` (reuses
`kpi_gate` for the trust verdict; pure-assembly, takes the series data as an argument —
decoupled from kpi_store, mirroring kpi_validate/kpi_series):

1. **Fail-closed feed assembly** — `build_memo_feed(company, schema_version, kpi_series,
   generated_at)`: query `kpi_gate.is_trusted(company, schema_version)`. If NOT trusted →
   return `{"company", "schema_version", "status": "WITHHELD", "withheld_reason":
   <the gate verdict, e.g. WITHHELD/NOT_EVALUATED>, "kpi_feeds": [], "generated_at"}` — no
   series values (the gap is surfaced, never fabricated). If TRUSTED → bundle the supplied
   `kpi_series` (a mapping/list of the company's KPI series, each series' points passed in
   by the caller) into `{"status": "TRUSTED", "kpi_feeds": [{kpi_id, points:[...],
   provenance}...], ...}`.
2. **Explicit typed artifact** — the returned dict has a DEFINED schema (documented keys),
   never loose untyped values; a `_memo_feed_schema_version` marks it for evolution.
3. **Provenance completeness** — every included series-point in a TRUSTED feed must carry
   provenance (`source_accession`, `source_table_id`, `source_cell_ref`); a point missing
   provenance is REFUSED (fail loud) — never bundled unattributed (mirrors slice-1's
   store-side provenance rule, enforced again at the feed boundary the memo trusts).
4. A thin **CLI** — `build` (company + schema_version + kpi_series JSON → the feed JSON).

**Explicitly NOT in this slice:** the LLM locate/parse/extraction that PRODUCES the series
points (the network/LLM layer, needs pilot + ground-truth); wiring the feed into the real
equity-memo pipeline (a follow-on seam like narrative/xval); the narrative section paths
(those come from the existing sec_narrative seam, out of the operational-KPI module's
scope). This slice = the fail-closed typed feed assembly ONLY.

## Current State Evidence

- **Forward (consumer):** the equity-memo pipeline / investing-team will consume this
  artifact; not wired yet (needs the LLM extraction layer first).
- **Reverse (reuse):** `kpi_gate.is_trusted(company, schema_version)` (slice 5) is the
  trust gate this feed obeys — fail-closed (WITHHELD by default). The break-aware series
  the caller passes in comes from `kpi_series.series_view` (slice 7). This module reads
  `is_trusted` and ASSEMBLES; it does not itself query kpi_store (points passed in),
  mirroring kpi_validate's decoupling.
- **Error (fail-loud + no fabrication):** a non-TRUSTED company → WITHHELD feed, no values
  (surfaced, not fabricated); a TRUSTED point missing provenance → refused loud. Malformed
  input → loud CLI error; a WITHHELD feed is a NORMAL result.
- **Data (shapes):** spec Requirement "Memo-feed contract is an explicit artifact"
  (`operational-kpi/spec.md` :358) — "a defined artifact (path + schema) carrying trusted
  series-points, narrative section paths, divergence/furnished flags, and per-item
  provenance — never loose untyped values"; "Provenance completeness for every series-point"
  (:275); the withhold-below-bar posture (:249).
- **Boundary:** reuse `kpi_gate` (slice 5) for the verdict; do not re-implement trust logic.

Evidence paths: `investing-toolkit/skills/analysis-kpi/scripts/kpi_gate.py`,
`.../kpi_series.py`, `docs/loom/2026-07-12-us-sec-primary-source-layer/specs/operational-kpi/spec.md`.

## Decision

Build `kpi_memo_feed.py`: `build_memo_feed` produces a typed, defined-schema feed —
TRUSTED (series + per-point provenance, refusing any provenance-less point) when
`kpi_gate.is_trusted`, else WITHHELD (the gate verdict as reason, no series values);
+ a CLI. Reuse `kpi_gate` for the verdict; take the series data as an argument.

**We will NOT:** fabricate or best-effort a WITHHELD series; bundle a provenance-less
point; re-implement the trust gate (reuse is_trusted); produce the series points (LLM
layer); wire into the real memo pipeline (follow-on); read the wall clock (generated_at
caller-supplied).

## Alternatives Considered

Fork — **include-partial vs withhold-whole on a non-TRUSTED company** — resolved by the
spec ("withhold-below-bar … not a partial or best-effort series") + the anti-fabrication
intent: WITHHOLD the whole series, surface the gap. No external library fork; the assembly
is stdlib pure logic + one kpi_gate read.

## What Becomes Obsolete

Nothing removed — additive. This is the capability's downstream boundary; it makes the
slice-5 trust verdict and slice-1 provenance rule load-bearing at the memo hand-off.

## Out of Scope

- LLM locate/parse/extraction; XBRL cross-check; real memo-pipeline wiring; narrative
  section paths; non-US markets; archiving the change-folder (the LLM layer is still
  unshipped — archive only when the whole capability ships).

## Open Questions

1. **kpi_series input shape** — this slice takes `kpi_series` as a mapping `kpi_id →
   {points, provenance}` (or a list of such); the LLM/extraction layer will produce it.
   Confirm the minimal shape at plan time (each series carries its points + each point its
   provenance triple).
2. **generated_at** — caller-supplied timestamp (no wall-clock), consistent with every
   other module's determinism. Confirm.
