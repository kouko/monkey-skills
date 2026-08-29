---
name: 2026-08-28-live-gate-post-fix-packet-source-undefined
description: the convergence loop's live-gate carve-out tells the orchestrator to mint from a "runner-supplied post-fix packet" that the live-gate runner never produces — live_host_review_gate.py resolves exactly one canonical packet bound to the initial reviewed_sha, and live_gate_adapter_probe.py types an unchanged post-fix SHA as a refusal, so a live-gate station reaching convergence has no defined packet source
status: closed
origin: 2026-08-28 review-loop-convergence arc — the whole-branch docs arm's confirmation round flagged the fix's own live-gate reconciliation sentence (review-loop-convergence.md §4) as invoking a packet the runner does not supply; recorded as non-gating debt per the arc's own durable-debt rule instead of opening a further review cycle
start: the next arc that touches the live-gate runner or its packet contract, or the first live-gate station run that actually reaches a convergence mint
---

Closed: amnesty-2026-08-30 (bulk cleanup, not per-entry adjudicated)

Options sketched at filing time (not decided): (a) extend the live-gate
runner to resolve and hand over a second canonical packet at the post-fix
SHA once a fix round lands; (b) declare the convergence mint unreachable
in a live-gate station and route those runs to the non-live-gate mint
path explicitly. Three terminology nits from the same confirmation round
ride along for the same future touch: "one-shot" used for a named
dispatch in SKILL.md Step 2 (A1 defines naming as the opposite); §6's
valve round not stating whether its two arms follow §1's naming rule;
§7's "transplants Directive 4 unchanged" overstating (it adds a
disclosure duty Directive 4 does not carry).
