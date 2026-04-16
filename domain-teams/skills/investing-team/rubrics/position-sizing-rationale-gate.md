---
name: position-sizing-rationale-gate
description: SHOULD gate — position size is justified via Kelly/risk-budget/vol-targeting, not arbitrary
gate_tier: SHOULD
---

# Position Sizing Rationale Gate

## Primary Sources

- `standards/position-sizing-and-risk.md` — Kelly criterion, volatility targeting, risk-budget allocation, Grade A/B/C size limits, hard cap rules
- `standards/conviction-grading.md` — Grade A (≤15%), Grade B (≤8%), Grade C (≤3%) size ceilings
- `standards/investment-thesis-structure.md` — conviction grade definition and its role in sizing decisions

## Prerequisites

This gate applies to any output that recommends taking or adjusting
a portfolio position. Pure screening outputs, watchlist additions,
and outputs that explicitly defer sizing to the user are exempt —
mark all criteria N/A with justification.

## Evaluation Instructions

You are evaluating whether position sizing is principled and
internally consistent. Rate each criterion 🟢/🟡/🔴.
Apply the N/A path for Criterion 4 only when the position is
unlevered long-only equity with no options overlay.

## Rubric Criteria

### Criterion 1: Sizing Method Identified

Does the output name a recognized sizing methodology?

- 🟢 Explicitly names and applies one of: fractional Kelly (with stated edge and win-rate inputs), volatility targeting (with target vol % and asset vol %), or risk-budget allocation (with portfolio risk budget and asset contribution). The method name and its key inputs both appear.
- 🟡 A sizing figure is stated and some rationale is given, but the method is not named or the key inputs are missing (e.g., "I size this at 5% because I have high conviction" — conviction stated but Kelly/vol/budget framework absent).
- 🔴 No sizing rationale at all; or size is a round number stated without any justification ("I'd put 10% in it"); or method is named but none of its required inputs are provided.

### Criterion 2: Conviction Grade Drives Size

Is the recommended position size consistent with the assigned conviction grade ceiling?

- 🟢 Conviction grade is assigned (A, B, or C) and the recommended size respects the grade ceiling from `standards/position-sizing-and-risk.md`: Grade A ≤15%, Grade B ≤8%, Grade C ≤3%. The grade and the size are both explicit and consistent.
- 🟡 Conviction grade is assigned but the size is not explicitly mapped to the grade ceiling (e.g., Grade B assigned, 6% size recommended, but the output does not confirm this is within the 8% cap).
- 🔴 Recommended size exceeds the conviction grade ceiling without explicit justification for the override; or no conviction grade is assigned and sizing floats without an anchor.

### Criterion 3: Hard Cap Respected

Does the recommended size stay within the 20–25% portfolio hard cap?

- 🟢 Recommended size is ≤20% of the portfolio. Or, if between 20–25%, the output explicitly acknowledges proximity to the cap and provides a rationale for the elevated concentration.
- 🟡 Size is in the 20–25% range with only passing acknowledgment of the cap (e.g., "this is a large position") without a substantive rationale for why concentration is justified.
- 🔴 Recommended size exceeds 25% of the portfolio without any explicit discussion of the hard cap override, or the output is silent on concentration risk entirely.

### Criterion 4: Fat-Tail / Asymmetric Risk Acknowledged

For levered or options-like positions: is tail risk explicitly bounded?

- 🟢 For levered positions or positions with embedded optionality: a Taleb fragility check is present (position bounded so total portfolio loss is survivable if position goes to zero), or the output explicitly states the maximum loss scenario and confirms it is within the portfolio's drawdown tolerance.
- 🟡 Asymmetric risk or leverage is mentioned but not quantified (e.g., "this has downside risk if it goes against us" without stating the bounded loss amount).
- 🔴 Levered, leveraged-ETF, or long-options position is sized with no fat-tail consideration or maximum-loss scenario analysis.
- N/A: Unlevered long-only equity position with no options overlay — mark N/A, no justification required beyond confirming the position type.

## Verdict Rules

- **PASS**: All applicable criteria 🟢 (N/A criteria excluded from verdict)
- **PASS_WITH_NOTES**: Any 🟡, no 🔴 — list each yellow criterion with a specific fix instruction
- **NEEDS_REVISION**: Any 🔴

## Output Format

1. **Criterion ratings**: `[🟢 / 🟡 / 🔴 / N/A — Criterion Name]` with one sentence of evidence
2. **Fix Instructions**: For each 🟡 or 🔴, a concrete fix instruction referencing `standards/position-sizing-and-risk.md`
3. **Verdict**: PASS / PASS_WITH_NOTES / NEEDS_REVISION

Never accept "I have high conviction" as a sizing methodology. If the method is absent, flag 🔴.
