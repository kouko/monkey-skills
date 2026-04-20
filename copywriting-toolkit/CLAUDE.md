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

## Envelope Violation (bounce-back contract)

Every downstream skill declares its `## Preconditions` schema in its own SKILL.md. The `using-copywriting-toolkit` router validates the envelope against that schema BEFORE launching the skill. On violation, the router does not launch; instead it emits a bounce-back envelope and re-routes upstream.

### Violation envelope shape

```json
{
  "violation": {
    "detected_by": "copywriting-<skill-that-rejected>",
    "detected_at": "ISO8601 timestamp",
    "missing": ["field1", "field2.nested"],
    "malformed": [{ "field": "name", "expected": "enum[a|b|c]", "got": "..." }],
    "bounce_to": "copywriting-<upstream-skill-to-re-enter>",
    "bounce_round": 1,
    "user_message": "Plain-language explanation for the user — what the pipeline cannot proceed without"
  },
  "original_envelope": { "...": "frozen snapshot of the envelope that failed validation — operator / audit inspection only; NOT auto-merged on re-entry" },
  "retries": {
    "bounce_round": 1,
    "revise_round_count": 0,
    "total_retries": 1
  }
}
```

### Bounce rules

1. **Single skill declares, router enforces** — skills do NOT self-dispatch bounce; they return the violation shape and let the router route.
2. **`original_envelope` is a forensic snapshot, not a merge source** — it freezes the envelope the router rejected so the user / operator can inspect what failed. On re-entry the upstream skill (typically `copywriting-intake`) runs FRESH; `original_envelope` is not merged back into the live envelope. This mirrors Express Mode's rule that bounce-backs force Q1-Q10: if Express synthesis was good enough, the violation would not have fired — so the re-entry starts from user words, not stale synthesis.
3. **Round caps** — three independent counters converge into `total_retries`:
   - `bounce_round` — increments on each schema violation
   - `revise_round_count` — increments on each evaluator-verdict auto-revise (Phase 7 FIXABLE, Phase 8 loop-back)
   - `total_retries = bounce_round + revise_round_count` — the aggregate
   Hard caps:
   - `bounce_round >= 3` → HALT (schema-loop stuck)
   - `revise_round_count >= 2` per phase → HALT (evaluator-loop stuck)
   - **`total_retries >= 4` (combined)** → HALT regardless of which counter got there. Prevents pathological cycles where schema bounces and verdict revisions alternate to bypass individual caps (mirrors `superpowers:executing-plans` stop-and-ask: when you can't make progress, ask)
4. **Evaluator verdicts are NOT violations** — `NEEDS_REVISION` from a MUST gate is a verdict with its own loop-back rule. Do not conflate: violation = schema gap before skill runs; verdict = judgement after skill runs. Both increment `total_retries`.
5. **user_message is mandatory** — always human-readable; cite the specific SKILL.md Preconditions row that failed (or evaluator finding, for verdict loops).

### Multi-field violations

If several fields are missing, list them all in `missing[]`. Router picks the SINGLE furthest-upstream skill to bounce to — usually `copywriting-intake` if any Level 1 field is absent. Bouncing to multiple upstreams in one round is forbidden (round counter would be ambiguous).

### Audit-stage exception

`copywriting-audit-stage` does NOT accept bounce-back to `copywriting-intake` (audit bypasses intake by design). Its only bounce target is `using-copywriting-toolkit` for re-collecting `external_copy` full text.

## Router Validation

`using-copywriting-toolkit` is the single enforcement point for precondition validation. It performs three checks before every skill launch:

1. **Aggregate retry cap** — read `envelope.retries.total_retries`; if `>= 4`, HALT and ask the user (do not launch any skill, do not bounce). Present the retries breakdown (`bounce_round` / `revise_round_count`) so the user can see why progress stalled.
2. **Preconditions check** — load the target skill's `## Preconditions § Required envelope fields` table from its SKILL.md, verify every row against the current envelope. On any missing / malformed field → emit `violation` envelope, do NOT launch the target skill, route to the `bounce_to` skill named in the target's Preconditions, increment `bounce_round` and `total_retries`.
3. **Express qualification (Shape A only)** — per `using-copywriting-toolkit/protocols/phase-decision-tree.md §Step 0.5`, inspect raw brief against intake's Level 1 field set. If qualified, dispatch intake in Express Mode (`copywriting-intake/protocols/express-mode.md`); otherwise default to Q1-Q10 full intake.

Router does not draft, does not judge gate verdicts, does not rewrite. It routes, validates, and bounces.

### Why validation lives in the router, not each skill

- **Single source of truth** — when preconditions change, only the target skill's SKILL.md Preconditions table changes. Router reads it fresh; no duplicated validation logic drifts.
- **Downstream skills stay focused** — ideation, drafting, voice tuning, gates all assume a well-formed envelope. They do not contain defensive input-validation code paths.
- **bounce_round counter is a router-local concern** — a single validator keeps the round cap coherent. If skills self-dispatched bounces, round counting would fragment and the round-3 HALT rule could be violated.

### Express Mode is not a Preconditions bypass

Express Mode replaces Q1-Q10 **elicitation** with synthesis-plus-single-turn-confirmation. The Intake Completeness MUST gate still runs. The downstream skill still sees a well-formed envelope that satisfies its Preconditions. If Express-synthesised fields turn out to be wrong, a downstream skill will emit a violation → router routes back to intake → intake on re-entry forces Q1-Q10 (not Express) because bounce-backs are a disqualifier.

## Cross-Plugin Delegation (Loose)

Phase 1 Message Confirmation inside `copywriting-intake` may RECOMMEND `planning-team` when the problem is thesis-level (unclear positioning / audience / goal). Do NOT enforce — user may proceed anyway. No auto-delegation.

## Agents

Plugin-local pair — NOT shared with `domain-teams`. Infrastructure stays independent.

### `agents/copywriter.md` (worker)

Drafting / ideation / audit-variant producer. Persona: reader-first copywriter in 糸井 / 岩崎 / 眞木 / 谷山 (JP) and Ogilvy / Schwartz / Halbert / Cialdini (Anglo) lineages, with 小霜「嘘をつかない」 discipline. Model tier: sonnet.

Used by (launches the agent, passing protocol + standards paths):
- `copywriting-intake` (Phase 0-1 brainstorming + Q1-Q10 intake)
- `copywriting-ideation` (Phase 2 divergence subagents + convergence)
- `copywriting-neta-injection` (Phase 3 WebSearch pipeline A-D + 4 techniques)
- 5 Phase-4 drafter skills (short / mid / long-pasona / long-extended / light-action)
- `copywriting-voice-positioning-stage` / `copywriting-voice-tone-stage` (Phase 5-6 tuning passes)
- `copywriting-audit-stage` (Phase 2 diagnose / Phase 3 rewrite variants)

Does NOT produce gate verdicts — that is `copywriter-evaluator`'s role.

### `agents/copywriter-evaluator.md` (evaluator)

Gate verdict producer. Persona: strict legal / framework reviewer (景品表示法 / FTC / Cialdini misuse / PASONA / BEAF / QUEST / PASTOR / PREP / CREMA / voice quadrant / form appropriate). Deliberately NOT copywriter-persona — aesthetic capture is an anti-pattern that contaminates ethics / form judgement. Model tier: opus.

Used by:
- `copywriting-intake` (Intake Completeness MUST gate on Understanding Summary)
- `copywriting-neta-injection` (Neta Safety SHOULD gate)
- `copywriting-voice-tone-stage` (Voice Consistency SHOULD gate)
- `copywriting-ethics-check-stage` (Ethics MUST gate, Phase 7)
- `copywriting-form-check-stage` (Form 8a MUST + 8b SHOULD, Phase 8)
- `copywriting-audit-stage` (reuses Phase 5-8 gates on external copy)

Does NOT draft or soften — only judges.

### Why two agents, two personas

Separation keeps each role honest:

- Copywriter persona (reader-first, voice-disciplined) produces quality drafts but is the wrong lens for legal / ethics / framework judgement — it prioritises elegance over compliance.
- Legal-reviewer persona produces reliable gate verdicts but is the wrong lens for drafting — it prioritises risk-avoidance over rhetorical force.

Running a single multi-role agent blurs both. Using `domain-teams:worker` / `domain-teams:evaluator` (generic) loses the copywriting-specific priors (lineage attribution rules, ethics landmines, voice traditions). Hence the specialized pair.

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
  agents/
    copywriter.md              # worker — sonnet, drafting / ideation / audit variants
    copywriter-evaluator.md    # evaluator — opus, legal / framework / voice gates
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
