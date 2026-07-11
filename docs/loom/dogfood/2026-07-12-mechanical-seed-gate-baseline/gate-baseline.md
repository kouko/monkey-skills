# Mechanical seed-gate acceptance baseline — 2026-07-12

Two live L1 matrix runs (gate-r1 `wf_1cf2301b-1c2`, gate-r2 `wf_7875db0d-637`;
haiku replays; 28 agents each, 0 errors) at branch HEAD `fbb9784d`, against
the pre-gate committed baseline
`docs/loom/dogfood/2026-07-10-principles-flow-seed-corpus/calibration-baseline-2026-07-11.md`
(4/18 PASS; prose-named stack/canon anchor drops in 14/18 artifacts).
Replay artifacts are ephemeral (session sandbox); this table + `runs.json`
are the durable record.

## Verdict: IMPROVED — pass rate 22% → 67%, dominant failure class displaced

| run/seed | oracle verdict | self-check caught → fixed | residual oracle misses |
|---|---|---|---|
| r1/seed1 | FAIL | 2 → 2 (exit 0 after fix) | TypeScript; React; PostgreSQL; Redis (all absent from inventory) |
| r1/seed2 | FAIL | 6 → 6 | 升級胃口 deferred (absent from inventory) |
| r1/seed3 | **PASS** | 4 → 4 | — |
| r1/seed4 | FAIL | 0 (self-check exit 0) | 升級胃口 deferred (pure inventory blindness) |
| r1/seed5 | **PASS** | 7 → 7 | — |
| r1/cold-operator | **PASS** | 4 → 4 | — |
| r2/seed1 | **PASS** | 2 → 2 | — |
| r2/seed2 | FAIL | 3 → 3 | on-device TTS anchor; 可逆性 deferred (both absent from inventory) |
| r2/seed3 | **PASS** | 6 → 6 | — |
| r2/seed4 | **PASS** | 4 → 4 | — |
| r2/seed5 | **PASS** | 5 → 5 | — |
| r2/cold-operator | **PASS** | 0 (clean first draft) | — |

Pass rate: **8/12 (67%)** vs baseline **4/18 (22%)**. Per-run: r1 3/6,
r2 5/6 (replay nondeterminism persists — same caveat as the calibration
baseline).

## Signal reading

1. **The gate mechanism works end-to-end**: the self-check caught misses
   in 10/12 artifacts (43 total) and the single bounded fix round cleared
   **100% of caught misses** (`selfCheckExitAfterFix: 0` on every fixed
   row; `selfCheckFixed` totals r1=23, r2=20). Zero courier errors, zero
   phantom-fix telemetry.
2. **The dominant failure class is displaced, not merely reduced**: the
   old class (entity present in draft context, dropped from `## Anchors`
   during drafting — 14/18 baseline artifacts) is now caught mechanically
   whenever the inventory names the entity. Every one of the 4 residual
   failures is an **inventory omission** — the drafting agent's own
   inventory never listed the entity, so the mechanical check was blind
   to it (r1/seed4 is the pure case: self-check exit 0, oracle exit 1).
3. **Recurrent inventory blind spot**: the 升級胃口 (upgrade appetite)
   deferred item accounts for 2 of 4 residual failures — the same item
   that recurred in the calibration baseline. Extraction-at-reading
   misses skew toward deferred/stance-like items over concrete tech
   nouns (3 of 6 residual miss LINES are deferred_items).
4. **No regression**: validator exits 0 across all 12; no `negative:`
   violations; cold-operator (human-grounded, held-out in L3 contexts)
   passed both runs.

## Residual + re-trigger (recorded, not actioned in this arc)

- New improvement frontier = **inventory quality** (the extraction step),
  no longer drafting discipline. Candidate remedies when re-triggered:
  a dedicated extraction pass with its own checklist emphasis on
  deferred/undecidable items, or a second independent extraction agent
  diffed against the first. Re-trigger: inventory-omission failures
  persist across future runs at a rate that caps the pass-rate.
- Fix bound stayed at 1 round and cleared everything it saw — the
  recorded reversal condition (raise to 3) was NOT met.
