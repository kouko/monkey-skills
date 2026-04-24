---
name: google-slides-builder
description: Execute slide-plan.json v1.2 against Google Slides backend — create blank deck, build slides with Google predefined layouts, insert text to placeholders, insert local images, emit deck URL. Use when user has a structured slide-plan (or equivalent) and asks to generate / 生成 / 匯出 / 做簡報 / create deck / google slides / プレゼン作成. MVP 僅支援 target=google-slides；html / pptx / marp 未實作。
---

# google-slides-builder

**Google Slides backend 的高層 orchestration**。讀 `slide-plan.json` v1.2，依序串接 **`google-slides-api` skill** 的 4 個 recipe（create-presentation → create-slides → insert-text → insert-image），外加 pre-flight validation，回傳 Drive URL。**不做設計判斷**（設計諮詢 → `slides-design`）、**不做首次設定**（auth / gws 安裝 → `google-slides-setup`）、**不做 template management**（v0.3 移除；見 PRODUCT-SPEC §3.2 Non-Goals 與 §3.5 Phase 2+ trigger）、**不做單一 API op recipe reference**（per-op 呼叫文件 → sibling skill `google-slides-api`）。

**Architectural layer split (v0.3.2)**：
- `google-slides-api` — 低層 recipes（per-op 呼叫 + placeholder_map 組裝 + error 對映）
- `google-slides-builder`（本 skill）— 高層 pipeline（`slide-plan.json` consumer + pre-flight + 4-recipe 串接 + 結果回傳）

本 skill 呼叫 `scripts/google-slides/gws-wrap.sh`（plugin root 下）包裝的 `gws` CLI；所有 shell script contract 與 exit code 對映見 TECH-SPEC §4.2。

## When to use

- 使用者已備 `slide-plan.json`（schema v1.2），頂層 `target == "google-slides"`
- 使用者貼來結構化資料（文字大綱 + 本機圖片路徑 + 每頁 `layout_hint`），要求自動合成 Google Slides
- 「跑 pipeline」「匯出 deck」「把這份計畫變成 Google Slides」

## When NOT to use

- **設計諮詢**（Minto / SCQA / chart-type / layout 選擇）→ `slides-design`
- **首次設定**（gws 未裝、OAuth 未配、Keychain / env 問題）→ `google-slides-setup`
- `target != "google-slides"`（html / pptx / marp 皆為 Phase 2+ trigger-gated，見 PRODUCT-SPEC §3.5）
- 任務超出 slides-toolkit 範圍（文案 → `copywriting-toolkit`；投資分析 → `investing-toolkit`）

## Prerequisites

- `google-slides-setup` 已跑完一次：
  - `~/.cache/slides-toolkit/bin/gws` 與 `jq` 已下載（HTTPS + `curl -f`；v0.3 不做 SHA-256 pin）
  - Google OAuth 已 grant（scopes：`presentations` + `drive.file`；見 TECH-SPEC §4.4）
  - `~/.config/gws/env.sh` 已補 issue #119 workaround（若偵測需要）
- macOS + Claude Code 執行環境；所有輸入檔 **UTF-8 only**

## Layout enum（slide-plan.json `layout_hint` 必填值）

每頁 `layout_hint` 必須屬於以下 7 個 Google Slides API `predefinedLayout` 值之一（TECH-SPEC §4.1）：

| enum | 用途 |
|---|---|
| `TITLE` | 封面 / 章節封 |
| `TITLE_AND_BODY` | 通用內頁（標題 + 條列內文） |
| `TITLE_AND_TWO_COLUMNS` | 雙欄對照 |
| `SECTION_HEADER` | 段落分隔頁（大標） |
| `MAIN_POINT` | 單一重點強調頁 |
| `BIG_NUMBER` | 大數字 KPI 頁 |
| `BLANK` | 空白（無預設 placeholder；自由排版） |

非此 7 值 → pre-flight exit 15。

## Input contract（slide-plan.json v1.2）

完整 schema 見 TECH-SPEC §4.1。必含頂層欄位：

| Field | Type | Required | Note |
|---|---|---|---|
| `version` | string | yes | 必為 `"1.2"` |
| `target` | string | yes | MVP 僅支援 `"google-slides"`；其他 → exit 12 |
| `output_title` | string | yes | 新 deck 檔名（UTF-8） |
| `dry_run` | bool | no (default `false`) | `true` → 只驗 schema / layout_hint enum / local image，不呼 API |
| `slides[]` | array | yes | 可為空（僅建空 deck）；每 slide 必含 `layout_hint`，可含 `replacements` + `images[]` |
| `slides[].slide_index` | int | yes | `>= 0` |
| `slides[].layout_hint` | string | **yes** | 屬 7 enum |
| `slides[].replacements` | object | no | `{"{{ROLE}}": value}`；ROLE 對映 layout placeholder（TITLE / SUBTITLE / BODY_N 等；見 `recipe-insert-text.md`） |
| `slides[].images[]` | array | no | 每 image 需 `placeholder_id`（layout placeholder role）+ `local_path`；`~` / 絕對 / cwd-relative 皆可 |

**v0.3 changes vs v1.1**：
- 刪除 `backend_config.template_ref`（template workflow 移除）
- `layout_hint` 從自由字串改為**必填 enum**
- `replacements` key 的 `{{ROLE}}` 對映改為 placeholder role（不再是 template 文字錨點）

## Workflow

按以下 4 步執行；任一步 fail，依 exit code 表回報並停止。

### Step 1 — Pre-flight check

Run `checklists/pre-flight.md`（10 項；每項 shell-runnable）。全通過才進 Step 2。關鍵驗證：
- jq: `.version == "1.2"`、`.target == "google-slides"`、每頁 `.layout_hint` 屬 7 enum
- `gws auth status` token 未過期（`credential-check.sh`）
- `scripts/google-slides/env-guard.sh check` 不回 exit 16（issue #119 workaround 在位）
- 所有 `slides[].images[].local_path` 存在 + 大小合格

### Step 2 — Recipe 1：create-presentation

`../google-slides-api/protocols/recipe-create-presentation.md`

- gws 命令：`gws slides presentations create --json '{"title":"<output_title>"}'`
- 輸入：`output_title`
- 輸出：新 deck 的 `presentationId` + `deck_url`
- 錯誤：403 / scope 缺 → exit 10；429 耗盡 → exit 11

### Step 3 — Recipe 2：create-slides

`../google-slides-api/protocols/recipe-create-slides.md`

- gws 命令：`gws slides presentations batchUpdate` 帶 `createSlide` requests（每頁一條，指定 `slideLayoutReference.predefinedLayout: <layout_hint>`）
- 輸入：上一步 `presentation_id` + `slides[].slide_index` + `slides[].layout_hint`
- 輸出：`placeholder_map`（`{slide_X: {ROLE: objectId}}`），由後續 `presentations.get` 補資料組成
- 錯誤：invalid layout enum → exit 15（pre-flight 已攔）；API fail → exit 12

### Step 4 — Recipe 3 + 4：insert-text + insert-image（per slide 需要時）

按 slide 需求各自執行；同一 slide 先 insert-text 後 insert-image：

**Recipe 3 — insert-text**（`../google-slides-api/protocols/recipe-insert-text.md`）：
- gws 命令：`gws slides presentations batchUpdate` 帶 `insertText` requests
- 輸入：`placeholder_map` + `slides[].replacements`
- key 剝殼 + upper-case → role → `placeholder_map[slide_X][role]` → `objectId`
- 錯誤：role 找不到 → **13a warning**（non-fatal）

**Recipe 4 — insert-image**（`../google-slides-api/protocols/recipe-insert-image.md`）：
- gws 流程：`drive.files.create` upload → `drive.permissions.create` (anyoneWithLink) → 取 `webContentLink` → `slides.presentations.batchUpdate` 帶 `createImage` + `pageElementProperties`（明確指定 pageObjectId + transform）
- 輸入：`placeholder_map` + `slides[].images[]`
- 錯誤：`placeholder_id` 在當前 slide 找不到 → **13b warning**（non-fatal）；upload 失敗 → exit 12；local 檔不存在 → exit 14

若 `slides[]` 為空 → 只做 Step 2，直接回 URL。

### Step 5 — Emit result

成功時 stdout 印單行 JSON：

```json
{
  "url": "https://docs.google.com/presentation/d/<presentation_id>/edit",
  "presentation_id": "<id>",
  "slides_count": N,
  "warnings": ["13a: slide_2 role=BODY_1 not found in layout"]
}
```

stderr 印人讀 progress + TaskUpdate 訊息（recipe 開始 / 結束、429 retry、warning 摘要）。

## Error handling（exit code 對映）

完整表見 TECH-SPEC §4.2；本 skill 常見：

| Exit | 意義 | 行動 |
|---|---|---|
| 10 | token expired / unauthenticated / scope 缺 | 回 `google-slides-setup` re-auth；user 跑 `gws auth login` |
| 11 | 429 rate limit 重試 5 次仍敗 | 稍後重試 |
| 12 | Google resource not found / `target` 不支援 / upload fail | 檢查 `target` 欄位 / Drive quota |
| 13a | insert-text 的 placeholder role 找不到 | **warning**；檢查 layout 是否提供此 role |
| 13b | insert-image 的 `placeholder_id` 找不到 | **warning**；檢查 `placeholder_map[slide_X]` |
| 14 | local image 檔案不存在 / 過大 / 格式不支援 | 檢查 `local_path` |
| 15 | schema validation failed（含 `layout_hint` 不在 enum） | 修 `slide-plan.json` |
| 16 | issue #119 / invalid_scope | 回 `google-slides-setup` 跑 `env-guard.sh apply` |
| 18 | Keychain + file backend 都 fail | 檢查 `KEYRING_BACKEND` |

**v0.3 removed exit codes**：
- ~~13c~~（`replaceAllShapesWithImage` 不命中）—— 本 skill 不再用此 API
- ~~13d~~（template schema drift）—— template workflow 移除
- ~~17~~（SHA-256 mismatch）—— bootstrap 不做 SHA pin（PRODUCT-SPEC v0.3 §3.2 Non-Goal）

**13a / 13b 為 warning**：pipeline 繼續走完、最後一併回報到 `warnings[]`；不 abort。

## Token expiry（passive）

依 TECH-SPEC §6.3 策略——**不**主動 refresh：

- Pre-flight 的 `credential-check.sh` 若回 `expires_in_sec < 0` → exit 10
- stderr 印：`Your gws refresh token has expired (Google External + Testing policy: 7-day lifetime). Please run: gws auth login then retry.`
- Claude 讀到 exit 10 → 自動路由到 `google-slides-setup` re-auth

**Because** 每週 3–5 份的使用頻率下，user 有節奏感；非必要時 auto-prompt 會打斷。

## Output contract

**stdout**（success 時單行 JSON）：

```json
{
  "url": "https://docs.google.com/presentation/d/<id>/edit",
  "presentation_id": "<id>",
  "slides_count": 12,
  "warnings": []
}
```

**stderr**：human-readable progress + TaskUpdate 事件（每 recipe 開始 / 結束、429 retry、13x warning 摘要）。

**exit code**：0 成功；非 0 依 §Error handling 表。

## 延伸參考

- TECH-SPEC §3.4（本 module 定義）、§4.1（schema v1.2）、§4.2（exit code）、§4.3（gws recipe 對映）、§4.4（OAuth scope）、§4.6（E2E data flow v0.3）
- PRODUCT-SPEC §4.2（3 核心 scenarios）、§4.4 Principle 2（Layout-based）、§3.5（Phase 2+ template-return trigger）
- 本 skill bundled files：
  - `checklists/pre-flight.md`
- Sibling skill（v0.3.2 架構拆分；recipes 移動到此）：
  - `../google-slides-api/SKILL.md`
  - `../google-slides-api/protocols/recipe-create-presentation.md`
  - `../google-slides-api/protocols/recipe-create-slides.md`
  - `../google-slides-api/protocols/recipe-insert-text.md`
  - `../google-slides-api/protocols/recipe-insert-image.md`
  - `../google-slides-api/references/api-error-codes.md`

---

> 🔄 CHECKPOINT: This artifact is raw output. Pipeline: consult your workflow for the next gate.
