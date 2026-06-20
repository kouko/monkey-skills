# Test Prompts Schema

> **Shared convention — bundled functional copy.** This file is
> bundled in both `skill-dev-toolkit:skill-refactor/references/` and
> `skill-dev-toolkit:skill-tuning/references/`. Same-PR drift rule:
> edits land in `skill-refactor/references/test-prompts-schema.md`
> first (canonical SoT location, shipped v1.6.0), then mirror here
> in the same PR. Runtime self-containment preserved on each side.

Schema for the `test-prompts.json` file maintained per skill.

## Purpose

`test-prompts.json` is the **input set** that drives evaluation
work for a skill — equivalence checks (skill-refactor), A/B
variant testing (skill-tuning), and creation eval (when
skill-creator-advance produces a new skill).

Without test prompts, evaluation tools can't run. The first action
of any evaluation skill, if test-prompts.json is missing, is to
collaborate with the user to create one.

## File location

```
<skill-dir>/test-prompts.json
```

Same level as `SKILL.md`. Not bundled inside the skill itself —
it's data, not skill content.

## Schema

```json
{
  "skill_name": "<skill-name>",
  "schema_version": 1,
  "created": "YYYY-MM-DD",
  "last_reviewed": "YYYY-MM-DD",
  "prompts": [
    {
      "id": 1,
      "category": "happy-path",
      "prompt": "What the user would actually type",
      "expected_behavior": "Short description of what the skill should do",
      "edge_case_dimensions": []
    },
    {
      "id": 2,
      "category": "edge-case",
      "prompt": "...",
      "expected_behavior": "...",
      "edge_case_dimensions": ["ambiguous input", "missing context"]
    },
    {
      "id": 3,
      "category": "stress",
      "prompt": "...",
      "expected_behavior": "...",
      "edge_case_dimensions": ["incomplete request", "tests intake / clarification flow"]
    }
  ]
}
```

## Field semantics

### `skill_name`
Matches the `name` in the target skill's frontmatter. Used as
sanity check.

### `schema_version`
Currently `1`. Incremented if the schema itself evolves.

### `created` / `last_reviewed`
ISO date. `last_reviewed` should be updated whenever the user
reviews and confirms the prompts still represent typical use.
Recommendation: re-review every 6 months or after a major skill
change.

### `prompts[].id`
Stable integer identifier; used to correlate runs across
iterations.

### `prompts[].category`

One of:

| Category | Purpose |
|---|---|
| `happy-path` | Most common use case; baseline functionality |
| `edge-case` | Tricky input that exercises specific instructions / fallbacks |
| `stress` | Deliberately incomplete / ambiguous; tests intake or clarification |

A skill with ≥3 prompts should have at least one of each category
when possible.

### `prompts[].prompt`
The literal string a user would say. Should be:

- Realistic (something someone would actually type)
- Specific enough that the skill has clear work to do
- Not overly long — prompt length isn't being tested

Bad: "Format this data" (too generic)
Good: "I have a CSV in ~/Downloads with columns Date, Customer,
Amount. Can you sort by date desc and remove rows where Amount is
missing?"

### `prompts[].expected_behavior`
1-2 sentence description of what the skill should produce. Not the
expected output verbatim — that would over-specify and prevent
legitimate variation.

Example: "Skill should ask the user for the column to sort, then
produce a sorted CSV with missing-Amount rows filtered out, and
report the row count diff."

### `prompts[].edge_case_dimensions`
For non-happy-path prompts, the specific dimensions being stressed.
Helps the eval tool understand what to verify.

Examples:
- `"ambiguous input"` — user request can be interpreted multiple ways
- `"missing context"` — required information not provided
- `"out-of-domain"` — input is on the boundary of the skill's scope
- `"contradictory request"` — user's stated goal conflicts with their data
- `"large input"` — tests handling of input scale

## Minimum viable

A `test-prompts.json` with **3 prompts** (1 happy + 1 edge + 1
stress) is sufficient for most skills. More is better but
diminishing returns; 5-7 is typical for mature skills.

A skill with **fewer than 3 test prompts cannot be evaluated by
skill-refactor or skill-tuning** — the evaluation gates self-abort
and prompt the user to provide more.

## Curation responsibility

Test prompts are user-confirmed (or at least user-acknowledged):

1. The skill's author (or refactor / tuning orchestrator) drafts
   prompts based on the skill's documented use cases
2. User reviews — does this look like what real users would type?
3. User confirms or edits
4. Saved as canonical for that skill

LLM-drafted prompts that the user never reviewed are unreliable —
they tend to over-fit to what the LLM thinks the skill should
handle, rather than what users actually do.

## Lifecycle

| Event | Action |
|---|---|
| Skill created | Author drafts initial test-prompts.json (≥3) |
| Skill refactored | No prompt changes (refactor preserves behavior) |
| Skill tasted (output A/B) | Prompts may be augmented if A/B reveals new use case |
| Skill rewritten | Re-review prompts; update `last_reviewed`; possibly augment |
| 6 months pass | Recommend re-review |

## Anti-patterns

| Anti-pattern | Why bad |
|---|---|
| All prompts are happy-path | Misses edge / stress cases; refactor that breaks edges passes the gate |
| Prompts are abstract / one-word | Doesn't trigger skill (Claude shortcuts simple prompts) |
| Prompts are LLM-generated and never reviewed | Reflects LLM's projection, not real user behavior |
| Prompts have *expected outputs* verbatim | Over-specifies; prevents legitimate output variation |
| Prompts duplicate each other (same category, same shape) | Wastes eval budget without adding signal |
| Stale prompts (>1 year, never reviewed) | Test the past version of the skill |

## Cross-skill use

The same `test-prompts.json` is used by:

- `skill-refactor` Q1 baseline + comparison runs
- `skill-tuning` for A/B variant runs
- `skill-creator-advance` Full Eval Path
- `skill-judge` (advisory; doesn't require but can use for context)

Single source per skill = consistent eval signal across tools.
