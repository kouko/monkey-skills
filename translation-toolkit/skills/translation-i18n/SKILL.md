---
name: translation-i18n
description: Translate i18n strings (PO / JSON / XLIFF / Android strings.xml / iOS .strings) preserving placeholders, keys, and project glossary. Web search ON, S1 back-trans SHOULD, M1+M2 strict.
version: 0.1.0
---

# translation-i18n

Layer 2-5 owner for **i18n format files** in `translation-toolkit`. Reads an `intake-spec` produced by `translation-intake` (Layer 1), parses one of five i18n format families, runs the shared DRAFT / REFLECT / IMPROVE core loop with strict placeholder + project-glossary preservation, and writes back into the original format.

## Inputs

- **source** — file path (one of `.po` / `.json` / `.xliff` / `strings.xml` / `.strings`) or an inline strings map keyed by ID.
- **intake-spec** — from `translation-intake`. If the user invokes this skill directly without one, run intake first (`--intake` flag) before continuing.
- **glossary_path** *(optional)* — repo-local project glossary (L1 tier of the 4-tier resolver). Defaults to `<caller_repo>/docs/i18n/glossary-{target_locale}.md`; missing → fall through to L2 bundled glossary in `glossary/`.

Service-interface contract (the four shared fields plus `web_search`) is defined in the design spec §Service Interface; no per-skill duplication here.

## When to use

- Routed in by `using-translation-toolkit` when the user supplies a PO / JSON / XLIFF / Android `strings.xml` / iOS `.strings` file.
- Invoked directly by name when the user already knows i18n is the right specialist.
- **Not** for prose / Markdown docs (use `translation-doc`), ad copy / catchphrases (use `translation-creative`), or reviewing an existing translation pair (use `translation-audit`).

## Web search policy

ON by default per `using-translation-toolkit` §"Web search trade-off note" (spec Decision #15). Override to OFF for batch i18n runs (1000s of strings):

```
--web-search=off
```

When OFF, glossary resolution stops at L2 (bundled) — L3 (web) is skipped, L4 (LLM-fallback) still runs. Spot-check a sample with web search re-enabled on a follow-up pass; do not ship a full untriaged batch.

## Pipeline

This skill executes **Layers 2-5** of the toolkit's 5-layer pipeline. (Layer 1 — intake — is the upstream `translation-intake` skill.)

### Layer 2: Preparation

1. **Parse format.** Auto-detect by extension first, then by content sniffing:
   - `.po` → gettext PO via polib-equivalent algorithm
   - `.json` → key-value map; recurse into nested objects, dot-notation key paths
   - `.xliff` / `.xlf` → XLIFF 2.x parser (`<unit>` / `<segment>` / `<source>` / `<target>`)
   - `strings.xml` → Android resource format (`<string>`, `<plurals>`, `<string-array>`)
   - `.strings` → iOS NSLocalizedString (`"key" = "value";` lines, `/* */` comments)

   Per-format read+write algorithms are in `protocols/format-roundtrip.md`. Preflight checks in `checklists/i18n-format-checklist.md` MUST run before parse.

2. **Protect-pass.** Mask every placeholder span with `⟦P:NN⟧` sentinels per `references/protect-pass-spec.md` (8 base classes — ICU plural, curly braces, printf, fenced code, inline code, HTML, URL, email). Layer i18n-specific patterns on top: ICU `select` / `selectordinal`, gender selectors, Android `<plurals>` items, format-arg tags inside `<![CDATA[...]]>`. See `protocols/placeholder-protect.md`.

3. **Source analysis.** For each entry, extract candidate difficult terms (ASCII abbreviations, CJK technical compounds, project-specific identifiers) and domain hints. Feeds into glossary resolve and into the WRITER prompt.

4. **Glossary resolve.** 4-tier fallthrough per `references/orthogonal-axes.md` and the plugin-level `docs/glossary-format-spec.md`:
   1. **L1 project** — `<repo>/docs/i18n/glossary-{target_locale}.md` (caller-supplied, highest priority)
   2. **L2 bundled** — `glossary/glossary-{source}--{target}.md` (Pontoon / GNOME / JLT / e-Stat / Tokyo / Cabinet / NAER ingested at build time)
   3. **L3 web search** — only if web search is ON; cite URL in audit-trail
   4. **L4 LLM fallback** — model proposes a translation; flagged in audit-trail with tier `L4` and lowest trust

   Only matched terms whose **source forms appear in the active chunk** flow into the WRITER / CRITIC / REVISER prompts — no full-glossary dump (see `references/core-loop.md` §8).

### Layer 3: Core loop

Three roles, one LLM call each per chunk per pass, per `references/core-loop.md`:

- **DRAFT** (WRITER) — `references/prompt-draft.md`
- **REFLECT 4D** (CRITIC) — `references/prompt-reflect-4d.md` (Accuracy / Fluency / Style / Terminology). i18n is 4D-only — no Effectiveness axis (that is `translation-creative` in transcreation mode).
- **IMPROVE** (REVISER) — `references/prompt-improve.md`

**Cross-string consistency.** All entries from the same source file are translated as a **single batch** in one LLM context. Per-entry prompts re-emit sibling entries inside `<CONTEXT>...</CONTEXT>` wrapping (analogous to the doc skill's `<TRANSLATE_THIS>` windowing on chunks): the active entry is wrapped in `<TRANSLATE_THIS>...</TRANSLATE_THIS>`, surrounding entries appear unwrapped as context only. This guarantees term consistency across keys without forcing each string to be translated in isolation. For very large `.po` / `.xliff` files exceeding the 2000-token chunk threshold, the file is split into multiple batches — each batch retains intra-batch context windowing.

WRITER and REVISER outputs MUST preserve every `⟦P:NN⟧` token exactly (same count, same IDs). CRITIC produces structured JSON critique only — never a rewrite.

### Layer 4: Verification

Per `references/verification-gates.md` §"Per-skill gate application". i18n's gate matrix is the leanest of the four format specialists — only M1 + M2 are active; S1 / S2 are typically skipped because per-string i18n payloads are too short for those gates to produce meaningful signal. I1 runs only when Layer 2 source-analysis flags untranslatable phrases.

| Gate | Tier | Action |
|---|---|---|
| **M1** | HARD | Placeholder integrity — count + ID set parity between source and target. Deterministic regex check. |
| **M2** | HARD | Project glossary compliance — every L1-mandated source term renders as its mapped target form (PASS_ADVISORY for `notes: context-dependent`). Deterministic lookup. |
| **S1** | SKIPPED | Back-translation — UI strings are too short for embedding-cosine similarity to produce a meaningful score. Active in `translation-doc` / `-creative` / `-audit` where chunks are longer. |
| **S2** | SKIPPED | Register preservation — too few tokens per string for the JUDGE register classifier to be reliable; UI register is also pinned by format conventions (button text, dialog title, etc.). |
| **I1** | INFO | Untranslatability flagging — runs only when source-analysis flags a phrase. Non-interactive: records borrow / explain / approximate decisions in the audit-trail; never blocks, never prompts. |

M1 and M2 being the only HARD gates makes the project glossary (M2) the dominant quality lever for i18n: invest in `<repo>/docs/i18n/glossary-{target_locale}.md` rather than relying on post-translation similarity gates that won't fire here.

When invoked through `translation-audit` against an existing translation pair, the full gate set (M1 + M2 + S1 + S2 + I1) is applied per the audit skill's matrix — i18n's local skip is for forward-translation runs only.

### Layer 5: Output

1. **Restore placeholder tokens.** Replace every `⟦P:NN⟧` in each translated entry with the original substring from the protect-pass token map. Tokens absent from the translation surface as M1 failures (already caught in Layer 4) — restore is a clean swap at this point.
2. **Write back to original format.** Per `protocols/format-roundtrip.md`: preserve key order, comments, `msgctxt` / `msgid_plural` / `<plurals>` structure, `translatable="false"` skip flags, escape rules. Writes to the same path family (e.g. `messages.po` → `messages.<target_locale>.po` if no explicit output path was given).
3. **Emit audit-trail JSON.** Schema per `references/audit-trail-spec.md`. Every chunk's `(source, draft, reflect, improve)` quadruple, every gate verdict with diff, every glossary resolution with tier + audit_path, every untranslatable decision.
4. **Update I1 untranslatability list (when applicable).** When Layer 2 source-analysis flagged any untranslatable phrase, record the borrow / explain / approximate decision in the audit trail. **Non-interactive** — no user prompt is ever raised, even when `translation-audit` is the downstream consumer.

## Cross-string consistency (recap)

Distinguishing trait of i18n vs the other format specialists: **the entire file is one batch context**, even though entries are independent at the format level. Reasoning:

- UI strings under the same key namespace share register, vocabulary, and brand voice. Translating each in isolation produces inconsistent surface forms (e.g., `Cancel` → `キャンセル` for `dialog.cancel` but `中止` for `nav.cancel` — both valid, but bad UX).
- The cross-entry `<CONTEXT>` window costs tokens but pays back in consistency and reduces project-glossary churn.
- For files large enough to exceed the 2000-token chunk threshold, batches are formed by splitting on entry boundaries (never inside an entry). Within a batch, all entries see each other; across batches, only L1 / L2 glossary enforces consistency.

## Roles

Same vocabulary as the rest of the toolkit (per `using-translation-toolkit` §Roles vocabulary):

- **WRITER** — produces the draft, preserves `⟦P:NN⟧` tokens.
- **CRITIC** — 4D structured JSON critique; no rewrites.
- **REVISER** — consumes critique, outputs v2; preserves placeholders.
- **BACK-TRANSLATOR** — blind v2 → source retranslation, used by S1.
- **JUDGE** — register classification, used by S2.

Roles are behavioral. Any LLM model can fill any role; this skill specifies behavior, not models.

## What this skill does NOT do

- **Does not run intake.** If invoked without an intake-spec, hand off to `translation-intake` first (or use `--intake` to run it inline).
- **Does not translate Markdown / prose docs.** Route to `translation-doc`.
- **Does not generate transcreation variants.** Route to `translation-creative` with `--variants=N`.
- **Does not audit existing translations.** Route to `translation-audit`.
- **Does not bypass M1 / M2.** No `--bypass-gates` flag exists (anti-pattern per spec Decision #15). Fix the underlying issue and re-run.
- **Does not prompt the user during I1.** Untranslatability decisions are recorded, not asked.

## See also

- `protocols/placeholder-protect.md` — i18n-specific patterns layered on protect-pass-spec base classes
- `protocols/format-roundtrip.md` — per-format (PO / JSON / XLIFF / Android / iOS) read+write algorithms
- `checklists/i18n-format-checklist.md` — 8-item preflight before parse + write
- `references/protect-pass-spec.md` — canonical protect-pass algorithm and `⟦P:NN⟧` token format
- `references/core-loop.md` — DRAFT / REFLECT / IMPROVE role contracts and cross-chunk windowing
- `references/4d-reflection.md` — critique axes for i18n's 4D mode
- `references/verification-gates.md` — gate semantics + audit-trail entry shapes
- `references/audit-trail-spec.md` — full audit-trail JSON schema
- `references/orthogonal-axes.md` — 5 intake axes + 4-tier glossary resolver definition
- `glossary/glossary-{source}--{target}.md` — bundled L2 glossary (5 pair files)
- `../using-translation-toolkit/SKILL.md` — router (when to land here)
- `../translation-intake/SKILL.md` — Layer 1 owner
- `../../../docs/superpowers/specs/2026-05-06-translation-toolkit-design.md` — full design spec (Sub-skill Responsibility Matrix + Decisions)
