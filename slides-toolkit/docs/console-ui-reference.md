# Google Cloud Console UI Reference — 2026-04

截至 2026-04-24，Google Cloud Console 的 OAuth / credential 管理介面已從舊版 "APIs & Services" 分拆到獨立的 **Google Auth Platform**。此文件記錄新 UI 導航對照，供 walkthrough 維護用。

## 舊 UI vs 新 UI 對照

| 舊 UI（pre-2026） | 新 UI（2026-04+） |
|---|---|
| APIs & Services → OAuth consent screen | **Google Auth Platform → Branding** |
| （OAuth consent screen 內子區塊 "Test users"） | **Google Auth Platform → Audience → Test users section** |
| APIs & Services → Credentials | **Google Auth Platform → Clients** |
| + CREATE CREDENTIALS → OAuth client ID | **Clients → + Create client** |
| APIs & Services → Library → Enable API | **APIs & Services → Library → Enable**（這部分不變）|
| APIs & Services → Enabled APIs & services | **APIs & Services → Enabled APIs & services**（不變）|

## 新 UI 分頁結構

**Google Auth Platform** 底下的 6 個分頁：

| 分頁 | URL 路徑 | 用途 |
|---|---|---|
| Overview | `/auth/overview?project=<id>` | 頁面儀表板 + Get Started 引導 |
| **Branding** | `/auth/branding?project=<id>` | App name / User support email / Developer contact / logo |
| **Audience** | `/auth/audience?project=<id>` | User Type（External/Internal）+ Publishing status + **Test users**（同頁區塊） |
| **Clients** | `/auth/clients?project=<id>` | OAuth 2.0 Client IDs 管理 + Create client |
| Data Access | `/auth/dataaccess?project=<id>` | Scopes 管理（宣告 app 會使用哪些 scope） |
| Verification Center | `/auth/verification?project=<id>` | Sensitive / Restricted scope verification 送審介面 |

## Path 重點

### 建 OAuth Client（Desktop）

1. `/auth/clients?project=<id>`
2. `+ Create client`
3. Application type: **Desktop app**（**不是** Web / Mobile / UWP）
4. Name: 任意（建議 `slides-toolkit-cli`）
5. Create → 彈出「OAuth client created」對話框
6. **Download JSON** 按鈕（secret 只在此對話框揭示，錯過要重建）

### 加 Test User

**易混淆**：新 UI 沒有獨立「Test users」分頁。

1. `/auth/audience?project=<id>`
2. **往下捲**到 **Test users** 區塊
3. `+ Add users`
4. 輸入 gmail（必須和後續 `gws auth login` 用同一帳號）
5. Save

若顯示「No test users added yet」= 還沒加；加完列表會顯示該 gmail。

### Enable APIs（這部分 UI 沒變）

1. `/apis/library?project=<id>`
2. 搜尋 `Google Slides API` → 點進去 → **Enable**
3. 重複：`Google Drive API` → Enable

或命令列（更快）：
```bash
gcloud services enable slides.googleapis.com drive.googleapis.com --project=<id>
```

### OAuth Consent Screen 首次設定

1. `/auth/overview?project=<id>` → 通常看到 "Get Started" 卡片
2. 填 Branding + Audience 資訊（一次問完）：
   - App name
   - User support email
   - Audience: **External**（個人 Gmail 唯一選項，沒有 Organization）
   - Developer contact email
3. 後續若要修改 Branding / Audience 分開進分頁改

## URL `<PROJECT_ID>` 替換模板

walkthrough 文件引用 Console URL 時，統一用 `<PROJECT_ID>` placeholder，讓使用者 `s/<PROJECT_ID>/slides-toolkit-260424/`（或自己的 project ID）。

```
https://console.cloud.google.com/auth/overview?project=<PROJECT_ID>
https://console.cloud.google.com/auth/branding?project=<PROJECT_ID>
https://console.cloud.google.com/auth/audience?project=<PROJECT_ID>
https://console.cloud.google.com/auth/clients?project=<PROJECT_ID>
https://console.cloud.google.com/apis/library?project=<PROJECT_ID>
https://console.cloud.google.com/apis/dashboard?project=<PROJECT_ID>
```

## 已知陷阱

### 「Publish App」按鈕 — 不要按

`/auth/overview` 頁面可能會顯示 `PUBLISH APP`（把 Testing 升 Production）。對個人自用 skill **不要按**：
- Production 模式下 sensitive scope 需送 verification（3-5 工作天）
- Restricted scope 需 CASA audit（$800-$8000）
- 個人 Gmail 工具走 Testing 完全合法且 Google 官方 sanctioned（見 `google-oauth-automation-limits.md` §Testing mode 硬限制）

若誤按 → 點 `BACK TO TESTING` 退回。

### Application type 選錯 → 之後踩 invalid_redirect_uri

Clients → Create client 時必選 **Desktop app**。選到 Web app 會在 `gws auth login` 時報：
```
invalid_redirect_uri
```
解法：刪掉錯的 client、重建、選 Desktop。

### Organization 沒選 No organization（個人 Gmail）

建 project 時 "Organization" 欄位若誤選了什麼（個人 Gmail 本來就沒 org，正常應只有 "No organization" 可選），後續 Audience 可能變得只能選 Internal → 個人帳號反而卡住。

## UI 變動歷史（已知）

| 時間 | 變動 |
|---|---|
| ~2026-Q1 | OAuth consent screen 拆成 Branding / Audience；Credentials 改名 Clients |
| 2025-01-22 | IAP OAuth Admin API deprecated → `gws auth setup` 失去自動建 client 能力 |
| 持續 | API library UI 小幅改版，但 Enable API 操作流程不變 |

本文件**僅對 2026-04 UI 有效**。若 Google 再改版，更新此文件 + 對應 walkthrough。
