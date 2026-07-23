# loom family backlog

> SSOT for cross-plugin open items. Convention: one entry per item with
> **start/re-trigger condition**, **origin** (PR / ledger / discussion),
> and **status** (`COMMITTED-NEXT` | `OPEN` | `PARKED` | `UPSTREAM`).
> Plugin-local parks stay in each plugin's README (§parked items with
> re-triggers); this file holds items that cross plugin boundaries or
> have no plugin home yet. Claude-side session memory keeps only a
> pointer here — this file is the durable truth (versioned, host-agnostic,
> greppable). Completed items are deleted, not archived — git history is
> the archive.

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
  resolved too. (b) **endorsement/guarantee curated field** —
  deferred (ix:tuple per-counterparty rows, no clean aggregate leaf); needs the
  note-table reconstruction path. (c) **興櫃 multi-period series** — semiannual
  (Q2/Q4) cadence; season-fallback already handles per-period absence, a series
  builder is future. (d) 🟢 debt: T3 canonical tie-break order untested (membership
  only), T2 3×502-exhaustion branch untested.

## investing-toolkit TW financial iXBRL 2.31.0 — post-ship follow-ups (OPEN)
- Status: OPEN
- Origin: TW financial-sector iXBRL (branch feat-tw-ixbrl-fh, 2026-07-23, 2.31.0);
  whole-branch review PASS with carried 🟢 debt.
- What: (a) **memo Phase-4 consumption of `not_applicable` DCF** (ANALYSIS/domain-teams
  layer, out of this data-layer arc) — `dcf_compute` now emits a structured
  `{"not_applicable":"financial-sector"}` dcf.json for financial tickers; confirm
  `report-equity-memo` Phase-4 seed + `domain-teams:investing-team` render "DCF N/A"
  gracefully rather than choking on the marker. (b) 🟢 Rule-of-Three duplication: the
  `sorted→values→meta` block in `twse_ixbrl_canonical.py` (`_sum_concepts`/`_first_present`/
  builder loop) and the by-concept-grouping block across the 3 note extractors in
  `twse_ixbrl_notes.py` — extract shared helpers on next touch. (c) 🟢 over-soft-cap
  functions: `dcf_compute.main`, `pack_memo_fetch`. (d) 🟢 fact-count guard decodes via
  big5hkscs, not the production `decode_ixbrl_document` — assert count-equality under the
  real decode too (coverage, not correctness). (e) 🟢 stale scratchpad citations in
  `twse_ixbrl_canonical.py`/`twse_ixbrl_notes.py` comments — migrate key measurement
  tables into a committed reference or trim. (f) US financial filers (`pack_us`) get no
  `sector_class` guard — pre-existing; a future US financial-comps path needs its own.

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
