---
name: 2026-08-10-family-integration-evaluation-seed
description: adjudicated direction for loom family integration — behavioral pull, not packaging; seed for the evaluation arc that decides how the loom-* plugins grow together
status: open
origin: 2026-08-10 cheap-hardening-batch arc — adjudicated in conversation; filed so the direction is citable instead of re-litigated
start: user authorizes the family-integration evaluation arc
---

- Start: user authorizes the family-integration evaluation arc

- Origin: 2026-08-10 cheap-hardening-batch arc — adjudicated in conversation; filed so the direction is citable instead of re-litigated

- The adjudicated direction: family integration means **behavioral
  pull, not packaging**. The integration surface is visibility built on
  shipped primitives — e.g. a `--family-scan` verb that shows what the
  installed loom-* plugins actually provide — not bundling plugins
  together or pre-wiring them.

- Explicitly rejected: **no stub files**. Shipping empty placeholder
  artifacts (hollow PRINCIPLES.md / DIRECTION.md scaffolds) so that
  presence-conditional machinery lights up is harmful: that machinery
  would consume hollow constitutions as if they were real decisions.
  Presence of an artifact must keep meaning someone actually authored
  it.

- The only hard-gate candidate: Axis 0's product-shaped moment
  (brainstorming's upstream-artifact gate, where an idea is recognized
  as product-shaped and routed to the upstream stations). Everything
  else stays pull/advisory.

- Foundation option: a partial merge of loom-code⊕loom-pipeline, which
  would also resolve the queue-layer ownership split recorded in
  `2026-08-10-queue-layer-family-ownership-north-star.md` (the
  `${CLAUDE_PLUGIN_ROOT}` cross-plugin gap traps family-wide tooling in
  single plugins). Whether to take it is the evaluation arc's question,
  not decided here.

- Next step when the start condition fires: open the evaluation arc
  with this entry and the queue-layer north-star entry as its seed
  inputs; the arc's job is to weigh the partial-merge option against
  staying multi-plugin with visibility verbs only.
