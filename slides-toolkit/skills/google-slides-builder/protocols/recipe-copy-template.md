# Recipe — copy-template

複製 user 自備的 template deck，得到新的 `presentation_id` 供後續 recipe 操作。對應 TECH-SPEC §4.3 table row 1。

## 目的

- 從 `templates/registry.md` 查 `template_ref` → Drive file ID
- 呼叫 `gws drive files copy` 複製一份（保留 template 不動）
- 回傳新 `presentation_id`（Drive 回傳的 file id，亦即 Slides deck id）

## Input

```json
{
  "template_ref": "weekly_report",
  "output_title": "2026-W17 Weekly Report"
}
```

| Field | Required | Note |
|---|---|---|
| `template_ref` | yes | 必須對應 `templates/registry.md` 一筆 `ref` |
| `output_title` | yes | 新 deck 檔名（UTF-8；出現在 Drive 檔案列表） |

## 步驟

### 1. Registry lookup

從 `templates/registry.md` 以 `template_ref` 查 Drive ID（解析 markdown table）：

```bash
# Pseudo-code intent
drive_id=$(awk -F'|' -v ref="$template_ref" '
  $2 ~ "^ *"ref" *$" {gsub(/ /,"",$3); print $3}
' templates/registry.md)
```

- 找不到 → **exit 12**，stderr 印：`template_ref "<ref>" not found in templates/registry.md; please add an entry.`

### 2. 呼叫 drive.files.copy

```bash
scripts/google-slides/gws-wrap.sh drive files copy \
  --fileId="$drive_id" \
  --json '{"name": "'"$output_title"'"}'
```

`gws-wrap.sh` 內部處理：
- `env-guard.sh check` pre-flight
- `gws auth status` ping（token 過期 → exit 10）
- 429 指數退避 retry（1 / 2 / 4 / 8 / 16s，jitter ±20%）

### 3. 解析 response

gws stdout 為 Drive API 原生回傳：

```json
{
  "kind": "drive#file",
  "id": "1NewCopyDeckId...",
  "name": "2026-W17 Weekly Report",
  "mimeType": "application/vnd.google-apps.presentation"
}
```

取 `.id` = 新 `presentation_id`；`jq -r '.id'`。

### 4. 傳遞給下一 recipe

後續 `recipe-replace-text` 與 `recipe-insert-image` 以此 `presentation_id` 為操作目標。

## 錯誤對映

| 情境 | Exit | Stderr 訊息關鍵字 |
|---|---|---|
| `template_ref` 不在 registry | 12 | `template_ref not found` |
| template Drive ID 已失效 / 404 | 12 | `File not found` |
| OAuth 權限不足（template 非自己擁有、且未分享） | 10 | `403` / `insufficientPermissions` |
| Token 過期 | 10 | `401` / `invalid_grant` |
| 429 重試 5 次仍敗 | 11 | `rate limit exhausted` |

## Example

**Input**:

```json
{
  "template_ref": "client_pitch",
  "output_title": "Acme Q2 提案 v1"
}
```

**Registry 內對應列**（`templates/registry.md`）：

```
| client_pitch | 1DeF...UvW | sha1:d4e5f6... | 18 pages |
```

**gws 呼叫**（pseudo）：

```
gws drive files copy --fileId=1DeF...UvW --json '{"name":"Acme Q2 提案 v1"}'
```

**Response**（Drive API 原生）：

```json
{
  "kind": "drive#file",
  "id": "1NewCopy_AbCdEf",
  "name": "Acme Q2 提案 v1",
  "mimeType": "application/vnd.google-apps.presentation"
}
```

**傳遞給下一 recipe 的狀態**：

```json
{"presentation_id": "1NewCopy_AbCdEf"}
```

---

**See also**: TECH-SPEC §4.3 recipe table、§4.7 registry format、`templates/registry.md`。
