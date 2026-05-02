---
name: ingest
description: |
  Add user-supplied context (tribal knowledge, design rationale,
  gotcha notes) to one or more dbt model / source / macro pages in
  .dbt-wiki/. Captures information that is NOT in manifest.json or
  schema.yml — Redshift sort_key reasons, materialization gotchas,
  cross-incident links, ticket references, etc. Notes are appended
  to the target page's `## User Notes` body section; /dbt-wiki:refresh
  preserves them verbatim.
  Triggers on "ingest dbt context", "add note to <model>", "remember
  that <model> ...", "/dbt-wiki:ingest", "把這個 dbt context 記下來",
  "新增 dbt 註記".
  Do NOT trigger for: first-time setup (use /dbt-wiki:init), updating
  manifest snapshot (use /dbt-wiki:refresh), querying (use
  /dbt-wiki:query), capturing repo-level WHY (use /repo-wiki:ingest
  if .repo-wiki/ exists).
---

# dbt-wiki — Ingest Workflow (v1.0)

User-supplied context capture. Mirrors `/repo-wiki:ingest` context
mode for the dbt-internal scope. Notes attach to specific
model / source / macro pages and survive `/dbt-wiki:refresh` runs
(preserved as user-owned `## User Notes` body section per SCHEMA.md).

dbt-wiki ingest is **context-only** in v1.0. It does NOT have:
- `git` mode (manifest.json snapshot supersedes git for dbt structure;
  use /dbt-wiki:refresh after `dbt parse` instead)
- `doc-import` mode (v2 backlog — for now, paste the doc summary as
  context manually, or write to a `docs/` file and reference it)

## Pre-condition Check

```bash
test -d .dbt-wiki || { echo "Knowledge base not initialized. Run /dbt-wiki:init first."; exit 1; }
test -f .dbt-wiki/index.md || { echo "Missing .dbt-wiki/index.md — re-run /dbt-wiki:init."; exit 1; }
```

If user invocation has no argument:

> Usage: `/dbt-wiki:ingest "<your note>"`
>
> Example: `/dbt-wiki:ingest "fct_orders sort_key is (order_date, customer_id) because Tableau extract joins on these — see incident #4521"`
>
> The note will be attached to the relevant model / source / macro
> page based on names mentioned in your text. If multiple matches
> or no match is detected, you'll be asked to clarify.

Exit cleanly if no arg.

## Step 1: Identify Target Resource(s)

Parse the user's argument text for resource names. Match against
existing pages under:
- `.dbt-wiki/models/*.md` — model names
- `.dbt-wiki/sources/*.md` — source names (in form `<source>__<table>`)
- `.dbt-wiki/macros/*.md` — macro names
- `.dbt-wiki/seeds/*.md`, `snapshots/*.md`, `exposures/*.md`

Matching strategy:
1. **Exact name match**: tokens in the argument that exactly match a
   resource name (case-sensitive, since dbt is case-sensitive)
2. **Tier-prefix match**: if user mentions a tier ("marts_msd 整層"),
   collect all models under that path prefix
3. **No match → ask**:

   > Couldn't identify a target resource in your note. Available models:
   > <list top 10 most-recently-edited; for full list see .dbt-wiki/index.md>
   >
   > Which model / source / macro should this note attach to?

4. **Multiple matches** (when user mentions 2+ resources, or tier-prefix
   matches multiple):

   > Your note mentions <list>. Attach to:
   > [a] all of them (same note copied to each)
   > [b] just <first one> — pick one
   > [c] cancel

## Step 2: Compose Note Entry

For each target resource:

```markdown
### <YYYY-MM-DD> <slug-from-first-sentence>
<full user-supplied text, lightly cleaned: trim, normalize whitespace,
preserve original wording — DO NOT rewrite as Claude's prose>
```

Slug rule: take first 6-8 words of the user's text, kebab-case, lowercase.
Skip dbt resource names already in heading. Examples:

| User text | Slug |
|---|---|
| "fct_orders sort_key is (order_date, customer_id) because..." | `sort-key-rationale` |
| "marts_msd permissions need prod_marts_readonly_group..." | `permissions-readonly-group` |
| "stg_customers has GDPR redaction merge — see incident #4521" | `gdpr-redaction-merge` |

If slug collides with an existing entry on the same date, append `-2`, `-3`, ...

## Step 3: Append to Target Page

Read the target page. Locate the `## User Notes` section:
- If exists: append the new entry below the last existing entry
- If missing: insert `## User Notes` after `## Tests` section (per SCHEMA.md
  standard ordering); then add the entry

NEVER:
- Modify any other section (Description / SQL Preview / Column Sources /
  Tests / Inline Comments / Cross-references / etc.)
- Remove existing User Notes entries
- Re-order existing entries
- Change the section heading text

## Step 4: Append Log Entry

```
## [<date>] ingest | attached note to <N> page(s)
- Targets: [<resource-name>, ...]
- Slug: <slug>
- Note size: <chars> chars
```

## Step 5: Summary

```
✓ Note attached to <N> page(s):
  - .dbt-wiki/models/fct_orders.md  (### 2026-05-02 sort-key-rationale)

  To verify: /dbt-wiki:query "fct_orders sort key 為什麼這樣設？"
  To add more: /dbt-wiki:ingest "<another note>"
```

## Cross-skill Integration

If `.repo-wiki/` exists in the same repo, suggest the user consider
whether the note belongs in dbt-wiki (dbt-internal: model behavior,
column quirks, materialization) or in repo-wiki (cross-cutting WHY:
business decisions, project-level history):

> Note attached to dbt-wiki. If this context is relevant beyond dbt
> (e.g., business-level decision touching multiple subsystems), consider
> also: `/repo-wiki:ingest "<context>"` to capture at repo level.

This is informational only — do NOT auto-cross-post.

## Rules

NEVER:
- Modify any file outside `.dbt-wiki/<page>.md` (specifically: never
  touch `dbt/`, `target/`, or other plugins' directories)
- Rewrite or paraphrase the user's note content (light whitespace
  normalization OK; semantic editing NOT OK)
- Auto-attach without confirming target on multi-match or no-match
- Skip the `## User Notes` section heading (refresh recognizes it as
  user-owned by name)
- Use `[[wikilinks]]` — only standard markdown links
- Connect to dbt Cloud / warehouse / external API

ALWAYS:
- Verify `.dbt-wiki/` exists before any work
- Match resource names case-sensitively (dbt convention)
- Append, never replace, existing User Notes entries
- Date-prefix every new entry (`### YYYY-MM-DD <slug>`)
- Preserve user's original wording and language (zh / ja / en mixed OK)
- Append a log entry per ingest invocation
- Suggest /repo-wiki:ingest cross-link when note has cross-cutting scope
  (informational; never auto-post)
