# Recipe — insert-image

把本機圖片上傳 Drive → 取得 public URL → 用 `replaceAllShapesWithImage`（或等價 API）把圖片嵌入 deck 對應 placeholder。對應 TECH-SPEC §4.3 table row 3。

## 目的

- 處理 `slides[].images[]` 陣列中的每張本機圖片
- 逐張上傳 Drive、設 public reader permission、取 `webContentLink`
- 用 batchUpdate `replaceAllShapesWithImage` 把圖片塞進 template 預留的 placeholder shape
- 可選：完成後刪除 Drive 上的暫存圖片檔（避免 Drive 堆積）

## 為什麼不能直接用 Drive 私有檔

Google Slides API 的 `replaceAllShapesWithImage` / `createImage` 的 `imageUrl` 欄位要求 **publicly accessible URL**（issue #2215、Slides API docs）。若圖片是 Drive 私有檔，即便 caller 有權限，Slides render pipeline 也抓不到 → 結果為空白。**唯一可靠做法**：上傳後加一筆 `role: reader / type: anyone` 的 permission，取 `webContentLink`。

**Because** 這是 Google 端架構限制、MVP 無法繞過。

## Input

```json
{
  "presentation_id": "1NewCopy_AbCdEf",
  "slides": [
    {
      "slide_index": 3,
      "images": [
        {
          "placeholder_id": "IMG_MAIN",
          "local_path": "~/Desktop/chart.png"
        }
      ]
    }
  ]
}
```

| Field | Required | Note |
|---|---|---|
| `presentation_id` | yes | 由 `recipe-copy-template` 傳來 |
| `slides[].images[].placeholder_id` | yes | Template 中 shape 的 placeholder token（建議 `{{IMG_N}}` 命名慣例） |
| `slides[].images[].local_path` | yes | 支援絕對 / `~` 展開 / cwd-relative（見 TECH-SPEC §9 OPEN-8） |

## 步驟

### 1. 路徑解析（TECH-SPEC §9 OPEN-8）

按順序嘗試，第一個成功即採：

1. **Absolute path**（以 `/` 開頭）→ 直接用
2. **`~` 展開**（以 `~/` 開頭）→ `eval echo "$path"`（**只** eval path value，不 eval 其他內容；防 injection）
3. **Relative to Claude Code cwd** → `"$PWD/$path"`

```bash
# Pseudo-code intent
resolve_path() {
  case "$1" in
    /*)   echo "$1" ;;
    \~*)  eval echo "$1" ;;
    *)    echo "$PWD/$1" ;;
  esac
}
```

### 2. 檔案檢查

- **存在性**：`[[ -f "$resolved" ]]`；否則 **exit 14**
- **Size**：`<  50 MB`（Drive 單檔上傳 multipart 限制，安全邊界）；超過 → exit 14 + hint「請先 resize，MVP 不做自動前處理」
- **Format**：副檔名 `.png` / `.jpg` / `.jpeg` / `.gif`；其他格式 → exit 14

### 3. Upload to Drive

```bash
scripts/google-slides/gws-wrap.sh drive files create \
  --json '{"name": "slides-img-'"$stamp"'.png", "mimeType": "image/png"}' \
  --upload="$resolved"
```

Response：

```json
{"kind":"drive#file","id":"1ImgFileId...","name":"slides-img-xxx.png"}
```

取 `.id` = `upload_file_id`。

上傳失敗 → **exit 12**（Drive 權限 / quota 問題）或 11（429 重試耗盡）。

### 4. Grant public reader permission

```bash
scripts/google-slides/gws-wrap.sh drive permissions create \
  --fileId="$upload_file_id" \
  --json '{"role": "reader", "type": "anyone"}'
```

**Because** 若 skip 此步，下一步 `replaceAllShapesWithImage` 的 `imageUrl` Google 取不到圖，結果空白（見本檔開頭警告）。

### 5. 取 webContentLink

```bash
scripts/google-slides/gws-wrap.sh drive files get \
  --fileId="$upload_file_id" \
  --fields=webContentLink
```

Response：

```json
{"webContentLink": "https://drive.google.com/uc?id=1ImgFileId&export=download"}
```

取 `.webContentLink` 為 `image_url`。

### 6. batchUpdate `replaceAllShapesWithImage`

```json
{
  "requests": [
    {
      "replaceAllShapesWithImage": {
        "imageUrl": "https://drive.google.com/uc?id=1ImgFileId&export=download",
        "containsText": {"text": "{{IMG_MAIN}}", "matchCase": true},
        "replaceMethod": "CENTER_INSIDE"
      }
    }
  ]
}
```

呼叫：

```bash
echo "$body" | scripts/google-slides/gws-wrap.sh slides presentations batchUpdate \
  --presentationId="$presentation_id" \
  --json-stdin
```

### 7. 解析 replies

```json
{
  "replies": [
    {"replaceAllShapesWithImage": {"occurrencesChanged": 1}}
  ]
}
```

- `occurrencesChanged == 0` → **warning 13c**（placeholder text 在 template shape 內找不到）
- 若改用 `createImage` + `objectId` 路徑（Phase 2 優化），對應 warning 為 **13b**

### 8. Cleanup（可選）

完成所有 image 嵌入後，可刪除 Drive 上的暫存圖片：

```bash
scripts/google-slides/gws-wrap.sh drive files delete --fileId="$upload_file_id"
```

**MVP 預設不刪**（便於 debug）；`slide-plan.json` 可在 `backend_config` 加 `cleanup_uploads: true` 觸發（Phase 2 擴充）。

## 錯誤對映

| 情境 | Exit | Stderr |
|---|---|---|
| `local_path` 不存在 | 14 | `local file not found: <resolved>` |
| 檔案 > 50MB 或格式不支援 | 14 | `unsupported image format / size` |
| Drive upload 失敗 | 12 | `upload failed: <reason>` |
| `replaceAllShapesWithImage` 找不到 placeholder text | **13c**（warning） | `[warn 13c] placeholder {{IMG_MAIN}} 未命中` |
| `createImage` 找不到 placeholder object id（Phase 2 路徑） | **13b**（warning） | `[warn 13b] placeholder_id IMG_MAIN not found` |
| Permission grant 失敗 | 10 / 12 | 視 error 性質 |
| 429 重試 5 次仍敗 | 11 | `rate limit exhausted` |

## 警告 — Phase 2+ Non-Goal

以下**不**在 MVP 範圍（見 PRODUCT-SPEC §3.2）：
- 圖片 resize / crop / format conversion（需 ImageMagick 或 Pillow runtime）
- 從 URL fetch 圖片（需處理 auth / CORS / retry；MVP 只收 local path）
- 自動壓縮到 Slides 建議尺寸
- EXIF 清除

user 需預先把圖片處理到「尺寸合適、格式 PNG/JPEG/GIF、<50MB」狀態。

## Example

**Input**:

```json
{
  "presentation_id": "1NewCopy_AbCdEf",
  "slides": [
    {
      "slide_index": 5,
      "images": [
        {"placeholder_id": "IMG_CHART", "local_path": "~/Desktop/revenue_q2.png"}
      ]
    }
  ]
}
```

**Resolved path**: `/Users/kouko/Desktop/revenue_q2.png`

**Upload 回傳**:

```json
{"id": "1AbCdImgFile", "name": "slides-img-20260423.png"}
```

**Permission 回傳**: `{"id":"anyoneWithLink","role":"reader","type":"anyone"}`

**webContentLink**: `https://drive.google.com/uc?id=1AbCdImgFile&export=download`

**batchUpdate body**:

```json
{
  "requests": [{
    "replaceAllShapesWithImage": {
      "imageUrl": "https://drive.google.com/uc?id=1AbCdImgFile&export=download",
      "containsText": {"text": "{{IMG_CHART}}", "matchCase": true},
      "replaceMethod": "CENTER_INSIDE"
    }
  }]
}
```

**Response**: `{"replies":[{"replaceAllShapesWithImage":{"occurrencesChanged":1}}]}`

**Output**（給 builder 的彙總）：

```json
{
  "presentation_id": "1NewCopy_AbCdEf",
  "images_inserted": 1,
  "warnings": []
}
```

---

**See also**: TECH-SPEC §4.2 exit 13b / 13c、§4.3、§9 OPEN-8（path 解析）；PRODUCT-SPEC §3.2 Non-Goals（圖片前處理）。
