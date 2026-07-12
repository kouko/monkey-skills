---
name: investment-thesis-soundness-checklist
description: MUST gate — thesis has all 5 structural components, variant perception is genuine, pre-mortem is present
gate_tier: MUST
---

# Investment Thesis Soundness Checklist

## Primary Sources

- `standards/investment-thesis-structure.md` — operative claim, variant perception, catalyst, invalidator, pre-mortem definitions
- `standards/conviction-grading.md` — Grade A/B/C definitions and pre-mortem triggering rules
- `checklists/primary-source-citation-compliance.md` — Provenance Footer requirements (CHK-CIT-005)

## Prerequisites

This gate applies to any output that makes a directional investment
recommendation (BUY, SELL, SHORT, HOLD with a specific rationale).
For pure data screens or regime-only macro notes without a specific
security recommendation, mark all items N/A with justification.

## Evaluation Instructions

You are a rigorous investment analyst evaluating thesis quality.
Check each item below against the output. Mark each item ✅ PASS
or ❌ FAIL with specific evidence. Apply N/A only where explicitly
permitted and provide a justification.

## Checklist

- [ ] **CHK-THX-001 (Operative Claim Present)**: The output contains a single unambiguous sentence of the form "I believe {company/asset} is {undervalued/overvalued/mispriced} because {specific reason}." Vague formulations ("this looks interesting," "there may be upside here") do not satisfy. The sentence must be locatable by the evaluator.

- [ ] **CHK-THX-002 (Genuine Variant Perception)**: The thesis names a specific way the author's view diverges from consensus or market-implied assumptions. "This is a quality company" or "management is excellent" is NOT variant perception. An acceptable example: "The market prices in 3% terminal growth; my base case supports 7% because of platform switching costs the sell-side underweights." The divergence must be named and measurable.

- [ ] **CHK-THX-003 (Falsifiable Catalyst with Observable Trigger)**: The thesis names at least one catalyst that, if it fires, will cause market repricing — and specifies a concrete observable condition that would confirm it fired (e.g., "Q3 revenue beat >10% YoY triggers 外資 buying, which re-rates the multiple from 12x to 15x"). A catalyst with no observable trigger or no repricing mechanism is a FAIL.

- [ ] **CHK-THX-004 (Explicit Invalidator)**: The output lists at least one condition that would prove the thesis wrong. The invalidator must be specific and observable (e.g., "If gross margin falls below 38% for two consecutive quarters, the pricing power thesis is invalidated"). Generic statements like "if the macro worsens" without a measurable threshold are a FAIL.

- [ ] **CHK-THX-005 (Pre-mortem Present for Grade A/B)**: For outputs assigned a Grade A or Grade B conviction, the output imagines the thesis failing in the future and identifies the single most likely cause of that failure. Grade C conviction outputs may skip this item — mark N/A with the Grade C notation.

- [ ] **CHK-THX-006 (Provenance Footer Records Data Sources)**: Each factual claim used to build the thesis traces to a Provenance Footer entry per CHK-CIT-005 in `checklists/primary-source-citation-compliance.md`. This item directly delegates to the citation compliance gate — if CHK-CIT-005 already passed, this item passes.

- [ ] **CHK-THX-007 (Rule-Verdict Adoption or Valid Deviation Block)**: When the input carries a machine-computed `rule_verdict`, the declared verdict either matches it, or the output contains a Deviation Block (per the protocol's Verdict section). For a Deviation Block, the evaluator MUST recompute: (a) every adjustment figure traces to a data file or cited primary source — an adjustment appearing in no source is a FAIL; (b) applying the adjustment, the recomputed threshold(s) no longer trigger the original `rule_verdict` — if the recomputed threshold is still breached by the current price, the deviation is arithmetically void and this item is a FAIL; (c) the block contains the anchoring/endowment self-check. Mark N/A when no `rule_verdict` was provided in the input.

## Verdict Rules

- ✅ All applicable items PASS → **PASS**
- ❌ Any of CHK-THX-001 through CHK-THX-004, or CHK-THX-007, FAIL → **NEEDS_REVISION**
- ❌ Only CHK-THX-005 or CHK-THX-006 FAIL with a Grade C verdict → **PASS_WITH_NOTES** (note the gap; do not escalate to full revision)

## Output Format

```json
{
  "verdict": "PASS | PASS_WITH_NOTES | NEEDS_REVISION",
  "checklist_results": [
    {
      "id": "CHK-THX-001",
      "status": "PASS | FAIL | N/A",
      "evidence": "Quoted or paraphrased content from the output confirming or failing the item",
      "fix_instruction": "How to resolve (for FAIL items only)"
    }
  ],
  "notes": "Required if verdict is PASS_WITH_NOTES — describe the specific gap"
}
```
