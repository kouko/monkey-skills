# verification-before-completion

[English](README.md) | [日本語](README.ja.md) | **繁體中文**

> **HARD-GATE — 沒跑套件層級測試前不准宣告「DONE」。** P3-B 規定。執行正規套件層級測試指令（`npm test` / `pytest` / `go test ./...` / `cargo test` 等），對沒有執行證據的 "done" 主張拒絕。抓的失敗模式：測試交互 bug（A + B 一起就 fail）、orphan 測試（存在但不在預設 suite）、lint pass 但測試 fail、手動測試不是驗證。

[loom-code](../..) plugin 的一部分。Agent 載入的是 [`SKILL.md`](SKILL.md)；本 README 是給人類看的。

## 套件層級執行才抓得到的 3 種失敗

1. **測試交互 bug** — Test A 單獨 PASS、B 單獨 PASS、A+B 一起 FAIL（共享可變狀態、fixture 洩漏、port 衝突）
2. **Orphan 測試** — 測試 file 存在、有 assertion，但根本沒被執行（`tests/` glob 漏掉、副檔名錯、config 排除）。作者以為有 coverage，實際是個洞
3. **Lint ≠ tests** — TypeScript 編譯過 + ESLint 過 + runtime null-deref。靜態分析跟測試執行正交

## 使用時機

- 任何要宣告 feature / task / branch "done" 前
- `subagent-driven-development` 在 task 結尾自動呼叫（快 suite 才會這樣，看 orchestrator）
- `finishing-a-development-branch` 收尾流程 Step 2 **強制** 呼叫

## 不使用時機

[`SKILL.md`](SKILL.md) §When NOT to Use：
- 還沒有測試（全新 repo、這次 commit 才加第一個測試）
- 純 doc / config / 重新生成的 code（無 runtime 行為改變）
- 測試基礎設施壞掉（runner crash，不是 test failure）
- 使用者明確 override AND 變更屬於 exempt 類別

## 包什麼

- [`SKILL.md`](SKILL.md) — HARD-GATE 措辭、免責清單、4 步流程、拒絕 8 種 Red Flags
- [`references/test-invocation-by-stack.md`](references/test-invocation-by-stack.md) — 各語言/build tool 的正規指令（20+ stacks）；monorepo 處理；各 runner 的「0 tests ran」偵測；慢 suite 處置

## Cross-skill 契約

- **被** `subagent-driven-development`（可選、每個 task 結尾）+ `finishing-a-development-branch`（必填 Step 2）呼叫
- **失敗時 route**：`tdd-iron-law`（明顯的失敗 → 寫 RED 修）/ `systematic-debugging`（不明顯的失敗 → 4-phase REPRODUCE）
- **不取代 CI** — CI 在 push 之後跑；本 skill 在 push 之前跑，讓 push 帶乾淨的 diff

## 這個 skill 不做的事

- 不寫測試（`tdd-iron-law` 的工作）
- 不評 code 品質（`requesting-code-review` / SDD reviewers）
- 不決定該有哪些測試 — suite 是 suite，本 skill 只驗「跑得起來 + 都過」

## 參考

- [`SKILL.md`](SKILL.md) — 運作規格
- [`references/test-invocation-by-stack.md`](references/test-invocation-by-stack.md) — 指令對照表
- [`../tdd-iron-law/SKILL.md`](../tdd-iron-law/SKILL.md) — 寫測試的規律
- [`../requesting-code-review/SKILL.md`](../requesting-code-review/SKILL.md) — 同層 pre-merge gate（人類審查）
- [`../systematic-debugging/SKILL.md`](../systematic-debugging/SKILL.md) — 失敗不明顯時
- [`../finishing-a-development-branch/SKILL.md`](../finishing-a-development-branch/SKILL.md) — orchestrator
- [`../using-loom-code/SKILL.md`](../using-loom-code/SKILL.md) — Router；本 skill 是 Stage 7（Verification）
