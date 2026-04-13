# Skill Coherence Gate

Grounds on: `standards/skill-md-structure.md`, `standards/file-conventions.md`.

## Scope Boundary

Review the **overall coherence** of a completed skill — structural
proportionality, workflow completeness, and routing fit. Do NOT
review grounding depth (that's the primary-source-grounding rubric's
job) or individual file correctness (that's the completeness
checklist's job).

Run this rubric against the entire skill directory after all
structural work is done.

## Flag Definitions

### Token Budget

- :red_circle: **Fatal**: SKILL.md exceeds ~6,000 tokens (~4,500 words). Hard cap from `standards/skill-md-structure.md`.
- :yellow_circle: **Warning**: SKILL.md is ~4,500–6,000 tokens — approaching the budget. Usually means workflow tables have grown too verbose or the Resource Manifest is duplicating content better kept in the standards files themselves.
- :green_circle: **Clear**: SKILL.md is under ~4,500 tokens, ideally in the ~3,000–4,500 sweet spot.

### Workflow Completeness

- :red_circle: **Fatal**: Any workflow has a phase marked with `--`, empty Protocol cell, or "TODO" placeholder. This is the "broken Monitoring workflow" pattern — the skill ships with a non-functional workflow path.
- :yellow_circle: **Warning**: Workflow phases exist but several lack Notes column content, Input and Output are vague, or the workflow table structure is inconsistent across workflows.
- :green_circle: **Clear**: Every workflow is fully specified — each phase has Agent, Protocol (or explicit "main" / "none"), Input, Output, and Notes as appropriate. Gates tables below workflows list the gates that trigger for that workflow.

### Router Fit

- :red_circle: **Fatal**: The skill doesn't appear in `using-domain-teams/SKILL.md` at all, OR its routing row has been removed without replacement. The user has no way to discover this team.
- :yellow_circle: **Warning**: Router entry exists but the "You want to..." phrases are vague or overlap heavily with another team without disambiguation in Ambiguous Cases.
- :green_circle: **Clear**: Router entry is present, specific, and non-overlapping. A user reading the router can confidently select this team for the stated intents.

### Duplicate-Skill Check

- :red_circle: **Fatal**: The skill overlaps > 50% with an existing team (e.g. new skill's workflows are duplicated in another team). This should have been caught in brainstorming — refactor or merge before shipping.
- :yellow_circle: **Warning**: Some overlap with an existing team (20-50%), but the boundary isn't clearly stated in "When NOT to Use" or Cross-Domain Awareness. Users will be confused about which team to pick.
- :green_circle: **Clear**: < 20% overlap with any existing team, OR overlap is deliberate and explicitly resolved by clear routing rules in "When NOT to Use" + Ambiguous Cases.

## Verdict Rules

1. **NEEDS_REVISION**: Any 1 :red_circle: fatal flag
2. **NEEDS_REVISION**: 2 or more :yellow_circle: warning flags
3. **PASS_WITH_NOTES**: Exactly 1 :yellow_circle: warning flag, no :red_circle:
4. **PASS**: All :green_circle: clear

## Rules

- Coherence failures are about shape, not content. A skill can have
  excellent standards but still fail this rubric if its SKILL.md is
  700 lines or its router entry is missing.
- When issuing NEEDS_REVISION for line budget overflow, MUST identify
  which sections are over-sized and suggest specific trim targets
  (e.g. "collapse the 4 workflow phase tables into a single shared
  template").
- Workflow Completeness fails open when the skill intentionally has
  no workflows (e.g. a pure reference skill). In that case, mark
  workflow section NOT_APPLICABLE → :green_circle:.
- Router Fit is NOT_APPLICABLE when reviewing the
  `using-domain-teams` router skill itself.

## Output Format

1. **Per-dimension flags**: Line Budget / Workflow Completeness / Router Fit / Duplicate-Skill Check
2. **Evidence**: Specific line counts, workflow names, router row quotes
3. **Trim suggestions** (line budget warning/fatal only): specific sections to compress
4. **Verdict**: PASS / PASS_WITH_NOTES / NEEDS_REVISION

PASS_WITH_NOTES issues auto-revise without human review. Be specific
about WHERE to trim or HOW to disambiguate routing.
