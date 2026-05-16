# subagent-driven-development

[English](README.md) | [日本語](README.ja.md) | **繁體中文**

> 把 >1 小時 或 跨多個 module 的工作切成 **≤5 分鐘的原子任務**，每個任務並行派出三個 subagent：**implementer**（worker，在 TDD 鐵律下實作）+ **spec-reviewer** + **code-quality-reviewer**（兩者皆 evaluator）。評分依據是 `domain-teams:code-team` 的 7 standards + 2 rubrics + 2 checklists 之 functional copy。

[code-toolkit](../..) plugin 的一部分。Agent 載入的是 [`SKILL.md`](SKILL.md)；本 README 是給人類看的。

## 觸發條件

`using-code-toolkit` 偵測到下列任一條件成立時自動 routing：

- 工作預估 **>1 小時**，或
- 工作觸及 **>1 個 module / >1 個檔案邊界**。

兩個 threshold 都沒到就直接走 `tdd-iron-law`。對一行修改派 3 個 subagent 是不划算的。

## 三角色

| Subagent | 角色 | 輸出 | 讀 | 寫 |
|---|---|---|---|---|
| `implementer` | worker | (status: DONE / DONE_WITH_CONCERNS / NEEDS_CONTEXT / BLOCKED) | task / spec / standards | code / 測試 / commit |
| `spec-reviewer` | evaluator | PASS / NEEDS_REVISION + gap list | artifact / spec / `checklists/spec-consistency.md` | 只產 verdict |
| `code-quality-reviewer` | evaluator | PASS / PASS_WITH_NOTES / NEEDS_REVISION + 六維度評分 + flags (🔴 / 🟡 / 🟢) | artifact / rubrics / checklist / 7 standards | 只產 verdict |

每個任務跑：implementer 一輪 + reviewer 並行一輪。Reviewer 守備範圍故意不重疊：spec-reviewer 不評品質，code-quality-reviewer 不評 spec 涵蓋度。混在一起會把 orchestrator 的解決演算法搞壞。

## Phase 1 acceptance test

4-task plan → SDD 派出 **12 個 subagent**（4 × 3），收回 12 個 verdict。每個任務最多 3 輪 re-dispatch 內收斂到 DONE。Phase 1 在 `tests/skill-triggering/prompts/` 驗證這個流程。

## 知識層（functional copy）

本 skill 下的 `standards/`、`rubrics/`、`checklists/` 所有檔案都是 `domain-teams/skills/code-team/{standards,rubrics,checklists}/` 的 byte-identical functional copy 加 5 行 SSOT header。要修改規律：

1. 編輯 `domain-teams:code-team` 側的 canonical。
2. 同 commit 跑 `python3 code-toolkit/scripts/distribute.py`。
3. CI 跑 `code-toolkit/scripts/verify-drift.py` 強制 byte-identical。

## 這個 skill 不做的事

- 不寫 code — 派 implementer 去寫。
- 不產 verdict — 派 reviewer 去評。
- 不決定要不要用 SDD — `using-code-toolkit` 負責 routing。
- 不產 plan — `writing-plans`（Phase 2；之前用 inline plan）負責。
- 不收尾 — `finishing-a-development-branch`（Phase 3）關 branch 並 delegate 到 `dev-workflow:git-memory`。

## 參考

- [`SKILL.md`](SKILL.md) — Orchestration 規格。
- [`agents/implementer-prompt.md`](agents/implementer-prompt.md) / [`agents/spec-reviewer-prompt.md`](agents/spec-reviewer-prompt.md) / [`agents/code-quality-reviewer-prompt.md`](agents/code-quality-reviewer-prompt.md) — 角色 prompt。
- [`../tdd-iron-law/SKILL.md`](../tdd-iron-law/SKILL.md) — Implementer 必須遵守的鐵律。
- [`../using-code-toolkit/SKILL.md`](../using-code-toolkit/SKILL.md) — Router；SDD 觸發規則。
- [`../../scripts/canonical/README.md`](../../scripts/canonical/README.md) — SSOT 指標 + drift 政策。
