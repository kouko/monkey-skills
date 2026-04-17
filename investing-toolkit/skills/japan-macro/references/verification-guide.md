# Japan Macro Indicator Verification Guide / 指標検証ガイド

How to verify, update, and add indicators in the japan-macro skill.

---

## 1. Verify existing presets are still active

Use the `getIndicatorInfo` API to check each preset's indicator code:

```bash
# Check a single indicator
curl -sS "https://dashboard.e-stat.go.jp/api/1.0/Json/getIndicatorInfo?Lang=EN&IndicatorCode={CODE}"
```

**What to check in the response:**
- `toDate`: should be `99991200` (= active, no end date). If it shows a specific date like `20241200`, the survey has been **discontinued**.
- `cycle.name`: should include `Month` for monthly data. If only `Calendar Year` or `Fiscal Year`, the indicator lacks monthly frequency.
- `RegionalRank.name`: should include `Japan` for nationwide data.

**Batch verification script** (run from `investing-toolkit/scripts/`):

```bash
# Verify all presets at once
for preset in cpi core-cpi core-core-cpi unemployment ip jgb10y \
  coincident-index machine-orders real-wages job-ratio \
  tertiary-index retail-sales service-sales; do

  # Extract code from estat_client.py PRESETS dict
  code=$(python3 -c "
import ast, re
with open('estat_client.py') as f: src = f.read()
m = re.search(r'\"$preset\":\s*\"(\d+)\"', src)
print(m.group(1) if m else 'NOT_FOUND')
")

  # Query API metadata
  curl -sS "https://dashboard.e-stat.go.jp/api/1.0/Json/getIndicatorInfo?Lang=EN&IndicatorCode=$code" | \
    python3 -c "
import json, sys
d = json.load(sys.stdin)
objs = d.get('GET_META_INDICATOR_INF',{}).get('METADATA_INF',{}).get('CLASS_INF',{}).get('CLASS_OBJ',[])
if isinstance(objs, dict): objs = [objs]
for obj in objs:
    classes = obj.get('CLASS', [])
    if isinstance(classes, dict): classes = [classes]
    for c in classes:
        cycle = c.get('cycle',{}).get('@name','')
        rank = c.get('RegionalRank',{}).get('@name','')
        to = c.get('@toDate','')
        stat = c.get('@statName','')
        if 'Month' in cycle and 'Japan' in rank:
            status = 'ACTIVE' if '9999' in to else 'DISCONTINUED:' + to
            print(f'$preset ($code): {stat} | Monthly | {status}')
            break
    else: continue
    break
"
done
```

**Expected output**: All presets should show `ACTIVE`. If any shows `DISCONTINUED`, follow step 3 to find a replacement.

---

## 2. Verify data freshness

After metadata verification, confirm actual data returns:

```bash
# Test all presets for data availability
for preset in cpi core-cpi core-core-cpi unemployment ip jgb10y \
  coincident-index machine-orders real-wages job-ratio \
  tertiary-index retail-sales service-sales; do

  uv run estat_client.py --preset "$preset" --no-cache 2>&1 | \
    python3 -c "
import json, sys
d = json.load(sys.stdin)
l = d.get('latest') or {}
s = (d.get('_provenance') or {}).get('staleness_days', '?')
print(f'$preset: date={l.get(\"date\",\"EMPTY\")} value={l.get(\"value\",\"NONE\")} staleness={s}d')
"
done
```

**What to check:**
- `date` should be within the last 2-3 months (monthly data)
- `value` should not be `NONE` or empty
- `staleness` should be < 120 days for monthly indicators

---

## 3. Find replacement when an indicator is discontinued

When a survey is discontinued, a replacement usually exists under a different StatCode.

**Step 1: Find related StatCodes**

Check the e-Stat API metadata PDF for survey names:
https://dashboard.e-stat.go.jp/static/api
→ Download 「パラメータ レスポンス ① メタ（系列）」PDF

Look for the old and new StatCode. Example:
- `00200544` サービス産業動向調査（旧, discontinued 2024-12）
- `00200546` サービス産業動態統計調査（新, active）

**Step 2: Search by StatCode**

```bash
curl -sS "https://dashboard.e-stat.go.jp/api/1.0/Json/getIndicatorInfo?Lang=EN&StatCode={NEW_STATCODE}"
```

**Step 3: Find the matching monthly indicator**

Look for an indicator with:
- Similar name to the old one
- `cycle.name = Month`
- `RegionalRank.name = Japan`
- `toDate = 99991200` (active)

**Step 4: Update preset**

In `estat_client.py`, update the `PRESETS` and `INDICATOR_NAMES` dicts.
Then run `sync-scripts.sh` + `sync-check.sh`.

---

## 4. Add a new indicator

**Step 1: Search by keyword**

```bash
uv run estat_client.py --search "keyword"
```

Note: search uses client-side filtering of the full catalog. Japanese keywords
may not work (catalog is in English). Use English keywords.

**Step 2: Search by Category code**

Use the Category codes from the API metadata PDF:

| Category | Code | Description |
|----------|------|-------------|
| 労働力 | 0301 | Labor force |
| 賃金・労働条件 | 0302 | Wages |
| 雇用 | 0303 | Employment |
| 鉱業 | 0501 | Mining |
| 製造業 | 0502 | Manufacturing |
| 商業 | 0601 | Commerce |
| サービス業 | 0603 | Services |
| 企業活動 | 0701 | Business activity |
| 金融・保険・通貨 | 0702 | Finance |
| 物価 | 0703 | Prices |
| 家計 | 0704 | Household |
| 国民経済計算 | 0705 | National accounts |
| 景気 | 0706 | Business conditions |

```bash
curl -sS "https://dashboard.e-stat.go.jp/api/1.0/Json/getIndicatorInfo?Lang=EN&Category={CODE}"
```

**Step 3: Verify the candidate**

```bash
# Check metadata
curl -sS "https://dashboard.e-stat.go.jp/api/1.0/Json/getIndicatorInfo?Lang=EN&IndicatorCode={CODE}"

# Test actual data
uv run estat_client.py --indicator {CODE} --no-cache
```

**Step 4: Add to estat_client.py**

Add to `PRESETS` dict + `INDICATOR_NAMES` dict. Run sync.

---

## 5. BOJ API indicator verification

For BOJ-sourced indicators, use the `getMetadata` endpoint:

```bash
# List all series in a database
curl -sS "https://www.stat-search.boj.or.jp/api/v1/getMetadata?format=json&lang=en&db={DB}"
```

Verify data availability:

```bash
uv run boj_client.py --db {DB} --code {CODE} --start-date {YYYYMM}
```

---

## Latest Verification Record

**Date**: 2026-04-17
**Verified by**: automated script
**Result**: All 13 e-Stat presets ACTIVE + Monthly. All return 2026 data.

| Preset | Code | Survey | Monthly | Status | Data From |
|--------|------|--------|---------|--------|-----------|
| cpi | 0703010501010030000 | Consumer Price Index | ✅ | ACTIVE | 1971 |
| core-cpi | 0703010501010030010 | Consumer Price Index | ✅ | ACTIVE | 1971 |
| core-core-cpi | 0703010501010030020 | Consumer Price Index | ✅ | ACTIVE | 1971 |
| unemployment | 0301010000020020010 | Labour Force Survey | ✅ | ACTIVE | 1953 |
| ip | 0502070301000090010 | Indices of Industrial Production | ✅ | ACTIVE | 1978 |
| jgb10y | 0702020300000010020 | Japan Bond Trading | ✅ | ACTIVE | 2013 |
| coincident-index | 0706010500000090010 | Indexes of Business Conditions | ✅ | ACTIVE | 1985 |
| machine-orders | 0701030000000010010 | Machinery Orders | ✅ | ACTIVE | 2005 |
| real-wages | 0302030201010090010 | Monthly Labour Survey | ✅ | ACTIVE | 2012 |
| job-ratio | 0301020001000010010 | Employment Referrals | ✅ | ACTIVE | 1963 |
| tertiary-index | 0603100300000090010 | Tertiary Industry Activity | ✅ | ACTIVE | 2018 |
| retail-sales | 0601010201010010000 | Current Survey of Commerce | ✅ | ACTIVE | 1980 |
| service-sales | 0603010000000010000 | Monthly Business Survey of Services | ✅ | ACTIVE | 2013 |

**Issues found and fixed in this verification:**
- `service-sales`: old code `0603010200000010000` (StatCode 00200544) discontinued 2024-12. Replaced with `0603010000000010000` (StatCode 00200546).
- `job-ratio`: old code `0301020001000010020` was fiscal-year only. Replaced with `0301020001000010010` (monthly, StatCode 00450222).
