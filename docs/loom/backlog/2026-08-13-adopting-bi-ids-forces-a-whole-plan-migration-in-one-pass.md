---
name: 2026-08-13-adopting-bi-ids-forces-a-whole-plan-migration-in-one-pass
description: the first brief to declare a BI- identifier makes every task in its plan illegal at once — brief mode treats any value naming no declared id as a defect, so adoption is all-or-nothing per plan with no incremental path
status: open
origin: 2026-08-13 brief-item-addressability arc, Task 11 spec review — running brief mode against this arc's own brief with one id injected produced ten unresolvable-citation errors, one per task, because every task in that plan cites by quote
start: the first brief that declares a BI- identifier is authored, OR a second arc adopts the convention — whichever comes first
---

- Start: the first brief that declares a BI- identifier is authored, OR a
  second arc adopts the convention — whichever comes first

- Origin: 2026-08-13 brief-item-addressability arc, Task 11 spec review —
  running brief mode against this arc's own brief with one id injected produced
  ten unresolvable-citation errors, one per task, because every task in that
  plan cites by quote

- **The cliff**: brief mode is regime-switched on the brief, not per task. A
  brief declaring zero ids runs in announced legacy mode and quote referents
  stay legal. The moment it declares ONE id, every task's `Brief item covered`
  must be a resolvable `BI-<n>` or `none — <reason>`; a quote referent becomes
  an error naming the task. So adoption is all-or-nothing per plan.

- **This is designed, not accidental** — grounded in
  `check_scenario_coverage.py`'s own docstring ("the brief HAS identifiers, so a
  value naming none of them is a defect rather than a legal prose referent") and
  intended by Task 4's two-regime split. The defect is not the behaviour; it is
  that nothing warns an author about the cliff before they step off it.

- **Why it matters now**: the next committed arc
  (`2026-08-13-requirement-identity-splits-between-birthplace-and-living-spec`)
  is the natural first adopter. If it declares ids in its brief without
  migrating every task's citation in the same pass, its own coverage gate fails
  on every task — a self-inflicted red gate on the arc that introduces the
  convention to real use.

- **Candidate shapes, none decided**: (a) a one-line warning when a brief
  declares ids and ANY task still carries a quote referent, distinguishing
  "mid-migration" from "malformed"; (b) a mixed regime where quote referents
  stay legal alongside ids, at the cost of the traceability the arc was built
  for; (c) leave it and document the cliff in `handoff-brief-format.md` so the
  first adopter is warned rather than surprised. (c) is cheapest and probably
  right; (a) is the honest middle.

- **Related**: the arc's plan records this under "Ironic self-reference" — the
  brief that introduces the convention declares no ids itself, because the
  convention does not exist until its own Task 1 lands.
