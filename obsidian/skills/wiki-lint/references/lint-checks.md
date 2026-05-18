# Wiki Lint — 14 Health Checks

Categorized into **structural** (format violations), **semantic** (content health), and **provenance** (source/citation integrity).

## Structural (format compliance)

### L01 — Frontmatter completeness

Each wiki page must have the full set of required frontmatter fields for its `type`. Missing any → **error**.

**Required fields by page type** (authority: [page-format.md](../../wiki-ingest/references/page-format.md) §Type-specific frontmatter):

| Page `type` | Required frontmatter fields |
|---|---|
| `wiki-entity`, `wiki-concept`, `wiki-synthesis`, `wiki-skill` | `title`, `type`, `domain`, `status`, `updated`, `tags`, `sources_count`, `summary` (8 fields) |
| `wiki-journal` | Same 8 as above **plus** `date` |
| `wiki-reference` | `title`, `type`, `source_path`, `date`, `ingested`, `contributes_to`, `tags`, `summary` (8 fields; `domain` / `status` / `updated` / `sources_count` are NOT required — reference pages are immutable per-source citation records, not lifecycle-managed knowledge pages) |

The per-type field sets diverge intentionally: reference pages are auto-generated audit-trail records (one per source ingest), while entity / concept / synthesis / skill pages are curated and evolve over time and so carry lifecycle metadata (`status`, `updated`, `sources_count`).

### L02 — Summary length
`frontmatter.summary` must be ≤200 characters, single line, no markdown. Violations → **error**.

### L03 — Required body sections

Each wiki page must have the body sections required by its `type`. Missing any → **error**.

**Required sections by page type** (authority: [page-format.md](../../wiki-ingest/references/page-format.md) §Body Structure and §Reference page body structure):

| Page `type` | Required body sections |
|---|---|
| `wiki-entity`, `wiki-concept`, `wiki-synthesis`, `wiki-skill`, `wiki-journal` | `## Summary`, `## Key Facts`, `## Connections` |
| `wiki-reference` | `## Source`, `## Source Excerpt / TL;DR`, `## Key Contributions` |

Reference pages use a different body shape because they are citation records, not knowledge cards — they do not synthesize claims, so `## Key Facts` and `## Connections` do not apply. The `## Source` section on reference pages is then further validated by L14.

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

**Exemption — reference page `## Source` section:** Wikilinks inside the `## Source` body section of `wiki/references/*.md` pages are out of scope for L07. These wikilinks intentionally point to **source files outside `wiki/`** (in the Sources layer — `references/<topic>/<file>.md`, `inbox/`, `reading_list/`, etc.) and resolve via Obsidian's bare-basename matching. Per [page-format.md §Reference page body structure](../../wiki-ingest/references/page-format.md#reference-page-body-structure), the wikilink basename matches `Path(source_path).stem` from frontmatter. Validation of these cross-layer links is handled by **L14**, which compares against `source_path` instead of the wiki-only inventory. L07 must skip these to avoid false-positive broken-link errors on every reference page.

### L08 — Stale pages
Pages with `frontmatter.updated` older than 90 days **and** `status: developing` → **warning** (consider promoting to `mature` or archiving).

Pages with `status: seed` for >30 days → **warning** (likely abandoned at seed; either flesh out or archive).

`status: archived` is exempt.

### L13 — Aliases required on cross-language slug

When a page's filename slug uses a different language script than its body language, the frontmatter `aliases:` field must be present and non-empty. Missing or empty `aliases:` → **warning** (SHOULD).

**Slug vs body language detection** (per [language-policy.md](language-policy.md)):
- **Slug language**: inferred from the filename (before `.md`). ASCII-only slug → Latin/English script. CJK characters in slug → zh/ja/ko script.
- **Body language**: inferred from the dominant script of the page body text (excluding code blocks and frontmatter). CJK character ratio ≥30% of body characters → CJK body.

**Cross-language condition** (triggers the check):
- Slug is ASCII-only **and** body language is CJK (zh-TW, ja, ko) — the typical case when `wiki-ingest` generates ASCII slugs from non-ASCII titles per language-policy §slug-generation.
- Slug contains CJK **and** body is primarily Latin/English (less common but also flagged).

**Rationale**: Obsidian search and `[[wikilink]]` autocomplete use the filename slug. When slug and body language diverge, users searching in their native language cannot discover the page without an alias. `aliases:` in frontmatter adds the native-language title as a searchable alternative.

**Examples**:
- `wiki/entities/softbank-group.md` (ASCII slug) with Japanese body → must have `aliases: [ソフトバンクグループ]` or similar → missing → **warning**
- `wiki/concepts/supply-chain-resilience.md` (ASCII slug) with zh-TW body → must have `aliases: [供應鏈韌性]` or similar → missing → **warning**

**Exemptions**: pages where slug and body language are the same script are exempt (no alias required). Pages with `status: archived` are exempt.

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

### L14 — Reference page `## Source` wikilink

Every page under `wiki/references/` must have a `## Source` body section containing exactly one wikilink in **bare basename** form (per [page-format.md §Wikilink resolution](../../wiki-ingest/references/page-format.md#wikilink-resolution) and §Reference page body structure).

Triggers (`wiki/references/*.md` only):

- Missing `## Source` heading → **warning**
- `## Source` section contains no wikilink → **warning**
- Wikilink contains `/` (path prefix, e.g. `[[references/foo/bar]]`) → **error**
- Wikilink ends with `.md` (extension, e.g. `[[bar.md]]` or `[[bar.md#anchor]]`) → **error**
- Wikilink basename ≠ basename of `source_path` from frontmatter → **warning** (likely stale; source renamed or re-ingested)

Detection regex (run against the body between `## Source` heading and the next `##` heading):

```
malformed_link_pattern = r'\[\[[^\]]*/[^\]]+\]\]|\[\[[^\]]+\.md[\]#]'
```

The second alternation uses `[\]#]` (not `\]\]`) so it catches both `[[foo.md]]` and `[[foo.md#anchor]]`. The first alternation already catches any `/` regardless of trailing anchor.

**Basename comparison** — parse the frontmatter as YAML (use `yaml.safe_load` or equivalent, **do not regex-extract**), then take `Path(source_path).stem`. YAML-quoted values like `source_path: "foo.md"` must be unquoted by the YAML parser before comparison; raw-string extraction will leave stray `"` characters that break the equality check.

**Rationale**: the `## Source` section is a human-navigation affordance for Obsidian. Path-prefixed or extension-suffixed wikilinks bypass Obsidian's shortest-link resolution and break preview / graph features. This is the most common LLM mistake on reference pages because `source_path` frontmatter (which keeps the full path) is right above it — LLMs sometimes copy that value into the wikilink, often retaining the YAML surrounding quotes too.

**Migration note**: reference pages created before this check existed will trigger missing-section warnings. Either re-ingest the source (regenerates correct format) or hand-edit. The check is warning-level (not error) precisely to allow gradual migration.

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
| L13 | Add `aliases:` field to frontmatter with the native-language title (e.g. `aliases: [余白, yohaku]`). Re-run `/wiki-ingest` on the source if you want the wiki page rebuilt (see language-policy.md §4. Aliases Conditional MUST) |
| L14 | Re-run `/wiki-ingest` on the source (regenerates `## Source` with correct format), OR hand-edit: take `source_path` from frontmatter, strip folder path and `.md` extension, write as `[[basename]]` |
