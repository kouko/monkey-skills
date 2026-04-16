# Taiwan Market Diagnosis Protocol

---
name: taiwan-market-diagnosis
description: Taiwan-specific equity diagnosis — 月營收 → 三大法人 → 董監持股 → 融資融券 → regime overlay → zh-TW memo
---

Taiwan equity analysis anchored in five locally-sourced data dimensions:
monthly revenue disclosure (月營收), institutional flow (三大法人),
governance signals (董監持股), margin/short sentiment (融資融券), and
global macro regime overlay. Cross-references
`standards/taiwan-equity-frameworks.md` for Taiwan-specific metric
definitions, `standards/investment-macro-regime.md` for IC regime
positioning, and `standards/investment-thesis-structure.md` +
`standards/decision-framework-and-verdict.md` for final synthesis.

**Default output language: Traditional Chinese (zh-TW).** The worker
may switch to English if the user writes in English and does not
specify a language preference. The analysis framework is bilingual —
use whichever term is clearer (e.g., "三大法人 (Three Major
Institutionals)").

## Trigger Detection

Activate this protocol when any of the following is present:

- Taiwan ticker format: 4-digit number (e.g., 2330, 0050) with or
  without explicit `.TW` / `.TWO` suffix
- Exchange keywords: TWSE, 上市, TPEx, TPEX, 上櫃
- Company keywords: 台積電, 聯發科, 鴻海, 台股
- Data-dimension keywords: 月營收, 三大法人, 融資融券, 董監持股
- Explicit user request for Taiwan market or 台股 analysis

## Phase 0: Mode and Budget Setup

**MUST run before Phase 1.** Read the `mode:` field from the worker
launch `### Input` section. If absent, default to `quick`.

| Mode | Default budget | Source cap | Token cap |
|---|---|---|---|
| **quick** (default) | 5 data dimensions screened | 5 sources | ~15k tokens |
| **deep** (opt-in) | full memo with L3 valuation | 15 sources | ~150k tokens |

In `quick` mode, Phases 2–5 produce summary flags only; Phase 7
produces a brief verdict without full valuation. In `deep` mode,
also run `protocols/deep-equity-research-memo.md` Phase 3 (L3
valuation) and Phase 4 (thesis) using Taiwan-specific data inputs.

## Phase 1: Scope Intake

- Accept: ticker + optional date range
- Confirm: company name, exchange (上市 TWSE vs. 上櫃 TPEx), and
  sector classification (electronics / semiconductor / financial /
  traditional industry / other)
- Request or acknowledge availability of data fixtures for each of
  the five dimensions below
- If any dimension's data is unavailable, note it explicitly and
  proceed with remaining dimensions; do not block on missing data

## Phase 2: 月營收 Analysis

Per `standards/taiwan-equity-frameworks.md` §月營收:

- Input: 3–6 months of monthly revenue figures (NT$ thousands)
- Compute MoM% and YoY% for each available month
- Compute 3-month rolling YoY average to smooth noise
- Assess trend direction: accelerating / stable / decelerating
- Note any known seasonality effect (e.g., Chinese New Year
  suppression in January–February; back-to-school cycle in Q3)
- **Flag — data lag**: if the most recent calendar month's
  announcement has not yet been released (Taiwan listed companies
  must disclose by the 10th of the following month), mark the
  most recent data point as provisional

## Phase 3: 三大法人 Analysis

Per `standards/taiwan-equity-frameworks.md` §三大法人:

- Input: daily or weekly net buy/sell figures for 外資
  (foreign institutions), 投信 (domestic investment trusts), and
  自營商 (proprietary dealers) — last 20 trading days preferred
- Compute running 5-day and 20-day cumulative net buy (NT$ millions
  or shares) for each of the three institution types
- Assess concordance: are 外資 and 投信 directionally aligned
  (both net buying or both net selling)?
- Identify divergence signal: 外資 selling + 投信 buying = monitor
  closely; may indicate domestic support against foreign exit
- **Flag — strong sell pressure**: all three institutions net
  selling simultaneously over the most recent 5-day window
- **Flag — strong accumulation**: 外資 and 投信 both net buying
  with 20-day cumulative above +NT$1B (or top-quintile for the
  stock's own history)

## Phase 4: 董監持股 Check

Per `standards/taiwan-equity-frameworks.md` §董監持股:

- Input: latest disclosed director and supervisor shareholding
  percentage + pledge ratio (質押比率), with prior-quarter
  comparison where available
- Assess shareholding trend: increasing / stable / decreasing
  over the last 3 months (one disclosure cycle)
- **Flag — governance risk**: pledge ratio > 50% (threshold per
  葉銀華 2008 Taiwan governance research)
- **Flag — insider exit signal**: any single insider's disclosed
  holding declines by > 5% of their personal stake within one
  monthly window; or aggregate director/supervisor holdings decline
  by > 2 percentage points in one quarter

## Phase 5: 融資融券 Sentiment

Per `standards/taiwan-equity-frameworks.md` §融資融券:

- Input: 融資使用率 (margin utilization rate, %) + 融券占股本比率
  (short interest as % of outstanding shares) + 融資融券比
  (margin long balance / short balance)
- Assess margin temperature: 融資使用率 > 80% = overheated retail
  leverage; > 90% = extreme caution zone
- Assess crowding: high 融資融券比 = crowded long; low ratio with
  rising short interest = building bearish conviction
- **Flag — margin call pressure**: 融資 balance rising while price
  is declining over the same window (forced selling risk builds)
- **Flag — short squeeze potential**: 融券 balance rising
  significantly while price is advancing (bears losing ground)

## Phase 6: Regime Overlay

Per `standards/investment-macro-regime.md`:

- Apply current global Investment Clock (IC) regime call to the
  Taiwan equity context; map the four IC quadrants to expected
  Taiwan equity and sector behavior
- Apply Taiwan-specific adjustment: Taiwan's technology sector
  (semiconductors, OLED, AI server supply chain) is driven by AI
  capex cycles and smartphone upgrade cycles and may diverge
  materially from the global IC regime
- Cross-check: is the current 三大法人 外資 flow behavior
  consistent or inconsistent with the global IC regime call?
  Inconsistency is itself an information signal worth noting

## Phase 7: Synthesis and Verdict

Per `standards/investment-thesis-structure.md` and
`standards/decision-framework-and-verdict.md`:

- Compile a five-dimension summary table: revenue trend / 三大法人
  concordance / governance posture / sentiment temperature / regime
  alignment
- State a preliminary verdict: **accumulate** / **hold** / **reduce**
  with a two-to-four sentence rationale citing the dominant signals
- If any dimension produced a critical flag (Phase 2–5), address it
  explicitly in the rationale; do not bury flags in footnotes
- In `deep` mode: append L3 valuation section and full investment
  thesis from `protocols/deep-equity-research-memo.md`

## Output Template (zh-TW default)

```
## 台股診斷報告：{代號} {公司名稱} — {日期}

### 月營收趨勢
| 月份 | 營收 (千元) | MoM% | YoY% |
|------|------------|------|------|
| …    | …          | …    | …    |
3個月滾動YoY均值：X%　趨勢方向：加速 / 穩定 / 減速
旗標（如有）：…

### 三大法人動向（近20日）
| 機構 | 5日累計 | 20日累計 |
|------|---------|---------|
| 外資 | …       | …       |
| 投信 | …       | …       |
| 自營商 | …     | …       |
一致性評估：…　旗標（如有）：…

### 董監持股與質押
持股比例：X%（上季：X%）　質押比率：X%
趨勢：增加 / 穩定 / 減少　旗標（如有）：…

### 籌碼面（融資融券）
融資使用率：X%　融券占股本：X%　融資融券比：X
溫度評估：…　旗標（如有）：…

### 總經背景（景氣循環位置）
IC象限：…　外資行為與IC一致性：一致 / 背離
台股特殊調整：…

### 五維摘要
| 維度       | 訊號方向 | 旗標 |
|------------|---------|------|
| 月營收     | …       | …    |
| 三大法人   | …       | …    |
| 董監持股   | …       | …    |
| 融資融券   | …       | …    |
| 景氣循環   | …       | …    |

### 操作建議
初步判斷：**加碼 / 持有 / 減碼**
理由：…（2–4句，引用主要訊號）

### 資料來源
| 數據項目 | 來源 | 查詢日期 |
|---------|------|---------|
| …       | …    | …       |
```
