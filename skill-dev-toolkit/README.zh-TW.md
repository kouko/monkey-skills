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

## 自足

每個 skill 內建 worth-it / 最小 skill 檢查,不委派給其他 plugin,因此**對其他 plugin
零 `plugin:skill` 引用**。(通用的程式碼變更 critique —— `complexity-critique` /
`proposal-critique` —— 與 session log 探勘 `distill-sessions` 留在 `dev-workflow`;
本工具組不依賴它們。)

## 授權

MIT —— 見 repo 根目錄 `LICENSE`。
