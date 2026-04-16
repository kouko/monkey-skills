# Portfolio Review Protocol

```yaml
---
name: portfolio-review
description: Portfolio allocation audit — regime consistency, concentration risk, rebalance proposal
---
```

Designed for reviewing an existing multi-position portfolio. Produces weight
recommendations only — not individual stock verdicts.

## Primary Sources

- `standards/investment-macro-regime.md` — L1 regime overlay (4-quadrant
  Greetham/Hartnett Investment Clock + Hedgeye GIP refinement); regime-to-
  asset-class mapping tables
- `standards/investment-portfolio-construction.md` — Barbell strategy,
  Risk Parity principles, concentration thresholds, allocation philosophy
- `standards/investment-sector-industry.md` — GICS sector taxonomy,
  Fama-French factor definitions (Value / Growth / Momentum / Quality /
  Size); factor-tilt identification
- `standards/position-sizing-and-risk.md` — conviction grade to position
  size mapping (Grade A / B / C), over-risk identification rules
- `standards/data-sources-and-fixtures.md` — provenance footer format,
  acceptable data source tiers

---

## Input Requirements

Minimum required:
- Holdings list: ticker and weight (% or absolute value)

Optional but improves output quality:
- Entry price per position
- Current price per position
- Target risk budget (e.g., max drawdown tolerance)
- Investment horizon (e.g., 1 year, 3–5 years, long-term)
- Liquidity constraints (e.g., cannot sell X for N months)
- User's current regime call

If holdings list is absent entirely: output `BLOCKED` — no portfolio review
is possible without holdings data.

---

## Phase 1: Holdings Intake and Normalization

**Input:** Holdings list in any format (table, CSV paste, natural language)

1. Parse all holdings. Accept table, CSV, or natural language prose.
2. Normalize to percentage weights:
   - Absolute values given: weight = position value / total portfolio value
   - Shares given but no prices: request prices OR note weights are
     approximate
3. Assign asset class: Equity (domestic/intl/EM), Fixed income (govt/
   corp/HY), Commodity, REIT, Cash, Alternative/crypto, or Unknown.
4. If current prices missing: note Phase 2 will use asset-class-level
   approximations, not individual-security data.

**Output:** Normalized weight table with ticker, weight %, asset class tag,
and any normalization notes.

---

## Phase 2: L1 Regime Overlay

**Input:** Normalized holdings table, user's regime call (optional)

Per `investment-macro-regime.md`:

1. Establish current regime: use user's call if provided; otherwise derive
   from the Growth/Inflation quadrant framework (rough — recommend user
   verify). Valid labels: Reflation (↑growth ↑inflation) / Goldilocks
   (↑growth ↓inflation) / Stagflation (↓growth ↑inflation) / Deflation
   (↓growth ↓inflation).
2. Map each asset class to the regime's favored / neutral / disfavored
   category per `investment-macro-regime.md` tables.
3. Flag regime-inconsistent positions (flag = note + explain; not auto-sell).
   Ask user if flagged weight is intentional.
4. Score aggregate consistency: Regime-aligned >60% / Mixed 40–60% /
   Regime-misaligned <40% of portfolio weight in favored/neutral assets.

**Output:** Regime label, per-asset-class mapping, flagged positions,
aggregate consistency label.

---

## Phase 3: Concentration and Factor Checks

**Input:** Normalized holdings table

Per `investment-portfolio-construction.md` and
`investment-sector-industry.md`:

**Concentration checks (hard flags):**
- Any single position > 15% of portfolio → hard concentration flag
- Any single GICS sector > 30% of portfolio → sector concentration flag
- Cash + cash equivalents > 40% → note as potential opportunity cost risk
  (not a hard flag — may be intentional)

**Factor tilt identification** (Fama-French definitions in
`investment-sector-industry.md`): flag if >40% weight concentrated in one
factor — Value (low P/B, P/E), Growth (high rev growth, high P/E), Quality
(high ROE, low leverage), or Size (small-cap / large-cap skew). Note tilts;
recommend reducing only if they conflict with user's horizon or risk budget.

**Output:** List of hard concentration flags (if any), sector concentration
flags (if any), factor tilt summary.

---

## Phase 4: Risk Budget Assessment

**Input:** Normalized holdings table, conviction grades (if known)

Per `position-sizing-and-risk.md`:

1. Record conviction grade per holding if user provided (A = deep research;
   B = partial research; C = quick screen / speculative; ? = ungraded).
2. Cross-check size vs. grade:
   - Grade A: up to ~15–20% appropriate
   - Grade B: up to ~8–12% appropriate
   - Grade C: up to ~3–5% appropriate; >8% = over-risk flag
3. If no grades provided: note risk budget assessment is incomplete.
4. Flag any ungraded position >10% as "ungraded concentration risk."

**Output:** Per-holding conviction / size alignment table, over-risk flags,
ungraded concentration flags.

---

## Phase 5: Rebalance Proposal

**Input:** Outputs from Phases 2, 3, 4; optional liquidity constraints

Propose specific weight adjustments. This is a weight-target recommendation,
not a trade order or timing signal.

Prioritization order (address in this sequence):
1. Fix hard concentration flags (single position >15%)
2. Fix regime-inconsistent positions (unless user confirmed intentional)
3. Align sizing with conviction grades (fix over-risk flags)
4. (Optional, lower priority) Reduce factor tilts if they conflict with
   user's stated horizon or risk budget

Rules:
- Apply liquidity constraints: do not propose reducing positions the user
  flagged as illiquid within their stated horizon
- Do not propose weight changes smaller than 2% (noise, not signal)
- Sum of proposed weights must equal 100% (or note any residual as cash)
- Label each change with the reason code: [CONCENTRATION] / [REGIME] /
  [CONVICTION-SIZING] / [FACTOR-TILT] / [OPTIONAL]

Present as table:

| Ticker | Current % | Proposed % | Change | Reason |
|---|---|---|---|---|
| ... | ... | ... | ... | ... |

If no changes are warranted: state "No rebalance actions triggered — portfolio
passes all concentration, regime, and conviction-sizing checks."

**Output:** Rebalance proposal table or no-action statement, with rationale
per line.

---

## Phase 6: Output Assembly

Assemble the final response in this exact structure:

```
## Portfolio Review: {DATE}

### Holdings Summary
| Ticker | Weight % | Asset Class | Notes |
|---|---|---|---|
Total positions: {N} | Total weight: 100% | [Normalization notes if any]

### Regime Consistency
Regime: {Reflation / Goldilocks / Stagflation / Deflation}
Overall: {Regime-aligned / Mixed / Regime-misaligned}
| Ticker | Asset Class | Regime Stance | Flag? |
|---|---|---|---|
[Notes on any flagged positions]

### Concentration Flags
[Hard flags, or "None"] | Factor tilt: {summary}

### Risk Budget
| Ticker | Conviction | Current % | Appropriate range | Flag? |
|---|---|---|---|---|

### Rebalance Proposal
| Ticker | Current % | Proposed % | Change | Reason |
|---|---|---|---|---|
[Or: "No rebalance actions triggered."]

### Provenance
| Data item | Value used | Source | As-of date |
|---|---|---|---|
```

**Scope reminder:** Weight recommendations only. For stock-level verdicts
run Quick Stock Screen or Deep Equity Research Memo on specific holdings.
