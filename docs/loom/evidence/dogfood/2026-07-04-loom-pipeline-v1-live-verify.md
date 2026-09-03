# loom-pipeline v0.1.0 — first live-verify (2026-07-04, day after merge)

> Scope agreed with kouko: segments 1+2 against a fresh toy project
> (`unit-converter`, job-tmp scratch); segment 3 (SDD triads via agentType)
> deferred to first real use — its dispatch machinery was already proven
> live by the F5 spike and the 2026-07-03 pipeline dogfood. Driver invoked
> exactly per the entry skill's contract (Workflow({scriptPath, args})).

## Result

| Run | Segment | Outcome |
|---|---|---|
| round 1 (`wf_e96f6d0d-140`) | 1 | **fail-loud in 5ms** — guardArgs rejected string args (finding 1) |
| round 2 (`wf_ff22820b-61d`) | 1 | principles station ran real work, then **recordLedger fail-loud** on a spread string (findings 2–3) |
| round 3 (same, resumed) | 1 | **COMPLETE** — principles ADOPTED (idempotency ✓), design DONE, critic panel 2× PASS_WITH_NOTES, ledger written |
| round 4 (`wf_dc83731c-51e`) | 2 | **COMPLETE first try** — spec DONE, 2 critics PASS_WITH_NOTES, validator hard gate DONE (exit 0), 16 requirements in the change-folder |

Ground artifacts verified on disk after each pass: `PRINCIPLES.md` /
`DESIGN.md` (product-level), `ui-flows.md` / `proposal.md` /
`specs/unit-conversion/spec.md` / `pipeline-ledger.md` (per-change) —
layout matches the audit-#472 convention exactly.

## Findings → fixes (all shipped on this branch, TDD-pinned)

1. **Workflow args arrive as a JSON STRING** through the harness (the tool
   doc's warning, confirmed live). guardArgs now parses a JSON string that
   yields a valid object (deterministic recovery); non-JSON still throws.
2. **mainDispatch ignored guardArgs's return** — the parsed object never
   propagated. Now `args = guardArgs(args)` (test-pinned).
3. **seg1 dispatches passed no `schema`** — agent() without opts.schema
   returns plain TEXT (the harness only injects StructuredOutput when a
   schema is passed); spreading that string into recordLedger produced
   indexed-char garbage. seg2/seg3 had schemas; seg1 lost them across
   remediation rounds. SEG1_STATION_SCHEMA / SEG1_CRITIC_SCHEMA added and
   threaded into all three dispatch sites.
4. **`validate_design_output.py` assumes DESIGN.md and ui-flows.md are
   colocated**, but the sanctioned layout splits them (product-level vs
   per-change). The station honestly validated each half separately and
   reported the mismatch (exit 1) rather than faking. → UPSTREAM item for
   loom-interface-design: the validator needs a dual-root mode. NOT fixed
   here (station plugin's contract, not the driver's).
5. **budget.spent() is turn-scoped** (shared pool), so the run summary
   compared apples to oranges (2.16M "spent" vs a 400k run cap) while the
   ledger said n/a. mainDispatch now captures a baseline at dispatch start
   and reports THIS RUN's delta in both the summary and the ledger
   (`Spent: 82713` vs cap 500000 on the seg2 run — same units at last).

## What the runs proved working (beyond the fixes)

- Fail-loud doctrine paid for itself twice: both integration defects were
  caught at the guard/ledger boundary in milliseconds, with named-input
  errors — zero silent derail (contrast the 2026-07-03 F4 incident).
- Idempotent adopt-if-valid: round 3 ADOPTED the PRINCIPLES.md that round
  2's station had authored — no rewrite, cost-cut recorded as intervention.
- Script-layer critic panel: per-judge verdicts landed in the ledger's G5
  section; two-valued verdicts throughout; no bare PASS anywhere.
- skillsRoot resolution + validator hard gate: seg2's
  `validate_spec_output.py` ran from the passed root and gated on exit 0.
- Ledger quality exceeded expectations: the design station's summary
  honestly reported the validator path mismatch, refused to invent a
  `loading` variant (synchronous math, no network), and hand-computed
  WCAG contrast when the lint CLI was unavailable offline.

## Open items after this pass

- Upstream: loom-interface-design validator dual-root mode (finding 4).
- The interventions bucket-A entry for a routine adopt is mis-filed (an
  adopt note is not an intervention) — prompt calibration, cosmetic.
- Segment 3 live run: deferred to the first real change (by agreement).
- The seg2↔seg3 seam: plan generation (writing-plans) lives in neither
  segment — the freeze definition for v1.1 batch mode must include it.
