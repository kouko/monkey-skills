---
name: scenario-stress-test-gate
description: SHOULD gate — memo enumerates bull/base/bear scenarios with explicit assumptions and probability weights
gate_tier: SHOULD
---

# Scenario Stress Test Gate

## Primary Sources

- `standards/investment-thesis-structure.md` — scenario analysis structure requirements
- `standards/conviction-grading.md` — Grade A/B/C thresholds that govern expected-value requirements
- `protocols/investment-memo.md` — memo section ordering and scenario placement

## Prerequisites

This gate applies to any full investment memo or recommendation with
a price target or expected-return claim. Quick screens, watchlist
additions, and regime-only macro notes are exempt — mark all
criteria N/A with justification.

## Evaluation Instructions

You are evaluating the completeness and rigor of scenario analysis
in an investing-team output. Rate each criterion 🟢/🟡/🔴.
Be strict: narrative hand-waving without explicit numbers is 🟡,
not 🟢.

## Rubric Criteria

### Criterion 1: Scenario Coverage

Does the output enumerate at least three distinct scenarios with meaningfully different premises?

- 🟢 Bull, Base, and Bear all present; each scenario has a distinct set of causal premises that differentiate it from the others. The three cases are not just relabelings of the same outcome.
- 🟡 Only 2 of 3 scenarios present; or all 3 are labeled but two are effectively identical (e.g., Bull and Base share the same revenue assumptions).
- 🔴 No scenarios enumerated; or scenarios described only as directional outcomes ("stock goes up" / "stock goes down") without explicit causal assumptions.

### Criterion 2: Conditioning Variables Explicit

Does each scenario state which specific input assumptions differ from the base case?

- 🟢 Each scenario explicitly names the variables that change and their values (e.g., "Bull: revenue growth 28% vs. Base 15%; GM expands 200bps from contract renegotiation. Bear: GM compresses 300bps from new competitor entry; revenue growth 6%"). Numbers are present — not just narrative descriptions.
- 🟡 Scenarios described in narrative terms that imply different assumptions but do not state them as explicit numbers (e.g., "Bull case assumes strong demand recovery" without quantifying what "strong" means).
- 🔴 Scenarios described only as target prices or EPS outcomes without any stated causal premises (e.g., "Bull: stock to NT$400; Bear: stock to NT$200").

### Criterion 3: Probability Weights Assigned

Are probability weights assigned to each scenario, and do they sum to 100%?

- 🟢 Each scenario is assigned an explicit probability; weights sum to 100%; the distribution is plausible given the thesis conviction (e.g., Grade B: Bull 25%, Base 55%, Bear 20%).
- 🟡 Probabilities present but do not sum to 100%; or the distribution is clearly asymmetric without stated justification (e.g., Bull 70% with no rationale for heavy skew); or probabilities are described qualitatively ("likely," "unlikely") without numbers.
- 🔴 No probability weights; or all three scenarios are implicitly treated as equally probable (33%/33%/33%) without discussion.

### Criterion 4: Expected Value Calculated

Is a probability-weighted expected return computed and stated?

- 🟢 Expected return = Σ(probability × scenario return) is computed and explicitly stated in the output. The formula or its result appears in the memo.
- 🟡 Expected value is not computed, but scenarios and probabilities are both present and clearly structured so the reader can compute it in one step.
- 🔴 Neither scenario-level returns nor an expected value figure is present; or expected return is stated as a round number without traceable calculation.

## Verdict Rules

- **PASS**: All four criteria 🟢
- **PASS_WITH_NOTES**: Any 🟡, no 🔴 — list each yellow criterion with the specific gap and a fix instruction
- **NEEDS_REVISION**: Any 🔴

## Output Format

1. **Criterion ratings**: `[🟢 / 🟡 / 🔴 Criterion Name]` with one sentence of evidence
2. **Fix Instructions**: For each 🟡 or 🔴, a concrete fix instruction
3. **Verdict**: PASS / PASS_WITH_NOTES / NEEDS_REVISION

Never sugar-coat. If numbers are absent, say so directly.
