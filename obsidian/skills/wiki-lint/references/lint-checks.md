# Wiki Lint — 12 Health Checks

Categorized into **structural** (format violations), **semantic** (content health), and **provenance** (source/citation integrity).

## Structural (format compliance)

### L01 — Frontmatter completeness
Each wiki page must have all 8 required fields. Missing any → **error**.

```
title type domain status updated tags sources_count summary
```

Per-page-type extras (`date` for journal, `source_path` for references) also required.

### L02 — Summary length
`frontmatter.summary` must be ≤200 characters, single line, no markdown. Violations → **error**.

### L03 — Required body sections
Every wiki page must have `## Summary`, `## Key Facts`, `## Connections`. Missing → **error**.

### L04 — Wikilink format
- Wikilinks MUST be **bare filename** form: `[[filename-slug]]`
- Wikilinks MUST NOT have `.md` extension
- Wikilinks MUST NOT include subfolder path prefix (`[[entities/foo]]` is forbidden)
- Wikilinks MUST NOT use absolute paths
- Wikilinks MUST NOT be wrapped in backticks (`` `[[Page]]` `` or `` **`[[Page]]`** `` renders as inline code in Obsidian, NOT a clickable link). Detect via regex: `` `[^`]*\[\[[^\]]+\]\][^`]*` `` (any backtick-bounded span containing a wikilink)

Violations → **error**.

### L05 — Mermaid placement
Mermaid code blocks (` ```mermaid ... ``` `) only allowed in `wiki-synthesis` pages. Found in entity/concept → **warning**.

## Semantic (content health)

### L06 — Orphan pages
A page is orphan if NO other wiki page links to it (`## Connections` of others doesn't reference it, no inline `[[link]]` mentions). Output → **warning** with suggestion: "consider deletion or linking".

Reference pages are exempt (always orphan-by-design until consumed).

### L07 — Broken wikilinks
Build a **filename inventory** by scanning `wiki/{entities,concepts,synthesis,skills,journal,references}/*.md` and stripping `.md`. Each `[[link]]` in any page body must match exactly one entry in this inventory.

- 0 matches → **error** (broken link); suggest closest existing filename (Levenshtein distance ≤2)
- 2+ matches → **error** (filename collision; should have been prevented at ingest by uniqueness check, indicates corruption); list all candidates

Path-prefixed forms (`[[entities/foo]]`) are caught by L04, not L07.

### L08 — Stale pages
Pages with `frontmatter.updated` older than 90 days **and** `status: developing` → **warning** (consider promoting to `mature` or archiving).

Pages with `status: seed` for >30 days → **warning** (likely abandoned at seed; either flesh out or archive).

`status: archived` is exempt.

## Provenance (source / citation integrity)

### L09 — Provenance drift
Page has `## Key Facts` bullets but no `## Sources` section, OR has `## Sources` but `sources_count: 0`. Either way → **warning** (citations broken).

### L10 — Manifest divergence
For each page, walk `wiki/.manifest.json` to find which sources contribute. If a contributor is listed in manifest but the wiki page has no link to its reference page → **warning**.

If `sources_count` in frontmatter disagrees with actual count from manifest → **warning**.

### L11 — Contradiction surfaced (intra-page)
Pages that have `## Contradictions` section → list them as **info** so the user can review unresolved conflicts in batch. This check is intra-page only — it surfaces what pages have already self-declared as contradictory, not new contradictions found across pages.

### L12 — Cross-page numeric / claim disagreement
Detect contradictions that span pages: when two pages cite a numeric value or categorical claim about the same canonical entity but disagree.

Heuristic (best-effort, not exhaustive):
1. Group pages by shared wikilink target — pages that all link to `[[Entity-X]]` are co-citers.
2. Within each group, scan `## Key Facts` bullets for numeric patterns (P/E ratios, percentages, currency, version strings) and named-fact patterns (CEO, founding year, headquarters) about the entity.
3. Flag pairs where the same fact key has materially different values across pages (e.g. P/E=39 on page A, P/E=19 on page B; difference >5% on numerics, exact mismatch on categorical).

Output → **warning** with both page citations and the conflicting bullet text. Recommend either:
- Updating the stale page via `/wiki-ingest` on the newer source, or
- Adding a `## Contradictions` section on the canonical entity page documenting the disagreement.

**Limits**: this check is *advisory* — it WILL miss semantic mismatches expressed in prose, and WILL false-positive on facts that are genuinely time-sensitive (e.g. "Q1 P/E was 39, Q3 P/E is 19" both correct as-of-date). User judgment required on every L12 hit.

## Lint output format

```
Wiki Lint Report — YYYY-MM-DD

ERRORS (3):
  L01: entities/foo.md — missing frontmatter fields: [tags, summary]
  L07: concepts/bar.md:15 — broken wikilink [[NonexistentPage]] (did you mean [[NearestPage]]?)
  L02: entities/baz.md — summary too long (247 chars > 200)

WARNINGS (7):
  L06: skills/setup-x.md — orphan (no inbound links)
  L08: concepts/old-idea.md — stale (updated 2026-01-15, status=developing)
  L09: entities/qux.md — has facts but no Sources section
  ...

INFO (2):
  L11: synthesis/finance-ai.md — has unresolved Contradictions:
        - Source A says X; Source B says Y
  ...

Total: 12 issues across 8 pages.

Run `/wiki-auto-research` to address Open Questions surfaced.
```

## Action recommendations per check

| Check | Suggested fix |
|---|---|
| L01 | Re-run `/wiki-ingest` on the source(s) that fed this page |
| L02 | Hand-edit summary to ≤200 chars |
| L03 | Add missing section (often `## Connections` is the one missed) |
| L04 | Hand-edit. For backtick-wrapped wikilinks, sed unwrap: `s/\`(\*\*)?(\[\[[^\]]+\]\])(\*\*)?\`/\1\2\3/g` (preserves bold markers if present). For .md extension, sed: `s/\[\[([^]]+)\.md\]\]/[[\1]]/g` |
| L05 | Move Mermaid to a synthesis page; replace with prose in entity/concept |
| L06 | Either link from a related page, archive, or delete |
| L07 | Fix link target or create the missing page via `/wiki-ingest` |
| L08 | Promote `status` to `mature` or `archived`; or refresh content |
| L09 | Re-ingest to rebuild Sources block from manifest |
| L10 | Re-ingest the affected source |
| L11 | Resolve contradictions (research, query author, or move to Open Questions) |
| L12 | Re-ingest stale page from current source, OR add `## Contradictions` block on canonical entity page documenting the disagreement (with as-of-date if time-sensitive) |
