# gws CLI 實測行為與 spec-drift 紀錄

截至 2026-04-24 kouko 機器上 `googleworkspace/cli` v0.22.5 的實測行為。用來對照 spec 文件（recipes 或 walkthrough）中可能 drift 的寫法。

## 1. Path parameters 進 `--params`，不是獨立 flag

❌ 錯誤（我們 spec 原本寫的）：
```bash
gws slides presentations get --presentationId="$DECK_ID"
gws slides presentations batchUpdate --presentationId="$DECK_ID" --json '...'
gws drive permissions create --fileId="$FILE_ID" --json '...'
```

✅ 正確：
```bash
gws slides presentations get --params "{\"presentationId\":\"$DECK_ID\"}"
gws slides presentations batchUpdate --params "{\"presentationId\":\"$DECK_ID\"}" --json '...'
gws drive permissions create --params "{\"fileId\":\"$FILE_ID\"}" --json '...'
```

規則：Google REST API 的 URL path / query parameters（如 `presentationId` / `fileId` / `fields` / `pageSize` / `q`）都丟進 `--params` JSON。`--json` 只用來帶 request body（POST / PATCH / PUT 的 payload）。

## 2. `gws drive files create --upload` 有 cwd sandbox

❌ 錯誤：
```bash
gws drive files create \
  --json '{"name":"x.png","mimeType":"image/png"}' \
  --upload /tmp/x.png
# → ERROR: --upload '/tmp/x.png' resolves to '/private/tmp/x.png' which is
#   outside the current directory
```

✅ 正確：
```bash
cd /tmp  # 先 cd 到檔案所在目錄
gws drive files create \
  --json '{"name":"x.png","mimeType":"image/png"}' \
  --upload x.png  # 用 basename，相對 path
```

規則：`--upload` **只接受 cwd 或其子目錄的相對路徑**，絕對路徑會被 reject。**無** env var / flag 可繞過。實作時 caller 必須 `cd "$(dirname "$PATH")"` + `basename` 做 path resolution。

## 3. `gws auth login --scopes=` vs `-s`

❌ 錯誤（我們 SKILL 原本寫的）：
```bash
gws auth login -s presentations,drive.file
# → 只有 presentations 進入 OAuth URL；drive.file 被忽略
```

✅ 正確：
```bash
gws auth login \
  --scopes=https://www.googleapis.com/auth/presentations,https://www.googleapis.com/auth/drive.file
```

規則：
- `-s` / `--services` 是「**service 名稱過濾器**」（用來過濾 scope picker 的可選項）；合法值是 gws 認得的服務短名（drive / gmail / sheets / slides / ...）
- `--scopes` 才是「**精準指定 scope**」；接受 comma-separated 完整 OAuth URL
- `drive.file` 不是 service 名 → 用 `-s` 時 silently ignored

## 4. Image URL 用 `uc?id=` 不用 `webContentLink`

Drive `files.create` 的 response 含 `webContentLink`，形如：
```
https://drive.google.com/uc?id=<FILE_ID>&export=download
```

❌ 錯誤：直接把 `webContentLink` 丟 `createImage.url` → Slides API render 失敗（`&export=download` 會觸發下載 rather than inline）

✅ 正確：
```bash
IMG_URL="https://drive.google.com/uc?id=$FILE_ID"  # 手動拼，不帶 export=download
```

## 5. 新建 deck 的 default slide 用 `CENTERED_TITLE` + `SUBTITLE` placeholder

`presentations.create` 回的 default 第一張 slide（layout = TITLE）**placeholder type 是 `CENTERED_TITLE` + `SUBTITLE`**，不是 `TITLE` + `SUBTITLE`。

Recipe 裡組 placeholder_map 時若 assume 所有 TITLE layout 都用 `TITLE` placeholder type，會在第一張 slide 漏掉。

實證從 `presentations.get` 回的 JSON：
```json
"pageElements": [
  {"objectId": "i0", "shape": {"placeholder": {"type": "CENTERED_TITLE"}}},
  {"objectId": "i1", "shape": {"placeholder": {"type": "SUBTITLE"}}}
]
```

## 6. `stderr` 的 `Using keyring backend: keyring` 是正常訊息

實測 gws 所有命令（涉及 auth 的）會在 stderr 印一行：
```
Using keyring backend: keyring
```

這**不是錯誤**，是 gws 告訴你它用 macOS Keychain 作 credential backend。實作時 stderr parsing 要能區分這類 progress log vs 真正 error。

## 7. batchUpdate reply object shape

對 `insertText` / `replaceAllText` 的 batchUpdate request，實測 reply 是**空物件** `{}`，不是 `{"insertText":{}}`：

```json
{
  "presentationId": "...",
  "replies": [
    {},
    {},
    {"createSlide": {"objectId": "slide_body"}}
  ]
}
```

只有像 `createSlide` 這種會產出新物件的 request，reply 才包含對應 key。解析時不要 assume 所有 request 都有對應 key。

## 8. `gws` 路徑固定 `~/.cache/slides-toolkit/bin/gws`（by bootstrap.sh）

skill 呼叫 gws 時用絕對路徑 `~/.cache/slides-toolkit/bin/gws`，不依賴 `$PATH`，這樣：
- 不需要要求使用者把 gws 加進 `$PATH`
- 避免和系統 gws（若有）衝突（future-proof：若使用者 brew install 了別版 gws，skill 用的仍是我們 pin 的版本）

## 9. `GOOGLE_WORKSPACE_CLI_CLIENT_ID/SECRET` env var **必須 export**（不只 set）

實測：只有 `source ~/.config/gws/env.sh` 還不夠，env.sh 內的 `export` 要讓子程序看到。Skill 內呼叫 gws 前應：
```bash
source ~/.config/gws/env.sh
export GOOGLE_WORKSPACE_CLI_CLIENT_ID GOOGLE_WORKSPACE_CLI_CLIENT_SECRET  # re-export for subprocess
```

或把 env.sh 寫成：
```bash
#!/usr/bin/env bash
export GOOGLE_WORKSPACE_CLI_CLIENT_ID='...'  # 已有 export 關鍵字 → source 後直接生效
export GOOGLE_WORKSPACE_CLI_CLIENT_SECRET='...'
```

---

## 新增 recipe 時的 checklist

若要加新 recipe 對應某個 Google API，套用以下 checklist：

- [ ] Path parameters（URL segments + query params）都進 `--params` JSON？
- [ ] Request body 進 `--json`（GET / DELETE 可能不需要）？
- [ ] 若有 file upload → 有 `cd` + basename 處理？
- [ ] OAuth scope 用完整 URL？確認是 Sensitive / Non-sensitive / Restricted 哪一級？
- [ ] 若有 Drive 產物 → 需要 public permission 才能被別處引用？
- [ ] Response parsing 預期包含空物件情境？
- [ ] Recipe md 尾部加「Live-tested behavior」區塊引用實測 JSON 片段？
