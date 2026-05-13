# legal-document-draft

依台灣法源起草新法律文件（隱私權政策 / 服務條款 / DPA / NDA），結合公司 profile + 談判 playbook。

## 快速上手

1. 確保 repo 根 `legal-playbook/profile.yml` 存在（schema 見 `assets/profile-schema.yml`）
2. 視需要維護 `legal-playbook/<clause>.md` 給談判立場預設值
3. 透過 `using-legal-toolkit` router 請求「起草隱私權政策」「寫一份 NDA」等
4. skill 互動詢問當次需要的變數（產品名 / 個資類別 / SDK 清單 等）
5. 輸出寫到 `legal-outputs/<timestamp>-<mode>/`
   - `<doc-type>.md` — 可上線文件
   - `compliance.md` — 法務內部 review（checklist 判定 + TBD 遷移指南）

## 4 個 mode

| Mode | 文件 | 主要法源 |
|---|---|---|
| privacy | 隱私權政策 / 個資告知事項 | 個資法 §8, §9, §21, 施行細則 §22, §27 |
| tos | 服務條款 | 民法, 消保法 §11-1 + §17, 公平交易法 |
| dpa | 委託處理協議 | 個資法 §4 + §8, 施行細則 §12 |
| nda | 保密協議 | 民法 §227, §247-1, §250, 商業慣例 |

## TBD 遷移

PDPC 子法授權的項目（具體通報時限 / 通報門檻）以 TBD 形式留在 `compliance.md`。PDPC 子法發布後的 patch 步驟在 `references/tbd-migration-template.md`（通常是 `assets/template-*.md` + `checklists/compliance-*.md` 10 行內編輯）。

## 不在範圍內

- 起草 GDPR-style 文件（Path A 只處理台灣現行法；spec §3 + §13 詳述）
- 審閱既有文件 — 改用 `legal-contract-review`
- 自動監視 PDPC 子法發布 — 頻率低，手動 monitor 即可

## 相關

- `legal-contract-review` — 審閱對方提供的草案（NDA / SaaS / etc.）
- `legal-playbook-author` — 撰寫 draft 引用的談判立場
