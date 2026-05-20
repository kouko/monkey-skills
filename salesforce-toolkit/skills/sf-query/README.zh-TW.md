# sf-query

透過 Salesforce DX MCP server 對已連線的 org 執行自然語言 Salesforce SOQL / SOSL query。以散文丟出商業問題，skill 會挑出對的 MCP tool、組合 SOQL（或 SOSL）字串、先把它印出來給你 sanity-check、執行、再把列以 table 呈現。

唯讀（read-only）。不做 DML、不改 metadata — 那是 `sf-deploy`（Phase 2）的範圍。

## 前置條件

- `/salesforce-toolkit:sf-setup` 已成功跑過（安裝 `sf` CLI 與 `salesforce-mcp` 並完成 browser OAuth）。
- `/mcp` 輸出顯示 `salesforce-mcp` 為 **connected**。

任一檢查失敗就停下來，請使用者執行 `/salesforce-toolkit:sf-setup`（若 OAuth token 過期則加 `--force-reauth`）。

## 範例 prompt

skill 一律會在執行**前**把組好的 query 以 fenced block echo 出來，讓使用者 sanity-check。以下展示 skill 應該產生的 SOQL pattern。

### 範例 1 — 最近的 record

> *"列出最近建立的 10 個 Account。"*

針對 `Account` 的標準 SOQL，以 `CreatedDate` 倒序排，並以 `LIMIT 10` 收斂：

```sql
SELECT Id, Name, Industry, Owner.Name, CreatedDate
FROM Account
ORDER BY CreatedDate DESC
LIMIT 10
```

### 範例 2 — 過濾後的 pipeline

> *"未來 30 天內 close、金額超過 $100k 的 Open Opportunity。"*

帶 `NEXT_N_DAYS:30` 日期 literal（無需引號）與數值 `Amount` 條件的 SOQL。`IsClosed = false` 排除已 won/lost 的列，使用者只會看到 open pipe：

```sql
SELECT Id, Name, StageName, Amount, CloseDate, Account.Name
FROM Opportunity
WHERE CloseDate = NEXT_N_DAYS:30
  AND Amount > 100000
  AND IsClosed = false
ORDER BY CloseDate ASC
LIMIT 200
```

### 範例 3 — 本 quarter 的彙總

> *"本 quarter 的 Case 依 Status 計數。"*

使用 `GROUP BY` 與 `THIS_QUARTER` 日期 literal 的彙總 SOQL：

```sql
SELECT Status, COUNT(Id) cnt
FROM Case
WHERE CreatedDate = THIS_QUARTER
GROUP BY Status
ORDER BY COUNT(Id) DESC
```

MCP server 會把彙總結果攤平成 plain JSON — 請以 2 欄 markdown table 呈現。

## Troubleshooting

常見 error（完整表格與修正方式見 [`SKILL.md`](SKILL.md) §"Common errors and how to handle them"）：

- `INVALID_FIELD` / `INVALID_TYPE` — field 或 object 不存在，或 field-level / object-level 讀取權限不足。
- `MALFORMED_QUERY: unexpected token` — 通常是 date literal 加了引號（應寫 `TODAY` 而非 `'TODAY'`），或 child relationship 名稱寫錯（應寫 `Cases` 而非 `Case`）。
- `INVALID_SESSION_ID` / `unauthorized` — OAuth token 過期；執行 `bash "${CLAUDE_PLUGIN_ROOT}/scripts/sf/refresh-auth.sh"`。
- `QUERY_TIMEOUT` — query 涵蓋資料量過大；在 indexed field（`Id` / `Name` / `CreatedDate` / `OwnerId`）上加上具選擇性的 `WHERE`，或把 `LIMIT` 收緊。

## References

- 完整 skill 指令：[`SKILL.md`](SKILL.md)
- [Salesforce SOQL & SOSL Reference](https://developer.salesforce.com/docs/atlas.en-us.soql_sosl.meta/soql_sosl/) — primary source
- [salesforcecli/mcp](https://github.com/salesforcecli/mcp) — upstream MCP server
