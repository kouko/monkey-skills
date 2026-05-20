# sf-report

Read this in: [English](README.md) | **日本語** | [繁體中文](README.zh-TW.md)

本 plugin に同梱の `salesforce` MCP server（Salesforce DX MCP、`data,metadata` toolset）経由で、Salesforce の **Report** と **Dashboard** に読み取り専用でアクセスします。skill は Report folder の一覧、Report metadata の取得、Report 実行、行データの取得、トレンド／集計／Top-N 分析、Dashboard widget のスナップショットを行い、すべて構造化 JSON で返します。UI scraping は使いません。

## Quickstart

Salesforce の Report または Dashboard widget を名前で指定して取得し、必要に応じてアドホックな filter 上書きを掛けて実行し、結果を会話内で分析します。出力には Report ID と実行 timestamp を必ず引用します。

## Prerequisites

- 初回のみ：`/salesforce-toolkit:sf-setup` を実行し、browser OAuth を完了する。
- `salesforce` MCP server が接続されていることを確認（`claude mcp list`）。
- Report 呼び出しが `INVALID_SESSION_ID` / token 期限切れを返した場合は、`bash salesforce-toolkit/scripts/sf/refresh-auth.sh` をユーザーに引き渡す。

## Example prompts

### Report を名前で実行

> 「今四半期の『Top 10 Won Opportunities this quarter』Report を見せて。」

skill は `list-reports` で Report ID を解決し、`describe-report` で日付 filter を確認したうえで `includeDetails=true` で実行し、行を Markdown 表として提示します。Report ID と実行 timestamp も併記します。

### Dashboard widget のスナップショット

> 「『Sales Pipeline Overview』Dashboard の widget データを取得して。」

skill は `list-dashboards` で Dashboard ID を解決し、`describe-dashboard` で widget 一覧とその source `reportId` を取得したうえで、各 widget の基底 Report を実行します。各 widget のデータは title と source Report ID 付きで引用されます。

### Pipeline funnel — Lead → Qualified → Won

> 「Lead → Qualified → Won の conversion を見せて。」

skill はまず事前作成済みの funnel Report があるかを確認（`list-reports` の部分一致）。あれば `includeDetails=false` で実行し、`factMap` から段階数と conversion 比率（Qualified/Lead、Won/Qualified、Won/Lead）を算出します。Report が無ければ、姉妹 skill `sf-query` に直接 SOQL aggregate を委譲します。

## Sibling skill

- **`sf-query`** — 既存 Report に対応しない問い合わせ、または 2,000 行 Report API 上限のため直接 SOQL のほうが綺麗に答えられる場合用の、アドホック SOQL / SOSL。

## Troubleshooting

完全な一覧は [`SKILL.md`](SKILL.md) の §Failure modes を参照。可視 folder 内に Report が無い（Folder sharing model）、legacy な Custom Report Type が `ReportNotSupportedException` を出す、2,000 行 API 上限、release 間の MCP tool 名 drift、session 中の認証期限切れなどを扱います。

## References

- skill の完全な指示：[`SKILL.md`](SKILL.md)
- Plugin 仕様：[`salesforce-toolkit/PRODUCT-SPEC.md`](../../PRODUCT-SPEC.md) + [`salesforce-toolkit/TECH-SPEC.md`](../../TECH-SPEC.md)
