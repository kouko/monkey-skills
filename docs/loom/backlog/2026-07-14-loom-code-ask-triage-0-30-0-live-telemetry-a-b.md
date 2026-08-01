---
name: 2026-07-14-loom-code-ask-triage-0-30-0-live-telemetry-a-b
description: loom-code ask-triage 0.30.0 — live telemetry A/B
status: OPEN
origin: PR #564 (loom-code 0.30.0 layered ask-autonomy defense); HANDOFF-2026-07-14 P2.
start: ~2-4 weeks after 2026-07-14 (needs organic session volume on the shipped ask-triage hook + kickoff L1-lite harvest; same pattern as the ascii-graph re-run below — run both in one telemetry pass if timing aligns).
---

- Start: ~2-4 weeks after 2026-07-14 (needs organic session volume on the
  shipped ask-triage hook + kickoff L1-lite harvest; same pattern as the
  ascii-graph re-run below — run both in one telemetry pass if timing
  aligns).
- Origin: PR #564 (loom-code 0.30.0 layered ask-autonomy defense);
  HANDOFF-2026-07-14 P2.
- Baseline: `docs/harness-audit/2026-07-22-bba-trigger-baseline.md`
  (07-01~07-22 pre-A/B measurement: 125 Ask events / ~15% bba coverage /
  sampled miss-rate ~25% of non-bba asks / ask-triage hook intercepts
  ≈19). Read it before running the A/B; reuse its grep patterns for
  comparability.
- What: session-log telemetry over `~/.claude/projects/**/*.jsonl` —
  mid-task ask turns that cite research/recommendation vs bare "X or Y?"
  asks, against the pre-0.30.0 baseline. Also the deferred hook-card
  escape-hatch sentence (PR #564 next-touch).
- Metric guards (from the baseline doc): (1) the primary metric is
  **bare-ask rate**, never bba invocation count — sampled gray-zone cases
  show inline briefings (question text carries stakes + mental model
  without invoking the skill), so invocation counts systematically
  undercount briefing behavior; count those as the cites-context leg.
  (2) Split legs at 07-08 (hook ship): the baseline doc's mixed-window
  numbers are overall baseline only, not the pre-hook leg. (3) The
  candidate B-leg hardening (triage-card line: bare non-trivial ask →
  lead with one stakes sentence) must be designed as a post-merge step —
  marketplace pulls GitHub main, so a feature-branch hook card is
  untestable pre-merge.
