# slides-toolkit/docs — 實作經驗文件

[English](README.md) | [日本語](README.ja.md) | **繁體中文**

這個目錄收錄 slides-toolkit 開發過程中累積的**實證資料**與**外部邊界觀察**。和 `PRODUCT-SPEC.md` / `TECH-SPEC.md` 的差異：

- **PRODUCT-SPEC / TECH-SPEC** = 規格與設計決策（should-be）
- **本目錄 `docs/`** = 實測行為、踩雷紀錄、環境假設（as-is）

當 spec 與實作發生 drift 時，`docs/` 是還原當時「為什麼這樣設計」的歷史紀錄，以及「Google / gws 的邊界在哪裡」的 reference。

## 檔案索引

| 檔案 | 用途 | 讀者 |
|---|---|---|
| [`implementation-journal-2026-04-24.md`](implementation-journal-2026-04-24.md) | 首次 live E2E 測試完整流程日誌（kouko macOS arm64、`@gmail.com`）— 從 brew install gcloud 到真實 deck 產出 | 想理解 v0.5.0 為何這樣演化的人 |
| [`gws-cli-quirks.md`](gws-cli-quirks.md) | 實測發現的 gws CLI 真實行為與 spec drift — `--params` vs flag、cwd sandbox、scope 語法、URL 格式 | 寫 skill 時踩雷的人 / 新增 recipe 的人 |
| [`google-oauth-automation-limits.md`](google-oauth-automation-limits.md) | Google OAuth policy 的自動化邊界 — 為何 OAuth client / test user / consent screen 不能自動化、gws source code 層級證據 | 懷疑「真的沒辦法自動嗎」的人 |
| [`console-ui-reference.md`](console-ui-reference.md) | Google Cloud Console 2026-04 新 UI（Google Auth Platform）的導航對照 — Branding / Audience / Clients 路徑 | Console 迷路的人 |

## 寫入時機

以下情境應該更新 `docs/`：

- **首次或重大 live E2E 測試** → 更新 `implementation-journal-*`（按日期）
- **發現 gws CLI 與 spec 不符** → 更新 `gws-cli-quirks.md`
- **Google / upstream policy / API 邊界變動** → 更新 `google-oauth-automation-limits.md` 或 `console-ui-reference.md`
- **新 recipe 開發時踩到的坑** → 更新 `gws-cli-quirks.md`

## 不屬於這裡的內容

- Spec 級別的設計決策 → `PRODUCT-SPEC.md` / `TECH-SPEC.md`
- 版本歷程 → `CHANGELOG.md`
- 使用者操作指引 → `skills/google-slides-setup/protocols/gcp-console-walkthrough.md`
- Recipe 具體呼叫方式 → `skills/google-slides-api/protocols/recipe-*.md`

`docs/` 是歷史 + 外部邊界的資料庫，不是 how-to。
