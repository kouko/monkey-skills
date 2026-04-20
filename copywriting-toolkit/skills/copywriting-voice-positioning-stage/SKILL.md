---
name: copywriting-voice-positioning-stage
description: Phase 5 Voice Quadrant positioning — 2-axis macro typology (Authority↔Affinity × Reason↔Emotion), EN/ZH/JP practitioners per quadrant, Schwartz × Quadrant routing. Use after Phase 4 draft before Phase 6 tone tuning. ボイス・ポジショニング。文案聲音象限。
---

# copywriting-voice-positioning-stage

Phase 5 — strategic voice positioning. Consumes a Phase 4 `draft` and tags it with a `voice_quadrant` before Phase 6 (`copywriting-voice-tone-stage`) performs tactical 4-axis tone tuning.

**Canon lives in** `standards/voice-quadrant-positioning.md` (658 lines). This SKILL.md is the **routing surface**, not the content — do not inline quadrant definitions or brand corpora when using this skill; read the standard.

## Scope

- Macro typology only: choose a voice **family** (1 of 4 quadrants), not micro-tuned tone.
- Input: Phase 4 envelope with `draft` + `brief` + (optionally) `message_thesis`, Schwartz awareness level, target audience register.
- Output: envelope with a new `voice_quadrant` field + optional `edge_note` (for legitimate Q2↔Q3 / Q1↔Q4 edge positions) + `next_stage: copywriting-voice-tone-stage`.
- Out of scope: 4-axis tone (Formality / Seriousness / Respectfulness / Enthusiasm) — that is Phase 6's job (`voice-and-tone.md`).

## The 2 Axes (summary)

```
         Authority (high social distance / institutional)
                 ↑
   Q1  Authority-Reason  |  Q2  Authority-Emotion
                         |
Reason ──────────────────┼────────────────── Emotion
                         |
   Q4  Affinity-Reason   |  Q3  Affinity-Emotion
                 ↓
         Affinity (low social distance / peer)
```

- **Authority ↔ Affinity** = Halliday (1978) Tenor: social distance / institutional vs peer register.
- **Reason ↔ Emotion** = Vaughn (1980, 1986) FCB Think/Feel axis.

**Synthesis disclosure**: the 2-axis **combination** is this team's synthesis. Cite Vaughn and Halliday individually as axis grounding; the combination is team synthesis, not a pre-existing published framework. See `standards/voice-quadrant-positioning.md §Primary Sources`.

## The Four Quadrants (one-line routing map)

Full per-quadrant treatment — positioning principle, linguistic markers, use cases, canonical brand corpus (with dated originals + copywriter attribution), copywriter cross-references, positive application hints — lives in `standards/voice-quadrant-positioning.md §The Four Quadrants`. Do **not** paraphrase from this summary; read the standard.

| Quadrant | Register | EN anchors | ZH anchors | JP anchors |
|----------|----------|------------|------------|------------|
| **Q1 Authority-Reason** — expert / direct-response, data-led, low 虛詞 density | *The Economist*, Rolls-Royce (Ogilvy 1958), WebMD | 報導者 The Reporter; Ogilvy / Schwartz / Halbert lineage for long-form DR | (craft cross-ref: Ogilvy school) |
| **Q2 Authority-Emotion** — manifesto / aspirational, aphoristic, Cialdini-authority aesthetic | Apple (Think Different, 1997), Nike (Just Do It, 1988), Patagonia, J&J | 誠品書店 (李欣頻 1990s), 中興百貨 (許舜英 1988–2001), 左岸咖啡館 (葉明桂) | MUJI 無印良品 (小池一子 / 田中一光 / Kenya Hara) |
| **Q3 Affinity-Emotion** — warm / conversational, narrative entry, peer solidarity | MailChimp, Innocent Drinks, Airbnb host-voice | TW consumer-warm tradition (see standard §Q3) | 糸井重里 (ほぼ日), 岩崎俊一, eg. 眞木準 lineage |
| **Q4 Affinity-Reason** — helpful advisor / practical utility, high specificity, peer register | REI expert advice, IKEA assembly voice | ZH consumer-advocate tradition (see standard §Q4) | 無印 operational copy overlap; category-specific practitioners |

Practitioner detail per quadrant — full voice statements, paired attributes, dated canonical corpus lines, era narration, copywriter attribution — is in the standard. **Do not invent brand lines; cite from the standard's corpus.**

## Schwartz × Quadrant Routing

When Phase 4 carries a Schwartz awareness level (from `persuasion-psychology-anchor.md`), it constrains the quadrant choice:

| Schwartz Level | Preferred Quadrant | Avoid |
|----------------|-------------------|-------|
| Level 1 (Most Aware) | Q4 (direct action) | Q2 (over-concept) |
| Level 2 (Product Aware) | Q4 / Q1 | — |
| Level 3 (Solution Aware) | Q1 / Q3 | — |
| Level 4 (Problem Aware) | Q3 (empathy entry) | Q4 direct push |
| Level 5 (Unaware) | **Q3 narrative entry** | **Q4 collapses conversion** |

**Hard rule**: never use Q4 direct-action voice for Schwartz Level 5 — mirrors the Schwartz (1966) no-direct-Offer rule. Full rationale in `standards/voice-quadrant-positioning.md §With persuasion-psychology-anchor.md Schwartz Levels`.

## Grounding (primary sources)

- **Vaughn, R.** (1980) "How Advertising Works: A Planning Model." *JAR* 20(5). FCB Think/Feel axis → Reason↔Emotion. **Canonical.**
- **Vaughn, R.** (1986) "How Advertising Works: A Planning Model Revisited." *JAR* 26(1).
- **Halliday, M.A.K.** (1978) *Language as Social Semiotic*. Edward Arnold. Register theory (Field / **Tenor** / Mode) → Authority↔Affinity. **Foundational.**
- **Halliday & Hasan** (1985) *Language, Context, and Text*. Deakin UP / OUP 1989.
- **Mark & Pearson** (2001) *The Hero and the Outlaw* — 12 brand archetypes, flagged **heuristic only** (see Neher 1996 critique + Xara-Brasil et al. 2018 empirical reduction to 4 clusters, cited in standard).

Full bibliography + contested-status flags in `standards/voice-quadrant-positioning.md §Primary Sources`.

## Preconditions

Formal schema used by `using-copywriting-toolkit` router for bounce-back routing. On violation, router emits the bounce-back envelope defined in `../../CLAUDE.md §Envelope Violation`.

### Required envelope fields (Level 1 — BLOCKED if missing)

| Field | Type | Source | Notes |
|---|---|---|---|
| `phase` | enum | Phase 4 OR Phase 3 overlay | `phase-4-draft` or `phase-3-neta-overlaid` |
| `form` | enum | intake | one of 5 Phase-4 form types — determines quadrant anchor corpus |
| `draft` | string | Phase 4 | non-empty; audit-stage may pass `external_copy` here |
| `brief.target_audience` | string | intake | for Tenor (Authority ↔ Affinity) diagnosis |
| `message_thesis` | string | intake | for Think/Feel (Reason ↔ Emotion) diagnosis |

### Optional fields

| Field | Type | Notes |
|---|---|---|
| `brief.schwartz_level` | enum 1-5 | activates Schwartz × Quadrant hard-rule table (Level 5 ≠ Q4) |
| `brief.voice_reference` | string | if present, constrains primary quadrant |
| `brief.channel` | string | affects register calibration |

### Upstream bounce target on violation

- `draft` missing → bounce to `copywriting-<form>` (Phase 4 drafter)
- `form` missing → bounce to `using-copywriting-toolkit` for mis-routing
- `brief` or `message_thesis` missing → bounce to `copywriting-intake`

## I/O Contract

**Input envelope** (from Phase 4):
```json
{
  "phase": "phase-4-draft",
  "form": "<long-form-pasona | mid-form | short-form | light-action | long-form-extended>",
  "brief": {
    "schwartz_level": "1 | 2 | 3 | 4 | 5",
    "...": "from intake"
  },
  "message_thesis": "...",
  "draft": "...",
  "next_stage": "copywriting-voice-positioning-stage"
}
```

**Output envelope** (to Phase 6):
```json
{
  "phase": "phase-5-voice-positioned",
  "form": "...",
  "brief": { "...": "passthrough (includes schwartz_level)" },
  "message_thesis": "...",
  "draft": "...",
  "voice_quadrant": {
    "primary": "Q1 | Q2 | Q3 | Q4",
    "edge": "Q2-Q3 | Q1-Q4 | null",
    "rationale": "1–3 sentences citing brand anchor from standard",
    "schwartz_alignment": "ok | hard_rule_applied | conflict_flagged",
    "execution_reference": "target-language native anchor(s) in the chosen quadrant — e.g. '龔大中 / 全聯經濟美學派' for zh-TW Q3. Optional when voice_reference is same-language.",
    "user_intent_signal": "original cross-language maestro the user cited, preserved for audit — e.g. '糸井重里'. null when no cross-language signal."
  },
  "next_stage": "copywriting-voice-tone-stage"
}
```

Positioning is orientation, not prison — legitimate edge positions (Q2↔Q3, Q1↔Q4) are allowed; record them in `edge`. Diagonal mixing (Q1+Q3, Q2+Q4) inside one piece is an anti-pattern — see `standards/voice-quadrant-positioning.md §Anti-Patterns`.

## Workflow

1. **Read** Phase 4 envelope.
2. **Load** `standards/voice-quadrant-positioning.md` in full. Quadrant selection must cite at least one brand corpus entry from the standard — do not invent anchors.
3. **Diagnose axes**:
   - Tenor (Authority vs Affinity) from brief's audience + channel + brand relationship.
   - Think/Feel (Reason vs Emotion) from message_thesis + decision type.
4. **Apply Schwartz × Quadrant table** if `brief.schwartz_level` is present. If the quadrant chosen on voice grounds collides with Schwartz preference, the Schwartz hard rule (Level 5 ≠ Q4) wins; soft mismatches surface as `schwartz_alignment: "conflict_flagged"` with rationale.
5. **Resolve cross-language execution anchor** (v1.2.1). If `brief.voice_notes.user_intent_signal` is present AND the cited maestro's native language ≠ `brief.output_language`, the maestro is a **quadrant signal**, NOT a source text:
   - Parse the maestro → quadrant mapping per `standards/voice-quadrant-positioning.md` (e.g. 糸井重里 → Q3 / Ogilvy → Q1 / 許舜英 → Q2).
   - Select the **target-language native anchor(s)** in that same quadrant from the standard's Per-quadrant anchors section — e.g. zh-TW Q3 → 龔大中 / 全聯經濟美學派; zh-TW Q2 → 許舜英 / 李欣頻 / 葉明桂; EN Q3 → MailChimp / Innocent.
   - Record as `voice_quadrant.execution_reference` (target-language anchor name(s)) alongside `voice_quadrant.user_intent_signal` (original maestro, preserved for audit).
   - Downstream Phase 4 drafter ideates **natively in `output_language`** using `execution_reference` register. Do NOT instruct the drafter to "translate from" or "channel" the cross-language maestro — that path produces 翻譯腔 (translation-flavored prose) which fails Voice Consistency.
6. **Check adjacency**: if the draft shows legitimate edge positioning, record it. If it shows diagonal mixing, flag as voice-collapse risk before Phase 6.
7. **Emit** output envelope with `next_stage: copywriting-voice-tone-stage`.

## Gate (SHOULD — downstream)

This skill does **not** own a voice-consistency gate. The SHOULD-tier Voice Consistency gate is owned by `copywriting-voice-tone-stage` (Phase 6) via `rubrics/voice-consistency-gate.md` in that skill. It evaluates consistency of the Phase 6 tone-tuned output against the `voice_quadrant` chosen here. Phase 5's job is to set the target; Phase 6 is where the gate fires.

If the Phase 6 evaluator returns NEEDS_REVISION citing quadrant mismatch, the revision loop can bounce back here to re-diagnose — but the gate lives in the tone skill, not here.

## Anti-patterns

- **Inlining the 658-line canon into this SKILL.md, the envelope, or the chat.** The standard is the canonical source; link to it.
- **Inventing brand corpus lines** ("Apple once said …"). Only cite from the standard's dated, attributed corpus.
- **Treating the quadrant as a hard label.** Voice lives on a continuum; legitimate edges exist — use `edge` field.
- **Diagonal mixing (Q1+Q3 or Q2+Q4) inside one piece** without deliberate transition craft — produces voice collapse.
- **Using Q4 direct-action voice for Schwartz Level 5 Unaware readers** — collapses conversion (Schwartz 1966 no-direct-Offer rule).
- **Skipping the archetype contested-status flag.** Mark & Pearson (2001) is heuristic, not empirical consensus — carry forward the flag when citing archetypes in the rationale.

## References

- `standards/voice-quadrant-positioning.md` — full 658-line canon (quadrants, brand corpora, Schwartz integration, anti-patterns, primary sources).
- Phase 6: `copywriting-voice-tone-stage` — 4-axis tone tuning + Voice Consistency gate.
- Phase 4 upstream: `copywriting-long-form-pasona`, `copywriting-mid-form`, `copywriting-short-form`, `copywriting-light-action`, `copywriting-long-form-extended` — each carries `persuasion-psychology-anchor.md` for Schwartz levels.
