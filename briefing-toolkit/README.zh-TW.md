# briefing-toolkit

跨已連接工具的每日**晨報**。對你 MCP 連線好的各服務做一次唯讀並行巡查,蒸餾成一份總統每日簡報(PDB)風格的摘要——再加上一張**零省略**、可點處理的行動表,**每天累積**供跨日延續性分析。

> [`README.md`](README.md) ・ [`README.ja.md`](README.ja.md)

## 它做什麼

`/daily-brief` 對最多 **7 個平台**(Gmail / Slack / Notion / Asana / Google Drive / Google Calendar / **GitHub**)做唯讀並行 fan-out,找出**與你相關**的事,在你指定的資料夾寫出兩份產物:

| 產物 | 角色 |
|---|---|
| `<日期>_晨報.md` | **Curated 簡報**(PDB 風格):今日焦點(動態、門檻驅動)· 當日行程 · 要回覆 · 進行中專案 · 未來 N 天——短、狠、每列可點。 |
| `<日期>_完整事項.md` | **零省略行動表**——每筆都列、依重要度排序,每列都是可點去處理的深連結。 |
| `<日期>_完整事項.csv` | 機讀索引。唯一識別碼欄是隔天延續性 diff 的 **JOIN 主鍵**。 |

### 延續性(主打功能)

產物以日期台帳累積。每次執行會讀「**最近一份**」簡報的 CSV 並做差分,標出 **✅ 已結**、**⏳ 仍在等你(已 N 天)**、**🆕 新發生**。延續性以**各項目 ID 去 live 平台重新驗證**為根據,絕不相信昨日文字(防止幻覺一路 carry-forward)。

## 前置需求

本 toolkit **消費你既有連線的 MCP server**並優雅降級(不自行註冊)。請依需求連好服務,例如:

- [`collab-toolkit`](../collab-toolkit/) — Slack / Asana / Notion
- [`gws-toolkit`](../gws-toolkit/) — Gmail / Google Calendar / Drive
- GitHub MCP server(或 `gh` CLI)

沒連的平台會在簡報的「資料源涵蓋聲明」中被標為盲區,其餘照常執行。

> ⚠️ 僅限 Claude Code CLI——底層 MCP 抓取在 Cowork sandbox 不支援。

## 安全

- 全程 **read-only**(search / fetch / read)。不改、不刪、不送出。
- **draft-only**——只寫進你指定的本機資料夾。**絕不**寫回 Notion / Slack / Gmail / Asana 或任何官方系統,**絕不**自動回覆。

## 排程

skill 是 on-demand。要「每天早上」自動跑,在上面疊一層 harness 觸發——`/schedule`、系統 cron、或 Cowork scheduled task,排成每早叫 `/daily-brief`。排程與遞送刻意不放進 skill。

## 不是這個 toolkit

- 績效回顧 / 自評 / 期間盤點 → 用 `performance-evidence-audit`(同一套跨平台機制,但朝過去、目標是證據)。
- 寫回 / 送出 / 對平台自動行動 → 設計上不做。

## Skills

| Skill | 指令 | 用途 |
|---|---|---|
| `daily-brief` | `/daily-brief` | 產生今日跨工具晨報 + 行動表。 |
