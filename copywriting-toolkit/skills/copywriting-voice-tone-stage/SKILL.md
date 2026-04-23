---
name: copywriting-voice-tone-stage
description: Fix voice drift / tone inconsistency and apply voice anchor register — Ogilvy 4-axis + individual-creator anchors (JP / ZH / EN). Use when you have a draft with a quadrant assigned AND need sentence-level tone polish — 語尾 / 呼吸 / rhythm refinement — before ethics gate. Not for macro quadrant selection (use copywriting-voice-quadrant-stage) or legal / ethics review (use copywriting-ethics-check-stage). ボイス・トーン調整・系譜クラフト。文案聲調修飾・語氣校正。
---

# copywriting-voice-tone-stage

Phase 6 — **tactical** voice + tone fine-tuning. Phase 5 fixed the macro
quadrant (Authority↔Affinity × Reason↔Emotion); this phase works *inside*
that quadrant: 4-axis micro voice calibration, Mailchimp-style tone
context-switching, and voice-anchor register application (80+ individual-
creator anchors across JP / ZH / EN / zh-HK with explicit LLM reproduction
gap awareness).

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
  adds value.
- The run is an `audit` — audit re-runs Phase 5-8 against existing copy;
  this skill still runs, but treats the provided copy as the draft input
  rather than regenerating.

### When Pass 3 (Voice Anchor) applies

Pass 3 activates iff either condition holds:

1. `brief.voice_reference` names a specific creator (any language — 糸井重里 / 岩崎俊一 / 眞木準 / 谷山雅計 / 仲畑貴志 / 許舜英 / 李欣頻 / 葉明桂 / or any named author with a matching `anchor-{slug}.md` in the library).

2. `voice_quadrant.primary` + `voice_quadrant.position` are set AND the brief requires register-signal-level voice lock (beyond 4-axis tuning). Signals: `tone_cue` contains register keywords, `message_thesis` is stance-loaded, or upstream skill annotates `register_lock_required: true`.

Otherwise Pass 3 is skipped; `tone_notes.register_signal_applied = null`.

**Cross-tradition transplant forbidden** — never force JP signatures onto ZH output (or vice versa), never force either onto Anglo output. `voice-and-tone.md §Anti-Patterns` + `voice-anchor-meta.md §Cross-Master Context` document the ban. Cross-language BORROWING allowed only when anchor frontmatter's `cross-reference-valid-for[target_lang] == STRONG` AND brief explicitly permits it.

**If lineage-language conflict detected** (e.g., `voice_reference: 糸井重里` but `output_language: zh-TW`) → emit `violation` envelope per `../../CLAUDE.md §Envelope Violation`; router routes to `copywriting-intake`.

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
  - `standards/voice-and-tone.md` — Tier 2 cross-framework voice SSOT. Ogilvy 1963/1983 Anglo long-copy canon + JP emotional-resonance tradition + 18F / Mailchimp 4-axis voice model + Mailchimp "one voice, multiple tones" + tone context-switching table.
  - `standards/voice-anchor-meta.md` — consolidated voice anchor metadata (schema + selection rubric + over-mimic fallback registry + verified lineage map + cross-reference registry + cross-cultural label rubric + drift corrections + cross-master context + axis extreme candidates). Consolidated in v1.13.0 from former meta-core + meta-detail + axis-extreme files.
  - `standards/{jp,zh,en}-q{1,2,3,4}-anchors.md` (12 files) — quadrant router index, landmark-organized (center / extreme / toward-Q{N}).
  - `standards/anchor-{slug}.md` (80+ files, all schema_version: 2.0) — per-creator v2 anchor bodies (Voice direction / Native critical read / Prose mechanics / Examples / Don't-over-mimic / Metadata).
- **Rubric (SHOULD gate)**:
  - `rubrics/voice-consistency-gate.md` — cross-stage / cross-candidate voice stability + tone contextual appropriateness + anchor fidelity. Runs AFTER tone tuning as the last voice-layer check before handing to Phase 7 ethics gates.

This skill does **not** own:

- Voice quadrant selection — `copywriting-voice-quadrant-stage` (Phase 5).
- Framework structure (PASONA stage ordering etc.) — Phase 4 workflow skills.
- Ethics / legal / ステマ — `copywriting-ethics-check-stage` (Phase 7).
- Form-appropriate character discipline — `copywriting-form-check-stage` (Phase 8).
- Library curation (4-condition rubric enforcement) — `scripts/lint-anchor-library.py` at CI time (v1.13.0+).

## Phase 6 Operating Model

Three sequential passes on the `draft`. Each pass returns either an edited draft or an annotation the next pass must honor. No pass may silently rewrite Phase 4's structural skeleton — frameworks are replaceable, voice is an irreplaceable asset, but structural edits belong to Phase 4 re-runs, not here.

### Pass 1 — 4-axis micro calibration (always runs)

Per `standards/voice-and-tone.md §Voice definition — 4 axes`:

| Axis | Left end | Right end |
|----|------|------|
| Formality | formal | casual |
| Seriousness | serious | funny |
| Respectfulness | respectful | irreverent |
| Enthusiasm | matter-of-fact | enthusiastic |

**Schwartz alignment passthrough**: `voice_quadrant` (including `schwartz_alignment`) passes through Phase 6 unchanged per `../../CLAUDE.md §Immutable fields`. If `schwartz_alignment == "conflict_flagged"`, Pass 1 MAY lightly soften axis defaults (e.g., keep enthusiasm matter-of-fact when L2 forced into Q2), but does NOT elaborate rationale — Phase 8 8b owns the rigorous consumer check.

Action:

1. Extract brand voice axis positions from `brief.voice_reference` + `voice_quadrant`. If absent, derive default from Phase 5 quadrant (Q1 ≈ formal / serious / respectful / matter-of-fact; Q3 ≈ casual / warm / respectful / warm-enthusiastic; etc.) and **disclose** the derivation in `tone_notes.axis_default_derived`.
2. **Self-check for axis drift**: lightly scan the draft for sentences whose axis reading obviously conflicts with the target vector by ≥2 steps. Rewrite the flagged sentences. The Voice Consistency SHOULD gate handles rigorous per-sentence enumeration; Pass 1 catches obvious drift.
3. Preserve framework stage boundaries (PASONA A / S / O labels, BEAF stages, etc.) verbatim.
4. Apply Ogilvy commandments explicitly: no empty-hype vocabulary (amazing / revolutionary / game-changing), headline voice = body voice (no click-bait exemption), long-copy must earn every body sentence.

### Pass 2 — tone context-switching (runs if the draft contains context-sensitive segments)

Per `standards/voice-and-tone.md §Tone context-switching table`:

| Context | Tone direction | Caution |
|------|------|------|
| Onboarding / Welcome | warm, encouraging | no bait-and-switch to hard sell |
| Error / Failure | calm, specific, non-deflecting | no humor masking |
| Crisis / Incident | serious, timely, transparent | no jokes, no hype, label uncertainty |
| Celebration / Launch | enthusiastic, user-grateful | user is subject, not brand |

**Voice stays constant; tone varies.** If brand voice is "playful," error-state remains playful in voice, but tone becomes calm and joke-free. Mailchimp-explicit rule (§voice-and-tone §Tone context-switching table).

For non-SaaS copy (product ads, long-form sales, キャッチコピー), the four contexts still map — e.g., PASONA's Affinity stage ≈ Onboarding tone; Offer stage ≈ Celebration tone (see `voice-and-tone.md §Integration with PASONA / BEAF / キャッチコピー frameworks`).

### Pass 3 — Voice Anchor Selection (runs only per §When Pass 3 applies)

**One linear 8-step flow.** v1.13.0 collapsed the former 4-branch dispatch (Pass 3a/3b/3c/3d) into a single flow — named creator, axis-extreme landmark, and register-signal routing all traverse the same steps; differences are candidate-pool filters or Step 2.3 priority, not separate control paths.

#### Step 1 — Load

```
load standards/voice-anchor-meta.md
load standards/{output_language}-q{voice_quadrant.primary}-anchors.md §Landmark: {position}
```

`{position}` ∈ {`center`, `extreme`, `toward-Q1`..`toward-Q4`, `axis-authority`, `axis-affinity`, `axis-reason`, `axis-emotion`}. Axis-extreme landmarks live in `voice-anchor-meta.md §Axis Extreme candidates` (cross-language section); per-quadrant router holds center / extreme / toward-Q{N} sections.

**Cross-lang opt-in**: additionally load `standards/{cross_ref_lang}-q{primary}-anchors.md §Landmark: {position}` ONLY when:
- Some candidate anchor's frontmatter has `cross-reference-valid-for[{output_language}] == STRONG`
- `brief.cross_lang_borrowing_allowed == true` (default false)

#### Step 2 — Candidate pool

Read all anchor entries in the Landmark section. Apply three filters in order:

**2.1 Automatic rejection** — exclude anchors matching `voice-anchor-meta.md §Automatic rejection`:
- Voice inseparable from ideological / traumatic content
- Biographical-tragic weight overpowers style on bare name
- Corpus LLM-latent-space illegible
- Register non-transferable to commercial frame
- Corpus THIN in target language

**2.2 Negation-of-axis** — if `brief.tone_cue` contains explicit axis negation (e.g. "not corporate", "not preachy"):
1. Forbid the negated axis; exclude candidates whose primary axis is negated
2. Record forbidden axis in `voice_quadrant.rationale` (carry-forward) for Phase 8 verification
3. If post-filter candidate pool is empty → emit `violation` envelope to intake requesting tone_cue clarification

**2.3 Named-creator forced rank 1** — if `brief.voice_reference` names a creator AND the corresponding `anchor-{slug}.md` is in the candidate pool:
- The named anchor is FORCED to rank 1 (primary). No override. User intent is authoritative.
- Agent still MUST evaluate fit relative to the brief. If `fit_score < MEDIUM-HIGH`, emit warning:

```json
tone_notes.register_signal_applied.named_master_fit_warning = {
  "slug": "...",
  "user_specified": true,
  "agent_fit_assessment": "MEDIUM | LOW",
  "mismatch_reasoning": "cite specific brief signals (thesis / target / scene / tone_cue tokens) — not generic prose",
  "proceeded_anyway": true
}
```

Warning is non-blocking. User intent executes; warning surfaces in envelope for user's next-turn review / substitution decision.

#### Step 3 — Fit judgment and ranking + confidence self-report

**Skipped if Step 2.3 forced rank 1**. Otherwise: agent ranks top-3 from remaining candidates, each emits `{rank, slug, fit_score, fit_reasoning}`:

- `fit_score` ∈ {`HIGH`, `MEDIUM-HIGH`, `MEDIUM`, `LOW`}
- `fit_reasoning` — must cite concrete brief signals (`message_thesis` clause, `target_audience` descriptor, scene keyword, tone_cue token). Generic prose ("matches quadrant") is unacceptable.

Rank 1 = primary.

**Step 3.5 — Self-report selection confidence** (v1.12.1 instrumentation, retained):

`agent_selection_confidence ∈ {HIGH, MEDIUM, LOW}`:
- `HIGH` — rank 1 明顯優於 rank 2;配對機制 (anchor mechanic × brief signal) 到位;無指名 master 誤配疑慮
- `MEDIUM` — rank 1 略優於 rank 2,或配對有疑慮 (payload 不足 / audience mismatch / register 略偏)
- `LOW` — 候選池整體弱 / 配對勉強 / 指名 master 疑似不合 brief / thesis

Non-blocking instrumentation; does NOT change routing. Used for data collection + downstream audit.

Library curation (`scripts/lint-anchor-library.py` at CI time) guarantees all candidates are baseline-eligible; runtime does NOT re-validate the legacy 4-condition rubric (Corpus-depth / Label-density / Commercial-register bridge / Over-mimic control) — moved to library-entry lint in v1.13.0.

#### Step 4 — Apply primary + mitigation inline

1. Read primary anchor's `§Prose mechanics` + `§Examples` as rewrite reference
2. Read primary anchor's `§Don't / Over-mimic §Mitigation` (≤15-word clause). Inject inline into rewrite prompt.
3. Rewrite `draft`, following anchor's mechanics
4. **Anchor autonomy on voice conflicts (v1.14.0)**: when anchor's `§Prose mechanics` or `§Don't` conflicts with `brief.form_hint` / `brief.tone_cue` / Phase 4 draft structure, **anchor wins** — mechanics are binding requirements, not suggestions. Do NOT override `brief.output_language` / `brief.audience` / `brief.product` / `brief.goal` (intake Level-1 fields, immutable). Example: `form_hint: "3 feature bullets"` vs anchor refusing feature enumeration → bullets subtracted and rewritten in anchor's native form.

**Mitigation fallback**: if primary references one of the 9 no-anchor-file authors (村上春樹 / 金庸 / 三島 / 莫言 / 太宰 / 余華 / Cormac McCarthy / DFW / James Ellroy) or the 3 movement/campaign entries (XR Declaration / Nike "Dream Crazy" / Luxury manifesto generic), read mitigation from `voice-anchor-meta.md §Over-mimic mitigation fallback registry`. All other cases: anchor file is the single source of truth.

#### Step 5 — Thesis-conflict self-check

After the rewrite but BEFORE emit, scan the polished draft:
- Does any span introduce a concept `envelope.message_thesis` explicitly negates?
- Does any span undermine the thesis assertion?

If conflict detected:
1. `revise_once`: rewrite the conflicting span while preserving anchor cadence / discipline
2. If revise-once still conflicts → `escalate` (Phase 8 Dimension 7 catches)

Record: `register_signal_applied.thesis_self_check ∈ {clear, revised_once, escalate}`.

#### Step 6 — Safe-substitute suggestion (conditional)

If `brief.voice_reference` names a specific creator, query:

```
substitute_candidates = [anchor for anchor in standards/anchor-*.md 
                         if named-creator ∈ anchor.frontmatter.safe_substitute_for]
```

**Qualifying rule**: candidate's over-mimic risk must be **strictly lower** than named creator's (ordering: `LOW < MEDIUM < MEDIUM-HIGH < HIGH < HIGH+`). Read named creator's risk from its own anchor frontmatter `Over-mimic risk:` line; fallback to `voice-anchor-meta.md §Over-mimic mitigation fallback registry`; default to `MEDIUM` if in neither.

If a qualifying candidate exists:
- Emit `substitute_suggested = {slug, rationale, strength: "suggested"}`
- **Contamination upgrade**: if `brief.tone_cue` contains tokens matching the substitute anchor's `§Don't / Failure mode` warning about named-creator contamination → upgrade to `strength: "strong"`. Signals to user that substitute isn't just safer but likely necessary.

Named creator remains default primary (Step 2.3 still holds). Substitute travels in envelope; user confirms switch in next turn.

#### Step 7 — Secondary anchor (opt-in, max 1)

Triggered by any of:
- (a) `brief` explicitly requests multi-anchor combination
- (b) Upstream skill annotates `envelope.secondary_anchor_requested = true`
- (c) Agent self-judges that primary anchor lacks a specific discipline / cadence AND a second anchor demonstrably fills the gap

If path (c), emit with `auto_triggered: true` flag for audit review:

```json
register_signal_applied.secondary_anchors[0] = {
  "slug": "...",
  "role": "secondary-discipline | secondary-cadence | cross-lang-borrowing",
  "rationale": "...",
  "auto_triggered": true
}
```

Hard constraints (unchanged):
- Max 1 secondary (no 3+ anchor pastiche composition)
- Cross-transplant ban still holds: JP signatures do not combine with ZH/EN anchors; same for ZH and EN

#### Step 8 — Output

```json
tone_notes.register_signal_applied = {
  "primary_anchor_slug": "...",
  "landmark_position": "center | extreme | toward-Q{N} | axis-{axis}",
  "named_master_forced_primary": true | false,
  "named_master_fit_warning": null | {
    "slug": "...",
    "user_specified": true,
    "agent_fit_assessment": "MEDIUM | LOW",
    "mismatch_reasoning": "...",
    "proceeded_anyway": true
  },
  "mitigation_clauses_applied": ["..."],
  "anchor_candidates_ranked": [
    {"rank": 1, "slug": "...", "fit_score": "HIGH | MEDIUM-HIGH | MEDIUM | LOW", "fit_reasoning": "..."}
  ],
  "substitute_suggested": null | {
    "slug": "...",
    "rationale": "...",
    "strength": "suggested | strong"
  },
  "secondary_anchors": [
    {
      "slug": "...",
      "role": "secondary-discipline | secondary-cadence | cross-lang-borrowing",
      "rationale": "...",
      "auto_triggered": true | false
    }
  ],
  "thesis_self_check": "clear | revised_once | escalate | not_applicable",
  "agent_selection_confidence": "HIGH | MEDIUM | LOW",
  "native_critical_vocab_cited": ["..."]
}
```

## Preconditions

Formal schema used by `using-copywriting-toolkit` router for bounce-back routing. On violation, router emits the bounce-back envelope defined in `../../CLAUDE.md §Envelope Violation`.

### Required envelope fields (Level 1 — BLOCKED if missing)

| Field | Type | Source | Notes |
|---|---|---|---|
| `phase` | enum | Phase 5 | must equal `phase-5-voice-positioned` |
| `voice_quadrant.primary` | enum Q1-Q4 | Phase 5 | required — macro quadrant before tactical tuning |
| `draft` | string | Phase 4 | non-empty |
| `form` | enum | intake | |
| `brief.output_language` | enum | intake | `ja` / `en` / `zh-TW` / etc. |

### Optional fields (activate extra passes)

| Field | Type | Notes |
|---|---|---|
| `brief.voice_reference` | string | names a creator → Pass 3 Step 2.3 forces rank 1 |
| `voice_quadrant.edge` | enum | Q2-Q3 / Q1-Q4 allowed edge positions |
| `voice_quadrant.position` | enum | center / extreme / toward-Q{N} / axis-{axis} — activates Pass 3 if non-null with register-lock signal |
| `message_thesis` | string | consumed by Pass 3 Step 5 thesis-conflict self-check |
| `brief.tone_cue` | string | activates Step 2.2 negation-of-axis + Step 6 contamination upgrade |
| `brief.cross_lang_borrowing_allowed` | bool | enables Step 1 cross-lang opt-in |

### Upstream bounce target on violation

- `voice_quadrant` missing → bounce to `copywriting-voice-quadrant-stage` (Phase 5 must run first)
- `draft` missing → bounce to `copywriting-<form>` (Phase 4 drafter)
- `brief.output_language` missing → bounce to `copywriting-intake` (Level 1 / 2 gap)

## Input Envelope (consumed)

Shape inherited from `copywriting-toolkit/CLAUDE.md §Handoff Envelope`, post-Phase 5:

```json
{
  "phase": "phase-5-voice-positioned",
  "form": "long-form-pasona | long-form-extended | mid-form | short-form | light-action | audit",
  "brief": { "voice_reference": "...", "output_language": "ja | en | zh-TW", "tone_cue": "...", "...": "..." },
  "message_thesis": "...",
  "voice_quadrant": {
    "primary": "Q1 | Q2 | Q3 | Q4",
    "edge": "Q2-Q3 | Q1-Q4 | null",
    "position": "center | extreme | toward-Q{N} | axis-{axis} | null",
    "rationale": "Phase 5 rationale",
    "schwartz_alignment": "ok | hard_rule_applied | conflict_flagged"
  },
  "draft": "the Phase 4 draft",
  "next_stage": "copywriting-voice-tone-stage"
}
```

Required keys: `voice_quadrant`, `draft`. Missing either → return to orchestrator with `status: upstream-incomplete` (Phase 5 must run first).

## Output Envelope (produced)

```json
{
  "phase": "phase-6-toned",
  "form": "long-form-pasona | ...",
  "brief": { "..." : "..." },
  "message_thesis": "...",
  "voice_quadrant": {
    "primary": "Q1 | Q2 | Q3 | Q4",
    "edge": "Q2-Q3 | Q1-Q4 | null",
    "position": "...",
    "rationale": "...",
    "schwartz_alignment": "ok | hard_rule_applied | conflict_flagged"
  },
  "draft": "the polished draft after 3 passes",
  "tone_notes": {
    "axis_target": { "formality": "casual", "seriousness": "serious", "respectfulness": "respectful", "enthusiasm": "warm" },
    "axis_default_derived": false,
    "tone_contexts_detected": ["onboarding", "celebration"],
    "tone_adjustments": [
      { "span": "sentence 3 of stage A", "context": "error", "before": "...", "after": "...", "rationale": "calm + non-deflecting" }
    ],
    "register_signal_applied": {
      "primary_anchor_slug": "...",
      "landmark_position": "center | extreme | toward-Q{N} | axis-{axis} | null",
      "named_master_forced_primary": true | false,
      "named_master_fit_warning": null,
      "mitigation_clauses_applied": ["..."],
      "anchor_candidates_ranked": [{"rank": 1, "slug": "...", "fit_score": "HIGH", "fit_reasoning": "..."}],
      "substitute_suggested": null,
      "secondary_anchors": [],
      "thesis_self_check": "clear | revised_once | escalate | not_applicable",
      "agent_selection_confidence": "HIGH | MEDIUM | LOW",
      "native_critical_vocab_cited": ["..."]
    },
    "ogilvy_flags": ["removed 'revolutionary' empty-hype token in stage S"]
  },
  "gate_verdict": "PASS | PASS_WITH_NOTES | NEEDS_REVISION",
  "gate_report": { "...see rubric §Output Format..." },
  "next_stage": "copywriting-ethics-check-stage"
}
```

**Breaking changes from v1.12.x → v1.13.0**:

Three `tone_notes` top-level fields are REMOVED and their semantics merged into `register_signal_applied`:

- `tone_notes.lineage_applied` → `register_signal_applied.primary_anchor_slug`
- `tone_notes.lineage_gap` → `register_signal_applied.named_master_fit_warning` (richer structured warning)
- `tone_notes.axis_extreme_applied` → `register_signal_applied.landmark_position` (axis landmarks flow through uniformly)

Downstream Phase 7/8 evaluators that read the old field paths must migrate. See `rubrics/voice-consistency-gate.md` for the updated Dimension 6 / Dimension 7 read paths.

Downstream (`copywriting-ethics-check-stage`) reads `draft` + `tone_notes` + `brief`. `tone_notes.ogilvy_flags` can surface 景品表示法 / FTC-relevant removals for Phase 7 cross-check.

## Gate — SHOULD (Voice Consistency)

- **Rubric**: `rubrics/voice-consistency-gate.md`
- **Agent**: `copywriting-toolkit/agents/copywriter-evaluator.md`
- **Trigger**: multi-stage OR multi-candidate artifact (PASONA 6 stages, BEAF 4 stages, ideation N candidates, or a series). Per the rubric's §Scope Boundary: single-stage / single short-form only → gate is skipped with `reason: cross-stage evaluation not possible` recorded in the envelope.
- **Position**: runs AFTER all 3 passes, as the last voice-layer check before Phase 7 legal gates pick up the artifact.
- **Dimensions** (per rubric): brand voice stability, tone contextual appropriateness, anchor style fidelity (if Pass 3 ran), JP emotional-resonance vs Anglo benefit-clear fit, voice quadrant coherence, over-mimic adherence (scoped to Pass 3), and **thesis alignment** (scoped to Pass 3 — catches anchor-induced drift from `envelope.message_thesis`).

Verdict handling:

- `PASS` → emit envelope; `next_stage: copywriting-ethics-check-stage`.
- `PASS_WITH_NOTES` (≤2 WARNINGS, no FATAL) → apply named fixes in one auto-revise round, re-run gate; if still `PASS_WITH_NOTES`, emit with notes disclosed (handoff-format §Section 3 max-2-rounds rule).
- `NEEDS_REVISION` (any FATAL or ≥3 WARNINGS) → BLOCKED. Return to the specific pass the rubric's `next_action` names. Do not forward to Phase 7.

## Anti-Patterns

- Rewriting framework stage structure during voice tuning. PASONA A / S / O boundaries are not Phase 6's territory.
- Swapping voice mid-artifact to match tone context ("error → serious voice"). `voice-and-tone.md §Anti-Patterns`: voice stays constant, only tone shifts.
- Transplanting signature mechanics across traditions (JP ↔ ZH ↔ EN). Cross-transplant ban is absolute; cross-language BORROWING (via STRONG cross-reference + brief opt-in) is the only permitted cross-tradition path.
- Re-running Step 2 `voice-anchor-meta.md` 4-condition validation at runtime. Library curation (`scripts/lint-anchor-library.py`) owns baseline eligibility; runtime trusts the library.
- Overriding Step 2.3 named-creator forced rank 1. User intent is authoritative; agent emits `named_master_fit_warning` but does NOT reassign primary.
- Filling the Voice Guide axes abstractly ("friendly, professional") with no side-by-side on-brand / off-brand examples (`voice-and-tone.md §Brand Voice Guide checklist`).
- Headline breaks voice for attention, then body "returns" — trust already lost at headline layer.
- Swallowing a `NEEDS_REVISION` gate verdict and forwarding to Phase 7.

**Drift callouts** (attribution corrections for 『24時間戦えますか？』NOT 岩崎, 「我不在咖啡館」is Altenberg sinicized NOT 葉明桂, 中興百貨 content-farm source discipline, etc.) are inlined in the corresponding anchor file's `§Don't / Over-mimic §Metadata` block; authoritative drift index lives at `voice-anchor-meta.md §Drift corrections catalog`.

## Files

- `standards/voice-and-tone.md` — Tier 2 cross-framework voice SSOT (third-party framework text byte-identical to `domain-teams:copywriting-team`; Brand Corpus curation Tier 2 per `CLAUDE.md §Provenance`).
- `standards/voice-anchor-meta.md` — consolidated voice anchor metadata (schema + selection rubric + over-mimic fallback + lineage map + cross-ref + cross-cultural label rubric + drift corrections + cross-master context + axis extreme candidates). New in v1.13.0 (supersedes split meta-core + meta-detail + axis-extreme).
- `standards/{jp,zh,en}-q{1,2,3,4}-anchors.md` — 12 quadrant router files (landmark-organized).
- `standards/anchor-{slug}.md` — 80+ per-creator v2 anchor body files. Library curation enforced by `scripts/lint-anchor-library.py` at CI time.
- `rubrics/voice-consistency-gate.md` — SHOULD gate rubric (scope boundary + dimensions + verdict thresholds).
