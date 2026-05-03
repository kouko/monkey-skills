---
name: wiki-lint
description: Run 11 health checks on wiki/ (structural, semantic, provenance). Use weekly or after wiki-ingest batches. Read-only — does not auto-fix. Do NOT use to fix issues (use wiki-ingest / wiki-cross-linker). Obsidian wiki 健全性チェック・健康檢查。
---

# Wiki Lint — Health Check on the Wiki Layer

Runs 11 health checks across the wiki and reports issues without modifying pages. User decides which fixes to apply.

See [lint-checks.md](references/lint-checks.md) for full check definitions.

## Pre-flight

1. Read `.env` for `OBSIDIAN_VAULT_PATH` (defaults `wiki/`).
2. If wiki/ doesn't exist or is empty, exit with "nothing to lint, run `/wiki-setup` and `/wiki-ingest` first".

## STEP 1 — Inventory the wiki

Build:
- List of all wiki pages by category
- All wikilinks (source page → target wikilink string)
- All page titles + filename slugs (for reverse lookup and broken-link detection)
- Frontmatter dump per page (for L01/L02 checks)
- Parsed `wiki/.manifest.json` (for L10 check)

## STEP 2 — Run the 11 checks

Execute all 11 checks defined in [lint-checks.md](references/lint-checks.md):

**Structural (must-fix):**
- L01: Frontmatter completeness
- L02: Summary length
- L03: Required body sections
- L04: Wikilink format
- L05: Mermaid placement

**Semantic (should-fix):**
- L06: Orphan pages
- L07: Broken wikilinks
- L08: Stale pages

**Provenance (advisory):**
- L09: Provenance drift
- L10: Manifest divergence
- L11: Contradictions surfaced

Severity: L01–L04, L07 → **error**. L05, L06, L08, L09, L10 → **warning**. L11 → **info**.

## STEP 3 — Report

Use the format in [lint-checks.md](references/lint-checks.md). Group by severity (errors first), then by check ID. Show file path with line number where applicable.

### Limit output

If errors > 50, collapse to "showing first 50 of N errors" and ask if user wants to see all. Long lint reports are signal — propose a remediation strategy rather than dumping everything.

## STEP 4 — Append to log

Append to `wiki/log.md`:

```markdown
| YYYY-MM-DD | lint | scope=full | <E> errors, <W> warnings, <I> info |
```

## STEP 5 — Recommend remediation

Group issues by their fix recipe (per the table in [lint-checks.md](references/lint-checks.md)):

```
Top fixes (by impact):
  1. Re-run `/wiki-ingest` on 3 sources → resolves 8 issues (L01, L09)
  2. Run `/wiki-cross-linker` → likely resolves most L06 orphans
  3. Hand-fix 2 broken wikilinks (L07) — see report above
  4. Run `/wiki-auto-research` on 5 Open Questions surfaced (L11)
```

## What wiki-lint does NOT do

- ❌ Does not modify any wiki page (read-only on `wiki/<category>/*.md`)
- ❌ Does not run web search (lint is local-only)
- ❌ Does not auto-fix — every fix is user-initiated via another skill or hand-edit
- ❌ Does not scan source notes (only audits the wiki layer itself)

**Write scope**: only appends one entry to `wiki/log.md` per run (audit trail). No other writes.

## When to invoke

| Trigger | Why |
|---|---|
| Weekly cadence | Catch stale pages, orphans, broken links from organic drift |
| After large `/wiki-ingest` batch (>10 pages) | Verify format compliance before pages compound |
| Before `/wiki-auto-research` campaign | Identify Open Questions inventory to prioritize |
| After page-format spec changes | Mass re-validate against new spec |
| On-demand when wiki "feels off" | Exploratory diagnostic |
