# Plan: loom-code skill-mining 修正落地

Source brief: docs/loom/specs/2026-06-22-loom-code-mining-fixes.md
Total tasks: 12
Critical-path depth: 3 (≤5)   ← T1 → T7 → T12
Execution order: parallel-where-possible
Plan-document-reviewer verdict: PASS (14/14, 2026-06-22)

Notes:
- 後修（PASS 後 additive，免重審）：T5 的 RED 由散文改為可跑 grep；欄位/DAG/結構不變，schema-safe。
- T4/T5/T6/T7 都 Edit `skills/subagent-driven-development/SKILL.md` → 共享檔，`Independent: false`，由 SDD 序列化派發（非 parallel）。彼此無語意依賴，故 Dependencies 多為 none，但不可標 Independent: true。
- T7/T8/T9/T10/T11 皆需 environment-gotchas.md 先存在 → Dependencies "Task 1 completes first"。其中 T8/T9/T10/T11 各動不同檔且僅依賴 T1 → 彼此 Independent: true，可在 T1 後一波並行；T7 因與 T4-T6 同檔不可並行。
- T12 是 dead-link gate：跑 validator 對整棵 loom-code 樹，需所有 pointer 與 validator 都就緒。
- 純 doc task 的 RED = 編輯前 grep 該斷言為假（exit 1）；GREEN = 編輯後 grep 命中（exit 0）。只有 T2 是傳統程式 TDD。

## Task 1 — 新增 environment-gotchas.md 共用 reference
- Description: 建立 `skills/using-loom-code/references/environment-gotchas.md`，收斂 5 類 orchestrator harness gotcha：(S1) 任何 Bash 檢視（grep/jq/sed/cat/head）不滿足 Edit/Write 的 Read precondition；(S2) dcg 互動——compound `git push && gh pr create` 要分兩次呼叫、`git checkout --` 被擋改 `git stash push`、commit body 含被擋字串改 `git commit -F /tmp/file`；(B3) `cd <subdir>` 在 Bash 持續→git 用絕對路徑或 `cd <repo-root> &&`；(D1) rebase 衝突用 Read+Edit 非 cat+Write；(E1) 未 staged 檔改名用 `mv` 非 `git mv`。每類一小節 + 一句 why。
- Module: skills/using-loom-code/references/environment-gotchas.md
- Files touched: skills/using-loom-code/references/environment-gotchas.md
- Context paths:
  - skills/using-loom-code/references/continuous-mode.md
  - docs/loom/specs/2026-06-22-loom-code-mining-fixes.md
- Acceptance:
  - RED: `test -f skills/using-loom-code/references/environment-gotchas.md` 失敗（檔不存在）
  - GREEN: 檔存在，且 `grep -q 'Read precondition' && grep -q 'git stash push' && grep -q 'git commit -F' && grep -q 'git mv'` 全命中（五類齊全）
- Dependencies: none
- Independent: true
- Brief item covered: "新增單一 skills/using-loom-code/references/environment-gotchas.md（涵蓋 S1/S2/B3/D1/E1）"

## Task 2 — check-skill-crossrefs.py dead-link validator（TDD）
- Description: 建 `scripts/check-skill-crossrefs.py`：走訪 `loom-code/skills/*/SKILL.md` 每個 markdown 相對連結 `](relative/path)`，解析（相對該 SKILL.md 目錄）後斷言目標存在；任一不存在則印出並 exit 1，全通過 exit 0。先寫 `scripts/test_check_skill_crossrefs.py`：fixture 含一個 dangling link → 斷言 exit 1；fixture 全有效 → exit 0。
- Module: loom-code/scripts/check-skill-crossrefs.py
- Files touched: loom-code/scripts/check-skill-crossrefs.py, loom-code/scripts/test_check_skill_crossrefs.py
- Context paths:
  - loom-code/scripts/check-shared-conventions-drift.py
  - loom-code/scripts/verify-drift.py
- Acceptance:
  - RED: `PYTHONDONTWRITEBYTECODE=1 python -m pytest loom-code/scripts/test_check_skill_crossrefs.py` 失敗（validator 未實作）
  - GREEN: 該 test 綠；validator 對 dangling-link fixture exit 1、對有效 fixture exit 0
- Dependencies: none
- Independent: true
- Brief item covered: "新增 loom-code/scripts/check-skill-crossrefs.py——走訪每個 SKILL.md 的相對連結、斷言目標檔存在"

## Task 3 — W1：plan-document-reviewer Check 11 文法補多前置 sequential
- Description: 在 `skills/writing-plans/references/plan-document-reviewer-prompt.md` 的 Check 11 合法文法（現為 `"none"` OR `"Task N completes first"` OR `"Tasks N, M parallel"`）補入 `"Tasks N, M complete first"`，與 `references/plan-format.md` L57（SSOT 四形式）對齊。
- Module: skills/writing-plans/references/plan-document-reviewer-prompt.md
- Files touched: skills/writing-plans/references/plan-document-reviewer-prompt.md
- Context paths:
  - skills/writing-plans/references/plan-format.md
- Acceptance:
  - RED: `grep -c 'Tasks N, M complete first' skills/writing-plans/references/plan-document-reviewer-prompt.md` 回 0
  - GREEN: Check 11 那列含 `"Tasks N, M complete first"`，且該文法集 = plan-format.md L57 四形式
- Dependencies: none
- Independent: true
- Brief item covered: "W1（真 bug）plan-document-reviewer L43 Check 11 文法補 \"Tasks N, M complete first\""

## Task 4 — B1：SDD capacity-error 補容量恢復 resume 路徑
- Description: 在 `skills/subagent-driven-development/SKILL.md` §Subagent capacity errors 段（"wait for capacity to recover" 之後）補 resume 路徑：容量恢復後 retrospective 補派被擋的 reviewer 到「已 commit 的產物」，NEEDS_REVISION → 新 fix commit（非 revert），其後流程同正常。
- Module: skills/subagent-driven-development/SKILL.md
- Files touched: skills/subagent-driven-development/SKILL.md
- Context paths:
  - skills/subagent-driven-development/SKILL.md
- Acceptance:
  - RED: `grep -iq 'retrospective\|容量恢復\|capacity recover' <capacity 段>` 無 resume 指引（編輯前為假）
  - GREEN: capacity 段含「恢復後補派 reviewer 到已 commit 產物 + NEEDS_REVISION→新 fix commit」字句
- Dependencies: none
- Independent: false
- Brief item covered: "B1 SDD capacity-error 段：補容量恢復後 resume 路徑"

## Task 5 — B2：SDD final-summary 預設推薦 finishing-a-development-branch
- Description: 在 `skills/subagent-driven-development/SKILL.md` §Continuous execution 的 final-summary pause point，補一句：全 task DONE 後預設推薦 `finishing-a-development-branch`（含 review+verification+push 的結構化 close-out），僅在使用者明確延後才提平級選項。
- Module: skills/subagent-driven-development/SKILL.md
- Files touched: skills/subagent-driven-development/SKILL.md
- Context paths:
  - skills/finishing-a-development-branch/SKILL.md
- Acceptance:
  - RED: `grep -c 'finishing-a-development-branch' skills/subagent-driven-development/SKILL.md` 在 §Continuous execution final-summary 段無推薦字句（編輯前該段為假）
  - GREEN: final-summary 段含「預設推薦 finishing-a-development-branch」（grep 命中於該段）
- Dependencies: none
- Independent: false
- Brief item covered: "B2 SDD §Continuous execution：補預設推薦 finishing-a-development-branch"

## Task 6 — B4：SDD parallel-wave commit 前 git status 檢查
- Description: 在 `skills/subagent-driven-development/SKILL.md` §Environment hygiene bullet 補一條：parallel wave 內每次 per-task commit 前先 `git status --short`，確認只 stage 該 task 檔——sibling implementer 可能已把自己的檔 stage 進共享 index，`git add <單檔>` 不會 unstage 它們。
- Module: skills/subagent-driven-development/SKILL.md
- Files touched: skills/subagent-driven-development/SKILL.md
- Context paths:
  - skills/subagent-driven-development/SKILL.md
- Acceptance:
  - RED: §Environment hygiene 無 `git status --short` 前置檢查字句（編輯前為假）
  - GREEN: §Environment hygiene 含「parallel wave commit 前 git status --short 確認只 stage 該 task 檔」
- Dependencies: none
- Independent: false
- Brief item covered: "B4 SDD §Environment hygiene：補 parallel wave commit 前 git status --short"

## Task 7 — SDD L112 放寬 read-precondition 措辭 + 指向共用 ref
- Description: 在 `skills/subagent-driven-development/SKILL.md` L112 Read-before-Edit 段，把「`grep`/`jq`」放寬為「任何 Bash 檢視（grep/jq/sed/cat/head）」，並加一句指向 `../using-loom-code/references/environment-gotchas.md`（細節在共用 ref）。
- Module: skills/subagent-driven-development/SKILL.md
- Files touched: skills/subagent-driven-development/SKILL.md
- Context paths:
  - skills/using-loom-code/references/environment-gotchas.md
- Acceptance:
  - RED: L112 段仍只列 grep/jq 且無 environment-gotchas pointer（編輯前為假）
  - GREEN: 措辭含 sed/cat 等廣義列舉，且含 `../using-loom-code/references/environment-gotchas.md` 連結（且該檔存在）
- Dependencies: Task 1 completes first
- Independent: false
- Brief item covered: "放寬 SDD L112 過窄措辭並改為指向共用 ref（消除雙重）"

## Task 8 — tdd-iron-law pointer 指向共用 ref
- Description: 在 `skills/tdd-iron-law/SKILL.md` 適當既有 section（§See also 或 §Red-Green-Refactor 尾；tdd-iron-law 無 §Cross-skill contract heading）加一行 pointer 指向 `../using-loom-code/references/environment-gotchas.md`，提醒直接 TDD 路徑（無 SDD）批次 refactor 時 Read-precondition 同樣適用。
- Module: skills/tdd-iron-law/SKILL.md
- Files touched: skills/tdd-iron-law/SKILL.md
- Context paths:
  - skills/tdd-iron-law/SKILL.md
  - skills/using-loom-code/references/environment-gotchas.md
- Acceptance:
  - RED: `grep -c 'environment-gotchas' skills/tdd-iron-law/SKILL.md` 回 0
  - GREEN: 含 `../using-loom-code/references/environment-gotchas.md` 連結（且檔存在）
- Dependencies: Task 1 completes first
- Independent: true
- Brief item covered: "5 處 pointer……tdd-iron-law → environment-gotchas.md"

## Task 9 — finishing 放寬 read-precondition + pointer（rebase/compound-push 收斂共用 ref）
- Description: 在 `skills/finishing-a-development-branch/SKILL.md`：放寬既有重複的 read-precondition 字句並改為指向 `../using-loom-code/references/environment-gotchas.md`；在 §Default flow push step（L126 附近）加一句指向共用 ref（compound push 分兩次呼叫 + rebase 衝突 Read+Edit 細節在共用 ref）。
- Module: skills/finishing-a-development-branch/SKILL.md
- Files touched: skills/finishing-a-development-branch/SKILL.md
- Context paths:
  - skills/finishing-a-development-branch/SKILL.md
  - skills/using-loom-code/references/environment-gotchas.md
- Acceptance:
  - RED: `grep -c 'environment-gotchas' skills/finishing-a-development-branch/SKILL.md` 回 0
  - GREEN: 含 `../using-loom-code/references/environment-gotchas.md` 連結（且檔存在），且原過窄 read-precondition 字句已收斂為指向
- Dependencies: Task 1 completes first
- Independent: true
- Brief item covered: "放寬……finishing 的過窄 read-precondition 措辭並改為指向共用 ref"

## Task 10 — using-git-worktrees pointer（E1 mv vs git mv）
- Description: 在 `skills/using-git-worktrees/SKILL.md` §The `.worktrees/` convention 加一行 pointer 指向 `../using-loom-code/references/environment-gotchas.md`（未 staged 檔改名用 mv 非 git mv 等 worktree 內檔案操作 gotcha 細節在共用 ref）。
- Module: skills/using-git-worktrees/SKILL.md
- Files touched: skills/using-git-worktrees/SKILL.md
- Context paths:
  - skills/using-git-worktrees/SKILL.md
  - skills/using-loom-code/references/environment-gotchas.md
- Acceptance:
  - RED: `grep -c 'environment-gotchas' skills/using-git-worktrees/SKILL.md` 回 0
  - GREEN: 含 `../using-loom-code/references/environment-gotchas.md` 連結（且檔存在）
- Dependencies: Task 1 completes first
- Independent: true
- Brief item covered: "5 處 pointer……using-git-worktrees → environment-gotchas.md"

## Task 11 — using-loom-code §Reference 登錄 environment-gotchas
- Description: 在 `skills/using-loom-code/SKILL.md` §Reference 清單加一行登錄 `references/environment-gotchas.md`（一句說明：orchestrator harness/dcg/Read-precondition gotcha 集中地，跨 SDD/tdd/finishing/worktrees 共用）。
- Module: skills/using-loom-code/SKILL.md
- Files touched: skills/using-loom-code/SKILL.md
- Context paths:
  - skills/using-loom-code/SKILL.md
  - skills/using-loom-code/references/environment-gotchas.md
- Acceptance:
  - RED: `grep -c 'environment-gotchas' skills/using-loom-code/SKILL.md` 回 0
  - GREEN: §Reference 含 `references/environment-gotchas.md` 條目（且檔存在）
- Dependencies: Task 1 completes first
- Independent: true
- Brief item covered: "+ using-loom-code §Reference 清單登錄"

## Task 12 — dead-link gate：validator 對全樹 exit 0
- Description: 跑 `python loom-code/scripts/check-skill-crossrefs.py`（對整棵 loom-code skills 樹），斷言 exit 0——所有相對連結（含本次新增 5 處 pointer + 既有 30+ 跨引用）皆解析得到。若有斷裂，修正對應 pointer/路徑直到綠。
- Module: loom-code/scripts/check-skill-crossrefs.py
- Files touched: （無新增；驗證步驟，必要時修前序 task 的 pointer 路徑）
- Context paths:
  - loom-code/scripts/check-skill-crossrefs.py
- Acceptance:
  - RED: 在 pointer 尚未全部就緒時跑 validator → exit 1（dangling）
  - GREEN: 全部 pointer + target 就緒後 `python loom-code/scripts/check-skill-crossrefs.py` exit 0
- Dependencies: Tasks 2, 7, 8, 9, 10, 11 parallel
- Independent: false
- Brief item covered: "進 CI，確保此次新增 pointer 與既有 30+ 跨引用永不靜默斷裂"
