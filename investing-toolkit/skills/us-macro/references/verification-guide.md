# US Macro Indicator Verification Guide

How to verify and maintain the 8 FRED series used by the us-macro skill.

---

## 1. Verify all series return data

```bash
cd investing-toolkit/scripts

for series in T10Y2Y DGS10 DGS2 FEDFUNDS CPIAUCSL CPILFESL GDPC1 INDPRO; do
  uv run fred_client.py --series "$series" --periods 3 --no-cache 2>&1 | \
    python3 -c "
import json, sys
d = json.load(sys.stdin)
l = d.get('latest') or {}
pv = d.get('_provenance') or {}
err = d.get('error', '')
if err:
    print(f'$series: ERROR - {err}')
else:
    print(f'$series: date={l.get(\"date\",\"???\")}  value={l.get(\"value\",\"\")}  staleness={pv.get(\"staleness_days\",\"?\")}d')
"
done
```

**Expected staleness by frequency:**

| Frequency | Series | Expected Staleness |
|-----------|--------|-------------------|
| Daily | T10Y2Y, DGS10, DGS2 | < 5 days |
| Monthly | FEDFUNDS, CPIAUCSL, CPILFESL, INDPRO | < 60 days |
| Quarterly | GDPC1 | < 200 days (advance estimate ~1 month after quarter-end) |

---

## 2. Verify FRED CSV endpoint is accessible

FRED CSV endpoint requires no API key:

```bash
# Quick connectivity check
curl -sS "https://fred.stlouisfed.org/graph/fredgraph.csv?id=DGS10" | tail -3
```

If this fails, check:
- FRED may be temporarily down (rare)
- Network/firewall blocking fred.stlouisfed.org
- FRED may have changed their CSV endpoint URL (check https://fred.stlouisfed.org)

---

## 3. Verify series IDs are still valid

FRED occasionally retires or renames series. To check a series exists:

```bash
# If this returns data, the series is valid
curl -sS "https://fred.stlouisfed.org/graph/fredgraph.csv?id={SERIES_ID}" | head -3
```

If a series is retired, FRED usually provides a successor. Check:
https://fred.stlouisfed.org/series/{SERIES_ID}

---

## 4. Add a new FRED series

**Step 1: Find the series ID**

Browse https://fred.stlouisfed.org or search:
```bash
# FRED doesn't have a search API without key, but you can check if a series exists:
curl -sS "https://fred.stlouisfed.org/graph/fredgraph.csv?id={CANDIDATE_ID}" | head -5
```

**Step 2: Verify data quality**

```bash
uv run fred_client.py --series {NEW_SERIES} --periods 12 --no-cache
```

Check: reasonable values, recent dates, no excessive gaps.

**Step 3: Add to us-macro skill**

1. Update `us-macro/SKILL.md` — add to the appropriate group (rates/inflation/growth)
2. Update `us-macro/references/us-macro-indicators.md` — add full indicator entry
3. No code change needed in `fred_client.py` (it accepts any FRED series ID)

---

## 5. Key differences from Japan verification

| | US (FRED) | Japan (e-Stat) |
|---|---|---|
| Series discovery | Browse fred.stlouisfed.org | API getIndicatorInfo |
| Series retirement risk | Low (FRED rarely retires) | Medium (surveys get restructured) |
| API key needed | No (CSV endpoint) | No (統計ダッシュボード) |
| Frequency verification | Not needed (FRED metadata on website) | Needed (some codes are year-only) |
| Code format | Short string (DGS10) | 19-digit number (0703010501010030000) |

---

## Latest Verification Record

**Date**: 2026-04-17
**Verified by**: automated script
**Result**: All 8 FRED series returning current data via CSV endpoint.

| Series | Full Name | Frequency | Latest Date | Latest Value | Staleness |
|--------|-----------|-----------|-------------|-------------|-----------|
| T10Y2Y | 10Y-2Y Treasury Spread | Daily | 2026-04-16 | 0.54% | 1d |
| DGS10 | 10-Year Treasury Yield | Daily | 2026-04-15 | 4.29% | 2d |
| DGS2 | 2-Year Treasury Yield | Daily | 2026-04-15 | 3.76% | 2d |
| FEDFUNDS | Effective Fed Funds Rate | Monthly | 2026-03-01 | 3.64% | 47d |
| CPIAUCSL | CPI All Items | Monthly | 2026-03-01 | 330.293 | 47d |
| CPILFESL | Core CPI (less food & energy) | Monthly | 2026-03-01 | 334.165 | 47d |
| GDPC1 | Real GDP | Quarterly | 2025-10-01 | $24,055.7B | 198d |
| INDPRO | Industrial Production Index | Monthly | 2026-03-01 | 101.79 | 47d |

**Notes:**
- GDPC1 staleness 198d is normal for quarterly data (Q4 2025 advance estimate)
- FRED CSV endpoint confirmed working without API key
- All series IDs valid, no retirements detected
