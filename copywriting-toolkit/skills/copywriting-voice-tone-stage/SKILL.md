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

### When lineage craft applies (Pass 3, v1.9.0)

Pass 3 triggers per the 4-branch dispatch (§Pass 3 activation guard). Post-v1.7.0, **Pass 3a/3b load per-master `anchor-{slug}.md` files directly** (via JP_CRAFT_MASTER_MAP / ZH_CRAFT_MASTER_MAP) — no wholesale craft-lineage load.

**JP craft-gate (Pass 3a)** — activates when:

1. `brief.voice_reference` ∈ {糸井重里, 岩崎俊一, 眞木準, 谷山雅計, 仲畑貴志}, OR
2. `brief.output_language == "ja"` AND Q3 state-proposal / 余韻 register is declared (routes through Pass 3d to JP Q3 quadrant router; returns to craft-gate if master identified)

**ZH craft-gate (Pass 3b)** — activates when:

1. `brief.voice_reference` ∈ {許舜英, 李欣頻, 葉明桂}, OR
2. `brief.output_language` is `zh-TW` or `zh-HK` AND Q2-maestro voice declared (routes through Pass 3d register-signal)

Note: `voice_quadrant` is the object emitted by Phase 5 (`{primary, edge, rationale, schwartz_alignment}`) — always dereference `.primary`, never read as string.

**Non-craft-gate Pass 3 paths**: Pass 3c (axis-extreme), Pass 3d (register-signal via quadrant router) — see §Pass 3 activation guard below for full dispatch logic.

**Cross-tradition transplant forbidden** — never force JP lineage onto ZH output (or vice versa), never force either onto Anglo output. `voice-and-tone.md §Anti-Patterns` + `voice-anchor-meta-detail.md §Cross-Master Context` document the ban.

**If both lineage triggers match** (e.g., `voice_reference: 糸井重里` but `output_language: zh-TW`) → emit `violation` envelope per `../../CLAUDE.md §Envelope Violation`; router routes to `copywriting-intake`. Do NOT self-dispatch bounce (fragments `bounce_round` counter).

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
  - `standards/anchor-jp-{itoi-shigesato,iwasaki-shunichi,maki-jun,taniyama-masakazu}-*.md` (v1.9.0) — per-master v2 Layer 1 voice bodies for 糸井 / 岩崎 / 眞木 / 谷山 (Pass 3a craft-gate). Replace the former `voice-anchor-meta-detail.md §Cross-Master Context (JP)` Tier 3 deep-dive; cross-master content absorbed into `voice-anchor-meta-detail.md §Cross-Master Context`.
  - `standards/anchor-zh-tw-{xu-shunying,lee-hsin-ping,ye-mingui}-*.md` (v1.9.0) — per-master v2 Layer 1 voice bodies for 許舜英 / 李欣頻 / 葉明桂 (Pass 3b craft-gate). Replace the former `voice-anchor-meta-detail.md §Cross-Master Context (ZH)` Tier 3 deep-dive; Z1-Z8 attribution corrections absorbed into `voice-anchor-meta-detail.md §Cross-Master Context` + inlined per-anchor Metadata (Z1 → 葉明桂; Z2 → 李欣頻; Z3/Z4 → 許舜英; Z5/Z7 → 吳念真; Z8 → 龔大中).
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

    # Tier 1 — Craft Gate (v1.7.0: load per-master v2 anchor as primary,
    #                      craft-lineage only for attribution corrections / lineage context)
    if voice_reference ∈ {糸井重里, 岩崎俊一, 眞木準, 谷山雅計, 仲畑貴志}:
        master_slug = JP_CRAFT_MASTER_MAP[voice_reference]
        load standards/anchor-jp-{master_slug}.md   # v2 Layer 1 voice body (PRIMARY)
        load standards/voice-anchor-meta-core.md    # over-mimic mitigation registry
        # Conditional: if brief needs cross-master context / era / attribution risk
        # → load standards/voice-anchor-meta-detail.md §Cross-Master Context (section-targeted)
        proceed to Pass 3a

    elif voice_reference ∈ {許舜英, 李欣頻, 葉明桂}:
        master_slug = ZH_CRAFT_MASTER_MAP[voice_reference]
        load standards/anchor-zh-tw-{master_slug}.md   # v2 Layer 1 voice body (PRIMARY)
        load standards/voice-anchor-meta-core.md
        # Conditional: attribution corrections (Z1-Z8) / cross-master lineage / 意識形態 era
        # → load standards/voice-anchor-meta-detail.md §Cross-Master Context
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

**Craft-gate master → anchor file mapping** (v1.7.0):

```
JP_CRAFT_MASTER_MAP = {
  糸井重里: itoi-shigesato-state-proposal,
  岩崎俊一: iwasaki-shunichi-yonin,
  眞木準: maki-jun-craft-aphorism,
  谷山雅計: taniyama-masakazu-discipline,
  仲畑貴志: nakahata-takashi-kougo-chokugen,  # v1.12.0 — 5th master, TCC 殿堂 2015
}

ZH_CRAFT_MASTER_MAP = {
  許舜英: xu-shunying-ideological-definitional,
  李欣頻: lee-hsin-ping-literary-consumption,
  葉明桂: ye-mingui-strategic-aphorism,
}
```

**If no branch condition is TRUE → Pass 3 MUST NOT load any standards.** Record the null annotations and skip. Do NOT load "just in case".

**Rationale** (v1.2.0 §Verification Density Principle + v1.3.2 optimization 1-4 + v1.7.0 craft-gate v2 alignment):
- v1.2.0 preserved craft-gate gate (6 masters); lineage standards 700 lines / 8-10K tokens load only when craft master cited
- v1.3.2 adds register-signal + axis-extreme branches with **landmark-targeted section read** (~1.5K per section) and **meta-core vs meta-detail split** (core ~2K always when Pass 3 triggers; detail ~3K only when Register Signal)
- v1.7.0 Pass 3a/3b shift to **per-master v2 anchor load** (~1.2K per anchor body) as primary, with `{jp,zh}-copy-craft-lineage.md` becoming **conditional-only** load (cross-master lineage / attribution corrections / era context). Eliminates the 7 orphan craft-gate anchor-*.md files + saves ~5K per craft-gate trigger (from 8-10K wholesale craft-lineage load to 1.2K focused anchor body).
- Net: Pass 3 per-trigger weighted cost ~3-5K (craft-gate path); ~5-7K (register-signal path)

**If predicate is TRUE → proceed to Pass 3a / 3b / 3c / 3d as applicable**.

#### Pass 3a — JP lineage (JP trigger matched, v1.7.0 per-master v2 load)

Load the master-specific v2 anchor file (from JP_CRAFT_MASTER_MAP above).
Each anchor carries the full v2 schema (Voice direction / Native critical
read / Prose mechanics / Examples / Don't / Metadata) tailored to that
master:

- **糸井重里** → `standards/anchor-jp-itoi-shigesato-state-proposal.md` —
  state-proposal grammar (「おいしい生活。」), non-imperative 句読点
  discipline, 平仮名 over-index, 体言止め ending preference.
- **岩崎俊一** → `standards/anchor-jp-iwasaki-shunichi-yonin.md` — 余韻
  / 無常 compound (「やがて、いのちに変わるもの。」), Buddhist
  finiteness undertone, rejects direct CTA.
- **眞木準** → `standards/anchor-jp-maki-jun-craft-aphorism.md` — Q2↔Q3
  border, 諧謔 + 知性 blend (see `voice-and-tone.md §JP emotional-
  resonance tradition` cross-link).
- **谷山雅計** → `standards/anchor-jp-taniyama-masakazu-discipline.md`
  — discipline-centric (3-reason test per candidate + compressive
  restraint).

**Conditional load of `voice-anchor-meta-detail.md §Cross-Master Context`** (v1.9.2 trigger simplified) — load ONLY when:
1. Brief explicitly requires cross-master lineage / historical era / critical debate context (genuinely cross-master)
2. Draft involves multiple JP masters side-by-side comparison

Default: do NOT load meta-detail. v2 anchor body carries sufficient voice signature + per-master `Don't` block + inline drift #JP-8 correction for standalone rewrite. v1.9.2 note: attribution-risk no longer auto-triggers meta-detail — all JP drift corrections are inlined in the corresponding anchor's Metadata.

**Critical attribution corrections (JP)** — drift #JP-8 (リゲイン「24時間戦えますか？」NOT 岩崎) inlined in `anchor-jp-iwasaki-shunichi-yonin.md §Don't / Over-mimic` + Metadata footer. Authoritative drift index in `voice-anchor-meta-detail.md §Drift corrections catalog`.

#### Pass 3b — ZH lineage (ZH trigger matched, v1.7.0 per-master v2 load)

Load the master-specific v2 anchor file (from ZH_CRAFT_MASTER_MAP above):

- **許舜英** → `standards/anchor-zh-tw-xu-shunying-ideological-definitional.md`
  — definitional inversion (「服裝就是一種高明的政治」), cross-domain
  vocabulary transplant (政治 / 姿態 / 命題 / 邏輯), cultural-critique
  payload density, paradox-as-hook ("不是 X, 是 Y"). 意識形態廣告 中興
  百貨 1988-1999 canon.
- **李欣頻** → `standards/anchor-zh-tw-lee-hsin-ping-literary-consumption.md`
  — 書店 / 閱讀 philosophical prose (「閱讀是唯一的迷信」), existential-
  aphorism register, 誠品敦南 1990s-2000s canon. Voice is Q2 tipping
  into Q2-Q3 edge (warmer than 許舜英's cool-aesthetic).
- **葉明桂** → `standards/anchor-zh-tw-ye-mingui-strategic-aphorism.md`
  — brand-personality mapping via systematic strategic frameworks.
  左岸咖啡館 1998- canon. Voice is Q2-Q3 edge (authority framing via
  warmth). Distinguished from 許舜英's cool manifesto register by
  brand-construction thesis (「不是賣咖啡，是經營咖啡館」).

**Conditional load of `voice-anchor-meta-detail.md §Cross-Master Context`** (v1.9.2 trigger simplified) — load ONLY when:
1. Brief cites cross-master comparison (許舜英 vs 李欣頻 register differentiation)
2. Brief references 意識形態 廣告 institutional-era context (1987-1999 decade) — Generational Context section
3. Brief references **孫大偉** (only ZH drift without an anchor home — Z6 lives in meta-detail)

Default: do NOT load meta-detail. Per-anchor `Don't` block + anchor Metadata carry inlined Z1 (葉明桂 anchor) + Z2 (李欣頻 anchor) + Z3/Z4/Z11 (許舜英 anchor) + Z5/Z7 (吳念真 anchor) + Z8/Z10 (龔大中 anchor + zh-q3 router) + Z9 (KC Tsang anchor). v1.9.2 note: attribution-risk triggers no longer need meta-detail unless Z6-specific.

**Critical attribution corrections (ZH)** — authoritative drift index in `voice-anchor-meta-detail.md §Drift corrections catalog`. Per-anchor inlines are SSOT. Exception: Z6 (孫大偉 agency = 奧美 → 偉太, NOT JWT) has no anchor home; lives in meta-detail Z6 section.

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
1. Read per-quadrant Landmark section — extract anchor entries + metadata. **Schema auto-detect (v1.5.0)**: inspect anchor file frontmatter. If `schema_version: 2.0`, extract Layer 1 v2 fields (Voice direction / Native critical read / Prose mechanics / Examples / Don't / Metadata) per `voice-anchor-meta-core.md §v2 schema`. Otherwise extract v1 fields (Era / Representative lines / Voice signature / LLM corpus depth / Over-mimic risk) per `voice-anchor-meta-core.md §v1 schema`. Both schemas coexist during migration window. Additional v2 entries live in `docs/voice-anchor-deep-dives/pilot-layer1-v2-*.md` — consult `docs/voice-library-recast-audit.md` for the mapping from v1 brand/campaign entries to v2 individual-creator recasts.
2. For each candidate anchor, verify anchor selection rubric (meta-core 4 conditions). For v2 entries, the over-mimic mitigation clause is in the anchor's own `Don't / Over-mimic` block (single source of truth). For v1 entries, consult meta-core's §Over-mimic mitigation registry.
3. **Rank top-3 candidates** by fit — emit `anchor_candidates_ranked` list (v1.3.5); then apply the primary (rank 1) voice signature to draft rewrite
4. **Thesis-conflict self-check** (v1.3.5): after the rewrite but BEFORE emit, scan the polished draft for spans that reintroduce a concept `envelope.message_thesis` explicitly negates, or undermine its assertion. If detected, revise the draft dropping the conflicting imagery (keep the anchor's cadence / discipline). Record the self-check outcome in `tone_notes.register_signal_applied.thesis_self_check` as `clear` / `revised_once` / `escalate` (escalate when revise-once still conflicts — downstream Dimension 7 will catch).
5. **Secondary anchor application** (v1.10.0): if a brief's register benefits from combining a primary register anchor + a supplementary discipline anchor (e.g. Fried+DHH antithesis primary + Stratechery "earn every declarative" discipline secondary), emit secondary anchors in the `secondary_anchors[]` array with `role` label. Common roles: `"secondary-discipline"` (borrow sentence-level rule only), `"secondary-cadence"` (borrow rhythm only), `"cross-lang-borrowing"` (borrow structure across language without vocabulary). Max 1 secondary per rewrite — 3+ anchors compose as pastiche.
6. **Safe-substitute suggestion** (v1.10.0, broadened v1.11.1): when `brief.voice_reference` names ANY master, query `{anchor for anchor where named-master ∈ anchor.frontmatter.safe_substitute_for}`. If a candidate exists AND its over-mimic risk is **strictly lower** than the named master's (LOW < MEDIUM < MEDIUM-HIGH < HIGH < HIGH+), emit `substitute_suggested = {slug, rationale}`. Read named-master risk from its own anchor file's `Over-mimic risk:` line first; fallback to meta-core §Over-mimic mitigation registry; default to MEDIUM if in neither. User-specified master remains default primary unless user confirms substitute in follow-up turn. **v1.11.1 contamination upgrade**: if `brief.tone_cue` contains tokens matching the substitute anchor's `Don't / Failure mode` warning about named-master contamination (e.g., tone_cue "華麗頹廢" matches 白先勇's anchor's warning about 張愛玲-style "華麗頹廢"), upgrade to `substitute_recommended_strong` — substitute isn't just safer but likely necessary.
7. Record `tone_notes.register_signal_applied = {primary_anchor_slug, secondary_anchors[], landmark_position, mitigation_clauses_applied, anchor_candidates_ranked[], substitute_suggested?, thesis_self_check}`

**v1.10.0 output schema** (register_signal_applied):
```json
{
  "primary_anchor_slug": "en-basecamp-fried-dhh-contrarian-manifesto",
  "landmark_position": "toward-Q1",
  "secondary_anchors": [
    {"slug": "en-stratechery-peer-analytical", "role": "secondary-discipline", "rationale": "apply 'earn every declarative' to technical claims"}
  ],
  "mitigation_clauses_applied": ["name the exact received wisdom being punctured; claim must survive without the contrarian frame"],
  "anchor_candidates_ranked": [
    {"rank": 1, "slug": "en-basecamp-fried-dhh-contrarian-manifesto", "fit_score": "HIGH", "fit_reasoning": "peer-to-peer developer register; antithesis matches 'deploy without anxiety' thesis"},
    {"rank": 2, "slug": "en-stratechery-peer-analytical", "fit_score": "MEDIUM-HIGH", "fit_reasoning": "analyst register skews essayistic for 3-paragraph landing hero"},
    {"rank": 3, "slug": "en-bernbach-ddb-confession-plain-style", "fit_score": "MEDIUM", "fit_reasoning": "historically Q1-anchored; VW-Think-Small less native to backend-eng audience"}
  ],
  "substitute_suggested": null,
  "thesis_self_check": "clear | revised_once | escalate",
  "native_critical_vocab_cited": ["peer-to-peer", "antithesis-headline", "earn every declarative"]
}
```

Emitting ranked candidates + optional secondary anchors surfaces Pass 3's interpretation space for downstream review and regression auditing — the same brief across runs may legitimately select different primaries, but the candidate set should be stable.

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
    "register_signal_applied": {
      "primary_anchor_slug": "zh-tw-wu-nien-jen-taiyu-peer-intimate | null",
      "landmark_position": "center | extreme | toward-Q{N} | null",
      "mitigation_clauses_applied": ["..."],
      "anchor_candidates_ranked": [{"rank": 1, "slug": "...", "fit_score": "HIGH", "fit_reasoning": "..."}],
      "thesis_self_check": "clear | revised_once | escalate | not_applicable",
      "native_critical_vocab_cited": ["..."]
    },
    "axis_extreme_applied": "mvp-stub-{position} | null",
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
  voice-anchor-meta-detail.md §Cross-Master Context).
- Attributing 「我不在咖啡館...」as original 葉明桂 line (actually Peter
  Altenberg sinicized — voice-anchor-meta-detail.md §Cross-Master Context drift #Z1).
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
- `standards/voice-anchor-meta-detail.md §Cross-Master Context` — Tier 3 JP lineage deep-dive
  (verbatim copy from `domain-teams:copywriting-team`).
- `standards/voice-anchor-meta-detail.md §Cross-Master Context` — Tier 3 ZH lineage deep-dive
  (NEW in v1.0.0; primary-source-researched; not cp'd from
  `domain-teams:copywriting-team`).
- `rubrics/voice-consistency-gate.md` — SHOULD gate rubric (verbatim copy).
