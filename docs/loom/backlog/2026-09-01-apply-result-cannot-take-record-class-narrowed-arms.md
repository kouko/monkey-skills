---
name: 2026-09-01-apply-result-cannot-take-record-class-narrowed-arms
description: review_batch.py validates ("spec-reviewer",) as a legal prose-lane arm set (record-class narrowing) but batch_review_cli.py apply-result hardcodes expected_arms from _LANE_ARMS, so an all-record-class prose batch cannot resolve through the CLI with the narrowed single arm — the orchestrator must either collect a docs-reviewer verdict the SKILL declares N/A-by-construction, or abandon the batch to individual fallback and lose the batching saving
status: open
origin: 2026-09-01 — prose-edit self-sweep arc (docs/loom/plans/2026-09-01-prose-edit-self-sweep.md), Review Batch prose-artifacts: all three members record-class; the dispatched docs-reviewer arm correctly refused to mint a verdict into an N/A slot, and _cmd_apply_result's `expected_arms = rb.expected_reviewer_arms(lane)` (both arms for "prose") left no CLI path to apply the spec-only result _arms_apply_to_lane already permits
start: event — the next all-record-class Review Batch reaches packet/apply-result, or when batch_review_cli.py's arm computation is next revised
---

`review_batch.py` `_arms_apply_to_lane` accepts `("spec-reviewer",)` for
the prose lane ("Existing record-class narrowing occupies the
code-quality slot with N/A, leaving only the spec arm"), and
`subagent-driven-development/SKILL.md` promises exactly that narrowing
for an all-record-class Batch. But `_cmd_apply_result` computes
`expected_arms = rb.expected_reviewer_arms(packet.declaration.review_lane)`,
which returns the full `_LANE_ARMS["prose"]` pair unconditionally — no
classification input exists on the CLI path, and
`len(arm_bindings) == len(expected_arms)` then rejects a spec-only
result file. The `packet`/`record-dispatch` side has the same gap: the
dispatch receipt records both arms.

Cost when it fires: the batch's dispatch receipt stays unapplied
(blocking record-dispatch for that batch id in that directory), and the
members re-route through individual review — the batching saving is
lost exactly on the lane (record-class prose) where batching is
cheapest.

Candidate fix: classify member `Files touched` at packet time (cite the
requesting-code-review §Classification SSOT) and record the narrowed
arm set in the declaration/receipt so `apply-result` expects
`("spec-reviewer",)` for an all-record-class Batch.

Second manifestation, same arc: the individual-fallback exit is blocked
by the same coupling — `plan_card.py --set-status "T<N>=done(<sha>)"`
refuses a direct write for a Task declared a batch member ("done may
only be written by batch_review_cli.py apply-result"), so a fallback
that by contract performs "zero Batch ledger mutation" leaves no
sanctioned way to ever mark the members done. The arc resolved it by
amending the plan's dispositions to `individual` (recorded in its DL-2)
before flipping; the fix above should also define the fallback's ledger
path explicitly.
