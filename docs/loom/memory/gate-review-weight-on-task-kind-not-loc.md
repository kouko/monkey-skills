---
name: gate-review-weight-on-task-kind-not-loc
description: When deciding how much review a change deserves, gate on task KIND (mechanical/prose/version-bump vs logic/heuristic/hook/security-surface), never on diff LOC size — LOC is a weak, sometimes wrong proxy
type: practice
origin: PR #514 (loom-code Review-weight: mechanical), 2026-07-08
---

An external opinion proposed tiering SDD/whole-branch review by diff
LOC size (e.g. "<50 lines → 1 reviewer, skip full retest"). A
`dev-workflow:proposal-critique` pass (WebSearch-verified) rejected the
LOC axis using this repo's own same-session evidence:

- A 20-30-line Stop-hook language-threshold fix needed the full
  two-reviewer panel to catch a real false-positive bug — a "<50
  lines → light review" rule would have shipped it.
- Several 1-line pointer/prose edits got a full implementer +
  spec-reviewer + code-quality-reviewer triad anyway — trivially
  mechanical, but LOC alone gave no signal to skip.

**Why:** diff size has no stable correlation with review-need. A short
logic/heuristic/hook/security-surface change is exactly as risky as a
long one; a long but purely mechanical batch edit is exactly as safe
as a short one. The axis that actually predicts risk is task **kind**,
not line count.

**How to apply:** when any proposal offers to "tier review by size,"
ask first whether the axis is LOC or kind. Push back on LOC-gating;
kind-gating (mechanical/prose/version-bump → light or skip; logic/
heuristic/hook/security-surface → full weight regardless of size) is
the shape that survives evidence. Shipped implementation: loom-code's
`Review-weight: mechanical` opt-in per-task field (PR #514) —
kind-gated via `plan-document-reviewer` Check 16, never LOC-gated.
