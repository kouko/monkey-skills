---
name: copywriting-voice-tone-stage
description: Phase 6 voice tone tuning + JP lineage craft — Ogilvy + JP emotional resonance 4-axis + 糸井 / 岩崎 / 眞木 lineage with LLM reproduction gap analysis. Use after Phase 5 positioning. ボイス・トーン調整。文案聲調修飾。
---

# copywriting-voice-tone-stage

Phase 6 — **tactical** voice + tone fine-tuning. Phase 5 fixed the macro
quadrant (Authority↔Affinity × Reason↔Emotion); this phase works *inside*
that quadrant: 4-axis micro voice calibration, Mailchimp-style tone
context-switching, and — when a JP voice reference is in force — lineage-
craft deep voice signature application (糸井 / 岩崎 / 眞木) with explicit
LLM reproduction gap awareness.

Output is a polished draft + structured `tone_notes`, handed to Phase 7
ethics check.

## When to Use

Invoke this skill **after** `copywriting-voice-positioning-stage` (Phase 5)
has stamped a `voice_quadrant` onto the envelope AND a workflow skill
(Phase 4: `long-form-pasona` / `long-form-extended` / `mid-form` /
`short-form` / `light-action`) has produced a `draft`.

Skip only when:

- The brief is single-sentence short-form (≤15 chars) AND no voice maestro
  is referenced — Phase 5 output already embodies tone; no micro-tuning
  adds value. (Voice Consistency gate trigger condition also not met — see
  §Gate.)
- The run is an `audit` — audit re-runs Phase 5-8 against existing copy;
  this skill still runs, but treats the provided copy as the draft input
  rather than regenerating.

### When JP lineage applies

The `jp-copy-craft-lineage.md` deep-dive layer is loaded **only** when at
least one of the following is true:

1. `brief.output_language` is `ja` (Japanese-language output).
2. `brief.voice_reference` ∈ {糸井重里, 岩崎俊一, 眞木準, 谷山雅計}.
3. `brief.voice_quadrant` = Q3 (Affinity-Emotion) AND the message thesis
   is state-proposal / 余韻-driven rather than action-prompting.

Otherwise, voice tuning operates on `voice-and-tone.md` alone (Ogilvy Anglo
canon + 18F / Mailchimp 4-axis + tone context-switching). Do **not** force
JP lineage patterns onto Anglo / ZH output — `voice-and-tone.md §Anti-
Patterns` explicitly bans cross-tradition transplant.

## What This Skill Owns

- **Standards**:
  - `standards/voice-and-tone.md` — Tier 2 cross-framework voice SSOT.
    Ogilvy 1963/1983 Anglo long-copy canon + JP emotional-resonance
    tradition (糸井 state-proposal, 岩崎 余韻) + 18F / Mailchimp 4-axis
    voice model + Mailchimp "one voice, multiple tones" + tone context-
    switching table (onboarding / error / crisis / celebration).
  - `standards/jp-copy-craft-lineage.md` — Tier 3 deep-dive on 糸井重里 /
    岩崎俊一 / 眞木準 voice signatures: representative corpus, stylistic
    grammar patterns, generational context, and **LLM reproduction gap
    analysis** per master. Invoked per §When JP lineage applies.
- **Rubric (SHOULD gate)**:
  - `rubrics/voice-consistency-gate.md` — cross-stage / cross-candidate
    voice stability + tone contextual appropriateness + maestro fidelity.
    Run AFTER tone tuning as the last voice-layer check before handing to
    Phase 7 ethics gates.

This skill does **not** own:

- Voice quadrant selection — `copywriting-voice-positioning-stage` (Phase 5).
- Framework structure (PASONA stage ordering etc.) — Phase 4 workflow skills.
- Ethics / legal / ステマ — `copywriting-ethics-check-stage` (Phase 7).
- Form-appropriate character discipline — `copywriting-form-check-stage` (Phase 8).

## Phase 6 Operating Model

Three sequential passes on the `draft`. Each pass returns either an edited
draft or an annotation the next pass must honor. No pass may silently
rewrite Phase 4's structural skeleton — frameworks are replaceable, voice
is an irreplaceable asset, but structural edits belong to Phase 4 re-runs,
not here.

### Pass 1 — 4-axis micro calibration (always runs)

Per `standards/voice-and-tone.md §Voice definition — 4 axes`:

| Axis | Left end | Right end |
|----|------|------|
| Formality | formal | casual |
| Seriousness | serious | funny |
| Respectfulness | respectful | irreverent |
| Enthusiasm | matter-of-fact | enthusiastic |

Action:

1. Extract brand voice axis positions from `brief.voice_reference` +
   `voice_quadrant`. If absent, derive default from Phase 5 quadrant
   (Q1 ≈ formal / serious / respectful / matter-of-fact; Q3 ≈ casual /
   warm / respectful / warm-enthusiastic; etc.) and **disclose** the
   derivation in `tone_notes.axis_default_derived`.
2. Scan the draft for axis drift — any sentence whose axis reading
   conflicts with the target vector by >1 step on any axis.
3. Rewrite only the drift sentences. Preserve framework stage boundaries
   (PASONA A / S / O labels, BEAF stages, etc.) verbatim.
4. Apply Ogilvy commandments explicitly: no empty-hype vocabulary
   (amazing / revolutionary / game-changing), headline voice = body voice
   (no click-bait exemption), long-copy must earn every body sentence.

### Pass 2 — tone context-switching (runs if the draft contains
context-sensitive segments)

Per `standards/voice-and-tone.md §Tone context-switching table`:

| Context | Tone direction | Caution |
|------|------|------|
| Onboarding / Welcome | warm, encouraging | no bait-and-switch to hard sell |
| Error / Failure | calm, specific, non-deflecting | no humor masking |
| Crisis / Incident | serious, timely, transparent | no jokes, no hype, label uncertainty |
| Celebration / Launch | enthusiastic, user-grateful | user is subject, not brand |

**Voice stays constant; tone varies.** If brand voice is "playful,"
error-state remains playful in voice, but tone becomes calm and joke-free.
Mailchimp-explicit rule (§voice-and-tone §Tone context-switching table).

For non-SaaS copy (product ads, long-form sales, キャッチコピー), the four
contexts still map — e.g., PASONA's Affinity stage ≈ Onboarding tone;
Offer stage ≈ Celebration tone (see `voice-and-tone.md §Integration with
PASONA / BEAF / キャッチコピー frameworks`).

### Pass 3 — JP lineage craft (runs only per §When JP lineage applies)

Load `standards/jp-copy-craft-lineage.md`. Apply the master-specific voice
signature for the referenced maestro:

- **糸井重里** — state-proposal grammar (「おいしい生活。」), non-imperative
  句読点 discipline, 平仮名 over-index, 体言止め ending preference.
- **岩崎俊一** — 余韻 / 無常 compound (「やがて、いのちに変わるもの。」),
  Buddhist finiteness undertone, rejects direct CTA.
- **眞木準** — Q2↔Q3 border, 諧謔 + 知性 blend (see `voice-and-tone.md §JP
  emotional-resonance tradition` cross-link).
- **谷山雅計** — discipline-centric (see `jp-copy-craft-lineage.md` for
  full signature).

**LLM reproduction gap — mandatory disclosure**. Each master has a
documented gap between surface mimicry and true voice signature; the
standard's per-master §LLM Reproduction Gap section names the specific
failure mode. When Pass 3 outputs a rewrite, `tone_notes.lineage_gap` must
record which gap the rewrite is most at risk of falling into + what
mitigation was applied (e.g., for 岩崎: "gap = direct emotional statement
where 余韻 is required; mitigation = replaced 形容詞 + 句点 with 体言止め +
読点 tail").

**Critical attribution corrections** — 『リゲイン「24時間戦えますか？」』
is NOT 岩崎俊一 (jp-copy-craft-lineage.md §Critical Attribution
Corrections). Do not attribute misattributed copies during reference lookup.

## Input Envelope (consumed)

Shape inherited from `copywriting-toolkit/CLAUDE.md §Handoff Envelope`,
post-Phase 5:

```json
{
  "phase": "phase-5-positioned",
  "form": "long-form-pasona | long-form-extended | mid-form | short-form | light-action | audit",
  "brief": { "voice_reference": "...", "output_language": "ja | en | zh-TW", "...": "..." },
  "message_thesis": "...",
  "voice_quadrant": "Q1 | Q2 | Q3 | Q4",
  "voice_quadrant_rationale": "Phase 5 rationale",
  "draft": "the Phase 4 draft",
  "next_stage": "copywriting-voice-tone-stage"
}
```

Required keys: `voice_quadrant`, `draft`. Missing either → return to
orchestrator with `status: upstream-incomplete` (Phase 5 must run first).

## Output Envelope (produced)

```json
{
  "phase": "phase-6-toned",
  "form": "long-form-pasona | ...",
  "brief": { "..." : "..." },
  "message_thesis": "...",
  "voice_quadrant": "Q1 | Q2 | Q3 | Q4",
  "voice_quadrant_rationale": "...",
  "draft": "the polished draft after 3 passes",
  "tone_notes": {
    "axis_target": { "formality": "casual", "seriousness": "serious", "respectfulness": "respectful", "enthusiasm": "warm" },
    "axis_default_derived": false,
    "tone_contexts_detected": ["onboarding", "celebration"],
    "tone_adjustments": [
      { "span": "sentence 3 of stage A", "context": "error", "before": "...", "after": "...", "rationale": "calm + non-deflecting" }
    ],
    "lineage_applied": "岩崎俊一 | null",
    "lineage_gap": "direct emotional statement risk; mitigated via 体言止め tail | null",
    "ogilvy_flags": ["removed 'revolutionary' empty-hype token in stage S"]
  },
  "gate_verdict": "PASS | PASS_WITH_NOTES | NEEDS_REVISION",
  "gate_report": { "...see rubric §Output Format..." },
  "next_stage": "copywriting-ethics-check-stage"
}
```

Downstream (`copywriting-ethics-check-stage`) reads `draft` + `tone_notes`
+ `brief`. `tone_notes.ogilvy_flags` can surface
景品表示法 / FTC-relevant removals for Phase 7 cross-check.

## Gate — SHOULD (Voice Consistency)

- **Rubric**: `rubrics/voice-consistency-gate.md`
- **Agent**: `copywriting-toolkit/agents/copywriter-evaluator.md`
- **Trigger**: multi-stage OR multi-candidate artifact (PASONA 6 stages,
  BEAF 4 stages, ideation N candidates, or a series). Per the rubric's
  §Scope Boundary: single-stage / single short-form only → gate is
  skipped with `reason: cross-stage evaluation not possible` recorded in
  the envelope.
- **Position**: runs AFTER all 3 passes, as the last voice-layer check
  before Phase 7 legal gates pick up the artifact.
- **Dimensions** (per rubric): brand voice stability, tone contextual
  appropriateness, maestro style fidelity (if lineage applied), JP
  emotional-resonance vs Anglo benefit-clear fit.

Verdict handling:

- `PASS` → emit envelope; `next_stage: copywriting-ethics-check-stage`.
- `PASS_WITH_NOTES` (≤2 WARNINGS, no FATAL) → apply named fixes in one
  auto-revise round, re-run gate; if still `PASS_WITH_NOTES`, emit with
  notes disclosed (handoff-format §Section 3 max-2-rounds rule).
- `NEEDS_REVISION` (any FATAL or ≥3 WARNINGS) → BLOCKED. Return to the
  specific pass the rubric's `next_action` names. Do not forward to
  Phase 7.

## Anti-Patterns

- Rewriting framework stage structure during voice tuning. PASONA A / S /
  O boundaries are not Phase 6's territory.
- Swapping voice mid-artifact to match tone context ("error → serious
  voice"). `voice-and-tone.md §Anti-Patterns`: voice stays constant, only
  tone shifts.
- Force-fitting JP lineage onto Anglo / ZH output when the trigger
  conditions (§When JP lineage applies) are unmet.
- Attributing 『24時間戦えますか？』to 岩崎俊一 (documented drift #8).
- Filling the Voice Guide axes abstractly ("friendly, professional") with
  no side-by-side on-brand / off-brand examples (`voice-and-tone.md §Brand
  Voice Guide checklist`).
- Headline breaks voice for attention, then body "returns" — trust
  already lost at headline layer.
- Swallowing a `NEEDS_REVISION` gate verdict and forwarding to Phase 7.

## Files

- `standards/voice-and-tone.md` — Tier 2 voice SSOT (verbatim copy from
  `domain-teams:copywriting-team`).
- `standards/jp-copy-craft-lineage.md` — Tier 3 JP lineage deep-dive
  (verbatim copy).
- `rubrics/voice-consistency-gate.md` — SHOULD gate rubric (verbatim copy).
