# Risk-triggered pre-build review and branch-end-only Build review — spec
intent: 2026-09-06-remove-build-time-reviews@c780ff3c
confirmed-behavior: 2026-09-06 @72788ab
pre-build-review: required — this change modifies workflow gates, review records, and the checker

## Requirements
REQ-1 — Mechanical readiness before Build
  BEFORE Build starts on a newly authored plan, the Loom flow shall require every non-memory task line to carry `acceptance: <numbers>` naming existing intent Acceptance lines and each referenced number to have a non-empty `A<n> positive: <test-id>` plus `negative: <test-id>` or `boundary: <test-id>` pair in that task's existing `Test:` line; it shall reject nonexistent references, any intent Acceptance line owned by no task, an intent whose Open questions is not exactly `- none`, and a new spec without `pre-build-review: required|not-required — <reason>` → Acceptance #1

REQ-2 — Formal spec review is risk-triggered and lightweight
  IF a new spec declares `pre-build-review: required` because the change affects security or privacy, irreversible data, a public contract, cross-system architecture, or materially ambiguous requirements THEN the Loom flow shall run one pre-build checkpoint with one independent reviewer covering both specification and adversarial concerns and no blind run; a new `not-required` spec shall proceed after mechanical readiness, while a legacy spec with no declaration resolves to `required` and proceeds after its existing passing spec review rather than failing declaration presence → Acceptance #2

REQ-3 — No automatic formal review during Build
  WHILE Build is active, including final-task and final-wave closure, the Loom flow shall not automatically invoke an `after-task` or `wave-end` formal review; every required task-scoped test and integration check shall pass before that task is complete or a dependent task begins, and the sole automatic transition after Build shall be the closing `branch-end` review after package tests pass → Acceptance #3

REQ-4 — Positive, negative, and adversary-first protection remains
  WHEN the effective full-lane risk policy classifies a task as `code` or `gate`, a fresh-context adversary shall author an executable abuse case before the implementer is dispatched; every implementer shall execute the task's positive and negative or boundary cases in its test-first cycle, and the implementation shall not remove, skip, invert, or weaken those cases → Acceptance #4

REQ-5 — Branch-end review remains mandatory
  WHEN every planned task and the package tests are complete, the Loom flow shall run exactly one closing `branch-end` review with the reviewer count, blind run, adversarial verification, and fix rounds required by the effective lane; Ship shall remain blocked until that checkpoint reaches its lane-defined passing verdict with no unresolved blocking finding → Acceptance #5

REQ-6 — Other branch-end review and shipping contracts remain unchanged
  Relative to loom-code 1.7.0 at `130b4ca1691de465be71df163f620d761abef5fa`, the Loom flow shall preserve the effective-lane outcomes (`full`, `small`, `express`, `gate-only`) and declaration grammar, each lane's branch-end reviewer floor, blind-run trigger, adversarial pass, package-test evidence, fix-round behaviour and stop condition, reviewer-implementer separation, the versioned `review.json` record, evidence freshness, the review-only HEAD requirement, second-vendor enforcement, and every Ship blocking rule not specific to pre-build, `after-task`, or `wave-end` review; `pre-build-review: not-required` shall never lower a forcing-path branch-end lane → Acceptance #6

REQ-7 — The Build-time deletion is measured on a real multi-task change
  WHEN the self-contained `evidence/replay-fixture.yaml` and its checksummed committed-plan plus ordered per-task patches replay the real merged `2026-09-03-small-change-lane` change task by task, compare the recorded loom-code 1.7.0 baseline with the candidate's first review-only branch-end commit using the fixture's exact checkout, commit-trailer, permanent-command, model-input, event, clock, expected-RED, and hidden-finding rules. The candidate shall have zero Build-time formal-review dispatches and zero Build-time checkpoint blocking, the permanent-test outcomes shall match, and each oracle finding shall be independently rediscovered at branch end or explicitly shown inapplicable with evidence; unavailable pinned input makes the measurement `UNGRADABLE` rather than a speed claim → Acceptance #7

## Design decision
- user-decided — Replace mandatory formal spec review with a declared-risk trigger, remove Build-time formal reviews, and retain one complete branch-end review.
- agent-decided — Add `pre-build-review: required|not-required — reason` to specs; the explicit declaration is mechanically checkable while semantic risk remains a reviewer-visible judgment.
- agent-decided — New task lines carry `acceptance: <numbers>` and their capped Test line carries compact `A<n>` case identifiers; scenario detail stays in the spec so the plan charter remains bounded.
- agent-decided — Treat missing declarations on legacy specs as `required`, because silently weakening an already-started change would be unsafe.
- agent-decided — Trigger pre-build review for security or privacy, irreversible data, public contracts, cross-system architecture, and material ambiguity; these are the cases where a wrong plan is expensive to reverse.
- agent-decided — Use one independent reviewer with both spec and adversarial duties at a required pre-build checkpoint; multiple readers and a blind run are deferred to branch end where runnable evidence exists.
- agent-decided — Keep waves only as task scheduling and integration boundaries, removing `review: after-task` from new plan syntax and all automatic wave-end review calculations.
- agent-decided — Keep task-level TDD and integration checks inside Build; a test failure remains a repair loop, not a formal review checkpoint.
- agent-decided — Keep the existing adversary-first rule for high-risk code and gate tasks, because executable negative cases protect implementation without issuing a review verdict.
- agent-decided — Preserve explicit user-requested review as an out-of-band diagnostic.
- agent-decided — Existing committed plans keep their old task and Test grammar byte-for-byte, including `review: after-task`; paired-case readiness applies only while authoring a new plan, the new runtime reads but ignores legacy review markers, and an already-running older runtime retains its original behaviour.
- user-decided — Use Claude as the second-vendor reviewer for this change's branch-end review.

## Alternatives considered
- Remove every pre-build review — rejected because irreversible, security, contract, and architecture mistakes are cheaper to catch before implementation.
- Keep the existing formal spec checkpoint for every designed change — rejected because it moves the same repeated waiting cost ahead of Build.
- Keep multiple spec reviewers but remove only the blind run — rejected because low-risk changes would still pay the dominant dispatch and fix-round cost.
- Infer semantic risk entirely from paths or keywords — rejected because those signals cannot reliably distinguish a routine edit from an irreversible decision; the declaration stays explicit and review-visible.
- Keep wave-end review but raise its size threshold — rejected because every threshold preserves the checkpoint machinery and makes runtime depend on workload shape.
- Remove adversary-first work with intermediate review — rejected because an adversary-authored failing test is test design, not a formal review verdict.
- Remove waves entirely — rejected because waves still express dependency and parallel integration order.

## Current state evidence
- Forward: `loom-design/skills/write-spec/SKILL.md` Step 4 always hands a product spec to the full review station before a plan exists.
- Reverse: `loom-code/skills/write-plan/SKILL.md` Step 4 requires `intake.spec-pass`, and Step 5 emits `review: after-task` plus a five-checkpoint Build budget.
- Error: `loom-code/skills/build/SKILL.md` §4 and §5 pause after marked tasks or sufficiently large waves, while `loom-code/skills/review/SKILL.md` applies the same blind-run setup to spec and runnable branch scopes.
- Data: `loom-code/contract/manifest.yaml` declares one review record and after-task, wave-end, branch-end scopes; `loom-code/scripts/loom_checker.py` recomputes the current spec verdict floor and after-task budget.
- Boundary: `loom-code/skills/review/SKILL.md` keeps lane-specific branch-end review, adversarial verification, blind run, fix rounds, and second-vendor enforcement unchanged.
- Replay: `docs/loom/2026-09-06-remove-build-time-reviews/evidence/replay-fixture.yaml` pins a committed-plan patch plus six checksummed task patches, their ordered application and Task trailers, expected adversary RED, permanent-command location, and missing-input failure.

## UI flows
### Plan readiness and optional spec review
- 新規格與計畫準備完成 → 每個非 memory task 都會指出自己負責的驗收編號，並為每個編號列出正向案例及負向或邊界案例；系統也會阻擋不存在或無人負責的驗收編號、未決定的使用者問題，以及沒有風險判定與原因的新規格。
- 一般變更準備完成 → 系統不派正式規格審閱，直接進入 Build。
- 變更涉及資安、隱私、不可逆資料、公用契約、跨系統架構或明顯需求歧義 → 系統只派一位獨立審閱者，同時檢查規格完整度與對抗面，不做規格盲跑；通過後進入 Build。
- 舊規格沒有新欄位 → 系統採安全預設，沿用既有規格審閱結果；舊 plan 保留原本測試語法且不需改寫。

### Build
- 一個 task 完成且測試通過 → 系統直接執行下一個可進行的 task，不等待審閱者，也不要求使用者回覆。
- task 測試或整合檢查失敗 → 系統修正並重跑受影響測試；測試通過前不進入下一個相依 task。
- 高風險 task 尚未開始 → 獨立對抗者先產生可執行的攻擊案例，實作者依正向與負向案例進行測試先行開發；這個步驟不產生 review verdict。
- 使用者在實作途中明確要求檢查 → 系統可以執行一次臨時 review，但不自動提出或排程它。
- 舊 plan 含有 `review: after-task` → 檔案保持原樣且仍可讀；新 runtime 不因該標記自動派審，已由舊 runtime 啟動的 Build 不在途中切換語意。

### Review and Ship
- 所有 task 與 package tests 完成 → 系統依既有風險與速度模式執行唯一一次完整 branch-end review。
- branch-end review 發現問題 → 系統修正後依既有 fix-round 規則重審，直到通過或達到停止條件。
- branch-end review 未通過或仍有 blocking finding → Ship 保持阻擋。
- branch-end review 通過 → 系統依既有證據新鮮度、盲跑報告、review-only HEAD 與 Ship gate 規則完成出貨。
