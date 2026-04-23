# Issue #119 Workaround — gws 個人 Gmail OAuth

> 上游 issue：`googleworkspace/cli#119`（TODO：填入 issue URL）
> 狀態：MVP 實裝時已確認 workaround 有效；[ASSUMPTION-3]（PRODUCT-SPEC
> §3.3）。若上游修復，見本文末 [何時可移除 workaround](#何時可移除-workaround)。

## 問題背景

`gws` CLI（`googleworkspace/cli`）內建了一組 OAuth Client ID + Secret，
用來讓 `gws auth login` 在 Google Workspace tenant 下 out-of-box 可用。

但在 **個人 `@gmail.com`** + **External + Testing consent screen** 組合
下，這組內建 Client 會拋出：

- `invalid_scope` — Google 拒絕 gws 要求的 scope 清單（通常是
  `--preset recommended` 拉的那組）
- `invalid_client` — Google 不承認 gws 內建 Client 對個人 Gmail 的合
  法性（因為 Workspace tenant 的 client 不能跨 tenant 使用）

## 根因

gws 預設 OAuth 流程設計面向 **Google Workspace tenant**（有
Admin Console、有公司 domain、有被 Admin 授權的 internal app）。
個人 `@gmail.com` 的 unverified External consent screen 不在這條路
徑上 —— Google 會把「Workspace tenant client × 個人 Gmail user」視
為跨 tenant 非法使用。

對 gws 團隊來說這不是 bug，是設計目標客群（Workspace）不包含個人
Gmail。對 kouko 來說這是硬阻塞（PRODUCT-SPEC §6.3.3 Risk：gws issue
#119，likelihood 高、impact 高）。

## Workaround

**用你自己 GCP project 建的 OAuth Client 取代 gws 內建的。**

gws 支援兩個 env var，存在時會覆寫內建 Client：

- `GOOGLE_WORKSPACE_CLI_CLIENT_ID`
- `GOOGLE_WORKSPACE_CLI_CLIENT_SECRET`

你的 Client（由 `gcp-console-walkthrough.md` §4–§5 下載的
`client_secret.json`）對你自己 GCP project 內的 OAuth consent screen
來說是「合法 first-party client」，不會踩 invalid_client；而且 scope
要什麼就要什麼（consent screen 自己定），不會踩 invalid_scope。

## 具體命令

### 一次性 export（只在當前 shell session 生效）

```bash
export GOOGLE_WORKSPACE_CLI_CLIENT_ID=$(jq -r .installed.client_id ~/.config/gws/client_secret.json)
export GOOGLE_WORKSPACE_CLI_CLIENT_SECRET=$(jq -r .installed.client_secret ~/.config/gws/client_secret.json)
```

**前置條件**：

- `~/.config/gws/client_secret.json` 存在（`gcp-console-walkthrough.md` §5）
- `jq` 在 PATH 內（`bootstrap.sh` 把 `~/.cache/slides-toolkit/bin/` 加進 PATH
  是一種作法；另一種是 alias `jq=~/.cache/slides-toolkit/bin/jq`）

### 寫入 shell profile（永久生效）

把上述兩行加到 `~/.zshrc`（zsh，macOS 預設）或 `~/.bashrc`（bash）：

```bash
# slides-toolkit — gws issue #119 workaround
if [ -f ~/.config/gws/client_secret.json ]; then
  export GOOGLE_WORKSPACE_CLI_CLIENT_ID=$(jq -r .installed.client_id ~/.config/gws/client_secret.json 2>/dev/null)
  export GOOGLE_WORKSPACE_CLI_CLIENT_SECRET=$(jq -r .installed.client_secret ~/.config/gws/client_secret.json 2>/dev/null)
fi
```

`2>/dev/null` 避免 `jq` 未裝時每次開 terminal 噴錯。

重啟 terminal 或 `source ~/.zshrc` 生效。

### 用 `env-guard.sh apply`（推薦）

讓 skill 幫你把 env var 寫進獨立的 `~/.config/gws/env.sh`（chmod
600），`scripts/google-slides/gws-wrap.sh` 每次呼叫前會 source 它：

```bash
bash scripts/google-slides/env-guard.sh apply
```

**優點**：

- 獨立檔案好管理（想移除 workaround 直接刪 `env.sh`）
- chmod 600 自動設對
- `gws-wrap.sh` 內部 source，不污染你的全域 shell profile
- 對齊 `standards/credential-hygiene.md` 規則 2（credential 集中 `~/.config/gws/`）

## 如何驗證 workaround 生效

**負驗證**（設定前跑一次）：

```bash
unset GOOGLE_WORKSPACE_CLI_CLIENT_ID GOOGLE_WORKSPACE_CLI_CLIENT_SECRET
gws auth login -s presentations,drive.file
# 預期：錯誤訊息含 invalid_scope 或 invalid_client
```

**正驗證**（設定後）：

```bash
source ~/.config/gws/env.sh   # 或重開 terminal（若寫進 profile）
gws auth login -s presentations,drive.file
# 預期：瀏覽器開啟 consent screen；完成後 `gws auth whoami` 回 email
```

或者用 `env-guard.sh check`：

```bash
bash scripts/google-slides/env-guard.sh check
# 預期：{"workaround_needed":false}  ← 代表已生效
# 若回 {"workaround_needed":true} 代表尚未 export，需重跑
```

## 何時可移除 workaround

以下條件**同時**滿足時可考慮移除：

1. `googleworkspace/cli` 官方修復 issue #119（例如：內建 Client 改為
   支援個人 Gmail；或 CLI 新增 `--use-external-oauth-client` 官方旗標）
2. 你把 `~/.cache/slides-toolkit/bin/gws` 升級到修復版
3. `scripts/google-slides/env-guard.sh` 的 feature flag 判定 version
   >= known-fixed version（TECH-SPEC §6.1 最後一段）

在此之前**保留 workaround**。每次 `bootstrap.sh` 升級 gws binary 版
本時重新驗證一次（負驗證 + 正驗證）即可 —— gws 改版有可能無聲中修復、
也有可能無聲中破壞 workaround，兩種方向都要警覺。

追蹤方式：訂閱 upstream issue 通知、或於 `bootstrap.sh` pin 新版本
時在 PR description 附上 issue 最新狀態。

## 相關檔案

- `protocols/gcp-console-walkthrough.md` §8 — setup flow 的第 8 步
- `standards/credential-hygiene.md` — credential 放 `~/.config/gws/` 的硬規則
- `../../scripts/google-slides/env-guard.sh` — check / apply 實作
- `../../scripts/google-slides/gws-wrap.sh` — 每次呼叫前 source `env.sh`
- TECH-SPEC §4.2 — `env-guard.sh` 契約、exit 16
- TECH-SPEC §6.1 — workaround 完整實作描述
- PRODUCT-SPEC §3.3 [ASSUMPTION-3] — workaround 穩定性假設
