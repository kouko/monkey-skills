# Plan: investing-toolkit data-layer consolidation + cache subsystem redesign

Source brief: docs/loom/specs/2026-07-11-investing-toolkit-data-consolidation.md
Change-folder input: N/A — no non-archived `docs/loom/<change-id>/` change-folder exists (stated loudly per §Consuming a loom-spec change-folder layer ii = 0); brief is the sole input.
Total tasks: 12
Critical-path depth: 5 (T1 → T2 → T3x → T4 → T5x)
Execution order: parallel-where-possible
Plan-document-reviewer verdict: PASS (round 2, 14/14 checks, 2026-07-11)

## Notes

- All new tests live under `investing-toolkit/tests/data/` (existing pytest
  root + `tests/data/` convention; CI pytest path override gotcha noted —
  tests run via the repo's existing package-level invocation, no new
  command-surface verb is introduced).
- Payload shapes are preserved verbatim (brief: shape unification OUT of
  scope). Fixture-based chain tests therefore stay valid.
- Exit-code recon (brief Open Q3): the only `returncode == 2` assertions in
  the repo are analysis-layer arg-validation tests
  (tests/analysis/test_analysis_comps.py:503,
  tests/analysis/test_comps_sector_compute.py:473) — analysis scripts are
  untouched by this arc; renumbering DATA-layer arg errors to 64 is safe.
- Old-folder fate (brief Open Q2): delete outright in T5c (proposed default,
  user did not object at sign-off).
- Whole-suite green is asserted at branch close by
  verification-before-completion, not by any single task; T5c's acceptance
  is targeted to the files it touches to keep level-5 tasks independent.
- T5b/T5c file sets are disjoint and each task's acceptance is
  self-contained; the transient "downstream docs updated but old dirs still
  present" (or inverse) intermediate state is branch-internal only.
- Amendment (post-PASS, 2026-07-11): per-task `Status` progress-ledger fields
  added at SDD start — additive runtime state per plan-format §Progress
  ledger; plan-document-reviewer re-run skipped (reviewer rule 6 explicitly
  accepts-and-ignores Status fields; schema unchanged).
- Resolved test command (session-cached, verified 424 passed/13s):
  `PYTHONDONTWRITEBYTECODE=1 uv run --quiet --with pytest --with 'pyyaml>=6.0' pytest investing-toolkit/tests/ -m "not network" -q --tb=short`

## Task 1 — cache_util: validated path resolution

- Description: Create `cache_util.py` with `resolve_cache_dir()` implementing
  the XDG/uv precedence ladder — explicit arg (CLI flag passthrough) >
  `INVESTING_TOOLKIT_CACHE` (stripped; empty string ⇒ ignored) >
  `$XDG_CACHE_HOME/investing-toolkit` > `~/.cache/investing-toolkit` — with
  post-resolution writability check: unwritable resolved dir ⇒ loud stderr
  warning + fallback to `tempfile.gettempdir()/investing-toolkit`. Contract:
  the returned directory is always writable.
- Module: investing-toolkit/skills/data-markets/scripts/cache_util.py (new)
- Files touched: investing-toolkit/skills/data-markets/scripts/cache_util.py,
  investing-toolkit/tests/data/test_cache_util.py
- Context paths:
  - investing-toolkit/skills/data-us/scripts/yfinance_client.py (lines 32-33, 90-110 — current resolution + helpers being replaced)
  - docs/loom/specs/2026-07-11-investing-toolkit-data-consolidation.md (§Smallest End State item 3)
- Acceptance:
  - RED: tests/data/test_cache_util.py::test_resolve_cache_dir_always_returns_writable_dir fails (module does not exist). Parametrized cases: precedence order incl. XDG layer; `INVESTING_TOOLKIT_CACHE=""` and `="/cache"` (the live-reproduced bug) both resolve to a writable dir with a warning on stderr for the unwritable case.
  - GREEN: test passes; `resolve_cache_dir(explicit="/cache")` emits stderr warning and returns writable tempdir path.
- External surfaces: none (stdlib only — platformdirs deliberately NOT adopted per brief §Alternatives 4)
- Dependencies: none
- Independent: false
- Status: done(91d80a8f)
- Brief item covered: "Single cache_util.py … XDG-compliant uv-style path precedence … empty-string-safe env parsing … writability check with loud stderr warning + tempdir fallback"; also SES item 6 "new tests for the /cache regression … empty-env-var parsing" (Decision: "regression tests for the live-reproduced bug")

## Task 2 — cache_util: cadence-aware TTL + roundtrip helpers

- Description: Add to `cache_util.py`: `compute_ttl(cadence, staleness_days)`
  (generalizing data-tw/dgbas_client.py's cadence bands per
  docs/cache-policy.md), `cache_path(source, key)`, `load_cache(path, ttl)`
  (fail-open: corrupt/expired ⇒ None), `save_cache(path, data)` (write
  failure ⇒ loud stderr warning, non-fatal — never silent `pass`), and
  `CACHE_SCHEMA_VERSION`. XDG disposability: deleting the cache dir mid-run
  only slows the next call.
- Module: investing-toolkit/skills/data-markets/scripts/cache_util.py
- Files touched: investing-toolkit/skills/data-markets/scripts/cache_util.py,
  investing-toolkit/tests/data/test_cache_util.py
- Context paths:
  - investing-toolkit/skills/data-tw/scripts/dgbas_client.py (the only cadence-aware implementation — `_compute_ttl`, cadence bands)
  - investing-toolkit/docs/cache-policy.md (declared TTL bands)
- Acceptance:
  - RED: tests/data/test_cache_util.py::test_ttl_and_roundtrip_contract fails (functions undefined). Covers: cadence→TTL mapping matches cache-policy.md bands; save→load roundtrip; expired entry ⇒ None; unwritable save path ⇒ stderr warning present, no exception.
  - GREEN: test passes.
- External surfaces: none (stdlib only)
- Dependencies: Task 1 completes first
- Independent: false
- Status: done(5d3d18d1)
- Brief item covered: "cadence-aware TTL API (generalizing dgbas's _compute_ttl), schema version … XDG disposability semantics"

## Task 3a — migrate US clients + pack module

- Description: Move data-us clients into data-markets: `yfinance_client.py`
  (becomes the single canonical copy), `fred_client.py` (single copy),
  `sec_edgar_client.py` (mtime TTL replaced by cache_util), plus
  `pack_us.py` (from data-us/pack.py pack-building logic, minus CLI shell).
  Replace every local cache block with `import cache_util`. Payload shapes
  unchanged.
- Module: investing-toolkit/skills/data-markets/scripts/
- Files touched: investing-toolkit/skills/data-markets/scripts/yfinance_client.py,
  investing-toolkit/skills/data-markets/scripts/fred_client.py,
  investing-toolkit/skills/data-markets/scripts/sec_edgar_client.py,
  investing-toolkit/skills/data-markets/scripts/pack_us.py,
  investing-toolkit/tests/data/test_data_markets_us.py
- Context paths:
  - investing-toolkit/skills/data-us/scripts/ (all 4 scripts)
  - investing-toolkit/tests/data/fixtures/ (data-us-*.json samples)
- Acceptance:
  - RED: tests/data/test_data_markets_us.py::test_us_migration_contract fails (files absent). Asserts: no `_CACHE_BASE`/local cache-helper definitions in migrated files (AST/grep check); `pack_us` builds snapshot/memo-fetch section keys identical to the data-us fixture sample (offline, fixture-fed).
  - GREEN: test passes.
- External surfaces: yfinance (unofficial Yahoo scraper), FRED API, SEC EDGAR — tests are offline/fixture-based per existing repo convention; no live calls in CI.
- Dependencies: Task 2 completes first
- Independent: true
- Status: done(57e22901)
- Brief item covered: "Deduplicated scripts/: 18 unique clients (yfinance ×5 → 1, fred ×2 → 1)"

## Task 3b — migrate JP clients + pack module

- Description: Move data-jp clients (boj, ecb, edinet, estat, tdnet — NOT
  yfinance, canonical copy comes from T3a) into data-markets as
  `pack_jp.py` + clients; underscore-dialect cache helpers (`_load_cache`)
  and import-time mkdir in edinet/tdnet replaced by cache_util (lazy).
  Tier-1 placeholder status preserved as-is.
- Module: investing-toolkit/skills/data-markets/scripts/
- Files touched: investing-toolkit/skills/data-markets/scripts/boj_client.py,
  investing-toolkit/skills/data-markets/scripts/ecb_client.py,
  investing-toolkit/skills/data-markets/scripts/edinet_client.py,
  investing-toolkit/skills/data-markets/scripts/estat_client.py,
  investing-toolkit/skills/data-markets/scripts/tdnet_client.py,
  investing-toolkit/skills/data-markets/scripts/pack_jp.py,
  investing-toolkit/tests/data/test_data_markets_jp.py
- Context paths:
  - investing-toolkit/skills/data-jp/scripts/ (all 7 scripts)
  - investing-toolkit/tests/data/fixtures/ (data-jp samples if present)
- Acceptance:
  - RED: tests/data/test_data_markets_jp.py::test_jp_migration_contract fails (files absent). Asserts: no local cache helpers (incl. underscore dialect), no import-time mkdir; pack_jp section keys match current data-jp output shape (fixture-fed).
  - GREEN: test passes.
- External surfaces: EDINET API (key-gated), TDnet via Yanoshin aggregator, BOJ/e-Stat/ECB — offline fixture tests only.
- Dependencies: Task 2 completes first
- Independent: true
- Status: done(3ef8cbfe)
- Brief item covered: "Deduplicated scripts/ … per-market pack modules"

## Task 3c — migrate TW clients + pack module

- Description: Move data-tw clients (cbc, dgbas, finmind, mops, ndc,
  statgov, twse_openapi — NOT yfinance) into data-markets as `pack_tw.py` +
  clients; dgbas's local cadence machinery replaced by cache_util's (T2
  generalized it); `verify=False` SSL flags preserved as-is (out of scope,
  documented in reference file at T5a).
- Module: investing-toolkit/skills/data-markets/scripts/
- Files touched: investing-toolkit/skills/data-markets/scripts/cbc_client.py,
  investing-toolkit/skills/data-markets/scripts/dgbas_client.py,
  investing-toolkit/skills/data-markets/scripts/finmind_client.py,
  investing-toolkit/skills/data-markets/scripts/mops_client.py,
  investing-toolkit/skills/data-markets/scripts/ndc_client.py,
  investing-toolkit/skills/data-markets/scripts/statgov_client.py,
  investing-toolkit/skills/data-markets/scripts/twse_openapi_client.py,
  investing-toolkit/skills/data-markets/scripts/pack_tw.py,
  investing-toolkit/tests/data/test_data_markets_tw.py
- Context paths:
  - investing-toolkit/skills/data-tw/scripts/ (all 9 scripts)
- Acceptance:
  - RED: tests/data/test_data_markets_tw.py::test_tw_migration_contract fails (files absent). Asserts: no local cache helpers; `_tier`/`_partial` output semantics preserved (fixture-fed shape check).
  - GREEN: test passes.
- External surfaces: TWSE OpenAPI, FinMind (anon rate-limited), MOPS/DGBAS/CBC/NDC/stat.gov scrapers — offline fixture tests only.
- Dependencies: Task 2 completes first
- Independent: true
- Status: done(cff427ed)
- Brief item covered: "Deduplicated scripts/ … per-market pack modules"

## Task 3d — migrate KR clients + pack module

- Description: Move data-kr clients (fdr — NOT yfinance) into data-markets
  as `pack_kr.py` + client; preserve `_provenance.primary_source_status` and
  the existing `sys.exit(1)-on-_partial` semantic (it becomes exit 2 under
  T4's contract — pack_kr itself stays exit-code-agnostic, returns section
  dict).
- Module: investing-toolkit/skills/data-markets/scripts/
- Files touched: investing-toolkit/skills/data-markets/scripts/fdr_client.py,
  investing-toolkit/skills/data-markets/scripts/pack_kr.py,
  investing-toolkit/tests/data/test_data_markets_kr.py
- Context paths:
  - investing-toolkit/skills/data-kr/scripts/ (all 3 scripts)
- Acceptance:
  - RED: tests/data/test_data_markets_kr.py::test_kr_migration_contract fails (files absent). Asserts: no local cache helpers; `_provenance` fields preserved (fixture-fed).
  - GREEN: test passes.
- External surfaces: FinanceDataReader / BOK ECOS undocumented endpoint — offline fixture tests only.
- Dependencies: Task 2 completes first
- Independent: true
- Status: done(4e8c0c05)
- Brief item covered: "Deduplicated scripts/ … per-market pack modules"

## Task 3e — migrate CN clients + pack module

- Description: Move data-cn clients (akshare, nbs — NOT yfinance, NOT fred:
  canonical copies from T3a) into data-markets as `pack_cn.py` + clients.
- Module: investing-toolkit/skills/data-markets/scripts/
- Files touched: investing-toolkit/skills/data-markets/scripts/akshare_client.py,
  investing-toolkit/skills/data-markets/scripts/nbs_client.py,
  investing-toolkit/skills/data-markets/scripts/pack_cn.py,
  investing-toolkit/tests/data/test_data_markets_cn.py
- Context paths:
  - investing-toolkit/skills/data-cn/scripts/ (all 5 scripts)
- Acceptance:
  - RED: tests/data/test_data_markets_cn.py::test_cn_migration_contract fails (files absent). Asserts: no local cache helpers; no local fred/yfinance copy present in CN set; pack_cn section keys match current shape (fixture-fed).
  - GREEN: test passes.
- External surfaces: akshare (eastmoney mirror), NBS — offline fixture tests only.
- Dependencies: Task 2 completes first
- Independent: true
- Status: done(c8b38f01)
- Brief item covered: "Deduplicated scripts/ … (fred ×2 → 1)"

## Task 4 — unified pack.py facade: market auto-detection + fail-loud exit contract

- Description: Create `pack.py` single entry: detect market from ticker
  suffix (`.TW/.TWO`→tw, `.KS/.KQ`→kr, `.SS/.SZ/.HK`→cn, `.T` or bare
  4-digit→jp, else us), `--market` explicit override (required for
  `--pack regime-pack`); dispatch to `pack_{market}`; assemble top-level
  `_status` block (`ok|partial|failed`, `failed_sections[]`, per-slot full
  traceback text); exit contract 0=all sections ok / 1=all failed /
  2=partial / 64=argument error. Migrate any data-skill path references in
  existing integration/structural tests to the new layout so the 59 chain
  tests stay green.
- Module: investing-toolkit/skills/data-markets/scripts/pack.py (new)
- Files touched: investing-toolkit/skills/data-markets/scripts/pack.py,
  investing-toolkit/tests/data/test_pack_facade.py,
  investing-toolkit/tests/integration/test_cross_layer_chains.py (path refs only)
- Context paths:
  - investing-toolkit/skills/data-us/scripts/pack.py (current CLI shell + error-slot construction, lines 198-213, 784-814)
  - investing-toolkit/skills/data-kr/scripts/pack.py (lines 681-682 — the only existing failure-propagating exit)
  - docs/loom/specs/2026-07-11-investing-toolkit-data-consolidation.md (§Smallest End State items 2, 4)
- Acceptance:
  - RED: tests/data/test_pack_facade.py::test_autodetect_and_exit_contract fails (pack.py absent). Parametrized: suffix→market table; regime-pack without --market ⇒ exit 64; all-clients-fail (simulated via unwritable-cache monkeypatch of subprocess env, the live-reproduced scenario) ⇒ exit 1 + `_status.failed` + traceback text in slots; one-section-fail ⇒ exit 2 + `_status.partial`.
  - GREEN: test passes AND `pytest investing-toolkit/tests/integration/test_cross_layer_chains.py` remains 59/59.
- External surfaces: none new (facade is stdlib; clients' surfaces unchanged)
- Dependencies: Tasks 3a, 3b, 3c, 3d, 3e complete first
- Independent: false
- Status: done(819cefc0)
- Brief item covered: "unified pack.py entry with market auto-detection … Fail-loud exit contract: 0/1/2, arg errors 64, top-level _status block, error slots carry full traceback"; also SES item 6 "existing 59 cross-layer chain tests keep passing … new tests for the … exit-code contract … market auto-detection"

## Task 5a — data-markets SKILL.md + per-market references

- Description: Write skills/data-markets/SKILL.md (thin: shared contract —
  cache path ladder, exit codes, `_status`, 5 pack worked examples with NO
  `${CLAUDE_PLUGIN_DATA}` anywhere, ticker-suffix routing table, per-market
  key summary, reference pointers) + `references/market-{us,jp,tw,kr,cn}.md`
  (sources, tiers incl. honest Tier-3 placeholder status, keys, caveats
  incl. TW `verify=False` note, rate limits).
- Module: investing-toolkit/skills/data-markets/
- Files touched: investing-toolkit/skills/data-markets/SKILL.md,
  investing-toolkit/skills/data-markets/references/market-us.md,
  investing-toolkit/skills/data-markets/references/market-jp.md,
  investing-toolkit/skills/data-markets/references/market-tw.md,
  investing-toolkit/skills/data-markets/references/market-kr.md,
  investing-toolkit/skills/data-markets/references/market-cn.md
- Context paths:
  - investing-toolkit/skills/data-{us,jp,tw,kr,cn}/SKILL.md (content being distilled)
  - CLAUDE.md (§Skill Structure — flat-folder + token cap rules)
- Acceptance:
  - RED (diagnostic): skills/data-markets/SKILL.md does not exist; token-count check has no target.
  - GREEN: SKILL.md body <5,000 tokens (measured, stated in task report — acceptance criterion from brief sign-off; repo cap 6k); `.claude/hooks/validate-skill-folder-structure.sh` passes; zero `${CLAUDE_PLUGIN_DATA}` occurrences under skills/data-markets/; all 5 reference files exist and are pointed to from SKILL.md.
- External surfaces: none (docs)
- Dependencies: Task 4 completes first
- Independent: true
- Status: done(6722bc38)
- Brief item covered: "Thin SKILL.md … + references/market-{us,jp,tw,cn,kr}.md carrying per-market detail; ${CLAUDE_PLUGIN_DATA} removed from all examples"

## Task 5b — downstream reference migration

- Description: Update every consumer to the merged skill: 8 SKILL.mds
  (analysis-comps, analysis-dcf, analysis-macro-regime, report-equity-memo,
  report-portfolio-review, report-stock-snapshot, report-screener-list,
  using-investing-toolkit router — router table gains data-markets row and
  the previously-omitted analysis-comps row), README.md + README.ja.md
  (22 `data-` references), all invocation examples to
  `data-markets/scripts/pack.py` form without `${CLAUDE_PLUGIN_DATA}`.
- Module: investing-toolkit/skills/
- Files touched: investing-toolkit/skills/analysis-comps/SKILL.md,
  investing-toolkit/skills/analysis-dcf/SKILL.md,
  investing-toolkit/skills/analysis-macro-regime/SKILL.md,
  investing-toolkit/skills/report-equity-memo/SKILL.md,
  investing-toolkit/skills/report-portfolio-review/SKILL.md,
  investing-toolkit/skills/report-stock-snapshot/SKILL.md,
  investing-toolkit/skills/report-screener-list/SKILL.md,
  investing-toolkit/skills/using-investing-toolkit/SKILL.md,
  investing-toolkit/README.md, investing-toolkit/README.ja.md
- Context paths:
  - investing-toolkit/skills/using-investing-toolkit/SKILL.md (current router table + intent routing, lines 26-40, 81-89)
- Acceptance:
  - RED (diagnostic): `grep -rn "data-\(us\|jp\|tw\|kr\|cn\)" investing-toolkit/skills/*/SKILL.md investing-toolkit/README*.md` returns hits.
  - GREEN: same grep returns zero hits (docs/adr/ and CHANGELOG.md exempt — historical record); router lists data-markets + all 6 analysis skills incl. analysis-comps.
- External surfaces: none (docs)
- Dependencies: Task 4 completes first
- Independent: true
- Status: done(fa65ef52+9a5fe56f)
- Brief item covered: "Downstream references updated: 8 SKILL.mds + README(s) + using-investing-toolkit router … Router analysis-comps omission naturally fixed"

## Task 5c — delete old skills + sync machinery + structural-test updates

- Description: Delete skills/data-{us,jp,tw,cn,kr}/ (5 dirs),
  scripts/sync-clients.sh, tests/test_sync_clients.py; update
  tests/test_skill_structure.py / tests/test_path_conventions.py /
  tests/test_plugin_metadata.py expectations to the merged layout; fix
  docs/cache-policy.md:265 phantom `check-script-sync.yml` claim.
- Module: investing-toolkit/tests/
- Files touched: investing-toolkit/skills/data-us/ (delete),
  investing-toolkit/skills/data-jp/ (delete),
  investing-toolkit/skills/data-tw/ (delete),
  investing-toolkit/skills/data-kr/ (delete),
  investing-toolkit/skills/data-cn/ (delete),
  investing-toolkit/scripts/sync-clients.sh (delete),
  investing-toolkit/tests/test_sync_clients.py (delete),
  investing-toolkit/tests/test_skill_structure.py,
  investing-toolkit/tests/test_path_conventions.py,
  investing-toolkit/tests/test_plugin_metadata.py,
  investing-toolkit/docs/cache-policy.md
- Context paths:
  - investing-toolkit/tests/test_skill_structure.py (current expectations)
- Acceptance:
  - RED (diagnostic): `ls investing-toolkit/skills/ | grep "data-us"` succeeds; tests/test_sync_clients.py exists.
  - GREEN: old dirs + sync script + sync test gone; `pytest investing-toolkit/tests/test_skill_structure.py investing-toolkit/tests/test_path_conventions.py investing-toolkit/tests/test_plugin_metadata.py` passes against merged layout; cache-policy.md cites no nonexistent CI file.
- External surfaces: none
- Dependencies: Task 4 completes first
- Independent: true
- Status: done(0469e21e+8c840a57+9b943e57+37cd9b78)
- Brief item covered: brief §What Becomes Obsolete "scripts/sync-clients.sh + all MD5-sync discipline; 4 copies of yfinance_client + 1 fred; stale check-script-sync.yml claims" (Decision: obsolete items are deleted in the same arc)

## Task 5d — data-fetcher agent rewrite + ADR + version bump

- Description: Rewrite agents/data-fetcher.md against the merged skill
  (pack.py facade, cache_util ladder, exit contract — replacing v1.x flat
  TTLs and pre-v2.0.0 script refs); write
  docs/adr/0009-data-markets-consolidation-and-cache-util.md (records the
  merge decision, supersedes ADR-0007's block-level-guard design, cites the
  live-reproduced /cache bug); update CHANGELOG.md + bump
  .claude-plugin/plugin.json version (marketplace description sync per repo
  gotcha if description changes).
- Module: investing-toolkit/docs/
- Files touched: investing-toolkit/agents/data-fetcher.md,
  investing-toolkit/docs/adr/0009-data-markets-consolidation-and-cache-util.md,
  investing-toolkit/CHANGELOG.md,
  investing-toolkit/.claude-plugin/plugin.json
- Context paths:
  - investing-toolkit/agents/data-fetcher.md (current stale content)
  - investing-toolkit/docs/adr/0007-skill-self-contained-cache-helpers.md (being superseded)
  - CLAUDE.md (§Cross-Plugin Delegation Contract — data-fetcher's contractual role)
- Acceptance:
  - RED (diagnostic): agents/data-fetcher.md still references `finmind_client.py` direct calls + flat "1h"/"6h"/"24h" TTLs; docs/adr/0009-*.md absent.
  - GREEN: data-fetcher.md references only merged-skill entry points; ADR-0009 exists with a "Supersedes: ADR-0007 §block-level guard" line; plugin.json version bumped; CHANGELOG entry present.
- External surfaces: none (docs/metadata)
- Dependencies: Task 4 completes first
- Independent: true
- Status: done(e556a463)
- Brief item covered: "agents/data-fetcher.md rewritten to the merged skill; ADR recording this decision and superseding ADR-0007's block-level-guard design"
