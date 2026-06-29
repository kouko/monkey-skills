---
name: obsidian-markdown
description: |
  Create and edit Obsidian Flavored Markdown — wikilinks, embeds, callouts, properties, and other Obsidian syntax. Use when working with .md files in Obsidian, or when the user mentions wikilinks, callouts, frontmatter, tags, or embeds.
---

# Obsidian Flavored Markdown Skill

Create and edit valid Obsidian Flavored Markdown. Obsidian extends CommonMark and GFM with wikilinks, embeds, callouts, properties, comments, and other syntax. This skill covers only Obsidian-specific extensions -- standard Markdown (headings, bold, italic, lists, quotes, code blocks, tables) is assumed knowledge.

## Workflow: Creating an Obsidian Note

1. **Add frontmatter** with properties (title, tags, aliases) at the top of the file. See [PROPERTIES.md](references/PROPERTIES.md) for all property types.
2. **Write content** using standard Markdown for structure, plus Obsidian-specific syntax below.
   - Each time the note needs a **diagram**, read [mermaid-quirks.md](references/mermaid-quirks.md) and check §Diagrams for whether to invoke `obsidian:obsidian-mermaid-visualizer` or write inline. Repeat for every diagram in the note — inline and delegate decisions are made per diagram, not per note.
3. **Consider a Table of Contents** for longer notes with multiple sections. Use `[[#Heading]]` wikilinks listed after the first heading.
4. **Link related notes** using wikilinks (`[[Note]]`) for internal vault connections that **already exist** (see §Internal Links for the existence rule), or standard Markdown links for external URLs.
5. **Embed content** from other notes, images, or PDFs using the `![[embed]]` syntax. See [EMBEDS.md](references/EMBEDS.md) for all embed types.
6. **Add callouts** for highlighted information using `> [!type]` syntax. See [CALLOUTS.md](references/CALLOUTS.md) for all callout types.
7. **Verify** the note renders correctly in Obsidian's reading view.

> When choosing between wikilinks and Markdown links: use `[[wikilinks]]` for notes within the vault (Obsidian tracks renames automatically) and `[text](url)` for external URLs only. Emit a `[[wikilink]]` only for a note that already exists (§Internal Links); otherwise write the term as plain bold text.

## Properties (Frontmatter)

```yaml
---
title: My Note
date: 2024-01-15
tags:
  - project
  - active
aliases:
  - Alternative Name
cssclasses:
  - custom-class
---
```

Default properties: `tags` (searchable labels), `aliases` (alternative note names for link suggestions), `cssclasses` (CSS classes for styling).

See [PROPERTIES.md](references/PROPERTIES.md) for all property types, tag syntax rules, and advanced usage.

## Tags

```markdown
#tag                    Inline tag
#nested/tag             Nested tag with hierarchy
```

Tags can contain letters, numbers (not first character), underscores, hyphens, and forward slashes. Tags can also be defined in frontmatter under the `tags` property.

## Table of Contents

For longer notes with multiple sections, consider adding a TOC after the first heading using `[[#Heading]]` wikilinks:

```markdown
## Table of Contents

- [[#Overview]]
- [[#Implementation]]
- [[#Results]]
- [[#References]]
```

Place the TOC immediately after the top-level `# Heading`, before the body content.

## Internal Links (Wikilinks)

```markdown
[[Note Name]]                          Link to note
[[Note Name|Display Text]]             Custom display text
[[Note Name#Heading]]                  Link to heading
[[Note Name#^block-id]]                Link to block
[[#Heading in same note]]              Same-note heading link
```

> **Only emit `[[Target]]` when `Target` already resolves to an existing note in the vault** (bare-basename match, including frontmatter aliases). Otherwise write the term as plain bold text (`**Target**`) with its relationship reason. Never emit a wikilink solely to create a placeholder note.
>
> Before emitting a `[[link]]`, verify the note exists — Glob/search the vault for the bare basename (and any frontmatter `aliases`) first. This is a behavioral check, not a scripted gate. If the vault is not accessible in your current context, default to the plain-text `**Target**` form rather than guessing.
>
> **Exempt:** same-note `[[#Heading]]`, `[[#^block]]`, and same-note Table-of-Contents links always resolve and are exempt from this rule.

Define a block ID by appending `^block-id` to any paragraph:

```markdown
This paragraph can be linked to. ^my-block-id
```

For lists and quotes, place the block ID on a separate line after the block:

```markdown
> A quote block

^quote-id
```

## Embeds

Prefix any wikilink with `!` to embed its content inline:

```markdown
![[Note Name]]                         Embed full note
![[Note Name#Heading]]                 Embed section
![[image.png]]                         Embed image
![[image.png|300]]                     Embed image with width
![[document.pdf#page=3]]               Embed PDF page
```

See [EMBEDS.md](references/EMBEDS.md) for audio, video, search embeds, and external images.

## Callouts

```markdown
> [!note]
> Basic callout.

> [!warning] Custom Title
> Callout with a custom title.

> [!faq]- Collapsed by default
> Foldable callout (- collapsed, + expanded).
```

Common types: `note`, `tip`, `warning`, `info`, `example`, `quote`, `bug`, `danger`, `success`, `failure`, `question`, `abstract`, `todo`.

See [CALLOUTS.md](references/CALLOUTS.md) for the full list with aliases, nesting, and custom CSS callouts.

## Comments

```markdown
This is visible %%but this is hidden%% text.

%%
This entire block is hidden in reading view.
%%
```

## Obsidian-Specific Formatting

```markdown
==Highlighted text==                   Highlight syntax
```

## Math (LaTeX)

```markdown
Inline: $e^{i\pi} + 1 = 0$

Block:
$$
\frac{a}{b} = c
$$
```

## Diagrams (Mermaid)

**Before writing any Mermaid block:** read [mermaid-quirks.md](references/mermaid-quirks.md) and run its pre-flight checklist.

### When to invoke `obsidian:obsidian-mermaid-visualizer`

Delegate to the visualizer when **any** of the following is true:

1. **Non-flowchart type** — the diagram is not a plain directional flow. This covers:
   `sequenceDiagram`, `stateDiagram-v2`, `erDiagram`, `classDiagram`, `C4Context` (and C4 variants),
   `gitGraph`, `gantt`, `timeline`, `mindmap`, `xychart-beta`, `pie`, `quadrant-chart`,
   `architecture-beta`, `block-beta` — anything other than `flowchart` / `graph`.

2. **Ambiguous type** — content could plausibly map to two or more diagram types
   (e.g. "process with states" → flowchart vs stateDiagram; "actors over time" → flowchart vs sequence).

3. **Complex flowchart** — would have more than ~6 nodes, or involves subgraphs
   or multi-level nesting.

4. **Data visualization** — encodes numeric data, proportions, or 2×2 positioning.

### When to write Mermaid inline

Write inline (without invoking the visualizer) only when **all** of the following hold:

- Clearly a `flowchart` / `graph` type — simple directional flow or decision tree
- ≤ 6 nodes, no subgraphs
- Special characters (`"`, `()`, `#`) in labels have already been substituted per Rule 6 of mermaid-quirks — `()` → `「」`, `"` → `『』`, `#` → `&#35;`
- Already read [mermaid-quirks.md](references/mermaid-quirks.md) and the pre-flight checklist is complete

### Obsidian-note links in Mermaid

To link a Mermaid node to an Obsidian note, add `class NodeName internal-link;`. Mention this requirement when invoking the visualizer, or apply it manually when writing inline.

## Footnotes

```markdown
Text with a footnote[^1].

[^1]: Footnote content.

Inline footnote.^[This is inline.]
```

## Complete Example

*The `[[wikilinks]]` below assume their target notes already exist in the vault (per §Internal Links). When authoring for real, link only notes that exist; otherwise write the term as plain bold text.*

````markdown
---
title: Project Alpha
date: 2024-01-15
tags:
  - project
  - active
status: in-progress
---

# Project Alpha

## Table of Contents

- [[#Tasks]]
- [[#Notes]]

This project builds on [[Project Planning]] using modern techniques.

> [!important] Key Deadline
> The first milestone is due on ==January 30th==.

## Tasks

- [x] Initial planning
- [ ] Development phase
  - [ ] Backend implementation
  - [ ] Frontend design

## Notes

The algorithm uses $O(n \log n)$ sorting. See [[Algorithm Notes#Sorting]] for details.

![[Architecture Diagram.png|600]]

Reviewed in [[Meeting Notes 2024-01-10#Decisions]].
````

## References

- [Obsidian Flavored Markdown](https://help.obsidian.md/obsidian-flavored-markdown)
- [Internal links](https://help.obsidian.md/links)
- [Embed files](https://help.obsidian.md/embeds)
- [Callouts](https://help.obsidian.md/callouts)
- [Properties](https://help.obsidian.md/properties)
