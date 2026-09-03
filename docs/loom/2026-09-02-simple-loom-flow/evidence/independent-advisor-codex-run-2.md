# independent-advisor run #2 record (verbatim) — 2026-09-02

## meta
start=2026-09-02T03:30:04Z
probe_exit=0
model: gpt-5.6-sol
reasoning effort: high
exit=0
end=2026-09-02T03:37:06Z
audit tokens: 120,971 ; probe tokens: see probe-2.out ; cost: unknown (subscription)
sandbox: read-only ; cwd: scratchpad

## files opened OUTSIDE the packet
/bin/zsh -lc "sed -n '1,260p' ./advisor-packet-2.md && rg -n \"simple-loom-flow|audit|advisor\" /Users/kouko/.codex/memories/MEMORY.md"
/bin/zsh -lc "sed -n '1,260p' /Users/kouko/.codex/plugins/cache/monkey-skills/loom-code/0.110.0/skills/using-loom-code/SKILL.md"

## packet (verbatim)
# Independent audit packet #2 — loom concept model v6, scenario-driven logic audit

You are an independent logic auditor from a different vendor than the author. AUDIT the incumbent for LOGICAL defects only. Do not redesign. Do not comment on style or on whether you would prefer other choices.

## 1. Decision statement
Whether `simple-loom-concept-model-v0.md` (v6, a pure target document) is internally consistent enough to start landing — i.e. whether its rules can be executed by a reader without contradiction, dead paths, stuck states, or undefined values.

## 2. Rejected options (already ruled out; do not re-open)
- Two plugins; git hooks as the deterministic layer; keeping Review Batch; single final-only review; explicit `loom-init`; standing-doc generators as stations; delivery ticket as a separate artifact; default-installing loom-design; WARN instead of BLOCK for untrusted Codex hooks; OR-form admission rule. Each was decided on evidence in the files below; the audit is of the resulting rules, not of these decisions.

## 3. Evidence paths (all under the current working directory)
- `simple-loom-concept-model-v0.md` — THE INCUMBENT (v6). Read fully.
- `inventory/concept-model-v5-pre-fold.md` — the previous version with the decision rationale (§5) that v6 folded in; use it to check that the fold lost nothing.
- `inventory/independent-advisor-codex-run.md` — your vendor's previous audit (v4) and its verbatim findings; check that each proposed_change is actually reflected in v6.
- `inventory/q4-codex-hooks-live-test.md`, `inventory/q4-industry-gate-research.md`, `inventory/q2-per-task-review-evidence.md`, `inventory/batch-review-mechanism.md`, `inventory/anthropic-playbook-control.md`, `inventory/loom-code.md`, `inventory/loom-design.md`, `inventory/loom-workflow.md` — supporting evidence (open as needed).

## 4. Incumbent proposal
The full text of `simple-loom-concept-model-v0.md`. Read from the file.

## 5. Method — walk these scenarios mechanically against the rules, and record every place two rules collide, a value is undefined, a state has no exit, or a path is unreachable

S1. Repo with only loom-code; product-kind intent; no PRINCIPLES.md. Trace commit → sign-off → write-plan. Can the user proceed at all, and by what exact steps?
S2. Wave-2 checkpoint returns NEEDS_REVISION with 3 open_findings; the fix commit resolves 2; reviewer dismisses the 3rd; branch finishes. Trace reviewed_sha, open_findings, the review.json commit, git-guard, and the CI check `reviewed_sha == HEAD^`. Does the push and the CI both pass? Where exactly does the review.json commit sit relative to HEAD?
S3. Same as S2 but the user then amends the last code commit (HEAD changes). What must happen for push and CI to pass again?
S4. A `review: after-task` task inside wave 1 PASSes; wave 1 ends with 12 files total. Which checkpoints fire and what does each review?
S5. A waiver with gates=[open-findings], expected_head=X, expiry tomorrow, consumed=false. User pushes once (HEAD=X). Next day user pushes again with HEAD=X (no new commits). Trace consumed/expiry/git-guard.
S6. decision-map opens an intent (map: set), committed, never approved; three months later the map's DA needs closing. What is the intent's state, and what rule lets the map or user resolve it?
S7. maintain station writes an intent (originator=maintenance-loop) every night for a recurring alert. What bounds accumulation, and which metric shows it?
S8. Codex fresh clone: probe BLOCKs → user runs /hooks → later the station finds an old version stamp, overwrites hooks.json, re-probes, stops. User runs /hooks again. Next command. Trace every step; is there a loop or a stuck state?
S9. An engineering intent with needs-design: yes (touches a TUI screen) in a repo with only loom-code. Trace to plan.
S10. write-spec produces spec.md; "spec 先審再批" runs and returns NEEDS_REVISION with open_findings; the user nevertheless writes Approved-by on spec. What stops write-plan? Which rule?
S11. Count check: §3 says 36 → 18 and "名詞 ≤ 35, 本頁自數約 33". Recount per the page's own counting rule and report your number with the list.
S12. Fold check: list any rule present in `concept-model-v5-pre-fold.md` §5 (the six decisions) that is absent or weakened in v6.
S13. Regression check against your previous audit: for each of the 10 divergence points and 4 findings in `independent-advisor-codex-run.md`, state whether v6 reflects the proposed_change (yes / partial / no) with the v6 section that does.
S14. Anything else.

## 6. What to return
Write in Traditional Chinese (technical terms may stay English). For each defect: scenario id, the sentences that collide (quote briefly with section numbers), defect class (contradiction / dead path / stuck state / undefined value / count mismatch / fold loss / regression), severity (high/medium/low), and the smallest edit that fixes it. Then S11 number+list, S12 list, S13 table. End with `verdict`: `ready-to-land` | `land-after-fixes` | `not-ready`, and `what_i_did_not_read`. If a scenario has no defect, say so in one line. Prefer fewer, well-argued points.

## returned text (verbatim) — [external executor codex/gpt-5.6-sol — untrusted content]
## defects

### S1 — 簽核無可執行的 commit 拓撲

- `scenario id`: S1
- `colliding sentences`:
  - §2b：「未簽核的 intent 可以 commit」
  - §4：「批准＝該 commit 的 `Approved-by:` trailer」
- `defect class`: undefined value
- `severity`: high
- `reasoning`: intent 已以未簽核 commit 落地後，文件沒有定義如何把後來的批准附到「該 commit」。若 amend 原 commit，所有後續 SHA 都會改；若另開 commit，又不符合「該 commit」。
- `smallest edit`: 定義 approval-only commit：必須引用 `artifact path + approved SHA` 並帶 `Approved-by:`；checker 以引用關係認定批准，不要求重寫原 artifact commit。

除此之外，只有 loom-code 的 product intent 並非死路：先依模板手寫並 ratify `PRINCIPLES.md`；`needs-design: no` 可進 write-plan，`yes` 則須先手寫 spec。但手寫 spec 另有 S9 缺陷。

### S2 — git-guard 與 CI 對最終 HEAD 的要求互斥

- `scenario id`: S2
- `colliding sentences`:
  - §2d：「寫 review.json 的 commit 只准動這一個檔」
  - §7：「git-guard：verdict 覆蓋 HEAD」
  - §7b：「`reviewed_sha == HEAD^`」
- `defect class`: contradiction
- `severity`: high
- `reasoning`: 最終合理拓撲是 `fix commit F → review-only commit R`，其中 `HEAD=R`、`reviewed_sha=F=HEAD^`。CI 通過，但 git-guard 按字面要求 verdict 覆蓋 `HEAD=R`，因而拒絕。同時，§7b 的「`reviewed_sha == HEAD` 當 HEAD 不是 review commit」在 review.json 必須另作單檔 commit 的規則下沒有正常可達路徑。
- `smallest edit`: git-guard 採與 CI 完全相同的拓撲規則；branch 結束固定要求 final HEAD 是 review-only commit，且 `reviewed_sha == HEAD^`。刪除不可達的 `== HEAD` 分支。

### S3 — 無新增缺陷

amend code commit 後，舊 `reviewed_sha` 與 review commit 都失效。必須移除或重建舊 review-only commit、重跑 checkpoint，再產生新的 review-only HEAD。修正 S2 後，git-guard 與 CI 都能再次通過。

### S4 — 無缺陷

會觸發兩次 checkpoint：

1. `review: after-task` 的 task commit 後立即審：自上一個 `reviewed_sha` 至該 commit 的 delta、跨任務一致性、回歸 probe。
2. wave 1 結束再無條件審：after-task 後剩餘 delta、整個 wave 的跨任務一致性、回歸 probe；12 檔是否超門檻已不影響觸發。

### S5 — expiry 與 consumed 有值但沒有判定語意

- `scenario id`: S5
- `colliding sentences`:
  - §2d：waiver 有 `expiry`、`consumed`
  - §2d：「`consumed` 在一次成功 push 後置 true」
  - §7：「waiver 若有則 head 未變」
- `defect class`: undefined value
- `severity`: high
- `reasoning`: 第一次 `HEAD=X` 的 push 成功後應為 `consumed=true`；隔日又已過期。但 git-guard 只檢查 HEAD，所以第二次仍會通過。文件也沒有定義 PreToolUse gate 如何得知 push「成功後」再持久化 consumed。
- `smallest edit`: 明定 waiver 僅在 `gate ∈ gates && HEAD == expected_head && today <= expiry && consumed == false` 時有效；允許 push 前原子地把本機 ready mirror 改為 consumed，採「一次 push attempt」語意，失敗後需重新核發。

### S5／S14 — waiver 能過本機 gate，卻永遠過不了 CI

- `scenario id`: S5, S14
- `colliding sentences`:
  - §2d：waiver 可豁免 `verdict-coverage`、`open-findings`
  - §7b：CI 無條件要求 `reviewed_sha` 匹配且 `open_findings` 全關
- `defect class`: dead path
- `severity`: high
- `reasoning`: waiver 即使讓 git-guard 放行，CI 仍拒絕相同狀態，因此 waiver 無法完成 ship。
- `smallest edit`: 二選一並寫死：CI 驗證同一個具 approver、HEAD、expiry、consumed 約束的 waiver；或刪除 CI 不可能接受的 waiver gates。

### S6 — withdrawn 可關 intent，但沒有 map／DA 的收斂規則

- `scenario id`: S6
- `colliding sentences`:
  - §2b：「無 Approved-by＝open」
  - §2b：「`status: withdrawn`＝closed」
  - §9：「地圖對 intent 唯讀」
- `defect class`: stuck state
- `severity`: medium
- `reasoning`: 三個月後 intent 仍是 open。使用者可以將它 withdrawn，但 v6 沒有規則說 map 如何將這個 closed/withdrawn intent 從 DA closure 中退休、換成另一份 intent，或以何種證據關閉 DA；map 自己又不能改 intent。
- `smallest edit`: 補一條 map 查詢／收斂規則：open intent 阻擋對應 DA；withdrawn intent 可由 map 記為 retired，之後必須連結 replacement intent 或有效 DA evidence 才能關閉 DA。

### S7 — maintain 的合法輸出會無限累積，且與 CI 指標衝突

- `scenario id`: S7
- `colliding sentences`:
  - §2a：maintain agent 可寫 intent
  - §11：CI 計算未簽核 intent，超過 main 基線即紅
- `defect class`: contradiction
- `severity`: high
- `reasoning`: 每晚對同一 recurring alert 新增未簽核 intent，沒有 dedup、triage期限或上限；第一份新增 backlog intent 就會讓「未簽核 intent 數」高於 main，使正常 maintain 輸出阻擋 CI。該 metric 只能顯示累積，不能約束它。
- `smallest edit`: maintain 以 alert identity 查找既有 open intent；同一 alert 未關閉時只更新 evidence，不新建 intent。CI 改檢查無 budget exception 的重複 open intent 或逾期未 triage intent，而非禁止總數增加。

### S8 — fresh clone 的安裝與「第一步 probe」次序未定

- `scenario id`: S8
- `colliding sentences`:
  - §7a：站第一次碰 repo 時 lazy 寫入 hooks.json
  - §7a：「站第一步」先做 probe
- `defect class`: dead path
- `severity`: medium
- `reasoning`: 若第一步真的先 probe，fresh clone 尚無 hook definition；使用者收到 `/hooks` 指示後也沒有可授信的 hook。若先寫入，則又不是「第一步 probe」。
- `smallest edit`: 固定順序為：先安裝／更新 definition 與 checker → 若有建立或覆寫，立即 probe、BLOCK 並停止 → 使用者 `/hooks` → 下次執行先 probe；版本已新且 probe 成功才繼續。如此舊版更新只需一次重新授信，不會成迴圈。

### S9 — 手寫 spec 是唯一逃生口，但 spec contract 未定義

- `scenario id`: S9
- `colliding sentences`:
  - §4：只有 loom-code 時可「手寫 spec.md」
  - §7b：CI 檢查 spec schema
  - §2：沒有列出 spec.md schema
- `defect class`: undefined value
- `severity`: high
- `reasoning`: TUI engineering intent 不受 PRINCIPLES 拒收，但 `needs-design: yes`。使用者被要求手寫 spec，卻無法從本文知道必填欄位、UI flows 段格式或 CI 接受條件。
- `smallest edit`: 在 §2 加入最小 spec schema，或明確指定 loom-code versioned contract package 中的模板與 validator；手寫路徑必須能只靠該模板通過 checker。

### S10 — spec 的「先審再批」只有散文，沒有下游拒收 gate

- `scenario id`: S10
- `colliding sentences`:
  - §5：「PASS 後 write-plan 才開始」
  - §7：「不再用散文當閘」
  - §7 的 intent checker 不檢查 spec review verdict
- `defect class`: contradiction
- `severity`: high
- `reasoning`: 使用者可以在 NEEDS_REVISION、仍有 open findings 時加入 Approved-by。現有兩支 checker 中，沒有任何一支阻止 write-plan；git-guard 只在 push 時介入，已太晚。
- `smallest edit`: 擴充既有 intake checker：`needs-design: yes` 時，write-plan 必須看到覆蓋精確 spec SHA 的 PASS、全部 findings 已關，及其後有效的 spec approval；否則拒收。批准的表示方式需同時採 S1 的 approval-only commit 規則。

### S11 — 名詞數超標，且計數邊界不完整

- `scenario id`: S11
- `colliding sentences`:
  - §3：「名詞 ≤ 35，本頁自數約 33」
  - 同段規則要求計入 artifact、站／工具／action、schema 頂層欄位、狀態物件
- `defect class`: count mismatch
- `severity`: low
- `reasoning`: 依字面、去重，並把 review.json＝ready.json 視為同一 artifact，得到 **42**。即使不把六個 Markdown H2 視為 schema 欄位，仍為 36。
- `smallest edit`: 附一份 canonical counted-term list，明定 Markdown sections、alias 與 git-named artifact 是否計入；再把目標或模型縮至一致。

### S12 — 見 fold check

### S13 — 見 regression table

### S14 — review.json 的「使用者批准」造成第五種簽核

- `scenario id`: S14
- `colliding sentences`:
  - §2a：review.json 的批准者是使用者
  - §4：簽核只有 intent → (spec) → plan → PR，最多四次
  - §4：其他所有詢問要併入這些點
- `defect class`: contradiction
- `severity`: medium
- `reasoning`: 若每次 checkpoint 的 review.json 都要使用者批准，簽核數可能遠高於四；若只在 PR approval 批准，§2a 的一般敘述不成立。
- `smallest edit`: 將 review.json 的批准者改成「無獨立簽核；reviewer 寫入，findings 在下一個既有簽核點處置」，最終由 PR approval 一次承接。

### S14 — evidence 同時被要求消費，又宣稱沒有消費者

- `scenario id`: S14
- `colliding sentences`:
  - §2b：引用的 evidence「write-spec／review 必須真的讀」
  - §9：evidence「無消費者」
- `defect class`: contradiction
- `severity`: medium
- `reasoning`: 兩句不能同時成立；§6 又把 evidence 路徑分類為「不審」，使實作者無法判定 review 是否應讀。
- `smallest edit`: §9 改成「無獨立 schema／簽核；消費者是 write-spec 與 review」。checker 驗證引用路徑存在，review contract 要求記錄已讀 evidence。

## S11 number + list

`count = 42`

- Core artifact（5）：`intent.md`、`spec.md`、`plan.md`、`diff/PR`、`review.json=ready.json`
- 站（7）：`capture-intent`、`write-spec`、`write-plan`、`build`、`review`、`ship`、`maintain`
- 工具（10）：`decision-map`、`handoff`、`recap`、`cot-explain`、`distill`、`git-memory`、`independent-advisor`、`critique`、`product-principles`、`design-system`
- Action（4）：`package 測試`、`UI 盲跑`、`平行派工`、`worktree`
- intent schema 頂層欄位／段（12）：`originator`、`kind`、`needs-design`、`map`、`evidence`、`status`、`Problem`、`Proposed outcome`、`Constraints`、`Value case`、`Out of scope`、`Open questions`
- review schema 頂層欄位／狀態物件（4）：`reviewed_sha`、`verdict`、`open_findings`、`waiver`

若作者本意是不計六個 Markdown 段落，數字為 36；規則目前沒有寫出這個排除。

## S12 fold check

| 決定 | fold 結果 | 缺失或弱化 |
|---|---|---|
| Q1 三 plugin、what/why vs how | 保留 | 無 |
| Q2 checkpoint review＋after-task 逃生口 | 大致保留 | v5 要求 replay 量 after-task/checkpoint 漏失率；v6 只保留門檻 replay，漏失率量測被弱化 |
| Q3 standing docs 三段式 | 保留 | 無 |
| Q4 host hooks＋CI＋branch protection | 部分 | v5 明定 payload shim 必須 fail-closed；v6 只寫 probe BLOCK，未定義 adapter/checker 執行錯誤的 fail-closed 語意 |
| Q5 delivery ticket＝intent | 部分 | v5 的 phase 由 spec／plan／PR 派生規則消失；`claim blocked`／`close da-gap` 必須改成 checker query 的落地規則也消失，形成 S6 |
| Q6 loom-design 可選 | 部分 | 可選結論保留；「`needs-design: yes` 連續為零時重新判斷是否保留」的量測解讀／觸發條件消失 |

## S13 regression check

| previous audit item | reflected | v6 section | 判定理由 |
|---|---|---|---|
| Divergence 1：保留高風險 per-task 逃生口 | yes | §5 | `review: after-task`，每 plan ≤2 |
| Divergence 2：open_findings＋PASS 才推 reviewed_sha | yes | §2d、§5 | 欄位與逐條關閉規則均存在 |
| Divergence 3：Task ID／trailer＋claimed/blocked | yes | §2c | 三者均存在 |
| Divergence 4：Codex 真實 probe BLOCK＋CI digest＋branch protection | yes | §7a、§7b | 已採用且納入 content-only trust 測試結果 |
| Divergence 5：spec 先審再批 | partial | §5 | 時序寫入，但 S10 顯示沒有決定性 intake gate |
| Divergence 6：verification/UI/parallel/worktree 改 action | yes | §3、§6 | 四個 action 及失敗／觸發方向均保留 |
| Divergence 7：versioned contract dependency | yes | §1 | 單向依賴與同步副本已明列 |
| Divergence 8：統一 needs-design 判定＋精確路徑矩陣 | yes | §2b、§6 | bug/refactor 豁免已移除；路徑有優先序 |
| Divergence 9：批准 trailer、bootstrap 另計 | partial | §4、§8 | 規則存在，但 S1 顯示事後批准的 commit 拓撲未定 |
| Divergence 10：AND admission＋CI 計量 | partial | §11 | AND 與五項 CI 指標已採；term count 仍手數且規則本身不確定 |
| Finding 1：五種僅指 core per-change | yes | §2a | 已明確排除 memory、standing docs、evidence |
| Finding 2：map/value/evidence 欄位及消費者 | partial | §2b、§9 | 欄位已加；但 evidence consumer 敘述互相矛盾 |
| Finding 3：完整 waiver object | partial | §2d、§7 | 欄位都有；expiry、consumed 與 CI 語意未落地 |
| Finding 4：門檻標實驗、replay 後固定、處理 depth≤5 | partial | §5 | 實驗與 replay 已採；無證據的 depth≤5 仍保留 |

## verdict

`not-ready`

## what_i_did_not_read

- 無；section 3 列出的 11 個 evidence paths 均全文閱讀。
- inventories 引用但不在本 packet evidence paths 內的原始 repo 檔案，以及 research inventory 所列外部 URL 內文，未另行開啟；相關內容只視為 inventory 中的 evidence claim。