# Cost of this change (commit timestamps, 2026-09-04)

| phase | from → to | minutes | notes |
|---|---|---|---|
| intent confirmed → plan committed | 00:10 → 00:12 | 2 | plan written by the orchestrator |
| build W0 (adversary-first probes → checker) | 00:12 → 00:39 | 27 | probes 00:19; W1-01/W1-02 ran in parallel in worktrees (00:21, 00:23) |
| after-task:W0-02 checkpoint (2 readers, 1 fix round, PRINCIPLES amendment) | 00:40 → 00:58 | 18 | codex NEEDS_REVISION ×3 important (all real), sonnet PASS_WITH_NOTES; fix round read only the two fix commits |
| integrate W1 + W1-03/W1-04 | 00:58 → 01:04 | 6 | station-summary sync across nine files |
| branch-end phase 1 (blind run + skill adversary) | 01:04 → 01:14 | 10 | adversary F1/F2 real (nit batch could not reach push; override claim) |
| F1/F2 fix + phase-2 readers, standing fix, fix round | 01:15 → 01:35 | 20 | F1/F2 fix, phase-2 readers, standing fix, fix round |

Total: intent confirmed 00:10 → branch-end review-only 01:34: 84 min (full lane); the 20-minute target applies to the next small-lane change (Acceptance 4).

Rules of this change applied to itself: stateful fix rounds (only the fix commits, resumed readers), severity by consequence, nits deferred to the ship nit batch, probes before the checker implementation (W0-01 → W0-02).
