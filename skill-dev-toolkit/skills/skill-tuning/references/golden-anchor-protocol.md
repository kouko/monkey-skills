# Golden Anchor Protocol

> **Shared convention — bundled functional copy.** This file is
> bundled in both `dev-workflow:skill-refactor/references/` and
> `dev-workflow:skill-tuning/references/`. Same-PR drift rule:
> any edit to this protocol must update both copies in the same
> PR. The two copies are intentionally synchronized functional
> copies, not delegated paths — runtime self-containment is
> preserved on each side. This copy lives in `skill-tuning`;
> the canonical SoT location for this convention's evolution is
> `skill-refactor/references/golden-anchor-protocol.md` (which
> shipped first in v1.6.0); when proposing changes, edit that
> path first then mirror here in the same PR.

How to maintain a `golden/` directory of curated reference outputs
for a skill, used as a stable evaluation anchor for refactor and
tuning work.

## What goldens are

Golden anchors are **human-curated examples of "what good output
looks like"** for a given skill. Each is a `(prompt, output)` pair
that the curator has reviewed and judged "this is the kind of
output we want this skill to produce".

Goldens differ from `test-prompts.json`:

| | `test-prompts.json` | `golden/` |
|---|---|---|
| Purpose | Run-on-current-skill input | Reference output to compare against |
| Authored by | Often LLM-drafted, user-confirmed | Always human-curated |
| What it tests | "Skill produces *some* output" | "Skill produces *this kind* of output" |
| Used by | Equivalence check (Q1) | Anchor comparison (Tier 2 escalation, taste check) |

## When goldens matter

Goldens are **optional but high-value** for skills where:

- Output has **taste-sensitive dimensions** (writing style, tone,
  voice, design feel)
- Output structure is conventional but the *quality* of fill-in is
  what matters (e.g., a status report has fixed sections, but the
  content quality varies)
- Equivalence check alone is insufficient — two outputs can be
  "equivalent" in content but one is clearly better

For purely mechanical skills (file transforms, fixed-format
generators), goldens are overkill — equivalence check suffices.

## Directory layout

```
<skill>/golden/
├── README.md                    ← curation policy, when last reviewed, who authored
├── golden-1.md                  ← (prompt, output) pair
├── golden-2.md
└── ...
```

Each golden file:

```markdown
---
id: golden-1
authored_by: <human>
authored_date: YYYY-MM-DD
last_reviewed: YYYY-MM-DD
prompt_pattern: "user request type that should trigger this anchor"
quality_dimensions:
  - tone: friendly-professional
  - length: concise (< 200 words)
  - structure: 3-section
---

# Prompt

<the user prompt>

# Anchor Output

<the golden output — what the skill should produce>

# Why This Is Good

<1-2 paragraphs from the curator explaining what makes this
output good; specifically the dimensions called out in
quality_dimensions>
```

## Curation policy

### How many goldens per skill

- **Minimum**: 3 for skills where goldens apply
- **Typical**: 5-10 covering core use cases
- **Maximum useful**: ~15; beyond that, marginal value drops

### Who curates

Goldens are **human work**, not AI-generated. The curator should:

- Be familiar with the skill's intended use
- Have judgment about what "good output" means in this context
- Be the same person across goldens for one skill (consistency)
- Document quality dimensions in frontmatter so other readers
  understand the criteria

### Curation process

1. Pick a representative prompt for the skill
2. Run the skill on it (current best version)
3. Either:
   - Accept the output as-is if it's truly good
   - Edit the output to be the version that demonstrates "good"
   - Write the desired output from scratch
4. Document in "Why This Is Good" what makes it good
5. Save to `golden/golden-N.md`
6. Re-review every 6 months or when the skill significantly evolves

### Review trigger

Goldens become stale. The curator should re-review:

- Every 6 months as a default rhythm
- When the skill has had a major rewrite (post-skill-creator-advance)
- When user feedback on the skill changes
- When a refactor or tuning round reveals goldens no longer
  reflect current judgment

Stale goldens are worse than no goldens — they create false
anchoring.

## How `skill-refactor` uses goldens

In Q1's Tier 2 escalation:

```
If 2-of-3 ensemble agree on equivalence (moderate confidence) and
golden anchors exist for this skill:

  For each test prompt:
    candidate_output = run skill_v_candidate on prompt
    
    For each golden in golden/ matching this prompt_pattern:
      similarity = compare(candidate_output, golden.anchor_output)
      
    If candidate's similarity to relevant golden < baseline's:
      FAIL — refactor moved away from anchored quality
    Else:
      PASS — refactor preserved or improved anchored quality
```

Golden-anchored equivalence is stronger than judge-only equivalence
because the comparison target is human-fixed, not LLM-floating.

## How `skill-tuning` uses goldens

In `skill-tuning` (per its protocol), goldens serve as the
ground-truth direction for variant exploration:

```
For each generated variant:
  similarity_to_golden = compare(variant_output, nearest_golden)
  
Variants that move away from golden = bad
Variants that move toward golden = good
Human selection still happens, but golden gives a baseline
"closer / further" signal.
```

## Drift management

The `golden/` directory is human-managed. Drift rules:

- Don't auto-edit goldens (this defeats the human-anchored purpose)
- Don't generate new goldens from skill outputs without human review
- When skill behavior must change (post-rewrite via
  skill-creator-advance), update goldens explicitly in the same PR
  as the skill change — don't leave dangling pre-rewrite goldens

## Anti-patterns

| Anti-pattern | Why it breaks goldens |
|---|---|
| AI-generated goldens | Defeats the purpose; goldens *are* the human anchor |
| Goldens that look identical to current skill output | Adds no information; just baseline-locks |
| Goldens that are unrealistic / aspirational | Pushes skill in directions it can't reach |
| One golden per skill | Insufficient variance; can't represent quality range |
| Stale goldens (>1 year old, never re-reviewed) | False anchor; better to have no golden than wrong golden |
| Goldens that don't explain "Why This Is Good" | Can't be applied; reader doesn't know what dimensions matter |

## Skip if not applicable

Many skills don't need goldens. Indicators:

- Output is purely deterministic (file transforms, JSON
  generation)
- "Good output" is binary (correct / incorrect, not better / worse)
- Skill is a one-step utility (no taste dimension)

For such skills, `skill-refactor` Q1's equivalence check + Q2's
token reduction + Q3's invariant check is sufficient. Goldens are
overkill.

This protocol applies only when goldens are warranted. Document
the decision in the skill's NOTICE: "Goldens not applicable
because <reason>".
