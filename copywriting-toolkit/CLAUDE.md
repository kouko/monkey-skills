# copywriting-toolkit — Plugin Conventions

## Copy-First Principle

All standards / protocols / checklists / rubrics / grounding notes are byte-identical copies from `domain-teams/skills/copywriting-team/`. Never paraphrase, condense, or "optimize" the original text.

- `cp` — do not rewrite
- SKILL.md references copied files (`See standards/X.md`) rather than inline-rewriting their content
- Per-commit diff check: `diff -q <file> <source>` must return nothing

### INLINE-duplicate clarification

"INLINE" means `cp` the same standard into multiple skills' `standards/` directories — NOT prose paste into SKILL.md.

- `persuasion-psychology-anchor.md` → duplicated across 5 Phase-4 workflow skills (identical copies)
- `sns-evolution-aisas-ulssas.md` → duplicated across long-form-pasona + light-action
- `kosimo-instinct-analysis.md` → single copy in ideation

All remain discrete files — referenced, never pasted.

## SKILL.md Budget

Each SKILL.md body ≤6K tokens (skill-team v4.8.1 budget). If grounding exceeds this, reference `standards/` files instead of inlining.

## Handoff Envelope

Between-skill artifact shape (JSON):

```json
{
  "phase": "phase-4-draft",
  "form": "long-form-pasona",
  "brief": { "...": "from intake" },
  "message_thesis": "...",
  "ideation_pool": ["... optional if Phase 2 ran ..."],
  "neta_candidates": ["... optional if Phase 3 ran pre-draft ..."],
  "draft": "...",
  "next_stage": "copywriting-voice-positioning-stage"
}
```

Each stage reads envelope, adds its layer, updates `next_stage`, returns.

## Cross-Plugin Delegation (Loose)

Phase 1 Message Confirmation inside `copywriting-intake` may RECOMMEND `planning-team` when the problem is thesis-level (unclear positioning / audience / goal). Do NOT enforce — user may proceed anyway. No auto-delegation.

## Evaluator

Own `agents/evaluator.md` — NOT shared with `domain-teams:evaluator`. Infrastructure stays independent.

Used by:
- `copywriting-ethics-check-stage` (Phase 7)
- `copywriting-form-check-stage` (Phase 8)
- `copywriting-audit-stage` (audits external copy)

## A/B Coexistence

`domain-teams:copywriting-team` remains untouched. Both plugins run in parallel. Do NOT modify the original in this plugin's commits. Consolidation deferred to post-A/B retrospective.

## Inline-Duplication Drift Risk

`persuasion-psychology-anchor.md` appears 5× identical in workflow skills. If drift observed later, a sync script is acceptable — do not attempt cross-skill loading at runtime.

## Skill Structure

```
copywriting-toolkit/
  .claude-plugin/plugin.json
  README.md
  CLAUDE.md
  agents/evaluator.md
  skills/
    <skill>/
      SKILL.md                  # ≤6K tokens, references the rest
      standards/*.md            # cp from domain-teams, byte-identical
      protocols/*.md            # same
      checklists/*.md           # only gate skills
      rubrics/*.md              # only gate skills
      research/*.md             # grounding notes, cp
```

## Branch / Commit Convention

- Branch: `feat/copywriting-toolkit-v1.0.0`
- Commit prefixes: `feat(copywriting-toolkit)` or `chore(copywriting-toolkit)` — CC CI whitelist only
- No `test:` / `ci:` commits — fixtures bundle into relevant `feat` commit
