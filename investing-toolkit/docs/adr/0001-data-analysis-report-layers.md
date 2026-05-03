# ADR-0001: Three-Layer Skill Architecture (Data / Analysis / Report)

- **Status**: Accepted
- **Date**: 2026-05-01
- **Version target**: investing-toolkit v2.0.0
- **Spec**: `docs/superpowers/specs/2026-05-01-investing-toolkit-v2.0.0-three-layer-design.md`

## Context

Through v1.x the investing-toolkit grew to 15 skills with overlapping concerns. Two structural problems became blocking:

1. **Mixed concerns inside a single skill**. `us-stock-snapshot`, `japan-stock-snapshot`, `taiwan-stock-snapshot`, `dcf-valuation`, `stock-screener`, `invest-portfolio`, and `investment-memo-writer` all bundled three distinct responsibilities — data fetching (I/O, tier routing, retries), analysis (pure compute over fetched JSON), and report formatting (Markdown card / memo / table). When one source changed (e.g. TWSE OpenAPI added `/rwd/`), edits had to be replayed across several skills with subtle drift.
2. **50+ duplicate client files**. `yfinance_client.py` appeared in 11 skills, `fred_client.py` in 7, `ta_client.py` in 3 — each with the same code path but no enforcement that they stay in sync. `sync-check.sh` partially addressed this, but with no CI gate the duplication silently drifted between PRs.

The single-responsibility violation also made testing painful: a unit test for "compute RSI" had to mock `yfinance.Ticker.history()`, which is an integration concern. And cross-skill composition (memo wants snapshot's data → enriches with macro) required either sub-agent dispatch (token-expensive, lossy through context boundaries) or scraping a peer skill's stdout.

## Decision

Adopt **Way B: three-layer split with country-bundled data skills**.

Every skill belongs to exactly one layer, identified by a directory-name prefix:

- `data-{country}/` — Layer 1: I/O only
- `analysis-{topic}/` — Layer 2: pure compute only
- `report-{deliverable}/` — Layer 3: orchestration + formatting

The 16-skill final list (15 → 16; gains `analysis-comps` + `report-screener-list`, splits `stock-screener` and `invest-portfolio` into compute/orchestration pairs, merges 3 country snapshots into 1 cross-country `report-stock-snapshot`) is enumerated in the spec §4.1.

## Layer Responsibilities

| Layer | Owns | Forbidden | I/O | Cross-skill calls |
|---|---|---|---|---|
| **Data** (`data-*`) | Network I/O, tier routing (e.g. EDINET key check), cache, batch dispatch (`pack.py --ticker AAPL` single, `--tickers AAPL,MSFT,GOOGL` batch). Country-bundled: 1 skill = 1 country = all clients for that country. | Computing indicators, ranking, formatting Markdown | yes (HTTP, file cache) | **none** — leaf nodes |
| **Analysis** (`analysis-*`) | Pure functions: input JSON → output JSON. RSI/MACD/BB compute, DCF iteration, comps multiples median/mean/quartile + anchor delta, screener filter+score+rank, portfolio P&L, IC+GIP regime classification. | Network I/O, file fetch, sub-agent dispatch | **none — zero exceptions** | none |
| **Report** (`report-*`) | Orchestration (call data skills via Bash, write JSON to temp file, call analysis skills via Bash, read result), country routing (ticker suffix → which `data-{country}` to call), Markdown formatting. May delegate to `domain-teams:investing-team` / `domain-teams:docs-team`. | Re-implementing a multiple, hand-rolling RSI inline, calling yfinance directly | yes (read/write temp files; subprocess) | yes (cross-plugin via plugin-name path) |

### Cross-skill data passing

- **Main agent + temp file** is the canonical pattern. The orchestrating skill (always a `report-*` or the user) calls Bash to run `data-X/scripts/pack.py > /tmp/data.json`, then Bash again to run `analysis-Y/scripts/compute.py --in /tmp/data.json > /tmp/result.json`, then formats from `/tmp/result.json`.
- **Sub-agent dispatch is NOT used** for layer-to-layer hand-off. It is reserved for autonomy-required work like `investing-team` agents (Worker / Evaluator).
- Rationale: subprocess + temp file is deterministic, debuggable, replayable, and round-trip lossless. Sub-agent dispatch incurs context-window costs and adds a serialization layer that benefits nothing here.

## Anthropic Skill-Folder Rule Compliance

Anthropic's skill convention requires that scripts live inside the skill folder that owns them. Two consequences:

1. **Each skill owns its `scripts/`**. `analysis-technical/scripts/ta_client.py` is owned by `analysis-technical`, not by a global `lib/`. This is the rule on **ownership**, not on **execution**.
2. **Cross-skill execution via Bash is allowed**. A `report-*` skill may run `bash {plugin}/skills/data-us/scripts/pack.py`. The script lives in `data-us/scripts/`; nothing in the rule prohibits another skill from spawning a subprocess into it. This is the explicit pattern v2.0.0 uses for data → analysis hand-off.

This is the same pattern already used in v1.x for `${CLAUDE_SKILL_DIR}` resolution and is preserved.

## Acceptable Duplications (CI-Enforced Sync)

Bundling the same client into multiple skill folders is a deliberate trade-off: it preserves "skill folder is self-contained" at the cost of file duplication. Drift is prevented by CI MD5 check.

> **2026-05-03 amendment (per ADR-0008)**: MCP server removed; the
> `investing-toolkit/scripts/` canonical-vs-skill-copy duality is gone.
> Only true cross-skill duplications remain. `data-us` is the reference
> skill for both groups (US is the architectural "first skill" by
> convention). The 5 single-skill groups added in PR #222 (nbs / akshare /
> dgbas / ndc / cbc / statgov / fdr) are deleted — those clients now live
> in exactly one skill each, no sync needed.

| File | Reference (data-us) | Cross-skill copies |
|---|---|---|
| `yfinance_client.py` | `investing-toolkit/skills/data-us/scripts/yfinance_client.py` | `data-jp`, `data-tw`, `data-kr`, `data-cn` (4 copies) |
| `fred_client.py` | `investing-toolkit/skills/data-us/scripts/fred_client.py` | `data-cn` (1 copy; CN uses FRED for cross-checks) |

All other clients (boj, ecb, estat, edinet, fdr, sec_edgar, mops, finmind, twse_openapi, tdnet, dgbas, ndc, cbc, statgov, nbs, akshare, ta) live in **exactly one skill** — no cross-skill duplication, no sync needed.

**CI check** (`.github/workflows/check-script-sync.yml`):
- For each cross-skill duplicated file, compute MD5 across all known locations. Fail the build if MD5 differs.
- Scope is **explicit** (skill list per group), not glob-based — prevents silent widening if a non-listed skill ever drops in a copy.
- On drift, the workflow prints the reference/drift MD5 plus up to 50 lines of unified diff so reviewers see what changed, not just that something changed.
- Status: **REQUIRED** on `main` branch protection (promoted in v2.1.x-d, 2026-05-02; scope tightened in ADR-0008, 2026-05-03).
- Local helper: `bash investing-toolkit/scripts/sync-clients.sh --check` reports drift; `bash investing-toolkit/scripts/sync-clients.sh` (no flag) propagates `data-us` reference → cross-skill copies.

## Slash-Command Rename Map (16 entries)

Slash commands track the new skill names. No alias shim — clean break per spec §6.3.

| v1.x command / skill | v2.0.0 command / skill |
|---|---|
| `/macro-us` (us-macro) | `/data-us` |
| `/macro-jp` (japan-macro) | `/data-jp` |
| `/macro-tw` (taiwan-macro) | `/data-tw` |
| `/macro-kr` (korea-macro) | `/data-kr` |
| `/macro-cn` (china-macro) | `/data-cn` |
| `/dcf` (dcf-valuation) | `/analysis-dcf` |
| (new) | `/analysis-comps` |
| (compute portion of stock-screener) | `/analysis-screener` |
| `/technical` (technical-snapshot) | `/analysis-technical` |
| (compute portion of invest-portfolio) | `/analysis-portfolio` |
| (macro-regime-snapshot) | `/analysis-macro-regime` |
| `/memo` (investment-memo-writer) | `/report-equity-memo` |
| `/snapshot-{us,jp,tw}` (3 skills) | `/report-stock-snapshot` (auto-routes by ticker suffix) |
| `/invest-portfolio` (orchestration portion) | `/report-portfolio-review` |
| (orchestration portion of stock-screener) | `/report-screener-list` |
| `/invest` (using-investing-toolkit) | `/invest` (router skill — kept; routing table updated) |

## Rationale

- **Separation of concerns**. One skill = one layer = one job. Touching a tier-routing rule in `data-jp` cannot break `analysis-dcf`.
- **Complexity-where-it-belongs**. Network retries, tier routing, batch parallelism, cache TTL — these belong in data. Pure math belongs in analysis. Orchestration belongs in report. Each layer's testing and review can use the right tool (integration test for data; pure unit test for analysis; smoke test for report).
- **Eliminates the snapshot/memo overlap**. `us-stock-snapshot` and `investment-memo-writer` no longer fight over who owns the SEC EDGAR client; `data-us` does. The report skills compose what they need.
- **Country bundling fits the analyst mental model**. "I'm researching a JP stock" → load `data-jp` once, get yfinance + EDINET + TDnet + BOJ + e-Stat + ECB. Country is the natural grouping for primary-source-grounded analysis.
- **Cross-country routing is Layer 3's job**. Mixed-market screener (`AAPL,2330.TW,7203.T`) is parsed and split by `report-screener-list`, which fans out to `data-{country}/pack.py --tickers <group>` per country in parallel.

## Alternatives Considered

- **Way A: shared library at toolkit root (`investing-toolkit/lib/`)**. Rejected: violates Anthropic's skill-folder ownership rule (the script owner becomes the toolkit root, not a skill), and breaks Cowork sandbox path resolution which expects everything reachable from a single skill folder.
- **Way C: keep 1 country = 3 skills (data + analysis + report per country)**. Rejected as 45-skill explosion. Most analysis is country-agnostic (DCF works on any cash-flow series); duplicating it per country produces drift with no benefit.
- **Sub-agent dispatch for data → analysis hand-off**. Rejected: temp-file IPC is deterministic and observable; sub-agent dispatch costs context tokens and adds a serialization layer that benefits nothing for pure-function compute.
- **Alias shim for renamed slash commands**. Rejected: defeats the purpose of a clean rename; users discover the new namespace faster without aliases. Major version bump (v1.16.4 → v2.0.0) is the correct mitigation.

## Consequences

### Positive

- Schema and breaking changes localized to one layer.
- New countries plug in by adding `data-{xx}/` only.
- New analyses (sector rollup, backtest) plug in by adding `analysis-*/` only.
- Comps + tearsheet roadmap (v2.1+) cleanly extends Layer 3 without touching Layers 1-2.
- Pure-function analysis layer enables fast, deterministic unit tests (no network mocks required).
- `report-stock-snapshot` collapses 3 country snapshot skills into 1 with auto-routing — fewer entry points for users.

### Negative

- **One-time slash command break**. Mitigated by prominent CHANGELOG and announcement; no alias shim.
- **MCP tool registration audit**. `mcp.json` paths must update per skill rename. Verified at PR 1 close.
- **Acceptable duplication of 4 client files** (yfinance × 5, fred × 2, nbs × 1, akshare × 1; ta_client.py = canonical only in v2.0.0). Mitigated by MD5 sync CI + helper script. Drift becomes a CI-blocking event in PR 3.
- **Slightly more files to navigate** for a single deliverable (data → analysis → report) versus an all-in-one skill. The trade-off is paid back the first time a single source change no longer cascades through 3+ skills.

### Neutral

- Layer-to-layer hand-off via temp file adds one subprocess hop per layer. Negligible at human-interactive timescales; replaces sub-agent dispatch which was strictly more expensive.
- Sync CI starts as advisory in PR 1, becomes required in PR 3 — gives the parallel skill-creation PRs room to land without a chicken-and-egg block.

## Future Expansion

New skills follow the prefix convention:

- New country data → `data-{country}/` (e.g. `data-eu`, `data-in`, `data-sg`)
- New compute → `analysis-{topic}/` (e.g. `analysis-sector-rollup`, `analysis-backtest`, `analysis-earnings`)
- New deliverable → `report-{format}/` (e.g. `report-comps-tearsheet` v2.1+, `report-earnings-update`)

A skill that does not fit one layer is a smell — re-decompose before merging.

## Implementation Order (informational)

PRs in spec §6.1:

1. **PR 1** (this PR) — skeleton: 16 skill folders + ADR + advisory CI sync. No behavior change yet.
2. **PR 2** — port v1.x logic into the new layers; route slash commands to new skills.
3. **PR 3** — promote CI sync from advisory to required; flip `mcp.json` paths; CHANGELOG announces v2.0.0.
4. **PR 4+** — Comps full path (peer discovery in `analysis-comps`, embedded in `report-equity-memo`).

The advisory-to-required transition for sync CI is the single most important governance step: as long as the toolkit has duplicated clients, drift = silent bug. Required-status CI eliminates the failure mode.

## References

- Spec: `docs/superpowers/specs/2026-05-01-investing-toolkit-v2.0.0-three-layer-design.md`
- Design principles: `investing-toolkit/docs/design-principles.md` (empirical-first design rule)
- Sync helper: `investing-toolkit/scripts/sync-clients.sh`
- CI check: `.github/workflows/check-script-sync.yml`
