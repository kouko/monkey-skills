---
name: 2026-08-10-queue-layer-family-ownership-north-star
description: the queue layer (backlog store + DIRECTION + plan ledger) is conceptually family-wide but physically owned by loom-code, because `${CLAUDE_PLUGIN_ROOT}` cannot point at sibling plugins — a cross-plugin primitive gap; north-star decision on where the layer should eventually live
status: OPEN
origin: 2026-08-10 cheap-hardening-batch arc — adjudicated in conversation during the direction-layer follow-up; filed so the decision is citable instead of re-litigated
start: next cross-plugin primitive change, or the partial-merge evaluation arc opening
---

- Start: next cross-plugin primitive change, or the partial-merge evaluation arc opening

- Origin: 2026-08-10 cheap-hardening-batch arc — adjudicated in conversation during the direction-layer follow-up; filed so the decision is citable instead of re-litigated

- What: the queue layer — the backlog store (`docs/loom/backlog/` +
  generated `BACKLOG.md`), `DIRECTION.md`, and the plan ledger — serves
  the whole loom-* family: every station's arcs read the ready query at
  kickoff and flip entries at close-out. Conceptually it is family-wide
  infrastructure. Physically it is trapped inside loom-code, because
  Claude Code's `${CLAUDE_PLUGIN_ROOT}` substitution can only resolve
  paths inside the plugin that declares it — there is no primitive for
  one plugin to point at a sibling plugin's files (the cross-plugin
  primitive gap). So the tooling ships where it can, not where it
  belongs.

- Why it matters: the family already carries a dual-owner
  inconsistency from the same gap — loom-memory (the practice-memory
  store skill) ships in loom-pipeline, while the backlog tooling
  (`backlog_index.py`, archive script) ships in loom-code. Two
  family-wide stores, two different accidental owners. Each new
  family-wide primitive added under this constraint deepens the split
  and makes an eventual consolidation more expensive.

- North star: the queue layer should be owned family-wide, not by
  whichever plugin happened to host its scripts. The concrete vehicle
  is undecided — candidates include a partial merge of
  loom-code⊕loom-pipeline (see the companion entry
  `2026-08-10-family-integration-evaluation-seed.md`) or a future host
  primitive that closes the cross-plugin gap. Next step when the start
  condition fires: re-evaluate ownership as part of that change rather
  than adding another accidentally-placed primitive.
