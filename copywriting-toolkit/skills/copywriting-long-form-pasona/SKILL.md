---
name: copywriting-long-form-pasona
description: Phase 4 long-form drafter — PASONA / 新PASONA / PASBECONA (神田昌典 canonical). Use for landing pages, sales letters, email campaigns, 記事広告, long CM copy. 長文案・PASONA。
---

# copywriting-long-form-pasona

Phase 4 variant — PASONA-family long-form drafter. Produces landing-page, sales-letter, email-campaign, and 記事広告 copy using 神田昌典's 旧 PASONA (5 stages) / 新 PASONA (6 stages) / PASBECONA (9 stages) canon. Hands the `draft` envelope field to `copywriting-voice-quadrant-stage`.

## Triggers

Run this skill when the brief targets any of:

- Landing pages (JP or JP-first audience)
- Sales letters with problem-agitation-solution-offer-narrow-action arc
- Email campaigns (sequence or single long-form)
- 記事広告 / advertorial long-form
- Long CM copy / video script prose
- High-ticket purchase (heavy-action) flows where PASONA-family fits best

Source workflow: `domain-teams/skills/copywriting-team/SKILL.md` § Long-Form Copy Writing.

Route away when:
- Audience is EN / international or brief favors education-first / story-first positioning → `copywriting-long-form-extended` (QUEST / PASTOR)
- Brief is headline / tagline only → `copywriting-short-form`
- Brief is EC product description → `copywriting-mid-form`
- Brief is opt-in / subscribe / download micro-conversion → `copywriting-light-action`

## Input Envelope

Expects upstream envelope from `copywriting-intake` (or `copywriting-ideation` if Phase 2 ran, or `copywriting-neta-injection` in pre-draft mode):

```json
{
  "phase": "phase-4-draft",
  "form": "long-form-pasona",
  "brief": { "product": "...", "audience": "...", "schwartz_level": "...", "voice_reference": "...", "target_length": "...", "channel": "..." },
  "message_thesis": "...",
  "ideation_pool": ["... optional — Affinity-quadrant seed candidates ..."],
  "neta_candidates": ["... optional pre-draft ..."]
}
```

Hard gate: `copywriting-intake` must have passed Intake Completeness. For PASBECONA (the longest variant), `target_length` and `channel` must be explicit — PASBECONA's 9 stages are wasted on short channels.

## Preconditions

Formal schema used by `using-copywriting-toolkit` router for bounce-back routing. On violation, router emits the bounce-back envelope defined in `../../CLAUDE.md §Envelope Violation`.

### Required envelope fields (Level 1 — BLOCKED if missing)

| Field | Type | Source | Notes |
|---|---|---|---|
| `phase` | enum | intake / ideation / neta | one of `phase-1-confirmed`, `phase-express-confirmed`, `phase-2-ideation-complete`, `phase-3-neta-baked` |
| `form` | string | intake | must equal `long-form-pasona` |
| `brief.product` | string | intake | non-empty |
| `brief.target_audience` | string | intake | Schwartz-aware persona |
| `brief.schwartz_level` | enum 1-5 | intake | drives PASONA stage emphasis |
| `brief.target_length` | string | intake | word-count range (short / medium / long / PASBECONA-long) |
| `brief.channel` | string | intake | LP / sales letter / email / 記事広告 |
| `message_thesis` | string | intake | confirmed 1-sentence thesis |
| `gate_verdict` | enum | intake | `PASS` or `PASS_WITH_NOTES` |

### Optional fields

| Field | Type | Notes |
|---|---|---|
| `brief.voice_reference` | string | 糸井 / 岩崎 / 眞木 / Ogilvy / default |
| `ideation_pool.winners[]` | array | if Phase 2 ran, Affinity-quadrant seeds feed Affinity stage |
| `neta_candidates[]` | array | if Phase 3 ran pre-draft |

### Upstream bounce target on violation

`copywriting-intake` — missing Level 1. If `form != "long-form-pasona"`, router mis-routed; bounce to `using-copywriting-toolkit`. If `target_length == "PASBECONA-long"` but `channel` lacks long-form fit → intake for length / channel reconciliation.

## Drafting Approach

The `copywriter` agent loads `protocols/write-long-form-copy.md` and `standards/long-form-pasona-canon.md`. Standard encodes:

- 旧 PASONA (5 stages) — 神田 2016 canonical book-first publication
- 新 PASONA (6 stages) — 神田 2016『稼ぐ言葉の法則』revision
- PASBECONA (9 stages) — 神田・衣田 2021『コピーライティング技術大全』extended form
- Three-framework applicability matrix (length × channel × awareness level routing)
- Inter-stage flow design principles
- Ethics boundary (delegated to `copywriting-ethics-check-stage`)
- Anti-patterns (problem-stage over-agitation, solution-stage without narrow-down)

Persuasion psychology layer (Cialdini 6 / Schwartz 5 / Kahneman System 1/2) lives in `standards/persuasion-psychology-anchor.md`. PASONA's Problem → Affinity → Solution arc maps onto Schwartz awareness levels (most-aware → unaware) — anchor standard provides the mapping.

SNS-era consumer behavior layer lives in `standards/sns-evolution-aisas-ulssas.md`. Long-form PASONA copy running on SNS-native channels must route through AISAS (秋山・杉山 2004) / SIPS / ULSSAS (飯髙 2019) consumer behavior models — purchase-funnel copy that ignores Search + Share stages fails on SNS.

Framework flow enforced by the protocol:
1. Framework selection — PASONA / 新 PASONA / PASBECONA — based on length + awareness level (see standard's routing matrix)
2. Seed integration — ideation pool Affinity candidates feed the Affinity stage; neta candidates (pre-draft mode) feed where relevant
3. Stage-by-stage draft following 神田 canonical order
4. Benefit / Narrow-down / Action stages bear the conversion weight; Problem / Agitation stages bear the awareness-raising weight

See `standards/long-form-pasona-canon.md` for the full canon, `standards/sns-evolution-aisas-ulssas.md` for SNS-era routing, and `protocols/write-long-form-copy.md` for the drafting procedure. Do not inline their content here.

## Inline Duplication Notice

`standards/persuasion-psychology-anchor.md` (5-way duplicate across Phase-4 workflow skills) and `standards/sns-evolution-aisas-ulssas.md` (2-way duplicate with `copywriting-light-action`) are byte-identical copies of the source in `domain-teams/skills/copywriting-team/standards/`. Drift-sync is accepted cost — see `copywriting-toolkit/CLAUDE.md` § Inline-Duplication Drift Risk.

## Output

The `copywriter` appends to envelope:

```json
{
  "phase": "phase-4-draft",
  "form": "long-form-pasona",
  "framework_selected": "pasona | new-pasona | pasbecona",
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
| 7 | `copywriting-ethics-check-stage` | MUST (evaluator-only) — 景品表示法 / FTC + dark-pattern check on narrow-down + action stages |
| 8 | `copywriting-form-check-stage` | MUST (evaluator-only) — PASONA stage adherence + length band match |
| (SHOULD) | voice-consistency inside form-check-stage | SHOULD — long-form with multiple sections triggers this |

## Next Stage

Hand off `draft` + full envelope to `copywriting-voice-quadrant-stage`. If user opted for post-draft neta overlay, `copywriting-neta-injection` runs first, then voice-positioning-stage.
