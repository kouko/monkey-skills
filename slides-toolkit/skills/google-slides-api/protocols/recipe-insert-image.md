# Recipe — insert-image

把本機圖片上傳 Drive → 設 `anyoneWithLink` reader permission → 手動組 public URL → 用 `createImage` 帶**明確 `elementProperties`** 把圖片插入對應 slide 的對應位置。對應 TECH-SPEC §4.3 recipe table row 4。

v0.3 改動：不再使用 `replaceAllShapesWithImage`（需 template 文字錨點）；改用 `createImage` 直接指定 `pageObjectId` + `size` + `transform`，與 `recipe-create-slides` 建的 layout placeholder 對位。

## ⚠️ 重要：cwd sandbox 限制

**`gws drive files create --upload <path>` 要求 `<path>` 落在 cwd 或其子目錄內**。絕對路徑或走出 cwd 的相對路徑會被 reject，錯誤訊息：`resolves to /private/tmp/xxx which is outside the current directory`。

→ 本 recipe 正確做法：**呼叫 upload 前先 `cd` 到圖片所在目錄，再用 basename（純檔名）當 `--upload` 參數**。

範例：

```bash
IMG_PATH="/Users/kouko/Desktop/chart.png"
cd "$(dirname "$IMG_PATH")"           # → /Users/kouko/Desktop
FILENAME=$(basename "$IMG_PATH")       # → chart.png
gws drive files create \
  --json "{\"name\":\"$FILENAME\",\"mimeType\":\"image/png\"}" \
  --upload "$FILENAME" \
  --params '{"fields":"id,name"}'
```

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

### 3. Upload to Drive（cd 後用純檔名）

```bash
cd "$(dirname "$resolved")"
FILENAME=$(basename "$resolved")

upload=$(scripts/google-slides/gws-wrap.sh drive files create \
  --json "{\"name\":\"$FILENAME\",\"mimeType\":\"image/png\"}" \
  --upload "$FILENAME" \
  --params '{"fields":"id,name"}')

upload_file_id=$(echo "$upload" | jq -r '.id')
```

**實測 gws CLI 規則**：

- `--upload` 是 flag（**不是** `--upload-file`；舊文件曾誤寫）
- `--upload` 參數必須相對於 cwd（見頂部 cwd sandbox 警告）
- `fields` 放 `--params`（Drive API 的 query param），回 JSON 只帶 `id` + `name`，降低雜訊
- Response → 取 `.id` 為 `upload_file_id`；上傳失敗 → exit 12（權限 / quota）或 11（429 耗盡）

### 4. Grant public reader permission

```bash
scripts/google-slides/gws-wrap.sh drive permissions create \
  --params "{\"fileId\":\"$upload_file_id\"}" \
  --json '{"role":"reader","type":"anyone"}'
```

**實測 gws CLI 規則**：`fileId` 是 path parameter → **必須塞 `--params`，不是獨立 `--fileId=` flag**。body（`role` / `type`）放 `--json`。若用錯 flag 會被 gws parser reject。

**Because** 若 skip，下一步 Slides render pipeline 抓不到圖。

### 5. 組 image URL（手動拼，不要用 response 的 `webContentLink`）

```bash
image_url="https://drive.google.com/uc?id=$upload_file_id"
```

**實測關鍵差異**：Drive API response 帶的 `webContentLink` 形如 `https://drive.google.com/uc?id=XXX&export=download`，**帶 `&export=download` 會讓 Slides createImage fetch 失敗**（render pipeline 拿到的是下載 response 而非圖片 raw bytes）。

→ **正確做法**：**不讀 response 的 `webContentLink`**；直接用 `FILE_ID` 手拼 `https://drive.google.com/uc?id=<FILE_ID>`（不帶 `&export=download`）。此 URL 型式實測可被 Slides render 正確抓到 PNG/JPEG。

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
        "url": "https://drive.google.com/uc?id=1ImgFileId",
        "elementProperties": {
          "pageObjectId": "slide_2",
          "size": {
            "height": {"magnitude": 2000000, "unit": "EMU"},
            "width":  {"magnitude": 2000000, "unit": "EMU"}
          },
          "transform": {
            "scaleX": 1, "scaleY": 1,
            "translateX": 6000000, "translateY": 1500000,
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
  --params "{\"presentationId\":\"$presentation_id\"}" \
  --json-stdin
```

**實測 gws CLI 規則**：`presentationId` 塞 `--params`（不是 `--presentationId=` 獨立 flag）；`requests` body 放 `--json` / `--json-stdin`。

**URL 注意**：上面 `url` 用 `https://drive.google.com/uc?id=<FILE_ID>`（不帶 `&export=download`）——見 §5。

**注意**：`pageObjectId` 是**slide 的 objectId**（`slide_<index>`），不是 placeholder 的 objectId。圖片會蓋到 slide 平面上，位置由 `transform` 決定；`placeholder_id` 僅用於**讀取原 placeholder 座標**，本 recipe 不呼叫 `replaceAllShapesWithImage`。

### 8. 解析 replies

```json
{"replies":[{"createImage":{"objectId":"new_image_g1"}}]}
```

成功則 reply 帶新圖片元素的 `objectId`。

### 9. Cleanup（可選）

完成所有 image 嵌入後，可刪 Drive 暫存圖片：

```bash
scripts/google-slides/gws-wrap.sh drive files delete \
  --params "{\"fileId\":\"$upload_file_id\"}"
```

**實測**：`fileId` 同樣塞 `--params`，不是獨立 flag。

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

**cd 後 upload**（圖片路徑落在 cwd）：

```bash
cd /Users/kouko/Desktop
gws drive files create \
  --json '{"name":"revenue_q2.png","mimeType":"image/png"}' \
  --upload 'revenue_q2.png' \
  --params '{"fields":"id,name"}'
# → {"id":"1AbCdImgFile","name":"revenue_q2.png"}
```

**Permission**（`fileId` 在 params）：

```bash
gws drive permissions create \
  --params '{"fileId":"1AbCdImgFile"}' \
  --json '{"role":"reader","type":"anyone"}'
```

**Image URL**（手拼；不從 response 讀 `webContentLink`）：`https://drive.google.com/uc?id=1AbCdImgFile`

**batchUpdate body**：

```json
{
  "requests": [{
    "createImage": {
      "url": "https://drive.google.com/uc?id=1AbCdImgFile",
      "elementProperties": {
        "pageObjectId": "slide_5",
        "size": {"height":{"magnitude":2000000,"unit":"EMU"},
                 "width": {"magnitude":2000000,"unit":"EMU"}},
        "transform": {"scaleX":1,"scaleY":1,"translateX":6000000,"translateY":1500000,"unit":"EMU"}
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

## Gotchas（實測踩到的坑）

| 坑 | 正確做法 |
|---|---|
| `--upload` 傳絕對路徑 → reject `resolves to ... which is outside the current directory` | 先 `cd "$(dirname $PATH)"`，用純檔名 `$(basename $PATH)` |
| 寫成 `--upload-file` | gws CLI 是 `--upload`（單字） |
| `drive permissions create --fileId=$ID` | `fileId` 塞 `--params '{"fileId":"..."}'`；Drive path param 一律走 params |
| `drive files delete --fileId=$ID` | 同上，用 `--params` |
| `slides presentations batchUpdate --presentationId=$ID` | 同上，用 `--params` |
| 直接把 response 的 `webContentLink`（`?id=XXX&export=download`）塞 `createImage.url` → Slides render 失敗 | 手拼 `https://drive.google.com/uc?id=<FILE_ID>`（不要 `&export=download`） |
| stderr 出現 `Using keyring backend: keyring` 誤判為錯誤 | 這是 gws 正常訊息；stdout 乾淨為 JSON。若要分離捕捉：`gws ... 2>/dev/null` 或 `2>err.log` |

## Live-tested behavior (2026-04-24)

- `gws drive files create --upload <name> --params '{"fields":"id,name"}' --json '{...}'` 回：`{"id":"<FILE_ID>","name":"<FILENAME>"}`
- `gws drive permissions create --params '{"fileId":"<FILE_ID>"}' --json '{"role":"reader","type":"anyone"}'` 回：`{"id":"anyoneWithLink","type":"anyone","role":"reader"}`（或類似，帶 permission id）
- 公用 URL `https://drive.google.com/uc?id=<FILE_ID>` 在 Slides `createImage.url` 實測可成功 embed PNG
- `createImage` reply 帶新圖的 `objectId`：`{"replies":[{"createImage":{"objectId":"SLIDES_API<random>"}}]}`
- cwd sandbox 錯誤實際訊息（stderr）："file path resolves to /private/tmp/xxx which is outside the current directory"（走出 cwd 時 gws 直接 reject，不進 API call）

---

**See also**: TECH-SPEC §4.2 exit 13b + 14、§4.3 recipe row 4、§4.6 E2E data flow step 4、§9 OPEN-8（path 解析）；PRODUCT-SPEC §3.2 Non-Goals（圖片前處理）。
