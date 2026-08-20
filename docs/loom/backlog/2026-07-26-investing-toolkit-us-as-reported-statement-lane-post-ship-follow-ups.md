---
name: 2026-07-26-investing-toolkit-us-as-reported-statement-lane-post-ship-follow-ups
description: investing-toolkit US as-reported statement lane — post-ship follow-ups
status: open
---

- (a) 🟢 **ACCEPTED RESIDUAL — a silent-NCI filer can still be falsely flagged by the
  balance-sheet identity.** `kpi_spine_view._minority_interest_term` reads an absent
  `MinorityInterest` as 0 on the `parent_only` branch. A filer that tags ONLY the
  parent-only `StockholdersEquity`, genuinely HAS a non-controlling interest, and tags
  that interest NOWHERE — no `MinorityInterest`, no incl-NCI equity total — therefore
  has its NCI silently treated as zero, and the residual it produces is exactly that
  interest: the filer is accused of our missing term. Recorded here rather than only in
  the module docstring because it is an accepted defect, not a documented behaviour.
  - **Why it is accepted, measured.** (1) It requires the filer to omit a
    balance-sheet line ASC 810-10-45-16 requires — NCI must be presented in equity,
    separately from parent equity. (2) It occurred **0 of 13 times in-sample**: of the
    committed probe's 32 checkable filers
    (`tests/data/fixtures/us_statement_shapes_probe_2026-07-26.json`), 13 resolved
    parent-only with no `MinorityInterest` at that instant, and all 13 balance EXACTLY
    — which can only hold if absence there really means "no non-controlling interest".
    (3) The alternative (absent MI ⇒ period uncheckable) would silence the identity for
    the single-entity majority, i.e. trade a zero-observed false accusation for
    switching the check off on the common case.
  - **The detectable half is handled AS OF the 2026-07-26 statement-lane conflict fix
    — it was not, when this item was written.** When the filer tags BOTH equity totals
    it is asserting an NCI exists (the line between the two subtotals), so an absent
    `MinorityInterest` there is a MISSING AMOUNT and the period is uncheckable —
    `_minority_interest_term`'s `nci_is_asserted` branch, pinned by
    `test_a_parent_only_period_whose_asserted_nci_has_no_amount_is_uncheckable`.
    - That claim was ASPIRATIONAL as first written, and the correction is the point.
      The branch was pinned only by tests feeding hand-built store dumps carrying both
      equity concepts — an input the PRODUCER could not emit. `build_statement_backfill`
      routed the `total_equity` chain through `_resolve_concept_per_period`, which read
      the two totals' (correct, necessary) difference as a value conflict and dropped
      the instant under BOTH concepts. So on the 17 probe filers that tag both (CVX,
      PSX, WFC, C, MS, IBM, QCOM, COST, PEP, JNJ, PFE, UNH, BA, GE, F, GM, TSLA) there
      was no equity at all, hence no identity, hence `nci_is_asserted` was UNREACHABLE
      end-to-end. The statement lane no longer selects between chain members, so the
      path is now genuinely reachable — verified live 2026-07-26 on TSLA, whose
      `2025-12-31` instant emits both `us-gaap:StockholdersEquity` (82,137M) and
      `us-gaap:StockholdersEquityIncludingPortionAttributableToNoncontrollingInterest`
      (82,807M); the 670M difference is its NCI.
    What remains open is only the case where NOTHING in the filing asserts the NCI, so
    nothing inside `companyfacts` can distinguish it from a genuine single entity.
  - Re-trigger: a real filer's flag turns out to trace to this (the flag's
    `equity_kind: "parent_only"` + `components.minority_interest: 0` is the signature),
    or the probe sample grows and the parent-only-with-untagged-NCI branch fires
    non-zero times. Fixing it needs evidence from OUTSIDE `companyfacts` (the filing's
    own equity statement or presentation linkbase); do not "fix" it by making absence
    uncheckable without re-measuring (2).
- (b) 🟡 **`build_top_line_backfill` is 208 code lines and carries a FIFTH verbatim copy
  of the 5-key DQC skip-flag dict.** Raised by the Task 5 code-quality re-review
  (2026-07-26). The statement lane extracted exactly this shape into
  `sec_edgar_client._statement_skip_flag`, and that helper's own docstring names
  `build_top_line_backfill` as a user of the shape it centralizes — but that function
  does not call it. Fix: rename the helper lane-neutral (`_dqc_skip_flag`) and route
  both lanes' appends through it.
  - **Deliberately deferred, with the reason stated.** This is a PRE-EXISTING shape;
    the arc touched that function twice (per-period concept resolution, then the
    null-value crash) and both times had a correctness reason to. This one does not:
    it is structural tidying with no behaviour at stake, and the reviewer itself said
    the orchestrator may legitimately defer it. Deferring keeps the branch's diff
    answerable.
  - Re-trigger: the next touch of `build_top_line_backfill` for any reason, or a SIXTH
    copy of the flag dict appearing. Do it as its own commit — a refactor mixed into a
    behaviour change is what makes the 208 lines hard to review in the first place.
- (c) 🟢 **`_statement_period_kind`'s instant branch returns before any date parsing**,
  so a truthy-but-unparseable `end` becomes a durable `period_end` and, downstream, the
  store's `period` key. The duration branch fails loud on the same corruption via
  `_duration_span_days`. Not observed and not plausible in `companyfacts`, so this is an
  asymmetry in the module's own fail-loud posture rather than a live defect — but the
  surrounding docstring states its other limits explicitly, so this one should be stated
  too (or closed with one `date.fromisoformat`).
- (d) 🟢 **The kept-raise docstring reads as exhaustive when it is illustrative.**
  `_statement_row_to_fact`'s "THE ONE WAY OUT THAT IS NEITHER" names only a non-empty
  unparseable `start`, but `_duration_span_days` also raises on an unparseable `end` and
  on a non-increasing window, and `float(value)` raises on a present-but-non-numeric
  value. The stated PRINCIPLE (absent field → skip, present-but-corrupt → raise loud)
  covers all four honestly; widen the subject from `start` to "a present-but-corrupt
  date or value".

- (e) 🟡 **Temporary equity can be SEVERAL lines, and the mezzanine chain picks
  only one.** Surfaced by the live dogfood; it is the ONE balance-identity flag that
  survives every fix this arc made, and it survives CORRECTLY.
  - **Measured.** TSLA 2016-12-31, checked vintage `0001564590-18-002956`
    (as_of 2018-02-23): assets 22,664,076,000 − (liabilities 16,750,167,000 +
    mezzanine 367,039,000 + parent-only equity 4,752,911,000 + minority interest
    785,175,000) = **8,784,000**. That residual is exactly TSLA's *Convertible
    senior notes* temporary-equity line for 2016 — a SECOND temporary-equity line
    sitting alongside the redeemable non-controlling interest the chain did pick.
  - **The shape, stated correctly** (an earlier revision of this entry said the
    chain "does not reach pre-2016", which was wrong — it was written from
    pre-fix evidence): `MEZZANINE_CHAIN` is a FIRST-PRESENT chain, so when a filer
    reports two distinct temporary-equity lines in one period it accounts for one
    and silently omits the other. Widening the chain to earlier eras would NOT fix
    this; the fix is to treat temporary equity as a SUM over the concepts present,
    not a first-present pick — which is a different rule from every other chain in
    the view and needs its own evidence before being written.
  - **The flag is doing its job, not misfiring.** It points at THIS VIEW's concept
    selection being too narrow, which is exactly what the check exists to surface.
    Leaving it visible beats tuning it silent.
  - Evidence bar for the fix: measure across the corpus which concepts carry
    temporary equity and how often a filer reports more than one in a period. A
    sum-rule adopted from one filer's balance sheet is how a wrong mapping enters —
    and unlike a first-present pick, a wrong SUM double-counts rather than omits.
  - Re-trigger: a second filer's surviving flag traces to a second temporary-equity
    line, or the corpus is re-probed for temporary-equity concept coverage.

- (f) 🟢 **Unit selection is now row-count dependent, so it is stable within a
  fetch but not across fetches.** `_companyfacts_unit_key`'s fallback picks the
  unit key with the most rows (replacing dictionary order, which was worse). SEC
  appends rows over time, so a concept whose two non-USD keys sat near a tie could
  select key A this quarter and key B next. `unit` is a NON-key field, the
  intra-pack guard compares `value` only, and the ingest driver has no unit guard —
  so the store would silently accumulate two unit series under one `kpi_id` with
  nothing failing loud. No near-tie is observed (the measured cases are 3-vs-303 and
  11-vs-295), and the rule this replaced was strictly weaker. Fix is either widening
  the docstring's determinism claim to name cross-fetch instability, or adding a
  per-kpi_id unit-change guard beside the existing value guard.
  - Re-trigger: a filer's `unit` changes between two fetches of the same `kpi_id`,
    or a concept is observed whose two non-USD key counts are within ~2x.
- (g) 🟢 **A hand-fed-payload test can pin a production path that is unreachable.**
  `test_a_parent_only_period_whose_asserted_nci_has_no_amount_is_uncheckable` was
  green for this entire branch while the code path it pins could not be reached from
  the producer at all — it fed a hand-built store dump carrying both equity
  concepts, an input the producer could not emit until the conflict-rule fix landed.
  The path is genuinely reachable now (TSLA 2025-12-31 carries both subtotals), so
  this is not a live hole; what is missing is anything STRUCTURAL preventing a
  repeat, since no view-layer test in this suite carries a reachability obligation.
  - Possible fix, not yet decided: require a new view-layer branch pin to name a
    filer in the committed 47-filer probe fixture that exercises it — the fixture is
    the available anchor, and naming one is cheap at authoring time and impossible
    to fake.
  - Re-trigger: the next view-layer test that pins a branch of a producer-fed code
    path, or a second incident of a green test over an unreachable path.
