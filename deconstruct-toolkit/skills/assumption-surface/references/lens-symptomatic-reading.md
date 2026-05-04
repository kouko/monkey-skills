# Lens: Symptomatic Reading (Althusser)

> **Source**: Louis Althusser, *Reading Capital* (with Étienne Balibar, 1968; English trans. Ben Brewster, NLB, 1970). The concept of "symptomatic reading" (*lecture symptomale*) is developed in Part 1, Ch 1, "From Capital to Marx's Philosophy," pp 13–34. Althusser argues that a text's "*omissions*, *gaps*, and *silences*" are themselves productive — they reveal the structure of the writer's frame.

For artifact deconstruction, we use a **simplified, operationalized**
version: scan the artifact for what is structurally absent, and treat
the absence as data.

## Core idea

A text never says everything. What it *doesn't* say is shaped by:

1. The writer's **frame** — what's so obvious it doesn't need saying
2. The writer's **discomfort** — what would weaken the argument if
   acknowledged
3. The writer's **audience** — what they assume the reader already
   knows
4. The writer's **field's blind spots** — what the field doesn't
   typically examine

Surfacing structural absence is **data extraction**, not gotcha-hunting.
The goal is to map the writer's **operative frame**, not catch them
out.

## Three diagnostic questions

For each artifact, run these three passes:

### Pass 1: What obvious counter-question is not posed?

The strongest sign of a buried assumption is when a **plainly relevant
counter-question** is never asked.

Examples:

| Artifact says | Plainly relevant counter-question (not posed) |
|---|---|
| "Our market is growing 20% YoY" | At what cost? What's our share of that growth vs competitors? |
| "We're profitable on a contribution basis" | What about fully-loaded? At what scale? |
| "We pivoted from B2C to B2B" | What did we lose by leaving B2C? Could we go back if needed? |
| "We're building the most diverse team" | Diverse along which axes? What does "most" mean — relative to whom? |
| "AI will change everything" | Which "everything"? On what timeline? With what limits? |

Each unposed counter-question is an assumption: **"the writer assumes
this question doesn't need to be asked here."**

### Pass 2: What category of evidence is missing?

Strong arguments back claims with appropriate evidence. Symptomatic
reading asks: when the writer cites evidence, **what kinds of evidence
are conspicuously absent**?

Categories to scan for:

- **Quantitative**: are claims about scale or magnitude unsourced?
- **Qualitative**: are claims about user / customer / stakeholder behavior unsupported by interview / case data?
- **Temporal**: are point-in-time claims missing trend context?
- **Comparative**: are claims about "best / first / leading" missing the comparison set?
- **Counterfactual**: are claims about success missing what failure would have looked like?
- **Negative cases**: are claims about a phenomenon missing the cases where it didn't apply?

Each missing category is an assumption: **"the writer assumes this
evidence is unnecessary."**

### Pass 3: What would the writer be uncomfortable to acknowledge?

This is the hardest pass. Read the artifact looking for **what would
be embarrassing to write**:

- That a competitor is winning some dimension
- That the founding thesis is partly wrong
- That a stakeholder is being managed-out of the conversation
- That the recommendation is risky for the writer's own status
- That the writer doesn't actually know the answer

The structural absence of these acknowledgments is data. They reveal
where the writer is **protecting** something.

This pass is the most prone to over-interpretation. Stay structural
(focus on **patterns of avoidance**), don't make personal accusations.

## Worked example: Strategy memo claiming "we should invest in mobile-first"

### Pass 1: Unposed counter-questions

- What's our cost of *building* mobile-first vs. the cost of staying desktop-primary?
- Are 70% of our users *paying users* or just registered?
- Has mobile-vs-desktop split changed over time? Is the current ratio stable, growing, or peaking?
- Do mobile users have lower LTV (smaller screens often correlate with smaller transactions)?
- Are there compliance / audit / regulatory considerations our enterprise customers raise around mobile?

Each unposed question is an assumption.

### Pass 2: Missing evidence categories

- **Quantitative**: 70% figure cited but no source, no methodology, no time window
- **Comparative**: no industry benchmark — is 70% high, low, or normal?
- **Negative cases**: no acknowledgment of segments where mobile-first would underserve
- **Counterfactual**: no scenario for what happens if we do *not* invest in mobile-first

### Pass 3: Discomforts

- The memo doesn't acknowledge that competitor X is mobile-first and winning — possibly because it would weaken the writer's "we're leading" framing
- The memo doesn't acknowledge that the original platform decision was desktop-primary — possibly because it would force a "we were wrong" admission

## Common pattern types

When you've done Pass 1–3, organize the surfaced assumptions into
familiar pattern types:

| Pattern | Example assumption |
|---|---|
| **Definitional silence** | Assumes "users" is one category, not multiple |
| **Methodological silence** | Assumes how-we-measured is non-controversial |
| **Comparative silence** | Assumes our market is the relevant frame |
| **Temporal silence** | Assumes the current snapshot is steady-state |
| **Stakeholder silence** | Assumes competing stakeholder views don't need addressing |
| **Counterfactual silence** | Assumes the alternative path doesn't bear examining |
| **Self-protective silence** | Assumes acknowledging weakness would harm the case |
| **Field-blindness silence** | Assumes the field's standard frames are correct |

Each labeled pattern helps the user understand *why* the assumption is
hidden, not just *that* it's hidden.

## Output format

```markdown
### Pass 1: Unposed counter-questions
- ...
- ...

### Pass 2: Missing evidence categories
- ...

### Pass 3: Acknowledgment-discomforts
- ...

### Pattern types
- Definitional silence: ...
- Methodological silence: ...
- ...

### Synthesized assumptions
<feed into the assumption table in SKILL.md Step 4>
```

## Pitfalls

- **Mind-reading the writer**: stay structural. "The writer would not
  acknowledge X" should be inferable from text patterns, not from
  your speculation about their psychology.
- **Treating every silence as suspicious**: many silences are appropriate
  (a 1-page memo can't address every counter-question). Focus on
  silences that *structurally matter* — where addressing them would
  shift the recommendation.
- **Confusing symptomatic reading with paranoid reading**: Eve Sedgwick
  distinguished the two — paranoid reading hunts for hidden malice,
  symptomatic reading maps absent structure. We do the latter.
- **Pattern over-fitting**: not every artifact uses every pattern type.
  Note when a pattern type genuinely doesn't apply.

## Why this lens fits assumption-surface (and not artifact-deconstruct)

`artifact-deconstruct` covers negative space as one of 6 dimensions —
a single pass among many. `assumption-surface` makes negative-space
*the central work*, supplemented by reverse-Toulmin. The two skills
have different center of gravity:

- `artifact-deconstruct` → 6 lenses + 6 dimensions, full picture
- `assumption-surface` → fast, atomic, focused on the assumption layer

Use `assumption-surface` when you need 30 assumptions in 10 minutes.
Use `artifact-deconstruct` when you need a full report.
