# Brief — operational-kpi slice 1: append-only bitemporal KPI store

Status: brainstorming output, awaiting sign-off → `writing-plans`
Arc: US SEC primary-source layer — capability 3 (`operational-kpi`), **slice 1 of a
multi-slice program**. The capability's validated spec is
`docs/loom/2026-07-12-us-sec-primary-source-layer/specs/operational-kpi/spec.md`
(~30 requirements / 72+ scenarios — far past loom's critical-path depth ≤5, so it
ships as a SEQUENCE of thin briefs, not one plan). This brief is the first slice:
the persistence substrate every later slice writes to.

## Design-side on-ramp

Axis 0: brownfield increment to an existing toolkit. A **validated loom-spec
change-folder already exists** for the whole capability (discovery/spec fan-out done,
`validate_spec_output.py`-clean). No new product/UI/principles surface is opened by
this slice — it realizes a subset of already-specced requirements. Proceed direct to
loom-code. On-ramp table rows 1-4: none fire (spec + change-folder already cover the
problem/users/spec surface).

## Problem

**Job:** *When any later operational-KPI slice produces a validated KPI value, I want
a place to persist it that never loses history — so a later restatement or
re-extraction adds a new record instead of overwriting the old one, and a memo re-run
"as of" an earlier date sees only what was known then (no look-ahead bias).*

Everything downstream in the operational-KPI pipeline (locate → parse → validate →
**store** → gate → feed memo) writes to this store. Without it, no later slice has
anywhere to land a point. It is the keystone, and it is pure/offline — no LLM, no
network, no domain decision needed to build it.

## Users

**Job story:** *When the KPI pipeline validates a series-point for
(company, kpi_id, period), I want to append it keyed by an accession-derived `as_of`
with full provenance, so that (a) re-processing the same filing is a no-op, (b) an
amendment appends a superseding record without erasing the original, and (c) a
point-in-time query returns exactly what was known as of a given date.*

Consumers (all later slices): the KPI validation/promotion step (appends), the
reliability-gate + memo-feed steps (query latest / point-in-time). No human UI — this
is a library module with a thin CLI, mirroring the other `analysis-*` scripts.

## Smallest End State

A new `investing-toolkit/skills/analysis-kpi/` skill housing one module,
`scripts/kpi_store.py`, that provides:

1. **Append-only bitemporal store** — `append(point)` where a point is keyed by
   `(company, kpi_id, period, as_of)`; persisted as **file-per-series JSON** (one file
   per `company`+`kpi_id`, holding a list of point records). The store resolves its own
   **durable DATA dir** (XDG_DATA_HOME ladder → `~/.local/share/investing-toolkit/
   kpi-store`), NOT `cache_util.resolve_cache_dir()` — that returns the *cache* dir
   (`~/.cache`, evictable), and a bitemporal series is irreplaceable history that must
   survive cache eviction. It uses **self-contained helpers that mirror cache_util's
   key-sanitization regex + atomic tmp-rename write PATTERN** (not a cross-skill
   `import cache_util` — cross-skill direct import is not this repo's pattern; analysis
   skills reach data-markets via subprocess, and importing into the analysis layer
   would breach the layer boundary). Never mutates or deletes an existing record.
2. **Idempotent append with an explicit dedup key** — dedup on
   `(company, kpi_id, period, as_of, source_accession)`; re-appending the identical
   accession with no correction is a **no-op**, not a second indistinguishable point.
3. **`as_of` is accession/disclosure-derived, not wall-clock** — the store validates
   that each point carries an explicit `as_of` sourced from the filing, and rejects a
   wall-clock-stamped point (avoids the PR #543 clock-mismatch class).
4. **Provenance completeness or reject** — a point missing `source_accession`,
   `source_table_id`, or `source_cell_ref` is refused at append (fail loud), never
   stored unattributed.
5. **Point-in-time + latest queries** — `query_point_in_time(company, kpi_id, period,
   as_of_date)` returns only records with `as_of <= as_of_date` (the record with the
   greatest such `as_of`); `query_latest(company, kpi_id, period)` returns the greatest
   `as_of` overall.
6. **Concurrency-safe append** — serialize concurrent writes to a series file
   (file lock / atomic append) so two runs for the same company cannot lose an append
   or corrupt the file.

A thin `kpi_store.py` CLI surface (append / query subcommands) declared in the skill,
so the new verbs are visible at the command surface (runnable-capability note).

**Explicitly NOT in this slice** (later slices): HTML table extraction/classification;
KPI schema propose→confirm; LLM locate; deterministic parse; rule validation; XBRL
cross-check; review-item queue; break-event detection/adjudication; reliability-gate
evaluation; memo-feed contract; observability. This slice is the store + its queries
ONLY. The dual as-reported/recast split (break-aware series) is deferred — this slice
stores flat bitemporal points; the break/recast lineage layer is a later slice, so the
`lineage`/`restates` fields are **persisted if present** but not yet interpreted.

## Current State Evidence

- **Forward (who will call it):** no consumer exists yet — this slice ships the store
  ahead of its callers (keystone-first). The pipeline orchestrator that will call
  `append`/`query_*` is a later slice. So Forward is intentionally empty for now; the
  CLI is the exercisable surface this slice ships.
- **Reverse (SSOT / convention ownership):** `data-markets/scripts/cache_util.py`
  (`:66` `resolve_cache_dir`, `:170` `cache_path` key-sanitization, `:225` `save_cache`
  atomic tmp+rename) is the **canonical persistence-PATTERN reference** — the store
  MIRRORS its XDG-ladder+writability-gate structure, its `_UNSAFE_KEY_CHARS`
  sanitization, and its atomic tmp+rename write, but **does not reuse the functions
  themselves**, for two grounded reasons: (a) `resolve_cache_dir()` returns the
  *cache* dir (evictable `~/.cache`); a durable bitemporal store must root under a DATA
  dir (`~/.local/share`), so the store needs its own resolver; (b) cross-skill direct
  `import cache_util` is NOT this repo's pattern — grep shows `import cache_util` only
  WITHIN data-markets (same-dir clients: `sec_edgar_client.py:53`, `mops_client.py:50`,
  …); analysis skills reach data-markets by **subprocess** (`analysis-comps/scripts/
  etf_aggregator.py:104` subprocesses `pack.py`), never by importing its modules. The
  TTL envelope (`load_cache`/`compute_ttl`) is also NOT reused — a bitemporal series is
  immutable append-only, no expiry. Layer note: this store is internal persistence of
  validated values, not external I/O — it lives in the `analysis-kpi` skill (analysis
  layer), NOT in data-markets (I/O only), per CLAUDE.md Cross-Plugin Delegation. The
  small self-contained helper duplication (sanitize + atomic-write) is a deliberate,
  flagged Rule-of-Three candidate: extract a shared module only when a THIRD durable
  store appears, not now.
- **Error (status/fail-loud discipline):** the capability spec's "Fail-loud on
  extraction failure" + "Provenance completeness" requirements
  (`docs/loom/2026-07-12-us-sec-primary-source-layer/specs/operational-kpi/spec.md`
  Req "Provenance completeness for every series-point" `:275`, "Fail-loud" `:290`) —
  a point missing provenance is refused, not zero-filled. `cache_util.save_cache`'s
  "loud stderr warning, never silent except:pass" is the tone to match.
- **Data (record shape):** the spec's series-point attrs (proposal.md `:73`):
  `company, kpi_id, period, as_of, value, lineage, provenance{accession, table_id,
  cell_ref}`. The dedup key (spec "Idempotent append" `:308`) adds `source_accession`.
- **Boundary (store substrate decision, already made):** spec "Bitemporal append-only
  store" Scenario "Store substrate is file/JSON, not a database" (`:167`) — append-only
  JSON files keyed by company/kpi_id, one file per series holding a list of point
  records, matching cache_util's file-per-key convention. NOT sqlite. This fork is
  spec-resolved, not re-opened here.

Evidence paths: `investing-toolkit/skills/data-markets/scripts/cache_util.py`,
`docs/loom/2026-07-12-us-sec-primary-source-layer/specs/operational-kpi/spec.md`,
`docs/loom/2026-07-12-us-sec-primary-source-layer/proposal.md`.

## Decision

Build `investing-toolkit/skills/analysis-kpi/scripts/kpi_store.py` as an append-only
bitemporal series store: file-per-series JSON (company+kpi_id), keyed points on
(company, kpi_id, period, as_of), idempotent-dedup on that key + source_accession,
provenance-required-or-reject, accession-derived-`as_of`-or-reject, point-in-time +
latest queries, concurrency-safe append. Resolve a durable DATA dir (XDG_DATA_HOME,
NOT the cache dir) with self-contained helpers that MIRROR cache_util's
sanitization + atomic-write patterns; do NOT `import cache_util` cross-skill and do NOT
reuse its TTL envelope. Ship a thin append/query CLI. House it in a new `analysis-kpi`
skill with a minimal SKILL.md that states the capability is built incrementally and
this slice = the store.

**We will NOT:** use sqlite (spec-resolved: JSON file-per-key); root the store in the
evictable cache dir; `import cache_util` across the skill boundary; build any
LLM/network/schema/gate/break/review machinery (later slices); interpret
break/recast lineage (store the fields, defer the semantics); overwrite or delete any
record; stamp `as_of` from wall-clock; store an unattributed point.

## Alternatives Considered

The one substrate fork — **JSON file-per-series vs sqlite** — is already resolved in
the validated spec (Scenario "Store substrate is file/JSON, not a database"), grounded
in the repo's own no-DB, file-per-key `cache_util` precedent. No external library
choice is introduced (the store uses only stdlib `json`/`pathlib`/`tempfile` + a
stdlib file lock), so no Axis-4 web-search fork applies to this slice. The bitemporal
design itself (transaction-time `as_of` + append-only, point-in-time read) is the
standard bitemporal / SCD-Type-2 pattern (Snodgrass, *Developing Time-Oriented
Database Applications*; Kimball SCD Type 2) — stable, decades-old knowledge, adopted as
specced rather than re-litigated.

## What Becomes Obsolete

Nothing is removed — this slice is purely additive (the first component of a new
capability). It does, however, **establish** the persistence contract that later
slices MUST write through; any later temptation to stash KPI values in an ad-hoc file
becomes a violation of this store's ownership once it ships.

## Out of Scope

- All later operational-KPI slices (extraction, schema, locate/parse, validation,
  cross-check, review queue, break-events, reliability-gate, memo-feed, observability).
- The dual as-reported/recast break-aware series layer (store the lineage fields; defer
  interpreting them).
- The reliability threshold value, per-industry KPI taxonomy, and pilot-ticker +
  ground-truth label set — these are OPERATING decisions the spec defers
  (`[deferred]` threshold + fail-closed default; per-company LLM-proposed schema;
  eval-stage-only pilot), NOT build prerequisites for any code slice including this one.
- Non-US markets (the capability is SEC-only).
- Archiving the change-folder (the capability is multi-slice; archive only when the
  last slice ships).

## Capability-scope evidence (2026-07-14 real-filing probe — carry to the schema slice)

A live probe of 3 real filings (JPM / DAL / AAPL, all fetched from EDGAR 2026-07-14)
measured how much operational-KPI signal survives in SEC-filed docs:
- **Filing-native + standardized families (banks, airlines): ~60-70% recoverable**, in
  clean HTML tables that `pandas.read_html` parses directly (verified: JPM Ex-99.2
  supplement, DAL 8-K Ex-99.1 operating-stats). LLM-locate + deterministic-parse is
  technically sound for these.
- **Strategically-withdrawn metrics collapse to ~0%** (AAPL iPhone units: confirmed
  absent from 10-K + Ex-99.1 + MD&A). Once a company stops disclosing a KPI it exits
  the filing permanently; SEC has no backfill obligation.
- **Company-specific vocabulary is the real friction** (JPM "overhead ratio" ≠ industry
  "efficiency ratio"; DAL "CASM-ex"/refinery-adjusted TRASM are DAL-only) → confirms the
  spec's **per-company schema** design; a universal KPI dictionary would not work.

**Confirmed value/intent (user, 2026-07-14 — LOCKED, carry to every later slice):** the
capability's purpose is **same-company historical trend of whatever operational KPIs
that company discloses in its filings** — used DIRECTLY, accepting that they are
company-specific and NOT cross-company comparable. Cross-company / industry
comparability is explicitly a non-goal. This makes the bitemporal store the exact
foundation: a per-company `(company, kpi_id, period)` time-series, with `as_of`
bitemporality so a later restatement yields BOTH the as-reported and revised values and
a point-in-time query answers "what was known as of date D" — trend integrity without
look-ahead bias.

**Scope (decided direction — (a), bites at the schema slice, not this store slice):** do
NOT pre-impose a KPI-family whitelist. For each company, extract whatever operational
KPIs its filings disclose and build a per-company time-series; deck-only / withdrawn
metrics (e.g. AAPL iPhone units) are handled by the fail-closed gate (withheld, never
fabricated), not treated as failures. The probe's finding stands as an expectation
setter (bank/airline series richest; consumer-tech thinner), not a hard scope filter.
This store slice is agnostic to which KPIs are in scope (it is `company`+`kpi_id`-keyed),
so the scope decision does not gate it.

## Open Questions

1. **File-lock primitive** — `fcntl.flock` (POSIX, the dev/CI host) vs a portable
   lockfile. Default: `fcntl.flock` on the series file, matching the toolkit's
   macOS/Linux-only footprint; confirm at plan time there is no Windows target. (A
   loud "lock unavailable" degradation, not a silent skip, if `fcntl` is absent.)
2. **Series-file envelope version** — mirror cache_util's `_cache_meta.version` idea
   with a distinct `_kpi_store_meta.version` so a future record-shape change is a
   detectable migration, not a silent misread. Default: yes, version the envelope.
   Resolve at the first implementation task.
