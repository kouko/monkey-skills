# requesting-code-review

[English](README.md) | [日本語](README.ja.md) | **繁體中文**

> Branch 全體 / PR 全體審查 skill。與 `subagent-driven-development` 的 per-task reviewer 不同 — 本 skill 在 branch 工作 **結束** 時觸發、merge 之前，抓 per-task review 看不到的 **跨任務交互作用**。派 code-reviewer subagent 載入 loom-code 的 rubrics + checklists + standards（從 `domain-teams:code-team` byte-identical functional copy），產出嚴重度標籤的結構化審查。

[loom-code](../..) plugin 的一部分。Agent 載入的是 [`SKILL.md`](SKILL.md)；本 README 是給人類看的。

## Per-task vs 全 branch 審查

| | SDD per-task reviewer | 本 skill（whole-branch） |
|---|---|---|
| Scope | 1 個原子 ≤5 分鐘 task | main 比 branch 累積變更 |
| 觸發時機 | 每個 SDD task triad 中 | 全 SDD 工作 DONE 後、merge 前 |
| 抓什麼 | per-task 品質失誤 | 跨任務交互作用、scope creep、架構一致性 |

同 rubrics、不同 scope。兩層處理不同失敗模式 — 都不可互相取代。

## 使用時機

- 「審我這個 branch」/「看一下我的變更」/「可以 merge 嗎？」
- 「code review 一下」/「audit 這個 diff」/「feature X 做完，看看」
- `subagent-driven-development` 完成多任務 plan 後主動呼叫
- `finishing-a-development-branch` 在收尾流程 Step 1 自動呼叫

## 不使用時機

[`SKILL.md`](SKILL.md) §When NOT to Use：
- Trivial diff（1 行 typo / doc 改動 / version bump / 生成 code 重生）
- 已 review 過 branch 且無新變更
- 對既有 code 做 compliance audit（用 `domain-teams:code-team` 被動 gate — 用途不同）
- 使用者明確 override AND 變更屬於 trivial

## 輸出

每個 verdict 帶：

- **`standards_version`** stamp（從 `plugin.json` 的 `version` 欄）— 讓 downstream reader 知道這次 review 是哪一版 rubric 跑的（v0.7.0 reviewer-discipline R1）。
- 7 維度評分（security / architecture / correctness / naming / tests / refactoring / **cross-task-coherence** — branch 限定）。
- 嚴重度標籤 findings（🔴 fatal / 🟡 should-fix / 🟢 nit），每個 finding 都必須帶 `where:`（file:line 或 commit SHA range）。**缺 `where` 整個 verdict 自動翻成 `NEEDS_REVISION`**（v0.7.0 reviewer-discipline R2 — opaque finding 無法修）。
- ≤5 條 summary。

聚合規則（對齊 `rubrics/quality-gate.md` SSOT）：

- 任一 🔴 → `NEEDS_REVISION`
- 任一 finding 缺 `where` → `NEEDS_REVISION`（malformed）
- **2 個以上 🟡** → `NEEDS_REVISION`（warnings 累積 = 系統性問題）
- 恰好 1 個 🟡、無 🔴、全部帶 `where` → `PASS_WITH_NOTES`
- 無 🔴、無 🟡 → `PASS`

R1+R2 紀律的 canonical 在 `loom-code/scripts/_reviewer-discipline.md`，由 `distribute.py` 自動注入 3 個 reviewer agent。

## Cross-skill

- **被** `finishing-a-development-branch`（收尾流程 Step 1）呼叫
- **可選 escalate**：大規模 audit 給 `domain-teams:code-team`（>500 LOC、security 敏感、incident 驅動）
- **rubrics 載入自** `../subagent-driven-development/{rubrics,checklists,standards}/` — 與 per-task reviewer 同 SSOT、層間無 drift

## 這個 skill 不做的事

- 不改 code（只是 evaluator）
- 不取代 SDD per-task review
- 不跑測試（那是 `verification-before-completion` 的工作）
- 不觸發 CI（push 到 remote 才觸發；本 skill 在 push 之前跑）

## 參考

- [`SKILL.md`](SKILL.md) — 運作規格
- [`agents/code-reviewer-prompt.md`](agents/code-reviewer-prompt.md) — subagent 角色 prompt
- [`../subagent-driven-development/SKILL.md`](../subagent-driven-development/SKILL.md) — per-task reviewer（不同 scope，同 rubrics）
- [`../verification-before-completion/SKILL.md`](../verification-before-completion/SKILL.md) — 同層的 pre-merge gate（test-suite）
- [`../finishing-a-development-branch/SKILL.md`](../finishing-a-development-branch/SKILL.md) — orchestrator
- [`../using-loom-code/SKILL.md`](../using-loom-code/SKILL.md) — Router；本 skill 是 Stage 6（Review）
