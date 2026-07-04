# dispatching-parallel-agents

[English](README.md) | [日本語](README.ja.md) | **繁體中文**

> **每個獨立的問題領域派一個 agent — 讓它們並行工作。** 預設是循序執行；並行 dispatch 是例外，必須用誠實的獨立性檢查（檔案不相交、symbol 不相交、無資料依賴）來正當化。原型：superpowers v5.1.0 `dispatching-parallel-agents`，依 loom-code 的 TDD iron-law + verdict 集約改編。

[loom-code](../..) plugin 的一部分。Agent 載入的是 [`SKILL.md`](SKILL.md)；本 README 是給人類看的。

## 這個 skill 做的事

當工作是 **2 個以上互相獨立的問題領域** — 修不相干的失敗測試檔、審查不相干的模組、抓取不相交輸入的資料 — 循序 dispatch 會浪費 wall-clock 時間。這個 skill 是 **across-domain dispatch 層**：辨識真正獨立的領域、為每個領域組一份自包含的 prompt、把所有 `Agent` 呼叫放在 **同一則 assistant message 裡** dispatch（harness 只在同一則訊息內才會並行執行），最後集約所有 verdict、一個都不能漏。

## 使用時機

- 3 個以上的測試檔因 **互不相關** 的原因失敗 — 每檔一個 implementer。
- 跨多個模組的 security audit — 每模組一個 reviewer。
- N 檔股票 / N 個地區 / N 條 feed 的資料抓取 — 每個輸入一個 data agent。
- `writing-plans` 標了 `independent: true` 的任務 **且** `files touched` 集合不相交 — 兩條件缺一不可；標記只是 plan 作者的主張，不是保證。

領域要稱得上獨立，必須全部成立：沒有共享檔案（或該檔在所有分支都是唯讀）、沒有任何分支會 rename / 移除 / re-export 的共享 symbol、沒有循序資料依賴。如果無法對每個領域用一句話說清楚它為何獨立，這工作就不獨立。

## 不使用時機

見 [`SKILL.md`](SKILL.md) §When to use vs. when NOT to：

- 任務共享檔案或 symbol — merge conflict + 非決定性狀態；改循序，或先把檔案拆開。
- 循序資料依賴（B 需要 A 的輸出）— 定義上就不是並行。
- 失敗可能共享同一個根因 / 根因未知 — 先派一個 agent 調查；拆散調查會把共同根因藏起來。
- 單一領域、複雜但內聚 — 派一個專注的 subagent，不是 N 個碎片。
- 兩個 reviewer 看同一個 artifact — `subagent-driven-development` 在任務層已經做了；不要重複包一層。

## 與 subagent-driven-development 的關係

SDD 的 implementer / reviewer 三員是 **單一領域內、以任務為單位**；這個 skill 是 **across-task / across-domain** 的互補層。並行 dispatch 不豁免任何規律：每條分支仍遵守 `tdd-iron-law`（先寫會失敗的測試 —「又小又並行」是合理化組合拳，一律拒絕），且 `verification-before-completion` 在 **整合點只跑一次** package 級測試套件、不是每分支各跑一次 — 各分支的套件單獨都會過，合併後的 diff 仍可能失敗。

## 兩種模式

- **Mode (a)** — 一個 orchestrator 在單一訊息裡展開 subagents；它們共享同一份 checkout，結果集約回該 orchestrator。skill 主體就是這個。
- **Mode (b)** — 多個獨立 session 同時在同一個 repo 上工作。Harness 不會跨 session 協調，所以需要明確規約：每個 agent 一個 worktree（見 [`../using-git-worktrees/SKILL.md`](../using-git-worktrees/SKILL.md)）+ 事前靜態切分不相交的 plan 任務 + 用 plan 的 `Status` 欄位當共享台帳 + 每個 agent 各開一個 PR。**承重的陷阱：** worktree 只隔離檔案，**不能** 防止重疊編輯的衝突 — 真正的防撞是 `files touched` 的不相交切分。實務上限：同時 ~3–5 個 agent。

## 這個 skill 不做的事

- **不** 取代 `subagent-driven-development` — SDD 仍是每個領域內以任務為單位的引擎。
- **不** 允許多個 implementer 並行寫同一批檔案 — 檔案衝突是禁止的，「git 會自己搞定」一律拒絕。
- **不** 讓任何分支豁免 `tdd-iron-law`。
- 在 router 裡 **沒有** Skill Priority 位置 — 輔助型 skill，隨需取用。

## 參考

- [`SKILL.md`](SKILL.md) — Agent 載入的運作規格（獨立性判準 + dispatch 模式 + 集約規則 + mode (b) + Red Flags）。
- [`../writing-plans/SKILL.md`](../writing-plans/SKILL.md) — 上游；產出這個 skill 消費的 `independent: true` atomic tasks。
- [`../subagent-driven-development/SKILL.md`](../subagent-driven-development/SKILL.md) — 橫向；單一領域內的任務級三員組。
- [`../verification-before-completion/SKILL.md`](../verification-before-completion/SKILL.md) — 下游；整合點只跑一次。
- [`../using-git-worktrees/SKILL.md`](../using-git-worktrees/SKILL.md) — mode (b) 並行 session 的必要條件。
