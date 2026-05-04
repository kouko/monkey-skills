# Recipe — insert-image

Upload a local image to Drive → grant `anyoneWithLink` reader permission → manually compose a public URL → call `createImage` with **explicit `elementProperties`** to place the image on the target slide. Corresponds to TECH-SPEC §4.3 recipe table row 4.

v0.3 change: `replaceAllShapesWithImage` (which required text-anchor placeholders in a template) is no longer used. `createImage` now specifies `pageObjectId` + `size` + `transform` directly, aligning with the layout placeholders created by `recipe-create-slides`.

## ⚠️ Important: cwd sandbox constraint

**`gws drive files create --upload <path>` requires `<path>` to be inside the current working directory (or a subdirectory)**. An absolute path, or a relative path that escapes cwd, is rejected with: `resolves to /private/tmp/xxx which is outside the current directory`.

→ The correct pattern: **`cd` into the image's directory before calling upload, and pass the basename (filename only) as `--upload`**.

Example:

```bash
IMG_PATH="/Users/kouko/Desktop/chart.png"
cd "$(dirname "$IMG_PATH")"           # → /Users/kouko/Desktop
FILENAME=$(basename "$IMG_PATH")       # → chart.png
gws drive files create \
  --json "{\"name\":\"$FILENAME\",\"mimeType\":\"image/png\"}" \
  --upload "$FILENAME" \
  --params '{"fields":"id,name"}'
```

## Purpose

- Process each local image in `slides[].images[]` one at a time
- Upload to Drive, grant public reader permission, compose the image URL
- Call `createImage` with `pageElementProperties` (pageObjectId + size + transform) to place the image at a specific spot on the target slide
- On failure, make stdout + exit code identify exactly which image

## Why we need Drive upload + public permission

The Google Slides API `createImage.url` field requires a **publicly accessible URL** (per Slides API docs). Private Drive files are unreachable from the Slides render pipeline even if the caller has access. The only reliable approach: upload, then add `role: reader / type: anyone` permission, and compose the `webContentLink`.

**Because** this is a Google-side architectural constraint; the MVP cannot work around it.

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
| `presentation_id` | yes | from `recipe-create-presentation` |
| `placeholder_map` | yes | from `recipe-create-slides` |
| `slides[].images[].placeholder_id` | yes | matches a key in `placeholder_map[slide_X]` (`TITLE` / `BODY_1` / ...); the image is placed at that placeholder's position |
| `slides[].images[].local_path` | yes | absolute / `~`-expanded / cwd-relative (TECH-SPEC §9 OPEN-8) |

## Steps

### 1. Resolve the path (TECH-SPEC §9 OPEN-8)

Try in order:

1. Absolute path (starts with `/`) → use as-is
2. `~/` expansion → `eval echo "$path"` (eval the path value only)
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

### 2. File checks (pre-flight already runs these; defense-in-depth here)

- Existence: `[[ -f "$resolved" ]]` — otherwise exit 14
- Size: `< 50 MB` (safe Drive multipart upload margin)
- Format: extension `.png` / `.jpg` / `.jpeg` / `.gif`; otherwise exit 14

### 3. Upload to Drive (cd first, pass basename)

```bash
cd "$(dirname "$resolved")"
FILENAME=$(basename "$resolved")

upload=$(scripts/google-slides/gws-wrap.sh drive files create \
  --json "{\"name\":\"$FILENAME\",\"mimeType\":\"image/png\"}" \
  --upload "$FILENAME" \
  --params '{"fields":"id,name"}')

upload_file_id=$(echo "$upload" | jq -r '.id')
```

**Live-tested gws CLI rules**:

- The flag is `--upload` (**not** `--upload-file`; older docs had this wrong)
- `--upload` must resolve relative to cwd (see the cwd-sandbox warning above)
- `fields` goes inside `--params` (a Drive API query parameter); the reply JSON carries only `id` + `name`, reducing noise
- Take `.id` from the response as `upload_file_id`; upload failure → exit 12 (permission / quota) or 11 (429 exhausted)

### 4. Grant public reader permission

```bash
scripts/google-slides/gws-wrap.sh drive permissions create \
  --params "{\"fileId\":\"$upload_file_id\"}" \
  --json '{"role":"reader","type":"anyone"}'
```

**Live-tested gws CLI rules**: `fileId` is a path parameter → **must go inside `--params`, not as a standalone `--fileId=` flag**. The body (`role` / `type`) goes in `--json`. Using the wrong flag is rejected by the gws parser.

**Because** without this permission, the Slides render pipeline cannot fetch the image in the next step.

### 5. Compose the image URL (construct manually; do not use the response's `webContentLink`)

```bash
image_url="https://drive.google.com/uc?id=$upload_file_id"
```

**Critical live-tested distinction**: the Drive API response returns a `webContentLink` of the form `https://drive.google.com/uc?id=XXX&export=download`. **The `&export=download` suffix makes Slides `createImage` fetch fail** (the render pipeline receives the download response rather than the raw image bytes).

→ **Correct approach**: **do not read `webContentLink` from the response**; construct the URL from `FILE_ID` directly as `https://drive.google.com/uc?id=<FILE_ID>` (no `&export=download`). This URL form has been verified to fetch correctly from the Slides render pipeline for PNG/JPEG.

### 6. Resolve the target position (look up the placeholder map)

```bash
slide_key="slide_${slide_index}"
target_object_id=$(jq -r --arg sk "$slide_key" --arg pid "$placeholder_id" \
  '.[$sk][$pid]' <<< "$placeholder_map")
```

If `target_object_id == "null"` → **13b warning** (the `placeholder_id` does not exist on the current layout); skip this image.

**Deciding size / transform**:

- **MVP strategy**: call `presentations.get` to read the target placeholder's `size` + `transform`, and reuse the same coordinates (the image overlays the placeholder's position)
- The Slides API requires `pageElementProperties.pageObjectId`; `size` may be omitted (defaults apply), but `transform` should be specified explicitly to avoid defaulting to the top-left corner

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

Invoke:

```bash
echo "$body" | scripts/google-slides/gws-wrap.sh slides presentations batchUpdate \
  --params "{\"presentationId\":\"$presentation_id\"}" \
  --json-stdin
```

**Live-tested gws CLI rules**: `presentationId` goes inside `--params` (not `--presentationId=` as a standalone flag); the `requests` body goes into `--json` / `--json-stdin`.

**URL note**: use `https://drive.google.com/uc?id=<FILE_ID>` without `&export=download` — see step 5.

**Note**: `pageObjectId` is the **slide's objectId** (`slide_<index>`), not the placeholder's objectId. The image is placed on the slide plane at coordinates driven by `transform`; `placeholder_id` is used **only to read the original placeholder's coordinates**. This recipe never calls `replaceAllShapesWithImage`.

### 8. Parse replies

```json
{"replies":[{"createImage":{"objectId":"new_image_g1"}}]}
```

On success, the reply includes the `objectId` of the new image element.

### 9. Cleanup (optional)

After all images are inserted, you can delete the temporary Drive uploads:

```bash
scripts/google-slides/gws-wrap.sh drive files delete \
  --params "{\"fileId\":\"$upload_file_id\"}"
```

**Live-tested**: `fileId` likewise goes inside `--params`, not as a standalone flag.

**MVP default is not to clean up** (easier debugging). A future `cleanup_uploads: true` field on the slide plan can trigger deletion (Phase 2).

## Error mapping

| Situation | Exit | Stderr |
|---|---|---|
| `local_path` does not exist | 14 | `local file not found: <resolved>` |
| File > 50MB or unsupported format | 14 | `unsupported image size / format` |
| Drive upload fails | 12 | `upload failed: <reason>` |
| Permission grant fails | 12 | `permission grant failed` |
| `placeholder_id` not in the slide's `placeholder_map` | **13b** (warning; non-fatal) | `[warn 13b] placeholder_id=<id> not found in slide_<N>` |
| `createImage` returns 400 (bad pageObjectId / URL unreachable) | 12 | `createImage failed: <reason>` |
| 429 still failing after 5 retries | 11 | `rate limit exhausted` |

## Phase 2+ Non-Goals (PRODUCT-SPEC §3.2)

Out of MVP scope:
- Image resize / crop / format conversion (would need an ImageMagick or Pillow runtime)
- Fetching images from a URL (requires auth / CORS / retry; MVP only accepts local paths)
- Auto-compressing to Slides' recommended dimensions
- EXIF scrubbing

Users must pre-process images to "appropriate size, PNG/JPEG/GIF format, < 50 MB".

## Example

**Input**:

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

**Resolved path**: `/Users/kouko/Desktop/revenue_q2.png`

**Upload after cd** (image path resolves inside cwd):

```bash
cd /Users/kouko/Desktop
gws drive files create \
  --json '{"name":"revenue_q2.png","mimeType":"image/png"}' \
  --upload 'revenue_q2.png' \
  --params '{"fields":"id,name"}'
# → {"id":"1AbCdImgFile","name":"revenue_q2.png"}
```

**Permission** (`fileId` in params):

```bash
gws drive permissions create \
  --params '{"fileId":"1AbCdImgFile"}' \
  --json '{"role":"reader","type":"anyone"}'
```

**Image URL** (constructed manually; ignoring the response's `webContentLink`): `https://drive.google.com/uc?id=1AbCdImgFile`

**batchUpdate body**:

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

**Response**: `{"replies":[{"createImage":{"objectId":"new_img_g1"}}]}`

**Output** (reported to the builder):

```json
{
  "presentation_id": "1NewDeckAbCdEf",
  "images_inserted": 1,
  "warnings": []
}
```

## Gotchas (pitfalls encountered in live testing)

| Pitfall | Correct approach |
|---|---|
| `--upload` with an absolute path → rejected with `resolves to ... which is outside the current directory` | `cd "$(dirname $PATH)"` first, then pass `$(basename $PATH)` |
| Typing `--upload-file` | The gws CLI flag is `--upload` (single word) |
| `drive permissions create --fileId=$ID` | `fileId` goes inside `--params '{"fileId":"..."}'`; every Drive path parameter uses `--params` |
| `drive files delete --fileId=$ID` | Same — use `--params` |
| `slides presentations batchUpdate --presentationId=$ID` | Same — use `--params` |
| Passing the response's `webContentLink` (`?id=XXX&export=download`) straight into `createImage.url` → Slides render fails | Construct `https://drive.google.com/uc?id=<FILE_ID>` manually (no `&export=download`) |
| Mistaking stderr `Using keyring backend: keyring` for an error | This is a normal gws message; stdout is clean JSON. To separate streams: `gws ... 2>/dev/null` or `2>err.log` |

## Live-tested behavior (2026-04-24)

- `gws drive files create --upload <name> --params '{"fields":"id,name"}' --json '{...}'` returns: `{"id":"<FILE_ID>","name":"<FILENAME>"}`
- `gws drive permissions create --params '{"fileId":"<FILE_ID>"}' --json '{"role":"reader","type":"anyone"}'` returns: `{"id":"anyoneWithLink","type":"anyone","role":"reader"}` (or similar, with a permission id)
- The public URL `https://drive.google.com/uc?id=<FILE_ID>` embeds PNG successfully when used as `createImage.url` in Slides
- The `createImage` reply carries the new image's `objectId`: `{"replies":[{"createImage":{"objectId":"SLIDES_API<random>"}}]}`
- The exact cwd-sandbox error message (stderr): `file path resolves to /private/tmp/xxx which is outside the current directory` — gws rejects the request before making the API call

---

**See also**: TECH-SPEC §4.2 exit 13b + 14, §4.3 recipe row 4, §4.6 E2E data flow step 4, §9 OPEN-8 (path resolution); PRODUCT-SPEC §3.2 Non-Goals (image preprocessing).
