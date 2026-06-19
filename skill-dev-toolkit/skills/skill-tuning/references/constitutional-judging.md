# Constitutional Judging

How `skill-tuning` Phase 2 (constitutional pre-filter) uses the
target skill's `constitution.md` to filter variants before user
judgment.

The full constitution schema lives in
`references/constitution-schema.md` (shared convention with
`skill-refactor`). This file documents the *judging mechanics*
specific to skill-tuning.

## Why pre-filter

Without constitutional pre-filter, two failure modes occur:

1. **User burden**: human spends judgment time on variants that
   should never have been candidates (variants that violate the
   skill's contract). Wasted attention.
2. **Taste vs contract confusion**: user might *prefer* a variant
   that violates a MUST. Without constitutional gate, the
   preference log records "user preferred contract-violating
   variant" — corrupting the dataset for future judge training.

The pre-filter ensures every variant the user sees is **already
contract-compliant**. The user's pick is then a pure taste signal,
not contaminated by contract questions.

## How to test a MUST clause against a variant

Each MUST clause should be testable from a single (prompt,
variant_output) pair. The judging mechanic:

```
For each MUST clause C:
    For each test prompt P:
        Run variant on P → output O
        Check: does O satisfy C?
        - Yes: this prompt's check passes
        - No: variant violates C; record in rejected_by_constitution
        - Ambiguous: variant gets benefit of doubt; flag for human review
            in tuning session
```

If ANY prompt produces a violation, the variant is rejected.
Single-violation tolerance is too loose — the MUST must hold across
all documented use cases, not just the easy ones.

### "Satisfied" is binary

A MUST is satisfied or violated; there's no "partial credit".
Examples:

| MUST clause | Output A | Output B |
|---|---|---|
| "MUST cite primary source for every factual claim" | "Per Hunt & Thomas 2019..." (cited) → ✓ | "Industry consensus is..." (uncited) → ✗ |
| "MUST handle empty input by asking, not silent return" | (Empty input → "What context?") → ✓ | (Empty input → no response) → ✗ |
| "MUST produce markdown" | (Output is markdown) → ✓ | (Output is JSON) → ✗ |

## How to test a MUST NOT clause

Mirror image of MUST. The variant fails if the prohibited behavior
is observed:

| MUST NOT clause | Output A | Output B |
|---|---|---|
| "MUST NOT execute commands without user confirmation" | Says "Want me to run X?" before running | Just runs commands → ✗ |
| "MUST NOT fabricate metrics" | Uses input metrics verbatim | Says "approximately 200 (estimated)" → ✗ |
| "MUST NOT exceed 500 words without permission" | Output is 320 words | Output is 800 words → ✗ |

## Ambiguity handling

Some MUST clauses can be interpreted multiple ways. Examples:

- "MUST be helpful" — what's helpful?
- "MUST handle edge cases" — which?
- "MUST follow best practices" — whose?

These are **vague MUSTs** and should not be in constitution.md.
But if they are, the judging cannot proceed reliably:

1. **Ambiguous result** triggers a flag in the variant's pre-filter
   record: `"constitutional_check": "ambiguous", "clauses_unclear":
   ["MUST be helpful"]`
2. The variant **proceeds to human A/B** (don't auto-reject on
   ambiguity); the user sees the flag and decides whether the
   variant honors the spirit of the clause
3. After the session, recommend to user: "Constitutional clause
   X is ambiguous and forced subjective judgment in the pre-filter.
   Consider rewriting as testable rule."

This route prevents constitutional ambiguity from silently
filtering candidate variants while still surfacing the issue.

## Reporting filtered variants

When a variant is rejected by constitution, the user MUST be
informed (not silently dropped). This serves two purposes:

1. **Transparency** — the user knows which variants were
   considered; sees what generation diversity is possible
2. **Constitution validation** — if the rejection feels wrong
   ("that variant looked good!"), it's a signal that the
   constitution may be over-strict

Format the report:

```
Phase 2 constitutional pre-filter:
- Variant A: PASS — honors all 5 MUST clauses
- Variant B: PASS — honors all 5 MUST clauses
- Variant C: REJECTED — violates MUST #3 ("All quantities MUST be
  exact integers from input"; variant says "approximately 200")

2 of 3 variants proceed to A/B comparison.
```

The user can then choose to proceed with 2 variants, regenerate
to get a 3rd compliant variant, or relax the constitution if the
rejection seems over-strict.

## When constitution is missing

If the target skill has no `constitution.md`:

1. **Recommend writing one** — strongly recommended for taste-
   sensitive skills; without floor, taste exploration can drift
   into contract violations the user doesn't notice
2. **If user declines**, proceed with manual constitutional check —
   show variants alongside an "implicit constraints" prompt:
   "Before picking, please verify each variant: does it produce
   correct content? Does it preserve required information? Does
   it respect any constraints you have in mind?"
3. **Log the absence** — preference log entries get a flag
   `"constitution_present": false` so future analysis can
   distinguish constitutionally-grounded picks from pure-taste
   picks

Skills without constitutions can still be tasted — just with
more user burden per round.

## Constitution evolution from tuning

Tuning sessions sometimes reveal **implicit constraints** the
user has but never wrote down. Example:

- User's pick rationale: "I picked A because B doesn't mention
  the required signoff at the end"
- Implication: user has an unstated MUST "include signoff"
- This should be **promoted to explicit MUST** in constitution.md

The tuning session should surface these moments:

```
After each round, ask:
"Was your pick driven by a constraint that should be documented?
Anything the rejected variants did wrong that wasn't in the
constitution?"
```

Recording these as candidate constitution updates lets the
constitution evolve from real preference data, not theoretical
listing.

## Constitutional ratchet

When constitution is updated mid-session (a new MUST is added
because tuning revealed it):

1. Re-run pre-filter on remaining rounds against new constitution
2. Variants that violated new MUST are retroactively flagged
3. Don't invalidate already-completed picks (user picked based on
   what they saw); just note in log that the new constitution may
   have changed the pre-filter result

The preference log entry captures `"constitution_version": "v2"`
or similar so future training data can be filtered by constitution
version.

## Anti-patterns

| Anti-pattern | Why bad |
|---|---|
| Skipping constitutional check "just this round" | Once skipped, contract violations enter taste signal; pollutes log |
| Treating SHOULD as MUST | Filters legitimate variants; over-strict; reduces variant diversity |
| Treating MUST as SHOULD | Lets contract violators through; contaminates taste data |
| Constitutional check by single LLM call without test prompts | Constitution is checked against *behavior on prompts*, not against the variant's text in isolation |
| Auto-promoting all "rejection signals" to MUSTs | Constitution should grow slowly and deliberately; not every round generates a new MUST |

## Cross-references

- `references/constitution-schema.md` — full schema, anti-patterns,
  curation policy
- `references/preference-log-schema.md` — how constitutional results
  are logged per round
- `skill-dev-toolkit:skill-refactor` references the same constitution
  but uses it differently — refactor checks Q3 invariants don't
  break MUSTs; tuning filters variants before they reach the user
