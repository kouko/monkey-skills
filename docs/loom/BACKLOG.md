# loom family backlog

> SSOT for cross-plugin open items. Convention: one entry per item with
> **start/re-trigger condition**, **origin** (PR / ledger / discussion),
> and **status** (`COMMITTED-NEXT` | `OPEN` | `PARKED` | `UPSTREAM`).
> Plugin-local parks stay in each plugin's README (§parked items with
> re-triggers); this file holds items that cross plugin boundaries or
> have no plugin home yet. Claude-side session memory keeps only a
> pointer here — this file is the durable truth (versioned, host-agnostic,
> greppable). Completed items are deleted, not archived — git history is
> the archive.

## G4 — Sonnet-vs-Fable gate quality A/B
- Status: OPEN
- Start: after the first REAL change runs through the pipeline
- Origin: PR #476 open question; protocol documented in
  loom-pipeline/README.md §G4
- What: same branch reviewed by both model tiers; compare verdict tokens
  + finding severity distributions against a human review. Also settles
  whether the two-valued verdict scheme inflates (untested house
  hypothesis, flagged in the industry research doc).

## validate_design_output.py dual-root mode
- Status: UPSTREAM (loom-interface-design)
- Start: next loom-interface-design touch
- Origin: live-verify finding 4 (report
  docs/loom/dogfood/2026-07-04-loom-pipeline-v1-live-verify.md); the
  validator assumes DESIGN.md + ui-flows.md are colocated, but the
  sanctioned layout (audit #472) splits product-level vs per-change —
  exit 1 is structurally guaranteed. Needs --design-root/--flows-root
  (or equivalent) arguments.

## Segment-3 first live run
- Status: OPEN
- Start: first real change (deliberately NOT burned on a toy — agreed
  2026-07-04; dispatch machinery already proven by the F5 spike and the
  2026-07-03 dogfood)
- What: SDD triads via agentType + whole-branch review + conditional
  ui-verification, driven by the merged driver against a real repo.

## loom-spec station briefing gate (#475 parity)
- Status: OPEN (original 值得做 list item 3, half-covered)
- Origin: 2026-07-03 dogfood — spec station resolved a product decision
  (ending-controls) inline. The pipeline's human gate (b) now covers
  DRIVER runs; loom-spec itself still lacks the brief-before-asking
  escalation for INTERACTIVE use.

## duration-override test affordance → interaction-flows enumeration
- Status: OPEN (original 值得做 list item 4)
- Origin: ui-verification first live run (PR #477 dogfood note) — 4
  states untestable behind a 25-minute wait; pipeline-produced apps
  should be required at design time to expose a test affordance.
  Candidate enumeration item for loom-interface-design:interaction-flows.

## Interventions bucket calibration (cosmetic)
- Status: OPEN (small)
- Origin: live-verify seg1 ledger — a routine adopt-if-valid note was
  filed as a bucket-A intervention; an adopt is a cost-cut record, not
  an intervention. Station preamble wording tweak in driver_30_seg1.js.
