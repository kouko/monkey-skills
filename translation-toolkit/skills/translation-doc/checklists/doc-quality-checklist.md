# Doc quality checklist — 6-item roundtrip

> Run after Layer 5 reassemble, before emit. Any unchecked item halts the
> run with a clear actionable message; do not silently degrade.
>
> All six items combined are cheap (byte-equality scans of structural spans
> + heading-depth counter + anchor-table reconciliation). The point is
> fail-fast on AST drift — markdown that round-trips visually but breaks
> code, links, anchors, or diagrams ships subtly broken docs that are hard
> to triage post-emit.

## The 6 items

- [ ] **1. Code blocks not modified.** Every fenced code block (``` ```lang … ``` ```)
      and every inline code span (`` `code` ``) in the target is byte-identical
      to its source counterpart. The protect-pass guarantees this by
      construction (code blocks are opaque tokens — the LLM never sees the
      bytes), but this check verifies the token-restore step did not corrupt
      whitespace, fence-delimiter count, or language-tag attribution. A
      mismatch here means the protect-pass / restore pipeline has a bug and
      every translated doc must be re-checked. Halt with the diff between
      source and target code-block content.

- [ ] **2. Link targets preserved.** For every markdown link `[text](url)`,
      reference-style link `[text][label]` + `[label]: url` definition, and
      bare URL in the source, the corresponding URL in the target is byte-
      identical to the source URL. Only the link **text** is allowed to
      change. The protect-pass owns the URL portion (per
      `protocols/markdown-ast-protect.md` extension 2); this check verifies
      the AST reassembler patched the right target back into the right
      position. URL drift here means broken links downstream — halt with
      the source/target URL pair that mismatched.

- [ ] **3. Heading levels match.** The count and depth of `#` / `##` / `###`
      / `####` / `#####` / `######` headings in the target is identical
      to the source. The translated heading **text** changes; the **`#`
      count** must not. Headings are AST structural nodes, not prose
      decoration — losing a level breaks the document outline, the
      auto-generated TOC (item 4), and any downstream tool that walks the
      AST. Surface the first source/target heading pair that disagrees on
      depth.

- [ ] **4. TOC links still resolve.** For every cross-link target in the
      source that points at a heading anchor (`[See section](#heading-name)`,
      auto-generated TOC `[Section](#section)`, GFM `[link]: #anchor`
      definitions), the corresponding anchor in the target document
      resolves to a translated heading. The Layer 5 reassembler computes
      the new anchor from the translated heading slug (lowercased,
      whitespace → `-`, special chars stripped per GFM rules) and rewrites
      cross-links to point at it. This check verifies every source anchor
      has a target match — a stale `#getting-started` pointing at a
      heading now slugged as `#はじめに` ships a broken doc. Halt with the
      list of unresolved anchors.

- [ ] **5. Mermaid diagrams unchanged.** Every fenced ` ```mermaid ` block
      in the target is byte-identical to its source counterpart. Mermaid
      node labels (`A[User] --> B[API]`) are explicitly NOT localised in
      v0.1 — the LLM cannot reliably modify diagram source without
      breaking the diagram (label-syntax characters like `[`, `]`, `(`,
      `)`, `{`, `}` carry structural meaning that LLMs hallucinate edits
      to). Diagram label localisation is a manual downstream task if the
      project wants it. Halt on any byte-level diff.

- [ ] **6. ASCII diagrams unchanged.** Any fenced code block with no
      language tag, with `text`, with `ascii`, or any indented code block
      that contains box-drawing characters (`─`, `│`, `┌`, `┐`, `└`, `┘`,
      `├`, `┤`, `┬`, `┴`, `┼`) or ASCII-art alignment (`+--+`, `|  |`,
      `\\`, `/`) is byte-identical to the source. ASCII art preserves its
      visual layout only when whitespace and alignment characters are
      exact; translating inline labels would shift columns and break the
      diagram. Same v0.1 non-goal as item 5: label localisation is manual
      if needed. Halt on byte-level diff.

## When to run

| Step | Items |
|---|---|
| Immediately after Layer 5 reassemble, before emit | 1, 2, 3, 4, 5, 6 |

All six items run in one pass after the AST is reassembled — none of them
require a separate LLM call.

## What this checklist does NOT cover

- **Placeholder count parity** — that's M1 (`references/verification-gates.md` §M1).
  M1 runs before this checklist; if M1 fails the run halts before reassemble,
  so this checklist never sees a placeholder-count mismatch.
- **Project glossary compliance** — that's M2.
- **Translation quality** — that's the 4D reflection axes
  (`references/4d-reflection.md`) and the S1 / S2 SHOULD gates.
- **Frontmatter YAML well-formedness** — the AST parser owns this; a
  malformed frontmatter halts at Layer 2 step 1 before any translation
  happens.
- **MDX-specific JSX expressions** — v0.1 treats MDX as markdown + HTML
  blocks (per `protocols/markdown-ast-protect.md` §"What is NOT covered
  here"); JSX-aware checks deferred to v0.2.

## See also

- `protocols/markdown-ast-protect.md` — owns items 1, 2, 5, 6 by construction
  (the protect-pass guarantees opacity; this checklist verifies)
- `references/verification-gates.md` §M1 / §M2 — placeholder + glossary
  gates that run before this checklist
- `references/audit-trail-spec.md` — where checklist results are recorded
  on a halt
