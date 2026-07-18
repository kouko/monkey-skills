# Plan: 52/53-week filer 支援 — week-based duration lane

Source brief: docs/loom/specs/2026-07-18-52-53-week-filer-support.md
Total tasks: 8
Critical-path depth: 5 (T1 → T3 → T4 → T5 → {T6, T7, T8})
Execution order: parallel-where-possible (final wave T6/T7/T8)
Plan-document-reviewer verdict: PASS (2026-07-18, 14/14)

## Notes

- **Change-folder detection**: the only non-archived `docs/loom/<change-id>/`
  folder (`2026-07-12-us-sec-primary-source-layer/`) belongs to the already
  SHIPPED US SEC arc (pending an archiving ruling) — binding to it would be a
  wrong-bind, so change-folder input is N/A; this plan derives from the
  brainstorming brief only.
- **Architecture ruling from recon** (satisfies brief Smallest End State #1):
  the pipeline is producer-emits/consumer-trusts over pack JSON. The shared
  week-band primitive lives as PURE functions/constants in
  `sec_edgar_client.py`; `kpi_xbrl.py` consumes the emitted fields and, where
  it needs the mapping itself, lazy-imports the pure function via the existing
  precedent at `kpi_xbrl.py:1140-1143` (sys.path insert + function-level
  import; tests stub `requests`/`edgar` in `sys.modules` per the
  `stub_data_layer_deps` fixture pattern). Exactly ONE table of week bands
  exists, in one file — the edgartools two-path-desync lesson is the reason
  this is a hard constraint.
- **Duration arithmetic facts** (from live recon, plan-binding): 12wk=83–84d
  rounds to 3 months → already passes Gate C; the killed spans are
  36wk≈251d→8, 16wk≈111d→4, 17wk≈119d→4, 24wk≈167d→5. Gate P kills COST
  Q3-filing facts by boundary distance (20d > ±10d tolerance).
- **Exact class strings** (per
  docs/loom/memory/prose-contract-mechanism-transcribes-from-code.md): the
  week-lane `duration_class` strings are decided in T3's code and then
  TRANSCRIBED into T5/T7/T8 prose — the placeholders here (e.g. "36wk-YTD")
  are directional, the shipped code is the contract.
- **Live-ticker validation** (brief acceptance #8, COST real recompute +
  AAPL/NVDA regression) is a finishing-phase verification step (network),
  not an SDD task — run after suite-green, before review, mirroring the
  2.23.0 arc's live test.
- **Fixture red lines**: machine-captured fixtures with `_provenance`; never
  hand-type XBRL values. PYTHONDONTWRITEBYTECODE=1; never `git add -A`.
- **Post-PASS amendment (re-review skipped, additive + schema-safe)**: per
  reviewer note, Tasks 2 and 3 flipped to `Independent: true` — files
  disjoint (sec_edgar_client.py+test vs kpi_xbrl.py+test), both depend only
  on Task 1's shipped primitive, no shared symbol beyond it. Also Task 4's
  Description clarified for the class-lane-precedence kickoff decision (FY
  anchor may be month-classed) — same RED/GREEN, same fields. All required
  fields and DAG structure unchanged; Checks 13/14 satisfied (disjointness
  verified above).
- **Reviewer note carried forward**: Smallest End State 8's LIVE half (COST
  real recompute + AAPL/NVDA live regression) is a finishing-phase step —
  SDD suite-green alone does not close it; the orchestrator runs it before
  review, per Notes above.
- Kickoff decision: one-way-door sweep → no NEW one-way doors; the three
  candidates (derived-Q4 inclusion policy, XBRL-lane trust ruling,
  disclosure + supplementary-YoY presentation) are all pre-ratified user
  decisions (2.23.0 arc rulings + this brief's sign-off 2026-07-18).
- Kickoff decision: class-lane precedence → the month map KEEPS precedence
  in `classify_fact_period` (52wk=364d and 53wk=371d both round to 12 →
  "12mo-FY"; 12/13wk quarters → "3mo"); the week lane adds classes ONLY for
  month-map misses (16wk≈111d→4, 17wk≈119d→4, 36wk≈251-252d→8, 24wk at
  167d→5; note 168d rounds to 6 and already passes as "6mo-YTD").
  Week-count honesty rides the per-point `duration_weeks` field on EVERY
  fact, independent of which lane classified it. Q4 derivation arithmetic
  uses `duration_weeks` (FY_weeks − YTD_weeks), tolerating a month-classed
  FY anchor.
- Kickoff decision: week-lane `duration_class` string morphology → follow
  the shipped month-lane morphology ("9mo-YTD"/"12mo-FY") → directionally
  "16wk"/"17wk"/"24wk-YTD"/"36wk-YTD"; exact set is T3's code decision,
  pinned by its tests then transcribed downstream.
- Kickoff decision: week-lane boundary tolerance (Gate P) → tight (≈±2d):
  week filers' period ends sit at exact weekly offsets from the per-filing
  dei FYE; widen only on an observed counterexample, never toward the month
  lane's ±10d.

## Task 1 — Shared week-band primitive + `duration_weeks` emission (producer)

- Description: add the single shared week-band primitive to
  `sec_edgar_client.py` as pure module-level code — a positive allowlist of
  week-based duration bands (≈12/13wk 83–91d quarter-length; ≈16/17wk
  111–119d week-Q4-length; ≈24/26wk 167–182d H1; ≈36/39wk 251–273d
  YTD-through-Q3; ≈52/53wk 363–371d FY), a pure span→week-count helper, and a
  pure span→week-lane-class mapping; emit per-fact `duration_weeks` alongside
  `duration_months` in `_build_dimensional_revenue_fact`. Out-of-band spans
  stay unclassified (fail-closed unchanged).
- Module: investing-toolkit/skills/data-markets (sec_edgar_client)
- Files touched: investing-toolkit/skills/data-markets/scripts/sec_edgar_client.py,
  investing-toolkit/tests/data/test_sec_edgar_dimensional.py
- Context paths:
  - investing-toolkit/skills/data-markets/scripts/sec_edgar_client.py (:2117-2158 `_duration_months`, :2526 attach site)
  - investing-toolkit/tests/data/test_sec_edgar_dimensional.py (:1085-1114 `test_duration_months_pins_realistic_span_bands` — extend, don't duplicate)
  - docs/loom/specs/2026-07-18-52-53-week-filer-support.md (§Smallest End State 1–2)
- Acceptance:
  - RED: new test asserting a 251d-span fact emits `duration_weeks == 36` and
    the pure mapper classifies 251d→YTD-through-Q3 band, 111d→week-Q4 band,
    365d(month-lane)→no week-lane claim; fails because neither field nor
    primitive exists.
  - GREEN: test passes; existing `_duration_months` tests untouched and green.
- External surfaces: XBRL duration-context semantics (period_start/period_end
  ISO dates) — stdlib `date` arithmetic only; no new third-party dependency.
- Dependencies: none
- Independent: false
- Brief item covered: "Positive allowlist of week-based duration bands"
  (Smallest End State 2) + "One shared week/month period-classification
  primitive" (Smallest End State 1, producer half)

## Task 2 — Week-aware fiscal boundary labeling (Gate P)

- Description: extend `_derive_fiscal_label`'s sub-annual path so week-based
  filers' period ends classify to fiscal quarters via a positive allowlist of
  week-offset boundaries from the per-filing fiscal-year-end (per-filing dei
  calendar, never cached), with a tight day tolerance, WITHOUT widening the
  month lane's `FISCAL_BOUNDARY_TOLERANCE_DAYS = 10`; non-matching period
  ends still raise `UnclassifiablePeriodError` (fail-closed unchanged).
- Module: investing-toolkit/skills/data-markets (sec_edgar_client)
- Files touched: investing-toolkit/skills/data-markets/scripts/sec_edgar_client.py,
  investing-toolkit/tests/data/test_sec_edgar_dimensional.py
- Context paths:
  - investing-toolkit/skills/data-markets/scripts/sec_edgar_client.py (:2166 tolerance, :2272-2350 `_derive_fiscal_label`, :2336-2347 boundaries+raise)
  - investing-toolkit/tests/data/test_sec_edgar_dimensional.py (:2173, :2300 existing tolerance/unclassifiable tests)
  - docs/loom/memory/fiscal-year-derive-per-fact-against-filing-calendar.md
- Acceptance:
  - RED: new test — COST-shaped case (fiscal year end 2026-08-30, period_end
    2026-05-10, i.e. 16 weeks before FYE) returns (FY2026, "Q3") instead of
    raising `UnclassifiablePeriodError`; a period_end far from every month
    AND week boundary still raises.
  - GREEN: test passes; existing month-lane boundary/tolerance tests all green
    (month lane behavior byte-identical).
- External surfaces: dei fiscal-calendar fields (`CurrentFiscalYearEndDate`)
  — existing parsing reused; no new dependency.
- Dependencies: Task 1 completes first (same-file serialization; boundary
  offsets derive from the same week-band table)
- Independent: true
- Brief item covered: "Gate P rework: ... boundary matching must become
  week-aware for the week lane instead of widening the ±10d month tolerance"
  (Smallest End State 3)

## Task 3 — Consumer week-lane duration classes (Gate C)

- Description: extend `classify_fact_period` in `kpi_xbrl.py` to accept
  week-lane facts: when `duration_months` maps to no month-lane class, use
  the fact's emitted `duration_weeks` against the SHARED primitive
  (lazy-imported from `sec_edgar_client` per the `kpi_xbrl.py:1140-1143`
  precedent — no second band table) to yield week-encoded `duration_class`
  strings (directionally `12wk`, `16wk`/`17wk`, `24wk-YTD`, `36wk-YTD`,
  `52wk-FY`/`53wk-FY` — exact strings are this task's code decision); facts
  with neither lane still raise (fail-closed unchanged).
- Module: investing-toolkit/skills/analysis-kpi (kpi_xbrl)
- Files touched: investing-toolkit/skills/analysis-kpi/scripts/kpi_xbrl.py,
  investing-toolkit/tests/analysis/test_kpi_xbrl.py
- Context paths:
  - investing-toolkit/skills/analysis-kpi/scripts/kpi_xbrl.py (:155 month map, :261-304 `classify_fact_period`, :1140-1143 lazy-import precedent)
  - investing-toolkit/tests/analysis/test_kpi_xbrl.py (:782 `test_classify_period_type`; `stub_data_layer_deps` fixture pattern)
- Acceptance:
  - RED: new test — a fact with `duration_months=8`, `duration_weeks=36`
    classifies to the week-lane YTD-through-Q3 class instead of raising; a
    fact with no `duration_weeks` and month ∉ {3,6,9,12} still raises.
  - GREEN: test passes; existing classification tests green.
- External surfaces: none (pure logic; lazy import stubbed in tests).
- Dependencies: Task 1 completes first (consumes `duration_weeks` +
  lazy-imports the shared primitive)
- Independent: true
- Brief item covered: "One shared week/month period-classification primitive
  — both ... Gate P ... and Gate C ... decide through it" (Smallest End
  State 1, consumer half) + week-band allowlist (Smallest End State 2)

## Task 4 — Q4 derivation on the week lane

- Description: extend `derive_q4_points` (and its gap accounting) so a
  week-lane-eligible FY point (month-classed "12mo-FY" carrying
  `duration_weeks` 52/53 — see Notes class-lane precedence — or week-classed)
  minus the matching week-lane YTD point (36wk-YTD class) mints
  a derived Q4 with `duration_weeks = FY_weeks − YTD_weeks` (16 or 17) and
  the 2.23.0 derived-tagging rules (verbatim dqc transcription) unchanged;
  when the week-lane YTD anchor is absent, `q4_source_missing` refusal fires
  exactly as today (fail-closed unchanged).
- Module: investing-toolkit/skills/analysis-kpi (kpi_xbrl)
- Files touched: investing-toolkit/skills/analysis-kpi/scripts/kpi_xbrl.py,
  investing-toolkit/tests/analysis/test_kpi_xbrl.py
- Context paths:
  - investing-toolkit/skills/analysis-kpi/scripts/kpi_xbrl.py (:899-930 `_q4_candidate_gap`, :933-975 `_mint_derived_q4_point`, :978-1044 `derive_q4_points`, :1031/:1034 class lookups)
  - investing-toolkit/tests/analysis/test_kpi_xbrl.py (:1434 `test_q4_derive_guarded_segregated`, :1619 provenance schema test)
- Acceptance:
  - RED: new test — week-lane fixture (53wk FY + 36wk YTD, full dimensional
    signatures) mints a derived Q4 point with `duration_weeks == 17`,
    `derived: True`, dqc transcription intact; sibling case without the YTD
    anchor yields `q4_source_missing`.
  - GREEN: test passes; existing month-lane Q4 derivation tests green.
- Dependencies: Task 3 completes first (same file; consumes week-lane class
  strings)
- Independent: false
- Brief item covered: "Q4 derivation works on the week lane: FY − 36wk-YTD,
  same fail-closed q4_source_missing refusal" (Smallest End State 4)

## Task 5 — Feed carries week counts + supplementary week-normalized YoY

- Description: propagate per-point `duration_weeks` through the quarterly
  series payload into the 1.1 feed, and, when a point's YoY comparator (same
  KPI signature, same fiscal quarter, prior fiscal year) has a DIFFERENT week
  count, attach a supplementary week-normalized YoY growth field
  ((value/weeks) vs (prior value/prior weeks) − 1) computed in code — the
  as-reported value stays the primary number; `build_quarterly_memo_feed`
  validation accepts the new fields; bump/keep
  `MEMO_FEED_QUARTERLY_SCHEMA_VERSION` per the file's existing
  schema-versioning convention (additive-field ruling is this task's code
  decision, made visible in the test).
- Module: investing-toolkit/skills/analysis-kpi (kpi_xbrl + kpi_memo_feed seam)
- Files touched: investing-toolkit/skills/analysis-kpi/scripts/kpi_xbrl.py,
  investing-toolkit/skills/analysis-kpi/scripts/kpi_memo_feed.py,
  investing-toolkit/tests/analysis/test_kpi_memo_feed.py,
  investing-toolkit/tests/analysis/test_kpi_xbrl.py
- Context paths:
  - investing-toolkit/skills/analysis-kpi/scripts/kpi_memo_feed.py (:105 schema version, :216-257 `build_quarterly_memo_feed`)
  - investing-toolkit/tests/analysis/test_kpi_memo_feed.py (:390-478 factory helpers, :481/:512/:570 quarterly envelope tests)
  - docs/loom/specs/2026-07-18-52-53-week-filer-support.md (§Smallest End State 5, 7 — user-ratified supplementary column)
- Acceptance:
  - RED: new test — a quarterly feed built from points where a 16wk Q4
    compares against a prior-year 17wk Q4 carries `duration_weeks` on both
    points and the supplementary normalized-YoY field on the current point;
    equal-week-count comparators carry NO supplementary field; as-reported
    `value` unchanged.
  - GREEN: test passes; tier-① `build_memo_feed` byte-identical; existing
    quarterly-envelope tests green.
- Dependencies: Task 4 completes first (same file kpi_xbrl.py; derived-Q4
  points must carry week counts before the feed can)
- Independent: false
- Brief item covered: "Per-point week-count labeling in the feed" (Smallest
  End State 5) + "Supplementary week-normalized YoY column (user-ratified)"
  (Smallest End State 7)

## Task 6 — Week-lane e2e seam test + month-lane regression pin

- Description: extend the pack→series→feed seam test with a machine-captured
  COST-shaped week-lane fixture (12wk quarters, 36wk YTD, 52/53wk FY, full
  dimensional signatures, `_provenance` documenting the capture recipe)
  asserting the whole chain: Gate P labels, week-lane classes, derived Q4
  with week count, feed fields incl. supplementary YoY; plus an explicit
  regression assertion that the existing month-lane fixture's chain output is
  unchanged. Test-only task — no production code.
- Module: investing-toolkit/tests (analysis e2e)
- Files touched: investing-toolkit/tests/analysis/test_kpi_xbrl_quarterly_e2e.py,
  investing-toolkit/tests/analysis/fixtures/ (new week-lane fixture JSON)
- Context paths:
  - investing-toolkit/tests/analysis/test_kpi_xbrl_quarterly_e2e.py (:74-93 dep stubbing, :142 existing chain test)
  - investing-toolkit/tests/analysis/fixtures/ (existing `xbrl_*_factpack.json` `_provenance` convention)
- Acceptance:
  - RED: the new e2e test fails if run before Tasks 1–5 land (week-lane chain
    unclassifiable); written against the shipped field/class names.
  - GREEN: e2e test passes; full suite green
    (`PYTHONDONTWRITEBYTECODE=1 uv run --with pytest --with 'pyyaml>=6.0'
    pytest investing-toolkit/tests/ -m "not network" -q`).
- External surfaces: fixture captured from SEC EDGAR via the pinned
  `--with 'requests==2.33.1' --with 'edgartools==5.42.0'` recipe (offline at
  test time; recipe recorded in `_provenance`).
- Dependencies: Task 5 completes first
- Independent: true
- Brief item covered: "Acceptance: live COST feed produces the quarterly
  series + derived Q4 ... AAPL/NVDA month-lane output byte-stable
  (regression); suite green" (Smallest End State 8, offline half)

## Task 7 — Protocol: unequal-quarter-length disclosure + supplementary YoY rule (domain-teams)

- Description: add to the Operating-KPI block of the investing-team memo
  protocol (and its template/appendix echoes) the unequal-quarter-length
  disclosure rule — whenever the feed carries week-lane points, the memo MUST
  label week counts per period, state the Walmart-style "which figures are
  affected" disclosure, and render the supplementary week-normalized YoY
  (from the feed field — the memo writer transcribes, never computes) — with
  every mechanism name transcribed verbatim from the Task 3/5 shipped schema
  strings; bump domain-teams to 5.10.0 (plugin.json ×2 mirrors + CHANGELOG).
- Module: domain-teams (investing-team protocol + plugin manifests)
- Files touched: domain-teams/skills/investing-team/protocols/deep-equity-research-memo.md,
  domain-teams/CHANGELOG.md, domain-teams/.claude-plugin/plugin.json,
  domain-teams/.codex-plugin/plugin.json
- Context paths:
  - domain-teams/skills/investing-team/protocols/deep-equity-research-memo.md (:135-200 Operating-KPI block; :162-191 trend-table shape, disclosure slots after :184; :387-399 template; :447-451 appendix)
  - docs/loom/memory/prose-contract-mechanism-transcribes-from-code.md
  - investing-toolkit/skills/analysis-kpi/scripts/kpi_memo_feed.py (shipped schema after Task 5 — transcription source)
- Acceptance:
  - RED: grep-level check fails before the edit — no week-count/disclosure
    tokens in the protocol; after the edit, grep pins the code-true tokens
    (the exact `duration_class` strings and feed field names from Tasks 3/5)
    in block + template + appendix, and plugin.json ×2 read 5.10.0.
  - GREEN: greps pass; CHANGELOG entry describes disclosure rule without
    inventing mechanisms (no reconciliation/WITHHELD vocabulary).
- Dependencies: Task 5 completes first (doc-mirrors-code: schema strings must
  be shipped before transcription)
- Independent: true
- Brief item covered: "Protocol disclosure rule ... wording transcribed from
  the shipped schema fields" (Smallest End State 6) + domain-teams → 5.10.0

## Task 8 — investing-toolkit docs + version bump 2.24.0

- Description: bump investing-toolkit to 2.24.0 (plugin.json ×2 mirrors +
  CHANGELOG entry describing the week-based duration lane: shared primitive,
  Gate P/C week lanes, week-count labels, supplementary normalized YoY —
  wording transcribed from shipped code, no overclaim), and update
  `report-equity-memo/SKILL.md` Phase 3.5 prose where it describes quarterly
  coverage so week-based filers are no longer described as
  refusal-terminal (brief Axis 5: refusal stays the fallback, no longer the
  expected COST outcome).
- Module: investing-toolkit (manifests + docs)
- Files touched: investing-toolkit/CHANGELOG.md,
  investing-toolkit/.claude-plugin/plugin.json,
  investing-toolkit/.codex-plugin/plugin.json,
  investing-toolkit/skills/report-equity-memo/SKILL.md
- Context paths:
  - investing-toolkit/CHANGELOG.md (:8 current 2.23.0 entry style)
  - investing-toolkit/skills/report-equity-memo/SKILL.md (:356+ Phase 3.5)
  - docs/loom/specs/2026-07-18-52-53-week-filer-support.md (§What Becomes Obsolete)
- Acceptance:
  - RED: version check fails before the edit (plugin.json ×2 still 2.23.0);
    after, `python3 -c` version read returns 2.24.0 on both mirrors and the
    CHANGELOG's new entry's mechanism tokens grep-match shipped code strings.
  - GREEN: checks pass; no CHANGELOG backfill of pre-2.22.0 gaps.
- Dependencies: Task 5 completes first (CHANGELOG describes shipped behavior)
- Independent: true
- Brief item covered: "Version bumps: investing-toolkit → 2.24.0" (Smallest
  End State version line) + "What Becomes Obsolete: ... protocol wording
  implying COST-class refusal is the terminal state — update in the same
  change"
