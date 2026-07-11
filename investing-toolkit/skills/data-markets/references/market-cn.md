# Market reference — CN

Distilled from the pre-migration `data-cn` skill's `SKILL.md`. All clients
below are byte-identical migrations (cache-layer only) — see
`references/migration-grounding.md` for the external-surface grounding.

## Sources + authority tiers

| Source | Tier | Client | Coverage |
|---|---|---|---|
| NBS new-SPA API (`data.stats.gov.cn/dg/website/publicrelease/web/external/*`) | **Tier A primary** | `nbs_client.py` | 21 presets: CPI/PPI/GDP/industrial/retail/FAI/trade/labor/PMI/money/real-estate/services |
| akshare aggregator (PBOC chinamoney + SHIBOR + Caixin, **via eastmoney mirror**) | Tier 2 — only for series NBS does not publish | `akshare_client.py` | 8 presets: LPR×2, RRR, SHIBOR-3M, 社融增量, new loans, Caixin Mfg/Svc PMI |
| FRED CSV | Tier A (US Fed as CN FX cross-source) | `fred_client.py` | DEXCHUS (CNY/USD), TRESEGCNM052N (FX reserves ex-gold) |
| yfinance (unofficial) | Tier 2 | `yfinance_client.py` | `.SS`/`.SZ`/`.HK` individual stocks; market indices |

**Honest gap**: canonical CN equity financials are Tier 2 (yfinance)
only — CSRC/cninfo (Tier-A for CN mainland equities) and HKEXnews
(Tier-A for `.HK`) primary-source disclosure are not integrated. This
mirrors the pre-migration skill's own stated scope, not a new regression.

## API keys + rate limits

None required — NBS, akshare, and FRED are all keyless. NBS new-SPA and
akshare endpoints are documented as reachable from TW/US/Anthropic IPs
(empirically verified pre-migration; rationale preserved in git history,
not restated here).

## Caveats

- **akshare = eastmoney mirror**, not a direct PBOC/Caixin feed — treat
  as a secondary aggregator; NBS-published series should always route
  through `nbs_client.py` instead (akshare's own NBS mirror is
  stale/lagged relative to NBS new-SPA).
- **NBS reachability is empirical, not contractually guaranteed** — no
  SLA; the new-SPA API is an unofficial-but-stable internal endpoint.
- BSE (北京证券交易所, codes starting `4`/`8`) is not covered by
  yfinance and is out of scope; bare numeric codes outside the
  {4,5,6}-digit conventions emit a stderr warning and pass through
  unchanged rather than being refused.
- Publication lags vary widely: CPI/PPI/PMI ~45-50d, GDP ~100d,
  industrial/retail/services ~135d in Jan-Feb (combined release), akshare
  LPR/SHIBOR same-day to 1BD.

## Error dialect

CN tags every observation with `_source` (`"nbs_spa"` / `"akshare"` /
`"csv"` / `"yfinance"`) inherited from the underlying client, plus the
same one-level `error`/`_error` section walk `pack.py`'s classifier
applies uniformly across all 5 markets.
