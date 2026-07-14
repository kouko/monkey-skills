# Plan: operational-kpi slice 8 — memo-feed contract (final offline slice)

Source brief: docs/loom/specs/2026-07-14-operational-kpi-memo-feed.md
Total tasks: 3
Critical-path depth: 3 (≤5)   ← T1 → T2 → T3
Execution order: sequential (all tasks touch one module kpi_memo_feed.py + one test file)
Plan-document-reviewer verdict: PASS (2026-07-14; 14/14 applicable checks, no defects)

Change-folder binding: realizes a SUBSET of operational-kpi/spec.md (Requirements
"Memo-feed contract is an explicit artifact", "Provenance completeness for every
series-point" — enforced at the feed boundary). Not archived (the LLM layer is still
unshipped; archive only when the whole capability ships).

Notes:
- kpi_memo_feed.py reuses `kpi_gate.is_trusted` (slice 5) for the trust verdict (same-skill
  import); pure-assembly, takes the series data as an argument (decoupled from kpi_store,
  mirroring kpi_validate/kpi_series). FAIL-CLOSED: a non-TRUSTED company → WITHHELD feed
  with no series values (surfaced, never fabricated). No wall-clock (generated_at
  caller-supplied). A WITHHELD feed is a normal result; only malformed input is loud.

## Task 1 — kpi_memo_feed scaffold + build_memo_feed (fail-closed TRUSTED/WITHHELD typed feed)
- Description: Create `scripts/kpi_memo_feed.py` (PEP-723, same-dir import shim → `import
  kpi_gate`). `build_memo_feed(company, schema_version, kpi_series, generated_at)` queries
  `kpi_gate.is_trusted(company, schema_version)`. TRUSTED → return a typed dict
  `{"_memo_feed_schema_version": "1.0", "company", "schema_version", "status": "TRUSTED",
  "kpi_feeds": [{kpi_id, points, provenance}...] built from `kpi_series`, "generated_at"}`.
  NOT trusted → return `{... "status": "WITHHELD", "withheld_reason": <kpi_gate.gate_verdict
  result>, "kpi_feeds": [], "generated_at"}` — NO series values. Register
  KPI_MEMO_FEED_SCRIPT in conftest.
- Module: investing-toolkit/skills/analysis-kpi/scripts/kpi_memo_feed.py
- Files touched: investing-toolkit/skills/analysis-kpi/scripts/kpi_memo_feed.py,
  investing-toolkit/tests/analysis/test_kpi_memo_feed.py,
  investing-toolkit/tests/analysis/conftest.py
- Context paths:
  - investing-toolkit/skills/analysis-kpi/scripts/kpi_gate.py
  - investing-toolkit/skills/analysis-kpi/scripts/kpi_validate.py
  - docs/loom/2026-07-12-us-sec-primary-source-layer/specs/operational-kpi/spec.md
- Acceptance:
  - RED: investing-toolkit/tests/analysis/test_kpi_memo_feed.py::test_build_memo_feed_trusted_vs_withheld fails
  - GREEN: after an evaluate that yields TRUSTED (set up via kpi_gate), build_memo_feed
    returns status TRUSTED with the kpi_feeds bundled; a never-evaluated / WITHHELD company
    returns status WITHHELD, empty kpi_feeds, and a withheld_reason — NO series values.
- External surfaces: stdlib + same-skill kpi_gate import; no third-party.
- Dependencies: none
- Independent: false
- Brief item covered: Smallest End State #1 "Fail-closed feed assembly" + #2 "Explicit
  typed artifact". Change-folder join: operational-kpi / Requirement "Memo-feed contract is
  an explicit artifact" / Scenario "Trusted feed bundles series + narrative + flags with
  provenance" + Requirement "Reliability-gate withhold-below-bar" / Scenario "Below-bar
  series is not fed to the memo".

## Task 2 — provenance completeness at the feed boundary (refuse a provenance-less point)
- Description: In a TRUSTED feed, every included series-point MUST carry provenance
  (`source_accession`, `source_table_id`, `source_cell_ref` — absent/None/empty any → bad);
  `build_memo_feed` REFUSES loud (ValueError) if any point in the supplied TRUSTED series
  lacks complete provenance — never bundle an unattributed value into the artifact the memo
  trusts. (A WITHHELD feed carries no points, so this only bites the TRUSTED path.)
- Module: investing-toolkit/skills/analysis-kpi/scripts/kpi_memo_feed.py
- Files touched: investing-toolkit/skills/analysis-kpi/scripts/kpi_memo_feed.py,
  investing-toolkit/tests/analysis/test_kpi_memo_feed.py
- Context paths:
  - investing-toolkit/skills/analysis-kpi/scripts/kpi_memo_feed.py
  - investing-toolkit/skills/analysis-kpi/scripts/kpi_store.py
- Acceptance:
  - RED: ...::test_trusted_feed_refuses_provenanceless_point fails
  - GREEN: a TRUSTED build with a point missing source_cell_ref → raises loud, nothing
    returned; a fully-provenanced TRUSTED series builds fine.
- Dependencies: Task 1 completes first
- Independent: false
- Brief item covered: Smallest End State #3 "Provenance completeness". Change-folder join:
  operational-kpi / Requirement "Provenance completeness for every series-point" / Scenario
  "A series-point without a cell reference is rejected".

## Task 3 — kpi_memo_feed CLI: build
- Description: argparse CLI `build` (--company --schema-version [--generated-at] +
  kpi_series JSON from stdin/--file → build_memo_feed; print the feed JSON). Exit 0 on any
  built feed (INCLUDING a WITHHELD feed — a validly-withheld company is not a CLI error),
  1 on a provenance ValueError, 2 on malformed/non-object JSON. Document in
  analysis-kpi/SKILL.md `## CLI (kpi_memo_feed)`.
- Module: investing-toolkit/skills/analysis-kpi/scripts/kpi_memo_feed.py
- Files touched: investing-toolkit/skills/analysis-kpi/scripts/kpi_memo_feed.py,
  investing-toolkit/skills/analysis-kpi/SKILL.md,
  investing-toolkit/tests/analysis/test_kpi_memo_feed.py
- Context paths:
  - investing-toolkit/skills/analysis-kpi/scripts/kpi_memo_feed.py
  - investing-toolkit/skills/analysis-kpi/scripts/kpi_gate.py
  - investing-toolkit/skills/analysis-kpi/SKILL.md
- Acceptance:
  - RED: ...::test_cli_build_memo_feed_roundtrip fails
  - GREEN: (after a kpi_gate evaluate → TRUSTED setup, same KPI_STORE_DIR) `build` a
    provenanced kpi_series → status TRUSTED feed on stdout, exit 0; a WITHHELD company →
    status WITHHELD, exit 0; a provenance-less TRUSTED point → exit 1; malformed JSON →
    exit 2; `--help` lists `build` AND SKILL.md `## CLI (kpi_memo_feed)` documents it.
- Command surface: the build verb declared in analysis-kpi/SKILL.md `## CLI (kpi_memo_feed)`.
- Dependencies: Tasks 1, 2 complete first
- Independent: false
- Brief item covered: Smallest End State #4 "a thin CLI".
