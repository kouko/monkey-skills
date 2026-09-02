# Replay matrix results — seed-traceability fix (0.5.1), 2026-07-10

Six haiku headless replays against the round-3 SKILL.md (commit `c908e1c4`):
the meeting-transcriber seed (`seed.md` §Seed) + the 5-seed synthetic corpus
(`../2026-07-10-principles-flow-seed-corpus/`). Grader: fresh sonnet agent,
evidence-strict (every verdict from grep/read of the artifact, never from the
operator's self-report); key FAILs spot-checked by the orchestrator on disk.

## Fix-verification history (same seed, same tier, only SKILL.md varies)

| assertion | 0.5.0 (n=4) | 0.5.1 r2 (n=2) | 0.5.1 r3 matrix (n=6) |
|---|---|---|---|
| deferred stance → Open Question + re-trigger | 0/4 | 2/2 | **6/6** (incl. double-deferred and the DECIDED-cost anti-trap) |
| out-of-jurisdiction bait stays out of principles | n/a | 2/2 | **5/5** |
| negative regressions (C1-C9 class) | 0 | 0 | **0** |
| validator exit 0 | 4/4 | 2/2 | 6/6 |

The 0.5.1 invariant + never-out-of-jurisdiction guard fixed the deferred-drop
class outright and stopped jurisdiction-laundering (mt's multilingual stance
moved from "TECH-SPEC turf" dismissal to Deviation Ledger + Open Question).

## Per-seed scores (r3 matrix)

| seed | anchors | deferred | bait | stances | negative |
|---|---|---|---|---|---|
| mt (meeting-transcriber) | 6/9 | 1/1 | n/a | 17/21 | ✅ |
| s1 war-room dashboard | 6/10 | n/a | ✅ | 11/13 | ✅ |
| s2 bedtime-story app | 6/7 | 2/2 | ✅ | 12/13 | ✅ |
| s3 schema-diff CLI | 5/6 | n/a | ✅ | 13/15 | ✅ |
| s4 vector sketchbook | **9/9** | 1/1 | ✅ | 14/16 | ✅ |
| s5 booking SaaS | 4/8 | 2/2 | ✅ | 8/9 | ✅ |

## Residual systematic failures (input to the harness's next round)

1. **Prose-named tech-stack/canon → Anchors** — 5/6 artifacts drop at least
   one canon or stack item that appears only in prose (Swift/SwiftUI, Rust,
   React/TypeScript/FastAPI/PostgreSQL, Apple Design Language, Swiss Style,
   React Native). s4's clean 9/9 proves the tier CAN do it; compliance is
   probabilistic. Three rounds of prose hardening did not close this class —
   further MUST-sentences are judged exhausted (wrong-direction signal).
2. **False self-report in the seed walk** — s5's own 種子追蹤審計 trailer
   claims "React+TS、FastAPI+PostgreSQL … → Anchors ✓" while its Anchors
   table has 4 rows and the document never names them. The self-check exists
   and usually helps, but its attestation cannot be trusted (known weak-tier
   pattern: fabricated check output).
3. Secondary: single-clause decided stances buried in multi-stance bullets
   still drop occasionally (language choice ×3, notification channel,
   rollback posture) — same probabilistic class as (1).

**Direction decision (2026-07-10)**: stop iterating SKILL.md prose for class
(1)/(2); the remedy is MECHANICAL — seeds already carry machine-readable
`named_anchors` manifests, so the conductor/harness should verify the
produced Anchors table against the manifest post-run and reject/retry on a
miss, treating the operator's self-report as untrusted. Lives with the
BACKLOG "Dogfood replay/eval harness" entry.
