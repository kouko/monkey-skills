# 2026-05-27 skill-mining advisory report

本次執行涵蓋 11 個軌跡（5 failure + 6 success），分布於 4 個目標技能，共產生 33 個 Memory Items。所觀察到的摩擦形態主要集中在兩個面向：**Brief 品質缺口**（brainstorming 技能在 Axis 走查之前或之後的結構性空白）以及 **技能管道銜接斷點**（finishing-a-development-branch 對上游 SDD 狀態的前提條件驗證不足）。success 軌跡則提供了明確的對策：平行工具呼叫、明確標記選項的提問、以及在寫檔之前先在對話內文提供摘要。

---

## Top anti-patterns

### 1. Brief 在關鍵決策點留下「未解決的設計問題」，迫使 writing-plans 階段發出阻塞式 AskUserQuestion

- **摩擦形狀**：brainstorming 技能的 Open Questions 區塊被設計用來記錄「無法自行確認的事實」，但實際執行中代理人常把「該選哪個選項」這類實作設計決策也放進 Open Questions，導致 writing-plans 無法展開，必須等用戶回應。
- **涉及 Items**：「Resolve implementation-design decisions during Axis 3/4, not as Open Questions for writing-plans」（session 3d998518, failure）、「Distinguish 'agent recommends' from 'agent decides' to prevent AskUserQuestion blocking」（session 269c265f, failure）。
- **影響技能**：`brainstorming/SKILL.md`（2 個 failure 軌跡）。
- **共同根因**：SKILL.md 對 Open Questions 的說明未明確區分「設計決策（屬於 Axis 3/4）」與「事實不確定性（才屬於 Open Questions）」，造成代理人把前者誤歸後者。

---

### 2. Current State Evidence 引用不可靠路徑：假設路徑存在、或引用 project memory 而非 repo 內檔案

- **摩擦形狀**：代理人在 Current State Evidence 環節引用了從未驗證存在性的路徑，或把 `~/.claude/projects/.../memory/` 下的記憶體檔案當成 codebase 的 `file:line` 來源，導致工具呼叫錯誤或日後無法重現。
- **涉及 Items**：「Verify codebase file paths with grep/find before citing in Current State Evidence」（session 854149d8, failure）、「Confine Current State Evidence recon to codebase files, not project memory」（session 854149d8, failure）、「Current State Evidence recon must verify SSOT ownership direction, not just file existence」（session 3d998518, failure）。
- **影響技能**：`brainstorming/SKILL.md`（3 個 failure Items 集中在同一症狀族群）。
- **共同根因**：SKILL.md 的 Current State Evidence 說明要求「grep/Read/Explore 填充」，但未明確要求：(a) 先驗證路徑存在、(b) 僅引用 repo 內路徑、(c) 追蹤 distribute.py 等分發腳本確認 SSOT 方向。

---

### 3. finishing-a-development-branch 在 SDD 尚未完成時即被觸發，導致對半成品執行收尾流程

- **摩擦形狀**：SKILL.md 沒有明確的「前提條件：SDD 所有 task 必須 DONE」檢查，也沒有在 SDD 最後一個 task 完成時提示用戶切換到收尾技能，造成技能在錯誤的時機點被啟用，或反之在 SDD 完成後長時間停留在等待狀態。
- **涉及 Items**：「Clarify that finishing-a-development-branch is a post-SDD gate, not a mid-pipeline phase」（session 06e68673, failure）、「Require explicit pipeline-readiness check before dispatching Step 1 code review」（session 06e68673, failure）、「Surface the branch-close handoff cue explicitly at SDD task-all-done boundary」（session 06e68673, failure）。
- **影響技能**：`finishing-a-development-branch/SKILL.md`（3 個相關 failure Items）。
- **共同根因**：SKILL.md 缺少 Step 0（管道就緒檢查）以及「SDD 上游在所有 task DONE 後主動發出 finishing 銜接提示」的跨技能合約。

---

### 4. Brief 缺乏用戶導向的決策摘要，用戶讀完長篇 brief 後仍需追問「我們到底決定做什麼」

- **摩擦形狀**：Brief 結構把 `## Decision` 放在多個 Axis 區塊之後，用戶在接收一份數百行的 brief 後無法立即定位核心決策，需要追問或重讀才能繼續行動。
- **涉及 Items**：「Open the brief with a one-paragraph plain-language decision summary」（session 854149d8, failure）、「Emit a brief orientation summary immediately after writing the brief file」（session 269c265f, failure）。
- **影響技能**：`brainstorming/SKILL.md`（2 個 failure Items，不同 session，症狀相同：brief 寫完後用戶需要二次確認）。
- **共同根因**：SKILL.md 的 Output Contract 規定了 brief 的結構，但沒有要求在 `Write` 之後立即在對話內文輸出一個簡短的決策摘要，也沒有要求 brief 以純文字摘要開頭。

---

### 5. Parallel worktree 分派時未告知實作者「worktree 從 main 分支，不繼承當前 branch HEAD」，導致下游 task 自行重做 cherry-pick

- **摩擦形狀**：SDD orchestrator 在平行分派 Task 2/3/4 時，沒有告知實作者必須 cherry-pick 前一個已完成 task 的 commit，實作者在 worktree 內自行發現並修復，增加了不必要的 latency 且留下重複 commit 紀錄。
- **涉及 Items**：「Parallel worktrees start from main HEAD, not parent session HEAD — acknowledge this before dispatch」（session 02523115, success）。
- **影響技能**：`subagent-driven-development/SKILL.md`（1 個 success Item 描述了繞過此摩擦的正確做法，暗示缺少明文指引）。
- **共同根因**：SKILL.md 目前對 worktree isolation 行為沒有說明，平行分派時未要求 orchestrator 主動提供 prerequisite commit SHA。

---

## Per-target SKILL.md modifications

### `code-toolkit/skills/brainstorming/SKILL.md`

本技能共有 18 個 Memory Items（8 failure + 10 success），修改集中在四個面向：(1) Open Questions 定義收窄、(2) Current State Evidence 來源限制、(3) Brief 決策可見性提升、(4) 成功模式的操作指引強化。

---

**修改一：Open Questions 定義收窄**

`## Output Contract — the brief` → `Optional but recommended sections` → `Open Questions`

```
### Open Questions

Open Questions capture facts the agent cannot determine from reconnaissance
(e.g., user's environment constraints, unstated preferences, external policy).

**Do NOT use Open Questions for implementation design choices.**
If you find yourself writing "Should we do X or Y?", resolve it in Axis 3
(decision paragraph) or Axis 4 (alternatives triage) instead.
writing-plans receives a fully-decided brief; unresolved design questions
produce blocking AskUserQuestion calls in that stage.
```

此修改根據 Items「Resolve implementation-design decisions during Axis 3/4, not as Open Questions for writing-plans」與「Distinguish 'agent recommends' from 'agent decides' to prevent AskUserQuestion blocking」，補足了代理人在 Open Questions 與 Axis 3/4 之間的邊界模糊問題。

---

**修改二：Current State Evidence 來源限制**

`## Output Contract — the brief` → `## Current State Evidence`

```
### Current State Evidence — constraints

1. **Verify paths before citing**: before reading any previously-known
   file path, run `ls` or `find` to confirm it exists — spec files and
   brief filenames change across PRs.

2. **Repo-only citations**: Evidence bullets must cite `file:line` paths
   within the project repo. Memory files (`~/.claude/projects/.../memory/`)
   are agent context, not valid codebase citations — do not cite them.

3. **Trace distribution direction**: for cross-plugin data flows, identify
   the write-origin (SSOT) vs read-only copy by reading any `distribute.py`
   or sync script in scope before declaring SSOT direction.
```

此修改整合 Items「Verify codebase file paths with grep/find before citing in Current State Evidence」、「Confine Current State Evidence recon to codebase files, not project memory」、「Current State Evidence recon must verify SSOT ownership direction, not just file existence」。

---

**修改三：Brief 開頭加入純文字決策摘要**

`## Output Contract — the brief` → minimum required sections 最頂部

```
### Lead with a plain-language decision summary (required)

Before the structured Axis sections, write a 3–5 sentence block covering:
- What we are building (the Axis 3 lock in one sentence)
- What is explicitly excluded
- What the immediately next step is (e.g., "proceed to writing-plans")

This is the first thing the user reads and must stand alone as the answer
to "what are we building and what are NOT we building?"
```

此修改根據 Item「Open the brief with a one-paragraph plain-language decision summary」，解決用戶讀完長篇 brief 後需追問核心決策的摩擦。

---

**修改四：Write 之後立即發出對話摘要**

`## Output Contract — the brief` → 最末尾新增

```
### Post-write orientation block (required)

Immediately after the `Write` tool call that creates the brief file,
emit a ≤10-line orientation block in the chat turn:
1. Axis 3 lock — one sentence
2. Top-3 eliminated alternatives — one-word reason each
3. What becomes obsolete
4. Handoff next step (e.g., "ready for writing-plans")

This replaces the pattern where the user must re-read the full brief
to locate the decision before they can continue.
```

此修改根據 Item「Emit a brief orientation summary immediately after writing the brief file」（session 269c265f，用戶在 brief 寫完 95 分鐘後回來才能繼續行動）。

---

**修改五：Axis 4 推薦做法「agent 提供建議 vs 用戶最終決定」釐清**

`## What this skill does NOT do`

```
- Does **not** force the user's choice — emits a `## My take` recommendation
  per §Axis 4 Anti-patterns, then lets the user accept, override, or ask back.
  (The user's right is to override the recommendation, not to be asked *before*
  the recommendation exists. AskUserQuestion without a prior recommendation
  transfers the decision burden; that is the anti-pattern to avoid.)
```

此修改根據 Item「Distinguish 'agent recommends' from 'agent decides' to prevent AskUserQuestion blocking」（session 269c265f，代理人因解讀「不做最終決定」而發出 AskUserQuestion，用戶 33 分鐘後才回應）。

---

### `code-toolkit/skills/finishing-a-development-branch/SKILL.md`

本技能共有 6 個 Memory Items（3 failure + 3 success），修改集中在：(1) SDD 完成前提條件的顯式檢查、(2) SDD 完成後的銜接提示合約。

---

**修改一：在 Default Flow 前加入 Step 0 管道就緒檢查**

`## Default flow — what happens if user just says 'finish this branch'` → Step 1 之前插入

```
### Step 0 — Pipeline readiness check (before anything else)

Check for an active SDD plan at `docs/code-toolkit/plans/<date>-<topic>-part-*.md`.
If any plan file contains tasks that are NOT yet marked DONE, surface:

  "SDD plan is still in progress — complete remaining tasks before closing
   the branch."
  STOP.

Only proceed to Step 1 when all SDD tasks across all active plan files
are confirmed DONE.
```

此修改根據 Items「Clarify that finishing-a-development-branch is a post-SDD gate, not a mid-pipeline phase」與「Require explicit pipeline-readiness check before dispatching Step 1 code review」。

---

**修改二：在 Cross-skill 合約表格加入 SDD → finishing 銜接提示**

`## Cross-skill contract — heavy delegation` → 合約表格加入一列

```
| SDD (upstream) | After all tasks DONE, SDD's final summary SHOULD include:
  "All tasks complete. Ready to invoke finishing-a-development-branch
   to close out this branch." |
```

此修改根據 Item「Surface the branch-close handoff cue explicitly at SDD task-all-done boundary」，解決 SDD 完成後分支停留在「done but not merged」狀態的摩擦。

---

**修改三：Default Flow 的 mandatory ASK 步驟加入「反問處理」**

`## Default flow` → step 6（顯示 commit message 請求批准）

```
If counter-question: resolve the question with a concrete counter-proposal,
then re-ask the binary (approve / override) in the same turn.
(Do not leave the step open-ended after a user follow-up question.)
```

此修改根據 Item「User counter-question in response to structured options triggers a full re-design round before finishing preconditions are met」，補足 AskUserQuestion 回應非二元選擇時的處理路徑。

---

### `code-toolkit/skills/subagent-driven-development/SKILL.md`

本技能共有 3 個 Memory Items（0 failure + 3 success），修改集中在平行 worktree 分派指引的補充。

---

**修改一：平行分派時告知 prerequisite commit SHA**

`## Process` → 平行 dispatch 段落後加入 callout

```
**Worktree isolation note**: `Agent(isolation: "worktree")` branches from
the repo's `main` HEAD, not from the orchestrator's current branch HEAD.
When dispatching parallel tasks that depend on a just-completed sequential
task, include the prerequisite commit SHA in each implementer prompt:

  "This worktree branches from main. Cherry-pick or rebase onto <SHA>
   (Task N's commit) before starting your implementation."

Failing to include this causes implementers to self-discover the missing
dependency and cherry-pick independently, adding latency and duplicate
commit entries to each worktree branch.
```

此修改根據 Item「Parallel worktrees start from main HEAD, not parent session HEAD — acknowledge this before dispatch」（session 02523115，Task 2/3 各自在 worktree 內重做 cherry-pick 才能編譯）。

---

**修改二：強調平行分派前的 Files-touched 不重疊確認**

`## Process` → 平行分派說明段落

```
Before emitting the parallel Agent dispatch message, explicitly verify
(from the plan's `Files touched` entries) that each parallel task's
file set is disjoint. Note: out-of-scope side-effect edits (files not
listed in any task's `Files touched`) remain a residual conflict risk
even after plan-level disjointness is confirmed — address them during
cherry-pick integration.
```

此修改根據 Item「Verify files-touched disjointness before parallel worktree dispatch to avoid integration conflicts」，正式化 orchestrator 在分派前閱讀並確認 Files touched 的做法（而非僅依賴 `Independent: true` 旗標）。

---

### `code-toolkit/skills/requesting-code-review/SKILL.md`

本技能共有 3 個 Memory Items（0 failure + 3 success），修改集中在 push trigger 語言覆蓋範圍與 reviewer 誤報防禦。

---

**修改一：Push-as-trigger 涵蓋非英文口語表達**

`## Push-as-trigger`

```
The trigger surface is **not limited to English or to precise CLI syntax**.
Any informal intent-to-publish message in any language counts as a trigger —
e.g. "先push", "先pushㄅ", "just push it", "推一下". When in doubt, treat
the message as a push-trigger and apply the gate.
```

此修改根據 Item「Intercept informal push commands as push-as-trigger regardless of phrasing」，確保非英文的口語推送請求也能被正確攔截。

---

**修改二：NEEDS_REVISION 發現前先驗證非誤報**

`## Process` → step 3 至 step 4 之間

```
Before surfacing a NEEDS_REVISION finding to the user, independently
verify it against the actual branch state:
- Run `ls` or `grep` to confirm the flagged file / symbol exists.
- If a finding looks like a false positive (e.g., "file doesn't exist"
  but the file was created in this branch), verify with `git ls-files`
  before escalating.
```

此修改根據 Item「Verify NEEDS_REVISION findings against source before escalating」，將 session 中觀察到的防禦性驗證步驟正式化。

---

## CLAUDE.md candidates

以下 2 條規則在 ≥2 個目標技能中重複出現，且具有跨技能適用性：

**候補 1**

```
Current State Evidence bullets must cite `file:line` paths within the
project repo. Memory files (`~/.claude/projects/.../memory/`) are agent
context, not citable codebase sources.
```

此規則在 `brainstorming`（2 個 failure Items）與 `subagent-driven-development`（1 個 success Item 驗證了一致的做法）中均有體現；它描述的是所有技能在蒐集 Evidence 時都應遵守的可重現性原則，而非特定技能的邏輯。

---

**候補 2**

```
When a commit message body must mention a destructive shell pattern
(e.g., `rm -rf`, `git checkout --`) as descriptive text, use
`git commit -F <tmpfile>` rather than an inline heredoc — the dcg hook
scans heredoc bodies for literal patterns regardless of context.
```

此規則來自 Item「Document dcg heredoc workaround for commit messages containing destructive-pattern literals」（session 269c265f，brainstorming target），但它的摩擦點在於 git commit 操作本身，與任何技能的語義無關；作為跨技能的 git workflow 守則最合適。

---

其餘 Items 未產生合格的 CLAUDE.md 候補：成功模式（平行工具呼叫、標記選項提問等）屬於特定技能的操作改善，不屬於需要專案層級強制執行的守則。

---

## New-skill candidates

目前無候補。所有觀察到的摩擦形態均已有對應的目標技能（`brainstorming`、`finishing-a-development-branch`、`subagent-driven-development`、`requesting-code-review`），且建議的修改都是對現有 SKILL.md 的補充，而非需要新技能來承接的空白領域。

---

## 數字摘要

- **分析軌跡數**：11（5 failure + 6 success）
- **Memory Items 總數**：33
- **目標技能分布**：
  - `brainstorming/SKILL.md`：18 Items（6 軌跡；4 failure + 2 success；最集中的修改目標）
  - `finishing-a-development-branch/SKILL.md`：9 Items（3 軌跡；2 failure + 1 success，但每條 failure 軌跡有 3 Items）
  - `subagent-driven-development/SKILL.md`：3 Items（1 軌跡；0 failure + 1 success）
  - `requesting-code-review/SKILL.md`：3 Items（1 軌跡；0 failure + 1 success）
- **CLAUDE.md 候補**：2 條
- **新技能候補**：0

---

## Action steps

1. **套用 brainstorming SKILL.md 修改（修改一至五）** （約 30 分鐘）

   優先處理：Open Questions 定義收窄（修改一）與 Current State Evidence 來源限制（修改二）是 failure 計數最高的兩個根因，且修改範圍明確，套用風險低。

   ```bash
   # 在 brainstorming/SKILL.md 內找到對應 anchor，手動套用以上 5 處修改
   grep -n "Open Questions\|Current State Evidence\|What this skill does NOT do\|Output Contract" \
     code-toolkit/skills/brainstorming/SKILL.md
   ```

2. **套用 finishing-a-development-branch SKILL.md 修改（修改一至三）** （約 20 分鐘）

   Step 0 管道就緒檢查（修改一）直接解決了本次最嚴重的跨技能銜接問題（3 個相關 failure Items）。建議與 brainstorming 修改在同一 PR 一起送審。

   ```bash
   grep -n "Default flow\|Cross-skill contract\|When NOT to use" \
     code-toolkit/skills/finishing-a-development-branch/SKILL.md
   ```

3. **套用 subagent-driven-development 與 requesting-code-review 修改** （約 15 分鐘）

   兩個技能各有 1–2 處修改，範圍小，可與上述修改合入同一 PR，或單獨作為小 commit。

   ```bash
   grep -n "Process\|Push-as-trigger\|parallel" \
     code-toolkit/skills/subagent-driven-development/SKILL.md \
     code-toolkit/skills/requesting-code-review/SKILL.md
   ```

4. **將 2 條 CLAUDE.md 候補加入專案 CLAUDE.md** （約 10 分鐘）

   確認兩條規則在現有 CLAUDE.md 中尚未有語義重疊條目，若無則直接追加至適當區段（Git 工作流守則、Evidence 蒐集守則）。

   ```bash
   grep -n "Current State\|commit.*heredoc\|dcg\|destructive" CLAUDE.md
   ```

5. **以本次修改後的 brainstorming 技能執行下一個 brainstorming session，作為 v0.5 dogfood** （約 1 個工作日後）

   驗證重點：Open Questions 是否不再含設計決策、Brief 是否以決策摘要開頭、post-write orientation block 是否出現。若 dogfood 顯示任何修改產生非預期副作用，可在下一輪 distill-sessions 中補足。
