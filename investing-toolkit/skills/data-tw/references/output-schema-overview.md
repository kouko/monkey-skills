# data-tw output schemas — overview

JSON Schema (Draft 2020-12) definitions for the 5 pack types emitted by
`scripts/pack.py`, plus a reusable error-envelope schema. Layer 2 (`analysis-*`)
and Layer 3 (`report-*`) skills consume `data-tw` output exclusively through
these contracts.

## Files

| Schema | Pack | Sample fixture |
|---|---|---|
| `schema-snapshot.json` | `--pack snapshot` | `tests/data/fixtures/data-tw-snapshot-sample.json` |
| `schema-memo-fetch.json` | `--pack memo-fetch` | `tests/data/fixtures/data-tw-memo-fetch-sample.json` |
| `schema-comps-multiples.json` | `--pack comps-multiples` | `tests/data/fixtures/data-tw-comps-multiples-sample.json` |
| `schema-screener-batch.json` | `--pack screener-batch` | `tests/data/fixtures/data-tw-screener-batch-sample.json` |
| `schema-regime-pack.json` | `--pack regime-pack` | `tests/data/fixtures/data-tw-regime-pack-sample.json` |
| `schema-error-envelope.json` | (reusable building block) | — |

All five pack schemas reference `schema-error-envelope.json` for every leaf
node — the wrapper produced by `pack.py wrap()`.

---

## TW-SPECIFIC: nested wrapper envelope

**This is unique among the 5 country data layers.** Every `data-tw` leaf is
wrapped through `pack.py wrap()` into the following envelope:

```jsonc
{
  "_tier": "A" | "2" | "2-gap",
  "_source": "mops" | "twse_openapi" | "finmind" | "yfinance" | "cbc" | "dgbas" | "ndc" | "statgov",
  "_action": "<client-action-name>",
  "data": { ... }       // success
  // OR
  "_error": "<reason>",  // failure
  "_stderr": "...",
  "_cmd": "..."
}
```

Other `data-{country}` layers do not nest underlying client output under a
typed wrapper of this exact shape. Consumer skills written against `data-us`
/ `data-jp` / `data-kr` / `data-cn` MUST adjust their access pattern when
reading `data-tw`:

```python
# data-tw — must drill through the wrapper
basic = pack["mops"]["company_basic"]["data"]
if "_error" in pack["mops"]["company_basic"]:
    ...

# data-us / others — direct access
income = pack["sec"]["10K"]["facts"]
```

### Tier semantics (TW-specific tier policy)

| `_tier` | Meaning | Sources |
|---|---|---|
| `A`     | Tier A primary primary-source | mops, twse_openapi, cbc, dgbas, ndc, statgov |
| `2`     | Tier 2 cross-source convenience | yfinance (info / multiples / batch); finmind for `.TWO` price history |
| `2-gap` | By-design Tier-A gap supplier — FinMind is the **primary** because no Tier A endpoint exists | finmind T86 daily flow + 融資融券 daily history |

`pack.py` does **not** fall back from Tier A to Tier 2 automatically. When a
Tier A leaf errors, the leaf carries `_error` + `_stderr` + `_cmd` and the
top-level `_partial` flag flips to `true`. Layer 2 / Layer 3 consumers decide
escalation policy.

---

## Pack contracts

### snapshot

Light single-ticker pack. Powers `report-stock-snapshot` and lighter slash-
command paths.

- yfinance: `info`, `history` (default period `1y`)
- mops (Tier A): `company_basic`, `balance_sheet`, `income_statement`
- twse (Tier A): `daily_price`, `pe_pb_yield`, `margin_balance`
- finmind (`2-gap`): `three_investor_flow` (T86 trailing 90 days)
- Top-level `_partial: bool` flips on any Tier A error.

### memo-fetch

Heavy single-ticker pack. Superset of `snapshot`, adds full disclosure history
needed for the equity-memo path.

- yfinance: same (default period `2y`)
- mops (Tier A): + `cash_flow`, `monthly_revenue`, `dividends` (5y), `director_holdings`,
  `insider_trades`, `announcements`
- twse (Tier A): + `three_investor` (snapshot, distinct from FinMind's daily series),
  + `stock_day_history` (`sii` only — TPEx has no `/rwd/`)
- finmind: + `margin_history` (`2-gap`, 90 days),
  + `price_history` (`2`, **only** when `_normalized.market == "otc"`)

### comps-multiples

Lightest pack. Yfinance multiples-only across one or many tickers — fuel for
`analysis-comps`. Per-ticker shape:

```jsonc
{
  "_tier": "2",
  "_source": "yfinance",
  "_action": "info-multiples",
  "data": {
    "multiples": {
      "trailingPE": …, "forwardPE": …,
      "priceToSalesTrailing12Months": …, "priceToBook": …,
      "enterpriseToEbitda": …, "enterpriseToRevenue": …,
      "marketCap": …, "enterpriseValue": …
    }
  }
}
```

Any of the 8 keys may be missing if yfinance does not return that field
for the ticker. No `_partial` flag (lightest pack).

### screener-batch

- yfinance: `info_batch`, `history_batch` (single subprocess each — efficient)
- mops (Tier A): per-ticker `company_basic`, keyed by yfinance-style ticker.

### regime-pack

Macro-only — no ticker dimension. 5 sources: `cbc`, `dgbas`, `ndc`, `statgov`
(plus FinMind/yfinance/MOPS/TWSE OpenAPI absent here).

> **NOTE — TW differs from `data-us`:** there is **no FRED leg**. Cross-country
> macro callers that need both TW and US should chain `data-tw --pack regime-pack`
> with `data-us --pack regime-pack`.

---

## ROC year date conventions (memo-fetch / snapshot)

`pack.py` performs all Gregorian → ROC year arithmetic — callers do not pass
ROC dates themselves.

### `latest_roc_quarter()` — used by balance_sheet / income_statement / cash_flow

Filing-deadline-aware. ROC year = Gregorian year - 1911.

| Date window (today) | (roc_year, season) returned |
|---|---|
| Nov 15 → Dec 31 | (Y-1911, 3) |
| Aug 15 → Nov 14 | (Y-1911, 2) |
| May 16 → Aug 14 | (Y-1911, 1) |
| Apr 1 → May 15 | (Y-1-1911, 4) |
| Jan 1 → Mar 31 | (Y-1-1911, 3) (Q4 of last year not yet filed; fall back to Q3) |

Example: fetched on 2026-05-01 → `(roc_year=114, season=4)` for Q4 2025
(filing deadline Mar 31 2026 has passed).

### `latest_revenue_month()` — used by monthly_revenue

月營收 published by the 10th of the following month. 5-day buffer:

- `today.day < 15` → fall back **2** months (last month not reliably published)
- `today.day >= 15` → fall back **15 days** (last month definitely available)

Example: fetched on 2026-05-01 → `(roc_year=115, month=3)` (Mar 2026 data,
because pre-day-15 falls back two months).

---

## NDC cycle signal score — IMPORTANT scale clarification

`schema-regime-pack.json` exposes `ndc.signal.data` containing two time series:
**score** (`景氣對策信號綜合分數`) and **color** (`景氣對策信號` 五色燈號).

The score is the **9-component composite**, each component scored 1–5, summed:

```
composite range: 9 (all-1) to 45 (all-5)
typical band     : roughly 16 – 38
```

The **5-color light** (`紅 / 黃紅 / 綠 / 黃藍 / 藍`) is derived from
band-thresholds applied to this composite — it is NOT the score itself.

> ⚠️ Do NOT confuse this with the "1–9" cycle scale that some popular charts
> (e.g. financial-news visualizations) display. Those use a re-scaled or
> color-coded representation. The raw value in `data-tw` is the composite
> 9–45 score straight from the NDC `景氣指標與燈號.csv`.

---

## Ticker conventions (snapshot / memo-fetch / comps / screener)

All ticker fields use the yfinance suffix form after normalization:

| Input | `_normalized.market` | `_normalized.ticker_yf` |
|---|---|---|
| `2330`     | `sii` | `2330.TW`  |
| `2330.TW`  | `sii` | `2330.TW`  |
| `2330.TWO` | `otc` | `2330.TWO` |

`pack.py normalize_ticker()` accepts any of the three forms and routes:

- `sii` → MOPS + TWSE OpenAPI primary; yfinance `.TW`
- `otc` → MOPS + TWSE OpenAPI primary; **price history via FinMind** (TPEx
  has no `/rwd/`); yfinance `.TWO`

In `schema-memo-fetch.json` this routing manifests structurally:

- `twse.stock_day_history` is **present iff `_normalized.market == "sii"`**
- `finmind.price_history` is **present iff `_normalized.market == "otc"`**

The schemas mark both as optional rather than encoding the conditional with
`if/then` — consumers should branch on `_normalized.market` directly.

---

## Validating live output against a schema

```bash
INVESTING_TOOLKIT_CACHE=/tmp/tw-cache uv run \
  investing-toolkit/skills/data-tw/scripts/pack.py \
  --ticker 2330.TW --pack snapshot > /tmp/tw-snap.json

uv run --with jsonschema --with referencing python3 - <<'PY'
import json
from pathlib import Path
from jsonschema import Draft202012Validator
from referencing import Registry, Resource

ref_dir = Path("investing-toolkit/skills/data-tw/references")
BASE = "file:///schemas/"
def load(name):
    return BASE + name, Resource.from_contents(json.loads((ref_dir / name).read_text()))
registry = Registry().with_resources([
    load(n) for n in [
        "schema-error-envelope.json", "schema-snapshot.json",
        "schema-memo-fetch.json",     "schema-comps-multiples.json",
        "schema-screener-batch.json", "schema-regime-pack.json",
    ]
])
schema = json.loads((ref_dir / "schema-snapshot.json").read_text())

# rewrite relative $refs to BASE+name so the registry resolves them
def rewrite(node):
    if isinstance(node, dict):
        for k, v in list(node.items()):
            if k == "$ref" and isinstance(v, str) and not v.startswith(("http", "#", "file:")):
                node[k] = BASE + v
            else:
                rewrite(v)
    elif isinstance(node, list):
        for it in node: rewrite(it)
rewrite(schema)

sample = json.loads(Path("/tmp/tw-snap.json").read_text())
errors = list(Draft202012Validator(schema, registry=registry).iter_errors(sample))
assert not errors, errors
print("TW snapshot live output validates")
PY
```

The cross-file `$ref` rewrite is required because the schemas use relative
filenames (`{"$ref": "schema-error-envelope.json"}`) — natural for an on-disk
reference set, but the `jsonschema` library needs a base URI to resolve them.

---

## Cross-pack invariants

Across all 5 packs:

1. Top-level always carries `_pack: "<one-of-five>"`.
2. Single-ticker packs (snapshot, memo-fetch, comps with one ticker) carry
   `_ticker` + `_normalized`. Batch packs carry `_tickers: [...]` and (for
   screener-batch / comps-multiples) `tickers: { <yf>: envelope }`.
3. `_partial: bool` appears on `snapshot`, `memo-fetch`, `regime-pack`. It
   is **absent** on `comps-multiples` and `screener-batch` — those callers
   walk per-leaf `_error` directly.
4. Every leaf is a `schema-error-envelope.json` instance — even `null` /
   missing data is represented through the wrapper, not by omitting the key.

---

## See also

- `SKILL.md` — full pack composition tables, tier policy, ticker conventions.
- `scripts/pack.py` — the canonical implementation (start at `wrap()` and the
  per-pack functions to trace the schema's emission point).
- Layer-spec: `docs/superpowers/specs/2026-05-01-investing-toolkit-v2.0.0-three-layer-design.md` §4.2.
