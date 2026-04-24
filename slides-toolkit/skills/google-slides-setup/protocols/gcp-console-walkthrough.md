# GCP Console Walkthrough — Google Slides Backend 首次設定

> Step-by-step tutorial：從零到 `gws auth whoami` 回傳 email。MVP scope
> 限個人 `@gmail.com` + macOS。
>
> **對齊 2026-04 Google Cloud Console 新 UI（Google Auth Platform）**。
> 舊版「APIs & Services → OAuth consent screen」入口仍 redirect，但分頁
> 結構已改為 Overview / Branding / Audience / Clients / Data Access。

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

## 選路：Path A（Fast）vs Path B（Manual）

本 walkthrough **分雙路徑**，第一步先決定走哪條：

```bash
command -v gcloud >/dev/null && echo "gcloud 已裝" || echo "gcloud 未裝"
```

| 條件 | 走哪條 | 理由 |
|---|---|---|
| `gcloud` 已裝 **或** 你願意讓 script 幫你裝 | **Path A（Fast Path）** | ~6–8 分鐘；自動化 project 建立 + API enable |
| 不想裝 gcloud，只想點 Console UI | **Path B（Full Manual）** | ~10–15 分鐘；全程 Console + bash |

> **兩條路徑共用結尾**：§Local 4 步（搬 client_secret.json → env vars
> → `gws auth login` → 驗證）。

**決策樹**：

```
                  ┌──────────────────────────┐
                  │  command -v gcloud?      │
                  └────────────┬─────────────┘
                     有        │         沒有
                  ┌────────────┴────────────┐
                  ▼                         ▼
           ┌─────────────┐         ┌──────────────────┐
           │ Path A      │         │ 願意裝 gcloud？   │
           │ auto-setup  │         └────┬──────────┬──┘
           └──────┬──────┘              │ 願意      │ 不願
                  │                     ▼          ▼
                  │              ┌──────────┐  ┌────────┐
                  │              │ Path A   │  │ Path B │
                  │              │ (裝完跑) │  │ (手動) │
                  │              └────┬─────┘  └───┬────┘
                  └─────────────────┐ │            │
                                    ▼ ▼            ▼
                           ┌──────────────┐  ┌──────────────┐
                           │ Console 手動  │  │ Console 手動  │
                           │ 2 步         │  │ 6 步         │
                           │ (Audience +  │  │ (完整流程)    │
                           │  Clients)    │  │              │
                           └──────┬───────┘  └──────┬───────┘
                                  │                 │
                                  └────────┬────────┘
                                           ▼
                                   ┌───────────────┐
                                   │ Local 4 步    │
                                   │ (共用結尾)     │
                                   └───────────────┘
```

---

## URL 規範（兩條路徑都會用）

新 UI 所有設定頁面都以 `?project=<PROJECT_ID>` 綁 project context。本文件
用 `<PROJECT_ID>` placeholder 表示你剛建的 project ID（**不是 Project
Name**；ID 在 Console 右上角 project selector 下拉可看到，通常長得像
`slides-toolkit-123456`）。

| 分頁 | URL |
|---|---|
| Overview | `https://console.cloud.google.com/auth/overview?project=<PROJECT_ID>` |
| Branding | `https://console.cloud.google.com/auth/branding?project=<PROJECT_ID>` |
| Audience | `https://console.cloud.google.com/auth/audience?project=<PROJECT_ID>` |
| Clients | `https://console.cloud.google.com/auth/clients?project=<PROJECT_ID>` |
| Data Access | `https://console.cloud.google.com/auth/dataaccess?project=<PROJECT_ID>` |
| API Library | `https://console.cloud.google.com/apis/library?project=<PROJECT_ID>` |

> **UI 導航備援**：左側漢堡 menu → **Google Auth Platform**。若看不到
> 該項，直接貼上面 URL 進瀏覽器即可。

---

# Path A — Fast Path（gcloud + `auto-setup.sh`）

> **適用**：你有 gcloud，或願意讓 script 幫你裝。總時間 ~6–8 分鐘。
>
> **script 契約**：`scripts/google-slides/auto-setup.sh` 自動做：
> (1) 偵測 / 安裝 gcloud → (2) `gcloud auth login` → (3) 建 project
> （若還沒） → (4) enable Slides + Drive API → (5) 印 Console URL 並
> 開瀏覽器讓你完成 Audience + Clients 兩步手動動作。

## §A1. 跑 `auto-setup.sh`

**為什麼要做**：把 Path B 的 §1（建 project）、§6（enable APIs）自動
化，只留兩步必須在 Console UI 內點的給使用者（建 OAuth client +
加 test user；這兩步目前沒有 gcloud 對應 API，只能 UI 操作）。

**操作**：

```bash
cd /path/to/monkey-skills/slides-toolkit
bash scripts/google-slides/auto-setup.sh
```

**script 會做**（不需你手動）：

1. `command -v gcloud` 偵測；沒有就問你 `brew install --cask google-cloud-sdk`
2. `gcloud auth login`（瀏覽器 OAuth 允許 × 1）
3. `gcloud projects create slides-toolkit-<random>` 或沿用現有
4. `gcloud services enable slides.googleapis.com drive.googleapis.com`
5. 印出 Console URL：
   - Branding 設定頁（§A2 用）
   - Audience 設定頁（§A3 用）
   - Clients 設定頁（§A4 用）
6. 以 `open <url>` 幫你開瀏覽器至 Branding 頁

**✅ 驗證**：Terminal 輸出類似：

```json
{
  "project_id": "slides-toolkit-123456",
  "gcloud_version": "5XX.0.0",
  "apis_enabled": ["slides.googleapis.com", "drive.googleapis.com"],
  "next": "Complete Branding/Audience/Clients in browser"
}
```

**❌ 常見錯誤**：
- `command not found: gcloud`（script 沒裝成功）→ 手動
  `brew install --cask google-cloud-sdk`，再重跑
- `ERROR: (gcloud.projects.create) Project creation failed` → project
  ID 全球唯一，換個 suffix 重跑；或直接沿用 `gcloud config set project`
  指向的既有 project
- `API [slides.googleapis.com] not enabled on project ...` 卻 exit 0 →
  帳號無 Billing（個人 Gmail 不用付費但仍需 link 免費 tier）；到
  `https://console.cloud.google.com/billing` link free-tier，重跑

## §A2. Branding（對應 Path B §2）

**為什麼要做**：新 UI 的 Branding 分頁 = 舊 UI「OAuth consent screen」
的 App information 區塊。填好這裡，Google 才知道同意畫面要顯示什麼
名字給使用者看。

**操作**：

1. 瀏覽器已由 `auto-setup.sh` 開到
   `https://console.cloud.google.com/auth/branding?project=<PROJECT_ID>`
2. 若 project 第一次用 Google Auth Platform，畫面會出現 **Get Started**
   按鈕 → 按下去（新 UI 會一次問完 Branding + Audience 基本設定）
3. 填：
   - **App name**：`slides-toolkit`
   - **User support email**：你自己的 Gmail
   - **Audience**：選 **External**（個人 Gmail 無 org，只有這個選項）
   - **Developer contact information**：你自己的 Gmail
4. 按 **CREATE**（或 **Save**）

**✅ 驗證**：Branding 頁顯示 App name = `slides-toolkit`，Publishing
status = **Testing**。

**❌ 常見錯誤**：
- 不小心按了 **PUBLISH APP** → 進入 Verification needed 流程；按
  **BACK TO TESTING** 退回
- App name 撞名（罕見，個人 project 無此限制）→ 改個名字

## §A3. Audience → Test users（對應 Path B §3）

**為什麼要做**：Testing mode 下 Google 只允許「Test users 清單內的
Gmail」完成 OAuth。**漏這步會在 §Local step L3 看到 `403
access_denied`**，這是新手最常踩的坑。

> **新 UI 重點**：Test users **不是獨立分頁**，而是 **Audience 分頁**
> 往下捲到的一個區塊。

**操作**：

1. 切換到 `https://console.cloud.google.com/auth/audience?project=<PROJECT_ID>`
2. 頁面往下捲找到 **"Test users"** 區塊
3. 按 **+ Add users**
4. 輸入你自己的 Gmail（必須與之後跑 `gws auth` 的那個帳號一致）
5. 按 **Save**

**✅ 驗證**：Test users 清單包含你的 Gmail，並顯示 "Up to 100 test
users allowed"。

**❌ 常見錯誤**：
- 找不到 Test users 區塊 → 滾到頁面最底；新 UI 把它埋在 Audience 分頁
  下半部
- 三個 Gmail 不一致（登入 Console 的 / 加 test user 的 / 之後 gws auth
  的）→ 都必須同一個。Console 右上角頭像確認目前登入帳號

## §A4. Create Desktop OAuth Client（對應 Path B §4 + §5）

**為什麼要做**：這是 gws 後續用來跑 OAuth flow 的 Client。**Application
type 必須選 `Desktop app`**（不是 Web、不是 Mobile）。Desktop type 會
給一組 client ID + client secret + 開 localhost callback 能力；Web
type 需要公開 redirect URI，CLI 工具用不了。

**操作**：

1. 切換到 `https://console.cloud.google.com/auth/clients?project=<PROJECT_ID>`
2. 按 **+ Create client**（新 UI 名稱；舊 UI 叫 "Create Credentials" → "OAuth client ID"）
3. **Application type**：選 **Desktop app**
4. **Name**：`slides-toolkit-cli`
5. 按 **Create** → 彈出對話框顯示 Client ID / Client Secret
6. 按 **Download JSON**（檔案會落到 `~/Downloads/client_secret_*.json`）

**✅ 驗證**：
- Clients 列表多一筆 type = Desktop 的 OAuth 2.0 Client
- `~/Downloads/` 有新下載的 `client_secret_*.json`

**❌ 常見錯誤**：
- 選到 Web application → 之後會踩 `invalid_redirect_uri`。回此分頁
  刪掉重建
- 沒按 Download JSON 就關對話框 → 不要緊，Clients 列表右側有下載
  icon（下箭頭），點它重新下載

**Path A 到此 Console 部分結束 → 直接跳到 [§Local](#local--4-步本機命令兩條路徑共用)**

---

# Path B — Full Manual（純 Console + bash）

> **適用**：你不想裝 gcloud，只想點 UI。總時間 ~10–15 分鐘。
>
> 全程使用 Console 新 UI（Google Auth Platform）+ 本機 bash 命令。

## §B1. Create GCP project

**為什麼要做**：OAuth Client ID 必須屬於某個 GCP project；這是
Google 的 tenant 邊界。你之後所有 API quota、credential、audit log
都掛在這個 project 底下。

**操作**：

1. 打開 https://console.cloud.google.com
2. 若第一次進，接受 T&C
3. 畫面左上角 project selector（目前可能顯示 "Select a project"）
4. 彈窗右上按 **NEW PROJECT**
5. **Project name**：`slides-toolkit`（或任何你喜歡的名字）
6. **Organization**：選 **No organization**（個人 Gmail 無 org）
7. 按 **CREATE**，等 ~30 秒
8. 右上 project selector 切到你剛建的 project

**✅ 驗證**：右上角 project selector 顯示你剛建的 project 名字；URL
欄的 `?project=<PROJECT_ID>` 會帶新的 ID。**記下這個 `<PROJECT_ID>`**
（接下來每個 URL 都要用）。

**❌ 常見錯誤**：
- 「You don't have permission to create projects」→ 你登入的帳號可能被
  Google Workspace 政策限制；換成真正個人 Gmail
- 建完看不到 → 重新整理、確認 project selector 下拉確實選中

## §B2. Branding（OAuth consent screen 新名稱）

**為什麼要做**：GCP 的 OAuth 必須先定義「我的 app 要給誰用」。個人
Gmail 無 org，只能選 **External**；不想過 Google production 審核，
就停在 **Testing** mode。Testing 的代價是 refresh token 壽命 7 天
（見 SKILL.md §Every 7 days maintenance）；好處是 0 審核、0 等待。

> **新 UI 變更**：舊版「APIs & Services → OAuth consent screen」已改為
> **Google Auth Platform → Branding**（`/auth/branding`）。
> 新 UI 把 branding 和 audience 分成兩分頁，但 **Get Started** 流程會
> 一次問完兩邊的必填欄位。

**操作**：

1. 打開 `https://console.cloud.google.com/auth/branding?project=<PROJECT_ID>`
   （或左側漢堡 → **Google Auth Platform** → **Branding**）
2. 若第一次用，畫面出現 **Get Started** 按鈕 → 按下去
3. App information：
   - **App name**：`slides-toolkit`
   - **User support email**：你自己的 Gmail
4. 下一步 Audience：
   - **User Type**：**External**
5. 下一步 Developer contact：
   - **Email address**：你自己的 Gmail
6. 按 **Create**

**✅ 驗證**：Branding 分頁顯示 App name = `slides-toolkit`；Overview
分頁（`/auth/overview?project=<PROJECT_ID>`）顯示 Publishing status
= **Testing**。

**❌ 常見錯誤**：
- 不小心按了 **PUBLISH APP** → 進入 Verification needed 流程；按
  **BACK TO TESTING** 退回
- Scopes 頁面被要求填 scope → **不要加任何 scope**（scope 由 CLI
  在 `gws auth login` 時動態要求）。Skip / Save and continue

## §B3. Audience → Test users

**為什麼要做**：Testing mode 下 Google 只允許「Test users 清單內的
Gmail」完成 OAuth。**漏這步會在 §L3 看到 `403 access_denied`**。

> **新 UI 重點**：Test users **不是獨立分頁**，是 **Audience 分頁**
> 內的一個區塊（舊 UI 曾短暫把它做成獨立 Test users 分頁，新 UI 合併）。

**操作**：

1. 打開 `https://console.cloud.google.com/auth/audience?project=<PROJECT_ID>`
2. 頁面往下捲到 **"Test users"** 區塊
3. 按 **+ Add users**
4. 輸入你自己的 Gmail（就是登入 Console 的這個 Gmail，也會是之後 `gws
   auth` 要用的 Gmail，三者必須一致）
5. 按 **Save**

**✅ 驗證**：Test users 清單顯示你的 Gmail。

**❌ 常見錯誤**：
- 翻半天找不到「Test users」分頁 → 它不是分頁，在 Audience 分頁往下
  捲
- 三個 Gmail 不一致 → Console 右上角頭像確認目前登入帳號

## §B4. Create Desktop OAuth Client（Clients 分頁）

**為什麼要做**：這是 gws 後續用來跑 OAuth flow 的 Client。**Application
type 必須選 `Desktop app`**（不是 Web、不是 Mobile）。

> **新 UI 變更**：舊版 Credentials 分頁已改名為 **Clients**
> （`/auth/clients`）。「+ CREATE CREDENTIALS → OAuth client ID」改為
> 直接 **+ Create client**。

**操作**：

1. 打開 `https://console.cloud.google.com/auth/clients?project=<PROJECT_ID>`
2. 按 **+ Create client**
3. **Application type**：選 **Desktop app**
4. **Name**：`slides-toolkit-cli`
5. 按 **Create** → 彈出對話框顯示 Client ID / Client Secret

**✅ 驗證**：Clients 列表多一筆 type = Desktop 的 OAuth 2.0 Client，
Name = `slides-toolkit-cli`。

**❌ 常見錯誤**：
- 選到 Web application → 之後 `gws auth login` 會踩
  `invalid_redirect_uri`。回此分頁刪掉重建

## §B5. Download `client_secret.json`

**為什麼要做**：gws CLI 需要讀這個 JSON 來知道 client_id /
client_secret。

**操作**：

1. 在剛剛 §B4 的對話框按 **Download JSON**
2. 或從 Clients 列表右側的下載 icon（下箭頭）下載

**✅ 驗證**：`~/Downloads/client_secret_*.json` 存在。

**❌ 常見錯誤**：
- 對話框已關、列表看不到下載 icon → 重新整理頁面；icon 可能需要 hover
  該列才出現

## §B6. Enable APIs：Google Slides API + Google Drive API

**為什麼要做**：GCP 預設不啟用任何 API，要明確啟用才能呼叫。本 MVP
只需兩個（least-privilege，ASVS V1）：

- **Google Slides API** — `replaceAllText` / `createImage` 等 batchUpdate
- **Google Drive API** — `files.copy` / `files.upload`（範圍限 `drive.file`）

**操作**：

1. 打開 `https://console.cloud.google.com/apis/library?project=<PROJECT_ID>`
2. 搜尋 `Google Slides API` → 點進去 → **Enable**
3. 瀏覽器返回（或重開 library URL），搜尋 `Google Drive API` → 點進去 → **Enable**

**✅ 驗證**：打開
`https://console.cloud.google.com/apis/dashboard?project=<PROJECT_ID>`
能看到 Slides API + Drive API 各一行。

**❌ 常見錯誤**：
- 只啟用 Slides 忘了 Drive → 跑到 copy template 時會 `403 API not
  enabled`
- 啟了多餘 API（e.g. Google Docs API）→ 無害但違反 least-privilege；
  可忽略或從 API dashboard 停用

**Path B 到此 Console 部分結束 → 繼續 §Local**

---

# §Local — 4 步（本機命令，兩條路徑共用）

> Path A 完成 §A1–A4 後、Path B 完成 §B1–B6 後，都從這裡開始。

## §L1. 搬 `client_secret.json` → `~/.config/gws/`

**為什麼要做**：放 `~/.config/gws/` 是 gws 官方慣例，也對齊
`standards/credential-hygiene.md` 規則 2「使用者 credential 統一放
`~/.config/gws/`」。

**操作**：

```bash
mkdir -p ~/.config/gws
chmod 700 ~/.config/gws
mv ~/Downloads/client_secret_*.json ~/.config/gws/client_secret.json
chmod 600 ~/.config/gws/client_secret.json
```

**✅ 驗證**：

```bash
ls -l ~/.config/gws/client_secret.json
# -rw-------  1 you  staff  ~400  ...  client_secret.json
```

權限必須是 `600`（只有你自己可讀寫）。這條規則來自
`standards/credential-hygiene.md` + ASVS V14。

**❌ 常見錯誤**：
- 忘了 chmod → `.gitignore` 能擋誤 commit，但 home 目錄權限錯還是
  可能被其他 process 讀。馬上 chmod
- 放錯路徑 → gws 會報找不到 client_secret；`env-guard.sh` 與
  `credential-check.sh` 都寫死這個路徑

## §L2. 跑 `bootstrap.sh` + 寫入 env vars

**為什麼要做**：本 skill 不要求使用者預裝 `gws` 或 `jq`。`bootstrap.sh`
從官方 GitHub release 抓這兩個 binary 到 `~/.cache/slides-toolkit/bin/`。

接著把 issue #119 env vars 寫入 `~/.config/gws/env.sh`：gws 內建的
OAuth Client ID 在個人 Gmail 上踩 `invalid_scope` /
`invalid_client`，必須改用你剛建的 OAuth Client。詳解：
`protocols/issue-119-workaround.md`。

**操作**：

```bash
cd /path/to/monkey-skills/slides-toolkit

# 1) 抓 binary
bash scripts/google-slides/bootstrap.sh

# 2) 寫 env vars 到 ~/.config/gws/env.sh（chmod 600）
bash scripts/google-slides/env-guard.sh apply
```

`env-guard.sh apply` 內部等價於：

```bash
cat > ~/.config/gws/env.sh <<EOF
export GOOGLE_WORKSPACE_CLI_CLIENT_ID=$(jq -r .installed.client_id ~/.config/gws/client_secret.json)
export GOOGLE_WORKSPACE_CLI_CLIENT_SECRET=$(jq -r .installed.client_secret ~/.config/gws/client_secret.json)
EOF
chmod 600 ~/.config/gws/env.sh
```

後續 `scripts/google-slides/gws-wrap.sh` 每次呼叫前會 source 這個檔。

**✅ 驗證**：

```bash
source ~/.config/gws/env.sh
echo $GOOGLE_WORKSPACE_CLI_CLIENT_ID
# 40+ 字元字串，結尾常是 .apps.googleusercontent.com

ls -l ~/.config/gws/env.sh
# -rw-------  1 you  staff  ...  env.sh
```

**❌ 常見錯誤**：
- exit 17 `SHA-256 mismatch`（bootstrap） → 網路被攔截或 upstream release
  剛變動。先確認網路，再看 upstream release page；不要手動繞過 SHA 檢查
- exit 1 `unknown platform` → 你的機器不是 darwin-arm64 / darwin-x86_64；
  MVP 不支援 Linux / WSL
- `jq: command not found` → `bootstrap.sh` 沒跑完，或 PATH 沒包含
  `~/.cache/slides-toolkit/bin`
- env var 有一個是空字串 → `client_secret.json` 結構異常（可能下載
  時選錯 client type）；回 §A4 / §B4 確認選了 Desktop app

## §L3. 跑 `gws auth login` → 瀏覽器同意

**為什麼要做**：向 Google 取得 refresh token。`gws` 會開瀏覽器讓你同
意 scope，callback 回 `localhost` 後把 token 存進 Keychain（或 file
backend fallback）。

**操作**：

```bash
source ~/.config/gws/env.sh   # 若 §L2 沒在同一 shell 跑
gws auth login --scopes=https://www.googleapis.com/auth/presentations,https://www.googleapis.com/auth/drive.file
```

**重要**：**不要**用 `--preset recommended` 或類似參數。`recommended`
preset 會拉一組包含 `drive`（full）和 `userinfo.email` 的 scope 清
單，而 Testing mode 的 consent screen 只允許特定 scope 組合，會踩
`invalid_scope`。**只寫明確的兩個 scope URL**（least-privilege，
TECH-SPEC §4.4）。

接著瀏覽器流程：

1. Terminal 顯示一個 URL，並自動開啟瀏覽器
2. 瀏覽器跳到 Google 登入 / 選帳號頁面，選 §A3 / §B3 加進 Test users
   的那個 Gmail
3. 看到「**Google hasn't verified this app**」警告頁 → **這是正常
   的**，因為你本來就沒申請 production 審核
4. 點左下 **Advanced**
5. 點 **Go to slides-toolkit (unsafe)**（文字會是你在 §A2 / §B2 填的
   App name）
6. 看到 scope 清單：
   - `See, edit, create, and delete only the specific Google Drive
     files you use with this app`（drive.file）
   - `See, edit, create, and delete all your Google Slides
     presentations`（presentations）
7. 點 **Continue** → **Allow**
8. 瀏覽器顯示「Authentication successful, you can close this tab」
9. Terminal 顯示 `Login successful` 或類似訊息

**✅ 驗證**（交給 §L4）。

**❌ 常見錯誤**：
- `invalid_scope` → 用了 `recommended` preset；改用明確的兩個 scope
  URL
- `invalid_client` → §L2 env var 未 export / env.sh 未 source；回 §L2
- `403 access_denied` → 你登入的 Gmail **不在** Test users 清單；回
  §A3 / §B3 加進去
- 點 **Back to safety** 取消了 → 重跑 `gws auth login`
- Callback 卡住 → 瀏覽器視窗被關、或防火牆擋 loopback；重跑 `gws
  auth login`，確認 `127.0.0.1` 可通

## §L4. 驗 `gws auth status`

**為什麼要做**：確認 refresh token 已存進 Keychain / file backend，
下次呼叫不會再跳 OAuth。

**操作**：

```bash
gws auth whoami
gws auth status
```

**✅ 驗證**：

```bash
$ gws auth whoami
your_email@gmail.com

$ gws auth status
Backend: keychain          # 或 file（見 SKILL.md §Workarounds）
Token valid: true
Expires in: 6d 23h 58m     # 7 天硬邊界（Testing mode）
```

**❌ 常見錯誤**：
- `gws auth whoami` 沒回 email → 回 §L3 重登
- Backend = file（而非 keychain）→ macOS Keychain silent fail，已自動
  fallback；閱讀 SKILL.md §Workarounds Keychain 段即可，非錯誤
- Expires in 顯示負值 → 7 天已過，跑 `gws auth login` re-auth（見
  SKILL.md §Every 7 days maintenance）

---

## 完成判準

```bash
gws auth whoami
# 回傳你的 Gmail = ✅ 設定完成
```

接著可以走 `google-slides-builder` skill 跑第一份 deck。若 whoami 沒
回傳或報錯，回 `checklists/setup-state.md` 逐項 diagnose。

## 預估總時間

| 路徑 | 段落 | 預估 |
|---|---|---|
| **Path A** | §A1 auto-setup.sh（含 gcloud 首次裝） | 3–4 分鐘 |
| | §A2–A4 Console 手動（Audience + Clients）+ 瀏覽器 OAuth × 1 | 2–3 分鐘 |
| | §L1–L4 Local | 1–2 分鐘 |
| | **Path A 合計** | **~6–8 分鐘** |
| **Path B** | §B1–B6 Console 手動 6 步 | 7–10 分鐘 |
| | §L1–L4 Local | 2–5 分鐘 |
| | **Path B 合計** | **~10–15 分鐘**（KR2 目標 ≤ 20 分鐘） |

下次設定新機器可直接跳到 §L2（復用現有 GCP project / OAuth Client /
Enabled APIs，只需重跑 bootstrap + re-auth）。
