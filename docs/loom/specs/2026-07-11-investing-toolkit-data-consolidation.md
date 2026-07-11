# Brief: investing-toolkit data-layer consolidation + cache subsystem redesign

Date: 2026-07-11
Branch: `finacial-analytics-r2`
Status: draft — awaiting user sign-off before writing-plans

## Design-side on-ramp

Axis 0 negative guard applies (architecture-shifting refactor of an existing
internal toolkit, not product-shaped user-facing new work) — on-ramp table
skipped silently. `loom-memory` recall ran earlier this session: no
investing-related entries in `docs/loom/memory/` (honest no-hit).

## Problem

When kouko asks for an investment report (equity memo, portfolio review,
screener, snapshot), the report pipeline's data layer must deliver correct
market data fast — and when it can't, it must fail loudly enough that the
orchestrating agent (and the user) see WHY instead of receiving
well-formed-but-semantically-empty JSON.

Today it violates that job in two ways, both live-reproduced this session:

1. **Silent empty-shell failure**: SKILL.md's canonical invocation
   `INVESTING_TOOLKIT_CACHE=${CLAUDE_PLUGIN_DATA}/cache` expands to `/cache`
   in skill bash context (the var is hook-context-only, empirically empty) →
   every client crashes at unguarded `CACHE_DIR.mkdir()` → 4/5 pack.py wrap
   the crash into `{"error":"client_failed"}` slots **and exit 0** in 0.1s.
   Downstream analysis reads `price=None` → garbage numbers (same failure
   class as ADR-0002, resurrected via the cache path).
2. **Drift machine**: 23 client scripts carry ~1,077 LOC of copy-pasted
   cache boilerplate in 3 naming dialects; ADR-0007's cadence-aware TTL
   landed in 1/23; its block-level CI guard was never built;
   `sync-clients.sh` covers only yfinance×5 + fred×2. The sync discipline
   has empirically failed twice (phantom `check-script-sync.yml` cited in
   4/5 SKILL.mds; LOG_TAG regression c97b7852).

## Users

- **kouko**, on macOS via Claude Code, consuming the toolkit almost
  exclusively through the report layer (confirmed 2026-07-11). Markets:
  TW/JP/US primarily. API keys mostly unset (EDINET/FRED/FinMind absent in
  live env check).
- **Fresh Claude agents** executing report-layer pipelines: they read one
  SKILL.md, run pack commands via Bash, and trust exit codes + JSON shape.
  They are the ones who must notice failure.

Job story: When a report skill requests a data pack, the agent wants one
unambiguous command whose exit code and output status are trustworthy, so
the report either contains real numbers or clearly states what's missing.

## Smallest End State

One data skill (proposed name: `data-markets`) replacing
`data-{us,jp,tw,cn,kr}`, with:

1. **Thin SKILL.md** (routing + shared contract + worked examples;
   ≤6k-token body per repo rule) + `references/market-{us,jp,tw,cn,kr}.md`
   carrying per-market detail (sources, tiers, key requirements, caveats).
2. **Deduplicated `scripts/`**: 18 unique clients (yfinance ×5 → 1,
   fred ×2 → 1) + per-market pack modules behind one `pack.py` entry with
   ticker-suffix market auto-detection (`.TW/.TWO`→tw, `.KS/.KQ`→kr,
   `.SS/.SZ/.HK`→cn, 4-digit/`.T`→jp, else us; `--market` explicit override,
   required for regime-pack which has no ticker).
3. **Single `cache_util.py`** (no sync needed — one copy): XDG-compliant
   uv-style path precedence (CLI flag > `INVESTING_TOOLKIT_CACHE` >
   `$XDG_CACHE_HOME/investing-toolkit` > default
   `~/.cache/investing-toolkit`; user decision 2026-07-11: follow the XDG
   dev-CLI convention, not Apple's `~/Library/Caches` — live-verified that
   uv/gh/claude/codex all use `~/.cache` on this machine), empty-string-safe
   env parsing (strip before truthiness), resolved-dir writability check
   with loud stderr warning + tempdir fallback (virtualenv pattern),
   cadence-aware TTL API (generalizing dgbas's `_compute_ttl`), schema
   version. XDG disposability semantics: deleting the cache dir may only
   slow the next run, never break it. No external cache library (requests-cache breaks yfinance's
   curl_cffi; diskcache doesn't solve path validation).
4. **Fail-loud exit contract**: 0 = all sections fetched, 1 = all failed,
   2 = partial; CLI-arg errors move to 64 (sysexits EX_USAGE) to free code 2
   (currently data-us/pack.py:784-811 uses 2 for arg validation). Top-level
   `_status` block enumerating failed sections; error slots carry full
   traceback text.
5. **Downstream references updated**: 8 SKILL.mds + README(s) +
   `using-investing-toolkit` router + `agents/data-fetcher.md` rewritten to
   the merged skill; `${CLAUDE_PLUGIN_DATA}` removed from all examples.
6. **Tests migrated + extended**: existing 59 cross-layer chain tests keep
   passing against the merged skill; new tests for the `/cache` regression
   (unwritable cache path → loud warning + fallback + real fetch), exit-code
   contract, empty-env-var parsing, market auto-detection.
7. **ADR** recording this decision and superseding ADR-0007's
   block-level-guard design.

## Current State Evidence

(Recon performed this session by 5 read-only audit agents + live tests;
all citations verified against working tree at 531d2eb3.)

- **Forward** (who calls the data layer): report skills invoke
  `data-{country}/scripts/pack.py` via Bash + temp files —
  `report-equity-memo/SKILL.md:106-134`; 8 SKILL.mds reference
  `data-{country}` by name (analysis-comps, analysis-dcf,
  analysis-macro-regime, report-equity-memo, report-portfolio-review,
  report-stock-snapshot, report-screener-list, using-investing-toolkit);
  README.md has 22 `data-` references.
- **Reverse** (SSOT/sync direction — read, not inferred):
  `scripts/sync-clients.sh:5-7` states the canonical-dir model was removed
  post-ADR-0008; **data-us is the live reference**, copies flow
  data-us → {jp,tw,kr,cn} for yfinance_client.py (×5, byte-identical, MD5
  `acd8c…67`) and data-us → data-cn for fred_client.py (×2). The other 16
  clients have **no** sync mechanism.
- **Error** (failure propagation): all 5 pack.py wrap client subprocess
  failure into error slots and exit 0 — `data-us/pack.py:198,213,814`
  (`return 0` unconditional), data-cn/data-jp implicit exit 0; sole
  exception `data-kr/pack.py:681-682` (`sys.exit(1)` iff top-level
  `_partial`). No downstream consumer checks error slots (grep: zero hits
  in data-us/tw/cn pack consumers).
- **Data** (cache path + shape): unguarded resolution expression identical
  in all 23 clients — `yfinance_client.py:32-33`
  (`os.environ.get("INVESTING_TOOLKIT_CACHE") or <home fallback>` — truthy
  `"/cache"` bypasses fallback), crash site `yfinance_client.py:91`
  (`CACHE_DIR.mkdir`), 23 sites enumerated in inventory. Output shapes
  diverge per market: `company_info` (us) / `info` (jp,kr) /
  `yfinance/info/data` (tw) / `yfinance_info` (cn) — live-verified.
- **Boundary** (contracts + tests): `docs/normalization-contract.md:33-95`
  (Tier 1/2/3 staging; Tier-3 canonical real only for US —
  `data-jp/pack.py:468-480`, `data-tw/pack.py:209,474,499`,
  `data-cn/pack.py:377-395`, `data-kr/pack.py:211,387-419` all placeholder);
  `tests/integration/test_cross_layer_chains.py` 59/59 passing (run
  read-only this session) — this suite is the merge's safety net.

Evidence paths appendix: `investing-toolkit/skills/data-*/SKILL.md`,
`investing-toolkit/skills/data-*/scripts/*.py`,
`investing-toolkit/scripts/sync-clients.sh`,
`investing-toolkit/docs/cache-policy.md`,
`investing-toolkit/docs/adr/0007-*.md`, `investing-toolkit/docs/adr/0008-*.md`,
live-test artifacts in session scratchpad (`us-badcache.json` reproduction).

## Alternatives Considered

Researched this session (WebSearch, EN sources; industry findings cited in
conversation):

1. **Patch in place ×23 + keep 5 skills** — rejected: any fix must be
   applied 23×, 16 clients have no sync mechanism, drift recurs (two
   documented failures of the sync discipline).
2. **Shared cache module × 5 skills via extended sync (plan B original)** —
   rejected by user 2026-07-11 after trade-off table: keeps the sync
   machine alive as a third group; user works through the report layer so
   per-market skill triggering has no value to them.
3. **Full fetch-architecture rewrite (subprocess → import, client base
   class)** — rejected: destroys the "client individually runnable"
   affordance, large blast radius, layer boundaries held up in audit.
4. **Adopt cache library** — rejected: requests-cache incompatible with
   yfinance curl_cffi transport (yfinance#2486); diskcache doesn't address
   path-resolution validation (the actual bug); PEP-723 scripts favor
   minimal deps. platformdirs-style resolution logic is small enough to
   hand-roll inside cache_util.
   Sources: docs.astral.sh/uv/concepts/cache/ (precedence ladder),
   platformdirs.readthedocs.io, github.com/ranaroussi/yfinance/issues/2486,
   grantjenks.com/docs/diskcache/, clig.dev (no partial-failure exit-code
   standard → in-house contract), pip.pypa.io/en/stable/topics/caching/.
   (Axis-4 bilingual note: JA-language sweep not performed for the library
   comparison — EN coverage was decisive and consistent; flagged honestly
   rather than silently.)

## What Becomes Obsolete (delete in same arc)

- `scripts/sync-clients.sh` + all MD5-sync discipline (yfinance×5, fred×2
  groups) — the merge removes its reason to exist.
- 4 copies of `yfinance_client.py` (572 LOC each) + 1 copy of
  `fred_client.py` (354 LOC) ≈ 2,642 LOC.
- ~1,077 LOC cache boilerplate across 23 clients → one cache_util.
- 5 per-market SKILL.mds (1,237 lines / 6,661 words) → 1 thin SKILL.md +
  5 reference files.
- Stale claims: `check-script-sync.yml` citations in 4 SKILL.mds
  (`data-us/SKILL.md:23-25` etc.), `docs/cache-policy.md:265`.
- `agents/data-fetcher.md` v1.x content (pre-v2.0.0 script references,
  flat TTLs) — rewrite against merged skill.
- ADR-0007's block-level-guard design — superseded by new ADR.
- Net LOC estimate: data layer 19,198 → ~14–15k (−4–5k), plus
  sync machinery.

## Decision

Build: one `data-markets` skill (thin SKILL.md + per-market references),
deduplicated clients, single cache_util with validated path resolution +
cadence-aware TTL, unified pack.py entry with market auto-detection, fail-loud
exit-code contract (0/1/2, arg errors 64) + `_status` block, downstream
reference migration, regression tests for the live-reproduced bug, and a
superseding ADR. Preserve: three-layer architecture, per-client individual
runnability, normalization-contract tiers (including honest Tier-3
placeholder status), existing pack names and output payload shapes (shape
unification is NOT in this arc — see Out of Scope).

Do NOT build: fetch-architecture rewrite, external cache library,
cross-market output-shape normalization, analysis/report layer changes.

## Out of Scope (adjacent, deliberately deferred)

- **Output-shape unification across markets** (5 divergent JSON shapes) —
  real problem, but doubles the blast radius and requires analysis-layer
  coordination; separate arc after this one lands.
- Stale-data refresh (sector-etf-aggregates 67d, macro-regime calibrations
  70d) and the broken weekly CI cron — separate arc.
- `report-equity-memo` delegation scope-parameter dead wire (violates
  cross-plugin contract Rule 2) — separate arc.
- DCF hardcoded US tax/WACC for non-US tickers — analysis-layer arc.
- `tools/validate_mcp_tools.py` dead code (references removed MCP server) —
  pre-existing orphan, flagged, deleted only on explicit user ask.
- Router `analysis-comps` omission — will be naturally fixed by the router
  update in this arc's doc migration IF touched; otherwise flagged.
- domain-teams:investing-team 2-week drift — separate sync arc.

## Open Questions

1. ~~Skill name~~ **RESOLVED 2026-07-11: `data-markets`** (user confirmed;
   `financial-*` variants rejected as semantically redundant inside
   investing-toolkit; layer prefix kept for router-table parallelism).
2. **Old skills' folder fate**: delete `data-{country}/` outright in the
   same PR (proposed default — marketplace plugin update is atomic; user
   did not object at sign-off) vs deprecation stubs for one release.
3. **Exit-code 2 consumers**: no known consumer of the current
   `return 2 = arg error` behavior was found (grep pending in plan);
   renumbering to 64 assumed safe — verify during planning.

## Sign-off

User signed off on Problem / Smallest End State / Out of Scope and the
`data-markets` name, 2026-07-11 (this session). SKILL.md body token count
<5k tokens added as an acceptance criterion (repo cap 6k; degradation
guard).
