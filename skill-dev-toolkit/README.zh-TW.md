# skill-dev-toolkit

從頭到尾撰寫 Claude Agent Skill 的**自足**工具組。零跨 plugin 依賴 —— 單獨安裝即可運作。

於 2026-06-20 自 `dev-workflow` 抽出,讓 skill 撰寫的生命週期能獨立於 dev-workflow
的 session / git / critique 工具散布。

## Skills(生命週期)

| Skill | 角色 |
|---|---|
| `skill-creator-advance` | 建立新 skill、大幅重設計、評估驅動開發、優化 description 觸發。 |
| `skill-judge` | 以 8 維 rubric 評 skill 設計品質(0–120 + 等第)。 |
| `dogfood-skill-testing` | 對草稿 SKILL.md 做盲測行為驗證 —— 該觸發時會不會觸發、workflow 是否符合自己的 contract。 |
| `skill-refactor` | 保留輸出行為的 token / 結構重構。 |
| `skill-tuning` | skill 輸出品質 A/B —— 人類判定挑選變體。 |

典型流程:**建立** → **評分 / 行為測試** → **重構 / 輸出調校**。

## Package-resource 重構

當重構同時修改 `SKILL.md` 與 bundled resource 時，`skill-refactor` 會先保存
**不可變基準（immutable baseline）**，並在隔離的 candidate 中編輯。它的
**分層關卡（layered gates）** 依序檢查 resource、所屬 skill 與整個 package；要求時，
Claude 與 Codex 都必須提供可評定的 **雙主機證據（dual-host evidence）**。**整包淨會計
（package net accounting）** 會衡量完整 package，避免把搬動文字誤報成刪減。

## 自足

每個 skill 內建 worth-it / 最小 skill 檢查,不委派給其他 plugin,因此**對其他 plugin
零 `plugin:skill` 引用**。(通用的程式碼變更 critique —— `complexity-critique` /
`proposal-critique` —— 與 session log 探勘 `distill-sessions` 留在 `loom-workflow`;
本工具組不依賴它們。)

## 授權

MIT —— 見 repo 根目錄 `LICENSE`。
