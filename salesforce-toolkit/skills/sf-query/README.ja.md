# sf-query

Salesforce DX MCP server 経由で接続済み org に対する自然言語の Salesforce SOQL query。ビジネス上の質問を散文で投げると、skill が SOQL 文字列を組み立て、sanity-check 用にそのまま表示してから upstream の `run_soql_query` MCP tool を呼び、行を table としてレンダリングする。

read-only。plugin は `data` MCP toolset のみ（唯一の tool：`run_soql_query`）を有効化。DML も metadata 変更もしない。SOSL は upstream MCP がまだ tool 化していないため、v0.1.0 は SOQL のみ。

## 事前条件

- `/salesforce-toolkit:sf-setup` が成功している（`sf` CLI + `salesforce-mcp` brew formula を install し — PATH 上のバイナリ名は `sf-mcp-server` — browser OAuth まで完了）。
- `/mcp` 出力で `salesforce` という MCP server が **connected** と表示されている（server 名は `.mcp.json` 由来、実際のバイナリは `sf-mcp-server`）。

いずれかに失敗していたら、user に `/salesforce-toolkit:sf-setup` 実行（OAuth token が expire しているなら `--force-reauth` を渡す）を依頼して停止する。

## 例示 prompt

skill は組み立てた query を fenced block で実行**前**に必ず echo して、user に sanity-check させる。以下は skill が出すべき SOQL の典型 pattern。

### 例 1 — 最近の record

> *"直近で作成された Account を 10 件表示して。"*

`Account` への標準 SOQL、`CreatedDate` desc で sort、`LIMIT 10`：

```sql
SELECT Id, Name, Industry, Owner.Name, CreatedDate
FROM Account
ORDER BY CreatedDate DESC
LIMIT 10
```

### 例 2 — 絞り込んだ pipeline

> *"今後 30 日以内に close する $100k 超の Open Opportunity。"*

`NEXT_N_DAYS:30` 日付 literal（quote 不要）と数値 `Amount` 述語を持つ SOQL。`IsClosed = false` で won/lost を除外し、open pipe のみ user に見せる：

```sql
SELECT Id, Name, StageName, Amount, CloseDate, Account.Name
FROM Opportunity
WHERE CloseDate = NEXT_N_DAYS:30
  AND Amount > 100000
  AND IsClosed = false
ORDER BY CloseDate ASC
LIMIT 200
```

### 例 3 — 今 quarter の集計

> *"今 quarter の Case を Status 別に count。"*

`GROUP BY` と `THIS_QUARTER` 日付 literal を使った集計 SOQL：

```sql
SELECT Status, COUNT(Id) cnt
FROM Case
WHERE CreatedDate = THIS_QUARTER
GROUP BY Status
ORDER BY COUNT(Id) DESC
```

MCP server は集計結果を plain JSON に flatten するので、2 列 markdown table としてレンダリングする。

## Troubleshooting

よくある error（fix 込みの full table は [`SKILL.md`](SKILL.md) §"Common errors and how to handle them" 参照）：

- `INVALID_FIELD` / `INVALID_TYPE` — field か object が存在しない、または field-level / object-level の read 権限がない。
- `MALFORMED_QUERY: unexpected token` — 多くは date literal を quote した（`TODAY` を `'TODAY'` と書いた）か、child relationship 名を間違えた（`Case` ではなく `Cases`）ケース。
- `INVALID_SESSION_ID` / `unauthorized` — OAuth token が expire。`bash "${CLAUDE_PLUGIN_ROOT}/scripts/sf/refresh-auth.sh"` を実行。
- `QUERY_TIMEOUT` — query が触ったデータ量が過大。indexed field（`Id` / `Name` / `CreatedDate` / `OwnerId`）に絞った `WHERE` を追加するか `LIMIT` をきつくする。

## References

- 完全な skill 指示：[`SKILL.md`](SKILL.md)
- [Salesforce SOQL Reference](https://developer.salesforce.com/docs/atlas.en-us.soql_sosl.meta/soql_sosl/) — primary source（この plugin の v0.1.0 で reach できるのは SOQL のみ）
- [salesforcecli/mcp](https://github.com/salesforcecli/mcp) — upstream MCP server
