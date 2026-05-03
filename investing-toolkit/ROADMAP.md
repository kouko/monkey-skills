# investing-toolkit Roadmap

---

# Future Roadmap (planning — post-v2.1.0)

This section tracks deferred work, organized by horizon. **Each item is independently shippable** — pick any one and a fresh Claude Code session has enough context to start. Items reference relevant ADRs and prior PRs for context.

**Pickup convention for new sessions**: read this section + the linked ADR/PR for the chosen item; that's the whole brief. Worktree pattern (`git worktree add -b feat/...`) recommended for any multi-PR work.

## Near-term — v2.1.x patches

Small loose-ends from v2.1.0 closure. Each ~½ to 1 day. No new architecture.

### v2.1.x-a — JP regime-pack fresh fixture refresh

- **What**: Run `data-jp/scripts/pack.py --pack regime-pack` against live BOJ Time-Series API to capture Tankan business DI + ESRI coincident-index / leading-index / 機械受注 data that PR-3 (#188) wired but didn't refresh in fixture. Replace `tests/data/fixtures/data-jp-regime-pack-sample.json`.
- **Why**: `classify_jp.py` currently engages IP fallback (`source: "ip"` instead of `coincident-index`) because pre-PR-3 fixture lacks Tankan + ESRI fields. Fresh fixture lets confidence rise from medium to high stable.
- **Files**: `investing-toolkit/tests/data/fixtures/data-jp-regime-pack-sample.json` (regenerate); `investing-toolkit/tests/integration/test_cross_layer_chains.py::test_chain_jp_classifier_e2e` (tighten `confidence in ("medium", "high")` → `confidence == "high"`).
- **Blocker**: BOJ Time-Series API reachability (occasionally rate-limited; should retry).
- **Acceptance**: JP test asserts `confidence == "high"`, `cycle_proxy.source == "coincident-index"` (not `"ip"`), `tankan_business_di.large_mfg` populated.
- **Reference**: PR-3 #188; ADR-0004 §"JP Tankan series code resolution".

### ~~v2.1.x-b — TW TIER as standalone NDC preset~~ → **demoted to v2.2.0-g**

- **Status**: Premise empirically false (verified 2026-05-02). Demoted to v2.2.0-g; see below.
- **What was found**: NDC's bulk-download ZIP (`ws.ndc.gov.tw/Download.ashx?...景氣指標及燈號.zip`) publishes `景氣對策信號構成項目.csv` with **8 components, not 9**. The TIER 9th component (`製造業營業氣候測驗點`) is published by 台灣經濟研究院 — a different institution — as a monthly press-release **PDF only**. It is not in `data.gov.tw`, not in NDC's ZIP, and `index.ndc.gov.tw/n/zh_tw/lightscore` is Cloudflare-protected with no public API contract. The original premise that TIER "lives in `signal-components` and just needs a standalone preset" is wrong.
- **What v2.1.x-b actually delivered**: Documentation correction — `grounding-tw-2026-05.md` updated to reflect the structural NDC bundle gap (8/9 schema lag); ROADMAP demotion to v2.2.0-g; integration test `test_chain_tw_classifier_e2e` tightened to lock `confidence == "high"` (which `v2.1.x-c` already achieved by fixing CPI YoY).
- **Why confidence is already high without TIER**: classify_tw confidence threshold is `≥ 6 components found + leading + coincident + cpi-yoy present`. v2.1.x-c (CPI YoY 修正) unblocked the cpi-yoy condition; 8/9 ≥ 6 satisfies the dispersion check. Adding TIER would close the dispersion gap (8/9 → 9/9) but would not change the confidence verdict.
- **Reference**: PR-4 #187 grounding-tw-2026-05.md; v2.1.x-b research session 2026-05-02.

### v2.1.x-c — DGBAS CPI YoY label correction

- **What**: PR-4 #187 review observed `data-tw/dgbas_client.py` `cpi` preset is labelled "CPI YoY%" but actually emits CPI INDEX values (110.16-110.93, base 2021=100). Add a separate `cpi-yoy` preset that returns true YoY (or fix existing preset's label/values).
- **Why**: classify_tw `cpi_context.latest_yoy` resolves to None on existing fixture because the values aren't true YoY. Downstream `bok_target_alignment`-like analyses also miss-read.
- **Files**: `investing-toolkit/skills/data-tw/scripts/dgbas_client.py`; pack.py; tests.
- **Blocker**: None (DGBAS publishes both forms).
- **Acceptance**: TW fixture surfaces true CPI YoY; classify_tw `cpi_context.latest_yoy` non-null.
- **Reference**: PR-4 #187 grounding-tw-2026-05.md fixture-deficiency note.

### v2.1.x-d — CI script-sync check promote to required

- **What**: Flip GitHub Actions workflow flag for `check-script-sync` from advisory to required. Currently MD5-mismatch warnings can land without blocking merge.
- **Why**: v2.0.0 added the sync mechanism but kept it advisory; drift risk grows with each PR.
- **Files**: `.github/workflows/skill-structure.yml` or repo branch protection rules.
- **Blocker**: Confirm last 30 days had zero false-positives (review CI run history).
- **Acceptance**: A test commit with deliberately desynced script copies fails CI.

### ~~v2.1.x-e — DGBAS `cpi-sa` (季調CPI) computed YoY companion~~ ✅ closed 2026-05-03

- **Status**: Closed. New `cpi-sa-yoy` preset added; `_compute_yoy_from_index` helper introduced (period=12, defensive YYYYMM-arithmetic + skip-on-gap + skip-on-zero-base).
- **Live verification**: 202603 = 1.47% (vs headline `cpi-yoy` 1.20% — SA bumps slightly higher per expected smoothing of Lunar New Year base effect). 795 observations after 12-obs trim. `_provenance.computed: true` + `_provenance.computation: "yoy_from_index (period=12; ...)"` set.
- **Pack wiring**: Skipped (regime-pack already covers headline `cpi-yoy`; SA-YoY available via direct CLI / future analysis-* consumer).
- **Reference**: ROADMAP cleanup follow-up PR (2026-05-03); v2.1.x-c root-cause + §v2.1.x-c² PR #209 cleanup port.

### ~~v2.1.x-f — DGBAS import-pi / export-pi USD-priced + 農工原料 sub-bundles~~ ✅ closed 2026-05-03

- **Status**: Closed. 8 new presets added covering all sheets PR #209 left out.
- **Sheets surfaced**:
  - `import-pi-usd` / `import-pi-usd-yoy` (`ipispl.xls` USD-priced)
  - `import-pi-raw` / `import-pi-raw-yoy` (`ipispl.xls` 農工原料 TWD)
  - `import-pi-raw-usd` / `import-pi-raw-usd-yoy` (`ipispl.xls` 農工原料 USD)
  - `export-pi-usd` / `export-pi-usd-yoy` (`epispl.xls` USD-priced)
- **Live magnitudes (202603)**: `import-pi-usd` 104.09 INDEX / 8.53% YoY; `import-pi-raw` 122.48 INDEX / 7.69% YoY; `import-pi-raw-usd-yoy` 11.51% (highest, raw-materials surge); `export-pi-usd-yoy` 12.70% (semiconductor-export driven).
- **Pack wiring**: Skipped (TWD headline in regime-pack stays canonical; USD / 農工原料 cuts available via direct CLI for trade-flow / terms-of-trade / cost-push analyses when needed).
- **Reference**: ROADMAP cleanup follow-up PR (2026-05-03); PR #209 §"Out-of-scope (kept simple)".

### ~~v2.1.x-g — Fix `test_kr_snapshot_samsung` yfinance history shape regression~~ ✅ closed 2026-05-03

- **Status**: Closed via test fix. data-kr/pack.py snapshot already returned the cross-country-symmetric T1 contract (`price_history` raw envelope as dict + `history` list-of-OHLCV records, matching data-us / data-jp); the assertion was the side that drifted.
- **What was done**: Updated `test_kr_snapshot_samsung` to assert the canonical contract — `price_history` is `dict`, `history` is `list[{date, open, high, low, close, volume}]`. Added per-field check on `history[0]` so future shape regressions surface immediately.
- **Why it predated v2.1.x**: KR pack adopted the canonical-OHLCV alias when data-us / data-jp introduced it (post-v1.x); the test was never updated to match. Failure stayed red because `@pytest.mark.network` runs are easy to skip locally; CI doesn't run network tests by default.
- **Files**: `investing-toolkit/tests/data/test_data_kr.py::test_kr_snapshot_samsung`. No client / pack changes needed.
- **Result**: Full suite now 383 passed, 2 skipped, 0 failed (was 1 failed pre-fix).
- **Reference**: PR #203 commit body §"Pre-existing failure"; v2.1.x test-suite session 2026-05-02 / 2026-05-03 fix session.

### v2.1.x-h — Scheduled weekly network-suite workflow

- **What**: Add a new GitHub Actions workflow `.github/workflows/scheduled-network-suite.yml` that runs `pytest -m network` against `investing-toolkit/tests/` on a `cron: "0 2 * * 1"` (Mondays 02:00 UTC) schedule + manual `workflow_dispatch`. Result is **report-only** (annotated job summary + optional GitHub Issue creation on first failure of a given week); does NOT gate any merge.
- **Why**: PR #216 added `pytest (offline)` as the per-PR gate but deliberately deferred the 34 `@pytest.mark.network` tests (live BOJ / NDC / DGBAS / FRED / yfinance / akshare / SEC EDGAR) because cloud IPs trigger flaky 5xx / Cloudflare bot blocks. Without a periodic run, live API shape drift sneaks in undetected (e.g. v2.1.x-g's yfinance `info.history` shape change went unnoticed for days). A weekly run + report catches drift early.
- **Files**: new `.github/workflows/scheduled-network-suite.yml` (cron + workflow_dispatch + pytest -m network + report-summary writer + optional `gh issue create` on failure); ROADMAP entry update to `v2.1.x-h ✅` after first green cycle.
- **Blocker**: Decide whether to mark certain known-flaky tests (NDC, MOPS MCP equivalence — see v2.1.x-i) as `@pytest.mark.flaky` to reduce noise, or accept the noise.
- **Acceptance**: First scheduled run lands; workflow surfaces per-test pass/fail in job summary; if ≥1 fails, GitHub Issue created with title `[network suite] N tests failed (YYYY-MM-DD)` and stderr links.
- **Reference**: PR #216 commit body §"Scope decision: offline only"; PR #220 retry session demonstrating that MCP stdio tests are CI-flaky and need periodic monitoring.

### v2.1.x-i — MCP stdio test stability hardening

- **What**: Investigate and fix the root cause of `test_mcp_equivalence_auto.py` flakiness on GitHub Actions runners (PR #220 saw `test_mops_fetch_rejects_missing_required_params` time out waiting for a JSON-RPC reply that the server log confirms it received). Likely fixes:
  1. **stdout flush hardening**: ensure FastMCP server flushes stdout after every JSON-RPC reply (`sys.stdout.flush()` or `python -u`)
  2. **Test reader retry-with-backoff**: `_call_mcp` helper currently has a fixed timeout; replace with retry loop that re-polls if reply arrives mid-buffer
  3. **Server warmup probe**: test does an explicit `tools/list` ping after spawn and waits for reply before any tool/call request, eliminating the "server not yet ready" race
  4. **Newline framing audit**: confirm every JSON-RPC envelope ends with a single `\n` and no partial writes possible (audit FastMCP version pin)
- **Why**: Each PR currently risks 1-in-N CI flakes on offline pytest job (now required). PR #220 needed a manual close+reopen cycle to retry. Cumulative drag on dev velocity. Local tests pass 6/6 because macOS stdio is unbuffered + faster CPU; CI Azure runner exposes buffer/timing races.
- **Files**: `investing-toolkit/servers/mcp_server.py` (flush hardening); `investing-toolkit/tests/test_mcp_equivalence_auto.py` `_call_mcp` helper (retry); possibly pin FastMCP version in `mcp_server.py` PEP 723 deps.
- **Blocker**: Need to reproduce the flake reliably — could try `pytest -p no:randomly --count=20` + GitHub Actions large-runner / slow-CPU emulation. If non-reproducible, fall back to (a) `pytest-rerunfailures` plugin with `reruns=2` (masks but unblocks), or (b) move MCP equivalence tests to `@pytest.mark.network` (deferred to v2.1.x-h scheduled cron, doesn't gate PRs).
- **Acceptance**: 50 consecutive CI runs pass `test_mcp_*` without close+reopen; OR explicit decision to demote to network-marked + documented in ADR.
- **Reference**: PR #220 retry session 2026-05-03; v2.1.x test-suite session.

## Mid-term — v2.2.0 candidates

Material features. ~1-3 weeks each. Do one at a time.

### v2.2.0-a — JP real-rate C+D+E framework restoration

- **What**: Restore the v1.10.0-deferred C+D+E real-rate decomposition for JP. C = ECB ex-post real-yield (already in v2.1.0 classify_jp); D = Tankan ex-ante inflation outlook (already wired in v1.x `boj_tankan_inflation_outlook`); E = JGBi (Japanese inflation-linked bonds) compared with nominal JGB.
- **Why**: 1-axis C-only is the weakest of the 5 countries. C+D+E is the framework `references/japan-real-rate-roadmap.md` describes; restoring it makes JP real-rate match US's 4-tier rigor.
- **Files**: `investing-toolkit/skills/data-jp/scripts/` new `mof_jgbi_client.py` (MoF publishes JGBi via PDF/XLSX, no API); `data-jp/pack.py` regime-pack JGBi block; `classify_jp.py` _build_real_rate_block extension.
- **Blocker**: MoF JGBi data is PDF-scraped or Excel-downloaded — fragile parser.
- **Acceptance**: classify_jp `real_rate_block` has 3 sub-blocks (ex_post / ex_ante / jgbi) all populated; cross-method central tendency derived.
- **Reference**: `analysis-macro-regime/references/japan-real-rate-roadmap.md`; v1.10.0 deferred list; v2.0.0 deferred list.

### v2.2.0-b — analysis-comps `--mode compute` activation

- **What**: v2.0.0 shipped `analysis-comps` skill with peer-discovery + multiples fetch but `--mode compute` is placeholder. Implement: percentile rank per multiple, composite score, anchor-vs-peer delta, sector tilt overlay.
- **Why**: Without compute, comps output is a table of numbers — analyst still does the math by hand. Compute mode produces verdict-grade output.
- **Files**: `investing-toolkit/skills/analysis-comps/scripts/comps_compute.py` (new compute path); SKILL.md update; integration tests.
- **Blocker**: None (data already in place).
- **Acceptance**: `comps_compute --mode compute` produces JSON with per-multiple percentile, composite score, anchor delta vs peer median.
- **Reference**: v2.0.0 deferred list.

### v2.2.0-c — Sector-adjusted multiples for Comps

- **What**: Banks → P/B + ROE; REITs → P/AFFO; Tech → EV/Revenue + Rule-of-40. Per-sector schema swap for the 5-multiple default.
- **Why**: P/E + EV/EBITDA on a bank or REIT is meaningless. Sector classifier + per-sector schema makes comps useful across sectors.
- **Files**: `analysis-comps/scripts/sector_classifier.py` (new — likely yfinance `info.sector` + manual override table); per-sector multiple schemas in `references/`; comps_compute extension.
- **Blocker**: Sector classification correctness (yfinance is sometimes wrong; need manual override).
- **Acceptance**: Apple → tech multiples (EV/Revenue + Rule-of-40); JPM → bank multiples (P/B + ROE); Realty Income → REIT multiples.
- **Reference**: v2.0.0 deferred list.

### v2.2.0-d — KR ESI explicit ECOS API integration

- **What**: Replace fdr_client KEYSTAT 'sentiment' fallback with native ECOS (한국은행 경제통계시스템) API call for 경제심리지수 K269.
- **Why**: KR Phase 1 PR-5 #186 noted ESI deferred; current code degrades gracefully but full primary-source integration is preferred.
- **Files**: `investing-toolkit/skills/data-kr/scripts/ecos_client.py` (new — needs ECOS API key); pack.py wiring; classify_kr.py read path.
- **Blocker**: **Apply for free key at ecos.bok.or.kr/api/#/AuthKeyApply** (~1 week審 review).
- **Acceptance**: classify_kr `esi_status: "fetched"` (not `"unavailable_via_fdr"`); ESI 91.7 (2026-04 latest) surfaces.
- **Reference**: PR-5 #186 grounding-kr-2026-05.md; ADR-0004 §"KR ECOS vs fdr trade-off".

### v2.2.0-e — KR DART primary-source equity integration ⭐

- **What**: Build `data-kr/scripts/dart_client.py` for KR equity primary source (analogous to US `sec_edgar_client.py`). DART (전자공시시스템) provides corporate filings, financial statements (XBRL/iXBRL/CSV), shareholder data.
- **Why**: **KR is the thinnest primary-source country** in v2.1.0 (fdr_client is secondary scrape). Building DART integration completes the 5-country symmetry on the equity side and unblocks KR memo-fetch / DCF Tier A path (parallel to US T3 in ADR-0003).
- **Files**: `data-kr/scripts/dart_client.py` (new); `data-kr/scripts/pack.py` memo-fetch + comps-multiples wired to DART; `references/schema-memo-fetch.json` KR-specific. Likely an ADR-0006 to record per-country financial statement Tier A approach for KR (parallel to ADR-0003 for US).
- **Blocker**: DART API key (already applied; check expiry); K-IFRS taxonomy mapping; iXBRL parser. ~2-3 weeks total.
- **Acceptance**: Samsung 005930.KS memo-fetch returns `_provenance.tier == "A"` with `accession` field per FY; DCF integration test green.
- **Reference**: ADR-0003 (US T3 mapping pattern); v2.0.0 deferred list.

### v2.2.0-g — TW TIER 製造業營業氣候測驗點 fetcher

- **What**: Build a TIER (製造業營業氣候測驗點) fetcher so classify_tw's 9th 構成 dispersion slot is populated. Feed `tier_manufacturing_climate.value` from a real upstream rather than calibration vintage.
- **Why**: NDC's 對策信號 2024-revision officially lists TIER as the 9th component, but NDC's bulk-download CSV stops at 8 columns (verified 2026-05-02). classify_tw degrades dispersion to 8/9 — confidence is already high (cpi-yoy + 8 components passes the threshold), but the dispersion 完備 narrative is incomplete.
- **Importance — medium-low** (re-assessed 2026-05-02): TIER is **already a constituent of NDC 領先指標** (which we fetch via the same bulk ZIP), so its forward-looking signal is ~80% covered by leading-index + CIER PMI we already pull. NDC 對策信號 score / color is unaffected (NDC computes the score internally with TIER). Adding TIER would close 8/9 → 9/9 dispersion + give a discrete monthly mom number for memo narrative, but is **not load-bearing** for regime classification. Defer until a TW-focused buy-side memo workflow concretely needs it.
- **Source-research blocker — partially resolved 2026-05-02**: 4 candidate routes evaluated; PDF route is the only viable free path:
  1. ✅ **TIER monthly-PDF scrape** — **viable, regex pattern verified**. URL: `https://www.tier.org.tw/forecast/{YYYYMM}.pdf`. PDF structure (verified against 202604.pdf, 15 pages): page 9 prose contains a 製造業 line, page 10 prose contains 服務業 + 營造業 lines. Regex template:
     ```
     (\d{4})年(\d+)月(製造|服務|營造)業營業氣候測驗點為([\d.]+)點
     [，,]\s*較(\d+)月修正後[之的為]([\d.]+)點
     ```
     One PDF yields 3 industry values + last-month revision. URL pattern stable since 2025-05 (12+ months observed). Fragility risks: TIER may reword «修正後之/的/為», month segment order may swap, or version footer may shift. **Before building**: regress regex against 5+ historical months to confirm pattern stability; add fallback to extract via positional Chinese-number normalization.
  2. ❌ **Aremos 經統資料庫** (`net.tedc.org.tw`) — paid subscription, ruled out.
  3. ❌ **NDC `index.ndc.gov.tw/n/zh_tw/lightscore` web-app** — origin server returned 522/504 during 2026-05-02 probe; even if reachable, would need browser-grade fetch + reverse-engineered XHR contract. Higher fragility than route #1.
  4. ❌ **MoneyDJ chart endpoint** (`moneydj.com/funddj/yl/BFRK01.djhtm?a=EI010150`) — third-party scrape, ToS unclear, dropped.
  - **Untried (open)**: writing to `service@tier.org.tw` to ask for a structured CSV/Excel monthly feed. Worth a single email before building the PDF parser.
- **Files (when ready)**: new `data-tw/scripts/tier_client.py` with `pdfplumber` or `pymupdf` for text extract + regex above + per-month cache (`~/.cache/investing-toolkit/tier/{YYYYMM}.json`); pack.py wires `tier` preset into regime-pack; classify_tw drops the "9th component" missing flag once `tier_value is not None`. Roughly 1.5–2 hr build + 5-month regex regression.
- **Acceptance**: classify_tw `tier_manufacturing_climate.value` non-null from a live source; integration test asserts `components_9._dispersion.components_found == 9`; per-PDF parser unit test covers ≥5 historical months.
- **Reference**: ROADMAP §v2.1.x-b empirical-finding note; grounding-tw-2026-05.md §"Fixture inspection — 8 of 9 components present (structural NDC bundle gap)"; v2.1.x research session (2026-05-02 Playwright + PDF probe).

### v2.2.0-f — CN credit impulse upgrade to true stock-yoy

- **What**: PR-6 #189 implemented credit impulse via TSF flow-yoy second-derivative (CICC convention) with honest methodology label. Upgrade to true stock-yoy (matches PBOC published 8.3% directly, no 5-20pp magnitude inflation).
- **Why**: Magnitude semantics gap is fully documented in `references/credit-impulse-methodology.md`; closing it removes the caveat.
- **Files**: `data-cn/scripts/akshare_client.py` add `tsf_stock_yoy` extraction (akshare may add it; or scrape pbc.gov.cn directly); `pack.py _compute_credit_impulse` Path 2 activates.
- **Blocker**: Whether PBOC stock series is in akshare; otherwise need direct PBOC scrape.
- **Acceptance**: classify_cn `credit_impulse.methodology` no longer mentions "flow-yoy second-derivative"; Path 2 fires.
- **Reference**: PR-6 #189; `analysis-macro-regime/references/credit-impulse-methodology.md`.

### v2.2.0-j — Cadence-aware adaptive cache TTL across all 14 clients

- **Status**: **Phase 0 + Phase 1 in flight (this PR)** — ADR-0007 + cache-policy.md + dgbas PoC implemented. Phases 2-4 follow.
- **What**: Replace per-client `CACHE_TTL_SECONDS` constants (1h/6h/24h, no rationale) with cadence-aware adaptive TTL. Each preset declares its publication cadence (`monthly`/`quarterly`/`daily`/`tick`/`event`/`immutable`/...); cache helper computes TTL from `cadence × staleness_days` per the [TTL bands](docs/cache-policy.md#ttl-bands) in cache-policy.md. Cache envelope upgraded to schema v2.0 with `_cache_meta.fetched_at` (replaces fragile `path.stat().st_mtime`). Block-level CI sync guard (Group 10 in `check-script-sync.yml`) enforces byte-equality of the helper across all 14 clients.
- **Why**: (1) Monthly CPI cached for 24h means ~30 wasted cache misses per release cycle — cadence-aware caches it for 7 days when fresh and tightens to 4 hours during the release window. (2) `mtime`-based TTL is fragile — `cp` / `rsync` / Docker volume mount / `tar -xzf` (without `-p`) all reset mtime to "now" while data is old. JSON envelope `fetched_at` removes that hazard. (3) DRY policy without breaking PEP 723 self-contained scripts (see ADR-0007 for *why* we embed instead of import a central `_cache.py`).
- **Architecture decision**: ADR-0007 explicitly rejects a central `_cache.py` shared module (would break PEP 723 self-containment + Anthropic skill convention). Each client embeds an identical `# === BEGIN cache helpers === … # === END cache helpers ===` block; CI block-level MD5 enforces equality.
- **Phases**:
  1. ✅ **Phase 0** — ADR-0007 + cache-policy.md + ROADMAP entry (this PR)
  2. ✅ **Phase 1** — dgbas PoC: `data-tw/scripts/dgbas_client.py` + MCP copy refactored end-to-end. Validates block-delimiter pattern, schema v2.0 envelope, cadence-aware TTL. (this PR)
  3. **Phase 2** — Extend `check-script-sync.yml` with Group 10 (block-level MD5 across all 14 clients). Initially the only client with the block is dgbas; check is trivially green. Group expands as Phase 3 migrates more clients.
  4. **Phase 3** — Bulk migration of remaining 13 clients to the synced block + per-preset cadence. Likely staged across 3-4 PRs (TW + KR + CN clients first, then JP + global). Each migration: copy helper block byte-identically; remove old `CACHE_TTL_SECONDS` constant; add `cadence` field to every preset.
  5. **Phase 4** — Close out: deprecate any leftover top-level `fetched_at` fields on data dicts (canonical now lives in `_cache_meta`); update `industry-indicator-cadence.md` cross-reference; update output-schema-overview.md docs across 5 data skills.
- **Files (overall)**: 14 client files (× 2 for skill + MCP copies = 28 file edits), `check-script-sync.yml`, `sync-clients.sh`, `docs/adr/0007-*.md`, `docs/cache-policy.md`, `industry-indicator-cadence.md`, 5 `data-{country}/references/output-schema-overview.md`.
- **Blocker**: None for Phases 2-3. Phase 4 docs touch is bookkeeping.
- **Acceptance** (per phase):
  - Phase 1: dgbas cache file shows `_cache_meta.version: "2.0"` + cadence-aware TTL; pytest 324/27/34 unchanged; live fetch shows `_cache: hit` + `_cache_age_seconds` + `_cache_ttl_seconds` on second invocation.
  - Phase 2: check-script-sync.yml Group 10 runs green on dgbas alone; deliberate-drift smoke test (mutate one helper line) → CI fails.
  - Phase 3 (per migration PR): `pytest -m "not network"` green; `bash sync-clients.sh --check` 0 drift; cache file inspection on each migrated client shows v2.0 envelope.
  - Phase 4: `grep -r "CACHE_TTL_SECONDS" investing-toolkit/` returns 0 matches.
- **Reference**: ADR-0007; cache-policy.md; 2026-05-03 design session (per-client copy-paste mode rejected for cache helper drift; central `_cache.py` rejected for PEP 723 / Anthropic violation).

## Long-term — Phase 2 + beyond

### Phase 2 — cross-country comparable surface (ADR-0005, deferred)

- **What**: Bottom-up design of `cross_country` block in regime card (currently null in Phase 1). Inspect 5 actual `native_verdict` shapes after Phase 1 has run for ≥4 weeks; identify common axes; ship comparable surface.
- **Re-trigger conditions** (any one):
  - [ ] Phase 1 stable on main ≥ 4 weeks (currently 0 days)
  - [ ] ≥ 5 multi-country `/invest-macro` or `/invest-portfolio` invocations producing real regime cards
  - [ ] Buy-side memo workflow concretely needs cross-country alignment that Phase 1 doesn't deliver
  - [ ] v2.2.0 release planning fits Phase 2 scope
- **6-month review**: If none fire, evaluate whether comparable surface is needed at all. 5 countries may be too heterogeneous for unified surface to add value over per-country `native_verdict` reads.
- **Reference**: [ADR-0004](docs/adr/0004-analysis-macro-regime-phase1-per-country-classifiers.md) §"Phase 2 — Deferred"; ADR-0005 (placeholder, not yet written).

### Earnings analysis workflow (blocked)

- **What**: Earnings beat/miss + revision tracking + estimate dispersion.
- **Blocker**: **Free consensus data source.** Refinitiv I/B/E/S, FactSet, Bloomberg = all paid. yfinance `analyst_estimates` is thin and stale. Visible Alpha / Estimize have free tiers but coverage is partial.
- **Status**: Not actionable without data source decision. Re-evaluate when a free / cheap source surfaces.
- **Reference**: v2.0.0 deferred list.

## Dropped (philosophy mismatch)

- ❌ **3-statement model** — sell-side artifact incompatible with buy-side primary-source pipeline philosophy. See ROADMAP §"v2.0.0 Dropped".
- ❌ **Per-country IC quadrant force-fit** — superseded by ADR-0004 (v2.1.0). Native classifiers replace unified IC where the framework breaks down (CN inflation framing inversion, JP exit-deflation, TW NDC 五色-led).

## How to pick the next item (for fresh-session pickup)

1. **Default**: do near-term v2.1.x patches first (a/b/c/d) — closes Phase 1 loose ends, ~3-5 days total
2. **If a v2.2.0 item is more compelling**: pick from a/b/c/d/e/f based on:
   - **Blocker readiness**: ECOS key applied? DART key still valid?
   - **Strategic value**: KR DART (v2.2.0-e) is the highest-leverage — covers KR's biggest gap and unblocks downstream KR memo-fetch / DCF
   - **Cost**: comps `--mode compute` (v2.2.0-b) is the cheapest material upgrade
3. **Phase 2**: don't proactively start; wait for re-trigger conditions
4. **Earnings**: skip until free data source surfaces

For each item, the brief above should be sufficient to start a fresh session with `/loop` or subagent-driven-development. Reference the linked ADR for design rationale; reference linked PRs for prior-art commits.

---



**Scope**: Decompose v1.9.0 unified IC + Hedgeye GIP classifier into 5 native per-country modules (`classify_us / jp / tw / kr / cn`). Defer cross-country comparable surface to Phase 2 (ADR-0005). See [ADR-0004](docs/adr/0004-analysis-macro-regime-phase1-per-country-classifiers.md).

### Shipped (PR-1 ~ PR-7)

- [x] PR-1: dispatcher infra (`_helpers.py` from former `_legacy_ic.py`, `_surface.py` `CountryRegimeCard`/`Phase1Output` dataclasses, `calibrations/` reader, TW `GROWTH_KEYS` patch, regression test)
- [x] PR-2: `classify_us.py` baseline + `calibrations/us.yaml` + `grounding-us-2026-05.md` (US is reference pattern for PR-3-6)
- [x] PR-3: `classify_jp.py` (BOJ + Tankan + ESRI CI + deflation regime) + `boj_client.py --tankan-business-di` flag (4 series codes verified vs BOJ docs) + e-Stat preset additions in `data-jp/pack.py`
- [x] PR-4: `classify_tw.py` (NDC 五色 + 9 構成 + TIER + TSMC overlay)
- [x] PR-5: `classify_kr.py` (BOK target + KOSTAT cycle + 가계부채 overlay + KOSPI concentration)
- [x] PR-6: `classify_cn.py` (PBOC + credit impulse + 4-comp dispersion + 房地产 overlay + CPI framing) + `_compute_credit_impulse()` in `data-cn/pack.py` + methodology doc
- [x] PR-7: cleanup (remove `_legacy_ic.py`, M1 rename `policy_target_pct` semantic collision, m1/m2 quote YAML dates, m3 cn.yaml `partial_refresh`, m4 KR ESI deferral note, bump v2.1.0)

### Process

- [x] 8 internal reviewer subagents (spec + code-quality × 4 countries) — all PASS/APPROVED, 0 MAJOR
- [x] Cross-country fresh-eyes audit — PASS_WITH_NOTES (1 MAJOR + 4 MINOR, all addressed in PR-7)
- [x] Native-language grounding (日本語 / 繁中 / 한국어 / 简中) — JP captured 4 material BOJ events (FY2026 outlook 1.9%→2.7-2.8%, 6-3 vote, Ueda 4/30 anchor)

### Deferred to v2.1.x / v2.2.0 / Phase 2

- [ ] **Phase 2 (ADR-0005)**: cross-country comparable surface design — bottom-up from observed `native_verdict` shapes. Re-trigger conditions: Phase 1 stable ≥4 weeks, ≥5 multi-country invocations, or buy-side memo workflow surfacing concrete need.
- [ ] KR ESI explicit ECOS API integration (free key required at ecos.bok.or.kr)
- [ ] TW TIER preset wiring at NDC client level + live TWSE monthly weight ingestion
- [ ] CN true stock-yoy credit impulse when PBOC publishes via akshare or direct scrape
- [ ] JP regime-pack fresh fixture refresh post-PR-3 (test currently uses pre-PR-3 fixture; classifier's IP-fallback path engaged)

---

## v2.0.0 — Three-Layer Architecture + Comps (released 2026-05-01)

**Scope**: Reorganize 15 v1.x skills into 5 data-{country} + 6 analysis-* + 4 report-* + 1 router (16 total). Add `analysis-comps` (peer multiples). Add runtime peer-discovery in `report-equity-memo`. Parallelize `fred_client` multi-series fetch (8 worker default).

### Skills
- [x] 5 Layer 1 data-{country}: data-us / data-jp / data-tw / data-kr / data-cn
- [x] 6 Layer 2 analysis-*: analysis-dcf / analysis-comps / analysis-screener / analysis-technical / analysis-portfolio / analysis-macro-regime
- [x] 4 Layer 3 report-*: report-equity-memo / report-stock-snapshot / report-portfolio-review / report-screener-list
- [x] using-investing-toolkit (router)

### Commands
- [x] All v1.x slash commands preserved (`/invest`, `/invest-macro`, `/invest-memo`, `/invest-screen`, `/invest-portfolio`)
- [x] NEW `/invest-snapshot` (single-ticker quick card)

### Architecture
- [x] ADR-0001: Three-Layer Skill Architecture
- [x] CI MD5 sync workflow (yfinance × 5, fred × 2, nbs × 1, akshare × 1)
- [x] sync-clients.sh canonical → copies helper
- [x] 296 non-network + 27 network automated pytest tests

### Deferred to v2.1+
- [ ] Sector-adjusted multiples for Comps (banks P/B+ROE / REITs P/AFFO / tech EV/Revenue+Rule-of-40)
- [ ] `analysis-comps --mode compute` activation (currently placeholder)
- [ ] JP real-rate decomposition C+D+E framework restoration (ECB ex-post + Tankan + JGBi)
- [ ] KR DART primary-source equity integration
- [ ] Earnings analysis workflow (waiting for free consensus data source)
- [ ] CI script-sync check promotion to required (currently advisory)

### Dropped
- ❌ 3-statement model (sell-side artifact, philosophy mismatch with buy-side primary-source pipeline)

---

## v1.0.0 — US + Macro Layer (current)

**Scope**: US stocks via yfinance + FRED macro data. Core invest* slash commands.

### Skills
- [x] using-investing-toolkit (router)
- [x] macro-regime-snapshot (IC + yield-curve + FRED)
- [x] us-stock-snapshot (yfinance + SEC EDGAR)
- [x] investment-memo-writer (→ domain-teams:investing-team)
- [x] dcf-valuation (3-stage DCF + sensitivity)

### Commands
- [x] /invest (router)
- [x] /invest-macro (regime call)
- [x] /invest-memo (full memo pipeline)

### Data adapters
- [x] scripts/yfinance_client.py
- [x] scripts/fred_client.py
- [x] agents/data-fetcher.md

---

## v1.1.0 — Taiwan Layer (current)

**Scope**: Taiwan equity data via FinMind. taiwan-stock-snapshot skill.

### New
- [x] scripts/finmind_client.py (FINMIND_API_TOKEN env, anonymous fallback)
- [x] skills/taiwan-stock-snapshot/SKILL.md
- [x] CasualMarket MCP installation guide (in scripts/README.md + taiwan-stock-snapshot)
- [x] investment-memo-writer Phase 1: FinMind commands for .TW/.TWO tickers
- [ ] /invest-screen {ticker} with --universe tw50 support (moved to v1.2.0)

---

## v1.2.0 — Screener + Technical Layer

**Scope**: Technical indicators, batch screener, portfolio review.

### New
- [x] scripts/ta_client.py (RSI/MACD/Bollinger/ATR/SMA from OHLCV, no external API)
- [x] scripts/yfinance_client.py --tickers batch mode
- [x] skills/technical-snapshot/SKILL.md (RSI, MACD, Bollinger, ATR, SMA)
- [x] skills/stock-screener/SKILL.md (valuation + momentum + trend composite score)
- [x] skills/invest-portfolio/SKILL.md (P&L snapshot + regime overlay + investing-team delegation)
- [x] /invest-screen {tickers} [--pe-max] [--above-sma200] [--rsi-min/max]
- [x] /invest-portfolio [holdings.csv | inline-list]

---

## v1.3.0 — Country Macro Skills (current)

**Scope**: Country-specific macro data skills with bilingual indicator references.

### New
- [x] scripts/boj_client.py (BOJ Time-Series API, no auth)
- [x] scripts/estat_client.py (統計ダッシュボード API, no auth)
- [x] skills/us-macro/SKILL.md (FRED 8 indicators + reference doc)
- [x] skills/japan-macro/SKILL.md (BOJ + 統計DB 13 indicators + bilingual reference)
- [x] macro-regime-snapshot: region=japan support
- [x] japan-boj-db-catalog.md (40+ DB bilingual catalog)

---

## v1.4.0 — Taiwan Macro

**Scope**: Taiwan macro indicators from 4 government sources.

### New
- [x] scripts/statgov_client.py (stat.gov.tw hidden chart JSON, 17 presets)
- [x] scripts/cbc_client.py (CBC Open Data API, 5 presets)
- [x] scripts/dgbas_client.py (DGBAS Excel .xls, 6 presets)
- [x] scripts/ndc_client.py (NDC ZIP/CSV, 6 presets)
- [x] skills/taiwan-macro/SKILL.md (30 indicators, 8 groups, trilingual references)

---

## v1.5.0 — Korea Macro

**Scope**: Korea macro indicators via FinanceDataReader (BOK ECOS-KEYSTAT).

### New
- [x] scripts/fdr_client.py (FinanceDataReader ECOS-KEYSTAT, 27 presets + 1 FRED)
- [x] skills/korea-macro/SKILL.md (28 indicators, 10 groups, trilingual references)
- [x] Unified indicator reference format across US/JP/TW/KR (93 indicators)
- [x] Cache migration to $CLAUDE_PLUGIN_DATA convention (10 scripts)

---

## v1.6.0 — China Macro

**Scope**: China macro indicators via akshare (NBS + PBOC + SHIBOR),
FRED fallbacks (CNY/USD, FX reserves), and yfinance market indices.

### New
- [x] scripts/akshare_client.py (19 presets: inflation/growth/trade/labor/sentiment/rates/money/credit — 2 Caixin PMI presets removed 2026-04-18, mirror ran 8mo stale)
- [x] skills/china-macro/SKILL.md (26 indicators total: 19 akshare + 2 FRED + 5 yfinance, trilingual references)
- [x] NBS WAF workaround — akshare mirrors (eastmoney, investing.com, chinamoney, shibor.org) remain reachable when `data.stats.gov.cn` blocks foreign IPs
- [x] 10 reference files including 119 indicator sections across US/JP/TW/KR/CN (unified format)
- [x] NBS new-SPA API reverse-engineered (`docs/nbs-indicator-catalog.md`): 2908-leaf indicator tree captured for future `nbs_client.py` work

---

## v1.7.0 — Monthly GDP Proxies for US + JP

**Scope**: Cross-market symmetric monthly GDP tracking. US and Japan gain
the monthly-GDP-proxy indicator packages that china-macro already provides
via 三大數據 + services-production.

**Background**: No major economy publishes official monthly GDP (UK and
Canada are exceptions). For US, the Fed family of nowcasts (GDPNow, CFNAI,
WEI) plus OECD CLI are the industry-standard proxies. For Japan, the
内閣府 景気動向指数 CI trio (先行/一致/遅行) is the canonical proxy, with
一致指数 treated as the definitive "current GDP feel".

### New
- [x] us-macro: +4 presets under new `nowcast` group — `GDPNOW` (Atlanta Fed), `CFNAI` (Chicago Fed), `WEI` (NY Fed), `USALOLITOAASTSAM` (OECD CLI, replacing discontinued USSLIND). 21 → 25 series.
- [x] japan-macro: +2 presets `leading-index` + `lagging-index` completing the 景気動向指数 CI trio. 14 → 16 active indicators.
- [x] references/indicators-growth.md expanded in both skills with full monthly-GDP-proxy documentation.

---

## v1.7.1 — China monthly GDP proxy tagging

**Scope**: Tier 2 symmetry with us-macro / japan-macro. Explicitly tag
三大数据 + `services-production-yoy` as monthly GDP proxy components
in china-macro documentation so all three country skills share the
same proxy-labelling convention.

### New
- [x] china-macro SKILL.md: Monthly GDP proxy callout in Overview; `growth` group re-titled as "三大数据 — monthly GDP proxy components"; 4 indicator rows tagged with bold proxy labels
- [x] china-macro README.md: cross-market parity Overview note
- [x] references/indicator-index.md: 4 indicators tagged `(**monthly GDP proxy component/companion**)`
- [x] references/indicators-growth.md: new 三大数据 monthly trio preamble explaining cross-market parallel + why Tier 3 synthesis is deferred
- [x] references/indicators-services.md: `services-production-yoy` annotated as 2017-introduced services-gap filler in the proxy package

### Deliberately NOT done — Tier 3 (synthesised single-number proxy)

Research finding: no market consensus across Li Keqiang Index (obsolete
post-2012 services shift), SF Fed China CAT (quarterly + standard-deviation
units, not monthly %YoY), Goldman CAI / Bloomberg China Monthly GDP
(proprietary), academic DFM nowcasts (each paper uses a different
variable set). Picking any single methodology would embed an analytical
choice in the data layer, violating the toolkit/analysis separation in
`CLAUDE.md` cross-plugin contract. Synthesis belongs in `investing-team`
analysis layer. See `docs/china-macro-research-frameworks.md §1d` for
deferred methodology options if requirements change.

---

## v1.7.2 — Router sync + Layer column

**Scope**: Documentation-only. Update `using-investing-toolkit/SKILL.md`
to reflect post-v1.6.0 indicator counts, the v1.7.0/v1.7.1 Monthly GDP
Proxy framework, and a new `Layer` column distinguishing data /
aggregation / delegation skills.

### New
- [x] using-investing-toolkit skill table synced: us-macro 21→25 series, japan-macro 20→22 presets, china-macro 28→34 indicators
- [x] Skill versions updated: us-macro / japan-macro → v1.7.0, china-macro → v1.7.1
- [x] Cross-market Monthly GDP Proxy Framework section added — summarises US nowcast / JP CI trio / CN 三大数据 parity + why CN stays Tier 2
- [x] `Layer` column added to Available Skills table (data / aggregation / delegation); skills re-sorted by layer for easier discovery

---

## v1.7.3 — Taiwan + Korea monthly GDP proxy tagging

**Scope**: Extend the cross-market Monthly GDP Proxy Framework from 3 to 5
markets. TW and KR already had CI-family indicators in their skills; v1.7.3
adds the Tier 2 tagging + framework row + references preamble.

### New

- [x] taiwan-macro: tag `signal` / `leading-index` / `coincident-index` as
  monthly GDP proxy components; SKILL + README + indicator-index + indicators-cycle
  (4 files) updated with **Taiwan 特色 五色景氣燈號** emphasis
- [x] korea-macro: tag `leading-cycle` (K254) / `coincident-cycle` (K253) as
  monthly GDP proxy leading + proxy; SKILL + README + indicator-index +
  indicators-sentiment (4 files) updated
- [x] Cross-market Monthly GDP Proxy Framework expanded from 3 → 5 markets
  in both `using-investing-toolkit/SKILL.md` and plugin-level `README.md`

### Deliberately NOT done

- **KR lagging CI** (후행지수순환변동치) — probed K255/K256; both map to
  other series (manufacturing-related, 16 rows) rather than Lagging CI
  Cyclical Component. BOK ECOS KEYSTAT does not expose this index.
  Statistics Korea (KOSIS) publishes it but would require a separate
  scraper — deferred to v1.8.0 if demand arises.
- **TW Tier 3 synthesis** — not needed; NDC already publishes pre-aggregated
  composite score + colour via `signal`.
- **KR Tier 3 synthesis** — not needed; BOK ECOS already publishes
  pre-aggregated CI cyclical components.

---

## v1.8.0 — Korea-macro catalogue + structural refactor + Tier-B expansion

**Scope**: Three-phase korea-macro upgrade — document the full BOK ECOS
KEYSTAT catalogue (mirror of the v1.6.0 NBS tree work for CN), refactor
the `sentiment` group, and add 15 Tier-B presets across 5 existing
groups + 1 new `demographics` group.

### Phase 1 — Catalogue
- [x] `skills/korea-macro/docs/bok-ecos-keystat-catalog.md` — 98-code
  human-readable catalogue grouped by category (monetary / rates /
  markets / FX / activity / CI / labor / BoP / prices / demographics)
  with preset status (in-skill / v1.8.0 / candidate / skip)
- [x] `skills/korea-macro/docs/bok-ecos-keystat.json` — machine-readable
  raw probe output
- [x] `skills/korea-macro/docs/tools/probe-keystat.py` — re-probe script
  (sweeps K001-K500)

### Phase 2 — Structural refactor
- [x] Split `sentiment` group into `sentiment` (CSI K252 / ESI K269 —
  survey-based) + `cycle` (CI pair K253/K254 — business cycle indices).
  Fixes the semantic inconsistency inherited from v1.5.0.
- [x] New `references/indicators-cycle.md` (moved CI content out of
  `indicators-sentiment.md`); `indicators-sentiment.md` retains only
  CSI/ESI

### Phase 3 — Tier-B expansion (+15 presets, 28 → 43 indicators)
- [x] `rates`: +`koribor-3m` (K063) — cross-market parallel of JP SHIBOR 3M
- [x] `growth`: +`private-consumption` (K259), +`equipment-investment` (K260),
  +`construction-investment` (K261) — GDP expenditure breakdown
- [x] `trade`: +`goods-exports` (K462) — fills the major gap of
  no-exports-indicator (KR export dependency ~40% of GDP)
- [x] `money`: +`m1` (K002), +`lf` (K004) — cross-market symmetry with JP/CN
- [x] `fx`: +`krw-jpy` (K153), +`krw-eur` (K154), +`krw-cny` (K156),
  +`fx-reserves` (K155)
- [x] **New `demographics` group** (+3 presets): `population` (K451),
  `aging-ratio` (K460), `fertility-rate` (K461) — long-horizon structural
  context (KR leads JP demographic decline by ~15-20 years)
- [x] New `references/indicators-demographics.md`

### Deferred (v1.9.0 candidate)

- **Full BOK ECOS API integration** — would unlock the remaining Tier-B
  candidates (identified in `docs/bok-ecos-keystat-catalog.md` as
  `candidate` rows) plus the lagging CI (후행지수순환변동치) not
  exposed via KEYSTAT. Requires free API key registration at
  https://ecos.bok.or.kr/api/#/AuthKeyApply.

---

## v1.8.1 — Korea industry activity layer

**Scope**: Closes the KR sector-activity coverage gap (identified as
`candidate` in v1.8.0 catalogue) — adds the monthly K201-K217 경제활동
cluster as a new `industry` group. Parallels JP `activity` group and
TW `production` group; completes cross-market parity for monthly
sector pulse.

### Phase 1 — New `industry` group (+11 presets, 43 → 54 indicators)
- [x] Manufacturing trio: `manufacturing-inventory` (K202),
  `manufacturing-shipment` (K203), `manufacturing-operating-rate` (K204)
- [x] Services + retail: `services-production` (K205),
  `retail-sales` (K206), `wholesale-retail` (K207),
  `credit-card-usage` (K210)
- [x] Capex cycle: `machinery-orders` (K213),
  `capital-goods-output` (K215)
- [x] Construction cycle: `construction-completion` (K216),
  `construction-orders` (K217)

### Phase 2 — Documentation
- [x] `skills/korea-macro/references/indicators-industry.md` (new, bilingual)
- [x] `skills/korea-macro/SKILL.md` — new group section + Step 1/2 fetch
  batches + lag table entries
- [x] `skills/korea-macro/README.md` — counts 43 → 54, group list 12 → 13
- [x] `skills/korea-macro/references/indicator-index.md` — 11 new rows +
  `industry (11)` group row
- [x] `skills/korea-macro/docs/bok-ecos-keystat-catalog.md` — 11 rows
  flipped `candidate` → `v1.8.1`
- [x] `skills/using-investing-toolkit/SKILL.md` + plugin-level `README.md`
  counts updated

### Deferred
- v1.10.0+: full BOK ECOS API integration (lagging CI + ~10K series,
  requires free API key; originally scoped as v1.9.0, re-deferred when
  macro-regime refresh took v1.9.0 slot)

---

## v1.9.0 — macro-regime-snapshot multi-country + LSEG real-rate block

**Scope**: Rewrite `macro-regime-snapshot` to cover **all 5 country
macro skills** (US/JP/TW/KR/CN) using the v1.7.0 monthly GDP proxies,
and absorb the LSEG `macro-rates-monitor` dashboard pattern — new
5-block output (Macro Summary / Yield Curve / Real Rate / IC+GIP /
Asset-Class Tilts) with signal-label semantics
(Expansion/Contraction, Accommodative/Restrictive). Adds US real-rate
block via 4 new FRED series; IC + GIP framework unchanged.

### Phase 1 — us-macro `real-rates` group (+4 FRED series, 25 → 29 total)
- [x] `scripts/` — no change (fred_client.py is a generic CSV fetcher)
- [x] `skills/us-macro/SKILL.md` — new `real-rates` group section + Step 1/2 updates
- [x] `skills/us-macro/references/us-macro-indicators.md` — new Real Rates
  section (T5YIE, T10YIE, DFII5, DFII10) with threshold framing

### Phase 2 — macro-regime-snapshot rewrite
- [x] `skills/macro-regime-snapshot/SKILL.md` — complete rewrite:
  - `region` expanded 3 → 9 values (us / japan / taiwan / korea / china /
    global / asia-pac / all / free-form list)
  - Per-country proxy routing (use v1.7.0 monthly GDP proxies, not raw IPI)
  - New Step 4: real-rate decomposition block (US only)
  - New Step 5: 5-block dashboard output format
- [x] `skills/macro-regime-snapshot/references/investment-clock-cheatsheet.md`
  — extended with per-country proxy mapping, real-rate thresholds
  section, signal-label glossary (LSEG absorption)

### Phase 3 — Plugin-level docs
- [x] `commands/invest-macro.md` — `--region` enum updated to 9 values +
  examples + Real-Rate block note
- [x] `skills/using-investing-toolkit/SKILL.md` — rows for us-macro
  (+ real-rates) and macro-regime-snapshot (5-country + LSEG dashboard)
- [x] `README.md` — Skills table counts + Version Highlights entry
- [x] `ROADMAP.md` — this v1.9.0 entry
- [x] `.claude-plugin/plugin.json` — 1.8.1 → 1.9.0

### Phase 4 — Per-country threshold calibration (Option B hybrid)
- [x] `references/thresholds-{us,japan,taiwan,korea,china}.md` (5 new
  files, consistent 8-section template) — per-country inflation target,
  NAIRU, r* estimate, real-rate block status, structural regime notes,
  asset-class tilt calibration, primary-source URLs, native-language sources
- [x] `references/recalibration-protocol.md` — triggers, cadence,
  source tiers (A/B/C/D), native-language priority, escalation rules
- [x] SKILL.md Step 1 — per-country threshold-file routing + explicit
  "do NOT apply US thresholds to non-US countries" guardrail

### Phase 5 — Primary-source grounding audit (following domain-teams convention)
- [x] `research/grounding-v1.9.0.md` — **consolidated audit trail**
  (5 parallel native-language research agents, 2026-04-18). Fixed
  **19 🔴 + 16 ⚠️ corrections** across 5 countries (critical vintage
  errors in BOJ展望/JILPT NAIRU/Fed FAIT-retired/PBOC-CPI-target-
  reduced/KOSPI-concentration/TSMC-weight). 20-year trajectory
  research (2005-2026) per country. Includes JP integration decision
  (full native-language priority), fabrication-risk warnings
  (3 unverifiable citations removed).
- [x] Threshold files updated with "Grounding Status" blocks at top
  (per-file corrections audit + next-recalibration date).
- [x] Cheatsheet "Threshold provenance" updated with revised r*
  estimates (HLW 0.75%, LM 1.68%, not prior 1.42% / 2.15%).

### LSEG absorption summary

Pattern ported from Anthropic's `financial-services-plugins/partner-built/lseg/skills/macro-rates-monitor` (paid MCP → free FRED data):

| LSEG pattern | Our port |
|--------------|----------|
| 4-block dashboard (Macro / Curve / Real Rate / Swap) | 5-block (added IC + GIP + Asset Tilts) |
| Real-rate decomposition (nominal − breakeven) | US-only via T5YIE/T10YIE/DFII5/DFII10 |
| Signal labels (Expansion/Restrictive/etc.) | Added to Block 1 + glossary in cheatsheet |
| Yield-curve slope + shape | Preserved (Block 2) |
| Swap-spread block | **Deferred to v1.10.0+** (needs more FRED series) |

### Deferred to v1.10.0+
- JP JGBi real-rate (MoF XLS scraper) — **delivered in v1.10.0 as C+D+E multi-source**
- KR KTBi real-rate (needs BOK ECOS API key) — still deferred
- ISM PMI via FRED NAPM — still deferred (FRED relicensing not available)
- TW / KR local PMI (製造業採購經理人指數 / 기업경기실사) — still deferred
- Swap-spread block — **delivered in v1.10.0 as Treasury-SOFR 3M proxy**
- Full BOK ECOS API (lagging CI 후행지수 + 10K series; re-deferred from v1.9.0)

---

## v1.10.0 — PMI + JP real rates + swap spread

**Scope**: Closes three data-coverage gaps from v1.9.0 deferred list —
ISM-substitute PMI in us-macro (OECD CLI proxy), full JP real-rate
support via C+D+E multi-source framework, and US swap-spread block
via Treasury-SOFR 3M proxy. `macro-regime-snapshot` Block 3 renamed
"Rate Stress Dashboard" to absorb the new JP real-rate and US
swap-spread sub-blocks.

### Phase 1 — us-macro `pmi` group (OECD CLI fallback)
- [x] `skills/us-macro/SKILL.md` — new `pmi` group section (single series
  USALOLITOAASTSAM, already fetched under `nowcast`; reused as PMI proxy
  with threshold documentation). ISM / S&P Global PMI removed from FRED
  in 2016 (St. Louis Fed blog citation in `references/us-macro-indicators.md`
  "PMI" section). USALOLITOAASTSAM counted once in the 31-series total.
- [x] `skills/us-macro/references/us-macro-indicators.md` — "PMI" section
  added with OECD CLI methodology + threshold framing (100 = long-run
  avg; ≥100.5 expansion, ≤99.5 contraction).

### Phase 2 — japan-macro `real-rates` group (C+D+E multi-source) + grounding note
- [x] `scripts/ecb_client.py` — new SDMX client for ECB long-term
  monthly ex-post real yields (M.JP.JPY.4F.BB.R_JP10YT_RR.YLDA).
- [x] `scripts/boj_client.py` — extended for Tankan
  1Y/3Y/5Y expected inflation series.
- [x] `skills/japan-macro/SKILL.md` — new `real-rates` group + Step 3b
  (ECB fetch) + multi-source routing table (MoF snapshot anchor + ECB
  monthly + Tankan survey). Presets: 22 → 27; groups: 9 → 10.
- [x] `skills/japan-macro/references/indicators-japan-real-rates.md` —
  new reference; C+D+E framework documentation.
- [x] `research/grounding-v1.10.0.md` — primary-source vetting for 3 new
  data sources (MoF auction history / ECB SDMX / BOJ Tankan) +
  rejection rationale for JSDA (999.999 sentinel confirmed via probe) /
  JBTS paths.

### Phase 3 — us-macro `swap-spreads` group (T-SOFR 3M proxy)
- [x] `skills/us-macro/SKILL.md` — new `swap-spreads` group section
  (DGS3MO − SOFR30DAYAVG proxy). 14-group structure documented.
- [x] `skills/us-macro/references/us-macro-indicators.md` — "Swap Spread /
  Money-Market Stress" section added with post-LIBOR methodology
  explanation (FRED has no clean term swap series after LIBOR wind-down).

### Phase 4 — macro-regime-snapshot integration
- [x] `skills/macro-regime-snapshot/SKILL.md` — Block 1 PMI row per
  country (US fetched live; JP/TW/KR/CN URL-only references pending
  licensed access). Block 3 renamed "Rate Stress Dashboard" with
  JP real-rate sub-block (C+D+E output) and US swap-spread sub-block.
  Step numbering preserves existing 5-block output contract.
- [x] `skills/macro-regime-snapshot/references/investment-clock-cheatsheet.md`
  — Rate Stress Dashboard interpretation guide added.

### Phase 5 — Plugin-level sync
- [x] `skills/using-investing-toolkit/SKILL.md` — us-macro / japan-macro /
  macro-regime-snapshot rows bumped to v1.10.0 with new groups/blocks noted.
- [x] `README.md` — v1.10.0 Version Highlights entry + Skills table
  updates for 3 affected rows.
- [x] `ROADMAP.md` — this v1.10.0 entry; v1.9.0 de-marked as (current).
- [x] `.claude-plugin/plugin.json` — 1.9.0 → 1.10.0.

### Deferred → partially delivered in v1.11.0

- CN Caixin PMI via akshare (eastmoney-backed) + NBS PMI via `nbs_client`
  **delivered** in v1.11.0 `china-macro.pmi` group (5 presets)
- TW Manufacturing PMI + NMI **delivered** in v1.11.0 `taiwan-macro.pmi`
  group via NDC 政府資料開放 dataset 6100 (free-tier access discovered
  during APAC probe)

---

## v1.16.5 — investment-memo-writer Phase 3 retarget to investing-team (current)

**Scope**: Small correctness fix closing a v1.12.0 drift.

### The stale routing

v1.12.0 (commit 2a92193) retargeted investment-memo-writer Phase 3
from `domain-teams:investing-team` → `domain-teams:research-team`
under the false premise "investing-team v5.0.0-v5.1.0 transient".
That premise was wrong — git log shows investing-team was created
at v5.0.0 (df10eaa) as a permanent team:
  - 12 standards / 5 protocols / 2 checklists / 5 rubrics
  - ISQ gate added v5.1.0 (de4d3b2)
  - Visibility Convention added v5.2.0 (323b50b)

research-team's own SKILL.md (since v5.0.0) explicitly redirects
investment work BACK to investing-team (lines 8-9, 68, 444-457 of
research-team/SKILL.md). So the v1.12.0 choice was:
  - Architecturally wrong (CLAUDE.md §Cross-Plugin Delegation
    Contract names investing-team as the canonical target)
  - Runtime inefficient (research-team bounces back to investing-team
    via SKILL.md prose redirect; one wasted LLM hop per memo)

### Commits (2)
- [x] Commit 1 (fix): `skills/investment-memo-writer/SKILL.md` —
      frontmatter description / Phase 3 heading+body / Taiwan detection
      paragraph / narration example / Cross-Plugin Delegation Contract
      § all retargeted research-team → investing-team. Phase 3 Gates
      table replaced with the real investing-team gate stack (was
      listing 7 invented "research-team gates"; now lists 2 MUST +
      4 SHOULD + 1 MAY from investing-team rubrics/).
- [x] Commit 2 (chore): plugin sync 1.16.4 → 1.16.5 + README +
      ROADMAP.

### Impact
- Functional: one fewer LLM indirection hop per memo dispatch.
- Correctness: Phase 3 now reaches investing-team directly instead of
  relying on research-team's SKILL.md prose bounce.
- Contract alignment: matches CLAUDE.md canonical delegation target.

No code / script / test changes. Regression 26/26 pass (unchanged).

---

## v1.16.4 — taiwan-stock-snapshot TWSE `/rwd/` wiring + design-principles doc

**Scope**: Small polish release closing two v1.16.3 loose ends.

### Commits (3)
- [x] Commit 1 (fix): `taiwan-stock-snapshot/SKILL.md` — wires TWSE
      `/rwd/` stock-day-history into Phase 1 as an explicit Tier A
      option for `.TW` tickers when memo needs regulator-raw prices.
      The action is no longer orphan (v1.16.3 shipped it documented
      only). Complements the yfinance-primary default used in
      technical-snapshot.
- [x] Commit 2 (docs): `docs/design-principles.md` (NEW) — codifies
      the "empirical-first design" rule earned from v1.14.0 + v1.16.3.
      README gains a link in Cross-country Reference Documents.
- [x] Commit 3 (chore): plugin sync 1.16.3 → 1.16.4.

No code / script / test changes. Regression suite unchanged (26/26).

### Tier A raw vs split-adjusted consumer map (post-v1.16.4)

| Consumer | Wants | Uses |
|---|---|---|
| `technical-snapshot` (RSI/MACD/BB/ATR/SMA) | Split-adjusted (TA standard) | yfinance_client |
| `stock-screener` (batch filter) | Split-adjusted | yfinance_client |
| `taiwan-stock-snapshot` (memo + ISQ citation) | Regulator-raw (primary-source) | twse_openapi stock-day-history for .TW; FinMind TaiwanStockPrice for .TWO |
| `investment-memo-writer` (via taiwan-stock-snapshot) | Regulator-raw | Same as above |

---

## v1.16.3 — TWSE stock-day-history action + empirical yfinance validation

**Scope**: User flagged technical-snapshot / stock-screener hard-coded
yfinance and asked whether TW coverage was reliable. Originally planned
as a suffix-based router (TWSE `/rwd/` primary for .TW). Mid-stack
empirical testing confirmed yfinance actually covers `.TW` / `.TWO`
correctly with split-adjusted prices (TA standard), so the final
architecture keeps yfinance as default for ALL markets and makes TWSE
`/rwd/` an *explicit-request* action for memo-citation primary-source
use.

### What's new in v1.16.3 code

Still valuable despite the priority flip — Tier A primary-source TW
OHLCV is useful for `taiwan-stock-snapshot` memo contexts where
regulator-raw prices are required:

`twse.com.tw/rwd/zh/afterTrading/STOCK_DAY` — discovered via
stock-day.html form inspection 2026-04-19. Not in openapi.twse.com.tw
catalogue. TWSE-authored → Tier A; month-granularity; past months
immutable (30d cache TTL).

### Commits (6)
- [x] Commit 1 (feat): `scripts/twse_openapi_client.py` — new
      `stock-day-history` action with per-month cache + ta-ready
      normalization (ROC→Gregorian, lowercase fields, parsed floats).
      MCP tool surface + contract test fixture updated.
- [x] Commit 2 (refactor): `scripts/ta_client.py` auto-compute
      `latest_date` / `latest_close` from `data[]` last row when
      absent. Defensive across all sources.
- [x] Commit 3 (fix): `skills/technical-snapshot/SKILL.md` — suffix
      router (original: TWSE primary for .TW).
- [x] Commit 4 (fix): `skills/stock-screener/SKILL.md` — partition
      `--tickers` by suffix (original).
- [x] Commit 5 (chore): Plugin sync 1.16.2 → 1.16.3.
- [x] Commit 6 (fix): **Flip .TW / .TWO priority to yfinance primary**
      after empirical validation — TSMC 2330.TW via yfinance returned
      243 rows / 1y in TWD with full info. Reverts Phase 1 to
      yfinance-for-all-markets; TWSE `/rwd/` stays as documented
      advanced action for memo-citation mode.

### Lesson learned

Should have empirically tested yfinance TW coverage BEFORE designing
the suffix router. Architected 5 commits around a hypothesis that
didn't survive contact with reality. TWSE `/rwd/` code still lands
(useful for memo primary-source citation), but the Phase 1 routing
stays simpler than initially planned.

### Known gaps / deferred
- KR/CN individual-stock primary-source clients — tracked in v1.15.0+
  deferred list; keep yfinance for now.
- Extended stock-screener country-specific signals (TW 融資融券 score,
  etc.) — out of scope.

---

## v1.16.2 — mops_fetch required-param validation

**Scope**: User-reported bug fix. `mops_fetch(action=..., ticker=...)` without
required year/month/season args used to crash with the cryptic Python error
`unsupported format string passed to NoneType.__format__` (f-string format
spec on None value from `types.SimpleNamespace` defaulting). Now returns a
friendly `{"error": "action '...' requires: --year, --month. ...", "action":
"..."}` dict.

### Commits
- [x] Commit 1: `scripts/mops_client.py` — `_REQUIRED_PARAMS` table +
      `_validate_action_params()` helper called at top of `_run_action()`;
      updated `mops_fetch` docstring with explicit `[required, params]`
      notation per action.
- [x] Commit 2: `tests/test_mcp_equivalence_auto.py` — 6 parametrized
      negative-case regression tests.
- [x] Commit 3: plugin sync 1.16.1 → 1.16.2.

### Root cause

`mops_client.py` is the only dispatcher-pattern MCP client in the plugin (16
actions funneled through `_run_action` via `types.SimpleNamespace`). All
other clients (twse/edinet/sec_edgar/etc.) either register separate tools per
action (JSONSchema `required` enforces params) or raise `SystemExit`
per-branch before any None-on-format. mops lacked top-level validation.

### Deferred
- Split `mops_fetch` into 16 individual MCP tools (would eliminate the
  dispatcher vulnerability architecturally) — ~2.2K token overhead, rejected
  for budget reasons in v1.14.0 plan review. Revisit if Anthropic raises
  session token budget OR core/extras MCP split ships.

---

## v1.16.1 — Cowork sandbox retrospective + maintenance automation

**Scope**: v1.14.0 premise failure correction + CI automation to make
keeping MCP cheap.

### Retrospective (confirmed empirically 2026-04-19)

Plugin-installed stdio MCP servers run INSIDE the Claude Desktop
Cowork sandbox, subject to the same URL allowlist as plugin-subprocess
scripts. v1.14.0 shipped MCP infrastructure believing MCP spawned
outside the sandbox — this was wrong. Anthropic's own plugins
(knowledge-work-plugins, financial-services-plugins) exclusively use
remote `type: http` MCP for exactly this reason.

**Decision**: keep MCP infrastructure (works fine in Code CLI,
preserves optionality for future remote-MCP pivot, rollback cost >
keeping cost), correct all documentation, add CI automation to reduce
recurring maintenance cost.

### Commits
- [x] Commit 1: `docs/mcp-setup.md` — honest retrospective at top;
      "What actually works where" table; token/latency trade-off;
      opt-out guidance.
- [x] Commit 2: 9 SKILL.md blockquotes changed from "MCP-prefer" to
      neutral dual-mode + explicit Cowork caveat; per-skill tool
      enumeration moved to `docs/mcp-setup.md` (single authoritative
      catalog).
- [x] Commit 3: `tests/test_mcp_equivalence_auto.py` — parameterized
      MCP↔CLI drift guard; 14 fixtures covering all public-tier
      clients. Runtime ~6 s warm / 30 s cold.
- [x] Commit 4: `tests/test_skill_md_sync.py` (canonical-phrase check
      + stale-tool-ref check) + `tools/validate_mcp_tools.py`
      (schema + description linter, all 29 tools pass).
- [x] Commit 5: plugin.json / README / ROADMAP sync 1.16.0 → 1.16.1.

### Maintenance cost reduction (estimated)

Before: ~3.5-6.5 h / 6 months for MCP maintenance (drift checks,
SKILL.md sync, scaffolding). After: <1 h / 6 months. Break-even on
the ~1 day automation investment: ~2 months.

### Known open items (deferred to v1.16.x+)

- MCP equivalence coverage expansion (14 → 18+ fixtures):
  sec_edgar_facts, sec_edgar_narrative, finmind, boj_fetch (generic),
  ecb_series. All require either API keys or stable public fixtures.
- `tools/scaffold_mcp_tool.py` for new-script bootstrapping (deferred
  — save ~15 min per future script, current ROI uncertain).
- Nightly URL probe for setup.sh external deps (uv install URL,
  Homebrew formula) — current `Scraper dependency freshness` CI
  partially covers this already.

### Long-term: would need to pivot strategy for real Cowork support
- Anthropic allowlists our data-source URLs (no ETA).
- We host investing-toolkit as remote-HTTP MCP (requires $5-20/mo
  infra, privacy consideration, out of scope for solo OSS plugin).

---

## v1.16.0 — Complete MCP tool surface

**Scope**: Wrap the 8 remaining data-fetching scripts deferred from
v1.14.0 plan so Cowork users are not blocked on macro / regime work
(`/invest-macro`, `macro-regime-snapshot`, country-macro skills).

### Phase 1 — Macro register_mcp_tools (Commits 1-3)
- [x] `boj_client.py`: boj_fetch + boj_tankan_inflation_outlook
- [x] `ecb_client.py`: ecb_series
- [x] `estat_client.py`: estat_fetch + estat_search
- [x] `cbc_client.py`: cbc_fetch
- [x] `dgbas_client.py`: dgbas_fetch
- [x] `ndc_client.py`: ndc_fetch
- [x] `statgov_client.py`: statgov_fetch
- [x] `fdr_client.py`: fdr_fetch

### Phase 2 — Central registry + plugin sync (Commits 4-5)
- [x] `servers/mcp_server.py`: 10 → 18 clients, 19 → 29 tools
- [x] Contract tests: `tools=29`, expected names set extended
- [x] Plugin sync 1.15.0 → 1.16.0 (auto-invalidates .mcp_ready marker)

### Deliberately NOT wrapped
- `ta_client.py` — transforms local OHLCV into RSI/MACD/Bollinger/ATR/SMA;
  not a data fetcher. Compose via MCP `yfinance_history` →
  local subprocess `ta_client.py` if needed from Cowork.

### Deferred to v1.16.x+ (budget review trigger)
- Session token cost 4.4K now (29 × ~150 tok); v1.14.0 plan flagged
  5K as split threshold. Next additions (dcf-jp, korea-stock-snapshot,
  sector-etf) may push over → investigate core/extras MCP server split.

---

## v1.15.0 — Japan individual-stock skill

**Scope**: Path γ stacked-PR carry-over from v1.13.0 — Japan joins US + TW
as the third market with a dedicated individual-stock data skill. Primary-
source Tier A (EDINET + TDnet + yfinance .T) with dual-mode tier routing
(Tier A if EDINET_API_KEY set, Tier 2 yfinance financials fallback else).

### Phase 1 — Data adapters (Commits 1-3)
- [x] `scripts/edinet_client.py` — EDINET v2 REST API; 7 forms
      (120/140/160/180/220/350 + 訂正版); type=5 CSV parsed into
      canonical key_metrics; ticker→EDINET code via public ZIP; PDL 1.0
- [x] `scripts/tdnet_client.py` — Yanoshin WEB-API index wrapper;
      決算短信 / 業績予想 / 株主総会 / 役員 / 自己株 classifier
- [x] `scripts/yfinance_client.py --action financials` — Tier 2 BS/PL/CF
      fallback; data_tier provenance label; Toyota FY2025 equivalence
      check vs EDINET passes (revenue/operating/net/OCF match exactly)

### Phase 2 — Skill + orchestration (Commits 4-6)
- [x] `skills/japan-stock-snapshot/SKILL.md` — dual-mode routing;
      upgrade-path footer for Tier 2 users; known gaps documented
- [x] `sync-scripts.sh` wires edinet/tdnet/yfinance into
      japan-stock-snapshot + investment-memo-writer + dcf-valuation
- [x] `servers/mcp_server.py` registers 10 clients × 19 tools
      (+4 edinet, +1 tdnet, +1 yfinance_financials); contract tests
      updated + all 3 pass
- [x] `investment-memo-writer` Phase 1 JP branch routes 4-digit tickers
      through EDINET (Tier A) or yfinance financials (Tier 2) + TDnet
- [x] Plugin-level sync 1.14.0 → 1.15.0

### Known gaps deferred to v1.15.x
- **信用取引残高 / 空売り per-stock** — J-Quants Standard (paid) only
- **daily 投資部門別 per-stock flow** — genuinely unavailable free
  (JPX publishes weekly aggregate only)
- **EPS via EDINET** — alias coverage incomplete for IFRS
  KeyFinancialData namespace; yfinance `.T` info fills gap
- **Narrative Item extraction from EDINET iXBRL** — CSV is
  table-only; narrative 事業等のリスク / MD&A text lives in iXBRL 本文
- **pre-April-2024 historical filings** — type=5 CSV was added
  2024-04; older filings need iXBRL parser

### Deferred to v1.16.0+ candidates
- J-Quants free tier `/listed/info` for 33業種 (if we need JPX
  industry classification vs yfinance GICS sector)
- `dcf-valuation` JP branch (auto-source EDINET key_metrics)
- Korea individual-stock skill (KRX + DART)
- China individual-stock skill (SZSE + eastmoney)

---

## v1.14.0 — MCP migration infrastructure

**Scope**: Expose all 8 data-fetch scripts as 13 MCP tools, bundled at
plugin level. Unblocks Claude Desktop Cowork users (previously all
`uv run scripts/...` calls blocked by Cowork sandbox URL allowlist);
Claude Code CLI keeps working via the identical-JSON dual-mode path.

### Phase 1 — Per-script register_mcp_tools()
- [x] Commit 1: `yfinance_client.py` / `akshare_client.py` /
      `nbs_client.py` (3 HIGH-risk scripts confirmed failing in sandbox)
- [x] Commit 2: `fred_client.py` / `sec_edgar_client.py` /
      `mops_client.py` / `twse_openapi_client.py` / `finmind_client.py`
      (5 Pattern C scripts)
- [x] 13 tools total; dispatch pattern used for mops (16 actions) and
      twse (10 actions) to keep session token cost manageable.

### Phase 2 — servers/ central registry + entry chain
- [x] Commit 3: `servers/mcp_server.py` + `--self-check` flag for
      setup-time dep warming. Follows official plugins-reference layout
      convention (`servers/` not `scripts/`).
- [x] Commit 4: `.mcp.json` + `servers/mcp_bootstrap.sh` +
      `servers/mcp_wrapper.py` + `servers/setup.sh`. V2 silent-auto
      design (pre-flight P3 probe 2026-04-19 confirmed Claude Desktop
      MCP handshake timeout cliff = 60 s, so synchronous bootstrap
      would fail on first install; background setup + stdlib wrapper
      keeps handshake under the limit).

### Phase 3 — Documentation + tests
- [x] Commit 5: 8 SKILL.md files carry MCP-aware prose blockquote
      (prefer MCP tools if registered, subprocess commands remain
      canonical fallback).
- [x] Commit 6: `docs/mcp-setup.md` — 3 install paths (CLI / Cowork
      Team private fork / Cowork Pro/Max limited) + troubleshooting.
- [x] Commit 7: `tests/test_mcp_contract.py` — 3 contract tests
      (self-check shape, stdio handshake exposes 13 tools, FRED
      MCP=CLI equivalence).

### Deferred to v1.15.0+
- Japan individual stock skill (Path γ carry-over from v1.13.0 plan).
- Wrap remaining 9 macro / reference scripts (boj / ecb / estat /
  cbc / dgbas / ndc / statgov / fdr / ta) as MCP demand surfaces.
- `.mcpb` Desktop Extension packaging (Chat-tab users only, niche).
- Remote HTTP MCP hosting (privacy + cost concerns).

---

## v1.13.0 — Individual stock fundamentals (US + TW)

**Scope**: Closes Pattern C NVDA demo 4 data gaps for US + TW markets.
Primary-source Tier A across all new fetchers.

### Phase 1 — SEC EDGAR (US)
- [x] `scripts/sec_edgar_client.py` (7 form types, XBRL + narrative)
- [x] `us-stock-snapshot` SKILL.md integration
- [x] `references/sec-edgar-guide.md` (new reference doc)

### Phase 2 — MOPS (TW 公司揭露)
- [x] `scripts/mops_client.py` (16 endpoints)
- [x] MOPS JSON API confirmed via 2-round probe (zero-auth, no cookie)
- [x] Historical depth: IFRS 財報 ROC 102-115 (13 yr); 重大訊息 ROC 85+ (30 yr)

### Phase 3 — TWSE OpenAPI (TW 交易)
- [x] `scripts/twse_openapi_client.py` (日行情 / 融資融券 / 三大法人
      snapshot / 產業 EPS / 除權息日曆)
- [x] TPEx bonus endpoint added (tpex-margin-balance)
- [x] Known gaps documented (daily T86 per-stock flow not in OpenAPI)

### Phase 4 — taiwan-stock-snapshot rebuild
- [x] SKILL.md rewrite: MOPS + TWSE OpenAPI Tier 1 primary; FinMind
      Tier 2 auto-fallback (Pattern A+B combo)
- [x] `references/data-sources.md` new reference doc (10 sections)

### Phase 5 — DCF + memo-writer integration
- [x] `dcf-valuation` SKILL.md — financial statements now available
- [x] `investment-memo-writer` Phase 1 — SEC EDGAR + MOPS + TWSE OpenAPI
      commands added

### Phase 6 — Plugin-level sync
- [x] plugin.json 1.12.0 → 1.13.0
- [x] README v1.13.0 Version Highlights prepended
- [x] ROADMAP this entry; v1.12.0 de-marked as (current)

### Deferred to v1.14.0+ candidates

- **v1.14.0 (stacked)**: `japan-stock-snapshot` skill (yfinance .T +
  evaluate EDINET XBRL for primary-source-grade)
- **v1.13.x patches**: analyst consensus (finnhub / alphavantage),
  market-wide MOPS t146sb10 broader coverage
- **v1.15.0+**: `korea-stock-snapshot` (FDR + DART), `china-stock-snapshot`
  (akshare extended)
- **軸 3 phase-split** (from v1.12.0 Pattern C UX) — if 軸 1+2 proves
  insufficient in practice
- **Full 5-parallel grounding re-audit** (~2026-Q3)

---

## v1.12.0 — Pattern C UX (file-write + visibility)

**Scope**: Fixes 3 UX issues exposed by v1.11.0 NVDA Pattern C demo:
(1) no file-write default (2500-word memo lived only in chat
transcript); (2) skill drift — investing-team reference should route
to research-team; (3) ~2 min agent silence during Phase 3 dispatch.

Cross-plugin: investing-toolkit (1.11.0 → 1.12.0) + domain-teams
(5.1.0 → 5.2.0).

### Phase 1 — investment-memo-writer file-write + narration + target fix
- [x] Phase 5 rewrite — default path
  `$CLAUDE_PLUGIN_DATA/memos/{YYYY-MM-DD}_{ticker}_{mode}_memo.md`
  (deep vs quick mode-separated filenames; overwrite on same-mode
  re-run); Obsidian mode auto-detect (env var → vault probe → vault
  CLAUDE.md folder convention → obsidian:obsidian-markdown skill)
- [x] Chat delivery — executive summary + gate verdicts + file link
  only; full memo stays in file (not repeated in chat)
- [x] Phase 3 target fix — `domain-teams:investing-team` →
  `domain-teams:research-team` (historical note preserved)
- [x] Narration Convention (軸 1) — pre-dispatch expectation-setting
  pattern documented

### Phase 2 — domain-teams Visibility Convention (v5.2.0)
- [x] `skill-team/SKILL.md` — new §Visibility Convention requiring
  `TaskUpdate` emission at 3 levels: phase transitions, milestones,
  heartbeat (≤60s max silence)
- [x] 7 workflow skills gain compliance block: research-team /
  code-team / design-team / docs-team / devops-team / qa-team /
  planning-team
- [x] Probabilistic vs structural guarantee trade-off documented;
  phase-split architecture (軸 3) deferred to v5.3.0+

### Phase 3 — Plugin-level sync
- [x] `investing-toolkit/.claude-plugin/plugin.json` — 1.11.0 → 1.12.0
- [x] `domain-teams/.claude-plugin/plugin.json` — 5.1.0 → 5.2.0
- [x] `investing-toolkit/README.md` — v1.12.0 Version Highlights
  prepended
- [x] `ROADMAP.md` — this v1.12.0 entry; v1.11.0 de-marked as (current)

### Deferred to v1.13.0+ candidates

- **軸 3 phase-split orchestration** — if 軸 1+2 prove insufficient
  in practice (structural guarantee for 60s max silence at cost of
  context-fragmentation between dispatches)
- **File-write convention extension** — apply file-persistence pattern
  to `stock-screener`, `dcf-valuation`, `invest-portfolio` outputs
- **Sector ETF cross-plugin workflow** — needs japan / korea /
  china stock-snapshot skills first (per v1.11.0 sector ETF audit)
- **KR KTBi via BOK ECOS API key** — carried from v1.9.0+ deferred
- **Full 5-parallel grounding re-audit** — target ~2026-Q3
- **JGBi YTM solver** — REJECTED per v1.11.0 brainstorm (architectural
  consistency; would make JP the only bond-math country among 5
  country-macro skills)

---

## v1.11.0 — Cross-country consistency refresh

**Scope**: Addresses v1.10.0 PMI asymmetry (1 / 5 countries live) +
grounding vintage drift (v1.9.0 baseline 2026-04-18 needed 2026-Q2
refresh for CN Work Report + BOJ 2026-01/03 holds). Closes Block 1
PMI row gap for CN + TW via free-tier sources; formalises JP + KR
URL-only status (both S&P Global licensed, no free path).

### Phase 1 — china-macro `pmi` group (Caixin + NBS)
- [x] `scripts/akshare_client.py` — `caixin-mfg-pmi` + `caixin-svc-pmi`
  via `index_pmi_man_cx` / `index_pmi_ser_cx` (eastmoney-backed; fresh
  endpoint distinct from 2026-04-18 excluded investing.com route)
- [x] `china-macro` new `pmi` group: 5 presets (2 Caixin via akshare +
  3 NBS `pmi-manufacturing` / `pmi-non-manufacturing` / `pmi-composite`
  via existing nbs_client, regrouped from legacy `sentiment`)
- [x] `references/indicators-pmi.md` — NBS ≥3000 incl. SOE vs Caixin ~430
  SME/民企 methodology contrast + 1-2mo Caixin-leads-NBS lag around
  turning points + 2015/2020-02/2022-04/2024-25 regime-shift sampling
- [x] Indicator count 34 → 36; akshare preset count 6 → 8

### Phase 2 — APAC PMI probes (TW live; JP/KR URL-only)
- [x] `taiwan-macro` new `pmi` group — `pmi-mfg` + `pmi-nmi` via
  `ndc_client.py` dedicated CSV endpoint (NDC 政府資料開放平臺 dataset
  6100, 政府資料開放授權條款第1版 CC BY-equivalent). Indicator count
  30 → 32. New `references/indicators-pmi.md`.
- [x] `japan-macro` — "PMI (URL reference only)" subsection added
  linking to S&P Global press releases; BOJ Tankan 業況判断DI noted
  as closest free sentiment proxy
- [x] `korea-macro` — "PMI (URL reference only)" subsection added
  linking to S&P Global Korea press release; CSI (K252) + ESI (K269)
  + business-cycle CI (K253/K254) noted as closest free proxies

### Phase 3 — CN + JP full grounding refresh (2026-Q2 vintage)
- [x] `thresholds-china.md` — 2026 Work Report GDP 4.5-5% range;
  LPR-1Y/5Y vintage refresh; 16 🔴 + 9 ⚠️ CN+JP corrections
- [x] `thresholds-japan.md` — BOJ held 0.75% 2026-01 + 2026-03;
  JILPT NAIRU refresh; Tankan 2026-Q1 vintage

### Phase 4 — US + TW + KR grounding delta addenda
- [x] `thresholds-us.md` — FOMC SEP long-run real r* 3.0 → 3.1%
- [x] `thresholds-taiwan.md` — CBC held 2.00% 2026-Q1
- [x] `thresholds-korea.md` — BOK 7-consecutive hold confirmation
- [x] 2 🔴 + 8 ⚠️ delta corrections across US/TW/KR

### Phase 5 — Consolidated audit trail
- [x] `skills/macro-regime-snapshot/research/grounding-v1.11.0.md`
  — 299-line consolidated audit trail covering all 5 countries
  (full CN + JP re-audit + US/TW/KR delta); 16 🔴 + 17 ⚠️ total

### Phase 6 — Plugin-level integration + sync
- [x] `skills/macro-regime-snapshot/SKILL.md` — Block 1 PMI row CN + TW
  promoted from N/A → live (citing preset names); Data Source
  Architecture section expanded with 5×9 cross-country coverage grid
  (Growth / Inflation / Policy rate / Yield curve / Real rate / PMI /
  Swap spread / FX / Equity). Consolidated into existing section per
  spec §3.6 Option X (replaces standalone coverage-matrix.md)
- [x] `skills/using-investing-toolkit/SKILL.md` — china-macro /
  taiwan-macro / macro-regime-snapshot rows bumped to v1.11.0
- [x] `README.md` — v1.11.0 Version Highlights prepended; Skills
  table updates
- [x] `ROADMAP.md` — this v1.11.0 entry
- [x] `.claude-plugin/plugin.json` — 1.10.0 → 1.11.0

### Deferred to v1.12.0+ candidates (carried forward)

- **KR KTBi real-rate via BOK ECOS API key** — free registration at
  ecos.bok.or.kr/api/#/AuthKeyApply; unlocks lagging CI 후행지수 +
  10K series concurrently (unchanged from v1.11.0 deferred)
- **JP au Jibun Bank / KR S&P Global Korea PMI licensed access** —
  both S&P Global licensed; no free-tier machine-readable path
  available; formalised as URL-only in v1.11.0
- **Full 5-parallel grounding re-audit (target ~2026-Q3)** — next
  full sweep on the cadence documented in `references/recalibration-
  protocol.md`
- **ISM PMI via FRED NAPM** — still blocked by 2016 FRED delisting;
  awaits hypothetical relicensing

### REJECTED — architecturally inconsistent

- **Full MoF 連動係数 + QuantLib CPIBond YTM solver for daily JGBi
  real yield** — originally deferred from v1.10.0 to v1.11.0 as "next
  major candidate". **Rejected during v1.11.0 brainstorming audit**:
  would make `japan-macro` the only bond-math country among the 5
  country-macro skills (US/JP/TW/KR/CN), violating the explicit
  "country-macro = pure data layer" discipline documented in
  `CLAUDE.md` Cross-Plugin Delegation Contract §3
  ("Data layer stays in toolkit, analysis layer stays in domain-teams").
  Bond-math solvers (YTM, duration-adjusted real-yield inversion) are
  an analysis-layer concern and belong in `domain-teams:investing-team`
  if pursued. v1.10.0 C+D+E multi-source anchor (ECB monthly ex-post +
  BOJ Tankan + MoF JGBi auction) is the permanent JP real-rate shape.
  Preserved here as a historical roadmap entry so the decision is
  discoverable.

---

## v2.0.0 — Quantitative Layer (tentative)

**Scope**: Backtesting integration, factor models.

### Ideas
- [ ] Backtesting workflow (integrates with domain-teams:investing-team standards/backtesting-and-robustness-discipline.md)
- [ ] Factor exposure snapshot (Fama-French 5-factor)
- [ ] Alpha Vantage premium adapter (technical indicators)
- [ ] Portfolio optimizer (risk parity / Kelly allocation)
