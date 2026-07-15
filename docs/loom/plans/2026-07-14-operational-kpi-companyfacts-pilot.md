# Plan: operational-kpi tier-② XBRL pilot (flat + dimensional, era-binding, declared break)

Source brief: docs/loom/specs/2026-07-14-operational-kpi-companyfacts-pilot.md
Total tasks: 6
Critical-path depth: 4 (≤5)   ← T1 → T2 → T3 → T6 (T4, T5 parallel leaves feeding T6)
Execution order: parallel-where-possible (Wave 1 = T1, T4, T5 — disjoint files)
Plan-document-reviewer verdict: PASS (2026-07-14, round 2 — prior Check-7 gap on Task 4 closed via the attest_source redesign; all 6 GREENs verified observable & achievable against real code)

Notes:
- Real captured fixture already committed: investing-toolkit/tests/analysis/fixtures/xbrl_aapl_factpack.json
  (verified live Apple values: iPhone revenue OLD-era FY2016 155.041B under SalesRevenueNet+
  us-gaap:ProductOrServiceAxis+AppleIphoneMember, NEW-era FY2024 201.183B / FY2025 209.628B under
  RevenueFromContract+srt:ProductOrServiceAxis+aapl:IPhoneMember; gross_profit FY2024 180.683B /
  FY2025 195.228B flat). The analysis layer (T1-T3) TDDs against this offline fixture; the data
  layer (T5) + e2e (T6) hit live edgartools behind the `network` marker (tests/conftest.py registers it).
- kpi_xbrl.py is PURE COMPUTE (stdlib only; mirrors kpi_validate/kpi_parse — no _store_fs import,
  no network). Anti-fabrication core: a missing/malformed fact RAISES, never a 0; a true 0 is a value.
- Fact-pack shape (declared, = the fixture): {company, facts:[{concept, axis, member, value,
  period_end, fiscal_year, accession, filed}]} — axis/member null for a flat concept.
- AMENDMENT (2026-07-14, post-Wave-1 review + live cross-check; additive safety, re-reviewed by
  re-dispatch): (a) T1/T5 — `period` MUST be derived from `period_end` (the year the fiscal
  period ENDS: `period_end[:4]` for Apple's Sept fiscal end), NEVER from edgartools' raw
  `fiscal_year` column, which is unreliable for prior-year comparatives (a fact ending 2024-09-28
  is column-labeled fiscal_year 2025 — off by one); a missing/malformed `period_end` FAILS LOUD
  (never emit period "None"). (b) T4 — an EMPTY `source_kinds` set must NOT attest TRUSTED (the
  "non-empty AND ⊆" conjunct): raise, never manufacture trust from zero source.

## Task 1 — kpi_xbrl fact→points adapter (fail-loud, provenance-mapped, source_kind)
- Description: Create `scripts/kpi_xbrl.py` (PEP-723, stdlib only). `facts_to_points(fact_pack,
  kpi_id, match, company, source_kind)` → a list of kpi_store-shaped points for facts matching a
  `match` (concept[+axis+member]) selector. Map XBRL provenance into the point shape:
  `source_accession`=fact `accession`, `source_table_id`=`"xbrl:"+axis` (or `"xbrl:companyfacts"`
  when axis is null), `source_cell_ref`=`concept` (flat) or `concept+"|"+member` (dimensional),
  `as_of`=fact `filed`, `period`=`fiscal_year` (str), `value`=fact `value`, plus `source_kind`.
  FAIL LOUD: a fact missing `value`/`accession`/`filed`, or a non-numeric value, RAISES a
  distinct ValueError naming the field — never emit a 0. Register KPI_XBRL_SCRIPT in
  tests/analysis/conftest.py AND register the `network` pytest marker there (mirrors
  tests/data/conftest.py — the later live tests T5/T6 need it registered in the analysis subtree).
- Module: investing-toolkit/skills/analysis-kpi/scripts/kpi_xbrl.py
- Files touched: investing-toolkit/skills/analysis-kpi/scripts/kpi_xbrl.py,
  investing-toolkit/tests/analysis/test_kpi_xbrl.py,
  investing-toolkit/tests/analysis/conftest.py
- Context paths:
  - investing-toolkit/skills/analysis-kpi/scripts/kpi_parse.py
  - investing-toolkit/skills/analysis-kpi/scripts/kpi_store.py
  - investing-toolkit/tests/analysis/fixtures/xbrl_aapl_factpack.json
- Acceptance:
  - RED: investing-toolkit/tests/analysis/test_kpi_xbrl.py::test_facts_to_points_maps_provenance_and_fails_loud
  - GREEN: from the fixture, the NEW-era iPhone fact → a point with value 209586000000,
    period "2025", source_accession "0000320193-25-000079", source_table_id
    "xbrl:srt:ProductOrServiceAxis", source_cell_ref
    "us-gaap:RevenueFromContractWithCustomerExcludingAssessedTax|aapl:IPhoneMember",
    as_of "2025-10-31", source_kind "xbrl-dimensional"; a fact with `value` removed RAISES
    (not a 0); a flat GrossProfit fact → source_table_id "xbrl:companyfacts", source_cell_ref
    "us-gaap:GrossProfit".
- External surfaces: stdlib only (json); no third-party.
- Dependencies: none
- Independent: true
- Brief item covered: Smallest End State #2 "Fact → points adapter … maps XBRL provenance into
  the point shape … FAIL LOUD … never a 0".

## Task 2 — era-specific logical-KPI binding resolver
- Description: Extend `kpi_xbrl.py` with `resolve_binding(fact_pack, binding, company)` where
  `binding` = `{kpi_id, sources:[{concept, axis, member, fy_min, fy_max, source_kind}]}`. Each
  fact is matched against the ordered `sources` (a source matches when concept+axis+member equal
  AND fiscal_year ∈ [fy_min, fy_max]); a matched fact is emitted (via Task-1 `facts_to_points`)
  under the single logical `kpi_id`. A fact matching no source is skipped (not fabricated); a
  fact matching >1 source RAISES (ambiguous binding). Reuses Task-1 mapping, not a reimpl.
- Module: investing-toolkit/skills/analysis-kpi/scripts/kpi_xbrl.py
- Files touched: investing-toolkit/skills/analysis-kpi/scripts/kpi_xbrl.py,
  investing-toolkit/tests/analysis/test_kpi_xbrl.py
- Context paths:
  - investing-toolkit/skills/analysis-kpi/scripts/kpi_xbrl.py
  - investing-toolkit/tests/analysis/fixtures/xbrl_aapl_factpack.json
- Acceptance:
  - RED: ...::test_resolve_binding_stitches_two_eras_into_one_kpi_id
  - GREEN: the `iphone_revenue` binding (sources: OLD SalesRevenueNet/us-gaap:ProductOrServiceAxis/
    aapl:AppleIphoneMember fy≤2017; NEW RevenueFromContract/srt:ProductOrServiceAxis/
    aapl:IPhoneMember fy≥2018) resolves the fixture's FY2016 + FY2024 + FY2025 iPhone facts all
    under kpi_id "iphone_revenue" (3 points); the GrossProfit facts match no iphone source (skipped).
- External surfaces: stdlib only.
- Dependencies: Task 1 completes first
- Independent: false
- Brief item covered: Smallest End State #3 "Era-specific binding … resolves each fact to its
  logical kpi_id, emitting points under one id across eras (a multi-facet remap)".

## Task 3 — declared structural break → non-naive dual series
- Description: Extend `kpi_xbrl.py` with `build_series_with_break(points, break_at_period)` that
  builds a local `applied_breaks=[{"break_period": break_at_period}]` from the declared boundary
  and delegates to the existing pure-compute `kpi_series.split_series(points, applied_breaks)`
  (slice 7 — plain args, NO persisted break lifecycle) so the resolved `iphone_revenue` points
  become a dual series SPLIT at the 2018 boundary — never a naive concat across the tagging-regime
  change. Imports kpi_series only (NOT kpi_break — the declared/pre-applied break intentionally
  bypasses kpi_break's persisted FLAGGED→CONFIRMED→APPLIED review-queue lifecycle).
- Module: investing-toolkit/skills/analysis-kpi/scripts/kpi_xbrl.py
- Files touched: investing-toolkit/skills/analysis-kpi/scripts/kpi_xbrl.py,
  investing-toolkit/tests/analysis/test_kpi_xbrl.py
- Context paths:
  - investing-toolkit/skills/analysis-kpi/scripts/kpi_series.py
  - investing-toolkit/skills/analysis-kpi/scripts/kpi_xbrl.py
- Acceptance:
  - RED: ...::test_declared_break_splits_series_not_concat
  - GREEN: `iphone_revenue` points (FY2016 old-tagged period "2016", FY2024/FY2025 new-tagged)
    through `build_series_with_break(points, "2018")` return `split_series`'s dict where the
    FY2016 point is in the `as_reported` partition (period < "2018") and the FY2024/FY2025 points
    are in the `recast` partition (period >= "2018") — NOT a single concatenated run.
- External surfaces: stdlib only.
- Dependencies: Task 2 completes first
- Independent: false
- Brief item covered: Smallest End State #4 "Declared structural break … the existing
  split_series/dual-series produces a correctly segmented as-reported trend — NEVER a naive concat".

## Task 4 — trusted-by-source: a gate source-attestation record for XBRL
- Description: Add `attest_source(company, schema_version, source_kinds, attested_at)` to
  `kpi_gate.py`. When `source_kinds` is non-empty AND ⊆ the trusted-by-source set
  `{"xbrl-companyfacts", "xbrl-dimensional"}`, persist a gate record (kind `"source-attestation"`,
  verdict TRUSTED) keyed by `(company, schema_version)` — via the SAME lock-guarded
  read-modify-write on the company's gate-records file that `evaluate` uses (`_gate_records_path` /
  `GATE_RECORDS_FILENAME_SUFFIX`). If `source_kinds` contains any non-trusted kind (e.g.
  `"llm-located"`), it does NOT record TRUSTED (raises a ValueError naming the offending kind) —
  so `is_trusted` stays fail-closed. `is_trusted`/`gate_verdict` are UNCHANGED (they already read
  whichever verdict is recorded) — no fabricated labels, no signature change, one trust authority.
  `attested_at` is caller-supplied (mirrors evaluate's `evaluated_at`, no wall-clock read).
- Module: investing-toolkit/skills/analysis-kpi/scripts/kpi_gate.py
- Files touched: investing-toolkit/skills/analysis-kpi/scripts/kpi_gate.py,
  investing-toolkit/tests/analysis/test_kpi_gate.py
- Context paths:
  - investing-toolkit/skills/analysis-kpi/scripts/kpi_gate.py
  - investing-toolkit/tests/analysis/test_kpi_gate.py
- Acceptance:
  - RED: ...::test_attest_source_records_trusted_for_xbrl_only
  - GREEN: `attest_source("AAPL", "1.0", {"xbrl-dimensional"}, attested_at="2026-07-14")` then
    `is_trusted("AAPL", "1.0")` is True with NO label set and NO evaluate record present;
    `attest_source("AAPL", "2.0", {"llm-located"}, attested_at="2026-07-14")` RAISES ValueError
    naming "llm-located" and leaves `is_trusted("AAPL", "2.0")` False (fail-closed unchanged).
- External surfaces: stdlib only (writes via existing _store_fs primitives).
- Dependencies: none
- Independent: true
- Brief item covered: Smallest End State #5 "Trusted-by-source … kpi_gate recognizes these
  source_kinds as auto-qualifying (no sampled label set). The gate stays meaningful for tier-③".

## Task 5 — data-layer dimensional-revenue fact-pack extractor (edgartools)
- Description: Add `extract_dimensional_revenue(ticker, form="10-K")` to `sec_edgar_client.py`:
  fetch the latest filing's XBRL via edgartools and emit the normalized fact-pack (the fixture
  shape: `{company, facts:[{concept, axis, member, value, period_end, fiscal_year, accession,
  filed}]}`) for every revenue fact carrying a product/segment/geographic axis — matching BOTH
  `us-gaap:*ProductOrServiceAxis`/`StatementBusinessSegmentsAxis`/`StatementGeographicalAxis`
  AND `srt:*` namespaces (the Apple false-negative lesson: never filter a single namespace).
- Module: investing-toolkit/skills/data-markets/scripts/sec_edgar_client.py
- Files touched: investing-toolkit/skills/data-markets/scripts/sec_edgar_client.py,
  investing-toolkit/tests/data/test_sec_edgar_dimensional_live.py
- Context paths:
  - investing-toolkit/skills/data-markets/scripts/sec_edgar_client.py
  - investing-toolkit/tests/data/test_data_markets_live.py
  - investing-toolkit/tests/analysis/fixtures/xbrl_aapl_factpack.json
- Acceptance:
  - RED: investing-toolkit/tests/data/test_sec_edgar_dimensional_live.py::test_extract_dimensional_revenue_aapl_live
  - GREEN (network-marked): `extract_dimensional_revenue("AAPL")` returns a fact-pack whose facts
    include an `aapl:IPhoneMember` (srt:ProductOrServiceAxis) revenue fact with value > 100e9 and
    the full {concept, axis, member, value, period_end, fiscal_year, accession, filed} keys; the
    new live test is marked `@pytest.mark.network` and is DESELECTED by `-m "not network"` (the
    offline suite stays green).
- External surfaces: edgartools==5.42.0 (network — SEC EDGAR XBRL; already a data-markets
  dependency via sec_edgar_client's PEP-723 header, run under `uv run --script`).
- Dependencies: none
- Independent: true
- Brief item covered: Smallest End State #1 "dimensional-revenue fact-pack extractor … BOTH
  us-gaap:* and srt:* namespaces (never filter one namespace)".

## Task 6 — end-to-end demo + kpi_xbrl CLI on real Apple data
- Description: Add a thin argparse CLI to `kpi_xbrl.py` (`build` — read a fact-pack JSON + a
  binding JSON from `--file`/stdin → resolve → points → print; mirrors kpi_memo_feed's CLI +
  exit-code convention 0/1/2). Add a `@pytest.mark.network` e2e test wiring the real chain:
  `sec_edgar_client.extract_dimensional_revenue("AAPL")` → `kpi_xbrl.resolve_binding` (iphone_revenue)
  → `build_series_with_break` (declared 2018 break); store the points; call
  `kpi_gate.attest_source(company, schema_version, {"xbrl-dimensional"}, attested_at=...)` so the
  gate records TRUSTED-by-source; then `kpi_memo_feed.build_memo_feed` (which reads
  `kpi_gate.is_trusted`) yields a TRUSTED feed — asserting iphone_revenue appears as a split dual
  series. (SCOPE AMENDMENT 2026-07-15: the live e2e proves the COMPLETE chain on iphone_revenue —
  dimensional extraction → fact→points → era-binding → declared break → trusted attestation →
  memo feed. gross_profit's FLAT-concept path is NOT re-fetched live here: T5's extractor is
  dimensional-only, and a live flat-companyfacts extractor is out of pilot scope; the flat path is
  already proven OFFLINE by T1's fixture flat-GrossProfit → point + T4's attest_source covering the
  xbrl-companyfacts source_kind. Additive scope reduction — removes an out-of-scope live fetch.)
  Document in analysis-kpi/SKILL.md `## CLI (kpi_xbrl)`.
- Module: investing-toolkit/skills/analysis-kpi/scripts/kpi_xbrl.py
- Files touched: investing-toolkit/skills/analysis-kpi/scripts/kpi_xbrl.py,
  investing-toolkit/skills/analysis-kpi/SKILL.md,
  investing-toolkit/tests/analysis/test_kpi_xbrl_e2e_live.py
- Context paths:
  - investing-toolkit/skills/analysis-kpi/scripts/kpi_memo_feed.py
  - investing-toolkit/skills/analysis-kpi/scripts/kpi_gate.py
  - investing-toolkit/skills/data-markets/scripts/sec_edgar_client.py
  - investing-toolkit/skills/analysis-kpi/SKILL.md
- Acceptance:
  - RED: investing-toolkit/tests/analysis/test_kpi_xbrl_e2e_live.py::test_apple_iphone_revenue_end_to_end_live
  - GREEN (network-marked): the e2e chain on live AAPL yields a TRUSTED memo feed containing
    `iphone_revenue` run through `build_series_with_break(points, "2018")`, with the live NEW-era
    facts (FY2023-2025, all post-2018, real values > 100e9) in the `recast` segment; `kpi_xbrl
    build --help` lists the `build` verb; the CLI verb is documented in analysis-kpi/SKILL.md
    `## CLI (kpi_xbrl)`; the offline suite (`-m "not network"`) stays green (e2e is
    @pytest.mark.network, deselected).
  - SCOPE AMENDMENT 2 (2026-07-15, live-probe discovery): `extract_dimensional_revenue` fetches
    `filings.latest()` only, so a single 10-K carries just ~3 comparative years — all NEW-era for
    AAPL. The pre-2018 OLD-era (`us-gaap:ProductOrServiceAxis`/`AppleIphoneMember`) segment is NOT
    reachable live without a multi-filing / filing-year selector (out of pilot scope — a follow-up
    slice: "multi-filing historical fetch" unlocks the full ~16-year live history). So the live e2e
    proves the COMPLETE chain wiring (live dimensional extraction → fact→points → era-binding →
    declared break → trusted attestation → TRUSTED memo feed) on the reachable NEW-era data;
    `as_reported` is legitimately EMPTY (no live OLD-era facts — never faked). The break-spanning
    dual-segment property IS proven, with REAL historical values (FY2016 + FY2024/2025), by T3's
    offline fixture test (`test_declared_break_splits_series_not_concat`, already GREEN).
- External surfaces: edgartools==5.42.0 (network; via Task-5 extractor) — the CLI itself is stdlib.
- Dependencies: Tasks 3, 4, 5 complete first
- Independent: false
- Brief item covered: Smallest End State #6 "End-to-end demonstration … real Apple → iphone_revenue
  (spans the 2018 declared break, dual series) + gross_profit … proving the 9-module chain on live data".
