---
name: a-refusal-contract-must-name-an-observable-state
description: a contract telling an agent to refuse by silence is unenforceable and unobservable — a refusal must be a named output state the orchestrator can distinguish from a dead agent, backed by mechanical validation at both the dispatch and intake boundaries
type: practice
origin: PR (reviewer packet fail-closed arc, 2026-08-25); live tests n=2 same-day
---

The reviewer discipline's original malformed-packet rule said "return no
verdict until the orchestrator supplies the complete packet". Two live
dispatches with a deliberately incomplete packet showed the reviewers do
not hold that line: one derived its own SHA via `git log`, read the
mutable worktree, and emitted a full verdict whose content was wrong
relative to the true snapshot. And even a reviewer that HAD obeyed would
have produced silence — indistinguishable from a dead dispatch arm.

**Why:** silence has no consumer. An orchestrator cannot branch on
"nothing came back for the right reason" vs "the agent died", so the
prose rule fails twice: the model side does not reliably obey it, and
the receiving side could not use it even if obeyed. The fix that held
was structural: a named refusal state (`verdict: MALFORMED_PACKET` +
`missing_fields:`), a pre-dispatch mechanical packet gate
(`review_context.py --validate`), and an intake gate that can never
mint the refusal (`loom_gate_markers.py`). Adversarial review of the
new validator immediately found bypasses (relative `target_repo`,
unconfined `resources`) — a fail-closed gate needs its own adversarial
probes before it counts as closed.

**How to apply:** when writing any contract clause of the form "on
condition X, do not produce output", replace it with "on condition X,
produce exactly this named refusal shape", give the refusal a consumer
rule at every receiving station (including confirmation seams and
resolution tables), and validate the condition mechanically on both
sides of the boundary rather than trusting either side's prose.
