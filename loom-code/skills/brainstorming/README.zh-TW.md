# brainstorming

[English](README.md) | [日本語](README.ja.md) | **繁體中文**

> **HARD-GATE — 沒探索意圖前不准動工實作。** 用 5 軸探索框架（問題 / 使用者 / 最小終局 / 替代方案 / 什麼變多餘）帶 user / agent 走完，產出 `writing-plans` 消費的結構化 brief。對「這個很簡單」「我知道要做什麼」「先寫了再說」這類合理化 **拒絕**。

[loom-code](../..) plugin 的一部分。Agent 載入的是 [`SKILL.md`](SKILL.md)；本 README 是給人類看的。

## HARD-GATE 的意思

要跳過的壓力 —「這個很簡單」「我知道要做什麼」「先寫了再說」— 正是這個 skill 存在要擋的失敗模式。**前 5 分鐘的 brainstorming 省下後面做錯方向的 50 分鐘 + 重構出來的 500 分鐘。**

如果 user / agent 在 5 軸還沒走完前就動實作（起草 code、開檔、要 call `tdd-iron-law`），本 skill 拒絕並回到探索階段。

## 5 軸框架

5 個都要走。只有 §When NOT to Use 列舉的例外才能省略。

| 軸 | 提問 | 根據 |
|---|---|---|
| 1 — 問題 | 使用者請這個變更來做什麼工作？**不是他提的解法。** | Christensen (1997) JTBD, ISBN 978-0875845852 |
| 2 — 使用者 | 誰、在什麼條件下、用什麼現有工具與限制 | Klement (2018) job-story 形式, ISBN 978-1718626751 |
| 3 — 最小終局 | 解決問題的最小可出貨終局是什麼 | Axis 3 常常委派到 `dev-workflow:complexity-critique` |
| 4 — 替代方案 | 還有哪 2-3 種解法、為什麼被刷掉 | 強制把 trade-off 講白 |
| 5 — 什麼變多餘 | 這個變更會讓哪些既有 code / 流程變冗 — 並 **在同個 PR 刪掉** | YAGNI + same-PR cleanup 紀律 |

## Current State Evidence — recon 紀律（v0.7.0+）

當變更觸碰既有 code 或流程，brief 必須帶上 `## Current State Evidence` section：5 個 sub-bullets（Forward / Reverse / Error / Data / Boundary）+ Evidence paths appendix，每個 bullet 都附 `file:line` 引用。Agent 用 `grep` / `Read` / 派 `Explore` 自己填；recon 是 agent 的工作，不是使用者的。Greenfield 任務允許 `N/A — greenfield` 跳過。Schema 見 [`references/handoff-brief-format.md`](references/handoff-brief-format.md) §Current State Evidence。

## 產出

寫到 `docs/code-toolkit/specs/YYYY-MM-DD-<topic>.md` 的結構化 brief。Schema 在 [`references/handoff-brief-format.md`](references/handoff-brief-format.md)。`writing-plans`（Phase 2）會消費這個 brief 拆成原子任務。

## 不使用時機

[`SKILL.md`](SKILL.md) §When NOT to Use 內限定列舉的例外：

- 一行的已知 pattern fix（typo / version bump / 不變動行為的 documented config 值）
- 在既有 test coverage 下的純 refactor（rename / extract-method / 既有測試保持綠）
- 失敗測試已存在且可重現的 bug fix
- 使用者明確 override AND 已給出涵蓋 5 軸的 spec

不在這份清單上的工作就適用 HARD-GATE。

## Cross-skill 委派

- **`dev-workflow:complexity-critique`** — 任選；Axis 3 出現「變更看起來太大」訊號時。跑 3 題刪除優先 triage（最小終局 / 前後 LOC / 什麼變多餘）。
- **`dev-workflow:proposal-critique`** — 任選；Axis 4 出現 3 個以上真實 option 要做 KEEP / DEFER / DROP triage 時。
- **`writing-plans`**（Phase 2）— 下個階段。消費這個 brief。
- **`tdd-iron-law`** — `writing-plans` 跑完 + SDD 派 implementer subagent 開始實作時觸發。

## 這個 skill 不做的事

- 不寫 code。
- 不替使用者做最終決定。只攤開 5 軸；決定由使用者下。
- 不取代 `dev-workflow:complexity-critique`。complexity-critique 對特定提案做批評；brainstorming 對開放問題做探索。

## 參考

- [`SKILL.md`](SKILL.md) — 運作規格。
- [`references/visual-companion.md`](references/visual-companion.md) — 什麼時候畫圖（Mermaid sequence / C4 / ER 等）。
- [`references/handoff-brief-format.md`](references/handoff-brief-format.md) — `writing-plans` 消費用的輸出 schema。
- [`../using-loom-code/SKILL.md`](../using-loom-code/SKILL.md) — Router；本 skill 是 Stage 1（Discovery）。
- [`../tdd-iron-law/SKILL.md`](../tdd-iron-law/SKILL.md) — 探索結束後實作階段觸發。
