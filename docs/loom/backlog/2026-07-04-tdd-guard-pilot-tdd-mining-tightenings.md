---
name: 2026-07-04-tdd-guard-pilot-tdd-mining-tightenings
description: TDD Guard pilot + TDD-mining tightenings
status: open
origin: harness-engineering audit rec 4 (docs/loom/audits/2026-07-04-harness-engineering-audit.md) + the 2026-07-04 three-route TDD-miss mining
start: first real SDD venue — same trigger as G4 / Segment-3 (komado-Viewfinder batch6)
---

- Start: first real SDD venue — same trigger as G4 / Segment-3
  (komado-Viewfinder batch6)
- Origin: harness-engineering audit rec 4
  (docs/loom/audits/2026-07-04-harness-engineering-audit.md) + the
  2026-07-04 three-route TDD-miss mining
- What: mount nizos/tdd-guard (or a loom-built equivalent: hook
  guarantees the check fires, LLM judges) on one real SDD run; measure
  latency / spend / false-block rate → adopt-vs-build decision. Bundle
  the two mining-derived tightenings into the same touch: reviewer
  tests-dimension must flag a zero-new-test feature branch on
  non-carve-out code (miss 3: whole-branch PASS never flagged it), and
  tdd-iron-law carve-outs must be DECLARED before coding, not claimed
  post-hoc (miss 2: "legacy backfill" framing for code shipped untested
  under the workflow's own banner).
