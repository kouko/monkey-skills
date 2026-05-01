# Migration Guide: investing-toolkit v1.x → v2.0.0

This guide helps users update to the v2.0.0 three-layer architecture.

## TL;DR

- **Slash commands keep working** — `/invest-memo`, `/invest-screen`, `/invest-portfolio`, `/invest-macro` still work with their v1.x names. Only `/invest-snapshot` is new.
- **All 14 v1.x skill directories were deleted** (`us-macro`, `japan-macro`, `dcf-valuation`, `investment-memo-writer`, …) and replaced by **5 `data-{country}` + 6 `analysis-*` + 4 `report-*`** skills (16 total including the router).
- **Direct skill invocations need updating** — if you wrote integrations that called e.g. `skills/dcf-valuation/SKILL.md` directly, you must update the skill name (see rename map below).
- **Data sources, output schemas, and computation logic — preserved or improved.** See [What stayed the same](#what-stayed-the-same).

## Quick start (haven't customized anything)

If you only used slash commands and didn't write your own integrations on top of investing-toolkit, **no action needed**.

```bash
git pull
claude-code update plugins
```

Continue using `/invest-memo AAPL`, `/invest-screen value`, `/invest-portfolio holdings.csv`, etc.

## If you wrote integrations on top of v1.x

For each v1.x use case, here is the v2.0.0 equivalent.

### Macro fetch (single country)

| | v1.x | v2.0.0 |
|---|---|---|
| Skill | `us-macro` / `japan-macro` / `taiwan-macro` / `korea-macro` / `china-macro` | `data-us` / `data-jp` / `data-tw` / `data-kr` / `data-cn` |
| Pack type | (single output) | `--pack regime` (or `equity` / `industry` / `screener-input` / `portfolio-input`) |

The new `data-{country}` skills bundle multiple pack types per country. Pick `--pack regime` for the v1.x macro-equivalent output.

### Macro regime classification (cross-country)

| | v1.x | v2.0.0 |
|---|---|---|
| Skill | `macro-regime-snapshot` | `analysis-macro-regime` |
| Input | (called country macro skills internally) | takes `data-{country}` regime-pack JSON via temp file |

### Individual stock data

| | v1.x | v2.0.0 |
|---|---|---|
| Skill | `us-stock-snapshot` / `japan-stock-snapshot` / `taiwan-stock-snapshot` | `data-us` / `data-jp` / `data-tw` with `--pack equity` |
| Composed report | (each was its own report) | `report-stock-snapshot` (country-aware orchestrator) |

### DCF compute

| | v1.x | v2.0.0 |
|---|---|---|
| Skill | `dcf-valuation` | `analysis-dcf` |
| Behaviour | unchanged formula (Damodaran 3-stage); buggy unit-normalisation heuristic removed |

### Stock screener

| | v1.x | v2.0.0 |
|---|---|---|
| Compute skill | `stock-screener` (data + compute combined) | `analysis-screener` (compute only) |
| Data input | (fetched internally via yfinance) | `data-{country} --pack screener-input` JSON via temp file |
| Composed report | (combined into stock-screener) | `report-screener-list` |

### Portfolio review

| | v1.x | v2.0.0 |
|---|---|---|
| Compute skill | `invest-portfolio` (data + compute combined) | `analysis-portfolio` (compute only) |
| Data input | (fetched internally) | `data-{country} --pack portfolio-input` JSON via temp file |
| Composed report | (combined into invest-portfolio) | `report-portfolio-review` |

### Equity memo

| | v1.x | v2.0.0 |
|---|---|---|
| Skill | `investment-memo-writer` | `report-equity-memo` |
| New section | (none) | **Comps** section via Phase 2.5 runtime `research-agent` peer-discovery (`--auto` / `--interactive`) |

## What stayed the same

- **All slash commands keep working** with their original names (`/invest-memo`, `/invest-screen`, `/invest-portfolio`, `/invest-macro`).
- **Data sources unchanged** — yfinance, FRED, SEC EDGAR, EDINET, MOPS, TWSE, FinanceDataReader (BOK ECOS-KEYSTAT), NBS, akshare.
- **DCF formula unchanged** — Damodaran 3-stage. `analysis-dcf` is the rename of v1.x `dcf-valuation` (with a buggy unit-normalisation heuristic removed; see [Fixed](../CHANGELOG.md)).
- **All 8 screener presets preserved** — `value` / `deep-value` / `quality` / etc.
- **5-country macro regime classification preserved** — Investment Clock + Growth/Inflation/Policy framework across US / JP / TW / KR / CN.
- **Output JSON schemas preserved** for snapshot, DCF, screener, and portfolio outputs (with `_provenance` improvements).

## What changed

- **New `analysis-comps`** — peer multiples comparison (P/E trailing + forward, EV/EBITDA, P/S, P/B) with statistics + anchor delta + composite ranking.
- **`report-equity-memo` Phase 2.5** — runtime `research-agent` peer-discovery for the Comps section (`--auto` mode automatic; `--interactive` mode prompts for confirmation).
- **`analysis-portfolio`** auto-resolves JP bare 4-digit tickers (`7203` ↔ `7203.T`) and KR equivalent — pre-fix users hit silent missing-price entries.
- **`fred_client.py`** — parallel multi-series fetch (default 8 workers; `FRED_MAX_WORKERS` env override) and removed custom User-Agent that triggered FRED's bot filter.
- **ADR-0001 three-layer architecture** — explicit Data / Analysis / Report separation with main-agent + temp-file passing replacing v1.x intra-skill subprocess dispatch.

## Skill rename map (full table)

| v1.x skill | v2.0.0 skill | Notes |
|---|---|---|
| `us-macro` | `data-us` (with `--pack regime`) | data layer; multi-pack |
| `japan-macro` | `data-jp` (with `--pack regime`) | data layer; multi-pack |
| `taiwan-macro` | `data-tw` (with `--pack regime`) | data layer; multi-pack |
| `korea-macro` | `data-kr` (with `--pack regime`) | data layer; multi-pack |
| `china-macro` | `data-cn` (with `--pack regime`) | data layer; multi-pack |
| `us-stock-snapshot` | `data-us` (with `--pack equity`) + `report-stock-snapshot` | data + report split |
| `japan-stock-snapshot` | `data-jp` (with `--pack equity`) + `report-stock-snapshot` | data + report split |
| `taiwan-stock-snapshot` | `data-tw` (with `--pack equity`) + `report-stock-snapshot` | data + report split |
| `technical-snapshot` | `analysis-technical` | analysis layer (pure compute) |
| `stock-screener` | `data-{country} --pack screener-input` + `analysis-screener` + `report-screener-list` | 3-layer split |
| `dcf-valuation` | `analysis-dcf` | analysis layer; bug-fixed |
| `invest-portfolio` | `data-{country} --pack portfolio-input` + `analysis-portfolio` + `report-portfolio-review` | 3-layer split |
| `macro-regime-snapshot` | `analysis-macro-regime` | analysis layer (pure compute) |
| `investment-memo-writer` | `report-equity-memo` | report layer; +Phase 2.5 Comps |
| (none) | `analysis-comps` | **NEW** — peer multiples |
| (none) | `report-stock-snapshot` | **NEW** — country-aware orchestrator |

The canonical mapping lives in [ADR-0001 §Slash-Command Rename Map](adr/0001-data-analysis-report-layers.md).

## Path convention changes

- **v1.x**: each skill had its own `scripts/` directory with copies of all clients (50+ duplicates across the toolkit).
- **v2.0.0**: canonical clients live at `investing-toolkit/scripts/`. `data-{country}/scripts/` keeps MD5-locked copies (CI-enforced via `.github/workflows/check-script-sync.yml`). `analysis-*` and `report-*` skills have **no client copies** — only their own compute or format scripts.
- **Cross-skill calls**: use `${CLAUDE_PLUGIN_ROOT}/skills/<skill>/scripts/<file>` (not `${CLAUDE_SKILL_DIR}/../<skill>/`).

To re-sync data-pack copies after editing a canonical client:

```bash
investing-toolkit/scripts/sync-clients.sh         # update copies
investing-toolkit/scripts/sync-clients.sh --check # CI dry-run mode
```

## Removed v1.x mechanisms

- `investing-toolkit/scripts/sync-scripts.sh` — replaced by `sync-clients.sh`.
- `investing-toolkit/scripts/sync-check.sh` — replaced by `sync-clients.sh --check`.
- `investing-toolkit/tests/test_skill_md_sync.py` — v1.16.1 dual-mode validation; v2.0.0 uses main-agent + Bash so per-skill MCP sync is no longer needed.

## Known v2.1+ items (deferred)

- **Earnings analysis** — DEFERRED. Waiting for a free consensus data source / dogfood demand.
- **3-statement model** — DROPPED. Sell-side artifact; philosophy mismatch with the buy-side primary-source pipeline.
- **Sector-adjusted multiples for Comps** — v2.1+. Banks (P/B + ROE), REITs (P/AFFO), tech (EV/Revenue + Rule-of-40).
- **`analysis-comps --mode compute` activation** — currently placeholder; falls back to direct compute with audit trail.
- **JP real-rate decomposition C+D+E framework restoration** — currently `null`; see `analysis-macro-regime/references/japan-real-rate-roadmap.md`.
- **KR DART primary-source equity integration** — v2.1+.

## References

- [ADR-0001](adr/0001-data-analysis-report-layers.md) — three-layer architecture decision record.
- [Spec](../../docs/superpowers/specs/2026-05-01-investing-toolkit-v2.0.0-three-layer-design.md) — full v2.0.0 design specification.
- [Plan](../../docs/superpowers/plans/2026-05-01-investing-toolkit-v2.0.0.md) — implementation plan.
- [CHANGELOG](../CHANGELOG.md) — release notes for v2.0.0.
