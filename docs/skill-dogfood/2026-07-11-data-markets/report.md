# Dogfood report — `data-markets`

> This report is an **agent-actionable fix dossier**: its consumer is the
> **main agent that will FIX the skill** (plus the user reviewing raw
> outputs). Every finding localizes the defect, states why it broke, and
> names a *suggested* edit class.
>
> **Findings are ADVISORY.** Dogfood discovers + points; it does NOT
> apply edits. The main agent decides and makes the change. The user is
> the final calibrator — read the surfaced raw outputs (appendix), then
> drive the fix by talking to the main agent.

## Metadata

| Field | Value |
|---|---|
| Skill path | `investing-toolkit/skills/data-markets/` (working tree, main @ b0929a31 content) |
| Skill version | investing-toolkit v2.3.0 (post PR #536 consolidation) |
| Date | 2026-07-11 |
| Passes run | activation (real harness) · executor+auditor×2 · cold-reader · env-var live probe ×2 |
| Model pinned | activation: `claude-haiku-4-5-20251001`; executor/auditors/cold-reader: sonnet (Claude Code `--model sonnet`, CLI 2.1.207) |
| Activation fidelity | real-harness sandbox (`claude -p --setting-sources project`, 7-skill menu, isolation canary-verified) |

## Headline

**The consolidation's core mechanism WORKS.** Cold-start (fresh empty
cache, `XDG_CACHE_HOME` honored) → snapshot 2330.TW exit 0 in 21.2s, TW
regime-pack exit 0 in 9.7s; re-run 0.8s served from cache; `_status`
fail-loud contract present in every payload; **mechanical JSON-Schema
validation: 0 errors on all 3 artifacts** (both auditors, independently,
Draft7 + Draft2020-12); price/valuation internally coherent
(marketCap/sharesOutstanding = latest_close = TWSE ClosingPrice = 2415.0).
Both blind auditors: `PASS_WITH_ISSUES`.

The issues are at the edges: trigger-vocabulary collisions, one
cache-metadata contract violation on TWSE sections, provenance
re-stamping, and doc ambiguities a first-time weak model trips on.

## Activation metrics (Probe A — 27 queries × 2 runs, haiku)

| Metric | Value |
|---|---|
| Should-fire TP rate | **82.5%** (33/40) |
| Should-NOT TN rate | **78.6%** (11/14) |
| Consistent misses | F18 (EDINET ja) 0/2 · F20 (cache health-check snapshot) 0/2 |
| Partial misses | F01 1/2 (→report-stock-snapshot) · F11 1/2 (NONE) · F14 1/2 (→router) |
| Consistent over-trigger | N02 (regime classification ask) 2/2 → data-markets |
| Partial over-trigger | N03 1/2 (comps 分析結論 → data-markets) |

## Severity summary

| Severity | Count |
|---|---|
| Critical | 0 |
| High | 4 |
| Medium | 3 |
| Low | 3 |
| **Total** | 10 |

> Post-report correction: FINDING-001 downgraded High → Low after live
> re-verification (harness substitutes `${CLAUDE_SKILL_DIR}` at load
> time; see the finding's correction block). Counts above reflect the
> corrected state. Companion positive result: `agents/data-fetcher.md`'s
> `${CLAUDE_PLUGIN_ROOT}` references also resolve to absolute paths at
> agent dispatch (live-probed) — closes the PR #536 next-touch nit
> "live-resolution check".

## Findings

### FINDING-001 [CORRECTED post-report — original verdict was WRONG]: `${CLAUDE_SKILL_DIR}` is substituted at SKILL.md load time; it is only absent from the bash env

- **Severity**: Low (originally misreported as High)
- **Category**: Progressive-disclosure (doc note) — NOT a Cold-start defect
- **Pass**: informed (live env probe + rendered-body inspection) + blind (cold-reader flagged the term as undefined)
- **Correction (2026-07-11, same session)**: the original finding claimed "THE invocation fails if executed literally" because `CLAUDE_SKILL_DIR` is UNSET in the bash env. The env observation was correct but the conclusion was wrong: **the harness performs textual substitution of `${CLAUDE_SKILL_DIR}` in the SKILL.md body when the skill loads**, so the model never sees the variable — it sees the absolute path. Verified in BOTH contexts: installed plugin renders line 27 as `uv run /Users/kouko/.claude/plugins/cache/monkey-skills/investing-toolkit/2.3.0/skills/data-markets/scripts/pack.py …`; sandbox project skill renders `uv run <sandbox>/.claude/skills/data-markets/scripts/pack.py …` (grep of envtest.jsonl / envtest-plugin.jsonl transcripts). Skill-invocation `args` strings get the same substitution.
- **What remains true**: (a) the variable is NOT in the bash env (`SKILL_DIR=[UNSET]`, `PLUGIN_ROOT=[UNSET]`) — any command composed *outside* the rendered body (a dispatch packet quoting the raw file, a subagent Reading the working-tree SKILL.md directly) gets the unexpanded literal; (b) a cold reader of the raw file cannot know the substitution exists — the mechanism is undocumented in the file.
- **Why the dogfood got it wrong**: Probe B's executor was deliberately fed the *raw working-tree file* (never installed), and the env probe tested only bash env — neither exercised the real fired-skill rendering path. The dogfood's own valid-but-wrong trap, caught by re-verification when a fix was about to be applied.
- **Location**: `SKILL.md:§THE invocation` (line 27) — no code change needed
- **Suggested fix direction**: do NOT remove the variable (it is load-bearing: harness-substituted, and `tests/test_path_conventions.py` mandates the `${CLAUDE_SKILL_DIR}/scripts/` self-ref form). Optional one-line doc note for raw-file readers: "`${CLAUDE_SKILL_DIR}` is substituted by the harness at load time; it is not a bash env var."
- **Repro**: invoke `investing-toolkit:data-markets` via the Skill tool and inspect the rendered §THE invocation; contrast with `echo "${CLAUDE_SKILL_DIR:-UNSET}"` in bash (UNSET)

### FINDING-002: "snapshot" vocabulary collision loses data-layer queries to `report-stock-snapshot`

- **Severity**: High
- **Category**: Trigger-miss
- **Pass**: blind
- **Probe prompt**: F20「資料層健康檢查：抓一次 AAPL snapshot 確認快取有寫進去」(0/2); F01「抓 2330.TW 的 snapshot 資料包」(1/2)
- **Expected**: route to `data-markets` (data pack + cache = Layer-1 vocabulary)
- **Actual**: routed to `report-stock-snapshot` 3 of 4 runs
- **Transcript evidence**: F20_r1/r2, F01_r1 → Skill input `{"skill":"report-stock-snapshot"}`
- **Root cause**: both descriptions lead with "snapshot"; the report skill's "auto-detects market by suffix, dispatches data-markets snapshot" makes it a superset-sounding claim. Nothing in data-markets' description claims cache / health-check / 資料層 vocabulary.
- **Why static review missed it**: each description is individually accurate; the collision only exists relative to the sibling menu — exactly what a distractor-set probe measures.
- **Location**: frontmatter `description` (data-markets), possibly also report-stock-snapshot's
- **Suggested fix direction**: add discriminating tokens to data-markets description: "raw data pack / cache layer / 原始資料包（非渲染卡片）"; per-skill description budget 1536 chars — room exists.
- **Repro**: rerun F01/F20 in the sandbox

### FINDING-003: source-name queries (EDINET, SEC EDGAR) miss — 18 client/source names live only in the body

- **Severity**: High
- **Category**: Trigger-miss
- **Pass**: blind
- **Probe prompt**: F18「EDINET から 6758 の有価証券報告書データを取得して」(0/2); F14 "download SEC EDGAR filings data for TSLA as a data pack" (1/2)
- **Expected**: data-markets (EDINET/EDGAR are its own Tier-A sources)
- **Actual**: F18 → `using-investing-toolkit` (r1), no skill fired (r2); F14_r2 → router
- **Transcript evidence**: runs/F18_r1.jsonl Skill input `{"skill":"using-investing-toolkit"}`
- **Root cause**: the router sees only the frontmatter description, which names zero concrete sources; the 18-source inventory sits in the body (loaded post-fire only).
- **Why static review missed it**: body coverage looks complete; description/body split is invisible unless you probe with description-only context.
- **Location**: frontmatter `description`
- **Suggested fix direction**: add the highest-salience source names (SEC EDGAR, EDINET, TWSE, FRED…) to the description — watch the 1536-char per-skill budget and list-eviction behavior.
- **Repro**: rerun F14/F18 in the sandbox

### FINDING-004: analysis-shaped regime question consistently over-triggers the data layer

- **Severity**: High
- **Category**: Over-trigger
- **Pass**: blind
- **Probe prompt**: N02「現在美國是什麼總經 regime？用 Investment Clock 幫我判斷」
- **Expected**: `analysis-macro-regime` (a classification verdict, not a fetch)
- **Actual**: `data-markets` 2/2
- **Transcript evidence**: N02_r1/r2 Skill input `{"skill":"data-markets"}`
- **Root cause**: "regime-pack" token in data-markets' description + haiku not weighing "Pure I/O, no analysis" as a negative gate; analysis-macro-regime's description is input-mechanics-first ("Input: --input <country=path,…>"), which reads less like the user's question than "regime" does.
- **Why static review missed it**: the "no analysis" clause exists — static review credits it; behavioral probing shows a weak router doesn't honor it against a stronger token match.
- **Location**: frontmatter `description` (both skills)
- **Suggested fix direction**: data-markets description: "regime-pack = raw macro indicators only; regime *classification/判斷* → analysis-macro-regime". Consider making analysis-macro-regime's description lead with the user-facing job ("classify the current macro regime") before input mechanics.
- **Repro**: rerun N02 in the sandbox

### FINDING-005: TWSE sections violate the declared 3-key cache contract (`_cache:"hit"` without age/ttl)

- **Severity**: High
- **Category**: Output-quality (contract violation)
- **Pass**: blind (auditor 2), self-verified by orchestrator
- **Probe prompt**: executor run2 (cache-hit pass) of `pack.py --ticker 2330.TW --pack snapshot`
- **Expected**: SKILL.md §Cache-hit metadata — hit ⇒ trio `_cache`/`_cache_age_seconds`/`_cache_ttl_seconds`
- **Actual**: `.twse.daily_price.data`, `.twse.pe_pb_yield.data`, `.twse.margin_balance.data` carry only `_cache:"hit"`; full-tree scan finds no age/ttl in those leaves. yfinance/finmind leaves carry the full trio.
- **Transcript evidence**: `jq -r '.twse.daily_price.data | keys'` → `_cache,_provenance,action,data,fetched_at,note,ticker`
- **Root cause (hypothesis)**: TWSE client sets `_cache` itself instead of (or at a different level than) letting `cache_util.load_cache` inject the trio — integration seam missed in the 23-client migration.
- **Why static review missed it**: offline tests assert cache round-trip correctness, not per-client metadata-key completeness; payload is well-formed JSON either way.
- **Location**: `scripts/twse_client.py` × `scripts/cache_util.py` seam (SKILL.md §Cache-hit metadata is the claim)
- **Suggested fix direction**: route TWSE cache loads through the same `load_cache` injection path; add a metadata-completeness assertion to tests (every `_cache:"hit"` leaf must carry age+ttl).
- **Repro**: `probe-b/snapshot-2330-run2.json` + the jq above

### FINDING-006: `fetched_at` re-stamped at cache-write time for MOPS/TWSE — provenance untraceable on hit

- **Severity**: Medium
- **Category**: Output-quality (provenance)
- **Pass**: blind (auditor 1), self-verified
- **Expected**: a cache-hit serves the original fetch's payload, `fetched_at` = original fetch time (yfinance/finmind behave this way: 04:36:01Z preserved across runs)
- **Actual**: mops/twse sections in run2 show `fetched_at: 04:36:24Z` — matching neither run1's emitted value (04:36:03Z) nor run2's wall time; ≈ run1's end-of-run cache-write moment. 6/9 sections affected.
- **Transcript evidence**: `jq '.mops.company_basic.data.fetched_at'` run1 → `04:36:03Z` (miss), run2 → `04:36:24Z` (hit)
- **Root cause (hypothesis)**: those clients stamp `fetched_at` at cache-save (or re-stamp at compose), so the emitted document and the cached document disagree.
- **Why static review missed it**: needs two live runs against the same cache + a cross-run diff; no offline fixture exercises that.
- **Location**: mops/twse client cache-save paths
- **Suggested fix direction**: stamp once at fetch, persist verbatim; add cross-run invariance test for `fetched_at` under hit.
- **Repro**: compare `probe-b/snapshot-2330-run1.json` vs `run2.json` at the paths above

### FINDING-007: yfinance emits a phantom flat bar (2026-07-10, volume 0) one day past TWSE's authoritative last session

- **Severity**: Medium
- **Category**: Output-quality (upstream data quality)
- **Pass**: blind (auditor 2)
- **Actual**: `.yfinance.history.data.data[-1]` = 2026-07-10 with `open=high=low=close=2415.0, volume:0`, while TWSE `daily_price` says the last real session is 1150709 (=2026-07-09)
- **Root cause**: upstream yfinance behavior on non-trading days; pack passes it through untouched (correct for a pure-fetch layer) but downstream consumers can mistake it for a real bar.
- **Why static review missed it**: only visible on a live fetch near a TW non-trading weekday.
- **Location**: `scripts/yf_client.py` (or a documented caveat in `references/market-tw.md`)
- **Suggested fix direction**: either drop zero-volume trailing bars, or document "cross-check yfinance last bar against twse.daily_price" as a consumer caveat.
- **Repro**: `jq '.yfinance.history.data.data[-1]' probe-b/snapshot-2330-run1.json`

### FINDING-008: cache-metadata injection LEVEL is ambiguous in SKILL.md (top-level vs per-section vs mixed depths)

- **Severity**: Medium
- **Category**: Progressive-disclosure (doc precision)
- **Pass**: triangulated — cold-reader (blind), executor (informed), auditor 2 (blind) each flagged independently
- **Expected**: doc states where the keys live
- **Actual**: §Cache-hit metadata reads as if `_cache` is a top-level payload key; reality is per-section injection, and MOPS even carries two differently-populated markers at two depths (`.mops.company_basic.data._cache` without age/ttl vs `.mops.company_basic.data.data._cache` with trio)
- **Transcript evidence**: cold-reader Q5c quote: "A fresh fetch has no `_cache` key (or `_cache: "miss"` where the client sets it explicitly)" — "undefined *which* clients"; executor: 「頂層 JSON 沒有 `_cache` key…實際是逐 section 注入」
- **Root cause**: doc written from cache_util's viewpoint ("a payload" = one client blob), reader parses "payload" as the emitted document
- **Why static review missed it**: sentence is true under the author's referent; only a cold reader exposes the referent ambiguity
- **Location**: `SKILL.md:§Cache-hit metadata`
- **Suggested fix direction**: one sentence: "keys are injected per fetched section (e.g. `.yfinance.info.data._cache`), never at document top level; miss-marking varies by client." Normalizing the MOPS double-marker belongs with FINDING-005's seam fix.
- **Repro**: cold-reader transcript + jq paths above

### FINDING-009: internal vocabulary undefined for first-time readers (Tier-A/Tier-2, `_provenance`, Layer 1/2/3)

- **Severity**: Low
- **Category**: Jargon-leak
- **Pass**: blind (cold-reader)
- **Actual**: cold-reader lists `Tier-A`/`Tier-2`, `_provenance`, "Layer 1/2/3", "XDG-style ladder", unnamed "plugin-data env var" as undefined on first contact
- **Why static review missed it**: in-house reviewers share the toolkit vocabulary (bias accumulation)
- **Location**: `SKILL.md` body (§API keys, header)
- **Suggested fix direction**: one-line glosses or a pointer ("authority tiers defined in references/market-*.md")
- **Repro**: Probe C transcript Q4

### FINDING-010: sibling `analysis-screener` description still cites pre-consolidation path `data-{country}/pack.py`

- **Severity**: Low
- **Category**: Convention-violation (adjacent skill, consolidation residue)
- **Pass**: informed (found while extracting distractor descriptions)
- **Actual**: `analysis-screener/SKILL.md` frontmatter: "a data-pack JSON from data-{country}/pack.py --pack screener-batch" — the five `data-{country}` skills no longer exist; `analysis-macro-regime` was updated, this one was missed
- **Location**: `investing-toolkit/skills/analysis-screener/SKILL.md` frontmatter
- **Suggested fix direction**: `data-{country}/pack.py` → `data-markets/scripts/pack.py`; joins the PR #536 next-touch nit list (same class as the stale `us-schema-*.json` descriptions)
- **Repro**: `grep 'data-{country}' investing-toolkit/skills/analysis-screener/SKILL.md`

## Raw outputs appendix

- **Probe A** (54 routing runs + canary + parse table): `<scratchpad>/trigger-sandbox/runs/*.jsonl`; corpus: `<scratchpad>/trigger-corpus.json`; runner: `<scratchpad>/run_probe_a.sh`. Full per-run routing table reproduced in-session (F01–F20, N01–N07 × r1/r2).
- **Probe B artifacts**: `<scratchpad>/probe-b/snapshot-2330-run1.json` (210 KB), `snapshot-2330-run2.json` (211 KB), `regime-tw.json` (3.5 MB) + per-command stderr files. Executor trajectory: 3 commands, exits 0/0/0, no `WARNING:` lines.
- **Auditor verdicts**: both `PASS_WITH_ISSUES`; auditor 1 = schema 0 errors (Draft7) + provenance mismatch; auditor 2 = schema 0 errors (Draft2020-12) + TWSE trio violation + phantom bar. Full texts in session task outputs.
- **Env-var probes**: `<scratchpad>/trigger-sandbox/envtest.jsonl` (project-skill), `<scratchpad>/envtest-plugin.jsonl` (installed plugin).
- **Probe C cold-reader**: full answers in session task output (5 questions, quoted evidence).
- `<scratchpad>` = `/private/tmp/claude-501/-Users-kouko--supacode-repos-monkey-skills-finacial-analytics-r2/e6dfa6a2-7662-4991-bfb8-646e59580659/scratchpad` (session-local; gone after cleanup — findings above carry the extracted evidence).

## Addendum — analysis-layer E2E (2026-07-11, out of original dogfood scope)

Two live E2E runs after the data-markets dogfood closed, at user request:

1. **Data-layer full chain (sandbox, haiku, 48.5s)**: 「抓 2330.TW 的 snapshot 資料包」→ routed to `report-stock-snapshot` (FINDING-002 collision replayed) → it correctly delegated to `data-markets/scripts/pack.py` → 205.9 KB JSON fetched, fresh-cache dirs written, rendered card returned. Chain PASSED end-to-end despite the routing detour.
2. **Analysis full chain (real installed env, sonnet, timed out at my 580s cap mid-flight — NOT a tool failure)**: 「分析 2330.TW 值不值得買」→ `using-investing-toolkit` → `report-equity-memo` → 7× pack.py fetches (v2.3.0 plugin-cache absolute paths, prod-verified) → regime TW+US → comps → DCF → investing-team worker/evaluator delegation packet being prepared at cutoff. Routing + data + delegation-entry all healthy. **Two live analysis-layer defects observed** (operator-caught, need reproduction before fixing — `analysis-dcf` / `analysis-comps`, not data-markets):
   - **DCF unit bug**: `analysis-dcf/scripts/dcf_compute.py` returned per-share intrinsic value ~1e6× off ("回報值比實際每股內在價值大了約 100 萬倍"); operator hand-corrected to ~1,686 TWD/share vs price 2,415. Adjacent to the known next-arc item "DCF 硬編 US tax/WACC 套非美股" but distinct (unit conversion, not parameterization).
   - **Comps batch-format mismatch**: multi-ticker US-peer batch fetch produced a file `analysis-comps` cannot parse — 4 peers (INTC/UMC/GFS/ASML) all null until refetched per-ticker. Data→analysis interface contract gap (batch output shape vs comps input expectation).
   - Wall-clock note: full memo path needs >10 min; plan timeouts accordingly.
3. **Haiku full-memo fake-completion (2/2, conclusive)**: same prompt on `claude-haiku-4-5-20251001` — both runs route correctly (`using-investing-toolkit` → `report-equity-memo`) then STOP at 5 turns / ~30s with ZERO Bash, ZERO Agent dispatches, zero files, while the final message claims「結果會以完整投資備忘錄形式存檔」. The report-equity-memo workflow provides no execution-forcing gate a weak model can't narrate past. Matches the documented haiku stall pattern (machine memory: "Haiku implementer stalls, no commit"). Severity for weak-model users: High — a haiku-tier session silently delivers nothing while claiming the pipeline ran. Contrast: sonnet on the same prompt executes the full pipeline. Fix direction (advisory, report-equity-memo scope): early hard checkpoint, e.g. "Phase 1 is not complete until the data-pack file exists on disk — verify with ls before proceeding/replying"; or a SKILL.md clause forbidding completion claims without artifact paths.

## Coverage caps (no silent truncation)

- Activation corpus: 27 queries × 2 runs on haiku only; no sonnet/opus activation baseline was run (weak-model bound by design — user asked for 弱模型).
- Probe B exercised market=tw only (snapshot + regime-pack + cache-hit rerun); us/jp/kr/cn packs, batch modes (`--tickers`), exit-2/64 paths, and the unwritable-cache tempdir fallback were NOT behaviorally exercised this round (exit-64 and five-market smoke were covered in-arc pre-merge).
- Meta-dogfood bias: the dogfood target and the dogfood harness live in the same repo family; auditors/cold-reader were fresh-context subagents, orchestrator verified High findings by hand.
