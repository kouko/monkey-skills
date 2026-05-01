# /invest-macro

**Trigger**: `/invest-macro [--region us|japan|taiwan|korea|china|global|asia-pac|all]`

Diagnose the current macro regime using the Investment Clock + Hedgeye GIP framework, extended with US real-rate decomposition (4-tier accommodative / neutral / moderately-restrictive / clearly-restrictive). Outputs a 5-block dashboard per country.

## What This Does

Pipeline (main agent dispatches):
1. `data-{country}/scripts/pack.py --pack regime-pack` per requested country (parallel)
2. `analysis-macro-regime/scripts/regime_compose.py --input us=...,jp=...,...` → IC + GIP regime card

## Examples

```
/invest-macro                                   # Default: US only
/invest-macro --region us
/invest-macro --region japan
/invest-macro --region taiwan
/invest-macro --region korea
/invest-macro --region china
/invest-macro --region global                   # US + JP
/invest-macro --region asia-pac                 # JP + TW + KR + CN
/invest-macro --region all                      # 5 markets side-by-side
/invest-macro --region us,korea                 # Free-form comma list
```

## Routing

Each `data-{country}` bundles its country's macro sources:

| Country | Sources |
|---|---|
| US | FRED (31 series; nowcast/rates/inflation/swap-spreads/real-rates groups) |
| JP | BOJ + e-Stat + ECB (real-rate via Fisher decomposition; v2.1+ extends to JGBi C+D+E) |
| TW | stat.gov.tw + CBC + DGBAS + NDC (五色景氣燈號 9-45 composite) |
| KR | FinanceDataReader → BOK ECOS-KEYSTAT (54 indicators) |
| CN | NBS new-SPA + akshare (PBOC + Caixin) + FRED USDCNY |

`analysis-macro-regime` then classifies each country's growth × inflation directions → IC quadrant + GIP regime; emits cross-country consensus when >1 country requested.

## Notes

- All data sources are free (no API key needed for core operation; `FRED_API_KEY` optional for higher US rate limits)
- Real-rate decomposition: US uses Fisher (Nominal − Breakeven) + optional DFII identity check; JP returns null (v2.1 restoration tracked in `analysis-macro-regime/references/japan-real-rate-roadmap.md`); TW / CN have no linker market; KR KTBi deferred
- Publication lags: CPI ~2-3 weeks, monthly GDP proxies ~3-6 weeks after reference month
- For full analysis with investment verdict → use `/invest-memo` or `domain-teams:investing-team`
