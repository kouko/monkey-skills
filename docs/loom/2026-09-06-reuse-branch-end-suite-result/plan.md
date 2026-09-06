# Single-owner local push-gate package test — plan
intent: 2026-09-06-reuse-branch-end-suite-result@ddee7445
spec: docs/loom/2026-09-06-reuse-branch-end-suite-result/spec.md@c8b3d83e
charter: 1.0

## Task DAG

### Wave 0 — One execution owner and fail-closed boundary

**W0-01 Make the local push hook the sole package-suite owner**  acceptance: 1,2,3
- Files: loom-code/skills/review/SKILL.md, loom-code/skills/ship/SKILL.md, loom-code/scripts/test_review_station_text.py, loom-code/scripts/test_ship_station_text.py
- Test: A1 positive: hook-only-owner; boundary: no-branch-end-run. A2 positive: no-explicit-preflight; negative: missing-hook-blocks. A3 positive: repo-command-neutral; boundary: no-path-classification.
- Risk: agent-decided — remove only the two station-owned duplicate calls; retain the deterministic push rule, recorded command contract, adversarial recomputes, and existing supported-host requirement.

**W0-02 Remove residual pre-review runs and reject push-gate mutation**  after: W0-01  acceptance: 1,2,4,5
- Files: loom-code/skills/build/SKILL.md, loom-code/skills/ship/SKILL.md, loom-code/scripts/loom_checker.py, loom-code/scripts/test_build_station_text.py, loom-code/scripts/test_ship_station_text.py, loom-code/scripts/test_loom_checker_push.py, loom-code/scripts/test_loom_checker_hardening.py
- Test: A1 positive: no-build-or-ship-suite; boundary: hook-only-run. A2 positive: stable-head-releases; negative: suite-moves-head-blocks. A4 positive: detected-command-runs; boundary: none-and-invalid-outcomes. A5 positive: environment-retry-stable; negative: tracked-fix-invalidates.
- Risk: agent-decided — remove the newly discovered Build and Ship-checklist suite calls, preserve other deterministic checks, and compare HEAD plus porcelain after executable probes without trusting recorded results.

### Wave 1 — Measured workflow reduction

**W1-01 Replay the same Ship-to-push case and measure the reduction**  after: W0-01,W0-02  acceptance: 6
- Files: docs/loom/2026-09-06-reuse-branch-end-suite-result/evidence/measurement.md, docs/loom/2026-09-06-reuse-branch-end-suite-result/evidence/probes/test_single_owner_push_gate.py
- Test: A6 positive: candidate-one-call-faster-same-verdict; boundary: observed-baseline-count-not-assumed.
- Risk: agent-decided — use one fixed local fixture and monotonic timings for both revisions; report measured counts and seconds without extrapolating to other repositories.

**W1-memory Memory step — graduated probes and store entries**  after: W1-01
- Files: loom-code/scripts/test_single_owner_push_gate.py, docs/loom/memory/
- Test: python3 scripts/check_loom_memory_integrity.py --check; python3 loom-code/scripts/test_single_owner_push_gate.py
- Risk: agent-decided — graduate only reusable repository-neutral cases and durable lessons; keep change-specific timing evidence under this change.

## Questions asked
1 — what — 當這個改動完成後，你希望達成什麼結果？例如：如果 Ship 的 HEAD 與 branch-end 已驗證的 commit 完全相同，就直接重用既有測試證據；只要程式或測試有任何變更，才重跑完整 suite。這是你要的嗎？
1 — what — 下一個要確認的是品質底線：哪些情況絕對不能重用舊結果？你希望還有哪些情況一定要強制重跑？
1 — what — 對於沒有設定安全範圍的 repo，你是否同意預設仍重跑完整 suite，避免 Loom 自行猜測哪些變更「應該沒影響」？
1 — consequence — 這次要不要用 Claude 作為第二位讀者？會多花幾分鐘與一些額度。
1 — what — 請確認以上就是你要的範圍。
1 — what — 這會修正剛才 intent 的 Proposed outcome，但不改變你要的外部結果：完整 suite 仍只跑一次，品質底線不降低。確認改成這個方向嗎？
2 — behaviour — 這個行為符合你的預期嗎？
2 — behaviour — 這就是你預期的修改後機制嗎？

## Risks
1. Removing the explicit preflight makes host-hook liveness essential; station text must block rather than describe an unguarded manual push as Loom Ship.
2. A suite may mutate Git while exiting zero; the final state recompute must cover package and adversarial execution before the hook releases the push.
3. Timing varies with machine load; only invocation count is deterministic, while elapsed time is evidence for the fixed replay rather than a universal promise.
