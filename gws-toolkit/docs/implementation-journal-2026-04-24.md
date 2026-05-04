# Implementation Journal — 2026-04-24

首次 live E2E 測試。目的：驗證 slides-toolkit v0.3.2 的 4 recipes 在真實環境可跑完 pipeline，產出可用的 Google Slides deck。

## Environment

- **Machine**：kouko 本機，macOS darwin-arm64
- **Google account**：`kouko.d@gmail.com`（個人 Gmail，非 Workspace org）
- **Starting state**：
  - `gcloud`：not installed
  - `brew`：`/opt/homebrew/bin/brew` ✓
  - `gws` binary：`~/.cache/slides-toolkit/bin/gws` 已由 `bootstrap.sh` 抓好（v0.22.5）
  - 無 GCP project、無 OAuth credentials

## Live Session 時序（精華）

### Phase 1 — 裝 gcloud + auth（~5 min）

```bash
brew install --cask google-cloud-sdk
# → ~1GB 下載；裝好後 /opt/homebrew/bin/gcloud → Google Cloud SDK 565.0.0

gcloud auth login --quiet
# → 自動開瀏覽器 localhost callback；點允許；回 terminal 印
#   "You are now logged in as [kouko.d@gmail.com]"
```

**注意事項**：
- 第一次嘗試用 `--no-launch-browser --brief` 失敗，原因：Bash tool 沒 stdin 接受 verification code。正確做法是**不加** `--no-launch-browser`，讓 gcloud 自己開瀏覽器 + localhost callback。
- 參考：<https://cloud.google.com/sdk/gcloud/reference/auth/login>

### Phase 2 — 嘗試 `gws auth setup`（失敗，但暴露真相）

```bash
gws auth setup --project slides-toolkit-260424 --dry-run
# → Step 3/6: Project set to slides-toolkit-260424（但 project 不存在也沒 create）
# → Step 4/5: Would enable 22 APIs
# → Step 5/5: Would configure OAuth credentials

gws auth setup --project slides-toolkit-260424  # 實跑
# → RESOURCES_NOT_FOUND on project
# → 即使 project 存在，亦會在 OAuth client 建立步驟報錯：
#   "OAuth client creation requires manual setup in the Google Cloud Console."
```

**發現**：`gws auth setup` 名字暗示全自動，實際只自動「enable APIs」一步。OAuth client 建立 / test user 加入皆**無法**自動。

**根因**（隨後 GitHub Explore 研究確認）：gws source `crates/google-workspace-cli/src/setup.rs:913` 有註解：
```rust
// (create_oauth_client removed due to IAP Admin APIs deprecation)
```
Google 的 IAP OAuth Admin API 在 2025-01-22 deprecated，gws 主動移除了對應的 create_oauth_client 實作。

### Phase 3 — 回到 gcloud 手動 project + enable APIs（~1 min）

```bash
PROJECT_ID="slides-toolkit-260424"
gcloud projects create "$PROJECT_ID" --name="slides-toolkit"
# → operations/create_project.global.*
# → 順帶自動 enable cloudapis.googleapis.com

gcloud config set project "$PROJECT_ID"
gcloud services enable slides.googleapis.com drive.googleapis.com --project="$PROJECT_ID"
```

### Phase 4 — 嘗試 ADC passthrough（失敗，但重要教訓）

嘗試繞開 Console manual：

```bash
gcloud auth application-default login \
  --scopes=openid,email,profile,presentations,drive.file
# → ERROR: cloud-platform scope required; added and retry
```

加 `cloud-platform` 後跑，瀏覽器顯示：
> **系統已封鎖這個應用程式**
> 這個應用程式嘗試存取您 Google 帳戶中的機密資訊。為保護您的帳戶，Google 已阻擋這個存取行為。

**發現**：gcloud 的 built-in OAuth client 雖然是 Google 官方驗證過，**但只為 Google Cloud 類 scope 驗證**（cloud-platform 等）。要向個人帳戶請求 `presentations` / `drive.file` 這類 user-sensitive scope 時，OAuth client 需**單獨通過該 scope 的 verification**。gcloud 沒通過 → Google 反濫用機制擋下。

**反推**：這解釋了為何 gws 強制使用者自建 OAuth client — 連 Google 自家 gcloud 都不能隨意借用 scope。

### Phase 5 — Console 手動 2 步（~3 min）

使用者在瀏覽器完成：
1. **Google Auth Platform → Audience** subpage，往下捲到 **Test users** section，`+ Add users` → `kouko.d@gmail.com` → Save
2. **Google Auth Platform → Clients** subpage，`+ Create client` → Application type: **Desktop app**（不是 Web）→ Name: `slides-toolkit-cli` → Create → **Download JSON** 到 `~/Downloads/`

**UI 注意點**：
- 新版 UI（2026 啟用）名稱：**Google Auth Platform**，不是舊版 "APIs & Services → OAuth consent screen"
- Test users 是 **Audience 分頁內的區塊**，**不是獨立分頁**。這點容易混淆
- "Credentials" 改名為 **Clients**

### Phase 6 — 本機搬 JSON + 寫 env.sh（~10 sec）

```bash
mkdir -p ~/.config/gws && chmod 700 ~/.config/gws
mv ~/Downloads/client_secret_*.json ~/.config/gws/client_secret.json
chmod 600 ~/.config/gws/client_secret.json

CLIENT_ID=$(jq -r '.installed.client_id' ~/.config/gws/client_secret.json)
CLIENT_SECRET=$(jq -r '.installed.client_secret' ~/.config/gws/client_secret.json)

cat > ~/.config/gws/env.sh <<EOF
#!/usr/bin/env bash
export GOOGLE_WORKSPACE_CLI_CLIENT_ID='$CLIENT_ID'
export GOOGLE_WORKSPACE_CLI_CLIENT_SECRET='$CLIENT_SECRET'
EOF
chmod 600 ~/.config/gws/env.sh
```

### Phase 7 — `gws auth login`（踩 scope flag 坑）

第一次嘗試：
```bash
gws auth login -s presentations,drive.file
# URL 產生時檢視：只包含 presentations，drive.file 沒進去
```

**發現**：`-s` / `--services` 是**篩選 scope picker 的 service 名**（e.g. drive, gmail），**不是**精準指定 scope。`drive.file` 不是 service 名 → 被忽略。

正確做法：用 `--scopes=` + 完整 OAuth URL：
```bash
source ~/.config/gws/env.sh
export GOOGLE_WORKSPACE_CLI_CLIENT_ID GOOGLE_WORKSPACE_CLI_CLIENT_SECRET
gws auth login \
  --scopes=https://www.googleapis.com/auth/presentations,https://www.googleapis.com/auth/drive.file
# → 印 URL + 開瀏覽器
# → 瀏覽器顯示 "Google hasn't verified this app"（正常，Testing mode）
# → Advanced → Go to slides-toolkit (unsafe) → Allow
# → terminal 顯示 "Authentication successful. Encrypted credentials saved."
```

### Phase 8 — E2E recipe 驗證（~2 min）

**Recipe 1 — create-presentation**：
```bash
gws slides presentations create --json '{"title":"slides-toolkit smoke test 2026-04-24"}'
# ✓ 成功。回 presentationId + layouts[] + slides[]（含 1 個 default TITLE slide，
#   placeholder: CENTERED_TITLE + SUBTITLE）
```

**Recipe 2 + 3 — create-slides + insert-text**：
```bash
gws slides presentations batchUpdate \
  --params "{\"presentationId\":\"$DECK_ID\"}" \
  --json '{"requests":[
    {"insertText":{"objectId":"i0","text":"slides-toolkit 測試成功 🎉"}},
    {"insertText":{"objectId":"i1","text":"End-to-end pipeline 驗證"}},
    {"createSlide":{"objectId":"slide_body","slideLayoutReference":{"predefinedLayout":"TITLE_AND_BODY"}}}
  ]}'
# ✓ 3 個 request 都 OK；createSlide reply 含 objectId: "slide_body"
```

取新 slide 的 placeholders：
```bash
gws slides presentations get \
  --params "{\"presentationId\":\"$DECK_ID\",\"fields\":\"slides(objectId,pageElements(objectId,shape(placeholder(type))))\"}"
# → slide_body 含 SLIDES_API1800863615_0 (TITLE) + SLIDES_API1800863615_1 (BODY)
```

填入 TITLE + BODY：
```bash
gws slides presentations batchUpdate \
  --params "{\"presentationId\":\"$DECK_ID\"}" \
  --json '{"requests":[
    {"insertText":{"objectId":"SLIDES_API1800863615_0","text":"4-recipe Pipeline 驗證"}},
    {"insertText":{"objectId":"SLIDES_API1800863615_1","text":"✓ recipe-create-presentation\n✓ recipe-create-slides (TITLE_AND_BODY layout)\n✓ recipe-insert-text (placeholder object ID mapping)"}}
  ]}'
# ✓ 成功
```

**Recipe 4 — insert-image**（踩最多坑）：
```bash
cd /tmp  # MUST: gws --upload 有 cwd sandbox，絕對路徑被 reject

gws drive files create \
  --json '{"name":"slides-toolkit-test.png","mimeType":"image/png"}' \
  --upload slides-toolkit-test.png \
  --params '{"fields":"id,name"}'
# ✓ 回 id + name

FILE_ID="14xLl4i1oCZClWXWAJgikXwYSs0doMxlK"

gws drive permissions create \
  --params "{\"fileId\":\"$FILE_ID\"}" \
  --json '{"role":"reader","type":"anyone"}'
# ✓ 注意：fileId 要在 --params，不是獨立 flag

IMG_URL="https://drive.google.com/uc?id=$FILE_ID"
# 注意：不要用 response 的 webContentLink（帶 &export=download 會讓 createImage 失敗）

gws slides presentations batchUpdate \
  --params "{\"presentationId\":\"$DECK_ID\"}" \
  --json "...createImage with pageElementProperties..."
# ✓ 成功，deck 右下角有圖
```

### 產物

- **Test deck**：<https://docs.google.com/presentation/d/1rCqdw0HvYow4Hr5l38Ark1ZzpDsGYptWtW-dHkYT6lY/edit>
- **Drive file**（test image）：`14xLl4i1oCZClWXWAJgikXwYSs0doMxlK`
- **GCP project**：`slides-toolkit-260424`

## 總結學到的事

1. **gws auth setup 只能自動 Enable APIs**，其他都得手動（因 IAP OAuth Admin API deprecation）
2. **ADC passthrough 繞不過** — Google 會擋非 verified client 請求 user-sensitive scope
3. **新 Console UI** 把 OAuth consent screen 改成 Google Auth Platform，Test users 在 Audience 分頁裡
4. **gws CLI 有多處 spec-drift**（--params vs flag、--upload cwd sandbox、--scopes 語法、URL 格式），詳見 [`gws-cli-quirks.md`](gws-cli-quirks.md)
5. **4 recipes 全部可實跑**，pipeline 架構正確

## 時間統計

| Phase | 耗時 |
|---|---|
| brew install gcloud | ~3 min |
| gcloud auth login | ~30 sec |
| Phase 2 `gws auth setup` 失敗摸索 | ~5 min（不計入正式流程） |
| Phase 3 project + APIs | ~30 sec |
| Phase 4 ADC 繞路失敗 | ~2 min（不計入） |
| Phase 5 Console 手動 2 步 | ~3 min |
| Phase 6 本機 JSON + env | ~10 sec |
| Phase 7 gws auth login（含踩 -s 坑） | ~2 min |
| Phase 8 recipe 實測 | ~3 min |

**第一次設定實際耗時**（含兩次繞路失敗）：~15 min
**第二次起（知道路徑）預期**：~7-8 min（對應 `auto-setup.sh` Path A）
