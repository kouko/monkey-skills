---
name: 2026-08-12-loom-plugin-consolidation-needs-sync-cost-data
description: whether to merge the six loom plugins into one — parked until shared-mechanism sync cost is measured, not decided on felt friction; loom-code already acts as the de facto anchor for shared infrastructure
status: closed
origin: 2026-08-12 adjudication-digest design discussion — the user observed shared mechanisms accumulating across plugins (progress tooling SSOT + shims in PR#680, gate markers, cross-plugin reviewer agents, family-relay, and the upcoming adjudication-digest protocol) and asked whether the plugins should be merged
start: a third shared-mechanism shim cascade lands, OR a per-ship sync-cost inventory (files touched across plugins per release, sampled over recent PRs) shows multi-plugin overhead dominating — whichever comes first
---

- Start: a third shared-mechanism shim cascade lands, OR a per-ship
  sync-cost inventory (files touched across plugins per release, sampled
  over recent PRs) shows multi-plugin overhead dominating — whichever
  comes first

- Origin: 2026-08-12 adjudication-digest design discussion — the user
  observed shared mechanisms accumulating across plugins (progress
  tooling SSOT + shims in PR#680, gate markers, cross-plugin reviewer
  agents, family-relay, and the upcoming adjudication-digest protocol)
  and asked whether the plugins should be merged

- The question split: **jurisdiction boundaries** (six stations map to
  distinct user intents and charters — merging moves that complexity
  from plugin boundaries into folder boundaries, it does not remove it)
  vs **shared infrastructure** (the actual felt pressure). The repo
  already has a working answer for the second half: consolidate shared
  machinery into loom-code as anchor + shims/references at call sites
  (PR#680 precedent) + the cross-plugin delegation contract.

- Prior history: the 0.10.0 DESIGN.md-conformance arc (PR#679) started
  from this same merge question, then dissolved into fixing upstream
  spec conformance after finding the upstream station had barely been
  used — no verdict on merging was recorded. The low-usage finding cuts
  both ways (merge to cut per-station overhead vs don't operate on a
  cold surface) — which is why this entry demands data, not argument.

- Decision inputs when the arc opens: (i) inventory of genuinely shared
  surfaces and their sync mechanisms (shim / mirror / contract-ref);
  (ii) measured per-ship sync cost — files touched across plugins per
  release over a recent-PR sample; (iii) per-station usage evidence
  (which stations fire in real sessions); (iv) the migration bill —
  marketplace entries, six plugin.json version histories, .codex-plugin
  mirrors, hook relocations, old-name mining after rename, install docs.

- Explicit decoupling: the adjudication-digest arc proceeds in loom-code
  regardless — loom-code is the anchor in both the merged and unmerged
  world, so that arc neither blocks on nor prejudges this decision.

- **SHIPPED 2026-08-17 — branch `loom-design-merge`** (blueprint
  `docs/loom/plans/2026-08-16-loom-design-merge-plan.md`, executed as
  parts 1-3). Resolution: **6 → 2**, not 6 → 1. The jurisdiction half of
  the split was answered by keeping the design/code boundary (the two
  surviving plugins are `loom-design` and `loom-code`) while collapsing
  the four design stations that shared one user intent into one plugin
  with one entry router — folder boundaries inside `loom-design`, plugin
  boundary only where the jurisdictions genuinely differ. The shared
  infrastructure half went the way this entry predicted: family hooks and
  `loom-memory` anchored into `loom-code` (D1/D2), member skill names
  unchanged (D3), so the 440-dispatch `loom-code:*` hot path took zero
  impact. Migration bill actually paid: 271 files, marketplace 6 → 2,
  five plugin.json + .codex-plugin mirrors retired, driver asset rebuilt,
  ~380 references re-pointed. Acceptance recorded in part-3's §6 table
  (2463 tests green, skill count 24, per-session injection 9213 bytes,
  cold-reader routing correct).
