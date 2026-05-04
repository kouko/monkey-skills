# Google OAuth Automation Limits — 什麼不能自動化，以及為什麼

截至 2026-04-24，Google 的 OAuth policy 硬性限制了 slides-toolkit（或任何第三方 CLI 工具）的自動化範圍。本文件整理這些邊界與**原始證據**。

## 能自動化的部分 ✅

透過 `gcloud` / gws / REST API 可以：

1. **GCP project 建立** — `gcloud projects create`
2. **Project API 啟用** — `gcloud services enable`
3. **OAuth consent screen branding** — `oauth2.googleapis.com/v1/projects/{id}/brands` REST API（gws `setup.rs` 內 `configure_consent_screen()` 用這個）
4. **OAuth consent screen 的 User Type 設定**（External / Internal）— 同上 brands API
5. **Binary 下載 + 安裝**（gws / jq）— 我們自己的 `bootstrap.sh`
6. **Credential 處理**（搬 client_secret.json / 寫 env.sh / chmod）

## 不能自動化的部分 ❌

### 1. OAuth Client ID（Desktop app）建立

**症狀**：嘗試 `gws auth setup` 時 error：
```
OAuth client creation requires manual setup in the Google Cloud Console.
```

**根因 — gws source 註解**（line 913, `crates/google-workspace-cli/src/setup.rs`）：
```rust
// (create_oauth_client removed due to IAP Admin APIs deprecation)
```

翻譯：gws 原本**有**自動建 OAuth client 的實作，但因 Google 的 **IAP OAuth Admin API 在 2025-01-22 deprecated**，該實作被主動移除。

**Google deprecation 公告**：<https://docs.cloud.google.com/iap/docs/deprecations/migrate-oauth-client>

**嘗試過的繞路**：
- `gcloud alpha iap oauth-brands` — 同一組 API，已 deprecated（2025-01-22）
- `gcloud alpha iap oauth-clients` — 同上
- 其他 Google API：**沒有 replacement API**

### 2. Test User 加入（OAuth consent screen → Audience）

**現況**：完全無 API。必須 Console UI 手動。

**原因推測**：test user list 是 Google 反濫用機制的一環 — 如果開 API，惡意 script 可以靜默把任意 gmail 加進某個 app 的 consent 白名單，配合釣魚手段提權。Google 選擇保留這個摩擦作為 anti-abuse gate。

**實測踩坑成本**：漏加 test user → OAuth flow 時報 `403 access_denied`，錯誤訊息不特別指向「加 test user」這個解法。新手容易卡 15 min+。

### 3. `client_secret.json` Download

**現況**：OAuth client 建立成功後，Console UI 會彈出對話框含 client_id + client_secret + Download 按鈕。**secret 只在這個對話框揭示一次**；之後任何 API / Console 操作都拿不到 raw secret（只能看到遮罩版）。

**嘗試過的繞路**：
- 沒有 `gcloud` / REST API 可以 retrieve secret after creation
- 若錯過對話框：只能 **刪掉 client + 重建**

### 4. gcloud ADC passthrough 請求 user-sensitive scope

**測試**：我們嘗試用 gcloud 的 built-in OAuth client 向個人帳戶請求 `presentations` + `drive.file` scope（`gcloud auth application-default login --scopes=...`）。

**結果**：瀏覽器顯示：
> **系統已封鎖這個應用程式**
> 這個應用程式嘗試存取您 Google 帳戶中的機密資訊。為保護您的帳戶，Google 已阻擋這個存取行為。

**根因**：OAuth client 的 scope 存取能力是 **per-client verified**。gcloud 的 built-in client 雖然是 Google 官方，但只對 **Cloud Platform 類 scope**（cloud-platform / compute / sqlservice / appengine 等）做過 verification。它沒有對 `presentations` / `drive.file` / `gmail.*` 等 **user-sensitive scope** 做 verification，因此 Google 的反濫用機制會 block。

**意涵**：即使 Google 自家 gcloud 都不能隨意借用 scope，第三方工具（gws / slides-toolkit）更不可能。**使用者必須自建 OAuth client + 自行通過 Testing mode 或 Production verification**。

## Testing mode 的硬限制

若使用者的 OAuth client 停留在 **External + Testing mode**（個人 @gmail 唯一可行模式），Google 施加：

1. **100 test user hard cap** — 每個 consent screen 最多 100 個 test user；超過需升 Production + verification
2. **7 天 refresh token expiry** — 非最小 scope（openid / email / profile）請求時，refresh token 7 天過期，使用者要重新跑 `gws auth login`
3. **Unverified warning** — 同意畫面顯示「Google hasn't verified this app」，需點 Advanced → unsafe 才能繼續

這些限制**無法繞過**，只能接受或升 Production（需 verification，sensitive scope 免費 3-5 工作天；restricted scope 需 CASA audit $800-$8000）。

## 結論：slides-toolkit 的永久邊界

在 Google 不恢復 OAuth Admin API 的前提下，slides-toolkit 的 setup flow **必然包含以下 manual 步驟**：

- **Console 手動 × 2**：Audience 加 test user、Clients 建 Desktop OAuth client + Download JSON
- **瀏覽器 OAuth 同意 × 2**：gcloud auth login（若走 Path A）、gws auth login

合計使用者動作：~2-3 分鐘 interactive time。

`auto-setup.sh` 自動 6-10 步中的 5 步（detect → install gcloud → gcloud auth → project create → enable APIs → wait for JSON → install credentials → gws auth login），把使用者 cognitive load 降到最低，**但不能消除 Google policy 的硬邊界**。

## 未來 re-eval 時機

以下情境應重新評估本文件結論：

- Google 發佈新的 OAuth Admin API（IAP 的 replacement）→ 重啟 `create_oauth_client` 自動化
- gws 發現新的 undocumented API 能繞 Console → 更新 gws 後同步
- slides-toolkit 決定 publish 給多人 → 考慮送 sensitive scope verification，走 Production mode 免除 test user + 7 天限制
- Google 把 Workspace 個人帳戶升級成支援 Organization（目前只有付費 Workspace 有）

## 來源

- [IAP OAuth Admin API deprecation](https://docs.cloud.google.com/iap/docs/deprecations/migrate-oauth-client) — 2025-01-22 公告
- [Manage App Audience](https://support.google.com/cloud/answer/15549945) — 100 cap + 7 天 refresh 政策
- [When verification is not needed](https://support.google.com/cloud/answer/13464323) — 個人自用豁免
- gws source `setup.rs:913` — `create_oauth_client removed due to IAP Admin APIs deprecation` 註解（via GitHub Explore 研究 2026-04-24）
- Implementation journal `implementation-journal-2026-04-24.md` Phase 4 — ADC passthrough 實測被擋
