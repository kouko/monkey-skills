# Protocol: Reverse-Toulmin

Standard Toulmin moves from grounds → warrant → claim. **Reverse-Toulmin**
goes the other direction: starting from the claim, work backward to
extract every assumption the claim depends on.

## Why reverse direction

Toulmin (forward) says: "this argument is constructed by stacking
ground + warrant + backing → claim." Useful when you want to *evaluate*
a single argument's logical structure.

Reverse-Toulmin says: "given this claim, what *must already be true*
for it to make sense?" Useful when you want to *map all hidden
infrastructure* a text rests on, faster than full Toulmin per claim.

## Procedure

For each claim:

### Step 1: State the claim verbatim

Don't paraphrase. Use the writer's words.

### Step 2: Ask the assumption-extraction question

Three forms, run all three:

1. **Logical**: "What must be true *categorically* for this claim to even be coherent?"
2. **Empirical**: "What facts must hold *in this specific case* for the claim to be true?"
3. **Methodological**: "What would have had to *be measured / observed / decided* in some prior step for this claim to be available?"

### Step 3: Write each answer as an assumption

Use the form: "**Assumes that ...**"

Examples:

> Claim: "We should invest in mobile-first design because 70% of our users are on mobile."

Reverse-Toulmin extraction:

- **Logical**: Assumes that "user platform" is a meaningful basis for design priority (vs. e.g., user value, conversion rate, support cost).
- **Empirical**: Assumes that the 70% figure is current, accurate, and representative of *paying* users (not just any user). Assumes that mobile vs desktop is the relevant axis (not iOS vs Android, or country, or new vs returning).
- **Methodological**: Assumes that the measurement counted **active** users (not just registered). Assumes the time window was long enough to be stable (not, e.g., a 7-day artifact). Assumes mobile-vs-desktop attribution is reliable (no double-counting, no detection failures).

That's 7 assumptions extracted from one claim.

### Step 4: Stop when assumptions become trivial

You can keep extracting indefinitely (every assumption itself rests on
sub-assumptions). Stop when:

- The next assumption is **trivial** (e.g., "assumes the writer can read English")
- The next assumption is **outside the artifact's scope** (e.g., "assumes physics works")
- You have ≥3 assumptions per claim — that's enough for surface-level mapping

For deep analysis (e.g., a 1-page memo deserves 30 minutes of scrutiny), 3–5 per claim is the sweet spot. For broad sweeps (a tweet thread with 30 claims), 1–2 per claim is enough.

## Worked example: "Customer trust is the foundation of our business"

### Step 1: Claim verbatim

"Customer trust is the foundation of our business."

### Step 2 + 3: Extract assumptions

**Logical**:
- Assumes that "trust" is a coherent variable that can be a "foundation"
- Assumes that businesses have a single "foundation" (not multiple co-foundations)
- Assumes that trust → business outcomes via a directional causal mechanism (not just correlated)

**Empirical**:
- Assumes that the writer's customer base treats trust as decision-relevant (some segments may not — commodity buyers, price-driven buyers)
- Assumes that *current* trust is meaningfully different from baseline (otherwise the claim is empty)

**Methodological**:
- Assumes that trust is **measurable** in some operational way (NPS / repeat-purchase / qualitative interviews)
- Assumes that the measurement is **shared** across the org (otherwise "we" don't have a coherent definition)

7 assumptions from one mission-statement-style claim. Most are
**foundational** — if any of them fail, the claim becomes hollow.

## Common assumption patterns to catch

When extracting, run through this checklist for each claim:

| Pattern | Look for |
|---|---|
| **Definitional** | Is a key term being used in a contestable way? ("growth" / "trust" / "users") |
| **Causal** | Is correlation being treated as causation? |
| **Aggregation** | Is a population-level statistic being projected onto individuals? |
| **Temporal** | Is past trend assumed to continue? Is short-term measurement assumed stable? |
| **Boundary** | Is "our market" / "our customers" / "the industry" assumed to have a clean edge? |
| **Counterfactual** | What would the world look like if the claim were *not* true — and is that world ruled out? |
| **Methodological** | Are measurement methods assumed reliable / unbiased? |
| **Stakeholder** | Are competing stakeholder views assumed reconciled? |

Each pattern, if matched, generates an assumption.

## Output format

```markdown
| Claim # | Claim verbatim | Assumptions extracted |
|---|---|---|
| 1 | "..." | • Logical: assumes that ... |
|   |   | • Empirical: assumes that ... |
|   |   | • Methodological: assumes that ... |
| 2 | "..." | • ... |
```

This table feeds Step 4 of the SKILL.md workflow (classify +
falsifiability test).

## Pitfalls

- **Restating the claim as an assumption** — "assumes that we should invest in mobile" is just the claim. The assumption is what *must precede* the claim.
- **Listing the writer's evidence as an assumption** — if "70% mobile" is stated as evidence, it's grounds, not assumption. The *assumption* is what makes 70% mobile *imply* mobile-first design priority.
- **Going infinitely meta** — every assumption rests on sub-assumptions. Stop at 3–5 per claim for surface-level mapping.
- **Conflating reverse-Toulmin with full Toulmin** — reverse-Toulmin extracts assumptions broadly; full Toulmin (in argument-deconstruct) maps them into claim-grounds-warrant-backing-rebuttal-qualifier structure. Use reverse-Toulmin for breadth, full Toulmin for depth.
