# Brief — Multi-filing historical fetch (P2)

**Date**: 2026-07-15
**Origin**: BACKLOG P2, operational-kpi arc follow-up (investing-toolkit 2.20.0 shipped)
**Stage**: brainstorming → (blocked on one Open Question) → writing-plans

## Problem

(Axis 1 — JTBD) A user wants to see a **single company's operating-KPI trend over
its full XBRL-era history (~2009→present, ~16 years)**, not just the ~3 comparative
years a single 10-K carries. The job: "show me how THIS company's own filing-native
operating KPI (e.g. iPhone revenue, a segment's revenue) has moved across its whole
reporting history, faithfully, without inventing or mislabeling any point." Today the
extractor stops at one filing, so the trend is truncated to 3 years.

## Users

(Axis 2) The investing-toolkit analysis/memo path (`analysis-kpi` → memo feed), for a
single-company same-company historical trend. Cross-company comparability is a
**non-goal** (locked design intent). Reliability target: **0.95 + DQC checks**.

## Current State Evidence

(All file:line from live recon, 2026-07-15.)

- **Forward (fetch)**: `extract_dimensional_revenue` — `sec_edgar_client.py:1985`.
  Enumerates all filings (`company.get_filings(form)`, `:2025`), applies the T6 exact-
  form filter (`:2034`), then **hard-collapses to ONE filing** via
  `filing = max(exact_filings, key=filing_date)` at **`:2037`**. Pulls `filing.xbrl()`
  → `xb.facts.to_dataframe()` (`:2043-2044`). Returns a flat `{"company", "facts":[...]}`
  at `:2054`; each fact = `{concept, dimensions, consolidation, value, period_end,
  fiscal_year, accession, filed}` (`_build_dimensional_revenue_fact:1939`, dims via
  `_dimension_signature:1889`).
- **Reverse (consumer seam)**: filing-count-**agnostic**. `facts_to_points:151` and
  `resolve_binding:199` both read the flat list (`for fact in fact_pack.get("facts",[])`
  at `:163` / `:233`). `build_series_with_break:296` delegates to period-keyed
  `kpi_series.split_series` (`:308`) — **never sees accession**. Era-stitching +
  declared-break machinery is entirely period-keyed.
- **Data (period)**: `_require_period:121` → `period_end[:4]` (`:137`), fail-loud on
  missing/malformed; `fiscal_year` derived from `period_end` at `:1979`, never
  edgartools' raw column (the known gotcha).
- **Error (anti-fabrication dedup)**: `resolve_binding:259-277`. Group by
  `(signature, period[:4])`; `values = {fact["value"] for fact in group}` (`:267`);
  **`len(values) > 1` → RAISES** (`:269-274`); identical → DEDUPE keep-one (`:277`);
  unmatched → SKIP (`:251`); >1 source match → RAISES (`:244-250`).
- **Boundary (edgartools enumeration)**: **already exists** — `company.get_filings(form)`
  returns an iterable collection (iterated at `:2034`); the code just collapses it. Also
  `list_filings:371` (metadata rows across years, no xbrl) and `acquire_filing:915`
  (single, `.latest()` at `:973` — carries the P3 amendment-shadowing bug, adjacent).

## Smallest End State

(Axis 3) **This brief = scope A only** (annual multi-filing on the proven machinery).
Quarterly (scope B) is a committed follow-up — see §Committed follow-up.

Change **one seam** — `sec_edgar_client.py:2037` — from "pick max filing" to a
**range-bounded, consecutive multi-filing fetch**, plus the overlap policy (C) for
duplicate `(signature, period)` pairs. Everything downstream is unchanged: the
concatenated flat `facts` list flows through `resolve_binding` → `build_series_with_break`
as-is (proven filing-agnostic).

Interface + fetch policy (resolved with user, 2026-07-15):

- **Range is a parameter, agent decides depth.** `extract_dimensional_revenue(ticker,
  form="10-K", since_year=None, until_year=None)`. The range knob lives in the data-fetch
  primitive; the *policy* of how much history to pull belongs to the analysis/agent layer
  (matches the toolkit's data-layer=I/O / analysis-layer=decisions contract).
- **Default = current behavior (latest filing only, ~3 yr).** No regression, no cold-fetch
  surprise. Historical depth is **opt-in** via `since_year`. Rationale: default-fetch-all
  is ~16 sequential `.xbrl()` downloads (tens of seconds cold) — too heavy for a default.
- **Consecutive within the requested range** (fetch every exact-form filing spanning
  [since_year, until_year]), NOT strided. Striding risks silent year-gaps (a filing may
  carry only 2 comparative years) and kills the overlaps policy C relies on — both violate
  the anti-fabrication no-silent-holes stance. The **range** is the cost knob; cache makes
  warm runs cheap.
- **Coverage honesty (DQC).** When the requested range exceeds availability (XBRL floor
  ~2009, or before the company's first filing), return what exists AND report the clamp
  (requested vs actual + reason) — never silently return a shorter range.
- **Forward-compat period key (for scope B).** A's identity/dedup key carries a
  `period_type` field, which A always sets to a single annual value (`FY`). B extends it
  with quarterly members (`Q1..Q4`/YTD) without rewriting the core. A does NOT model
  quarters; it only reserves the slot. Exact `period_type` shape is B's (loom-spec) call.

## Alternatives Considered

(Axis 4 — WebSearch EN+JA, 2026-07-15)

1. **SEC official REST API (companyfacts / frames)** — one HTTP call for a concept's full
   history. [SEC EDGAR APIs](https://www.sec.gov/search-filings/edgar-application-programming-interfaces).
   **REJECTED**: returns only default-axis (total) facts — dimensional members are not
   reliably present ("all numbers coming in are overarching figures",
   [Alteryx community, live report](https://community.alteryx.com/t5/Alteryx-Designer-Desktop-Discussions/SEC-Edgar-API-Service/td-p/1031684)).
   Our capability keys on the **full dimensional signature** → this loses the whole point.
2. **Loop the trusted single-filing extractor × N accessions + concatenate facts**
   (current path, un-collapsed). **CHOSEN**: reuses the exact live-validated code path
   that preserves each fact's full signature; the consumer is provably filing-agnostic so
   concatenation "just works". Cost: N network calls (cached) + the overlap policy.
3. **edgartools `XBRLS` multi-filing stitching class**
   ([edgartools docs](https://edgartools.readthedocs.io/en/latest/getting-xbrl/)).
   **REJECTED for now**: stitches at the *rendered-statement* level; unverified whether it
   preserves raw per-fact dimensional signatures, and memory records edgartools shape
   surprises caught 3× (`fixtures-mirror-producer-shape`). Adds dependency on its stitching
   semantics we'd have to re-validate.

## What Becomes Obsolete

(Axis 5) The hard-collapse `max(exact_filings, key=filing_date)` at `:2037` is replaced by
the multi-filing loop for the historical path. **Mostly additive** (a capability
extension) — no runbook/convention is retired. Adjacent: the same `.latest()` amendment-
shadow bug in `acquire_filing:973` (P3) could be fixed in the same change or left; **out of
scope unless trivially co-located**.

## Decision

**RESOLVED — user chose policy (C) + range-param design on 2026-07-15.** Build option #2:
un-collapse the fetch seam at `sec_edgar_client.py:2037` into a range-bounded consecutive
multi-filing fetch (`since_year`/`until_year`, default = latest-only), concatenate facts
across the requested range's exact-form 10-Ks, and for duplicate `(signature, period)`
pairs apply **newest-filing-wins + a restatement DQC flag** (prefer the value from the
most-recently-filed 10-K; when a superseded value differs, record a data-quality flag
capturing old→new + the two accessions). Add a coverage report (requested vs actual range
+ clamp reason). Reserve a `period_type` field on the identity key (A sets `FY`) for scope
B. This replaces the existing hard-RAISE-on-disagreement path for the *cross-filing
overlap* case only — the intra-filing anti-fabrication invariants (>1 source match,
unmatched-skip, malformed-period fail-loud) are UNCHANGED. Everything downstream of the
concatenated flat `facts` list (`resolve_binding` → `build_series_with_break`) is
unchanged.

## Out of Scope

- Pre-XBRL era (before ~2009) — no XBRL exists; needs the deferred LLM-extraction tier.
- Non-dollar operational stats (subscribers/units/…) — separate P2 tier, needs a pilot
  ticker + ground-truth from the user.
- A single ticker→series CLI spanning both scripts (today none exists; library-only).
- `acquire_filing:973` `.latest()` fix — separate P3 unless trivially co-located.
- Fiscal-calendar map for FY-named-by-start-year filers (a later concern).

## Open Questions

**Q1 (BLOCKING) — restatement / overlap-resolution policy.** When two adjacent 10-Ks
report the SAME `(signature, period)` with DIFFERENT values (a restatement), what should
the merged series do? Current dedup RAISES on any value disagreement (`kpi_xbrl.py:269`),
which over a 16-year span almost certainly aborts the whole series. Options:

- **(A) Newest-filing-wins (silent)** — prefer the value from the most-recently-filed
  10-K; drop the superseded value. Simplest usable path; matches "the company's own
  latest corrected view". Con: silently discards the as-originally-reported value.
- **(B) Keep RAISE (fail-loud on any disagreement)** — literal anti-fabrication purity.
  Con: any restatement over 16 years aborts the series → likely unusable in practice.
- **(C) Newest-wins + restatement DQC flag** — prefer newest, but attach a data-quality
  flag recording the point was restated (old→new). Matches the stated **0.95 + DQC**
  reliability target; keeps the trend usable AND surfaces restatements. **RECOMMENDED.**
  Con: slightly more machinery than (A).

Recommendation: **(C)** — it honors the locked "0.95 + DQC" design intent, yields a usable
16-year trend, and never silently hides a restatement (the anti-fabrication spirit is
"never invent/mislabel", not "abort on any restatement"). Conditional reversal: if the
user wants zero new DQC surface right now, fall back to **(A)** and defer the flag to a
later DQC pass.

**RESOLVED 2026-07-15: user chose (C).** See §Decision.

## Committed follow-up (scope B — quarterly)

**Not in this brief; committed for the next cycle (user confirmed both A and B needed,
2026-07-15).** Add 10-Q support for quarterly resolution. This is NOT a `form="10-Q"`
parameter swap — it requires extending the period-identity model, because a 10-Q tags BOTH
the 3-month quarter AND the year-to-date cumulative under the SAME `period_end` (e.g. both
"3 months ended 9/30" and "9 months ended 9/30"). The current key `(concept, dimensions,
period_end[:4])` has no duration discriminator, so naive 10-Q ingestion would conflate
single-quarter with YTD — exactly the conflation class this arc exists to prevent.

- **Routes through `loom-spec` first** — the period-duration state space needs fan-out
  (Q1–Q4 / 3mo·6mo·9mo·YTD / fiscal-year-end variants / Q4-implied-by-subtraction /
  transition periods), then loom-code.
- **Reuses A's multi-filing fetch plumbing + policy C** (why A is sequenced first).
- **Consumes A's reserved `period_type` slot** (extends `FY` with quarterly members;
  no core rewrite). Exact `period_type` shape is B's design call.
- Also verify 10-Q dimensional-breakdown completeness vs 10-K (segments sometimes
  condensed in 10-Qs) — an open question for B's spec.

## Design-side on-ramp

N/A for scope A — brownfield, test-covered increment to a shipped capability (Axis 0
negative guard). Scope B, by contrast, WILL route through `loom-spec` (multi-state period
model on a data surface) before its own loom-code cycle.
