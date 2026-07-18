# Brief — memo 接線切片：quarterly KPI series → report-equity-memo → investing-team

Date: 2026-07-18 · Stage: brainstorming output (loom-code Stage 1) · Consumer: `writing-plans`

## Design-side on-ramp

Offered in the post-ship roadmap turn (PRINCIPLES.md absent; loom-product-principles
suggested) — **user chose direct** (brainstorm → plan → SDD). The derived-Q4 trust
policy is settled per-slice here (see Open Questions → Decision) instead of via a
constitution run; a future PRINCIPLES.md run may generalize it.

## Problem

The equity memo currently argues thesis and valuation from DCF + comps + macro-regime
+ xval only — it contains **zero operational-KPI evidence** (grep: no `analysis-kpi` /
quarterly reference anywhere in `report-equity-memo` or `investing-team`). The job:
when kouko runs `/report-equity-memo` on a US ticker, the memo should present the
company's quarterly operational-KPI trends (segment/product revenue from 10-Q XBRL)
as thesis-support evidence — with the 2.22.0 anti-fabrication guarantees (parallel
calendar/fiscal labels, derived-Q4 segregation, coverage honesty) surviving end-to-end
into the rendered tables, not silently flattened by the delegation into prose.

Secondary job (process): this slice is knowledge-triage v2's named live acceptance
（「真實驗收=financial重做」）— the DOMAIN.md prevention layer gets its first real fight.

## Users

- **kouko**, running `/report-equity-memo <US-ticker>` on this machine; reads the memo
  later with investor eyes — a mislabeled derived value or silently spliced series is
  the worst failure (worse than absence).
- **investing-team gates** (CHK-CIT / CHK-THX) as institutional consumer: every number
  must trace to a source; upstream `_status`/`warnings[]` transcribed verbatim
  (primary-source-citation-compliance.md:24,32,36).

## Smallest End State

One US ticker's memo run produces an Operating-KPI quarterly trend exhibit with honest
labels, and the investing-team protocol knows where to put it:

1. **Fetch step** (investing-toolkit, data layer): a callable path that produces the
   dimensional-revenue fact-pack JSON for one ticker (today `extract_dimensional_revenue`
   at sec_edgar_client.py:2568 has zero pack callers).
2. **Analysis step** (investing-toolkit): CLI-expose the quarterly series build via the
   **existing but unconsumed** `kpi_memo_feed.py` contract (analysis-kpi
   SKILL.md:392-426) — NOT raw kpi_xbrl library calls; emits one memo-feed JSON
   (series + derived-Q4 lane + coverage flags, DQC schema intact).
3. **Orchestration** (report-equity-memo): one new phase between Phase 3 (DCF) and
   Phase 4 (delegation); memo-feed JSON path joins the `### Resource Paths` list
   (SKILL.md:356-380). US-only; non-US tickers skip the phase with an explicit
   skip note (no silent absence).
4. **Protocol** (domain-teams, investing-team): a new Operating-KPI block in the memo
   protocol + output template (deep-equity-research-memo.md:286-370) defining table
   shape (last 8 quarters), derived-Q4 cell tagging, coverage-gap footnotes.
   Gate contract **unchanged** — recon confirmed gates reference inputs generically;
   the new series rides existing CHK-CIT-004/007 + provenance-footer machinery.
5. Both plugin versions bumped (investing-toolkit + domain-teams) — content PRs
   without a bump are silent no-ops on device (repo memory).

## Current State Evidence

- **Forward** — memo pipeline today: Phase 1 single `pack.py --pack memo-fetch`
  (report-equity-memo/SKILL.md:107-117) → Phases 2/2.5/2.6/3 (macro-regime, comps,
  xval US-only, dcf; SKILL.md:128-342) → Phase 4 delegates to
  `domain-teams:investing-team` passing 5 JSON paths as `### Resource Paths`
  (SKILL.md:356-380); verdicts return into a "Gate Results" section (SKILL.md:465-468).
  KPI/quarterly: zero hits.
- **Reverse** — SSOT direction per repo CLAUDE.md §Cross-Plugin Delegation Contract
  (CLAUDE.md:62-84): data layer stays in investing-toolkit; analysis/protocol/gates
  stay in domain-teams; gate logic must never be duplicated toolkit-side; targets
  referenced as `plugin:skill`. The protocol/template SSOT is
  `domain-teams/skills/investing-team/protocols/deep-equity-research-memo.md`.
- **Error** — honesty machinery already shipped in 2.22.0: coverage flags
  `no_quarterly_coverage` (kpi_xbrl.py:1105-1164, emitted :1251-1263), Q4 basis
  refusals `q4_basis_mismatch`/`q4_source_missing` (kpi_xbrl.py:882-913, 787-861),
  `assert_dqc_schema` single-flag-schema enforcement (kpi_xbrl.py:158-201).
  Downstream, CHK-CIT-007 requires verbatim transcription of upstream
  `_status`/`warnings[]` (primary-source-citation-compliance.md:36).
- **Data** — per-point schema: `period` = fiscal label + honest
  `calendar_year`/`calendar_quarter` pair + `period_type`/`cumulative`/
  `duration_class` (kpi_xbrl.py:432-465, docstring :52-63); derived-Q4 lane points
  carry `derived: True` + PLURAL `source_accessions`/`source_forms` + DQC
  `derived_q4` (kpi_xbrl.py:928-957); `derive_q4_points` returns `{"points","gaps"}`
  (kpi_xbrl.py:961-1042); memo-fetch pack keys (pack_us.py:916-936) do NOT include
  the dimensional fact-pack shape kpi_xbrl consumes.
- **Boundary** — the seams this change crosses: quarterly builders are library-only,
  not CLI-exposed (kpi_xbrl.py:961,1167 vs CLI :1327-1340 `build` only);
  `kpi_memo_feed.py` is a built-but-unconsumed producer (analysis-kpi
  SKILL.md:392-426); investing-team protocol has NO operational-KPI home — closest
  existing treatment is the Taiwan-only 月營收 block
  (deep-equity-research-memo.md:136-143); MUST gates listed at
  investing-team SKILL.md:386-388.

Evidence paths appendix:
`investing-toolkit/skills/report-equity-memo/SKILL.md`,
`investing-toolkit/skills/report-equity-memo/references/phase4-seed-contract.md`,
`investing-toolkit/skills/analysis-kpi/SKILL.md`,
`investing-toolkit/skills/analysis-kpi/scripts/kpi_xbrl.py`,
`investing-toolkit/skills/analysis-kpi/scripts/kpi_memo_feed.py`,
`investing-toolkit/skills/data-markets/scripts/pack_us.py`,
`investing-toolkit/skills/data-markets/scripts/sec_edgar_client.py`,
`domain-teams/skills/investing-team/protocols/deep-equity-research-memo.md`,
`domain-teams/skills/investing-team/checklists/primary-source-citation-compliance.md`,
`CLAUDE.md` (§Cross-Plugin Delegation Contract).

Standing red lines from repo memory (bind this slice):
`docs/loom/memory/fiscal-year-derive-per-fact-against-filing-calendar.md` (never
`period_end[:4]`, never stamp filing focus),
`docs/loom/memory/match-kpi-on-full-dimensional-signature-not-one-axis.md`,
`docs/loom/memory/hand-authored-fixture-is-a-fabrication-risk.md` (fixtures =
machine-captured with `_provenance`),
`docs/loom/memory/critic-finding-is-hypothesis-until-code-recon.md`.

## Alternatives Considered (Axis 4 — research-grounded)

Industry research (EN 5 queries + JA 2 queries, 2026-07-18):

- **Where KPIs live**: sell-side notes carry a dedicated post-earnings "Quarterly
  Update" section + Financial Exhibits appendix ([EN]
  wallstreetprep.com/knowledge/sample-equity-research-report/); buy-side memos are
  thesis-first — KPIs sit in an operations/financial support section feeding the
  thesis ([EN] mergersandinquisitions.com/equity-research-report/). JA practice
  mirrors: KPI 過去推移 as analysis backbone; filers publish 決算データシート
  (セグメント別損益推移表+KPI表) ([JA] buffett-code.com/articles/5641,
  lycorp.co.jp/ja/ir/library/indicator.html).
- **Implied Q4**: Q4 = FY − ΣQ1-3 is standard practice ([EN]
  stocktitan.net/articles/10-q-quarterly-report-guide, fastercapital.com 10-K vs
  10-Q toolkit); labeling is informal practitioner vocabulary ("implied", footnote),
  no formal standard. **EN/JA asymmetry finding**: JP filers report true Q4 every
  quarter (決算短信), so JA-convention readers do not expect derivation — an
  explicit machine-applied label is strictly clearer than the industry baseline
  ([JA] hiromethod.com/sec-filing, estrilda.damonge.com annual-report guide).
- **Coverage gaps**: US practice truncates the series on metric discontinuation
  (Netflix/Apple precedent, [EN] variety.com 2024); ASC 280 requires retrospective
  restatement on segment change — never splice silently ([EN] dart.deloitte.com
  ASC 280 roadmap §4-9); TSE norm is footnote-the-reason + continue if computable
  ([JA] faq.jpx.co.jp knowledge8448).

Wiring alternatives:

| Option | What | Rejected because |
|---|---|---|
| A. Extend memo-fetch pack to include dimensional facts | One fetch, one pack | Bloats the frozen memo-fetch schema (us-schema-memo-fetch.json required set) for data only one downstream phase needs; schema churn risk on the already-shipped pack |
| B. Separate KPI fetch step in the new phase (**chosen**) | New phase fetches fact-pack → runs memo-feed | Keeps memo-fetch stable; mirrors how regime-pack (Phase 2) already does a second fetch — precedented in-skill |
| C. Generalize the TW 月營收 block into the KPI section now | One unified operational-series treatment | Different cadence (monthly MOPS vs quarterly XBRL), different market; merging now couples two data models in one slice — deferred with re-trigger (next TW memo touch) |
| D. New MUST gate row for derived-Q4 labeling | Gate names the KPI input | Recon shows gates are deliberately input-generic; CHK-CIT-004/007 already cover fabrication + verbatim warnings; adding a named-input row breaks that genericity for no caught-failure evidence |

My take: **B**, plus protocol-side Operating-KPI block placed as thesis-support
(buy-side convention) with full table in the exhibit/appendix, not a sell-side
front-page quarterly-update section. Conditional reversal: if the fetch step turns
out to need >1 new client entry-point, revisit A (schema extension) before building
a parallel fetch path.

## Decision

Build the smallest end state above: separate fetch in a new report-equity-memo phase
(US-only, explicit skip elsewhere) → `kpi_memo_feed.py` CLI as the single analysis
entry → memo-feed JSON path added to the Phase-4 Resource Paths → new Operating-KPI
block in the investing-team protocol/template (derived-Q4 cells tagged per-cell with
footnote; coverage gaps truncate + footnote; <4 real quarters → appendix-only per
research) → both plugins version-bumped. Gate contract unchanged. We will NOT:
extend the memo-fetch schema, touch the TW 月營收 block, add gate rows, or backfill
analysis-kpi SKILL.md beyond the memo-feed surface this slice ships.

**Derived-Q4 presentation policy (user-ratified 2026-07-18: option a): the memo
trend table INCLUDES derived-Q4 cells, each tagged per-cell as derived with a
footnote naming the formula (FY − ΣQ1-3) and the plural source accessions. Two
standing safeguards: a series with <4 reported quarters renders appendix-only
(never in the body); non-US tickers with true reported Q4 never receive the
derived tag (out of scope this slice anyway — US-only).**

## What Becomes Obsolete

- Nothing retires (recon: zero existing KPI wiring — greenfield seam).
- `kpi_memo_feed.py` moves from dangling-producer to consumed — its "unconsumed"
  status note in analysis-kpi SKILL.md:392-426 must be updated in this change.
- analysis-kpi SKILL.md is stale vs shipped code (documents only `build`; omits the
  whole quarterly/derive_q4/coverage surface). This slice updates the memo-feed
  portion it touches; the full doc backfill is adjacent debt → BACKLOG note, not
  this slice (surgical-edit rule).

## Out of Scope

- JP/TW/KR/CN quarterly KPI (EDINET 短信 has true Q4 — implied-Q4 tagging would be
  wrong there; separate slice).
- TW 月營收 block generalization (re-trigger: next TW memo protocol touch).
- New gates / checklist rows; any change to CHK-CIT/CHK-THX text.
- memo-fetch pack schema changes.
- Full analysis-kpi SKILL.md backfill (BACKLOG).
- Real-ticker quarterly dogfood is a validation activity riding this slice's
  verification, not a scope item.

## Open Questions

- ~~Q1 (user fork): derived-Q4 presentation~~ — **RESOLVED 2026-07-18: user chose
  (a) include-and-tag** (per-cell derived tag + formula footnote; <4 reported
  quarters → appendix-only; no derived tag for true-Q4 markets). Rejected: (b)
  reported-only body + appendix lane; (c) full exclusion. This ruling is the
  flagship value judgment candidate for a future PRINCIPLES.md run.
- Q2 (plan-time, not user-blocking): which KPI bindings ship in the first memo run —
  reuse the shipped default binding set vs per-ticker config. Planner decides from
  kpi_memo_feed.py's existing contract.

## Size call

> 1 hour, ≥2 plugins, ≥4 modules → `writing-plans` → SDD after user sign-off.
