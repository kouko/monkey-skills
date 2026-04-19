# Design Spec: investing-toolkit v1.10.0 — PMI + JP Real Rates + Swap Spread

**Date**: 2026-04-18
**Topic**: Absorb three v1.9.0-deferred items into macro-regime-snapshot and country macros
**Previous release**: v1.9.0 (PR #92, merged 2026-04-18) — multi-country regime skill + US real-rate block + per-country threshold files + primary-source grounding audit

## 1. Goal

Close three data-coverage gaps left open in v1.9.0:

1. **ISM PMI absence** — Block 1 (Macro Summary) has no PMI signal; v1.9.0 `signal` glossary lists PMI thresholds but no series fetches it.
2. **JP real-rate block absence** — `thresholds-japan.md` notes that JGBi data exists but is not yet wired; only US has a Real Rate Decomposition block.
3. **Swap spread absence** — `Rate Stress Dashboard` block 4 covers real rates only; LSEG reference pattern also includes swap-spread as liquidity stress signal.

Deliver all three as one v1.10.0 PR with five-commit stack, matching v1.9.0's pattern for reviewability.

## 2. Context

v1.9.0 explicitly deferred these items (see `investing-toolkit/ROADMAP.md` v1.9.0 deferred list):

- **ISM PMI**: FRED-side `NAPMHNEI / NAPMHNII` series discontinued ~2023 when ISM pulled free FRED licensing. Alternative = S&P Global PMI (still on FRED) with method-delta caveat.
- **JP JGBi (物価連動国債)**: No free MoF-direct API. Data reaches secondary market via JSDA (日本証券業協会) 公社債店頭売買参考統計値 daily CSV, covering 2008-03-25 onward. BOJ 統計時系列 DB does NOT include JGBi (probed 2026-04-18).
- **Swap spread**: Post-LIBOR (2023), FRED's clean 10Y USD swap series (`ICERATES1100USD10Y` etc.) discontinued. SOFR swap curve not cleanly published on FRED. Fallback = Treasury-SOFR 3M spread as money-market liquidity proxy.

**MacroMicro rejected** as data source: ToS Section 1 (繞過技術防護禁止), Section 11 (嚴禁下載數據), Section 7 (禁止再分發) conflict with open-source plugin distribution; 403 bot block on public pages confirms technical countermeasure in place. Only compliant use = URL link reference (per ToS footer 「歡迎分享本網站提供之資訊連結」).

## 3. Scope — Single v1.10.0 PR, five commits

### 3.1 Commit 1 — Item 1: S&P Global PMI via FRED

**Files modified**:
- `investing-toolkit/scripts/` — none (FRED CSV path unchanged)
- `investing-toolkit/skills/us-macro/SKILL.md` — add `pmi` group; description bumped to 13 groups / ~31 series
- `investing-toolkit/skills/us-macro/references/us-macro-indicators.md` — add PMI section with ISM delta note

**Data**:
- Primary: S&P Global US Manufacturing PMI + Services PMI — probe actual live FRED series IDs at implementation (`USAPMIM` / similar)
- Fallback 1: `USALOLITOAASTSAM` (OECD CLI, already in us-macro v1.7.0 `nowcast` group — correlation ~0.85 with ISM manufacturing)
- Fallback 2: `NAPMPI` (historical, discontinued after ~2023) — flagged "stale"

**Signal thresholds (for Block 1)**: `>52` Expansion / `50-52` Near-neutral / `<50` Contraction

**Reference note content**:
- Explain ISM 2023 FRED discontinuation (licensing retraction)
- S&P Global vs ISM: different sample, different questionnaire methodology; correlation ~0.85 on direction, absolute values can differ by ±2-3 points
- URL pointer to `https://www.ismworld.org/` for manual ISM cross-check (link only, no scraping)
- URL pointer to MacroMicro ISM chart page as optional visual reference (link only, not scraped)

### 3.2 Commit 2 — Item 2: JSDA client + JP real-rates

**Files added**:
- `investing-toolkit/scripts/jsda_client.py` — new client (synced to skill)

**Files modified**:
- `investing-toolkit/skills/japan-macro/SKILL.md` — new `real-rates` group, bumped to 24 indicators / 13 groups
- `investing-toolkit/skills/japan-macro/references/indicators-japan-real-rates.md` — new reference file (JGBi explanation, BEI methodology)
- `investing-toolkit/skills/macro-regime-snapshot/references/thresholds-japan.md` — Real Rate Decomposition section rewrite (was "Not available")

**jsda_client.py API**:
```python
def fetch_daily_reference(date: str | None = None) -> pd.DataFrame:
    # date=None → latest business day
    # auto-fallback on 404 to prior business day
    # Returns columns: 銘柄コード, 銘柄名, 償還年月, 利率, 参考値(利回り)

def fetch_jgbi_series(years: int = 5) -> pd.DataFrame:
    # Filter rows where 銘柄名 contains "物価連動"
    # Select current 10Y benchmark (longest outstanding to maturity ≤ 10)
    # Returns: date-indexed real yield time-series

def compute_bei(years: int = 5) -> pd.DataFrame:
    # BEI = JGB 10Y nominal − JGBi 10Y real
    # JGB 10Y nominal sourced from existing boj_client.py or FRED IRLTLT01JPM156N
    # Returns: date, nominal_10y, real_10y, bei_10y
```

**Data source**:
- URL pattern: `https://market.jsda.or.jp/shijyo/saiken/baibai/baisanchi/files/S{YYMMDD}.csv` (probe exact format at implementation)
- Archive listing: `archive2024.html`, `archive2025.html` for history backfill
- Coverage: 2008-03-25 onward (PDF pre-dates 2008-03-25 and 2026-04-01 PDF discontinuation is CSV-only — not affected)

**Group presets**:
- `real-10y` — JGBi 10Y secondary market real yield
- `nominal-10y` — JGB 10Y nominal (boj_client `GBNJR10` or FRED IRLTLT01JPM156N)
- `bei-10y` — computed breakeven
- `real-rate-signal` — categorical (Accommodative / Neutral / Restrictive)

**thresholds-japan.md — Real Rate Decomposition section**:
- Replace "Not available" with: "Available via JSDA path as of v1.10.0"
- BOJ r* anchor (−0.25%, from v1.9.0 grounding audit)
- Thresholds (looser than US by 75 bp due to JP r* being ~75 bp below US):
  - Real rate < 0% → Accommodative
  - 0% ≤ Real rate < 1.0% → Neutral
  - Real rate ≥ 1.0% → Restrictive
- Note absence of direct 5Y JGBi benchmark (only 10Y is liquid); 5Y omitted by design

### 3.3 Commit 3 — Item 3: US swap spread

**Files modified**:
- `investing-toolkit/skills/us-macro/SKILL.md` — new `swap-spreads` group, bumped to 14 groups / ~32-33 series
- `investing-toolkit/skills/us-macro/references/us-macro-indicators.md` — Swap Spread section with threshold provenance

**Data source**:
- Primary attempt: FRED OIS series + Treasury series (e.g., `SOFR30DAYAVG` daily minus `DGS3MO`, or long-end proxy if available)
- Fallback: **Treasury-SOFR 3M spread** = `DGS3MO − SOFR` as money-market liquidity proxy; note in reference "no direct 10Y swap spread — T-SOFR 3M is liquidity proxy, not term-structure swap spread"

**Signal thresholds** (based on 2010-2025 history):
- `< 20 bp` → Normal
- `20-50 bp` → Elevated
- `> 50 bp` → Stressed (exceeded in 2008 GFC, 2020 COVID, 2023 SVB)

### 3.4 Commit 4 — macro-regime-snapshot integration

**Files modified**:
- `investing-toolkit/skills/macro-regime-snapshot/SKILL.md`
- `investing-toolkit/skills/macro-regime-snapshot/references/investment-clock-cheatsheet.md`

**Changes**:
- **Block 1 (Macro Summary)** — add PMI row per country:
  - US: S&P Global composite
  - JP: 景気動向指数 CI 's PMI-proxy components already there; mark N/A + link to Jibun Bank Japan PMI if available
  - TW/KR/CN: N/A + reference URL
- **Block 4 (rename: Rate Stress Dashboard)**:
  - US sub-block: Real Rate Decomposition (unchanged from v1.9.0) + new Swap Spread sub-block
  - JP sub-block: new Real Rate Decomposition (from Commit 2) — no swap spread (no OIS-like free data)
  - TW/KR/CN sub-blocks: N/A notes preserved from v1.9.0
- **cheatsheet**: add PMI signal glossary + swap spread threshold provenance table

### 3.5 Commit 5 — plugin-level sync

**Files modified**:
- `investing-toolkit/skills/using-investing-toolkit/SKILL.md` — us-macro row (~31 series incl. pmi + swap-spreads), japan-macro row (24 indicators / 13 groups incl. real-rates), macro-regime-snapshot row (5-country IC+GIP + real-rate US+JP + swap-spread US)
- `investing-toolkit/README.md` — v1.10.0 Version Highlights entry
- `investing-toolkit/ROADMAP.md` — v1.10.0 entry (current), demote v1.9.0
- `investing-toolkit/.claude-plugin/plugin.json` — `"version": "1.9.0"` → `"1.10.0"`

## 4. Data Flow

```
Item 1 (PMI):
  FRED (S&P Global series) → fred_client.py (existing)
  → us-macro skill `pmi` group → macro-regime-snapshot Block 1 row

Item 2 (JP real rates):
  JSDA daily CSV → jsda_client.py (new)
      ↓
  JGBi 10Y real ─┐
  JGB 10Y nominal (boj_client.py existing) ─┤
                 ↓
      japan-macro skill `real-rates` group
                 ↓
      macro-regime-snapshot Block 4 JP sub-block

Item 3 (US swap spread):
  FRED (OIS / SOFR / Treasury series) → fred_client.py
  → us-macro skill `swap-spreads` group
  → macro-regime-snapshot Block 4 US sub-block (next to real-rate)
```

## 5. Error Handling

- **JSDA 404 on non-business day** → client auto-fallback to prior business day (max 7 day retry)
- **FRED series discontinued mid-release** (e.g. S&P Global changes licensing) → document fallback in reference note; Block 1 shows last-valid date + "stale since" flag
- **Missing JGBi liquidity for 5Y tenor** → explicit design choice, only 10Y exposed; reference note explains
- **Swap spread fallback** (no direct 10Y swap) → use T-SOFR 3M as proxy with explicit reference note about term-structure limitation

## 6. Testing & Verification

Per-commit manual verification:

| Commit | Command / Check |
|--------|-----------------|
| 1 | `uv run scripts/fred_client.py --series <PMI_series_id> --periods 24` returns ≥ 20 months of recent data |
| 2 | `uv run scripts/jsda_client.py --date 2026-04-17` returns non-empty JGBi row; `--jgbi-series --years 5` returns monthly real yield; `--bei --years 5` returns 3-column output |
| 3 | `uv run scripts/fred_client.py --series <swap_spread_proxy> --periods 24` returns clean series |
| 4 | `/invest-macro --region us` shows PMI row + swap spread sub-block; `/invest-macro --region japan` shows real-rate block |
| 5 | `bash scripts/sync-scripts.sh && bash scripts/sync-check.sh` exit 0; `plugin.json` version = 1.10.0 |

Global check before PR:
```bash
cd investing-toolkit
bash scripts/sync-scripts.sh && bash scripts/sync-check.sh
cat .claude-plugin/plugin.json | python3 -c "import sys, json; print(json.load(sys.stdin)['version'])"
# Expected: 1.10.0
```

## 7. Explicit Non-Goals (v1.10.0)

- **No KR KTBi integration** — requires ECOS API key registration; defer to v1.10.1 or v1.11.0
- **No CN / TW real-rate blocks** — no developed inflation-linked bond market; remains "not available" with explanation
- **No MacroMicro integration** — ToS conflicts (see §2)
- **No ISM direct paid API** — out of scope for free-tier toolkit
- **No JP PMI (Jibun Bank)** — licensed, not freely fetched; URL reference only if added to cheatsheet
- **No investing-team standards update** — data layer only

## 8. Branch + PR Plan

```
Branch: feat/regime-pmi-jgbi-swap-v1.10.0
PR title: feat(investing-toolkit): v1.10.0 PMI + JP real-rates + swap spread
PR base: main
Stack: 5 commits (as §3)
```

## 9. Self-Review

- **Placeholder scan**: §3.1 and §3.3 intentionally leave exact FRED series IDs unresolved — will be probed at implementation (Commit 1 verification step). This is a known-unknown, not a placeholder; fallback logic documented.
- **Internal consistency**: five-commit structure matches v1.9.0 pattern; per-item files isolated cleanly; no cross-commit file overlap except in §3.4 which explicitly integrates.
- **Scope check**: 3 items, single PR, one week of v1.9.0 backlog — appropriately sized. Larger than v1.8.1 (single skill), smaller than v1.9.0 (whole regime skill rewrite + 5-country grounding).
- **Ambiguity check**:
  - "Rename Block 4 to Rate Stress Dashboard" — decided: yes, rename; update SKILL.md consistently.
  - "JP 5Y JGBi" — decided: out of scope (illiquid), 10Y only.
  - "Swap spread term" — decided: T-SOFR 3M proxy if no 10Y clean; reference explains limitation.

## 10. Deferred to v1.10.1 / v1.11.0+

- KR KTBi + full BOK ECOS API integration (~4-5 hours, requires API key)
- JP Jibun Bank PMI (licensed)
- CN/TW real-rate blocks (no free data path)
- Swap spread extension to 10Y term-structure (requires licensed data)
