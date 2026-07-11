# Plan: investing-toolkit dogfood fix package (post data-markets consolidation)

Source brief: docs/skill-dogfood/2026-07-11-data-markets/report.md (dogfood findings; user-approved scope: fixes ①②③④ + architecture option A) — no separate brainstorming brief; bug-fix package per family on-ramp negative guard. Diagnoses (systematic-debugging Phase 1-4, both hypotheses VERIFIED) are embedded in each task's Context.
Total tasks: 7
Critical-path depth: 1 (all tasks independent; no inter-task dependencies)
Execution order: parallel-where-possible
Plan-document-reviewer verdict: PASS (round 2, 14/14, 2026-07-11)

## Task 1 — DCF unit-contract fix (drop $M assumption, absolute-currency input)
- Description: Remove the spurious `* 1_000_000` per-share conversion in dcf_compute.py and align the script (and its fixtures) to data-markets' actual absolute-currency output contract.
- Module: investing-toolkit/skills/analysis-dcf
- Files touched: investing-toolkit/skills/analysis-dcf/scripts/dcf_compute.py, investing-toolkit/tests/analysis/test_analysis_dcf.py, investing-toolkit/tests/analysis/fixtures/dcf_tw_absolute_currency.json (new), investing-toolkit/tests/analysis/fixtures/aapl_memo_fetch.json (reshape to absolute USD + update dependent assertions)
- Context paths:
  - investing-toolkit/skills/analysis-dcf/scripts/dcf_compute.py (bug at :143 `per_share = (equity_value * 1_000_000) / shares_outstanding`; docstring :24 claims `# $M` input)
  - investing-toolkit/skills/data-markets/scripts/pack_tw.py (:264 emits `"unit": "TWD"` absolute; all 5 markets emit absolute currency — verified)
  - Diagnosis facts: 2330.TW memo-fetch → mid = 1,685,938,388.84 (wrong, exactly 1e6×); removing the factor → 1685.94 (matches hand-calc). Existing fixture aapl_memo_fetch.json was hand-authored in $M (revenue[0]=383285) — it bakes the wrong contract in; reshape to absolute (383285000000) so tests exercise the real Layer-1 shape.
- Acceptance:
  - RED: tests/analysis/test_analysis_dcf.py::test_per_share_sane_magnitude_absolute_currency_input fails (mid > 1e9 on absolute-currency TW fixture)
  - GREEN: mid within plausible per-share band (assert 50 <= mid <= 20000 for the TW fixture; tighter exact-value assertion with tolerance welcome); full package suite still green after aapl fixture reshape
- External surfaces: none (stdlib + repo scripts only)
- Dependencies: none
- Independent: true
- Brief item covered: report Addendum item 2 "DCF unit bug: dcf_compute.py returned per-share intrinsic value ~1e6× off"

## Task 2 — comps batch-peer expansion + fail-loud unresolvable ticker
- Description: Teach comps_compute.py's `--peers` loader to expand a multi-ticker batch pack (info: {T1:{...},T2:{...}}) into N peer entries, and make an unresolvable ticker loud (warning/_provenance entry or non-zero exit) instead of silent all-null; document the batch shape in analysis-comps SKILL.md Input Contract.
- Module: investing-toolkit/skills/analysis-comps
- Files touched: investing-toolkit/skills/analysis-comps/scripts/comps_compute.py, investing-toolkit/skills/analysis-comps/SKILL.md, investing-toolkit/tests/analysis/test_analysis_comps.py, investing-toolkit/tests/analysis/fixtures/comps_peer_batch_two_tickers.json (new)
- Context paths:
  - investing-toolkit/skills/analysis-comps/scripts/comps_compute.py (:1374-1383 peer loop assumes 1 path = 1 ticker; `_resolve_ticker` :123-130 falls back to filename stem; `_extract_multiples` :133-150 `info.get(bogus)` → all None, exit 0)
  - investing-toolkit/skills/data-markets/schemas/us-schema-comps-multiples.json (:5 — batch `--tickers T1,T2` is the documented peer-fetch shape; pack_us.py:600-643 implements it correctly)
  - Diagnosis facts: repro 4/4 (2 local + 2 E2E transcripts); peers[0].ticker becomes filename stem (e.g. "BATCH-PEERS"), all multiples null. Contract verdict: comps under-implements the shape the data layer advertises.
- Acceptance:
  - RED: tests/analysis/test_analysis_comps.py::test_batch_peer_file_multiple_tickers_not_silently_nulled fails (batch fixture → 1 bogus peer, null multiples)
  - GREEN: batch fixture expands to 2 peer entries keyed by real tickers with non-null multiples; a peers file whose ticker cannot be resolved produces a loud signal (assert warning/_provenance or non-zero exit), never silent nulls
- External surfaces: none
- Dependencies: none
- Independent: true
- Brief item covered: report Addendum item 2 "Comps batch-format mismatch: 4 peers all null until refetched per-ticker"

## Task 3 — TWSE cache-hit metadata trio (FINDING-005)
- Description: Route TWSE section cache loads through the same cache_util injection path as yfinance/finmind so every `_cache:"hit"` leaf carries `_cache_age_seconds` + `_cache_ttl_seconds`, per SKILL.md's declared 3-key contract.
- Module: investing-toolkit/skills/data-markets
- Files touched: investing-toolkit/skills/data-markets/scripts/twse_client.py, investing-toolkit/tests/data/test_cache_metadata_completeness.py (new; place per tests/data/ conventions)
- Context paths:
  - investing-toolkit/skills/data-markets/scripts/cache_util.py (load_cache injects the trio — reference behavior)
  - investing-toolkit/skills/data-markets/SKILL.md §Cache-hit metadata (the declared contract)
  - Dogfood FINDING-005 facts: `.twse.daily_price.data|keys` on a cache-hit run = `_cache,_provenance,action,data,fetched_at,note,ticker` — trio absent; yfinance leaf carries `{_cache:"hit",_cache_age_seconds:23,_cache_ttl_seconds:3600}`. Root-cause hypothesis (unverified): twse client sets `_cache` itself instead of using load_cache injection — implementer verifies via code read before fixing (systematic-debugging Phase 2 for this one lives inside the task).
- Acceptance:
  - RED: test_cache_metadata_completeness fails — a twse cached payload (use tmp cache dir + two loads, offline-safe fixture/mock per tests/data/ conventions) yields `_cache:"hit"` without age/ttl
  - GREEN: every `_cache:"hit"` leaf in twse payloads carries the full trio; suite green
- External surfaces: TWSE OpenAPI client code (network-marked tests stay @network; the new test must run offline via fixtures/mocks per house convention)
- Dependencies: none
- Independent: true
- Brief item covered: FINDING-005 "TWSE sections violate the declared 3-key cache contract"

## Task 4 — data-markets trigger vocabulary + cache-metadata doc clarification (FINDING-002/003 + 008 + regime negative clause of 004)
- Description: Rewrite data-markets' frontmatter description to add discriminating vocabulary (raw data pack / cache layer / 原始資料包（非渲染卡片）, top source names SEC EDGAR·EDINET·TWSE·FRED, and a negative clause routing regime *classification/判斷* to analysis-macro-regime); clarify §Cache-hit metadata injection level (per-section, not document top level; miss-marking varies by client).
- Module: investing-toolkit/skills/data-markets
- Files touched: investing-toolkit/skills/data-markets/SKILL.md
- Context paths:
  - docs/skill-dogfood/2026-07-11-data-markets/report.md (FINDING-002/003/004/008 — probe prompts + failing queries F01/F20/F18/F14/N02)
  - Constraint: per-skill description budget 1536 chars (harness silently evicts oversized descriptions — machine memory feedback_skill_list_description_budget_eviction)
- Acceptance:
  - RED (diagnostic): grep shows description lacks 原始資料包/cache/source-name tokens and regime negative clause; §Cache-hit metadata lacks per-section clarification
  - GREEN: grep assertions pass; description block ≤1536 chars (`wc -c`); trigger re-probe of failing queries F01/F20/F18/F14/N02 in the existing sandbox (≥2 runs each, haiku) — report actual rates; behavioral probe is best-effort evidence, grep assertions are the hard gate
- External surfaces: none
- Dependencies: none
- Independent: true
- Brief item covered: FINDING-002 "snapshot vocabulary collision", FINDING-003 "source-name queries miss", FINDING-008 "cache-metadata level ambiguous", FINDING-004 negative-clause half (data-markets side)

## Task 5 — analysis-screener stale path fix (FINDING-010)
- Description: Replace the pre-consolidation reference `data-{country}/pack.py` in analysis-screener's frontmatter description with the current `data-markets/scripts/pack.py` path.
- Module: investing-toolkit/skills/analysis-screener
- Files touched: investing-toolkit/skills/analysis-screener/SKILL.md
- Context paths:
  - docs/skill-dogfood/2026-07-11-data-markets/report.md (FINDING-010)
- Acceptance:
  - RED (diagnostic): `grep 'data-{country}' investing-toolkit/skills/analysis-screener/SKILL.md` matches
  - GREEN: grep no longer matches; description references data-markets/scripts/pack.py; description ≤1536 chars
- External surfaces: none
- Dependencies: none
- Independent: true
- Brief item covered: FINDING-010 "analysis-screener description still cites pre-consolidation path"

## Task 6 — analysis-macro-regime description leads with user-facing job (FINDING-004)
- Description: Rewrite analysis-macro-regime's frontmatter description to lead with the user-facing job ("classify the current macro regime / 判斷當前總經 regime") before input mechanics, so analysis-shaped regime questions route to it instead of the data layer.
- Module: investing-toolkit/skills/analysis-macro-regime
- Files touched: investing-toolkit/skills/analysis-macro-regime/SKILL.md
- Context paths:
  - docs/skill-dogfood/2026-07-11-data-markets/report.md (FINDING-004 — N02 2/2 over-trigger; current description is input-mechanics-first)
- Acceptance:
  - RED (diagnostic): description's first sentence is input-mechanics-first (starts with "Pure-compute … Input: --input …" before naming the user-facing job)
  - GREEN: first sentence names the classification job in user vocabulary (EN + 中文 trigger tokens 判斷/regime 分類); input mechanics moved after; ≤1536 chars; sandbox re-probe of N02 (≥2 runs, haiku) reported as best-effort evidence
- External surfaces: none
- Dependencies: none
- Independent: true
- Brief item covered: FINDING-004 "analysis-shaped regime question consistently over-triggers the data layer" (analysis-macro-regime side)

## Task 7 — report-equity-memo artifact hard checkpoints (architecture option A)
- Description: Add execution-forcing artifact gates to report-equity-memo's phase workflow: each phase is complete ONLY when its named artifact exists on disk (verify with ls before proceeding), and the final reply MUST cite produced artifact paths — no completion claims without artifacts (anti fake-completion clause targeting weak models).
- Module: investing-toolkit/skills/report-equity-memo
- Files touched: investing-toolkit/skills/report-equity-memo/SKILL.md
- Context paths:
  - docs/skill-dogfood/2026-07-11-data-markets/report.md (Addendum item 3: haiku 2/2 fake-completion — 5 turns, zero Bash/Agent, zero files, claims 「結果會以完整投資備忘錄形式存檔」)
- Acceptance:
  - RED (diagnostic): grep shows no artifact-existence gate / no completion-claim clause in report-equity-memo/SKILL.md phase sections
  - GREEN: each phase section names its artifact + an ls-verify step; a MUST clause forbids completion claims without citing artifact paths; cold-read check — one fresh-context sonnet agent, given only the edited SKILL.md, answers "when may you tell the user the memo is done?" with the artifact-gate rule (wording-contract floor per house convention); optional best-effort: one haiku sandbox re-run
- External surfaces: none
- Dependencies: none
- Independent: true
- Brief item covered: report Addendum item 3 "Haiku full-memo fake-completion (2/2)" + user-approved architecture option A (最小硬化)

## Notes
- No brainstorming brief exists: scope was set by the dogfood report + explicit user instruction (「請開始修」+ option A choice). Treated as the user-override path with the dogfood report as brief-equivalent; every task's Brief item covered points at a concrete report finding.
- Both bug diagnoses (Tasks 1-2) completed systematic-debugging Phases 1-4 with hypotheses VERIFIED before this plan; key facts embedded above so implementers need not re-derive them.
- Comps fix direction (expand batch vs loud-fail-only) decided by orchestrator: expand + loud fallback, because data-markets' schema documents batch as the intended peer shape and house doctrine is fail-loud (rejecting silent-null is the same disease class as PR #536's exit-0-with-error-slots).
- Task 4's behavioral trigger re-probe is evidence, not a hard gate — routing is probabilistic; the deterministic grep assertions gate the task.
- All 7 tasks Independent: true with pairwise-disjoint Files touched → single parallel dispatch wave eligible per dispatching-parallel-agents. (Amended post-split from 5→7; renumbering only, schema unchanged — re-review done in round 2.)
- Parallel-wave commit discipline: implementers do NOT run git commit (one-worktree interleaved-commit race, machine memory feedback_parallel_implementers_one_worktree_interleave_commits); orchestrator commits per task sequentially after the wave, staging each task's Files touched explicitly (never git add -A).
