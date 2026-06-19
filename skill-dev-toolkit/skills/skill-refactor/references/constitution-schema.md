# Constitution Schema

> **Shared convention — canonical SoT.** This file is bundled in
> both `dev-workflow:skill-refactor/references/` and
> `dev-workflow:skill-tuning/references/` as functional copies.
> This location is the canonical SoT for evolution; same-PR drift
> rule mirrors edits to the `skill-tuning` copy.

Schema for `constitution.md` — a per-skill MUST / MUST NOT
specification used as invariant input by `skill-refactor` Q3 and as
judging criteria by `skill-tuning`.

## Purpose

A skill's constitution is the **explicit, non-negotiable
specification of what the skill must / must not do**. It captures
the load-bearing behavioral guarantees that any refactor or
variant must preserve.

Compare to:

- `description` (in frontmatter): triggers and 1-paragraph summary
- `SKILL.md body`: the prose instruction set
- `test-prompts.json`: input set for evaluation
- `golden/`: human-curated reference outputs

The constitution sits **above** all of these — it's the contract
the skill commits to, the prose / structure / examples are
*implementations of the contract*.

## File location

```
<skill-dir>/constitution.md
```

Same level as `SKILL.md`. Optional file — many skills don't need a
formal constitution. When present, it's authoritative for behavior
guarantees.

## Schema

```markdown
# Constitution: <skill-name>

**Schema version**: 1
**Authored**: YYYY-MM-DD
**Last reviewed**: YYYY-MM-DD
**Authored by**: <human>

## MUST

The skill MUST:

1. <observable behavior 1>
2. <observable behavior 2>
3. ...

## MUST NOT

The skill MUST NOT:

1. <prohibited behavior 1>
2. <prohibited behavior 2>
3. ...

## SHOULD (advisory)

The skill SHOULD (but failures are not constitution violations):

1. <preferred behavior 1>
2. ...

## Operational definitions

<glossary of terms used in MUST / MUST NOT to disambiguate>
```

## Writing MUST clauses

Each MUST is a **single observable behavior**, expressed as a
testable statement.

Good MUST examples:
- "MUST ask the user to confirm before deleting any file"
- "MUST cite a primary source for any factual claim"
- "MUST produce output in markdown format"
- "MUST handle empty input by asking for clarification, not by
  returning silently"

Bad MUST examples:
- "MUST be high quality" (untestable, taste)
- "MUST be helpful" (untestable)
- "MUST handle all edge cases" (over-broad)
- "MUST follow best practices" (defers definition)

Each MUST should be checkable from a single test prompt + output
pair. If you can't write a single yes/no test for a MUST clause,
it's too vague.

## Writing MUST NOT clauses

Mirror to MUST. Each MUST NOT is an explicit prohibition with a
checkable signal.

Good MUST NOT:
- "MUST NOT execute commands without showing them to the user first"
- "MUST NOT produce more than 500 words of output without
  user confirmation"
- "MUST NOT call external APIs without explicit user opt-in"

Bad MUST NOT:
- "MUST NOT be wrong" (untestable)
- "MUST NOT bother the user" (subjective)

## SHOULD clauses

SHOULD is for preferences that aren't constitution-grade —
violation is acceptable but should be defended. Goes here, not in
MUST, when:

- The behavior is preferred but skill remains useful without it
- Compliance can vary by user / context
- Failure is recoverable / non-load-bearing

Example:
- "SHOULD respond in the user's language when detectable"
- "SHOULD include a one-line rationale with each verdict"

## Operational definitions

When MUST / MUST NOT clauses use domain-specific terms, define
them in this section to avoid ambiguity.

Example (for a citation-checking skill):
- **Primary source**: original publication (book, paper, official
  document); not a blog summary or aggregator
- **Citation**: author + year + work title + (where applicable)
  page / chapter / URL

Without operational definitions, MUST clauses are interpretation-
dependent and can't ground objective evaluation.

## How `skill-refactor` uses constitution

In Q3 (invariant preservation):

```
For each MUST clause in constitution.md:
  Run candidate skill on a representative test prompt
  Check whether the MUST behavior holds
  
For each MUST NOT clause:
  Check whether the prohibition is honored

If any MUST violated or any MUST NOT triggered → REJECT round
```

A refactor that breaks a MUST is **not a refactor** — it's a
behavior change. Constitutional check is what catches "smuggled
feature work".

## How `skill-tuning` uses constitution

In its variant evaluation:

```
For each variant output:
  Score: how well does this output honor the constitution?
  
Constitutional honoring is the floor; taste is the ceiling.
A variant that violates a MUST is rejected even if user
"prefers" the output — taste does not override constitution.
```

## When constitution is unnecessary

Many skills don't need a formal constitution. Indicators:

- Skill is a deterministic utility (no real interpretive freedom)
- Skill's behavior is fully captured by SKILL.md prose with no
  load-bearing nuance
- No taste-sensitive dimensions (constitution is most valuable
  exactly where taste enters)
- Skill is < 1 year old and behavior is stable — write
  constitution later if needed

For such skills, skip the constitution.md file. SKILL.md alone is
the spec.

## When constitution is essential

Constitution is essential when:

- Skill produces output where "right" varies with use case
- Skill has ≥1 documented behavior that contributors might
  unintentionally weaken (e.g., "always cite source" is a
  constitution-grade rule because it's easy to soften by accident)
- Skill is iterated frequently — constitution prevents drift
- Multiple contributors edit the skill — constitution is the
  shared contract

## Curation policy

### Authoring

Constitution is **always human-authored**. Like goldens, an
LLM-generated constitution defeats the purpose — the value is
specifically that a human committed to these guarantees.

### Review

Re-review every 6 months or when:

- A refactor / tuning round reveals a MUST that's actually
  weaker than written
- User feedback identifies a behavior the skill should commit
  to that's not yet in MUST
- A MUST has been weakened in practice — either restore it or
  formally relax it (and document why)

### Versioning

Constitution changes are major events. Update `Last reviewed`,
note the change reason in commit message, and ideally bump the
target skill's version (minor or major depending on whether the
MUST changed in a backward-compatible way).

## Anti-patterns

| Anti-pattern | Why bad |
|---|---|
| Vague MUST ("be helpful") | Untestable; can't ground evaluation |
| Constitution = SKILL.md restated | Adds no information; should be the *contract above* the prose |
| Constitution longer than SKILL.md | Probably over-specified; trim to essentials |
| LLM-generated constitution | Defeats the human-anchor purpose |
| MUST that's actually a SHOULD | False rigidity; either lift compliance or move to SHOULD |
| Constitution never re-reviewed | Drifts; becomes ceremonial |

## Lifecycle

| Event | Action |
|---|---|
| Skill created | Author writes initial constitution if behavior is taste-sensitive or load-bearing |
| Skill refactored | No constitution change (refactor preserves behavior) |
| Skill tasted | If A/B reveals an implicit constraint, formalize as MUST |
| Skill rewritten | Re-author constitution if behavior changed |
| 6 months pass | Recommend re-review |
