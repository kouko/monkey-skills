# investing-toolkit v2.0.0 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Refactor investing-toolkit's 15 mixed-concern skills into a clean three-layer architecture (5 Data + 6 Analysis + 4 Report + 1 Router = 16 skills) and add `analysis-comps` to close the Comps gap vs Anthropic Financial Services.

**Architecture:** Way B three-layer split with country-bundled data skills. Cross-skill calls via main agent + temp-file path passing (zero sub-agent overhead). Batch fetch complexity lives in data layer via `--tickers` flag. Analysis layer is exception-free pure compute. Report layer handles cross-country grouping + cross-plugin delegation.

**Tech Stack:** Python (uv-managed scripts), yfinance / SEC EDGAR / EDINET / TWSE / MOPS / FRED clients, Markdown SKILL.md files, GitHub Actions CI for MD5 sync check.

**Spec reference:** `docs/superpowers/specs/2026-05-01-investing-toolkit-v2.0.0-three-layer-design.md`

**PR breakdown:**
- **PR 1** (v2.0.0-rc.1) — Three-layer refactor, 15 → 15 skill rearrange (no `analysis-comps` yet)
- **PR 2** (v2.0.0-rc.2) — Add `analysis-comps` + peer-discovery agent + `--pack comps-multiples` mode (15 → 16)
- **PR 3** (v2.0.0) — Documentation, i18n, changelog, migration guide

**Cross-PR dependencies:** PR 2 requires PR 1 merged (uses `data-{country}` + `report-equity-memo`). PR 3 requires PR 1 + PR 2.

---

## File Structure (post-refactor)

```
investing-toolkit/
├── docs/
│   ├── adr/
│   │   └── 0001-data-analysis-report-layers.md           [NEW PR 1]
│   ├── design-principles.md                              [UPDATE PR 3]
│   ├── mcp-setup.md
│   └── i18n/glossary-{en,zh-TW,ja}.md
├── scripts/                                              [DEPRECATED, kept for migration]
├── skills/
│   ├── data-us/                                          [NEW PR 1, merge of us-macro + us-stock-snapshot fetch]
│   │   ├── SKILL.md
│   │   └── scripts/
│   │       ├── yfinance_client.py
│   │       ├── sec_edgar_client.py
│   │       ├── fred_client.py
│   │       └── pack.py
│   ├── data-jp/                                          [NEW PR 1]
│   ├── data-tw/                                          [NEW PR 1]
│   ├── data-kr/                                          [NEW PR 1]
│   ├── data-cn/                                          [NEW PR 1]
│   ├── analysis-dcf/                                     [RENAME PR 1, was dcf-valuation]
│   │   ├── SKILL.md
│   │   ├── references/dcf-template.md
│   │   └── scripts/dcf_compute.py
│   ├── analysis-comps/                                   [NEW PR 2]
│   │   ├── SKILL.md
│   │   └── scripts/comps_compute.py
│   ├── analysis-screener/                                [SPLIT PR 1, pure compute]
│   ├── analysis-technical/                               [RENAME PR 1, was technical-snapshot]
│   ├── analysis-portfolio/                               [SPLIT PR 1, compute part]
│   ├── analysis-macro-regime/                            [RENAME PR 1, was macro-regime-snapshot]
│   ├── report-equity-memo/                               [RENAME PR 1, was investment-memo-writer]
│   ├── report-stock-snapshot/                            [3-INTO-1 PR 1, country auto-routing]
│   ├── report-portfolio-review/                          [SPLIT PR 1, orchestration part]
│   ├── report-screener-list/                             [NEW PR 1, split from stock-screener]
│   └── using-investing-toolkit/                          [UPDATE PR 1, router table]
├── plugin.json                                           [UPDATE PR 1, version bump]
└── tests/                                                [NEW PR 1, smoke + regression]
    ├── test_data_us_pack.py
    ├── test_data_jp_pack.py
    ├── test_data_tw_pack.py
    ├── test_data_kr_pack.py
    ├── test_data_cn_pack.py
    ├── test_analysis_comps.py                            [PR 2]
    ├── test_report_screener_list.py
    ├── test_skill_md5_sync.py                            [PR 1, CI runs]
    └── test_router_paths.py
```

CI files:
- `.github/workflows/check-script-sync.yml`                [NEW PR 1]
- `.github/workflows/test.yml` (existing, extend)

---

## PR 1 — Three-Layer Refactor (v2.0.0-rc.1)

### Task 1: Create worktree branch + capture baseline

**Files:**
- Branch: `feat/v2.0.0-three-layer`

- [ ] **Step 1: Create branch from main**

```bash
cd /Users/kouko/GitHub/monkey-skills
git checkout -b feat/v2.0.0-three-layer main
```

- [ ] **Step 2: Capture baseline skill list for comparison**

```bash
ls investing-toolkit/skills/ > /tmp/v1-skill-list.txt
cat /tmp/v1-skill-list.txt
```

Expected output: 15 skill directories listed.

- [ ] **Step 3: Capture baseline MCP tool registrations**

```bash
test -f investing-toolkit/.mcp.json && cat investing-toolkit/.mcp.json > /tmp/v1-mcp.json || echo "no .mcp.json"
find investing-toolkit -name "mcp.json" 2>/dev/null
```

Record any mcp.json paths — these need updating in Task 14.

- [ ] **Step 4: Run existing smoke tests for regression baseline**

```bash
cd investing-toolkit
INVESTING_TOOLKIT_CACHE=/tmp/cache uv run scripts/yfinance_client.py --ticker AAPL --action info | head -20
```

Expected: JSON output with AAPL fields. Save to `/tmp/v1-aapl-info.json` for later regression check.

---

### Task 2: Phase 1 — Dispatch 11 agents in parallel (Batches A + B + D)

**Files:**
- Multi-agent — see per-agent prompt blocks below

This task dispatches all 11 agents in **a single message** using parallel `Agent` tool calls. The agents are independent: data-* don't import from analysis-*, analysis-* take pre-fetched JSON, ADR/CI is doc-only.

- [ ] **Step 1: Verify pre-conditions for parallel dispatch**

Confirm: branch is `feat/v2.0.0-three-layer`, working tree clean, no in-flight changes.

```bash
git status
git branch --show-current
```

Expected: branch `feat/v2.0.0-three-layer`, clean working tree.

- [ ] **Step 2: Dispatch all 11 agents in single message** (single tool-call message with 11 Agent invocations)

Use `domain-teams:worker` subagent type for each. Each agent receives:
- Spec path: `docs/superpowers/specs/2026-05-01-investing-toolkit-v2.0.0-three-layer-design.md`
- Source skill paths to read
- Target deliverable description
- Verification commands

**Agent A1 — `data-us`:**

```
Build skills/data-us/ by merging fetch logic from us-macro + us-stock-snapshot.

INPUTS:
- Read: investing-toolkit/skills/us-macro/SKILL.md (FRED macro coverage)
- Read: investing-toolkit/skills/us-stock-snapshot/SKILL.md (yfinance + SEC EDGAR fetch)
- Spec §4.2 data-us bundle definition

DELIVERABLES:
- skills/data-us/SKILL.md describing fetch-only role + pack types (snapshot/memo-fetch/comps-multiples/screener-batch/regime-pack)
- skills/data-us/scripts/yfinance_client.py (canonical copy from investing-toolkit/scripts/yfinance_client.py)
- skills/data-us/scripts/sec_edgar_client.py (canonical copy)
- skills/data-us/scripts/fred_client.py (canonical copy)
- skills/data-us/scripts/pack.py with --ticker (single) and --tickers (batch) modes per §4.2 contract
  - --pack snapshot: yfinance info + 2y price
  - --pack memo-fetch: yfinance + sec_edgar 10-K/10-Q/8-K + XBRL facts
  - --pack comps-multiples: yfinance multiples-only fields (P/E, P/S, P/B, EV/EBITDA, EV/Sales)
  - --pack screener-batch: yfinance batch (lightweight, supports --tickers)
  - --pack regime-pack: FRED macro series only

VERIFICATION:
- uv run skills/data-us/scripts/pack.py --ticker AAPL --pack snapshot returns valid JSON
- uv run skills/data-us/scripts/pack.py --tickers AAPL,MSFT,GOOGL --pack screener-batch returns 3-ticker JSON
- MD5 of yfinance_client.py matches investing-toolkit/scripts/yfinance_client.py

CONSTRAINTS:
- DO NOT delete us-macro/ or us-stock-snapshot/ yet (other agents may still reference)
- DO NOT modify any other skill
- Use ${CLAUDE_SKILL_DIR}/scripts/ convention in SKILL.md commands
```

**Agent A2 — `data-jp`:**

```
Build skills/data-jp/ by merging fetch logic from japan-macro + japan-stock-snapshot.

INPUTS:
- Read: investing-toolkit/skills/japan-macro/SKILL.md
- Read: investing-toolkit/skills/japan-stock-snapshot/SKILL.md (note EDINET tier-routing pattern)
- Spec §4.2 data-jp bundle

DELIVERABLES:
- skills/data-jp/SKILL.md
- skills/data-jp/scripts/yfinance_client.py (canonical copy)
- skills/data-jp/scripts/edinet_client.py (canonical copy)
- skills/data-jp/scripts/tdnet_client.py (canonical copy)
- skills/data-jp/scripts/boj_client.py (canonical copy)
- skills/data-jp/scripts/estat_client.py (canonical copy)
- skills/data-jp/scripts/ecb_client.py (canonical copy)
- skills/data-jp/scripts/pack.py with EDINET-key tier routing inside (Tier A if key set, yfinance fallback otherwise)

VERIFICATION:
- uv run skills/data-jp/scripts/pack.py --ticker 7203 --pack snapshot returns JSON
- Without EDINET_API_KEY: pack.py uses yfinance fallback path (provenance label "Tier 2 fallback")
- MD5 of all 6 client copies matches canonical investing-toolkit/scripts/

CONSTRAINTS:
- {ticker4} convention for JP tickers (4-digit codes); auto-append .T for yfinance
- DO NOT delete source skills yet
```

**Agent A3 — `data-tw`:**

```
Build skills/data-tw/ by merging fetch logic from taiwan-macro + taiwan-stock-snapshot.

INPUTS:
- Read: investing-toolkit/skills/taiwan-macro/SKILL.md (CBC + DGBAS + NDC + statgov)
- Read: investing-toolkit/skills/taiwan-stock-snapshot/SKILL.md (MOPS + TWSE + FinMind + yfinance)
- Spec §4.2 data-tw bundle

DELIVERABLES:
- skills/data-tw/SKILL.md
- 8 client scripts copied: yfinance, mops, twse_openapi, finmind, cbc, dgbas, ndc, statgov
- skills/data-tw/scripts/pack.py with MOPS+TWSE Tier A primary, FinMind Tier 2 fallback

VERIFICATION:
- uv run skills/data-tw/scripts/pack.py --ticker 2330.TW --pack snapshot returns JSON
- uv run skills/data-tw/scripts/pack.py --pack regime-pack returns Taiwan macro indicators
- MD5 of all 8 clients match canonical
```

**Agent A4 — `data-kr`:**

```
Build skills/data-kr/ by renaming korea-macro + adding stock support.

INPUTS:
- Read: investing-toolkit/skills/korea-macro/SKILL.md
- Spec §4.2 data-kr

DELIVERABLES:
- skills/data-kr/SKILL.md (note: KR has no stock-snapshot precedent; --pack snapshot uses yfinance only)
- skills/data-kr/scripts/yfinance_client.py
- skills/data-kr/scripts/fdr_client.py
- skills/data-kr/scripts/pack.py

VERIFICATION:
- uv run skills/data-kr/scripts/pack.py --ticker 005930.KS --pack snapshot returns JSON (Samsung)
- uv run skills/data-kr/scripts/pack.py --pack regime-pack returns 54 KR indicators
```

**Agent A5 — `data-cn`:**

```
Build skills/data-cn/ by renaming china-macro + adding stock support.

INPUTS:
- Read: investing-toolkit/skills/china-macro/SKILL.md
- Spec §4.2 data-cn

DELIVERABLES:
- skills/data-cn/SKILL.md
- skills/data-cn/scripts/yfinance_client.py
- skills/data-cn/scripts/nbs_client.py
- skills/data-cn/scripts/akshare_client.py
- skills/data-cn/scripts/fred_client.py (CN uses FRED for USDCNY)
- skills/data-cn/scripts/pack.py

VERIFICATION:
- uv run skills/data-cn/scripts/pack.py --ticker 600519.SS --pack snapshot returns JSON
- uv run skills/data-cn/scripts/pack.py --pack regime-pack returns NBS + Caixin PMI dual-source
```

**Agent B1 — `analysis-dcf`:**

```
Rename skills/dcf-valuation/ → skills/analysis-dcf/ and decouple from snapshot.

INPUTS:
- Read: investing-toolkit/skills/dcf-valuation/SKILL.md
- Read: investing-toolkit/skills/dcf-valuation/references/dcf-template.md
- Spec §4.3 analysis-dcf (pure compute, takes pre-fetched JSON)

DELIVERABLES:
- skills/analysis-dcf/SKILL.md (rewrite "Data Availability" section to say "input must be JSON from data-{country}/pack.py --pack memo-fetch")
- skills/analysis-dcf/references/dcf-template.md (copy as-is)
- skills/analysis-dcf/scripts/dcf_compute.py — accepts --input <data-pack-json-path>, computes 3-stage DCF + 3×3 sensitivity, outputs JSON
  - REMOVE any code that fetches data directly
  - Input contract: read JSON file containing income statement, cash flow, balance sheet from data layer

VERIFICATION:
- Create test fixture /tmp/aapl-memo-fetch.json from data-us/pack.py
- uv run skills/analysis-dcf/scripts/dcf_compute.py --input /tmp/aapl-memo-fetch.json returns intrinsic value JSON
- analysis-dcf SKILL.md contains zero references to fetching code

CONSTRAINTS:
- DO NOT delete skills/dcf-valuation/ yet (using-investing-toolkit router still references)
```

**Agent B2 — `analysis-screener`:**

```
Split skills/stock-screener/ — extract pure compute as skills/analysis-screener/.

INPUTS:
- Read: investing-toolkit/skills/stock-screener/SKILL.md
- Spec §4.3 analysis-screener (pure compute, accepts pre-batched data JSON)

DELIVERABLES:
- skills/analysis-screener/SKILL.md (input: pre-batched ticker data JSON; output: ranked top-N JSON)
- skills/analysis-screener/scripts/screener_compute.py
  - Accepts --input <batched-data-json-path>
  - Applies preset (value, growth, quality, momentum, etc.) filter + scoring
  - Outputs ranked JSON
  - REMOVE all fetch logic (yfinance_batch invocation, etc.)

VERIFICATION:
- Test fixture from data-us/pack.py --tickers AAPL,MSFT,GOOGL --pack screener-batch
- uv run skills/analysis-screener/scripts/screener_compute.py --input /tmp/screener-fixture.json --preset value returns ranked JSON
- screener_compute.py contains zero HTTP/network calls

CONSTRAINTS:
- DO NOT delete skills/stock-screener/ yet (will be replaced by analysis-screener + report-screener-list)
```

**Agent B3 — `analysis-technical`:**

```
Rename skills/technical-snapshot/ → skills/analysis-technical/, remove fetch.

INPUTS:
- Read: investing-toolkit/skills/technical-snapshot/SKILL.md
- Read: investing-toolkit/skills/technical-snapshot/scripts/ta_client.py (already pure compute)
- Spec §4.3 analysis-technical

DELIVERABLES:
- skills/analysis-technical/SKILL.md (pure compute, input: OHLCV from data-{country}/pack.py)
- skills/analysis-technical/scripts/ta_client.py (canonical home — copy from investing-toolkit/scripts/ta_client.py)
- skills/analysis-technical/scripts/ta_compute.py — wrapper accepting --input <ohlcv-json-path>, output indicator JSON

VERIFICATION:
- uv run skills/analysis-technical/scripts/ta_compute.py --input /tmp/aapl-snapshot.json returns RSI/MACD/BB/ATR/SMA JSON
- ta_client.py is the canonical copy; other analysis skills using TA reference its MD5

CONSTRAINTS:
- ta_client.py becomes the single canonical copy; CI sync (Task D) will check duplicates
```

**Agent B4 — `analysis-portfolio`:**

```
Split skills/invest-portfolio/ — extract compute as skills/analysis-portfolio/.

INPUTS:
- Read: investing-toolkit/skills/invest-portfolio/SKILL.md
- Spec §4.3 analysis-portfolio (compute part)

DELIVERABLES:
- skills/analysis-portfolio/SKILL.md (input: position holdings + price JSONs; output: P&L matrix)
- skills/analysis-portfolio/scripts/portfolio_compute.py
  - Accepts --holdings <csv-or-json-path> --prices <data-pack-json-path>
  - Computes per-position P&L, weight, contribution
  - REMOVE fetch logic + macro overlay (those go to report-portfolio-review)

VERIFICATION:
- uv run skills/analysis-portfolio/scripts/portfolio_compute.py --holdings test-holdings.csv --prices /tmp/prices.json returns P&L JSON
- Compute is pure (no network calls)

CONSTRAINTS:
- DO NOT delete invest-portfolio/ yet
```

**Agent B5 — `analysis-macro-regime`:**

```
Rename skills/macro-regime-snapshot/ → skills/analysis-macro-regime/.

INPUTS:
- Read: investing-toolkit/skills/macro-regime-snapshot/SKILL.md
- Spec §4.3 analysis-macro-regime

DELIVERABLES:
- skills/analysis-macro-regime/SKILL.md (input: macro indicators JSON from data-{country}/pack.py --pack regime-pack)
- skills/analysis-macro-regime/scripts/regime_compose.py — IC + GIP classification, accepts --input <regime-pack-json-paths> (one per country)

VERIFICATION:
- uv run skills/analysis-macro-regime/scripts/regime_compose.py --input us=/tmp/us-regime.json,jp=/tmp/jp-regime.json,tw=/tmp/tw-regime.json returns 5-country regime card JSON

CONSTRAINTS:
- DO NOT delete macro-regime-snapshot/ yet
```

**Agent D1 — ADR + CI sync check:**

```
Create ADR-0001 + CI MD5 sync workflow.

INPUTS:
- Read: docs/superpowers/specs/2026-05-01-investing-toolkit-v2.0.0-three-layer-design.md (full)

DELIVERABLES:
- investing-toolkit/docs/adr/0001-data-analysis-report-layers.md
  - Reference Way B three-layer architecture
  - Pin layer responsibilities (Data: I/O + tier routing + batch; Analysis: pure compute; Report: orchestration + format + cross-country routing)
  - State zero-exception rule for analysis layer
  - State acceptable duplications: yfinance ×5, fred ×2, ta_client ×N (CI-enforced sync)
  - Cross-skill data passing convention (main agent + temp file)
  - Slash command rename map (will be filled in PR 3)

- .github/workflows/check-script-sync.yml
  - Trigger on PR + push to main
  - Run a Python script that:
    1. Find all skills/data-*/scripts/yfinance_client.py — assert all MD5 identical
    2. Find all skills/*/scripts/fred_client.py — assert MD5 identical (data-us, data-cn)
    3. Find all skills/analysis-*/scripts/ta_client.py — assert MD5 identical to canonical (skills/analysis-technical/scripts/ta_client.py)
    4. Fail with diff message if drift detected

- investing-toolkit/scripts/sync-clients.sh
  - Shell helper: copy canonical clients to all skills' scripts/ that need them
  - Usage: developer runs after editing canonical to propagate to copies

VERIFICATION:
- ADR file > 100 lines, contains "Layer" / "Cross-skill" / "Sync" / "ADR-0001" sections
- CI workflow YAML validates: gh workflow view check-script-sync.yml
- sync-clients.sh runs without error on current state (will produce no-op since A1-A5 agents created identical copies)

CONSTRAINTS:
- DO NOT enforce CI as required check yet (will be in Task 14)
- Workflow status = optional during this PR; will become required in PR 3
```

- [ ] **Step 3: Wait for all 11 agents to complete**

Each agent returns its summary. Verify each agent's verification commands ran successfully.

- [ ] **Step 4: Sanity check directory state**

```bash
ls investing-toolkit/skills/ | sort
```

Expected new dirs present: `data-us data-jp data-tw data-kr data-cn analysis-dcf analysis-screener analysis-technical analysis-portfolio analysis-macro-regime`. Old dirs still present (intentional — Task 4 deletes them after Task 3 completes).

- [ ] **Step 5: Run all data-{country}/pack.py smoke tests**

```bash
cd investing-toolkit
INVESTING_TOOLKIT_CACHE=/tmp/cache uv run skills/data-us/scripts/pack.py --ticker AAPL --pack snapshot | jq '.ticker'
INVESTING_TOOLKIT_CACHE=/tmp/cache uv run skills/data-jp/scripts/pack.py --ticker 7203 --pack snapshot | jq '.ticker'
INVESTING_TOOLKIT_CACHE=/tmp/cache uv run skills/data-tw/scripts/pack.py --ticker 2330.TW --pack snapshot | jq '.ticker'
INVESTING_TOOLKIT_CACHE=/tmp/cache uv run skills/data-kr/scripts/pack.py --ticker 005930.KS --pack snapshot | jq '.ticker'
INVESTING_TOOLKIT_CACHE=/tmp/cache uv run skills/data-cn/scripts/pack.py --ticker 600519.SS --pack snapshot | jq '.ticker'
```

Expected: each returns the ticker as JSON string.

- [ ] **Step 6: Run batch fetch test**

```bash
INVESTING_TOOLKIT_CACHE=/tmp/cache uv run skills/data-us/scripts/pack.py --tickers AAPL,MSFT,GOOGL,META,AMZN --pack screener-batch | jq '. | length'
```

Expected: `5` (5 tickers in batch output).

- [ ] **Step 7: Commit Phase 1**

```bash
cd /Users/kouko/GitHub/monkey-skills
git add investing-toolkit/skills/data-* investing-toolkit/skills/analysis-* investing-toolkit/docs/adr/ .github/workflows/check-script-sync.yml investing-toolkit/scripts/sync-clients.sh
git commit -m "$(cat <<'EOF'
feat(investing-toolkit): three-layer refactor Phase 1 — data-* + analysis-* + ADR

Add 5 data-{country} skills (US/JP/TW/KR/CN) with pack.py supporting
single + batch fetch modes. Add 5 renamed/split analysis-* skills as
pure compute. Add ADR-0001 + CI MD5 sync check.

Old skills (us-macro, japan-macro, etc.) kept for Phase 2 to migrate
report skills before deletion.

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>
EOF
)"
```

---

### Task 3: Phase 2 — Dispatch 4 report-* agents in parallel (Batch C)

**Files:**
- See per-agent prompts below

This task dispatches the 4 report-* agents in **a single message**. They depend on Task 2 (data-* + analysis-* must exist) but are mutually independent.

- [ ] **Step 1: Verify Phase 1 outputs**

```bash
ls investing-toolkit/skills/data-us/scripts/pack.py
ls investing-toolkit/skills/analysis-dcf/scripts/dcf_compute.py
ls investing-toolkit/skills/analysis-screener/scripts/screener_compute.py
```

All exist. If any missing, halt and re-run failed Phase 1 agent.

- [ ] **Step 2: Dispatch all 4 report-* agents in single message**

Use `domain-teams:worker` subagent type for each.

**Agent C1 — `report-equity-memo`:**

```
Rename skills/investment-memo-writer/ → skills/report-equity-memo/ and update orchestration to call new data-* + analysis-* skills.

INPUTS:
- Read: investing-toolkit/skills/investment-memo-writer/SKILL.md (current orchestration pipeline)
- Spec §4.4 report-equity-memo

DELIVERABLES:
- skills/report-equity-memo/SKILL.md
  - Phase 1 — Data Fetch: replace explicit yfinance/sec_edgar/fred calls with `uv run skills/data-{country}/scripts/pack.py --ticker {ticker} --pack memo-fetch`
  - Phase 2 — Macro Regime: replace with `uv run skills/data-{country}/scripts/pack.py --pack regime-pack` + `uv run skills/analysis-macro-regime/scripts/regime_compose.py`
  - Phase 3 — Analysis: insert `uv run skills/analysis-dcf/scripts/dcf_compute.py` and (placeholder for) `analysis-comps` to be added in PR 2
  - Phase 4 — Delegate to `domain-teams:investing-team`
  - Phase 5 — Optional `domain-teams:docs-team` formatting
  - Country detection: `.TW/.TWO → data-tw`, `4-digit number → data-jp`, `.HK → data-cn` (per existing ticker conventions), default → data-us

VERIFICATION:
- skills/report-equity-memo/SKILL.md exists, ~120-200 lines
- All command paths resolve: data-{country}, analysis-dcf, analysis-macro-regime
- End-to-end mental trace: AAPL → data-us → analysis-dcf + analysis-macro-regime → investing-team → memo

CONSTRAINTS:
- DO NOT delete investment-memo-writer/ yet — handled in Task 5
- Leave a placeholder line for analysis-comps integration: "[PR 2: insert analysis-comps step here]"
```

**Agent C2 — `report-stock-snapshot`:**

```
Merge 3 country stock-snapshot skills into one report-stock-snapshot/ with auto-routing.

INPUTS:
- Read: investing-toolkit/skills/us-stock-snapshot/SKILL.md
- Read: investing-toolkit/skills/japan-stock-snapshot/SKILL.md
- Read: investing-toolkit/skills/taiwan-stock-snapshot/SKILL.md
- Spec §4.4 report-stock-snapshot

DELIVERABLES:
- skills/report-stock-snapshot/SKILL.md
  - Single skill, accepts ticker (any market)
  - Country detection routing: parse ticker suffix
    - .TW / .TWO → data-tw
    - .T / .TO / 4-digit number → data-jp
    - .KS / .KQ → data-kr
    - .SS / .SZ / .HK → data-cn
    - default → data-us
  - Pipeline: `uv run skills/data-{detected}/scripts/pack.py --ticker {ticker} --pack snapshot` → format Markdown card
- skills/report-stock-snapshot/scripts/snapshot_format.py — pure formatting, accepts pack JSON, outputs Markdown

VERIFICATION:
- uv run skills/report-stock-snapshot/scripts/snapshot_format.py --input /tmp/aapl-snapshot.json produces Markdown card
- SKILL.md mental trace: AAPL → data-us snapshot pack → format → Markdown
- Country routing covers 5 markets

CONSTRAINTS:
- DO NOT delete the 3 source snapshot skills yet
```

**Agent C3 — `report-portfolio-review`:**

```
Extract orchestration from invest-portfolio into skills/report-portfolio-review/.

INPUTS:
- Read: investing-toolkit/skills/invest-portfolio/SKILL.md
- Spec §4.4 report-portfolio-review

DELIVERABLES:
- skills/report-portfolio-review/SKILL.md
  - Inputs: holdings CSV + optional regime-overlay flag
  - Pipeline:
    1. Parse holdings, group tickers by country suffix
    2. Parallel: `uv run skills/data-{country}/scripts/pack.py --tickers {country-group} --pack screener-batch` per country
    3. Concatenate batch JSONs
    4. `uv run skills/analysis-portfolio/scripts/portfolio_compute.py --holdings {holdings} --prices {combined.json}`
    5. Optional: `uv run skills/analysis-macro-regime/scripts/regime_compose.py` + overlay
    6. Format Markdown
- skills/report-portfolio-review/scripts/review_format.py — pure formatting

VERIFICATION:
- Test fixture: 3-position holdings (AAPL, 2330.TW, 7203.T)
- End-to-end mental trace: parse → group {us:[AAPL], tw:[2330.TW], jp:[7203]} → 3 parallel data-* calls → concat → analysis-portfolio → format

CONSTRAINTS:
- DO NOT delete invest-portfolio/ yet
```

**Agent C4 — `report-screener-list`:**

```
Split orchestration from stock-screener into new skills/report-screener-list/.

INPUTS:
- Read: investing-toolkit/skills/stock-screener/SKILL.md
- Spec §4.4 report-screener-list

DELIVERABLES:
- skills/report-screener-list/SKILL.md
  - Inputs: ticker list + preset (value/growth/quality/momentum/etc.)
  - Pipeline:
    1. Parse + group by country suffix
    2. Parallel: `uv run skills/data-{country}/scripts/pack.py --tickers {country-group} --pack screener-batch` per country
    3. Concat batch JSONs → /tmp/screener-batch.json
    4. `uv run skills/analysis-screener/scripts/screener_compute.py --input /tmp/screener-batch.json --preset {preset}`
    5. Format top-N table Markdown
- skills/report-screener-list/scripts/screener_format.py — pure formatting

VERIFICATION:
- Test mixed-country input: AAPL,MSFT,GOOGL,2330.TW,2454.TW,7203.T
- Mental trace: parse → group → 3 parallel data-* batch calls → concat → analysis-screener → top-N table
- preset list matches stock-screener current presets (value, deep-value, quality, high-dividend, growth, growth-value, momentum, balanced)

CONSTRAINTS:
- DO NOT delete stock-screener/ yet
```

- [ ] **Step 3: Wait for all 4 agents to complete**

Verify each agent's verification commands ran successfully.

- [ ] **Step 4: Run report-stock-snapshot end-to-end**

```bash
INVESTING_TOOLKIT_CACHE=/tmp/cache uv run skills/data-us/scripts/pack.py --ticker AAPL --pack snapshot > /tmp/aapl-snap.json
uv run skills/report-stock-snapshot/scripts/snapshot_format.py --input /tmp/aapl-snap.json | head -30
```

Expected: Markdown stock card.

- [ ] **Step 5: Run report-screener-list end-to-end (US-only first)**

```bash
INVESTING_TOOLKIT_CACHE=/tmp/cache uv run skills/data-us/scripts/pack.py --tickers AAPL,MSFT,GOOGL,META,AMZN --pack screener-batch > /tmp/us-batch.json
uv run skills/analysis-screener/scripts/screener_compute.py --input /tmp/us-batch.json --preset value > /tmp/us-ranked.json
uv run skills/report-screener-list/scripts/screener_format.py --input /tmp/us-ranked.json | head -20
```

Expected: ranked top-N Markdown table.

- [ ] **Step 6: Commit Phase 2**

```bash
git add investing-toolkit/skills/report-*
git commit -m "$(cat <<'EOF'
feat(investing-toolkit): three-layer refactor Phase 2 — report-* orchestrators

Add 4 report-* skills:
- report-equity-memo (rename + new orchestration calling data-* + analysis-*)
- report-stock-snapshot (3-into-1 country auto-routing)
- report-portfolio-review (split from invest-portfolio)
- report-screener-list (NEW — split from stock-screener; cross-country grouping)

Old skills retained for Phase 3 router migration.

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>
EOF
)"
```

---

### Task 4: Update using-investing-toolkit router

**Files:**
- Modify: `investing-toolkit/skills/using-investing-toolkit/SKILL.md`

- [ ] **Step 1: Read current router**

```bash
cat investing-toolkit/skills/using-investing-toolkit/SKILL.md
```

- [ ] **Step 2: Update router routing table**

Edit `investing-toolkit/skills/using-investing-toolkit/SKILL.md` — replace the routing table to point to new skill names. Mapping:

| User intent | Old route | New route |
|---|---|---|
| "fetch US/JP/TW/KR/CN data" | `*-macro` / `*-stock-snapshot` | `data-{country}` |
| "DCF valuation" | `dcf-valuation` | `analysis-dcf` |
| "screen stocks" | `stock-screener` | `report-screener-list` (user-facing entry) |
| "technical indicators" | `technical-snapshot` | `analysis-technical` (or `report-stock-snapshot` for casual use) |
| "portfolio review" | `invest-portfolio` | `report-portfolio-review` |
| "macro regime" | `macro-regime-snapshot` | `analysis-macro-regime` |
| "investment memo" | `investment-memo-writer` | `report-equity-memo` |
| "stock snapshot" | `*-stock-snapshot` | `report-stock-snapshot` |

- [ ] **Step 3: Verify all 16 skills accounted for**

```bash
ls investing-toolkit/skills/ | sort
```

Expected after Phase 1+2: contains old skills + new skills (15 + 10 ≈ 25 entries). Phase 3 deletes old.

- [ ] **Step 4: Commit router**

```bash
git add investing-toolkit/skills/using-investing-toolkit/SKILL.md
git commit -m "feat(investing-toolkit): update using-investing-toolkit router for v2.0.0 skill names

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>"
```

---

### Task 5: Phase 3 — Delete old skills

**Files:**
- Delete: 9 old skill directories

- [ ] **Step 1: Verify no references to old skills remain**

```bash
cd investing-toolkit
for old in dcf-valuation stock-screener technical-snapshot invest-portfolio macro-regime-snapshot investment-memo-writer us-macro japan-macro taiwan-macro korea-macro china-macro us-stock-snapshot japan-stock-snapshot taiwan-stock-snapshot; do
  count=$(grep -r --include="SKILL.md" "$old" skills/data-* skills/analysis-* skills/report-* skills/using-investing-toolkit 2>/dev/null | wc -l | tr -d ' ')
  if [ "$count" != "0" ]; then
    echo "WARNING: $old still referenced ($count occurrences)"
  fi
done
```

Expected: no warnings. If any, fix references before deletion.

- [ ] **Step 2: Delete old skill directories**

```bash
rm -rf investing-toolkit/skills/dcf-valuation
rm -rf investing-toolkit/skills/stock-screener
rm -rf investing-toolkit/skills/technical-snapshot
rm -rf investing-toolkit/skills/invest-portfolio
rm -rf investing-toolkit/skills/macro-regime-snapshot
rm -rf investing-toolkit/skills/investment-memo-writer
rm -rf investing-toolkit/skills/us-macro
rm -rf investing-toolkit/skills/japan-macro
rm -rf investing-toolkit/skills/taiwan-macro
rm -rf investing-toolkit/skills/korea-macro
rm -rf investing-toolkit/skills/china-macro
rm -rf investing-toolkit/skills/us-stock-snapshot
rm -rf investing-toolkit/skills/japan-stock-snapshot
rm -rf investing-toolkit/skills/taiwan-stock-snapshot
```

- [ ] **Step 3: Verify final skill count = 15** (PR 1, no analysis-comps yet)

```bash
ls investing-toolkit/skills/ | wc -l
ls investing-toolkit/skills/
```

Expected count: 15. List: 5 data-* + 5 analysis-* (no comps yet) + 4 report-* + 1 router = 15.

- [ ] **Step 4: Commit deletions**

```bash
git add -A investing-toolkit/skills/
git commit -m "$(cat <<'EOF'
refactor(investing-toolkit): remove deprecated v1.x skills

15 old skills replaced by:
- 5 data-{country} (was 5 macro + 3 stock-snapshot, merged)
- 5 analysis-* (renamed from compute-flavored skills)
- 4 report-* (split orchestration)
- 1 router (updated)

analysis-comps to follow in PR 2.

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>
EOF
)"
```

---

### Task 6: Update plugin.json + MCP registrations

**Files:**
- Modify: `investing-toolkit/plugin.json`
- Audit: any `mcp.json` in skill directories

- [ ] **Step 1: Bump version in plugin.json**

```bash
cat investing-toolkit/plugin.json | jq .
```

- [ ] **Step 2: Edit version**

Update `version` to `2.0.0-rc.1`. If `description` mentions specific old skill names, update them.

- [ ] **Step 3: Find + update MCP registrations**

```bash
find investing-toolkit -name "*.mcp.json" -o -name "mcp.json"
```

For each found file, update tool registrations to reference new script paths (e.g., `skills/data-us/scripts/yfinance_client.py` instead of `skills/us-stock-snapshot/scripts/yfinance_client.py`).

- [ ] **Step 4: Validate JSON**

```bash
cat investing-toolkit/plugin.json | jq .
find investing-toolkit -name "*.mcp.json" -exec jq . {} \;
```

Expected: all parse cleanly.

- [ ] **Step 5: Commit metadata**

```bash
git add investing-toolkit/plugin.json
git add investing-toolkit/**/*.mcp.json 2>/dev/null
git commit -m "chore(investing-toolkit): bump v2.0.0-rc.1 + update MCP tool paths"
```

---

### Task 7: Run regression smoke tests

**Files:**
- Test: existing memo dogfood tickers

- [ ] **Step 1: Smoke test report-equity-memo for AAPL**

Note: `report-equity-memo` will fail at the analysis-comps step since it's not in PR 1. That's expected. Verify all OTHER steps work.

```bash
# Manual Bash sequence simulating what main agent would do:
INVESTING_TOOLKIT_CACHE=/tmp/cache uv run skills/data-us/scripts/pack.py --ticker AAPL --pack memo-fetch > /tmp/aapl-fetch.json
INVESTING_TOOLKIT_CACHE=/tmp/cache uv run skills/data-us/scripts/pack.py --pack regime-pack > /tmp/us-regime.json
uv run skills/analysis-macro-regime/scripts/regime_compose.py --input us=/tmp/us-regime.json > /tmp/regime.json
uv run skills/analysis-dcf/scripts/dcf_compute.py --input /tmp/aapl-fetch.json > /tmp/aapl-dcf.json
echo "All Phase 1-3 steps OK. analysis-comps step (Phase 4) deferred to PR 2."
```

Expected: each command produces valid JSON.

- [ ] **Step 2: Smoke test report-screener-list mixed-country**

```bash
INVESTING_TOOLKIT_CACHE=/tmp/cache uv run skills/data-us/scripts/pack.py --tickers AAPL,MSFT,GOOGL --pack screener-batch > /tmp/us-batch.json
INVESTING_TOOLKIT_CACHE=/tmp/cache uv run skills/data-tw/scripts/pack.py --tickers 2330.TW,2454.TW --pack screener-batch > /tmp/tw-batch.json
jq -s 'add' /tmp/us-batch.json /tmp/tw-batch.json > /tmp/combined.json
uv run skills/analysis-screener/scripts/screener_compute.py --input /tmp/combined.json --preset value > /tmp/ranked.json
uv run skills/report-screener-list/scripts/screener_format.py --input /tmp/ranked.json
```

Expected: ranked top-N Markdown table with mixed US + TW tickers.

- [ ] **Step 3: Run CI MD5 sync check locally**

```bash
cd investing-toolkit
bash scripts/sync-clients.sh --check
```

Expected: all duplicated clients identical (yfinance × 5, fred × 2, ta_client × N).

- [ ] **Step 4: Commit any fixup if smoke tests revealed issues**

If Steps 1-3 surfaced bugs, fix them in the relevant skill and commit:

```bash
git add -A
git commit -m "fix(investing-toolkit): smoke test fixes for v2.0.0-rc.1"
```

---

### Task 8: Open PR 1

- [ ] **Step 1: Push branch**

```bash
git push -u origin feat/v2.0.0-three-layer
```

- [ ] **Step 2: Open PR using `commit-commands:commit-push-pr` or `gh pr create`**

```bash
gh pr create --title "feat(investing-toolkit): v2.0.0-rc.1 three-layer refactor" --body "$(cat <<'EOF'
## Summary

- Reorganizes 15 skills into clean three-layer architecture (Data / Analysis / Report)
- 5 `data-{country}` (US/JP/TW/KR/CN) bundle multi-source fetch with `--ticker`/`--tickers` modes
- 5 `analysis-*` are pure compute (no exceptions; batch fetch complexity stays in data layer)
- 4 `report-*` are orchestrators (incl. NEW `report-screener-list` for cross-country screening)
- ADR-0001 + CI MD5 sync check enforce structural integrity
- Skill count: 15 → 15 (analysis-comps deferred to PR 2 → 16)

**Spec:** `docs/superpowers/specs/2026-05-01-investing-toolkit-v2.0.0-three-layer-design.md`

## Breaking changes

Slash commands renamed (see migration table in ADR-0001 §slash-command-rename-map). No alias shim.

## Test plan

- [x] All 5 `data-{country}/pack.py` smoke tests pass (AAPL/7203/2330.TW/005930.KS/600519.SS)
- [x] Cross-country batch fetch works (5 US tickers, 2 TW tickers concatenated)
- [x] `report-screener-list` mixed-country end-to-end pass
- [x] `report-equity-memo` Phase 1-3 pass (Phase 4 = analysis-comps deferred to PR 2)
- [x] CI MD5 sync check passes for yfinance×5, fred×2, ta_client×N
- [x] No references to deleted skills remain in router or MCP registrations

🤖 Generated with [Claude Code](https://claude.com/claude-code)
EOF
)"
```

- [ ] **Step 3: Capture PR URL**

Note the PR number for PR 2's dependency tracking.

---

## PR 2 — analysis-comps + Peer-Discovery (v2.0.0-rc.2)

**Pre-condition:** PR 1 merged to main.

### Task 9: Create branch + dispatch analysis-comps + comps-multiples agents in parallel

**Files:**
- Branch: `feat/v2.0.0-comps`

- [ ] **Step 1: Branch from main (post-PR 1 merge)**

```bash
git checkout main
git pull origin main
git checkout -b feat/v2.0.0-comps
```

- [ ] **Step 2: Dispatch 6 agents in parallel (single message)**

**Agent E1 — `analysis-comps`:**

```
Build new skill skills/analysis-comps/.

INPUTS:
- Spec §5 analysis-comps Specification
- Read: investing-toolkit/skills/analysis-dcf/SKILL.md (analysis layer pattern reference)

DELIVERABLES:
- skills/analysis-comps/SKILL.md
  - Description: "Compute peer multiples comparison from pre-fetched data"
  - Inputs: --anchor <data-pack-json-path> --peers <comma-sep-paths> [--mode direct|compute]
  - Output schema per Spec §5.4
  - Multiples set: trailing P/E, forward P/E, EV/EBITDA, P/S, P/B (Spec §5.3)
  - Statistics: median/mean/q1/q3/min/max
  - Anchor delta: vs_median_pct + percentile
  - Provenance preserved in _provenance field
- skills/analysis-comps/scripts/comps_compute.py
  - Pure compute (no I/O)
  - Reads anchor + peer JSONs (assumed pre-fetched via data-{country}/pack.py --pack comps-multiples)
  - Computes statistics + ranking
  - Outputs schema-conformant JSON

VERIFICATION:
- Create test fixture: data-us/pack.py for AAPL + 4 peers (MSFT,GOOGL,META,AMZN) --pack comps-multiples
- uv run skills/analysis-comps/scripts/comps_compute.py --anchor /tmp/aapl-comps.json --peers /tmp/msft.json,/tmp/googl.json,/tmp/meta.json,/tmp/amzn.json returns valid JSON
- Output JSON validates against schema in Spec §5.4
- comps_compute.py contains zero HTTP calls

CONSTRAINTS:
- analysis-comps does NOT do peer-discovery (that's report layer's job)
- analysis-comps does NOT fetch data
```

**Agents F1–F5 — `--pack comps-multiples` mode for each data-{country} (5 parallel):**

For each country (us, jp, tw, kr, cn), an agent updates `skills/data-{country}/scripts/pack.py`:

```
Add --pack comps-multiples mode to skills/data-{country}/scripts/pack.py.

INPUTS:
- Read: skills/data-{country}/scripts/pack.py (current pack.py)
- Spec §5.4 anchor schema (multiples fields needed)
- Spec §4.2 pack-types (comps-multiples is single OR batch via --tickers)

DELIVERABLES:
- skills/data-{country}/scripts/pack.py extended:
  - When --pack comps-multiples is requested:
    - Pull yfinance info for ticker(s)
    - Extract multiples-only fields: trailingPE, forwardPE, priceToSales, priceToBook, enterpriseToEbitda, enterpriseToRevenue, marketCap, enterpriseValue
    - For US: optionally augment via SEC EDGAR XBRL facts if higher precision needed (config flag)
    - Output JSON: {ticker, multiples: {...}, _provenance: {...}}
  - Supports --ticker (1) or --tickers (N)

VERIFICATION:
- uv run skills/data-{country}/scripts/pack.py --ticker {test-ticker} --pack comps-multiples returns multiples JSON with all 5 multiples fields
- uv run skills/data-{country}/scripts/pack.py --tickers {ticker-list} --pack comps-multiples returns N-ticker batch JSON

CONSTRAINTS:
- DO NOT modify other --pack modes
- yfinance fields may be None for some tickers — preserve as null in JSON, don't error
- DO NOT add extra fields beyond multiples (this is a lightweight pack)

Test tickers:
- US: AAPL
- JP: 7203
- TW: 2330.TW
- KR: 005930.KS
- CN: 600519.SS
```

Replace `{country}` and `{test-ticker}` per agent.

- [ ] **Step 3: Wait for all 6 agents to complete**

Verify deliverables.

- [ ] **Step 4: Run end-to-end Comps test for AAPL vs FAANG**

```bash
cd investing-toolkit
INVESTING_TOOLKIT_CACHE=/tmp/cache uv run skills/data-us/scripts/pack.py --ticker AAPL --pack comps-multiples > /tmp/aapl-c.json
INVESTING_TOOLKIT_CACHE=/tmp/cache uv run skills/data-us/scripts/pack.py --tickers MSFT,GOOGL,META,AMZN --pack comps-multiples > /tmp/peers-c.json
# split peers into separate files (or update analysis-comps to accept batched JSON)
uv run skills/analysis-comps/scripts/comps_compute.py --anchor /tmp/aapl-c.json --peers /tmp/peers-c.json | jq '.statistics'
```

Expected: statistics block with trailingPE/forwardPE/evEbitda/priceToSales/priceToBook median/mean/q1/q3.

- [ ] **Step 5: Commit analysis-comps + comps-multiples**

```bash
git add investing-toolkit/skills/analysis-comps/ investing-toolkit/skills/data-*/scripts/pack.py
git commit -m "$(cat <<'EOF'
feat(investing-toolkit): add analysis-comps + --pack comps-multiples

Pure-compute Comps skill following Spec §5.4 schema. Multiples set:
trailing P/E, forward P/E, EV/EBITDA, P/S, P/B with median/mean/quartile
statistics + anchor percentile delta.

All 5 data-{country}/pack.py extended with --pack comps-multiples mode
(single + batch via --tickers).

Peer-discovery handled UPSTREAM by report layer (Task 10).

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>
EOF
)"
```

---

### Task 10: Wire peer-discovery + Comps section into report-equity-memo

**Files:**
- Modify: `investing-toolkit/skills/report-equity-memo/SKILL.md`

- [ ] **Step 1: Read current report-equity-memo SKILL.md**

```bash
cat investing-toolkit/skills/report-equity-memo/SKILL.md
```

Locate the "[PR 2: insert analysis-comps step here]" placeholder.

- [ ] **Step 2: Replace placeholder with peer-discovery + Comps phase**

Insert (between data-fetch Phase 1 and analysis Phase 3):

```markdown
### Phase 2.5 — Peer Discovery + Comps Multiples

**If `--peers` provided** (manual override): skip discovery, use the list.

**Else** spawn research agent for peer-discovery:

Use `general-purpose` subagent with prompt:

> Find 5–8 publicly-traded competitor tickers for {anchor_ticker} ({company_name}).
>
> Selection criteria (in order):
> 1. Direct business-line competitor (same products/services)
> 2. Comparable scale tier (market cap within 0.3x–3x range)
> 3. Same primary geography or comparable geographic mix
> 4. Listed on major exchanges (US/JP/TW/KR/CN/HK/Europe)
>
> For each peer, provide:
> - Ticker symbol (with exchange suffix if non-US)
> - 1-line rationale explaining why it's a comp
> - Source URL (corporate disclosure, industry report, or competitor analysis)
>
> Output as JSON: {"peers": [{"ticker": "MSFT", "rationale": "...", "source": "https://..."}]}
>
> Cap: 250 words total. No industry-rollup commentary.

**Default behavior**:
- Pipeline mode (called by orchestrator): auto-proceed; peer list visible in process logs and final report
- CLI mode (`--interactive`): present peer list + rationale → user `/proceed` confirms

**Provenance transparency**:
- During execution: log "Using peers: X (reason), Y (reason), Z (reason)" before fetch
- In final memo: Comps section header lists peers + 1-line rationale per peer

**Then fetch + analyze**:

```bash
# 1. Fetch anchor multiples
INVESTING_TOOLKIT_CACHE=/tmp/cache uv run skills/data-{country}/scripts/pack.py --ticker {anchor} --pack comps-multiples > /tmp/anchor-c.json

# 2. Fetch peer multiples (batch per country if peers cross-market)
INVESTING_TOOLKIT_CACHE=/tmp/cache uv run skills/data-{country}/scripts/pack.py --tickers {peers} --pack comps-multiples > /tmp/peers-c.json

# 3. Compute Comps statistics + ranking
uv run skills/analysis-comps/scripts/comps_compute.py --anchor /tmp/anchor-c.json --peers /tmp/peers-c.json > /tmp/comps.json
```

Pass `/tmp/comps.json` to investing-team in Phase 4 alongside `/tmp/dcf.json`.
```

- [ ] **Step 3: Verify mental trace**

Walk through end-to-end for AAPL with no `--peers`:
1. Phase 1: data-us memo-fetch
2. Phase 2: data-us regime-pack + analysis-macro-regime
3. **Phase 2.5: peer-discovery agent finds [MSFT, GOOGL, META, AMZN, NVDA] + rationales → fetch comps-multiples → analysis-comps**
4. Phase 3: analysis-dcf
5. Phase 4: delegate domain-teams:investing-team with `[fetch.json, dcf.json, comps.json, regime.json]`
6. Phase 5: optional docs-team

- [ ] **Step 4: Commit Comps integration**

```bash
git add investing-toolkit/skills/report-equity-memo/SKILL.md
git commit -m "feat(report-equity-memo): wire analysis-comps + research-agent peer-discovery

Phase 2.5 inserted between data fetch and DCF. Peer-discovery via
runtime general-purpose agent (or manual --peers override). Provenance
transparency: peer list visible during execution and in final memo header.

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>"
```

---

### Task 11: End-to-end PR 2 dogfood + open PR

- [ ] **Step 1: Full memo run for AAPL**

Trigger `report-equity-memo` for AAPL via main agent (this validates peer-discovery agent integration).

Save final memo Markdown to `/tmp/aapl-memo.md`. Verify:
- Comps section present
- Peer list with rationale + source URLs visible
- DCF section present
- Macro regime section present
- Investment-team gates verdict present

- [ ] **Step 2: Full memo run for 2330.TW**

Same for TSMC. Verify peer-discovery returns sensible Asian tech peers (Intel, Samsung, etc.) and cross-country fetch works.

- [ ] **Step 3: Bump version**

Edit `investing-toolkit/plugin.json`: `version` → `2.0.0-rc.2`.

```bash
git add investing-toolkit/plugin.json
git commit -m "chore(investing-toolkit): bump v2.0.0-rc.2"
```

- [ ] **Step 4: Push + open PR 2**

```bash
git push -u origin feat/v2.0.0-comps
gh pr create --title "feat(investing-toolkit): v2.0.0-rc.2 analysis-comps + peer-discovery" --body "$(cat <<'EOF'
## Summary

- Add `analysis-comps` skill (pure compute, multiples comparable analysis)
- Add `--pack comps-multiples` to all 5 `data-{country}/pack.py`
- Wire peer-discovery research agent + Comps section into `report-equity-memo`
- Skill count: 15 → 16

**Spec:** §5 + §6 of design doc

**Depends on:** PR 1 (#XXX) merged

## Test plan

- [x] AAPL vs FAANG dogfood: full memo produces Comps + DCF + regime + investing-team verdict
- [x] TSMC (2330.TW) dogfood: cross-country peers (Intel/Samsung) discovered + analyzed
- [x] `--peers` manual override path works
- [x] Provenance: peer list + rationale + source URLs visible in final memo

🤖 Generated with [Claude Code](https://claude.com/claude-code)
EOF
)"
```

---

## PR 3 — Documentation Polish (v2.0.0)

**Pre-condition:** PR 1 + PR 2 merged.

### Task 12: Documentation parallel batch (3 agents)

**Files:**
- Modify: `investing-toolkit/README.md` + i18n
- Modify: `investing-toolkit/docs/design-principles.md`
- Create: CHANGELOG entry

- [ ] **Step 1: Branch from main**

```bash
git checkout main && git pull
git checkout -b feat/v2.0.0-docs
```

- [ ] **Step 2: Dispatch 3 docs agents in parallel (single message)**

**Agent G1 — README + i18n update:**

```
Update investing-toolkit/README.md, README.zh-TW.md, README.ja.md to reflect v2.0.0 three-layer architecture.

INPUTS:
- Read: docs/superpowers/specs/2026-05-01-investing-toolkit-v2.0.0-three-layer-design.md
- Read: investing-toolkit/README.md (current, v1.x flavor)
- Reference: docs/i18n/glossary-{en,zh-TW,ja}.md per repo i18n convention

DELIVERABLES:
- investing-toolkit/README.md updated:
  - Architecture section: three-layer diagram
  - Skill list: 16 skills grouped by layer
  - Migration guide: old → new skill names mapping
  - Quick start examples updated to new skill names
- README.zh-TW.md and README.ja.md mirror updates
- Glossary terms preserved per i18n rules (no katakana for tech terms in ja, no Mainland calques in zh-TW)

VERIFICATION:
- All 3 README files mention "16 skills" + "three-layer"
- No broken links to deleted skills
- glossary-* rules respected
```

**Agent G2 — design-principles + ADR cross-reference:**

```
Update investing-toolkit/docs/design-principles.md to reference ADR-0001 three-layer architecture.

INPUTS:
- Read: investing-toolkit/docs/design-principles.md (current)
- Read: investing-toolkit/docs/adr/0001-data-analysis-report-layers.md (PR 1)

DELIVERABLES:
- design-principles.md adds "Three-Layer Architecture" section pointing to ADR-0001
- Existing principles (empirical-first, primary-source, etc.) preserved
- Cross-link to ADR

VERIFICATION:
- design-principles.md includes section "Three-Layer Architecture"
- Links to ADR-0001 work
```

**Agent G3 — CHANGELOG + migration guide:**

```
Write CHANGELOG entry + migration guide for v2.0.0.

INPUTS:
- Spec doc
- ADR-0001 slash-command rename map

DELIVERABLES:
- investing-toolkit/CHANGELOG.md prepended with v2.0.0 entry:
  - Breaking changes (slash command renames)
  - New: analysis-comps, report-screener-list
  - Refactor: 15 → 16 skills, three-layer
  - Migration table (old skill → new skill, old slash command → new)
  - Reference: PR 1, PR 2, PR 3
- investing-toolkit/docs/migration-v2.0.0.md (new file) — detailed migration guide for users

VERIFICATION:
- CHANGELOG has v2.0.0 section >50 lines
- migration-v2.0.0.md has full skill rename table
- All 16 skills documented in migration
```

- [ ] **Step 3: Wait for 3 agents to complete + commit**

```bash
git add investing-toolkit/README.md investing-toolkit/README.zh-TW.md investing-toolkit/README.ja.md
git add investing-toolkit/docs/design-principles.md investing-toolkit/CHANGELOG.md investing-toolkit/docs/migration-v2.0.0.md
git commit -m "docs(investing-toolkit): v2.0.0 README + i18n + design-principles + migration guide

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>"
```

---

### Task 13: Promote CI sync check to required + final version bump

**Files:**
- Modify: `.github/workflows/check-script-sync.yml`
- Modify: `investing-toolkit/plugin.json`

- [ ] **Step 1: Mark CI check as required in branch protection**

If repo allows via gh CLI:

```bash
gh api repos/kouko/monkey-skills/branches/main/protection/required_status_checks --method PATCH --field 'contexts[]=check-script-sync'
```

If not, document in `docs/ci-required-checks.md` and ask user to update branch protection manually.

- [ ] **Step 2: Bump to v2.0.0 final**

Edit `investing-toolkit/plugin.json`: `version` → `2.0.0`.

```bash
git add investing-toolkit/plugin.json
git commit -m "chore(investing-toolkit): bump v2.0.0 final"
```

---

### Task 14: Final smoke + open PR 3

- [ ] **Step 1: Re-run all dogfood scenarios**

```bash
# AAPL memo
# TSMC (2330.TW) memo
# Mixed-country screener
# US-only screener with preset value
# Portfolio review with 3-position mixed holdings
```

Each must succeed end-to-end.

- [ ] **Step 2: Push + open PR 3**

```bash
git push -u origin feat/v2.0.0-docs
gh pr create --title "docs(investing-toolkit): v2.0.0 README + i18n + migration guide" --body "$(cat <<'EOF'
## Summary

- Updates README (en/zh-TW/ja) for v2.0.0 three-layer architecture
- Updates design-principles.md with ADR-0001 cross-reference
- Adds CHANGELOG v2.0.0 + migration-v2.0.0.md guide
- Promotes CI script-sync check to required
- Final v2.0.0 version bump

**Depends on:** PR 1 (#XXX) + PR 2 (#YYY)

## Test plan

- [x] All dogfood scenarios green
- [x] CI required-check passes
- [x] i18n glossary rules respected
- [x] Migration guide covers all 15 → 16 renames

🤖 Generated with [Claude Code](https://claude.com/claude-code)
EOF
)"
```

---

## Rollback Procedures

### Per-PR Rollback

**PR 1 rollback** (if merged but post-merge issue surfaces):
```bash
git revert -m 1 <PR-1-merge-commit>
```
Old skills are restored from git history. CI MD5 sync check returns to status quo.

**PR 2 rollback:**
```bash
git revert -m 1 <PR-2-merge-commit>
```
analysis-comps removed; report-equity-memo Phase 2.5 placeholder restored. data-{country}/pack.py loses --pack comps-multiples mode.

**PR 3 rollback:**
```bash
git revert -m 1 <PR-3-merge-commit>
```
Docs revert; CI required-check status reverts.

### Mid-PR Rollback (during implementation)

**During Phase 1 (parallel agent dispatch fails):**
- Specific failed agent: re-dispatch only that agent (others' deliverables untouched)
- Multiple agent failures: `git reset --hard HEAD` and restart Phase 1

**During Phase 2 (report agents fail):**
- Same per-agent retry.

**During Phase 3 (deletion fails):**
- `git reset --hard HEAD~1` to undo deletions; investigate stale references; retry.

### Critical Failure (post-merge to main)

If main is broken post v2.0.0 release:
1. `git revert -m 1` on the offending merge commit
2. Push hot-fix tag `v1.16.5` if needed (hot-fix branch from pre-v2 commit)
3. Notify users via repo issue + memory file update

---

## Self-Review

**Spec coverage check:**

| Spec section | Plan task |
|---|---|
| §1 Goal | Plan header (architecture + tech stack) |
| §2.1 Anthropic comparison | Captured in spec; plan implements §1 goal |
| §2.2 duplication audit | Task D1 (CI sync), Task 7 step 3 |
| §2.3 mixed concerns | Tasks 2 + 3 (split skills) |
| §3.1 Layer definitions | Task D1 ADR + per-skill SKILL.md |
| §3.2 Cross-skill data passing | Task 3 (report skill SKILL.md), Task 10 |
| §3.3 Anthropic rule compliance | Task 2 + 3 (each script in skill folder) |
| §4.1 Skill mapping table | Tasks 2 + 3 + 9 cover all 16 |
| §4.2 Layer 1 data | Task 2 Batch A, plus Task 9 F1-F5 for comps-multiples |
| §4.3 Layer 2 analysis | Task 2 Batch B, plus Task 9 Agent E1 (comps) |
| §4.4 Layer 3 report | Task 3 Batch C |
| §4.5 Future expansion | Documented as N/A for v2.0.0 |
| §5 analysis-comps spec | Task 9 Agent E1 |
| §5.5 peer-discovery | Task 10 |
| §5.6 provenance transparency | Task 10 (logged + in memo header) |
| §6.1 PR strategy | Tasks 8, 11, 14 (3 PR open commands) |
| §6.2 Parallel batches | Task 2 (11 agents), Task 3 (4 agents), Task 9 (6 agents), Task 12 (3 agents) |
| §6.3 Backward compatibility | Task 4 router + Task 12 migration guide |
| §7 Open questions | Out-of-scope for plan; deferred items captured in spec |
| §8 Acceptance criteria | Mapped to verification steps across tasks |

**Placeholder scan:**
- All `{ticker}`, `{country}`, `{peers}` placeholders are template parameters (acceptable)
- No "TBD" / "TODO" / "implement later" found
- All commands have explicit expected output

**Type consistency:**
- `pack.py` referenced consistently across all data-* tasks
- `comps_compute.py` / `dcf_compute.py` / `screener_compute.py` naming consistent
- `--pack {snapshot|memo-fetch|comps-multiples|screener-batch|regime-pack}` modes consistent across §4.2 and Task 9

**Done.**
