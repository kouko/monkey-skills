---
name: signal-quality-assessment-gate
description: SHOULD gate — assess the credibility of the analysis conclusion via ISQ (Investment Signal Quality) 4-dimension scoring
gate_tier: SHOULD
---

# Signal Quality Assessment Gate (ISQ)

## Primary Sources

- `standards/investment-signal-quality.md` — ISQ framework definition, scoring formula, dimension rubrics
- `standards/investment-thesis-structure.md` — thesis structure that ISQ evaluates
- `standards/decision-framework-and-verdict.md` — verdict conditions that ISQ quality-checks

## Prerequisites

This gate applies to any investing-team output that contains a **conclusion**:
- BUY / HOLD / SELL verdict
- Rebalance recommendation
- Macro regime call with asset-class tilts
- Price target or expected return

Quick data lookups (snapshot cards without verdict) are exempt — mark all
criteria N/A with justification.

## Evaluation Instructions

You are evaluating the **credibility of the analysis conclusion**, not
the quality of the process (that is handled by MUST gates). Read the
full memo output, then score each ISQ dimension independently.

Reference `standards/investment-signal-quality.md` for dimension
definitions, score ranges, and anchoring questions.

## Rubric Criteria

### ISQ-1: Confidence (35%)

Rate the evidence base supporting the conclusion.

| 🟢 | 🟡 | 🔴 |
|----|----|----|
| Multiple independent primary sources cited; key assumptions explicitly stated and cross-verified; data gaps acknowledged with stated impact | Adequate sourcing but some assumptions unverified; minor data gaps not explicitly addressed | Mostly LLM recall; few or no primary sources; critical assumptions unstated; conclusion outpaces evidence |

Score: ___ / 1.0

---

### ISQ-2: Intensity / Strength (30%)

Rate the strength of the investment signal.

| 🟢 | 🟡 | 🔴 |
|----|----|----|
| Clear valuation gap with quantified margin of safety; identifiable catalyst with timeline; multiple converging indicators | Reasonable thesis but catalyst vague or timeline uncertain; some indicators mixed | No coherent thesis; contradictory indicators; conclusion reads as a guess rather than a reasoned position |

Score: ___ / 5 (normalize to 0–1 by ÷5)

---

### ISQ-3: Expectation Gap (20%)

Rate how much this conclusion diverges from market consensus.

| 🟢 | 🟡 | 🔴 |
|----|----|----|
| Explicit variant perception: states what the market is missing and why; falsifiable catalyst identified; contrarian view with evidence | Some differentiation from consensus but not explicitly articulated; partially overlaps sell-side views | Conclusion IS the consensus; restates known information; no alpha insight |

Score: ___ / 1.0

---

### ISQ-4: Timeliness (15%)

Rate the time-sensitivity and actionability of the conclusion.

| 🟢 | 🟡 | 🔴 |
|----|----|----|
| Imminent catalyst (< 1 month); data is current (fetched within days); window of opportunity clearly stated | Near-term relevance (1–3 months); data reasonably fresh; no urgency stated but thesis is time-bounded | No time dependency; data may be stale; conclusion would be identical 6 months ago |

Score: ___ / 1.0

---

## Scoring

Compute ISQ score:

```
isq = (confidence × 0.35) + ((intensity / 5) × 0.30) + (expectation_gap × 0.20) + (timeliness × 0.15)
```

## Verdict

| ISQ Score | Label | Gate Verdict |
|-----------|-------|-------------|
| ≥ 0.8 | Strong Signal | PASS |
| 0.6–0.8 | Medium Signal | PASS_WITH_NOTES — note dimensions below 0.6 |
| 0.4–0.6 | Weak Signal | PASS_WITH_NOTES — recommend additional data before acting |
| < 0.4 | Noise | PASS_WITH_NOTES — flag as low-credibility; do not suppress output |

ISQ is informational — it never produces FAIL. Even Noise-level conclusions
are delivered to the user with the ISQ annotation visible, so the user can
make their own judgment.

## Output Format

```markdown
### Signal Quality (ISQ)

| Dimension | Score | Note |
|-----------|-------|------|
| Confidence | {score} | {brief justification} |
| Intensity | {raw}/5 ({normalized}) | {brief justification} |
| Expectation Gap | {score} | {brief justification} |
| Timeliness | {score} | {brief justification} |

**ISQ Score**: {total} — **{label}**
_{one-sentence actionability note}_
```
