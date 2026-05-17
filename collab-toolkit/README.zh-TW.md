# collab-toolkit

> 封裝 [vercel-labs/agent-browser](https://github.com/vercel-labs/agent-browser) 的瀏覽器自動化工具包。
> 5 個唯讀辦公協作 skill，用於職場資訊感知。

[![Language: English](https://img.shields.io/badge/lang-EN-blue)](README.md) [![日本語](https://img.shields.io/badge/lang-JA-blue)](README.ja.md) [![繁體中文](https://img.shields.io/badge/lang-zh--TW-blue)](README.zh-TW.md)

## 功能介紹

連接你日常使用的辦公協作服務 — Asana、Slack、Notion、Google Calendar、Gmail — 提供：

- **狀態可視化**：公司動態、進行中的工作、團隊活動
- **跨工具搜尋**：透過 Claude Code 對公司內部資料進行自然語言搜尋
- **背景執行**：首次登入後以無頭模式運行，在你工作時同步執行

基於 agent-browser 的語義優先 snapshot 模型 — 不需要脆弱的 CSS selector，不需要 API token，只需使用現有的 Chrome 登入狀態。

## 快速開始

```bash
# 透過 Claude Code marketplace 安裝 plugin
/plugin install collab-toolkit

# 一次性初始化（macOS 建議使用 Homebrew）
/collab-setup
```

就這樣。`/collab-setup` 會自動執行：
1. 安裝 `agent-browser`（macOS 使用 brew，替代方案為 npm）
2. 下載 Chrome for Testing
3. 安裝 `~/.local/bin/abx` 包裝器
4. 偵測你的 Chrome 設定檔，寫入設定
5. 驗證所有 5 個服務皆已登入

完成後，你可以問 Claude 像這樣的問題：
- "列出我本週到期的 Asana 任務"
- "搜尋 5 月 1 日後 #engineering 頻道中關於 OKR 的 Slack 訊息"
- "今天 Google Calendar 上有什麼行程"
- "找出下週二 10am 到 4pm 之間空閒的 30 分鐘時段"

## 支援的 UI 語言

v0.1.6+ 支援 **English / 繁體中文 / 日本語** UI 標籤。每個 protocol 都有 `Localized labels` 表格列出 3 種語言的 role+name 對照。其他語系（zh-CN / ko / 歐洲語言）可能部分可用 — 歡迎驗證過的標籤透過 PR 補充。

帳號介面語言為繁中時，protocol 會自動匹配繁中標籤。英文/日文帳號同理。

## 設定檔模式

| 模式 | 內容 | 使用時機 |
|---|---|---|
| **Dedicated**（預設、v0.1.2+） | 位於 `~/.local/share/collab-toolkit/profiles/dedicated/` 的單一統合設定檔。Google SSO 在服務間自動串接 → 5 個服務通常只需 2-3 次登入。設定流程由 Claude 編排（透過 AskUserQuestion，不需在終端機操作）。 | **預設 — 辦公協作用途推薦。** 多 profile、多帳號、SSO refresh 等情境都能穩定運作。與日常 Chrome 狀態完全脫鉤。 |
| **Shared**（`--shared`、選擇性啟用） | 透過 `--profile <name>` 重複使用日常 Chrome 的登入狀態 | ⚠️ Shared 模式有已知失敗情境：Chrome 執行中時 cookies 無法轉移（profile lock）、macOS Keychain 可能需要手動授權、多個 Chrome profile 時要挑「對」的、有 SSO refresh 的服務在 headless 下可能失效、verify 對行銷頁面 redirect 容易誤判。**僅在以下條件成立時推薦：只有 1 個 Chrome profile、5 個服務全用同一個 Google 帳號、沒有 SSO refresh。** |

隨時切換：`/collab-setup --switch-mode`（v0.1.2 後支援雙向 toggle）。

## Skill 清單

| Skill | 核心 protocol |
|---|---|
| `asana-automate` | task-list, task-detail, project-overview, search-global |
| `slack-automate` | search-messages, channel-read, thread-read, find-user |
| `notion-automate` | search-workspace, page-fetch, database-query, page-backlinks |
| `gcal-automate` | agenda-view, event-search, find-free-slots, shared-calendar-read |
| `gmail-automate` | mail-search, thread-read, inbox-summary, label-read |

## 注意事項

- ⚠️ **不支援 Cowork sandbox** — 需要本地 Chrome / OS 存取權限
- ⚠️ **v0.1.0 不支援 CI / 排程執行**（shared 模式僅限本地；dedicated 模式的可攜性延後至 v0.2.0+）
- **隱私範圍**：在 shared 模式下，agent-browser 可存取你 Chrome 的所有 cookie，不僅限於這 5 個服務。信任來源是本地 Rust binary 與開放原始碼。
- **登入狀態耦合**：在 shared 模式下，若你在日常使用的 Chrome 中登出某服務，自動化將失效，直到重新登入為止。

## 疑難排解

| 症狀 | 解決方法 |
|---|---|
| `ERR: config not found` | 執行 `/collab-setup` |
| `⚠️ ~/.local/bin not on PATH` | 在 shell 的 rc 檔中加入 `export PATH="$HOME/.local/bin:$PATH"` |
| `ERR: UI changed` | 開啟受影響 skill 的 `references/ui-patterns.md`，重新 snapshot 並更新 |
| `Login wall detected` | Shared 模式：透過 Chrome 登入。Dedicated 模式：`/collab-setup --reauth <service>` |

## 開發

```bash
# 單元測試（bats）
cd collab-toolkit && bats scripts/tests/

# 結構檢查（從儲存庫根目錄執行）
python scripts/check-skill-structure.py
```

## 架構

完整設計規格請見 `docs/superpowers/specs/2026-05-15-collab-toolkit-v0.1.0-design.md`。
