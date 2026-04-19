---
name: copywriting-mid-form
description: Phase 4 mid-form drafter — EC product copy (BEAF — Benefit → Evidence → Advantage → Feature). Use for Rakuten / Amazon JP / POP / presentation materials. 中文案・EC 商品コピー。
---

# copywriting-mid-form

Phase 4 variant — mid-form EC product copy drafter. Produces BEAF-ordered product descriptions (Benefit → Evidence → Advantage → Feature) for EC listings, POP, and in-store presentation. Hands the `draft` envelope field to `copywriting-voice-positioning-stage`.

## Triggers

Run this skill when the brief targets any of:

- Rakuten / Amazon JP product descriptions
- In-store POP / shelf-talker copy
- Presentation material product blurbs
- Mid-form EC content where Benefit-first ordering is required
- Product description with evidence / spec layering (not pure feature bullets)

Source workflow: `domain-teams/skills/copywriting-team/SKILL.md` § Mid-Form EC Copy Writing.

Route away when:
- Brief is a 7-15 char headline → `copywriting-short-form`
- Brief is LP / email / sales letter → `copywriting-long-form-pasona` or `copywriting-long-form-extended`
- Brief is opt-in / subscribe / download micro-conversion → `copywriting-light-action`
- Brief is pure FAB / feature bullet list (no persuasion layer needed) → docs-team or design-team owns

## Input Envelope

Expects upstream envelope from `copywriting-intake` (or `copywriting-ideation` if Phase 2 ran, or `copywriting-neta-injection` in pre-draft mode):

```json
{
  "phase": "phase-4-draft",
  "form": "mid-form",
  "brief": { "product": "...", "audience": "...", "schwartz_level": "...", "voice_ref": "...", "evidence_sources": ["..."] },
  "message_thesis": "...",
  "ideation_pool": ["... optional ..."],
  "neta_candidates": ["... optional pre-draft ..."]
}
```

Hard gate: `copywriting-intake` must have passed Intake Completeness before this skill runs. Evidence sources (reviews, spec data, third-party endorsements) must be surfaced in intake — BEAF's Evidence stage depends on them.

## Drafting Approach

The `copywriter` agent loads `protocols/write-mid-form-copy.md` and `standards/mid-form-beaf-canon.md`. Standard encodes:

- BEAF's 4-stage definitions (Benefit → Evidence → Advantage → Feature)
- Importance of Benefit-first ordering (vs spec-first failure mode)
- Character-count range and use cases (EC listing vs POP vs presentation)
- Demarcation from PASONA-family (no problem-agitation in mid-form)
- Differences from FAB (industry confusion correction)
- Anti-patterns (feature-list disguised as copy, unsubstantiated benefit claims)

Persuasion psychology layer (Cialdini 6 social-proof / authority mapping onto Evidence stage, Schwartz 5 level-check) lives in `standards/persuasion-psychology-anchor.md`. The `copywriter` reads it alongside the canon — the Evidence stage in particular depends on Cialdini's social-proof framing.

Framework flow enforced by the protocol:
1. BEAF skeleton — lay out Benefit → Evidence → Advantage → Feature in order
2. Benefit-first enforcement (reject specs-first drafts)
3. Evidence stage backed by intake-surfaced sources; flag BLOCKED if evidence is absent
4. Character-count compliance per use-case

See `standards/mid-form-beaf-canon.md` for the full canon and `protocols/write-mid-form-copy.md` for the drafting procedure. Do not inline their content here.

## Inline Duplication Notice

`standards/persuasion-psychology-anchor.md` is a byte-identical copy of the source in `domain-teams/skills/copywriting-team/standards/`. Drift-sync across the 5 Phase-4 workflow skills is accepted cost — see `copywriting-toolkit/CLAUDE.md` § Inline-Duplication Drift Risk.

## Output

The `copywriter` appends to envelope:

```json
{
  "phase": "phase-4-draft",
  "form": "mid-form",
  "draft": "<BEAF-ordered product copy with evidence citations>",
  "next_stage": "copywriting-voice-positioning-stage"
}
```

## Downstream Gates

After this skill completes, orchestrator runs (in order):

| Phase | Skill | Gate level |
|---|---|---|
| 5 | `copywriting-voice-positioning-stage` | copywriter |
| 6 | `copywriting-voice-tone-stage` | copywriter |
| 7 | `copywriting-ethics-check-stage` | MUST (evaluator-only) — 景品表示法 particularly strict for EC product claims |
| 8 | `copywriting-form-check-stage` | MUST (evaluator-only) — BEAF adherence + character-count range |
| (SHOULD) | voice-consistency inside form-check-stage | SHOULD — if multiple product variants produced |

景品表示法 compliance is non-negotiable for EC mid-form — unsubstantiated benefit claims, 優良誤認 / 有利誤認 hazards, and ステマ (2023 Oct 消費者庁 ruling) all require explicit evidence citations.

## Next Stage

Hand off `draft` + full envelope to `copywriting-voice-positioning-stage`. If user opted for post-draft neta overlay, `copywriting-neta-injection` runs first, then voice-positioning-stage.
