# Taiwan Local Rigor Gate

```yaml
---
name: taiwan-local-rigor-gate
description: MAY gate — Taiwan equity memos correctly interpret 三大法人/月營收/董監持股/融資融券 and cite TWSE/MOPS primary sources
gate_tier: MAY
trigger: Taiwan-listed ticker OR TWSE/MOPS/FSC data used
---
```

## Trigger Condition

This gate applies ONLY when the memo meets at least one of:

- Covers a Taiwan-listed stock (ticker with `.TW`, `.TWO`, or a 4-digit TWSE/TPEx code)
- Uses TWSE/MOPS/FSC data: 三大法人, 月營收, 董監持股, 融資融券

If neither condition applies, return: `SKIP — Taiwan Local Rigor gate does not apply to this memo.`

Do NOT penalize a memo for omitting Taiwan-specific data when the memo is clearly scoped to a non-Taiwan equity
and happens to mention Taiwan macro context in passing.

## Prerequisites

This gate runs AFTER the investment memo structure checklist passes.
Do not re-check whether data fields are present — focus on whether
their interpretation is correct and whether primary sources are cited.

## Criteria

### Criterion 1: 融資/融券 directional signals correct (🟢/🟡/🔴)

- 🟢 融資 (margin long) interpreted as retail bullish signal; 融券 (short-sale) interpreted as bearish positioning; rising 融資 + falling price read as margin call pressure risk
- 🟡 Signals partially correct but one direction is unclear or hedged
- 🔴 融資 and 融券 conflated, reversed, or described as a single "margin trading" metric with undifferentiated signal

### Criterion 2: 三大法人 categories correctly distinguished (🟢/🟡/🔴)

- 🟢 外資及陸資 / 投信 / 自營商 treated as three distinct categories with appropriate signal weights (外資 = large/trend-following; 投信 = often contrarian; 自營商 = often hedging)
- 🟡 Categories mentioned but signal weights not differentiated
- 🔴 All three lumped as "institutions" with a single undifferentiated signal

### Criterion 3: 月營收 timing interpreted correctly (🟢/🟡/🔴)

- 🟢 Revenue data sourced from the correct disclosure window (10th calendar day of following month); staleness correctly assessed against that deadline
- 🟡 Revenue timing mentioned but disclosure deadline not checked
- 🔴 Revenue described as "end of month" or other incorrect deadline; or revenue data used without checking whether latest period has been announced yet

### Criterion 4: 董監持股 pledge ratio interpreted as governance risk (🟢/🟡/🔴/N/A)

- 🟢 Pledge ratio >50% flagged as governance risk with 葉銀華 2008 rationale; declining shareholding trend noted as potential distribution signal
- 🟡 Pledge ratio mentioned but not interpreted (just stated as a number)
- 🔴 High pledge ratio described as neutral or positive ("directors have skin in the game via pledged shares") — this is incorrect
- N/A: 董監持股 data not available or not material to the memo

### Criterion 5: Taiwan data cites TWSE/MOPS/FSC as primary (🟢/🟡/🔴)

- 🟢 Institutional flows from TWSE T86; revenue from MOPS; governance data from TWSE insider holdings page; or explicitly sourced from a data provider that tracks these official sources
- 🟡 Data source not specified but data appears credible (e.g., FinMind or TEJ, which aggregate MOPS/TWSE)
- 🔴 Data described as "from Taiwan financial news" or other non-primary aggregator without verifying it matches MOPS/TWSE official data

### Criterion 6: Taiwan-specific cycle adjustment applied (🟢/🟡/🔴/N/A)

- 🟢 If global macro regime diverges from Taiwan tech sector cycle, the divergence is noted and explained (e.g., global Stagflation but Taiwan AI server export cycle in Recovery phase → regime-exception documented)
- 🟡 Global regime used without consideration of Taiwan-specific cycle
- 🔴 Global regime applied directly to Taiwan stock without any local adjustment, AND the memo covers a Taiwan tech exporter (semiconductor, PCB, ODM) where the divergence is material
- N/A: Memo covers a Taiwan domestics stock (bank, retailer, telecom) where global regime applies directly

## Verdict Rules

- **PASS**: all applicable criteria 🟢 (N/A criteria excluded from scoring)
- **PASS_WITH_NOTES**: any 🟡, no 🔴
- **NEEDS_REVISION**: any 🔴

PASS_WITH_NOTES: the evaluator must list each 🟡 criterion by number and state what the worker should clarify or add. Do not auto-revise factual interpretation errors — escalate to user.

## Note to Evaluator

This is a MAY gate. Scope it tightly:

- Only score criteria that are directly relevant to the memo's content.
  If the memo does not discuss 融資融券 at all, mark Criterion 1 as N/A
  rather than 🔴 — absence of data is not a mis-interpretation.
- Criterion 6 (cycle adjustment) is N/A for Taiwan domestic stocks
  (banks, retailers, telecoms) where global macro applies directly.
  Only flag 🔴 for tech exporters where the divergence is material.
- Do not invent Taiwan-specific data gaps that the memo's scope does
  not require. A US-equity memo that briefly references TSMC supply
  chain does not trigger this gate.

## Output Format

1. **Trigger check**: state whether gate applies and why (ticker, data type); or return SKIP
2. **Criteria scores**: one row per criterion — criterion number, 🟢/🟡/🔴/N/A, one-line evidence quote from memo
3. **Fix instructions**: for each 🔴 or 🟡, state exactly what the worker must correct or add
4. **Verdict**: PASS / PASS_WITH_NOTES / NEEDS_REVISION

Never sugar-coat. Flag 🔴 criteria clearly and state the specific mis-interpretation.
