# Retrieval Procedure — NL Question → Schema Context

This file defines how `to-sql` gathers the schema context needed to
generate SQL for a business question. Read this before assembling any
prompt (see `references/prompt-assembly.md`). Do NOT invent a retrieval
procedure that contradicts this spec or the `query` skill's tiered
loading contract.

Referenced from: `SKILL.md § Step 1`

---

## 1. Tiered Retrieval — Reuse `query`'s Mechanism

`to-sql` does **not** build its own retrieval layer. It reuses the same
two-tier loading that `query` applies for K1–K3 semantic classes
(`query/SKILL.md` §§ Step 2–3):

**Tier 1 — summary frontmatter (fast scan)**
Load the `summary:` field from the YAML frontmatter of each candidate
knowledge page (`entities/`, `metrics/`, `concepts/`). The index
(`.dbt-wiki/index.md`) lists every knowledge page with its summary line.
Use this tier to identify which pages are relevant to the question before
loading full bodies. Do NOT load full pages during the scan pass.

**Tier 2 — full page body (on demand)**
Load the complete `.md` body only for pages that passed the Tier-1 scan.
For `entities/` pages, the full body includes `## Fields` (the
business-term → column dictionary), `## Relationships`, and `## Evidence`.
For `metrics/` pages, the full body includes `## Materialized Columns`
(when present — see §3.2), `## Calculation`, and `## Relationships`.
For `concepts/` pages, the full body includes the rule definition and
`## Relationships`.

**Page-count guard (inherited from `query`):** if the relevant set exceeds
30 pages before Tier-2 loading, apply the too-broad handling defined in
§5 before proceeding.

---

## 2. Pre-condition

Before any retrieval, confirm the wiki exists at the expected location.
This is the same check `query` performs in its Step 0:

```bash
WIKI_DIR=$(git rev-parse --show-toplevel 2>/dev/null) || WIKI_DIR="$PWD"
test -d "$WIKI_DIR/.dbt-wiki" || {
  echo "No .dbt-wiki/ found. Run /dbt-wiki:init first."
  exit 1
}
```

`to-sql` is read-only. It never writes to `.dbt-wiki/`. See §6.

---

## 3. Pages to Load for SQL Generation

Given a business question, pull the following pages in this order. Load
Tier-1 summaries first across all categories; then promote to Tier-2
full-body only the relevant candidates.

### 3.1 Entities (`entities/`)

For each business entity referenced in the question (directly or implied
by the subject noun phrase):

- Load the matching `entities/<entity-slug>.md` in full (Tier 2).
- The `## Fields` section is the most critical target: it maps each
  **business term** (the language the question uses) to the physical
  `model.column` reference. Use this dictionary for schema-linking in
  prompt assembly.
- The `relationships:` frontmatter block and `## Relationships` body
  section expose **typed edges** — especially `joins` edges (which model
  joins to which on which keys) used to derive join-paths (§3.4).
- Record the `derived_from` unique_ids to identify which evidence models
  back this entity; load those `_evidence/` pages in §3.5.

### 3.2 Metrics (`metrics/`)

For each metric mentioned or implied in the question:

- Load the matching `metrics/<metric-slug>.md` in full (Tier 2).
- The `## Materialized Columns` section — when present — contains the
  **column card mapping**: it maps each pre-aggregated variant of the
  metric (e.g., `gmv_mtd`, `gmv_qtd`, `gmv_last_month`) to its physical
  `model.column` and specifies that the correct SQL pattern is
  `SELECT <column>` rather than re-aggregating. Use these cards as
  authoritative schema-link targets.

  > **Note**: `## Materialized Columns` is produced by the metric-card
  > distillation work (PR #364). If the section is absent, the metric
  > page pre-dates that work; fall back to the `## Calculation` section
  > for the aggregation formula and the `derived_from` evidence model for
  > physical column names.

- The `relationships:` `measures` edge identifies which entity this
  metric aggregates over (GROUP BY grain) — load the target entity page
  if not already loaded.
- The `relationships:` `depends_on` edges name concept pages that define
  cross-cutting rules (e.g., "active customer") required to correctly
  filter or compute the metric.

### 3.3 Concepts (`concepts/`)

For each cross-cutting business rule that filters, qualifies, or defines
a boundary condition in the question (e.g., "active customers only",
"online channel", "paid orders"):

- Load the matching `concepts/<concept-slug>.md` in full (Tier 2).
- Use the concept's body to inform WHERE-clause conditions and JOIN
  filter predicates in prompt assembly.

Concepts are often reached transitively via metric `depends_on` edges
(§3.2) rather than from the question text directly. Follow those edges.

### 3.4 Relationships and Join-Paths

Typed edges in the knowledge layer are the join-path source. They are
present in two places:

1. **Frontmatter `relationships:` block** — machine-readable edge list.
   Each edge has a `type`, a `target` (relative path), and a `note`.
2. **`## Relationships` body section** — human-readable prose describing
   the same edges.

For SQL generation, the most important edge types are:

| Edge type | Location | SQL use |
|---|---|---|
| `joins` | entity pages | Provides the JOIN key pair: `entity_A.key = entity_B.key`. Use to build explicit `JOIN ... ON ...` clauses. |
| `measures` | metric pages | Confirms the GROUP BY anchor entity and grain. |
| `depends_on` | metric pages | Identifies concept pages whose rules become WHERE / HAVING conditions. |

**Deriving join-paths:** To join entity A to entity B in a query, walk
the `joins` edges in entity pages starting from A. If A has no direct
`joins` edge to B, walk one hop via an intermediate entity C that has
`joins` edges to both A and B. Do not invent join keys that are not
present in a `relationships:` edge. If no join-path exists in the wiki,
state that the join cannot be derived from the current knowledge base.

### 3.5 Evidence Layer — Physical Column Names and Types

After identifying the knowledge pages in §§3.1–3.3, load the backing
evidence pages for real column names and data types:

- For each entity: load the `_evidence/models/<model>.md` pages listed in
  its `## Evidence` section (sourced from `derived_from` frontmatter).
  The evidence model's `columns[]` array contains the physical column
  names and, when `catalog.json` was present at init time, the data types.
- For each metric: load the evidence model(s) in its `derived_from` list.
  If `## Materialized Columns` cards are present in the metric page, the
  physical `model.column` reference is already explicit — evidence loading
  confirms existence but is not required to determine the column name.

Evidence pages are in `.dbt-wiki/_evidence/models/`. Use only column
names that appear explicitly in evidence — do not infer or guess column
names from business-term labels alone.

---

## 4. Retrieval Output

After completing the tiered load, the retrieval stage hands off a
structured context bundle to prompt assembly:

```
retrieval_context:
  entities:           # list of fully-loaded entity pages (slug + fields dict + relationships)
  metrics:            # list of fully-loaded metric pages (slug + column-cards if present + relationships)
  concepts:           # list of fully-loaded concept pages (slug + rule body)
  join_paths:         # list of {from_entity, to_entity, via_key_pair, note} derived from joins edges
  evidence_models:    # list of {unique_id, columns: [{name, type}]} from _evidence/ pages loaded
  pages_consulted:    # ordered list of .dbt-wiki/... paths loaded (for citation in Step 5)
```

This bundle is the sole input to `references/prompt-assembly.md`.

---

## 5. Exception Handling

### 5.1 Not Found

If no knowledge page matches the entity, metric, or concept mentioned in
the question:

1. Check the index.md summary lines for fuzzy matches (similar slugs,
   synonym terms).
2. If the question uses a technical model name (e.g., `fct_orders`), look
   for a `_evidence/models/fct_orders.md` page directly as a fallback —
   evidence-layer description is better than nothing.
3. If no match exists at either layer, do not hallucinate. Report:

   > No knowledge page found for "<term>". The wiki does not contain a
   > definition for this entity/metric/concept. Evidence-layer description
   > (if available): [link to `_evidence/` page]. To add this knowledge,
   > run `/dbt-wiki:ingest` to record business context, or
   > `/dbt-wiki:refresh` if the model was recently added.

4. Do not attempt SQL generation for the missing term. If the missing
   term is central to the question, stop and report. If it is peripheral
   (e.g., a filter concept that is missing but the main entity and metric
   are found), proceed with a caveat in the output.

### 5.2 Ambiguous

If the question matches multiple knowledge pages (e.g., "revenue" matches
`gross-merchandise-value.md`, `net-revenue.md`, and `subscription-revenue.md`):

1. List the candidates with their summary lines.
2. Ask the user to disambiguate before loading full pages:

   > "Revenue" matches multiple metrics: (1) Gross Merchandise Value —
   > total order value before refunds; (2) Net Revenue — after refunds
   > and discounts; (3) Subscription Revenue — recurring component only.
   > Which do you mean?

3. Do not load all candidates in full — Tier-1 summaries are sufficient
   to present the choice.

### 5.3 Too Broad

If the Tier-1 scan of the question would require loading more than 30
pages in full (e.g., "generate SQL for all sales metrics"):

1. Report the count and ask the user to narrow the scope. Suggest
   concrete filters such as a mart tier, a specific entity, or a date
   range qualifier:

   > This question would require loading N pages. Narrow scope by
   > specifying a tier (e.g., "in marts/"), a specific entity
   > (e.g., "for Customer"), or a metric family (e.g., "GMV metrics
   > only")?

2. Do not proceed with full loading without explicit user confirmation
   ("yes, load all").

---

## 6. Read-Only Constraint

`to-sql` consumes `.dbt-wiki/` strictly as a read-only knowledge base.
It never:

- Writes or modifies any page in `.dbt-wiki/`.
- Creates synthesis files (that is `query`'s Step 6.5).
- Appends to `log.md` on behalf of the retrieval stage (the SKILL.md
  Step 5 output block handles the query log entry).

Any write to `.dbt-wiki/` during a `to-sql` session is a bug.
