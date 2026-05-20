# salesforce-toolkit

> 唯讀的 Salesforce 工具包 — 透過官方 Salesforce DX MCP server（[`salesforcecli/mcp`](https://github.com/salesforcecli/mcp)、Apache-2.0），對你的 org 進行自然語言 SOQL / SOSL 查詢與 Report / Dashboard 分析。

[English](README.md) | [日本語](README.ja.md) | **繁體中文**

> ⚠️ **不支援 Cowork — 只支援 Claude Code CLI / Code 分頁。** 第一次設定會跑 `sf org login web`，這是需要 TTY 的瀏覽器 OAuth 流程；Claude Desktop 的 Cowork sandbox 不會暴露這條路徑（限制與 [`gws-toolkit`](../gws-toolkit/)、[`collab-toolkit`](../collab-toolkit/) 相同）。如果你在 Cowork 上，請切換到 Claude Code CLI 或 Claude Desktop 的 Code 分頁。

## 功能介紹

把 Claude Code 接到你的 Salesforce org，讓你用自然語言問問題：

- **資料查詢** — 自然語言 SOQL / SOSL：列出 object、抓 record、過濾、聚合、走訪父子關聯
- **Reports 與 Dashboards** — 列出資料夾、抓 metadata、執行 Report、拉 row 資料、Dashboard widget 快照、趨勢 / Top-N / 漏斗分析
- **唯讀章程** — 只啟用 `data,metadata` MCP toolset；不做 Apex deploy、metadata push、user CRUD,等到 v0.2+ 推出破壞性操作的 safety wrapper 才開放

v0.1.0 包裝上游的 Salesforce DX MCP server（[`salesforcecli/mcp`](https://github.com/salesforcecli/mcp)、Apache-2.0、2026 GA）— vendor 維護、schema-aware 的工具表面,沒有第三方 query DSL 漂移問題。

## 快速開始

```bash
# 0. 一次性：安裝 Homebrew（如果還沒裝過）。
#    在 Terminal.app 跑一次,然後重啟 Claude Code：
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
```

```
# 在 Claude Code 內：
1. /plugin install salesforce-toolkit          # 從 marketplace 安裝 plugin
2. /salesforce-toolkit:sf-setup                # Claude 引導你跑完 setup — 不用碰 terminal
3. /reload-plugins                             # 啟用 salesforce MCP server（Claude 會提醒你）
```

`/sf-setup` 從頭到尾留在這個對話：Claude 用 `credential-check.sh` 探測現況 → 用非互動模式跑缺的 `brew install sf` + `brew install salesforce-mcp` → 用 question UI 問你 instance URL 跟 alias → 把 `sf org login web` 丟到背景 → 輪詢 OAuth 完成 → 提示你跑 `/reload-plugins`。耗時：~3-5 分鐘（大部分是瀏覽器按 OAuth 同意）。重跑 ~5 秒（每個 step 都會探測現況,裝過的就 skip）。

> **brew 是唯一的一次性外部 step。** brew installer 本身會跑 `sudo`,從 Claude Code 的 Bash tool 跑不動 — 這就是為什麼 Step 0 留下。裝完 brew 之後其他全部留在對話內。

> Power-user 路徑：在自己 terminal 跑 `bash $CLAUDE_PLUGIN_ROOT/scripts/sf/auto-setup.sh` 走 TTY-prompt 完整 install,跟對話內路徑收斂到同一個 end state。

設定完成後,你可以這樣問 Claude：

- 「列出最近 10 筆超過 $50K 的 Opportunity」
- 「給我看 EMEA team 的 pipeline,依 stage 分群」
- 「拉 Weekly Revenue Dashboard,幫我整理重點變動」

## Skill 清單

| Skill | 用途 |
|---|---|
| [`sf-query`](skills/sf-query/) | 自然語言 SOQL / SOSL — 列出 object、抓 record、過濾、聚合、走訪父子關聯 |
| [`sf-report`](skills/sf-report/) | Salesforce Reports + Dashboards — 列出資料夾、抓 metadata、執行 Report、拉 row 資料、widget 快照、趨勢 / Top-N / 漏斗分析 |

兩個 skill 都是唯讀。寫入類 toolset（`users` / `code-analyzer` / Apex deploy）延到 v0.2+,而且即使到時候,也必須使用者明確輸入寫入請求才會執行。

## 工具堆疊

| Component | Source | 角色 |
|---|---|---|
| [`sf` CLI](https://developer.salesforce.com/tools/salesforcecli) | `brew install sf` | Salesforce DX CLI — 提供 OAuth（`sf org login web`）、org / alias 管理、token 快取 |
| [`salesforce-mcp`](https://github.com/salesforcecli/mcp) | `brew install salesforce-mcp`（Apache-2.0） | MCP server,暴露 60+ Salesforce tool（data / metadata / orgs / users / code-analyzer）;v0.1.0 只啟用 `data,metadata` toolset。brew formula 名為 `salesforce-mcp`,但實際安裝的 binary 是 `sf-mcp-server`（npm 套件 `@salesforce/mcp` 也是 ship 同一個 binary） |
| [`bin/sf-mcp-launcher.sh`](bin/sf-mcp-launcher.sh) | plugin 內建 shim | Launcher：優先使用 PATH 上的 `sf-mcp-server` binary,沒有的話 fallback 到 `npx -y @salesforce/mcp`;兩條路徑都不通時印出 `sf-setup` 提示 |
| Homebrew | https://brew.sh | macOS 套件管理器 — 如果沒裝,`sf-setup` 會自動安裝（會有 y/N 確認） |
| Node ≥ 26（傳遞依賴） | Homebrew 依賴 | `sf-mcp-server` binary 的執行環境 |

`sf-setup` 一次把這 4 個可安裝項目串好。Launcher shim 讓 `.mcp.json` 即使在沒裝 brew 的情況下也能載入 — server 會在第一次 MCP tool 呼叫時透過 `npx` 啟動。

## 前置需求

| 項目 | 需求 |
|---|---|
| OS | macOS 14+（darwin-arm64 / darwin-x86_64）。Linux / WSL 規劃在 Phase 2+。 |
| Shell | zsh 或 bash（macOS 預設的 zsh 即可） |
| Terminal | 真正的 TTY（Terminal.app / iTerm2 / VS Code 內建終端）— OAuth 確認 prompt 需要 |
| Browser | Chrome 或 Safari（`sf org login web` 過程中需要一次） |
| Salesforce org | 可以透過瀏覽器 OAuth 登入的 Production、Sandbox、Scratch 或 Developer Edition org。非 Production org 請透過 `--instance-url=` 傳給 `sf-setup`。 |

**不需要**：Python、uv、gcloud、自建的 Connected App。v0.1.0 使用 `sf` CLI 內附的 public OAuth client。

## token 過期時的重新認證

Salesforce DX OAuth 的 refresh token 有效期由 org 政策決定（sandbox 通常數小時到幾天,Production 較長）。過期時,Claude Code 會告訴你 MCP server 連不到 org。不必重跑整個安裝器即可重新認證：

```bash
bash scripts/sf/refresh-auth.sh
```

或同等的 `/salesforce-toolkit:sf-setup --force-reauth`。兩種做法都會跳過 brew 步驟,只針對既有 alias 重跑 `sf org login web`。

## 疑難排解

最常見的症狀都在 [`commands/sf-setup.md`](commands/sf-setup.md) §Troubleshooting 涵蓋（TTY 守衛 / 不支援的 OS / brew 安裝失敗 / OAuth 流程被取消 / verify 空 / 互斥旗標）。要做更深入的狀態檢查,可以跑 `bash scripts/sf/credential-check.sh --json`,沒有 side effect 地 dump 目前的 `sf` + brew + MCP 狀態。

scripts 內已經處理好的兩個非 TTY 注意事項（你不用做什麼 — 這裡只列出來給你看背景）：

- **`SF_DISABLE_TELEMETRY=true` 會被自動 export。** 第一次跑 `sf` 會跳一個 y/N 的 telemetry 同意 prompt,在非 TTY 環境（Claude Code 的 Bash tool）會 hang 住;setup script 透過 export 這個 env var 把 prompt skip 掉。
- **非 TTY 模式下不會印 OAuth URL。** `sf org login web` 在沒有真正 TTY attach 的時候不會把 auth URL 印到 stdout/stderr,所以 Claude 沒辦法把 URL inline 顯示給你（瀏覽器還是會自動開）。如果瀏覽器沒開,請改走 Path B（Terminal power-user）— 那條路徑會原生印出 URL。

## 架構

```
┌──────────────────────────────────────────────────────────────┐
│  Claude Code (CLI / Code 分頁)                               │
│                                                              │
│  ┌─────────────┐         ┌─────────────┐                     │
│  │  sf-query   │         │  sf-report  │                     │
│  │  (SKILL.md) │         │  (SKILL.md) │                     │
│  └──────┬──────┘         └──────┬──────┘                     │
│         │                       │                            │
│         └───────────┬───────────┘                            │
│                     ▼                                        │
│        mcp__salesforce__*  (60+ tools, data + metadata)      │
└─────────────────────┬────────────────────────────────────────┘
                      │  stdio MCP transport
                      ▼
        bin/sf-mcp-launcher.sh   (brew → npx fallback)
                      │
                      ▼
        sf-mcp-server  (brew `salesforce-mcp` / npm `@salesforce/mcp` 的 binary, Apache-2.0)
                      │
                      ▼
                  sf CLI  (sf org login web 拿到的 OAuth token)
                      │
                      ▼
              Salesforce org REST API
```

設定時間（一次性）：`/salesforce-toolkit:sf-setup` 在使用者終端跑 6 步驟安裝器。執行時：Claude Code 載入 `.mcp.json` → spawn launcher shim → 透過 stdio spawn `sf-mcp-server` → MCP tool 對兩個 skill 變為可用。

## 連結

- [PRODUCT-SPEC.md](PRODUCT-SPEC.md) — 產品方向、Users、JTBD、Scope、Non-goals、競品定位、KR 目標
- [TECH-SPEC.md](TECH-SPEC.md) — 模組設計、`.mcp.json` 結構、shell script 合約、alias 推論、安全性
- [CHANGELOG.md](CHANGELOG.md) — 版本歷史
- [`commands/sf-setup.md`](commands/sf-setup.md) — `/salesforce-toolkit:sf-setup` command reference 與疑難排解
- 母 repository：[`monkey-skills`](https://github.com/kouko/monkey-skills)

## 相關連結

- [`gws-toolkit`](../gws-toolkit/) — Google Workspace（Slides / Docs / Sheets / Drive）工具包;同樣不支援 Cowork（TTY 必須的 OAuth）
- [`collab-toolkit`](../collab-toolkit/) — Asana / Slack / Notion,透過各服務官方 MCP server;同樣的唯讀章程
- [Salesforce DX MCP](https://github.com/salesforcecli/mcp) — 本 plugin 包裝的上游 MCP server（Apache-2.0）
- [Salesforce CLI 文件](https://developer.salesforce.com/docs/atlas.en-us.sfdx_cli_reference.meta/sfdx_cli_reference/cli_reference_unified.htm) — `sf` command reference

## 授權

MIT — 詳見 [LICENSE-MIT.txt](LICENSE-MIT.txt)。
