# Changelog

All notable changes to the `dbt-wiki` plugin are documented here.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/), and this plugin adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [3.3.0] — 2026-07-24

### ⚠️ BREAKING — `/dbt-wiki:sync` renamed to `/dbt-wiki:update` (no alias)

The `sync` skill was a one-way dbt→wiki refresh, but "sync" connotes a
bidirectional operation and misled users into expecting it to push wiki
edits back into dbt. It never did — one-way discipline (never touch
`dbt/target`) is unchanged, only the name was wrong. The skill's folder,
`name:` frontmatter, and every cross-skill reference (`rescan`,
`redistill`, `init`, `query`, `review`, `ingest`, `pack`, `README.md`,
the Codex manifest's `longDescription`) were renamed via `git mv` (history
preserved, `git log --follow` traces it) — **no `sync` alias survives**.
Natural-language triggers `sync dbt-wiki` / `同步 wiki` still route to
`update`, so saying "sync" still works; the slash command
`/dbt-wiki:sync` itself no longer exists — use `/dbt-wiki:update`.

### Changed — `update` is now the full maintenance verb (was: `sync`'s one-shot orchestration)

`update`'s pipeline grew to eight steps: (optional) ingest-front →
rescan → gated redistill (with materiality triage) → **phantom-column
lint gate** (runs the existing `lint_identifier_fidelity.py`,
JSON + exit-code, no new script) → **review hand-off** (surfaces the
review queue instead of auto-certifying pages) → a structured
scorecard (regenerated pages / phantom count / pages awaiting review).
The four early-exit shortcuts that used to stop short of this pipeline
now fall through to Step 5, so "run update" mechanically completes the
whole maintenance pass instead of silently doing a partial refresh.

### Added — `using-dbt-wiki` family-entry router

New `dbt-wiki/skills/using-dbt-wiki/SKILL.md`: an obsidian-style routing
table (Setup / Input / **Maintain** — `update` is the primary verb,
`rescan` and `redistill` demoted to "advanced" — / Read / Certify /
Export) plus a Quick Start sequence (`init → (ingest) → update → query →
review`) and zh/ja trigger keywords.

### Added — CI wire-up

`dbt-wiki` gets its first CI job (`.github/workflows/test-dbt-wiki.yml`):
it globs **every `dbt-wiki/skills/*/assets/*_test.py`** — 17 scripts as of
this release — and runs each one directly, failing the job on the first
non-zero exit. Direct execution, not `pytest`: these are self-executing
smoke scripts (9 guarded by `if __name__ == "__main__"`, the other 8
running their checks at module level) with no `test_*` functions, so pytest collects
nothing from them. The glob is deliberate — a newly added script test is
picked up automatically, with no workflow edit. Previously these tests
existed but never ran anywhere.

## [3.2.1] — 2026-07-08

### Changed — pack: `_index.md` consumption is grep-first; summaries capped

A live efficiency probe on a real ~200-page bundle showed the consuming
agent reading the entire `_index.md` into context — at that scale the
index exceeds a single read (~35K tokens) and the full-read costs two
round-trips per question, while the probe's actual page hits all came
from grep-visible alias text. For an LLM consumer a large index is a
cheap **grep surface**, not a document to read:

- **Consumption contract reworded to grep-first** in all three places a
  consumer meets the index (the generated `_index.md` header, the
  bundle template's folder orientation, generation-guidance §1 step 1 +
  the Pre-flight checklist): grep the index for the question's business
  terms (the `〔aka: …〕` aliases are the designed grep surface), open
  only the pages the matching lines cite; whole-file read is the
  fallback when grep misses.
- **Index summaries capped at 80 chars** (`build_bundle_index.py
  cap_summary`, break at the latest sentence boundary inside the cap,
  ellipsis on hard cap) — the full summary lives on the page; the index
  line only needs enough gloss to disambiguate a grep hit. Measured on
  the probe bundle: summaries were 36% of index bytes. Tests 13 → 16
  cases.

All examples synthetic (`acme` / `ledger` / `stream`).

## [3.2.0] — 2026-07-07

### Added — pack: `knowledge/_index.md` retrieval entry point (Step 2.7)

A flat bundle `knowledge/` with hundreds of pages left the consuming agent
slug-guessing or grepping every file to find the right page. New deterministic
asset `pack/assets/build_bundle_index.py` (13-case TDD) emits
`knowledge/_index.md` — one line per frozen page (title, status, one-line
summary, aliases; syntheses use their `question`), grouped by page type —
derived from the **frozen pages' own frontmatter** (never the source
`index.md`, whose format varies by init version), so the index always matches
exactly what was frozen. `_`-files excluded; unrecognized `type:` lands in an
"Other pages" section rather than being silently dropped; idempotent; exits
non-zero on an empty knowledge dir. The bundle template wires it as the FIRST
read of the Ground step; generation-guidance §1 points schema-linking at it.

### Added — pack: syntheses freeze into the bundle (Step 2)

`syntheses/` pages (verified deep-dive answers — the highest-cost,
human-verified knowledge in a wiki) were silently excluded from the freeze
scope. Step 2 / bundle-format now include them alongside
entities/metrics/concepts; they freeze and flatten exactly like the other
types and are indexed under `## Syntheses`.

`flatten_links.py` was extended to make that true (caught by branch review —
a synthesis page frozen with the old flattener left broken links that
deterministically failed Step 2.6): `syntheses` joins the knowledge-folder
flatten set, and the `_evidence`-only delink regex is generalized to **any
remaining pathed `.md` link** — covering the SCHEMA-synthesis
`.dbt-wiki/_evidence/…` shape, `_archive/`, and source-repo paths
(`../../models/…`), all dead at a portable target. Test suite 6→10 cases,
including an end-to-end SCHEMA-shaped synthesis page.

### Added — pack Step 7: frontmatter YAML-parse + page-count parity checks

Two acceptance gaps closed:

- **(a2) YAML parse.** The most-warned pack failure mode — a bad
  `<TRIGGER_PHRASES>` substitution breaking the template's folded block
  scalar (bundle dead on arrival: skill never triggers) — passed Step 7,
  whose checks were grep-only. A real `yaml.safe_load` of the emitted
  `SKILL.md` frontmatter now gates acceptance.
- **(c2) page-count parity.** Step 2 is a manual copy; a silently omitted
  page passed every existing check. Step 7 now compares source knowledge
  page count (entities/metrics/concepts/syntheses) against frozen bundle
  count (`_`-files excluded) and fails on mismatch.

### Changed — generation-guidance: `_relations.md`-first column confirmation, checklist-first structure, `(via:)` trust tiers

- **§1.3 contradiction fix (consumer-efficiency).** §1.3 claimed the bundle
  has "no offline column dump to cross-check against" and told the consumer
  to probe the live warehouse per column — but Step 2.5 ships exactly that
  dump as `knowledge/_relations.md`. §1.3 now routes column confirmation to
  `_relations.md` first; live-probe only for "needs introspect" relations,
  columns absent there, or drift suspicion. Execution remains the only gate.
- **Checklist-first.** The summary checklist sat at the very end of a file
  the consumer is told to read before every generation. It now leads the
  file as a "Pre-flight checklist" with §-anchors — scan per question, drill
  into only the guardrails the question touches. §8 reduced to a pointer.
- **`(via:)` confidence tiers (§4).** The value_domain provenance tiers the
  native `query` skill already teaches (`accepted_values` = CI-enforced /
  `distinct` = sampled, can drift / `inferred` = provisional hypothesis)
  never reached the bundle — a consumer trusted an inferred enum like a
  CI-enforced one. §4 now states the tiers and the per-tier behavior.

### Changed — bundle-skill-template: dedup the §0 rationale, wire `_index.md`

The template's "Why execution is the only gate" callout duplicated guidance
§0 almost verbatim (~10 lines loaded into every consumer's context, already
drifting). It is now a 3-line pointer at §0; the rationale lives only in
generation-guidance. The Ground step and folder orientation now route page
discovery through `knowledge/_index.md`, and the guidance bullet says "scan
the Pre-flight checklist" instead of "read the whole file".

All examples remain synthetic (`acme-analytics`, `account.md`, `mrr.md`).

## [3.1.1] — 2026-07-05

### Fixed — Codex dispatch-portability (per-host reference files for Phase B fan-out)

`init`'s Phase B parallel orchestration (inherited by reference in
`redistill` §Step 3) already phrased subagent dispatch in host-neutral
prose but had zero per-host reference file (Codex dispatch-portability
survey finding, `docs/skill-mining/2026-07-05-codex-dispatch-
portability-survey.md`). Added `init/references/{claude-code-tools.md,
codex-tools.md}` and pointed `init/SKILL.md` + `redistill/SKILL.md` at
them.

## [3.1.0] — 2026-06-24

### Added — materiality triage in `sync` (Phase 2): cosmetic-only changes skip the LLM gate

`sync` no longer prompts a (paid, non-deterministic) `redistill` when the dbt
change that flagged knowledge pages stale was **cosmetic only** — a comment /
whitespace / `schema.yml` description edit that did not change a model's meaning.
Only **material** evidence changes (column add/remove/rename, `depends_on` /
lineage, materialization, or a logic change) reach the gate.

How it works (all deterministic, `rescan` stays 0-LLM):

- **`logic_sha`** (`rescan/assets/logic_sha.py`, 10-case TDD) — a comment-stripped,
  sqlglot-normalized SQL fingerprint (regex fallback + `method` flag when sqlglot
  can't parse). Comment/whitespace edits leave it unchanged; logic edits change it.
- **per-model classifier** (`rescan/assets/classify_materiality.py`, 14-case TDD) —
  labels each changed model material/cosmetic by comparing column-name-set,
  `depends_on`, materialization, and `logic_sha` against a baseline cached in
  `_internal/logic_sha_cache.json`; `rescan` Step 2.6 emits
  `_internal/last_rescan_materiality.json`.
- **page-level triage** (`sync/assets/triage_worklist.py`, 10-case TDD) — a stale
  page is material iff ANY of its `derived_from` changed-models is material
  (OR-aggregation). `sync` Step 2.5 drops cosmetic-only pages from the gate
  (kept flagged stale, surfaced, not re-distilled). All-cosmetic → cheap exit 0,
  no prompt.

Industry-aligned (dbt's own `state:modified` has the file-checksum flaw; dbt
state-aware orchestration moved to comment-ignoring semantic diffs). Fallback:
when `last_rescan_materiality.json` is absent (a `rescan` from before this
feature, or first upgrade) `sync` treats all stale pages as material — never
blocks. No evidence-page schema change; `init` untouched.

## [3.0.0] — 2026-06-24

### Changed (BREAKING) — `/dbt-wiki:refresh` → `/dbt-wiki:rescan`

The `refresh` command is renamed to `rescan`. `refresh` over-promised: it reads
as "fully re-sync everything", but the command only rebuilt the cheap mechanical
**evidence** layer (manifest diff + sqlglot lineage) and *flagged* knowledge
pages stale — it never re-distilled the semantic layer. `rescan` names exactly
what it does: re-scan the evidence, 0 LLM, safe to run daily.

Migration: replace `/dbt-wiki:refresh` with `/dbt-wiki:rescan` — behaviour is
otherwise identical. Existing `.dbt-wiki/` vaults need no change; historical
`refresh` log entries are left as-is.

### Added — `/dbt-wiki:redistill` (the LLM half — fast-follow now shipped)

Re-distills the knowledge pages `rescan` flagged stale so their semantic prose
catches up with the changed evidence.

- Deterministic work-list (`redistill/assets/collect_redistill_worklist.py`,
  13-case test): stale + non-mature + non-archived pages **with provenance**,
  grouped by the domain owning the majority of their `derived_from` evidence
  (via `_internal/ownership.json`). Falls back to a single `(all)` group when
  ownership.json is absent (small / sequential init had no domain fan-out).
- Skips human-certified `mature` pages by default (`--force-mature` to include).
  **Delegates** the actual distillation to init's `references/distill-*.md`
  (single source of truth — no copied logic), then runs reconcile +
  lint_identifier_fidelity + build_index_knowledge. `--dry-run` / `--yes`.
- User-triggered only: LLM cost + non-determinism stay off the daily path.

### Added — `/dbt-wiki:sync` (one-shot orchestrator)

"Just bring my wiki up to date": runs `rescan`, then if it left knowledge pages
stale, **gates** an LLM `redistill` behind an explicit yes (non-interactive
default = no). Delegates to both sibling skills — owns the sequencing + the gate,
never reimplements their logic. `--no-redistill` / `--redistill` / `--yes` /
`--force-mature` / `--dry-run`.

### Notes

- Command-reference cross-links updated repo-wide (init / query / review /
  ingest prose, init asset templates, README ×3). `pack`'s "re-run to refresh"
  is the English verb, not the command — left unchanged.
- Phase 2 (materiality triage in `sync`, so cosmetic-only changes skip the gate)
  is the next fast-follow.

## [2.14.1] — 2026-06-20

### Changed — `query` leverages `value_domain` (value-grounded answers)

`init` §3.4 captures `value_domain` enums on categorical columns so a consumer
can map a user's colloquial term to the exact stored warehouse value — the
packed `pack` bundle's generation-guidance uses this, but the native
`/dbt-wiki:query` skill never did (it had no value-domain query class and zero
`value_domain` references). So a "what statuses exist?" question, or a filter
implied by an answer, wasn't grounded on the stored values the knowledge base
already records.

`query/SKILL.md` adds **query class K4 — Value domain / categorical values**
(load the column's `## Fields` `value_domain`, surface the stored values verbatim
+ the `(via:)` confidence, and map a colloquial label to the exact stored
literal, flagging the difference) plus a Step-4 synthesis note to quote stored
values verbatim and ground equality filters on them. Doc-only; no script,
schema, or other-skill change — `ingest` needs no change (it only appends User
Notes and never touches distillation / value_domain).

## [2.14.0] — 2026-06-20

### Added — `lint_identifier_fidelity.py` build-time gate (phantom-column citations)

A behavioral dogfood of a packed bundle (financial-reporting domain, ~60+ leaf
columns per table) surfaced a class of knowledge defect the existing gates miss:
a `## Fields` table citing a `model.column` that **does not exist** in the
manifest (a dropped `__daily` suffix, an invented prefix, a bare name for a
column that was split in two). A SQL-generating consumer then emits a query
referencing a non-existent column that fails at execution — and nothing in the
page looks wrong on inspection. A deterministic sweep of one real bundle found
4 such phantom citations among 906 (the other 902 were correct).

New `assets/lint_identifier_fidelity.py` (+ test, 8/8) cross-checks every
`` `model.column` `` cited in `entities/` / `metrics/` / `concepts/` against the
model's evidence `columns:` frontmatter, verifying **only** `sqlglot`-extracted
models (complete output-column set); citations to `schema_yml_only` / `failed`
models or non-evidence relations are skipped as unverifiable, never flagged
(zero false positives). Exit non-zero ⇒ phantom citations exist. Deterministic,
pure stdlib, reads `.dbt-wiki/` only. Wired into `init` (copy-loop + new Step
6.8 gate after reconcile) and `refresh` (copy-loop + knowledge-regen note).
Complements `lint_schema_divergence.py` (twin schema-delta documentation) — that
checks whether divergence is *documented*; this checks whether cited columns
*exist*.

## [2.13.4] — 2026-06-20

### Changed — distill-entities §3.4 hardens value_domain adherence

A behavioral dogfood of a packed bundle hit a recurring distillation miss: a
small-cardinality categorical column (a sales-funnel stage column) had its values
listed in the `## Fields` Meaning **prose** but carried no machine-readable
`value_domain` annotation — so a SQL-generating consumer could not turn the
categorical filter into a literal and had to guess. A sweep found several more
state/classification columns with the same prose-only pattern. The §3.4 rule
already required value_domain for ≤20-value categoricals; the gap was adherence,
not the rule.

`references/distill-entities.md` §3.4 now states an explicit **prose-enumeration
hard trigger**: if a column's discrete values appear anywhere in its Meaning
prose, the distiller MUST also emit the `value_domain: [...]` annotation in the
same cell (prose is an obligation to annotate, never a substitute). Adds the
companion guidance for filter-critical lifecycle/stage columns whose
terminal-state semantics are ambiguous: capture the stored values, and add a
`## Caveats` note where the business meaning needs human confirmation. Spec-prose
only — no script or data-path change.

## [2.13.3] — 2026-06-20

### Changed — emitted bundle handles the no-warehouse-tool case gracefully

A behavioral dogfood of a packed bundle (cold-reader probe) surfaced a
cold-start gap: the bundle SKILL.md's generate→execute→inspect loop assumes the
consuming agent has a warehouse-connect tool, but said nothing about what to do
when it has **none** — leaving a first-timer blocked at step 3 with no guidance.

`assets/bundle-skill-template.md` step 3 (Execute) now adds a no-tool
degradation clause: if nothing in the environment can reach the warehouse, the
agent delivers the grounded SQL, tells the user it needs a SQL-executing tool,
and states the connection prerequisites (the warehouse engine, any VPN /
credentials, and the dev-schema prefix to substitute) — rather than fabricating
an answer. Project-specific connection details stay in each emitted bundle, not
the template (generic, no warehouse schema leaks). Template-only change; no
script or data path affected.

## [2.13.2] — 2026-06-20

### Changed — trim the `review` skill description to the house standard

`review` (926 chars) was the last dbt-wiki description over the 250 cap
(the other five shipped in 2.13.1). Trimmed to 229: what + when + one CJK
trigger (審核) + a positive redirect to `query`; dropped the trilingual
trigger list and the "Do NOT trigger for X" block. Metadata only — no
behavior change; body untouched. Routing verified by a blind A/B
(routes to ground truth).

## [2.13.1] — 2026-06-20

### Changed — trim 5 skill descriptions to the house description standard

The `query` / `ingest` / `init` / `refresh` / `pack` skill `description` fields
(1156–1731 chars) were over the 1024 spec ceiling and well over the house
standard's 250 cap. Trimmed to 239–248 chars each: kept what + when + positive
triggers (one representative CJK trigger each) and the lifecycle redirects
(setup→init, updates→refresh, ask→query); moved the exhaustive bilingual
trigger lists and the "Do NOT trigger for X" blocks out of the description.
Metadata only — no skill behavior change; bodies untouched. Triggering parity
verified by a 12-probe blind A/B (old vs new routed identically, 12/12 to ground
truth, including 7 CJK/bilingual prompts and the init↔refresh boundary). See
`docs/skill-mining/2026-06-19-skill-description-standard.md`.
## [2.13.0] — 2026-06-20

### Added — deterministic Phase-B finalization scripts (index regen + reconcile)

Two Phase-B finalization steps were specified as prose only, so the orchestrator
hand-implemented them each init — error-prone and token-expensive at 50–120
knowledge pages. Both are now shipped, tested scripts.

- **`build_index_knowledge.py`** (+ test, 8/8): regenerates `index.md`'s
  `## Entities` / `## Metrics` / `## Concepts` sections deterministically from
  each knowledge page's frontmatter (`title` / `title_local` / `status` /
  `summary` / `aliases`) in the SCHEMA canonical line shape, updates the
  `- Knowledge pages:` stats line, and leaves the evidence sections untouched.
  Previously `build_evidence_pages.py` only wrote stub placeholders and Phase B
  Step 6 / refresh Step 6 said "regenerate by hand".
- **`reconcile.py`** (+ test, 11/11): the Step 6.7 reconcile pass — scans every
  `relationships[].target`, warns on a missing reserved-entity slug or writes a
  `status: seed` stub for a genuine dangling reference, and lints `derived_from`
  cross-domain contamination via `_internal/ownership.json`. Degrades gracefully
  when `ownership.json` is absent (small projects with no domain fan-out): every
  dangling ref is stubbed and the contamination lint is a no-op.

Both are wired into `init` (Step 4 copy loop, Phase B Step 6, Step 6.7) and the
index regen into `refresh` (Step 6 + the rebuildable-cache bootstrap). Pure
stdlib + pyyaml, idempotent, no project specifics.

## [2.12.1] — 2026-06-19

### Changed — `init` lands only production scripts, not the one-shot `*_test.py`

Follow-up to 2.12.0's "`_internal/` is a rebuildable cache". `init` copied both
the 7 production extraction scripts **and** their 7 `*_test.py` into
`.dbt-wiki/_internal/`, but the smoke tests run once at first-init verification
and are dead weight on disk thereafter (gitignored since 2.12.0, but still
cluttering the working tree). `init` now copies **only the 7 production scripts**
(+ `synthesis_template.md`, copy block compacted to a loop); the optional Step 4c
/ 4g / evidence-generator smoke tests run in-place from `<SKILL_DIR>/assets/`.
Halves the `.py` landed in the user's repo (14 → 7) with no change to the
production data path; `refresh` is untouched (it invokes no `*_test.py`).

## [2.12.0] — 2026-06-19

Three generic defects surfaced by a behavioral dogfood of a packed analytics
bundle, fixed at the plugin source so every project benefits.

### Fixed — `pack` flatten no longer breaks in-page links

Flatten-on-freeze relocates pages to a flat `knowledge/` but copied their
content verbatim, so cross-folder links (`[X](../entities/x.md)`) and dropped
`_evidence/` citations stayed nested and broke in the bundle — **766 broken
links** on one real bundle. New **Step 2.6** + `pack/assets/flatten_links.py`
(stdlib, idempotent, pure path-shape; `flatten_links_test.py`, 6/6) rewrites
cross-folder links to flat siblings (`[X](x.md)`) and delinks dropped-evidence
references to plain label text. Step 7 acceptance now gates on **zero broken
intra-`knowledge/` links**; `references/bundle-format.md` documents the rule.

### Added — bundle carries the warehouse SQL dialect

`init` resolved the sqlglot dialect (Step 4a) but never persisted it, and
`pack` reads only `.dbt-wiki/`, so a repo-less consuming agent had no way to
know which SQL dialect to generate (date functions, casts, concatenation differ
by engine). `init` now writes `dialect:` into `index.md` frontmatter (next to
`source_language:`); `pack` reads it into a new `<WAREHOUSE_DIALECT>` template
placeholder, emitting a **"Warehouse engine"** line in the bundle SKILL.md.
Engine ≠ a specific MCP/CLI, so tool-agnosticism is preserved.

### Changed — `_internal/` is a rebuildable cache, self-healed by `refresh`

The `_internal/` extraction scripts are mechanical copies of the plugin's own
`assets/`, yet `init` landed them permanently in the user's repo (14 `.py`
including 7 one-shot `*_test.py`) and `refresh` hard-failed if they were absent
("re-run init"). Result: scripts duplicated into every repo, committed to git,
and drifting on plugin upgrade. Now `init` emits a `.dbt-wiki/.gitignore`
ignoring `_internal/` + `__pycache__` (with a `git rm --cached` note for repos
that already tracked it), and `refresh` **self-heals** `_internal/` from the
plugin's init assets (`<SKILL_DIR>/../init/assets`) instead of erroring — so a
fresh clone with a gitignored `_internal/` just works. `SCHEMA.md` documents
`_internal/` as rebuildable tooling, not knowledge state.

## [2.11.0] — 2026-06-18

### Added — `pack` physical-anchor layer (`knowledge/_relations.md`)

`dbt-wiki:pack` drops the `_evidence/` layer when freezing a bundle — correct
for semantic grounding, but it loses the one physical fact the knowledge layer
cannot supply: the **schema-qualified table**. A bundle deployed at a repo-less
target (no dbt project, no `.dbt-wiki/`) that still reaches the same warehouse
then can't write a runnable `FROM <schema>.<table>`.

New **Step 2.5** + `assets/build_relations_anchor.py` (stdlib + pyyaml via
PEP 723; `assets/build_relations_anchor_test.py`, 6/6) emit
`knowledge/_relations.md`: for every relation the knowledge pages derive from,
its **schema** (offline from the source `_evidence/` pages — complete, and
correctly reflecting dbt custom-schema concatenation like `<db>__marts`, which
a single-schema assumption gets wrong) + its **column list** (offline names +
descriptions, or real **types** via the optional `--with-catalog` live-warehouse
merge — the orchestrator runs the `information_schema.columns` query with its
own tool; `pack` still connects to no warehouse). Deliberately NOT a re-import
of the evidence layer — no lineage / raw SQL / materialization, only the
relation→schema→columns map a warehouse-connected agent needs to qualify a
`FROM`. The bundle SKILL.md template + `references/bundle-format.md` now
document `_relations.md` and the schema-qualification step.

## [2.10.0] — 2026-06-17

### Added — deterministic Phase A evidence-page generator

Phase A previously described page emission as "for each model, write
`<model>.md`" — infeasible beyond a few dozen models (real projects have
hundreds–thousands). Init now ships `assets/build_evidence_pages.py`
(stdlib-only, with `build_evidence_pages_test.py`): a deterministic
generator that consumes `manifest.json` + the sqlglot/comment JSONL and
emits **every** evidence page (models / sources / used-macros / seeds /
snapshots / singular tests) plus `index.md` and `lineage.md`, exactly per
the SCHEMA.md page contracts. Step 4 copies it; Step 5 invokes it instead
of describing a per-model hand-write.

### Added — Phase B persistence verification gate + deliverable contract

Hardened Phase B fan-out against the "agent analysed but never wrote
files" failure mode. New **Step 6.6 persistence gate** runs after fan-out
and before reconcile: it counts pages on disk, cross-checks each domain's
return manifest against actual files, retries failed domains with an
explicit "files are the deliverable" directive, and — for harnesses where
spawned/async agents don't reliably persist — switches to a
**return-and-materialize** shape (agent returns `{folder, slug, content}`
via structured output; the orchestrator writes the files). A new
"deliverable contract" subsection states that a domain agent's deliverable
is files on disk, never its reply message.

No SCHEMA changes (schema stays frozen for v2.x); both items are additive
to the init workflow + assets.

## [2.9.0] — 2026-06-16

### Changed — canonical-model selection rule in distillation specs

Sharpened how Phase B picks the **canonical model** for an entity or
metric when several models carry the same data at a similar grain (a
dimension plus a dashboard/export reshape, or per-segment / per-region /
per-brand / per-scenario twins). Previously the specs said only "the
mart / fact / dimension model that carries the grain" — ambiguous when
more than one candidate exists.

The rule now states that **DAG position and authority are different
axes**: moving downstream means *more specialized*, not *more
authoritative*. The canonical model is the **most-downstream model that
is still general-purpose** — bounded below by a floor (never a `stg_` /
single-attribute fragment) and above by a ceiling (never a
presentation / export / per-segment leaf, which is a narrower copy). The
`feeds_into` fan-out count is a canonicality signal **only within** the
assembly layer, never across layers.

- `references/distill-entities.md` — new §2.1 "Picking the canonical
  model when several models share that grain"; cross-reference added to
  §3.3 (Evidence column rule) and a new §7 anti-pattern row.
- `references/distill-metrics.md` — parallel guidance on the §3a
  "Source model" bullet, including a `[bug]`-tagged caveat to flag
  structurally parallel twins with a **different measure basis**
  (tax-inclusive vs tax-exclusive, differing currency) that must not be
  naively UNION-ed or summed.

Affects future `init` / `refresh` distillation only; existing knowledge
pages are unchanged until re-distilled.

## [2.7.0] — 2026-06-05

### Added — `/dbt-wiki:review` certification command

A new `review` skill provides a prioritized review queue for wiki pages
that need human verification. It surfaces `developing` pages alongside
stale `mature` pages (those not reviewed within the configured staleness
window) in a ranked order that highlights risk signals:

- `(via: inferred)` value-domain entries — automatically inferred values
  that have not been human-confirmed.
- `[bug]` / `[no-test]` caveat tags — known defects or untested
  assertions in the page's Caveats block.
- Inbound reference count — pages cited by many other pages carry higher
  risk if their content is wrong.

Reviewing a page promotes it from `developing` to `mature` (or resets a
stale `mature` page's certification clock) and stamps `reviewed_by` /
`reviewed_at` fields on the frontmatter. A `## [date] review | …` log
entry is appended to the page's History section. Stale `mature` pages
are flagged for re-review; they are never automatically demoted.

### Changed — metric fork standard in `distill-metrics.md` §3b

The rule governing when a metric variant forks to a separate page has
been made more precise. A metric forks only when:

- **Grain differs** — the entity-key dimensionality changes (e.g.,
  order-level vs. customer-level aggregation), or
- **Measure definition differs** — including `ratio`, `derived`, or
  `conversion` metric types whose formula or base events diverge.

Variants that differ only by a dimension value (source, scenario, time
period, region, or business unit) stay on one page as documented
variants. This replaces the prior segment-only guidance and eliminates
ambiguity for multi-axis variant decisions.

## [2.6.0] — 2026-06-05

### Added — parallel orchestration spec for large projects (Phase B)

Distill runs on large projects can now fan out per-domain subagent workers
rather than executing serially. An internal ownership registry
(`.dbt-wiki/_internal/ownership.json`) tracks reserved-slug ownership and
domain→unique_id maps so concurrent workers do not collide on shared slugs.

- **Per-domain subagent fan-out** — each domain runs its own distill agent in
  parallel; the orchestrator coordinates wave boundaries and dependency order.
- **`.dbt-wiki/_internal/ownership.json`** — new reserved file (not a wiki
  page). Stores two maps: `reserved_slug → owner_domain` and
  `domain → [unique_id, ...]`. Created before fan-out; updated atomically by
  each worker at commit time.
- **Step 6.7 reconcile pass** — post-fan-out reconciliation distinguishes
  reserved-owner-failed pages (emit `WARNING`, keep existing owner) from
  genuine dangler stubs (status remains `seed`). Cross-domain `derived_from`
  contamination is flagged as a lint warning; workers must not emit
  `derived_from` references that cross domain boundaries without explicit
  approval.

### Added — `has_metricflow` pre-fan-out gate

An orchestration guard checks whether the project uses MetricFlow (semantic
layer) before launching metric-domain agents. On SQL-derivation projects
(where metrics are defined directly in SQL models rather than via the
MetricFlow DSL), metric agents skip the MetricFlow branch entirely, avoiding
spurious "no semantic manifest found" warnings.

### Added — `/dbt-wiki:refresh` pre-stale `derived_from` domain-consistency lint

`refresh` now runs a WARNING-only lint pass before executing any distill
steps. The pass checks whether existing `derived_from` references in the
current wiki cross domain boundaries in a way that is inconsistent with the
ownership registry. The lint is gated: it fires only when
`ownership.json` is present; projects without the registry are unaffected.
No pages are modified; findings are printed as warnings for human review.

### Added — optional `## Caveats` severity/type tags across distill specs

Caveat blocks in distill agent specs (`distill-concepts.md`, `distill-entities.md`,
`distill-metrics.md`) now support structured severity/type inline tags:

- `[bug]` — known incorrect behavior
- `[limitation]` — known capability boundary
- `[temporal]` — time-sensitive or likely to change
- `[no-test]` — assertion not covered by an automated test

Tags are optional; untagged caveats remain valid. Consumers may use tags to
filter or prioritize caveat display.

## [2.5.0] — 2026-06-04

### Added — recall pack: SCHEMA v2.1 (additive-optional; v2.0 pages remain valid)

Four optional frontmatter keys added to the page contract; existing pages require
no changes.

- **`aliases`** — list of project-language synonyms, GL codes, and abbreviations
  for a model or entity (e.g. `[ARR, MRR, 月次経常収益]`). Distill agents
  auto-emit this field by extracting un-bridgeable project terms from page
  bodies; no human gate required. Index lines surface aliases so tiered query
  matches project-language terms directly.
- **`title_local`** — project-language title for the model or entity (parallel to
  the English `title`). Auto-emitted alongside `aliases`; fully automatic.
- **`reviewed_by`** / **`reviewed_at`** — review lifecycle markers (reviewer
  identity + ISO date). Workflow is deferred; keys are reserved in the schema now
  so pages written today are forward-compatible.

### Added — value-domain provenance marker

Value-domain lists now carry a `(via: accepted_values | distinct | inferred)`
provenance tag so text-to-SQL consumers can distinguish ground-truth enums
(sourced from dbt `accepted_values` tests or a live `DISTINCT` query) from
inferred values (extracted heuristically from column descriptions or sample rows).

### Changed — value-domain rule relaxed to permit-but-tag

The previous rule ("list only production values; omit hypotheticals") is relaxed
in both `SCHEMA.md` and `distill-entities.md §3.4`: inferred values are now
**allowed** when tagged `(via: inferred)`. Ground-truth values continue to be
preferred; the tag makes the epistemic status explicit rather than silently
excluding uncertain-but-useful entries.

## [2.4.0] — 2026-06-03

### Added — `pack`: export the knowledge base as a portable analytics skill

dbt-wiki is repositioned as a **knowledge / context layer**, not a query
engine. Real-data dogfood + an industry scan (Vanna, Wren AI, dbt MCP +
MetricFlow, dbt-labs' own agent skills) confirmed the differentiator is not
another NL→SQL engine but **portable curated knowledge** an agent can carry to
wherever it already has warehouse access. The new `/dbt-wiki:pack` skill freezes
the distilled `.dbt-wiki/` knowledge into a self-contained, portable Agent Skill
folder (`<project>-analytics/`) that a downstream agent uses **with its own
warehouse-connect tool** to ground, generate, execute, and iterate on SQL.

**New skill — `skills/pack/`** (owner-run packager):
- `SKILL.md` — 8-step packager: locate `.dbt-wiki/` → create the flat
  `<project>-analytics/` bundle → **freeze** the knowledge layer into a flat
  `knowledge/` (flatten-on-freeze: source nests, bundle stays flat) → copy the
  generation guidance → instantiate the bundle `SKILL.md` from the template →
  reserve `examples/` → write the snapshot annotation (source `manifest_sha` +
  build date + rebuild pointer) → verify the emitted folder is a flat valid skill.
- `references/bundle-format.md` — spec for the emitted bundle (flat-skill
  constraint, portability into `~/.claude/skills/`, on-demand knowledge, the
  snapshot-annotation block).
- `references/generation-guidance.md` — the to-sql semantic guardrails
  (aggregate form · join-grain / fan-out · value-grounding · source
  disambiguation · temporal) + schema-linking, **reframed for a
  warehouse-connected agent**: generate → execute via your own tool → inspect →
  iterate. **Execution is the only gate** — there is deliberately no static
  existence check (see Removed below for why).
- `assets/bundle-skill-template.md` — the emitted bundle's `SKILL.md` template
  (tool-agnostic 4-step consumption procedure; names no specific warehouse tool).

### Removed — the `to-sql` runtime shell (BREAKING)

`skills/to-sql/` is retired. Its never-execute, in-repo NL2SQL design was a half
solution (a generator that can't run its own output can't catch the semantic
errors that only execution reveals). Its semantic guardrails are preserved in
`pack/references/generation-guidance.md`. `/dbt-wiki:to-sql` no longer exists;
use `/dbt-wiki:pack` to export an analytics bundle and run SQL through your own
warehouse tool. README Skills tables (en / ja / zh-TW) updated; two stale
cross-references repointed (`SCHEMA.md`, `distill-entities.md`).

**The static SQL validator was dropped, not carried forward.** A synthetic
end-to-end pack dogfood surfaced that a static existence check (parse SQL → look
up tables/columns in a frozen schema) has no coherent home in a portable
**snapshot** bundle: the live warehouse drifts (columns added / renamed /
dropped) and the bundle does not auto-update, so a frozen check gives false
confidence (a dropped column still "exists" in the snapshot) or false errors (a
new column the snapshot never saw). It also could not see the dangerous
errors — semantically-valid wrong-number bugs — which only execution reveals.
The validator (`validate_sql.py` + its 16-case test, a relic of the
never-execute `to-sql` design) was therefore removed; `knowledge/` **grounds**
generation, execution **gates** it.

Pure spec/markdown; no warehouse driver in dbt-wiki itself (warehouse-agnostic
by design); all examples synthetic.

### Deferred (noted, not in this release)

- **Gold-example generation** into the bundle's reserved `examples/` slot.
- **`init` catalog.json / connect value_domain enrichment** (OQ-A mechanism).
- **A synthetic `acme-analytics/` demo bundle** (must live OUTSIDE `skills/` to
  avoid skill-in-skill nesting).

## [2.3.0] — 2026-06-02

### Added — to-sql semantic correctness guardrails (dogfood-driven)

Real-data dogfood (5 axes on a live warehouse) showed the to-sql static
validator (sqlglot parse + manifest existence) catches syntax + hallucination
but **not** semantic errors — valid SQL that returns the wrong number, which a
non-SQL user can't detect. Observed: aggregation form (avg-order-value 3x
divergence between `SUM/SUM` and `AVG(row-ratio)`), join-grain fan-out (84x row
inflation from a partial join key), value-grounding (a region/city filter using
the user's term instead of the stored code → 0 rows), and source ambiguity (the
same business term answerable by two tables with different figures). This
release closes those gaps in two layers.

**Prompt guardrails — `to-sql/references/prompt-assembly.md`** (added as §4
sub-sections; no renumber of §5–§8):
- **§4e Aggregate Semantics** — derived ratios/averages default to aggregate-level
  `SUM(num)/SUM(denom)`, never `AVG(row-ratio)`; prefer the metric page's
  `## Calculation` form; state the form used (§8i).
- **§4f Join Grain / Fan-out** — JOINs must use the full/compound grain key from
  the relationship edge's `note`; warn on grain mismatch; never `SUM` over
  fanned-out rows (§8j).
- **§4g Value Grounding** — categorical filters use the knowledge page's
  `value_domain` enum if present, else don't assume user-term = stored-value
  (`ILIKE`/assumption); record the mapping (§8g).
- **§4h Source Disambiguation** — when ≥2 sources answer the same term, surface
  both with their basis instead of silently picking (§8h).
- Wired into the §6 prompt template; §8 output contract gains assumption
  surfaces §8g–§8j (joining the existing §8e temporal / §8f NULL-ordering).

**Knowledge-layer capture (so the guardrails have authoritative data)**:
- `assets/SCHEMA.md` — Relationships spec now requires the edge `note` to record
  the **compound join key** (all key columns); knowledge-entity gains optional
  **`value_domain` capture** (body annotation, ≤20-distinct threshold) for small
  categorical columns.
- `init/references/distill-metrics.md` §5 — derived-ratio metrics MUST define
  their aggregation form (aggregate-level vs avg-of-row-ratios).
- `init/references/distill-entities.md` §3.4 — `## Fields` distillation captures
  `value_domain` for small categorical columns, aligned with SCHEMA.

Pure spec/markdown; no warehouse/execution; all examples synthetic. The static
validator itself also gained two same-family false-positive fixes earlier on
this line (SELECT-alias and CTE-name exclusion) with a regression-lock test set.

## [2.2.0] — 2026-06-02

### Added — `to-sql`: natural-language → SQL skill (NL2SQL part 1, zero-shot)

The first consumer skill that turns the knowledge base into actual queries.
`/dbt-wiki:to-sql` takes a natural-language **business question** and generates
a **runnable SQL query** grounded in the distilled knowledge — distinct from
`/dbt-wiki:query`, which *explains* the data (meaning + lineage). This is
part 1 (the in-repo runtime consumer) of the NL2SQL effort; a portable
packager that exports a standalone skill is a planned follow-up.

Architecture reuses what the knowledge base already provides — the schema is
already decomposed into semantic entities with summaries + a typed relationship
graph, so retrieval reuses `query`'s tiered loading rather than standing up a
vector store. Research backing (dbt Semantic Layer benchmark, RASL / SAFE-SQL):
business-vocabulary→physical-column mapping is the dominant NL→SQL accuracy
lever; the metric **column cards** (v2.1.0) feed this directly.

- **`skills/to-sql/SKILL.md`** — pipeline: pre-condition + `manifest_sha` drift
  check (reuses `query` Step 0) → retrieve schema context → assemble prompt →
  generate SQL (project's adapter dialect) → **static-validate** → present
  (SQL + cited knowledge pages + validation result + drift caveat).
- **`skills/to-sql/assets/validate_sql.py`** (+ test) — static validator:
  sqlglot parse + referenced table/column extraction (with SQL-alias→model
  resolution), checked for existence against `manifest.json` (optional
  `catalog.json` enrichment). Missing tables/columns are surfaced so a
  hallucinated column is caught before the SQL is presented. Manifest-load
  failure returns a structured error rather than raising. 9/9 tests pass.
- **`skills/to-sql/references/retrieval.md`** — what to pull (entities + field
  dictionaries, metrics incl. `## Materialized Columns` cards, concepts,
  `relationships` join-paths, `_evidence/` backing columns) and how to handle
  not-found / ambiguous / too-broad.
- **`skills/to-sql/references/prompt-assembly.md`** — schema-linking, column-card
  preference (SELECT the pre-built column, don't re-aggregate), join-path
  assembly, an explicit **empty few-shot slot** (v1 is zero-shot; gold examples
  are a planned increment), output contract, and the dialect rule.

**Boundary (unchanged hard rule):** `to-sql` **generates** SQL but **never
executes it and never connects to a warehouse** — validation is static only
(parse + manifest existence).

Zero changes to `init` / `query` / `refresh` core logic; `to-sql` is additive.
READMEs (en/ja/zh-TW) gain a `to-sql` row disambiguating it from `query`.

## [2.1.0] — 2026-06-02

### Added — metric column cards (materialized-metric mapping)

Completes the v2.0 minimal-state knowledge layer (knowledge layer + relationship
graph were already shipped; this is the last piece). Many dbt projects
pre-materialize a metric into mart columns — a "column forest" such as monthly
GMV exposed as `gmv_mtd` / `gmv_qtd` / `gmv_ytd` / `gmv_mom` / `gmv_yoy` plus
channel-segment variants. For text-to-SQL, the value is the **mapping**
(business variant → physical `model.column`), not a formula — the consumer
SELECTs the pre-built column rather than synthesizing a `GROUP BY`. This is the
strongest schema-linking lever for NL→SQL accuracy on projects without a
MetricFlow / dbt Semantic Layer definition.

- **SCHEMA `knowledge-metric`** — new **optional** `## Materialized Columns`
  body section (Variant | Model | Column | Grain). Appears only when a metric's
  variants are pre-materialized into mart columns; body-only (no frontmatter
  block); does not break "one metric = one page". The v2.x freeze header is
  clarified to permit additive optional body sections (no change to frontmatter
  shape / page types / naming / mandatory sections).
- **`distill-metrics.md` §3c — Materialization detection** — a front-gate in the
  SQL-derivation branch: anchor signal (column forest **or** pre-aggregated
  one-row-per-grain) routes the metric to the column-card output; mart-layer +
  schema.yml description alone are corroborating, not sufficient. Non-materialized
  metrics keep the existing formula / no-formula-fallback path (paths disjoint).
- **`distill-metrics.md` §5b — Materialized Columns Output** — producer spec for
  the card: the Variant|Model|Column|Grain table, plus a **forest-compression
  rule** — for regular naming (`gmv_{period}_{segment}`) capture the pattern +
  enumerated dimension values rather than enumerating ~100 rows; enumerate
  per-variant only when naming is irregular. Includes a `## Calculation`
  reconciliation note (materialized → SELECT pre-built column, no aggregation).
- **Worked example (§10b)** — a fully synthetic pre-aggregated Store GMV metric
  page (dimension-level compressed mapping table), plus a §11 decision-rule row
  making the materialized-vs-formula split explicit.

Artifact-only refinement of the v2.0 distill spec; zero warehouse / log / external
calls. `init` / `query` / `refresh` consume the new section generically (no
hardcoded body-section allowlist) — no changes required there.

## [2.0.0] — 2026-06-01

### BREAKING — Knowledge-centric redesign

dbt-wiki v2.0 shifts its purpose from **dbt resource structure distillation**
to **data knowledge distillation**: help users understand and analyze the
DATA (business entities, metrics, concepts), not just the shape of dbt objects.

#### Architecture: dual-layer model

**Knowledge layer (new, LLM-distilled)** — lives at the top of `.dbt-wiki/`:

- `entities/` — business objects (Customer, Order, Subscription) spanning
  multiple stg→int→mart models; each page includes a plain-language field
  glossary (no separate glossary directory)
- `metrics/` — business metrics (MRR, churn, LTV): definition, calculation
  rationale, caveats, source models; if the project has MetricFlow metrics,
  those are ingested as the authoritative input rather than re-derived
- `concepts/` — cross-cutting business rules encoded in SQL but belonging to
  no single entity ("active customer = order in last 90 days", fiscal year
  definitions, status enumerations)

Each knowledge page carries a `## Relationships` section with typed links
(entity↔entity, metric→entity, metric→concept, concept→entity/metric,
knowledge→`_evidence/`) derived from lineage and SQL semantics — a
lightweight knowledge graph without a graph database.

**Evidence layer (demoted, mechanical)** — existing manifest+sqlglot output
relocated under `_evidence/`:

- `_evidence/models/`, `_evidence/sources/`, `_evidence/macros/`, etc.
- All manifest+sqlglot extraction, column lineage, `manifest_sha` drift
  detection, and `syntheses/` stale tracking are fully preserved — these
  remain the distillation inputs and the authoritative structural truth.
- `lineage.md` and `syntheses/` stay at `.dbt-wiki/` root.

#### init: two-phase pipeline

- **Phase A** (mechanical, unchanged logic) — builds evidence layer under
  `_evidence/`, same sqlglot + manifest pipeline as v1.x.
- **Phase B** (new) — LLM-distills knowledge layer (`entities/`, `metrics/`,
  `concepts/`) reading Phase A output; each knowledge page records
  `derived_from: [evidence model uids]` for freshness tracking.

v1.x detection: if init finds an existing `.dbt-wiki/` containing pages with
`## User Notes`, it prints a one-time warning recommending backup before
proceeding. No migration is attempted (clean break).

#### query: semantic question classes

`/dbt-wiki:query` gains three new semantic question classes alongside the
existing structural ones:

- **K1** — entity lookup ("what is a Customer in this project?")
- **K2** — metric explanation ("how is MRR calculated?", "what are the caveats?")
- **K3** — cross-cutting concept ("what counts as an active subscription?")

Structural classes (C1–C11) are preserved; they now read from the evidence
layer directly.

#### refresh: thin evidence refresh + knowledge stale-flagging

`/dbt-wiki:refresh` refreshes the evidence layer (unchanged core logic) and
flags knowledge pages stale via `derived_from` when their source evidence
models change — reusing the existing `syntheses` stale mechanism. Auto
re-distillation of stale knowledge pages is a documented fast-follow, NOT
included in this release; user re-runs `/dbt-wiki:query` or init Phase B
to regenerate individual pages.

#### SCHEMA frozen at v2.0

`SCHEMA.md` is re-versioned and frozen at v2.0. All page-type definitions
(knowledge layer + evidence layer) are documented there. Future breaking
changes require v3.0+.

### Migration

**Clean break — no migration script.** v1.x `.dbt-wiki/` is rebuilt from
scratch by re-running `/dbt-wiki:init`. v1.x User Notes are NOT automatically
preserved (init warns once on detection; back up manually before re-init if
needed). The evidence layer's structural content (lineage, column data) is
fully regenerated from manifest+sqlglot.

---

## [1.3.0] — 2026-05-03

### Added — Lineage diagrams (ASCII + Mermaid) + auto-saved syntheses with stale detection

Two coupled features make `/dbt-wiki:query` answers richer AND
trustable over time.

#### 1. Lineage diagrams in query answers

For C2 (upstream) / C3 (downstream) / C4 (column-level) / C10
(refactoring impact) classes, query answers now include both:

- **ASCII tree** — renders in Claude Code chat output, any terminal,
  any markdown viewer. Always shown immediately.
- **Mermaid graph LR** — renders in IDE Markdown preview (Dataspell,
  VS Code, Cursor, JetBrains family), GitHub web view, Obsidian,
  mermaid.live. Saved into the synthesis page so user can re-open
  in their IDE for visual exploration.

New asset `format_lineage_diagram.py` (~360 lines, pure stdlib + PEP
723) generates both formats. Two modes:

```
column mode: consumes recursive_column_lineage.py JSONL
              + (model_uid, column) → ASCII tree + Mermaid (column nodes)
model mode:  consumes manifest.json directly
              + model_uid + direction (ancestors / descendants / both)
              → ASCII tree + Mermaid (model nodes)
```

Truncation policy: max 30 nodes per diagram (configurable via
`--max-nodes`); above that, append `truncated["⚠..."]` node and refer
user to full `lineage.md`. Node IDs use full-uid hash suffix to avoid
collisions when names are long; self-loops + duplicate edges deduped.

5/5 tests pass (column ancestors+descendants / ancestors-only / model
both / missing record / mermaid node-id safety). Real-world verified
on example mart_customer__dimension (38 upstream models, truncates
cleanly).

#### 2. Auto-saved syntheses with precise stale detection

`/dbt-wiki:query` now auto-saves answers to `.dbt-wiki/syntheses/<slug>.md`
for lineage / decision classes (C2/C3/C4/C9/C10). Information-only
classes (C1/C5/C6/C7/C8/C11) ask user before saving (default no).

Synthesis frontmatter records:
- `manifest_sha` at save time
- `affected_models` — the EXACT model uids the answer depends on
  (target model + every model in the rendered diagram tree)
- `query_class`, `sources_consulted`, `verification_run`, `verified_paths`

`/dbt-wiki:refresh` Step 6.5 uses `affected_models` for **precise**
stale detection: only mark stale when one of THOSE models actually
changed in this refresh's added / modified / removed sets — not just
"manifest_sha drifted" (which would mark everything stale on every
refresh).

When marked stale, refresh:
- Sets `stale: true`, `stale_at: <today>`, `stale_reason: <which models changed>`
- Prepends a banner to the synthesis body so the user sees it as the
  FIRST thing when opening the .md file in their IDE
- Does **NOT** regenerate the answer (preserves original; user controls
  when to re-query — avoids LLM cost + answer-wording drift on every refresh)

User re-runs `/dbt-wiki:query "<original question>"` → fresh answer
overwrites the synthesis, clears the stale flag.

### Files added

- **`assets/format_lineage_diagram.py`** (~360 lines, pure stdlib, PEP 723)
- **`assets/format_lineage_diagram_test.py`** (~190 lines, 5 cases pass)
- **`assets/synthesis_template.md`** — markdown shape with full frontmatter

### Files changed

- **`skills/init/SKILL.md`** — Step 4 cp block extends with 3 new files
  (diagram script + test + synthesis template) → `.dbt-wiki/_internal/`
- **`skills/query/SKILL.md`**:
  - New Step 4.5 — diagram generation (when + how to invoke
    `format_lineage_diagram.py` for each query class; ASCII always in
    chat, Mermaid always in synthesis)
  - New Step 6.5 — auto-save synthesis with full frontmatter
    (manifest_sha + affected_models for precise stale detection)
  - Step 7 log entry gains `Synthesis saved: <path>` line
- **`skills/refresh/SKILL.md`**:
  - New Step 6.5 — synthesis stale-detection logic (~50 lines bash + Python
    pseudocode). Non-destructive: marks `stale: true` + prepends banner
    to body; original answer + diagrams preserved.
  - Step 7 log entry gains `Syntheses marked stale: N` line
- **`skills/init/assets/SCHEMA.md`**:
  - Directory layout adds `syntheses/` with one-line description
  - New `### synthesis` page-type definition with full frontmatter
    template + body section spec + stale lifecycle explanation
- **`.claude-plugin/plugin.json`** — 1.2.0 → 1.3.0 (minor — new capability,
  fully backward compatible)

### Backward compatibility

**Zero break**:
- Lineage diagrams are STRICTLY additive to query output (ASCII + Mermaid
  appended after the text answer)
- Auto-save synthesis only kicks in for new queries; existing
  `.dbt-wiki/syntheses/` (none in v1.0–v1.2 since query never auto-saved)
  are unaffected
- Stale detection: synthesis WITHOUT `affected_models` field (none yet —
  this is v1.3 introducing it) falls back to `manifest_sha` drift
  comparison (less precise but always works)

### Real-world impact preview (example-dbt-pipeline)

After re-running `/dbt-wiki:init` (or just `/dbt-wiki:refresh`):
- `format_lineage_diagram.py` becomes available in `.dbt-wiki/_internal/`
- Next `/dbt-wiki:query "mart_customer__dimension 上游"` → answer includes
  ASCII tree (15 nodes, terminal-readable) + Mermaid block (renders in
  Dataspell preview)
- Answer auto-saved to `.dbt-wiki/syntheses/mart-customer-dimension-upstream.md`
- Future refresh after `dim_customers` changes → that synthesis
  marked stale with banner: "affected_models changed: dim_customers"

### Decision rationale

- **Why both ASCII + Mermaid**: ASCII covers the lowest common denominator
  (terminal output, any markdown viewer); Mermaid adds rich rendering
  where supported. User pays nothing for having both.
- **Why precise stale detection (vs full re-query)**: re-querying every
  refresh costs LLM tokens + introduces answer-wording drift (breaks
  git diff stability). Mark-stale-with-banner is honest about
  uncertainty without forcing regeneration.
- **Why script not LLM-generated diagrams**: deterministic, testable,
  consistent output across queries; LLM doesn't need to remember
  Mermaid syntax.

---

## [1.2.0] — 2026-05-03

### Added — `SELECT * FROM <final_cte>` wrapper-pattern unwrap

dbt projects very commonly end models with the convention:

```sql
WITH staging AS (...),
     enriched AS (...),
     final AS (
         SELECT col1, col2, calculation AS col3 FROM enriched
     )
SELECT * FROM final
```

In v1.0–v1.1.2, sqlglot saw only the outer `SELECT *` and reported a
single column named `*`. Models authored with this convention lost all
per-column information. On the example-dbt-pipeline dogfood, this hit
**71% of models** (860/1209), making column-level lineage queries
mostly useless for marts/dash tiers.

v1.2.0 adds an unwrap fallback in `extract_column_lineage.py`. When
the script detects a top-level `SELECT * FROM <single_table>` AND the
referenced table is a CTE in the same SQL's WITH clause, it walks into
the CTE and uses ITS projections as the model's columns. Recursive up
to depth 5 (handles `cte_a = SELECT * FROM cte_b = SELECT * FROM cte_c`).

For each unwrapped column, sources are extracted from direct column
references in the inner CTE's expression. If the inner CTE has a
single FROM table (the typical `final AS (SELECT ... FROM merge_data)`
pattern), unqualified column references are auto-resolved to that
table — so a single-CTE wrapper produces clean `merge_data.col1` style
sources.

### Real-world impact (example-dbt-pipeline, 1209 model files)

| Metric | v1.1 | v1.2 | Δ |
|---|---|---|---|
| Models with real column names | 349 (28.9%) | 1209 (100%) | **+860 / +247%** |
| Models stuck at just `*` | 860 | 0 | **−860** |
| Avg columns per model (real) | 1 | 12 | **+12×** |
| Total column entries unlocked | ~349 | ~14,500 | **+41×** |

### Files changed

- **`dbt-wiki/skills/init/assets/extract_column_lineage.py`**:
  new helper `_expand_star_via_cte()` (~80 lines). Detects `SELECT *
  FROM <cte>` pattern, recursively walks nested wrappers (max_depth=5),
  resolves unqualified column refs against the inner CTE's single FROM
  table when applicable. Hooked into `extract_lineage()` BEFORE the
  per-projection loop — if unwrap succeeds, use it; otherwise fall
  through to existing logic (preserves all v1.1 behavior for non-wrapper
  SQL).
- **`dbt-wiki/skills/init/assets/extract_column_lineage_test.py`**:
  - 2 new test cases (Cases 8 + 9): single-level wrapper + nested
    wrapper. Both pass.
  - Test runner switched to `uv run` first (fall back to plain python3
    if uv not installed). Previously ran via `sys.executable` which
    couldn't honor PEP 723 metadata, so all sqlglot-dependent tests
    silently skipped on machines without manually pip-installed
    sqlglot.
- **`.claude-plugin/plugin.json`**: 1.1.2 → 1.2.0 (minor bump — new
  capability, fully backward compatible).

### Backward compatibility

**Zero break**. The unwrap is a strictly additive fallback:
- If your SQL doesn't use the `SELECT * FROM <cte>` pattern, code path
  is identical to v1.1.x
- If your SQL DOES use the pattern but the CTE isn't found / FROM has
  joins / nested too deep — fall through to v1.1's behavior (Star → `*`)
- All 7 v1.1 test cases still pass

### Limitations (v1.2.0)

- Only handles single-table FROM in the outer `SELECT *`. If outer is
  `SELECT * FROM cte_a JOIN cte_b ON ...`, no unwrap (could be added
  in v1.3 by merging projections from both CTEs).
- For unqualified column refs inside the CTE, only resolves to a single
  default table — if the CTE itself has joins, references stay as
  `<unqualified>` (the recursive-lineage extractor can still resolve
  these via downstream chain).
- max_depth=5 should cover all realistic dbt wrapper chains; if you
  somehow have `cte1 → cte2 → cte3 → cte4 → cte5 → cte6`, deepest one
  is skipped.

### Migration

Re-run `/dbt-wiki:init` to regenerate model pages with full column
lineage. Existing v1.1.x `.dbt-wiki/` pages will be overwritten by
init's re-run (same idempotency contract); user-owned `## User Notes`
sections are preserved.

---

## [1.1.2] — 2026-05-03

### Fixed — `.dbt-wiki/` now writes to git repo root, not cwd

v1.0–v1.1.1 used relative paths like `mkdir -p .dbt-wiki/models`, which
resolved to `$PWD` at invocation time. Combined with v1.1.1's smart
dbt project detection (which lets the user run init from anywhere),
this meant `.dbt-wiki/` would land wherever the user happened to be:

- Run from `~/repo/`        → `~/repo/.dbt-wiki/`        ✓
- Run from `~/repo/dbt/`    → `~/repo/dbt/.dbt-wiki/`    ✗
- Run from `~/repo/dbt/models/staging/` → 4 levels deep ✗✗

This was inconsistent with the CLAUDE.md drop-in (Step 2 of init),
which already wrote to **git repo root**. Two output locations for the
same plugin = bad UX. Also broke refresh / query when the user changed
cwd between init and subsequent invocations.

### Fix

All three skills (init / refresh / query) now perform a single
**Step 0pre**: detect git repo root via `git rev-parse --show-toplevel`,
fall back to `$PWD` if not in a git repo, then `cd "$WIKI_DIR"`. After
that, every existing `.dbt-wiki/...` path in the SKILL.md auto-resolves
to the right place — no bulk path rewrites needed.

Result:

- `.dbt-wiki/` always lives at the git repo root
- Co-located with `.git/`, `CLAUDE.md` drop-in, and (if installed) `.repo-wiki/`
- init / refresh / query can be run from ANY cwd within the repo and
  always read/write the same `.dbt-wiki/`

### Files changed

- **`skills/init/SKILL.md`** — new Step 0pre (4-line bash) inserted before
  Step 0a; everything below works unchanged.
- **`skills/refresh/SKILL.md`** — same Step 0pre prepended to existing
  pre-condition check; error message now includes `$WIKI_DIR` for clarity.
- **`skills/query/SKILL.md`** — same Step 0pre prepended.
- **`skills/init/assets/SCHEMA.md`** — Architecture section clarifies
  `.dbt-wiki/` location ("at git repo root, same level as .git/ and CLAUDE.md").
- **`.claude-plugin/plugin.json`** — 1.1.1 → 1.1.2 (patch — bug fix, no
  behavior change for users who already ran from git repo root).

### Backward compatibility

**Pre-existing `.dbt-wiki/` directories at non-root locations** (created
by v1.0–v1.1.1 when user ran from a subfolder) are NOT auto-migrated.
After upgrading to v1.1.2, the next `/dbt-wiki:init` will create a NEW
`.dbt-wiki/` at the git repo root, leaving the old one orphaned.
Migration: manually `mv <old-location>/.dbt-wiki <repo-root>/.dbt-wiki`,
or delete the old one and re-run init from scratch.

### Edge cases

- **Not in a git repo**: `git rev-parse` fails silently; WIKI_DIR
  falls back to `$PWD`. User must invoke from a sensible location
  (typically the project root). Same constraint as v1.1.0.
- **Submodules**: `git rev-parse --show-toplevel` returns the
  submodule's root, not the parent repo. This is correct: each
  submodule with its own dbt project gets its own `.dbt-wiki/`.

---

## [1.1.1] — 2026-05-03

### Changed — 5-tier dbt project root detection

v1.0/v1.1 only checked two hardcoded locations relative to cwd:
`./dbt/dbt_project.yml` and `./dbt_project.yml`. Anyone with a
non-standard layout (e.g. dbt under `data/dbt-prod/`) or running init
from inside a subdirectory (e.g. `models/staging/`) hit "Cannot find
dbt_project.yml" and had to cd to the right place.

v1.1.1 introduces a **5-tier resolver**, tried in priority order:

1. **Explicit arg**: `/dbt-wiki:init <path>` — pass the directory
2. **`$DBT_PROJECT_DIR` env var** — matches dbt CLI / dbt-mcp convention
3. **Ancestor walk from cwd** — up to 5 levels up (handles `models/staging/...`)
4. **Descendant scan from cwd** — `find -maxdepth 3` with exclusions
   (`node_modules`, `.git`, `target`, `.venv`, `__pycache__`,
   `dbt_packages`, `.repo-wiki`, `.dbt-wiki`)
5. **Legacy whitelist** (`./` and `dbt/`) — kept for back-compat

First match wins. Output reports which tier resolved (e.g. `detected
via: ancestor walk from cwd`) so user can debug if it picked the wrong
project (rare, but possible in monorepos with multiple dbt projects).

**Files changed**:
- `dbt-wiki/skills/init/SKILL.md` — Step 0 split into 0a (resolver,
  ~70 lines bash) + 0b (artifact + Python runner verification). Failure
  message lists every tier checked with actionable hints.
- `dbt-wiki/skills/refresh/SKILL.md` — same resolver inlined (refresh
  needs identical detection; can't rely on init having stored the path
  since user might run refresh from a different cwd).
- `dbt-wiki/skills/query/SKILL.md` — drift check uses the same resolver
  minus the explicit-arg tier (query doesn't take a path arg).
- `dbt-wiki/.claude-plugin/plugin.json` — 1.1.0 → 1.1.1.

**Coverage matrix**:

| User's cwd | dbt at | v1.1.0 | v1.1.1 |
|---|---|---|---|
| repo root | `./dbt/` (example style) | ✅ | ✅ |
| repo root | `./` | ✅ | ✅ |
| `models/staging/` | `../../dbt_project.yml` | ❌ | ✅ (ancestor walk) |
| any cwd, `$DBT_PROJECT_DIR` set | (env-pointed) | ❌ | ✅ (env var) |
| repo root with `data/dbt-prod/` | non-standard subdir | ❌ | ✅ (downward scan) |
| explicit `/dbt-wiki:init ./other/` | wherever | ❌ | ✅ (arg) |
| Multi-dbt monorepo | multiple matches | ❌ | ⚠️ first match wins (disambiguate via arg or env var) |

**Backward compatibility**: zero break. Tier 5 is the exact v1.0/v1.1
behavior. Existing users see no change.

---

## [1.1.0] — 2026-05-03

### Added — recursive cross-model column lineage

dbt-wiki v1.0.0's column lineage was **single-hop** (within one
compiled SQL): `fct_orders.customer_id ← stg_orders.customer_id`. To
trace back to source you'd manually walk the chain across model pages.

v1.1.0 ships **precomputed recursive lineage** that walks the dbt DAG
bidirectionally (ancestors back to source + descendants forward to
leaf marts) and stores it in each model page's
`## Column Lineage Chains` body section. Now `/dbt-wiki:query` can
answer "fct_orders.customer_id 從哪一路來?" or "rename
stg_customers.email 會影響哪些 model 的哪些 column?" by loading a
single page.

This is the recursive lineage capability comparable to [canva-public/dbt-column-lineage-extractor](https://github.com/canva-public/dbt-column-lineage-extractor),
implemented inside dbt-wiki without an additional pip dependency.
Same sqlglot under the hood (via existing `extract_column_lineage.py`);
the new script `extract_recursive_column_lineage.py` is pure stdlib.

**Files added**:
- `dbt-wiki/skills/init/assets/extract_recursive_column_lineage.py`
  (382 lines): consumes per-SQL JSONL from `extract_column_lineage.py
  --batch` plus `target/manifest.json`. Builds an alias-map (model name
  / alias / schema-qualified / fully-qualified all map to manifest
  unique_id) and a feeds_into reverse-DAG. Recursively walks ancestors
  (via the alias-map) and descendants (via feeds_into matched against
  downstream models' per-SQL sources). Cycle + max-depth protection.
  Output is JSONL — one record per `(model_uid, column)` with
  `ancestors` and `descendants` as nested dict trees.
- `dbt-wiki/skills/init/assets/extract_recursive_column_lineage_test.py`
  (260 lines): synthetic 4-model dbt project with COALESCE multi-source.
  6 cases: 1) full ancestor chain back to source through stg, 2) negative
  descendant test (different column), 3) positive descendant chain
  through fct to mart (2 hops), 4) single-hop ancestor, 5) 2-hop
  descendant via intermediate, 6) whole-project mode produces 1 record
  per (model, column). All 6 pass on pure stdlib (no sqlglot needed
  for test).

**Files changed**:
- `dbt-wiki/skills/init/SKILL.md`:
  - Step 4 cp block extended to copy the 2 new scripts to
    `.dbt-wiki/_internal/`
  - New Step 4f: invoke recursive script after Step 4b's per-SQL
    extraction; output JSONL piped to `/tmp/dbt-wiki-recursive-lineage.jsonl`
  - New Step 4g: optional verify of recursive script via its smoke test
- `dbt-wiki/skills/init/assets/SCHEMA.md`:
  - New body section `## Column Lineage Chains` with example showing
    nested ancestors + descendants tree
  - Standard sections list updated to include `Column Lineage Chains`
    (so refresh regenerates it like other derived sections)
- `dbt-wiki/skills/query/SKILL.md`:
  - C4 (Column-level lineage) row updated: now loads single model page's
    `## Column Lineage Chains` section (precomputed recursive chain)
    instead of needing to walk multiple upstream pages
- `dbt-wiki/.claude-plugin/plugin.json`: 1.0.0 → 1.1.0

**Relationship to PR #213** (open at time of this PR):
PR #213 adopts PEP 723 + uv for dependency management. This PR (v1.1.0)
adds recursive lineage. The two are orthogonal — both modify
`init/SKILL.md` script invocation but at different points (PR #213
changes WHICH runner; this PR adds WHAT TO RUN). Whichever lands first,
the second needs a small rebase on `plugin.json` version field.

**Limitations** (documented in script docstring):
- SQL-local aliases like `SELECT f.a FROM stg_orders AS f` require
  sqlglot to back-resolve `f` → `stg_orders` in its lineage output.
  If sqlglot emits `f.a` literally, recursive walker marks
  `_unresolved::f::a` and stops at that branch.
- CTEs inside compiled SQL — same story; sqlglot usually walks through
  them but not always.
- max_depth defaults to 10 (configurable via `--max-depth`); cycles
  marked as `_cycle` (rare in dbt but possible with snapshot models).
- For Redshift specifically: late-binding views work normally.

**Why implement vs. depend on dbt-column-lineage-extractor**:
- Avoid external pip dep (one less thing for users to install)
- Same underlying sqlglot — no quality gap on dialect support
- Output format we control (matches dbt-wiki SCHEMA conventions)
- Reuses existing per-SQL lineage from v1.0.0 (composable, not duplicated)
- 380-line implementation vs. external dependency — net code we own

---

## [1.0.1] — 2026-05-03

### Changed — PEP 723 inline metadata + uv-first execution

Both bundled scripts (`extract_column_lineage.py`, `extract_sql_comments.py`)
now declare their Python and dependency requirements via PEP 723 inline
metadata. With [uv](https://github.com/astral-sh/uv) installed, `uv run`
auto-creates an ephemeral env, installs sqlglot, runs the script, and
cleans up — no manual `pip install sqlglot` required.

**Why**: the original v1.0.0 design required users to manually
`pip install sqlglot` into their dbt Python env. That step was easy to
forget and polluted the dbt env with a tool not used by dbt itself.
PEP 723 + uv removes the step entirely while preserving full
backward-compatibility with plain `python3` (for users without uv).

**Files changed**:
- `dbt-wiki/skills/init/assets/extract_column_lineage.py` — added
  PEP 723 block declaring `sqlglot>=25.0` and `requires-python = ">=3.10"`;
  shebang updated to `#!/usr/bin/env -S uv run --script`; module docstring
  documents both execution modes
- `dbt-wiki/skills/init/assets/extract_sql_comments.py` — added PEP 723
  block with empty `dependencies` list (pure stdlib); same shebang change.
  PEP 723 included for consistency even though no third-party dep
- `dbt-wiki/skills/init/SKILL.md`:
  - Step 0 Pre-condition Check rewritten: detects `uv` first, falls back
    to `python3` with sqlglot. Sets `$PY_RUNNER` for downstream steps.
    Both detection paths produce a clear "next step" hint if neither
    is available.
  - Step 4 column-lineage script invocations changed from `python3 ...`
    to `$PY_RUNNER ...`
  - Step 4d comment-extraction script invocations same change
- `dbt-wiki/skills/refresh/SKILL.md` — same Step 0 detection + invocation
  changes as init
- `dbt-wiki/README.md` / `README.zh-TW.md` / `README.ja.md` — Quick start
  Step 2 + Pre-conditions section updated to present uv as primary,
  pip as fallback (in all three languages)
- `dbt-wiki/.claude-plugin/plugin.json` — version bumped 1.0.0 → 1.0.1;
  description updated to mention PEP 723 + uv

**Backward compatibility**: zero break. Users with sqlglot already
installed via pip continue to work unchanged (init detects this path
in Step 0).

**Test verification** (local):
- `uv run extract_column_lineage.py` on a 4-column SQL with COALESCE +
  JOIN → correct column lineage output (auto-installed sqlglot 30.6
  in 5ms ephemeral env)
- `uv run extract_sql_comments.py` on a 3-comment SQL (line + jinja +
  inline) → all 3 entries with correct line numbers + kind classification

**Decision rationale**: uv is increasingly the Python tooling standard
(used by dbt-coves, modal, duckdb, etc.). PEP 723 inline metadata is
the official Python recommendation for self-contained scripts (PEP
accepted late 2024). Adopting both removes the "manual install"
friction without imposing dependency on a custom installer or vendored
sqlglot copy. Backward fallback to plain `python3 + pip` ensures users
who haven't adopted uv yet still get full functionality.

---

## [1.0.0] — 2026-05-02

### Added — Initial release

Four skills for local-only LLM-queryable dbt knowledge (symmetric with repo-wiki: init / refresh / ingest / query).

**Skills**:
- `/dbt-wiki:init` — first-time setup. Reads `target/manifest.json` (model metadata, refs/sources, schema.yml columns, tests), `target/compiled/<project>/**/*.sql` parsed via [sqlglot](https://github.com/tobymao/sqlglot) for **column-level lineage**, AND `dbt/models/**/*.sql` raw files parsed via regex for **inline SQL/jinja comments** (`-- ...`, `/* ... */`, `{# ... #}`). Plugin ships 4 scripts in `assets/` (flat — Anthropic skill convention forbids nested asset subdirs): `extract_column_lineage.py` + `_test.py` (sqlglot lineage with `--batch` JSONL mode; 7-case smoke test, all passing on sqlglot 30.6) and `extract_sql_comments.py` + `_test.py` (regex comment extractor with `--batch` mode; 6-case smoke test including multibyte/Chinese, all passing). Init copies all 4 to `.dbt-wiki/_internal/`. Generates one markdown page per model / source / macro (used) / seed / snapshot / singular test / exposure under `.dbt-wiki/`. Writes `.dbt-wiki/SCHEMA.md`, `index.md`, `lineage.md`, `log.md`, plus an idempotent CLAUDE.md drop-in. Re-runnable: refreshes manifest-derived fields, archives orphans, preserves custom body sections.
- `/dbt-wiki:refresh` — incremental update. Compares current `manifest.json` md5 against `manifest_sha` in log.md; processes only added / modified / removed models / sources / macros. Re-runs sqlglot lineage AND comment extraction on changed files. Removed models are archived to `.dbt-wiki/_archive/<date>/`, never hard-deleted. **Preserves user-owned `## User Notes` body section verbatim** (managed by /dbt-wiki:ingest). Always regenerates `index.md` and `lineage.md` (derived files). Asks user to confirm diff summary before writing.
- `/dbt-wiki:ingest` — capture user-supplied context that is NOT in manifest.json or schema.yml: gotchas, design rationale, ticket references, incident links. Auto-detects target model / source / macro from message text; appends note as dated entry under `## User Notes` body section on the matched page. Multi-target match resolution (asks user to clarify on no-match or multi-match). Survives `/dbt-wiki:refresh` cycles (refresh treats `## User Notes` as user-owned). Mirrors `/repo-wiki:ingest` context-mode behavior for the dbt-internal scope. Doc-import mode and git-mode are intentionally NOT included (use /dbt-wiki:refresh for manifest snapshots; use /repo-wiki:ingest for cross-cutting WHY).
- `/dbt-wiki:query` — natural-language Q&A. Routes question to one of 11 query classes (C1: model lookup, C2/C3: upstream/downstream lineage, C4: column-level lineage, C5: materialization filter, C6: tag/group/tier filter, C7: test coverage, C8: source attribution, C9: macro usage, C10: refactoring impact, C11: schema gaps). Loads minimum pages for the class. Drift-aware: warns if current `manifest.json` SHA differs from wiki snapshot. Suggests `/dbt-wiki:refresh` when stale. Answers can draw from inline comments AND user notes alongside structured manifest data — gives WHY-aware responses, not just structural ones.

**Schema (frozen at v1.0)**:
- `model` page type with frontmatter: `unique_id`, `materialization`, `tags`, `schema`, `database`, `group`, `access`, `contract_enforced`, `last_updated`, `manifest_sha`, `columns_extracted_via`, `columns[]` (each with `name`/`type`/`description`/`declared_in_schema_yml`/`tests`/`sources` from sqlglot), `depends_on` (refs/sources/macros), `feeds_into`, `generic_tests`, `recorded_decisions` (cross-link to repo-wiki)
- `source` page type with `unique_id`, `source_name`, `table_name`, `schema`, `database`, `loaded_at_field`, `freshness`, `columns`, `fed_by`, `feeds_into`
- `macro` page type with `unique_id`, `package`, `path`, `arguments`, `description`, `used_by_models`
- Same pattern for seed / snapshot / test / exposure
- `index.md` grouped by tier path / materialization / tag / group
- `lineage.md` with ASCII tree (per source) + adjacency list (per model); tier-aggregated view for >500-node projects
- `log.md` append-only with init / refresh / query entries; tracks `manifest_sha` and sqlglot failures

**Coexistence with [`repo-wiki`](../repo-wiki/)**:
- Both plugins write to distinct hidden dirs (`.dbt-wiki/` vs `.repo-wiki/`); neither modifies the other
- CLAUDE.md drop-ins use distinct markers
- dbt-wiki: STRUCTURE + COLUMN LINEAGE (auto-derived from manifest + sqlglot)
- repo-wiki: WHY (decisions, refactor history; manual ingest)
- Cross-link freely from either side

**Pre-conditions**:
- dbt project (manifest.json schema v9+ recommended)
- `dbt parse && dbt compile` must run before init/refresh
- Python 3.x + `sqlglot` (`pip install sqlglot`)
- Dialect support: redshift / postgres / snowflake / bigquery / databricks / clickhouse / duckdb / mysql / oracle / spark / sqlite / tsql

### Design decisions

- **Decision 1**: `manifest.json` + `compiled/*.sql` are source of truth; never re-derive what dbt already parsed. Specifically, init parses `compiled/*.sql` not `raw_code` because dbt's own jinja engine has the most accurate expansion.
- **Decision 2**: sqlglot is a hard dependency for v1.0. The whole point of dbt-wiki vs reading manifest.json directly is column-level lineage — without sqlglot, the value proposition collapses. User installs via `pip install sqlglot` in their dbt env.
- **Decision 3**: Local-only. No dbt Cloud, no warehouse calls. catalog.json (real warehouse types) and run_results.json (test pass/fail) are v2 backlog opt-in reads, not v1 requirements.
- **Decision 4**: Refresh idempotency via `manifest_sha`. If current manifest hash matches log.md's last record, refresh exits without changes. User can force by deleting the manifest_sha line from log.md.
- **Decision 5**: Archive, never hard-delete. Orphaned models go to `.dbt-wiki/_archive/<date>/`. User can restore manually if needed.
- **Decision 6**: Coexist with repo-wiki via distinct hidden dirs and CLAUDE.md drop-in markers. Neither plugin needs to know about the other; cross-links are user-authored.
- **Decision 7**: Macro pages only for macros used by ≥1 model. Filter `manifest.macros` by checking each model's `depends_on.macros`. Avoids spam for unused macros (especially in dbt_utils).
- **Decision 8**: Filename collision: when same `name` exists in different packages, use `<package>__<name>.md` (matches repo-wiki convention).
- **Decision 9**: Drift-aware query (DT4). When `manifest.json` SHA differs from wiki snapshot, query prepends a warning and recommends `/dbt-wiki:refresh`. Stale-but-best-effort answers are better than refusing to answer; explicit warning preserves user trust.
- **Decision 10**: Symmetric command set with repo-wiki (init / refresh / ingest / query). Original draft had only 3 skills (init / refresh / query) on the reasoning that "dbt-wiki is a derivation engine, repo-wiki is an accumulation engine". User pushback during PR review noted that dropping ingest forced users to learn two mental models AND left dbt-wiki standalone-incomplete (no way to add tribal knowledge if repo-wiki not installed). Added `/dbt-wiki:ingest` for context capture; kept `refresh` distinct from `ingest` because they're functionally different (manifest snapshot replacement vs user-input accumulation). End result is more symmetric than repo-wiki's polymorphic ingest (git/context/doc-import all conflated): each verb does one thing.
- **Decision 11**: Inline comment extraction via regex on raw_code, NOT sqlglot on compiled. Reasoning: (a) jinja `{# ... #}` comments are stripped by `dbt compile` — extracting them needs raw_code; (b) sqlglot's comment handling varies by dialect and can drop positional context; (c) regex is dialect-agnostic and preserves source line numbers. The per-model `## Inline Comments` body section displays line-number-prefixed entries so user can locate them in source. Trade-off: regex doesn't classify comments by structural position (header vs pre-CTE vs inline) — line number is sufficient for LLM query.
- **Decision 12**: `## User Notes` is user-owned, refresh preserves verbatim. Same protection model as repo-wiki's ingest-accumulated entity sections (Responsibility / Architecture / etc.). The schema explicitly lists `## User Notes` as user-owned (alongside any other non-standard `##` heading the user adds). Refresh's "preserve custom body sections" rule already covered this; the ingest skill formalizes the use case.

### Pre-trial validation

Plan validation against `<local dbt project>` (real dbt-on-Redshift project, ~200+ models across multiple tiers — staging / intermediate / marts / reporting / exports):
- ✅ dbt project layout matches dbt-wiki's expectations (`dbt/dbt_project.yml`, `dbt/models/<tier>/`, `dbt/target/`)
- ✅ User already has dbt CLI
- ⏳ sqlglot install required (`pip install sqlglot` in their dbt env) — pre-condition
- ⏳ Real-world dogfood scheduled post-merge: `/dbt-wiki:init` against example-dbt-pipeline → measure model count, sqlglot failure rate, lineage depth, query response quality

### Known limitations (v1.0)

- **Macros with conditional SQL**: sqlglot may fail on extreme jinja edge cases (rare; dbt compile usually resolves). Failed models still get pages, just without `columns[].sources`.
- **Cross-package column lineage**: when a model uses a dbt_utils macro that itself wraps SELECT logic, sqlglot sees the expanded SQL but column names may be macro-generated and not match user expectation.
- **Late-binding views (Redshift)**: sqlglot supports them syntactically; semantic correctness depends on dialect maturity.
- **Singular test attribution**: tests in `tests/*.sql` (not schema.yml) are listed in their own pages; cross-linking to affected models via `depends_on` parsing.
- **No catalog.json / run_results.json yet**: column types in v1 are from schema.yml only (warehouse-real types are v2 backlog).
- **Wall-clock for init**: ~30s-2min for typical 100-300 model projects (sqlglot is single-threaded per file; v2 may parallelize).

### Inspiration & credits

- **[dbt-labs/dbt-core](https://github.com/dbt-labs/dbt-core)** — `manifest.json` schema is the canonical source-of-truth for dbt project structure. v1 leans entirely on dbt's parse output; never re-derives.
- **[tobymao/sqlglot](https://github.com/tobymao/sqlglot)** — column-lineage extraction is impossible without a SQL AST library; sqlglot's multi-dialect support (redshift/snowflake/bigquery/etc.) makes dbt-wiki dialect-agnostic for free. MIT-licensed pure Python, no native deps.
- **[`repo-wiki`](../repo-wiki/)** — sibling plugin in monkey-skills. Conventions reused: SKILL.md structure (Step-by-step workflow + Rules), SCHEMA.md frozen-until-v2.0, log.md append-only operation tracking, CLAUDE.md drop-in idempotency, `_archive/` for safe removal.
- **[lis186/SourceAtlas](https://github.com/lis186/SourceAtlas)** — its information-theory analysis discipline (high-entropy file priority, scan-ratio bounds) inspired repo-wiki v1.2. dbt-wiki doesn't use those directly (manifest.json eliminates the need for heuristic scanning) but shares the spirit of "let the structured truth do the work, don't re-invent parsing."
