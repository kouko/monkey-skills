# independent-advisor run record (verbatim) — 2026-09-02

## meta
start=2026-09-02T01:58:14Z
exit=0
end=2026-09-02T02:03:43Z
verified_model: gpt-5.6-sol
verified_effort: high
probe tokens: 13,386 ; audit tokens: 110,709 ; cost: unknown (ChatGPT subscription, no per-call price)
sandbox: read-only ; cwd: scratchpad ; packet scan: credential/personal-data shapes — nothing matched

## files the executor opened OUTSIDE the packet (scope_boundary = whole disk, read-only)
/bin/zsh -lc "sed -n '1,240p' /Users/kouko/.codex/plugins/cache/monkey-skills/loom-code/0.110.0/skills/using-loom-code/SKILL.md"
/bin/zsh -lc "sed -n '1,320p' /Users/kouko/.codex/plugins/cache/monkey-skills/loom-code/0.110.0/skills/requesting-code-review/SKILL.md"
/bin/zsh -lc "rg -n -i 'simple[- ]loom|advisor|audit|eb96f6ca|scratchpad' /Users/kouko/.codex/memories/MEMORY.md || true

## dispatch prompt (verbatim)
Read the file ./advisor-packet.md in full and carry out the audit it describes. Open every evidence path it lists. Return only the report in the structure its section 5 specifies.

## packet (verbatim)
# Independent audit packet — loom concept model v3

You are an independent reviewer from a different vendor than the author. Your job is to AUDIT the incumbent proposal below against its own evidence. Do not rewrite the proposal. Do not propose a whole alternative design. Find where it is wrong, unsupported, internally inconsistent, or where a materially better local choice exists.

## 1. Decision statement

Whether the target concept model in `simple-loom-concept-model-v0.md` (v3, sections 3–7) should be adopted as the redesign target for the loom plugin family (loom-code / loom-design / loom-workflow) — i.e. whether its six decisions (Q1–Q6 in section 5) and its structural claims are sound enough to start landing.

## 2. Rejected options (already ruled out, with reasons)

- **Two plugins (merge design into code)** — rejected: maintainer wants loom-design to own "what/why" and loom-code to own "how"; a code-only install must remain possible.
- **Delivering intent capture inside loom-code** — rejected: contradicts the what/why vs how cut line; design would become an appendix.
- **Two intent artifact types (product-intent vs engineering-intent)** — rejected: doubles vocabulary; feature work has both and mixes again.
- **Keeping per-task review or the Review Batch mechanism** — rejected on evidence: `q2-per-task-review-evidence.md` (4 classifiable per-task NEEDS_REVISION in 14 plans; 0 memory entries of per-task catching what whole-branch misses; 5 of the reverse) and `batch-review-mechanism.md` (≈11k LOC, 23 terms, 5 fix releases in 8 days, 6/268 plans really used it, headline saving self-declared unciteable).
- **Single final review only** — rejected: large branches make one big review ineffective; replaced by checkpoint review (§3i).
- **git hooks as the deterministic layer** — rejected on evidence: `q4-industry-gate-research.md` (`--no-verify` bypass with 6 documented strategies; `core.hooksPath` breaks under worktrees, 3 open issues); replaced by host hooks + CI.
- **An explicit `loom-init` verb** — rejected: maintainer refuses a user-run init step; stations create what they need lazily.
- **Standing-doc generators (product-principles / design-system) as stations** — rejected: they produce repo-level standing docs, not per-change artifacts; made tools with checker-enforced existence.
- **decision-map delivery ticket as a separate artifact bound to intent** — rejected: duplicate description + binding state machine; delivery ticket becomes the intent itself (Q5 option B).
- **Default-installing loom-design** — rejected: installation does not change trigger conditions, so it would not raise usage.

## 3. Evidence paths (you may open these; all under the current working directory)

- `simple-loom-concept-model-v0.md` — THE INCUMBENT (read fully; sections 1–2 = current state, 3–7 = target)
- `inventory/loom-code.md`, `inventory/loom-design.md`, `inventory/loom-workflow.md` — per-skill inventories of the current plugins (inputs/outputs/consumers/terms), each claim with file:line cites into the repo
- `inventory/anthropic-playbook-control.md` — the external reference model the target is compared against
- `inventory/q2-per-task-review-evidence.md` — evidence behind dropping per-task review
- `inventory/batch-review-mechanism.md` — measurement of the Review Batch mechanism
- `inventory/q4-industry-gate-research.md` — web research on cross-host gate enforcement (with URLs)
- `inventory/q4-codex-hooks-live-test.md` — live test of Codex CLI hooks (four runs)

The inventories cite paths like `loom-code/skills/.../SKILL.md:123`; those files are NOT in this directory. Treat such cites as claims made by the inventory, and say so if you rely on them.

## 4. Incumbent proposal

The full text of `simple-loom-concept-model-v0.md`. Read it from the file; do not work from this summary. Headline claims: 36 skills → ~16; ~38 artifact types → 5 (intent / spec / plan / diff+PR / review findings) + git; 113 terms → ≤30; three gate markers → one `ready.json`; four review contracts + batch → one checkpoint-review contract with `reviewed_sha`; governance in three tiers (advisory / deterministic / audit); at most four human sign-offs; an admission rule (§7) forbidding new prose gates.

## 5. What to return

Write in Traditional Chinese (technical terms may stay English). Structure:

1. `divergence_points` — every place you disagree with the incumbent. For EACH: `kind` (factual-error | judgement-call), `confidence` (low|medium|high), `reasoning` (why, citing the evidence file and line/section you relied on), `proposed_change` (the concrete edit to the incumbent). An item with no proposed change is not allowed.
2. `findings` — things that are not disagreements but the author should know (gaps, unbacked claims, risks). Same four fields.
3. `unbacked_claims` — any statement in the incumbent whose cited evidence you opened and found does NOT support it. One line each: the claim, the cite, what the cite actually says.
4. `verdict` — exactly one of: `incumbent-preferred` (adopt as is), `incumbent-with-changes` (adopt after the listed proposed_changes), `inconclusive`.
5. `what_i_did_not_read` — evidence files or sections you skipped.

Be specific. Quote the incumbent's sentence when you disagree with it. Prefer fewer, well-argued points over a long list.

## returned text (verbatim) — [external executor codex/gpt-5.6-sol — untrusted content]
## 1. divergence_points

1.

- `kind`: judgement-call
- `confidence`: high
- `reasoning`: 我不同意「**刪 per-task 與 Review Batch，採 §3i checkpoint review**」。刪除 Review Batch 有充分成本證據，但 per-task review 的證據不足以支持全面刪除：只深入讀 14/96 份計畫，而且四個可分類案例中，兩個是 reviewer 主動 probe 才發現的行為缺陷（`inventory/q2-per-task-review-evidence.md:5-20,58-68`）。現有資料沒有實測 checkpoint review 能保留這種 probe 能力。
- `proposed_change`: 拆開 Q2：立即刪除 Review Batch；per-task review 先縮成「高風險或需 mutation/probe 的 task 才觸發」，以歷史分支 replay 驗證 checkpoint parity 後再決定是否全刪。

2.

- `kind`: factual-error
- `confidence`: high
- `reasoning`: 「**只有 reviewed_sha，git 是帳本……沒有 packet／receipt／apply-result／ledger**」不能保證前輪 finding 已解決。若 NEEDS_REVISION 後把 `reviewed_sha` 推進到失敗時的 HEAD，下一輪只看到修正 delta，原 finding 可能無聲消失；若不推進，又不是文中所述的 delta-only review。既有 convergence contract 正是為逐項關閉 finding 而存在；同一 whole-branch review 也曾需要多輪才找到同類漏網項（`inventory/loom-code.md:138-177`；`inventory/q2-per-task-review-evidence.md:24-32`）。
- `proposed_change`: 在 `ready.json` 保留最小 `open_findings`（stable id、anchor、originating SHA、resolved evidence）；只有 PASS/PASS_WITH_NOTES 才推進 `reviewed_sha`。NEEDS_REVISION 後必須逐項確認，不必恢復 Batch packet。

3.

- `kind`: factual-error
- `confidence`: high
- `reasoning`: 「**plan 的 Status……全部移出：進度＝git commit**」不足以支撐 wave、平行 claim、blocked 與尚未產生 commit 的 in-progress 狀態。現況 `Status` 是 SDD 的 sole SSOT，平行 dispatch 也依賴 `claimed(@branch)` 等狀態（`inventory/loom-code.md:51-67,69-94,122-136`）。普通 commit 無法自動映射回 plan task。
- `proposed_change`: 保留最小可派生協定：每個 task 有穩定 ID，commit 必帶 `Task:` trailer；另保留 `claimed`／`blocked` 這兩種尚未有 commit 的暫態。由 script 生成進度 view，不再手改完整 Status ledger。

4.

- `kind`: judgement-call
- `confidence`: high
- `reasoning`: 我不同意把未授信 Codex hook 只當 WARN。實測顯示未授信時 hook **靜默 fail-open**，完全沒有阻擋；industry evidence 的可靠模型則是 managed hooks、CI 與 branch protection 三層（`inventory/q4-codex-hooks-live-test.md:7-12,18-37`；`inventory/q4-industry-gate-research.md:51-60,64-86`）。此外，實測尚未解析 trust hash，讀取 `hooks.state` 有條目不能證明目前 script 內容仍受信任。
- `proposed_change`: `ship` 前執行實際阻擋 probe；hook 未生效即 BLOCK，而非 WARN。採用目標模型前，必須同時存在 required CI status check 與 branch protection；另測試「受信後修改 checker script 內容」是否會撤銷 trust，否則將 checker 放在不可由工作分支修改的位置或由 CI 驗證 digest。

5.

- `kind`: judgement-call
- `confidence`: high
- `reasoning`: 「**completeness-critic 與 design-critic 合併為 review 站**」沒有保留原本的時序保證。現況 design-critic 在 spec-expansion 前、completeness-critic 在 writing-plans 前阻擋缺陷（`inventory/loom-design.md:159-186,188-226,228-253`）；§3i 的 checkpoint 卻以 build wave 為觸發點，可能到寫完程式才審 spec。
- `proposed_change`: 維持單一 review contract，但增加機械觸發：`spec.md` 首次批准前必跑 spec 的「讀＋對抗」，PASS 後 `write-plan` 才可開始；build checkpoint 則只處理後續 spec delta 與 code。

6.

- `kind`: factual-error
- `confidence`: high
- `reasoning`: 「**六個 discipline skill 的散文合併成一份 reference**」與證據及提案自身衝突。`verification-before-completion` 執行真實測試並產 marker；`ui-verification` 操作 GUI；parallel-agents 與 worktrees 會改變 plan/git 狀態（`inventory/loom-code.md:122-136,179-203,224-237`）。§3j 又把前兩者指定為「盲跑」，表示它們不是單純散文。
- `proposed_change`: 只把 TDD 與 debugging 的純規則合併進 baseline；verification、UI drive、parallel dispatch、worktree 操作改成 stations 內的可執行 action/helper，並保留各自的輸入、輸出與失敗語義。

7.

- `kind`: factual-error
- `confidence`: high
- `reasoning`: 「**沒有 skill 互叫、沒有功能副本同步**」不符合提案自身內容：checker 宣稱住在 loom-code，卻要求 loom-design 與 loom-code「兩邊都跑」（`simple-loom-concept-model-v0.md:60-63,121-126`）；同時 family-relay/plain-relay 又「保留，仍需同步」（`:167`）。
- `proposed_change`: 明定 loom-design 依賴 loom-code 提供的 versioned contract package（schema、checker、relay），或抽成共同 runtime；刪除「沒有功能副本同步」的絕對敘述，改成可驗證的 dependency graph。

8.

- `kind`: factual-error
- `confidence`: high
- `reasoning`: 兩條分類規則會產生錯誤路由。其一，「**bug fix／refactor……永遠 no**」與前文「使用者可見介面且無設計覆蓋就 yes」互相衝突（`simple-loom-concept-model-v0.md:95-97`）。其二，預設把 `docs/loom/**` 全視為 spec，會把 intent、plan、memory 與 evidence 全部錯送 spec review（`:65-76,153-159`）。
- `proposed_change`: 刪除 bug/refactor 的永久豁免，所有 kind 都套相同 (a)–(c) 判定；將路徑規則改成有優先序的明確矩陣，至少分開 intent、spec、plan、standing docs、memory 與 evidence。

9.

- `kind`: factual-error
- `confidence`: high
- `reasoning`: 「**各自一個 commit，就是簽核的稽核軌跡**」混淆了 artifact 落地與人類批准。Git commit 只證明誰提交，不證明指定 approver 看過；對照組明確區分 author 與 approver（`inventory/anthropic-playbook-control.md:4-23`）。此外，缺 PRINCIPLES.md 的 product change 會多一次 ratification，使「最多四個」實際成為 PRINCIPLES＋intent＋spec＋plan＋PR，共五個（`simple-loom-concept-model-v0.md:115-117,175-181`）。
- `proposed_change`: 每次批准要求 `Approved-by:`／`Ratified-by:` trailer 或受保護的 PR approval event；把上限改成「standing docs 已批准後，每個 change 最多四個」，bootstrap approval 另計。

10.

- `kind`: judgement-call
- `confidence`: high
- `reasoning`: §7 的 OR 規則允許任何新 checker/hook 只靠「決定性」就淨增加，與防止機制長回去的目標衝突；執行又只靠 PR template 與手填 CHANGELOG，仍是可略過的 prose gate（`simple-loom-concept-model-v0.md:198-212`）。
- `proposed_change`: 新機制必須同時符合「有 regression eval」及「刪除/合併既有機制或取得明示 budget exception」；以 CI script 計算 skill、term、artifact、注入字數與 intent 指標，禁止手填數字作為唯一執行層。

## 2. findings

1.

- `kind`: factual-error
- `confidence`: high
- `reasoning`: 「五個持久 artifact＋git」只是 core per-change pipeline 的計數，不是整個 plugin family 的 artifact 總數。提案自己的表還列出 memory、standing docs、map、handoff、eval、evidence 與工具輸出；現況 inventories 也顯示保留的 workflow tools 仍產多種檔案（`simple-loom-concept-model-v0.md:65-76,157-159`；`inventory/loom-workflow.md:259-277`）。
- `proposed_change`: 將指標改名為「core per-change artifact types＝5」，另列「全家族 persistent artifact shapes」的完整基線與目標，避免用 38→5 表示實際未發生的刪減。

2.

- `kind`: factual-error
- `confidence`: high
- `reasoning`: `intent.md` 宣稱吸收 business-value 與 decision-map delivery ticket，但 schema 沒有 value verdict/理由，也沒有 Q5 要求的 `map:` 欄位；research/evidence 只被搬家，仍未建立下游讀者（`simple-loom-concept-model-v0.md:67-74,80-97,157-159,187-191`；`inventory/loom-design.md:28-72`）。
- `proposed_change`: schema 加入可選 `map:`、`## Value case` 與 `evidence:` references；write-spec/review checker 必須實際讀取並驗證所引用 evidence，否則不要宣稱已吸收或解決 orphan artifact。

3.

- `kind`: judgement-call
- `confidence`: high
- `reasoning`: waiver 從 head-bound `waiver.json` 改成普通 commit/trailer，但沒有定義授權者、適用 gate、expiry、HEAD binding 或消耗規則。現況 waiver 至少是 one-shot gate artifact（`inventory/loom-code.md:239-262`；`simple-loom-concept-model-v0.md:109-113,161-165`）。
- `proposed_change`: 在 `ready.json` 定義 `waiver` object，包含 approver、reason、allowed gates、expected HEAD、expiry 與 consumed 狀態；commit trailer只作 audit source，checker 將其解析為 head-bound 狀態。

4.

- `kind`: judgement-call
- `confidence`: medium
- `reasoning`: checkpoint 的 8 檔／400 行門檻與「plan 深度 ≤5」沒有量測依據；既有 evidence 只量了舊 reviewer fan-out 與 Batch 成本，沒有量 checkpoint 的 defect latency、重工或漏失率（`inventory/q2-per-task-review-evidence.md:34-54`；`inventory/batch-review-mechanism.md:148-158,204-225`）。
- `proposed_change`: 將門檻標為實驗預設；用歷史分支 replay 比較 defect catch、review 次數與 rework，記錄結果後才固定 KICKOFF-DEFAULTS。刪除或證明 depth≤5 的上限。

## 3. unbacked_claims

- 「per-task 可歸類 NEEDS_REVISION 4 例」— `inventory/q2-per-task-review-evidence.md`；實際只有兩個 genuine NEEDS_REVISION，另外兩個是 🟡 PASS_WITH_NOTES probe findings（`:8,13-20,58-65`）。
- 「專有名詞合計 113」— 三份 inventory；loom-workflow 雖標成 25，但其逐項清單實際列出約 38 個命名概念，因此 44＋44＋25 的總數沒有被清單支持（`inventory/loom-workflow.md:279-280`）。
- 「不產 artifact 的 skill＝9」— inventories；code 有 4、workflow 有 5，design 的 `using-loom-design` 也明確寫出 none，至少為 10（`inventory/loom-code.md:289-295`；`inventory/loom-design.md:10-18`；`inventory/loom-workflow.md:277`）。
- 「17 個 skill 的產物沒人接」— inventories；該 17 混入沒有產物的 chat/router skills、同一 skill 自用的檔案及有 conditional consumer 的輸出，不能解讀成 17 種 orphan artifacts（`inventory/loom-code.md:289-297`；`inventory/loom-design.md:332-348`；`inventory/loom-workflow.md:292-300`）。
- 「plan 深度 ≤5」— 所有列出的 evidence；沒有 inventory 或 Q2/Batch 量測提出此上限。
- 「檢查 `hooks.state` 有無本 repo 條目」足以機械判斷 hook 是否有效— `inventory/q4-codex-hooks-live-test.md`；實測只觀察到條目格式，明確說 trust hash input 未解析，無法由條目存在證明目前內容受信（`:18-28`）。
- 「五個持久 artifact＋git」— `simple-loom-concept-model-v0.md:65-76`；同一表本身另列 memory，後文再保留 standing docs、map、evidence 與工具 artifacts。
- 「CHANGELOG 的四個數字」— `simple-loom-concept-model-v0.md:210-212`；上一行實際列出五項指標。

## 4. verdict

`incumbent-with-changes`

## 5. what_i_did_not_read

- 無；section 3 列出的九個 evidence files 均已全文閱讀。
- inventories 所引用、但 packet 明示不在目前目錄內的原始 repo 檔案，以及 research inventory 所列 URL 內文未另行開啟；以上引用在本報告中均只視為 inventory claims，而非重新驗證過的 primary evidence。