# Brief — operational-kpi slice 2: review-item queue + human-confirm seam

Status: brainstorming output, awaiting sign-off → `writing-plans`
Arc: US SEC primary-source layer — capability 3 (`operational-kpi`), **slice 2 of the
multi-slice program**. Validated spec:
`docs/loom/2026-07-12-us-sec-primary-source-layer/specs/operational-kpi/spec.md`.
Slice 1 (append-only bitemporal KPI store) shipped on branch
`feat-operational-kpi-bitemporal-store`; this slice is stacked on it (same
`analysis-kpi` skill). Confirmed capability intent (locked 2026-07-14): same-company
historical KPI trend from filings, used directly.

## Design-side on-ramp

Axis 0: brownfield increment; validated change-folder already covers the discovery.
No new product/UI surface. Proceed direct to loom-code.

## Problem

**Job:** *When the pipeline is not confident enough to auto-trust a value — a
first-time company's proposed KPI schema, a low-confidence extraction, or a
definition-drift break — I want it routed to a durable review queue for a HUMAN to
adjudicate, and I want the pipeline itself to be structurally unable to self-approve,
so the anti-fabrication seam is enforced, not just convention.*

The whole operational-KPI pipeline is fail-closed: anything uncertain must WAIT for a
human confirm rather than guess. That waiting needs a queue primitive — enqueue a
review-item, list what's open, adjudicate it with an immutable record of WHO decided
and WHEN, and a boundary that the automated pipeline cannot cross to confirm its own
work. This slice builds that authorization primitive; schema propose→confirm (slice 3)
and low-confidence extraction (later) both plug into it.

## Users

**Job story:** *When any pipeline stage produces something that must not be trusted
without a human — a proposed schema, a below-threshold KPI, a flagged break — I want it
enqueued as a typed review-item referencing its subject; and when a human operator
adjudicates it via the CLI, I want who/when stamped immutably (a later re-adjudication
appends, never overwrites), and any attempt by the automated caller to adjudicate its
own item rejected.*

Consumers (later slices): schema-confirm (slice 3), low-confidence-extraction enqueue,
break-event adjudication. Operator surface: a CLI acting on the queue file.

## Smallest End State

A new module `investing-toolkit/skills/analysis-kpi/scripts/review_queue.py` (same
skill as slice 1's `kpi_store.py`) providing:

1. **Enqueue** — `enqueue(item)` appends a review-item to a durable queue file. An item
   carries `review_item_id`, `subject_type` (`kpi-schema` | `kpi-instance` |
   `break-event`), `subject_id`, `reason`, `status="OPEN"`, and a `created_at`. The
   queue file is the single source of pending work (a deterministic per-`subject_type`
   or single-file partition), append-only.
2. **List open** — `list_open()` returns the OPEN items (the operator's work list).
3. **Adjudicate** — `adjudicate(review_item_id, decision, adjudicated_by, resolution)`
   moves an OPEN item to a resolved state (`APPROVED` | `REJECTED` | `EDITED`) and
   records an adjudication record. Legal transitions only (OPEN → resolved; a resolved
   item may be REOPENed → OPEN).
4. **Immutable adjudicator identity** — every adjudication appends `adjudicated_by` +
   `adjudicated_at` as an APPEND-ONLY record; a later re-adjudication adds a NEW record,
   never overwrites the first (audit trail).
5. **Confirm-seam authorization boundary (enforced, not convention)** — `adjudicate`
   REQUIRES a non-empty human `adjudicated_by`; a call flagged as the automated pipeline
   (e.g. `adjudicated_by` empty/None, or an explicit `actor_is_pipeline=True`) is
   REJECTED loud. The pipeline cannot self-confirm. The boundary is stated in the
   docstring AND enforced at the call.
6. **A thin `review_queue.py` CLI** — `enqueue` / `list` / `adjudicate` subcommands,
   declared in the skill's `## CLI`.

**Reuse (not re-duplicate, not yet extract):** the durable-DATA-dir resolution,
key-sanitization, atomic tmp+rename write, and per-file `fcntl` lock built in slice 1's
`kpi_store.py` are reused by same-skill import (`review_queue.py` imports them from
`kpi_store`). This is the SECOND durable store in the skill; per the recorded memory
`docs/loom/memory/durable-store-mirrors-cache-util-not-imports-it.md`, the shared-module
EXTRACT happens at the THIRD durable store, not now — so import from `kpi_store`, do not
copy and do not prematurely extract a `_store_fs.py`.

**Explicitly NOT in this slice:** the kpi-schema propose→confirm lifecycle itself (slice
3 — it will CREATE schema-proposal review-items and act on adjudication results); any
LLM/locate/parse; the reliability gate; break-event detection; the memo feed. This
slice is the queue + adjudication seam ONLY. `subject_type` values are accepted as
opaque strings this slice — the schema/break objects they reference are later slices.

## Current State Evidence

- **Forward (who will call it):** no consumer yet — the queue ships ahead of its callers
  (slice 3 schema-confirm is the first). CLI is the exercisable surface.
- **Reverse (SSOT / reuse ownership):** `investing-toolkit/skills/analysis-kpi/scripts/
  kpi_store.py` owns the durable-store fs primitives (`resolve_store_dir`, the
  `_UNSAFE_KEY_CHARS` sanitize, `_atomic_write`, the `_acquire_series_lock`/
  `_release_series_lock` pair). `review_queue.py` reuses them by same-skill import — NOT
  a cross-skill import (both live in `analysis-kpi/scripts/`, so the layer boundary the
  memory guards is not crossed). The Rule-of-Three extract is deferred to a third store.
- **Error (fail-loud discipline):** slice-1 pattern — reject loud + write nothing on a
  precondition violation (here: adjudicate with no human identity). Mirror it.
- **Data (record shapes):** spec `review-item` attrs (proposal.md object model):
  `review_item_id, subject_type, subject_id, reason, status, resolution`; adjudication
  adds `adjudicated_by, adjudicated_at`. States (proposal.md): `open →(pick up)→
  in_review →(resolve)→ {approved|rejected|edited} →(reopen)→ open`.
- **Boundary (authorization):** spec Requirement "Confirm-seam authorization boundary is
  stated" (`operational-kpi/spec.md` :392) + "Adjudication carries immutable identity"
  (:384) + "Review-item queue lifecycle and human-confirm seam" (:136).

Evidence paths: `investing-toolkit/skills/analysis-kpi/scripts/kpi_store.py`,
`docs/loom/2026-07-12-us-sec-primary-source-layer/specs/operational-kpi/spec.md`,
`docs/loom/2026-07-12-us-sec-primary-source-layer/proposal.md`,
`docs/loom/memory/durable-store-mirrors-cache-util-not-imports-it.md`.

## Decision

Build `analysis-kpi/scripts/review_queue.py`: a durable append-only review-item queue
with enqueue / list-open / adjudicate, legal state transitions, immutable append-only
adjudicator identity, and an ENFORCED confirm-seam authorization boundary (no pipeline
self-confirm); reuse slice-1's fs primitives by same-skill import; ship a thin CLI.

**We will NOT:** build the kpi-schema lifecycle (slice 3); interpret `subject_type`
beyond an opaque string; extract a shared `_store_fs.py` yet (Rule-of-Three: 3rd store);
overwrite any adjudication record; let the pipeline self-confirm; cross the skill
boundary (reuse is same-skill import of kpi_store).

## Alternatives Considered

The one design fork — **enforce the no-self-confirm boundary IN this data layer vs
delegate it to a named ops/CLI wrapper** — the spec ("Confirm-seam authorization
boundary is stated") permits either, requiring only that the boundary be *stated*. We
enforce it HERE (reject an adjudicate lacking a human identity) because a purely
convention-level boundary is the exact anti-fabrication seam the capability exists to
harden — an enforced check is strictly stronger and cheap. No external library fork, so
no Axis-4 web search. Queue-file-JSON substrate follows slice 1's file-per-key precedent
(spec-resolved: no DB).

## What Becomes Obsolete

Nothing removed — additive. This slice ESTABLISHES the authorization primitive that
slice 3's schema-confirm MUST route through (a later temptation to self-confirm a schema
in code becomes a violation of this seam once it ships).

## Out of Scope

- kpi-schema propose→confirm lifecycle (slice 3); LLM/locate/parse; reliability gate;
  break-events; memo feed.
- Extracting shared fs primitives into `_store_fs.py` (deferred to the 3rd durable store).
- Non-US markets; archiving the change-folder (capability still multi-slice).

## Open Questions

1. **Queue-file partition** — one queue file vs per-`subject_type` partition. Default:
   one append-only queue file per store root (simplest single-source-of-pending-work);
   revisit if contention or scale demands partitioning. Resolve at plan time.
2. **created_at provenance** — series-points require accession-derived `as_of`; a
   review-item's `created_at` is a runtime event, not a filing fact, so it is NOT held
   to the accession-derived rule (it is a caller-supplied timestamp). Confirm this
   distinction in the plan (don't wrongly import slice-1's as_of guard here).
