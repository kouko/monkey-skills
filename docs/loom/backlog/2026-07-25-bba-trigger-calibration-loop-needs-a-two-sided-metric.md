---
name: 2026-07-25-bba-trigger-calibration-loop-needs-a-two-sided-metric
description: bba trigger calibration loop — needs a two-sided metric
status: PARKED
origin: bba proactive-trigger-hardening arc (2026-07-25, PR #613 → cf332584). After round-over-round dogfood iteration visibly moved the firing rate, the user asked whether the same method could iterate indefinitely to raise it further; offered, left undecided at close-out, parked here in the follow-up hygiene session.
start: after the ~2026-07-28 deployed-surface telemetry A/B reports an organic BARE-ASK RATE (baseline `docs/harness-audit/2026-07-22-bba-trigger-baseline.md`) — and only if that measurement shows the shipped cards still under-fire. Building before then means tuning against the pre-merge weak-model dogfood, which is directional only (5 rounds, hand-picked scenarios).
---

- Start: after the ~2026-07-28 deployed-surface telemetry A/B reports an
  organic BARE-ASK RATE (baseline
  `docs/harness-audit/2026-07-22-bba-trigger-baseline.md`) — and only if that
  measurement shows the shipped cards still under-fire. Building before then
  means tuning against the pre-merge weak-model dogfood, which is directional
  only (5 rounds, hand-picked scenarios).
- Origin: bba proactive-trigger-hardening arc (2026-07-25, PR #613 → cf332584).
  After round-over-round dogfood iteration visibly moved the firing rate, the
  user asked whether the same method could iterate indefinitely to raise it
  further; offered, left undecided at close-out, parked here in the follow-up
  hygiene session.
- What: a bba-specific replay-matrix + improve-loop pair mirroring
  `principles-replay-matrix` / `principles-improve-loop` (fixed seed corpus →
  haiku headless replay → mechanical grading → ONE fixer edit per round,
  accepted only on a verified win + confirmation re-run + held-out smoke →
  proposal branch, never pushed), applied to the bba trigger wording now
  carried by `loom-code/hooks/router-card.md` rule 5, the four design-side
  `using-*` routers, and the `dev-workflow:brief-before-asking` description.
- **Load-bearing constraint — the metric MUST be two-sided**: brief-when-
  warranted UP *and* brief-on-trivial DOWN, graded on held-out scenarios kept
  out of the tuning corpus. A one-sided "did bba fire?" counter is precisely
  the metric the 07-22 baseline rejected: a loop optimizing it converges on
  over-firing, degrading every trivial ask into a briefing — the failure mode
  the user's own plain-language rule calls out ("not a license to over-brief").
  Without the held-out split the loop overfits its own seeds.
- Cross-ref: this is a narrow instance of the loom-code replay matrix entry
  above. If that general arc ships first, this becomes a seed-corpus + grader
  addition to it, not a second harness.
