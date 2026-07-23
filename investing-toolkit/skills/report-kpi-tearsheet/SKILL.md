---
name: report-kpi-tearsheet
description: >-
  Layer-3 read-only Markdown tearsheet for one company's recorded operational
  KPIs — periods as columns (newest left), one row per kpi_id, a †-marked
  disagreement cell + Revisions footnote when a later filing changed a value.
  Subprocesses kpi_store.py `dump` then a pure formatter; no fetch, no
  analysis, no verdict. Fires on "tearsheet", "KPI tearsheet", "KPI 一頁總覽",
  "KPI 總覽", "有沒有變", "KPI ワンページ", "何を記録した". KPI 觀察歷史一頁總覽。
  KPI 観測履歴ワンページサマリー。
---

# report-kpi-tearsheet

**Layer 3 — Report** in the investing-toolkit v2.0.0 three-layer architecture
(Data → Analysis → Report). This skill answers one question: *for this
company, what operational KPIs have I recorded, for which periods, and has
any later filing changed a value?* It renders the `analysis-kpi` bitemporal
store's history as a Markdown table. It is **read-only** — it never writes to
the store, never fetches from the network, and issues no analysis or
verdict.

It subprocesses `analysis-kpi`'s store CLI and its own pure formatter (never
imports either — the analysis↔report boundary is subprocess-not-import,
`analysis-kpi/SKILL.md`).

---

## Workflow

### Step 1 — Dump the company's KPI series

```bash
uv run ${CLAUDE_PLUGIN_ROOT}/skills/analysis-kpi/scripts/kpi_store.py \
  dump --company {company} > /tmp/{company_safe}-kpi-dump.json
```

`{company}` is the store's `company` field verbatim (whatever identifier the
intake lanes wrote it under); `{company_safe}` replaces `/` and spaces with
`_` for filesystem safety. `dump` never raises: an unknown company or an
empty store yields `{"company": ..., "series": [], "warnings": []}`, exit 0.

### Step 2 — Render the Markdown tearsheet

```bash
uv run ${CLAUDE_SKILL_DIR}/scripts/tearsheet_format.py \
  --in /tmp/{company_safe}-kpi-dump.json \
  --as-of {today, issuer's local date} \
  [--store-dir {label for the footer}] \
  [--out {path}]
```

- `--in` — path to Step 1's dump JSON (omit to read stdin instead).
- `--as-of` — **required**, no wall-clock default. Pass today's date in the
  issuer's timezone (fall back to the analyst's local date if the issuer's
  timezone is unclear); it stamps the header and the provenance footer.
- `--store-dir` — optional; a label surfaced in the footer's provenance line
  (e.g. the resolved store path from Step 1, for traceability). Does not
  change where `dump` read from — that is Step 1's concern.
- `--out` — optional path to write the rendered Markdown to a file instead of
  stdout.

`tearsheet_format.py` is **pure** — no HTTP, no subprocess, no env access
beyond argparse/stdin (mirrors `snapshot_format.py`'s contract).

**Artifact gate**: when `--out` is passed, the step is not complete until the
target file exists — verify with `ls {path}` before surfacing it to the user.

---

## Store location (`KPI_STORE_DIR`)

Step 1 reads whatever store `kpi_store.py` resolves via its usual ladder:
`KPI_STORE_DIR` env override → `$XDG_DATA_HOME/investing-toolkit/kpi-store` →
`~/.local/share/investing-toolkit/kpi-store`. Set `KPI_STORE_DIR` before Step
1 to point the dump at a non-default store (e.g. a test fixture directory);
this skill does not set it itself.

---

## Output

- Header: `# KPI Tearsheet — {company}` + `As of: {as-of}`.
- One table: periods as **columns**, newest left, unified across the
  company's KPIs by raw `(period_start, period_end)` identity; one row per
  `kpi_id`; a cell shows the latest `canonical_value` with thousands
  separators (+ `unit` when present); an absent cell renders `N/A`.
- **Disagreement**: a period where a later filing recorded a different value
  for the same period renders its cell as the latest canonical value suffixed
  `†`. A trailing `## Revisions` block then lists every recorded vintage for
  that (kpi, period) — `<canonical_value> — recorded <as_of> —
  <source_accession>`, oldest first. **Both vintages are retained; neither is
  called "wrong"** — this mirrors the store's own `history` doctrine
  (a restatement supersedes, it does not erase). No disagreement anywhere →
  no `## Revisions` block.
- Footer: always a provenance line (`Rendered {as-of} from {n} series`, plus
  the `--store-dir` label when passed). If the dump carried `warnings`
  (e.g. `"skipped corrupt series file: <name>"`), a `## Warnings` block
  echoes each one verbatim.

**Graceful-empty**: an unknown company or an empty store still renders a
friendly card — `No KPI records for {company}.` — instead of an empty table,
exit 0. A corrupt series file on disk never crashes the render; it is skipped
per-file and surfaced in the `## Warnings` footer instead.

---

## Out of Scope

Mirrors the brainstorming brief (`docs/loom/specs/2026-07-23-kpi-tearsheet.md`
§Out of Scope) — this skill deliberately does NOT:

- Deliver to the Obsidian vault (its own frontmatter `type` design is a
  separate, deferred ride-on).
- Define a coverage-file schema — the tearsheet reads the store directly; the
  store IS the per-company artifact for now.
- Wire a user-facing prose-lane SKILL entry point (separate pending BACKLOG
  item).
- Read `kpi_memo_feed` / the quarterly-XBRL feed — that is a different data
  pool the memo pipeline consumes (TRUSTED quarterly feed); this skill reads
  the CURATED confirmed store instead.
- Issue any analysis or verdict — it reads the store, it does not judge;
  Buy/Hold/Sell-shaped verdicts belong to `report-equity-memo` /
  `domain-teams:investing-team`.
- Apply a retention/lookback policy, or switch to a periods-as-rows layout
  (a documented conditional reversal for a future JP-market variant only).

---

## See also

- `analysis-kpi` — Layer 2 bitemporal KPI store (`kpi_store.py`
  `append` / `query` / `list-series` / `dump`); `references/cli-reference.md`
  documents every subcommand.
- `report-stock-snapshot` — pure-formatter precedent this skill's
  `tearsheet_format.py` follows.
- `report-equity-memo` — full investment memo with verdicts; the destination
  for analysis this skill deliberately omits.

---

_Layer 3 (Report) skill • investing-toolkit • KPI 觀察歷史一頁總覽（期別為欄、
變更用 † 標記） • KPI 観測履歴ワンページサマリー（期間を列に、変更は † マー
クで表示）_
