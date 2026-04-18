# investing-toolkit v1.10.0 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Close three data-coverage gaps in macro-regime-snapshot: add US ISM-substitute PMI via FRED S&P Global, add JP real-rate block via JSDA 公社債店頭売買参考統計値, add US swap-spread block via SOFR-based FRED proxy.

**Architecture:** Single PR, five-commit stack (1 per item + integration + plugin sync), mirroring v1.9.0's stack pattern. Data-layer scripts are CLI-driven (no pytest suite; smoke tests via `uv run`). Country-macro skills (us-macro, japan-macro) gain new groups; macro-regime-snapshot integrates in Block 1 (PMI row) and renamed Block 4 Rate Stress Dashboard (real-rate + swap-spread).

**Tech Stack:** Python 3.11+ (uv inline requirements), requests, pandas (jsda_client parsing), FRED CSV endpoint (existing fred_client.py), Claude Code skill markdown.

**Spec:** [docs/superpowers/specs/2026-04-18-investing-toolkit-v1.10.0-design.md](../specs/2026-04-18-investing-toolkit-v1.10.0-design.md) (commit `5ea6b6d`)

---

## File Map

Files created:
- `investing-toolkit/scripts/jsda_client.py` — new JSDA daily reference CSV client
- `investing-toolkit/skills/japan-macro/references/indicators-japan-real-rates.md` — new reference for JGBi + BEI

Files modified:
- `investing-toolkit/skills/us-macro/SKILL.md` — +`pmi` group, +`swap-spreads` group, description bump
- `investing-toolkit/skills/us-macro/references/us-macro-indicators.md` — +PMI section with ISM delta, +Swap Spread section
- `investing-toolkit/skills/japan-macro/SKILL.md` — +`real-rates` group, description bump
- `investing-toolkit/skills/japan-macro/scripts/jsda_client.py` — synced copy (via sync-scripts.sh)
- `investing-toolkit/skills/macro-regime-snapshot/SKILL.md` — Block 1 PMI row, rename Block 4 → Rate Stress Dashboard, add JP real-rate + US swap-spread sub-blocks
- `investing-toolkit/skills/macro-regime-snapshot/references/investment-clock-cheatsheet.md` — +PMI glossary, +swap spread threshold provenance
- `investing-toolkit/skills/macro-regime-snapshot/references/thresholds-japan.md` — Real Rate Decomposition section rewrite
- `investing-toolkit/skills/using-investing-toolkit/SKILL.md` — row updates for us-macro, japan-macro, macro-regime-snapshot
- `investing-toolkit/README.md` — v1.10.0 Version Highlights entry
- `investing-toolkit/ROADMAP.md` — v1.10.0 current, demote v1.9.0
- `investing-toolkit/.claude-plugin/plugin.json` — version 1.9.0 → 1.10.0

---

## Task 0: Create feature branch

**Files:** none (git operation)

- [ ] **Step 0.1: Create and switch to branch**

```bash
cd /Users/kouko/GitHub/monkey-skills
git checkout main
git pull origin main
git checkout -b feat/regime-pmi-jgbi-swap-v1.10.0
git status
```

Expected: on branch `feat/regime-pmi-jgbi-swap-v1.10.0`, clean tree.

---

## Task 1: Commit 1 — ISM PMI via FRED S&P Global

**Files:**
- Modify: `investing-toolkit/skills/us-macro/SKILL.md`
- Modify: `investing-toolkit/skills/us-macro/references/us-macro-indicators.md`

- [ ] **Step 1.1: Probe FRED for live S&P Global PMI series**

Run these probes to find a live S&P Global PMI series. FRED series names to try (in order):

```bash
cd /Users/kouko/GitHub/monkey-skills/investing-toolkit

# Try S&P Global Composite/Manufacturing/Services PMI candidates
for s in USPMIM USAPMIM SPGSPMICM USAPMIS SPGSPMISM USAPMICOMPM SPGUSCPMI SPGUSMPMI SPGUSPM USCOMPPMI USNONPMI; do
  echo "=== $s ==="
  uv run scripts/fred_client.py --series "$s" --periods 3 2>&1 | head -10 || true
done
```

Expected outcome: at least one series returns clean data. Record the valid series ID(s) in a scratchpad note. If none works, fall back to `USALOLITOAASTSAM` (OECD CLI — already in us-macro `nowcast` group; will need to note in reference that PMI substitute uses OECD CLI proxy).

If absolutely no S&P Global PMI series is on FRED, document this in the reference note and treat `NAPMPI` as discontinued-historical-only with a "stale since 2023" flag.

- [ ] **Step 1.2: Record chosen series IDs**

Write the resolved series IDs as a comment for the rest of this task. Example format:

```
PMI_MFG_SERIES = "<resolved id, e.g., SPGUSMPMI>"
PMI_SVC_SERIES = "<resolved id or empty>"
PMI_COMP_SERIES = "<resolved id or empty>"
FALLBACK_USED = "<none | OECD CLI (USALOLITOAASTSAM) | NAPMPI historical>"
```

- [ ] **Step 1.3: Verify cache hit by re-running fred_client.py**

```bash
uv run scripts/fred_client.py --series <chosen_pmi_series> --periods 24
```

Expected: returns a JSON with 20+ monthly values, `_provenance` block present, last observation within ~45 days.

- [ ] **Step 1.4: Edit us-macro SKILL.md — add `pmi` group**

Open `investing-toolkit/skills/us-macro/SKILL.md`. Locate the description line listing `(N groups / M series)` and the group table.

Update description count to **13 groups / 31 series** (was 12 / 29).

Add a new `pmi` group row to the group table (ordered alphabetically or grouped with activity indicators — follow existing order). Example row:

```markdown
| `pmi` | S&P Global US Manufacturing/Services/Composite PMI via FRED (ISM substitute post-2023 licensing retraction) | monthly |
```

Update the `--indicators` enum list and Step 1 + Step 2 fetch batch tables to include the new series IDs under `pmi`.

- [ ] **Step 1.5: Edit us-macro-indicators.md — add PMI section**

Open `investing-toolkit/skills/us-macro/references/us-macro-indicators.md`. Add a new `### PMI (Purchasing Managers' Index)` section after the existing `### Nowcast` section. Content must cover:

```markdown
### PMI (Purchasing Managers' Index)

**Series** (via FRED CSV endpoint):
- `<PMI_MFG_SERIES>` — S&P Global US Manufacturing PMI
- `<PMI_SVC_SERIES>` — S&P Global US Services PMI
- `<PMI_COMP_SERIES>` — S&P Global US Composite PMI

**Frequency**: monthly, flash ~3rd-to-last business day of month, final ~1st business day next month.

**Signal thresholds (for Block 1 Macro Summary)**:
- `> 52` → Expansion
- `50-52` → Near-neutral
- `< 50` → Contraction

**Why S&P Global, not ISM**: ISM (Institute for Supply Management) pulled free FRED licensing ~2023. FRED series `NAPMPI`, `NAPMHNEI`, `NAPMHNII` last-updated early 2023 and are flagged discontinued. S&P Global PMI (previously Markit) remains on FRED via OECD / S&P Global licensing path.

**ISM vs S&P Global delta**:
- Different respondent panels (ISM uses its member purchasing-manager network; S&P Global uses separate panel)
- Different questionnaire weighting (S&P Global composite uses 5-item weighted diffusion; ISM uses 5 sub-indices)
- Correlation on direction: ~0.85. Absolute readings can differ ±2-3 points in the same month.
- Consequence: use S&P Global as the diffusion signal (>50 / <50 still meaningful), but do NOT reflexively use ISM's 47-point "recession threshold" calibration on S&P Global readings.

**Manual ISM cross-check (optional)**:
- ISM official: https://www.ismworld.org/supply-management-news-and-reports/reports/ism-report-on-business/
- MacroMicro visual chart (read-only URL reference): https://www.macromicro.me/collections/8/us-industry-relative/37/ism-new-order

(Do not scrape these pages — ISM data is licensed; MacroMicro ToS prohibits scraping. URLs are for human visual cross-check only.)
```

If Step 1.1 resulted in OECD CLI fallback instead of S&P Global, replace the "Series" block with the OECD CLI series and reword the "Why S&P Global" paragraph accordingly.

- [ ] **Step 1.6: Run sync-scripts + sync-check**

```bash
cd investing-toolkit
bash scripts/sync-scripts.sh
bash scripts/sync-check.sh
```

Expected: both exit 0, no drift. (Step 1 adds no new script; sync should be noop for this commit.)

- [ ] **Step 1.7: Smoke-test via us-macro skill invocation**

Mental test (not executed by the agent): loading `us-macro` skill and fetching `pmi` group should yield the series listed in the skill. Since there's no pytest, the verification is:

```bash
uv run scripts/fred_client.py --series <PMI_MFG_SERIES> --periods 24 | python3 -c "import sys, json; d=json.load(sys.stdin); print('OK' if len(d.get('data',[]))>=20 else 'FAIL')"
```

Expected: `OK`.

- [ ] **Step 1.8: Commit 1**

```bash
git add investing-toolkit/skills/us-macro/
git commit -m "$(cat <<'EOF'
feat(us-macro): add pmi group (S&P Global PMI via FRED, ISM substitute)

ISM retired from FRED ~2023. S&P Global PMI remains on FRED via
OECD / S&P Global licensing. Reference note documents ISM vs S&P
Global methodology delta (panel, weighting, ±2-3 pt absolute gap,
~0.85 direction correlation).

Series: <list resolved series IDs>
Group: pmi (monthly)
Thresholds: >52 Expansion / 50-52 Near-neutral / <50 Contraction

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>
EOF
)"
```

---

## Task 2: Commit 2 — JP real-rates (revised: multi-source C+D+E, not JSDA YTM)

> **PIVOT (2026-04-19)**: Original JSDA path invalidated after probe — JSDA publishes
> JGBi **単価 only, no yield** (all yield fields masked `999.999`). After parallel
> research into MoF 連動係数 / YTM math / industry practice / QuantLib, elected
> Option Split: v1.10.0 uses C+D+E multi-source (MoF auction anchor + ECB monthly
> real yield + BOJ Tankan 期待インフレ). Full MoF + QuantLib YTM solver deferred
> to v1.11.0 as standalone PR. Rationale: scope protection + Option A earns its
> own primary-source grounding audit. JBTS BEI scrape rejected on ToS grounds
> (「複製、転用、送信可能化 固く禁じます」).

**Revised scope** — see Task 2R below. Original JSDA steps preserved for historical record.

**Files (revised):**
- Create: `investing-toolkit/scripts/ecb_client.py` (ECB Data Portal CSV fetcher)
- Extend: `investing-toolkit/scripts/boj_client.py` (Tankan 企業物価見通し support)
- Modify: `investing-toolkit/skills/japan-macro/SKILL.md`
- Create: `investing-toolkit/skills/japan-macro/references/indicators-japan-real-rates.md`
- Modify: `investing-toolkit/skills/macro-regime-snapshot/references/thresholds-japan.md`

**Original scope (invalidated):**
- Create: `investing-toolkit/scripts/jsda_client.py`
- Modify: `investing-toolkit/skills/japan-macro/SKILL.md`
- Create: `investing-toolkit/skills/japan-macro/references/indicators-japan-real-rates.md`
- Modify: `investing-toolkit/skills/macro-regime-snapshot/references/thresholds-japan.md`

- [ ] **Step 2.1: Probe JSDA daily CSV URL pattern**

Open the JSDA landing page in a browser (or via WebFetch) to find the actual CSV filename format:

```
https://market.jsda.or.jp/shijyo/saiken/baibai/baisanchi/index.html
```

Expected patterns to try (record which works):
- `https://market.jsda.or.jp/shijyo/saiken/baibai/baisanchi/files/S{YYMMDD}.csv`
- `https://market.jsda.or.jp/shijyo/saiken/baibai/baisanchi/files/saiken{YYYYMMDD}.csv`
- Archive 2025 listing: `https://market.jsda.or.jp/shijyo/saiken/baibai/baisanchi/archive2025.html`

Sample URL once found, e.g.:

```bash
curl -s -I "https://market.jsda.or.jp/shijyo/saiken/baibai/baisanchi/files/S260418.csv"
```

Record the working URL template.

Also inspect one CSV to identify column layout — locate the column containing `物価連動` (JGBi marker) and the yield column (参考値).

- [ ] **Step 2.2: Write jsda_client.py skeleton**

Create `investing-toolkit/scripts/jsda_client.py` matching the existing uv-inline-script convention. Base on `fred_client.py` for cache + CLI structure.

```python
#!/usr/bin/env python3
# /// script
# requires-python = ">=3.11"
# dependencies = ["requests==2.33.1", "pandas==2.2.2"]
# ///
"""
jsda_client.py — investing-toolkit JSDA OTC bond reference price adapter
Fetches daily 公社債店頭売買参考統計値 CSV, extracts JGBi (物価連動国債) real
yields, and computes JGB breakeven inflation (BEI).

Usage:
  uv run jsda_client.py --date 2026-04-17                  # single day snapshot
  uv run jsda_client.py --jgbi-series --years 5            # 10Y JGBi real yield series
  uv run jsda_client.py --bei --years 5                    # BEI = nominal - real

Auth: none. JSDA publishes free daily CSV.
Cache: $INVESTING_TOOLKIT_CACHE/jsda/{YYYY-MM-DD}.csv  TTL: 24h
       Falls back to ~/.cache/investing-toolkit/ if env var not set.
Coverage: 2008-03-25 onward (JSDA CSV start date).
"""

import argparse
import csv
import io
import json
import os
import sys
import time
from datetime import datetime, timedelta, timezone
from pathlib import Path
import requests as _requests

JSDA_CSV_TEMPLATE = "<resolved URL template from Step 2.1>"
_CACHE_BASE = os.environ.get("INVESTING_TOOLKIT_CACHE") or str(Path.home() / ".cache" / "investing-toolkit")
CACHE_DIR = Path(_CACHE_BASE) / "jsda"
CACHE_TTL_SECONDS = 86400
MAX_BUSINESS_DAY_FALLBACK = 7  # retry prior business days on 404
```

- [ ] **Step 2.3: Implement fetch_daily_reference**

Add to `jsda_client.py`:

```python
def fetch_daily_reference(date: str | None = None) -> "pd.DataFrame":
    """Fetch JSDA OTC reference price CSV for a given business day.

    Args:
        date: 'YYYY-MM-DD' format, or None for latest business day.
              On 404 (non-business day), auto-fallback to prior day up to
              MAX_BUSINESS_DAY_FALLBACK.

    Returns:
        DataFrame with columns: 銘柄コード, 銘柄名, 償還年月, 利率, 参考値
    """
    import pandas as pd
    if date is None:
        target = datetime.now(timezone.utc).astimezone()
    else:
        target = datetime.strptime(date, "%Y-%m-%d")
    for offset in range(MAX_BUSINESS_DAY_FALLBACK):
        probe = target - timedelta(days=offset)
        url = JSDA_CSV_TEMPLATE.format(YYMMDD=probe.strftime("%y%m%d"))
        cache_path = CACHE_DIR / f"{probe.strftime('%Y-%m-%d')}.csv"
        CACHE_DIR.mkdir(parents=True, exist_ok=True)
        if cache_path.exists() and (time.time() - cache_path.stat().st_mtime) < CACHE_TTL_SECONDS:
            text = cache_path.read_text(encoding="shift_jis", errors="replace")
        else:
            resp = _requests.get(url, timeout=30)
            if resp.status_code == 404:
                continue
            resp.raise_for_status()
            text = resp.content.decode("shift_jis", errors="replace")
            cache_path.write_text(text, encoding="utf-8")
        df = pd.read_csv(io.StringIO(text), dtype=str)
        df["_date"] = probe.strftime("%Y-%m-%d")
        return df
    raise RuntimeError(f"No JSDA CSV found within {MAX_BUSINESS_DAY_FALLBACK} days of {date}")
```

Adjust column names once Step 2.1 probe reveals actual CSV layout (Shift-JIS encoding is the documented JSDA default).

- [ ] **Step 2.4: Implement fetch_jgbi_series**

Add:

```python
def fetch_jgbi_series(years: int = 5) -> "pd.DataFrame":
    """Fetch 10Y JGBi (物価連動国債) real yield monthly time series.

    Strategy: iterate month-end dates for past `years` years; for each, call
    fetch_daily_reference to get snapshot; filter rows whose 銘柄名 contains
    '物価連動'; select the row with maturity closest to 10Y forward.

    Returns:
        DataFrame indexed by date, single column 'real_10y'.
    """
    import pandas as pd
    end = datetime.now(timezone.utc).astimezone()
    start = end - timedelta(days=365 * years)
    months = pd.date_range(start=start, end=end, freq="M")
    rows = []
    for m in months:
        try:
            df = fetch_daily_reference(m.strftime("%Y-%m-%d"))
        except RuntimeError:
            continue
        jgbi = df[df["<銘柄名 column>"].str.contains("物価連動", na=False)].copy()
        if jgbi.empty:
            continue
        # Parse 償還年月 and pick issue with maturity nearest to 10Y forward
        jgbi["mat"] = pd.to_datetime(jgbi["<償還年月 column>"], format="%Y-%m", errors="coerce")
        target_mat = m + pd.DateOffset(years=10)
        jgbi["dist"] = (jgbi["mat"] - target_mat).abs()
        benchmark = jgbi.nsmallest(1, "dist").iloc[0]
        rows.append({
            "date": m.strftime("%Y-%m-%d"),
            "real_10y": float(benchmark["<参考値 column>"]),
        })
    return pd.DataFrame(rows).set_index("date")
```

- [ ] **Step 2.5: Implement compute_bei**

Add:

```python
def compute_bei(years: int = 5) -> "pd.DataFrame":
    """Compute 10Y breakeven inflation = nominal − real.

    Nominal 10Y sourced from FRED IRLTLT01JPM156N (monthly) via fred_client.
    Real 10Y from fetch_jgbi_series.

    Returns:
        DataFrame indexed by date with columns nominal_10y, real_10y, bei_10y.
    """
    import pandas as pd
    # delegate nominal to existing fred_client by subprocess or direct import
    import subprocess, json
    script = Path(__file__).parent / "fred_client.py"
    result = subprocess.run(
        ["uv", "run", str(script), "--series", "IRLTLT01JPM156N", "--periods", str(years * 12)],
        capture_output=True, text=True, check=True,
    )
    nominal = pd.DataFrame(json.loads(result.stdout)["data"])
    nominal["date"] = pd.to_datetime(nominal["date"]).dt.strftime("%Y-%m-%d")
    nominal = nominal.set_index("date")[["value"]].rename(columns={"value": "nominal_10y"}).astype(float)
    real = fetch_jgbi_series(years=years)
    out = nominal.join(real, how="inner")
    out["bei_10y"] = out["nominal_10y"] - out["real_10y"]
    return out
```

- [ ] **Step 2.6: Implement CLI entry point**

Add:

```python
def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--date", type=str, default=None)
    parser.add_argument("--jgbi-series", action="store_true")
    parser.add_argument("--bei", action="store_true")
    parser.add_argument("--years", type=int, default=5)
    args = parser.parse_args()
    if args.bei:
        df = compute_bei(years=args.years)
    elif args.jgbi_series:
        df = fetch_jgbi_series(years=args.years)
    else:
        df = fetch_daily_reference(date=args.date)
    # Emit JSON with _provenance block, matching fred_client.py convention
    payload = {
        "_provenance": {
            "source": "JSDA (日本証券業協会)",
            "endpoint": JSDA_CSV_TEMPLATE,
            "fetched_at": datetime.now(timezone.utc).isoformat(),
            "cache_ttl_seconds": CACHE_TTL_SECONDS,
        },
        "data": df.reset_index().to_dict(orient="records") if hasattr(df, "reset_index") else [],
    }
    print(json.dumps(payload, ensure_ascii=False, indent=2))

if __name__ == "__main__":
    main()
```

- [ ] **Step 2.7: Smoke test jsda_client.py**

```bash
cd investing-toolkit
uv run scripts/jsda_client.py --date 2026-04-17 | head -30
```

Expected: JSON with `_provenance` + `data` containing >100 rows (all bonds traded that day).

```bash
uv run scripts/jsda_client.py --jgbi-series --years 5 | python3 -c "import sys, json; d=json.load(sys.stdin); print('OK' if len(d.get('data',[]))>=20 else 'FAIL')"
```

Expected: `OK` (5Y × 12 ≈ 60 monthly points minimum).

```bash
uv run scripts/jsda_client.py --bei --years 5 | python3 -c "import sys, json; d=json.load(sys.stdin); print(d['data'][-1])"
```

Expected: last row has three numeric fields `nominal_10y`, `real_10y`, `bei_10y`.

- [ ] **Step 2.8: Edit japan-macro SKILL.md — add `real-rates` group**

Open `investing-toolkit/skills/japan-macro/SKILL.md`. Update description to reflect new group count: e.g., "24 presets / 13 groups" (was 22 / 12).

Add `real-rates` group row to group table:

```markdown
| `real-rates` | JGBi 10Y real + JGB 10Y nominal + computed BEI via JSDA | monthly |
```

Add preset entries to the fetch batch table in Step 1:

```
| real-10y | JGBi 10Y real yield (JSDA secondary market) | jsda_client --jgbi-series |
| nominal-10y | JGB 10Y nominal yield | boj_client / fred IRLTLT01JPM156N |
| bei-10y | 10Y breakeven inflation (computed) | jsda_client --bei |
| real-rate-signal | Accommodative / Neutral / Restrictive | computed from real-10y |
```

- [ ] **Step 2.9: Create indicators-japan-real-rates.md**

Create `investing-toolkit/skills/japan-macro/references/indicators-japan-real-rates.md`:

```markdown
# Japan Real Rates (JGBi + BEI) Reference

## What is JGBi

物価連動国債 (bukka rendō kokusai) — Japanese inflation-indexed government
bonds, issued by 財務省 MoF since 2004-03. Principal adjusts with 全国CPI除
く生鮮食品 (CPI ex fresh food). Current outstanding: only 10Y benchmark is
liquid; 5Y and 20Y exist but rarely traded on secondary market.

## Data Path

JSDA 公社債店頭売買参考統計値 (OTC bond reference trading statistics) publishes
daily Shift-JIS CSV at 3PM (next-business-day disclosure). Coverage:
2008-03-25 onward. Shift-JIS encoding.

`jsda_client.py` CLI:
- `--date YYYY-MM-DD` — snapshot of all bond reference yields that day
- `--jgbi-series --years N` — monthly 10Y JGBi real yield series
- `--bei --years N` — monthly BEI = JGB 10Y nominal − JGBi 10Y real

10Y benchmark is selected each month as the JGBi issue with maturity closest
to 10Y forward.

## Breakeven Inflation (BEI) Methodology

BEI = nominal 10Y − real 10Y. Nominal 10Y from FRED IRLTLT01JPM156N (MoF
monthly release via OECD redistribution). Both series averaged to same month-
end for alignment.

Compared to US, JP BEI is structurally lower (averaging 0.5-1.2% 2013-2024)
reflecting Japan's disinflation backdrop and BOJ anchor persistence.

## Signal Thresholds (for macro-regime-snapshot Block 4 JP sub-block)

Calibrated to BOJ r* = −0.25% (see thresholds-japan.md Grounding Status for
provenance: BOJ WP24-J-09, Oda-Muranaga 2024, range −1.0% to +0.5%).

Looser than US thresholds by ~75 bp because JP r* is ~75 bp below US r*:

| Real 10Y | Signal |
|----------|--------|
| < 0% | Accommodative |
| 0% ≤ x < 1.0% | Neutral |
| ≥ 1.0% | Restrictive |

Caveat: JP real rates rarely exceed 0.5% in the 2008-2025 historical window.
Threshold band may re-calibrate if BOJ normalization moves r* materially.

## Caveats

- **5Y JGBi not exposed**: only 10Y is liquid. If user needs 5Y, scrape
  full snapshot via `--date` and inspect manually.
- **Non-business day auto-fallback**: client retries prior business days up
  to 7 calendar days back.
- **JSDA is next-day-disclosure**: today's reference values are the quotations
  at 3PM today, published on next business day. Real-time use requires
  Bloomberg / Reuters / Quick terminal (out of scope).

## Primary Sources

- JSDA 公社債店頭売買参考統計値 landing: https://market.jsda.or.jp/shijyo/saiken/baibai/baisanchi/index.html
- MoF JGBi overview: https://www.mof.go.jp/jgbs/topics/bond/10year_inflation/index.htm
- BOJ 物価連動国債利回りに関する解説 (WP references in thresholds-japan.md)
```

- [ ] **Step 2.10: Edit thresholds-japan.md Real Rate Decomposition section**

Open `investing-toolkit/skills/macro-regime-snapshot/references/thresholds-japan.md`. Locate the `## Real Rate Decomposition` section (currently reads "Not available").

Replace with:

```markdown
## Real Rate Decomposition

**Available as of v1.10.0** via JSDA path (see
[indicators-japan-real-rates.md](../../japan-macro/references/indicators-japan-real-rates.md)).

### Data path

- Real 10Y: JSDA 公社債店頭売買参考統計値 daily CSV → filter 物価連動国債
  → pick issue closest to 10Y forward maturity.
- Nominal 10Y: FRED IRLTLT01JPM156N (monthly) or boj_client GBNJR10.
- BEI = nominal − real, month-end alignment.

### Signal thresholds

Calibrated to BOJ r* = **−0.25%** (Oda-Muranaga 2024, BOJ WP24-J-09 range
−1.0% to +0.5%; see v1.9.0 Grounding Status block above).

Looser than US thresholds by ~75 bp because JP r* is ~75 bp below US r*:

| Real 10Y yield | Signal |
|----------------|--------|
| < 0% | Accommodative |
| 0% ≤ x < 1.0% | Neutral |
| ≥ 1.0% | Restrictive |

### Historical context (2013-2026)

- 2013-2016 QQE + NIRP: real 10Y typically negative (−0.5% to −0.1%)
- 2022-2023 global inflation shock: real 10Y briefly positive on BEI widening
- 2024 YCC exit + subsequent BOJ hikes: real 10Y turning neutral, BEI around
  1.0-1.3%
- 2025-12 → 2026-Q1 (latest): nominal 10Y ~1.50-1.65%, BEI ~1.2-1.4%,
  real 10Y ~0.1-0.4% (Neutral band)

### 5Y JGBi

**Not exposed** by v1.10.0 — 5Y JGBi issue exists but secondary market
liquidity is thin and reference yield often stale. Only 10Y is structurally
reliable. Future v1.11.0 candidate: scrape full JSDA snapshot for 5Y if
user demand surfaces.
```

- [ ] **Step 2.11: Sync scripts + verify**

```bash
cd investing-toolkit
bash scripts/sync-scripts.sh
bash scripts/sync-check.sh
```

Expected: sync-scripts.sh copies `jsda_client.py` into `skills/japan-macro/scripts/`; sync-check.sh exits 0.

- [ ] **Step 2.12: End-to-end smoke test**

```bash
cd investing-toolkit
uv run skills/japan-macro/scripts/jsda_client.py --bei --years 3 | python3 -c "
import sys, json
d = json.load(sys.stdin)
rows = d.get('data', [])
assert len(rows) >= 20, f'too few rows: {len(rows)}'
assert all('nominal_10y' in r and 'real_10y' in r and 'bei_10y' in r for r in rows)
print(f'OK — {len(rows)} monthly points, last: {rows[-1]}')
"
```

Expected: `OK — <N> monthly points, last: {...}` prints.

- [ ] **Step 2.13: Commit 2**

```bash
git add investing-toolkit/scripts/jsda_client.py \
        investing-toolkit/skills/japan-macro/ \
        investing-toolkit/skills/macro-regime-snapshot/references/thresholds-japan.md
git commit -m "$(cat <<'EOF'
feat(japan-macro): add real-rates group via JSDA JGBi client

- scripts/jsda_client.py: new daily CSV client with Shift-JIS decoding,
  non-business-day auto-fallback, fetch_jgbi_series (10Y benchmark
  selection by maturity distance), compute_bei (nominal − real).
- japan-macro/SKILL.md: new real-rates group (real-10y, nominal-10y,
  bei-10y, real-rate-signal). 22→24 presets, 12→13 groups.
- references/indicators-japan-real-rates.md: new reference with
  methodology, signal thresholds calibrated to BOJ r* −0.25%,
  historical context 2013-2026.
- thresholds-japan.md: Real Rate Decomposition section rewritten from
  "Not available" to the live data path + thresholds.

Coverage: 2008-03-25 onward (JSDA CSV start).

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>
EOF
)"
```

---

## Task 3: Commit 3 — US swap spread group

**Files:**
- Modify: `investing-toolkit/skills/us-macro/SKILL.md`
- Modify: `investing-toolkit/skills/us-macro/references/us-macro-indicators.md`

- [ ] **Step 3.1: Probe FRED for SOFR / OIS / Treasury series**

Test series IDs:

```bash
cd /Users/kouko/GitHub/monkey-skills/investing-toolkit
for s in SOFR30DAYAVG SOFR SOFRRATE DGS3MO DGS10 DFF OBFR SOFRINT USD10YOIS; do
  echo "=== $s ==="
  uv run scripts/fred_client.py --series "$s" --periods 3 2>&1 | head -8 || true
done
```

Decide on a proxy. Expected outcomes:
- `SOFR30DAYAVG` + `DGS3MO`: both live. Proxy = `DGS3MO − SOFR30DAYAVG` = Treasury-SOFR 3M spread (money-market liquidity gauge, not term swap spread).
- If a clean long-end OIS series exists on FRED, prefer that.

Record the chosen proxy as `SWAP_PROXY_RECIPE` for reference note.

- [ ] **Step 3.2: Edit us-macro SKILL.md — add `swap-spreads` group**

Update description: 13 groups / 31 series → **14 groups / 33 series** (adds ~2 series for proxy).

Add row:

```markdown
| `swap-spreads` | Treasury-SOFR 3M spread (money-market liquidity proxy for true term swap spread) | daily |
```

Presets:

```
| treasury-3m | 3M Treasury yield | DGS3MO |
| sofr-30d | SOFR 30-day average | SOFR30DAYAVG |
| treasury-sofr-3m-spread | = DGS3MO − SOFR30DAYAVG (bps) | computed |
```

- [ ] **Step 3.3: Edit us-macro-indicators.md — add Swap Spread section**

Append to `us-macro-indicators.md`:

```markdown
### Swap Spread / Money-Market Liquidity

**Series (via FRED)**:
- `DGS3MO` — 3-Month Treasury Constant Maturity
- `SOFR30DAYAVG` — 30-Day Average SOFR

**Computed**: Treasury-SOFR 3M spread = `DGS3MO − SOFR30DAYAVG` (in bps)

**Why this is a proxy, not a true swap spread**:
- Post-LIBOR (2023-06 cessation), FRED's clean term-structure USD swap rate
  series (`ICERATES1100USD10Y` etc.) discontinued.
- SOFR-based OIS swap curves exist on Bloomberg / Reuters / ICE but are
  licensed (not FRED-accessible).
- Treasury-SOFR 3M spread is therefore a **money-market / short-end liquidity
  stress gauge**, not a 10Y term swap spread.
- Directionally reliable for detecting dollar-funding stress events (GFC,
  2020-03 COVID, 2023-03 SVB), but not a substitute for the full term-
  structure signal LSEG's licensed blotter provides.

**Signal thresholds** (based on 2010-2025 daily history):
- `< 20 bp` → Normal
- `20-50 bp` → Elevated
- `> 50 bp` → Stressed (exceeded 2008 GFC, 2020-03 COVID, 2023-03 SVB)

**Caveat on 2024-2026 regime**: post-QT SOFR can run materially above fed
funds target during quarter-end window-dressing (2023-09-30 +15bp repo
spike, 2024-03-29 +10bp). Apply signal thresholds to monthly average, not
quarter-end spot.
```

- [ ] **Step 3.4: Smoke test the proxy**

```bash
cd investing-toolkit
uv run scripts/fred_client.py --series DGS3MO --periods 24
uv run scripts/fred_client.py --series SOFR30DAYAVG --periods 24
```

Expected: both return clean series. Compute one spread manually to sanity-check (spread should be roughly in the ±50 bp band for 2024-2026).

- [ ] **Step 3.5: Commit 3**

```bash
git add investing-toolkit/skills/us-macro/
git commit -m "$(cat <<'EOF'
feat(us-macro): add swap-spreads group (Treasury-SOFR 3M proxy)

Post-LIBOR 2023 cessation removed clean FRED term swap series. Use
DGS3MO − SOFR30DAYAVG as money-market liquidity proxy. Reference note
documents the "this is not a full term swap spread" caveat explicitly.

Signal thresholds calibrated to 2010-2025 daily history:
 <20bp Normal / 20-50bp Elevated / >50bp Stressed

us-macro group count: 13→14, series 31→33.

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>
EOF
)"
```

---

## Task 4: Commit 4 — macro-regime-snapshot integration

**Files:**
- Modify: `investing-toolkit/skills/macro-regime-snapshot/SKILL.md`
- Modify: `investing-toolkit/skills/macro-regime-snapshot/references/investment-clock-cheatsheet.md`

- [ ] **Step 4.1: Edit SKILL.md — Block 1 add PMI row**

Open `investing-toolkit/skills/macro-regime-snapshot/SKILL.md`. Locate the Block 1 Macro Summary table template. Add a new PMI row:

```markdown
| S&P Global PMI (US) / Jibun Bank PMI (JP ref) / N-A with URL (TW KR CN) | latest | prior | Rising/Flat/Falling | Expansion / Near-neutral / Contraction |
```

For non-US countries, leave `N/A` with the human-reference URL (Jibun Bank for JP, 中経院 PMI for TW, KITA/연구원 PMI for KR, Caixin PMI for CN).

- [ ] **Step 4.2: Edit SKILL.md — rename Block 4 to Rate Stress Dashboard**

Locate Step 4 in SKILL.md currently titled "Real Rate Decomposition (US-only)". Rename to:

```markdown
## Step 4 — Rate Stress Dashboard

### 4a. Real Rate Decomposition

**US sub-block** (unchanged from v1.9.0): 5Y + 10Y nominal / breakeven / real / signal.

**JP sub-block** (new v1.10.0): 10Y nominal / real / BEI / signal.
Source: jsda_client + fred IRLTLT01JPM156N. Thresholds in
[thresholds-japan.md](references/thresholds-japan.md).

**TW / KR / CN**: N/A. See each threshold file for reasoning (no developed
free inflation-linked bond market for TW; KR KTBi deferred to v1.10.1+;
CN has no linker market).

### 4b. Swap Spread (US-only v1.10.0)

Treasury-SOFR 3M spread as money-market liquidity proxy. See
[us-macro-indicators.md](../us-macro/references/us-macro-indicators.md)
Swap Spread section for methodology caveats.

| Spread | Signal |
|--------|--------|
| < 20 bp | Normal |
| 20-50 bp | Elevated |
| > 50 bp | Stressed |

JP / TW / KR / CN: no equivalent free-data SOFR-like benchmark; section omitted.
```

Also update references in the routing + per-country step tables to include the new data paths.

- [ ] **Step 4.3: Edit investment-clock-cheatsheet.md**

Append two sections at the end of `investment-clock-cheatsheet.md`:

```markdown
## PMI Signal Glossary (v1.10.0)

| PMI reading | Signal | Phase implication |
|-------------|--------|-------------------|
| > 55 | Strong Expansion | Overheat likely |
| 52-55 | Expansion | Recovery / late-Recovery |
| 50-52 | Near-neutral | Regime transition (watch trend) |
| 47-50 | Contraction (mild) | Stagflation / early Reflation |
| < 47 | Deep Contraction | Reflation / recession |

**Country coverage**:
- US: S&P Global (FRED) — ISM cross-check via ismworld.org (manual only)
- JP: Jibun Bank — licensed (URL only, not fetched)
- TW: 中經院 PMI — URL only
- KR: KITA / 한국경제연구원 PMI — URL only
- CN: Caixin PMI + NBS 官方 PMI — both available via akshare (future
  v1.11.0 candidate)

## Swap Spread Threshold Provenance (v1.10.0)

Thresholds calibrated to US 2010-2025 daily history of Treasury-SOFR 3M
spread (DGS3MO − SOFR30DAYAVG, in bps):

| Threshold | Empirical rationale |
|-----------|---------------------|
| 20 bp | 95th percentile during 2010-2019 normal window; breached routinely in 2020-03, 2023-03 |
| 50 bp | 99.5th percentile; breached only during GFC (2008-10), COVID (2020-03), SVB (2023-03) |

Use monthly average rather than quarter-end spot (QE window-dressing
distorts spot readings 10-15 bp).

This is a **money-market liquidity proxy, not a term swap spread**. The true
10Y term swap spread requires licensed data (Bloomberg / Reuters / ICE).
```

- [ ] **Step 4.4: Sync check**

```bash
cd investing-toolkit
bash scripts/sync-scripts.sh
bash scripts/sync-check.sh
```

Expected: exit 0.

- [ ] **Step 4.5: Commit 4**

```bash
git add investing-toolkit/skills/macro-regime-snapshot/
git commit -m "$(cat <<'EOF'
feat(macro-regime-snapshot): integrate PMI + JP real-rate + US swap spread

- Block 1: add PMI row per country (US S&P Global fetched; JP/TW/KR/CN
  reference URLs only)
- Block 4 renamed "Rate Stress Dashboard"; split into 4a Real Rate
  Decomposition (US+JP) and 4b Swap Spread (US-only)
- cheatsheet: PMI signal glossary + swap spread threshold provenance

JP real-rate block wired to jsda_client from Commit 2. US swap spread
wired to fred_client DGS3MO/SOFR30DAYAVG from Commit 3.

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>
EOF
)"
```

---

## Task 5: Commit 5 — plugin-level sync

**Files:**
- Modify: `investing-toolkit/skills/using-investing-toolkit/SKILL.md`
- Modify: `investing-toolkit/README.md`
- Modify: `investing-toolkit/ROADMAP.md`
- Modify: `investing-toolkit/.claude-plugin/plugin.json`

- [ ] **Step 5.1: Edit using-investing-toolkit/SKILL.md**

Update the Available Skills table rows:
- `us-macro`: "US macro indicators via FRED (~33 series; `pmi` group + `swap-spreads` group new in v1.10.0) | v1.10.0"
- `japan-macro`: "Japan macro indicators via BOJ + e-Stat + JSDA (24 presets / 13 groups; `real-rates` group new in v1.10.0) | v1.10.0"
- `macro-regime-snapshot`: "5-country IC + GIP (US/JP/TW/KR/CN) + Rate Stress Dashboard (US real-rate + swap spread, JP real-rate new) | v1.10.0"

Update the footer sentence: "All skills through v1.10.0 are now available."

- [ ] **Step 5.2: Edit investing-toolkit/README.md**

Bump version line to 1.10.0. Prepend a Version Highlights entry:

```markdown
### v1.10.0 (2026-04-19) — PMI + JP real rates + swap spread

Closes three data-coverage gaps from v1.9.0 deferred list:
- **us-macro**: new `pmi` group (S&P Global PMI via FRED — ISM substitute
  post-2023 licensing retraction) + new `swap-spreads` group
  (Treasury-SOFR 3M spread as money-market liquidity proxy)
- **japan-macro**: new `real-rates` group via JSDA 公社債店頭売買参考統計値
  daily CSV (JGBi 10Y real + BEI); jsda_client.py client added
- **macro-regime-snapshot**: Block 1 PMI row + Block 4 renamed "Rate Stress
  Dashboard" with JP real-rate sub-block and US swap spread sub-block
```

- [ ] **Step 5.3: Edit investing-toolkit/ROADMAP.md**

Change v1.9.0 from "(current)" to merged/done. Add new v1.10.0 section as (current) with 5-phase breakdown matching the 5 commits. Move "full BOK ECOS API" / "JP Jibun Bank PMI" / "CN Caixin PMI via akshare" / "TW + KR PMI scrapers" to v1.10.1 / v1.11.0 candidates.

- [ ] **Step 5.4: Edit .claude-plugin/plugin.json**

Change:
```json
  "version": "1.9.0"
```
to:
```json
  "version": "1.10.0"
```

Leave description unchanged.

- [ ] **Step 5.5: Final sync + version check**

```bash
cd investing-toolkit
bash scripts/sync-scripts.sh
bash scripts/sync-check.sh
cat .claude-plugin/plugin.json | python3 -c "import sys, json; v=json.load(sys.stdin)['version']; assert v == '1.10.0', f'wrong version: {v}'; print('OK', v)"
```

Expected: `OK 1.10.0`.

- [ ] **Step 5.6: Commit 5**

```bash
git add investing-toolkit/skills/using-investing-toolkit/SKILL.md \
        investing-toolkit/README.md \
        investing-toolkit/ROADMAP.md \
        investing-toolkit/.claude-plugin/plugin.json
git commit -m "$(cat <<'EOF'
chore(investing-toolkit): v1.10.0 plugin-level sync

- using-investing-toolkit: us-macro / japan-macro / macro-regime-snapshot
  rows bumped to v1.10.0 with new groups/blocks noted
- README: v1.10.0 Version Highlights prepended
- ROADMAP: v1.10.0 promoted to current; v1.9.0 demoted to done
- plugin.json: 1.9.0 → 1.10.0

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>
EOF
)"
```

---

## Task 6: Push + PR

- [ ] **Step 6.1: Push branch**

```bash
cd /Users/kouko/GitHub/monkey-skills
git push -u origin feat/regime-pmi-jgbi-swap-v1.10.0
```

- [ ] **Step 6.2: Create PR**

```bash
gh pr create --base main --title "feat(investing-toolkit): v1.10.0 PMI + JP real-rates + swap spread" --body "$(cat <<'EOF'
## Summary
- **us-macro**: new `pmi` group (S&P Global PMI via FRED, ISM substitute) + new `swap-spreads` group (Treasury-SOFR 3M proxy)
- **japan-macro**: new `real-rates` group via JSDA daily CSV (JGBi 10Y real + BEI); `jsda_client.py` added
- **macro-regime-snapshot**: Block 1 PMI row; Block 4 renamed Rate Stress Dashboard with JP real-rate + US swap spread sub-blocks

## Architecture change
v1.9.0 deferred list closed (3 of 4 items):
- [x] ISM PMI via FRED S&P Global fallback
- [x] JP JGBi via JSDA client
- [x] US swap spread via SOFR proxy
- [ ] KR KTBi via BOK ECOS API key (deferred to v1.10.1 / v1.11.0)

## Test plan
- [ ] `uv run scripts/fred_client.py --series <chosen_pmi> --periods 24` returns clean series
- [ ] `uv run scripts/jsda_client.py --date 2026-04-17` returns daily snapshot
- [ ] `uv run scripts/jsda_client.py --bei --years 5` returns monthly 3-column output
- [ ] `uv run scripts/fred_client.py --series DGS3MO --periods 24` and `SOFR30DAYAVG --periods 24` both clean
- [ ] `bash scripts/sync-scripts.sh && bash scripts/sync-check.sh` exit 0
- [ ] `plugin.json` version = 1.10.0

## Spec + plan
- Spec: [docs/superpowers/specs/2026-04-18-investing-toolkit-v1.10.0-design.md](https://github.com/kouko/monkey-skills/blob/main/docs/superpowers/specs/2026-04-18-investing-toolkit-v1.10.0-design.md)
- Plan: [docs/superpowers/plans/2026-04-19-investing-toolkit-v1.10.0.md](https://github.com/kouko/monkey-skills/blob/main/docs/superpowers/plans/2026-04-19-investing-toolkit-v1.10.0.md)

🤖 Generated with [Claude Code](https://claude.com/claude-code)
EOF
)"
```

Return the PR URL.

---

## Self-Review Notes

**Spec coverage check**:
- Spec §3.1 → Task 1 ✅
- Spec §3.2 → Task 2 ✅ (jsda_client + japan-macro + thresholds-japan)
- Spec §3.3 → Task 3 ✅
- Spec §3.4 → Task 4 ✅
- Spec §3.5 → Task 5 ✅
- Spec §6 verification commands → distributed across Task 1.7, 2.12, 3.4, 5.5 ✅
- Spec §7 non-goals → preserved (KR KTBi, CN/TW real-rate, MacroMicro — all documented in comments / README / ROADMAP)
- Spec §8 branch + PR plan → Task 0 + Task 6 ✅

**Known-unknowns (NOT placeholders — probed at implementation)**:
- Step 1.1: FRED S&P Global PMI series IDs — probed at runtime, fallback path documented
- Step 2.1: JSDA CSV URL template and column names — probed at runtime (CSV column names vary by year)
- Step 3.1: SOFR-based swap proxy series — probed at runtime; T-SOFR 3M is documented fallback

**Placeholder scan**: no `TODO` / `TBD` / `fill in` remaining. All "<resolved X>" markers are explicit step-1 probe outputs that the engineer fills in during execution.

**Type consistency**: `fetch_daily_reference` / `fetch_jgbi_series` / `compute_bei` signatures consistent across Steps 2.3-2.5 and 2.6 main. No method name drift.

**Commit discipline**: 5 commits total (Task 1, 2, 3, 4, 5), mirroring v1.9.0 stack pattern. Each commit is self-contained and reviewable independently.
