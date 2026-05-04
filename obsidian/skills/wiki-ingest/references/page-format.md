# Wiki Page Format Specification

**Authoritative spec** for all pages generated under `wiki/`. This file is owned by `wiki-ingest`. Other skills (`wiki-lint`, `wiki-cross-linker`, `wiki-auto-research`) reference their own copies of the relevant fragments — do not cross-link to this file.

## Frontmatter (8 fields, all required)

```yaml
---
title: "Page Title (human-readable, can include CJK)"
type: wiki-entity                   # wiki-entity | wiki-concept | wiki-synthesis
domain: finance                     # finance | ai | dev | economy | design
status: seed                        # seed | developing | mature | archived
updated: YYYY-MM-DD                 # ISO date, latest ingest touching this page
tags:
  - tag1
  - tag2                            # 1+ tags, free vocabulary
sources_count: N                    # cumulative count, increments on each ingest
summary: "≤200 chars single-line summary used by tiered retrieval"
---
```

### Field rules

| Field | Constraint |
|---|---|
| `title` | Quoted string, can contain CJK / spaces / colons |
| `type` | One of `wiki-entity`, `wiki-concept`, `wiki-synthesis`. **Skill, journal, reference pages use their own type values** (see below) |
| `domain` | Lowercase, single value, free vocabulary (suggested: `finance`, `ai`, `dev`, `economy`, `design`) |
| `status` | Lifecycle: `seed` (just born) → `developing` (multiple sources, gaps) → `mature` (well-cited, stable) → `archived` (superseded) |
| `updated` | ISO date `YYYY-MM-DD`. Update on every ingest touching the page |
| `tags` | YAML list, lowercase-kebab-case preferred |
| `sources_count` | Integer, increments by 1 each time a new source contributes |
| `summary` | **≤200 characters**, single line, no markdown. Used by `wiki-query` tiered retrieval to avoid loading full pages |

### Type-specific frontmatter for non-entity/concept pages

- **Skills pages** (`wiki/skills/*.md`): `type: wiki-skill`
- **Journal pages** (`wiki/journal/*.md`): `type: wiki-journal`, add `date: YYYY-MM-DD`
- **Reference pages** (`wiki/references/*.md`): `type: wiki-reference`, add `source_path: <vault-relative path of original>`, `contributes_to: [list of wiki page links]`

## Body Structure (3 Required + 2 Conditional)

### Required sections

```markdown
## Summary
(2–4 sentences) What this entity/concept is, why it matters, current status.
End with confidence: high | medium | unverified.

## Key Facts
- Bullet list, 3–10 verifiable facts or data points
- Each bullet is a single self-contained claim
- Use provenance markers at end of bullet:
  - (no marker) = directly cited from source
  - ^[inferred] = LLM-synthesized from multiple sources
  - ^[ambiguous] = sources disagree or evidence weak

## Connections
- [[OtherWikiPage]] — one-line reason for the link
- At least 1 [[wikilink]] required
- Link reason is mandatory (forces semantic linking, not symbolic)
```

### Conditional sections

```markdown
## Contradictions
<!-- Trigger: sources contain mutually exclusive claims -->
- Source A says X; Source B says Y. Conflict point: ...
- Mark unresolved with `[!warning]` callout if material

## Open Questions
<!-- Trigger: identified-but-unanswered questions -->
- Concrete question (will be picked up by wiki-auto-research)
- Optionally tagged with priority: (high) (medium) (low)
```

### Optional sections (free addition)

| Section | When to use |
|---|---|
| `## Mermaid Diagram` | **Synthesis pages only.** Entity/concept pages do not require diagrams |
| `## Sources` | Reference list at bottom, links to `wiki/references/<source>.md` pages |
| `## Event Log` | Time-stamped material updates (was previously `last_verified` frontmatter) |

## Conventions

| Rule | Spec |
|---|---|
| **Wikilinks** | `[[filename-slug]]` — bare filename only, NO subfolder path, NO `.md` extension. Obsidian-idiomatic shortest-link form |
| **Callouts** | `[!important]` for Summary key insight; `[!warning]` for unresolved contradiction; `[!note]` for nuances |
| **Provenance markers** | `^[inferred]` and `^[ambiguous]` go at the **end of a Key Facts bullet**, not inline |
| **Mermaid** | Only on `wiki-synthesis` pages |
| **Tables** | Markdown tables OK in any section; prefer over long bulleted comparisons |
| **Code blocks** | Use language hints; quote source provenance in caption when from a specific source |

## Filename rules

- **Globally unique within `wiki/`** — filenames MUST be unique across all 6 subfolders (`entities/`, `concepts/`, `synthesis/`, `skills/`, `journal/`, `references/`). This is a hard requirement because wikilinks are bare filenames; collisions break linking.
- ASCII-safe filenames preferred for wikilink stability: `MAB-bandit-algorithms.md` not `多臂老虎機.md`
- Dashes between words, not underscores or camelCase
- Reference pages: `YYYY-MM-DD-<slug>.md` (date-prefixed for ordering, naturally unique)
- Journal pages: `YYYY-MM-DD-<slug>.md` (date-prefixed, naturally unique)
- Entity / concept / synthesis / skill pages: when boundary is ambiguous and a name is taken, disambiguate with a qualifier suffix (e.g., `qlib-microsoft.md` vs `qlib-language.md`), not by adding a path prefix to the wikilink.

## Wikilink resolution

All wikilinks use **bare filename without `.md`**:

```markdown
✅ [[Thompson-Sampling]]                  — entity
✅ [[exploration-exploitation]]           — concept
✅ [[2026-04-20-台積電財報]]                — reference (date-prefixed)
✅ [[MAB-quant-trading-landscape]]        — synthesis
❌ [[entities/Thompson-Sampling]]         — path prefix forbidden
❌ [[Thompson-Sampling.md]]               — extension forbidden
❌ [[/wiki/entities/Thompson-Sampling]]   — absolute path forbidden
```

Rationale: Obsidian's "shortest path that is unambiguous" link style; pages may be reclassified across subfolders without breaking inbound links.

### NEVER wrap wikilinks in backticks (critical)

Markdown's code-span precedence eats the wikilink syntax. Backticked wikilinks render as gray inline code, NOT as clickable links:

```markdown
❌ `[[Thompson-Sampling]]`             — renders as inline code, NOT a link
❌ **`[[Thompson-Sampling]]`**         — bold + inline code, still NOT a link
❌ `**[[Thompson-Sampling]]**`         — same: code-span eats everything inside
✅ [[Thompson-Sampling]]               — clickable wikilink
✅ **[[Thompson-Sampling]]**           — bold + clickable wikilink
✅ *[[Thompson-Sampling]]*             — italic + clickable wikilink
```

Why: in Obsidian's markdown parser (and CommonMark generally), code spans `` `...` `` are tokenized BEFORE wikilinks. The text inside backticks becomes a single inline-code node, never reaching the wikilink parser. Bold / italic do not have this problem because they don't tokenize their content as opaque text.

### Common contexts — list / table / callout

Wikilinks inside structural elements still resolve correctly **as long as no backticks wrap them**:

```markdown
✅ List item with bold wikilink:
- **[[Thompson-Sampling]]** — Bayesian MAB algorithm

❌ Same list item with backticks (the original production bug):
- **`[[Thompson-Sampling]]`** — renders as gray inline code, no link

✅ Table cell:
| Algorithm | Implementation |
|---|---|
| MAB | [[Thompson-Sampling]] |

❌ Table cell with backticks:
| Algorithm | Implementation |
|---|---|
| MAB | `[[Thompson-Sampling]]` |

✅ Callout body:
> [!note] Related entity
> See [[Thompson-Sampling]] for the algorithm baseline.

❌ Callout body with backticks:
> [!note] Related entity
> See `[[Thompson-Sampling]]` for the algorithm baseline.
```

### Adjacent backticks are fine — only wrapping breaks

Backticks placed **next to** a wikilink (not around it) are valid. This is common when citing a code symbol alongside its concept page:

```markdown
✅ Adjacent code reference (allowed):
- [[qlib]] — the `qlib.workflow.cli` entry point handles config loading
- See [[Thompson-Sampling]] (`scipy.stats.beta.rvs` under the hood)

❌ Wikilink wrapped in backticks (not allowed):
- `[[qlib]]` — broken, renders as inline code
```

The rule: backticks must NOT contain `[[ ... ]]` syntax. Backticks before, after, or in adjacent words are fine.

### Adjacent symbols and multiple wikilinks

```markdown
✅ Emoji / arrow prefixes work:
- 🔗 [[Thompson-Sampling]]
- → [[exploration-exploitation]]
- ⚠️ [[Magnificent-Seven]] (concentration risk)

✅ Multiple consecutive wikilinks (space- or comma-separated):
See [[Thompson-Sampling]] [[UCB]] [[epsilon-greedy]] for MAB algorithm baselines.
See [[Thompson-Sampling]], [[UCB]], and [[epsilon-greedy]].

✅ Wikilinks in inline prose:
The [[Thompson-Sampling]] approach outperforms [[UCB]] in non-stationary environments.
```

### Obsidian-specific syntax — alias, anchor, embed

Obsidian extends `[[...]]` with three optional features. Use them when needed:

```markdown
✅ Alias (display text overrides filename):
[[Thompson-Sampling|the Bayesian MAB approach]]
[[2026-04-20-台積電財報|TSMC Q1 earnings]]
   ↑ Useful for inline prose where the filename slug reads awkwardly

✅ Anchor (link to a specific heading within the page):
[[Thompson-Sampling#Algorithm details]]
[[Magnificent-Seven#Concentration risk]]
   ↑ Useful for cross-referencing a specific section

✅ Combined alias + anchor:
[[Thompson-Sampling#Algorithm details|see the algorithm section]]

✅ Embed (transclusion — renders the linked page inline; rare in wiki/):
![[Thompson-Sampling]]
![[Thompson-Sampling#Algorithm details]]
   ↑ Note the leading `!` — embeds the content rather than linking
   ↑ Use sparingly; pages should self-contain rather than transclude

❌ All the above with backticks still fail:
`[[Thompson-Sampling|alias]]`              — inline code, not a link
`[[Thompson-Sampling#Section]]`            — same
`![[Thompson-Sampling]]`                   — same; backticks beat embed too
```

### Coverage summary

The rule "no backticks **around** a wikilink" applies in **every** context:

| Context | Wrap rule | Examples covered above |
|---|---|---|
| Body prose | ❌ no backticks around `[[...]]` | `[[Page]]`, `**[[Page]]**`, `*[[Page]]*` |
| List items | ❌ same | `- [[Page]] — ...`, `- **[[Page]]** — ...` |
| Table cells | ❌ same | `\| [[Page]] \|` |
| Callout body | ❌ same | `> See [[Page]] for ...` |
| Adjacent code | ✅ backticks NOT around link OK | `` [[Page]] (`field-name`) `` |
| Emoji / symbol prefix | ✅ OK | `🔗 [[Page]]`, `→ [[Page]]` |
| Multiple links | ✅ OK | `[[A]] [[B]]`, `[[A]], [[B]]` |
| Alias | ✅ OK (without backticks) | `[[Page\|display text]]` |
| Anchor | ✅ OK (without backticks) | `[[Page#Section]]` |
| Embed | ✅ OK (without backticks) | `![[Page]]` |

Common offender pattern: emphasizing a wikilink with backticks for "code-style" appearance. **Don't.** Use bold or italic instead, or leave it plain.

## Tiered retrieval contract (consumer-facing)

`wiki-query` reads in order:
1. `wiki/hot.md` — session cache (≤300 chars)
2. `frontmatter.summary` only — across all matching pages (≤200 chars each)
3. Full page body — only after 1 and 2 are insufficient

Consequence: **`summary` MUST be self-contained**. Do not write summaries that depend on body context.

## Sources block convention

When a page cites references, append:

```markdown
## Sources
- [[2026-04-20-台積電財報]] — Q1 CoWoS data
- [[2026-04-15-MAB-survey-paper]] — algorithm taxonomy
```

`wiki-ingest` is responsible for:
1. Creating the `wiki/references/<filename>.md` page on first encounter of a source
2. Updating that reference page's `contributes_to:` list
3. Appending the link in the consuming page's `## Sources` block

## What NOT to do

- ❌ Embed full paragraphs from sources verbatim (copyright, dilution of synthesized value)
- ❌ Use 9+ body sections (the legacy SCHEMA failure mode this spec corrects)
- ❌ Skip `summary` frontmatter (breaks tiered retrieval)
- ❌ Use absolute paths in wikilinks
- ❌ Mark inferred claims as direct citations (provenance integrity)
- ❌ Write Mermaid in entity/concept pages (clutter; reserve for synthesis)
