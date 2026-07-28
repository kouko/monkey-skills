# loom family backlog

> SSOT for cross-plugin open items. Convention: one entry per item with
> **start/re-trigger condition**, **origin** (PR / ledger / discussion),
> and **status** (`COMMITTED-NEXT` | `OPEN` | `PARKED` | `UPSTREAM` |
> `SHIPPED` | `CLOSED — SUPERSEDED`). The last two are the exceptions to the
> deletion rule below, and both were already in use before they were listed
> here (`SHIPPED` at two entries; `CLOSED — SUPERSEDED` where a brief requires
> a discoverable pointer that a deleted entry could not carry).
> Plugin-local parks stay in each plugin's README (§parked items with
> re-triggers); this file holds items that cross plugin boundaries or
> have no plugin home yet. Claude-side session memory keeps only a
> pointer here — this file is the durable truth (versioned, host-agnostic,
> greppable). Completed items are deleted, not archived — git history is
> the archive.

## dev-workflow → loom-workflow rename — evaluated, NOT recommended (PARKED)
- Status: PARKED
- Start: only if dev-workflow becomes genuinely loom-only — i.e. `dbt-model-style`
  has moved out AND no non-loom caller remains (git-memory no longer gates
  non-loom commits). Not today's reality.
- Origin: bba proactive-trigger-hardening arc (2026-07-25) side-discussion.
  User asked whether dev-workflow, since loom-* is its dominant citer
  (loom-code 23 + loom-pipeline 2 prose refs vs ~3 non-loom), should be
  renamed `loom-workflow`.
- Verdict: **NOT recommended now.** (1) Asserts a false loom-exclusivity —
  `dev-workflow:git-memory` gates EVERY commit in any repo, loom or not; the
  prose-reference count misses harness/user invocation. (2) `dbt-model-style`
  is dbt-specific, not loom — the plugin is a general dev toolkit. (3) Inverts
  the placement principle (below): the health test is "does the skill stand
  alone", not "who cites it most". (4) Breaking rename blast radius reaches the
  user's OWN global rules (`~/.claude/rules/institution-maintenance.md` cites
  `dev-workflow:git-memory`; `judgment-rubrics.md` cites
  `dev-workflow:brief-before-asking`), marketplace.json, 25+ repo refs, and all
  guard tests pinning `dev-workflow:` strings. (5) Name by function, not by
  dominant caller (callers change; function doesn't).
- Better path if the goal is family-membership clarity: document dev-workflow's
  dual role (loom shared foundation + standalone dev tools) in loom-memory /
  family reception — no rename.
- **Placement principle (reusable, worth recording separately)**: a skill
  belongs in the shared general layer (dev-workflow) iff it stands alone
  outside loom; the citation-count metric will always favor loom and is the
  wrong test. Same error class as "move bba into loom" — mis-scoping a general
  tool into the loom namespace.

## dbt-wiki 3.3.0 — post-rename follow-ups (OPEN)
- Status: OPEN
- Start: next substantive touch of dbt-wiki's `query` / `init` / `ingest`
  SKILL.md, or the next dbt-wiki arc — whichever comes first.
- Origin: PR for `feat-dbt-wiki-update-rename` (dbt-wiki 3.3.0, sync→update
  rename + `using-dbt-wiki` router + first CI); whole-branch review round-2
  findings N2 and the disclosed pre-existing overage.
- What: (a) **Demotion-stale sibling cross-refs** — six references still name
  `/dbt-wiki:rescan` as the action for "wiki is stale / dbt changed", which
  now contradicts rescan's own narrowed description and the router's
  "`update` is the whole answer": `skills/query/SKILL.md:233,244,343,377`,
  `skills/init/SKILL.md:1136`, `skills/ingest/SKILL.md:16`. They survived
  every rename sweep because they contain no `sync` token — only the
  DEMOTION makes them stale, which no grep for the old name can see. Point
  them at `/dbt-wiki:update`, keeping rescan named as the cheap alternative
  where LLM cost is the stated concern. (b) **`skills/init/SKILL.md` is
  ~6,435 words**, over the repo's ~4,500-word soft cap — pre-existing,
  unrelated to the rename arc; folding a large prose refactor into that
  branch would have been scope creep. Needs its own extract-to-references
  pass.

## loom gate hardening — deferred CI-side arc (OPEN)
- Status: OPEN
- Start: next substantive touch of `loom-code/scripts/loom_gate_markers.py`,
  the pipeline seg2 validator (`loom-pipeline/scripts/driver_40_seg2.js`), or a
  decision to add server-side gate re-checks.
- Origin: loom gate-hardening mechanical arc (branch
  `loom-gate-hardening-mechanical`, 2026-07-20/21); audit
  `docs/loom/audits/2026-07-20-loom-mechanism-weakness-audit.md` §7 + the
  branch brief §Out of Scope. The mechanical fixes (verified→`--run`, push-guard
  wrappers, batch precursor guard, version-bump `scripts/`) shipped this branch;
  the items below were deferred because they are NOT locally solvable as
  mechanical fixes.
- What: (a) **waiver + review-pass "cannot self-mint"** — local cryptographic
  unforgeability is impossible (the gated agent shares the shell; Axis-4 research
  in the audit §7). Real fix = CI-side re-check + a deliberateness bar (deny-list
  / PreToolUse), i.e. a separate trust domain. This SUPERSEDES audit §7 rec#2's
  "waiver needs an un-self-suppliable token" — that token does not exist locally.
  (b) **pipeline seg2 validator self-report**: the Workflow-sandboxed
  `driver_40_seg2.js` cannot exec a subprocess, so "the gate runs the validator
  itself" needs an architecture change (move the validator call to a
  sandbox-external step); `batch_queue.py` already does it right because it is
  sandbox-external Python. (c) **#8 DESIGN.md path resolution** —
  `mint_critic_verdict.py` resolves `--files` change-folder-relative but
  DESIGN.md is product-level → exit 4 under canonical layout. (d) **#6 Codex
  git-guard-shim fail-open** on payload-shape drift — needs Codex's real payload
  spec. (e) flat-folder CI omits loom-discovery + loom-pipeline; mint lockstep
  test lives only in loom-interface-design.

## loom-memory store hardening — deferred F2/F3/F5/F6 (OPEN)
- Status: OPEN
- Start: at ~150 store entries, on a real recall miss, or next substantive
  touch of `loom-pipeline/skills/loom-memory/SKILL.md`.
- Origin: loom-memory design review (2026-07-22; branch
  `loom-memory-integrity`). F1 (integrity checker + CI) + F4 (recall
  staleness caveat) SHIPPED this branch; the review's other findings were
  triaged DEFER because they are slow-burn or hard to mechanize.
- What: (a) **F2 size governance** — the store (81 entries, README §Index
  ~33 KB) has no cap / graduation / hot-tier, unlike the sibling auto-memory
  MEMORY.md (24.4 KB soft cap + archive index). Grows unbounded; recall greps
  the whole store. Revisit at ~150 entries. (b) **F3 recall precision** —
  keyword-grep has a false-negative floor (a semantic match with no shared
  keyword is silently missed); the cheap mitigation is a "try alternate
  keyword angles before concluding no-hits" recall nudge (embeddings are YAGNI
  at this scale). (c) **F5 prune trigger** — prune is manual-only with no
  age/size signal that ever wakes it → one-directional accumulation; F4's
  verify-before-act caveat already covers most of the staleness *harm*, so the
  trigger is low-priority. (d) **F6 mirror-hook verification** — the
  auto-memory→loom-store bridge (`.claude/hooks/remind-memory-mirror.sh`) is
  remind-only and hard to mechanize (CI can't see per-machine auto-memory);
  accept, or improve the reminder's specificity.

## investing-toolkit TW iXBRL endorsement/guarantee 2.33.0 — post-ship follow-ups (OPEN)
- Status: OPEN
- Origin: TW iXBRL endorsement/guarantee ingestion (branch tw-ixbrl-endorsement,
  2026-07-24, 2.33.0); whole-branch review PASS, all 🟢.
- What: (a) 🟢 **memo-render the endorsement field** (domain-teams / report-equity-memo
  layer, out of this data-layer arc) — `_extract_notes` now surfaces the
  `endorsement_guarantee` curated field (aggregate + per-counterparty rows); wire the
  memo protocol to render the credit-risk / self-dealing signal. The reserved
  `endorsement_guarantee` key is taxonomy-INDEPENDENT but sits in a taxonomy-SHAPED
  notes dict — the render consumer must special-case it regardless of taxonomy.
  (b) 🟢 **terminal-span forward-scan edge**: `_endorsement_row_segments`' last row span
  runs to end-of-facts; if a filing ever has a table trailing the endorsement section
  reusing a shared concept (EndingBalance2/ActualAmountProvided) AND the last endorser
  row omits it, `_first_in_span` could absorb the trailing value. Not observed on 1101
  (資金貸與 sits BEFORE the anchors); confirm with a 2nd endorsement fixture. (c) 🟢
  **no fh+endorsement fixture**: the cross-taxonomy "a financial holding can carry
  endorsement too" claim rests on the -ci 1101 merge + shared code, not a fixture where
  an fh notes dict actually gains `endorsement_guarantee` beside bank-name keys — add one
  when a populated-fh filing is available.

## investing-toolkit TW iXBRL ingestion 2.27.0 — post-ship follow-ups (OPEN)
- Status: OPEN
- Start: next touch of `investing-toolkit/skills/data-markets/scripts/twse_ixbrl_*.py`
  or `pack_tw.py` memo-fetch.
- Origin: TW iXBRL ingestion (branch xbrl-tw, PR #592, 2026-07-19); brief/plan
  Decision Log + whole-branch review ship-as-debt rulings.
- What: ~~(a) **financial `-fh` canonical + notes sub-arc**~~ ✅ SHIPPED 2026-07-23
  (2.31.0, branch feat-tw-ixbrl-fh) — `-fh`/`-basi`/`-bd`/`-ins` canonical builders +
  5-way classifier + bank asset-quality notes + smart-decode + DCF fail-loud;
  securities-dealer (`-bd`) and insurer (`-ins`, incl. life/P&C/reinsurance sub-shapes)
  resolved too. ~~(b) **endorsement/guarantee curated field**~~ ✅ SHIPPED 2.33.0
  (branch tw-ixbrl-endorsement) — `extract_endorsement_guarantee_notes`
  reconstructs per-counterparty rows by document-order segmentation on the
  `CompanyNameOfTheEndorserGuarantor` anchor + a span-scoped curated aggregate
  (avoids the 資金貸與 doc-wide-sum overcount), routed by population through
  `_extract_notes`; the deferral test flipped to an inclusion assertion.
  (c) **興櫃 multi-period series** — semiannual
  (Q2/Q4) cadence; season-fallback already handles per-period absence, a series
  builder is future. **Update (2.35.0):** the TW KPI store producer (`kpi_tw` +
  `kpi_tw_ingest`) now handles the 興櫃 semiannual cadence — a 6-month duration
  maps through the store's existing `_qtrs` machinery (→ 2 quarters) with no new
  `period_kind`. So 興櫃 multi-period now only needs 興櫃 FETCH; the series-build
  side is done. (d) 🟢 debt: T3 canonical tie-break order untested (membership
  only), T2 3×502-exhaustion branch untested.

## investing-toolkit TW financial iXBRL 2.31.0 — post-ship follow-ups (OPEN)
- Status: OPEN
- Origin: TW financial-sector iXBRL (branch feat-tw-ixbrl-fh, 2026-07-23, 2.31.0);
  whole-branch review PASS with carried 🟢 debt.
- What: ~~(a) **memo Phase-4 consumption of `not_applicable` DCF**~~ ✅ SHIPPED 2.32.1
  (three render surfaces branch on the marker → "DCF: N/A — financial sector"; live
  2882.TW dogfood CLEAN). ~~(b) 🟢 Rule-of-Three duplication~~ ✅ SHIPPED 2.32.1
  (`_ordered_values_meta` in canonical, `_group_and_select_current` in notes). (c) 🟢
  over-soft-cap functions: `dcf_compute.main`, `pack_memo_fetch` — STILL OPEN (and
  `report-equity-memo/SKILL.md` body now within ~115 words of the hard cap; next addition
  needs a trim). ~~(d) 🟢 fact-count guard under production decode~~ ✅ SHIPPED 2.32.1
  (`test_fixture_fact_counts_match_under_production_decode`, 8 fixtures, zero deltas).
  ~~(e) 🟢 stale scratchpad citations~~ ✅ SHIPPED 2.32.1 (all 5 replaced with the
  operative measured fact inline). (f) US financial filers (`pack_us`) get no
  `sector_class` guard — pre-existing; a future US financial-comps path needs its own.

## investing-toolkit TW financial iXBRL 2.32.1 — post-ship follow-ups (OPEN)
- Status: OPEN
- Origin: TW financial iXBRL Phase-4 consumption arc (branch tw-fin-ixbrl-followups,
  2026-07-24, 2.32.1 — renumbered from 2.31.1 after main advanced to 2.32.0);
  2882.TW live render dogfood.
- What: (a) 🟢 **stale/over-broad `_status.failed_sections`** — the 2882.TW memo-fetch
  emits `_status.failed_sections: ["mops"]` while `mops.*` (company_basic + balance/income/
  cash) is fully populated with legible data; the flag looks stale/over-broad. Pre-existing
  in `pack_tw`'s `_status` computation, out of the DCF-render arc; a memo would surface it in
  Limitations. Reconcile the flag with actual section presence on next `pack_tw` touch.
  (b) 🟢 **em-dash grep fragility** — the pin phrase `DCF: N/A — financial sector` uses an
  em-dash (`—`); the orchestrator acceptance grep and every render surface share the one
  pinned string (internally consistent, cannot drift without a deliberate edit), but a future
  hand-edit typing a hyphen would silently break the grep. Consider a hyphen-tolerant match
  or a stable marker token if the phrase is ever re-typed. (c) 🟢 Rule-of-Three tail (below
  threshold, next-touch): `_derive_total_debt` now == `_sum_concepts(...)` verbatim (2 sites),
  and two `twse_ixbrl_canonical.py` builder loops (~:350/:528) + `_derive_fcf` still inline the
  `sorted→values→meta` shape `_ordered_values_meta` abstracts — route through the helper when
  next touched. (d) 🟢 `test_twse_ixbrl_fixtures.py` module docstring still says "these 7
  fixtures" though it now also exercises the -ci 2330 fixture; the 2330 fact-count literal
  `2002` is a 3rd pin copy — touch-up on next edit.

## investing-toolkit US as-reported statement lane — post-ship follow-ups (OPEN)

- Status: OPEN. Filed 2026-07-26 from the Task 7 review rounds (branch
  `feat-us-as-reported-statement-lane`; shipped version TBD at close-out — the
  branch still carries 2.37.0 from the preceding arc).
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

## investing-toolkit — spine chain misses 33 filer-years of reported history (CLOSED — superseded)

- Status: **CLOSED 2026-07-26 — SUPERSEDED, do not start.** The fix this entry
  proposed (widen the chains with early-era synonyms) is no longer the plan.
  Pointer: `docs/loom/specs/2026-07-26-as-filed-statement-reconstruction.md`
  §What Becomes Obsolete, implemented on branch `feat-spine-chain-coverage`.
  That brief resolves revenue from the FILING'S OWN calculation tree instead of
  from a chain (`kpi_spine_view._revenue_total`), so the missing-synonym cause
  below no longer produces a short series on the as-filed path — KO's
  `SalesRevenueGoodsNet` is picked up because the filer declared it as its
  total, not because anyone added it to a list.
  - **What this does NOT cover, stated so the closure is not oversold.** The
    reconstruction is a SECOND entry point; `derive_spine` over the store dump
    still resolves `SPINE_FIELD_CHAINS` and still starts those five filers'
    revenue late. And only `revenue` moved — the other 13 fields resolve by
    chain on both paths (`kpi_spine_view.py`, the disposition block above
    `SPINE_FIELD_CHAINS`), so `net_income`'s 6 TGT filer-years below are
    untouched by the brief.
  - **Kept rather than deleted**, against this file's "completed items are
    deleted" convention: the brief REQUIRES a pointer here, and a deleted entry
    carries none — a future reader who greps for the synonym fix must land on
    the reconstruction rather than on nothing. The measured table below is also
    the artifact the entry was filed to preserve.
- Originally filed 2026-07-26 from the post-PR end-to-end coverage audit of
  PR #619 (branch `feat-us-as-reported-statement-lane`, 2.38.0).
- **What.** The spine chains omit concepts that filers really used, so a field
  starts late rather than showing a hole. Measured over the arc's own 47-filer
  corpus, duration-filtered to annual 10-K rows:

  | field | filers affected | filer-years lost | who |
  |---|---|---|---|
  | `revenue` | 5 / 46 | **27** | KO 2007-2015 (9y), JNJ 2007-2015 (9y), MRK 2011-2015 (5y), AMD 2008-2009 (2y), PFE 2014-2015 (2y) |
  | `net_income` | 1 / 46 | **6** | TGT 2013-2019 |
  | `operating_income`, `capex` | 0 / 46 | 0 | — |

  41 of 46 filers have complete revenue coverage. The dominant cause is one
  missing synonym: those filers tagged early-era revenue
  `SalesRevenueGoodsNet`, and the chain lists only `SalesRevenueNet`.
- **Why it hid.** A missing chain concept does not create a GAP — the field's
  span simply starts later, so a mid-series-hole check (which this arc ran, and
  which found zero holes across five filers) cannot see it. It is only visible
  by comparing the years the CHAIN can serve against the years the filer
  reported the same line under ANY concept. That comparison is the artifact
  this entry exists to preserve.
- **Why it was NOT fixed in the shipping branch.** The chains are the source of
  the store's series identity, so widening one is a durable decision, and the
  candidate list used to MEASURE the gap was hand-picked rather than measured —
  it proves those six filers used those tags, not that adding the tags is safe
  for the other 41. Adding a concept that turns out to mean something narrower
  (a segment, a product line, a net-of-something variant) would write wrong
  values into an append-only store, which is strictly worse than the current
  honest short series.
- **The evidence bar, retained but no longer a work item.** Widening the chains
  is superseded on the as-filed path and NOT recommended on the store path; if
  anyone widens one anyway, this is still the bar it has to clear, in order:
  1. For each candidate concept, check on the filers that DO have full coverage
     whether the candidate is also present and, if so, whether it agrees with
     the chain's own value for the same period. A candidate that disagrees
     anywhere is a different line, not a synonym.
  2. Confirm the candidate is the WHOLE-COMPANY line, not a dimensional or
     segment slice — `companyfacts` carries only default-axis facts, which
     helps, but a filer can still tag a narrower total.
  3. Only then widen, and re-run the coverage audit to confirm the 33 years
     land and nothing else moves.
- **Verification artifact to reuse**: the audit itself
  (`e2e_coverage.py` / `chain_coverage.py` shapes from that session) — coverage
  matrix + independent value check against the `companyconcept` endpoint, which
  is a different API path from the `companyfacts` the lane reads. Note the
  duration filter is load-bearing in both: a 10-K also tags quarterly rows, and
  counting them makes a quarter masquerade as a fiscal year (this bit the audit
  itself once — JNJ FY2009, a 97-day row compared against the annual figure).
- Re-trigger: NONE for the fix — it is superseded. Re-read this entry only if
  the STORE path's short revenue series is reported as a defect (the
  reconstruction does not serve `kpi_store dump | kpi_spine_view derive`), or
  if `net_income`'s 6 TGT filer-years surface, which no shipped change covers.

## loom docs — two stale change-folders belong to shipped arcs (OPEN)

- Status: OPEN. Filed 2026-07-26 from the as-filed-reconstruction plan's
  `## Notes` (change-folder binding: N/A), which had to establish this to state
  that neither folder binds that branch.
- **What.** `docs/loom/2026-07-12-us-sec-primary-source-layer` and
  `docs/loom/2026-07-19-8k-prose-kpi-intake` sit un-archived at the top level of
  `docs/loom/` while both belong to arcs that already shipped. Archive them.
- **Why it matters, and why it is small.** A live-looking change-folder is the
  first thing a new arc's planner checks for a binding; two that bind nothing
  make every future plan spend a paragraph ruling them out (this one did). Pure
  housekeeping — no code, no tests.
- **Why it was not done in that arc.** Unrelated to the branch's work; folding
  it in would have been scope creep in a branch already touching 8 modules.
- Re-trigger: the next loom arc that opens a change-folder, or any docs-only
  housekeeping pass over `docs/loom/`.

## investing-toolkit — the `reconstruct` verb inverts the pack layering (OPEN)

- Status: OPEN. Filed 2026-07-26 at the close of the as-filed-reconstruction arc
  (branch `feat-spine-chain-coverage`); recorded as its plan's `## Decision Log`
  entry "Task 9 → whoever revisits the pack layering".
- **What.** `pack_us.py` is a Layer-1 I/O module, and the `reconstruct` verb
  there imports an analysis-layer function (`kpi_us_statement_shape.statements_for`)
  — the opposite of this repo's usual direction, where analysis calls data and
  never the reverse. The inversion is named in a comment at the site, so it is
  visible rather than silent.
- **Why it was accepted rather than fixed mid-arc.** It is a TWO-WAY door. The
  repo's convention crosses layers by SUBPROCESS, which is unavailable here:
  `statements_for` takes a live edgartools `Filing` object, which does not
  survive a JSON boundary. Restructuring inside the arc would have been a plan
  change improvised at implementation time.
- **The honest resolution, not yet decided.** The verb probably belongs in
  analysis-kpi, with data-markets supplying only acquisition
  (`sec_edgar_client._acquire_raw_filing`). That is a plan change and wants its
  own brief — it moves a shipped command surface, so the SKILL.md declaration
  and `SUPPORTED_PACKS` registration move with it.
- Re-trigger: the next arc that touches `pack_us.py`'s verb set or the
  analysis-kpi ↔ data-markets boundary; or a second analysis import landing in a
  Layer-1 module, which would make this a pattern rather than one exception.

## investing-toolkit kpi_id identity 2.37.0 — post-ship follow-ups (OPEN)

- Status: OPEN. Filed at close-out 2026-07-26 (branch `feat-kpi-id-consolidation-axis`).
- (a) 🟡 **No committed dogfood HARNESS.** The close-out dogfood (real
  `ingest_pack` → `kpi_store.append` over 47 cached live packs) is what caught the
  filename-length regression the 1084-test suite and the replay probe both missed —
  but it ran from a session scratchpad and was NOT committed, so the next arc has to
  rebuild it. The committed probe
  (`tests/data/fixtures/capture_kpi_id_identity_probe.py`) replays the selector loop
  only, by design. Making the dogfood repo-ready is real work (fetch/cache path,
  isolated stores, counts-only output) and wants its own test + review, which is why
  it was filed rather than patched in at close-out. Re-trigger: the next arc that
  changes a producer or the store's write path — per
  `docs/loom/memory/a-data-probe-is-not-a-pipeline-dogfood.md`, do NOT let a probe
  stand in for it again.
- (a2) 🟡 **`_signature_key` and `derive_kpi_id` disagree about the
  ConsolidationItemsAxis — the guard can raise a FALSE collision.**
  `derive_kpi_id` EXCLUDES `srt:ConsolidationItemsAxis` from the breakdown pairs
  (`kpi_xbrl_ingest.py:255`); `_signature_key` leaves it in (`:348`). So a fact
  carrying that axis INSIDE `dimensions` — rather than in its own `consolidation`
  field — yields ONE kpi_id but TWO claim keys, and `_claim_kpi_id` refuses a pair
  the id derivation is explicitly tested to fold
  (`test_kpi_xbrl_ingest.py:662-669`). Executed probe, close-out review round 3:
  `{SegmentAxis: DataCenterMember, srt:ConsolidationItemsAxis: OperatingSegmentsMember}`
  + `consolidation=None` versus `{SegmentAxis: DataCenterMember}` +
  `consolidation="OperatingSegmentsMember"` → identical id, non-equal claim keys,
  raise. **Not reachable through the shipped producer**:
  `sec_edgar_client._dimension_signature` allowlists four breakdown axes and routes
  the consolidation axis to its own field (`:2265-2281`), so only a hand-built or
  third-party `--pack` can express it; and it fails LOUD (whole-pack abort), never a
  silent merge. Deliberately NOT fixed at close-out: aligning the two would change
  `_signature_key`'s selector grouping, a wider blast radius than the defect, and the
  brief scoped that function as untouched. Both affected docstrings now state the
  divergence instead of claiming unification. Re-trigger: any arc that admits
  third-party fact-packs, or the next touch of either key builder.
- (a3) 🟢 **Two modules disagree on what "the consolidation axes" means.**
  `kpi_xbrl_ingest._CONSOLIDATION_AXIS_LOCAL` (`:101`) names ONE axis; the producer's
  `sec_edgar_client._CONSOLIDATION_AXIS_LOCAL_NAMES` (`:1997-2000`) names TWO
  (`ConsolidationItemsAxis`, `ConsolidatedEntitiesAxis`) and folds both into the one
  `consolidation` field. Unreachable today for the same allowlist reason as (a2);
  fold into (a2)'s fix when it happens.
- (b) 🟢 **Predictable temp path in the probe capture script**
  (`tests/data/fixtures/capture_kpi_id_identity_probe.py:93`): the pack cache is a
  fixed name under the world-writable system temp dir (CWE-377), and its cached
  packs become committed evidence. Hand-run dev script only; move to `mkdtemp` or a
  repo-local ignored dir on next touch.
- (c) 🟢 **Stale cross-reference in the same script** (~:54-57): it cites "the
  sibling probe script's fetch loop", but the only committed sibling
  (`capture_companyconcept_form_domain.py`) has no fetch loop or cache. The
  reference does not resolve; fix wording on next touch.

## investing-toolkit — a ticker resolving to a re-registered holding company returns nothing, successfully (OPEN)

- Status: OPEN. Filed 2026-07-27 from the 71-filer live sweep run for PR #621.
- Origin: dogfood of `pack.py --pack reconstruct`. `XOM` returns
  `requested: 0 / succeeded: 0 / failed: 0`, `failed_items: []`,
  `_status: "ok"`, exit 0, in 0.1 s — a clean success over zero filings.
- Cause, measured 2026-07-27 with the post-#621 merged read: SEC's own
  `company_tickers.json` maps `XOM` to CIK **2115436** ("ExxonMobil Holdings
  Corp"), which carries 26 filings (S-8 POS ×23, 8-K, POSASR, 8-K12B) and
  **zero 10-Ks**. The predecessor CIK **34088** carries 3,552 filings and
  **31 10-Ks spanning 1994-03-11 to 2026-02-18**. `resolve_cik` succeeds,
  `list_filings` returns an empty list, the loop never runs, and
  `pack_reconstruct` reports the empty result as healthy. The defect is ours:
  `requested == 0` is not distinguished from a completed run.
- **Two populations, not one — do not conflate them.** Only **1 of 71** roster
  filers exhibits THIS defect (`silent_empty`: XOM alone). `BLK` is the
  neighbouring shape: its current CIK 2012383 carries 5,049 filings but only
  **2 10-Ks, 2025-02-25 and 2026-02-25**, so it returns a truthful-but-shallow
  4-year history rather than a silent nothing. Both stem from the same cause
  (a re-registration that leaves the history under a predecessor CIK) and the
  population grows with every such reorganisation, but only XOM's failure mode
  is a lie.
- Scope note: `statement-backfill` already fails loud here — verified from
  source, not from the CHANGELOG sentence: `sec_edgar_client.py:3980-3990`
  returns `_statement_backfill_error_slot` when the `us_gaap` concept set is
  empty, and `pack_us.py:1166-1171` passes it through with no `facts` key,
  while `pack_reconstruct` (`pack_us.py:1539-1544`) iterates an empty
  `list_filings` and reports ok. **The two US lanes genuinely disagree on the
  same ticker** — but note their guards trip on DIFFERENT conditions (backfill
  on "zero us-gaap concepts", reconstruct on "zero 10-K filings"); they agree
  about XOM only because both happen to hold. Fixing the guard is cheap;
  deciding whether to STITCH across a predecessor CIK is a separate, larger
  question that 2.38.0 explicitly declined ("never stitched from a predecessor
  CIK") and this entry does not reopen.
- Start: READY. Smallest end state is a typed error when a resolved CIK yields
  zero filings of the requested form, naming the CIK so the reader can see the
  entity is wrong rather than the history empty.

## investing-toolkit — the as-filed lane returns revenue with no cells at all for banks (OPEN)

- Status: OPEN. Filed 2026-07-27 from the post-#621 end-to-end run.
- Origin: `pack.py --pack reconstruct --ticker JPM` →
  `kpi_spine_view derive-as-filed`. The `revenue` field comes back with
  **zero periods** — not one typed cell — while `gross_profit`, `cash` and
  `capex` in the same payload correctly carry `not_presented`.
- The data is present: JPM's income statement DOES carry
  `us-gaap_RevenuesNetOfInterestExpense` labelled "Total net revenue". The
  structural rule declines it because `revenue_totals` finds **three surviving
  candidates** (`InvestmentBankingRevenue`, `PrincipalTransactionsRevenue`,
  `RevenuesNetOfInterestExpense`) and refuses to pick when the count ≠ 1
  (`kpi_spine_view.py:1102-1105`); the payload's `verification` section reports
  `ambiguous_total` ×8. **Declining is correct** (user decision 「甲」,
  2026-07-26: a visible typed gap, never a chain fallback).
- **The calculation tree is NOT the problem** — recorded because the first
  draft of this entry said it was, and that would have sent someone hunting a
  missing linkbase: 195 of 239 income-statement lines across the 8 filings
  carry a `calculation_parent`, and `RevenuesNetOfInterestExpense` is itself
  the declared parent of `NoninterestIncome`.
- The defect is the SHAPE of the decline, and it is narrower than "no typing":
  the payload DOES name the candidates in an `unresolved` key
  (`kpi_spine_view.py:1210-1214`, deliberately — "the typed gap: the candidates
  are named"). What is missing is per-PERIOD typing: a consumer iterating
  `periods` gets an empty dict and must know to look elsewhere, while every
  other empty field hands it `not_presented` in the same loop. A fifth cell
  state, or `not_presented` carrying the reason, would close it.
- Blast radius, measured from `post/sweep.jsonl` rather than assumed — **3 of
  71**, and it is not "the banking sector": `ambiguous_total` fires for 5
  filers (BAC, BX, C, JPM, WFC) but BAC and BX still RESOLVE revenue, so the
  exact defect (unresolved revenue, zero fill, via `ambiguous_total`) is JPM,
  WFC and C. Separately, `revenue_concept: null` covers **8** filers (BLK, C,
  JPM, MO, NOW, PGR, WFC, XOM — 7 excluding XOM, whose null is the
  silent-empty case above rather than a resolution failure), and **four of
  those are non-banks** (MO, NOW, PGR, BLK), so the null-revenue population
  and the bank population are different sets. PR #621 moved JPM/BAC/C from 3
  annual periods to 10 and WFC from 4 to 12.
- The store lane is unaffected: JPM's `revenue` spans 19 years there
  (2007-2025 per `JPM_spine.json`), so this is an as-filed-lane presentation
  gap, not data loss.
- Start: READY. The roster census this would normally need is already in
  `post/sweep.jsonl` (the `ambiguous_total` and `revenue_concept: null`
  counts above came from it), so the open question is only whether to add a
  cell state or to reuse `not_presented` with a reason.

## investing-toolkit — store-lane revenue covers 10 years where its sibling fields cover 18-20 (OPEN)

- Status: OPEN, **DIAGNOSED** — filed 2026-07-27 as an undiagnosed observation
  and diagnosed the same day by the entry's own fact-check; the cause was
  reachable from a payload this session already held.
- Origin: post-#621 end-to-end run. `KO` through `statement-backfill →
  kpi_us_statements_ingest → kpi_store dump → kpi_spine_view derive`:
  `revenue` covers 2016-2025 (10 years) while **eight** fields cover 2007-2025
  (19 years: gross_profit, operating_income, net_income, eps_basic, and the
  cash-flow trio plus capex), `pretax_income` and `total_assets` cover
  2008-2025 (18), and `total_equity`/`cash` reach 2006 (20).
  `total_liabilities` is absent from KO's store lane entirely. The store holds
  exactly one revenue-family series for KO, `us-gaap:Revenues`.
- Contrast: `JPM`'s store lane carries TWO revenue-family series
  (`Revenues` 19 years, `RevenuesNetOfInterestExpense` 13) and the view
  resolves 19 — so this is filer-shaped, not a lane-wide cap.
- **Cause, measured** from the cached companyfacts payload
  (`facts_0000021344.json`): KO's 2007-2017 revenue is tagged
  `us-gaap:SalesRevenueGoodsNet` — 27 10-K rows — and that concept is **not a
  member of `_STATEMENT_SPINE_CHAINS["revenue"]`**, which holds exactly five
  entries (`Revenues`, `RevenuesNetOfInterestExpense`,
  `RevenueFromContractWithCustomer{Excluding,Including}AssessedTax`,
  `SalesRevenueNet`). KO carries ZERO rows of the ASC 606 concept, so the
  originally-filed hypothesis — an ASC 606 transition stranding old rows — had
  the right shape and the wrong concept. `coverage.skipped_rows` confirms no
  pre-2016 `Revenues` row was fetched-then-dropped.
- Why it matters: revenue is the first field anyone reads on a trend, and this
  is the lane that otherwise reaches 19-20 years. A 10-year revenue series
  beside a 19-year net-income series reads as a gap in the company, not in the
  tool. Note this is the SAME failure mode PR #620 fixed for the as-filed lane
  (a fixed concept chain cannot see a concept nobody listed) surviving in the
  store lane, which #620 did not touch — and the concept is one #620's own
  brief NAMED: `docs/loom/specs/2026-07-26-as-filed-statement-reconstruction.md`
  lists "pharma/beverage (`SalesRevenueGoodsNet`: MRK, PFE, KO)" among the
  sector-shaped revenue blanks. The as-filed lane stopped depending on the
  chain; the store lane still does, and its chain still does not list the
  concept the brief had already identified for this exact filer.
- Start: READY. Smallest end state is a chain-membership audit — for each
  roster filer, which revenue-family concepts appear in its companyfacts and
  which of those the chain lists — not a new mechanism.

## investing-toolkit — full three-statement + management-KPI history in kpi_store (OPEN)

- Status: OPEN — the destination arc the longitudinal work has been building
  toward. Filed 2026-07-25 after the user stated the intent explicitly: *"這一
  整段機械處理應該是要做出完整的三大表與管理/非財務指標的年度與季度的連續歷史
  資料給後續分析用的"*. That intent is the store's charter; this entry records
  how far the producers actually are from it, and in what order to close the gap.
- Start: READY. The `kpi_id` identity arc it depended on shipped as 2.37.0
  (branch `feat-kpi-id-consolidation-axis`); that ordering was a real dependency,
  not politeness — see §Sequencing.
- **The container is already right; only the feed is missing.** Grounding:
  - `report-kpi-tearsheet` is metric-AGNOSTIC — one row per `kpi_id`, periods as
    columns, whatever the store holds (`report-kpi-tearsheet/SKILL.md`). It never
    needs to learn about statements or operational KPIs.
  - `kpi_store` is bitemporal, so a restated line item keeps both vintages — the
    property that makes it an analysis substrate rather than a snapshot. Downstream
    analysis reads `kpi_store dump/query`, NOT the tearsheet (the tearsheet is a
    human one-pager over the same data).
  - **The TW producer already proves the shape**: `kpi_tw._KPI_FIELDS`
    (`kpi_tw.py:33-50`) writes a 15-field three-statement spine (revenue,
    gross_profit, operating_income, pretax_income, net_income, eps_basic,
    total_assets, total_liabilities, total_equity, cash, operating/investing/
    financing_cash_flow, capex, fcf) across `_STATEMENTS` (`:53`) into the same
    store the US dimensional producer writes to.

### Sub-arc (a) — US three-statement producer (mirror the TW lane)

- **Gap**: the US side computes canonical statements but never STORES them.
  `DCF_CONCEPT_MAPPING` (`pack_us.py:125-175`) is **14 fields chosen for DCF**,
  assembled into `income_statement` / `cash_flow` / `balance_sheet` inside
  `pack_memo_fetch` (`pack_us.py:939-941`) — and no caller of `kpi_store.append`
  consumes a memo-fetch pack (verified 2026-07-25 across every producer in
  `analysis-kpi/scripts/`). So every memo run re-fetches and accumulates nothing.
- **Cheap part**: the raw source is already fetched and cached — `action_facts`
  without `--concept` returns the filer's full concept inventory
  (`sec_edgar_client.py:695-700`, names + counts, values only per-concept). No new
  data layer.
- **Hard part, and the real work**: concept → line-item normalization. Statement
  hierarchy, sign conventions, and **subtotal reconciliation** (components must add
  back to the reported subtotal). Without the add-back check this lane is a silent-
  lie generator — a wrong mapping is invisible in a rendered table.
- **Identity**: follow the TW precedent — `kpi_id` from a repo-CANONICAL field slug,
  never the filer's raw concept string (a filer's tagging changes across years;
  a concept-keyed id fragments the series — `docs/loom/memory/derived-durable-id-
  slug-is-a-lossy-one-way-door.md`, and the 2.36.0 `total_revenue` decision).
- Open scope question for the brief: 14 DCF fields (parity with today) vs the TW
  15-field spine (cross-market comparability) vs a genuinely full statement. The
  spine is the likely smallest end state; a full statement is a different arc.

### Sub-arc (b) — management / non-financial KPI wiring

- **Gap**: the machinery shipped, the user path did not. `kpi_prose_candidates`
  (Part 1, 2.28.0) + number robustness (Part 2, 2.29.0) produce verbatim-anchored
  prose KPI candidates and `commit_to_store` (`kpi_prose_candidates.py:719`) appends
  them to the SAME store — but nothing is SKILL-wired, so the capability is
  unreachable from a conversation.
- **Fail-closed by design, keep it**: `commit_to_store(confirmed=False)` writes
  NOTHING without an explicit human confirm-all. Wiring must expose that confirm
  step, never route around it.
- **Blocked on**: Part 3 (lifecycle / re-verification / table-vs-prose and
  prose-vs-prose conflict, surface-version marker) — scoped in
  §"非金錢營運 KPI 自動化" above. Do not re-scope it here (SSOT).

### Sub-arc (c) — rendering the annual + quarterly continuum

- Already filed in full as §"KPI tearsheet — multi-granularity + per-market period
  menu (OPEN)" — sub-quarter classifier, per-market granularity menu, discrete-vs-
  cumulative axis, separate views per granularity. **Pointer only, do not restate.**
- Relevance here: US annual and quarterly each render correctly today; a MIXED
  table interleaves granularities. Once (a) lands, a company's store holds far more
  rows and the interleave stops being cosmetic.

### Sequencing (the dependency, stated)

1. `kpi_id` identity arc — **prerequisite for (a), and it SHIPPED as 2.37.0.** (a)
   multiplies stored series per company by roughly an order of magnitude (statement
   fields × periods, later × segment dimensions). Collision probability in a lossy
   id derivation rises with the number of distinct signatures, and a collision
   aborts an entire pack. Scaling the feed before fixing identity would have scaled
   the abort surface with it. The 2.37.0 close-out dogfood also showed why this
   ordering mattered concretely: JNJ's 4-axis signatures put the series FILENAME
   within 12 bytes of the OS limit, and (a)'s statement fields add more signatures
   per company, not fewer.
2. Sub-arc (a) — the largest capability gain per arc, and it has a worked TW
   precedent to mirror rather than design from scratch.
3. Sub-arc (c) — becomes user-visible pressure only after (a) fills the store.
4. Sub-arc (b) — independent of (a) and (c); ordering against them is a priority
   call, not a dependency. Blocked only on its own Part 3.

## investing-toolkit top-line revenue lane 2.36.0 — post-ship follow-ups (OPEN)
- Status: OPEN
- Start: next touch of `analysis-kpi/scripts/kpi_xbrl_ingest.py`,
  `analysis-kpi/scripts/kpi_store.py`, `analysis-kpi/scripts/kpi_xbrl.py`, or
  `data-markets/scripts/sec_edgar_client.py`.
- Origin: company total (top-line) revenue arc (branch feat-total-revenue-lane,
  2026-07-25, 2.36.0). Brief `docs/loom/specs/2026-07-25-company-total-revenue.md`,
  plan `docs/loom/plans/2026-07-25-company-total-revenue.md`. Every item below is
  a per-task review ruling that was deliberately NOT closed in-branch, with the
  reason recorded — none is an oversight.
- What:
  (a) 🟡 **`_q4_basis_mismatch_reason` guards the map ENTRY, not the field**
      (`kpi_xbrl.py:989,997`). A present calendar entry whose `fiscal_year_end`
      is `None` compares EQUAL to another such entry, so two unstated calendars
      silently affirm "shared basis" — the opposite of this repo's fail-loud
      posture. Unreachable today (Lane A emits no 9-month YTD rows and
      `derive_q4_points` takes one pack's map) but `pack_us.py:1017-1019` already
      merges two lanes' calendars into one envelope, which is the shape that
      reaches it. Fix is a field-level guard, consumer-side. TRIPWIRE (whole-branch
      review 2026-07-25): the unreachability expires the moment the multi-granularity
      arc makes Lane A quarterly — which the brief's §Out of Scope explicitly plans —
      so prefer a guard in the entry over relying on the reachability note.
  (b) 🟡 **`_SOURCE_FORM_BY_FOCUS` cannot express an amendment** (`kpi_xbrl.py:231-233`).
      Because focus→form maps `FY` to the literal `"10-K"`, the top-line backfill
      must skip `10-K/A` carriers rather than mislabel them — and a 10-K/A is the
      canonical carrier of a RESTATED annual figure. So an amended fiscal year
      keeps its ORIGINAL number in the backfill lane and never learns the
      correction. This is a value-staleness gap, not a coverage gap. Fix is
      consumer-side vocabulary, then widen the producer allowlist; pinned today by
      a red test so a producer-only widening cannot slip through.
  (c) 🟡 **Lane B's envelope contract is unverified at the seam.** The two-lane e2e
      (`tests/analysis/test_top_line_two_lane_e2e.py`) runs Lane A through its real
      producer but hand-builds Lane B's envelope, because `pack_kpi_quarterly`
      reaches its facts through edgartools `Filing` objects an offline suite cannot
      stub. The envelope-contract defect class this arc caught on Lane A is
      therefore NOT covered on Lane B — the same blind spot, one lane over. The
      file states the asymmetry; closing it needs a fixture strategy for the
      per-filing lane.
  (d) 🟡 **`summarize_concept` is currency-blind** (`sec_edgar_client.py:281`):
      `units.get("USD") or next(iter(units.values()), [])` returns whatever unit
      exists when USD is absent, and `float(row["value"])` then pushes it into a
      USD-assumed store with no error — a number carries no unit. Found while
      probing carrier forms: TM and HMC report in JPY. Blocked today only
      incidentally, because those filers' rows are all 20-F and the carrier-form
      allowlist drops them. Pre-existing, not introduced by this arc.
  (e) 🟢 **Promote `kpi_store._dedup_key` / `_canonical_value` to public aliases.**
      `kpi_xbrl_ingest`'s disagreement guard reaches across into both private
      symbols — correct, because a local copy would silently drift from the store's
      own definitions, but the encapsulation is owed. A zero-behaviour alias beside
      each private definition plus four call-site flips; deliberately deferred
      because `kpi_store.py` was outside the arc's declared file scope.
  (f) 🟡 **In-batch disagreement is unguarded.** Two conflicting flat facts sharing
      a dedup key WITHIN one pack still reach `kpi_store.append`'s silent
      first-record-wins (`kpi_store.py:321-325`). The shipped guard is store-aware
      (cross-call) only. Unreachable through either producer today — one winner per
      filing upstream — so it would require a producer bug; ~5 lines to close by
      accumulating validated keys in-batch. RAISED 🟢→🟡 by the whole-branch
      review 2026-07-25: the reachability reason is sound, but cheap hardening
      inside a file this arc already owns should not hide behind 'unreachable
      today' when it guards the exact invariant the arc exists to protect on a
      one-way door.
  (g) 🟢 **`coverage.skipped_rows` merges gap types under one key** in the backfill
      lane, discriminated by `type`, where this module's convention elsewhere is one
      coverage key per gap type (`unclassifiable_periods`, `fetch_failures`,
      `axis_exclusions`, `top_line_gaps`).
  (h) 🟢 **`"accessions": [None]` violates the ONE DQC flag schema** when a skip
      flag names a row with no accession (`assert_dqc_schema`, `kpi_xbrl.py:270-280`,
      requires non-empty strings). Pre-existing across sibling flags in
      `sec_edgar_client.py`, not introduced here.
  (i) 🟢 **`kpi_tw_ingest` has no `## CLI (...)` section in
      `analysis-kpi/references/cli-reference.md`** — it is the only one of the
      twelve indexed persistence/compute scripts missing one (the file documents
      eleven). Pre-existing since 2.35.0 (the TW iXBRL arc), surfaced while
      reconciling the index count during this branch's close-out. Deliberately NOT
      closed here: writing it means reading the shipped `kpi_tw_ingest.py` CLI and
      documenting its real flags/exit codes, which belongs to the TW arc's file
      scope, not the top-line lane's. `analysis-kpi/SKILL.md` now DISCLOSES the gap
      in the CLI-reference sentence rather than stating a count that is wrong about
      one referent or the other — so closing this item also means deleting that
      disclosure clause.
  (l) 🟢 **A kpi_id collision aborts BOTH lanes for the WHOLE pack** — FILED AS
      DELIBERATE, not a defect. `ingest_pack` builds every point before appending
      any (`kpi_xbrl_ingest.py`, `_claim_kpi_id` raises during selector mapping),
      so one colliding dimensional signature refuses the pack's top-line lane too:
      the live INTC Lane B run of 2026-07-25 landed ZERO of 473 facts on a single
      Intel-Foundry signature collision. That all-or-nothing blast radius is arc
      (d)'s shipped design and the alternative is worse — partial ingest would
      leave an append-only store holding one lane of a pack, and the store's dedup
      key would silently keep the FIRST of two colliding series, which is exactly
      the one-way-door data loss the guard exists to prevent
      (`docs/loom/memory/derived-durable-id-slug-is-a-lossy-one-way-door.md`).
      Fail-loud beats a silent discard on a durable store. Revisit ONLY if a real
      pack is found where a genuinely-distinct collision coexists with an
      otherwise-healthy top-line lane AND the operator cannot re-run after fixing
      the producer; the fix would then be per-lane isolation of the claim map, not
      a weaker guard. Raised by the whole-branch review 2026-07-25 while closing
      the over-fire that made the blast radius visible.
  (j) 🟡 **The New-Year guard misses a two-sided divergence along the dei NOMINAL
      fiscal-year end** (`sec_edgar_client.py::_is_near_new_year_boundary`). The
      shipped guard is one-sided along `period_end` — correct, and it recovered the
      whole December-filer backfill — but the two lanes' labels diverge along a
      SECOND axis the guard cannot see: the filing's `dei:CurrentFiscalYearEndDate`,
      which drifts per filing for 52/53-week filers. When that nominal sits in early
      January and the row's actual end fell back into late December, Lane B
      (`_derive_fiscal_label`) walks FORWARD to the January nominal and answers the
      next year while Lane A answers the period-end year; the guard does not fire
      and no coverage reason is emitted. Measured against both real label functions
      (2026-07-25): `2024-12-28` / nominal `--01-03` → Lane A 2024, Lane B 2025 FY;
      `2025-12-31` / `--01-02` → Lane A 2025, Lane B 2026 FY. Cost is a MISLABELLED
      year, not an absent one — the two lanes then key one fiscal year two ways and
      the store shows a spurious restatement dagger from a single filing, which is
      exactly the failure the two-lane e2e's docstring names.
      **Why Lane A cannot close it alone:** the guard's whole premise is that this
      lane has no dei calendar, and its `companyconcept` rows carry only
      `{start, end, value, accn, form, fy, fp, filed}` (`summarize_concept`). None of
      those varies with the nominal — a 52/53-week year is 364/371 days whatever the
      nominal — and `fy`/`fp` are the CARRYING filing's focus, not the fact's
      (measured over all 777 `concept_*.json` files in the local EDGAR cache
      2026-07-25 — split across two cache-envelope payload shapes, 480 files with
      the body at `data` and 297 nested one level deeper at `data.data`; a re-run
      must cover both or it silently drops whichever shape it doesn't parse —
      predicate stated so it can be re-run: us-gaap `companyconcept` payloads, rows
      as `summarize_concept` reshapes them, `start`/`end`/`accn`/`filed` present and
      `fy` an int, `end - start` within 340-380 days — 10175 of 15276 such annual
      rows, 66.6%, carry an `fy` differing from `end`'s own calendar year). So a
      late-December row from a January-nominal filer is indistinguishable here
      from a plain December filer's row, and narrowing the guard on this axis
      is not available to the producer.
      **What would close it:** the same consumer-side work as item (a) — both reduce
      to Lane A having no calendar, so the fix belongs where the two lanes' calendars
      MEET (`pack_us.py:1017-1019` merges both into one envelope). Once Lane B's
      per-accession `fiscal_calendars` are in hand beside Lane A's facts, a consumer
      can re-label or quarantine a Lane A year whose Lane B calendar puts it in a
      different fiscal year. A producer-side alternative exists but is partial and
      was NOT taken: `fy` IS authoritative on a row that is its own filing's
      current-period fact, so grouping rows by accession could recover the nominal
      label for years whose own 10-K is still in the API's XBRL window (~2009+) —
      it does nothing for the older comparative-only years that are this lane's
      reason to exist, and it would mean reading `fy`, which this module forbids by
      name. Filed as its OWN item rather than folded into (a): they share a root
      cause but not a failure mode (that one silently affirms "shared basis" between
      two unstated calendars; this one mislabels a year) and not a fix site, and
      folding a live mislabeling hazard into an unreachable-today entry would bury
      it. Sequence it WITH (a) when the consumer-side calendar work is picked up.
      Documented at the four producer sites + `data-markets/SKILL.md` +
      `investing-toolkit/CHANGELOG.md` (2026-07-25) rather than left implied.
  (k) 🟢 **`_is_near_new_year_boundary` is misnamed** — it no longer means "near"
      (symmetric proximity), it means "has crossed into January". The docstring
      compensates; the name does not, and a symmetric-sounding name on an asymmetric
      guard is precisely the shape
      `docs/loom/memory/a-test-can-pin-behaviour-with-a-false-rationale.md` §2 tells
      us to hunt. Deliberately NOT renamed in the doc-only round that found (j): a
      coherent rename also drags the pinning test's NAME
      (`test_near_new_year_skip_leaves_lane_b_the_sole_authority`), a local in
      `test_sec_edgar_top_line_backfill.py:277`, and three narrative docstrings in
      `test_top_line_two_lane_e2e.py` (:71, :110, :396) — leaving any behind
      desynchronizes the vocabulary, which is its own drift surface. Behaviour-
      preserving; wants one sweep + a suite run, not a prose commit.

## investing-toolkit US XBRL→kpi_store producer 2.34.0 — post-ship follow-ups (OPEN)
- Status: OPEN
- Start: next substantive touch of `analysis-kpi/scripts/kpi_xbrl_ingest.py` or the
  next US-XBRL-lane arc.
- Origin: arc (d) US XBRL→kpi_store producer (branch feat-kpi-xbrl-store-producer,
  2.34.0, 2026-07-25); whole-branch review PASS_WITH_NOTES + per-task 🟢 findings,
  logged not fixed. Brief/plan `docs/loom/{specs,plans}/2026-07-24-kpi-xbrl-store-producer.md`.
- What:
  (a) ✅ **RESOLVED by the 2.37.0 identity arc — struck 2026-07-26.** This item said
  the collision guard keyed on a finer identity than the store, and that
  `derive_kpi_id` was consolidation-blind. Both were fixed on branch
  `feat-kpi-id-consolidation-axis`: `_signature_key` normalizes the consolidation
  qualifier through the consumer's own rule (2.36.0), and `derive_kpi_id` now takes
  the qualifier and gives a NON-default member its own token (`e60a0745`). Its
  prescribed remedy ("normalize consolidation in `_signature_key`, or compare
  NORMALIZED signatures in the guard") is what shipped. Kept as a struck line rather
  than deleted because (b) and (c) below are still open under this same heading.
  (b) 🟢 `kpi_xbrl_ingest.py` has NO try/except wrapper — a bad `--pack` / malformed
  JSON / a fact-pack missing both ticker+company surfaces as a raw traceback (exit 1),
  unlike sibling scripts' clean-message convention. Add clean error handling on next touch.
  (c) 🟢 `_real_shaped_pack`/`_FY2020_PERIOD_START` duplicated across
  `test_kpi_xbrl_ingest.py` + `test_kpi_xbrl_to_tearsheet_e2e.py` (2nd occurrence —
  Rule of Three). Lift to a shared `conftest.py` fixture at the 3rd caller.

## investing-toolkit TW KPI producer 2.35.0 — post-ship follow-ups (OPEN)
- Status: OPEN
- Start: next substantive touch of `analysis-kpi/scripts/kpi_tw.py` /
  `kpi_tw_ingest.py`, or the next TW-KPI-lane arc.
- Origin: TW-market kpi_store producer (branch tw-kpi-store, 2.35.0, 2026-07-25);
  brief/plan `docs/loom/{specs,plans}/2026-07-25-tw-kpi-store-producer.md`.
- What:
  (a) 🟢 **glue-free TW envelope production** — a `pack_tw` verb emitting
  `{canonical, facts, coords}` (mirroring `pack_us.pack_kpi_quarterly`), so TW is
  "ticker→tearsheet without glue" like US. Today `run_pipeline` emits `canonical`
  but NOT `facts` (the `as_of` authorisation date lives in a fact), so the ingest
  consumes an envelope the caller assembles; the dogfood assembles it by hand. A
  data-markets envelope task closes this.
  (b) 🟢 **`tw_canonical_to_points` `zip(values, periods)` truncation** — a
  `zip` silently truncates if the two lists diverge in length; a len-assert would
  fail loud instead. Unreachable today (the canonical layer builds values and
  periods in parallel), but a future canonical change could desync them silently.
  (c) 🟢 **mirrored injective guard keys on bare field-name** — the collision
  guard keys `claimed_by` on the bare field-name, not `(statement, field)`. A
  field-name recurring across two statements would RE-CLAIM (merge) rather than
  raise. Unreachable today (the emitted field names are disjoint across
  statements); key on `(statement, field)` when a real cross-statement name
  appears.
  (d) 🟢 **wire the TW KPI store into report-equity-memo Phase 3.5** — like the
  US chain feeds the memo's quarterly-KPI section, the TW store should surface in
  the TW memo path. Deferred (out of this producer-only arc).
  (e) 🟢 **point `unit` is per-field best-effort** — `tw_canonical_to_points`
  copies `unit` from `_meta[field].get("unit")`; a canonical field whose `_meta`
  lacks `unit` silently yields `unit=None` (same class as the shipped TWD fix,
  per-field). Non-fatal (the dogfood path carried TWD); consider a fail-loud or a
  canonical-wide TWD default when a TW field's unit is absent.

## investing-toolkit `source_kind` naming debt — endpoint-name axis vs shape axis (OPEN)
- Status: OPEN
- Start: the next rename/migration touch of a `source_kind` stored value —
  NOT a plain next-touch of the two named files, since either rename is a
  durable-store migration (existing points already carry the value), not a
  code edit.
- Origin: company total (top-line) revenue lane arc (branch
  feat-total-revenue-lane, 2026-07-25); plan
  `docs/loom/plans/2026-07-25-company-total-revenue.md` §Notes "Known naming
  debt, deliberately NOT fixed in this arc" + Task 11's RFC 6648 / BCP 178
  evaluation (uniform "ours" prefixes carry zero discriminating information
  and must be renamed once a value becomes de facto standard — exactly the
  situation a durable-store rename creates).
- What: this arc pinned the `source_kind` vocabulary shape mechanically
  (`kpi_gate.TRUSTED_SOURCE_KINDS` now asserts every trusted member starts
  with the trust-class segment `xbrl-`), but two pre-existing values already
  violate the `<trust-class>-<lane>` shape and were deliberately left unfixed:
  (a) 🟢 `xbrl-companyfacts` names a specific SEC REST endpoint
  (`data.sec.gov/api/xbrl/companyconcept/...`), yet
  `kpi_tw_ingest.py:54` reuses the identical literal for TW MOPS iXBRL
  ingestion, where no such endpoint exists at all — its second segment mixes
  an endpoint-name axis with the shape axis the other trusted values
  (`xbrl-dimensional`, `xbrl-topline`) use.
  (b) 🟢 `kpi_prose_candidates.py:433,697` mints a bare `"prose"` value with
  no trust-class segment at all. It sits OUTSIDE `TRUSTED_SOURCE_KINDS` (an
  untrusted lane), so this arc's convention-pin test does not touch it, but
  it is the same naming inconsistency one axis over.
  Both are cheap to rename in code but expensive to rename live — either
  change requires a durable-store migration (backfill already-stored points
  under the old literal) rather than an edit, which is why this arc shipped
  them as documented debt instead of silent drift. Revisit when a
  TW-specific or prose-specific trust class is introduced (the natural
  rename point) or when a store migration is separately budgeted.

## investing-toolkit quarterly 2.22.0 — post-ship follow-ups (OPEN)
- Status: OPEN
- Start: next touch of `investing-toolkit/skills/data-markets/scripts/sec_edgar_client.py`
  or `analysis-kpi/scripts/kpi_xbrl.py`.
- Origin: scope-B quarterly rebuild (branch feat-operational-kpi-quarterly,
  2026-07-18); whole-branch review PASS_WITH_NOTES ship-as-debt rulings +
  T9 spec-reviewer follow-up.
- What: (a) split `extract_dimensional_revenue` (~355 lines, the one 🟡);
  (b) thread the REAL `filing.form` string into the fact pack so the analysis
  layer stops inferring `source_form` from dei focus; (c) public alias for
  `_dimension_quarterly_absence` (cross-layer underscore bind); (d) call
  `assert_dqc_schema` at kpi_xbrl's data-layer-flag ingestion point (~:464);
  (e) 🟢 nits: selection-gap slot overwrite, literal 'None' in gap reason,
  accession-less 10-K coverage entry.

## investing-toolkit memo-wiring 2.23.0 — post-ship follow-ups (OPEN)
- Status: OPEN
- Start: next touch of `report-equity-memo/references/schema-phase4-input-bundle.json`,
  `analysis-kpi/scripts/kpi_memo_feed.py`, or `data-markets/scripts/pack.py`.
- Origin: memo quarterly-KPI wiring slice (branch feat-memo-quarterly-kpi-wiring,
  2026-07-18); per-task + whole-branch review ship-as-debt rulings.
- What: (a) the one 🟡 — schema↔envelope coupling unguarded: nothing asserts
  `schema-phase4-input-bundle.json`'s kpi_quarterly_feed required-set equals
  the envelope `build_quarterly_memo_feed` actually emits (both sides pinned
  separately, can drift green-green) — add a coupling assertion or route a
  real feed through the B2 validator; (b) pack.py PEP 723 header declares no
  deps while pack_us direct-imports sec_edgar_client — bare `uv run pack.py`
  crashes on ModuleNotFoundError for EVERY networked pack incl. Phase 1
  memo-fetch (pre-existing, live-confirmed 2026-07-18); cheap hardening =
  add requests/edgartools pins to pack.py's header (touches all packs, needs
  its own review); (c) 🟢 nits: build-quarterly CLI exit-1 arm untested;
  non-dict series entries raise AttributeError not ValueError; `_is_blank`
  dup vs tier-① idiom; mixed-company sample fixture caveat; jsonschema-absent
  silent skip in test_pack_schemas; no socket guard in chain test; module-scoped
  sys.modules fixture no teardown; `${MEMO_DATE}` defined only in Phase 3.5;
  doc wording "concept" vs real field `kpi_id` in schema prose + CHANGELOG.

## investing-toolkit 52/53-week filer support 2.24.0 — post-ship debt (SHIPPED 2026-07-19)
- Status: SHIPPED (feat-52-53-week-filer-support; recon verdict (b) — facts
  existed, two gates dropped them; live validation: COST 11 derived Q4
  points recomputed exact vs press releases; AAPL/NVDA anchors byte-stable;
  bonus find: AAPL's genuine 14-week FY2023-Q1 got week_normalized_yoy
  correctly). Plan: docs/loom/plans/2026-07-18-52-53-week-filer-support.md.
- Debt (all 🟢, fire on next touch of the named file):
  - kpi lane: `_duration_months`/`_duration_weeks`/`week_lane_band` each
    re-parse period dates via `_duration_span_days` (2-3 parses per fact) —
    single computed span pass-through if the path ever gets hot
    (sec_edgar_client.py, T1/branch review nit).
  - e2e: real-COST Q4 assertion recomputes from the fixture's own operands
    instead of an independently-pinned literal
    (test_kpi_xbrl_quarterly_e2e.py, T6 nit).
  - protocol: "Walmart-style" term overload vs the spec Out-of-Scope's
    "Walmart-style week-53→week-1 lookback" (deep-equity-research-memo.md,
    T7 nit); month-lane derived Q4 mints deliberately omit duration_weeks
    (byte-identical month lane) — revisit only if a consumer needs it.
  - report-equity-memo SKILL.md ~:385 pre-existing "Live-verified …
    AAPL/NVDA/COST" comment describes the 2.23.0-era COST refusal — reads
    stale now that COST classifies; one-line reframe on next touch.

## investing-toolkit 非金錢營運 KPI 自動化 (2026-07-19..20; Route B SHIPPED; ARC PIVOTED to a narrative-evidence layer; XBRL Route A demoted)
- Status: **Route B SHIPPED** (#590, 2.26.0). The committed next arc PIVOTED
  after a live big-tech probe (2026-07-20) — see the pivot note below — from
  "XBRL Route A" to a **source-anchored narrative+KPI evidence layer**, whose
  **Slice A Part 1 SHIPPED** (#593, 2.28.0) and **Part 2 SHIPPED** (this PR,
  2.29.0). XBRL Route A (footprint/capacity allowlist) is DEMOTED to a parked
  option for retail/REIT/utility filers only.
- **Pivot evidence (2026-07-20):** a live probe of the 7 mega-caps showed the
  XBRL footprint allowlist yields ~0 real operational KPIs for big tech (only
  traps: AMZN mwh hedge-notional, TSLA 20M pay-package milestone); the real
  operational KPIs live in 8-K earnings-release PROSE — which Route B's TABLE
  walker AND the bulk-narrative layer both drop (META Family DAP, GOOGL MAU,
  TSLA deliveries). An agent-project prior-art survey confirmed no popular OSS
  project does verbatim-anchored + longitudinal + human-confirm grounding — that
  triad is our differentiator. Research: `docs/loom/research/2026-07-19-*.md`.
- **Narrative-evidence arc — Slice A = "Route B for prose" (3-part split, user-approved):**
  - **Part 1 SHIPPED (#593, 2.28.0):** mechanical prose KPI producer —
    `exhibit_prose.py` (surface + `--locate`) + `kpi_prose_candidates.py`
    (propose/gate/confirm/commit_to_store/intake) → prose datum with verbatim
    quote + `prose:{start}-{end}` anchor into the byte-unchanged tier-① store.
    Change-folder `docs/loom/2026-07-19-8k-prose-kpi-intake/`, plan
    `docs/loom/plans/2026-07-19-8k-prose-kpi-intake-part-1.md`. NOT yet
    SKILL-wired (foundational machinery).
  - **Part 2 SHIPPED (this PR, 2.29.0) — number robustness:** word-scale
    (locator absorbs the magnitude word; value multiplier via `Decimal`, so META
    DAP "3.56 billion" is 3,560,000,000 not 3.56), one consistent normalization
    (nbsp/thin-space grouping, full-width + Arabic-Indic digits, full-width
    comma/period, curly quotes — every fold length-preserving so offsets and the
    anchor survive), date/fiscal-period label rejection, bounding-qualifier
    metadata, bounded provenance context window. Plan
    `docs/loom/plans/2026-07-20-8k-prose-kpi-intake-part-2.md`.
    **Three fabrication bugs of one class were caught in review** — a token whose
    anchor holds LITERALLY while being semantically meaningless (nbsp fusing two
    unrelated numbers; magnitude absorption reopening the period-label filter;
    nbsp after a comma-grouped number). The lesson for Part 3: `text[start:end]
    == token` is guaranteed by construction and therefore proves nothing about
    whether the match is semantically right. Two declared limits remain in the
    plan's §Notes (non-adjacent qualifier; same-clause PII proximity).
  - **Part 2 next-touch (2🟢 from whole-branch review, logged not fixed):**
    `_bounded_quote` re-anchors on the FIRST occurrence of a repeated token, so
    the re-clamped window can center on an occurrence other than the one
    `char_offset_span` names (still grounded, no fabrication); and
    `commit_to_store` never invokes `passes_substring_gate` — the gate is a
    predicate callers must remember to call rather than a barrier on the commit
    path (pre-existing from Part 1). Make it structural in Part 3.
  - **Part 3 must carry a SURFACE-VERSION marker.** Part 2 changed how the
    canonical prose surface is produced (newline fold + char folds), i.e. a
    silent surface-version bump. An audit confirmed this is SAFE today — no
    consumer re-derives the surface to re-check a stored offset, no committed
    fixture carries a `prose:` anchor, and the route is not SKILL-wired, so
    nothing is stored in anger. But the spec's own MUST (change-folder
    `spec.md:149-165`: store a content hash + flattener version, re-verify
    `quote == canonical_text[start:end]` on read) is exactly the mechanism that
    would have made this unsafe — and it is the one deferred to Part 3. When
    Part 3 builds the re-verifier it needs a policy/surface version marker, or a
    live store written under an older surface will drift undetectably.
  - **Part 2 next-touch, two more of the recurring class (🟢, logged not fixed):**
    the `--locate` CLI fuses a U+2028-separated file (a public entry point whose
    documented contract is canonical input, so input-conditional); and
    `<style>`/`<script>` text is not suppressed by the walker, so CSS/JS numerals
    enter the candidate stream (`10.5pt`, `720px`) — PRE-EXISTING at origin/main,
    0 of 4 real filings checked carry either tag.
- **investing-toolkit test-suite hygiene (found 2026-07-20, unrelated to the
  prose arc):** `test_pack_schemas.py::test_pack_live_output_matches_schema[kr-
  snapshot]` fails on `ModuleNotFoundError: No module named 'edgar'`
  (`sec_edgar_client.py:801`) — a MISSING OPTIONAL DEPENDENCY, not a network
  failure, but it is hidden by the `-m "not network"` deselect everyone runs. If
  the deselect list and the optional-dep set drift, this fails for a reason
  nobody is watching. Fits the repo's existing pytest-config-drift gotcha.
  - **Part 3 (next brief) — lifecycle/hardening:** table-vs-prose + prose-vs-prose
    + order-independent dedup, 8-K/A supersession, anchor drift (hash+version
    re-verify), concurrency scope + batch atomicity, resource bounds/ReDoS,
    prompt-injection, propose-failure state, human-edit-re-gate. 12 deferred
    scenarios in the change-folder §Notes.
  - **SKILL wiring** (analysis-kpi SKILL.md CLI-reference + a user-facing prose
    intake workflow) — pending; do when the capability is user-ready.
  - **Slice B (later) — curated narrative PASSAGES → memo** (relevance/taste
    layer over the existing bulk narrative text).
  - **Slice C — KPI observation history (US lane)** (plan
    `docs/loom/plans/2026-07-22-kpi-observation-history.md`, brief
    `docs/loom/specs/2026-07-20-kpi-observation-history.md`) — shipped shape:
    store enumeration; period identity = raw `(start,end)` pair with fiscal
    labels as analysis coordinates; write-time integrity stamp (hash of the
    anchored span + surface version); `history`/coverage read across filings,
    disagreement flagged. **Retention DROPPED** — the earlier ten-year-lookback
    "industry norm" framing was unevidenced (CFA sets no lookback window;
    practitioner guidance clusters 3–5yr; 会社四季報 prints 5 periods by default;
    vendors sell depth as product tiers — no consensus to conform to).
    **Tearsheet
    DEFERRED** — no shipped public format exists for "one company, many
    operating KPIs, many years", and the prose lane is not yet user-invocable.
  - **Slice C deferred / future items:**
    - Conflict-resolution policy (B) — different source types, same period:
      audited-wins auto-resolution, **data-gated** (needs a per-point
      source-TYPE field + a second populated lane before it can resolve on
      anything; today T6 surfaces a (B)-shaped conflict as `disagreement=True`).
    - Dedup-key migration — moving store identity to the `(start,end)` date
      pair at the write-side dedup layer (the 5-tuple still carries the string
      `period`); user-gated, backfill-blocked by first-record-wins.
  - **Pre-existing defects found during the Slice C recon (2026-07-22) — log,
    not fixed here (not ours, out of scope):**
    - `comps_compute._concept_fy_end` (`comps_compute.py:206-207`) hardcodes
      `fiscal_year_ends`, so a TW pack (which emits `periods`) returns `None`
      every time — provenance column silently blank, no error.
    - Values/periods can pair WRONGLY on a mid-series gap: `_extract` skips
      missing labels instead of appending `None`, then `_meta` slices
      `periods[: len(revenue)]`, truncating periods from the END
      (`pack_jp.py:232-236`/`:274`, `pack_tw.py:275`, `pack_kr.py:325`).
    - JP EDINET Tier-A canonical is an empty stub (`pack_jp.py:463-478`) — the
      better source produces the emptier canonical.
    - TW canonical blocks are absent from `tw-schema-memo-fetch.json` entirely.
    - The four `_YF_LABEL_MAP*` copies differ in content, so ADR-0001's CI MD5
      drift check covers none of them.
- **Route A — XBRL non-monetary footprint/capacity allowlist — DEMOTED/PARKED**
  (serves retail/REIT/utility filers, NOT big tech; only pick up if the user's
  portfolio needs those names). Census outcome — the only viable territory is a
  physical-footprint / capacity allowlist keyed on standard (not extension)
  concepts:
  - `us-gaap:NumberOfStores` — COST, CVS
  - `us-gaap:NumberOfRestaurants` — MCD
  - `us-gaap:NumberOfRealEstateProperties` — O (clean total), PLD
    (dimensioned); AMT is extension-only (excluded from the standard-concept
    allowlist)
  - utility generating capacity in MW — NEE, DUK, SO
  - program-unit counts — BA
  THREE mandatory defenses, each required before ANY allowlist promotion:
  (a) per-filer semantic verification — a standard concept can still be the
  wrong quantity (SBUX `NumberOfStores`=113 is a sub-brand trap, not the
  system total); (b) value-sanity gate — reject corrupted magnitudes (MET
  claims-count tagged 3,360 in one filing, 308B in another — a ~10⁸ jump
  that must fail loud, not pass through); (c) QName-keyed classification,
  never unit-string — 7/15 energy/utility filers tag hedge-notional
  bbl/mcf/MWh with units identical to real production volumes, so the unit
  string cannot disambiguate; classify on the concept QName. Route A DOES
  carry the per-point `currency` ISO-code passthrough rider (gate already
  reads it, drops it before emission — CSV/feed currently carries
  implicit-USD only) since Route A touches XBRL feed emission.
- FAR-PARKED, out of scope for BOTH routes: pre-2003 KPI extraction from
  10-K prose. Before the 2003-03 earnings-8-K furnishing mandate (then
  Item 12; renumbered Item 2.02 in 2004-08) there is no
  structured earnings-release exhibit to parse (Route B) and no XBRL fact to
  allowlist (Route A) — recovering those KPIs is a separate 10-K-text
  problem, not a variant of either arc here.

## investing-toolkit KPI tearsheet — multi-granularity + per-market period menu (OPEN)
- Status: OPEN
- Start: a real need to tearsheet a TW/JP company (monthly / half-year data), or
  the next substantive touch of `report-kpi-tearsheet` / `kpi_store`'s period
  classifier. NOT triggered by US-only annual+quarterly use — that works today.
- Origin: 2026-07-24 first real tearsheet dogfood (JNJ, US annual — CLEAN) then a
  mixed annual+quarterly probe surfaced that a flat date-sorted table interleaves
  granularities; user asked whether it should be per-market. Research:
  `docs/loom/research/2026-07-24-market-period-granularity-regimes.md` (PR #609),
  three regulator-primary-source agents (US/JP/TW/KR/CN) + a layout survey + a
  local `_qtrs` probe.
- What (the coupled design the research scoped — do NOT cut it into "annual vs
  quarterly", that was the US-centric assumption the research disproved):
  1. **Sub-quarter classifier, STORE-owned.** `_qtrs` refuses spans <1 quarter, so
     a monthly period gets a null `period_axis_key` and renders as an orphan
     column (12×N for N monthly KPIs — probe-verified). Extend the classifier to
     give monthly (and any sub-quarter) span a real identity. Belongs in the store,
     never the formatter (2.32.0 Decision: alignment identity is store-owned).
  2. **Per-market granularity menu**, not a global binary: US = annual+quarterly;
     TW = annual+quarterly+**monthly** (證交法§36, mandatory); JP = annual+
     **half-year** (the sole legally-mandated interim filing since the 2024 FIEA
     reform)+quarterly(cumulative, now exchange-rule); KR/CN = annual+half-year+
     quarterly(cumulative). No market files a standalone Q4; JP/KR/CN file no
     standalone Q2 — do NOT build Q4/Q2 collision handling for ingest.
  3. **Discrete-vs-cumulative axis** must surface in the rendered output — US/TW
     file both natively; JP, CN, and KR-through-Q3 file cumulative-only (discrete
     = derived by subtraction). Two columns that look alike but sit on different
     axes is the silent-lie class this repo keeps getting bitten by.
  4. **Layout**: separate views per granularity (a `--granularity` flag or
     distinct sections), never one date-sorted table — every shipped product
     surveyed (US terminals, 四季報, 株探) keeps them apart; none groups quarters
     under a year.
  Already-solid foundation (do not re-solve): the store's raw `(period_start,
  period_end)` identity already separates a cumulative Q3 from a discrete Q3
  unmodified — the hard cross-market case falls out of the observation-history
  date-pair decision.
- Sequencing note: this is the tearsheet successor in the longitudinal trilogy
  (tearsheet ✅ 2.32.0 → THIS / Part-3 hardening → replay-matrix). User-stated
  intent (2026-07-24): decide priority against Part 3 after more real tearsheet
  use; the monthly gap only bites on TW/JP data, so US-only use does not force it.

## investing-toolkit quarterly — JNJ RestatementAxis signature blind spot (SHIPPED 2026-07-19, 2.25.0)
- Status: SHIPPED (feat-jnj-restatement-axis-signature; both fix shapes
  landed — ①vintage/unknown/conflict axis exclusion-with-count +
  `period_recast` memo flag ②`signature_refused` per-signature refusal —
  plus the live-sweep-discovered ConsolidatedEntitiesAxis promotion
  [INTC sibling-axis synonym, member-semantics-verified]. 12/12 tickers
  TRUSTED, 25/25 anchors exact; JNJ revived 373 series/511 derived Q4
  with recast annotation; INTC healed 9 wny restored. Post-ship debt:
  🟢 double `_dimension_signature` recompute per rejected fact
  (memoize on next producer touch); 🟢 `currency` ISO passthrough rides
  the non-monetary double-arc below.)
- What: `_dimension_signature` (sec_edgar_client.py ~:2073, shipped
  2.22.0/#583, untouched by the 52/53-week arc) whitelists only the 4
  breakdown axes + ConsolidationItems and silently DROPS
  `srt:RestatementAxis` — a prior-period reclassification adjustment fact
  (JNJ Q3-2024 Shockwave ±20M, acc 0000200406-25-000209) collapses onto
  the real fact's signature → resolve_binding's intra-filing-ambiguity
  fail-loud fires (correctly, facing FALSE ambiguity) → and the abort is
  whole-series: one poisoned signature refuses the entire ticker (feed
  exits on empty input).
- Fix shape (two independent pieces): (1) treat RestatementAxis like
  ConsolidationItemsAxis — a separate reconciliation qualifier, never a
  breakdown collapse (per
  docs/loom/memory/match-kpi-on-full-dimensional-signature-not-one-axis.md);
  (2) consider narrowing the abort granularity from whole-series to
  per-signature refusal-with-gap so one poisoned signature doesn't zero a
  ticker. Evidence artifacts: scratchpad sweep_JNJ_series.err +
  jnj_probe.py (session 2026-07-19, volatile).
- Otherwise the sweep validated the design everywhere: JNJ's pack layer
  classified 6,462/6,462 facts dual-lane with zero unclassifiable
  (drifting 13-week quarter-ends absorbed); INTC (also a 52/53-week
  filer) produced 9 correct week_normalized_yoy points (13-vs-14wk,
  hand-verified −23.38%).

## investing-toolkit quarterly — parked capability arcs (PARKED)
- Status: PARKED
- Start: (calc-linkbase) a real filer whose dimensional concepts genuinely
  lack "Revenue" and misclassify — insurance was the hypothesized case and
  its concepts already carry Revenue; (Form-NT) a user asks for
  not-yet-due vs overdue vs late distinction in coverage reports.
- Origin: rebuild-findings.md §REJECTED/parked (2026-07-17); archived
  change-folder docs/loom/archive/2026-07-18-2026-07-16-operational-kpi-quarterly/.
- What: (a) calc-linkbase "read the filer's own rollup" defense-in-depth
  layer; (b) Form-NT late-filing detection on SEC deadline regulation
  (10-Q +40/45d, 10-K +60/75/90d via dei:EntityFilerCategory).

## knowledge-triage v2.1 — mechanize enforcement semantics (COMMITTED-NEXT)
- Status: COMMITTED-NEXT (start condition MET 2026-07-18: second
  weak-model run reproduced the failure family in mutated form —
  see the dogfood report's leg 2)
- Origin: 2026-07-18 live dogfood, both weak-model legs
  (`docs/loom/dogfood/2026-07-18-knowledge-triage-live-spec-leg.md`);
  knowledge-triage arc PR #581/#582.
- What (diagnosis): across spec+design stations on haiku, the headline
  rule survives (landmines flagged domain-convention) but prose-only
  ENFORCEMENT SEMANTICS do not — leg 1: invented enum values, dropped
  SHAPING tier + gate language, hardcoded settlement-basis in REQ-002
  against its own flag; leg 2: enum held, SHAPING label kept but its
  consequence INVERTED ("do not block"), 締め日 silently assumed to
  calendar month. Vocabulary survives; enforcement dies in prose.
- Fix (three cuts, per pipeline-enforced-gates precedent):
  a. loom-spec `validate_spec_output.py`: `evidence_needed:` value
     whitelist (three pin values only); SHAPING|DEFERRABLE label
     required within each domain-convention tag's neighborhood;
     SHAPING without `deferred: <reason>` ⇒ nonzero exit (gate rule
     encoded mechanically). RED fixtures = the real leg-1 artifacts.
  b. loom-interface-design: design-critic gains a mechanical pre-check
     row (grep the artifact: out-of-enum tag values, or SHAPING marked
     non-blocking without `deferred:` ⇒ NEEDS_REVISION finding);
     one-line supplement AFTER the pin in both drafting references
     stating the SHAPING consequence inline (proximity for weak
     readers, extraction-severing precedent).
  c. loom-spec completeness-critic: consistency lens — proposal-level
     open flags vs spec.md requirement text that silently resolves the
     same question (leg 1's REQ-002; not mechanically checkable).
  d. loom-product-principles `validate_principles_output.py` (leg 3,
     2026-07-18): `evidence_needed:`/`— assumption:` marker whitelist
     when present + provenance check (Anchors rows claiming seed
     provenance must quote strings literally present in the seed —
     kills the fabricated-attribution variant). The unmarked
     target-invention evasion is judgment-shaped, NOT mechanizable —
     residual = interactive human ratification + downstream stations'
     own triage; labeled honestly, no grep pretends to catch it.
- Evidence note: leg 3 doubles as a natural control — within one weak
  run, every validator-enforced dimension survived and every prose-only
  duty died. The mechanize-the-consequences thesis is confirmed, not
  just inferred.
- Next-touch (from cut-d review, 2026-07-18): the `--seed` provenance
  check has no in-skill caller — product-principles has no persisted
  raw-seed-file convention, so Step 8 cannot pass the flag (T16
  spec-reviewer endorsed omission; live callers today = dogfood/CI
  harnesses holding the seed independently). Re-trigger: when
  loom-pipeline (or any headless driver) starts persisting its
  run-input seed to a fixed path, add a conditional pass-through
  sentence to product-principles SKILL.md Step 8. Also re-measure
  `_PROVENANCE_MIN_MATCH` (n=1, 3-char corridor) against the next real
  dogfood artifact.

## loom-code ask-triage 0.30.0 — live telemetry A/B (OPEN)
- Status: OPEN
- Start: ~2-4 weeks after 2026-07-14 (needs organic session volume on the
  shipped ask-triage hook + kickoff L1-lite harvest; same pattern as the
  ascii-graph re-run below — run both in one telemetry pass if timing
  aligns).
- Origin: PR #564 (loom-code 0.30.0 layered ask-autonomy defense);
  HANDOFF-2026-07-14 P2.
- Baseline: `docs/harness-audit/2026-07-22-bba-trigger-baseline.md`
  (07-01~07-22 pre-A/B measurement: 125 Ask events / ~15% bba coverage /
  sampled miss-rate ~25% of non-bba asks / ask-triage hook intercepts
  ≈19). Read it before running the A/B; reuse its grep patterns for
  comparability.
- What: session-log telemetry over `~/.claude/projects/**/*.jsonl` —
  mid-task ask turns that cite research/recommendation vs bare "X or Y?"
  asks, against the pre-0.30.0 baseline. Also the deferred hook-card
  escape-hatch sentence (PR #564 next-touch).
- Metric guards (from the baseline doc): (1) the primary metric is
  **bare-ask rate**, never bba invocation count — sampled gray-zone cases
  show inline briefings (question text carries stakes + mental model
  without invoking the skill), so invocation counts systematically
  undercount briefing behavior; count those as the cites-context leg.
  (2) Split legs at 07-08 (hook ship): the baseline doc's mixed-window
  numbers are overall baseline only, not the pre-hook leg. (3) The
  candidate B-leg hardening (triage-card line: bare non-trivial ask →
  lead with one stakes sentence) must be designed as a post-merge step —
  marketplace pulls GitHub main, so a feature-branch hook card is
  untestable pre-merge.

## Pocock loom roadmap — arcs C/D/E remainder (OPEN)
- Status: OPEN
- Start: C rides the next writing-lean.md / compression-catalog touch;
  D is schedulable any time (equivalence-gated slim round 2); E needs
  its own brainstorm arc.
- Origin: 2026-07-14 Pocock loom-* design review (5-option roadmap,
  user-approved order T8→B→C→D→E); arcs A (#565/#566/#568) and B (#569,
  loom-code 0.31.0 AFK research lane) shipped.
- What: C = Negation failure mode + sentence-level no-op test into
  skill-dev-toolkit writing-lean.md / compression catalog (two-currencies
  framing already shipped in A). D = equivalence-gated slim round 2 over
  requesting-code-review (4,325 w) + spec-expansion (4,113 w) + skill-judge
  (5,429 w, over-proxy pre-existing, disclosed in #566). E = wayfinder-style
  persistent decision map (mechanism research done 2026-07-14, needs its
  own brainstorm arc).

## AFK research lane (#569) next-touches (OPEN)
- Status: OPEN
- Start: next kickoff-briefing.md touch.
- Origin: PR #569 per-task + whole-branch reviews (all 🟢).
- What: unify §(b) "compact research packet" vs §(f) "worker packet" on one
  term; add one clause pinning arm-3 pin write timing (pre- vs
  post-approval); note "arm 1/2/3" numbering is kickoff-briefing-local
  convention (SDD §Asking the user SSOT has no literal numbering).

## slim-round-2 residue — skill-judge checklist ablation + Essence-drift guards (OPEN)
- Status: OPEN
- Start: ablation piece = next skill-judge touch, or when roadmap C ships
  writing-lean's sentence-level no-op test (whichever first); lockstep-test
  piece = next touch of either pointer paragraph.
- Origin: slim-round-2 branch whole-branch review (2 🟢) + further-slimming
  assessment (2026-07-15 session).
- What: (a) skill-judge Quick Reference Checklist (~330 w) is a compressed
  restatement of D1-D8 — a redundancy-trap candidate; run skill-refactor
  ablation mode (full-vs-ablated behavioral runs) before cutting/merging,
  never cut on intuition. (b) the "Essence:"/"in brief:" compressed
  restatements inside requesting-code-review's and spec-expansion's pointer
  paragraphs are a second drift surface vs their references/ files — add
  lockstep tests (same pattern as test_asking_user_briefing_escalation.py's
  threshold triple) if either pair drifts once.

## ascii-graph trigger fix — post-ship telemetry A/B re-run (OPEN)
- Status: OPEN
- Start: ~2-4 weeks after PR #529 + PR #530 merge (needs organic session
  volume on the shipped trigger card + preload).
- Origin: 2026-07-10 trigger-rate analysis session; brief
  `docs/loom/specs/2026-07-10-ascii-graph-trigger-fix.md`; dogfood
  `docs/loom/dogfood/2026-07-10-visual-trigger-weak-model-dogfood.md`
  (n=2/arm directional gate-check — the real A/B is this re-run).
- What: re-run the session-log telemetry (grep `~/.claude/projects/**/*.jsonl`:
  Skill invocations of `ascii-graph` vs assistant-drawn box-drawing lines
  containing CJK) against the 2026-07-10 baseline — 1/1042 organic firing,
  56 CJK hand-drawn sessions, family-relay.md Read 1/216, visual-companion.md
  0/56. Success = organic firing up, CJK hand-drawn share down. While there,
  triage the deferred debts recorded in both PR bodies (escape_for_json
  triplication, awk §(b.1) boundary, regex-vs-YAML description test).

## skill-creator-advance Case (c) gate inheritance ambiguity (OPEN)
- Status: OPEN
- Start: next structural redesign touching skill-dev-toolkit/skills/
  skill-creator-advance/SKILL.md (behavior change → route through
  skill-creator-advance's own redesign path, NOT skill-refactor).
- Origin: refactor/skill-creator-advance-token-slim equivalence runs
  (2026-07-13): all four independent runners (2 baseline + 2 candidate)
  flagged that the "Improving an Existing Skill" router's Case (c)
  structural-rewrite flow does not explicitly inherit Pre-Creation
  Gates 1/2, and there is no documented pattern for "shared library
  across split skills" despite the flat-folder rule making it a natural
  ask. Judge 3 marked the resulting gate-machinery divergence
  "uncertain" — pre-existing ambiguity, present in both pre- and
  post-refactor versions.
- What: decide whether Case (c) should explicitly run Gates 1/2
  (worth-it / smallest-end-state) before drafting a split, and add a
  documented shared-code-across-skills pattern (candidates surfaced by
  the runs: third skill via delegation contract / plugin-root module /
  duplicate-with-SSOT-note).

## Change-binding chain integration test (OPEN)
- Status: OPEN
- Start: next loom-code touch.
- Origin: Cluster B whole-branch review 🟡 (2026-07-10, PR #526). The
  parent designer/PM-loop implementation entry completed 2026-07-10:
  Cluster B shipped as PR #526, Cluster A (construction flow, Tasks
  1-7 incl. cold-operator dogfood ship gate, 4 PASS + 1 PARTIAL with
  F1-F3 folded back) shipped on branch
  `feat-loom-product-principles-construction-flow` — this debt item is
  the only survivor.
- What: no integration test exercises the spec→plan→coverage→archive
  CHAIN — a plan fixture with a real join key scored covered by
  `check_scenario_coverage.py`, then the same change-id archived by
  `archive_change_folder.py`. Grammar consistency verified manually;
  the test guards future drift. Add
  `loom-code/scripts/test_change_binding_chain.py`.

## Dogfood replay/eval harness for the principles construction flow (OPEN)
- Status: OPEN
- Start: several rounds of real L1/L2 data accumulated, or a regression
  suspicion the manual loop is too slow to chase.
- Origin: 2026-07-10 cold-operator dogfood close-out discussion — the
  user asked whether human-run dogfood records can become automated
  test / iteration material. Three human-grounded seeds already exist:
  pip-note-app (paper run,
  `docs/loom/dogfood/2026-07-10-designer-pm-loop-paper/`), quote-tool
  (simulated-user Target B,
  `docs/loom/dogfood/2026-07-10-weak-model-dual-dogfood/`), and
  meeting-transcriber (live cold-operator run — structured seed +
  verbatim transcript in
  `docs/loom/dogfood/2026-07-10-principles-flow-cold-operator/`
  `seed.md` / `transcript.md`).
- 2026-07-10 matrix update: a 5-seed synthetic corpus now exists
  (`docs/loom/dogfood/2026-07-10-principles-flow-seed-corpus/`, input +
  grader-only oracle pairs) and its first 6-run matrix is graded
  (`docs/loom/dogfood/2026-07-10-principles-flow-cold-operator/matrix-results.md`).
  Two residuals from that run — prose-named stack/canon → Anchors drops
  (5/6 artifacts) and the seed-walk self-report being observably FALSE
  (seed5) — are now covered mechanically; see the 2026-07-11 update
  below.
- 2026-07-11 update: L1 (regression matrix Workflow,
  `.claude/workflows/principles-replay-matrix.js`) and L2 (mechanical
  traceability gate,
  `loom-product-principles/scripts/check_seed_traceability.py`) shipped
  on branch `feat-principles-replay-loop-l1-l2`, closing both residuals
  above. Design SSOT: `docs/loom/specs/2026-07-10-principles-replay-loop.md`
  (§Level 1, §Level 2).
- 2026-07-12 update: the mechanical seed-coverage gate shipped (PR #545)
  — drafting agent authors `seed-inventory.md` at reading time, the
  PIPELINE runs `check_seed_traceability.py` (headless: matrix courier;
  interactive: SKILL.md Step 8), verbatim miss list feeds ONE fix-agent
  round. Acceptance 4/18 (22%) → 8/12 (67%); the fix round cleared
  43/43 caught misses (baseline:
  `docs/loom/dogfood/2026-07-12-mechanical-seed-gate-baseline/`). The
  residual failure class is now inventory OMISSIONS at
  extraction-at-reading time — displaced upstream, not eliminated.
  Inventory quality is the current improvement frontier (recorded
  next-arc candidate: independent second extraction agent diffed against
  the first, or extraction-checklist emphasis on deferred/stance items;
  re-trigger: omission failures capping the pass-rate in future runs).
- What: Level 3 — the autonomous improvement loop (matrix → grade →
  implementer proposes a SKILL.md fix → review → re-run) — is now
  BUILT: `.claude/workflows/principles-improve-loop.js` (saved workflow
  `principles-improve-loop`), brief SSOT
  `docs/loom/specs/2026-07-11-principles-replay-l3-loop.md`. Design
  history remains at `docs/loom/specs/2026-07-10-principles-replay-loop.md`
  §Level 3 — do not restate it here. `skill-dev-toolkit:skill-tuning`
  remains the candidate variant-diversification engine, deliberately
  NOT wired in yet. Re-evaluation note (2026-07-12): its recorded
  re-trigger (single-fixer plateau — per the L3 brief's §Decision) was
  formally MET on 2026-07-11 (L3 run2 hit the plateau brake after
  consecutive rejected rounds,
  `docs/loom/dogfood/2026-07-11-l3-loop-run2/`), but the plateau's
  underlying failure class was resolved by the mechanical seed-coverage
  gate (PR #545), not by fixer diversification — so meeting the trigger
  does NOT activate this entry; it needs a NEW plateau observed on
  post-gate L3 runs before wiring in. Two
  still-unbuilt reuse tiers from the original
  discussion remain adjacent open ideas, not folded into L1/L2/L3:
  simulated-user replay (answer-bank + correction-events from the
  transcripts driving a simulated user that injects recorded
  corrections) and judge rubric (the graded reports' 5 criteria +
  B1-B6/F1-F7 findings as labeled ground truth for an LLM judge).
  Division of labor, agreed with the user: mechanical/regression
  coverage goes automatic; NEW failure-mode discovery and taste calls
  stay human — simulated users are systematically agreeable and miss
  owner-only corrections (ground truth lives with the human; both
  live runs proved read-back catches what simulation would wave
  through). When a SECOND station ships a headless/seeded mode,
  promote the seed-traceability invariant from product-principles
  SKILL.md to a family-shared convention (n=1 today, deliberately
  station-local). Calibration DONE 2026-07-11 (3 matrix runs, 18
  artifacts, stable-fragment + `|`-alternative tokens; committed
  baseline: `docs/loom/dogfood/2026-07-10-principles-flow-seed-corpus/calibration-baseline-2026-07-11.md`).
  Grade-courier robustness (stage-throw guard) shipped 2026-07-11 on
  branch `feat-replay-matrix-stage-guard` — both stage bodies in
  `principles-replay-matrix.js` now catch stage errors into degraded
  failed rows instead of `pipeline()` dropping the seed to null. The
  other harness next-touch candidate, anchor-match precision
  (`check_seed_traceability.py` restricting anchor match to the
  first/canon-name cell), is DEFERRED — see
  `docs/loom/specs/2026-07-11-replay-matrix-stage-guard.md` §Companion
  decision for the reason (n=1 observed false-negative, under-report-only,
  no mechanical rule yet separates it from a reproduced true positive);
  revisit when L1 data shows drop-signal distortion attributable to it.

## loom-code replay matrix — per-change objective regression measurement (OPEN)
- Status: OPEN
- Start: user commits to the arc; or the next wave of loom-code skill-text
  changes where "did this make it worse?" is asked without a measurement to
  answer it.
- Origin: 2026-07-23 discussion (purpose aligned: objective per-change
  better/worse measurement, not one-shot evaluation); survey + seed inventory
  in `docs/loom/research/2026-07-23-loom-mechanism-quantitative-eval-methods.md`.
- What: generalize the `principles-replay-matrix` pattern (fixed seed corpus →
  haiku headless replay → mechanical grading from exit codes only → per-seed
  win/loss/tie + pass-rate, n≥2 replicates, eval semantics never CI) to
  loom-code. Scope is smaller than it looks — the corpus raw material already
  exists (~30 seed-grade items): 26 probe rows in
  `docs/loom/audits/2026-07-16-loom-weak-model-behavioral-audit.md`, the
  git-checkable review-quality oracle in
  `docs/loom/dogfood/2026-07-06-g4-sonnet-vs-fable-ab.md`,
  `docs/loom/firing-corpus/*.jsonl` (reuse as-is), the waiver-pressure probe
  (2026-07-20 audit §5), and pipeline-driver F4. Work = normalize probes into
  seed/oracle pairs + copy the replay-matrix workflow + wire loom-code's
  existing mechanical gates as graders. Red/green discipline per change: the
  targeted failure enters the corpus RED first; effectiveness = new seed
  GREEN + zero old-seed regressions + cost delta. Floor-only honesty: this
  measures stability (known failure modes), not output quality — quality
  stays with blind A/B (`skill-tuning`) / rubrics / human read, ratcheting
  the floor via new seeds after each discovered quality failure. Standing
  habit effective immediately (pre-arc): every new dogfood/live failure is
  recorded as a seed+oracle pair in `docs/loom/dogfood/`, so the corpus
  accretes before the harness exists. Cross-ref: the entry above reserves
  promoting the seed-traceability invariant to a family convention when a
  second station ships a seeded mode — this arc shipping fires that trigger.

## bba trigger calibration loop — needs a two-sided metric (PARKED)
- Status: PARKED
- Start: after the ~2026-07-28 deployed-surface telemetry A/B reports an
  organic BARE-ASK RATE (baseline
  `docs/harness-audit/2026-07-22-bba-trigger-baseline.md`) — and only if that
  measurement shows the shipped cards still under-fire. Building before then
  means tuning against the pre-merge weak-model dogfood, which is directional
  only (5 rounds, hand-picked scenarios).
- Origin: bba proactive-trigger-hardening arc (2026-07-25, PR #613 → cf332584).
  After round-over-round dogfood iteration visibly moved the firing rate, the
  user asked whether the same method could iterate indefinitely to raise it
  further; offered, left undecided at close-out, parked here in the follow-up
  hygiene session.
- What: a bba-specific replay-matrix + improve-loop pair mirroring
  `principles-replay-matrix` / `principles-improve-loop` (fixed seed corpus →
  haiku headless replay → mechanical grading → ONE fixer edit per round,
  accepted only on a verified win + confirmation re-run + held-out smoke →
  proposal branch, never pushed), applied to the bba trigger wording now
  carried by `loom-code/hooks/router-card.md` rule 5, the four design-side
  `using-*` routers, and the `dev-workflow:brief-before-asking` description.
- **Load-bearing constraint — the metric MUST be two-sided**: brief-when-
  warranted UP *and* brief-on-trivial DOWN, graded on held-out scenarios kept
  out of the tuning corpus. A one-sided "did bba fire?" counter is precisely
  the metric the 07-22 baseline rejected: a loop optimizing it converges on
  over-firing, degrading every trivial ask into a briefing — the failure mode
  the user's own plain-language rule calls out ("not a license to over-brief").
  Without the held-out split the loop overfits its own seeds.
- Cross-ref: this is a narrow instance of the loom-code replay matrix entry
  above. If that general arc ships first, this becomes a seed-corpus + grader
  addition to it, not a second harness.

## Operationalize "product-shaped" in family reception (OPEN)
- Status: OPEN
- Start: next time any session or dogfood cold-reader again reports
  guessing at whether work is "product-shaped" vs "an increment" (one
  more occurrence past the 2026-07-10 loom-discovery dogfood, per the
  two-occurrence rule).
- Origin: loom-discovery dogfood
  (`docs/skill-dogfood/2026-07-10-loom-discovery/report.md` FINDING-010)
  — three independent cold-readers flagged "product-shaped" as never
  operationalized; it gates on-ramp rows 1 AND 4, so the ambiguity is
  family-wide, not loom-discovery's.
- What: add a one-line decidable test (or 2 worked examples) to
  `loom-pipeline/hooks/family-reception.md` — mind the 60 non-empty-line
  budget enforced by `test_pipeline_reception.py`; may need to land in
  the entry skills' §Intake instead.

## Grounding notes for sibling stations' claude-code-tools.md (OPEN)
- Status: OPEN
- Start: next touch of loom-spec or loom-interface-design references/.
- Origin: loom-discovery SDD Task 3 code-quality review (2026-07-10) —
  loom-discovery's claude-code-tools.md now carries a verified-against-
  frontmatter grounding note; loom-spec's and loom-interface-design's
  equivalents lack one (same gap, inherited convention).
- What: add the same one-paragraph grounding note (verification date +
  evidence grain) to each sibling's references/claude-code-tools.md.

## On-ramp row 4 vs rows 2/3 precedence unstated (OPEN)
- Status: OPEN
- Start: a real session where discovery and interface-design/spec
  on-ramp rows fire together and the session visibly picks wrong (the
  row-4-vs-row-1 case is already resolved in the reception file).
- Origin: loom-discovery dogfood FINDING-007 + router cold-reader
  (2026-07-10); Probe A q9 live-confirmed the adjacent row-4-vs-row-1
  seam splits 50/50 at description level.
- What: one precedence sentence covering row 4 vs rows 2/3 — but the
  reception file sits exactly at its 60-line budget, so this likely
  lands in `using-loom-discovery` §Intake as a tie-break note instead.

## Automate research-toolkit's sync-primitives.sh (PARKED)
- Status: PARKED
- Start: a second real drift incident (a synced primitive shipped out of
  sync with its SSOT and reached `main` before CI's MD5 drift gate
  caught it — not just failed a PR check, actually merged wrong). One
  incident (PR #519) was caught by the existing CI gate before merge,
  which is the gate working as designed, not a failure of it.
- Origin: raised during review of
  `docs/loom/specs/2026-07-08-deep-deep-research-fact-opinion-classification.md`
  (2026-07-08) — an external critique suggested moving
  `research-toolkit/scripts/sync-primitives.sh` from a manual step
  (backstopped only by a CI-side MD5 drift gate) to a git pre-commit
  hook or build-pipeline dependency, for local "fail loud" instead of
  async CI-only catch. Valid idea, evaluated and deliberately deferred
  from that brief because it targets the *pre-existing, repo-wide*
  SSOT-sync convention shared by every synced primitive in
  `research-toolkit` (not something that brief's `claimType` change
  introduced) — out of scope for a single-feature brief.
- What: if triggered, add a local pre-commit hook (or equivalent) that
  detects an edit to a declared SSOT primitive
  (`research-toolkit/skills/deep-deep-research/scripts/{schemas,rank,prompts,dedup}.py`)
  and either auto-runs `sync-primitives.sh` for the known sibling skills
  or blocks the commit until it's run manually. Keep the existing CI MD5
  gate regardless — this is a local speed-up, not a replacement for the
  CI backstop.

## Mechanical reminder hook for docs/loom/memory-worthy trailers (PARKED)
- Status: PARKED
- Start: the "trailers written but docs/loom/memory not checked" lapse
  (documented only in this session's private machine-local auto-memory
  as `feedback_fold_repo_memory_writes_into_same_branch_pr.md` — not yet
  promoted to a repo-committed `docs/loom/memory/` entry) recurs a THIRD
  time even after PR #521's fix (the
  finishing-a-development-branch Step 6/Step 8 re-sequencing). Two
  occurrences (PR #519, PR #520) already triggered the process fix in
  #521; a third occurrence AFTER that fix is the signal this needs
  mechanical backup, not just better sequencing.
- Origin: PR #521 review discussion (2026-07-08) — an external critique
  suggested a `PostToolUse` hook enforcing this "100% declaratively";
  evaluated and deliberately deferred, not built, because (a) PR #521's
  process fix hasn't had a single real-world data point yet, (b) "is
  this content memory-worthy" is a semantic judgment a hook can't
  reliably make — at best a heuristic reminder (git-memory returned a
  non-empty trailer set AND no docs/loom/memory/ file touched in this
  commit → warn), which risks false-positive noise on the many routine
  commits that correctly have local-only trailers.
- What: if triggered, build a lightweight `PostToolUse` hook on `git
  commit` that fires the heuristic above as a non-blocking reminder
  (never a hard block — the judgment call stays with the agent/user).
  Do not attempt to make the memory-worthiness decision itself
  mechanical.

## Mechanical-gates v2 candidates (loom-code 0.23.0 follow-ups)
- Status: OPEN
- Start: first fatigue evidence from daily use of the push gate, or next
  git-guard touch — whichever comes first
- Origin: PR #492 final verdict (2 🟢 next-touch) + its Decision trailers
- What: (a) waiver `scope` field checked on the read side (single-scope
  today); (b) git-guard docstring limitations list gains the
  `git -c core.hooksPath` route; (c) **patch-id relaxation** of the
  strict-HEAD-sha review marker — today ANY post-verdict commit forces
  re-review or waiver, which is correct for content changes but costly
  for message-only amends; relax to diff patch-id match if re-review-on-
  amend proves too expensive. First candidate friction datum
  (2026-07-04): docs-only microbranches face the same full
  review-or-waiver cost as code branches.

## TDD Guard pilot + TDD-mining tightenings
- Status: OPEN
- Start: first real SDD venue — same trigger as G4 / Segment-3
  (komado-Viewfinder batch6)
- Origin: harness-engineering audit rec 4
  (docs/loom/audits/2026-07-04-harness-engineering-audit.md) + the
  2026-07-04 three-route TDD-miss mining
- What: mount nizos/tdd-guard (or a loom-built equivalent: hook
  guarantees the check fires, LLM judges) on one real SDD run; measure
  latency / spend / false-block rate → adopt-vs-build decision. Bundle
  the two mining-derived tightenings into the same touch: reviewer
  tests-dimension must flag a zero-new-test feature branch on
  non-carve-out code (miss 3: whole-branch PASS never flagged it), and
  tdd-iron-law carve-outs must be DECLARED before coding, not claimed
  post-hoc (miss 2: "legacy backfill" framing for code shipped untested
  under the workflow's own banner).

## validate_design_output.py dual-root mode
- Status: UPSTREAM (loom-interface-design)
- Start: next loom-interface-design touch
- Origin: live-verify finding 4 (report
  docs/loom/dogfood/2026-07-04-loom-pipeline-v1-live-verify.md); the
  validator assumes DESIGN.md + ui-flows.md are colocated, but the
  sanctioned layout (audit #472) splits product-level vs per-change —
  exit 1 is structurally guaranteed. Needs --design-root/--flows-root
  (or equivalent) arguments.

## Segment-3 first live run
- Status: OPEN
- Start: first real change (deliberately NOT burned on a toy — agreed
  2026-07-04; dispatch machinery already proven by the F5 spike and the
  2026-07-03 dogfood)
- What: SDD triads via agentType + whole-branch review + conditional
  ui-verification, driven by the merged driver against a real repo.

## duration-override test affordance → interaction-flows enumeration
- Status: OPEN (original 值得做 list item 4)
- Origin: ui-verification first live run (PR #477 dogfood note) — 4
  states untestable behind a 25-minute wait; pipeline-produced apps
  should be required at design time to expose a test affordance.
  Candidate enumeration item for loom-interface-design:interaction-flows.

## Goal-oriented firing-corpus `expected` narrower than design
- Status: OPEN
- Start: next reuse of docs/loom/firing-corpus/goal-oriented.jsonl, or
  next firing-harness touch
- Origin: PR #489 residual; transcript-check requirement documented as
  trap #6 in the loom-code/scripts/loom_firing_harness.py module
  docstring
- What: every goal-oriented record expects `loom-code:using-loom-code`,
  so fired-skill grading alone cannot catch a design-side on-ramp
  regression (deleting brainstorming's Axis 0 would not move a single
  record off EXACT/FAMILY). The corpus's real acceptance criterion —
  whether the design-side recommendation SURFACES in the transcript —
  is not automated; any reuse must run the F3-style transcript check,
  or the corpus needs `expected` widened to the design-sanctioned set.

## Sibling plugin SKILL.md frontmatter versions lag plugin.json
- Status: OPEN
- Start: next version bump of any sibling plugin, or next touch of the
  manifest-drift tooling (.claude/hooks/check-codex-manifest-drift.sh)
- Origin: PR #490 loom-interface-design agent flag — drift lives in
  SKILL.md frontmatter, not READMEs, so #490's README pass left it
  unfixed
- What: SKILL.md frontmatter `version:` is stale across all three
  siblings (verified 2026-07-06): loom-interface-design 4× 0.3.0 vs
  plugin.json 0.4.1; loom-product-principles 0.3.0/0.1.0 vs 0.4.0;
  loom-spec 0.2.2/0.2.1/0.1.0 vs 0.4.1. Decide the contract
  (frontmatter tracks plugin version vs deliberate per-skill semver),
  then either sync or add a drift gate next to the codex-manifest one.
  New instance: loom-pipeline shipped loom-memory SKILL.md frontmatter
  `version: 0.1.0` while plugin.json moved to 0.5.0 (2026-07-06,
  followed sibling practice deliberately) — the undecided contract now
  covers loom-pipeline too.

## .claude/hooks ↔ .codex/hooks mirror has no drift gate
- Status: OPEN
- Start: third mirrored hook-script pair, or next touch of
  check-codex-manifest-drift.sh — whichever comes first
- Origin: PR (this branch) Tasks 6+7 quality review, 2026-07-06 —
  remind-memory-mirror.sh became the SECOND byte-identical
  .claude/.codex hook pair (first: validate-skill-folder-structure.sh,
  since 2026-06-17); nothing enforces identity
  (check-codex-manifest-drift.sh gates only */plugin.json; loom-code CI
  pytests .claude/hooks/ only; CLAUDE.md documents the manifest mirror,
  not the hook-script mirror)
- What: Rule of Three — at the third pair (or next drift-tooling
  touch), add a cmp-based identity test or extend the drift hook to
  cover .claude/hooks/*.sh ↔ .codex/hooks/*.sh.

## #468 reviewer next-touch nits (loom-code TECH-SPEC + CI)
- Status: OPEN
- Start: next loom-code/TECH-SPEC.md touch
- Origin: PR #468 whole-branch reviewer 🟢 next-touch nits (2026-07-02)
- What: freshness-checked 2026-07-06 — (a) dimension-count drift STILL
  PRESENT: TECH-SPEC.md:420 `dimension_scores` lists 6 keys and :261
  says "7-dimension scores" for code-reviewer, whose actual contract is
  10 dimensions (agents/code-reviewer.md description); the same drift
  exists INSIDE agents/code-reviewer.md itself (verified 2026-07-06:
  its line 10 says "7-dimension scores" while its own frontmatter
  description and findings `dimension` enum say 10), so the fix touch
  should sweep the agent file too; (b) dual
  path-presentation styles (mixed backtick/plain paths) STILL PRESENT
  in TECH-SPEC.md; (c) loom CI steps sharing one `run:` block appears
  ALREADY FIXED — all four loom-*-ci.yml workflows now run one command
  per step; confirm and drop sub-item (c) at next touch.

## Living-spec deferred debt bundle
- Status: OPEN
- Start: next living-spec script touch
  (loom-code/scripts/living_spec_*.py or check-living-spec-index.py)
- Origin: living-spec index slices 1–4 + capstone G (#447–#455)
  deferred-debt ledger
- What: (a) regex suffix-vocab lockstep — two regexes must move
  together when the suffix vocabulary changes; (b) drift-lane
  tokenize-ization; (c) Rule-of-Three `_matched_files` extraction;
  (d) Open-Q6 ready-signal binding for BOTH merge-boundary gates
  (verify-index + active-coverage).

## Codex hook events — apply_patch handler emits none (UPSTREAM)
- Status: UPSTREAM (openai/codex#16732, #20204)
- Start: next Codex CLI version bump in this environment — re-run the
  live-fire ritual in docs/loom/codex-verification.md §remind-memory-mirror
  (codex exec writes a type:project note to a memory-pattern path; grep the
  session rollout log for the reminder fingerprint)
- Origin: 2026-07-06 live-fire test on Codex 0.139.0 — apply_patch wrote
  files but the rollout log carried zero hook events; official docs say
  apply_patch matches Edit/Write matchers, so wiring is dormant-correct
- What: BOTH mirrored repo hooks (.codex/hooks/remind-memory-mirror.sh and
  .codex/hooks/validate-skill-folder-structure.sh) are inert on Codex until
  upstream fixes ApplyPatchHandler hook emission. No local fix applies —
  matcher/payload changes cannot help when the handler never emits. On
  upstream fix: verify firing, then also confirm the payload carries
  tool_input.file_path (the script's silent-no-op tolerance would mask a
  key-name mismatch; probe with a catch-all debug hook if needed).

## Anti-copy acceptance greps pass paraphrase copies
- Status: OPEN
- Start: next touch of loom-code writing-plans SKILL.md or the
  plan-document-reviewer prompt
- Origin: 2026-07-06 loom-memory-skill task 1 quality review — the
  plan's anti-copy GREEN criterion grepped for verbatim charter-row
  text; the implementer shipped a complete five-row PARAPHRASE of the
  charter's jurisdiction table that passed the mechanical grep while
  violating its intent; only the quality reviewer's judgment leg
  caught it
- What: anti-copy / SSOT-protection acceptance criteria authored in
  plans need TWO legs — the mechanical verbatim grep AND an explicit
  reviewer-judgment check ("no paraphrase reproduction of the
  protected content"); candidate: one line in writing-plans'
  acceptance-criteria guidance + one check hint in the
  plan-document-reviewer prompt.

## research-toolkit primitive-sync tests cite old deep-research SSOT path
- Status: OPEN
- Start: next research-toolkit scripts/primitives touch, or as a tiny
  surgical PR
- Origin: whole-branch review of research-skill-r2 (2026-07-06,
  docs/loom/dogfood/2026-07-06-research-toolkit-firing-ab.md branch)
- What: per-skill `test_primitives_present.py` files + sync headers still
  cite the SSOT path `research-toolkit/skills/deep-research/scripts/`,
  but the folder is now `deep-deep-research/` (pre-existing residue of
  the earlier rename; functional copies still verify byte-identity, only
  the cited path string is stale). Sweep the path strings, keep
  `scripts/sync-primitives.sh` + check-script-sync.yml semantics intact.
  ALSO sweep member SKILL.md body prose (fact-check ~L12-21, deep-read
  ~L11-18 and siblings) where bare "deep-research" still means the
  sibling deep-deep-research — since the using-research-toolkit router
  now reserves "deep-research" for the host BUILT-IN skill, the bare
  term is newly ambiguous to readers (2026-07-06 review-panel nit).

## General goal-loop harness extraction (PARKED)
- Status: PARKED
- Start (re-trigger): a third real convergence-loop target appears
  (Rule of Three) — extract the shared skeleton from
  `obsidian/skills/wiki-update/scripts/wiki_fix_loop.js` +
  `.claude/workflows/principles-improve-loop.js` then. Candidates:
  loom-spec batch quality loop.
- Origin: superseded brief
  `docs/loom/specs/2026-07-23-goal-loop-harness.md` (6 research sweeps
  + §Design constraints 1-5 + §loom-* integration map) — left as the
  extraction's regspec substrate; superseded 2026-07-23 same-day by the
  user's scope re-cut from "general harness + 2 adapters" to "obsidian
  wiki-update thin orchestrator + loop engine" (plan
  `docs/loom/plans/2026-07-23-wiki-update-loop.md`).
- What: parked is the EXTRACTION — a target-agnostic loop skeleton +
  adapter contract (criteria-freeze preflight, one-violation-class-per-
  round dispatch, brakes/ratchet verdicts, proposal-branch-never-push
  exit) generalized out of the two now-independent implementations
  (`principles-improve-loop.js` and wiki-update's `wiki_fix_loop.js`),
  plus the judge-family fork (mechanical-verdict-only vs LLM-judged
  targets) the superseded brief's research already surfaced. NOT
  parked: the research conclusions themselves — brakes/ratchet/verdict
  design + the "weak-tier executors need mechanical verdict paths"
  lesson are already consumed by wiki-update's shipped `loop_verdict.py`
  / `wiki_fix_loop.js` (bounded-duplication disclosure per the plan's
  Notes), so no further action is owed there.

## operational-kpi full-dimensional-signature slice — follow-ups (2026-07-15)

Context: docs/loom/{specs,plans}/2026-07-15-operational-kpi-full-dimensional-signature.md
(branch feat-operational-kpi-xbrl-pilot). All non-blocking review notes, deferred by
agreement of the per-task + whole-branch reviewers.

- What: retire the OLD pilot fixture `investing-toolkit/tests/analysis/fixtures/xbrl_aapl_factpack.json`.
  5 tests still consume it (incl. `test_cli_build_resolves_binding_and_prints_points`); their
  old single-{axis,member} facts have no `dimensions` key, so `resolve_binding` degrades to a
  coincidental concept-only match (`{} == {}`). Migrate those 5 to `xbrl_signature_factpack.json`
  + full-signature bindings, then delete the old fixture. Also fix the now-stale
  `AMBIGUOUS_OVERLAPPING_BINDING` docstring in test_kpi_xbrl.py (it cites fy-range overlap; fy_min/
  fy_max are dead fields). (T1/T7 review + whole-branch 🟡-adjacent.)
- What: `sec_edgar_client.acquire_filing` (~:973) has the SAME `.latest()` amendment-shadowing bug
  that sig-slice T6 fixed in `extract_dimensional_revenue` — a 10-K/A can shadow the real 10-K.
  Apply the same exact-form filter. (T6 code-quality 🟢.)
- What (watch-list, no live evidence yet): `_is_revenue_concept` excludes only
  `ContractWithCustomerLiabilityRevenue*`; sibling deferred concepts `DeferredRevenueCurrent`/
  `Noncurrent` also contain "Revenue". Add to the exclusion set IF a survey ever surfaces them
  polluting a real fact-pack. (Whole-branch 🟢.)
- What (DRY nit): the dedup-by-period key in `kpi_xbrl.resolve_binding` (~:264) re-implements
  ad-hoc `period_end[:4]` slicing instead of reusing `_require_period`'s validated parsing — no
  correctness impact (the surviving representative still fails loud via _require_period). (Whole-branch 🟢.)
- What (next capability, NOT a defect): multi-filing historical fetch — `extract_dimensional_revenue`
  fetches one 10-K (~3 comparative years). The full ~16-year live history needs fetching + stitching
  multiple filings across eras (the offline era-stitching + declared-break machinery already handles
  the cross-era join; only the multi-filing FETCH is missing). Unlocks the deep live trend.

## Phase Containment Effectiveness — success measure for plan-stage fact grounding (OPEN)
- Status: OPEN
- Start: evaluate at the close-out (whole-branch review and/or live dogfood) of each
  investing-toolkit arc that ships AFTER the plan-stage fact-grounding change
  (`docs/loom/plans/2026-07-27-plan-stage-fact-grounding.md`) lands. The baseline cannot be
  computed yet — see the Baseline note below and the reconciliation entry that follows this
  one.
- Origin: `docs/loom/specs/2026-07-27-plan-stage-fact-grounding.md` Open Question 1 —
  "How is success measured? … Without this the change ships unfalsifiable." Plan Task 9
  (`docs/loom/plans/2026-07-27-plan-stage-fact-grounding.md:452-455`) fixes the measure's
  cheapest viable form. Evidence: `docs/loom/audits/2026-07-27-investing-arc-defect-provenance-audit.md`
  §2 (root-cause taxonomy) and §3 (arc-by-arc dossier).
- What: **Phase Containment Effectiveness (PCE)** — the share of planning-origin defects
  caught BEFORE close-out (whole-branch review or live dogfood) rather than AT close-out.
  **Planning-origin defect** (the audit's Category A, "計畫事實錯"), defined inline so a
  future reader can classify without re-reading the audit: a defect where the PLAN ITSELF
  asserted a false technical claim — a wrong formula/identity, an instruction to reuse a
  semantically incompatible helper, a cited measurement that doesn't support its conclusion,
  a field count that doesn't match the code, or a brief requirement that never made it into a
  task. This is distinct from the audit's Category B (tests that pass without discriminating
  power — fixtures that coincidentally mask a bug) and Category C (ordinary
  implementation-vs-plan mismatches); PCE counts Category A only, because A is the one that
  survives every downstream conformance check (spec-reviewer checks output against plan, and
  the plan is the thing that's wrong).
  - **Cheap classification rule (deliberately narrow)**: for each confirmed Category-A
    instance, classify only whether it reached close-out or was caught before close-out — a
    binary call. Do NOT attribute the earlier catches to a specific stage (plan review vs.
    per-task review vs. implementation-time refusal, etc.) — that per-instance stage
    attribution requires forensic tracing of each defect's exact catch point across every
    task, which is not the cheap form this measure is supposed to take. It is also not this
    measure's job: PCE only needs to answer whether close-out is where the defect surfaced,
    not which earlier mechanism would have caught it. Do NOT attempt this classification for
    Category B or C defects either; they are cheap to catch regardless of category, so
    classifying them buys nothing toward this measure.
  - **Formula**: PCE = (confirmed planning-origin defects caught before close-out) / (total
    confirmed planning-origin defects).
  - **Arcs to evaluate over**: seven already-shipped investing-toolkit arcs — KPI tearsheet
    (PR #605), TW 背書保證 iXBRL (PR #610), US XBRL→store producer (PR #611), TW store
    producer (PR #612), 公司總營收兩線 (PR #616), kpi_id injective (PR #618), US as-reported
    線 (PR #619) — plus one **in-progress** arc, the as-filed reconstruction (branch
    `feat-sec-submissions-pagination`), whose audit coverage is explicitly incomplete
    (audit header §Scope, and §1's scoreboard — task-level PASS/PASS_WITH_NOTES counts are unfilled for
    this arc, only the NEEDS_REVISION count is known, because it hasn't shipped).
  - **Baseline: cannot be computed from the current audit.** The source document
    (`docs/loom/audits/2026-07-27-investing-arc-defect-provenance-audit.md`) contains four
    internally inconsistent claims about the same Category-A instances, so any count or
    close-out/pre-close-out split drawn from it right now would be unreliable — see the
    reconciliation entry immediately below for the specific inconsistencies and their
    citations. Do not compute or assert a PCE number until that entry is resolved.

## investing-toolkit arc defect-provenance audit — internal inconsistencies need reconciliation (OPEN)
- Status: OPEN
- Start: before computing the Phase Containment Effectiveness baseline (entry above) — that
  measure depends on a trustworthy Category-A count and close-out determination from this
  document.
- Origin: found while writing the Phase Containment Effectiveness BACKLOG entry (Task 9,
  `docs/loom/plans/2026-07-27-plan-stage-fact-grounding.md:452-455`), round 3, after a prior
  round's attempt to compute a baseline from this audit produced a four-bucket per-instance
  attribution that both reviewers rejected as out of scope. Re-checking the source turned up
  the inconsistencies below.
- What: `docs/loom/audits/2026-07-27-investing-arc-defect-provenance-audit.md` makes four
  internally inconsistent claims about its own Category-A ("計畫事實錯") findings for PR #619
  and the audit's overall detectability claim:
  (Citations below use **section anchors**, not line numbers: adding the audit's erratum
  header pushed every line under it down, which invalidated this entry's original pointers
  in the same change set that catalogued citation drift. The shift's magnitude is
  deliberately not stated — a self-referential count is a claim that must be re-measured on
  every edit, and failing to re-measure it is exactly how the previous remediation round
  broke this passage. See the "what 0.39.0 does NOT close" entry, item 3.)
  1. **Scoreboard count vs. dossier count mismatch.** §1's scoreboard reports PR #619 as
     `A×2`; §3.7 enumerates three A-instances (A-1 the equity-identity probe, A-2 the reused
     selector, A-3 the retired-numbers doc).
  2. **"Only detectable at close-out" contradicted by the audit's own dossier.** §5's
     sentence "A 類的偵測面只有兩個，都在收尾" (grep for it; it is the lead-in to that
     section's bullet pair, not its closing line) asserts A-class defects are
     structurally detectable ONLY at close-out; §3.7 (a quality reviewer's
     spontaneous cross-read at per-task review), §3.8 (an implementer's
     task-level refusal before any code was written), and §6 (citing that
     refusal as a positive counterexample) all document earlier catches.
  3. **"Caught before merge" contradicted by a shipped defect.** §6 states
     every A-defect was caught before merge; §3.7's A-3 states the wrong text
     ("GOOGL from 2014, DIS from 2018" — as `analysis-kpi/SKILL.md` read at the time of the
     audit, 2026-07-27; that text has since been corrected to 2012/2016, so the pointer no
     longer greps) shipped — i.e. was
     NOT caught before merge.
  4. ~~**Self-contradicting count within one sentence.**~~ **WITHDRAWN** — not a
     contradiction. §3.8's opening reads "A 類三連…implementer 拒絕動工並回報四項量測":
     three Category-A defects, and four measurements reported by the implementer. Two
     different quantities in one sentence, not one quantity stated twice. Withdrawn on
     whole-branch review of `feat-plan-fact-grounding`, which read the line rather than the
     summary of it — the same failure this branch's own cross-read rule exists to catch,
     committed while writing the entry that catalogues it. Left visible rather than deleted:
     the reconciliation task must not re-derive a phantom item, and the miss is the point.
  - **Why it matters**: the Phase Containment Effectiveness measure (entry above) needs a
    reliable Category-A count and a reliable close-out/pre-close-out split per confirmed
    instance. Items 1-3 cannot be trusted as-is. Reconcile by re-reading the
    underlying session transcripts this audit was extracted from (audit header §Method) and correcting
    the audit's prose, then recompute the PCE baseline from the corrected document.

## Plan-stage fact grounding — what 0.39.0 does NOT close (OPEN)
- Status: OPEN
- Start: next time a planning-origin defect reaches close-out despite 0.39.0's contracts —
  or when the PCE entry above is first evaluated, whichever comes first. Each item below is
  independently actionable; do not treat the list as one unit of work.
- Origin: whole-branch review of `feat-plan-fact-grounding` (loom-code 0.39.0), which held
  the branch to the standard the branch itself argues for. Findings 1-3 of that review plus
  the orchestrator's carried close-out list.
- What:
  1. **The preventive half of the citation rule is unenforced.**
     `writing-plans/references/plan-format.md:149` ("Any verifiable technical assertion in a
     plan carries a `file:line` citation…") requires a citation on every verifiable
     assertion, but no plan-document-reviewer check verifies compliance — the checks table
     stays at 16 rows and `loom-code/scripts/test_plan_obligation_sweep.py:68` pins
     `max(row_numbers) == PRE_EXISTING_MAX_CHECK_NUMBER` (the constant, `= 16`, at
     `test_plan_obligation_sweep.py:32`). Reviewer item 7 is by design a no-op when no
     citation is present.
     Net effect: 0.39.0 catches a **cited** false fact (measured — see the dogfood note's
     §Re-run) and misses an **uncited** one, which is the cheaper authoring path and the
     shape of the audit's own §3.8 instance ("15 fields" asserted three times where
     the code says 14). Fix is either Check 17 plus amending the pin, or an explicit decision
     to accept the residual. Branch-local evidence that author-side discipline does not
     self-hold: five citation inaccuracies in this branch's own commits, the fifth inside the
     section documenting the citation fixes.
  2. **The acceptance-criteria family is untouched.** Candidate check, append-only numbering:
     *acceptance criteria must be executable by the actor bound to satisfy them.* Origin:
     Task 7's GREEN required `check_version_bump.py`, which reads committed blobs, while the
     implementer is forbidden from committing. It survived all three plan-review rounds — the
     rounds asked whether the criteria were correct, never whether the bound actor could run
     them. Two further instances in the audit's §3.8 (a RED naming filers with no data; a RED
     contradicting the brief on DUK) sit in this family.
  3. **`file:line` citations drift under parallel edits.** Four measured instances on this
     branch (`:365`→`:372` from a concurrent insertion, `:41` vs `:40`, `:32-39` vs `:34-39`,
     a path missing its directory). The T1 rule should prefer an anchor that survives
     insertion, and date any bare line number it keeps.
     - **DETECTION (mechanised, 0.40.0).** The `loom-code/scripts/check_doc_citations.py`
       script (default mode: path:line bounds with unique-suffix fallback) now verifies every
       `` `path:line` `` and `` `path:line-range` `` citation in the docs/loom corpus. Measured
       on the committed corpus: **0% false positive, 8/8 true positives on the line-exceeds-bounds class**; the documented content-drift instances (bounds-valid, content-wrong) are NOT detectable by this check — see `docs/loom/dogfood/2026-07-28-citation-check-corpus-run.md` §3a.
     - **PREVENTION (open).** Durable anchors over bare line numbers remain unimplemented.
     - **§N-anchor detection (experimental, implemented behind the flag but not invoked by the
       review mode).** The `--sections` flag detects §N references resolving to numbered
       headings (§N / §N.M in the cited file). Zero true positives on the corpus to date;
       awaiting a re-measured threshold for escalation from experimental to default. Same
       corpus-run note, same section.
     - **Quoted-citation false positives (parser v1 limitation).** The default-mode check
       cannot distinguish a citation inside fenced code blocks, blockquotes, table cells, and inline examples — dogfood notes quoting
       tool output, deliberately-broken fixture examples — from a live citation; both are
       checked identically, producing false findings. 2/2 observed on this branch's own
       dogfood notes. Reviewers must treat pre-pass findings inside fenced code blocks, blockquotes, table cells, and inline examples as
       advisory, not as defects (see `requesting-code-review/SKILL.md:97`).
  4. **`Reuse-adequacy` is declarative-only.** Nothing enforces that a task carrying a reuse
     instruction fills the field.
  5. **Implementer test counts are not reproducible.** Two implementers reported "437 passed";
     no scope reproduces it. The reproducible ones, each with the command that yields it:
     `python3 -m pytest loom-code/scripts/ -q` → 363 at the time of that report, and
     `python3 -m pytest loom-code/scripts/ loom-pipeline/scripts/ -q` → 581. Both are dated
     figures, not standing ones — re-run the command rather than citing the number. A count
     that cannot be reproduced is not a verification claim.
     Candidate fix: require the dispatch packet's `Resolved test command` to be echoed
     verbatim in the report beside the count.
  6. **The drift-boundary clause lands at one tier only.** Measured before/after on the same
     fixture: sonnet went from silently absorbing a stale pointer (while asserting the source
     said it at that location) to detecting, classifying and recording it; haiku went from
     naming the drift to papering it over with an invented `:180-182` range. Verdicts stayed
     correct in all four cells and no false alarm appeared, so the clause ships — but the two
     haiku runs contradict each other, so run-to-run variance at that tier exceeds the effect
     at n=1. Do not describe the clause as working at both tiers.
     Evidence: `docs/loom/dogfood/2026-07-27-plan-fact-grounding-coldread.md`.
  7. **Next amendment to reviewer item 7 must split it, not extend it.** Three amendments were
     concatenated into one ~200-word numbered list item (~6× its sibling contract items).
     Split into labelled sub-bullets — action / consequence / boundary — before adding a
     fourth. A long run-on read by the weakest tier is the shape this repo's standing finding
     says fails.
  8. **`loom-code/scripts/test_writing_plans_readme_sync.py:51-52` uses `str.index`** — raises
     `ValueError` on a missing anchor instead of a readable assertion failure. 🟢
  9. **The two cross-read guard test files are ~45% identical.** Defensible under this repo's
     SSOT-and-functional-copy convention and the two genuinely different verdict models;
     next-touch only. 🟢
  10. **Shipped with a known defect of its own, stated rather than fixed.** The
      entry titled "investing-toolkit arc defect-provenance audit — internal inconsistencies
      need reconciliation" still opens by saying the audit "makes four internally
      inconsistent claims" while its item 4 is struck WITHDRAWN and its own §Why it matters
      concludes that items 1-3 are the live ones. The audit's erratum says 三處; this
      entry's header is the stale copy — withdrawing item 4 did not re-measure the tally
      that counts it.
      - **Why it is shipped rather than corrected**: this is the self-referential class
        described in `docs/loom/memory/a-passage-that-describes-itself-decays-on-every-edit.md`,
        and every close-out round that fixed an instance of it wrote a fresh one into
        whatever surface the fix touched — a wrong file citation, an invalidated pointer set,
        a stale shift magnitude, a wrong positional descriptor, a wrong instance tally, a
        round count sitting between its own abstention and its own prohibition. The
        terminal-round rule set before that round's verdict was: another instance of this
        class gets recorded, not rewritten. Round after round of moving one clause is evidence that
        this prose surface is not driven clean by iteration, and that evidence is worth more
        shipped than hidden behind a seventh edit.
      - **Fix when the reconciliation runs**: correcting the audit's three live
        inconsistencies and re-deriving this entry's header tally is one task, not two. Do
        not fix the tally alone — that re-creates the same decoupling in the other direction.
  11. **`writing-plans/SKILL.md` is at its hard word cap.** This change pushed it over
      CHK-SKL-010's 4,500-word ceiling (CI caught it at 4,571); rationale prose was trimmed
      to bring it back under, and it now sits a handful of words below the cap. The next
      addition to that file **cannot be an append** — it must extract an existing section to
      `references/` and link it, or trade words out. Note the extraction hazards already
      recorded in this store: `extract-to-reference-load-bearing-rule` and
      `extraction-severing-cross-ref-needs-weak-model-test` (a strong-model equivalence gate
      passes while a weak model drops the severed link, so extraction needs a weak-model
      cold read). The file is also far above the repo's ~3,750-word soft target, which is a
      standing condition of this skill rather than something this change introduced.
  12. **Release obligations are invisible to every plan check.** This branch's plan passed
      14/14 with no version-bump task; the omission produced a live wrong version token in a
      shipped annotation (item 3's 0.39.0/0.40.0 finding above). Check 8 sweeps the brief;
      nothing sweeps repo conventions. Candidate: a standing release-obligations note in
      writing-plans, or an append-only reviewer check.
  13. **A gating obligation stated in a task Description binds nothing.** T3's "stop before
      Task 4 ships the dependency" lived in prose; the Dependencies field did not encode it;
      parallel marking let T4 commit first. Second consequence: the pre-pass population
      caveat later folded into `requesting-code-review/SKILL.md:97` (the 0% false-positive
      figure's scope) reached that file only at whole-branch review, not during the branch's
      own plan-driven tasks. Candidate: plan-format rule — a Description sentence that gates
      ANOTHER task must be encoded as a Dependencies edge or it does not exist.

## spec-reviewer Rule R3 forbids the cross-read item 7 now requires (OPEN)
- Status: OPEN
- Start: next edit to either reviewer contract's discipline rules, or the next time a
  reviewer's R3 compliance lets a false reported figure through.
- Origin: whole-branch review of `feat-plan-fact-grounding`, finding 3. The contradiction was
  latent before 0.39.0; item 7 makes it adjacent — the two rules now sit ~30 lines apart in
  the same document.
- What: `agents/spec-reviewer.md` (same shape in `agents/code-quality-reviewer.md`) newly
  **requires** a reviewer to independently open a cited source and confirm it says what the
  claim says (item 7), while Rule R3 in the same contract **forbids** independently confirming
  a reported test result. Both are the same epistemic act. A weak-tier reader has to reconcile
  them; on this branch 5 of 7 spec-reviewer dispatches resolved it by violating R3.
  - **Ruling from that review: the rule is wrong, not the reviewers.** R3 conflates "do not
    substitute for the verification station" (sound) with "do not independently confirm
    reported evidence" (unsound, and contradicted by this branch's own thesis).
  - **Evidence**: an implementer-reported test count of `437` that no reproducible scope
    yields survived every R3-compliant reviewer on this branch and was caught only by a
    reviewer that violated R3.
  - Not fixed here because R3 is outside this branch's diff — changing a discipline rule that
    governs every reviewer dispatch is its own change with its own review.
