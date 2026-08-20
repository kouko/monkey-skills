---
name: 2026-08-18-bare-req-id-coverage-semantics-dogfood
description: blind dogfood of the bare `REQ-<n>` plan-referent semantics (a bare id covers every scenario of the requirement) — measure the over-claim rate of cold plan-writers on an id-mode fixture folder and the plan-document-reviewer's catch rate; results bind whether OQ-3 flips to scenario-only citations
status: open
origin: requirement-identity-hybrid arc kickoff (2026-08-18) — the user chose option A (bare id = requirement-level coverage) and asked for the dogfood AFTER the arc ships rather than as a plan task
start: after loom-code 0.86.0 / loom-design 0.3.0 land on main (this arc's PR) — first quiet slot; needs no other arc
---

- What to measure: 2 cold sonnet plan-writers each get an id-mode fixture
  change-folder (3 requirements × 2–3 scenarios) plus
  `writing-plans/references/plan-format.md`; count (1) tasks citing a
  bare `REQ-<n>` while delivering only a subset of that requirement's
  scenarios (over-claim), (2) how many of those `plan-document-reviewer`
  catches, (3) malformed id-form join keys.
- Decision it binds: OQ-3 in
  `docs/loom/plans/2026-08-18-requirement-identity-hybrid.md` — bare id
  covers all scenarios (option A). High over-claim + low catch → flip to
  scenario-only (cost: one resolver branch in
  `loom-code/scripts/check_scenario_coverage.py`, `_BARE_REQ_ID` path) or
  add a visibility line "REQ-3 cited bare → covers S1, S2, S3" so the
  reviewer sees the expansion.
- Cheap hardening available regardless of the measurement: the
  visibility line above (a stdout note, no semantics change).
