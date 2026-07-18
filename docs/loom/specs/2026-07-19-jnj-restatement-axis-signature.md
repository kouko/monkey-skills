# Brief — JNJ RestatementAxis 修復：vintage-axis exclusion + per-signature refusal granularity

Date: 2026-07-19 · Stage: brainstorming output (loom-code Stage 1) · Consumer: `writing-plans`

## Design-side on-ramp

Axis 0 negative guard: bug fix on the shipped quarterly lane — silently
skipped per the family reception table.

## Problem

The 12-ticker live sweep (2026-07-19) found JNJ completely locked out of the
quarterly KPI lane: `_dimension_signature` silently DROPS `srt:RestatementAxis`,
so a prior-period reclassification adjustment pair (acc 0000200406-25-000209,
Shockwave ±20M, US↔NonUS) collapses onto the real quarter fact's signature →
`resolve_binding` fires its intra-filing-ambiguity fail-loud (correct reflex,
FALSE ambiguity) → and the raise propagates out of `build_quarterly_series`'s
per-group loop, aborting the ENTIRE ticker (feed exits on empty input). The
job: any filer tagging restatement/reclassification vintage axes gets a
normal quarterly feed, with the adjustment facts excluded from primary KPI
binding on taxonomy-grounded semantics — and no single poisoned signature
ever zeroes a whole ticker again.

## Users

- **kouko**, running `/report-equity-memo` on large-cap US filers (JNJ today;
  any filer tagging RestatementAxis pairs); a silently-conflated superseded
  vintage would be worse than the current honest lock-out.
- **Weak-model memo writers** consuming the feed — exclusion must surface as
  machine-readable provenance (flag/gap), never silent.

## Smallest End State

1. **Producer — recognized-vintage exclusion + no more silent drops**
   (`sec_edgar_client.py`): facts carrying `srt:RestatementAxis` (any member)
   are EXCLUDED from the pack's primary dimensional facts and counted in a
   machine-readable channel (ride the existing `selection_gaps`-style
   accounting or a sibling counter — implementer reads the existing
   channels and picks the fitting one, decision visible in tests).
   Simultaneously, the silent-drop else-branch dies: a fact carrying ANY
   unrecognized `dim_` axis (neither breakdown whitelist, nor
   ConsolidationItems, nor the vintage allowlist) is also
   excluded-with-count instead of collapsing onto the default signature —
   fail-closed toward exclusion, never toward collision
   (docs/loom/memory/shared-classifier-over-open-dialects-needs-allowlist.md:
   the sweep proves only RestatementAxis COLLIDED, not that no sibling
   exists; unfalsified ≠ proven). **Provenance reaches the memo**: the
   vintage-exclusion fact flows into the feed's `coverage_flags` channel
   (whose verbatim-disclosure protocol rule already exists generically),
   so the memo annotates "period recast — prior-published figures differ"
   as metadata beside, never inside, the series — matching vendor
   practice (second research round, 2026-07-19: Capital IQ/Compustat
   primary product = latest-restated series; ASC 280 / 企業会計基準第17号
   recast-for-comparability norm; PIT is a backtesting-only concern).
2. **NO fourth signature field**: signature stays `{concept, dimensions,
   consolidation}` — the exact-3-key pinned shape
   (test_kpi_xbrl.py:2625-2629) and all `_fact_matches`/`_fact_signature_key`
   call sites stay untouched. Grounding: XBRL US guidance — the default
   (axis-absent) member IS the restated current value; axis-qualified facts
   are superseded vintages/one-time deltas, not parallel bindable series.
3. **Consumer — per-signature refusal granularity** (`kpi_xbrl.py`
   `build_quarterly_series` loop ~:1595-1626): wrap the per-group
   `resolve_binding` call so a genuine intra-filing-ambiguity ValueError
   becomes a per-signature refusal entry on the existing non-fatal
   channel (`coverage_flags` sibling type or `gaps`-style entry with the
   verbatim reason), and the loop CONTINUES to the next signature. Empty
   result for one signature, full results for the rest. Defense-in-depth:
   with fix 1 the JNJ collision disappears, so this path is pinned by a
   synthetic true-ambiguity fixture.
4. **Acceptance**: (a) unit: RestatementAxis fixture fact excluded with
   count; unknown-axis fact excluded with count; synthetic true-ambiguity
   pack → one refused signature entry + siblings still emitted; (b) live:
   JNJ chain end-to-end → feed TRUSTED with real derived Q4 points (the
   sweep's exact refusal is the RED baseline) AND the recast annotation
   present in coverage_flags; 12-ticker regression anchors unchanged
   (suite + AAPL/NVDA/COST spot values); (c) suite green.

Version: investing-toolkit → 2.25.0. domain-teams untouched (coverage_flags
verbatim-disclosure protocol rule already covers new flag types
generically — verify at plan time, no protocol edit expected).

## Current State Evidence

- **Forward**: `_build_dimensional_revenue_fact` → `_dimension_signature`
  (sec_edgar_client.py:2053-2083; whitelist `_DIMENSIONAL_REVENUE_AXIS_LOCAL_NAMES`
  :1829-1834, consolidation carve-out :2079, silent fall-through :2079-2082
  with NO else) → pack facts → `_fact_matches` (kpi_xbrl.py:416-432) /
  `_fact_signature_key` (:1483-1494) → `build_quarterly_series` per-group
  loop (:1595-1626, `resolve_binding` at :1619, NO try/except).
- **Reverse (SSOT)**: investing-toolkit owns the data layer; no domain-teams
  surface in scope. BACKLOG §"JNJ RestatementAxis signature blind spot"
  (docs/loom/BACKLOG.md:72-89) is the SSOT tracking entry — consumed by this
  arc.
- **Error**: intra-filing multi-value raise `_reduce_window_group`
  (kpi_xbrl.py:609-627, ValueError :621-627); live refusal text captured in
  scratchpad `sweep_JNJ_series.err`; downstream `kpi_memo_feed` fails on
  empty input (sweep_JNJ_feed.err).
- **Data**: JNJ acc 0000200406-25-000209 — Shockwave reclassification pair
  +20M US / −20M NonUS carrying `srt:RestatementAxis` (member per probe:
  RevisionOfPriorPeriodReclassificationAdjustmentMember; re-verify at
  implementation, probe script scratchpad `jnj_probe.py`). JNJ pack layer
  otherwise perfect: 6,462/6,462 facts dual-lane classified, zero
  unclassifiable. Only 1 of 12 sweep tickers collided.
- **Boundary**: existing non-fatal per-signature channels the fix rides:
  `coverage_flags` via `_dimension_quarterly_absence_flags` (wired
  kpi_xbrl.py:1459-1471), `gaps` surfaced per-entry (:1641),
  `selection_gaps` at pack layer. Signature-shape pins that must NOT break:
  test_kpi_xbrl.py:2625-2629 (exact 3-key), test_sec_edgar_dimensional.py
  :605-659/:680-709 (consolidation precedent tests).

## Alternatives Considered (Axis 4 — research-grounded)

1. **Carry RestatementAxis INTO the signature (4th field / new dimension)** —
   adjustment facts become their own bindable series. Rejected: taxonomy
   semantics say axis-qualified facts are superseded vintages / one-time
   deltas ([EN] XBRL US "Reporting Restated Values in the Face of the
   Financials", https://xbrl.us/guidance/reporting-restated-values-in-the-face-of-the-financials/ —
   "it is assumed that the default value is the restated amount");
   presenting a ±delta as a period KPI value is the fabrication risk in
   reverse. Also largest blast radius (breaks the 3-key pinned shape, all
   matcher call sites). Reversal trigger: a future originally-reported-vs-
   restated delta-analysis feature makes axis-carrying an opt-in lane.
2. **Filter-and-exclude with provenance (CHOSEN)** — matches shipped-consumer
   practice: edgartools' ergonomic default is undimensioned/opt-in
   dimensional querying ([EN] https://edgartools.readthedocs.io/en/latest/xbrl-querying/ );
   DQC has no direct RestatementAxis rule (insufficient data — honest) but
   DQC_0233's spirit (don't smuggle adjustments into primary series)
   aligns ([EN] dqc_us_rules releases).
3. **Granularity-only fix (keep the collision, just don't abort the
   ticker)** — rejected as sole fix: the collided signature would still
   refuse (JNJ's MedTech series still missing) and the false ambiguity
   remains a lie in the gap record. Kept as fix 3 (defense-in-depth for
   GENUINE ambiguity).
- [JA] finding: EDINET uses its own 遡及処理 dimension, not
  srt:RestatementAxis — this fix is US-GAAP-specific by construction; JP
  lane unaffected.

Second round — investment-practice layer (user-requested, 2026-07-19):

4. **Vendor canonical series = latest-restated**: Capital IQ "Latest
   Financials" delivers the latest instance incl. restatements as the
   primary series; Compustat Point-In-Time is a SEPARATE
   backtesting-only product ([EN]
   S&P/Capital IQ methodology docs; Portfolio123 backtesting-data
   methodology frames look-ahead bias as quant-backtest-specific).
5. **Segment recast is mandatory-retrospective in both jurisdictions**:
   ASC 280 requires prior-period recast for comparability (ASU 2023-07
   deliberately renamed it "recast" vs error-correction "restate") —
   [EN] Deloitte DART §4.9; Japan's 企業会計基準第17号 mirrors it —
   [JA] ASBJ 基準第17号 + EY Japan commentary. The recast vintage is
   definitionally the comparable one. EN/JA agree.
6. Adjustment-line-mistaken-for-period-value case studies: insufficient
   data in both languages — a data-modeling failure mode, not a named
   industry phenomenon.
7. Practice-layer addition adopted into Smallest End State 1: memo-level
   recast annotation via coverage_flags (metadata beside, never inside,
   the series).

## What Becomes Obsolete (Axis 5)

- BACKLOG §"JNJ RestatementAxis signature blind spot" — consumed; delete on
  ship.
- The silent-drop else-path in `_dimension_signature` (replaced by
  exclude-with-count) and the stale "three axis local names" docstring
  (:1845, now four) — fix in the same change.
- The whole-series abort semantics of `build_quarterly_series` (replaced by
  per-signature refusal entries).

## Decision

Build: producer-side vintage-axis exclusion (RestatementAxis allowlisted as
a recognized vintage qualifier; unknown axes excluded-with-count instead of
silently collapsed), keeping the 3-key signature shape untouched; plus
consumer-side per-signature refusal granularity riding the existing
non-fatal channels; live JNJ acceptance + 12-ticker regression; 2.25.0.
NOT building: a bindable restatement-series lane (opt-in future feature),
any domain-teams protocol change (generic coverage_flags disclosure already
covers new flag types — verify at plan time), non-US mechanisms (EDINET 遡及
処理 is a different axis entirely).

## Out of Scope

- Originally-reported-vs-restated delta analytics (future opt-in lane).
- 52/53-week post-ship 🟢 debt (fires on next touch of named files —
  unrelated).
- Backfilling other tickers' historical packs; JP/TW/KR/CN lanes.

## Open Questions

1. Which existing counter channel carries the exclusions (`selection_gaps`
   vs a sibling counter) — implementer reads the pack schema and picks;
   plan pins the choice via test.
2. The exact RestatementAxis member on the JNJ pair (probe said
   RevisionOfPriorPeriodReclassificationAdjustmentMember) — re-verify live
   during implementation; exclusion is member-agnostic (any member on the
   axis) so the answer doesn't fork the design.
