# Changelog

All notable changes to investing-toolkit will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

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
