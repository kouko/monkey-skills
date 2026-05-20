# sf-report

Read this in: [English](README.md) | [日本語](README.ja.md) | **繁體中文**

透過本 plugin 內附的 `salesforce` MCP server（Salesforce DX MCP，`data,metadata` toolset）以唯讀方式存取 Salesforce 的 **Report** 與 **Dashboard**。此 skill 可列出 Report 資料夾、取得 Report metadata、執行 Report、抓取列資料、跑趨勢／聚合／Top-N 分析、以及對 Dashboard widget 做快照，全部回傳結構化 JSON，不做 UI scraping。

## Quickstart

依名稱抓取 Salesforce 的 Report 或 Dashboard widget，必要時加上臨時 filter 覆寫後執行，並在對話內分析結果。輸出一律附上來源 Report ID 與執行 timestamp。

## Prerequisites

- 一次性：執行 `/salesforce-toolkit:sf-setup` 並完成 browser OAuth。
- 確認 `salesforce` MCP server 已連線（`claude mcp list`）。
- 若 Report 呼叫回傳 `INVALID_SESSION_ID` / token 過期，請以 `bash salesforce-toolkit/scripts/sf/refresh-auth.sh` 交回使用者執行。

## Example prompts

### 以名稱執行 Report

> 「給我看本季的『Top 10 Won Opportunities this quarter』report。」

此 skill 會以 `list-reports` 解出 Report ID，用 `describe-report` 確認日期 filter，再以 `includeDetails=true` 執行，最後將列以 Markdown 表格呈現，並附上 Report ID 與執行 timestamp。

### Dashboard widget 快照

> 「抓『Sales Pipeline Overview』Dashboard 的 widget 資料。」

此 skill 呼叫 `list-dashboards` 解出 Dashboard ID，再用 `describe-dashboard` 列出其 widget 與來源 `reportId`，接著執行每個 widget 背後的 Report。每筆 widget 資料皆附上 title 與來源 Report ID 引用。

### Pipeline funnel — Lead → Qualified → Won

> 「給我看 Lead → Qualified → Won 的 conversion。」

此 skill 會先檢查是否有預建的 funnel Report（`list-reports` 子字串比對）。若有，會以 `includeDetails=false` 執行，並從 `factMap` 算出各階段筆數與 conversion 比率（Qualified/Lead、Won/Qualified、Won/Lead）。若沒有 Report，此 skill 會將請求交給姊妹 skill `sf-query` 跑直接的 SOQL aggregate。

## Sibling skill

- **`sf-query`** — 用於無法對應到既有 Report 的查詢，或 2,000 列 Report API 上限讓直接 SOQL 反而更乾淨的情境，提供臨時的 SOQL / SOSL。

## Troubleshooting

完整列表請見 [`SKILL.md`](SKILL.md) §Failure modes — 涵蓋 Report 不在任何可見資料夾（Folder sharing model）、legacy Custom Report Type 觸發 `ReportNotSupportedException`、2,000 列 API 上限、release 間 MCP tool 名稱 drift，以及 session 中認證過期。

## References

- 完整 skill 指示：[`SKILL.md`](SKILL.md)
- Plugin 規格：[`salesforce-toolkit/PRODUCT-SPEC.md`](../../PRODUCT-SPEC.md) + [`salesforce-toolkit/TECH-SPEC.md`](../../TECH-SPEC.md)
