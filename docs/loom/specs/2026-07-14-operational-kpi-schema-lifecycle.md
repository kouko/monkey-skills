# Brief — operational-kpi slice 3: kpi-schema propose→confirm lifecycle + fs extract

Status: brainstorming output, awaiting sign-off → `writing-plans`
Arc: US SEC primary-source layer — capability 3 (`operational-kpi`), **slice 3 of the
multi-slice program**. Stacked on slice 2 (`feat-operational-kpi-review-queue`). Spec:
`docs/loom/2026-07-12-us-sec-primary-source-layer/specs/operational-kpi/spec.md`.
Confirmed intent: same-company historical KPI trend from filings.

## Design-side on-ramp

Axis 0: brownfield increment; validated change-folder covers discovery. Proceed direct.

## Problem

**Job:** *When the pipeline meets a company with no KPI schema, I want an LLM to
PROPOSE that company's own KPI set, a HUMAN to confirm it exactly once, and extraction
to stay strictly inside that confirmed schema — so per-company KPIs are trusted only
after human sign-off, never auto-discovered or guessed.* (Same-company, company-specific
KPIs — the confirmed intent — need a per-company registry, not a universal dictionary.)

Two parts: (a) the **Rule-of-Three fs extract** — this is the THIRD durable store in the
skill (kpi_store, review_queue, now kpi_schema), the point at which the recorded memory
`durable-store-mirrors-cache-util-not-imports-it.md` says to EXTRACT the shared
durable-store primitives into one module instead of a third same-skill import; (b) the
**kpi-schema lifecycle** — propose (LLM-supplied defs, stored), confirm-once (through the
slice-2 review-queue seam), schema-scoped extraction boundary, superseded-blocks.

## Users

**Job story:** *When the pipeline first needs KPIs for a company, I want it to store a
PROPOSED schema (the LLM's candidate defs) and enqueue a confirm review-item — never
extract yet; once a human confirms via the review-queue, the schema is CONFIRMED and only
its kpi_ids are extractable; a superseded schema with no confirmed successor blocks
extraction and re-proposes.*

Consumers (later slices): the extraction/locate step (checks the CONFIRMED schema before
extracting); the reliability-gate (re-evaluates on a schema version bump).

## Smallest End State

**Part A — fs extract (Rule-of-Three):** a new `investing-toolkit/skills/analysis-kpi/
scripts/_store_fs.py` holding the shared durable-store primitives currently in
`kpi_store.py` (`resolve_store_dir`, `_UNSAFE_KEY_CHARS`/sanitize, `_atomic_write`,
`_acquire_series_lock`/`_release_series_lock`). Repoint `kpi_store.py` and
`review_queue.py` to import from it. Pure refactor under existing test coverage — all
slice-1 + slice-2 tests stay green, unchanged.

**Part B — kpi-schema lifecycle** in `scripts/kpi_schema.py`:
1. **propose** — `propose(company, kpi_defs, review_item_id)` stores a PROPOSED schema
   (per-company, `version=1`, `status="PROPOSED"`, `kpi_defs` = list of
   `{kpi_id, label, unit, locate_hint}` supplied by the caller — the LLM produces them
   upstream; this layer stores them) AND enqueues a `subject_type="kpi-schema"`
   review-item via the slice-2 review-queue. No extraction happens on propose.
2. **confirm** — `confirm(company, adjudicated_by)` transitions the company's PROPOSED
   schema to CONFIRMED (records confirmed_by/at), routed through the review-queue's
   human-confirm seam (the pipeline cannot self-confirm — reuse slice-2's authorization
   boundary). Confirm-once: a second confirm on an already-CONFIRMED schema is rejected.
3. **schema-scoped boundary** — `is_kpi_in_confirmed_schema(company, kpi_id)` (or
   `confirmed_kpi_ids(company)`) → only kpi_ids in the CONFIRMED schema are valid; an
   unlisted metric is not extractable (the boundary the extraction slice will consult).
4. **status gating** — a PROPOSED (unconfirmed) schema blocks extraction (query returns
   "not confirmed"); a SUPERSEDED schema with no CONFIRMED successor blocks + signals
   re-propose.
5. **amend / supersede** — `amend(company, new_kpi_defs, review_item_id)` proposes a new
   version (status PROPOSED, supersedes the prior on confirm) through the same
   propose→confirm path — never a code-level per-company hardcode.
6. A thin **CLI** — `propose` / `confirm` / `status` subcommands, in the skill `## CLI`.

**Explicitly NOT in this slice:** the LLM that GENERATES kpi_defs (defs are passed in);
any locate/parse/extraction; rule validation; reliability gate; break-events; memo feed.
This slice is the schema registry lifecycle + the fs extract ONLY.

## Current State Evidence

- **Forward (consumers):** none yet — schema registry ships ahead of the extraction slice
  that will consult `confirmed_kpi_ids`. CLI is the exercisable surface.
- **Reverse (SSOT / reuse):** `kpi_store.py` currently owns the fs primitives; slice 2's
  `review_queue.py` imports them same-skill. This slice EXTRACTS them to `_store_fs.py`
  (the recorded Rule-of-Three trigger — 3rd store) and repoints all three modules. The
  review-queue seam (`review_queue.enqueue` / `adjudicate`) is reused for schema confirm.
- **Error (fail-loud):** slice-1/2 pattern — reject loud on illegal transition (confirm
  an already-CONFIRMED / absent schema; self-confirm via the review-queue auth boundary).
- **Data (shapes):** spec `kpi-schema` attrs (proposal.md): `schema_id, company, version,
  status, confirmed_by/at` + `kpi_defs`. States: `proposed →(human confirm)→ confirmed
  →(active)→ {active | superseded →(drift)→ new proposed}`.
- **Boundary:** spec Requirements "KPI schema propose-then-confirm lifecycle" (:28),
  "Schema-scoped extraction boundary" (:49), "Superseded schema without a confirmed
  successor blocks" (:342). Reuse `docs/loom/memory/durable-store-mirrors-cache-util-not-imports-it.md`
  (the extract-at-3rd rule this slice executes).

Evidence paths: `investing-toolkit/skills/analysis-kpi/scripts/kpi_store.py`,
`.../review_queue.py`, `docs/loom/2026-07-12-us-sec-primary-source-layer/specs/operational-kpi/spec.md`,
`docs/loom/memory/durable-store-mirrors-cache-util-not-imports-it.md`.

## Decision

(A) Extract the shared durable-store fs primitives into `_store_fs.py`; repoint
kpi_store + review_queue (refactor under coverage). (B) Build `kpi_schema.py`: per-company
propose (stores LLM-supplied defs + enqueues a confirm review-item) → human confirm-once
(through the review-queue auth seam) → CONFIRMED unlocks a schema-scoped kpi_id boundary;
PROPOSED/SUPERSEDED block; amend re-proposes a new version. Ship a CLI.

**We will NOT:** generate kpi_defs with an LLM here (passed in); build locate/parse/
extraction/validation/gate/break-events (later slices); let the pipeline self-confirm a
schema (reuse the slice-2 boundary); hardcode any per-company KPI; extract more than the
shared fs primitives in Part A.

## Alternatives Considered

The fork — **extract fs primitives now vs a third same-skill import** — is resolved by the
recorded memory: 3rd durable store = extract. Deferring would leave three modules importing
kpi_store's private helpers (a smell the Rule-of-Three exists to end). No external library
fork. The schema substrate follows slice-1/2's file-per-key JSON precedent.

## What Becomes Obsolete

- kpi_store's + review_queue's inline/own copies of the shared fs primitives become the
  extracted `_store_fs.py` — repoint (do not leave duplicates). The slice-2 same-skill
  import of kpi_store's private helpers is replaced by importing `_store_fs`.

## Out of Scope

- LLM kpi_defs generation; locate/parse/extraction; rule validation; reliability gate;
  break-events; memo feed; non-US markets; archiving the change-folder.

## Open Questions

1. **Where confirm is driven** — does `kpi_schema.confirm` call `review_queue.adjudicate`
   internally, or does the operator adjudicate the review-item (via the review CLI) and
   `kpi_schema` react? Default: `confirm` adjudicates the schema's review-item through the
   review-queue seam (single call, still enforcing the human-identity boundary), so the
   schema transition and the audit record stay consistent. Resolve at plan time.
2. **One schema file per company** (mirrors kpi_store's file-per-series) vs a single
   registry file. Default: file-per-company (consistent, lock-per-company). Confirm in plan.
