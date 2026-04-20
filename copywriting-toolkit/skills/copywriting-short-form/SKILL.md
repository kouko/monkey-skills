---
name: copywriting-short-form
description: Write キャッチコピー / headlines / taglines (7-15 chars, AIDMA A+I, 3秒ルール, 5 切入點 framework). Use when you have a confirmed brief with short-form deliverable — tagline, SNS post, banner, CM title — after intake, before voice positioning. Not for EC product description (use copywriting-mid-form) or long-form LP / sales letter (use copywriting-long-form-pasona / -extended). Not for raw briefs — route via using-copywriting-toolkit first. 短文案・キャッチコピー作成。
---

# copywriting-short-form

Phase 4 variant — short-form headline / キャッチコピー drafter. Produces 7-15 character candidates using AIDMA A+I scope, 3 秒ルール landability, and 5 切入點 approach selection. Hands the `draft` envelope field to `copywriting-voice-quadrant-stage`.

## Triggers

Run this skill when the brief targets any of:

- Headlines, taglines, CM titles
- SNS post body, banner copy, short ad copy
- Product naming catchcopy
- Short キャッチコピー for campaigns (landing-page hero copy stays in long-form)

Source workflow: `domain-teams/skills/copywriting-team/SKILL.md` § Short-Form キャッチコピー Writing.

Route away when:
- Brief needs mid-form EC product body → `copywriting-mid-form`
- Brief needs LP / email / sales letter → `copywriting-long-form-pasona` or `copywriting-long-form-extended`
- Brief is opt-in / subscribe / download CTA → `copywriting-light-action`

## Input Envelope

Expects upstream envelope from `copywriting-intake` (or `copywriting-ideation` if Phase 2 ran, or `copywriting-neta-injection` in pre-draft mode):

```json
{
  "phase": "phase-4-draft",
  "form": "short-form",
  "brief": { "product": "...", "audience": "...", "schwartz_level": "...", "voice_reference": "..." },
  "message_thesis": "...",
  "ideation_pool": ["... optional ..."],
  "neta_candidates": ["... optional pre-draft ..."]
}
```

Hard gate: `copywriting-intake` must have passed Intake Completeness before this skill runs. Do not short-circuit if `brief.schwartz_level` or `brief.voice_reference` is missing — kick back to intake.

## Preconditions

Formal schema used by `using-copywriting-toolkit` router for bounce-back routing. On violation, router emits the bounce-back envelope defined in `../../CLAUDE.md §Envelope Violation`.

### Required envelope fields (Level 1 — BLOCKED if missing)

| Field | Type | Source | Notes |
|---|---|---|---|
| `phase` | enum | intake / ideation / neta | one of `phase-1-confirmed`, `phase-express-confirmed`, `phase-2-ideation-complete`, `phase-3-neta-baked` |
| `form` | string | intake | must equal `short-form` |
| `brief.product` | string | intake | non-empty |
| `brief.target_audience` | string | intake | target emotion / pain surfaced |
| `brief.channel` | string | intake | SNS / banner / CM title / tagline / etc. |
| `brief.char_limit_band` | string | intake | 7-15 default; explicit if custom |
| `gate_verdict` | enum | intake | `PASS` or `PASS_WITH_NOTES` |

### Required form-specific fields

| Field | Type | Notes |
|---|---|---|
| `brief.schwartz_level` | enum 1-5 | drives 5 切入點 selection |
| `brief.voice_reference` | string | maestro tag (糸井 / 岩崎 / 眞木 / 谷山 / Ogilvy / default) |

### Upstream bounce target on violation

`copywriting-intake` — any Level 1 missing is an intake gap. If `form != "short-form"`, router mis-routed; bounce to `using-copywriting-toolkit`.

## Drafting Approach

The `copywriter` agent loads `protocols/write-short-form-copy.md` and `standards/short-form-catchcopy-canon.md`. Standard encodes:

- AIDMA short-form action scope (A + I only — short copy does not carry D/M/A)
- 7-15 character golden range rationale
- 3 秒ルール landability test
- 5 切入點 approach tree (benefit / fear / subversion / calling / question)
- 4 voice masters (糸井重里 / 岩崎俊一 / 眞木準 / 谷山雅計) + TCC 年鑑 reference
- Anglo vs JP demarcation + SNS-era evolution notes
- Anti-patterns (generic-voice, AI-sounding candidates)

Persuasion psychology layer (Cialdini 6 / Schwartz 5 / Kahneman System 1 routing) lives in `standards/persuasion-psychology-anchor.md`. The `copywriter` reads it alongside the canon for approach-to-psychology mapping.

Framework flow enforced by the protocol:
1. Approach selection from 5 切入點 (matches Schwartz awareness level)
2. Divergent draft pass (multiple candidates, AIDMA A+I only)
3. Forbidden-phrase audit — 谷山 「なんかいいよね禁止」; each finalist must justify with 3 concrete reasons
4. Character-count + 3 秒ルール compliance check

See `standards/short-form-catchcopy-canon.md` for the full canon and `protocols/write-short-form-copy.md` for the drafting procedure. Do not inline their content here.

## Inline Duplication Notice

`standards/persuasion-psychology-anchor.md` is a byte-identical copy of the source in `domain-teams/skills/copywriting-team/standards/`. Drift-sync across the 5 Phase-4 workflow skills is accepted cost — see `copywriting-toolkit/CLAUDE.md` § Inline-Duplication Drift Risk.

## Output

The `copywriter` appends to envelope:

```json
{
  "phase": "phase-4-draft",
  "form": "short-form",
  "draft": "<3-5 finalist candidates, each with 3 justifying reasons + char count>",
  "approach_selected": "<one of 5 切入點>",
  "next_stage": "copywriting-voice-quadrant-stage"
}
```

Candidate output shape — progress reporting, checkpoint prompts, and 3-reason rationale are produced inline following the envelope schema above. Structured handoff-format tooling is owned by `copywriting-intake` (Phase 0-1 entry) and is not re-loaded here.

## Downstream Gates

After this skill completes, orchestrator runs (in order):

| Phase | Skill | Gate level |
|---|---|---|
| 5 | `copywriting-voice-quadrant-stage` | copywriter |
| 6 | `copywriting-voice-tone-stage` | copywriter |
| 7 | `copywriting-ethics-check-stage` | MUST (evaluator-only) — 景品表示法 / FTC |
| 8 | `copywriting-form-check-stage` | MUST (evaluator-only) — framework adherence, 7-15 chars, 3 秒ルール |
| (SHOULD) | voice-consistency inside form-check-stage | SHOULD — multi-candidate output triggers this |

Short-form outputs almost always trigger the voice-consistency gate because multiple candidates share one brand voice. Do not suppress it.

## Next Stage

Hand off `draft` + full envelope to `copywriting-voice-quadrant-stage`. If user opted for post-draft neta overlay, `copywriting-neta-injection` runs first, then voice-positioning-stage.
