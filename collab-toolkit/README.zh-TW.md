# collab-toolkit

> 由各服務官方 MCP server 或 CLI 驅動的唯讀辦公協作工具包 — 5 個 skill。
> Asana / Slack / Notion / Gmail / Google Calendar。

[![Language: English](https://img.shields.io/badge/lang-EN-blue)](README.md) [![日本語](https://img.shields.io/badge/lang-JA-blue)](README.ja.md) [![繁體中文](https://img.shields.io/badge/lang-zh--TW-blue)](README.zh-TW.md)

## 功能介紹

連接 Claude Code 與你日常使用的辦公協作服務 — Asana、Slack、Notion、Gmail、Google Calendar — 提供：

- **狀態可視化**：公司動態、進行中的工作、團隊活動
- **跨工具搜尋**：透過 Claude Code 對公司內部資料進行自然語言搜尋
- **唯讀章程**：不寫入、不執行破壞性操作 — v0.2.0 延續 v0.1.x 的 non-goal

v0.2.0 透過每個服務各自的**官方通道**驅動 — 5 個服務的 vendor 端 MCP / CLI 支援皆已成熟，因此完全退役 v0.1.x 的瀏覽器 snapshot 堆疊。

## 快速開始

```bash
# 透過 Claude Code marketplace 安裝 plugin
/plugin install collab-toolkit

# 一次性初始化
/collab-setup
```

`/collab-setup` 會引導你：安裝 `gws` CLI（優先 Homebrew，npm 為 fallback）→ 一次 Google OAuth（同時涵蓋 Gmail + GCal）→ 分別執行 `/mcp add` 安裝 Asana、Slack、Notion。5 個服務、總共 4 次 OAuth。

完成後，你可以問 Claude 像這樣的問題：
- "列出我本週到期的 Asana 任務"
- "搜尋 5 月 1 日後 #engineering 頻道中關於 OKR 的 Slack 訊息"
- "今天 Google Calendar 上有什麼行程"
- "找出下週二 10am 到 4pm 之間空閒的 30 分鐘時段"

## 支援的服務

| Service | 通道 | 設定步驟 |
|---|---|---|
| Asana  | 官方 MCP V2 (`mcp.asana.com/v2/mcp`)        | `/mcp add asana` — Claude Code native OAuth pre-registration |
| Slack  | 官方 MCP（2026-02 GA）                       | `/mcp add slack` |
| Notion | 官方遠端 MCP (`mcp.notion.com/mcp`)          | `/mcp add notion` |
| Gmail  | Google Workspace CLI (`gws`)                | `gws auth`（與 GCal 共用 OAuth） |
| GCal   | Google Workspace CLI (`gws`、同一 binary)   | （與 Gmail 同一個 OAuth） |

## Skill 清單

| Skill | 核心 protocol |
|---|---|
| `asana-automate`  | task-list, task-detail, project-overview, search-global |
| `slack-automate`  | search-messages, channel-read, thread-read, find-user |
| `notion-automate` | search-workspace, page-fetch, database-query |
| `gcal-automate`   | agenda-view, event-search, find-free-slots, shared-calendar-read |
| `gmail-automate`  | mail-search, thread-read, inbox-summary, label-read |

> Notion `page-backlinks` 於 v0.2.0 移除 — Notion API 沒有原生 backlinks endpoint，v0.1.6 透過 UI scraping 的繞道方案無法移植到官方 MCP。詳見 `CHANGELOG.md` §Notes。

## 注意事項

- ⚠️ **不支援 Cowork sandbox** — 需要本地安裝 `gws` binary，且 sandbox 不會暴露各服務 `/mcp add` 的 OAuth 流程
- **唯讀章程**：不引入任何寫入操作 — 延續 v0.1.x 的 non-goal
- **個人 Google 帳號**：OAuth 同意畫面對未驗證 app 強制 25 scope 上限 — 觸頂時請至 Cloud Console 整理用不到的 API

## 疑難排解

| 症狀 | 解決方法 |
|---|---|
| `gws: command not found` | 重新執行 `brew install gws`（或 npm fallback）；確認 `PATH` 包含 brew prefix（`brew --prefix`/bin） |
| `gws auth` → `connection refused` | 瀏覽器流程逾時 — 重新執行 `gws auth`，加快點完 consent 畫面（idempotent） |
| `OAuth scope exceeded 25` | 個人 Google 帳號對未驗證 app 的上限 — 至 Cloud Console 整理用不到的 API |
| `/mcp add` 失敗 | 更新 Claude Code — native OAuth pre-registration 在 2026 年下半年推出，舊版本沒有一鍵流程 |
| `GOOGLE_CLOUD_PROJECT not set` | 在 shell rc 中 export env var 並 reload — 詳見 `/collab-setup` Step 2 |

## 從 v0.1.x 遷移

v0.1.x 依賴位於 `~/.local/share/` 與 `~/.config/collab-toolkit/` 的瀏覽器自動化堆疊。v0.2.0 已不再參照這些。具體的 `rm -rf` 清理指令與選擇性的套件 uninstall 步驟，請見 `CHANGELOG.md` §Migration block。

## 開發

```bash
# 結構檢查（從儲存庫根目錄執行）
python scripts/check-skill-structure.py
```

## 架構

v0.2.0 遷移 brief：`docs/collab-toolkit/specs/2026-05-19-v0.2.0-migration.md`。
