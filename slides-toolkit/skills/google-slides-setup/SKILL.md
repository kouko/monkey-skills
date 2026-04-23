---
name: google-slides-setup
description: First-time Google Slides backend onboarding for slides-toolkit — GCP Console OAuth setup, gws CLI bootstrap, issue #119 workaround, and credential hygiene. 使用時機：第一次用 gws / 看到 401 403 auth / invalid_scope / invalid_client / 重新跑 setup / state detection 判斷要補哪一步。MVP 只處理個人 @gmail.com（macOS）；Google Workspace 企業帳號 Phase 2+。
---

# google-slides-setup

一次性把機器設定好，讓 `google-slides-builder` 可以呼叫 gws CLI 操作
Google Slides。MVP scope = 個人 `@gmail.com` + macOS；Workspace 企業
帳號與 Linux / CI 屬 Phase 2+。

## When to use

呼叫本 skill 的四個時機：

1. **首次設定** — 全新機器 / 全新 Google 帳號，還沒有 `~/.config/gws/`
2. **憑證過期** — 距離上次 `gws auth` 已超過 7 天（Google External +
   Testing policy 硬邊界；見 [Every 7 days maintenance](#every-7-days-maintenance)）
3. **Auth error** — `google-slides-builder` 回傳 exit code 10 / 16 /
   18，或 stderr 出現 `401` / `403` / `invalid_scope` / `invalid_client`
4. **State detect** — 不確定目前狀態（binary 裝了沒？token 還有效嗎？）
   先跑 `scripts/google-slides/credential-check.sh`，依回傳 JSON 決定分支

## Prerequisites

| 項 | 要求 | 備註 |
|---|---|---|
| OS | macOS (darwin-arm64 或 darwin-x86_64) | MVP 唯一支援平台；Linux / WSL 屬 Phase 2+ |
| Shell | zsh 或 bash | 預設 macOS zsh 即可 |
| 網路工具 | `curl` | macOS 預裝 |
| 瀏覽器 | Chrome 或 Safari | 一次性 GCP Console 操作用 |
| Google 帳號 | 個人 `@gmail.com` | Workspace 企業帳號 Phase 2+ |
| 密碼管理 | macOS Keychain 可用（預設） | Keychain silent fail 時自動 fallback 到 file backend，見 [Workarounds](#workarounds) |

**不需要**：Python、uv、gcloud、brew、npm。所有 binary (`gws`, `jq`)
由 `scripts/google-slides/bootstrap.sh` 自抓至 `~/.cache/slides-toolkit/bin/`
並做 SHA-256 驗證（TECH-SPEC §2.3）。

## Workflow overview

```
  [Start]
     │
     ▼
┌─────────────────────────────┐
│ State detection             │   ← 必跑第一步
│ credential-check.sh         │
└──────────┬──────────────────┘
           │ JSON: {backend, token_valid, expires_in_sec}
           ▼
 ┌─────────┴──────────────┬──────────────────────┬─────────────────┐
 │ binary 缺              │ binary 有 / 未 auth   │ token 過期       │ 全部就緒
 ▼                        ▼                      ▼                  ▼
 [Setup flow] 10 步        [從 Setup step 8 起]    [Re-auth only]     [結束]
 ├─ Console 6 步           ├─ env var workaround   ├─ gws auth 重登
 └─ 本機 4 步              └─ gws auth login       └─ 10 秒搞定
```

詳細分支對照：`checklists/setup-state.md`。

## State detection

**先跑 state detect，再決定進哪條分支。**不要盲衝 setup flow。

```bash
bash scripts/google-slides/credential-check.sh
```

預期 JSON 輸出：

```json
{"backend":"keychain","token_valid":true,"expires_in_sec":518400}
```

依結果分支：

| 回傳 | 分支 | 進入點 |
|---|---|---|
| `credential-check.sh` 本身找不到 / `~/.cache/slides-toolkit/bin/` 空 | 全新機器 | Setup flow step 1 |
| `backend=keychain`, `token_valid=true`, `expires_in_sec > 0` | 全部就緒 | 直接跑 `google-slides-builder` |
| `backend=keychain`, `token_valid=false` 或 `expires_in_sec <= 0` | 過期 | [Every 7 days maintenance](#every-7-days-maintenance) |
| `backend=file` | Keychain silent fail，已 fallback | 繼續，但請閱讀 [Workarounds](#workarounds) Keychain 段 |
| exit 18 | Keychain 不可讀 + file backend 也失敗 | 重跑 Setup step 3（Client Secret 下載）與 step 8–9 |

完整檢查清單：`checklists/setup-state.md`。

## Setup flow

總共 **10 步**，拆成兩段：6 步瀏覽器 Console 操作 + 4 步本機命令。

**完整逐步 tutorial**：`protocols/gcp-console-walkthrough.md`（預估 10–15 分鐘）

| # | 地點 | 做什麼 | 出錯時回到 |
|---|---|---|---|
| 1 | 瀏覽器 | Create GCP project | walkthrough §1 |
| 2 | 瀏覽器 | OAuth consent screen → External + Testing | walkthrough §2 |
| 3 | 瀏覽器 | Add yourself as Test user（**漏這步 = 403**） | walkthrough §3 |
| 4 | 瀏覽器 | Create OAuth 2.0 Client ID → **Desktop app**（不是 Web） | walkthrough §4 |
| 5 | 瀏覽器 | Download `client_secret.json` → `~/.config/gws/` | walkthrough §5 |
| 6 | 瀏覽器 | Enable APIs：Google Slides API + Google Drive API | walkthrough §6 |
| 7 | Terminal | `bash scripts/google-slides/bootstrap.sh`（抓 gws + jq） | walkthrough §7 |
| 8 | Terminal | Export issue #119 env vars（見下節） | `protocols/issue-119-workaround.md` |
| 9 | Terminal | `gws auth login -s presentations,drive.file`（**不要用 `recommended` preset**） | walkthrough §9 |
| 10 | 瀏覽器 | 同意頁面 → Advanced → Go to app (unsafe) → Approve | walkthrough §10 |

**完成判準**：

```bash
gws auth whoami
# 預期輸出：your_email@gmail.com
```

## Workarounds

### Issue #119（個人 Gmail invalid_scope / invalid_client）

gws CLI 內建 OAuth client 對個人 `@gmail.com` 帳號會踩 `invalid_scope`
或 `invalid_client`。解法：export 自建 OAuth Client 的 ID + Secret 為
env var，gws 會改用它。

快速命令（完整版 + 寫入 shell profile 步驟見 `protocols/issue-119-workaround.md`）：

```bash
export GOOGLE_WORKSPACE_CLI_CLIENT_ID=$(jq -r .installed.client_id ~/.config/gws/client_secret.json)
export GOOGLE_WORKSPACE_CLI_CLIENT_SECRET=$(jq -r .installed.client_secret ~/.config/gws/client_secret.json)
```

或用 `scripts/google-slides/env-guard.sh`：

```bash
bash scripts/google-slides/env-guard.sh check   # 偵測是否需要 workaround
bash scripts/google-slides/env-guard.sh apply   # 寫入 ~/.config/gws/env.sh (chmod 600)
```

追蹤上游修復：`googleworkspace/cli` issue #119（TODO：填入 upstream 討論連結）。

### macOS Keychain silent fail（fallback 到 file backend）

gws 預設把 refresh token 寫進 macOS Keychain，但偶爾會在特定 profile
狀態下 silent fail（寫入看似成功、下次讀不到）。`credential-check.sh`
偵測到此情況會自動 fallback：

```bash
export KEYRING_BACKEND=file
```

Token 改存 `~/.config/gws/keyring-file.json`（chmod 600，`.gitignore`
已擋）。與 Keychain 的差異：安全等級略降（明文檔案 vs Keychain 加
密），但在**個人機器 + home 目錄權限正確**的前提下，ASVS V14 L1 可接受。

**不要在 personal machine 預設設 `KEYRING_BACKEND=file`** —
`standards/credential-hygiene.md` 規則 5。

## Credential hygiene

本 skill 處理的都是敏感 credential。**必讀**：`standards/credential-hygiene.md`

五條硬規則（摘要）：

1. Skill repo 絕不儲存任何 credential（repo 只放 code + docs）
2. 使用者 credential 統一放 `~/.config/gws/`（由 gws 管）
3. `.claude/settings.json` deny rule 防止 Claude 讀 credential 進 context
4. `.gitignore` pattern 防止誤 commit
5. macOS 優先 Keychain；Linux/CI 才降級 file backend

洩漏 incident response playbook 與 ASVS v5.0.0 L1 mapping（V1 / V13 /
V14 / V16）同樣在該 standards 檔。

## Every 7 days maintenance

**Google External + Testing mode refresh token 壽命 = 7 天**（Google
OAuth policy 硬邊界，MVP 不申請 production 過審，故無法繞）。

每 7 天（或看到 exit 10 `token expired`）跑一次：

```bash
gws auth login -s presentations,drive.file
# 瀏覽器跳出 → 同意 → 回 callback
# 10 秒搞定
```

**不需要重跑 setup flow**，Client Secret 與 OAuth Client 仍有效，只是
refresh token 過期。

**Passive 告知策略（TECH-SPEC §6.3）**：`google-slides-builder`
pre-flight 偵測到 token 過期會 exit 10，Claude 讀到此 exit code 自動
提示 re-auth，而非每次主動 prompt 打斷使用者。

## Error messages guide

| 訊息 / 狀態 | 根因 | 回到 |
|---|---|---|
| `401 Unauthorized` | token 過期或未 auth | [Every 7 days maintenance](#every-7-days-maintenance) |
| `403 Forbidden` + `access_denied` | 你的 Gmail 不在 Test users | walkthrough §3（Add test user） |
| `403 Forbidden` + `API not enabled` | Slides / Drive API 未啟用 | walkthrough §6 |
| `invalid_scope` | gws 內建 client 對個人 Gmail 不認 scope | [Issue #119 workaround](#issue-119個人-gmail-invalid_scope--invalid_client) |
| `invalid_client` | Client ID / Secret 未 export，或 `client_secret.json` 缺 | walkthrough §5、§8 |
| `Google hasn't verified this app` | 正常；點 Advanced → Go to app (unsafe) | walkthrough §10 |
| exit 17 `SHA-256 mismatch` | binary 校驗失敗（可能網路受攻擊 / release 變動） | 確認網路，重跑 bootstrap；若持續，檢查 upstream release + SHA256SUMS |
| exit 18 `Keychain unavailable and file-backend also failed` | Keychain 權限異常 + `~/.config/gws/` 權限異常 | 檢查 `~/.config/gws/` 是否 chmod 600，重跑 Setup step 8–9 |
| `gws auth login` 卡住在 localhost callback | 防火牆擋 loopback，或瀏覽器視窗已關 | 重跑 step 9；確認 127.0.0.1 可通 |

## Checklist

每次跑完 setup，用 `checklists/setup-state.md` 的 6 項 state check 自
驗一遍：(1) gws binary / (2) jq binary / (3) gcloud 可選 /
(4) `client_secret.json` 存在 / (5) issue #119 env vars /
(6) `gws auth whoami` 回傳 email。任一項失敗 → checklist 會指向
`gcp-console-walkthrough.md` 對應步驟。

## References

- `protocols/gcp-console-walkthrough.md` — 完整 10 步 tutorial
- `protocols/issue-119-workaround.md` — gws 個人 Gmail workaround 詳解
- `standards/credential-hygiene.md` — 5 條硬規則 + incident response + ASVS L1 mapping
- `checklists/setup-state.md` — 6 項 state check
- 上游 TECH-SPEC：`plugins/slides-toolkit/TECH-SPEC.md` §3.2, §4.2, §6.1, §6.2, §8
- 上游 PRODUCT-SPEC：`plugins/slides-toolkit/PRODUCT-SPEC.md` §6.3.3 risks
