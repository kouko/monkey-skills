# Recipe — create-slides

對剛建好的空 deck 跑一次 `presentations.batchUpdate`，用 `createSlide` requests 逐頁建立 slide，每頁帶 `slideLayoutReference.predefinedLayout` 指定 Google 內建 layout。從 response 解析每頁的 placeholder `objectId`，建構 `placeholder_map` 往下游傳。對應 TECH-SPEC §4.3 recipe table row 2。

## 目的

- 依 `slide-plan.json` 的 `slides[]` 陣列，依序 `createSlide`
- 每頁用 `layout_hint` enum 指定 Google 內建 predefined layout
- 解析 `createSlide` response，把每頁的 placeholder `objectId` 收齊成 `placeholder_map`
- `placeholder_map` 往下游傳給 `recipe-insert-text` 與 `recipe-insert-image`

**Because** 使用 Google 內建 predefined layout（`TITLE` / `TITLE_AND_BODY` / ...）可避免 template copy 的 placeholder drift 風險，且由 Google 端保證 layout 視覺基本可讀性（PRODUCT-SPEC v0.3 §4.4 Principle 2）。

## Input

| Field | Required | Note |
|---|---|---|
| `presentation_id` | yes | 由 `recipe-create-presentation` 傳來 |
| `slides[].slide_index` | yes | `>= 0`；決定插入順序 |
| `slides[].layout_hint` | yes | **必須屬 7 enum** |

`layout_hint` **僅允許** 7 值（對應 Google Slides API `Page.slideProperties.layoutObjectId` → `predefinedLayout`；見 TECH-SPEC §4.1）：

| enum | 用途 |
|---|---|
| `TITLE` | 封面 / 章節封 |
| `TITLE_AND_BODY` | 通用內頁（標題 + 條列內文） |
| `TITLE_AND_TWO_COLUMNS` | 雙欄對照（左右各一區塊） |
| `SECTION_HEADER` | 段落分隔頁（大標）|
| `MAIN_POINT` | 單一重點強調頁 |
| `BIG_NUMBER` | 大數字凸顯頁（KPI / metric） |
| `BLANK` | 空白（自由排版；無預設 placeholder） |

**非 7 值 → exit 15**（pre-flight 已攔；若跑到此 recipe 才發現為 defence-in-depth）。

## 步驟

### 1. 處理預設首頁

`presentations.create` 回的 deck 有**一個預設首頁**（通常 layout 為 `TITLE`）。策略：

- 若 plan `slides[0].layout_hint == "TITLE"` → **保留**預設首頁，視為 `slide_index: 0`；後續 `createSlide` 從 index 1 開始
- 否則 → 先用 `deleteObject` request 刪預設首頁，再從 `slide_index: 0` 起全部 `createSlide`

**Because** 保留再改 layout 比刪了重建省一次 API round trip；但 layout mismatch 時不值得用 `updatePageProperties` 去改 layoutReference（可能跨 master/layout 對映斷裂）。

### 2. 組 batchUpdate body

對 `slides[]` 逐筆產一個 `createSlide` request：

```json
{
  "createSlide": {
    "objectId": "slide_${index}",
    "insertionIndex": "${index}",
    "slideLayoutReference": {
      "predefinedLayout": "${layout_hint}"
    }
  }
}
```

用 `jq` 一次攤平：

```bash
requests=$(jq '[
  .slides[] | {
    createSlide: {
      objectId: ("slide_" + (.slide_index | tostring)),
      insertionIndex: (.slide_index | tostring),
      slideLayoutReference: { predefinedLayout: .layout_hint }
    }
  }
]' slide-plan.json)

body=$(jq -n --argjson r "$requests" '{requests: $r}')
```

### 3. 呼叫 batchUpdate

```bash
echo "$body" | scripts/google-slides/gws-wrap.sh slides presentations batchUpdate \
  --presentationId="$presentation_id" \
  --json-stdin
```

### 4. 解析 response → `placeholder_map`

Response 結構（簡化）：

```json
{
  "replies": [
    {"createSlide": {"objectId": "slide_0"}},
    {"createSlide": {"objectId": "slide_1"}}
  ]
}
```

**但 `createSlide` reply 不含 placeholder objectId**——須另發一次 `presentations.get` 或每個 slide 跑 `pages.get` 取得 `pageElements`（每個 `pageElement.shape.placeholder` 帶 `type` 與 `objectId`）。

**推薦流程**（最小 API call）：`createSlide` 後直接 `presentations.get --fields='slides(objectId,pageElements(objectId,shape(placeholder)))'`：

```bash
scripts/google-slides/gws-wrap.sh slides presentations get \
  --presentationId="$presentation_id" \
  --fields='slides(objectId,pageElements(objectId,shape(placeholder)))'
```

從結果建 `placeholder_map`（key 為 **placeholder role**，符合下游 insertText 的 key 對映；見 `recipe-insert-text.md`）：

```json
{
  "slide_0": {
    "TITLE":    "g1a2b3_0",
    "SUBTITLE": "g1a2b3_1"
  },
  "slide_1": {
    "TITLE":  "g4c5d6_0",
    "BODY_1": "g4c5d6_1"
  }
}
```

**對映規則**：`shape.placeholder.type` 值（e.g. `TITLE` / `SUBTITLE` / `BODY`）→ `placeholder_map` 的 key。同 type 多個 placeholder（e.g. `TITLE_AND_TWO_COLUMNS` 會有兩個 `BODY`）則以 `BODY_1` / `BODY_2` 編號（依 `shape.placeholder.index` 或出現順序）。

### 5. 傳給下游

```json
{
  "presentation_id": "1NewDeckAbCdEf",
  "placeholder_map": { /* 如上 */ },
  "slides_created": N
}
```

## 錯誤對映

| 情境 | Exit | Stderr |
|---|---|---|
| `layout_hint` 不在 7 enum（pre-flight 漏攔） | **15** | `invalid layout_hint "<value>"; must be one of {TITLE, TITLE_AND_BODY, ...}` |
| `createSlide` 回 400（invalid predefinedLayout） | **15** | 同上 |
| API 呼叫失敗（token / quota / 5xx） | 10 / 11 / **12** | 依 `gws-wrap.sh` 判斷 |
| `presentations.get` 後 `placeholder_map` 為空（layout 無 placeholder，如 `BLANK`） | 0（正常） | stderr 印 info：`slide_N is BLANK, no placeholders` |
| 429 重試耗盡 | 11 | `rate limit exhausted` |

## 注意事項

- **Enum 驗證應在 pre-flight 完成**（`checklists/pre-flight.md` 第 3 項）；本 recipe 只做 defence-in-depth
- **`BLANK` layout 無 placeholder**：下游 `recipe-insert-text` 若對 `BLANK` slide 收到 replacements 則回 **13a warning**
- **`slide_index` 連續**：假設 `slides[].slide_index` 為 0, 1, 2, ... 連續整數（無空缺）。非連續時 `insertionIndex` 語意以**最終 deck 排序**為準，建議 plan 產生時就按順序排好
- **`createSlide` objectId**：設為 `slide_<index>` 便於 debug；Google 接受 6-50 字元，a–z A–Z 0–9 `_` `-`

## Example

**Input**（從 slide-plan.json 截取）：

```json
{
  "presentation_id": "1NewDeckAbCdEf",
  "slides": [
    {"slide_index": 0, "layout_hint": "TITLE"},
    {"slide_index": 1, "layout_hint": "SECTION_HEADER"},
    {"slide_index": 2, "layout_hint": "TITLE_AND_BODY"}
  ]
}
```

**batchUpdate body**：

```json
{
  "requests": [
    {"createSlide": {"objectId":"slide_0","insertionIndex":"0","slideLayoutReference":{"predefinedLayout":"TITLE"}}},
    {"createSlide": {"objectId":"slide_1","insertionIndex":"1","slideLayoutReference":{"predefinedLayout":"SECTION_HEADER"}}},
    {"createSlide": {"objectId":"slide_2","insertionIndex":"2","slideLayoutReference":{"predefinedLayout":"TITLE_AND_BODY"}}}
  ]
}
```

**Response + presentations.get → placeholder_map**：

```json
{
  "presentation_id": "1NewDeckAbCdEf",
  "placeholder_map": {
    "slide_0": {"TITLE": "g_0_title", "SUBTITLE": "g_0_sub"},
    "slide_1": {"TITLE": "g_1_title"},
    "slide_2": {"TITLE": "g_2_title", "BODY_1": "g_2_body"}
  },
  "slides_created": 3
}
```

---

**See also**: TECH-SPEC §4.1 schema v1.2（`layout_hint` enum）、§4.3 recipe row 2、§4.6 E2E data flow step 2；PRODUCT-SPEC §4.4 Principle 2。

<!-- TODO: `predefinedLayout` 7 enum 實際 string 值應以 Google Slides API 官方文件為準：
https://developers.google.com/slides/api/reference/rest/v1/presentations.pages#predefinedlayout
本檔列 7 個為最穩定常見子集；若官方 API 有新增（如 ONE_COLUMN_TEXT）屬 Phase 2 enum 擴充。 -->
