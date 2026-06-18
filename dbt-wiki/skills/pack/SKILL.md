---
name: pack
description: |
  Package the dbt-wiki knowledge base into a portable, warehouse-tool-agnostic
  analytics skill. Run by the PROJECT OWNER (someone who has a distilled
  `.dbt-wiki/`) to freeze the curated semantic knowledge into a self-contained
  Agent Skill folder `<project>-analytics/` (SKILL.md + knowledge/ + references/
  + examples/) that a teammate or agent can drop into `~/.claude/skills/` and use
  with their OWN warehouse-connect tool — no dbt project, no DB driver required.
  The emitted bundle carries knowledge + SQL-generation guidance, NOT an executor.
  Triggers: "package the dbt-wiki knowledge", "build a portable analytics skill",
  "freeze the knowledge base into a bundle", "export dbt-wiki for a teammate",
  "make a shareable analytics skill", "/dbt-wiki:pack",
  "把 dbt-wiki 知識打包", "封裝成可攜知識 skill", "做一個分析 skill 給同事",
  "dbt-wiki をパッケージ化", "知識 skill を書き出す".
  Do NOT trigger for: querying the knowledge base (use /dbt-wiki:query), building
  or refreshing `.dbt-wiki/` itself (use /dbt-wiki:init or /dbt-wiki:refresh),
  adding tribal knowledge (use /dbt-wiki:ingest), or running SQL against a
  warehouse (the emitted bundle does that, with the consuming agent's own tool).
---

# dbt-wiki — Pack Workflow (emit a portable analytics skill)

`pack` reads a project's distilled `.dbt-wiki/` knowledge base and **emits a
self-contained Agent Skill folder** named `<project>-analytics/`. That folder is
portable: hand it to a teammate who has no dbt project — only their own
warehouse-connect tool (an MCP / CLI that runs SQL) — and it grounds them in the
project's semantic knowledge and tells them how to generate **correct** SQL.

The emitted bundle carries **knowledge + generation guidance, not an executor**.
The consuming agent brings execution. For the exact shape `pack` produces, this
skill is governed by [bundle-format](references/bundle-format.md) (the output
contract), instantiates [the bundle SKILL.md template](assets/bundle-skill-template.md),
and copies in [generation-guidance](references/generation-guidance.md).

## Governance — read first (hard red line)

A **real** emitted bundle freezes a real warehouse's schema, column names, and
value domains. It MUST land in the **user's own private repo** (or
`~/.claude/skills/`), **NEVER** committed into this public plugin repo — a real
bundle would leak real warehouse schema into a public artifact.

**Every example in this SKILL.md is SYNTHETIC** (`acme-analytics`,
`fct_account_monthly`, `account_id`, `report_month`, `region_code [NL, EU, APAC]`).
When you run `pack` for real, the emitted `acme-analytics/`-equivalent folder is
the user's private deliverable — do not stage it into this repo.

## Step 0 — Locate `.dbt-wiki/`

Find the knowledge base the same way `query` / `init` do — the git repo root
where `.dbt-wiki/` lives, falling back to the current `$PWD`. `pack` must read
from the SAME location `init` wrote to, regardless of where it is invoked from.

```bash
# WIKI_DIR = git repo root (where .dbt-wiki/ lives); fallback to current $PWD.
WIKI_DIR=$(git rev-parse --show-toplevel 2>/dev/null) || WIKI_DIR="$PWD"
cd "$WIKI_DIR" || { echo "Cannot cd to $WIKI_DIR"; exit 1; }

test -d .dbt-wiki || { echo "Knowledge base not initialized at $WIKI_DIR/.dbt-wiki/. Run /dbt-wiki:init first."; exit 1; }
test -f .dbt-wiki/log.md || { echo "Missing .dbt-wiki/log.md — re-run /dbt-wiki:init."; exit 1; }
```

Decide the project slug. Ask the user for the business name if it is not obvious
from the repo; kebab-case it. The emitted folder is `<project-slug>-analytics/`
and the slug must match the bundle SKILL.md frontmatter `name` (synthetic
example: `acme-analytics`).

## Step 1 — Create the bundle folder (flat skill)

Create the output folder OUTSIDE this repo (the user's private location or
`~/.claude/skills/`), as a **flat** Agent Skill — `SKILL.md` plus single-level
subfolders, no nesting — per the Flat-skill constraint in
[bundle-format](references/bundle-format.md):

```
<project>-analytics/
  SKILL.md           # instantiated in Step 4
  knowledge/         # frozen in Step 2
  references/         # copied in Step 3
  examples/           # reserved slot (Step 5)
```

## Step 2 — Freeze the knowledge layer into `knowledge/` (FLATTEN)

Copy the **curated semantic** layer from the source `.dbt-wiki/` into the
bundle's `knowledge/`: the distilled **entities** (with their `## Fields` column
cards + inline `value_domain` enums), **metrics** (with `## Calculation` +
`## Materialized Columns`), **concepts**, and the **relationships** graph — and
critically the **compound / composite join keys** carried in each relationship
edge `note` (e.g. `joins on account_id + report_month (composite key — both
columns required)`). Keep each frozen page's `derived_from` / provenance
frontmatter so the snapshot's lineage stays traceable.

**Flatten-on-freeze (CRITICAL).** The source `.dbt-wiki/` **nests**
(`entities/`, `metrics/`, `concepts/`, `_evidence/models/`, …). The emitted
`knowledge/` MUST be **FLAT** — write every frozen page as a **direct child** of
`knowledge/`, never re-introducing a subfolder. Apply the Flattening rule in
[bundle-format](references/bundle-format.md):

- slugs are already kebab-case, so write `knowledge/<slug>.md` directly;
- prefix the **page type** into the filename **only on a cross-type name
  collision** (e.g. `knowledge/metric-monthly-recurring-revenue.md`);
- **never** create `knowledge/entities/…` or `knowledge/metrics/…`.

```
✅ FLAT (what pack must emit):
  acme-analytics/knowledge/account.md
  acme-analytics/knowledge/monthly-recurring-revenue.md
  acme-analytics/knowledge/metric-monthly-recurring-revenue.md   # only on collision

❌ NESTED (forbidden — re-introduces a subfolder):
  acme-analytics/knowledge/entities/account.md
  acme-analytics/knowledge/metrics/mrr.md
```

**Drop** the mechanical layer when freezing, per the "What is dropped" rule in
[bundle-format](references/bundle-format.md): the bulky `_evidence/` pages (raw
manifest / sqlglot dumps), `index.md` / `lineage.md` / `log.md` machinery, and
any `_internal/` artifacts. The bundle carries the curated semantic knowledge,
not the full evidence base.

## Step 2.5 — Emit the physical-anchor `knowledge/_relations.md`

The frozen `knowledge/` names dbt relations (`int_x.col`) but — because the
`_evidence/` layer is dropped (Step 2) — it does **not** carry the
schema-qualified table an analyst needs in a `FROM`. For a bundle deployed at a
**repo-less target that still reaches the same warehouse**, restore the thin,
high-value anchor: for every relation the knowledge pages derive from, its
**schema + column list**. dbt-wiki ships a deterministic generator —
[`assets/build_relations_anchor.py`](assets/build_relations_anchor.py)
(PEP 723; declares `pyyaml`, so run it with `uv run`).

**Offline (default)** — schema + column names + descriptions, read from the
source `.dbt-wiki/_evidence/` pages (pack already stands on them; no manifest
or warehouse access needed). **Schema is the load-bearing piece** and is
complete; it correctly reflects dbt custom-schema concatenation (e.g. marts in
`<db>__marts`), which a single-schema assumption gets wrong:

```bash
uv run <SKILL_DIR>/assets/build_relations_anchor.py \
    --evidence-dir "$WIKI_DIR/.dbt-wiki/_evidence" \
    --knowledge-dir "<project>-analytics/knowledge" \
    --out "<project>-analytics/knowledge/_relations.md"
```

(`<SKILL_DIR>` = the directory containing this SKILL.md. If `.dbt-wiki/_evidence/`
is absent — e.g. an evidence-pruned wiki — skip this step and note in the
bundle that `FROM` schemas must be resolved live.)

**`--with-catalog` (optional, real column TYPES)** — when the target runs
against the live warehouse and you want true types / full columns for the
**canonical** relations (those the knowledge pages cite as `model.column`):
the **orchestrator** runs ONE `information_schema.columns` query *with its own
warehouse tool*, saves the JSON, and passes it. `pack` itself connects to no
warehouse (see Rules) — the query is the orchestrator's, exactly as the
consuming bundle brings its own execution.

```bash
# 1. (your warehouse tool) pull RAW column rows for the cited relations:
#      SELECT table_schema, table_name, ordinal_position, column_name, data_type
#      FROM information_schema.columns
#      WHERE table_schema IN (<schemas>) AND table_name IN (<cited relations>)
#      ORDER BY 1,2,3
#    ⚠ Do NOT LISTAGG over information_schema (unsupported on Redshift system
#      tables); pull RAW rows — the script aggregates per relation. Save the
#      tool's JSON result to /tmp/catalog.json.
# 2. merge it:
uv run <SKILL_DIR>/assets/build_relations_anchor.py \
    --evidence-dir "$WIKI_DIR/.dbt-wiki/_evidence" \
    --knowledge-dir "<project>-analytics/knowledge" \
    --out "<project>-analytics/knowledge/_relations.md" \
    --catalog /tmp/catalog.json
```

Skip `--with-catalog` when packing offline — the offline anchor (schema +
column names) already makes the bundle self-sufficient for schema-qualifying a
`FROM`; the live tool fills any missing column detail per-table on demand.

The emitted `_relations.md` is a flat child of `knowledge/` (it loads on
demand like any knowledge page). Verify the generator on first run (optional):
`uv run <SKILL_DIR>/assets/build_relations_anchor_test.py` → "6/6 passed".

## Step 3 — Copy in the generation guidance

Copy this skill's [generation-guidance](references/generation-guidance.md)
**verbatim** into the bundle's `references/generation-guidance.md`. It is the
schema-linking + five-guardrail SQL-generation guidance (aggregate level /
compound-grain joins / value-grounding / source disambiguation / temporal),
reframed for a warehouse-connected agent (generate → execute via your own tool →
iterate). Do not edit it per-bundle — it is project-agnostic reference material.

## Step 4 — Instantiate the bundle's `SKILL.md`

First capture the snapshot provenance — you fill these two values into the
template below, and they are also the snapshot annotation (see Step 6 for what
they mean):

```bash
SOURCE_MANIFEST_SHA=$(grep -m 1 'manifest_sha:' .dbt-wiki/log.md | sed 's/.*manifest_sha: //' | tr -d ' ')
BUILD_DATE=$(date +%Y-%m-%d)
```

Then copy [the bundle SKILL.md template](assets/bundle-skill-template.md) to
`<project>-analytics/SKILL.md` and fill its placeholders:

| Placeholder | Fill with |
|---|---|
| `<PROJECT_SLUG>` | the kebab-case slug (e.g. `acme`) — so `name:` becomes `acme-analytics` |
| `<PROJECT_NAME>` | the human project name (e.g. `Acme`) |
| `<PROJECT_DESCRIPTION>` | one short clause on what the project's data is about |
| `<TRIGGER_PHRASES>` | extra activation phrases (see substitution contract below) |
| `<SOURCE_MANIFEST_SHA>` | `$SOURCE_MANIFEST_SHA` captured above (source `manifest_sha` from `.dbt-wiki/log.md`) |
| `<BUILD_DATE>` | `$BUILD_DATE` captured above (today, `YYYY-MM-DD`) |

**Language — match the knowledge layer.** The packaged knowledge follows the
same source-language rule as distillation (init wrote pages in the project's
source language). Read `source_language` from `.dbt-wiki/index.md` frontmatter
(`grep -m1 'source_language:' .dbt-wiki/index.md`). Write the bundle's
**project-specific prose** in that language: `<PROJECT_DESCRIPTION>`,
`<PROJECT_NAME>` where natural, the body's "What this is" / orientation /
worked-example sections, and `<TRIGGER_PHRASES>` (use the project-language terms
a local analyst would actually type). The `knowledge/` pages are copied
**verbatim** in Step 2, so they are already in the source language — do NOT
translate them. Keep ASCII / English for the `name:` slug, the snapshot
frontmatter keys, and `references/generation-guidance.md` (the five SQL
guardrails are universal, language-neutral agent guidance, not project
knowledge — leave it as shipped).

**Substitution contract for `<TRIGGER_PHRASES>` (YAML-fragile).** The template's
frontmatter `description` is a **folded block scalar** (`>-`). `<TRIGGER_PHRASES>`
sits inside that folded block, so substitute it as a **single-line plain string**
— no leading `-`, `:`, or `#`, and **no embedded newline**. A multi-line or
list-shaped substitution breaks the folded scalar and the YAML fails to parse.
If you have several phrases, join them into one sentence (e.g.
`Also fires on "acme MRR by region", "active acme accounts this quarter".`).

## Step 5 — `examples/` slot (reserved, empty in v1)

Create the empty `examples/` folder. It is the **reserved slot** for gold
question → correct-SQL few-shot examples; in **v1 it MAY be empty**, per the
`examples/` rule in [bundle-format](references/bundle-format.md). A later
increment (gold-example generation) populates it without changing the bundle
shape. Do not invent examples here — an empty reserved slot is the v1 contract.

## Step 6 — Write the snapshot annotation

The bundle is a **point-in-time snapshot** and must record its provenance + a
rebuild pointer, per the Snapshot-annotation block in
[bundle-format](references/bundle-format.md). The
[bundle SKILL.md template](assets/bundle-skill-template.md) carries the
annotation in its **frontmatter** (`source_manifest_sha` / `build_date` /
`snapshot_note`), so prefer the frontmatter form for coherence (a separate
`PROVENANCE.md` is the documented alternative, not needed when the template
already holds it).

The `source_manifest_sha` and `build_date` you filled in Step 4 **are** this
annotation — `source_manifest_sha` is the same `manifest_sha` key `query` reads
for its drift check, so the bundle's lineage traces back to the exact knowledge
snapshot it was built from. Confirm both landed in the emitted frontmatter.

The template's `snapshot_note` already states the snapshot / re-run-`pack`
contract — no extra prose needed. (If you ever emit `PROVENANCE.md` instead, it
must carry the same three things: `source_manifest_sha`, `build_date`, and the
"snapshot — re-run `dbt-wiki:pack` to refresh; does not auto-update" note.)

## Step 7 — Verify the emitted folder is a flat valid skill

Before declaring done, verify the bundle against the Acceptance summary in
[bundle-format](references/bundle-format.md):

```bash
BUNDLE="<path-to>/acme-analytics"   # synthetic example path

# (a) SKILL.md exists and its frontmatter parses (name + the snapshot keys).
test -f "$BUNDLE/SKILL.md" || { echo "FAIL: no SKILL.md"; exit 1; }
grep -q '^name: .*-analytics' "$BUNDLE/SKILL.md" || { echo "FAIL: bad/missing name"; exit 1; }
grep -q '^source_manifest_sha:' "$BUNDLE/SKILL.md" || { echo "FAIL: missing snapshot annotation"; exit 1; }

# (b) FLAT — no subfolder contains another subfolder (single-level only).
NESTED=$(find "$BUNDLE" -mindepth 2 -type d)
[ -z "$NESTED" ] || { echo "FAIL: nested subfolders found:"; echo "$NESTED"; exit 1; }

# (c) the three expected subfolders exist; knowledge/ has direct-child pages.
for d in knowledge references examples; do
  test -d "$BUNDLE/$d" || { echo "FAIL: missing $d/"; exit 1; }
done
echo "✓ flat valid skill"
```

Confirm no placeholder leaked: grep the emitted `SKILL.md` for
`<PROJECT_` / `<SOURCE_MANIFEST_SHA>` / `<BUILD_DATE>` / `<TRIGGER_PHRASES>` — any
match means an unfilled placeholder (re-do Step 4).

## What you produced

A portable `<project>-analytics/` Agent Skill (synthetic: `acme-analytics/`) —
flat, self-contained, snapshot-annotated — that grounds a warehouse-connected
agent in the project's semantic knowledge and guides correct SQL generation. It
loads its `knowledge/` on demand (unbounded) and names no specific warehouse
tool: the consuming agent supplies execution.

## Rules

NEVER:
- Commit a **real** emitted bundle into this public plugin repo (governance red
  line — it carries real warehouse schema). The deliverable is the user's
  private artifact.
- Emit a **nested** `knowledge/` (or any nested subfolder) — the bundle must be a
  flat Agent Skill. Flatten on freeze (Step 2).
- Substitute `<TRIGGER_PHRASES>` as a multi-line or list value — it breaks the
  template's folded block scalar (Step 4 substitution contract).
- Freeze the `_evidence/` / `index.md` / `lineage.md` / `log.md` machinery into
  the bundle — only the curated semantic knowledge is frozen (Step 2).
- Connect to a warehouse or execute SQL — `pack` only packages; execution is the
  consuming bundle's job, with the agent's own tool.

ALWAYS:
- Read the source `manifest_sha` from `.dbt-wiki/log.md` and stamp it +
  `build_date` into the bundle (Step 6) — the snapshot's provenance.
- Keep frozen pages' `derived_from` / provenance frontmatter (traceable lineage).
- Carry the full **compound join key** in each relationship edge `note` into the
  frozen `knowledge/` — dropping a key column silently fans out rows downstream.
- Verify the emitted folder is a flat valid skill before declaring done (Step 7).
- Keep every example synthetic; the real bundle is the user's private deliverable.
