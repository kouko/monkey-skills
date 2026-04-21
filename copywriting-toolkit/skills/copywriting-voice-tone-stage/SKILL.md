---
name: copywriting-voice-tone-stage
description: Fix voice drift / tone inconsistency and apply maestro lineage register — Ogilvy 4-axis + JP (糸井 / 岩崎 / 眞木 / 谷山) + ZH (許舜英 / 李欣頻 / 葉明桂 / 龔大中) lineage craft. Use when you have a draft with a quadrant assigned AND need sentence-level tone polish — 語尾 / 呼吸 / rhythm refinement — before ethics gate. Not for macro quadrant selection (use copywriting-voice-quadrant-stage) or legal / ethics review (use copywriting-ethics-check-stage). ボイス・トーン調整・系譜クラフト。文案聲調修飾・語氣校正。
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

Invoke this skill **after** `copywriting-voice-quadrant-stage` (Phase 5)
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

### When lineage craft applies (Pass 3)

Pass 3 loads a language-specific lineage standard. Exactly one of the
two lineage files loads — never both, never cross-transplanted:

**JP lineage** — `jp-copy-craft-lineage.md` loads when:

1. `brief.output_language` is `ja` (Japanese-language output), OR
2. `brief.voice_reference` ∈ {糸井重里, 岩崎俊一, 眞木準, 谷山雅計}, OR
3. `voice_quadrant.primary == "Q3"` (Affinity-Emotion) AND the message
   thesis is state-proposal / 余韻-driven rather than action-prompting.

**ZH lineage** — `zh-copy-craft-lineage.md` loads when:

1. `brief.output_language` is `zh-TW` or `zh-HK` AND a Q2-or-Q2-edge
   maestro voice is declared, OR
2. `brief.voice_reference` ∈ {許舜英, 李欣頻, 葉明桂}, OR
3. `voice_quadrant.primary == "Q2"` (Authority-Emotion) AND the target
   audience is ZH-sphere consumer-class context (e.g., TW 都會消費主義,
   HK 文化消費) where the Taiwan / Hong Kong Q2 canon is the relevant
   reference, not Anglo / JP.

Note: `voice_quadrant` is the object emitted by Phase 5
(`{primary, edge, rationale, schwartz_alignment}`) — always dereference
`.primary`, never read it as a string.

**Neither lineage applies** → Pass 3 does NOT run. Voice tuning operates
on `voice-and-tone.md` alone (Ogilvy Anglo canon + 18F / Mailchimp
4-axis + tone context-switching).

**Cross-tradition transplant is forbidden** — never force JP lineage
patterns onto ZH output (or vice versa), never force either onto Anglo
output. `voice-and-tone.md §Anti-Patterns` + both lineage standards'
§Anti-Patterns sections explicitly ban this.

**If both lineage triggers match** (e.g., brief has `voice_reference:
糸井重里` but `output_language: zh-TW`) → emit a `violation` envelope
per `../../CLAUDE.md §Envelope Violation`; router routes to
`copywriting-intake` for clarification. Do NOT self-dispatch the
bounce — that would fragment `bounce_round` counter per L2 contract
(§Router Validation single enforcement point).

Violation payload:
```json
{
  "violation": {
    "detected_by": "copywriting-voice-tone-stage",
    "missing": [],
    "malformed": [{
      "field": "brief.voice_reference + brief.output_language",
      "expected": "consistent lineage (JP maestro + ja OR ZH maestro + zh-*)",
      "got": "cross-lineage conflict (e.g., 糸井重里 + zh-TW)"
    }],
    "bounce_to": "copywriting-intake",
    "user_message": "Voice reference and output language disagree on lineage — intake needs to resolve which tradition applies."
  }
}
```

## What This Skill Owns

- **Standards**:
  - `standards/voice-and-tone.md` — Tier 2 cross-framework voice SSOT.
    Ogilvy 1963/1983 Anglo long-copy canon + JP emotional-resonance
    tradition (糸井 state-proposal, 岩崎 余韻) + 18F / Mailchimp 4-axis
    voice model + Mailchimp "one voice, multiple tones" + tone context-
    switching table (onboarding / error / crisis / celebration).
  - `standards/jp-copy-craft-lineage.md` — Tier 3 JP deep-dive on
    糸井重里 / 岩崎俊一 / 眞木準 / 谷山雅計 voice signatures:
    representative corpus, stylistic grammar patterns, generational
    context, and **LLM reproduction gap analysis** per master. Invoked
    per §When lineage craft applies (JP branch).
  - `standards/zh-copy-craft-lineage.md` — Tier 3 ZH deep-dive on
    許舜英 (意識形態 / 中興百貨) / 李欣頻 (誠品) / 葉明桂 (奧美 /
    左岸) voice signatures: 11 + 7 + 3 dated verbatim corpus entries,
    stylistic grammar (definitional inversion / cultural-critique
    density / brand-personality mapping), generational context
    (1990s 台灣都會消費主義覺醒), 4 attribution-drift corrections,
    and per-master LLM reproduction gap analysis. Invoked per §When
    lineage craft applies (ZH branch).
- **Rubric (SHOULD gate)**:
  - `rubrics/voice-consistency-gate.md` — cross-stage / cross-candidate
    voice stability + tone contextual appropriateness + maestro fidelity.
    Run AFTER tone tuning as the last voice-layer check before handing to
    Phase 7 ethics gates.

This skill does **not** own:

- Voice quadrant selection — `copywriting-voice-quadrant-stage` (Phase 5).
- Framework structure (PASONA stage ordering etc.) — Phase 4 workflow skills.
- Ethics / legal / ステマ — `copywriting-ethics-check-stage` (Phase 7).
- Form-appropriate character discipline — `copywriting-form-check-stage` (Phase 8).

## Phase 6 Operating Model

Three sequential passes on the `draft`. Each pass returns either an edited
draft or an annotation the next pass must honor. No pass may silently
rewrite Phase 4's structural skeleton — frameworks are replaceable, voice
is an irreplaceable asset, but structural edits belong to Phase 4 re-runs,
not here.

### Pre-pass: `schwartz_alignment` awareness note (v1.2.0 — downgraded from consumer)

**v1.2.0 change**: The authoritative consumer of `schwartz_alignment` moved to Phase 8 8b rubric (single enforcement point per §Verification Density Principle). Pre-pass now downgraded to a lightweight awareness note.

If `envelope.voice_quadrant.schwartz_alignment == "conflict_flagged"`:

- Record it in `tone_notes.schwartz_awareness_note` (one-line acknowledgement; do NOT elaborate full rationale here — Phase 5 already recorded it in `voice_quadrant.rationale`).
- Pass 1 may lightly compensate 4-axis defaults (e.g., avoid double-mismatch by keeping enthusiasm matter-of-fact when L2 forced into Q2) but is NOT responsible for rigorous compensation verification — that's Phase 8 8b's job.
- If `hard_rule_applied`, acknowledge but do not attempt to revert.
- Pass `voice_quadrant` (including `schwartz_alignment`) forward unchanged per `../../CLAUDE.md §Immutable fields`.

**Rationale for downgrade**: Phase 5 writes the flag; Phase 8 8b consumes it at the form-fidelity level. Phase 6 pre-pass previously did a third pass of compensation reasoning that duplicated Phase 5's rationale emit and Phase 8's fidelity check — redundant per v1.2.0 §Verification Density Principle. Lightweight note keeps the flag visible to Pass 1 without re-verifying.

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
2. **Self-check for axis drift** (v1.2.0 — downgraded from full scan):
   lightly scan the draft for sentences whose axis reading obviously
   conflicts with the target vector by ≥2 steps. Rewrite the flagged
   sentences. Do NOT do a rigorous per-sentence enumeration — that is
   the Voice Consistency SHOULD gate's job (single authoritative
   enforcement per §Verification Density Principle). Pass 1 is "catch
   the obvious" not "catch everything".
3. Preserve framework stage boundaries (PASONA A / S / O labels, BEAF
   stages, etc.) verbatim.
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

### Pass 3 — Lineage craft / register signal / axis extreme (runs only per §When lineage craft applies)

Pass 3 branches into **three mutually exclusive load paths** based on voice_reference + voice_quadrant configuration. v1.3.2 expanded v1.2.0's single "craft gate" path into 3 tiers for the voice anchor library (PR 1 foundation v1.3.0 + content v1.3.1).

#### Pass 3 activation guard (v1.3.2 — 3-tier branching)

**Before loading any standards**, the agent MUST verify Pass 3 trigger evaluates to TRUE per §When lineage craft applies. Then branch:

```
# Pass 3 activation predicate (outer gate, v1.2.0 preserved)
if Pass 3 triggered:

    # Tier 1 — Craft Gate (existing 6 canonical masters, v1.2.0 behavior)
    if voice_reference ∈ {糸井重里, 岩崎俊一, 眞木準, 谷山雅計}:
        load standards/jp-copy-craft-lineage.md
        load standards/voice-anchor-meta-core.md  (for over-mimic mitigation)
        # NO meta-detail, NO per-quadrant, NO axis-extreme
        proceed to Pass 3a

    elif voice_reference ∈ {許舜英, 李欣頻, 葉明桂}:
        load standards/zh-copy-craft-lineage.md
        load standards/voice-anchor-meta-core.md
        proceed to Pass 3b

    # Tier 3 — Axis Extreme (new, v1.3.2)
    elif voice_quadrant.position starts with "axis-":
        load standards/voice-anchor-meta-core.md
        load standards/axis-extreme-anchors.md
        proceed to Pass 3c

    # Tier 2 — Register Signal (new, v1.3.2) — default for any other Pass-3-triggered case
    else:
        load standards/voice-anchor-meta-core.md
        load standards/voice-anchor-meta-detail.md
        position = voice_quadrant.position OR "center" (default fallback)
        load standards/{output_language}-q{voice_quadrant.primary}-anchors.md §Landmark: {position}
        if cross-reference-valid-for[output_language] == STRONG for cited anchor:
            load standards/{cross-ref-lang}-q{voice_quadrant.primary}-anchors.md §Landmark: {position}
        proceed to Pass 3d

else (Pass 3 not triggered):
    # No load, skip to Phase 7
    tone_notes.lineage_applied = null
    tone_notes.register_signal_applied = null
    tone_notes.axis_extreme_applied = null
```

**If no branch condition is TRUE → Pass 3 MUST NOT load any standards.** Record the null annotations and skip. Do NOT load "just in case".

**Rationale** (v1.2.0 §Verification Density Principle + v1.3.2 optimization 1-4):
- v1.2.0 preserved craft-gate gate (6 masters); lineage standards 700 lines / 8-10K tokens load only when craft master cited
- v1.3.2 adds register-signal + axis-extreme branches with **landmark-targeted section read** (~1.5K per section) and **meta-core vs meta-detail split** (core ~2K always when Pass 3 triggers; detail ~3K only when Register Signal)
- Net: Pass 3 per-trigger weighted cost ~5-7K (down from 8-10K pre-split)

**If predicate is TRUE → proceed to Pass 3a / 3b / 3c / 3d as applicable**.

#### Pass 3a — JP lineage (JP trigger matched)

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

**Critical attribution corrections (JP)** — 『リゲイン「24時間戦えますか？」』
is NOT 岩崎俊一 (jp-copy-craft-lineage.md §Critical Attribution
Corrections). Do not attribute misattributed copies during reference lookup.

#### Pass 3b — ZH lineage (ZH trigger matched)

Load `standards/zh-copy-craft-lineage.md`. Apply the master-specific voice
signature for the referenced maestro:

- **許舜英** — definitional inversion (「服裝就是一種高明的政治」), cross-
  domain vocabulary transplant (政治 / 姿態 / 命題 / 邏輯), cultural-
  critique payload density, paradox-as-hook ("不是 X, 是 Y"). 意識形態
  廣告 中興百貨 1988-1999 canon.
- **李欣頻** — 書店 / 閱讀 philosophical prose (「閱讀是唯一的迷信」),
  existential-aphorism register, 誠品敦南 1990s-2000s canon. Voice is
  Q2 tipping into Q2-Q3 edge (warmer than 許舜英's cool-aesthetic).
- **葉明桂** — brand-personality mapping via systematic strategic
  frameworks. 左岸咖啡館 1998- canon. Voice is Q2-Q3 edge (authority
  framing via warmth). Distinguished from 許舜英's cool manifesto
  register by brand-construction thesis (「不是賣咖啡，是經營咖啡館」).

**Critical attribution corrections (ZH)** — see
`zh-copy-craft-lineage.md §Critical Attribution Corrections`:
- 「我不在咖啡館...」originates from Peter Altenberg (German poet,
  sinicized); NOT an original 葉明桂 line, though used in 左岸 campaigns.
- 「拋開書本到街上去」references 寺山修司 1967 book title; 李欣頻
  credited the allusion in her own writing.
- 意識形態廣告 founded **1987** (not 1988 as sometimes reported);
  中興百貨 canonical window 1988-1999.
- Content-farm reprints of "中興百貨 文案" mix canonical 許舜英 work
  with post-2000 agency imitations — anchor only to《許舜英購物日記》+
  意識形態 award archives when citing.

#### Pass 3 cross-branch common rules

**LLM reproduction gap — mandatory disclosure**. Each master in each
lineage has a documented gap between surface mimicry and true voice
signature; the standard's per-master §LLM Reproduction Gap section
names the specific failure mode. When Pass 3 outputs a rewrite,
`tone_notes.lineage_gap` must record which gap the rewrite is most at
risk of falling into + what mitigation was applied. Examples:

- JP 岩崎: "gap = direct emotional statement where 余韻 is required;
  mitigation = replaced 形容詞 + 句点 with 体言止め + 読点 tail"
- ZH 許舜英: "gap = hollow definitional inversion without cultural-
  critique payload; mitigation = forced concrete target audience tension
  before drafting, verified inversion lands on a real social observation
  not a decorative paradox"

**Forbidden cross-transplant**: Pass 3a and Pass 3b are mutually
exclusive — never apply JP signatures to ZH output or vice versa.
Both lineage standards' §Anti-Patterns sections ban this explicitly.

#### Pass 3c — Axis Extreme branch (v1.3.2, new)

When `voice_quadrant.position` starts with `axis-*` (e.g. `axis-authority-extreme`), Pass 3 loads `axis-extreme-anchors.md` — a cross-language file covering 4 axis-extreme positions (authority/affinity/reason/emotion). **MVP**: file is placeholder with candidate lists; V2 research will populate with full entries (BBC News / Supreme Court / Hallmark / Wikipedia / Mailchimp help center neutral etc.).

During MVP period: if brief triggers `axis-*` position, agent should note the placeholder status in `tone_notes.axis_extreme_applied = "mvp-stub-{position}"` and apply best-effort register matching from candidate list in the file. If V2 content is present, apply per standard anchor entry.

#### Pass 3d — Register Signal branch (v1.3.2, new)

When voice_reference is not a craft-gate master AND position is not axis-extreme (the default Pass-3-triggered case), Pass 3 loads the per-quadrant anchor file matching `output_language` × `voice_quadrant.primary`. **Landmark-targeted read**: only the `## Landmark: {position}` section is consumed (~1.5K tokens vs ~3K whole file). Fallback to whole-file read when position is missing.

When cross-reference registry (meta-detail) shows `cross-reference-valid-for[output_language] == STRONG` for any anchor in the target section, ALSO load the corresponding cross-lang file's same Landmark section. Most common: JP→zh-TW STRONG (zh-TW Q3 brief with 糸井 cross-ref loads jp-q3 center).

Register-Signal apply:
1. Read per-quadrant Landmark section — extract anchor entries + metadata (per meta-core schema)
2. For each candidate anchor, verify anchor selection rubric (meta-core 4 conditions) + consult over-mimic mitigation registry (meta-core) for required clauses
3. Apply best-fit anchor's voice signature to draft rewrite
4. Record `tone_notes.register_signal_applied = {anchor_slug, landmark_position, mitigation_clauses_applied}`

**Cross-branch rule**: if multiple branches' conditions match (e.g. voice_reference names a craft-gate master AND voice_quadrant.position = axis-*), Craft Gate wins. Tier precedence: Craft Gate > Axis Extreme > Register Signal.

## Preconditions

Formal schema used by `using-copywriting-toolkit` router for bounce-back routing. On violation, router emits the bounce-back envelope defined in `../../CLAUDE.md §Envelope Violation`.

### Required envelope fields (Level 1 — BLOCKED if missing)

| Field | Type | Source | Notes |
|---|---|---|---|
| `phase` | enum | Phase 5 | must equal `phase-5-voice-positioned` |
| `voice_quadrant.primary` | enum Q1-Q4 | Phase 5 | required — macro quadrant before tactical tuning |
| `draft` | string | Phase 4 | non-empty |
| `form` | enum | intake | |
| `brief.output_language` | enum | intake | `ja` / `en` / `zh-TW` / etc. — activates JP lineage pass when `ja` |

### Optional fields (activate extra passes)

| Field | Type | Notes |
|---|---|---|
| `brief.voice_reference` | string | 糸井 / 岩崎 / 眞木 / 谷山 → activates Pass 3 JP lineage |
| `voice_quadrant.edge` | enum | Q2-Q3 / Q1-Q4 allowed edge positions |
| `message_thesis` | string | state-proposal vs action-prompting classification → Q3 JP lineage trigger |

### Upstream bounce target on violation

- `voice_quadrant` missing → bounce to `copywriting-voice-quadrant-stage` (Phase 5 must run first)
- `draft` missing → bounce to `copywriting-<form>` (Phase 4 drafter)
- `brief.output_language` missing → bounce to `copywriting-intake` (Level 1 / 2 gap)

## Input Envelope (consumed)

Shape inherited from `copywriting-toolkit/CLAUDE.md §Handoff Envelope`,
post-Phase 5:

```json
{
  "phase": "phase-5-voice-positioned",
  "form": "long-form-pasona | long-form-extended | mid-form | short-form | light-action | audit",
  "brief": { "voice_reference": "...", "output_language": "ja | en | zh-TW", "...": "..." },
  "message_thesis": "...",
  "voice_quadrant": {
    "primary": "Q1 | Q2 | Q3 | Q4",
    "edge": "Q2-Q3 | Q1-Q4 | null",
    "rationale": "Phase 5 rationale",
    "schwartz_alignment": "ok | hard_rule_applied | conflict_flagged"
  },
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
  emotional-resonance vs Anglo benefit-clear fit, voice quadrant
  coherence, over-mimic adherence (v1.3.2, scoped to Pass 3), and
  **thesis alignment** (v1.3.4, scoped to Pass 3 — catches anchor-
  induced drift from `envelope.message_thesis`).

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
  conditions (§When lineage craft applies — JP branch) are unmet.
- Force-fitting ZH lineage onto JP / Anglo output when the ZH branch
  trigger conditions are unmet.
- Cross-transplanting JP signatures (体言止め, 余韻) into ZH output or
  ZH signatures (definitional inversion, cultural-critique density)
  into JP output. Both lineage standards ban this in §Anti-Patterns.
- Attributing 『24時間戦えますか？』to 岩崎俊一 (documented drift #8 in
  jp-copy-craft-lineage.md).
- Attributing 「我不在咖啡館...」as original 葉明桂 line (actually Peter
  Altenberg sinicized — zh-copy-craft-lineage.md drift #Z1).
- Citing "中興百貨 文案" from content-farm reprint lists without
  anchoring to 許舜英購物日記 + 意識形態 archives (drift #Z4).
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
  (verbatim copy from `domain-teams:copywriting-team`).
- `standards/zh-copy-craft-lineage.md` — Tier 3 ZH lineage deep-dive
  (NEW in v1.0.0; primary-source-researched; not cp'd from
  `domain-teams:copywriting-team`).
- `rubrics/voice-consistency-gate.md` — SHOULD gate rubric (verbatim copy).
