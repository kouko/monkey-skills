# Markdown AST Protect — markdown-specific patterns

> **Base spec**: `references/protect-pass-spec.md` (functional copy of the canonical
> `scripts/canonical/protect-pass-spec.md`). Read that first — it defines the
> `⟦P:NN⟧` token format, the 8 base classes (ICU plural, curly braces, printf,
> fenced code, inline code, HTML, URL, email), the priority-order overlap
> rules, and the M1 count-parity check.
>
> This protocol layers **markdown-specific patterns on top** of the base classes.
> It does NOT replace the base spec — it adds patterns that only show up in
> markdown / MDX payloads, and clarifies how the base classes apply when the
> source is parsed as a markdown AST.

## Pattern stack — when this protocol applies

Markdown AST parse runs first (Layer 2 step 1). The AST splits the source
into block-level nodes (paragraph, heading, code, table, list, html-block,
math-block, frontmatter) and inline-level nodes (text, code, link, html,
math). The base protect-pass then runs over each prose region (paragraph
text, heading text, list-item text, table-cell text). Markdown-specific
extensions below add new spans the base classes don't cover.

Same priority-ordered overlap model as the base spec: earlier patterns win on
overlap, longer / outer spans win on containment.

## Markdown-specific patterns

### 1. Code blocks — fenced + indented, ENTIRE block is one token

Fenced code blocks (``` ```lang … ``` ```) and indented code blocks (4-space
or 1-tab indent, blank line above) are masked **entire** as a single token.
The base spec's P-class 4 (fenced code) covers fenced; this extension adds
indented code under the same class.

```
SOURCE   :
    Header text.

        def foo():
            pass

    More text.

MASKED   :
    Header text.

    ⟦P:01⟧

    More text.

TOKEN MAP: { ⟦P:01⟧: "    def foo():\n        pass" }
```

Inline code (`` `npm install` ``) is the base spec's P-class 5 — masked
per-span, not part of the surrounding code-block span.

The LLM never sees code-block contents; round-trip is byte-identical. This
is the strongest preservation guarantee in the skill — code-block content
modification is impossible by construction, not by gate.

### 2. URLs — markdown link syntax, bare URLs, reference-style

Markdown link syntax `[text](url)` is split into two protected zones and a
translatable middle:

```
SOURCE   : 'See [the docs](https://example.com/guide) for details.'
MASKED   : 'See ⟦P:01⟧the docs⟦P:02⟧ for details.'
TOKEN MAP:
  ⟦P:01⟧: '['
  ⟦P:02⟧: '](https://example.com/guide)'
```

The link **text** (`the docs`) remains translatable prose between the two
tokens. The opening `[` and the closing `](url)` are each one token. The
URL is owned by the closing token's span — there is no separate URL token
for it (containment rule).

Bare URLs (no markdown link wrapper) are the base spec's P-class 7:

```
SOURCE   : 'See https://example.com/guide for details.'
MASKED   : 'See ⟦P:01⟧ for details.'
TOKEN MAP: { ⟦P:01⟧: 'https://example.com/guide' }
```

Reference-style links use a label + a definition. Both the label-bearing
inline span and the definition line are tokenised:

```
SOURCE   :
    See [the docs][guide] for details.

    [guide]: https://example.com/guide

MASKED   :
    See ⟦P:01⟧the docs⟦P:02⟧ for details.

    ⟦P:03⟧

TOKEN MAP:
  ⟦P:01⟧: '['
  ⟦P:02⟧: '][guide]'
  ⟦P:03⟧: '[guide]: https://example.com/guide'
```

The label `guide` and the definition target are both opaque to the LLM;
only the link text translates. Numeric labels (`[1]`) work the same way.

### 3. HTML — base class for inline tags, block-level extension for `<div>`-class blocks

The base spec's P-class 6 handles inline HTML tags (`<a>`, `<br/>`, etc.) —
those work identically inside markdown. Markdown additionally recognises
**HTML blocks**: a multi-line region starting with a block-level tag
(`<div>`, `<table>`, `<details>`, etc.) at column zero. The markdown AST
treats the entire block as raw HTML and excludes it from prose parsing.

This protocol masks HTML blocks **entire** as a single token (parallel to
fenced code), not as an open-tag + middle + close-tag triple:

```
SOURCE   :
    Heading text.

    <details>
      <summary>Click to expand</summary>
      <p>Hidden content here.</p>
    </details>

    Tail text.

MASKED   :
    Heading text.

    ⟦P:01⟧

    Tail text.

TOKEN MAP: { ⟦P:01⟧: "<details>\n  <summary>Click to expand</summary>\n  <p>Hidden content here.</p>\n</details>" }
```

Rationale: localising the inner content of an HTML block requires HTML-aware
translation that breaks the AST contract; defer to a manual second pass if
the project actually wants that content translated. v0.1 chooses safety
over reach.

Inline HTML inside prose paragraphs (`<kbd>Ctrl</kbd>`) stays under the base
P-class 6 rules — the kbd content `Ctrl` does NOT translate inside the
opaque tag span.

### 4. Math blocks — LaTeX `$$…$$` and `$…$`, ENTIRE span masked

Display math (`$$ … $$`, may span multiple lines) and inline math (`$ … $`)
are masked entire. LLMs cannot reliably modify equations and any change is
silently wrong; never expose math to the WRITER.

```
SOURCE   : 'The formula $E = mc^2$ describes mass-energy equivalence.'
MASKED   : 'The formula ⟦P:01⟧ describes mass-energy equivalence.'
TOKEN MAP: { ⟦P:01⟧: '$E = mc^2$' }
```

```
SOURCE   :
    The Schrödinger equation:

    $$
    i\hbar \frac{\partial}{\partial t} \Psi = \hat{H} \Psi
    $$

    governs quantum evolution.

MASKED   :
    The Schrödinger equation:

    ⟦P:01⟧

    governs quantum evolution.

TOKEN MAP: { ⟦P:01⟧: "$$\ni\\hbar \\frac{\\partial}{\\partial t} \\Psi = \\hat{H} \\Psi\n$$" }
```

Inline `$…$` parsing is heuristic — a bare `$` in financial prose
(`$5 to $10`) is NOT math. The AST parser uses standard CommonMark + GFM
math extension rules: `$…$` is math only when both delimiters have non-
whitespace adjacent characters and no whitespace immediately inside. False
positives surface as "math token contains prose" warnings on M1.

### 5. Frontmatter YAML — body masked, optional prose-field selective translation

Markdown frontmatter is a `---\n…\n---` block at file start (line 1).
The body is YAML; arbitrary YAML structure is opaque to the translator.

**Default behavior**: mask the entire frontmatter block as one token —
preserves byte-identical YAML, including key order, comments, and quoting.

```
SOURCE   :
    ---
    title: Getting Started
    description: A short guide.
    tags: [tutorial, intro]
    ---

    # Welcome

    Body prose here.

MASKED   :
    ⟦P:01⟧

    # Welcome

    Body prose here.

TOKEN MAP: { ⟦P:01⟧: "---\ntitle: Getting Started\ndescription: A short guide.\ntags: [tutorial, intro]\n---" }
```

**Opt-in selective translation**: when the intake-spec lists prose-bearing
frontmatter fields (commonly `title`, `description`, `summary`), the AST
parser extracts those values, hands them through the prose pipeline, and
the Layer 5 reassembler patches the translated values back into the
frontmatter YAML. Other YAML keys remain untouched.

```yaml
# intake-spec hint
frontmatter_translate_fields: [title, description]
```

After translation:

```
RESTORED :
    ---
    title: はじめに
    description: 簡単なガイドです。
    tags: [tutorial, intro]
    ---

    # ようこそ

    本文プローズはここに。
```

`tags`, `slug`, `date`, `layout`, and any field not on the opt-in list stay
byte-identical.

### 6. Mermaid + ASCII diagrams — fenced code with special lang, ENTIRE block masked

Mermaid diagrams are fenced with ` ```mermaid `; ASCII art / box-drawing
diagrams typically appear in a fenced block with no language tag, with
`text`, with `ascii`, or as an indented code block. **All such blocks are
masked entire** under the same rule as code blocks (P-class 4 / extension
1 above).

```
SOURCE   :
    Architecture overview:

    ```mermaid
    flowchart LR
      A[User] --> B[API]
      B --> C[(DB)]
    ```

    See the diagram above.

MASKED   :
    Architecture overview:

    ⟦P:01⟧

    See the diagram above.

TOKEN MAP: { ⟦P:01⟧: "```mermaid\nflowchart LR\n  A[User] --> B[API]\n  B --> C[(DB)]\n```" }
```

Node labels (`User`, `API`, `DB`) are NOT translated. Mermaid label
localisation requires a separate diagram-aware pass; v0.1 explicitly does
not attempt it (per `checklists/doc-quality-checklist.md` item 5). Same
rule applies to ASCII art: box-drawing characters and inline labels stay
byte-identical.

### 7. Tables — cell content translates, separators preserved

GFM tables: cell text IS translatable prose, but the `|` separators, the
header alignment row (`:---:`), and column boundaries are AST structure
that must round-trip byte-identical.

```
SOURCE   :
    | Step | Action                 |
    |:----:|------------------------|
    | 1    | Install dependencies   |
    | 2    | Run the build          |

MASKED   :
    | Step | Action                 |
    |:----:|------------------------|
    | 1    | Install dependencies   |
    | 2    | Run the build          |
```

Per-cell prose runs through the prose pipeline; the surrounding `|` /
alignment-row scaffolding is reconstructed by the Layer 5 reassembler from
the AST. Cells containing inline code (`` `foo` ``), inline links, or
inline math get the corresponding base-class / extension token applied to
the cell content only.

Tables with multiline cells (HTML `<br>` for line break) follow base
P-class 6 for the `<br>` tag.

### 8. Footnotes / link references — labels preserved, body content translates

GFM footnotes use `[^label]` for the inline reference and `[^label]: …`
for the definition. The label is opaque (preserves cross-reference); the
definition body is translatable prose.

```
SOURCE   :
    See the spec[^1] for details.

    [^1]: The full RFC is at https://example.com/rfc.

MASKED   :
    See the spec⟦P:01⟧ for details.

    ⟦P:02⟧ The full RFC is at ⟦P:03⟧.

TOKEN MAP:
  ⟦P:01⟧: '[^1]'
  ⟦P:02⟧: '[^1]:'
  ⟦P:03⟧: 'https://example.com/rfc'
```

The footnote body (`The full RFC is at …`) translates; the label `[^1]`
and the URL inside it are masked. Same rule applies to numeric (`[^1]`),
named (`[^longnote]`), and inline (`^[footnote text]`) variants.

Heading-anchor cross-links (`[See section](#heading-name)`) follow the URL
rule (extension 2): the `#heading-name` anchor is part of the closing-
token span and is opaque to the LLM. The Layer 5 reassembler is responsible
for updating anchors to match translated heading slugs (covered by
`checklists/doc-quality-checklist.md` item 4).

## Order of operations (markdown)

Per Layer 2 of `SKILL.md`:

1. **Markdown AST parse** (Layer 2 step 1) — split block + inline nodes;
   identify code, math, html-block, frontmatter, mermaid / diagram, tables,
   footnotes. Hands per-node prose strings to protect-pass.
2. **Protect-pass** (Layer 2 step 2) — base 8 classes per
   `references/protect-pass-spec.md`, then markdown extensions above.
3. **Source analysis** (Layer 2 step 3) — operates on masked text.
4. **Glossary resolve** (Layer 2 step 4) — operates on masked text.
5. **Core loop** (Layer 3) — DRAFT / REFLECT / IMPROVE see only masked text;
   `<TRANSLATE_THIS>` windowing per chunk.
6. **M1 verification** (Layer 4) — count `⟦P:NN⟧` tokens in v2 vs source.
7. **Restore** (Layer 5 step 1) — swap `⟦P:NN⟧` → original substring.
8. **Reassemble markdown** (Layer 5 step 2) — stitch chunks; preserve AST
   structure; check `checklists/doc-quality-checklist.md` 6 items.

Steps 1, 7, 8 are owned by the AST parser / reassembler. Steps 2-6 are
governed by this protocol + `references/protect-pass-spec.md`.

## What is NOT covered here

- **Per-format i18n placeholders** (ICU plural / Android `<plurals>` / iOS
  `.strings` escapes) — see `translation-i18n/protocols/placeholder-protect.md`.
- **Brand-voice forbidden phrases** — see `translation-creative` (Task D5).
- **Existing-target diff protection in audit-only mode** — see
  `translation-audit` (Task D6).
- **Mermaid / diagram label localisation** — explicit non-goal in v0.1
  (per `checklists/doc-quality-checklist.md` item 5).
- **MDX-specific JSX expressions** (`{props.value}`, `<Component/>`) — v0.1
  treats MDX as markdown + HTML blocks; full JSX-aware protect deferred to
  v0.2 if real MDX corpora surface as a need.

## See also

- `references/protect-pass-spec.md` — canonical 8-class base spec, restoration
  rule, M1 count-parity check, examples.
- `checklists/doc-quality-checklist.md` — 6-item roundtrip check applied
  after Layer 5 reassemble.
- `references/verification-gates.md` §M1 — exact diff format on placeholder
  count mismatch.
- `references/core-loop.md` §5 — `<TRANSLATE_THIS>` cross-chunk windowing
  for long markdown documents.
