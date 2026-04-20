---
name: copywriting-long-form-extended
description: Phase 4 long-form drafter — QUEST (Fortin 2005) / PASTOR (Edwards 2016). Use for EN/intl landing pages, coaching / consulting sales, story-driven sales letters, guide-based positioning. Not for JP 神田 PASONA family (use copywriting-long-form-pasona) or EC product copy (use copywriting-mid-form). 長文案・QUEST・PASTOR。
---

# copywriting-long-form-extended

Phase 4 variant — QUEST / PASTOR extended long-form drafter. Produces EN / international landing-page and story-driven sales copy for briefs where PASONA-family is not the best fit. Hands the `draft` envelope field to `copywriting-voice-quadrant-stage`.

## Triggers

Run this skill when the brief targets any of:

- EN / international audience landing pages
- Coaching / consulting / expert-positioning sales pages
- Story-driven sales letters (shepherd-guide narrative)
- Education-first or guide-based positioning
- Content-marketing long-form with a soft sell at the end
- Any long-form brief where PASONA's problem-agitation arc feels culturally wrong for the audience

Source workflow: `domain-teams/skills/copywriting-team/SKILL.md` § Long-Form Extended (QUEST / PASTOR).

Route away when:
- Audience is JP-first with strong problem-agitation tolerance → `copywriting-long-form-pasona`
- Brief is headline / tagline only → `copywriting-short-form`
- Brief is EC product description → `copywriting-mid-form`
- Brief is opt-in / subscribe / download micro-conversion → `copywriting-light-action`

## Input Envelope

Expects upstream envelope from `copywriting-intake` (or `copywriting-ideation` if Phase 2 ran, or `copywriting-neta-injection` in pre-draft mode):

```json
{
  "phase": "phase-4-draft",
  "form": "long-form-extended",
  "brief": { "product": "...", "audience": "...", "schwartz_level": "...", "voice_reference": "...", "positioning": "expert | shepherd | ...", "language": "en | ja | ..." },
  "message_thesis": "...",
  "ideation_pool": ["... optional ..."],
  "neta_candidates": ["... optional pre-draft ..."]
}
```

Hard gate: `copywriting-intake` must have passed Intake Completeness. `positioning` and `language` fields drive the QUEST-vs-PASTOR decision — if absent, kick back to intake.

## Preconditions

Formal schema used by `using-copywriting-toolkit` router for bounce-back routing. On violation, router emits the bounce-back envelope defined in `../../CLAUDE.md §Envelope Violation`.

### Required envelope fields (Level 1 — BLOCKED if missing)

| Field | Type | Source | Notes |
|---|---|---|---|
| `phase` | enum | intake / ideation / neta | one of `phase-1-confirmed`, `phase-express-confirmed`, `phase-2-ideation-complete`, `phase-3-neta-baked` |
| `form` | string | intake | must equal `long-form-extended` |
| `brief.product` | string | intake | non-empty |
| `brief.target_audience` | string | intake | Schwartz-aware persona |
| `brief.schwartz_level` | enum 1-5 | intake | |
| `brief.positioning` | enum | intake | `expert` / `shepherd` / `guide` / `educator` — drives QUEST vs PASTOR |
| `brief.language` | enum | intake | `en` / `ja` / `zh-TW` / etc. — EN default favours this skill over pasona |
| `message_thesis` | string | intake | |
| `gate_verdict` | enum | intake | `PASS` or `PASS_WITH_NOTES` |

### Optional fields

| Field | Type | Notes |
|---|---|---|
| `brief.voice_reference` | string | Ogilvy / Schwartz / default |
| `ideation_pool.winners[]` | array | seeds Stimulate (QUEST) or Story / Transformation (PASTOR) |
| `neta_candidates[]` | array | if Phase 3 ran pre-draft |

### Upstream bounce target on violation

`copywriting-intake` — missing Level 1. If `form != "long-form-extended"`, bounce to `using-copywriting-toolkit`. If `positioning` and `language` are both absent, audience culture fit is unknowable — always bounce; do not guess.

## Drafting Approach

The `copywriter` agent loads `protocols/write-long-form-copy.md` and `standards/long-form-extended-frameworks.md`. Standard encodes:

- QUEST — Michel Fortin 2005 (Qualify → Understand → Educate → Stimulate → Transition) + 5 stages + mountain-metaphor flow
- PASTOR — Ray Edwards 2016 (Problem / Person → Amplify / Aspiration → Story / Solution → Testimony / Transformation → Offer → Response) + 6 stages with multi-meaning dimensions + narrative requirement
- Extended routing matrix (education-first / expert positioning → QUEST; personal-story / shepherd-guide positioning → PASTOR)
- Selection criteria (extended) — length, audience, narrative-fit
- Cross-framework stage mapping with PASONA (for mixed-audience briefs)
- Ethics boundary (delegated to `copywriting-ethics-check-stage`)
- Anti-patterns (QUEST without qualifier → wasted education; PASTOR without transformation proof → hollow story)

Persuasion psychology layer (Cialdini 6 / Schwartz 5 / Kahneman System 1/2) lives in `standards/persuasion-psychology-anchor.md`. QUEST's Qualify stage maps onto Schwartz awareness-level filtering; PASTOR's Testimony / Transformation stage maps onto Cialdini's social-proof and liking principles.

Framework flow enforced by the protocol:
1. Framework selection — QUEST vs PASTOR — via `long-form-extended-frameworks.md` §Extended routing matrix
2. Seed integration — ideation pool candidates feed Stimulate (QUEST) or Story / Transformation (PASTOR)
3. Stage-by-stage draft
4. For QUEST: verify mountain-metaphor progression — no stage skipped. For PASTOR: narrative must be grounded in real testimony, not composite fiction (ethics boundary with FTC Endorsement Guides)

See `standards/long-form-extended-frameworks.md` for the full canon and `protocols/write-long-form-copy.md` for the drafting procedure. Do not inline their content here.

## Inline Duplication Notice

`standards/persuasion-psychology-anchor.md` is a byte-identical copy of the source in `domain-teams/skills/copywriting-team/standards/`. Drift-sync across the 5 Phase-4 workflow skills is accepted cost — see `copywriting-toolkit/CLAUDE.md` § Inline-Duplication Drift Risk.

Note: this skill shares `protocols/write-long-form-copy.md` verbatim with `copywriting-long-form-pasona`. The protocol dispatches on `framework_selected` — each skill's own Type-A standard (pasona-canon vs extended-frameworks) carries the framework-specific stage definitions.

## Output

The `copywriter` appends to envelope:

```json
{
  "phase": "phase-4-draft",
  "form": "long-form-extended",
  "framework_selected": "quest | pastor",
  "draft": "<stage-labeled long-form copy>",
  "next_stage": "copywriting-voice-quadrant-stage"
}
```

## Downstream Gates

After this skill completes, orchestrator runs (in order):

| Phase | Skill | Gate level |
|---|---|---|
| 5 | `copywriting-voice-quadrant-stage` | copywriter |
| 6 | `copywriting-voice-tone-stage` | copywriter |
| 7 | `copywriting-ethics-check-stage` | MUST (evaluator-only) — FTC Endorsement Guides especially strict on PASTOR testimony |
| 8 | `copywriting-form-check-stage` | MUST (evaluator-only) — QUEST 5-stage or PASTOR 6-stage adherence + length band match |
| (SHOULD) | voice-consistency inside form-check-stage | SHOULD — long-form with multiple sections triggers this |

PASTOR briefs with composite / fictional testimony trigger an automatic NEEDS_REVISION verdict at ethics gate. Real transformation evidence is non-negotiable.

## Next Stage

Hand off `draft` + full envelope to `copywriting-voice-quadrant-stage`. If user opted for post-draft neta overlay, `copywriting-neta-injection` runs first, then voice-positioning-stage.
