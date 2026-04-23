---
schema_version: 1
last_updated: 2026-04-23
owner: kouko
---

# Template Registry

此檔案記錄使用者在 Google Drive 自備的 Slides template，供 `google-slides-builder` 查找。`slide-plan.json` 的 `backend_config.template_ref` 以 `ref`（下表第一欄）為 lookup key，映射到對應 **Drive file ID**。

> **⚠️ Drive ID 屬個人資料，本檔案不入 public repo**。
> `.gitignore` / `settings.json` deny rule 的雙重防護僅覆蓋 `~/.config/gws/**`；本檔在 repo 內，若填入真實 Drive ID 切勿 commit 到 public branch。建議策略：(1) 保持本檔在 private fork / 本機 only；(2) 或在本檔旁放一份 `.local`（e.g. `registry.local.md`）並寫入 `.gitignore`，讓 public repo 版本只留骨架。

## Usage（builder 的 lookup 流程）

1. `slide-plan.json` 指定 `backend_config.template_ref: "client_pitch"`
2. builder 讀本檔，找 `ref == "client_pitch"` 列 → 取 `drive_id` 欄
3. 呼叫 `gws drive files copy --fileId=<drive_id>`
4. 得新 deck → 進 `recipe-replace-text` + `recipe-insert-image`

找不到 `ref` → builder exit 12，提示 user 在本檔新增一筆。

## Registry table

| ref | drive_id | schema_fingerprint | 用途 | notes |
|---|---|---|---|---|
| `client_proposal_v3` | `TODO: fill Drive ID` | `TODO: sha1:...` | 客戶提案 | 12 頁；placeholders `{{TITLE}} {{AGENDA}} {{SECTION_N}} {{BODY_N}} {{IMG_N}} {{CTA}}` |
| `weekly_report` | `TODO: fill Drive ID` | `TODO: sha1:...` | 每週工作週報 | 4 頁；`{{WEEK}} {{DATE}} {{PROGRESS_N}} {{NEXT_N}} {{IMG_CHART}}` |
| `tech_talk` | `TODO: fill Drive ID` | `TODO: sha1:...` | 對外技術分享 | 可變頁數；`{{TITLE}} {{SUBTITLE}} {{HEADLINE}} {{BODY_N}} {{CODE_N}} {{IMG_N}}` |

**欄位說明**：

| 欄 | 說明 |
|---|---|
| `ref` | slide-plan 中 `backend_config.template_ref` 指向的 slug；建議 `snake_case`，不含空白 |
| `drive_id` | Drive 檔案 ID（URL 中 `/d/<ID>/` 段） |
| `schema_fingerprint` | 可選；template placeholder 集合的 sha1 hash（OPEN-10 解；TECH-SPEC §4.7）。偵測 template 被改動時 warn 13d |
| 用途 | 人讀描述（哪種場景用） |
| notes | 頁數、placeholder 命名清單、其他備註 |

## How to add a new template

1. **在 Drive 建新 template**
   - 新建一份 Google Slides deck
   - 固定 layout / 字型 / 色系（不打算自動替換的部分）
   - 每張 slide 中要替換的文字位置，寫 `{{PLACEHOLDER_NAME}}`（`{{UPPER_CASE}}` 慣例）
   - 要放圖的位置，在 slide 畫一個 shape（例：矩形），在 shape 的 text 內填 `{{IMG_N}}`（例 `{{IMG_MAIN}}`、`{{IMG_CHART_1}}`）——`replaceAllShapesWithImage` 以此 text 為錨點

2. **取 Drive ID**
   - 打開 template URL：`https://docs.google.com/presentation/d/<ID>/edit#slide=...`
   - 複製 `/d/` 與 `/edit` 之間的段落 = Drive file ID

3. **在本表新增一列**
   - 新 `ref`（例 `q3_kickoff`）
   - 貼上 Drive ID 到 `drive_id`
   - `schema_fingerprint` 可留 `TODO:` 先空；首次 builder run 後可從 stderr 讀出 fingerprint 補回
   - `notes` 寫頁數 + placeholder 清單（方便日後記起用法）

4. **驗證（dry run）**
   - 組 minimal `slide-plan.json`：`{"version":"1.1","target":"google-slides","output_title":"test","backend_config":{"template_ref":"<new_ref>"},"dry_run":true,"slides":[]}`
   - 跑 `google-slides-builder` → 應回 `dry_run: true` 成功（驗證 registry lookup 通）

## Placeholder 命名慣例（強制）

- 全大寫 + 底線：`{{TITLE}}`、`{{BODY_1}}`、`{{IMG_MAIN}}`
- 編號用底線加數字：`{{BODY_1}} / {{BODY_2}} / {{BODY_3}}`（避免 `{{BODY1}} {{BODY_1}}` 混用）
- 圖片 placeholder 一律 `{{IMG_...}}` 前綴；避免和文字 key 碰撞
- **不**使用 Slides 原生 `<<mergefield>>` 語法（避免與 `replaceAllText` 衝突）

## 為何 Drive ID 不該公開

- Drive file ID 本身**不是**密碼，但搭配已取得 OAuth token 的任何人，可嘗試 `drive.files.get`、`drive.files.copy`
- 若 template 被惡意 copy / 散佈，你的設計 IP / 未公開資料（即使 template 中只有骨架）會外流
- Google 的 `drive.file` scope 限制是「本 app 建立 / 開啟的 file」，但一旦 ID 公開，任何人都可嘗試以自己的 OAuth 打開（`anyone with link` 權限若誤開就失守）
- **best practice**：Drive ID 只留本機 + private fork；public repo 僅保留 `TODO` 骨架

## TODO / Open

- 真實 template Drive ID 由 kouko 本機填入；本檔 commit 至 public repo 前確認僅 `TODO` 或已從 private fork 覆蓋
- `schema_fingerprint` 計算方式見 TECH-SPEC §9 OPEN-10；自動生成 helper 暫為 Phase 2 trigger（首次發現 template drift warning）
- Phase 2+ 若引入其他 backend（html / pptx / marp），其對應 registry 各自放於該 builder skill（本檔僅限 google-slides）
