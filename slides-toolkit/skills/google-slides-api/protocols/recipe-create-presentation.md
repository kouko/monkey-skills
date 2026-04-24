# Recipe — create-presentation

呼叫 `gws slides presentations create` 建立一份**空白**的新 Google Slides deck，作為後續 `recipe-create-slides` / `recipe-insert-text` / `recipe-insert-image` 的目標。對應 TECH-SPEC §4.3 recipe table row 1。

## 目的

- 以 `slide-plan.json` 頂層的 `output_title` 作為新 deck 的 `title`
- 一次 API call 建立空 deck（無任何 slide），取得新 `presentationId`
- 把 `presentationId` 往下游傳（`recipe-create-slides` 用）
- 不使用 template copy（v0.3 移除；見 PRODUCT-SPEC §3.2 Non-Goal）

**Because** create-from-scratch 模型零 template 管理 overhead、零 Drive ID 洩漏風險、零 schema drift（PRODUCT-SPEC v0.3 §4.4 Principle 2 Layout-based）。

## Input

| Field | Required | From | Note |
|---|---|---|---|
| `output_title` | yes | `slide-plan.json` top-level | UTF-8 only；non-empty |

```json
{
  "output_title": "2026-W17 Weekly Report"
}
```

## 步驟

### 1. 讀 `output_title`

```bash
title=$(jq -r '.output_title' slide-plan.json)
[[ -n "$title" ]] || { echo "missing output_title" >&2; exit 15; }
```

### 2. 呼叫 gws

```bash
body=$(jq -n --arg t "$title" '{title: $t}')

echo "$body" | scripts/google-slides/gws-wrap.sh slides presentations create \
  --json-stdin
```

**gws 命令 intent**：`gws slides presentations create --json '{"title":"<output_title>"}'`

### 3. 解析 response

Response（簡化）：

```json
{
  "presentationId": "1NewDeckAbCdEf",
  "title": "2026-W17 Weekly Report",
  "slides": [
    {"objectId": "p", "pageElements": []}
  ]
}
```

**注意**：`presentations.create` 會回一個**預設首頁**（通常 `objectId: "p"`，layout 為 `TITLE`）。下游 `recipe-create-slides` 須把此預設首頁納入 placeholder_map（視為 `slide_index: 0` 若 plan 第 0 頁為 `TITLE`；否則 `batchUpdate` 先 `deleteObject` 刪除再 `createSlide` 補回）。實際策略見 `recipe-create-slides.md` §1。

取 `presentationId`：

```bash
deck_id=$(echo "$resp" | jq -r '.presentationId')
```

### 4. 傳給下游

```json
{
  "presentation_id": "1NewDeckAbCdEf",
  "deck_url": "https://docs.google.com/presentation/d/1NewDeckAbCdEf/edit"
}
```

## 錯誤對映

| 情境 | Exit | Stderr |
|---|---|---|
| `output_title` 缺 / 非 string / empty | 15 | `schema validation failed: output_title` |
| Token 過期 | 10 | `401 / invalid_grant; run gws auth login` |
| 403 forbidden（scope 不足 / Drive quota / policy） | **10** | `insufficient permissions — check presentations + drive.file scope` |
| 429 重試 5 次仍敗 | **11** | `rate limit exhausted` |
| 其他 5xx | 依 `gws-wrap.sh` 判斷（retry）；耗盡 → 11 | — |
| Response 缺 `presentationId` | 12 | `create failed: no presentationId in response` |

**注意**：v0.3 exit table（TECH-SPEC §4.2）中 exit 10 涵蓋 unauthenticated / scope-missing 情境；403 建議映到 10 以便 Claude 統一路由到 `google-slides-setup` re-auth。

## 注意事項

- **UTF-8 only**：`output_title` 含日文 / 中文 / emoji 時 gws 處理無虞，但 `jq` 必須在 UTF-8 locale 執行（`gws-wrap.sh` 首行已 `export LC_ALL=en_US.UTF-8`；見 TECH-SPEC §8.5）
- **Dry-run**：若 `dry_run: true` 則本 recipe **不執行**；由 pre-flight 短路返回 `{"url":null,"presentation_id":null,...}`（見 checklists/pre-flight.md 第 10 項）
- **不做 Drive folder 指定**：MVP 預設新 deck 落在 user Drive root；folder 指定屬 Phase 2+（無明確 trigger）

## Example

**Input**（從 `slide-plan.json` 截取）：

```json
{
  "output_title": "2026-W17 週報"
}
```

**gws 命令**（intent）：

```bash
gws slides presentations create --json '{"title":"2026-W17 週報"}'
```

**Response**（簡化）：

```json
{
  "presentationId": "1Xyz123NewDeck",
  "title": "2026-W17 週報",
  "slides": [{"objectId": "p"}]
}
```

**Output**（往下游傳）：

```json
{
  "presentation_id": "1Xyz123NewDeck",
  "deck_url": "https://docs.google.com/presentation/d/1Xyz123NewDeck/edit"
}
```

---

**See also**: TECH-SPEC §4.2 exit code、§4.3 recipe table row 1、§4.6 E2E data flow step 1；PRODUCT-SPEC §4.4 Principle 2 Layout-based。

<!-- TODO: 實際 `gws slides presentations create` 的 flag 命名（`--json` vs `--json-stdin`）與 response envelope 應以 `gws --help` 最新輸出為準；此檔以 intent 層描述。 -->
