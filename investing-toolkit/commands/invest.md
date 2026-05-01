# /invest

**Trigger**: `/invest`

Route to the right investing-toolkit skill based on your investing intent.

## What This Does

Invokes `skills/using-investing-toolkit/SKILL.md` — the v2.0.0 router. Three layers:

- **Data** (`data-{country}`): pure I/O for US / JP / TW / KR / CN
- **Analysis** (`analysis-*`): pure compute (DCF, screener scoring, technical, portfolio P&L, macro regime)
- **Report** (`report-*`): orchestration + Markdown (memo, snapshot, portfolio review, screener list)

If you have a specific intent, use a direct command:
- `/invest-macro` — 5-country macro regime call
- `/invest-memo {ticker}` — full investment memo with verdict
- `/invest-screen {tickers}` — cross-country stock screener with 8 presets
- `/invest-portfolio` — portfolio review with optional regime overlay
- `/invest-snapshot {ticker}` — single-ticker quick snapshot card

## Examples

```
/invest
/invest What can you do for Taiwan stocks?
/invest I want to analyze 2330.TW
```
