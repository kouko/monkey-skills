---
name: google-slides-builder
description: Execute slide-plan.json v1.1 against Google Slides backend — copy template from Drive registry, replaceAllText, insert local images, emit deck URL. Use when user has a structured slide-plan (or equivalent) and asks to generate / 生成 / 匯出 / 做簡報 / create deck / google slides / プレゼン作成. MVP 僅支援 target=google-slides；html / pptx / marp 未實作。
---

# google-slides-builder

**Google Slides backend 的執行層**。讀 `slide-plan.json` v1.1，依序跑 3 個 core recipe（copy-template → replace-text → insert-image），回傳 Drive URL。**不做設計判斷**（設計諮詢 → `slides-design`）、**不做首次設定**（auth / gws 安裝 → `google-slides-setup`）。

本 skill 呼叫 `scripts/google-slides/gws-wrap.sh`（plugin root 下）包裝的 `gws` CLI；所有 shell script contract 與 exit code 對映見 TECH-SPEC §4.2。

## When to use

- 使用者已備 `slide-plan.json`（schema v1.1），頂層 `target == "google-slides"`
- 使用者貼來結構化資料（文字大綱 + 本機圖片路徑 + template 指向），要求自動合成 Google Slides
- 「跑 pipeline」「匯出 deck」「把這份計畫變成 Google Slides」

## When NOT to use

- **設計諮詢**（Minto / SCQA / chart-type 選擇）→ `slides-design`
- **首次設定**（gws 未裝、OAuth 未配、Keychain / env 問題）→ `google-slides-setup`
- `target != "google-slides"`（html / pptx / marp 皆為 Phase 2+ trigger-gated，見 PRODUCT-SPEC §3.5）
- 任務超出 slides-toolkit 範圍（文案 → `copywriting-toolkit`；投資分析 → `investing-toolkit`）

## Prerequisites

- `google-slides-setup` 已跑完一次：
  - `~/.cache/slides-toolkit/bin/gws` 與 `jq` 已下載 + SHA-256 verified
  - Google OAuth 已 grant（scopes：`presentations` + `drive.file`；見 TECH-SPEC §4.4）
  - `~/.config/gws/env.sh` 已補 issue #119 workaround（若偵測需要）
- `templates/registry.md` 已註冊至少一筆 template（填 Drive ID）
- macOS + Claude Code 執行環境；所有輸入檔 **UTF-8 only**

## Input contract（slide-plan.json v1.1）

完整 schema 見 TECH-SPEC §4.1。必含頂層欄位：

| Field | Type | Required | Note |
|---|---|---|---|
| `version` | string | yes | 必為 `"1.1"` |
| `target` | string | yes | MVP 僅支援 `"google-slides"`；其他 → exit 12 |
| `output_title` | string | yes | 新 deck 檔名（UTF-8） |
| `dry_run` | bool | no (default `false`) | `true` → 只驗 schema / registry / local image，不呼 API |
| `backend_config.template_ref` | string | yes | 對應 `templates/registry.md` 的 `ref` 欄 |
| `slides[]` | array | yes | 可為空（僅 copy template）；每 slide 可含 `replacements` map 與 `images[]` |
| `slides[].replacements` | object | no | `{{UPPER_CASE}}: value`；Unicode 允許 |
| `slides[].images[]` | array | no | 每 image 需 `placeholder_id` + `local_path`；`~` / 絕對 / cwd-relative 皆可（見 TECH-SPEC §9 OPEN-8） |

**Placeholder 命名慣例**：全部用 `{{UPPER_CASE}}`（例：`{{TITLE}}`、`{{BODY_1}}`、`{{IMG_MAIN}}`）——低碰撞、視覺一致。

## Workflow

按以下 4 步執行；任一步 fail，依 exit code 表回報並停止。

### Step 1 — Pre-flight check

Run `checklists/pre-flight.md`（10 項；每項 shell-runnable）。所有 check 通過才進 Step 2；否則依該 check 指定的 exit code 回報。

**關鍵驗證**：
- jq: `.version == "1.1"`、`.target == "google-slides"`、`.backend_config.template_ref` 非空
- `gws auth status` token 未過期（`credential-check.sh`）
- `scripts/google-slides/env-guard.sh check` 不回 exit 16（issue #119 workaround 在位）

### Step 2 — Resolve template

從 `templates/registry.md` 以 `backend_config.template_ref` 當 lookup key 找 Drive ID。

找不到 → exit 12，訊息指引 user 去編輯 `templates/registry.md` 補一筆。

### Step 3 — Execute 3 recipes in order

按順序執行；前一步失敗則停，**不**跳過：

1. **copy-template** — 從 registry Drive ID 複製一份 → 得新 `presentation_id`
   見 `protocols/recipe-copy-template.md`
2. **replace-text** — 對新 deck 跑 `replaceAllText` batchUpdate（所有 `{{KEY}}: value`）
   見 `protocols/recipe-replace-text.md`
3. **insert-image** — 本機圖片上傳 Drive、設 public link，再 `replaceAllShapesWithImage`
   見 `protocols/recipe-insert-image.md`

若 `slides[]` 為空 → 只做 Step 3.1，直接回 URL。

### Step 4 — Emit result

成功時 stdout 印單行 JSON：

```json
{
  "url": "https://docs.google.com/presentation/d/<presentation_id>/edit",
  "presentation_id": "<id>",
  "slides_count": N,
  "warnings": ["13a: placeholder {{FOO}} 未命中"]
}
```

stderr 印人讀 progress + TaskUpdate 訊息（recipe 開始 / 結束、429 retry、warning 摘要）。

## Error handling（exit code 對映）

完整表見 TECH-SPEC §4.2；本 skill 常見：

| Exit | 意義 | 行動 |
|---|---|---|
| 10 | token expired / unauthenticated | 呼叫 `google-slides-setup` re-auth sub-protocol；user 跑 `gws auth login` |
| 11 | 429 rate limit 重試 5 次仍敗 | 稍後重試；若連續發生，降低並發 |
| 12 | Google resource not found（template / deck / `target` 不支援） | 檢查 registry Drive ID / `target` 欄位 |
| 13a | `replaceAllText` 零 replacement（某 key 在 template 找不到） | **warning**；檢查 template 是否有此 placeholder |
| 13b | `createImage` 找不到 placeholder object id | **warning**；檢查 template shape id |
| 13c | `replaceAllShapesWithImage` 找不到 placeholder text | **warning**；檢查 `{{IMG_N}}` 是否存在於 shape 上 |
| 13d | Template schema drift（fingerprint mismatch） | **warning**；user 決定是否重 approve template |
| 14 | local image 檔案不存在 | 檢查 `local_path`（`~` 已展開） |
| 15 | schema validation failed | 修 `slide-plan.json` |
| 16 | issue #119 / invalid_scope | 回 `google-slides-setup` 跑 `env-guard.sh apply` |

**13 系列為 warning**：pipeline 繼續走完、最後一併回報到 `warnings[]`；不 abort。

## Token expiry（passive）

依 TECH-SPEC §6.3 策略——**不**主動 refresh：

- Pre-flight 的 `credential-check.sh` 若回 `expires_in_sec < 0` → exit 10
- stderr 印：`Your gws refresh token has expired (Google External + Testing policy: 7-day lifetime). Please run: \`gws auth login\` then retry.`
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

- TECH-SPEC §3.4（本 module 定義）、§4.1（schema）、§4.2（exit code）、§4.3（gws recipe 對映）、§4.4（OAuth scope）、§4.6（E2E data flow）、§4.7（registry format）
- PRODUCT-SPEC §4.2（3 核心 scenarios）、§6.2（設計知識層定位）
- 本 skill bundled files：
  - `checklists/pre-flight.md`
  - `protocols/recipe-copy-template.md`
  - `protocols/recipe-replace-text.md`
  - `protocols/recipe-insert-image.md`
  - `templates/registry.md`（user-editable；Drive ID 不入 public repo）

---

> 🔄 CHECKPOINT: This artifact is raw output. Pipeline: consult your workflow for the next gate.
