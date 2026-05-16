# tdd-iron-law

[English](README.md) | [日本語](README.ja.md) | **繁體中文**

> **沒先寫一個會失敗的測試，就不准寫任何 production code。** 依據：Beck (2002) *Test-Driven Development: By Example* 序章＋第 1 章＋第 II 部，Addison-Wesley，ISBN 978-0321146533；Martin (2008) *Clean Code* 第 9 章 TDD 三法則，Prentice Hall，ISBN 978-0132350884；和田卓人 訳 (2017) 『テスト駆動開発』 オーム社 ISBN 978-4274217883。

[code-toolkit](../..) plugin 的一部分。Agent 載入的是 [`SKILL.md`](SKILL.md)；本 README 是給人類看的。

## 這個 skill 強制執行的規律

一條規律，三本一級書目同證：

- **Beck (2002) 序章**：*"Write the test you wish you had. Make it fail. Make it pass. Make it clean."*
- **Martin (2008) Clean Code 第 9 章「TDD 三法則」§1**：*"You may not write production code until you have written a failing unit test."*
- **和田卓人 訳 (2017) 訳者解説**：「テストは仕様の具体化であり、設計の feedback loop である」。

違反規律時，唯一正確的處置是：**刪掉那段 code，把測試補上，從頭再來。** 不是「之後再補測試」。刪除不是處罰，是還原違規時被切斷的 feedback loop。

## 使用時機

當 `using-code-toolkit` 偵測到實作工作（新功能 / bug fix / 重構 / migration）會自動觸發；`subagent-driven-development` 的 implementer subagent 內部也會自呼叫。

## 不使用時機

例外清單在 [`SKILL.md`](SKILL.md) §When NOT to Use 內限定列舉：

- 用完即丟的 spike code（同 session 內刪掉、不 commit、不再引用）
- 純由規格生成的程式碼（protobuf、ORM migration 等）
- 一行的 getter / setter / 單純委派
- 純設定檔（不含任何可執行邏輯）
- 使用者明確 override AND 工作屬於上述任一類

不在這份清單上的工作就適用 Iron Law。不准自行發明新的例外。

## 這個 skill 不做的事

- 不量測 coverage。Coverage 是落後指標，TDD 目標是 feedback loop。
- 不替使用者寫測試 — 它只強制「使用者 / agent 在 production code 之前先寫會失敗的測試」。
- 不取代 `verification-before-completion`（Phase 3）— 後者會再次檢查 diff 中的每個行為都對應 commit 歷史上的「失敗→成功」測試紀錄。

## 知識層

[`standards/tdd-standard.md`](standards/tdd-standard.md) 是 `domain-teams/skills/code-team/standards/tdd-standard.md` 的 byte-identical functional copy 加上 5 行 SSOT header。Drift 由 `code-toolkit/scripts/verify-drift.py` 監測。要修改規律，請在 `domain-teams:code-team` 側改 canonical，然後在同個 commit 跑 `code-toolkit/scripts/distribute.py`。

## 參考

- [`SKILL.md`](SKILL.md) — Agent 載入的運作規格（鐵律 + cycle + 例外清單 + Red Flags + false-green 診斷）。
- [`standards/tdd-standard.md`](standards/tdd-standard.md) — TDD 規律完整版（F.I.R.S.T、三法則、anti-patterns、JP anchor）。
- [`references/testing-anti-patterns.md`](references/testing-anti-patterns.md) — 附一級書目引用的 anti-pattern 索引。
- [`../using-code-toolkit/SKILL.md`](../using-code-toolkit/SKILL.md) — Router（這個 skill 在流程裡的位置）。
- [`../../scripts/canonical/README.md`](../../scripts/canonical/README.md) — SSOT 指標 + drift 政策。
