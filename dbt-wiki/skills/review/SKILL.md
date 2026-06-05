---
name: review
description: |
  Human certification loop for dbt-wiki knowledge pages. Lists pages
  that need review (status: developing awaiting first certification, or
  status: mature but flagged stale by a refresh), prioritizes them by
  risk/impact so the most dangerous pages surface first, and walks a
  human reviewer through certifying each one. Promotes certified pages
  to mature; flags pages that cannot be certified as needing more work
  without demoting them.
  Trigger phrases: "review pages", "certify", "promote to mature",
  "what needs review", "show review queue", "which pages need sign-off",
  "review backlog", "mark as mature", "re-certify stale pages",
  "審核", "認證", "升級成熟", "哪些頁面待審", "需要審核",
  "レビュー", "認定", "成熟に昇格", "レビューキュー",
  "/dbt-wiki:review".
  Do NOT trigger for: querying the wiki (use /dbt-wiki:query), ingesting
  tribal knowledge (use /dbt-wiki:ingest), updating after dbt parse
  (use /dbt-wiki:refresh), or first-time setup (use /dbt-wiki:init).
---

# dbt-wiki — Review Workflow (v2.1)

Human certification loop. Knowledge pages start as `developing` (LLM-distilled,
not yet human-verified). A page becomes `mature` only when a human confirms its
business meaning, field definitions, and value-domain claims are correct. Stale
`mature` pages (flagged by `/dbt-wiki:refresh`) re-enter the queue for
re-certification. This skill orchestrates that loop.

## Pre-condition Check (Step 0)

```bash
# Same WIKI_DIR resolution as query/init — wiki lives at the git repo root.
WIKI_DIR=$(git rev-parse --show-toplevel 2>/dev/null) || WIKI_DIR="$PWD"
cd "$WIKI_DIR" || { echo "Cannot cd to $WIKI_DIR"; exit 1; }

test -d .dbt-wiki || {
  echo "Knowledge base not initialized at $WIKI_DIR/.dbt-wiki/. Run /dbt-wiki:init first."
  exit 1
}
test -f .dbt-wiki/index.md || {
  echo "Missing .dbt-wiki/index.md — re-run /dbt-wiki:init."
  exit 1
}
```

## Step 1 — Build the Review Queue

Scan every knowledge page under `.dbt-wiki/entities/`, `.dbt-wiki/metrics/`,
and `.dbt-wiki/concepts/`. A page enters the queue when it meets **either**
condition:

| Condition | Meaning |
|---|---|
| `status: developing` | First certification needed — page was distilled by the LLM but no human has signed off yet. |
| `status: mature` AND `stale: true` | Re-certification needed — the page was previously certified, but `/dbt-wiki:refresh` flagged it stale because one or more of its `derived_from` evidence models changed. |

Pages with `status: seed` are not yet distilled — skip them.
Pages with `status: archived` are retired — skip them.

**How to read the queue:**

```bash
# Collect queue candidates — read frontmatter of all knowledge pages.
# For each file under .dbt-wiki/{entities,metrics,concepts}/*.md:
#   - Parse the YAML frontmatter (lines between the --- delimiters).
#   - Include if:  status == "developing"
#              OR (status == "mature" AND stale == true)
# Exclude if: status in ("seed", "archived")
find .dbt-wiki/entities .dbt-wiki/metrics .dbt-wiki/concepts \
     -maxdepth 1 -name "*.md" 2>/dev/null
```

For each candidate page, read its frontmatter to extract:
- `title` — human-readable name
- `type` — knowledge-entity | knowledge-metric | knowledge-concept
- `status` — developing | mature
- `stale` — true | false
- `stale_reason` — why it was flagged (set by refresh; null on first-cert pages)
- `updated` — last distilled/edited date
- `derived_from` — list of evidence model unique_ids (used to compute reference count in Step 2)
- `aliases` — project-language synonyms (display aid)

If the queue is empty, report:

> All knowledge pages are either certified (mature + not stale) or not yet
> distilled (seed). Nothing to review.
> Run `/dbt-wiki:refresh` if you suspect recently changed evidence models
> have not been propagated yet.

## Step 2 — Prioritize by Risk / Impact

For each queued page, compute a **risk score** and rank highest-first.
The score combines three signals:

### Signal A — Inferred value-domain count

Count occurrences of `(via: inferred)` in the page **body** (the text after
the frontmatter `---` block). Each `(via: inferred)` suffix on a
`value_domain:` line marks a categorical enum that was guessed from SQL
structure with no `accepted_values` test and no `DISTINCT` backing — it is a
hypothesis. A query that hard-filters on a wrong enum silently returns zero
rows.

- Read the full body of each queued page.
- `inferred_count` = count of `(via: inferred)` occurrences in the body text.

### Signal B — Caveat landmine count

Count occurrences of `[bug]` and `[no-test]` tags in the page **body**
(inside the `## Caveats` section, but search the whole body to be safe):

- `[bug]` — known incorrect behavior that produces wrong results if unhandled.
- `[no-test]` — an assertion not guarded by a dbt test; can change silently.

`landmine_count` = count of `[bug]` + count of `[no-test]` in the body text.

### Signal C — Inbound reference count

How many other knowledge pages **point to** this page? A highly-referenced
page has outsized blast radius — if its definition is wrong, every downstream
page that depends on it inherits the error.

Scan **all** knowledge pages (not just queued ones) under
`.dbt-wiki/{entities,metrics,concepts}/*.md` and count:

1. `relationships[].target` entries in the frontmatter that resolve to this
   page's relative path (e.g., `order.md` from a sibling entity page, or
   `../entities/customer.md` from a metric page).
2. `derived_from:` entries that list a `unique_id` **also listed in this
   page's own `derived_from:`** — a partial-overlap proxy: pages sharing
   evidence overlap are likely closely coupled.

`ref_count` = total distinct pointing pages found by rule 1 (relationship
edges) + any additional pages found by rule 2 that were not already counted.

For this step, do **not** load full page bodies of non-queued pages — read
only their frontmatter (`relationships:` and `derived_from:` fields) to keep
load cost proportional to the wiki size.

### Composite rank

Sort the queue descending by the tuple `(inferred_count, landmine_count,
ref_count)` — most-inferred first, then most-landmined, then most-referenced
as a tiebreaker. Where all three scores are equal, sort by `updated`
ascending (older page reviewed first).

**Display the queue as a ranked table:**

```
## Review Queue (<N> pages)

| # | Page | Type | Condition | Inferred | Landmines | Refs | Last Updated |
|---|------|------|-----------|----------|-----------|------|--------------|
| 1 | [Order](entities/order.md) | entity | developing | 3 | 2 | 4 | 2026-05-10 |
| 2 | [Monthly Revenue](metrics/monthly-revenue.md) | metric | stale (evidence changed) | 1 | 1 | 6 | 2026-04-22 |
| 3 | [Active Customer](concepts/active-customer.md) | concept | developing | 0 | 1 | 2 | 2026-05-28 |
...
```

For `stale` pages, the Condition cell reads "stale — `<stale_reason>`" if
`stale_reason` is set; otherwise "stale (evidence changed)".

For `developing` pages with `inferred_count > 0`, append a brief note below
the table:

> Pages with inferred value-domains (Signal A > 0) carry the highest SQL
> risk: a wrong enum in a WHERE clause silently returns zero rows. Confirm
> the `value_domain` lists in the `## Fields` / `## Definition` sections
> against the actual warehouse values before certifying.

---

*(Steps 3–6 — certify action, write reviewed_by / reviewed_at, flag
not-certifiable pages, and log — are added in the next task.)*

## Rules

NEVER:
- Demote a page (do not change `status: mature` → `status: developing`; flag
  it not-certifiable instead — see Step 3+ when added).
- Auto-certify pages without human confirmation — certification is a human
  action, not an LLM action.
- Modify `.dbt-wiki/_evidence/` pages — review touches only knowledge pages.
- Skip the pre-condition check — a missing wiki or stale index causes
  misleading queue output.
- Use `[[wikilinks]]` — only standard markdown links.

ALWAYS:
- Read frontmatter of ALL three knowledge folders when building the queue
  (entities + metrics + concepts) — missing a folder silently hides pages.
- Surface `stale_reason` when available — it tells the reviewer exactly what
  changed and why re-certification is needed.
- Show Signal A / B / C scores in the queue table — reviewers need to know
  WHY a page ranks high, not just that it does.
- Load only frontmatter of non-queued pages for Signal C — do not load bodies
  of pages not in the queue (minimizes token cost on large wikis).
