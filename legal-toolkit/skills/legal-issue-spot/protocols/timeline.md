# Protocol — timeline

Step 2 of the `legal-issue-spot` pipeline. Reads the structured 事實摘要
written by `parse-facts.md` and emits a chronological timeline table to
`issues.md §時間軸`. Pure-LLM transformation; no external lookups.

Path A discipline applies to date phrasing: ISO 8601 only (no GDPR-style
"within 72 hours" rhetoric); for unrealized / unknown anchors use the
`⏳ 待釐清` marker family — same convention as
`legal-incident-response/protocols/pii-breach.md` Step 4 + the
`template-pii-breach-incident-record.md` §時間軸 block.

## Input contract

- **Source file**: `issues.md` (created by `parse-facts.md`)
- **Source section**: `§事實摘要` — must already exist and contain the
  structured 當事人 / 行為 / 時間 / 金額 / 標的 fact extraction
- **Working dir**: `<cwd>/legal-outputs/<YYYY-MM-DD-HHmm>-issue-spot/`

## Output contract

- **Target file**: `issues.md` (same file; append-only at this step)
- **Target section heading**: `## §時間軸` (exact byte sequence — the
  grader will grep for it)
- **Body**: a single markdown table with columns
  `時間 (ISO 8601 or ⏳)` / `事件` / `當事人` / `備註`
- Rows ordered chronologically (earliest first; `⏳ 待釐清` rows last,
  by best-effort future ordering then alphabetic on `事件`)

## ISO 8601 convention

Mirror `legal-incident-response/protocols/pii-breach.md` Step 4b:

| Precision | Form | Example |
|---|---|---|
| Day | `YYYY-MM-DD` | `2026-04-12` |
| Day + time | `YYYY-MM-DDTHH:MM` | `2026-04-12T14:30` |
| Day + time + TZ | `YYYY-MM-DDTHH:MM±HH:MM` | `2026-04-12T14:30+08:00` (use when source 事實 explicitly states 時區) |
| Quarter known, date unknown | `⏳ 待釐清 (預計 YYYY-Q[1-4])` | `⏳ 待釐清 (預計 2026-Q3)` |
| Promised but unspecified | `⏳ 對方未告知 (聲明於 YYYY-MM-DD)` | `⏳ 對方未告知 (聲明於 2026-05-10)` |
| No anchor at all | `⏳ 待釐清` | `⏳ 待釐清` |

Pick the **finest precision the source 事實 actually supports**. Do NOT
fabricate hour/minute precision when the source only says "上午" — use
day precision. Do NOT fabricate timezone — omit it unless source states it.

## Procedure

1. **Open** `issues.md` and read the `§事實摘要` section. If the section
   is missing, empty, or contains 0 dated events → halt (see fallback
   below).
2. **Enumerate** every distinct dated event mentioned in the section:
   每個 (時點, 事件, 當事人) tuple gets one row. A single 事實 sentence
   may yield 2-3 rows if it describes multiple events.
3. **Normalize each 時點** to the ISO 8601 precision table above. Round
   DOWN — if the source says "二月初", normalize to `YYYY-02` (month
   precision rendered as `YYYY-02-01` with a 備註 noting "原文：二月初").
4. **Classify unrealized / unknown anchors** — for each event whose
   時點 is in the future or not yet known, pick the right `⏳` form:
   - Future event with no committed date → `⏳ 待釐清`
   - Future event with quarter committed → `⏳ 待釐清 (預計 YYYY-Q[1-4])`
   - Promised by counterparty but no date → `⏳ 對方未告知 (聲明於 <聲明日 ISO>)`
5. **Sort** rows ascending by 時點. Place `⏳` rows after all dated rows.
   Among `⏳` rows: those with quarter estimates first (sorted by
   estimate), then `⏳ 對方未告知 ...` (sorted by 聲明日), then bare
   `⏳ 待釐清`.
6. **Render** the table under the heading `## §時間軸` in `issues.md`.
   Columns exactly: `| 時間 (ISO 8601 or ⏳) | 事件 | 當事人 | 備註 |`.
   Append at end of file (do not overwrite earlier sections).
7. **Spot-check** — verify every row's 當事人 cell names a party that
   appeared in `§事實摘要`. If a row introduces a new actor, fix
   `parse-facts.md` (back-edit `§事實摘要`) before continuing — do
   NOT silently introduce parties at the timeline stage.
8. Hand off to `spot-issues.md`.

## Halt + ask user fallback

If `§事實摘要` is missing, empty, or contains 0 dated events, halt and
emit the following prompt to the user (zh-TW):

```
⚠️ 此事實型態目前沒有可定錨的時間資訊。

可能原因：
- §事實摘要 仍是空白（請先重跑 parse-facts.md）
- 原始事實描述裡完全沒有時點（連「最近」「前陣子」都沒有）

建議：
1. 補一下事件發生的大致時點（年月即可），重新跑此 skill；或
2. 確認此分析不需要時間軸 → 我可以跳過這步、直接進 spot-issues。

請回覆「補時點」或「跳過」。
```

If user replies「跳過」: write a single placeholder row to `§時間軸`:

```markdown
## §時間軸

| 時間 (ISO 8601 or ⏳) | 事件 | 當事人 | 備註 |
|---|---|---|---|
| ⏳ 待釐清 | 本案無可定錨之時間資訊 | — | 經使用者確認跳過時間軸建構 |
```

Then continue to `spot-issues.md`. If user replies「補時點」: re-run
`parse-facts.md` first, then re-enter this protocol.

## Worked example

Suppose `§事實摘要` contains:

> 2026-04-12 業務 A 將客戶聯絡人名單（約 800 筆）以 LINE 傳給合作夥伴 B 公司窗口；
> 2026-05-10 客戶 C 來信申訴並要求說明，公司於同日下午 14:30 回覆收訖；
> B 公司窗口口頭表示會在 7 日內回覆刪除進度，但目前尚未告知具體時點。
> 公司預計 2026 年 Q3 完成內部 SOP 修訂。

The rendered `§時間軸` becomes:

```markdown
## §時間軸

| 時間 (ISO 8601 or ⏳) | 事件 | 當事人 | 備註 |
|---|---|---|---|
| 2026-04-12 | 將客戶聯絡人名單（約 800 筆）以 LINE 傳送 | 業務 A → B 公司窗口 | 個資傳輸行為，是否符合 §27 待後續涵攝 |
| 2026-05-10 | 客戶來信申訴並要求說明 | 客戶 C → 公司 | 觸發 §3 當事人查詢權 |
| 2026-05-10T14:30 | 公司回覆收訖 | 公司 → 客戶 C | 同日回覆，留存 LINE 截圖 |
| ⏳ 待釐清 (預計 2026-Q3) | 內部 SOP 修訂完成 | 公司 | 公司自訂時程，非法定義務 |
| ⏳ 對方未告知 (聲明於 2026-05-10) | B 公司回覆刪除進度 | B 公司窗口 → 公司 | 口頭承諾 7 日內回覆，需書面催告 |
```

Notes on the example:

- Row 1 uses day precision (`2026-04-12`) — source says the date but
  not the hour.
- Row 3 uses `T14:30` precision because the source explicitly says
  "下午 14:30"; no timezone added (source does not state TZ).
- Row 4 is a future event with quarter committed → `⏳ 待釐清 (預計 2026-Q3)`.
- Row 5 is the promised-but-unspecified case → `⏳ 對方未告知 (聲明於 2026-05-10)`.
- 當事人 cells use arrow notation (`A → B`) when the event is a
  directed action between two parties; single-party events use just
  the actor.

## Failure modes

- `§事實摘要` missing → halt at Step 1 with the user-prompt above
- Fabricated time precision (hour added when source has only day) →
  caught by `parse-facts.md ↔ timeline.md` cross-read in Step 7;
  back-edit precision down
- New 當事人 introduced at this stage (not in `§事實摘要`) → halt and
  back-edit `§事實摘要`; do not silently introduce
- `⏳` form used incorrectly (e.g., `⏳ 待釐清` for a quarter-committed
  event) → re-classify per the table in §ISO 8601 convention
