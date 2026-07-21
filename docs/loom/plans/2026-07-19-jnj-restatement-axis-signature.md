# Plan: JNJ RestatementAxis 修復 — vintage-axis exclusion + per-signature refusal granularity

Source brief: docs/loom/specs/2026-07-19-jnj-restatement-axis-signature.md
Total tasks: 5
Critical-path depth: 4 (T1 → T2 → T3 → {T4, T5})
Execution order: parallel-where-possible (final wave T4/T5)
Plan-document-reviewer verdict: PASS (2026-07-19, 14/14)

## Notes

- **Change-folder detection**: only non-archived folder is the shipped US SEC
  arc's stale one (pending archive ruling) — wrong-bind, N/A; plan derives
  from the brainstorming brief.
- **Kickoff decision: signature shape frozen** — NO fourth signature field;
  signature stays `{concept, dimensions, consolidation}` (exact-3-key pin
  test_kpi_xbrl.py:2625-2629 must stay green untouched). User-ratified via
  brief checkpoint; grounded in XBRL US default-member semantics.
- **Kickoff decision: fail-closed direction** — a fact carrying ANY
  non-whitelist `dim_` axis is excluded-with-count, never collapsed onto the
  default signature. RestatementAxis is the named vintage category; anything
  else counts as unknown-axis (allowlist discipline per
  docs/loom/memory/shared-classifier-over-open-dialects-needs-allowlist.md).
- Kickoff decision (arm-1 delegations, implementer decides + test pins):
  exact pack-level exclusion counter channel (read the existing pack
  accounting — `selection_gaps` sibling or new counter — and match its
  schema style); the new coverage_flag type string for the memo-visible
  recast annotation (self-describing, morphology-consistent with existing
  flag types like `no_quarterly_coverage`).
- **domain-teams verified untouched at plan time**: the memo protocol's
  coverage_flags rule is generic ("top-level coverage_flags[] disclosed
  inline on the affected cell(s), never truncated",
  deep-equity-research-memo.md trend-table bullets) — a new flag type needs
  no protocol edit, no domain-teams bump.
- **Live JNJ acceptance** (brief SES 4b: feed TRUSTED + recast annotation;
  RED baseline = scratchpad sweep_JNJ_series.err refusal) is a
  finishing-phase step (network), mirroring the two prior arcs — SDD
  suite-green alone does not close it.
- Fixture red lines: machine-captured or factory-synthetic per existing
  conventions with `_provenance`; never hand-type XBRL values.
  PYTHONDONTWRITEBYTECODE=1; never `git add -A`; stray __pycache__ under
  skills/ → `trash`, not rm.
- **Post-PASS amendment (re-review skipped, additive + schema-safe)**: per
  reviewer note, kpi_memo_feed.py added to Task 2's Files touched (its
  Description already permitted the conditional edit); all fields and DAG
  unchanged.
- Kickoff decision: one-way-door sweep → no NEW one-way doors; the
  signature-shape ruling (no 4th field) was user-ratified at the brief
  checkpoint with two research rounds behind it.
- Execution decision (post-T5, 12-ticker live sweep, fd6650e9): T1's
  exclusion regressed INTC — its 2021-2023 filings tag segment facts with
  `srt:ConsolidatedEntitiesAxis = OperatingSegmentsMember`, a sibling-axis
  spelling of the recognized consolidation qualifier (member value equals
  ConsolidationItemsAxis's default, proving semantics). Fix: promoted
  ConsolidatedEntitiesAxis to a second consolidation-qualifier axis (same
  `consolidation` slot); both-axes-differing-members → excluded under new
  self-describing `consolidation_conflict` category. Two-way door
  (whitelist addition), agent-decided, live-verified INTC re-sweep. This is
  the exclude→count→verify-semantics→promote flow working as designed.

## Task 1 — Producer: vintage/unknown-axis exclusion with count (kill the silent drop)

- Description: rework `_dimension_signature`'s axis loop so a fact carrying
  any `dim_` axis that is neither in `_DIMENSIONAL_REVENUE_AXIS_LOCAL_NAMES`
  nor the ConsolidationItems carve-out is EXCLUDED from the pack's primary
  facts and counted by category — `srt:RestatementAxis` (any member) as the
  named vintage-exclusion category, everything else as unknown-axis — in a
  machine-readable pack accounting channel (match the existing pack
  accounting schema; channel choice pinned by the test). Fix the stale
  "three axis local names" docstring (:1845). The 3-key signature shape and
  all existing signature tests stay byte-identical.
- Module: investing-toolkit/skills/data-markets (sec_edgar_client)
- Files touched: investing-toolkit/skills/data-markets/scripts/sec_edgar_client.py,
  investing-toolkit/tests/data/test_sec_edgar_dimensional.py
- Context paths:
  - investing-toolkit/skills/data-markets/scripts/sec_edgar_client.py (:1829-1834 whitelist, :1840 consolidation axis, :2053-2083 `_dimension_signature`, :2079-2082 silent fall-through)
  - investing-toolkit/tests/data/test_sec_edgar_dimensional.py (:605-659 `test_build_fact_full_signature`, :680-709 subsegments test — conventions + must stay green)
  - docs/loom/specs/2026-07-19-jnj-restatement-axis-signature.md (§Smallest End State 1-2)
- Acceptance:
  - RED: new parametrized test — a fact row carrying
    `dim_srt_RestatementAxis` (member
    RevisionOfPriorPeriodReclassificationAdjustmentMember) is NOT emitted
    as a primary fact and the pack accounting counts one vintage exclusion;
    a fact carrying an unrecognized axis (e.g. a synthetic
    `dim_us-gaap_SomeFutureAxis`) is likewise excluded-with-count; a
    whitelist-only fact is emitted unchanged. Fails today because both
    collapse silently onto the default signature.
  - GREEN: test passes; existing signature-shape tests untouched and green.
- Dependencies: none
- Independent: false
- Brief item covered: "Producer — recognized-vintage exclusion + no more
  silent drops" + "NO fourth signature field" (Smallest End State 1-2)

## Task 2 — Consumer: recast annotation flows into feed coverage_flags

- Description: surface the pack's vintage-exclusion accounting as a
  memo-visible coverage flag — when the consumed pack reports ≥1
  vintage-category exclusion, `build_quarterly_series` (or its
  coverage-flag wiring seam) emits a new self-describing coverage_flag
  entry ("period recast — prior-published figures differ" semantics; exact
  type string is this task's code decision, pinned by test) alongside the
  existing `no_quarterly_coverage`-style flags; `build_quarterly_memo_feed`
  passes it through verbatim (verify its validation accepts the new type —
  adjust only if a type allowlist exists). Unknown-axis exclusions do NOT
  emit the recast flag (they are not a vintage statement) — they stay
  pack-level accounting only.
- Module: investing-toolkit/skills/analysis-kpi (kpi_xbrl + feed seam)
- Files touched: investing-toolkit/skills/analysis-kpi/scripts/kpi_xbrl.py,
  investing-toolkit/skills/analysis-kpi/scripts/kpi_memo_feed.py,
  investing-toolkit/tests/analysis/test_kpi_xbrl.py,
  investing-toolkit/tests/analysis/test_kpi_memo_feed.py
- Context paths:
  - investing-toolkit/skills/analysis-kpi/scripts/kpi_xbrl.py (:1459-1471 coverage-flag wiring in `build_series_with_break`, :1555-1645 `build_quarterly_series`)
  - investing-toolkit/skills/analysis-kpi/scripts/kpi_memo_feed.py (:216+ `build_quarterly_memo_feed` passthrough/validation)
  - investing-toolkit/tests/analysis/test_kpi_memo_feed.py (envelope tests + factory helpers)
- Acceptance:
  - RED: new test — a quarterly series built from a pack carrying one
    vintage exclusion emits the recast coverage_flag with the affected
    accession/period context, and the flag survives the feed passthrough;
    a pack with zero exclusions emits no such flag.
  - GREEN: tests pass; existing coverage_flags tests green.
- Dependencies: Task 1 completes first (consumes the pack channel T1 defines)
- Independent: false
- Brief item covered: "Provenance reaches the memo: the vintage-exclusion
  fact flows into the feed's coverage_flags channel ... memo annotates
  'period recast — prior-published figures differ' as metadata beside,
  never inside, the series" (Smallest End State 1)

## Task 3 — Consumer: per-signature refusal granularity (no whole-ticker abort)

- Description: wrap the per-group `resolve_binding` call in
  `build_quarterly_series`'s loop so a genuine intra-filing-ambiguity
  ValueError (from `_reduce_window_group`) is caught per signature group,
  recorded as a non-fatal per-signature refusal entry (ride the existing
  gaps/coverage_flags machinery; verbatim exception text preserved in the
  entry), and the loop CONTINUES — one poisoned signature yields one
  refusal entry, all sibling signatures still emit. Other exception types
  still propagate (no blanket except).
- Module: investing-toolkit/skills/analysis-kpi (kpi_xbrl)
- Files touched: investing-toolkit/skills/analysis-kpi/scripts/kpi_xbrl.py,
  investing-toolkit/tests/analysis/test_kpi_xbrl.py
- Context paths:
  - investing-toolkit/skills/analysis-kpi/scripts/kpi_xbrl.py (:1595-1626 per-group loop + `resolve_binding` call :1619, :609-627 `_reduce_window_group` ValueError)
  - investing-toolkit/tests/analysis/test_kpi_xbrl.py (existing quarterly-series tests + factory helpers)
- Acceptance:
  - RED: new test — a synthetic pack where ONE signature carries a genuine
    intra-filing two-distinct-values ambiguity and a SIBLING signature is
    clean: today `build_quarterly_series` raises and nothing emits; after
    the fix it returns the sibling's series plus one refusal entry carrying
    the verbatim ambiguity reason.
  - GREEN: test passes; the existing direct `resolve_binding` ambiguity
    raise test stays green (the raise itself is unchanged — only the loop
    catches it).
- Dependencies: Task 2 completes first (same files; refusal entries ride
  the channel shapes T2 settles)
- Independent: false
- Brief item covered: "Consumer — per-signature refusal granularity ...
  the loop CONTINUES to the next signature" (Smallest End State 3)

## Task 4 — E2E seam test: restatement pack through the chain

- Description: extend the e2e seam test with a JNJ-shaped synthetic fixture
  (factory-constructed per existing conventions, `_provenance` declares
  synthetic + models JNJ acc 0000200406-25-000209's Shockwave ±20M
  reclassification pair): assert end-to-end that the restatement pair is
  excluded at the pack layer, the real fact binds cleanly (no false
  ambiguity), the recast coverage_flag reaches the feed, and — in a second
  fixture variant with a genuine ambiguity — the refused signature yields
  a refusal entry while siblings emit. Test-only task.
- Module: investing-toolkit/tests (analysis e2e)
- Files touched: investing-toolkit/tests/analysis/test_kpi_xbrl_quarterly_e2e.py,
  investing-toolkit/tests/analysis/fixtures/ (new fixture JSON, single-level)
- Context paths:
  - investing-toolkit/tests/analysis/test_kpi_xbrl_quarterly_e2e.py (existing chain tests + dep stubbing :121-140 region)
  - investing-toolkit/tests/analysis/fixtures/ (existing `_provenance` conventions)
- Acceptance:
  - RED: written against the shipped T1-T3 contract; fails on pre-arc code
    (the restatement pair would collapse → ambiguity raise aborts the
    chain). Runs OFFLINE.
  - GREEN: e2e tests pass; full suite green.
- Dependencies: Task 3 completes first
- Independent: true
- Brief item covered: "Acceptance (a) unit/synthetic chain coverage"
  (Smallest End State 4a)

## Task 5 — CHANGELOG + version bump 2.25.0

- Description: bump investing-toolkit to 2.25.0 (plugin.json ×2 mirrors via
  the sync script when the drift guard fires) + CHANGELOG entry describing
  the vintage-axis exclusion, unknown-axis fail-closed accounting, recast
  coverage flag, and per-signature refusal granularity — every mechanism
  token transcribed from the shipped code (grep-pinned), no overclaim, no
  claims about the live JNJ validation that runs at finishing.
- Module: investing-toolkit (manifests + CHANGELOG)
- Files touched: investing-toolkit/CHANGELOG.md,
  investing-toolkit/.claude-plugin/plugin.json,
  investing-toolkit/.codex-plugin/plugin.json
- Context paths:
  - investing-toolkit/CHANGELOG.md (:8 v2.24.0 entry style)
  - docs/loom/memory/prose-contract-mechanism-transcribes-from-code.md (incl. the comments-lie refinement — transcribe from behavior/tests, not comments)
- Acceptance:
  - RED: version check reads 2.24.0 ×2 before; after, both mirrors read
    2.25.0 and the CHANGELOG head entry's mechanism tokens each grep-match
    shipped code/test files.
  - GREEN: checks pass; no backfill.
- Dependencies: Task 3 completes first (describes shipped behavior)
- Independent: true
- Brief item covered: "Version: investing-toolkit → 2.25.0" (Smallest End
  State version line)
