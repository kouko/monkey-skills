# Plan: KPI tearsheet — store read CLI + report-kpi-tearsheet formatter

Source brief: docs/loom/specs/2026-07-23-kpi-tearsheet.md
Total tasks: 9
Critical-path depth: 5 (≤5 ✓) — longest chain: Task 3 → Task 4 → Task 5 → Task 6 → Task 9 (chain A Task 1 → Task 2 joins at level 2; Tasks 7, 8 join mid-graph)
Execution order: parallel-where-possible
Plan-document-reviewer verdict: PASS (2026-07-23, round 2, 14/14 checks; round-1 gap = --out flag had no implementing task, fixed into Task 5)

## Notes

- **Change-folder binding: N/A, loudly.** Two non-archived change-folders exist
  (`docs/loom/2026-07-12-us-sec-primary-source-layer/`,
  `docs/loom/2026-07-19-8k-prose-kpi-intake/`); grep-verified NEITHER covers a
  tearsheet capability (0 hits; their Requirements are intake-side, reserved
  for Part 3 / prose-lane arcs). This plan derives from the brainstorming
  brief only. Do not bind either folder.
- **PINNED dump payload schema (SSOT for Tasks 2, 3, 4, 5, 8; transcribe
  VERBATIM from this pin, never from each other).** `kpi_store.py dump
  --company <C>` emits exactly this JSON object to stdout:

  ```json
  {
    "company": "<C>",
    "series": [
      {
        "kpi_id": "<kpi_id>",
        "periods": [
          {
            "period_start": "YYYY-MM-DD or null",
            "period_end": "YYYY-MM-DD or null",
            "period_kind": "duration | instant | null",
            "period_axis_key": "<snapped-month-end-ISO>|q<qtrs> or null",
            "period_labels": ["<every distinct point['period'] label observed>"],
            "disagreement": false,
            "latest": { "...point fields verbatim...": "", "canonical_value": 0 },
            "observations": [ { "...point fields verbatim...": "", "canonical_value": 0 } ]
          }
        ]
      }
    ],
    "warnings": []
  }
  ```

  Semantics: `series` sorted by `kpi_id`; `periods` grouped via the store's own
  `same_period` (raw date-pair identity, labels display-only) and sorted
  ascending by `_period_sort_key`; `observations` sorted ascending by `as_of`,
  each point verbatim-plus-`canonical_value` (computed by the store's
  `_canonical_value` — Decimal, never float); `latest` = the max-`as_of`
  observation; `disagreement` per the store's `history` doctrine (≥2
  observations AND ≥2 distinct canonical values); `warnings` carries
  corrupt-file skip notes (`"skipped corrupt series file: <name>"`). Unknown
  company or empty store → `{"company": "<C>", "series": [], "warnings": []}`,
  exit 0.
- **Rendering commitments from the brief (Tasks 3-5)**: periods as COLUMNS
  newest-left; one row per kpi_id; unified period axis across the company's
  KPIs (same_period identity); absent cell `N/A`; disagreement cell = latest
  canonical value + `†` marker (plain-char superscript-style, renders in
  terminal AND Obsidian — resolves the brief's marker Open Question); footnote
  block lists every vintage (canonical value, as_of, source_accession);
  header = company + as-of render date; footer = provenance (store dir,
  series-file count) + warnings.
- Test command (all tasks): `PYTHONDONTWRITEBYTECODE=1 uv run --quiet --with
  pytest --with 'pyyaml>=6.0' pytest investing-toolkit/tests/ -m "not network"
  -q`. Never write __pycache__ into skill dirs (hook blocks edits).
- Post-PASS amendment note 2 (2026-07-24, whole-branch review fix): the pinned
  schema gains `period_axis_key` — the store-owned canonical cross-KPI
  column-alignment identity (`"<snapped-month-end>|q<qtrs>"`, null when
  uncomputable; null keys never merge). Added because the whole-branch review
  found the formatter's raw-tuple axis diverged from `same_period` in both
  directions (drift-split + silent degenerate-entry overwrite). Schema-only
  pin amendment; task fields/DAG unchanged — re-review of the plan document
  skipped per §Amending a PASS plan; the CODE change is under whole-branch
  review round 2.
- Post-PASS amendment note: kickoff-decision lines below added to ## Notes
  after the round-2 PASS — additive prose only, no task/field/DAG change —
  re-review skipped per writing-plans §Amending a PASS plan.
- Kickoff decision: cell value display → render `canonical_value` with
  thousands separators, verbatim-faithful (no B/M lossy compaction), `unit`
  appended when present. (Two-way door, agent-decided, recorded unbriefed.)
- Kickoff sweep result: zero one-way-door decisions (read-only arc, no store
  format change, internal co-shipped payload contract, presentation-layer
  layout already user-signed in the brief).
- Decision Log: [2026-07-24, T2 round-2 review] The reviewer live-reproduced a
  PRE-EXISTING corrupt-file escape in the untouched `list_series`/`history`
  readers (non-dict JSON → AttributeError through `_load_series`, violating
  their own never-raise contracts — same class as the T2 finding fixed in
  `dump_company`). Two-way door, no briefing: agent decided FIX-NOW on this
  branch as micro-task T2b (root-cause guard inside `_load_series` +
  RED tests for both readers + the dict-with-non-list-points sub-path test
  T2 round-2 flagged), per the repo's cheap-hardening-over-threshold rule,
  rather than BACKLOG deferral.
- Implementer trap-guards: Read a file before Edit; on modified-since-read,
  re-Read then re-Edit — never retry the same diff. If a guard/hook blocks the
  same command twice, stop and report verbatim. The Write tool refuses the
  basename `report.md`. Conventional-commit subjects: whitelisted type +
  MANDATORY scope, e.g. `feat(investing-toolkit): ...`.

## Task 1 — kpi_store CLI: `list-series` subcommand

- Description: Add a `list-series` subcommand to `kpi_store.py`'s existing
  argparse CLI that prints `list_series()`'s result as a JSON array of
  `[company, kpi_id]` pairs to stdout, exit 0 (empty store → `[]`, exit 0).
- Module: investing-toolkit/skills/analysis-kpi/scripts/kpi_store.py
- Files touched: investing-toolkit/skills/analysis-kpi/scripts/kpi_store.py,
  investing-toolkit/tests/test_kpi_store_read_cli.py
- Context paths:
  - investing-toolkit/skills/analysis-kpi/scripts/kpi_store.py (`main` :628,
    `_cli_query` :613 exit-code conventions, `list_series` :517)
  - investing-toolkit/tests/ (existing kpi store CLI test conventions — find
    the test file exercising the append/query CLI and mirror its
    subprocess+`KPI_STORE_DIR` tmp-dir pattern)
- Acceptance:
  - RED: `test_kpi_store_read_cli.py::test_list_series_prints_pairs_json`
    fails (subcommand does not exist; argparse exits 2)
  - GREEN: with two appended points (two distinct series) under a tmp
    `KPI_STORE_DIR`, `kpi_store.py list-series` exits 0 and stdout parses to
    the two sorted `[company, kpi_id]` pairs; empty store → `[]` exit 0
- External surfaces: none (stdlib argparse/json; store files on disk)
- Dependencies: none
- Independent: true
- Brief item covered: "kpi_store.py CLI grows read exposure … candidates:
  `list-series` + a one-company `dump`" (brief §Smallest End State 1)

## Task 2 — kpi_store CLI: `dump --company` subcommand (pinned payload)

- Description: Add a `dump --company <C>` subcommand emitting the PINNED
  payload (## Notes schema, transcribe verbatim): group each of the company's
  series' points into periods via `same_period`, sort per pin, compute
  `canonical_value` via `_canonical_value`, `disagreement` per `history`
  doctrine, `latest` = max-as_of, corrupt series files skipped per-file into
  `warnings`. Unknown company/empty store → empty-`series` payload, exit 0.
- Module: investing-toolkit/skills/analysis-kpi/scripts/kpi_store.py
- Files touched: investing-toolkit/skills/analysis-kpi/scripts/kpi_store.py,
  investing-toolkit/tests/test_kpi_store_read_cli.py
- Context paths:
  - investing-toolkit/skills/analysis-kpi/scripts/kpi_store.py (`same_period`
    :230, `_period_sort_key` :274, `_canonical_value` :403, `history` :440,
    `list_kpis` :571, corrupt-skip pattern :530-540)
  - docs/loom/plans/2026-07-23-kpi-tearsheet.md (## Notes pinned schema)
- Acceptance:
  - RED: `test_kpi_store_read_cli.py::test_dump_groups_vintages_and_flags_disagreement`
    fails (subcommand does not exist)
  - GREEN: a series holding two same-period vintages with different values
    (J&J shape) + one single-observation period dumps to the pinned shape:
    one period entry with 2 observations, `disagreement: true`,
    `canonical_value` Decimal-correct for a `(value="93,775", scale=1e6)`
    point vs a base point; label-only differences do NOT split a period;
    unknown company → empty payload exit 0
- External surfaces: none
- Dependencies: Task 1 completes first (same file — argparse `main` region)
- Independent: false
- Brief item covered: "the store's import-only reads … must become
  CLI-reachable first" (brief §Smallest End State 1)

## Task 3 — tearsheet_format.py: core KPI × period table

- Description: Create
  `investing-toolkit/skills/report-kpi-tearsheet/scripts/tearsheet_format.py`
  (pure formatter, PEP 723 stdlib-only, no HTTP/subprocess) with
  `render_tearsheet(dump: dict) -> str` and a CLI `--in <dump.json>` /
  stdin → Markdown to stdout: header (`# KPI Tearsheet — <company>` +
  as-of render date passed via `--as-of`, required — no wall-clock default),
  one table with periods as COLUMNS newest-left (unified across KPIs by the
  pin's period entries; column header = shortest period label, tiebreak
  first-seen), one row per `kpi_id`, latest `canonical_value` (+ `unit` when
  present) per cell, `N/A` for absent cells.
- Module: investing-toolkit/skills/report-kpi-tearsheet/scripts/tearsheet_format.py
- Files touched:
  investing-toolkit/skills/report-kpi-tearsheet/scripts/tearsheet_format.py,
  investing-toolkit/tests/test_tearsheet_format.py
- Context paths:
  - docs/loom/plans/2026-07-23-kpi-tearsheet.md (## Notes pinned schema —
    fixtures transcribe VERBATIM from the pin, never hand-shaped)
  - investing-toolkit/skills/report-stock-snapshot/scripts/snapshot_format.py
    (pure-formatter precedent: arg shape, stdout contract, N/A handling)
- Acceptance:
  - RED: `test_tearsheet_format.py::test_table_periods_as_columns_newest_left`
    fails (module does not exist)
  - GREEN: a pin-shaped fixture with 2 KPIs × 3 periods (one KPI missing one
    period) renders a Markdown table whose header row orders period columns
    newest-left and whose missing cell is `N/A`
- External surfaces: none (stdlib only — snapshot_format.py precedent)
- Dependencies: none (fixtures from the pinned schema, not from Task 2's code)
- Independent: true
- Brief item covered: "periods as columns (newest left), one row per kpi_id;
  unified period axis … absent cell → N/A" (brief §Smallest End State 2)

## Task 4 — tearsheet_format.py: disagreement marker + vintage footnote

- Description: Extend the renderer: a period cell whose pin entry has
  `disagreement: true` renders the latest canonical value suffixed with `†`;
  after the table, a `## Revisions` block lists, per flagged (kpi, period),
  every observation as `<canonical_value> — recorded <as_of> —
  <source_accession>` in as_of order. No flagged cells → no block.
- Module: investing-toolkit/skills/report-kpi-tearsheet/scripts/tearsheet_format.py
- Files touched:
  investing-toolkit/skills/report-kpi-tearsheet/scripts/tearsheet_format.py,
  investing-toolkit/tests/test_tearsheet_format.py
- Context paths:
  - docs/loom/plans/2026-07-23-kpi-tearsheet.md (## Notes pinned schema +
    rendering commitments)
- Acceptance:
  - RED: `test_tearsheet_format.py::test_disagreement_cell_marker_and_revisions_block`
    fails (marker/block not rendered)
  - GREEN: a fixture with one two-vintage disagreement period renders `†` on
    that cell only, and the `## Revisions` block lists both vintages with
    as_of + accession; a no-disagreement fixture renders no `## Revisions`
    heading
- External surfaces: none
- Dependencies: Task 3 completes first
- Independent: false
- Brief item covered: "Multi-vintage disagreement: cell … marker; a footnote
  block … lists EVERY vintage (value, as_of, source accession)" (brief
  §Smallest End State 2)

## Task 5 — tearsheet_format.py: graceful-empty + provenance/warnings footer

- Description: Extend the renderer: empty `series` → a "No KPI records for
  <company>." card (still exit 0); footer always renders a provenance line
  (`Rendered <as-of> from <n> series` + `--store-dir` label when passed) and,
  when `warnings` is non-empty, a `## Warnings` block echoing each warning
  verbatim (snapshot/screener partial-footer precedent); add the optional
  `--out <path>` flag — write the rendered Markdown to `<path>` (stdout
  default unchanged), exit 0.
- Module: investing-toolkit/skills/report-kpi-tearsheet/scripts/tearsheet_format.py
- Files touched:
  investing-toolkit/skills/report-kpi-tearsheet/scripts/tearsheet_format.py,
  investing-toolkit/tests/test_tearsheet_format.py
- Context paths:
  - docs/loom/plans/2026-07-23-kpi-tearsheet.md (## Notes pinned schema)
  - investing-toolkit/skills/report-screener-list/SKILL.md (:115-117 warnings
    footer precedent)
- Acceptance:
  - RED: `test_tearsheet_format.py::test_empty_series_card_and_warnings_footer`
    fails
  - GREEN: empty-series fixture renders the no-records card + provenance
    footer, exit 0; a fixture with one warning renders it verbatim in
    `## Warnings`; with `--out <tmp>/tearsheet.md` the identical Markdown
    lands at that path (file exists, content == stdout-mode output)
- External surfaces: none
- Dependencies: Task 4 completes first (same file)
- Independent: false
- Brief item covered: "graceful-empty conventions … missing → N/A,
  partial/corrupt-skip surfaced in a warnings footer" (brief §Smallest End
  State 2)

## Task 6 — report-kpi-tearsheet SKILL.md

- Description: Author
  `investing-toolkit/skills/report-kpi-tearsheet/SKILL.md` (frontmatter
  name+description per repo convention; body ≤ soft cap): Layer-3 read-only
  deliverable; two-step workflow (subprocess-not-import, snapshot precedent):
  `uv run …/analysis-kpi/scripts/kpi_store.py dump --company <C> >
  /tmp/<C>-kpi-dump.json` then `uv run …/report-kpi-tearsheet/scripts/
  tearsheet_format.py --in /tmp/<C>-kpi-dump.json --as-of <date>`; artifact
  gate (`ls` the output when `--out` used); `KPI_STORE_DIR` override note;
  graceful-empty statement; Out-of-Scope mirror (no vault delivery, no
  verdicts, reads curated store not the quarterly feed); i18n footer
  (ja/zh-TW/en) per sibling skills.
- Module: investing-toolkit/skills/report-kpi-tearsheet/SKILL.md
- Files touched: investing-toolkit/skills/report-kpi-tearsheet/SKILL.md
- Context paths:
  - investing-toolkit/skills/report-stock-snapshot/SKILL.md (structure +
    workflow-section precedent)
  - docs/loom/specs/2026-07-23-kpi-tearsheet.md (§Smallest End State, §Out of
    Scope — transcribe scope statements)
  - docs/loom/plans/2026-07-23-kpi-tearsheet.md (## Notes — the two shipped
    CLI shapes to document; transcribe flags verbatim from Tasks 2/5 GREEN)
- Acceptance:
  - RED: `investing-toolkit/skills/report-kpi-tearsheet/SKILL.md` absent
    (diagnostic: `test -f` fails)
  - GREEN: file exists; grep confirms `dump --company`, `--in`, `--as-of`,
    `KPI_STORE_DIR`, and an Out-of-Scope section naming vault delivery; the
    skill-folder-structure hook accepts the layout (flat subfolders only)
- External surfaces: none (prose)
- Dependencies: Tasks 2, 5 complete first (documents both CLIs — doc-mirrors-code)
- Independent: false
- Brief item covered: "New skill `report-kpi-tearsheet` … the new skill's
  SKILL.md documents the read workflow" (brief §Smallest End State 2-3)

## Task 7 — cli-reference.md: document the new read subcommands

- Description: Extend
  `investing-toolkit/skills/analysis-kpi/references/cli-reference.md`'s
  kpi_store section with `list-series` and `dump --company` (flags, exit
  codes, one worked example each, payload pointed at — not copied — via a
  one-line shape summary + pointer to the tearsheet skill).
- Module: investing-toolkit/skills/analysis-kpi/references/cli-reference.md
- Files touched:
  investing-toolkit/skills/analysis-kpi/references/cli-reference.md
- Context paths:
  - investing-toolkit/skills/analysis-kpi/references/cli-reference.md (:9-41
    existing kpi_store section format)
  - docs/loom/plans/2026-07-23-kpi-tearsheet.md (## Notes pinned schema —
    summarize, don't copy)
- Acceptance:
  - RED: grep for `list-series` in cli-reference.md returns 0 hits
  - GREEN: both subcommands documented in the existing table format; grep
    finds `list-series` and `dump` with `--company` in the kpi_store section
- External surfaces: none (prose)
- Dependencies: Task 2 completes first (doc-mirrors-code)
- Independent: false
- Brief item covered: "`analysis-kpi/references/cli-reference.md` gains the
  new read subcommands" (brief §Smallest End State 3)

## Task 8 — producer↔consumer integration test (real store → dump → render)

- Description: New test that, under a tmp `KPI_STORE_DIR`, appends real
  points via `kpi_store.py append` CLI (two vintages of one period + one
  other-period point, J&J shape), runs `dump --company` via subprocess, feeds
  the ACTUAL dump bytes to `tearsheet_format.py` via subprocess, and asserts
  the rendered Markdown shows the `†` marker + both vintages in
  `## Revisions`. This closes the pin↔reality seam: if Task 2's real payload
  drifts from the pin the formatter fixtures were built on, THIS test fails.
- Module: investing-toolkit/tests/test_tearsheet_integration.py
- Files touched: investing-toolkit/tests/test_tearsheet_integration.py
- Context paths:
  - investing-toolkit/tests/test_kpi_store_read_cli.py (Task 1/2 subprocess
    conventions)
  - docs/loom/plans/2026-07-23-kpi-tearsheet.md (## Notes pinned schema)
- Acceptance:
  - RED: `test_tearsheet_integration.py::test_store_to_tearsheet_end_to_end`
    fails before Tasks 2+5 land (subcommand/module absent); after they land
    it must pass WITHOUT modification
  - GREEN: end-to-end subprocess chain renders the disagreement marker +
    revisions block from a real store on disk
- External surfaces: none
- Dependencies: Tasks 2, 5 complete first
- Independent: false
- Brief item covered: brief §Current State Evidence Boundary (subprocess
  crossing) + repo memory `market-canonical-must-satisfy-consumer-field-contract`
  / `fixtures-mirror-producer-shape` (structural seam closure)

## Task 9 — version bump + CHANGELOG + codex manifest sync

- Description: Bump investing-toolkit to `2.32.0` in
  `.claude-plugin/plugin.json`, run `python3 scripts/sync_codex_manifests.py
  investing-toolkit` (mirrors `.codex-plugin/plugin.json`), add the
  `## [v2.32.0] — <date>` CHANGELOG entry (new skill + store read CLI +
  supersedes CHANGELOG:84's "tearsheet deferred" note), stamp the entry's
  test count via `pytest --collect-only` at close-out.
- Module: investing-toolkit/.claude-plugin/plugin.json (primary; mirror +
  CHANGELOG ride along per repo version-bump convention)
- Files touched: investing-toolkit/.claude-plugin/plugin.json,
  investing-toolkit/.codex-plugin/plugin.json, investing-toolkit/CHANGELOG.md
- Context paths:
  - investing-toolkit/CHANGELOG.md (entry format; :84 deferral note to
    supersede)
  - scripts/sync_codex_manifests.py (mirror mechanism)
- Acceptance:
  - RED: grep `2.32.0` in investing-toolkit/.claude-plugin/plugin.json
    returns 0 hits
  - GREEN: both plugin.json files read `2.32.0`; CHANGELOG has the v2.32.0
    entry; the codex-manifest-drift hook/CI check is clean
- External surfaces: none
- Dependencies: Tasks 6, 7, 8 complete first (version last)
- Independent: false
- Brief item covered: "Docs … investing-toolkit version bump + CHANGELOG"
  (brief §Smallest End State 3; §Axis 5 CHANGELOG:84 supersession)
