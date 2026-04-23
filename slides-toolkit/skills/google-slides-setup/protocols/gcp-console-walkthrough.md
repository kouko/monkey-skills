# GCP Console Walkthrough — Google Slides Backend 首次設定

> Step-by-step tutorial：從零到 `gws auth whoami` 回傳 email。MVP scope
> 限個人 `@gmail.com` + macOS。全程預估 **10–15 分鐘**。

## 前置確認

動手前確認：

- 你有可用的 **個人 `@gmail.com`** 帳號（Google Workspace 企業帳號走
  Admin Console 流程，屬 Phase 2+，本 walkthrough 不涵蓋）
- 作業系統是 **macOS**（darwin-arm64 或 darwin-x86_64；M 系列與 Intel 皆可）
- 瀏覽器是 **Chrome 或 Safari**（其他瀏覽器理論上也行，但 Google OAuth
  頁面以這兩者為標準體驗）
- Terminal 裡 `curl --version` 可正常執行

如果你已有「半完成」狀態（binary 抓過 / client_secret.json 存在但
auth 掛掉），先跑 `checklists/setup-state.md` 判斷目前卡在哪一步，
然後跳到對應章節，**不要**整條重跑。

---

## Part A — 瀏覽器 Console 操作（6 步）

以下 6 步全部在 https://console.cloud.google.com 內完成。

### §1. Create GCP project

**為什麼要做**：OAuth Client ID 必須屬於某個 GCP project；這是
Google 的 tenant 邊界。你之後所有 API quota、credential、audit log
都掛在這個 project 底下。

**操作**：

1. 打開 https://console.cloud.google.com
2. 若第一次進，接受 T&C
3. 畫面左上角「Select a project」→ 右上「NEW PROJECT」
4. Project name 填：`slides-toolkit`（或任何你喜歡的名字）
5. Organization 若有選項，選 "No organization"（個人 Gmail 無 org）
6. 按 **CREATE**，等 ~30 秒

**預期結果**：右上角 project selector 顯示你剛建的 project 名字。

**常見錯誤**：
- 「You don't have permission to create projects」→ 你登入的帳號可能被
  Google Workspace 政策限制；換成真正個人 Gmail。
- 建完看不到：重新整理、確認 project selector 下拉確實選中

---

### §2. OAuth consent screen → External + Testing

**為什麼要做**：GCP 的 OAuth 必須先定義「我的 app 要給誰用」。個人
Gmail 無 org，只能選 **External**；不想過 Google production 審核，
就停在 **Testing** mode。Testing 的代價是 refresh token 壽命 7 天
（見 SKILL.md §Every 7 days maintenance）；好處是 0 審核、0 等待。

**操作**：

1. 左側選單「APIs & Services」→「OAuth consent screen」
2. User Type 選 **External** → CREATE
3. App information：
   - App name：`slides-toolkit`
   - User support email：你自己的 Gmail
   - Developer contact：你自己的 Gmail
4. 其他欄位空著 → SAVE AND CONTINUE
5. Scopes 頁面：**不要加任何 scope**（要用的 scope 由 CLI 動態要求）→
   SAVE AND CONTINUE
6. Test users 頁面見 §3
7. Summary 頁面：BACK TO DASHBOARD
8. Publishing status 應顯示 **Testing**

**預期結果**：OAuth consent screen dashboard 顯示 Testing mode + App
name = `slides-toolkit`。

**常見錯誤**：
- 不小心按了 "PUBLISH APP" → 進入 Verification needed 流程；按
  "BACK TO TESTING" 退回。

---

### §3. Add yourself as Test user

**為什麼要做**：Testing mode 下 Google 只允許「Test users 清單內的
Gmail」完成 OAuth。**漏這步會在 step 10 看到 `403 access_denied`**，
這是新手最常踩的坑。

**操作**：

1. OAuth consent screen → 往下拉到「Test users」區塊
2. 按 **+ ADD USERS**
3. 輸入你自己的 Gmail（就是步驟 §1 登入這個 Console 的那個 Gmail）
4. 按 **ADD** → **SAVE**

**預期結果**：Test users 清單包含你的 Gmail。

**常見錯誤**：
- 用了別的 Gmail 登入 Console，但加 test user 加錯 → 確認 Console 右
  上角登入的帳號 == 之後 `gws auth` 要用的帳號 == test user 清單內的
  帳號。三者必須同一個。

---

### §4. Create OAuth 2.0 Client ID → Desktop app type

**為什麼要做**：這是 gws 後續用來跑 OAuth flow 的 Client。**Application
type 必須選 `Desktop app`**（不是 Web、不是 Mobile）。Desktop type 會
給一組 client ID + client secret + 開 localhost callback 能力；Web
type 需要公開 redirect URI，CLI 工具用不了。

**操作**：

1. 左側「APIs & Services」→「Credentials」
2. 上方「+ CREATE CREDENTIALS」→「OAuth client ID」
3. Application type 選 **Desktop app**
4. Name 填：`slides-toolkit-cli`
5. CREATE → 跳出「OAuth client created」對話框，先別關

**預期結果**：Credentials 頁面列表多一筆 OAuth 2.0 Client IDs，
type = Desktop。

**常見錯誤**：
- 選到 Web application → 之後會踩 invalid_redirect_uri。刪掉重建。

---

### §5. Download `client_secret.json` → `~/.config/gws/`

**為什麼要做**：gws CLI 需要讀這個 JSON 來知道 client_id / client_secret。
放 `~/.config/gws/` 是 gws 官方慣例，也對齊 `standards/credential-hygiene.md`
規則 2「使用者 credential 統一放 `~/.config/gws/`」。

**操作**：

1. 在剛剛 §4 的對話框按 **DOWNLOAD JSON**（或從 Credentials 列表右側
   下載圖示）
2. Terminal：

   ```bash
   mkdir -p ~/.config/gws
   chmod 700 ~/.config/gws
   mv ~/Downloads/client_secret_*.json ~/.config/gws/client_secret.json
   chmod 600 ~/.config/gws/client_secret.json
   ```

**預期結果**：

```bash
ls -l ~/.config/gws/client_secret.json
# -rw-------  1 you  staff  ~400  ...  client_secret.json
```

權限必須是 `600`（只有你自己可讀寫）。這條規則來自
`standards/credential-hygiene.md` + ASVS V14。

**常見錯誤**：
- 忘了 chmod → `standards/credential-hygiene.md` 規則 4 的 `.gitignore`
  能擋誤 commit，但 home 目錄權限錯還是可能被其他 process 讀。馬上 chmod。
- 放錯路徑 → gws 會報找不到 client_secret；`scripts/google-slides/env-guard.sh`
  和 §8 的 `jq -r .installed.client_id ~/.config/gws/client_secret.json`
  都寫死這個路徑。

---

### §6. Enable APIs：Google Slides API + Google Drive API

**為什麼要做**：GCP 預設不啟用任何 API，要明確啟用才能呼叫。本 MVP
只需兩個（least-privilege，ASVS V1）：

- **Google Slides API** — `replaceAllText` / `createImage` 等 batchUpdate
- **Google Drive API** — `files.copy` / `files.upload`（範圍限 `drive.file`）

**操作**：

1. 左側「APIs & Services」→「Enabled APIs & services」→「+ ENABLE APIS AND SERVICES」
2. 搜尋 `Google Slides API` → ENABLE
3. 回上一頁，搜尋 `Google Drive API` → ENABLE

**預期結果**：Enabled APIs 列表包含兩者。

**常見錯誤**：
- 只啟用 Slides 忘了 Drive → 跑到 copy template 時會 `403 API not enabled`。
- 啟了多餘 API（e.g. Google Docs API）→ 無害但違反 least-privilege；
  可忽略或於 Credentials 頁面移除。

---

## Part B — 本機命令（4 步）

### §7. 跑 `bootstrap.sh`

**為什麼要做**：本 skill 不要求使用者預裝 `gws` 或 `jq`。`bootstrap.sh`
從官方 GitHub release 抓這兩個 binary 到 `~/.cache/slides-toolkit/bin/`，
並對每個 binary 做 **SHA-256 比對**（TECH-SPEC §2.3，ASVS V13 supply
chain）。

**操作**：

```bash
cd /path/to/monkey-skills/plugins/slides-toolkit
bash scripts/google-slides/bootstrap.sh
```

**預期結果**：

```json
{"gws_version":"v0.X.Y","jq_version":"1.7.1","cache_dir":"~/.cache/slides-toolkit/bin"}
```

（TODO：具體 `gws` / `jq` 版本號於 release commit 由 `scripts/google-slides/bootstrap.sh`
內 pin，TECH-SPEC §2.4 標為 TBD。）

**常見錯誤**：
- exit 17 `SHA-256 mismatch` → 網路被攔截或 upstream release 剛變動。
  先確認網路，再看 upstream release page 是否有新版；不要手動繞過
  SHA 檢查。
- exit 1 `unknown platform` → 你的機器不是 darwin-arm64 / darwin-x86_64；
  MVP 不支援 Linux / WSL。

---

### §8. Export issue #119 env vars

**為什麼要做**：gws 內建的 OAuth Client ID 在個人 Gmail 上踩
`invalid_scope` / `invalid_client`（upstream issue #119）。Workaround
是 export 你剛建的 OAuth Client credential 為 env var，讓 gws 用你的
而不是它內建的。詳解：`protocols/issue-119-workaround.md`。

**操作**（快速版）：

```bash
export GOOGLE_WORKSPACE_CLI_CLIENT_ID=$(jq -r .installed.client_id ~/.config/gws/client_secret.json)
export GOOGLE_WORKSPACE_CLI_CLIENT_SECRET=$(jq -r .installed.client_secret ~/.config/gws/client_secret.json)
```

若想永久生效（每次開 terminal 自動 load），加進 `~/.zshrc` 或 `~/.bashrc`
 —— 作法見 `protocols/issue-119-workaround.md` §寫入 shell profile。

或改用 `scripts/google-slides/env-guard.sh apply` 讓 skill 幫你寫進
`~/.config/gws/env.sh`（chmod 600），`scripts/google-slides/gws-wrap.sh`
每次呼叫前會 source 這個檔。

**預期結果**：

```bash
echo $GOOGLE_WORKSPACE_CLI_CLIENT_ID
# 40+ 字元的字串，結尾常是 .apps.googleusercontent.com
```

**常見錯誤**：
- `jq: command not found` → §7 `bootstrap.sh` 沒跑，或 PATH 沒包含
  `~/.cache/slides-toolkit/bin`。
- 兩個 env var 有一個空字串 → `client_secret.json` 結構異常（可能你
  下載時選錯 client type，見 §4 要選 **Desktop app**）。

---

### §9. 跑 `gws auth login`

**為什麼要做**：向 Google 取得 refresh token。`gws` 會開瀏覽器讓你同
意 scope，callback 回 `localhost` 後把 token 存進 Keychain（或 file
backend fallback）。

**操作**：

```bash
gws auth login -s presentations,drive.file
```

**重要**：**不要**用 `--preset recommended` 或類似參數。`recommended`
preset 會拉一組包含 `drive`（full）和 `userinfo.email` 的 scope 清
單，而 Testing mode 的 consent screen 只允許特定 scope 組合，會踩
`invalid_scope`。**只寫 `-s presentations,drive.file`**（least-privilege，
TECH-SPEC §4.4）。

**預期結果**：Terminal 顯示一個 URL，並自動開啟瀏覽器。

**常見錯誤**：
- `invalid_scope` → 可能用了 `recommended` preset；改用明確的
  `-s presentations,drive.file`
- `invalid_client` → §8 env var 未 export；回 §8
- 自動開啟瀏覽器失敗 → 手動複製 URL 貼到瀏覽器網址列

---

### §10. 瀏覽器同意 → callback

**為什麼要做**：完成 OAuth 三方握手。Testing mode 的 consent screen
會顯示「Google hasn't verified this app」警告——**這是正常的**，因
為你本來就沒申請 production 審核。

**操作**：

1. 瀏覽器會跳到 Google 登入 / 選帳號頁面，選 §3 加進 Test users 的那個 Gmail
2. 會看到「**Google hasn't verified this app**」警告頁
3. 點左下 **Advanced**
4. 點 **Go to slides-toolkit (unsafe)**（文字會是你在 §2 填的 App name）
5. 看到 scope 清單（`See, edit, create, and delete only the specific
   Google Drive files you use with this app` + `See, edit, create, and
   delete all your Google Slides presentations`）
6. 點 **Continue** → **Allow**
7. 瀏覽器顯示「Authentication successful, you can close this tab」
8. Terminal 顯示 `Login successful` 或類似訊息

**預期結果**：`gws auth whoami` 回傳你的 Gmail：

```bash
gws auth whoami
# your_email@gmail.com
```

**常見錯誤**：
- `403 access_denied` → 你登入的 Gmail **不在** Test users 清單；
  回 §3 加進去
- 點 "BACK TO SAFETY" 取消了 → 重跑 §9
- Callback 卡住 → 瀏覽器視窗被關、防火牆擋 loopback；重跑 §9

---

## 完成判準

```bash
gws auth whoami
# 回傳你的 Gmail = ✅ 設定完成
```

接著可以走 `google-slides-builder` skill 跑第一份 deck。若 whoami 沒
回傳或報錯，回 `checklists/setup-state.md` 逐項 diagnose。

## 預估總時間

| 段落 | 預估 |
|---|---|
| Part A（Console 6 步） | 8–10 分鐘（熟練後可壓到 5 分鐘） |
| Part B（本機 4 步） | 2–5 分鐘（bootstrap 下載 + gws auth 等待） |
| **合計** | **10–15 分鐘**（KR2 目標 ≤ 20 分鐘，PRODUCT-SPEC §3.1） |

下次設定新機器可直接跳到 §7（復用現有 GCP project / Client Secret /
Enabled APIs，只需重跑 bootstrap + re-auth）。
