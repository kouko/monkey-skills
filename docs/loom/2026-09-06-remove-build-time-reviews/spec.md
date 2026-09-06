# Remove automatic reviews during Build — spec
intent: 2026-09-06-remove-build-time-reviews@d6a8829a
confirmed-behavior: 2026-09-06 @5ba1019

## Requirements
REQ-1 — No automatic formal review during Build
  WHILE Build still has unfinished tasks, the Loom flow shall run task-scoped tests and necessary integration checks but shall not automatically invoke formal review for an individual task or a completed wave → Acceptance #1

REQ-2 — Positive and negative protection remains before implementation
  BEFORE a task implementation begins, the Loom flow shall retain its positive test-first case and, where the existing risk policy requires adversary-first work, an independently authored negative or abuse case that the implementation may not weaken or remove → Acceptance #2

REQ-3 — Branch-end review remains mandatory
  WHEN every planned task is complete, the Loom flow shall run the existing branch-end review with the reviewer count, blind run, adversarial verification, and fix rounds required by the effective lane before Ship may begin → Acceptance #3

REQ-4 — All other review and shipping contracts remain unchanged
  The Loom flow shall preserve lane selection, reviewer-implementer separation, the versioned review record, evidence freshness, the blind-run report, the review-only HEAD requirement, and every Ship blocking rule not specific to after-task or wave-end review → Acceptance #4

REQ-5 — The deletion is measured on a real multi-task change
  WHEN a historical multi-task change that triggered an intermediate checkpoint is replayed, the new flow shall use fewer review dispatches and less checkpoint waiting while still running the same permanent tests and surfacing the findings observable at branch end → Acceptance #5

## Design decision
- user-decided — Remove only automatically triggered after-task and wave-end formal reviews; do not redesign the wider verification model until this deletion is measured.
- agent-decided — Keep waves as task scheduling and integration boundaries, because parallel work and merge ordering remain useful even when wave completion no longer triggers review.
- agent-decided — Remove `review: after-task` from new plan syntax and remove the wave-size review calculation from Build, because leaving either marker would preserve two ways to reintroduce the deleted checkpoint.
- agent-decided — Keep task-level TDD and integration checks inside Build; a test failure remains a repair loop, not a formal review checkpoint.
- agent-decided — Keep the current adversary-first rule for high-risk code and gate tasks, because executable negative cases protect implementation without issuing a review verdict.
- agent-decided — Keep one branch-end review over the complete branch, including its existing lane-specific reviewer, blind-run, adversarial, and fix-round behavior.
- agent-decided — Preserve explicit user-requested review as an out-of-band diagnostic, because deleting automatic checkpoints does not need to prohibit the user from asking for an inspection.
- agent-decided — Measure elapsed waiting and review dispatches separately from defect-fix time, because moving a real finding to branch end does not make its repair cost disappear.
- user-decided — Use Claude as the second-vendor reviewer for this change.

## Alternatives considered
- Redesign lanes, risk classification, review evidence, and Ship together — rejected because it adds unrelated failure modes before the cost of intermediate reviews is isolated.
- Keep wave-end review but raise the file or line threshold — rejected because every threshold retains the checkpoint machinery and makes the result workload-dependent.
- Keep `review: after-task` as a default escape hatch — rejected because planned automatic exceptions would preserve the same per-task review path; explicit user-requested review remains available.
- Remove adversary-first work together with intermediate review — rejected because an adversary that writes failing abuse cases before implementation is test design, not a formal review verdict.
- Remove waves entirely — rejected because waves still express dependency and parallel integration order.

## Current state evidence
- Forward: `loom-code/skills/build/SKILL.md` at `Step 5` invokes review immediately for a task marked `review: after-task`.
- Reverse: `loom-code/skills/write-plan/SKILL.md` at `Step 5 — Write the plan` emits the `review: after-task` task grammar and budgets intermediate checkpoints.
- Error: `loom-code/skills/build/SKILL.md` at `Step 6 — close the wave` computes file and line thresholds and invokes wave-end review before later work continues.
- Data: `loom-code/contract/manifest.yaml` at the `checkpoint` mechanism and plan `Task DAG` field declares after-task, wave-end, and branch-end scopes in one contract.
- Boundary: `loom-code/skills/review/SKILL.md` at `Which slice this checkpoint owns` distinguishes after-task and wave-end scopes from branch-end; this change deletes the first two automatic callers but retains branch-end behavior.

## UI flows
### Plan and Build
- 計畫完成 → 系統仍建立 task、相依關係、正向測試與既有風險規則要求的負向或攻擊案例，但不安排 task 後或 wave 後的正式審查。
- 一個 task 完成且測試通過 → 系統直接執行下一個可進行的 task，不等待審閱者，也不要求使用者回覆。
- task 測試或整合檢查失敗 → 系統修正並重跑受影響測試；測試通過前不進入下一個相依 task。
- 高風險 task 尚未開始 → 獨立對抗者仍先產生負向或攻擊案例，實作者依正向與負向案例進行測試先行開發；這個步驟不產生 review verdict。
- 使用者在實作途中明確要求檢查 → 系統可以執行一次臨時 review，但新流程不會自動提出或排程它。

### Review and Ship
- 所有 task 完成 → 系統依既有風險與速度模式執行一次完整 branch-end review。
- branch-end review 發現問題 → 系統修正後依既有 fix-round 規則重審，直到通過或達到停止條件。
- branch-end review 通過 → 系統依既有證據新鮮度、盲跑報告、review-only HEAD 與 Ship gate 規則完成出貨。
