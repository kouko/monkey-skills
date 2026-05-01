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
typically `data-{country}/pack.py --pack comps-multiples` for both anchor
and each peer.

```
data-{country}/pack.py --pack comps-multiples (anchor + N peers)
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
JSON files produced by `data-{country}/pack.py --pack comps-multiples`.
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
  "_provenance": { "skill": "data-us", ... }
}
```

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
| `--peers`           | yes      | One or more peer JSON paths, comma-separated                                       |
| `--mode`            | no       | `direct` (use multiples in JSON) / `compute` (recompute from base financials, v2.1+ placeholder). Default `direct`. |
| `--rationale-map`   | no       | Optional JSON map `{ticker: rationale}` to merge into output `peers[*].rationale`. |

In v2.0.0 only `--mode direct` is wired; `--mode compute` is a placeholder
for sector-adjusted recomputation deferred to v2.1+ per Spec §5.3.

## Multiples Set (v2.0.0)

Classic 5 (per Spec §5.3):

1. `trailingPE`
2. `forwardPE`
3. `evEbitda` (input alias `enterpriseToEbitda` accepted)
4. `priceToSales`
5. `priceToBook`

Sector-adjusted multiples (banks: P/B+ROE; REITs: P/AFFO; tech:
EV/Revenue + Rule-of-40) are deferred to v2.1+.

## Output Contract (Spec §5.4)

```json
{
  "anchor": {
    "ticker": "AAPL",
    "multiples": {
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
    "anchor_data_source": "data-us/pack.py --pack comps-multiples",
    "peer_data_sources":  ["data-us/pack.py --pack comps-multiples", ...],
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

**Mode fallback (v2.0.0)**: `--mode compute` is not yet implemented; if
requested, the script emits a stderr warning, falls back to `direct`,
stamps `_provenance.mode = "direct"` (actual computation mode) and
`_provenance.requested_mode = "compute"` (audit trail).

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

## Cross-Plugin Handoff

This skill outputs JSON only. Memo composition and prose verdict belong
upstream:

```
data-{country}:pack.py --pack comps-multiples (anchor + N peers)
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
