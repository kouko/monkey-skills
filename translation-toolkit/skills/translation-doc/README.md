# translation-doc

**English** | [日本語](README.ja.md) | [繁體中文](README.zh-TW.md)

> Translate markdown / technical documentation.
> Preserves code blocks, URLs, HTML, math, frontmatter, mermaid, and ASCII diagrams.

Part of the [translation-toolkit](../..) plugin. Operational spec
Claude loads is [`SKILL.md`](SKILL.md); this README is for humans.

## Why a dedicated doc skill

Markdown looks like prose but isn't all prose. A naive translation
pass will re-flow code fences, translate URL paths, mangle mermaid
diagram source, drop YAML frontmatter keys, and break TOC anchors —
all silent at the LLM-output level until a renderer breaks or a
reviewer notices anchors no longer resolve.

`translation-doc` walks the markdown AST, masks every structural span
(8 base placeholder classes + markdown-specific extensions), translates
only the prose, and reassembles a roundtrip-clean target. Chunks are
long enough that S1 + S2 (back-translation similarity + register
classification) produce reliable signal — unlike `translation-i18n`
where short UI strings make those gates noisy.

## Pipeline

```
intake-spec (from translation-intake)
        │
Layer 2 — Preparation
        ├── markdown AST parse: prose blocks vs structural blocks
        ├── protect-pass: mask code / URLs / HTML / math / frontmatter /
        │   mermaid / ASCII diagrams as ⟦P:NN⟧ tokens
        ├── source analysis: extract candidate difficult terms
        └── glossary resolve (4-tier: L1 project → L2 bundled → L3 web → L4 LLM)
        │
Layer 3 — Core loop (DRAFT → REFLECT 4D → IMPROVE)
        │   └── cross-chunk windowing: full doc as context;
        │       active chunk wrapped in <TRANSLATE_THIS>
        │
Layer 4 — Verification (M1 + M2 HARD; S1 + S2 SHOULD; I1 INFO)
        │
Layer 5 — Output
        ├── restore ⟦P:NN⟧ → original spans
        ├── reassemble markdown (preserve heading depth, list nesting,
        │   footnote ordering, table separators)
        ├── roundtrip check (code blocks byte-identical, link targets
        │   unchanged, anchors resolve)
        └── emit audit-trail.json
```

## What gets protected

Masked entire (LLM never sees the bytes inside): fenced / inline / indented
code, bare URLs, HTML blocks + inline tags, LaTeX math (`$$…$$` / `$…$`),
YAML frontmatter body, mermaid + ASCII diagrams. Inside markdown link
syntax `[text](url)`, only `url` is masked — `text` stays translatable.
Table separators and footnote labels also masked.

Markdown-specific patterns layer on top of the 8 base classes documented
in `references/protect-pass-spec.md`. Per-element rules in
[`protocols/markdown-ast-protect.md`](protocols/markdown-ast-protect.md).

## Cross-chunk windowing

Long markdown documents chunk at section boundaries. Per chunk,
WRITER / CRITIC / REVISER prompts re-emit the **entire document** with
only the active chunk wrapped in `<TRANSLATE_THIS>...</TRANSLATE_THIS>`;
surrounding sections appear unwrapped as context.

This preserves:

- **Cross-section term consistency** — a glossary term translated in
  Section 3 stays consistent when Section 7 reuses it
- **Heading-anchor continuity** — target anchors stay consistent
  because the active chunk's heading is translated with full visibility
  of the doc-wide heading set
- **Footnote-reference integrity** — labels follow the same windowing

Below the 2000-token chunk threshold, the document is a single chunk
and the windowing degenerates to a normal prompt.

## Verification gate matrix

Full gate set, calibrated for prose-length chunks:

| Gate | Tier | What it checks |
|---|---|---|
| **M1** | HARD | Placeholder integrity — `⟦P:NN⟧` count + ID set parity for code / URLs / HTML / math / frontmatter / diagram tokens |
| **M2** | HARD | Project glossary compliance — every L1-mandated source term renders as its mapped target form |
| **S1** | SHOULD | Back-translation — subagent produces blind v2 → source retranslation; embedding-cosine similarity vs source. WARN below threshold; output proceeds. Skipped with audit-trail flag if runtime provides no isolation. |
| **S2** | SHOULD | Register preservation — JUDGE classifies source vs target register; mismatch surfaces a WARN |
| **I1** | INFO | Untranslatability flagging — runs only when source-analysis flags a phrase. Non-interactive. |

S1 / S2 are SHOULD, not HARD: a single-chunk failure with a clear
cause records to the audit-trail and surfaces to the caller, but does
not block emit. M1 / M2 still HARD-block on failure.

## Roundtrip checklist

Before emit, [`checklists/doc-quality-checklist.md`](checklists/doc-quality-checklist.md)
verifies:

1. Code blocks byte-identical
2. Link targets unchanged
3. Heading levels match
4. TOC anchors resolve
5. Mermaid + ASCII diagrams byte-identical
6. Frontmatter keys preserved

Failure on any item halts emit and surfaces to the caller.

## Web search policy

ON by default. Override to OFF for batch doc runs (e.g. translating a
multi-hundred-page handbook):

```
--web-search=off
```

When OFF, glossary resolution stops at L2 (bundled) — L3 (web) is
skipped, L4 (LLM-fallback) still runs.

## What this skill does NOT do

- **Does not run intake.** Hand off to [`translation-intake`](../translation-intake)
  (or use `--intake`)
- **Does not touch code-block contents** or **modify ASCII / mermaid diagrams** —
  both masked entire. Localizing diagram node labels is a manual
  downstream task.
- **Does not translate URL paths** — only link `text` is translatable.
- **Does not translate i18n files** ([`translation-i18n`](../translation-i18n)),
  **generate variants** ([`translation-creative`](../translation-creative)),
  or **audit existing pairs** ([`translation-audit`](../translation-audit))
- **Does not bypass M1 / M2.** No `--bypass-gates` flag (anti-pattern per
  spec Decision #15)

## See also

- [`SKILL.md`](SKILL.md) — operational spec
- [`protocols/markdown-ast-protect.md`](protocols/markdown-ast-protect.md) ·
  [`checklists/doc-quality-checklist.md`](checklists/doc-quality-checklist.md)
- [`references/verification-gates.md`](references/verification-gates.md) ·
  [`references/core-loop.md`](references/core-loop.md) (`<TRANSLATE_THIS>` windowing)
- Typography: [`typography/jlreq-summary.md`](typography/jlreq-summary.md) (ja-JP) ·
  [`typography/clreq-summary.md`](typography/clreq-summary.md) (zh-CN / zh-TW)
- Plugin: [`../../README.md`](../../README.md) ·
  Router: [`../using-translation-toolkit`](../using-translation-toolkit) ·
  Layer 1: [`../translation-intake`](../translation-intake)
