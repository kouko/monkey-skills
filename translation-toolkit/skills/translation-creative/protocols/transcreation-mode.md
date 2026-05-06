# Transcreation mode — protocol

> Transcreation is **re-creation in the target culture for the same
> persuasive intent**. Surface deviation is expected and desirable; the
> WRITER is licensed to swap puns, substitute cultural anchors, restructure
> sentence rhythm, and choose locale-equivalent metaphors.
>
> This protocol owns the mode-entry contract, the 5th Effectiveness axis,
> the `--variants=N` differentiation rule, the S1 MUST behavior, and the
> M2 glossary-leeway rule.

Defined in `references/orthogonal-axes.md` and `references/5d-effectiveness.md`;
this protocol is the operational glue.

---

## When to enter transcreation mode

The mode field on the intake-spec is the single load-bearing input. Three
entry paths:

1. **Explicit user choice** — intake-spec carries `mode: transcreation`
   either because the user typed it during explicit intake, or because
   `translation-intake` inferred it from a strong signal (user said "ad
   copy", "headline", "tagline", "catchphrase", "campaign", "transcreate").
2. **Genre-driven default** — when the input shape is ad copy / headline /
   tagline / brand voice content and the user did not specify mode,
   `translation-intake` defaults to `transcreation`. Marketing **briefs**
   (long-form prose describing a campaign) default to `faithful` because
   the brief itself is reference material — the persuasive copy lives in
   downstream artifacts.
3. **Mode override at invocation** — user can pass `--mode=transcreation`
   on a `translation-creative` invocation to override the spec. The
   override is recorded in the audit-trail so downstream review can see
   the resolved mode + its source.

If mode is `faithful`, this protocol is mostly inactive: 4D REFLECT runs
(no Effectiveness), S1 stays SHOULD, M2 stays strict, variants are still
available but use a less aggressive differentiation prompt. The rest of
this document describes what changes when mode = transcreation.

---

## What changes when mode = transcreation

### Change 1 — REFLECT becomes 5D

The Effectiveness axis is added per `references/prompt-reflect-5d.md` and
`references/5d-effectiveness.md`. The CRITIC produces a 5-axis JSON:
4D + `effectiveness: [...]`. Empty array on a chunk = "no effectiveness
concerns". The REVISER consumes the 5-axis critique on IMPROVE.

**Concerns the Effectiveness axis catches** (canonical list per
`references/5d-effectiveness.md`):

- Cultural-reference fail (pun / idiom / allusion / meme lost without
  local replacement)
- CTA strength dilution (verb intensity downgraded)
- Emotional pull mismatch (excitement / fear / aspiration / nostalgia
  flattened or shifted)
- Target-culture taboo violation (unlucky numbers, color associations,
  homophones)
- Brand-voice drift (warm brand sounding cold in target, or vice versa)
- Anchor-figure / reference substitution missed (Steve Jobs quote where
  a target-locale authority anchor would carry the load-bearing weight)
- Genre-convention mismatch (en-US punchy headlines verbatim into JP
  where 7-15 char convention applies)
- Phonetic / rhythm element lost (alliteration, syllable counts, brand
  rhythm)
- Number / claim hedging shift ("save 50%" vs 「半額」 vs 「五折」)

### Change 2 — S1 promoted from SHOULD to MUST

Back-translation gate behavior in transcreation:

- **Threshold**: 0.70 cosine similarity (relaxed from faithful's 0.85,
  per `references/verification-gates.md` §S1).
- **Tier**: MUST (promoted from SHOULD). A v2 with similarity below 0.70
  is a **FAIL** — not a WARN. The output is **blocked**; the run does not
  emit until the v2 either crosses the threshold or the user escalates
  to manual review.
- **Why MUST**: when surface deviation is licensed, M1 (placeholder
  parity) and S2 (register) are insufficient guards against outright
  topic drift. S1 is the only gate that catches "the v2 is well-written
  copy about a different product / promise / audience". Without S1 MUST,
  transcreation could silently produce coherent-but-wrong copy.
- **Resolution path on FAIL**:
  1. Run REFLECT again with critique focus on the drift dimensions
     identified by S1 (similarity report includes the lowest-overlap
     spans).
  2. Run IMPROVE again to emit v3.
  3. Re-run S1 on v3.
  4. If v3 still fails, halt and surface to the caller with the audit
     trail. The fix path is human review, NOT flipping S1 off.
- **Bypass**: there is no `--bypass-gates` flag (anti-pattern per spec
  Decision #15). The MUST is hard.

### Change 3 — M2 glossary leeway

In transcreation mode, M2 (project glossary compliance) gains a narrow
exception path:

- **Default M2 behavior unchanged**: every L1-mandated source term must
  render as its mapped target form. A missing glossary term in v2 is
  still M2 FAIL.
- **Transcreation exception**: if the WRITER's chosen rendering deviates
  from the L1 mapping AND the deviation enables a **culturally
  equivalent** translation that the literal mapping would have killed,
  the deviation is **acceptable but auditable**.

  Example: glossary maps "freedom" → 「自由」. In a campaign for an
  outdoor brand targeting JP, the literal 「自由」 reads abstract /
  political; transcreation might choose 「解き放たれる感覚」 ("the
  sensation of being unleashed") which captures the brand's intent
  better. M2 records the deviation with rationale, but does not block.

- **What audit trail records** (mandatory when this exception fires):
  - The L1 source term
  - The L1 mapped target form
  - The actual rendering chosen
  - The Effectiveness-axis rationale (which Effectiveness concern the
    deviation addresses)
  - A `glossary_leeway: true` flag on the M2 entry

- **What this exception does NOT cover**:
  - **Brand-name handling** is L1 strict — no leeway. Brand-name
    deviations are M2 FAIL even in transcreation. (Brand-name decisions
    are part of the brand brief; if the brief says preserve verbatim,
    the WRITER preserves verbatim.)
  - **Legally-mandated terminology** (regulatory disclosures, drug
    names, financial terms) is L1 strict — no leeway. The intake-spec
    `domain` field signals when this applies.
  - **`PASS_ADVISORY` notes already give context-dependent leeway** for
    flagged terms — this transcreation exception is for terms NOT
    flagged advisory (i.e., normally strict L1 terms).

### Change 4 — Brand brief becomes recommended

`protocols/brand-brief-intake.md` is **optional in faithful** but
**recommended in transcreation**. A missing brief in transcreation surfaces
a WARN (does not block; the WRITER falls back to intake-spec `register` +
`intent` + `domain` fields, but the Effectiveness axis lacks brand-voice
ground truth and tends to be conservative).

### Change 5 — Variant differentiation prompt becomes aggressive

When `--variants=N` is set in transcreation mode, the WRITER prompt for
each variant is instructed to differ on a tactical axis (see "How variants
differ" below). In faithful mode, variants exist but differ less
aggressively (mostly on phrasing rhythm), because the licensed deviation
budget is smaller.

---

## How variants differ (the differentiation rule)

When `--variants=N` is requested, each variant is a **full, independent
DRAFT → REFLECT → IMPROVE run**. The WRITER prompt for each variant is
instructed to differ from sibling variants on a specific tactical axis,
NOT to paraphrase a shared draft. The differentiation axes (the WRITER
picks one per variant; the audit trail records the chosen axis):

1. **Structure-preserving** — keep source sentence structure, swap only
   surface lexicon. Conservative variant; closest to source rhythm.
2. **Rhythm-restructuring** — restructure for natural target rhythm.
   Sentence boundaries move; pacing shifts to target-language convention
   (e.g., en-US punchy headlines → JP 7-15 char form).
3. **Metaphor-substitution** — replace source metaphor with a target-
   culture-equivalent metaphor. Surface diverges most here; intent
   preserved by the metaphor's persuasive payload, not its literal
   content.
4. **Anchor-substitution** — when source uses a culture anchor (e.g.,
   a celebrity / framework / event reference), substitute with the
   target-locale anchor that carries equivalent authority weight.
5. **Genre-convention pivot** — restructure to match target marketing
   genre conventions (e.g., en-US single-CTA → JP multi-CTA + testimonial
   block).

Constraints on the differentiation:

- Variants must be **strategically different**, not synonym swaps. A
  variant set where v1 says "Don't waste time" and v2 says "Stop wasting
  time" violates this rule — both are structure-preserving with surface
  paraphrase. Audit trail flags this as `variant_differentiation: WARN`.
- Each variant must independently pass M1 / M2 / S2.
- Each variant must pass S1 (MUST in transcreation). A variant that
  fails S1 is **dropped** from the emitted set. If all `N` variants
  fail S1, the run halts.
- The first variant emitted is conventionally structure-preserving
  (the "safest" option) so downstream review has a stable anchor; the
  remaining variants escalate in deviation budget.

---

## Worked example — en-US → ja-JP transcreation with N=3 variants

**Source** (en-US, source mode = transcreation, brand brief = Patagonia-
style outdoor):

> Stop wasting time. Get organized in 5 minutes. Try Notion free.

(This source is from `references/5d-effectiveness.md` §"Concrete example"
— reused here to show how the differentiation rule lands.)

**Variant 1 — Structure-preserving**:

> 時間を、無駄にしない。5分で、すべてが整う。Notion を、無料で始めよう。

Preserves three-sentence structure + imperative form + CTA position.
Lower deviation; closest to source rhythm.

**Variant 2 — Rhythm-restructuring**:

> もう、時間に追われない。
> Notion なら、5分で仕事が整う。
> いますぐ無料で始める。

Restructures opening as pain-statement (JP DR convention) instead of
imperative. Mid-line shifts to brand-named claim. CTA imperative form
preserved but reframed. (Matches `references/5d-effectiveness.md`'s
v2-after-IMPROVE example.)

**Variant 3 — Metaphor-substitution**:

> 「時間がない」は、もう、言わない。
> Notion で、5分の魔法。
> 30秒で、無料登録。

Substitutes "wasting time" with "stop saying 'no time'" (cultural-meme-
aware reframe). Substitutes "get organized" with 「魔法」 (magic) — a
JP marketing-copy convention for productivity tools. CTA tightened to
30秒 specificity (JP DR convention favors numerical specificity).

All three pass S1 in transcreation (similarity ≥ 0.70 because the
persuasive intent — productivity, time saving, free trial — is preserved
across all three despite the surface divergence).

---

## What this protocol does NOT cover

- **Faithful mode behavior** — described in SKILL.md; this protocol
  describes only the transcreation deltas.
- **The Effectiveness axis content itself** — that lives in
  `references/5d-effectiveness.md`. This protocol describes when the
  axis applies; the axis defines its own concerns + output format.
- **S1 algorithm** — that lives in `references/verification-gates.md`
  §S1. This protocol owns only the SHOULD → MUST tier flip and its
  resolution path.
- **M2 algorithm** — same: lives in `references/verification-gates.md`
  §M2. This protocol owns only the glossary-leeway exception in
  transcreation mode.
- **Brand brief field semantics** — lives in
  `protocols/brand-brief-intake.md`. This protocol notes only that the
  brief is **recommended** in transcreation (vs optional in faithful).

---

## See also

- `../SKILL.md` — invokes this protocol when mode = transcreation
- `../references/orthogonal-axes.md` — mode field definition + intake
  defaults
- `../references/5d-effectiveness.md` — full Effectiveness axis spec
- `../references/prompt-reflect-5d.md` — 5D CRITIC prompt template
- `../references/verification-gates.md` §S1 + §M2 — gate algorithms
  this protocol modifies
- `protocols/brand-brief-intake.md` — brand brief capture template
  (recommended at mode-entry boundary)
- `checklists/creative-checklist.md` — items 1, 2, 5 specifically
  verify transcreation deltas
