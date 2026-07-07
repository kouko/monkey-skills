# Bundle format — the portable analytics skill `pack` emits

This document specifies the **output structure** the `pack` skill
produces: a self-contained, portable Agent Skill folder named
`<project>-analytics/` that freezes a project's distilled `.dbt-wiki/`
knowledge into a bundle a warehouse-connected agent can load for
grounding. The bundle carries **knowledge + generation guidance**, not
an executor — the consuming agent brings its own warehouse-connect
tool (an MCP / CLI that runs SQL) to actually execute.

All examples below are **synthetic** (`acme-analytics`,
`fct_account_monthly`, `account_id`, `report_month`, …). A real bundle
distilled against a real warehouse is governed: it lands in the user's
**private** repo, never in this public plugin repo.

## Top-level shape

`pack` emits **one folder**, named after the project, suffixed
`-analytics`:

```
acme-analytics/                  # the emitted Agent Skill (synthetic name)
  SKILL.md                       # entry point — the consumption contract
  knowledge/                     # frozen distilled knowledge (read on-demand)
    _index.md                    #   retrieval entry point: one line per page (Step 2.7)
    _relations.md                #   physical anchor: relation -> schema + columns (Step 2.5)
  references/                    # generation guidance (copied in from pack)
  examples/                      # gold few-shot context (MAY be empty in v1)
  PROVENANCE.md                  # snapshot annotation (OR fold into SKILL.md frontmatter)
```

The folder slug derives from the project's business name in kebab-case
(e.g. `acme-analytics`), matching the consuming bundle's frontmatter
`name`.

## Flat-skill constraint (single-level subfolders, NO nesting)

The emitted bundle is an **Agent Skill** and MUST obey the same
Anthropic skill convention this repo enforces on its own skills:

> **A skill is a flat directory: `SKILL.md` + any number of
> single-level subfolders. A subfolder MUST NOT contain another
> subfolder.**

So `knowledge/`, `references/`, `examples/` each hold files **directly**
— never a nested folder:

```
✅ OK (single level):
acme-analytics/knowledge/customer.md
acme-analytics/knowledge/monthly-recurring-revenue.md
acme-analytics/references/generation-guidance.md

❌ NOT OK (subfolder inside a subfolder):
acme-analytics/knowledge/entities/customer.md   ← knowledge/ opens entities/
acme-analytics/knowledge/metrics/mrr.md         ← knowledge/ opens metrics/
```

> **Note — the `.dbt-wiki/` source tree is NOT a skill and is exempt.**
> The source `.dbt-wiki/` knowledge base in the user's repo legitimately
> nests (`_evidence/models/…`, `entities/…`, `metrics/…`,
> `concepts/…`). That nesting is fine *there* — it is generated wiki
> output, not a skill bundle. When `pack` **freezes** the knowledge into
> the bundle's `knowledge/`, it must **flatten** it (see "Knowledge
> layer — flattening" below) so the emitted bundle stays a valid flat
> skill.

## Portability

The emitted bundle is a standalone Agent Skill with no dependency on
dbt-wiki, on the source `.dbt-wiki/`, or on any dbt project. It can be:

- dropped into `~/.claude/skills/acme-analytics/`, or
- placed in any **Skills-compatible agent's** skill directory, or
- handed to a teammate who has **no dbt project** — only their own
  warehouse-connect tool — and still be useful (curated semantic
  knowledge + generation guidance + the consumption contract).

Portability is why everything the agent needs is **inside** the folder
(knowledge, guidance, contract) and why the consumption contract is
**tool-agnostic**: the bundle never names a specific warehouse MCP /
CLI; the consuming agent supplies execution.

## On-demand knowledge loading (unbounded)

`knowledge/` is the bundle's grounding layer. It is **read on demand,
not loaded up front**. The bundle's `SKILL.md` body stays small (the
consumption contract); the knowledge it points at can be **large /
unbounded** — the agent loads only the pages relevant to the question
being answered.

This mirrors how the source `dbt-wiki:query` workflow tiers retrieval
(index → summary → full page): the bundle's `SKILL.md` orients the
agent to `knowledge/`, and the agent pulls the entity / metric / concept
pages it needs per question. A bundle for a large project may carry
hundreds of knowledge pages without bloating the always-loaded
`SKILL.md`.

## `knowledge/` — what gets frozen (and flattened)

`knowledge/` is a **frozen snapshot** of the distilled knowledge layer
from the source `.dbt-wiki/` (page types owned by
`init/assets/SCHEMA.md`). It carries the **semantic** layer, not the raw
evidence dump:

- **entities** — one page per business object. Includes the
  plain-language `## Fields` column dictionary (the "column cards"),
  **including `value_domain` enum annotations** for small-cardinality
  categorical columns (e.g. `region_code` →
  `value_domain: [NL, EU, APAC]`) so a generator maps user terms to
  stored warehouse values without guessing.
- **metrics** — one page per business measure, with `## Calculation`
  (correct aggregation form + grain) and any `## Materialized Columns`
  variant→`model.column` mapping.
- **concepts** — one page per cross-cutting business rule.
- **syntheses** — verified deep-dive answer pages (when the source wiki
  has them). They are the highest-cost knowledge — human-verified
  question → analysis paths — and freeze exactly like the other types.
- **relationships** — the typed-edge graph carried in each page's
  frontmatter `relationships:` + body `## Relationships`. This is
  load-bearing for correct SQL: the edge `note` records the **full
  compound / composite join key** (e.g.
  `joins on account_id + report_month (composite key — both columns
  required)`). A generator MUST read the full key before emitting a
  JOIN — dropping a column silently fans out rows.

**Flattening rule.** The source layer nests
(`entities/customer.md`, `metrics/mrr.md`, …). Because the bundle must
stay a **flat** skill, `pack` writes these as direct children of
`knowledge/`. Knowledge slugs are already kebab-case, so a flat layout
needs no per-type subfolder; if a name collision is possible across
types, prefix the page type into the filename (e.g.
`metric-monthly-recurring-revenue.md`) — never re-introduce a
subfolder. Frozen pages keep their `derived_from` / provenance
frontmatter so the snapshot's lineage is traceable.

What is **dropped** when freezing: the bulky `_evidence/` mechanical
layer (raw manifest/sqlglot pages), `index.md`/`lineage.md`/`log.md`
machinery, and any `_internal/` artifacts. The bundle carries the
**curated semantic knowledge**, not the full evidence base.

## `knowledge/_index.md` — retrieval entry point (generated at pack time)

A flat `knowledge/` with hundreds of pages leaves the consuming agent
slug-guessing or grepping every file to *find* the right page. Pack
Step 2.7 generates `knowledge/_index.md` — one line per frozen page
(title, status, one-line summary, aliases), grouped by page type — from
the **frozen pages' own frontmatter**, so it always matches exactly what
was frozen. The consuming contract tells the agent to read it FIRST and
open only the pages it points to. Like `_relations.md`, it is a flat
`_`-prefixed child of `knowledge/` and not itself an indexed page.

## `knowledge/_relations.md` — physical anchor (the one thing re-carried from `_evidence/`)

Dropping `_evidence/` is right for grounding (the mechanical layer is noise
for a generation agent and stales fast) — with **one** exception that the
knowledge layer cannot supply: the **schema-qualified table**. Knowledge pages
name relations as `model.column`, never `schema.model`, so a bundle deployed at
a **repo-less target** can't write a runnable `FROM` without it. Step 2.5
restores exactly this thin anchor — `knowledge/_relations.md`, a flat
on-demand child of `knowledge/` listing, for every relation the knowledge pages
derive from:

- its **schema** (load-bearing; complete; reflects dbt custom-schema
  concatenation like `<db>__marts`, which a single-schema guess gets wrong), and
- its **column list** — offline from the source `_evidence/` pages (names +
  descriptions), or, with `--with-catalog`, real **types** pulled from the live
  warehouse for the canonical relations.

This is deliberately NOT a re-import of the evidence layer: no lineage, no raw
SQL, no materialization internals — only the relation→schema→columns map a
warehouse-connected agent needs to qualify a `FROM`. See `SKILL.md` Step 2.5.

## `references/` — generation guidance (copied in)

`references/` holds the SQL-**generation guidance** for the consuming
agent — produced separately (the `pack` skill's own
`references/generation-guidance.md`) and **copied** into each emitted
bundle. It reframes the semantic guardrails (correct aggregation /
compound-grain joins / value-grounding / source disambiguation /
temporal grounding) + schema-linking as guidance for a
warehouse-connected agent: **generate SQL grounded in `knowledge/` →
execute via your own warehouse tool → iterate**. It is reference
material the bundle's `SKILL.md` points at on demand.

## Language

The bundle inherits the knowledge layer's language. The source `.dbt-wiki/`
distills pages in the **project's source-comment language** (dbt-wiki treats
comments as the source of truth), so the frozen `knowledge/` pages are already
in that language and are copied **verbatim** — `pack` never translates them. The
bundle's own `SKILL.md` writes its **project-specific** prose (description,
orientation, worked example, trigger phrases) in the same `source_language`
(read from `.dbt-wiki/index.md`). What stays ASCII / English regardless: the
`name:` slug, frontmatter keys, knowledge slugs / links, stored `value_domain`
values, and `references/generation-guidance.md` — the SQL guardrails are
universal, language-neutral agent guidance, not project knowledge.

## `examples/` — gold few-shot context (slot reserved)

`examples/` is the slot for in-domain **question → correct-SQL** gold
examples that ground the agent with worked few-shot context. In **v1 it
MAY be empty** — the slot is reserved so a later increment (gold-example
generation, optionally execution-verified against a real warehouse) can
populate it without changing the bundle shape.

## Snapshot-annotation block

A bundle is a **point-in-time snapshot** of the source `.dbt-wiki/`. It
will go stale as the dbt project evolves. Every emitted bundle MUST
carry a snapshot annotation recording its provenance and a rebuild
pointer. Place it in **either**:

- the bundle's `SKILL.md` **frontmatter**, **or**
- a dedicated **`PROVENANCE.md`** at the bundle root.

The annotation MUST carry:

1. **`manifest_sha`** — the source `manifest_sha` the knowledge was
   distilled from (read from the source `.dbt-wiki/log.md` at pack
   time). Anchors the snapshot to a specific warehouse/manifest state.
2. **build date** — the `YYYY-MM-DD` the bundle was packed.
3. **a rebuild note** — explicit text that this is a snapshot and that
   refreshing requires re-running `pack`, e.g. *"This is a snapshot of
   the project's distilled knowledge. It does not auto-update — re-run
   `pack` against a refreshed `.dbt-wiki/` to rebuild."*

`PROVENANCE.md` (synthetic) example:

```markdown
# Provenance — acme-analytics

- source_manifest_sha: <md5-of-manifest-at-distill-time>
- build_date: 2026-06-03
- packed_by: dbt-wiki:pack

This bundle is a **snapshot** of acme's distilled knowledge as of the
build date above. It does **not** auto-update. To refresh, re-run
`dbt-wiki:pack` against an updated `.dbt-wiki/` and replace this folder.
```

Equivalent frontmatter form (when folded into `SKILL.md` instead):

```yaml
source_manifest_sha: <md5-of-manifest-at-distill-time>
build_date: 2026-06-03
snapshot_note: "Snapshot — re-run dbt-wiki:pack to refresh; does not auto-update."
```

## Relative-path references

Inside the emitted bundle, the `SKILL.md` references its sibling
subfolders by **relative path** (relative to the bundle root), per repo
convention: `knowledge/<page>.md`, `references/generation-guidance.md`,
`examples/<example>.md`. The bundle never uses absolute filesystem
paths and never uses `[[wikilinks]]` (standard markdown links only,
matching the source `.dbt-wiki/` convention).

**Intra-`knowledge/` links are flattened to match the flat layout.** The source
pages link cross-folder (`[X](../entities/x.md)`, `[S](../syntheses/s.md)`) and
cite dropped or repo-local files (`[m](../_evidence/models/m.md)`,
`[m](.dbt-wiki/_evidence/models/m.md)`, `[SPEC](../../models/…/SPEC.md)`);
after the flatten-on-freeze those paths are wrong (the target is a flat
sibling, or a file that does not exist at a portable target). pack Step 2.6
rewrites them: knowledge cross-folder → flat sibling `[X](x.md)`; any other
pathed `.md` link → delinked to plain label text. Acceptance (Step 7) requires
**zero broken intra-`knowledge/` links**.

## Acceptance summary

A conformant `pack` output is a folder `<project>-analytics/` that:

- is a **flat** Agent Skill (`SKILL.md` + single-level subfolders, no
  nested subfolders) whose `SKILL.md` frontmatter **parses as YAML**;
- contains `knowledge/` (frozen entities/metrics/concepts/syntheses +
  column cards + relationships with **compound join-keys** +
  `value_domain`) at **page-count parity** with the source knowledge
  layer, plus the generated `knowledge/_index.md` retrieval entry point,
  `references/` (generation guidance), and an `examples/` slot (MAY be
  empty in v1);
- is **portable** — drops into `~/.claude/skills/` or any
  Skills-compatible agent, usable with only a warehouse-connect tool
  and no dbt project;
- loads its `knowledge/` **on demand** (unbounded) rather than up front;
- carries a **snapshot-annotation block** (in `SKILL.md` frontmatter or
  `PROVENANCE.md`) with source `manifest_sha` + build date + a "this is
  a snapshot — re-run `pack` to refresh" note.
