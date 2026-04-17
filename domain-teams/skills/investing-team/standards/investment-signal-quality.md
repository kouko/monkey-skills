# Investment Signal Quality (ISQ)

## Purpose

ISQ assesses the **credibility of an analysis conclusion** — not the stock
itself. After a memo, verdict, or regime call is produced, ISQ answers:
"How much should I trust this conclusion?"

ISQ is orthogonal to quality gates:
- Gates check **process compliance** ("Did you cite sources? Is the thesis structured?")
- ISQ checks **conclusion credibility** ("Is this conclusion well-supported and actionable?")

## Primary Source

Framework adapted from Dexter Kabu JP (raditrejp/dexter-kabu-jp),
`src/tools/signal/isq.ts`. Original formula preserved; dimension
definitions expanded with investing-team context.

---

## ISQ Dimensions

### 1. Confidence (weight: 35%)

How certain is the analysis given available data and reasoning?

| Score | Condition |
|-------|-----------|
| 0.9–1.0 | Multiple independent data sources confirm; primary-source grounded; assumptions validated |
| 0.7–0.8 | Data adequate; key assumptions stated and reasonable; minor gaps noted |
| 0.5–0.6 | Partial data; some assumptions unverified; acknowledged uncertainty |
| 0.3–0.4 | Significant data gaps; speculative assumptions; low citation density |
| 0.0–0.2 | Mostly LLM recall; no primary source anchoring; critical data missing |

**Anchoring question**: "If I had to bet money on this conclusion, how confident am I in the supporting evidence?"

---

### 2. Intensity / Strength (weight: 30%)

How strong is the signal? Scale 1–5, normalized by ÷5.

| Score | Condition |
|-------|-----------|
| 5 | Extreme signal: deep margin of safety (>40%), regime inflection, multiple converging catalysts |
| 4 | Strong signal: clear valuation gap, sector tailwind, identifiable catalyst |
| 3 | Moderate signal: reasonable thesis but no overwhelming evidence |
| 2 | Weak signal: marginal thesis, mixed indicators, no clear catalyst |
| 1 | Noise: contradictory signals, no coherent thesis, pure speculation |

**Anchoring question**: "If 100 analysts saw this data, how many would reach the same conclusion?"

---

### 3. Expectation Gap (weight: 20%)

How much does this conclusion diverge from market consensus?

| Score | Condition |
|-------|-----------|
| 0.9–1.0 | Strong variant perception: market clearly mispricing; explicit contrarian thesis with falsifiable catalyst |
| 0.6–0.8 | Moderate gap: market partially aware but underweighting a factor |
| 0.3–0.5 | Small gap: conclusion aligns with consensus; limited alpha potential |
| 0.0–0.2 | No gap: conclusion IS the consensus; this analysis adds no new insight |

**Anchoring question**: "Does this analysis tell the investor something the market doesn't already know?"

High expectation gap + high confidence = strongest actionable signal.
High expectation gap + low confidence = speculative contrarian = risky.

---

### 4. Timeliness (weight: 15%)

How time-sensitive is this conclusion?

| Score | Condition |
|-------|-----------|
| 0.9–1.0 | Imminent catalyst (earnings next week, regulatory decision, M&A deadline) |
| 0.6–0.8 | Near-term relevance (1–3 months); thesis still forming |
| 0.3–0.5 | Medium-term (3–12 months); structural thesis, no urgency |
| 0.0–0.2 | No time dependency; evergreen observation; data already stale |

**Anchoring question**: "If I read this analysis 30 days from now, would it still be actionable?"

---

## ISQ Formula

```
isq_score = confidence × 0.35
          + (intensity / 5) × 0.30
          + expectation_gap × 0.20
          + timeliness × 0.15
```

Score range: 0.0 – 1.0

## Signal Labels

| Score | Label | Interpretation |
|-------|-------|---------------|
| ≥ 0.8 | **Strong Signal** (強シグナル) | High-conviction, actionable conclusion |
| 0.6–0.8 | **Medium Signal** (中シグナル) | Reasonable conclusion, act with position sizing discipline |
| 0.4–0.6 | **Weak Signal** (弱シグナル) | Low conviction; use as input, not as standalone decision basis |
| < 0.4 | **Noise** (ノイズ) | Insufficient evidence; do not act on this conclusion |

---

## When ISQ Applies

ISQ evaluates the **final output** of an investing-team workflow:

| Workflow | ISQ applies to |
|----------|---------------|
| Deep Equity Research Memo | The BUY/HOLD/SELL verdict + target price |
| Quick Stock Screen | The screen card's assessment |
| Portfolio Review | The rebalance recommendations |
| Macro Regime Diagnosis | The IC phase call + asset-class tilts |
| Taiwan-Specific Diagnosis | The verdict + sizing |

ISQ does NOT apply to intermediate steps (data fixtures, individual gate verdicts).

---

## ISQ Output Format

Append to the end of the investing-team delivery:

```markdown
### Signal Quality (ISQ)

| Dimension | Score | Note |
|-----------|-------|------|
| Confidence | 0.75 | 2 primary sources, FRED data fresh, yfinance PE stale by 1 day |
| Intensity | 4/5 (0.80) | Clear valuation gap + regime tailwind |
| Expectation Gap | 0.65 | Market underweighting China demand recovery catalyst |
| Timeliness | 0.70 | Earnings in 3 weeks; catalyst window open |

**ISQ Score**: 0.74 — **Medium Signal**
_Act with position sizing discipline. Strengthen conviction with additional data before full position._
```

---

## Interaction with Gates

ISQ is NOT a pass/fail gate. It is an informational annotation:
- A memo can **PASS** all MUST gates but receive ISQ = 0.35 (Noise) — meaning
  the analysis followed correct process but the conclusion lacks evidence
- A memo can have ISQ = 0.90 (Strong) and still **FAIL** a MUST gate — meaning
  the conclusion may be correct but the process was flawed

Both signals are valuable and should be presented together.
