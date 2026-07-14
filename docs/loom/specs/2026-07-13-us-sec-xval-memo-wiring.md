# Brief — wire analysis-xval into the equity-memo pipeline

Status: brainstorming output, awaiting sign-off → `writing-plans`
Arc: US SEC primary-source layer — the deferred memo-wiring follow-on for
capability 2 (financial-table-xval, shipped #562). Narrative memo-wiring already
shipped (#558); this brief covers ONLY xval.

## Design-side on-ramp

Axis 0: brownfield increment to an existing toolkit (wire a shipped Layer-2 skill
into an existing memo pipeline). No new product/UI/spec surface — proceed direct to
loom-code. No change-folder covers memo-wiring (it is the consumption layer, not a
new capability).

## Problem

**Job:** *When I read a US equity memo, I want the financial-statement numbers I'm
about to trust to have already been independently cross-checked against SEC XBRL —
so a mis-tag, restatement, or rounding artifact is surfaced in the memo as a trust
signal, instead of silently flowing into the valuation.*

The `analysis-xval` skill computes exactly this (doc-table vs companyfacts
divergence, low/med/high + structural findings, two/single-source labelled), but it
is a standalone CLI today — nothing in the memo pipeline feeds it data or reads its
findings. The memo trusts whatever the data layer hands it.

## Users

**Job story:** *When the equity-memo pipeline evaluates a US company, I want its
financial-statement cells cross-validated against XBRL and the divergence trust
signals (especially high-alerts) handed to the memo writer and the citation gates,
so the memo can weight or challenge a number rather than take it on faith.*

Consumer: `report-equity-memo` → `domain-teams:investing-team` (the memo writer +
its citation/trust gates). Narrative already has this seam (seed §5); xval does not.

## Smallest End State

Follow the **comps/dcf analysis-step pattern**, NOT narrative's eager-in-pack
pattern — because xval is Layer-2 ANALYSIS, not data (layer discipline: data-markets
does I/O only; analysis-* computes). Three parts:

1. **Data layer (memo-fetch produces the two xval INPUT packs):**
   - **Source-B companyfacts pack builder (the keystone / Open-Q2):** a new
     data-markets function that turns companyfacts into
     `{"cik", "facts": {"<taxonomy>": {"<tag>": [<summarize_concept rows>]}}}` —
     the exact shape `build_source_b_index` requires. `fetch_facts` +
     `summarize_concept` exist but emit the wrong shape; this assembles them.
   - **Source-A doc-table-cells pack:** acquire the latest 10-K filing
     (`_acquire_raw_filing` on the accession already in `sec_filings`), call
     `extract_statement_cells` per primary statement, and **wrap the bare cell list
     into `{"accession", "statement_name", "cells": [...]}`** (defusing the
     documented envelope seam).
   - Both land as memo-fetch pack keys with a **depth-1 `_status` envelope** and a
     **pack_inventory-safe (positive-allowlist) data shape**, so `pack_inventory`
     reports them present/absent correctly across all 5 markets without reopening
     the false-presence hole.
2. **Analysis layer (a new `report-equity-memo` Phase-2.5 step):** run
   `xval_compute.py --source-a <pack> --source-b <pack>` → `xval.json`, mirroring the
   existing `dcf.json` / `comps.json` analysis steps.
3. **Surfacing:** hand `xval.json` into the Phase-4 investing-team delegation packet
   AND add a **seed element 6** ("read the xval high_alerts / doc-only findings
   before you cite a financial number") mirroring narrative's seed §5 and the
   read-before-cite discipline.

**Deferred (late-vetoable):** a dedicated mechanical trust-signal GATE for xval
high-alerts (a CHK-CIT-007-adjacent `rule_verdict`-style check, like analysis-dcf's
rule_verdict). The seed read-instruction is the smallest honest surfacing; a
hard gate is a natural follow-on once the wiring is proven end-to-end.

## Current State Evidence

- **Forward (memo-fetch pack):** `pack_us.py::pack_memo_fetch` (`:700`) assembles the
  US memo pack; return dict at `:741-763` (keys `sec_filings`/`sec_facts`/
  `sec_narrative`/statements). New `xval_source_a`/`xval_source_b` keys slot here.
  `sec_filings` (`:724-728`) already provides the accession to xval.
- **Reverse (SSOT / layer ownership):** CLAUDE.md Cross-Plugin Delegation — "data
  layer stays in toolkit (I/O only); analysis layer computes." → the companyfacts
  pack builder + Source-A extraction wrap live in data-markets; `build_report`
  invocation lives in report-equity-memo's analysis phase. `dcf`/`comps` are the
  precedent (separate analysis JSONs handed in Phase 4).
- **Error (status discipline):** `report-equity-memo/references/phase4-seed-contract.md`
  §5 (`:61-85`) — narrative read-contract; `:79-85` — "failure signal is depth-1
  only; never infer completeness by walking sections." xval's status envelope MUST
  follow the same depth-1 rule.
- **Data (producer shapes):** `sec_edgar_client.py::extract_statement_cells` (`:1645`)
  returns a BARE `list[dict]` (or an error dict; discriminate by `isinstance dict`);
  `fetch_facts` (`:237`) / `summarize_concept` (`:269`) emit companyfacts rows;
  `xval_compute.py::build_report` (`:543`) reads `source_a_pack.get("cells")` +
  `source_b_pack.get("facts")`.
- **Boundary (inventory classifier):** `docs/loom/memory/shared-classifier-over-open-dialects-needs-allowlist.md`
  — `pack_inventory` must decide presence by a POSITIVE data-shape allowlist, not an
  error-key denylist; the new xval keys must present as data-bearing.

Evidence paths: `investing-toolkit/skills/data-markets/scripts/pack_us.py`,
`.../sec_edgar_client.py`, `investing-toolkit/skills/analysis-xval/scripts/xval_compute.py`,
`investing-toolkit/skills/report-equity-memo/SKILL.md` + `references/phase4-seed-contract.md`,
`docs/loom/memory/shared-classifier-over-open-dialects-needs-allowlist.md`.

## Decision

Build the xval memo-wiring as: (1) a data-markets **companyfacts Source-B pack
builder** + a **Source-A cells pack** producer (latest 10-K, envelope-wrapped), both
emitted from `pack_memo_fetch` with a depth-1 status envelope and inventory-safe
shape; (2) a **report-equity-memo Phase-2.5 analysis step** that runs
`xval_compute` on the two packs → `xval.json`; (3) surface `xval.json` to
investing-team + a **seed element 6** read-before-cite instruction. Respect the
layer discipline (data fetch vs analysis compute) and the comps/dcf precedent.

**We will NOT:** run `build_report` inside the data-markets pack layer (layer
violation); xval the 10-Q in this slice (10-K annual is the primary memo anchor —
10-Q is a late-vetoable extension); build the deferred hard trust-signal gate
(seed read-instruction first); fabricate any companyfacts context_ref or value;
reopen the pack_inventory false-presence hole.

## Alternatives Considered

The one real fork — WHERE xval runs in the pipeline — is grounded in the repo's own
two established patterns (no external library choice, so no Axis-4 web search):

1. **Eager-in-pack (narrative pattern)** — run `build_report` inside
   `pack_memo_fetch`, emit an `xval` result block. Rejected: xval is Layer-2
   analysis; running compute in the data-markets pack layer violates the layer
   discipline (narrative is eager-in-pack only because it is pure data extraction).
2. **Separate analysis step (comps/dcf pattern) — CHOSEN.** memo-fetch emits the two
   DATA packs; a report-equity-memo analysis phase runs the COMPUTE. Matches
   `dcf.json`/`comps.json`, respects the layer split.
3. **Lazy / memo-writer-triggered** — the writer invokes xval on demand. Rejected:
   pushes orchestration + I/O into the domain-team writer, against the toolkit's
   orchestrate-then-delegate contract.

## What Becomes Obsolete

- The `xval_compute.py` docstring's "Open Q2 — real companyfacts fetcher not wired"
  caveat (`:89-133`) is retired once the Source-B pack builder ships — update it.
- The SKILL.md envelope-wrap seam note becomes an implemented contract (the wiring
  layer now does the wrap) — keep the note but point it at the new producer.
- Nothing removed from behavior; this is additive wiring.

## Out of Scope

- operational-kpi (capability 3) — still blocked on user-domain decisions.
- xval on 10-Q (this slice: latest 10-K only).
- A dedicated hard trust-signal gate for xval high-alerts (seed read-instruction
  first; gate is a proven-wiring follow-on).
- Non-US markets (companyfacts + edgartools statements are SEC-only).
- Archiving the change-folder (operational-kpi still unshipped).

## Open Questions

1. **Which primary statements to xval** — all four (balance sheet / income / cash
   flow / equity) or a subset for the first slice? Default: the statements
   `extract_statement_cells` reliably returns for a 10-K; confirm at plan time
   against the real filing (a `StatementNotFound` on equity is a loud skip, not a
   failure). Resolve during the first live-probe SDD task.
