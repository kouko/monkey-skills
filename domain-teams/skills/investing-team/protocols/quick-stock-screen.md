# Quick Stock Screen Protocol

```yaml
---
name: quick-stock-screen
description: Single-ticker fast screen — one valuation framework, thesis skeleton, and a preliminary verdict in one pass
---
```

Designed for "give me a quick take on X" requests before committing to a
Deep Equity Research Memo. Completes in one model turn.

## Primary Sources

- `standards/investment-security-valuation.md` — L3 valuation framework
  selection and intrinsic value range computation
- `standards/investment-thesis-structure.md` — operative claim, variant
  perception delta, primary risk sentence structure
- `standards/decision-framework-and-verdict.md` — BUY/HOLD/SELL verdict
  rules, conviction grading (A/B/C)
- `standards/data-sources-and-fixtures.md` — provenance footer format,
  acceptable data source tiers, fixture protocol
- `standards/taiwan-equity-frameworks.md` — TWSE sector averages, P/B
  context, local market conventions (apply when .TW suffix detected)

---

## Phase 1: Scope Intake

**Input:** Ticker symbol from user (e.g., NVDA, 2330.TW, 9984.T)

1. Record ticker exactly as provided.
2. Detect market from suffix:
   - `.TW` → Taiwan Stock Exchange; load `taiwan-equity-frameworks.md`
     context for Phase 3
   - `.T` → Tokyo Stock Exchange
   - No suffix or `.US` → US equity (NYSE / NASDAQ default)
3. Note company name if known; do not hallucinate — leave blank if uncertain.
4. Ask: "Do you have a data fixture? If not, I will note gaps and proceed."
   If no fixture: proceed with explicit gap acknowledgment in Phase 6.

**Output:** Ticker, market, data-availability status

---

## Phase 2: Data Assembly

**Input:** Ticker, market, user-provided fixture (optional)

Minimum data set: current price, market cap or EV, trailing revenue (YoY
trend), trailing P/E or EV/EBITDA (if profitable), book value per share
(asset-heavy or Taiwan).

Rules:
- Mark unavailable items `[MISSING]` in provenance; do not fabricate.
- If ALL of price, market cap, and revenue are missing: output `BLOCKED`
  with suggested source (e.g., Yahoo Finance; TWSE MOPS for .TW).
- Accept partial data; flag gaps in every affected calculation.

**Output:** Populated data table with source and as-of date per item, or
BLOCKED status.

---

## Phase 3: Quick L3 Valuation (One Framework Only)

**Input:** Data table from Phase 2

Per `investment-security-valuation.md`, select **exactly one** framework
based on company profile:

| Company type | Framework to apply |
|---|---|
| Growth (low / no earnings, revenue growing >20% YoY) | EV/Revenue multiple OR DCF with explicit growth assumptions |
| Profitable mature (positive earnings, growth <20%) | P/E vs. sector median + EV/EBITDA sanity check |
| Asset-heavy (real estate, infrastructure, utilities) | P/Book or NAV |
| Taiwan listed | Apply selected framework PLUS check P/B vs. TWSE sector average |

Steps:
1. State framework choice and reason (one sentence).
2. List all input assumptions explicitly (growth rate, discount rate, margin,
   comparable set — whatever the chosen framework requires).
3. Compute Bear / Base / Bull intrinsic value: Bear = conservative inputs,
   Base = central case, Bull = optimistic inputs.
4. Position current price: below Bear → "undervalued"; within range →
   "fair value band"; above Bull → "overvalued".
5. If data gaps block numeric estimate: describe directional implication
   qualitatively and flag `[LOW CONFIDENCE]`.

**Output:** Framework name, assumptions, Bear/Base/Bull range, price position
label.

---

## Phase 4: Thesis Skeleton

**Input:** Valuation output, any additional context from user

Per `investment-thesis-structure.md`, write exactly three sentences:

1. **Operative claim** — "I believe [ticker] is [overvalued/undervalued/fairly
   valued] because [primary driver in one clause]."
2. **Variant perception delta** — "This differs from consensus in that
   [one specific disagreement with prevailing market view]."
   - If consensus is unknown: write "Consensus view unknown; this screen
     cannot assess variant perception."
3. **Primary risk** — "The biggest invalidator of this thesis is [specific
   falsifiable condition]."

Do not expand beyond three sentences. This is a skeleton, not a memo.

**Output:** Three-sentence thesis skeleton.

---

## Phase 5: Preliminary Verdict

**Input:** Valuation output, thesis skeleton

Per `decision-framework-and-verdict.md`:

1. Issue one verdict: **BUY** / **HOLD** / **SELL**
2. Write rationale in 1–2 sentences connecting valuation position to thesis.
3. Assign conviction grade:
   - Default: **Grade C** (quick screen, limited data)
   - Upgrade to **Grade B** only if user explicitly stated "I have strong
     conviction" or provided a comprehensive data fixture
   - Grade A is not available from this protocol — it requires the deep
     equity research memo
4. Append the following note verbatim:
   > "This is a quick screen (Grade C conviction). For Grade A analysis,
   > run the Deep Equity Research Memo protocol."

**Output:** Verdict line (BUY/HOLD/SELL), conviction grade, rationale,
upgrade note.

---

## Phase 6: Provenance Footer

**Input:** All data items used across Phases 2–5

Per `data-sources-and-fixtures.md`, produce a table:

| Data item | Value used | Source | As-of date | Gap flag |
|---|---|---|---|---|
| ... | ... | ... | ... | — or [MISSING] |

Every numeric input to Phase 3 must appear. Source = "user-provided fixture"
or "Model prior — verify independently" + `[LOW CONFIDENCE]` flag.

---

## Output Format

Assemble the final response in this exact structure:

```
## Quick Screen: {TICKER} — {DATE}

### Valuation
[Framework used and why]
[Assumptions: list each input]
[Bear / Base / Bull intrinsic value range]
[Current price: {price} — {overvalued / fair value band / undervalued}]

### Thesis Skeleton
1. {Operative claim}
2. {Variant perception delta}
3. {Primary risk}

### Preliminary Verdict
{BUY / HOLD / SELL} — Conviction: Grade {C or B}
{1–2 sentence rationale}
> "This is a quick screen (Grade C conviction). For Grade A analysis,
> run the Deep Equity Research Memo protocol."

### Provenance
| Data item | Value used | Source | As-of date | Gap flag |
|---|---|---|---|---|
| ... | ... | ... | ... | ... |
```

Do not add sections beyond those listed above. Do not editorialize outside
the defined fields.
