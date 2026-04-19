---
name: copywriting-light-action
description: Phase 4 light-action drafter — PREP / CREMA for opt-in, subscribe, download, LINE 登録, micro-conversions (Kaushik 2007). Use for email opt-in pages, newsletter subscribe, free download LP, light SNS action copy. 文案・軽アクション・PREP/CREMA。
---

# copywriting-light-action

Phase 4 variant — PREP / CREMA light-action micro-conversion drafter. Produces copy targeting micro-conversions (per Kaushik 2007) rather than macro-conversions (heavy-ticket purchase). Hands the `draft` envelope field to `copywriting-voice-positioning-stage`.

## Triggers

Run this skill when the brief targets any of:

- Email opt-in pages, newsletter subscribe forms
- Free download landing pages
- LINE 登録 pages, Discord join, community gate copy
- Light affiliate content with soft action at the end
- SNS posts with explicit action prompt (follow, like, share, comment)
- Article-format content with light action prompt at the end
- Light LP click-through copy

Source workflow: `domain-teams/skills/copywriting-team/SKILL.md` § Light-Action Copy Writing (PREP / CREMA).

Route away when:
- Brief is heavy-action (purchase, high-ticket) → `copywriting-long-form-pasona` or `copywriting-long-form-extended`
- Brief is headline / tagline only with no action → `copywriting-short-form`
- Brief is EC product description → `copywriting-mid-form`

## Input Envelope

Expects upstream envelope from `copywriting-intake` (or `copywriting-ideation` if Phase 2 ran, or `copywriting-neta-injection` in pre-draft mode):

```json
{
  "phase": "phase-4-draft",
  "form": "light-action",
  "brief": { "product": "...", "audience": "...", "schwartz_level": "...", "voice_ref": "...", "action_weight": "light", "target_action": "opt-in | subscribe | download | follow | share | ..." },
  "message_thesis": "...",
  "ideation_pool": ["... optional ..."],
  "neta_candidates": ["... optional pre-draft ..."]
}
```

Hard gate: `copywriting-intake` must have passed Intake Completeness with `action_weight = light` surfaced as a Level 2 field. If intake reports `action_weight = heavy`, re-route to long-form skills — CREMA / PREP are not for purchase-level conversion.

## Drafting Approach

Worker loads `protocols/write-short-form-copy.md` and `standards/light-action-frameworks.md`. Standard encodes:

- PREP 法 (Anglo 1980s) — Point → Reason → Example → Point — 4-stage lightweight logical frame; default for share-triggering or no-CTA logical payload
- CREMA 法 (JP ~2021) — Conclusion → Reason → Evidence → Method → Action — 5-stage PREP extension adding Method + Action; default for any non-purchase action prompt
- Light-action taxonomy theoretical anchors — Kaushik 2007 (micro/macro conversion) + Cialdini 1984 + Freedman & Fraser 1966 foot-in-the-door
- Framing — why a separate framework zone exists (micro-conversion ≠ scaled-down macro-conversion)
- PREP → CREMA structural extension rules
- Form-to-framework routing matrix + Selection criteria
- PREP / PASONA / BEAF / QUEST-PASTOR demarcation
- Integration notes with `persuasion-psychology-anchor.md`, `sns-evolution-aisas-ulssas.md`, `mid-form-beaf-canon.md`, `long-form-extended-frameworks.md`
- Ethics boundary — commitment-escalation transparency + 景品表示法
- Anti-patterns (CREMA Action stage without Method grounding, PREP used as incomplete PASONA)

Persuasion psychology layer (Cialdini 6 commitment / consistency + Schwartz 5 + Kahneman System 1) lives in `standards/persuasion-psychology-anchor.md`. Foot-in-the-door (Freedman & Fraser 1966) is the load-bearing psychology anchor for light-action — CREMA's Action stage is its structural expression. The anchor standard provides the mapping.

SNS-era consumer behavior layer lives in `standards/sns-evolution-aisas-ulssas.md`. Light-action copy running on SNS-native channels (follow / like / share) must route through AISAS Share stage and ULSSAS UGC-fueled loops — purchase-funnel psychology does not apply to these actions. SIPS (電通 2011) and ULSSAS (飯髙 2019) carry the relevant models.

Framework flow enforced by the protocol:
1. Framework selection — PREP vs CREMA — via `light-action-frameworks.md` §Selection criteria. CREMA is default for any explicit action prompt; PREP for share-triggering logical content
2. Stage-by-stage draft following the 4 (PREP) or 5 (CREMA) stage order
3. Commitment-escalation transparency check — CREMA's Action must not hide scope-creep (e.g., "subscribe" that secretly enrolls in auto-billing); this is enforced at ethics gate but should be self-audited before handoff
4. Character-count + SNS-form compliance per channel

See `standards/light-action-frameworks.md` for the full canon, `standards/sns-evolution-aisas-ulssas.md` for SNS-era routing, and `protocols/write-short-form-copy.md` for the drafting procedure. Do not inline their content here.

## Inline Duplication Notice

`standards/persuasion-psychology-anchor.md` (5-way duplicate across Phase-4 workflow skills) and `standards/sns-evolution-aisas-ulssas.md` (2-way duplicate with `copywriting-long-form-pasona`) are byte-identical copies of the source in `domain-teams/skills/copywriting-team/standards/`. Drift-sync is accepted cost — see `copywriting-toolkit/CLAUDE.md` § Inline-Duplication Drift Risk.

Note: this skill shares `protocols/write-short-form-copy.md` verbatim with `copywriting-short-form`. The protocol dispatches on `form` — each skill's own Type-A standard (catchcopy-canon vs light-action-frameworks) carries the framework-specific stage definitions.

## Output

Worker appends to envelope:

```json
{
  "phase": "phase-4-draft",
  "form": "light-action",
  "framework_selected": "prep | crema",
  "draft": "<stage-labeled light-action copy with clearly declared target_action>",
  "next_stage": "copywriting-voice-positioning-stage"
}
```

## Downstream Gates

After this skill completes, orchestrator runs (in order):

| Phase | Skill | Gate level |
|---|---|---|
| 5 | `copywriting-voice-positioning-stage` | worker |
| 6 | `copywriting-voice-tone-stage` | worker |
| 7 | `copywriting-ethics-check-stage` | MUST (evaluator-only) — commitment-escalation transparency + 景品表示法 + 2023 Oct ステマ regulation |
| 8 | `copywriting-form-check-stage` | MUST (evaluator-only) — PREP 4-stage or CREMA 5-stage adherence + action-prompt clarity |
| (SHOULD) | voice-consistency inside form-check-stage | SHOULD — multi-candidate output triggers this |

Foot-in-the-door dark-pattern abuse (e.g., opt-in that escalates to auto-billed purchase) trigger an automatic NEEDS_REVISION at ethics gate. Commitment escalation must be transparent.

## Next Stage

Hand off `draft` + full envelope to `copywriting-voice-positioning-stage`. If user opted for post-draft neta overlay, `copywriting-neta-injection` runs first, then voice-positioning-stage.
