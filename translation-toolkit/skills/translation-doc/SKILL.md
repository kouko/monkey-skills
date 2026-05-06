---
name: translation-doc
description: Translate markdown / technical documentation preserving code blocks, URLs, HTML, math blocks, frontmatter, mermaid + ASCII diagrams. Web search ON, S1+S2 SHOULD, M1+M2 strict.
version: 0.1.0
---

# translation-doc

Layer 2-5 owner for **markdown / technical documentation** in `translation-toolkit`. Reads an `intake-spec` from `translation-intake` (Layer 1), parses the markdown AST so structural spans (code, URLs, HTML, math, frontmatter, mermaid, ASCII diagrams) are masked, runs the shared DRAFT / REFLECT / IMPROVE core loop with cross-chunk `<TRANSLATE_THIS>` windowing, and reassembles a roundtrip-clean target file.

## Inputs

- **source** — markdown file path (`.md` / `.markdown` / `.mdx`) or an inline markdown string.
- **intake-spec** — from `translation-intake`. If invoked directly without one, run intake first (`--intake` flag) before continuing.
- **glossary_path** *(optional)* — repo-local project glossary (L1 tier of the 4-tier resolver). Defaults to `<caller_repo>/docs/i18n/glossary-{target_locale}.md`; missing → fall through to L2 bundled glossary in `glossary/`.

Service-interface contract (the four shared fields plus `web_search`) is defined in the design spec §Service Interface; no per-skill duplication here.

## When to use

- Routed in by `using-translation-toolkit` when the user supplies a `.md` / `.mdx` / `.markdown` file or pastes technical-documentation prose.
- Invoked directly by name when the user already knows markdown is the right specialist.
- **Not** for i18n format files (use `translation-i18n`), ad copy / catchphrases (use `translation-creative`), or reviewing an existing translation pair (use `translation-audit`).

## Web search policy

ON by default per `using-translation-toolkit` §"Web search trade-off note" (spec Decision #15). Override to OFF for batch doc runs (e.g. translating a multi-hundred-page handbook):

```
--web-search=off
```

When OFF, glossary resolution stops at L2 (bundled) — L3 (web) is skipped, L4 (LLM-fallback) still runs. Spot-check a sample with web search re-enabled before shipping a full untriaged batch.

## Pipeline

This skill executes **Layers 2-5** of the toolkit's 5-layer pipeline. (Layer 1 — intake — is the upstream `translation-intake` skill.)

### Layer 2: Preparation

1. **Markdown AST parse.** Walk the markdown source and split into prose blocks vs. structural blocks (fenced code, indented code, inline code, markdown link targets, bare URLs, HTML blocks / inline tags, LaTeX math, frontmatter YAML, mermaid / ASCII diagrams, table separators, footnote labels). Per-element rules in `protocols/markdown-ast-protect.md`.

2. **Protect-pass.** Mask every structural span with `⟦P:NN⟧` sentinels per `references/protect-pass-spec.md` (8 base classes — ICU plural, curly braces, printf, fenced code, inline code, HTML, URL, email). Layer markdown-specific patterns on top: bare URLs in markdown link syntax, frontmatter YAML body, math blocks (`$$…$$` / `$…$`), mermaid + ASCII diagram blocks, table cell boundaries, footnote labels. See `protocols/markdown-ast-protect.md`.

3. **Source analysis.** Per chunk, extract candidate difficult terms (technical compounds, project-specific identifiers, ASCII abbreviations) and cross-link references (other headings in the same doc, footnote bodies). Feeds into glossary resolve and into the WRITER prompt.

4. **Glossary resolve.** 4-tier fallthrough per `references/orthogonal-axes.md` and the plugin-level `docs/glossary-format-spec.md`:
   1. **L1 project** — `<repo>/docs/i18n/glossary-{target_locale}.md` (caller-supplied, highest priority)
   2. **L2 bundled** — `glossary/glossary-{source}--{target}.md` (Pontoon / GNOME / JLT / e-Stat / Tokyo / Cabinet / NAER ingested at build time)
   3. **L3 web search** — only if web search is ON; cite URL in audit-trail
   4. **L4 LLM fallback** — model proposes a translation; flagged in audit-trail with tier `L4` and lowest trust

   Only matched terms whose **source forms appear in the active chunk** flow into the WRITER / CRITIC / REVISER prompts — no full-glossary dump (see `references/core-loop.md` §8).

### Layer 3: Core loop

Three roles, one LLM call each per chunk per pass, per `references/core-loop.md`:

- **DRAFT** (WRITER) — `references/prompt-draft.md`
- **REFLECT 4D** (CRITIC) — `references/prompt-reflect-4d.md` (Accuracy / Fluency / Style / Terminology). Doc mode is 4D — Effectiveness is `translation-creative`'s axis in transcreation mode.
- **IMPROVE** (REVISER) — `references/prompt-improve.md`

**Cross-chunk windowing.** Long markdown documents are chunked at section boundaries. Per chunk, the WRITER / CRITIC / REVISER prompts re-emit the entire document with only the **active chunk** wrapped in `<TRANSLATE_THIS>...</TRANSLATE_THIS>`; surrounding sections appear unwrapped as context. This preserves cross-section term consistency, heading-anchor continuity, and footnote-reference integrity without forcing each chunk to be translated in isolation. Below the chunk threshold (default 2000 source tokens) the document is a single chunk and the windowing degenerates to a normal prompt.

WRITER and REVISER outputs MUST preserve every `⟦P:NN⟧` token exactly (same count, same IDs). CRITIC produces structured JSON critique only — never a rewrite.

### Layer 4: Verification

Per `references/verification-gates.md` §"Per-skill gate application". `translation-doc` runs the **full meaningful gate set** — chunks are long enough that S1 / S2 produce reliable signal, unlike `translation-i18n` where short UI strings make those gates noisy.

| Gate | Tier | Action |
|---|---|---|
| **M1** | HARD | Placeholder integrity — count + ID set parity for code blocks / URLs / HTML / math / frontmatter / diagram tokens between source and target. Deterministic regex check. |
| **M2** | HARD | Project glossary compliance — every L1-mandated source term renders as its mapped target form (PASS_ADVISORY for `notes: context-dependent`). Deterministic lookup. |
| **S1** | SHOULD | Back-translation — subagent dispatches a blind v2 → source retranslation; embedding-cosine similarity vs original source. Reliable for prose-length doc chunks. Requires runtime subagent / task-isolation capability; gracefully skips with audit-trail flag `S1: SKIPPED (no isolation capability)` otherwise. |
| **S2** | SHOULD | Register preservation — JUDGE classifies source vs target register on a discourse / formality axis. Reliable for prose chunks; UI-string register-pinning concerns from i18n do not apply. |
| **I1** | INFO | Untranslatability flagging — runs only when Layer 2 source-analysis flags a phrase. Non-interactive: records borrow / explain / approximate decisions in the audit-trail; never blocks, never prompts. |

S1 / S2 are **SHOULD**, not HARD: a single-chunk failure with a clear cause (e.g. terminology mismatch on a domain term outside the project glossary) records to the audit-trail and surfaces to the caller, but does not block emit. M1 / M2 still HARD-block the run on failure.

### Layer 5: Output

1. **Restore placeholder tokens.** Replace every `⟦P:NN⟧` in each translated chunk with the original substring from the protect-pass token map. Tokens absent from the translation surface as M1 failures (already caught in Layer 4) — restore is a clean swap at this point.
2. **Reassemble markdown.** Stitch translated chunks back into a single document, preserving source byte-position of code blocks, math blocks, mermaid / ASCII diagrams, frontmatter, and table separators. Heading depth, list nesting, and footnote ordering preserved from the source AST.
3. **Roundtrip check.** Per `checklists/doc-quality-checklist.md`: code blocks byte-identical, link targets unchanged, heading levels match, TOC anchors resolve, mermaid + ASCII diagrams byte-identical. Failure on any item halts emit and surfaces to the caller.
4. **Emit audit-trail JSON.** Schema per `references/audit-trail-spec.md`. Every chunk's `(source, draft, reflect, improve)` quadruple, every gate verdict with diff, every glossary resolution with tier + audit_path, every untranslatable decision.

## Cross-chunk consistency (recap)

Distinguishing trait of `translation-doc` vs `translation-i18n`: **chunks are long-form prose** and benefit from in-context surrounding sections. The `<TRANSLATE_THIS>` windowing pattern (TA's contribution) keeps glossary terms consistent across chapters / sections and lets the WRITER see how a term was translated 200 lines earlier without re-injecting the full glossary on every call. Heading anchors, footnote labels, and cross-link references follow the same windowing — the active chunk's heading is translated with full visibility of the doc-wide heading set, so target anchors stay consistent.

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
- **Does not touch code-block contents.** Fenced + indented code is masked entire; the LLM never sees the bytes inside.
- **Does not modify ASCII / mermaid diagrams.** Treated as code blocks (masked entire). The LLM cannot localise diagram node labels — that's a manual task downstream if needed.
- **Does not translate URL paths.** Markdown link syntax `[text](url)` keeps `url` masked; only `text` is translatable.
- **Does not translate i18n format files.** Route to `translation-i18n`.
- **Does not generate transcreation variants.** Route to `translation-creative` with `--variants=N`.
- **Does not audit existing translations.** Route to `translation-audit`.
- **Does not bypass M1 / M2.** No `--bypass-gates` flag exists (anti-pattern per spec Decision #15). Fix the underlying issue and re-run.
- **Does not prompt the user during I1.** Untranslatability decisions are recorded, not asked.

## See also

- `protocols/markdown-ast-protect.md` — markdown-specific patterns layered on protect-pass-spec base classes
- `checklists/doc-quality-checklist.md` — 6-item roundtrip check before emit
- `references/protect-pass-spec.md` — canonical protect-pass algorithm and `⟦P:NN⟧` token format
- `references/core-loop.md` — DRAFT / REFLECT / IMPROVE role contracts and `<TRANSLATE_THIS>` windowing
- `references/4d-reflection.md` — critique axes for doc mode
- `references/verification-gates.md` — gate semantics + audit-trail entry shapes
- `references/audit-trail-spec.md` — full audit-trail JSON schema
- `references/orthogonal-axes.md` — 5 intake axes + 4-tier glossary resolver definition
- `glossary/glossary-{source}--{target}.md` — bundled L2 glossary (5 pair files)
- `typography/jlreq-summary.md` — JLReq typography rules for `target_locale=ja-JP`
- `typography/clreq-summary.md` — CLReq typography rules for `target_locale=zh-CN` / `zh-TW`
- `../using-translation-toolkit/SKILL.md` — router (when to land here)
- `../translation-intake/SKILL.md` — Layer 1 owner
- `../../../docs/superpowers/specs/2026-05-06-translation-toolkit-design.md` — full design spec (Sub-skill Responsibility Matrix + Decisions)
