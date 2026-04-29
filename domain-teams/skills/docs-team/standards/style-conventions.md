# Style Conventions (Shared Standard)

Prose style rules for docs-team. All terms trace to Google Developer Documentation
Style Guide (primary) and Microsoft Writing Style Guide (secondary), with a
reader-first philosophical preamble from the Japanese technical writing tradition.

Primary sources:
- [Google Developer Documentation Style Guide](https://developers.google.com/style) (CC BY 3.0)
- [Microsoft Writing Style Guide](https://learn.microsoft.com/en-us/style-guide/welcome/)
- [JTAP 技術文書 3 原則](https://www.jtapco.co.jp/training-02) (reader-first principle)

## Reader-First Principle (読み手優先の原則)

Before applying any style rule, recognize the asymmetry between writer and reader.
The writer knows the intent; the reader starts from zero.

As formulated by the Japanese technical writing tradition (JTAP 技術文書 3 原則):

> **第 1 原則**: 書き手と読み手の違いを認識する
> *"Recognize the difference between writer and reader"*

This principle sits above all Google/Microsoft style rules. Those mechanical
rules exist because they systematically reduce the writer-reader gap. When in
doubt about a style choice, ask:

> Does this narrow the gap my reader faces, or does it only serve my convenience as the writer?

If the answer favors writer convenience, rewrite.

## Primary Style: Google Developer Documentation Style Guide

### Voice and Grammar

- **Active voice** — "The compiler reports an error" not "An error is reported by the compiler"
- **Second person** — "you" not "we" or "the user"
- **Present tense** — "The function returns" not "The function will return" or "returned"
- **Conversational but not frivolous** — friendly, professional, never jokey

### Capitalization and Punctuation

- **Sentence case** for titles and headings — "Write a tutorial" not "Write A Tutorial"
- **Serial comma** (Oxford comma) in all lists — "apples, oranges, and bananas"
- **One space** after periods
- **No periods** on titles, headings, or short list items
- **Standard American spelling** and punctuation

### Formatting

- **Numbered lists** for sequential steps where order matters
- **Bulleted lists** for non-sequential items
- **Code font** for code, commands, file names, literal text
- **Bold** for UI elements (button names, menu items)
- **Descriptive link text** — "See the [installation guide]" not "Click [here]"
- Place **conditional statements before instructions** — "If X, then do Y" not "Do Y if X"

### Accessibility

- **Alt text** for all images
- **No directional language** ("above", "below") — use "preceding" or explicit references
- **Consider a global audience** — avoid idioms, cultural references, assumed knowledge

## Secondary Style: Microsoft Writing Style Guide

Microsoft's style overlaps heavily with Google but optimizes for consumer-friendly
voice. Use Microsoft's **Top 10 tips** as a quick-reference checklist:

1. **Bigger ideas, fewer words** — "Shorter is always better"
2. **Write like you speak** — read it aloud; avoid jargon
3. **Project friendliness** — use contractions ("it's", "you'll", "we're")
4. **Get to the point fast** — front-load keywords for scanning
5. **Be brief** — prune every excess word
6. **When in doubt, don't capitalize** — default to sentence case
7. **Skip periods** on titles, headings, short list items
8. **Remember the last comma** — Oxford comma required
9. **Don't be spacey** — one space after periods
10. **Revise weak writing** — start with verbs; cut "you can" and "there is/are"

Microsoft's overarching mantra: **"Above all, simple and human."**

### When to prefer Microsoft over Google
- **Consumer-facing docs** (onboarding flows, error messages, release notes) where
  a warmer tone matters more than developer terseness
- **Short-form content** (tooltips, button labels) where Microsoft's Top 10 is faster to apply

### When to prefer Google over Microsoft
- **Developer reference** (API docs, CLI docs, config schemas) where
  rule-driven consistency matters more than voice
- **Long-form technical explanation** where Google's rule-driven discipline
  prevents voice drift

## Filename and Structural Conventions

### Filenames
- **Kebab-case** for Markdown files: `write-tutorial.md`, not `writeTutorial.md` or `Write_Tutorial.md`
- **Descriptive** — the filename should reveal the content, not be `doc1.md`
- **Stable** — renames break inbound links; prefer an aliases frontmatter field over rename

### Heading hierarchy
- **One H1 per file** — the document title
- **No skipped levels** — H2 follows H1, not H3
- **Sentence case** headings throughout
- **Parallel structure** in sibling headings — all imperative, or all noun phrases, not mixed

### Link text
- **Descriptive** — "See the installation guide" not "Click here"
- **Within sentence flow** — integrate the link into the sentence, don't dump a bare URL

## What to Avoid

- Passive voice when the actor matters
- First person plural ("we", "us") except in Explanation mode discussing design
- Future tense for current behavior
- Title Case In Headings
- Jargon without definition
- Idioms, cultural references, humor that doesn't translate
- "Simply", "just", "easy" — these minimize reader difficulty and alienate beginners
- "Please" before instructions — it's noise in technical docs

## Mechanical Enforcement

Most of these rules can be enforced with linting tools, but docs-team evaluates
them via the **Style Convention SHOULD gate** (`rubrics/style.md`)
which uses judgment-based scoring because we cannot run Vale or markdownlint
inside Claude Code.

When these rules would produce false positives in context (e.g., legitimate
passive voice when the actor is unknown), the SHOULD gate allows skipping with
a stated reason.

## Sources

- [Google Developer Documentation Style Guide](https://developers.google.com/style) — primary
- [Google Style Highlights](https://developers.google.com/style/highlights) — quick reference
- [Google Style Voice](https://developers.google.com/style/voice) — tense and voice rules
- [Microsoft Writing Style Guide welcome](https://learn.microsoft.com/en-us/style-guide/welcome/) — secondary
- [Microsoft Top 10 tips for style and voice](https://learn.microsoft.com/en-us/style-guide/top-10-tips-style-voice) — quick checklist
- [JTAP 技術文書 3 原則と 6 つのルール](https://www.jtapco.co.jp/training-02) — reader-first philosophical preamble
