---
name: review
description: |
  Human certification loop for dbt-wiki pages — lists pages needing review (developing or mature-but-stale), prioritizes by risk, certifies each → mature. Use for 'review pages', 'certify', 'what needs review', '審核'. Query → query.
---

# dbt-wiki — Review Workflow (v2.1)

Human certification loop. Knowledge pages start as `developing` (LLM-distilled,
not yet human-verified). A page becomes `mature` only when a human confirms its
business meaning, field definitions, and value-domain claims are correct. Stale
`mature` pages (flagged by `/dbt-wiki:rescan`) re-enter the queue for
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
| `status: mature` AND `stale: true` | Re-certification needed — the page was previously certified, but `/dbt-wiki:rescan` flagged it stale because one or more of its `derived_from` evidence models changed. |

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
- `stale_reason` — why it was flagged (set by rescan; null on first-cert pages)
- `updated` — last distilled/edited date
- `derived_from` — list of evidence model unique_ids (used to compute reference count in Step 2)
- `aliases` — project-language synonyms (display aid)

If the queue is empty, report:

> All knowledge pages are either certified (mature + not stale) or not yet
> distilled (seed). Nothing to review.
> Run `/dbt-wiki:rescan` if you suspect recently changed evidence models
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

## Step 3 — Per-Page Review Surface

For each queued page (working through the ranked queue top-to-bottom, one page
at a time), surface the following so the human can verify efficiently without
re-reading every body line:

**Inferred value-domains** (`via: inferred`)
: List every `value_domain:` line in the `## Fields` / `## Definition` body
  section that carries `(via: inferred)`. These are AI guesses — no
  `accepted_values` test and no `DISTINCT` evidence backs them. Example surface:

  ```
  Field `status` — value_domain: [pending, active, cancelled]  (via: inferred)
  Field `region` — value_domain: [north, south]  (via: inferred)
  ```

  Ask the human: "Do these match the values you see in your warehouse?"

**Caveat landmines** (`[bug]` / `[no-test]`)
: Quote each Caveat entry tagged `[bug]` or `[no-test]` verbatim. Example:

  ```
  [bug]  amount includes tax when channel = 'web' (ticket #1234)
  [no-test]  soft-deleted rows excluded by convention — no dbt test guards this
  ```

**Evidence lineage** (`derived_from`)
: List the `derived_from` model unique_ids so the human can spot whether the
  page is rooted in the right models. Do not load the evidence pages —
  the unique_ids are sufficient.

**Page summary**
: Display the `summary` frontmatter field (one sentence the LLM wrote to
  describe the entity/metric/concept). This is the fastest way for the human to
  confirm the page describes what they think it describes.

After surfacing the above, ask:

> "Does everything above look correct? Reply **yes** to certify, **skip** to
> defer this page, or describe any corrections needed."

Do NOT certify automatically — certification is always a human action.

---

## Step 4 — On Human Approval: Certify (Promote to `mature`)

When the human replies affirmatively (yes / looks good / certify / approve / 認証 / 認定):

1. **Set `status: mature`** in the page frontmatter.

2. **Stamp `reviewed_by`**: infer the reviewer's name from `git config user.name`
   in the wiki's git repo. If the command fails or the human overrides (e.g.
   "put my name as Alice"), use the human-supplied value instead.

3. **Stamp `reviewed_at`**: today's date in ISO-8601 format (`YYYY-MM-DD`).

4. **If the page was stale**, clear the staleness fields:
   - Set `stale: false`
   - Set `stale_at: null`
   - Set `stale_reason: null`

5. **Append one log entry per certified page to `.dbt-wiki/log.md`**:

   ```
   ## [YYYY-MM-DD] review | certified <type>/<slug>.md by <reviewer>
   - Previous status: <developing | stale-mature>
   - New status: mature
   - Reviewer notes: <free text or "none">
   ```

   Example:
   ```
   ## [2026-05-15] review | certified entities/order.md by alice
   - Previous status: developing
   - New status: mature
   - Reviewer notes: none
   ```

   Create `.dbt-wiki/log.md` with a `# dbt-wiki log` header if it does not yet
   exist.

6. Confirm back: "Certified `<title>` as mature (reviewed_by: `<name>`,
   reviewed_at: `<date>`)."

Move on to the next queued page.

---

## Step 5 — Stale `mature` Pages: Flag, Never Auto-Demote

A `mature` page that `/dbt-wiki:rescan` has flagged with `stale: true` enters
the queue as **"re-review needed"** (Step 1 already handles this). The rule:

**NEVER auto-demote `mature → developing` on staleness.**

Rationale: a page that has been human-certified retains its certification value
even when the underlying evidence models change. Demoting it automatically on
every rescan would thrash the human certification record and create false
impressions that every previously-reviewed page is unreviewed again.

Instead:

| Human action | What the agent does |
|---|---|
| Re-certifies (Step 4 approval) | Clear `stale` / `stale_at` / `stale_reason`, update `reviewed_at`, keep `status: mature`. |
| Explicitly downgrades ("this needs rework") | Set `status: developing`, clear `reviewed_by` / `reviewed_at`, add a Caveat noting why. |
| Skips ("defer") | Leave all frontmatter unchanged — page stays `mature + stale`, re-appears in the next review queue. |

Only the human decides whether a stale-mature page drops back to `developing`.
The agent never makes that decision unilaterally.

---

## Step 6 — Implementation Note (Prose-Driven, No Python)

This entire review loop is **LLM-prose-driven**:

- The agent reads frontmatter and body text using the Read tool.
- The agent presents the surface (Step 3), waits for human reply, then writes
  frontmatter edits using the Edit tool if approved.
- **No Python scripts, no automation harness.** The human is in the loop on
  every page; the agent is the interface.
- **Write only the approved pages.** If the human skips a page or requests
  corrections, do not touch that page's frontmatter until the human confirms
  the corrections are addressed.

---

## Rules

NEVER:
- Demote a page unilaterally (do not change `status: mature` → `status: developing`
  except on explicit human instruction — see Step 5).
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
