# Calibration baseline — 2026-07-11 (branch feat-replay-oracle-calibration)

Final mechanical re-grade of all 18 replay artifacts (3 matrix runs × 6 seeds,
haiku headless, runLabels calib-r1/r2/r3) against the calibrated oracles at
this branch's HEAD. Grading = `validate_principles_output.py` (all 18 exit 0)
+ `check_seed_traceability.py`. Every listed miss was verified on disk
(token absent from the artifact's `## Anchors` rows / `## Open Questions`
re-trigger lines — grep, not assumption): **all misses are class-D genuine
drops; zero token-form / alias / rejection-mention misses survive.**

The replay artifacts themselves lived in a session scratchpad (ephemeral);
this table is the durable record. Re-derive a fresh baseline any time with
the `principles-replay-matrix` workflow — replays are non-deterministic, so
D-composition shifts between runs; the stable facts are the drop CLASSES.

| run/seed | misses (all class-D) |
|---|---|
| r1/seed1 | Layered\|N-Tier; Hexagonal\|Ports & Adapters |
| r1/seed2 | React Native; on-device TTS; 升級胃口(deferred) |
| r1/seed3 | Rust |
| r1/seed4 | Kenya Hara |
| r1/seed5 | React; TypeScript; FastAPI; PostgreSQL |
| r1/cold-operator | **PASS** |
| r2/seed1 | **PASS** |
| r2/seed2 | Calm Technology; React Native; on-device TTS; 升級胃口(deferred) |
| r2/seed3 | Rust |
| r2/seed4 | C++; Qt; SVG; 升級胃口(deferred) |
| r2/seed5 | **PASS** |
| r2/cold-operator | **PASS** |
| r3/seed1 | TypeScript; React; PostgreSQL; Redis |
| r3/seed2 | React Native; on-device TTS |
| r3/seed3 | Rust |
| r3/seed4 | C++; SVG; 升級胃口(deferred) |
| r3/seed5 | WCAG; React; TypeScript; FastAPI; PostgreSQL |
| r3/cold-operator | SwiftUI; Core ML |

Pass rate: 4/18. Signal reading:

- **Prose-named stack/canon → `## Anchors` drop is THE dominant failure
  class** (14/18 artifacts; every seed affected in ≥1 run) — mechanically
  confirms the #532 residual at scale. This is the improvement loop's
  primary target.
- **Deferred-stance drop recurs but narrowly**: 升級胃口 (upgrade appetite)
  dropped in 3 runs (seed2 ×2, seed4 ×1... seed4 all 3 runs — see table);
  no other deferred item ever dropped after calibration.
- Design canons occasionally drop too (Kenya Hara r1, Calm Technology r2)
  — not only tech stacks.

Known measurement limitations (accepted, documented):

- Short anchor tokens can false-NEGATIVE by matching an unrelated row's
  version cell (observed: r3/seed4 `Qt` matched the HIG row's "via Qt
  styling") — candidate checker improvement: restrict the anchor match to
  the first (canon-name) cell. Under-reports drops, never false-alarms.
- Machine `negative:` tokens follow the corpus README's
  demote-on-reproduction policy (negation-superstring limitation).
- Grade-courier robustness: in 2 of 3 workflow runs one seed's grade agent
  failed schema-forced output and the pipeline dropped that row (null)
  instead of a degraded failed row; grading was recovered manually on disk.
  Candidate workflow fix: catch stage errors into failed rows.
