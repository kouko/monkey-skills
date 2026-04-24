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

resp=$(echo "$body" | scripts/google-slides/gws-wrap.sh slides presentations create \
  --json-stdin)
```

**實測 gws CLI 命令**：

```bash
gws slides presentations create --json '{"title":"<output_title>"}'
```

- 無 path param（`presentations.create` 無 `presentationId` 輸入）
- body 全部放 `--json`（或 `--json-stdin`）
- 呼叫時 stderr 會印 `Using keyring backend: keyring`（正常訊息，非錯誤；stdout 乾淨為 JSON）

### 3. 解析 response

實測 response（刪節）：

```json
{
  "presentationId": "1NewDeckAbCdEf",
  "title": "2026-W17 Weekly Report",
  "pageSize": {"width": {...}, "height": {...}, "unit": "EMU"},
  "layouts": [ /* 所有 predefined layout 定義（TITLE / TITLE_AND_BODY / ... ） */ ],
  "masters": [ /* master slide */ ],
  "slides": [
    {
      "objectId": "<default_slide_id>",
      "pageElements": [
        {"objectId": "...", "shape": {"placeholder": {"type": "CENTERED_TITLE"}}},
        {"objectId": "...", "shape": {"placeholder": {"type": "SUBTITLE"}}}
      ]
    }
  ]
}
```

**注意**：`presentations.create` 會回**一個預設首頁**（layout 為 `TITLE`），內含 2 個 placeholder：**`CENTERED_TITLE`** + **`SUBTITLE`**（注意不是 `TITLE`；Google Slides `Placeholder.type` 對 TITLE layout 用 `CENTERED_TITLE`）。`layouts[]` 頂層也帶回所有 predefined layout 的完整定義，可供下游 debug / 參考。

下游 `recipe-create-slides` 的處理策略：若 plan `slides[0].layout_hint == "TITLE"`，把此預設首頁納入 placeholder_map（role 對映 `CENTERED_TITLE` / `SUBTITLE`）；否則先 `deleteObject` 刪除。

取 `presentationId`：

```bash
deck_id=$(echo "$resp" | jq -r '.presentationId')
```

### 3b. 取預設首頁 placeholder 物件 ID（若要複用）

```bash
gws slides presentations get \
  --params "{\"presentationId\":\"$deck_id\",\"fields\":\"slides(objectId,pageElements(objectId,shape(placeholder(type))))\"}"
```

- **注意**：`presentationId` 放 `--params` 的 JSON 裡，**不是**獨立 flag（gws CLI 把 path parameter 一律塞 `--params`）
- `fields` 也放 `--params` 裡同一個 JSON
- 回的 JSON 頂層是 `{"slides":[{"objectId":"...","pageElements":[...]}]}`

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

**gws 命令**：

```bash
gws slides presentations create --json '{"title":"2026-W17 週報"}'
```

**Response**（刪節）：

```json
{
  "presentationId": "1Xyz123NewDeck",
  "title": "2026-W17 週報",
  "slides": [{
    "objectId": "g_default_slide",
    "pageElements": [
      {"objectId": "g_default_title", "shape": {"placeholder": {"type": "CENTERED_TITLE"}}},
      {"objectId": "g_default_sub",   "shape": {"placeholder": {"type": "SUBTITLE"}}}
    ]
  }]
}
```

**Output**（往下游傳）：

```json
{
  "presentation_id": "1Xyz123NewDeck",
  "deck_url": "https://docs.google.com/presentation/d/1Xyz123NewDeck/edit"
}
```

## Live-tested behavior (2026-04-24)

實際跑 `gws slides presentations create --json '{"title":"..."}'` 觀察：

- stderr 必定印 `Using keyring backend: keyring`（一行，非錯誤，表示 gws 正在讀 token store）；呼叫者若要捕 stdout 純 JSON，請 `2>/dev/null` 或 `2>err.log`
- stdout 回的頂層 JSON 含 `presentationId` / `title` / `pageSize` / `slides[]` / `layouts[]`（所有 predefined layout 的完整定義）/ `masters[]` / `notesMaster` / `revisionId`
- 新 deck **已含一個 default slide**（layout = TITLE），帶 **2 個 placeholder**：`CENTERED_TITLE`（注意：不是 `TITLE`）+ `SUBTITLE`
- Deck URL 固定格式：`https://docs.google.com/presentation/d/<presentationId>/edit`
- `presentations.get` 用 `--params` 傳 `presentationId` + `fields`：`gws slides presentations get --params "{\"presentationId\":\"$DECK_ID\",\"fields\":\"slides(objectId,pageElements(objectId,shape(placeholder(type))))\"}"`

---

**See also**: TECH-SPEC §4.2 exit code、§4.3 recipe table row 1、§4.6 E2E data flow step 1；PRODUCT-SPEC §4.4 Principle 2 Layout-based。
