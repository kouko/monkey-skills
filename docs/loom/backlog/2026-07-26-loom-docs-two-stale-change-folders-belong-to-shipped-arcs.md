---
name: 2026-07-26-loom-docs-two-stale-change-folders-belong-to-shipped-arcs
description: loom docs — two stale change-folders belong to shipped arcs
status: OPEN
---

- **What.** `docs/loom/2026-07-12-us-sec-primary-source-layer` and
  `docs/loom/2026-07-19-8k-prose-kpi-intake` sit un-archived at the top level of
  `docs/loom/` while both belong to arcs that already shipped. Archive them.
- **Why it matters, and why it is small.** A live-looking change-folder is the
  first thing a new arc's planner checks for a binding; two that bind nothing
  make every future plan spend a paragraph ruling them out (this one did). Pure
  housekeeping — no code, no tests.
- **Why it was not done in that arc.** Unrelated to the branch's work; folding
  it in would have been scope creep in a branch already touching 8 modules.
- Re-trigger: the next loom arc that opens a change-folder, or any docs-only
  housekeeping pass over `docs/loom/`.
