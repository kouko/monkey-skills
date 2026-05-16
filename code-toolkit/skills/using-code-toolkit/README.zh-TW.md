# using-code-toolkit

[English](README.md) | [日本語](README.ja.md) | **繁體中文**

> code-toolkit 的 router 與框架章程。透過 plugin 的 SessionStart hook 自動注入到每一個 Claude Code / Codex CLI session，確保 agent 在動筆寫 code 之前就知道規則。

[code-toolkit](../..) plugin 的一部分。Agent 載入的是 [`SKILL.md`](SKILL.md)；本 README 是給人類判斷是否安裝、怎麼用的文件。

## 為什麼需要 router

`code-toolkit` 提供 Superpowers 風格的流程層（brainstorm → plan → SDD → TDD iron-law → debugging → code-review → finish-branch），加上一個與 `domain-teams:code-team` standards byte-identical 的知識層 functional copy。沒有 router 的話，agent 每次都得自己判斷在哪個階段要載入哪個 skill、引用哪本一級書目（Beck / Martin / Fowler / OWASP / 徳丸本）。Router 把這個決策統一掉。

走 SessionStart hook 注入 router，是為了避免使用者忘記主動呼叫；Phase 1.5 會加 `CODE_TOOLKIT_MODE=off` 環境變數，讓已裝 `obra/superpowers` 的使用者選擇關掉本 plugin 的 hook。

## 路由目標

| 階段 | Skill | v0.1.0 狀態 |
|---|---|---|
| 探索 | [`brainstorming`](../brainstorming) | ✅ 已 ship |
| 計畫 | [`writing-plans`](../writing-plans) | ✅ 已 ship |
| 執行 | [`subagent-driven-development`](../subagent-driven-development) | ✅ 已 ship |
| 紀律 | [`tdd-iron-law`](../tdd-iron-law) | ✅ 已 ship |
| 修復 | [`systematic-debugging`](../systematic-debugging) | ✅ 已 ship |
| 審查 | [`requesting-code-review`](../requesting-code-review) | ✅ 已 ship |
| 驗收 | [`verification-before-completion`](../verification-before-completion) | ✅ 已 ship |
| 收尾 | [`finishing-a-development-branch`](../finishing-a-development-branch) | ✅ 已 ship |
| 輔助 | [`using-git-worktrees`](../using-git-worktrees) | ✅ 已 ship（lateral 工具，不在線性流程中） |

## 使用時機

- 任何寫程式相關工作 — 新功能 / bug fix / 重構 / migration / 依賴升級 / review。
- 觸發詞（多語）：「加個功能 / 重構 / 修 bug / 機能を追加 / リファクタ / バグを直して / add a feature / refactor / fix this bug」。

## 不使用時機

- 純讀取性問題（「這個 function 在做什麼？」）— Router 不寫不審，直接回答即可。
- 對已交付產出做合規評分審查 — 用 `domain-teams:code-team`（被動 gate 入口）。
- 寫 / 重構 *skill* 本身（不是 application code）— 用 `dev-workflow:skill-creator-advance` / `skill-refactor`。

## 並存契約

- **`domain-teams:code-team`** — 保留為審查用的被動 gate 入口。本 toolkit 的知識層是它的 functional copy，`scripts/verify-drift.py` 監測 drift。
- **`dev-workflow:{git-memory, complexity-critique, proposal-critique}`** — 在對應節點 delegate 過去（不重新實作）。
- **`obra/superpowers`** — Skill 名稱與 SessionStart hook 重疊。要關掉 code-toolkit 的 hook 注入：`export CODE_TOOLKIT_MODE=off`。

## 參考

- [`SKILL.md`](SKILL.md) — Agent 載入的運作規格。
- [`../../PRODUCT-SPEC.md`](../../PRODUCT-SPEC.md) — 商業 / 使用者 / Q-lock。
- [`../../TECH-SPEC.md`](../../TECH-SPEC.md) — 架構 / hooks / SSOT。
- [`../../ROADMAP.md`](../../ROADMAP.md) — Phase 計畫 / Decision Ledger。
