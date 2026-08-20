---
name: 2026-07-10-change-binding-chain-integration-test
description: Change-binding chain integration test
status: open
origin: Cluster B whole-branch review 🟡 (2026-07-10, PR #526). The parent designer/PM-loop implementation entry completed 2026-07-10: Cluster B shipped as PR #526, Cluster A (construction flow, Tasks 1-7 incl. cold-operator dogfood ship gate, 4 PASS + 1 PARTIAL with F1-F3 folded back) shipped on branch `feat-loom-product-principles-construction-flow` — this debt item is the only survivor.
start: next loom-code touch.
---

- Start: next loom-code touch.
- Origin: Cluster B whole-branch review 🟡 (2026-07-10, PR #526). The
  parent designer/PM-loop implementation entry completed 2026-07-10:
  Cluster B shipped as PR #526, Cluster A (construction flow, Tasks
  1-7 incl. cold-operator dogfood ship gate, 4 PASS + 1 PARTIAL with
  F1-F3 folded back) shipped on branch
  `feat-loom-product-principles-construction-flow` — this debt item is
  the only survivor.
- What: no integration test exercises the spec→plan→coverage→archive
  CHAIN — a plan fixture with a real join key scored covered by
  `check_scenario_coverage.py`, then the same change-id archived by
  `archive_change_folder.py`. Grammar consistency verified manually;
  the test guards future drift. Add
  `loom-code/scripts/test_change_binding_chain.py`.
