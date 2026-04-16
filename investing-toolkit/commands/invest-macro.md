# /invest-macro

**Trigger**: `/invest-macro [--region us|tw|global]`

Diagnose the current macro regime using Investment Clock + Hedgeye GIP framework.
Fetches FRED data (yield curve, CPI, GDP, Industrial Production) and outputs:
- IC phase (Recovery / Overheat / Stagflation / Reflation)
- GIP quadrant (Growth / Inflation rate-of-change)
- 3 asset-class tilts
- Key indicator table with FRED data

## What This Does

Invokes `skills/macro-regime-snapshot/SKILL.md`.

## Examples

```
/invest-macro
/invest-macro --region us
/invest-macro --region global
```

## Notes

- Requires Python: `pip install -r investing-toolkit/scripts/requirements.txt`
- FRED data has publication lags (CPI ~2-3 weeks, GDP ~1 month)
- For free FRED API key (higher rate limits): https://fred.stlouisfed.org/docs/api/api_key.html
  Then: `export FRED_API_KEY=your_key`
- For full analysis with investment verdict → use `/invest-memo` or `domain-teams:investing-team`
