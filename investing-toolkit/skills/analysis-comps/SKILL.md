---
name: analysis-comps
description: >-
  Pure-compute peer multiples comparison. Input: --anchor <data-pack-json>
  --peers <comma-sep-paths>. Output: comps table JSON with median/mean/quartile
  statistics + anchor delta + ranking.
  Comps 相対評価純計算層。同業相對估值純計算層。
---

# analysis-comps

Pure-compute Layer 2 skill in the v2.0.0 three-layer architecture
(data → analysis → report). Implements peer-multiples comparable analysis
over pre-fetched data packs — the second estimation pillar alongside
`analysis-dcf`.

## Layer 2 Contract — NO I/O

This skill performs **zero network or external file I/O** beyond reading
the `--anchor` and `--peers` JSON paths. No yfinance / SEC EDGAR / MOPS
clients are imported. Fetching is the responsibility of the caller —
typically `data-markets/scripts/pack.py --ticker <t> --pack comps-multiples`
for both anchor and each peer.

```
data-markets/scripts/pack.py --ticker <t> --pack comps-multiples (anchor + N peers)
                                              ↓
                                       analysis-comps (this skill)
                                              ↓
                                       comps table JSON
```

Callers (e.g. `report-equity-memo`) compose this skill with the data layer.

## Peer-Discovery is NOT this skill's job

`analysis-comps` consumes pre-fetched peer data only. Peer-list discovery
(WebSearch + competitor research → 5–8 tickers + per-peer rationale) is
the **report layer's** responsibility (see Spec §5.5). When the report
skill receives `--peers <list>` from the user it skips discovery; when
only `--anchor <ticker>` is given it spawns a research agent at runtime.
By the time JSON paths arrive at this skill, the peer set is final.

## Input Contract

`--anchor <path>` and each comma-separated `--peers` path must point to
JSON files produced by `data-markets/scripts/pack.py --ticker <t> --pack comps-multiples`.
Minimum shape per file:

```json
{
  "pack": "comps-multiples",
  "ticker": "AAPL",
  "fetched_at": "2026-05-01T00:00:00Z",
  "info": {
    "AAPL": {
      "trailingPE":         28.5,
      "forwardPE":          25.1,
      "priceToSales":        7.2,
      "priceToBook":        35.4,
      "enterpriseToEbitda": 21.3
    }
  },
  "_provenance": { "skill": "data-markets", ... }
}
```

**Batch peer files** — a single `--peers` path may instead point at a
*batch* pack produced by `data-markets/scripts/pack.py --tickers T1,T2,...
--pack comps-multiples` (per `us-schema-comps-multiples.json`): no
top-level `ticker` field, and `info` (== `tickers`) keyed by **N**
tickers instead of 1. The script expands this into one peer entry per
key — e.g. one `--peers batch.json` file with `info: {"MSFT": {...},
"GOOGL": {...}}` yields two peer entries (`MSFT`, `GOOGL`), each with
its own multiples. Batch and single-ticker peer paths may be mixed
freely in one comma-separated `--peers` list.

```json
{
  "pack": "comps-multiples",
  "fetched_at": "2026-05-01T00:00:00Z",
  "tickers": { "MSFT": { "trailingPE": 33.1, ... }, "GOOGL": { "trailingPE": 24.5, ... } },
  "info":    { "MSFT": { "trailingPE": 33.1, ... }, "GOOGL": { "trailingPE": 24.5, ... } }
}
```

If a `--peers` path resolves to **no** ticker at all (empty `info`/
`tickers` and no top-level `ticker` field — e.g. a batch-fetch-failure
envelope), the file is skipped and a warning naming the path is added to
`_provenance.warnings`; it is never silently added as a bogus
filename-stem peer with every multiple null.

**Field aliasing** — yfinance reports `enterpriseToEbitda`; the Spec §5.4
informal name is `evEbitda`. Either is accepted on input; the output
schema normalises to `evEbitda`.

**Per-peer rationale** can be supplied separately via `--rationale-map
<json-path>` whose contents look like:

```json
{ "MSFT": "Direct big-tech competitor in cloud / productivity",
  "GOOGL": "...",
  "META": "...",
  "AMZN": "..." }
```

If absent, `peers[*].rationale` is emitted as `null` (research-agent
output is the report layer's domain).

## CLI

```
uv run scripts/comps_compute.py \
    --anchor <anchor-pack-json-path> \
    --peers  <peer1.json>,<peer2.json>,...,<peerN.json> \
   [--mode direct|compute] \
   [--rationale-map <rationale-json-path>]
```

| Flag                | Required | Notes                                                                              |
|---------------------|----------|------------------------------------------------------------------------------------|
| `--anchor`          | yes      | Path to anchor ticker's `comps-multiples` pack JSON                                |
| `--peers`           | yes      | One or more peer JSON paths, comma-separated. Each path may be a single-ticker pack or a batch pack (`info` keyed by N tickers) — see §Input Contract. |
| `--mode`            | no       | `direct` (use multiples from comps-multiples pack) / `compute` (recompute from memo-fetch raw fundamentals; v2.2.0-b+). Default `direct`. |
| `--anchor-base`     | only when `--mode compute` | Path to anchor's memo-fetch pack JSON (Layer-1 raw fundamentals; required for compute mode). |
| `--rationale-map`   | no       | Optional JSON map `{ticker: rationale}` to merge into output `peers[*].rationale`. |

See §"Direct vs Compute — when to use which" below for choosing between modes.

## Multiples Set

### Direct mode (v2.0.0+) — fixed 5

Classic 5 multiples (per Spec §5.3) are emitted in `--mode direct` regardless of sector:

1. `trailingPE`
2. `forwardPE`
3. `evEbitda` (input alias `enterpriseToEbitda` accepted)
4. `priceToSales`
5. `priceToBook`

### Compute mode (v2.2.0-c+) — sector-aware schema dispatch

In `--mode compute`, the multiples emitted depend on the anchor's sector. The
`sector_classifier.py` module routes the anchor via
`(yfinance.info.sector, info.industry)` against
`references/sector-routing.yaml` plus per-issuer overrides in
`references/sector-overrides.yaml`, dispatching to one of 9 sector schemas:

| schema_id | Multiples | Indicators |
|---|---|---|
| `default` | trailingPE / forwardPE / evEbitda / priceToSales / priceToBook | gross_margin / operating_margin / FCF_yield |
| `bank` | trailingPE / forwardPE / priceToBook / priceToTangibleBook | ROE |
| `insurance` | trailingPE / priceToBook / priceToTangibleBook | ROE / book_value_growth |
| `asset-manager` | trailingPE / priceToBook / evEbitda | ROE |
| `reit` | priceToFFO / evEbitdare / priceToBook / priceToTangibleBook | (none) |
| `tech-saas` | forwardPE / priceToSales / evRevenue | rule_of_40 / gross_margin / FCF_margin |
| `tech-semis` | trailingPE / forwardPE / priceToSales / evEbitda | gross_margin / FCF_margin |
| `energy` | evEbitda / priceToBook / priceToCFO | FCF_yield / debt_to_equity |
| `utilities` | trailingPE / evEbitda / priceToBook | debt_to_equity |

Per-schema definitions live in `references/schema-<id>.json` (the SoT for what
each schema emits + a `deferred_concepts` field listing industry-specific
concepts not in standard US-GAAP XBRL — e.g. NIM for banks, AFFO for REITs,
combined ratio for insurers, AUM for asset managers, oil reserves for energy —
which are documented but NOT emitted as null fields).

REIT `priceToFFO` and `evEbitdare` are NAREIT approximations: strict NAREIT
FFO subtracts `gains_on_sale_of_property`, which is not a standard XBRL concept
→ omitted, with disclosure in per-multiple `compute_provenance.note`.

`--sector-override <id>` debug flag forces a schema (bypasses both yaml routing
and override table); `--show-routing` prints the resolved schema_id + source on
stderr for diagnostics.

### `--sector-benchmark` — SPDR sector ETF aggregate benchmark (v2.2.0-c-bench, opt-in)

Adds an `etf_benchmark` block under `anchor` showing per-multiple and
per-indicator divergence vs the anchor's mapped SPDR sector ETF aggregate.

```bash
uv run scripts/comps_compute.py --mode compute \
  --anchor anchor.json --anchor-base anchor-memo-fetch.json --peers peer.json \
  --sector-benchmark
```

- Mapping: `anchor.schema_id` (from sector classifier) → SPDR ETF (`bank → XLF`,
  `tech-saas → XLK`, `reit → XLRE`, `energy → XLE`, `utilities → XLU`,
  `default → XLY`). See [`references/etf-schema-map.json`](references/etf-schema-map.json).
- Aggregates refreshed weekly by GitHub Actions
  (`.github/workflows/sector-etf-aggregates.yml`); runtime reads
  `references/sector-etf-aggregate-<ETF>.json`.
- Bands: `in_line` (≤20% delta) / `notable` (20–50%) / `extreme` (>50%).
- Non-US ticker → `etf_benchmark: {status: "skipped"}`.
- Stale aggregate (`>14 days`) → `etf_benchmark.warnings` includes `"aggregate stale"`.
- Flag absent → `etf_benchmark` key absent (v2.2.0-c shape preserved).

Spec: [`docs/superpowers/specs/2026-05-05-investing-toolkit-v2.2.0-c-bench-spdr-etf-benchmark-design.md`](../../../docs/superpowers/specs/2026-05-05-investing-toolkit-v2.2.0-c-bench-spdr-etf-benchmark-design.md).

## Output Contract (Spec §5.4) — direct mode

For compute mode, the anchor block additionally carries `multiples_compute`
+ `divergence` + `compute_provenance` (see §"Direct vs Compute" below).

```json
{
  "anchor": {
    "ticker": "AAPL",
    "multiples_direct": {
      "trailingPE": 28.5, "forwardPE": 25.1, "evEbitda": 21.3,
      "priceToSales": 7.2, "priceToBook": 35.4
    }
  },
  "peers": [
    {
      "ticker": "MSFT",
      "multiples": { ... },
      "rationale": "Direct big-tech competitor in cloud / productivity"
    },
    { "ticker": "GOOGL", "multiples": { ... }, "rationale": null }
  ],
  "statistics": {
    "trailingPE":   { "median": 26.1, "mean": 27.3, "q1": 22.0, "q3": 30.5, "min": 18.5, "max": 35.2, "n": 4 },
    "forwardPE":    { ... },
    "evEbitda":     { ... },
    "priceToSales": { ... },
    "priceToBook":  { ... }
  },
  "anchor_delta": {
    "trailingPE": { "value": 28.5, "vs_median_pct": 9.2,  "percentile": 0.65 },
    "forwardPE":  { "value": 25.1, "vs_median_pct": -3.1, "percentile": 0.40 },
    "evEbitda":   { ... },
    "priceToSales": { ... },
    "priceToBook":  { ... }
  },
  "ranking": [
    { "ticker": "GOOGL", "composite_rank": 1, "trailingPE_rank": 1, "forwardPE_rank": 1, ... },
    { "ticker": "META",  "composite_rank": 2, ... },
    { "ticker": "AAPL",  "composite_rank": 3, ... },
    { "ticker": "MSFT",  "composite_rank": 4, ... },
    { "ticker": "AMZN",  "composite_rank": 5, ... }
  ],
  "_provenance": {
    "skill":              "analysis-comps",
    "anchor_data_source": "data-markets/scripts/pack.py --pack comps-multiples",
    "peer_data_sources":  ["data-markets/scripts/pack.py --pack comps-multiples", ...],
    "computed_at":        "2026-05-01T12:00:00Z",
    "io":                 "none",
    "mode":               "direct",
    "requested_mode":     "direct",
    "warnings":           []
  }
}
```

### Computation summary

For each of the 5 multiples:

1. **Statistics across the peer set** (anchor excluded) — `median`,
   `mean`, `q1` (25th pct), `q3` (75th pct), `min`, `max`, `n`. Peers
   with `null` for that multiple are skipped per-multiple, not globally.
2. **Anchor delta** — `value` (anchor's value), `vs_median_pct` =
   `((anchor − median) / median) × 100`, `percentile` = empirical
   percentile of anchor inside `peer_values ∪ {anchor}`.
3. **Per-multiple rank** — ascending across `anchor + peers` (lowest =
   "cheapest"); peers missing a multiple receive rank `null` for that
   multiple and are skipped from the average.
4. **Composite rank** — average of per-multiple ranks across the 5
   multiples (ignoring `null`s), then re-ranked ascending. Lowest
   composite_rank = "cheapest by composite multiples". Ties receive the
   same rank (competition / min ranking: e.g. values `[10, 20, 20, 30]`
   → ranks `[1, 2, 2, 4]` — not dense `[1, 2, 2, 3]`).

**Quartile convention**: `q1` / `q3` use
`statistics.quantiles(method="inclusive")` — equivalent to R-7 / Excel
`QUARTILE.INC`. For peer count `n=1`, `q1 = q3 =` the value.

**Percentile**:
`anchor_delta.{multiple}.percentile = #(peer_values ≤ anchor + 1) / (n + 1)`
where `n =` peer count. Anchor at exact median yields `0.5` in symmetric
distributions; ties bias upward (weak / inclusive ranking).

**Mode behaviour (v2.2.0-b+)**: `--mode compute` requires `--anchor-base
<memo-fetch.json>`. When supplied, the anchor block additionally carries
`multiples_compute` (3 of 5 multiples computed from raw fundamentals;
`priceToBook` and `evEbitda` deferred to v2.2.0-l), `divergence`
(per-multiple `abs_diff` / `pct_diff` / `alert ∈ {low, medium, high, n/a}`
per `references/divergence-thresholds.md`), and `compute_provenance`
(per-multiple numerator/denominator source + `accession_basis` Tier A
trace). `peers` remain single-input direct only — divergence is
anchor-only by design.

**Validation**: `--mode compute` without `--anchor-base` exits 2 with a
helpful stderr message. `--mode direct` with `--anchor-base` warns and
ignores. `_provenance.mode` records the effective mode; `requested_mode`
preserves the audit trail.

### Edge cases

- **Some peers missing some multiples (`null`)** — skip that ticker for
  that multiple's statistics; ranking still includes the ticker by
  averaging available ranks.
- **Empty peers** (anchor only) — emit warning in
  `_provenance.warnings`; statistics report `min=max=median=mean=anchor`,
  `q1=q3=anchor`, `n=0`; `anchor_delta.*.vs_median_pct=0.0`,
  `percentile=0.5`. Ranking has the single anchor entry only.
- **Field-name aliasing** — yfinance `enterpriseToEbitda` is normalised
  to `evEbitda` internally and in output.
- **Provenance source extraction** — anchor and peer source paths are
  read from each input JSON's `_provenance.skill` / `_provenance.source`
  if present; falls back to the input file path.

## Direct vs Compute — when to use which

| Mode | Trust source | Use case |
|---|---|---|
| `--mode direct` (default) | yfinance pre-cooked multiples (Yahoo's own EPS / EV definitions) | Industry comparability — aligns with Bloomberg / FactSet convention. Good for screen-style ranking; safe for sell-side memos. |
| `--mode compute` (v2.2.0-b+) | Recomputed from SEC EDGAR raw fundamentals + yfinance market data | Primary-source audit — every multiple traces back to a 10-K accession. Required for buy-side memos / short theses where the analyst must defend each number. |

### What compute mode actually computes (v2.2.0-c)

The full set of computable multiples + indicators (subset emitted per anchor schema_id):

#### Multiples

| Multiple | Definition | Notes |
|---|---|---|
| `trailingPE` | `current_price ÷ (FY net_income / shares_outstanding)` | FY-trailing, **not TTM** — diverges ~5-10% from yfinance TTM during the fiscal year (definitional gap, not a bug). |
| `forwardPE` | (pass-through) | Forward EPS is sell-side consensus aggregate; no primary source. Stamped `computed: false`. |
| `priceToSales` | `marketCap / FY revenue[0]` | |
| `priceToBook` | `marketCap / equity[0]` | (v2.2.0-l) |
| `evEbitda` | `(marketCap + total_debt − cash) / (operating_income[0] + D&A[0])` | (v2.2.0-l) |
| `priceToTangibleBook` | `marketCap / (equity[0] − goodwill[0] − intangibles[0])` | (v2.2.0-c) Empty goodwill/intangibles arrays substitute 0 (immaterial-empty signal); negative tangible book → null + note. |
| `priceToFFO` | `marketCap / (net_income[0] + D&A[0])` | (v2.2.0-c) **Approximation**: gains_on_sale not subtracted (XBRL gap). REIT-specific. |
| `evEbitdare` | `(marketCap + total_debt − cash) / (operating_income[0] + D&A[0])` | (v2.2.0-c) **Approximation**: impairment + gains_on_sale not added back (XBRL gap). REIT-specific. |
| `priceToCFO` | `marketCap / operating_cash_flow[0]` | (v2.2.0-c) Energy / midstream lean. |
| `evRevenue` | `(marketCap + total_debt − cash) / revenue[0]` | (v2.2.0-c) Tech-SaaS lean (often loss-making). |

#### Indicators (v2.2.0-c)

Operating-context metrics emitted as percentages (`{value: float, unit: "pct"}`); subset varies per schema.

| Indicator | Definition |
|---|---|
| `ROE` | `net_income[0] / equity[0] × 100` |
| `book_value_growth` | `(equity[0] − equity[1]) / equity[1] × 100` |
| `gross_margin` | `gross_profit[0] / revenue[0] × 100` |
| `operating_margin` | `operating_income[0] / revenue[0] × 100` |
| `FCF_yield` | `(operating_cash_flow[0] − capex[0]) / marketCap × 100` |
| `FCF_margin` | `(operating_cash_flow[0] − capex[0]) / revenue[0] × 100` |
| `debt_to_equity` | `total_debt[0] / equity[0] × 100` (resolution: prefer flat `total_debt[0]`; fallback to `long_term_debt[0] + short_term_debt[0]` recomposition) |
| `rule_of_40` | `revenue_growth_yoy + operating_margin` (sum of two pcts; revenue_growth_yoy = `(revenue[0] − revenue[1]) / revenue[1] × 100`) |

### Divergence interpretation

`divergence[m].alert` takes 4 values:

- `low` (≤5%): rounding/timing noise — ignore
- `medium` (5-15%): mention briefly in narrative
- `high` (>15%): trace to SEC accession in `compute_provenance[m].accession_basis` — the divergence is the story
- `n/a`: compute null (deferred multiple) or pass-through (forwardPE)

See [`references/divergence-thresholds.md`](references/divergence-thresholds.md) for band rationale.

### Required for compute mode

- `--anchor`: comps-multiples pack (existing direct-mode input)
- `--anchor-base`: memo-fetch pack (NEW; required only for `--mode compute`)
- `--peers`: comps-multiples pack(s) (peers stay direct-only — anchor-only compute reduces fetch overhead)

If `--mode compute` is invoked without `--anchor-base`, exit code 2 with stderr message.

## Cross-Plugin Handoff

This skill outputs JSON only. Memo composition and prose verdict belong
upstream:

```
data-markets:scripts/pack.py --pack comps-multiples (anchor + N peers)
  → analysis-comps (this skill, pure compute)
  → report-equity-memo (orchestrates Comps section into full memo)
       → domain-teams:investing-team (variant perception, conviction)
       → domain-teams:docs-team (formatting, optional)
```

This skill never delegates and never writes files; it prints JSON to
stdout and returns.

---

## i18n footer

- 日本語: pack.py が事前取得した同業他社の `comps-multiples` JSON を入力として、
  5 種倍率（trailingPE / forwardPE / EV-EBITDA / P/S / P/B）の中央値・平均・
  四分位、アンカーとの乖離、合成ランキングを純計算する Layer 2 スキル。
  **ネットワーク・外部 I/O 一切なし**。同業選定は report 層の責務。
- 繁體中文: 對 pack.py 預先抓取的同業 `comps-multiples` JSON 進行純計算，輸出
  5 種倍率（trailingPE / forwardPE / EV/EBITDA / P/S / P/B）的中位數、平均、
  四分位、anchor 偏離與合成排名（Layer 2）。**無任何網路 / 外部 I/O**。
  同業挑選由 report 層負責。
- English: Pure-compute Layer 2 peer comps over pre-fetched
  `comps-multiples` packs. Emits median / mean / quartile statistics,
  anchor delta vs median, percentile, and composite ranking across 5
  multiples (trailingPE / forwardPE / EV-EBITDA / P/S / P/B). **No
  network or external file I/O.** Peer-discovery happens upstream in
  the report layer.
