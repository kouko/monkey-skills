# collab-toolkit

> **非 Google** 辦公協作工具包（Asana / Slack / Notion）— 由各服務官方 MCP server 驅動的唯讀讀取。
> Gmail / Google Calendar 移交給 [`gws-toolkit`](../gws-toolkit/) 處理（Phase 2+）。

[![Language: English](https://img.shields.io/badge/lang-EN-blue)](README.md) [![日本語](https://img.shields.io/badge/lang-JA-blue)](README.ja.md) [![繁體中文](https://img.shields.io/badge/lang-zh--TW-blue)](README.zh-TW.md)

## 功能介紹

連接 Claude Code 與你日常使用的非 Google 辦公協作服務 — Asana、Slack、Notion — 提供：

- **狀態可視化**：公司動態、進行中的工作、團隊活動
- **跨工具搜尋**：透過 Claude Code 對公司內部資料進行自然語言搜尋
- **唯讀章程**：不寫入、不執行破壞性操作 — v0.2.0 延續 v0.1.x 的 non-goal

v0.2.0 透過每個服務各自的**官方 MCP server** 驅動 — 3 個服務的 MCP 支援皆已成熟，因此完全退役 v0.1.x 的瀏覽器 snapshot 堆疊。

## 快速開始

```bash
# 透過 Claude Code marketplace 安裝 plugin
/plugin install collab-toolkit

# 一次性初始化
/collab-setup
```

3 個 MCP server（Asana / Slack / Notion）會由 plugin 的 `mcpServers` block **自動註冊** — 不需手動執行 `/mcp add`。OAuth 會在你第一次呼叫每個 server 的 tool 時觸發。

完成後，你可以問 Claude 像這樣的問題：
- "列出我本週到期的 Asana 任務"
- "搜尋 5 月 1 日後 #engineering 頻道中關於 OKR 的 Slack 訊息"
- "找出關於 <主題> 的 Notion 頁面"

## 支援的服務

| Service | 通道 | 配線方式 |
|---|---|---|
| Asana  | 官方 MCP V2 (`mcp.asana.com/v2/mcp`)         | 由 plugin `mcpServers` 自動註冊 |
| Slack  | 官方 MCP（2026-02 GA、`mcp.slack.com/mcp`） | 自動註冊；OAuth scope 內嵌宣告 |
| Notion | 官方遠端 MCP (`mcp.notion.com/mcp`)          | 由 plugin `mcpServers` 自動註冊 |

> Gmail 與 Google Calendar 原本列在 v0.2.0 brief（5 服務計畫），cycle 末段轉向交給 [`gws-toolkit`](../gws-toolkit/) 處理 — 統一 Google OAuth client、避免與既有 Slides/Docs/Sheets/Drive skill 的 binary/scope 重複。詳見 `CHANGELOG.md` §"Late-pivot 2026-05-19"。

## Skill 清單

| Skill | 核心 protocol |
|---|---|
| `asana-automate`  | task-list, task-detail, project-overview, search-global |
| `slack-automate`  | search-messages, channel-read, thread-read, find-user |
| `notion-automate` | search-workspace, page-fetch, database-query |

> Notion `page-backlinks` 於 v0.2.0 移除 — Notion API 沒有原生 backlinks endpoint，v0.1.6 透過 UI scraping 的繞道方案無法移植到官方 MCP。詳見 `CHANGELOG.md` §Notes。

## 注意事項

- ⚠️ **不支援 Cowork sandbox** — sandbox 不會暴露各服務 `/mcp add` 的 OAuth 流程
- **唯讀章程**：不引入任何寫入操作 — 延續 v0.1.x 的 non-goal

## 疑難排解

| 症狀 | 解決方法 |
|---|---|
| `/mcp list` 中看不到 MCP server | plugin 沒載入 — 用 `/plugin list` 確認 `collab-toolkit` 已安裝；需要時重啟 Claude Code |
| MCP tool 回傳 "auth required" | 第一次的 OAuth 還沒完成 — Claude Code 應該會自動跳；若沒跳就重啟 Claude Code |
| Asana OAuth 失敗 `redirect_uri not registered` | 看 `commands/collab-setup.md` §Troubleshooting 的 per-user `clientId` escape hatch |

## 從 v0.1.x 遷移

v0.1.x 依賴位於 `~/.local/share/` 與 `~/.config/collab-toolkit/` 的瀏覽器自動化堆疊。v0.2.0 已不再參照這些。具體的 `rm -rf` 清理指令與選擇性的套件 uninstall 步驟，請見 `CHANGELOG.md` §Migration block。

## 開發

```bash
# 結構檢查（從儲存庫根目錄執行）
python scripts/check-skill-structure.py collab-toolkit
```

## 架構

v0.2.0 遷移 brief：`docs/collab-toolkit/specs/2026-05-19-v0.2.0-migration.md`（原本以 5 服務 scope，cycle 末段 pivot 到 3 服務 — 詳見 `CHANGELOG.md`）。
