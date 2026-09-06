# Remove automatic reviews during Build — spec
intent: 2026-09-06-remove-build-time-reviews@d6a8829a
confirmed-behavior: 2026-09-06 @77c179b

## Requirements
REQ-1 — No automatic formal review during Build
  WHILE Build is active, including final-task and final-wave closure, the Loom flow shall not automatically invoke an `after-task` or `wave-end` formal review; every required task-scoped test and integration check shall pass before that task is complete or a dependent task begins, and the sole automatic transition to formal review shall be the closing `branch-end` review after package tests pass → Acceptance #1

REQ-2 — Positive and negative protection remains before implementation
  BEFORE a task implementation begins, the plan shall trace every Acceptance behaviour the task owns to at least one positive case and one negative or boundary case; the implementer shall execute those cases in the task's test-first cycle and they shall pass before task completion. WHEN the effective full-lane risk policy classifies a task as `code` or `gate`, a fresh-context adversary shall additionally author an abuse case before the implementer is dispatched; the implementation may not remove, skip, invert, or weaken any of these cases → Acceptance #2

REQ-3 — Branch-end review remains mandatory
  WHEN every planned task and the package tests are complete, the Loom flow shall run exactly one closing `branch-end` review with the reviewer count, blind run, adversarial verification, and fix rounds required by the effective lane; Ship shall remain blocked until that checkpoint reaches its lane-defined passing verdict with no unresolved blocking finding → Acceptance #3

REQ-4 — All other review and shipping contracts remain unchanged
  Relative to loom-code 1.7.0 at `130b4ca1691de465be71df163f620d761abef5fa`, the Loom flow shall preserve the mechanical effective-lane selection and every declared mode (`full`, `small`, `express`, `gate-only`), including each mode's branch-end reviewer floor, blind-run trigger, adversarial pass, package-test evidence, fix-round behaviour, and stop condition. It shall also preserve reviewer-implementer separation, the versioned `review.json` record, evidence freshness, the blind-run report, the review-only HEAD requirement, and every Ship blocking rule not specific to `after-task` or `wave-end` review → Acceptance #4

REQ-5 — The deletion is measured on a real multi-task change
  WHEN the committed `2026-09-03-small-change-lane` change is replayed from its plan commit `6a2910e7` through its last planned-task commit `8bd5fc7e`, compare the baseline runtime `130b4ca1` with the candidate's first review-only branch-end commit on the same machine and checkout inputs. Count a formal-review dispatch only when `dispatch[].role` is `reviewer`, `blind-runner`, or `adversary` and `dispatch[].task` begins `after-task:` or `wave-end:`; measure checkpoint blocking from the first such dispatch timestamp through its passing checkpoint commit, and report defect-fix time separately. Both runs shall execute the exact Test commands named by the fixed plan, retain raw command output and timestamps, and present every important-or-worse baseline intermediate finding to the branch-end readers as a fixed oracle. The candidate shall have zero Build-time formal-review dispatches and zero Build-time checkpoint blocking, the permanent-test outcomes shall match, and each oracle finding shall be independently rediscovered at branch end or explicitly shown inapplicable with evidence → Acceptance #5

## Design decision
- user-decided — Remove only automatically triggered after-task and wave-end formal reviews; do not redesign the wider verification model until this deletion is measured.
- agent-decided — Keep waves as task scheduling and integration boundaries, because parallel work and merge ordering remain useful even when wave completion no longer triggers review.
- agent-decided — Remove `review: after-task` from new plan syntax and remove the wave-size review calculation from Build, because leaving either marker would preserve two ways to reintroduce the deleted checkpoint.
- agent-decided — Keep task-level TDD and integration checks inside Build; a test failure remains a repair loop, not a formal review checkpoint.
- agent-decided — Keep the current adversary-first rule for high-risk code and gate tasks, because executable negative cases protect implementation without issuing a review verdict.
- agent-decided — Keep one branch-end review over the complete branch, including its existing lane-specific reviewer, blind-run, adversarial, and fix-round behavior.
- agent-decided — Preserve explicit user-requested review as an out-of-band diagnostic, because deleting automatic checkpoints does not need to prohibit the user from asking for an inspection.
- agent-decided — Measure elapsed waiting and review dispatches separately from defect-fix time, because moving a real finding to branch end does not make its repair cost disappear.
- agent-decided — Existing committed plans keep their text byte-for-byte, including `review: after-task`; under the new runtime those legacy markers are readable but ignored for automatic dispatch. A Build already started under an older runtime keeps that runtime's behaviour, so this change does not silently migrate an active worktree.
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
- Replay: `docs/loom/2026-09-03-small-change-lane/plan.md` pins the task graph and permanent Test commands; its `review.json` records two `after-task:W0-02` reviewer dispatches and their important findings, while `evidence/cost.md` records the checkpoint as 18 elapsed minutes.

## UI flows
### Plan and Build
- 計畫完成 → 每條驗收行為都有至少一個正向案例及一個負向或邊界案例；系統仍建立 task 與相依關係，高風險 task 另有獨立攻擊案例，但不安排 task 後或 wave 後的正式審查。
- 一個 task 完成且測試通過 → 系統直接執行下一個可進行的 task，不等待審閱者，也不要求使用者回覆。
- task 測試或整合檢查失敗 → 系統修正並重跑受影響測試；測試通過前不進入下一個相依 task。
- 高風險 task 尚未開始 → 獨立對抗者仍先產生負向或攻擊案例，實作者依正向與負向案例進行測試先行開發；這個步驟不產生 review verdict。
- 使用者在實作途中明確要求檢查 → 系統可以執行一次臨時 review，但新流程不會自動提出或排程它。
- 舊 plan 含有 `review: after-task` → 檔案保持原樣且仍可讀；新 runtime 不因該標記自動派審，已由舊 runtime 啟動的 Build 則不在途中切換語意。

### Review and Ship
- 所有 task 與 package tests 完成 → 系統依既有風險與速度模式執行唯一一次完整 branch-end review。
- branch-end review 發現問題 → 系統修正後依既有 fix-round 規則重審，直到通過或達到停止條件。
- branch-end review 未通過或仍有 blocking finding → Ship 保持阻擋。
- branch-end review 通過 → 系統依既有證據新鮮度、盲跑報告、review-only HEAD 與 Ship gate 規則完成出貨。
