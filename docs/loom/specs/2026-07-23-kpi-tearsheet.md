# Brief: KPI tearsheet — one-company one-page read surface for the KPI store

Date: 2026-07-23. Stage: brainstorming output → writing-plans input.
Origin: BACKLOG §非金錢營運 KPI deferred item; user-ordered arc sequence
tearsheet → Part 3 → loom-code replay matrix (2026-07-23 decision — use the
store first, harden second, measure the mechanism third).

## Problem

When the user wants to know "what have I recorded for this company, and has
any figure changed?", the only path today is importing `kpi_store` from Python
and reading raw JSON — the store's read capabilities shipped in 2.30.0
(`history` with vintages + disagreement) have NO human-readable surface. The
job-to-be-done: **glance at one company's recorded operational KPIs — values,
periods, when recorded, and whether any later filing changed them — without
writing code.** This is the first "reader" of the store in the
coverage-artifact sense established by
`docs/loom/research/2026-07-19-longhorizon-equity-analysis-process-and-deliverables.md`
(memo and tearsheet are readers of a maintained per-company artifact).

## Users

kouko, solo, in Claude Code terminal sessions. Two moments: (a) right after
an intake session ("did everything land?"), (b) before/while analyzing a
company ("what do I already hold, any restatement flags?"). Data exists only
for companies previously fed through the intake lanes (8-K table / prose /
XBRL adapter). Obsidian vault archiving is a later convenience, not the
primary moment.

## Smallest End State

1. **`kpi_store.py` CLI grows read exposure** (exact subcommand shape decided
   at plan time; candidates: `list-series` + a one-company `dump`). Rationale:
   the tearsheet renderer lives in the report layer, and the layer rule is
   subprocess-not-import (`analysis-kpi/SKILL.md:43-48`), so the store's
   import-only reads (`history` :440, `list_series` :517, `list_kpis` :571)
   must become CLI-reachable first.
2. **New skill `report-kpi-tearsheet`** (ADR naming convention
   `docs/adr/0001-data-analysis-report-layers.md:145` — `report-{format}`)
   with `scripts/tearsheet_format.py`, a **pure formatter** following the
   shipped `report-stock-snapshot/scripts/snapshot_format.py` pattern
   (JSON in → Markdown to stdout, no analysis, no HTTP): subprocesses the new
   kpi_store CLI reads and renders ONE company's tearsheet:
   - Header: company + as-of date (fund-factsheet convention).
   - One KPI table: **periods as columns** (newest left), one row per
     `kpi_id`; unified period axis across the company's KPIs via the raw
     `(period_start, period_end)` identity (`same_period` semantics — labels
     are display only); absent cell → `N/A`.
   - **Multi-vintage disagreement**: cell shows the latest-`as_of` canonical
     value with a superscript-style marker; a footnote block below the table
     lists EVERY vintage (value, as_of, source accession) for each flagged
     cell. Both vintages retained, neither called "wrong" — mirrors the
     store's own doctrine (`kpi_store.py history` :456-462).
   - Footer: provenance line (store dir + series files read + render date) and
     the graceful-empty conventions of the report layer (missing → `N/A`,
     partial/corrupt-skip surfaced in a warnings footer, per
     `report-stock-snapshot/SKILL.md:83` and
     `report-screener-list/SKILL.md:115-117`).
   - Output: stdout, optional `--out <path>`.
3. Docs: `analysis-kpi/references/cli-reference.md` gains the new read
   subcommands; the new skill's SKILL.md documents the read workflow (the gap
   noted at `investing-toolkit/CHANGELOG.md:84`); investing-toolkit version
   bump + CHANGELOG.

## Current State Evidence

- **Forward** (data source): read API `query_point_in_time` :356,
  `query_latest` :374, `history` :440 (returns observations sorted by as_of +
  `disagreement` flag), `list_series` :517, `list_companies` :564,
  `list_kpis` :571 — all in
  `investing-toolkit/skills/analysis-kpi/scripts/kpi_store.py`; CLI has ONLY
  `append`/`query` (:628-643). Point fields: identity+provenance
  (`_REQUIRED_PROVENANCE_FIELDS` :116, dedup 5-tuple :154), period identity
  :161-168, explicit `scale` consumed via `_canonical_value` :403-437, display
  `unit`, optional `lineage`/`restates`, `integrity` stamp. Store dir ladder
  `KPI_STORE_DIR` → XDG → `~/.local/share/investing-toolkit/kpi-store`
  (`_store_fs.resolve_store_dir` :43-64).
- **Reverse** (rendering precedent): `report-stock-snapshot/scripts/snapshot_format.py`
  — pure formatter, Markdown to stdout, `N/A` for missing
  (SKILL.md:63-90); `report-screener-list/scripts/screener_format.py` same
  shape (SKILL.md:174-192); report→analysis subprocess precedent
  `report-screener-list/SKILL.md:162`.
- **Error**: store reads never-raise on absent/corrupt (`list_series`
  :530-540, `history` :489-499, `_matching_points` :349-351; CLI query prints
  `null` :623); render side `N/A` + warnings-footer precedent (above).
- **Data**: store may legitimately be EMPTY or hold companies with a single
  vintage everywhere — tearsheet must render usefully in both (empty store →
  "no companies recorded" card; no disagreements → no footnote block).
- **Boundary**: analysis↔report crossing is subprocess-not-import
  (`analysis-kpi/SKILL.md:43-48`, `kpi_store.py` docstring :21-28, CLAUDE.md
  §Cross-Plugin Delegation Contract). Vault frontmatter schema is
  equity-memo-specific; a tearsheet would mint its own `type` descriptor
  (`report-equity-memo/references/vault-frontmatter.md:12,65-67`) — DEFERRED
  (Out of Scope).

Evidence paths appendix: investing-toolkit/skills/analysis-kpi/scripts/kpi_store.py ·
investing-toolkit/skills/analysis-kpi/SKILL.md ·
investing-toolkit/skills/analysis-kpi/references/cli-reference.md ·
investing-toolkit/skills/report-stock-snapshot/SKILL.md ·
investing-toolkit/skills/report-screener-list/SKILL.md ·
investing-toolkit/skills/report-equity-memo/references/vault-frontmatter.md ·
docs/adr/0001-data-analysis-report-layers.md · investing-toolkit/CHANGELOG.md

## Alternatives Considered (Axis 4 — researched 2026-07-23, EN+JA)

| Layout | Shipped by | Verdict |
|---|---|---|
| Periods as COLUMNS, newest left (rows = metrics) | stockanalysis.com (TTM+5FY, ~30 rows), TIKR [EN] | **CHOSEN** — scales for our many-periods × few-KPIs shape; our data is SEC-native, follow the US-terminal convention |
| Periods as ROWS with type-marker letters (連/中/四/予/会) | 四季報, kabutan [JA] | Rejected for v1 — fits few-periods × many-metrics; the EN/JA divergence is real (both ecosystems internally consistent). **Conditional reversal**: a JP-market tearsheet (EDINET-sourced, JP audience) flips to this layout |
| Restatement as "As Restated" extra column | ASC 250 / SEC FRM practice [EN] | Rejected — one extra column per restated period is too wide for a one-pager |
| Restatement as document-title flag（訂正）/ 訂正前・訂正後 side-by-side | TSE 適時開示 practice [JA] | Rejected — document-level granularity, ours is cell-level |
| Cell marker + below-table vintage footnote | Generalized from 四季報's marker-letter pattern | **CHOSEN** — the only convention that survives at cell granularity |

Sell-side page-1 (rating/target banner) and factsheet skeleton informed the
header/footer; no rating/verdict on the tearsheet (it reads the store, it does
not judge — verdicts belong to the memo pipeline).

## What Becomes Obsolete (Axis 5)

- The ad-hoc "import kpi_store in a python one-liner" read practice (this
  session's e2e demo script shape) — replaced by the CLI + tearsheet.
- `investing-toolkit/CHANGELOG.md:84`'s "tearsheet deferred" note — superseded
  by this arc's CHANGELOG entry.
- Nothing else: the change is additive by design (YAGNI checked: the additive
  scope IS the user-chosen purpose of the arc — make the shipped store
  usable; scope deliberately minimal, vault delivery deferred).

## Decision

Build (1) CLI read exposure on kpi_store, (2) `report-kpi-tearsheet` skill
with a pure Markdown formatter (periods-as-columns, cell-marker + vintage
footnote for disagreements, graceful-empty), (3) docs + version bump. Do NOT
build: vault delivery, coverage-file schema, JP layout variant, any analysis/
verdict content, any store write path.

## Out of Scope

- Obsidian vault delivery (own frontmatter `type` design — follow-up ride-on)
- Coverage-file schema (tearsheet reads the store directly; the store IS the
  per-company artifact for now)
- prose-lane user-facing SKILL wiring (separate pending BACKLOG item)
- kpi_memo_feed / quarterly-XBRL feed integration (different data pool — memo
  §九 consumes the TRUSTED quarterly feed; tearsheet reads the CURATED
  confirmed store)
- Retention/lookback policy (dropped in Slice C as unevidenced)
- JP periods-as-rows variant (documented conditional reversal)

## Open Questions

- Exact CLI read-subcommand shape (`list-series` + `dump --company` vs
  per-read subcommands) — plan time, driven by what the formatter minimally
  needs.
- Disagreement marker syntax in plain Markdown (superscript char vs `[^n]`
  footnote syntax) — plan time; must render in terminal AND Obsidian.

## Design-side on-ramp (Axis 0)

Reception rows 1 (no `docs/loom/PRINCIPLES.md`, product-shaped) and 2
(user-facing surface, no DESIGN.md/ui-flows) technically fire — offered to the
user ONCE with the recommendation to go DIRECT (document-genre deliverable
following two shipped report-skill precedents + a completed industry format
research; not a GUI needing the design station). User chose: (recorded at
sign-off).
