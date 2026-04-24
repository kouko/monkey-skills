# Recipe — insert-image

把本機圖片上傳 Drive → 設 `anyoneWithLink` reader permission → 取 `webContentLink` → 用 `createImage` 帶**明確 `pageElementProperties`** 把圖片插入對應 slide 的對應位置。對應 TECH-SPEC §4.3 recipe table row 4。

v0.3 改動：不再使用 `replaceAllShapesWithImage`（需 template 文字錨點）；改用 `createImage` 直接指定 `pageObjectId` + `size` + `transform`，與 `recipe-create-slides` 建的 layout placeholder 對位。

## 目的

- 逐張處理 `slides[].images[]` 中的本機圖片
- 上傳 Drive、設 public reader permission、取 `webContentLink`
- `createImage` 帶 `pageElementProperties`（pageObjectId + 尺寸 + transform）明確放到目標 slide 對應位置
- 失敗時 stdout + exit code 清楚指出哪一張

## 為什麼需要 Drive upload + public permission

Google Slides API 的 `createImage.url` 欄位要求 **publicly accessible URL**（Slides API docs）。Drive 私有檔即使 caller 有權限，Slides render pipeline 也抓不到。**唯一可靠做法**：上傳後加 `role: reader / type: anyone` permission，取 `webContentLink`。

**Because** 此為 Google 端架構限制，MVP 無法繞過。

## Input

```json
{
  "presentation_id": "1NewDeckAbCdEf",
  "placeholder_map": {
    "slide_2": {"TITLE": "g_2_title", "BODY_1": "g_2_body"}
  },
  "slides": [
    {
      "slide_index": 2,
      "images": [
        {
          "placeholder_id": "BODY_1",
          "local_path": "~/Desktop/chart.png"
        }
      ]
    }
  ]
}
```

| Field | Required | Note |
|---|---|---|
| `presentation_id` | yes | 由 `recipe-create-presentation` 傳來 |
| `placeholder_map` | yes | 由 `recipe-create-slides` 傳來 |
| `slides[].images[].placeholder_id` | yes | 對應 `placeholder_map[slide_X]` 的 key（`TITLE` / `BODY_1` / ...）；圖片將放到該 placeholder 所在位置 |
| `slides[].images[].local_path` | yes | 絕對 / `~` 展開 / cwd-relative（TECH-SPEC §9 OPEN-8） |

## 步驟

### 1. 路徑解析（TECH-SPEC §9 OPEN-8）

按順序嘗試：

1. Absolute path（以 `/` 開頭）→ 直接用
2. `~/` 展開 → `eval echo "$path"`（只 eval path value）
3. cwd-relative → `"$PWD/$path"`

```bash
resolve_path() {
  case "$1" in
    /*)   echo "$1" ;;
    \~*)  eval echo "$1" ;;
    *)    echo "$PWD/$1" ;;
  esac
}
```

### 2. 檔案檢查（pre-flight 已做；此處 defence-in-depth）

- 存在性：`[[ -f "$resolved" ]]` 否則 exit 14
- Size：`< 50 MB`（Drive multipart upload 安全邊界）
- Format：副檔名 `.png` / `.jpg` / `.jpeg` / `.gif`；其他 → exit 14

### 3. Upload to Drive

```bash
scripts/google-slides/gws-wrap.sh drive files create \
  --json '{"name":"slides-img-'"$stamp"'.png","mimeType":"image/png"}' \
  --upload="$resolved"
```

Response → 取 `.id` 為 `upload_file_id`。上傳失敗 → exit 12（權限 / quota）或 11（429 耗盡）。

### 4. Grant public reader permission

```bash
scripts/google-slides/gws-wrap.sh drive permissions create \
  --fileId="$upload_file_id" \
  --json '{"role":"reader","type":"anyone"}'
```

**Because** 若 skip，下一步 Slides render pipeline 抓不到圖。

### 5. 取 `webContentLink`

```bash
scripts/google-slides/gws-wrap.sh drive files get \
  --fileId="$upload_file_id" \
  --fields=webContentLink
```

取 `.webContentLink` 為 `image_url`。

### 6. 解析目標位置（從 placeholder_map 對位）

```bash
slide_key="slide_${slide_index}"
target_object_id=$(jq -r --arg sk "$slide_key" --arg pid "$placeholder_id" \
  '.[$sk][$pid]' <<< "$placeholder_map")
```

若 `target_object_id == "null"` → **13b warning**（placeholder_id 在當前 layout 不存在），略過此圖。

**決定 size / transform**：

- **MVP 策略**：查 `presentations.get` 取 target placeholder 的 `size` + `transform`，沿用同樣座標（圖片覆蓋到 placeholder 位置）
- Slides API 要求 `pageElementProperties` 必填 `pageObjectId`；`size` 可省（預設），`transform` 建議明確指定以避免落到左上角

### 7. batchUpdate `createImage`

```json
{
  "requests": [
    {
      "createImage": {
        "url": "https://drive.google.com/uc?id=1ImgFileId&export=download",
        "elementProperties": {
          "pageObjectId": "slide_2",
          "size": {
            "height": {"magnitude": 3000000, "unit": "EMU"},
            "width":  {"magnitude": 4500000, "unit": "EMU"}
          },
          "transform": {
            "scaleX": 1, "scaleY": 1,
            "translateX": 500000, "translateY": 500000,
            "unit": "EMU"
          }
        }
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

**注意**：`pageObjectId` 是**slide 的 objectId**（`slide_<index>`），不是 placeholder 的 objectId。圖片會蓋到 slide 平面上，位置由 `transform` 決定；`placeholder_id` 僅用於**讀取原 placeholder 座標**，本 recipe 不呼叫 `replaceAllShapesWithImage`。

### 8. 解析 replies

```json
{"replies":[{"createImage":{"objectId":"new_image_g1"}}]}
```

成功則 reply 帶新圖片元素的 `objectId`。

### 9. Cleanup（可選）

完成所有 image 嵌入後，可刪 Drive 暫存圖片：

```bash
scripts/google-slides/gws-wrap.sh drive files delete --fileId="$upload_file_id"
```

**MVP 預設不刪**（便於 debug）；若 `slide-plan.json` 擴充 `cleanup_uploads: true` 則觸發（Phase 2）。

## 錯誤對映

| 情境 | Exit | Stderr |
|---|---|---|
| `local_path` 不存在 | 14 | `local file not found: <resolved>` |
| 檔案 > 50MB / 格式不支援 | 14 | `unsupported image size / format` |
| Drive upload 失敗 | 12 | `upload failed: <reason>` |
| Permission grant 失敗 | 12 | `permission grant failed` |
| `placeholder_id` 在當前 slide `placeholder_map` 不存在 | **13b**（warning；non-fatal） | `[warn 13b] placeholder_id=<id> not found in slide_<N>` |
| `createImage` 回 400（pageObjectId 錯 / URL 抓不到） | 12 | `createImage failed: <reason>` |
| 429 重試 5 次耗盡 | 11 | `rate limit exhausted` |

## Phase 2+ Non-Goal（PRODUCT-SPEC §3.2）

以下**不**在 MVP 範圍：
- 圖片 resize / crop / format conversion（需 ImageMagick / Pillow runtime）
- 從 URL fetch 圖片（需 auth / CORS / retry；MVP 只收 local path）
- 自動壓縮到 Slides 建議尺寸
- EXIF 清除

使用者需預先把圖處理到「尺寸合適、格式 PNG/JPEG/GIF、<50MB」狀態。

## Example

**Input**：

```json
{
  "presentation_id": "1NewDeckAbCdEf",
  "placeholder_map": {"slide_5": {"BODY_1": "g_5_body"}},
  "slides": [
    {
      "slide_index": 5,
      "images": [
        {"placeholder_id": "BODY_1", "local_path": "~/Desktop/revenue_q2.png"}
      ]
    }
  ]
}
```

**Resolved path**：`/Users/kouko/Desktop/revenue_q2.png`

**Upload**：`{"id":"1AbCdImgFile"}`

**Permission**：`{"role":"reader","type":"anyone"}`

**webContentLink**：`https://drive.google.com/uc?id=1AbCdImgFile&export=download`

**batchUpdate body**：

```json
{
  "requests": [{
    "createImage": {
      "url": "https://drive.google.com/uc?id=1AbCdImgFile&export=download",
      "elementProperties": {
        "pageObjectId": "slide_5",
        "size": {"height":{"magnitude":3000000,"unit":"EMU"},
                 "width": {"magnitude":4500000,"unit":"EMU"}},
        "transform": {"scaleX":1,"scaleY":1,"translateX":500000,"translateY":500000,"unit":"EMU"}
      }
    }
  }]
}
```

**Response**：`{"replies":[{"createImage":{"objectId":"new_img_g1"}}]}`

**Output**（給 builder 彙總）：

```json
{
  "presentation_id": "1NewDeckAbCdEf",
  "images_inserted": 1,
  "warnings": []
}
```

---

**See also**: TECH-SPEC §4.2 exit 13b + 14、§4.3 recipe row 4、§4.6 E2E data flow step 4、§9 OPEN-8（path 解析）；PRODUCT-SPEC §3.2 Non-Goals（圖片前處理）。

<!-- TODO: `createImage.elementProperties.size / transform` 的具體 EMU 值應從
`presentations.get` 讀原 placeholder 座標帶入；本檔示例用固定值。EMU 定義與
預設 slide 尺寸（10"×5.63"）對照見 Google Slides API 官方文件：
https://developers.google.com/slides/api/concepts/page-elements -->
