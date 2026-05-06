---
name: translation-creative
description: Translate ad copy / marketing brief / headline / catchphrase via faithful or transcreation mode. 5D reflection in transcreation. S1 back-translation = MUST in transcreation, SHOULD in faithful. Variants opt-in via --variants=N.
version: 0.1.0
---

# translation-creative

Layer 2-5 owner for **ad copy / marketing brief / headline / tagline / catchphrase** in `translation-toolkit`. Reads an `intake-spec` produced by `translation-intake` (Layer 1), runs an optional brand-brief intake, then runs the shared DRAFT / REFLECT / IMPROVE core loop with mode-conditional behavior: **faithful** mode = 4D reflection + S1 SHOULD; **transcreation** mode = 5D reflection (adds Effectiveness axis) + S1 MUST. Default emits a single output; `--variants=N` opts into N genuinely different alternatives.

## Inputs

- **source** — ad copy / headline / tagline / marketing-brief string, or a path to a short text file.
- **intake-spec** — from `translation-intake`. If invoked directly without one, run intake first (`--intake` flag) before continuing. Intake-spec carries `mode` (faithful | transcreation) — the load-bearing field for this skill.
- **brand brief** *(optional but strongly recommended for transcreation)* — captured per `protocols/brand-brief-intake.md` (archetype, tone-of-voice, do-not-say list, signature phrases, target persona, CTA style, brand-name handling). Skill-local; not part of the four shared service-interface fields.
- **glossary_path** *(optional)* — repo-local project glossary (L1 tier of the 4-tier resolver). Defaults to `<caller_repo>/docs/i18n/glossary-{target_locale}.md`; missing → fall through to L2 bundled glossary in `glossary/`.

Service-interface contract (the four shared fields plus `web_search`) is defined in the design spec §Service Interface; no per-skill duplication here.

## When to use

- Routed in by `using-translation-toolkit` when the input is ad-shaped (short, persuasive, headline-like) or when the user explicitly names ad copy / marketing / catchphrase / tagline / brand voice.
- Invoked directly by name when the user already knows creative is the right specialist.
- **Not** for i18n format files (use `translation-i18n`), prose / Markdown docs (use `translation-doc`), or reviewing an existing translation pair (use `translation-audit`).

## Modes

Mode is declared in the intake-spec and controls REFLECT axis count + S1 gate tier:

- **faithful** — preserves source structure + sentence boundaries with target-natural phrasing. 4D REFLECT (per `references/prompt-reflect-4d.md`). S1 = SHOULD (WARN on similarity < 0.85, output proceeds).
- **transcreation** — departs from literal surface to land equivalent persuasion in the target culture. Pun / rhyme / cultural-anchor substitution allowed and often required. 5D REFLECT (4D + Effectiveness axis, per `references/prompt-reflect-5d.md` and `references/5d-effectiveness.md`). S1 = MUST (FAIL on similarity < 0.70, output blocked). See `protocols/transcreation-mode.md` for the full mode-entry contract.

If the intake-spec does not specify mode explicitly, the router defaults ad-shaped genres to `transcreation` and prose-leaning marketing-brief content to `faithful`; the upstream `translation-intake` records the resolved mode + reason in the spec.

## Web search policy

ON by default per `using-translation-toolkit` §"Web search trade-off note" (spec Decision #15) — creative work benefits from current cultural / campaign context. Override to OFF when working with an established brand voice that risks contamination from competitor copy:

```
--web-search=off
```

When OFF, glossary resolution stops at L2 (bundled) — L3 (web) is skipped, L4 (LLM-fallback) still runs. Effectiveness-axis critique still operates from training-time cultural knowledge; transcreation does not require web search but loses freshness on recent slogans / memes / campaign references.

## Pipeline

This skill executes **Layers 2-5** of the toolkit's 5-layer pipeline. (Layer 1 — intake — is the upstream `translation-intake` skill, augmented here by the optional brand-brief intake in Layer 2 step 1.)

### Layer 2: Preparation

1. **Brand brief intake.** Per `protocols/brand-brief-intake.md`. Captures brand archetype (Hero / Sage / Outlaw / etc.), tone-of-voice axes (authoritative ↔ playful, formal ↔ casual, warm ↔ cool), do-not-say list, signature phrases (verbatim-preserve vs locale-transcreate decision), target persona, CTA style, and per-locale brand-name handling. **Recommended for transcreation; optional for faithful** (faithful mode falls back to intake-spec `register` + `intent` fields if no brief is provided). Brief outputs land in the audit-trail `brand_brief` block.

2. **Protect-pass.** Mask any structural spans with `⟦P:NN⟧` sentinels per `references/protect-pass-spec.md` (8 base classes — ICU plural, curly braces, printf, fenced code, inline code, HTML, URL, email). Ad copy is rarely placeholder-heavy, but URLs (campaign-link UTMs), HTML (rich-text email creative), and brand-name tokens still occur and MUST be masked when present.

3. **Source analysis.** Per chunk, extract: cultural references (idioms, allusions, anchor figures), wordplay (puns, rhymes, alliteration), CTA verbs + intensity, and untranslatability candidates (concepts with no clean target equivalent — flagged for I1). Feeds into glossary resolve, the WRITER prompt, and the Effectiveness axis in transcreation mode.

4. **Glossary resolve.** 4-tier fallthrough per `references/orthogonal-axes.md` and the plugin-level `docs/glossary-format-spec.md`:
   1. **L1 project** — `<repo>/docs/i18n/glossary-{target_locale}.md` (caller-supplied, highest priority)
   2. **L2 bundled** — `glossary/glossary-{source}--{target}.md` (Pontoon / GNOME / JLT / e-Stat / Tokyo / Cabinet / NAER ingested at build time)
   3. **L3 web search** — only if web search is ON; cite URL in audit-trail
   4. **L4 LLM fallback** — model proposes a translation; flagged in audit-trail with tier `L4` and lowest trust

   Only matched terms whose **source forms appear in the active chunk** flow into the WRITER / CRITIC / REVISER prompts — no full-glossary dump (see `references/core-loop.md` §8).

### Layer 3: Core loop

Three roles, one LLM call each per chunk per pass, per `references/core-loop.md`:

- **DRAFT** (WRITER) — `references/prompt-draft.md`. Receives brand-brief context (when present) alongside intake-spec axes; instructed to honor signature phrases + do-not-say list.
- **REFLECT** (CRITIC) — axis count is mode-conditional:
  - **faithful mode** → 4D per `references/prompt-reflect-4d.md` (Accuracy / Fluency / Style / Terminology)
  - **transcreation mode** → 5D per `references/prompt-reflect-5d.md` (4D + Effectiveness, defined in `references/5d-effectiveness.md`). Effectiveness judges whether the target preserves the **persuasion intent** in target culture (CTA strength, cultural-reference landing, emotional pull, taboo avoidance, brand-voice consistency, anchor-figure substitution, genre-convention fit, phonetic / rhythm preservation, claim-framing convention).
- **IMPROVE** (REVISER) — `references/prompt-improve.md`. Consumes the 4D or 5D critique and emits v2; preserves all `⟦P:NN⟧` tokens and any signature phrases marked verbatim-preserve in the brand brief.

WRITER and REVISER outputs MUST preserve every `⟦P:NN⟧` token exactly (same count, same IDs). CRITIC produces structured JSON critique only — never a rewrite.

### Layer 4: Verification

Per `references/verification-gates.md` §"Per-skill gate application". `translation-creative`'s defining trait is the **mode-conditional S1 tier flip** — back-translation is SHOULD in faithful but promoted to MUST in transcreation, the only place in the toolkit where a tier flip drives a HARD gate.

| Gate | Tier | Action |
|---|---|---|
| **M1** | HARD | Placeholder integrity — count + ID set parity for any URL / HTML / brand-token sentinels between source and target. Deterministic regex check. |
| **M2** | HARD | Project glossary compliance — every L1-mandated source term renders as its mapped target form (PASS_ADVISORY for `notes: context-dependent`). In transcreation mode see `protocols/transcreation-mode.md` §"Glossary leeway" — culturally-driven violations are auditable but allowed. Deterministic lookup. |
| **S1** | **MUST in transcreation, SHOULD in faithful** | Back-translation — subagent dispatches a blind v2 → source retranslation; embedding-cosine similarity vs original source. Threshold = **0.85** in faithful, **0.70** in transcreation (relaxed, per `references/verification-gates.md` §S1). **MUST in transcreation** = similarity below threshold blocks output as FAIL (not WARN). **SHOULD in faithful** = similarity below threshold surfaces a WARN to the caller, output proceeds. Skipped with audit-trail flag `S1: SKIPPED (no isolation capability)` if the runtime provides no subagent dispatch. |
| **S2** | SHOULD | Register preservation — JUDGE classifies source vs target register on a discourse / formality axis. Reliable for short ad-copy chunks because brand brief + intake-spec pin the register tightly; mismatch surfaces a WARN. |
| **I1** | INFO | Untranslatability flagging — runs only when Layer 2 source-analysis flags a phrase. Non-interactive: records borrow / explain / approximate decisions in the audit-trail; never blocks, never prompts. Particularly active in transcreation where cultural references frequently force an explicit borrow / substitute decision. |

S1's mode-conditional tier is the only case in the toolkit where a SHOULD becomes MUST. The reasoning, per spec Decision #4: in transcreation the WRITER is licensed to deviate substantially from the source surface, so M1 (placeholder count) and S2 (register) are insufficient guards against outright topic drift — S1 is the only gate that catches "the v2 is well-written copy about a different product". Promoting it to MUST in transcreation closes that hole; keeping it SHOULD in faithful avoids over-blocking on legitimate stylistic restructuring.

### Layer 5: Output

1. **Restore placeholder tokens.** Replace every `⟦P:NN⟧` in the translated text with the original substring from the protect-pass token map. Tokens absent from the translation surface as M1 failures (already caught in Layer 4) — restore is a clean swap at this point.
2. **Default emit: 1 translation.** A single best-effort target-locale rendering, paired with the audit-trail block.
3. **`--variants=N` opt-in: emit N genuinely different alternatives.** Each variant is a **full, independent DRAFT → REFLECT → IMPROVE run** with the WRITER prompt instructed to vary on a tactical axis (per `protocols/transcreation-mode.md` §"How variants differ"): variant 1 might preserve source structure; variant 2 might restructure for natural target rhythm; variant 3 might substitute a culturally equivalent metaphor. Variants are NOT paraphrases of a single draft — that pattern is explicitly forbidden because it produces synonym-swap noise instead of strategically different options.
4. **Emit audit-trail JSON.** Schema per `references/audit-trail-spec.md`. Records: brand brief (when present), every chunk's `(source, draft, reflect, improve)` quadruple per variant, every gate verdict with diff, every glossary resolution with tier + audit_path, every untranslatability decision, every transcreation-mode glossary-leeway override with rationale, and a `variant_index` per chunk when `--variants=N` was used.

## Variants and consistency

Distinguishing trait of `translation-creative` vs the other format specialists: **variants are a first-class output mode, not paraphrase noise.** Reasoning:

- Ad copy benefits from A/B candidates; downstream creative review is human and prefers strategically different starting points to picking between near-identical wordings.
- Each variant runs its own full core loop (3 LLM calls + gates) because shared draft → forked critique would produce critique that does not actually fit the variant being judged.
- The `variant_index` field in the audit trail lets downstream review tools (or `translation-audit` if pointed at a variant set) attribute issues to the specific variant.
- If a single variant fails S1 in transcreation mode (FAIL), that variant is dropped from the emitted set. If all `N` variants fail S1, the run halts and surfaces failure (rather than silently emitting fewer than N).

## Roles

Same vocabulary as the rest of the toolkit (per `using-translation-toolkit` §Roles vocabulary):

- **WRITER** — produces the draft, preserves `⟦P:NN⟧` tokens, honors brand-brief signature phrases + do-not-say list.
- **CRITIC** — 4D (faithful) or 5D (transcreation) structured JSON critique; no rewrites.
- **REVISER** — consumes critique, outputs v2; preserves placeholders + signature phrases.
- **BACK-TRANSLATOR** — blind v2 → source retranslation, used by S1 (MUST in transcreation, SHOULD in faithful).
- **JUDGE** — register classification, used by S2.

Roles are behavioral. Any LLM model can fill any role; this skill specifies behavior, not models.

## Cross-plugin composition

`copywriting-toolkit` can be invoked **after** creative translation for additional tone polish (e.g., voice-quadrant repositioning, ethics gates, framework-fit checks). This is **user-explicit composition only** — `translation-creative` does NOT auto-invoke `copywriting-toolkit`. Users who want the chain run it as two skill invocations:

```
1. translation-creative ... → creative-translated copy + audit-trail
2. copywriting-toolkit (using-copywriting-toolkit) ← creative-translated copy as input
```

`translation-creative` does not duplicate copywriting-toolkit's voice / form / ethics gates; the two skills are complementary and run sequentially when the user asks.

## What this skill does NOT do

- **Does not run intake.** If invoked without an intake-spec, hand off to `translation-intake` first (or use `--intake` to run it inline).
- **Does not generate brand strategy.** The brand brief intake captures existing brand decisions; it does not invent archetype / tone / persona from scratch. Missing brief in transcreation mode produces a WARN, not a generated strategy.
- **Does not replace human creative review.** Creative output ships to a human reviewer downstream — the audit trail + variant index are designed to make that review fast.
- **Does not translate brand names without explicit intake instruction.** Brand names default to verbatim-preserve unless the brand brief explicitly specifies translate / transliterate (katakana / 音譯 / hangul) / locale-substitute. Audit trail records the decision.
- **Does not auto-invoke `copywriting-toolkit`.** Composition is explicit (see above).
- **Does not paraphrase a single draft into variants.** `--variants=N` runs N independent core loops with axis-differentiated prompts (see Layer 5 step 3).
- **Does not bypass M1 / M2 in faithful mode.** No `--bypass-gates` flag exists (anti-pattern per spec Decision #15). Fix the underlying issue and re-run.
- **Does not bypass S1 in transcreation mode.** When S1 is MUST, a sub-threshold v2 blocks output; the resolution is to revise (re-run the loop with critique focus on the drift) or escalate to a human translator, NOT to flip the gate off.
- **Does not prompt the user during I1.** Untranslatability decisions are recorded, not asked.

## See also

- `protocols/brand-brief-intake.md` — brand brief capture template (archetype / tone / do-not-say / signature phrases / persona / CTA style / brand-name handling)
- `protocols/transcreation-mode.md` — when to enter transcreation mode, the 5th Effectiveness axis, how variants differ, S1 MUST contract, glossary leeway rule
- `checklists/creative-checklist.md` — 6-item creative-quality checklist (cultural references, persuasion intent, brand voice, do-not-say, variant differentiation, CTA strength)
- `references/protect-pass-spec.md` — canonical protect-pass algorithm and `⟦P:NN⟧` token format
- `references/core-loop.md` — DRAFT / REFLECT / IMPROVE role contracts and `<TRANSLATE_THIS>` windowing
- `references/4d-reflection.md` — critique axes for faithful mode
- `references/prompt-reflect-5d.md` + `references/5d-effectiveness.md` — 5-axis critique for transcreation mode (4D + Effectiveness)
- `references/verification-gates.md` — gate semantics including the §S1 mode-conditional tier flip
- `references/audit-trail-spec.md` — full audit-trail JSON schema (variant_index field documented here)
- `references/orthogonal-axes.md` — 5 intake axes + 4-tier glossary resolver definition
- `glossary/glossary-{source}--{target}.md` — bundled L2 glossary (5 pair files)
- `typography/jlreq-summary.md` — JLReq typography rules for `target_locale=ja-JP`
- `typography/clreq-summary.md` — CLReq typography rules for `target_locale=zh-CN` / `zh-TW`
- `../using-translation-toolkit/SKILL.md` — router (when to land here)
- `../translation-intake/SKILL.md` — Layer 1 owner
- `../../../docs/superpowers/specs/2026-05-06-translation-toolkit-design.md` — full design spec (Sub-skill Responsibility Matrix + Decision #4 on S1 tier flip + Decision #15 on web-search default)
