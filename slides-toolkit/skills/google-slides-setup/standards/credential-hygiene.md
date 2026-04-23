# Credential Hygiene — google-slides-setup

> Applies to：`slides-toolkit` plugin，特別是 Google Slides backend
> 處理的 OAuth Client Secret、refresh token、env var workaround。
> Baseline：OWASP ASVS v5.0.0 L1（`app-security-standard.md`）；
> 本 standards 為該 baseline 對 slides-toolkit 的專案化細則，不取代
> 上位 standard。

## 五條硬規則（non-negotiable）

### 規則 1 — Skill repo 絕不儲存任何 credential

**Repo 只放 code + docs + 測試 fixture（不含真實值）。**

禁止進入任何 commit 的項目：

- `client_secret.json`（包含 OAuth Client ID + Client Secret）
- `token.json` / `keyring-file.json`（refresh token）
- `env.sh`（含 `GOOGLE_WORKSPACE_CLI_CLIENT_ID/SECRET` 明文）
- 任何 `SHA256SUMS` 以外的 `~/.config/gws/` 下檔案
- 真實 Drive ID、真實帳號 email（個資）混入 `tests/fixtures/`

**Because**：ASVS V13（Configuration）+ V14（Data Protection）—— secrets
不得存在於 source code / build artifacts / logs。即使是 private repo，
也會經 backup / CI runner / mirror / clone 發散。

### 規則 2 — 使用者 credential 統一放 `~/.config/gws/`

所有使用者端 credential **只允許**放在 `~/.config/gws/`：

```
~/.config/gws/
├── config.yaml             # non-secret; account, client_id ref
├── client_secret.json      # OAuth Client Secret（600）
├── env.sh                  # issue #119 workaround env vars（600）
└── keyring-file.json       # refresh token，僅 Keychain fallback 時（600）
```

權限要求：

- `~/.config/gws/` 目錄：`700`
- 所有檔案：`600`

**Because**：(a) 集中管理 = incident response 時清除範圍明確（
[§Incident response](#incident-response)）；(b) 與 gws CLI 官方慣例一
致；(c) home-dir scope 符合 macOS 單一使用者假設 + ASVS V14
secrets-at-rest。

### 規則 3 — `.claude/settings.json` deny rule

加入 Claude Code 的 `settings.json`，防止 Claude 意外讀到 credential
並把內容帶入 context（一旦進 context = 有機會流到 model provider
logs、被摘要、被 commit）：

```json
{
  "permissions": {
    "deny": [
      "Read(~/.config/gws/**)",
      "Read(~/.cache/slides-toolkit/bin/.version)",
      "Bash(cat ~/.config/gws/*)",
      "Bash(cat ~/.config/gws/**)",
      "Bash(cp ~/.config/gws/* *)",
      "Bash(git add ~/.config/gws/*)",
      "Write(~/.config/gws/**)"
    ]
  }
}
```

7 條 pattern 涵蓋：

1. `Read(~/.config/gws/**)` — 禁止 Claude Read tool 直接讀 credential
2. `Read(~/.cache/slides-toolkit/bin/.version)` — 版本檔有時會被 Claude
   當成「no-harm metadata」去讀；事實上 SHA-256 pin 無 secret，但限讀減少 surface
3. `Bash(cat ~/.config/gws/*)` — 禁止透過 `cat` 讀 credential
4. `Bash(cat ~/.config/gws/**)` — `**` 全路徑涵蓋子目錄
5. `Bash(cp ~/.config/gws/* *)` — 禁止 `cp` 複製 credential 出 `~/.config/gws/`
6. `Bash(git add ~/.config/gws/*)` — 最後一道防線：即使誤放入 repo，
   `git add` 也被擋
7. `Write(~/.config/gws/**)` — 禁止 Claude Write tool 誤寫覆蓋；gws 本
   身寫 credential 經 shell script 外部跑，不經 Claude Write，不受影響

**Because**：ASVS V14（secrets-at-rest）+ V16（logs 不含 secret）。
Claude Code context 實務上是 log surface 之一，deny rule 是便宜有效
的預防措施。

### 規則 4 — `.gitignore` pattern

Plugin root `.gitignore` 必含：

```gitignore
# credentials — never commit（repo-relative pattern only）
.config/gws/
*/keyring-file.json
*/env.sh
# Note: home-dir credential files (~/.config/gws/**) cannot be
# protected by .gitignore (git uses repo-relative paths only and
# does not expand ~). Home-dir credential read access is blocked by
# the settings.json deny rule in §規則 3.

# binary cache
.cache/slides-toolkit/

# runtime artifacts (tests fixtures with real IDs/paths)
tests/fixtures/*.drive_id.txt
tests/fixtures/*.local

# macOS
.DS_Store
```

**重要**：`.gitignore` 使用 repo-relative pattern，**不展開 `~`**。
home-dir 下的 credential（實務上全部都在 `~/.config/gws/`）**不受
`.gitignore` 保護** —— 那是靠**規則 3 的 settings.json deny rule**。

**Because**：責任單一化 —— repo-relative 靠 `.gitignore`、home-dir
靠 `settings.json`，不混淆「.gitignore 有寫就安全」。對齊 TECH-SPEC §8.2。

### 規則 5 — macOS 優先 Keychain；Linux/CI 才降級 file backend

Keychain 是 macOS 原生加密 credential 存儲，安全性高於明文檔案。

- **Personal macOS machine**：**不得** 主動設 `KEYRING_BACKEND=file`。
  保持 Keychain 預設。
- **Keychain silent fail**：`scripts/google-slides/credential-check.sh`
  偵測到 Keychain 寫入成功但讀不到時，**自動** fallback 到 file backend
  並寫 `export KEYRING_BACKEND=file` 到 `~/.config/gws/env.sh`。此為
  technical workaround，非一般情況。
- **Linux / CI**（Phase 2+）：Keychain 不存在，可明確使用 file backend。
  進入 Phase 2+ 時重新評估 ASVS 需求（可能升 L2 要求）。

**Because**：Keychain vs file backend 的 ASVS V14 差距是「硬體/作業系
統 crypto vs file-system permission」—— 明文檔（即使 chmod 600）在機
器被物理取得時較容易被讀出。MVP 只支援 macOS，就用 Keychain；除非
silent fail 才降級。

## 敏感度分級

對照 TECH-SPEC §2.4 外部依賴與 §4.8 credential flow：

| 物件 | 敏感度 | 洩漏後果 | 處理優先序 |
|---|---|---|---|
| OAuth Client Secret（`client_secret.json` 內 `installed.client_secret`） | 🔴 高 | 攻擊者可冒用你的 OAuth Client 開 consent screen 騙 Test users；雖然 consent screen 仍限 Test users，但會嚴重混淆 incident 範圍 | 立即 revoke + rotate |
| Refresh token（Keychain 或 `keyring-file.json`） | 🔴 高 | 攻擊者可在 7 天 TTL 內無 consent 存取你的 Slides / Drive.file | 立即 `gws auth logout` + Keychain/file 清除 |
| `env.sh`（含 Client ID + Secret 明文） | 🔴 高 | 等同 Client Secret 洩漏 | 立即 delete + rotate |
| `client_secret.json` 內的 `installed.client_id` | 🟡 中 | 單獨 Client ID 無法 auth；配 Secret 才危險 | 視 Secret 狀態處理 |
| `gws` binary 本身 + SHA-256 pin | ⚪ 低 | 公開資源；SHA-256 pin 是 integrity control，非 secret | 無 |
| `registry.md` 內 Drive ID（若 template 本身非機密） | ⚪ 低 | Drive ID 仍需 scope 才能存取；洩漏本身不授權 | 無 |
| Google 帳號 email | 🟡 中 | 個資 + phishing 攻擊面；不建議入 repo | 以 placeholder 取代 |

分級對應原則：🔴 = 即時啟動 incident response；🟡 = 視上下文判斷；
⚪ = 無需特別處理但避免不必要曝光。

## Incident response

發現 credential 已 commit / push / 外洩時：

### Step 1 — 立即 revoke

打開 https://console.cloud.google.com → APIs & Services → Credentials
→ 刪除該 OAuth Client ID。**不要**只是「暫停」——直接刪，才能確保
舊 Client Secret 無法再換 refresh token。

### Step 2 — 建立新 OAuth Client

回到 `protocols/gcp-console-walkthrough.md` §4–§5 重新建立 Desktop
app 類型的 OAuth Client + 下載新 `client_secret.json`。

### Step 3 — 清除舊 token

```bash
gws auth logout
# Keychain 清除（若有用）：
security delete-generic-password -s gws-cli 2>/dev/null
# file backend 清除（若有用）：
rm -f ~/.config/gws/keyring-file.json ~/.config/gws/env.sh
```

### Step 4 — 重新 auth

依 `protocols/gcp-console-walkthrough.md` §7–§10 重跑。

### Step 5 — 若已 commit 到 git

**清 git 歷史**（destructive ops，需 kouko 明確確認後再執行）：

```bash
# 使用 git-filter-repo（推薦，新版工具）；git filter-branch 已 deprecated
git filter-repo --path <leaked-file> --invert-paths

# 若已 push 到遠端：
git push --force-with-lease origin <branch>
```

**不要**只用 `git rm --cached <file>` —— 那只清當前 HEAD，歷史仍殘。

**通知所有 clone / fork 過的協作者** rebase 或重 clone。

### Step 6 — Rotate 衍生資源

7 天內有被使用到的任何 Google 資源，檢查 audit log（Google Cloud
Console → Logging）確認無可疑存取。雖然 MVP scope 最小（只有
`presentations` + `drive.file`），仍需檢查。

### Step 7 — 寫 incident log

建立 `plugins/slides-toolkit/incidents/YYYY-MM-DD-<short-description>.md`
（目錄採 on-demand 建立，對齊 TECH-SPEC §2.1、§8.4）。內容含：

- 發現時間 / 發現方式（grep? GitHub secret scan alert?）
- 洩漏 vector（e.g. 誤 commit `client_secret.json`）
- 影響範圍（token TTL 內可能被利用時窗）
- Revoke + rotate 時間點
- Root cause（例：規則 3 settings.json deny rule 未套用）
- 預防改善（e.g. 加 pre-commit hook `gitleaks protect --staged`）

**不得**在 incident log 內寫入實際 secret（Meta-rule：incident log 本
身也是 ASVS V16 audit surface，不能又再次洩漏）。

## OWASP ASVS v5.0.0 L1 對應

本 standards 觸及的 ASVS L1 verification 項（對齊
`app-security-standard.md` 與 TECH-SPEC §8.6）：

| ASVS chapter | 本 standards 對應 |
|---|---|
| **V1** Encoding & Sanitization | OAuth scope 最小化（least-privilege：`presentations` + `drive.file`，不要 `drive` full、`userinfo.email`）；UTF-8-only pipeline 避免 mojibake 造成 injection surface |
| **V13** Configuration | 規則 5（Keychain 優先 + file backend 降級判斷）；binary SHA-256 pin 屬 secure defaults + dependency integrity |
| **V14** Data Protection | 規則 1（repo 無 secret）+ 規則 2（集中 `~/.config/gws/` chmod 600）+ 規則 4（`.gitignore`）+ 規則 3（`settings.json` deny rule 阻擋 Claude 讀）= secrets-at-rest 多層防護 |
| **V16** Security Logging & Error Handling | Incident response 寫 `incidents/` 但不含 secret；exit code 表（TECH-SPEC §4.2）不把 token 值印到 stderr |

**Because**：ASVS L1 是個人 / 內部工具的合理 baseline（
`app-security-standard.md` §Default Tier）。slides-toolkit 處理個人
OAuth credential、非 PCI / HIPAA / 金融資料，L1 足夠；若 Phase 2+
publish 給外部多使用者，重新評估是否升 L2。

## 相關檔案

- `app-security-standard.md`（code-team standards，上位 ASVS 錨定）
- TECH-SPEC §4.8 — credential flow 詳圖
- TECH-SPEC §8.1 — settings.json deny rule 完整清單
- TECH-SPEC §8.2 — `.gitignore` pattern 完整清單
- TECH-SPEC §8.4 — incident response playbook（本 standards 細化版）
- TECH-SPEC §8.6 — ASVS L1 mapping（本 standards 延伸）
- `protocols/gcp-console-walkthrough.md` §5 — `client_secret.json` chmod 600
- `protocols/issue-119-workaround.md` — env var workaround 與 `env.sh` 的 chmod
