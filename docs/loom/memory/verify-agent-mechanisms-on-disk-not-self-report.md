---
name: verify-agent-mechanisms-on-disk-not-self-report
description: Behavioral verification of agent-facing mechanisms on cheap model tiers — real-session drive with unique markers, disk-verified effects, transcript grep for output fingerprints, per-verb cold-reader agents, two consecutive clean rounds; never accept the model's self-report as the oracle
type: process
origin: PR #500 branch, 2026-07-06 — three dogfood series on one branch
---

When behaviorally verifying agent-facing mechanisms (hooks, skills,
charters) on cheap model tiers, never accept the model's self-report
as the oracle. The reliable recipe, proven across three dogfood
series on one branch:

1. **Drive the behavior in a REAL session** (headless `-p` / `exec`)
   with a unique per-round marker string.
2. **Verify effects on DISK** — files, counts, byte-equality.
3. **For delivery questions, grep the SESSION TRANSCRIPT / rollout
   log** for the mechanism's output fingerprint — the transcript
   shows what actually fired even when the model's summary omits it.
4. **Per-verb cold-reader agents** whose ONLY context is the artifact
   under test.
5. **Require 2 consecutive all-clean rounds**; any failure resets the
   counter.

**Why:** this caught a charter under-specification, a fabricated
mechanism claim, a weak-model information drop, and an upstream Codex
handler bug — all invisible in model self-reports.

**How to apply:** follow the five steps above whenever certifying
that a hook / skill / charter behaves correctly under a weak model
tier. The self-report is data about what the model believes, never
evidence of what happened; disk state and the transcript are the
evidence. Do not declare a round clean until every verb's disk and
transcript checks pass, and do not stop before two consecutive clean
rounds.
