---
name: market-regime-consistency-gate
description: SHOULD gate — security recommendation coheres with the stated L1 macro regime call
gate_tier: SHOULD
---

# Market Regime Consistency Gate

## Primary Sources

- `standards/investment-macro-regime.md` — Investment Clock quadrant definitions, favored/disfavored asset classes per quadrant, Greetham & Hartnett 2004 framework
- `standards/investment-thesis-structure.md` — L1/L2/L3 analysis hierarchy; regime as L1 context
- `research/investment-clock-grounding.md` — empirical grounding and quadrant-to-sector mapping

## Prerequisites

This gate applies to any output that recommends a specific security
or asset-class position. Pure macro regime assessments (no security
recommendation) are exempt — mark all criteria N/A with
justification.

## Evaluation Instructions

You are evaluating whether the security recommendation is coherent
with the stated macro regime. Rate each criterion 🟢/🟡/🔴.
A recommendation that explicitly acknowledges regime tension and
argues through it is 🟢 — the gate rewards transparency, not
mechanical regime-following.

## Rubric Criteria

### Criterion 1: Regime Stated

Does the output explicitly identify the current Investment Clock quadrant?

- 🟢 The Investment Clock quadrant (Reflation, Overheat, Stagflation, or Recovery) is explicitly named, with at least two supporting data points (e.g., yield curve slope, CPI trajectory, PMI direction, or central bank posture) that justify the quadrant assignment.
- 🟡 The macro environment is described in narrative terms ("inflationary environment," "late-cycle conditions," "risk-off backdrop") without mapping to a specific Investment Clock quadrant or citing supporting data.
- 🔴 No regime context provided; or the output explicitly claims "regime doesn't matter for this stock" without any supporting argument for why the stock is regime-neutral.

### Criterion 2: Recommendation is Regime-Consistent

Does the security's sector or asset class sit in a favored or neutral zone for the stated regime?

- 🟢 The security's asset class or sector is in the favored or neutral quadrant for the stated regime per `standards/investment-macro-regime.md` §Quadrant Asset Allocation. Or, if the security is in a disfavored sector, a documented exception exists (see Criterion 3).
- 🟡 The security is in a disfavored or neutral sector but the regime tension is acknowledged without a full exception argument (e.g., "utilities are usually weak in Overheat but this one has a contracted revenue stream").
- 🔴 The security is in a clearly disfavored sector for the stated regime (e.g., a BUY on commodity equities during a Stagflation quadrant call, or a BUY on rate-sensitive REITs during Overheat) with no regime caveat of any kind.

### Criterion 3: Exception Logic Documented (if applicable)

If the recommendation goes against the regime, is the exception explicitly reasoned?

- 🟢 The exception is explicitly argued with company-specific or asset-specific evidence that insulates the position from regime headwinds (e.g., "Despite Stagflation regime disfavoring equities broadly, this company has multi-year fixed-price supplier contracts and 85% recurring revenue, which decouples its earnings from the macro cycle in the following ways..."). The exception is substantive, not a label.
- 🟡 Exception mentioned but reasoning is thin or circular (e.g., "this is a special case," "this company is different," or restating the thesis without connecting it to why the regime headwind does not apply).
- 🔴 No exception documented for a clearly regime-inconsistent recommendation — the output simply ignores the regime conflict.
- N/A: Recommendation is regime-aligned (Criteria 1 and 2 both 🟢) or the position is regime-neutral by asset class (cash, short-duration govvies) — mark N/A, confirm which condition applies.

## Verdict Rules

- **PASS**: All applicable criteria 🟢 (N/A criteria excluded from verdict)
- **PASS_WITH_NOTES**: Any 🟡, no 🔴 — list each yellow criterion with the specific gap and a fix instruction
- **NEEDS_REVISION**: Any 🔴

## Output Format

1. **Criterion ratings**: `[🟢 / 🟡 / 🔴 / N/A — Criterion Name]` with one sentence of evidence
2. **Fix Instructions**: For each 🟡 or 🔴, a concrete fix instruction referencing `standards/investment-macro-regime.md`
3. **Verdict**: PASS / PASS_WITH_NOTES / NEEDS_REVISION

A regime conflict that is explicitly acknowledged and argued through is not a failure. A regime conflict that is silently ignored is always 🔴.
