# Changelog

All notable changes to investing-toolkit will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [v2.1.1] — 2026-07-05

### Fixed — `report-equity-memo` Codex dispatch-portability

Phase 2.5's peer-discovery step named `general-purpose` (a real
Claude-Code built-in agent-type name) directly in `SKILL.md`, with no
literal `Agent(...)` syntax but also no per-host reference file (Codex
dispatch-portability survey finding, `docs/skill-mining/2026-07-05-
codex-dispatch-portability-survey.md` — classed borderline (A)/(B)).
Reworded to "dispatch a general-reasoning subagent" and added
`references/{claude-code-tools.md,codex-tools.md}` mapping
`general-purpose` onto Codex's `default`/`worker`/`explorer` built-ins.

## [v2.1.0] — 2026-05-02

`analysis-macro-regime` Phase 1 per-country classifier refactor. Decomposed the v1.9.0 unified IC + Hedgeye GIP classifier into 5 native per-country modules (`classify_us / jp / tw / kr / cn`). See [ADR-0004](docs/adr/0004-analysis-macro-regime-phase1-per-country-classifiers.md) for design rationale + Phase 2 deferral.

### Added

- **5 per-country classifier modules** (`classify_{us,jp,tw,kr,cn}.py`) — each implements its country's native framework rather than re-labeling legacy IC:
  - **US**: IC + Hedgeye GIP + Fed FIT (post-FAIT 2025) + 4-tier real-rate decomposition (HLW / LM / SEP / NY Fed composite) + yield-curve overlay.
  - **JP**: BOJ stance + Tankan business sentiment DI (大企業/中小企業 × 製造/非製造) + ESRI 景気動向指数 CI + deflation/inflation regime detection + ECB ex-post real-yield 4-tier band.
  - **TW**: NDC 五色景氣燈號 score-led (9-45 composite) + 9 構成項目 dispersion (per 2024 revision) + TIER 製造業營業氣候測驗點 + TSMC TAIEX concentration overlay.
  - **KR**: BOK 단일 2% target alignment + KOSTAT 동행지수순환변동치 cycle phase + 가계부채 GDP overlay + KOSPI 삼성+SK 하이닉스 ~40.96% concentration overlay.
  - **CN**: PBOC reaction (7天逆回购 1.40% post-2024-07) + credit impulse (CICC TSF flow-yoy 2nd-derivative) + 4-component dispersion alarm + 房地产 GDP-share overlay (3 definitions disclosed) + CPI framing enum (`supportive_recovery_below_target` captures PBOC's "wants inflation up" stance).
- **5 calibration YAMLs** (`scripts/calibrations/{us,jp,tw,kr,cn}.yaml`) — machine-readable extracts of `references/thresholds-{country}.md` (2026-Q1/Q2 vintages). All numeric thresholds plumbed into classifier code instead of sitting as un-executed documentation.
- **5 grounding research notes** (`research/grounding-{country}-2026-05.md`) — partial-recalibration delta refreshes per `recalibration-protocol.md` template. JP captured 4 material BOJ events 2026-04-19 → 2026-05-02 (FY2026 核 CPI 1.9%→2.7-2.8% upward revision, 6-3 vote, Ueda 4/30 anchor).
- **Output schema `2.0-phase1`** with `by_country.{cc}` envelope (country / framework_used / native_verdict / indicators_used / data_quality / confidence / provenance). `cross_country` hardcoded `null` (deferred to Phase 2).
- **Per-country fetch additions**:
  - JP: `boj_client.py --tankan-business-di` (4 series codes verified vs BOJ official docs); `pack.py` wires Tankan + ESRI coincident-index / leading-index / 機械受注 e-Stat presets.
  - CN: `pack.py:_compute_credit_impulse()` (CICC TSF flow → trailing-12m-sum YoY → 12-month change); methodology doc at `references/credit-impulse-methodology.md`.

### Changed

- **Output schema migration** for direct `regime_compose.py` consumers: read `out["by_country"][cc]` instead of `out["countries"][cc]`. `out["cross_country"]` is `null` in Phase 1.
- **Per-country threshold reference docs** (`references/thresholds-{country}.md`) — partial-recalibration refresh from v1.11.0 (2026-04-19) to 2026-05-02. JP captures 4 material BOJ policy events.

### Removed

- `_legacy_ic.py` — the v1.9.0 unified `classify_country()` IC + GIP fallback path. Helpers migrated to `_helpers.py`; per-country classifiers import from there.
- `out["countries"]` and `out["cross_country_consensus"]` schema fields (replaced by `out["by_country"]`; consensus deferred to Phase 2).

### Deferred (per fresh-eyes audit + ADR-0004)

- **Cross-country comparable surface** (Phase 2 / ADR-0005). Re-trigger: Phase 1 stable ≥4 weeks, ≥5 multi-country invocations, or memo workflow surfacing concrete need. If none fire within 6 months, evaluate whether comparable surface is needed at all.
- **KR ESI explicit ECOS API integration** — current code uses fdr_client KEYSTAT 'sentiment' group as best-effort fallback; explicit ECOS key-based integration deferred to v2.2.0.
- **TW TIER preset wiring at NDC client level** + live TWSE monthly weight ingestion — deferred to v2.1.x or v2.2.0.
- **CN true stock-yoy credit impulse** — current implementation uses flow-yoy second-derivative with explicit honest methodology label; switch when PBOC publishes stock series via akshare or direct scrape.

## [v2.0.0] — 2026-05-01

Three-Layer Skill Architecture (Data / Analysis / Report). See [ADR-0001](docs/adr/0001-data-analysis-report-layers.md) for the architectural decision and [migration guide](docs/migration-v2.0.0.md) for v1.x → v2.0.0 upgrade instructions.

### Breaking changes

- Plugin version bumped 1.16.5 → 2.0.0 (skill-API breaking changes — see Removed below).
- All 14 v1.x skill **directories** deleted and replaced by 16 new skills under three layers (5 `data-{country}` + 6 `analysis-*` + 4 `report-*` + 1 router).
- Removed `investing-toolkit/scripts/sync-scripts.sh`, `investing-toolkit/scripts/sync-check.sh`, and `investing-toolkit/tests/test_skill_md_sync.py` — the v1.16.1 dual-mode sync mechanism is retired.
- Slash-command **internal routing** now points at the new skills (full mapping in [ADR-0001 §Slash-Command Rename Map](docs/adr/0001-data-analysis-report-layers.md)). User-facing slash command names (`/invest-memo`, `/invest-screen`, `/invest-portfolio`, `/invest-macro`) are preserved.

### Added

- **5 new `data-{country}` skills** (US / JP / TW / KR / CN) — Layer 1 country-bundled fetch with 5 pack types each (`equity` / `regime` / `industry` / `screener-input` / `portfolio-input`).
- **6 new `analysis-*` skills** (Layer 2, pure compute, no I/O):
  - `analysis-dcf` — Damodaran 3-stage DCF (rename of v1.x `dcf-valuation`).
  - `analysis-comps` — peer multiples comparison (5 multiples: P/E trailing + forward, EV/EBITDA, P/S, P/B); statistics + anchor delta + composite ranking. **NEW.**
  - `analysis-screener` — multi-criteria screener engine (rename of v1.x `stock-screener` compute path).
  - `analysis-technical` — RSI / MACD / Bollinger / ATR / SMA (rename of v1.x `technical-snapshot`).
  - `analysis-portfolio` — holdings P&L + regime overlay (rename of v1.x `invest-portfolio`).
  - `analysis-macro-regime` — IC + GIP regime classification across US/JP/TW/KR/CN (rename of v1.x `macro-regime-snapshot`).
- **4 new `report-*` skills** (Layer 3, orchestrators):
  - `report-equity-memo` — full equity memo pipeline (rename of v1.x `investment-memo-writer`).
  - `report-stock-snapshot` — country-aware stock snapshot (consolidates v1.x `us-stock-snapshot` / `japan-stock-snapshot` / `taiwan-stock-snapshot`).
  - `report-portfolio-review` — portfolio review report (orchestrator above `analysis-portfolio`).
  - `report-screener-list` — screener list report. **NEW.**
- **`analysis-comps`** as a first-class skill: peer multiples (P/E trailing + forward, EV/EBITDA, P/S, P/B) with median / mean / IQR statistics, anchor delta vs peer median, and composite ranking.
- **`report-equity-memo` Phase 2.5**: runtime `research-agent` peer-discovery for the Comps section (`--auto` / `--interactive` modes).
- **ADR-0001**: Three-Layer Skill Architecture decision record at `investing-toolkit/docs/adr/0001-data-analysis-report-layers.md`.
- **Migration guide**: user-facing v1.x → v2.0.0 upgrade guide at `investing-toolkit/docs/migration-v2.0.0.md`.
- **CI sync workflow**: `.github/workflows/check-script-sync.yml` enforces MD5 equality between canonical clients (`investing-toolkit/scripts/`) and `data-{country}/scripts/` copies. Advisory in v2.0.0; will become required in v2.0.1+.
- **New helper**: `investing-toolkit/scripts/sync-clients.sh` (canonical → copies sync; `--check` mode for CI).
- **New slash command**: `/invest-snapshot` → routes to `report-stock-snapshot`.
- **Test suite**: 296 non-network + 27 network automated pytest tests covering data packs, analysis compute, and report orchestration.

### Changed

- **Architecture** — three-layer separation (Data / Analysis / Report). Layer 1 is I/O-only, Layer 2 is pure compute, Layer 3 orchestrates. See ADR-0001.
- **Cross-skill data passing** — main agent + temp files (replaces v1.x intra-skill subprocess dispatch). Each layer reads/writes JSON via temp file paths passed by the main agent.
- **`fred_client.py`** — parallel multi-series fetch via `ThreadPoolExecutor` (default 8 workers; configurable via `FRED_MAX_WORKERS` env var); removed custom User-Agent header (FRED bot filter blocked it, causing intermittent fetch failures).
- **Slash commands** — internal routing updated; user-facing names preserved (`/invest-memo`, `/invest-screen`, `/invest-portfolio`, `/invest-macro`). New: `/invest-snapshot`.

### Removed

- 14 v1.x skill directories: `us-macro`, `japan-macro`, `taiwan-macro`, `korea-macro`, `china-macro`, `us-stock-snapshot`, `japan-stock-snapshot`, `taiwan-stock-snapshot`, `technical-snapshot`, `stock-screener`, `dcf-valuation`, `invest-portfolio`, `macro-regime-snapshot`, `investment-memo-writer`.
- `investing-toolkit/scripts/sync-scripts.sh` (replaced by `sync-clients.sh`).
- `investing-toolkit/scripts/sync-check.sh` (replaced by `sync-clients.sh --check`).
- `investing-toolkit/tests/test_skill_md_sync.py` (v1.16.1 dual-mode validation; obsolete in v2.0.0 main-agent + Bash architecture).

### Fixed

- **JP bare 4-digit ticker resolution** (critical): `analysis-portfolio._resolve_price()` now auto-resolves `7203` ↔ `7203.T` mismatches between holdings files and `data-jp` pack output. Pre-fix produced silent missing-price entries; post-fix logs the mapping under `_provenance.ticker_resolutions`.
- **ROC quarter filing-aware logic**: `data-tw/pack.py.latest_roc_quarter()` no longer returns unfiled quarters near the Mar 31 / May 15 / Aug 14 / Nov 14 filing-deadline boundaries.
- **`analysis-dcf`** removed a dangerous unit-normalisation heuristic that mis-scaled BRK.A-style low-share-count stocks by 1e6× (mis-classifying market cap and intrinsic value).
- ~30 Wave 4 quality findings addressed in PR #172 and ~10 in PR #173.

### Pull requests

- **#172** — three-layer refactor (15 → 15 skills; 14 v1.x deleted; 11 + 4 implementer agents across Phase 1 + Phase 2; ADR-0001; 272-test suite baseline).
- **#173** — `analysis-comps` + `report-equity-memo` peer-discovery (15 → 16 skills; 24 new tests; `fred_client` parallel fetch + UA fix).
- **#(this PR)** — documentation polish (CHANGELOG, migration guide, READMEs, design-principles update) and final v2.0.0 plugin-version bump.

### Slash-command routing map (high-level)

User-facing slash commands stay stable. Only the underlying skill they route to changes.

| Slash command | v1.x routes to | v2.0.0 routes to |
|---|---|---|
| `/invest-macro` | `us-macro` / `japan-macro` / `taiwan-macro` / `korea-macro` / `china-macro` | `data-{country}` regime-pack + `analysis-macro-regime` |
| `/invest-memo` | `investment-memo-writer` | `report-equity-memo` |
| `/invest-screen` | `stock-screener` | `report-screener-list` |
| `/invest-portfolio` | `invest-portfolio` | `report-portfolio-review` |
| `/invest-snapshot` *(new)* | (none) | `report-stock-snapshot` |

For the full v1 skill → v2 skill mapping (16 entries including internal renames), see [ADR-0001 §Slash-Command Rename Map](docs/adr/0001-data-analysis-report-layers.md).

[v2.0.0]: https://github.com/kouko/monkey-skills/releases/tag/investing-toolkit-v2.0.0
