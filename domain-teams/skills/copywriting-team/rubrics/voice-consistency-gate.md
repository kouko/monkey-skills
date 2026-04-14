# Rubric: Voice Consistency Gate

SHOULD gate (qualitative flag-based). Triggers: multi-stage / multi-
candidate artifact (multiple stages, candidates, or a series). For
single-stage / single short-form only artifacts, trigger condition is
not met and the gate is skipped (reason: cross-stage evaluation not
possible).

## Scope Boundary

This gate reviews:
- Voice (brand persona fixed across contexts) stability across
  artifact stages / candidates
- Tone (context-sensitive register) contextual appropriateness
- Voice maestro reference (糸井 / 岩崎 / 眞木 / 谷山) style fidelity
  when adopted
- **Clarity of the JP emotional resonance vs Anglo benefit-clear
  choice** (relative to target audience)

This gate does NOT review:
- Framework structure (PASONA stage ordering, BEAF ordering) →
  `../checklists/persuasion-framework-adherence-checklist.md`
- Ethics / legal boundaries →
  `../checklists/ethics-checklist.md`
- Character-count discipline → `form-appropriate-gate.md`

## Primary Sources

- `../standards/voice-and-tone.md` — Ogilvy 1963/1983 + 糸井 / 岩崎
  JP emotional tradition + 18F / Mailchimp Voice 4-axis + Mailchimp
  "one voice, multiple tones" + Tone context-switching table
  (onboarding / error / crisis / celebration).
- `../standards/voice-quadrant-positioning.md` — 2-axis macro typology
  (Authority↔Affinity × Reason↔Emotion) + EN/ZH/JP representative
  practitioners + ZH micro-indicators (particle density / loanword mix /
  punctuation pacing).
- `../standards/short-form-catchcopy-canon.md` — Four voice maestros
  (糸井 / 岩崎 / 眞木 / 谷山) canonical voice definitions.
- grounding SSOT: `../research/grounding-v4.12.0.md` §3 Cluster B.3-B.8
  + §8 Load-bearing claims; `../research/grounding-v4.18.0.md` for
  voice quadrant grounding.

## Dimensions

### Dimension 1: Brand Voice Stability (RUB-CTW-VC-001)

Whether voice maintains a stable persona across multiple stages /
candidates. Mailchimp principle: "Voice doesn't change much from day
to day."

- 🔴 **Fatal**: The persona becomes a different person across stages /
  candidates (e.g., stage 1 is casual friend tone, stage 3 is
  corporate formal, stage 5 is irreverent joker). The voice guide is
  not functioning as SSOT, and readers sense a patchwork feel.
- 🟡 **Warning**: Overall voice is maintained but drifts in 2-3 spots
  (e.g., one stage becomes extremely formal on the Formality axis, or
  one stage becomes matter-of-fact on the Enthusiasm axis). The drift
  intent is not explained in artifact metadata.
- 🟢 **Clear**: Voice 4-axis position (Formality / Seriousness /
  Respectfulness / Enthusiasm) is consistent across all stages /
  candidates. When comparing example passages, they read as "written
  by the same brand." Any drift is explicitly noted as intentional
  tone adjustment.

### Dimension 2: Tone Contextual Appropriateness (RUB-CTW-VC-002)

Against the Mailchimp Tone context-switching table (onboarding / error /
crisis / celebration), whether context-specific tone is appropriate.
Voice is constant, Tone varies (Mailchimp canonical).

- 🔴 **Fatal**: Context mismatch. Using celebration tone in a crisis
  (bright exclamation marks, emojis, festive feel), playful jokes in
  an error state, suddenly switching to sales-push mode during
  onboarding, or other **tone that misreads the context**. Damages
  reader trust.
- 🟡 **Warning**: Tone partially fits the context but adjustment range
  is insufficient (e.g., entire onboarding is uniformly "enthusiastic
  welcome" with no tonal gradient in the final "next action" stage).
  Or in crisis-adjacent contexts (incident / API outage notification),
  tone is "too serious" and there is concern voice itself is shifting.
- 🟢 **Clear**: Voice is maintained across all contexts while tone is
  appropriately adjusted per context. Specifically: crisis / error
  state shows "sincerity + no deflection," celebration makes "the
  user the subject of gratitude," onboarding shows "enthusiasm +
  embrace," all explicitly designed.

### Dimension 3: Voice Maestro Reference Fidelity (RUB-CTW-VC-003)

When a voice maestro (糸井重里 / 岩崎俊一 / 眞木準 / 谷山雅計) is
declared as the reference voice in artifact metadata or input brief,
whether the output is faithful to that maestro's canonical style.

- 🔴 **Fatal**: Named reference ("糸井風" / "岩崎風" declared) but the
  output departs from the style. Examples:
  - "糸井風" declared → imperative CTA barrage (糸井 is a state-
    proposal type, not an action-driving type)
  - "岩崎風" declared → no Buddhist impermanence or seasonal feel,
    just promotional sales copy
  - "眞木風" declared → zero 掛詞 / phonetic technique, literal
    direct-translation copy
  - "谷山風" declared → descriptive copy with no "resolution / new
    meaning proposal"
- 🟡 **Warning**: Some elements of the maestro's voice are captured but
  overall remains "partially reminiscent." Examples: 糸井's everyday
  vocabulary is present but ambiguity tolerance is weak / 岩崎's
  character range (10-15 字) fits but the finite / impermanence
  sentiment is thin.
- 🟢 **Clear**: The maestro voice's canonical traits (糸井 = state
  proposal / ambiguity space, 岩崎 = seasonal feel / finitude /
  Buddhist impermanence, 眞木 = 掛詞 / phonetics, 谷山 = resolution /
  meaning proposal) are clearly present in the output, at a level
  where placing it alongside the maestro's actual work produces no
  dissonance.
- **Note**: For artifacts that do not declare a maestro reference, this
  dimension is `not_applicable` (neither 🟡 nor 🔴 is assigned).

### Dimension 4: Clarity of Voice Tradition Choice (RUB-CTW-VC-004)

Whether the voice tradition is clearly chosen for the target audience.
Three recognized traditions: **JP emotional** (糸井 / 岩崎 — 余韻,
state-proposal, impermanence), **Anglo benefit-clear** (Ogilvy long-
form direct), **ZH copywriting** (經濟美學 observational wit, 意識形態
literary-ideological, or 數位實務 direct-action — see
`voice-quadrant-positioning.md` §ZH Copywriting Tradition). Prevents
cross-tradition transplant errors.

- 🔴 **Fatal**: Tradition mismatch. A JP-market artifact uses only
  Anglo "Just Do It"-style direct CTA + adjective hype (zero emotional
  resonance / 余韻 / 掛詞). An Anglo-market artifact uses excessively
  ambiguous / 余韻-oriented "translated-sounding" copy. A ZH-market
  (Taiwan) artifact uses pure JP particle density (呢/よ/ね style) or
  pure Anglo benefit-push without 龔大中-style observational warmth.
  Forceful application of a tradition that does not fit the target
  audience.
- 🟡 **Warning**: Tradition choice is not stated in artifact metadata
  and is ambiguous from the output. Example: JP-market target but 30%
  reads as Anglo direct style, 70% as JP emotional — unclear whether
  intentional hybrid or accidental inconsistency. Or choice is stated
  but execution is half-hearted.
- 🟢 **Clear**: Tradition is stated in artifact metadata (e.g., "JP
  emotional / 糸井 + 岩崎系", "Anglo benefit-clear / Ogilvy long-form",
  "ZH 經濟美學 / 龔大中系") + consistently executed throughout the
  output. If hybrid, the intent and proportion are explicitly stated.

### Dimension 5: Voice Quadrant Coherence (RUB-CTW-VC-005)

When a voice quadrant position (Q1 Authority-Reason / Q2 Authority-
Emotion / Q3 Affinity-Emotion / Q4 Affinity-Reason) is declared in
artifact metadata or input brief,
whether the output's linguistic markers are consistent with the
declared quadrant. Grounded in `voice-quadrant-positioning.md`.

**Mechanical distinguishability criteria** (per quadrant):

| Marker | Q1 Authority+Reason | Q2 Authority+Emotion | Q3 Affinity+Emotion | Q4 Affinity+Reason |
|--------|---------------------|---------------------|---------------------|---------------------|
| 虛詞 density (per 100 chars) | ≤2 | ≤2 | 3-6 | ≤2 |
| Emoji / exclamation | prohibited | prohibited | sparing | permitted |
| Abstract-noun ratio | medium-high | high | low | low |
| Imperative verbs leading | rare | rare | rare | common |
| Evidence style | data/citation | aphorism/manifesto | everyday anecdote | numerical specific |

- 🔴 **Fatal**: Declared quadrant is Q1 (Authority+Reason) but output
  uses casual particles, emoji, informal register throughout. Or
  declared Q3 (Affinity+Emotion) but output is data-table-heavy with
  zero emotional resonance. Or declared Q4 (direct action) used for
  Schwartz Level 5 Unaware readers (Q3 narrative entry required per
  `voice-quadrant-positioning.md` §Schwartz × Quadrant).
- 🟡 **Warning**: Quadrant alignment is mostly maintained but 1-2
  sections drift into an adjacent quadrant without declared intent
  (adjacent = Q1↔Q2 or Q1↔Q4 or Q2↔Q3 or Q3↔Q4). Or diagonal mixing
  attempted without deliberate transition craft.
- 🟢 **Clear**: Linguistic markers (particle density, evidence style,
  emotional vocabulary, abstract-noun ratio) are consistent with the
  declared quadrant. Any adjacent-quadrant excursion is deliberate
  and justified.
- **Note**: For artifacts without a quadrant declaration, this
  dimension is `not_applicable` (excluded from verdict calculation).

## Verdict Rules

- Any single 🔴 fatal → `NEEDS_REVISION` (escalate to user)
- **2 or more** 🟡 warnings → `NEEDS_REVISION`
- **1** 🟡 warning (no 🔴) → `PASS_WITH_NOTES` (auto-revise trigger)
- All 🟢 clear → `PASS`
- Dimensions 3 (maestro reference) and 5 (quadrant coherence) are
  `not_applicable` for artifacts without the respective declaration.
  `not_applicable` is excluded from verdict calculation (not counted
  as 🔴, 🟡, or 🟢).

## Rules

- First confirm whether a voice guide SSOT exists. If a brand voice
  guide (4-axis + side-by-side examples) is not included in the
  artifact input, evaluate dimensions 1/2 using "inferred voice" and
  note "voice guide not provided; inferred from output" in `note`.
- Be strict against the temptation to declare maestro reference
  "nominally only." Named references must be judged on canonical
  fidelity.
- Do not mistake tone changes for voice changes. Voice constant / tone
  variable is canon.
- Do not be a gatekeeper. For PASS_WITH_NOTES, concretize the revision
  spec; for NEEDS_REVISION, present at least 1 alternative
  ("rewriting like this would achieve 🟢").

## Output Format

```json
{
  "verdict": "PASS | PASS_WITH_NOTES | NEEDS_REVISION",
  "dimensions": [
    {
      "id": "RUB-CTW-VC-001",
      "name": "Brand Voice Stability",
      "flag": "red | yellow | green | not_applicable",
      "evidence": "Specific quoted examples showing drift / stability",
      "suggestion": "If red/yellow, concrete improvement suggestion"
    }
  ],
  "voice_guide_provided": true,
  "maestro_reference_declared": "糸井 | 岩崎 | 眞木 | 谷山 | none",
  "target_tradition": "JP-emotional | Anglo-benefit-clear | ZH-copywriting | hybrid | unclear",
  "quadrant_declared": "Q1 | Q2 | Q3 | Q4 | none",
  "summary": "1-3 sentence overall assessment + next-step priority"
}
```
