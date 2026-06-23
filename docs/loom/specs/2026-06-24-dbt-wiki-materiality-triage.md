# Brief — dbt-wiki Phase 2: materiality triage

Date: 2026-06-24 · Topic: sync auto-skips the redistill gate for cosmetic-only changes
Branch: dbt-wiki-redfresh-r2 (continues Phase 1, commit 9b97010b)

## Problem

When the user runs `/dbt-wiki:sync` after a dbt change that only touched
comments or `schema.yml` descriptions, sync still flags knowledge pages stale
and **prompts an LLM redistill**. The job-to-be-done: *keep the cheap daily path
quiet on cosmetic changes — only ask to spend LLM tokens when a model's
semantics actually changed.* Today sync's gate fires on ANY stale page, so a
pure-comment edit (validated real case: 19 staging models, comment/description
only) needlessly asks the user to re-distill.

## Users

The dbt-wiki maintainer running the daily/per-feature update path. Common flow:
edit models → `dbt parse && compile` → `/dbt-wiki:sync`. The dbt change is often
**already committed** by the time sync runs (so git-diff of the source is blind),
and the dbt project may not be a git repo at all. Triage must work regardless.

## Smallest End State

1. A `logic_sha` for a model = md5 of its **compiled SQL after stripping comments
   and normalizing** via sqlglot (`parse_one(sql, dialect).sql(comments=False,
   normalize=True)`); regex comment-strip fallback + `method` flag when sqlglot
   cannot parse.
2. `rescan` maintains `_internal/logic_sha_cache.json` (`{uid: {sha, method}}`):
   for each changed model it computes the new logic_sha, compares to the cached
   one, updates the cache.
3. `rescan` emits `_internal/last_rescan_materiality.json` (`{uid: "material" |
   "cosmetic"}`) for every changed model:
   - **material** if column-name-set, depends_on, materialization, OR logic_sha
     changed; or the model was added/removed; or logic_sha came from the regex
     fallback / no cached baseline exists (conservative-unknown → material).
   - **cosmetic** if the model is in `modified` (raw_code_md5 changed) but
     column-name-set, depends_on, materialization, AND logic_sha are all
     unchanged.
4. `sync` triage step: a stale knowledge page is **material** iff ANY of its
   `derived_from ∩ changed_uids` models is material (OR-aggregation). Cosmetic-
   only stale pages are dropped from the gate (left flagged stale, not
   re-distilled, surfaced in the summary). Only material pages enter the gate.

## Current State Evidence

- **Forward (gate entry point):** `dbt-wiki/skills/sync/SKILL.md` Step 2–3 — the
  gate currently fires whenever `collect_redistill_worklist.py` returns
  `total_selected > 0`. Triage inserts between work-list collection and the gate.
- **Reverse (classification hook):** `dbt-wiki/skills/rescan/SKILL.md` Step 2
  (modified-detection, ~L157–172) already compares materialization / depends_on /
  columns-COUNT / `raw_code_md5`. Note it compares column **count**, not the
  name-set — triage needs the name-set. logic_sha comparison + materiality verdict
  hook in here; the map is written near Step 6.5 (stale flagging, ~L446–471).
- **Data:** model evidence frontmatter (`skills/init/assets/SCHEMA.md` ~L468–524)
  stores `materialization`, `depends_on`, `columns`, `raw_code_md5` — **no
  logic_sha** today. Decision: do NOT add it to the page; cache it in `_internal/`.
- **Boundary (precedent):** `_internal/ownership.json` (rescan Step 6.4) is the
  precedent for a rebuildable `_internal/` JSON cache rescan reads/writes.
  `collect_redistill_worklist.py` already reads `_internal/ownership.json`.
- **Dependency present:** sqlglot is already declared
  (`skills/init/assets/extract_column_lineage.py` PEP-723) — no new dependency.

## Decision

Build **approach (B): a self-contained comment-stripped logic fingerprint**, with
the fingerprint cached in `_internal/logic_sha_cache.json` (NOT in evidence-page
frontmatter, NOT seeded by init). This touches only `rescan` (compute + cache +
emit materiality map) plus `sync` (consume the map to partition stale pages) plus
one new helper. Rejected: (A) git-diff of dbt source — blind when the dbt change
is already committed or the project isn't a git repo, silently degrading to
full-redistill exactly in the common (clean-repo) case. Industry confirmation
(WebSearch EN+JA agree): dbt's basic `state:modified` has the same file-checksum
flaw; dbt's state-aware orchestration / dbt State moved to semantic, comment-
ignoring diffs — i.e. (B). We use a normalized-SQL hash (lighter than sqlglot's
full Change-Distiller AST diff, sufficient for comment/whitespace insensitivity).

rescan stays 0-LLM and cheap (logic_sha is a deterministic local hash). Triage is
deterministic and unit-testable.

## Out of Scope

- Full sqlglot AST semantic diff (Change Distiller) — overkill; a normalized-hash
  equality is enough to separate cosmetic from material.
- Seeding the full cache via `init` — optional later enhancement; lazy build is
  the MVP (first change per model after upgrade classifies material, conservative).
- Warehouse-level data-change detection (what dbt State does on top of source
  freshness) — out of local scope.
- Changing the evidence-page frontmatter schema.
- A `--no-triage` escape hatch — defer unless a need surfaces (`--redistill`
  already forces the gate; `--force-mature` is orthogonal).

## Open Questions

- First-change-after-upgrade is classified material (no cached baseline). Accept
  the one-time over-distill, or add an opt-in `init`-seed in a follow-up? (MVP:
  accept.)
- sqlglot parse-failure rate on real compiled dbt SQL is unknown; the regex
  fallback + conservative-material handling covers it, but worth logging the
  `method` so we can measure how often the fallback fires.

## Edge cases (must be covered by tests)

1. Logic change keeping identical column names → logic_sha changes → material.
2. Comment-only change → raw_code_md5 changes, logic_sha identical → cosmetic.
3. schema.yml `description:` only → compiled SQL + columns unchanged → cosmetic.
4. Mixed material+cosmetic derived_from for one page → material (OR).
5. No cached baseline (first run) → material.
6. sqlglot parse failure → regex fallback, method flagged, → material.
7. Added / removed model → material.
8. Cross-domain stale page → triaged per its full derived_from set.
