# Creative checklist — 6-item creative-quality

> Run after Layer 4 verification gates pass, before Layer 5 emit. Any
> unchecked item halts the run with a clear actionable message; do not
> silently degrade.
>
> The 6 items operationalize the qualitative judgments that the gates +
> Effectiveness axis produce — this checklist is the final pre-emit
> sanity sweep that catches issues which slipped through both. Combined
> cost is small (audit-trail scan + diff against brand brief + 1 LLM
> round-robin call when variant differentiation needs scoring).

## The 6 items

- [ ] **1. Cultural references land in target.** Every cultural reference
      flagged by Layer 2 source analysis (idiom, allusion, anchor figure,
      pun, meme, locale-specific concept) has a recorded handling
      decision in the audit-trail I1 block: **borrow** (source script
      preserved with optional gloss), **explain** (target prose explains
      the reference inline), or **approximate** (target substitutes a
      culturally equivalent reference). Halt if any flagged reference
      surfaces in the v2 with no I1 entry — that means the LLM silently
      dropped or literally translated a load-bearing cultural element.
      Concrete examples: 御朱印 in JP religious-tourism copy → borrow
      with gloss for non-JP audience; 寿司 → borrow verbatim (universally
      recognized loanword); a "Steve Jobs said" anchor in en-US source
      → approximate or rephrase as authority-neutral when the cultural
      weight is the load-bearing element (per
      `references/5d-effectiveness.md` §"Anchor-figure substitution").

- [ ] **2. Persuasion intent preserved (verified by S1).** The S1
      back-translation gate verdict must be PASS (or PASS_ADVISORY with
      an audit-trail rationale). Threshold = **0.85** in faithful mode,
      **0.70** in transcreation mode (relaxed because surface deviation
      is licensed). In transcreation, S1 is **MUST** — a sub-threshold
      v2 already blocks at Layer 4; this checklist item is the final
      verification that the gate verdict is recorded and the audit trail
      cites the similarity score. Halt if S1 SKIPPED with no recorded
      reason (legitimate skip is "no isolation capability" — anything
      else is a pipeline bug).

- [ ] **3. Brand voice consistent with brief.** When a brand brief was
      captured at Layer 2 step 1, the v2 must honor the three voice
      axes (authority / formality / warmth) declared in the brief. The
      audit-trail `brand_brief_consistency` field records the per-axis
      verdict (PASS / WARN). A WARN here is not auto-halt (voice is
      qualitative; some drift is expected) but is surfaced to the
      caller. Halt only on **direct contradiction** — a brief that says
      `warmth: warm (4/5)` and a v2 that reads cold-detached is a
      contradiction; a brief that says `formality: casual (3/5)` and a
      v2 that has one slightly formal sentence is a WARN. When no
      brief was captured (faithful mode, no brief provided), this item
      is N/A and the audit trail records `brand_brief: not_provided`.

- [ ] **4. Do-not-say list respected.** Substring-scan the v2 against
      the do-not-say list captured in the brand brief (Field 3 of
      `protocols/brand-brief-intake.md`). The scan is case-insensitive
      with word-boundary respect (no false positive on "cheaply" if
      "cheap" is banned, but yes hit on "Cheap deal"). Halt on any
      hit; the resolution is to re-run REVISER with the offending
      phrase explicitly forbidden in the IMPROVE prompt. When no brief
      was captured, this item degenerates to "intake-spec banned
      terms" (if any) and is N/A when intake also has nothing. Audit
      trail records every hit + the substituted phrase chosen.

- [ ] **5. Variants are genuinely different (when `--variants=N`).**
      Skip when N=1 (default emit). When N≥2, each variant must differ
      from sibling variants on a tactical axis per
      `protocols/transcreation-mode.md` §"How variants differ". The
      check is a JUDGE-call comparing each variant pair on a 5-axis
      differentiation scale: structure / rhythm / metaphor / anchor /
      genre-convention. Two variants matching on **all 5 axes** are
      considered paraphrases (FAIL — the LLM produced synonym-swap
      noise instead of strategically different options). Two variants
      matching on **4 of 5 axes** is a WARN (still emit, but flag for
      reviewer attention). Audit trail records the differentiation
      matrix per variant pair. When all variants pass differentiation,
      the audit trail records `variant_differentiation: PASS` per pair.

- [ ] **6. CTA strength matches source.** The brand brief Field 6 (or
      intake-spec inferred when no brief) declares CTA style as
      **direct** / **suggestive** / **aspirational**. The v2's CTA
      verb intensity must match: a **direct** source (e.g., "Buy now")
      rendered as 「ご検討ください」 in v2 fails this check (over-
      polite, kills urgency); a **suggestive** source rendered as a
      **direct** v2 also fails (over-aggressive for the brand voice).
      When the source carries multiple CTAs (e.g., a long-form ad with
      headline CTA + footer CTA), each CTA is checked independently
      against the brief's per-position declaration (e.g., Patagonia
      example brief — `default: aspirational, storefront_pages:
      direct`). Halt with the source / target CTA pair and the
      mismatch direction (over-polite / over-aggressive) so the
      REVISER can target the fix.

## When to run

| Step | Items |
|---|---|
| Immediately after Layer 4 verification gates pass, before Layer 5 emit | 1, 2, 3, 4, 6 |
| When `--variants=N` with N≥2, after all variants complete their core loops | 5 |

Items 1-4 + 6 are checked once per emitted output. Item 5 is checked
once per variant-pair across the variant set; e.g., N=3 produces 3
pairs (v1-v2, v1-v3, v2-v3) and each pair gets a verdict.

## What this checklist does NOT cover

- **Placeholder count parity** — that's M1 (`references/verification-gates.md`
  §M1). M1 runs at Layer 4; if M1 fails the run halts before this
  checklist sees the output.
- **Project glossary compliance** — that's M2, including the
  transcreation-mode glossary-leeway exception
  (`protocols/transcreation-mode.md` §"M2 glossary leeway").
- **4D / 5D translation quality axes** — that's the REFLECT step
  (`references/4d-reflection.md` + `references/5d-effectiveness.md`)
  consumed by IMPROVE before this checklist runs.
- **Format / roundtrip integrity** — creative output is plain text;
  there is no AST roundtrip to verify (vs `translation-doc`'s
  6-item doc-quality-checklist which owns markdown roundtrip).
- **Human creative review** — explicitly out of scope per SKILL.md
  §"What this skill does NOT do". The checklist + audit trail are
  designed to make downstream human review fast, not to replace it.

## See also

- `../SKILL.md` — invokes this checklist at the Layer 4 → Layer 5 boundary
- `../protocols/brand-brief-intake.md` — Fields 3 (do-not-say), 6 (CTA
  style), and the per-axis voice declaration this checklist verifies
  against
- `../protocols/transcreation-mode.md` — §"How variants differ" defines
  the 5-axis differentiation scale used by item 5; §"M2 glossary
  leeway" defines what M2 audit entries mean (informs item 1 review)
- `../references/verification-gates.md` §S1 — back-translation algorithm
  + the mode-conditional 0.85 / 0.70 thresholds checked by item 2
- `../references/5d-effectiveness.md` — Effectiveness-axis concerns that
  feed item 1 (cultural references) and item 6 (CTA strength)
- `../references/audit-trail-spec.md` — schema for the I1 block, the
  brand_brief_consistency block, and the variant_differentiation matrix
  that this checklist reads
