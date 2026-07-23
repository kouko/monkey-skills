# Plan: TW financial-sector iXBRL ingestion (-fh / -basi / -bd / -ins)

Source brief: docs/loom/specs/2026-07-22-tw-ixbrl-fh-ingestion.md
Total tasks: 14
Critical-path depth: 5 (≤5) — longest chain T1→T2→T9→T11→T12 (and T1→T4→T5→T11→T12,
  T1→T14→T9→T11→T12); T13 sits at depth 4, T14 at depth 2 — off the critical path.
Execution order: parallel-where-possible
Plan-document-reviewer verdict: PASS (2026-07-22, amended plan) — round 1 PASSED after
fixing Task 9's Dependencies syntax; plan then amended post-PASS with Task 13 (DCF
financial-sector refusal guard, kickoff decision A); re-review of the amended plan
PASSED clean (depth 5 confirmed, T13 at depth 4 off critical path, DAG acyclic, all
Independent:true file-sets disjoint, brief coverage complete).

## Notes
- All measurement evidence (verbatim concept names, real numbers) lives in
  `scratchpad/fh-measurement{,-round2,-round3,-round4}.md`; raw filing bodies in
  `scratchpad/fh_raw*/` (23 filings, already fetched + verified against the live
  extractor). Fixtures copy from there.
- The four canonical builders (T5-T8) all edit `twse_ixbrl_canonical.py` and so are
  `Independent: false` (SDD dispatches them sequentially), but each depends ONLY on
  T4's classifier+registry — they form ONE dependency level, not a chain. Same for
  the two notes tasks (T9, T10) on `twse_ixbrl_notes.py`.
- Layer separation (per CLAUDE.md): this arc is DATA-LAYER-first. The `sector_class`
  marker + omission of DCF-trigger fields keeps downstream DCF fail-loud. Kickoff
  briefing surfaced that "fail-loud via missing revenue" would trip the memo's Phase-3
  artifact gate (`report-equity-memo/SKILL.md:344`) and hard-crash a TW financial memo
  — so the user ratified pulling the analysis-layer DCF sector-refusal guard forward
  into THIS arc (Task 13), realized as a structured `not_applicable` result in
  `dcf_compute.py` (testable) rather than a prose skip in the orchestrator (untestable).
- Kickoff decision: memo hard-crash on financial-sector DCF → resolve in the analysis
  layer: `dcf_compute.py` emits a structured `not_applicable` dcf.json for
  `sector_class=financial` (user decision A, 2026-07-22). The BACKLOG "DCF sector-refusal
  guard" item is CONSUMED by Task 13.
- Mid-implementation discovery (T9): MOPS serves the WHOLE financial family (-fh/-basi/
  -bd/-ins) as UTF-8 despite a `charset=big5` declaration, while -ci filings are genuine
  Big5 (measured at byte level: 2882 NameOfTheCompany bytes are UTF-8 國泰世華銀行; a
  big5hkscs decode garbles them). The existing hardcoded `big5hkscs` decode in
  `twse_ixbrl_fetch.py:117` therefore silently corrupts every Chinese-text (nonNumeric)
  fact for all financial filers — a latent bug that only manifests for the families this
  arc adds. Numeric facts + fact counts are unaffected (ASCII), so T1/T5-T8 stay valid.
  Resolution (kickoff-style decision A, agent-proceeded after an extended user-veto window
  on an inferable correctness fix consistent with the ratified goal): add Task 14 — a
  smart-decode (UTF-8-strict first, big5hkscs fallback) — as a prerequisite for the notes
  tasks (T9/T10), which need legible bank-subsidiary names to state NPL scope honestly.
- Decision Log: `NetIncomeLoss` vs `ProfitLossAttributableToOwnersOfParent` (T5) — the
  -fh canonical uses the consolidated bottom line (`ProfitLossAttributableToOwnersOfParent`),
  documented in a code comment; two-way-door, late-vetoable.
- Version bump / CHANGELOG / plugin.json mirror happen at finishing (collides with the
  parallel `feat-prose-kpi-part-2` worktree on those coordination files — resolve then,
  against the then-current origin/main).

## Task 1 — Capture real financial-sector fixtures
- Description: Copy real MOPS Big5 iXBRL bodies (already fetched + verified in
  `scratchpad/fh_raw*/`) into repo fixtures, one per taxonomy sub-shape, with a
  one-line provenance cite (co_id + period + "verified live 2026-07"). Mark the new
  `.html` fixtures `binary` in `.gitattributes` (Big5 breaks utf-8 tooling — proven
  in the -ci arc). Add a parametrized smoke test asserting each parses to >0 facts.
- Module: tests fixtures
- Files touched: investing-toolkit/tests/data/fixtures/twse_ixbrl_2882_2026Q1_C.html,
  investing-toolkit/tests/data/fixtures/twse_ixbrl_2890_2026Q1_C.html,
  investing-toolkit/tests/data/fixtures/twse_ixbrl_2801_2026Q1_C.html,
  investing-toolkit/tests/data/fixtures/twse_ixbrl_2820_2026Q1_A.html,
  investing-toolkit/tests/data/fixtures/twse_ixbrl_6005_2026Q1_C.html,
  investing-toolkit/tests/data/fixtures/twse_ixbrl_2867_2026Q1_A.html,
  investing-toolkit/tests/data/fixtures/twse_ixbrl_2851_2025Q1_A.html,
  investing-toolkit/.gitattributes,
  investing-toolkit/tests/data/test_twse_ixbrl_fixtures.py
- Context paths:
  - scratchpad/fh-measurement.md (fixture provenance + fact counts)
  - investing-toolkit/tests/data/fixtures/twse_ixbrl_2330_2024Q3_C.html (existing -ci fixture shape)
  - investing-toolkit/.gitattributes (existing binary-mark pattern)
- Acceptance:
  - RED: test_twse_ixbrl_fixtures.py parametrized over the 7 new fixtures — fails (fixtures absent) then passes when each `parse_ixbrl_facts` yields the measured fact count (±0, exact-count guard per the -ci arc).
  - GREEN: 7 fixtures present, binary-marked, each parses to its measured fact count.
- Dependencies: none
- Independent: false
- Brief item covered: "Fixtures captured from real filings (Big5, `binary` in `.gitattributes`), provenance-cited … ≥1 per taxonomy, plus a two-bank-subsidiary FHC and ≥2 insurer sub-shapes"

## Task 2 — Parser: capture tuple attributes
- Description: Extend `parse_ixbrl_facts` to capture `tupleRef` and `tupleID`
  attributes into the emitted fact dict (currently dropped). Additive — existing
  fields and the existing exact-fact-count guard stay valid.
- Module: twse_ixbrl_parser
- Files touched: investing-toolkit/skills/data-markets/scripts/twse_ixbrl_parser.py,
  investing-toolkit/tests/data/test_twse_ixbrl_parser.py
- Context paths:
  - investing-toolkit/skills/data-markets/scripts/twse_ixbrl_parser.py (:143 parse_ixbrl_facts, :82 _ATTR_RE, :170 fact dict build)
  - investing-toolkit/tests/data/fixtures/twse_ixbrl_2882_2026Q1_C.html (has NPL tuples)
- Acceptance:
  - RED: a test asserting a parsed NPL fact from the 2882 fixture carries non-empty `tupleID`/`tupleRef` keys — fails now (attrs dropped).
  - GREEN: fact dict includes `tupleRef`/`tupleID`; a non-tuple fact carries them as None/absent; existing parser tests still green.
- External surfaces: none (pure text parsing, stdlib re)
- Dependencies: Task 1 completes first
- Independent: true
- Brief item covered: "Parser tuple support — capture `tupleRef`/`tupleID` in the fact dict, keyed by subsidiary"

## Task 3 — Fetch: report_id C→A fallback
- Description: Add a fetch helper that tries `report_id="C"` (consolidated) then falls
  back to `"A"` (individual) when C returns the absence sentinel — filers publishing
  only an individual report (insurers, bills-finance) need A. Correct the module
  comment claiming "A" is never served.
- Module: twse_ixbrl_fetch
- Files touched: investing-toolkit/skills/data-markets/scripts/twse_ixbrl_fetch.py,
  investing-toolkit/tests/data/test_twse_ixbrl_fetch.py
- Context paths:
  - investing-toolkit/skills/data-markets/scripts/twse_ixbrl_fetch.py (:94 fetch_ixbrl_body, :123 fetch_with_season_fallback, :64 build_t164sb01_url, :74 is_not_found_body)
- Acceptance:
  - RED: a test (stubbed HTTP) where C returns the 檔案不存在 sentinel and A returns a body — the new helper returns the A body + "A"; fails now (no such helper).
  - GREEN: helper returns (body, "A") on C-absent/A-present; returns C body + "C" when C present; returns None when both absent.
- External surfaces: HTTP GET to MOPS t164sb01 (existing surface; stub in tests via the module's existing requests-stub pattern)
- Dependencies: none
- Independent: true
- Brief item covered: "Fetch rule … try `C` then fall back to `A` rather than key on type"

## Task 4 — 5-way taxonomy classifier + dispatch registry
- Description: Add `classify_taxonomy(facts) -> "ci"|"fh"|"basi"|"bd"|"ins"` (by
  namespace-prefix inspection) replacing the `_is_fh_taxonomy` boolean, and refactor
  `build_canonical` to look up the classification in a builder REGISTRY (dict keyed by
  taxonomy tag), defaulting to the existing unsupported marker for tags with no
  registered builder yet. No behavior change for `-ci` (still routes to its mapping)
  or for financial tags (still unsupported until T5-T8 register builders).
- Module: twse_ixbrl_canonical
- Files touched: investing-toolkit/skills/data-markets/scripts/twse_ixbrl_canonical.py,
  investing-toolkit/tests/data/test_twse_ixbrl_canonical.py
- Context paths:
  - investing-toolkit/skills/data-markets/scripts/twse_ixbrl_canonical.py (:126 _is_fh_taxonomy, :229 build_canonical, :238 unsupported branch, :49 _CONCEPT_MAP)
  - all 7 fixtures from Task 1 (one per taxonomy for the parametrized classifier test)
- Acceptance:
  - RED: `classify_taxonomy` returns the correct tag for each of the 5 taxonomy fixtures (parametrized) — fails now (function absent).
  - GREEN: classifier correct on all fixtures; `build_canonical` on a -ci fixture unchanged; on -fh/-basi/-bd/-ins still returns unsupported (no builder yet); `_is_fh_taxonomy` removed or wrapped.
- Dependencies: Task 1 completes first
- Independent: true
- Brief item covered: "5-way taxonomy classifier + sector marker — replace the `_is_fh_taxonomy` boolean with a classifier returning one of `ci`/`fh`/`basi`/`bd`/`ins`"

## Task 5 — -fh (FHC) canonical builder
- Description: Register a `-fh` builder in the T4 registry: three statements from the
  measured `ifrs-full:`/`tifrs-bsci-fh:` concepts (deposits `DepositsFromCustomers`/
  `DepositsFromBanks` kept DISTINCT from interest-bearing borrowings `BondsIssued`/
  `OtherBorrowings`/`CommercialPapersIssuedNet`/repo), NII, profit/EPS. Emit
  `sector_class="financial"` and OMIT the DCF-trigger fields (revenue/ebit/fcf/capex/
  total_debt) so downstream DCF fails loud. Remove `-fh` from the unsupported default.
- Module: twse_ixbrl_canonical
- Files touched: investing-toolkit/skills/data-markets/scripts/twse_ixbrl_canonical.py,
  investing-toolkit/tests/data/test_twse_ixbrl_canonical.py
- Context paths:
  - scratchpad/fh-measurement.md (§2882 verbatim concepts + real numbers for value assertions)
  - investing-toolkit/skills/data-markets/scripts/twse_ixbrl_canonical.py (T4 registry + _CONCEPT_MAP pattern)
- Acceptance:
  - RED: `build_canonical(2882_facts)` returns a canonical with balance_sheet.total_equity == the measured Equity value, deposits and borrowings as distinct keys, `sector_class=="financial"`, and NO `total_debt`/`revenue` keys — fails now (unsupported).
  - GREEN: assertion passes with real traced values; `NetIncomeLoss`-vs-`ProfitLossAttributableToOwnersOfParent` resolved to the consolidated bottom line deliberately (documented in a code comment, per the measured mismatch caveat).
- External surfaces: none (pure mapping over parsed facts)
- Dependencies: Task 4 completes first
- Independent: false
- Brief item covered: "`-fh` (FHC) canonical + bank asset-quality notes — three statements (deposits vs interest-bearing borrowings distinct)"

## Task 6 — -basi (standalone bank + bills-finance) canonical builder
- Description: Register a `-basi` builder: three statements from `tifrs-bsci-basi:`/
  `ifrs-full:` concepts (deposit sub-lines rolled to a comparable shape). Emit
  `sector_class="financial"`, omit DCF-trigger fields. Degrade GRACEFULLY for
  bills-finance `-basi` filers (華票-type) that carry NO deposits / NO NPL — absence
  is normal, not an error.
- Module: twse_ixbrl_canonical
- Files touched: investing-toolkit/skills/data-markets/scripts/twse_ixbrl_canonical.py,
  investing-toolkit/tests/data/test_twse_ixbrl_canonical.py
- Context paths:
  - scratchpad/fh-measurement-round2.md (§-basi concepts), scratchpad/fh-measurement-round4.md (§華票 no-NPL/no-deposit degrade)
  - investing-toolkit/tests/data/fixtures/twse_ixbrl_2801_2026Q1_C.html, twse_ixbrl_2820_2026Q1_A.html
- Acceptance:
  - RED: `build_canonical(2801_facts)` returns three-statement canonical w/ sector_class; AND `build_canonical(2820_facts)` (bills-finance) returns a valid canonical with deposits/NPL fields absent-but-not-erroring — fails now.
  - GREEN: both pass; bills-finance canonical omits deposit/NPL keys without raising.
- External surfaces: none
- Dependencies: Task 4 completes first
- Independent: false
- Brief item covered: "`-basi` (standalone bank + bills-finance) canonical … Must degrade gracefully for bills-finance `-basi` filers"

## Task 7 — -bd (broker) canonical builder
- Description: Register a `-bd` builder: three statements from `tifrs-bsci-bd:`/
  `ifrs-full:` concepts (no NPL, no deposits). Emit `sector_class="financial"`, omit
  DCF-trigger fields.
- Module: twse_ixbrl_canonical
- Files touched: investing-toolkit/skills/data-markets/scripts/twse_ixbrl_canonical.py,
  investing-toolkit/tests/data/test_twse_ixbrl_canonical.py
- Context paths:
  - scratchpad/fh-measurement-round2.md + round3.md (§-bd concepts; 44 shared across 3 brokers)
  - investing-toolkit/tests/data/fixtures/twse_ixbrl_6005_2026Q1_C.html
- Acceptance:
  - RED: `build_canonical(6005_facts)` returns three-statement canonical w/ `sector_class=="financial"`, no total_debt/revenue — fails now.
  - GREEN: passes with real traced values (assets/equity/cash from the fixture).
- External surfaces: none
- Dependencies: Task 4 completes first
- Independent: false
- Brief item covered: "`-bd` (broker) canonical — separate taxonomy, no NPL. Stable"

## Task 8 — -ins (insurer) canonical builder
- Description: Register an `-ins` builder covering the 67-concept UNION across life /
  P&C / reinsurance. Key on `tifrs-bsci-ins:` PLUS an `ifrs-full:` fallback for the
  reinsurer sub-shape (which books insurance liabilities under generic
  `ifrs-full:LiabilitiesArisingFromInsuranceContracts`/`ReinsuranceAssets`). Emit
  `sector_class="financial"`, omit DCF-trigger fields.
- Module: twse_ixbrl_canonical
- Files touched: investing-toolkit/skills/data-markets/scripts/twse_ixbrl_canonical.py,
  investing-toolkit/tests/data/test_twse_ixbrl_canonical.py
- Context paths:
  - scratchpad/fh-measurement-round3.md (§-ins 67-concept union table + reinsurer ifrs-full fallback)
  - investing-toolkit/tests/data/fixtures/twse_ixbrl_2867_2026Q1_A.html (life), twse_ixbrl_2851_2025Q1_A.html (reinsurer)
- Acceptance:
  - RED: `build_canonical(2867_facts)` (life) emits insurance-contract-liability via `tifrs-bsci-ins:`; AND `build_canonical(2851_facts)` (reinsurer) emits the SAME canonical field via the `ifrs-full:` fallback — the reinsurer assertion fails now (would drop the field).
  - GREEN: both sub-shapes populate the insurance-liability canonical field; sector_class set.
- External surfaces: none
- Dependencies: Task 4 completes first
- Independent: false
- Brief item covered: "`-ins` (insurer) canonical — covers the 67-concept UNION … keys on `tifrs-bsci-ins:` PLUS an `ifrs-full:` fallback for the reinsurer sub-shape"

## Task 9 — -fh NPL/coverage notes via tuple
- Description: Add a `-fh` asset-quality note extractor to `twse_ixbrl_notes.py`:
  resolve NPL ratio / coverage ratio / NPL amount / gross receivables by loan
  category using the `tupleRef`/`tupleID` attributes (from T2), tagged with the
  banking-subsidiary name (`tifrs-notes:NameOfTheCompany`). Handle post-merger FHCs
  with DUPLICATED parallel NPL trees (NPL1+NPL2) — key by subsidiary, not per-filer.
- Module: twse_ixbrl_notes
- Files touched: investing-toolkit/skills/data-markets/scripts/twse_ixbrl_notes.py,
  investing-toolkit/tests/data/test_twse_ixbrl_notes.py
- Context paths:
  - scratchpad/fh-measurement.md (§2882 NPL tuple tree + TotalLoans CoverageRatio=1031.17%)
  - investing-toolkit/skills/data-markets/scripts/twse_ixbrl_notes.py (:104 _select_current_fact, :111 extract_curated_notes)
  - investing-toolkit/tests/data/fixtures/twse_ixbrl_2882_2026Q1_C.html, twse_ixbrl_2890_2026Q1_C.html (dup-tree)
- Acceptance:
  - RED: extractor on 2882 returns the TotalLoans coverage ratio == 1031.17 (the measured value) tagged with 國泰世華銀行 — fails now (no extractor; tuple-blind selection would grab a wrong loan-category row).
  - GREEN: correct TotalLoans coverage on 2882; on 2890 (two bank subs) BOTH subsidiaries' NPL trees resolve distinctly.
- External surfaces: none
- Dependencies: Tasks 2, 4, 14 complete first
- Independent: false
- Brief item covered: "`-fh` … NPL/coverage/NPL-amount/gross-receivables … tagged with banking-subsidiary name"

## Task 10 — -basi NPL/coverage notes via context_ref suffix
- Description: Add a `-basi` asset-quality note extractor: resolve NPL/coverage from
  the `context_ref` suffix pattern (`..._TotalLoansMember`) + `Member`-suffixed
  concept names — NO tuple parser needed. Return empty gracefully for bills-finance
  `-basi` filers (no NPL).
- Module: twse_ixbrl_notes
- Files touched: investing-toolkit/skills/data-markets/scripts/twse_ixbrl_notes.py,
  investing-toolkit/tests/data/test_twse_ixbrl_notes.py
- Context paths:
  - scratchpad/fh-measurement-round2.md (§-basi context_ref-suffix NPL), round4.md (§華票 no-NPL)
  - investing-toolkit/tests/data/fixtures/twse_ixbrl_2801_2026Q1_C.html, twse_ixbrl_2820_2026Q1_A.html
- Acceptance:
  - RED: extractor on 2801 returns its TotalLoans coverage ratio (measured value) via the context_ref-suffix path — fails now.
  - GREEN: 2801 coverage resolved; 2820 (bills-finance) returns empty/absent without raising.
- External surfaces: none
- Dependencies: Tasks 4, 14 complete first
- Independent: false
- Brief item covered: "`-basi` … + NPL/coverage read from `context_ref` suffix (NO tuple parser needed)"

## Task 11 — CLI run_pipeline: fetch-fallback + financial composition
- Description: Wire `run_pipeline` (twse_ixbrl.py) to use the T3 C→A fetch fallback,
  and to compose the financial canonical + asset-quality notes by taxonomy (call the
  T4 classifier; route -fh/-basi through their note extractors; -bd/-ins canonical
  only). Keep the -ci path unchanged.
- Module: twse_ixbrl (CLI)
- Files touched: investing-toolkit/skills/data-markets/scripts/twse_ixbrl.py,
  investing-toolkit/tests/data/test_twse_ixbrl_cli.py
- Context paths:
  - investing-toolkit/skills/data-markets/scripts/twse_ixbrl.py (:70 run_pipeline, :81 fetch call)
  - all 7 fixtures (offline: stub fetch to return fixture bodies)
- Acceptance:
  - RED: `run_pipeline` for an insurer (fetch stubbed: C-absent, A-present) returns an -ins canonical (fetched via A); for a -fh filer returns canonical + NPL notes — fails now (unsupported / C-only fetch).
  - GREEN: both paths produce correct structured output offline; -ci path regression-free.
- External surfaces: subprocess/CLI composition of the 4 sibling modules + MOPS fetch (stub in tests, per the existing offline-CI stub pattern — module-level requests import must be stubbed before import, per the -ci arc's CI fix)
- Dependencies: Tasks 3, 5, 6, 7, 8, 9, 10 complete first
- Independent: false
- Brief item covered: "Wired into memo-fetch … fetch layer routes insurers to `report_id=A`"

## Task 12 — pack_tw memo-fetch wiring + degradation
- Description: Wire `pack_memo_fetch` (pack_tw.py) to accept financial-taxonomy
  `twse_ixbrl` results (currently labeled "-ci industrial") and surface the canonical
  + asset-quality notes; on iXBRL failure, degrade to the yfinance stub (non-empty),
  as the -ci path does — no regression.
- Module: pack_tw
- Files touched: investing-toolkit/skills/data-markets/scripts/pack_tw.py,
  investing-toolkit/tests/data/test_data_markets_tw.py
- Context paths:
  - investing-toolkit/skills/data-markets/scripts/pack_tw.py (:413 pack_memo_fetch, :471-494 twse_ixbrl wiring, :205 yfinance-stub fallback)
- Acceptance:
  - RED: `pack_memo_fetch` for a financial ticker (run_client stubbed to a financial canonical) surfaces sector_class + canonical + notes in the pack; on stubbed failure it falls back to the yfinance stub — fails now (labeled -ci-only; financial result mis-handled).
  - GREEN: financial canonical+notes surfaced; failure → yfinance stub not empty; existing -ci memo path regression-free (package-level tests green).
- External surfaces: subprocess run_client to twse_ixbrl.py (stub in tests); yfinance fallback (existing surface)
- Dependencies: Task 11 completes first
- Independent: false
- Brief item covered: "Wired into memo-fetch with iXBRL-failure degradation to yfinance stub (as `-ci`)"

## Task 13 — DCF financial-sector refusal guard
- Description: Make `dcf_compute.py` recognize `sector_class="financial"` in its input
  JSON and emit a structured `{"not_applicable": "financial-sector", "reason": ...}`
  result (written to the dcf.json output) with a clean exit, INSTEAD of raising
  `ValueError` on the deliberately-absent `income_statement.revenue`. This satisfies
  the memo's Phase-3 artifact gate with a "DCF N/A for financials" marker rather than
  crashing the memo. Realizes user kickoff-decision A; consumes the BACKLOG "DCF
  sector-refusal guard" item. (Enforcement lives in `dcf_compute.py` — testable — not
  in orchestrator prose, per the Claude-prose-can't-pytest lesson.)
- Module: analysis-dcf
- Files touched: investing-toolkit/skills/analysis-dcf/scripts/dcf_compute.py,
  investing-toolkit/tests/analysis/test_analysis_dcf.py
- Context paths:
  - investing-toolkit/skills/analysis-dcf/scripts/dcf_compute.py (:175 missing-revenue raise, :333 _validate_input_shape, :385 main)
  - investing-toolkit/tests/analysis/fixtures/dcf_short_revenue.json (existing shape for a financial-style input fixture)
- Acceptance:
  - RED: `main()` on an input carrying `sector_class="financial"` and no `income_statement.revenue` writes a dcf.json containing `not_applicable == "financial-sector"` and exits 0 — fails now (raises ValueError on missing revenue).
  - GREEN: financial input → structured not_applicable dcf.json, exit 0; a normal industrial input still computes DCF unchanged (regression-free); package-level test suite green.
- External surfaces: none (pure compute over input JSON; no network)
- Dependencies: Task 5 completes first
- Independent: true
- Brief item covered: "sector_class marker + DCF-trigger-field omission keep the downstream valuation fail-loud, not silent-wrong" (realized as the structured DCF refusal, pulled from BACKLOG per kickoff decision A)

## Task 14 — Smart-decode financial-family filings (UTF-8-first, Big5 fallback)
- Description: MOPS serves the whole financial family (-fh/-basi/-bd/-ins) as UTF-8
  despite a `charset=big5` declaration, while -ci filings are genuine Big5. The
  hardcoded `big5hkscs` decode in `twse_ixbrl_fetch.py` silently corrupts every Chinese-
  text fact for financial filers (measured at byte level). Replace it with a shared
  `decode_ixbrl_document(raw: bytes) -> str` helper: try UTF-8 strict first, fall back to
  `big5hkscs` (errors="replace") on UnicodeDecodeError. Place the helper in a STDLIB-only
  module (twse_ixbrl_parser.py — parse-adjacent, avoids the requests module-level-import
  trap for test consumers), and have twse_ixbrl_fetch.py call it. This unblocks the notes
  tasks (T9/T10), which need legible bank-subsidiary names.
- Module: twse_ixbrl_parser (helper) + twse_ixbrl_fetch (call site)
- Files touched: investing-toolkit/skills/data-markets/scripts/twse_ixbrl_parser.py,
  investing-toolkit/skills/data-markets/scripts/twse_ixbrl_fetch.py,
  investing-toolkit/tests/data/test_twse_ixbrl_parser.py
- Context paths:
  - investing-toolkit/skills/data-markets/scripts/twse_ixbrl_fetch.py (~:117/:120 the hardcoded big5hkscs decode)
  - investing-toolkit/tests/data/fixtures/twse_ixbrl_2882_2026Q1_C.html (financial=UTF-8), twse_ixbrl_2330_2024Q3_C.html (-ci=Big5)
- Acceptance:
  - RED: `decode_ixbrl_document(<2882 bytes>)` yields text containing `國泰世華銀行` (the bank-subsidiary name) — fails now (only big5hkscs exists, garbles it); AND `decode_ixbrl_document(<2330 bytes>)` decodes the genuine-Big5 -ci fixture without error/garble.
  - GREEN: helper UTF-8-first/Big5-fallback; fetch.py uses it; a financial fixture's Chinese text is legible, a -ci fixture still decodes correctly; existing fetch + fixture-count tests stay green (counts are ASCII-invariant).
- External surfaces: the MOPS t164sb01 HTTP body encoding (category-1) — grounded in the byte-level measurement of the committed fixtures (financial=UTF-8, -ci=Big5) cited in Notes; a fresh live probe is optional since the committed fixtures are the evidence.
- Dependencies: Task 1 completes first
- Independent: false
- Brief item covered: (mid-implementation correctness fix, Notes §Mid-implementation discovery) — enables honest bank-subsidiary-name tagging in `-fh`/`-basi` NPL notes
